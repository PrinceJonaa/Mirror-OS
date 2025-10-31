'use client';
import React, { useState, useMemo } from 'react';
import { BarChart3, TrendingDown, Layers, Info, Download, Filter, Search } from 'lucide-react';
import * as d3 from 'd3';

interface CollapseFeature {
  feature_index: number;
  feature_name?: string;
  collapse_score: number;
  contribution_pct: number;
}

interface CollapseMapViewerProps {
  data: CollapseFeature[];
  metadata?: {
    m_total: number;
    m_effective: number;
    collapse_ratio: number;
    meff_liji: number;
  };
}

const CollapseMapViewer: React.FC<CollapseMapViewerProps> = ({ data, metadata }) => {
  const [viewMode, setViewMode] = useState<'bar' | 'treemap' | 'table'>('bar');
  const [searchQuery, setSearchQuery] = useState('');
  const [minContribution, setMinContribution] = useState(0);
  const [showTop, setShowTop] = useState(20);

  // Filter and sort data
  const filteredData = useMemo(() => {
    return data
      .filter(d => {
        const name = d.feature_name || `Feature ${d.feature_index}`;
        const matchesSearch = name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                            d.feature_index.toString().includes(searchQuery);
        const meetsThreshold = d.contribution_pct >= minContribution;
        return matchesSearch && meetsThreshold;
      })
      .sort((a, b) => b.collapse_score - a.collapse_score)
      .slice(0, showTop);
  }, [data, searchQuery, minContribution, showTop]);

  // Calculate cumulative contribution
  const cumulativeData = useMemo(() => {
    return filteredData.reduce((acc, d, idx) => {
      const cumulative = idx === 0 ? d.contribution_pct : acc[idx - 1].cumulative + d.contribution_pct;
      acc.push({ ...d, cumulative });
      return acc;
    }, [] as Array<CollapseFeature & { cumulative: number }>);
  }, [filteredData]);

  // Color scale
  const colorScale = d3.scaleSequential(d3.interpolateViridis)
    .domain([0, Math.max(...data.map(d => d.collapse_score))]);

  // Export as CSV
  const handleExport = () => {
    const csv = [
      'Feature Index,Feature Name,Collapse Score,Contribution %',
      ...filteredData.map(d => 
        `${d.feature_index},${d.feature_name || `Feature ${d.feature_index}`},${d.collapse_score},${d.contribution_pct}`
      )
    ].join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'collapse_map.csv';
    a.click();
  };

  return (
    <div className="w-full space-y-4">
      {/* Header with Metadata */}
      {metadata && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
            <div className="flex items-center gap-2 mb-2">
              <Layers className="w-4 h-4 text-blue-600" />
              <span className="text-xs font-medium text-blue-900">Total Dimensions</span>
            </div>
            <p className="text-2xl font-bold text-blue-900">{metadata.m_total}</p>
          </div>
          
          <div className="bg-green-50 rounded-lg p-4 border border-green-200">
            <div className="flex items-center gap-2 mb-2">
              <Layers className="w-4 h-4 text-green-600" />
              <span className="text-xs font-medium text-green-900">Effective Dims</span>
            </div>
            <p className="text-2xl font-bold text-green-900">{metadata.m_effective}</p>
          </div>
          
          <div className="bg-orange-50 rounded-lg p-4 border border-orange-200">
            <div className="flex items-center gap-2 mb-2">
              <TrendingDown className="w-4 h-4 text-orange-600" />
              <span className="text-xs font-medium text-orange-900">Collapse Ratio</span>
            </div>
            <p className="text-2xl font-bold text-orange-900">
              {(metadata.collapse_ratio * 100).toFixed(1)}%
            </p>
          </div>
          
          <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
            <div className="flex items-center gap-2 mb-2">
              <BarChart3 className="w-4 h-4 text-purple-600" />
              <span className="text-xs font-medium text-purple-900">M_eff (Li-Ji)</span>
            </div>
            <p className="text-2xl font-bold text-purple-900">
              {metadata.meff_liji.toFixed(2)}
            </p>
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="bg-white rounded-lg border p-4 space-y-4">
        <div className="flex flex-wrap items-center gap-4">
          {/* View Mode */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode('bar')}
              className={`px-3 py-2 text-sm rounded flex items-center gap-2 ${
                viewMode === 'bar'
                  ? 'bg-blue-100 text-blue-800 font-medium'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              Bar Chart
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={`px-3 py-2 text-sm rounded flex items-center gap-2 ${
                viewMode === 'table'
                  ? 'bg-blue-100 text-blue-800 font-medium'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <Layers className="w-4 h-4" />
              Table
            </button>
          </div>

          <div className="border-l h-8" />

          {/* Search */}
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search features..."
                className="w-full pl-9 pr-3 py-2 text-sm border rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          {/* Export */}
          <button
            onClick={handleExport}
            className="px-3 py-2 text-sm bg-green-50 text-green-700 rounded hover:bg-green-100 flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            Export CSV
          </button>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-600" />
            <label className="text-sm text-gray-700">Min Contribution:</label>
            <input
              type="range"
              min="0"
              max="20"
              step="0.5"
              value={minContribution}
              onChange={(e) => setMinContribution(Number(e.target.value))}
              className="w-32"
            />
            <span className="text-sm font-medium text-gray-900">{minContribution.toFixed(1)}%</span>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-700">Show Top:</label>
            <select
              value={showTop}
              onChange={(e) => setShowTop(Number(e.target.value))}
              className="px-2 py-1 text-sm border rounded"
            >
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
              <option value={data.length}>All ({data.length})</option>
            </select>
          </div>

          <div className="ml-auto text-sm text-gray-600">
            Showing {filteredData.length} of {data.length} features
          </div>
        </div>
      </div>

      {/* Visualization */}
      {viewMode === 'bar' && (
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            Collapse Score Distribution
          </h3>
          
          {/* Bar Chart */}
          <div className="space-y-2">
            {cumulativeData.map((feature, idx) => {
              const name = feature.feature_name || `Feature ${feature.feature_index}`;
              const barColor = colorScale(feature.collapse_score);
              
              return (
                <div key={feature.feature_index} className="group">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-mono text-gray-500 w-8">{idx + 1}</span>
                    <span className="text-sm font-medium text-gray-900 flex-1 truncate">
                      {name}
                    </span>
                    <span className="text-xs text-gray-600 w-16 text-right">
                      {feature.contribution_pct.toFixed(2)}%
                    </span>
                    <span className="text-xs text-gray-500 w-16 text-right">
                      Σ {feature.cumulative.toFixed(1)}%
                    </span>
                  </div>
                  <div className="relative h-8 bg-gray-100 rounded overflow-hidden">
                    <div
                      className="h-full transition-all duration-300 group-hover:opacity-80"
                      style={{
                        width: `${(feature.contribution_pct / Math.max(...data.map(d => d.contribution_pct))) * 100}%`,
                        backgroundColor: barColor
                      }}
                    />
                    <div className="absolute inset-0 flex items-center px-2">
                      <span className="text-xs font-medium text-white drop-shadow">
                        Score: {feature.collapse_score.toFixed(4)}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Legend */}
          <div className="mt-6 pt-4 border-t">
            <div className="flex items-center gap-4 text-xs text-gray-600">
              <div className="flex items-center gap-2">
                <Info className="w-4 h-4" />
                <span>Higher collapse score = more redundancy with other features</span>
              </div>
              <div className="ml-auto">
                <span className="font-medium">Σ</span> = Cumulative contribution
              </div>
            </div>
          </div>
        </div>
      )}

      {viewMode === 'table' && (
        <div className="bg-white rounded-lg border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Rank</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Feature</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-700 uppercase">Index</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-700 uppercase">Collapse Score</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-700 uppercase">Contribution</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-700 uppercase">Cumulative</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {cumulativeData.map((feature, idx) => {
                  const name = feature.feature_name || `Feature ${feature.feature_index}`;
                  const barColor = colorScale(feature.collapse_score);
                  
                  return (
                    <tr key={feature.feature_index} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm text-gray-900 font-medium">{idx + 1}</td>
                      <td className="px-4 py-3 text-sm text-gray-900">{name}</td>
                      <td className="px-4 py-3 text-sm text-gray-600 text-right font-mono">
                        {feature.feature_index}
                      </td>
                      <td className="px-4 py-3 text-sm text-right">
                        <div className="flex items-center justify-end gap-2">
                          <div
                            className="w-3 h-3 rounded"
                            style={{ backgroundColor: barColor }}
                          />
                          <span className="font-mono">{feature.collapse_score.toFixed(4)}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-right font-medium text-gray-900">
                        {feature.contribution_pct.toFixed(2)}%
                      </td>
                      <td className="px-4 py-3 text-sm text-right text-gray-600">
                        {feature.cumulative.toFixed(1)}%
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Info Panel */}
      <div className="bg-blue-50 rounded-lg border border-blue-200 p-4">
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
          <div className="text-sm text-blue-900">
            <p className="font-medium mb-2">Understanding the Collapse Map:</p>
            <ul className="space-y-1 text-xs">
              <li>• <strong>Collapse Score:</strong> Measures how much a feature overlaps with eigenvectors (higher = more redundancy)</li>
              <li>• <strong>Contribution %:</strong> How much this feature contributes to dimensional collapse</li>
              <li>• <strong>Cumulative:</strong> Running total of contributions (top features often account for 80-90% of collapse)</li>
              <li>• <strong>High scores indicate:</strong> Feature is highly correlated with others or is a derived/composite metric</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CollapseMapViewer;
