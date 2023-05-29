
import openai
import re
import time
import json
from openai.error import Timeout
import jsonlines
import numpy as np
import os

from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_chain, wait_fixed
# from utils import *
from collections import Counter
import random

# parse arguments
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--api_key', type=str, required=True)
parser.add_argument('--output_path', type=str, default="../outputs/feedback_gpt_3.5_turbo_llama_.json")
parser.add_argument(
        "--model",
        "-m",
        type=str
            )

args = parser.parse_args()




# function to compare two files and do a/b test using ChatGPT API
def clean_prediction(file1):
    with open(file1) as f1:
        lines1 = f1.readlines()

        with jsonlines.open(f"table/answer/{file1.split('/')[2].split('.jsonl')[0]}_clean.jsonl", mode="w") as outfile:
        # with jsonlines.open(f"evaluation/abtest/{file1.split('/')[2].split('.jsonl')[0]}_{file2.split('/')[2].split('.jsonl')[0]}_comparison.jsonl", mode="a") as outfile:
            for i in range(80):
                data1 = json.loads(lines1[i])
                # data2 = json.loads(lines2[i])
                
                # if data1["query"] != data2["query"]:
                #     continue
                    
                query = data1["question_id"]
                response1 = data1["text"]


                if "### Answer:" not in response1:
                    continue
                if "### Revision" not in response1:
                    response1 = response1.split('### Answer:')[1].split('\n\n### Feedback')[0]
                # elif "### Revision 2:\n'" not in response1: 
                #     response1 = response1.split('### Revision 1:\n')[1].split('\n\n### Feedback 2:')[0]
                else: 
                    # response1 = response1.split('### Revision 2:\n')[1].split('\n\n### Feedback 3:')[0]
                    revision_num = len(response1.split('### Revision ')) - 1
                    if '\n\n### Feedback' in response1.split('### Revision ')[-1]:
                        response1 = response1.split('### Revision ')[-1].split('\n\n### Feedback')[0][1:]
                    else: 
                        if revision_num == 1:
                            response1 = response1.split('### Answer:')[1].split('\n\n### Feedback')[0]
                        else: 
                            response1 = response1.split('### Revision ')[-2].split('\n\n### Feedback')[0][1:]

                if response1.startswith(":"):
                    response1 = response1[1:]
                if response1.startswith("\n"):
                    response1 = response1[1:]
               
                revised = {
                    "question_id": query,
                    "text": response1,
                    "answer_id": data1["answer_id"],
                    "model_id": data1["model_id"],
                    "metadata": {}}
    
                outfile.write(revised)
                # print(num_alpaca_win, num_koala_win)
            
        # return num_alpaca_win / total, num_koala_win / total

def main(args):
    clean_prediction("table/answer/unicorn_106k_3epoch_sharegpt_alpaca_flan_merged_ver3_add_mathcode_2048_13b_force_revise3_2048_random2.jsonl")



if __name__ == "__main__":
    main(args)
