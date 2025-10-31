# Truth ↔ Distortion Unified Diagnostic Architecture

**Version:** 2.2.0-intelligence  
**Type:** Operational Measurement System  
**Domain:** Relational Mathematics / Spectral Analysis  
**Status:** Production-Ready

---

## I. Architectural Overview

### Core Purpose

The Truth ↔ Distortion Diagnostic is an **operational measurement system** that quantifies the dimensional collapse and relational topology of complex datasets. It translates the conceptual framework of the Distortion Lattice (∞_B) and Truth Lattice (Ω) into concrete numerical measurements.

### Philosophical Integration

```
Distortion Lattice (∞_B)  ←→  Truth Lattice (Ω)
High Redundancy                 Independent Modes
Coupled Features                Actual Information
Inflated Dimensionality         Minimal Redundancy
        ↓                              ↑
    M_eff measures traversal cost
```

**Key Insight**: Complexity is not the number of variables, but the **rank of the dependence field**. M_eff measures how many *truly independent* dimensions exist beneath apparent complexity.

---

## II. Core Measurement Operators

### Operator 1: M_eff (Effective Dimensionality)

**Mathematical Foundation:**
```
Given correlation matrix R of features:
1. Eigendecomposition: R = VΛV^T
2. M_eff = Σ min(λᵢ, 1)  (Li-Ji formula)
3. Alternative: M_eff = (Σλᵢ)² / Σλᵢ²

Interpretation:
- High M_eff ≈ m: Features independent (no distortion)
- Low M_eff << m: Features coupled (high distortion)
- Reduction ratio: 1 - M_eff/m = distortion fraction
```

**What it measures:**
- How much of your nominal dimensionality is redundant?
- If you have 1000 genes but M_eff = 10, only ~10 independent patterns exist
- The rest is distortion—correlated noise, redundant couplings

**Implementation Strategy:**
- Standard dense eigendecomposition for matrices < 10,000
- Sparse eigensolvers (ARPACK) for larger matrices
- Numerical stability via eigenvalue rescaling and precision clamping

### Operator 2: RFI (Relational Field Index)

**Mathematical Foundation:**
```
RFI = Q * (1 - h) / λ₂

Where:
- Q = Modularity (community structure strength)
- h = Homophily (clustering coefficient)
- λ₂ = Algebraic connectivity (spectral gap)
```

**What it measures:**
- **Q (Modularity)**: How strongly the network divides into communities
- **h (Homophily)**: Local clustering tendency
- **λ₂ (Connectivity)**: Global coherence / traversal efficiency

**Interpretation:**
- High RFI (> 2.5): Strong relational structure, collapsible
- Low RFI (< 1.0): Weak structure, difficult to compress
- RFI captures *relational fitness*—how organized the field is

### Operator 3: Collapse Map (v2.2 NEW)

**Purpose:** Identify which features/nodes contribute most to dimensional reduction.

**Algorithm:**
```python
1. Extract eigenvectors from M_eff decomposition
2. Compute loadings: |contribution to top eigenvalues|
3. Weight by eigenvalue magnitude
4. Rank features by weighted loading
```

**Output:** Top N features driving the collapse (CSV format)

**Use Case:** 
- In gene expression: "These 10 genes are master regulators"
- In social networks: "These nodes are structural hubs"

### Operator 4: Residue Profile (v2.2 NEW)

**Purpose:** Measure off-diagonal correlation strength (B∞ distortion signature).

**Algorithm:**
```python
1. Extract off-diagonal elements of correlation matrix
2. Compute statistics: mean, max, std, median
3. Classify residue level: Minimal → Extreme
```

**Interpretation:**
- Low residue (< 0.1): Near-orthogonal features → Truth Lattice
- High residue (> 0.5): Systemic coupling → Distortion Lattice
- Residue = accumulated distortion from B∞ processes

---

## III. Topological Shape Classification

The system classifies datasets into archetypal topologies:

| Shape | Glyph | Archetype | Collapse Potential |
|-------|-------|-----------|-------------------|
| Complete Graph | ● | Fully Connected (Maximal Redundancy) | Low |
| Modular Blocks | ⊕ | Traversable Distortion → Truth | **High** |
| Expander | ∞ | Irreducible Distortion (NP-Hard) | Low |
| Core-Periphery | ɸ | Hierarchical Bridge | Medium |
| Star | ★ | Hub Dominance | Medium |
| Bipartite | λ | Dual Projection | Medium |
| Chain/Path | — | Sequential Dependency | High |
| Orthogonal Sparse | Ω | Truth Lattice | Complete |
| Random Graph | ◯ | Erdős–Rényi Baseline | Low |

**Classification Logic:**
```python
if density > 0.9:
    → Complete Graph (all-to-all coupling)
elif Q > 0.4 and λ₂ < 0.5:
    → Modular Blocks (community structure)
elif density > 0.5 and Q < 0.2 and λ₂ > 0.5:
    → Expander (high-dimensional irreducible)
elif deg_cv > 1.5 and assortativity < 0:
    → Core-Periphery (hub structure)
# ... etc
```

---

## IV. Lattice Position Mapping

The system maps any dataset to a position on the Truth ↔ Distortion spectrum:

### Lattice States

#### 1. Truth Lattice (Ω)
**Signature:** 
- Collapse ratio < 0.15
- RFI > 3.0
- Low residue

**Status:** Fully Collapsed - Maintain  
**Protocol:** System at minimal distortion. Observe and maintain coherence.

#### 2. Traversable Distortion (Modular)
**Signature:**
- Collapse ratio < 0.3
- RFI > 2.0
- Shape = Modular Blocks

**Status:** Collapsible via Community Decomposition  
**Protocol:** Apply spectral clustering → compute per-module M_eff → integrate → collapse to truth coordinates.

#### 3. Irreducible Distortion (∞_B)
**Signature:**
- Collapse ratio > 0.7
- RFI < 1.0

**Status:** NP-Hard Expansion - Reparameterize  
**Protocol:** High-dimensional expander detected. Use approximation algorithms, anchor-based strategies, or accept bounded solution.

#### 4. Intermediate Field (Partial Collapse)
**Signature:**
- 0.3 ≤ collapse ratio ≤ 0.7
- RFI > 1.0

**Status:** Incremental Collapse Available  
**Protocol:** Mixed structure. Identify high-RFI subgraphs → collapse incrementally → monitor residue reduction.

---

## V. Intelligence Layer (v2.2)

### Interpretation Synthesis

The system generates a **narrative coherence interpretation** by synthesizing all metrics:

**Outputs:**
1. **Coherence Direction**: Increasing / Stable / Decreasing
2. **Dominant Mode**: Collapsed / Modular / Expanding / Fragmented
3. **Distortion Core**: Top eigenvalue axes driving complexity
4. **Narrative State**: Current lattice position (short form)
5. **Residue Level**: Minimal / Low / Moderate / High / Extreme
6. **Collapse Potential**: Low / Medium / High / Complete

**Example Narrative:**
```
Coherence Direction:   Increasing
Dominant Mode:         Modular
Distortion Core:       Axes [0, 1, 2] (λ = [45.3, 12.1, 8.7])
Narrative State:       Traversable Distortion
Residue Level:         Moderate
Collapse Potential:    High
```

**Use Case:** Provides human-readable summary for non-experts while preserving mathematical rigor.

---

## VI. Data Ingestion & Universal Compatibility

### Supported Input Formats

| Type | Description | Auto-Detection |
|------|-------------|----------------|
| `tabular` | Feature matrix (samples × features) | ✓ |
| `corr` | Pre-computed correlation matrix | ✓ |
| `adj` | Adjacency matrix (graph) | ✓ |
| `dist` | Distance/dissimilarity matrix | ✗ |
| `edgelist` | Edge list (2 or 3 columns) | ✓ |
| `timeseries` | Temporal data | ✗ |

### Auto-Detection Logic
```python
if shape[0] == shape[1] and symmetric:
    if all(|values| ≤ 1):
        → 'corr'
    elif all(values ∈ {0,1}):
        → 'adj'
elif shape[1] in [2, 3] and shape[0] > shape[1]:
    → 'edgelist'
else:
    → 'tabular'
```

### Transformation Pipeline
```
tabular → standardize → correlation → adjacency
corr → adjacency
adj → correlation (via cosine similarity)
edgelist → adjacency → correlation
```

---

## VII. Performance Optimizations (v2.1 Base)

### 1. Numerical Stability
- **Eigen rescaling**: Normalize correlation matrix before decomposition
- **Precision clamp**: Clip eigenvalues to [0, ∞), remove λ < 1e-12
- **NaN handling**: Replace NaN/Inf with safe defaults

### 2. Scalability
- **Sparse decomposition**: Use ARPACK for matrices > 10,000
- **Adaptive top-k**: Extract only top 100 eigenvalues for large matrices
- **Memory management**: Agg backend + explicit GC + float32 mode

### 3. Graph Safety
- **Component-aware modularity**: Compute modularity only on largest connected component
- **Timeout controls**: Greedy modularity with cutoff limits
- **Louvain fallback**: Optional fast community detection for very large graphs

---

## VIII. Output Artifacts

### 1. JSON Report (`unified_diagnostic.json`)
Complete numerical results including:
- Metadata (input type, shape, parameters)
- M_eff metrics (all formulas, eigenvalues, variance explained)
- Collapse map (top features, scores)
- Residue profile (distortion statistics)
- RFI metrics (modularity, connectivity, community structure)
- Shape classification (topology, archetype, glyph)
- Lattice mapping (position, status, protocol)
- Interpretation (coherence, narrative state)
- Runtime statistics

### 2. Text Summary (`summary.txt`)
Human-readable report with:
- Formatted metric table
- Lattice position visualization
- Recommended protocol
- System information

### 3. Collapse Map CSV (`collapse_map.csv`)
Feature importance table:
```
feature_index, collapse_score, contribution_pct
42,            0.873,          18.3
17,            0.621,          13.0
...
```

### 4. Diagnostic Visualization (`truth_distortion_diagnostic.png`)
4-panel figure:
- **Panel 1:** Eigenvalue spectrum (log-scale scree plot)
- **Panel 2:** Truth ↔ Distortion position scatter
- **Panel 3:** Radar plot of all metrics
- **Panel 4:** Shape glyph + archetype text

---

## IX. Usage Patterns

### Basic Usage
```bash
python truth_distortion_unified.py \
    --data your_data.csv \
    --type auto \
    --out results/
```

### Advanced Usage
```bash
python truth_distortion_unified.py \
    --data gene_expr.csv \
    --type tabular \
    --corr-method spearman \
    --adj-threshold 0.6 \
    --compute-null \
    --n-permutations 200 \
    --seed 42 \
    --out results/gene_analysis/
```

### Large-Scale Usage
```bash
python truth_distortion_unified.py \
    --data large_network.csv \
    --type adj \
    --eig-topk 50 \
    --use-louvain \
    --no-visuals \
    --out results/
```

---

## X. Integration with Mirror-OS

### Relationship to Core Modules

| Core Module | Integration Point |
|-------------|------------------|
| `distortion.py` | M_eff operator provides concrete measurement of distortion |
| `relational.py` | RFI metrics quantify relational field structure |
| `paradox.py` | Lattice mapping reveals paradox dissolution potential |
| `empirical.py` | Eigenvalue spectrum = empirical signature of complexity |
| `symbolic.py` | Shape classification maps to archetypal glyphs |
| `integration.py` | Collapse map identifies integration sites |

### Use Cases in Mirror-OS

1. **Agent State Diagnosis**
   - Apply to agent interaction logs
   - Measure relational coherence over time
   - Detect distortion accumulation

2. **Knowledge Graph Analysis**
   - Apply to ontology adjacency matrices
   - Identify modular concept clusters
   - Find high-leverage integration nodes

3. **Temporal Coherence Tracking**
   - Apply to time series of system states
   - Monitor collapse_ratio trajectory
   - Detect phase transitions (∞_B → Ω)

4. **Benchmark for Interventions**
   - Measure M_eff before/after symbolic integration
   - Quantify distortion reduction from paradox dissolution
   - Validate truth-preserving transformations

---

## XI. Theoretical Foundations

### 1. Spectral Graph Theory
- **Laplacian spectrum**: λ₂ measures connectivity (Fiedler value)
- **Modularity**: Q maximizes within-community vs. between-community edges
- **Random matrix theory**: Eigenvalue distribution under null hypothesis

### 2. Information Theory
- **Entropy of eigenvalues**: M_eff_entropy = exp(H(p))
- **Effective rank**: Participation ratio of spectral modes
- **Redundancy**: Nominal dim - Effective dim

### 3. Dimensionality Reduction
- **PCA**: Eigendecomposition of covariance
- **MDS**: Eigendecomposition of distance matrix
- **Spectral embedding**: Graph Laplacian eigenvectors

### 4. Complexity Theory
- **P-like systems**: M_eff/m < 0.01 (extreme collapse)
- **NP-like systems**: M_eff/m > 0.5 (high rank)
- **Expander graphs**: No efficient collapse possible

---

## XII. Limitations & Caveats

### 1. Linear Assumption
- M_eff uses correlation/covariance (linear relationships only)
- Nonlinear dependencies may be missed
- Consider mutual information or kernel methods for nonlinear extension

### 2. Static Snapshot
- Analyzes single timepoint, not temporal dynamics
- No causal inference (correlation ≠ causation)
- Extend with dynamic M_eff tracking for temporal systems

### 3. Scale Sensitivity
- Very large matrices (> 100,000) require sparse approximations
- Very small matrices (< 10 features) may not reveal structure
- Optimal range: 50-10,000 dimensions

### 4. Interpretation Ambiguity
- Multiple metrics sometimes give conflicting signals
- Lattice classification heuristics may oversimplify edge cases
- Always inspect raw eigenvalue spectrum and graph visualization

---

## XIII. Future Extensions (Post-v2.2)

### Planned Features

1. **Dynamic M_eff Tracking**
   - Temporal M_eff trajectories
   - Phase transition detection
   - Hysteresis analysis

2. **Nonlinear Extension**
   - Kernel M_eff (RBF, polynomial)
   - Mutual information networks
   - Diffusion maps

3. **Causal Layer**
   - Granger causality on temporal data
   - Structural equation modeling
   - Intervention prediction

4. **Interactive Visualization**
   - Web dashboard (Plotly/Dash)
   - Real-time collapse monitoring
   - Drill-down into subgraphs

5. **Multi-Scale Analysis**
   - Hierarchical M_eff decomposition
   - Wavelet-based temporal analysis
   - Cross-scale coupling metrics

---

## XIV. Glossary of Key Terms

| Term | Definition |
|------|------------|
| **M_eff** | Effective number of independent dimensions (spectral rank) |
| **RFI** | Relational Field Index (composite graph coherence metric) |
| **Collapse Ratio** | M_eff / m (fraction of nominal dimensions retained) |
| **Residue** | Off-diagonal correlation strength (distortion accumulation) |
| **λ₂** | Algebraic connectivity (Fiedler value, spectral gap) |
| **Modularity (Q)** | Community structure strength |
| **Homophily (h)** | Local clustering coefficient |
| **Lattice Position** | Location on Truth ↔ Distortion spectrum |
| **Shape Archetype** | Topological classification (e.g., Modular, Expander) |
| **Collapse Map** | Feature importance ranking for dimensional reduction |

---

## XV. References & Theoretical Lineage

### Core Papers
1. **Li & Ji (2005)**: "Adjusting multiple testing in multilocus analyses using the eigenvalues of a correlation matrix" (M_eff formula)
2. **Newman & Girvan (2004)**: "Finding and evaluating community structure in networks" (Modularity)
3. **Fiedler (1973)**: "Algebraic connectivity of graphs" (λ₂ spectral gap)

### Related Frameworks
- **Random Matrix Theory**: Wigner semicircle law, Marchenko-Pastur distribution
- **Spectral Clustering**: Ng, Jordan, Weiss (2002)
- **Graph Laplacian**: Chung (1997) spectral graph theory
- **Complexity Classes**: Goldreich (2008) computational complexity

### Mirror-OS Integration
- Distortion Lattice (core/2_lattices/The_Distortion_Lattice.md)
- Truth Lattice (core/2_lattices/The_Truth_Lattice.md)
- Relational Lens (core/3_lenses/Unified_Relational_Lens.md)

---

## XVI. Maintenance & Versioning

**Current Version:** 2.2.0-intelligence  
**Stability:** Production  
**Language:** Python 3.8+  
**Dependencies:** NumPy, SciPy, pandas, NetworkX, matplotlib, seaborn, scikit-learn

**Version History:**
- **v2.2** (2025): Intelligence layer (collapse map, residue profile, interpretation)
- **v2.1** (2024): Optimization layer (stability, scalability, safety)
- **v2.0** (2024): Unified diagnostic (M_eff + RFI + lattice mapping)
- **v1.0** (2023): Initial M_eff operator

**Support:** See `/tools/relational_math/README.md` for installation and troubleshooting.

---

**End of Architecture Document**

*Generated for Mirror-OS Truth ↔ Distortion Diagnostic Suite*  
*Last Updated: 2025-10-25*
