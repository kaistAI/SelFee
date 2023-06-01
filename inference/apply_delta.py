"""This code is sourced from 7a95b21 commit of https://github.com/tatsu-lab/stanford_alpaca/blob/main/weight_diff.py

Apply the delta weights on top of a base model.

"""
import sys
sys.path.append('../train')

from typing import Optional

import fire
import torch
import tqdm
import transformers
from train import smart_tokenizer_and_embedding_resize




@torch.inference_mode()
def recover(
    path_raw,
    path_diff,
    path_tuned: Optional[str] = None,
    device="cpu",
    test_inference=True
):
    """Recover the original weights from the released weight diff.

    This function is given for you to run.

    Things to do before running this:
        1. Convert Meta's released weights into huggingface format. Follow this guide:
            https://huggingface.co/docs/transformers/main/model_doc/llama
        2. Make sure you cloned the released weight diff into your local machine. The 7B and 13B weight diff are located at:
            https://huggingface.co/kaist-ai/selfee-7b-delta/tree/main
            and
            https://huggingface.co/kaist-ai/selfee-13b-delta/tree/main, respectively.
        3. Run this function with the correct paths. E.g.,
            python apply_delta.py --path_raw <path_to_step_1_dir> --path_diff <path_to_step_2_dir>

    Additional notes:
        - If things run too slowly, and you have an 80G GPU lying around, let GPU go brrr by setting `--device "cuda"`.
        - If you want to save the recovered weights, set `--path_tuned <your_path_tuned>`.
            Next time you can load the recovered weights directly from `<your_path_tuned>`.
    """
    model_raw: transformers.PreTrainedModel = transformers.AutoModelForCausalLM.from_pretrained(
        path_raw,
        device_map={"": torch.device(device)},
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True,
    )
    model_recovered: transformers.PreTrainedModel = transformers.AutoModelForCausalLM.from_pretrained(
        path_diff,
        device_map={"": torch.device(device)},
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True,
    )

    tokenizer_raw: transformers.PreTrainedTokenizer = transformers.AutoTokenizer.from_pretrained(
        path_raw, use_fast =False
    )
    if tokenizer_raw.pad_token is None:
        smart_tokenizer_and_embedding_resize(
            special_tokens_dict=dict(pad_token="[PAD]"),
            model=model_raw,
            tokenizer=tokenizer_raw,
        )
    tokenizer_recovered: transformers.PreTrainedTokenizer = transformers.AutoTokenizer.from_pretrained(
        path_diff, use_fast =False
    )

    state_dict_recovered = model_recovered.state_dict()
    state_dict_raw = model_raw.state_dict()
    for key in tqdm.tqdm(state_dict_recovered):
        state_dict_recovered[key].add_(state_dict_raw[key])


    if path_tuned is not None:
        model_recovered.save_pretrained(path_tuned)
        tokenizer_recovered.save_pretrained(path_tuned)

    # if test_inference:
    #     input_text = (
    #         "Below is an instruction that describes a task. "
    #         "Write a response that appropriately completes the request.\r\n\r\n"
    #         "### Instruction:\r\nList three technologies that make life easier.\r\n\r\n### Response:"
    #     )
    #     inputs = tokenizer_recovered(input_text, return_tensors="pt")
    #     out = model_recovered.generate(inputs=inputs.input_ids, max_new_tokens=2048)
    #     output_text = tokenizer_recovered.batch_decode(out, skip_special_tokens=True)[0]
    #     output_text = output_text[len(input_text) :]
    #     print(f"Input: {input_text}\nCompletion: {output_text}")

    return model_recovered, tokenizer_recovered


def main(**kwargs):
    recover(**kwargs)


if __name__ == "__main__":
    fire.Fire(main)