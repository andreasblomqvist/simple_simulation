import React, { useState } from 'react';
import { Card, Typography, Divider, Tabs, Form, Input, Button } from 'antd';
import BaselineInputGrid from '../components/scenario-runner/BaselineInputGrid';
import ScenarioList from '../components/scenario-runner/ScenarioList';
import ScenarioLevers from '../components/scenario-runner/ScenarioLevers';
import ResultsTable from '../components/scenario-runner/ResultsTable';
import ScenarioComparison from '../components/scenario-runner/ScenarioComparison';

const { Title } = Typography;
const { TabPane } = Tabs;

const ScenarioCreationForm = () => (
  <div style={{ marginLeft: 24, marginRight: 24 }}>
    <Form layout="vertical">
      <Form.Item label="Scenario Name" required>
        <Input placeholder="Enter scenario name" />
      </Form.Item>
      <Form.Item label="Description">
        <Input.TextArea placeholder="Describe this scenario (optional)" rows={3} />
      </Form.Item>
      <Form.Item label="Time Range" required>
        <Input placeholder="e.g. 2025-2030" />
      </Form.Item>
      <Form.Item label="Office Scope" required>
        <Input placeholder="e.g. Group, Stockholm, Munich" />
      </Form.Item>
      <Button type="primary">Save Scenario</Button>
    </Form>
  </div>
);

const cardStyle = { marginTop: 16 };
const cardBodyStyle = { padding: '12px 0 0 0' };

const ScenarioRunner: React.FC = () => {
  const [activeKey, setActiveKey] = useState('list');

  // Handler for 'View' button: jump to Levers & Results tab
  const handleViewScenario = (id: number) => {
    setActiveKey('levers');
    // In the future, load scenario data by id here
  };

  return (
    <div style={{ marginTop: 16, padding: '0 24px 24px 24px' }}>
      <Title level={2}>Scenario Runner</Title>
      <Tabs activeKey={activeKey} onChange={setActiveKey} type="card" style={{ marginBottom: 32 }}>
        <TabPane tab="Scenarios" key="list">
          <div style={{ marginLeft: 24, marginRight: 24 }}>
            <ScenarioList
              onNext={() => setActiveKey('create')}
              onEdit={() => {}}
              onDelete={() => {}}
              onCompare={() => setActiveKey('compare')}
              onExport={() => {}}
              onView={handleViewScenario}
            />
          </div>
        </TabPane>
        <TabPane tab="Scenario Creation" key="create">
          <ScenarioCreationForm />
        </TabPane>
        <TabPane tab="Baseline Input" key="baseline">
          <div style={{ marginLeft: 24, marginRight: 24, marginTop: 16 }}>
            <BaselineInputGrid />
          </div>
        </TabPane>
        <TabPane tab="Levers & Results" key="levers">
          <div style={{ marginLeft: 24, marginRight: 24, marginTop: 16 }}>
            <ScenarioLevers onNext={() => {}} onBack={() => {}} />
            <Divider />
            <ResultsTable onNext={() => {}} onBack={() => {}} />
          </div>
        </TabPane>
        <TabPane tab="Comparison" key="compare">
          <div style={{ marginLeft: 24, marginRight: 24, marginTop: 16 }}>
            <ScenarioComparison onBack={() => {}} />
          </div>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default ScenarioRunner; 