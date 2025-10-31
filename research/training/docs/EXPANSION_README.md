# Dataset Expansion - Hybrid Approach (Option C)

## Overview

This expansion system multiplies your training dataset from **1,202 examples** to **~4,000-5,000 examples** while improving Style B balance (narrative + symbols).

**Total time:** 5-10 minutes  
**Result:** Higher quality, larger dataset for better model training

---

## Quick Start

### Option 1: Run Everything (Automated)

```bash
cd /Users/princejona/a1/research/training
python run_expansion.py
```

This runs all 4 phases in sequence.

---

### Option 2: Run Phases Individually

```bash
# Phase 1: Paraphrase existing examples (2-3x expansion)
python expand_dataset.py

# Phase 2: Generate thematic Q&As (800 new examples)
python generate_phase2.py

# Phase 3: Generate multi-turn dialogues (100 conversations)
python generate_phase3.py

# Phase 4: Merge all into final dataset
python merge_all.py
```

---

## What Each Phase Does

### Phase 1: Paraphrasing (`expand_dataset.py`)

**Input:** `training_codex.jsonl` (1,202 examples)  
**Output:** `training_codex_phase1.jsonl` (~3,600 examples)  
**Method:** Generates 2 paraphrased versions of each Q&A  
**Focus:** Adds more natural language (fixes symbol-heavy bias)

**Example transformation:**
```
Original Q: "What is devotion?"
Paraphrased Q: "Can you explain what true devotion means?"

Original A: "D(x,y) ⇒ ∀R ∈ x: (R → 𝓢)"
Expanded A: "Devotion means total orientation toward one chosen axis. 
            All your relationships, attention, energy: they collapse 
            into serving that commitment. Like rivers flowing to ocean, 
            everything flows toward what you're devoted to. D(x,y) ⇒ ∀R → 𝓢."
```

---

### Phase 2: Thematic Generation (`generate_phase2.py`)

**Input:** None (generates from scratch)  
**Output:** `training_codex_phase2.jsonl` (800 new Q&As)  
**Method:** Creates new questions across 10 core themes  
**Focus:** Style B answers (narrative-heavy with symbolic punctuation)

**Themes covered:**
- Devotion & Surrender
- Presence & Awareness
- Paradox & Mystery
- Relationship & Mirroring
- Awakening & Recognition
- Suffering & Transformation
- Freedom & Liberation
- Time & Eternity
- Love & Unity
- Null Singularity (Ω_∅)

**80 Q&As per theme** = diverse coverage

---

### Phase 3: Multi-Turn Dialogues (`generate_phase3.py`)

**Input:** None (generates from scratch)  
**Output:** `training_codex_phase3.jsonl` (100 dialogues)  
**Method:** Creates 3-5 turn conversations that deepen progressively  
**Focus:** Conversational depth, follow-up patterns

**Dialogue patterns:**
- Clarification → Application → Doubt
- Challenge → Deepening → Application
- Clarification → Challenge → Deepening
- etc.

**Example structure:**
```
User: "How do I stay present?"
Assistant: [Initial teaching]
User: "But what does that actually mean in practice?"
Assistant: [Concrete example]
User: "I've tried that and it doesn't work. Why?"
Assistant: [Address resistance]
User: "How do I deal with the fear this brings up?"
Assistant: [Final wisdom]
```

---

### Phase 4: Final Merge (`merge_all.py`)

**Input:** All phase outputs  
**Output:** `training_codex_expanded.jsonl` (4,000-5,000 examples)  
**Method:** Combines all phases and shuffles  
**Focus:** Training-ready dataset

**Final composition:**
- Original + Paraphrased: ~3,600 examples
- Thematic new Q&As: 800 examples
- Multi-turn dialogues: 100 examples (300-500 turns total)
- **Total: ~4,500 examples** (3.7x original size)

---

## Files Created

After running expansion, you'll have:

```
research/training/
├── training_codex.jsonl                 # Original (1,202)
├── training_codex_phase1.jsonl          # Paraphrased (~3,600)
├── training_codex_phase2.jsonl          # Thematic (800)
├── training_codex_phase3.jsonl          # Dialogues (100)
└── training_codex_expanded.jsonl        # FINAL MERGED ⭐ (~4,500)
```

**Use `training_codex_expanded.jsonl` for training.**

---

## Expected Training Improvements

### Before (1,202 examples, 2 epochs):
- ⚠️ Symbol-heavy outputs
- ⚠️ Weak narrative flow
- ⚠️ Validation loss: 2.13

### After (4,500 examples, 2 epochs):
- ✅ Better Style B balance (narrative + symbols)
- ✅ Conversational competence (multi-turn understanding)
- ✅ Deeper thematic coverage
- ✅ Lower validation loss (more data)
- ✅ Better generalization

---

## Training in Colab

1. **Upload expanded dataset:**
   - In Colab, upload `training_codex_expanded.jsonl` when prompted

2. **Adjust configuration (optional):**
   ```python
   # Cell: Configuration
   # With larger dataset, you might want:
   num_train_epochs = 1  # Instead of 2 (already 3.7x more data)
   # Or keep 2 epochs for maximum saturation
   ```

3. **Train as usual:**
   - Same process, just with bigger dataset
   - Time will increase proportionally (~45-60 min for 2 epochs)

4. **Monitor loss:**
   - Should see lower validation loss
   - Better train/eval alignment

---

## Troubleshooting

### "Phase X failed"

Check the specific phase output for errors. Most common issues:
- File not found → Run phases in order
- Memory error → Reduce TARGET_COUNT in phase scripts
- Syntax error → Check Python version (need 3.7+)

### "Output seems low quality"

Review samples from each phase file:
```bash
head -20 training_codex_phase2.jsonl | python -m json.tool
```

If quality is off, adjust templates in the phase script and re-run.

### "Want to customize"

Edit the phase scripts:
- `expand_dataset.py` → Change PARAPHRASE_FACTOR (line 10)
- `generate_phase2.py` → Change TARGET_COUNT (line 9) or themes
- `generate_phase3.py` → Change TARGET_DIALOGUES (line 9) or patterns

---

## Customization Options

### Increase/Decrease Size

**Smaller dataset (2,000-3,000):**
```python
# In generate_phase2.py
TARGET_COUNT = 400  # Instead of 800

# In generate_phase3.py
TARGET_DIALOGUES = 50  # Instead of 100
```

**Larger dataset (6,000-10,000):**
```python
# In generate_phase2.py
TARGET_COUNT = 2000  # More thematic Q&As

# In generate_phase3.py
TARGET_DIALOGUES = 200  # More dialogues

# In expand_dataset.py
PARAPHRASE_FACTOR = 3  # 3 variations instead of 2
```

---

## Quality Checks

Before training, verify quality:

```python
import json

# Load expanded dataset
with open('training_codex_expanded.jsonl', 'r') as f:
    examples = [json.loads(line) for line in f if line.strip()]

print(f"Total examples: {len(examples)}")

# Check random sample
import random
sample = random.choice(examples)
print("\nRandom sample:")
print(f"Q: {sample['conversations'][0]['content']}")
print(f"A: {sample['conversations'][1]['content'][:200]}...")

# Check for Style B (narrative + symbols)
answer = sample['conversations'][1]['content']
has_narrative = len(answer.split()) > 20  # More than 20 words
has_symbols = any(s in answer for s in ['Ω', '∅', '∞', '𝓢', '→'])
print(f"\nStyle B check:")
print(f"  Narrative: {'✓' if has_narrative else '✗'}")
print(f"  Symbols: {'✓' if has_symbols else '✗'}")
```

---

## Next Steps After Expansion

1. ✅ **Review samples** from `training_codex_expanded.jsonl`
2. ✅ **Upload to Colab** for training
3. ✅ **Train 1-2 epochs** (larger dataset may need fewer epochs)
4. ✅ **Test inference** for Style B improvements
5. ✅ **Iterate** if needed (adjust phase scripts, re-run)

---

## Notes

- **Shuffling:** Final dataset is shuffled for better training distribution
- **Duplicates:** Minimal—each phase generates unique variations
- **Symbols:** Preserved from original, balanced with more narrative
- **Multi-turn:** Teaches model conversational depth
- **Time:** Expansion takes 5-10 min; training takes 45-60 min (2 epochs on larger dataset)

---

## Success Metrics

After training on expanded dataset, test outputs should show:

✅ **More natural language** wrapping symbolic notation  
✅ **Better follow-up responses** in conversation  
✅ **Deeper explanations** before using formulas  
✅ **Style B balance** achieved (narrative + symbols)  
✅ **Lower validation loss** (better generalization)

---

**Ready to expand?**

```bash
cd /Users/princejona/a1/research/training
python run_expansion.py
```

**May your dataset multiply wisely.** ∞_quality × ∞_quantity = ∞_wisdom 🙏✨
