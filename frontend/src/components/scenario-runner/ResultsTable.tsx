import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Typography, Space, Select, message, Spin, Empty } from 'antd';
import type { SimulationResults, ScenarioDefinition, OfficeName } from '../../types/unified-data-structures';
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

// Helper function to get available offices from simulation results
function getAvailableOffices(data: SimulationResults | null): string[] {
  if (!data || !data.years) return [];
  
  // Get offices from the first available year
  const firstYear = Object.keys(data.years)[0];
  if (!firstYear) return [];
  
  return Object.keys(data.years[firstYear].offices);
}

// Helper function to extract KPI value from simulation results
function getKPIValue(data: SimulationResults | null, office: OfficeName, kpiKey: string, year: number): number {
  if (!data || !data.years[year.toString()]) return 0;
  
  const yearData = data.years[year.toString()];
  
  // Find the actual office name in the results (case-insensitive)
  const availableOffices = Object.keys(yearData.offices);
  const actualOfficeName = availableOffices.find(name => 
    name.toLowerCase() === office.toLowerCase()
  );
  
  if (!actualOfficeName) {
    console.log(`[DEBUG][ResultsTable] Office '${office}' not found in results. Available offices:`, availableOffices);
    return 0;
  }
  
  const officeData = yearData.offices[actualOfficeName];
  if (!officeData) return 0;
  
  // Access data directly from officeData (not under kpis)
  const financial = officeData.financial || {};
  const growth = officeData.growth || {};
  const journeys = officeData.journeys || {};

  let value = 0;
  switch (kpiKey) {
    case 'FTE':
      value = officeData.total_fte || 0;
      break;
    case 'Sales':
      value = financial.net_sales || 0;
      break;
    case 'EBITDA':
      value = financial.ebitda || 0;
      break;
    case 'EBITDA%':
      value = financial.margin ? financial.margin * 100 : 0;
      break;
    case 'Growth%':
      value = growth.total_growth_percent || 0;
      break;
    case 'J-1':
      value = journeys.journey_percentages?.["Journey 1"] || 0;
      break;
    case 'J-2':
      value = journeys.journey_percentages?.["Journey 2"] || 0;
      break;
    case 'J-3':
      value = journeys.journey_percentages?.["Journey 3"] || 0;
      break;
    case 'J-4':
      value = journeys.journey_percentages?.["Journey 4"] || 0;
      break;
    default:
      value = 0;
  }
  
  // If office-level data is zero, fall back to group-level KPIs
  if (value === 0 && yearData.kpis) {
    console.log(`[DEBUG][ResultsTable] Falling back to group KPIs for ${kpiKey} in ${actualOfficeName} (${year})`);
    
    // Use yearly_kpis for year-specific data, fall back to aggregated data
    const yearlyKpis = yearData.kpis.yearly_kpis?.[year.toString()];
    const financial = yearlyKpis?.financial || yearData.kpis.financial;
    const growth = yearlyKpis?.growth || yearData.kpis.growth;
    const journeys = yearlyKpis?.journeys || yearData.kpis.journeys;
    
    switch (kpiKey) {
      case 'FTE':
        value = financial?.total_consultants || 0;
        break;
      case 'Sales':
        value = financial?.net_sales || 0;
        break;
      case 'EBITDA':
        value = financial?.ebitda || 0;
        break;
      case 'EBITDA%':
        value = financial?.margin ? financial.margin * 100 : 0;
        break;
      case 'Growth%':
        value = growth?.total_growth_percent || 0;
        break;
      case 'J-1':
        value = journeys?.journey_percentages?.["Journey 1"] || 0;
        break;
      case 'J-2':
        value = journeys?.journey_percentages?.["Journey 2"] || 0;
        break;
      case 'J-3':
        value = journeys?.journey_percentages?.["Journey 3"] || 0;
        break;
      case 'J-4':
        value = journeys?.journey_percentages?.["Journey 4"] || 0;
        break;
    }
  }
  
  if (value === 0) {
    console.log(`[DEBUG][ResultsTable] Zero value for ${kpiKey} in ${actualOfficeName} (${year}):`, {
      officeData: officeData,
      financial: financial,
      growth: growth,
      journeys: journeys
    });
  }
  
  return value;
}

// Helper function to format values based on KPI type
function formatValue(value: number, kpiKey: string): string {
  const kpi = kpis.find(k => k.key === kpiKey);
  if (!kpi) return String(value);

  // Helper for M/B formatting
  const formatLargeNumber = (num: number) => {
    if (Math.abs(num) >= 1_000_000_000) {
      return (num / 1_000_000_000).toFixed(2).replace(/\.00$/, '') + 'B';
    }
    if (Math.abs(num) >= 1_000_000) {
      return (num / 1_000_000).toFixed(2).replace(/\.00$/, '') + 'M';
    }
    return num.toLocaleString();
  };

  switch (kpi.unit) {
    case 'percentage':
      return `${value.toFixed(1)}%`;
    case 'currency':
      return `SEK ${formatLargeNumber(value)}`;
    case 'count':
      return formatLargeNumber(value);
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

// Helper function to extract Group/global KPI value from simulation results
function getGroupKPIValue(data: SimulationResults | null, kpiKey: string, year: number): number {
  if (!data || !data.years[year.toString()]) return 0;
  
  const yearData = data.years[year.toString()];
  const kpis = yearData.kpis;
  
  if (!kpis) {
    console.log(`[DEBUG][ResultsTable] No KPIs found for year ${year}`);
    return 0;
  }
  
  // Use yearly_kpis for year-specific data, fall back to aggregated data
  const yearlyKpis = kpis.yearly_kpis?.[year.toString()];
  const financial = yearlyKpis?.financial || kpis.financial;
  const growth = yearlyKpis?.growth || kpis.growth;
  const journeys = yearlyKpis?.journeys || kpis.journeys;
  
  switch (kpiKey) {
    case 'FTE':
      return financial?.total_consultants || 0;
    case 'Sales':
      return financial?.net_sales || 0;
    case 'EBITDA':
      return financial?.ebitda || 0;
    case 'EBITDA%':
      return financial?.margin ? financial.margin * 100 : 0;
    case 'Growth%':
      return growth?.total_growth_percent || 0;
    case 'J-1':
      return journeys?.journey_percentages?.["Journey 1"] || 0;
    case 'J-2':
      return journeys?.journey_percentages?.["Journey 2"] || 0;
    case 'J-3':
      return journeys?.journey_percentages?.["Journey 3"] || 0;
    case 'J-4':
      return journeys?.journey_percentages?.["Journey 4"] || 0;
    default:
      return 0;
  }
}

// Helper function to build table data from simulation results
function buildTableData(
  scenarioData: SimulationResults | null,
  office: OfficeName | 'Group'
): TableRow[] {
  if (!scenarioData || !scenarioData.years) {
    console.warn('[DEBUG][ResultsTable] scenarioData or scenarioData.years is undefined:', scenarioData);
    return [];
  }

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
      let value = 0;
      if (office === 'Group') {
        value = getGroupKPIValue(scenarioData, kpi.key, yearNum);
      } else {
        value = getKPIValue(scenarioData, office, kpi.key, yearNum);
      }
      mainRow[year] = formatValue(value, kpi.key);
    });
    rows.push(mainRow);

    // Delta row (comparing each year to the first year)
    const deltaRow: TableRow = { kpi: 'Δ', isDelta: true, kpiKey: kpi.key };
    years.forEach(year => {
      const yearNum = parseInt(year);
      let scenarioVal = 0;
      let baselineVal = 0;
      if (office === 'Group') {
        scenarioVal = getGroupKPIValue(scenarioData, kpi.key, yearNum);
        baselineVal = getGroupKPIValue(scenarioData, kpi.key, baselineYearNum);
      } else {
        scenarioVal = getKPIValue(scenarioData, office, kpi.key, yearNum);
        baselineVal = getKPIValue(scenarioData, office, kpi.key, baselineYearNum);
      }
      const isPercent = kpi.unit === 'percentage';
      deltaRow[year] = getDeltaCell(scenarioVal, baselineVal, isPercent);
    });
    rows.push(deltaRow);
  });

  return rows;
}

const ResultsTable: React.FC<ResultsTableProps> = ({ scenarioId, onNext, onBack }) => {
  console.log('[DEBUG][ResultsTable] Rendering with scenarioId:', scenarioId);
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
        
        console.log('[DEBUG][ResultsTable] Loading scenario results for ID:', scenarioId);
        
        // Get existing scenario results instead of re-running simulation
        const results = await scenarioApi.getScenarioResults(scenarioId);
        
        console.log('[DEBUG][ResultsTable] Loaded results:', results);
        
        setScenarioData(results);
        
        // Update available offices from the results
        const offices = getAvailableOffices(results);
        setAvailableOffices(offices as OfficeName[]);
        
        // Set the first available office as selected
        if (offices.length > 0 && !offices.includes(selectedOffice as any)) {
          setSelectedOffice(offices[0] as OfficeName);
        }
        
      } catch (err) {
        console.error('[DEBUG][ResultsTable] Error loading results:', err);
        setError(err instanceof Error ? err.message : 'Failed to load results');
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
    if (!scenarioData || !scenarioData.years) {
      console.warn('[DEBUG][ResultsTable] scenarioData or scenarioData.years is undefined in generateColumns:', scenarioData);
      return [];
    }
    
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
    const notFound = error.toLowerCase().includes('not found');
    return (
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <Empty description={notFound ? 'This scenario does not exist. Please save your scenario first.' : error} />
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

  if (!scenarioData.years) {
    return (
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <Empty description="Simulation results are empty. The simulation may have failed or returned no data." />
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
        rowKey={row => row.isDelta ? `group-${row.kpiKey}-${row.isDelta}` : `group-${row.kpi}-${row.isDelta}`}
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
        rowKey={row => row.isDelta ? `${selectedOffice}-${row.kpiKey}-${row.isDelta}` : `${selectedOffice}-${row.kpi}-${row.isDelta}`}
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