We provide code for augmenting ChatGPT response starting from the original query. 
1. set OPEN_API_KEYS as list of usable openai api keys, divided by comma
'''export OPEN_API_KEYS={api key 1},{api key 2}, ...'''
2. 
'''
python call_openai_multiprocessing_alpaca.py --input-path --output-path --fail-path
'''
3. 