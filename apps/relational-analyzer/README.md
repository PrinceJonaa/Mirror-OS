# Relational Math Toolkit

Advanced mathematical framework for analyzing relational structures in data using truth/distortion theory. Includes core analysis tools and competition-specific implementations.

## 📁 Project Structure

```
relational_math/
├── README.md                          # This file
├── truth_distortion_unified.py        # � Core analysis engine
├── analyze.py                         # Quick analysis wrapper
├── list_datasets.py                   # Dataset utilities
│
├── competitions/                      # 🏆 Competition-specific work
│   ├── template/                      # Template for new competitions
│   │   └── README.md
│   ├── nfl_big_data_bowl_2026/       # NFL player movement prediction
│   │   ├── README.md
│   │   ├── requirements.txt
│   │   ├── notebooks/                 # Jupyter notebooks
│   │   ├── scripts/                   # Python scripts
│   │   ├── docs/                      # Documentation
│   │   └── models/                    # Saved models
│   └── [future_competitions]/
│
├── data/                              # 📊 Datasets
│   ├── nfl-big-data-bowl-2026-prediction/
│   ├── discipline_data_clean.csv
│   ├── gdp_data_clean.csv
│   └── [other_datasets]/
│
├── results/                           # 📈 Analysis outputs
│   ├── nfl_analysis/
│   ├── discipline_analysis/
│   └── [other_results]/
│       ├── unified_diagnostic.json
│       ├── summary.txt
│       ├── collapse_map.csv
│       └── truth_distortion_diagnostic.png
│
└── docs/                              # 📚 Core documentation
    ├── RM_Translation_Layer.md
    ├── Relational_Math_Chains.md
    ├── Relational_Math_Master_Chain.md
    └── TRUTH_DISTORTION_DIAGNOSTIC.md
```

## 🚀 Quick Start

### 1. List Available Datasets

```bash
python list_datasets.py
```

### 2. Run Analysis

```bash
python truth_distortion_unified.py --data data/YOUR_FILE.csv --type auto --out results/YOUR_ANALYSIS
```

### 3. View Results

Results saved in `results/YOUR_ANALYSIS/`:

- `unified_diagnostic.json` - Complete metrics
- `summary.txt` - Human-readable report
- `collapse_map.csv` - Feature importance rankings
- `truth_distortion_diagnostic.png` - Visualization

---

## 🏆 Competitions

### Active: NFL Big Data Bowl 2026

**Location:** `competitions/nfl_big_data_bowl_2026/`  
**Goal:** Predict player movement while ball is in air  
**Status:** Relational analysis complete, GNN model in progress  
**Key Insight:** Players are highly coupled (16.5% collapse ratio) → Use GNN

[See competition README →](competitions/nfl_big_data_bowl_2026/README.md)

### Start a New Competition

Use the template structure for any new Kaggle competition or data science project:

```bash
cp -r competitions/template competitions/your_competition_2026
```

[See template README →](competitions/template/README.md)

---

## 📊 Supported Data Types

- **Tabular** - Standard CSV with rows × columns
- **Correlation Matrix** - Pre-computed correlations
- **Adjacency Matrix** - Network/graph connections
- **Edge List** - Network edges (2-3 columns)

Auto-detection identifies the type automatically, or specify with `--type` flag.

## 🔍 What It Measures

### M_eff (Effective Dimensionality)

How much the data collapses from its nominal dimensions to effective dimensions. Low M_eff = high redundancy.

### RFI (Relational Field Index)

Topological coherence of the relational structure. Measures modularity, connectivity, and traversability.

### Collapse Map

Which features/variables drive dimensional reduction? What's redundant vs. essential?

### Residue Profile

Off-diagonal correlation strength. Measures systemic coupling vs. independence.

### Topological Shape

What's the structural archetype? (Modular blocks, Complete graph, Star, etc.)

---

## 📖 Key Metrics Explained

| Metric | Range | Interpretation |
|--------|-------|----------------|
| **Collapse Ratio** | 0-100% | % of dimensions that remain effective (lower = more collapse) |
| **M_eff** | 1 to N | Effective dimensions (1 = complete redundancy, N = full independence) |
| **RFI** | 0 to ∞ | Relational coherence (higher = more structured) |
| **Modularity Q** | 0 to 1 | Community structure strength (1 = perfect modules) |

### Decision Guide by Collapse Ratio

- **< 30%**: Highly coupled system → Use relational models (GNN, attention)
- **30-70%**: Moderate coupling → Mixed approach (features + relationships)
- **> 70%**: Weak coupling → Simple models suffice (linear, tree-based)

---

## 🎯 Example Workflows

### Analyze Competition Data

```bash
cd competitions/nfl_big_data_bowl_2026
python scripts/nfl_relational_analyzer.py
```

### Analyze School Discipline Data

```bash
# Full contextual analysis (50 dimensions)
python truth_distortion_unified.py \
  --data data/discipline_data_enriched.csv \
  --type tabular \
  --out results/discipline_full
```

## 🎯 Example Workflows

### Analyze School Discipline Data
```bash
# Full contextual analysis (50 dimensions)
python truth_distortion_unified.py \
  --data data/discipline_data_enriched.csv \
  --type tabular \
  --out results/discipline_full

# Just discipline metrics (7 dimensions)
python truth_distortion_unified.py \
  --data data/discipline_data_clean.csv \
  --type tabular \
  --out results/discipline_core
```

### Self-Diagnostic Mode

Analyze the diagnostic tool's own code structure:

```bash
python truth_distortion_unified.py --self-test --out results/self_diagnostic
```

### Check Convergence (for iterative refactoring)

```bash
python truth_distortion_unified.py --check-convergence --out results/self_diagnostic
```

---

## 🚀 Quick Start for New Competition

```bash
# 1. Copy template
cp -r competitions/template competitions/your_competition_2026

# 2. Add your data
mkdir data/your_competition_data

# 3. Run relational analysis
python truth_distortion_unified.py \
  --data data/your_competition_data/train.csv \
  --type auto \
  --out results/your_competition_analysis

# 4. Check collapse_ratio in results/summary.txt
# - If < 0.3: Build relational model (GNN)
# - If > 0.7: Use simple baseline

# 5. Build model based on insights
cd competitions/your_competition_2026
# Create your_{competition}_model.py based on collapse_map.csv
```

---

## 🛠️ Command Line Options

```bash
python truth_distortion_unified.py [OPTIONS]

Required (unless --self-test):
  --data PATH              Input CSV file path

Optional:
  --type TYPE              Data type: auto, tabular, corr, adj, edgelist
  --corr-method METHOD     Correlation: pearson, spearman, kendall
  --adj-threshold FLOAT    Threshold for adjacency (default: 0.7)
  --out DIR                Output directory (default: results/)
  --seed INT               Random seed for reproducibility
  --no-visuals             Skip visualization generation
  --compute-null           Compute permutation-based null model

Self-Diagnostic:
  --self-test              Analyze the program's own structure
  --save-history           Append metrics to history.json
  --check-convergence      Check if M_eff has plateaued
  --convergence-report     Generate convergence assessment
```

## 📚 Documentation

- `TRUTH_DISTORTION_DIAGNOSTIC.md` - Conceptual framework
- `Relational_Math_Master_Chain.md` - Mathematical foundations
- `RM_Translation_Layer.md` - Implementation details
- `data/README.md` - Data directory guide

## 🔄 Version

Current: **v2.2.5** (Intelligence Layer)

Features:
- Dimensional collapse analysis (M_eff)
- Relational topology (RFI)
- Collapse map (feature importance)
- Residue profile (coupling strength)
- Interpretation layer (narrative synthesis)
- Self-diagnostic mode (recursive analysis)
- Convergence detection (refactoring guide)

## 🎓 Example Results

From discipline data analysis:

**7-Dimension Analysis (Discipline Metrics Only):**

- M_eff: 1.22 / 7 (extreme collapse)
- All exclusion types are 96%+ correlated
- Conclusion: Track one composite metric

**50-Dimension Analysis (Full Context):**

- M_eff: 46.64 / 50 (maintains complexity)
- Grade level, demographics, school type add independent information
- Conclusion: Context drives variation, not exclusion severity

From NFL Big Data Bowl 2026 analysis:

**Player Movement Analysis:**

- M_eff: ~3.6 / 22 (16.5% collapse ratio - highly coupled)
- Top features: dist_to_ball (20.6%), speed_toward_ball (20.4%), speed (20.2%)
- Role modularity: 33.86% (moderate clustering)
- Decision: Build GNN model instead of independent trajectory predictors
- Impact: Expected 0.3-0.5 yards RMSE improvement

---

## 🤝 Contributing

When adding new competitions:

1. Use `competitions/template/` structure
2. Create `{competition}_relational_analyzer.py` to integrate truth_distortion_unified.py
3. Document insights in competition `README.md`
4. Keep data in `data/{competition_name}/`
5. Save results in `results/{competition_name}/`

---

## 🔗 Related Projects

- Core framework: `/core/` (Codices and theoretical foundation)
- Applications: `/applications/` (Real-world implementations)
- Research: `/research/` (Training and experiments)

---

Generated by Mirror-OS Truth ↔ Distortion Diagnostic Suite
