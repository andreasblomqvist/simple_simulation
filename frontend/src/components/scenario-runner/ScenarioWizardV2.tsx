import React, { useState, useRef, useEffect } from 'react';
import { ChevronLeft, ChevronRight, X, Save, Play, Loader2 } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Progress } from '../ui/progress';
import ScenarioCreationFormV2 from './ScenarioCreationFormV2';
import BaselineInputGridV2 from './BaselineInputGridV2';
import ScenarioLeversV2 from './ScenarioLeversV2';
import type { ScenarioLeversRef } from './ScenarioLeversV2';
import type { ScenarioDefinition, ScenarioResponse, ErrorResponse } from '../../types/unified-data-structures';
import { scenarioApi } from '../../services/scenarioApi';
import { useNavigate, useParams } from 'react-router-dom';
import ErrorDisplay from '../common/ErrorDisplay';
import { showMessage } from '../../utils/message';
import { cn } from '../../lib/utils';

const steps = [
  { 
    title: 'Scenario Details',
    description: 'Define basic scenario information'
  },
  { 
    title: 'Baseline Input',
    description: 'Configure initial parameters'
  },
  { 
    title: 'Levers',
    description: 'Set scenario adjustments and run simulation'
  },
];

interface ScenarioWizardV2Props {
  onCancel: () => void;
  onComplete: () => void;
  scenario?: Partial<ScenarioDefinition> | null;
  id?: string;
}

const ScenarioWizardV2: React.FC<ScenarioWizardV2Props> = ({ 
  onCancel, 
  onComplete, 
  scenario: initialScenario, 
  id: propId 
}) => {
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

  const editingId = propId || urlId;

  useEffect(() => {
    if (editingId) {
      scenarioApi.getScenario(editingId).then(data => {
        console.log('[DEBUG] Loaded scenario data:', data);
        setScenario(data);
        
        const actualScenario = data?.definition || data;
        
        if (actualScenario?.baseline_input) {
          setBaselineData(actualScenario.baseline_input);
        } else {
          setBaselineData({
            global: {
              recruitment: {},
              churn: {}
            }
          });
        }
      });
    }
  }, [editingId]);

  const handleDetailsNext = (data: { scenario: ScenarioDefinition }) => {
    setScenario(data.scenario);
    setCurrent(1);
  };

  const handleBaselineNext = (data: any) => {
    setBaselineData(data);
    setCurrent(2);
  };

  const handleBaselineStepNext = () => {
    if (baselineGridRef.current && baselineGridRef.current.getCurrentData) {
      const currentData = baselineGridRef.current.getCurrentData();
      setBaselineData(currentData);
    }
    setCurrent(2);
  };

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
      console.warn('Validation endpoint not available, skipping validation');
      return true;
    } finally {
      setValidationLoading(false);
    }
  };

  const handleLeversSave = async () => {
    if (saving) return;
    setSaving(true);
    setValidationErrors([]);
    
    try {
      let baselineInput = baselineData || {
        global: {
          recruitment: {},
          churn: {}
        }
      };
      if (baselineGridRef.current && baselineGridRef.current.getCurrentData) {
        const gridData = baselineGridRef.current.getCurrentData();
        // Use the grid data if it exists and is properly structured
        if (gridData && gridData.global) {
          baselineInput = gridData;
        }
      }
      
      let leversData = {};
      if (leversRef.current && leversRef.current.getCurrentData) {
        leversData = leversRef.current.getCurrentData();
      }
      
      const scenarioWithData = {
        ...scenario,
        description: scenario.description || 'No description provided',
        baseline_input: baselineInput,
        levers: {
          recruitment: leversData.recruitment || {},
          churn: leversData.churn || {},
          progression: leversData.progression || {}
        },
        economic_params: scenario.economic_params || {}
      } as ScenarioDefinition;
      
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
      
      onComplete();
    } catch (error) {
      try {
        const errorData = JSON.parse((error as Error).message);
        showMessage.error(`Failed to save scenario: ${errorData.detail}`);
      } catch {
        showMessage.error('Failed to save scenario: ' + (error as Error).message);
      }
    } finally {
      setSaving(false);
    }
  };

  const handleRunSimulation = async () => {
    setSimulating(true);
    setSimulationError(null);
    setSimulationResult(null);
    
    try {
      let baselineInput = baselineData || {
        global: {
          recruitment: {},
          churn: {}
        }
      };
      if (baselineGridRef.current && baselineGridRef.current.getCurrentData) {
        const gridData = baselineGridRef.current.getCurrentData();
        // Use the grid data if it exists and is properly structured
        if (gridData && gridData.global) {
          baselineInput = gridData;
        }
      }
      
      let leversData = {};
      if (leversRef.current && leversRef.current.getCurrentData) {
        leversData = leversRef.current.getCurrentData();
      }
      
      const scenarioWithData = {
        ...scenario,
        description: scenario.description || 'No description provided',
        baseline_input: baselineInput,
        levers: {
          recruitment: leversData.recruitment || {},
          churn: leversData.churn || {},
          progression: leversData.progression || {}
        },
        economic_params: scenario.economic_params || {}
      } as ScenarioDefinition;
      
      const result = await scenarioApi.runScenarioDefinition(scenarioWithData);
      if (result.status === 'success') {
        setSimulationResult(result);
      } else {
        setSimulationError(result.error_message || 'Simulation failed');
      }
    } catch (error) {
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

  const progressPercentage = ((current + 1) / steps.length) * 100;

  return (
    <div className="w-full p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">
            {editingId ? 'Edit Scenario' : 'Create New Scenario'}
          </h2>
          <p className="text-muted-foreground">
            {steps[current].description}
          </p>
        </div>
        <Button variant="ghost" size="sm" onClick={onCancel}>
          <X className="h-4 w-4 mr-2" />
          Cancel
        </Button>
      </div>

      {/* Progress */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          {steps.map((step, index) => (
            <span 
              key={step.title}
              className={cn(
                "font-medium",
                index <= current ? "text-primary" : "text-muted-foreground"
              )}
            >
              {step.title}
            </span>
          ))}
        </div>
        <Progress value={progressPercentage} className="h-2" />
      </div>

      {/* Main Content */}
      {current === 1 ? (
        // Full-width baseline input step
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <span className="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-primary-foreground text-sm font-medium">
                  {current + 1}
                </span>
                <span>{steps[current].title}</span>
              </CardTitle>
            </CardHeader>
          </Card>
          <BaselineInputGridV2 
            onNext={handleBaselineNext} 
            ref={baselineGridRef} 
            initialData={baselineData} 
          />
          <div className="flex justify-between pt-4 px-6">
            <Button variant="outline" onClick={handleBack}>
              <ChevronLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <Button onClick={handleBaselineStepNext}>
              Next
              <ChevronRight className="h-4 w-4 ml-2" />
            </Button>
          </div>
        </div>
      ) : (
        // Regular card layout for other steps
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <span className="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-primary-foreground text-sm font-medium">
                {current + 1}
              </span>
              <span>{steps[current].title}</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {current === 0 && (
              <ScenarioCreationFormV2
                scenario={scenario as ScenarioDefinition}
                onNext={handleDetailsNext}
                onBack={onCancel}
              />
            )}
          
            {current === 2 && (
              <>
                <ScenarioLeversV2 
                  onNext={handleRunSimulation} 
                  onBack={handleBack} 
                  ref={leversRef} 
                  baselineData={baselineData} 
                />
                
                <div className="flex justify-between pt-4">
                  <Button variant="outline" onClick={handleBack}>
                    <ChevronLeft className="h-4 w-4 mr-2" />
                    Back
                  </Button>
                  <div className="space-x-2">
                    <Button 
                      onClick={handleRunSimulation}
                      disabled={simulating}
                      variant="secondary"
                    >
                      {simulating ? (
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      ) : (
                        <Play className="h-4 w-4 mr-2" />
                      )}
                      Run Simulation
                    </Button>
                    <Button 
                      onClick={handleLeversSave}
                      disabled={saving || validationLoading}
                    >
                      {saving || validationLoading ? (
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      ) : (
                        <Save className="h-4 w-4 mr-2" />
                      )}
                      Save Scenario
                    </Button>
                  </div>
                </div>

                {/* Validation Errors */}
                {validationErrors.length > 0 && (
                  <div className="mt-4">
                    <ErrorDisplay 
                      error={{ detail: `Validation failed: ${validationErrors.join(', ')}` }}
                      onDismiss={() => setValidationErrors([])}
                    />
                  </div>
                )}

                {/* Simulation Error */}
                {simulationError && (
                  <div className="mt-4">
                    <ErrorDisplay 
                      error={simulationError}
                      onRetry={handleRunSimulation}
                      onDismiss={() => setSimulationError(null)}
                    />
                  </div>
                )}

                {/* Simulation Results */}
                {simulationResult && (
                  <Card className="mt-4">
                    <CardHeader>
                      <CardTitle className="text-lg">Simulation Results</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <pre className="bg-muted p-4 rounded-md text-sm overflow-auto max-h-64 text-muted-foreground">
                        {JSON.stringify(simulationResult.results, null, 2)}
                      </pre>
                    </CardContent>
                  </Card>
                )}
              </>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ScenarioWizardV2;