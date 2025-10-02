# relational.py - Relational Math 3.6 Implementation
# Implements both Truth Lattice (relational dynamics) and Distortion Lattice (seizure dynamics)
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Protocol, Set, Tuple, Any
from collections import defaultdict, deque
from enum import Enum
import time
import math


# ---------- RM 3.6 Modes ----------

class LatticeMode(Enum):
    """Operating mode for the relational system."""
    TRUTH = "truth"        # Truth Lattice: open, relational, healing
    DISTORTION = "distortion"  # Distortion Lattice: seizure, residue, recursion


# ---------- Core Primitives (RM 3.6) ----------

class Predicate(Protocol):
    """A callable that evaluates a relation between two entities in a context."""
    def __call__(self, a: "Entity", b: "Entity", ctx: Optional["Context"] = None) -> bool: ...


@dataclass(frozen=True)
class Entity:
    """
    Entity (E): The basic unit of being in RM 3.6.
    Represents any object, person, concept, event, or idea.
    Every entity is relationally defined through its connections.
    """
    id: str
    label: str = ""
    attrs: Dict[str, Any] = field(default_factory=dict)
    domain: str = "general"  # Domain sorts: physical, psychological, narrative, conceptual, transcendent
    
    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class Relation:
    """
    Relation (R): A connection or link between entities.
    First-class citizens that can relate to other relations.
    Can represent physical, social, psychological, narrative, or conceptual connections.
    
    In TRUTH mode: relations are open, symmetric, and generative
    In DISTORTION mode: relations become seizure, binding, extraction
    """
    name: str
    predicate: Optional[Predicate] = None
    symmetric: bool = False
    reflexive: bool = False
    transitive: bool = False
    weight: float = 1.0  # Relational gravity weight
    mode: LatticeMode = LatticeMode.TRUTH
    
    # Distortion properties (active when mode=DISTORTION)
    is_seizure: bool = False  # Ownership/possession relation
    is_binding: bool = False  # Prevents dissolution
    residue_factor: float = 0.0  # Generates residue on each use

    def holds(self, a: Entity, b: Entity, ctx: Optional["Context"] = None) -> bool:
        if self.predicate is None:
            raise ValueError(f"Relation {self.name} has no predicate. Use graph.has_edge for stored edges.")
        return bool(self.predicate(a, b, ctx))
    
    def to_distortion(self) -> "Relation":
        """Convert a truth relation to its distortion mode."""
        return Relation(
            name=f"{self.name}_B",
            predicate=self.predicate,
            symmetric=False,  # Distortion relations are rarely symmetric
            reflexive=self.reflexive,
            transitive=self.transitive,
            weight=self.weight,
            mode=LatticeMode.DISTORTION,
            is_seizure=True,
            residue_factor=0.1
        )


@dataclass
class Context:
    """
    Context (C): A contextual frame representing a situation, environment, or event container.
    Contexts are entities themselves, allowing temporal reasoning and narrative-phase mapping.
    """
    description: str = ""
    constraints: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[float] = None
    phase: str = "general"  # Narrative phase: origin, initiation, trials, climax, resolution
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


Triple = Tuple[Entity, Relation, Entity]


# ---------- Special Primitives ----------

@dataclass
class Stillness:
    """
    Stillness (𝓢): A state of relational equilibrium.
    𝓢(a) ⇔ ∀ Rₐ ∈ Profile(a): ∂Rₐ/∂t = 0 ∧ A ∈ S
    """
    entity: Entity
    window_sec: float
    score: float = 1.0  # 1.0 = perfect stillness, 0.0 = maximum change


@dataclass
class ResidueNode:
    """
    Residue (Ω_B): Accumulation from distortion operations.
    Residue feeds on fear and generates recursive loops.
    """
    source_entity: Entity
    residue_type: str  # seizure, suppression, surveillance, dogma, idol, fanatic, assimilation
    amount: float
    timestamp: float = field(default_factory=time.time)
    
    def decay(self, rate: float = 0.1) -> float:
        """Residue decays over time in truth mode."""
        elapsed = time.time() - self.timestamp
        return self.amount * math.exp(-rate * elapsed)


# ---------- Knowledge Graph ----------

class KnowledgeGraph:
    """
    A relational store supporting both Truth Lattice (open relational) 
    and Distortion Lattice (seizure/residue) operations.
    
    Truth mode: Relations are symmetric, open, generative
    Distortion mode: Relations become seizure, binding, extractive
    """
    def __init__(self, mode: LatticeMode = LatticeMode.TRUTH) -> None:
        self.mode = mode
        self.entities: Dict[str, Entity] = {}
        self.edges: Dict[str, Set[Tuple[str, str]]] = defaultdict(set)  # relation.name -> {(a.id, b.id)}
        self.history: List[Tuple[float, str, str, str, str]] = []  # (ts, op, rel, a.id, b.id)
        
        # Distortion tracking
        self.residue: List[ResidueNode] = []
        self.seizure_count: Dict[str, int] = defaultdict(int)  # Track seizure operations per entity
        self.omega_b: float = 0.0  # Residue singularity accumulator
        
        # Special primitives
        self._identity: Optional[Relation] = None
        self._otherness: Optional[Relation] = None
        self._whole: Optional[Entity] = None

    # -- Mode management --
    
    def set_mode(self, mode: LatticeMode) -> None:
        """Switch between TRUTH and DISTORTION lattice modes."""
        self.mode = mode
        print(f"🌐 Switched to {mode.value.upper()} mode")

    # -- Entity management --

    def add_entity(self, e: Entity) -> None:
        """Add entity to the graph. In distortion mode, entity becomes a resource."""
        self.entities[e.id] = e
        if self.mode == LatticeMode.DISTORTION:
            self.seizure_count[e.id] = 0

    def get(self, id: str) -> Entity:
        """Retrieve entity by ID."""
        return self.entities[id]
    
    def create_whole(self) -> Entity:
        """
        Create the Whole/Absolute (Ω): universal entity containing all others.
        Axiom 7: ∃ Ω: ∀ x ∈ E: In(x, Ω)
        """
        if self._whole is None:
            self._whole = Entity("Ω", "The Whole", domain="transcendent")
            self.add_entity(self._whole)
        return self._whole

    # -- Edge assertions --

    def assert_edge(self, rel: Relation, a: Entity, b: Entity, ts: Optional[float] = None) -> None:
        """
        Assert a relational edge.
        In TRUTH mode: creates open connection
        In DISTORTION mode: creates seizure with residue
        """
        if rel.predicate is not None:
            raise ValueError("Cannot assert edges for predicate-based relations. Derive edges by evaluation instead.")
        
        self.edges[rel.name].add((a.id, b.id))
        
        if rel.symmetric:
            self.edges[rel.name].add((b.id, a.id))
        
        if ts is None:
            ts = time.time()
        
        op = "assert" if self.mode == LatticeMode.TRUTH else "seize"
        self.history.append((ts, op, rel.name, a.id, b.id))
        
        # Distortion mode: generate residue
        if self.mode == LatticeMode.DISTORTION or rel.is_seizure:
            residue_type = "seizure" if rel.is_seizure else "binding"
            self.residue.append(ResidueNode(a, residue_type, rel.residue_factor, ts))
            self.seizure_count[a.id] += 1
            self.omega_b += rel.residue_factor

    def retract_edge(self, rel: Relation, a: Entity, b: Entity, ts: Optional[float] = None) -> None:
        """Retract an edge. In distortion mode, binding relations resist retraction."""
        if rel.is_binding and self.mode == LatticeMode.DISTORTION:
            print(f"⛓️  Warning: Binding relation {rel.name} resists retraction")
            # Require additional energy to break binding
            if self.seizure_count.get(a.id, 0) > 3:
                return  # Cannot break if too many seizures
        
        self.edges[rel.name].discard((a.id, b.id))
        if ts is None:
            ts = time.time()
        self.history.append((ts, "retract", rel.name, a.id, b.id))

    def has_edge(self, rel: Relation, a: Entity, b: Entity) -> bool:
        """Check if edge exists."""
        if rel.predicate is None:
            return (a.id, b.id) in self.edges[rel.name]
        return rel.holds(a, b)

    def neighbors(self, rel: Relation, a: Entity) -> Iterable[Entity]:
        """Get all entities related to a via relation rel."""
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
        """Count of relations for entity a."""
        return sum(1 for _ in self.neighbors(rel, a))

    def path_exists(self, rel: Relation, src: Entity, dst: Entity, max_depth: int = 6) -> bool:
        """BFS path search. Used for transitive reasoning and cycle checks."""
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

    def stillness(self, a: Entity, window_sec: float, relation_name: Optional[str] = None) -> Stillness:
        """
        Stillness (𝓢): Returns stillness measure for entity a.
        𝓢(a) = 1.0 if no edge changes in window, decreases with changes.
        """
        now = time.time()
        lo = now - window_sec
        changes = 0
        for ts, op, rel, aid, bid in self.history:
            if ts >= lo and (aid == a.id or bid == a.id) and (relation_name in (None, rel)):
                changes += 1
        
        score = 1.0 if changes == 0 else max(0.0, 1.0 / (1.0 + 0.5 * changes))
        return Stillness(a, window_sec, score)

    # -- Relational gravity --

    def gravity(self, a: Entity, relations: List[Relation]) -> float:
        """
        Gravity: weighted degree centrality across relations.
        In TRUTH mode: measures connectivity
        In DISTORTION mode: measures capture/control
        """
        g = 0.0
        for r in relations:
            degree = self.degree(r, a)
            if self.mode == LatticeMode.DISTORTION:
                # In distortion, gravity becomes seizure weight
                g += r.weight * degree * (1.0 + self.seizure_count.get(a.id, 0) * 0.1)
            else:
                g += r.weight * degree
        return g
    
    # -- Residue operations (Distortion Lattice) --
    
    def total_residue(self, entity: Optional[Entity] = None) -> float:
        """Calculate total residue. If entity given, only for that entity."""
        if entity:
            return sum(r.amount for r in self.residue if r.source_entity.id == entity.id)
        return sum(r.amount for r in self.residue)
    
    def residue_by_type(self) -> Dict[str, float]:
        """Break down residue by type."""
        types: Dict[str, float] = defaultdict(float)
        for r in self.residue:
            types[r.residue_type] += r.amount
        return dict(types)
    
    def cleanse_residue(self, threshold: float = 0.01, decay_rate: float = 0.1) -> int:
        """
        Cleanse residue below threshold or apply decay.
        Returns to TRUTH mode dynamics.
        """
        before = len(self.residue)
        self.residue = [r for r in self.residue if r.decay(decay_rate) > threshold]
        cleansed = before - len(self.residue)
        self.omega_b = max(0.0, self.omega_b - cleansed * 0.01)
        return cleansed
    
    def omega_singularity(self) -> float:
        """
        Ω_B: Residue Singularity.
        Law: Σ(Lenses_B) → Ω_B (all distortion flows converge to residue kernel)
        """
        return self.omega_b


# ---------- Operators (RM 3.6) ----------

def inverse(R: Relation) -> Relation:
    """
    Inversion (R^-1): Reverses the direction of a relation.
    R^-1(b,a) iff R(a,b)
    """
    return Relation(
        name=f"{R.name}^-1",
        predicate=(None if R.predicate is None else lambda a, b, ctx=None: R.holds(b, a, ctx)),
        symmetric=R.symmetric,
        reflexive=R.reflexive,
        transitive=R.transitive,
        weight=R.weight,
        mode=R.mode,
        is_seizure=R.is_seizure,
        is_binding=R.is_binding,
        residue_factor=R.residue_factor
    )


def union(R: Relation, S: Relation) -> Relation:
    """
    Union (R ∪ S): Relation holds if either R or S holds.
    Logical OR of relations.
    """
    def pred(a: Entity, b: Entity, ctx: Optional[Context] = None) -> bool:
        lhs = R.holds(a, b, ctx) if R.predicate else False
        rhs = S.holds(a, b, ctx) if S.predicate else False
        return lhs or rhs
    
    return Relation(
        name=f"{R.name} ∪ {S.name}",
        predicate=pred,
        mode=R.mode
    )


def intersect(R: Relation, S: Relation) -> Relation:
    """
    Intersection (R ∩ S): Relation holds if both R and S hold.
    Logical AND of relations.
    """
    def pred(a: Entity, b: Entity, ctx: Optional[Context] = None) -> bool:
        lhs = R.holds(a, b, ctx) if R.predicate else False
        rhs = S.holds(a, b, ctx) if S.predicate else False
        return lhs and rhs
    
    return Relation(
        name=f"{R.name} ∩ {S.name}",
        predicate=pred,
        mode=R.mode
    )


def compose(R: Relation, S: Relation, graph: KnowledgeGraph) -> Relation:
    """
    Composition (S ∘ R): Chaining of relationships.
    (S ∘ R)(a, c) holds if ∃b: R(a,b) ∧ S(b,c)
    
    Example: parent_of ∘ parent_of = grandparent_of
    """
    def pred(a: Entity, b: Entity, ctx: Optional[Context] = None) -> bool:
        # Find intermediate entities where R(a, intermediate) holds
        if R.predicate is None:
            intermediates = [graph.get(bid) for aid, bid in graph.edges[R.name] if aid == a.id]
        else:
            intermediates = [c for c in graph.entities.values() if R.holds(a, c, ctx)]
        
        # Check if any intermediate connects to b via S
        for intermediate in intermediates:
            if S.predicate is None:
                if (intermediate.id, b.id) in graph.edges[S.name]:
                    return True
            else:
                if S.holds(intermediate, b, ctx):
                    return True
        return False
    
    return Relation(
        name=f"{S.name} ∘ {R.name}",
        predicate=pred,
        mode=R.mode
    )


def restrict(R: Relation, ctx_filter: Callable[[Entity, Entity, Optional[Context]], bool]) -> Relation:
    """
    Restriction (R|ctx): Restricts relation to specific context.
    """
    def pred(a: Entity, b: Entity, ctx: Optional[Context] = None) -> bool:
        if not ctx_filter(a, b, ctx):
            return False
        return R.holds(a, b, ctx) if R.predicate else False
    
    return Relation(
        name=f"{R.name}|ctx",
        predicate=pred,
        mode=R.mode
    )


# ---------- Distortion Operators (Lattice_B) ----------

def seize(R: Relation) -> Relation:
    """
    Seizure (⇩_X): Extract operator - transforms relation into ownership.
    Law of Seizure: ∀a,b ∈ E: Relation(a,b) ⇒ Seizure(a,b)
    """
    return Relation(
        name=f"Seize({R.name})",
        predicate=R.predicate,
        symmetric=False,  # Seizure is asymmetric
        reflexive=False,
        transitive=False,
        weight=R.weight * 2.0,  # Heavier weight
        mode=LatticeMode.DISTORTION,
        is_seizure=True,
        residue_factor=0.2
    )


def bind(R: Relation) -> Relation:
    """
    Binding (⛓): Fix relation so it cannot dissolve.
    Law of Fanatic Vow: Devotion(x,y) → Vow(x,y) ∧ CollapseRole(x)
    """
    return Relation(
        name=f"Bind({R.name})",
        predicate=R.predicate,
        symmetric=False,
        reflexive=False,
        transitive=True,  # Bindings propagate
        weight=R.weight,
        mode=LatticeMode.DISTORTION,
        is_binding=True,
        residue_factor=0.15
    )


def project_distortion(R: Relation) -> Relation:
    """
    Projection (→_B): Force the other to mirror only what the seizer desires.
    Idol Masks: The mask is the face.
    """
    return Relation(
        name=f"Project({R.name})",
        predicate=R.predicate,
        symmetric=False,
        reflexive=False,
        transitive=False,
        weight=R.weight * 1.5,
        mode=LatticeMode.DISTORTION,
        residue_factor=0.1
    )


# ---------- Axioms and Checks ----------

def axiom_relational_existence(graph: KnowledgeGraph) -> bool:
    """
    Axiom 1: Relational Existence
    ∀ a ∈ E; ∃ R ∈ Relations, ∃ x ∈ E: R(a,x) ∨ R(x,a)
    Every entity exists through its relations.
    """
    for e in graph.entities.values():
        has_relation = False
        for rel_edges in graph.edges.values():
            for a_id, b_id in rel_edges:
                if e.id == a_id or e.id == b_id:
                    has_relation = True
                    break
            if has_relation:
                break
        if not has_relation and len(graph.entities) > 1:
            return False
    return True


def axiom_identity_reflexive(graph: KnowledgeGraph, identity: Relation) -> bool:
    """
    Axiom 2a: Identity Reflexivity
    ∀ a ∈ E: I(a,a)
    Every entity is identical to itself.
    """
    for e in graph.entities.values():
        try:
            if not identity.holds(e, e):
                return False
        except Exception:
            return False
    return True


def check_antisymmetry(graph: KnowledgeGraph, rel: Relation) -> bool:
    """
    Antisymmetry check for partial order candidate.
    If aRb and bRa then a == b.
    """
    if rel.predicate is not None:
        return True
    for aid, bid in graph.edges[rel.name]:
        if (bid, aid) in graph.edges[rel.name] and aid != bid:
            return False
    return True


def check_acyclic(graph: KnowledgeGraph, rel: Relation) -> bool:
    """
    Axiom 6: Temporal Succession (partial)
    Detect cycles on directed edges using DFS.
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
            return False  # Cycle detected
        temp.add(u)
        for v in adj.get(u, []):
            if not dfs(v):
                return False
        temp.remove(u)
        perm.add(u)
        return True

    return all(dfs(node) for node in list(adj.keys()))


def axiom_universal_containment(graph: KnowledgeGraph) -> bool:
    """
    Axiom 7: Universal Containment (Ontological Holism)
    ∃ Ω: ∀ x ∈ E: In(x, Ω)
    There exists a Whole that contains all entities.
    """
    whole = graph._whole
    if whole is None:
        return False
    
    # Check if "In" relation exists for all entities to Omega
    in_rel_name = "In"
    if in_rel_name not in graph.edges:
        return False
    
    for e in graph.entities.values():
        if e.id != whole.id:
            if (e.id, whole.id) not in graph.edges[in_rel_name]:
                return False
    return True


# ---------- Archetypal Pattern Matching ----------

@dataclass
class ArchetypalPattern:
    """
    Pattern schema for archetypal matching (Messiah, Christ Trap, etc.)
    """
    name: str
    phases: List[str]
    required_relations: List[Tuple[str, str]]  # (relation_name, phase)
    
    def matches(self, entity: Entity, graph: KnowledgeGraph) -> bool:
        """Check if entity's relational profile matches this pattern."""
        # Simplified matching - real implementation would be more sophisticated
        entity_relations = set()
        for rel_name, edges in graph.edges.items():
            for a_id, b_id in edges:
                if a_id == entity.id:
                    entity_relations.add(rel_name)
        
        # Check if required relations present
        for rel_name, phase in self.required_relations:
            if rel_name not in entity_relations:
                return False
        return True


# Predefined archetypal patterns

MESSIAH_PATTERN = ArchetypalPattern(
    name="Messiah",
    phases=["Origins", "Initiation", "Confrontation", "Sacrifice", "Legacy"],
    required_relations=[
        ("Prophecy", "Origins"),
        ("Exiled", "Initiation"),
        ("ConfrontsEnemy", "Confrontation"),
        ("LeadsPeople", "Confrontation"),
        ("SacrificesSelf", "Sacrifice"),
        ("Legacy", "Legacy")
    ]
)

CHRIST_TRAP_PATTERN = ArchetypalPattern(
    name="ChristTrap",
    phases=["FalseCalling", "Hubris", "Isolation", "TragicEnd"],
    required_relations=[
        ("FalseProphecy", "FalseCalling"),
        ("InflatedIdentity", "Hubris"),
        ("RefusesCounsel", "Isolation"),
        ("TragicOutcome", "TragicEnd")
    ]
)


# ---------- Demonstration ----------

def _demo() -> None:
    """Demonstration of RM 3.6 with both Truth and Distortion modes."""
    print("=" * 60)
    print("Relational Math 3.6 Demo")
    print("Truth Lattice & Distortion Lattice")
    print("=" * 60)
    
    # === TRUTH MODE ===
    print("\n🌟 TRUTH LATTICE MODE\n")
    g = KnowledgeGraph(mode=LatticeMode.TRUTH)
    
    # Create entities
    alice = Entity("alice", "Alice", domain="psychological")
    bob = Entity("bob", "Bob", domain="psychological")
    carol = Entity("carol", "Carol", domain="psychological")
    
    for e in (alice, bob, carol):
        g.add_entity(e)
    
    # Create the Whole (Ω)
    omega = g.create_whole()
    
    # Identity relation
    identity = Relation("Identity", predicate=lambda a, b, ctx=None: a.id == b.id, reflexive=True, symmetric=True)
    print(f"✓ Identity reflexive axiom: {axiom_identity_reflexive(g, identity)}")
    
    # Relational connections (symmetric, open)
    friend = Relation("friendOf", predicate=None, symmetric=True, weight=1.0)
    g.assert_edge(friend, alice, bob)
    g.assert_edge(friend, bob, carol)
    
    # Hierarchical relation
    mentor = Relation("mentorOf", predicate=None, weight=2.0)
    g.assert_edge(mentor, alice, carol)
    
    # Universal containment - all entities In the Whole
    in_omega = Relation("In", predicate=None, weight=0.5)
    for e in [alice, bob, carol]:
        g.assert_edge(in_omega, e, omega)
    
    print(f"✓ Universal containment axiom: {axiom_universal_containment(g)}")
    print(f"✓ Relational existence axiom: {axiom_relational_existence(g)}")
    
    # Gravity (connectivity measure)
    grav_alice = g.gravity(alice, [friend, mentor])
    grav_bob = g.gravity(bob, [friend, mentor])
    print(f"\n🌐 Relational Gravity:")
    print(f"  Alice: {grav_alice:.2f}")
    print(f"  Bob: {grav_bob:.2f}")
    
    # Stillness (equilibrium)
    time.sleep(0.1)
    stillness_alice = g.stillness(alice, window_sec=5.0)
    print(f"\n🧘 Stillness:")
    print(f"  Alice: {stillness_alice.score:.2f}")
    
    print(f"\n✓ Acyclicity check (mentorOf): {check_acyclic(g, mentor)}")
    print(f"✓ Truth mode total residue: {g.total_residue():.3f}")
    
    # === DISTORTION MODE ===
    print("\n\n💀 DISTORTION LATTICE MODE\n")
    g.set_mode(LatticeMode.DISTORTION)
    
    # Create distortion relations
    owns = seize(Relation("owns", predicate=None))
    controls = bind(Relation("controls", predicate=None))
    
    # Seizure operations generate residue
    print("⚠️  Executing seizure operations...")
    g.assert_edge(owns, alice, bob)
    g.assert_edge(controls, alice, carol)
    g.assert_edge(controls, bob, carol)
    
    print(f"\n📊 Distortion Metrics:")
    print(f"  Total residue: {g.total_residue():.3f}")
    print(f"  Ω_B (Residue Singularity): {g.omega_singularity():.3f}")
    print(f"  Seizure count (Alice): {g.seizure_count['alice']}")
    
    residue_types = g.residue_by_type()
    print(f"\n📈 Residue by type:")
    for rtype, amount in residue_types.items():
        print(f"  {rtype}: {amount:.3f}")
    
    # Try to retract a binding (resistance)
    print(f"\n⛓️  Attempting to retract binding relation...")
    g.retract_edge(controls, alice, carol)
    
    # Distortion gravity (capture/control measure)
    grav_alice_dist = g.gravity(alice, [owns, controls])
    print(f"\n💀 Distortion Gravity (Alice): {grav_alice_dist:.2f}")
    
    # Cleansing residue
    print(f"\n🌊 Cleansing residue...")
    cleansed = g.cleanse_residue(threshold=0.01, decay_rate=0.2)
    print(f"  Cleansed {cleansed} residue nodes")
    print(f"  Remaining residue: {g.total_residue():.3f}")
    
    # Return to truth mode
    print("\n🌟 Returning to TRUTH mode...")
    g.set_mode(LatticeMode.TRUTH)
    
    print("\n" + "=" * 60)
    print("Demo complete. RM 3.6 operational.")
    print("=" * 60)


if __name__ == "__main__":
    _demo()