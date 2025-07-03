import React, { useState } from 'react';
import { Steps, Button, message, Card } from 'antd';
import ScenarioCreationForm from './ScenarioCreationForm';
import BaselineInputGrid from './BaselineInputGrid';
import ScenarioLevers from './ScenarioLevers';
import type { ScenarioDefinition } from '../../types/scenarios';
import { scenarioApi } from '../../services/scenarioApi';

const { Step } = Steps;

const steps = [
  { title: 'Scenario Details' },
  { title: 'Baseline Input' },
  { title: 'Levers' },
];

interface ScenarioWizardProps {
  onCancel: () => void;
  onComplete: () => void;
  scenario?: Partial<ScenarioDefinition> | null;
}

const ScenarioWizard: React.FC<ScenarioWizardProps> = ({ onCancel, onComplete, scenario: initialScenario }) => {
  const [current, setCurrent] = useState(0);
  const [scenario, setScenario] = useState<Partial<ScenarioDefinition>>(initialScenario || {});
  const [saving, setSaving] = useState(false);

  // Step 1: Scenario Details
  const handleDetailsNext = (data: { scenario: ScenarioDefinition }) => {
    setScenario(data.scenario);
    setCurrent(1);
  };

  // Step 2: Baseline Input (editable, but for now just go next)
  const handleBaselineNext = () => {
    setCurrent(2);
  };

  // Step 3: Levers (now final step)
  const handleLeversSave = async () => {
    setSaving(true);
    try {
      await scenarioApi.createScenario(scenario as ScenarioDefinition);
      message.success('Scenario saved!');
      onComplete();
    } catch (error) {
      message.error('Failed to save scenario: ' + (error as Error).message);
    } finally {
      setSaving(false);
    }
  };

  const handleBack = () => {
    setCurrent(current - 1);
  };

  return (
    <Card style={{ margin: 32, position: 'relative' }}>
      {/* Cancel button at top right inside Card */}
      <Button onClick={onCancel} style={{ position: 'absolute', top: 24, right: 32, zIndex: 10 }}>Cancel</Button>
      <Steps current={current} style={{ marginBottom: 32 }}>
        {steps.map(step => (
          <Step key={step.title} title={step.title} />
        ))}
      </Steps>
      {current === 0 && (
        <ScenarioCreationForm
          scenario={scenario as ScenarioDefinition}
          onNext={handleDetailsNext}
          onBack={onCancel}
        />
      )}
      {current === 1 && (
        <>
          <BaselineInputGrid />
          <div style={{ marginTop: 24, textAlign: 'right' }}>
            <Button onClick={handleBack} style={{ marginRight: 8 }}>Back</Button>
            <Button type="primary" onClick={handleBaselineNext}>Next</Button>
          </div>
        </>
      )}
      {current === 2 && (
        <>
          <ScenarioLevers onNext={() => {}} onBack={handleBack} />
          <div style={{ marginTop: 24, textAlign: 'right' }}>
            <Button onClick={handleBack} style={{ marginRight: 8 }}>Back</Button>
            <Button type="primary" loading={saving} onClick={handleLeversSave} style={{ marginRight: 8 }}>Save</Button>
            <Button type="default" onClick={() => {/* Run Simulation logic here */}}>Run Simulation</Button>
          </div>
        </>
      )}
    </Card>
  );
};

export default ScenarioWizard; 