import React, { useState } from 'react';
import { Card, Table, Checkbox, Button, Typography, Space, List } from 'antd';

const { Title } = Typography;

const mockScenarios = [
  { id: 1, name: 'Oslo Growth Plan', created: '2025-07-01' },
  { id: 2, name: 'Stockholm Expansion', created: '2025-06-15' },
  { id: 3, name: 'Munich Conservative', created: '2025-06-10' },
];

const comparisonKPIs = ['FTE', 'Growth%', 'Sales', 'EBITDA', 'EBITDA%', 'J-1', 'J-2', 'J-3'];
const years = [2025, 2026, 2027, 2028, 2029, 2030];

// Mock comparison data: { [scenarioId]: { [kpi]: { [year]: value } } }
const mockComparisonData: Record<number, Record<string, Record<number, string | number>>> = {
  1: {
    FTE: { 2025: 1500, 2026: 1600, 2027: 1700, 2028: 1800, 2029: 1900, 2030: 2000 },
    'Growth%': { 2025: '5%', 2026: '6%', 2027: '6%', 2028: '5%', 2029: '5%', 2030: '5%' },
    Sales: { 2025: 3000, 2026: 3200, 2027: 3400, 2028: 3600, 2029: 3800, 2030: 4000 },
    EBITDA: { 2025: 500, 2026: 600, 2027: 700, 2028: 800, 2029: 900, 2030: 1000 },
    'EBITDA%': { 2025: '16.7%', 2026: '18.8%', 2027: '20.6%', 2028: '22.2%', 2029: '23.7%', 2030: '25.0%' },
    'J-1': { 2025: '38%', 2026: '33%', 2027: '36%', 2028: '37%', 2029: '36%', 2030: '34%' },
    'J-2': { 2025: '50%', 2026: '54%', 2027: '50%', 2028: '45%', 2029: '41%', 2030: '36%' },
    'J-3': { 2025: '12%', 2026: '12%', 2027: '14%', 2028: '18%', 2029: '23%', 2030: '30%' },
  },
  2: {
    FTE: { 2025: 1400, 2026: 1500, 2027: 1600, 2028: 1700, 2029: 1800, 2030: 1900 },
    'Growth%': { 2025: '4%', 2026: '5%', 2027: '6%', 2028: '6%', 2029: '6%', 2030: '6%' },
    Sales: { 2025: 2800, 2026: 3000, 2027: 3200, 2028: 3400, 2029: 3600, 2030: 3800 },
    EBITDA: { 2025: 450, 2026: 550, 2027: 650, 2028: 750, 2029: 850, 2030: 950 },
    'EBITDA%': { 2025: '16.1%', 2026: '18.3%', 2027: '20.3%', 2028: '22.1%', 2029: '23.6%', 2030: '25.0%' },
    'J-1': { 2025: '36%', 2026: '32%', 2027: '35%', 2028: '36%', 2029: '35%', 2030: '33%' },
    'J-2': { 2025: '52%', 2026: '56%', 2027: '52%', 2028: '47%', 2029: '43%', 2030: '38%' },
    'J-3': { 2025: '12%', 2026: '12%', 2027: '13%', 2028: '17%', 2029: '22%', 2030: '29%' },
  },
  3: {
    FTE: { 2025: 1300, 2026: 1350, 2027: 1400, 2028: 1450, 2029: 1500, 2030: 1550 },
    'Growth%': { 2025: '3%', 2026: '4%', 2027: '4%', 2028: '4%', 2029: '4%', 2030: '4%' },
    Sales: { 2025: 2600, 2026: 2700, 2027: 2800, 2028: 2900, 2029: 3000, 2030: 3100 },
    EBITDA: { 2025: 400, 2026: 450, 2027: 500, 2028: 550, 2029: 600, 2030: 650 },
    'EBITDA%': { 2025: '15.4%', 2026: '16.7%', 2027: '17.9%', 2028: '19.0%', 2029: '20.0%', 2030: '21.0%' },
    'J-1': { 2025: '34%', 2026: '31%', 2027: '33%', 2028: '34%', 2029: '33%', 2030: '31%' },
    'J-2': { 2025: '54%', 2026: '58%', 2027: '54%', 2028: '49%', 2029: '45%', 2030: '40%' },
    'J-3': { 2025: '12%', 2026: '11%', 2027: '13%', 2028: '17%', 2029: '22%', 2030: '29%' },
  },
};

interface ScenarioComparisonProps {
  onBack: () => void;
}

const ScenarioComparison: React.FC<ScenarioComparisonProps> = ({ onBack }) => {
  const [selected, setSelected] = useState<number[]>([1, 2]);

  const handleCheck = (id: number, checked: boolean) => {
    setSelected(prev => checked ? [...prev, id] : prev.filter(sid => sid !== id));
  };

  // Build columns: first column is KPI, then one for each selected scenario per year
  const columns = [
    { title: 'KPI', dataIndex: 'kpi', key: 'kpi', width: 120 },
    ...selected.flatMap(sid =>
      years.map(year => ({
        title: `${mockScenarios.find(s => s.id === sid)?.name || ''} ${year}`,
        dataIndex: `${sid}-${year}`,
        key: `${sid}-${year}`,
        align: 'right' as const,
        width: 120,
      }))
    ),
  ];

  // Build dataSource: one row per KPI
  const dataSource = comparisonKPIs.map(kpi => {
    const row: any = { kpi };
    selected.forEach(sid => {
      years.forEach(year => {
        row[`${sid}-${year}`] = mockComparisonData[sid][kpi][year];
      });
    });
    return row;
  });

  return (
    <Card title={<Title level={4} style={{ margin: 0 }}>Scenario Comparison</Title>} style={{ maxWidth: 1200, margin: '0 auto' }}>
      <List
        header={<b>Select scenarios to compare:</b>}
        dataSource={mockScenarios}
        renderItem={item => (
          <List.Item>
            <Checkbox
              checked={selected.includes(item.id)}
              onChange={e => handleCheck(item.id, e.target.checked)}
            >
              {item.name} <span style={{ color: '#888', marginLeft: 8 }}>({item.created})</span>
            </Checkbox>
          </List.Item>
        )}
        style={{ marginBottom: 24, maxWidth: 400 }}
      />
      <Table
        columns={columns}
        dataSource={dataSource}
        pagination={false}
        size="middle"
        rowKey={row => row.kpi}
        bordered
        style={{ marginBottom: 24 }}
        scroll={{ x: true }}
      />
      <Space>
        <Button onClick={onBack}>Back</Button>
      </Space>
    </Card>
  );
};

export default ScenarioComparison; 