# empirical.py
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union
from collections import defaultdict
import json
import random
import time
import math
import traceback

# ============================================================
# 0) Core ideas
#    Presence -> Perception -> Measurement -> Pattern -> Decision
#    Everything leaves a repeatable trace or it wasn't known.
# ============================================================

Timestamp = float
JSON = Dict[str, Any]


# ============================================================
# 1) Primitives: Stimulus, Sensor, Measurement, Oracle
# ============================================================

@dataclass
class Stimulus:
    """
    A concrete, reproducible input to a system under test (SUT).
    payload is arbitrary but should be JSON-serializable.
    """
    name: str
    payload: JSON
    apply: Optional[Callable[[JSON], Any]] = None  # optional convenience hook

    def run(self) -> Any:
        if self.apply is None:
            return self.payload
        return self.apply(self.payload)


@dataclass
class Measurement:
    """
    A single observation with timestamp and optional meta.
    value should be JSON-serializable (or convertible).
    """
    name: str
    value: Any
    t: Timestamp = field(default_factory=lambda: time.time())
    meta: JSON = field(default_factory=dict)

    def to_json(self) -> JSON:
        v = self.value
        # try to coerce if not JSON-serializable
        if hasattr(v, "__dict__"):
            v = v.__dict__  # lossy but pragmatic
        return {"name": self.name, "value": v, "t": self.t, "meta": self.meta}


OracleFn = Callable[[Measurement, JSON], bool]

@dataclass
class Oracle:
    """
    An oracle decides pass/fail for a single measurement.
    config holds thresholds, tolerances, etc.
    """
    name: str
    fn: OracleFn
    config: JSON = field(default_factory=dict)

    def check(self, m: Measurement) -> bool:
        try:
            return bool(self.fn(m, self.config))
        except Exception:
            return False


# ============================================================
# 2) Test Case and Experiment Scaffolding
# ============================================================

@dataclass
class TestCase:
    """
    A runnable test flow:
      - setup: prepares SUT/context, returns context dict
      - act: consumes a Stimulus + context, returns raw result
      - observe: maps (result, context) -> Measurement(s)
      - oracles: list of validations applied to named measurements
    """
    name: str
    setup: Callable[[], JSON]
    act: Callable[[Stimulus, JSON], Any]
    observe: Callable[[Any, JSON], List[Measurement]]
    oracles: Dict[str, List[Oracle]] = field(default_factory=dict)  # measurement.name -> [oracles]
    teardown: Optional[Callable[[JSON], None]] = None
    notes: str = ""

@dataclass
class TrialConfig:
    repeats: int = 1
    seed: Optional[int] = None
    timeout_s: Optional[float] = None
    adversarial: bool = False
    adversary_budget: int = 0  # number of perturbations if adversarial

@dataclass
class TrialResult:
    ok: bool
    errors: List[str]
    measurements: List[Measurement]
    decisions: Dict[str, Dict[str, bool]]  # m.name -> oracle.name -> bool
    trace_id: str
    started_at: Timestamp
    ended_at: Timestamp
    context_snapshot: JSON = field(default_factory=dict)

@dataclass
class Experiment:
    name: str
    plan: List[Tuple[TestCase, Stimulus, TrialConfig]] = field(default_factory=list)
    meta: JSON = field(default_factory=dict)

    def add(self, case: TestCase, stimulus: Stimulus, cfg: Optional[TrialConfig] = None) -> None:
        self.plan.append((case, stimulus, cfg or TrialConfig()))

    def __iter__(self):
        return iter(self.plan)


# ============================================================
# 3) Adversarial input generator (seedable)
#    Lightweight, extensible perturbations.
# ============================================================

def seed_rng(seed: Optional[int]) -> None:
    if seed is not None:
        random.seed(seed)

def perturb(payload: JSON, budget: int, rng: random.Random) -> JSON:
    """
    Apply up to 'budget' small, schema-free perturbations to numbers/strings/lists.
    """
    def mutate(x: Any) -> Any:
        if isinstance(x, (int, float)):
            scale = 1 + (rng.random() - 0.5) * 0.2  # +/-10%
            return x * scale
        if isinstance(x, str):
            if not x:
                return x
            i = rng.randrange(0, len(x))
            ch = chr((ord(x[i]) + rng.randrange(-2, 3)) % 126 or 32)
            return x[:i] + ch + x[i+1:]
        if isinstance(x, list) and x:
            if rng.random() < 0.5 and len(x) > 1:
                i = rng.randrange(0, len(x))
                j = rng.randrange(0, len(x))
                x = x[:]
                x[i], x[j] = x[j], x[i]
                return x
            else:
                x = x[:]
                x.append(x[-1])
                return x
        if isinstance(x, dict) and x:
            k = rng.choice(list(x.keys()))
            x = dict(x)
            x[k] = mutate(x[k])
            return x
        return x

    out = dict(payload)
    for _ in range(max(0, budget)):
        out = mutate(out)
    return out


# ============================================================
# 4) Trace Recorder: replayable evidence
# ============================================================

@dataclass
class Trace:
    """
    Replayable trace of one trial execution.
    """
    id: str
    case: str
    seed: Optional[int]
    started_at: Timestamp
    ended_at: Timestamp
    stimulus: JSON
    context: JSON
    measurements: List[JSON]
    decisions: Dict[str, Dict[str, bool]]
    errors: List[str] = field(default_factory=list)
    meta: JSON = field(default_factory=dict)

    def to_json(self) -> JSON:
        return asdict(self)

    @staticmethod
    def from_json(j: JSON) -> "Trace":
        return Trace(**j)


class Recorder:
    def __init__(self) -> None:
        self._traces: Dict[str, Trace] = {}

    def save(self, t: Trace) -> None:
        self._traces[t.id] = t

    def get(self, trace_id: str) -> Optional[Trace]:
        return self._traces.get(trace_id)

    def export_json(self) -> str:
        return json.dumps({k: v.to_json() for k, v in self._traces.items()}, ensure_ascii=False, indent=2)

    def import_json(self, text: str) -> None:
        raw = json.loads(text)
        for k, v in raw.items():
            self._traces[k] = Trace.from_json(v)

    def list_ids(self) -> List[str]:
        return list(self._traces.keys())


# ============================================================
# 5) Harness: run a TestCase once or many times
# ============================================================

def now_id(prefix: str = "trace") -> str:
    return f"{prefix}-{int(time.time() * 1000)}-{random.randint(1000, 9999)}"

def run_once(case: TestCase, stimulus: Stimulus, cfg: TrialConfig, recorder: Optional[Recorder] = None) -> TrialResult:
    started = time.time()
    rng = random.Random(cfg.seed)
    errors: List[str] = []
    decisions: Dict[str, Dict[str, bool]] = defaultdict(dict)
    m_all: List[Measurement] = []
    trace_id = now_id()

    # Setup
    try:
        context = case.setup()
    except Exception as e:
        ended = time.time()
        tb = traceback.format_exc()
        errors.append(f"setup_error: {e}\n{tb}")
        tr = TrialResult(False, errors, [], {}, trace_id, started, ended, {})
        if recorder:
            recorder.save(Trace(trace_id, case.name, cfg.seed, started, ended,
                                stimulus.payload, {}, [], {}, errors))
        return tr

    # Act
    raw_result: Any = None
    try:
        payload = stimulus.payload
        if cfg.adversarial and cfg.adversary_budget > 0:
            payload = perturb(payload, cfg.adversary_budget, rng)
        # optional timeout via soft check (cooperative)
        if cfg.timeout_s is not None:
            t0 = time.time()
            raw_result = case.act(Stimulus(stimulus.name, payload), context)
            if (time.time() - t0) > cfg.timeout_s:
                errors.append("timeout_soft: act exceeded timeout")
        else:
            raw_result = case.act(Stimulus(stimulus.name, payload), context)
    except Exception as e:
        tb = traceback.format_exc()
        errors.append(f"act_error: {e}\n{tb}")

    # Observe
    try:
        ms = case.observe(raw_result, context)
        m_all.extend(ms)
    except Exception as e:
        tb = traceback.format_exc()
        errors.append(f"observe_error: {e}\n{tb}")

    # Oracles
    for m in m_all:
        for oracle in case.oracles.get(m.name, []):
            try:
                decisions[m.name][oracle.name] = oracle.check(m)
            except Exception:
                decisions[m.name][oracle.name] = False

    # Teardown
    try:
        if case.teardown:
            case.teardown(context)
    except Exception as e:
        tb = traceback.format_exc()
        errors.append(f"teardown_error: {e}\n{tb}")

    ended = time.time()
    ok = (len(errors) == 0) and all(all(v for v in od.values()) for od in decisions.values())
    tr = TrialResult(ok, errors, m_all, decisions, trace_id, started, ended, context_snapshot=context)

    if recorder:
        recorder.save(Trace(
            id=trace_id,
            case=case.name,
            seed=cfg.seed,
            started_at=started,
            ended_at=ended,
            stimulus=stimulus.payload,
            context=context,
            measurements=[m.to_json() for m in m_all],
            decisions=decisions,
            errors=errors,
            meta={"adversarial": cfg.adversarial, "budget": cfg.adversary_budget}
        ))
    return tr


def run_experiment(exp: Experiment, recorder: Optional[Recorder] = None) -> List[TrialResult]:
    results: List[TrialResult] = []
    for case, stim, cfg in exp:
        seed_rng(cfg.seed)
        for i in range(max(1, cfg.repeats)):
            results.append(run_once(case, stim, cfg, recorder))
    return results


# ============================================================
# 6) Oracles: ready-made validators
# ============================================================

def oracle_eq(expected: Any) -> Oracle:
    return Oracle(
        name="equals",
        fn=lambda m, cfg: m.value == expected,
        config={"expected": expected},
    )

def oracle_close(rel_tol: float = 1e-9, abs_tol: float = 1e-12) -> Oracle:
    def _close(m: Measurement, cfg: JSON) -> bool:
        if not isinstance(m.value, (int, float)):
            return False
        exp = cfg.get("expected")
        if exp is None:
            return False
        return math.isclose(m.value, float(exp), rel_tol=cfg.get("rel_tol", rel_tol), abs_tol=cfg.get("abs_tol", abs_tol))
    return Oracle("close", _close, {"rel_tol": rel_tol, "abs_tol": abs_tol, "expected": None})

def oracle_range(lo: float, hi: float, inclusive: bool = True) -> Oracle:
    def _rng(m: Measurement, cfg: JSON) -> bool:
        try:
            x = float(m.value)
            return (lo <= x <= hi) if inclusive else (lo < x < hi)
        except Exception:
            return False
    return Oracle("range", _rng, {"lo": lo, "hi": hi, "inclusive": inclusive})

def oracle_nonempty() -> Oracle:
    return Oracle("nonempty", lambda m, cfg: bool(m.value))

def oracle_len_at_least(n: int) -> Oracle:
    return Oracle("len_at_least", lambda m, cfg: hasattr(m.value, "__len__") and len(m.value) >= n, {"n": n})

def oracle_schema(keys: List[str]) -> Oracle:
    def _ok(m: Measurement, cfg: JSON) -> bool:
        if not isinstance(m.value, dict):
            return False
        return all(k in m.value for k in keys)
    return Oracle("schema", _ok, {"keys": keys})

def oracle_monotone(non_decreasing: bool = True) -> Oracle:
    """
    Expects measurement.value to be a sequence of numbers.
    """
    def _mono(m: Measurement, cfg: JSON) -> bool:
        xs = m.value
        if not isinstance(xs, list) or not all(isinstance(x, (int, float)) for x in xs):
            return False
        pairs = zip(xs, xs[1:])
        return all((a <= b) if non_decreasing else (a >= b) for a, b in pairs)
    name = "mono_nondec" if non_decreasing else "mono_nonninc"
    return Oracle(name, _mono, {"non_decreasing": non_decreasing})


# ============================================================
# 7) Comparators, Diff, and Diagnostics
# ============================================================

@dataclass
class Diff:
    same: bool
    msg: str
    a: Any = None
    b: Any = None

def compare(a: Any, b: Any, rel_tol: float = 1e-9, abs_tol: float = 1e-12) -> Diff:
    if type(a) != type(b):
        return Diff(False, f"type mismatch: {type(a).__name__} != {type(b).__name__}", a, b)
    if isinstance(a, (int, float)):
        ok = math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)
        return Diff(ok, "numbers close" if ok else "numbers differ", a, b)
    if isinstance(a, str):
        return Diff(a == b, "strings equal" if a == b else "strings differ", a, b)
    if isinstance(a, list):
        if len(a) != len(b):
            return Diff(False, f"list length {len(a)} != {len(b)}", a, b)
        for i, (x, y) in enumerate(zip(a, b)):
            d = compare(x, y, rel_tol, abs_tol)
            if not d.same:
                d.msg = f"idx {i}: {d.msg}"
                return d
        return Diff(True, "lists equal")
    if isinstance(a, dict):
        ka, kb = set(a.keys()), set(b.keys())
        if ka != kb:
            return Diff(False, f"key mismatch: {ka ^ kb}", a, b)
        for k in ka:
            d = compare(a[k], b[k], rel_tol, abs_tol)
            if not d.same:
                d.msg = f"key {k}: {d.msg}"
                return d
        return Diff(True, "dicts equal")
    return Diff(a == b, "objects equal" if a == b else "objects differ", a, b)

def diagnose(result: TrialResult) -> JSON:
    report: JSON = {
        "trace_id": result.trace_id,
        "ok": result.ok,
        "errors": result.errors,
        "dur_ms": int((result.ended_at - result.started_at) * 1000),
        "decisions": result.decisions,
        "measurements": [m.to_json() for m in result.measurements],
        "context": result.context_snapshot,
    }
    # add quick failure focus
    if not result.ok:
        failing = []
        for mname, od in result.decisions.items():
            for oname, val in od.items():
                if not val:
                    failing.append({"measurement": mname, "oracle": oname})
        report["failing_checks"] = failing
    return report


# ============================================================
# 8) Test Plan authoring helpers (tables as data)
# ============================================================

@dataclass
class TestPlanRow:
    """
    A human-friendly row. Convert to (TestCase, Stimulus, TrialConfig) later.
    """
    case_name: str
    stimulus_name: str
    payload: JSON
    oracles: Dict[str, List[Oracle]]  # map measurement name -> oracles
    repeats: int = 1
    seed: Optional[int] = None
    adversarial: bool = False
    adversary_budget: int = 0
    notes: str = ""

def make_experiment_from_rows(
    rows: List[TestPlanRow],
    setup: Callable[[], JSON],
    act: Callable[[Stimulus, JSON], Any],
    observe: Callable[[Any, JSON], List[Measurement]],
    teardown: Optional[Callable[[JSON], None]] = None,
    exp_name: str = "Experiment"
) -> Experiment:
    exp = Experiment(exp_name)
    for r in rows:
        case = TestCase(
            name=r.case_name,
            setup=setup,
            act=act,
            observe=observe,
            oracles=r.oracles,
            teardown=teardown,
            notes=r.notes
        )
        stim = Stimulus(name=r.stimulus_name, payload=r.payload)
        cfg = TrialConfig(repeats=r.repeats, seed=r.seed, adversarial=r.adversarial, adversary_budget=r.adversary_budget)
        exp.add(case, stim, cfg)
    return exp


# ============================================================
# 9) Presence metrics (optional): stability and repeatability
# ============================================================

@dataclass
class PresenceMetrics:
    """
    Coarse metrics for 'is this experiment stable and repeatable?'
    """
    pass_rate: float
    avg_duration_ms: float
    flakiness: float  # variance of pass/fail across repeats (0 = stable)
    coverage_proxy: float  # fraction of measurements that had any oracle bound

def summarize(results: List[TrialResult]) -> PresenceMetrics:
    if not results:
        return PresenceMetrics(0.0, 0.0, 1.0, 0.0)
    passes = [1.0 if r.ok else 0.0 for r in results]
    pass_rate = sum(passes) / len(results)
    durs = [(r.ended_at - r.started_at) * 1000.0 for r in results]
    avg_dur = sum(durs) / len(durs)
    mean = pass_rate
    var = sum((p - mean) ** 2 for p in passes) / len(passes)
    flakiness = min(1.0, var * 4.0)  # soft scale
    # coverage proxy
    measured = sum(len(r.measurements) for r in results)
    bounded = 0
    for r in results:
        for m in r.measurements:
            if r.decisions.get(m.name):
                bounded += 1
    coverage = (bounded / measured) if measured else 0.0
    return PresenceMetrics(round(pass_rate, 4), round(avg_dur, 2), round(flakiness, 4), round(coverage, 4))


# ============================================================
# 10) Minimal fixtures for common patterns
# ============================================================

def fixture_setup_empty() -> JSON:
    return {}

def fixture_teardown_noop(ctx: JSON) -> None:
    return

def fixture_observe_single_value(result: Any, ctx: JSON) -> List[Measurement]:
    return [Measurement("value", result)]

def fixture_act_identity(stim: Stimulus, ctx: JSON) -> Any:
    # Example SUT: return the payload as-is
    return stim.payload

def fixture_oracles_exact(expected: Any) -> Dict[str, List[Oracle]]:
    return {"value": [oracle_eq(expected)]}


# ============================================================
# 11) Replay utilities
# ============================================================

def replay_trace(trace: Trace, case: TestCase, recorder: Optional[Recorder] = None) -> TrialResult:
    """
    Re-executes a case with the exact same stimulus/context seed recorded in the trace.
    Note: if 'setup' is not deterministic, the context may differ; you can replace case.setup
    with a function that returns trace.context for true replay.
    """
    cfg = TrialConfig(repeats=1, seed=trace.seed, adversarial=False)
    stim = Stimulus(trace.case, trace.stimulus)
    return run_once(case, stim, cfg, recorder)