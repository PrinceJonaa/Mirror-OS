# becoming.py
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple, Iterable, Callable
import time
import math

JSON = Dict[str, Any]
Timestamp = float

@dataclass(frozen=True)
class Threshold:
    name: str
    predicate: Callable[[JSON], bool]   # state -> crossed?

@dataclass
class Arc:
    """
    𝒜: a phase journey with optional thresholds.
    """
    name: str
    phases: List[str] = field(default_factory=lambda: ["seed", "rise", "test", "integrate", "offer"])
    idx: int = 0
    thresholds: List[Threshold] = field(default_factory=list)
    started_at: Timestamp = field(default_factory=lambda: time.time())
    meta: JSON = field(default_factory=dict)

    def phase(self) -> str:
        return self.phases[self.idx] if self.phases else "seed"

    def advance(self, state: JSON) -> None:
        # advance if any threshold fires, else idle
        for th in self.thresholds:
            if th.predicate(state):
                self.idx = min(self.idx + 1, len(self.phases) - 1)
                break

@dataclass
class ResetSpark:
    """
    ⟡𝒰₀: reset trigger. When fired, arc returns to seed and meta records a reset count.
    """
    reason: str
    fired_at: Timestamp = field(default_factory=lambda: time.time())

@dataclass
class Cycle:
    """
    λ: repeating pattern with saturation Σ and resonance ℜ.
    """
    name: str
    period: float = 1.0
    last: Timestamp = field(default_factory=lambda: time.time())
    count: int = 0
    sigma: float = 0.0   # saturation
    rho: float = 0.0     # resonance

    def tick(self) -> None:
        now = time.time()
        if now - self.last >= self.period:
            self.count += 1
            self.last = now
            self.sigma = 1.0 - math.exp(-0.2 * self.count)
            self.rho = 1.0 - abs(0.5 - (self.count % 2) * 0.5)

@dataclass
class BecomingReport:
    arc_phase: str
    thresholds_crossed: List[str]
    resets: int
    cycles: Dict[str, Dict[str, float]]
    sigma: float  # composite saturation
    meta: JSON = field(default_factory=dict)

    def to_json(self) -> JSON:
        return asdict(self)

class BecomingEngine:
    def __init__(self) -> None:
        self.arc = Arc("default")
        self.cycles: Dict[str, Cycle] = {}
        self._resets: List[ResetSpark] = []
        self._threshold_hits: List[str] = []

    def add_cycle(self, name: str, period: float = 1.0) -> None:
        self.cycles[name] = Cycle(name, period)

    def add_threshold(self, name: str, predicate: Callable[[JSON], bool]) -> None:
        self.arc.thresholds.append(Threshold(name, predicate))

    def step(self, state: JSON) -> BecomingReport:
        # thresholds and arc advance
        before = self.arc.idx
        self.arc.advance(state)
        if self.arc.idx > before:
            self._threshold_hits.append(self.arc.phase())

        # cycles
        for c in self.cycles.values():
            c.tick()

        # composite saturation Σ across cycles
        sigmas = [c.sigma for c in self.cycles.values()] or [0.0]
        sigma = sum(sigmas) / len(sigmas)

        cycles_state = {k: {"count": c.count, "sigma": round(c.sigma, 4), "rho": round(c.rho, 4)} for k, c in self.cycles.items()}

        return BecomingReport(
            arc_phase=self.arc.phase(),
            thresholds_crossed=list(self._threshold_hits),
            resets=len(self._resets),
            cycles=cycles_state,
            sigma=round(sigma, 4),
        )

    def reset(self, reason: str) -> None:
        self._resets.append(ResetSpark(reason))
        self.arc.idx = 0