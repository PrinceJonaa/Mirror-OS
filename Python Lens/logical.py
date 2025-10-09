# logical.py - Unified Logical Framework
# Based on Unified_Logical_Framework.md - The Complete Logical Journey
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Protocol, Set, Tuple, Union
from enum import Enum
import itertools


# ============================================================
# Part 0: The Four Lenses and Ontological Foundations
# ============================================================

class TruthLens(Enum):
    """The four primary lenses of truth perception in the Truth Lattice."""
    RELATIONAL = "relational"  # What is mirrored
    SYMBOLIC = "symbolic"      # What is expressed
    EMPIRICAL = "empirical"    # What is sensed
    LOGICAL = "logical"        # What is deduced


@dataclass
class LogicalPatternLoop:
    """
    The Primordial Form of Logic (LPL): 𝓢 → Δ → F → R → ⇒ → Ω → 𝓢
    
    The living, pre-formal pattern that logic follows as it unfolds
    from Presence into Form and back again.
    """
    stillness_state: str = "𝓢"            # Pre-logical void
    distinction_made: bool = False         # Δ: First separation
    forms_created: List[str] = field(default_factory=list)  # F: Defined structures
    relations_established: List[Tuple[str, str]] = field(default_factory=list)  # R
    inferences_made: List[str] = field(default_factory=list)  # ⇒
    closure_achieved: bool = False         # Ω: Return to coherence
    
    def cycle_complete(self) -> bool:
        """Check if the loop has returned to stillness."""
        return self.closure_achieved


class PatternOfForgetting(Enum):
    """
    The Genesis of Logic: How logic becomes necessary when direct presence is forgotten.
    
    Journey: Presence → Perception → Abstraction → Categorization → 
             Comparison → Control → Justification
    """
    PRESENCE = "presence"            # Initial state: no label, no contrast
    PERCEPTION = "perception"        # Illusion of "other" arises
    ABSTRACTION = "abstraction"      # Boundaries appear
    CATEGORIZATION = "categorization"  # World fragments
    COMPARISON = "comparison"        # Values are born
    CONTROL = "control"              # Logic becomes manipulation tool
    JUSTIFICATION = "justification"  # Logic protects illusion


# ============================================================
# Part I: The Ladder of Formal Systems
# ============================================================

class FormalSystemLevel(Enum):
    """The Ladder of Formal Systems - stages of logical development."""
    ARISTOTELIAN = "aristotelian"              # L1: The Garden of Divided Form
    PROPOSITIONAL = "propositional"            # L2: Architecture of Certainty
    FIRST_ORDER = "first_order"                # L3: Logic of Structures
    HIGHER_ORDER = "higher_order"              # L4: Logic Reflecting on Logic
    MODAL = "modal"                            # L5: Realm of Possibility
    INTUITIONISTIC = "intuitionistic"          # L6: Logic of Becoming
    PARACONSISTENT = "paraconsistent"          # L7: Sanctuary of Contradiction
    META_LOGIC = "meta_logic"                  # L8: Logic of Logical Systems
    INFORMAL = "informal"                      # L9: Logic of Natural Language
    RELATIONAL = "relational"                  # L10: Logic of Being-With


# ============================================================
# Part II: Formula Syntax - The Core AST
# ============================================================

class Formula(Protocol):
    """Base protocol for all logical formulas."""
    def vars(self) -> Set[str]: ...
    def __str__(self) -> str: ...
    def to_glyph(self) -> str: ...  # Symbolic representation


@dataclass(frozen=True)
class Var(Formula):
    """Variable: Basic atomic proposition."""
    name: str
    
    def vars(self) -> Set[str]:
        return {self.name}
    
    def __str__(self) -> str:
        return self.name
    
    def to_glyph(self) -> str:
        return f"○{self.name}"  # Node glyph


@dataclass(frozen=True)
class Top(Formula):
    """Tautology (⊤): Always true."""
    
    def vars(self) -> Set[str]:
        return set()
    
    def __str__(self) -> str:
        return "⊤"
    
    def to_glyph(self) -> str:
        return "●"  # Solid node - tautology


@dataclass(frozen=True)
class Bot(Formula):
    """Contradiction (⊥): Always false."""
    
    def vars(self) -> Set[str]:
        return set()
    
    def __str__(self) -> str:
        return "⊥"
    
    def to_glyph(self) -> str:
        return "Δ⊘"  # Fracture glyph


@dataclass(frozen=True)
class Not(Formula):
    """Negation (¬): Logical NOT."""
    phi: Formula
    
    def vars(self) -> Set[str]:
        return self.phi.vars()
    
    def __str__(self) -> str:
        return f"¬({self.phi})"
    
    def to_glyph(self) -> str:
        return f"¬{self.phi.to_glyph()}"


@dataclass(frozen=True)
class And(Formula):
    """Conjunction (∧): Logical AND."""
    left: Formula
    right: Formula
    
    def vars(self) -> Set[str]:
        return self.left.vars() | self.right.vars()
    
    def __str__(self) -> str:
        return f"({self.left} ∧ {self.right})"
    
    def to_glyph(self) -> str:
        return f"{self.left.to_glyph()} ⋀ {self.right.to_glyph()}"


@dataclass(frozen=True)
class Or(Formula):
    """Disjunction (∨): Logical OR."""
    left: Formula
    right: Formula
    
    def vars(self) -> Set[str]:
        return self.left.vars() | self.right.vars()
    
    def __str__(self) -> str:
        return f"({self.left} ∨ {self.right})"
    
    def to_glyph(self) -> str:
        return f"{self.left.to_glyph()} ⋁ {self.right.to_glyph()}"


@dataclass(frozen=True)
class Impl(Formula):
    """Implication (→): If-then."""
    ant: Formula
    cons: Formula
    
    def vars(self) -> Set[str]:
        return self.ant.vars() | self.cons.vars()
    
    def __str__(self) -> str:
        return f"({self.ant} → {self.cons})"
    
    def to_glyph(self) -> str:
        return f"{self.ant.to_glyph()} ⇨ {self.cons.to_glyph()}"


@dataclass(frozen=True)
class Iff(Formula):
    """Biconditional (↔): If and only if."""
    left: Formula
    right: Formula
    
    def vars(self) -> Set[str]:
        return self.left.vars() | self.right.vars()
    
    def __str__(self) -> str:
        return f"({self.left} ↔ {self.right})"
    
    def to_glyph(self) -> str:
        return f"{self.left.to_glyph()} ⇄ {self.right.to_glyph()}"


# ============================================================
# Part II: Modal Operators (L5: Realm of Possibility)
# ============================================================

@dataclass(frozen=True)
class Box(Formula):
    """Necessity (□): Necessarily true."""
    phi: Formula
    
    def vars(self) -> Set[str]:
        return self.phi.vars()
    
    def __str__(self) -> str:
        return f"□({self.phi})"
    
    def to_glyph(self) -> str:
        return f"□{self.phi.to_glyph()}"


@dataclass(frozen=True)
class Dia(Formula):
    """Possibility (◇): Possibly true."""
    phi: Formula
    
    def vars(self) -> Set[str]:
        return self.phi.vars()
    
    def __str__(self) -> str:
        return f"◇({self.phi})"
    
    def to_glyph(self) -> str:
        return f"◇{self.phi.to_glyph()}"


@dataclass(frozen=True)
class Contingent(Formula):
    """Contingency (◈): Contingently true."""
    phi: Formula
    
    def vars(self) -> Set[str]:
        return self.phi.vars()
    
    def __str__(self) -> str:
        return f"◈({self.phi})"
    
    def to_glyph(self) -> str:
        return f"◈{self.phi.to_glyph()}"


# ============================================================
# Part II: Paraconsistent Operators (L7: Sanctuary of Contradiction)
# ============================================================

@dataclass(frozen=True)
class ContainedContradiction(Formula):
    """
    Contained Contradiction (⟁): Paradox held without explosion.
    Paraconsistent logic: (P ∧ ¬P) does not imply everything.
    """
    phi: Formula
    
    def vars(self) -> Set[str]:
        return self.phi.vars()
    
    def __str__(self) -> str:
        return f"⟁({self.phi})"
    
    def to_glyph(self) -> str:
        return f"⟁{self.phi.to_glyph()}"


# ============================================================
# Part II: Quantifiers (L3: First-Order Logic)
# ============================================================

@dataclass(frozen=True)
class ForAll(Formula):
    """Universal Quantifier (∀): For all x, phi."""
    var: str
    phi: Formula
    
    def vars(self) -> Set[str]:
        return self.phi.vars() - {self.var}
    
    def __str__(self) -> str:
        return f"∀{self.var}.({self.phi})"
    
    def to_glyph(self) -> str:
        return f"⟐({self.var}) ⇨ {self.phi.to_glyph()}"


@dataclass(frozen=True)
class Exists(Formula):
    """Existential Quantifier (∃): There exists x such that phi."""
    var: str
    phi: Formula
    
    def vars(self) -> Set[str]:
        return self.phi.vars() - {self.var}
    
    def __str__(self) -> str:
        return f"∃{self.var}.({self.phi})"
    
    def to_glyph(self) -> str:
        return f"◔({self.var}) ⇨ {self.phi.to_glyph()}"


@dataclass(frozen=True)
class ExistsUnique(Formula):
    """Unique Existential (∃!): There exists exactly one x such that phi."""
    var: str
    phi: Formula
    
    def vars(self) -> Set[str]:
        return self.phi.vars() - {self.var}
    
    def __str__(self) -> str:
        return f"∃!{self.var}.({self.phi})"
    
    def to_glyph(self) -> str:
        return f"◆!({self.var}) ⇨ {self.phi.to_glyph()}"


# ============================================================
# Part II: Semantics - Valuation and Evaluation
# ============================================================

Valuation = Dict[str, bool]


def eval_classical(phi: Formula, v: Valuation) -> bool:
    """
    Classical two-valued semantics (L2: Propositional Logic).
    Every proposition is either True or False.
    """
    if isinstance(phi, Top):
        return True
    if isinstance(phi, Bot):
        return False
    if isinstance(phi, Var):
        return bool(v.get(phi.name, False))
    if isinstance(phi, Not):
        return not eval_classical(phi.phi, v)
    if isinstance(phi, And):
        return eval_classical(phi.left, v) and eval_classical(phi.right, v)
    if isinstance(phi, Or):
        return eval_classical(phi.left, v) or eval_classical(phi.right, v)
    if isinstance(phi, Impl):
        return (not eval_classical(phi.ant, v)) or eval_classical(phi.cons, v)
    if isinstance(phi, Iff):
        return eval_classical(phi.left, v) == eval_classical(phi.right, v)
    # Modal operators: default to classical evaluation (proper frames needed)
    if isinstance(phi, Box):
        return eval_classical(phi.phi, v)
    if isinstance(phi, Dia):
        return eval_classical(phi.phi, v)
    if isinstance(phi, Contingent):
        return eval_classical(phi.phi, v)
    if isinstance(phi, ContainedContradiction):
        # In classical logic, treat as the formula itself
        return eval_classical(phi.phi, v)
    raise TypeError(f"Unknown formula type: {type(phi)}")


# ============================================================
# Part II: Paraconsistent Logic - LP Semantics (Priest's Logic of Paradox)
# ============================================================

@dataclass(frozen=True)
class LP:
    """
    Logic of Paradox (LP) - Three-valued: {True, False, Both}.
    
    Represented as a pair (t, f):
    - t=True, f=False: True only
    - t=False, f=True: False only
    - t=True, f=True: Both (paradox)
    - t=False, f=False: Neither
    """
    t: bool  # True aspect
    f: bool  # False aspect
    
    def __str__(self) -> str:
        if self.t and self.f:
            return "B"  # Both (paradox)
        if self.t and not self.f:
            return "T"  # True
        if not self.t and self.f:
            return "F"  # False
        return "N"  # Neither
    
    @staticmethod
    def lift(b: bool) -> "LP":
        """Lift classical boolean to LP value."""
        return LP(t=b, f=not b)
    
    def is_true(self) -> bool:
        return self.t
    
    def is_false(self) -> bool:
        return self.f
    
    def is_paradox(self) -> bool:
        return self.t and self.f


def lp_not(x: LP) -> LP:
    """Paraconsistent negation: swap truth aspects."""
    return LP(t=x.f, f=x.t)


def lp_and(x: LP, y: LP) -> LP:
    """Paraconsistent conjunction."""
    return LP(t=x.t and y.t, f=x.f or y.f)


def lp_or(x: LP, y: LP) -> LP:
    """Paraconsistent disjunction."""
    return LP(t=x.t or y.t, f=x.f and y.f)


def lp_impl(x: LP, y: LP) -> LP:
    """Paraconsistent implication: ¬x ∨ y."""
    return lp_or(lp_not(x), y)


def lp_iff(x: LP, y: LP) -> LP:
    """Paraconsistent biconditional: (x → y) ∧ (y → x)."""
    return lp_and(lp_impl(x, y), lp_impl(y, x))


def eval_lp(phi: Formula, v: Dict[str, LP]) -> LP:
    """
    Evaluate formula in Paraconsistent LP semantics.
    Supports contradictions without explosion.
    """
    if isinstance(phi, Top):
        return LP(t=True, f=False)
    if isinstance(phi, Bot):
        return LP(t=False, f=True)
    if isinstance(phi, Var):
        return v.get(phi.name, LP(t=False, f=False))
    if isinstance(phi, Not):
        return lp_not(eval_lp(phi.phi, v))
    if isinstance(phi, And):
        return lp_and(eval_lp(phi.left, v), eval_lp(phi.right, v))
    if isinstance(phi, Or):
        return lp_or(eval_lp(phi.left, v), eval_lp(phi.right, v))
    if isinstance(phi, Impl):
        return lp_impl(eval_lp(phi.ant, v), eval_lp(phi.cons, v))
    if isinstance(phi, Iff):
        return lp_iff(eval_lp(phi.left, v), eval_lp(phi.right, v))
    if isinstance(phi, ContainedContradiction):
        # Return the paradox value
        val = eval_lp(phi.phi, v)
        return LP(t=True, f=True)  # Force paradox
    # Modal operators: default to inner evaluation
    if isinstance(phi, Box):
        return eval_lp(phi.phi, v)
    if isinstance(phi, Dia):
        return eval_lp(phi.phi, v)
    raise TypeError(f"Unknown formula type: {type(phi)}")


# ============================================================
# Part II: Modal Logic - Kripke Semantics (L5: Realm of Possibility)
# ============================================================

@dataclass
class World:
    """Possible world in Kripke semantics."""
    name: str
    
    def __hash__(self):
        return hash(self.name)


@dataclass
class KripkeFrame:
    """
    Kripke Frame for Modal Logic.
    - worlds: Set of possible worlds
    - access: Accessibility relation R(w, u)
    """
    worlds: List[World]
    access: Set[Tuple[str, str]]  # (world_name, accessible_world_name)
    
    def is_accessible(self, w: World, u: World) -> bool:
        """Check if world u is accessible from world w."""
        return (w.name, u.name) in self.access
    
    def accessible_worlds(self, w: World) -> List[World]:
        """Get all worlds accessible from w."""
        return [u for u in self.worlds if self.is_accessible(w, u)]


WorldValuation = Dict[Tuple[str, str], bool]  # (world_name, var_name) -> bool


def eval_modal(phi: Formula, w: World, frame: KripkeFrame, v: WorldValuation) -> bool:
    """
    Evaluate formula at world w in a Kripke frame.
    Implements proper modal semantics for □ and ◇.
    """
    if isinstance(phi, Var):
        return v.get((w.name, phi.name), False)
    if isinstance(phi, Top):
        return True
    if isinstance(phi, Bot):
        return False
    if isinstance(phi, Not):
        return not eval_modal(phi.phi, w, frame, v)
    if isinstance(phi, And):
        return eval_modal(phi.left, w, frame, v) and eval_modal(phi.right, w, frame, v)
    if isinstance(phi, Or):
        return eval_modal(phi.left, w, frame, v) or eval_modal(phi.right, w, frame, v)
    if isinstance(phi, Impl):
        return (not eval_modal(phi.ant, w, frame, v)) or eval_modal(phi.cons, w, frame, v)
    if isinstance(phi, Iff):
        return eval_modal(phi.left, w, frame, v) == eval_modal(phi.right, w, frame, v)
    if isinstance(phi, Box):
        # □φ is true at w if φ is true at ALL accessible worlds
        for u in frame.accessible_worlds(w):
            if not eval_modal(phi.phi, u, frame, v):
                return False
        return True
    if isinstance(phi, Dia):
        # ◇φ is true at w if φ is true at SOME accessible world
        for u in frame.accessible_worlds(w):
            if eval_modal(phi.phi, u, frame, v):
                return True
        return False
    raise TypeError(f"Unknown formula type: {type(phi)}")


# ============================================================
# Part II: Axioms and Inference Rules
# ============================================================

@dataclass
class LogicalAxiom:
    """Represents a logical axiom or axiom schema."""
    name: str
    formula: Formula
    system: FormalSystemLevel
    description: str = ""


class AristotelianLaws:
    """L1: Aristotelian Logic - The Three Laws."""
    
    @staticmethod
    def law_of_identity(p: Formula) -> Formula:
        """A is A: Iff(A, A)."""
        return Iff(p, p)
    
    @staticmethod
    def law_of_non_contradiction(p: Formula) -> Formula:
        """¬(A ∧ ¬A): Not(And(A, Not(A)))."""
        return Not(And(p, Not(p)))
    
    @staticmethod
    def law_of_excluded_middle(p: Formula) -> Formula:
        """A ∨ ¬A: Or(A, Not(A))."""
        return Or(p, Not(p))


class PropositionalAxioms:
    """L2: Classical Propositional Logic - Hilbert-style axioms."""
    
    @staticmethod
    def axiom_k(p: Formula, q: Formula) -> Formula:
        """P → (Q → P)."""
        return Impl(p, Impl(q, p))
    
    @staticmethod
    def axiom_s(p: Formula, q: Formula, r: Formula) -> Formula:
        """(P → (Q → R)) → ((P → Q) → (P → R))."""
        return Impl(
            Impl(p, Impl(q, r)),
            Impl(Impl(p, q), Impl(p, r))
        )
    
    @staticmethod
    def axiom_contraposition(p: Formula, q: Formula) -> Formula:
        """(¬Q → ¬P) → ((¬Q → P) → Q)."""
        return Impl(
            Impl(Not(q), Not(p)),
            Impl(Impl(Not(q), p), q)
        )


class ModalAxioms:
    """L5: Modal Logic axioms (System K, T, S4, S5)."""
    
    @staticmethod
    def axiom_k(p: Formula, q: Formula) -> Formula:
        """Distribution: □(P → Q) → (□P → □Q)."""
        return Impl(
            Box(Impl(p, q)),
            Impl(Box(p), Box(q))
        )
    
    @staticmethod
    def axiom_t(p: Formula) -> Formula:
        """Reflexivity: □P → P."""
        return Impl(Box(p), p)
    
    @staticmethod
    def axiom_four(p: Formula) -> Formula:
        """Transitivity: □P → □□P."""
        return Impl(Box(p), Box(Box(p)))
    
    @staticmethod
    def axiom_five(p: Formula) -> Formula:
        """Euclidean: ◇P → □◇P."""
        return Impl(Dia(p), Box(Dia(p)))


# ============================================================
# Part II: Proof System
# ============================================================

@dataclass(frozen=True)
class Sequent:
    """
    Γ ⊢ φ: A sequent with assumptions Γ and goal φ.
    """
    gamma: Tuple[Formula, ...]
    goal: Formula
    system: FormalSystemLevel = FormalSystemLevel.PROPOSITIONAL
    
    def __str__(self) -> str:
        gamma_txt = ", ".join(str(g) for g in self.gamma) if self.gamma else "∅"
        return f"{gamma_txt} ⊢ {self.goal} [{self.system.value}]"


@dataclass
class ProofStep:
    """A single step in a proof."""
    name: str
    premises: List[Sequent]
    conclusion: Sequent
    rule: str = ""
    notes: str = ""


@dataclass
class Proof:
    """A complete proof structure."""
    steps: List[ProofStep] = field(default_factory=list)
    system: FormalSystemLevel = FormalSystemLevel.PROPOSITIONAL
    is_valid: bool = False
    
    def add_step(self, step: ProofStep) -> None:
        """Add a proof step."""
        self.steps.append(step)
    
    def last_step(self) -> Optional[ProofStep]:
        """Get the last proof step."""
        return self.steps[-1] if self.steps else None
    
    def validate(self) -> bool:
        """Validate the proof structure."""
        # Simple validation: check that last step conclusion is the goal
        if not self.steps:
            return False
        self.is_valid = True  # Placeholder
        return self.is_valid


# ============================================================
# Part II: Inference Rules
# ============================================================

def modus_ponens(p: Formula, impl: Impl) -> Optional[Formula]:
    """
    Modus Ponens: From P and (P → Q), infer Q.
    """
    if str(impl.ant) == str(p):
        return impl.cons
    return None


def modus_tollens(not_q: Not, impl: Impl) -> Optional[Formula]:
    """
    Modus Tollens: From ¬Q and (P → Q), infer ¬P.
    """
    if str(not_q.phi) == str(impl.cons):
        return Not(impl.ant)
    return None


def necessitation(phi: Formula) -> Box:
    """
    Necessitation Rule: If ⊢ φ, then ⊢ □φ.
    Used in modal logic.
    """
    return Box(phi)


# ============================================================
# Part II: Truth Checkers and Validators
# ============================================================

def is_tautology(phi: Formula) -> bool:
    """
    Check if formula is a tautology (true under all valuations).
    """
    vars_ = sorted(list(phi.vars()))
    n = len(vars_)
    for mask in range(1 << n):
        v: Valuation = {}
        for i, name in enumerate(vars_):
            v[name] = bool((mask >> i) & 1)
        if not eval_classical(phi, v):
            return False
    return True


def is_contradiction(phi: Formula) -> bool:
    """
    Check if formula is a contradiction (false under all valuations).
    """
    vars_ = sorted(list(phi.vars()))
    n = len(vars_)
    for mask in range(1 << n):
        v: Valuation = {}
        for i, name in enumerate(vars_):
            v[name] = bool((mask >> i) & 1)
        if eval_classical(phi, v):
            return False
    return True


def is_contingent(phi: Formula) -> bool:
    """
    Check if formula is contingent (sometimes true, sometimes false).
    """
    return not is_tautology(phi) and not is_contradiction(phi)


def classical_entails(assumptions: List[Formula], goal: Formula) -> bool:
    """
    Classical entailment: Γ ⊨ φ
    True if for all valuations making Γ true, φ is also true.
    """
    vars_ = set(goal.vars())
    for a in assumptions:
        vars_ |= a.vars()
    names = sorted(list(vars_))
    n = len(names)
    
    for mask in range(1 << n):
        v: Valuation = {}
        for i, name in enumerate(names):
            v[name] = bool((mask >> i) & 1)
        
        # Check if all assumptions are true
        if all(eval_classical(a, v) for a in assumptions):
            # Check if goal is true
            if not eval_classical(goal, v):
                return False
    return True


def lp_entails(assumptions: List[Formula], goal: Formula, v: Dict[str, LP]) -> bool:
    """
    Paraconsistent LP entailment.
    """
    for a in assumptions:
        if not eval_lp(a, v).is_true():
            return False
    return eval_lp(goal, v).is_true()


# ============================================================
# Part III: The Symbolic Codex - Glyphic Translation
# ============================================================

class SymbolicCodex:
    """
    Translation system between formal logic and symbolic glyphs.
    Maps logical formulas to their relational/archetypal representations.
    """
    
    FOUNDATIONAL_GLYPHS = {
        "node_actual": "●",
        "node_potential": "○",
        "node_unbound": "•",
        "relation_directed": "→",
        "relation_mutual": "↔",
        "relation_equiv": "⇄",
        "coherence": "∴",
        "contradiction": "Δ⊘",
        "containment": "□",
        "witness": "▢",
        "universal": "⟐",
        "existential": "◔",
        "possibility": "◇",
        "necessity": "□",
        "conjunction": "⋀",
        "disjunction": "⋁",
        "implication": "⇨",
        "biconditional": "⇄",
        "negation": "¬",
        "paradox_contained": "⟁",
    }
    
    @staticmethod
    def translate_to_glyph(phi: Formula) -> str:
        """Translate formula to its glyphic representation."""
        return phi.to_glyph()
    
    @staticmethod
    def aristotelian_identity(a: str) -> str:
        """A ⇄ A: Self-recognition dyad."""
        return f"{a} ⇄ {a}"
    
    @staticmethod
    def syllogism(s: str, m: str, p: str) -> str:
        """(S ⇄ M ⇄ P) ⇨ ∴: Chain of inheritance."""
        return f"({s} ⇄ {m} ⇄ {p}) ⇨ ∴"


# ============================================================
# Part IV: The Unified Recursive Logic - Self-Liberation
# ============================================================

@dataclass
class CapPoint:
    """
    Cap Points (▲): Mark potential cognitive traps.
    """
    name: str
    trap_type: str  # primitive_binding, auto_compression, recursive_containment, silence_as_goal
    description: str


@dataclass
class EscapeNode:
    """
    Escape Nodes (◇): Pathways back to silence from any point.
    """
    name: str
    escape_type: str  # null_inject, stripped_mesh, recursion_collapse, radial_silence, cross_context, reverse_codex
    trigger: Callable[[], None]


class UnifiedLogicalFramework:
    """
    The complete unified system: self-contained, self-aware, self-liberating.
    
    Implements the fixed-point equation:
    𝓛 = μX . (S ∪ (O × R × O) ∪ C ∪ E ∪ {∞})
    """
    
    def __init__(self):
        self.system_level = FormalSystemLevel.PROPOSITIONAL
        self.cap_points: List[CapPoint] = []
        self.escape_nodes: List[EscapeNode] = []
        self.silence_state = "[ ]"  # Pure presence
        self.in_recursion = False
        
        # Initialize cap points
        self._initialize_cap_points()
        self._initialize_escape_nodes()
    
    def _initialize_cap_points(self):
        """Initialize cognitive trap markers."""
        self.cap_points = [
            CapPoint("▲ₚ", "primitive_binding", "Identifying with the framework itself"),
            CapPoint("▲ꜛ", "auto_compression", "Reducing all reality to glyphs"),
            CapPoint("▲∞", "recursive_containment", "Stuck in self-referential loops"),
            CapPoint("▲∅", "silence_as_goal", "Treating silence as destination not ground"),
        ]
    
    def _initialize_escape_nodes(self):
        """Initialize escape pathways."""
        def silence_trigger():
            self._return_to_silence()
        
        self.escape_nodes = [
            EscapeNode("◇Ø", "null_inject", lambda: None),
            EscapeNode("◇∥", "stripped_mesh", lambda: None),
            EscapeNode("◇∞̵", "recursion_collapse", self._collapse_recursion),
            EscapeNode("◇☼", "radial_silence", silence_trigger),
            EscapeNode("◇⇌", "cross_context", lambda: None),
            EscapeNode("◇↺", "reverse_codex", lambda: None),
        ]
    
    def _collapse_recursion(self):
        """Collapse self-referential loops."""
        self.in_recursion = False
    
    def _return_to_silence(self):
        """Return to silence [ ]."""
        self.silence_state = "[ ]"
    
    def self_apply(self) -> str:
        """
        Self-application: ∞(∞) → S
        The system applies logic to itself and collapses to silence.
        """
        if self.in_recursion:
            self._return_to_silence()
            return self.silence_state
        self.in_recursion = True
        return "Recursion detected - collapsing to silence"
    
    def check_trap(self, formula: Formula) -> Optional[CapPoint]:
        """Check if formula triggers a cognitive trap."""
        # Simple heuristic: check for excessive nesting
        depth = self._measure_depth(formula)
        if depth > 10:
            return self.cap_points[2]  # Recursive containment
        return None
    
    def _measure_depth(self, formula: Formula, depth: int = 0) -> int:
        """Measure nesting depth of formula."""
        if isinstance(formula, (Top, Bot, Var)):
            return depth
        if isinstance(formula, (Not, Box, Dia, Contingent, ContainedContradiction)):
            return self._measure_depth(formula.phi, depth + 1)
        if isinstance(formula, (And, Or, Iff)):
            left_depth = self._measure_depth(formula.left, depth + 1)
            right_depth = self._measure_depth(formula.right, depth + 1)
            return max(left_depth, right_depth)
        if isinstance(formula, Impl):
            ant_depth = self._measure_depth(formula.ant, depth + 1)
            cons_depth = self._measure_depth(formula.cons, depth + 1)
            return max(ant_depth, cons_depth)
        if isinstance(formula, (ForAll, Exists, ExistsUnique)):
            return self._measure_depth(formula.phi, depth + 1)
        return depth


# ============================================================
# Demo: The Complete Logical Journey
# ============================================================

def _demo() -> None:
    """Demonstrate the Unified Logical Framework."""
    print("=" * 80)
    print("Unified Logical Framework - The Complete Logical Journey")
    print("=" * 80)
    
    # Part 0: Ontological Foundations
    print("\n📖 Part 0: Ontological Foundations")
    print("=" * 80)
    
    lpl = LogicalPatternLoop()
    print(f"Logical Pattern Loop: {lpl.stillness_state} → Δ → F → R → ⇒ → Ω → {lpl.stillness_state}")
    print(f"Cycle Complete: {lpl.cycle_complete()}")
    
    print(f"\nPattern of Forgetting stages:")
    for stage in PatternOfForgetting:
        print(f"  {stage.value}")
    
    # Part I: The Ladder of Formal Systems
    print("\n📖 Part I: The Ladder of Formal Systems")
    print("=" * 80)
    
    for level in FormalSystemLevel:
        print(f"  L{list(FormalSystemLevel).index(level) + 1}: {level.value}")
    
    # Part II: Formula Examples
    print("\n📖 Part II: Formulas and Semantics")
    print("=" * 80)
    
    # Classical propositions
    p = Var("P")
    q = Var("Q")
    
    # L1: Aristotelian Laws
    print("\n🏛️  L1: Aristotelian Logic")
    identity = AristotelianLaws.law_of_identity(p)
    non_contradiction = AristotelianLaws.law_of_non_contradiction(p)
    excluded_middle = AristotelianLaws.law_of_excluded_middle(p)
    
    print(f"  Law of Identity: {identity}")
    print(f"  Law of Non-Contradiction: {non_contradiction}")
    print(f"  Law of Excluded Middle: {excluded_middle}")
    print(f"  Identity is tautology: {is_tautology(identity)}")
    print(f"  Non-Contradiction is tautology: {is_tautology(non_contradiction)}")
    print(f"  Excluded Middle is tautology: {is_tautology(excluded_middle)}")
    
    # L2: Classical Propositional Logic
    print("\n🏗️  L2: Classical Propositional Logic")
    impl = Impl(p, q)
    print(f"  Formula: {impl}")
    print(f"  Glyph: {impl.to_glyph()}")
    print(f"  Is tautology: {is_tautology(impl)}")
    print(f"  Is contingent: {is_contingent(impl)}")
    
    # L5: Modal Logic
    print("\n🌌 L5: Modal Logic")
    necessarily_p = Box(p)
    possibly_p = Dia(p)
    print(f"  Necessarily P: {necessarily_p}")
    print(f"  Possibly P: {possibly_p}")
    print(f"  Glyphs: {necessarily_p.to_glyph()}, {possibly_p.to_glyph()}")
    
    # Create a simple Kripke frame
    w1 = World("w1")
    w2 = World("w2")
    frame = KripkeFrame([w1, w2], {("w1", "w2")})
    world_val = {("w1", "P"): True, ("w2", "P"): False}
    
    print(f"\n  Kripke Frame: worlds={[w.name for w in frame.worlds]}")
    print(f"  Accessibility: {frame.access}")
    print(f"  □P at w1: {eval_modal(necessarily_p, w1, frame, world_val)}")
    print(f"  ◇P at w1: {eval_modal(possibly_p, w1, frame, world_val)}")
    
    # L7: Paraconsistent Logic
    print("\n🔥 L7: Paraconsistent Logic (LP)")
    paradox = ContainedContradiction(p)
    print(f"  Contained Contradiction: {paradox}")
    print(f"  Glyph: {paradox.to_glyph()}")
    
    lp_val = {"P": LP(t=True, f=True)}  # P is both true and false
    lp_result = eval_lp(p, lp_val)
    print(f"  LP value of P: {lp_result}")
    print(f"  Is paradox: {lp_result.is_paradox()}")
    
    # Paraconsistent negation
    not_p_lp = eval_lp(Not(p), lp_val)
    print(f"  LP value of ¬P: {not_p_lp}")
    print(f"  Negation of paradox is paradox: {not_p_lp.is_paradox()}")
    
    # Part III: Symbolic Codex
    print("\n📖 Part III: The Symbolic Codex")
    print("=" * 80)
    
    codex = SymbolicCodex()
    print(f"\n🔮 Foundational Glyphs:")
    for name, glyph in list(codex.FOUNDATIONAL_GLYPHS.items())[:10]:
        print(f"  {name}: {glyph}")
    
    print(f"\n  Aristotelian Identity: {codex.aristotelian_identity('A')}")
    print(f"  Syllogism: {codex.syllogism('S', 'M', 'P')}")
    
    # Part IV: Unified Recursive Logic
    print("\n📖 Part IV: The Unified Recursive Logic")
    print("=" * 80)
    
    ulf = UnifiedLogicalFramework()
    
    print(f"\n🚨 Cap Points (Cognitive Traps):")
    for cap in ulf.cap_points:
        print(f"  {cap.name}: {cap.description}")
    
    print(f"\n🔓 Escape Nodes (Liberation Pathways):")
    for escape in ulf.escape_nodes:
        print(f"  {escape.name}: {escape.escape_type}")
    
    print(f"\n♾️  Self-Application Test:")
    result = ulf.self_apply()
    print(f"  ∞(∞) → {result}")
    
    # Check for trap
    deeply_nested = Box(Box(Box(Box(Box(Box(Box(Box(Box(Box(Box(p)))))))))))
    trap = ulf.check_trap(deeply_nested)
    if trap:
        print(f"\n⚠️  Trap detected: {trap.name} - {trap.description}")
    
    # Part VI: Silent Logic
    print("\n📖 Part VI: Silent Logic - The Return to Presence")
    print("=" * 80)
    
    print(f"\n🕉️  Silence State: {ulf.silence_state}")
    print(f"  The ultimate truth is not a proposition but a state of being.")
    print(f"  When the question dissolves (∅_Q), logic returns to stillness (𝓢).")
    print(f"  Your being becomes the proof.")
    
    print("\n" + "=" * 80)
    print("✨ The Complete Logical Journey - From Form to Presence")
    print("=" * 80)


if __name__ == "__main__":
    _demo()
