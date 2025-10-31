#!/usr/bin/env python3
"""
Truth ↔ Distortion Unified Diagnostic v2.2 (Intelligence Layer)
================================================================

Building on v2.1 optimizations, adds interpretation intelligence:
  - Collapse Map: Eigenvector contribution analysis
  - Residue Profile: Off-diagonal distortion signature  
  - Interpretation Layer: Coherence direction + narrative state

v2.2 New Features:
  - compute_collapse_map(): Feature importance for dimensional reduction
  - compute_residue_profile(): Correlation distortion measurement
  - generate_interpretation(): Narrative synthesis layer

v2.1 Base (maintained):
  - Numerical stability: eigen rescaling + precision clamp
  - Graph safety: component-aware modularity + timeout controls
  - Memory efficiency: Agg backend + explicit GC + float32 mode
  - Performance: adaptive sparse decomposition for large matrices

Usage:
    python truth_distortion_unified.py --data <file> --type auto --out results/
"""

import os
import sys
import json
import warnings
import time
import gc
import numpy as np
import pandas as pd
from pathlib import Path
import argparse
from scipy import stats
from scipy.sparse import csgraph
from scipy.spatial.distance import pdist, squareform
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

# Set matplotlib backend to non-interactive for memory safety
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# PART 0: Extra imports and utilities restored
import networkx as nx
warnings.filterwarnings('ignore')

__version__ = "2.2.5"

###############################################################################
# PART 0: Utility helpers (JSON sanitization)
###############################################################################

def sanitize_for_json(obj):
    """Recursively convert numpy types/arrays into JSON-serializable Python types."""
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

def _sanitize_array(x: np.ndarray, *, diag: float | None = None, clip: tuple[float, float] | None = None, zero_diag: bool = False) -> np.ndarray:
    """Generic array sanitization: replace non-finite, set diagonal, optional clip.
    Args:
        x: input array
        diag: if provided, sets diagonal to this value
        clip: (min, max) to clip values
        zero_diag: if True, sets diagonal to 0.0 (overrides diag)
    Returns:
        sanitized array (copy)
    """
    y = np.array(x, dtype=float, copy=True)
    y[~np.isfinite(y)] = 0.0
    if zero_diag:
        np.fill_diagonal(y, 0.0)
    elif diag is not None:
        np.fill_diagonal(y, diag)
    if clip is not None:
        y = np.clip(y, clip[0], clip[1])
    return y

###############################################################################
# PART 0A: Matrix Utilities (Transformer, Sanitizer, Validator)
###############################################################################

class MatrixSanitizer:
    """Unified sanitizer for matrices with type-aware options."""

    @staticmethod
    def sanitize(M: np.ndarray, *, matrix_type: str = 'generic', clip: tuple[float, float] | None = None,
                 diag: float | None = None, zero_diag: bool = False) -> np.ndarray:
        y = np.array(M, dtype=float, copy=True)
        y[~np.isfinite(y)] = 0.0
        if zero_diag:
            np.fill_diagonal(y, 0.0)
        elif diag is not None:
            np.fill_diagonal(y, diag)
        if clip is not None:
            y = np.clip(y, clip[0], clip[1])
        # type-specific clamps
        if matrix_type == 'correlation':
            y = np.clip(y, -1.0, 1.0)
        return y

    @classmethod
    def corr(cls, R: np.ndarray) -> np.ndarray:
        return cls.sanitize(R, matrix_type='correlation', diag=1.0, clip=(-1.0, 1.0))

    @classmethod
    def adj(cls, A: np.ndarray) -> np.ndarray:
        return cls.sanitize(A, matrix_type='adjacency', zero_diag=True)

class MatrixTransformer:
    """Stateless matrix transforms (pure functions)."""

    @staticmethod
    def symmetrize(M: np.ndarray, name: str = "Matrix", atol: float = 1e-6) -> np.ndarray:
        try:
            if not np.allclose(M, M.T, atol=atol):
                print(f"  [Warning] {name} not symmetric; symmetrizing...")
                return (M + M.T) / 2
            return M
        except Exception:
            return M

    @staticmethod
    def corr_to_adj(R: np.ndarray, threshold: float) -> np.ndarray:
        A = np.greater(np.abs(R), threshold).astype(np.int8)
        return MatrixSanitizer.adj(A)

    @staticmethod
    def adj_to_corr(A: np.ndarray) -> np.ndarray:
        R = cosine_similarity(A)
        return MatrixSanitizer.corr(R)

    @staticmethod
    def numeric_matrix(df: pd.DataFrame) -> np.ndarray:
        X = df.select_dtypes(include=[np.number]).values
        if X.size == 0:
            raise ValueError("Data contains no numeric columns.")
        return X

class MatrixValidator:
    """Validation and gentle correction for loaded matrices."""

    @staticmethod
    def validate(R: np.ndarray, A: np.ndarray, metadata: dict, tol: float = 1e-6):
        notes = []

        # Shapes
        if R.shape != A.shape:
            notes.append(f"shape_mismatch: corr{R.shape} vs adj{A.shape}")
            n = min(R.shape[0], A.shape[0])
            R = R[:n, :n]
            A = A[:n, :n]

        # Symmetry
        sym_corr = float(np.max(np.abs(R - R.T))) if R.size else 0.0
        sym_adj = float(np.max(np.abs(A - A.T))) if A.size else 0.0
        if sym_corr > tol:
            R = (R + R.T) / 2
            notes.append("corr_symmetrized")
        if sym_adj > tol:
            A = (A + A.T) / 2
            notes.append("adj_symmetrized")

        # Diagonals
        if R.size:
            np.fill_diagonal(R, 1.0)
        if A.size:
            np.fill_diagonal(A, 0.0)

        # Sanitize
        R = MatrixSanitizer.corr(R)
        A = MatrixSanitizer.adj(A)

        # Stats
        adj_density = float(np.mean(A > 0)) if A.size else 0.0
        corr_offdiag = float(np.mean(np.abs(R[~np.eye(R.shape[0], dtype=bool)]))) if R.shape[0] > 1 else 0.0

        metadata = dict(metadata) if isinstance(metadata, dict) else {}
        metadata['validation'] = {
            'corr_symmetry_delta_max': sym_corr,
            'adj_symmetry_delta_max': sym_adj,
            'adj_density': adj_density,
            'corr_offdiag_mean_abs': corr_offdiag,
            'notes': notes
        }

        if notes:
            print(f"  [Validate] Applied corrections: {', '.join(notes)}")
        print(f"  [Validate] Adjacency density: {adj_density:.3f}; |R|_offdiag mean: {corr_offdiag:.3f}")

        return R, A, metadata

###############################################################################
# PART 0B: Composable Loading Pipeline (Threshold Crossing Protocol)
###############################################################################

class BaseParser:
    """Abstract base class for data parsers."""
    def parse(self, data_path: str) -> pd.DataFrame:
        raise NotImplementedError

class TabularParser(BaseParser):
    """Parses generic CSV files into a DataFrame."""
    def parse(self, data_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(data_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Input file not found: {data_path}")
        except pd.errors.EmptyDataError:
            raise ValueError("Input CSV is empty.")
        except Exception as e:
            raise ValueError(f"Failed to read CSV: {e}")

class BaseTransformer:
    """Abstract base class for data transformers."""
    def transform(self, df: pd.DataFrame, metadata: dict) -> tuple[np.ndarray, np.ndarray, dict]:
        raise NotImplementedError

class CorrelationTransformer(BaseTransformer):
    """Transforms a DataFrame assumed to be a correlation matrix."""
    def __init__(self, adj_threshold: float = 0.7):
        self.adj_threshold = adj_threshold

    def transform(self, df: pd.DataFrame, metadata: dict) -> tuple[np.ndarray, np.ndarray, dict]:
        metadata['input_type'] = 'corr'
        R = MatrixTransformer.symmetrize(df.values, "CorrelationMatrix")
        R = MatrixSanitizer.corr(R)
        A = MatrixTransformer.corr_to_adj(R, self.adj_threshold)
        return R, A, metadata

class AdjacencyTransformer(BaseTransformer):
    """Transforms a DataFrame assumed to be an adjacency matrix."""
    def transform(self, df: pd.DataFrame, metadata: dict) -> tuple[np.ndarray, np.ndarray, dict]:
        metadata['input_type'] = 'adj'
        A = MatrixTransformer.symmetrize(df.values, "AdjacencyMatrix")
        A = MatrixSanitizer.adj(A)
        R = MatrixTransformer.adj_to_corr(A)
        return R, A, metadata

class TabularTransformer(BaseTransformer):
    """Transforms a raw tabular DataFrame into correlation and adjacency matrices."""
    def __init__(self, corr_method: str = 'pearson', adj_threshold: float = 0.7):
        self.corr_method = corr_method
        self.adj_threshold = adj_threshold

    def transform(self, df: pd.DataFrame, metadata: dict) -> tuple[np.ndarray, np.ndarray, dict]:
        metadata['input_type'] = 'tabular'
        X = MatrixTransformer.numeric_matrix(df)
        if X.shape[1] < 2:
            raise ValueError("Tabular data must have at least 2 numeric columns.")

        X_scaled = StandardScaler().fit_transform(X)
        
        if self.corr_method == 'pearson':
            R = np.corrcoef(X_scaled.T)
        elif self.corr_method == 'spearman':
            from scipy.stats import spearmanr
            R = spearmanr(X_scaled)[0]
        elif self.corr_method == 'kendall':
            from scipy.stats import kendalltau
            n_features = X_scaled.shape[1]
            R = np.eye(n_features)
            for i in range(n_features):
                for j in range(i + 1, n_features):
                    tau, _ = kendalltau(X_scaled[:, i], X_scaled[:, j])
                    R[i, j] = R[j, i] = tau
        else:
            raise ValueError(f"Unknown corr_method: {self.corr_method}")

        R = MatrixSanitizer.corr(R)
        A = MatrixTransformer.corr_to_adj(R, self.adj_threshold)
        metadata['n_samples'] = X.shape[0]
        metadata['n_features'] = X.shape[1]
        metadata['corr_method'] = self.corr_method
        return R, A, metadata

class EdgeListTransformer(BaseTransformer):
    """Transforms an edgelist DataFrame into adjacency and correlation matrices."""
    def transform(self, df: pd.DataFrame, metadata: dict) -> tuple[np.ndarray, np.ndarray, dict]:
        metadata['input_type'] = 'edgelist'
        if df.shape[1] == 2:
            G = nx.from_pandas_edgelist(df, source=df.columns[0], target=df.columns[1])
        elif df.shape[1] == 3:
            G = nx.from_pandas_edgelist(df, source=df.columns[0], target=df.columns[1], edge_attr='weight')
        else:
            raise ValueError("Edge list must have 2 or 3 columns.")

        A = nx.to_numpy_array(G, nodelist=sorted(G.nodes()))
        A = MatrixSanitizer.adj(A)
        R = MatrixTransformer.adj_to_corr(A)
        metadata['n_nodes'] = G.number_of_nodes()
        metadata['n_edges'] = G.number_of_edges()
        return R, A, metadata

class LoadPipeline:
    """Orchestrates a parsing and transformation pipeline."""
    def __init__(self, parser: BaseParser, transformer: BaseTransformer):
        self.parser = parser
        self.transformer = transformer

    def run(self, data_path: str) -> tuple[np.ndarray, np.ndarray, dict]:
        print(f"  [Pipeline] Parser: {self.parser.__class__.__name__}, Transformer: {self.transformer.__class__.__name__}")
        df = self.parser.parse(data_path)
        metadata = {'input_path': data_path, 'input_shape': df.shape}
        R, A, metadata = self.transformer.transform(df, metadata)
        metadata['corr_shape'] = R.shape
        metadata['adj_shape'] = A.shape
        return R, A, metadata

class LoadPipelineFactory:
    """Factory to create the correct loading pipeline based on data type."""

    @staticmethod
    def create(data_type: str, corr_method: str, adj_threshold: float) -> LoadPipeline:
        parser = TabularParser() # All current types start from a CSV
        
        if data_type == 'corr':
            transformer = CorrelationTransformer(adj_threshold)
        elif data_type == 'adj':
            transformer = AdjacencyTransformer()
        elif data_type == 'tabular':
            transformer = TabularTransformer(corr_method, adj_threshold)
        elif data_type == 'edgelist':
            transformer = EdgeListTransformer()
        # Add other transformers for 'dist', 'timeseries' if needed
        else:
            raise ValueError(f"Unsupported data_type for pipeline factory: {data_type}")
            
        return LoadPipeline(parser, transformer)

    @staticmethod
    def auto_detect_and_create(data_path: str, corr_method: str, adj_threshold: float) -> LoadPipeline:
        """Auto-detects data type and returns the appropriate pipeline."""
        try:
            df = pd.read_csv(data_path, nrows=100) # Read a sample for detection
        except Exception as e:
            raise ValueError(f"Failed to read sample from {data_path} for auto-detection: {e}")

        data_type = 'tabular' # Default
        if df.shape[0] == df.shape[1]:
            matrix = df.values
            if np.allclose(matrix, matrix.T, atol=1e-6):
                if np.all(np.abs(matrix) <= 1.01) and np.allclose(np.diag(matrix), 1.0):
                    data_type = 'corr'
                elif np.all(np.isin(matrix, [0, 1])):
                    data_type = 'adj'
        elif df.shape[1] in [2, 3] and df.shape[0] > df.shape[1]:
            data_type = 'edgelist'
        
        print(f"[Auto-detect] Detected type: {data_type}")
        return LoadPipelineFactory.create(data_type, corr_method, adj_threshold)

def load_data_with_pipeline(data_path: str, data_type: str, corr_method: str, adj_threshold: float):
    """Entry point for the new composable loading system."""
    if data_type == 'auto':
        pipeline = LoadPipelineFactory.auto_detect_and_create(data_path, corr_method, adj_threshold)
    else:
        pipeline = LoadPipelineFactory.create(data_type, corr_method, adj_threshold)
    
    return pipeline.run(data_path)

###############################################################################
# PART 0B: Validation Bridge (sanity checks after load)
###############################################################################

def validate_loaded_data(R: np.ndarray, A: np.ndarray, metadata: dict, tol: float = 1e-6):
    """Validate and gently correct loaded matrices; annotate metadata."""
    return MatrixValidator.validate(R, A, metadata, tol)

###############################################################################
# PART 1: M_eff Computation (Dimensional Collapse)
###############################################################################

def compute_meff(corr_matrix, n_permutations=None, eig_topk=100):
    """Compute M_eff with v2.1 optimizations."""
    m = corr_matrix.shape[0]

    # Hard limit to prevent memory blow-ups
    if m > 50000:
        raise ValueError("Matrix too large for eigenvalue decomposition (m > 50000)")

    max_abs = np.max(np.abs(corr_matrix)) if m > 0 else 0.0
    corr_matrix_scaled = corr_matrix / max_abs if max_abs > 0 else corr_matrix
    
    if m > 10000:
        print(f"  [M_eff] Large matrix detected ({m}x{m}), using sparse solver...")
        from scipy.sparse.linalg import eigsh
        try:
            k = min(eig_topk, m - 2)
            eigenvals, eigenvecs = eigsh(corr_matrix_scaled, k=k, which='LA', return_eigenvectors=True)
            eigenvals = np.sort(eigenvals)[::-1]
            eigenvecs = eigenvecs[:, np.argsort(eigenvals)[::-1]]
        except:
            print("  [M_eff] Sparse solver failed, falling back to dense...")
            eigenvals, eigenvecs = np.linalg.eigh(corr_matrix_scaled)
            eigenvals = eigenvals[::-1]
            eigenvecs = eigenvecs[:, ::-1]
    else:
        eigenvals, eigenvecs = np.linalg.eigh(corr_matrix_scaled)
        eigenvals = eigenvals[::-1]
        eigenvecs = eigenvecs[:, ::-1]
    
    eigenvals = np.clip(eigenvals, 0, None)
    eigenvals = eigenvals[eigenvals > 1e-12]
    m_effective = len(eigenvals)
    
    meff_liji = (eigenvals.sum()**2) / (eigenvals**2).sum() if len(eigenvals) > 0 else 0.0
    meff_min = np.minimum(eigenvals, 1).sum()
    meff_pr = (eigenvals.sum()**2) / (eigenvals**2).sum() if len(eigenvals) > 0 else 0.0
    
    if len(eigenvals) > 0:
        p = eigenvals / eigenvals.sum()
        entropy = -np.sum(p * np.log(p + 1e-12))
        meff_entropy = np.exp(entropy)
    else:
        meff_entropy = 0.0
    
    # Avoid division by zero; if m==0 then ratio is 0 (no dimensions)
    collapse_ratio = meff_min / max(m, 1)
    
    results = {
        'meff_liji': float(meff_liji),
        'meff_min': float(meff_min),
        'meff_pr': float(meff_pr),
        'meff_entropy': float(meff_entropy),
        'm_total': int(m),
        'm_effective': int(m_effective),
        'collapse_ratio': float(collapse_ratio),
        'eigenvalues': eigenvals.tolist()[:500],
    'eigenvectors': [[float(x) for x in row] for row in eigenvecs.tolist()] if m <= 1000 else [],  # Store for collapse map
        'eigenvectors_available': bool(m <= 1000),
        'top_10_eigenvalues': eigenvals[:10].tolist() if len(eigenvals) >= 10 else eigenvals.tolist(),
        'explained_variance_ratio': (eigenvals / eigenvals.sum()).tolist()[:500] if len(eigenvals) > 0 else []
    }
    
    if n_permutations and n_permutations > 0:
        if m > 5000:
            print("  [M_eff] Skipping null model for large matrix (m > 5000)")
            results['null_permutations_skipped'] = True
        else:
            null_meffs = []
            for _ in range(n_permutations):
                perm_idx = np.random.permutation(m)
                perm_corr = corr_matrix[perm_idx, :][:, perm_idx]
                perm_corr_scaled = perm_corr / np.max(np.abs(perm_corr))
                perm_eigs = np.linalg.eigvalsh(perm_corr_scaled)
                perm_eigs = np.clip(perm_eigs, 0, None)
                perm_eigs = perm_eigs[perm_eigs > 1e-12]
                null_meff = np.minimum(perm_eigs, 1).sum()
                null_meffs.append(null_meff)
            
            results['null_meff_mean'] = float(np.mean(null_meffs))
            results['null_meff_std'] = float(np.std(null_meffs))
            results['meff_zscore'] = float((meff_min - np.mean(null_meffs)) / (np.std(null_meffs) + 1e-12))
    
    return results

###############################################################################
# PART 1B: Collapse Map (v2.2 NEW)
###############################################################################

def compute_collapse_map(corr_matrix, meff_metrics, out_dir, n_top=10):
    """
    Compute feature importance for dimensional collapse.
    
    Returns top features/nodes contributing most to M_eff reduction.
    """
    print("\n[Collapse Map] Computing feature importance...")
    
    eigenvalues = np.array(meff_metrics['eigenvalues'])
    
    # Get eigenvectors if available
    if meff_metrics.get('eigenvectors_available', False) and len(meff_metrics.get('eigenvectors', [])) > 0:
        eigenvectors = np.array(meff_metrics['eigenvectors'])
    else:
        # Recompute for small matrices
        if corr_matrix.shape[0] <= 1000:
            eigenvals, eigenvectors = np.linalg.eigh(corr_matrix)
            eigenvals = eigenvals[::-1]
            eigenvectors = eigenvectors[:, ::-1]
        else:
            print("  [Warning] Matrix too large for collapse map, skipping...")
            return {'status': 'skipped', 'reason': 'matrix_too_large'}
    
    # Compute loadings (absolute contribution to top eigenvalues)
    n_components = min(10, eigenvectors.shape[1], len(eigenvalues))
    if n_components == 0:
        return {'status': 'degenerate', 'reason': 'no_components'}
    # Handle uniform eigenspectrum (no informative weighting)
    if eigenvalues[:n_components].sum() < 1e-12:
        return {'status': 'degenerate', 'reason': 'uniform_eigenspectrum'}
    loadings = np.abs(eigenvectors[:, :n_components])
    
    # Weight by eigenvalue magnitude
    denom = eigenvalues[:n_components].sum()
    weights = (eigenvalues[:n_components] / denom) if denom > 0 else np.ones(n_components) / max(n_components, 1)
    weighted_loadings = loadings @ weights

    # Degenerate zero-variance case
    if np.max(weighted_loadings) < 1e-6:
        print("  [Warning] Collapse map is degenerate (zero variance).")
        return {'status': 'degenerate', 'reason': 'zero_variance'}
    
    # Get top contributors
    top_indices = np.argsort(weighted_loadings)[::-1][:n_top]
    top_scores = weighted_loadings[top_indices]
    
    # Create collapse map
    collapse_map = pd.DataFrame({
        'feature_index': top_indices,
        'collapse_score': top_scores,
        'contribution_pct': 100 * top_scores / top_scores.sum()
    })
    
    # Save to CSV
    try:
        collapse_map.to_csv(f'{out_dir}/collapse_map.csv', index=False)
    except Exception as e:
        print(f"  [Warning] Could not save collapse_map.csv: {e}")
        return {'status': 'io_error', 'reason': str(e)}
    
    print(f"  Top collapse driver: Feature {top_indices[0]} (score={top_scores[0]:.3f})")
    
    return {
        'top_features': top_indices.tolist(),
        'scores': top_scores.tolist(),
        'status': 'computed'
    }

###############################################################################
# PART 1C: Residue Profile (v2.2 NEW)
###############################################################################

def compute_residue_profile(corr_matrix):
    """
    Compute off-diagonal correlation residue (distortion signature).
    
    Measures systemic correlation strength = B∞ residue accumulation.
    """
    print("\n[Residue Profile] Computing distortion signature...")
    
    # Degenerate case
    if corr_matrix.shape[0] < 2:
        return {
            'residue_mean': 0.0,
            'residue_max': 0.0,
            'residue_std': 0.0,
            'residue_median': 0.0,
            'residue_level': 'Degenerate'
        }

    try:
        # Get off-diagonal elements
        mask = ~np.eye(corr_matrix.shape[0], dtype=bool)
        off_diag = np.abs(corr_matrix[mask])
        if off_diag.size == 0:
            return {
                'residue_mean': 0.0,
                'residue_max': 0.0,
                'residue_std': 0.0,
                'residue_median': 0.0,
                'residue_level': 'Degenerate'
            }
        
        # Compute residue statistics
        residue_mean = float(np.mean(off_diag))
        residue_max = float(np.max(off_diag))
        residue_std = float(np.std(off_diag))
        residue_median = float(np.median(off_diag))
    except Exception as e:
        print(f"  [Residue Warning] Failed to compute residue profile: {e}")
        return {
            'residue_mean': 0.0,
            'residue_max': 0.0,
            'residue_std': 0.0,
            'residue_median': 0.0,
            'residue_level': 'Error',
            'error': str(e)
        }
    
    # Classify residue level
    if residue_mean < 0.1:
        level = "Minimal"
    elif residue_mean < 0.3:
        level = "Low"
    elif residue_mean < 0.5:
        level = "Moderate"
    elif residue_mean < 0.7:
        level = "High"
    else:
        level = "Extreme"

    # Uniform field flag
    if residue_std < 1e-6 and residue_mean > 1e-6:
        level += " (Uniform)"

    # Binary input hint
    note = None
    if np.all(np.isin(corr_matrix, [0, 1])):
        note = "Binary input—residue = edge density"
        print(f"  Note: {note}")
    
    print(f"  Residue level: {level} (mean={residue_mean:.3f})")
    
    return {
        'residue_mean': residue_mean,
        'residue_max': residue_max,
        'residue_std': residue_std,
        'residue_median': residue_median,
        'residue_level': level,
        'note': note
    }

###############################################################################
# PART 2: RFI Computation (Relational Field Index)
###############################################################################

class RFITopology:
    """Encapsulate RFI graph construction and metrics."""

    def __init__(self, adj_matrix: np.ndarray, *, weighted: bool = True, use_louvain: bool = False):
        self.adj_matrix = np.array(adj_matrix)
        self.weighted = bool(weighted)
        self.use_louvain = bool(use_louvain)
        self.G = None
        self.G_main = None
        self.n_components = 0
        self._build_graph()

    def _build_graph(self):
        if self.weighted and np.any((self.adj_matrix > 0) & (self.adj_matrix != 1)):
            G = nx.from_numpy_array(self.adj_matrix)
        else:
            G = nx.from_numpy_array(self.adj_matrix, create_using=nx.Graph)
        G.remove_edges_from(nx.selfloop_edges(G))
        components = list(nx.connected_components(G))
        self.n_components = len(components)
        if self.n_components > 1:
            largest_cc = max(components, key=len)
            self.G_main = G.subgraph(largest_cc).copy()
            print(f"  [RFI] Using largest connected component: {len(self.G_main)} / {self.adj_matrix.shape[0]} nodes")
        else:
            self.G_main = G
        self.G = G

    def _compute_modularity(self):
        if self.G_main is None:
            self._build_graph()
        Q = 0.0
        n_communities = 0
        community_mapping = {}
        n_nodes = len(self.G_main) if self.G_main is not None else 0
        if self.G_main is None or n_nodes == 0:
            return 0.0, 0, {}
        try:
            if self.use_louvain:
                try:
                    import importlib
                    community_louvain = importlib.import_module('community')
                    partition = community_louvain.best_partition(self.G_main)
                    communities = [set([k for k, v in partition.items() if v == com]) for com in set(partition.values())]
                    Q = nx.community.modularity(self.G_main, communities)
                    n_communities = len(communities)
                    community_mapping = {str(node): int(comm_id) for node, comm_id in partition.items()}
                    print("  [RFI] Using Louvain algorithm")
                except Exception:
                    print("  [RFI] Louvain not installed, falling back to greedy...")
                    self.use_louvain = False
            if not self.use_louvain:
                if n_nodes <= 10:
                    cutoff = 1
                    best_n = max(1, n_nodes - 1)
                else:
                    cutoff = min(10, n_nodes // 4)
                    best_n = max(cutoff, min(20, n_nodes // 2))
                communities = list(nx.community.greedy_modularity_communities(self.G_main, cutoff=cutoff, best_n=best_n))
                Q = nx.community.modularity(self.G_main, communities)
                n_communities = len(communities)
                # Build community mapping from greedy communities
                for comm_id, community in enumerate(communities):
                    for node in community:
                        community_mapping[str(node)] = int(comm_id)
        except Exception as e:
            print(f"  [RFI Warning] Modularity computation failed: {e}")
            Q = 0.0
            n_communities = 0
            community_mapping = {}
        return Q, n_communities, community_mapping

    def _compute_connectivity(self):
        if self.G_main is None:
            self._build_graph()
        if self.G_main is None:
            return 0.0, 0.0
        try:
            h = nx.average_clustering(self.G_main, weight='weight' if self.weighted else None)
        except Exception:
            h = 0.0
        try:
            laplacian = nx.normalized_laplacian_matrix(self.G_main).toarray()
            eigenvals = np.linalg.eigvalsh(laplacian)
            eigenvals = np.sort(eigenvals)
            lambda_2 = eigenvals[1] if len(eigenvals) > 1 else 0.0
        except Exception:
            lambda_2 = 0.0
        return h, lambda_2

    def compute(self) -> dict:
        if self.G_main is None:
            self._build_graph()
        G = self.G_main
        if G is None or len(G) == 0:
            return {
                'rfi': 0.0,
                'modularity_Q': 0.0,
                'homophily_h': 0.0,
                'lambda_2': 0.0,
                'n_communities': 0,
                'n_components': int(self.n_components),
                'avg_degree': 0.0,
                'density': 0.0,
                'transitivity': 0.0,
                'diameter': None,
                'avg_path_length': None,
                'n_nodes': 0,
                'n_edges': 0,
                'community_mapping': {},
                'adjacency_matrix': []
            }
        Q, n_communities, community_mapping = self._compute_modularity()
        h, lambda_2 = self._compute_connectivity()

        lambda_2 = max(lambda_2, 1e-6)
        rfi = Q * (1 - h) / lambda_2
        rfi = float(np.clip(rfi, 0, 1e6))

        try:
            A_main = nx.to_numpy_array(G)
            deg_values = A_main.sum(axis=1)
            avg_degree = float(np.mean(deg_values)) if deg_values.size > 0 else 0.0
        except Exception:
            avg_degree = 0.0

        try:
            density = nx.density(G)
        except Exception:
            density = 0.0

        try:
            transitivity = nx.transitivity(G)
        except Exception:
            transitivity = 0.0

        try:
            diameter = nx.diameter(G) if len(G) > 1 and nx.is_connected(G) else None
        except Exception:
            diameter = None

        try:
            avg_path_length = nx.average_shortest_path_length(G) if len(G) > 1 and nx.is_connected(G) else None
        except Exception:
            avg_path_length = None

        return {
            'rfi': float(rfi),
            'modularity_Q': float(Q),
            'homophily_h': float(h),
            'lambda_2': float(lambda_2),
            'n_communities': int(n_communities),
            'n_components': int(self.n_components),
            'avg_degree': float(avg_degree),
            'density': float(density),
            'transitivity': float(transitivity),
            'diameter': float(diameter) if diameter is not None else None,
            'avg_path_length': float(avg_path_length) if avg_path_length is not None else None,
            'n_nodes': len(G),
            'n_edges': G.number_of_edges(),
            'community_mapping': community_mapping,
            'adjacency_matrix': self.adj_matrix.tolist()
        }

def compute_rfi(adj_matrix, weighted=True, use_louvain=False):
    """Compute RFI via RFITopology encapsulation."""
    return RFITopology(adj_matrix, weighted=weighted, use_louvain=use_louvain).compute()

###############################################################################
# PART 3: Shape Classification
###############################################################################

def classify_shape(adj_matrix, rfi_metrics, corr_matrix=None):
    """Classify topological shape."""
    Q = rfi_metrics['modularity_Q']
    lambda_2 = rfi_metrics['lambda_2']
    density = rfi_metrics['density']
    h = rfi_metrics['homophily_h']
    transitivity = rfi_metrics['transitivity']
    
    # Identity correlation implies perfectly orthogonal features
    if corr_matrix is not None and corr_matrix.size > 0 and np.allclose(corr_matrix, np.eye(corr_matrix.shape[0])):
        return {
            'shape': 'Identity',
            'archetype': 'Perfectly Orthogonal',
            'glyph': 'I',
            'degree_cv': 0.0,
            'degree_mean': 0.0,
            'degree_std': 0.0,
            'degree_max': 0,
            'assortativity': 0.0
        }

    G = nx.from_numpy_array(adj_matrix)
    G.remove_edges_from(nx.selfloop_edges(G))
    
    components = list(nx.connected_components(G))
    if len(components) > 1:
        largest_cc = max(components, key=len)
        G = G.subgraph(largest_cc).copy()
    
    try:
        A_g = nx.to_numpy_array(G)
        degrees = A_g.sum(axis=1)
        deg_std = float(np.std(degrees)) if degrees.size > 0 else 0.0
        deg_mean = float(np.mean(degrees)) if degrees.size > 0 else 0.0
        deg_cv = deg_std / deg_mean if deg_mean > 0 else 0.0
        deg_max = int(np.max(degrees)) if degrees.size > 0 else 0
    except Exception:
        degrees = np.array([])
        deg_std = 0.0
        deg_mean = 0.0
        deg_cv = 0.0
        deg_max = 0
    
    try:
        assortativity = nx.degree_assortativity_coefficient(G)
    except:
        assortativity = 0.0
    
    # Classification via rules table (first match wins)
    rules = [
        (lambda: density > 0.9, ("Complete Graph", "Fully Connected (Maximal Redundancy)", "●")),
        (lambda: Q > 0.4 and lambda_2 < 0.5, ("Modular Blocks", "Traversable Distortion → Truth", "⊕")),
        (lambda: density > 0.5 and Q < 0.2 and lambda_2 > 0.5, ("Expander", "Irreducible Distortion (NP-Hard)", "∞")),
        (lambda: deg_cv > 1.5 and assortativity < 0, ("Core-Periphery", "Hierarchical Bridge", "ɸ")),
        (lambda: len(G) > 0 and deg_max > 0.5 * len(G) and deg_cv > 2.0, ("Star", "Hub Dominance", "★")),
        (lambda: Q > 0.6 and rfi_metrics['n_communities'] == 2, ("Bipartite", "Dual Projection", "λ")),
        (lambda: transitivity < 0.1 and rfi_metrics.get('diameter') and rfi_metrics['diameter'] > 0.5 * len(G), ("Chain/Path", "Sequential Dependency", "—")),
        (lambda: density < 0.2 and lambda_2 > 0.7, ("Orthogonal Sparse", "Truth Lattice (Ω)", "Ω")),
        (lambda: 0.3 < Q < 0.5 and 0.3 < density < 0.7, ("Random Graph", "Erdős–Rényi Baseline", "◯")),
    ]
    shape, archetype, glyph = "Intermediate", "Mixed Field", "Ψ"
    for pred, (s, a, g) in rules:
        try:
            if pred():
                shape, archetype, glyph = s, a, g
                break
        except Exception:
            # Ignore rule errors and continue to next rule
            continue
    
    return {
        'shape': shape,
        'archetype': archetype,
        'glyph': glyph,
        'degree_cv': float(deg_cv),
        'degree_mean': float(deg_mean),
        'degree_std': float(deg_std),
        'degree_max': int(deg_max),
        'assortativity': float(assortativity)
    }

###############################################################################
# PART 4: Symbolic Mapping (Truth ↔ Distortion Lattice)
###############################################################################

def map_to_lattice(meff_metrics, rfi_metrics, shape_metrics):
    """Map to Truth ↔ Distortion lattice position."""
    collapse_ratio = meff_metrics['collapse_ratio']
    rfi = rfi_metrics['rfi']
    shape = shape_metrics['shape']
    Q = rfi_metrics['modularity_Q']
    
    if collapse_ratio < 0.15 and rfi > 3.0:
        lattice = "Truth Lattice (Ω)"
        status = "Fully Collapsed - Maintain"
        protocol = "System at minimal distortion. Observe and maintain coherence."
        collapse_potential = "Complete"
        
    elif collapse_ratio < 0.3 and rfi > 2.0 and shape == "Modular Blocks":
        lattice = "Traversable Distortion (Modular)"
        status = "Collapsible via Community Decomposition"
        protocol = "Apply spectral clustering → compute per-module M_eff → integrate symbolic modules → collapse to truth coordinates."
        collapse_potential = "High"
        
    elif collapse_ratio > 0.7 and rfi < 1.0:
        lattice = "Irreducible Distortion (∞_B)"
        status = "NP-Hard Expansion - Reparameterize"
        protocol = "High-dimensional expander detected. Use approximation algorithms, anchor-based strategies, or accept bounded solution."
        collapse_potential = "Low"
        
    elif 0.3 <= collapse_ratio <= 0.7 and rfi > 1.0:
        lattice = "Intermediate Field (Partial Collapse)"
        status = "Incremental Collapse Available"
        protocol = "Mixed structure. Identify high-RFI subgraphs → collapse incrementally → monitor residue reduction."
        collapse_potential = "Medium"
        
    elif collapse_ratio < 0.3 and rfi < 1.0:
        lattice = "Fragmented Collapse"
        status = "Disconnected Modules"
        protocol = "Low connectivity despite collapse. Reconnect weakly connected components or treat as independent subsystems."
        collapse_potential = "Medium"
        
    elif collapse_ratio > 0.7 and rfi > 2.0:
        lattice = "Structured Complexity"
        status = "High-Dimensional but Organized"
        protocol = "Topology is coherent but dimensionality is high. Use dimensionality reduction (PCA, UMAP) before collapse."
        collapse_potential = "Medium"
        
    else:
        lattice = "Unknown Configuration"
        status = "Edge Case - Manual Inspection Required"
        protocol = "Metrics outside standard classification bounds. Verify data quality and check for anomalies."
        collapse_potential = "Unknown"
    
    return {
        'lattice_position': lattice,
        'status': status,
        'recommended_protocol': protocol,
        'collapse_potential': collapse_potential,
        'traversal_strategy': "Modular" if Q > 0.4 else "Direct" if rfi > 3.0 else "Approximation"
    }

###############################################################################
# PART 4B: Interpretation Layer (v2.2 NEW)
###############################################################################

def _interpret_collapse_direction(collapse_ratio: float, rfi: float) -> str:
    if collapse_ratio < 0.2 and rfi > 2.5:
        return "Increasing"
    if collapse_ratio > 0.6 and rfi < 1.5:
        return "Decreasing"
    return "Stable"


def _infer_dominant_mode(collapse_ratio: float, rfi_metrics: dict) -> str:
    if collapse_ratio < 0.3 and rfi_metrics.get('rfi', 0.0) < 1.0:
        return "Collapsed but Disconnected"
    if collapse_ratio < 0.3:
        return "Collapsed"
    if rfi_metrics.get('modularity_Q', 0.0) > 0.4:
        return "Modular"
    if collapse_ratio > 0.7:
        return "Expanding"
    return "Fragmented"


def _narrative_state_from_lattice(lattice_map: dict) -> str:
    return lattice_map.get('lattice_position', 'Unknown').split('(')[0].strip()


def _format_distortion_core(meff_metrics: dict) -> str:
    top_eigs = (list(meff_metrics.get('top_10_eigenvalues', [])) + [0, 0, 0])[:3]
    return f"Axes [0, 1, 2] (λ = {top_eigs})"


def generate_interpretation(meff_metrics, rfi_metrics, shape_metrics, lattice_map, residue_profile):
    """
    Generate narrative coherence interpretation.
    
    Synthesizes all metrics into human-readable story.
    """
    print("\n[Interpretation] Generating narrative synthesis...")
    
    try:
        # Degenerate graph case
        if rfi_metrics.get('n_nodes', 0) < 2:
            print("  [Warning] Degenerate graph (n_nodes < 2), returning degenerate interpretation.")
            return {
                'coherence_direction': 'N/A',
                'dominant_mode': 'Degenerate',
                'distortion_core': 'N/A',
                'narrative_state': 'No Relational Field',
                'residue_level': 'N/A',
                'collapse_potential': 'N/A',
                'status': 'degenerate_graph'
            }

        collapse_ratio = meff_metrics.get('collapse_ratio', 0.0)
        rfi = rfi_metrics.get('rfi', 0.0)
        residue = residue_profile.get('residue_mean', 0.0)

        # Coherence direction
        coherence_direction = _interpret_collapse_direction(collapse_ratio, rfi)

        # Dominant mode
        dominant_mode = _infer_dominant_mode(collapse_ratio, rfi_metrics)

        # Distortion core (top 3 eigenvalue axes)
        distortion_core = _format_distortion_core(meff_metrics)

        # Narrative state
        narrative_state = _narrative_state_from_lattice(lattice_map)
    
        print(f"  Coherence Direction: {coherence_direction}")
        print(f"  Dominant Mode: {dominant_mode}")
        
        return {
            'coherence_direction': coherence_direction,
            'dominant_mode': dominant_mode,
            'distortion_core': distortion_core,
            'narrative_state': narrative_state,
            'residue_level': residue_profile.get('residue_level', 'Unknown'),
            'collapse_potential': lattice_map.get('collapse_potential', 'Unknown')
        }
    except Exception as e:
        print(f"  [Interpretation Warning] Fallback due to error: {e}")
        return {
            'coherence_direction': 'Stable',
            'dominant_mode': 'Fragmented',
            'distortion_core': 'N/A',
            'narrative_state': 'Unknown',
            'residue_level': residue_profile.get('residue_level', 'Unknown'),
            'collapse_potential': lattice_map.get('collapse_potential', 'Unknown'),
            'status': 'fallback'
        }

###############################################################################
# PART 5: Visualization
###############################################################################

def generate_visualizations(meff_metrics, rfi_metrics, shape_metrics, lattice_map, out_dir, skip_visuals=False):
    """Generate diagnostic visualizations."""
    if skip_visuals:
        print("  [Viz] Skipping visualization (--no-visuals flag)")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    eigenvals = meff_metrics['eigenvalues'][:500]
    axes[0, 0].plot(range(1, len(eigenvals)+1), eigenvals, 'o-', linewidth=2, markersize=3)
    axes[0, 0].axhline(y=1, color='r', linestyle='--', linewidth=1.5, label='λ=1 threshold')
    axes[0, 0].set_xlabel('Eigenvalue Index', fontsize=11)
    axes[0, 0].set_ylabel('Eigenvalue Magnitude', fontsize=11)
    axes[0, 0].set_title(f'Eigenvalue Spectrum\nM_eff={meff_metrics["meff_min"]:.1f} / m={meff_metrics["m_total"]}', fontsize=12)
    axes[0, 0].legend(fontsize=9)
    axes[0, 0].grid(True, alpha=0.3)
    if len(eigenvals) > 1:
        axes[0, 0].set_yscale('log')
    
    collapse_ratio = meff_metrics['collapse_ratio']
    rfi_value = rfi_metrics['rfi']
    
    axes[0, 1].scatter([rfi_value], [collapse_ratio], s=400, c='red', marker='*', zorder=10, edgecolors='black', linewidths=2)
    axes[0, 1].set_xlabel('RFI (Relational Field Index)', fontsize=11)
    axes[0, 1].set_ylabel('Collapse Ratio (M_eff / m)', fontsize=11)
    axes[0, 1].set_title(f'Truth ↔ Distortion Position\n{lattice_map["lattice_position"]}', fontsize=12)
    
    axes[0, 1].axhline(y=0.3, color='gray', linestyle='--', alpha=0.4)
    axes[0, 1].axvline(x=2.0, color='gray', linestyle='--', alpha=0.4)
    axes[0, 1].text(0.5, 0.85, 'Irreducible\nDistortion ∞', ha='center', fontsize=9, color='darkred', weight='bold')
    axes[0, 1].text(3.5, 0.2, 'Traversable\nDistortion ⊕', ha='center', fontsize=9, color='darkorange', weight='bold')
    axes[0, 1].text(3.5, 0.05, 'Truth Ω', ha='center', fontsize=9, color='darkgreen', weight='bold')
    axes[0, 1].grid(True, alpha=0.3)
    rfi_clamped = max(0.0, min(rfi_value, 20.0))
    axes[0, 1].set_xlim(-0.5, max(5, rfi_clamped + 1))
    axes[0, 1].set_ylim(0, 1)
    
    categories = ['Collapse', 'RFI', 'Modularity', 'Connectivity', 'Clustering']
    values = [
        1 - collapse_ratio,
        min(rfi_value / 5.0, 1.0),
        rfi_metrics['modularity_Q'],
        min(rfi_metrics['lambda_2'], 1.0),
        rfi_metrics['homophily_h']
    ]
    
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]
    
    ax_radar = plt.subplot(223, projection='polar')
    ax_radar.plot(angles, values, 'o-', linewidth=2, color='teal')
    ax_radar.fill(angles, values, alpha=0.25, color='teal')
    ax_radar.set_xticks(angles[:-1])
    ax_radar.set_xticklabels(categories, fontsize=9)
    ax_radar.set_ylim(0, 1)
    ax_radar.set_title('Metric Profile', fontsize=12, pad=20)
    ax_radar.grid(True)
    
    axes[1, 1].text(0.5, 0.7, f'Shape: {shape_metrics["shape"]}', ha='center', fontsize=14, weight='bold')
    axes[1, 1].text(0.5, 0.5, f'Glyph: {shape_metrics["glyph"]}', ha='center', fontsize=48)
    axes[1, 1].text(0.5, 0.3, f'{shape_metrics["archetype"]}', ha='center', fontsize=11, style='italic', wrap=True)
    axes[1, 1].text(0.5, 0.1, f'Collapse Potential: {lattice_map["collapse_potential"]}', ha='center', fontsize=12, 
                    color='darkgreen' if lattice_map["collapse_potential"] == "High" else 'darkorange')
    axes[1, 1].axis('off')
    axes[1, 1].set_xlim(0, 1)
    axes[1, 1].set_ylim(0, 1)
    
    plt.tight_layout()
    plt.savefig(f'{out_dir}/truth_distortion_diagnostic.png', dpi=200, bbox_inches='tight')
    plt.close('all')
    gc.collect()

###############################################################################
# PART 6: Unified Pipeline
###############################################################################

def run_unified_diagnostic(
    data_path,
    data_type='auto',
    corr_method='pearson',
    adj_threshold=0.7,
    out_dir='results',
    compute_null=False,
    n_permutations=100,
    eig_topk=100,
    use_louvain=False,
    skip_visuals=False,
    seed=None
):
    """Run complete diagnostic pipeline with v2.2 intelligence layers."""
    start_time = time.time()
    
    if seed is not None:
        np.random.seed(seed)
        print(f"[Seed] Random seed set to {seed}")
    
    os.makedirs(out_dir, exist_ok=True)
    
    print("="*70)
    print(f" Truth ↔ Distortion Unified Diagnostic v{__version__}")
    print("="*70)
    
    # Load data
    print(f"\n[1/7] Loading data: {data_path}")
    corr_matrix, adj_matrix, metadata = load_data_with_pipeline(
        data_path, data_type, corr_method, adj_threshold
    )
    print(f"  Correlation matrix: {corr_matrix.shape}")
    print(f"  Adjacency matrix: {adj_matrix.shape}")

    # Validate and gently correct loaded matrices; enrich metadata
    corr_matrix, adj_matrix, metadata = validate_loaded_data(corr_matrix, adj_matrix, metadata)
    
    # M_eff
    print("\n[2/7] Computing M_eff (dimensional collapse)...")
    meff_metrics = compute_meff(corr_matrix, n_permutations if compute_null else None, eig_topk)
    print(f"  M_eff (Li-Ji): {meff_metrics['meff_liji']:.2f}")
    print(f"  M_eff (min-λ): {meff_metrics['meff_min']:.2f}")
    print(f"  Collapse ratio: {meff_metrics['collapse_ratio']:.2%}")
    
    # Collapse Map (v2.2)
    collapse_map = compute_collapse_map(corr_matrix, meff_metrics, out_dir)
    
    # Residue Profile (v2.2)
    residue_profile = compute_residue_profile(corr_matrix)
    
    # RFI
    print("\n[3/7] Computing RFI (relational topology)...")
    rfi_metrics = compute_rfi(adj_matrix, weighted=True, use_louvain=use_louvain)
    print(f"  RFI: {rfi_metrics['rfi']:.3f}")
    print(f"  Modularity Q: {rfi_metrics['modularity_Q']:.3f}")
    print(f"  λ₂: {rfi_metrics['lambda_2']:.3f}")
    
    # Shape
    print("\n[4/7] Classifying topological shape...")
    shape_metrics = classify_shape(adj_matrix, rfi_metrics, corr_matrix)
    print(f"  Shape: {shape_metrics['shape']}")
    print(f"  Glyph: {shape_metrics['glyph']}")
    print(f"  Archetype: {shape_metrics['archetype']}")
    
    # Lattice
    print("\n[5/7] Mapping to Truth ↔ Distortion lattice...")
    lattice_map = map_to_lattice(meff_metrics, rfi_metrics, shape_metrics)
    print(f"  Position: {lattice_map['lattice_position']}")
    print(f"  Status: {lattice_map['status']}")
    print(f"  Collapse potential: {lattice_map['collapse_potential']}")
    
    # Interpretation (v2.2)
    interpretation = generate_interpretation(meff_metrics, rfi_metrics, shape_metrics, lattice_map, residue_profile)
    
    # Visualization
    print("\n[6/7] Generating visualizations...")
    generate_visualizations(meff_metrics, rfi_metrics, shape_metrics, lattice_map, out_dir, skip_visuals)
    
    runtime = time.time() - start_time
    
    # Save results
    print("\n[7/7] Saving results...")
    report = {
        'metadata': metadata,
        'meff': meff_metrics,
        'collapse_map': collapse_map,
        'residue_profile': residue_profile,
        'rfi': rfi_metrics,
        'shape': shape_metrics,
        'lattice': lattice_map,
        'interpretation': interpretation,
        'version': __version__,
        'runtime_seconds': float(runtime)
    }
    
    # Ensure JSON-serializable
    report = sanitize_for_json(report)
    with open(f'{out_dir}/unified_diagnostic.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Summary
    summary = f"""
╔═══════════════════════════════════════════════════════════════════╗
║      TRUTH ↔ DISTORTION UNIFIED DIAGNOSTIC REPORT v{__version__}   ║
╚═══════════════════════════════════════════════════════════════════╝

DATA METADATA
  Input type:        {metadata['input_type']}
  Shape:             {metadata['corr_shape']}

DIMENSIONAL COLLAPSE (M_eff)
  M_eff (Li-Ji):     {meff_metrics['meff_liji']:.2f}
  M_eff (min-λ):     {meff_metrics['meff_min']:.2f}
  M_eff (entropy):   {meff_metrics['meff_entropy']:.2f}
  Total dimensions:  {meff_metrics['m_total']}
  Effective dims:    {meff_metrics['m_effective']}
  Collapse ratio:    {meff_metrics['collapse_ratio']:.2%}

RESIDUE PROFILE
  Mean residue:      {residue_profile['residue_mean']:.3f}
  Max residue:       {residue_profile['residue_max']:.3f}
  Residue level:     {residue_profile['residue_level']}

RELATIONAL TOPOLOGY (RFI)
  RFI:               {rfi_metrics['rfi']:.3f}
  Modularity (Q):    {rfi_metrics['modularity_Q']:.3f}
  Homophily (h):     {rfi_metrics['homophily_h']:.3f}
  λ₂:                {rfi_metrics['lambda_2']:.3f}
  Density:           {rfi_metrics['density']:.3f}
  Transitivity:      {rfi_metrics['transitivity']:.3f}
  Components:        {rfi_metrics['n_components']}

TOPOLOGICAL SHAPE
  Shape:             {shape_metrics['shape']}
  Glyph:             {shape_metrics['glyph']}
  Archetype:         {shape_metrics['archetype']}
  Degree CV:         {shape_metrics['degree_cv']:.2f}
  Assortativity:     {shape_metrics['assortativity']:.3f}

LATTICE POSITION
  Position:          {lattice_map['lattice_position']}
  Status:            {lattice_map['status']}
  Collapse potential: {lattice_map['collapse_potential']}
  Traversal strategy: {lattice_map['traversal_strategy']}

INTERPRETATION
  Coherence Direction:   {interpretation['coherence_direction']}
  Dominant Mode:         {interpretation['dominant_mode']}
  Distortion Core:       {interpretation['distortion_core']}
  Narrative State:       {interpretation['narrative_state']}
  Residue Level:         {interpretation['residue_level']}
  Collapse Potential:    {interpretation['collapse_potential']}

RECOMMENDED PROTOCOL
  {lattice_map['recommended_protocol']}

SYSTEM INFO
  Runtime:           {runtime:.2f} seconds
  Version:           {__version__}

═══════════════════════════════════════════════════════════════════
Generated by Mirror-OS Truth ↔ Distortion Diagnostic Suite
https://github.com/Mirror-OS/truth-distortion-diagnostic
═══════════════════════════════════════════════════════════════════
"""
    
    with open(f'{out_dir}/summary.txt', 'w') as f:
        f.write(summary)
    
    print(summary)
    print(f"\n✓ Complete! Results saved to {out_dir}/")
    print(f"  - unified_diagnostic.json")
    print(f"  - summary.txt")
    if isinstance(collapse_map, dict) and collapse_map.get('status') == 'computed':
        print(f"  - collapse_map.csv")
    if not skip_visuals:
        print(f"  - truth_distortion_diagnostic.png")
    return report

###############################################################################
# PART 7: Self-Diagnostic Mode (Recursive Analysis)
###############################################################################

def extract_function_metrics():
    """
    Extract quantitative metrics from this script's own functions.
    Treats each function as a node, measures coupling via call graphs.
    """
    import ast
    import sys

    # Get source code from the actual script file
    try:
        script_path = __file__
        with open(script_path, 'r') as f:
            source = f.read()
    except Exception:
        print("  [Error] Cannot read source file for self-analysis")
        return {}

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"  [Error] Syntax error in source: {e}")
        return {}

    # Extract all function definitions
    functions = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name

            # Count internal calls (coupling)
            calls = []
            for n in ast.walk(node):
                if isinstance(n, ast.Call):
                    # Handle both direct calls and attribute calls
                    if isinstance(n.func, ast.Name):
                        calls.append(n.func.id)
                    elif isinstance(n.func, ast.Attribute):
                        # For things like self.method() or obj.func()
                        if isinstance(n.func.value, ast.Name):
                            calls.append(n.func.attr)

            # Count branches (complexity)
            branches = sum(1 for n in ast.walk(node) if isinstance(n, ast.If))

            # Count loops
            loops = sum(1 for n in ast.walk(node) \
                       if isinstance(n, (ast.For, ast.While)))

            # Lines of code (robust to missing end_lineno)
            start = getattr(node, 'lineno', None)
            end = getattr(node, 'end_lineno', None)
            if isinstance(start, int) and isinstance(end, int) and end >= start:
                loc = int(end - start)
            else:
                loc = 0

            functions[func_name] = {
                'calls': calls,
                'branches': branches,
                'loops': loops,
                'loc': loc,
                'complexity': branches + loops + 1
            }

    return functions

def build_function_correlation_matrix(functions):
    """
    Build correlation matrix from function call graph.

    Returns:
      - R_combined: blended correlation + call graph similarity
      - func_names: list of function names in order
      - call_graph: symmetric 0/1 adjacency from direct calls

    C[i,j] = correlation between function i and function j based on:
      - Direct call relationships
      - Shared complexity patterns
      - Similar LOC
    """
    func_names = list(functions.keys())
    n = len(func_names)

    if n == 0:
        return np.eye(1), ['no_functions'], np.zeros((1, 1))

    # Initialize feature matrix
    # Rows = functions, Cols = [complexity, loc, #calls, #branches, #loops]
    X = np.zeros((n, 5))

    for i, fname in enumerate(func_names):
        f = functions[fname]
        X[i, 0] = f['complexity']
        X[i, 1] = f['loc']
        X[i, 2] = len(f['calls'])
        X[i, 3] = f['branches']
        X[i, 4] = f['loops']

    # Standardize (avoid division by zero)
    X_std = X.std(axis=0)
    X_std[X_std < 1e-12] = 1.0
    X = (X - X.mean(axis=0)) / X_std

    # Compute correlation
    if n > 1:
        R = np.corrcoef(X)
    else:
        R = np.ones((1, 1))

    # Add call graph edges (direct coupling)
    call_graph = np.zeros((n, n))
    for i, fname in enumerate(func_names):
        for call in functions[fname]['calls']:
            if call in func_names:
                j = func_names.index(call)
                call_graph[i, j] = 1.0

    # Make call graph symmetric (bidirectional coupling)
    call_graph = (call_graph + call_graph.T) / 2.0

    # Blend correlation + call graph
    R_combined = 0.6 * R + 0.4 * call_graph
    np.fill_diagonal(R_combined, 1.0)

    # Sanitize
    R_combined = np.nan_to_num(R_combined, nan=0.0, posinf=1.0, neginf=-1.0)

    return R_combined, func_names, call_graph

def self_test(out_dir='self_diagnostic', save_history: bool = False, history_path: str | None = None):
    """
    Run the diagnostic on itself.

    Computes M_eff of the program's own function structure.
    """
    print("\n" + "="*70)
    print(" 🔄 SELF-DIAGNOSTIC MODE: Program Analyzing Itself")
    print("="*70)

    # Extract function metrics
    print("\n[1/4] Extracting function metrics from source code...")
    functions = extract_function_metrics()

    if not functions:
        print("  [Error] No functions found or source unavailable")
        return None

    print(f"  Found {len(functions)} functions")

    # Build correlation matrix + call graph
    print("\n[2/4] Building function correlation and call graph...")
    corr_matrix, func_names, call_graph = build_function_correlation_matrix(functions)
    print(f"  Correlation matrix: {corr_matrix.shape}")

    # Compute M_eff
    print("\n[3/4] Computing M_eff of program structure...")
    meff_metrics = compute_meff(corr_matrix)

    print(f"\n  📊 PROGRAM COMPLEXITY METRICS:")
    print(f"     M_eff: {meff_metrics['meff_min']:.2f} / {meff_metrics['m_total']}")
    print(f"     Collapse ratio: {meff_metrics['collapse_ratio']:.2%}")
    print(f"     Effective dimensionality: {meff_metrics['m_effective']}")

    # Interpret
    if meff_metrics['collapse_ratio'] < 0.3:
        status = "✅ HIGHLY MODULAR (Low coupling)"
        recommendation = "Code is well-factored with minimal redundancy."
    elif meff_metrics['collapse_ratio'] < 0.6:
        status = "⚠️  MODERATE COUPLING"
        recommendation = "Some refactoring opportunities exist."
    else:
        status = "❌ HIGH COUPLING (Spaghetti code)"
        recommendation = "Significant refactoring needed—functions too interdependent."

    print(f"\n  🎯 ASSESSMENT: {status}")
    print(f"     {recommendation}")

    # Build adjacency for RFI from pure call graph (stronger topology signal)
    adj_matrix = (call_graph > 0).astype(np.int8)
    np.fill_diagonal(adj_matrix, 0)

    # Compute RFI
    print("\n[4/4] Computing RFI of function call graph...")
    rfi_metrics = compute_rfi(adj_matrix, weighted=False)

    print(f"\n  📈 RELATIONAL TOPOLOGY:")
    print(f"     RFI: {rfi_metrics['rfi']:.3f}")
    print(f"     Modularity: {rfi_metrics['modularity_Q']:.3f}")
    print(f"     Communities: {rfi_metrics['n_communities']}")

    # Classify shape
    shape_metrics = classify_shape(adj_matrix, rfi_metrics, corr_matrix)
    print(f"\n  🔷 PROGRAM SHAPE: {shape_metrics['shape']}")
    print(f"     Glyph: {shape_metrics['glyph']}")
    print(f"     Archetype: {shape_metrics['archetype']}")

    # Identify most coupled functions (collapse drivers)
    print("\n  🔗 TOP 5 COUPLED FUNCTIONS (Collapse Drivers):")
    coupling_scores = np.sum(np.abs(corr_matrix), axis=0)
    top_indices = np.argsort(coupling_scores)[::-1][:min(5, len(func_names))]
    for idx in top_indices:
        fname = func_names[idx]
        score = coupling_scores[idx]
        print(f"     {fname}: {score:.2f}")

    # Save self-diagnostic report
    os.makedirs(out_dir, exist_ok=True)

    report = {
        'program_metrics': {
            'n_functions': len(functions),
            'meff': meff_metrics,
            'rfi': rfi_metrics,
            'shape': shape_metrics
        },
        'function_names': func_names,
        'coupling_scores': coupling_scores.tolist()
    }

    with open(f'{out_dir}/self_diagnostic.json', 'w') as f:
        json.dump(report, f, indent=2)

    # Optionally append to history
    if save_history:
        hp = history_path or os.path.join(out_dir, 'history.json')
        history_manager = HistoryManager(hp)
        entry = {
            'timestamp': float(time.time()),
            'version': __version__,
            'n_functions': int(len(functions)),
            'meff_min': float(meff_metrics.get('meff_min', 0.0)),
            'collapse_ratio': float(meff_metrics.get('collapse_ratio', 0.0)),
            'eigenvalues': meff_metrics.get('eigenvalues', [])[:10],
            'rfi': float(rfi_metrics.get('rfi', 0.0)),
            'modularity_Q': float(rfi_metrics.get('modularity_Q', 0.0)),
            'lambda_2': float(rfi_metrics.get('lambda_2', 0.0)),
        }
        history_manager.append(entry)

    print(f"\n✓ Self-diagnostic complete! Report saved to {out_dir}/")
    
    return report

###############################################################################
# PART 7B: Convergence Utilities (Recursive Coherence Detection)
###############################################################################

class HistoryManager:
    """Manages loading and saving of the self-diagnostic history file."""
    def __init__(self, history_path: str):
        self.history_path = history_path

    def load(self) -> list:
        if not os.path.exists(self.history_path):
            return []
        try:
            with open(self.history_path, 'r') as f:
                data = json.load(f)
            if isinstance(data, dict) and 'history' in data:
                return data['history']
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, IOError):
            return []

    def save(self, history: list):
        os.makedirs(os.path.dirname(self.history_path), exist_ok=True)
        with open(self.history_path, 'w') as f:
            json.dump(history, f, indent=2)

    def append(self, entry: dict):
        history = self.load()
        history.append(entry)
        if len(history) > 500: # Keep history manageable
            history = history[-500:]
        self.save(history)
        print(f"  [History] Appended iteration to {self.history_path} (n={len(history)})")


def check_convergence(history_file: str = 'self_diagnostic/history.json', window: int = 3, variation_threshold: float = 0.02) -> bool:
    """Return True if M_eff has plateaued within the last `window` entries."""
    hist = HistoryManager(history_file).load()
    if len(hist) < window:
        print(f"[Convergence] Not enough history (have {len(hist)}, need {window})")
        return False
    recent = hist[-window:]
    meffs = [float(h.get('meff_min', 0.0)) for h in recent]
    mean = float(np.mean(meffs)) if len(meffs) else 0.0
    std = float(np.std(meffs)) if len(meffs) else 0.0
    variation = (std / mean) if mean > 0 else 1.0
    print(f"[Convergence] Recent M_eff: {meffs} | variation={variation*100:.2f}% | threshold={variation_threshold*100:.2f}%")
    return variation < variation_threshold

def rfi_stable(history_file: str = 'self_diagnostic/history.json', delta: float = 0.1) -> bool:
    hist = HistoryManager(history_file).load()
    if len(hist) < 2:
        return False
    r1 = float(hist[-1].get('rfi', 0.0))
    r0 = float(hist[-2].get('rfi', 0.0))
    diff = abs(r1 - r0)
    print(f"[Convergence] RFI change: {diff:.3f} (threshold {delta:.3f})")
    return diff < delta

def eigenvalue_gap_clear(history_file: str = 'self_diagnostic/history.json', gap_threshold: float = 0.3) -> bool:
    hist = HistoryManager(history_file).load()
    if not hist:
        return False
    eigs = hist[-1].get('eigenvalues', [])
    if not eigs or len(eigs) < 3:
        return False
    lam1, lam2, lam3 = float(eigs[0]), float(eigs[1]), float(eigs[2])
    if lam1 <= 0:
        return False
    ratio = (lam2 - lam3) / lam1
    print(f"[Convergence] Eigen gap ratio: {ratio:.3f} (threshold {gap_threshold:.3f})")
    return ratio > gap_threshold

def generate_convergence_report(history_file: str = 'self_diagnostic/history.json') -> dict:
    status = 'CONVERGED' if check_convergence(history_file) else 'EVOLVING'
    evidence = []
    hist = HistoryManager(history_file).load()
    recent_meff = [float(h.get('meff_min', 0.0)) for h in hist[-3:]] if len(hist) >= 3 else []

    if status == 'CONVERGED':
        evidence.append({
            'signal': 'M_eff plateau',
            'recent_meff': recent_meff,
            'interpretation': 'Dimensional collapse has reached natural limit'
        })
        if eigenvalue_gap_clear(history_file):
            evidence.append({
                'signal': 'Eigenvalue separation',
                'interpretation': 'Functional modules fully resolved'
            })
        if rfi_stable(history_file):
            evidence.append({
                'signal': 'RFI stabilization',
                'interpretation': 'Communication topology finalized'
            })
        conclusion = 'System has collapsed to minimal complete description (Ω)'
    else:
        conclusion = 'System still becoming (𝒰) - continue refactoring'

    return {
        'status': status,
        'evidence': evidence,
        'conclusion': conclusion
    }

###############################################################################
# CLI
###############################################################################

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Truth ↔ Distortion Unified Diagnostic v2.2 (Intelligence Layer)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
v2.2 New Features:
  - Collapse Map: Feature importance for dimensional reduction
  - Residue Profile: Off-diagonal correlation distortion
  - Interpretation Layer: Narrative coherence synthesis

Examples:
  python truth_distortion_unified.py --data gene_expr.csv --type tabular --out results/
  python truth_distortion_unified.py --data corr_matrix.csv --type corr --seed 42 --out results/
  python truth_distortion_unified.py --data network.csv --type adj --use-louvain --out results/
  
  # Self-diagnostic mode (analyze program's own structure)
  python truth_distortion_unified.py --self-test --out self_diagnostic/
        """
    )

    parser.add_argument('--data', type=str, required=False, help='Input data file (CSV) [not needed for --self-test]')
    parser.add_argument('--type', type=str, default='auto', 
                        choices=['auto', 'tabular', 'corr', 'adj', 'edgelist'],
                        help='Data type (default: auto-detect)')
    parser.add_argument('--corr-method', type=str, default='pearson',
                        choices=['pearson', 'spearman', 'kendall'],
                        help='Correlation method for tabular data (default: pearson)')
    parser.add_argument('--adj-threshold', type=float, default=0.7,
                        help='Correlation threshold for adjacency matrix (default: 0.7)')
    parser.add_argument('--out', type=str, default='results',
                        help='Output directory (default: results/)')
    parser.add_argument('--compute-null', action='store_true',
                        help='Compute permutation-based null M_eff (slower)')
    parser.add_argument('--n-permutations', type=int, default=100,
                        help='Number of permutations for null model (default: 100)')
    parser.add_argument('--eig-topk', type=int, default=100,
                        help='Top-k eigenvalues for large matrices (default: 100)')
    parser.add_argument('--use-louvain', action='store_true',
                        help='Use Louvain algorithm for large graphs (requires python-louvain)')
    parser.add_argument('--no-visuals', action='store_true',
                        help='Skip visualization generation (headless mode)')
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed for reproducibility')
    parser.add_argument('--save-history', action='store_true',
                        help='When running --self-test, append metrics to self_diagnostic/history.json')
    parser.add_argument('--check-convergence', action='store_true',
                        help='Check if recent self-test history indicates convergence (M_eff plateau)')
    parser.add_argument('--convergence-report', action='store_true',
                        help='Generate and print a convergence report based on history')
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('--self-test', action='store_true',
                        help='Run diagnostic on the program itself (recursive meta-analysis)')

    args = parser.parse_args()

    try:
        # Convergence-only actions (do not require --data)
        if args.check_convergence or args.convergence_report:
            hp = os.path.join(args.out, 'history.json')
            converged = check_convergence(history_file=hp)
            if args.convergence_report:
                report = generate_convergence_report(history_file=hp)
                print("\n" + "="*67)
                print(" RECURSIVE CONVERGENCE DIAGNOSTIC")
                print("="*67)
                print(json.dumps(report, indent=2))
                # Save report
                os.makedirs(args.out, exist_ok=True)
                with open(os.path.join(args.out, 'convergence_report.json'), 'w') as f:
                    json.dump(report, f, indent=2)
            # Exit code communicates status if check was requested
            if args.check_convergence:
                if converged:
                    print("\n✓ CODE OPTIMAL - Stop refactoring")
                    sys.exit(0)
                else:
                    print("\n⚡ Continue refactoring to reduce M_eff")
                    sys.exit(1)
        elif args.self_test:
            self_test(out_dir=args.out, save_history=args.save_history, history_path=os.path.join(args.out, 'history.json'))
        else:
            if not args.data:
                parser.error("--data is required unless using --self-test mode")
            run_unified_diagnostic(
                data_path=args.data,
                data_type=args.type,
                corr_method=args.corr_method,
                adj_threshold=args.adj_threshold,
                out_dir=args.out,
                compute_null=args.compute_null,
                n_permutations=args.n_permutations,
                eig_topk=args.eig_topk,
                use_louvain=args.use_louvain,
                skip_visuals=args.no_visuals,
                seed=args.seed
            )
    except FileNotFoundError:
        print(f"[Error] Input file not found: {args.data}")
    except ValueError as e:
        print(f"[Error] {e}")
    except Exception as e:
        print(f"[Critical Error] {e}")
