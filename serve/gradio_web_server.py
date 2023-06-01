import argparse
from collections import defaultdict
import datetime
import json
import os
import time
import uuid

import gradio as gr
import requests

from serve.conversation import (default_conversation, conv_templates,
                                   SeparatorStyle)
from serve.constants import LOGDIR
from serve.utils import (build_logger, server_error_msg,
    violates_moderation, moderation_msg)
from serve.gradio_patch import Chatbot as grChatbot
from serve.gradio_css import code_highlight_css

NAME = "SelFee"

logger = build_logger("gradio_web_server", "gradio_web_server.log")

headers = {"User-Agent": f"{NAME} Client"}

no_change_btn = gr.Button.update()
enable_btn = gr.Button.update(interactive=True)
disable_btn = gr.Button.update(interactive=False)

priority = {
    "SelFee-7B": "aaaaaab",
    "SelFee-13B": "aaaaaaa",    
}


def get_conv_log_filename():
    t = datetime.datetime.now()
    name = os.path.join(LOGDIR, f"{t.year}-{t.month:02d}-{t.day:02d}-conv.json")
    return name


def get_model_list():
    ret = requests.post(args.controller_url + "/refresh_all_workers")
    assert ret.status_code == 200
    ret = requests.post(args.controller_url + "/list_models")
    models = ret.json()["models"]
    models.sort(key=lambda x: priority.get(x, x))
    logger.info(f"Models: {models}")
    return models


get_window_url_params = """
function() {
    const params = new URLSearchParams(window.location.search);
    url_params = Object.fromEntries(params);
    console.log(url_params);
    return url_params;
    }
"""


def load_demo(url_params, request: gr.Request):
    logger.info(f"load_demo. ip: {request.client.host}. params: {url_params}")

    dropdown_update = gr.Dropdown.update(visible=True)
    if "model" in url_params:
        model = url_params["model"]
        if model in models:
            dropdown_update = gr.Dropdown.update(
                value=model, visible=True)

    state = default_conversation.copy()
    return (state,
            dropdown_update,
            gr.Chatbot.update(visible=True),
            gr.Textbox.update(visible=True),
            gr.Button.update(visible=True),
            gr.Row.update(visible=True),
            gr.Accordion.update(visible=True))


def load_demo_refresh_model_list(request: gr.Request):
    logger.info(f"load_demo. ip: {request.client.host}")
    models = get_model_list()
    state = default_conversation.copy()
    return (state, gr.Dropdown.update(
               choices=models,
               value=models[0] if len(models) > 0 else ""),
            gr.Chatbot.update(visible=True),
            gr.Textbox.update(visible=True),
            gr.Button.update(visible=True),
            gr.Row.update(visible=True),
            gr.Accordion.update(visible=True))


def vote_last_response(state, vote_type, model_selector, request: gr.Request):
    with open(get_conv_log_filename(), "a") as fout:
        data = {
            "tstamp": round(time.time(), 4),
            "type": vote_type,
            "model": model_selector,
            "state": state.dict(),
            "ip": request.client.host,
        }
        fout.write(json.dumps(data) + "\n")


def upvote_last_response(state, model_selector, request: gr.Request):
    logger.info(f"upvote. ip: {request.client.host}")
    vote_last_response(state, "upvote", model_selector, request)
    return ("",) + (disable_btn,) * 3


def downvote_last_response(state, model_selector, request: gr.Request):
    logger.info(f"downvote. ip: {request.client.host}")
    vote_last_response(state, "downvote", model_selector, request)
    return ("",) + (disable_btn,) * 3


def flag_last_response(state, model_selector, request: gr.Request):
    logger.info(f"flag. ip: {request.client.host}")
    vote_last_response(state, "flag", model_selector, request)
    return ("",) + (disable_btn,) * 3


def stop_response(state, model_selector, request: gr.Request):
    logger.info(f"stop. ip: {request.client.host}")
    _ = requests.post(state.worker_addr + "/worker_stop_stream", timeout=5)
    return ("",) + (enable_btn, enable_btn, disable_btn, enable_btn, enable_btn)


def regenerate(state, request: gr.Request):
    logger.info(f"regenerate. ip: {request.client.host}")

    human_pos = []
    for i, (role, message) in enumerate(state.messages):
        if i < 2:
            continue
        is_revision = message.strip().startswith("Revision") and role == state.roles[1]
        is_feedback = message.strip().startswith("Feedback") and role == state.roles[0]
        is_human = not is_revision and not is_feedback and role == state.roles[0]

        if is_human:
            human_pos.append(i)

    last_human = human_pos[-1]
    state.messages = state.messages[:last_human+2]
    state.messages[-1][-1] = None
    state.skip_next = False
    return (state, state.to_gradio_chatbot(), "") + (disable_btn, disable_btn, enable_btn, disable_btn, disable_btn)


def clear_history(request: gr.Request):
    logger.info(f"clear_history. ip: {request.client.host}")
    state = default_conversation.copy()
    return (state, state.to_gradio_chatbot(), "") + (disable_btn,) * 5


def add_text(state, text, request: gr.Request):
    logger.info(f"add_text. ip: {request.client.host}. len: {len(text)}")
    if len(text) <= 0:
        state.skip_next = True
        return (state, state.to_gradio_chatbot(), "") + (no_change_btn,) * 5
    if args.moderate:
        flagged = violates_moderation(text)
        if flagged:
            state.skip_next = True
            return (state, state.to_gradio_chatbot(), moderation_msg) + (
                no_change_btn,) * 5

    text = text[:1536]  # Hard cut-off
    state.append_message(state.roles[0], text)
    state.append_message(state.roles[1], None)
    state.skip_next = False
    return (state, state.to_gradio_chatbot(), "") + (disable_btn, disable_btn, enable_btn, disable_btn, disable_btn)


def post_process_code(code):
    sep = "\n```"
    if sep in code:
        blocks = code.split(sep)
        if len(blocks) % 2 == 1:
            for i in range(1, len(blocks), 2):
                blocks[i] = blocks[i].replace("\\_", "_")
        code = sep.join(blocks)
    return code


def http_bot(state, model_selector, temperature, max_new_tokens, request: gr.Request):
    logger.info(f"http_bot. ip: {request.client.host}")
    start_tstamp = time.time()
    model_name = model_selector

    if state.skip_next:
        # This generate call is skipped due to invalid inputs
        yield (state, state.to_gradio_chatbot()) + (no_change_btn,) * 5
        return

    if len(state.messages) == state.offset + 2:
        # First round of conversation
        if "koala" in model_name: # Hardcode the condition
            template_name = "bair_v1"
        else:
            template_name = "v1"
        new_state = conv_templates[template_name].copy()
        new_state.conv_id = uuid.uuid4().hex
        new_state.append_message(new_state.roles[0], state.messages[-2][1])
        new_state.append_message(new_state.roles[1], None)
        state = new_state

    # Query worker address
    controller_url = args.controller_url
    ret = requests.post(controller_url + "/get_worker_address",
            json={"model": model_name})
    worker_addr = ret.json()["address"]
    state.worker_addr = worker_addr
    logger.info(f"model_name: {model_name}, worker_addr: {worker_addr}")

    # No available worker
    if worker_addr == "":
        state.messages[-1][-1] = server_error_msg
        yield (state, state.to_gradio_chatbot(), disable_btn, disable_btn, disable_btn, enable_btn, enable_btn)
        return

    # Construct prompt
    prompt = state.get_prompt()
    skip_echo_len = len(prompt.replace("</s>", " "))  # why previously + 1?
    # skip_echo_len = len(prompt.replace("</s>", " ")) + 1

    # For debugging
    # state.messages[-1][-1] = "[DEBUG PURPOSE ONLY]\n[PROMPT]\n" + prompt
    # state.append_message(state.roles[1], None)

    # Make requests
    pload = {
        "model": model_name,
        "prompt": prompt,
        "temperature": float(temperature),
        "max_new_tokens": int(max_new_tokens),
        "stop": "</s>",
        # "stop": state.sep if state.sep_style == SeparatorStyle.SINGLE else state.sep2,
    }
    logger.info(f"==== request ====\n{pload}")

    state.messages[-1][-1] = "▌"
    yield (state, state.to_gradio_chatbot()) + (disable_btn, disable_btn, enable_btn, disable_btn, disable_btn)
    # yield (state, state.to_gradio_chatbot()) + (disable_btn,) * 5

    initial_message_length = len(state.messages)
    try:
        # Stream output
        response = requests.post(worker_addr + "/worker_generate_stream",
            headers=headers, json=pload, stream=True, timeout=20)
        is_feedback = True
        for chunk in response.iter_lines(decode_unicode=False, delimiter=b"\0"):
            if chunk:
                data = json.loads(chunk.decode())
                if data["error_code"] == 0:
                    output = data["text"][skip_echo_len:].strip()
                    output = post_process_code(output)
                    output_blocks = output.split("###")
                    # output_blocks = [(o if i == 0 else "###" + o) for i, o in enumerate(output.split("###")) if o]
                    current_message_length = len(state.messages)
                    while current_message_length < initial_message_length + len(output_blocks) - 1:
                        if not is_feedback:
                            state.append_message(state.roles[1], None)
                            is_feedback = True
                        else:
                            state.append_message(state.roles[0], None)
                            is_feedback = False
                        current_message_length = len(state.messages)
                    for i, output_block in enumerate(output_blocks):
                        state.messages[initial_message_length - 1 + i][-1] = output_block
                    state.messages[-1][-1] = state.messages[-1][-1] + "▌"
                    yield (state, state.to_gradio_chatbot()) + (disable_btn, disable_btn, enable_btn, disable_btn, disable_btn)
                else:
                    output = data["text"] + f" (error_code: {data['error_code']})"
                    state.messages[-1][-1] = output
                    yield (state, state.to_gradio_chatbot()) + (disable_btn, disable_btn, disable_btn, enable_btn, enable_btn)
                    return
                time.sleep(0.02)
    except requests.exceptions.RequestException as e:
        state.messages[-1][-1] = server_error_msg + f" (error_code: 4)"
        yield (state, state.to_gradio_chatbot()) + (disable_btn, disable_btn, disable_btn, enable_btn, enable_btn)
        return

    state.messages[-1][-1] = state.messages[-1][-1][:-1]
    state.worker_addr = None
    yield (state, state.to_gradio_chatbot()) + (enable_btn, enable_btn, disable_btn, enable_btn, enable_btn)

    finish_tstamp = time.time()
    logger.info(f"{output}")

    with open(get_conv_log_filename(), "a") as fout:
        data = {
            "tstamp": round(finish_tstamp, 4),
            "type": "chat",
            "model": model_name,
            "start": round(start_tstamp, 4),
            "finish": round(start_tstamp, 4),
            "state": state.dict(),
            "ip": request.client.host,
        }
        fout.write(json.dumps(data) + "\n")


notice_markdown = ("""
# SelFee: Iterative Self-Revising LLM Empowered by Self-Feedback Generation

We are excited to announce the release of SelFee, our new instruction-following language model that generates self-feedback on its response and self-revises based on feedback. Check out our <a href= "https://kaistai.github.io/SelFee/">blog post!</a>

Note: The current model is enforced to revise at least once. To control the number of minimum enforced revisions, check out our <a href="https://github.com/kaistAI/SelFee">Github</a> source code! Also, the delta weights and the training data are released on <a href="https://huggingface.co/datasets/kaist-ai/selfee-train">huggingface</a>.
""")


learn_more_markdown = ("""
### Terms of use
By using this service, users are required to agree to the following terms: The service is a research preview intended for non-commercial use only. It only provides limited safety measures and may generate offensive content. It must not be used for any illegal, harmful, violent, racist, or sexual purposes. The service may collect user dialogue data for future research.

### License
The service is a research preview intended for non-commercial use only, subject to the model [License](https://github.com/facebookresearch/llama/blob/main/MODEL_CARD.md) of LLaMA, [Terms of Use](https://openai.com/policies/terms-of-use) of the data generated by OpenAI, and [Privacy Practices](https://chrome.google.com/webstore/detail/sharegpt-share-your-chatg/daiacboceoaocpibfodeljbdfacokfjb) of ShareGPT. Please contact us if you find any potential violation.
""")


css = code_highlight_css + """
pre {
    white-space: pre-wrap;       /* Since CSS 2.1 */
    white-space: -moz-pre-wrap;  /* Mozilla, since 1999 */
    white-space: -pre-wrap;      /* Opera 4-6 */
    white-space: -o-pre-wrap;    /* Opera 7 */
    word-wrap: break-word;       /* Internet Explorer 5.5+ */
}
"""


def build_demo():
    with gr.Blocks(title=f"{NAME}", theme="JohnSmith9982/small_and_pretty", css=css) as demo:
        state = gr.State()

        # Draw layout
        notice = gr.Markdown(notice_markdown)

        with gr.Row(elem_id="model_selector_row"):
            model_selector = gr.Dropdown(
                choices=models,
                value=models[0] if len(models) > 0 else "",
                interactive=True,
                show_label=False).style(container=False)

        chatbot = grChatbot(elem_id="chatbot", label="Chat with SelFee", visible=True).style(height=550)
        with gr.Row():
            with gr.Column(scale=20):
                textbox = gr.Textbox(show_label=False,
                    placeholder="Enter text and press ENTER", visible=False).style(container=False)
            with gr.Column(scale=1, min_width=50):
                submit_btn = gr.Button(value="Send", visible=False)

        with gr.Row(visible=False) as button_row:
            upvote_btn = gr.Button(value="👍  Upvote", interactive=False)
            downvote_btn = gr.Button(value="👎  Downvote", interactive=False)
            # flag_btn = gr.Button(value="⚠️  Flag", interactive=False)
            stop_btn = gr.Button(value="⏹️  Stop Generation", interactive=False)
            regenerate_btn = gr.Button(value="🔄  Regenerate", interactive=False)
            clear_btn = gr.Button(value="🗑️  Clear history", interactive=False)

        with gr.Accordion("Parameters", open=False, visible=False) as parameter_row:
            temperature = gr.Slider(minimum=0.0, maximum=1.0, value=0.7, step=0.1, interactive=True, label="Temperature",)
            max_output_tokens = gr.Slider(minimum=0, maximum=2048, value=2048, step=64, interactive=True, label="Max output tokens",)

        gr.Markdown(learn_more_markdown)
        url_params = gr.JSON(visible=False)

        # Register listeners
        btn_list = [upvote_btn, downvote_btn, stop_btn, regenerate_btn, clear_btn]
        upvote_btn.click(upvote_last_response,
            [state, model_selector], [textbox, upvote_btn, downvote_btn, stop_btn])
        downvote_btn.click(downvote_last_response,
            [state, model_selector], [textbox, upvote_btn, downvote_btn, stop_btn])
        # flag_btn.click(flag_last_response,
        #     [state, model_selector], [textbox, upvote_btn, downvote_btn, flag_btn])
        regenerate_event = regenerate_btn.click(regenerate, state,
            [state, chatbot, textbox] + btn_list).then(
            http_bot, [state, model_selector, temperature, max_output_tokens],
            [state, chatbot] + btn_list)
        clear_btn.click(clear_history, None, [state, chatbot, textbox] + btn_list)

        submit_event = textbox.submit(add_text, [state, textbox], [state, chatbot, textbox] + btn_list
            ).then(http_bot, [state, model_selector, temperature, max_output_tokens],
                   [state, chatbot] + btn_list)
        submit_click_event = submit_btn.click(add_text, [state, textbox], [state, chatbot, textbox] + btn_list
            ).then(http_bot, [state, model_selector, temperature, max_output_tokens],
                   [state, chatbot] + btn_list)

        stop_btn.click(fn=None, inputs=None, outputs=None, cancels=[submit_event, submit_click_event, regenerate_event], queue=False)
        stop_btn.click(fn=stop_response, inputs=[state, model_selector], outputs=[textbox] + btn_list, queue=False)

        if args.model_list_mode == "once":
            demo.load(load_demo, [url_params], [state, model_selector,
                chatbot, textbox, submit_btn, button_row, parameter_row],
                _js=get_window_url_params)
        elif args.model_list_mode == "reload":
            demo.load(load_demo_refresh_model_list, None, [state, model_selector,
                chatbot, textbox, submit_btn, button_row, parameter_row])
        else:
            raise ValueError(f"Unknown model list mode: {args.model_list_mode}")

    return demo


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int)
    parser.add_argument("--controller-url", type=str, default="http://localhost:21001")
    parser.add_argument("--concurrency-count", type=int, default=10)
    parser.add_argument("--model-list-mode", type=str, default="once",
        choices=["once", "reload"])
    parser.add_argument("--share", action="store_true")
    parser.add_argument("--moderate", action="store_true",
        help="Enable content moderation")
    args = parser.parse_args()
    logger.info(f"args: {args}")

    models = get_model_list()

    logger.info(args)
    demo = build_demo()
    demo.queue(concurrency_count=args.concurrency_count, status_update_rate=10,
               api_open=False).launch(server_name=args.host, server_port=args.port,
                                      share=args.share, max_threads=200)
