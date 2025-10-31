# User Guide: How to Interpret Visualizations

**Dashboard Version:** Phase 5 (October 2025)  
**Audience:** Data scientists, researchers, system analysts  
**Purpose:** Understand diagnostic run visualizations and extract insights

---

## Table of Contents

1. [Overview](#overview)
2. [Topology Graph](#topology-graph)
3. [Collapse Map](#collapse-map)
4. [Lattice Phase Plane](#lattice-phase-plane)
5. [Comparison View](#comparison-view)
6. [Common Patterns & Insights](#common-patterns--insights)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The Integration Dashboard provides three primary visualization types to analyze diagnostic runs:

| Visualization | Purpose | Key Insights |
|--------------|---------|--------------|
| **Topology Graph** | Network structure of feature relationships | Communities, hubs, isolated nodes |
| **Collapse Map** | Feature importance ranking | Which features matter most |
| **Lattice Phase Plane** | System-level coherence positioning | Overall health and stability |

---

## Topology Graph

### What It Shows

The **Topology Graph** visualizes relationships between features in your dataset as a network. Each node represents a feature, and edges represent statistical dependencies or correlations.

### Visual Elements

**Nodes (Circles):**
- **Size:** Proportional to node degree (number of connections)
- **Color:** Community membership (features that cluster together)
- **Position:** Force-directed layout (strongly connected nodes are closer)

**Edges (Lines):**
- **Presence:** Statistical relationship exists between features
- **Weight:** Shown as edge thickness (if available)

**Labels:**
- Display for high-degree nodes (>5 connections)
- Show feature names or indices

### Interactive Controls

| Control | Action | Purpose |
|---------|--------|---------|
| **Click node** | Pin/unpin position | Freeze node for detailed inspection |
| **Drag node** | Reposition | Adjust layout for clarity |
| **Scroll wheel** | Zoom in/out | Focus on specific regions |
| **Drag background** | Pan view | Navigate large networks |
| **Search bar** | Filter by name | Quickly find specific features |
| **Community filter** | Highlight group | Isolate community for analysis |

### How to Interpret

#### 1. Hub Nodes (Large, Many Connections)
**What:** Features with high degree centrality  
**Meaning:** These features are statistically related to many others  
**Action:** Investigate these first—they're often key drivers or confounders

**Example:**
```
feature_18: Degree 6, Community 0
→ This feature connects to 6 others
→ Likely a core variable in your dataset
→ Changes here may cascade to connected features
```

#### 2. Communities (Color Groups)
**What:** Clusters of densely connected nodes  
**Meaning:** Features that vary together or share latent factors  
**Action:** Treat community members as related—they may represent different aspects of the same underlying phenomenon

**Example:**
```
Community 0 (Blue): feature_1, feature_12, feature_18
Community 1 (Orange): feature_6, feature_7, feature_11
→ Blue features likely measure similar concepts
→ Orange features form a separate module
```

#### 3. Isolated Nodes (Small, Few Connections)
**What:** Features with degree 0-1  
**Meaning:** Statistically independent from most others  
**Action:** May be noise, or genuinely independent signals worth isolating

**Example:**
```
feature_5: Degree 0
→ Not related to any other features
→ Could be measurement error OR a unique signal
```

#### 4. Bridge Nodes (Connect Communities)
**What:** Nodes with edges spanning multiple color groups  
**Meaning:** Features that mediate between subsystems  
**Action:** Critical for understanding cross-domain interactions

### Typical Patterns

| Pattern | Appearance | Interpretation |
|---------|------------|----------------|
| **Star topology** | One central hub, many spokes | Single dominant feature (potential confounder) |
| **Modular network** | Distinct color clusters | Multiple independent subsystems |
| **Hairball** | Dense, tangled mess | High multicollinearity, needs dimensionality reduction |
| **Sparse graph** | Many isolated nodes | Mostly independent features, low redundancy |

---

## Collapse Map

### What It Shows

The **Collapse Map** ranks features by their contribution to the system's effective dimensionality. It answers: "Which features matter most for capturing system behavior?"

### Visual Elements

**Horizontal Bars:**
- **Length:** Contribution percentage (longer = more important)
- **Color:** Collapse score (gradient from dark to bright)
- **Rank:** Position in list (#1 is most important)

**Metadata Cards:**
- **Total Dimensions (m_total):** Original number of features
- **Effective Dimensions (m_effective):** Reduced dimensionality after analysis
- **Collapse Ratio:** m_effective / m_total (lower = more redundancy)
- **M_eff (Li-Ji):** Alternative effective dimension estimate

### How to Interpret

#### 1. Top Features (Ranks #1-10)
**What:** Features with highest contribution percentages  
**Meaning:** These capture most of the system's variance  
**Action:** Focus your modeling and interpretation on these

**Example:**
```
#1 Feature 35: 11.06%
#2 Feature 32: 10.56%
#3 Feature 29: 10.36%
→ Top 3 features account for ~32% of effective behavior
→ These are your "signal" features
```

#### 2. Contribution Percentage
**What:** Each feature's share of effective dimensionality  
**Meaning:** Higher % = more unique information provided  
**Action:** Features with <1% contribution are candidates for removal

**Interpretation:**
- **>10%:** Core feature, essential for modeling
- **5-10%:** Significant contributor, keep in analysis
- **1-5%:** Moderate signal, consider in ensemble
- **<1%:** Noise or redundant, safe to drop

#### 3. Cumulative Contribution
**What:** Running total of contribution percentages  
**Meaning:** How much variance you capture with top N features  
**Action:** Use to select feature subset for dimensionality reduction

**Example:**
```
Top 5 features: 52% cumulative
Top 10 features: 78% cumulative
Top 20 features: 95% cumulative
→ Can capture 95% of behavior with just 20 features
```

#### 4. Collapse Ratio
**What:** m_effective / m_total ratio  
**Meaning:** Degree of redundancy in your dataset  

| Ratio | Interpretation | Action |
|-------|----------------|--------|
| **>0.8** | Low redundancy | Most features are unique, keep all |
| **0.5-0.8** | Moderate collapse | Standard dimensionality reduction helpful |
| **0.2-0.5** | High collapse | Strong redundancy, aggressive pruning possible |
| **<0.2** | Extreme collapse | Dataset has major collinearity issues |

**Example:**
```
m_total: 39 features
m_effective: 19.7
Collapse ratio: 0.505
→ Your 39 features behave like ~20 independent ones
→ ~50% of features are redundant information
```

### View Modes

**Bar Chart (Default):**
- Quick ranking visualization
- Easy to spot top contributors
- Good for presentations

**Table View:**
- Detailed numerical data
- Sortable columns
- Export-friendly format

### Filters & Controls

| Control | Purpose |
|---------|---------|
| **Show Top N** | Limit to top-ranking features |
| **Min Contribution** | Filter out low-impact features |
| **Search** | Find specific feature by name/index |
| **Export CSV** | Download data for external analysis |

---

## Lattice Phase Plane

### What It Shows

The **Lattice Phase Plane** positions each diagnostic run in a 2D space defined by:
- **X-axis:** RFI (Relational Field Index) - Relational coherence strength
- **Y-axis:** Collapse Ratio - Dimensional reduction degree

This creates a "map" of system states across all your analyses.

### Visual Elements

**Points (Circles):**
- Each point = one diagnostic run
- **Color:** Shape category (automatically detected)
- **Size:** Uniform for all runs
- **Position:** (RFI, Collapse Ratio) coordinates

**Background Regions:**
- **Truth Lattice:** High RFI, low collapse (structured, low-dimensional)
- **Irreducible Distortion:** High RFI, high collapse (structured but redundant)
- **Coherent Structure:** Low RFI, low collapse (complex, independent)
- **Chaotic Domain:** Low RFI, high collapse (noise, little signal)

**Legend:**
- Lists all shape categories detected
- Color-coded for quick reference

### How to Interpret

#### 1. RFI (X-Axis) - Relational Field Index

**Range:** Typically 0.0 to 3.0 (higher values possible)

| RFI Value | Meaning | Interpretation |
|-----------|---------|----------------|
| **0.0-0.5** | Weak relational structure | Features mostly independent |
| **0.5-1.0** | Moderate structure | Some clear patterns emerging |
| **1.0-2.0** | Strong structure | Well-defined relationships |
| **>2.0** | Very strong structure | Highly organized system |

**Example:**
```
Run A: RFI = 2.638
→ Very strong relational field
→ Features are highly interdependent
→ System exhibits clear organizational structure
```

#### 2. Collapse Ratio (Y-Axis)

**Range:** 0.0 to 1.0

| Ratio | Meaning | Interpretation |
|-------|---------|----------------|
| **0.0-0.3** | Low collapse | High effective dimensionality |
| **0.3-0.6** | Moderate collapse | Medium redundancy |
| **0.6-0.8** | High collapse | Significant redundancy |
| **0.8-1.0** | Extreme collapse | Nearly all information in few dims |

**Example:**
```
Run A: Collapse = 0.505
→ Moderate dimensional reduction
→ About half the features are redundant
→ System has meaningful structure without over-collapse
```

#### 3. Lattice Zones

**Truth Lattice (High RFI, Low Collapse):**
- **Best case scenario**
- Strong structure + high effective dimensionality
- System is organized but information-rich
- **Action:** This is your target state

**Irreducible Distortion (High RFI, High Collapse):**
- Strong structure but mostly redundant
- Few degrees of freedom despite organization
- May indicate over-fitting or measurement redundancy
- **Action:** Investigate why structure doesn't yield unique information

**Coherent Structure (Low RFI, Low Collapse):**
- Complex, independent features
- No strong relational field, but rich behavior
- Common in high-dimensional, diverse datasets
- **Action:** Consider clustering or embedding techniques

**Chaotic Domain (Low RFI, High Collapse):**
- **Worst case scenario**
- Little structure AND little unique information
- Mostly noise or measurement error
- **Action:** Data quality issues, consider re-collection

#### 4. Trajectories & Comparisons

**Comparing Multiple Runs:**
- Points close together → Similar system states
- Points far apart → Different regimes or datasets
- Trajectories (if time series) → System evolution

**Example:**
```
Run A (GDP data): RFI=0.0, Collapse=0.607 → Coherent Structure
Run B (Meal data): RFI=2.638, Collapse=0.505 → Truth Lattice
→ Meal data has stronger relational patterns
→ Meal data is better structured for analysis
```

### Interactive Features

| Action | Result |
|--------|--------|
| **Hover point** | See run details (ID, shape, metrics) |
| **Click point** | Navigate to run detail page |
| **Zoom** | Focus on dense regions |
| **Pan** | Explore different zones |

---

## Comparison View

### What It Shows

The **Comparison View** allows side-by-side analysis of 2+ diagnostic runs across all three visualization types.

### How to Use

**1. Select Runs:**
- From dashboard, check 2+ runs
- Click "Compare Selected" button
- Redirects to comparison page

**2. Navigate Tabs:**
- **📊 Metrics:** Table of run metadata
- **🌐 Topologies:** Side-by-side network graphs
- **📉 Collapse Maps:** Side-by-side feature rankings

### How to Interpret

#### Metrics Tab
Compare basic properties:
- Status (completed/failed)
- Data paths
- Timestamps
- Duration
- Errors

**Use Case:** Quick sanity check before detailed comparison

#### Topologies Tab
**What to Look For:**
- **Network size:** More nodes/edges = more features/relationships
- **Community count:** More colors = more distinct subsystems
- **Density:** Hairball vs. sparse graph
- **Hub nodes:** Same features central across runs?

**Example Comparison:**
```
Run 1: 39 nodes, 36 edges, 3 communities
Run 2: 5 nodes, 5 edges, 1 community
→ Run 1 is much more complex
→ Run 2 may be simpler or missing relationships
```

#### Collapse Maps Tab
**What to Look For:**
- **Top features:** Are the same features important?
- **Contribution spread:** One run more evenly distributed?
- **Collapse ratio:** Which run has more redundancy?

**Example Comparison:**
```
Run 1 Top: Feature 35 (11%), Feature 32 (10%)
Run 2 Top: Feature 4 (24%), Feature 3 (21%)
→ Different features are important
→ Run 2 has higher concentration (24% vs 11%)
→ Datasets likely capture different phenomena
```

---

## Common Patterns & Insights

### Pattern 1: High RFI + Low Collapse = Ideal State

**Signature:**
- Lattice: Point in upper-left (Truth Lattice zone)
- Topology: Modular network with clear communities
- Collapse: Gradual contribution decrease (no single dominant feature)

**Meaning:** Dataset has strong, meaningful structure with rich, non-redundant information

**Action:** Proceed with confidence to modeling

---

### Pattern 2: Star Topology + High Top Feature Contribution

**Signature:**
- Topology: One massive hub node, many small spokes
- Collapse: #1 feature has >20% contribution
- Lattice: Likely high RFI, variable collapse

**Meaning:** One feature dominates everything (potential confounder)

**Action:** 
1. Investigate the hub feature (what is it?)
2. Consider removing it to see underlying structure
3. May be a "batch effect" or measurement artifact

---

### Pattern 3: Hairball Topology + High Collapse Ratio

**Signature:**
- Topology: Dense network, hard to see individual nodes
- Collapse: High collapse ratio (>0.7)
- Lattice: High RFI, high collapse (Irreducible Distortion)

**Meaning:** Features are highly correlated but mostly redundant

**Action:**
1. Apply PCA or factor analysis
2. Likely measuring the same latent variable repeatedly
3. Dimensionality reduction will help significantly

---

### Pattern 4: Sparse Graph + Low Collapse Ratio

**Signature:**
- Topology: Many isolated nodes, few edges
- Collapse: Low collapse ratio (<0.3)
- Lattice: Low RFI, low collapse (Coherent Structure)

**Meaning:** Features are mostly independent, high-dimensional behavior

**Action:**
1. May need more data to detect relationships
2. Or features genuinely capture different aspects
3. Good for ensemble methods (features are diverse)

---

### Pattern 5: Inconsistent Results Across Runs

**Signature:**
- Topology: Completely different network structures
- Collapse: Different top features
- Lattice: Points in different zones

**Meaning:** Datasets are fundamentally different OR analysis parameters need tuning

**Action:**
1. Verify data preprocessing is consistent
2. Check if datasets are from different populations
3. Ensure analysis parameters are appropriate for both

---

## Troubleshooting

### Issue: Empty Visualizations

**Symptoms:**
- "No topology data available"
- "No collapse map data"
- Blank lattice plane

**Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| Run failed | Check run status, see error message |
| Data too small | Need minimum ~5 features for topology |
| Analysis incomplete | Wait for run to finish processing |
| API error | Check backend logs, restart if needed |

---

### Issue: Topology Graph Is a Hairball

**Symptoms:**
- Can't see individual nodes
- Everything is connected
- No clear structure

**Solutions:**

1. **Adjust Force Parameters:**
   - Increase link distance (spread nodes apart)
   - Decrease charge strength (reduce repulsion)

2. **Filter by Community:**
   - Use community filter to isolate clusters
   - Analyze one module at a time

3. **Search for Specific Nodes:**
   - Use search bar to highlight features of interest
   - Pin important nodes to stabilize layout

4. **Data Preprocessing:**
   - Consider correlation threshold adjustment
   - Remove very high-degree nodes (potential confounders)

---

### Issue: All Features Have Similar Collapse Scores

**Symptoms:**
- Collapse map bars are all nearly the same height
- Contribution percentages evenly distributed

**Meaning:** Dataset has balanced information across features (not a bug!)

**Interpretation:**
- No single feature dominates
- May need all features for accurate modeling
- Dimensionality reduction will be less effective

---

### Issue: Lattice Points Clustered at (0, high)

**Symptoms:**
- All runs at RFI ≈ 0
- Collapse ratio 0.6-0.9
- Clustered in Chaotic Domain

**Causes:**
1. **Small datasets:** Not enough data for relationship detection
2. **Noisy measurements:** High measurement error
3. **Inappropriate analysis:** Algorithm tuned wrong

**Solutions:**
- Collect more data (need n >> m typically)
- Check data quality and preprocessing
- Adjust analysis parameters (correlation thresholds, etc.)

---

### Issue: Can't Compare Runs (Error Message)

**Symptoms:**
- "Unable to Compare Runs" error page
- Instructions to select 2+ runs

**Cause:** Fewer than 2 runs selected

**Solution:**
1. Return to dashboard
2. Check 2+ run checkboxes
3. Click "Compare Selected" button

---

## Best Practices

### 1. Start with Lattice View
- Get system-level overview first
- Identify which runs are in "good" zones
- Focus detailed analysis on promising runs

### 2. Use Topology to Understand Structure
- Identify hub features (potential confounders)
- Map out subsystems (communities)
- Check for expected relationships

### 3. Use Collapse Map for Feature Selection
- Rank features by importance
- Set cutoff (e.g., top 80% cumulative)
- Validate selected features with domain knowledge

### 4. Compare Runs to Validate
- Consistent patterns across runs → robust findings
- Inconsistent patterns → investigate differences
- Use comparison view for apples-to-apples analysis

### 5. Iterate Analysis
- Adjust parameters based on visualizations
- Remove confounders identified in topology
- Re-run to see cleaner structure

---

## Keyboard Shortcuts

| Key | Action | Context |
|-----|--------|---------|
| `⌘ K` | Create new run | Dashboard |
| `⌘ R` | Refresh data | Dashboard |
| `Esc` | Close modals | Anywhere |
| `←/→` | Navigate tabs | Comparison view |

---

## Export & Reporting

### Available Exports

1. **Collapse Map CSV:**
   - Click "Export CSV" in collapse map viewer
   - Includes: feature index, name, collapse score, contribution %

2. **Screenshots:**
   - Use browser screenshot tools
   - All visualizations are SVG (high quality)

3. **Run Data JSON:**
   - From run detail page
   - Click "Export JSON" button
   - Full diagnostic results

### Creating Reports

**Recommended Flow:**
1. Take screenshots of key visualizations
2. Export collapse map CSV for tables
3. Export JSON for reproducibility
4. Combine in document with interpretations

---

## Getting Help

**Questions about:**
- **Visualization bugs:** Check browser console, report with screenshot
- **Interpretation:** Refer to "Common Patterns" section above
- **Mathematical details:** See technical documentation
- **API issues:** Check backend logs (`dashboard/backend/backend.log`)

**Need More Details?**
- Technical docs: See `ARCHITECTURE.md` and `DATA_FLOW.md`
- Code: All visualizations in `dashboard/frontend/components/visualizations/`
- Theory: See `core/` directory for Relational Math framework

---

**User Guide Version:** 1.0  
**Last Updated:** October 30, 2025  
**Maintainer:** Dashboard Development Team

**End of User Guide**
