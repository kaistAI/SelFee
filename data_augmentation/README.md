We provide code for augmenting ChatGPT response starting from the original query. 
1. You need to get your API key to get access to the GPT-4 API.
```
export OPENAI_API_KEYS={personal_key}
```
2. You need to set 3 arguments when augmenting the training dataset. 
'input-path'
path of your raw dataset
'output-path'
path where you save after augmenting
'fail-path'
path where augmentation is failed instances are collected(mainly due to the token length limit or api key error)

For example, you can input the following command for augmenting training dataset for alpaca query.
```
python call_openai_multiprocessing_alpaca.py --input-path ../outputs/raw/alpaca_data.json --output-path ../outputs/alpaca/feedback_gpt_3.5_turbo_alpaca.jsonl --fail-path ../outputs/alpaca/feedback_gpt_3.5_turbo_alpaca_fail.jsonl
```
For flan/math/code dataset, you input the following command. For flan collection dataset, for example, you have:
```
python call_openai_multiprocessing_flan.py --input-path ../outputs/raw/flan_collection.json --output-path ../outputs/flan+code+math/feedback_gpt_3.5_turbo_flan.jsonl --fail-path ../outputs/flan+code+math/feedback_gpt_3.5_turbo_flan_fail.jsonl
```
For ShareGPT dataset, you input the following command:
```
python call_openai_multiprocessing_sharegpt.py --input-path ../outputs/raw/sharegpt_90k_processed.jsonl --output-path ../outputs/sharegpt/feedback_gpt_3.5_turbo_sharegpt.jsonl --fail-path ../outputs/sharegpt/feedback_gpt_3.5_turbo_sharegpt_fail.jsonl
```
3. If there is a failed instance, you can input the following command to redo the augmenting process for failed instance. For example, for alpaca query, you can do:
```
python call_openai_multiprocessing_alpaca.py --input-path ../outputs/alpaca/feedback_gpt_3.5_turbo_alpaca_fail.jsonl --output-path ../outputs/alpaca/feedback_gpt_3.5_turbo_alpaca.jsonl --fail-path ../outputs/alpaca/feedback_gpt_3.5_turbo_alpaca_fail2.jsonl
```