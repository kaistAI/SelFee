from datasets import load_dataset
import json
json_list=[]
for config_name in ["alpaca", "flan", "aqua", "conala", "dmcc", "dr_repair", "gsm8k", "math", "mbpp", "sharegpt"]
    dataset = load_dataset('kaist-ai/selfee-train')["alpaca"]
json_list.extend(dataset)
merged_json = json.dumps(json_list)

# Write the merged JSON to a new file
with open('../outputs/feedback_gpt_3.5_turbo_merged_whole.json', 'w+') as f:
    f.write(merged_json)
