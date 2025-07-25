import React, { useState, useRef, useEffect } from 'react';
import { Steps, Button, Card } from 'antd';
import ScenarioCreationForm from './ScenarioCreationForm';
import BaselineInputGrid from './BaselineInputGrid';
import ScenarioLevers from './ScenarioLevers';
import ModernResultsDisplay from './ModernResultsDisplay';
import type { ScenarioLeversRef } from './ScenarioLevers';
import type { ScenarioDefinition, ScenarioResponse, ErrorResponse } from '../../types/unified-data-structures';
import { scenarioApi } from '../../services/scenarioApi';
import { useNavigate, useParams } from 'react-router-dom';
import ErrorDisplay from '../common/ErrorDisplay';
import { showMessage } from '../../utils/message';

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
  id?: string; // Add id prop for editing scenarios
}

const ScenarioWizard: React.FC<ScenarioWizardProps> = ({ onCancel, onComplete, scenario: initialScenario, id: propId }) => {
  const { id: urlId } = useParams<{ id?: string }>();
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

  // Use propId if provided, otherwise use URL param
  const editingId = propId || urlId;

  useEffect(() => {
    if (editingId) {
      scenarioApi.getScenario(editingId).then(data => {
        console.log('[DEBUG] Loaded scenario data:', data);
        console.log('[DEBUG] Scenario data keys:', Object.keys(data));
        console.log('[DEBUG] Scenario data.baseline_input:', data.baseline_input);
        console.log('[DEBUG] Scenario data.definition:', data.definition);
        
        setScenario(data);
        
        // Handle both direct scenario and nested definition structure
        const actualScenario = data?.definition || data;
        console.log('[DEBUG] Actual scenario structure:', actualScenario);
        console.log('[DEBUG] Actual scenario.baseline_input:', actualScenario?.baseline_input);
        
        // If the scenario has baseline_input, set it
        if (actualScenario?.baseline_input) {
          setBaselineData(actualScenario.baseline_input);
          console.log('[DEBUG] Loaded baseline data from scenario:', actualScenario.baseline_input);
        } else {
          console.log('[DEBUG] No baseline_input found in scenario data');
          // Set empty baseline data using new format
          setBaselineData({
            global_data: {
              recruitment: {},
              churn: {}
            }
          });
        }
      });
    }
  }, [editingId]);

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
      console.log('[DEBUG] Setting baseline data from grid:', currentData);
    } else {
      console.log('[DEBUG] No baselineGridRef.current available');
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
        levers: {
          recruitment: leversData.recruitment || {},
          churn: leversData.churn || {},
          progression: leversData.progression || {}
        }
        // Remove progression_config and cat_curves - these are loaded from backend
      } as ScenarioDefinition;
      console.log('[LEVER DEBUG] (SAVE) Full scenario being sent to backend:', scenarioWithData);
      
      // ✅ Validate before saving
      const isValid = await handleValidateScenario(scenarioWithData);
      if (!isValid) {
        return;
      }
      
      if (editingId) {
        await scenarioApi.updateScenario(editingId, scenarioWithData);
        showMessage.success('Scenario updated!');
      } else {
        const newScenarioId = await scenarioApi.createScenario(scenarioWithData);
        setScenarioId(newScenarioId);
        showMessage.success('Scenario created!');
      }
      navigate('/scenario-runner');
    } catch (error) {
      // ✅ Enhanced error display with correlation ID
      try {
        const errorData = JSON.parse((error as Error).message);
        showMessage.error(`Failed to save scenario: ${errorData.detail}`);
        console.error(`Save failed [corr: ${errorData.correlation_id}]:`, error);
      } catch {
        showMessage.error('Failed to save scenario: ' + (error as Error).message);
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
        levers: {
          recruitment: leversData.recruitment || {},
          churn: leversData.churn || {},
          progression: leversData.progression || {}
        }
        // Remove progression_config and cat_curves - these are loaded from backend
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
    <div style={{ position: 'relative', width: '100%' }}>
      {/* Cancel button at top right */}
      <Button onClick={onCancel} style={{ position: 'absolute', top: 8, right: 8, zIndex: 10 }}>Cancel</Button>
      
      {/* Header */}
      <div style={{ padding: '12px 16px', borderBottom: '1px solid #f0f0f0' }}>
        <h2 style={{ margin: 0, fontSize: '18px' }}>Create New Scenario</h2>
      </div>
      
      <Steps current={current} style={{ margin: '16px 16px 24px 16px' }}>
        {steps.map(step => (
          <Step key={step.title} title={step.title} />
        ))}
      </Steps>
      <div style={{ padding: '0 16px' }}>
        {current === 0 && (
          <ScenarioCreationForm
            scenario={scenario as ScenarioDefinition}
            onNext={handleDetailsNext}
            onBack={onCancel}
          />
        )}
        {current === 1 && (
          <>
            <BaselineInputGrid onNext={handleBaselineNext} ref={baselineGridRef} initialData={baselineData} />
            <div style={{ marginTop: 16, textAlign: 'right', paddingBottom: '16px' }}>
              <Button onClick={handleBack} style={{ marginRight: 8 }}>Back</Button>
              <Button type="primary" onClick={handleBaselineStepNext}>Next</Button>
            </div>
          </>
        )}
        {current === 2 && (
          <>
            <ScenarioLevers onNext={handleRunSimulation} onBack={handleBack} ref={leversRef} baselineData={baselineData} />
            <div style={{ marginTop: 16, textAlign: 'right', paddingBottom: '16px' }}>
              <Button type="primary" loading={saving} onClick={handleLeversSave} disabled={saving}>Save</Button>
            </div>
            {simulating && <div style={{ marginTop: 16, paddingBottom: '16px' }}>Running simulation...</div>}
            {validationErrors.length > 0 && (
              <div style={{ marginTop: 16, paddingBottom: '16px' }}>
                <ErrorDisplay 
                  error={{ detail: `Validation failed: ${validationErrors.join(', ')}` }}
                  onDismiss={() => setValidationErrors([])}
                />
              </div>
            )}
            {simulationError && (
              <div style={{ marginTop: 16, paddingBottom: '16px' }}>
                <ErrorDisplay 
                  error={simulationError}
                  onRetry={handleRunSimulation}
                  onDismiss={() => setSimulationError(null)}
                />
              </div>
            )}
            {simulationResult && (
              <div style={{ marginTop: 16, paddingBottom: '16px' }}>
                <h4 style={{ marginBottom: '12px' }}>Simulation Results</h4>
                <ModernResultsDisplay result={simulationResult} />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default ScenarioWizard; 