import React, { useState } from 'react';
import { Card, Table, Slider, Button, Space, Typography, Row, Col, Tooltip, Collapse } from 'antd';
import { InfoCircleOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;
const { Panel } = Collapse;

const ROLES = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P'];
const LEVERS = ['Recruitment', 'Churn', 'Progression'] as const;

type LeverType = typeof LEVERS[number];

type LeverState = Record<LeverType, Record<string, number>>;

const defaultValue = 1.0;
const min = 0.0;
const max = 2.0;
const step = 0.01;

// Mock baseline values for each role and lever
const baselineValues: Record<LeverType, Record<string, number>> = {
  Recruitment: { A: 20, AC: 8, C: 4, SrC: 1, AM: 1, M: 0, SrM: 0, Pi: 0, P: 0 },
  Churn: { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 0, Pi: 0, P: 0 },
  Progression: { A: 1, AC: 1, C: 1, SrC: 1, AM: 1, M: 1, SrM: 1, Pi: 1, P: 1 },
};

// Mock CAT progression probabilities (from progression_config.py)
const catProgressionData: Record<string, Record<string, number>> = {
  'A': { 'CAT0': 0.0, 'CAT6': 0.919, 'CAT12': 0.85, 'CAT18': 0.0, 'CAT24': 0.0, 'CAT30': 0.0 },
  'AC': { 'CAT0': 0.0, 'CAT6': 0.054, 'CAT12': 0.759, 'CAT18': 0.400, 'CAT24': 0.0, 'CAT30': 0.0 },
  'C': { 'CAT0': 0.0, 'CAT6': 0.050, 'CAT12': 0.442, 'CAT18': 0.597, 'CAT24': 0.278, 'CAT30': 0.643 },
  'SrC': { 'CAT0': 0.0, 'CAT6': 0.206, 'CAT12': 0.438, 'CAT18': 0.317, 'CAT24': 0.211, 'CAT30': 0.206 },
  'AM': { 'CAT0': 0.0, 'CAT6': 0.0, 'CAT12': 0.0, 'CAT18': 0.189, 'CAT24': 0.197, 'CAT30': 0.234 },
  'M': { 'CAT0': 0.0, 'CAT6': 0.00, 'CAT12': 0.01, 'CAT18': 0.02, 'CAT24': 0.03, 'CAT30': 0.04 },
  'SrM': { 'CAT0': 0.0, 'CAT6': 0.00, 'CAT12': 0.005, 'CAT18': 0.01, 'CAT24': 0.015, 'CAT30': 0.02 },
  'Pi': { 'CAT0': 0.0 },
  'P': { 'CAT0': 0.0 },
};

const catLabels = {
  'CAT0': '0-6 months',
  'CAT6': '6-12 months', 
  'CAT12': '12-18 months',
  'CAT18': '18-24 months',
  'CAT24': '24-30 months',
  'CAT30': '30+ months',
};

interface ScenarioLeversProps {
  onNext: () => void;
  onBack: () => void;
}

const ScenarioLevers: React.FC<ScenarioLeversProps> = ({ onNext, onBack }) => {
  const [levers, setLevers] = useState<LeverState>(() =>
    LEVERS.reduce((acc, lever) => {
      acc[lever] = ROLES.reduce((racc, role) => {
        racc[role] = defaultValue;
        return racc;
      }, {} as Record<string, number>);
      return acc;
    }, {} as LeverState)
  );

  const handleSlider = (lever: LeverType, role: string, value: number) => {
    setLevers(prev => ({
      ...prev,
      [lever]: { ...prev[lever], [role]: value },
    }));
  };

  const handleReset = (lever: LeverType) => {
    setLevers(prev => ({
      ...prev,
      [lever]: ROLES.reduce((racc, role) => {
        racc[role] = defaultValue;
        return racc;
      }, {} as Record<string, number>),
    }));
  };

  const getProgressionImpact = (role: string, multiplier: number) => {
    const catData = catProgressionData[role] || {};
    const impact: Record<string, { original: number; adjusted: number }> = {};
    
    Object.entries(catData).forEach(([cat, originalProb]) => {
      impact[cat] = {
        original: originalProb,
        adjusted: Math.min(originalProb * multiplier, 1.0)
      };
    });
    
    return impact;
  };

  const columns = [
    {
      title: 'Role',
      dataIndex: 'role',
      key: 'role',
      width: 100,
      fixed: 'left' as const,
    },
    ...LEVERS.flatMap(lever => [
      {
        title: (
          <Row align="middle" justify="space-between" style={{ width: 200 }}>
            <Col>
              {lever} Multiplier
              {lever === 'Progression' && (
                <Tooltip title="Progression multiplier affects CAT-based progression probabilities. Values < 1 slow progression, > 1 accelerate it.">
                  <InfoCircleOutlined style={{ marginLeft: 4, color: '#1890ff' }} />
                </Tooltip>
              )}
            </Col>
            <Col>
              <Button size="small" onClick={() => handleReset(lever)}>Reset All</Button>
            </Col>
          </Row>
        ),
        dataIndex: lever,
        key: lever,
        width: 250,
        render: (_: any, record: any) => (
          <Space>
            <Slider
              min={min}
              max={max}
              step={step}
              value={levers[lever][record.role]}
              onChange={val => handleSlider(lever, record.role, val as number)}
              style={{ width: 120 }}
            />
            <span style={{ width: 40, display: 'inline-block', textAlign: 'right' }}>{levers[lever][record.role].toFixed(2)}</span>
          </Space>
        ),
      },
      lever !== 'Progression' ? {
        title: `${lever} Actual (per month)`,
        dataIndex: `${lever}-actual`,
        key: `${lever}-actual`,
        width: 100,
        render: (_: any, record: any) => {
          const baseline = baselineValues[lever][record.role] || 0;
          const multiplier = levers[lever][record.role];
          const actual = baseline * multiplier;
          return <span>{actual.toFixed(2)}</span>;
        },
      } : {
        title: 'Max Change',
        dataIndex: 'Progression-max-change',
        key: 'Progression-max-change',
        width: 120,
        render: (_: any, record: any) => {
          const multiplier = levers.Progression[record.role];
          const impact = getProgressionImpact(record.role, multiplier);
          let maxChange = 0;
          let sign = '=';
          Object.values(impact).forEach(({ original, adjusted }) => {
            const diff = adjusted - original;
            if (Math.abs(diff) > Math.abs(maxChange)) {
              maxChange = diff;
              sign = diff > 0 ? '+' : diff < 0 ? '-' : '=';
            }
          });
          const color = maxChange > 0 ? '#52c41a' : maxChange < 0 ? '#ff4d4f' : '#666';
          const formatted = `${sign} ${(Math.abs(maxChange) * 100).toFixed(1)}%`;
          return <span style={{ color, fontWeight: 'bold' }}>{formatted}</span>;
        },
      },
      lever === 'Progression' ? {
        title: 'Expected Time on Level',
        dataIndex: 'Progression-expected-time',
        key: 'Progression-expected-time',
        width: 170,
        render: (_: any, record: any) => {
          const multiplier = levers.Progression[record.role];
          const impact = getProgressionImpact(record.role, multiplier);
          let maxProb = 0;
          let maxOrigProb = 0;
          Object.values(impact).forEach(({ original, adjusted }) => {
            if (adjusted > maxProb) maxProb = adjusted;
            if (original > maxOrigProb) maxOrigProb = original;
          });
          let value = 'N/A';
          let origValue = '';
          if (maxProb > 0) {
            const expectedPeriods = 1 / maxProb;
            const expectedMonths = Math.round(expectedPeriods * 6);
            value = `${expectedMonths} mo`;
            if (multiplier !== 1.0 && maxOrigProb > 0) {
              const origPeriods = 1 / maxOrigProb;
              const origMonths = Math.round(origPeriods * 6);
              origValue = `${origMonths} mo`;
            }
          }
          return (
            <span>
              {value}
              {origValue && (
                <span style={{ color: '#888', fontSize: 12, marginLeft: 4 }}>(was {origValue})</span>
              )}
            </span>
          );
        },
      } : null,
    ]),
  ];
  // Filter out any null columns (from Progression non-matches)
  const filteredColumns = columns.filter(Boolean);

  const dataSource = ROLES.map(role => ({
    key: role,
    role,
    Recruitment: levers.Recruitment[role],
    'Recruitment-actual': baselineValues.Recruitment[role] * levers.Recruitment[role],
    Churn: levers.Churn[role],
    'Churn-actual': baselineValues.Churn[role] * levers.Churn[role],
    Progression: levers.Progression[role],
  }));

  return (
    <div style={{ marginLeft: 24, marginRight: 24 }}>
      <Card title={<Title level={4} style={{ margin: 0 }}>Scenario Levers</Title>}>
        <Table
          columns={filteredColumns}
          dataSource={dataSource}
          pagination={false}
          size="middle"
          bordered
          scroll={{ x: true }}
          style={{ marginBottom: 24 }}
        />
        
        <Space>
          <Button onClick={onBack}>Back</Button>
          <Button type="primary" onClick={onNext}>Next: Results</Button>
        </Space>
      </Card>
    </div>
  );
};

export default ScenarioLevers; 