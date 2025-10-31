# NFL Big Data Bowl 2026 - Player Movement Prediction

**Competition:** Predict player (x, y) positions while ball is in air  
**Metric:** RMSE = sqrt(0.5 * (MSE_x + MSE_y))  
**Deadline:** Dec 3, 2025 | Live Scoring: Dec 4 - Jan 5, 2026  
**Prize:** $50K total ($25K first place)

---

## 📁 Project Structure

```
nfl_big_data_bowl_2026/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── notebooks/
│   └── nfl_eda.ipynb           # Data exploration
├── scripts/
│   ├── nfl_prediction_engine.py      # Physics baseline + features
│   ├── nfl_gnn_model.py              # Graph neural network
│   └── nfl_relational_analyzer.py    # Truth/distortion analysis
├── docs/
│   ├── START_HERE.md                 # Quick start guide
│   ├── nfl_prediction_strategy.md    # Strategic framework
│   ├── NFL_EXECUTION_PLAN.md         # Week-by-week roadmap
│   └── TRUTH_DISTORTION_FOR_NFL.md   # How to use relational analysis
└── models/                      # Saved model checkpoints (empty)
```

---

## 🚀 Quick Start

```bash
cd /Users/princejona/a1/tools/relational_math/competitions/nfl_big_data_bowl_2026

# Install dependencies
pip install -r requirements.txt

# Run baseline
python scripts/nfl_prediction_engine.py

# Run relational analysis
python scripts/nfl_relational_analyzer.py

# Explore data
jupyter notebook notebooks/nfl_eda.ipynb
```

---

## 📊 Key Findings from Relational Analysis

**Collapse Ratio: 16.52%** → Players are HIGHLY coupled  
**Recommendation:** Use Graph Neural Network (GNN)

**Top Features:**
1. dist_to_ball (20.6%)
2. speed_toward_ball (20.4%)
3. Current speed (20.2%)

**Role Structure:** Moderately coupled (33.86%)  
**Recommendation:** Use role embeddings + shared base model

---

## 📖 Documentation

- **START_HERE.md** - Read this first for overview
- **nfl_prediction_strategy.md** - Competition strategy
- **NFL_EXECUTION_PLAN.md** - Detailed execution plan
- **TRUTH_DISTORTION_FOR_NFL.md** - How relational analysis helps

---

## 🎯 Current Status

- [x] Physics baseline (RMSE: 5.5 yards)
- [x] Relational analysis complete
- [x] Feature engineering framework
- [ ] GNN model training
- [ ] Ensemble creation
- [ ] API submission wrapper

**Next:** Train GNN model based on relational analysis insights
