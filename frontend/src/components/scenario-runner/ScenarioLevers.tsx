import React, { useState, forwardRef, useImperativeHandle } from 'react';
import { Card, Table, Slider, Button, Space, Typography, Row, Col, Tooltip, Collapse } from 'antd';
import { InfoCircleOutlined } from '@ant-design/icons';
import styles from './ScenarioLevers.module.css';

const { Title, Text } = Typography;
const { Panel } = Collapse;

const ROLES = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P'];
const LEVERS = ['recruitment', 'churn', 'progression'] as const;
const LEVELS = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P'];

type LeverType = typeof LEVERS[number];

type LeverState = Record<LeverType, Record<string, number>>;

const defaultValue = 1.0;
const min = 0.0;
const max = 2.0;
const step = 0.01;

// Mock baseline values for each role and lever
const baselineValues: Record<LeverType, Record<string, number>> = {
  recruitment: { A: 20, AC: 8, C: 4, SrC: 1, AM: 1, M: 0, SrM: 0, Pi: 0, P: 0 },
  churn: { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 0, Pi: 0, P: 0 },
  progression: { A: 1, AC: 1, C: 1, SrC: 1, AM: 1, M: 1, SrM: 1, Pi: 1, P: 1 },
};

// Function to get complete levers data
export function getCompleteLevers(leversData?: any): LeverState {
  if (!leversData || typeof leversData !== 'object') {
    return baselineValues;
  }

  const result: LeverState = {
    recruitment: { ...baselineValues.recruitment },
    churn: { ...baselineValues.churn },
    progression: { ...baselineValues.progression }
  };

  // Process recruitment levers
  if (leversData.recruitment && typeof leversData.recruitment === 'object') {
    Object.entries(leversData.recruitment).forEach(([level, value]) => {
      if (typeof value === 'number' && !isNaN(value)) {
        result.recruitment[level] = value;
      }
    });
  }

  // Process churn levers
  if (leversData.churn && typeof leversData.churn === 'object') {
    Object.entries(leversData.churn).forEach(([level, value]) => {
      if (typeof value === 'number' && !isNaN(value)) {
        result.churn[level] = value;
      }
    });
  }

  // Process progression levers
  if (leversData.progression && typeof leversData.progression === 'object') {
    Object.entries(leversData.progression).forEach(([level, value]) => {
      if (typeof value === 'number' && !isNaN(value)) {
        result.progression[level] = value;
      }
    });
  }

  return result;
}

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
  onNext?: () => void;
  onBack?: () => void;
  levers?: LeverState;
  readOnly?: boolean;
  baselineValues?: Record<LeverType, Record<string, number>>;
  baselineData?: any;
}

export interface ScenarioLeversRef {
  getCurrentData: () => LeverState;
}

const ScenarioLevers = forwardRef<ScenarioLeversRef, ScenarioLeversProps>(({ onNext, onBack, levers: externalLevers, readOnly = false, baselineValues: propBaselineValues, baselineData }, ref) => {
  const [levers, setLevers] = useState<LeverState>(() =>
    externalLevers || baselineValues // Use externalLevers if provided, otherwise fallback to baselineValues
  );
  

  // Expose current data to parent via ref
  useImperativeHandle(ref, () => ({
    getCurrentData: () => {
      console.log('DEBUG: ScenarioLevers getCurrentData called, returning:', levers);
      return levers;
    }
  }));

  // If externalLevers changes, update state
  React.useEffect(() => {
    if (externalLevers) setLevers(externalLevers);
  }, [externalLevers]);

  // Helper function to sanitize lever values
  const sanitizeLeverValue = (value: any): number => {
    if (value === null || value === undefined || value === '' || isNaN(value)) {
      return 1.0;
    }
    const numValue = Number(value);
    return isNaN(numValue) ? 1.0 : Math.max(0, numValue);
  };

  const handleSlider = (lever: LeverType, role: string, value: number) => {
    const sanitizedValue = sanitizeLeverValue(value);
    setLevers(prev => ({
      ...prev,
      [lever]: { ...prev[lever], [role]: sanitizedValue },
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
      title: 'Level',
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
              {lever.charAt(0).toUpperCase() + lever.slice(1)} Multiplier
              {lever === 'progression' && (
                <Tooltip title="Progression multiplier affects CAT-based progression probabilities. Values < 1 slow progression, > 1 accelerate it.">
                  <InfoCircleOutlined style={{ marginLeft: 4, color: '#1890ff' }} />
                </Tooltip>
              )}
            </Col>
            {!readOnly && (
              <Col>
                <Button size="small" onClick={() => handleReset(lever)}>Reset All</Button>
              </Col>
            )}
          </Row>
        ),
        dataIndex: lever,
        key: lever,
        width: 250,
        render: (_: any, record: any) => (
          readOnly ? (
            <span style={{ width: 40, display: 'inline-block', textAlign: 'right' }}>{levers[lever][record.role].toFixed(2)}</span>
          ) : (
            <Space className={styles.leverSlider}>
              <Slider
                min={min}
                max={max}
                step={step}
                value={levers[lever][record.role]}
                onChange={val => handleSlider(lever, record.role, val as number)}
                style={{ width: 120 }}
                trackStyle={{ backgroundColor: '#1890ff', height: 6 }}
                handleStyle={{ borderColor: '#40a9ff', backgroundColor: '#40a9ff' }}
              />
              <span style={{ width: 40, display: 'inline-block', textAlign: 'right' }}>{levers[lever][record.role].toFixed(2)}</span>
            </Space>
          )
        ),
      },
      lever !== 'progression' ? {
        title: `${lever.charAt(0).toUpperCase() + lever.slice(1)} Actual (avg per month)`,
        dataIndex: `${lever}-actual`,
        key: `${lever}-actual`,
        width: 100,
        render: (_: any, record: any) => {
          const baseline = baselineValues[lever][record.role] || 0;
          const multiplier = levers[lever][record.role];
          const actual = baseline * multiplier;
          
          
          let color = '#fff';
          if (multiplier > 1) color = '#52c41a';
          else if (multiplier < 1) color = '#ff4d4f';
          return <span style={{ color, fontWeight: 'bold' }}>{actual.toFixed(2)}</span>;
        },
      } : {
        title: 'Max Change',
        dataIndex: 'progression-max-change',
        key: 'progression-max-change',
        width: 120,
        render: (_: any, record: any) => {
          const multiplier = levers.progression[record.role];
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
      lever === 'progression' ? {
        title: 'Expected Time on Level',
        dataIndex: 'progression-expected-time',
        key: 'progression-expected-time',
        width: 170,
        render: (_: any, record: any) => {
          const multiplier = levers.progression[record.role];
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
  // Filter out any null columns (from progression non-matches)
  const filteredColumns = columns.filter((col): col is NonNullable<typeof col> => col !== null);

  return (
    <div>
      <Table
        columns={filteredColumns}
        dataSource={LEVELS.map(level => ({
          key: level,
          role: level,
          recruitment: levers.recruitment[level],
          'recruitment-actual': baselineValues.recruitment[level] * levers.recruitment[level],
          churn: levers.churn[level],
          'churn-actual': baselineValues.churn[level] * levers.churn[level],
          progression: levers.progression[level],
        }))}
        pagination={false}
        size="middle"
        bordered
        scroll={{ x: true }}
        style={{ marginBottom: 16 }}
      />
      {(!readOnly && (onNext || onBack)) && (
        <div style={{ textAlign: 'right' }}>
          {onBack && <Button onClick={onBack} style={{ marginRight: 8 }}>Back</Button>}
          {onNext && <Button type="primary" onClick={onNext}>Run Simulation</Button>}
        </div>
      )}
    </div>
  );
});

export default ScenarioLevers;
export { baselineValues }; 