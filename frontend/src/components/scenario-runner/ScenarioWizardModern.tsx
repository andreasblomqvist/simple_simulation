import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Label } from '../ui/label';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../ui/tabs';
import { Checkbox } from '../ui/checkbox';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import { Slider } from '../ui/slider';
import { Progress } from '../ui/progress';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { Separator } from '../ui/separator';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import type { ScenarioDefinition, ScenarioResponse, ErrorResponse, OfficeName } from '../../types/unified-data-structures';
import { scenarioApi } from '../../services/scenarioApi';
import ErrorDisplay from '../common/ErrorDisplay';
import { showMessage } from '../../utils/message';
import { 
  CheckCircle2, 
  ChevronRight, 
  ChevronLeft,
  Clock, 
  Users, 
  Settings, 
  AlertCircle, 
  Info, 
  Loader2,
  FileText,
  BarChart3,
  Play,
  Save,
  X
} from 'lucide-react';

interface ScenarioWizardModernProps {
  onCancel: () => void;
  onComplete: () => void;
  scenario?: Partial<ScenarioDefinition> | null;
  id?: string;
}

const steps = [
  { 
    id: 'details',
    title: 'Scenario Details',
    description: 'Configure basic scenario information',
    icon: FileText
  },
  { 
    id: 'baseline',
    title: 'Baseline Input',
    description: 'Set recruitment and churn data',
    icon: BarChart3
  },
  { 
    id: 'levers',
    title: 'Scenario Levers',
    description: 'Configure multipliers and run simulation',
    icon: Settings
  },
];

const ScenarioWizardModern: React.FC<ScenarioWizardModernProps> = ({ 
  onCancel, 
  onComplete, 
  scenario: initialScenario, 
  id: propId 
}) => {
  const { id: urlId } = useParams<{ id?: string }>();
  const navigate = useNavigate();
  
  // State management
  const [currentStep, setCurrentStep] = useState(0);
  const [scenario, setScenario] = useState<Partial<ScenarioDefinition>>(initialScenario || {});
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [simulating, setSimulating] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [availableOffices, setAvailableOffices] = useState<OfficeName[]>([]);
  const [baselineData, setBaselineData] = useState<any>(null);
  const [simulationResult, setSimulationResult] = useState<ScenarioResponse | null>(null);
  const [simulationError, setSimulationError] = useState<ErrorResponse | string | null>(null);
  const [leversData, setLeversData] = useState<any>({
    recruitment: {},
    churn: {},
    progression: {}
  });

  // Form data for step 1
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    startYear: 2025,
    startMonth: 1,
    endYear: 2027,
    endMonth: 12,
    officeScope: 'group' as 'group' | 'individual',
    selectedOffices: [] as OfficeName[]
  });

  const editingId = propId || urlId;

  // Load scenario data and offices
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        // Load available offices
        const offices = await scenarioApi.getAvailableOffices();
        setAvailableOffices(offices);

        // Load scenario if editing
        if (editingId) {
          const data = await scenarioApi.getScenario(editingId);
          setScenario(data);
          
          // Set form data
          const actualScenario = data?.definition || data;
          setFormData({
            name: actualScenario.name || '',
            description: actualScenario.description || '',
            startYear: actualScenario.time_range?.start_year || 2025,
            startMonth: actualScenario.time_range?.start_month || 1,
            endYear: actualScenario.time_range?.end_year || 2027,
            endMonth: actualScenario.time_range?.end_month || 12,
            officeScope: actualScenario.office_scope?.includes('Group') ? 'group' : 'individual',
            selectedOffices: actualScenario.office_scope?.filter(office => office !== 'Group') || []
          });

          // Set baseline data
          if (actualScenario?.baseline_input) {
            setBaselineData(actualScenario.baseline_input);
          }

          // Set levers data
          if (actualScenario?.levers) {
            setLeversData(actualScenario.levers);
          }
        }
      } catch (error) {
        setErrors(['Failed to load data: ' + (error as Error).message]);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [editingId]);

  // Step navigation
  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  // Step 1: Validate and proceed
  const handleDetailsNext = () => {
    const newErrors: string[] = [];
    
    if (!formData.name.trim()) {
      newErrors.push('Scenario name is required');
    }
    
    if (formData.startYear >= formData.endYear) {
      newErrors.push('End year must be after start year');
    }
    
    if (formData.officeScope === 'individual' && formData.selectedOffices.length === 0) {
      newErrors.push('Please select at least one office');
    }

    if (newErrors.length > 0) {
      setErrors(newErrors);
      return;
    }

    setErrors([]);
    nextStep();
  };

  // Save scenario
  const handleSave = async () => {
    if (saving) return;
    
    setSaving(true);
    setErrors([]);
    setValidationErrors([]);
    
    try {
      const timeRange = {
        start_year: formData.startYear,
        start_month: formData.startMonth,
        end_year: formData.endYear,
        end_month: formData.endMonth,
      };

      const officeScope = formData.officeScope === 'group' 
        ? ['Group'] 
        : formData.selectedOffices;

      const scenarioDefinition: ScenarioDefinition = {
        name: formData.name,
        description: formData.description || 'No description provided',
        time_range: timeRange,
        office_scope: officeScope,
        baseline_input: baselineData || { global: { recruitment: {}, churn: {} } },
        levers: leversData,
        economic_params: {},
      };

      // Validate scenario
      try {
        const validation = await scenarioApi.validateScenario(scenarioDefinition);
        if (!validation.valid) {
          setValidationErrors(validation.errors);
          return;
        }
      } catch (error) {
        console.warn('Validation endpoint not available, skipping validation');
      }

      if (editingId) {
        await scenarioApi.updateScenario(editingId, scenarioDefinition);
        showMessage.success('Scenario updated successfully!');
      } else {
        await scenarioApi.createScenario(scenarioDefinition);
        showMessage.success('Scenario created successfully!');
      }
      
      navigate('/scenario-runner');
    } catch (error) {
      try {
        const errorData = JSON.parse((error as Error).message);
        setErrors([`Failed to save scenario: ${errorData.detail}`]);
      } catch {
        setErrors(['Failed to save scenario: ' + (error as Error).message]);
      }
    } finally {
      setSaving(false);
    }
  };

  // Run simulation
  const handleRunSimulation = async () => {
    setSimulating(true);
    setSimulationError(null);
    setSimulationResult(null);
    
    try {
      const timeRange = {
        start_year: formData.startYear,
        start_month: formData.startMonth,
        end_year: formData.endYear,
        end_month: formData.endMonth,
      };

      const officeScope = formData.officeScope === 'group' 
        ? ['Group'] 
        : formData.selectedOffices;

      const scenarioDefinition: ScenarioDefinition = {
        name: formData.name,
        description: formData.description || 'No description provided',
        time_range: timeRange,
        office_scope: officeScope,
        baseline_input: baselineData || { global: { recruitment: {}, churn: {} } },
        levers: leversData,
        economic_params: {},
      };

      const result = await scenarioApi.runScenarioDefinition(scenarioDefinition);
      if (result.status === 'success') {
        setSimulationResult(result);
        showMessage.success('Simulation completed successfully!');
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

  if (loading) {
    return (
      <div className="w-full max-w-4xl mx-auto px-4 py-8">
        <Card className="border-0 shadow-md">
          <CardContent className="flex items-center justify-center py-16">
            <div className="text-center space-y-4">
              <LoadingSpinner className="mx-auto h-8 w-8 text-primary" />
              <p className="text-sm text-muted-foreground font-medium">Loading scenario data...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="w-full max-w-6xl mx-auto px-4 py-6 space-y-8">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div className="space-y-2">
          <h1 className="text-2xl font-bold tracking-tight text-foreground">
            {editingId ? 'Edit Scenario' : 'Create New Scenario'}
          </h1>
          <p className="text-sm text-muted-foreground leading-relaxed">
            {steps[currentStep].description}
          </p>
        </div>
        <Button 
          variant="outline" 
          onClick={onCancel} 
          size="default"
          className="w-fit lg:w-auto"
        >
          <X className="w-4 h-4 mr-2" />
          Cancel
        </Button>
      </div>

      {/* Progress Indicator */}
      <Card className="border-0 shadow-sm bg-muted/30">
        <CardContent className="p-6">
          <div className="space-y-6">
            {/* Step indicators */}
            <div className="flex items-center justify-between">
              {steps.map((step, index) => {
                const StepIcon = step.icon;
                const isActive = index === currentStep;
                const isCompleted = index < currentStep;
                
                return (
                  <div key={step.id} className="flex items-center flex-1">
                    <div className="flex flex-col items-center space-y-3 flex-1">
                      {/* Icon circle */}
                      <div className={`
                        flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all duration-300
                        ${isCompleted 
                          ? 'bg-primary border-primary text-primary-foreground shadow-sm' 
                          : isActive
                          ? 'bg-background border-primary text-primary shadow-sm ring-2 ring-primary/20' 
                          : 'border-border text-muted-foreground bg-background'
                        }
                      `}>
                        {isCompleted ? (
                          <CheckCircle2 className="w-5 h-5" />
                        ) : (
                          <StepIcon className="w-5 h-5" />
                        )}
                      </div>
                      
                      {/* Step info */}
                      <div className="text-center max-w-24">
                        <p className={`text-xs font-medium leading-tight ${
                          isActive ? 'text-primary' : isCompleted ? 'text-primary' : 'text-muted-foreground'
                        }`}>
                          {step.title}
                        </p>
                      </div>
                    </div>
                    
                    {/* Connector line */}
                    {index < steps.length - 1 && (
                      <div className="flex-1 px-4">
                        <div className={`h-px transition-all duration-300 ${
                          index < currentStep ? 'bg-primary' : 'bg-border'
                        }`} />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
            
            {/* Progress bar */}
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-xs font-medium text-muted-foreground">
                  Step {currentStep + 1} of {steps.length}
                </span>
                <span className="text-xs font-medium text-muted-foreground">
                  {Math.round(((currentStep + 1) / steps.length) * 100)}% Complete
                </span>
              </div>
              <Progress 
                value={((currentStep + 1) / steps.length) * 100} 
                className="w-full h-2" 
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Error Display */}
      {(errors.length > 0 || validationErrors.length > 0) && (
        <Alert variant="destructive" className="border-destructive/20 bg-destructive/10">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            <div className="space-y-3">
              <h4 className="font-medium text-sm">Please correct the following issues:</h4>
              <ul className="space-y-1 text-xs">
                {[...errors, ...validationErrors].map((error, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="block w-1 h-1 rounded-full bg-destructive mt-1.5 flex-shrink-0" />
                    {error}
                  </li>
                ))}
              </ul>
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Step Content */}
      <Card className="border-0 shadow-md">
        <CardHeader className="pb-6 border-b border-border/50">
          <div className="flex items-center gap-4">
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-primary/10 text-primary">
              {React.createElement(steps[currentStep].icon, { className: "w-4 h-4" })}
            </div>
            <div>
              <CardTitle className="text-lg font-semibold text-foreground">
                {steps[currentStep].title}
              </CardTitle>
              <p className="text-sm text-muted-foreground mt-1">
                {steps[currentStep].description}
              </p>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-6">
          {currentStep === 0 && (
            <ScenarioDetailsStep 
              formData={formData}
              setFormData={setFormData}
              availableOffices={availableOffices}
            />
          )}
          {currentStep === 1 && (
            <BaselineInputStep
              data={baselineData}
              onChange={setBaselineData}
            />
          )}
          {currentStep === 2 && (
            <div className="space-y-6">
              <ScenarioLeversStep
                data={leversData}
                onChange={setLeversData}
                baselineData={baselineData}
              />
              
              {/* Simulation Actions */}
              <Card className="bg-primary/5 border-primary/20">
                <CardHeader className="pb-4">
                  <CardTitle className="text-base font-medium flex items-center gap-2 text-foreground">
                    <Play className="w-4 h-4 text-primary" />
                    Test Your Scenario
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-3">
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      Run a simulation to preview the results before saving your scenario.
                    </p>
                    <Button
                      onClick={handleRunSimulation}
                      disabled={simulating}
                      className="w-full sm:w-auto"
                      variant="default"
                      size="default"
                    >
                      {simulating ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Running Simulation...
                        </>
                      ) : (
                        <>
                          <Play className="w-4 h-4 mr-2" />
                          Run Simulation
                        </>
                      )}
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Simulation Results */}
              {simulationError && (
                <Alert variant="destructive" className="border-destructive/20 bg-destructive/10">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    <div className="space-y-3">
                      <h4 className="font-medium text-sm">Simulation Error</h4>
                      <ErrorDisplay 
                        error={simulationError}
                        onRetry={handleRunSimulation}
                        onDismiss={() => setSimulationError(null)}
                      />
                    </div>
                  </AlertDescription>
                </Alert>
              )}

              {simulationResult && (
                <Card className="border-0 bg-green-50/50 dark:bg-green-950/20 border-green-200 dark:border-green-800">
                  <CardHeader className="pb-4">
                    <CardTitle className="text-base font-medium flex items-center gap-2 text-green-700 dark:text-green-400">
                      <CheckCircle2 className="w-4 h-4" />
                      Simulation Completed Successfully
                    </CardTitle>
                    <p className="text-sm text-muted-foreground mt-1">
                      Review the results below, then save your scenario to continue.
                    </p>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="bg-background rounded-lg border p-4 max-h-96 overflow-auto">
                      <pre className="text-xs text-foreground whitespace-pre-wrap font-mono">
                        {JSON.stringify(simulationResult.results, null, 2)}
                      </pre>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </CardContent>
        <CardFooter className="bg-muted/20 border-t border-border/50 px-6 py-4">
          <div className="flex justify-between items-center w-full">
            <Button
              variant="outline"
              onClick={prevStep}
              disabled={currentStep === 0}
              size="default"
              className="min-w-24"
            >
              {currentStep === 0 ? (
                'Start'
              ) : (
                <>
                  <ChevronLeft className="w-4 h-4 mr-2" />
                  Back
                </>
              )}
            </Button>
            
            <div className="flex gap-3">
              {currentStep < steps.length - 1 && (
                <Button 
                  onClick={currentStep === 0 ? handleDetailsNext : nextStep}
                  size="default"
                  className="min-w-24"
                >
                  Next
                  <ChevronRight className="w-4 h-4 ml-2" />
                </Button>
              )}
              {currentStep === steps.length - 1 && (
                <Button 
                  onClick={handleSave} 
                  disabled={saving}
                  size="default"
                  className="min-w-32"
                >
                  {saving ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="w-4 h-4 mr-2" />
                      Save Scenario
                    </>
                  )}
                </Button>
              )}
            </div>
          </div>
        </CardFooter>
      </Card>
    </div>
  );
};

// Step 1: Scenario Details Component
const ScenarioDetailsStep: React.FC<{
  formData: any;
  setFormData: (data: any) => void;
  availableOffices: OfficeName[];
}> = ({ formData, setFormData, availableOffices }) => {
  const updateFormData = (field: string, value: any) => {
    setFormData({ ...formData, [field]: value });
  };

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  return (
    <div className="space-y-8">
      {/* Basic Information */}
      <div className="space-y-6">
        <div className="space-y-3">
          <Label htmlFor="name" className="text-sm font-medium text-foreground">
            Scenario Name <span className="text-destructive">*</span>
          </Label>
          <Input
            id="name"
            value={formData.name}
            onChange={(e) => updateFormData('name', e.target.value)}
            placeholder="e.g. Oslo Growth Plan 2025-2027"
            className="text-sm"
            required
          />
          <p className="text-xs text-muted-foreground leading-relaxed">
            Choose a descriptive name that clearly identifies this scenario
          </p>
        </div>

        <div className="space-y-3">
          <Label htmlFor="description" className="text-sm font-medium text-foreground">
            Description
          </Label>
          <Textarea
            id="description"
            value={formData.description}
            onChange={(e) => updateFormData('description', e.target.value)}
            placeholder="Describe the purpose, assumptions, and objectives of this scenario..."
            rows={3}
            className="text-sm resize-none"
          />
          <p className="text-xs text-muted-foreground leading-relaxed">
            Optional: Provide context about this scenario's objectives and key assumptions
          </p>
        </div>
      </div>

      <Separator />

      {/* Time Range */}
      <div className="space-y-6">
        <div className="space-y-3">
          <Label className="text-sm font-medium text-foreground flex items-center gap-2">
            <Clock className="w-4 h-4 text-primary" />
            Time Range <span className="text-destructive">*</span>
          </Label>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Define the simulation period for your scenario (typically 2-3 years)
          </p>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="p-5 space-y-4 bg-green-50/50 dark:bg-green-950/20 border-green-200/50 dark:border-green-800/50">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500" />
              <h4 className="text-sm font-medium text-foreground">Start Date</h4>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="startYear" className="text-xs font-medium text-muted-foreground">Year</Label>
                <Input
                  id="startYear"
                  type="number"
                  value={formData.startYear}
                  onChange={(e) => updateFormData('startYear', parseInt(e.target.value))}
                  min={2020}
                  max={2100}
                  className="text-sm"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="startMonth" className="text-xs font-medium text-muted-foreground">Month</Label>
                <Select
                  value={formData.startMonth.toString()}
                  onValueChange={(value) => updateFormData('startMonth', parseInt(value))}
                >
                  <SelectTrigger className="text-sm">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {monthNames.map((month, index) => (
                      <SelectItem key={index + 1} value={(index + 1).toString()}>
                        {month}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </Card>
          
          <Card className="p-5 space-y-4 bg-red-50/50 dark:bg-red-950/20 border-red-200/50 dark:border-red-800/50">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-red-500" />
              <h4 className="text-sm font-medium text-foreground">End Date</h4>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="endYear" className="text-xs font-medium text-muted-foreground">Year</Label>
                <Input
                  id="endYear"
                  type="number"
                  value={formData.endYear}
                  onChange={(e) => updateFormData('endYear', parseInt(e.target.value))}
                  min={2020}
                  max={2100}
                  className="text-sm"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="endMonth" className="text-xs font-medium text-muted-foreground">Month</Label>
                <Select
                  value={formData.endMonth.toString()}
                  onValueChange={(value) => updateFormData('endMonth', parseInt(value))}
                >
                  <SelectTrigger className="text-sm">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {monthNames.map((month, index) => (
                      <SelectItem key={index + 1} value={(index + 1).toString()}>
                        {month}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </Card>
        </div>
      </div>

      <Separator />

      {/* Office Scope */}
      <div className="space-y-6">
        <div className="space-y-3">
          <Label className="text-sm font-medium text-foreground flex items-center gap-2">
            <Users className="w-4 h-4 text-primary" />
            Office Scope <span className="text-destructive">*</span>
          </Label>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Choose whether to apply this scenario to all offices or select specific ones
          </p>
        </div>
        
        <Card className="p-5">
          <div className="space-y-5">
            {/* Group option */}
            <div className="flex items-start gap-4 p-4 rounded-lg border-2 border-transparent hover:border-border/50 transition-colors">
              <input
                type="radio"
                id="scope-group"
                checked={formData.officeScope === 'group'}
                onChange={() => updateFormData('officeScope', 'group')}
                className="w-4 h-4 text-primary border-2 focus:ring-primary mt-1"
              />
              <div className="flex-1 space-y-2">
                <Label htmlFor="scope-group" className="text-sm font-medium cursor-pointer text-foreground">
                  Group (All Offices)
                </Label>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  Apply this scenario to all offices in the organization automatically
                </p>
              </div>
            </div>
            
            {/* Individual offices option */}
            <div className="flex items-start gap-4 p-4 rounded-lg border-2 border-transparent hover:border-border/50 transition-colors">
              <input
                type="radio"
                id="scope-individual"
                checked={formData.officeScope === 'individual'}
                onChange={() => updateFormData('officeScope', 'individual')}
                className="w-4 h-4 text-primary border-2 focus:ring-primary mt-1"
              />
              <div className="flex-1 space-y-3">
                <div className="space-y-2">
                  <Label htmlFor="scope-individual" className="text-sm font-medium cursor-pointer text-foreground">
                    Individual Offices
                  </Label>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    Select specific offices to include in this scenario
                  </p>
                </div>

                {formData.officeScope === 'individual' && (
                  <Card className="p-4 bg-muted/30 border-muted">
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <Label className="text-xs font-medium text-foreground">
                          Select Offices <span className="text-destructive">*</span>
                        </Label>
                        <Badge variant="secondary" className="text-xs">
                          {formData.selectedOffices.length} selected
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3 max-h-48 overflow-y-auto">
                        {availableOffices
                          .filter(office => office !== 'Group')
                          .map(office => (
                          <div key={office} className="flex items-center gap-2 p-2 rounded-md hover:bg-muted/70 transition-colors">
                            <Checkbox
                              id={`office-${office}`}
                              checked={formData.selectedOffices.includes(office)}
                              onCheckedChange={(checked) => {
                                if (checked) {
                                  updateFormData('selectedOffices', [...formData.selectedOffices, office]);
                                } else {
                                  updateFormData('selectedOffices', 
                                    formData.selectedOffices.filter((o: OfficeName) => o !== office)
                                  );
                                }
                              }}
                            />
                            <Label htmlFor={`office-${office}`} className="text-xs cursor-pointer flex-1 leading-tight">
                              {office}
                            </Label>
                          </div>
                        ))}
                      </div>
                    </div>
                  </Card>
                )}
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

// Step 2: Baseline Input Component
const BaselineInputStep: React.FC<{
  data: any;
  onChange: (data: any) => void;
}> = ({ data, onChange }) => {
  const roles = ['Consultant', 'Sales', 'Recruitment'];
  const levels = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP'];
  
  // Generate months for the simulation period
  const months = Array.from({ length: 24 }, (_, i) => {
    const date = new Date(2025, i);
    return {
      key: `${date.getFullYear()}${(date.getMonth() + 1).toString().padStart(2, '0')}`,
      display: date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' })
    };
  });

  const initializeData = () => {
    if (!data) {
      const initialData = {
        global: {
          recruitment: {},
          churn: {}
        }
      };
      onChange(initialData);
      return initialData;
    }
    return data;
  };

  const currentData = initializeData();

  const updateCellValue = (role: string, type: 'recruitment' | 'churn', level: string, month: string, value: number) => {
    const newData = { ...currentData };
    if (!newData.global) newData.global = {};
    if (!newData.global[type]) newData.global[type] = {};
    if (!newData.global[type][role]) newData.global[type][role] = {};
    if (!newData.global[type][role][level]) newData.global[type][role][level] = {};
    
    newData.global[type][role][level][month] = value;
    onChange(newData);
  };

  const getCellValue = (role: string, type: 'recruitment' | 'churn', level: string, month: string): number => {
    return currentData?.global?.[type]?.[role]?.[level]?.[month] || 0;
  };

  const DataTable: React.FC<{
    role: string;
    type: 'recruitment' | 'churn';
    title: string;
  }> = ({ role, type, title }) => (
    <Card className="border-0 shadow-sm">
      <CardHeader className="pb-4">
        <CardTitle className="text-sm font-medium flex items-center gap-2 text-foreground">
          <Badge 
            variant={type === 'recruitment' ? 'default' : 'secondary'}
            className="text-xs"
          >
            {title}
          </Badge>
        </CardTitle>
        <p className="text-xs text-muted-foreground leading-relaxed">
          {type === 'recruitment' 
            ? 'Number of new hires expected each month' 
            : 'Number of departures expected each month'
          }
        </p>
      </CardHeader>
      <CardContent className="p-3">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b border-border">
                <th className="p-2 text-left text-xs font-medium text-muted-foreground sticky left-0 bg-background min-w-20 w-28">
                  Month
                </th>
                {levels.map(level => (
                  <th key={level} className="p-2 text-center text-xs font-medium text-muted-foreground min-w-16">
                    {level}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {months.slice(0, 12).map(month => (
                <tr key={month.key} className="border-b border-border/50 hover:bg-muted/30 transition-colors">
                  <td className="p-2 text-xs font-medium text-foreground sticky left-0 bg-background w-28">
                    {month.display}
                  </td>
                  {levels.map(level => (
                    <td key={level} className="p-1">
                      <Input
                        type="number"
                        value={getCellValue(role, type, level, month.key)}
                        onChange={(e) => updateCellValue(role, type, level, month.key, parseInt(e.target.value) || 0)}
                        className="w-full h-7 text-center text-xs border-0 bg-muted/40 focus:bg-background hover:bg-background transition-colors"
                        min="0"
                        placeholder="0"
                      />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-8">
      <div className="space-y-3">
        <h3 className="text-base font-semibold text-foreground flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-primary" />
          Configure Baseline Data
        </h3>
        <p className="text-sm text-muted-foreground leading-relaxed">
          Set monthly recruitment and churn numbers for each role and level. This data serves as the foundation for your scenario.
        </p>
      </div>

      <Tabs defaultValue={roles[0]} className="w-full">
        <TabsList className="grid grid-cols-3 mb-6 h-10 w-full">
          {roles.map(role => (
            <TabsTrigger key={role} value={role} className="text-xs font-medium">
              {role}
            </TabsTrigger>
          ))}
        </TabsList>

        {roles.map(role => (
          <TabsContent key={role} value={role} className="space-y-6">
            <DataTable role={role} type="recruitment" title="Monthly Recruitment" />
            <DataTable role={role} type="churn" title="Monthly Churn" />
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
};

// Step 3: Scenario Levers Component
const ScenarioLeversStep: React.FC<{
  data: any;
  onChange: (data: any) => void;
  baselineData?: any;
}> = ({ data, onChange }) => {
  const levels = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P'];
  const leverTypes = [
    { 
      key: 'recruitment', 
      title: 'Recruitment Multipliers', 
      description: 'Adjust recruitment rates by level (1.0 = baseline, 2.0 = double)',
      color: 'bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800'
    },
    { 
      key: 'churn', 
      title: 'Churn Multipliers', 
      description: 'Adjust churn/turnover rates by level (1.0 = baseline, 0.5 = half)',
      color: 'bg-red-50 dark:bg-red-950 border-red-200 dark:border-red-800'
    },
    { 
      key: 'progression', 
      title: 'Progression Multipliers', 
      description: 'Adjust promotion/progression rates by level (1.0 = baseline)',
      color: 'bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800'
    }
  ] as const;

  const updateLeverValue = (leverType: string, level: string, value: number) => {
    const newData = { ...data };
    if (!newData[leverType]) newData[leverType] = {};
    newData[leverType][level] = Math.round(value * 100) / 100; // Round to 2 decimal places
    onChange(newData);
  };

  const getLeverValue = (leverType: string, level: string): number => {
    return data?.[leverType]?.[level] || 1.0;
  };

  const resetToBaseline = (leverType: string) => {
    const newData = { ...data };
    if (!newData[leverType]) newData[leverType] = {};
    levels.forEach(level => {
      newData[leverType][level] = 1.0;
    });
    onChange(newData);
  };

  return (
    <div className="space-y-8">
      <div className="space-y-3">
        <h3 className="text-base font-semibold text-foreground flex items-center gap-2">
          <Settings className="w-4 h-4 text-primary" />
          Configure Scenario Levers
        </h3>
        <p className="text-sm text-muted-foreground leading-relaxed">
          Adjust multipliers to model different scenarios. Use 1.0 for baseline rates, values above 1.0 to increase, and below 1.0 to decrease.
        </p>
      </div>

      {leverTypes.map(({ key, title, description, color }) => (
        <Card key={key} className={`border-0 shadow-sm ${color}`}>
          <CardHeader className="pb-4">
            <div className="flex items-start justify-between gap-4">
              <div className="space-y-2 flex-1">
                <CardTitle className="text-base font-medium text-foreground flex items-center gap-2">
                  {title}
                </CardTitle>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  {description}
                </p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => resetToBaseline(key)}
                className="shrink-0 text-xs"
              >
                Reset to 1.0
              </Button>
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {levels.map(level => (
                <div key={level} className="space-y-3 p-4 rounded-lg bg-background border border-border/50">
                  <div className="flex items-center justify-between">
                    <Badge variant="secondary" className="w-10 h-6 justify-center text-xs font-mono">
                      {level}
                    </Badge>
                    <Badge 
                      variant="outline" 
                      className={`text-xs font-medium ${
                        getLeverValue(key, level) === 1.0 
                          ? 'text-muted-foreground border-muted-foreground/30' 
                          : getLeverValue(key, level) > 1.0 
                          ? 'text-green-600 border-green-300 bg-green-50 dark:bg-green-950' 
                          : 'text-red-600 border-red-300 bg-red-50 dark:bg-red-950'
                      }`}
                    >
                      {getLeverValue(key, level) === 1.0 
                        ? 'Baseline' 
                        : getLeverValue(key, level) > 1.0 
                        ? `+${Math.round((getLeverValue(key, level) - 1) * 100)}%`
                        : `${Math.round((getLeverValue(key, level) - 1) * 100)}%`
                      }
                    </Badge>
                  </div>
                  <div className="space-y-3">
                    <Slider
                      value={[getLeverValue(key, level)]}
                      onValueChange={([value]) => updateLeverValue(key, level, value)}
                      min={0}
                      max={2}
                      step={0.01}
                      className="w-full"
                    />
                    <Input
                      type="number"
                      value={getLeverValue(key, level).toFixed(2)}
                      onChange={(e) => updateLeverValue(key, level, parseFloat(e.target.value) || 1.0)}
                      min={0}
                      max={2}
                      step={0.01}
                      className="w-full h-8 text-center text-xs font-mono"
                      placeholder="1.00"
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default ScenarioWizardModern;