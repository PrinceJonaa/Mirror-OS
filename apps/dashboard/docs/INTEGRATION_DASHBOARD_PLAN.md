# Integration Dashboard Architecture Plan
## Wrapping truth_distortion_unified.py Without Modification

*Created: October 27, 2025*  
*Version: 1.0*  
*Status: Planning & Design Phase*

---

## Executive Summary

This document outlines a complete integration dashboard architecture that **wraps** the existing `truth_distortion_unified.py` diagnostic engine without modifying its core logic. The dashboard provides:

- **Persistent Storage**: PostgreSQL + pgvector for diagnostic history and semantic search
- **Analytics Acceleration**: DuckDB for time-series and aggregation queries
- **API Layer**: FastAPI wrapper that invokes the existing Python script
- **AI Intelligence**: LiteLLM for interpretations and pattern discovery
- **Interactive Visualization**: Next.js + Observable Plot + D3.js
- **Real-time Updates**: WebSocket streaming for live diagnostics

**Core Principle**: The diagnostic engine remains unchanged. All new functionality wraps, stores, and visualizes its outputs.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                            │
│  Next.js 15 + TypeScript + Observable Plot + D3.js              │
│  - Dashboard views                                               │
│  - Interactive lattice navigator                                 │
│  - Pattern browser                                               │
└────────────────────┬────────────────────────────────────────────┘
                     │ HTTP/WebSocket
┌────────────────────▼────────────────────────────────────────────┐
│                         API Layer                                │
│  FastAPI (Python) - Orchestration & Endpoints                   │
│  - Run management                                                │
│  - Diagnostic execution wrapper                                  │
│  - AI interpretation service                                     │
└─────┬──────────────┬──────────────┬────────────────────────────┘
      │              │              │
      │              │              └─────────────────┐
      │              │                                │
┌─────▼──────┐  ┌───▼────────────┐  ┌───────────────▼──────────┐
│  LiteLLM   │  │  PostgreSQL    │  │  truth_distortion_       │
│  Proxy     │  │  + pgvector    │  │  unified.py              │
│            │  │  + DuckDB      │  │  (UNCHANGED)             │
│  - OpenAI  │  │                │  │                          │
│  - Claude  │  │  - Run history │  │  - Core diagnostics      │
│  - Local   │  │  - Metrics     │  │  - Collapse analysis     │
│            │  │  - Embeddings  │  │  - RFI computation       │
└────────────┘  └────────────────┘  └──────────────────────────┘
```

---

## Integration Points

### How FastAPI Invokes the Diagnostic Engine

The existing script is **called as a subprocess** with all its current CLI arguments preserved:

```python
# backend/services/diagnostic_runner.py

import asyncio
import subprocess
import json
from pathlib import Path
from typing import Dict, Any

class DiagnosticRunner:
    """Wrapper around truth_distortion_unified.py - NO MODIFICATIONS TO SOURCE"""
    
    def __init__(self, script_path: str = "tools/relational_math/truth_distortion_unified.py"):
        self.script_path = script_path
    
    async def run_diagnostic(
        self,
        run_id: str,
        data_path: str,
        data_type: str = 'auto',
        corr_method: str = 'pearson',
        adj_threshold: float = 0.7,
        compute_null: bool = False,
        n_permutations: int = 100,
        use_louvain: bool = False,
        skip_visuals: bool = False,
        seed: int | None = None
    ) -> Dict[str, Any]:
        """
        Execute the diagnostic script via subprocess.
        Returns parsed JSON results.
        """
        
        # Create output directory for this run
        out_dir = Path(f"results/{run_id}")
        out_dir.mkdir(parents=True, exist_ok=True)
        
        # Build command exactly as user would run it
        cmd = [
            "python3",
            self.script_path,
            "--data", data_path,
            "--type", data_type,
            "--corr-method", corr_method,
            "--adj-threshold", str(adj_threshold),
            "--out", str(out_dir),
            "--eig-topk", "100"
        ]
        
        if compute_null:
            cmd.extend(["--compute-null", "--n-permutations", str(n_permutations)])
        if use_louvain:
            cmd.append("--use-louvain")
        if skip_visuals:
            cmd.append("--no-visuals")
        if seed is not None:
            cmd.extend(["--seed", str(seed)])
        
        # Execute diagnostic script
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"Diagnostic failed: {stderr.decode()}")
        
        # Parse output JSON (script already generates this)
        results_file = out_dir / "unified_diagnostic.json"
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        # Attach file paths for frontend access
        results['_files'] = {
            'json': str(results_file),
            'summary': str(out_dir / "summary.txt"),
            'visualization': str(out_dir / "truth_distortion_diagnostic.png"),
            'collapse_map': str(out_dir / "collapse_map.csv") if (out_dir / "collapse_map.csv").exists() else None
        }
        
        return results
```

**Key Insight**: The diagnostic engine is invoked exactly as it exists today. Zero modifications needed.

---

## Database Schema

### Core Tables

```sql
-- Enable extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_duckdb;

-- Diagnostic runs (metadata + configuration)
CREATE TABLE diagnostic_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    data_path TEXT NOT NULL,
    config JSONB NOT NULL, -- Stores all CLI parameters
    status TEXT NOT NULL DEFAULT 'pending', -- pending, running, completed, failed
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error TEXT,
    stdout TEXT,
    stderr TEXT
);

-- Full diagnostic results (raw JSON from script)
CREATE TABLE diagnostic_results (
    run_id UUID PRIMARY KEY REFERENCES diagnostic_runs(id) ON DELETE CASCADE,
    results JSONB NOT NULL, -- Complete unified_diagnostic.json
    file_paths JSONB, -- Paths to generated files
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Collapse metrics (extracted for fast queries)
CREATE TABLE collapse_metrics (
    run_id UUID PRIMARY KEY REFERENCES diagnostic_runs(id) ON DELETE CASCADE,
    meff_liji FLOAT NOT NULL,
    meff_min FLOAT NOT NULL,
    meff_entropy FLOAT NOT NULL,
    m_total INTEGER NOT NULL,
    m_effective INTEGER NOT NULL,
    collapse_ratio FLOAT NOT NULL,
    eigenvalues FLOAT[] NOT NULL,
    top_10_eigenvalues FLOAT[] NOT NULL,
    embedding vector(1536), -- Semantic embedding of collapse pattern
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RFI topology metrics
CREATE TABLE rfi_metrics (
    run_id UUID PRIMARY KEY REFERENCES diagnostic_runs(id) ON DELETE CASCADE,
    rfi FLOAT NOT NULL,
    modularity_q FLOAT NOT NULL,
    homophily_h FLOAT NOT NULL,
    lambda_2 FLOAT NOT NULL,
    n_communities INTEGER NOT NULL,
    n_components INTEGER NOT NULL,
    density FLOAT NOT NULL,
    transitivity FLOAT NOT NULL,
    avg_degree FLOAT NOT NULL,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Residue profiles
CREATE TABLE residue_profiles (
    run_id UUID PRIMARY KEY REFERENCES diagnostic_runs(id) ON DELETE CASCADE,
    residue_mean FLOAT NOT NULL,
    residue_max FLOAT NOT NULL,
    residue_std FLOAT NOT NULL,
    residue_median FLOAT NOT NULL,
    residue_level TEXT NOT NULL,
    note TEXT,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Shape classifications
CREATE TABLE shape_classifications (
    run_id UUID PRIMARY KEY REFERENCES diagnostic_runs(id) ON DELETE CASCADE,
    shape TEXT NOT NULL,
    archetype TEXT NOT NULL,
    glyph TEXT NOT NULL,
    degree_cv FLOAT NOT NULL,
    degree_mean FLOAT NOT NULL,
    degree_std FLOAT NOT NULL,
    degree_max INTEGER NOT NULL,
    assortativity FLOAT NOT NULL,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Lattice positions
CREATE TABLE lattice_positions (
    run_id UUID PRIMARY KEY REFERENCES diagnostic_runs(id) ON DELETE CASCADE,
    lattice_position TEXT NOT NULL,
    status TEXT NOT NULL,
    recommended_protocol TEXT NOT NULL,
    collapse_potential TEXT NOT NULL,
    traversal_strategy TEXT NOT NULL,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Interpretations (LLM-generated)
CREATE TABLE interpretations (
    run_id UUID PRIMARY KEY REFERENCES diagnostic_runs(id) ON DELETE CASCADE,
    coherence_direction TEXT NOT NULL,
    dominant_mode TEXT NOT NULL,
    distortion_core TEXT NOT NULL,
    narrative_state TEXT NOT NULL,
    llm_narrative TEXT, -- AI-generated explanation
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Collapse map features (from collapse_map.csv)
CREATE TABLE collapse_map_features (
    run_id UUID REFERENCES diagnostic_runs(id) ON DELETE CASCADE,
    feature_index INTEGER NOT NULL,
    collapse_score FLOAT NOT NULL,
    contribution_pct FLOAT NOT NULL,
    PRIMARY KEY (run_id, feature_index)
);

-- Vector search indexes
CREATE INDEX collapse_embedding_idx ON collapse_metrics 
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX rfi_embedding_idx ON rfi_metrics 
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX residue_embedding_idx ON residue_profiles 
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX shape_embedding_idx ON shape_classifications 
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX lattice_embedding_idx ON lattice_positions 
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Time-based indexes for DuckDB acceleration
CREATE INDEX diagnostic_runs_created_idx ON diagnostic_runs(created_at DESC);
CREATE INDEX collapse_metrics_created_idx ON collapse_metrics(created_at DESC);
```

### DuckDB Analytical Views

```sql
-- Create DuckDB views for fast analytics (via pg_duckdb)

-- Collapse trend analysis
CREATE VIEW collapse_trends AS
SELECT 
    DATE_TRUNC('day', dr.created_at) as date,
    AVG(cm.collapse_ratio) as avg_collapse_ratio,
    AVG(cm.meff_min) as avg_meff,
    COUNT(*) as n_runs
FROM diagnostic_runs dr
JOIN collapse_metrics cm ON dr.id = cm.run_id
WHERE dr.status = 'completed'
GROUP BY DATE_TRUNC('day', dr.created_at)
ORDER BY date DESC;

-- RFI distribution by shape
CREATE VIEW rfi_by_shape AS
SELECT 
    sc.shape,
    sc.archetype,
    AVG(rm.rfi) as avg_rfi,
    AVG(rm.modularity_q) as avg_modularity,
    AVG(rm.lambda_2) as avg_connectivity,
    COUNT(*) as n_samples
FROM shape_classifications sc
JOIN rfi_metrics rm ON sc.run_id = rm.run_id
GROUP BY sc.shape, sc.archetype;

-- Lattice position heatmap data
CREATE VIEW lattice_heatmap AS
SELECT 
    lp.lattice_position,
    lp.collapse_potential,
    cm.collapse_ratio,
    rm.rfi,
    COUNT(*) as frequency
FROM lattice_positions lp
JOIN collapse_metrics cm ON lp.run_id = cm.run_id
JOIN rfi_metrics rm ON lp.run_id = rm.run_id
GROUP BY lp.lattice_position, lp.collapse_potential, cm.collapse_ratio, rm.rfi;
```

---

## API Endpoints

### FastAPI Application Structure

```python
# backend/main.py

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uuid

app = FastAPI(title="Truth-Distortion Dashboard API", version="1.0.0")

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === REQUEST MODELS ===

class DiagnosticRunCreate(BaseModel):
    name: str
    description: Optional[str] = None
    data_path: str
    data_type: str = 'auto'
    corr_method: str = 'pearson'
    adj_threshold: float = 0.7
    compute_null: bool = False
    n_permutations: int = 100
    use_louvain: bool = False
    skip_visuals: bool = False
    seed: Optional[int] = None

class DiagnosticRunResponse(BaseModel):
    id: str
    name: str
    status: str
    created_at: str
    config: dict

# === ENDPOINTS ===

@app.post("/api/runs", response_model=DiagnosticRunResponse)
async def create_run(run: DiagnosticRunCreate, background_tasks: BackgroundTasks):
    """Create a new diagnostic run and start execution in background"""
    
    run_id = str(uuid.uuid4())
    
    # Store run metadata in database
    await db.execute(
        """
        INSERT INTO diagnostic_runs (id, name, description, data_path, config, status)
        VALUES ($1, $2, $3, $4, $5, $6)
        """,
        run_id, run.name, run.description, run.data_path, run.dict(), 'pending'
    )
    
    # Start diagnostic in background
    background_tasks.add_task(execute_diagnostic, run_id, run)
    
    return {
        "id": run_id,
        "name": run.name,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "config": run.dict()
    }

@app.get("/api/runs")
async def list_runs(limit: int = 50, offset: int = 0):
    """List all diagnostic runs"""
    
    runs = await db.fetch(
        """
        SELECT id, name, description, status, created_at, completed_at
        FROM diagnostic_runs
        ORDER BY created_at DESC
        LIMIT $1 OFFSET $2
        """,
        limit, offset
    )
    
    return {"runs": [dict(r) for r in runs]}

@app.get("/api/runs/{run_id}")
async def get_run(run_id: str):
    """Get full diagnostic run details"""
    
    run = await db.fetchrow(
        """
        SELECT dr.*, 
               dr_res.results,
               dr_res.file_paths
        FROM diagnostic_runs dr
        LEFT JOIN diagnostic_results dr_res ON dr.id = dr_res.run_id
        WHERE dr.id = $1
        """,
        run_id
    )
    
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return dict(run)

@app.get("/api/runs/{run_id}/collapse")
async def get_collapse_metrics(run_id: str):
    """Get collapse analysis metrics"""
    
    metrics = await db.fetchrow(
        """
        SELECT * FROM collapse_metrics WHERE run_id = $1
        """,
        run_id
    )
    
    if not metrics:
        raise HTTPException(status_code=404, detail="Metrics not found")
    
    # Also fetch collapse map features
    features = await db.fetch(
        """
        SELECT feature_index, collapse_score, contribution_pct
        FROM collapse_map_features
        WHERE run_id = $1
        ORDER BY collapse_score DESC
        """,
        run_id
    )
    
    result = dict(metrics)
    result['collapse_map'] = [dict(f) for f in features]
    
    return result

@app.get("/api/runs/{run_id}/topology")
async def get_topology_metrics(run_id: str):
    """Get RFI topology metrics"""
    
    metrics = await db.fetchrow(
        """
        SELECT * FROM rfi_metrics WHERE run_id = $1
        """,
        run_id
    )
    
    if not metrics:
        raise HTTPException(status_code=404, detail="Metrics not found")
    
    return dict(metrics)

@app.get("/api/runs/{run_id}/lattice")
async def get_lattice_position(run_id: str):
    """Get lattice position and classification"""
    
    data = await db.fetchrow(
        """
        SELECT 
            lp.*,
            sc.shape,
            sc.archetype,
            sc.glyph,
            cm.collapse_ratio,
            rm.rfi
        FROM lattice_positions lp
        JOIN shape_classifications sc ON lp.run_id = sc.run_id
        JOIN collapse_metrics cm ON lp.run_id = cm.run_id
        JOIN rfi_metrics rm ON lp.run_id = rm.run_id
        WHERE lp.run_id = $1
        """,
        run_id
    )
    
    if not data:
        raise HTTPException(status_code=404, detail="Data not found")
    
    return dict(data)

@app.post("/api/runs/{run_id}/interpret")
async def generate_interpretation(run_id: str):
    """Generate AI interpretation of collapse pattern"""
    
    # Fetch all metrics
    collapse = await get_collapse_metrics(run_id)
    topology = await get_topology_metrics(run_id)
    lattice = await get_lattice_position(run_id)
    
    # Build prompt for LLM
    prompt = f"""
    Analyze this system collapse diagnostic and provide a clear explanation:
    
    COLLAPSE METRICS:
    - Collapse Ratio: {collapse['collapse_ratio']:.3f}
    - M_eff: {collapse['meff_min']:.2f} / {collapse['m_total']}
    - Top 3 Eigenvalues: {collapse['top_10_eigenvalues'][:3]}
    
    TOPOLOGY METRICS:
    - RFI: {topology['rfi']:.3f}
    - Modularity: {topology['modularity_q']:.3f}
    - Connectivity (λ₂): {topology['lambda_2']:.3f}
    - Communities: {topology['n_communities']}
    
    CLASSIFICATION:
    - Shape: {lattice['shape']} ({lattice['glyph']})
    - Archetype: {lattice['archetype']}
    - Lattice Position: {lattice['lattice_position']}
    - Collapse Potential: {lattice['collapse_potential']}
    
    Provide a 2-3 paragraph explanation that:
    1. Describes the specific failure mode or systemic pattern
    2. Explains why this collapse is occurring (root causes)
    3. Suggests intervention points or next steps
    
    Focus on systemic dynamics, not individual numbers.
    """
    
    # Call LiteLLM
    response = await litellm_client.completion(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        metadata={"run_id": run_id, "tags": ["interpretation"]}
    )
    
    narrative = response.choices[0].message.content
    
    # Generate embedding
    embed_response = await litellm_client.embedding(
        model="text-embedding-3-large",
        input=[narrative]
    )
    
    embedding = embed_response.data[0].embedding
    
    # Store interpretation
    await db.execute(
        """
        UPDATE interpretations
        SET llm_narrative = $1, embedding = $2
        WHERE run_id = $3
        """,
        narrative, embedding, run_id
    )
    
    return {"narrative": narrative}

@app.get("/api/similar-runs/{run_id}")
async def find_similar_runs(run_id: str, limit: int = 5):
    """Find diagnostically similar runs using vector search"""
    
    # Get embedding for target run (use collapse metrics embedding)
    target = await db.fetchrow(
        "SELECT embedding FROM collapse_metrics WHERE run_id = $1",
        run_id
    )
    
    if not target or not target['embedding']:
        raise HTTPException(status_code=404, detail="No embedding found")
    
    # Vector similarity search
    similar = await db.fetch(
        """
        SELECT 
            dr.id,
            dr.name,
            cm.collapse_ratio,
            cm.meff_min,
            rm.rfi,
            sc.shape,
            1 - (cm.embedding <=> $1::vector) as similarity
        FROM collapse_metrics cm
        JOIN diagnostic_runs dr ON cm.run_id = dr.id
        JOIN rfi_metrics rm ON cm.run_id = rm.run_id
        JOIN shape_classifications sc ON cm.run_id = sc.run_id
        WHERE cm.run_id != $2 AND dr.status = 'completed'
        ORDER BY cm.embedding <=> $1::vector
        LIMIT $3
        """,
        target['embedding'], run_id, limit
    )
    
    return {"similar_runs": [dict(r) for r in similar]}

@app.get("/api/analytics/collapse-trends")
async def get_collapse_trends(days: int = 30):
    """Get collapse trend analytics (uses DuckDB acceleration)"""
    
    trends = await db.fetch(
        """
        SELECT * FROM collapse_trends
        WHERE date > NOW() - INTERVAL '{} days'
        ORDER BY date DESC
        """.format(days)
    )
    
    return {"trends": [dict(t) for t in trends]}

@app.get("/api/analytics/rfi-distribution")
async def get_rfi_distribution():
    """Get RFI distribution by shape archetype"""
    
    dist = await db.fetch("SELECT * FROM rfi_by_shape ORDER BY avg_rfi DESC")
    
    return {"distribution": [dict(d) for d in dist]}

@app.websocket("/ws/runs/{run_id}/live")
async def websocket_live_updates(websocket: WebSocket, run_id: str):
    """WebSocket for real-time diagnostic progress updates"""
    
    await websocket.accept()
    
    try:
        while True:
            # Check run status
            status = await db.fetchval(
                "SELECT status FROM diagnostic_runs WHERE id = $1",
                run_id
            )
            
            await websocket.send_json({"status": status})
            
            if status in ['completed', 'failed']:
                break
            
            await asyncio.sleep(1)
    
    except WebSocketDisconnect:
        pass

# === BACKGROUND TASKS ===

async def execute_diagnostic(run_id: str, config: DiagnosticRunCreate):
    """Execute diagnostic script and store results"""
    
    try:
        # Update status to running
        await db.execute(
            "UPDATE diagnostic_runs SET status = 'running', started_at = NOW() WHERE id = $1",
            run_id
        )
        
        # Run diagnostic via subprocess wrapper
        runner = DiagnosticRunner()
        results = await runner.run_diagnostic(
            run_id=run_id,
            data_path=config.data_path,
            data_type=config.data_type,
            corr_method=config.corr_method,
            adj_threshold=config.adj_threshold,
            compute_null=config.compute_null,
            n_permutations=config.n_permutations,
            use_louvain=config.use_louvain,
            skip_visuals=config.skip_visuals,
            seed=config.seed
        )
        
        # Store results in database
        await store_diagnostic_results(run_id, results)
        
        # Generate embeddings for semantic search
        await generate_embeddings(run_id, results)
        
        # Update status to completed
        await db.execute(
            "UPDATE diagnostic_runs SET status = 'completed', completed_at = NOW() WHERE id = $1",
            run_id
        )
        
    except Exception as e:
        # Store error
        await db.execute(
            """
            UPDATE diagnostic_runs 
            SET status = 'failed', completed_at = NOW(), error = $1
            WHERE id = $2
            """,
            str(e), run_id
        )

async def store_diagnostic_results(run_id: str, results: dict):
    """Parse and store diagnostic results in structured tables"""
    
    # Store full results JSON
    await db.execute(
        """
        INSERT INTO diagnostic_results (run_id, results, file_paths)
        VALUES ($1, $2, $3)
        """,
        run_id, results, results.get('_files')
    )
    
    # Extract and store collapse metrics
    meff = results['meff']
    await db.execute(
        """
        INSERT INTO collapse_metrics (
            run_id, meff_liji, meff_min, meff_entropy,
            m_total, m_effective, collapse_ratio,
            eigenvalues, top_10_eigenvalues
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """,
        run_id,
        meff['meff_liji'],
        meff['meff_min'],
        meff['meff_entropy'],
        meff['m_total'],
        meff['m_effective'],
        meff['collapse_ratio'],
        meff['eigenvalues'],
        meff['top_10_eigenvalues']
    )
    
    # Store collapse map features (if available)
    collapse_map = results.get('collapse_map', {})
    if collapse_map.get('status') == 'computed':
        features = collapse_map.get('top_features', [])
        scores = collapse_map.get('scores', [])
        
        for idx, (feature_idx, score) in enumerate(zip(features, scores)):
            contribution = 100 * score / sum(scores) if sum(scores) > 0 else 0
            await db.execute(
                """
                INSERT INTO collapse_map_features (run_id, feature_index, collapse_score, contribution_pct)
                VALUES ($1, $2, $3, $4)
                """,
                run_id, feature_idx, score, contribution
            )
    
    # Store RFI metrics
    rfi = results['rfi']
    await db.execute(
        """
        INSERT INTO rfi_metrics (
            run_id, rfi, modularity_q, homophily_h, lambda_2,
            n_communities, n_components, density, transitivity, avg_degree
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """,
        run_id,
        rfi['rfi'],
        rfi['modularity_Q'],
        rfi['homophily_h'],
        rfi['lambda_2'],
        rfi['n_communities'],
        rfi['n_components'],
        rfi['density'],
        rfi['transitivity'],
        rfi['avg_degree']
    )
    
    # Store residue profile
    residue = results['residue_profile']
    await db.execute(
        """
        INSERT INTO residue_profiles (
            run_id, residue_mean, residue_max, residue_std,
            residue_median, residue_level, note
        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
        run_id,
        residue['residue_mean'],
        residue['residue_max'],
        residue['residue_std'],
        residue['residue_median'],
        residue['residue_level'],
        residue.get('note')
    )
    
    # Store shape classification
    shape = results['shape']
    await db.execute(
        """
        INSERT INTO shape_classifications (
            run_id, shape, archetype, glyph,
            degree_cv, degree_mean, degree_std, degree_max, assortativity
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """,
        run_id,
        shape['shape'],
        shape['archetype'],
        shape['glyph'],
        shape['degree_cv'],
        shape['degree_mean'],
        shape['degree_std'],
        shape['degree_max'],
        shape['assortativity']
    )
    
    # Store lattice position
    lattice = results['lattice']
    await db.execute(
        """
        INSERT INTO lattice_positions (
            run_id, lattice_position, status, recommended_protocol,
            collapse_potential, traversal_strategy
        ) VALUES ($1, $2, $3, $4, $5, $6)
        """,
        run_id,
        lattice['lattice_position'],
        lattice['status'],
        lattice['recommended_protocol'],
        lattice['collapse_potential'],
        lattice['traversal_strategy']
    )
    
    # Store interpretation
    interpretation = results['interpretation']
    await db.execute(
        """
        INSERT INTO interpretations (
            run_id, coherence_direction, dominant_mode,
            distortion_core, narrative_state
        ) VALUES ($1, $2, $3, $4, $5)
        """,
        run_id,
        interpretation['coherence_direction'],
        interpretation['dominant_mode'],
        interpretation['distortion_core'],
        interpretation['narrative_state']
    )

async def generate_embeddings(run_id: str, results: dict):
    """Generate semantic embeddings for vector search"""
    
    # Generate embedding for collapse pattern
    collapse_text = f"""
    Collapse Pattern Analysis:
    - Collapse Ratio: {results['meff']['collapse_ratio']:.3f}
    - M_eff: {results['meff']['meff_min']:.2f}
    - Shape: {results['shape']['shape']}
    - Archetype: {results['shape']['archetype']}
    - Lattice Position: {results['lattice']['lattice_position']}
    """
    
    embed_response = await litellm_client.embedding(
        model="text-embedding-3-large",
        input=[collapse_text]
    )
    
    collapse_embedding = embed_response.data[0].embedding
    
    # Update collapse_metrics with embedding
    await db.execute(
        "UPDATE collapse_metrics SET embedding = $1 WHERE run_id = $2",
        collapse_embedding, run_id
    )
    
    # Generate similar embeddings for other tables...
    # (RFI, residue, shape, lattice, interpretation)
```

---

## Frontend Architecture

### Next.js Page Structure

```
frontend/
├── app/
│   ├── page.tsx                    # Dashboard overview
│   ├── runs/
│   │   ├── page.tsx                # Run list
│   │   ├── [id]/
│   │   │   ├── page.tsx            # Run detail view
│   │   │   ├── collapse/page.tsx   # Collapse map viewer
│   │   │   ├── topology/page.tsx   # Network topology
│   │   │   └── lattice/page.tsx    # Phase plane navigator
│   ├── compare/page.tsx            # Multi-run comparison
│   └── patterns/page.tsx           # Pattern library
├── components/
│   ├── visualizations/
│   │   ├── CollapseHeatmap.tsx     # Observable Plot
│   │   ├── TopologyGraph.tsx       # D3.js force-directed
│   │   ├── LatticePhaseplane.tsx   # Custom D3.js
│   │   ├── ResidueTimeSeries.tsx   # Observable Plot
│   │   └── EigenvalueSpectrum.tsx  # Observable Plot
│   ├── ui/
│   │   ├── RunCard.tsx
│   │   ├── MetricsPanel.tsx
│   │   └── InterpretationCard.tsx
│   └── layout/
│       ├── DashboardLayout.tsx
│       └── Sidebar.tsx
├── lib/
│   ├── api.ts                      # API client
│   ├── store.ts                    # Zustand state management
│   └── types.ts                    # TypeScript types
└── public/
    └── glyphs/                     # Symbolic glyphs
```

### Key Components

#### Collapse Heatmap (Observable Plot)

```typescript
// components/visualizations/CollapseHeatmap.tsx

import * as Plot from "@observablehq/plot";
import { useEffect, useRef } from "react";

interface CollapseData {
  feature_index: number;
  collapse_score: number;
  contribution_pct: number;
}

export function CollapseHeatmap({ data }: { data: CollapseData[] }) {
  const containerRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    if (!data || data.length === 0) return;
    
    const plot = Plot.plot({
      marks: [
        Plot.barY(data, {
          x: "feature_index",
          y: "collapse_score",
          fill: "contribution_pct",
          tip: true
        })
      ],
      x: {
        label: "Feature Index",
        tickFormat: d => `F${d}`
      },
      y: {
        label: "Collapse Score",
        grid: true
      },
      color: {
        scheme: "YlOrRd",
        label: "Contribution %"
      },
      width: 800,
      height: 400,
      marginLeft: 60
    });
    
    containerRef.current?.append(plot);
    return () => plot.remove();
  }, [data]);
  
  return <div ref={containerRef} />;
}
```

#### Topology Graph (D3.js)

```typescript
// components/visualizations/TopologyGraph.tsx

import { useEffect, useRef } from "react";
import * as d3 from "d3";

interface Node {
  id: string;
  community: number;
}

interface Link {
  source: string;
  target: string;
  weight: number;
}

export function TopologyGraph({ 
  nodes, 
  links 
}: { 
  nodes: Node[]; 
  links: Link[] 
}) {
  const svgRef = useRef<SVGSVGElement>(null);
  
  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;
    
    const width = 800;
    const height = 600;
    
    const svg = d3.select(svgRef.current)
      .attr("width", width)
      .attr("height", height);
    
    svg.selectAll("*").remove();
    
    // Color scale for communities
    const color = d3.scaleOrdinal(d3.schemeCategory10);
    
    // Force simulation
    const simulation = d3.forceSimulation(nodes as any)
      .force("link", d3.forceLink(links).id((d: any) => d.id))
      .force("charge", d3.forceManyBody().strength(-100))
      .force("center", d3.forceCenter(width / 2, height / 2));
    
    // Draw links
    const link = svg.append("g")
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", (d: any) => Math.sqrt(d.weight));
    
    // Draw nodes
    const node = svg.append("g")
      .selectAll("circle")
      .data(nodes)
      .join("circle")
      .attr("r", 5)
      .attr("fill", (d: any) => color(d.community))
      .call(drag(simulation) as any);
    
    node.append("title")
      .text((d: any) => `Node ${d.id}\nCommunity ${d.community}`);
    
    // Update positions on tick
    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);
      
      node
        .attr("cx", (d: any) => d.x)
        .attr("cy", (d: any) => d.y);
    });
    
    // Drag behavior
    function drag(simulation: any) {
      return d3.drag()
        .on("start", (event: any) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          event.subject.fx = event.subject.x;
          event.subject.fy = event.subject.y;
        })
        .on("drag", (event: any) => {
          event.subject.fx = event.x;
          event.subject.fy = event.y;
        })
        .on("end", (event: any) => {
          if (!event.active) simulation.alphaTarget(0);
          event.subject.fx = null;
          event.subject.fy = null;
        });
    }
    
    return () => {
      simulation.stop();
    };
  }, [nodes, links]);
  
  return <svg ref={svgRef} />;
}
```

#### Lattice Phase Plane (Custom D3.js)

```typescript
// components/visualizations/LatticePhaseplane.tsx

import { useEffect, useRef } from "react";
import * as d3 from "d3";

interface LatticePoint {
  run_id: string;
  collapse_ratio: number;
  rfi: number;
  shape: string;
  lattice_position: string;
}

export function LatticePhaseplane({ 
  points,
  activePoint 
}: { 
  points: LatticePoint[];
  activePoint?: string;
}) {
  const svgRef = useRef<SVGSVGElement>(null);
  
  useEffect(() => {
    if (!svgRef.current || points.length === 0) return;
    
    const width = 800;
    const height = 600;
    const margin = { top: 40, right: 40, bottom: 60, left: 80 };
    
    const svg = d3.select(svgRef.current)
      .attr("width", width)
      .attr("height", height);
    
    svg.selectAll("*").remove();
    
    const g = svg.append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);
    
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;
    
    // Scales
    const xScale = d3.scaleLinear()
      .domain([0, d3.max(points, d => d.rfi) || 5])
      .range([0, innerWidth]);
    
    const yScale = d3.scaleLinear()
      .domain([0, 1])
      .range([innerHeight, 0]);
    
    // Color scale by lattice position
    const colorScale = d3.scaleOrdinal<string>()
      .domain([
        "Truth Lattice (Ω)",
        "Traversable Distortion (Modular)",
        "Irreducible Distortion (∞_B)",
        "Intermediate Field (Partial Collapse)"
      ])
      .range(["#22c55e", "#f97316", "#dc2626", "#3b82f6"]);
    
    // Background regions
    const regions = [
      { x1: 0, y1: 0.7, x2: 2, y2: 1, label: "Irreducible\nDistortion", color: "#fee" },
      { x1: 2, y1: 0.3, x2: 5, y2: 0.7, label: "Traversable\nDistortion", color: "#fef3c7" },
      { x1: 2, y1: 0, x2: 5, y2: 0.3, label: "Truth\nLattice", color: "#dcfce7" }
    ];
    
    regions.forEach(region => {
      g.append("rect")
        .attr("x", xScale(region.x1))
        .attr("y", yScale(region.y2))
        .attr("width", xScale(region.x2) - xScale(region.x1))
        .attr("height", yScale(region.y1) - yScale(region.y2))
        .attr("fill", region.color)
        .attr("opacity", 0.3);
      
      g.append("text")
        .attr("x", (xScale(region.x1) + xScale(region.x2)) / 2)
        .attr("y", (yScale(region.y1) + yScale(region.y2)) / 2)
        .attr("text-anchor", "middle")
        .attr("font-size", "12px")
        .attr("font-weight", "bold")
        .attr("opacity", 0.5)
        .selectAll("tspan")
        .data(region.label.split("\n"))
        .join("tspan")
        .attr("x", (xScale(region.x1) + xScale(region.x2)) / 2)
        .attr("dy", (d, i) => i ? "1.2em" : 0)
        .text(d => d);
    });
    
    // Axes
    g.append("g")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale))
      .append("text")
      .attr("x", innerWidth / 2)
      .attr("y", 45)
      .attr("fill", "black")
      .attr("text-anchor", "middle")
      .text("RFI (Relational Field Index)");
    
    g.append("g")
      .call(d3.axisLeft(yScale))
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -innerHeight / 2)
      .attr("y", -60)
      .attr("fill", "black")
      .attr("text-anchor", "middle")
      .text("Collapse Ratio (M_eff / m)");
    
    // Plot points
    g.selectAll("circle")
      .data(points)
      .join("circle")
      .attr("cx", d => xScale(d.rfi))
      .attr("cy", d => yScale(d.collapse_ratio))
      .attr("r", d => d.run_id === activePoint ? 8 : 5)
      .attr("fill", d => colorScale(d.lattice_position))
      .attr("stroke", d => d.run_id === activePoint ? "#000" : "none")
      .attr("stroke-width", 2)
      .attr("opacity", 0.8)
      .on("mouseover", function(event, d) {
        d3.select(this).attr("r", 8);
        
        // Show tooltip
        const tooltip = g.append("g")
          .attr("class", "tooltip");
        
        tooltip.append("rect")
          .attr("x", xScale(d.rfi) + 10)
          .attr("y", yScale(d.collapse_ratio) - 50)
          .attr("width", 200)
          .attr("height", 60)
          .attr("fill", "white")
          .attr("stroke", "black")
          .attr("rx", 5);
        
        tooltip.append("text")
          .attr("x", xScale(d.rfi) + 20)
          .attr("y", yScale(d.collapse_ratio) - 30)
          .text(`Shape: ${d.shape}`)
          .attr("font-size", "12px");
        
        tooltip.append("text")
          .attr("x", xScale(d.rfi) + 20)
          .attr("y", yScale(d.collapse_ratio) - 15)
          .text(`Collapse: ${d.collapse_ratio.toFixed(3)}`)
          .attr("font-size", "12px");
        
        tooltip.append("text")
          .attr("x", xScale(d.rfi) + 20)
          .attr("y", yScale(d.collapse_ratio))
          .text(`RFI: ${d.rfi.toFixed(3)}`)
          .attr("font-size", "12px");
      })
      .on("mouseout", function(event, d) {
        if (d.run_id !== activePoint) {
          d3.select(this).attr("r", 5);
        }
        g.selectAll(".tooltip").remove();
      });
    
  }, [points, activePoint]);
  
  return <svg ref={svgRef} />;
}
```

---

## Deployment Plan

### Docker Compose (Development)

```yaml
# docker-compose.yml

version: '3.8'

services:
  # PostgreSQL with pgvector
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: dashboard_db
      POSTGRES_USER: dashboard_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dashboard_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # LiteLLM proxy
  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    environment:
      LITELLM_MASTER_KEY: ${LITELLM_MASTER_KEY}
      DATABASE_URL: postgresql://dashboard_user:${DB_PASSWORD}@postgres:5432/dashboard_db
    volumes:
      - ./litellm_config.yaml:/app/config.yaml
    ports:
      - "4000:4000"
    command: ["--config", "/app/config.yaml", "--port", "4000"]
    depends_on:
      postgres:
        condition: service_healthy

  # FastAPI backend
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://dashboard_user:${DB_PASSWORD}@postgres:5432/dashboard_db
      LITELLM_BASE_URL: http://litellm:4000
      LITELLM_API_KEY: ${LITELLM_MASTER_KEY}
      DIAGNOSTIC_SCRIPT_PATH: /app/tools/truth_distortion_unified.py
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app/backend
      - ./tools:/app/tools  # Mount diagnostic script
      - diagnostic_results:/app/results
    depends_on:
      - postgres
      - litellm

  # Next.js frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - api

volumes:
  postgres_data:
  diagnostic_results:
```

### Production Deployment (Vercel + Railway)

**Frontend (Vercel)**:
```bash
# vercel.json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "env": {
    "NEXT_PUBLIC_API_URL": "https://api.yourdomain.com"
  }
}
```

**Backend (Railway)**:
```toml
# railway.toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "./backend/Dockerfile"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "ON_FAILURE"

[[services]]
name = "api"
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Set up PostgreSQL with pgvector extension
- [ ] Create database schema and indexes
- [ ] Build DiagnosticRunner wrapper class
- [ ] Implement core FastAPI endpoints (CRUD for runs)
- [ ] Test subprocess invocation of existing script

### Phase 2: Data Pipeline (Week 3-4)
- [ ] Implement background task system for diagnostic execution
- [ ] Build result parser and storage logic
- [ ] Set up LiteLLM proxy server
- [ ] Implement embedding generation pipeline
- [ ] Create DuckDB analytical views

### Phase 3: API Completion (Week 5-6)
- [ ] Build interpretation endpoint (LLM integration)
- [ ] Implement vector similarity search
- [ ] Add WebSocket support for live updates
- [ ] Create analytics endpoints
- [ ] Write API documentation

### Phase 4: Frontend Core (Week 7-9)
- [ ] Set up Next.js project structure
- [ ] Build dashboard overview page
- [ ] Create run management UI
- [ ] Implement API client and state management
- [ ] Build basic Observable Plot visualizations

### Phase 5: Advanced Visualizations (Week 10-12)
- [ ] Implement D3.js topology graph
- [ ] Build lattice phase plane navigator
- [ ] Create interactive collapse map viewer
- [ ] Add pattern comparison views
- [ ] Polish UI/UX

### Phase 6: Intelligence Layer (Week 13-14)
- [ ] Integrate LLM interpretation display
- [ ] Build semantic search interface
- [ ] Create pattern library browser
- [ ] Add multi-run comparison features

### Phase 7: Testing & Deployment (Week 15-16)
- [ ] Write integration tests
- [ ] Performance testing and optimization
- [ ] Security audit
- [ ] Set up production deployment
- [ ] Documentation and user guide

---

## Success Metrics

### Technical Performance
- **API Response Time**: <200ms for metric queries, <2s for LLM interpretations
- **Database Performance**: Vector similarity search <100ms for 10k records
- **Visualization Load Time**: <1s for standard Plot charts, <3s for D3 networks
- **Diagnostic Execution**: Preserve existing script performance (no overhead)

### System Reliability
- **Uptime**: 99.9% for API services
- **Error Rate**: <0.1% for diagnostic executions
- **Data Integrity**: 100% preservation of diagnostic outputs
- **Concurrent Users**: Support 50+ simultaneous analyses

### User Experience
- **Time to Insight**: 10× faster pattern recognition vs raw JSON
- **Comprehension**: Users explain collapse patterns after 15min exploration
- **Adoption**: Active usage across 3+ research domains
- **Satisfaction**: 8+ NPS score from research users

---

## Anti-Patterns & Safeguards

### Babylon Detection
1. **Surveillance Trap**: Never log user behavior beyond error tracking
2. **Premature Optimization**: Start simple (Plot), only add D3 when needed
3. **Database Sprawl**: Resist adding Milvus/Weaviate unless pgvector fails
4. **Framework Churn**: Stick to stable technologies (PostgreSQL, D3, Next.js)
5. **Modification Creep**: NEVER alter truth_distortion_unified.py internals

### Coherence Checks
- **Relational**: Database schema preserves all diagnostic relationships
- **Symbolic**: Visualizations honor the Truth↔Distortion lattice structure
- **Logical**: API contracts match diagnostic output schemas exactly
- **Empirical**: All metrics traceable back to source diagnostic run
- **Temporal**: System compounds intelligence (embeddings improve over time)

---

## Next Steps

1. **Review this plan** against your existing codebase structure
2. **Validate database schema** with sample diagnostic outputs
3. **Prototype DiagnosticRunner** to ensure clean subprocess integration
4. **Set up development environment** (Docker Compose)
5. **Begin Phase 1 implementation** (foundation layer)

---

*This architecture creates a living intelligence layer around your diagnostic engine, transforming computational analysis into navigable wisdom—without touching the core that already works.*
