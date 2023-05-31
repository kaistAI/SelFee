from datasets import load_dataset
import json
dataset = load_dataset('kaist-ai/selfee-train')["train"]


# Write the merged JSON to a new file
with open('../outputs/feedback_gpt_3.5_turbo_merged_whole.json', 'w+') as f:
    json.dump(dataset, f)