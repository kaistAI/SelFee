import json

# Load JSON files into variables
json_list = []
for filename in ['../outputs/feedback_gpt_3.5_turbo_llama.jsonl',
'../outputs/flan+code+math/feedback_gpt_3.5_turbo_aqua.jsonl',
'../outputs/flan+code+math/feedback_gpt_3.5_turbo_conala.jsonl',
'../outputs/flan+code+math/feedback_gpt_3.5_turbo_dmcc.jsonl',
'../outputs/flan+code+math/feedback_gpt_3.5_turbo_dr_repair.jsonl',
'../outputs/flan+code+math/feedback_gpt_3.5_turbo_flan.jsonl',
'../outputs/flan+code+math/feedback_gpt_3.5_turbo_gsm8k.jsonl',
'../outputs/flan+code+math/feedback_gpt_3.5_turbo_math_hendrycks.jsonl',
'../outputs/flan+code+math/feedback_gpt_3.5_turbo_mbpp.jsonl',
'../outputs/feedback_gpt_3.5_turbo_sharegpt_90k_processed.json']:
    with open(filename, 'r') as f:
        new_list = json.loads(f.read())
    json_list.extend(new_list)

# Convert merged list back into a JSON string
merged_json = json.dumps(json_list)

# Write the merged JSON to a new file
with open('feedback_gpt_3.5_turbo_merged_whole.json', 'w+') as f:
    f.write(merged_json)
