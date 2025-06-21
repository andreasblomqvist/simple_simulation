import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Select, InputNumber, Checkbox, Button, Space, Collapse, Table, Tabs, Typography, message, Spin, Alert, Input } from 'antd';
import { SettingOutlined, RocketOutlined, TableOutlined, LoadingOutlined, ControlOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { simulationApi } from '../services/simulationApi';
import { useTheme } from '../components/ThemeContext';
import type { OfficeConfig, SimulationResults } from '../services/simulationApi';
import { EnhancedKPICard } from '../components/v2/EnhancedKPICard';
import WorkforcePyramidChart from '../components/v2/WorkforcePyramidChart';
import WorkforceStackedBarChart from '../components/v2/WorkforceStackedBarChart';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

// Add constants for lever manipulation
const LEVERS = [
  { key: 'recruitment', label: 'Recruitment' },
  { key: 'churn', label: 'Churn' },
  { key: 'progression', label: 'Progression' },
  { key: 'utr', label: 'UTR' },
];

const LEVELS = ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"];

const MONTHS = [
  { value: 1, label: 'January' },
  { value: 2, label: 'February' },
  { value: 3, label: 'March' },
  { value: 4, label: 'April' },
  { value: 5, label: 'May' },
  { value: 6, label: 'June' },
  { value: 7, label: 'July' },
  { value: 8, label: 'August' },
  { value: 9, label: 'September' },
  { value: 10, label: 'October' },
  { value: 11, label: 'November' },
  { value: 12, label: 'December' }
];

const TIME_PERIODS = [
  { value: 'monthly', label: 'Monthly' },
  { value: 'half-year', label: 'Half Year' },
  { value: 'yearly', label: 'Yearly' }
];

const OFFICE_JOURNEYS = [
  { value: 'New Office', label: 'New Office (0-24 FTE)' },
  { value: 'Emerging Office', label: 'Emerging Office (25-199 FTE)' },
  { value: 'Established Office', label: 'Established Office (200-499 FTE)' },
  { value: 'Mature Office', label: 'Mature Office (500+ FTE)' }
];

// Helper function to compute monthly rate from cumulative probability
function getMonthlyRateFromCumulative(cumulative: number, months: number) {
  if (cumulative >= 1) cumulative = 0.9999;
  if (cumulative <= 0) return 0;
  return 1 - Math.pow(1 - cumulative, 1 / months);
}

/**
 * Parse baseline comparison string and return formatted diff display
 * Input: comparisonString: "621 (baseline: 750, -129)", baselinePercent: 38
 * Output: { text: "Diff vs baseline (750, 38%): -129", isPositive: false, isNegative: true }
 */
function parseBaselineComparison(comparisonString: string, baselinePercent?: number) {
  if (!comparisonString || !comparisonString.includes('baseline:')) {
    return null;
  }
  
  // Extract baseline and difference from "621 (baseline: 750, -129)"
  const baselineMatch = comparisonString.match(/baseline:\s*(\d+)/);
  const diffMatch = comparisonString.match(/,\s*([-+]?\d+)\)/);
  
  if (baselineMatch && diffMatch) {
    const baseline = baselineMatch[1];
    const diff = diffMatch[1];
    const isPositive = diff.startsWith('+') || (!diff.startsWith('-') && parseInt(diff) > 0);
    const isNegative = diff.startsWith('-');
    
    // Include baseline percentage if available
    const baselineDisplay = baselinePercent !== undefined ? `${baseline}, ${baselinePercent}%` : baseline;
    
    return {
      text: `Diff vs baseline (${baselineDisplay}): ${diff}`,
      isPositive,
      isNegative,
      diffValue: diff,
      baseline: baselineDisplay
    };
  }
  
  return null;
}

const SimulationLabV2: React.FC = () => {
  const { darkMode } = useTheme();
  
  // Form state
  const [selectedLever, setSelectedLever] = useState<string | undefined>();
  const [selectedLevel, setSelectedLevel] = useState<string | undefined>();
  const [leverValue, setLeverValue] = useState<number | null>(null);
  const [applyToAllMonths, setApplyToAllMonths] = useState(false);
  const [applyToAllOffices, setApplyToAllOffices] = useState(true);
  const [selectedOffices, setSelectedOffices] = useState<string[]>([]);
  const [activeYear, setActiveYear] = useState('2025');
  
  // Economic parameters
  const [priceIncrease, setPriceIncrease] = useState(3.0);
  const [salaryIncrease, setSalaryIncrease] = useState(3.0);
  const [workingHours, setWorkingHours] = useState(166.4);
  const [unplannedAbsence, setUnplannedAbsence] = useState(15.7);
  const [otherExpense, setOtherExpense] = useState(19000000);
  
  // Simulation duration
  const [simulationDuration, setSimulationDuration] = useState(3); // Default 3 years
  const [selectedDurationUnit, setSelectedDurationUnit] = useState('years');
  
  // API data
  const [officeConfig, setOfficeConfig] = useState<OfficeConfig[]>([]);
  const [simulationResults, setSimulationResults] = useState<SimulationResults | null>(null);
  const [availableYears, setAvailableYears] = useState<string[]>([]);
  
  // Loading states
  const [loading, setLoading] = useState(false);
  const [configLoading, setConfigLoading] = useState(true);
  const [simulationRunning, setSimulationRunning] = useState(false);
  
  // Error states
  const [error, setError] = useState<string | null>(null);

  // Add lever manipulation state
  const [selectedLevers, setSelectedLevers] = useState(['recruitment']);
  const [selectedLevels, setSelectedLevels] = useState(['AM']);
  const [selectedMonth, setSelectedMonth] = useState(1);
  const [selectedTimePeriod, setSelectedTimePeriod] = useState('monthly');
  
  // Logs filtering state
  const [selectedOfficeFilter, setSelectedOfficeFilter] = useState<string | null>(null);
  const [selectedOfficeJourney, setSelectedOfficeJourney] = useState('');

  // Add state for applied levers
  const [appliedLevers, setAppliedLevers] = useState<any[]>([]);
  const [leverApplying, setLeverApplying] = useState(false);

  // Add state to track last simulation configuration
  const [lastSimulationConfig, setLastSimulationConfig] = useState<any>(null);

  // Load office configuration on mount
  useEffect(() => {
    const loadOfficeConfig = async () => {
      try {
        setConfigLoading(true);
        console.log('[SIMULATION] 🔄 Loading office configuration...');
        const config = await simulationApi.getOfficeConfig();
        setOfficeConfig(config);
        console.log(`[SIMULATION] ✅ Loaded ${config.length} office configurations`);
        setError(null);
      } catch (err) {
        console.error('[SIMULATION] ❌ Failed to load office config:', err);
        setError('Failed to load office configuration');
      } finally {
        setConfigLoading(false);
      }
    };

    loadOfficeConfig();
  }, []);

  // Preserve applied levers in sessionStorage to survive navigation
  useEffect(() => {
    const savedLevers = sessionStorage.getItem('simulation-applied-levers');
    if (savedLevers) {
      try {
        const parsedLevers = JSON.parse(savedLevers);
        setAppliedLevers(parsedLevers);
        console.log(`[SIMULATION] 🔄 Restored ${parsedLevers.length} applied levers from session`);
      } catch (err) {
        console.warn('[SIMULATION] ⚠️  Failed to restore saved levers:', err);
      }
    }
  }, []);

  // Save applied levers to sessionStorage whenever they change
  useEffect(() => {
    if (appliedLevers.length > 0) {
      sessionStorage.setItem('simulation-applied-levers', JSON.stringify(appliedLevers));
      console.log(`[SIMULATION] 💾 Saved ${appliedLevers.length} applied levers to session`);
    } else {
      sessionStorage.removeItem('simulation-applied-levers');
    }
  }, [appliedLevers]);

  const handleClearAllLevers = () => {
    setAppliedLevers([]);
    console.log('[SIMULATION] 🗑️ All applied levers have been cleared.');
  };

  const handleRunSimulation = async (isRetry?: boolean | React.MouseEvent<HTMLElement>) => {
    // Check if the call is a retry, not just a mouse event
    const isRetryRun = typeof isRetry === 'boolean' && isRetry;

    try {
      setSimulationRunning(true);
      setError(null);
  
      // --- Build the correct simulation request payload ---
      const current_date = new Date();
      const start_year = current_date.getFullYear();
      const start_month = current_date.getMonth() + 1;

      let end_year = start_year;
      let end_month = start_month;

      if (selectedDurationUnit === 'years') {
        end_year += simulationDuration;
      } else { // months
        end_month += simulationDuration;
        end_year += Math.floor((end_month - 1) / 12);
        end_month = ((end_month - 1) % 12) + 1;
      }

      const simulationConfig = {
        start_year,
        start_month,
        end_year,
        end_month,
        price_increase: priceIncrease / 100, // Convert percentage to float
        salary_increase: salaryIncrease / 100, // Convert percentage to float
        hy_working_hours: workingHours,
        unplanned_absence: unplannedAbsence / 100, // Convert percentage to float
        other_expense: otherExpense,
        office_overrides: appliedLevers.reduce((acc, lever) => {
          if (!acc[lever.office]) {
            acc[lever.office] = {};
          }
          const key = `${lever.lever}_${lever.level}`;
          acc[lever.office][key] = Number(lever.value) / 100; // Convert percentage to float
          return acc;
        }, {})
      };
  
      console.log('[SIMULATION] 🚀 Running simulation with config:', simulationConfig);
      
      // Save the configuration for potential retries
      setLastSimulationConfig(simulationConfig);
  
      const results = await simulationApi.runSimulation(simulationConfig);
      
      // --- RAW RESULTS DEBUG ---
      console.log('%c[DEBUG] Raw Simulation Results from Backend:', 'color: #FF6347; font-weight: bold;', results);
      // --- END RAW RESULTS DEBUG ---

      setSimulationResults(results);
      console.log('[SIMULATION] ✅ Simulation run successful.');
  
    } catch (err) {
      console.error('[SIMULATION] ❌ Simulation run failed:', err);
      setError('Simulation run failed. Check console for details.');
    } finally {
      setSimulationRunning(false);
    }
  };

  const handleApplyLevers = async () => {
    // Re-use the main simulation running logic
    await handleRunSimulation();
  };

  // Load available years when simulation results exist
  useEffect(() => {
    if (simulationResults && simulationResults.years) {
      // Extract years directly from simulation results
      const years = Object.keys(simulationResults.years).sort();
      setAvailableYears(years);
      
      // Set active year to first year if current activeYear is not in the results
      if (years.length > 0 && !years.includes(activeYear)) {
        setActiveYear(years[0]);
        console.log(`[YEAR SWITCH] Setting active year to ${years[0]} from available years:`, years);
      }
    }
  }, [simulationResults, activeYear]);

  // Computed data from API
  const leverOptions = officeConfig.length > 0 ? simulationApi.extractLeverOptions(officeConfig) : [];
  const levelOptions = selectedLever && officeConfig.length > 0 
    ? simulationApi.extractLevelOptions(officeConfig, selectedLever) 
    : [];
  const officeOptions = officeConfig.length > 0 ? simulationApi.extractOfficeOptions(officeConfig) : [];
  
  // Enhanced kpiData that includes both financial and growth KPIs
  const enhancedKpiData = (() => {
    if (!simulationResults || !activeYear) return { kpis: [], seniorityKPIs: null };
    
    // Get base financial KPIs
    const financialKPIs = simulationApi.extractKPIData(simulationResults, activeYear);
    
    // Get seniority KPIs to extract growth data
    // Use the first available year as baseline for proper comparison
    const baselineYear = availableYears.length > 0 ? availableYears[0] : activeYear;
    const seniorityKPIs = simulationApi.extractSeniorityKPIs(simulationResults, activeYear, officeConfig, baselineYear);
    
    // Add growth KPIs from seniorityKPIs
    const growthKPIs = [];
    if (seniorityKPIs) {
      // Total Growth Rate KPI
      if (seniorityKPIs.totalGrowthDetails) {
        growthKPIs.push({
          title: 'Total Growth',
          currentValue: seniorityKPIs.totalGrowthDetails.percentage,
          previousValue: '0.0%', // Baseline is always 0% growth
          unit: '',
          description: 'Total workforce growth compared to baseline',
          change: seniorityKPIs.totalGrowthDetails.absolute,
          changePercent: parseFloat(seniorityKPIs.totalGrowthDetails.percentage.replace(/[+%]/g, '')),
          rawValue: seniorityKPIs.totalGrowthDetails.current
        });
      }
      
      // Non-Debit Ratio KPI
      if (seniorityKPIs.nonDebitDetails) {
        growthKPIs.push({
          title: 'Non-Debit Ratio',
          currentValue: seniorityKPIs.nonDebitDetails.percentage,
          previousValue: `${seniorityKPIs.nonDebitDetails.baseline}%`,
          unit: '',
          description: 'Percentage of non-consultant roles (Sales, Recruitment, Operations)',
          change: seniorityKPIs.nonDebitDetails.absolute,
          changePercent: seniorityKPIs.nonDebitDetails.absolute,
          rawValue: seniorityKPIs.nonDebitDetails.current
        });
      }
      
      // Journey Distribution KPIs
      ['journey1', 'journey2', 'journey3', 'journey4'].forEach((journey, index) => {
        const journeyDetails = seniorityKPIs[`${journey}Details`];
        if (journeyDetails) {
          const journeyDefinitions = ['A, AC, C', 'SrC, AM', 'M, SrM', 'PiP'];
          growthKPIs.push({
            title: `Journey ${index + 1} (${journeyDefinitions[index]})`,
            currentValue: journeyDetails.percentage,
            previousValue: `${journeyDetails.baseline} FTE`,
            unit: '',
            description: `Workforce distribution in Journey ${index + 1}: ${journeyDefinitions[index]}`,
            change: journeyDetails.absolute,
            changePercent: journeyDetails.baseline > 0 ? (journeyDetails.absolute / journeyDetails.baseline) * 100 : 0,
            rawValue: journeyDetails.current
          });
        }
      });
    }
    
    // Store seniorityKPIs for use in other parts of the component
    return {
      kpis: [...financialKPIs, ...growthKPIs],
      seniorityKPIs
    };
  })();

  // --- START ENHANCED DEBUG LOGGING ---
  useEffect(() => {
    if (simulationResults && activeYear) {
      console.log(`%c[DEBUG] Year Changed: ${activeYear}`, 'color: #7B68EE; font-weight: bold;');
      
      const yearData = simulationResults.years?.[activeYear];
      console.log('[DEBUG] Data for active year:', yearData);
      
      const extractedKPIs = enhancedKpiData.seniorityKPIs;
      console.log('[DEBUG] Extracted Seniority KPIs for the year:', extractedKPIs);

      if (extractedKPIs) {
        console.log('[DEBUG] Baseline year used for comparison:', extractedKPIs.baselineYear);
        console.log({
          journey1: extractedKPIs.journey1Details,
          journey2: extractedKPIs.journey2Details,
          journey3: extractedKPIs.journey3Details,
          journey4: extractedKPIs.journey4Details,
        });
      }
    }
  }, [activeYear, simulationResults, enhancedKpiData]);
  // --- END ENHANCED DEBUG LOGGING ---

  // Extract kpiData and seniorityKPIs from the enhanced calculation
  const kpiData = enhancedKpiData.kpis;
  const seniorityKPIs = enhancedKpiData.seniorityKPIs;
  
  // Debug log for year switching
  console.log('[YEAR DEBUG] Current activeYear:', activeYear);
  console.log('[YEAR DEBUG] Available years:', availableYears);
  console.log('[YEAR DEBUG] Simulation results years:', simulationResults ? Object.keys(simulationResults.years || {}) : 'No results');
  console.log('[KPI DEBUG] Enhanced kpiData length:', kpiData.length);
  
  const tableData = simulationResults && activeYear
    ? simulationApi.extractTableData(simulationResults, activeYear, officeConfig)
    : [];
  
  // Year change handler with debug logging
  const handleYearChange = (year: string) => {
    console.log(`[YEAR CHANGE] Switching from ${activeYear} to ${year}`);
    setActiveYear(year);
    console.log(`[YEAR CHANGE] Active year updated to: ${year}`);
  };

  // Debug log for table data
  if (tableData && tableData.length > 0) {
    console.log('[DEBUG] Table data sample:', tableData[0]);
    console.log('[DEBUG] Table data length:', tableData.length);
  } else {
    console.log('[DEBUG] Table data is empty or null');
  }
  
  const seniorityData = simulationResults && activeYear
    ? simulationApi.extractSeniorityData(simulationResults, activeYear, officeConfig)
    : [];

  const tableColumns = [
    {
      title: 'Office/Segment/Profile',
      dataIndex: 'office',
      key: 'office',
    },
    {
      title: 'Office Journey',
      dataIndex: 'office_journey',
      key: 'office_journey',
    },
    {
      title: 'FTE',
      dataIndex: 'fte',
      key: 'fte',
    },
    {
      title: 'Delta',
      dataIndex: 'delta',
      key: 'delta',
    },
    {
      title: 'Price',
      dataIndex: 'price',
      key: 'price',
    },
    {
      title: 'Salary',
      dataIndex: 'salary',
      key: 'salary',
    },
    {
      title: 'YTD Change',
      dataIndex: 'ytdChange',
      key: 'ytdChange',
    }
  ];

  // Prepare data for WorkforcePyramidChart from simulation results
  const journeyMap: Record<string, string> = {
    A: 'Journey 1',
    AC: 'Journey 1',
    C: 'Journey 1',
    SrC: 'Journey 2',
    AM: 'Journey 2',
    M: 'Journey 3',
    SrM: 'Journey 3',
    PiP: 'Journey 4',
  };

  let pyramidData = LEVELS.map(level => ({
    level,
    fte: 0,
    journey: journeyMap[level],
  }));

  if (simulationResults && activeYear) {
    // Use the first office (or aggregate all offices if needed)
    const seniorityRows = simulationApi.extractSeniorityData(simulationResults, activeYear, officeConfig);
    console.log('seniorityRows sample', seniorityRows[0]);
    if (seniorityRows.length > 0) {
      // Aggregate FTE by level across all offices
      const fteByLevel: Record<string, number> = {};
      LEVELS.forEach(level => { fteByLevel[level] = 0; });
      seniorityRows.forEach(row => {
        LEVELS.forEach(level => {
          const key = `level${level}`;
          let value = row[key];
          if (typeof value === 'string' && value.includes('(')) {
            value = value.split(' ')[0];
          }
          fteByLevel[level] += Number(value) || 0;
        });
      });
      pyramidData = LEVELS.map(level => ({
        level,
        fte: fteByLevel[level],
        journey: journeyMap[level],
      }));
    }
  }

  // Prepare data for WorkforceStackedBarChart from simulation results (movement data)
  const MOVEMENT_TYPES = ['Churned', 'Recruited', 'Progressed In'];
  let stackedBarData: { level: string; type: string; value: number }[] = [];
  if (simulationResults && activeYear) {
    // Get the year data
    const yearData = simulationResults.years[activeYear];
    if (yearData?.offices) {
      // Aggregate movement data across all offices for each level
      const movementByLevel: Record<string, Record<string, number>> = {};
      LEVELS.forEach(level => {
        movementByLevel[level] = {};
        MOVEMENT_TYPES.forEach(type => { movementByLevel[level][type] = 0; });
      });
      
      // Sum movement data across all offices
      Object.values(yearData.offices).forEach((officeData: any) => {
        if (officeData.levels) {
          // Check all roles for movement data
          ['Consultant', 'Sales', 'Recruitment'].forEach(role => {
            const roleData = officeData.levels[role];
            if (roleData) {
              LEVELS.forEach(level => {
                const levelData = roleData[level];
                                  if (levelData && levelData.length > 0) {
                    // Get the latest period data (sum across all periods for the year)
                    const totalMovement = levelData.reduce((sum: any, periodData: any) => {
                      sum.churned += periodData.churned || 0;
                      sum.recruited += periodData.recruited || 0;
                      sum.progressed_in += periodData.progressed_in || 0;
                      return sum;
                    }, { churned: 0, recruited: 0, progressed_in: 0 });
                    
                    movementByLevel[level]['Churned'] += totalMovement.churned;
                    movementByLevel[level]['Recruited'] += totalMovement.recruited;
                    movementByLevel[level]['Progressed In'] += totalMovement.progressed_in;
                  }
              });
            }
          });
        }
      });
      
      // Convert to chart data format
      stackedBarData = LEVELS.flatMap(level =>
        MOVEMENT_TYPES.map(type => ({ 
          level, 
          type, 
          value: movementByLevel[level][type] 
        }))
      ).filter(item => item.value > 0); // Only show levels with movement
    }
  }

  // Debug logs
  console.log('SimulationLabV2 rendered');
  console.log('stackedBarData', stackedBarData);

  return (
    <div style={{ padding: '24px' }}>
      {/* Back Navigation */}
      <div style={{ marginBottom: '16px' }}>
        <Link to="/">
          <Button type="link" style={{ padding: 0, fontSize: '14px' }}>
            ← Back to Dashboard
          </Button>
        </Link>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert
          message="Error"
          description={error}
          type="error"
          showIcon
          closable
          onClose={() => setError(null)}
          style={{ marginBottom: '16px' }}
        />
      )}

      {/* Simulation Levers Card */}
      <Card 
        title="Simulation Levers" 
        style={{ marginBottom: '16px' }}
      >
        <Row gutter={16} align="middle" style={{ marginBottom: 16 }}>
          <Col span={6}>
            <Text strong>Lever Type</Text>
            <Select
              style={{ width: '100%', marginTop: '4px' }}
              placeholder="Select lever"
              value={selectedLevers[0]}
              onChange={(value) => setSelectedLevers([value])}
            >
              {LEVERS.map(l => <Select.Option key={l.key} value={l.key}>{l.label}</Select.Option>)}
            </Select>
          </Col>
          <Col span={6}>
            <Text strong>Levels</Text>
            <Select
              mode="multiple"
              style={{ width: '100%', marginTop: '4px' }}
              placeholder="Select levels"
              value={selectedLevels}
              onChange={setSelectedLevels}
            >
              {LEVELS.map(lv => <Select.Option key={lv} value={lv}>{lv}</Select.Option>)}
            </Select>
          </Col>
          <Col span={6}>
            <Text strong>Value (%)</Text>
            <InputNumber
              style={{ width: '100%', marginTop: '4px' }}
              placeholder="Enter percentage"
              min={0}
              max={selectedLevers.includes('utr') ? 100 : 100}
              step={0.1}
              value={leverValue}
              onChange={v => setLeverValue(v ?? 0)}
              suffix="%"
            />
          </Col>
          <Col span={6}>
            <Text strong>Apply to</Text>
            <Select
              style={{ width: '100%', marginTop: '4px' }}
              value={selectedTimePeriod}
              onChange={setSelectedTimePeriod}
            >
              <Select.Option value="monthly">Monthly</Select.Option>
              <Select.Option value="half-year">Half-Yearly</Select.Option>
              <Select.Option value="yearly">Yearly</Select.Option>
            </Select>
          </Col>
        </Row>

        {/* Office Selection Row */}
        <Row gutter={16} align="middle">
          <Col span={8}>
            <Checkbox
              checked={applyToAllOffices}
              onChange={e => {
                setApplyToAllOffices(e.target.checked);
                if (e.target.checked) {
                  setSelectedOfficeJourney('');
                  setSelectedOffices([]);
                }
              }}
            >
              Apply to all offices
            </Checkbox>
          </Col>
          {!applyToAllOffices && (
            <>
              <Col span={8}>
                <Text strong>Office Journey</Text>
                <Select
                  style={{ width: '100%', marginTop: '4px' }}
                  value={selectedOfficeJourney}
                  onChange={(value) => {
                    setSelectedOfficeJourney(value);
                    if (value) setSelectedOffices([]);
                  }}
                  placeholder="Select journey type"
                  allowClear
                >
                  <Select.Option value="New Office">New Office (0-24 FTE)</Select.Option>
                  <Select.Option value="Emerging Office">Emerging Office (25-199 FTE)</Select.Option>
                  <Select.Option value="Established Office">Established Office (200-499 FTE)</Select.Option>
                  <Select.Option value="Mature Office">Mature Office (500+ FTE)</Select.Option>
                </Select>
              </Col>
              {!selectedOfficeJourney && (
                <Col span={8}>
                  <Text strong>Specific Offices</Text>
                  <Select
                    mode="multiple"
                    style={{ width: '100%', marginTop: '4px' }}
                    placeholder="Select offices"
                    value={selectedOffices}
                    onChange={setSelectedOffices}
                  >
                    {officeOptions.map(office => <Select.Option key={office.value} value={office.value}>{office.label}</Select.Option>)}
                  </Select>
                </Col>
              )}
            </>
          )}
        </Row>
        
        {/* Apply Levers Button and Applied Levers Display */}
        <Row gutter={16} style={{ marginTop: 16, marginBottom: 16 }}>
          <Col span={6}>
            <Button 
              type="primary"
              icon={leverApplying ? <LoadingOutlined /> : <ControlOutlined />}
              loading={leverApplying}
              onClick={handleApplyLevers}
              disabled={!selectedLevers.length || !selectedLevels.length || leverValue === null || configLoading}
              style={{ width: '100%' }}
            >
              {leverApplying ? 'Applying...' : 'Apply Lever'}
            </Button>
          </Col>
          <Col span={6}>
            <Button 
              danger
              onClick={handleClearAllLevers}
              disabled={appliedLevers.length === 0 || configLoading}
              style={{ width: '100%' }}
            >
              Clear All Levers ({appliedLevers.length})
            </Button>
          </Col>
          <Col span={12}>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              Configure lever settings above, then click "Apply Lever" to add to simulation. 
              Applied levers will be used when running simulations.
            </Text>
          </Col>
        </Row>

        {/* Applied Levers Display */}
        {appliedLevers.length > 0 && (
          <Collapse style={{ marginTop: 16 }}>
            <Collapse.Panel header={`📊 Applied Levers (${appliedLevers.length})`} key="applied-levers">
              <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                {appliedLevers.map((lever, index) => (
                  <Card key={lever.id} size="small" style={{ marginBottom: 8 }}>
                    <Row align="middle">
                      <Col span={18}>
                        <Text strong>{lever.leverType.toUpperCase()}</Text>
                        <Text style={{ marginLeft: 8, color: '#666' }}>
                          {lever.levels.join(', ')} levels • {lever.value}% • {lever.timePeriod}
                        </Text>
                        <br />
                        <Text type="secondary" style={{ fontSize: '11px' }}>
                          {lever.officeJourney ? `${lever.officeJourney}` : `${lever.targetOffices.length} office(s)`}
                          {' • Applied: '}{new Date(lever.appliedAt).toLocaleTimeString()}
                        </Text>
                      </Col>
                      <Col span={6} style={{ textAlign: 'right' }}>
                        <Button 
                          type="text" 
                          size="small" 
                          danger
                          onClick={() => {
                            setAppliedLevers(prev => prev.filter(l => l.id !== lever.id));
                            message.success('Lever removed');
                          }}
                        >
                          Remove
                        </Button>
                      </Col>
                    </Row>
                  </Card>
                ))}
              </div>
            </Collapse.Panel>
          </Collapse>
        )}
      </Card>

      {/* Simulation Scope Card */}
      <Card 
        title="Simulation Scope" 
        style={{ marginBottom: '16px' }}
      >
        {/* Duration Selection */}
        <Row gutter={16} align="middle" style={{ marginBottom: 16 }}>
          <Col span={12}>
            <Text strong>Simulation Duration</Text>
            <Input.Group compact style={{ marginTop: '4px' }}>
              <InputNumber
                style={{ width: '60%' }}
                value={simulationDuration}
                onChange={(value) => setSimulationDuration(value || 1)}
                step={1}
                min={1}
                max={120}
              />
              <Select
                style={{ width: '40%' }}
                value={selectedDurationUnit}
                onChange={setSelectedDurationUnit}
              >
                <Select.Option value="months">Months</Select.Option>
                <Select.Option value="half-years">Half-Years</Select.Option>
                <Select.Option value="years">Years</Select.Option>
              </Select>
            </Input.Group>
            <Text type="secondary" style={{ fontSize: '11px' }}>
              {(() => {
                const totalMonths = selectedDurationUnit === 'years' ? simulationDuration * 12 : 
                                  selectedDurationUnit === 'half-years' ? simulationDuration * 6 : 
                                  simulationDuration;
                const endYear = 2025 + Math.ceil(totalMonths / 12) - 1;
                return totalMonths <= 12 ? '2025' : `2025-${endYear}`;
              })()}
            </Text>
          </Col>
        </Row>


      </Card>

      {/* Economic Parameters Card */}
      <Card 
        title="Economic Parameters" 
        style={{ 
          marginBottom: '24px',
          backgroundColor: darkMode ? '#1f1f1f' : undefined,
          borderColor: darkMode ? '#303030' : undefined
        }}
      >
        <Row gutter={[16, 16]}>
          <Col span={6}>
            <Text strong>Price Increase (%)</Text>
            <InputNumber
              style={{ width: '100%', marginTop: '4px' }}
              value={priceIncrease}
              onChange={(value) => setPriceIncrease(value || 0)}
              suffix="%"
              step={0.1}
              min={0}
              max={100}
            />
            <div style={{ fontSize: '11px', color: darkMode ? '#999' : '#888', marginTop: '2px' }}>
              Annual percentage increase in hourly prices for all offices
            </div>
          </Col>
          <Col span={6}>
            <Text strong>Salary Increase (%)</Text>
            <InputNumber
              style={{ width: '100%', marginTop: '4px' }}
              value={salaryIncrease}
              onChange={(value) => setSalaryIncrease(value || 0)}
              suffix="%"
              step={0.1}
              min={0}
              max={100}
            />
            <div style={{ fontSize: '11px', color: darkMode ? '#999' : '#888', marginTop: '2px' }}>
              Annual percentage increase in monthly salaries for all offices
            </div>
          </Col>
          <Col span={6}>
            <Text strong>Working Hours</Text>
            <InputNumber
              style={{ width: '100%', marginTop: '4px' }}
              value={workingHours}
              onChange={(value) => setWorkingHours(value || 0)}
              step={0.1}
              min={0}
            />
            <div style={{ fontSize: '11px', color: darkMode ? '#999' : '#888', marginTop: '2px' }}>
              Standard working hours per FTE per month (before absence)
            </div>
          </Col>
          <Col span={6}>
            <Text strong>Unplanned Absence (hours/month)</Text>
            <InputNumber
              style={{ width: '100%', marginTop: '4px' }}
              value={unplannedAbsence}
              onChange={(value) => setUnplannedAbsence(value || 0)}
              step={0.1}
              min={0}
              max={workingHours}
            />
            <div style={{ fontSize: '11px', color: darkMode ? '#999' : '#888', marginTop: '2px' }}>
              Average unplanned absence per FTE per month (hours)
            </div>
          </Col>
          <Col span={6}>
            <Text strong>Other Expense</Text>
            <InputNumber
              style={{ width: '100%', marginTop: '4px' }}
              value={otherExpense}
              onChange={(value) => setOtherExpense(value || 0)}
              formatter={value => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
              step={1000}
              min={0}
            />
            <div style={{ fontSize: '11px', color: darkMode ? '#999' : '#888', marginTop: '2px' }}>
              Lump sum per <b>month</b> for <b>all offices combined</b> (not per person or per office), in <b>SEK</b>
            </div>
          </Col>
        </Row>
      </Card>



      {/* Run Simulation Button */}
      <Row style={{ marginBottom: '24px' }}>
        <Col span={24} style={{ textAlign: 'center' }}>
          <Space size="middle">
            <Button 
              type="primary" 
              size="large"
              icon={simulationRunning ? <LoadingOutlined /> : <RocketOutlined />}
              loading={simulationRunning}
              onClick={handleRunSimulation}
              disabled={configLoading}
              style={{ minWidth: '200px' }}
            >
              {simulationRunning ? 'Running Simulation...' : 'Run Simulation'}
            </Button>
            <Button 
              size="large"
              onClick={() => window.location.href = '/configuration'}
              disabled={configLoading}
            >
              Load Config Data
            </Button>
            <Button 
              size="large"
              onClick={() => {
                setAppliedLevers([]);
                setPriceIncrease(3.0);
                setSalaryIncrease(2.0);
                setWorkingHours(166.4);
                setUnplannedAbsence(15.7);
                setOtherExpense(19000000);
                setSimulationDuration(3);
                setSelectedDurationUnit('years');
                message.success('Configuration reset to defaults');
              }}
              disabled={configLoading}
            >
              Reset to Config
            </Button>
          </Space>
        </Col>
      </Row>



      {/* Simulation Results Card */}
      <Card title="Simulation Results">
        {/* Year Selector Tabs */}
        {availableYears.length > 0 ? (
          <div>
            <div style={{ marginBottom: '8px', fontSize: '14px', color: '#666' }}>
              <strong>Active Year: {activeYear}</strong> | Available Years: {availableYears.join(', ')}
            </div>
            <Tabs activeKey={activeYear} onChange={handleYearChange} style={{ marginBottom: '24px' }}>
              {availableYears.map(year => (
                <TabPane tab={`Year ${year} ${year === activeYear ? '(Active)' : ''}`} key={year} />
              ))}
            </Tabs>
          </div>
        ) : (
          <div style={{ 
            textAlign: 'center', 
            padding: '40px', 
            color: '#8c8c8c',
            marginBottom: '24px'
          }}>
            <Text type="secondary">
              No simulation results available. Run a simulation to see data.
            </Text>
          </div>
        )}

        {/* Data/Insights Tabs */}
        <Tabs defaultActiveKey="data" style={{ marginBottom: 24 }}>
          <TabPane tab="Data Tab" key="data">
            {/* Financial Performance */}
            {simulationResults && (
              <div style={{ marginBottom: '32px' }}>
                <Title level={4} style={{ marginBottom: '16px' }}>Financial Performance</Title>
                <Row gutter={[16, 16]}>
                  <Col xs={24} sm={12} lg={8}>
                    <Card size="small" style={{ textAlign: 'center', height: '120px' }}>
                      <Text type="secondary" style={{ fontSize: '12px' }}>Net Sales</Text>
                      <div style={{ fontSize: '20px', fontWeight: '600', margin: '4px 0' }}>
                        {(() => {
                          const kpi = kpiData.find(k => k.title === 'Net Sales');
                          return kpi ? kpi.currentValue : 'N/A';
                        })()}
                      </div>
                      <Text type="secondary" style={{ fontSize: '10px', display: 'block', marginBottom: '2px' }}>
                        Total revenue from client services
                      </Text>
                      {(() => {
                        const kpi = kpiData.find(k => k.title === 'Net Sales');
                        if (kpi && kpi.previousValue !== undefined) {
                          return (
                            <div style={{ fontSize: '9px', color: '#8c8c8c', lineHeight: '1.1' }}>
                              <div>Baseline: {kpi.previousValue} {kpi.unit}</div>
                              {kpi.change !== undefined && (
                                <div style={{ 
                                  color: kpi.change >= 0 ? '#52c41a' : '#f5222d',
                                  fontWeight: '600'
                                }}>
                                  {kpi.change >= 0 ? '+' : ''}{(kpi.change / 1000000).toFixed(1)}M vs baseline
                                </div>
                              )}
                            </div>
                          );
                        }
                        return null;
                      })()}
                    </Card>
                  </Col>
                  <Col xs={24} sm={12} lg={8}>
                    <Card size="small" style={{ textAlign: 'center', height: '120px' }}>
                      <Text type="secondary" style={{ fontSize: '12px' }}>Total Salary Costs</Text>
                      <div style={{ fontSize: '20px', fontWeight: '600', margin: '4px 0' }}>
                        {(() => {
                          const kpi = kpiData.find(k => k.title === 'Total Salary Costs');
                          return kpi ? kpi.currentValue : 'N/A';
                        })()}
                      </div>
                      <Text type="secondary" style={{ fontSize: '10px', display: 'block', marginBottom: '2px' }}>
                        Total salary costs including employment overhead
                      </Text>
                      {(() => {
                        const kpi = kpiData.find(k => k.title === 'Total Salary Costs');
                        if (kpi && kpi.previousValue !== undefined) {
                          return (
                            <div style={{ fontSize: '9px', color: '#8c8c8c', lineHeight: '1.1' }}>
                              <div>Baseline: {kpi.previousValue} {kpi.unit}</div>
                              {kpi.change !== undefined && (
                                <div style={{ 
                                  color: kpi.change >= 0 ? '#52c41a' : '#f5222d',
                                  fontWeight: '600'
                                }}>
                                  {kpi.change >= 0 ? '+' : ''}{(kpi.change / 1000000).toFixed(1)}M vs baseline
                                </div>
                              )}
                            </div>
                          );
                        }
                        return null;
                      })()}
                    </Card>
                  </Col>
                  <Col xs={24} sm={12} lg={8}>
                    <Card size="small" style={{ textAlign: 'center', height: '120px' }}>
                      <Text type="secondary" style={{ fontSize: '12px' }}>EBITDA</Text>
                      <div style={{ fontSize: '20px', fontWeight: '600', margin: '4px 0' }}>
                        {(() => {
                          const kpi = kpiData.find(k => k.title === 'EBITDA');
                          return kpi ? kpi.currentValue : 'N/A';
                        })()}
                      </div>
                      <Text type="secondary" style={{ fontSize: '10px', display: 'block', marginBottom: '2px' }}>
                        Earnings before interest, taxes, depreciation
                      </Text>
                      {(() => {
                        const kpi = kpiData.find(k => k.title === 'EBITDA');
                        if (kpi && kpi.previousValue !== undefined) {
                          return (
                            <div style={{ fontSize: '9px', color: '#8c8c8c', lineHeight: '1.1' }}>
                              <div>Baseline: {kpi.previousValue} {kpi.unit}</div>
                              {kpi.change !== undefined && (
                                <div style={{ 
                                  color: kpi.change >= 0 ? '#52c41a' : '#f5222d',
                                  fontWeight: '600'
                                }}>
                                  {kpi.change >= 0 ? '+' : ''}{(kpi.change / 1000000).toFixed(1)}M vs baseline
                                </div>
                              )}
                            </div>
                          );
                        }
                        return null;
                      })()}
                    </Card>
                  </Col>
                  <Col xs={24} sm={12} lg={8}>
                    <Card size="small" style={{ textAlign: 'center', height: '120px' }}>
                      <Text type="secondary" style={{ fontSize: '12px' }}>EBITDA Margin</Text>
                      <div style={{ fontSize: '20px', fontWeight: '600', margin: '4px 0' }}>
                        {(() => {
                          const kpi = kpiData.find(k => k.title === 'EBITDA Margin');
                          return kpi ? kpi.currentValue : 'N/A';
                        })()}
                      </div>
                      <Text type="secondary" style={{ fontSize: '10px', display: 'block', marginBottom: '2px' }}>
                        EBITDA as percentage of net sales
                      </Text>
                      {(() => {
                        const kpi = kpiData.find(k => k.title === 'EBITDA Margin');
                        if (kpi && kpi.previousValue !== undefined) {
                          return (
                            <div style={{ fontSize: '9px', color: '#8c8c8c', lineHeight: '1.1' }}>
                              <div>Baseline: {kpi.previousValue}</div>
                              {kpi.change !== undefined && (
                                <div style={{ 
                                  color: kpi.change >= 0 ? '#52c41a' : '#f5222d',
                                  fontWeight: '600'
                                }}>
                                  {kpi.change >= 0 ? '+' : ''}{kpi.change.toFixed(1)}% vs baseline
                                </div>
                              )}
                            </div>
                          );
                        }
                        return null;
                      })()}
                    </Card>
                  </Col>
                  <Col xs={24} sm={12} lg={8}>
                    <Card size="small" style={{ textAlign: 'center', height: '120px' }}>
                      <Text type="secondary" style={{ fontSize: '12px' }}>Gross Margin</Text>
                      <div style={{ fontSize: '20px', fontWeight: '600', margin: '4px 0' }}>
                        {(() => {
                          const kpi = kpiData.find(k => k.title === 'Gross Margin');
                          return kpi ? kpi.currentValue : 'N/A';
                        })()}
                      </div>
                      <Text type="secondary" style={{ fontSize: '10px', display: 'block', marginBottom: '2px' }}>
                        Net sales minus total costs
                      </Text>
                      {(() => {
                        const kpi = kpiData.find(k => k.title === 'Gross Margin');
                        if (kpi && kpi.previousValue !== undefined) {
                          return (
                            <div style={{ fontSize: '9px', color: '#8c8c8c', lineHeight: '1.1' }}>
                              <div>Baseline: {kpi.previousValue} {kpi.unit}</div>
                              {kpi.change !== undefined && (
                                <div style={{ 
                                  color: kpi.change >= 0 ? '#52c41a' : '#f5222d',
                                  fontWeight: '600'
                                }}>
                                  {kpi.change >= 0 ? '+' : ''}{(kpi.change / 1000000).toFixed(1)}M vs baseline
                                </div>
                              )}
                            </div>
                          );
                        }
                        return null;
                      })()}
                    </Card>
                  </Col>
                  <Col xs={24} sm={12} lg={8}>
                    <Card size="small" style={{ textAlign: 'center', height: '120px' }}>
                      <Text type="secondary" style={{ fontSize: '12px' }}>Avg Hourly Rate</Text>
                      <div style={{ fontSize: '20px', fontWeight: '600', margin: '4px 0' }}>
                        {(() => {
                          const kpi = kpiData.find(k => k.title === 'Avg Hourly Rate');
                          return kpi ? kpi.currentValue : 'N/A';
                        })()}
                      </div>
                      <Text type="secondary" style={{ fontSize: '10px', display: 'block', marginBottom: '2px' }}>
                        Average hourly rate for consultant services
                      </Text>
                      {(() => {
                        const kpi = kpiData.find(k => k.title === 'Avg Hourly Rate');
                        if (kpi && kpi.previousValue !== undefined) {
                          return (
                            <div style={{ fontSize: '9px', color: '#8c8c8c', lineHeight: '1.1' }}>
                              <div>Baseline: {kpi.previousValue} {kpi.unit}</div>
                              {kpi.change !== undefined && (
                                <div style={{ 
                                  color: kpi.change >= 0 ? '#52c41a' : '#f5222d',
                                  fontWeight: '600'
                                }}>
                                  {kpi.change >= 0 ? '+' : ''}{kpi.change.toFixed(0)} SEK vs baseline
                                </div>
                              )}
                            </div>
                          );
                        }
                        return null;
                      })()}
                    </Card>
                  </Col>
                </Row>
              </div>
            )}

            {/* Seniority Analysis Panel */}
            <Collapse style={{ marginBottom: '24px' }}>
              <Collapse.Panel header="📊 Seniority Analysis" key="seniority">
                <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
                  {/* Journey KPIs with Definitions and Baseline Comparison */}
                   <Col xs={24} sm={12} lg={6}>
                     <Card size="small" style={{ textAlign: 'center', height: '140px' }}>
                       <Text type="secondary" style={{ fontSize: '12px' }}>Journey 1</Text>
                       <div style={{ fontSize: '20px', fontWeight: '600', margin: '4px 0' }}>
                         {seniorityKPIs?.journey1Details?.percentage || 'N/A'}
                       </div>
                       <Text type="secondary" style={{ fontSize: '10px', display: 'block', marginBottom: '2px' }}>
                         {seniorityKPIs?.journey1Definition || 'A, AC, C'}
                       </Text>
                       {seniorityKPIs?.journey1Details && (
                         <div style={{ fontSize: '9px', color: '#8c8c8c', lineHeight: '1.1' }}>
                           <div>Current: {seniorityKPIs.journey1Details.current} FTE</div>
                           <div>Baseline: {seniorityKPIs.journey1Details.baseline} FTE</div>
                           <div style={{ 
                             color: seniorityKPIs.journey1Details.absolute >= 0 ? '#52c41a' : '#f5222d',
                             fontWeight: '600'
                           }}>
                             {seniorityKPIs.journey1Details.absoluteDisplay}
                           </div>
                         </div>
                       )}
                     </Card>
                   </Col>
                   <Col xs={24} sm={12} lg={6}>
                     <Card size="small" style={{ textAlign: 'center', height: '140px' }}>
                       <Text type="secondary" style={{ fontSize: '12px' }}>Journey 2</Text>
                       <div style={{ fontSize: '20px', fontWeight: '600', margin: '4px 0' }}>
                         {seniorityKPIs?.journey2Details?.percentage || 'N/A'}
                       </div>
                       <Text type="secondary" style={{ fontSize: '10px', display: 'block', marginBottom: '2px' }}>
                         {seniorityKPIs?.journey2Definition || 'SrC, AM'}
                       </Text>
                       {seniorityKPIs?.journey2Details && (
                         <div style={{ fontSize: '9px', color: '#8c8c8c', lineHeight: '1.1' }}>
                           <div>Current: {seniorityKPIs.journey2Details.current} FTE</div>
                           <div>Baseline: {seniorityKPIs.journey2Details.baseline} FTE</div>
                           <div style={{ 
                             color: seniorityKPIs.journey2Details.absolute >= 0 ? '#52c41a' : '#f5222d',
                             fontWeight: '600'
                           }}>
                             {seniorityKPIs.journey2Details.absoluteDisplay}
                           </div>
                         </div>
                       )}
                     </Card>
                   </Col>
                   <Col xs={24} sm={12} lg={6}>
                     <Card size="small" style={{ textAlign: 'center', height: '140px' }}>
                       <Text type="secondary" style={{ fontSize: '12px' }}>Journey 3</Text>
                       <div style={{ fontSize: '20px', fontWeight: '600', margin: '4px 0' }}>
                         {seniorityKPIs?.journey3Details?.percentage || 'N/A'}
                       </div>
                       <Text type="secondary" style={{ fontSize: '10px', display: 'block', marginBottom: '2px' }}>
                         {seniorityKPIs?.journey3Definition || 'M, SrM'}
                       </Text>
                       {seniorityKPIs?.journey3Details && (
                         <div style={{ fontSize: '9px', color: '#8c8c8c', lineHeight: '1.1' }}>
                           <div>Current: {seniorityKPIs.journey3Details.current} FTE</div>
                           <div>Baseline: {seniorityKPIs.journey3Details.baseline} FTE</div>
                           <div style={{ 
                             color: seniorityKPIs.journey3Details.absolute >= 0 ? '#52c41a' : '#f5222d',
                             fontWeight: '600'
                           }}>
                             {seniorityKPIs.journey3Details.absoluteDisplay}
                           </div>
                         </div>
                       )}
                     </Card>
                   </Col>
                   <Col xs={24} sm={12} lg={6}>
                     <Card size="small" style={{ textAlign: 'center', height: '140px' }}>
                       <Text type="secondary" style={{ fontSize: '12px' }}>Journey 4</Text>
                       <div style={{ fontSize: '20px', fontWeight: '600', margin: '4px 0' }}>
                         {seniorityKPIs?.journey4Details?.percentage || 'N/A'}
                       </div>
                       <Text type="secondary" style={{ fontSize: '10px', display: 'block', marginBottom: '2px' }}>
                         {seniorityKPIs?.journey4Definition || 'PiP'}
                       </Text>
                       {seniorityKPIs?.journey4Details && (
                         <div style={{ fontSize: '9px', color: '#8c8c8c', lineHeight: '1.1' }}>
                           <div>Current: {seniorityKPIs.journey4Details.current} FTE</div>
                           <div>Baseline: {seniorityKPIs.journey4Details.baseline} FTE</div>
                           <div style={{ 
                             color: seniorityKPIs.journey4Details.absolute >= 0 ? '#52c41a' : '#f5222d',
                             fontWeight: '600'
                           }}>
                             {seniorityKPIs.journey4Details.absoluteDisplay}
                           </div>
                         </div>
                       )}
                     </Card>
                   </Col>
                </Row>
                
                <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
                  {/* Additional Seniority KPIs with Baseline Comparison */}
                   <Col xs={24} sm={12} lg={8}>
                     <Card size="small" style={{ textAlign: 'center', height: '120px' }}>
                       <Text type="secondary" style={{ fontSize: '12px' }}>Progression Rate (avg)</Text>
                       <div style={{ fontSize: '20px', fontWeight: '600', margin: '4px 0' }}>
                         {seniorityKPIs?.progressionRateDetails?.percentage || 'N/A'}
                       </div>
                       {seniorityKPIs?.progressionRateDetails && (
                         <div style={{ fontSize: '9px', color: '#8c8c8c', lineHeight: '1.2' }}>
                           <div style={{ color: '#1890ff', fontWeight: '500' }}>→ Stable</div>
                           <div style={{ marginTop: '2px' }}>{seniorityKPIs.progressionRateDetails.description}</div>
                         </div>
                       )}
                     </Card>
                   </Col>
                   <Col xs={24} sm={12} lg={8}>
                     <Card size="small" style={{ textAlign: 'center', height: '120px' }}>
                       <Text type="secondary" style={{ fontSize: '12px' }}>Total Growth for Period</Text>
                       <div style={{ fontSize: '20px', fontWeight: '600', margin: '4px 0' }}>
                         {seniorityKPIs?.totalGrowthDetails?.percentage || 'N/A'}
                       </div>
                       {seniorityKPIs?.totalGrowthDetails && (
                         <div style={{ fontSize: '9px', color: '#8c8c8c', lineHeight: '1.2' }}>
                           <div>Current: {seniorityKPIs.totalGrowthDetails.current} FTE</div>
                           <div>Baseline: {seniorityKPIs.totalGrowthDetails.baseline} FTE</div>
                           <div style={{ 
                             color: seniorityKPIs.totalGrowthDetails.absolute >= 0 ? '#52c41a' : '#f5222d',
                             fontWeight: '600'
                           }}>
                             {seniorityKPIs.totalGrowthDetails.absoluteDisplay}
                           </div>
                         </div>
                       )}
                     </Card>
                   </Col>
                   <Col xs={24} sm={12} lg={8}>
                     <Card size="small" style={{ textAlign: 'center', height: '120px' }}>
                       <Text type="secondary" style={{ fontSize: '12px' }}>Non-debit Ratio</Text>
                       <div style={{ fontSize: '20px', fontWeight: '600', margin: '4px 0' }}>
                         {seniorityKPIs?.nonDebitDetails?.percentage || 'N/A'}
                       </div>
                       {seniorityKPIs?.nonDebitDetails && (
                         <div style={{ fontSize: '9px', color: '#8c8c8c', lineHeight: '1.2' }}>
                           <div>Current: {seniorityKPIs.nonDebitDetails.current}%</div>
                           <div>Baseline: {seniorityKPIs.nonDebitDetails.baseline}%</div>
                           <div style={{ 
                             color: seniorityKPIs.nonDebitDetails.absolute >= 0 ? '#52c41a' : '#f5222d',
                             fontWeight: '600'
                           }}>
                             {seniorityKPIs.nonDebitDetails.absoluteDisplay}
                           </div>
                         </div>
                       )}
                     </Card>
                   </Col>
                </Row>

                {/* Seniority Distribution Table */}
                <div style={{ marginBottom: '16px' }}>
                  <Title level={5}>Seniority Distribution by Office</Title>
                  <Table
                    size="small"
                    pagination={false}
                    columns={[
                      { title: 'Office', dataIndex: 'office', key: 'office' },
                      { 
                        title: 'Total', 
                        dataIndex: 'total', 
                        key: 'total', 
                        render: (value) => {
                          if (typeof value === 'string' && value.includes('(')) {
                            const [base, delta] = value.split(' (');
                            const deltaValue = delta.replace(')', '');
                            const isPositive = deltaValue.startsWith('+');
                            const isNegative = deltaValue.startsWith('-');
                            return (
                              <span style={{ fontWeight: '600' }}>
                                {base}{' '}
                                <span style={{ 
                                  color: isPositive ? '#52c41a' : isNegative ? '#f5222d' : '#8c8c8c',
                                  fontSize: '0.9em'
                                }}>
                                  ({deltaValue})
                                </span>
                              </span>
                            );
                          }
                          return <span style={{ fontWeight: '600' }}>{value}</span>;
                        }
                      },
                      { 
                        title: 'A Level', 
                        dataIndex: 'levelA', 
                        key: 'levelA',
                        render: (value) => {
                          if (typeof value === 'string' && value.includes('(')) {
                            const [base, delta] = value.split(' (');
                            const deltaValue = delta.replace(')', '');
                            const isPositive = deltaValue.startsWith('+');
                            const isNegative = deltaValue.startsWith('-');
                            return (
                              <span>
                                {base}{' '}
                                <span style={{ 
                                  color: isPositive ? '#52c41a' : isNegative ? '#f5222d' : '#8c8c8c',
                                  fontSize: '0.85em'
                                }}>
                                  ({deltaValue})
                                </span>
                              </span>
                            );
                          }
                          return value;
                        }
                      },
                      { 
                        title: 'AC Level', 
                        dataIndex: 'levelAC', 
                        key: 'levelAC',
                        render: (value) => {
                          if (typeof value === 'string' && value.includes('(')) {
                            const [base, delta] = value.split(' (');
                            const deltaValue = delta.replace(')', '');
                            const isPositive = deltaValue.startsWith('+');
                            const isNegative = deltaValue.startsWith('-');
                            return (
                              <span>
                                {base}{' '}
                                <span style={{ 
                                  color: isPositive ? '#52c41a' : isNegative ? '#f5222d' : '#8c8c8c',
                                  fontSize: '0.85em'
                                }}>
                                  ({deltaValue})
                                </span>
                              </span>
                            );
                          }
                          return value;
                        }
                      },
                      { 
                        title: 'C Level', 
                        dataIndex: 'levelC', 
                        key: 'levelC',
                        render: (value) => {
                          if (typeof value === 'string' && value.includes('(')) {
                            const [base, delta] = value.split(' (');
                            const deltaValue = delta.replace(')', '');
                            const isPositive = deltaValue.startsWith('+');
                            const isNegative = deltaValue.startsWith('-');
                            return (
                              <span>
                                {base}{' '}
                                <span style={{ 
                                  color: isPositive ? '#52c41a' : isNegative ? '#f5222d' : '#8c8c8c',
                                  fontSize: '0.85em'
                                }}>
                                  ({deltaValue})
                                </span>
                              </span>
                            );
                          }
                          return value;
                        }
                      },
                      { 
                        title: 'SrC Level', 
                        dataIndex: 'levelSrC', 
                        key: 'levelSrC',
                        render: (value) => {
                          if (typeof value === 'string' && value.includes('(')) {
                            const [base, delta] = value.split(' (');
                            const deltaValue = delta.replace(')', '');
                            const isPositive = deltaValue.startsWith('+');
                            const isNegative = deltaValue.startsWith('-');
                            return (
                              <span>
                                {base}{' '}
                                <span style={{ 
                                  color: isPositive ? '#52c41a' : isNegative ? '#f5222d' : '#8c8c8c',
                                  fontSize: '0.85em'
                                }}>
                                  ({deltaValue})
                                </span>
                              </span>
                            );
                          }
                          return value;
                        }
                      },
                      { 
                        title: 'AM Level', 
                        dataIndex: 'levelAM', 
                        key: 'levelAM',
                        render: (value) => {
                          if (typeof value === 'string' && value.includes('(')) {
                            const [base, delta] = value.split(' (');
                            const deltaValue = delta.replace(')', '');
                            const isPositive = deltaValue.startsWith('+');
                            const isNegative = deltaValue.startsWith('-');
                            return (
                              <span>
                                {base}{' '}
                                <span style={{ 
                                  color: isPositive ? '#52c41a' : isNegative ? '#f5222d' : '#8c8c8c',
                                  fontSize: '0.85em'
                                }}>
                                  ({deltaValue})
                                </span>
                              </span>
                            );
                          }
                          return value;
                        }
                      },
                      { 
                        title: 'M Level', 
                        dataIndex: 'levelM', 
                        key: 'levelM',
                        render: (value) => {
                          if (typeof value === 'string' && value.includes('(')) {
                            const [base, delta] = value.split(' (');
                            const deltaValue = delta.replace(')', '');
                            const isPositive = deltaValue.startsWith('+');
                            const isNegative = deltaValue.startsWith('-');
                            return (
                              <span>
                                {base}{' '}
                                <span style={{ 
                                  color: isPositive ? '#52c41a' : isNegative ? '#f5222d' : '#8c8c8c',
                                  fontSize: '0.85em'
                                }}>
                                  ({deltaValue})
                                </span>
                              </span>
                            );
                          }
                          return value;
                        }
                      },
                      { 
                        title: 'SrM Level', 
                        dataIndex: 'levelSrM', 
                        key: 'levelSrM',
                        render: (value) => {
                          if (typeof value === 'string' && value.includes('(')) {
                            const [base, delta] = value.split(' (');
                            const deltaValue = delta.replace(')', '');
                            const isPositive = deltaValue.startsWith('+');
                            const isNegative = deltaValue.startsWith('-');
                            return (
                              <span>
                                {base}{' '}
                                <span style={{ 
                                  color: isPositive ? '#52c41a' : isNegative ? '#f5222d' : '#8c8c8c',
                                  fontSize: '0.85em'
                                }}>
                                  ({deltaValue})
                                </span>
                              </span>
                            );
                          }
                          return value;
                        }
                      },
                      { 
                        title: 'PiP Level', 
                        dataIndex: 'levelPiP', 
                        key: 'levelPiP',
                        render: (value) => {
                          if (typeof value === 'string' && value.includes('(')) {
                            const [base, delta] = value.split(' (');
                            const deltaValue = delta.replace(')', '');
                            const isPositive = deltaValue.startsWith('+');
                            const isNegative = deltaValue.startsWith('-');
                            return (
                              <span>
                                {base}{' '}
                                <span style={{ 
                                  color: isPositive ? '#52c41a' : isNegative ? '#f5222d' : '#8c8c8c',
                                  fontSize: '0.85em'
                                }}>
                                  ({deltaValue})
                                </span>
                              </span>
                            );
                          }
                          return value;
                        }
                      },
                      { 
                        title: 'Operations', 
                        dataIndex: 'operations', 
                        key: 'operations',
                        render: (value) => {
                          if (typeof value === 'string' && value.includes('(')) {
                            const [base, delta] = value.split(' (');
                            const deltaValue = delta.replace(')', '');
                            const isPositive = deltaValue.startsWith('+');
                            const isNegative = deltaValue.startsWith('-');
                            return (
                              <span>
                                {base}{' '}
                                <span style={{ 
                                  color: isPositive ? '#52c41a' : isNegative ? '#f5222d' : '#8c8c8c',
                                  fontSize: '0.85em'
                                }}>
                                  ({deltaValue})
                                </span>
                              </span>
                            );
                          }
                          return value;
                        }
                      },
                      { title: 'Non-debit Ratio', dataIndex: 'nonDebitRatio', key: 'nonDebitRatio', render: (value) => <span style={{ fontWeight: '500' }}>{value}%</span> }
                    ]}
                                     dataSource={seniorityData}
                  />
                </div>
              </Collapse.Panel>
            </Collapse>

            {/* Detailed Data Analysis Table */}
            <div>
              <Title level={4} style={{ marginBottom: '16px' }}>
                <TableOutlined style={{ marginRight: '8px' }} />
                Detailed Data Analysis
              </Title>
              <Table
                columns={tableColumns}
                dataSource={tableData}
                pagination={false}
                size="small"
                bordered
                expandable={{
                  expandedRowRender: (record) => (
                    <div style={{ padding: '16px' }}>
                      <Row gutter={16}>
                        <Col span={12}>
                          <Text strong>Role Breakdown:</Text>
                          <div style={{ marginTop: '8px' }}>
                            <Text type="secondary">Consultant: {record.consultantFTE || 0} FTE</Text><br/>
                            <Text type="secondary">Sales: {record.salesFTE || 0} FTE</Text><br/>
                            <Text type="secondary">Recruitment: {record.recruitmentFTE || 0} FTE</Text><br/>
                            <Text type="secondary">Operations: {record.operationsFTE || 0} FTE</Text>
                          </div>
                        </Col>
                        <Col span={12}>
                          <Text strong>Financial Details:</Text>
                          <div style={{ marginTop: '8px' }}>
                            <Text type="secondary">Revenue: {record.revenue || 'N/A'}</Text><br/>
                            <Text type="secondary">Gross Margin: {record.grossMargin || 'N/A'}</Text><br/>
                            <Text type="secondary">EBITDA: {record.ebitda || 'N/A'}</Text><br/>
                            <Text type="secondary">Journey: {record.office_journey || 'N/A'}</Text>
                          </div>
                        </Col>
                      </Row>
                    </div>
                  ),
                  rowExpandable: (record) => record.office !== 'No data', // Only expand rows with data
                }}
                            />
            </div>

            {/* Logs Section */}
            {simulationResults && activeYear && (() => {
              const yearData = simulationResults.years[activeYear];
              if (!yearData?.offices) return null;

              // Process logs data with aggregation
              const processLogsData = () => {
                const logs: any[] = [];
                const offices = Object.keys(yearData.offices);
                const levels = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP'];

                offices.forEach(officeName => {
                  const officeData = yearData.offices[officeName];
                  if (!officeData.levels) return;

                  // Dynamically get roles from the data instead of hardcoding
                  const roles = Object.keys(officeData.levels);

                  roles.forEach(role => {
                    const roleData = officeData.levels[role];
                    if (!roleData) return;

                    levels.forEach(level => {
                      const levelData = roleData[level];
                      if (!levelData || !Array.isArray(levelData)) return;

                      // Calculate yearly aggregated values
                      const yearlyTotals = {
                        recruited: 0,
                        churned: 0,
                        progressedOut: 0,
                        progressedIn: 0,
                        totalBefore: levelData[0] ? (levelData[0].total - levelData[0].recruited + levelData[0].churned + levelData[0].progressed_out - levelData[0].progressed_in) : 0,
                        totalAfter: levelData[levelData.length - 1]?.total || 0
                      };

                      const monthlyData: any[] = [];

                      // Process each time period for monthly breakdown
                      levelData.forEach((periodData: any, periodIndex: number) => {
                        if (!periodData) return; // Guard against null/undefined periodData
                        
                        yearlyTotals.recruited += periodData.recruited || 0;
                        yearlyTotals.churned += periodData.churned || 0;
                        yearlyTotals.progressedOut += periodData.progressed_out || 0;
                        yearlyTotals.progressedIn += periodData.progressed_in || 0;

                        if (periodData.recruited > 0 || periodData.churned > 0 || periodData.progressed_out > 0 || periodData.progressed_in > 0) {
                          monthlyData.push({
                            key: `${officeName}-${role}-${level}-${periodIndex}`,
                            office: officeName,
                            role: role,
                            level: level,
                            period: `Month ${periodIndex + 1}`,
                            periodIndex: periodIndex,
                            recruited: periodData.recruited || 0,
                            churned: periodData.churned || 0,
                            progressedOut: periodData.progressed_out || 0,
                            progressedIn: periodData.progressed_in || 0,
                            totalBefore: periodIndex > 0 ? (levelData[periodIndex - 1]?.total || 0) : yearlyTotals.totalBefore,
                            totalAfter: periodData.total || 0
                          });
                        }
                      });

                      // Only add if there's activity
                      if (yearlyTotals.recruited > 0 || yearlyTotals.churned > 0 || yearlyTotals.progressedOut > 0 || yearlyTotals.progressedIn > 0) {
                        logs.push({
                          key: `${officeName}-${role}-${level}-yearly`,
                          office: officeName,
                          role: role,
                          level: level,
                          period: `${activeYear} Total`,
                          periodIndex: -1, // Special value for yearly aggregation
                          recruited: yearlyTotals.recruited,
                          churned: yearlyTotals.churned,
                          progressedOut: yearlyTotals.progressedOut,
                          progressedIn: yearlyTotals.progressedIn,
                          totalBefore: yearlyTotals.totalBefore,
                          totalAfter: yearlyTotals.totalAfter,
                          isYearlyTotal: true,
                          monthlyData: monthlyData
                        });
                      }
                    });
                  });

                  // Add operations logs if they exist
                  if (officeData.operations && Array.isArray(officeData.operations)) {
                    const firstOperation = officeData.operations[0];
                    const lastOperation = officeData.operations[officeData.operations.length - 1];
                    
                    const yearlyTotals = {
                      recruited: 0,
                      churned: 0,
                      totalBefore: firstOperation && firstOperation.total !== undefined ? 
                        (firstOperation.total - (firstOperation.recruited || 0) + (firstOperation.churned || 0)) : 0,
                      totalAfter: lastOperation?.total || 0
                    };

                    const monthlyData: any[] = [];

                    officeData.operations.forEach((periodData: any, periodIndex: number) => {
                      if (!periodData) return; // Guard against null/undefined periodData
                      
                      yearlyTotals.recruited += periodData.recruited || 0;
                      yearlyTotals.churned += periodData.churned || 0;

                      if (periodData && (periodData.recruited > 0 || periodData.churned > 0)) {
                        monthlyData.push({
                          key: `${officeName}-Operations-Operations-${periodIndex}`,
                          office: officeName,
                          role: 'Operations',
                          level: 'Operations',
                          period: `Month ${periodIndex + 1}`,
                          periodIndex: periodIndex,
                          recruited: periodData.recruited || 0,
                          churned: periodData.churned || 0,
                          progressedOut: 0,
                          progressedIn: 0,
                          totalBefore: periodIndex > 0 ? (officeData.operations[periodIndex - 1]?.total || 0) : yearlyTotals.totalBefore,
                          totalAfter: periodData.total || 0
                        });
                      }
                    });

                    if (yearlyTotals.recruited > 0 || yearlyTotals.churned > 0) {
                      logs.push({
                        key: `${officeName}-Operations-Operations-yearly`,
                        office: officeName,
                        role: 'Operations',
                        level: 'Operations',
                        period: `${activeYear} Total`,
                        periodIndex: -1,
                        recruited: yearlyTotals.recruited,
                        churned: yearlyTotals.churned,
                        progressedOut: 0,
                        progressedIn: 0,
                        totalBefore: yearlyTotals.totalBefore,
                        totalAfter: yearlyTotals.totalAfter,
                        isYearlyTotal: true,
                        monthlyData: monthlyData
                      });
                    }
                  }
                });

                return logs.sort((a, b) => {
                  if (a.office !== b.office) return a.office.localeCompare(b.office);
                  if (a.role !== b.role) return a.role.localeCompare(b.role);
                  if (a.level !== b.level) return a.level.localeCompare(b.level);
                  return a.periodIndex - b.periodIndex;
                });
              };

              const allLogsData = processLogsData();
              const uniqueOffices = [...new Set(allLogsData.map((log: any) => log.office))];
              const uniqueRoles = [...new Set(allLogsData.map((log: any) => log.role))];
              const uniqueLevels = [...new Set(allLogsData.map((log: any) => log.level))];
              
              // Filter logs based on selected office
              const logsData = selectedOfficeFilter 
                ? allLogsData.filter((log: any) => log.office === selectedOfficeFilter)
                : allLogsData;

              const logsColumns = [
                { 
                  title: 'Office', 
                  dataIndex: 'office', 
                  key: 'office',
                  width: 120,
                  filters: uniqueOffices.map((office: string) => ({ text: office, value: office })),
                  onFilter: (value: any, record: any) => record.office === value,
                },
                { 
                  title: 'Role', 
                  dataIndex: 'role', 
                  key: 'role',
                  width: 100,
                  filters: uniqueRoles.map((role: string) => ({ text: role, value: role })),
                  onFilter: (value: any, record: any) => record.role === value,
                },
                { 
                  title: 'Level', 
                  dataIndex: 'level', 
                  key: 'level',
                  width: 80,
                  filters: uniqueLevels.map((level: string) => ({ text: level, value: level })),
                  onFilter: (value: any, record: any) => record.level === value,
                },
                { 
                  title: 'Period', 
                  dataIndex: 'period', 
                  key: 'period',
                  width: 120,
                  render: (text: string, record: any) => (
                    <span style={{ fontWeight: record.isYearlyTotal ? '600' : '400' }}>
                      {text}
                    </span>
                  ),
                  sorter: (a: any, b: any) => a.periodIndex - b.periodIndex,
                },
                { 
                  title: 'FTE Before', 
                  dataIndex: 'totalBefore', 
                  key: 'totalBefore',
                  width: 90,
                  render: (value: any, record: any) => (
                    <span style={{ fontWeight: record.isYearlyTotal ? '600' : '500' }}>{value}</span>
                  )
                },
                { 
                  title: 'Recruited', 
                  dataIndex: 'recruited', 
                  key: 'recruited',
                  width: 90,
                  render: (value: any, record: any) => value > 0 ? (
                    <span style={{ 
                      color: '#52c41a', 
                      fontWeight: record.isYearlyTotal ? '700' : '600' 
                    }}>
                      +{value}
                    </span>
                  ) : '-'
                },
                { 
                  title: 'Churned', 
                  dataIndex: 'churned', 
                  key: 'churned',
                  width: 90,
                  render: (value: any, record: any) => value > 0 ? (
                    <span style={{ 
                      color: '#f5222d', 
                      fontWeight: record.isYearlyTotal ? '700' : '600' 
                    }}>
                      -{value}
                    </span>
                  ) : '-'
                },
                { 
                  title: 'Progressed Out', 
                  dataIndex: 'progressedOut', 
                  key: 'progressedOut',
                  width: 110,
                  render: (value: any, record: any) => value > 0 ? (
                    <span style={{ 
                      color: '#fa8c16', 
                      fontWeight: record.isYearlyTotal ? '700' : '600' 
                    }}>
                      -{value}
                    </span>
                  ) : '-'
                },
                { 
                  title: 'Progressed In', 
                  dataIndex: 'progressedIn', 
                  key: 'progressedIn',
                  width: 110,
                  render: (value: any, record: any) => value > 0 ? (
                    <span style={{ 
                      color: '#1890ff', 
                      fontWeight: record.isYearlyTotal ? '700' : '600' 
                    }}>
                      +{value}
                    </span>
                  ) : '-'
                },
                { 
                  title: 'FTE After', 
                  dataIndex: 'totalAfter', 
                  key: 'totalAfter',
                  width: 90,
                  render: (value: any, record: any) => (
                    <span style={{ fontWeight: record.isYearlyTotal ? '600' : '500' }}>{value}</span>
                  )
                },
                {
                  title: 'Net Change',
                  key: 'netChange',
                  width: 100,
                  render: (_: any, record: any) => {
                    const netChange = record.totalAfter - record.totalBefore;
                    const changeColor = netChange > 0 ? '#52c41a' : netChange < 0 ? '#f5222d' : '#8c8c8c';
                    const changeText = netChange > 0 ? `+${netChange}` : `${netChange}`;
                    return (
                      <span style={{ 
                        color: changeColor, 
                        fontWeight: record.isYearlyTotal ? '700' : '600' 
                      }}>
                        {changeText}
                      </span>
                    );
                  }
                }
              ];

              // Monthly details columns (for expanded rows)
              const monthlyColumns = [
                { title: 'Month', dataIndex: 'period', key: 'period', width: 100 },
                { title: 'FTE Before', dataIndex: 'totalBefore', key: 'totalBefore', width: 90 },
                { 
                  title: 'Recruited', 
                  dataIndex: 'recruited', 
                  key: 'recruited',
                  width: 90,
                  render: (value: any) => value > 0 ? <span style={{ color: '#52c41a', fontWeight: '600' }}>+{value}</span> : '-'
                },
                { 
                  title: 'Churned', 
                  dataIndex: 'churned', 
                  key: 'churned',
                  width: 90,
                  render: (value: any) => value > 0 ? <span style={{ color: '#f5222d', fontWeight: '600' }}>-{value}</span> : '-'
                },
                { 
                  title: 'Progressed Out', 
                  dataIndex: 'progressedOut', 
                  key: 'progressedOut',
                  width: 110,
                  render: (value: any) => value > 0 ? <span style={{ color: '#fa8c16', fontWeight: '600' }}>-{value}</span> : '-'
                },
                { 
                  title: 'Progressed In', 
                  dataIndex: 'progressedIn', 
                  key: 'progressedIn',
                  width: 110,
                  render: (value: any) => value > 0 ? <span style={{ color: '#1890ff', fontWeight: '600' }}>+{value}</span> : '-'
                },
                { title: 'FTE After', dataIndex: 'totalAfter', key: 'totalAfter', width: 90 },
                {
                  title: 'Net Change',
                  key: 'netChange',
                  width: 100,
                  render: (_: any, record: any) => {
                    const netChange = record.totalAfter - record.totalBefore;
                    const changeColor = netChange > 0 ? '#52c41a' : netChange < 0 ? '#f5222d' : '#8c8c8c';
                    const changeText = netChange > 0 ? `+${netChange}` : `${netChange}`;
                    return <span style={{ color: changeColor, fontWeight: '600' }}>{changeText}</span>;
                  }
                }
              ];

              // Summary stats
              const summaryStats = {
                totalRecruitment: logsData.reduce((sum: number, log: any) => sum + log.recruited, 0),
                totalChurn: logsData.reduce((sum: number, log: any) => sum + log.churned, 0),
                totalProgressedOut: logsData.reduce((sum: number, log: any) => sum + log.progressedOut, 0),
                totalProgressedIn: logsData.reduce((sum: number, log: any) => sum + log.progressedIn, 0),
                officesActive: new Set(logsData.map((log: any) => log.office)).size,
                periodsActive: new Set(logsData.map((log: any) => log.period)).size
              };

              return (
                <div style={{ marginTop: '32px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <Title level={4} style={{ margin: 0 }}>
                      📋 Movement Logs - Year {activeYear}
                    </Title>
                    
                    {/* Office Filter Selector */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Text strong style={{ fontSize: '13px' }}>Filter by Office:</Text>
                      <Select
                        placeholder="All Offices"
                        value={selectedOfficeFilter}
                        onChange={setSelectedOfficeFilter}
                        allowClear
                        style={{ minWidth: '150px' }}
                        size="small"
                      >
                        {uniqueOffices.map((office: string) => (
                          <Select.Option key={office} value={office}>
                            {office}
                          </Select.Option>
                        ))}
                      </Select>
                    </div>
                  </div>
                  
                  {/* Filter Status */}
                  {selectedOfficeFilter && (
                    <div style={{ 
                      marginBottom: '16px', 
                      padding: '8px 12px', 
                      backgroundColor: darkMode ? '#003a8c' : '#e6f7ff', 
                      borderRadius: '4px',
                      border: darkMode ? '1px solid #1890ff' : '1px solid #91d5ff'
                    }}>
                      <Text style={{ fontSize: '12px', color: darkMode ? '#91d5ff' : '#1890ff' }}>
                        📍 Showing logs for: <Text strong>{selectedOfficeFilter}</Text> 
                        ({logsData.length} yearly aggregations)
                      </Text>
                    </div>
                  )}

                  {/* Summary Cards */}
                  <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
                    <Col xs={24} sm={12} lg={6}>
                      <div 
                        className={darkMode ? 'summary-card-dark' : 'summary-card-light'}
                        style={{ 
                          textAlign: 'center', 
                          height: '100px',
                          borderRadius: '6px',
                          padding: '16px',
                          display: 'flex',
                          flexDirection: 'column',
                          justifyContent: 'center'
                        }}
                      >
                        <Text type="secondary" style={{ fontSize: '11px', color: darkMode ? '#d9d9d9 !important' : 'inherit' }}>Total Recruitment</Text>
                        <div style={{ fontSize: '18px', fontWeight: '600', margin: '4px 0', color: '#52c41a' }}>
                          +{summaryStats.totalRecruitment}
                        </div>
                        <Text type="secondary" style={{ fontSize: '10px', color: darkMode ? '#8c8c8c !important' : 'inherit' }}>
                          New hires across all offices
                        </Text>
                      </div>
                    </Col>
                    <Col xs={24} sm={12} lg={6}>
                      <div 
                        className={darkMode ? 'summary-card-dark' : 'summary-card-light'}
                        style={{ 
                          textAlign: 'center', 
                          height: '100px',
                          borderRadius: '6px',
                          padding: '16px',
                          display: 'flex',
                          flexDirection: 'column',
                          justifyContent: 'center'
                        }}
                      >
                        <Text type="secondary" style={{ fontSize: '11px', color: darkMode ? '#d9d9d9 !important' : 'inherit' }}>Total Churn</Text>
                        <div style={{ fontSize: '18px', fontWeight: '600', margin: '4px 0', color: '#f5222d' }}>
                          -{summaryStats.totalChurn}
                        </div>
                        <Text type="secondary" style={{ fontSize: '10px', color: darkMode ? '#8c8c8c !important' : 'inherit' }}>
                          Departures across all offices
                        </Text>
                      </div>
                    </Col>
                    <Col xs={24} sm={12} lg={6}>
                      <div 
                        className={darkMode ? 'summary-card-dark' : 'summary-card-light'}
                        style={{ 
                          textAlign: 'center', 
                          height: '100px',
                          borderRadius: '6px',
                          padding: '16px',
                          display: 'flex',
                          flexDirection: 'column',
                          justifyContent: 'center'
                        }}
                      >
                        <Text type="secondary" style={{ fontSize: '11px', color: darkMode ? '#d9d9d9 !important' : 'inherit' }}>Progression Moves</Text>
                        <div style={{ fontSize: '18px', fontWeight: '600', margin: '4px 0', color: '#1890ff' }}>
                          {summaryStats.totalProgressedOut}
                        </div>
                        <Text type="secondary" style={{ fontSize: '10px', color: darkMode ? '#8c8c8c !important' : 'inherit' }}>
                          Level promotions & transitions
                        </Text>
                      </div>
                    </Col>
                    <Col xs={24} sm={12} lg={6}>
                      <div 
                        className={darkMode ? 'summary-card-dark' : 'summary-card-light'}
                        style={{ 
                          textAlign: 'center', 
                          height: '100px',
                          borderRadius: '6px',
                          padding: '16px',
                          display: 'flex',
                          flexDirection: 'column',
                          justifyContent: 'center'
                        }}
                      >
                        <Text type="secondary" style={{ fontSize: '11px', color: darkMode ? '#d9d9d9 !important' : 'inherit' }}>Activity Scope</Text>
                        <div style={{ fontSize: '14px', fontWeight: '600', margin: '4px 0', color: darkMode ? '#ffffff !important' : 'inherit' }}>
                          {summaryStats.officesActive} offices
                        </div>
                        <div style={{ fontSize: '12px', margin: '2px 0', color: darkMode ? '#ffffff !important' : 'inherit' }}>
                          {summaryStats.periodsActive} periods
                        </div>
                        <Text type="secondary" style={{ fontSize: '10px', color: darkMode ? '#8c8c8c !important' : 'inherit' }}>
                          {logsData.length} yearly aggregations
                        </Text>
                      </div>
                    </Col>
                  </Row>

                  {/* Legend */}
                  <div style={{ 
                    marginBottom: '16px', 
                    padding: '12px 16px', 
                    backgroundColor: darkMode ? '#1f1f1f' : '#fafafa', 
                    borderRadius: '6px',
                    border: darkMode ? '1px solid #303030' : '1px solid #f0f0f0'
                  }}>
                    <Text strong style={{ marginRight: '24px' }}>Legend:</Text>
                    <span style={{ color: '#52c41a', fontWeight: '600', marginRight: '16px' }}>
                      +Recruited (new hires)
                    </span>
                    <span style={{ color: '#f5222d', fontWeight: '600', marginRight: '16px' }}>
                      -Churned (departures)
                    </span>
                    <span style={{ color: '#fa8c16', fontWeight: '600', marginRight: '16px' }}>
                      -Progressed Out (promotions away)
                    </span>
                    <span style={{ color: '#1890ff', fontWeight: '600', marginRight: '16px' }}>
                      +Progressed In (promotions received)
                    </span>
                    <Text type="secondary" style={{ fontSize: '12px', marginLeft: '16px' }}>
                      💡 Click on yearly totals to expand monthly breakdown
                    </Text>
                  </div>

                  {/* Logs Table with Expandable Rows */}
                  <Table
                    columns={logsColumns}
                    dataSource={logsData}
                    pagination={{ 
                      pageSize: 20, 
                      showSizeChanger: true, 
                      showQuickJumper: true,
                      showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} movements`
                    }}
                    size="small"
                    bordered
                    scroll={{ x: 1000 }}
                    style={{ marginBottom: '16px' }}
                    expandable={{
                      expandedRowRender: (record) => {
                        if (!record.monthlyData || record.monthlyData.length === 0) {
                          return (
                            <div style={{ padding: '16px', textAlign: 'center', color: '#8c8c8c' }}>
                              <Text type="secondary">No monthly breakdown available for this item</Text>
                            </div>
                          );
                        }
                        
                        return (
                          <div style={{ margin: '0', backgroundColor: darkMode ? '#0f0f0f' : '#fafafa' }}>
                            <div style={{ padding: '8px 16px', borderBottom: '1px solid #f0f0f0' }}>
                              <Text strong style={{ fontSize: '13px', color: '#1890ff' }}>
                                📅 Monthly Breakdown: {record.office} - {record.role} {record.level}
                              </Text>
                            </div>
                            <Table
                              columns={monthlyColumns}
                              dataSource={record.monthlyData}
                              pagination={false}
                              size="small"
                              showHeader={true}
                              bordered={false}
                              style={{ backgroundColor: 'transparent' }}
                            />
                          </div>
                        );
                      },
                      rowExpandable: (record) => record.monthlyData && record.monthlyData.length > 0,
                      expandIcon: ({ expanded, onExpand, record }) => (
                        record.monthlyData && record.monthlyData.length > 0 ? (
                          <span 
                            onClick={e => onExpand(record, e)}
                            style={{ 
                              cursor: 'pointer', 
                              marginRight: '8px',
                              color: '#1890ff',
                              fontSize: '12px'
                            }}
                          >
                            {expanded ? '📅' : '📊'}
                          </span>
                        ) : (
                          <span style={{ marginRight: '8px', color: '#d9d9d9', fontSize: '12px' }}>•</span>
                        )
                      ),
                    }}
                  />

                  {logsData.length === 0 && (
                    <div style={{ 
                      textAlign: 'center', 
                      padding: '40px', 
                      color: darkMode ? '#8c8c8c' : '#8c8c8c',
                      backgroundColor: darkMode ? '#1f1f1f' : '#fafafa',
                      borderRadius: '6px',
                      border: darkMode ? '1px solid #303030' : '1px solid #f0f0f0'
                    }}>
                      <Text type="secondary">
                        {selectedOfficeFilter 
                          ? `No movement activities recorded for ${selectedOfficeFilter} in Year ${activeYear}.`
                          : `No movement activities recorded for Year ${activeYear}.`
                        }
                        <br />
                        This could indicate stable headcount or no simulation data available.
                      </Text>
                    </div>
                  )}
                </div>
              );
            })()}
            </TabPane>
          <TabPane tab="Insights Tab" key="insights">
            {/* Year & Office Selectors (reuse existing logic) */}
            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col span={8}>
                <Text strong>Year:</Text> {activeYear}
              </Col>
              <Col span={8}>
                <Text strong>Office:</Text> All Offices {/* (Add office selector if needed) */}
              </Col>
            </Row>
            {/* KPI Cards Section */}
            <Row gutter={[16, 16]} style={{ marginBottom: 32 }}>
              {kpiData.map((kpi) => (
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
            {/* Workforce Charts */}
            <Card title="Workforce Charts" style={{ marginBottom: 32 }}>
              <Row gutter={24}>
                <Col xs={24} md={12}>
                  <WorkforcePyramidChart data={pyramidData} />
                </Col>
                <Col xs={24} md={12}>
                  <WorkforceStackedBarChart data={stackedBarData} />
                </Col>
              </Row>
              {/* Journey Distribution and Non-Debit Ratio Summary */}
              {seniorityKPIs && (
                <div style={{ marginTop: 24, textAlign: 'center', color: '#ccc', fontSize: 16 }}>
                  <div>
                    <b>Journey Distribution:</b>
                    {` ${seniorityKPIs.journey1Details?.percentage || 'N/A'} Journey 1 (A, AC, C)`}
                    {`, ${seniorityKPIs.journey2Details?.percentage || 'N/A'} Journey 2 (SrC, AM)`}
                    {`, ${seniorityKPIs.journey3Details?.percentage || 'N/A'} Journey 3 (M, SrM)`}
                    {`, ${seniorityKPIs.journey4Details?.percentage || 'N/A'} Journey 4 (PiP)`}
                  </div>
                  <div style={{ marginTop: 8 }}>
                    <b>Non-Debit Ratio:</b> {seniorityKPIs.nonDebitDetails?.percentage || 'N/A'}
                  </div>
                </div>
              )}
            </Card>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default SimulationLabV2; 