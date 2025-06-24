import React from 'react';
import { Row, Col, Card, Typography, theme } from 'antd';

const { Text, Title } = Typography;
const { useToken } = theme;

interface KPIDisplaysProps {
  simulationData: any;
  formatNumber: (value: number) => string;
  selectedYear: string;
  setSelectedYear: (year: string) => void;
}

const KPIDisplays: React.FC<KPIDisplaysProps> = ({ 
  simulationData, 
  formatNumber, 
  selectedYear, 
  setSelectedYear 
}) => {
  const { token } = useToken();

  const getYearData = () => {
    if (!simulationData?.years?.[selectedYear]) {
      return { financial: null, growth: null, journeys: null };
    }

    const yearData = simulationData.years[selectedYear];
    return {
      financial: yearData.kpis?.financial || null,
      growth: yearData.kpis?.growth || null,
      journeys: yearData.kpis?.journeys || null
    };
  };

  // Local formatter for numbers (no K rounding)
  const formatNumberNoK = (value: number) => {
    if (typeof value !== 'number' || isNaN(value)) return '';
    return value.toLocaleString('sv-SE', { maximumFractionDigits: 0 });
  };

  const renderFinancialKPIs = () => {
    const data = getYearData();
    if (!data.financial) return null;

    const financial = data.financial;
    
    return (
      <Card 
        title="💰 Financial Performance"
        style={{ marginBottom: 24 }}
        extra={<Text type="secondary" style={{ fontSize: '12px' }}>Year {selectedYear}</Text>}
      >
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={6}>
            <Card size="small">
              <div style={{ textAlign: 'center' }}>
                <Title level={4} style={{ margin: 0, color: token.colorPrimary }}>
                  {formatNumber(financial.net_sales)}
                </Title>
                <Text type="secondary">Net Sales</Text>
              </div>
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card size="small">
              <div style={{ textAlign: 'center' }}>
                <Title level={4} style={{ margin: 0, color: token.colorSuccess }}>
                  {formatNumber(financial.ebitda)}
                </Title>
                <Text type="secondary">EBITDA</Text>
              </div>
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card size="small">
              <div style={{ textAlign: 'center' }}>
                <Title level={4} style={{ margin: 0, color: token.colorWarning }}>
                  {(financial.margin * 100).toFixed(1)}%
                </Title>
                <Text type="secondary">Margin</Text>
              </div>
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card size="small">
              <div style={{ textAlign: 'center' }}>
                <Title level={4} style={{ margin: 0, color: token.colorInfo }}>
                  {formatNumberNoK(financial.avg_hourly_rate)}
                </Title>
                <Text type="secondary">Avg Hourly Rate</Text>
              </div>
            </Card>
          </Col>
        </Row>
      </Card>
    );
  };

  const renderGrowthKPIs = () => {
    const data = getYearData();
    if (!data.growth) return null;

    const growth = data.growth;
    
    return (
      <Card 
        title="📈 Growth Metrics"
        style={{ marginBottom: 24 }}
        extra={<Text type="secondary" style={{ fontSize: '12px' }}>Year {selectedYear}</Text>}
      >
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={6}>
            <Card size="small">
              <div style={{ textAlign: 'center' }}>
                <Title level={4} style={{ margin: 0, color: token.colorPrimary }}>
                  {growth.current_total_fte}
                </Title>
                <Text type="secondary">Total FTE</Text>
              </div>
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card size="small">
              <div style={{ textAlign: 'center' }}>
                <Title level={4} style={{ margin: 0, color: token.colorSuccess }}>
                  {growth.non_debit_ratio.toFixed(1)}%
                </Title>
                <Text type="secondary">Non-Debit Ratio</Text>
              </div>
            </Card>
          </Col>
        </Row>
      </Card>
    );
  };

  const renderJourneyKPIs = () => {
    const data = getYearData();
    if (!data.journeys) return null;

    const journeys = data.journeys;
    
    return (
      <Card 
        title="🏢 Journey Distribution"
        style={{ marginBottom: 24 }}
        extra={<Text type="secondary" style={{ fontSize: '12px' }}>Year {selectedYear}</Text>}
      >
        <Row gutter={[16, 16]}>
          {Object.entries(journeys.journey_totals || {}).map(([journey, fte]) => (
            <Col xs={24} sm={12} md={6} key={journey}>
              <Card size="small">
                <div style={{ textAlign: 'center' }}>
                  <Title level={4} style={{ margin: 0, color: token.colorPrimary }}>
                    {fte as number}
                  </Title>
                  <Text type="secondary">{journey}</Text>
                </div>
              </Card>
            </Col>
          ))}
        </Row>
      </Card>
    );
  };

  return (
    <div>
      {renderFinancialKPIs()}
      {renderGrowthKPIs()}
      {renderJourneyKPIs()}
    </div>
  );
};

export default KPIDisplays; 