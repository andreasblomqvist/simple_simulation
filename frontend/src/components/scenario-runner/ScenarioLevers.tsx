import React, { useState } from 'react';
import { Card, Table, Slider, Button, Space, Typography, Row, Col } from 'antd';

const { Title } = Typography;

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
            <Col>{lever} Multiplier</Col>
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
      {
        title: `${lever} Actual`,
        dataIndex: `${lever}-actual`,
        key: `${lever}-actual`,
        width: 100,
        render: (_: any, record: any) => {
          const baseline = baselineValues[lever][record.role] || 0;
          const multiplier = levers[lever][record.role];
          const actual = baseline * multiplier;
          return <span>{actual.toFixed(2)}</span>;
        },
      },
    ]),
  ];

  const dataSource = ROLES.map(role => ({
    key: role,
    role,
    Recruitment: levers.Recruitment[role],
    'Recruitment-actual': baselineValues.Recruitment[role] * levers.Recruitment[role],
    Churn: levers.Churn[role],
    'Churn-actual': baselineValues.Churn[role] * levers.Churn[role],
    Progression: levers.Progression[role],
    'Progression-actual': baselineValues.Progression[role] * levers.Progression[role],
  }));

  return (
    <Card title={<Title level={4} style={{ margin: 0 }}>Scenario Levers</Title>} style={{ maxWidth: 1200, margin: '0 auto' }}>
      <Table
        columns={columns}
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
  );
};

export default ScenarioLevers; 