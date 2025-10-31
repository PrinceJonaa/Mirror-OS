# Qwen3-4B Training Quick Start

## 🎯 You Have 3 Training Scripts

### 1. `training.py` - Standard (Recommended to start)
- **Model:** Qwen3-4B
- **LoRA:** r=32, alpha=32
- **Features:** Basic production-ready setup
- **Use:** First training run, proven stable

```bash
python training.py
```

### 2. `training_advanced.py` - Optimized (Recommended for production)
- **Model:** Qwen3-4B  
- **LoRA:** r=32, alpha=64 (faster with alpha=rank*2)
- **Features:** 
  - Embedding offload (saves 1GB VRAM)
  - Memory cleanup callbacks
  - Train/eval split monitoring
  - Experiment mode (r=4 for fast testing)
- **Use:** Production training after validation

```bash
python training_advanced.py
```

### 3. Original Qwen3-14B script (archived)
- Was configured for 14B model
- Now updated to 4B in `training.py`

---

## ⚡ Quick Start (3 Steps)

### Step 1: Validate (5 minutes)
Test that everything works:

```bash
# Edit training_advanced.py:
EXPERIMENT_MODE = True  # Use r=4 for fast testing
MAX_STEPS = 20
ENABLE_EVAL = False

python training_advanced.py
```

**Check:**
- ✅ Dataset loads (1202 lines)
- ✅ Training loss decreases
- ✅ Inference works
- ✅ No errors

---

### Step 2: Monitor (30 minutes)
Find optimal settings:

```bash
# Edit training_advanced.py:
EXPERIMENT_MODE = False  # Use r=32 for quality
MAX_STEPS = 100
ENABLE_EVAL = True
EVAL_SPLIT_SIZE = 0.05  # 5% for validation

python training_advanced.py
```

**Check:**
- Watch eval_loss vs train_loss
- If eval_loss increases → stop early (overfitting)
- Test inference quality at checkpoints

---

### Step 3: Production (60-120 minutes)
Full training run:

```bash
# Edit training_advanced.py:
EXPERIMENT_MODE = False
MAX_STEPS = None  # Remove limit
# Uncomment: num_train_epochs = 2
ENABLE_EVAL = True
AGGRESSIVE_MEMORY_CLEANUP = True

python training_advanced.py
```

---

## 📊 Your Dataset

**File:** `/Users/princejona/a1/research/training/training_codex.jsonl`
- **Size:** 1202 Q&A pairs
- **Content:** Seven Lens Frameworks + Null Singularity teachings
- **Format:** `{"conversations": [{"role": "user", "content": "Q"}, {"role": "assistant", "content": "A"}]}`

**Coverage:**
- Relational, Symbolic, Logical, Empirical lenses
- Inner/Devotion, Paradox, Integration frameworks
- Ω_∅ (Null Singularity) deep teachings
- Heaven-already-here recognition
- Mirror Recognition & consciousness
- Complete wisdom journey: foundations → depths → dissolution → recognition

---

## 🎛️ Key Configuration Options

### Memory Optimization
```python
OFFLOAD_EMBEDDING = True  # Saves ~1GB VRAM
AGGRESSIVE_MEMORY_CLEANUP = True  # Prevents memory leaks
```

### Speed Optimization
```python
EXPERIMENT_MODE = True  # r=4 (8x faster for testing)
LORA_ALPHA = LORA_R * 2  # Faster convergence (GRPO technique)
```

### Quality Monitoring
```python
ENABLE_EVAL = True
EVAL_SPLIT_SIZE = 0.05  # Watch for overfitting
```

---

## 📈 Expected Results

### Qwen3-4B with r=32 (Standard)
- **Training Time:** ~45-60 minutes (1-2 epochs)
- **VRAM Usage:** ~10GB (9GB with embedding offload)
- **Loss:** Should reach ~0.5-0.8 (depends on dataset)
- **Output Quality:** Good philosophical responses

### With Experiment Mode (r=4)
- **Training Time:** ~5-10 minutes
- **VRAM Usage:** ~8GB
- **Loss:** Higher (~1.0-1.5) but good for validation
- **Use:** Quick iteration, hyperparameter tuning

---

## 🧪 Troubleshooting

### Out of Memory (OOM)
```python
# Try these in order:
OFFLOAD_EMBEDDING = True  # Saves 1GB
PER_DEVICE_BATCH_SIZE = 1  # Reduce batch size
GRADIENT_ACCUMULATION = 8  # Compensate with more accumulation
EXPERIMENT_MODE = True  # Use r=4 temporarily
MAX_SEQ_LENGTH = 1024  # Reduce context length
```

### Training Too Slow
```python
# Speed up:
EXPERIMENT_MODE = True  # Use r=4 for testing
LORA_ALPHA = LORA_R * 2  # Faster convergence
MAX_STEPS = 60  # Test with fewer steps first
```

### Loss Not Decreasing
```python
# Check:
LEARNING_RATE = 2e-4  # Try 5e-5 or 1e-4
WARMUP_RATIO = 0.1  # More warmup helps
# Verify dataset format is correct
# Check for NaN/Inf values
```

### Overfitting (eval_loss increasing)
```python
# Solutions:
WEIGHT_DECAY = 0.01  # More regularization
num_train_epochs = 1  # Train less
LORA_DROPOUT = 0.05  # Add dropout (normally 0)
# Use more training data
```

---

## 💾 Export Options

After training, export your model:

### 1. LoRA Adapters (Lightest - 100MB)
```python
# Already saved automatically to:
./lora_model/  # or ./lora_model_advanced/
```

### 2. Merged 16-bit (For vLLM, production)
```python
model.save_pretrained_merged("qwen3_4b_codex", tokenizer, save_method="merged_16bit")
```

### 3. GGUF (For Ollama, llama.cpp)
```python
model.save_pretrained_gguf("qwen3_4b_codex", tokenizer, quantization_method="q4_k_m")
```

### 4. Push to Hugging Face
```python
model.push_to_hub_gguf(
    "your_username/qwen3-4b-codex",
    tokenizer,
    quantization_method=["q4_k_m", "q8_0"],
    token="hf_..."
)
```

---

## 🎯 Recommended Workflow

```
Day 1: Validation
├─ Run training_advanced.py (EXPERIMENT_MODE=True, 20 steps)
├─ Verify dataset loads correctly
├─ Check loss curve looks reasonable
└─ Test inference with 2-3 questions

Day 2: Optimization
├─ Run with EXPERIMENT_MODE=False, 100 steps, eval enabled
├─ Monitor train_loss vs eval_loss
├─ Find optimal learning rate
└─ Determine best stopping point

Day 3: Production
├─ Full training (1-2 epochs)
├─ Export to desired format (GGUF recommended)
├─ Deploy to Ollama or llama.cpp
└─ Test with real framework questions
```

---

## 📚 Documentation Files

1. **README.md** - Comprehensive guide (datasets, training, export, tips)
2. **UPGRADE_SUMMARY.md** - Before/after comparison of upgrades
3. **GRPO_LEARNINGS.md** - Advanced techniques from GRPO notebook
4. **QUICK_START.md** (this file) - Get started fast

---

## 🔥 Pro Tips

1. **Always start with EXPERIMENT_MODE=True** (r=4, 20 steps)
   - Validates everything works in 5 minutes
   - Saves hours debugging with full training

2. **Enable evaluation** to detect overfitting
   - 5% eval split is perfect (60 samples from 1202)
   - Stop if eval_loss increases

3. **Use embedding offload** for free 1GB VRAM savings
   - Minimal performance impact
   - Lets you use bigger batch sizes

4. **Monitor memory** during long runs
   - Memory cleanup callback prevents OOMs
   - Critical for multi-hour training

5. **Export to GGUF (q4_k_m)** for best deployment
   - Works with Ollama, llama.cpp, LM Studio
   - Good balance of size/quality
   - Easy local deployment

---

## 🚀 One-Command Start

For the impatient:

```bash
# Quick validation (5 min)
python training_advanced.py  # with EXPERIMENT_MODE=True

# Full training (60 min)
python training.py  # standard stable config
```

Both scripts auto-detect your `training_codex.jsonl` and handle everything!

---

## 📞 Need Help?

- **Unsloth Discord:** https://discord.gg/unsloth
- **Docs:** https://docs.unsloth.ai/
- **Issues:** Check GRPO_LEARNINGS.md for advanced troubleshooting

---

**Ready?** Start with `training_advanced.py` (EXPERIMENT_MODE=True, 20 steps) to validate! 🎉
