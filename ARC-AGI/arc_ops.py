# arc_ops.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple, Any, Optional, Set
import itertools

from arc_dsl import (
    Grid, Color, remap_colors, threshold, rotate_to, reflect,
    largest_component_mask, until_fixed_point, best_palette_mapping
)

# ============ Operation primitives ============

@dataclass(frozen=True)
class Op:
    name: str
    apply: Callable[[Grid], Grid]
    cost: float = 1.0
    # invariants used for pruning/search guidance
    palette_preserved: bool = False
    area_preserved: bool = True   # most transforms keep area unless crop/pad/tile
    monotone_pixels: bool = True  # non-destructive color overwrite? (heuristic)

    def __str__(self) -> str:
        return self.name

@dataclass
class Program:
    ops: List[Op]
    def run(self, g: Grid) -> Grid:
        for op in self.ops:
            g = op.apply(g)
        return g
    def cost(self) -> float:
        return sum(op.cost for op in self.ops)
    def __str__(self) -> str:
        return " ∘ ".join(op.name for op in self.ops) if self.ops else "ID"


# ============ Parameter sources from training ============

@dataclass(frozen=True)
class TrainStats:
    input_pal: Set[Color]
    output_pal: Set[Color]
    area_eq_all: bool
    palette_eq_all: bool

def compute_stats(pairs: List[Tuple[Grid, Grid]]) -> TrainStats:
    in_pal = set().union(*[x.palette() for x,_ in pairs])
    out_pal = set().union(*[y.palette() for _,y in pairs])
    area_eq = all(x.h * x.w == y.h * y.w for x,y in pairs)
    pal_eq = all(x.palette() == y.palette() for x,y in pairs)
    return TrainStats(in_pal, out_pal, area_eq_all=area_eq, palette_eq_all=pal_eq)


# ============ Parameterized factories ============

def primitives_always() -> List[Op]:
    ops: List[Op] = []
    # Identity (cheap)
    ops.append(Op("id", lambda g: g, cost=0.05, palette_preserved=True))
    # Rotations
    for k in range(4):
        ops.append(Op(f"rot{k}", lambda g, kk=k: rotate_to(g, kk), cost=0.6 if k else 0.1, palette_preserved=True))
    # Reflections
    ops += [
        Op("flip_h", lambda g: reflect(g, "h"), cost=0.7, palette_preserved=True),
        Op("flip_v", lambda g: reflect(g, "v"), cost=0.7, palette_preserved=True),
    ]
    # Largest component mask (not palette preserving)
    ops.append(Op("largest_comp", lambda g: largest_component_mask(g, bg=0), cost=1.2, palette_preserved=False, area_preserved=False))
    return ops

def threshold_ops(pairs: List[Tuple[Grid,Grid]], max_colors: int = 4) -> List[Op]:
    # keep a few strong colors observed in inputs
    pal = []
    for x,_ in pairs:
        pal.extend(list(x.palette()))
    keepers = list(dict.fromkeys(pal))[:max_colors]  # unique, keep order
    ops = []
    for c in keepers:
        name = f"thresh=={c}"
        ops.append(Op(name, lambda g, cc=c: threshold(g, {cc}, keep_as=1, else_as  =0), cost=1.0,
                      palette_preserved=False, area_preserved=True, monotone_pixels=True))
    return ops

def color_remap_ops(pairs: List[Tuple[Grid,Grid]], limit: int = 5) -> List[Op]:
    # bind a few plausible palette permutations from the training pairs
    ops = []
    for i, (x, y) in enumerate(pairs[:3]):  # use first few for hints
        mapping = best_palette_mapping(x, y, limit=limit)
        if mapping:
            ops.append(Op(f"remap#{i}:{mapping}", lambda g, m=mapping: remap_colors(g, m), cost=1.1,
                          palette_preserved=False))
    return ops

def fixed_point_ops() -> List[Op]:
    # placeholder for closure-type rules; identity closure does nothing but establishes framework
    return [Op("fixed(id)", lambda g: until_fixed_point(g, lambda z: z, max_steps=3), cost=0.2)]

def tiling_ops() -> List[Op]:
    # lightweight tilers; ARC puzzles sometimes replicate motifs
    from arc_dsl import Grid
    def _tile2(g: Grid) -> Grid: return g.tile(2,2)
    def _tile3(g: Grid) -> Grid: return g.tile(3,3)
    return [
        Op("tile2x2", _tile2, cost=1.4, area_preserved=False),
        Op("tile3x3", _tile3, cost=1.7, area_preserved=False),
    ]

# ============ Op generator ============

def generate_ops(pairs: List[Tuple[Grid,Grid]]) -> List[Op]:
    stats = compute_stats(pairs)
    ops = []
    ops.extend(primitives_always())
    ops.extend(threshold_ops(pairs))
    ops.extend(color_remap_ops(pairs))
    ops.extend(fixed_point_ops())
    ops.extend(tiling_ops())
    # If all examples preserve area, slightly prefer area-preserving ops by cost nudging
    if stats.area_eq_all:
        ops = [Op(o.name, o.apply, max(0.05, o.cost * (0.9 if o.area_preserved else 1.05)),
                  o.palette_preserved, o.area_preserved, o.monotone_pixels) for o in ops]
    return ops