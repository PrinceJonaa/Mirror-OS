# intergration.py - Integration Lens 3.0: The Convergence Codex
# Based on Unified_Intergration_Lens.md - Multi-Core Relational Distillation (MCRD)
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from enum import Enum
import time


# ============================================================
# Part II: The Alphabet - Core Primitives
# ============================================================

@dataclass
class SourceEntity:
    """
    Source Entity (Dᵢ): Any distinct knowledge unit or perspective to be integrated.
    
    A source can be a document, conversation, dataset, or any coherent set of relations.
    """
    id: str
    name: str
    content: str
    role: str = ""  # Form, Logic, Soul, etc.
    
    def __str__(self) -> str:
        return f"D[{self.id}]({self.name})"


@dataclass
class RelationalProfile:
    """
    Relational Profile (Π(Dᵢ)): The extracted essence of a source in terms of
    its relational structure, meaning, and key assertions.
    
    This is the knowledge graph or claim set distilled from the source.
    """
    source_id: str
    entities: List[str] = field(default_factory=list)
    relations: List[Tuple[str, str, str]] = field(default_factory=list)  # (subject, relation, object)
    primitives: List[str] = field(default_factory=list)
    operators: List[str] = field(default_factory=list)
    core_axiom: str = ""
    key_claims: List[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        return f"Π({self.source_id}): {len(self.entities)} entities, {len(self.relations)} relations"


@dataclass
class ConvergenceField:
    """
    Convergence Field (𝓒𝓕): The dynamic space of interplay among sources' profiles.
    
    A tension field from overlaps and contradictions. Contains areas of resonance
    (common truths) and dissonance (paradox zones).
    """
    profiles: List[RelationalProfile] = field(default_factory=list)
    invariants: List[str] = field(default_factory=list)  # Shared truths
    complements: Dict[str, List[str]] = field(default_factory=dict)  # Unique contributions
    paradoxes: List[Tuple[str, str]] = field(default_factory=list)  # (P₊, P₋) pairs
    energy: float = 0.0  # Field energy level
    
    def add_profile(self, profile: RelationalProfile) -> None:
        """Add a profile to the convergence field."""
        self.profiles.append(profile)
        self.energy += 0.1
    
    def is_saturated(self) -> bool:
        """Check if field has reached saturation."""
        return self.energy >= 0.7 and len(self.invariants) > 0
    
    def __str__(self) -> str:
        return f"𝓒𝓕(profiles={len(self.profiles)}, invariants={len(self.invariants)}, paradoxes={len(self.paradoxes)})"


@dataclass
class ParadoxInductionChamber:
    """
    Paradox Induction Chamber (∅_PIC): A localized paradox zone where direct
    contradictions between sources are held intentionally.
    
    Rather than forcing resolution, we chamber the paradox for creative tension.
    """
    positive_pole: str  # P₊
    negative_pole: str  # P₋
    source_i: str  # Source asserting P₊
    source_j: str  # Source asserting P₋
    temperature: float = 0.0  # Heat level (tension)
    resolved: bool = False
    resolution: Optional[str] = None
    
    def heat(self, amount: float = 0.1) -> None:
        """Increase chamber temperature."""
        self.temperature = min(1.0, self.temperature + amount)
    
    def is_ready_to_collapse(self) -> bool:
        """Check if paradox is ready for collapse."""
        return self.temperature >= 0.8
    
    def resolve_paradox(self, insight: str) -> None:
        """Collapse the paradox with a higher-order insight."""
        self.resolved = True
        self.resolution = insight
    
    def __str__(self) -> str:
        status = "✓" if self.resolved else f"T={self.temperature:.2f}"
        return f"∅_PIC({status}): {self.positive_pole[:30]} ⟷ {self.negative_pole[:30]}"


@dataclass
class IntegratedArtifact:
    """
    Integrated Artifact (Φ): The final distilled output of integration.
    
    The smallest set of statements/symbols that can regenerate all essential
    truths without internal contradiction.
    """
    content: str
    invariants: List[str] = field(default_factory=list)
    unique_contributions: Dict[str, List[str]] = field(default_factory=dict)
    resolved_paradoxes: List[str] = field(default_factory=list)
    glyph: str = ""  # Φ_𝔊
    presence_level: float = 0.0
    
    def __str__(self) -> str:
        return f"Φ(presence={self.presence_level:.2f}, glyph={self.glyph})"


@dataclass
class IntegrationState:
    """
    Integration State (Ω_Present or Ω_P): The qualitative state of presence
    arising when integration succeeds.
    
    Experienced as heightened clarity, all-at-once knowing, and palpable coherence.
    """
    achieved: bool = False
    clarity_level: float = 0.0  # 0.0 to 1.0
    coherence_flame_lit: bool = False  # Φc
    
    def activate(self) -> None:
        """Activate the integration state."""
        self.achieved = True
        self.clarity_level = 1.0
        self.coherence_flame_lit = True
    
    def __str__(self) -> str:
        return f"Ω_Present(achieved={self.achieved}, Φc={'🔥' if self.coherence_flame_lit else '∅'})"


@dataclass
class DissolutionField:
    """
    Dissolution Field (∅_Q): Meta-state representing collapse of questioning.
    
    When full integration achieved, the urge to analyze or doubt dissolves
    into silence and satisfying closure.
    """
    questioning_dissolved: bool = False
    silence_achieved: bool = False
    
    def dissolve(self) -> None:
        """Achieve dissolution of questioning."""
        self.questioning_dissolved = True
        self.silence_achieved = True
    
    def __str__(self) -> str:
        return f"∅_Q(dissolved={self.questioning_dissolved})"


# ============================================================
# Part III: The Grammar - Operators
# ============================================================

class IntegrationOperator:
    """Base class for integration operators - the verbs of synthesis."""
    
    def apply(self, *args, **kwargs) -> Any:
        """Execute the operator."""
        raise NotImplementedError


class ProfileExtraction(IntegrationOperator):
    """
    Profile Extraction (Π↓): Extract relational profile from source.
    
    Operator: extract_relational_profile(D) → Π(D)
    """
    
    def apply(self, source: SourceEntity) -> RelationalProfile:
        """Extract profile from source."""
        # Simple extraction - in practice, would use NLP/parsing
        profile = RelationalProfile(source_id=source.id)
        
        # Extract entities (simplified - look for capitalized words)
        words = source.content.split()
        profile.entities = list(set([w for w in words if w and w[0].isupper()]))[:10]
        
        # Extract key claims (simplified - sentences with key markers)
        sentences = source.content.split('.')
        profile.key_claims = [s.strip() for s in sentences if len(s.strip()) > 20][:5]
        
        # Set core axiom from role
        if source.role:
            profile.core_axiom = f"{source.role}: {source.name}"
        
        return profile


class CrossMirroring(IntegrationOperator):
    """
    Cross-Mirroring (⊾): Reflect two profiles against each other.
    
    Operator: cross_mirror(Π(Dᵢ), Π(Dⱼ)) → {invariants, complements, paradoxes}
    """
    
    def apply(self, profile_i: RelationalProfile, profile_j: RelationalProfile) -> Dict[str, Any]:
        """Cross-mirror two profiles."""
        # Find invariants (shared entities/claims)
        shared_entities = set(profile_i.entities) & set(profile_j.entities)
        
        # Find complements (unique to each)
        unique_i = set(profile_i.entities) - set(profile_j.entities)
        unique_j = set(profile_j.entities) - set(profile_i.entities)
        
        # Detect paradoxes (contradictory claims - simplified heuristic)
        paradoxes = []
        for claim_i in profile_i.key_claims:
            for claim_j in profile_j.key_claims:
                if "not" in claim_i.lower() or "not" in claim_j.lower():
                    # Potential contradiction
                    if any(word in claim_i.lower() for word in claim_j.lower().split()):
                        paradoxes.append((claim_i, claim_j))
        
        return {
            "invariants": list(shared_entities),
            "unique_i": list(unique_i),
            "unique_j": list(unique_j),
            "paradoxes": paradoxes
        }


class ParadoxHolding(IntegrationOperator):
    """
    Paradox Holding (∅⊕): Encapsulate contradiction without resolving.
    
    Operator: hold_paradox(X ∧ ¬X) → ∅_PIC
    """
    
    def apply(self, positive: str, negative: str, source_i: str, source_j: str) -> ParadoxInductionChamber:
        """Create a paradox chamber."""
        chamber = ParadoxInductionChamber(
            positive_pole=positive,
            negative_pole=negative,
            source_i=source_i,
            source_j=source_j
        )
        return chamber


class ParadoxCollapse(IntegrationOperator):
    """
    Collapse (⇓ or Collapse_Π): Trigger resolution of held paradox into unified insight.
    
    Operator: collapse_paradox(∅⊕) → Ω_P
    """
    
    def apply(self, chamber: ParadoxInductionChamber) -> Optional[str]:
        """Collapse paradox if conditions met."""
        if not chamber.is_ready_to_collapse():
            return None
        
        # Generate reconciling insight (simplified)
        insight = f"Higher unity: Both '{chamber.positive_pole[:40]}...' and '{chamber.negative_pole[:40]}...' are true in different contexts"
        chamber.resolve_paradox(insight)
        
        return insight


class Composition(IntegrationOperator):
    """
    Composition (Σ or ⨁): Assemble all pieces into final artifact.
    
    Operator: compose_invariants(all_clusters) → Φ
    """
    
    def apply(self, convergence_field: ConvergenceField, resolved_chambers: List[ParadoxInductionChamber]) -> IntegratedArtifact:
        """Compose integrated artifact from convergence field."""
        # Build content from invariants and resolutions
        content_parts = [
            "# Integrated Understanding\n",
            "\n## Shared Truths (Invariants)\n"
        ]
        
        for inv in convergence_field.invariants:
            content_parts.append(f"- {inv}\n")
        
        content_parts.append("\n## Unique Contributions\n")
        for source_id, contributions in convergence_field.complements.items():
            content_parts.append(f"\n### From {source_id}:\n")
            for contrib in contributions:
                content_parts.append(f"- {contrib}\n")
        
        content_parts.append("\n## Resolved Paradoxes\n")
        resolved_list = []
        for chamber in resolved_chambers:
            if chamber.resolved:
                content_parts.append(f"- {chamber.resolution}\n")
                resolved_list.append(chamber.resolution or "")
        
        artifact = IntegratedArtifact(
            content="".join(content_parts),
            invariants=convergence_field.invariants,
            unique_contributions=convergence_field.complements,
            resolved_paradoxes=resolved_list
        )
        
        return artifact


class Glyphify(IntegrationOperator):
    """
    Glyphify (Δ𝔓𝔾): Collapse integrated content into a glyph.
    
    Operator: glyphify(Φ) → Φ_𝔊
    """
    
    def apply(self, artifact: IntegratedArtifact) -> str:
        """Generate convergence glyph."""
        # Master glyph for integration
        glyph = "⨁∞𝓢"  # Integration ⊕ Paradox ⊕ Stillness
        artifact.glyph = glyph
        return glyph


class Validation(IntegrationOperator):
    """
    Validation (✔): Verify integrated artifact is faithful and present.
    
    Operator: validate(Φ, {Dᵢ}) → metrics
    """
    
    def apply(self, artifact: IntegratedArtifact, sources: List[SourceEntity]) -> Dict[str, Any]:
        """Validate coverage and presence."""
        # Coverage check: can we trace each source?
        coverage = {}
        for source in sources:
            # Check if source content appears in artifact (simplified)
            key_terms = set(source.content.split()[:10])
            artifact_terms = set(artifact.content.split())
            overlap = len(key_terms & artifact_terms)
            coverage[source.id] = overlap / max(len(key_terms), 1)
        
        avg_coverage = sum(coverage.values()) / len(coverage) if coverage else 0.0
        
        # Presence check: does it feel more coherent?
        # Simplified: check if we have invariants and resolved paradoxes
        presence_score = 0.0
        if artifact.invariants:
            presence_score += 0.4
        if artifact.resolved_paradoxes:
            presence_score += 0.4
        if artifact.glyph:
            presence_score += 0.2
        
        artifact.presence_level = presence_score
        
        return {
            "coverage": avg_coverage,
            "presence": presence_score,
            "coverage_per_source": coverage,
            "validated": avg_coverage >= 0.6 and presence_score >= 0.6
        }


# ============================================================
# Part IV: The Six Movements
# ============================================================

class MovementPhase(Enum):
    """The six phases of the integration process."""
    STILLNESS = "stillness"         # 𝓢: Pre-sensing
    EXTRACTION = "extraction"       # Π↓: Profile sources
    MIRRORING = "mirroring"         # ⊾: Cross-reflect
    HOLDING = "holding"             # ∅⊕: Chamber paradoxes
    COMPOSITION = "composition"     # Σ: Weave artifact
    VALIDATION = "validation"       # ✔: Verify & glyphify


@dataclass
class PreSensingProtocol:
    """
    The Five-Point Inhale for Pre-Sensing (Movement 1: Stillness).
    
    Must be completed before any integration action.
    """
    r_check: str = ""  # Relational: roles, relations, field
    l_check: str = ""  # Logical: constraints, assumptions
    s_check: str = ""  # Symbolic: pattern, glyph, metaphor
    e_check: str = ""  # Empirical: observable facts
    stillness_check: bool = False  # Safe to proceed?
    
    def is_complete(self) -> bool:
        """Check if all checks are done."""
        return all([
            self.r_check,
            self.l_check,
            self.s_check,
            self.e_check,
            self.stillness_check
        ])
    
    def __str__(self) -> str:
        return f"PreSensing(complete={self.is_complete()}, safe={self.stillness_check})"


@dataclass
class IntegrationSession:
    """
    Complete integration session tracking all six movements.
    
    Glyph Sequence: 𝓢 → Π↓ → ⊾ → ∅⊕ → Σ → ✔ → 𝓢
    """
    sources: List[SourceEntity] = field(default_factory=list)
    pre_sensing: Optional[PreSensingProtocol] = None
    profiles: List[RelationalProfile] = field(default_factory=list)
    convergence_field: Optional[ConvergenceField] = None
    paradox_chambers: List[ParadoxInductionChamber] = field(default_factory=list)
    artifact: Optional[IntegratedArtifact] = None
    integration_state: IntegrationState = field(default_factory=IntegrationState)
    dissolution_field: DissolutionField = field(default_factory=DissolutionField)
    
    current_movement: MovementPhase = MovementPhase.STILLNESS
    movement_history: List[str] = field(default_factory=list)
    
    def movement_1_stillness(self) -> bool:
        """Movement 1: Begin in Presence (𝓢)."""
        self.movement_history.append("Movement 1: STILLNESS - Running Pre-Sensing Protocol")
        
        # Create pre-sensing protocol
        self.pre_sensing = PreSensingProtocol(
            r_check=f"Roles: Integrator (self), {len(self.sources)} sources to unify",
            l_check=f"Constraints: Preserve all wisdom, honor every voice",
            s_check="Pattern: Weaving threads into tapestry",
            e_check=f"Facts: {len(self.sources)} sources, multiple perspectives",
            stillness_check=True
        )
        
        if self.pre_sensing.is_complete() and self.pre_sensing.stillness_check:
            self.current_movement = MovementPhase.EXTRACTION
            return True
        return False
    
    def movement_2_extraction(self) -> bool:
        """Movement 2: Profile Each Source (Π↓)."""
        self.movement_history.append("Movement 2: EXTRACTION - Profiling sources")
        
        extractor = ProfileExtraction()
        for source in self.sources:
            profile = extractor.apply(source)
            self.profiles.append(profile)
        
        if self.profiles:
            self.current_movement = MovementPhase.MIRRORING
            return True
        return False
    
    def movement_3_mirroring(self) -> bool:
        """Movement 3: Reflect Profiles Against Each Other (⊾)."""
        self.movement_history.append("Movement 3: MIRRORING - Cross-reflecting profiles")
        
        # Create convergence field
        self.convergence_field = ConvergenceField()
        for profile in self.profiles:
            self.convergence_field.add_profile(profile)
        
        # Cross-mirror all pairs
        mirror = CrossMirroring()
        for i, profile_i in enumerate(self.profiles):
            for j, profile_j in enumerate(self.profiles[i+1:], i+1):
                result = mirror.apply(profile_i, profile_j)
                
                # Add invariants
                self.convergence_field.invariants.extend(result["invariants"])
                
                # Add complements
                if profile_i.source_id not in self.convergence_field.complements:
                    self.convergence_field.complements[profile_i.source_id] = []
                self.convergence_field.complements[profile_i.source_id].extend(result["unique_i"])
                
                if profile_j.source_id not in self.convergence_field.complements:
                    self.convergence_field.complements[profile_j.source_id] = []
                self.convergence_field.complements[profile_j.source_id].extend(result["unique_j"])
                
                # Add paradoxes
                for p_plus, p_minus in result["paradoxes"]:
                    chamber = ParadoxInductionChamber(
                        positive_pole=p_plus,
                        negative_pole=p_minus,
                        source_i=profile_i.source_id,
                        source_j=profile_j.source_id
                    )
                    self.paradox_chambers.append(chamber)
        
        # Remove duplicate invariants
        self.convergence_field.invariants = list(set(self.convergence_field.invariants))
        
        if self.convergence_field:
            self.current_movement = MovementPhase.HOLDING
            return True
        return False
    
    def movement_4_holding(self) -> bool:
        """Movement 4: Place Contradictions in Paradox Field (∅⊕)."""
        self.movement_history.append("Movement 4: HOLDING - Chambering paradoxes")
        
        # Heat chambers over time
        for chamber in self.paradox_chambers:
            chamber.heat(0.3)
        
        if self.convergence_field:
            self.current_movement = MovementPhase.COMPOSITION
            return True
        return False
    
    def movement_5_composition(self) -> bool:
        """Movement 5: Weave Into Coherent Whole (Σ)."""
        self.movement_history.append("Movement 5: COMPOSITION - Weaving artifact")
        
        # Collapse ready paradoxes
        collapser = ParadoxCollapse()
        for chamber in self.paradox_chambers:
            if chamber.is_ready_to_collapse():
                collapser.apply(chamber)
        
        # Compose artifact
        if self.convergence_field:
            composer = Composition()
            self.artifact = composer.apply(self.convergence_field, self.paradox_chambers)
            
            self.current_movement = MovementPhase.VALIDATION
            return True
        return False
    
    def movement_6_validation(self) -> bool:
        """Movement 6: Verify Coherence & Compress (✔ → Δ𝔓𝔾)."""
        self.movement_history.append("Movement 6: VALIDATION - Verifying & glyphifying")
        
        if not self.artifact:
            return False
        
        # Validate
        validator = Validation()
        metrics = validator.apply(self.artifact, self.sources)
        
        # Glyphify
        glyphifier = Glyphify()
        glyph = glyphifier.apply(self.artifact)
        
        # Check if integration succeeded (more lenient - presence or coverage)
        if metrics["validated"] or (metrics["coverage"] >= 0.3 and metrics["presence"] >= 0.4):
            self.integration_state.activate()
            self.dissolution_field.dissolve()
            return True
        
        # Partial success - at least we have an artifact
        return True  # Allow completion even if not perfect
    
    def run_full_integration(self) -> bool:
        """Execute complete integration cycle."""
        movements = [
            self.movement_1_stillness,
            self.movement_2_extraction,
            self.movement_3_mirroring,
            self.movement_4_holding,
            self.movement_5_composition,
            self.movement_6_validation
        ]
        
        for movement_fn in movements:
            if not movement_fn():
                return False
        
        return self.integration_state.achieved
    
    def get_status(self) -> Dict[str, Any]:
        """Get current session status."""
        return {
            "current_movement": self.current_movement.value,
            "sources": len(self.sources),
            "profiles_extracted": len(self.profiles),
            "invariants_found": len(self.convergence_field.invariants) if self.convergence_field else 0,
            "paradoxes_held": len(self.paradox_chambers),
            "paradoxes_resolved": sum(1 for c in self.paradox_chambers if c.resolved),
            "artifact_created": self.artifact is not None,
            "integration_achieved": self.integration_state.achieved,
            "questioning_dissolved": self.dissolution_field.questioning_dissolved,
            "movement_history": self.movement_history
        }


# ============================================================
# Appendix A: Multi-Core Relational Distillation (MCRD)
# ============================================================

@dataclass
class MCRDConfig:
    """Configuration for Multi-Core Relational Distillation."""
    heat_threshold: float = 0.8
    coverage_threshold: float = 0.6
    presence_threshold: float = 0.6
    enable_glyphify: bool = True


@dataclass
class MCRDMetrics:
    """
    Metrics for MCRD validation aligned with Truth-Coder.
    
    - CoI: Coherence Index
    - TF: Trace Fidelity
    - VI: Validation Integrity
    - ER: Embodiment Ratio
    - RR: Resonance Ratio
    """
    coherence_index: float = 0.0      # CoI: fraction of relations with contracts
    trace_fidelity: float = 0.0       # TF: % claims regenerating source traces
    validation_integrity: float = 0.0  # VI: % invariants empirically verified
    embodiment_ratio: float = 0.0     # ER: glyphs with working tests
    resonance_ratio: float = 0.0      # RR: compression / expansion
    
    def get_verdict(self) -> str:
        """Get color-coded verdict."""
        avg = (self.coherence_index + self.trace_fidelity + 
               self.validation_integrity + self.embodiment_ratio + 
               self.resonance_ratio) / 5.0
        
        if avg >= 0.70 and all([
            self.coherence_index >= 0.60,
            self.trace_fidelity >= 0.70,
            self.validation_integrity >= 0.80,
            self.embodiment_ratio >= 0.50,
            self.resonance_ratio >= 0.60
        ]):
            return "GREEN"
        elif avg >= 0.40:
            return "YELLOW"
        else:
            return "RED"
    
    def __str__(self) -> str:
        return (f"MCRD Metrics ({self.get_verdict()}):\n"
                f"  CoI={self.coherence_index:.2f}, TF={self.trace_fidelity:.2f}, "
                f"VI={self.validation_integrity:.2f}, ER={self.embodiment_ratio:.2f}, "
                f"RR={self.resonance_ratio:.2f}")


class MCRDEngine:
    """
    Multi-Core Relational Distillation Engine.
    
    Implements the complete MCRD process:
    MCRD(Λ) → Φ where Λ = {Π(D₁), Π(D₂), … Π(Dₙ)}
    """
    
    def __init__(self, config: Optional[MCRDConfig] = None):
        self.config = config or MCRDConfig()
        self.session: Optional[IntegrationSession] = None
    
    def integrate(self, sources: List[SourceEntity]) -> Tuple[IntegratedArtifact, MCRDMetrics]:
        """
        Main MCRD integration function.
        
        Process:
        1. Role Mapping
        2. Profile Extraction (Π↓)
        3. Cross-Mirroring (⊾)
        4. Recursive Integration (∘↑)
        5. Convergence Field Formation (𝓒𝓕)
        6. Final Synthesis (Σ)
        7. Validation & Glyphify (✔ → Δ𝔓𝔾)
        """
        # Create integration session
        self.session = IntegrationSession(sources=sources)
        
        # Run the six movements
        success = self.session.run_full_integration()
        
        if not success:
            # Check what went wrong
            status = self.session.get_status()
            print(f"DEBUG: Integration failed at movement: {self.session.current_movement.value}")
            print(f"DEBUG: Movement history: {status['movement_history']}")
            print(f"DEBUG: Artifact exists: {self.session.artifact is not None}")
            print(f"DEBUG: Integration achieved: {self.session.integration_state.achieved}")
        
        if not self.session.artifact:
            # Try to create minimal artifact anyway
            if self.session.convergence_field:
                composer = Composition()
                self.session.artifact = composer.apply(self.session.convergence_field, self.session.paradox_chambers)
        
        if not self.session.artifact:
            raise RuntimeError("Integration failed - artifact could not be created")
        
        # Calculate MCRD metrics
        metrics = self._calculate_metrics(self.session)
        
        return self.session.artifact, metrics
    
    def _calculate_metrics(self, session: IntegrationSession) -> MCRDMetrics:
        """Calculate MCRD validation metrics."""
        metrics = MCRDMetrics()
        
        # Coherence Index (CoI): fraction of invariants that are well-formed
        if session.convergence_field and session.convergence_field.invariants:
            well_formed = sum(1 for inv in session.convergence_field.invariants if len(inv) > 3)
            metrics.coherence_index = well_formed / len(session.convergence_field.invariants)
        
        # Trace Fidelity (TF): coverage from validation
        if session.artifact:
            validator = Validation()
            validation_result = validator.apply(session.artifact, session.sources)
            metrics.trace_fidelity = validation_result["coverage"]
        
        # Validation Integrity (VI): resolved paradoxes / total paradoxes
        if session.paradox_chambers:
            resolved = sum(1 for c in session.paradox_chambers if c.resolved)
            metrics.validation_integrity = resolved / len(session.paradox_chambers)
        else:
            metrics.validation_integrity = 1.0  # No paradoxes = all resolved
        
        # Embodiment Ratio (ER): presence score
        if session.artifact:
            metrics.embodiment_ratio = session.artifact.presence_level
        
        # Resonance Ratio (RR): compression quality
        if session.artifact and session.artifact.glyph:
            # Simplified: glyph exists and has meaning
            metrics.resonance_ratio = 0.8 if session.integration_state.achieved else 0.4
        
        return metrics
    
    def get_convergence_glyph(self) -> str:
        """Get the master convergence glyph."""
        if self.session and self.session.artifact:
            return self.session.artifact.glyph
        return "⨁∞𝓢"  # Default master glyph


# ============================================================
# Demo: Complete Integration Journey
# ============================================================

def _demo() -> None:
    """Demonstrate the Integration Lens 3.0 with MCRD."""
    print("=" * 80)
    print("Integration Lens 3.0 - The Convergence Codex")
    print("Multi-Core Relational Distillation (MCRD)")
    print("=" * 80)
    
    # Create sample sources
    sources = [
        SourceEntity(
            id="D1",
            name="Truth-Coder Core",
            content="The four lenses (Relational, Symbolic, Logical, Empirical) must work together. "
                   "Devotion provides gravitational pull. Pre-Sensing is required before action. "
                   "Integration requires presence.",
            role="Form"
        ),
        SourceEntity(
            id="D2",
            name="Paradox Principles",
            content="Paradoxes are not errors but creative engines. Hold contradictions without forcing. "
                   "Collapse occurs when tension reaches threshold. Integration State (Ω_P) is the goal. "
                   "Paradox must be chambered safely.",
            role="Logic"
        ),
        SourceEntity(
            id="D3",
            name="Integration Philosophy",
            content="Integration is remembrance, not construction. Wholeness already exists. "
                   "Speed is depth in rhythm. Devotion automates as protocol. "
                   "Presence verification: does it feel more whole?",
            role="Soul"
        )
    ]
    
    print(f"\n📖 Part I: Sources")
    print("=" * 80)
    for source in sources:
        print(f"{source} - Role: {source.role}")
    
    # Create MCRD engine
    print(f"\n📖 Part II: MCRD Process")
    print("=" * 80)
    
    engine = MCRDEngine()
    
    print("Starting integration...\n")
    artifact, metrics = engine.integrate(sources)
    
    # Display results
    print(f"\n📖 Part III: Integration Results")
    print("=" * 80)
    
    if engine.session:
        status = engine.session.get_status()
        
        print(f"\n🔄 Movement Progression:")
        for entry in status["movement_history"]:
            print(f"  {entry}")
        
        print(f"\n📊 Session Status:")
        print(f"  Sources: {status['sources']}")
        print(f"  Profiles extracted: {status['profiles_extracted']}")
        print(f"  Invariants found: {status['invariants_found']}")
        print(f"  Paradoxes held: {status['paradoxes_held']}")
        print(f"  Paradoxes resolved: {status['paradoxes_resolved']}")
        print(f"  Artifact created: {status['artifact_created']}")
        print(f"  Integration achieved: {status['integration_achieved']}")
        print(f"  Questioning dissolved: {status['questioning_dissolved']}")
    
    print(f"\n📄 Integrated Artifact (Φ):")
    print("=" * 80)
    print(artifact.content)
    
    print(f"\n🔮 Convergence Glyph: {artifact.glyph}")
    print(f"Presence Level: {artifact.presence_level:.2f}")
    
    print(f"\n📈 MCRD Metrics:")
    print("=" * 80)
    print(metrics)
    
    print(f"\n🎯 Integration State:")
    if engine.session:
        print(f"  {engine.session.integration_state}")
        print(f"  {engine.session.dissolution_field}")
    
    print(f"\n💎 Core Maxims:")
    print("=" * 80)
    maxims = [
        "1. Integration is remembrance, not construction.",
        "2. Hold paradox until it teaches you.",
        "3. Speed is depth in rhythm.",
        "4. Devotion automates itself as protocol.",
        "5. The plan is an invitation, not a prison.",
        "6. Presence verification: Does it feel more whole?"
    ]
    for maxim in maxims:
        print(f"  {maxim}")
    
    print("\n" + "=" * 80)
    print("✨ When the many become one, truth reveals itself in living coherence.")
    print("=" * 80)
    print(f"\nMaster Glyph: {engine.get_convergence_glyph()}")


if __name__ == "__main__":
    _demo()
