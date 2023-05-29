PROMPT_DICT = {
    "prompt_input": (
        "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Answer:\n"
    ),
    "prompt_no_input": (
        "Below is an instruction that describes a task. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\n{instruction}\n\n### Answer:\n"
    ),
}
ANSWER_TEXT = "{output}"
REVISION_TEXT = "\n\n### Revision {number}:\n{revision}"


def make_full_source(example):
    """Make prompt for self-feedback."""
    
    prompt_input, prompt_no_input = PROMPT_DICT["prompt_input"], PROMPT_DICT["prompt_no_input"]
    prompt = prompt_input.format_map(example) if example.get("input", "") != "" else prompt_no_input.format_map(example)
    return prompt


def make_full_target(example):
    """Make target for self-feedback."""
    prompt = ""
    outputs = example["outputs"]
    for i, output in enumerate(outputs):
        if i == 0:
            answer = output["output"]
            prompt += ANSWER_TEXT.format(output=answer)
        else:
            revision = output["output"]
            revision_number = i
            prompt += REVISION_TEXT.format(number=revision_number, revision=revision)
        if "feedback" in output:
            feedback = output["feedback"]
            feedback_number = i + 1
            prompt += "\n\n### Feedback {number}:\n{feedback}".format(number=feedback_number, feedback=feedback)
    
    return prompt



def make_answer_only_source(example):
    prompt_input, prompt_no_input = PROMPT_DICT["prompt_input"], PROMPT_DICT["prompt_no_input"]
    prompt = prompt_input.format_map(example) if example.get("input", "") != "" else prompt_no_input.format_map(example)

    return prompt


def make_answer_only_target(example, eos_token):
    answer = example["outputs"][0]["output"]
    prompt = "{output}".format(output=answer)

    return prompt + eos_token


if __name__ == "__main__":
    example_len2_model1 = {
        "instruction": "Write a response that appropriately completes the request.",
        "input": "This is the input.",
        "outputs": [
            {
                "output": "This is the first model output.",
                "feedback": "This is the chatGPT feedback to the first model output.",
            },
            {
                "output": "This is the second chatGPT output.",
                "feedback": "This is the chatGPT feedback to the second chatGPT output.",
            },
        ],
            "model-output-length": 1,
    }
    
    assert make_answer_only_source(example_len2_model1) == (
        "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\nWrite a response that appropriately completes the request.\n\n"
        "### Input:\nThis is the input.\n\n"
        "### Answer:\n"
    )
    assert make_answer_only_target(example_len2_model1, eos_token="</s>") == (
        "This is the first model output.</s>"
    )

    
