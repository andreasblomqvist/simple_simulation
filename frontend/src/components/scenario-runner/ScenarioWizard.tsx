import React, { useState } from 'react';
import { Steps, Button, message, Card } from 'antd';
import ScenarioCreationForm from './ScenarioCreationForm';
import BaselineInputGrid from './BaselineInputGrid';
import ScenarioLevers from './ScenarioLevers';
import type { ScenarioDefinition, ScenarioResponse } from '../../types/scenarios';
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
  const [scenarioId, setScenarioId] = useState<string>('');
  const [saving, setSaving] = useState(false);
  const [simulating, setSimulating] = useState(false);
  const [simulationResult, setSimulationResult] = useState<ScenarioResponse | null>(null);
  const [simulationError, setSimulationError] = useState<string | null>(null);

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
      // Create the scenario only at the final step
      const newScenarioId = await scenarioApi.createScenario(scenario as ScenarioDefinition);
      setScenarioId(newScenarioId);
      message.success('Scenario saved!');
      // Do NOT call onComplete here; stay on levers step
    } catch (error) {
      message.error('Failed to save scenario: ' + (error as Error).message);
    } finally {
      setSaving(false);
    }
  };

  // Run Simulation logic
  const handleRunSimulation = async () => {
    setSimulating(true);
    setSimulationError(null);
    setSimulationResult(null);
    try {
      const result = await scenarioApi.runScenarioDefinition(scenario as ScenarioDefinition);
      if (result.status === 'success') {
        setSimulationResult(result);
      } else {
        setSimulationError(result.error_message || 'Simulation failed');
      }
    } catch (error) {
      setSimulationError((error as Error).message);
    } finally {
      setSimulating(false);
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
          <ScenarioLevers onNext={handleRunSimulation} onBack={handleBack} />
          <div style={{ marginTop: 24, textAlign: 'right' }}>
            <Button type="primary" loading={saving} onClick={handleLeversSave}>Save</Button>
          </div>
          {simulating && <div style={{ marginTop: 24 }}>Running simulation...</div>}
          {simulationError && <div style={{ marginTop: 24, color: 'red' }}>{simulationError}</div>}
          {simulationResult && (
            <div style={{ marginTop: 24 }}>
              <h4>Simulation Results</h4>
              <pre style={{ maxHeight: 300, overflow: 'auto', background: '#222', color: '#fff', padding: 12, borderRadius: 4 }}>
                {JSON.stringify(simulationResult.results, null, 2)}
              </pre>
            </div>
          )}
        </>
      )}
    </Card>
  );
};

export default ScenarioWizard; 