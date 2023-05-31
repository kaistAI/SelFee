import json

# Load JSON files into variables
json_list = []
for filename in ['../outputs/alpaca/feedback_gpt_3.5_turbo_alpaca.jsonl',
'../outputs/flan+code+math/feedback_gpt_3.5_turbo_aqua.jsonl',
'../outputs/flan+code+math/feedback_gpt_3.5_turbo_conala.jsonl',
'../outputs/flan+code+math/feedback_gpt_3.5_turbo_dmcc.jsonl',
'../outputs/flan+code+math/feedback_gpt_3.5_turbo_dr_repair.jsonl',
'../outputs/flan+code+math/feedback_gpt_3.5_turbo_flan.jsonl',
'../outputs/flan+code+math/feedback_gpt_3.5_turbo_gsm8k.jsonl',
'../outputs/flan+code+math/feedback_gpt_3.5_turbo_math_hendrycks.jsonl',
'../outputs/flan+code+math/feedback_gpt_3.5_turbo_mbpp.jsonl',
'../outputs/sharegpt/feedback_gpt_3.5_turbo_sharegpt_90k_processed.jsonl']:
    with open(filename, 'r') as f:
        for line in f:
            item =json.loads(line)
            item["dataset"]=filename.split('_')[-1].split('.')[0]
            # print(item["dataset_name"])
            json_list.append(item)
# Convert merged list back into a JSON string


# Write the merged JSON to a new file
with open('feedback_gpt_3.5_turbo_merged_whole.json', 'w+') as f:
    json.dump(json_list, f)
    print(len(json_list))
