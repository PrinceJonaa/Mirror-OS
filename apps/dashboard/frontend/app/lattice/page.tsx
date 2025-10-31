'use client';

import { useState } from 'react';
import useSWR from 'swr';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import LatticePhasePlane from '@/components/visualizations/LatticePhasePlane';

interface LatticePoint {
  run_id: string;
  collapse_ratio: number;
  rfi: number;
  shape: string;
  status: string;
  created_at: string;
}

export default function LatticePage() {
  const [selectedRunId, setSelectedRunId] = useState<string | undefined>();

  const { data: latticeData, error, isLoading } = useSWR<{ points: LatticePoint[] }>(
    '/api/analytics/lattice-points',
    async (url: string) => {
      const res = await fetch(url);
      if (!res.ok) throw new Error('Failed to fetch lattice data');
      return res.json();
    }
  );

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading lattice data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 mb-4">Failed to load lattice data</div>
          <Link href="/" className="text-blue-600 hover:text-blue-800">
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

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
          <h1 className="text-3xl font-bold text-gray-900">Lattice Phase Plane</h1>
          <p className="text-gray-600 mt-2">
            Explore all completed diagnostic runs on the relational coherence phase plane.
            Each point represents a system's position in the lattice of truth and distortion.
          </p>
        </div>

        {/* Visualization */}
        <div className="bg-white shadow rounded-lg p-6">
          {latticeData?.points && latticeData.points.length > 0 ? (
            <LatticePhasePlane
              points={latticeData.points}
              activeRunId={selectedRunId}
            />
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500">No completed runs available for lattice visualization.</p>
              <Link href="/" className="text-blue-600 hover:text-blue-800 mt-2 inline-block">
                Run a diagnostic to get started
              </Link>
            </div>
          )}
        </div>

        {/* Legend/Info */}
        {latticeData?.points && latticeData.points.length > 0 && (
          <div className="mt-6 bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Understanding the Lattice</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-medium text-gray-900 mb-2">X-Axis: RFI (Relational Field Index)</h3>
                <p className="text-sm text-gray-600">
                  Measures the strength and coherence of relational patterns. Higher values indicate
                  stronger field effects and more structured relational dynamics.
                </p>
              </div>
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Y-Axis: Collapse Ratio</h3>
                <p className="text-sm text-gray-600">
                  Quantifies the degree of dimensional reduction in the system's effective dynamics.
                  Lower values suggest more complex, higher-dimensional behavior.
                </p>
              </div>
            </div>
            <div className="mt-4">
              <h3 className="font-medium text-gray-900 mb-2">Lattice Zones</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div className="bg-green-50 p-3 rounded">
                  <div className="font-medium text-green-900">Truth Lattice</div>
                  <div className="text-green-700">High coherence, low collapse</div>
                </div>
                <div className="bg-red-50 p-3 rounded">
                  <div className="font-medium text-red-900">Irreducible Distortion</div>
                  <div className="text-red-700">High coherence, high collapse</div>
                </div>
                <div className="bg-blue-50 p-3 rounded">
                  <div className="font-medium text-blue-900">Coherent Structure</div>
                  <div className="text-blue-700">Low coherence, low collapse</div>
                </div>
                <div className="bg-yellow-50 p-3 rounded">
                  <div className="font-medium text-yellow-900">Chaotic Domain</div>
                  <div className="text-yellow-700">Low coherence, high collapse</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}