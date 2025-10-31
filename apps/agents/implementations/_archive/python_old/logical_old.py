# logical.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Protocol, Set, Tuple, Union

# ============================================================
# 1) Logical syntax: formulas as a tiny AST
# ============================================================

class Formula(Protocol):
    def vars(self) -> Set[str]: ...
    def __str__(self) -> str: ...

@dataclass(frozen=True)
class Var(Formula):
    name: str
    def vars(self) -> Set[str]:
        return {self.name}
    def __str__(self) -> str:
        return self.name

@dataclass(frozen=True)
class Top(Formula):
    def vars(self) -> Set[str]:
        return set()
    def __str__(self) -> str:
        return "⊤"

@dataclass(frozen=True)
class Bot(Formula):
    def vars(self) -> Set[str]:
        return set()
    def __str__(self) -> str:
        return "⊥"

@dataclass(frozen=True)
class Not(Formula):
    phi: Formula
    def vars(self) -> Set[str]:
        return self.phi.vars()
    def __str__(self) -> str:
        return f"¬({self.phi})"

@dataclass(frozen=True)
class And(Formula):
    left: Formula
    right: Formula
    def vars(self) -> Set[str]:
        return self.left.vars() | self.right.vars()
    def __str__(self) -> str:
        return f"({self.left} ∧ {self.right})"

@dataclass(frozen=True)
class Or(Formula):
    left: Formula
    right: Formula
    def vars(self) -> Set[str]:
        return self.left.vars() | self.right.vars()
    def __str__(self) -> str:
        return f"({self.left} ∨ {self.right})"

@dataclass(frozen=True)
class Impl(Formula):
    ant: Formula
    cons: Formula
    def vars(self) -> Set[str]:
        return self.ant.vars() | self.cons.vars()
    def __str__(self) -> str:
        return f"({self.ant} → {self.cons})"

@dataclass(frozen=True)
class Iff(Formula):
    left: Formula
    right: Formula
    def vars(self) -> Set[str]:
        return self.left.vars() | self.right.vars()
    def __str__(self) -> str:
        return f"({self.left} ↔ {self.right})"

# Modalities (optional use)
@dataclass(frozen=True)
class Box(Formula):
    phi: Formula
    def vars(self) -> Set[str]:
        return self.phi.vars()
    def __str__(self) -> str:
        return f"□({self.phi})"

@dataclass(frozen=True)
class Dia(Formula):
    phi: Formula
    def vars(self) -> Set[str]:
        return self.phi.vars()
    def __str__(self) -> str:
        return f"◇({self.phi})"


# ============================================================
# 2) Classic two-valued semantics
# ============================================================

Valuation = Dict[str, bool]

def eval_classic(phi: Formula, v: Valuation) -> bool:
    if isinstance(phi, Top):
        return True
    if isinstance(phi, Bot):
        return False
    if isinstance(phi, Var):
        return bool(v.get(phi.name, False))
    if isinstance(phi, Not):
        return not eval_classic(phi.phi, v)
    if isinstance(phi, And):
        return eval_classic(phi.left, v) and eval_classic(phi.right, v)
    if isinstance(phi, Or):
        return eval_classic(phi.left, v) or eval_classic(phi.right, v)
    if isinstance(phi, Impl):
        return (not eval_classic(phi.ant, v)) or eval_classic(phi.cons, v)
    if isinstance(phi, Iff):
        return eval_classic(phi.left, v) == eval_classic(phi.right, v)
    # Modal operators require a frame. Default to internal reading: □p ≡ p, ◇p ≡ p
    if isinstance(phi, Box):
        return eval_classic(phi.phi, v)
    if isinstance(phi, Dia):
        return eval_classic(phi.phi, v)
    raise TypeError(f"Unknown formula type: {phi}")


# ============================================================
# 3) Paraconsistent LP semantics (Priest’s Logic of Paradox)
#    Truth values: T, F, B (both). We encode as a pair (t,f).
# ============================================================

@dataclass(frozen=True)
class LP:
    # pair: t says it is true, f says it is false
    t: bool
    f: bool

    def __str__(self) -> str:
        if self.t and self.f:
            return "B"
        if self.t and not self.f:
            return "T"
        if not self.t and self.f:
            return "F"
        return "N"  # neither

    @staticmethod
    def lift(b: bool) -> "LP":
        return LP(t=b, f=not b)

    def true(self) -> bool:
        return self.t

    def false(self) -> bool:
        return self.f

def lp_not(x: LP) -> LP:
    return LP(t=x.f, f=x.t)

def lp_and(x: LP, y: LP) -> LP:
    return LP(t=x.t and y.t, f=x.f or y.f)

def lp_or(x: LP, y: LP) -> LP:
    return LP(t=x.t or y.t, f=x.f and y.f)

def lp_impl(x: LP, y: LP) -> LP:
    # x → y is equivalent to ¬x ∨ y
    return lp_or(lp_not(x), y)

def lp_iff(x: LP, y: LP) -> LP:
    # (x → y) ∧ (y → x)
    return lp_and(lp_impl(x, y), lp_impl(y, x))

def eval_lp(phi: Formula, v: Dict[str, LP]) -> LP:
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
    # modal default: identity (inject proper frames if needed)
    if isinstance(phi, Box):
        return eval_lp(phi.phi, v)
    if isinstance(phi, Dia):
        return eval_lp(phi.phi, v)
    raise TypeError(f"Unknown formula type: {phi}")

def entails_lp(assumptions: List[Formula], goal: Formula, v: Dict[str, LP]) -> bool:
    """
    LP entailment: Γ ⊨ goal if in the given valuation, every assumption is true (t=True)
    and the goal is true (t=True). We do not allow explosion from contradictions.
    """
    for a in assumptions:
        if not eval_lp(a, v).true():
            return False
    return eval_lp(goal, v).true()


# ============================================================
# 4) Sequents, rules, and a light proof scaffold
# ============================================================

@dataclass(frozen=True)
class Sequent:
    """
    Γ ⊢ φ
    Γ is a multiset of assumptions. No explosion by default.
    """
    gamma: Tuple[Formula, ...]
    goal: Formula
    system: str = "LP"   # "CLASSIC" or "LP"

    def __str__(self) -> str:
        gamma_txt = ", ".join(str(g) for g in self.gamma) if self.gamma else "∅"
        return f"{gamma_txt} ⊢ {self.goal} [{self.system}]"

@dataclass
class ProofStep:
    name: str
    premises: List[Sequent]
    conclusion: Sequent
    notes: str = ""

@dataclass
class Proof:
    steps: List[ProofStep] = field(default_factory=list)
    discharged: bool = False

    def add(self, step: ProofStep) -> None:
        self.steps.append(step)

    def last(self) -> Optional[ProofStep]:
        return self.steps[-1] if self.steps else None


# Common rules as helpers

def rule_modus_ponens(context: Tuple[Formula, ...], a: Formula, imp: Impl) -> Optional[Formula]:
    # From a and (a → b) infer b
    if str(imp.ant) == str(a):
        return imp.cons
    return None

def rule_necessitation(box_axiom: bool, phi: Formula) -> Optional[Box]:
    # If ⊢ φ and the system supports N, infer ⊢ □φ
    if box_axiom:
        return Box(phi)
    return None

def rule_generalization(univ_axiom: bool, phi: Formula) -> Optional[Formula]:
    # Placeholder for first-order generalization if you add quantifiers
    if univ_axiom:
        return phi
    return None


# ============================================================
# 5) Axioms, schemas, and quick checkers
# ============================================================

@dataclass(frozen=True)
class AxiomSchema:
    """
    Represents a schema that can be instantiated by providing
    formula arguments through a mapping function.
    """
    name: str
    builder: Callable[..., Formula]

# Classic Hilbert-style schemas (restricted)
AXIOM_K = AxiomSchema("K", lambda p, q: Impl(Box(Impl(p, q)), Impl(Box(p), Box(q))))
AXIOM_T = AxiomSchema("T", lambda p: Impl(Box(p), p))
AXIOM_NEC = AxiomSchema("NEC", lambda p: Box(p))  # schema for rule, not a real axiom

# Tautology checker (classic)
def is_tautology(phi: Formula) -> bool:
    vars_ = sorted(list(phi.vars()))
    n = len(vars_)
    for mask in range(1 << n):
        v: Valuation = {}
        for i, name in enumerate(vars_):
            v[name] = bool((mask >> i) & 1)
        if not eval_classic(phi, v):
            return False
    return True

# Consistency checker (LP): detects if both φ and ¬φ are true in a given LP valuation
def is_lp_contradiction(phi: Formula, v: Dict[str, LP]) -> bool:
    val_phi = eval_lp(phi, v)
    val_not = eval_lp(Not(phi), v)
    return val_phi.true() and val_not.true()

# Non-explosive consequence (LP): Γ, if consistent on pivot, may allow EFQ on that pivot
def cautious_efq(assumptions: List[Formula], pivot: Formula, goal: Formula, v: Dict[str, LP]) -> bool:
    """
    Explosion from pivot only if pivot is not both true and false.
    If pivot is contradictory under v, block EFQ.
    """
    if is_lp_contradiction(pivot, v):
        return False
    # If Γ proves pivot and ¬pivot is also assumed false, allow EFQ to goal.
    # Here we require pivot true, and Not(pivot) false.
    ok_assumps = all(eval_lp(a, v).true() for a in assumptions)
    if not ok_assumps:
        return False
    if not eval_lp(pivot, v).true():
        return False
    if eval_lp(Not(pivot), v).false():
        return True
    return False


# ============================================================
# 6) Contracts: pre, post, invariant decorators
#    You can attach these to any function in your project.
# ============================================================

@dataclass
class Contract:
    name: str
    pre: Optional[Callable[..., bool]] = None
    post: Optional[Callable[..., bool]] = None
    invariant: Optional[Callable[[Any], bool]] = None

def with_contract(contract: Contract) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        def wrapped(*args, **kwargs):
            if contract.pre and not contract.pre(*args, **kwargs):
                raise AssertionError(f"[{contract.name}] precondition failed")
            result = fn(*args, **kwargs)
            if contract.post and not contract.post(result, *args, **kwargs):
                raise AssertionError(f"[{contract.name}] postcondition failed")
            if contract.invariant and not contract.invariant(result):
                raise AssertionError(f"[{contract.name}] invariant violated")
            return result
        wrapped.__name__ = fn.__name__
        wrapped.__doc__ = fn.__doc__
        return wrapped
    return decorator


# ============================================================
# 7) Utility constructors to ease authoring
# ============================================================

def implies(p: Formula, q: Formula) -> Impl:
    return Impl(p, q)

def iff(p: Formula, q: Formula) -> Iff:
    return Iff(p, q)

def conj(*phis: Formula) -> Formula:
    if not phis:
        return Top()
    out: Formula = phis[0]
    for x in phis[1:]:
        out = And(out, x)
    return out

def disj(*phis: Formula) -> Formula:
    if not phis:
        return Bot()
    out: Formula = phis[0]
    for x in phis[1:]:
        out = Or(out, x)
    return out


# ============================================================
# 8) Minimal modal frame (optional)
#    If you need actual modal reasoning later, wire a Kripke frame.
# ============================================================

@dataclass
class World:
    name: str

@dataclass
class Frame:
    worlds: List[World]
    access: Set[Tuple[str, str]]  # accessibility pairs (w, u)

def eval_box(phi: Formula, w: World, frame: Frame, val: Dict[Tuple[str, str], bool]) -> bool:
    """
    Example: two-valued modal evaluation with a world-indexed valuation.
    val[(world.name, var)] = bool
    """
    for u in frame.worlds:
        if (w.name, u.name) in frame.access:
            if not eval_classic_world(phi, u, val):
                return False
    return True

def eval_classic_world(phi: Formula, w: World, val: Dict[Tuple[str, str], bool]) -> bool:
    if isinstance(phi, Var):
        return bool(val.get((w.name, phi.name), False))
    if isinstance(phi, Top):
        return True
    if isinstance(phi, Bot):
        return False
    if isinstance(phi, Not):
        return not eval_classic_world(phi.phi, w, val)
    if isinstance(phi, And):
        return eval_classic_world(phi.left, w, val) and eval_classic_world(phi.right, w, val)
    if isinstance(phi, Or):
        return eval_classic_world(phi.left, w, val) or eval_classic_world(phi.right, w, val)
    if isinstance(phi, Impl):
        return (not eval_classic_world(phi.ant, w, val)) or eval_classic_world(phi.cons, w, val)
    if isinstance(phi, Iff):
        return eval_classic_world(phi.left, w, val) == eval_classic_world(phi.right, w, val)
    if isinstance(phi, Box):
        # □φ true at w if φ holds at all accessible u
        return eval_box(phi.phi, w, frame=Frame([w], set()), val=val)  # placeholder
    if isinstance(phi, Dia):
        # ◇φ true at w if φ holds at some accessible u
        return eval_classic_world(phi.phi, w, val)
    raise TypeError(f"Unknown formula type: {phi}")


# ============================================================
# 9) Quick examples as functions (no I/O side effects)
#    These are not demos. They are ready-to-import utilities.
# ============================================================

def classic_entails(assumptions: List[Formula], goal: Formula) -> bool:
    """
    Γ ⊨_CLASSIC goal iff for every boolean valuation that makes Γ true,
    goal is also true.
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
        if all(eval_classic(a, v) for a in assumptions):
            if not eval_classic(goal, v):
                return False
    return True

def lp_entails(assumptions: List[Formula], goal: Formula, v: Optional[Dict[str, LP]] = None) -> bool:
    """
    LP entailment with a provided LP valuation.
    If v is None, defaults everything to N (neither true nor false) which
    will make entailment fail unless goal is ⊤ or assumptions are trivial.
    """
    v = v or {}
    return entails_lp(assumptions, goal, v)