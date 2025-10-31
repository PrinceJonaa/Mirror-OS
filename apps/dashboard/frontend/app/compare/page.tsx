'use client';

import { useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, CheckCircle, XCircle, Clock, AlertCircle } from 'lucide-react';
import { fetchRun } from '@/lib/api';
import type { DiagnosticRun } from '@/lib/types';
import { format } from 'date-fns';
import TopologyGraphStatic from '@/components/visualizations/TopologyGraphStatic';
import CollapseMapCompact from '@/components/visualizations/CollapseMapCompact';

type TabType = 'metrics' | 'topologies' | 'collapse';

interface TopologyData {
  nodes: Array<{ id: string; degree: number; community: number }>;
  links: Array<{ source: string; target: string; weight: number }>;
}

interface CollapseFeature {
  feature_name: string;
  feature_index: number;
  contribution_percent: number;
  collapse_score: number;
  cumulative_contribution: number;
  rank: number;
}

interface CollapseDataItem {
  feature_index: number;
  collapse_score: number;
  contribution_pct: number;
}

export default function ComparePage() {
  const searchParams = useSearchParams();
  const idsParam = searchParams.get('ids');
  const ids = idsParam ? idsParam.split(',') : [];
  const idsKey = ids.join(','); // For useEffect dependency
  
  const [runs, setRuns] = useState<DiagnosticRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>('metrics');
  const [topologyData, setTopologyData] = useState<Record<string, TopologyData>>({});
  const [collapseData, setCollapseData] = useState<Record<string, CollapseFeature[]>>({});
  const [loadingVisualizations, setLoadingVisualizations] = useState(false);

  useEffect(() => {
    if (ids.length < 2) {
      setError('Please select at least 2 runs to compare');
      setLoading(false);
      return;
    }

    const loadRuns = async () => {
      try {
        const fetchedRuns = await Promise.all(ids.map(id => fetchRun(id)));
        setRuns(fetchedRuns);
      } catch (err) {
        setError('Failed to load runs for comparison');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadRuns();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [idsKey]); // idsKey encodes the ids array

  // Load visualization data when switching tabs
  useEffect(() => {
    if (activeTab === 'metrics' || runs.length === 0) return;

    const loadVisualizations = async () => {
      setLoadingVisualizations(true);
      
      if (activeTab === 'topologies') {
        const topologyPromises = runs.map(async (run) => {
          try {
            const response = await fetch(`http://localhost:8000/api/runs/${run.id}/topology-graph`);
            console.log(`Topology fetch for ${run.id}:`, response.status, response.statusText);
            if (response.ok) {
              const data = await response.json();
              console.log(`Topology data for ${run.id}:`, data);
              return { runId: run.id, data };
            } else {
              console.error(`Topology fetch failed for ${run.id}: ${response.status}`);
            }
          } catch (err) {
            console.error(`Failed to load topology for run ${run.id}:`, err);
          }
          return { runId: run.id, data: null };
        });
        
        const results = await Promise.all(topologyPromises);
        console.log('All topology results:', results);
        const topologyMap: Record<string, TopologyData> = {};
        results.forEach(({ runId, data }) => {
          if (data) topologyMap[runId] = data;
        });
        console.log('Topology map:', topologyMap);
        setTopologyData(topologyMap);
      } else if (activeTab === 'collapse') {
        const collapsePromises = runs.map(async (run) => {
          try {
            const response = await fetch(`http://localhost:8000/api/runs/${run.id}/collapse-features`);
            console.log(`Collapse fetch for ${run.id}:`, response.status, response.statusText);
            if (response.ok) {
              const result = await response.json();
              console.log(`Collapse data for ${run.id}:`, result);
              
              // Transform backend format to match CollapseMapCompact expected format
              const features = (result.data || []).map((item: CollapseDataItem, idx: number) => ({
                feature_name: `Feature ${item.feature_index}`,
                feature_index: item.feature_index,
                contribution_percent: item.contribution_pct || 0,
                collapse_score: item.collapse_score || 0,
                cumulative_contribution: 0, // Will be calculated in component
                rank: idx + 1
              }));
              
              return { runId: run.id, data: features };
            } else {
              console.error(`Collapse fetch failed for ${run.id}: ${response.status}`);
            }
          } catch (err) {
            console.error(`Failed to load collapse data for run ${run.id}:`, err);
          }
          return { runId: run.id, data: [] };
        });
        
        const results = await Promise.all(collapsePromises);
        console.log('All collapse results:', results);
        const collapseMap: Record<string, CollapseFeature[]> = {};
        results.forEach(({ runId, data }) => {
          collapseMap[runId] = data;
        });
        console.log('Collapse map:', collapseMap);
        setCollapseData(collapseMap);
      }
      
      setLoadingVisualizations(false);
    };

    loadVisualizations();
  }, [activeTab, runs]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'running':
        return <Clock className="w-5 h-5 text-yellow-500 animate-spin" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'running':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Clock className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading runs for comparison...</p>
        </div>
      </div>
    );
  }

  if (error || ids.length < 2) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <Link href="/" className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800 mb-4">
            <ArrowLeft className="w-4 h-4 mr-1" />
            Back to Dashboard
          </Link>
          <div className="bg-red-50 border-2 border-red-200 rounded-lg p-8 text-center">
            <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-red-800 mb-2">Unable to Compare Runs</h2>
            <p className="text-red-600 mb-4">{error || 'Please select at least 2 runs to compare'}</p>
            <div className="mt-4 p-4 bg-white rounded border border-red-200">
              <p className="text-sm text-gray-700 font-medium mb-2">To compare runs:</p>
              <ol className="text-sm text-gray-600 text-left space-y-1 max-w-md mx-auto">
                <li>1. Go back to the dashboard</li>
                <li>2. Select 2 or more runs using checkboxes</li>
                <li>3. Click the &quot;Compare Selected&quot; button</li>
              </ol>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <Link href="/" className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800 mb-4">
          <ArrowLeft className="w-4 h-4 mr-1" />
          Back to Dashboard
        </Link>

        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Run Comparison</h1>
          <p className="text-sm text-gray-600">Comparing {runs.length} diagnostic runs</p>
        </div>

        {/* Tabs */}
        <div className="bg-white shadow rounded-lg mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('metrics')}
                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'metrics'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                📊 Metrics
              </button>
              <button
                onClick={() => setActiveTab('topologies')}
                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'topologies'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                🌐 Topologies
              </button>
              <button
                onClick={() => setActiveTab('collapse')}
                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'collapse'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                📉 Collapse Maps
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'metrics' && (
              <div className="space-y-6">
                {/* Comparison Table */}
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sticky left-0 bg-gray-50 z-10">
                          Metric
                        </th>
                        {runs.map((run, idx) => (
                          <th key={run.id} scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Run {idx + 1}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">{/* Status */}
              {/* Status */}
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 sticky left-0 bg-white">
                  Status
                </td>
                {runs.map(run => (
                  <td key={run.id} className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(run.status)}
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(run.status)}`}>
                        {run.status}
                      </span>
                    </div>
                  </td>
                ))}
              </tr>

              {/* Data Path */}
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 sticky left-0 bg-white">
                  Data Path
                </td>
                {runs.map(run => (
                  <td key={run.id} className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                    {run.data_path}
                  </td>
                ))}
              </tr>

              {/* Created At */}
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 sticky left-0 bg-white">
                  Created At
                </td>
                {runs.map(run => (
                  <td key={run.id} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {run.created_at ? format(new Date(run.created_at), 'PPpp') : 'N/A'}
                  </td>
                ))}
              </tr>

              {/* Started At */}
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 sticky left-0 bg-white">
                  Started At
                </td>
                {runs.map(run => (
                  <td key={run.id} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {run.started_at ? format(new Date(run.started_at), 'PPpp') : 'N/A'}
                  </td>
                ))}
              </tr>

              {/* Completed At */}
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 sticky left-0 bg-white">
                  Completed At
                </td>
                {runs.map(run => (
                  <td key={run.id} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {run.completed_at ? format(new Date(run.completed_at), 'PPpp') : 'N/A'}
                  </td>
                ))}
              </tr>

              {/* Duration */}
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 sticky left-0 bg-white">
                  Duration
                </td>
                {runs.map(run => {
                  let duration = 'N/A';
                  if (run.started_at && run.completed_at) {
                    const start = new Date(run.started_at);
                    const end = new Date(run.completed_at);
                    const diff = end.getTime() - start.getTime();
                    const seconds = Math.floor(diff / 1000);
                    const minutes = Math.floor(seconds / 60);
                    const hours = Math.floor(minutes / 60);
                    if (hours > 0) {
                      duration = `${hours}h ${minutes % 60}m`;
                    } else if (minutes > 0) {
                      duration = `${minutes}m ${seconds % 60}s`;
                    } else {
                      duration = `${seconds}s`;
                    }
                  } else if (run.started_at) {
                    duration = 'Running...';
                  }
                  return (
                    <td key={run.id} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {duration}
                    </td>
                  );
                })}
              </tr>

              {/* Error */}
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 sticky left-0 bg-white">
                  Error
                </td>
                {runs.map(run => (
                  <td key={run.id} className="px-6 py-4 text-sm text-gray-900 max-w-xs">
                    {run.error ? (
                      <span className="text-red-600 truncate block">{run.error}</span>
                    ) : (
                      <span className="text-green-600">None</span>
                    )}
                  </td>
                ))}
              </tr>

              {/* Actions */}
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 sticky left-0 bg-white">
                  Actions
                </td>
                {runs.map(run => (
                  <td key={run.id} className="px-6 py-4 whitespace-nowrap text-sm">
                    <a
                      href={`/runs/${run.id}`}
                      className="text-blue-600 hover:text-blue-800 font-medium"
                    >
                      View Details →
                    </a>
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
                
                {/* Summary Cards */}
                <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-white shadow rounded-lg p-6">
                    <h3 className="text-sm font-medium text-gray-500 mb-2">Completed Runs</h3>
                    <p className="text-3xl font-bold text-green-600">
                      {runs.filter(r => r.status === 'completed').length} / {runs.length}
                    </p>
                  </div>
                  <div className="bg-white shadow rounded-lg p-6">
                    <h3 className="text-sm font-medium text-gray-500 mb-2">Failed Runs</h3>
                    <p className="text-3xl font-bold text-red-600">
                      {runs.filter(r => r.status === 'failed').length} / {runs.length}
                    </p>
                  </div>
                  <div className="bg-white shadow rounded-lg p-6">
                    <h3 className="text-sm font-medium text-gray-500 mb-2">Average Duration</h3>
                    <p className="text-3xl font-bold text-blue-600">
                      {(() => {
                        const completed = runs.filter(r => r.started_at && r.completed_at);
                        if (completed.length === 0) return 'N/A';
                        const totalMs = completed.reduce((sum, r) => {
                          const start = new Date(r.started_at!).getTime();
                          const end = new Date(r.completed_at!).getTime();
                          return sum + (end - start);
                        }, 0);
                        const avgMs = totalMs / completed.length;
                        const seconds = Math.floor(avgMs / 1000);
                        const minutes = Math.floor(seconds / 60);
                        return minutes > 0 ? `${minutes}m ${seconds % 60}s` : `${seconds}s`;
                      })()}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'topologies' && (
              <div>
                {loadingVisualizations ? (
                  <div className="flex items-center justify-center py-12">
                    <Clock className="w-8 h-8 text-blue-500 animate-spin mr-3" />
                    <p className="text-gray-600">Loading topology graphs...</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {runs.map((run, idx) => (
                      <TopologyGraphStatic
                        key={run.id}
                        nodes={topologyData[run.id]?.nodes || []}
                        links={topologyData[run.id]?.links || []}
                        runName={`Run ${idx + 1}: ${run.id.substring(0, 8)}`}
                      />
                    ))}
                  </div>
                )}
                {!loadingVisualizations && Object.keys(topologyData).length === 0 && (
                  <div className="text-center py-12 text-gray-500">
                    <p>No topology data available for these runs</p>
                    <p className="text-sm mt-2">Make sure runs were executed with topology graph generation enabled</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'collapse' && (
              <div>
                {loadingVisualizations ? (
                  <div className="flex items-center justify-center py-12">
                    <Clock className="w-8 h-8 text-blue-500 animate-spin mr-3" />
                    <p className="text-gray-600">Loading collapse maps...</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {runs.map((run, idx) => (
                      <CollapseMapCompact
                        key={run.id}
                        features={collapseData[run.id] || []}
                        runName={`Run ${idx + 1}: ${run.id.substring(0, 8)}`}
                        topN={10}
                      />
                    ))}
                  </div>
                )}
                {!loadingVisualizations && Object.keys(collapseData).length === 0 && (
                  <div className="text-center py-12 text-gray-500">
                    <p>No collapse data available for these runs</p>
                    <p className="text-sm mt-2">Make sure runs were executed with collapse map generation enabled</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
