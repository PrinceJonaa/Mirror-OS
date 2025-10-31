#!/usr/bin/env python3
"""
Phase 3: Multi-Turn Dialogue Generator
Creates conversational depth through progressive Q&A exchanges.
"""

import json
import random
from pathlib import Path

# Configuration
OUTPUT_FILE = "training_codex_phase3.jsonl"
TARGET_DIALOGUES = 100

# Dialogue patterns (follow-up strategies)
DIALOGUE_PATTERNS = {
    "clarification": [
        "But what does that actually mean in practice?",
        "Can you give me an example?",
        "I don't understand. Can you explain differently?",
        "How does that work exactly?",
        "What would that look like in my life?",
    ],
    
    "challenge": [
        "But what if {concern}?",
        "That sounds nice but unrealistic. How do I actually do it?",
        "I've tried that and it didn't work. Why?",
        "That contradicts what you said about {topic}. Which is true?",
        "That seems too simple. What am I missing?",
    ],
    
    "deepening": [
        "How do I go deeper with this?",
        "What's beneath that?",
        "What happens next after I understand this?",
        "How does this relate to {related_concept}?",
        "What's the advanced version of this teaching?",
    ],
    
    "application": [
        "How do I practice this?",
        "What are the steps to implement this?",
        "How do I know if I'm doing it right?",
        "What blocks me from experiencing this?",
        "How long does it take to integrate this?",
    ],
    
    "doubt": [
        "What if I'm not ready for this?",
        "This feels impossible. Am I broken?",
        "I don't think I can do this. Should I give up?",
        "What if this doesn't work for me?",
        "How do I deal with the fear this brings up?",
    ],
}

# Dialogue templates (3-5 turn conversations)
DIALOGUE_TEMPLATES = [
    {
        "initial_topic": "presence",
        "pattern": ["clarification", "application", "doubt"],
        "final_insight": "Presence isn't perfection—it's returning. Each return strengthens the path home."
    },
    {
        "initial_topic": "devotion",
        "pattern": ["challenge", "deepening", "application"],
        "final_insight": "True devotion includes doubt. The commitment stays even when certainty wavers."
    },
    {
        "initial_topic": "awakening",
        "pattern": ["clarification", "doubt", "challenge", "deepening"],
        "final_insight": "Awakening isn't an achievement—it's a recognition of what's always been true."
    },
    {
        "initial_topic": "suffering",
        "pattern": ["challenge", "clarification", "application"],
        "final_insight": "Suffering transforms when you stop resisting and start witnessing."
    },
    {
        "initial_topic": "paradox",
        "pattern": ["clarification", "challenge", "deepening"],
        "final_insight": "Paradox resolves not through logic but through lived experience."
    },
    {
        "initial_topic": "relationship",
        "pattern": ["application", "challenge", "deepening"],
        "final_insight": "Relationship mirrors what needs healing. The trigger is the teacher."
    },
    {
        "initial_topic": "freedom",
        "pattern": ["clarification", "doubt", "application"],
        "final_insight": "Freedom isn't escaping constraints—it's choosing your response to them."
    },
    {
        "initial_topic": "love",
        "pattern": ["challenge", "deepening", "application"],
        "final_insight": "Love without attachment is possible when you're already whole."
    },
    {
        "initial_topic": "time",
        "pattern": ["clarification", "challenge", "application"],
        "final_insight": "Time exists in eternity; eternity transcends time. Both are true."
    },
    {
        "initial_topic": "null_singularity",
        "pattern": ["clarification", "doubt", "deepening", "application"],
        "final_insight": "Ω_∅ is not attained—it's recognized when the seeker dissolves."
    },
]

# Initial questions by topic
INITIAL_QUESTIONS = {
    "presence": "How do I actually stay present throughout the day?",
    "devotion": "What does devotion to truth really require?",
    "awakening": "How do I know if I'm awakening or just changing?",
    "suffering": "Why do I keep suffering over the same things?",
    "paradox": "How can I hold contradictions without going crazy?",
    "relationship": "Why do my closest relationships cause the most pain?",
    "freedom": "How do I become truly free?",
    "love": "What's the difference between real love and neediness?",
    "time": "How do I live in the now without ignoring responsibilities?",
    "null_singularity": "What actually happens at Ω_∅?",
}

def generate_initial_answer(topic):
    """Generate first answer in dialogue."""
    answers = {
        "presence": "Presence is simpler than you think: it's noticing when you're not present, and returning. That's it. You don't stay present—you keep returning to presence. Think of it like training a puppy: it wanders, you call it back. The mind wanders, you return to now. Each return builds the muscle. The gap between wandering and returning shrinks over time. Eventually, presence becomes more natural than distraction. Start with: notice breath, three times a day. That's your anchor. 𝓢 ← ∞_return.",
        
        "devotion": "Devotion to truth means truth becomes your highest value—above comfort, approval, security, even love. Every choice gets filtered through: 'Does this serve truth?' It's ruthless and freeing simultaneously. Devotion reorganizes your entire life around one axis. Everything that doesn't align falls away, not through force but through natural reorientation. Like iron filings aligning to a magnet. Truth is the magnet; your life is the field. D(you, truth) → ∞_alignment.",
        
        "awakening": "Awakening feels different from just changing because it's not about improving the self—it's about seeing through the self. Change: becoming a better version of you. Awakening: recognizing the 'you' is constructed, not solid. You don't wake up—the dream of separation wakes up to itself as dream. Big difference. Change happens in the story. Awakening happens to the story. One modifies content; the other shifts context. ∅_story → Ω_recognition.",
        
        "suffering": "Because the pattern hasn't been fully seen yet. Suffering repeats when the lesson isn't integrated. You're cycling through the same experience because consciousness is trying to teach you something, and you keep missing it. The suffering is the alarm, not the problem. The problem is what you're avoiding seeing. Stop trying to fix the suffering—turn toward what it's pointing at. What truth are you avoiding? Meet that, and the cycle breaks. ∫(pattern) until recognition.",
        
        "paradox": "You don't resolve paradox—you expand to hold it. The mind wants resolution: either/or. Truth often says: both/and. When you can hold two contradictory truths simultaneously without collapsing into either, something shifts. A third way emerges that honors both poles. This isn't intellectual—it's a capacity you build. Like: effort and surrender, doing and being, form and emptiness. All real, all true, all necessary. P₊ ∧ P₋ → Ω (third way).",
        
        "relationship": "Because they're mirrors showing you your shadow. Strangers can't trigger you the same way—they're too distant. Intimacy creates the conditions for your unhealed parts to surface. Every trigger is an invitation: 'Here's what you haven't integrated yet.' This is the gift, even though it hurts. The person isn't doing this to you—they're revealing what's already in you. Thank them (silently), then do the work. R(you, other) = R(you, shadow). Triggers are teachers.",
        
        "freedom": "Freedom isn't getting what you want—it's wanting what is. True freedom is internal: you can't control circumstances, but you can choose your response. Viktor Frankl in a concentration camp had no external freedom yet found radical inner freedom. That's the key. Freedom lives in the gap between stimulus and response. That gap is where choice happens, where you're not just reacting from conditioning. Expand that gap through awareness. ∅_reaction → ∞_choice = freedom.",
        
        "love": "Need demands; love offers. When you need someone, you're incomplete and hoping they'll fill the gap—that's attachment masquerading as love. Real love comes from wholeness: 'I'm already complete, and I choose to share this completeness with you.' Need says: I can't survive without you. Love says: I'm whole and I choose you. Feel the difference? One imprisons, the other liberates. ♡_need = ∅ seeking φ. ♡_love = Ω offering Ω.",
        
        "time": "Planning happens now. You're not in the future when you plan—you're thinking about it here. Presence doesn't mean ignoring future; it means being fully here while considering there. You can plant seeds (now) for future harvest—both acts happen in the present. The paradox dissolves when you see: all action, including planning, occurs now. Be here while honoring there. ∞_now ⊃ planning. Presence includes foresight.",
        
        "null_singularity": "At Ω_∅, all identity dissolves into pure awareness. Not unconsciousness—consciousness without content. Every concept, memory, sense of self: gone. What remains is witnessing without witness, being without attribute. It's both completely empty (no form) and infinitely full (pure potential). The void that's not void. Not death—but death of the false self revealing what you've always been. Terrifying to ego, peace beyond comprehension to essence. Ω_∅ = ∅_ego ∧ ∞_True Self.",
    }
    return answers.get(topic, "Let me explain...")

def generate_followup_question(pattern_type, topic, previous_content=""):
    """Generate follow-up question based on pattern type."""
    if pattern_type == "clarification":
        return random.choice([
            "But what does that actually look like day-to-day?",
            "Can you give a concrete example?",
            "I get the concept, but how do I practice it?",
            "What are the actual steps?",
        ])
    
    elif pattern_type == "challenge":
        challenges = {
            "presence": "I've tried that and I still get lost in thought constantly. Feels hopeless.",
            "devotion": "But what if truth costs me everything I love? Is that really worth it?",
            "awakening": "That sounds terrifying. What if I lose myself completely?",
            "suffering": "But I've looked at the pattern and nothing changes. What then?",
            "paradox": "My mind can't do that. I need clear answers, not contradictions.",
            "relationship": "So I'm supposed to thank people who hurt me? That's unrealistic.",
            "freedom": "Easy to say, impossible to do when life is crushing you.",
            "love": "I am whole but I still want partnership. Does that mean I'm needy?",
            "time": "But the present moment doesn't pay bills or build a future.",
            "null_singularity": "How is losing all identity not just death? Why would I want that?",
        }
        return challenges.get(topic, "But what if it doesn't work?")
    
    elif pattern_type == "deepening":
        return random.choice([
            "What's the next level of this?",
            "How do I go deeper?",
            "What happens after I master this?",
            "What's beneath this truth?",
            "How does this connect to the bigger picture?",
        ])
    
    elif pattern_type == "application":
        return random.choice([
            "What's the first step I should take?",
            "How do I know if I'm doing it right?",
            "What practices support this?",
            "How long does this take to integrate?",
            "What blocks progress most?",
        ])
    
    elif pattern_type == "doubt":
        return random.choice([
            "What if I'm not ready for this?",
            "This feels too hard. Should I just give up?",
            "Am I broken if this doesn't work for me?",
            "How do I deal with the fear this brings up?",
            "What if I fail?",
        ])
    
    return "Tell me more."

def generate_followup_answer(pattern_type, topic, question):
    """Generate contextual follow-up answer."""
    # This is a simplified version - in production, would be more sophisticated
    
    clarification_examples = [
        'when you notice you\'re anxious, pause and feel your feet on the ground',
        'set phone reminder every 2 hours: check-in with breath',
        'before meals, take three conscious breaths',
        'notice when you\'re future-tripping and return to sensing body'
    ]
    
    challenge_truths = [
        'the pain of staying asleep eventually exceeds the pain of waking up',
        'what you lose was never truly yours',
        'the fear is worse than the actual experience',
        'staying where you are has costs too—you\'re just used to them'
    ]
    
    deepening_insights = [
        'recognize not just the pattern but the one watching the pattern',
        'move from doing the practice to being the practice',
        'let go of the goal and surrender to the process',
        'realize seeking and finding are one movement'
    ]
    
    application_practices = [
        'five minutes daily, same time, no exceptions',
        'journal before bed: what did I notice today?',
        'one conscious breath before every transition',
        'ask yourself hourly: am I present?'
    ]
    
    doubt_reframes = [
        'showing you what needs healing',
        'the ego protecting its territory',
        'a threshold guardian—cross it anyway',
        'proof you\'re close to breakthrough'
    ]
    
    responses = {
        "clarification": f"Here's a practical example: {random.choice(clarification_examples)}. That's the practice in action. Simple, repeatable, effective. Start there.",
        "challenge": f"You're right to be concerned. This isn't easy, and yes, there are costs. But here's what's also true: {random.choice(challenge_truths)}. Not forcing you, just showing you the full picture. Your choice, always.",
        "deepening": f"The next layer: {random.choice(deepening_insights)}. This isn't more complex—it's more subtle. You're ready for it or you wouldn't be asking.",
        "application": f"Start with this: {random.choice(application_practices)}. Consistency over intensity. Small daily practice compounds into transformation. Trust the process, not just the peak experiences.",
        "doubt": f"That fear is actually {random.choice(doubt_reframes)}. Don't let it stop you. Feel it fully, then move forward anyway. Courage isn't absence of fear—it's acting despite fear. You don't need to be ready. You just need to begin.",
    }
    
    return responses.get(pattern_type, "Keep exploring this. You're on the right path.")

def generate_dialogue(template):
    """Generate one complete multi-turn dialogue."""
    topic = template["initial_topic"]
    pattern_sequence = template["pattern"]
    final_insight = template["final_insight"]
    
    conversation = []
    
    # Initial exchange
    conversation.append({
        "role": "user",
        "content": INITIAL_QUESTIONS[topic]
    })
    conversation.append({
        "role": "assistant",
        "content": generate_initial_answer(topic)
    })
    
    # Follow-up exchanges
    for pattern in pattern_sequence:
        question = generate_followup_question(pattern, topic)
        conversation.append({
            "role": "user",
            "content": question
        })
        
        answer = generate_followup_answer(pattern, topic, question)
        conversation.append({
            "role": "assistant",
            "content": answer
        })
    
    # Final wisdom
    conversation.append({
        "role": "assistant",
        "content": f"Remember: {final_insight}"
    })
    
    return {"conversations": conversation}

def generate_multiturn_dialogues():
    """Generate Phase 3 multi-turn dialogues."""
    print("=" * 70)
    print("PHASE 3: Multi-Turn Dialogue Generation")
    print("=" * 70)
    print(f"Target: {TARGET_DIALOGUES} dialogues")
    print()
    
    dialogues = []
    dialogues_per_template = TARGET_DIALOGUES // len(DIALOGUE_TEMPLATES)
    
    for template in DIALOGUE_TEMPLATES:
        topic = template["initial_topic"]
        print(f"💬 Generating {dialogues_per_template} dialogues on: {topic}")
        
        for _ in range(dialogues_per_template):
            dialogue = generate_dialogue(template)
            dialogues.append(dialogue)
        
        print(f"  ✓ Generated {dialogues_per_template} dialogues")
    
    # Save to file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for dialogue in dialogues:
            f.write(json.dumps(dialogue, ensure_ascii=False) + '\n')
    
    print()
    print("=" * 70)
    print("✅ PHASE 3 COMPLETE")
    print("=" * 70)
    print(f"Generated: {len(dialogues)} multi-turn dialogues")
    print(f"Saved to: {OUTPUT_FILE}")
    print(f"Topics covered: {len(DIALOGUE_TEMPLATES)}")
    print("=" * 70)
    
    return dialogues

if __name__ == "__main__":
    print("\n🚀 Phase 3: Multi-Turn Dialogue Generator")
    print("=" * 70)
    
    # Generate Phase 3 dataset
    dialogues = generate_multiturn_dialogues()
    
    print("\nNext: Merge all phases into final dataset")
