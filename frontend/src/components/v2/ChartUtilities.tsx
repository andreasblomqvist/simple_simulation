import React, { useState, useEffect, useRef } from 'react';
import { Typography, Tag, Button, Tooltip } from 'antd';
import { InfoCircleOutlined, ExclamationCircleOutlined, CheckCircleOutlined, WarningOutlined } from '@ant-design/icons';

const { Text } = Typography;

// Enhanced annotation types
export interface ChartAnnotation {
  id: string;
  year: number;
  month?: number;
  position: {
    x: number;
    y: number;
  };
  content: {
    title: string;
    description: string;
    type: 'milestone' | 'warning' | 'info' | 'success' | 'target';
    priority: 'high' | 'medium' | 'low';
  };
  visual: {
    color: string;
    icon: string;
    shape: 'circle' | 'square' | 'diamond';
  };
  interactive: {
    clickable: boolean;
    hoverable: boolean;
    expandable: boolean;
  };
  metadata?: {
    source?: string;
    confidence?: number;
    lastUpdated?: string;
  };
}

// Custom tooltip data structure
export interface TooltipData {
  title: string;
  items: TooltipItem[];
  footer?: string;
  position: { x: number; y: number };
  temporal?: {
    currentPeriod: string;
    previousPeriod?: string;
    trend?: 'up' | 'down' | 'stable';
    changePercent?: number;
  };
}

export interface TooltipItem {
  label: string;
  value: string | number;
  color?: string;
  unit?: string;
  change?: {
    value: number;
    type: 'absolute' | 'percentage';
  };
  significance?: 'high' | 'medium' | 'low';
}

// Interactive Chart Annotation Component
interface ChartAnnotationProps {
  annotation: ChartAnnotation;
  onAnnotationClick?: (annotation: ChartAnnotation) => void;
  onAnnotationHover?: (annotation: ChartAnnotation | null) => void;
  isHighlighted?: boolean;
  scale?: number;
}

export const InteractiveAnnotation: React.FC<ChartAnnotationProps> = ({
  annotation,
  onAnnotationClick,
  onAnnotationHover,
  isHighlighted = false,
  scale = 1
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  const getAnnotationIcon = () => {
    switch (annotation.content.type) {
      case 'milestone': return <CheckCircleOutlined />;
      case 'warning': return <WarningOutlined />;
      case 'info': return <InfoCircleOutlined />;
      case 'success': return <CheckCircleOutlined />;
      case 'target': return <ExclamationCircleOutlined />;
      default: return <InfoCircleOutlined />;
    }
  };

  const getAnnotationColor = () => {
    switch (annotation.content.type) {
      case 'milestone': return '#722ed1';
      case 'warning': return '#faad14';
      case 'info': return '#1890ff';
      case 'success': return '#52c41a';
      case 'target': return '#ff4d4f';
      default: return '#8c8c8c';
    }
  };

  const handleClick = () => {
    if (annotation.interactive.clickable) {
      setIsExpanded(!isExpanded);
      onAnnotationClick?.(annotation);
    }
  };

  const handleMouseEnter = () => {
    if (annotation.interactive.hoverable) {
      setIsHovered(true);
      onAnnotationHover?.(annotation);
    }
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    onAnnotationHover?.(null);
  };

  const baseSize = 8 * scale;
  const expandedSize = 12 * scale;
  const size = isHovered || isHighlighted ? expandedSize : baseSize;

  return (
    <g 
      transform={`translate(${annotation.position.x}, ${annotation.position.y})`}
      onClick={handleClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      style={{ cursor: annotation.interactive.clickable ? 'pointer' : 'default' }}
    >
      {/* Annotation background */}
      <circle
        cx={0}
        cy={0}
        r={size + 2}
        fill="white"
        stroke={getAnnotationColor()}
        strokeWidth={2}
        opacity={0.9}
      />
      
      {/* Annotation shape */}
      {annotation.visual.shape === 'circle' && (
        <circle
          cx={0}
          cy={0}
          r={size}
          fill={getAnnotationColor()}
          opacity={isHovered || isHighlighted ? 1 : 0.8}
        />
      )}
      
      {annotation.visual.shape === 'square' && (
        <rect
          x={-size}
          y={-size}
          width={size * 2}
          height={size * 2}
          fill={getAnnotationColor()}
          rx={2}
          opacity={isHovered || isHighlighted ? 1 : 0.8}
        />
      )}
      
      {annotation.visual.shape === 'diamond' && (
        <polygon
          points={`0,${-size} ${size},0 0,${size} ${-size},0`}
          fill={getAnnotationColor()}
          opacity={isHovered || isHighlighted ? 1 : 0.8}
        />
      )}

      {/* Priority indicator */}
      {annotation.content.priority === 'high' && (
        <circle
          cx={size * 0.6}
          cy={-size * 0.6}
          r={3}
          fill="#ff4d4f"
          stroke="white"
          strokeWidth={1}
        />
      )}

      {/* Pulse animation for high priority */}
      {annotation.content.priority === 'high' && (
        <circle
          cx={0}
          cy={0}
          r={size + 4}
          fill="none"
          stroke={getAnnotationColor()}
          strokeWidth={1}
          opacity={0.5}
        >
          <animate
            attributeName="r"
            values={`${size + 4};${size + 8};${size + 4}`}
            dur="2s"
            repeatCount="indefinite"
          />
          <animate
            attributeName="opacity"
            values="0.5;0.1;0.5"
            dur="2s"
            repeatCount="indefinite"
          />
        </circle>
      )}

      {/* Connection line to chart element */}
      <line
        x1={0}
        y1={size + 2}
        x2={0}
        y2={size + 15}
        stroke={getAnnotationColor()}
        strokeWidth={1}
        strokeDasharray="2,2"
        opacity={0.6}
      />
    </g>
  );
};

// Enhanced Custom Tooltip Component
interface CustomTooltipProps {
  data: TooltipData;
  visible: boolean;
  onClose?: () => void;
  className?: string;
}

export const CustomChartTooltip: React.FC<CustomTooltipProps> = ({
  data,
  visible,
  onClose,
  className = ''
}) => {
  const tooltipRef = useRef<HTMLDivElement>(null);
  const [adjustedPosition, setAdjustedPosition] = useState(data.position);

  useEffect(() => {
    if (visible && tooltipRef.current) {
      const tooltip = tooltipRef.current;
      const rect = tooltip.getBoundingClientRect();
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;

      let { x, y } = data.position;

      // Adjust horizontal position
      if (x + rect.width > viewportWidth - 20) {
        x = viewportWidth - rect.width - 20;
      }
      if (x < 20) {
        x = 20;
      }

      // Adjust vertical position
      if (y + rect.height > viewportHeight - 20) {
        y = data.position.y - rect.height - 20;
      }
      if (y < 20) {
        y = 20;
      }

      setAdjustedPosition({ x, y });
    }
  }, [data.position, visible]);

  if (!visible) return null;

  const getTrendIcon = () => {
    if (!data.temporal?.trend) return null;
    
    switch (data.temporal.trend) {
      case 'up': return <span style={{ color: '#52c41a' }}>↗️</span>;
      case 'down': return <span style={{ color: '#ff4d4f' }}>↘️</span>;
      case 'stable': return <span style={{ color: '#8c8c8c' }}>➡️</span>;
      default: return null;
    }
  };

  const formatChange = (change: { value: number; type: 'absolute' | 'percentage' }) => {
    const sign = change.value >= 0 ? '+' : '';
    const suffix = change.type === 'percentage' ? '%' : '';
    return `${sign}${change.value.toFixed(1)}${suffix}`;
  };

  return (
    <div
      ref={tooltipRef}
      className={`custom-chart-tooltip ${className}`}
      style={{
        position: 'fixed',
        left: adjustedPosition.x,
        top: adjustedPosition.y,
        background: 'rgba(0, 0, 0, 0.9)',
        color: 'white',
        padding: '12px 16px',
        borderRadius: '8px',
        fontSize: '12px',
        pointerEvents: 'auto',
        zIndex: 1000,
        boxShadow: '0 8px 24px rgba(0, 0, 0, 0.4)',
        maxWidth: '300px',
        border: '1px solid rgba(255, 255, 255, 0.1)'
      }}
    >
      {/* Header */}
      <div style={{ 
        fontWeight: 'bold', 
        marginBottom: '8px', 
        display: 'flex', 
        alignItems: 'center', 
        gap: '8px',
        borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
        paddingBottom: '8px'
      }}>
        <span>{data.title}</span>
        {data.temporal && getTrendIcon()}
      </div>

      {/* Temporal context */}
      {data.temporal && (
        <div style={{ 
          marginBottom: '8px', 
          padding: '6px 8px', 
          background: 'rgba(255, 255, 255, 0.1)', 
          borderRadius: '4px',
          fontSize: '11px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>{data.temporal.currentPeriod}</span>
            {data.temporal.changePercent !== undefined && (
              <span style={{ 
                color: data.temporal.changePercent >= 0 ? '#52c41a' : '#ff4d4f',
                fontWeight: 'bold'
              }}>
                {data.temporal.changePercent >= 0 ? '+' : ''}{data.temporal.changePercent.toFixed(1)}%
              </span>
            )}
          </div>
          {data.temporal.previousPeriod && (
            <div style={{ color: '#d9d9d9', marginTop: '2px' }}>
              vs. {data.temporal.previousPeriod}
            </div>
          )}
        </div>
      )}

      {/* Data items */}
      <div style={{ marginBottom: '8px' }}>
        {data.items.map((item, index) => (
          <div 
            key={index}
            style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              marginBottom: '4px',
              alignItems: 'center'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              {item.color && (
                <div style={{ 
                  width: '8px', 
                  height: '8px', 
                  background: item.color, 
                  borderRadius: '50%' 
                }} />
              )}
              <span>{item.label}:</span>
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <span style={{ fontWeight: 'bold' }}>
                {typeof item.value === 'number' ? item.value.toLocaleString() : item.value}
                {item.unit && <span style={{ color: '#d9d9d9' }}> {item.unit}</span>}
              </span>
              
              {item.change && (
                <span style={{ 
                  color: item.change.value >= 0 ? '#52c41a' : '#ff4d4f',
                  fontSize: '10px'
                }}>
                  ({formatChange(item.change)})
                </span>
              )}
              
              {item.significance && (
                <div style={{ 
                  width: '4px', 
                  height: '4px', 
                  borderRadius: '50%',
                  background: item.significance === 'high' ? '#ff4d4f' : 
                             item.significance === 'medium' ? '#faad14' : '#52c41a'
                }} />
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      {data.footer && (
        <div style={{ 
          borderTop: '1px solid rgba(255, 255, 255, 0.2)', 
          paddingTop: '8px', 
          fontSize: '10px', 
          color: '#d9d9d9',
          fontStyle: 'italic'
        }}>
          {data.footer}
        </div>
      )}

      {/* Close button for persistent tooltips */}
      {onClose && (
        <Button
          type="text"
          size="small"
          onClick={onClose}
          style={{ 
            position: 'absolute', 
            top: '4px', 
            right: '4px', 
            color: 'white',
            width: '20px',
            height: '20px',
            minWidth: '20px',
            padding: 0
          }}
        >
          ×
        </Button>
      )}
    </div>
  );
};

// Year highlighting utilities
export interface YearHighlight {
  year: number;
  color: string;
  intensity: number; // 0-1
  label?: string;
}

export const createYearHighlight = (
  year: number,
  type: 'current' | 'target' | 'baseline' | 'comparison'
): YearHighlight => {
  const highlights = {
    current: { color: '#722ed1', intensity: 0.8, label: 'Current Year' },
    target: { color: '#52c41a', intensity: 0.6, label: 'Target Year' },
    baseline: { color: '#ff4d4f', intensity: 0.6, label: 'Baseline Year' },
    comparison: { color: '#1890ff', intensity: 0.4, label: 'Comparison Year' }
  };

  return {
    year,
    ...highlights[type]
  };
};

// Chart export utilities
export const exportChartData = (
  data: any[],
  filename: string,
  format: 'csv' | 'json' = 'csv'
) => {
  let content: string;
  let mimeType: string;
  let extension: string;

  if (format === 'csv') {
    const headers = Object.keys(data[0] || {});
    const csvRows = [
      headers.join(','),
      ...data.map(row => 
        headers.map(header => {
          const value = row[header];
          return typeof value === 'string' ? `"${value}"` : value;
        }).join(',')
      )
    ];
    content = csvRows.join('\n');
    mimeType = 'text/csv';
    extension = 'csv';
  } else {
    content = JSON.stringify(data, null, 2);
    mimeType = 'application/json';
    extension = 'json';
  }

  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${filename}.${extension}`;
  link.click();
  URL.revokeObjectURL(url);
};

// Responsive chart utilities
export const getResponsiveChartDimensions = (
  containerWidth: number,
  aspectRatio: number = 16/9,
  minHeight: number = 300,
  maxHeight: number = 600
) => {
  const calculatedHeight = containerWidth / aspectRatio;
  const height = Math.max(minHeight, Math.min(maxHeight, calculatedHeight));
  
  return {
    width: containerWidth,
    height,
    margin: {
      top: containerWidth < 768 ? 20 : 40,
      right: containerWidth < 768 ? 20 : 60,
      bottom: containerWidth < 768 ? 40 : 80,
      left: containerWidth < 768 ? 40 : 80
    }
  };
};

// Animation utilities
export const createChartAnimation = (
  duration: number = 1000,
  delay: number = 0,
  easing: string = 'ease-out'
) => ({
  initial: { opacity: 0, scale: 0.8 },
  animate: { opacity: 1, scale: 1 },
  transition: { duration: duration / 1000, delay: delay / 1000, ease: easing }
});

export default {
  InteractiveAnnotation,
  CustomChartTooltip,
  createYearHighlight,
  exportChartData,
  getResponsiveChartDimensions,
  createChartAnimation
}; 