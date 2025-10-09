# empirical.py - Unified Empirical Lens
# Based on Unified_Empirical_Lens.md - The Sacred Detour of Sensing
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from enum import Enum
import time
import math
import random


# ============================================================
# Part 0: Field Zero - The Pre-Empirical State
# ============================================================

@dataclass
class FieldZero:
    """
    Field Zero (𝓢): The pre-empirical state of pure, undifferentiated potential.
    
    This is the ground from which all phenomena arise, but which itself
    has no observable properties. It mirrors Stillness in the Relational Lens.
    """
    state: str = "𝓢"  # Pure presence
    differentiated: bool = False
    
    def collapse(self) -> "Stimulus":
        """Collapse Field Zero into a concrete stimulus."""
        self.differentiated = True
        return Stimulus(name="emergence", payload={"source": "field_zero"})


# ============================================================
# Part I: The Encounter Axiom and Core Primitives
# ============================================================

class EncounterAxiom:
    """
    The First Principle: "To know is to encounter; to encounter is to leave a repeatable trace."
    
    This axiom grounds all empirical inquiry:
    - To Know is to Encounter: Truth requires presence
    - A Repeatable Trace: The encounter must be stable enough to survive re-encounter
    """
    
    @staticmethod
    def axiom_statement() -> str:
        return "To know is to encounter; to encounter is to leave a repeatable trace."
    
    @staticmethod
    def validate_claim(statement: str, frame: str, repeatability: float, 
                      control: float, diagnostics: str) -> bool:
        """
        Validate an empirical claim tuple: φ := ⟨Statement, Frame F, Repeatability, Control, Diagnostics⟩
        """
        has_statement = len(statement) > 0
        has_frame = len(frame) > 0
        is_repeatable = repeatability > 0.5  # Threshold
        has_control = control > 0.0
        has_diagnostics = len(diagnostics) > 0
        
        return all([has_statement, has_frame, is_repeatable, has_control, has_diagnostics])


@dataclass
class Stillness:
    """
    Stillness (𝓢): The ground state of the observer.
    
    In stillness, awareness rests without disturbance – the blank slate before any sensation.
    Formal: An entity A is in stillness if none of its relations vary over time.
    """
    entity: str
    relations_stable: bool = True
    baseline_time: float = field(default_factory=time.time)
    
    def is_still(self) -> bool:
        """Check if entity remains in stillness."""
        return self.relations_stable
    
    def __str__(self) -> str:
        return f"𝓢({self.entity})"


@dataclass
class Stimulus:
    """
    Stimulus (ξ): Any external or internal change that perturbs stillness.
    
    Stimuli are the sparks that ignite sensation. If A ∈ 𝓢 at time t,
    then a non-zero stimulus ξ breaks that stillness.
    Formal: ξ ⇒ ∂A/∂t ≠ 0
    """
    name: str
    payload: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    intensity: float = 1.0
    
    def __str__(self) -> str:
        return f"ξ({self.name})"


@dataclass
class Sensation:
    """
    Sensation (σ): The immediate, raw registration of a stimulus.
    
    It is the pre-conceptual, phenomenal experience before interpretation.
    Formal: A relation between the observer and the stimulus source.
    """
    source: str
    observer: str
    raw_experience: Any
    timestamp: float = field(default_factory=time.time)
    modality: str = "unspecified"  # visual, auditory, tactile, etc.
    
    def __str__(self) -> str:
        return f"σ({self.modality})"


@dataclass
class Observer:
    """
    Observer (▢): The witnessing entity that experiences sensations.
    
    The observer provides the center from which sensations are experienced and measured.
    Implicitly present in every measurement.
    Formal: ξ ↦ ▢
    """
    name: str
    position: Dict[str, Any] = field(default_factory=dict)
    calibrated: bool = False
    saturation_level: float = 0.0  # 0.0 to 1.0
    
    def is_saturated(self) -> bool:
        """Check if observer has reached saturation (overload)."""
        return self.saturation_level >= 1.0
    
    def reset(self) -> None:
        """Reset observer to baseline state."""
        self.saturation_level = 0.0
    
    def __str__(self) -> str:
        return f"▢({self.name})"


@dataclass
class Boundary:
    """
    Boundary (∂): The delineation between self and other.
    
    Boundaries allow the observer to say "this is here, that is there,"
    preventing sensory confusion.
    """
    label: str
    inside: Set[str] = field(default_factory=set)
    outside: Set[str] = field(default_factory=set)
    
    def crosses(self, entity: str) -> bool:
        """Check if entity crosses the boundary."""
        return entity in self.inside or entity in self.outside
    
    def __str__(self) -> str:
        return f"∂({self.label})"


@dataclass
class Measurement:
    """
    Measurement (μ): The operator that captures raw sensation into stable representation.
    
    It is the bridge from the empirical to the symbolic, compressing experience into information.
    Formal: μ: σ ↦ (value, unit)
    """
    name: str
    value: Any
    unit: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    compressed_from: Optional[str] = None  # What was lost in compression
    
    def to_glyph(self) -> str:
        """Convert measurement to its glyphic form: ⧇"""
        return f"⧇({self.name}={self.value}{self.unit})"
    
    def __str__(self) -> str:
        return f"μ({self.name}: {self.value}{self.unit})"


@dataclass
class Pattern:
    """
    Pattern (P): A perceived regularity or structure across multiple measurements.
    
    Pattern-recognition is both a primitive ability and an active operator.
    Formal: P = f(σ₁, σ₂, … σₙ)
    """
    name: str
    instances: List[Measurement] = field(default_factory=list)
    regularity_score: float = 0.0  # 0.0 to 1.0
    
    def add_instance(self, m: Measurement) -> None:
        """Add a measurement instance to the pattern."""
        self.instances.append(m)
    
    def detect_regularity(self) -> float:
        """Calculate regularity score based on variance."""
        if len(self.instances) < 2:
            return 0.0
        
        # Simple heuristic: low variance = high regularity
        values = [m.value for m in self.instances if isinstance(m.value, (int, float))]
        if not values:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std_dev = math.sqrt(variance)
        
        # Normalize: high regularity when std_dev is low relative to mean
        if mean == 0:
            return 1.0 if std_dev == 0 else 0.0
        
        regularity = max(0.0, 1.0 - (std_dev / abs(mean)))
        self.regularity_score = regularity
        return regularity
    
    def to_glyph(self) -> str:
        """Convert pattern to its glyphic form: ⧀"""
        return f"⧀({self.name})"
    
    def __str__(self) -> str:
        return f"P({self.name}, n={len(self.instances)}, r={self.regularity_score:.2f})"


@dataclass
class Memory:
    """
    Memory (M): The retention of past sensations or measured patterns.
    
    Provides context for new encounters and allows for recognition or expectation.
    Formal: A set of past observation relations preserved over time.
    """
    traces: Dict[str, List[Measurement]] = field(default_factory=dict)
    
    def store(self, key: str, measurement: Measurement) -> None:
        """Store a measurement in memory."""
        if key not in self.traces:
            self.traces[key] = []
        self.traces[key].append(measurement)
    
    def recall(self, key: str) -> Optional[List[Measurement]]:
        """Recall measurements by key."""
        return self.traces.get(key)
    
    def __str__(self) -> str:
        return f"M({len(self.traces)} traces)"


class Silence:
    """
    Silence (∅): The conceptual absorber of experience.
    
    The state where no signal remains. Denoted by ∅ or [ ], it is both the origin
    from which sensation arises and the terminus to which it must return.
    """
    
    @staticmethod
    def symbol() -> str:
        return "∅"
    
    @staticmethod
    def frame() -> str:
        return "[ ]"
    
    @staticmethod
    def is_silent(measurement: Measurement) -> bool:
        """Check if measurement represents silence."""
        return measurement.value == 0 or measurement.value is None


# ============================================================
# Part I: The Six Empirical Axioms (A1-A6)
# ============================================================

class EmpiricalAxioms:
    """
    The Six Axioms that define the integrity of the Empirical Lens.
    These are operational rules for inquiry, not merely philosophical.
    """
    
    @staticmethod
    def a1_repeatability_as_anchor(trial_count: int, success_threshold: float = 0.7) -> bool:
        """
        A1: Repeatability as Anchor
        If a statement is empirical, there exists a trial class within which it can be re-seen.
        Intuition: no loop, no trust.
        """
        return trial_count > 0 and success_threshold > 0.5
    
    @staticmethod
    def a2_framed_objectivity(frame: str, transformations: List[str]) -> bool:
        """
        A2: Framed Objectivity
        Objectivity is invariance under declared transformations of the observer/instrument,
        not the absence of the observer.
        """
        return len(frame) > 0 and len(transformations) > 0
    
    @staticmethod
    def a3_measurement_as_compression(original_dims: int, compressed_dims: int) -> float:
        """
        A3: Measurement as Compression
        Every measurement collapses high-dimensional relation into bounded value.
        Returns compression ratio.
        """
        if original_dims == 0:
            return 0.0
        return compressed_dims / original_dims
    
    @staticmethod
    def a4_control_as_proof(perturbation: Any, response_pattern: Pattern) -> bool:
        """
        A4: Control as Proof (Minimal Causality)
        A causal claim requires stable mapping from controlled intervention to patterned response.
        """
        return response_pattern.regularity_score > 0.6
    
    @staticmethod
    def a5_noise_as_proposal(residuals: List[float]) -> bool:
        """
        A5: Noise as Sacrificial Fire (Statistical Coherence)
        Outliers are proposals. We treat them as noise only after model articulation
        and residuals show no structure.
        """
        if not residuals:
            return True
        # Check if residuals have structure (autocorrelation)
        mean = sum(residuals) / len(residuals)
        variance = sum((r - mean) ** 2 for r in residuals) / len(residuals)
        # Low variance = low structure = true noise
        return variance < 0.1
    
    @staticmethod
    def a6_time_as_adjudicator(duration: float, stability_threshold: float = 1.0) -> float:
        """
        A6: Time as the Adjudicator
        Empirical truth strengthens with the length of its echo.
        Returns trust score.
        """
        return min(1.0, duration / stability_threshold)


# ============================================================
# Part I: The Minimal Ontology of an Experiment
# ============================================================

@dataclass
class System:
    """System (S): The entity or field under study. Represented as ◎."""
    name: str
    state: Dict[str, Any] = field(default_factory=dict)
    
    def to_glyph(self) -> str:
        return f"◎({self.name})"


@dataclass
class Instrument:
    """Instrument (I): A relational mediator that co-creates a value with the System. Represented as ◚."""
    name: str
    calibrated: bool = False
    coupling: float = 0.0  # Degree of coupling with system (0=independent, 1=fully coupled)
    
    def calibrate(self) -> None:
        """Calibrate instrument to truth."""
        self.calibrated = True
    
    def to_glyph(self) -> str:
        return f"◚({self.name})"


@dataclass
class Protocol:
    """Protocol (P): The algorithm that constrains Context, defining setup, timing, and sampling rules. Represented as ≡."""
    name: str
    steps: List[str] = field(default_factory=list)
    
    def add_step(self, step: str) -> None:
        self.steps.append(step)
    
    def to_glyph(self) -> str:
        return f"≡({self.name})"


@dataclass
class Model:
    """Model (M): A compressive story that maps inputs to outputs. Represented as ≅."""
    name: str
    parameters: Dict[str, float] = field(default_factory=dict)
    drift_score: float = 0.0  # μ𝒹: How far model has drifted from reality
    
    def predict(self, input_val: Any) -> Any:
        """Predict output from input."""
        return input_val  # Placeholder
    
    def to_glyph(self) -> str:
        return f"≅({self.name})"


@dataclass
class Record:
    """Record (D): The trace left by Measure function over repeated trials. Represented as Σ(v)."""
    measurements: List[Measurement] = field(default_factory=list)
    
    def add(self, m: Measurement) -> None:
        self.measurements.append(m)
    
    def to_glyph(self) -> str:
        return f"Σ({len(self.measurements)})"


@dataclass
class EmpiricalClaim:
    """
    An empirical claim φ is a structured tuple:
    φ := ⟨Statement, Frame F, Repeatability spec, Control spec, Diagnostics⟩
    
    Two identical statements with different frames are fundamentally different claims.
    """
    statement: str
    frame: str
    repeatability: float
    control: float
    diagnostics: str
    
    def is_valid(self) -> bool:
        """Validate using the Encounter Axiom."""
        return EncounterAxiom.validate_claim(
            self.statement, self.frame, self.repeatability, 
            self.control, self.diagnostics
        )
    
    def __str__(self) -> str:
        return f"φ⟨{self.statement}⟩ in [{self.frame}]"


# ============================================================
# Part II: The Invariance Ladder - How Truth Hardens
# ============================================================

class InvarianceRung(Enum):
    """The ladder of increasing invariance - how objectivity hardens."""
    INTRA_LAB = 1          # Same team, different days
    CROSS_INSTRUMENT = 2   # Different tools, same protocol
    CROSS_SITE = 3         # Different teams, different locations
    CROSS_SPECIES = 4      # Different domains/materials
    CROSS_PARADIGM = 5     # Different theoretical models


@dataclass
class InvarianceLadder:
    """
    Track how a finding climbs the ladder of invariance.
    Each rung climbed reduces dependence on hidden local relations.
    """
    claim: EmpiricalClaim
    current_rung: InvarianceRung = InvarianceRung.INTRA_LAB
    evidence: Dict[InvarianceRung, List[str]] = field(default_factory=dict)
    
    def climb(self, rung: InvarianceRung, evidence: str) -> None:
        """Climb to a higher rung with supporting evidence."""
        if rung not in self.evidence:
            self.evidence[rung] = []
        self.evidence[rung].append(evidence)
        if rung.value > self.current_rung.value:
            self.current_rung = rung
    
    def trust_score(self) -> float:
        """Calculate trust based on highest rung achieved."""
        return self.current_rung.value / len(InvarianceRung)


# ============================================================
# Part II: From Event-Truth to Echo-Truth
# ============================================================

@dataclass
class EventTruth:
    """Event-Truth: A simple, repeatable observation. "X happened again." """
    event: str
    occurrences: int = 0
    
    def observe(self) -> None:
        self.occurrences += 1


@dataclass
class EchoTruth:
    """
    Echo-Truth: A reliable, patterned response in a downstream field from a specific intervention.
    "ΔX reliably bends field Y over predictable time window."
    
    Formally: Δ at t₀ ⇒ pattern Y over [t₁…t₁+k] with invariance across Repeat
    """
    intervention: str
    response_pattern: Pattern
    time_window: Tuple[float, float]
    invariance_score: float = 0.0
    
    def validate(self) -> bool:
        """Validate echo-truth by checking pattern regularity."""
        return self.response_pattern.regularity_score > 0.7


# ============================================================
# Part III: The Pattern of Forgetting - Empirical Distortion
# ============================================================

class PathStage(Enum):
    """The seven stages of the Pattern of Forgetting."""
    STILLNESS = "stillness"               # Open awareness
    STIMULUS_TRIGGER = "stimulus_trigger" # Instant filing
    SENSATION_COMPRESSED = "sensation_compressed"  # Jump to label
    PATTERN_RIGID = "pattern_rigid"       # Lock-in
    MEASUREMENT_BLIND = "measurement_blind"  # Context-less data
    VALIDATION_RITUAL = "validation_ritual"  # Self-sealing
    CLOSURE = "closure"                   # Curiosity dies


@dataclass
class PatternOfForgetting:
    """
    The degraded cycle where measurement replaces encounter.
    This is over-recognition: mind's efficiency hijacks the loop.
    """
    current_stage: PathStage = PathStage.STILLNESS
    distortion_level: float = 0.0  # 0.0 to 1.0
    
    def advance_stage(self) -> None:
        """Move to the next stage of forgetting."""
        stages = list(PathStage)
        current_idx = stages.index(self.current_stage)
        if current_idx < len(stages) - 1:
            self.current_stage = stages[current_idx + 1]
            self.distortion_level = (current_idx + 1) / len(stages)
    
    def is_degraded(self) -> bool:
        """Check if loop has fully degraded."""
        return self.current_stage == PathStage.CLOSURE


@dataclass
class ModelDrift:
    """
    Model Drift (μ𝒹): The model becomes more important than the phenomenon.
    
    Empirical goal shifts from describing reality to defending the model.
    This is a distortion threshold.
    """
    model: Model
    drift_rate: float = 0.0
    threshold: float = 0.7  # Critical point
    
    def update_drift(self, anomaly_count: int, total_observations: int) -> None:
        """Calculate drift based on ignored anomalies."""
        if total_observations == 0:
            self.drift_rate = 0.0
            return
        self.drift_rate = anomaly_count / total_observations
        self.model.drift_score = self.drift_rate
    
    def has_crossed_threshold(self) -> bool:
        """Check if drift has crossed critical threshold."""
        return self.drift_rate >= self.threshold


@dataclass
class ParadigmCollapse:
    """
    Paradigm Collapse (𝓘𝓣): Inversion Threshold where established truth becomes distortion.
    
    The paradigm becomes so successful it blinds adherents to new phenomena.
    """
    paradigm_name: str
    success_domain: str
    blind_spots: List[str] = field(default_factory=list)
    inversion_point: bool = False
    
    def add_blind_spot(self, phenomenon: str) -> None:
        """Add a phenomenon the paradigm cannot explain."""
        self.blind_spots.append(phenomenon)
        if len(self.blind_spots) > 3:  # Threshold
            self.inversion_point = True
    
    def has_inverted(self) -> bool:
        """Check if paradigm has reached inversion threshold."""
        return self.inversion_point


# ============================================================
# Part III: The Path of Remembering - The Stillness Pathway
# ============================================================

@dataclass
class PathOfRemembering:
    """
    The healthy, integrated use of the lens where observation is an act of presence.
    This is the path back from forgetting.
    """
    steps_completed: List[str] = field(default_factory=list)
    saturation_level: float = 0.0  # Progress toward Lens Saturation
    
    def complete_step(self, step: str) -> None:
        """Complete a step on the path of remembering."""
        self.steps_completed.append(step)
        self.saturation_level = len(self.steps_completed) / 8.0  # 8 steps total
    
    def is_saturated(self) -> bool:
        """Check if Lens Saturation has been achieved."""
        return self.saturation_level >= 1.0


# ============================================================
# Part III: Pre-Sensing Protocol (60-90 seconds)
# ============================================================

@dataclass
class PreSensingProtocol:
    """
    A repeatable method to enter the Path of Remembering before observation.
    Takes 60-90 seconds and roots the observer in whole-field awareness.
    """
    relational_check: bool = False
    logical_check: bool = False
    symbolic_check: bool = False
    empirical_check: bool = False
    stillness_achieved: bool = False
    
    def run(self) -> bool:
        """Execute the complete protocol."""
        self.relational_check = True  # Feel the link, drop roles
        self.logical_check = True      # Name frame lightly, check axioms
        self.symbolic_check = True     # Notice pre-loaded labels
        self.empirical_check = True    # Suspend recognition
        self.stillness_achieved = True # Drop sequence, feel whole
        
        return all([
            self.relational_check,
            self.logical_check,
            self.symbolic_check,
            self.empirical_check,
            self.stillness_achieved
        ])
    
    def __str__(self) -> str:
        return f"PreSensing(complete={self.stillness_achieved})"


# ============================================================
# Part IV: Empirical Pattern Cycles and Transformation Loops
# ============================================================

@dataclass
class StimulusResponseLoop:
    """
    The basic feedback loop: ξ → σ → reaction → new ξ
    Tends toward equilibrium (negative feedback) or runaway (positive feedback).
    """
    stimuli: List[Stimulus] = field(default_factory=list)
    responses: List[Any] = field(default_factory=list)
    is_stable: bool = False
    
    def add_cycle(self, stimulus: Stimulus, response: Any) -> None:
        """Add a stimulus-response pair."""
        self.stimuli.append(stimulus)
        self.responses.append(response)
    
    def check_stability(self) -> bool:
        """Check if loop has stabilized."""
        if len(self.stimuli) < 3:
            return False
        # Simple heuristic: check if last 3 responses are similar
        recent = self.responses[-3:]
        if all(isinstance(r, (int, float)) for r in recent):
            variance = sum((r - sum(recent)/3) ** 2 for r in recent) / 3
            self.is_stable = variance < 0.1
        return self.is_stable


@dataclass
class CalibrationCycle:
    """
    Ongoing adjustment of measurement apparatus to maintain alignment with reality.
    observation → error detected → calibration → improved observation
    """
    instrument: Instrument
    error_history: List[float] = field(default_factory=list)
    
    def detect_error(self, measured: float, actual: float) -> float:
        """Detect and record error."""
        error = abs(measured - actual)
        self.error_history.append(error)
        return error
    
    def calibrate(self) -> None:
        """Perform calibration to reduce error."""
        self.instrument.calibrate()
        self.error_history.clear()


# ============================================================
# Part IV: Empirical Distortions and Phenomena
# ============================================================

@dataclass
class EmpiricalDrift:
    """Gradual deviation of measurement from truth over time."""
    baseline: float
    current: float
    drift_per_time: float = 0.0
    
    def measure_drift(self, time_delta: float) -> float:
        """Calculate drift rate."""
        if time_delta == 0:
            return 0.0
        self.drift_per_time = (self.current - self.baseline) / time_delta
        return self.drift_per_time


@dataclass
class EmpiricalCollapse:
    """Sudden breakdown of observation capacity due to overstimulation or apophenia."""
    observer: Observer
    overload_threshold: float = 1.0
    
    def check_overload(self) -> bool:
        """Check if observer has experienced collapse."""
        return self.observer.saturation_level >= self.overload_threshold


# ============================================================
# Part V: The Research Pipeline - Seven-Stage Loop
# ============================================================

@dataclass
class ResearchPipeline:
    """
    The seven-stage empirical inquiry loop implementing the axioms.
    Maps to the universal logical pattern: 𝓢 → Δ → F → R → ⇒ → Ω → 𝓢
    """
    name: str
    frame: str = ""
    raw_data: List[Any] = field(default_factory=list)
    structured_data: List[Measurement] = field(default_factory=list)
    hypotheses: List[str] = field(default_factory=list)
    findings: List[EmpiricalClaim] = field(default_factory=list)
    current_stage: int = 1
    
    def stage_1_frame_definition(self, frame: str) -> None:
        """Stage 1: Explicitly name the frame F."""
        self.frame = frame
        self.current_stage = 2
    
    def stage_2_source_capture(self, data: List[Any]) -> None:
        """Stage 2: Gather raw data."""
        self.raw_data.extend(data)
        self.current_stage = 3
    
    def stage_3_structuring(self) -> None:
        """Stage 3: Normalize data, embed context."""
        for datum in self.raw_data:
            m = Measurement(
                name=f"datum_{len(self.structured_data)}",
                value=datum,
                context={"frame": self.frame}
            )
            self.structured_data.append(m)
        self.current_stage = 4
    
    def stage_4_preliminary_patterning(self) -> None:
        """Stage 4: Spot patterns, generate hypotheses."""
        if len(self.structured_data) >= 3:
            self.hypotheses.append("Pattern detected in data")
        self.current_stage = 5
    
    def stage_5_formal_testing(self) -> None:
        """Stage 5: Apply formal methods, validate patterns."""
        for hyp in self.hypotheses:
            claim = EmpiricalClaim(
                statement=hyp,
                frame=self.frame,
                repeatability=0.8,
                control=0.7,
                diagnostics="formal testing applied"
            )
            self.findings.append(claim)
        self.current_stage = 6
    
    def stage_6_integration(self) -> None:
        """Stage 6: Feed findings into other lenses."""
        # Placeholder for cross-lens integration
        self.current_stage = 7
    
    def stage_7_feedback(self) -> None:
        """Stage 7: Treat result as living echo, iterate."""
        self.current_stage = 1  # Loop back


# ============================================================
# Part V: The Ladder of Empirical Rigor
# ============================================================

class RigorRung(Enum):
    """Hierarchy of increasing rigor and certainty in empirical methods."""
    ANECDOTAL = 1          # Single informal observation
    CASE_STUDY = 2         # Detailed single instance
    CORRELATIONAL = 3      # Statistical patterns
    CONTROLLED_EXPERIMENT = 4  # Causal isolation
    META_ANALYSIS = 5      # Synthesis of multiple studies


# ============================================================
# Part X: The Living Arc - From Stillness to Stillness
# ============================================================

@dataclass
class LivingArc:
    """
    The grand empirical arc: ∅ → 𝓢 → ξ ⇨ σ ⇨ μ ⇨ P … Ω ⇨ ∅ → 𝓢
    
    A cycle of knowing that begins in stillness, moves through sensation,
    often descends into forgetting, and returns to re-membering.
    """
    stages: List[str] = field(default_factory=list)
    current: str = "∅"  # Silence
    
    def trace_arc(self) -> List[str]:
        """Return the complete arc sequence."""
        return ["∅", "𝓢", "ξ", "σ", "μ", "P", "Ω", "∅", "𝓢"]
    
    def advance(self) -> str:
        """Advance through the arc."""
        arc = self.trace_arc()
        if self.current in arc:
            idx = arc.index(self.current)
            if idx < len(arc) - 1:
                self.current = arc[idx + 1]
        return self.current


# ============================================================
# Demo: The Complete Empirical Journey
# ============================================================

def _demo() -> None:
    """Demonstrate the Unified Empirical Lens."""
    print("=" * 80)
    print("Unified Empirical Lens - The Sacred Detour of Sensing")
    print("=" * 80)
    
    # Part 0: Field Zero
    print("\n📖 Part 0: Field Zero - The Pre-Empirical State")
    print("=" * 80)
    
    field = FieldZero()
    print(f"Field Zero state: {field.state}")
    print(f"Differentiated: {field.differentiated}")
    
    stimulus = field.collapse()
    print(f"Collapsed into stimulus: {stimulus}")
    
    # Part I: The Encounter Axiom
    print("\n📖 Part I: The Encounter Axiom")
    print("=" * 80)
    
    print(f"Axiom: {EncounterAxiom.axiom_statement()}")
    
    # Create empirical claim
    claim = EmpiricalClaim(
        statement="Temperature rises with sunlight exposure",
        frame="controlled laboratory, 20°C baseline",
        repeatability=0.85,
        control=0.9,
        diagnostics="thermometer calibrated, 10 trials"
    )
    print(f"\nEmpirical Claim: {claim}")
    print(f"Valid: {claim.is_valid()}")
    
    # Part I: Core Primitives
    print("\n📖 Part I: Core Primitives")
    print("=" * 80)
    
    stillness = Stillness("observer_1")
    print(f"Stillness: {stillness}")
    
    stimulus = Stimulus("light_flash", {"intensity": 100, "duration": 0.5})
    print(f"Stimulus: {stimulus}")
    
    sensation = Sensation("light_source", "observer_1", "bright white flash", modality="visual")
    print(f"Sensation: {sensation}")
    
    observer = Observer("scientist_a", {"room": "lab_1"})
    print(f"Observer: {observer}")
    
    measurement = Measurement("brightness", 850, "lumens", {"instrument": "photometer"})
    print(f"Measurement: {measurement}")
    print(f"Glyph: {measurement.to_glyph()}")
    
    # Part I: The Six Axioms
    print("\n📖 Part I: The Six Empirical Axioms")
    print("=" * 80)
    
    print(f"A1 (Repeatability): {EmpiricalAxioms.a1_repeatability_as_anchor(10, 0.8)}")
    print(f"A2 (Framed Objectivity): {EmpiricalAxioms.a2_framed_objectivity('lab_frame', ['rotate_instrument', 'change_observer'])}")
    print(f"A3 (Compression Ratio): {EmpiricalAxioms.a3_measurement_as_compression(1000, 10):.2f}")
    
    pattern = Pattern("daily_cycle")
    pattern.instances = [
        Measurement("temp", 20.0, "°C"),
        Measurement("temp", 21.0, "°C"),
        Measurement("temp", 20.5, "°C"),
    ]
    pattern.detect_regularity()
    print(f"A4 (Control as Proof): {EmpiricalAxioms.a4_control_as_proof('heat', pattern)}")
    print(f"A5 (Noise as Proposal): {EmpiricalAxioms.a5_noise_as_proposal([0.01, -0.02, 0.01])}")
    print(f"A6 (Time as Adjudicator): {EmpiricalAxioms.a6_time_as_adjudicator(5.0, 3.0):.2f}")
    
    # Part II: The Invariance Ladder
    print("\n📖 Part II: The Invariance Ladder")
    print("=" * 80)
    
    ladder = InvarianceLadder(claim)
    ladder.climb(InvarianceRung.INTRA_LAB, "Replicated by same team")
    ladder.climb(InvarianceRung.CROSS_INSTRUMENT, "Confirmed with different thermometer")
    ladder.climb(InvarianceRung.CROSS_SITE, "Reproduced at 3 universities")
    
    print(f"Current rung: {ladder.current_rung.name}")
    print(f"Trust score: {ladder.trust_score():.2f}")
    
    # Part II: Echo-Truth
    print("\n📖 Part II: From Event-Truth to Echo-Truth")
    print("=" * 80)
    
    event = EventTruth("sunrise")
    for _ in range(5):
        event.observe()
    print(f"Event-Truth: '{event.event}' observed {event.occurrences} times")
    
    echo = EchoTruth(
        "add_fertilizer",
        pattern,
        (0.0, 30.0),
        invariance_score=0.85
    )
    print(f"Echo-Truth: {echo.intervention} → pattern over {echo.time_window} days")
    print(f"Validated: {echo.validate()}")
    
    # Part III: The Pattern of Forgetting
    print("\n📖 Part III: The Pattern of Forgetting")
    print("=" * 80)
    
    forgetting = PatternOfForgetting()
    print(f"Initial stage: {forgetting.current_stage.value}")
    
    for _ in range(3):
        forgetting.advance_stage()
        print(f"  → {forgetting.current_stage.value} (distortion: {forgetting.distortion_level:.2f})")
    
    # Model Drift
    model = Model("newtonian_physics", {"G": 6.67e-11})
    drift = ModelDrift(model)
    drift.update_drift(anomaly_count=15, total_observations=100)
    print(f"\nModel Drift: {drift.drift_rate:.2f}")
    print(f"Threshold crossed: {drift.has_crossed_threshold()}")
    
    # Paradigm Collapse
    paradigm = ParadigmCollapse("classical_mechanics", "terrestrial_motion")
    paradigm.add_blind_spot("mercury_precession")
    paradigm.add_blind_spot("photoelectric_effect")
    paradigm.add_blind_spot("blackbody_radiation")
    paradigm.add_blind_spot("atomic_spectra")
    print(f"\nParadigm: {paradigm.paradigm_name}")
    print(f"Blind spots: {len(paradigm.blind_spots)}")
    print(f"Has inverted: {paradigm.has_inverted()}")
    
    # Part III: Pre-Sensing Protocol
    print("\n📖 Part III: Pre-Sensing Protocol")
    print("=" * 80)
    
    protocol = PreSensingProtocol()
    success = protocol.run()
    print(f"Protocol: {protocol}")
    print(f"Ready to observe: {success}")
    
    # Part V: Research Pipeline
    print("\n📖 Part V: The Research Pipeline")
    print("=" * 80)
    
    pipeline = ResearchPipeline("temperature_study")
    pipeline.stage_1_frame_definition("controlled_lab_environment")
    pipeline.stage_2_source_capture([20.0, 21.5, 20.8, 22.0])
    pipeline.stage_3_structuring()
    pipeline.stage_4_preliminary_patterning()
    pipeline.stage_5_formal_testing()
    
    print(f"Pipeline: {pipeline.name}")
    print(f"Frame: {pipeline.frame}")
    print(f"Raw data points: {len(pipeline.raw_data)}")
    print(f"Structured measurements: {len(pipeline.structured_data)}")
    print(f"Hypotheses: {len(pipeline.hypotheses)}")
    print(f"Findings: {len(pipeline.findings)}")
    print(f"Current stage: {pipeline.current_stage}")
    
    # Part X: The Living Arc
    print("\n📖 Part X: The Living Arc - From Stillness to Stillness")
    print("=" * 80)
    
    arc = LivingArc()
    full_arc = arc.trace_arc()
    print(f"Complete Arc: {' → '.join(full_arc)}")
    print(f"\nTracing the journey:")
    for stage in full_arc:
        arc.current = stage
        print(f"  {stage}", end="")
        if stage == "𝓢":
            print(" (Stillness - pregnant silence)")
        elif stage == "ξ":
            print(" (Stimulus - first ripple)")
        elif stage == "σ":
            print(" (Sensation - tasting duality)")
        elif stage == "μ":
            print(" (Measurement - encoding the real)")
        elif stage == "P":
            print(" (Pattern - structures emerge)")
        elif stage == "Ω":
            print(" (Overload - forgetting)")
        elif stage == "∅":
            print(" (Silence - remembering)")
        else:
            print()
    
    print("\n" + "=" * 80)
    print("✨ The Sacred Detour Complete - From Silence to Silence")
    print("=" * 80)


if __name__ == "__main__":
    _demo()
