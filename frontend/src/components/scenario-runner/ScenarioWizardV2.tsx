import React from 'react';
import { ChevronLeft, ChevronRight, X, Save, Play, Loader2 } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Progress } from '../ui/progress';
import ScenarioCreationFormV2 from './ScenarioCreationFormV2';
import BaselineInputGridV2 from './BaselineInputGridV2';
import ScenarioLeversV2 from './ScenarioLeversV2';
import type { ScenarioLeversRef } from './ScenarioLeversV2';
import type { ScenarioDefinition } from '../../types/unified-data-structures';
import ErrorDisplay from '../common/ErrorDisplay';
import { cn } from '../../lib/utils';
import { useScenarioForm } from '../../hooks';

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
  // Use the scenario form hook for all business logic
  const {
    state,
    current,
    steps,
    progressPercentage,
    baselineGridRef,
    leversRef,
    handleDetailsNext,
    handleBaselineNext,
    handleBaselineStepNext,
    handleBack,
    handleLeversSave,
    handleRunSimulation,
    isEditing,
    editingId
  } = useScenarioForm({
    onComplete,
    onCancel,
    initialScenario,
    editingId: propId
  });


  return (
    <div className="w-full p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">
            {isEditing ? 'Edit Scenario' : 'Create New Scenario'}
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

      {/* Main Content - all steps use regular card layout now */}
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
                scenario={state.scenario as ScenarioDefinition}
                onNext={handleDetailsNext}
                onBack={onCancel}
              />
            )}
          
            {current === 1 && (
              <ScenarioLeversV2 
                onNext={handleLeversSave} 
                onBack={handleBack} 
                onRunSimulation={handleRunSimulation}
                ref={leversRef} 
                baselineData={state.baselineData}
                saving={state.saving}
                simulating={state.simulating}
              />
            )}

                {/* Validation Errors */}
                {state.validationErrors.length > 0 && (
                  <div className="mt-4">
                    <ErrorDisplay 
                      error={{ detail: `Validation failed: ${state.validationErrors.join(', ')}` }}
                      onDismiss={() => {}}
                    />
                  </div>
                )}

                {/* Simulation Error */}
                {state.simulationError && (
                  <div className="mt-4">
                    <ErrorDisplay 
                      error={state.simulationError}
                      onRetry={handleRunSimulation}
                      onDismiss={() => {}}
                    />
                  </div>
                )}

            {/* Simulation Results */}
            {state.simulationResult && (
              <Card className="mt-4">
                <CardHeader>
                  <CardTitle className="text-lg">Simulation Results</CardTitle>
                </CardHeader>
                <CardContent>
                  <pre className="bg-muted p-4 rounded-md text-sm overflow-auto max-h-64 text-muted-foreground">
                    {JSON.stringify(state.simulationResult.results, null, 2)}
                  </pre>
                </CardContent>
              </Card>
            )}
          </CardContent>
        </Card>
    </div>
  );
};

export default ScenarioWizardV2;