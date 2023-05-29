# Adopted from tatsu-lab@stanford_alpaca. Below is the original copyright:
#    Copyright 2023 Rohan Taori, Ishaan Gulrajani, Tianyi Zhang, Yann Dubois, Xuechen Li
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import copy
from dataclasses import dataclass, field
import json
import logging
import pathlib
from typing import Dict, Optional, Sequence

import torch

import transformers
from torch.utils.data import Dataset
from transformers import Trainer

# TODO: import and use code from ../data/dataset.py

import feedback_utils

IGNORE_INDEX = -100
DEFAULT_PAD_TOKEN = "[PAD]"
DEFAULT_EOS_TOKEN = "</s>"
DEFAULT_BOS_TOKEN = "</s>"
DEFAULT_UNK_TOKEN = "</s>"


@dataclass
class ModelArguments:
    model_name_or_path: Optional[str] = field(default="facebook/opt-125m")


@dataclass
class DataArguments:
    data_path: str = field(default=None,
                           metadata={"help": "Path to the training data."})
    lazy_preprocess: bool = False
    training_objective: str = field(default="full", metadata={"help": "Training objective. Options: full, faf, split, full-after-answer"})


@dataclass
class TrainingArguments(transformers.TrainingArguments):
    cache_dir: Optional[str] = field(default=None)
    optim: str = field(default="adamw_torch")
    model_max_length: int = field(
        default=512,
        metadata={
            "help":
            "Maximum sequence length. Sequences will be right padded (and possibly truncated)."
        },
    )


def safe_save_model_for_hf_trainer(trainer: transformers.Trainer,
                                   output_dir: str):
    """Collects the state dict and dump to disk."""
    state_dict = trainer.model.state_dict()
    if trainer.args.should_save:
        cpu_state_dict = {
            key: value.cpu()
            for key, value in state_dict.items()
        }
        del state_dict
        trainer._save(output_dir, state_dict=cpu_state_dict)  # noqa



def smart_tokenizer_and_embedding_resize(
    special_tokens_dict: Dict,
    tokenizer: transformers.PreTrainedTokenizer,
    model: transformers.PreTrainedModel,
):
    """Resize tokenizer and embedding.

    Note: This is the unoptimized version that may make your embedding size not be divisible by 64.
    """
    num_new_tokens = tokenizer.add_special_tokens(special_tokens_dict)
    model.resize_token_embeddings(len(tokenizer))

    if num_new_tokens > 0:
        input_embeddings = model.get_input_embeddings().weight.data
        output_embeddings = model.get_output_embeddings().weight.data

        input_embeddings_avg = input_embeddings[:-num_new_tokens].mean(
            dim=0, keepdim=True)
        output_embeddings_avg = output_embeddings[:-num_new_tokens].mean(
            dim=0, keepdim=True)

        input_embeddings[-num_new_tokens:] = input_embeddings_avg
        output_embeddings[-num_new_tokens:] = output_embeddings_avg


def _tokenize_fn(strings: Sequence[str],
                 tokenizer: transformers.PreTrainedTokenizer) -> Dict:
    """Tokenize a list of strings."""
    tokenized_list = [
        tokenizer(
            text,
            return_tensors="pt",
            padding="longest",
            max_length=tokenizer.model_max_length,
            truncation=True,
        ) for text in strings
    ]
    input_ids = labels = [
        tokenized.input_ids[0] for tokenized in tokenized_list
    ]
    input_ids_lens = labels_lens = [
        tokenized.input_ids.ne(tokenizer.pad_token_id).sum().item()
        for tokenized in tokenized_list
    ]
    return dict(
        input_ids=input_ids,
        labels=labels,
        input_ids_lens=input_ids_lens,
        labels_lens=labels_lens,
    )


def preprocess(
    sources: Sequence[str],
    targets: Sequence[str],
    tokenizer: transformers.PreTrainedTokenizer,
) -> Dict:
    """Preprocess the data by tokenizing."""
    examples = [s + t for s, t in zip(sources, targets)]
    examples_tokenized, sources_tokenized = [_tokenize_fn(strings, tokenizer) for strings in (examples, sources)]
    input_ids = examples_tokenized["input_ids"]
    labels = copy.deepcopy(input_ids)
    for label, source_len in zip(labels, sources_tokenized["input_ids_lens"]):
        label[:source_len] = IGNORE_INDEX
    return dict(input_ids=input_ids, labels=labels)


class SupervisedDataset(Dataset):
    """Dataset for supervised fine-tuning."""

    def __init__(self, data_path: str, tokenizer: transformers.PreTrainedTokenizer, training_objective: str):
        super(SupervisedDataset, self).__init__()
        logging.warning("Loading data...")
        list_data_dict = json.load(open(data_path, "r"))

        sources = []
        targets = []    
        logging.warning("Formatting inputs...")
        if training_objective == "full":
            for example in list_data_dict:
                source = feedback_utils.make_full_source(example)
                target = feedback_utils.make_full_target(example)
                target += f"{tokenizer.eos_token}"
                sources.append(source)
                targets.append(target)
        elif training_objective == "faf":
            for example in list_data_dict:
                source = feedback_utils.make_FAF_source(example)
                target = feedback_utils.make_FAF_target(example)
                target += f"{tokenizer.eos_token}"
                sources.append(source)
                targets.append(target)
        elif training_objective == "split":
            for example in list_data_dict:
                example_sources, example_targets = feedback_utils.make_split_example(example, eos_token=tokenizer.eos_token)
                
                sources.extend(example_sources)
                targets.extend(example_targets)
        elif training_objective == "full-after-answer":
            for example in list_data_dict:
                source = feedback_utils.make_full_after_answer_source(example)
                target = feedback_utils.make_full_after_answer_target(example)
                target += f"{tokenizer.eos_token}"
                sources.append(source)
                targets.append(target)
        elif training_objective == "continual-active":
            for example in list_data_dict:
                source = feedback_utils.make_continual_active_source(example)
                target = feedback_utils.make_continual_active_target(example, eos_token=tokenizer.eos_token)
                sources.append(source)
                targets.append(target)
        elif training_objective == "answer-only":
            for example in list_data_dict:
                source = feedback_utils.make_answer_only_source(example)
                target = feedback_utils.make_answer_only_target(example, eos_token=tokenizer.eos_token)
                sources.append(source)
                targets.append(target)
        else:
            raise NotImplementedError

        logging.warning(f"Number of source examples: {len(sources)}")
        logging.warning(f"Number of target examples: {len(targets)}")

        logging.warning("Tokenizing inputs... This may take some time...")
        data_dict = preprocess(sources, targets, tokenizer)
        
        self.input_ids = data_dict["input_ids"]
        self.labels = data_dict["labels"]

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, i) -> Dict[str, torch.Tensor]:
        return dict(input_ids=self.input_ids[i], labels=self.labels[i])


class LazySupervisedDataset(Dataset):
    """Dataset for supervised fine-tuning."""

    def __init__(self, data_path: str,
                 tokenizer: transformers.PreTrainedTokenizer, 
                 training_objective: str):
        super(LazySupervisedDataset, self).__init__()
        logging.warning("Loading data...")
        list_data_dict = json.load(open(data_path, "r"))

        logging.warning("Formatting inputs...Skip in lazy mode")
        self.tokenizer = tokenizer
        self.list_data_dict = list_data_dict
        self.training_objective = training_objective

    def __len__(self):
        return len(self.list_data_dict)

    def __getitem__(self, i) -> Dict[str, torch.Tensor]:
        examples = self.list_data_dict[i]
        if isinstance(i, int):
            examples = [examples]
        sources = []
        targets = []    
        if self.training_objective == "full":
            for example in examples:
                source = feedback_utils.make_full_source(example)
                target = feedback_utils.make_full_target(example)
                target += f"{self.tokenizer.eos_token}"
                sources.append(source)
                targets.append(target)
        elif self.training_objective == "faf":
            for example in examples:
                source = feedback_utils.make_FAF_source(example)
                target = feedback_utils.make_FAF_target(example)
                target += f"{self.tokenizer.eos_token}"
                sources.append(source)
                targets.append(target)
        elif self.training_objective == "split":
            for example in examples:
                example_sources, example_targets = feedback_utils.make_split_example(example, eos_token=self.tokenizer.eos_token)
                
                sources.extend(example_sources)
                targets.extend(example_targets)
        elif self.training_objective == "full-after-answer":
            for example in examples:
                source = feedback_utils.make_full_after_answer_source(example)
                target = feedback_utils.make_full_after_answer_target(example)
                target += f"{self.tokenizer.eos_token}"
                sources.append(source)
                targets.append(target)
        elif self.training_objective == "continual-active":
            for example in examples:
                source = feedback_utils.make_continual_active_source(example)
                target = feedback_utils.make_continual_active_target(example, eos_token=self.tokenizer.eos_token)
                sources.append(source)
                targets.append(target)
        elif self.training_objective == "answer-only":
            for example in examples:
                source = feedback_utils.make_answer_only_source(example)
                target = feedback_utils.make_answer_only_target(example, eos_token=self.tokenizer.eos_token)
                sources.append(source)
                targets.append(target)
        else:
            raise NotImplementedError

        data_dict = preprocess(sources, targets, self.tokenizer)
        if isinstance(i, int):
            data_dict = dict(input_ids=data_dict["input_ids"][0],
                             labels=data_dict["labels"][0])
        return data_dict


@dataclass
class DataCollatorForSupervisedDataset(object):
    """Collate examples for supervised fine-tuning."""

    tokenizer: transformers.PreTrainedTokenizer

    def __call__(self, instances: Sequence[Dict]) -> Dict[str, torch.Tensor]:
        input_ids, labels = tuple([instance[key] for instance in instances]
                                  for key in ("input_ids", "labels"))
        input_ids = torch.nn.utils.rnn.pad_sequence(
            input_ids,
            batch_first=True,
            padding_value=self.tokenizer.pad_token_id)
        labels = torch.nn.utils.rnn.pad_sequence(labels,
                                                 batch_first=True,
                                                 padding_value=IGNORE_INDEX)
        return dict(
            input_ids=input_ids,
            labels=labels,
            attention_mask=input_ids.ne(self.tokenizer.pad_token_id),
        )


def make_supervised_data_module(tokenizer: transformers.PreTrainedTokenizer,
                                data_args) -> Dict:
    """Make dataset and collator for supervised fine-tuning."""
    dataset_cls = (LazySupervisedDataset
                   if data_args.lazy_preprocess else SupervisedDataset)
    train_dataset = dataset_cls(tokenizer=tokenizer,
                                data_path=data_args.data_path, 
                                training_objective=data_args.training_objective)
    data_collator = DataCollatorForSupervisedDataset(tokenizer=tokenizer)
    return dict(train_dataset=train_dataset,
                eval_dataset=None,
                data_collator=data_collator)


def train():
    parser = transformers.HfArgumentParser(
        (ModelArguments, DataArguments, TrainingArguments))
    model_args, data_args, training_args = parser.parse_args_into_dataclasses()

    assert data_args.training_objective in ["full", "faf", "split", "full-after-answer", "continual-active", "answer-only"]
    
    model = transformers.LlamaForCausalLM.from_pretrained(
        model_args.model_name_or_path,
        cache_dir=training_args.cache_dir,
    )

    tokenizer = transformers.AutoTokenizer.from_pretrained(
        model_args.model_name_or_path,
        cache_dir=training_args.cache_dir,
        model_max_length=training_args.model_max_length,
        padding_side="right",
        use_fast=False,
    )
    if tokenizer.pad_token is None:
        smart_tokenizer_and_embedding_resize(
            special_tokens_dict=dict(pad_token=DEFAULT_PAD_TOKEN),
            tokenizer=tokenizer,
            model=model,
        )
    if "llama" in model_args.model_name_or_path:
        tokenizer.add_special_tokens({
            "eos_token": DEFAULT_EOS_TOKEN,
            "bos_token": DEFAULT_BOS_TOKEN,
            "unk_token": DEFAULT_UNK_TOKEN,
        })

    data_module = make_supervised_data_module(tokenizer=tokenizer,
                                              data_args=data_args)
    trainer = Trainer(model=model,
                    tokenizer=tokenizer,
                    args=training_args,
                    **data_module)

    if list(pathlib.Path(training_args.output_dir).glob("checkpoint-*")):
        trainer.train(resume_from_checkpoint=True)
    else:
        trainer.train()
    trainer.save_state()
    safe_save_model_for_hf_trainer(trainer=trainer,
                                   output_dir=training_args.output_dir)


if __name__ == "__main__":
    train()
