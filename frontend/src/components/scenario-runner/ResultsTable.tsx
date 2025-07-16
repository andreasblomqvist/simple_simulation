import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Typography, Space, Select, message, Spin, Empty } from 'antd';
import type { SimulationResults, ScenarioDefinition, OfficeName } from '../../types/unified-data-structures';
import { scenarioApi } from '../../services/scenarioApi';
import { normalizeBaselineInput } from '../../utils/normalizeBaselineInput';

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
  
  // Access data directly from officeData (not under kpis)
  const financial = officeData.financial || {};
  const growth = officeData.growth || {};
  const kpis = officeData.kpis || {};

  switch (kpiKey) {
    case 'FTE':
      return officeData.fte || officeData.total_fte || 0;
    case 'Sales':
      return (financial as any).net_sales || (kpis as any).financial?.net_sales || 0;
    case 'EBITDA':
      return (financial as any).ebitda || (kpis as any).financial?.ebitda || 0;
    case 'EBITDA%':
      const margin = (financial as any).margin || (kpis as any).financial?.margin;
      return margin ? margin * 100 : 0; // Convert to percent
    case 'Growth%':
      return (growth as any).total_growth_percent || (kpis as any).growth?.total_growth_percent || 0;
    case 'J-1':
      return (kpis as any).journeys?.journey_percentages?.["Journey 1"] || 0;
    case 'J-2':
      return (kpis as any).journeys?.journey_percentages?.["Journey 2"] || 0;
    case 'J-3':
      return (kpis as any).journeys?.journey_percentages?.["Journey 3"] || 0;
    case 'J-4':
      return (kpis as any).journeys?.journey_percentages?.["Journey 4"] || 0;
    default:
      return 0;
  }
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
  
  // Try to get KPIs from the top-level kpis object first
  const yearlyKpis = data.kpis?.yearly_kpis?.[year.toString()];
  if (yearlyKpis) {
    switch (kpiKey) {
      case 'FTE':
        return yearlyKpis.financial?.total_consultants || 0;
      case 'Sales':
        return yearlyKpis.financial?.net_sales || 0;
      case 'EBITDA':
        return yearlyKpis.financial?.ebitda || 0;
      case 'EBITDA%':
        return yearlyKpis.financial?.margin ? yearlyKpis.financial.margin * 100 : 0;
      case 'Growth%':
        return yearlyKpis.growth?.total_growth_percent || 0;
      case 'J-1':
        return yearlyKpis.journeys?.journey_percentages?.["Journey 1"] || 0;
      case 'J-2':
        return yearlyKpis.journeys?.journey_percentages?.["Journey 2"] || 0;
      case 'J-3':
        return yearlyKpis.journeys?.journey_percentages?.["Journey 3"] || 0;
      case 'J-4':
        return yearlyKpis.journeys?.journey_percentages?.["Journey 4"] || 0;
      default:
        return 0;
    }
  }
  
  // Fallback: aggregate from all offices
  const yearData = data.years[year.toString()];
  const offices = Object.values(yearData.offices);
  
  switch (kpiKey) {
    case 'FTE':
      return offices.reduce((sum, office) => sum + (office.fte || office.total_fte || 0), 0);
    case 'Sales':
      return offices.reduce((sum, office) => sum + ((office.financial?.net_sales as any) || 0), 0);
    case 'EBITDA':
      return offices.reduce((sum, office) => sum + ((office.financial?.ebitda as any) || 0), 0);
    case 'EBITDA%':
      const totalSales = offices.reduce((sum, office) => sum + ((office.financial?.net_sales as any) || 0), 0);
      const totalEbitda = offices.reduce((sum, office) => sum + ((office.financial?.ebitda as any) || 0), 0);
      return totalSales > 0 ? (totalEbitda / totalSales) * 100 : 0;
    case 'Growth%':
      // For growth, we'll use the first office's growth data as a proxy
      const firstOffice = offices[0];
      return (firstOffice?.growth as any)?.total_growth_percent || 0;
    case 'J-1':
    case 'J-2':
    case 'J-3':
    case 'J-4':
      // For journey data, we'll use the first office's journey data as a proxy
      const firstOfficeKpis = offices[0]?.kpis;
      const journeyNum = kpiKey.split('-')[1];
      return (firstOfficeKpis as any)?.journeys?.journey_percentages?.[`Journey ${journeyNum}`] || 0;
    default:
      return 0;
  }
}

// Helper function to build table data from simulation results
function buildTableData(
  scenarioData: SimulationResults | null,
  office: OfficeName | 'Group'
): TableRow[] {
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
    const deltaRow: TableRow = { kpi: 'Δ', isDelta: true };
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
        // Fetch full scenario definition
        console.log('[DEBUG][ResultsTable] Fetching scenario from API with ID:', scenarioId);
        const scenario = await scenarioApi.getScenario(scenarioId);
        // Handle both direct scenario and nested definition structure
        const actualScenario = scenario?.definition || scenario;
        // Normalize baseline_input and ensure required structure
        if (actualScenario && actualScenario.baseline_input) {
          actualScenario.baseline_input = normalizeBaselineInput(actualScenario.baseline_input);
        } else {
          // Ensure baseline_input exists with proper structure
          actualScenario.baseline_input = normalizeBaselineInput({});
        }
        
        // Ensure baseline_input has the exact structure backend expects
        if (!actualScenario.baseline_input.global) {
          actualScenario.baseline_input.global = {};
        }
        if (!actualScenario.baseline_input.global.recruitment) {
          actualScenario.baseline_input.global.recruitment = {};
        }
        if (!actualScenario.baseline_input.global.churn) {
          actualScenario.baseline_input.global.churn = {};
        }
        
        // Ensure each role has proper leveled structure matching the data structure documentation
        const roles = ['Consultant', 'Sales', 'Recruitment'];
        for (const role of roles) {
          if (!actualScenario.baseline_input.global.recruitment[role]) {
            actualScenario.baseline_input.global.recruitment[role] = {
              A: { '202501': 0.0, '202502': 0.0, '202503': 0.0, '202504': 0.0, '202505': 0.0, '202506': 0.0, '202507': 0.0, '202508': 0.0, '202509': 0.0, '202510': 0.0, '202511': 0.0, '202512': 0.0 },
              AC: { '202501': 0.0, '202502': 0.0, '202503': 0.0, '202504': 0.0, '202505': 0.0, '202506': 0.0, '202507': 0.0, '202508': 0.0, '202509': 0.0, '202510': 0.0, '202511': 0.0, '202512': 0.0 }
            };
          }
          
          if (!actualScenario.baseline_input.global.churn[role]) {
            actualScenario.baseline_input.global.churn[role] = {
              A: { '202501': 0.0, '202502': 0.0, '202503': 0.0, '202504': 0.0, '202505': 0.0, '202506': 0.0, '202507': 0.0, '202508': 0.0, '202509': 0.0, '202510': 0.0, '202511': 0.0, '202512': 0.0 },
              AC: { '202501': 0.0, '202502': 0.0, '202503': 0.0, '202504': 0.0, '202505': 0.0, '202506': 0.0, '202507': 0.0, '202508': 0.0, '202509': 0.0, '202510': 0.0, '202511': 0.0, '202512': 0.0 }
            };
          }
        }
        
        // Debug logging
        console.log('[DEBUG][ResultsTable] Final baseline_input structure:', JSON.stringify(actualScenario.baseline_input, null, 2));
        
        // Debug progression config structure
        console.log('[DEBUG][ResultsTable] Progression config structure:', JSON.stringify(actualScenario.progression_config, null, 2));
        
        // Ensure other required fields exist
        if (!actualScenario.progression_config || !actualScenario.progression_config.levels) {
          actualScenario.progression_config = {
            levels: {
              A: {
                progression_months: [1, 4, 7, 10],
                time_on_level: 6,
                start_tenure: 1,
                next_level: 'AC',
                journey: 'J-1'
              },
              AC: {
                progression_months: [1, 4, 7, 10],
                time_on_level: 9,
                start_tenure: 6,
                next_level: 'C',
                journey: 'J-1'
              },
              C: {
                progression_months: [1, 7],
                time_on_level: 18,
                start_tenure: 15,
                next_level: 'SrC',
                journey: 'J-1'
              },
              SrC: {
                progression_months: [1, 7],
                time_on_level: 18,
                start_tenure: 33,
                next_level: 'AM',
                journey: 'J-1'
              },
              AM: {
                progression_months: [1, 7],
                time_on_level: 48,
                start_tenure: 51,
                next_level: 'M',
                journey: 'J-1'
              },
              M: {
                progression_months: [1],
                time_on_level: 48,
                start_tenure: 99,
                next_level: 'SrM',
                journey: 'J-1'
              },
              SrM: {
                progression_months: [1],
                time_on_level: 120,
                start_tenure: 147,
                next_level: 'Pi',
                journey: 'J-1'
              },
              Pi: {
                progression_months: [1],
                time_on_level: 12,
                start_tenure: 267,
                next_level: 'P',
                journey: 'J-1'
              },
              P: {
                progression_months: [1],
                time_on_level: 1000,
                start_tenure: 279,
                next_level: 'X',
                journey: 'J-1'
              },
              X: {
                progression_months: [1],
                time_on_level: 1279,
                start_tenure: 1279,
                next_level: null,
                journey: 'J-1'
              }
            }
          };
        }
        if (!actualScenario.cat_curves || !actualScenario.cat_curves.curves) {
          actualScenario.cat_curves = {
            curves: {
              A: {
                curves: {
                  CAT0: 0.0,
                  CAT6: 0.919,
                  CAT12: 0.85
                }
              },
              AC: {
                curves: {
                  CAT0: 0.0,
                  CAT6: 0.919,
                  CAT12: 0.85
                }
              },
              C: {
                curves: {
                  CAT0: 0.0,
                  CAT6: 0.919,
                  CAT12: 0.85
                }
              },
              M: {
                curves: {
                  CAT0: 0.0,
                  CAT6: 0.919,
                  CAT12: 0.85
                }
              },
              SM: {
                curves: {
                  CAT0: 0.0,
                  CAT6: 0.919,
                  CAT12: 0.85
                }
              },
              P: {
                curves: {
                  CAT0: 0.0,
                  CAT6: 0.919,
                  CAT12: 0.85
                }
              }
            }
          };
        }
        if (!actualScenario.levers) {
          actualScenario.levers = {
            recruitment: { A: 1.0, AC: 1.0 },
            churn: { A: 1.0, AC: 1.0 },
            progression: { A: 1.0, AC: 1.0 }
          };
        }
        if (!actualScenario.economic_params) {
          actualScenario.economic_params = {
            working_hours_per_month: 160.0,
            employment_cost_rate: 0.3,
            unplanned_absence: 0.05,
            other_expense: 1000000.0
          };
        }
        // Run simulation by definition
        console.log('[DEBUG][ResultsTable] Running simulation for scenario:', actualScenario);
        console.log('[DEBUG][ResultsTable] Final scenario structure being sent:', JSON.stringify(actualScenario, null, 2));
        const results = await scenarioApi.runScenarioDefinition(actualScenario, actualScenario.office_scope);
        console.log('[DEBUG][ResultsTable] Scenario API results:', results);
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
        console.error('[DEBUG][ResultsTable] Error loading results for scenarioId:', scenarioId, err);
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
        rowKey={row => `${row.kpi}-${row.isDelta}`}
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
        rowKey={row => `${row.kpi}-${row.isDelta}`}
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