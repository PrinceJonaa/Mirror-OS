# relational.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Protocol, Set, Tuple
from collections import defaultdict, deque
import time


# ---------- Core Types ----------

class Predicate(Protocol):
    def __call__(self, a: "Entity", b: "Entity", ctx: Optional["Context"] = None) -> bool: ...


@dataclass(frozen=True)
class Entity:
    """An entity node in the relational field."""
    id: str
    label: str = ""
    attrs: Dict[str, object] = field(default_factory=dict)


@dataclass
class Relation:
    """
    A binary relation on Entity x Entity with an optional predicate.
    If predicate is None, the relation is treated as a named edge set stored in the graph.
    """
    name: str
    predicate: Optional[Predicate] = None
    symmetric: bool = False
    reflexive: bool = False
    transitive: bool = False
    weight: float = 1.0  # used by gravity metrics

    def holds(self, a: Entity, b: Entity, ctx: Optional["Context"] = None) -> bool:
        if self.predicate is None:
            raise ValueError(f"Relation {self.name} has no predicate. Use graph.has_edge for stored edges.")
        return bool(self.predicate(a, b, ctx))


@dataclass
class Context:
    """Execution frame for relation evaluation."""
    description: str = ""
    constraints: Dict[str, object] = field(default_factory=dict)


Triple = Tuple[Entity, Relation, Entity]


# ---------- Knowledge Graph ----------

class KnowledgeGraph:
    """
    A light relational store supporting asserted edges and evaluated relations.
    Time-stamped history supports stillness diagnostics.
    """
    def __init__(self) -> None:
        self.entities: Dict[str, Entity] = {}
        self.edges: Dict[str, Set[Tuple[str, str]]] = defaultdict(set)  # relation.name -> {(a.id, b.id)}
        self.history: List[Tuple[float, str, str, str, str]] = []  # (ts, op, rel, a.id, b.id)

    # -- Entity management --

    def add_entity(self, e: Entity) -> None:
        self.entities[e.id] = e

    def get(self, id: str) -> Entity:
        return self.entities[id]

    # -- Edge assertions --

    def assert_edge(self, rel: Relation, a: Entity, b: Entity, ts: Optional[float] = None) -> None:
        if rel.predicate is not None:
            raise ValueError("Cannot assert edges for predicate-based relations. Derive edges by evaluation instead.")
        self.edges[rel.name].add((a.id, b.id))
        if rel.symmetric:
            self.edges[rel.name].add((b.id, a.id))
        if ts is None:
            ts = time.time()
        self.history.append((ts, "assert", rel.name, a.id, b.id))

    def retract_edge(self, rel: Relation, a: Entity, b: Entity, ts: Optional[float] = None) -> None:
        self.edges[rel.name].discard((a.id, b.id))
        if ts is None:
            ts = time.time()
        self.history.append((ts, "retract", rel.name, a.id, b.id))

    def has_edge(self, rel: Relation, a: Entity, b: Entity) -> bool:
        if rel.predicate is None:
            return (a.id, b.id) in self.edges[rel.name]
        return rel.holds(a, b)

    def neighbors(self, rel: Relation, a: Entity) -> Iterable[Entity]:
        if rel.predicate is None:
            for aid, bid in self.edges[rel.name]:
                if aid == a.id:
                    yield self.entities[bid]
        else:
            for e in self.entities.values():
                if rel.holds(a, e):
                    yield e

    # -- Graph utilities --

    def degree(self, rel: Relation, a: Entity) -> int:
        return sum(1 for _ in self.neighbors(rel, a))

    def path_exists(self, rel: Relation, src: Entity, dst: Entity, max_depth: int = 6) -> bool:
        """BFS on a single relation. For transitive reasoning and cycle checks."""
        seen = {src.id}
        q: deque[Entity] = deque([src])
        depth = 0
        while q and depth <= max_depth:
            for _ in range(len(q)):
                node = q.popleft()
                if node.id == dst.id:
                    return True
                for nxt in self.neighbors(rel, node):
                    if nxt.id not in seen:
                        seen.add(nxt.id)
                        q.append(nxt)
            depth += 1
        return False

    # -- Stillness diagnostics --

    def stillness(self, a: Entity, window_sec: float, relation_name: Optional[str] = None) -> float:
        """
        Returns 1.0 if no edge changes for entity a in the given time window.
        Returns value in [0,1] scaling down with number of changes.
        """
        now = time.time()
        lo = now - window_sec
        changes = 0
        for ts, op, rel, aid, bid in self.history:
            if ts >= lo and (aid == a.id or bid == a.id) and (relation_name in (None, rel)):
                changes += 1
        if changes == 0:
            return 1.0
        return max(0.0, 1.0 / (1.0 + 0.5 * changes))

    # -- Relational gravity --

    def gravity(self, a: Entity, relations: List[Relation]) -> float:
        """
        Gravity is a weighted degree centrality across given relations.
        """
        g = 0.0
        for r in relations:
            g += r.weight * self.degree(r, a)
        return g


# ---------- Operators ----------

def inverse(R: Relation) -> Relation:
    return Relation(
        name=f"{R.name}^-1",
        predicate=(None if R.predicate is None else lambda a, b, ctx=None: R.holds(b, a, ctx)),
        symmetric=R.symmetric,
        reflexive=R.reflexive,
        transitive=R.transitive,
        weight=R.weight,
    )


def union(R: Relation, S: Relation) -> Relation:
    def pred(a: Entity, b: Entity, ctx: Optional[Context] = None) -> bool:
        lhs = R.holds(a, b, ctx) if R.predicate else False
        rhs = S.holds(a, b, ctx) if S.predicate else False
        return lhs or rhs
    # For edge relations without predicates, union requires a graph-level operation.
    return Relation(name=f"{R.name} ∪ {S.name}", predicate=pred)


def intersect(R: Relation, S: Relation) -> Relation:
    def pred(a: Entity, b: Entity, ctx: Optional[Context] = None) -> bool:
        lhs = R.holds(a, b, ctx) if R.predicate else False
        rhs = S.holds(a, b, ctx) if S.predicate else False
        return lhs and rhs
    return Relation(name=f"{R.name} ∩ {S.name}", predicate=pred)


def compose(R: Relation, S: Relation, graph: KnowledgeGraph) -> Relation:
    """
    (S ∘ R)(a, c) holds if there exists b such that R(a,b) and S(b,c).
    Works with predicate relations or stored edges via graph.
    """
    def pred(a: Entity, c: Entity, ctx: Optional[Context] = None) -> bool:
        if R.predicate is None:
            candidates = [graph.get(bid) for aid, bid in graph.edges[R.name] if aid == a.id]
        else:
            candidates = [b for b in graph.entities.values() if R.holds(a, b, ctx)]
        for b in candidates:
            if S.predicate is None:
                if (b.id, c.id) in graph.edges[S.name]:
                    return True
            else:
                if S.holds(b, c, ctx):
                    return True
        return False
    return Relation(name=f"{S.name} ∘ {R.name}", predicate=pred)


def restrict(R: Relation, ctx_filter: Callable[[Entity, Entity, Optional[Context]], bool]) -> Relation:
    def pred(a: Entity, b: Entity, ctx: Optional[Context] = None) -> bool:
        if not ctx_filter(a, b, ctx):
            return False
        return R.holds(a, b, ctx) if R.predicate else False
    return Relation(name=f"{R.name}|ctx", predicate=pred)


# ---------- Axioms and Checks ----------

def axiom_identity_reflexive(graph: KnowledgeGraph, identity: Relation) -> bool:
    ok = True
    for e in graph.entities.values():
        try:
            if not identity.holds(e, e):
                ok = False
        except Exception:
            ok = False
    return ok


def check_antisymmetry(graph: KnowledgeGraph, rel: Relation) -> bool:
    """
    Antisymmetry for partial order candidate: if aRb and bRa then a == b.
    Only checks asserted edges for non predicate relations.
    """
    if rel.predicate is not None:
        return True
    for aid, bid in graph.edges[rel.name]:
        if (bid, aid) in graph.edges[rel.name] and aid != bid:
            return False
    return True


def check_acyclic(graph: KnowledgeGraph, rel: Relation) -> bool:
    """
    Detect cycles on directed edges for a given relation using DFS.
    Only for non predicate relations.
    """
    if rel.predicate is not None:
        return True
    adj: Dict[str, List[str]] = defaultdict(list)
    for aid, bid in graph.edges[rel.name]:
        adj[aid].append(bid)

    temp: Set[str] = set()
    perm: Set[str] = set()

    def dfs(u: str) -> bool:
        if u in perm:
            return True
        if u in temp:
            return False
        temp.add(u)
        for v in adj.get(u, []):
            if not dfs(v):
                return False
        temp.remove(u)
        perm.add(u)
        return True

    return all(dfs(node) for node in list(adj.keys()))


# ---------- Minimal Demo ----------

def _demo() -> None:
    print("Relational 1.0 demo")
    g = KnowledgeGraph()

    # Entities
    alice = Entity("alice", "Alice")
    bob = Entity("bob", "Bob")
    carol = Entity("carol", "Carol")
    for e in (alice, bob, carol):
        g.add_entity(e)

    # Predicate relation: identity
    identity = Relation("Identity", predicate=lambda a, b, ctx=None: a.id == b.id, reflexive=True, symmetric=True)
    print("Identity reflexive axiom:", axiom_identity_reflexive(g, identity))

    # Stored edge relation: friendOf (symmetric)
    friend = Relation("friendOf", predicate=None, symmetric=True, weight=1.0)
    g.assert_edge(friend, alice, bob)
    g.assert_edge(friend, bob, carol)

    # Stored edge relation: parentOf (not symmetric, acyclic required)
    parent = Relation("parentOf", predicate=None, weight=2.0)
    g.assert_edge(parent, alice, carol)  # Alice is parent of Carol

    print("friendOf edges:", g.edges["friendOf"])
    print("parentOf edges:", g.edges["parentOf"])
    print("Check acyclicity parentOf:", check_acyclic(g, parent))

    # Compose: grandparentOf := parentOf ∘ parentOf
    grandparent = compose(parent, parent, g)
    print("Is Alice grandparent of anyone?", any(grandparent.holds(alice, x) for x in g.entities.values()))

    # Inverse and union
    childOf = inverse(parent)
    kin = union(parent, childOf)
    print("Alice has kin with Carol:", kin.holds(alice, carol))

    # Gravity metric
    grav_alice = g.gravity(alice, [friend, parent])
    grav_bob = g.gravity(bob, [friend, parent])
    print("Gravity Alice:", grav_alice, "Gravity Bob:", grav_bob)

    # Stillness after a change
    s1 = g.stillness(alice, window_sec=5.0)
    g.retract_edge(friend, alice, bob)
    s2 = g.stillness(alice, window_sec=5.0)
    print("Stillness before:", s1, "after:", s2)


if __name__ == "__main__":
    _demo()