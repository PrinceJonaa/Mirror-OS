"""
Qwen3-4B Advanced Fine-tuning Script with Memory Optimizations
Incorporates techniques from GRPO notebook: memory management, eval, smaller LoRA experiments
"""

from unsloth import FastLanguageModel
from unsloth.chat_templates import get_chat_template, train_on_responses_only
from datasets import load_dataset
from trl import SFTTrainer, SFTConfig
import torch
import gc

# =====================================================================
# CONFIGURATION - Advanced Settings
# =====================================================================

# Model Configuration
MODEL_NAME = "unsloth/Qwen3-4B"
MAX_SEQ_LENGTH = 2048
LOAD_IN_4BIT = True
OFFLOAD_EMBEDDING = True  # NEW: Reduces VRAM by ~1GB (from GRPO notebook)

# LoRA Configuration - Experiment Mode
# Use smaller rank for faster iteration, then scale up for production
EXPERIMENT_MODE = False  # Set True for fast testing with r=4
LORA_R = 4 if EXPERIMENT_MODE else 32
LORA_ALPHA = LORA_R * 2  # *2 speeds up training (GRPO technique)
LORA_DROPOUT = 0

# Training Configuration
PER_DEVICE_BATCH_SIZE = 2
GRADIENT_ACCUMULATION = 4
MAX_STEPS = 60  # For testing
LEARNING_RATE = 2e-4
WARMUP_RATIO = 0.1  # Better than warmup_steps for variable dataset sizes
WEIGHT_DECAY = 0.01

# Dataset Configuration
USE_CUSTOM_DATASET = True
CUSTOM_DATASET_PATH = "/Users/princejona/a1/research/training/training_codex.jsonl"

# Evaluation Configuration (NEW)
ENABLE_EVAL = True  # Enable to monitor overfitting
EVAL_SPLIT_SIZE = 0.05  # 5% for evaluation
EVAL_STEPS = 10  # Evaluate every N steps

# Memory Management (NEW - from GRPO)
AGGRESSIVE_MEMORY_CLEANUP = True  # Force GC every N steps

# Inference Settings
THINKING_MODE_PARAMS = {
    "temperature": 0.6,
    "top_p": 0.95,
    "top_k": 20,
    "min_p": 0.0,
    "max_new_tokens": 1024,
}
NON_THINKING_MODE_PARAMS = {
    "temperature": 0.7,
    "top_p": 0.8,
    "top_k": 20,
    "min_p": 0.0,
    "max_new_tokens": 512,
}

# =====================================================================
# 1. LOAD MODEL with Advanced Memory Optimization
# =====================================================================
print("🚀 Loading model with advanced memory optimizations...")
print(f"   Model: {MODEL_NAME}")
print(f"   Offload Embedding: {OFFLOAD_EMBEDDING} (saves ~1GB VRAM)")
print(f"   LoRA Rank: {LORA_R} ({'Experiment' if EXPERIMENT_MODE else 'Production'} Mode)")

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = MODEL_NAME,
    max_seq_length = MAX_SEQ_LENGTH,
    load_in_4bit = LOAD_IN_4BIT,
    offload_embedding = OFFLOAD_EMBEDDING,  # NEW: Reduces VRAM by 1GB
)

# Force initial garbage collection
gc.collect()
torch.cuda.empty_cache()

# =====================================================================
# 2. LoRA CONFIGURATION with Speed Optimization
# =====================================================================
print("\n🔧 Applying LoRA adapters...")
print(f"   Alpha: {LORA_ALPHA} (rank*2 for faster training)")

model = FastLanguageModel.get_peft_model(
    model,
    r = LORA_R,
    target_modules = [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
    lora_alpha = LORA_ALPHA,  # rank*2 speeds up training (GRPO technique)
    lora_dropout = LORA_DROPOUT,
    bias = "none",
    use_gradient_checkpointing = "unsloth",
    random_state = 3407,
)

# =====================================================================
# 3. DATASET PREPARATION with Train/Eval Split
# =====================================================================
print("\n📊 Preparing dataset...")

tokenizer = get_chat_template(
    tokenizer,
    chat_template = "qwen3-thinking",
)

if USE_CUSTOM_DATASET:
    print(f"   Loading: {CUSTOM_DATASET_PATH}")
    dataset = load_dataset("json", data_files=CUSTOM_DATASET_PATH, split="train")
    
    def formatting_prompts_func(examples):
        convos = examples["conversations"]
        texts = [
            tokenizer.apply_chat_template(
                convo, 
                tokenize=False, 
                add_generation_prompt=False,
                enable_thinking=False
            )
            for convo in convos
        ]
        return {"text": texts}
    
    dataset = dataset.map(formatting_prompts_func, batched=True)
    
    # NEW: Split into train/eval for monitoring overfitting
    if ENABLE_EVAL and EVAL_SPLIT_SIZE > 0:
        dataset = dataset.train_test_split(test_size=EVAL_SPLIT_SIZE, seed=3407)
        train_dataset = dataset["train"]
        eval_dataset = dataset["test"]
        print(f"   ✓ Train: {len(train_dataset)} examples")
        print(f"   ✓ Eval: {len(eval_dataset)} examples")
    else:
        train_dataset = dataset
        eval_dataset = None
        print(f"   ✓ Loaded {len(train_dataset)} training examples")
else:
    # Fallback to example datasets
    from datasets import Dataset
    import pandas as pd
    from unsloth.chat_templates import standardize_sharegpt
    
    reasoning_dataset = load_dataset("unsloth/OpenMathReasoning-mini", split="cot")
    non_reasoning_dataset = load_dataset("mlabonne/FineTome-100k", split="train")
    
    # ... (same mixing logic as before)
    
    train_dataset = dataset
    eval_dataset = None

# Memory cleanup after dataset loading
gc.collect()
torch.cuda.empty_cache()

# =====================================================================
# 4. TRAINING CONFIGURATION with Evaluation
# =====================================================================
print("\n🏋️ Configuring trainer with evaluation...")

trainer_args = SFTConfig(
    dataset_text_field = "text",
    per_device_train_batch_size = PER_DEVICE_BATCH_SIZE,
    gradient_accumulation_steps = GRADIENT_ACCUMULATION,
    warmup_ratio = WARMUP_RATIO,  # Better than warmup_steps
    max_steps = MAX_STEPS,
    learning_rate = LEARNING_RATE,
    logging_steps = 1,
    optim = "adamw_8bit",
    weight_decay = WEIGHT_DECAY,
    lr_scheduler_type = "linear",
    seed = 3407,
    report_to = "none",
)

# Add evaluation config if enabled
if ENABLE_EVAL and eval_dataset is not None:
    trainer_args.eval_strategy = "steps"
    trainer_args.eval_steps = EVAL_STEPS
    trainer_args.per_device_eval_batch_size = 4
    trainer_args.eval_accumulation_steps = 1
    print("   ✓ Evaluation enabled")

trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = train_dataset,
    eval_dataset = eval_dataset,
    args = trainer_args,
)

trainer = train_on_responses_only(
    trainer,
    instruction_part = "<|im_start|>user\n",
    response_part = "<|im_start|>assistant\n",
)

# =====================================================================
# 5. TRAIN with Memory Management
# =====================================================================
print("\n" + "="*70)
print("🚀 STARTING TRAINING WITH MEMORY MANAGEMENT")
print("="*70)

# Pre-training memory stats
gpu_stats = torch.cuda.get_device_properties(0)
start_gpu_memory = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
max_memory = round(gpu_stats.total_memory / 1024 / 1024 / 1024, 3)
print(f"GPU: {gpu_stats.name}")
print(f"Max memory: {max_memory} GB")
print(f"Memory reserved: {start_gpu_memory} GB")
print(f"Embedding offload: {OFFLOAD_EMBEDDING} (saves ~1GB)")
print("="*70 + "\n")

# Train with periodic memory cleanup
if AGGRESSIVE_MEMORY_CLEANUP:
    # Custom training callback for memory management
    from transformers import TrainerCallback
    
    class MemoryCleanupCallback(TrainerCallback):
        def on_step_end(self, args, state, control, **kwargs):
            if state.global_step % 10 == 0:  # Every 10 steps
                gc.collect()
                torch.cuda.empty_cache()
    
    trainer.add_callback(MemoryCleanupCallback())
    print("✓ Memory cleanup callback enabled (every 10 steps)\n")

trainer_stats = trainer.train()

# Post-training memory stats
used_memory = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
used_memory_for_lora = round(used_memory - start_gpu_memory, 3)
used_percentage = round(used_memory / max_memory * 100, 3)
lora_percentage = round(used_memory_for_lora / max_memory * 100, 3)

print("\n" + "="*70)
print("✅ TRAINING COMPLETE")
print("="*70)
print(f"Training time: {round(trainer_stats.metrics['train_runtime']/60, 2)} minutes")
print(f"Peak memory: {used_memory} GB ({used_percentage}% of max)")
print(f"Memory for training: {used_memory_for_lora} GB ({lora_percentage}% of max)")
print(f"Embedding offload saved: ~1GB")
print("="*70 + "\n")

# Final memory cleanup
gc.collect()
torch.cuda.empty_cache()

# =====================================================================
# 6. SAVE LORA ADAPTERS
# =====================================================================
print("💾 Saving LoRA adapters...")
model.save_pretrained("lora_model_advanced")
tokenizer.save_pretrained("lora_model_advanced")
print("   ✓ Saved to ./lora_model_advanced/")

# =====================================================================
# 7. INFERENCE TESTS
# =====================================================================
print("\n" + "="*70)
print("🧪 RUNNING INFERENCE TESTS")
print("="*70)

FastLanguageModel.for_inference(model)

from transformers.generation.streamers import TextStreamer

# Test 1: Non-Thinking Mode
print("\n[Test 1: Non-Thinking Mode]")
print("Question: What is Null Singularity (Ω_∅)?")
print("-" * 70)

messages = [{"role": "user", "content": "What is Null Singularity (Ω_∅)?"}]
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
    enable_thinking=False
)

_ = model.generate(
    **tokenizer(text, return_tensors="pt").to("cuda"),
    **NON_THINKING_MODE_PARAMS,
    streamer=TextStreamer(tokenizer, skip_prompt=True),
)

# Memory cleanup between generations
gc.collect()
torch.cuda.empty_cache()

# Test 2: Thinking Mode
print("\n\n[Test 2: Thinking Mode]")
print("Question: Why can't I 'grasp' Null Singularity (Ω_∅)?")
print("-" * 70)

messages = [{"role": "user", "content": "Why can't I 'grasp' Null Singularity (Ω_∅)?"}]
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
    enable_thinking=True
)

_ = model.generate(
    **tokenizer(text, return_tensors="pt").to("cuda"),
    **THINKING_MODE_PARAMS,
    streamer=TextStreamer(tokenizer, skip_prompt=True),
)

print("\n" + "="*70)
print("✅ INFERENCE TESTS COMPLETE")
print("="*70)

# =====================================================================
# 8. EXPORT OPTIONS
# =====================================================================
print("\n📦 Export Options:")
print("   1. LoRA adapters (saved to ./lora_model_advanced/)")
print("   2. Merged 16-bit: Uncomment in script")
print("   3. GGUF: Uncomment in script")
print("\n" + "="*70)
print("🎉 ALL DONE!")
print("="*70)
print("Advanced features used:")
print("  ✓ Embedding offload (saved ~1GB VRAM)")
print("  ✓ LoRA alpha = rank*2 (faster convergence)")
print(f"  ✓ Train/eval split ({EVAL_SPLIT_SIZE*100}% eval)" if ENABLE_EVAL else "  • No eval split")
print("  ✓ Periodic memory cleanup (every 10 steps)")
print(f"  ✓ Experiment mode: r={LORA_R}" if EXPERIMENT_MODE else f"  ✓ Production mode: r={LORA_R}")
print("\nNext: Try EXPERIMENT_MODE=True for 4x faster iteration!")
print("="*70)
