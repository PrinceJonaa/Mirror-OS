# truth-lattice.py
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

# These modules are expected to live in the same package
# If you have namespaced packages, adjust the imports accordingly.
from relational import (
    KnowledgeGraph,
    Entity,
    Relation,
    check_acyclic,
)
from symbolic import (
    GenesisEngine,
    GenesisConfig,
    Glyph,
)
from logical import (
    Formula,
    Var,
    Not,
    And,
    Or,
    Impl,
    Iff,
    LP,
    eval_lp,
    lp_entails,
    classic_entails,
)
from empirical import (
    Measurement,
    Oracle,
    Experiment,
    TestCase,
    TrialConfig,
    Recorder,
    oracle_eq,
    oracle_nonempty,
    oracle_schema,
    fixture_setup_empty,
    fixture_teardown_noop,
    fixture_observe_single_value,
    fixture_act_identity,
    TestPlanRow,
    make_experiment_from_rows,
    summarize,
    PresenceMetrics,
)
from paradox import (
    ParadoxEngine,
    ParadoxEngineConfig,
    ParadoxSeed,
    Evidence,
    ParadoxResolution,
    frame_measurement_rule,
    frame_role,
    frame_time,
)

JSON = Dict[str, Any]


# ============================================================
# 1) Lattice configuration and container
# ============================================================

@dataclass
class TruthLatticeConfig:
    glyph_top_k: int = 6
    paradox_heat_threshold: float = 1.0
    randomize_vectors: bool = False


@dataclass
class TruthLattice:
    """
    The Truth Lattice binds the five lenses into one working surface.

    Components:
      - graph: relational store
      - genesis: symbolic glyph engine
      - paradox: resolution engine with optional glyph and presence hooks
      - recorder: empirical recorder for repeatable traces
    """
    graph: KnowledgeGraph = field(default_factory=KnowledgeGraph)
    genesis: GenesisEngine = field(default_factory=lambda: GenesisEngine(GenesisConfig(top_k=6)))
    paradox: ParadoxEngine = field(init=False)
    recorder: Recorder = field(default_factory=Recorder)
    cfg: TruthLatticeConfig = field(default_factory=TruthLatticeConfig)

    def __post_init__(self) -> None:
        # Wire paradox engine with adapters to symbolic and empirical
        p_cfg = ParadoxEngineConfig(
            heat_threshold=self.cfg.paradox_heat_threshold,
            randomize=self.cfg.randomize_vectors,
        )
        self.paradox = ParadoxEngine(
            cfg=p_cfg,
            glyph_builder=self._glyph_builder_from_paradox,
            presence_metric=self._presence_metric_from_state,
        )

    # --------------------------------------------------------
    # Paradox adapters
    # --------------------------------------------------------

    def _glyph_builder_from_paradox(self, invariant: str, ctx: JSON) -> Dict[str, Any]:
        """
        Build a small glyph spec from an invariant sentence using the symbolic engine.
        """
        glyph, spec = self.genesis.glyphify(name=ctx.get("vector", "Invariant"), corpus=[invariant])
        return spec

    def _presence_metric_from_state(self, state: JSON) -> float:
        """
        Convert simple state into a coarse presence score in [0, 1].
        This uses a soft clipping on evidence, perspectives, and frames.
        """
        e = float(state.get("evidence_count", 0))
        p = float(state.get("perspectives", 0))
        f = float(state.get("frames", 0))
        # diminishing returns
        score = 1.0 - 0.5 ** min(6.0, 0.3 * e + 0.5 * p + 0.7 * f)
        return round(max(0.0, min(1.0, score)), 4)

    # --------------------------------------------------------
    # Relational -> Symbolic
    # --------------------------------------------------------

    def glyph_from_cluster(
        self,
        name: str,
        nodes: Sequence[Entity],
        relations: Sequence[Relation],
    ) -> Tuple[Glyph, Dict[str, Any]]:
        """
        Compress a relational subgraph into a symbolic glyph.
        Creates a text corpus from edges and feeds it to the Genesis engine.
        """
        corpus: List[str] = []
        ids = {e.id for e in nodes}
        for R in relations:
            for a in nodes:
                for b in self.graph.neighbors(R, a):
                    if b.id in ids:
                        ai = a.label or a.id
                        bi = b.label or b.id
                        corpus.append(f"{ai} {R.name} {bi}")
        if not corpus:
            # fallback hint when no internal edges are present
            names = ", ".join(e.label or e.id for e in nodes)
            corpus = [f"mirror bridge union among {names}"]
        glyph, spec = self.genesis.glyphify(name, corpus)
        return glyph, spec

    # --------------------------------------------------------
    # Relational -> Empirical
    # --------------------------------------------------------

    def measurements_from_graph(
        self,
        nodes: Sequence[Entity],
        relations: Sequence[Relation],
    ) -> List[Measurement]:
        """
        Collect a few general purpose graph measurements for diagnostics.
        """
        ms: List[Measurement] = []
        # Node and edge counts per relation
        ms.append(Measurement("node_count", len(nodes)))
        for R in relations:
            cnt = 0
            seen = set()
            for a in nodes:
                for b in self.graph.neighbors(R, a):
                    key = (a.id, R.name, b.id)
                    if key not in seen:
                        seen.add(key)
                        cnt += 1
            ms.append(Measurement(f"edges[{R.name}]", cnt))
        # Degree distribution for the first relation if any
        if relations:
            R0 = relations[0]
            degs = [self.graph.degree(R0, a) for a in nodes]
            ms.append(Measurement(f"degree_seq[{R0.name}]", degs))
        return ms

    def experiment_check_acyclic(
        self,
        relation: Relation,
        exp_name: str = "acyclic_check",
    ) -> Experiment:
        """
        Builds a small experiment that asserts a stored-edge relation is acyclic.
        """
        def setup() -> JSON:
            return {"relation": relation.name}

        def act(stim, ctx) -> Any:
            # no-op system under test, result is computed in observe
            return {"relation": relation.name}

        def observe(result: Any, ctx: JSON) -> List[Measurement]:
            ok = check_acyclic(self.graph, relation)
            return [Measurement("acyclic", ok), Measurement("relation_name", relation.name)]

        oracles = {
            "acyclic": [oracle_eq(True)],
            "relation_name": [oracle_nonempty()],
        }
        case = TestCase(
            name="acyclicity",
            setup=setup,
            act=act,
            observe=observe,
            oracles=oracles,
            teardown=fixture_teardown_noop,
        )
        exp = Experiment(exp_name)
        exp.add(case, stimulus=fixture_act_identity.__defaults__[0] if fixture_act_identity.__defaults__ else None)  # type: ignore
        return exp

    # --------------------------------------------------------
    # Paradox end to end
    # --------------------------------------------------------

    def resolve_paradox(
        self,
        seed: ParadoxSeed,
        evidence: Iterable[Evidence] = (),
        perspectives: Iterable[str] = (),
        frames: Iterable[Any] = (),
        context: Optional[JSON] = None,
    ) -> ParadoxResolution:
        """
        One-shot resolution. The engine will add a glyph hint and presence score.
        """
        return self.paradox.resolve(
            seed=seed,
            evidence=evidence,
            perspectives=perspectives,
            frames=frames,
            context=context,
        )

    # --------------------------------------------------------
    # Logical checks on resolutions
    # --------------------------------------------------------

    def check_resolution_consistency_classic(
        self,
        assumptions: List[Formula],
        invariant_as_var: str = "I",
    ) -> bool:
        """
        Classic entailment of a placeholder invariant from assumptions.
        Map your invariant sentence to a boolean variable I for fast checking.
        """
        I = Var(invariant_as_var)
        return classic_entails(assumptions, I)

    def check_resolution_nonexplosive_lp(
        self,
        assumptions: List[Formula],
        invariant_as_var: str = "I",
        lp_values: Optional[Dict[str, LP]] = None,
    ) -> bool:
        """
        LP style entailment that avoids explosion. Returns True if invariant is at least true.
        """
        I = Var(invariant_as_var)
        v = lp_values or {}
        return lp_entails(assumptions, I, v)

    # --------------------------------------------------------
    # Exporters
    # --------------------------------------------------------

    def export_dot(
        self,
        relations: Sequence[Relation],
        nodes: Optional[Sequence[Entity]] = None,
        name: str = "G",
    ) -> str:
        """
        Export a DOT graph for quick visualization. Only stored-edge relations are shown.
        """
        nodes = list(nodes) if nodes is not None else list(self.graph.entities.values())
        ids = {e.id for e in nodes}
        lines = [f'digraph "{name}" {{']
        # node declarations
        for e in nodes:
            label = e.label or e.id
            lines.append(f'  "{e.id}" [label="{label}"];')
        # edges
        for R in relations:
            if R.predicate is not None:
                continue
            for (a_id, b_id) in self.graph.edges.get(R.name, set()):
                if a_id in ids and b_id in ids:
                    lines.append(f'  "{a_id}" -> "{b_id}" [label="{R.name}"];')
        lines.append("}")
        return "\n".join(lines)

    def bundle_spec(
        self,
        name: str,
        glyph_spec: Optional[Dict[str, Any]] = None,
        resolution: Optional[ParadoxResolution] = None,
        measurements: Optional[List[Measurement]] = None,
        extras: Optional[JSON] = None,
    ) -> JSON:
        """
        Create a single JSON payload that captures the state across lenses.
        """
        blob: JSON = {
            "name": name,
            "glyph": glyph_spec or {},
            "resolution": resolution.to_json() if resolution else {},
            "measurements": [m.to_json() for m in (measurements or [])],
            "meta": extras or {},
        }
        return blob

    # --------------------------------------------------------
    # Convenience orchestrations
    # --------------------------------------------------------

    def compress_and_resolve(
        self,
        name: str,
        nodes: Sequence[Entity],
        relations: Sequence[Relation],
        seed: ParadoxSeed,
        evidence: Iterable[Evidence] = (),
        perspectives: Iterable[str] = (),
        frames: Iterable[Any] = (),
        extras: Optional[JSON] = None,
    ) -> JSON:
        """
        Full pipeline:
          1) make a glyph from the relational cluster
          2) take measurements
          3) resolve the paradox and attach glyph hint and presence
          4) bundle everything into a portable spec
        """
        glyph, glyph_spec = self.glyph_from_cluster(name, nodes, relations)
        ms = self.measurements_from_graph(nodes, relations)
        res = self.resolve_paradox(seed, evidence, perspectives, frames)
        return self.bundle_spec(
            name=name,
            glyph_spec=glyph_spec,
            resolution=res,
            measurements=ms,
            extras=extras,
        )