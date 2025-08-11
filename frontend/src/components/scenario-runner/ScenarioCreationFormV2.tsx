import React, { useState, useEffect } from 'react';
import { ChevronRight, Building2, Globe } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { RadioGroup, RadioGroupItem } from '../ui/radio-group';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import { useToast } from '../ui/use-toast';
import { useSearchParams } from 'react-router-dom';
import type { ScenarioDefinition, TimeRange, OfficeName } from '../../types/unified-data-structures';
import { scenarioApi } from '../../services/scenarioApi';
import { cn } from '../../lib/utils';

interface ScenarioCreationFormV2Props {
  scenario?: ScenarioDefinition;
  onNext: (result: { scenarioId: string; scenario: ScenarioDefinition }) => void;
  onBack: () => void;
  loading?: boolean;
}

const ScenarioCreationFormV2: React.FC<ScenarioCreationFormV2Props> = ({ 
  scenario, 
  onNext, 
  onBack, 
  loading = false 
}) => {
  const { toast } = useToast();
  const [searchParams] = useSearchParams();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    startYear: 2025,
    endYear: 2027,
    startMonth: 1,
    endMonth: 12,
    officeScope: 'group' as 'group' | 'individual',
    offices: [] as string[],
  });
  const [availableOffices, setAvailableOffices] = useState<OfficeName[]>([]);
  const [loadingOffices, setLoadingOffices] = useState(true);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [baselineInfo, setBaselineInfo] = useState<{
    type: 'business-plan' | 'aggregated-plan' | null;
    office?: string;
    year?: number;
    loading: boolean;
    error?: string;
  }>({ type: null, loading: false });
  const [businessPlans, setBusinessPlans] = useState<Array<{
    id: string;
    office_id: string;
    year: number;
    month: number;
  }>>([]);
  const [selectedBusinessPlan, setSelectedBusinessPlan] = useState<string>('');

  useEffect(() => {
    loadAvailableOffices();
    loadBusinessPlans();
  }, []);

  // Detect business plan baseline from URL parameters
  useEffect(() => {
    const baseline = searchParams.get('baseline');
    const office = searchParams.get('office');
    const year = searchParams.get('year');

    console.log('[DEBUG] URL params:', { baseline, office, year });

    if (baseline && (baseline === 'business-plan' || baseline === 'aggregated-plan')) {
      const yearNum = year ? parseInt(year) : new Date().getFullYear();
      
      console.log('[DEBUG] Setting baseline info:', { type: baseline, office, year: yearNum });
      
      setBaselineInfo({
        type: baseline as 'business-plan' | 'aggregated-plan',
        office: office || undefined,
        year: yearNum,
        loading: false
      });

      // Pre-fill form based on baseline type
      if (baseline === 'business-plan' && office) {
        setFormData(prev => ({
          ...prev,
          name: `${office.charAt(0).toUpperCase() + office.slice(1)} Business Plan Scenario`,
          description: `Scenario based on ${office} business plan for ${yearNum}`,
          startYear: yearNum,
          endYear: yearNum + 2,
          officeScope: 'individual',
          offices: [office]
        }));
      } else if (baseline === 'aggregated-plan') {
        setFormData(prev => ({
          ...prev,
          name: `Aggregated Business Plan Scenario`,
          description: `Scenario based on aggregated business plans for ${yearNum}`,
          startYear: yearNum,
          endYear: yearNum + 2,
          officeScope: 'group'
        }));
      }
    }
  }, [searchParams]);

  useEffect(() => {
    if (scenario && scenario.time_range) {
      setFormData({
        name: scenario.name || '',
        description: scenario.description || '',
        startYear: scenario.time_range.start_year,
        endYear: scenario.time_range.end_year,
        startMonth: scenario.time_range.start_month,
        endMonth: scenario.time_range.end_month,
        officeScope: scenario.office_scope && scenario.office_scope.includes('Group') ? 'group' : 'individual',
        offices: scenario.office_scope ? scenario.office_scope.filter(office => office !== 'Group') : [],
      });
    }
  }, [scenario]);

  const loadAvailableOffices = async () => {
    try {
      setLoadingOffices(true);
      const offices = await scenarioApi.getAvailableOffices();
      setAvailableOffices(offices);
    } catch (error) {
      toast({
        title: "Error",
        description: 'Failed to load available offices: ' + (error as Error).message,
        variant: "destructive",
      });
    } finally {
      setLoadingOffices(false);
    }
  };

  const loadBusinessPlans = async () => {
    try {
      const response = await fetch('http://localhost:8000/business-plans');
      if (response.ok) {
        const plans = await response.json();
        // Group by office and year, showing only the latest month for each office-year combination
        const latestPlans = plans.reduce((acc: any[], plan: any) => {
          const key = `${plan.office_id}-${plan.year}`;
          const existing = acc.find(p => `${p.office_id}-${p.year}` === key);
          if (!existing || plan.month > existing.month) {
            return [...acc.filter(p => `${p.office_id}-${p.year}` !== key), plan];
          }
          return acc;
        }, []);
        setBusinessPlans(latestPlans.sort((a: any, b: any) => {
          if (a.year !== b.year) return b.year - a.year;
          if (a.office_id !== b.office_id) return a.office_id.localeCompare(b.office_id);
          return b.month - a.month;
        }));
      }
    } catch (error) {
      console.error('Failed to load business plans:', error);
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Scenario name is required';
    }

    if (formData.startYear < 2020 || formData.startYear > 2100) {
      newErrors.startYear = 'Start year must be between 2020 and 2100';
    }

    if (formData.endYear < 2020 || formData.endYear > 2100) {
      newErrors.endYear = 'End year must be between 2020 and 2100';
    }

    if (formData.endYear < formData.startYear) {
      newErrors.endYear = 'End year must be after start year';
    }

    if (formData.startMonth < 1 || formData.startMonth > 12) {
      newErrors.startMonth = 'Start month must be between 1 and 12';
    }

    if (formData.endMonth < 1 || formData.endMonth > 12) {
      newErrors.endMonth = 'End month must be between 1 and 12';
    }

    if (formData.officeScope === 'individual' && formData.offices.length === 0) {
      newErrors.offices = 'Select at least one office';
    }

    if (!selectedBusinessPlan) {
      newErrors.businessPlan = 'Business plan selection is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    const timeRange: TimeRange = {
      start_year: formData.startYear,
      start_month: formData.startMonth,
      end_year: formData.endYear,
      end_month: formData.endMonth,
    };

    const officeScopeList: OfficeName[] = formData.officeScope === 'group' 
      ? ['Group'] 
      : formData.offices as OfficeName[];

    let baselineInput = undefined;

    // Fetch business plan baseline data if specified
    if (baselineInfo.type && baselineInfo.year) {
      try {
        setBaselineInfo(prev => ({ ...prev, loading: true, error: undefined }));
        
        let baselineResponse;
        if (baselineInfo.type === 'business-plan' && baselineInfo.office) {
          // Individual office business plan
          baselineResponse = await fetch(
            `/api/business-plans/export-baseline?office_id=${baselineInfo.office}&year=${baselineInfo.year}&start_month=${formData.startMonth}&end_month=${formData.endMonth}`
          );
        } else if (baselineInfo.type === 'aggregated-plan') {
          // Aggregated business plan
          baselineResponse = await fetch(
            `/api/business-plans/aggregated/export-baseline?year=${baselineInfo.year}&start_month=${formData.startMonth}&end_month=${formData.endMonth}`
          );
        }

        if (baselineResponse && baselineResponse.ok) {
          baselineInput = await baselineResponse.json();
          console.log('[DEBUG] Baseline data loaded:', baselineInput);
          toast({
            title: "Success",
            description: "Business plan baseline loaded successfully",
          });
        } else {
          throw new Error(`Failed to fetch baseline: ${baselineResponse?.statusText}`);
        }
        
        setBaselineInfo(prev => ({ ...prev, loading: false }));
      } catch (error) {
        const errorMsg = `Failed to load business plan baseline: ${(error as Error).message}`;
        setBaselineInfo(prev => ({ ...prev, loading: false, error: errorMsg }));
        toast({
          title: "Error",
          description: errorMsg,
          variant: "destructive",
        });
        return;
      }
    }

    const scenarioDefinition: ScenarioDefinition = {
      name: formData.name,
      description: formData.description,
      time_range: timeRange,
      office_scope: officeScopeList,
      levers: {},
      economic_params: {},
      baseline_input: baselineInput || undefined,
      business_plan_id: selectedBusinessPlan || undefined
    };

    console.log('[DEBUG] Final scenario definition:', scenarioDefinition);
    console.log('[DEBUG] Business plan ID in scenario:', scenarioDefinition.business_plan_id);
    onNext({ scenarioId: '', scenario: scenarioDefinition });
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  if (loadingOffices) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading available offices...</p>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Business Plan Baseline Info */}
      {baselineInfo.type && (
        <Alert className="border-blue-200 bg-blue-50">
          <div className="flex items-start space-x-3">
            {baselineInfo.type === 'business-plan' ? (
              <Building2 className="h-5 w-5 text-blue-600 mt-0.5" />
            ) : (
              <Globe className="h-5 w-5 text-blue-600 mt-0.5" />
            )}
            <div className="flex-1">
              <AlertDescription className="text-blue-800">
                <div className="font-medium mb-1">
                  {baselineInfo.type === 'business-plan' 
                    ? 'Individual Office Business Plan Baseline' 
                    : 'Aggregated Business Plan Baseline'}
                </div>
                <div className="text-sm">
                  {baselineInfo.type === 'business-plan' && baselineInfo.office && (
                    <span>Office: <Badge variant="outline" className="text-blue-700 border-blue-300">{baselineInfo.office}</Badge></span>
                  )}
                  {baselineInfo.year && (
                    <span className={baselineInfo.office ? 'ml-3' : ''}>
                      Year: <Badge variant="outline" className="text-blue-700 border-blue-300">{baselineInfo.year}</Badge>
                    </span>
                  )}
                </div>
                <div className="text-xs mt-2 text-blue-600">
                  Scenario will be initialized with business plan recruitment and churn data as baseline
                </div>
              </AlertDescription>
            </div>
          </div>
        </Alert>
      )}

      {/* Baseline Loading/Error States */}
      {baselineInfo.loading && (
        <Alert>
          <AlertDescription>Loading business plan baseline data...</AlertDescription>
        </Alert>
      )}
      
      {baselineInfo.error && (
        <Alert variant="destructive">
          <AlertDescription>{baselineInfo.error}</AlertDescription>
        </Alert>
      )}

      {/* Scenario Name */}
      <div className="space-y-2">
        <Label htmlFor="name">Scenario Name *</Label>
        <Input
          id="name"
          placeholder="e.g. Oslo Growth Plan 2025-2027"
          value={formData.name}
          onChange={(e) => handleInputChange('name', e.target.value)}
          className={cn(errors.name && "border-destructive")}
        />
        {errors.name && (
          <p className="text-sm text-destructive">{errors.name}</p>
        )}
      </div>

      {/* Description */}
      <div className="space-y-2">
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          placeholder="Describe the scenario (optional)"
          value={formData.description}
          onChange={(e) => handleInputChange('description', e.target.value)}
          rows={2}
        />
      </div>

      {/* Business Plan Baseline */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Business Plan Baseline *</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Label htmlFor="businessPlan">Select Business Plan</Label>
            <Select
              value={selectedBusinessPlan}
              onValueChange={(value) => {
                setSelectedBusinessPlan(value);
                if (value && value !== 'none') {
                  const plan = businessPlans.find(p => p.id === value);
                  if (plan) {
                    // Update form with business plan details
                    const capitalizedOffice = plan.office_id.charAt(0).toUpperCase() + plan.office_id.slice(1);
                    setFormData(prev => ({
                      ...prev,
                      name: prev.name || `${capitalizedOffice} Business Plan Scenario`,
                      description: prev.description || `Based on ${capitalizedOffice} business plan (${plan.year}/${plan.month})`,
                      startYear: plan.year,
                      startMonth: plan.month,
                      officeScope: 'individual',
                      offices: [capitalizedOffice]
                    }));
                    setBaselineInfo({
                      type: 'business-plan',
                      office: plan.office_id,
                      year: plan.year,
                      loading: false
                    });
                  }
                } else {
                  setBaselineInfo({ type: null, loading: false });
                }
              }}
            >
              <SelectTrigger className={cn(errors.businessPlan && "border-destructive")}>
                <SelectValue placeholder="Select a business plan *" />
              </SelectTrigger>
              <SelectContent>
                {businessPlans.map(plan => (
                  <SelectItem key={plan.id} value={plan.id}>
                    {plan.office_id.charAt(0).toUpperCase() + plan.office_id.slice(1)} - {plan.year}/{plan.month}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.businessPlan && (
              <p className="text-sm text-destructive">{errors.businessPlan}</p>
            )}
            <p className="text-sm text-muted-foreground">
              Select a business plan to use its recruitment and churn data as baseline values for the scenario
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Time Range */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Time Range</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="space-y-2">
            <Label htmlFor="startYear">Start Year *</Label>
            <Input
              id="startYear"
              type="number"
              min={2020}
              max={2100}
              value={formData.startYear}
              onChange={(e) => handleInputChange('startYear', parseInt(e.target.value))}
              className={cn(errors.startYear && "border-destructive")}
            />
            {errors.startYear && (
              <p className="text-sm text-destructive">{errors.startYear}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="startMonth">Start Month *</Label>
            <Select
              value={formData.startMonth.toString()}
              onValueChange={(value) => handleInputChange('startMonth', parseInt(value))}
            >
              <SelectTrigger className={cn(errors.startMonth && "border-destructive")}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Array.from({ length: 12 }, (_, i) => (
                  <SelectItem key={i + 1} value={(i + 1).toString()}>
                    {i + 1}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.startMonth && (
              <p className="text-sm text-destructive">{errors.startMonth}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="endYear">End Year *</Label>
            <Input
              id="endYear"
              type="number"
              min={2020}
              max={2100}
              value={formData.endYear}
              onChange={(e) => handleInputChange('endYear', parseInt(e.target.value))}
              className={cn(errors.endYear && "border-destructive")}
            />
            {errors.endYear && (
              <p className="text-sm text-destructive">{errors.endYear}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="endMonth">End Month *</Label>
            <Select
              value={formData.endMonth.toString()}
              onValueChange={(value) => handleInputChange('endMonth', parseInt(value))}
            >
              <SelectTrigger className={cn(errors.endMonth && "border-destructive")}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Array.from({ length: 12 }, (_, i) => (
                  <SelectItem key={i + 1} value={(i + 1).toString()}>
                    {i + 1}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.endMonth && (
              <p className="text-sm text-destructive">{errors.endMonth}</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Office Scope */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Office Scope</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <RadioGroup
            value={formData.officeScope}
            onValueChange={(value: 'group' | 'individual') => handleInputChange('officeScope', value)}
            className="flex flex-col space-y-2"
          >
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="group" id="group" />
              <Label htmlFor="group">Group (all offices)</Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="individual" id="individual" />
              <Label htmlFor="individual">Individual Offices</Label>
            </div>
          </RadioGroup>

          {formData.officeScope === 'individual' && (
            <div className="space-y-2">
              <Label htmlFor="offices">Select Offices *</Label>
              <Select
                value={formData.offices.length > 0 ? formData.offices[0] : ''}
                onValueChange={(value) => {
                  const currentOffices = formData.offices;
                  if (currentOffices.includes(value)) {
                    handleInputChange('offices', currentOffices.filter(office => office !== value));
                  } else {
                    handleInputChange('offices', [...currentOffices, value]);
                  }
                }}
              >
                <SelectTrigger className={cn(errors.offices && "border-destructive")}>
                  <SelectValue placeholder="Choose offices">
                    {formData.offices.length > 0 ? `${formData.offices.length} office(s) selected` : 'Choose offices'}
                  </SelectValue>
                </SelectTrigger>
                <SelectContent>
                  {availableOffices.filter(office => office !== 'Group').map(office => (
                    <SelectItem key={office} value={office}>
                      <div className="flex items-center space-x-2">
                        <span>{office}</span>
                        {formData.offices.includes(office) && (
                          <span className="text-primary">✓</span>
                        )}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {formData.offices.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {formData.offices.map(office => (
                    <span
                      key={office}
                      className="inline-flex items-center px-2 py-1 text-xs bg-primary/10 text-primary rounded-md"
                    >
                      {office}
                      <button
                        type="button"
                        onClick={() => handleInputChange('offices', formData.offices.filter(o => o !== office))}
                        className="ml-1 hover:text-primary/70"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              )}
              {errors.offices && (
                <p className="text-sm text-destructive">{errors.offices}</p>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Progression Configuration Notice */}
      <Alert className="border-green-200 bg-green-50">
        <div className="flex items-start space-x-3">
          <div className="flex-1">
            <AlertDescription className="text-green-800">
              <div className="font-medium mb-1">
                Default Progression Configuration Included
              </div>
              <div className="text-sm">
                This scenario will automatically include default progression rates and CAT matrix values for career advancement modeling.
              </div>
            </AlertDescription>
          </div>
        </div>
      </Alert>

      {/* Action Buttons */}
      <div className="flex justify-between pt-4">
        <Button type="button" variant="outline" onClick={onBack}>
          Back
        </Button>
        <Button type="submit" disabled={loading}>
          {loading ? (
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
              <span>Loading...</span>
            </div>
          ) : (
            <>
              Next: Configure Baseline Input
              <ChevronRight className="h-4 w-4 ml-2" />
            </>
          )}
        </Button>
      </div>
    </form>
  );
};

export default ScenarioCreationFormV2;