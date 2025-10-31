'use client'

import { useState } from 'react'
import useSWR from 'swr'
import { ArrowLeft, BarChart3, TrendingUp, GitCompare, X, CheckCircle, Plus } from 'lucide-react'
import { fetchRuns, createRun } from '@/lib/api'
import { format } from 'date-fns'
import Link from 'next/link'
import FileInputManager from '@/components/FileInputManager'
import type { CreateRunRequest } from '@/lib/types'

interface Run {
  id: string
  status: string
  data_path: string
  created_at: string
}

interface NewFile {
  path: string;
  source: 'upload' | 'path' | 'browse';
}

export default function PatternComparisonPage() {
  const { data: runsData } = useSWR('/api/runs', fetchRuns)
  const [selectedRun1, setSelectedRun1] = useState<string>('')
  const [selectedRun2, setSelectedRun2] = useState<string>('')
  const [step, setStep] = useState<'select' | 'compare'>('select')
  const [showAddFiles, setShowAddFiles] = useState(false)
  const [newFiles, setNewFiles] = useState<Array<{ path: string; source: 'upload' | 'path' | 'browse' }>>([])
  const [creatingRun, setCreatingRun] = useState<string | null>(null)

  const completedRuns = runsData?.runs?.filter((run: Run) => run.status === 'completed') || []

  const handleCompare = () => {
    if (selectedRun1 && selectedRun2 && selectedRun1 !== selectedRun2) {
      setStep('compare')
    }
  }

  const handleReset = () => {
    setSelectedRun1('')
    setSelectedRun2('')
    setStep('select')
    setShowAddFiles(false)
    setNewFiles([])
  }

  const handleFileSelected = (filePath: string, source: 'upload' | 'path' | 'browse') => {
    setNewFiles(prev => [...prev, { path: filePath, source }])
    setShowAddFiles(false)
  }

  const handleCreateRun = async (file: { path: string; source: 'upload' | 'path' | 'browse' }) => {
    setCreatingRun(file.path)
    
    try {
      const runRequest: CreateRunRequest = {
        name: `Run from ${file.source} - ${file.path.split('/').pop()}`,
        description: `Created via ${file.source} file input`,
        data_path: file.path,
        data_type: 'auto',
        corr_method: 'pearson',
        adj_threshold: 0.7,
        compute_null: false,
        n_permutations: 100,
        use_louvain: false,
        skip_visuals: false
      }

      await createRun(runRequest)
      
      // Refresh the runs data
      // Note: In a real app, you might want to use SWR's mutate or refetch
      window.location.reload()
    } catch (error) {
      console.error('Failed to create run:', error)
      alert('Failed to create diagnostic run. Please try again.')
    } finally {
      setCreatingRun(null)
    }
  }

  if (step === 'compare') {
    const run1 = completedRuns.find((r: Run) => r.id === selectedRun1)
    const run2 = completedRuns.find((r: Run) => r.id === selectedRun2)

    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-6">
            <Link
              href="/"
              className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800 mb-4"
            >
              <ArrowLeft className="w-4 h-4 mr-1" />
              Back to Dashboard
            </Link>
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Visual Pattern Comparison</h1>
                <p className="text-sm text-gray-600 mt-1">Side-by-side analysis of two diagnostic runs</p>
              </div>
              <button
                onClick={handleReset}
                className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 flex items-center"
              >
                <X className="w-4 h-4 mr-2" />
                New Comparison
              </button>
            </div>
          </div>

          {/* Selected Runs Info */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-lg font-semibold mb-4">Comparison Overview</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="border border-blue-200 rounded-lg p-4 bg-blue-50">
                <h3 className="font-medium text-blue-900 mb-2">Run 1</h3>
                <p className="text-sm text-gray-700 truncate">{run1?.id}</p>
                <p className="text-xs text-gray-600">
                  {run1 && format(new Date(run1.created_at), 'PPp')}
                </p>
                <p className="text-xs text-gray-600 mt-1">Data: {run1?.data_path}</p>
              </div>
              <div className="border border-green-200 rounded-lg p-4 bg-green-50">
                <h3 className="font-medium text-green-900 mb-2">Run 2</h3>
                <p className="text-sm text-gray-700 truncate">{run2?.id}</p>
                <p className="text-xs text-gray-600">
                  {run2 && format(new Date(run2.created_at), 'PPp')}
                </p>
                <p className="text-xs text-gray-600 mt-1">Data: {run2?.data_path}</p>
              </div>
            </div>
          </div>

          {/* Pattern Analysis */}
          <div className="space-y-6">
            {/* Lattice Position Comparison */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center">
                <BarChart3 className="w-5 h-5 mr-2" />
                Lattice Position Comparison
              </h2>
              <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-700 mb-3">
                  Compare positions in the global phase space to understand relative collapse patterns.
                </p>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Run 1 Position:</span>
                    <span className="ml-2 text-blue-600">(Higher collapse, lower RFI)</span>
                  </div>
                  <div>
                    <span className="font-medium">Run 2 Position:</span>
                    <span className="ml-2 text-green-600">(Lower collapse, higher RFI)</span>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-8 text-center">
                <p className="text-gray-600">
                  View the complete lattice visualization at{' '}
                  <Link href="/lattice" className="text-blue-600 hover:underline">
                    /lattice
                  </Link>
                </p>
              </div>
            </div>

            {/* Metrics Comparison */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center">
                <TrendingUp className="w-5 h-5 mr-2" />
                Detailed Metrics Comparison
              </h2>
              <div className="text-center py-8 text-gray-500">
                <GitCompare className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Detailed metrics comparison coming soon...</p>
                <p className="text-sm mt-2">
                  View individual runs for comprehensive metrics:
                </p>
                <div className="mt-4 space-x-4">
                  <Link
                    href={`/runs/${selectedRun1}`}
                    className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 rounded text-sm hover:bg-blue-200"
                  >
                    <CheckCircle className="w-3 h-3 mr-1" />
                    Run 1 Details
                  </Link>
                  <Link
                    href={`/runs/${selectedRun2}`}
                    className="inline-flex items-center px-3 py-1 bg-green-100 text-green-800 rounded text-sm hover:bg-green-200"
                  >
                    <CheckCircle className="w-3 h-3 mr-1" />
                    Run 2 Details
                  </Link>
                </div>
              </div>
            </div>

            {/* Pattern Interpretation */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-4">Pattern Interpretation</h2>
              <div className="space-y-4">
                <div className="p-4 bg-blue-50 border-l-4 border-blue-400">
                  <h3 className="font-medium text-blue-900">Collapse Pattern Analysis</h3>
                  <p className="text-sm text-blue-800 mt-1">
                    Based on lattice positions, these runs show different collapse characteristics. 
                    The positioning suggests different levels of system stability and relational fitness.
                  </p>
                </div>
                <div className="p-4 bg-green-50 border-l-4 border-green-400">
                  <h3 className="font-medium text-green-900">Next Steps</h3>
                  <ul className="text-sm text-green-800 mt-1 space-y-1">
                    <li>• Examine individual run details for specific metrics</li>
                    <li>• Review topology graphs to understand network structure</li>
                    <li>• Analyze collapse maps for spatial patterns</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-6">
          <Link
            href="/"
            className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800 mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-1" />
            Back to Dashboard
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">Visual Pattern Comparison</h1>
          <p className="text-sm text-gray-600 mt-1">
            Compare diagnostic runs to identify patterns and differences in collapse behavior
          </p>
        </div>

        {/* Selection Form */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-6">Select Runs to Compare</h2>
          
          {completedRuns.length < 2 ? (
            <div className="text-center py-8 text-gray-500">
              <GitCompare className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>Need at least 2 completed runs to compare</p>
              <p className="text-sm mt-2">
                Currently have {completedRuns.length} completed runs
              </p>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="block text-sm font-medium text-gray-700">
                      First Run
                    </label>
                    <button
                      onClick={() => setShowAddFiles(!showAddFiles)}
                      className="text-xs text-blue-600 hover:text-blue-800 flex items-center"
                    >
                      <Plus className="w-3 h-3 mr-1" />
                      Add File
                    </button>
                  </div>
                  <select
                    value={selectedRun1}
                    onChange={(e) => setSelectedRun1(e.target.value)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select a run...</option>
                    {completedRuns.map((run: Run) => (
                      <option key={run.id} value={run.id}>
                        {format(new Date(run.created_at), 'PPp')} - {run.data_path}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="block text-sm font-medium text-gray-700">
                      Second Run
                    </label>
                    <button
                      onClick={() => setShowAddFiles(!showAddFiles)}
                      className="text-xs text-blue-600 hover:text-blue-800 flex items-center"
                    >
                      <Plus className="w-3 h-3 mr-1" />
                      Add File
                    </button>
                  </div>
                  <select
                    value={selectedRun2}
                    onChange={(e) => setSelectedRun2(e.target.value)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select a run...</option>
                    {completedRuns
                      .filter((run: Run) => run.id !== selectedRun1)
                      .map((run: Run) => (
                        <option key={run.id} value={run.id}>
                          {format(new Date(run.created_at), 'PPp')} - {run.data_path}
                        </option>
                      ))}
                  </select>
                </div>
              </div>

              {showAddFiles && (
                <div className="mb-6">
                  <FileInputManager
                    onFileSelected={handleFileSelected}
                    selectedFile={newFiles.length > 0 ? newFiles[newFiles.length - 1].path : undefined}
                  />
                </div>
              )}

              {newFiles.length > 0 && (
                <div className="mb-6 p-4 bg-blue-50 rounded-lg">
                  <h3 className="font-medium text-blue-900 mb-3">New Files Added</h3>
                  <div className="space-y-2">
                    {newFiles.map((file, index) => (
                      <div key={index} className="text-sm bg-white p-2 rounded">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex-1">
                            <span className="text-gray-800">{file.path}</span>
                            <span className="text-xs text-gray-500 ml-2 capitalize">via {file.source}</span>
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <button
                              onClick={() => {
                                setSelectedRun1(file.path)
                                setShowAddFiles(false)
                              }}
                              className="w-full px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                              disabled={selectedRun1 === file.path || creatingRun === file.path}
                            >
                              Select as Run 1
                            </button>
                          </div>
                          <div>
                            <button
                              onClick={() => {
                                setSelectedRun2(file.path)
                                setShowAddFiles(false)
                              }}
                              className="w-full px-2 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                              disabled={selectedRun2 === file.path || creatingRun === file.path}
                            >
                              Select as Run 2
                            </button>
                          </div>
                        </div>
                        <button
                          onClick={() => handleCreateRun(file)}
                          disabled={creatingRun === file.path}
                          className="w-full mt-2 px-2 py-1 text-xs bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50"
                        >
                          {creatingRun === file.path ? 'Creating...' : 'Create Diagnostic Run'}
                        </button>
                      </div>
                    ))}
                  </div>
                  <p className="text-xs text-blue-700 mt-3">
                    Click &quot;Select as Run 1&quot; or &quot;Select as Run 2&quot; to use these files in comparison, or create a diagnostic run first.
                  </p>
                </div>
              )}

              {selectedRun1 && selectedRun2 && (
                <div className="border-t pt-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="font-medium">Ready to Compare</h3>
                      <p className="text-sm text-gray-600">
                        Selected two runs for comparison
                      </p>
                    </div>
                    <button
                      onClick={handleCompare}
                      className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center"
                    >
                      <GitCompare className="w-4 h-4 mr-2" />
                      Compare Patterns
                    </button>
                  </div>
                </div>
              )}

              {/* Quick Stats */}
              <div className="mt-6 pt-6 border-t">
                <h3 className="text-sm font-medium text-gray-700 mb-3">Available Runs</h3>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {completedRuns.slice(0, 10).map((run: Run) => (
                    <div
                      key={run.id}
                      className={`p-3 rounded border text-sm ${
                        selectedRun1 === run.id
                          ? 'border-blue-300 bg-blue-50'
                          : selectedRun2 === run.id
                          ? 'border-green-300 bg-green-50'
                          : 'border-gray-200'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="truncate">
                          <p className="font-medium truncate">{run.data_path}</p>
                          <p className="text-xs text-gray-500">
                            {format(new Date(run.created_at), 'PPp')}
                          </p>
                        </div>
                        <div className="flex space-x-2 ml-4">
                          <button
                            onClick={() => setSelectedRun1(selectedRun1 === run.id ? '' : run.id)}
                            className={`px-2 py-1 rounded text-xs ${
                              selectedRun1 === run.id
                                ? 'bg-blue-600 text-white'
                                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                            }`}
                          >
                            Run 1
                          </button>
                          <button
                            onClick={() => setSelectedRun2(selectedRun2 === run.id ? '' : run.id)}
                            className={`px-2 py-1 rounded text-xs ${
                              selectedRun2 === run.id
                                ? 'bg-green-600 text-white'
                                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                            }`}
                          >
                            Run 2
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                {completedRuns.length > 10 && (
                  <p className="text-xs text-gray-500 mt-2">
                    Showing first 10 of {completedRuns.length} runs
                  </p>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}