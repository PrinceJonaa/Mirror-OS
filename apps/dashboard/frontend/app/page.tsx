'use client';

import { useState, useEffect } from 'react';
import useSWR from 'swr';
import { Plus, Activity, CheckCircle, XCircle, Clock, RefreshCw, Search, GitCompare } from 'lucide-react';
import { fetchDashboardStats, fetchRuns, createRun } from '@/lib/api';
import type { DiagnosticRun, DashboardStats } from '@/lib/types';
import { format } from 'date-fns';
import Link from 'next/link';
import Tooltip from '@/components/Tooltip';
import LoadingSkeleton from '@/components/LoadingSkeleton';
import ToastContainer, { useToast } from '@/components/Toast';
import FileInputManager from '@/components/FileInputManager';

export default function Home() {
  const { toasts, showToast, closeToast } = useToast();
  const { data: stats, isLoading: statsLoading } = useSWR<DashboardStats>('/api/dashboard/stats', fetchDashboardStats, {
    refreshInterval: 5000,
  });
  const { data: runsRaw, mutate, isLoading: runsLoading } = useSWR<{ runs: DiagnosticRun[] }>(
    '/api/runs',
    fetchRuns,
    { refreshInterval: 3000 }
  );

  const [showCreateForm, setShowCreateForm] = useState(false);
  const [dataPath, setDataPath] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [statusFilter, setStatusFilter] = useState<'all'|'completed'|'failed'|'running'|'pending'>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [selectedRuns, setSelectedRuns] = useState<Set<string>>(new Set());
  const [compareMode, setCompareMode] = useState(false);
  const runsPerPage = 10;

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
      setCurrentPage(1); // Reset to first page on search
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const runs: DiagnosticRun[] = Array.isArray(runsRaw?.runs) ? runsRaw.runs : [];
  const filteredRuns: DiagnosticRun[] = runs
    .filter(r => statusFilter === 'all' || r.status === statusFilter)
    .filter(r => {
      if (!debouncedSearch) return true;
      const searchLower = debouncedSearch.toLowerCase();
      const dataPath = r.data_path?.toLowerCase() || '';
      const name = r.name?.toLowerCase() || '';
      return dataPath.includes(searchLower) || name.includes(searchLower);
    });
  
  // Pagination
  const totalPages = Math.ceil(filteredRuns.length / runsPerPage);
  const paginatedRuns = filteredRuns.slice((currentPage - 1) * runsPerPage, currentPage * runsPerPage);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd/Ctrl + K to toggle create form
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setShowCreateForm(prev => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Helper to calculate run duration
  const getRunDuration = (run: DiagnosticRun): string => {
    if (run.status === 'pending') return 'Not started';
    if (run.status === 'running') {
      const start = new Date(run.started_at || run.created_at);
      const now = new Date();
      const diff = Math.floor((now.getTime() - start.getTime()) / 1000);
      return `Running for ${diff}s`;
    }
    if (run.completed_at && (run.started_at || run.created_at)) {
      const start = new Date(run.started_at || run.created_at);
      const end = new Date(run.completed_at);
      const diff = Math.floor((end.getTime() - start.getTime()) / 1000);
      if (diff < 60) return `${diff}s`;
      if (diff < 3600) return `${Math.floor(diff / 60)}m ${diff % 60}s`;
      return `${Math.floor(diff / 3600)}h ${Math.floor((diff % 3600) / 60)}m`;
    }
    return 'Unknown';
  };

  const handleDeleteRun = async (id: string) => {
    if (!confirm('Are you sure you want to delete this run?')) return;
    try {
      const { deleteRun } = await import('@/lib/api');
      await deleteRun(id);
      mutate();
      showToast('Run deleted successfully', 'success');
    } catch (error) {
      console.error('Failed to delete run:', error);
      showToast('Failed to delete run', 'error');
    }
  };

  const handleBulkDelete = async () => {
    if (selectedRuns.size === 0) return;
    if (!confirm(`Are you sure you want to delete ${selectedRuns.size} run(s)?`)) return;
    try {
      const { deleteRun } = await import('@/lib/api');
      await Promise.all(Array.from(selectedRuns).map(id => deleteRun(id)));
      setSelectedRuns(new Set());
      mutate();
      showToast(`${selectedRuns.size} run(s) deleted successfully`, 'success');
    } catch (error) {
      console.error('Failed to delete runs:', error);
      showToast('Failed to delete some runs', 'error');
    }
  };

  const toggleRunSelection = (id: string) => {
    const newSelection = new Set(selectedRuns);
    if (newSelection.has(id)) {
      newSelection.delete(id);
    } else {
      newSelection.add(id);
    }
    setSelectedRuns(newSelection);
  };

  const toggleSelectAll = () => {
    if (selectedRuns.size === paginatedRuns.length) {
      setSelectedRuns(new Set());
    } else {
      setSelectedRuns(new Set(paginatedRuns.map(r => r.id)));
    }
  };

  const handleCreateRun = async () => {
    setSubmitting(true);
    try {
      await createRun({
        name: `Run ${new Date().toLocaleString()}`,
        description: '',
        data_path: dataPath,
        data_type: 'auto',
        corr_method: 'pearson',
        adj_threshold: 0.7,
        compute_null: false,
        n_permutations: 100,
        use_louvain: false,
        skip_visuals: false,
        seed: undefined,
      });
      setDataPath('');
      setShowCreateForm(false);
      mutate();
      showToast('Diagnostic run created successfully!', 'success');
    } catch (error) {
      console.error('Failed to create run:', error);
      showToast('Failed to create run. Please check your data path.', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'running':
        return <Activity className="w-5 h-5 text-blue-500 animate-pulse" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
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

  // Show loading skeleton while fetching initial data
  if (statsLoading || runsLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Integration Dashboard</h1>
            <p className="mt-2 text-gray-600">Truth Distortion Unified Diagnostic System</p>
          </div>
          <LoadingSkeleton />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Integration Dashboard</h1>
            <p className="mt-2 text-gray-600">Truth Distortion Unified Diagnostic System</p>
          </div>
          <div className="flex items-center space-x-4">
            <Link
              href="/lattice"
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <Activity className="w-4 h-4 mr-2" />
              Lattice View
            </Link>
            <Tooltip content="This dashboard allows you to run and monitor truth distortion diagnostics on your data. Create a new run by clicking the button below and providing a valid data path." position="left" />
          </div>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
            <div className="bg-white shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center flex-1">
                    <div className="shrink-0">
                      <Activity className="h-6 w-6 text-gray-400" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Total Runs</dt>
                        <dd className="text-2xl font-semibold text-gray-900">{stats.total_runs}</dd>
                      </dl>
                    </div>
                  </div>
                  <Tooltip content="Total number of diagnostic runs created" position="bottom" />
                </div>
              </div>
            </div>

            <div className="bg-white shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center flex-1">
                    <div className="shrink-0">
                      <CheckCircle className="h-6 w-6 text-green-400" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Completed</dt>
                        <dd className="text-2xl font-semibold text-gray-900">{stats.completed_runs}</dd>
                      </dl>
                    </div>
                  </div>
                  <Tooltip content="Runs that finished successfully" position="bottom" />
                </div>
              </div>
            </div>

            <div className="bg-white shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center flex-1">
                    <div className="shrink-0">
                      <XCircle className="h-6 w-6 text-red-400" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Failed</dt>
                        <dd className="text-2xl font-semibold text-gray-900">{stats.failed_runs}</dd>
                      </dl>
                    </div>
                  </div>
                  <Tooltip content="Runs that encountered errors during execution" position="bottom" />
                </div>
              </div>
            </div>

            <div className="bg-white shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center flex-1">
                    <div className="shrink-0">
                      <Clock className="h-6 w-6 text-blue-400" />
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Success Rate</dt>
                        <dd className="text-2xl font-semibold text-gray-900">
                          {stats.total_runs > 0
                            ? Math.round((stats.completed_runs / stats.total_runs) * 100)
                            : 0}
                          %
                        </dd>
                      </dl>
                    </div>
                  </div>
                  <Tooltip content="Percentage of runs completed successfully out of total runs" position="bottom" />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Create Run Button */}
        <div className="mb-6 flex flex-col sm:flex-row items-start sm:items-center gap-3">
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 w-full sm:w-auto justify-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Diagnostic Run
          </button>
          <button
            onClick={() => mutate()}
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 w-full sm:w-auto justify-center"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </button>
          {selectedRuns.size > 0 && (
            <button
              onClick={handleBulkDelete}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 w-full sm:w-auto justify-center"
            >
              <XCircle className="w-4 h-4 mr-2" />
              Delete Selected ({selectedRuns.size})
            </button>
          )}
          <button
            onClick={() => {
              setCompareMode(!compareMode);
              if (compareMode) setSelectedRuns(new Set()); // Clear selection when exiting compare mode
            }}
            className={`inline-flex items-center px-4 py-2 border text-sm font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 w-full sm:w-auto justify-center ${
              compareMode 
                ? 'bg-purple-600 text-white border-transparent hover:bg-purple-700' 
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
            }`}
          >
            <GitCompare className="w-4 h-4 mr-2" />
            {compareMode ? `Compare (${selectedRuns.size})` : 'Compare Runs'}
          </button>
          {compareMode && selectedRuns.size >= 2 && (
            <button
              onClick={() => {
                // Navigate to comparison view
                const ids = Array.from(selectedRuns).join(',');
                window.location.href = `/compare?ids=${ids}`;
              }}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 w-full sm:w-auto justify-center"
            >
              View Comparison ({selectedRuns.size} runs)
            </button>
          )}
          <span className="text-xs text-gray-500 sm:ml-auto hidden sm:inline">
            Tip: Press <kbd className="px-2 py-1 bg-gray-100 border rounded">⌘ K</kbd> to quickly create a run
          </span>
        </div>

        {/* Create Form */}
        {showCreateForm && (
          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Create New Run</h3>
            
            {/* File Input Manager */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Data File <span className="text-red-500">*</span>
              </label>
              <FileInputManager 
                onFileSelected={(filePath: string) => setDataPath(filePath)}
              />
              {dataPath && (
                <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-md">
                  <p className="text-sm text-blue-800">
                    <strong>Selected:</strong> {dataPath}
                  </p>
                </div>
              )}
            </div>

            <div className="flex flex-col sm:flex-row gap-3">
              <button
                type="button"
                onClick={handleCreateRun}
                disabled={submitting || !dataPath.trim()}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 w-full sm:w-auto justify-center"
              >
                {submitting ? 'Creating...' : 'Create Run'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowCreateForm(false);
                  setDataPath('');
                }}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 w-full sm:w-auto justify-center"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {/* Runs List */}
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="px-4 sm:px-6 py-4 border-b border-gray-200">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <div className="flex items-center gap-4">
                <h2 className="text-lg font-medium text-gray-900">Diagnostic Runs</h2>
                {compareMode && (
                  <div className="flex items-center gap-2">
                    <button
                      onClick={toggleSelectAll}
                      className="text-xs text-purple-600 hover:text-purple-800 font-medium"
                    >
                      {selectedRuns.size === paginatedRuns.length ? 'Deselect All' : 'Select All on Page'}
                    </button>
                  </div>
                )}
              </div>
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search by data path..."
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    className="pl-9 pr-3 py-1.5 text-sm border rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full"
                  />
                </div>
                <div className="flex items-center gap-2">
                  <label className="text-sm text-gray-600 shrink-0">Filter:</label>
                  <select
                    value={statusFilter}
                    onChange={e => {
                      setStatusFilter(e.target.value as 'all' | 'completed' | 'failed' | 'running' | 'pending');
                      setCurrentPage(1); // Reset to first page on filter change
                    }}
                    className="border rounded px-2 py-1 text-sm flex-1 sm:flex-none"
                  >
                    <option value="all">All</option>
                    <option value="completed">Completed</option>
                    <option value="failed">Failed</option>
                    <option value="running">Running</option>
                    <option value="pending">Pending</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
          <div className="divide-y divide-gray-200">
            {paginatedRuns.length > 0 ? (
              paginatedRuns.map((run: DiagnosticRun) => (
                <div key={run.id} className="px-4 sm:px-6 py-4 hover:bg-gray-50">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                    <div className="flex items-start space-x-3 min-w-0 flex-1">
                      {compareMode && (
                        <input
                          type="checkbox"
                          checked={selectedRuns.has(run.id)}
                          onChange={() => toggleRunSelection(run.id)}
                          className="mt-1 w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                        />
                      )}
                      {getStatusIcon(run.status)}
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-gray-900 truncate">{run.data_path}</p>
                        <p className="text-xs text-gray-500 wrap-break-word">
                          Created: {run.created_at ? format(new Date(run.created_at), 'PPpp') : 'N/A'} • Duration: {getRunDuration(run)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 sm:shrink-0 self-start sm:self-center">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                          run.status
                        )}`}
                      >
                        {run.status}
                      </span>
                      <a
                        href={`/runs/${run.id}`}
                        className="text-blue-600 hover:text-blue-800 text-sm font-medium whitespace-nowrap"
                      >
                        View Details →
                      </a>
                      {!compareMode && (
                        <button
                          onClick={() => handleDeleteRun(run.id)}
                          className="text-red-600 hover:text-red-800 text-sm font-medium whitespace-nowrap"
                          title="Delete this run"
                        >
                          <XCircle className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                  {run.error && (
                    <div className="mt-2 text-sm text-red-600 bg-red-50 px-3 py-2 rounded wrap-break-word">
                      <strong>Error:</strong> {run.error}
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="px-6 py-16 text-center">
                {runs.length === 0 ? (
                  <>
                    <Activity className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Diagnostic Runs Yet</h3>
                    <p className="text-gray-500 mb-6 max-w-md mx-auto">
                      Get started by creating your first diagnostic run. Analyze your data to detect truth distortions, 
                      measure relational fitness, and explore network structure.
                    </p>
                    <button
                      onClick={() => setShowCreateForm(true)}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Create First Run
                    </button>
                  </>
                ) : (
                  <>
                    <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Matching Runs</h3>
                    <p className="text-gray-500 mb-6">
                      No runs match your current filters or search query.
                    </p>
                    <button
                      onClick={() => {
                        setSearchQuery('');
                        setStatusFilter('all');
                        setCurrentPage(1);
                      }}
                      className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50"
                    >
                      Clear Filters
                    </button>
                  </>
                )}
              </div>
            )}
          </div>
          
          {/* Pagination */}
          {totalPages > 1 && (
            <div className="px-4 sm:px-6 py-4 border-t border-gray-200 flex flex-col sm:flex-row items-center justify-between gap-3">
              <div className="text-sm text-gray-500 text-center sm:text-left">
                Showing {((currentPage - 1) * runsPerPage) + 1} to {Math.min(currentPage * runsPerPage, filteredRuns.length)} of {filteredRuns.length} runs
              </div>
              <div className="flex gap-2 flex-wrap justify-center">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="px-3 py-1 border rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Previous
                </button>
                {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                  <button
                    key={page}
                    onClick={() => setCurrentPage(page)}
                    className={`px-3 py-1 border rounded text-sm ${
                      page === currentPage ? 'bg-blue-600 text-white' : 'hover:bg-gray-50'
                    }`}
                  >
                    {page}
                  </button>
                ))}
                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="px-3 py-1 border rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
      <ToastContainer toasts={toasts} onClose={closeToast} />
    </div>
  );
}
