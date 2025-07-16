import React, { useState, useRef, useEffect } from 'react';
import { Steps, Button, message, Card } from 'antd';
import ScenarioCreationForm from './ScenarioCreationForm';
import BaselineInputGrid from './BaselineInputGrid';
import ScenarioLevers from './ScenarioLevers';
import type { ScenarioLeversRef } from './ScenarioLevers';
import type { ScenarioDefinition, ScenarioResponse, ErrorResponse } from '../../types/unified-data-structures';
import { scenarioApi } from '../../services/scenarioApi';
import { useNavigate, useParams } from 'react-router-dom';
import { normalizeBaselineInput } from '../../utils/normalizeBaselineInput';
import ErrorDisplay from '../common/ErrorDisplay';

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
  const { id } = useParams<{ id?: string }>();
  const [current, setCurrent] = useState(0);
  const [scenario, setScenario] = useState<Partial<ScenarioDefinition>>(initialScenario || {});
  const [scenarioId, setScenarioId] = useState<string>('');
  const [saving, setSaving] = useState(false);
  const [simulating, setSimulating] = useState(false);
  const [simulationResult, setSimulationResult] = useState<ScenarioResponse | null>(null);
  const [simulationError, setSimulationError] = useState<ErrorResponse | string | null>(null);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [validationLoading, setValidationLoading] = useState(false);
  const [baselineData, setBaselineData] = useState<any>(null);
  const baselineGridRef = useRef<any>(null);
  const leversRef = useRef<ScenarioLeversRef>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (id) {
      scenarioApi.getScenario(id).then(data => {
        setScenario(data);
      });
    }
  }, [id]);

  // Step 1: Scenario Details
  const handleDetailsNext = (data: { scenario: ScenarioDefinition }) => {
    setScenario(data.scenario);
    setCurrent(1);
  };

  // Step 2: Baseline Input
  const handleBaselineNext = (data: any) => {
    setBaselineData(data);
    setCurrent(2);
  };

  // Step 2: Baseline Input (manual navigation)
  const handleBaselineStepNext = () => {
    if (baselineGridRef.current && baselineGridRef.current.getCurrentData) {
      const currentData = baselineGridRef.current.getCurrentData();
      setBaselineData(currentData);
    }
    setCurrent(2);
  };

  // ✅ Add validation helper
  const handleValidateScenario = async (scenarioData: ScenarioDefinition): Promise<boolean> => {
    setValidationLoading(true);
    setValidationErrors([]);
    
    try {
      const validation = await scenarioApi.validateScenario(scenarioData);
      if (!validation.valid) {
        setValidationErrors(validation.errors);
        return false;
      }
      return true;
    } catch (error) {
      // If validation endpoint doesn't exist yet, continue without validation
      console.warn('Validation endpoint not available, skipping validation');
      return true;
    } finally {
      setValidationLoading(false);
    }
  };

  // Step 3: Levers (now final step)
  const handleLeversSave = async () => {
    if (saving) return; // Prevent duplicate calls
    setSaving(true);
    setValidationErrors([]);
    
    try {
      // Always get the latest baseline data from the grid
      let baselineInput = baselineData;
      if (baselineGridRef.current && baselineGridRef.current.getCurrentData) {
        baselineInput = baselineGridRef.current.getCurrentData();
        baselineInput = normalizeBaselineInput(baselineInput);
        console.log('[LEVER DEBUG] (SAVE) baselineGridRef.current.getCurrentData() returned:', baselineInput);
      } else {
        console.log('[LEVER DEBUG] (SAVE) baselineGridRef.current is null or getCurrentData not available for save');
      }
      // Always get the latest levers data
      let leversData = {};
      if (leversRef.current && leversRef.current.getCurrentData) {
        leversData = leversRef.current.getCurrentData();
        console.log('[LEVER DEBUG] (SAVE) leversRef.current.getCurrentData() returned:', leversData);
      } else {
        console.log('[LEVER DEBUG] (SAVE) leversRef.current is null or getCurrentData not available for save');
      }
      const scenarioWithData = {
        ...scenario,
        description: scenario.description || 'No description provided', // ✅ Ensure description
        baseline_input: baselineInput,
        levers: leversData
      } as ScenarioDefinition;
      console.log('[LEVER DEBUG] (SAVE) Full scenario being sent to backend:', scenarioWithData);
      
      // ✅ Validate before saving
      const isValid = await handleValidateScenario(scenarioWithData);
      if (!isValid) {
        return;
      }
      
      if (id) {
        await scenarioApi.updateScenario(id, scenarioWithData);
        message.success('Scenario updated!');
      } else {
        const newScenarioId = await scenarioApi.createScenario(scenarioWithData);
        setScenarioId(newScenarioId);
        message.success('Scenario created!');
      }
      navigate('/scenario-runner');
    } catch (error) {
      // ✅ Enhanced error display with correlation ID
      try {
        const errorData = JSON.parse((error as Error).message);
        message.error(`Failed to save scenario: ${errorData.detail}`);
        console.error(`Save failed [corr: ${errorData.correlation_id}]:`, error);
      } catch {
        message.error('Failed to save scenario: ' + (error as Error).message);
      }
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
      // Always get the latest baseline data from the grid
      let baselineInput = baselineData;
      if (baselineGridRef.current && baselineGridRef.current.getCurrentData) {
        baselineInput = baselineGridRef.current.getCurrentData();
        baselineInput = normalizeBaselineInput(baselineInput);
        console.log('[LEVER DEBUG] baselineGridRef.current.getCurrentData() returned:', baselineInput);
      } else {
        console.log('[LEVER DEBUG] baselineGridRef.current is null or getCurrentData not available for simulation');
      }
      // Always get the latest levers data
      let leversData = {};
      if (leversRef.current && leversRef.current.getCurrentData) {
        leversData = leversRef.current.getCurrentData();
        console.log('[LEVER DEBUG] leversRef.current.getCurrentData() returned:', leversData);
      } else {
        console.log('[LEVER DEBUG] leversRef.current is null or getCurrentData not available for simulation');
      }
      const scenarioWithData = {
        ...scenario,
        description: scenario.description || 'No description provided', // ✅ Ensure description
        baseline_input: baselineInput,
        levers: leversData
      } as ScenarioDefinition;
      console.log('[LEVER DEBUG] Full scenario being sent to backend for simulation:', scenarioWithData);
      const result = await scenarioApi.runScenarioDefinition(scenarioWithData);
      if (result.status === 'success') {
        setSimulationResult(result);
      } else {
        setSimulationError(result.error_message || 'Simulation failed');
      }
    } catch (error) {
      // ✅ Enhanced error handling with correlation ID
      try {
        const errorData = JSON.parse((error as Error).message);
        setSimulationError(errorData);
      } catch {
        setSimulationError((error as Error).message);
      }
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
          <BaselineInputGrid onNext={handleBaselineNext} ref={baselineGridRef} />
          <div style={{ marginTop: 24, textAlign: 'right' }}>
            <Button onClick={handleBack} style={{ marginRight: 8 }}>Back</Button>
            <Button type="primary" onClick={handleBaselineStepNext}>Next</Button>
          </div>
        </>
      )}
      {current === 2 && (
        <>
          <ScenarioLevers onNext={handleRunSimulation} onBack={handleBack} ref={leversRef} />
          <div style={{ marginTop: 24, textAlign: 'right' }}>
            <Button type="primary" loading={saving} onClick={handleLeversSave} disabled={saving}>Save</Button>
          </div>
          {simulating && <div style={{ marginTop: 24 }}>Running simulation...</div>}
          {validationErrors.length > 0 && (
            <div style={{ marginTop: 16 }}>
              <ErrorDisplay 
                error={{ detail: `Validation failed: ${validationErrors.join(', ')}` }}
                onDismiss={() => setValidationErrors([])}
              />
            </div>
          )}
          {simulationError && (
            <div style={{ marginTop: 16 }}>
              <ErrorDisplay 
                error={simulationError}
                onRetry={handleRunSimulation}
                onDismiss={() => setSimulationError(null)}
              />
            </div>
          )}
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