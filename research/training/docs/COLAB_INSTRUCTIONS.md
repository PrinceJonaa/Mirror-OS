# Google Colab Training Instructions

## 📦 What You Have

1. **`Qwen3_4B_Training_Colab.ipynb`** - Ready-to-run notebook
2. **`training_codex.jsonl`** - Your dataset (1202 Q&A pairs)

---

## 🚀 Steps to Train in Colab

### Step 1: Upload Notebook to Colab

1. Go to [colab.research.google.com](https://colab.research.google.com)
2. Click **File → Upload notebook**
3. Upload `Qwen3_4B_Training_Colab.ipynb`

---

### Step 2: Enable GPU

1. Click **Runtime → Change runtime type**
2. Select **Hardware accelerator: T4 GPU**
3. Click **Save**

---

### Step 3: Run Setup (Cell 1-3)

Run the first 3 cells:
1. **Cell 1**: Title/description (just markdown)
2. **Cell 2**: Setup heading (just markdown)
3. **Cell 3**: Install Unsloth (~3 minutes)

Wait for installation to complete. You'll see:
```
✅ Installation complete!
```

---

### Step 4: Upload Your Dataset

**Cell 4** will show a file upload button. Click it and select:
- **`training_codex.jsonl`** from your computer

You'll see:
```
✅ Uploaded: training_codex.jsonl
   Size: XXX KB
   Lines: 1202
   Format: ✅ Valid JSONL with 'conversations' field
```

---

### Step 5: Configure Settings (Cell 6)

Run **Cell 6** to set configuration. Default settings are good for testing:

```python
EXPERIMENT_MODE = True   # Fast testing (5-10 min)
MAX_STEPS = 60           # Quick test run
ENABLE_EVAL = True       # Monitor overfitting
```

For production training, change to:
```python
EXPERIMENT_MODE = False  # Use r=32 for quality
MAX_STEPS = None         # Remove limit
# Uncomment: num_train_epochs = 1
```

---

### Step 6: Run All Remaining Cells

Click **Runtime → Run all** (or run cells one by one)

The notebook will:
1. ✅ Load Qwen3-4B (~2 min)
2. ✅ Apply LoRA adapters (~30 sec)
3. ✅ Prepare your dataset (~1 min)
4. ✅ Configure trainer (~10 sec)
5. ✅ Train the model (~10-60 min depending on settings)
6. ✅ Save model
7. ✅ Run inference tests
8. ✅ Download trained model

---

## ⏱️ Expected Timeline

### Experiment Mode (EXPERIMENT_MODE=True, 60 steps)
- **Total time:** ~10-15 minutes
- **Purpose:** Validate dataset format, check if loss decreases
- **Quality:** Lower (r=4), good for testing

### Production Mode (EXPERIMENT_MODE=False, 1-2 epochs)
- **Total time:** ~45-90 minutes
- **Purpose:** Full quality training
- **Quality:** High (r=32), production-ready

---

## 📊 What to Watch During Training

You'll see a table like this:

| Step | Loss | eval_loss | runtime |
|------|------|-----------|---------|
| 1    | 2.45 | 2.50      | 10s     |
| 10   | 1.83 | 1.92      | 95s     |
| 20   | 1.24 | 1.35      | 185s    |
| 30   | 0.89 | 0.98      | 275s    |

**Good signs:**
- ✅ Loss decreasing steadily
- ✅ eval_loss close to loss (not overfitting)
- ✅ No errors or warnings

**Warning signs:**
- ⚠️ eval_loss > loss by 0.5+ (overfitting - stop early!)
- ⚠️ Loss stuck or increasing (bad learning rate)
- ⚠️ Out of memory errors (reduce batch size in Cell 6)

---

## 💾 Downloading Your Model

**Cell 13** will automatically download `lora_model.zip` containing:
- Adapter weights (~100MB)
- Tokenizer files
- Config files

**To use locally:**
```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "./lora_model",  # Path to unzipped folder
    max_seq_length = 2048,
    load_in_4bit = True,
)
```

---

## 🧪 Testing During Training

After training completes, the notebook runs two inference tests:

**Test 1: Non-Thinking Mode**
- Question: "What is Null Singularity (Ω_∅)?"
- Fast, direct answers

**Test 2: Thinking Mode**
- Question: "Why can't I 'grasp' Null Singularity?"
- Detailed reasoning with <think> blocks

**Cell 12** lets you test your own questions!

---

## 🔧 Troubleshooting

### "Out of Memory" Error

Edit **Cell 6**:
```python
PER_DEVICE_BATCH_SIZE = 1  # Reduce from 2
GRADIENT_ACCUMULATION = 8  # Increase from 4
```

### "Runtime disconnected"

Free Colab limits to ~12 hours. Tips:
- Keep browser tab active
- Use Colab Pro for longer sessions
- Save checkpoints frequently

### Training loss not decreasing

Try:
```python
LEARNING_RATE = 5e-5  # Lower from 2e-4
WARMUP_RATIO = 0.2     # More warmup
```

### "Dataset format error"

Verify your `training_codex.jsonl` has this format:
```json
{"conversations": [{"role": "user", "content": "Q"}, {"role": "assistant", "content": "A"}]}
```

---

## 📤 Exporting to GGUF (Optional)

Want to use with Ollama/llama.cpp? Run **Cell 15**:

Uncomment the code and run to get GGUF format (Q4_K_M recommended).

---

## 💡 Pro Tips

1. **Start with Experiment Mode** (EXPERIMENT_MODE=True, 60 steps)
   - Validates everything works in ~10 minutes
   - Check loss decreases properly
   - Test inference quality

2. **Monitor eval_loss** to detect overfitting
   - If eval_loss increases while train_loss decreases → stop!
   - Means model memorizing, not learning

3. **Save to Google Drive** for persistence
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   # Save model to: /content/drive/MyDrive/models/
   ```

4. **Use Colab Pro** for longer training
   - Free tier: ~12 hours max
   - Pro: 24 hours + better GPUs (A100)

5. **Test inference frequently**
   - Use Cell 12 to test custom questions
   - Verify model learned your philosophical framework
   - Check for hallucinations or incorrect responses

---

## 📝 Full Workflow Summary

```
1. Upload notebook to Colab ✅
2. Enable T4 GPU ✅
3. Run installation (3 min) ✅
4. Upload training_codex.jsonl ✅
5. Configure settings ✅
6. Run all cells (10-60 min) ✅
7. Monitor training progress ✅
8. Test inference ✅
9. Download trained model ✅
10. Deploy locally or to Ollama ✅
```

---

## 🎯 Quick Start Commands

**For testing (10 min):**
- Keep all defaults
- Run all cells
- Verify loss decreases

**For production (60 min):**
- Set `EXPERIMENT_MODE = False`
- Set `MAX_STEPS = None`
- Uncomment `num_train_epochs = 1`
- Run all cells

---

## 🆘 Need Help?

- **Unsloth Discord:** https://discord.gg/unsloth
- **Docs:** https://docs.unsloth.ai/
- **GitHub Issues:** https://github.com/unslothai/unsloth

---

**Ready to train?** Upload the notebook and dataset, then click **Runtime → Run all**! 🚀
