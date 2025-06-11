import React, { useState } from 'react';
import { Card, Row, Col, Typography, Select, InputNumber, Button, Divider, message } from 'antd';

const { Title } = Typography;
const { Option } = Select;

const OFFICES = [
  'Stockholm', 'Munich', 'Hamburg', 'Helsinki', 'Oslo', 'Berlin',
  'Copenhagen', 'Zurich', 'Frankfurt', 'Cologne', 'Amsterdam',
  'Toronto', 'London'
];
const LEVELS = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP'];
const LEVERS = [
  { key: 'recruitment', label: 'Recruitment' },
  { key: 'churn', label: 'Churn' },
  { key: 'progression', label: 'Progression' },
  { key: 'utr', label: 'UTR' },
];
const HALVES = ['H1', 'H2'];

// Example simulation state (should be lifted to context or parent in real app)
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

export default function Simulation() {
  // State for lever manipulation
  const [selectedLever, setSelectedLever] = useState('recruitment');
  const [selectedHalf, setSelectedHalf] = useState('H1');
  const [selectedLevel, setSelectedLevel] = useState('AM');
  const [selectedOffices, setSelectedOffices] = useState([] as string[]);
  const [leverValue, setLeverValue] = useState(0.1);
  const [levers, setLevers] = useState<LeversState>(getDefaultLevers());

  // Apply lever value to selected offices/level/half
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
    message.success('Lever value applied!');
  };

  // (Simulation run logic would use the levers state)

  return (
    <Card title={<Title level={4}>Simulation Lever Manipulation</Title>}>
      <Row gutter={16} align="middle">
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
      <Divider />
      {/* (Optional: Show a summary table of current lever values for selected offices/level/half) */}
    </Card>
  );
} 