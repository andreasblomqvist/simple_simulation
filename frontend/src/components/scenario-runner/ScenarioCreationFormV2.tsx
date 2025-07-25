import React, { useState, useEffect } from 'react';
import { ChevronRight } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { RadioGroup, RadioGroupItem } from '../ui/radio-group';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { useToast } from '../ui/use-toast';
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

  useEffect(() => {
    loadAvailableOffices();
  }, []);

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

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
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

    const scenarioDefinition: ScenarioDefinition = {
      name: formData.name,
      description: formData.description,
      time_range: timeRange,
      office_scope: officeScopeList,
      levers: {},
      economic_params: {},
    };

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