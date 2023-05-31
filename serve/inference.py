"""Inference for FastChat models."""
import abc
import torch
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, LlamaTokenizer, AutoModel
except ImportError:
    from transformers import AutoTokenizer, AutoModelForCausalLM, LLaMATokenizer, AutoModel
from serve.conversation import conv_templates, SeparatorStyle
from serve.monkey_patch_non_inplace import replace_llama_attn_with_non_inplace_operations

import logging

def load_model(model_path, device, num_gpus, load_8bit=False, debug=False):
    if device == "cpu":
        kwargs = {}
    elif device == "cuda":
        kwargs = {"torch_dtype": torch.float16}
        if num_gpus == "auto":
            kwargs["device_map"] = "auto"
        else:
            num_gpus = int(num_gpus)
            if num_gpus != 1:
                kwargs.update({
                    "device_map": "auto",
                    "max_memory": {i: "13GiB" for i in range(num_gpus)},
                })
    elif device == "mps":
        kwargs = {"torch_dtype": torch.float16}
        # Avoid bugs in mps backend by not using in-place operations.
        replace_llama_attn_with_non_inplace_operations()
    else:
        raise ValueError(f"Invalid device: {device}")

    tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=False)
    model = AutoModelForCausalLM.from_pretrained(model_path,
        low_cpu_mem_usage=True, **kwargs)

    if (device == "cuda" and num_gpus == 1) or device == "mps":
        model.to(device)

    if debug:
        print(model)

    return model, tokenizer


@torch.inference_mode()
def generate_stream(model, tokenizer, params, device,
                    context_len=2048, stream_interval=2):

    min_num_revisions = 1
    max_num_revisions = 3

    max_num_bubbles = max_num_revisions * 2  # feedbacks and revisions

    prompt = params["prompt"]
    l_prompt = len(prompt)
    temperature = float(params.get("temperature", 1.0))
    max_new_tokens = int(params.get("max_new_tokens", 256))
    stop_str = params.get("stop", None)

    input_ids = tokenizer(prompt).input_ids
    output_ids = list(input_ids)

    max_src_len = context_len - max_new_tokens - 8
    input_ids = input_ids[-max_src_len:]

    revision_not_needed_texts = ["Revision is not needed", "revision is not needed", "No revision is needed", "no revision is needed", "No revisions needed", "no revisions needed"]
    revision_not_needed_texts_ids = [tokenizer.encode(s)[2:] for s in revision_not_needed_texts]
    
    revision_needed_input_ids = tokenizer("Revision is needed").input_ids[2:]

    current_num_revisions = len(prompt.split('### Revision'))
    current_bubbles = len(prompt.split('###'))
    
    min_num_revisions += current_num_revisions
    max_num_bubbles += current_bubbles

    for i in range(max_new_tokens):
        if i == 0:
            out = model(
                torch.as_tensor([input_ids], device=device), use_cache=True)
            logits = out.logits
            past_key_values = out.past_key_values
        else:
            attention_mask = torch.ones(
                1, past_key_values[0][0].shape[-2] + 1, device=device)
            out = model(input_ids=torch.as_tensor([[token]], device=device),
                        use_cache=True,
                        attention_mask=attention_mask,
                        past_key_values=past_key_values)
            logits = out.logits
            past_key_values = out.past_key_values

        last_token_logits = logits[0][-1]

        if device == "mps":
            # Switch to CPU by avoiding some bugs in mps backend.
            last_token_logits = last_token_logits.float().to("cpu")

        if temperature < 1e-4:
            token = int(torch.argmax(last_token_logits))
        else:
            probs = torch.softmax(last_token_logits / temperature, dim=-1)
            token = int(torch.multinomial(probs, num_samples=1))

        output_ids.append(token)

        if token == tokenizer.eos_token_id:
            stopped = True
        else:
            stopped = False

        if i % stream_interval == 0 or i == max_new_tokens - 1:
            output = tokenizer.decode(output_ids, skip_special_tokens=True)
            output_ids_string = " ".join([str(output_id) for output_id in output_ids])

            match_revision_not_needed_text = None
            match_revision_not_needed_text_ids = None    
            if len(output.split('### Revision')) < min_num_revisions:
                for revision_not_needed_text, revision_not_needed_text_ids in zip(revision_not_needed_texts, revision_not_needed_texts_ids):
                    if revision_not_needed_text in output:
                        # print("@@@", output, revision_not_needed_text)
                        match_revision_not_needed_text = revision_not_needed_text
                        match_revision_not_needed_text_ids = revision_not_needed_text_ids

                        logging.error(f"matched revision not needed | {match_revision_not_needed_text} | {output}")

                        break
            
            if match_revision_not_needed_text is not None:
                match_revision_not_needed_text_ids_string = " ".join([str(match_revision_not_needed_text_id) for match_revision_not_needed_text_id in match_revision_not_needed_text_ids])
                revision_not_needed_pos = output_ids_string.rfind(match_revision_not_needed_text_ids_string)
                output_ids_trunc = [int(temp_output_id) for temp_output_id in output_ids_string[:revision_not_needed_pos].strip().split(" ")]
                back_len = len(output_ids) - len(output_ids_trunc)

                output_ids = output_ids_trunc + revision_needed_input_ids

                new_past_key_values = []
                for layer_past_key_values in past_key_values:
                    new_layer_past_key_values = []
                    for past in layer_past_key_values:
                        new_past = past[:, :, :past.size(2) - back_len, :]
                        new_layer_past_key_values.append(new_past)
                    new_past_key_values.append(new_layer_past_key_values)
                past_key_values = new_past_key_values

                attention_mask = torch.ones(
                    1, past_key_values[0][0].shape[-2] + len(revision_needed_input_ids), device=device)
                out = model(input_ids=torch.as_tensor([revision_needed_input_ids], device=device),
                            use_cache=True,
                            attention_mask=attention_mask,
                            past_key_values=past_key_values)
                logits = out.logits
                past_key_values = out.past_key_values
                
                last_token_logits = logits[0][-1]
                
                if device == "mps":
                    # Switch to CPU by avoiding some bugs in mps backend.
                    last_token_logits = last_token_logits.float().to("cpu")

                if temperature < 1e-4:
                    token = int(torch.argmax(last_token_logits))
                else:
                    probs = torch.softmax(last_token_logits / temperature, dim=-1)
                    token = int(torch.multinomial(probs, num_samples=1))

                output_ids.append(token)

                stopped = False

            if len(output.split('###')) > max_num_bubbles:
                logging.error(f"max_num_bubbles exceeded | {output}")
                stopped = True

        if i % stream_interval == 0 or i == max_new_tokens - 1 or stopped:
            output = tokenizer.decode(output_ids, skip_special_tokens=True)
            output = "###".join(output.split('###')[:max_num_bubbles])
            pos = output.rfind(stop_str, l_prompt)
            if pos != -1:
                output = output[:pos]
                stopped = True
            yield output

        if stopped:
            break

    del past_key_values


class ChatIO(abc.ABC):
    @abc.abstractmethod
    def prompt_for_input(self, role: str) -> str:
        """Prompt for input from a role."""

    @abc.abstractmethod
    def prompt_for_output(self, role: str):
        """Prompt for output from a role."""

    @abc.abstractmethod
    def stream_output(self, output_stream, skip_echo_len: int):
        """Stream output."""


def chat_loop(model_path: str, device: str, num_gpus: str, load_8bit: bool,
              conv_template: str, temperature: float, max_new_tokens: int,
              chatio: ChatIO, debug: bool):
    # Model
    model, tokenizer = load_model(model_path, device,
        num_gpus, load_8bit, debug)
    
    # Chat
    conv = conv_templates[conv_template].copy()
    while True:
        try:
            inp = chatio.prompt_for_input(conv.roles[0])
        except EOFError:
            inp = ""
        if not inp:
            print("exit...")
            break

        conv.append_message(conv.roles[0], inp)
        conv.append_message(conv.roles[1], None)

        generate_stream_func = generate_stream
        prompt = conv.get_prompt()
        skip_echo_len = len(prompt.replace("</s>", " ")) + 1

        params = {
            "model": model_path,
            "prompt": prompt,
            "temperature": temperature,
            "max_new_tokens": max_new_tokens,
            "stop": conv.sep if conv.sep_style == SeparatorStyle.SINGLE else conv.sep2,
        }

        chatio.prompt_for_output(conv.roles[1])
        output_stream = generate_stream_func(model, tokenizer, params, device)
        outputs = chatio.stream_output(output_stream, skip_echo_len)
        # NOTE: strip is important to align with the training data.
        conv.messages[-1][-1] = outputs.strip()

        # if debug:
        #     print("\n", {"prompt": prompt, "outputs": outputs}, "\n")
