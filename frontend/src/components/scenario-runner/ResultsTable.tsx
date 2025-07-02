import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Typography, Space, Select, message, Spin, Empty } from 'antd';
import type { SimulationResults, ScenarioDefinition, OfficeName } from '../../types/scenarios';
import { scenarioApi } from '../../services/scenarioApi';

const { Title } = Typography;
const { Option } = Select;

// KPI definitions
const kpis = [
  { key: 'FTE', label: 'FTE', unit: 'count' },
  { key: 'Growth%', label: 'Growth%', unit: 'percentage' },
  { key: 'Sales', label: 'Sales', unit: 'currency' },
  { key: 'EBITDA', label: 'EBITDA', unit: 'currency' },
  { key: 'EBITDA%', label: 'EBITDA%', unit: 'percentage' },
  { key: 'J-1', label: 'J-1', unit: 'percentage' },
  { key: 'J-2', label: 'J-2', unit: 'percentage' },
  { key: 'J-3', label: 'J-3', unit: 'percentage' },
  { key: 'J-4', label: 'J-4', unit: 'percentage' },
];

// Types for table data
interface TableRow {
  kpi: string;
  isDelta: boolean;
  [key: string]: any;
}

interface ResultsTableProps {
  scenarioId: string;
  onNext?: () => void;
  onBack?: () => void;
}

// Helper function to extract KPI value from simulation results
function getKPIValue(data: SimulationResults | null, office: OfficeName, kpiKey: string, year: number): number {
  if (!data || !data.years[year.toString()]) return 0;
  
  const yearData = data.years[year.toString()];
  const officeData = yearData.offices[office];
  
  if (!officeData) return 0;
  
  switch (kpiKey) {
    case 'FTE':
      return officeData.total_fte;
    case 'Sales':
      return officeData.financial?.net_sales || 0;
    case 'EBITDA':
      return officeData.financial?.ebitda || 0;
    case 'EBITDA%':
      return officeData.financial?.margin || 0;
    case 'Growth%':
      return officeData.growth?.total_growth_percent || 0;
    case 'J-1':
    case 'J-2':
    case 'J-3':
    case 'J-4':
      // Journey percentages would need to be calculated from role data
      // For now, return 0 - this would need to be implemented based on actual data structure
      return 0;
    default:
      return 0;
  }
}

// Helper function to format values based on KPI type
function formatValue(value: number, kpiKey: string): string {
  const kpi = kpis.find(k => k.key === kpiKey);
  if (!kpi) return String(value);
  
  switch (kpi.unit) {
    case 'percentage':
      return `${value.toFixed(1)}%`;
    case 'currency':
      return `${value.toLocaleString('en-US', { style: 'currency', currency: 'SEK', minimumFractionDigits: 0 })}`;
    case 'count':
      return value.toLocaleString();
    default:
      return String(value);
  }
}

// Helper function to calculate delta between scenario and baseline
function getDeltaCell(scenarioVal: number, baselineVal: number | undefined, isPercent: boolean = false) {
  if (scenarioVal === undefined || baselineVal === undefined) return null;
  
  const absDelta = scenarioVal - baselineVal;
  const pctDelta = baselineVal !== 0 ? (absDelta / baselineVal) * 100 : 0;
  const color = absDelta > 0 ? '#52c41a' : absDelta < 0 ? '#ff4d4f' : '#888';
  
  const absStr = isPercent ? `${absDelta > 0 ? '+' : ''}${absDelta.toFixed(1)}%` : `${absDelta > 0 ? '+' : ''}${absDelta.toFixed(0)}`;
  const pctStr = `(${pctDelta > 0 ? '+' : ''}${pctDelta.toFixed(1)}%)`;
  
  return <span style={{ color, fontSize: 13 }}>{absStr} <span style={{ color: '#aaa', fontSize: 12 }}>{pctStr}</span></span>;
}

// Helper function to build table data from simulation results
function buildTableData(scenarioData: SimulationResults | null, office: OfficeName): TableRow[] {
  if (!scenarioData) return [];
  
  const rows: TableRow[] = [];
  const years = Object.keys(scenarioData.years).sort();
  
  // Use the first year as baseline
  const baselineYear = years[0];
  const baselineYearNum = parseInt(baselineYear);
  
  kpis.forEach(kpi => {
    // Main scenario row
    const mainRow: TableRow = { kpi: kpi.label, isDelta: false };
    years.forEach(year => {
      const yearNum = parseInt(year);
      const value = getKPIValue(scenarioData, office, kpi.key, yearNum);
      mainRow[year] = formatValue(value, kpi.key);
    });
    rows.push(mainRow);
    
    // Delta row (comparing each year to the first year)
    const deltaRow: TableRow = { kpi: 'Δ', isDelta: true };
    years.forEach(year => {
      const yearNum = parseInt(year);
      const scenarioVal = getKPIValue(scenarioData, office, kpi.key, yearNum);
      const baselineVal = getKPIValue(scenarioData, office, kpi.key, baselineYearNum);
      const isPercent = kpi.unit === 'percentage';
      deltaRow[year] = getDeltaCell(scenarioVal, baselineVal, isPercent);
    });
    rows.push(deltaRow);
  });
  
  return rows;
}

const ResultsTable: React.FC<ResultsTableProps> = ({ scenarioId, onNext, onBack }) => {
  const [scenarioData, setScenarioData] = useState<SimulationResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedOffice, setSelectedOffice] = useState<OfficeName>('Stockholm');
  const [availableOffices, setAvailableOffices] = useState<OfficeName[]>([]);

  // Load scenario results
  useEffect(() => {
    const loadResults = async () => {
      try {
        setLoading(true);
        setError(null);
        // Load scenario results
        const results = await scenarioApi.runScenarioById(scenarioId);
        setScenarioData(results.results);
        // Extract available offices from the data
        if (results.results && Object.keys(results.results.years).length > 0) {
          const firstYear = Object.keys(results.results.years)[0];
          const offices = Object.keys(results.results.years[firstYear].offices);
          setAvailableOffices(offices);
          if (offices.length > 0 && !offices.includes(selectedOffice)) {
            setSelectedOffice(offices[0]);
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load scenario results');
        message.error('Failed to load scenario results');
      } finally {
        setLoading(false);
      }
    };
    if (scenarioId) {
      loadResults();
    }
  }, [scenarioId]);

  // Generate table columns dynamically based on available years
  const generateColumns = () => {
    if (!scenarioData) return [];
    
    const years = Object.keys(scenarioData.years).sort();
    
    return [
      {
        title: 'KPI',
        dataIndex: 'kpi',
        key: 'kpi',
        width: 120,
        className: 'kpi-col',
      },
      ...years.map(year => ({
        title: year,
        dataIndex: year,
        key: year,
        width: 100,
        align: 'right' as const,
        className: 'scenario-year-col',
      })),
    ];
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>Loading scenario results...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <Empty description={error} />
        {onBack && <Button onClick={onBack} style={{ marginTop: 16 }}>Back</Button>}
      </div>
    );
  }

  if (!scenarioData) {
    return (
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <Empty description="No scenario data available" />
        {onBack && <Button onClick={onBack} style={{ marginTop: 16 }}>Back</Button>}
      </div>
    );
  }

  const columns = generateColumns();
  const groupData = buildTableData(scenarioData, 'Group');
  const officeData = buildTableData(scenarioData, selectedOffice);

  return (
    <div>
      {/* Group Table Title */}
      <div style={{ fontWeight: 600, fontSize: 18, margin: '16px 0 8px 0' }}>🏢 Group <span style={{ fontWeight: 400, fontSize: 16 }}>📊 Key Metrics</span></div>
      <Table
        columns={columns}
        dataSource={groupData}
        pagination={false}
        size="middle"
        rowKey={(row, idx) => `${row.kpi}-${idx}`}
        bordered
        style={{ marginBottom: 32 }}
        scroll={{ x: true }}
        rowClassName={row => row.isDelta ? 'delta-row' : ''}
      />
      {/* Office Selector */}
      {availableOffices.length > 1 && (
        <div style={{ marginBottom: 16 }}>
          <Space>
            <span style={{ fontWeight: 500 }}>Select Office:</span>
            <Select
              value={selectedOffice}
              onChange={setSelectedOffice}
              style={{ minWidth: 180 }}
            >
              {availableOffices.filter(office => office !== 'Group').map(office => (
                <Option key={office} value={office}>{office}</Option>
              ))}
            </Select>
          </Space>
        </div>
      )}
      {/* Office Table Title */}
      <div style={{ fontWeight: 600, fontSize: 18, margin: '16px 0 8px 0' }}>{selectedOffice} <span style={{ fontWeight: 400, fontSize: 16 }}>📊 Key Metrics</span></div>
      <Table
        columns={columns}
        dataSource={officeData}
        pagination={false}
        size="middle"
        rowKey={(row, idx) => `${row.kpi}-${idx}`}
        bordered
        style={{ marginBottom: 24 }}
        scroll={{ x: true }}
        rowClassName={row => row.isDelta ? 'delta-row' : ''}
      />
      {(onBack || onNext) && (
        <Space>
          {onBack && <Button onClick={onBack}>Back</Button>}
          {onNext && <Button type="primary" onClick={onNext}>Next: Compare Scenarios</Button>}
        </Space>
      )}
    </div>
  );
};

export default ResultsTable; 