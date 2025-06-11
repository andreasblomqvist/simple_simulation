import React, { useState } from 'react';
import { Form, InputNumber, Select, Button, Card, Row, Col, Typography, Table, Tag, Spin, message } from 'antd';
import { useConfig } from '../components/ConfigContext';

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
const HALVES = ['H1', 'H2'];
type LeversState = Record<string, Record<string, Record<string, number>>>;
const getDefaultLevers = (): LeversState => {
  const obj: LeversState = {};
  OFFICES.forEach(office => {
    obj[office] = {};
    LEVELS.forEach(level => {
      obj[office][level] = {};
      LEVERS.forEach(lv => {
        HALVES.forEach(h => {
          obj[office][level][`${lv.key}_${h}`] = 0.1;
        });
      });
    });
  });
  return obj;
};

// Example roles for each level
const ROLES = ['Consultant', 'Sales', 'Recruitment', 'Operations'];

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
  const ROLES = ['Consultant', 'Sales', 'Recruitment', 'Operations'];
  const ROLES_WITH_LEVELS = ['Consultant', 'Sales', 'Recruitment'];
  const LEVELS = ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"];
  return Object.entries(results.offices).map(([officeName, officeData]: any) => {
    let rows: any[] = [];
    let officeTotal = 0;
    let officeStartTotal = 0;
    ROLES.forEach(role => {
      if (ROLES_WITH_LEVELS.includes(role)) {
        let roleTotal = 0;
        let roleStartTotal = 0;
        let totalPrice = 0;
        let totalSalary = 0;
        let totalWithPrice = 0;
        let totalWithSalary = 0;
        let roleStartPrice = 0;
        let roleStartSalary = 0;
        let totalStartWithPrice = 0;
        let totalStartWithSalary = 0;
        let deltas: number[] = [];
        const children = LEVELS.map(level => {
          const arr = officeData.levels?.[role]?.[level] || [];
          const last = arr.length > 0 ? arr[arr.length - 1] : {};
          const first = arr.length > 0 ? arr[0] : {};
          const delta = arr.length > 1 ? (last.total ?? 0) - (first?.total ?? 0) : null;
          roleTotal += last.total || 0;
          roleStartTotal += first.total || 0;
          if (delta !== null && delta !== undefined) deltas.push(delta);
          if (last.price) {
            totalPrice += last.price * (last.total || 0);
            totalWithPrice += last.total || 0;
          }
          if (last.salary) {
            totalSalary += last.salary * (last.total || 0);
            totalWithSalary += last.total || 0;
          }
          if (first.price) {
            roleStartPrice += first.price * (first.total || 0);
            totalStartWithPrice += first.total || 0;
          }
          if (first.salary) {
            roleStartSalary += first.salary * (first.total || 0);
            totalStartWithSalary += first.total || 0;
          }
          return {
            key: `${officeName}-${role}-${level}`,
            office: '',
            role: '',
            level,
            total: (last.total !== undefined && first.total !== undefined)
              ? `${last.total} (${first.total})`
              : last.total ?? '',
            delta: delta !== null && delta !== undefined ? Number(delta.toFixed(1)) : null,
            price: (last.price !== undefined && first.price !== undefined)
              ? `${Number(last.price.toFixed(1))} (${Number(first.price.toFixed(1))})`
              : last.price !== undefined ? Number(last.price.toFixed(1)) : null,
            salary: (last.salary !== undefined && first.salary !== undefined)
              ? `${Number(last.salary.toFixed(1))} (${Number(first.salary.toFixed(1))})`
              : last.salary !== undefined ? Number(last.salary.toFixed(1)) : null,
            journey: '',
            totalRole: (last.total !== undefined && first.total !== undefined)
              ? `${last.total} (${first.total})`
              : last.total ?? 0,
            fteStart: first.total || 0,
          };
        });
        officeTotal += roleTotal;
        officeStartTotal += roleStartTotal;
        // Calculate average delta for the role
        const avgDelta = deltas.length > 0 ? Number((deltas.reduce((a, b) => a + b, 0) / deltas.length).toFixed(1)) : null;
        rows.push({
          key: `${officeName}-${role}`,
          office: '',
          role,
          level: '',
          total: '',
          delta: avgDelta,
          price: (totalWithPrice > 0 && totalStartWithPrice > 0)
            ? `${Number((totalPrice / totalWithPrice).toFixed(1))} (${Number((roleStartPrice / totalStartWithPrice).toFixed(1))})`
            : null,
          salary: (totalWithSalary > 0 && totalStartWithSalary > 0)
            ? `${Number((totalSalary / totalWithSalary).toFixed(1))} (${Number((roleStartSalary / totalStartWithSalary).toFixed(1))})`
            : null,
          journey: '',
          totalRole: `${roleTotal} (${roleStartTotal})`,
          children,
        });
      } else {
        // Flat role (e.g., Operations)
        let opTotal = 0;
        let opStartTotal = 0;
        let opTotalPrice = 0;
        let opStartPrice = 0;
        let opTotalSalary = 0;
        let opStartSalary = 0;
        let opTotalWith = 0;
        let opStartWith = 0;
        let deltas: number[] = [];
        const children = (officeData[role.toLowerCase()] || []).map((item: any, idx: number, arr: any[]) => {
          const first = arr[0] || {};
          const last = item;
          const delta = arr.length > 1 ? (last.total ?? 0) - (first?.total ?? 0) : null;
          opTotal += last.total || 0;
          opStartTotal += first.total || 0;
          if (last.price) {
            opTotalPrice += last.price * (last.total || 0);
            opTotalWith += last.total || 0;
          }
          if (last.salary) {
            opTotalSalary += last.salary * (last.total || 0);
          }
          if (first.price) {
            opStartPrice += first.price * (first.total || 0);
            opStartWith += first.total || 0;
          }
          if (first.salary) {
            opStartSalary += first.salary * (first.total || 0);
          }
          if (delta !== null && delta !== undefined) deltas.push(delta);
          return {
            key: `${officeName}-${role}-op-${idx}`,
            office: '',
            role: '',
            level: '',
            total: '',
            delta: delta !== null && delta !== undefined ? Number(delta.toFixed(1)) : null,
            price: last.price ? Number(last.price.toFixed(1)) : null,
            salary: last.salary ? Number(last.salary.toFixed(1)) : null,
            journey: '',
            totalRole: last.total || 0,
            fteStart: first.total || 0,
          };
        });
        const avgDelta = deltas.length > 0 ? Number((deltas.reduce((a, b) => a + b, 0) / deltas.length).toFixed(1)) : null;
        rows.push({
          key: `${officeName}-${role}`,
          office: '',
          role,
          level: '',
          total: '',
          delta: avgDelta,
          price: (opTotalWith > 0 && opStartWith > 0)
            ? `${Number((opTotalPrice / opTotalWith).toFixed(1))} (${Number((opStartPrice / opStartWith).toFixed(1))})`
            : '',
          salary: (opTotalWith > 0 && opStartWith > 0)
            ? `${Number((opTotalSalary / opTotalWith).toFixed(1))} (${Number((opStartSalary / opStartWith).toFixed(1))})`
            : '',
          journey: '',
          totalRole: `${opTotal} (${opStartTotal})`,
          children,
        });
      }
    });
    // Office summary row price/salary
    let officeTotalPrice = 0;
    let officeStartPrice = 0;
    let officeTotalSalary = 0;
    let officeStartSalary = 0;
    let officeTotalWith = 0;
    let officeStartWith = 0;
    rows.forEach(row => {
      // Only sum role rows (not children)
      if (row.role && !row.level) {
        const [curFte, startFte] = row.totalRole.split(' ').map((n: string) => parseInt(n.replace(/[()]/g, '')));
        // Price
        if (row.price && row.price.includes('(')) {
          const [curPrice, startPrice] = row.price.split(' ').map((n: string) => parseFloat(n.replace(/[()]/g, '')));
          officeTotalPrice += curPrice * curFte;
          officeStartPrice += startPrice * startFte;
          officeTotalWith += curFte;
          officeStartWith += startFte;
        }
        // Salary
        if (row.salary && row.salary.includes('(')) {
          const [curSalary, startSalary] = row.salary.split(' ').map((n: string) => parseFloat(n.replace(/[()]/g, '')));
          officeTotalSalary += curSalary * curFte;
          officeStartSalary += startSalary * startFte;
        }
      }
    });
    // Add office summary row with officeTotal in 'total' and also in 'totalRole'
    rows.unshift({
      key: `${officeName}-office`,
      office: officeName,
      role: '',
      level: '',
      total: officeTotal,
      delta: officeStartTotal !== officeTotal ? Number(((officeTotal - officeStartTotal) / officeStartTotal * 100).toFixed(1)) : null,
      price: (officeTotalWith > 0 && officeStartWith > 0)
        ? `${Number((officeTotalPrice / officeTotalWith).toFixed(1))} (${Number((officeStartPrice / officeStartWith).toFixed(1))})`
        : '',
      salary: (officeTotalWith > 0 && officeStartWith > 0)
        ? `${Number((officeTotalSalary / officeTotalWith).toFixed(1))} (${Number((officeStartSalary / officeStartWith).toFixed(1))})`
        : '',
      journey: officeData.office_journey || '',
      totalRole: `${officeTotal} (${officeStartTotal})`,
    });
    return rows;
  }).flat();
}

const levelColumns = [
  { title: 'Level', dataIndex: 'level', key: 'level' },
  { title: 'Total', dataIndex: 'total', key: 'total' },
  { title: 'Price (H1)', dataIndex: 'price', key: 'price' },
  { title: 'Salary (H1)', dataIndex: 'salary', key: 'salary' },
  { title: 'Recruitment (H1)', dataIndex: 'recruitment', key: 'recruitment' },
  { title: 'Churn (H1)', dataIndex: 'churn', key: 'churn' },
  { title: 'Progression (H1)', dataIndex: 'progression', key: 'progression' },
  { title: 'UTR (H1)', dataIndex: 'utr', key: 'utr' },
];

const roleColumns = [
  { title: 'Role', dataIndex: 'role', key: 'role' },
  { title: 'FTE', dataIndex: 'fte', key: 'fte' },
  { title: 'KPI', dataIndex: 'kpi', key: 'kpi' },
];

export default function SimulationLab() {
  const [formVals, setFormVals] = useState({
    start_year: 2024,
    start_half: 'H1',
    end_year: 2025,
    end_half: 'H2',
    price_increase: 0.03,
    salary_increase: 0.03,
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  // Lever manipulation state
  const [selectedLever, setSelectedLever] = useState('recruitment');
  const [selectedHalf, setSelectedHalf] = useState('H1');
  const [selectedLevel, setSelectedLevel] = useState('AM');
  const [selectedOffices, setSelectedOffices] = useState([] as string[]);
  const [leverValue, setLeverValue] = useState(0.1);
  const { levers, setLevers } = useConfig();
  const [lastAppliedSummary, setLastAppliedSummary] = useState<string[] | null>(null);
  const [simulationResults, setSimulationResults] = useState<any>(null);
  const [baselineResults, setBaselineResults] = useState<any>(null);

  const handleFormChange = (changed: any, all: any) => {
    setFormVals(all);
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const ROLES_WITH_LEVELS = ['Consultant', 'Sales', 'Recruitment'];
      const FLAT_ROLE = 'Operations';
      const LEVELS = ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"];
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
        if (levels[FLAT_ROLE]) {
          office_overrides[office].roles[FLAT_ROLE] = { ...levels[FLAT_ROLE] };
        }
      });
      // LOGGING: Print the office_overrides payload
      console.log('[DEBUG] office_overrides payload:', office_overrides);
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
      // Get values for each level
      const levelTotalsFirst: { [key: string]: number } = {};
      const levelTotalsLast: { [key: string]: number } = {};
      LEVELS.forEach(level => {
        levelTotalsFirst[level] = levels[level]?.[firstIdx]?.total ?? 0;
        levelTotalsLast[level] = levels[level]?.[lastIdx]?.total ?? 0;
      });
      // Get operations
      const opsTotalFirst = operations?.[firstIdx]?.total ?? 0;
      const opsTotalLast = operations?.[lastIdx]?.total ?? 0;
      // Get metrics
      const firstMetrics = metrics?.[firstIdx] || {};
      const lastMetrics = metrics?.[lastIdx] || {};
      // Calculate total FTEs
      const totalFTEFirst = Object.values(levelTotalsFirst).reduce((a, b) => a + b, 0) + opsTotalFirst;
      const totalFTELast = Object.values(levelTotalsLast).reduce((a, b) => a + b, 0) + opsTotalLast;
      // Delta
      const delta = totalFTELast - totalFTEFirst;
      // Use office_journey if present, else fallback
      const journeyName = officeData.office_journey || '';
      return {
        name: officeName,
        journey: journeyName,
        total_fte: totalFTELast,
        delta,
        levelTotals: levelTotalsLast,
        opsTotal: opsTotalLast,
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
    if (!result || !result.offices) return null;
    const offices = result.offices;
    const periods = result.periods || [];
    const lastIdx = periods.length - 1;
    // Aggregate journey totals
    const journeyTotals: { [key: string]: number } = { 'Journey 1': 0, 'Journey 2': 0, 'Journey 3': 0, 'Journey 4': 0 };
    let totalConsultants = 0;
    let totalNonConsultants = 0;
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
      // For non-debit ratio: sum all consultants and non-consultants
      if (officeData.metrics && officeData.metrics[lastIdx]) {
        // Recompute for accuracy: sum all levels except operations
        if (officeData.levels) {
          Object.entries(officeData.levels).forEach(([level, arr]: any) => {
            if (arr && arr[lastIdx]) totalConsultants += arr[lastIdx].total || 0;
          });
        }
        if (officeData.operations && officeData.operations[lastIdx]) {
          totalNonConsultants += officeData.operations[lastIdx].total || 0;
        }
      }
    });
    const totalJourney = Object.values(journeyTotals).reduce((a, b) => a + b, 0);
    const overallNonDebitRatio = totalNonConsultants > 0 ? (totalConsultants / totalNonConsultants) : null;
    return { journeyTotals, totalJourney, overallNonDebitRatio };
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
      updatedLevers[office][selectedLevel][`${selectedLever}_${selectedHalf}`] = leverValue;
    });
    setLevers(updatedLevers);

    // Build summary array of all applied levers for selected offices
    const defaultValue = 0.1;
    const leverSummaries: string[] = [];
    selectedOffices.forEach(office => {
      if (!updatedLevers[office]) return;
      Object.entries(updatedLevers[office]).forEach(([level, leverObj]) => {
        Object.entries(leverObj as Record<string, number>).forEach(([leverHalf, value]) => {
          if ((value as number) !== defaultValue) {
            const [leverKey, half] = leverHalf.split('_');
            const leverLabel = LEVERS.find(l => l.key === leverKey)?.label || leverKey;
            const percent = `${((value as number) * 100).toFixed(0)}%`;
            leverSummaries.push(`${leverLabel} for level ${level} (${half}) set to ${percent} for ${office}`);
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

  // Add debug log before transforming results
  if (simulationResults) {
    // eslint-disable-next-line no-console
    console.log('[DEBUG] Raw simulationResults:', simulationResults);
  }
  return (
    <Card title={<Title level={4} style={{ margin: 0 }}>Simulation Lab</Title>}>
      {/* Lever Manipulation Panel */}
      <Row gutter={16} align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <span>Lever: </span>
          <Select value={selectedLever} onChange={setSelectedLever} style={{ width: 130 }}>
            {LEVERS.map(l => <Option key={l.key} value={l.key}>{l.label}</Option>)}
          </Select>
        </Col>
        <Col>
          <span>Half: </span>
          <Select value={selectedHalf} onChange={setSelectedHalf} style={{ width: 70 }}>
            {HALVES.map(h => <Option key={h} value={h}>{h}</Option>)}
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
      {/* Simulation Form */}
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
            <Form.Item label="Start Half" name="start_half" rules={[{ required: true }]}> 
              <Select>
                <Option value="H1">H1</Option>
                <Option value="H2">H2</Option>
              </Select>
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Form.Item label="End Year" name="end_year" rules={[{ required: true }]}> 
              <InputNumber min={2000} max={2100} style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Form.Item label="End Half" name="end_half" rules={[{ required: true }]}> 
              <Select>
                <Option value="H1">H1</Option>
                <Option value="H2">H2</Option>
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
        </Row>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading}>
            {loading ? 'Running...' : 'Run Simulation'}
          </Button>
        </Form.Item>
        {error && <Text type="danger">{error}</Text>}
      </Form>

      {/* KPI Cards */}
      {aggregatedKPIs && (
        <Row gutter={16} style={{ marginBottom: 32 }}>
          {Object.entries(aggregatedKPIs.journeyTotals).map(([journey, value]) => (
            <Col xs={24} sm={12} md={6} key={journey}>
              <Card>
                <Text type="secondary">{journey}</Text>
                <Title level={3} style={{ margin: 0 }}>{value}</Title>
                <Text type="secondary">
                  {aggregatedKPIs.totalJourney > 0 ? ((value / aggregatedKPIs.totalJourney) * 100).toFixed(1) : '0.0'}%
                </Text>
              </Card>
            </Col>
          ))}
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Text type="secondary">Non-Debit Ratio</Text>
              <Title level={3} style={{ margin: 0 }}>{aggregatedKPIs.overallNonDebitRatio !== null ? aggregatedKPIs.overallNonDebitRatio.toFixed(2) : 'N/A'}</Title>
            </Card>
          </Col>
        </Row>
      )}

      {/* Expandable Table (single table, hierarchical data) */}
      <Table
        columns={[
          {
            title: 'Office / Level / Role',
            key: 'name',
            render: (text, record) => {
              if ('office' in record && record.office) return <span style={{ fontWeight: 600 }}>{record.office}</span>;
              if ('role' in record && record.role) return <span style={{ marginLeft: 24 }}>{record.role}</span>;
              if ('level' in record && record.level) return <span style={{ marginLeft: 48 }}>{record.level}</span>;
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
            dataIndex: 'totalRole',
            key: 'totalRole',
            render: (text) => {
              if (!text) return null;
              if (typeof text === 'string' && text.includes('(')) {
                const [current, start] = text.split(' ').map((n: string) => parseInt(n.replace(/[()]/g, '')));
                const color = current < start ? 'red' : current > start ? 'green' : 'inherit';
                return <span style={{ color }}>{text}</span>;
              }
              return text;
            },
          },
          {
            title: 'Delta',
            dataIndex: 'delta',
            key: 'delta',
            render: (text) => text ?? null,
          },
          {
            title: 'Price',
            dataIndex: 'price',
            key: 'price',
            render: (text) => {
              if (!text && text !== 0) return null;
              if (typeof text === 'string' && text.includes('(')) {
                const [current, start] = text.split(' ').map((n: string) => parseFloat(n.replace(/[()]/g, '')));
                const color = current < start ? 'red' : current > start ? 'green' : 'inherit';
                return <span style={{ color }}>{text}</span>;
              }
              return text;
            },
          },
          {
            title: 'Salary',
            dataIndex: 'salary',
            key: 'salary',
            render: (text) => {
              if (!text && text !== 0) return null;
              if (typeof text === 'string' && text.includes('(')) {
                const [current, start] = text.split(' ').map((n: string) => parseFloat(n.replace(/[()]/g, '')));
                const color = current < start ? 'red' : current > start ? 'green' : 'inherit';
                return <span style={{ color }}>{text}</span>;
              }
              return text;
            },
          },
        ]}
        dataSource={simulationResults ? transformResults(simulationResults, baselineResults) : []}
        rowKey="key"
        pagination={false}
        expandable={{
          defaultExpandAllRows: false,
        }}
      />
    </Card>
  );
} 