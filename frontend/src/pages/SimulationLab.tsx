import React, { useState, useEffect } from 'react';
import { Form, InputNumber, Select, Button, Card, Row, Col, Typography, Table, Tag, Spin, message, Space, Checkbox, Tabs } from 'antd';
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
type LeversState = Record<string, Record<string, Record<string, number>>>;
const getDefaultLevers = (): LeversState => {
  const obj: LeversState = {};
  OFFICES.forEach(office => {
    obj[office] = {};
    LEVELS.forEach(level => {
      obj[office][level] = {};
      LEVERS.forEach(lv => {
        // Initialize monthly values (1-12) with realistic defaults
        for (let month = 1; month <= 12; month++) {
                  // Use realistic sustainable rates as defaults
        if (lv.key === 'recruitment') {
          obj[office][level][`${lv.key}_${month}`] = level === 'A' ? 0.025 : 0.015; // 2.5% for A level, 1.5% for others
        } else if (lv.key === 'churn') {
          obj[office][level][`${lv.key}_${month}`] = 0.014; // 1.4% historical churn
        } else if (lv.key === 'progression') {
          obj[office][level][`${lv.key}_${month}`] = month === 5 || month === 11 ? 0.08 : 0.0; // 8% in May/Nov only
        } else {
          obj[office][level][`${lv.key}_${month}`] = 0.9; // UTR default
        }
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
      const current = simArray && simArray.length > 0 ? simArray[simArray.length - 1] : null;
      const baselineRole = baselineRoles['Operations'] || {};
      const baselineTotal = baselineRole.total ?? 0;
      
      // Handle null operations data (offices without operations)
      if (current && current !== null) {
        officeCurrentTotal += current.total ?? 0;
        officeBaselineTotal += baselineTotal;
        rows.push({
          key: `${officeName}-Operations`,
          role: 'Operations',
          total: `${current.total !== undefined ? current.total : ''} (${baselineTotal !== undefined ? baselineTotal : ''})`,
          price: `${current.price !== undefined ? current.price.toFixed(2) : ''} (${baselineRole.price_1 !== undefined ? Number(baselineRole.price_1).toFixed(2) : ''})`,
          salary: `${current.salary !== undefined ? current.salary.toFixed(2) : ''} (${baselineRole.salary_1 !== undefined ? Number(baselineRole.salary_1).toFixed(2) : ''})`,
        });
      } else {
        // Office has no operations data
        officeBaselineTotal += baselineTotal;
        rows.push({
          key: `${officeName}-Operations`,
          role: 'Operations',
          total: `0 (${baselineTotal !== undefined ? baselineTotal : ''})`,
          price: `- (${baselineRole.price_1 !== undefined ? Number(baselineRole.price_1).toFixed(2) : ''})`,
          salary: `- (${baselineRole.salary_1 !== undefined ? Number(baselineRole.salary_1).toFixed(2) : ''})`,
        });
      }
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

// DEPRECATED: Financial KPIs are now calculated in the backend via KPI service
// This function is kept for backward compatibility but is no longer used
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
        
        // Only consultants generate revenue (billable to clients)
        const consultantRole = office.roles && office.roles['Consultant'];
        if (consultantRole && typeof consultantRole === 'object' && !Array.isArray(consultantRole)) {
          Object.entries(consultantRole).forEach(([level, data]: any) => {
            if (!data) return;
            const fte = data.total ?? 0;
            const price = data.price_1 ?? 0; // This is hourly rate
            
            totalFTE += fte;
            totalWeightedPrice += fte * price;
          });
        }
        
        // Include all roles for salary costs (consultants, sales, recruitment, operations)
        ['Consultant', 'Sales', 'Recruitment'].forEach(role => {
          const roleData = office.roles && office.roles[role];
          if (!roleData) return;
          
          if (typeof roleData === 'object' && !Array.isArray(roleData)) {
            // Role with levels
            Object.entries(roleData).forEach(([level, data]: any) => {
              if (!data) return;
              const fte = data.total ?? 0;
              const salary = data.salary_1 ?? 0;
              
              totalWeightedSalary += fte * salary;
            });
          }
        });
        
        // Include operations in salary costs
        const operationsRole = office.roles['Operations'];
        if (operationsRole && typeof operationsRole === 'object') {
          const opsFTE = operationsRole.total ?? 0;
          const opsSalary = operationsRole.salary_1 ?? 0;
          totalWeightedSalary += opsFTE * opsSalary;
        }
      });
    } else {
      // Simulation results format
      Object.values(officesData).forEach((office: any) => {
        if (!office.levels) return;
        
        // Only consultants generate revenue (billable to clients)
        // Sales, Recruitment, and Operations are cost centers
        if (office.levels && office.levels['Consultant']) {
          Object.entries(office.levels['Consultant']).forEach(([level, arr]: any) => {
            if (!Array.isArray(arr) || arr.length === 0) return;
            const last = arr[arr.length - 1];
            if (!last) return;
            const fte = last.total ?? 0;
            const price = last.price ?? 0; // This is hourly rate
            
            totalFTE += fte;
            totalWeightedPrice += fte * price;
          });
        }
        
        // Include all roles for salary costs (consultants, sales, recruitment, operations)
        ['Consultant', 'Sales', 'Recruitment'].forEach(role => {
          if (!office.levels || !office.levels[role]) return;
          
          Object.entries(office.levels[role]).forEach(([level, arr]: any) => {
            if (!Array.isArray(arr) || arr.length === 0) return;
            const last = arr[arr.length - 1];
            if (!last) return;
            const fte = last.total ?? 0;
            const salary = last.salary ?? 0;
            
            totalWeightedSalary += fte * salary;
          });
        });
        
        // Include operations in salary costs
        if (office.operations && Array.isArray(office.operations) && office.operations.length > 0) {
          const lastOps = office.operations[office.operations.length - 1];
          if (lastOps) {
            const opsFTE = lastOps.total ?? 0;
            const opsSalary = lastOps.salary ?? 0;
            totalWeightedSalary += opsFTE * opsSalary;
          }
        }
      });
    }
    
    // Calculate consultant-weighted average price (only consultants generate revenue)
    const avgPrice = totalFTE > 0 ? totalWeightedPrice / totalFTE : 0;
    
    // FIXED: Handle baseline vs simulation calculation differently
    let simulationMonths;
    let workingHoursForCalculation;
    
    if (isBaseline) {
      // For baseline: use monthly data (166.4 hours per month, 1 month)
      simulationMonths = 1;
      workingHoursForCalculation = 166.4; // Monthly working hours
    } else {
      // For simulation: use total hours for entire simulation period
      simulationMonths = hyWorkingHours / 166.4; // hyWorkingHours is total hours, 166.4 is monthly hours
      workingHoursForCalculation = hyWorkingHours;
    }
    
    const totalMonthlySalaryCosts = totalWeightedSalary;
    
    // Add social costs (Swedish employer costs: ~25% social security + benefits)
    const socialCostMultiplier = 1.25; // 25% on top of salary for social costs, benefits, etc.
    const totalSalaryCosts = totalMonthlySalaryCosts * simulationMonths * socialCostMultiplier;
    
    // Use the UTR from simulation data if available, otherwise default
    const avgUTR = 0.85; // Use the UTR provided in the simulation data
    
    // Calculate time-based metrics for consultants only (revenue generators)
    const consultantTime = totalFTE * workingHoursForCalculation; // Only consultant FTE for revenue
    const availableConsultantTime = consultantTime * (1 - unplannedAbsence);
    const invoicedTime = availableConsultantTime * avgUTR;
    
    // Calculate financials
    // Revenue: Only from consultants (hourly rate * hours * UTR)
    const netSales = invoicedTime * avgPrice;
    // Costs: All roles (consultants, sales, recruitment, operations) + social costs
    const totalSalaries = totalSalaryCosts;
    const ebitda = netSales - totalSalaries - otherExpense;
    const margin = netSales > 0 ? (ebitda / netSales) * 100 : 0;
    
    // Debug logging
    console.log(`[DEBUG] Financial calculation (${isBaseline ? 'BASELINE' : 'CURRENT'}):`, {
      totalFTE,
      avgPrice,
      avgUTR,
      workingHoursForCalculation,
      simulationMonths,
      totalMonthlySalaryCosts,
      socialCostMultiplier,
      totalSalaryCosts,
      consultantTime,
      availableConsultantTime,
      invoicedTime,
      netSales,
      totalSalaries,
      otherExpense,
      ebitda,
      margin
    });
    
    return {
      totalFTE,
      consultantTime,
      availableConsultantTime,
      invoicedTime,
      avgUTR,
      avgPrice,
      netSales,
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

// Add helper to compute monthly rate from cumulative probability
function getMonthlyRateFromCumulative(cumulative: number, months: number) {
  if (cumulative >= 1) cumulative = 0.9999;
  if (cumulative <= 0) return 0;
  return 1 - Math.pow(1 - cumulative, 1 / months);
}

export default function SimulationLab() {
  const [formVals, setFormVals] = useState({
    duration_value: 24, // Duration amount
    duration_unit: 'months', // 'months' or 'years'
    price_increase: 3.0, // 3% as percentage
    salary_increase: 3.0, // 3% as percentage
    unplanned_absence: 5.0, // 5% as percentage
    hy_working_hours: 166.4, // Monthly working hours
    other_expense: 100000,
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  // Lever manipulation state
  const [selectedLevers, setSelectedLevers] = useState(['recruitment']);
  const [selectedLevels, setSelectedLevels] = useState(['AM']);
  const [selectedMonth, setSelectedMonth] = useState(1);
  const [selectedOffices, setSelectedOffices] = useState([] as string[]);
  const [leverValue, setLeverValue] = useState(2.5); // Start with realistic A-level recruitment rate (2.5%)
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
  // Add new state variables for time period and office journey selection
  const [selectedTimePeriod, setSelectedTimePeriod] = useState('monthly');
  const [selectedOfficeJourney, setSelectedOfficeJourney] = useState('');
  const [applyToAllOffices, setApplyToAllOffices] = useState(false);
  // Add new state for lever matrix UI
  const [matrixOffice, setMatrixOffice] = useState(OFFICES[0]);
  const [matrixMonth, setMatrixMonth] = useState(1);
  const [matrixEditing, setMatrixEditing] = useState<null | { level: string, lever: string }>(null);
  const [matrixDraftLevers, setMatrixDraftLevers] = useState<LeversState | null>(null);

  // Fetch config on mount
  useEffect(() => {
    setConfigLoading(true);
    fetch('/api/offices/config')
      .then(res => res.json())
      .then(data => {
        setConfigOffices(data);
        setConfigLoading(false);
        // Only set originalConfigOffices if it is empty
        setOriginalConfigOffices(prev => (prev && prev.length > 0 ? prev : data));
        
        // Initialize levers with imported data if available, otherwise use defaults
        if (Object.keys(levers).length === 0) {
          loadImportedData(data);
        }
      })
      .catch(() => setConfigLoading(false));
  }, []);

  // Function to load actual imported data from backend
  const loadImportedData = (offices: any[]) => {
    try {
      // Convert office data to lever format
      const importedLevers: LeversState = {};
      offices.forEach((office: any) => {
        importedLevers[office.name] = {};
        
        // Handle roles with levels (Consultant, Sales, Recruitment)
        ['Consultant', 'Sales', 'Recruitment'].forEach(roleName => {
          const roleData = office.roles[roleName];
          if (roleData) {
            Object.entries(roleData).forEach(([levelName, levelData]: [string, any]) => {
              if (!importedLevers[office.name][levelName]) {
                importedLevers[office.name][levelName] = {};
              }
              
              // Convert monthly data to lever format
              for (let month = 1; month <= 12; month++) {
                importedLevers[office.name][levelName][`recruitment_${month}`] = levelData[`recruitment_${month}`] || (levelName === 'A' ? 0.025 : 0.015);
                importedLevers[office.name][levelName][`churn_${month}`] = levelData[`churn_${month}`] || 0.014;
                importedLevers[office.name][levelName][`progression_${month}`] = levelData[`progression_${month}`] || (month === 5 || month === 11 ? 0.08 : 0.0);
                importedLevers[office.name][levelName][`utr_${month}`] = levelData[`utr_${month}`] || 0.9;
              }
            });
          }
        });
      });
      
      setLevers(importedLevers);
      console.log('[DEBUG] Loaded imported configuration data:', importedLevers);
    } catch (error) {
      console.error('Failed to load imported data:', error);
      setLevers(getDefaultLevers());
    }
  };

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
      console.log('[DEBUG] Selected lever:', selectedLevers);
      console.log('[DEBUG] Selected level:', selectedLevels);
      console.log('[DEBUG] Selected offices:', selectedOffices);
      console.log('[DEBUG] Lever value:', leverValue);
      
      // Calculate start and end dates from duration
      const startYear = 2025;
      const startMonth = 1;
      const durationMonths = formVals.duration_unit === 'years' ? formVals.duration_value * 12 : formVals.duration_value;
      const endYear = startYear + Math.floor((startMonth + durationMonths - 2) / 12);
      const endMonth = ((startMonth + durationMonths - 2) % 12) + 1;
      
      const res = await fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          start_year: startYear,
          start_month: startMonth,
          end_year: endYear,
          end_month: endMonth,
          price_increase: Number(formVals.price_increase) / 100, // Convert percentage to decimal
          salary_increase: Number(formVals.salary_increase) / 100, // Convert percentage to decimal
          unplanned_absence: Number(formVals.unplanned_absence) / 100, // Convert percentage to decimal
          hy_working_hours: formVals.hy_working_hours,
          other_expense: formVals.other_expense,
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
    const totalFTE = totalConsultants + totalNonConsultants;
    // FIXED: Non-debit ratio should be (Non-Consultants / Total FTE) * 100
    // This represents the percentage of people who are not billable consultants
    const overallNonDebitRatio = totalFTE > 0 ? (totalNonConsultants / totalFTE) * 100 : null;
    
    // Debug logging for non-debit ratio
    console.log('[DEBUG] Non-debit ratio calculation:', {
      totalConsultants,
      totalNonConsultants,
      totalFTE,
      overallNonDebitRatio: overallNonDebitRatio?.toFixed(1) + '%'
    });
    
    // Calculate delta for non-debit ratio
    let nonDebitDelta = null;
    if (prevIdx >= 0) {
      const prevTotalFTE = prevTotalConsultants + prevTotalNonConsultants;
      if (prevTotalFTE > 0) {
        const prevNonDebitRatio = (prevTotalNonConsultants / prevTotalFTE) * 100;
        if (overallNonDebitRatio !== null) {
          nonDebitDelta = overallNonDebitRatio - prevNonDebitRatio;
        }
      }
    }
    
    // Calculate total growth for period
    let totalGrowth = null;
    let totalGrowthPercent = null;
    let baselineTotalFTE = null;
    
    if (originalConfigOffices && originalConfigOffices.length > 0) {
      // Calculate baseline total FTE from original config
      baselineTotalFTE = originalConfigOffices.reduce((sum: number, office: any) => {
        let officeTotal = 0;
        
        // Add consultant, sales, recruitment roles
        if (office.roles) {
          ['Consultant', 'Sales', 'Recruitment'].forEach(roleName => {
            const role = office.roles[roleName];
            if (role && typeof role === 'object') {
              // Role has levels
              Object.values(role).forEach((levelData: any) => {
                if (levelData && typeof levelData === 'object' && 'total' in levelData) {
                  officeTotal += levelData.total || 0;
                }
              });
            }
          });
        }
        
        // Add operations (single number, not levels)
        if (office.operations && typeof office.operations === 'number') {
          officeTotal += office.operations;
        }
        
        return sum + officeTotal;
      }, 0);
      
      // Calculate growth
      totalGrowth = totalFTE - baselineTotalFTE;
      totalGrowthPercent = baselineTotalFTE > 0 ? (totalGrowth / baselineTotalFTE) * 100 : 0;
      
      // Debug logging
      console.log('[DEBUG] Total Growth calculation:', {
        currentTotalFTE: totalFTE,
        baselineTotalFTE,
        totalGrowth,
        totalGrowthPercent: totalGrowthPercent?.toFixed(1) + '%'
      });
    }

    return { 
      journeyTotals, 
      totalJourney, 
      overallNonDebitRatio, 
      totalConsultants, 
      totalNonConsultants, 
      nonDebitDelta,
      totalGrowth,
      totalGrowthPercent,
      baselineTotalFTE,
      totalFTE
    };
  };



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
    let targetOffices: string[] = [];
    if (applyToAllOffices) {
      targetOffices = OFFICES;
    } else if (selectedOfficeJourney) {
      targetOffices = configOffices
        .filter(office => {
          const totalFTE = office.roles ? 
            Object.values(office.roles).reduce((sum: number, role: any) => {
              if (typeof role === 'object' && role !== null) {
                if ('total' in role) {
                  return sum + (role.total || 0);
                } else {
                  return sum + Object.values(role).reduce((levelSum: number, levelData: any) => 
                    levelSum + (levelData?.total || 0), 0);
                }
              }
              return sum;
            }, 0) : 0;
          let journey = '';
          if (totalFTE >= 500) journey = 'Mature Office';
          else if (totalFTE >= 200) journey = 'Established Office';
          else if (totalFTE >= 25) journey = 'Emerging Office';
          else journey = 'New Office';
          return journey === selectedOfficeJourney;
        })
        .map(office => office.name);
    } else {
      targetOffices = selectedOffices;
    }
    if (targetOffices.length === 0) {
      message.warning('Please select at least one office or office journey.');
      return;
    }
    let targetMonths: number[] = [];
    if (selectedTimePeriod === 'yearly') {
      targetMonths = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
    } else if (selectedTimePeriod === 'half-year') {
      if (selectedMonth <= 6) {
        targetMonths = [1, 2, 3, 4, 5, 6];
      } else {
        targetMonths = [7, 8, 9, 10, 11, 12];
      }
    } else if (applyToAllMonths) {
      targetMonths = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
    } else {
      targetMonths = [selectedMonth];
    }
    const updatedLevers = { ...levers };
    targetOffices.forEach(office => {
      updatedLevers[office] = { ...updatedLevers[office] };
      selectedLevels.forEach(level => {
        updatedLevers[office][level] = { ...updatedLevers[office][level] };
        selectedLevers.forEach(leverKey => {
          targetMonths.forEach(month => {
            updatedLevers[office][level][`${leverKey}_${month}`] = effectiveMonthlyRate;
          });
        });
      });
    });
    setLevers(updatedLevers);
    // Build grouped summary
    const leverSummaries: string[] = [];
    // Group by lever, value, levels, months, offices
    const groupKey = (leverKey: string, value: number) => `${leverKey}|${value}`;
    const groupMap: Record<string, { leverKey: string, value: number, levels: Set<string>, months: Set<number>, offices: Set<string> }> = {};
    targetOffices.forEach(office => {
      selectedLevels.forEach(level => {
        selectedLevers.forEach(leverKey => {
          targetMonths.forEach(month => {
            const key = groupKey(leverKey, effectiveMonthlyRate);
            if (!groupMap[key]) {
              groupMap[key] = { leverKey, value: effectiveMonthlyRate, levels: new Set(), months: new Set(), offices: new Set() };
            }
            groupMap[key].levels.add(level);
            groupMap[key].months.add(month);
            groupMap[key].offices.add(office);
          });
        });
      });
    });
    Object.values(groupMap).forEach(group => {
      const leverLabel = LEVERS.find(l => l.key === group.leverKey)?.label || group.leverKey;
      const percent = `${(group.value * 100).toFixed(1)}%`;
      const levelsStr = Array.from(group.levels).join(', ');
      // Show month range or list
      const monthsArr = Array.from(group.months).sort((a, b) => a - b);
      let monthsStr = '';
      if (monthsArr.length === 12 && monthsArr[0] === 1 && monthsArr[11] === 12) {
        monthsStr = 'months 1–12';
      } else if (monthsArr.length > 1) {
        monthsStr = `months ${monthsArr[0]}–${monthsArr[monthsArr.length - 1]}`;
      } else {
        monthsStr = `month ${monthsArr[0]}`;
      }
      const officesStr = Array.from(group.offices).join(', ');
      leverSummaries.push(`${leverLabel} for levels ${levelsStr} set to ${percent} for ${monthsStr} in ${officesStr}`);
    });
    if (leverSummaries.length > 0) {
      setLastAppliedSummary(leverSummaries);
    } else {
      setLastAppliedSummary(['No levers applied.']);
    }
  };

  const handleReset = async () => {
    try {
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
        duration_value: 24, // Duration amount
        duration_unit: 'months', // 'months' or 'years'
        price_increase: 3.0, // 3% as percentage
        salary_increase: 3.0, // 3% as percentage
        unplanned_absence: 5.0, // 5% as percentage
        hy_working_hours: 166.4, // Monthly working hours
        other_expense: 100000,
      });
      
      // Reload the original config data from backend to reset backend state
      const res = await fetch('/api/offices/config');
      if (res.ok) {
        const configData = await res.json();
        setConfigOffices(configData);
        setOriginalConfigOffices(configData);
        // Load the fresh config data into levers
        loadImportedData(configData);
        console.log('[DEBUG] Reset: Reloaded original config data from backend');
      } else {
        console.error('Failed to reload config data during reset');
      }
      
      // Show success message
      message.success('Simulation reset to original configuration');
    } catch (error) {
      console.error('Error during reset:', error);
      message.error('Failed to reset simulation');
    }
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

  // Simulation duration calculation for reference
  const simulationDurationMonths = formVals ? 
    (formVals.duration_unit === 'years' ? formVals.duration_value * 12 : formVals.duration_value) : 1;

  // After simulationResults are set, use KPIs from backend
  const backendKPIs = simulationResults?.kpis || null;

  // Use backend KPIs if available, otherwise fall back to frontend calculation
  const aggregatedKPIs = backendKPIs ? {
    journeyTotals: backendKPIs.journeys?.journey_totals || {} as Record<string, number>,
    totalJourney: Object.values(backendKPIs.journeys?.journey_totals || {}).reduce((a, b) => (a as number) + (b as number), 0) as number,
    overallNonDebitRatio: backendKPIs.growth?.non_debit_ratio || null as number | null,
    totalConsultants: backendKPIs.financial?.total_consultants || 0 as number,
    totalNonConsultants: (backendKPIs.growth?.current_total_fte || 0) - (backendKPIs.financial?.total_consultants || 0) as number,
    nonDebitDelta: backendKPIs.growth?.non_debit_delta || null as number | null,
    totalGrowth: backendKPIs.growth?.total_growth_absolute || null as number | null,
    totalGrowthPercent: backendKPIs.growth?.total_growth_percent || null as number | null,
    baselineTotalFTE: backendKPIs.growth?.baseline_total_fte || null as number | null,
    totalFTE: backendKPIs.growth?.current_total_fte || 0 as number
  } : getAggregatedKPIs();

  // Helper to get lever value for matrix
  const getMatrixLeverValue = (office: string, level: string, lever: string, month: number) => {
    const source = matrixDraftLevers || levers;
    return source?.[office]?.[level]?.[`${lever}_${month}`] ?? '';
  };

  // Helper to get default value for highlighting
  const getMatrixDefaultValue = (level: string, lever: string, month: number) => {
    if (lever === 'recruitment') return level === 'A' ? 0.025 : 0.015;
    if (lever === 'churn') return 0.014;
    if (lever === 'progression') return (month === 5 || month === 11) ? 0.08 : 0.0;
    if (lever === 'utr') return 0.9;
    return '';
  };

  // Handler for cell edit
  const handleMatrixCellChange = (level: string, lever: string, value: number) => {
    setMatrixDraftLevers(prev => {
      const draft = prev ? { ...prev } : JSON.parse(JSON.stringify(levers));
      if (!draft[matrixOffice]) draft[matrixOffice] = {};
      if (!draft[matrixOffice][level]) draft[matrixOffice][level] = {};
      draft[matrixOffice][level][`${lever}_${matrixMonth}`] = value;
      return draft;
    });
  };

  // Handler for Apply
  const handleMatrixApply = () => {
    if (matrixDraftLevers) {
      setLevers(matrixDraftLevers);
      setMatrixDraftLevers(null);
      message.success('Levers updated for this office/month.');
    }
  };

  // Handler for Reset
  const handleMatrixReset = () => {
    setMatrixDraftLevers(null);
    message.info('Draft changes discarded.');
  };

  // Lever matrix columns
  const leverMatrixColumns = LEVERS.map(lv => ({
    title: lv.label,
    dataIndex: lv.key,
    key: lv.key,
    render: (_: any, row: any) => {
      const value = getMatrixLeverValue(matrixOffice, row.level, lv.key, matrixMonth);
      const defaultValue = getMatrixDefaultValue(row.level, lv.key, matrixMonth);
      const changed = value !== '' && value !== undefined && value !== null && Number(value) !== defaultValue;
      return (
        <InputNumber
          min={0}
          max={lv.key === 'utr' ? 1 : 1}
          step={0.001}
          value={value === '' ? undefined : Number(value)}
          onChange={(v: string | number | null) => {
            let num = typeof v === 'string' ? parseFloat(v) : v;
            if (num === null || isNaN(Number(num))) num = 0;
            handleMatrixCellChange(row.level, lv.key, Number(num));
          }}
          style={{ width: 80, background: changed ? '#ffe58f' : undefined }}
          formatter={(val: string | number | undefined) => val !== undefined ? (lv.key === 'utr' ? `${(Number(val) * 100).toFixed(1)}%` : `${(Number(val) * 100).toFixed(1)}%`) : ''}
          parser={(str: string | undefined) => {
            if (!str) return '';
            const num = Number(str.replace('%', ''));
            return isNaN(num) ? '' : num / 100;
          }}
        />
      );
    }
  }));

  // Lever matrix data
  const leverMatrixData = LEVELS.map(level => ({ key: level, level }));

  // Compute the effective monthly rate if yearly or half-year is selected
  let effectiveMonthlyRate = leverValue / 100;
  let helperText = '';
  if (selectedTimePeriod === 'yearly') {
    effectiveMonthlyRate = getMonthlyRateFromCumulative(leverValue / 100, 12);
    helperText = `Yearly: ${leverValue}% → Monthly: ${(effectiveMonthlyRate * 100).toFixed(2)}% (applied to all 12 months)`;
  } else if (selectedTimePeriod === 'half-year') {
    effectiveMonthlyRate = getMonthlyRateFromCumulative(leverValue / 100, 6);
    helperText = `Half Year: ${leverValue}% → Monthly: ${(effectiveMonthlyRate * 100).toFixed(2)}% (applied to 6 months)`;
  } else {
    helperText = `Monthly: ${leverValue}%`;
  }

  return (
    <Card title={<Title level={4} style={{ margin: 0 }}>Simulation Lab</Title>}>
      {/* Lever Manipulation Panel - always at the top */}
      <Row gutter={16} align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <span>Levers: </span>
          <Select
            mode="multiple"
            value={selectedLevers}
            onChange={setSelectedLevers}
            style={{ width: 180 }}
          >
            {LEVERS.map(l => <Option key={l.key} value={l.key}>{l.label}</Option>)}
          </Select>
        </Col>
        <Col>
          <span>Levels: </span>
          <Select
            mode="multiple"
            value={selectedLevels}
            onChange={setSelectedLevels}
            style={{ width: 180 }}
          >
            {LEVELS.map(lv => <Option key={lv} value={lv}>{lv}</Option>)}
          </Select>
        </Col>
        <Col>
          <span>Value: </span>
          <InputNumber
            min={0}
            max={selectedLevers.includes('utr') ? 100 : 100}
            step={0.1}
            value={leverValue}
            onChange={v => setLeverValue(v ?? 0)}
            style={{ width: 90 }}
            suffix="%"
          />
          <div style={{ fontSize: 12, color: '#aaa', marginTop: 2 }}>{helperText}</div>
        </Col>
      </Row>

      {/* Time Period Selection Row */}
      <Row gutter={16} align="middle" style={{ marginBottom: 16 }}>
        <Col>
          <span>Time Period: </span>
          <Select value={selectedTimePeriod} onChange={setSelectedTimePeriod} style={{ width: 120 }}>
            {TIME_PERIODS.map(tp => <Option key={tp.value} value={tp.value}>{tp.label}</Option>)}
          </Select>
        </Col>
        {selectedTimePeriod === 'monthly' && (
          <Col>
            <span>Month: </span>
            <Select value={selectedMonth} onChange={setSelectedMonth} style={{ width: 120 }}>
              {MONTHS.map(m => <Option key={m.value} value={m.value}>{m.value}</Option>)}
            </Select>
          </Col>
        )}
        {selectedTimePeriod === 'half-year' && (
          <Col>
            <span>Reference Month: </span>
            <Select value={selectedMonth} onChange={setSelectedMonth} style={{ width: 120 }}>
              {MONTHS.map(m => <Option key={m.value} value={m.value}>{m.value}</Option>)}
            </Select>
            <Text type="secondary" style={{ marginLeft: 8, fontSize: 12 }}>
              ({selectedMonth <= 6 ? 'First half (Jan-Jun)' : 'Second half (Jul-Dec)'})
            </Text>
          </Col>
        )}
        {selectedTimePeriod === 'monthly' && (
          <Col>
            <Checkbox
              checked={applyToAllMonths}
              onChange={e => setApplyToAllMonths(e.target.checked)}
            >
              Apply to all months
            </Checkbox>
          </Col>
        )}
      </Row>

      {/* Office Selection Row */}
      <Row gutter={16} align="middle" style={{ marginBottom: 16 }}>
        <Col>
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
            <Col>
              <span>Office Journey: </span>
              <Select
                value={selectedOfficeJourney}
                onChange={(value) => {
                  setSelectedOfficeJourney(value);
                  if (value) setSelectedOffices([]);
                }}
                style={{ width: 200 }}
                placeholder="Select journey type"
                allowClear
              >
                {OFFICE_JOURNEYS.map(oj => <Option key={oj.value} value={oj.value}>{oj.label}</Option>)}
              </Select>
            </Col>
            {!selectedOfficeJourney && (
              <Col>
                <span>Specific Offices: </span>
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
            )}
          </>
        )}
      </Row>

      {/* Action Buttons Row */}
      <Row gutter={16} align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Button type="primary" onClick={handleApply}>Apply</Button>
        </Col>
        <Col>
          <Button onClick={() => loadImportedData(configOffices)}>Load Config Data</Button>
        </Col>
        <Col>
          <Button onClick={handleReset}>Reset</Button>
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
            <Form.Item label="Simulation Duration" name="duration_value" rules={[{ required: true }]}> 
              <InputNumber min={1} max={120} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Form.Item label="Duration Unit" name="duration_unit" rules={[{ required: true }]}> 
              <Select>
                <Option value="months">Months</Option>
                <Option value="years">Years</Option>
              </Select>
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Form.Item label="Price Increase (%)" name="price_increase" rules={[{ required: true }]}> 
              <InputNumber min={0} max={100} step={0.1} style={{ width: '100%' }} suffix="%" />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Form.Item label="Salary Increase (%)" name="salary_increase" rules={[{ required: true }]}> 
              <InputNumber min={0} max={100} step={0.1} style={{ width: '100%' }} suffix="%" />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Form.Item label="Unplanned Absence (%)" name="unplanned_absence" rules={[{ required: true }]}> 
              <InputNumber min={0} max={100} step={0.1} style={{ width: '100%' }} suffix="%" />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Form.Item label="Monthly Working Hours" name="hy_working_hours" rules={[{ required: true }]}> 
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
            const numValue = Number(value);
            const percent = aggregatedKPIs.totalJourney > 0 ? ((numValue / aggregatedKPIs.totalJourney) * 100) : 0;
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
                  <div style={{ fontSize: 22, fontWeight: 600, marginBottom: 2 }}>{numValue}</div>
                  {delta !== null && delta !== undefined && Math.abs(delta) > 0.01 && (
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
                    {aggregatedKPIs.overallNonDebitRatio !== null && aggregatedKPIs.overallNonDebitRatio !== undefined ? `${aggregatedKPIs.overallNonDebitRatio.toFixed(1)}%` : 'N/A'}
                  </div>
                  {/* Show absolute numbers */}
                  <div style={{ fontSize: 11, color: '#aaa', marginTop: 2 }}>
                    Consultants: {aggregatedKPIs.totalConsultants || 0}
                  </div>
                  <div style={{ fontSize: 11, color: '#aaa' }}>
                    Sales+Rec+Ops: {aggregatedKPIs.totalNonConsultants || 0}
                  </div>
                  {/* Show delta if available */}
                  {aggregatedKPIs.nonDebitDelta !== null && aggregatedKPIs.nonDebitDelta !== undefined && Math.abs(aggregatedKPIs.nonDebitDelta) > 0.01 && (
                    <div style={{ fontSize: 11, fontWeight: 500, color: aggregatedKPIs.nonDebitDelta > 0 ? '#52c41a' : '#ff4d4f', marginTop: 2 }}>
                      Δ {aggregatedKPIs.nonDebitDelta > 0 ? '+' : ''}{aggregatedKPIs.nonDebitDelta.toFixed(1)}%
                    </div>
                  )}
                </div>
              </div>
            </Card>
          </Col>
          {/* Total Growth for Period KPI */}
          <Col xs={24} sm={12} md={6} key="total-growth">
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
                <div>
                  <Text style={{ color: '#bfbfbf', fontSize: 12 }}>Total Growth for Period</Text>
                  <div style={{ fontWeight: 700, fontSize: 22, color: '#fff', lineHeight: 1 }}>
                    {aggregatedKPIs.totalGrowthPercent !== null && aggregatedKPIs.totalGrowthPercent !== undefined ? `${aggregatedKPIs.totalGrowthPercent > 0 ? '+' : ''}${aggregatedKPIs.totalGrowthPercent.toFixed(1)}%` : 'N/A'}
                  </div>
                  {/* Show absolute numbers */}
                  <div style={{ fontSize: 11, color: '#aaa', marginTop: 2 }}>
                    Current: {aggregatedKPIs.totalFTE || 0} FTE
                  </div>
                  <div style={{ fontSize: 11, color: '#aaa' }}>
                    Baseline: {aggregatedKPIs.baselineTotalFTE || 0} FTE
                  </div>
                  {/* Show absolute growth */}
                  {aggregatedKPIs.totalGrowth !== null && aggregatedKPIs.totalGrowth !== undefined && (
                    <div style={{ fontSize: 11, fontWeight: 500, color: aggregatedKPIs.totalGrowth > 0 ? '#52c41a' : aggregatedKPIs.totalGrowth < 0 ? '#ff4d4f' : '#aaa', marginTop: 2 }}>
                      {aggregatedKPIs.totalGrowth > 0 ? '+' : ''}{aggregatedKPIs.totalGrowth} FTE
                    </div>
                  )}
                </div>
              </div>
            </Card>
          </Col>
          {/* Financial KPIs - Using Backend Data */}
          {backendKPIs && backendKPIs.financial && (
            <>
              <Col xs={24} sm={12} md={6} key="net-sales">
                <Card bordered={false} style={{background: '#1f1f1f', color: '#fff', borderRadius: 12, minHeight: 80, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'flex-start', padding: 16}}>
                  <div style={{ fontSize: 12, color: '#bfbfbf' }}>Net Sales</div>
                  <div style={{ fontWeight: 700, fontSize: 22, color: '#fff' }}>
                    {backendKPIs.financial.current_net_sales !== null && backendKPIs.financial.current_net_sales !== undefined ? 
                      backendKPIs.financial.current_net_sales.toLocaleString(undefined, { maximumFractionDigits: 0 }) : 'N/A'}
                  </div>
                  {backendKPIs.financial.baseline_net_sales !== null && backendKPIs.financial.baseline_net_sales !== undefined && (
                    <div style={{ fontSize: 11, color: '#aaa', marginTop: 2 }}>
                      Baseline: {backendKPIs.financial.baseline_net_sales.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </div>
                  )}
                  {backendKPIs.financial.net_sales_delta !== null && backendKPIs.financial.net_sales_delta !== undefined && Math.abs(backendKPIs.financial.net_sales_delta) > 1 && (
                    <div style={{ fontSize: 11, fontWeight: 500, color: backendKPIs.financial.net_sales_delta > 0 ? '#52c41a' : '#ff4d4f', marginTop: 2 }}>
                      Δ {backendKPIs.financial.net_sales_delta > 0 ? '+' : ''}{backendKPIs.financial.net_sales_delta.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </div>
                  )}
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6} key="ebitda">
                <Card bordered={false} style={{background: '#1f1f1f', color: '#fff', borderRadius: 12, minHeight: 80, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'flex-start', padding: 16}}>
                  <div style={{ fontSize: 12, color: '#bfbfbf' }}>EBITDA</div>
                  <div style={{ fontWeight: 700, fontSize: 22, color: '#fff' }}>
                    {backendKPIs.financial.current_ebitda !== null && backendKPIs.financial.current_ebitda !== undefined ? 
                      backendKPIs.financial.current_ebitda.toLocaleString(undefined, { maximumFractionDigits: 0 }) : 'N/A'}
                  </div>
                  {backendKPIs.financial.baseline_ebitda !== null && backendKPIs.financial.baseline_ebitda !== undefined && (
                    <div style={{ fontSize: 11, color: '#aaa', marginTop: 2 }}>
                      Baseline: {backendKPIs.financial.baseline_ebitda.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </div>
                  )}
                  {backendKPIs.financial.ebitda_delta !== null && backendKPIs.financial.ebitda_delta !== undefined && Math.abs(backendKPIs.financial.ebitda_delta) > 1 && (
                    <div style={{ fontSize: 11, fontWeight: 500, color: backendKPIs.financial.ebitda_delta > 0 ? '#52c41a' : '#ff4d4f', marginTop: 2 }}>
                      Δ {backendKPIs.financial.ebitda_delta > 0 ? '+' : ''}{backendKPIs.financial.ebitda_delta.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </div>
                  )}
                </Card>
              </Col>
              <Col xs={24} sm={12} md={6} key="margin">
                <Card bordered={false} style={{background: '#1f1f1f', color: '#fff', borderRadius: 12, minHeight: 80, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'flex-start', padding: 16}}>
                  <div style={{ fontSize: 12, color: '#bfbfbf' }}>Margin</div>
                  <div style={{ fontWeight: 700, fontSize: 22, color: '#fff' }}>
                    {backendKPIs.financial.current_margin !== null && backendKPIs.financial.current_margin !== undefined ? 
                      `${backendKPIs.financial.current_margin.toFixed(1)}%` : 'N/A'}
                  </div>
                  {backendKPIs.financial.baseline_margin !== null && backendKPIs.financial.baseline_margin !== undefined && (
                    <div style={{ fontSize: 11, color: '#aaa', marginTop: 2 }}>
                      Baseline: {backendKPIs.financial.baseline_margin.toFixed(1)}%
                    </div>
                  )}
                  {backendKPIs.financial.margin_delta !== null && backendKPIs.financial.margin_delta !== undefined && Math.abs(backendKPIs.financial.margin_delta) > 0.1 && (
                    <div style={{ fontSize: 11, fontWeight: 500, color: backendKPIs.financial.margin_delta > 0 ? '#52c41a' : '#ff4d4f', marginTop: 2 }}>
                      Δ {backendKPIs.financial.margin_delta > 0 ? '+' : ''}{backendKPIs.financial.margin_delta.toFixed(1)}%
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

      {/* Levers Table (Matrix) */}
      <Tabs defaultActiveKey="main" items={[{
        key: 'main',
        label: 'Simulation',
        children: (
          <>
            {/* Existing content */}
          </>
        )
      }, {
        key: 'levers',
        label: 'Levers Table',
        children: (
          <Card title={<span>Levers Table (Matrix)</span>} style={{ marginBottom: 24 }}>
            <Row gutter={16} align="middle" style={{ marginBottom: 16 }}>
              <Col>
                <span>Office: </span>
                <Select value={matrixOffice} onChange={setMatrixOffice} style={{ width: 180 }}>
                  {OFFICES.map(ofc => <Option key={ofc} value={ofc}>{ofc}</Option>)}
                </Select>
              </Col>
              <Col>
                <span>Month: </span>
                <Select value={matrixMonth} onChange={setMatrixMonth} style={{ width: 120 }}>
                  {MONTHS.map(m => <Option key={m.value} value={m.value}>{m.label}</Option>)}
                </Select>
              </Col>
              <Col>
                <Button type="primary" onClick={handleMatrixApply} disabled={!matrixDraftLevers}>Apply</Button>
              </Col>
              <Col>
                <Button onClick={handleMatrixReset} disabled={!matrixDraftLevers}>Reset</Button>
              </Col>
            </Row>
            <Table
              columns={[
                { title: 'Level', dataIndex: 'level', key: 'level' },
                ...leverMatrixColumns
              ]}
              dataSource={leverMatrixData}
              pagination={false}
              size="small"
              bordered
            />
            <div style={{ marginTop: 12, color: '#888', fontSize: 13 }}>
              <span>Yellow cells = changed from default. Values are in percent (e.g., 0.08 = 8%).</span>
            </div>
          </Card>
        )
      }]} />
    </Card>
  );
} 