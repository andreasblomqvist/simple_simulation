import React, { useState } from 'react';
import { Card, Typography, Divider, Button, Steps } from 'antd';
import BaselineInputGrid from '../components/scenario-runner/BaselineInputGrid';
import ScenarioList from '../components/scenario-runner/ScenarioList';
import ScenarioLevers from '../components/scenario-runner/ScenarioLevers';
import ResultsTable from '../components/scenario-runner/ResultsTable';
import ScenarioComparison from '../components/scenario-runner/ScenarioComparison';

const { Title, Paragraph } = Typography;
const { Step } = Steps;

const ScenarioCreationForm = ({ onNext, onBack }: { onNext: () => void, onBack: () => void }) => (
  <Card title="Create New Scenario">
    <Paragraph>Scenario details form (name, description, time range, office scope)...</Paragraph>
    <Button onClick={onBack} style={{ marginRight: 8 }}>Back</Button>
    <Button type="primary" onClick={onNext}>Next: Baseline Input</Button>
  </Card>
);

const steps = [
  { title: 'Scenario List' },
  { title: 'Scenario Creation' },
  { title: 'Baseline Input' },
  { title: 'Scenario Levers' },
  { title: 'Results' },
  { title: 'Comparison' },
];

const ScenarioRunner: React.FC = () => {
  const [current, setCurrent] = useState(0);

  const goTo = (idx: number) => setCurrent(idx);
  const next = () => setCurrent(prev => Math.min(prev + 1, steps.length - 1));
  const prev = () => setCurrent(prev => Math.max(prev - 1, 0));

  // Handler for 'View' button: jump to Scenario Levers step (index 3)
  const handleViewScenario = (id: number) => {
    setCurrent(3);
    // In the future, load scenario data by id here
  };

  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>Scenario Runner</Title>
      <Steps current={current} style={{ marginBottom: 32 }}>
        {steps.map(s => <Step key={s.title} title={s.title} />)}
      </Steps>
      <Divider />
      {current === 0 && (
        <ScenarioList
          onNext={next}
          onEdit={() => {}}
          onDelete={() => {}}
          onCompare={() => {}}
          onExport={() => {}}
          onView={handleViewScenario}
        />
      )}
      {current === 1 && <ScenarioCreationForm onNext={() => next()} onBack={prev} />}
      {current === 2 && (
        <Card title="Step 1: Baseline Input Data" style={{ maxWidth: 1200, margin: '0 auto', marginBottom: 32 }}>
          <BaselineInputGrid />
          <div style={{ textAlign: 'right', marginTop: 24 }}>
            <Button onClick={prev} style={{ marginRight: 8 }}>Back</Button>
            <Button type="primary" size="large" onClick={next}>
              Next: Scenario Levers
            </Button>
          </div>
        </Card>
      )}
      {current === 3 && <ScenarioLevers onNext={next} onBack={prev} />}
      {current === 4 && <ResultsTable onNext={next} onBack={prev} />}
      {current === 5 && <ScenarioComparison onBack={prev} />}
    </div>
  );
};

export default ScenarioRunner; 