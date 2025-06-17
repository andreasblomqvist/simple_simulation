import React, { useState } from 'react';
import { Card, Statistic, Tag, Tooltip, Typography, Modal, Row, Col, Table, Progress } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined, MinusOutlined, InfoCircleOutlined, ExpandOutlined, LineChartOutlined, FlagOutlined } from '@ant-design/icons';
import { useYearNavigation } from './YearNavigationProvider';

const { Text } = Typography;

// Types for KPI data
interface SparklineData {
  year: number;
  value: number;
  isProjected?: boolean;
}

interface KPICardProps {
  title: string;
  currentValue: number;
  previousValue?: number;
  unit?: string;
  prefix?: React.ReactNode;
  suffix?: string;
  target?: number;
  sparklineData?: SparklineData[];
  formatValue?: (value: number, unit?: string) => string;
  onClick?: () => void;
  className?: string;
  loading?: boolean;
  trend?: 'up' | 'down' | 'stable';
  description?: string;
  precision?: number;
}

// Year-over-Year change indicator component
const YearOverYearIndicator: React.FC<{
  currentValue: number;
  previousValue?: number;
  unit?: string;
  showTooltip?: boolean;
}> = ({ currentValue, previousValue, unit = '', showTooltip = true }) => {
  if (previousValue === undefined || previousValue === null) {
    return null;
  }

  // Calculate percentage change
  const change = previousValue !== 0 ? ((currentValue - previousValue) / Math.abs(previousValue)) * 100 : 0;
  const direction = change > 0 ? 'up' : change < 0 ? 'down' : 'stable';
  
  // Determine color and icon
  const getIndicatorProps = () => {
    switch (direction) {
      case 'up':
        return {
          color: '#52c41a',
          icon: <ArrowUpOutlined />,
          text: `+${Math.abs(change).toFixed(1)}%`
        };
      case 'down':
        return {
          color: '#f5222d',
          icon: <ArrowDownOutlined />,
          text: `-${Math.abs(change).toFixed(1)}%`
        };
      default:
        return {
          color: '#8c8c8c',
          icon: <MinusOutlined />,
          text: '0.0%'
        };
    }
  };

  const { color, icon, text } = getIndicatorProps();

  const indicator = (
    <div 
      style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: '4px',
        color,
        fontSize: '14px',
        fontWeight: 600
      }}
    >
      {icon}
      <span>{text}</span>
      {showTooltip && (
        <InfoCircleOutlined 
          style={{ fontSize: '12px', color: '#8c8c8c', marginLeft: '2px' }} 
        />
      )}
    </div>
  );

  if (!showTooltip) {
    return indicator;
  }

  return (
    <Tooltip
      title={
        <div>
          <div>Previous Year: {previousValue.toLocaleString()}{unit}</div>
          <div>Current Year: {currentValue.toLocaleString()}{unit}</div>
          <div style={{ color }}>
            Change: {direction === 'up' ? '+' : direction === 'down' ? '' : ''}{change.toFixed(1)}%
          </div>
        </div>
      }
      placement="top"
    >
      {indicator}
    </Tooltip>
  );
};

// Mini sparkline component (simplified version)
const MiniSparkline: React.FC<{
  data: SparklineData[];
  currentYear: number;
  height?: number;
}> = ({ data, currentYear, height = 40 }) => {
  if (!data || data.length === 0) return null;

  const maxValue = Math.max(...data.map(d => d.value));
  const minValue = Math.min(...data.map(d => d.value));
  const range = maxValue - minValue || 1;

  const points = data.map((point, index) => {
    const x = (index / (data.length - 1)) * 100;
    const y = height - ((point.value - minValue) / range) * height;
    return `${x},${y}`;
  }).join(' ');

  return (
    <div style={{ width: '100%', height }}>
      <svg width="100%" height="100%" viewBox={`0 0 100 ${height}`}>
        {/* Trend line */}
        <polyline
          points={points}
          fill="none"
          stroke="#1890ff"
          strokeWidth="2"
          opacity={0.8}
        />
        
        {/* Current year indicator */}
        {data.map((point, index) => {
          if (point.year === currentYear) {
            const x = (index / (data.length - 1)) * 100;
            const y = height - ((point.value - minValue) / range) * height;
            return (
              <circle
                key={point.year}
                cx={x}
                cy={y}
                r="3"
                fill="#1890ff"
                stroke="#ffffff"
                strokeWidth="2"
              />
            );
          }
          return null;
        })}
      </svg>
    </div>
  );
};

// Detailed view modal component
const KPIDetailModal: React.FC<{
  visible: boolean;
  onClose: () => void;
  title: string;
  currentValue: number;
  previousValue?: number;
  unit?: string;
  target?: number;
  sparklineData?: SparklineData[];
  description?: string;
  precision?: number;
}> = ({ 
  visible, 
  onClose, 
  title, 
  currentValue, 
  previousValue, 
  unit = '', 
  target, 
  sparklineData,
  description,
  precision = 1
}) => {
  const { selectedYear } = useYearNavigation();

  // Calculate detailed metrics
  const yearOverYearChange = previousValue ? ((currentValue - previousValue) / Math.abs(previousValue)) * 100 : 0;
  const targetProgress = target ? (currentValue / target) * 100 : undefined;
  const targetGap = target ? target - currentValue : undefined;

  // Historical data table
  const historicalData = sparklineData?.map(item => ({
    key: item.year,
    year: item.year,
    value: item.value,
    change: sparklineData.find(prev => prev.year === item.year - 1) 
      ? ((item.value - sparklineData.find(prev => prev.year === item.year - 1)!.value) / Math.abs(sparklineData.find(prev => prev.year === item.year - 1)!.value)) * 100
      : 0,
    isProjected: item.isProjected || false,
    isCurrent: item.year === selectedYear
  })) || [];

  const columns = [
    {
      title: 'Year',
      dataIndex: 'year',
      key: 'year',
      render: (year: number, record: any) => (
        <span style={{ fontWeight: record.isCurrent ? 'bold' : 'normal' }}>
          {year} {record.isCurrent && <Tag color="blue">Current</Tag>}
          {record.isProjected && <Tag color="orange">Projected</Tag>}
        </span>
      )
    },
    {
      title: 'Value',
      dataIndex: 'value',
      key: 'value',
      render: (value: number) => `${value.toLocaleString()}${unit}`
    },
    {
      title: 'YoY Change',
      dataIndex: 'change',
      key: 'change',
      render: (change: number) => {
        if (change === 0) return '-';
        const color = change > 0 ? '#52c41a' : '#f5222d';
        const icon = change > 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />;
        return (
          <span style={{ color }}>
            {icon} {Math.abs(change).toFixed(1)}%
          </span>
        );
      }
    }
  ];

  return (
    <Modal
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <LineChartOutlined />
          <span>{title} - Detailed View</span>
        </div>
      }
      open={visible}
      onCancel={onClose}
      footer={null}
      width={800}
      styles={{ body: { maxHeight: '70vh', overflowY: 'auto' } }}
    >
      {/* Key Metrics Overview */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={8}>
          <Card size="small">
            <Statistic
              title="Current Value"
              value={currentValue}
              precision={precision}
              suffix={unit}
              valueStyle={{ color: '#1890ff', fontSize: '20px' }}
            />
          </Card>
        </Col>
        
        {previousValue !== undefined && (
          <Col xs={24} sm={8}>
            <Card size="small">
              <Statistic
                title="YoY Change"
                value={Math.abs(yearOverYearChange)}
                precision={1}
                suffix="%"
                prefix={yearOverYearChange > 0 ? <ArrowUpOutlined /> : yearOverYearChange < 0 ? <ArrowDownOutlined /> : <MinusOutlined />}
                valueStyle={{ 
                  color: yearOverYearChange > 0 ? '#3f8600' : yearOverYearChange < 0 ? '#cf1322' : '#8c8c8c',
                  fontSize: '20px'
                }}
              />
            </Card>
          </Col>
        )}
        
        {target !== undefined && (
          <Col xs={24} sm={8}>
            <Card size="small">
              <Statistic
                title="Target Progress"
                value={targetProgress || 0}
                precision={0}
                suffix="%"
                prefix={<FlagOutlined />}
                valueStyle={{ 
                  color: (targetProgress || 0) >= 100 ? '#3f8600' : '#8c8c8c',
                  fontSize: '20px'
                }}
              />
              {targetGap !== undefined && (
                <div style={{ marginTop: '8px' }}>
                  <Progress 
                    percent={Math.min(targetProgress || 0, 100)} 
                    status={(targetProgress || 0) >= 100 ? 'success' : 'active'}
                    size="small"
                  />
                  <Typography.Text type="secondary" style={{ fontSize: '12px' }}>
                    {targetGap > 0 ? `${targetGap.toLocaleString()}${unit} to target` : 'Target achieved!'}
                  </Typography.Text>
                </div>
              )}
            </Card>
          </Col>
        )}
      </Row>

      {/* Description */}
      {description && (
        <div style={{ marginBottom: '24px', padding: '16px', backgroundColor: '#fafafa', borderRadius: '6px' }}>
          <Typography.Text>{description}</Typography.Text>
        </div>
      )}

      {/* Enhanced Sparkline Chart */}
      {sparklineData && sparklineData.length > 0 && (
        <div style={{ marginBottom: '24px' }}>
          <Typography.Title level={5} style={{ marginBottom: '16px' }}>Trend Analysis</Typography.Title>
          <div style={{ width: '100%', height: '120px', backgroundColor: '#fafafa', borderRadius: '6px', padding: '16px' }}>
            <MiniSparkline 
              data={sparklineData} 
              currentYear={selectedYear}
              height={88}
            />
          </div>
        </div>
      )}

      {/* Historical Data Table */}
      {historicalData.length > 0 && (
        <div>
          <Typography.Title level={5} style={{ marginBottom: '16px' }}>Historical Data</Typography.Title>
          <Table
            columns={columns}
            dataSource={historicalData}
            pagination={false}
            size="small"
            style={{ marginBottom: '16px' }}
            scroll={{ x: true }}
          />
        </div>
      )}

      {/* Insights */}
      <div style={{ marginTop: '24px', padding: '16px', backgroundColor: '#f6ffed', borderRadius: '6px', border: '1px solid #b7eb8f' }}>
        <Typography.Title level={5} style={{ marginBottom: '8px', color: '#389e0d' }}>
          📊 Key Insights
        </Typography.Title>
        <ul style={{ margin: 0, paddingLeft: '20px' }}>
          {yearOverYearChange > 0 && (
            <li style={{ color: '#389e0d', marginBottom: '4px' }}>
              Positive year-over-year growth of {Math.abs(yearOverYearChange).toFixed(1)}%
            </li>
          )}
          {yearOverYearChange < 0 && (
            <li style={{ color: '#cf1322', marginBottom: '4px' }}>
              Year-over-year decline of {Math.abs(yearOverYearChange).toFixed(1)}%
            </li>
          )}
          {target && (targetProgress || 0) >= 100 && (
            <li style={{ color: '#389e0d', marginBottom: '4px' }}>
              Target achieved! Currently at {targetProgress?.toFixed(0)}% of target
            </li>
          )}
          {target && (targetProgress || 0) < 100 && (
            <li style={{ color: '#d48806', marginBottom: '4px' }}>
              {(100 - (targetProgress || 0)).toFixed(0)}% remaining to reach target
            </li>
          )}
          {sparklineData && sparklineData.length >= 3 && (
            <li style={{ color: '#1890ff', marginBottom: '4px' }}>
              {sparklineData.length} years of historical data available for trend analysis
            </li>
          )}
        </ul>
      </div>
    </Modal>
  );
};

/**
 * EnhancedKPICard Component
 * 
 * Displays key performance indicators with enhanced features:
 * - Year-over-year change indicators with color coding
 * - Mini sparkline charts for trend visualization
 * - Target comparison and progress tracking
 * - Contextual tooltips and detailed information
 * - Click-to-expand functionality with detailed modal
 * - Responsive design for all screen sizes
 */
export const EnhancedKPICard: React.FC<KPICardProps> = ({
  title,
  currentValue,
  previousValue,
  unit = '',
  prefix,
  suffix,
  target,
  sparklineData,
  formatValue,
  onClick,
  className = '',
  loading = false,
  trend,
  description,
  precision = 1
}) => {
  const { selectedYear } = useYearNavigation();
  const [detailModalVisible, setDetailModalVisible] = useState(false);

  // Default value formatter
  const defaultFormatValue = (value: number, unit?: string) => {
    if (typeof value !== 'number' || isNaN(value)) return '-';
    
    // Format large numbers with appropriate suffixes
    if (Math.abs(value) >= 1000000000) {
      return `${(value / 1000000000).toFixed(precision)}B${unit}`;
    } else if (Math.abs(value) >= 1000000) {
      return `${(value / 1000000).toFixed(precision)}M${unit}`;
    } else if (Math.abs(value) >= 1000) {
      return `${(value / 1000).toFixed(precision)}K${unit}`;
    }
    
    return `${value.toFixed(precision)}${unit}`;
  };

  const valueFormatter = formatValue || defaultFormatValue;

  // Determine if target is met
  const targetMet = target !== undefined && currentValue >= target;
  const targetProgress = target !== undefined ? (currentValue / target) * 100 : undefined;

  const handleCardClick = () => {
    if (onClick) {
      onClick();
    } else {
      // Default behavior: show detailed view
      setDetailModalVisible(true);
    }
  };

  return (
    <>
      <Card
        className={`enhanced-kpi-card ${className} enhanced-kpi-card--clickable`}
        hoverable
        onClick={handleCardClick}
        loading={loading}
        style={{
          height: '220px',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          borderRadius: '8px',
          position: 'relative',
        }}
        bodyStyle={{ padding: '20px', height: '100%', display: 'flex', flexDirection: 'column' }}
        actions={[
          <Tooltip title="View detailed analysis">
            <ExpandOutlined key="expand" />
          </Tooltip>
        ]}
      >
        {/* Header */}
        <div style={{ marginBottom: '12px' }}>
          <Text type="secondary" style={{ fontSize: '14px', fontWeight: 500 }}>
            {title}
          </Text>
          {description && (
            <Tooltip title={description}>
              <InfoCircleOutlined 
                style={{ 
                  marginLeft: '6px', 
                  fontSize: '12px', 
                  color: '#8c8c8c',
                  cursor: 'help'
                }} 
              />
            </Tooltip>
          )}
        </div>

        {/* Main Value */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <Statistic
            value={currentValue}
            precision={precision}
            prefix={prefix}
            suffix={suffix}
            valueStyle={{
              fontSize: '28px',
              fontWeight: 'bold',
              color: '#262626',
              lineHeight: 1.2
            }}
            formatter={(value) => valueFormatter(Number(value), unit)}
          />
          
          {/* Year-over-Year Indicator */}
          <div style={{ marginTop: '8px' }}>
            <YearOverYearIndicator
              currentValue={currentValue}
              previousValue={previousValue}
              unit={unit}
            />
          </div>
        </div>

        {/* Context Information */}
        <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #f0f0f0' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            {previousValue !== undefined && (
              <div style={{ textAlign: 'left' }}>
                <Text type="secondary" style={{ fontSize: '12px' }}>Previous Year</Text>
                <div style={{ fontSize: '14px', fontWeight: 500 }}>
                  {valueFormatter(previousValue, unit)}
                </div>
              </div>
            )}
            
            {target !== undefined && (
              <div style={{ textAlign: 'right' }}>
                <Text type="secondary" style={{ fontSize: '12px' }}>Target</Text>
                <div style={{ 
                  fontSize: '14px', 
                  fontWeight: 500,
                  color: targetMet ? '#52c41a' : '#8c8c8c'
                }}>
                  {valueFormatter(target, unit)}
                  {targetProgress !== undefined && (
                    <Tag 
                      color={targetMet ? 'success' : 'default'} 
                      style={{ marginLeft: '4px', fontSize: '11px' }}
                    >
                      {targetProgress.toFixed(0)}%
                    </Tag>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Mini Sparkline */}
          {sparklineData && sparklineData.length > 0 && (
            <div style={{ marginTop: '8px' }}>
              <MiniSparkline 
                data={sparklineData} 
                currentYear={selectedYear}
                height={30}
              />
            </div>
          )}
        </div>
      </Card>

      {/* Detailed View Modal */}
      <KPIDetailModal
        visible={detailModalVisible}
        onClose={() => setDetailModalVisible(false)}
        title={title}
        currentValue={currentValue}
        previousValue={previousValue}
        unit={unit}
        target={target}
        sparklineData={sparklineData}
        description={description}
        precision={precision}
      />
    </>
  );
};

export default EnhancedKPICard; 