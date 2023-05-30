
<p align="center" width="100%">
<a href="https://self-feedback-beta.dreamgonf.ly/" target="_blank"><img src="assets/llama_selfie.png" alt="KAIST-Selfee" style="width: 50%; min-width: 300px; display: block; margin: auto;"></a>
</p>

# SelFee: Iterative Self-Revising LLM Empowered by <br/> Self-Feedback Generation

[![Code License](https://img.shields.io/badge/Code%20License-Apache_2.0-green.svg)](https://github.com/tatsu-lab/stanford_alpaca/blob/main/LICENSE)
[![Data License](https://img.shields.io/badge/Data%20License-CC%20By%20NC%204.0-red.svg)](https://github.com/tatsu-lab/stanford_alpaca/blob/main/DATA_LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


## News
[May 31, 2023] Initial release: We released the first version of Selfee! Check out the <a href="https://lklab.kaist.ac.kr/">blog post</a> for more details.


## Overview
This is the repository for the KAIST Selfee project, which aims to build and share an instruction-following LLaMA model. This repo mainly has five contents:
- The selection process of the 178K training data for Selfee ([detail](#data-release), [code](data_collection)).
- The generation process for the training data and its result. ([detail](#data-generation-process), [code](data_augmentation)).
- The training process for the model  ([detail](#training), [code](train)).
- The inference process for the model ([detail](#inferencing), [code](inference)).
- The evaluation method and dataset ([detail](#evaluating), [code](evaluation)).


This repository is based on the [Stanford-Alpaca](https://github.com/tatsu-lab/stanford_alpaca/) and [Vicuna](https://github.com/lm-sys/FastChat/) repository. Thanks to all the contributors for these awesome repositories!! 🙌



**We highly recommend you read our [blog post](https://lklab.kaist.ac.kr/) for more details about the model.**


## Data Release
For data collection, we collected datasets from five different fields. These are the Stanford Alpaca dataset, math collection, code collection, Flan collection, and ShareGPT.
<b>Stanford Alpaca dataset</b>
<p>
	We include the dataset used to train the Stanford Alpaca model. The dataset contains around 52k examples, which is generated by OpenAI’s text-davinci-003 following the self-instruct process.<br>
</p>
<b>Math collection</b>
<p>
	The math collection included three kinds of datasets: Aqua (10k), GSM8K (8.79k), and Math (7.47k). Since we knew the answers to these questions, we asked ChatGPT for feedback after providing the correct answer.<br>
</p>	
<div class="entry-title title-sm">
	<b>Code collection</b>
</div>
<p>
	The code collection had three types of datasets, namely Conala (2.78k), Deepmind Code Contest (8.16k), Dr Repair (18k), and Mbpp (969). As with the math collection, we asked ChatGPT for feedback after providing the correct answer.<br>
</p>	
<div class="entry-title title-sm">
	<b>Flan collection</b>
</div>
<p>
	The Flan collection included subsets of Flan collection datasets such as Flan (Flan 2021), T0 (P3 excluding Flan 2021), and Niv2 (Super-Natural Instructions). We only used ten instances per task and excluded the subsets from Dr Repair and Deepmind Code Contest because they were included in the code collection. As with the math and code collections, we asked ChatGPT for feedback after providing the correct answer. Our collection had 15.6k instances.<br>
</p>	

<div class="entry-title title-sm">
	<b>ShareGPT</b>
</div>
<p>
	We initially collected 90k dialogues shared by users on ShareGPT were collected using public APIs.To maintain data quality, we removed any non-English conversations and deduplicated at the user-query level. We utilized only the first instruction-answer pair from human and machine and removed any machine answer ending with a question mark, as we only required descriptive instructions. This resulted in 54.6k examples for training.<br>
</p>		

## Data Generation Process

<source media="(min-width: 1200px)" src="videos/Selfee_Data_Augmentation_Scheme.mp4" type="video/mp4">
To train our model with high-quality instructions and answer pairs, we utilized data augmentation using OpenAI API calls. The process involved three steps. <br>
Firstly, we collected various instructions from multiple fields and fed them to ChatGPT to generate answers. <br>
Secondly, we gathered feedback on the generated answer by querying ChatGPT again and asked it to determine if the initial answer required any revision. <br>
Thirdly, if a revision was necessary, we passed the instruction, initial answer, and feedback pair to ChatGPT to generate a revised answer and its feedback pair. 
We repeated the process until we received feedback that required no further revision or hit the maximum iteration. However, due to the token limitation of the ChatGPT API, we had to truncate some instances that needed more than 4096 tokens while augmenting.<br>

## Training

We utilize <a href="https://github.com/lm-sys/FastChat">FastChat</a> to train the model. Given the instruction, we fine-tune the model to generate the answer and feedback chain (including the revisions).<br>

To reproduce the training procedure, here are the steps. <br>

```
pip install -r requirements.txt
```

```
torchrun --nproc_per_node=4 train/train_mem.py \
    --model_name_or_path llama-7b \
    --data_path outputs/feedback_gpt_3.5_turbo_merged_whole.json \
    --bf16 True \
    --output_dir ckpt/selfee-7b \
    --num_train_epochs 3 \
    --per_device_train_batch_size 16 \
    --per_device_eval_batch_size 16 \
    --gradient_accumulation_steps 2 \
    --evaluation_strategy "no" \
    --save_strategy "steps" \
    --save_steps 5000 \
    --save_total_limit 1 \
    --learning_rate 2e-5 \
    --weight_decay 0. \
    --warmup_ratio 0.03 \
    --lr_scheduler_type "cosine" \
    --logging_steps 1 \
    --fsdp "shard_grad_op auto_wrap" \
    --fsdp_transformer_layer_cls_to_wrap 'LlamaDecoderLayer' \
    --tf32 True \
    --model_max_length 2048 \
    --gradient_checkpointing True \
    --lazy_preprocess True \
    --training_objective full \
```

The hyperparameters are as follows, following Vicuna and Alpaca.

| Hyperparameter | Global Batch Size | Learning rate | Epochs | Max length | Weight decay |
| --- | ---: | ---: | ---: | ---: | ---: |
| SelFee (7B, 13B) | 128 | 2e-5 | 3 | 2048 | 0 |


## Inference
<b>Autonomous Inference Mode</b><br>

Because SelFee is trained to generate iterative feedback and revisions until the response is satisfying, it automatically generates iterative feedback and revisions on a single forward pass. The model autonomously decides when to stop generating revisions based on the feedback. If the feedback chain ends with sequences like `Revision is not needed.`, the model autonomously terminates generation. <br>

For autonomous inference mode, 

```
python inference/inference.py --model-path "ckpt/selfee-7b" --model-id "selfee" --question-file "evaluation/template/question.jsonl" --answer-file "evaluation/answer/selfee_7b_autonomous.jsonl" 
```


<b>Revision Enforce Inference Mode</b><br>
We observed that increasing the minimum number of required revisions corresponds to a corresponding increase in performance. To enforce revisions, we automatically replace sequences such as `Revision is not needed.` into `Revision is needed.` during self-feedback generation. Because SelFee is trained to generate `Revision {index}:` after the sequence of `Revision is needed.`, the model would continually revise the answer.   

For revision enforce inference mode, use the `max-num-revision` argument. 

```
python inference/inference.py --model-path "ckpt/selfee-7b" --model-id "selfee" --question-file "evaluation/template/question.jsonl" --answer-file "evaluation/answer/selfee_7b_enforce_3_revision.jsonl" --max-num-revision 3
```



## Evaluation
Following evaluation setting of Vicuna, we evaluate on 80 diverse queries and utilize GPT-4 language model as the evaluator, scoring a model's response relative to ChatGPT's response. One of the difference with Vicuna evaluation is that due to positional bias of GPT-4, we employ a bidirectional evaluation setting. This means that each evaluation instance is inferred twice, depending on its position.<br>

We release the inference result of SelFee in the folder of `evaluation/answer` and also the scores generated by GPT-4 in the folder of `evaluation/review`. <br>

### GPT-4 Automatic Evaluation
First, you need to get your API key to get access to the GPT-4 API.
```
export OPENAI_API_KEYS={personal_key}
```

To compare the performance of a generation result (for example, located on `evaluation/answer/file_A.jsonl`) with another generation result (located on `evaluation/anwer/file_B.jsonl`), 


```
python evaluation/gpt4_automatic_evaluation.py -q evaluation/template/question.jsonl -a evaluation/answer/file_A.jsonl evaluation/answer/file_B.jsonl -p evaluation/template/prompt.jsonl -r evaluation/template/reviewer.jsonl -o evaluation/review/A_vs_B.jsonl
```

To mitigate the positional bias of GPT-4 model, we apply a bidirectional evaluation setting. Therefore, automatic evaluation with opposite position is also needed.

```
python evaluation/gpt4_automatic_evaluation.py -q evaluation/template/question.jsonl -a evaluation/answer/file_B.jsonl evaluation/answer/file_A.jsonl -p evaluation/template/prompt.jsonl -r evaluation/template/reviewer.jsonl -o evaluation/review/B_vs_A.jsonl
```

## Limitations 
Similar to other LLaMA-finetuned models, SelFee also make some mistakes especially for math, reasoning, factuality, and coding tasks. Although our performance outperforms ChatGPT on Vicuna setting, the evaluation setting contains some limitations in terms of comprehension (limited to 80 queries), inconsistency, and unreliability. Therefore, further research for a better evaluation setting is needed. Please take these claims with a grain of salt.

### Online demo
Check out the <a href="https://self-feedback-beta.dreamgonf.ly/">demo</a>!


### Team members
<a href="https://seonghyeonye.github.io/)">Seonghyeon Ye*</a>,  <a href="https://github.com/dreamgonfly">Yongrae Jo*</a>, <a href="https://github.com/doeyoungkim">Doyoung Kim*</a>, <a href="https://scholar.google.com/citations?user=xKrSnDoAAAAJ&hl">Sungdong Kim</a>, <a href="https://github.com/hbin0701">Hyeonbin Hwang</a>, and <a href="https://seominjoon.github.io/">Minjoon Seo</a>. <br/>
(* denotes equal contribution)

### Release
We will make available the training, serving, and evaluation code for our first release on a GitHub repository: <a href="https://github.com/seonghyeonye/Self-Feedback">https://github.com/seonghyeonye/Self-Feedback</a>. Additionally, we have released the Selfee-7B and Selfee-13B model weights, which can be found with instructions <a href="https://github.com/seonghyeonye/Self-Feedback#selfee-weights">here</a>. Keep up-to-date with the latest developments by following us on <a href="https://twitter.com/">Twitter</a>!

### License

The research preview online demo is only for non-commercial use and is subject to various licenses and terms of use, including the LLaMA model <a href="https://github.com/facebookresearch/llama/blob/main/MODEL_CARD.md">License</a>, OpenAI's <a href="https://openai.com/policies/terms-of-use">Terms of Use</a> for the generated data, and ShareGPT's <a href="https://chrome.google.com/webstore/detail/sharegpt-share-your-chatg/daiacboceoaocpibfodeljbdfacokfjb">Privacy Practices</a>. If you suspect any violations, please reach out to us.





### Citation

Please cite if you use the data or code in this repo.

```
@misc{selfee2023,
	author = {Ye, Seonghyeon and Jo, Yongrae and Kim, Doyoung and Kim, Sungdong and Hwang, Hyeonbin and Seo, Minjoon},
	title = {SelFee: Iterative Self-Revising LLM Empowered by Self-Feedback Generation},
	url = {https://kaist-lklab.github.io/selfee},
	month = {May},
	year = {2023},
	howpublished = {Blog post}
}
```
