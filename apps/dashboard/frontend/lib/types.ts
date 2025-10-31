// API Types
export interface DiagnosticRun {
  id: string;
  name?: string;
  description?: string;
  data_path?: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  created_at: string;
  started_at?: string;
  completed_at?: string;
  config: DiagnosticConfig;
  error?: string;
  results?: DiagnosticResults;
}

export interface DiagnosticConfig {
  [key: string]: unknown;
}

export interface DiagnosticResults {
  run_id: string;
  collapse_metrics: CollapseMetric[];
  rfi_metrics: RFIMetric[];
}

export interface CollapseMetric {
  collapse_type: string;
  magnitude: number;
  severity: number;
  [key: string]: unknown;
}

export interface RFIMetric {
  field_name: string;
  fitness_score: number;
  coherence_score: number;
  [key: string]: unknown;
}

export interface DashboardStats {
  total_runs: number;
  completed_runs: number;
  failed_runs: number;
  pending_runs: number;
  success_rate: number;
}

export interface CreateRunRequest {
  name: string;
  description?: string;
  data_path: string;
  data_type?: string;
  corr_method?: string;
  adj_threshold?: number;
  compute_null?: boolean;
  n_permutations?: number;
  use_louvain?: boolean;
  skip_visuals?: boolean;
  seed?: number;
}
