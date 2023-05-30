"""This code is sourced from 4960ca7 commit of https://github.com/lm-sys/FastChat/blob/main/fastchat/eval/get_model_answer.py"""

import argparse
from transformers import AutoTokenizer, AutoModelForCausalLM, LlamaForCausalLM
import torch
import os
import json
from tqdm import tqdm
import shortuuid
import ray

from load_model import get_conversation_template


# This is only for Selfee.
def generate_with_enforced_revisions(model, tokenizer, prompt: str, temperature: float, max_new_tokens: int, max_num_revisions: int, device):

    revision_not_needed_texts = ["Revision is not needed", "revision is not needed", "No revision is needed", "no revision is needed", "No revisions needed", "no revisions needed"]
    stop_str = "</s>"
    stream_interval = 1

    l_prompt = len(prompt)
    input_ids = tokenizer(prompt).input_ids
    output_ids = list(input_ids)
    revision_not_needed_texts_ids = [tokenizer.encode(s)[2:] for s in revision_not_needed_texts]

    revision_needed_input_ids = tokenizer("Revision is needed").input_ids[2:]
                
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
            for revision_not_needed_text, revision_not_needed_text_ids in zip(revision_not_needed_texts, revision_not_needed_texts_ids):
                if revision_not_needed_text in output:
                    match_revision_not_needed_text = revision_not_needed_text
                    match_revision_not_needed_text_ids = revision_not_needed_text_ids
                    break

            if len(output.split('### Revision')) < max_num_revisions and match_revision_not_needed_text is not None:
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

        if i % stream_interval == 0 or i == max_new_tokens - 1 or stopped:
            output = tokenizer.decode(output_ids, skip_special_tokens=True)
            pos = output.rfind(stop_str, l_prompt)
            if pos != -1:
                output = output[:pos]
                stopped = True
            
        if stopped:
            return output

    return output

def parse(response):
    if "### Answer:" not in response:
        response = "N/A"
    if "### Revision" not in response:
        response = response.split('### Answer:')[1].split('\n\n### Feedback')[0]
    else: 
        revision_num = len(response.split('### Revision ')) - 1
        if '\n\n### Feedback' in response.split('### Revision ')[-1]:
            response = response.split('### Revision ')[-1].split('\n\n### Feedback')[0][1:]
        else: 
            if revision_num == 1:
                response = response.split('### Answer:')[1].split('\n\n### Feedback')[0]
            else: 
                response = response.split('### Revision ')[-2].split('\n\n### Feedback')[0][1:]

    if response.startswith(":"):
        response = response[1:]
    if response.startswith("\n"):
        response = response[1:]
    return response
    

def run_eval(model_path, model_id, question_file, answer_file, num_gpus, max_num_revisions):
    # split question file into num_gpus files
    ques_jsons = []
    with open(os.path.expanduser(question_file), "r") as ques_file:
        for line in ques_file:
            ques_jsons.append(line)

    chunk_size = len(ques_jsons) // num_gpus
    ans_handles = []
    for i in range(0, len(ques_jsons), chunk_size):
        ans_handles.append(
            get_model_answers.remote(
                model_path, model_id, ques_jsons[i : i + chunk_size], max_num_revisions
            )
        )

    ans_jsons = []
    for ans_handle in ans_handles:
        ans_jsons.extend(ray.get(ans_handle))

    with open(os.path.expanduser(answer_file), "w") as ans_file:
        for line in ans_jsons:
            ans_file.write(json.dumps(line) + "\n")


@ray.remote(num_gpus=1)
@torch.inference_mode()
def get_model_answers(model_path, model_id, question_jsons, max_num_revisions):
    model_path = os.path.expanduser(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=False)
    model = AutoModelForCausalLM.from_pretrained(
        model_path, low_cpu_mem_usage=True, torch_dtype=torch.float16
    ).cuda()

    ans_jsons = []
    for i, line in enumerate(tqdm(question_jsons)):
        ques_json = json.loads(line)
        idx = ques_json["question_id"]
        qs = ques_json["text"]
        conv = get_conversation_template(model_id)
        conv.append_message(conv.roles[0], qs)
        conv.append_message(conv.roles[1], None)
        prompt = conv.get_prompt()

        input_ids = tokenizer([prompt]).input_ids
        if 'selfee' in model_id:
            original = generate_with_enforced_revisions(
                model = model,
                tokenizer = tokenizer,
                prompt = prompt,
                temperature= 0.7, 
                max_new_tokens=2048,
                max_num_revisions=max_num_revisions+1, 
                device='cuda')
            
            outputs = parse(original)
            ans_id = shortuuid.uuid()
            ans_jsons.append(
                {
                    "question_id": idx,
                    "whole_generation": original,
                    "text": outputs,
                    "answer_id": ans_id,
                    "model_id": model_id,
                    "metadata": {},
                }
            )
            
        else: 

            output_ids = model.generate(
                torch.as_tensor(input_ids).cuda(),
                do_sample=True,
                temperature=0.7,
                max_new_tokens=1024,
            )
        
            output_ids = output_ids[0][len(input_ids[0]) :]
            outputs = tokenizer.decode(output_ids, skip_special_tokens=True).strip()

            ans_id = shortuuid.uuid()
            ans_jsons.append(
                {
                    "question_id": idx,
                    "text": outputs,
                    "answer_id": ans_id,
                    "model_id": model_id,
                    "metadata": {},
                }
            )
    return ans_jsons


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", type=str, required=True)
    parser.add_argument("--model-id", type=str, required=True)
    parser.add_argument("--question-file", type=str, required=True)
    parser.add_argument("--answer-file", type=str, default="answer.jsonl")
    parser.add_argument("--num-gpus", type=int, default=1)
    parser.add_argument("--max-num-revisions", type=int, default=3)
    args = parser.parse_args()

    ray.init()
    run_eval(
        args.model_path,
        args.model_id,
        args.question_file,
        args.answer_file,
        args.num_gpus,
        args.max_num_revisions
    )