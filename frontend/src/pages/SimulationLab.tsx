import React, { useState } from 'react';
import { Form, InputNumber, Select, Button, Card, Row, Col, Typography, Table, Tag, Spin, message } from 'antd';

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
  // results: { offices: { [office]: { levels: { [level]: [ ... ] }, ... } } }
  return Object.entries(results.offices).map(([officeName, officeData]: any) => {
    const baselineOffice = baseline?.offices?.[officeName] || {};
    return {
      key: officeName,
      office: officeName,
      journey: officeData.journey ?? '-',
      totalFte: officeData.total_fte ?? '-',
      growth: officeData.growth ?? '-',
      nonDebitRatio: officeData.non_debit_ratio ?? '-',
      children: Object.entries(officeData.levels).map(([levelName, levelData]: any) => {
        const baselineLevel = baselineOffice.levels?.[levelName] || {};
        // Use the last period's data for each level
        const lastIdx = Array.isArray(levelData) ? levelData.length - 1 : -1;
        const lastData = lastIdx >= 0 ? levelData[lastIdx] : {};
        const price_h1 = lastData.price ?? 0;
        const salary_h1 = lastData.salary ?? 0;
        // Recruitment, churn, progression, utr are not in backend output per level, so set to '-'
        // If you add them to backend, update here accordingly
        const recruitment_h1 = lastData.recruitment_h1 ?? '-';
        const churn_h1 = lastData.churn_h1 ?? '-';
        const progression_h1 = lastData.progression_h1 ?? '-';
        const utr_h1 = lastData.utr_h1 ?? '-';
        const baseline_price_h1 = baselineLevel.price_h1 ?? 0;
        const baseline_salary_h1 = baselineLevel.salary_h1 ?? 0;
        const baseline_recruitment_h1 = baselineLevel.recruitment_h1 ?? 0;
        const baseline_churn_h1 = baselineLevel.churn_h1 ?? 0;
        const baseline_progression_h1 = baselineLevel.progression_h1 ?? 0;
        const baseline_utr_h1 = baselineLevel.utr_h1 ?? 0;
        return {
          key: `${officeName}-${levelName}`,
          level: levelName,
          total: lastData.total ?? '-',
          price: `${price_h1.toFixed(2)}${getDiffString(price_h1, baseline_price_h1, false)}`,
          salary: `${salary_h1.toFixed(2)}${getDiffString(salary_h1, baseline_salary_h1, false)}`,
          recruitment: recruitment_h1,
          churn: churn_h1,
          progression: progression_h1,
          utr: utr_h1,
          children: ROLES.map(role => ({
            key: `${officeName}-${levelName}-${role}`,
            role,
            fte: '-',
            kpi: '-',
          })),
        };
      }),
    };
  });
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
  const [levers, setLevers] = useState<LeversState>(getDefaultLevers());
  const [lastAppliedSummary, setLastAppliedSummary] = useState<string | null>(null);
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
    setLevers(prev => {
      const updated = { ...prev };
      selectedOffices.forEach(office => {
        updated[office] = { ...updated[office] };
        updated[office][selectedLevel] = { ...updated[office][selectedLevel] };
        updated[office][selectedLevel][`${selectedLever}_${selectedHalf}`] = leverValue;
      });
      return updated;
    });
    // Build summary string
    const leverLabel = LEVERS.find(l => l.key === selectedLever)?.label || selectedLever;
    const percent = `${(leverValue * 100).toFixed(0)}%`;
    const officeList = selectedOffices.join(', ');
    setLastAppliedSummary(`${leverLabel} for level ${selectedLevel} (${selectedHalf}) set to ${percent} for ${officeList}.`);
    message.success('Lever value applied!');
  };

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
        <div style={{ marginBottom: 16, fontWeight: 500, color: '#096dd9' }}>{lastAppliedSummary}</div>
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
              if ('level' in record && record.level) return <span style={{ marginLeft: 24 }}>{record.level}</span>;
              if ('role' in record && record.role) return <span style={{ marginLeft: 48 }}>{record.role}</span>;
              return null;
            },
          },
          {
            title: 'Journey',
            dataIndex: 'journey',
            key: 'journey',
            render: (journey, record) => {
              if ('journey' in record && record.journey) return <Tag>{record.journey}</Tag>;
              return null;
            },
          },
          {
            title: 'Total FTE',
            dataIndex: 'totalFte',
            key: 'totalFte',
            render: (val, record) => {
              if ('totalFte' in record && record.totalFte !== undefined && record.totalFte !== null) return String(record.totalFte);
              if ('total' in record && record.total !== undefined && record.total !== null) return String(record.total);
              if ('fte' in record && record.fte !== undefined && record.fte !== null) return String(record.fte);
              return null;
            },
          },
          {
            title: 'Delta',
            dataIndex: 'delta',
            key: 'delta',
            render: (delta, record) => {
              if ('delta' in record && typeof record.delta === 'number') {
                return <span style={{ color: record.delta > 0 ? '#52c41a' : record.delta < 0 ? '#ff4d4f' : '#bfbfbf' }}>{record.delta > 0 ? '+' : ''}{record.delta}</span>;
              }
              return null;
            },
          },
          {
            title: 'Growth %',
            key: 'growth',
            render: (val, record) => {
              if ('growth' in record && record.growth !== undefined && record.growth !== null) return String(record.growth);
              if ('kpi' in record && record.kpi !== undefined && record.kpi !== null) return String(record.kpi);
              return null;
            },
          },
          {
            title: 'Non-Debit Ratio',
            key: 'ndr',
            render: (val, record) => {
              if ('nonDebitRatio' in record && record.nonDebitRatio !== undefined && record.nonDebitRatio !== null) return String(record.nonDebitRatio);
              return null;
            },
          },
          // Level columns
          {
            title: 'Price (H1)',
            key: 'price',
            render: (val, record) => {
              if ('price' in record && record.price !== undefined && record.price !== null) return String(record.price);
              return null;
            },
          },
          {
            title: 'Salary (H1)',
            key: 'salary',
            render: (val, record) => {
              if ('salary' in record && record.salary !== undefined && record.salary !== null) return String(record.salary);
              return null;
            },
          },
          {
            title: 'Recruitment (H1)',
            key: 'recruitment',
            render: (val, record) => {
              if ('recruitment' in record && record.recruitment !== undefined && record.recruitment !== null) return String(record.recruitment);
              return null;
            },
          },
          {
            title: 'Churn (H1)',
            key: 'churn',
            render: (val, record) => {
              if ('churn' in record && record.churn !== undefined && record.churn !== null) return String(record.churn);
              return null;
            },
          },
          {
            title: 'Progression (H1)',
            key: 'progression',
            render: (val, record) => {
              if ('progression' in record && record.progression !== undefined && record.progression !== null) return String(record.progression);
              return null;
            },
          },
          {
            title: 'UTR (H1)',
            key: 'utr',
            render: (val, record) => {
              if ('utr' in record && record.utr !== undefined && record.utr !== null) return String(record.utr);
              return null;
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