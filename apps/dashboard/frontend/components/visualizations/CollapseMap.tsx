"use client"

import { useEffect, useRef } from "react"
import * as d3 from "d3"

interface CollapsePattern {
  run_id: string
  collapse_ratio: number
  rfi: number
  stability_score: number
  coherence_index: number
  resonance_frequency: number
  harmonics: number[]
}

interface CollapseMapProps {
  data: CollapsePattern[]
  width?: number
  height?: number
}

export function CollapseMap({ data, width = 800, height = 400 }: CollapseMapProps) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!data?.length || !svgRef.current) return

    const svg = d3.select(svgRef.current)
    svg.selectAll("*").remove()

    // Set up dimensions and margins
    const margin = { top: 20, right: 120, bottom: 60, left: 80 }
    const innerWidth = width - margin.left - margin.right
    const innerHeight = height - margin.top - margin.bottom

    const g = svg
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`)

    // Create scales
    const xScale = d3.scaleLinear()
      .domain([0, 1])
      .range([0, innerWidth])

    const yScale = d3.scaleLinear()
      .domain([0, 1])
      .range([innerHeight, 0])

    const intensityScale = d3.scaleSequential(d3.interpolateInferno)
      .domain([0, 1])

    // Create a grid for the heatmap
    const gridSize = 40
    const gridX = Math.ceil(innerWidth / gridSize)
    const gridY = Math.ceil(innerHeight / gridSize)

    // For each grid cell, calculate average collapse pattern
    const gridData = []
    for (let i = 0; i < gridX; i++) {
      for (let j = 0; j < gridY; j++) {
        const xMin = i * gridSize / innerWidth
        const xMax = (i + 1) * gridSize / innerWidth
        const yMin = j * gridSize / innerHeight
        const yMax = (j + 1) * gridSize / innerHeight

        // Find data points in this grid cell
        const pointsInCell = data.filter(d => 
          d.collapse_ratio >= xMin && d.collapse_ratio < xMax &&
          d.rfi >= yMin && d.rfi < yMax
        )

        if (pointsInCell.length > 0) {
          const avgStability = d3.mean(pointsInCell, d => d.stability_score) || 0
          const avgCoherence = d3.mean(pointsInCell, d => d.coherence_index) || 0
          const avgResonance = d3.mean(pointsInCell, d => d.resonance_frequency) || 0

          // Combine metrics into intensity score
          const intensity = (avgStability + avgCoherence + (1 - Math.abs(avgResonance - 0.5))) / 3

          gridData.push({
            x: i,
            y: j,
            intensity,
            count: pointsInCell.length,
            avgStability,
            avgCoherence,
            avgResonance,
            xMin,
            xMax,
            yMin,
            yMax
          })
        }
      }
    }

    // Draw heatmap rectangles
    g.selectAll(".heat-rect")
      .data(gridData)
      .enter()
      .append("rect")
      .attr("class", "heat-rect")
      .attr("x", d => d.x * (innerWidth / gridX))
      .attr("y", d => d.y * (innerHeight / gridY))
      .attr("width", innerWidth / gridX)
      .attr("height", innerHeight / gridY)
      .attr("fill", d => intensityScale(d.intensity))
      .attr("stroke", "#fff")
      .attr("stroke-width", 1)
      .style("cursor", "pointer")
      .on("mouseover", function(event, d) {
        // Show tooltip
        const tooltip = g.selectAll(".tooltip").data([d])
        
        const tooltipEnter = tooltip.enter()
          .append("g")
          .attr("class", "tooltip")
          .style("opacity", 0)

        tooltipEnter.append("rect")
          .attr("x", d.x * (innerWidth / gridX) + 10)
          .attr("y", d.y * (innerHeight / gridY) - 10)
          .attr("width", 180)
          .attr("height", 90)
          .attr("fill", "white")
          .attr("stroke", "#ccc")
          .attr("rx", 4)

        tooltipEnter.append("text")
          .attr("x", d.x * (innerWidth / gridX) + 15)
          .attr("y", d.y * (innerHeight / gridY) + 10)
          .text(`Runs: ${d.count}`)
          .style("font-size", "12px")
          .style("font-weight", "bold")

        tooltipEnter.append("text")
          .attr("x", d.x * (innerWidth / gridX) + 15)
          .attr("y", d.y * (innerHeight / gridY) + 30)
          .text(`Stability: ${d.avgStability.toFixed(3)}`)
          .style("font-size", "11px")

        tooltipEnter.append("text")
          .attr("x", d.x * (innerWidth / gridX) + 15)
          .attr("y", d.y * (innerHeight / gridY) + 45)
          .text(`Coherence: ${d.avgCoherence.toFixed(3)}`)
          .style("font-size", "11px")

        tooltipEnter.append("text")
          .attr("x", d.x * (innerWidth / gridX) + 15)
          .attr("y", d.y * (innerHeight / gridY) + 60)
          .text(`Resonance: ${d.avgResonance.toFixed(3)}`)
          .style("font-size", "11px")

        tooltipEnter.append("text")
          .attr("x", d.x * (innerWidth / gridX) + 15)
          .attr("y", d.y * (innerHeight / gridY) + 75)
          .text(`Intensity: ${d.intensity.toFixed(3)}`)
          .style("font-size", "11px")

        g.selectAll(".tooltip")
          .transition()
          .duration(200)
          .style("opacity", 1)
      })
      .on("mouseout", function() {
        g.selectAll(".tooltip")
          .transition()
          .duration(500)
          .style("opacity", 0)
          .remove()
      })

    // Add axes
    g.append("g")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale))
      .append("text")
      .attr("x", innerWidth / 2)
      .attr("y", 40)
      .attr("fill", "black")
      .style("text-anchor", "middle")
      .text("Collapse Ratio")

    g.append("g")
      .call(d3.axisLeft(yScale))
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", -50)
      .attr("x", -innerHeight / 2)
      .attr("fill", "black")
      .style("text-anchor", "middle")
      .text("RFI (Relative Frequency Index)")

    // Add color scale legend
    const legendWidth = 20
    const legendHeight = 200
    const legend = g.append("g")
      .attr("transform", `translate(${innerWidth + 10}, 0)`)

    const legendScale = d3.scaleLinear()
      .domain([0, 1])
      .range([legendHeight, 0])

    const legendAxis = d3.axisRight(legendScale)

    const defs = svg.append("defs")
    const linearGradient = defs.append("linearGradient")
      .attr("id", "legend-gradient")
      .attr("x1", "0%")
      .attr("x2", "0%")
      .attr("y1", "0%")
      .attr("y2", "100%")

    linearGradient.selectAll("stop")
      .data(d3.range(0, 1.1, 0.1))
      .enter()
      .append("stop")
      .attr("offset", d => `${d * 100}%`)
      .attr("stop-color", d => intensityScale(d))

    legend.append("rect")
      .attr("width", legendWidth)
      .attr("height", legendHeight)
      .style("fill", "url(#legend-gradient)")

    legend.append("g")
      .attr("transform", `translate(${legendWidth}, 0)`)
      .call(legendAxis)

    legend.append("text")
      .attr("transform", `translate(${legendWidth/2}, -5)`)
      .style("text-anchor", "middle")
      .style("font-size", "12px")
      .text("Intensity")

  }, [data, width, height])

  if (!data?.length) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="mb-4">
          <h3 className="text-lg font-semibold">Collapse Pattern Heatmap</h3>
          <p className="text-gray-600">Loading collapse patterns...</p>
        </div>
        <div className="flex items-center justify-center h-96 text-gray-500">
          No collapse data available
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold">Collapse Pattern Heatmap</h3>
        <p className="text-gray-600">
          Spatial distribution of collapse patterns across collapse ratio and RFI dimensions
        </p>
      </div>
      <div>
        <svg ref={svgRef} className="w-full h-auto" />
        <div className="mt-4 text-sm text-gray-600">
          <p>• Each cell shows the average collapse pattern of runs in that region</p>
          <p>• Hover over cells to see detailed metrics</p>
          <p>• Color intensity indicates combined stability, coherence, and resonance values</p>
        </div>
      </div>
    </div>
  )
}