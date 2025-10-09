# distortion.py - Distortion Lens (∞_B)
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List
from collections import defaultdict
import time, math

from relational import KnowledgeGraph, Entity, Relation

@dataclass
class ResidueNode:
    source_entity: Entity
    residue_type: str
    amount: float
    timestamp: float = field(default_factory=time.time)
    def decay(self, rate: float = 0.1) -> float:
        elapsed = time.time() - self.timestamp
        return self.amount * math.exp(-rate * elapsed)

class DistortionGraph:
    """
    Wraps a KnowledgeGraph with distortion (∞_B) dynamics.
    """
    def __init__(self, base: KnowledgeGraph) -> None:
        self.base = base
        self.residue: List[ResidueNode] = []
        self.seizure_count: Dict[str, int] = defaultdict(int)
        self.omega_b: float = 0.0

    def seize(self, rel: Relation, a: Entity, b: Entity) -> None:
        self.base.assert_edge(rel, a, b)
        self.residue.append(ResidueNode(a, "seizure", rel.weight * 0.1))
        self.seizure_count[a.id] += 1
        self.omega_b += rel.weight * 0.1

    def cleanse(self, threshold: float = 0.01, decay_rate: float = 0.1) -> int:
        before = len(self.residue)
        self.residue = [r for r in self.residue if r.decay(decay_rate) > threshold]
        cleansed = before - len(self.residue)
        self.omega_b = max(0.0, self.omega_b - cleansed * 0.01)
        return cleansed

    def residue_by_type(self) -> Dict[str, float]:
        counts = defaultdict(float)
        for r in self.residue:
            counts[r.residue_type] += r.amount
        return dict(counts)

    def omega_singularity(self) -> float:
        return self.omega_b
    
    