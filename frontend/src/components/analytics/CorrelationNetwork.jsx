import React, { useState } from 'react';
import { motion } from 'framer-motion';

const nodes = [
  { id: 'Peak_0.85V', label: 'Peak Voltage', x: 50, y: 15 },
  { id: 'Energy', label: 'Signal Energy', x: 85, y: 40 },
  { id: 'DCT_1', label: 'DCT 1', x: 75, y: 85 },
  { id: 'Mean', label: 'Mean', x: 25, y: 85 },
  { id: 'Kurtosis', label: 'Kurtosis', x: 15, y: 40 },
  { id: 'Skewness', label: 'Skewness', x: 50, y: 50 }, // Central node
];

const edges = [
  // Central connections
  { source: 0, target: 5, strength: 0.85 },
  { source: 1, target: 5, strength: 0.72 },
  { source: 2, target: 5, strength: 0.45 },
  { source: 3, target: 5, strength: 0.60 },
  { source: 4, target: 5, strength: 0.55 },
  // Perimeter connections
  { source: 0, target: 1, strength: 0.65 },
  { source: 1, target: 2, strength: 0.35 },
  { source: 2, target: 3, strength: 0.80 },
  { source: 3, target: 4, strength: 0.40 },
  { source: 4, target: 0, strength: 0.50 },
];

export default function CorrelationNetwork() {
  const [hoveredNode, setHoveredNode] = useState(null);

  return (
    <div className="glass-card flex flex-col relative" style={{ height: '320px', background: 'var(--dark-slate-dark)', color: 'white', overflow: 'hidden' }}>
      <h3 className="text-h3 mb-2" style={{ color: 'white', zIndex: 10 }}>Feature Correlation Network</h3>
      <p style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.6)', zIndex: 10 }}>
        Visualizing multi-collinearity between engineered e-tongue features. Thicker lines indicate stronger Pearson correlation.
      </p>

      <div style={{ flex: 1, position: 'relative', marginTop: '1rem' }}>
        <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet">
          
          {/* Edges */}
          {edges.map((edge, i) => {
            const sourceNode = nodes[edge.source];
            const targetNode = nodes[edge.target];
            const isHighlighted = hoveredNode === null || hoveredNode === edge.source || hoveredNode === edge.target;
            
            return (
              <motion.line
                key={`edge-${i}`}
                x1={sourceNode.x}
                y1={sourceNode.y}
                x2={targetNode.x}
                y2={targetNode.y}
                stroke={isHighlighted ? 'var(--primary-orange)' : 'rgba(255, 255, 255, 0.1)'}
                strokeWidth={edge.strength * 3}
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: isHighlighted ? edge.strength * 0.8 + 0.2 : 0.1 }}
                transition={{ duration: 1.5, delay: i * 0.1 }}
              />
            );
          })}

          {/* Nodes */}
          {nodes.map((node, i) => {
            const isHovered = hoveredNode === i;
            const isHighlighted = hoveredNode === null || hoveredNode === i || edges.some(e => (e.source === hoveredNode && e.target === i) || (e.target === hoveredNode && e.source === i));
            
            return (
              <g 
                key={`node-${i}`} 
                onMouseEnter={() => setHoveredNode(i)}
                onMouseLeave={() => setHoveredNode(null)}
                style={{ cursor: 'pointer' }}
              >
                <motion.circle
                  cx={node.x}
                  cy={node.y}
                  r={isHovered ? 6 : 4}
                  fill={isHighlighted ? 'var(--white)' : 'rgba(255, 255, 255, 0.3)'}
                  stroke={isHighlighted ? 'var(--primary-orange)' : 'none'}
                  strokeWidth={2}
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: 'spring', delay: i * 0.1 + 0.5 }}
                />
                
                <text
                  x={node.x}
                  y={node.y + (node.y > 50 ? 10 : -8)}
                  fontSize="4"
                  fill={isHighlighted ? 'var(--white)' : 'rgba(255, 255, 255, 0.3)'}
                  textAnchor="middle"
                  fontWeight={isHovered ? 'bold' : 'normal'}
                  style={{ pointerEvents: 'none', transition: 'all 0.3s' }}
                >
                  {node.label}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}
