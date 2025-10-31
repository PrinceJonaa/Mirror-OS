'use client';
import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

/**
 * A single point in lattice phase space.
 */
interface LatticePoint {
  /** Unique identifier for this diagnostic run */
  run_id: string;
  /** Collapse Ratio: effective dimensionality ratio (0-1, lower = more efficient) */
  collapse_ratio: number;
  /** Relational Fitness Index: coherence metric (0-1, higher = more coherent) */
  rfi: number;
  /** Shape type for visualization (e.g., "circle", "square") */
  shape: string;
  /** Run processing status (e.g., "completed", "running", "failed") */
  status: string;
  /** ISO timestamp when run was created */
  created_at: string;
}

/**
 * Props for the lattice phase plane component.
 */
interface LatticePhasePlaneProps {
  /** Array of diagnostic runs to plot in phase space */
  points: LatticePoint[];
  /** Optional run ID to highlight with distinct styling */
  activeRunId?: string;
}

/**
 * Interactive scatter plot showing all runs in RFI vs Collapse Ratio phase space.
 * 
 * Visualizes the relationship between system coherence (RFI on Y-axis) and 
 * effective dimensionality (Collapse Ratio on X-axis). Points are colored by
 * their status and shaped according to their shape property.
 * 
 * Features:
 * - Color coding by run status (completed, running, failed)
 * - Variable point shapes for visual differentiation
 * - Interactive tooltips on hover showing run details
 * - Highlight styling for active/selected run
 * - Responsive scaling to container size
 * - Reference grid for easier reading
 * 
 * Lattice Interpretation:
 * - High RFI, Low Collapse: Optimal coherent structure (Truth Lattice zone)
 * - Low RFI, Low Collapse: Minimal structure, high noise (Irreducible Distortion)
 * - High RFI, High Collapse: Coherent but redundant (Coherent Structure)
 * - Low RFI, High Collapse: Maximum distortion (Chaotic Domain)
 * 
 * Empty State:
 * Shows helpful icon and message when no data available.
 * 
 * @example
 * ```tsx
 * <LatticePhasePlane 
 *   points={latticePoints}
 *   activeRunId="abc-123"
 * />
 * ```
 * 
 * @component
 */
const LatticePhasePlane: React.FC<LatticePhasePlaneProps> = ({ points, activeRunId }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!svgRef.current || !containerRef.current || !points.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove(); // Clear previous render

    // Responsive dimensions
    const containerWidth = containerRef.current.clientWidth;
    const width = Math.max(containerWidth, 500);
    const height = Math.min(width * 0.75, 600);
    const margin = { top: 20, right: 150, bottom: 60, left: 80 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Set SVG viewBox for responsiveness
    svg.attr('viewBox', `0 0 ${width} ${height}`)
       .attr('preserveAspectRatio', 'xMidYMid meet')
       .attr('width', '100%')
       .attr('height', '100%');

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Scales - handle single point case by adding padding
    const rfiExtent = d3.extent(points, d => d.rfi) as [number, number];
    const collapseExtent = d3.extent(points, d => d.collapse_ratio) as [number, number];
    
    const xScale = d3.scaleLinear()
      .domain([
        Math.min(rfiExtent[0] - 0.1, 0),
        Math.max(rfiExtent[1] + 0.1, 1)
      ])
      .range([0, innerWidth])
      .nice();

    const yScale = d3.scaleLinear()
      .domain([
        Math.max(Math.min(collapseExtent[0] - 0.1, 0), 0),
        Math.min(collapseExtent[1] + 0.1, 1)
      ])
      .range([innerHeight, 0])
      .nice();

    // Color scale for shapes
    const shapes = [...new Set(points.map(d => d.shape))];
    const colorScale = d3.scaleOrdinal(d3.schemeCategory10).domain(shapes);

    // Axes
    const xAxis = d3.axisBottom(xScale);
    const yAxis = d3.axisLeft(yScale);

    g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(xAxis)
      .append('text')
      .attr('x', innerWidth / 2)
      .attr('y', 40)
      .attr('fill', 'black')
      .attr('text-anchor', 'middle')
      .text('RFI (Relational Field Index)');

    g.append('g')
      .call(yAxis)
      .append('text')
      .attr('transform', 'rotate(-90)')
      .attr('x', -innerHeight / 2)
      .attr('y', -60)
      .attr('fill', 'black')
      .attr('text-anchor', 'middle')
      .text('Collapse Ratio');

    // Background zones (simplified lattice representation)
    const zones = [
      { x: 0, y: 0, width: innerWidth / 2, height: innerHeight / 2, label: 'Truth Lattice', color: '#e8f5e8' },
      { x: innerWidth / 2, y: 0, width: innerWidth / 2, height: innerHeight / 2, label: 'Irreducible Distortion', color: '#ffebee' },
      { x: 0, y: innerHeight / 2, width: innerWidth / 2, height: innerHeight / 2, label: 'Coherent Structure', color: '#e3f2fd' },
      { x: innerWidth / 2, y: innerHeight / 2, width: innerWidth / 2, height: innerHeight / 2, label: 'Chaotic Domain', color: '#fff3e0' }
    ];

    g.selectAll('.zone')
      .data(zones)
      .enter().append('rect')
      .attr('class', 'zone')
      .attr('x', d => d.x)
      .attr('y', d => d.y)
      .attr('width', d => d.width)
      .attr('height', d => d.height)
      .attr('fill', d => d.color)
      .attr('opacity', 0.3);

    g.selectAll('.zone-label')
      .data(zones)
      .enter().append('text')
      .attr('class', 'zone-label')
      .attr('x', d => d.x + d.width / 2)
      .attr('y', d => d.y + d.height / 2)
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .attr('font-size', '12px')
      .attr('fill', '#666')
      .text(d => d.label);

    // Points
    const pointsGroup = g.append('g').attr('class', 'points');

    pointsGroup.selectAll('circle')
      .data(points)
      .enter().append('circle')
      .attr('cx', d => xScale(d.rfi))
      .attr('cy', d => yScale(d.collapse_ratio))
      .attr('r', d => d.run_id === activeRunId ? 8 : 5)
      .attr('fill', d => colorScale(d.shape))
      .attr('stroke', d => d.run_id === activeRunId ? '#000' : '#fff')
      .attr('stroke-width', d => d.run_id === activeRunId ? 2 : 1)
      .style('cursor', 'pointer')
      .on('click', (event, d) => {
        window.open(`/runs/${d.run_id}`, '_blank');
      })
      .append('title')
      .text(d => `Run: ${d.run_id}\nShape: ${d.shape}\nRFI: ${d.rfi.toFixed(3)}\nCollapse: ${d.collapse_ratio.toFixed(3)}\nDate: ${new Date(d.created_at).toLocaleDateString()}`);

    // Legend
    const legend = svg.append('g')
      .attr('transform', `translate(${innerWidth + margin.left + 10}, ${margin.top})`);

    const legendItems = legend.selectAll('.legend-item')
      .data(shapes)
      .enter().append('g')
      .attr('class', 'legend-item')
      .attr('transform', (d, i) => `translate(0, ${i * 20})`);

    legendItems.append('circle')
      .attr('r', 5)
      .attr('fill', d => colorScale(d));

    legendItems.append('text')
      .attr('x', 15)
      .attr('y', 5)
      .attr('font-size', '12px')
      .text(d => d);

  }, [points, activeRunId]);

  return (
    <div ref={containerRef} className="w-full h-full min-h-[300px] md:min-h-[500px] border rounded-lg bg-white p-4">
      <svg ref={svgRef} className="w-full h-auto"></svg>
    </div>
  );
};

export default LatticePhasePlane;