'use client';
import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

/**
 * Node in the static topology graph.
 * Simpler than the interactive version - no pinning support.
 */
interface Node extends d3.SimulationNodeDatum {
  /** Unique identifier for the node (e.g., "feature_0") */
  id: string;
  /** Number of connections this node has */
  degree: number;
  /** Community/cluster ID for coloring */
  community: number;
}

/**
 * Edge connecting two nodes.
 */
interface Link extends d3.SimulationLinkDatum<Node> {
  /** Source node ID or object */
  source: string | Node;
  /** Target node ID or object */
  target: string | Node;
  /** Edge strength/weight */
  weight: number;
}

/**
 * Props for the static topology graph component.
 */
interface TopologyGraphStaticProps {
  /** Array of nodes to display */
  nodes: Node[];
  /** Array of edges between nodes */
  links: Link[];
  /** Display name for this run (shown in header) */
  runName?: string;
}

/**
 * Static (read-only) network visualization for comparison view.
 * 
 * Simplified version of TopologyGraph designed for side-by-side comparison.
 * Auto-stabilizes after 3 seconds and has no interactive controls.
 * Responsive sizing adapts to container width.
 * 
 * Features:
 * - Community-based coloring
 * - Node sizing by degree
 * - Labels for high-degree nodes (degree > 5)
 * - Auto-stopping simulation
 * - Zoom and pan support
 * - Responsive SVG sizing
 * 
 * Empty State:
 * Shows helpful message with icon when no data available.
 * 
 * @example
 * ```tsx
 * <TopologyGraphStatic 
 *   nodes={topologyData.nodes}
 *   links={topologyData.links}
 *   runName="Run 1: abc123"
 * />
 * ```
 * 
 * @component
 */
const TopologyGraphStatic: React.FC<TopologyGraphStaticProps> = ({ 
  nodes, 
  links, 
  runName = 'Run'
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!svgRef.current || !containerRef.current || !nodes.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    // Responsive dimensions based on container
    const containerWidth = containerRef.current.clientWidth;
    const width = containerWidth;
    const height = Math.min(containerWidth * 0.8, 500); // 4:5 aspect ratio, max 500px

    svg.attr('viewBox', `0 0 ${width} ${height}`)
      .attr('preserveAspectRatio', 'xMidYMid meet')
      .attr('width', '100%')
      .attr('height', '100%');

    const g = svg.append('g');

    // Community colors
    const communities = [...new Set(nodes.map(n => n.community))];
    const colorScale = d3.scaleOrdinal(d3.schemeCategory10).domain(communities.map(String));

    // Create simulation
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink<Node, Link>(links)
        .id(d => d.id)
        .distance(50))
      .force('charge', d3.forceManyBody().strength(-100))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(15))
      .force('x', d3.forceX(width / 2).strength(0.1))
      .force('y', d3.forceY(height / 2).strength(0.1));

    // Draw links
    const link = g.append('g')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.3)
      .attr('stroke-width', (d: Link) => Math.sqrt(d.weight || 1));

    // Draw nodes
    const node = g.append('g')
      .selectAll('circle')
      .data(nodes)
      .join('circle')
      .attr('r', (d: Node) => 4 + Math.sqrt(d.degree || 1) * 2)
      .attr('fill', (d: Node) => colorScale(String(d.community)))
      .attr('stroke', '#fff')
      .attr('stroke-width', 1.5);

    // Add labels for high-degree nodes
    const labels = g.append('g')
      .selectAll('text')
      .data(nodes.filter((d: Node) => d.degree > 5))
      .join('text')
      .text((d: Node) => d.id)
      .attr('font-size', 10)
      .attr('dx', 8)
      .attr('dy', 3)
      .attr('fill', '#666')
      .style('pointer-events', 'none');

    // Add tooltips
    node.append('title')
      .text((d: Node) => `${d.id}\nDegree: ${d.degree}\nCommunity: ${d.community}`);

    // Zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.5, 3])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom);

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: Link) => (d.source as Node).x!)
        .attr('y1', (d: Link) => (d.source as Node).y!)
        .attr('x2', (d: Link) => (d.target as Node).x!)
        .attr('y2', (d: Link) => (d.target as Node).y!);

      node
        .attr('cx', (d: Node) => d.x!)
        .attr('cy', (d: Node) => d.y!);

      labels
        .attr('x', (d: Node) => d.x!)
        .attr('y', (d: Node) => d.y!);
    });

    // Stop simulation after stabilization
    simulation.alpha(1).restart();
    setTimeout(() => simulation.stop(), 3000);

    return () => {
      simulation.stop();
    };
  }, [nodes, links]);

  if (!nodes.length) {
    return (
      <div className="flex items-center justify-center bg-gray-50 rounded-lg border-2 border-dashed border-gray-300 min-h-[300px]">
        <div className="text-center text-gray-500">
          <svg className="w-16 h-16 mx-auto mb-3 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <p className="text-sm font-medium">No Topology Data Available</p>
          <p className="text-xs mt-1 text-gray-400">Run: {runName}</p>
          <p className="text-xs mt-2 text-gray-400">This run may not have generated network data yet</p>
        </div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="border rounded-lg bg-white shadow-sm overflow-hidden">
      <div className="bg-gray-50 px-4 py-2 border-b">
        <h3 className="text-sm font-semibold text-gray-700">{runName}</h3>
        <p className="text-xs text-gray-500">
          {nodes.length} nodes, {links.length} links
        </p>
      </div>
      <div className="p-2">
        <svg ref={svgRef} className="w-full h-auto" style={{ minHeight: '300px', maxHeight: '500px' }} />
      </div>
    </div>
  );
};

export default TopologyGraphStatic;
