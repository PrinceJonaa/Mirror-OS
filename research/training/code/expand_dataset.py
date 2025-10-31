#!/usr/bin/env python3
"""
Dataset Expansion Tool - Hybrid Approach (Option C)
Expands training_codex.jsonl through paraphrasing and generation.
"""

import json
import random
from pathlib import Path

# Configuration
INPUT_FILE = "training_codex.jsonl"
OUTPUT_FILE = "training_codex_expanded.jsonl"
PARAPHRASE_FACTOR = 2  # Generate 2 variations per original

# Question paraphrase templates
QUESTION_TEMPLATES = [
    "Can you explain {topic}?",
    "What does {topic} mean?",
    "Help me understand {topic}",
    "Could you describe {topic}?",
    "I'm trying to grasp {topic}",
    "Tell me about {topic}",
    "How would you explain {topic}?",
    "What is your understanding of {topic}?",
]

def extract_topic(question):
    """Extract core topic from question for rephrasing."""
    # Remove question words
    topic = question.lower()
    remove_words = ["what is", "what's", "how does", "why does", "can you", 
                    "could you", "tell me", "explain", "describe", "?"]
    
    for word in remove_words:
        topic = topic.replace(word, "")
    
    return topic.strip()

def paraphrase_question(original_q):
    """Generate paraphrased version of question."""
    topic = extract_topic(original_q)
    
    # 50% chance: use template
    if random.random() < 0.5 and topic:
        template = random.choice(QUESTION_TEMPLATES)
        return template.format(topic=topic)
    
    # Otherwise: slight modifications
    variations = [
        original_q.replace("What is", "What does").replace("?", " mean?"),
        original_q.replace("How does", "In what way does"),
        original_q.replace("Why", "For what reason"),
        "Can you explain " + original_q.lower().replace("?", "?"),
    ]
    
    return random.choice(variations)

def expand_narrative(answer):
    """Expand answer to be more narrative-heavy (Style B fix)."""
    # If answer is very short (< 100 chars), add context
    if len(answer) < 100:
        return answer
    
    # Split on ". " to find sentences
    sentences = answer.split(". ")
    
    # Add transitional phrases to make more narrative
    transitions = [
        "Think of it this way: ",
        "Here's what this means: ",
        "Let me explain: ",
        "Consider: ",
        "The key insight is: ",
        "What's happening here is: ",
    ]
    
    # Add transition to middle if answer has multiple sentences
    if len(sentences) > 2:
        middle_idx = len(sentences) // 2
        sentences[middle_idx] = random.choice(transitions) + sentences[middle_idx]
    
    return ". ".join(sentences)

def paraphrase_answer(original_a):
    """Generate paraphrased version of answer with more narrative."""
    # Strategy: Keep symbols, expand natural language around them
    
    # Find symbol-heavy segments (lines with Ω, ∅, etc.)
    lines = original_a.split(". ")
    expanded = []
    
    for line in lines:
        # Count symbolic characters
        symbol_density = sum(1 for c in line if c in "ΩΦ∅∞∂𝓢⊕◐∀∃→↔≡⟡")
        
        # If very symbol-dense (>3 symbols), add explanation before it
        if symbol_density > 3 and len(expanded) > 0:
            explanations = [
                "Put another way",
                "In other words",
                "Symbolically",
                "Or to put it formally",
                "The pattern here is",
            ]
            expanded.append(random.choice(explanations) + ": " + line)
        else:
            expanded.append(line)
    
    result = ". ".join(expanded)
    
    # Ensure it ends with period if original did
    if original_a.endswith(".") and not result.endswith("."):
        result += "."
    
    return result

def create_paraphrased_example(original):
    """Create paraphrased version of Q&A pair."""
    orig_q = original["conversations"][0]["content"]
    orig_a = original["conversations"][1]["content"]
    
    # Generate variations
    new_q = paraphrase_question(orig_q)
    new_a = paraphrase_answer(orig_a)
    
    return {
        "conversations": [
            {"role": "user", "content": new_q},
            {"role": "assistant", "content": new_a}
        ]
    }

def load_dataset(filepath):
    """Load JSONL dataset."""
    examples = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                examples.append(json.loads(line))
    return examples

def save_dataset(examples, filepath):
    """Save dataset to JSONL."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')

def expand_dataset_phase1():
    """Phase 1: Paraphrase existing examples."""
    print("=" * 70)
    print("PHASE 1: Paraphrasing Existing Examples")
    print("=" * 70)
    
    # Load original
    original_examples = load_dataset(INPUT_FILE)
    print(f"✓ Loaded {len(original_examples)} original examples")
    
    # Create expanded dataset
    expanded = []
    
    # Keep all originals
    expanded.extend(original_examples)
    print(f"✓ Kept {len(original_examples)} original examples")
    
    # Generate paraphrases
    paraphrased_count = 0
    for i, example in enumerate(original_examples):
        # Generate PARAPHRASE_FACTOR variations
        for _ in range(PARAPHRASE_FACTOR):
            paraphrased = create_paraphrased_example(example)
            expanded.append(paraphrased)
            paraphrased_count += 1
        
        # Progress indicator
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(original_examples)} examples...")
    
    print(f"✓ Generated {paraphrased_count} paraphrased examples")
    print(f"✓ Total after Phase 1: {len(expanded)} examples")
    
    # Save intermediate result
    save_dataset(expanded, "training_codex_phase1.jsonl")
    print(f"✓ Saved to training_codex_phase1.jsonl")
    
    return expanded

if __name__ == "__main__":
    print("\n🚀 Dataset Expansion Tool - Phase 1: Paraphrasing")
    print("=" * 70)
    
    # Check input file exists
    if not Path(INPUT_FILE).exists():
        print(f"❌ Error: {INPUT_FILE} not found!")
        exit(1)
    
    # Run Phase 1
    expanded = expand_dataset_phase1()
    
    print("\n" + "=" * 70)
    print("✅ PHASE 1 COMPLETE")
    print("=" * 70)
    print(f"Original: {len(load_dataset(INPUT_FILE))} examples")
    print(f"Expanded: {len(expanded)} examples")
    print(f"Growth: {len(expanded) / len(load_dataset(INPUT_FILE)):.1f}x")
    print()
    print("Next steps:")
    print("1. Review sample from training_codex_phase1.jsonl")
    print("2. Approve quality")
    print("3. Run Phase 2 (thematic generation)")
    print("=" * 70)
