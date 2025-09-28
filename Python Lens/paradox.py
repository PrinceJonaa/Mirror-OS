# paradox.py
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union
import time
import math
import json
import random

# ============================================================
# Paradox Induction Codex – Code Model (PIC 1.0)
# Seed -> Chamber -> Saturate -> Frame -> Collapse -> Resolution
# ============================================================

JSON = Dict[str, Any]
Timestamp = float

# Optional dependencies are expressed as callables to avoid hard imports.
# You may pass:
# - glyph_builder(conclusion:str, context:JSON) -> Dict   from symbolic.py
# - lp_contradiction(phi:Any, context:JSON) -> bool       from logical LP
# - presence_metric(state:JSON) -> float                  from empirical.py


# -----------------------------
# Claims, Seeds, Evidence
# -----------------------------

@dataclass(frozen=True)
class Claim:
    """
    A single propositional assertion captured as text plus optional structure.
    """
    text: str
    source: str = ""
    meta: JSON = field(default_factory=dict)

    def __str__(self) -> str:
        return self.text


@dataclass(frozen=True)
class ParadoxSeed:
    """
    A minimal contradiction: A and not-A, stated as two claims in tension.
    """
    positive: Claim
    negative: Claim
    scope: str = "same-frame"  # same-frame, cross-frame, unknown
    tags: List[str] = field(default_factory=list)
    meta: JSON = field(default_factory=dict)


@dataclass
class Evidence:
    """
    Any artifact that heats the chamber: examples, counterexamples, measurements,
    relational maps, role or time splits, quotes, or structured data.
    """
    label: str
    payload: Any
    weight: float = 1.0
    meta: JSON = field(default_factory=dict)


# -----------------------------
# Chamber, Thermodynamics, Frames
# -----------------------------

@dataclass
class ParadoxChamber:
    """
    A bounded container that holds the contradiction without forcing a premature choice.
    Temperature rises with added evidence and perspective diversity until collapse is ready.
    """
    seed: ParadoxSeed
    context: JSON = field(default_factory=dict)
    created_at: Timestamp = field(default_factory=lambda: time.time())
    temperature: float = 0.0
    evidence: List[Evidence] = field(default_factory=list)
    perspectives: List[str] = field(default_factory=list)   # e.g., roles, lenses, time-slices
    frames: List["Frame"] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: f"pic-{int(time.time()*1000)}-{random.randint(1000,9999)}")

    def add_evidence(self, ev: Evidence) -> None:
        self.evidence.append(ev)
        self.temperature += max(0.05, math.log1p(ev.weight) * 0.1)

    def add_perspective(self, name: str, weight: float = 1.0) -> None:
        if name not in self.perspectives:
            self.perspectives.append(name)
            self.temperature += 0.05 * weight

    def attach_frame(self, frame: "Frame") -> None:
        self.frames.append(frame)
        self.temperature += 0.08

    def annotate(self, text: str) -> None:
        self.notes.append(text)

    def ready(self, threshold: float = 1.0) -> bool:
        return self.temperature >= threshold


@dataclass
class Frame:
    """
    A reframing boundary that can dissolve apparent contradiction by changing
    role, time, level of abstraction, or measurement rule.
    """
    name: str
    rule: Callable[[Claim, Claim, JSON], bool]
    description: str = ""
    meta: JSON = field(default_factory=dict)

    def compatible(self, a: Claim, b: Claim, ctx: JSON) -> bool:
        """
        Returns True if in this frame the two claims can both be held without direct conflict.
        """
        return bool(self.rule(a, b, ctx))


# -----------------------------
# Collapse Vectors
# -----------------------------

@dataclass(frozen=True)
class CollapseVector:
    """
    A strategy that tries to resolve paradox into a higher-order invariant.
    """
    name: str
    apply: Callable[["ParadoxChamber"], "ParadoxResolution"]
    priority: int = 5
    meta: JSON = field(default_factory=dict)


# Predefined vector factories

def cv_complementarity() -> CollapseVector:
    """
    For wave vs particle style oppositions. Returns a both-and invariant with domain conditions.
    """
    def _run(ch: ParadoxChamber) -> ParadoxResolution:
        ctx = {"type": "complementarity", "conditions": []}
        # Heuristic: if any frame marked measurement-rule is present, use it to gate the invariant.
        conds = []
        for fr in ch.frames:
            if "measurement" in fr.meta.get("kind", "") or fr.meta.get("kind") == "measurement":
                conds.append(fr.name)
        if not conds:
            conds = [f"measurement-context-{i}" for i, _ in enumerate(ch.frames)]
        ctx["conditions"] = conds
        invariant = f"Both claims are valid under different measurement conditions: {', '.join(conds)}"
        return ParadoxResolution.ok(
            kind="complementarity",
            invariant=invariant,
            chamber=ch,
            mapping={"A": ch.seed.positive.text, "notA": ch.seed.negative.text},
            context=ctx
        )
    return CollapseVector("complementarity", _run, priority=3)


def cv_level_lift() -> CollapseVector:
    """
    Lifts A and not-A into a higher abstraction where both are subcases.
    """
    def _run(ch: ParadoxChamber) -> ParadoxResolution:
        pos = ch.seed.positive.text
        neg = ch.seed.negative.text
        invariant = f"There exists a higher concept H such that both statements are projections: H -> {{{pos} | {neg}}}"
        return ParadoxResolution.ok(
            kind="level-lift",
            invariant=invariant,
            chamber=ch,
            mapping={"super": "H", "cases": [pos, neg]},
            context={"abstraction": "lifted"}
        )
    return CollapseVector("level-lift", _run, priority=4)


def cv_role_split() -> CollapseVector:
    """
    Splits by role identity. A is true for role R1, not-A holds for role R2.
    """
    def _run(ch: ParadoxChamber) -> ParadoxResolution:
        roles = [p for p in ch.perspectives if p.startswith("role:")]
        if len(roles) < 2:
            return ParadoxResolution.noop("role-split requires at least two role perspectives", ch)
        a_role = roles[0].split(":", 1)[1]
        b_role = roles[1].split(":", 1)[1]
        invariant = f"A holds for role {a_role}, not-A holds for role {b_role}"
        return ParadoxResolution.ok(
            kind="role-split",
            invariant=invariant,
            chamber=ch,
            mapping={"A@role": a_role, "~A@role": b_role},
            context={"roles": roles}
        )
    return CollapseVector("role-split", _run, priority=5)


def cv_time_partition() -> CollapseVector:
    """
    Uses time to separate assertions. A then, not-A now (or vice versa).
    """
    def _run(ch: ParadoxChamber) -> ParadoxResolution:
        t0 = ch.created_at
        t1 = time.time()
        invariant = f"A applies before t0, not-A applies after t1"
        return ParadoxResolution.ok(
            kind="time-partition",
            invariant=invariant,
            chamber=ch,
            mapping={"t0": t0, "t1": t1},
            context={"time_partition": True}
        )
    return CollapseVector("time-partition", _run, priority=6)


def cv_redefine_terms() -> CollapseVector:
    """
    Finds definitional drift. If terms are used differently, unify through precise definitions.
    """
    def _run(ch: ParadoxChamber) -> ParadoxResolution:
        invariant = "The terms differ in definition. Standardize vocabulary and both statements align."
        return ParadoxResolution.ok(
            kind="redefine-terms",
            invariant=invariant,
            chamber=ch,
            mapping={},
            context={"lexical": "standardized"}
        )
    return CollapseVector("redefine-terms", _run, priority=2)


# -----------------------------
# Resolution Product
# -----------------------------

@dataclass
class ParadoxResolution:
    """
    Result of a collapse attempt.
    status: ok, noop, fail
    kind: vector name or category
    invariant: single sentence description of the reconciled truth
    """
    status: str
    kind: str
    invariant: str
    chamber_id: str
    glyph_hint: Optional[Dict[str, Any]] = None
    mapping: JSON = field(default_factory=dict)
    context: JSON = field(default_factory=dict)
    presence: float = 0.0
    meta: JSON = field(default_factory=dict)

    @staticmethod
    def ok(kind: str, invariant: str, chamber: ParadoxChamber, mapping: JSON, context: JSON) -> "ParadoxResolution":
        return ParadoxResolution(
            status="ok",
            kind=kind,
            invariant=invariant,
            chamber_id=chamber.id,
            mapping=mapping,
            context=context
        )

    @staticmethod
    def noop(reason: str, chamber: ParadoxChamber) -> "ParadoxResolution":
        return ParadoxResolution(
            status="noop",
            kind="noop",
            invariant=f"no collapse: {reason}",
            chamber_id=chamber.id
        )

    @staticmethod
    def fail(reason: str, chamber: ParadoxChamber) -> "ParadoxResolution":
        return ParadoxResolution(
            status="fail",
            kind="error",
            invariant=f"failed: {reason}",
            chamber_id=chamber.id
        )

    def to_json(self) -> JSON:
        return asdict(self)


# -----------------------------
# Engine
# -----------------------------

@dataclass
class ParadoxEngineConfig:
    heat_threshold: float = 1.0
    vectors: List[CollapseVector] = field(default_factory=lambda: [
        cv_redefine_terms(),
        cv_complementarity(),
        cv_level_lift(),
        cv_role_split(),
        cv_time_partition(),
    ])
    max_attempts: int = 8
    randomize: bool = False
    auto_frame_same_sense: bool = True  # if claims use different senses, add a frame automatically


class ParadoxEngine:
    """
    Orchestrates paradox handling. You can inject custom vectors and hooks.
    """
    def __init__(
        self,
        cfg: Optional[ParadoxEngineConfig] = None,
        glyph_builder: Optional[Callable[[str, JSON], Dict[str, Any]]] = None,
        presence_metric: Optional[Callable[[JSON], float]] = None
    ) -> None:
        self.cfg = cfg or ParadoxEngineConfig()
        self.glyph_builder = glyph_builder
        self.presence_metric = presence_metric

    # --- lifecycle ---

    def chamber(self, seed: ParadoxSeed, context: Optional[JSON] = None) -> ParadoxChamber:
        ch = ParadoxChamber(seed=seed, context=context or {})
        # Prime with a default note
        ch.annotate("Paradox chamber created")
        # If same words appear with different senses, auto-frame a sense-split
        if self.cfg.auto_frame_same_sense and self._suspicious_lexical(ch):
            fr = Frame(
                name="sense-split",
                description="Different senses of a shared term are allowed",
                rule=lambda a, b, ctx: True,
                meta={"kind": "lexical"}
            )
            ch.attach_frame(fr)
            ch.annotate("Auto frame: sense-split")
        return ch

    def heat(self, chamber: ParadoxChamber, evidence: Iterable[Evidence] = ()) -> ParadoxChamber:
        for ev in evidence:
            chamber.add_evidence(ev)
        return chamber

    def reflect(self, chamber: ParadoxChamber, perspectives: Iterable[str]) -> ParadoxChamber:
        for p in perspectives:
            chamber.add_perspective(p, weight=1.0)
        return chamber

    def frame(self, chamber: ParadoxChamber, frames: Iterable[Frame]) -> ParadoxChamber:
        for fr in frames:
            chamber.attach_frame(fr)
        return chamber

    def collapse(self, chamber: ParadoxChamber) -> ParadoxResolution:
        if not chamber.ready(self.cfg.heat_threshold):
            return ParadoxResolution.noop("insufficient heat to trigger collapse", chamber)

        vectors = list(self.cfg.vectors)
        if self.cfg.randomize:
            random.shuffle(vectors)
        else:
            vectors.sort(key=lambda v: v.priority)

        attempts = 0
        last = ParadoxResolution.noop("no vector succeeded", chamber)
        for v in vectors:
            attempts += 1
            if attempts > self.cfg.max_attempts:
                break
            try:
                res = v.apply(chamber)
            except Exception as e:
                last = ParadoxResolution.fail(f"vector {v.name} error: {e}", chamber)
                continue
            if res.status == "ok":
                # optional glyph
                if self.glyph_builder:
                    res.glyph_hint = self.glyph_builder(res.invariant, {"vector": v.name, "context": res.context})
                # optional presence score
                if self.presence_metric:
                    res.presence = float(self.presence_metric({
                        "vector": v.name,
                        "evidence_count": len(chamber.evidence),
                        "perspectives": len(chamber.perspectives),
                        "frames": len(chamber.frames),
                        "invariant": res.invariant
                    }))
                return res
            last = res
        return last

    # --- helpers ---

    def _suspicious_lexical(self, chamber: ParadoxChamber) -> bool:
        """
        Quick lexical heuristic: if positive and negative share a head word, assume sense split helps.
        """
        def head(s: str) -> str:
            return s.strip().lower().split()[0] if s.strip() else ""
        return head(chamber.seed.positive.text) == head(chamber.seed.negative.text) and head(chamber.seed.positive.text) != ""

    # Convenience one-shot
    def resolve(
        self,
        seed: ParadoxSeed,
        evidence: Iterable[Evidence] = (),
        perspectives: Iterable[str] = (),
        frames: Iterable[Frame] = (),
        context: Optional[JSON] = None
    ) -> ParadoxResolution:
        ch = self.chamber(seed, context)
        self.heat(ch, evidence)
        self.reflect(ch, perspectives)
        self.frame(ch, frames)
        return self.collapse(ch)


# -----------------------------
# Ready frames
# -----------------------------

def frame_measurement_rule(name: str = "measurement-rule") -> Frame:
    """
    Allows both claims when they are gated by different measurement procedures.
    """
    return Frame(
        name=name,
        description="Claims are compatible when measured under distinct procedures",
        rule=lambda a, b, ctx: True,
        meta={"kind": "measurement"}
    )

def frame_role(name: str, role_a: str, role_b: str) -> Frame:
    """
    Role split. Validates compatibility if claims partition by role identities.
    """
    def _rule(a: Claim, b: Claim, ctx: JSON) -> bool:
        return True  # actual role binding is enforced by the collapse vector
    return Frame(
        name=name,
        description=f"Role partition {role_a} vs {role_b}",
        rule=_rule,
        meta={"kind": "role", "roles": [role_a, role_b]}
    )

def frame_time(name: str = "time-slice") -> Frame:
    return Frame(
        name=name,
        description="Claims refer to different time slices",
        rule=lambda a, b, ctx: True,
        meta={"kind": "time"}
    )


# -----------------------------
# Serialization
# -----------------------------

def export_chamber(chamber: ParadoxChamber) -> str:
    blob = {
        "id": chamber.id,
        "seed": {
            "positive": asdict(chamber.seed.positive),
            "negative": asdict(chamber.seed.negative),
            "scope": chamber.seed.scope,
            "tags": chamber.seed.tags,
            "meta": chamber.seed.meta,
        },
        "context": chamber.context,
        "created_at": chamber.created_at,
        "temperature": chamber.temperature,
        "evidence": [asdict(ev) for ev in chamber.evidence],
        "perspectives": list(chamber.perspectives),
        "frames": [{"name": f.name, "description": f.description, "meta": f.meta} for f in chamber.frames],
        "notes": list(chamber.notes),
    }
    return json.dumps(blob, ensure_ascii=False, indent=2)

def export_resolution(res: ParadoxResolution) -> str:
    return json.dumps(res.to_json(), ensure_ascii=False, indent=2)


# -----------------------------
# Quick builders
# -----------------------------

def seed_from_text(a_text: str, b_text: str, scope: str = "same-frame", source_a: str = "", source_b: str = "") -> ParadoxSeed:
    return ParadoxSeed(positive=Claim(a_text, source=source_a), negative=Claim(b_text, source=source_b), scope=scope)

def evidence_examples(*items: Tuple[str, Any]) -> List[Evidence]:
    """
    Build evidence from (label, payload) pairs with default weight 1.0.
    """
    return [Evidence(label=k, payload=v, weight=1.0) for k, v in items]

def role_tag(role: str) -> str:
    return f"role:{role}"