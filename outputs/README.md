We provide each preprocessed dataset in this directory. We also provide some of the raw datasets that are used to proceed the data augmentation step. Dataset that are omitted are accessible from each site.
1. Math
Aqua: https://huggingface.co/datasets/aqua_rat
GSM8K: https://huggingface.co/datasets/gsm8k
Math: https://github.com/hendrycks/math
2. Code
Conala: https://huggingface.co/datasets/neulab/conala
Mbpp: https://huggingface.co/datasets/mbpp
DrRepair: https://github.com/michiyasunaga/DrRepair
DeepMind CodeContests: https://github.com/deepmind/code_contests
3. ShareGPT
https://github.com/lm-sys/FastChat/issues/90

How to make the training dataset for our model:
1. unzip alpaca and sharegpt dataset
'''
tar -zxvf alpaca/alpaca.tar.gz
tar -zxvf sharegpt/sharegpt.tar.gz
'''
2. merge all the preprocessed dataset into one
'''
python merge_data.py
'''