"""
Qwen3-4B-Thinking Fine-tuning Script using Unsloth
"""

from unsloth import FastLanguageModel
from unsloth.chat_templates import get_chat_template, train_on_responses_only
from datasets import load_dataset
from trl import SFTTrainer, SFTConfig
import torch

# -------- 1. Load Model --------
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/Qwen3-4B-Thinking-2507",
    max_seq_length = 2048,
    load_in_4bit = True,
    load_in_8bit = False,
    full_finetuning = False,
)

# -------- 2. LoRA Configuration --------
model = FastLanguageModel.get_peft_model(
    model,
    r = 32,
    target_modules = [
        "q_proj","k_proj","v_proj","o_proj",
        "gate_proj","up_proj","down_proj",
    ],
    lora_alpha = 32,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth",
    random_state = 3407,
    use_rslora = False,
    loftq_config = None,
)

# -------- 3. Dataset Preparation --------
tokenizer = get_chat_template(
    tokenizer,
    chat_template = "qwen3-thinking",
)

dataset = load_dataset("unsloth/OpenMathReasoning-mini", split="cot")

def generate_conversation(examples):
    problems  = examples["problem"]
    solutions = examples["generated_solution"]
    conversations = []
    for problem, solution in zip(problems, solutions):
        conversations.append([
            {"role" : "user", "content" : problem},
            {"role" : "assistant", "content" : solution},
        ])
    return {"conversations": conversations}

dataset = dataset.map(generate_conversation, batched=True)

def formatting_prompts_func(examples):
    convos = examples["conversations"]
    texts = [
        tokenizer.apply_chat_template(convo, tokenize=False, add_generation_prompt=False)
        for convo in convos
    ]
    return {"text": texts}

dataset = dataset.map(formatting_prompts_func, batched=True)

# -------- 4. Training Configuration --------
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    eval_dataset = None,
    args = SFTConfig(
        dataset_text_field = "text",
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        max_steps = 60,
        learning_rate = 2e-4,
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        report_to = "none",
    ),
)

# Only train on assistant responses
trainer = train_on_responses_only(
    trainer,
    instruction_part = "<|im_start|>user\n",
    response_part = "<|im_start|>assistant\n",
)

# -------- 5. Train --------
trainer_stats = trainer.train()

# -------- 6. Save LoRA Adapters --------
model.save_pretrained("lora_model")
tokenizer.save_pretrained("lora_model")

# -------- 7. Inference Example --------
messages = [{"role": "user", "content": "Solve (x + 2)^2 = 0."}]
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
    enable_thinking=False,
)

from transformers import TextStreamer
_ = model.generate(
    **tokenizer(text, return_tensors="pt").to("cuda"),
    max_new_tokens=450,
    temperature=0.7,
    top_p=0.8,
    top_k=20,
    streamer=TextStreamer(tokenizer, skip_prompt=False),
)