'use client';
import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { Target, Zap, Filter, Search, Info, Play, Pause, RotateCcw, Maximize2 } from 'lucide-react';

/**
 * Node in the topology graph network.
 * Extends D3's SimulationNodeDatum for force-directed layout support.
 */
interface Node extends d3.SimulationNodeDatum {
  /** Unique identifier for the node (e.g., "feature_0") */
  id: string;
  /** Number of connections this node has to other nodes */
  degree: number;
  /** Community/cluster ID this node belongs to (for coloring) */
  community: number;
  /** Whether this node is pinned in place (user interaction) */
  pinned?: boolean;
}

/**
 * Edge connecting two nodes in the topology graph.
 * Extends D3's SimulationLinkDatum for force-directed layout support.
 */
interface Link extends d3.SimulationLinkDatum<Node> {
  /** Source node (string ID or Node object after D3 processing) */
  source: string | Node;
  /** Target node (string ID or Node object after D3 processing) */
  target: string | Node;
  /** Strength of the relationship (0-1, affects edge thickness) */
  weight: number;
}

/**
 * Props for the TopologyGraph component.
 */
interface TopologyGraphProps {
  /** Array of nodes to visualize */
  nodes: Node[];
  /** Array of edges connecting nodes */
  links: Link[];
}

/**
 * Interactive network visualization of feature topology.
 * 
 * Renders a force-directed graph showing relationships between features
 * in a diagnostic run. Supports interactive controls:
 * - Drag nodes to reposition
 * - Click to pin/unpin nodes
 * - Zoom and pan
 * - Search and filter by community
 * - Multiple layout modes (force, radial, circular)
 * 
 * Features:
 * - Community detection coloring
 * - Node sizing by degree centrality
 * - Real-time force simulation
 * - Adjustable physics parameters
 * - Selected node detail panel
 * 
 * @example
 * ```tsx
 * <TopologyGraph 
 *   nodes={[
 *     { id: 'feature_0', degree: 3, community: 0 },
 *     { id: 'feature_1', degree: 5, community: 0 }
 *   ]}
 *   links={[
 *     { source: 'feature_0', target: 'feature_1', weight: 0.85 }
 *   ]}
 * />
 * ```
 * 
 * @component
 */
const TopologyGraph: React.FC<TopologyGraphProps> = ({ nodes, links }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [, setHoveredNode] = useState<Node | null>(null);
  const [highlightedCommunity, setHighlightedCommunity] = useState<number | null>(null);
  const [isPaused, setIsPaused] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [linkDistance, setLinkDistance] = useState(50);
  const [chargeStrength, setChargeStrength] = useState(-100);
  const [showLabels, setShowLabels] = useState(true);
  const [layoutMode, setLayoutMode] = useState<'force' | 'radial' | 'circular'>('force');
  const simulationRef = useRef<d3.Simulation<Node, Link> | null>(null);

  useEffect(() => {
    if (!svgRef.current || !containerRef.current || !nodes.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    // Responsive dimensions
    const containerWidth = containerRef.current.clientWidth;
    const width = Math.max(containerWidth, 600); // Minimum 600px
    const height = Math.min(width * 0.75, 600); // 4:3 aspect ratio, max 600px

    svg.attr('viewBox', `0 0 ${width} ${height}`)
      .attr('preserveAspectRatio', 'xMidYMid meet')
      .attr('width', '100%')
      .attr('height', '100%');

    // Create main group for zoom/pan
    const g = svg.append('g');

    // Color scale for communities
    const communityIds = [...new Set(nodes.map(n => n.community))];
    const colorScale = d3.scaleOrdinal(d3.schemeCategory10).domain(communityIds.map(String));

    // Size scale for degrees
    const degreeExtent = d3.extent(nodes, d => d.degree) as [number, number];
    const sizeScale = d3.scaleLinear()
      .domain(degreeExtent[0] === degreeExtent[1] ? [0, degreeExtent[1] || 1] : degreeExtent)
      .range([6, 20]);

    // Boundary force to keep nodes within viewport
    const boundaryPadding = 30;
    const boundaryForce = () => {
      nodes.forEach(node => {
        if (!node.pinned) {
          // Keep nodes within bounds with soft constraints
          if (node.x !== undefined) {
            node.x = Math.max(boundaryPadding, Math.min(width - boundaryPadding, node.x));
          }
          if (node.y !== undefined) {
            node.y = Math.max(boundaryPadding, Math.min(height - boundaryPadding, node.y));
          }
        }
      });
    };

    // Create simulation based on layout mode
    let simulation: d3.Simulation<Node, Link>;
    
    if (layoutMode === 'radial') {
      // Radial layout by community
      simulation = d3.forceSimulation<Node>(nodes)
        .force('link', d3.forceLink<Node, Link>(links).id(d => d.id).distance(linkDistance))
        .force('charge', d3.forceManyBody().strength(chargeStrength / 2))
        .force('r', d3.forceRadial<Node>(d => d.community * 80 + 100, width / 2, height / 2))
        .force('boundary', boundaryForce);
    } else if (layoutMode === 'circular') {
      // Circular layout
      simulation = d3.forceSimulation<Node>(nodes)
        .force('link', d3.forceLink<Node, Link>(links).id(d => d.id).distance(linkDistance))
        .force('charge', d3.forceManyBody().strength(chargeStrength / 3))
        .force('boundary', boundaryForce);
      
      // Position nodes in circle
      nodes.forEach((node, i) => {
        const angle = (i / nodes.length) * 2 * Math.PI;
        node.x = width / 2 + Math.cos(angle) * 200;
        node.y = height / 2 + Math.sin(angle) * 200;
      });
    } else {
      // Standard force layout
      simulation = d3.forceSimulation<Node>(nodes)
        .force('link', d3.forceLink<Node, Link>(links).id(d => d.id).distance(linkDistance))
        .force('charge', d3.forceManyBody().strength(chargeStrength))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide<Node>().radius(d => sizeScale(d.degree) + 5))
        .force('boundary', boundaryForce);
    }

    simulationRef.current = simulation;

    // Filter nodes based on search
    const filteredNodeIds = searchQuery 
      ? new Set(nodes.filter(n => n.id.toLowerCase().includes(searchQuery.toLowerCase())).map(n => n.id))
      : new Set(nodes.map(n => n.id));

    // Create links
    const link = g.append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(links)
      .enter().append('line')
      .attr('stroke', d => {
        const sourceNode = typeof d.source === 'object' ? d.source : nodes.find(n => n.id === d.source);
        const targetNode = typeof d.target === 'object' ? d.target : nodes.find(n => n.id === d.target);
        if (!sourceNode || !targetNode) return '#999';
        if (highlightedCommunity !== null && 
            (sourceNode.community === highlightedCommunity || targetNode.community === highlightedCommunity)) {
          return colorScale(highlightedCommunity.toString());
        }
        return '#999';
      })
      .attr('stroke-opacity', d => {
        const sourceNode = typeof d.source === 'object' ? d.source : nodes.find(n => n.id === d.source);
        const targetNode = typeof d.target === 'object' ? d.target : nodes.find(n => n.id === d.target);
        if (!sourceNode || !targetNode) return 0.1;
        if (searchQuery && !(filteredNodeIds.has(sourceNode.id) && filteredNodeIds.has(targetNode.id))) {
          return 0.1;
        }
        if (highlightedCommunity !== null && 
            sourceNode.community === highlightedCommunity && 
            targetNode.community === highlightedCommunity) {
          return 0.8;
        }
        return 0.3;
      })
      .attr('stroke-width', d => Math.sqrt(d.weight) * 2);

    // Create node groups
    const nodeGroup = g.append('g')
      .attr('class', 'nodes')
      .selectAll('g')
      .data(nodes)
      .enter().append('g')
      .attr('class', 'node-group')
      .style('cursor', 'pointer');

    // Add circles
    nodeGroup.append('circle')
      .attr('r', d => sizeScale(d.degree))
      .attr('fill', d => colorScale(d.community.toString()))
      .attr('stroke', d => {
        if (d.pinned) return '#ff6b6b';
        if (highlightedCommunity !== null && d.community === highlightedCommunity) return '#000';
        return '#fff';
      })
      .attr('stroke-width', d => {
        if (d.pinned) return 3;
        if (highlightedCommunity !== null && d.community === highlightedCommunity) return 2.5;
        return 1.5;
      })
      .attr('opacity', d => {
        if (searchQuery && !filteredNodeIds.has(d.id)) return 0.15;
        if (highlightedCommunity !== null && d.community !== highlightedCommunity) return 0.2;
        return 1;
      })
      .on('click', function(event, d) {
        event.stopPropagation();
        setSelectedNode(d);
        // Toggle pin
        d.pinned = !d.pinned;
        if (d.pinned) {
          d.fx = d.x;
          d.fy = d.y;
        } else {
          d.fx = null;
          d.fy = null;
        }
        d3.select(this)
          .attr('stroke', d.pinned ? '#ef4444' : '#fff') // Use Tailwind red-500 for pinned
          .attr('stroke-width', d.pinned ? 3 : 1.5);
      })
      .on('mouseenter', function(event, d) {
        setHoveredNode(d);
        d3.select(this)
          .transition()
          .duration(200)
          .attr('r', sizeScale(d.degree) * 1.3);
      })
      .on('mouseleave', function(event, d) {
        setHoveredNode(null);
        d3.select(this)
          .transition()
          .duration(200)
          .attr('r', sizeScale(d.degree));
      })
      .call(d3.drag<SVGCircleElement, Node>()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('drag', (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          if (!d.pinned) {
            d.fx = null;
            d.fy = null;
          }
        }));

    // Add labels
    nodeGroup.append('text')
      .text(d => d.id.replace('feature_', ''))
      .attr('font-size', '10px')
      .attr('dx', d => sizeScale(d.degree) + 3)
      .attr('dy', 3)
      .attr('fill', '#333')
      .attr('opacity', showLabels ? 0.8 : 0)
      .style('pointer-events', 'none');

    // Add pin indicator
    nodeGroup.append('circle')
      .attr('r', 3)
      .attr('fill', '#ef4444') // Use Tailwind red-500 for pinned indicator
      .attr('cx', d => sizeScale(d.degree) * 0.7)
      .attr('cy', d => -sizeScale(d.degree) * 0.7)
      .attr('opacity', d => d.pinned ? 1 : 0);

    // Zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom);

    // Update positions on tick
    simulation.on('tick', () => {
      link
        .attr('x1', d => (d.source as Node).x!)
        .attr('y1', d => (d.source as Node).y!)
        .attr('x2', d => (d.target as Node).x!)
        .attr('y2', d => (d.target as Node).y!);

      nodeGroup.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    // Pause/resume control
    if (isPaused) {
      simulation.stop();
    }

    return () => {
      simulation.stop();
    };
  }, [nodes, links, highlightedCommunity, searchQuery, linkDistance, chargeStrength, isPaused, showLabels, layoutMode]);

  // Calculate network statistics
  const stats = {
    totalNodes: nodes.length,
    totalLinks: links.length,
    communities: [...new Set(nodes.map(n => n.community))].length,
    avgDegree: nodes.length > 0 ? (nodes.reduce((sum, n) => sum + n.degree, 0) / nodes.length).toFixed(2) : 0,
    maxDegree: nodes.length > 0 ? Math.max(...nodes.map(n => n.degree)) : 0,
    density: nodes.length > 1 ? (2 * links.length / (nodes.length * (nodes.length - 1))).toFixed(3) : 0
  };

  const handleReset = () => {
    // Unpin all nodes
    nodes.forEach(n => {
      n.pinned = false;
      n.fx = null;
      n.fy = null;
    });
    setHighlightedCommunity(null);
    setSearchQuery('');
    setIsPaused(false);
    if (simulationRef.current) {
      simulationRef.current.alpha(1).restart();
    }
  };

  const handleRecallNodes = () => {
    // Move all nodes back within bounds
    const width = 800;
    const height = 600;
    const padding = 50;
    
    nodes.forEach(n => {
      // Unpin if outside bounds
      if (n.x !== undefined && (n.x < 0 || n.x > width)) {
        n.pinned = false;
        n.fx = null;
        n.fy = null;
      }
      if (n.y !== undefined && (n.y < 0 || n.y > height)) {
        n.pinned = false;
        n.fx = null;
        n.fy = null;
      }
      
      // Bring nodes back to center area if they're off-screen
      if (n.x !== undefined && n.x < 0) n.x = padding;
      if (n.x !== undefined && n.x > width) n.x = width - padding;
      if (n.y !== undefined && n.y < 0) n.y = padding;
      if (n.y !== undefined && n.y > height) n.y = height - padding;
    });
    
    if (simulationRef.current) {
      simulationRef.current.alpha(0.5).restart();
    }
  };

  const handleCenterGraph = () => {
    if (!svgRef.current) return;
    const svg = d3.select(svgRef.current);
    const zoomBehavior = d3.zoom<SVGSVGElement, unknown>().transform;
    svg.transition()
      .duration(750)
      .call(zoomBehavior, d3.zoomIdentity);
  };

  const handleFindCentral = () => {
    const centralNode = nodes.reduce((max, node) => node.degree > max.degree ? node : max, nodes[0]);
    if (centralNode) {
      setSelectedNode(centralNode);
      setSearchQuery(centralNode.id);
    }
  };

  return (
    <div className="w-full h-full min-h-[700px] flex flex-col lg:flex-row gap-4">
      {/* Sidebar Controls */}
      <div className="lg:w-64 space-y-4">
        {/* Stats Panel */}
        <div className="bg-white rounded-lg border p-4 shadow-sm">
          <h3 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
            <Info className="w-4 h-4" />
            Network Stats
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-700 font-medium">Nodes:</span>
              <span className="font-semibold text-gray-900">{stats.totalNodes}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-700 font-medium">Links:</span>
              <span className="font-semibold text-gray-900">{stats.totalLinks}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-700 font-medium">Communities:</span>
              <span className="font-semibold text-gray-900">{stats.communities}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-700 font-medium">Avg Degree:</span>
              <span className="font-semibold text-gray-900">{stats.avgDegree}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-700 font-medium">Max Degree:</span>
              <span className="font-semibold text-gray-900">{stats.maxDegree}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-700 font-medium">Density:</span>
              <span className="font-semibold text-gray-900">{stats.density}</span>
            </div>
          </div>
        </div>

        {/* Search */}
        <div className="bg-white rounded-lg border p-4 shadow-sm">
          <h3 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
            <Search className="w-4 h-4" />
            Search Nodes
          </h3>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by ID..."
            className="w-full px-3 py-2 text-sm border rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="mt-2 text-xs text-blue-600 hover:text-blue-800 font-medium"
            >
              Clear search
            </button>
          )}
        </div>

        {/* Community Filter */}
        <div className="bg-white rounded-lg border p-4 shadow-sm">
          <h3 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
            <Filter className="w-4 h-4" />
            Communities
          </h3>
          <div className="space-y-1">
            {[...new Set(nodes.map(n => n.community))].sort((a, b) => a - b).map(comm => (
              <button
                key={comm}
                onClick={() => setHighlightedCommunity(highlightedCommunity === comm ? null : comm)}
                className={`w-full text-left px-3 py-2 text-sm rounded transition-colors ${
                  highlightedCommunity === comm
                    ? 'bg-blue-100 text-blue-800 font-semibold'
                    : 'bg-gray-50 text-gray-700 hover:bg-gray-100 font-medium'
                }`}
              >
                <span className="inline-block w-3 h-3 rounded-full mr-2" 
                  style={{ backgroundColor: d3.schemeCategory10[comm % 10] }}
                />
                Community {comm} ({nodes.filter(n => n.community === comm).length} nodes)
              </button>
            ))}
          </div>
        </div>

        {/* Layout Controls */}
        <div className="bg-white rounded-lg border p-4 shadow-sm">
          <h3 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
            <Zap className="w-4 h-4" />
            Layout
          </h3>
          <div className="space-y-3">
            <div>
              <label className="text-xs font-medium text-gray-700 block mb-1">Mode</label>
              <select
                value={layoutMode}
                onChange={(e) => setLayoutMode(e.target.value as 'force' | 'radial' | 'circular')}
                className="w-full text-sm border rounded px-2 py-1.5 font-medium"
              >
                <option value="force">Force-Directed</option>
                <option value="radial">Radial (by community)</option>
                <option value="circular">Circular</option>
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-gray-700 block mb-1">
                Link Distance: {linkDistance}
              </label>
              <input
                type="range"
                min="10"
                max="150"
                value={linkDistance}
                onChange={(e) => setLinkDistance(Number(e.target.value))}
                className="w-full"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-700 block mb-1">
                Charge: {chargeStrength}
              </label>
              <input
                type="range"
                min="-300"
                max="-10"
                value={chargeStrength}
                onChange={(e) => setChargeStrength(Number(e.target.value))}
                className="w-full"
              />
            </div>
            <div className="flex items-center justify-between">
              <label className="text-xs font-medium text-gray-700">Show Labels</label>
              <button
                onClick={() => setShowLabels(!showLabels)}
                className={`px-2 py-1 text-xs font-semibold rounded ${
                  showLabels ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-600'
                }`}
              >
                {showLabels ? 'ON' : 'OFF'}
              </button>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="bg-white rounded-lg border p-4 shadow-sm">
          <h3 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
            <Target className="w-4 h-4" />
            Actions
          </h3>
          <div className="space-y-2">
            <button
              onClick={() => setIsPaused(!isPaused)}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 text-xs bg-blue-50 text-blue-700 rounded hover:bg-blue-100 transition-colors"
            >
              {isPaused ? <Play className="w-3 h-3" /> : <Pause className="w-3 h-3" />}
              {isPaused ? 'Resume' : 'Pause'} Simulation
            </button>
            <button
              onClick={handleFindCentral}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 text-xs bg-purple-50 text-purple-700 rounded hover:bg-purple-100 transition-colors"
            >
              <Target className="w-3 h-3" />
              Find Central Node
            </button>
            <button
              onClick={handleRecallNodes}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 text-xs bg-orange-50 text-orange-700 rounded hover:bg-orange-100 transition-colors"
            >
              <Target className="w-3 h-3" />
              Recall Lost Nodes
            </button>
            <button
              onClick={handleCenterGraph}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 text-xs bg-green-50 text-green-700 rounded hover:bg-green-100 transition-colors"
            >
              <Maximize2 className="w-3 h-3" />
              Center View
            </button>
            <button
              onClick={handleReset}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 text-xs bg-red-50 text-red-700 rounded hover:bg-red-100 transition-colors"
            >
              <RotateCcw className="w-3 h-3" />
              Reset All
            </button>
          </div>
        </div>

        {/* Node Info */}
        {selectedNode && (
          <div className="bg-white rounded-lg border p-4 shadow-sm">
            <h3 className="text-sm font-bold text-gray-900 mb-3">Selected Node</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-700 font-medium">ID:</span>
                <span className="font-semibold text-gray-900">{selectedNode.id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-700 font-medium">Degree:</span>
                <span className="font-semibold text-gray-900">{selectedNode.degree}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-700 font-medium">Community:</span>
                <span className="font-semibold text-gray-900">{selectedNode.community}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-700 font-medium">Status:</span>
                <span className="font-semibold text-gray-900">{selectedNode.pinned ? '📌 Pinned' : 'Free'}</span>
              </div>
            </div>
            <p className="mt-3 text-xs text-gray-600 italic font-medium">
              Click node again to {selectedNode.pinned ? 'unpin' : 'pin'}
            </p>
          </div>
        )}

        {/* Help */}
        <div className="bg-blue-50 rounded-lg border border-blue-200 p-3">
          <h4 className="text-xs font-bold text-blue-900 mb-2">💡 Tips</h4>
          <ul className="text-xs text-blue-800 space-y-1 font-medium">
            <li>• Drag nodes to reposition</li>
            <li>• Click to pin/unpin nodes</li>
            <li>• Scroll to zoom in/out</li>
            <li>• Hover for quick info</li>
            <li>• Filter by community</li>
          </ul>
        </div>
      </div>

      {/* Main Graph */}
      <div ref={containerRef} className="flex-1 bg-white rounded-lg border shadow-sm">
        <svg ref={svgRef} className="w-full h-full min-h-[400px] md:min-h-[600px]"></svg>
      </div>
    </div>
  );
};

export default TopologyGraph;