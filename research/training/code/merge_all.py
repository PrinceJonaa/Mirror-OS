#!/usr/bin/env python3
"""
Final Merge Script
Combines all phases into one expanded training dataset.
"""

import json
import random
from pathlib import Path

# Input files
ORIGINAL_FILE = "training_codex.jsonl"
PHASE1_FILE = "training_codex_phase1.jsonl"
PHASE2_FILE = "training_codex_phase2.jsonl"
PHASE3_FILE = "training_codex_phase3.jsonl"

# Output file
FINAL_FILE = "training_codex_expanded.jsonl"

def load_jsonl(filepath):
    """Load JSONL file."""
    examples = []
    if not Path(filepath).exists():
        return examples
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                examples.append(json.loads(line))
    return examples

def save_jsonl(examples, filepath):
    """Save to JSONL."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')

def merge_all_phases():
    """Merge all phases into final dataset."""
    print("=" * 70)
    print("FINAL MERGE: Combining All Phases")
    print("=" * 70)
    print()
    
    # Load all phases
    print("📂 Loading datasets...")
    original = load_jsonl(ORIGINAL_FILE)
    phase1 = load_jsonl(PHASE1_FILE)
    phase2 = load_jsonl(PHASE2_FILE)
    phase3 = load_jsonl(PHASE3_FILE)
    
    print(f"  ✓ Original: {len(original)} examples")
    print(f"  ✓ Phase 1 (paraphrased): {len(phase1)} examples")
    print(f"  ✓ Phase 2 (thematic): {len(phase2)} examples")
    print(f"  ✓ Phase 3 (dialogues): {len(phase3)} examples")
    print()
    
    # Merge all (Phase1 already contains original)
    all_examples = []
    
    if phase1:
        all_examples.extend(phase1)  # Contains original + paraphrased
    else:
        all_examples.extend(original)  # Fallback if Phase1 wasn't run
    
    all_examples.extend(phase2)
    all_examples.extend(phase3)
    
    print(f"📊 Total before shuffle: {len(all_examples)} examples")
    
    # Shuffle for better training distribution
    random.shuffle(all_examples)
    
    print(f"🔀 Shuffled for training distribution")
    print()
    
    # Save final dataset
    save_jsonl(all_examples, FINAL_FILE)
    
    print("=" * 70)
    print("✅ MERGE COMPLETE")
    print("=" * 70)
    print(f"Final dataset: {FINAL_FILE}")
    print(f"Total examples: {len(all_examples)}")
    print(f"Growth from original: {len(all_examples) / len(original):.1f}x")
    print()
    print("Dataset breakdown:")
    print(f"  • Original + Paraphrased: {len(phase1) if phase1 else len(original)}")
    print(f"  • Thematic new Q&As: {len(phase2)}")
    print(f"  • Multi-turn dialogues: {len(phase3)}")
    print()
    print("=" * 70)
    print()
    print("🎯 Next steps:")
    print("1. Review sample from training_codex_expanded.jsonl")
    print("2. Upload to Colab for training")
    print("3. Train with same settings (2 epochs)")
    print("4. Test inference for Style B improvements")
    print("=" * 70)
    
    return all_examples

if __name__ == "__main__":
    print("\n🚀 Final Merge: Creating Expanded Dataset")
    print("=" * 70)
    
    # Merge all phases
    final_dataset = merge_all_phases()
    
    print("\n✨ Dataset expansion complete!")
    print(f"   Ready for training: {FINAL_FILE}")
