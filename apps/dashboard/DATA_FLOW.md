# Data Flow Architecture: Dashboard System

**Document Version:** 1.0  
**Last Updated:** October 30, 2025  
**Purpose:** Comprehensive data flow from script execution through visualization

---

## System Overview

```
┌─────────────┐      ┌──────────────┐      ┌───────────────┐      ┌─────────────┐
│   Python    │      │  PostgreSQL  │      │   FastAPI     │      │   Next.js   │
│   Scripts   │─────▶│   Database   │◀────▶│   Backend     │◀────▶│   Frontend  │
│ (Analysis)  │      │   (Storage)  │      │ (REST API)    │      │    (UI)     │
└─────────────┘      └──────────────┘      └───────────────┘      └─────────────┘
      │                      │                      │                      │
      │                      │                      │                      │
   CSV/JSON             Structured              JSON                 SVG/D3.js
   Results              Relations             Response              Visualizations
```

---

## Component Architecture

### 1. Python Analysis Layer
**Location:** `/Users/princejona/a1/tools/relational_math/`

**Key File:**
- `truth_distortion_unified.py` - **The complete unified diagnostic engine**
  - Integrates ALL relational math components
  - Combines Truth Lattice + Distortion Lattice analysis
  - Runs topology analysis, collapse detection, and RFI calculation
  - Single source of truth for all diagnostics

**Backend Integration:**
- FastAPI calls `truth_distortion_unified.py` as subprocess
- Path: `/Users/princejona/a1/tools/relational_math/truth_distortion_unified.py`
- Configuration: Set via `DIAGNOSTIC_SCRIPT_PATH` environment variable

**Inputs:** 
- CSV data files (via command-line argument)
- Configuration parameters (optional CLI flags)

**Outputs:**
- Diagnostic results (JSON to stdout)
- Topology data (node/edge lists)
- Collapse features (ranked list)
- Lattice point (RFI, collapse ratio, zone)
- Metadata (timestamps, status)

---

### 2. Database Layer
**Technology:** PostgreSQL 15  
**Location:** `dashboard/backend/` (Docker container or localhost:5432)

**Schema:**

```sql
-- Table: diagnostic_runs
CREATE TABLE diagnostic_runs (
    id UUID PRIMARY KEY,
    data_path TEXT NOT NULL,
    status TEXT NOT NULL,  -- 'pending', 'running', 'completed', 'failed'
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    error TEXT
);

-- Table: diagnostic_results
CREATE TABLE diagnostic_results (
    id SERIAL PRIMARY KEY,
    run_id UUID REFERENCES diagnostic_runs(id) ON DELETE CASCADE,
    m_total INTEGER,
    m_effective FLOAT,
    collapse_ratio FLOAT,
    rfi FLOAT,
    shape TEXT,
    results_json JSONB  -- Full analysis output
);

-- Table: topology_data
CREATE TABLE topology_data (
    id SERIAL PRIMARY KEY,
    run_id UUID REFERENCES diagnostic_runs(id) ON DELETE CASCADE,
    nodes JSONB,  -- Array of {id, degree, community}
    links JSONB,  -- Array of {source, target, weight}
    metadata JSONB
);

-- Table: collapse_features
CREATE TABLE collapse_features (
    id SERIAL PRIMARY KEY,
    run_id UUID REFERENCES diagnostic_runs(id) ON DELETE CASCADE,
    feature_index INTEGER,
    feature_name TEXT,
    collapse_score FLOAT,
    contribution_pct FLOAT,
    rank INTEGER
);

-- Table: lattice_points
CREATE TABLE lattice_points (
    id SERIAL PRIMARY KEY,
    run_id UUID REFERENCES diagnostic_runs(id),
    collapse_ratio FLOAT,
    rfi FLOAT,
    shape TEXT,
    status TEXT,
    created_at TIMESTAMP
);
```

**Indexes:**
```sql
CREATE INDEX idx_runs_status ON diagnostic_runs(status);
CREATE INDEX idx_runs_created ON diagnostic_runs(created_at DESC);
CREATE INDEX idx_results_run ON diagnostic_results(run_id);
CREATE INDEX idx_topology_run ON topology_data(run_id);
CREATE INDEX idx_collapse_run ON collapse_features(run_id);
CREATE INDEX idx_lattice_run ON lattice_points(run_id);
```

---

### 3. API Layer (FastAPI Backend)
**Location:** `dashboard/backend/main.py`  
**Port:** 8000  
**Technology:** FastAPI + asyncpg

**Endpoints:**

#### Runs Management
```http
GET    /api/runs              # List all diagnostic runs (paginated)
POST   /api/runs              # Create new run (triggers analysis)
GET    /api/runs/{id}         # Get single run details
DELETE /api/runs/{id}         # Delete run and all related data
DELETE /api/runs              # Bulk delete (query params: ids[])
```

#### Results & Data
```http
GET /api/runs/{id}/results          # Get diagnostic results (m_eff, RFI, etc.)
GET /api/runs/{id}/topology-graph   # Get network topology data
GET /api/runs/{id}/collapse-features # Get feature importance rankings
GET /api/runs/{id}/lattice-point    # Get lattice coordinates
```

#### Health & Meta
```http
GET /api/health    # API health check
GET /api/lattice   # Get all runs for lattice view
```

---

### 4. Frontend Layer (Next.js 16)
**Location:** `dashboard/frontend/`  
**Port:** 3000  
**Technology:** Next.js 16 + React + TypeScript + Tailwind + D3.js

**Page Structure:**
```
/                          - Dashboard (run list, stats)
/runs/[id]                 - Run detail page (topology, collapse, results)
/compare                   - Comparison view (2+ runs side-by-side)
/lattice                   - Lattice phase plane (all runs)
/compare-visuals           - Legacy comparison demo
```

**Component Structure:**
```
components/
├── visualizations/
│   ├── TopologyGraph.tsx          # Interactive network (run detail)
│   ├── TopologyGraphStatic.tsx    # Read-only network (comparison)
│   ├── CollapseMapViewer.tsx      # Full collapse viewer (run detail)
│   ├── CollapseMapCompact.tsx     # Compact bars (comparison)
│   └── LatticePhasePlane.tsx      # Phase plane scatter plot
├── ui/
│   ├── Card.tsx
│   ├── Button.tsx
│   └── Tooltip.tsx
└── layout/
    └── Navigation.tsx
```

---

## Detailed Data Flow

### Flow 1: Creating a New Diagnostic Run

```
┌─────────┐
│  User   │
│ Action  │
└────┬────┘
     │ 1. Clicks "New Diagnostic Run"
     │    Selects CSV file
     │    Sets parameters
     ▼
┌──────────────┐
│   Frontend   │
│  (Next.js)   │
└──────┬───────┘
     │ 2. POST /api/runs
     │    { data_path: "/path/to/data.csv", ... }
     ▼
┌──────────────┐
│   Backend    │
│  (FastAPI)   │
└──────┬───────┘
     │ 3. INSERT INTO diagnostic_runs
     │    Status: 'pending'
     │    Returns run_id: UUID
     ▼
┌──────────────┐
│  Database    │
│ (PostgreSQL) │
└──────┬───────┘
     │ 4. Run created, status='pending'
     │
     ├─────────────────┐
     │                 │ 5. Backend spawns subprocess
     ▼                 ▼
┌──────────────┐  ┌────────────────┐
│  Database    │  │ Python Script  │
│ (Update)     │  │ (Analysis)     │
└──────────────┘  └────────┬───────┘
                           │ 6. Reads CSV
                           │    Runs truth_distortion_unified.py
                           │    Computes topology + collapse + RFI
                           │    Outputs JSON to stdout
                           ▼
                  ┌────────────────┐
                  │ Analysis Output│
                  │ (JSON files)   │
                  └────────┬───────┘
                           │ 7. Writes results to files
                           │    /results/{run_id}/
                           ▼
                  ┌────────────────┐
                  │   Backend      │
                  │ (Result Parser)│
                  └────────┬───────┘
                           │ 8. Reads JSON results
                           │    Parses topology, collapse
                           │    Updates database
                           ▼
                  ┌────────────────┐
                  │   Database     │
                  │ (Final State)  │
                  └────────────────┘
                           │ Status: 'completed'
                           │ All data inserted:
                           │  - diagnostic_results
                           │  - topology_data
                           │  - collapse_features
                           │  - lattice_points
```

**Timeline:**
- **T+0s:** User submits request
- **T+0.1s:** Database record created
- **T+0.2s:** Python subprocess started
- **T+1-5s:** Analysis runs (depends on data size)
- **T+5.1s:** Results parsed and inserted
- **T+5.2s:** Frontend polls and updates UI

---

### Flow 2: Viewing a Run's Topology Graph

```
┌─────────┐
│  User   │
│ Clicks  │
│ Run ID  │
└────┬────┘
     │ 1. Navigate to /runs/{id}
     ▼
┌──────────────┐
│   Next.js    │
│   Router     │
└──────┬───────┘
     │ 2. Page component renders
     │    Triggers data fetch (SWR)
     ▼
┌──────────────┐
│   Frontend   │
│ (API Client) │
└──────┬───────┘
     │ 3. GET /api/runs/{id}/topology-graph
     ▼
┌──────────────┐
│   Backend    │
│  (FastAPI)   │
└──────┬───────┘
     │ 4. SELECT FROM topology_data
     │    WHERE run_id = {id}
     ▼
┌──────────────┐
│  Database    │
│ (PostgreSQL) │
└──────┬───────┘
     │ 5. Returns JSON:
     │    {
     │      nodes: [{id, degree, community}, ...],
     │      links: [{source, target, weight}, ...],
     │      metadata: {node_count, edge_count, ...}
     │    }
     ▼
┌──────────────┐
│   Backend    │
│ (Serializer) │
└──────┬───────┘
     │ 6. Formats response
     │    Adds CORS headers
     ▼
┌──────────────┐
│   Frontend   │
│ (SWR Cache)  │
└──────┬───────┘
     │ 7. Caches data
     │    Passes to component
     ▼
┌──────────────┐
│  TopologyGraph│
│  Component   │
└──────┬───────┘
     │ 8. D3.js processing:
     │    - Creates force simulation
     │    - Positions nodes
     │    - Draws SVG elements
     ▼
┌──────────────┐
│   Browser    │
│ (Rendered)   │
└──────────────┘
     │ 9. User sees interactive graph
     │    Can drag, zoom, pin nodes
```

**Data Transformation:**

**Database → API:**
```json
{
  "nodes": [
    {"id": "feature_0", "degree": 3, "community": 0},
    {"id": "feature_1", "degree": 7, "community": 0}
  ],
  "links": [
    {"source": "feature_0", "target": "feature_1", "weight": 0.85}
  ]
}
```

**API → D3.js:**
```typescript
interface Node extends d3.SimulationNodeDatum {
  id: string;
  degree: number;
  community: number;
  x?: number;  // Added by D3 simulation
  y?: number;
  vx?: number;
  vy?: number;
}

// D3 converts links to reference node objects
{
  source: Node,  // Object reference, not string
  target: Node,
  weight: number
}
```

---

### Flow 3: Comparing Multiple Runs

```
┌─────────┐
│  User   │
│ Selects │
│ 2+ Runs │
└────┬────┘
     │ 1. Checks run checkboxes
     │    Clicks "Compare Selected"
     ▼
┌──────────────┐
│  Dashboard   │
│    Page      │
└──────┬───────┘
     │ 2. router.push('/compare?ids=a,b,c')
     ▼
┌──────────────┐
│   Compare    │
│    Page      │
└──────┬───────┘
     │ 3. Parse URL params
     │    ids = ['run_a_id', 'run_b_id']
     ▼
┌──────────────┐
│   Frontend   │
│ (useEffect)  │
└──────┬───────┘
     │ 4. Parallel fetch for each run:
     │
     ├──── GET /api/runs/run_a_id ────┐
     │                                  │
     └──── GET /api/runs/run_b_id ────┤
                                       │
     ┌─────────────────────────────────┘
     │ 5. Both responses received
     ▼
┌──────────────┐
│   Compare    │
│    State     │
└──────┬───────┘
     │ 6. User clicks "Topologies" tab
     ▼
┌──────────────┐
│   Frontend   │
│ (Tab Logic)  │
└──────┬───────┘
     │ 7. Parallel fetch topology data:
     │
     ├── GET /api/runs/run_a_id/topology-graph ──┐
     │                                            │
     └── GET /api/runs/run_b_id/topology-graph ──┤
                                                  │
     ┌────────────────────────────────────────────┘
     │ 8. Both topology datasets ready
     ▼
┌──────────────┐
│   Compare    │
│    View      │
└──────┬───────┘
     │ 9. Renders:
     │    <TopologyGraphStatic run_a_data />
     │    <TopologyGraphStatic run_b_data />
     │    Side-by-side in 2-column grid
     ▼
┌──────────────┐
│   Browser    │
│ (2 Graphs)   │
└──────────────┘
     │ 10. User visually compares
```

**Performance Optimization:**
- SWR caching: If run data already fetched, reuse
- Parallel requests: All API calls happen simultaneously
- Lazy loading: Topology/collapse data only fetched when tab active

---

### Flow 4: Lattice Phase Plane (All Runs)

```
┌─────────┐
│  User   │
│ Clicks  │
│ Lattice │
└────┬────┘
     │ 1. Navigate to /lattice
     ▼
┌──────────────┐
│  Lattice     │
│   Page       │
└──────┬───────┘
     │ 2. GET /api/lattice
     ▼
┌──────────────┐
│   Backend    │
│  (FastAPI)   │
└──────┬───────┘
     │ 3. SELECT FROM lattice_points
     │    JOIN diagnostic_runs
     │    WHERE status = 'completed'
     │    ORDER BY created_at DESC
     ▼
┌──────────────┐
│  Database    │
│ (PostgreSQL) │
└──────┬───────┘
     │ 4. Returns array of points:
     │    [{
     │      run_id: UUID,
     │      collapse_ratio: float,
     │      rfi: float,
     │      shape: string,
     │      created_at: timestamp
     │    }, ...]
     ▼
┌──────────────┐
│   Frontend   │
│ (SWR Cache)  │
└──────┬───────┘
     │ 5. Passes to LatticePhasePlane component
     ▼
┌──────────────┐
│LatticePhasePlane│
│  Component   │
└──────┬───────┘
     │ 6. D3.js rendering:
     │    - Create scales (x: RFI, y: Collapse)
     │    - Draw axes
     │    - Plot points (circles)
     │    - Add legend
     │    - Attach tooltips
     ▼
┌──────────────┐
│   Browser    │
│ (Scatter Plot)│
└──────────────┘
     │ 7. User hovers/clicks points
     │    → Navigate to run detail
```

---

## Data Formats & Schemas

### 1. Topology Graph Data

**Database Storage (JSONB):**
```json
{
  "nodes": [
    {
      "id": "feature_0",
      "degree": 3,
      "community": 0
    }
  ],
  "links": [
    {
      "source": "feature_0",
      "target": "feature_1",
      "weight": 0.85
    }
  ],
  "metadata": {
    "node_count": 39,
    "edge_count": 36,
    "num_communities": 3
  }
}
```

**API Response:**
```json
{
  "nodes": [...],
  "links": [...],
  "metadata": {...}
}
```

**Frontend TypeScript:**
```typescript
interface TopologyData {
  nodes: Array<{
    id: string;
    degree: number;
    community: number;
  }>;
  links: Array<{
    source: string;
    target: string;
    weight: number;
  }>;
  metadata: {
    node_count: number;
    edge_count: number;
    num_communities: number;
  };
}
```

---

### 2. Collapse Features Data

**Database Rows:**
```sql
run_id | feature_index | feature_name | collapse_score | contribution_pct | rank
-------|---------------|--------------|----------------|------------------|-----
uuid   | 35            | Feature 35   | 0.95          | 11.06           | 1
uuid   | 32            | Feature 32   | 0.92          | 10.56           | 2
```

**API Response:**
```json
{
  "data": [
    {
      "feature_index": 35,
      "feature_name": "Feature 35",
      "collapse_score": 0.95,
      "contribution_pct": 11.06,
      "rank": 1
    }
  ],
  "metadata": {
    "m_total": 39,
    "m_effective": 19.7,
    "collapse_ratio": 0.505,
    "meff_liji": 19.2
  }
}
```

**Frontend TypeScript:**
```typescript
interface CollapseFeature {
  feature_index: number;
  feature_name?: string;
  collapse_score: number;
  contribution_pct: number;
  rank?: number;
}

interface CollapseData {
  data: CollapseFeature[];
  metadata: {
    m_total: number;
    m_effective: number;
    collapse_ratio: number;
    meff_liji: number;
  };
}
```

---

## Performance Considerations

### Database Queries

**Optimized Patterns:**

1. **Run List (Dashboard):**
   ```sql
   SELECT id, data_path, status, created_at, duration_seconds
   FROM diagnostic_runs
   WHERE status = 'completed'  -- Uses index
   ORDER BY created_at DESC    -- Uses index
   LIMIT 20 OFFSET 0;          -- Pagination
   ```
   **Performance:** ~1-2ms for 1000s of runs

2. **Topology Data:**
   ```sql
   SELECT nodes, links, metadata
   FROM topology_data
   WHERE run_id = $1;  -- Uses index, single row
   ```
   **Performance:** ~5-10ms for 1000-node graph

3. **Lattice Points (All Runs):**
   ```sql
   SELECT lp.run_id, lp.collapse_ratio, lp.rfi, lp.shape,
          dr.status, dr.created_at
   FROM lattice_points lp
   JOIN diagnostic_runs dr ON lp.run_id = dr.run_id
   WHERE dr.status = 'completed';
   ```
   **Performance:** ~10-20ms for 100s of runs

### Frontend Optimization

**Strategies:**

1. **SWR Caching:**
   - Cache duration: 60 seconds
   - Revalidate on focus
   - Deduplication of parallel requests

2. **Lazy Loading:**
   - Topology/collapse data only fetched when tab active
   - D3 simulations started on-demand

3. **Virtualization:**
   - Run list uses pagination (20 per page)
   - Large collapse maps show top N (default 20)

4. **SVG Optimization:**
   - Force simulations auto-stop after 3 seconds
   - No unnecessary re-renders (React.memo)
   - Responsive sizing via CSS (not full redraw)

---

## Error Handling

### Python Analysis Layer

**Failure Modes:**
- File not found → Error written to database
- Invalid CSV format → Parsing error logged
- Insufficient data → Analysis fails gracefully

**Recovery:**
```python
try:
    results = run_analysis(data_path)
    write_results(results)
except Exception as e:
    update_run_status(run_id, 'failed', error=str(e))
```

### API Layer

**Error Responses:**
```json
{
  "detail": "Run not found",
  "status_code": 404
}
```

**Common Errors:**
- 404: Run ID doesn't exist
- 400: Invalid request (missing required fields)
- 500: Database connection error

### Frontend Layer

**Error Display:**
- Toast notifications for transient errors
- Error boundaries for component crashes
- Empty states for missing data
- Helpful error pages with guidance

---

## Security & Access Control

**Current State:** No authentication (local deployment)

**Future Considerations:**
- API key authentication for backend
- User accounts with per-user run isolation
- Role-based access (viewer, editor, admin)
- CORS configuration for production

---

## Monitoring & Logging

### Backend Logs

**Location:** `dashboard/backend/backend.log`

**Contents:**
- API request logs (method, path, status, duration)
- Database query logs (slow queries flagged)
- Error traces (full stack traces for 500s)

**Example:**
```
2025-10-30 14:23:15 INFO GET /api/runs 200 12ms
2025-10-30 14:23:18 INFO GET /api/runs/84a75bf6.../topology-graph 200 8ms
2025-10-30 14:23:45 ERROR POST /api/runs 500 "Database connection failed"
```

### Frontend Logs

**Console Logging:**
- Development: Full debug logs
- Production: Errors only

**Example:**
```javascript
console.log('Topology fetch for run_id:', response.status);
console.error('Failed to load data:', error);
```

---

## Deployment Architecture

### Development Setup

```
localhost:3000 (Next.js) → localhost:8000 (FastAPI) → localhost:5432 (PostgreSQL)
```

**No Docker:** Direct process execution

### Production Setup (Future)

```
┌──────────────┐
│   Nginx      │ Port 80/443
│ (Reverse     │
│   Proxy)     │
└──────┬───────┘
       │
       ├─────→ Next.js (Container, Port 3000)
       │
       └─────→ FastAPI (Container, Port 8000)
                  │
                  └───→ PostgreSQL (Container, Port 5432)
```

**Docker Compose:**
- Managed networking
- Persistent volumes for database
- Auto-restart policies

---

## Troubleshooting Guide

### Issue: Visualization Not Loading

**Check:**
1. Backend running? `curl http://localhost:8000/api/health`
2. Database connected? Check backend logs
3. Data exists? Query database directly
4. Frontend console errors? Open DevTools

### Issue: Slow Topology Rendering

**Causes:**
- Graph too large (>500 nodes)
- Force simulation not converging

**Solutions:**
- Increase simulation timeout
- Apply filtering (community-based)
- Consider static layout pre-computation

### Issue: Missing Data in Comparison

**Causes:**
- Run not completed
- API endpoint mismatch
- Data structure change

**Debug:**
1. Check run status in database
2. Inspect API response in Network tab
3. Verify data transformation logic

---

## Future Enhancements

**Planned:**
1. **Real-time updates:** WebSocket for live run progress
2. **Export functionality:** Download visualizations as PNG/SVG
3. **Annotation system:** User comments on runs/features
4. **Advanced filtering:** Complex queries on lattice plane
5. **Batch operations:** Compare 10+ runs, diff analysis

---

**Document Maintainer:** Dashboard Development Team  
**Last Reviewed:** October 30, 2025  
**Related Docs:** `USER_GUIDE_VISUALIZATIONS.md`, `ARCHITECTURE.md`

**End of Data Flow Documentation**
