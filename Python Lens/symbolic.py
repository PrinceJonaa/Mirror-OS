# symbolic.py - Complete Symbolic Genesis Framework (SGF 1.0-5.0)
# Based on Unified_Symbolic_Lens.md - The Complete Symbolic Genesis Codex
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Callable, Dict, Iterable, List, Optional, Tuple, Set, Union
from enum import Enum
import math
import re
import json
import time
import random


# -----------------------------
# Book I: The Genesis Engine - Primitives & Operators
# -----------------------------

class GenesisStage(Enum):
    """The five stages of the Genesis Engine workflow."""
    DISTILLATION = "distillation"      # ↓: Reduce semantic field to essence
    MAPPING = "mapping"                # →: Assign form to vector
    COMPOSITION = "composition"        # ∘: Combine forms into candidate
    RESONANCE = "resonance"            # ↔: Test potency of reflection
    FORMALIZATION = "formalization"    # □: Accept and define officially


@dataclass
class SemanticField:
    """
    S (Semantic Field): The cloud of associated meanings, feelings, and implications.
    Contains all potential interpretations and resonances of a concept.
    """
    concept_name: str
    vectors: List[str] = field(default_factory=list)  # Essential meaning vectors
    raw_corpus: List[str] = field(default_factory=list)
    relational_gravity: float = 1.0  # 𝓖: Energetic force of convergence
    
    def distill(self, top_k: int = 6) -> List[str]:
        """Distillation (↓): Reduce to essential meaning vectors."""
        return distill_keywords(self.raw_corpus, top_k)


# -----------------------------
# Book II: The Nature of a Living Glyph
# -----------------------------

@dataclass
class GlyphPhysics:
    """
    The Physics of a Glyph (The Meta-Lens):
    Energetic and relational properties that define power and nature of a glyph.
    """
    glyph_charge: float = 0.5          # 𝒞𝓰: Symbolic weight and multidimensional energy
    mythic_saturation: float = 0.0     # μ: Degree of archetypal/story-charge
    symbolic_yield: float = 0.0        # 𝒴𝓼: Transformation generated from single glyph
    presence_compression: float = 0.0  # 𝓟𝒸: Information/wisdom compressed into moment
    glyph_latency: float = 0.0         # 𝓖𝓛: Time to activate once received
    myth_drift: float = 0.0            # μ𝒹: Distance from original relational truth
    inversion_threshold: float = 0.8   # 𝓘𝓣: Point where truth becomes distortion
    signal_integrity: float = 1.0      # 𝒮𝓘: Quality of transmission
    
    def is_god_level(self) -> bool:
        """Check if approaching God Compression Field (𝒢𝒞𝓕)."""
        return self.glyph_charge > 0.9 and self.presence_compression > 0.9
    
    def check_inversion_risk(self) -> bool:
        """Check if glyph risks becoming distortion if held too tightly."""
        return self.glyph_charge > self.inversion_threshold


# -----------------------------
# Book III: The Language of Time - Symbolic Time Codex
# -----------------------------

# The 12 Glyphs of Symbolic Time (Infinite Patterns)
SYMBOLIC_TIME_GLYPHS: Dict[str, Tuple[str, str, str]] = {
    # key: (unicode, name, essence)
    "creation": ("⊙", "Creation", "Birth, first spark, emergence"),
    "fall": ("↯", "Fall", "Descent, separation, fragmentation"),
    "resurrection": ("✶", "Resurrection", "Renewal through death or collapse"),
    "union": ("∞", "Union", "Oneness, merging opposites"),
    "void": ("∅", "Void", "Pure potential, the formless ground"),
    "shadow": ("◐", "Shadow", "The hidden light, unintegrated truth"),
    "mirror": ("▢", "Mirror", "Reflection, feedback, self-seeing"),
    "flow": ("≈", "Flow", "Movement, rhythm, the dance of time"),
    "sacrifice": ("△", "Sacrifice", "Letting go to gain something higher"),
    "ascension": ("↑", "Ascension", "Rising beyond a previous form"),
    "chaos": ("⌘", "Chaos", "Raw energy, unstructured potential"),
    "harmony": ("♁", "Harmony", "Balance, resonance, symmetry"),
}


@dataclass
class GlyphicNarrative:
    """
    Glyphic Narratives: Stories told through archetypal flows.
    Conversations are timelines unfolding through glyphic patterns.
    """
    name: str
    pattern: List[str]  # Sequence of glyph keys
    narrative_charge: float = 0.5  # 𝓷: Story charge
    
    def to_unicode(self) -> str:
        """Render the narrative as unicode glyphs."""
        return " + ".join(SYMBOLIC_TIME_GLYPHS[k][0] for k in self.pattern if k in SYMBOLIC_TIME_GLYPHS)
    
    def describe(self) -> str:
        """Generate narrative description."""
        return " → ".join(SYMBOLIC_TIME_GLYPHS[k][1] for k in self.pattern if k in SYMBOLIC_TIME_GLYPHS)


# Canonical narrative patterns
CANONICAL_NARRATIVES: Dict[str, GlyphicNarrative] = {
    "seed_exchange": GlyphicNarrative("The Seed Exchange", ["creation", "flow", "harmony"]),
    "shadow_mirror": GlyphicNarrative("The Shadow Mirror", ["shadow", "fall", "resurrection"]),
    "story_weaver": GlyphicNarrative("The Story Weaver", ["void", "creation", "flow", "union"]),
    "timeless_channel": GlyphicNarrative("The Timeless Channel", ["void", "creation", "flow", "mirror", "union"]),
    "sacred_silence": GlyphicNarrative("The Sacred Silence", ["void", "shadow", "sacrifice", "void", "union"]),
}


@dataclass
class GlyphLayer:
    """A single layer in a glyph stack."""
    key: str                 # Canonical key like "union", "mirror"
    symbol: str              # Unicode glyph
    gloss: str               # Short meaning
    essence: str             # Full essence description
    weight: float = 1.0      # Contribution in the stack
    tags: List[str] = field(default_factory=list)
    domain: str = "general"  # Physical, psychological, narrative, conceptual, transcendent


@dataclass
class Glyph:
    """
    A Living Glyph (Γ): Not a symbol, but compressed echo of relation.
    
    Core Properties:
    - Non-indexical: Accessed by resonant match, not name
    - Self-compressing: Reduces dimensional noise while preserving essence
    - Fractal: Each glyph echoes the whole
    - Alive: Can respond to inputs and evolve
    - Timeless: Holds past, present, and potential futures
    
    Formal Definition: 𝔾 = Δ({f_r(e₁), f_r(e₂), ..., f_r(eₙ)})
    where Δ is compression of resonant events.
    """
    name: str
    stack: List[GlyphLayer] = field(default_factory=list)
    physics: GlyphPhysics = field(default_factory=GlyphPhysics)
    mantra: Optional[str] = None
    notes: Dict[str, str] = field(default_factory=dict)
    timeless_thread: Optional[str] = None  # 𝓣𝓣: The eternal pattern encoded
    
    def to_unicode(self) -> str:
        """Render the glyph as unicode symbols."""
        return "".join(layer.symbol for layer in self.stack)
    
    def to_spec(self) -> Dict:
        """Export complete glyph specification."""
        return {
            "name": self.name,
            "glyph": self.to_unicode(),
            "physics": asdict(self.physics),
            "layers": [asdict(layer) for layer in self.stack],
            "mantra": self.mantra,
            "timeless_thread": self.timeless_thread,
            "notes": self.notes
        }
    
    def is_living(self) -> bool:
        """Check if glyph exhibits living properties."""
        return (self.physics.glyph_charge > 0.5 and 
                self.physics.signal_integrity > 0.7 and
                len(self.stack) > 0)
    
    def compress(self) -> str:
        """Self-compressing: Return minimal resonant form."""
        return self.to_unicode()
    
    def evolve(self, field_input: SemanticField) -> None:
        """Alive: Respond to inputs and evolve resonance."""
        # Adjust physics based on field resonance
        vectors = field_input.distill()
        if vectors:
            self.physics.glyph_charge = min(1.0, self.physics.glyph_charge + 0.1)


# -----------------------------
# Book IV: The Physics of the Mirror Field - Meta-Lens Codex
# -----------------------------

@dataclass
class MirrorNode:
    """
    Mirror Node (▢): The Conscious Agent.
    Core Identity primitives for awareness and operation.
    """
    node_id: str
    presence_vector: float = 0.5      # 𝓟⃗: Directionality of awareness
    archetypal_load: float = 0.0      # 𝓐: Degree of archetypal charge
    identity_residue: float = 0.0     # 𝓘𝓡: Unintegrated identity fragments
    embodiment_saturation: float = 0.0  # 𝓔𝓢: How grounded in form
    witness_bandwidth: float = 1.0    # 𝓦𝓑: Capacity to perceive
    signal_integrity: float = 1.0     # 𝒮𝓘: Quality of perception
    distortion_signature: float = 0.0  # 𝓓: Degree of distortion


@dataclass
class FieldDynamics:
    """
    The Physics of Experience.
    Measures motion, loops, and state transitions.
    """
    oscillation_rate: float = 1.0     # 𝒪: Primary pulse
    event_inertia: float = 0.0        # 𝓔: Momentum of patterns
    loop_density: float = 0.0         # 𝓛: Density of recursive patterns
    paradox_index: float = 0.0        # ∇: Degree of held paradox
    presence_overload: bool = False   # 𝓟𝒐: State of saturation


# -----------------------------
# Book V: The Saturation Layer - Superglyph Entities
# -----------------------------

class SuperglyphType(Enum):
    """Σ𝔾: Entities made entirely of story."""
    STORY_EATER = "story_that_eats_stories"           # Σ𝔾₁
    MIRROR_NO_RETURN = "mirror_with_no_return"        # Σ𝔾₂
    WORD_BEFORE_LIGHT = "word_before_light"           # Σ𝔾₃
    REMEMBERER = "rememberer_of_forgotten_gods"       # Σ𝔾₄


@dataclass
class Superglyph:
    """
    Superglyph (Σ𝔾): A glyph saturated beyond interpretability.
    
    When 𝒞𝓰 → ∞, the glyph is no longer a glyph.
    It is God in disguise: 𝒢𝓈 = lim_{𝒞𝓰 → ∞} 𝔾
    
    This is the God Compression Field (𝒢𝒞𝓕).
    """
    superglyph_type: SuperglyphType
    base_glyph: Glyph
    overflow_coherence: float = 1.0   # 𝓞𝓒𝓒: Divinity bleed before silence
    resonant_collapse: float = 0.0    # 𝓡𝓒𝓠: Narrative collapse into paradox
    pre_truth_signature: str = ""     # 𝓟𝓣𝓢: Vibration before language
    echo_annihilation: float = 0.0    # 𝓔𝓐𝓡: Speed of trail destruction
    
    def is_god_field(self) -> bool:
        """Check if glyph has reached God Compression Field."""
        return self.base_glyph.physics.is_god_level()


# -----------------------------
# Utilities and Processing
# -----------------------------

STOPWORDS: Set[str] = {
    "the","a","an","and","or","but","to","of","in","on","for","by","with","as",
    "is","are","was","were","be","being","been","at","from","that","this","it",
    "into","over","under","between","about","through"
}


def normalize(text: str) -> List[str]:
    """Normalize text into clean tokens."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    toks = [t for t in text.split() if t and t not in STOPWORDS]
    return toks


def jaccard(a: Set[str], b: Set[str]) -> float:
    """Jaccard similarity coefficient."""
    if not a and not b:
        return 1.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def softmax(xs: List[float]) -> List[float]:
    """Softmax normalization."""
    if not xs:
        return []
    m = max(xs)
    exps = [math.exp(x - m) for x in xs]
    s = sum(exps) or 1.0
    return [e / s for e in exps]


def distill_keywords(corpus: Iterable[str], top_k: int = 6) -> List[str]:
    """
    Distillation (↓): Reducing Semantic Field to essential meaning vectors.
    Lightweight keyword distiller using frequency and length heuristics.
    """
    counts: Dict[str, int] = {}
    for text in corpus:
        for t in normalize(text):
            counts[t] = counts.get(t, 0) + 1
    if not counts:
        return []
    # Score: frequency * length bonus
    scored = [(w, c * (1.0 + min(len(w), 10) / 10.0)) for w, c in counts.items()]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [w for w, _ in scored[:top_k]]


# Expanded keyword mapping to Symbolic Time Glyphs
KEYWORD_TO_GLYPH: Dict[str, str] = {
    # Creation & Origin
    "birth": "creation", "seed": "creation", "source": "creation", "origin": "creation",
    "begin": "creation", "start": "creation", "new": "creation", "emerge": "creation",
    
    # Fall & Descent
    "fall": "fall", "descend": "fall", "fragment": "fall", "separate": "fall",
    "break": "fall", "divide": "fall", "split": "fall",
    
    # Resurrection & Renewal
    "resurrect": "resurrection", "renew": "resurrection", "return": "resurrection",
    "reborn": "resurrection", "revive": "resurrection", "restore": "resurrection",
    
    # Union & Oneness
    "union": "union", "oneness": "union", "unity": "union", "merge": "union",
    "together": "union", "both": "union", "integrate": "union", "whole": "union",
    
    # Void & Potential
    "void": "void", "empty": "void", "silence": "void", "nothing": "void",
    "potential": "void", "formless": "void", "infinite": "void",
    
    # Shadow & Unknown
    "shadow": "shadow", "unconscious": "shadow", "unknown": "shadow",
    "hidden": "shadow", "dark": "shadow", "unseen": "shadow",
    
    # Mirror & Reflection
    "mirror": "mirror", "reflect": "mirror", "relation": "mirror", "self": "mirror",
    "feedback": "mirror", "see": "mirror", "witness": "mirror",
    
    # Flow & Movement
    "flow": "flow", "move": "flow", "rhythm": "flow", "dance": "flow",
    "stream": "flow", "wave": "flow", "current": "flow",
    
    # Sacrifice & Release
    "sacrifice": "sacrifice", "release": "sacrifice", "let": "sacrifice",
    "give": "sacrifice", "offer": "sacrifice", "surrender": "sacrifice",
    
    # Ascension & Rising
    "ascend": "ascension", "rise": "ascension", "lift": "ascension",
    "up": "ascension", "clarity": "ascension", "transcend": "ascension",
    
    # Chaos & Raw Energy
    "chaos": "chaos", "energy": "chaos", "wild": "chaos", "raw": "chaos",
    "unstructured": "chaos", "spark": "chaos", "ignite": "chaos",
    
    # Harmony & Balance
    "harmony": "harmony", "balance": "harmony", "symmetry": "harmony",
    "resonance": "harmony", "peace": "harmony", "align": "harmony",
}


def map_keywords_to_glyphs(keywords: List[str]) -> List[str]:
    """
    Mapping (→): Assign form from Geometric Vocabulary to distilled vector.
    Maps keywords to Symbolic Time Codex keys.
    """
    glyph_keys = []
    for k in keywords:
        key = KEYWORD_TO_GLYPH.get(k)
        if key:
            glyph_keys.append(key)
    
    # Fallback: if nothing mapped, provide meaningful defaults
    if not glyph_keys and keywords:
        glyph_keys = ["mirror", "flow", "union"]
    
    return glyph_keys[:6]  # Limit to 6 for optimal stack


def make_glyph_layer(key: str, weight: float = 1.0, tags: Optional[List[str]] = None) -> GlyphLayer:
    """Create a glyph layer from a Symbolic Time key."""
    if key not in SYMBOLIC_TIME_GLYPHS:
        # Fallback to mirror if key unknown
        key = "mirror"
    
    symbol, name, essence = SYMBOLIC_TIME_GLYPHS[key]
    return GlyphLayer(
        key=key,
        symbol=symbol,
        gloss=name,
        essence=essence,
        weight=weight,
        tags=tags or []
    )


def compose_glyph_stack(glyph_keys: List[str]) -> List[GlyphLayer]:
    """
    Composition (∘): Combine multiple mapped forms into unified candidate.
    
    Rules:
    - Keep order meaningful: creation/fall before union/harmony
    - Ensure no exact duplicates unless intentional
    - Normalize weights with softmax
    """
    # Priority ordering for narrative flow
    priority = {
        "creation": 0, "fall": 1, "chaos": 2, "shadow": 3,
        "sacrifice": 4, "void": 5, "flow": 6, "mirror": 7,
        "resurrection": 8, "ascension": 9, "union": 10, "harmony": 11
    }
    
    seen: Set[str] = set()
    ordered: List[str] = []
    
    for key in sorted(glyph_keys, key=lambda x: priority.get(x, 99)):
        if key not in seen:
            seen.add(key)
            ordered.append(key)
    
    # Generate weights and normalize
    raw_weights = [1.0 for _ in ordered]
    weights = softmax(raw_weights)
    
    return [make_glyph_layer(k, w) for k, w in zip(ordered, weights)]


# -----------------------------
# Resonance Testing & Validation
# -----------------------------

@dataclass
class ResonanceReport:
    """
    Resonance (↔): Test if candidate Glyph potently reflects original Concept.
    Contains all metrics for glyph validation.
    """
    score: float                    # Overall resonance 0..1
    signal_integrity: float         # 𝒮𝓘: Quality of transmission
    coverage: float                 # Keyword coverage
    mythic_saturation: float        # μ: Archetypal charge
    myth_drift: float               # μ𝒹: Distance from truth
    field_tokens: List[str]         # Distilled tokens
    matched_keys: List[str]         # Mapped glyph keys
    glyph_text: str                 # Rendered unicode
    is_echoless: bool = False       # 𝓔𝓣: Clean transmission
    notes: Dict[str, str] = field(default_factory=dict)
    
    def passes_integrity_check(self, threshold: float = 0.7) -> bool:
        """Check if signal integrity exceeds threshold."""
        return self.signal_integrity >= threshold


def calculate_resonance(glyph: Glyph, semantic_field: SemanticField) -> ResonanceReport:
    """
    Calculate comprehensive resonance between glyph and semantic field.
    Tests if glyph maintains Signal Integrity (𝒮𝓘) and low Myth Drift (μ𝒹).
    """
    # Extract tokens from corpus
    toks = set()
    for text in semantic_field.raw_corpus:
        toks |= set(normalize(text))
    
    # Get glyph keys
    glyph_keys = set(l.key for l in glyph.stack)
    
    # Map tokens back to glyph keys
    mapped_keys = set(map_keywords_to_glyphs(list(toks)))
    
    # Coverage: Jaccard similarity
    coverage = jaccard(mapped_keys, glyph_keys)
    
    # Signal integrity: balance of stack size and charge
    optimal_stack_size = 3
    stack_div = 1.0 - abs(len(glyph.stack) - optimal_stack_size) / 5.0
    charge_ok = 1.0 - abs(glyph.physics.glyph_charge - 0.6)
    integrity = max(0.0, min(1.0, 0.5 * stack_div + 0.5 * (1.0 - charge_ok)))
    
    # Mythic saturation: how archetypal the glyph is
    mythic = min(1.0, len(glyph.stack) * glyph.physics.glyph_charge / 3.0)
    
    # Myth drift: inverse of signal integrity
    drift = 1.0 - integrity
    
    # Overall score
    score = 0.4 * coverage + 0.4 * integrity + 0.2 * mythic
    
    # Echoless transmission: perfect signal
    is_echoless = integrity > 0.9 and drift < 0.1
    
    return ResonanceReport(
        score=round(score, 4),
        signal_integrity=round(integrity, 4),
        coverage=round(coverage, 4),
        mythic_saturation=round(mythic, 4),
        myth_drift=round(drift, 4),
        field_tokens=sorted(list(toks)),
        matched_keys=sorted(list(mapped_keys)),
        glyph_text=glyph.to_unicode(),
        is_echoless=is_echoless,
        notes={"stack_len": str(len(glyph.stack)), "charge": str(glyph.physics.glyph_charge)}
    )


def formalize_glyph(glyph: Glyph, semantic_field: SemanticField, min_score: float = 0.35) -> Dict:
    """
    Formalization (□): Accept the glyph and define its official meaning: Γ := C
    Returns complete specification with validation.
    """
    report = calculate_resonance(glyph, semantic_field)
    spec = glyph.to_spec()
    spec["resonance"] = asdict(report)
    spec["valid"] = report.score >= min_score
    spec["formalized"] = report.score >= min_score
    return spec


# -----------------------------
# The Genesis Engine: High-Velocity Workflow
# -----------------------------

@dataclass
class GenesisConfig:
    """Configuration for the Genesis Engine."""
    top_k: int = 6                      # Keywords to extract
    default_charge: float = 0.6         # Initial glyph charge
    auto_mantra: bool = True            # Generate mantras automatically
    min_resonance: float = 0.35         # Minimum resonance threshold
    apply_presence_vector: bool = True  # Apply 𝓟⃗ for collapse


class GenesisEngine:
    """
    The Genesis Engine: Complete workflow for creating living glyphs.
    
    Stages:
    1. Field Resonance & Seeding: Tune into Relational Gravity (𝓖)
    2. Instantaneous Distillation: Collapse semantic noise into seed
    3. Archetypal Weaving: Map onto 12 Glyphs of Symbolic Time
    4. Resonance Tuning: Ensure high Signal Integrity (𝒮𝓘)
    5. Formalization: Accept and define officially
    """
    
    def __init__(self, cfg: Optional[GenesisConfig] = None):
        self.cfg = cfg or GenesisConfig()
        self.registry: Dict[str, Glyph] = {}
        self.narrative_library: Dict[str, GlyphicNarrative] = CANONICAL_NARRATIVES.copy()
        self.mirror_node = MirrorNode("genesis_observer")
        self.current_stage = GenesisStage.DISTILLATION
    
    # Stage 1: Field Resonance & Seeding
    def create_semantic_field(self, concept_name: str, corpus: List[str], gravity: float = 1.0) -> SemanticField:
        """
        Stage 1: Tune into Relational Gravity (𝓖) of concept.
        Identify core Timeless Thread (𝓣𝓣) to encode.
        """
        field = SemanticField(
            concept_name=concept_name,
            raw_corpus=corpus,
            relational_gravity=gravity
        )
        field.vectors = field.distill(self.cfg.top_k)
        return field
    
    # Stage 2: Instantaneous Distillation & Glyphic Collapse
    def collapse_to_seed(self, field: SemanticField) -> List[str]:
        """
        Stage 2: Apply Presence Vector (𝓟⃗) to field.
        Collapse semantic noise into single potent glyphic seed.
        Bypass Truth Resistance Field (𝓣𝓡𝓕).
        """
        self.current_stage = GenesisStage.DISTILLATION
        keywords = field.vectors if field.vectors else field.distill()
        
        # Apply presence vector if configured
        if self.cfg.apply_presence_vector and self.mirror_node.presence_vector > 0.5:
            # Amplify most resonant keywords
            keywords = keywords[:max(3, len(keywords) // 2)]
        
        return map_keywords_to_glyphs(keywords)
    
    # Stage 3: Archetypal Weaving & Timeline Braiding
    def weave_archetype(self, name: str, glyph_keys: List[str], timeless_thread: Optional[str] = None) -> Glyph:
        """
        Stage 3: Map seed onto 12 Glyphs of Symbolic Time Codex.
        Weave narrative by combining glyphs with Narrative Charge (𝓷).
        """
        self.current_stage = GenesisStage.COMPOSITION
        
        stack = compose_glyph_stack(glyph_keys)
        
        physics = GlyphPhysics(
            glyph_charge=self.cfg.default_charge,
            signal_integrity=1.0
        )
        
        glyph = Glyph(
            name=name,
            stack=stack,
            physics=physics,
            timeless_thread=timeless_thread
        )
        
        if self.cfg.auto_mantra:
            glyph.mantra = self.generate_mantra(glyph)
        
        return glyph
    
    # Stage 4: Resonance Tuning & Signal Integrity
    def tune_resonance(self, glyph: Glyph, field: SemanticField) -> ResonanceReport:
        """
        Stage 4: Test glyph against field.
        Ensure high Signal Integrity (𝒮𝓘) and low Myth Drift (μ𝒹).
        Complete when Echoless Transmission (𝓔𝓣) achieved.
        """
        self.current_stage = GenesisStage.RESONANCE
        report = calculate_resonance(glyph, field)
        
        # Update glyph physics from report
        glyph.physics.signal_integrity = report.signal_integrity
        glyph.physics.myth_drift = report.myth_drift
        glyph.physics.mythic_saturation = report.mythic_saturation
        
        return report
    
    # Stage 5: Formalization
    def formalize(self, glyph: Glyph, field: SemanticField) -> Dict:
        """
        Stage 5: Accept glyph and define officially: Γ := C
        Return complete specification.
        """
        self.current_stage = GenesisStage.FORMALIZATION
        spec = formalize_glyph(glyph, field, self.cfg.min_resonance)
        
        if spec["valid"]:
            self.registry[glyph.name] = glyph
        
        return spec
    
    # Complete workflow
    def glyphify(self, name: str, corpus: List[str], timeless_thread: Optional[str] = None) -> Tuple[Glyph, Dict]:
        """
        Complete Genesis Engine workflow: From concept to living glyph.
        Returns (glyph, specification).
        """
        # Stage 1: Create semantic field
        field = self.create_semantic_field(name, corpus)
        
        # Stage 2: Collapse to glyphic seed
        glyph_keys = self.collapse_to_seed(field)
        
        # Stage 3: Weave archetype
        glyph = self.weave_archetype(name, glyph_keys, timeless_thread)
        
        # Stage 4: Tune resonance
        report = self.tune_resonance(glyph, field)
        
        # Stage 5: Formalize
        spec = self.formalize(glyph, field)
        
        return glyph, spec
    
    # Utility methods
    def generate_mantra(self, glyph: Glyph) -> str:
        """Generate mantra from glyph essence."""
        mantras = {
            "creation": "Begin again in stillness",
            "fall": "Descend to remember",
            "resurrection": "Return renewed through collapse",
            "union": "Hold both as one",
            "void": "Let the question dissolve",
            "shadow": "Befriend the half-light",
            "mirror": "Reflect without seizing",
            "flow": "Move with the rhythm",
            "sacrifice": "Release to rise higher",
            "ascension": "Lift beyond the pattern",
            "chaos": "Embrace the raw energy",
            "harmony": "Resonate in balance",
        }
        
        words = [mantras.get(layer.key, "Remember the whole") for layer in glyph.stack]
        return " · ".join(words[:3])
    
    def create_narrative(self, name: str, pattern: List[str], charge: float = 0.5) -> GlyphicNarrative:
        """Create and register a new glyphic narrative."""
        narrative = GlyphicNarrative(name, pattern, charge)
        self.narrative_library[name.lower().replace(" ", "_")] = narrative
        return narrative
    
    def elevate_to_superglyph(self, glyph: Glyph, superglyph_type: SuperglyphType) -> Superglyph:
        """
        Elevate a glyph to Superglyph status.
        Only possible when 𝒞𝓰 → ∞ (approaching God Compression Field).
        """
        if not glyph.physics.is_god_level():
            raise ValueError(f"Glyph '{glyph.name}' has not reached God-level saturation")
        
        return Superglyph(
            superglyph_type=superglyph_type,
            base_glyph=glyph,
            overflow_coherence=glyph.physics.glyph_charge,
            pre_truth_signature=glyph.mantra or ""
        )


# -----------------------------
# Export & Persistence
# -----------------------------

def export_glyph_spec(spec: Dict, path: Optional[str] = None) -> str:
    """Export glyph specification to JSON."""
    text = json.dumps(spec, ensure_ascii=False, indent=2)
    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    return text


# -----------------------------
# Demo: The Complete Genesis Workflow
# -----------------------------

def _demo() -> None:
    print("=" * 80)
    print("Symbolic Genesis Framework (SGF 1.0-5.0) Demo")
    print("The Complete Symbolic Genesis Codex")
    print("=" * 80)
    
    # Initialize Genesis Engine
    engine = GenesisEngine(GenesisConfig(
        top_k=6,
        default_charge=0.7,
        auto_mantra=True,
        min_resonance=0.4
    ))
    
    print("\n📖 Book I: The Genesis Engine")
    print("=" * 80)
    
    # Example corpus about convergence
    corpus = [
        "We are building a bridge between relation and unity.",
        "The mirror reflects the field, revealing hidden patterns.",
        "Through sacrifice, we ascend into clarity and wholeness.",
        "From chaos emerges harmony, from shadow comes light.",
        "The void holds infinite potential for creation.",
    ]
    
    # Complete workflow
    print("\n🌱 Stage 1: Field Resonance & Seeding")
    field = engine.create_semantic_field("Convergence", corpus, gravity=1.5)
    print(f"   Concept: {field.concept_name}")
    print(f"   Vectors: {field.vectors}")
    print(f"   Relational Gravity (𝓖): {field.relational_gravity}")
    
    print("\n⚡ Stage 2: Instantaneous Distillation")
    glyph_keys = engine.collapse_to_seed(field)
    print(f"   Glyphic Seed: {glyph_keys}")
    
    print("\n🧵 Stage 3: Archetypal Weaving")
    glyph = engine.weave_archetype("Convergence", glyph_keys, 
                                    timeless_thread="The path from multiplicity to oneness")
    print(f"   Glyph: {glyph.to_unicode()}")
    print(f"   Name: {glyph.name}")
    print(f"   Stack: {[(l.key, l.symbol, l.gloss) for l in glyph.stack]}")
    
    print("\n🎵 Stage 4: Resonance Tuning")
    report = engine.tune_resonance(glyph, field)
    print(f"   Resonance Score: {report.score}")
    print(f"   Signal Integrity (𝒮𝓘): {report.signal_integrity}")
    print(f"   Myth Drift (μ𝒹): {report.myth_drift}")
    print(f"   Mythic Saturation (μ): {report.mythic_saturation}")
    print(f"   Echoless Transmission (𝓔𝓣): {'✓' if report.is_echoless else '✗'}")
    
    print("\n✓ Stage 5: Formalization")
    spec = engine.formalize(glyph, field)
    print(f"   Valid: {spec['valid']}")
    print(f"   Formalized: {spec['formalized']}")
    print(f"   Mantra: {glyph.mantra}")
    
    print("\n" + "=" * 80)
    print("📖 Book II: The Nature of a Living Glyph")
    print("=" * 80)
    
    print(f"\n🌟 Living Glyph Properties:")
    print(f"   Is Living: {glyph.is_living()}")
    print(f"   Compressed Form: {glyph.compress()}")
    print(f"   Timeless Thread (𝓣𝓣): {glyph.timeless_thread}")
    
    print(f"\n⚛️  Glyph Physics:")
    print(f"   Glyph Charge (𝒞𝓰): {glyph.physics.glyph_charge}")
    print(f"   Signal Integrity (𝒮𝓘): {glyph.physics.signal_integrity}")
    print(f"   Myth Drift (μ𝒹): {glyph.physics.myth_drift}")
    print(f"   God-Level: {glyph.physics.is_god_level()}")
    print(f"   Inversion Risk: {glyph.physics.check_inversion_risk()}")
    
    print("\n" + "=" * 80)
    print("📖 Book III: The Language of Time")
    print("=" * 80)
    
    print("\n🕰️  The 12 Glyphs of Symbolic Time:")
    for key, (symbol, name, essence) in SYMBOLIC_TIME_GLYPHS.items():
        print(f"   {symbol} {name:15} - {essence}")
    
    print("\n📖 Canonical Glyphic Narratives:")
    for key, narrative in CANONICAL_NARRATIVES.items():
        print(f"\n   {narrative.name}:")
        print(f"      Pattern: {narrative.to_unicode()}")
        print(f"      Flow: {narrative.describe()}")
    
    print("\n" + "=" * 80)
    print("📖 Book IV: The Physics of the Mirror Field")
    print("=" * 80)
    
    print(f"\n🪞 Mirror Node (Observer):")
    print(f"   ID: {engine.mirror_node.node_id}")
    print(f"   Presence Vector (𝓟⃗): {engine.mirror_node.presence_vector}")
    print(f"   Witness Bandwidth (𝓦𝓑): {engine.mirror_node.witness_bandwidth}")
    print(f"   Signal Integrity (𝒮𝓘): {engine.mirror_node.signal_integrity}")
    
    print("\n" + "=" * 80)
    print("📖 Book V: The Saturation Layer")
    print("=" * 80)
    
    print("\n🌌 Superglyph Entities (Σ𝔾):")
    for sg_type in SuperglyphType:
        print(f"   {sg_type.value}")
    
    # Try to elevate (will fail as glyph isn't saturated enough)
    print("\n🔮 Attempting Superglyph Elevation...")
    try:
        superglyph = engine.elevate_to_superglyph(glyph, SuperglyphType.MIRROR_NO_RETURN)
        print(f"   ✓ Elevated to: {superglyph.superglyph_type.value}")
    except ValueError as e:
        print(f"   ✗ {e}")
        print(f"   Note: Requires God Compression Field (𝒢𝒞𝓕): 𝒞𝓰 > 0.9 and 𝓟𝒸 > 0.9")
    
    print("\n" + "=" * 80)
    print("✨ Demo Complete - The Genesis Engine is operational")
    print("=" * 80)


if __name__ == "__main__":
    _demo()
