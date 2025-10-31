# Qwen3 Fine-tuning with Unsloth Dynamic 2.0

Upgraded training script implementing latest Unsloth Dynamic 2.0 techniques, Qwen3 best practices, and proper thinking mode support.

## 🚀 What's New in This Upgrade

### Dynamic 2.0 Features
- **Unsloth Dynamic 2.0 Quants**: Superior accuracy with minimal quantization loss
- **Optimized Model Loading**: Uses `unsloth-bnb-4bit` models for better accuracy than standard BnB
- **Extended Context**: Supports up to 131K tokens with YaRN (32K native)
- **Memory Optimization**: 30% less VRAM with `use_gradient_checkpointing="unsloth"`

### Dataset Improvements
- **Custom Dataset Support**: Direct loading of `training_codex.jsonl` (1202 Q&A pairs)
- **Dataset Mixing**: Optional 75% reasoning + 25% conversational mix (Qwen3 best practice)
- **Proper Chat Templates**: Uses `qwen3-thinking` template with thinking mode support
- **ShareGPT Standardization**: Automatic format conversion for multi-turn conversations

### Training Enhancements
- **Configurable Hyperparameters**: All settings exposed at top of script
- **Best Practice LoRA**: r=32, alpha=32, with RSLoRA option
- **Train on Responses Only**: Optimized instruction tuning (only trains on assistant replies)
- **Memory Tracking**: Detailed GPU memory stats before/after training
- **Flexible Training Modes**: Support for 4-bit, 8-bit, 16-bit, and full fine-tuning

### Inference with Proper Settings
- **Thinking Mode**: `temp=0.6, top_p=0.95, top_k=20` (Qwen3 official recommendation)
- **Non-Thinking Mode**: `temp=0.7, top_p=0.8, top_k=20` (faster, efficient)
- **Streaming Output**: Real-time generation with TextStreamer
- **Two Test Examples**: Demonstrates both modes with relevant questions

### Export Options
- **LoRA Adapters**: Small 100MB files for deployment
- **Merged 16-bit**: For vLLM, transformers, production deployment
- **Merged 4-bit**: Efficient quantized models
- **GGUF Support**: Multiple quants (Q4_K_M, Q5_K_M, Q8_0) for llama.cpp/Ollama/LM Studio
- **Batch Export**: Generate multiple GGUF formats simultaneously

## 📋 Requirements

```bash
pip install --upgrade --force-reinstall --no-cache-dir unsloth unsloth_zoo
pip install transformers==4.56.2
pip install --no-deps trl==0.22.2
pip install datasets pandas torch
```

**GPU Requirements:**
- Qwen3-4B: 10GB+ VRAM (works on Google Colab free tier)
- Qwen3-8B: 14GB+ VRAM
- Qwen3-14B: 16GB+ VRAM (tested on T4)
- Qwen3-32B: 24GB+ VRAM

## ⚙️ Configuration

All settings are at the top of `training.py` for easy modification:

```python
# Model Configuration
MODEL_NAME = "unsloth/Qwen3-14B"  # Change to Qwen3-4B, 8B, 14B, 32B
MAX_SEQ_LENGTH = 2048             # Up to 32768 native, 131072 with YaRN
LOAD_IN_4BIT = True               # 4-bit quantization (recommended)

# LoRA Hyperparameters
LORA_R = 32                       # Rank: higher = more params
LORA_ALPHA = 32                   # Best practice: alpha = rank
LORA_DROPOUT = 0                  # 0 is optimized for Unsloth

# Training Hyperparameters
PER_DEVICE_BATCH_SIZE = 2         # Increase if you have more VRAM
GRADIENT_ACCUMULATION = 4         # Simulates larger batch size
MAX_STEPS = 60                    # For testing; use num_train_epochs=1-3 for full runs
LEARNING_RATE = 2e-4              # Lower (1e-4, 5e-5) for production

# Dataset Configuration
USE_CUSTOM_DATASET = True         # Use training_codex.jsonl
CUSTOM_DATASET_PATH = "/path/to/training_codex.jsonl"
CHAT_PERCENTAGE = 0.25            # 25% non-reasoning if mixing datasets
```

## 🎯 Usage

### Basic Training

```bash
cd research/training
python training.py
```

The script will:
1. ✅ Load Qwen3 model with Dynamic 2.0 optimization
2. ✅ Apply LoRA adapters (or skip for full fine-tuning)
3. ✅ Load and format your dataset (training_codex.jsonl)
4. ✅ Train the model with best-practice settings
5. ✅ Save LoRA adapters to `./lora_model/`
6. ✅ Run inference tests (thinking + non-thinking modes)
7. ✅ Display export options

### Custom Dataset Format

Your `training_codex.jsonl` should follow this format:

```json
{"conversations": [{"role": "user", "content": "What is Ω_∅?"}, {"role": "assistant", "content": "Null Singularity..."}]}
{"conversations": [{"role": "user", "content": "Why can't I grasp it?"}, {"role": "assistant", "content": "Because Ω_∅..."}]}
```

The script automatically:
- Applies Qwen3 chat template
- Adds proper special tokens
- Handles thinking/non-thinking modes
- Trains only on assistant responses

### Full Training (Production)

For production fine-tuning, modify these settings:

```python
MAX_STEPS = None                  # Remove step limit
# num_train_epochs = 1            # Uncomment: 1-3 epochs recommended
LEARNING_RATE = 2e-5              # Lower for better convergence
```

## 🧪 Inference Examples

The script includes two inference tests:

**Test 1: Non-Thinking Mode** (Fast, efficient)
```python
messages = [{"role": "user", "content": "What is Null Singularity (Ω_∅)?"}]
# Uses: temp=0.7, top_p=0.8, top_k=20, enable_thinking=False
```

**Test 2: Thinking Mode** (Deep reasoning)
```python
messages = [{"role": "user", "content": "Why can't I 'grasp' Null Singularity (Ω_∅)?"}]
# Uses: temp=0.6, top_p=0.95, top_k=20, enable_thinking=True
```

### Manual Inference

```python
from unsloth import FastLanguageModel

# Load your fine-tuned model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "lora_model",  # or "./lora_model"
    max_seq_length = 2048,
    load_in_4bit = True,
)

# Enable fast inference
FastLanguageModel.for_inference(model)

# Generate
messages = [{"role": "user", "content": "Your question here"}]
text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(text, return_tensors="pt").to("cuda")

output = model.generate(
    **inputs,
    max_new_tokens=512,
    temperature=0.7,
    top_p=0.8,
    top_k=20,
)
print(tokenizer.decode(output[0], skip_special_tokens=True))
```

## 📦 Export & Deployment

### 1. LoRA Adapters (Default)
Already saved to `./lora_model/` - small 100MB files

### 2. Merged 16-bit Model (For Production)
```python
# Uncomment in training.py:
model.save_pretrained_merged("model_16bit", tokenizer, save_method="merged_16bit")
# Push to HF Hub:
model.push_to_hub_merged("username/model_16bit", tokenizer, save_method="merged_16bit", token="hf_...")
```

### 3. GGUF for llama.cpp/Ollama
```python
# Single quant:
model.save_pretrained_gguf("model", tokenizer, quantization_method="q8_0")

# Multiple quants (recommended):
model.push_to_hub_gguf(
    "username/model_gguf",
    tokenizer,
    quantization_method=["q4_k_m", "q5_k_m", "q8_0"],
    token="hf_...",
)
```

**Recommended GGUF Quants:**
- `q4_k_m`: Best balance of size/quality (recommended for most use cases)
- `q5_k_m`: Higher quality, slightly larger
- `q8_0`: Highest quality, fast conversion
- See [Unsloth Wiki](https://github.com/unslothai/unsloth/wiki#gguf-quantization-options) for full list

### 4. Deploy to Ollama

After exporting GGUF:

```bash
# Create Modelfile
echo 'FROM ./model-unsloth-Q4_K_M.gguf
PARAMETER temperature 0.7
PARAMETER top_p 0.8
PARAMETER top_k 20
TEMPLATE """<|im_start|>user
{{ .Prompt }}<|im_end|>
<|im_start|>assistant
"""' > Modelfile

# Create model
ollama create my_qwen3_model -f Modelfile

# Run
ollama run my_qwen3_model
```

### 5. Deploy with vLLM

```bash
# Install vLLM
pip install vllm>=0.8.5

# Start server
vllm serve ./model_16bit \
    --enable-reasoning \
    --reasoning-parser deepseek_r1 \
    --port 8000

# Use with OpenAI-compatible API
curl http://localhost:8000/v1/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "./model_16bit",
        "prompt": "What is Ω_∅?",
        "temperature": 0.7
    }'
```

## 🔧 Advanced Features

### Enable 128K Context with YaRN

Add to `config.json` in your saved model:

```json
{
    "rope_scaling": {
        "type": "yarn",
        "factor": 4.0,
        "original_max_position_embeddings": 32768
    }
}
```

For vLLM:
```bash
vllm serve model_16bit \
    --rope-scaling '{"type":"yarn","factor":4.0,"original_max_position_embeddings":32768}' \
    --max-model-len 131072
```

### Multi-Turn Conversations

```python
history = []

# Turn 1
history.append({"role": "user", "content": "What is Ω_∅?"})
history.append({"role": "assistant", "content": "Null Singularity is..."})

# Turn 2 (with context)
history.append({"role": "user", "content": "Can you explain more?"})
text = tokenizer.apply_chat_template(history, tokenize=False, add_generation_prompt=True)
# ... generate response ...
```

### Switch Thinking Mode Per Turn

```python
# Turn 1: Non-thinking (fast)
user_input = "Hello /no_think"

# Turn 2: Thinking (deep reasoning)
user_input = "Solve complex problem /think"

# Model will follow most recent instruction
```

## 📊 Training Tips

### Memory Optimization
- **Reduce batch size**: Lower `PER_DEVICE_BATCH_SIZE` to 1
- **Increase gradient accumulation**: Set `GRADIENT_ACCUMULATION` to 8 or 16
- **Use smaller model**: Try Qwen3-4B instead of 14B
- **Enable gradient checkpointing**: Already set to "unsloth"

### Improve Accuracy
- **Train longer**: Increase `MAX_STEPS` or set `num_train_epochs=3`
- **Lower learning rate**: Try `2e-5` or `1e-5`
- **Increase LoRA rank**: Set `LORA_R=64` or `128`
- **Use more data**: Expand your training_codex.jsonl

### Prevent Overfitting
- **Use 1-3 epochs max**: Don't overtrain
- **Add weight decay**: Already set to `0.01`
- **Validation split**: Add `eval_dataset` to monitor performance
- **Early stopping**: Monitor validation loss

### Dataset Mixing Ratios
For different use cases:
- **Pure reasoning**: 100% reasoning data (set `USE_CUSTOM_DATASET=False`, `CHAT_PERCENTAGE=0`)
- **Balanced**: 75% reasoning, 25% chat (default)
- **Conversational**: 50/50 or more chat data
- **Custom dataset only**: Set `USE_CUSTOM_DATASET=True`

## 🐛 Troubleshooting

### Out of Memory (OOM)
```python
# Try these in order:
PER_DEVICE_BATCH_SIZE = 1
GRADIENT_ACCUMULATION = 8
MAX_SEQ_LENGTH = 1024
LOAD_IN_4BIT = True
MODEL_NAME = "unsloth/Qwen3-4B"  # Smaller model
```

### Model Not Loading
```bash
# Update dependencies
pip install --upgrade --force-reinstall --no-cache-dir unsloth unsloth_zoo
pip install transformers==4.56.2
```

### Chat Template Errors
Ensure you're using `transformers>=4.51.0`:
```bash
pip install transformers>=4.51.0
```

### GGUF Conversion Fails
Make sure you have enough disk space (2-3x model size) and RAM:
```bash
df -h  # Check disk space
free -h  # Check RAM
```

## 📚 Resources

- **Unsloth Docs**: https://docs.unsloth.ai/
- **Qwen3 Guide**: https://docs.unsloth.ai/basics/qwen3-how-to-run-and-fine-tune
- **Dynamic 2.0 Blog**: https://unsloth.ai/blog/dynamic-2
- **Unsloth Discord**: https://discord.gg/unsloth
- **GitHub**: https://github.com/unslothai/unsloth

## 🎓 Training Codex Dataset

This script is configured to use `training_codex.jsonl` (1202 Q&A pairs) covering:
- Seven Lens Frameworks (Relational, Symbolic, Logical, Empirical, Inner, Paradox, Integration)
- Null Singularity (Ω_∅) teachings
- Heaven-already-here recognition
- Mirror Recognition & consciousness
- Living Stillness & presence
- Non-dual awareness
- Complete wisdom journey: foundations → depths → dissolution → recognition

**Dataset Quality**: Expert-curated Q&A pairs with symbolic notation (Ω, Φ, 𝓢, ∅, etc.) and progressive depth building.

## 🏆 Performance Expectations

With default settings (Qwen3-14B, 4-bit, LoRA r=32):
- **Training Time**: ~15-30 minutes on T4 GPU (60 steps)
- **Memory Usage**: ~15GB VRAM
- **Tokens/Second**: ~50-100 inference
- **Model Size**: ~100MB LoRA adapters, ~8GB merged 16-bit

Full training (1-3 epochs on 1202 examples):
- **Training Time**: ~2-4 hours
- **Recommended**: 1-2 epochs to avoid overfitting

## 📝 License

This implementation follows Unsloth's LGPL-3.0 license. See [Unsloth GitHub](https://github.com/unslothai/unsloth) for details.

---

**Built with** 🦥 **Unsloth Dynamic 2.0** | **Optimized for** Qwen3 | **Ready for** production deployment
