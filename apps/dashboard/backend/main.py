"""
Truth-Distortion Dashboard API
FastAPI wrapper around truth_distortion_unified.py diagnostic engine
"""

import asyncio
import json
import os
import subprocess
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import math
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect, UploadFile, File, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import asyncpg
import uvicorn
import shutil

# === CONFIGURATION ===

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://dashboard_user:password@localhost:5432/dashboard_db")
DIAGNOSTIC_SCRIPT_PATH = os.getenv("DIAGNOSTIC_SCRIPT_PATH", "/Users/princejona/a1/tools/relational_math/truth_distortion_unified.py")

# File upload settings - 500MB max
MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500MB in bytes

# === UTILITIES ===

def sanitize_for_json(obj):
    """Recursively sanitize objects for JSON serialization, replacing NaN/Inf with None"""
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    return obj

# === MODELS ===

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

class DiagnosticRun(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    data_path: str
    config: dict
    status: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None

class TopologyNode(BaseModel):
    id: str
    degree: int
    community: int

class TopologyLink(BaseModel):
    source: str
    target: str
    weight: float

class TopologyGraphResponse(BaseModel):
    nodes: List[TopologyNode]
    links: List[TopologyLink]
    metadata: Dict[str, Any]

class LatticePoint(BaseModel):
    run_id: str
    collapse_ratio: float
    rfi: float
    shape: str
    status: str
    created_at: str

class LatticePointsResponse(BaseModel):
    points: List[LatticePoint]

class CollapsePattern(BaseModel):
    run_id: str
    collapse_ratio: float
    rfi: float
    stability_score: float
    coherence_index: float
    resonance_frequency: float
    harmonics: List[float]

class CollapseMapResponse(BaseModel):
    patterns: List[CollapsePattern]

# === DIAGNOSTIC RUNNER ===

class DiagnosticRunner:
    """Wrapper around truth_distortion_unified.py - NO MODIFICATIONS TO SOURCE"""

    def __init__(self, script_path: str = DIAGNOSTIC_SCRIPT_PATH):
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

        # Build command exactly as user would run it (use python3.11 to access installed packages)
        cmd = [
            "python3.11",
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

# === DATABASE CONNECTION ===

class Database:
    def __init__(self, database_url: str = DATABASE_URL):
        self.database_url = database_url
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Initialize database connection pool"""
        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=1,
            max_size=10,
            command_timeout=60
        )

    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()

    async def execute(self, query: str, *args):
        """Execute a query without returning results"""
        if not self.pool:
            raise HTTPException(status_code=503, detail="Database not available")
        async with self.pool.acquire() as conn:
            await conn.execute(query, *args)

    async def fetch(self, query: str, *args):
        """Execute a query and return all results"""
        if not self.pool:
            raise HTTPException(status_code=503, detail="Database not available")
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        """Execute a query and return one result"""
        if not self.pool:
            raise HTTPException(status_code=503, detail="Database not available")
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args):
        """Execute a query and return a single value"""
        if not self.pool:
            raise HTTPException(status_code=503, detail="Database not available")
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)

# Global database instance
db = Database()

# === FASTAPI APP ===

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    try:
        await db.connect()
        print("Database connected")
    except Exception as e:
        print(f"Database connection failed: {e}")
        print("Starting without database - some endpoints will not work")
        # Don't raise exception, continue without database
    
    yield
    
    # Shutdown
    try:
        await db.disconnect()
        print("Database disconnected")
    except Exception as e:
        print(f"Database disconnect error: {e}")

app = FastAPI(
    title="Truth-Distortion Dashboard API",
    version="1.0.0",
    description="API wrapper around truth_distortion_unified.py diagnostic engine",
    lifespan=lifespan
)

print("FastAPI app created")

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("CORS middleware added")

# Global diagnostic runner
runner = DiagnosticRunner()

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
        run_id, run.name, run.description, run.data_path, json.dumps(run.dict()), 'pending'
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
        SELECT dr.*, dr_res.results, dr_res.file_paths
        FROM diagnostic_runs dr
        LEFT JOIN diagnostic_results dr_res ON dr.id = dr_res.run_id
        WHERE dr.id = $1
        """,
        run_id
    )

    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    return dict(run)

@app.delete("/api/runs/{run_id}")
async def delete_run(run_id: str):
    """Delete a diagnostic run and all associated data"""

    # Check if run exists
    run = await db.fetchrow(
        "SELECT id FROM diagnostic_runs WHERE id = $1",
        run_id
    )

    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    # Delete associated data (cascade will handle most)
    await db.execute("DELETE FROM diagnostic_runs WHERE id = $1", run_id)

    return {"message": "Run deleted successfully"}

@app.get("/api/runs/{run_id}/status")
async def get_run_status(run_id: str):
    """Get current status of a diagnostic run"""

    status = await db.fetchrow(
        "SELECT status, error FROM diagnostic_runs WHERE id = $1",
        run_id
    )

    if not status:
        raise HTTPException(status_code=404, detail="Run not found")

    return dict(status)

@app.get("/api/runs/{run_id}/results")
async def get_run_results(run_id: str):
    """Get detailed results for a completed diagnostic run"""
    
    # Check if run exists and is completed
    run = await db.fetchrow(
        "SELECT status FROM diagnostic_runs WHERE id = $1",
        run_id
    )
    
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    if run['status'] != 'completed':
        raise HTTPException(status_code=400, detail=f"Run is {run['status']}, not completed")
    
    # Fetch all related data
    results = await db.fetchrow(
        "SELECT results, file_paths FROM diagnostic_results WHERE run_id = $1",
        run_id
    )
    
    metrics = await db.fetch(
        "SELECT * FROM collapse_metrics WHERE run_id = $1",
        run_id
    )
    
    patterns = await db.fetch(
        "SELECT * FROM rfi_metrics WHERE run_id = $1",
        run_id
    )
    
    if not results:
        raise HTTPException(status_code=404, detail="Results not found")
    
    # Safely parse JSON fields
    parsed_results = {}
    parsed_file_paths = {}
    
    try:
        parsed_results = json.loads(results['results']) if results['results'] else {}
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Error parsing results JSON: {e}")
        parsed_results = {}
    
    try:
        parsed_file_paths = json.loads(results['file_paths']) if results['file_paths'] else {}
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Error parsing file_paths JSON: {e}")
        parsed_file_paths = {}
    
    return {
        "run_id": run_id,
        "results": parsed_results,
        "file_paths": parsed_file_paths,
        "metrics": [dict(m) for m in metrics] if metrics else [],
        "patterns": [dict(p) for p in patterns] if patterns else []
    }

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    
    total_runs = await db.fetchval(
        "SELECT COUNT(*) FROM diagnostic_runs"
    )
    
    completed_runs = await db.fetchval(
        "SELECT COUNT(*) FROM diagnostic_runs WHERE status = 'completed'"
    )
    
    failed_runs = await db.fetchval(
        "SELECT COUNT(*) FROM diagnostic_runs WHERE status = 'failed'"
    )
    
    pending_runs = await db.fetchval(
        "SELECT COUNT(*) FROM diagnostic_runs WHERE status IN ('pending', 'running')"
    )
    
    return {
        "total_runs": total_runs or 0,
        "completed_runs": completed_runs or 0,
        "failed_runs": failed_runs or 0,
        "pending_runs": pending_runs or 0,
        "success_rate": round((completed_runs / total_runs * 100) if total_runs else 0, 2)
    }

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

    # Sanitize results to handle NaN/Inf values
    results = sanitize_for_json(results)

    # Store full results JSON (serialize to string for asyncpg)
    await db.execute(
        """
        INSERT INTO diagnostic_results (run_id, results, file_paths)
        VALUES ($1, $2, $3)
        """,
        run_id, json.dumps(results), json.dumps(results.get('_files'))
    )

    # Extract and store collapse metrics
    try:
        meff = results.get('meff', {})
        if meff:
            await db.execute(
                """
                INSERT INTO collapse_metrics (
                    run_id, meff_liji, meff_min, meff_entropy,
                    m_total, m_effective, collapse_ratio,
                    eigenvalues, top_10_eigenvalues
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                run_id,
                meff.get('meff_liji'),
                meff.get('meff_min'),
                meff.get('meff_entropy'),
                meff.get('m_total'),
                meff.get('m_effective'),
                meff.get('collapse_ratio'),
                json.dumps(meff.get('eigenvalues')),
                json.dumps(meff.get('top_10_eigenvalues'))
            )
    except Exception as e:
        print(f"Warning: Could not store collapse_metrics: {e}")

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
    try:
        rfi = results.get('rfi', {})
        if rfi:
            await db.execute(
                """
                INSERT INTO rfi_metrics (
                    run_id, rfi, modularity_q, homophily_h, lambda_2,
                    n_communities, n_components, density, transitivity, avg_degree
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                run_id,
                rfi.get('rfi'),
                rfi.get('modularity_Q'),
                rfi.get('homophily_h'),
                rfi.get('lambda_2'),
                rfi.get('n_communities'),
                rfi.get('n_components'),
                rfi.get('density'),
                rfi.get('transitivity'),
                rfi.get('avg_degree')
            )
    except Exception as e:
        print(f"Warning: Could not store rfi_metrics: {e}")

    # Store residue profile
    try:
        residue = results.get('residue_profile', {})
        if residue:
            await db.execute(
                """
                INSERT INTO residue_profiles (
                    run_id, residue_mean, residue_max, residue_std,
                    residue_median, residue_level, note
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                run_id,
                residue.get('residue_mean'),
                residue.get('residue_max'),
                residue.get('residue_std'),
                residue.get('residue_median'),
                residue.get('residue_level'),
                residue.get('note')
            )
    except Exception as e:
        print(f"Warning: Could not store residue_profiles: {e}")

    # Store shape classification
    try:
        shape = results.get('shape', {})
        if shape:
            await db.execute(
                """
                INSERT INTO shape_classifications (
                    run_id, shape, archetype, glyph,
                    degree_cv, degree_mean, degree_std, degree_max, assortativity
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                run_id,
                shape.get('shape'),
                shape.get('archetype'),
                shape.get('glyph'),
                shape.get('degree_cv'),
                shape.get('degree_mean'),
                shape.get('degree_std'),
                shape.get('degree_max'),
                shape.get('assortativity')
            )
    except Exception as e:
        print(f"Warning: Could not store shape_classifications: {e}")

    # Store lattice position
    try:
        lattice = results.get('lattice', {})
        if lattice:
            await db.execute(
                """
                INSERT INTO lattice_positions (
                    run_id, lattice_position, status, recommended_protocol,
                    collapse_potential, traversal_strategy
                ) VALUES ($1, $2, $3, $4, $5, $6)
                """,
                run_id,
                lattice.get('lattice_position'),
                lattice.get('status'),
                lattice.get('recommended_protocol'),
                lattice.get('collapse_potential'),
                lattice.get('traversal_strategy')
            )
    except Exception as e:
        print(f"Warning: Could not store lattice_positions: {e}")

    # Store interpretation
    try:
        interpretation = results.get('interpretation', {})
        if interpretation:
            await db.execute(
                """
                INSERT INTO interpretations (
                    run_id, coherence_direction, dominant_mode,
                    distortion_core, narrative_state
                ) VALUES ($1, $2, $3, $4, $5)
                """,
                run_id,
                interpretation.get('coherence_direction'),
                interpretation.get('dominant_mode'),
                json.dumps(interpretation.get('distortion_core')),
                interpretation.get('narrative_state')
            )
    except Exception as e:
        print(f"Warning: Could not store interpretations: {e}")

# === WEBSOCKET FOR LIVE UPDATES ===

@app.websocket("/ws/runs/{run_id}/live")
async def websocket_live_updates(websocket: WebSocket, run_id: str):
    """WebSocket for real-time diagnostic progress updates"""

    await websocket.accept()

    try:
        while True:
            # Check run status
            status = await db.fetchrow(
                "SELECT status, error FROM diagnostic_runs WHERE id = $1",
                run_id
            )

            if not status:
                await websocket.send_json({"error": "Run not found"})
                break

            await websocket.send_json({
                "status": status['status'],
                "error": status['error']
            })

            if status['status'] in ['completed', 'failed']:
                break

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        pass

# === HEALTH CHECK ===

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/runs/{run_id}/topology-graph", response_model=TopologyGraphResponse)
async def get_topology_graph(run_id: str):
    """Get topology graph data for visualization"""

    # Check if run exists and is completed
    run = await db.fetchrow(
        "SELECT status, data_path FROM diagnostic_runs WHERE id = $1",
        run_id
    )

    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    if run['status'] != 'completed':
        raise HTTPException(status_code=400, detail=f"Run is {run['status']}, not completed")

    # Fetch results
    results = await db.fetchrow(
        "SELECT results FROM diagnostic_results WHERE run_id = $1",
        run_id
    )

    if not results:
        raise HTTPException(status_code=404, detail="Results not found")

    data = json.loads(results['results'])

    # Extract RFI data
    rfi = data.get('rfi', {})
    if not rfi:
        raise HTTPException(status_code=404, detail="Topology data not available for this run")

    # Try to get stored adjacency matrix first
    adjacency_matrix = rfi.get('adjacency_matrix', [])
    community_mapping = rfi.get('community_mapping', {})

    # If no stored adjacency matrix, try to load from result files
    if not adjacency_matrix:
        # Check if there's metadata about file paths
        file_paths = data.get('_files', {})
        
        # Try to load correlation matrix and convert to adjacency
        # This is a fallback - we'll create a simple topology from available metrics
        n_nodes = rfi.get('n_nodes', 0)
        
        if n_nodes == 0 or n_nodes == 1:
            # Not enough nodes for a meaningful graph
            raise HTTPException(
                status_code=404, 
                detail="Topology graph requires at least 2 nodes. This dataset may not have sufficient relational structure."
            )
        
        # Create a minimal graph structure from available data
        # Build nodes based on feature count (from metadata if available)
        metadata = data.get('metadata', {})
        n_features = metadata.get('n_features', n_nodes)
        
        nodes = []
        links = []
        
        # Create nodes (one per feature)
        for i in range(n_features):
            nodes.append({
                "id": f"feature_{i}",
                "degree": 0,  # Will be calculated
                "community": 0  # No community detection without adjacency matrix
            })
        
        # Note: Without adjacency matrix, we can't build meaningful links
        # Return empty graph with explanation
        return {
            "nodes": nodes,
            "links": links,
            "metadata": {
                "node_count": len(nodes),
                "link_count": 0,
                "density": 0,
                "community_count": 1,
                "note": "Adjacency matrix not available. Graph structure cannot be visualized. Run diagnostic with skip_visuals=False to generate full topology data."
            }
        }

    # Build nodes and links from stored adjacency matrix
    nodes = []
    links = []
    n = len(adjacency_matrix)

    # Calculate degrees and build nodes
    for i in range(n):
        degree = sum(1 for j in range(n) if adjacency_matrix[i][j] != 0)
        community = community_mapping.get(str(i), 0) # Default to 0 if not found
        nodes.append({
            "id": f"feature_{i}",
            "degree": degree,
            "community": community
        })

    # Build links (upper triangle to avoid duplicates)
    for i in range(n):
        for j in range(i + 1, n):
            weight = adjacency_matrix[i][j]
            if weight != 0:
                links.append({
                    "source": f"feature_{i}",
                    "target": f"feature_{j}",
                    "weight": float(weight)
                })

    # Calculate metadata
    metadata = {
        "node_count": len(nodes),
        "link_count": len(links),
        "density": len(links) / (n * (n - 1) / 2) if n > 1 else 0,
        "community_count": len(set(node['community'] for node in nodes))
    }

    return {
        "nodes": nodes,
        "links": links,
        "metadata": metadata
    }

@app.get("/api/runs/{run_id}/collapse-features")
async def get_collapse_features(run_id: str):
    """Get per-feature collapse contribution data for visualization"""

    # Check if run exists and is completed
    run = await db.fetchrow(
        "SELECT status, data_path FROM diagnostic_runs WHERE id = $1",
        run_id
    )

    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    if run['status'] != 'completed':
        raise HTTPException(status_code=400, detail=f"Run is {run['status']}, not completed")

    # Fetch results
    results = await db.fetchrow(
        "SELECT results FROM diagnostic_results WHERE run_id = $1",
        run_id
    )

    if not results:
        raise HTTPException(status_code=404, detail="Results not found")

    data = json.loads(results['results'])

    # Extract collapse map from results
    collapse_map_raw = data.get('collapse_map', {})
    
    if not collapse_map_raw or collapse_map_raw.get('status') != 'computed':
        # Fallback: try to build from eigenvalues
        eigenvalues = data.get('meff', {}).get('eigenvalues', [])
        if not eigenvalues:
            raise HTTPException(status_code=404, detail="Collapse map data not available for this run")
        
        # Build collapse map from eigenvalues (simplified)
        total = sum(eigenvalues)
        collapse_map = [
            {
                "feature_index": i,
                "collapse_score": ev,
                "contribution_pct": (ev / total * 100) if total > 0 else 0
            }
            for i, ev in enumerate(eigenvalues)
        ]
        # Sort by contribution descending
        collapse_map.sort(key=lambda x: x['contribution_pct'], reverse=True)
    else:
        # Use the computed collapse map
        top_features = collapse_map_raw.get('top_features', [])
        scores = collapse_map_raw.get('scores', [])
        
        # Combine into list of dicts
        collapse_map = []
        for idx, (feat_idx, score) in enumerate(zip(top_features, scores)):
            # Calculate contribution percentage (normalized by sum of all scores)
            total_score = sum(scores)
            collapse_map.append({
                "feature_index": feat_idx,
                "collapse_score": score,
                "contribution_pct": (score / total_score * 100) if total_score > 0 else 0
            })

    # Extract metadata
    meff_data = data.get('meff', {})
    metadata = {
        "m_total": meff_data.get('m_total', 0),
        "m_effective": meff_data.get('m_effective', 0),
        "collapse_ratio": meff_data.get('collapse_ratio', 0),
        "meff_liji": meff_data.get('meff_liji', 0)
    }

    return {
        "data": collapse_map,
        "metadata": metadata
    }

# === FILE MANAGEMENT ENDPOINTS ===

ALLOWED_EXTENSIONS = {'.csv', '.json', '.xlsx', '.xls', '.tsv', '.txt'}
UPLOAD_DIR = Path("/tmp/dashboard_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class FileUploadResponse(BaseModel):
    success: bool
    file_path: Optional[str] = None
    filename: Optional[str] = None
    error: Optional[str] = None

class FileValidationResponse(BaseModel):
    valid: bool
    path: str
    error: Optional[str] = None
    file_type: Optional[str] = None
    size: Optional[int] = None

class FolderBrowseResponse(BaseModel):
    path: str
    files: List[dict]
    error: Optional[str] = None

@app.post("/api/files/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a file for diagnostic processing - supports large files up to 500MB"""
    
    # Validate filename exists
    if not file.filename:
        return FileUploadResponse(
            success=False,
            error="No filename provided"
        )
    
    # Validate file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        return FileUploadResponse(
            success=False,
            error=f"File type {file_extension} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Create unique filename to avoid conflicts
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename
    
    try:
        # Save uploaded file in chunks for large file support
        chunk_size = 1024 * 1024  # 1MB chunks
        total_size = 0
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(chunk_size):
                total_size += len(chunk)
                # Check if file exceeds max size
                if total_size > MAX_UPLOAD_SIZE:
                    # Clean up the partial file
                    file_path.unlink()
                    return FileUploadResponse(
                        success=False,
                        error=f"File size exceeds maximum allowed size of {MAX_UPLOAD_SIZE / (1024 * 1024):.0f}MB"
                    )
                buffer.write(chunk)
        
        # Get file size
        file_size = file_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        
        return FileUploadResponse(
            success=True,
            file_path=str(file_path),
            filename=f"{file.filename} ({file_size_mb:.2f} MB)"
        )
    except Exception as e:
        # Clean up partial file on error
        if file_path.exists():
            file_path.unlink()
        return FileUploadResponse(
            success=False,
            error=f"Failed to save file: {str(e)}"
        )

@app.post("/api/files/upload-multiple")
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """Upload multiple files for diagnostic processing"""
    
    results = []
    for file in files:
        if not file.filename:
            results.append({
                "filename": "unknown",
                "success": False,
                "error": "No filename provided"
            })
            continue
        
        # Validate file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": f"File type {file_extension} not allowed"
            })
            continue
        
        # Create unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename
        
        try:
            # Save file in chunks
            chunk_size = 1024 * 1024  # 1MB chunks
            total_size = 0
            with open(file_path, "wb") as buffer:
                while chunk := await file.read(chunk_size):
                    total_size += len(chunk)
                    # Check if file exceeds max size
                    if total_size > MAX_UPLOAD_SIZE:
                        file_path.unlink()
                        results.append({
                            "filename": file.filename,
                            "success": False,
                            "error": f"File exceeds {MAX_UPLOAD_SIZE / (1024 * 1024):.0f}MB limit"
                        })
                        break
                    buffer.write(chunk)
                else:
                    # File completed successfully
                    file_size = file_path.stat().st_size
                    file_size_mb = file_size / (1024 * 1024)
                    
                    results.append({
                        "filename": file.filename,
                        "success": True,
                        "file_path": str(file_path),
                        "size_mb": round(file_size_mb, 2)
                    })
        except Exception as e:
            if file_path.exists():
                file_path.unlink()
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e)
            })
    
    return {
        "total": len(files),
        "successful": sum(1 for r in results if r.get("success")),
        "failed": sum(1 for r in results if not r.get("success")),
        "results": results
    }

@app.get("/api/files/validate", response_model=FileValidationResponse)
async def validate_file_path(path: str = Query(..., description="File path to validate")):
    """Validate if a file path exists and is compatible"""
    
    try:
        file_path = Path(path)
        
        # Check if file exists
        if not file_path.exists():
            return FileValidationResponse(
                valid=False,
                path=path,
                error="File does not exist"
            )
        
        # Check if it's a file (not directory)
        if not file_path.is_file():
            return FileValidationResponse(
                valid=False,
                path=path,
                error="Path is not a file"
            )
        
        # Check file extension
        file_extension = file_path.suffix.lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            return FileValidationResponse(
                valid=False,
                path=path,
                error=f"File type {file_extension} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Get file size
        file_size = file_path.stat().st_size
        
        return FileValidationResponse(
            valid=True,
            path=path,
            file_type=file_extension,
            size=file_size
        )
        
    except Exception as e:
        return FileValidationResponse(
            valid=False,
            path=path,
            error=f"Error validating path: {str(e)}"
        )

@app.get("/api/files/browse", response_model=FolderBrowseResponse)
async def browse_folder(path: str = Query("/", description="Folder path to browse")):
    """Browse folder contents and find compatible files"""
    
    try:
        folder_path = Path(path)
        
        # Check if path exists and is directory
        if not folder_path.exists():
            return FolderBrowseResponse(
                path=path,
                files=[],
                error="Folder does not exist"
            )
        
        if not folder_path.is_dir():
            return FolderBrowseResponse(
                path=path,
                files=[],
                error="Path is not a directory"
            )
        
        # Get directory contents
        contents = []
        
        # List all files and directories
        for item in folder_path.iterdir():
            item_info = {
                "name": item.name,
                "path": str(item),
                "type": "folder" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else None,
                "extension": item.suffix.lower() if item.is_file() else None,
                "compatible": item.is_file() and item.suffix.lower() in ALLOWED_EXTENSIONS
            }
            contents.append(item_info)
        
        # Sort: folders first, then files by name
        contents.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))
        
        return FolderBrowseResponse(
            path=path,
            files=contents
        )
        
    except Exception as e:
        return FolderBrowseResponse(
            path=path,
            files=[],
            error=f"Error browsing folder: {str(e)}"
        )

@app.get("/api/analytics/lattice-points", response_model=LatticePointsResponse)
async def get_lattice_points():
    """Get lattice points for all completed runs"""

    points = await db.fetch(
        """
        SELECT
            dr.id as run_id,
            cm.collapse_ratio,
            rm.rfi,
            'Unknown' as shape,
            dr.status,
            dr.created_at
        FROM diagnostic_runs dr
        JOIN collapse_metrics cm ON dr.id = cm.run_id
        JOIN rfi_metrics rm ON dr.id = rm.run_id
        WHERE dr.status = 'completed'
        ORDER BY dr.created_at DESC
        """
    )

    result = {
        "points": [
            {
                "run_id": str(p['run_id']),
                "collapse_ratio": float(p['collapse_ratio']) if p['collapse_ratio'] is not None else 0.0,
                "rfi": float(p['rfi']) if p['rfi'] is not None else 0.0,
                "shape": p['shape'] or 'Unknown',
                "status": p['status'] or 'unknown',
                "created_at": (
                    p['created_at'].isoformat() if hasattr(p['created_at'], "isoformat")
                    else str(p['created_at'])
                )
            }
            for p in points
        ]
    }
    return result

@app.get("/api/analytics/collapse-map", response_model=CollapseMapResponse)
async def get_collapse_map():
    """Get collapse pattern data for heatmap visualization"""

    patterns = await db.fetch(
        """
        SELECT
            dr.id as run_id,
            cm.collapse_ratio,
            rm.rfi,
            rm.modularity_q,
            rm.homophily_h,
            rm.lambda_2,
            rm.transitivity,
            dr.status
        FROM diagnostic_runs dr
        JOIN collapse_metrics cm ON dr.id = cm.run_id
        JOIN rfi_metrics rm ON dr.id = rm.run_id
        WHERE dr.status = 'completed'
        ORDER BY dr.created_at DESC
        """
    )

    result = {
        "patterns": [
            {
                "run_id": str(p['run_id']),
                "collapse_ratio": float(p['collapse_ratio']) if p['collapse_ratio'] else 0.0,
                "rfi": float(p['rfi']) if p['rfi'] else 0.0,
                "stability_score": float(p['modularity_q']) if p['modularity_q'] else 0.0,
                "coherence_index": float(p['homophily_h']) if p['homophily_h'] else 0.0,
                "resonance_frequency": float(p['lambda_2']) if p['lambda_2'] else 0.0,
                "harmonics": [float(p['transitivity']) if p['transitivity'] else 0.0]
            }
            for p in patterns
        ]
    }
    return result

# === MAIN ===

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )