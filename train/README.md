We provide training code for our model.
If you want to replicate the training step of SelFee 7B, you can utilize the following code:
'''
torchrun --nproc_per_node=4 fastchat/train/train_mem.py \
    --model_name_or_path llama_7B/llama-7b \
    --data_path ../outputs/feedback_gpt_3.5_turbo_merged_whole.json \
    --bf16 True \
    --output_dir ../ckpt/selfee_7b_epoch3_len2048 \
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
'''
