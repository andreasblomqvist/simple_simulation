import React from 'react';
import { Bar } from '@ant-design/charts';

export interface WorkforceStackedBarData {
  level: string; // e.g., 'A', 'AC', ...
  type: string; // e.g., 'Churned', 'Recruited', 'Progressed In' OR 'Consultant', 'Sales', 'Recruitment'
  value: number; // count for movements or fte for roles
}

interface WorkforceStackedBarChartProps {
  data?: WorkforceStackedBarData[];
  height?: number;
}

const movementColors: Record<string, string> = {
  'Churned': '#f5222d',        // Red for departures
  'Recruited': '#52c41a',      // Green for new hires  
  'Progressed In': '#1890ff',  // Blue for promotions in
};

const defaultData: WorkforceStackedBarData[] = [
  { level: 'A', type: 'Churned', value: 3 },
  { level: 'A', type: 'Recruited', value: 8 },
  { level: 'A', type: 'Progressed In', value: 0 },
  { level: 'AC', type: 'Churned', value: 2 },
  { level: 'AC', type: 'Recruited', value: 4 },
  { level: 'AC', type: 'Progressed In', value: 5 },
  { level: 'C', type: 'Churned', value: 2 },
  { level: 'C', type: 'Recruited', value: 2 },
  { level: 'C', type: 'Progressed In', value: 3 },
  { level: 'SrC', type: 'Churned', value: 1 },
  { level: 'SrC', type: 'Recruited', value: 1 },
  { level: 'SrC', type: 'Progressed In', value: 2 },
  { level: 'AM', type: 'Churned', value: 1 },
  { level: 'AM', type: 'Recruited', value: 1 },
  { level: 'AM', type: 'Progressed In', value: 1 },
  { level: 'M', type: 'Churned', value: 1 },
  { level: 'M', type: 'Recruited', value: 0 },
  { level: 'M', type: 'Progressed In', value: 1 },
  { level: 'SrM', type: 'Churned', value: 0 },
  { level: 'SrM', type: 'Recruited', value: 0 },
  { level: 'SrM', type: 'Progressed In', value: 1 },
  { level: 'PiP', type: 'Churned', value: 0 },
  { level: 'PiP', type: 'Recruited', value: 0 },
  { level: 'PiP', type: 'Progressed In', value: 0 },
];

const WorkforceStackedBarChart: React.FC<WorkforceStackedBarChartProps> = ({ data = defaultData, height = 300 }) => {
  const config = {
    data,
    isStack: true,
    xField: 'level',     // Levels on X-axis (A, AC, C, etc.)
    yField: 'value',     // Values on Y-axis (count/FTE)
    seriesField: 'type',
    color: (datum: WorkforceStackedBarData) => movementColors[datum.type] || '#888',
    legend: { position: 'top-right' },
    barWidthRatio: 0.7,
    height,
    label: {
      position: 'inside',
      style: { fill: '#fff', fontWeight: 600 },
      formatter: (datum: any) => datum.value > 0 ? `${datum.value}` : '',
    },
    tooltip: {
      customContent: (title: string, items: any[]) => {
        if (!items || items.length === 0) return null;
        return `<div style='padding:8px;'>
          <b>Level:</b> ${title}<br/>
          ${items.map(item => `<span style='color:${item.color}'>${item.name}:</span> ${item.value} people<br/>`).join('')}
        </div>`;
      },
    },
    animation: true,
  };
  return <Bar {...config} />;
};

export default WorkforceStackedBarChart; 