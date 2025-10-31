/**
 * Frontend Test Fixtures
 * 
 * Sample data for testing visualization components without backend.
 * Includes small, medium, and large datasets for different test scenarios.
 */

// ==================== TOPOLOGY DATA ====================

/**
 * Small topology graph (5 nodes, 2 communities).
 * Good for unit tests and quick rendering validation.
 */
export const smallTopologyData = {
  nodes: [
    { id: 'A', degree: 3, community: 0 },
    { id: 'B', degree: 2, community: 0 },
    { id: 'C', degree: 2, community: 0 },
    { id: 'D', degree: 2, community: 1 },
    { id: 'E', degree: 1, community: 1 }
  ],
  links: [
    { source: 'A', target: 'B', weight: 0.9 },
    { source: 'A', target: 'C', weight: 0.8 },
    { source: 'B', target: 'C', weight: 0.7 },
    { source: 'D', target: 'E', weight: 0.6 }
  ],
  metrics: {
    node_count: 5,
    edge_count: 4,
    avg_degree: 2.0,
    modularity: 0.5
  }
};

/**
 * Medium topology graph (20 nodes, 3 communities).
 * Good for testing layout algorithms and community detection.
 */
export const mediumTopologyData = {
  nodes: Array.from({ length: 20 }, (_, i) => ({
    id: `Node_${i}`,
    degree: Math.floor(Math.random() * 5) + 2,
    community: Math.floor(i / 7)
  })),
  links: Array.from({ length: 35 }, (_, i) => ({
    source: `Node_${i % 20}`,
    target: `Node_${(i + 1 + Math.floor(Math.random() * 5)) % 20}`,
    weight: 0.5 + Math.random() * 0.5
  })),
  metrics: {
    node_count: 20,
    edge_count: 35,
    avg_degree: 3.5,
    modularity: 0.42
  }
};

/**
 * Large topology graph (100 nodes, 5 communities).
 * Good for performance testing and stress testing visualizations.
 */
export const largeTopologyData = {
  nodes: Array.from({ length: 100 }, (_, i) => ({
    id: `Node_${i}`,
    degree: Math.floor(Math.random() * 10) + 1,
    community: Math.floor(i / 20)
  })),
  links: Array.from({ length: 200 }, (_, i) => {
    const source = Math.floor(Math.random() * 100);
    let target = Math.floor(Math.random() * 100);
    // Avoid self-loops
    while (target === source) {
      target = Math.floor(Math.random() * 100);
    }
    return {
      source: `Node_${source}`,
      target: `Node_${target}`,
      weight: 0.3 + Math.random() * 0.7
    };
  }),
  metrics: {
    node_count: 100,
    edge_count: 200,
    avg_degree: 4.0,
    modularity: 0.38
  }
};

/**
 * Empty topology data.
 * Good for testing empty state handling.
 */
export const emptyTopologyData = {
  nodes: [],
  links: [],
  metrics: {
    node_count: 0,
    edge_count: 0,
    avg_degree: 0,
    modularity: 0
  }
};

// ==================== COLLAPSE FEATURES ====================

/**
 * Sample collapse features (top 15 ranked).
 * Realistic distribution following power law.
 */
export const sampleCollapseFeatures = [
  {
    feature_name: 'Gene_BRCA1',
    feature_index: 0,
    contribution_percent: 28.5,
    collapse_score: 0.95,
    cumulative_contribution: 28.5,
    rank: 1
  },
  {
    feature_name: 'Gene_TP53',
    feature_index: 1,
    contribution_percent: 18.2,
    collapse_score: 0.88,
    cumulative_contribution: 46.7,
    rank: 2
  },
  {
    feature_name: 'Gene_EGFR',
    feature_index: 2,
    contribution_percent: 12.3,
    collapse_score: 0.79,
    cumulative_contribution: 59.0,
    rank: 3
  },
  {
    feature_name: 'Gene_MYC',
    feature_index: 3,
    contribution_percent: 9.1,
    collapse_score: 0.72,
    cumulative_contribution: 68.1,
    rank: 4
  },
  {
    feature_name: 'Gene_KRAS',
    feature_index: 4,
    contribution_percent: 6.8,
    collapse_score: 0.65,
    cumulative_contribution: 74.9,
    rank: 5
  },
  {
    feature_name: 'Gene_PTEN',
    feature_index: 5,
    contribution_percent: 5.2,
    collapse_score: 0.58,
    cumulative_contribution: 80.1,
    rank: 6
  },
  {
    feature_name: 'Gene_RB1',
    feature_index: 6,
    contribution_percent: 4.1,
    collapse_score: 0.51,
    cumulative_contribution: 84.2,
    rank: 7
  },
  {
    feature_name: 'Gene_APC',
    feature_index: 7,
    contribution_percent: 3.3,
    collapse_score: 0.45,
    cumulative_contribution: 87.5,
    rank: 8
  },
  {
    feature_name: 'Gene_VHL',
    feature_index: 8,
    contribution_percent: 2.8,
    collapse_score: 0.39,
    cumulative_contribution: 90.3,
    rank: 9
  },
  {
    feature_name: 'Gene_CDH1',
    feature_index: 9,
    contribution_percent: 2.2,
    collapse_score: 0.34,
    cumulative_contribution: 92.5,
    rank: 10
  },
  {
    feature_name: 'Gene_STK11',
    feature_index: 10,
    contribution_percent: 1.8,
    collapse_score: 0.29,
    cumulative_contribution: 94.3,
    rank: 11
  },
  {
    feature_name: 'Gene_SMAD4',
    feature_index: 11,
    contribution_percent: 1.5,
    collapse_score: 0.24,
    cumulative_contribution: 95.8,
    rank: 12
  },
  {
    feature_name: 'Gene_CDKN2A',
    feature_index: 12,
    contribution_percent: 1.2,
    collapse_score: 0.20,
    cumulative_contribution: 97.0,
    rank: 13
  },
  {
    feature_name: 'Gene_ATM',
    feature_index: 13,
    contribution_percent: 0.9,
    collapse_score: 0.16,
    cumulative_contribution: 97.9,
    rank: 14
  },
  {
    feature_name: 'Gene_NF1',
    feature_index: 14,
    contribution_percent: 0.7,
    collapse_score: 0.12,
    cumulative_contribution: 98.6,
    rank: 15
  }
];

/**
 * Empty collapse features.
 * Good for testing empty state handling.
 */
export const emptyCollapseFeatures: typeof sampleCollapseFeatures = [];

// ==================== LATTICE POINTS ====================

/**
 * Sample lattice points distributed across all zones.
 * Includes points in Truth Lattice, Irreducible Distortion, 
 * Coherent Structure, and Chaotic Domain.
 */
export const sampleLatticePoints = [
  // Truth Lattice (high RFI, low collapse)
  {
    run_id: 'run-001',
    run_name: 'Optimal Run A',
    rfi: 0.85,
    collapse_ratio: 0.25,
    timestamp: '2025-01-20T10:00:00Z',
    lattice_zone: 'Truth Lattice',
    shape: 'circle',
    status: 'completed'
  },
  {
    run_id: 'run-002',
    run_name: 'Optimal Run B',
    rfi: 0.78,
    collapse_ratio: 0.30,
    timestamp: '2025-01-20T11:00:00Z',
    lattice_zone: 'Truth Lattice',
    shape: 'circle',
    status: 'completed'
  },
  // Coherent Structure (high RFI, high collapse)
  {
    run_id: 'run-003',
    run_name: 'Redundant System',
    rfi: 0.75,
    collapse_ratio: 0.70,
    timestamp: '2025-01-20T12:00:00Z',
    lattice_zone: 'Coherent Structure',
    shape: 'square',
    status: 'completed'
  },
  {
    run_id: 'run-004',
    run_name: 'Over-fitted Model',
    rfi: 0.82,
    collapse_ratio: 0.65,
    timestamp: '2025-01-20T13:00:00Z',
    lattice_zone: 'Coherent Structure',
    shape: 'square',
    status: 'completed'
  },
  // Irreducible Distortion (low RFI, low collapse)
  {
    run_id: 'run-005',
    run_name: 'Noisy Data',
    rfi: 0.35,
    collapse_ratio: 0.28,
    timestamp: '2025-01-20T14:00:00Z',
    lattice_zone: 'Irreducible Distortion',
    shape: 'triangle',
    status: 'completed'
  },
  {
    run_id: 'run-006',
    run_name: 'Random Baseline',
    rfi: 0.40,
    collapse_ratio: 0.22,
    timestamp: '2025-01-20T15:00:00Z',
    lattice_zone: 'Irreducible Distortion',
    shape: 'triangle',
    status: 'completed'
  },
  // Chaotic Domain (low RFI, high collapse)
  {
    run_id: 'run-007',
    run_name: 'Failed Run A',
    rfi: 0.30,
    collapse_ratio: 0.75,
    timestamp: '2025-01-20T16:00:00Z',
    lattice_zone: 'Chaotic Domain',
    shape: 'cross',
    status: 'failed'
  },
  {
    run_id: 'run-008',
    run_name: 'Distorted System',
    rfi: 0.25,
    collapse_ratio: 0.80,
    timestamp: '2025-01-20T17:00:00Z',
    lattice_zone: 'Chaotic Domain',
    shape: 'cross',
    status: 'completed'
  },
  // Middle zone (moderate everything)
  {
    run_id: 'run-009',
    run_name: 'Average Run',
    rfi: 0.55,
    collapse_ratio: 0.50,
    timestamp: '2025-01-20T18:00:00Z',
    lattice_zone: 'Transition Zone',
    shape: 'circle',
    status: 'completed'
  },
  {
    run_id: 'run-010',
    run_name: 'Baseline Model',
    rfi: 0.60,
    collapse_ratio: 0.45,
    timestamp: '2025-01-20T19:00:00Z',
    lattice_zone: 'Transition Zone',
    shape: 'circle',
    status: 'completed'
  }
];

/**
 * Empty lattice points.
 * Good for testing empty state handling.
 */
export const emptyLatticePoints: typeof sampleLatticePoints = [];

// ==================== DIAGNOSTIC RUNS ====================

/**
 * Sample diagnostic runs with full metadata.
 */
export const sampleDiagnosticRuns = [
  {
    run_id: 'run-001',
    name: 'Lung Cancer Dataset A',
    status: 'completed',
    created_at: '2025-01-20T10:00:00Z',
    completed_at: '2025-01-20T10:05:32Z',
    config: {
      dataset: 'GSE12345',
      method: 'relational_meff',
      params: { threshold: 0.05 }
    },
    rfi: 0.85,
    collapse_ratio: 0.25
  },
  {
    run_id: 'run-002',
    name: 'Lung Cancer Dataset B',
    status: 'completed',
    created_at: '2025-01-20T11:00:00Z',
    completed_at: '2025-01-20T11:04:18Z',
    config: {
      dataset: 'GSE67890',
      method: 'relational_meff',
      params: { threshold: 0.01 }
    },
    rfi: 0.78,
    collapse_ratio: 0.30
  },
  {
    run_id: 'run-003',
    name: 'SAT Problem Test',
    status: 'running',
    created_at: '2025-01-20T12:00:00Z',
    completed_at: null,
    config: {
      dataset: 'sat_n100_k3',
      method: 'sat_meff',
      params: { clauses: 300 }
    },
    rfi: null,
    collapse_ratio: null
  },
  {
    run_id: 'run-004',
    name: 'Failed Pipeline Test',
    status: 'failed',
    created_at: '2025-01-20T13:00:00Z',
    completed_at: '2025-01-20T13:01:45Z',
    config: {
      dataset: 'invalid_data',
      method: 'relational_meff',
      params: {}
    },
    rfi: null,
    collapse_ratio: null,
    error: 'Invalid input format: missing required columns'
  }
];

// ==================== COMPARISON DATA ====================

/**
 * Pair of runs for comparison testing.
 */
export const comparisonPair = {
  run1: {
    id: 'run-001',
    name: 'Lung Cancer Dataset A',
    topology: smallTopologyData,
    collapse: sampleCollapseFeatures.slice(0, 10),
    rfi: 0.85,
    collapse_ratio: 0.25
  },
  run2: {
    id: 'run-002',
    name: 'Lung Cancer Dataset B',
    topology: {
      ...mediumTopologyData,
      nodes: mediumTopologyData.nodes.slice(0, 8),
      links: mediumTopologyData.links.slice(0, 12)
    },
    collapse: sampleCollapseFeatures.slice(0, 10).map(f => ({
      ...f,
      contribution_percent: f.contribution_percent * 0.8, // Different distribution
      collapse_score: f.collapse_score * 0.9
    })),
    rfi: 0.78,
    collapse_ratio: 0.30
  }
};

// ==================== UTILITY FUNCTIONS ====================

/**
 * Generate random topology data with specified size.
 */
export function generateRandomTopology(nodeCount: number, avgDegree: number = 3) {
  const nodes = Array.from({ length: nodeCount }, (_, i) => ({
    id: `Node_${i}`,
    degree: Math.floor(Math.random() * avgDegree * 2) + 1,
    community: Math.floor(Math.random() * Math.sqrt(nodeCount))
  }));

  const edgeCount = Math.floor((nodeCount * avgDegree) / 2);
  const links = Array.from({ length: edgeCount }, () => {
    const source = Math.floor(Math.random() * nodeCount);
    let target = Math.floor(Math.random() * nodeCount);
    while (target === source) {
      target = Math.floor(Math.random() * nodeCount);
    }
    return {
      source: `Node_${source}`,
      target: `Node_${target}`,
      weight: 0.3 + Math.random() * 0.7
    };
  });

  return { nodes, links, metrics: { node_count: nodeCount, edge_count: edgeCount, avg_degree: avgDegree, modularity: 0.4 } };
}

/**
 * Generate random collapse features with power law distribution.
 */
export function generateRandomCollapseFeatures(count: number = 15) {
  const features = [];
  let cumulative = 0;

  for (let i = 0; i < count; i++) {
    // Power law: first features contribute more
    const contribution = (100 / Math.pow(i + 1, 1.2));
    cumulative += contribution;
    
    features.push({
      feature_name: `Feature_${i}`,
      feature_index: i,
      contribution_percent: parseFloat(contribution.toFixed(2)),
      collapse_score: parseFloat((1 - i / count).toFixed(2)),
      cumulative_contribution: parseFloat(cumulative.toFixed(2)),
      rank: i + 1
    });
  }

  // Normalize to 100%
  const total = cumulative;
  features.forEach(f => {
    f.contribution_percent = parseFloat(((f.contribution_percent / total) * 100).toFixed(2));
    f.cumulative_contribution = parseFloat(((f.cumulative_contribution / total) * 100).toFixed(2));
  });

  return features;
}
