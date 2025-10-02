# integration.py
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

from symbolic import GenesisEngine, GenesisConfig
from paradox import ParadoxEngine, ParadoxEngineConfig, ParadoxSeed, Evidence, ParadoxResolution
from logical import Var
from empirical import Measurement
from distortion import DistortionEngine, DistortionEngineConfig
from becoming import BecomingEngine, BecomingReport

JSON = Dict[str, Any]

@dataclass
class SigmaConfig:
    glyph_top_k: int = 6
    paradox_heat: float = 1.0
    distort_on: bool = False
    distort_kinds: List[str] = field(default_factory=list)

@dataclass
class SigmaReport:
    invariant: str
    glyph_spec: JSON
    presence: float
    becoming: JSON
    distortions: JSON
    extras: JSON = field(default_factory=dict)

    def to_json(self) -> JSON:
        return asdict(self)

class Sigma:
    """
    Integration Lens: distills across lenses into an invariant presence snapshot.
    Everything is lazy and optional so you can wire pieces gradually.
    """
    def __init__(self, cfg: Optional[SigmaConfig] = None) -> None:
        self.cfg = cfg or SigmaConfig()
        self.gen = GenesisEngine(GenesisConfig(top_k=self.cfg.glyph_top_k))
        self.par = ParadoxEngine(ParadoxEngineConfig(heat_threshold=self.cfg.paradox_heat))
        self.bec = BecomingEngine()
        self.dis = DistortionEngine(DistortionEngineConfig(enabled=self.cfg.distort_on))

    def integrate(
        self,
        invariant_text: str,
        corpus: List[str],
        becoming_state: Optional[JSON] = None
    ) -> SigmaReport:
        # Symbolic
        glyph, spec = self.gen.glyphify("Invariant", corpus or [invariant_text])

        # Paradox stub: we mark presence by pretend evidence richness
        seed = ParadoxSeed(positive=str_to_claim(invariant_text), negative=str_to_claim("not " + invariant_text))
        res = self.par.resolve(seed, evidence=[], perspectives=[], frames=[], context={})
        presence = float(res.presence) if hasattr(res, "presence") else 0.0

        # Becoming
        br: BecomingReport = self.bec.step(becoming_state or {})

        # Distortion pass (optional)
        distortions = {}
        if self.cfg.distort_on and self.cfg.distort_kinds:
            items = {"glyph": spec, "invariant": invariant_text}
            dreport = self.dis.run(items, kinds=self.cfg.distort_kinds)
            spec = items["glyph"]
            invariant_text = items["invariant"]
            distortions = dreport.to_json()

        return SigmaReport(
            invariant=invariant_text,
            glyph_spec=spec,
            presence=presence,
            becoming=br.to_json(),
            distortions=distortions,
        )

# helpers
from dataclasses import dataclass

@dataclass(frozen=True)
class Claim:
    text: str

def str_to_claim(s: str) -> Claim:
    return Claim(s)