#!/usr/bin/env python3
"""
Phase 2: Thematic Expansion Generator
Generates 500-1000 new Q&As across core themes in Style B.
"""

import json
import random
from pathlib import Path

# Configuration
OUTPUT_FILE = "training_codex_phase2.jsonl"
TARGET_COUNT = 800  # Adjust as needed (500-1000 range)

# Core themes from your framework
THEMES = {
    "devotion": [
        "What happens when devotion is tested by loss?",
        "How does devotion differ from dependency?",
        "Can devotion exist without an object?",
        "What is the relationship between devotion and freedom?",
        "How do I deepen my devotion?",
        "What role does devotion play in awakening?",
        "How does devotion transform suffering?",
        "What is devotional surrender?",
        "How do I know if my devotion is authentic?",
        "What happens when two devotions conflict?",
    ],
    
    "presence": [
        "How do I stay present during emotional pain?",
        "What's the relationship between presence and joy?",
        "Can I be present and still plan ahead?",
        "How does presence relate to productivity?",
        "What blocks presence most?",
        "How do I bring presence into relationships?",
        "What's the difference between awareness and presence?",
        "How does presence heal trauma?",
        "Can presence be cultivated or only revealed?",
        "What is effortless presence?",
    ],
    
    "paradox": [
        "How can I act without attachment to outcomes?",
        "What does it mean to be in the world but not of it?",
        "How can effort and effortlessness coexist?",
        "What's the paradox of seeking enlightenment?",
        "How can I change while accepting what is?",
        "What does it mean to hold paradox without resolving it?",
        "How is the path both necessary and illusory?",
        "What's the paradox of spiritual practice?",
        "How can I be complete yet always becoming?",
        "What's the relationship between doing and being?",
    ],
    
    "relationship": [
        "How do I love without losing myself?",
        "What is conscious partnership?",
        "How do relationships serve awakening?",
        "What's the difference between codependence and devotion in relationship?",
        "How do I navigate conflict consciously?",
        "What is sacred intimacy?",
        "How do I know when to stay vs leave a relationship?",
        "What role does vulnerability play in connection?",
        "How do I maintain sovereignty in relationship?",
        "What is the purpose of romantic relationship?",
    ],
    
    "awakening": [
        "What are the stages of awakening?",
        "How do I integrate awakening experiences?",
        "What's the dark night of the soul?",
        "How do I know if I'm awakening or just changing?",
        "What happens after initial awakening?",
        "How does awakening affect daily life?",
        "What is spiritual bypassing?",
        "How do I stay grounded while awakening?",
        "What role does the body play in awakening?",
        "Can awakening be lost?",
    ],
    
    "suffering": [
        "How do I transform suffering into wisdom?",
        "What's the difference between pain and suffering?",
        "How does resistance create suffering?",
        "What is the gift in suffering?",
        "How do I be with suffering without being consumed?",
        "What role does acceptance play in ending suffering?",
        "How does suffering relate to karma?",
        "What is redemptive suffering?",
        "How do I help others who are suffering?",
        "What is the relationship between suffering and compassion?",
    ],
    
    "freedom": [
        "What is true freedom?",
        "How does discipline create freedom?",
        "What's the relationship between freedom and responsibility?",
        "How do I free myself from conditioning?",
        "What is freedom from the known?",
        "How does freedom relate to choice?",
        "What is spiritual freedom?",
        "How do I find freedom in limitation?",
        "What blocks freedom?",
        "How is freedom different from license?",
    ],
    
    "time": [
        "How do I live in the now while honoring the past?",
        "What is cyclical time vs linear time?",
        "How does presence relate to memory?",
        "What is timeless awareness?",
        "How do I heal time (past wounds)?",
        "What is the relationship between becoming and being?",
        "How does time healing work?",
        "What is sacred timing?",
        "How do I trust divine timing?",
        "What happens to time in deep presence?",
    ],
    
    "love": [
        "What is unconditional love?",
        "How does love differ from attachment?",
        "What is self-love vs self-indulgence?",
        "How does love transform fear?",
        "What is the highest love?",
        "How do I love what I judge?",
        "What is love as recognition?",
        "How does love relate to truth?",
        "What is fierce love?",
        "How do I become love rather than seek it?",
    ],
    
    "null_singularity": [
        "What practices lead to Ω_∅?",
        "How long does the Ω_∅ state last?",
        "What is the fear of Ω_∅?",
        "How is Ω_∅ different from dissociation?",
        "What comes after touching Ω_∅?",
        "How does Ω_∅ relate to the void?",
        "What is the relationship between Ω_∅ and pure awareness?",
        "Can Ω_∅ be permanent?",
        "How does Ω_∅ transform perception?",
        "What is the gateway to Ω_∅?",
    ],
}

# Answer templates with Style B structure (narrative + symbols)
ANSWER_STRUCTURES = [
    # Structure 1: Definition → Explanation → Example → Symbol
    lambda concept, detail1, detail2, symbol: f"{concept} means {detail1}. Think of it like this: {detail2}. When you truly understand this, everything shifts. The key is recognizing that {detail1} isn't just theory—it's lived reality. {symbol}",
    
    # Structure 2: Question back → Exploration → Resolution → Symbol
    lambda concept, detail1, detail2, symbol: f"Ask yourself: what would happen if {detail1}? Most people avoid this question because {detail2}. But facing it directly reveals the truth: {concept} isn't what you think it is. It's actually the doorway to freedom. {symbol}",
    
    # Structure 3: Paradox → Hold → Insight → Symbol
    lambda concept, detail1, detail2, symbol: f"Here's the paradox: {detail1} and {detail2} are both true. You can't resolve this intellectually—you have to live it. When you stop trying to choose one side, {concept} reveals itself as the third way. Not either/or, but both/and. {symbol}",
    
    # Structure 4: Direct → Expand → Practice → Symbol
    lambda concept, detail1, detail2, symbol: f"{concept}. That's the simple truth. But living it requires {detail1}. Start by noticing {detail2} in your daily life. Each time you catch it, you're building new neural pathways. This isn't fast, but it's real. {symbol}",
    
    # Structure 5: Metaphor → Unpack → Apply → Symbol
    lambda concept, detail1, detail2, symbol: f"Imagine {detail1}. That's what {concept} is like. Just as {detail2}, so too does this truth operate in your life. You've probably experienced it without naming it. Recognition is the first step. {symbol}",
]

def generate_answer_styleb(question, theme):
    """Generate Style B answer (narrative + symbols) for a question."""
    
    # Theme-specific answer components
    components = {
        "devotion": {
            "concepts": ["total orientation", "single-pointed focus", "unified commitment", "sacred alignment"],
            "details1": ["choosing one axis and letting everything else orbit it", "collapsing all motivations into one central truth", "making every choice serve the chosen commitment"],
            "details2": ["relationships naturally reorganize around it", "what doesn't serve it falls away organically", "resistance emerges and must be met with presence"],
            "symbols": ["D(x, Ω) = ∞_alignment", "∀R → 𝓢", "devotion = ∅_distraction", "D ⊃ all relations"],
        },
        
        "presence": {
            "concepts": ["being here completely", "consciousness without escape", "awareness anchored in now", "stillness amid motion"],
            "details1": ["dropping the stories about this moment", "feeling everything without resistance", "meeting reality as-is without buffer"],
            "details2": ["thoughts arise but don't sweep you away", "you notice the gap between stimulus and response", "each breath becomes a return to source"],
            "symbols": ["𝓢 = ∞_now", "presence → ∅_escape", "∂(awareness)/∂t = 0", "𝓢 ⊃ all experience"],
        },
        
        "paradox": {
            "concepts": ["holding opposites", "third-way emergence", "both/and thinking", "transcending duality"],
            "details1": ["refusing to collapse into either pole", "staying in the tension without resolution", "allowing contradiction to coexist"],
            "details2": ["the mind wants resolution but truth wants fullness", "synthesis emerges from sustained holding", "the answer appears when you stop demanding one"],
            "symbols": ["P₊ ∧ P₋ → Ω", "paradox = gateway", "∅_resolution = ∞_truth", "⊕ (paradox held)"],
        },
        
        "relationship": {
            "concepts": ["mirror recognition", "mutual awakening", "sacred encounter", "wholeness meeting wholeness"],
            "details1": ["seeing yourself reflected in the other", "using relationship as spiritual practice", "honoring both sovereignty and union"],
            "details2": ["triggers reveal unintegrated shadow", "intimacy creates conditions for growth", "two wholes choosing to dance together"],
            "symbols": ["R(Ω, Ω) = mirror", "∂(self) through other", "R = mutual recognition", "♡ = Ω seeing Ω"],
        },
        
        "awakening": {
            "concepts": ["recognition of true nature", "ego dissolution", "identity collapse", "return to source"],
            "details1": ["seeing through the illusion of separation", "recognizing you're awareness not content", "the falling away of false self"],
            "details2": ["it's both terrifying and liberating", "everything you thought you were dissolves", "what remains is what you've always been"],
            "symbols": ["Ω_recognition", "∅_ego → ∞_Self", "awakening = remembering", "Φ → Ω"],
        },
        
        "suffering": {
            "concepts": ["resistance to what is", "teacher in disguise", "invitation to presence", "transformer of consciousness"],
            "details1": ["meeting pain without creating story", "feeling fully without identifying", "accepting what cannot be changed"],
            "details2": ["pain is sensation, suffering is resistance", "what you resist persists", "acceptance transforms without changing circumstances"],
            "symbols": ["suffering = resistance × pain", "acceptance → ∅_suffering", "∫(pain)·(1-resistance) = growth", "𝓢 ⊃ pain"],
        },
        
        "freedom": {
            "concepts": ["inner liberation", "choice beyond conditioning", "sovereignty of being", "unconditioned response"],
            "details1": ["recognizing you're not your programming", "responding rather than reacting", "choosing from presence not pattern"],
            "details2": ["circumstances may be fixed but your relationship to them isn't", "freedom lives in the gap between stimulus and response", "liberation from the known"],
            "symbols": ["freedom = ∅_conditioning", "Ω ∧ ∅_pattern", "choice ← 𝓢", "liberation = ∞_possibility"],
        },
        
        "time": {
            "concepts": ["eternal now", "timeless presence", "cyclical return", "duration vs eternity"],
            "details1": ["dropping into the gap between past and future", "recognizing now as the only reality", "experiencing eternity in the present"],
            "details2": ["time is measurement, eternity is being", "past and future exist as thoughts arising now", "the timeless contains all time"],
            "symbols": ["∞_now ⊃ all time", "eternity = ∅_time", "present = portal", "𝓢 = timeless"],
        },
        
        "love": {
            "concepts": ["recognition of unity", "seeing self in other", "essence connection", "unconditional acceptance"],
            "details1": ["dissolving boundaries while honoring distinction", "extending wholeness rather than seeking completion", "allowing without possessing"],
            "details2": ["attachment grasps, love releases", "need demands, love offers", "fear contracts, love expands"],
            "symbols": ["♡ = Ω recognizing Ω", "love = ∅_separation", "∞_acceptance", "♡ ⊃ all forms"],
        },
        
        "null_singularity": {
            "concepts": ["complete dissolution", "consciousness without content", "void that's not empty", "ground of being"],
            "details1": ["all identity collapsing into pure awareness", "the state before any arising", "witnessing without witness"],
            "details2": ["not unconsciousness but awareness without object", "terrifying to ego, peaceful to essence", "death of everything yet more alive than ever"],
            "symbols": ["Ω_∅ = ∅_form ∧ ∞_potential", "pure being", "∅_I → Ω", "singularity of awareness"],
        },
    }
    
    theme_data = components.get(theme, components["presence"])  # Default to presence
    
    # Randomly select components
    concept = random.choice(theme_data["concepts"])
    detail1 = random.choice(theme_data["details1"])
    detail2 = random.choice(theme_data["details2"])
    symbol = random.choice(theme_data["symbols"])
    
    # Select structure
    structure = random.choice(ANSWER_STRUCTURES)
    
    # Generate answer
    answer = structure(concept, detail1, detail2, symbol)
    
    return answer

def generate_thematic_dataset():
    """Generate Phase 2 thematic Q&As."""
    print("=" * 70)
    print("PHASE 2: Thematic Expansion Generation")
    print("=" * 70)
    print(f"Target: {TARGET_COUNT} new Q&As")
    print()
    
    examples = []
    questions_per_theme = TARGET_COUNT // len(THEMES)
    
    for theme, base_questions in THEMES.items():
        print(f"🔮 Generating {questions_per_theme} Q&As for theme: {theme}")
        
        theme_count = 0
        while theme_count < questions_per_theme:
            # Select random question from theme
            question = random.choice(base_questions)
            
            # Generate Style B answer
            answer = generate_answer_styleb(question, theme)
            
            # Create conversation
            example = {
                "conversations": [
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": answer}
                ]
            }
            
            examples.append(example)
            theme_count += 1
        
        print(f"  ✓ Generated {theme_count} examples for {theme}")
    
    # Save to file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')
    
    print()
    print("=" * 70)
    print("✅ PHASE 2 COMPLETE")
    print("=" * 70)
    print(f"Generated: {len(examples)} thematic Q&As")
    print(f"Saved to: {OUTPUT_FILE}")
    print(f"Themes covered: {len(THEMES)}")
    print("=" * 70)
    
    return examples

if __name__ == "__main__":
    print("\n🚀 Phase 2: Thematic Expansion Generator")
    print("=" * 70)
    
    # Generate Phase 2 dataset
    examples = generate_thematic_dataset()
    
    print("\nNext: Run Phase 3 (multi-turn dialogues)")
    print("Then: Merge all phases into final expanded dataset")
