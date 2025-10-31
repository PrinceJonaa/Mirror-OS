# agents.py (sketchy but runnable scaffolding)
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple
from truth_lattice import TruthLattice
from arc_dsl import Grid
from arc_ops import Program
from solver import a_star_search
from paradox import ParadoxSeed, Evidence, frame_measurement_rule, role_tag
from empirical import Measurement, diagnose

@dataclass
class Explorer:
    def perceive(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # extract quick features
        trains = [(Grid(ex["input"]), Grid(ex["output"])) for ex in task["train"]]
        feats = {
            "avg_palette": sum(len(x.palette()) for x,_ in trains)/max(1,len(trains)),
            "area_preserved": all(x.h*x.w==y.h*y.w for x,y in trains),
        }
        return {"trains": trains, "features": feats}

@dataclass
class Synthesizer:
    def propose(self, trains, max_len=5, beam=200) -> List[Program]:
        return a_star_search(trains, max_len=max_len, beam=beam)

@dataclass
class Critic:
    def evaluate(self, prog: Program, trains) -> Dict[str, Any]:
        mismatches = []
        for x,y in trains:
            out = prog.run(x)
            mismatches.append(sum(int(out.cells[r][c]!=y.cells[r][c]) 
                                  for r in range(min(out.h,y.h)) 
                                  for c in range(min(out.w,y.w))))
        return {"score": sum(m==0 for m in mismatches), "mismatches": mismatches}

@dataclass
class Mediator:
    lattice: TruthLattice
    def repair(self, candidates: List[Program], test_grid: Grid) -> Grid:
        outs = [(p, p.run(test_grid)) for p in candidates]
        if not outs: return test_grid
        if all(o[1].cells == outs[0][1].cells for o in outs): return outs[0][1]
        # paradox
        from paradox import Claim
        seed = ParadoxSeed(positive=Claim("prog0_output"), negative=Claim("prog1_output"))
        ev = [
            Evidence("palette0", len(outs[0][1].palette())),
            Evidence("palette1", len(outs[1][1].palette())),
            Evidence("input_palette", len(test_grid.palette()))
        ]
        res = self.lattice.resolve_paradox(seed, evidence=ev,
                                           perspectives=[role_tag("prog0"), role_tag("prog1")],
                                           frames=[frame_measurement_rule()])
        # trivial policy from resolution
        choose = 0 if (res.kind=="complementarity" and len(test_grid.palette())%2==0) else 1
        choose = min(choose, len(outs)-1)
        return outs[choose][1]

@dataclass
class Librarian:
    lattice: TruthLattice
    def store_skill(self, name: str, trains, program: Program):
        # compress to glyph signature
        glyph, spec = self.lattice.glyph_from_cluster(
            name, [], []  # you can feed text corpus from ops instead of a subgraph
        )
        return {"name": name, "glyph": spec.get("glyph",""), "ops": [op.name for op in program.ops]}

@dataclass
class Coach:
    def adjust(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        # tweak search params based on recent repairs
        return {"beam": 300 if any(h["repaired"] for h in history[-5:]) else 200}

# Orchestrator
class Team:
    def __init__(self):
        self.lattice = TruthLattice()
        self.explorer = Explorer()
        self.synth = Synthesizer()
        self.critic = Critic()
        self.mediator = Mediator(self.lattice)
        self.librarian = Librarian(self.lattice)
        self.coach = Coach()
        self.history = []

    def solve(self, task: Dict[str, Any]) -> List[Grid]:
        obs = self.explorer.perceive(task)
        trains = obs["trains"]
        params = self.coach.adjust(self.history)
        cands = self.synth.propose(trains, max_len=5, beam=params["beam"])
        perfect = [p for p in cands if all(p.run(x).cells == y.cells for x,y in trains)]
        chosen = (perfect or cands)[:2]

        outputs = []
        for ex in task["test"]:
            g = Grid(ex["input"])
            out = chosen[0].run(g) if len(chosen)==1 else self.mediator.repair(chosen, g)
            outputs.append(out)

        # log a tiny event
        solved = len(perfect)>0
        self.history.append({"solved": solved, "repaired": len(chosen)>1 and not solved})
        if solved:
            self.librarian.store_skill("win", trains, perfect[0])
        return outputs