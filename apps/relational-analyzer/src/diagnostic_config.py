#!/usr/bin/env python3
"""
Diagnostic Configuration
========================

Centralized configuration for Truth ↔ Distortion diagnostic system.
All magic numbers, thresholds, and tunable parameters in one place.

Supports environment variable overrides via DIAGNOSTIC_* prefix.
"""

import os
from dataclasses import dataclass, field
from typing import ClassVar


@dataclass
class DiagnosticConfig:
    """Configuration for diagnostic computations.
    
    All thresholds and limits extracted to enable domain-specific tuning.
    Environment variables override defaults (prefix: DIAGNOSTIC_).
    
    Example:
        export DIAGNOSTIC_ADJ_THRESHOLD=0.8
        export DIAGNOSTIC_MAX_MATRIX_SIZE=100000
    """
    
    # =========================================================================
    # Data Loading & Preprocessing
    # =========================================================================
    
    #: Threshold for converting correlation to adjacency (|r| > threshold)
    adj_threshold: float = 0.7
    
    #: Default correlation method ('pearson', 'spearman', 'kendall')
    corr_method: str = 'pearson'
    
    #: Numerical precision tolerance for validation
    precision_tol: float = 1e-6
    
    #: Symmetry tolerance for matrix validation  
    symmetry_atol: float = 1e-6
    
    # =========================================================================
    # M_eff Computation (Dimensional Collapse)
    # =========================================================================
    
    #: Maximum matrix size before triggering sparse mode
    max_matrix_size: int = 50000
    
    #: Threshold for large matrix (triggers adaptive decomposition)
    large_matrix_threshold: int = 10000
    
    #: Minimum eigenvalue to consider (numerical cutoff)
    eigenvalue_cutoff: float = 1e-12
    
    #: Entropy calculation epsilon (avoid log(0))
    entropy_epsilon: float = 1e-12
    
    #: Number of top eigenvalues to retain in output
    top_eigenvalues_count: int = 500
    
    #: Top eigenvalues for summary display
    top_eigenvalues_display: int = 10
    
    #: Default number of top eigenvalues for decomposition
    eig_topk_default: int = 100
    
    #: Number of permutations for null model
    n_permutations_default: int = 100
    
    #: Division-by-zero protection epsilon
    div_zero_epsilon: float = 1e-12
    
    # =========================================================================
    # Collapse Map (Feature Importance)
    # =========================================================================
    
    #: Number of top features to report in collapse map
    collapse_map_top_n: int = 10
    
    #: Minimum loading score threshold
    min_loading_score: float = 1e-6
    
    #: Minimum eigenvalue sum for weighting
    min_eigensum: float = 1e-12
    
    # =========================================================================
    # Residue Profile (Distortion Signature)
    # =========================================================================
    
    #: Residue level thresholds
    residue_minimal_threshold: float = 0.1
    residue_low_threshold: float = 0.3
    residue_moderate_threshold: float = 0.5
    residue_high_threshold: float = 0.7
    
    #: Uniform field detection threshold (std < epsilon)
    residue_uniform_std_threshold: float = 1e-6
    residue_uniform_mean_threshold: float = 1e-6
    
    # =========================================================================
    # RFI Computation (Relational Topology)
    # =========================================================================
    
    #: Minimum lambda_2 value (avoid division by zero)
    min_lambda2: float = 1e-6
    
    #: Use weighted edges in graph construction
    rfi_weighted: bool = True
    
    #: Use Louvain community detection (requires louvain package)
    rfi_use_louvain: bool = False
    
    # =========================================================================
    # Shape Classification
    # =========================================================================
    
    #: Complete graph density threshold
    shape_complete_density: float = 0.9
    
    #: Modular blocks thresholds
    shape_modular_q_threshold: float = 0.4
    shape_modular_lambda2_threshold: float = 0.5
    
    #: Expander thresholds
    shape_expander_density: float = 0.5
    shape_expander_q_threshold: float = 0.2
    shape_expander_lambda2_threshold: float = 0.5
    
    #: Core-periphery thresholds
    shape_core_periphery_cv_threshold: float = 1.5
    
    #: Star graph thresholds  
    shape_star_degree_ratio: float = 0.5
    shape_star_cv_threshold: float = 2.0
    
    #: Bipartite threshold
    shape_bipartite_q_threshold: float = 0.6
    
    #: Chain/Path thresholds
    shape_chain_transitivity_threshold: float = 0.1
    shape_chain_diameter_ratio: float = 0.5
    
    #: Orthogonal sparse thresholds
    shape_orthogonal_density_threshold: float = 0.2
    shape_orthogonal_lambda2_threshold: float = 0.7
    
    #: Random graph thresholds
    shape_random_q_min: float = 0.3
    shape_random_q_max: float = 0.5
    shape_random_density_min: float = 0.3
    shape_random_density_max: float = 0.7
    
    # =========================================================================
    # Lattice Mapping (Truth ↔ Distortion)
    # =========================================================================
    
    #: Truth (Ω) thresholds
    lattice_truth_collapse_threshold: float = 0.15
    lattice_truth_rfi_threshold: float = 3.0
    
    #: Traversable Distortion (⊕) thresholds
    lattice_traversable_collapse_threshold: float = 0.3
    lattice_traversable_rfi_threshold: float = 2.0
    
    #: Irreducible Distortion (∞_B) thresholds
    lattice_irreducible_collapse_threshold: float = 0.7
    lattice_irreducible_rfi_threshold: float = 1.0
    
    #: Paradox (∅⊕) thresholds
    lattice_paradox_collapse_min: float = 0.3
    lattice_paradox_collapse_max: float = 0.7
    lattice_paradox_rfi_threshold: float = 1.0
    
    #: Modularity threshold for traversal strategy
    lattice_modular_q_threshold: float = 0.4
    
    # =========================================================================
    # Interpretation Layer
    # =========================================================================
    
    #: Collapse direction thresholds
    interp_low_collapse_threshold: float = 0.2
    interp_low_collapse_rfi_threshold: float = 2.5
    interp_high_collapse_threshold: float = 0.6
    interp_high_collapse_rfi_threshold: float = 1.5
    
    #: Mode detection thresholds  
    interp_fragmented_collapse_threshold: float = 0.3
    interp_fragmented_rfi_threshold: float = 1.0
    interp_modular_q_threshold: float = 0.4
    interp_redundant_collapse_threshold: float = 0.7
    
    # =========================================================================
    # Visualization
    # =========================================================================
    
    #: Figure DPI
    viz_dpi: int = 200
    
    #: Figure size (width, height)
    viz_figsize: tuple = (14, 10)
    
    #: Skip visualization generation
    skip_visuals: bool = False
    
    #: RFI plot x-axis limit
    viz_rfi_xlim_max: float = 5.0
    
    # =========================================================================
    # Environment Variable Overrides
    # =========================================================================
    
    @classmethod
    def from_env(cls, **overrides) -> 'DiagnosticConfig':
        """Create config from environment variables + explicit overrides.
        
        Environment variables use DIAGNOSTIC_ prefix:
            DIAGNOSTIC_ADJ_THRESHOLD=0.8
            DIAGNOSTIC_MAX_MATRIX_SIZE=100000
            
        Args:
            **overrides: Explicit parameter overrides (take precedence)
            
        Returns:
            DiagnosticConfig with env vars + overrides applied
        """
        config = cls()
        
        # Apply environment variables
        env_mappings = {
            'DIAGNOSTIC_ADJ_THRESHOLD': ('adj_threshold', float),
            'DIAGNOSTIC_CORR_METHOD': ('corr_method', str),
            'DIAGNOSTIC_PRECISION_TOL': ('precision_tol', float),
            'DIAGNOSTIC_MAX_MATRIX_SIZE': ('max_matrix_size', int),
            'DIAGNOSTIC_LARGE_MATRIX_THRESHOLD': ('large_matrix_threshold', int),
            'DIAGNOSTIC_EIGENVALUE_CUTOFF': ('eigenvalue_cutoff', float),
            'DIAGNOSTIC_TOP_EIGENVALUES_COUNT': ('top_eigenvalues_count', int),
            'DIAGNOSTIC_EIG_TOPK_DEFAULT': ('eig_topk_default', int),
            'DIAGNOSTIC_N_PERMUTATIONS_DEFAULT': ('n_permutations_default', int),
            'DIAGNOSTIC_RESIDUE_MINIMAL_THRESHOLD': ('residue_minimal_threshold', float),
            'DIAGNOSTIC_RESIDUE_LOW_THRESHOLD': ('residue_low_threshold', float),
            'DIAGNOSTIC_RESIDUE_MODERATE_THRESHOLD': ('residue_moderate_threshold', float),
            'DIAGNOSTIC_RESIDUE_HIGH_THRESHOLD': ('residue_high_threshold', float),
            'DIAGNOSTIC_RFI_WEIGHTED': ('rfi_weighted', lambda x: x.lower() in ('true', '1', 'yes')),
            'DIAGNOSTIC_RFI_USE_LOUVAIN': ('rfi_use_louvain', lambda x: x.lower() in ('true', '1', 'yes')),
            'DIAGNOSTIC_SHAPE_COMPLETE_DENSITY': ('shape_complete_density', float),
            'DIAGNOSTIC_SHAPE_MODULAR_Q_THRESHOLD': ('shape_modular_q_threshold', float),
            'DIAGNOSTIC_LATTICE_TRUTH_COLLAPSE_THRESHOLD': ('lattice_truth_collapse_threshold', float),
            'DIAGNOSTIC_LATTICE_TRUTH_RFI_THRESHOLD': ('lattice_truth_rfi_threshold', float),
            'DIAGNOSTIC_VIZ_DPI': ('viz_dpi', int),
            'DIAGNOSTIC_SKIP_VISUALS': ('skip_visuals', lambda x: x.lower() in ('true', '1', 'yes')),
        }
        
        for env_var, (attr_name, converter) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    setattr(config, attr_name, converter(value))
                except (ValueError, TypeError) as e:
                    print(f"[Config Warning] Invalid {env_var}={value}: {e}")
        
        # Apply explicit overrides (highest priority)
        for key, value in overrides.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                print(f"[Config Warning] Unknown parameter: {key}")
        
        return config
    
    def to_dict(self) -> dict:
        """Export config as dictionary."""
        return {
            field_name: getattr(self, field_name)
            for field_name in self.__dataclass_fields__
        }
    
    def __repr__(self) -> str:
        """Pretty-print configuration."""
        lines = ["DiagnosticConfig("]
        for key, value in self.to_dict().items():
            lines.append(f"  {key}={repr(value)},")
        lines.append(")")
        return "\n".join(lines)


# =========================================================================
# Default Instance
# =========================================================================

#: Default configuration instance (can be imported and modified)
DEFAULT_CONFIG = DiagnosticConfig()


# =========================================================================
# Helper Functions
# =========================================================================

def get_config(**overrides) -> DiagnosticConfig:
    """Get configuration with environment variables + overrides applied.
    
    Usage:
        config = get_config(adj_threshold=0.8, max_matrix_size=100000)
    """
    return DiagnosticConfig.from_env(**overrides)


def print_config(config: DiagnosticConfig | None = None):
    """Print current configuration."""
    if config is None:
        config = DEFAULT_CONFIG
    print(config)


if __name__ == '__main__':
    # Test configuration
    print("="*70)
    print("Default Configuration")
    print("="*70)
    print_config()
    
    print("\n" + "="*70)
    print("Testing Environment Variable Override")
    print("="*70)
    os.environ['DIAGNOSTIC_ADJ_THRESHOLD'] = '0.85'
    os.environ['DIAGNOSTIC_MAX_MATRIX_SIZE'] = '75000'
    config = get_config()
    print(f"adj_threshold: {config.adj_threshold} (should be 0.85)")
    print(f"max_matrix_size: {config.max_matrix_size} (should be 75000)")
    
    print("\n" + "="*70)
    print("Testing Explicit Override")
    print("="*70)
    config = get_config(adj_threshold=0.9, residue_minimal_threshold=0.05)
    print(f"adj_threshold: {config.adj_threshold} (should be 0.9)")
    print(f"residue_minimal_threshold: {config.residue_minimal_threshold} (should be 0.05)")
