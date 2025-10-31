"""
M_eff Operator - Distortion → Truth Traversal Measurement
========================================================

This module implements M_eff as the operational measure of dimensional 
collapse when traversing from the Distortion Lattice (∞_B) to the Truth 
Lattice (Ω).

Core Principle:
    Complexity = Rank of Dependence Field
    M_eff = Spectral measure of effective dimensionality
    
Integration with Mirror-OS:
    - Distortion Lattice: Redundant couplings inflate nominal dimension
    - Truth Lattice: Independent modes = actual information
    - M_eff: Traversal cost from distortion → truth

Mathematical Foundation:
    Given correlation matrix R of features:
    1. Eigendecomposition: R = VΛV^T
    2. M_eff = Σ min(λᵢ, 1)  (Li-Ji formula)egrrf
    3. Or: M_eff = (Σλᵢ)² / Σλᵢ²  (Alternative)
    
    Interpretation:
    - High M_eff ≈ m: Features independent (no distortion)
    - Low M_eff << m: Features coupled (high distortion)
    - Reduction ratio: 1 - M_eff/m = distortion fraction
"""

import numpy as np
from typing import Tuple, Optional, Dict
from dataclasses import dataclass

@dataclass
class MeffResult:
    """Results of M_eff analysis"""
    nominal_dimensions: int
    meff_liji: float
    meff_min_lambda: float
    reduction_ratio: float
    eigenvalues: np.ndarray
    alpha_effective: float
    
    def __repr__(self):
        return f"""M_eff Analysis:
  Nominal: {self.nominal_dimensions}
  M_eff (Li-Ji): {self.meff_liji:.2f}
  M_eff (min(λ,1)): {self.meff_min_lambda:.2f}
  Reduction: {self.reduction_ratio:.1%}
  α_eff = {self.alpha_effective:.6f}"""


class MeffOperator:
    """
    Operational implementation of M_eff for measuring distortion.
    
    This translates the conceptual Distortion → Truth collapse into
    a concrete numerical measurement.
    """
    
    def __init__(self, alpha: float = 0.05):
        """
        Initialize M_eff operator.
        
        Args:
            alpha: Significance threshold for effective correction
        """
        self.alpha = alpha
    
    def compute_correlation_field(self, X: np.ndarray) -> np.ndarray:
        """
        Compute the correlation field (dependency structure).
        
        Args:
            X: Data matrix (features × samples)
            
        Returns:
            Correlation matrix R
        """
        # Standardize features
        X_std = (X - X.mean(axis=1, keepdims=True)) / (X.std(axis=1, keepdims=True) + 1e-10)
        
        # Correlation matrix
        R = np.corrcoef(X_std)
        
        # Handle NaN/Inf
        R = np.nan_to_num(R, nan=0.0, posinf=1.0, neginf=-1.0)
        
        return R
    
    def spectral_decomposition(self, R: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Eigendecomposition of correlation field.
        
        Args:
            R: Correlation matrix
            
        Returns:
            eigenvalues, eigenvectors
        """
        eigenvalues, eigenvectors = np.linalg.eigh(R)
        
        # Sort descending
        idx = eigenvalues.argsort()[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]
        
        # Clip negative eigenvalues (numerical artifacts)
        eigenvalues = np.maximum(eigenvalues, 0)
        
        return eigenvalues, eigenvectors
    
    def compute_meff(self, eigenvalues: np.ndarray) -> Tuple[float, float]:
        """
        Compute M_eff using multiple formulas.
        
        Args:
            eigenvalues: Eigenvalues of correlation matrix
            
        Returns:
            (M_eff_LiJi, M_eff_min_lambda)
        """
        # Li-Ji formula: (Σλ)² / Σλ²
        sum_lambda = eigenvalues.sum()
        sum_lambda_sq = (eigenvalues ** 2).sum()
        meff_liji = (sum_lambda ** 2) / (sum_lambda_sq + 1e-10)
        
        # Min-lambda formula: Σ min(λ, 1)
        meff_min = np.minimum(eigenvalues, 1.0).sum()
        
        return meff_liji, meff_min
    
    def measure_distortion(self, X: np.ndarray) -> MeffResult:
        """
        Primary method: Measure distortion in data.
        
        This is the operational implementation of:
        "How much redundancy exists in this field?"
        
        Args:
            X: Data matrix (features × samples)
            
        Returns:
            MeffResult with complete analysis
        """
        m = X.shape[0]  # Nominal dimensions
        
        # Step 1: Extract correlation field
        R = self.compute_correlation_field(X)
        
        # Step 2: Spectral decomposition
        eigenvalues, eigenvectors = self.spectral_decomposition(R)
        
        # Step 3: Compute M_eff
        meff_liji, meff_min = self.compute_meff(eigenvalues)
        
        # Step 4: Distortion metrics
        reduction_ratio = 1.0 - (meff_liji / m)
        alpha_eff = self.alpha / meff_liji
        
        return MeffResult(
            nominal_dimensions=m,
            meff_liji=meff_liji,
            meff_min_lambda=meff_min,
            reduction_ratio=reduction_ratio,
            eigenvalues=eigenvalues,
            alpha_effective=alpha_eff
        )
    
    def classify_complexity(self, result: MeffResult) -> str:
        """
        Classify problem complexity based on M_eff.
        
        Returns:
            Complexity class string
        """
        ratio = result.meff_liji / result.nominal_dimensions
        
        if ratio < 0.01:
            return "P-like (extreme collapse, <1% effective dims)"
        elif ratio < 0.1:
            return "Structured (moderate collapse, <10% effective dims)"
        elif ratio < 0.5:
            return "Medium (50% reduction)"
        else:
            return "NP-like (high rank, >50% effective dims)"


def demonstrate_meff():
    """Demonstration of M_eff on synthetic data."""
    print("=" * 60)
    print("M_eff Operator Demonstration")
    print("=" * 60)
    
    # Create synthetic data with known structure
    np.random.seed(42)
    
    # 10 true independent components
    n_components = 10
    n_samples = 100
    true_signals = np.random.randn(n_components, n_samples)
    
    # 1000 observed features (correlated projections)
    n_features = 1000
    weights = np.random.randn(n_features, n_components)
    noise = np.random.randn(n_features, n_samples) * 0.1
    X = weights @ true_signals + noise
    
    # Measure distortion
    op = MeffOperator(alpha=0.05)
    result = op.measure_distortion(X)
    
    print(result)
    print(f"\nComplexity class: {op.classify_complexity(result)}")
    print(f"\nTrue components: {n_components}")
    print(f"Measured M_eff: {result.meff_liji:.2f}")
    print(f"Accuracy: {abs(result.meff_liji - n_components) / n_components * 100:.1f}% error")
    
    # Show eigenvalue spectrum
    print(f"\nTop 20 eigenvalues:")
    for i, lam in enumerate(result.eigenvalues[:20]):
        print(f"  λ{i+1}: {lam:.2f}")


if __name__ == "__main__":
    demonstrate_meff()
