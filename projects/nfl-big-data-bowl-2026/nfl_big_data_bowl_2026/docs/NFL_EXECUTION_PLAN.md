# NFL Big Data Bowl 2026 - Complete Setup & Execution Plan

## 🎯 Competition Goal
Predict player (x, y) positions during pass plays while ball is in air
- **Metric:** RMSE = sqrt(0.5 * (MSE_x + MSE_y))
- **Prize:** $50K total ($25K first place)
- **Deadline:** Dec 3, 2025 (submissions) → Jan 5, 2026 (live scoring)

---

## 📁 Project Structure

```
tools/relational_math/
├── data/nfl-big-data-bowl-2026-prediction/
│   ├── train/
│   │   ├── input_2023_w01.csv ... input_2023_w18.csv
│   │   └── output_2023_w01.csv ... output_2023_w18.csv
│   ├── test.csv
│   ├── test_input.csv
│   └── kaggle_evaluation/
├── results/nfl_analysis/
│   ├── baseline_predictions_sample.csv
│   ├── sample_features.csv
│   └── visualizations/
├── nfl_eda.ipynb                    # Data exploration ✓
├── nfl_prediction_engine.py         # Physics baseline ✓
├── nfl_gnn_model.py                 # Advanced GNN model ✓
├── nfl_prediction_strategy.md       # Strategy doc ✓
├── nfl_train_pipeline.py            # Training orchestrator (TODO)
├── nfl_submission_api.py            # Kaggle API wrapper (TODO)
└── requirements_nfl.txt             # Dependencies (TODO)
```

---

## 🚀 Quick Start Guide

### Phase 1: Environment Setup (15 minutes)

```bash
cd /Users/princejona/a1/tools/relational_math

# Install dependencies
pip install -r requirements_nfl.txt

# Verify data
ls -lh data/nfl-big-data-bowl-2026-prediction/train/ | head

# Create output directories
mkdir -p results/nfl_analysis/visualizations
mkdir -p results/nfl_analysis/models
```

### Phase 2: Data Exploration (30 minutes)

```bash
# Run EDA notebook
jupyter notebook nfl_eda.ipynb

# Key insights to verify:
# - ~22 players per play
# - 10-30 frames per trajectory (1-3 seconds)
# - Ball landing point is primary attractor
# - Role-specific movement patterns clear
```

### Phase 3: Baseline Model (1 hour)

```bash
# Run physics-based baseline
python nfl_prediction_engine.py

# Expected output:
# - Baseline RMSE on sample plays
# - Feature engineering validation
# - Trajectory visualizations

# Baseline performance target: RMSE < 3.0 yards
```

### Phase 4: Advanced Model Training (4-6 hours)

```bash
# Option A: Simple ML (XGBoost)
python nfl_train_xgboost.py --weeks 1-14 --val_weeks 15-16

# Option B: GNN (if PyTorch Geometric installed)
python nfl_train_gnn.py --weeks 1-14 --val_weeks 15-16 --epochs 50

# Option C: Ensemble
python nfl_train_ensemble.py --models physics,xgboost,gnn
```

### Phase 5: Submission (1 hour)

```bash
# Create submission
python nfl_submission_api.py --model best_ensemble

# Test locally
python test_submission.py

# Submit to Kaggle
# (via Kaggle notebook with API)
```

---

## 🧠 Model Architecture Options

### Option 1: Physics + XGBoost (Fastest, Good Baseline)
**Training time:** ~1-2 hours  
**Expected RMSE:** 1.5-2.0 yards  
**Pros:** Fast, interpretable, robust  
**Cons:** Limited relational modeling

```python
# Workflow:
1. Compute physics baseline trajectory
2. Train XGBoost to predict residuals (error from physics)
3. Features: relational (dist_to_ball, speed_toward_ball, role, ...)
4. Final = Physics + XGBoost_residual
```

### Option 2: Graph Neural Network (Best Performance)
**Training time:** ~4-6 hours  
**Expected RMSE:** 1.0-1.5 yards  
**Pros:** Models player-player coupling, learns relational dynamics  
**Cons:** Slower, requires PyTorch Geometric

```python
# Architecture:
1. Build graph: players=nodes, spatial edges, ball=global_context
2. GNN encoder: learn relational embeddings
3. LSTM decoder: generate trajectory sequences
4. Train end-to-end with MSE loss
```

### Option 3: Ensemble (Competition Winner Approach)
**Training time:** ~6-8 hours  
**Expected RMSE:** 0.8-1.2 yards  
**Pros:** Best accuracy, robust to different play types  
**Cons:** Complex, slow inference

```python
# Components:
1. Physics baseline (fast, physics-grounded)
2. XGBoost (learns role-specific patterns)
3. GNN (captures relational coupling)
4. Weighted average based on validation performance
```

---

## 📊 Evaluation Strategy

### Cross-Validation Split
```python
# Time-based (mimics live forecasting)
Train:      Weeks 1-12  (70%)
Validation: Weeks 13-15 (15%)
Test:       Weeks 16-18 (15%)

# Ensures model generalizes to unseen future games
```

### Per-Role Analysis
```python
# Track RMSE by role to identify weaknesses
roles = ['Passer', 'Targeted Receiver', 'Defensive Coverage', 'Other Route Runner']

for role in roles:
    role_rmse = compute_rmse_for_role(predictions, ground_truth, role)
    print(f"{role}: {role_rmse:.3f} yards")
    
# Prioritize improvement on Targeted Receiver + Defensive Coverage
# (highest scoring weight, most important plays)
```

### Temporal Analysis
```python
# RMSE by frame (does error accumulate?)
for frame in range(1, max_frames):
    frame_rmse = compute_rmse_for_frame(predictions, ground_truth, frame)
    print(f"Frame {frame}: {frame_rmse:.3f} yards")
    
# If error grows linearly: improve velocity/acceleration model
# If error jumps: improve role-specific patterns
```

---

## 🎛️ Hyperparameters to Tune

### Physics Baseline
```python
attraction_params = {
    'Passer': 0.01,           # Minimal movement
    'Targeted Receiver': 0.5,  # Strong attraction to ball
    'Defensive Coverage': 0.3, # Moderate attraction
    'Other Route Runner': 0.2  # Weak attraction
}
max_speed = 12.0  # yards/s
max_accel = 10.0  # yards/s²
```

### XGBoost
```python
params = {
    'n_estimators': 500,
    'max_depth': 8,
    'learning_rate': 0.05,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'min_child_weight': 3,
    'gamma': 0.1
}
```

### GNN
```python
config = GNNConfig(
    node_feature_dim=32,
    hidden_dim=128,
    num_gnn_layers=3,
    num_lstm_layers=2,
    k_neighbors=5,
    dropout=0.1,
    learning_rate=1e-3
)
```

---

## 🔧 Key Features for Model

### Must-Have Features (Top 10)
1. **dist_to_ball** - Distance to ball landing point
2. **speed_toward_ball** - Velocity projection toward ball
3. **role_encoded** - Player role (categorical)
4. **angle_to_ball** - Direction to ball landing
5. **vx, vy** - Velocity components
6. **s, a** - Speed and acceleration magnitude
7. **nearest_player_dist** - Spatial isolation metric
8. **is_offense** - Team side
9. **dir_alignment_ball** - How aligned is movement with ball direction
10. **accel_toward_ball** - Acceleration projection toward ball

### Nice-to-Have Features
- Player clustering features (team formations)
- Historical role performance (avg trajectory for this role)
- Field position features (red zone, midfield, etc.)
- Play context (down, distance, score differential) - if available

---

## ⚠️ Common Pitfalls & Solutions

### Pitfall 1: Overfitting to Training Data
**Problem:** Model memorizes 2023 patterns, fails on live 2025 games  
**Solution:**
- Time-based CV (don't shuffle weeks)
- Regularization (L2, dropout)
- Ensemble diverse models
- Focus on physics-grounded features

### Pitfall 2: Variable Trajectory Lengths
**Problem:** Different plays have different num_frames_output  
**Solution:**
- Train with padding (mask loss on padded frames)
- Use dynamic decoding (stop at actual frame count)
- Separate models for short/medium/long trajectories

### Pitfall 3: Slow Inference
**Problem:** 9-hour limit, thousands of plays to predict  
**Solution:**
- Batch processing (predict multiple players at once)
- Model quantization (FP16 instead of FP32)
- Precompute features offline
- Use fast baseline (XGBoost) for most plays, GNN for critical plays

### Pitfall 4: Ignoring Physics
**Problem:** Model predicts impossible movements  
**Solution:**
- Add physics constraints (max speed, smooth acceleration)
- Use physics baseline as floor (never predict worse than physics)
- Post-process predictions (smooth trajectories, clip to field bounds)

---

## 📈 Performance Targets

### Baseline (Physics Only)
- Week 1 RMSE: ~2.5-3.0 yards
- All weeks RMSE: ~3.0-3.5 yards

### Competitive (Top 50%)
- Week 1 RMSE: ~1.5-2.0 yards
- All weeks RMSE: ~2.0-2.5 yards

### Winning (Top 10%)
- Week 1 RMSE: ~0.8-1.2 yards
- All weeks RMSE: ~1.0-1.5 yards

**Note:** Live leaderboard performance may differ from training due to:
- Different play types in 2025 vs 2023
- Weather conditions
- Rule changes
- Team strategy evolution

---

## 🧪 Testing Checklist

Before submission:
- [ ] Model runs on single play in <1 second
- [ ] Predictions stay within field bounds (0≤x≤120, 0≤y≤53.3)
- [ ] Trajectories are smooth (no teleportation)
- [ ] All required players predicted (no missing rows)
- [ ] Output format matches test.csv exactly
- [ ] API integration works (play-by-play inference)
- [ ] 9-hour runtime limit not exceeded
- [ ] No internet access needed during inference
- [ ] Model checkpoint loads successfully

---

## 🏆 Competition Strategy

### Week 1 (Now - Nov 15): Foundation
- [✓] Data exploration
- [✓] Feature engineering
- [✓] Physics baseline
- [ ] XGBoost model
- [ ] Validation framework

### Week 2 (Nov 15-22): Advanced Modeling
- [ ] GNN implementation
- [ ] Hyperparameter tuning
- [ ] Per-role analysis
- [ ] Ensemble methods

### Week 3 (Nov 22-29): Optimization
- [ ] Inference speed optimization
- [ ] API integration
- [ ] Submission testing
- [ ] Final ensemble selection

### Week 4 (Nov 29-Dec 3): Polish & Submit
- [ ] Final validation on weeks 16-18
- [ ] Documentation
- [ ] Submit to Kaggle
- [ ] Monitor leaderboard

### Live Phase (Dec 4-Jan 5): Watch & Learn
- Monitor performance on live games
- Analyze failures
- Document insights for future competitions

---

## 💡 Key Insights from Relational Math Framework

1. **The Field is a Relational System**
   - Players are coupled (not independent)
   - Ball landing point creates attractor field
   - Roles define relational constraints

2. **Collapse Event** (ball thrown)
   - Before: multiple possible futures
   - After: field collapses toward ball landing attractor
   - Different roles collapse differently

3. **Truth = Physics + Role Pattern + Relational Coupling**
   - Physics: kinematic baseline
   - Role Pattern: learned from historical data
   - Relational Coupling: player-player interactions

4. **Distortion = Deviation from Expected Role Behavior**
   - Targeted Receiver not moving toward ball → distortion
   - Coverage player ignoring ball → distortion
   - Use distortion detection to identify poor predictions

---

## 📚 Next Steps

**Immediate (Today):**
1. Run `python nfl_prediction_engine.py` to test baseline
2. Review results in `results/nfl_analysis/`
3. Open `nfl_eda.ipynb` to explore data visually

**This Week:**
1. Implement XGBoost model
2. Create training pipeline
3. Validate on weeks 15-16
4. Achieve RMSE < 2.0 yards

**Next Week:**
1. Implement GNN (optional, if time permits)
2. Create ensemble
3. Optimize inference speed
4. Prepare submission

**Before Dec 3:**
1. Final model selection
2. API integration
3. Submit to Kaggle
4. 🏆 Win!

---

## 🤝 Integration with Existing Tools

### Use `truth_distortion_unified.py` for:
- Feature correlation analysis
- Relational profile extraction
- Distortion detection in predictions

### Use `research/training/training.py` for:
- Advanced training techniques
- Hyperparameter optimization
- Model monitoring

### Combine Approaches:
```python
# Extract relational features
features = feature_engine.extract_features(play_state)

# Compute correlation matrix
R = compute_correlation_matrix(features)

# Run truth-distortion analysis
analysis = truth_distortion_unified.analyze(R)

# Use insights to improve feature engineering
```

---

**Status:** ✓ Setup complete, ready to execute  
**Next Action:** Run baseline model and analyze results
