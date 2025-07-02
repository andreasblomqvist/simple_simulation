import React, { useState } from 'react';
import { Card, Table, Button, Typography, Space, Select } from 'antd';

const { Title } = Typography;
const { Option } = Select;

const years = [2025, 2026, 2027, 2028, 2029, 2030];
const offices = [
  { key: 'Group', label: '🏢 Group' },
  { key: 'Stockholm', label: '🏙️ Stockholm' },
  { key: 'Munich', label: '🏰 Munich' },
];
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

// Mock baseline data: same structure as mockResults
const baselineResults = [
  { office: 'Group', kpi: 'FTE', 2025: 1600, 2026: 1650, 2027: 1700, 2028: 1750, 2029: 1800, 2030: 1850 },
  { office: 'Group', kpi: 'Growth%', 2025: '4.5%', 2026: '5.5%', 2027: '6%', 2028: '5%', 2029: '5%', 2030: '5%' },
  { office: 'Group', kpi: 'Sales', 2025: 2900, 2026: 3100, 2027: 3300, 2028: 3500, 2029: 3700, 2030: 3900 },
  { office: 'Group', kpi: 'EBITDA', 2025: 480, 2026: 580, 2027: 680, 2028: 780, 2029: 880, 2030: 980 },
  { office: 'Group', kpi: 'EBITDA%', 2025: '16.0%', 2026: '18.0%', 2027: '20.0%', 2028: '21.5%', 2029: '23.0%', 2030: '24.0%' },
  { office: 'Group', kpi: 'J-1', 2025: '37%', 2026: '32%', 2027: '35%', 2028: '36%', 2029: '35%', 2030: '33%' },
  { office: 'Group', kpi: 'J-2', 2025: '51%', 2026: '53%', 2027: '51%', 2028: '46%', 2029: '42%', 2030: '37%' },
  { office: 'Group', kpi: 'J-3', 2025: '12%', 2026: '13%', 2027: '14%', 2028: '18%', 2029: '23%', 2030: '30%' },
  { office: 'Stockholm', kpi: 'FTE', 2025: 830, 2026: 860, 2027: 910, 2028: 960, 2029: 1010, 2030: 1060 },
  { office: 'Stockholm', kpi: 'Growth%', 2025: '4.2%', 2026: '3.7%', 2027: '6.0%', 2028: '5.7%', 2029: '5.4%', 2030: '5.1%' },
  { office: 'Stockholm', kpi: 'Sales', 2025: 1180, 2026: 1280, 2027: 1380, 2028: 1480, 2029: 1580, 2030: 1680 },
  { office: 'Stockholm', kpi: 'EBITDA', 2025: 210, 2026: 230, 2027: 260, 2028: 290, 2029: 320, 2030: 350 },
  { office: 'Stockholm', kpi: 'EBITDA%', 2025: '16.2%', 2026: '16.5%', 2027: '17.5%', 2028: '18.3%', 2029: '19.0%', 2030: '19.7%' },
  { office: 'Stockholm', kpi: 'J-1', 2025: '41%', 2026: '39%', 2027: '38%', 2028: '37%', 2029: '36%', 2030: '35%' },
  { office: 'Stockholm', kpi: 'J-2', 2025: '47%', 2026: '49%', 2027: '50%', 2028: '51%', 2029: '52%', 2030: '53%' },
  { office: 'Stockholm', kpi: 'J-3', 2025: '12%', 2026: '12%', 2027: '12%', 2028: '12%', 2029: '12%', 2030: '12%' },
  { office: 'Munich', kpi: 'FTE', 2025: 310, 2026: 330, 2027: 360, 2028: 390, 2029: 420, 2030: 450 },
  { office: 'Munich', kpi: 'Growth%', 2025: '5.2%', 2026: '6.9%', 2027: '9.6%', 2028: '8.8%', 2029: '8.1%', 2030: '7.5%' },
  { office: 'Munich', kpi: 'Sales', 2025: 590, 2026: 640, 2027: 690, 2028: 740, 2029: 790, 2030: 840 },
  { office: 'Munich', kpi: 'EBITDA', 2025: 85, 2026: 95, 2027: 115, 2028: 135, 2029: 155, 2030: 175 },
  { office: 'Munich', kpi: 'EBITDA%', 2025: '13.0%', 2026: '13.5%', 2027: '15.5%', 2028: '17.0%', 2029: '18.5%', 2030: '19.7%' },
  { office: 'Munich', kpi: 'J-1', 2025: '36%', 2026: '35%', 2027: '34%', 2028: '33%', 2029: '32%', 2030: '31%' },
  { office: 'Munich', kpi: 'J-2', 2025: '49%', 2026: '51%', 2027: '53%', 2028: '55%', 2029: '57%', 2030: '59%' },
  { office: 'Munich', kpi: 'J-3', 2025: '15%', 2026: '14%', 2027: '13%', 2028: '12%', 2029: '11%', 2030: '10%' },
];

function getBaselineRow(office, kpi) {
  return baselineResults.find(row => row.office === office && row.kpi === kpi);
}

function getDeltaCell(scenarioVal, baselineVal, isPercent = false) {
  if (scenarioVal === undefined || baselineVal === undefined) return null;
  // Parse percent strings if needed
  let s = scenarioVal, b = baselineVal;
  if (isPercent) {
    s = parseFloat(String(s).replace('%',''));
    b = parseFloat(String(b).replace('%',''));
  }
  const absDelta = s - b;
  const pctDelta = b !== 0 ? (absDelta / b) * 100 : 0;
  const color = absDelta > 0 ? '#52c41a' : absDelta < 0 ? '#ff4d4f' : '#888';
  const absStr = isPercent ? `${absDelta > 0 ? '+' : ''}${absDelta.toFixed(1)}%` : `${absDelta > 0 ? '+' : ''}${absDelta}`;
  const pctStr = `(${pctDelta > 0 ? '+' : ''}${pctDelta.toFixed(1)}%)`;
  return <span style={{ color, fontSize: 13 }}>{absStr} <span style={{ color: '#aaa', fontSize: 12 }}>{pctStr}</span></span>;
}

function buildTableData(results, office) {
  const rows = [];
  kpis.forEach(kpi => {
    const scenarioRow = results.find(row => row.kpi === kpi && row.office === office);
    const baselineRow = getBaselineRow(office, kpi);
    if (!scenarioRow) return;
    // Main scenario row
    rows.push({ ...scenarioRow, isDelta: false });
    // Delta row
    const deltaRow = { kpi: 'Δ', isDelta: true };
    years.forEach(year => {
      const scenarioVal = scenarioRow[year];
      const baselineVal = baselineRow ? baselineRow[year] : undefined;
      const isPercent = typeof scenarioVal === 'string' && String(scenarioVal).includes('%');
      deltaRow[year] = getDeltaCell(scenarioVal, baselineVal, isPercent);
    });
    rows.push(deltaRow);
  });
  return rows;
}

const columns = [
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
  // Always show Group results
  const groupResults = mockResults.filter(row => row.office === 'Group');
  // Office selector and results (excluding Group)
  const [selectedOffice, setSelectedOffice] = useState(offices[1].key); // Default to Stockholm
  const officeResults = mockResults.filter(row => row.office === selectedOffice);

  return (
    <div style={{ marginLeft: 24, marginRight: 24 }}>
      <Card title={<Title level={4} style={{ margin: 0 }}>Scenario Results</Title>}>
        <Title level={5} style={{ marginBottom: 12 }}>🏢 Group <span style={{ fontWeight: 400, fontSize: 16 }}>📊 Key Metrics</span></Title>
        <Table
          columns={columns}
          dataSource={buildTableData(groupResults, 'Group')}
          pagination={false}
          size="middle"
          rowKey={(row, idx) => `${row.kpi}-${idx}`}
          bordered
          style={{ marginBottom: 32 }}
          scroll={{ x: true }}
          rowClassName={row => row.isDelta ? 'delta-row' : ''}
        />
        <div style={{ marginBottom: 16 }}>
          <Space>
            <span style={{ fontWeight: 500 }}>Select Office:</span>
            <Select
              value={selectedOffice}
              onChange={setSelectedOffice}
              style={{ minWidth: 180 }}
            >
              {offices.filter(o => o.key !== 'Group').map(office => (
                <Option key={office.key} value={office.key}>{office.label}</Option>
              ))}
            </Select>
          </Space>
        </div>
        <Title level={5} style={{ marginBottom: 12 }}>{offices.find(o => o.key === selectedOffice)?.label} <span style={{ fontWeight: 400, fontSize: 16 }}>📊 Key Metrics</span></Title>
        <Table
          columns={columns}
          dataSource={buildTableData(officeResults, selectedOffice)}
          pagination={false}
          size="middle"
          rowKey={(row, idx) => `${row.kpi}-${idx}`}
          bordered
          style={{ marginBottom: 24 }}
          scroll={{ x: true }}
          rowClassName={row => row.isDelta ? 'delta-row' : ''}
        />
        <Space>
          <Button onClick={onBack}>Back</Button>
          <Button type="primary" onClick={onNext}>Next: Compare Scenarios</Button>
        </Space>
      </Card>
    </div>
  );
};

export default ResultsTable; 