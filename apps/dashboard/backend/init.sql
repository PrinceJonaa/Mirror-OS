-- Enable required extensions
-- CREATE EXTENSION IF NOT EXISTS vector; -- Temporarily disabled for testing
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Diagnostic Runs Table
CREATE TABLE diagnostic_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    -- API-exposed columns
    data_path TEXT,
    data_type VARCHAR(50),
    corr_method VARCHAR(50),
    adj_threshold REAL,
    compute_null BOOLEAN,
    n_permutations INTEGER,
    use_louvain BOOLEAN,
    skip_visuals BOOLEAN,
    seed INTEGER,
    config JSONB,
    error TEXT
);

-- Metrics Table
CREATE TABLE diagnostic_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES diagnostic_runs(id) ON DELETE CASCADE,
    metric_name VARCHAR(255) NOT NULL,
    metric_value NUMERIC,
    metric_type VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Patterns Table
CREATE TABLE diagnostic_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES diagnostic_runs(id) ON DELETE CASCADE,
    pattern_type VARCHAR(100),
    pattern_data JSONB,
    confidence_score NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Embeddings Table for Semantic Search (temporarily using JSONB instead of vector)
CREATE TABLE diagnostic_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES diagnostic_runs(id) ON DELETE CASCADE,
    content_type VARCHAR(100),
    content TEXT,
    embedding JSONB, -- Temporarily using JSONB instead of vector for testing
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Convergence History Table
CREATE TABLE convergence_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES diagnostic_runs(id) ON DELETE CASCADE,
    iteration INTEGER,
    convergence_score NUMERIC,
    distortion_metrics JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- System State Snapshots
CREATE TABLE system_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES diagnostic_runs(id) ON DELETE CASCADE,
    snapshot_type VARCHAR(100),
    snapshot_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for Performance
CREATE INDEX idx_diagnostic_runs_status ON diagnostic_runs(status);
CREATE INDEX idx_diagnostic_runs_created_at ON diagnostic_runs(created_at DESC);
CREATE INDEX idx_diagnostic_metrics_run_id ON diagnostic_metrics(run_id);
CREATE INDEX idx_diagnostic_patterns_run_id ON diagnostic_patterns(run_id);
CREATE INDEX idx_diagnostic_embeddings_run_id ON diagnostic_embeddings(run_id);

-- Diagnostic Results table (stores full JSON output)
CREATE TABLE diagnostic_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES diagnostic_runs(id) ON DELETE CASCADE,
    results JSONB,
    file_paths JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Collapse metrics, RFI metrics and other derived tables referenced by code
CREATE TABLE collapse_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES diagnostic_runs(id) ON DELETE CASCADE,
    meff_liji NUMERIC,
    meff_min NUMERIC,
    meff_entropy NUMERIC,
    m_total NUMERIC,
    m_effective NUMERIC,
    collapse_ratio NUMERIC,
    eigenvalues JSONB,
    top_10_eigenvalues JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE rfi_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES diagnostic_runs(id) ON DELETE CASCADE,
    rfi NUMERIC,
    modularity_q NUMERIC,
    homophily_h NUMERIC,
    lambda_2 NUMERIC,
    n_communities INTEGER,
    n_components INTEGER,
    density NUMERIC,
    transitivity NUMERIC,
    avg_degree NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE residue_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES diagnostic_runs(id) ON DELETE CASCADE,
    residue_mean NUMERIC,
    residue_max NUMERIC,
    residue_std NUMERIC,
    residue_median NUMERIC,
    residue_level VARCHAR(50),
    note TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE shape_classifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES diagnostic_runs(id) ON DELETE CASCADE,
    shape VARCHAR(100),
    archetype VARCHAR(100),
    glyph VARCHAR(100),
    degree_cv NUMERIC,
    degree_mean NUMERIC,
    degree_std NUMERIC,
    degree_max NUMERIC,
    assortativity NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE lattice_positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES diagnostic_runs(id) ON DELETE CASCADE,
    lattice_position VARCHAR(255),
    status VARCHAR(100),
    recommended_protocol TEXT,
    collapse_potential NUMERIC,
    traversal_strategy TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE interpretations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES diagnostic_runs(id) ON DELETE CASCADE,
    coherence_direction VARCHAR(255),
    dominant_mode VARCHAR(255),
    distortion_core JSONB,
    narrative_state TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Vector Search Indexes (temporarily disabled)
-- CREATE INDEX idx_embeddings_vector ON diagnostic_embeddings USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_convergence_history_run_id_iteration ON convergence_history(run_id, iteration);

-- Analytical Views
CREATE VIEW diagnostic_run_summary AS
SELECT
    dr.id,
    dr.name,
    dr.status,
    dr.created_at,
    dr.completed_at,
    COUNT(dm.id) as metric_count,
    COUNT(dp.id) as pattern_count,
    AVG(dm.metric_value) as avg_metric_value
FROM diagnostic_runs dr
LEFT JOIN diagnostic_metrics dm ON dr.id = dm.run_id
LEFT JOIN diagnostic_patterns dp ON dr.id = dp.run_id
GROUP BY dr.id, dr.name, dr.status, dr.created_at, dr.completed_at;

CREATE VIEW latest_convergence_scores AS
SELECT DISTINCT ON (run_id)
    run_id,
    iteration,
    convergence_score,
    distortion_metrics
FROM convergence_history
ORDER BY run_id, iteration DESC;

-- Permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dashboard_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dashboard_user;