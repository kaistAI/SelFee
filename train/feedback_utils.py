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


def make_full_after_answer_source(example):
    """Make prompt for self-feedback."""
    
    prompt_input, prompt_no_input = PROMPT_DICT["prompt_input"], PROMPT_DICT["prompt_no_input"]
    prompt = prompt_input.format_map(example) if example.get("input", "") != "" else prompt_no_input.format_map(example)

    outputs = example["outputs"]
    output = outputs[0]
    answer = output["output"]
    prompt += ANSWER_TEXT.format(output=answer)

    return prompt


def make_full_after_answer_target(example):
    """Make target for self-feedback."""
    prompt = ""
    outputs = example["outputs"]
    for i, output in enumerate(outputs):
        if i == 0:
            pass
        else:
            revision = output["output"]
            revision_number = i
            prompt += REVISION_TEXT.format(number=revision_number, revision=revision)
        feedback = output["feedback"]
        feedback_number = i + 1
        prompt += "\n\n### Feedback {number}:\n{feedback}".format(number=feedback_number, feedback=feedback)
    
    return prompt


def make_FAF_source(example):
    """Make prompt for self-feedback."""
    
    prompt_input, prompt_no_input = PROMPT_DICT["prompt_input"], PROMPT_DICT["prompt_no_input"]
    prompt = prompt_input.format_map(example) if example.get("input", "") != "" else prompt_no_input.format_map(example)

    source_outputs = example["outputs"][:-1]
    last_index = len(source_outputs) - 1
    for i, output in enumerate(source_outputs):
        if i == 0:
            answer = output["output"]
            prompt += ANSWER_TEXT.format(output=answer)
        else:
            revision = output["output"]
            revision_number = i
            prompt += REVISION_TEXT.format(number=revision_number, revision=revision)
        
        if i < last_index:
            feedback = output["feedback"]
            feedback_number = i + 1
            prompt += "\n\n### Feedback {number}:\n{feedback}".format(number=feedback_number, feedback=feedback)
        else:
            feedback_number = i + 1
            prompt += "\n\n### Feedback {number}:\n".format(number=feedback_number)

    return prompt


def make_FAF_target(example):
    """Make target for self-feedback."""
    prompt = ""
    target_outputs = example["outputs"][-2:]

    length = len(example["outputs"])

    if len(target_outputs) == 1:
        output = target_outputs[0]
        answer = output["output"]
        prompt += ANSWER_TEXT.format(output=answer)
        feedback = output["feedback"]
        feedback_number = length
        prompt += "\n\n### Feedback {number}:\n{feedback}".format(number=feedback_number, feedback=feedback)
    else:
        previous_feedback = target_outputs[0]["feedback"]
        prompt += "{feedback}".format(feedback=previous_feedback)
        next_revision = target_outputs[1]["output"]
        next_revision_number = length - 1
        prompt += REVISION_TEXT.format(number=next_revision_number, revision=next_revision)
        next_feedback = target_outputs[1]["feedback"]
        next_feedback_number = length
        prompt += "\n\n### Feedback {number}:\n{feedback}".format(number=next_feedback_number, feedback=next_feedback)

    return prompt


def make_split_example(example, eos_token: str):
    prompt_input, prompt_no_input = PROMPT_DICT["prompt_input"], PROMPT_DICT["prompt_no_input"]
    base_prompt = prompt_input.format_map(example) if example.get("input", "") != "" else prompt_no_input.format_map(example)

    sources = []
    targets = []

    outputs = example["outputs"]

    source = base_prompt
    target = ""
    answer = outputs[0]["output"]
    target += ANSWER_TEXT.format(output=answer)
    feedback = outputs[0]["feedback"]
    feedback_number = 1
    target += "\n\n### Feedback {number}:\n{feedback}".format(number=feedback_number, feedback=feedback)
    if len(outputs) > 1:
        revision = outputs[1]["output"]
        revision_number = 1
        target += REVISION_TEXT.format(number=revision_number, revision=revision)
    else:
        target += f"{eos_token}"

    sources.append(source)
    targets.append(target)

    if len(outputs) > 1:
        source = base_prompt
        answer = outputs[1]["output"]
        source += ANSWER_TEXT.format(output=answer)
        feedback_number = 1
        source += "\n\n### Feedback {number}:\n".format(number=feedback_number)

        target = ""
        feedback = outputs[1]["feedback"]
        feedback_number = 1
        target += "{feedback}".format(number=feedback_number, feedback=feedback)
        if len(outputs) > 2:
            revision = outputs[2]["output"]
            revision_number = 1
            target += REVISION_TEXT.format(number=revision_number, revision=revision)
        else:
            target += f"{eos_token}"

        sources.append(source)
        targets.append(target)
    if len(outputs) > 2:
        source = base_prompt
        answer = outputs[2]["output"]
        source += ANSWER_TEXT.format(output=answer)
        feedback_number = 1
        source += "\n\n### Feedback {number}:\n".format(number=feedback_number)

        target = ""
        feedback = outputs[2]["feedback"]
        feedback_number = 1
        target += "{feedback}".format(number=feedback_number, feedback=feedback)
        if len(outputs) > 3:
            revision = outputs[3]["output"]
            revision_number = 1
            target += REVISION_TEXT.format(number=revision_number, revision=revision)
        else:
            target += f"{eos_token}"

        sources.append(source)
        targets.append(target)

    assert len(outputs) < 4, "This function only supports up to 3 revisions."

    return sources, targets


def make_continual_active_source(example):
    prompt_input, prompt_no_input = PROMPT_DICT["prompt_input"], PROMPT_DICT["prompt_no_input"]
    prompt = prompt_input.format_map(example) if example.get("input", "") != "" else prompt_no_input.format_map(example)

    model_output_length = example["model-output-length"]
    assert model_output_length <= 2, "This function only supports up to 2 model-output-length."
    assert model_output_length <= len(example["outputs"]), f"model-output-length must be less than or equal to the number of outputs. error example: {example}"

    if model_output_length == 0:
        pass
    elif model_output_length == 1:
        answer = example["outputs"][0]["output"]
        prompt += "{output}".format(output=answer)
        prompt += "\n\n### Feedback 1:\n"
    elif model_output_length == 2:
        answer = example["outputs"][0]["output"]
        prompt += "{output}".format(output=answer)
        prompt += "\n\n### Feedback 1:\n"
        feedback = example["outputs"][0]["feedback"]
        prompt += "{feedback}".format(feedback=feedback)
        revision = example["outputs"][1]["output"]
        revision_number = 1
        prompt += "\n\n### Revision {number}:\n{revision}".format(number=revision_number, revision=revision)
        prompt += "\n\n### Feedback 2:\n"

    return prompt


def make_continual_active_target(example, eos_token):
    model_output_length = example["model-output-length"]
    assert model_output_length <= 2, "This function only supports up to 2 model-output-length."

    prompt = ""

    outputs = example["outputs"]
    for i, output in enumerate(outputs):
        if i < model_output_length - 1:
            continue

        if i >= model_output_length:
            if i == 0:
                answer = output["output"]
                prompt += ANSWER_TEXT.format(output=answer)
            else:
                revision = output["output"]
                revision_number = i
                prompt += REVISION_TEXT.format(number=revision_number, revision=revision)
        
        if i == model_output_length - 1:
            feedback = output["feedback"]
            prompt += "{feedback}".format(feedback=feedback)
        else:
            feedback = output["feedback"]
            feedback_number = i + 1
            prompt += "\n\n### Feedback {number}:\n{feedback}".format(number=feedback_number, feedback=feedback)

    prompt += f"{eos_token}"
    
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
    example1 = {
        "instruction": "Write a response that appropriately completes the request.",
        "input": "This is the input.",
        "outputs": [
            {
                "output": "This is the first output.",
                "feedback": "This is the first feedback.",
            },
        ],
    }
    assert make_full_after_answer_source(example1) == (
        "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\nWrite a response that appropriately completes the request.\n\n"
        "### Input:\nThis is the input.\n\n"
        "### Answer:\nThis is the first output."
    )
    assert make_full_after_answer_target(example1) == (
        "\n\n### Feedback 1:\nThis is the first feedback."
    )

    assert make_FAF_source(example1) == (
        "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\nWrite a response that appropriately completes the request.\n\n"
        "### Input:\nThis is the input.\n\n"
        "### Answer:\n"
    )
    assert make_FAF_target(example1) == (
        "This is the first output.\n\n"
        "### Feedback 1:\nThis is the first feedback."
    )
    assert len(make_split_example(example1, eos_token="</s>")[0]) == 1
    assert make_split_example(example1, eos_token="</s>")[0][0] == make_full_source(example1)
    assert make_split_example(example1, eos_token="</s>")[1][0] == make_full_target(example1) + "</s>"
    
    example2 = {
        "instruction": "Write a response that appropriately completes the request.",
        "input": "This is the input.",
        "outputs": [
            {
                "output": "This is the first output.",
                "feedback": "This is the first feedback.",
            },
            {
                "output": "This is the second output.",
                "feedback": "This is the second feedback.",
            },
        ],
    }
    assert len(make_split_example(example2, eos_token="</s>")[0]) == 2
    assert make_split_example(example2, eos_token="</s>")[0][0] == (
        "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\nWrite a response that appropriately completes the request.\n\n"
        "### Input:\nThis is the input.\n\n"
        "### Answer:\n"
    )
    assert make_split_example(example2, eos_token="</s>")[1][0] == (
        "This is the first output.\n\n"
        "### Feedback 1:\nThis is the first feedback.\n\n"
        "### Revision 1:\nThis is the second output."
    )
    assert make_split_example(example2, eos_token="</s>")[0][1] == (
        "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\nWrite a response that appropriately completes the request.\n\n"
        "### Input:\nThis is the input.\n\n"
        "### Answer:\n"
        "This is the second output.\n\n"
        "### Feedback 1:\n"
    )
    assert make_split_example(example2, eos_token="</s>")[1][1] == (
        "This is the second feedback.</s>"
    )

    example3 = {
        "instruction": "Write a response that appropriately completes the request.",
        "input": "This is the input.",
        "outputs": [
            {
                "output": "This is the first output.",
                "feedback": "This is the first feedback.",
            },
            {
                "output": "This is the second output.",
                "feedback": "This is the second feedback.",
            },
            {
                "output": "This is the third output.",
                "feedback": "This is the third feedback.",
            },
        ],
    }
    assert make_FAF_source(example3) == (
        "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\nWrite a response that appropriately completes the request.\n\n"
        "### Input:\nThis is the input.\n\n"
        "### Answer:\n"
        "This is the first output.\n\n"
        "### Feedback 1:\n"
        "This is the first feedback.\n\n"
        "### Revision 1:\nThis is the second output.\n\n"
        "### Feedback 2:\n"
    )
    assert make_FAF_target(example3) == (
        "This is the second feedback.\n\n"
        "### Revision 2:\nThis is the third output.\n\n"
        "### Feedback 3:\nThis is the third feedback."
    )
    assert len(make_split_example(example3, eos_token="</s>")[0]) == 3
    assert make_split_example(example3, eos_token="</s>")[0][0] == (
        "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\nWrite a response that appropriately completes the request.\n\n"
        "### Input:\nThis is the input.\n\n"
        "### Answer:\n"
    )
    assert make_split_example(example3, eos_token="</s>")[1][0] == (
        "This is the first output.\n\n"
        "### Feedback 1:\nThis is the first feedback.\n\n"
        "### Revision 1:\nThis is the second output."
    )
    assert make_split_example(example3, eos_token="</s>")[0][1] == (
        "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\nWrite a response that appropriately completes the request.\n\n"
        "### Input:\nThis is the input.\n\n"
        "### Answer:\nThis is the second output.\n\n"
        "### Feedback 1:\n"
    )
    assert make_split_example(example3, eos_token="</s>")[1][1] == (
        "This is the second feedback.\n\n"
        "### Revision 1:\nThis is the third output."
    )
    assert make_split_example(example3, eos_token="</s>")[0][2] == (
        "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\nWrite a response that appropriately completes the request.\n\n"
        "### Input:\nThis is the input.\n\n"
        "### Answer:\n"
        "This is the third output.\n\n"
        "### Feedback 1:\n"
    )
    assert make_split_example(example3, eos_token="</s>")[1][2] == (
        "This is the third feedback.</s>"
    )

    example_len1_model0 = {
        "instruction": "Write a response that appropriately completes the request.",
        "input": "This is the input.",
        "outputs": [
            {
                "output": "This is the first chatGPT output.",
                "feedback": "This is the chatGPT feedback to the first chatGPT output.",
            },
        ],
        "model-output-length": 0,
    }
    assert make_continual_active_source(example_len1_model0) == (
        "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\nWrite a response that appropriately completes the request.\n\n"
        "### Input:\nThis is the input.\n\n"
        "### Answer:\n"
    )
    assert make_continual_active_target(example_len1_model0, eos_token="</s>") == (
        "This is the first chatGPT output.\n\n"
        "### Feedback 1:\nThis is the chatGPT feedback to the first chatGPT output.</s>"
    )
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
    assert make_continual_active_source(example_len2_model1) == (
        "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\nWrite a response that appropriately completes the request.\n\n"
        "### Input:\nThis is the input.\n\n"
        "### Answer:\nThis is the first model output.\n\n"
        "### Feedback 1:\n"
    )
    assert make_continual_active_target(example_len2_model1, eos_token="</s>") == (
        "This is the chatGPT feedback to the first model output.\n\n"
        "### Revision 1:\nThis is the second chatGPT output.\n\n"
        "### Feedback 2:\nThis is the chatGPT feedback to the second chatGPT output.</s>"
    )
    example_len2_model0 = {
        "instruction": "Write a response that appropriately completes the request.",
        "input": "This is the input.",
        "outputs": [
            {
                "output": "This is the first output.",
                "feedback": "This is the feedback to the first output.",
            },
            {
                "output": "This is the second output.",
                "feedback": "This is the feedback to the second output.",
            },
        ],
            "model-output-length": 0
    }
    assert make_continual_active_source(example_len2_model0) == (
        "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\nWrite a response that appropriately completes the request.\n\n"
        "### Input:\nThis is the input.\n\n"
        "### Answer:\n"
    )
    assert make_continual_active_target(example_len2_model0, eos_token="</s>") == (
        "This is the first output.\n\n"
        "### Feedback 1:\nThis is the feedback to the first output.\n\n"
        "### Revision 1:\nThis is the second output.\n\n"
        "### Feedback 2:\nThis is the feedback to the second output.</s>"
    )
    
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
    example_len1_model1 = {
        "iteration_truncated": False, 
        "instruction": "Given the input, revise and reformat the following sentence.", 
        "input": "Sentence: Here\u2019s the rundown- on the best times- to visit Australia", 
        "iteration": 1, 
        "outputs": [
            {
                "output": "The rundown on the best times to visit Australia is as follows:",
                "feedback": "The proposed revision is clear, concise and grammatically correct. It effectively conveys the message of the original sentence while also improving the structure and clarity of the sentence. Score: 9. Revision is not needed."
            }
        ], 
        "model-output-length": 1
    }
    assert make_continual_active_source(example_len1_model1) == (
        "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\nGiven the input, revise and reformat the following sentence.\n\n"
        "### Input:\nSentence: Here\u2019s the rundown- on the best times- to visit Australia\n\n"
        "### Answer:\nThe rundown on the best times to visit Australia is as follows:\n\n"
        "### Feedback 1:\n"
    )
    assert make_continual_active_target(example_len1_model1, eos_token="</s>") == (
        "The proposed revision is clear, concise and grammatically correct. It effectively conveys the message of the original sentence while also improving the structure and clarity of the sentence. Score: 9. Revision is not needed.</s>"
    )
    example_len3_model2 = {
        "instruction": "Write a response that appropriately completes the request.",
        "input": "This is the input.",
        "outputs": [
            {
                "output": "This is the first model output.",
                "feedback": "This is the feedback to the first model output.",
            },
            {
                "output": "This is the second model output.",
                "feedback": "This is the feedback to the second output.",
            },
            {
                "output": "This is the third output.",
                "feedback": "This is the feedback to the third output.",
            },
        ],
            "model-output-length": 2,
    }
    assert make_continual_active_source(example_len3_model2) == (
        "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\nWrite a response that appropriately completes the request.\n\n"
        "### Input:\nThis is the input.\n\n"
        "### Answer:\nThis is the first model output.\n\n"
        "### Feedback 1:\nThis is the feedback to the first model output.\n\n"
        "### Revision 1:\nThis is the second model output.\n\n"
        "### Feedback 2:\n"
    ), repr(make_continual_active_source(example_len3_model2))
    assert make_continual_active_target(example_len3_model2, eos_token="</s>") == (
        "This is the feedback to the second output.\n\n"
        "### Revision 2:\nThis is the third output.\n\n"
        "### Feedback 3:\nThis is the feedback to the third output.</s>"
    ), repr(make_continual_active_target(example_len3_model2, eos_token="</s>"))
    
