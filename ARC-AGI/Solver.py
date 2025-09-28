# solver.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Callable, Optional, Any
import heapq
import itertools

from arc_dsl import Grid
from arc_ops import Op, Program, generate_ops

# Lattice stack
from truth_lattice import TruthLattice
from paradox import ParadoxSeed, Evidence, frame_measurement_rule, role_tag

# -----------------------------
# Task schema:
#   task = {
#     "train": [{"input": [[...]], "output": [[...]]}, ...],
#     "test":  [{"input": [[...]]}, ...]
#   }
# -----------------------------

# ---------- scoring & invariants ----------

@dataclass
class Score:
    matches: int
    cost: float
    def key(self):  # higher is better for matches, lower cost breaks ties
        return (self.matches, -self.cost)

def program_score(p: Program, pairs: List[Tuple[Grid,Grid]]) -> Score:
    matches = 0
    for x,y in pairs:
        if p.run(x).cells == y.cells:
            matches += 1
    return Score(matches, p.cost())

def palette_mismatch(p: Program, pairs: List[Tuple[Grid,Grid]]) -> bool:
    # If all ops preserve palette and some example changes palette -> impossible
    if all(o.palette_preserved for o in p.ops) and any(x.palette() != y.palette() for x,y in pairs):
        return True
    return False

def area_mismatch(p: Program, pairs: List[Tuple[Grid,Grid]]) -> bool:
    if all(o.area_preserved for o in p.ops) and any(x.h*x.w != y.h*y.w for x,y in pairs):
        return True
    return False

def early_violation(p: Program, pairs: List[Tuple[Grid,Grid]], limit_examples: int = 2) -> bool:
    # Cheap partial run on first few examples; if already wrong on easy invariants, prune.
    for x,y in pairs[:limit_examples]:
        out = p.run(x)
        # trivial impossibilities
        if len(out.palette()) > 10:  # ARC palette bound
            return True
        # if area should match but doesn't
        if all(o.area_preserved for o in p.ops) and (out.h*out.w != x.h*x.w):
            return True
    return False

# ---------- A* search over programs ----------

@dataclass(order=True)
class PQItem:
    priority: float
    score: Tuple[int, float] = field(compare=False)
    program: Program = field(compare=False)

def a_star_search(pairs: List[Tuple[Grid,Grid]], max_len: int = 5, beam: int = 200) -> List[Program]:
    ops = generate_ops(pairs)
    # open set prioritized by heuristic: -matches + tiny cost
    start = Program([])
    best: List[Program] = []
    pq: List[PQItem] = []
    base_score = program_score(start, pairs)
    heapq.heappush(pq, PQItem(priority= -base_score.matches + 0.01*start.cost(), score=base_score.key(), program=start))

    seen = set()
    while pq and len(best) < beam:
        item = heapq.heappop(pq)
        prog = item.program

        # Evaluate full score; if perfect on all examples, keep
        sc = program_score(prog, pairs)
        if sc.matches == len(pairs):
            best.append(prog)
            continue

        if len(prog.ops) >= max_len:
            continue

        # Prune by static invariants
        if palette_mismatch(prog, pairs) or area_mismatch(prog, pairs) or early_violation(prog, pairs):
            continue

        # Expand
        for op in ops:
            new_ops = tuple(o.name for o in (prog.ops + [op]))
            if new_ops in seen:
                continue
            seen.add(new_ops)

            child = Program(prog.ops + [op])
            # quick partial check on one example to guide priority
            partial = 0
            try:
                x0,y0 = pairs[0]
                if child.run(x0).cells == y0.cells:
                    partial = 1
            except Exception:
                continue
            # Priority: prefer higher matches; small cost; and partial hit
            score = program_score(child, pairs)
            priority = -(score.matches + 0.25*partial) + 0.01*child.cost()
            heapq.heappush(pq, PQItem(priority=priority, score=score.key(), program=child))

    # If none perfect found, return top few by score
    if not best:
        # harvest the best few explored (not tracked in this simple loop), so re-enumerate cheaply
        # Fallback: enumerate short programs and rank (beam search style)
        return beam_search_fallback(pairs, ops, max_len=max_len, beam=beam)
    return best[:beam]

def beam_search_fallback(pairs: List[Tuple[Grid,Grid]], ops: List[Op], max_len: int = 4, beam: int = 200) -> List[Program]:
    pool = [Program([])]
    for _ in range(max_len):
        cand = []
        for p in pool:
            for op in ops:
                q = Program(p.ops + [op])
                if palette_mismatch(q, pairs) or area_mismatch(q, pairs) or early_violation(q, pairs):
                    continue
                cand.append(q)
        cand.sort(key=lambda P: program_score(P, pairs).key(), reverse=True)
        pool = cand[:beam]
    pool.sort(key=lambda P: program_score(P, pairs).key(), reverse=True)
    return pool[:beam]


# ---------- Paradox-based tie-breaking ----------

def paradox_repair(lattice: TruthLattice, candidates: List[Program], test_grid: Grid) -> Grid:
    outs: List[Tuple[Program, Grid]] = []
    for p in candidates:
        try:
            outs.append((p, p.run(test_grid)))
        except Exception:
            continue
    if not outs:
        return test_grid

    # unanimous → done
    ref = outs[0][1]
    if all(o[1].cells == ref.cells for o in outs):
        return ref

    # Build paradox with minimal claims
    seed = ParadoxSeed(
        positive=lattice.paradox.chamber.__annotations__ and lattice.paradox.chamber,  # dummy poke for type hints
        # We’ll construct simple textual claims via helper below
        positive=None,  # type: ignore
        negative=None   # type: ignore
    )  # we'll replace via helper to avoid importing Claim directly here

    # create simple claims without importing Claim (keep loose coupling)
    from paradox import Claim
    seed = ParadoxSeed(positive=Claim("prog0_output"), negative=Claim("prog1_output"))

    evidence = [
        Evidence("palette_size_prog0", len(outs[0][1].palette())),
        Evidence("palette_size_prog1", len(outs[1][1].palette())),
        Evidence("input_palette_size", len(test_grid.palette())),
    ]
    res = lattice.resolve_paradox(
        seed=seed,
        evidence=evidence,
        perspectives=[role_tag("prog0"), role_tag("prog1")],
        frames=[frame_measurement_rule()],
    )
    # Heuristics based on resolution kind
    choose = 0
    if res.kind == "complementarity":
        cond = (len(test_grid.palette()) % 2 == 0)
        choose = 0 if cond else 1
    elif res.kind == "redefine-terms":
        # Prefer lower-cost program under lexical alignment
        choose = 0 if outs[0][0].cost() <= outs[1][0].cost() else 1
    else:
        # Majority-by-similarity fallback: pick output closest to first by palette
        p0 = len(outs[0][1].palette())
        p1 = len(outs[1][1].palette())
        choose = 0 if abs(p0 - len(test_grid.palette())) <= abs(p1 - len(test_grid.palette())) else 1
    return outs[min(choose, len(outs)-1)][1]


# ---------- Public API ----------

def solve_task(task: Dict[str, Any], lattice: Optional[TruthLattice] = None, topk: int = 5) -> List[Grid]:
    lattice = lattice or TruthLattice()

    # Parse
    train_pairs: List[Tuple[Grid,Grid]] = [(Grid(ex["input"]), Grid(ex["output"])) for ex in task["train"]]
    tests: List[Grid] = [Grid(ex["input"]) for ex in task["test"]]

    # Search
    candidates = a_star_search(train_pairs, max_len=5, beam=200)
    # Keep the ones that fit all train examples if possible
    perfect = [p for p in candidates if all(p.run(x).cells == y.cells for x,y in train_pairs)]
    chosen = (perfect or candidates)[:topk]

    # Inference
    outputs: List[Grid] = []
    for g in tests:
        if len(chosen) == 1:
            outputs.append(chosen[0].run(g))
        else:
            outputs.append(paradox_repair(lattice, chosen[:2], g))
    return outputs


# ---------- Batch runner ----------

def solve_tasks(tasks: List[Dict[str, Any]], lattice: Optional[TruthLattice] = None) -> List[List[Grid]]:
    return [solve_task(t, lattice=lattice) for t in tasks]