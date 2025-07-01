import React from 'react';
import { Card, Table, Button, Typography, Space } from 'antd';

const { Title } = Typography;

const years = [2025, 2026, 2027, 2028, 2029, 2030];
const offices = ['Group', 'Stockholm', 'Munich'];
const kpis = ['FTE', 'Growth%', 'Sales', 'EBITDA', 'EBITDA%', 'J-1', 'J-2', 'J-3'];

// Mock data: [{ office, kpi, 2025, 2026, ... }]
const mockResults = [
  { office: 'Group', kpi: 'FTE', 2025: 1500, 2026: 1600, 2027: 1700, 2028: 1800, 2029: 1900, 2030: 2000 },
  { office: 'Group', kpi: 'Growth%', 2025: '5%', 2026: '6%', 2027: '6%', 2028: '5%', 2029: '5%', 2030: '5%' },
  { office: 'Group', kpi: 'Sales', 2025: 3000, 2026: 3200, 2027: 3400, 2028: 3600, 2029: 3800, 2030: 4000 },
  { office: 'Group', kpi: 'EBITDA', 2025: 500, 2026: 600, 2027: 700, 2028: 800, 2029: 900, 2030: 1000 },
  { office: 'Group', kpi: 'EBITDA%', 2025: '16.7%', 2026: '18.8%', 2027: '20.6%', 2028: '22.2%', 2029: '23.7%', 2030: '25.0%' },
  { office: 'Group', kpi: 'J-1', 2025: '38%', 2026: '33%', 2027: '36%', 2028: '37%', 2029: '36%', 2030: '34%' },
  { office: 'Group', kpi: 'J-2', 2025: '50%', 2026: '54%', 2027: '50%', 2028: '45%', 2029: '41%', 2030: '36%' },
  { office: 'Group', kpi: 'J-3', 2025: '12%', 2026: '12%', 2027: '14%', 2028: '18%', 2029: '23%', 2030: '30%' },
  { office: 'Stockholm', kpi: 'FTE', 2025: 821, 2026: 850, 2027: 900, 2028: 950, 2029: 1000, 2030: 1050 },
  { office: 'Stockholm', kpi: 'Growth%', 2025: '4.0%', 2026: '3.5%', 2027: '5.9%', 2028: '5.6%', 2029: '5.3%', 2030: '5.0%' },
  { office: 'Stockholm', kpi: 'Sales', 2025: 1200, 2026: 1300, 2027: 1400, 2028: 1500, 2029: 1600, 2030: 1700 },
  { office: 'Stockholm', kpi: 'EBITDA', 2025: 200, 2026: 220, 2027: 250, 2028: 280, 2029: 310, 2030: 340 },
  { office: 'Stockholm', kpi: 'EBITDA%', 2025: '16.7%', 2026: '16.9%', 2027: '17.9%', 2028: '18.7%', 2029: '19.4%', 2030: '20.0%' },
  { office: 'Stockholm', kpi: 'J-1', 2025: '40%', 2026: '38%', 2027: '37%', 2028: '36%', 2029: '35%', 2030: '34%' },
  { office: 'Stockholm', kpi: 'J-2', 2025: '48%', 2026: '50%', 2027: '51%', 2028: '52%', 2029: '53%', 2030: '54%' },
  { office: 'Stockholm', kpi: 'J-3', 2025: '12%', 2026: '12%', 2027: '12%', 2028: '12%', 2029: '12%', 2030: '12%' },
  { office: 'Munich', kpi: 'FTE', 2025: 300, 2026: 320, 2027: 350, 2028: 380, 2029: 410, 2030: 440 },
  { office: 'Munich', kpi: 'Growth%', 2025: '5.0%', 2026: '6.7%', 2027: '9.4%', 2028: '8.6%', 2029: '7.9%', 2030: '7.3%' },
  { office: 'Munich', kpi: 'Sales', 2025: 600, 2026: 650, 2027: 700, 2028: 750, 2029: 800, 2030: 850 },
  { office: 'Munich', kpi: 'EBITDA', 2025: 80, 2026: 90, 2027: 110, 2028: 130, 2029: 150, 2030: 170 },
  { office: 'Munich', kpi: 'EBITDA%', 2025: '13.3%', 2026: '13.8%', 2027: '15.7%', 2028: '17.3%', 2029: '18.8%', 2030: '20.0%' },
  { office: 'Munich', kpi: 'J-1', 2025: '35%', 2026: '34%', 2027: '33%', 2028: '32%', 2029: '31%', 2030: '30%' },
  { office: 'Munich', kpi: 'J-2', 2025: '50%', 2026: '52%', 2027: '54%', 2028: '56%', 2029: '58%', 2030: '60%' },
  { office: 'Munich', kpi: 'J-3', 2025: '15%', 2026: '14%', 2027: '13%', 2028: '12%', 2029: '11%', 2030: '10%' },
];

const columns = [
  {
    title: 'Office',
    dataIndex: 'office',
    key: 'office',
    width: 120,
    render: (office: string, row: any, idx: number) => {
      // Only show office name on first KPI row for each office
      if (idx === 0 || mockResults[idx - 1].office !== office) {
        return <b>{office}</b>;
      }
      return '';
    },
  },
  {
    title: 'KPI',
    dataIndex: 'kpi',
    key: 'kpi',
    width: 120,
  },
  ...years.map(year => ({
    title: year.toString(),
    dataIndex: year,
    key: year,
    width: 100,
    align: 'right' as const,
  })),
];

interface ResultsTableProps {
  onNext: () => void;
  onBack: () => void;
}

const ResultsTable: React.FC<ResultsTableProps> = ({ onNext, onBack }) => {
  return (
    <Card title={<Title level={4} style={{ margin: 0 }}>Scenario Results</Title>} style={{ maxWidth: 1200, margin: '0 auto' }}>
      <Table
        columns={columns}
        dataSource={mockResults}
        pagination={false}
        size="middle"
        rowKey={(row) => `${row.office}-${row.kpi}`}
        bordered
        style={{ marginBottom: 24 }}
        scroll={{ x: true }}
      />
      <Space>
        <Button onClick={onBack}>Back</Button>
        <Button type="primary" onClick={onNext}>Next: Compare Scenarios</Button>
      </Space>
    </Card>
  );
};

export default ResultsTable; 