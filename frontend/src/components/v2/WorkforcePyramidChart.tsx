import React from 'react';

// Define the props for the chart
export interface WorkforcePyramidData {
  level: string; // e.g., 'A', 'AC', ...
  fte: number;
  journey: string; // e.g., 'Journey 1', ...
}

interface WorkforcePyramidChartProps {
  data: WorkforcePyramidData[];
  height?: number;
  width?: number;
}

// Color mapping for journeys (customize as needed)
const journeyColors: Record<string, string> = {
  'Journey 1': '#1890ff',
  'Journey 2': '#52c41a',
  'Journey 3': '#faad14',
  'Journey 4': '#f5222d',
};

const levelOrder = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP'];

const WorkforcePyramidChart: React.FC<WorkforcePyramidChartProps> = ({ data, height = 400, width = 350 }) => {
  // Sort and prepare data
  const sortedData = [...data].sort((a, b) => levelOrder.indexOf(a.level) - levelOrder.indexOf(b.level));
  const totalFTE = sortedData.reduce((sum, d) => sum + d.fte, 0);
  const dataWithPercent = sortedData.map(d => ({ ...d, percent: d.fte / totalFTE * 100 }));
  const maxFTE = Math.max(...dataWithPercent.map(d => d.fte), 1);

  // Layout
  const barHeight = height / (dataWithPercent.length + 1);
  const barMaxWidth = width * 0.85;
  const centerX = width / 2;

  return (
    <svg width={width} height={height} style={{ display: 'block', margin: '0 auto' }}>
      {/* Bars */}
      {dataWithPercent.map((d, i) => {
        const barWidth = (d.fte / maxFTE) * barMaxWidth;
        const y = height - (i + 1) * barHeight;
        return (
          <g key={d.level}>
            <rect
              x={centerX - barWidth / 2}
              y={y}
              width={barWidth}
              height={barHeight * 0.7}
              fill={journeyColors[d.journey] || '#888'}
              rx={6}
            />
            <text
              x={centerX}
              y={y + barHeight * 0.45}
              textAnchor="middle"
              alignmentBaseline="middle"
              fontWeight={600}
              fontSize={Math.max(14, barHeight * 0.28)}
              fill="#fff"
              style={{ pointerEvents: 'none' }}
            >
              {`${d.fte} (${d.percent.toFixed(0)}%)`}
            </text>
            {/* Level label on left */}
            <text
              x={centerX - barMaxWidth / 2 - 10}
              y={y + barHeight * 0.45}
              textAnchor="end"
              alignmentBaseline="middle"
              fontWeight={500}
              fontSize={Math.max(13, barHeight * 0.22)}
              fill="#444"
            >
              {d.level}
            </text>
          </g>
        );
      })}
      {/* Total label at top */}
      <text
        x={centerX}
        y={barHeight * 0.5}
        textAnchor="middle"
        fontWeight={600}
        fontSize={16}
        fill="#444"
      >
        {`Total = ${totalFTE}`}
      </text>
    </svg>
  );
};

// Example default data for development/testing
WorkforcePyramidChart.defaultProps = {
  data: [
    { level: 'A', fte: 40, journey: 'Journey 1' },
    { level: 'AC', fte: 35, journey: 'Journey 1' },
    { level: 'C', fte: 30, journey: 'Journey 1' },
    { level: 'SrC', fte: 25, journey: 'Journey 2' },
    { level: 'AM', fte: 20, journey: 'Journey 2' },
    { level: 'M', fte: 15, journey: 'Journey 3' },
    { level: 'SrM', fte: 10, journey: 'Journey 3' },
    { level: 'PiP', fte: 5, journey: 'Journey 4' },
  ],
};

export default WorkforcePyramidChart; 