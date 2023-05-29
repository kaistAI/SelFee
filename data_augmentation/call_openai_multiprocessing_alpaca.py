from concurrent.futures import ProcessPoolExecutor

import argparse
import multiprocessing

import openai

from time import sleep
from random import random
import nltk
nltk.download('punkt')
from nltk import tokenize
import json

import fcntl

from typing import List
import os

from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    RetryError
)  # for exponential backoff

API_KEYS = os.environ["OPENAI_API_KEYS"].split(",")
MAX_WAIT_TIME=1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-path", type=str, required=True)
    parser.add_argument("--output-path", type=str, required=True)
    parser.add_argument("--fail-path", type=str, required=True)
    parser.add_argument("--requests-per-minute", type=int, default=60, help="Number of requests per minute per API key")
    parser.add_argument("--input-streaming", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    if not args.input_streaming:
        no_streaming(args.input_path, args.output_path, args.fail_path, args.requests_per_minute, args.limit)
    else:
        streaming(args.input_path, args.output_path, args.fail_path, args.requests_per_minute, args.limit)


def no_streaming(input_path, output_path, fail_path, requests_per_minute, limit):

    input_items = []
    input_format = input_path.split(".")[-1]
    with open(input_path, "r") as input_file:
        if input_format == "jsonl":
            for line in input_file:
                input_items.append(json.loads(line))
        elif input_format == "json":
            input_items = json.load(input_file)
        else:
            raise ValueError(f"Unknown input format: {input_format}")

    if limit is not None:
        input_items = input_items[:limit]
        
    process(input_items, output_path, fail_path, requests_per_minute)


def streaming(input_path, output_path, fail_path, requests_per_minute, limit):

    last_modified = None
    last_items = None
    
    while True:
        stats = os.stat(input_path)
        modified = stats.st_mtime
        if last_modified is not None and last_modified == modified:
            sleep(1)
            continue
        
        input_items = []
        input_format = input_path.split(".")[-1]
        with open(input_path, "r") as input_file:
            if input_format == "jsonl":
                for line in input_file:
                    input_items.append(json.loads(line))
            elif input_format == "json":
                input_items = json.load(input_file)
            else:
                raise ValueError(f"Unknown input format: {input_format}")

        if limit is not None:
            input_items = input_items[:limit]
            
        if last_items is not None:
            added_items = [item for item in input_items if item not in last_items]
        else:
            added_items = input_items

        process(added_items, output_path, fail_path, requests_per_minute)

        last_modified = modified


def process(input_items, output_path, fail_path, requests_per_minute):
    num_api_keys = len(API_KEYS)

    requests_per_minute_total = requests_per_minute * num_api_keys

    with ProcessPoolExecutor(max_workers=num_api_keys * requests_per_minute) as executor:
        for item_index, item in enumerate(input_items):
            api_key = API_KEYS[item_index % num_api_keys]    
            executor.submit(call_api_and_save, api_key=api_key, item=item, output_path=output_path, fail_path=fail_path)
            sleep(1 / requests_per_minute_total * 60)
    

def call_api_and_save(api_key: str, item: dict, output_path: str, fail_path: str):
    try:

        output_item = call_api(api_key, item)
        success = True
    except Exception as e:
        success = False

    if success:
        output_line = json.dumps(output_item)
        with open(output_path, "a") as output_file:
            fcntl.flock(output_file, fcntl.LOCK_EX)
            output_file.write(output_line + "\n")
            fcntl.flock(output_file, fcntl.LOCK_UN)
    else:
        fail_line = json.dumps(item)
        with open(fail_path, "a") as fail_file:
            fcntl.flock(fail_file, fcntl.LOCK_EX)
            fail_file.write(fail_line + "\n")
            fcntl.flock(fail_file, fcntl.LOCK_UN)


def call_api(api_key: str, task: str):
    openai.api_key = api_key

    last_flag = False
    item = {}
    item["iteration_truncated"]=False

    print('Testing %s ...' % task)
    # print('testing index %d-------------------------------------------------------------------------------------'%index)
    instruction = task["instruction"]
    input = task["input"]
    item['instruction']=instruction
    item['input']=input
    outputs=[]
    message=[]
    if input == "":
        context = f"{instruction}\n"
    else:
        context = f"{instruction}\n{input}\n"
    #0
    message.append({"role": "user", "content": f"{context}"})
    answer = completion_with_backoff(
        model="gpt-3.5-turbo",
        messages = message,#0,1,2  6,5,4
        temperature=1.0,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )['choices'][0]['message']['content']
    print("answer:", answer)
    #3 7
    # message.append({"role": "assistant", "content": answer})
    message=[{"role": "user", "content": f"{context}Here is a proposed answer:\n{answer}\n\nAre there any comments or critiques for the above answer? If so, write one under 100 words. You may score the quality of the answer on the scale of 1-10 (1: no code/no sense; 10: perfect) Also, classify if revision is needed by responding \"Revision is needed\" or \"Revision is not needed\" at the end. Normally, score of less than 9 should be revised.\n\nCritique:"}]
                    # Describe possible feedbacks that can improve the answer. The feedback should be under 100 words. If there is nothing to improve, just say \"No Feedback\".Feedback:"})
        # source ="Instruction: " + task["instruction"] + '\Answer: ' + output + "\n\nAre there any comments or feedbacks for the above answer? If so, write one within 100 words. Also, classify if revision is needed by responding \"Revision is needed\" or \"Revision is not needed\" at the end.\n\Feedback1:"
    # print(source)
    # message.append({"role": "user", "content": instruction+":\n"+input})
    # message.append({"role":"user","content":"Are there any comments or critiques for the above answer? If so, write one within 100 words. If not, just say \"Revision is not needed\"."})
    feedback = completion_with_backoff(
    model="gpt-3.5-turbo",
    messages = message,
    temperature=1.0,
    max_tokens=128,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    # stop=["\n\n"]
    )
    feedback = feedback['choices'][0]['message']['content']
    #1: 0
    message.append({"role": "assistant", "content": feedback})
    outputs.append({"output":answer, "feedback":feedback})
    print("feedback:", feedback)
    iteration=1
    while("no critique" not in message[-1]["content"].lower()) and ("no revision" not in message[-1]["content"].lower()) and ("no need" not in message[-1]["content"].lower()) and ("not needed" not in message[-1]["content"].lower()):
        if iteration>=5:
            item["iteration_truncated"]=True
            break
        #2 6
        if last_flag == False:
            message.append({"role":"user","content":"Revise the answer based on your own critique within 500 words. Your revision should be simple and clear, so do not add any rhetorics such as apology for the past mistake. Write as if the revised answer is the first try.\nRevision:"})
        else:
            message.append({"role":"user","content":"Revise the answer based on your own critique within 500 words. Your revision should be simple and clear, so do not add any rhetorics such as apology for the past mistake.\nRevision:"})
        answer = completion_with_backoff(
            model="gpt-3.5-turbo",
            messages = message,#0,1,2  6,5,4
            temperature=1.0,
            max_tokens=512,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )['choices'][0]['message']['content']
        if ("N/A" in answer):
            break
        iteration +=1
        while answer!=delete_revision_word_from_last(answer):
            answer = delete_revision_word_from_last(answer)
        answer_split = answer.split('.')
        if "i apologize" in answer_split[0].lower():
            answer_split=answer_split[1:]
            answer = ('.').join(answer_split)
        print("answer:", answer)
        #3 7
        message.append({"role": "assistant", "content": answer})
        #4 8
        if iteration>2:
            last_flag = True
        if last_flag ==False:
            message.append({"role": "user", "content": f"{context}Here is a proposed answer:\n{answer}\n\nAre there any comments or critiques for the above answer? If so, write one under 100 words. You may score the quality of the answer on the scale of 1-10 (1: no code/no sense; 10: perfect) Also, classify if revision is needed by responding \"Revision is needed\" or \"Revision is not needed\" at the end. Normally, score of less than 9 should be revised.\n\nCritique:"})
        else:
            message=[{"role": "user", "content": f"{context}Here is a proposed answer:\n{answer}\n\nAre there any comments or critiques for the above answer? If so, write one under 100 words. You may score the quality of the answer on the scale of 1-10 (1: no code/no sense; 10: perfect) Also, classify if revision is needed by responding \"Revision is needed\" or \"Revision is not needed\" at the end. Normally, score of less than 9 should be revised.\n\nCritique:"}]
        #message=[{"role":"user","content":f"{context}Here is a proposed answer:\n{answer}\nDescribe possible feedbacks that can improve the answer. The feedback should be under 100 words. If there is nothing to improve, just say \"No Feedback\".Feedback:"}]
        
        feedback = completion_with_backoff(
        model="gpt-3.5-turbo",
        messages = message,#4
        temperature=1.0,
        max_tokens=128,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        # stop=["\n\n"]
        )['choices'][0]['message']['content']
        feedback_sentence= feedback.split('.')
        if "but" in feedback_sentence[-1].lower() and("revision is needed" in feedback_sentence[-1].lower() or "revision is not needed"in feedback_sentence[-1].lower() ):
            if"revision is needed" in feedback_sentence[-1].lower() :
                last_sentence = "Revision is needed"
            else:
                last_sentence = "Revision is not needed"
            feedback_sentence[-1] = last_sentence
            feedback=('.').join(feedback_sentence)
        print("feedback:", feedback)
        #5
        message.append({"role": "assistant", "content": feedback})
        outputs.append({"output":answer, "feedback":feedback})
    item["iteration"]=iteration
    item['outputs']=outputs
    return item


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def completion_with_backoff(**kwargs):
    try:
        return openai.ChatCompletion.create(**kwargs)
    except Exception as e:
        print('-------------------------------------------------------------------------------------')
        print(e)
        print("kwargs", kwargs)
        print("API key", openai.api_key)
        print('-------------------------------------------------------------------------------------')
        raise e


def delete_revision_word_from_last(answer):
    line_split = answer.split('\n')
    if len(line_split)>0:
        original = ('\n').join(line_split[:-1])

        sentence_split = tokenize.sent_tokenize(line_split[-1])
        if len(sentence_split)>0:
            if "revision " in sentence_split[-1]:
                add_sentence = ('').join(sentence_split[:-1])
                answer=original+'\n'+add_sentence    
        else:
            answer= ('\n').join(line_split[:-1])
    return answer

                    
if __name__ == "__main__":
    main()
