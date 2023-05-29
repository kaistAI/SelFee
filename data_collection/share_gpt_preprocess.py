

import json
from langdetect import detect
from bs4 import BeautifulSoup
def extract(html_string):
# Set the HTML code style string

    # Create a BeautifulSoup object from the HTML string
    soup = BeautifulSoup(html_string, 'lxml')

    # Get the text from the HTML
    text = soup.get_text()
    return text
revised_list=[]
check=[]
for llama_json in [json.load(open("outputs/sg_90k_part1.json")), json.load(open("outputs/sg_90k_part2.json"))]:
    for index in range(len(llama_json)):
        try:
            task ={}
            task["instruction"] = extract(llama_json[index]["conversations"][0]["value"])
            task["input"]=""
            task["output"]=extract(llama_json[index]["conversations"][1]["value"])
            if detect(task["instruction"])=='en' and detect(task["output"])=='en':
                if task["output"][-1]=='?':
                    check.append(llama_json[index]["conversations"])
                else:
                    revised_list.append(task)

        except:
            print( llama_json[index]["conversations"])

# with open("outputs/sharegpt_90k_processed.json", 'w+') as fd:
#     json.dump(revised_list, fd, indent=4)
with open("../outputs/sharegpt/sharegpt_90k_processed.json", 'w+') as fd:
    json.dump(check, fd, indent=4)
# print(len(json.load(open("outputs/sharegpt_90k_processed.json"))))
