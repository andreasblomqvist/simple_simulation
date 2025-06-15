import React, { useState, useEffect } from 'react';
import { Form, InputNumber, Select, Button, Card, Row, Col, Typography, Table, Tag, Spin, message, Space, Checkbox } from 'antd';
import { useConfig } from '../components/ConfigContext';
import { TeamOutlined, PieChartOutlined, RiseOutlined, PercentageOutlined, UserOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;
const { Option } = Select;
const LEVELS = ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"];
const OFFICES = [
  'Stockholm', 'Munich', 'Hamburg', 'Helsinki', 'Oslo', 'Berlin',
  'Copenhagen', 'Zurich', 'Frankfurt', 'Cologne', 'Amsterdam',
  'Toronto', 'London'
];
const LEVERS = [
  { key: 'recruitment', label: 'Recruitment' },
  { key: 'churn', label: 'Churn' },
  { key: 'progression', label: 'Progression' },
  { key: 'utr', label: 'UTR' },
];
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
type LeversState = Record<string, Record<string, Record<string, number>>>;
const getDefaultLevers = (): LeversState => {
  const obj: LeversState = {};
  OFFICES.forEach(office => {
    obj[office] = {};
    LEVELS.forEach(level => {
      obj[office][level] = {};
      LEVERS.forEach(lv => {
        // Initialize monthly values (1-12)
        for (let month = 1; month <= 12; month++) {
          obj[office][level][`${lv.key}_${month}`] = 0.1;
        }
      });
    });
  });
  return obj;
};

// Example roles for each level
const ROLES = ['Consultant', 'Sales', 'Recruitment', 'Operations'];
const ROLES_WITH_LEVELS = ['Consultant', 'Sales', 'Recruitment'];

// Helper to calculate diffs and format lever changes
function getDiffString(current: number, baseline: number, percent = true) {
  const diff = current - baseline;
  if (diff === 0) return '';
  const sign = diff > 0 ? '+' : '';
  return percent ? ` (${sign}${(diff * 100).toFixed(0)}%)` : ` (${sign}${diff.toFixed(2)})`;
}

// Transform simulation results for expandable table
function transformResults(results: any, baseline: any) {
  // results: { offices: { [office]: { levels: { [role]: { [level]: [ ... ] } }, ... } } }
  const ROLES = ['Consultant', 'Sales', 'Recruitment'];
  const ROLES_WITH_LEVELS = ['Consultant', 'Sales', 'Recruitment'];
  const LEVELS = ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"];
  return Object.entries(results.offices).map(([officeName, officeData]: any) => {
    let rows: any[] = [];
    let officeCurrentTotal = 0;
    let officeBaselineTotal = 0;
    // Find the original config for this office
    const baselineOffice = Array.isArray(baseline) ? baseline.find((o: any) => o.name === officeName) : undefined;
    const baselineRoles = baselineOffice && baselineOffice.roles ? baselineOffice.roles : {};
    // Leveled roles
    ROLES_WITH_LEVELS.forEach((role: string) => {
      const simLevels = officeData.levels && officeData.levels[role] ? officeData.levels[role] : {};
      const baselineRole = baselineRoles[role] || {};
      let roleCurrentTotal = 0;
      let roleBaselineTotal = 0;
      const children = LEVELS.map((level: string) => {
        const simArray = simLevels[level]; // array of period objects
        const current = simArray && simArray.length > 0 ? simArray[simArray.length - 1] : {};
        const baselineLevel = baselineRole && baselineRole[level] ? baselineRole[level] : {};
        const baselineTotal = baselineLevel.total ?? 0;
        roleCurrentTotal += current.total ?? 0;
        roleBaselineTotal += baselineTotal;
        return {
          key: `${officeName}-${role}-${level}`,
          level,
          total: `${current.total !== undefined ? current.total : ''} (${baselineTotal !== undefined ? baselineTotal : ''})`,
          price: `${current.price !== undefined ? current.price.toFixed(2) : ''} (${baselineLevel.price_1 !== undefined ? Number(baselineLevel.price_1).toFixed(2) : ''})`,
          salary: `${current.salary !== undefined ? current.salary.toFixed(2) : ''} (${baselineLevel.salary_1 !== undefined ? Number(baselineLevel.salary_1).toFixed(2) : ''})`,
        };
      });
      officeCurrentTotal += roleCurrentTotal;
      officeBaselineTotal += roleBaselineTotal;
      rows.push({
        key: `${officeName}-${role}`,
        role,
        total: `${roleCurrentTotal !== undefined ? roleCurrentTotal : ''} (${roleBaselineTotal !== undefined ? roleBaselineTotal : ''})`,
        children,
      });
    });
    // Flat role: Operations
    if (officeData.operations && Array.isArray(officeData.operations)) {
      const simArray = officeData.operations;
      const current = simArray && simArray.length > 0 ? simArray[simArray.length - 1] : {};
      const baselineRole = baselineRoles['Operations'] || {};
      const baselineTotal = baselineRole.total ?? 0;
      officeCurrentTotal += current.total ?? 0;
      officeBaselineTotal += baselineTotal;
      rows.push({
        key: `${officeName}-Operations`,
        role: 'Operations',
        total: `${current.total !== undefined ? current.total : ''} (${baselineTotal !== undefined ? baselineTotal : ''})`,
        price: `${current.price !== undefined ? current.price.toFixed(2) : ''} (${baselineRole.price_1 !== undefined ? Number(baselineRole.price_1).toFixed(2) : ''})`,
        salary: `${current.salary !== undefined ? current.salary.toFixed(2) : ''} (${baselineRole.salary_1 !== undefined ? Number(baselineRole.salary_1).toFixed(2) : ''})`,
      });
    }
    return {
      key: officeName,
      office: officeName,
      journey: officeData.office_journey,
      total: `${officeCurrentTotal !== undefined ? officeCurrentTotal : ''} (${officeBaselineTotal !== undefined ? officeBaselineTotal : ''})`,
      children: rows,
    };
  });
}

// Move LEVER_KEYS above configColumns and getConfigTableData
const LEVER_KEYS = [
  { key: 'fte', label: 'FTE' },
  ...Array.from({ length: 12 }, (_, i) => [
    { key: `price_${i + 1}`, label: `Price ${i + 1}` },
    { key: `salary_${i + 1}`, label: `Salary ${i + 1}` },
    { key: `recruitment_${i + 1}`, label: `Recruitment ${i + 1}` },
    { key: `churn_${i + 1}`, label: `Churn ${i + 1}` },
    { key: `progression_${i + 1}`, label: `Progression ${i + 1}` },
    { key: `utr_${i + 1}`, label: `UTR ${i + 1}` },
  ]).flat(),
];

// Move configColumns definition after LEVER_KEYS
const configColumns: any[] = [
  {
    title: 'Role',
    dataIndex: 'role',
    key: 'role',
    render: (text: string, row: any) => (
      <span>{row.level ? '' : row.role}</span>
    ),
  },
  {
    title: 'Level',
    dataIndex: 'level',
    key: 'level',
    render: (text: string) => text || '-',
  },
  {
    title: 'Total FTE',
    dataIndex: 'fte',
    key: 'fte',
    render: (text: any, row: any) => {
      if (row.level) {
        return row.total ?? row.fte ?? 0;
      } else if (row.children && row.children.length > 0) {
        return row.children.reduce((sum: number, child: any) => sum + (child.total ?? child.fte ?? 0), 0);
      } else {
        return row.total ?? row.fte ?? 0;
      }
    },
  },
  // Show only key monthly values to avoid clutter
  { title: 'Price (Jan)', dataIndex: 'price_1', key: 'price_1', render: (val: any) => val !== undefined && val !== null && !isNaN(Number(val)) ? Number(val).toFixed(2) : '-' },
  { title: 'Salary (Jan)', dataIndex: 'salary_1', key: 'salary_1', render: (val: any) => val !== undefined && val !== null && !isNaN(Number(val)) ? Number(val).toFixed(2) : '-' },
  { title: 'Recruitment (Jan)', dataIndex: 'recruitment_1', key: 'recruitment_1', render: (val: any) => val !== undefined && val !== null ? val : '-' },
  { title: 'Churn (Jan)', dataIndex: 'churn_1', key: 'churn_1', render: (val: any) => val !== undefined && val !== null ? val : '-' },
  { title: 'Progression (May)', dataIndex: 'progression_5', key: 'progression_5', render: (val: any) => val !== undefined && val !== null ? val : '-' },
  { title: 'Progression (Nov)', dataIndex: 'progression_11', key: 'progression_11', render: (val: any) => val !== undefined && val !== null ? val : '-' },
  { title: 'UTR (Jan)', dataIndex: 'utr_1', key: 'utr_1', render: (val: any) => val !== undefined && val !== null ? val : '-' },
];

const getConfigTableData = (officeData: { roles?: { [key: string]: { [key: string]: any } } }): any[] => {
  if (!officeData || !officeData.roles) return [];
  let rows: any[] = [];
  ROLES.forEach((role: string) => {
    const roleData = officeData.roles![role] as Record<string, any>;
    if (roleData) {
      if (ROLES_WITH_LEVELS.includes(role)) {
        const children = LEVELS.map((level: string) => {
          const data = (roleData && Object.prototype.hasOwnProperty.call(roleData, level)) ? (roleData as Record<string, any>)[level] : {};
          const price = (data.price_1 !== undefined) ? Number(data.price_1).toFixed(2) : '-';
          const salary = (data.salary_1 !== undefined) ? Number(data.salary_1).toFixed(2) : '-';
          const levers: any = {};
          // Show key monthly values
          ['price_1', 'salary_1', 'recruitment_1', 'churn_1', 'progression_5', 'progression_11', 'utr_1'].forEach(key => {
            const v = data[key];
            levers[key] = v !== undefined && v !== null && !isNaN(Number(v)) ? Number(v).toFixed(2) : v ?? '-';
          });
          return {
            key: `${role}-${level}`,
            role,
            level,
            total: data.total ?? 0,
            price,
            salary,
            ...levers,
          };
        });
        // Compute averages for price and salary for parent row
        const validPrices = children.map(c => parseFloat((c.price || '').toString())).filter(n => !isNaN(n));
        const avgPrice = validPrices.length ? (validPrices.reduce((a, b) => a + b, 0) / validPrices.length) : null;
        const price = avgPrice !== null ? avgPrice.toFixed(2) : '-';
        const validSalaries = children.map(c => parseFloat((c.salary || '').toString())).filter(n => !isNaN(n));
        const avgSalary = validSalaries.length ? (validSalaries.reduce((a, b) => a + b, 0) / validSalaries.length) : null;
        const salary = avgSalary !== null ? avgSalary.toFixed(2) : '-';
        rows.push({
          key: role,
          role,
          price,
          salary,
          children,
        });
      } else {
        // Flat role (Operations)
        const data = (roleData as Record<string, any>) || {};
        const price = (data.price_1 !== undefined) ? Number(data.price_1).toFixed(2) : '-';
        const salary = (data.salary_1 !== undefined) ? Number(data.salary_1).toFixed(2) : '-';
        const levers: any = {};
        ['price_1', 'salary_1', 'recruitment_1', 'churn_1', 'progression_5', 'progression_11', 'utr_1'].forEach(key => {
          const v = data[key];
          levers[key] = v !== undefined && v !== null && !isNaN(Number(v)) ? Number(v).toFixed(2) : v ?? '-';
        });
        rows.push({
          key: role,
          role,
          price,
          salary,
          ...levers,
          total: data.total ?? 0,
        });
      }
    } else {
      // Role missing in backend, show as zero
      if (ROLES_WITH_LEVELS.includes(role)) {
        const children = LEVELS.map((level: string) => ({
          key: `${role}-${level}`,
          role,
          level,
          total: 0,
          price: '-',
          salary: '-',
          price_1: '-', salary_1: '-', recruitment_1: '-', churn_1: '-', progression_5: '-', progression_11: '-', utr_1: '-',
        }));
        rows.push({
          key: role,
          role,
          price: '-',
          salary: '-',
          children,
        });
      } else {
        rows.push({
          key: role,
          role,
          price: '-',
          salary: '-',
          price_1: '-', salary_1: '-', recruitment_1: '-', churn_1: '-', progression_5: '-', progression_11: '-', utr_1: '-',
          total: 0,
        });
      }
    }
  });
  return rows;
};

const levelColumns = [
  { title: 'Level', dataIndex: 'level', key: 'level' },
  { title: 'Total', dataIndex: 'total', key: 'total' },
  { title: 'Price (Jan)', dataIndex: 'price', key: 'price' },
  { title: 'Salary (Jan)', dataIndex: 'salary', key: 'salary' },
  { title: 'Recruitment (Jan)', dataIndex: 'recruitment', key: 'recruitment' },
  { title: 'Churn (Jan)', dataIndex: 'churn', key: 'churn' },
  { title: 'Progression (May)', dataIndex: 'progression', key: 'progression' },
  { title: 'UTR (Jan)', dataIndex: 'utr', key: 'utr' },
];

const roleColumns = [
  { title: 'Role', dataIndex: 'role', key: 'role' },
  { title: 'FTE', dataIndex: 'fte', key: 'fte' },
  { title: 'KPI', dataIndex: 'kpi', key: 'kpi' },
];

// Add helper to calculate financial KPIs
function calculateFinancialKPIs({
  offices,
  unplannedAbsence,
  hyWorkingHours,
  otherExpense,
  baseline = null
}: {
  offices: any,
  unplannedAbsence: number,
  hyWorkingHours: number,
  otherExpense: number,
  baseline?: any
}) {
  // Helper function to calculate KPIs for a given dataset
  const calculateKPIs = (officesData: any, isBaseline = false) => {
    let totalFTE = 0;
    let totalWeightedPrice = 0;
    let totalWeightedSalary = 0;
    
    if (isBaseline && Array.isArray(officesData)) {
      // Baseline is the original config format
      officesData.forEach((office: any) => {
        if (!office.roles) return;
        
        ['Consultant', 'Sales', 'Recruitment'].forEach(role => {
          const roleData = office.roles[role];
          if (!roleData) return;
          
          if (typeof roleData === 'object' && !Array.isArray(roleData)) {
            // Role with levels
            Object.entries(roleData).forEach(([level, data]: any) => {
              const fte = data.total ?? 0;
              const price = data.price_1 ?? 0;
              const salary = data.salary_1 ?? 0;
              
              totalFTE += fte;
              totalWeightedPrice += fte * price;
              totalWeightedSalary += fte * salary;
            });
          }
        });
      });
    } else {
      // Simulation results format
      Object.values(officesData).forEach((office: any) => {
        if (!office.levels) return;
        
        // Process all billable roles: Consultant, Sales, Recruitment
        ['Consultant', 'Sales', 'Recruitment'].forEach(role => {
          if (!office.levels[role]) return;
          
          Object.entries(office.levels[role]).forEach(([level, arr]: any) => {
            if (!Array.isArray(arr) || arr.length === 0) return;
            const last = arr[arr.length - 1];
            const fte = last.total ?? 0;
            const price = last.price ?? 0;
            const salary = last.salary ?? 0;
            
            totalFTE += fte;
            totalWeightedPrice += fte * price;
            totalWeightedSalary += fte * salary;
          });
        });
      });
    }
    
    // Calculate FTE-weighted averages
    const avgPrice = totalFTE > 0 ? totalWeightedPrice / totalFTE : 0;
    const avgSalary = totalFTE > 0 ? totalWeightedSalary / totalFTE : 0;
    
    // Use a default UTR since it's not returned in the simulation results
    const avgUTR = 0.85; // Default 85% utilization
    
    // Calculate time-based metrics (assuming hyWorkingHours is for the simulation period)
    const consultantTime = totalFTE * hyWorkingHours;
    const availableConsultantTime = consultantTime * (1 - unplannedAbsence);
    const invoicedTime = availableConsultantTime * avgUTR;
    
    // Calculate financials
    const netSales = invoicedTime * avgPrice;
    const totalSalaries = totalFTE * avgSalary * hyWorkingHours; // Salary cost for the period
    const ebitda = netSales - totalSalaries - otherExpense;
    const margin = netSales > 0 ? (ebitda / netSales) * 100 : 0;
    
    return {
      totalFTE,
      consultantTime,
      availableConsultantTime,
      invoicedTime,
      avgUTR,
      avgPrice,
      netSales,
      avgSalary,
      totalSalaries,
      otherExpense,
      ebitda,
      margin
    };
  };
  
  // Calculate current KPIs
  const current = calculateKPIs(offices);
  
  // Calculate baseline KPIs if provided
  let baselineKPIs = null;
  let deltas = null;
  
  if (baseline) {
    baselineKPIs = calculateKPIs(baseline, true);
    deltas = {
      netSales: current.netSales - baselineKPIs.netSales,
      ebitda: current.ebitda - baselineKPIs.ebitda,
      margin: current.margin - baselineKPIs.margin
    };
  }
  
  return {
    ...current,
    baseline: baselineKPIs,
    deltas
  };
}

export default function SimulationLab() {
  const [formVals, setFormVals] = useState({
    start_year: 2025,
    start_month: 1,
    end_year: 2026,
    end_month: 12,
    price_increase: 0.03,
    salary_increase: 0.03,
    unplanned_absence: 0.05,
    hy_working_hours: 998.4,
    other_expense: 100000,
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  // Lever manipulation state
  const [selectedLever, setSelectedLever] = useState('recruitment');
  const [selectedMonth, setSelectedMonth] = useState(1);
  const [selectedLevel, setSelectedLevel] = useState('AM');
  const [selectedOffices, setSelectedOffices] = useState([] as string[]);
  const [leverValue, setLeverValue] = useState(0.1);
  const { levers, setLevers } = useConfig();
  const [lastAppliedSummary, setLastAppliedSummary] = useState<string[] | null>(null);
  const [simulationResults, setSimulationResults] = useState<any>(null);
  const [baselineResults, setBaselineResults] = useState<any>(null);
  const [showConfig, setShowConfig] = useState(false);
  const [config, setConfig] = useState<any>(null);
  const [configOffices, setConfigOffices] = useState<any[]>([]);
  const [originalConfigOffices, setOriginalConfigOffices] = useState<any[]>([]);
  const [configLoading, setConfigLoading] = useState(false);
  const [showConfigTable, setShowConfigTable] = useState(false);
  const [selectedConfigOffice, setSelectedConfigOffice] = useState<string>('');
  // Add state for the checkbox
  const [applyToAllMonths, setApplyToAllMonths] = useState(false);

  // Fetch config on mount
  useEffect(() => {
    setConfigLoading(true);
    fetch('/api/offices')
      .then(res => res.json())
      .then(data => {
        setConfigOffices(data);
        setConfigLoading(false);
        // Only set originalConfigOffices if it is empty
        setOriginalConfigOffices(prev => (prev && prev.length > 0 ? prev : data));
      })
      .catch(() => setConfigLoading(false));
  }, []);

  // Update selectedConfigOffice when configOffices changes
  useEffect(() => {
    if (Array.isArray(configOffices) && configOffices.length > 0) {
      setSelectedConfigOffice(configOffices[0].name);
    }
  }, [configOffices]);

  const handleFormChange = (changed: any, all: any) => {
    setFormVals(all);
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const office_overrides: Record<string, { roles: any }> = {};
      Object.entries(levers).forEach(([office, levels]) => {
        office_overrides[office] = { roles: {} };
        // Roles with levels
        ROLES_WITH_LEVELS.forEach(role => {
          office_overrides[office].roles[role] = {};
          LEVELS.forEach(level => {
            if (levels[level]) {
              office_overrides[office].roles[role][level] = { ...levels[level] };
            }
          });
        });
        // Flat role (Operations)
        if (levels[ROLES[3]]) {
          office_overrides[office].roles[ROLES[3]] = { ...levels[ROLES[3]] };
        }
      });
      // Add debug logging
      console.log('[DEBUG] office_overrides payload:', JSON.stringify(office_overrides, null, 2));
      console.log('[DEBUG] Selected lever:', selectedLever);
      console.log('[DEBUG] Selected month:', selectedMonth);
      console.log('[DEBUG] Selected level:', selectedLevel);
      console.log('[DEBUG] Selected offices:', selectedOffices);
      console.log('[DEBUG] Lever value:', leverValue);
      
      const res = await fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formVals,
          start_year: Number(formVals.start_year),
          end_year: Number(formVals.end_year),
          price_increase: Number(formVals.price_increase),
          salary_increase: Number(formVals.salary_increase),
          office_overrides
        }),
      });
      if (!res.ok) throw new Error('Simulation failed');
      const data = await res.json();
      setResult(data);
      setSimulationResults(data);
      setBaselineResults(data);
      setConfig(data);
      setShowConfig(true);
    } catch (err: any) {
      setError(err.message);
      message.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Helper to extract the first and last period's data for each office
  const getOfficeKPIData = () => {
    if (!result || !result.offices) return [];
    const offices = result.offices;
    const periods = result.periods || [];
    const firstIdx = 0;
    const lastIdx = periods.length - 1;
    return Object.entries(offices).map(([officeName, officeData]: any) => {
      const levels = officeData.levels;
      const operations = officeData.operations;
      const metrics = officeData.metrics;
      
      // Get values for each level across all roles
      let totalFTEFirst = 0;
      let totalFTELast = 0;
      
      // Process roles with levels (Consultant, Sales, Recruitment)
      ROLES_WITH_LEVELS.forEach(role => {
        if (levels && levels[role]) {
          LEVELS.forEach(level => {
            if (levels[role][level] && Array.isArray(levels[role][level])) {
              const levelArray = levels[role][level];
              totalFTEFirst += levelArray[firstIdx]?.total ?? 0;
              totalFTELast += levelArray[lastIdx]?.total ?? 0;
            }
          });
        }
      });
      
      // Get operations
      const opsTotalFirst = operations?.[firstIdx]?.total ?? 0;
      const opsTotalLast = operations?.[lastIdx]?.total ?? 0;
      
      // Add operations to totals
      totalFTEFirst += opsTotalFirst;
      totalFTELast += opsTotalLast;
      
      // Get metrics
      const firstMetrics = metrics?.[firstIdx] || {};
      const lastMetrics = metrics?.[lastIdx] || {};
      
      // Calculate delta
      const delta = totalFTELast - totalFTEFirst;
      
      // Use office_journey if present, else fallback
      const journeyName = officeData.office_journey || '';
      
      return {
        name: officeName,
        journey: journeyName,
        total_fte: totalFTELast,
        delta,
        kpis: {
          growth: lastMetrics.growth ?? 0,
          recruitment: lastMetrics.recruitment ?? 0,
          churn: lastMetrics.churn ?? 0,
          non_debit_ratio: lastMetrics.non_debit_ratio ?? null,
        },
        original_journey: officeData.original_journey || '',
      };
    });
  };

  const officeKPIData = getOfficeKPIData();

  // Aggregate KPIs for cards
  const getAggregatedKPIs = () => {
    if (!result || !result.offices || !simulationResults) return null;
    const offices = result.offices;
    const periods = result.periods || [];
    const lastIdx = periods.length - 1;
    const prevIdx = periods.length - 2;
    
    // Aggregate journey totals
    const journeyTotals: { [key: string]: number } = { 'Journey 1': 0, 'Journey 2': 0, 'Journey 3': 0, 'Journey 4': 0 };
    let totalConsultants = 0;
    let totalNonConsultants = 0;
    let prevTotalConsultants = 0;
    let prevTotalNonConsultants = 0;
    
    Object.keys(journeyTotals).forEach(j => { journeyTotals[j] = 0; });
    
    Object.values(offices).forEach((officeData: any) => {
      // Sum journeys
      if (officeData.journeys) {
        Object.keys(journeyTotals).forEach(j => {
          const arr = officeData.journeys[j];
          if (arr && arr[lastIdx]) {
            journeyTotals[j] += arr[lastIdx].total || 0;
          }
        });
      }
      
      // For non-debit ratio: sum consultants vs non-consultants
      if (officeData.levels) {
        // Sum consultants only
        if (officeData.levels['Consultant']) {
          LEVELS.forEach(level => {
            const levelArray = officeData.levels['Consultant'][level];
            if (levelArray && levelArray[lastIdx]) {
              totalConsultants += levelArray[lastIdx].total || 0;
            }
            // Previous period for delta calculation
            if (levelArray && levelArray[prevIdx] && prevIdx >= 0) {
              prevTotalConsultants += levelArray[prevIdx].total || 0;
            }
          });
        }
        
        // Sum Sales and Recruitment (non-consultants)
        ['Sales', 'Recruitment'].forEach(role => {
          if (officeData.levels[role]) {
            LEVELS.forEach(level => {
              const levelArray = officeData.levels[role][level];
              if (levelArray && levelArray[lastIdx]) {
                totalNonConsultants += levelArray[lastIdx].total || 0;
              }
              // Previous period for delta calculation
              if (levelArray && levelArray[prevIdx] && prevIdx >= 0) {
                prevTotalNonConsultants += levelArray[prevIdx].total || 0;
              }
            });
          }
        });
      }
      
      // Sum operations (non-consultants)
      if (officeData.operations && officeData.operations[lastIdx]) {
        totalNonConsultants += officeData.operations[lastIdx].total || 0;
      }
      if (officeData.operations && officeData.operations[prevIdx] && prevIdx >= 0) {
        prevTotalNonConsultants += officeData.operations[prevIdx].total || 0;
      }
    });
    
    const totalJourney = Object.values(journeyTotals).reduce((a, b) => a + b, 0);
    const overallNonDebitRatio = totalNonConsultants > 0 ? (totalConsultants / totalNonConsultants) : null;
    
    // Calculate delta for non-debit ratio
    let nonDebitDelta = null;
    if (prevIdx >= 0 && prevTotalNonConsultants > 0) {
      const prevNonDebitRatio = prevTotalConsultants / prevTotalNonConsultants;
      if (overallNonDebitRatio !== null) {
        nonDebitDelta = overallNonDebitRatio - prevNonDebitRatio;
      }
    }
    
    return { 
      journeyTotals, 
      totalJourney, 
      overallNonDebitRatio, 
      totalConsultants, 
      totalNonConsultants, 
      nonDebitDelta 
    };
  };

  const aggregatedKPIs = getAggregatedKPIs();

  // Table columns for office KPIs
  const columns = [
    {
      title: 'Office',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <Text strong>{text}</Text>,
    },
    {
      title: 'Journey',
      dataIndex: 'journey',
      key: 'journey',
      render: (journey: string) => <Tag>{journey}</Tag>,
    },
    {
      title: 'Total FTE',
      dataIndex: 'total_fte',
      key: 'total_fte',
    },
    {
      title: 'Delta',
      dataIndex: 'delta',
      key: 'delta',
      render: (delta: number) => <span style={{ color: delta > 0 ? '#52c41a' : delta < 0 ? '#ff4d4f' : '#bfbfbf' }}>{delta > 0 ? '+' : ''}{delta}</span>,
    },
    {
      title: 'Growth %',
      key: 'growth',
      render: (value: any, row: any) => (value !== undefined && value !== null && !isNaN(value)) ? value : '-'
    },
    {
      title: 'Non-Debit Ratio',
      key: 'ndr',
      render: (value: any, row: any) => (value !== undefined && value !== null && !isNaN(value)) ? value : '-'
    },
  ];

  const handleApply = () => {
    if (selectedOffices.length === 0) {
      message.warning('Please select at least one office.');
      return;
    }
    // Build the updated levers object first
    const updatedLevers = { ...levers };
    selectedOffices.forEach(office => {
      updatedLevers[office] = { ...updatedLevers[office] };
      updatedLevers[office][selectedLevel] = { ...updatedLevers[office][selectedLevel] };
      if (applyToAllMonths) {
        ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'].forEach(month => {
          updatedLevers[office][selectedLevel][`${selectedLever}_${month}`] = leverValue;
        });
      } else {
        updatedLevers[office][selectedLevel][`${selectedLever}_${selectedMonth}`] = leverValue;
      }
    });
    setLevers(updatedLevers);

    // Build summary array of all applied levers for selected offices
    const defaultValue = 0.1;
    const leverSummaries: string[] = [];
    selectedOffices.forEach(office => {
      if (!updatedLevers[office]) return;
      Object.entries(updatedLevers[office]).forEach(([level, leverObj]) => {
        Object.entries(leverObj as Record<string, number>).forEach(([leverMonth, value]) => {
          if ((value as number) !== defaultValue) {
            const [leverKey, month] = leverMonth.split('_');
            const leverLabel = LEVERS.find(l => l.key === leverKey)?.label || leverKey;
            const percent = `${((value as number) * 100).toFixed(0)}%`;
            leverSummaries.push(`${leverLabel} for level ${level} (${month}) set to ${percent} for ${office}`);
          }
        });
      });
    });
    if (leverSummaries.length > 0) {
      setLastAppliedSummary(leverSummaries);
    } else {
      setLastAppliedSummary(['No levers applied.']);
    }
  };

  const handleReset = () => {
    // Reset levers to default values
    setLevers(getDefaultLevers());
    // Clear ALL simulation results and state
    setSimulationResults(null);
    setBaselineResults(null);
    setResult(null);
    setConfig(null);
    setShowConfig(false);
    // Clear applied summary
    setLastAppliedSummary(null);
    // Reset form to default values
    setFormVals({
      start_year: 2025,
      start_month: 1,
      end_year: 2026,
      end_month: 12,
      price_increase: 0.03,
      salary_increase: 0.03,
      unplanned_absence: 0.05,
      hy_working_hours: 998.4,
      other_expense: 100000,
    });
    // Show success message
    message.success('Simulation reset to original configuration');
  };

  // Add debug log before transforming results
  if (simulationResults) {
    // eslint-disable-next-line no-console
    console.log('[DEBUG] Raw simulationResults:', simulationResults);
    // eslint-disable-next-line no-console
    console.log('[DEBUG] simulationResults.offices:', simulationResults.offices);
    // eslint-disable-next-line no-console
    console.log('[DEBUG] originalConfigOffices:', originalConfigOffices);
  }

  // In the render, use the first office in configOffices for the config table
  const selectedOfficeData = Array.isArray(configOffices) && configOffices.length > 0
    ? configOffices.find((o: any) => o.name === selectedConfigOffice)
    : null;

  // After simulationResults are set, calculate KPIs
  const financialKPIs = simulationResults && formVals && originalConfigOffices && originalConfigOffices.length > 0 ? calculateFinancialKPIs({
    offices: simulationResults.offices,
    unplannedAbsence: formVals.unplanned_absence,
    hyWorkingHours: formVals.hy_working_hours,
    otherExpense: formVals.other_expense,
    baseline: originalConfigOffices
  }) : null;

  return (
    <Card title={<Title level={4} style={{ margin: 0 }}>Simulation Lab</Title>}>
      {/* Lever Manipulation Panel - always at the top */}
      <Row gutter={16} align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <span>Lever: </span>
          <Select value={selectedLever} onChange={setSelectedLever} style={{ width: 130 }}>
            {LEVERS.map(l => <Option key={l.key} value={l.key}>{l.label}</Option>)}
          </Select>
        </Col>
        <Col>
          <span>Month: </span>
          <Select value={selectedMonth} onChange={setSelectedMonth} style={{ width: 120 }}>
            {MONTHS.map(m => <Option key={m.value} value={m.value}>{m.value}</Option>)}
          </Select>
        </Col>
        <Col>
          <span>Level: </span>
          <Select value={selectedLevel} onChange={setSelectedLevel} style={{ width: 90 }}>
            {LEVELS.map(lv => <Option key={lv} value={lv}>{lv}</Option>)}
          </Select>
        </Col>
        <Col>
          <span>Offices: </span>
          <Select
            mode="multiple"
            value={selectedOffices}
            onChange={setSelectedOffices}
            style={{ minWidth: 200 }}
            placeholder="Select offices"
          >
            {OFFICES.map(ofc => <Option key={ofc} value={ofc}>{ofc}</Option>)}
          </Select>
        </Col>
        <Col>
          <span>Value: </span>
          <InputNumber
            min={0}
            max={selectedLever === 'utr' ? 1 : 1}
            step={0.01}
            value={leverValue}
            onChange={v => setLeverValue(v ?? 0)}
            style={{ width: 90 }}
          />
        </Col>
        <Col>
          <Checkbox
            checked={applyToAllMonths}
            onChange={e => setApplyToAllMonths(e.target.checked)}
          >
            Apply to all months
          </Checkbox>
        </Col>
        <Col>
          <Button type="primary" onClick={handleApply}>Apply</Button>
        </Col>
      </Row>
      {lastAppliedSummary && (
        <div style={{ marginBottom: 16, fontWeight: 500, color: '#096dd9' }}>
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            {lastAppliedSummary.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Simulation Form and rest of the content follows */}
      <Form
        layout="vertical"
        initialValues={formVals}
        onValuesChange={handleFormChange}
        onFinish={handleSubmit}
        style={{ marginBottom: 32 }}
      >
        <Row gutter={16}>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Form.Item label="Start Year" name="start_year" rules={[{ required: true }]}> 
              <InputNumber min={2000} max={2100} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Form.Item label="Start Month" name="start_month" rules={[{ required: true }]}> 
              <Select>
                {MONTHS.map(m => <Option key={m.value} value={m.value}>{m.label}</Option>)}
              </Select>
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Form.Item label="End Year" name="end_year" rules={[{ required: true }]}> 
              <InputNumber min={2000} max={2100} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Form.Item label="End Month" name="end_month" rules={[{ required: true }]}> 
              <Select>
                {MONTHS.map(m => <Option key={m.value} value={m.value}>{m.label}</Option>)}
              </Select>
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Form.Item label="Price Increase (%)" name="price_increase" rules={[{ required: true }]}> 
              <InputNumber min={0} max={1} step={0.01} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Form.Item label="Salary Increase (%)" name="salary_increase" rules={[{ required: true }]}> 
              <InputNumber min={0} max={1} step={0.01} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Form.Item label="Unplanned Absence (%)" name="unplanned_absence" rules={[{ required: true }]}> 
              <InputNumber min={0} max={1} step={0.01} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Form.Item label="HY Working Hours" name="hy_working_hours" rules={[{ required: true }]}> 
              <InputNumber min={0} max={2000} step={0.1} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Form.Item label="Other Expense" name="other_expense" rules={[{ required: true }]}> 
              <InputNumber min={0} step={100} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
        </Row>
        {/* Toggle buttons moved here */}
        <div style={{ marginBottom: 16 }}>
          <Space>
            <Button
              type={showConfigTable ? 'primary' : 'default'}
              onClick={() => setShowConfigTable(true)}
            >
              Show Current Config
            </Button>
            <Button
              type={!showConfigTable ? 'primary' : 'default'}
              onClick={() => setShowConfigTable(false)}
            >
              Show Simulation Results
            </Button>
          </Space>
        </div>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} style={{ marginRight: 8 }}>
            {loading ? 'Running...' : 'Run Simulation'}
          </Button>
          <Button onClick={handleReset}>Reset to Config</Button>
        </Form.Item>
        {error && <Text type="danger">{error}</Text>}
      </Form>

      {/* KPI Cards - Modern Dashboard Style (now after the form, before the table) */}
      {aggregatedKPIs && (
        <Row gutter={[24, 24]} style={{ marginBottom: 32 }}>
          {Object.entries(aggregatedKPIs.journeyTotals).map(([journey, value]) => {
            // Calculate percentage and delta
            const percent = aggregatedKPIs.totalJourney > 0 ? ((value / aggregatedKPIs.totalJourney) * 100) : 0;
            // Find delta: percentage change from previous period (if available)
            let delta = null;
            if (result && result.offices) {
              const offices = result.offices;
              const periods = result.periods || [];
              const currentIdx = periods.length - 1;
              const prevIdx = periods.length - 2;
              
              if (prevIdx >= 0 && currentIdx >= 0) {
                let currentTotal = 0;
                let prevTotal = 0;
                
                Object.values(offices).forEach((officeData: any) => {
                  if (officeData.journeys && officeData.journeys[journey]) {
                    const journeyArray = officeData.journeys[journey];
                    if (journeyArray && Array.isArray(journeyArray)) {
                      // Current period total
                      if (journeyArray[currentIdx]) {
                        currentTotal += journeyArray[currentIdx].total || 0;
                      }
                      // Previous period total
                      if (journeyArray[prevIdx]) {
                        prevTotal += journeyArray[prevIdx].total || 0;
                      }
                    }
                  }
                });
                
                // Calculate delta
                if (prevTotal > 0) {
                  delta = ((currentTotal - prevTotal) / prevTotal) * 100;
                } else if (currentTotal > 0) {
                  delta = 100; // 100% increase from 0
                } else {
                  delta = 0; // Both are 0
                }
                
                // Debug logging
                console.log(`[DEBUG] Journey ${journey}: Current=${currentTotal}, Previous=${prevTotal}, Delta=${delta}%`);
              }
            }
            
            let deltaColor = '#bfbfbf';
            if (delta !== null) {
              if (delta > 0) deltaColor = '#52c41a';
              else if (delta < 0) deltaColor = '#ff4d4f';
            }
            return (
              <Col xs={24} sm={12} md={6} key={journey}>
                <Card
                  bordered={false}
                  style={{
                    background: '#1f1f1f',
                    color: '#fff',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.45)',
                    borderRadius: 12,
                    minHeight: 80,
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center',
                    alignItems: 'flex-start',
                    padding: 16,
                  }}
                >
                  <div style={{ fontSize: 32, fontWeight: 700, marginBottom: 2, color: '#40a9ff' }}>{percent.toFixed(1)}%</div>
                  <div style={{ fontSize: 22, fontWeight: 600, marginBottom: 2 }}>{value}</div>
                  {delta !== null && Math.abs(delta) > 0.01 && (
                    <div style={{ fontSize: 18, fontWeight: 500, color: deltaColor }}>
                      Δ {delta > 0 ? '+' : ''}{delta.toFixed(1)}%
                    </div>
                  )}
                  <div style={{ fontSize: 16, fontWeight: 400, marginTop: 4, color: '#aaa' }}>{journey}</div>
                </Card>
              </Col>
            );
          })}
          {/* Non-Debit Ratio card in the same row */}
          <Col xs={24} sm={12} md={6} key="non-debit-ratio">
            <Card
              bordered={false}
              style={{
                background: '#1f1f1f',
                color: '#fff',
                boxShadow: '0 2px 8px rgba(0,0,0,0.45)',
                borderRadius: 12,
                minHeight: 80,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'flex-start',
                padding: 16,
              }}
              bodyStyle={{ padding: 0 }}
            >
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: 4 }}>
                <PercentageOutlined style={{ fontSize: 20, color: '#ffa940', marginRight: 8 }} />
                <div>
                  <Text style={{ color: '#bfbfbf', fontSize: 12 }}>Non-Debit Ratio</Text>
                  <div style={{ fontWeight: 700, fontSize: 22, color: '#fff', lineHeight: 1 }}>
                    {aggregatedKPIs.overallNonDebitRatio !== null ? aggregatedKPIs.overallNonDebitRatio.toFixed(2) : 'N/A'}
                  </div>
                  {/* Show absolute numbers */}
                  <div style={{ fontSize: 11, color: '#aaa', marginTop: 2 }}>
                    Consultants: {aggregatedKPIs.totalConsultants || 0}
                  </div>
                  <div style={{ fontSize: 11, color: '#aaa' }}>
                    Sales+Rec+Ops: {aggregatedKPIs.totalNonConsultants || 0}
                  </div>
                  {/* Show delta if available */}
                  {aggregatedKPIs.nonDebitDelta !== null && Math.abs(aggregatedKPIs.nonDebitDelta) > 0.01 && (
                    <div style={{ fontSize: 11, fontWeight: 500, color: aggregatedKPIs.nonDebitDelta > 0 ? '#52c41a' : '#ff4d4f', marginTop: 2 }}>
                      Δ {aggregatedKPIs.nonDebitDelta > 0 ? '+' : ''}{aggregatedKPIs.nonDebitDelta.toFixed(2)}
                    </div>
                  )}
                </div>
              </div>
            </Card>
          </Col>
          {/* Financial KPIs */}
          {financialKPIs && (
            <>
              <Col xs={24} sm={12} md={6} key="net-sales">
                <Card bordered={false} style={{background: '#1f1f1f', color: '#fff', borderRadius: 12, minHeight: 80, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'flex-start', padding: 16}}>
                  <div style={{ fontSize: 12, color: '#bfbfbf' }}>Net Sales</div>
                  <div style={{ fontWeight: 700, fontSize: 22, color: '#fff' }}>{financialKPIs.netSales.toLocaleString(undefined, { maximumFractionDigits: 0 })}</div>
                  {financialKPIs.baseline && (
                    <div style={{ fontSize: 11, color: '#aaa', marginTop: 2 }}>
                      Baseline: {financialKPIs.baseline.netSales.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </div>
                  )}
                  {financialKPIs.deltas && Math.abs(financialKPIs.deltas.netSales) > 1 && (
                    <div style={{ fontSize: 11, fontWeight: 500, color: financialKPIs.deltas.netSales > 0 ? '#52c41a' : '#ff4d4f', marginTop: 2 }}>
                      Δ {financialKPIs.deltas.netSales > 0 ? '+' : ''}{financialKPIs.deltas.netSales.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </div>
                  )}
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6} key="ebitda">
                <Card bordered={false} style={{background: '#1f1f1f', color: '#fff', borderRadius: 12, minHeight: 80, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'flex-start', padding: 16}}>
                  <div style={{ fontSize: 12, color: '#bfbfbf' }}>EBITDA</div>
                  <div style={{ fontWeight: 700, fontSize: 22, color: '#fff' }}>{financialKPIs.ebitda.toLocaleString(undefined, { maximumFractionDigits: 0 })}</div>
                  {financialKPIs.baseline && (
                    <div style={{ fontSize: 11, color: '#aaa', marginTop: 2 }}>
                      Baseline: {financialKPIs.baseline.ebitda.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </div>
                  )}
                  {financialKPIs.deltas && Math.abs(financialKPIs.deltas.ebitda) > 1 && (
                    <div style={{ fontSize: 11, fontWeight: 500, color: financialKPIs.deltas.ebitda > 0 ? '#52c41a' : '#ff4d4f', marginTop: 2 }}>
                      Δ {financialKPIs.deltas.ebitda > 0 ? '+' : ''}{financialKPIs.deltas.ebitda.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </div>
                  )}
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6} key="margin">
                <Card bordered={false} style={{background: '#1f1f1f', color: '#fff', borderRadius: 12, minHeight: 80, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'flex-start', padding: 16}}>
                  <div style={{ fontSize: 12, color: '#bfbfbf' }}>Margin</div>
                  <div style={{ fontWeight: 700, fontSize: 22, color: '#fff' }}>
                    {financialKPIs.margin.toFixed(1)}%
                  </div>
                  {financialKPIs.baseline && (
                    <div style={{ fontSize: 11, color: '#aaa', marginTop: 2 }}>
                      Baseline: {financialKPIs.baseline.margin.toFixed(1)}%
                    </div>
                  )}
                  {financialKPIs.deltas && Math.abs(financialKPIs.deltas.margin) > 0.1 && (
                    <div style={{ fontSize: 11, fontWeight: 500, color: financialKPIs.deltas.margin > 0 ? '#52c41a' : '#ff4d4f', marginTop: 2 }}>
                      Δ {financialKPIs.deltas.margin > 0 ? '+' : ''}{financialKPIs.deltas.margin.toFixed(1)}%
                    </div>
                  )}
                </Card>
              </Col>
            </>
          )}
        </Row>
      )}

      {/* Table Section - after KPI cards */}
      <div style={{ marginBottom: 24 }}>
        {showConfigTable ? (
          <>
            <Row align="middle" gutter={16} style={{ marginBottom: 16 }}>
              <Col>
                <Select
                  value={selectedConfigOffice}
                  onChange={setSelectedConfigOffice}
                  style={{ width: 200 }}
                  options={configOffices.map((office: any) => ({ label: office.name, value: office.name }))}
                />
              </Col>
            </Row>
            <Table
              columns={configColumns}
              dataSource={getConfigTableData(selectedOfficeData)}
              rowKey={row => row.key}
              loading={configLoading}
              pagination={false}
              expandable={{
                childrenColumnName: 'children',
                defaultExpandAllRows: true,
              }}
            />
          </>
        ) :
          <Table
            columns={[
              {
                title: 'Office / Level / Role',
                key: 'name',
                render: (text, record) => {
                  if ('office' in record && record.office && typeof record.office === 'string') return <span style={{ fontWeight: 600 }}>{record.office}</span>;
                  if ('role' in record && record.role && typeof record.role === 'string') return <span style={{ marginLeft: 24 }}>{record.role}</span>;
                  if ('level' in record && record.level && typeof record.level === 'string') return <span style={{ marginLeft: 48 }}>{record.level}</span>;
                  return null;
                },
              },
              {
                title: 'Journey',
                dataIndex: 'journey',
                key: 'journey',
                render: (text) => text || null,
              },
              {
                title: 'FTE',
                dataIndex: 'total',
                key: 'total',
                render: (text) => {
                  if (typeof text !== 'string') return null;
                  const match = text.match(/^([\d.]+) \(([^)]+)\)$/);
                  if (!match) return text;
                  const current = parseFloat(match[1]);
                  const baseline = parseFloat(match[2]);
                  let color = undefined;
                  if (current > baseline) color = 'green';
                  else if (current < baseline) color = 'red';
                  return <span style={{ color }}>{text}</span>;
                },
              },
              {
                title: 'Delta',
                key: 'delta',
                render: (text, record) => {
                  // Use the FTE value for delta calculation
                  const fteText = record.total;
                  if (typeof fteText !== 'string') return null;
                  const match = fteText.match(/^([\d.]+) \(([^)]+)\)$/);
                  if (!match) return null;
                  const current = parseFloat(match[1]);
                  const baseline = parseFloat(match[2]);
                  const delta = current - baseline;
                  let color = undefined;
                  if (delta > 0) color = 'green';
                  else if (delta < 0) color = 'red';
                  if (delta === 0) return null;
                  return <span style={{ color }}>{delta > 0 ? '+' : ''}{delta}</span>;
                },
              },
              {
                title: 'Price',
                dataIndex: 'price',
                key: 'price',
                render: (text) => {
                  if (typeof text !== 'string') return null;
                  const match = text.match(/^([\d.]+) \(([^)]+)\)$/);
                  if (!match) return text;
                  const current = parseFloat(match[1]);
                  const baseline = parseFloat(match[2]);
                  let color = undefined;
                  if (current > baseline) color = 'green';
                  else if (current < baseline) color = 'red';
                  return <span style={{ color }}>{text}</span>;
                },
              },
              {
                title: 'Salary',
                dataIndex: 'salary',
                key: 'salary',
                render: (text) => {
                  if (typeof text !== 'string') return null;
                  const match = text.match(/^([\d.]+) \(([^)]+)\)$/);
                  if (!match) return text;
                  const current = parseFloat(match[1]);
                  const baseline = parseFloat(match[2]);
                  let color = undefined;
                  if (current > baseline) color = 'green';
                  else if (current < baseline) color = 'red';
                  return <span style={{ color }}>{text}</span>;
                },
              },
            ]}
            dataSource={simulationResults ? transformResults(simulationResults, originalConfigOffices) : []}
            rowKey="key"
            pagination={false}
            expandable={{
              defaultExpandAllRows: false,
            }}
          />
        }
      </div>

      {/* Configuration card at the bottom */}
      {showConfig && config && (
        <Card title="Configuration" style={{ marginBottom: 16 }}>
          <pre style={{ 
            background: '#1f1f1f', 
            padding: 16, 
            borderRadius: 8,
            color: '#fff',
            fontSize: 14,
            maxHeight: '400px',
            overflow: 'auto'
          }}>
            {JSON.stringify(config, (key, value) => 
              typeof value === 'number' ? Number(value.toFixed(2)) : value
            , 2)}
          </pre>
        </Card>
      )}
    </Card>
  );
} 