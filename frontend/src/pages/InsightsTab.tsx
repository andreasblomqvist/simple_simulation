import React from 'react';
import { Row, Col, Card, Typography, Divider } from 'antd';
import { EnhancedKPICard } from '../components/v2/EnhancedKPICard';
// import CombinedStackedBarChart from '../components/v2/CombinedStackedBarChart'; // Placeholder for the chart component

const { Title, Text } = Typography;

const InsightsTab: React.FC = () => {
  // Placeholder KPI data (replace with real data integration)
  const kpis = [
    { title: 'Growth', currentValue: 12.5, previousValue: 10.2, unit: '%', description: 'Total FTE growth vs. baseline' },
    { title: 'Non-debit Ratio', currentValue: 18.3, previousValue: 17.9, unit: '%', description: 'Share of non-debit FTEs' },
    { title: 'Net Revenue', currentValue: 739.5, previousValue: 700.0, unit: 'M SEK', description: 'Net sales for the year' },
    { title: 'EBITDA', currentValue: 129.3, previousValue: 120.0, unit: 'M SEK', description: 'Earnings before interest, taxes, depreciation' },
    { title: 'Margin', currentValue: 17.4, previousValue: 17.1, unit: '%', description: 'EBITDA margin' },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Title level={2} style={{ color: 'var(--ant-primary-color)' }}>Insights</Title>
      <Divider />
      {/* KPI Cards Section */}
      <Row gutter={[16, 16]} style={{ marginBottom: 32 }}>
        {kpis.map((kpi) => (
          <Col xs={24} sm={12} md={8} lg={6} key={kpi.title}>
            <EnhancedKPICard
              title={kpi.title}
              currentValue={kpi.currentValue}
              previousValue={kpi.previousValue}
              unit={kpi.unit}
              description={kpi.description}
            />
          </Col>
        ))}
      </Row>
      {/* Combined Stacked Bar Chart Section */}
      <Card title="Workforce Flows: Recruitment, Churn, Progression" style={{ marginBottom: 32 }}>
        {/* <CombinedStackedBarChart /> */}
        <div style={{ textAlign: 'center', color: '#888', padding: 40 }}>
          [Combined Stacked Bar Chart Placeholder]
        </div>
      </Card>
      {/* Additional Executive Insights Section */}
      <Card title="Executive Insights" style={{ marginBottom: 32 }}>
        <Text type="secondary">[Additional insights and charts will appear here]</Text>
      </Card>
    </div>
  );
};

export default InsightsTab; 