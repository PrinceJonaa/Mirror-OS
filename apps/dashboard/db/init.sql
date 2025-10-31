-- Database initialization script for Truth-Distortion Dashboard
-- Run this against a fresh PostgreSQL database

-- Enable required extensions
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

-- DuckDB analytical views
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