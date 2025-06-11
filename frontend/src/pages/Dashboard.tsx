import React from 'react';
import { Card, Row, Col, Typography, Table, Progress, Space } from 'antd';

const { Title, Text } = Typography;

const kpis = [
  { label: 'KPI 1', value: '[Value]' },
  { label: 'KPI 2', value: '[Value]' },
  { label: 'KPI 3', value: '[Value]' },
  { label: 'KPI 4', value: '[Value]' },
];

const levelColumns = [
  { title: 'Level', dataIndex: 'level', key: 'level' },
  { title: 'Value', dataIndex: 'value', key: 'value' },
];
const levelData = [
  { key: '1', level: 'A', value: 10 },
  { key: '2', level: 'B', value: 20 },
  { key: '3', level: 'C', value: 30 },
];

const growthDrivers = [
  { label: 'Driver 1', value: 40 },
  { label: 'Driver 2', value: 60 },
  { label: 'Driver 3', value: 80 },
];

export default function Dashboard() {
  return (
    <Space direction="vertical" size={24} style={{ width: '100%' }}>
      {/* KPI Cards Row */}
      <Row gutter={16}>
        {kpis.map(kpi => (
          <Col span={6} key={kpi.label}>
            <Card>
              <Title level={5}>{kpi.label}</Title>
              <Text strong style={{ fontSize: 24 }}>{kpi.value}</Text>
            </Card>
          </Col>
        ))}
      </Row>
      {/* Charts Row */}
      <Row gutter={16}>
        <Col span={12}>
          <Card style={{ height: 260, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#bfbfbf' }}>
            [Chart 1]
          </Card>
        </Col>
        <Col span={12}>
          <Card style={{ height: 260, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#bfbfbf' }}>
            [Chart 2]
          </Card>
        </Col>
      </Row>
      {/* Level Breakdown Table */}
      <Card title={<Title level={5} style={{ margin: 0 }}>Level Breakdown</Title>}>
        <Table columns={levelColumns} dataSource={levelData} pagination={false} />
      </Card>
      {/* Growth Drivers */}
      <Card title={<Title level={5} style={{ margin: 0 }}>Growth Drivers</Title>}>
        <Space direction="vertical" size={16} style={{ width: '100%' }}>
          {growthDrivers.map(driver => (
            <div key={driver.label}>
              <Row justify="space-between">
                <Col><Text>{driver.label}</Text></Col>
                <Col><Text strong>{driver.value}</Text></Col>
              </Row>
              <Progress percent={driver.value} showInfo={false} />
            </div>
          ))}
        </Space>
      </Card>
    </Space>
  );
} 