# symbolic.py
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Callable, Dict, Iterable, List, Optional, Tuple, Set
import math
import re
import json
import time
import random

# -----------------------------
# Symbolic Primitives
# -----------------------------

# Canon of base glyphs (Symbolic Time set)
BASE_GLYPHS: Dict[str, str] = {
    "origin": "⊙",      # seed, birth, source
    "charge": "↯",      # spark, disturbance, ignition
    "resurrection": "✶",# renewal, return, reframe
    "union": "∞",       # unity, nonduality, both-and
    "null": "∅",        # the void, silence, empty question
    "shadow": "◐",      # half-light, unconscious, unknown
    "mirror": "▢",      # reflection, relation, self-other
    "bridge": "≈",      # similarity, isomorphism, cross-context
    "sacrifice": "△",   # release, offering, letting go
    "ascend": "↑",      # lift, clarity, orientation
    "weave": "⌘",       # pattern, code, knot
    "earth": "♁",       # embodiment, matter, world
}

STOPWORDS: Set[str] = {
    "the","a","an","and","or","but","to","of","in","on","for","by","with","as",
    "is","are","was","were","be","being","been","at","from","that","this","it",
    "into","over","under","between","about","through"
}

# -----------------------------
# Data Structures
# -----------------------------

@dataclass
class GlyphLayer:
    key: str                 # canonical key like "union", "mirror"
    symbol: str              # unicode glyph
    gloss: str               # short meaning
    weight: float = 1.0      # contribution in the stack
    tags: List[str] = field(default_factory=list)

@dataclass
class Glyph:
    """
    A living glyph built from layers.
    name: human handle
    stack: ordered layers, top is last
    charge: strength from 0 to 1, used in resonance
    """
    name: str
    stack: List[GlyphLayer] = field(default_factory=list)
    charge: float = 0.5
    mantra: Optional[str] = None
    notes: Dict[str, str] = field(default_factory=dict)

    def to_text(self) -> str:
        return "".join(layer.symbol for layer in self.stack)

    def to_spec(self) -> Dict:
        return {
            "name": self.name,
            "glyph": self.to_text(),
            "charge": round(self.charge, 4),
            "layers": [asdict(layer) for layer in self.stack],
            "mantra": self.mantra,
            "notes": self.notes
        }

# -----------------------------
# Tokenization and utilities
# -----------------------------

def normalize(text: str) -> List[str]:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    toks = [t for t in text.split() if t and t not in STOPWORDS]
    return toks

def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 1.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0

def softmax(xs: List[float]) -> List[float]:
    m = max(xs) if xs else 0.0
    exps = [math.exp(x - m) for x in xs]
    s = sum(exps) or 1.0
    return [e / s for e in exps]

# -----------------------------
# Distillation
# -----------------------------

def distill_keywords(corpus: Iterable[str], top_k: int = 6) -> List[str]:
    """
    Very lightweight keyword distiller:
      1) count frequencies
      2) prefer mid-length content words
      3) return top_k
    """
    counts: Dict[str, int] = {}
    for text in corpus:
        for t in normalize(text):
            counts[t] = counts.get(t, 0) + 1
    if not counts:
        return []
    # score: frequency * length bonus
    scored = [(w, c * (1.0 + min(len(w), 10) / 10.0)) for w, c in counts.items()]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [w for w, _ in scored[:top_k]]

# -----------------------------
# Mapping: keywords -> base glyph keys
# -----------------------------

# You can extend this mapping as your lexicon grows
KEYWORD_TO_BASE: Dict[str, str] = {
    # unity and integration
    "union": "union", "oneness": "union", "nonduality": "union", "both": "union", "together": "union",
    "bridge": "bridge", "translate": "bridge", "map": "bridge", "mirror": "mirror", "reflect": "mirror",
    "empty": "null", "silence": "null", "void": "null", "nothing": "null",
    "birth": "origin", "seed": "origin", "source": "origin", "origin": "origin",
    "spark": "charge", "ignite": "charge", "shock": "charge", "energy": "charge",
    "resurrect": "resurrection", "renew": "resurrection", "return": "resurrection",
    "shadow": "shadow", "unconscious": "shadow", "unknown": "shadow",
    "sacrifice": "sacrifice", "let": "sacrifice", "release": "sacrifice", "give": "sacrifice",
    "ascend": "ascend", "lift": "ascend", "clarity": "ascend", "up": "ascend",
    "weave": "weave", "pattern": "weave", "code": "weave", "knot": "weave",
    "earth": "earth", "body": "earth", "matter": "earth", "world": "earth",
    # relational math resonance
    "relation": "mirror", "loop": "weave", "graph": "weave", "role": "mirror",
}

def map_keywords_to_bases(keywords: List[str]) -> List[str]:
    bases = []
    for k in keywords:
        key = KEYWORD_TO_BASE.get(k)
        if key:
            bases.append(key)
    # fallback if nothing mapped
    if not bases and keywords:
        # pick a reasonable pair: mirror + bridge
        bases = ["mirror", "bridge"]
    return bases[:6]

# -----------------------------
# Composition: build a glyph stack
# -----------------------------

def make_layer(key: str, weight: float = 1.0, tags: Optional[List[str]] = None) -> GlyphLayer:
    symbol = BASE_GLYPHS.get(key, "?")
    gloss = {
        "origin": "seed and source",
        "charge": "spark of ignition",
        "resurrection": "renewal through return",
        "union": "two become one",
        "null": "void and silence",
        "shadow": "half-light domain",
        "mirror": "relation and reflection",
        "bridge": "cross-context link",
        "sacrifice": "release to rise",
        "ascend": "orientation and lift",
        "weave": "pattern and knot",
        "earth": "embodiment in matter",
    }.get(key, "unknown")
    return GlyphLayer(key=key, symbol=symbol, gloss=gloss, weight=weight, tags=tags or [])

def compose_stack(bases: List[str]) -> List[GlyphLayer]:
    """
    Rules:
      - keep order meaningful: origin/charge before union/bridge
      - ensure no exact duplicates unless intentional
      - normalize weights with softmax so stack sums to 1 by default
    """
    seen: Set[str] = set()
    ordered: List[str] = []
    priority = {"origin": 0, "charge": 1, "shadow": 2, "sacrifice": 3, "bridge": 4,
                "mirror": 5, "weave": 6, "ascend": 7, "union": 8, "resurrection": 9, "earth": 10}
    for b in sorted(bases, key=lambda x: priority.get(x, 99)):
        if b not in seen:
            seen.add(b)
            ordered.append(b)
    raw_weights = [1.0 for _ in ordered]
    weights = softmax(raw_weights)
    return [make_layer(k, w) for k, w in zip(ordered, weights)]

# -----------------------------
# Resonance and validation
# -----------------------------

@dataclass
class ResonanceReport:
    score: float                 # 0..1
    signal_integrity: float      # heuristic confidence 0..1
    coverage: float              # keyword coverage
    field_tokens: List[str]      # distilled tokens
    matched_bases: List[str]     # mapped base keys
    glyph_text: str              # rendered stack
    notes: Dict[str, str] = field(default_factory=dict)

def resonance(glyph: Glyph, corpus: Iterable[str]) -> ResonanceReport:
    toks = set()
    for t in corpus:
        toks |= set(normalize(t))
    bases = set(l.key for l in glyph.stack)
    # compute simple overlaps by mapping tokens back to base keys
    mapped = set(map_keywords_to_bases(list(toks)))
    coverage = jaccard(mapped, bases)
    # signal integrity favors balanced stacks and non-trivial charge
    stack_div = 1.0 - abs(len(glyph.stack) - 3) / 5.0
    charge_ok = 1.0 - abs(glyph.charge - 0.6)
    integrity = max(0.0, min(1.0, 0.5 * stack_div + 0.5 * (1.0 - charge_ok)))
    score = 0.6 * coverage + 0.4 * integrity
    return ResonanceReport(
        score=round(score, 4),
        signal_integrity=round(integrity, 4),
        coverage=round(coverage, 4),
        field_tokens=sorted(list(toks)),
        matched_bases=sorted(list(mapped)),
        glyph_text=glyph.to_text(),
        notes={"stack_len": str(len(glyph.stack))}
    )

# -----------------------------
# Formalization and export
# -----------------------------

def formalize(glyph: Glyph, corpus: Iterable[str], min_score: float = 0.35) -> Dict:
    report = resonance(glyph, corpus)
    spec = glyph.to_spec()
    spec["resonance"] = asdict(report)
    spec["valid"] = report.score >= min_score
    return spec

def export_spec(spec: Dict, path: Optional[str] = None) -> str:
    text = json.dumps(spec, ensure_ascii=False, indent=2)
    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    return text

# -----------------------------
# The Genesis Engine
# -----------------------------

@dataclass
class GenesisConfig:
    top_k: int = 6
    default_charge: float = 0.6
    auto_mantra: bool = True

class GenesisEngine:
    def __init__(self, cfg: Optional[GenesisConfig] = None):
        self.cfg = cfg or GenesisConfig()
        self.registry: Dict[str, Glyph] = {}

    def distill(self, corpus: Iterable[str]) -> List[str]:
        return distill_keywords(corpus, self.cfg.top_k)

    def map(self, keywords: List[str]) -> List[str]:
        return map_keywords_to_bases(keywords)

    def compose(self, name: str, bases: List[str]) -> Glyph:
        stack = compose_stack(bases)
        g = Glyph(name=name, stack=stack, charge=self.cfg.default_charge)
        if self.cfg.auto_mantra:
            g.mantra = self.autogenerate_mantra(g)
        return g

    def resonate(self, glyph: Glyph, corpus: Iterable[str]) -> ResonanceReport:
        return resonance(glyph, corpus)

    def formalize(self, glyph: Glyph, corpus: Iterable[str], min_score: float = 0.35) -> Dict:
        return formalize(glyph, corpus, min_score)

    def glyphify(self, name: str, corpus: Iterable[str]) -> Tuple[Glyph, Dict]:
        kws = self.distill(corpus)
        bases = self.map(kws)
        g = self.compose(name, bases)
        spec = self.formalize(g, corpus)
        # registry side-effect
        self.registry[name] = g
        return g, spec

    def autogenerate_mantra(self, glyph: Glyph) -> str:
        text = glyph.to_text()
        verbs = {
            "⊙": "begin again in stillness",
            "↯": "ignite what is asleep",
            "✶": "return renewed",
            "∞": "hold both as one",
            "∅": "let the question fall silent",
            "◐": "befriend the half-light",
            "▢": "mirror without grabbing",
            "≈": "cross the unseen bridge",
            "△": "release to rise",
            "↑": "lift and orient",
            "⌘": "weave the pattern you carry",
            "♁": "let truth take form",
        }
        words = [verbs.get(layer.symbol, "remember") for layer in glyph.stack]
        # compact mantra
        return " · ".join(words[:3])

# -----------------------------
# Tiny demo
# -----------------------------

def _demo() -> None:
    print("Symbolic 1.0 demo")
    engine = GenesisEngine()

    corpus = [
        "We are building a bridge between relation and unity.",
        "Mirror the field, then release control to ascend into clarity.",
        "Let the shadow speak so the pattern can renew.",
    ]

    glyph, spec = engine.glyphify("Convergence", corpus)
    report = spec["resonance"]

    print("Glyph:", glyph.to_text(), "name:", glyph.name)
    print("Mantra:", glyph.mantra)
    print("Stack:", [(l.key, l.symbol) for l in glyph.stack])
    print("Resonance score:", report["score"], "coverage:", report["coverage"])
    print("Valid:", spec["valid"])

    # Write spec to file if desired
    # export_spec(spec, "convergence_glyph.json")

if __name__ == "__main__":
    _demo()