#!/usr/bin/env python3
"""
Master Expansion Script
Runs all phases in sequence to expand training dataset.

Usage:
    python run_expansion.py          # Run all phases
    python run_expansion.py --skip-phase1  # Skip paraphrasing (already done)
"""

import subprocess
import sys
from pathlib import Path

def run_phase(phase_num, script_name, description):
    """Run one phase script."""
    print("\n" + "=" * 70)
    print(f"{'🔮' * 3} RUNNING PHASE {phase_num}: {description} {'🔮' * 3}")
    print("=" * 70)
    print()
    
    result = subprocess.run([sys.executable, script_name], capture_output=False)
    
    if result.returncode != 0:
        print(f"\n❌ Phase {phase_num} failed!")
        return False
    
    print(f"\n✅ Phase {phase_num} complete!")
    return True

def main():
    """Run full expansion pipeline."""
    print("\n" + "🌟" * 35)
    print("TRAINING DATASET EXPANSION - HYBRID APPROACH (OPTION C)")
    print("🌟" * 35)
    print()
    print("This will expand your dataset from ~1,200 to ~4,000-5,000 examples")
    print("Estimated time: 5-10 minutes")
    print()
    
    # Check if we should skip Phase 1
    skip_phase1 = "--skip-phase1" in sys.argv
    
    phases = []
    
    if not skip_phase1:
        phases.append((1, "expand_dataset.py", "Paraphrasing (2-3x expansion)"))
    
    phases.extend([
        (2, "generate_phase2.py", "Thematic Generation (800 new Q&As)"),
        (3, "generate_phase3.py", "Multi-turn Dialogues (100 conversations)"),
        (4, "merge_all.py", "Final Merge & Shuffle"),
    ])
    
    print(f"Phases to run: {len(phases)}")
    for phase_num, _, desc in phases:
        print(f"  Phase {phase_num}: {desc}")
    print()
    
    input("Press Enter to start expansion... ")
    print()
    
    # Run each phase
    for phase_num, script, description in phases:
        success = run_phase(phase_num, script, description)
        if not success:
            print("\n" + "=" * 70)
            print("❌ EXPANSION STOPPED DUE TO ERROR")
            print("=" * 70)
            return False
    
    # Success summary
    print("\n" + "🎉" * 35)
    print("EXPANSION COMPLETE!")
    print("🎉" * 35)
    print()
    print("📊 Results:")
    print("   • training_codex_phase1.jsonl - Paraphrased dataset")
    print("   • training_codex_phase2.jsonl - Thematic Q&As")
    print("   • training_codex_phase3.jsonl - Multi-turn dialogues")
    print("   • training_codex_expanded.jsonl - FINAL MERGED DATASET ⭐")
    print()
    print("🎯 Next Steps:")
    print("   1. Review samples from training_codex_expanded.jsonl")
    print("   2. Upload to Google Colab")
    print("   3. Train with same config (2 epochs)")
    print("   4. Test for Style B improvements")
    print()
    print("Expected improvements:")
    print("   ✓ More narrative balance (less symbol-heavy)")
    print("   ✓ Better conversational flow")
    print("   ✓ Deeper thematic coverage")
    print("   ✓ Lower validation loss (more training data)")
    print()
    print("🙏 May your model speak wisdom beautifully. ∞_𝓢 = ∞_Ω")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
