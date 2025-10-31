# Competition Template

Use this template for any new Kaggle/data science competition.

## Structure

```
competition_name/
├── README.md                # Competition overview
├── requirements.txt         # Python dependencies
├── notebooks/              # Jupyter notebooks for EDA
├── scripts/                # Python scripts for models/pipelines
├── docs/                   # Documentation and strategy
└── models/                 # Saved model checkpoints
```

## Quick Setup

```bash
# Copy this template
cp -r template/ your_competition_name/

# Update README.md with:
# - Competition name and goal
# - Evaluation metric
# - Deadline
# - Prize pool

# Add your work to appropriate folders
```

## Naming Convention

**Competitions folder naming:**
- `competition_name_year/` (lowercase, underscores)
- Examples: `nfl_big_data_bowl_2026/`, `titanic_2024/`, `house_prices_2025/`

**File naming:**
- Scripts: `{competition_prefix}_{purpose}.py`
- Notebooks: `{competition_prefix}_{analysis_type}.ipynb`
- Docs: `{TOPIC}.md`

## Integration with truth_distortion_unified.py

For any relational/network-based competition:

1. Create `{competition}_relational_analyzer.py` in `scripts/`
2. Use truth_distortion_unified.py to:
   - Compute M_eff (dimensional collapse)
   - Analyze relational topology (RFI)
   - Identify feature importance (collapse map)
   - Validate predictions (residue profile)

See `nfl_big_data_bowl_2026/` for reference implementation.
