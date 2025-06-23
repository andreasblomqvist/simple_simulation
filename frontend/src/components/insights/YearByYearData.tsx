import React from 'react';
import { Row, Col, Card, Typography, Select, theme } from 'antd';

const { Title, Text } = Typography;
const { Option } = Select;
const { useToken } = theme;

interface YearByYearDataProps {
  simulationData: any;
  selectedYear: string;
  setSelectedYear: (year: string) => void;
  formatNumber: (value: number) => string;
}

const YearByYearData: React.FC<YearByYearDataProps> = ({
  simulationData,
  selectedYear,
  setSelectedYear,
  formatNumber
}) => {
  const { token } = useToken();

  if (!simulationData?.years) return null;

  const years = Object.keys(simulationData.years).sort();

  return (
    <Card title="Year-by-Year Financial Progression" style={{ marginBottom: 24 }}>
      <div style={{ marginBottom: 16 }}>
        <Text>Select Year: </Text>
        <Select 
          value={selectedYear} 
          onChange={setSelectedYear}
          style={{ width: 120, marginLeft: 8 }}
        >
          {years.map(year => (
            <Option key={year} value={year}>{year}</Option>
          ))}
        </Select>
      </div>

      {/* Multi-Year Comparison Table */}
      {years.length > 1 && (
        <Card size="small" title="Multi-Year Comparison" style={{ marginBottom: 16 }}>
          <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
            <Row gutter={[8, 8]} style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: 8 }}>
              <Col span={4}><Text strong>Year</Text></Col>
              <Col span={5}><Text strong>Revenue</Text></Col>
              <Col span={3}><Text strong>FTE</Text></Col>
              <Col span={5}><Text strong>EBITDA</Text></Col>
              <Col span={3}><Text strong>Margin</Text></Col>
              <Col span={4}><Text strong>Avg Rate</Text></Col>
            </Row>
            {years.map(year => {
              const yearData = simulationData.years[year];
              return (
                <Row key={year} gutter={[8, 8]} style={{ 
                  fontSize: '11px', 
                  marginBottom: 4,
                  backgroundColor: year === selectedYear ? token.colorPrimaryBg : 'transparent',
                  padding: '4px 0'
                }}>
                  <Col span={4}><Text strong>{year}</Text></Col>
                  <Col span={5}><Text>{formatNumber(yearData.total_revenue || 0)}</Text></Col>
                  <Col span={3}><Text>{yearData.total_fte || 0}</Text></Col>
                  <Col span={5}><Text>{formatNumber(yearData.ebitda || 0)}</Text></Col>
                  <Col span={3}><Text>{((yearData.margin || 0) * 100).toFixed(1)}%</Text></Col>
                  <Col span={4}><Text>{(yearData.avg_hourly_rate || 0).toFixed(0)} SEK</Text></Col>
                </Row>
              );
            })}
          </div>
        </Card>
      )}

      {selectedYear && simulationData.years[selectedYear] && (
        <div>
          <Title level={4}>Financial Summary for {selectedYear}</Title>
          
          {/* Year Financial Overview */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={12} md={6}>
              <Card size="small">
                <Text type="secondary">Total Revenue</Text>
                <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
                  {formatNumber(simulationData.years[selectedYear].total_revenue || 0)}
                </div>
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card size="small">
                <Text type="secondary">Total FTE</Text>
                <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
                  {simulationData.years[selectedYear].total_fte || 0}
                </div>
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card size="small">
                <Text type="secondary">EBITDA</Text>
                <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
                  {formatNumber(simulationData.years[selectedYear].ebitda || 0)}
                </div>
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card size="small">
                <Text type="secondary">Margin</Text>
                <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
                  {((simulationData.years[selectedYear].margin || 0) * 100).toFixed(1)}%
                </div>
              </Card>
            </Col>
          </Row>

          {/* Monthly Progression */}
          {simulationData.years[selectedYear].months && (
            <Card size="small" title={`Monthly Progression for ${selectedYear}`} style={{ marginBottom: 16 }}>
              <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                <Row gutter={[8, 8]} style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: 8 }}>
                  <Col span={3}><Text strong>Month</Text></Col>
                  <Col span={4}><Text strong>Revenue</Text></Col>
                  <Col span={3}><Text strong>FTE</Text></Col>
                  <Col span={4}><Text strong>EBITDA</Text></Col>
                  <Col span={3}><Text strong>Margin</Text></Col>
                  <Col span={4}><Text strong>Avg Rate</Text></Col>
                </Row>
                {Object.entries(simulationData.years[selectedYear].months).map(([month, data]: [string, any]) => (
                  <Row key={month} gutter={[8, 8]} style={{ fontSize: '11px', marginBottom: 4 }}>
                    <Col span={3}><Text>{month}</Text></Col>
                    <Col span={4}><Text>{formatNumber(data.revenue || 0)}</Text></Col>
                    <Col span={3}><Text>{data.total_fte || 0}</Text></Col>
                    <Col span={4}><Text>{formatNumber(data.ebitda || 0)}</Text></Col>
                    <Col span={3}><Text>{((data.margin || 0) * 100).toFixed(1)}%</Text></Col>
                    <Col span={4}><Text>{(data.avg_hourly_rate || 0).toFixed(0)} SEK</Text></Col>
                  </Row>
                ))}
              </div>
            </Card>
          )}
        </div>
      )}
    </Card>
  );
};

export default YearByYearData; 