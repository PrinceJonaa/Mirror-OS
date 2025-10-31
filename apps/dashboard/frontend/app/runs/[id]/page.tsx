'use client';

import { use, useState } from 'react';
import useSWR from 'swr';
import { ArrowLeft, Activity, CheckCircle, XCircle, Clock, Trash2 } from 'lucide-react';
import { fetchRun, fetchRunResults, fetchCollapseFeatures, deleteRun } from '@/lib/api';
import type { DiagnosticRun, DiagnosticResults } from '@/lib/types';
import { format } from 'date-fns';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import TopologyGraph from '@/components/visualizations/TopologyGraph';
import CollapseMapViewer from '@/components/visualizations/CollapseMapViewer';

export default function RunDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const [deleting, setDeleting] = useState(false);
  const [activeTab, setActiveTab] = useState('summary');
  
  const { data: run, error: runError } = useSWR<DiagnosticRun>(`/api/runs/${id}`, () => fetchRun(id), {
    refreshInterval: 3000,
  });
  const { data: results, error: resultsError } = useSWR<DiagnosticResults>(
    run?.status === 'completed' ? `/api/runs/${id}/results` : null,
    () => fetchRunResults(id)
  );
  const { data: topologyData, error: topologyError } = useSWR(
    run?.status === 'completed' ? `/api/runs/${id}/topology-graph` : null,
    async (url) => {
      const res = await fetch(url);
      if (!res.ok) {
        // Don't throw error for 404 - just means no topology data
        if (res.status === 404) return null;
        throw new Error('Failed to fetch topology data');
      }
      return res.json();
    }
  );
  const { data: collapseFeaturesData } = useSWR(
    run?.status === 'completed' ? `/api/runs/${id}/collapse-features` : null,
    () => fetchCollapseFeatures(id)
  );
  const { data: latticeData } = useSWR(
    run?.status === 'completed' ? `/api/analytics/lattice-points` : null,
    async (url) => {
      const res = await fetch(url);
      if (!res.ok) {
        if (res.status === 404) return null;
        throw new Error('Failed to fetch lattice data');
      }
      return res.json();
    }
  );

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      case 'failed':
        return <XCircle className="w-6 h-6 text-red-500" />;
      case 'running':
        return <Activity className="w-6 h-6 text-blue-500 animate-pulse" />;
      default:
        return <Clock className="w-6 h-6 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (!run) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Activity className="w-8 h-8 text-blue-500 animate-pulse" />
      </div>
    );
  }

  // Show error if run failed to load
  if (runError) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center max-w-md">
          <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Unable to Load Run</h2>
          <p className="text-gray-600 mb-2">Could not retrieve diagnostic run information</p>
          <p className="text-sm text-gray-500 mb-4">This run may have been deleted or the ID is incorrect</p>
          <Link 
            href="/" 
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  // Export helpers
  const handleExportJSON = () => {
    if (!results) return;
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `diagnostic_results_${run.id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleExportCSV = () => {
    if (!results) return;
    // Collapse metrics to CSV
    const collapseRows = results.collapse_metrics?.map(m =>
      Object.values(m).join(',')
    ) || [];
    const collapseHeader = results.collapse_metrics?.length ? Object.keys(results.collapse_metrics[0]).join(',') : '';
    // RFI metrics to CSV
    const rfiRows = results.rfi_metrics?.map(m =>
      Object.values(m).join(',')
    ) || [];
    const rfiHeader = results.rfi_metrics?.length ? Object.keys(results.rfi_metrics[0]).join(',') : '';
    let csv = '';
    if (collapseHeader) {
      csv += 'Collapse Metrics\n' + collapseHeader + '\n' + collapseRows.join('\n') + '\n\n';
    }
    if (rfiHeader) {
      csv += 'RFI Metrics\n' + rfiHeader + '\n' + rfiRows.join('\n') + '\n';
    }
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `diagnostic_results_${run.id}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this run? This action cannot be undone.')) return;
    setDeleting(true);
    try {
      await deleteRun(id);
      router.push('/');
    } catch (error) {
      console.error('Failed to delete run:', error);
      alert('Failed to delete run');
      setDeleting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
                {/* Export Buttons */}
        {run.status === 'completed' && results && (
          <div className="mb-4 flex flex-col sm:flex-row gap-3">
            <button
              onClick={handleExportJSON}
              className="px-4 py-2 bg-blue-600 text-white rounded shadow hover:bg-blue-700 text-sm w-full sm:w-auto justify-center inline-flex items-center"
            >
              Export JSON
            </button>
            <button
              onClick={handleExportCSV}
              className="px-4 py-2 bg-green-600 text-white rounded shadow hover:bg-green-700 text-sm w-full sm:w-auto justify-center inline-flex items-center"
            >
              Export CSV
            </button>
            <button
              onClick={handleDelete}
              disabled={deleting}
              className="px-4 py-2 bg-red-600 text-white rounded shadow hover:bg-red-700 disabled:opacity-50 text-sm w-full sm:w-auto justify-center inline-flex items-center"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              {deleting ? 'Deleting...' : 'Delete Run'}
            </button>
          </div>
        )}
        {/* Header */}
        <div className="mb-6">
          <Link
            href="/"
            className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800 mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-1" />
            Back to Dashboard
          </Link>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-center space-x-4">
              {getStatusIcon(run.status)}
              <div className="min-w-0">
                <h1 className="text-2xl font-bold text-gray-900">Diagnostic Run</h1>
                <p className="text-sm text-gray-600 truncate">{run.id}</p>
              </div>
            </div>
            <span
              className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium self-start sm:self-auto ${getStatusColor(
                run.status
              )}`}
            >
              {run.status}
            </span>
          </div>
        </div>

        {/* Run Info */}
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Run Information</h2>
          <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Data Path</dt>
              <dd className="mt-1 text-sm text-gray-900">{run.data_path}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Status</dt>
              <dd className="mt-1 text-sm text-gray-900">{run.status}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Created At</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {format(new Date(run.created_at), 'PPpp')}
              </dd>
            </div>
            {run.started_at && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Started At</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {format(new Date(run.started_at), 'PPpp')}
                </dd>
              </div>
            )}
            {run.completed_at && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Completed At</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {format(new Date(run.completed_at), 'PPpp')}
                </dd>
              </div>
            )}
          </dl>
          {run.error && (
            <div className="mt-4 text-sm text-red-600 bg-red-50 px-4 py-3 rounded">
              <strong>Error:</strong> {run.error}
            </div>
          )}
        </div>

        {/* Results */}
        {results && (
          <>
            {/* Tabs */}
            <div className="bg-white shadow rounded-lg mb-6">
              <div className="border-b border-gray-200">
                <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
                  {[
                    { id: 'summary', name: 'Summary', available: true, reason: '' },
                    { id: 'topology', name: 'Topology Graph', available: !!topologyData, reason: topologyData ? '' : 'No topology data available - adjacency matrix not stored' },
                    { id: 'collapse', name: 'Collapse Map', available: !!collapseFeaturesData, reason: collapseFeaturesData ? '' : 'No collapse feature data available' },
                    { id: 'lattice', name: 'Lattice Position', available: true, reason: '' }
                  ].map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => tab.available && setActiveTab(tab.id)}
                      className={`py-4 px-1 border-b-2 font-medium text-sm ${
                        activeTab === tab.id
                          ? 'border-blue-500 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      } ${!tab.available ? 'opacity-50 cursor-not-allowed' : ''}`}
                      disabled={!tab.available}
                      title={tab.reason || tab.name}
                    >
                      {tab.name}
                      {!tab.available && <span className="ml-1 text-xs">⚠️</span>}
                    </button>
                  ))}
                </nav>
              </div>

              <div className="p-6">
                {/* Summary Tab */}
                {activeTab === 'summary' && (
                  <>
                    {/* Collapse Metrics */}
                    {results.collapse_metrics && results.collapse_metrics.length > 0 && (
                      <div className="mb-6">
                        <h3 className="text-lg font-medium text-gray-900 mb-4">Collapse Metrics</h3>
                        <ResponsiveContainer width="100%" height={300}>
                          <BarChart data={results.collapse_metrics}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="collapse_type" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="magnitude" fill="#3b82f6" name="Magnitude" />
                            <Bar dataKey="severity" fill="#ef4444" name="Severity" />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    )}

                    {/* RFI Metrics */}
                    {results.rfi_metrics && results.rfi_metrics.length > 0 && (
                      <div className="mb-6">
                        <h3 className="text-lg font-medium text-gray-900 mb-4">RFI Metrics</h3>
                        <ResponsiveContainer width="100%" height={300}>
                          <LineChart data={results.rfi_metrics}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="field_name" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey="fitness_score" stroke="#10b981" name="Fitness Score" />
                            <Line type="monotone" dataKey="coherence_score" stroke="#6366f1" name="Coherence Score" />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    )}

                    {/* Summary Stats */}
                    <div>
                      <h3 className="text-lg font-medium text-gray-900 mb-4">Summary Statistics</h3>
                      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                        <div className="bg-blue-50 px-4 py-3 rounded">
                          <dt className="text-sm font-medium text-blue-900">Total Collapses</dt>
                          <dd className="mt-1 text-2xl font-semibold text-blue-900">
                            {results.collapse_metrics?.length || 0}
                          </dd>
                        </div>
                        <div className="bg-green-50 px-4 py-3 rounded">
                          <dt className="text-sm font-medium text-green-900">RFI Fields</dt>
                          <dd className="mt-1 text-2xl font-semibold text-green-900">
                            {results.rfi_metrics?.length || 0}
                          </dd>
                        </div>
                        <div className="bg-purple-50 px-4 py-3 rounded">
                          <dt className="text-sm font-medium text-purple-900">Avg Fitness</dt>
                          <dd className="mt-1 text-2xl font-semibold text-purple-900">
                            {results.rfi_metrics && results.rfi_metrics.length > 0
                              ? (
                                  results.rfi_metrics.reduce((sum: number, m) => sum + (m.fitness_score || 0), 0) /
                                  results.rfi_metrics.length
                                ).toFixed(2)
                              : 'N/A'}
                          </dd>
                        </div>
                      </div>
                    </div>
                  </>
                )}

                {/* Topology Tab */}
                {activeTab === 'topology' && topologyData && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between mb-6">
                      <h3 className="text-lg font-semibold text-gray-900">Network Topology</h3>
                      <div className="flex items-center gap-4 text-sm text-gray-600">
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                          <span>{topologyData.metadata.node_count} nodes</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 bg-gray-400 rounded-full"></div>
                          <span>{topologyData.metadata.link_count} links</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                          <span>{topologyData.metadata.community_count} communities</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-gray-50 rounded-lg border border-gray-200 p-1">
                      <TopologyGraph nodes={topologyData.nodes} links={topologyData.links} />
                    </div>
                    
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <div className="flex items-start gap-3">
                        <div className="text-blue-600 mt-0.5">
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </div>
                        <div className="flex-1 text-sm text-blue-900">
                          <p className="font-medium mb-1">Interactive Features:</p>
                          <ul className="space-y-1 text-blue-800">
                            <li>• <strong>Drag</strong> nodes to reposition them</li>
                            <li>• <strong>Click</strong> nodes to pin/unpin (red outline when pinned)</li>
                            <li>• <strong>Scroll</strong> or use mouse wheel to zoom in/out</li>
                            <li>• <strong>Hover</strong> over nodes to see details</li>
                            <li>• Use controls on the left to adjust physics and layout</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Collapse Map Tab */}
                {activeTab === 'collapse' && collapseFeaturesData && (
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Feature Collapse Analysis</h3>
                    <CollapseMapViewer 
                      data={collapseFeaturesData.data || []} 
                      metadata={collapseFeaturesData.metadata}
                    />
                  </div>
                )}

                {/* Lattice Tab */}
                {activeTab === 'lattice' && latticeData && (
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Lattice Position</h3>
                    <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-600">Your run&apos;s position in the global phase space:</p>
                      <div className="mt-2 grid grid-cols-2 gap-4">
                        <div>
                          <span className="text-xs text-gray-500">Collapse Ratio:</span>
                          <p className="text-lg font-semibold">
                            {latticeData.points.find((p: { run_id: string }) => p.run_id === id)?.collapse_ratio?.toFixed(3) || 'N/A'}
                          </p>
                        </div>
                        <div>
                          <span className="text-xs text-gray-500">RFI:</span>
                          <p className="text-lg font-semibold">
                            {latticeData.points.find((p: { run_id: string }) => p.run_id === id)?.rfi?.toFixed(3) || 'N/A'}
                          </p>
                        </div>
                      </div>
                    </div>
                    <p className="text-gray-600 text-sm">
                      View the complete lattice at <Link href="/lattice" className="text-blue-600 hover:underline">/lattice</Link>
                    </p>
                  </div>
                )}
              </div>
            </div>
          </>
        )}

        {run.status === 'running' && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-8 text-center">
            <div className="relative w-16 h-16 mx-auto mb-4">
              <Activity className="w-16 h-16 text-blue-500 animate-pulse absolute" />
              <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
            </div>
            <p className="text-blue-900 font-medium text-lg">Diagnostic Running</p>
            <p className="text-blue-700 text-sm mt-2">Processing your data... Results will appear when complete</p>
            <div className="mt-4 flex items-center justify-center gap-2">
              <div className="h-2 w-2 bg-blue-600 rounded-full animate-bounce"></div>
              <div className="h-2 w-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="h-2 w-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
