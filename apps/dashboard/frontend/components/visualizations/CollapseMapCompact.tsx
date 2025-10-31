'use client';
import React from 'react';
import * as d3 from 'd3';

/**
 * Feature with collapse/importance metrics.
 */
interface CollapseFeature {
  /** Display name of the feature */
  feature_name: string;
  /** Numeric index of the feature */
  feature_index: number;
  /** Percentage contribution to system behavior (0-100) */
  contribution_percent: number;
  /** Collapse score indicating feature importance (0-1) */
  collapse_score: number;
  /** Cumulative contribution up to and including this feature */
  cumulative_contribution: number;
  /** Rank position (1 = most important) */
  rank: number;
}

/**
 * Props for the compact collapse map component.
 */
interface CollapseMapCompactProps {
  /** Array of features ranked by importance */
  features: CollapseFeature[];
  /** Display name for this run */
  runName?: string;
  /** Number of top features to display (default: 10) */
  topN?: number;
}

/**
 * Compact visualization of feature importance rankings.
 * 
 * Shows top N features as horizontal bars colored by collapse score.
 * Designed for comparison view where space is limited.
 * 
 * Features:
 * - Viridis color scale based on collapse_score
 * - Rank numbers (#1, #2, etc.)
 * - Feature names and contribution percentages
 * - Responsive horizontal bars
 * 
 * Empty State:
 * Displays helpful icon and message when no data available.
 * 
 * @example
 * ```tsx
 * <CollapseMapCompact 
 *   features={collapseFeatures}
 *   runName="Run 1"
 *   topN={10}
 * />
 * ```
 * 
 * @component
 */
const CollapseMapCompact: React.FC<CollapseMapCompactProps> = ({ 
  features, 
  runName = 'Run',
  topN = 10
}) => {
  const topFeatures = features.slice(0, topN);
  
  // Color scale for collapse scores
  const colorScale = d3.scaleSequential(d3.interpolateViridis)
    .domain([
      Math.min(...topFeatures.map(f => f.collapse_score)),
      Math.max(...topFeatures.map(f => f.collapse_score))
    ]);

  if (!features.length) {
    return (
      <div className="border rounded-lg bg-white shadow-sm p-6">
        <div className="bg-gray-50 px-4 py-2 border-b -mx-6 -mt-6 mb-4">
          <h3 className="text-sm font-semibold text-gray-700">{runName}</h3>
        </div>
        <div className="flex flex-col items-center justify-center py-8 text-gray-500">
          <svg className="w-16 h-16 mb-3 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p className="text-sm font-medium">No Collapse Map Data</p>
          <p className="text-xs mt-1 text-gray-400">This run hasn&apos;t generated feature collapse data yet</p>
        </div>
      </div>
    );
  }

  return (
    <div className="border rounded-lg bg-white shadow-sm overflow-hidden">
      <div className="bg-gray-50 px-4 py-2 border-b">
        <h3 className="text-sm font-semibold text-gray-700">{runName}</h3>
        <p className="text-xs text-gray-500">
          Top {topN} collapse features
        </p>
      </div>
      
      <div className="p-4">
        <div className="space-y-2">
          {topFeatures.map((feature) => (
            <div key={feature.feature_index} className="flex items-center gap-2">
              <span className="text-xs font-medium text-gray-500 w-6">
                #{feature.rank}
              </span>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-medium text-gray-700 truncate">
                    {feature.feature_name}
                  </span>
                  <span className="text-xs font-semibold text-gray-900 ml-2">
                    {feature.contribution_percent.toFixed(2)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-300"
                    style={{
                      width: `${feature.contribution_percent}%`,
                      backgroundColor: colorScale(feature.collapse_score)
                    }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
        
        {features.length > topN && (
          <div className="mt-3 pt-3 border-t text-center">
            <p className="text-xs text-gray-500">
              +{features.length - topN} more features
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default CollapseMapCompact;
