# arc_dsl.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Dict, Callable, Optional, Iterable, Any, Set
from collections import deque, Counter
import itertools

Color = int
GridT = List[List[Color]]

def _check_rect(cells: GridT) -> None:
    if not cells:
        return
    w = len(cells[0])
    if any(len(r) != w for r in cells):
        raise ValueError("non-rectangular grid")

@dataclass(frozen=True)
class Grid:
    """
    Immutable 2D grid, values are small ints [0..9] per ARC convention.
    """
    cells: GridT

    def __post_init__(self):
        _check_rect(self.cells)
        h = len(self.cells)
        w = len(self.cells[0]) if h else 0
        object.__setattr__(self, "h", h)
        object.__setattr__(self, "w", w)

    # --- basic access/traits ---

    def at(self, r: int, c: int) -> Color:
        return self.cells[r][c]

    def eq(self, other: "Grid") -> bool:
        return self.cells == other.cells

    def palette(self) -> Set[Color]:
        return {v for row in self.cells for v in row}

    def hist(self) -> Counter:
        return Counter(v for row in self.cells for v in row)

    def count(self, color: Color) -> int:
        return self.hist()[color]

    def copy(self) -> "Grid":
        return Grid([row[:] for row in self.cells])

    def map(self, fn: Callable[[Color], Color]) -> "Grid":
        return Grid([[fn(v) for v in row] for row in self.cells])

    def with_cell(self, r: int, c: int, v: Color) -> "Grid":
        m = [row[:] for row in self.cells]
        m[r][c] = v
        return Grid(m)

    # --- transforms ---

    def rotate90(self) -> "Grid":
        return Grid([list(reversed(col)) for col in zip(*self.cells)])

    def rotate180(self) -> "Grid":
        return self.rotate90().rotate90()

    def rotate270(self) -> "Grid":
        return self.rotate180().rotate90()

    def flip_h(self) -> "Grid":
        return Grid([list(reversed(row)) for row in self.cells])

    def flip_v(self) -> "Grid":
        return Grid(list(reversed(self.cells)))

    def transpose(self) -> "Grid":
        return Grid([list(col) for col in zip(*self.cells)])

    def crop(self, r0: int, c0: int, r1: int, c1: int) -> "Grid":
        r0 = max(0, r0); c0 = max(0, c0)
        r1 = min(self.h, r1); c1 = min(self.w, c1)
        if r0 >= r1 or c0 >= c1:
            return Grid([[0]])
        return Grid([row[c0:c1] for row in self.cells[r0:r1]])

    def pad(self, top: int, left: int, bottom: int, right: int, fill: Color = 0) -> "Grid":
        new_h = max(0, self.h + top + bottom)
        new_w = max(0, self.w + left + right)
        out = [[fill for _ in range(new_w)] for _ in range(new_h)]
        for r in range(self.h):
            for c in range(self.w):
                rr, cc = r + top, c + left
                if 0 <= rr < new_h and 0 <= cc < new_w:
                    out[rr][cc] = self.cells[r][c]
        return Grid(out)

    # --- compositional pasting/tiling ---

    def paste(self, fg: "Grid", r0: int, c0: int, transparent: Optional[Color] = None) -> "Grid":
        out = [row[:] for row in self.cells]
        for r in range(fg.h):
            for c in range(fg.w):
                v = fg.cells[r][c]
                if transparent is not None and v == transparent:
                    continue
                rr, cc = r0 + r, c0 + c
                if 0 <= rr < self.h and 0 <= cc < self.w:
                    out[rr][cc] = v
        return Grid(out)

    def tile(self, times_r: int, times_c: int) -> "Grid":
        out = []
        for _ in range(times_r):
            for row in self.cells:
                out.append(row * times_c)
        return Grid(out)

    # --- components & morphology ---

    def components(self, bg: Optional[Color] = None, connectivity: int = 4) -> List["Component"]:
        seen = [[False]*self.w for _ in range(self.h)]
        comps: List[Component] = []
        nbrs = [(1,0),(-1,0),(0,1),(0,-1)] if connectivity == 4 else \
               [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
        for r in range(self.h):
            for c in range(self.w):
                v = self.cells[r][c]
                if (bg is not None and v == bg) or seen[r][c]:
                    continue
                q = deque([(r,c)])
                seen[r][c] = True
                pixels = []
                while q:
                    rr, cc = q.popleft()
                    pixels.append((rr,cc,self.cells[rr][cc]))
                    for dr,dc in nbrs:
                        nr, nc = rr+dr, cc+dc
                        if 0 <= nr < self.h and 0 <= nc < self.w and not seen[nr][nc]:
                            if bg is None or self.cells[nr][nc] != bg:
                                seen[nr][nc] = True
                                q.append((nr,nc))
                comps.append(Component(self, pixels))
        return comps

    def flood_fill(self, r: int, c: int, new: Color) -> "Grid":
        target = self.at(r,c)
        if target == new:
            return self
        out = [row[:] for row in self.cells]
        q = deque([(r,c)])
        out[r][c] = new
        nbrs = [(1,0),(-1,0),(0,1),(0,-1)]
        while q:
            rr, cc = q.popleft()
            for dr, dc in nbrs:
                nr, nc = rr+dr, cc+dc
                if 0 <= nr < self.h and 0 <= nc < self.w and out[nr][nc] == target:
                    out[nr][nc] = new
                    q.append((nr,nc))
        return Grid(out)

    def dilate(self, bg: Color = 0) -> "Grid":
        out = [row[:] for row in self.cells]
        nbrs = [(1,0),(-1,0),(0,1),(0,-1)]
        for r in range(self.h):
            for c in range(self.w):
                if self.cells[r][c] != bg:
                    continue
                # if any neighbor non-bg, expand
                for dr, dc in nbrs:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < self.h and 0 <= nc < self.w and self.cells[nr][nc] != bg:
                        out[r][c] = self.cells[nr][nc]
                        break
        return Grid(out)

    def erode(self, bg: Color = 0) -> "Grid":
        out = [row[:] for row in self.cells]
        nbrs = [(1,0),(-1,0),(0,1),(0,-1)]
        for r in range(self.h):
            for c in range(self.w):
                if self.cells[r][c] == bg:
                    continue
                # if any neighbor bg, shrink
                for dr, dc in nbrs:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < self.h and 0 <= nc < self.w and self.cells[nr][nc] == bg:
                        out[r][c] = bg
                        break
        return Grid(out)

    # --- bounding boxes & masks ---

    def bbox_of_color(self, color: Color) -> Tuple[int,int,int,int]:
        coords = [(r,c) for r in range(self.h) for c in range(self.w) if self.cells[r][c] == color]
        if not coords:
            return (0,0,1,1)
        rs = [r for r,_ in coords]; cs = [c for _,c in coords]
        return (min(rs), min(cs), max(rs)+1, max(cs)+1)

    def mask_color(self, color: Color, fill: Color = 1, else_as: Color = 0) -> "Grid":
        return self.map(lambda v: fill if v == color else else_as)

    # --- symmetry hints (coarse) ---

    def is_h_symmetric(self) -> bool:
        return self.cells == self.flip_h().cells

    def is_v_symmetric(self) -> bool:
        return self.cells == self.flip_v().cells

    def best_rotation_to_match(self, other: "Grid") -> int:
        cands = [self, self.rotate90(), self.rotate180(), self.rotate270()]
        for k, g in enumerate(cands):
            if g.cells == other.cells:
                return k
        return 0


@dataclass(frozen=True)
class Component:
    grid: Grid
    pixels: List[Tuple[int,int,Color]]  # (r,c,v)

    def bbox(self) -> Tuple[int,int,int,int]:
        rs = [r for r,_,_ in self.pixels]
        cs = [c for _,c,_ in self.pixels]
        return min(rs), min(cs), max(rs)+1, max(cs)+1  # r0,c0,r1,c1 (exclusive)

    def to_mask(self, fill: Color = 0) -> Grid:
        r0,c0,r1,c1 = self.bbox()
        out = [[fill for _ in range(c1-c0)] for _ in range(r1-r0)]
        for r,c,v in self.pixels:
            out[r-r0][c-c0] = v
        return Grid(out)


# ---------- helpers ----------

def until_fixed_point(g: Grid, op: Callable[[Grid], Grid], max_steps: int = 20) -> Grid:
    prev = g
    for _ in range(max_steps):
        nxt = op(prev)
        if nxt.cells == prev.cells:
            return nxt
        prev = nxt
    return prev

def remap_colors(g: Grid, mapping: Dict[Color, Color]) -> Grid:
    return g.map(lambda v: mapping.get(v, v))

def threshold(g: Grid, keep: Set[Color], keep_as: Color = 1, else_as: Color = 0) -> Grid:
    return g.map(lambda v: keep_as if v in keep else else_as)

def rotate_to(g: Grid, k: int) -> Grid:
    k %= 4
    return [g, g.rotate90(), g.rotate180(), g.rotate270()][k]

def reflect(g: Grid, axis: str) -> Grid:
    return g.flip_h() if axis == "h" else g.flip_v()

def largest_component_mask(g: Grid, bg: Optional[Color] = 0) -> Grid:
    comps = g.components(bg=bg)
    if not comps:
        return g
    comp = max(comps, key=lambda c: len(c.pixels))
    return comp.to_mask(fill=0)

def best_palette_mapping(src: Grid, tgt: Grid, limit: int = 5) -> Dict[Color, Color]:
    """
    Brute-force small palette permutation to minimize mismatches.
    If palettes are big, fall back to greedy by frequency.
    """
    sp = list(src.palette())
    tp = list(tgt.palette())
    k = min(len(sp), len(tp))
    sp = sp[:limit]; tp = tp[:limit]
    best_map, best_err = {}, 10**9
    for perm in itertools.permutations(tp, k):
        m = {sp[i]: perm[i] for i in range(k)}
        # error = cells that wouldn't match after remap
        err = 0
        for r in range(min(src.h, tgt.h)):
            for c in range(min(src.w, tgt.w)):
                if m.get(src.at(r,c), src.at(r,c)) != tgt.at(r,c):
                    err += 1
        if err < best_err:
            best_err, best_map = err, m
    if best_map:
        return best_map
    # greedy fallback
    sh, th = src.hist(), tgt.hist()
    sp_sorted = [c for c,_ in sh.most_common(limit)]
    tp_sorted = [c for c,_ in th.most_common(limit)]
    return {s:t for s,t in zip(sp_sorted, tp_sorted)}