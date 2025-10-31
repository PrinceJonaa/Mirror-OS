# NFL Big Data Bowl 2026 - Prediction Competition 🏈⚡

## Quick Start

**New here?** Read this first: [`START_HERE.md`](START_HERE.md)

---

## 📁 Files Overview

### 🚀 Getting Started
- **`START_HERE.md`** - Complete setup and strategy guide
- **`README_NFL.md`** - Competition overview and relational approach
- **`NFL_EXECUTION_PLAN.md`** - Week-by-week implementation roadmap

### 🧠 Strategy & Analysis
- **`nfl_prediction_strategy.md`** - Strategic framework (4-lens analysis)
- **`TRUTH_DISTORTION_FOR_NFL.md`** - How to use relational analysis for edge

### 💻 Code
- **`nfl_prediction_engine.py`** - Physics baseline + feature engineering (✅ WORKS)
- **`nfl_relational_analyzer.py`** - Truth/distortion analysis integration (✅ WORKS)
- **`nfl_gnn_model.py`** - Graph neural network architecture
- **`nfl_eda.ipynb`** - Data exploration notebook

### 📦 Config
- **`requirements.txt`** - Python dependencies

---

## 🎯 Current Status

### ✅ Complete
- Physics baseline model (RMSE: 5.5 yards)
- Relational analysis framework
- Feature engineering pipeline
- Data profiling

### 📊 Key Insights from Analysis
- **Collapse Ratio:** 16.5% (VERY LOW - high player coupling)
- **Recommendation:** GNN essential, players highly coupled
- **Top Features:** dist_to_ball, speed_toward_ball, vx, vy
- **Role Structure:** Moderately coupled - use role embeddings + shared model

### 🔄 Next Steps
1. Train GNN model with relational features
2. Validate with residue profile
3. Create ensemble
4. Submit to Kaggle

---

## 🚀 Run Analysis

```bash
# 1. Explore data
jupyter notebook nfl_eda.ipynb

# 2. Test baseline
python nfl_prediction_engine.py

# 3. Run relational analysis
python nfl_relational_analyzer.py

# 4. Review results
cat ../results/nfl_analysis/relational_analysis.json
```

---

## 📈 Performance Targets

- **Baseline (Physics):** 5.5 yards RMSE ✅
- **Competitive (XGBoost):** 2.0 yards RMSE
- **Advanced (GNN):** 1.0-1.5 yards RMSE
- **Winning (Ensemble):** 0.8-1.2 yards RMSE

---

## 🏆 Competition Details

- **Deadline:** December 3, 2025
- **Live Phase:** December 4 - January 5, 2026
- **Prize:** $50,000 total
- **Metric:** RMSE on (x, y) coordinates

---

## 📚 Learn More

Read the docs in order:
1. `START_HERE.md` - Overview & setup
2. `nfl_prediction_strategy.md` - Strategic framework
3. `TRUTH_DISTORTION_FOR_NFL.md` - Relational analysis guide
4. `NFL_EXECUTION_PLAN.md` - Implementation roadmap

---

**Ready to win!** 🏆
