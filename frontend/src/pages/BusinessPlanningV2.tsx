/**
 * Business Planning V2 - Main Business Planning Page
 * 
 * Comprehensive business planning interface that serves as Planacy replacement
 * Supports multi-office planning, aggregated baselines, and simulation integration
 */
import React, { useState, useEffect, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';
import { 
  Building2, 
  Calendar, 
  TrendingUp, 
  Download, 
  Upload, 
  Play,
  Globe,
  PlusCircle,
  Settings
} from 'lucide-react';
import { useOfficeStore } from '../stores/officeStore';
import { useBusinessPlanStore } from '../stores/businessPlanStore';
import { ExpandablePlanningGrid } from '../components/business-planning/ExpandablePlanningGrid';
import { OfficeSelector } from '../components/business-planning/OfficeSelector';
import { PlanningDashboard } from '../components/business-planning/PlanningDashboard';
import { AggregatedPlanView } from '../components/business-planning/AggregatedPlanView';
import { SimulationIntegration } from '../components/business-planning/SimulationIntegration';
import { ImportExportTools } from '../components/business-planning/ImportExportTools';
import type { OfficeConfig } from '../types/office';
import '../components/business-planning/business-planning.css';

type PlanningTab = 'office-planning' | 'aggregated' | 'dashboard' | 'simulation' | 'settings';

export const BusinessPlanningV2: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState<PlanningTab>('office-planning');
  const [selectedOfficeId, setSelectedOfficeId] = useState<string | null>(null);
  const [selectedYear, setSelectedYear] = useState<number>(new Date().getFullYear());
  const [showAggregatedView, setShowAggregatedView] = useState(false);

  const { 
    offices, 
    loading: officesLoading, 
    loadOffices 
  } = useOfficeStore();

  const {
    monthlyPlans,
    loading: plansLoading,
    error: plansError,
    loadBusinessPlans,
    clearError
  } = useBusinessPlanStore();

  // Initialize from URL params
  useEffect(() => {
    const tab = searchParams.get('tab') as PlanningTab;
    const office = searchParams.get('office');
    const year = searchParams.get('year');

    if (tab && ['office-planning', 'aggregated', 'dashboard', 'simulation', 'settings'].includes(tab)) {
      setActiveTab(tab);
    }
    if (office) {
      setSelectedOfficeId(office);
    }
    if (year && !isNaN(parseInt(year))) {
      setSelectedYear(parseInt(year));
    }
  }, [searchParams]);

  // Load initial data
  useEffect(() => {
    loadOffices();
  }, [loadOffices]);

  // Auto-select first office if none selected
  useEffect(() => {
    if (!selectedOfficeId && offices.length > 0) {
      setSelectedOfficeId(offices[0].id);
    }
  }, [selectedOfficeId, offices]);

  // Update URL when state changes
  useEffect(() => {
    const params = new URLSearchParams();
    params.set('tab', activeTab);
    if (selectedOfficeId) params.set('office', selectedOfficeId);
    params.set('year', selectedYear.toString());
    setSearchParams(params, { replace: true });
  }, [activeTab, selectedOfficeId, selectedYear, setSearchParams]);

  const selectedOffice = useMemo(() => 
    offices.find(office => office.id === selectedOfficeId),
    [offices, selectedOfficeId]
  );

  const availableYears = useMemo(() => {
    const currentYear = new Date().getFullYear();
    return Array.from({ length: 5 }, (_, i) => currentYear + i - 1);
  }, []);

  const handleTabChange = (value: string) => {
    setActiveTab(value as PlanningTab);
  };

  const handleOfficeChange = (officeId: string) => {
    setSelectedOfficeId(officeId);
  };

  const handleYearChange = (year: number) => {
    setSelectedYear(year);
  };

  const handleCreateScenario = async () => {
    if (!selectedOffice) return;
    
    try {
      // Navigate to scenario creation with business plan as baseline
      window.location.href = `/scenarios/new?baseline=business-plan&office=${selectedOfficeId}&year=${selectedYear}`;
    } catch (error) {
      console.error('Failed to create scenario from business plan:', error);
    }
  };

  const handleCreateAggregatedBaseline = async () => {
    try {
      // Navigate to scenario creation with aggregated baseline
      window.location.href = `/scenarios/new?baseline=aggregated-plan&year=${selectedYear}`;
    } catch (error) {
      console.error('Failed to create aggregated baseline:', error);
    }
  };

  const tabs = [
    {
      key: 'office-planning' as PlanningTab,
      label: 'Office Planning',
      icon: Building2,
      description: 'Create detailed business plans for individual offices'
    },
    {
      key: 'aggregated' as PlanningTab,
      label: 'Company-Wide',
      icon: Globe,
      description: 'View and manage aggregated business plans across all offices'
    },
    {
      key: 'dashboard' as PlanningTab,
      label: 'Analytics',
      icon: TrendingUp,
      description: 'Business plan analytics and performance insights'
    },
    {
      key: 'simulation' as PlanningTab,
      label: 'Scenarios',
      icon: Play,
      description: 'Create scenarios using business plans as baselines'
    },
    {
      key: 'settings' as PlanningTab,
      label: 'Settings',
      icon: Settings,
      description: 'Business planning configuration and templates'
    }
  ];

  const isLoading = officesLoading || plansLoading;

  return (
    <div className="business-planning-v2 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Business Planning</h1>
          <p className="text-muted-foreground">
            Create and manage business plans that serve as simulation baselines
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Quick Actions */}
          <Button 
            variant="outline" 
            size="sm"
            onClick={handleCreateScenario}
            disabled={!selectedOffice}
          >
            <Play className="h-4 w-4 mr-2" />
            Create Scenario
          </Button>
          
          <Button 
            variant="outline" 
            size="sm"
            onClick={handleCreateAggregatedBaseline}
          >
            <Globe className="h-4 w-4 mr-2" />
            Aggregated Baseline
          </Button>

          <ImportExportTools 
            selectedOffice={selectedOffice}
            selectedYear={selectedYear}
          />
        </div>
      </div>

      {/* Error Display */}
      {plansError && (
        <Alert variant="destructive">
          <AlertDescription>
            {plansError}
            <Button 
              variant="link" 
              size="sm" 
              onClick={clearError}
              className="ml-2 p-0 h-auto"
            >
              Dismiss
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={handleTabChange} className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          {tabs.map(tab => {
            const Icon = tab.icon;
            return (
              <TabsTrigger 
                key={tab.key} 
                value={tab.key}
                className="flex items-center gap-2"
              >
                <Icon className="h-4 w-4" />
                <span className="hidden sm:inline">{tab.label}</span>
              </TabsTrigger>
            );
          })}
        </TabsList>

        {/* Office Planning Tab */}
        <TabsContent value="office-planning" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Building2 className="h-5 w-5" />
                    Office Business Planning
                  </CardTitle>
                  <p className="text-sm text-muted-foreground">
                    Create detailed monthly plans with expandable rows for each role and level. 
                    Input recruitment, churn, price, and UTR for every role/level combination.
                  </p>
                </div>
                
                <div className="flex items-center gap-3">
                  <OfficeSelector
                    offices={offices}
                    selectedOfficeId={selectedOfficeId}
                    onOfficeChange={handleOfficeChange}
                    disabled={isLoading}
                  />
                  
                  <select
                    value={selectedYear}
                    onChange={(e) => handleYearChange(parseInt(e.target.value))}
                    className="px-3 py-1 border rounded-md bg-background"
                    disabled={isLoading}
                  >
                    {availableYears.map(year => (
                      <option key={year} value={year}>{year}</option>
                    ))}
                  </select>
                </div>
              </div>
            </CardHeader>
            
            <CardContent>
              {selectedOffice ? (
                <ExpandablePlanningGrid
                  office={selectedOffice}
                  year={selectedYear}
                  onYearChange={handleYearChange}
                />
              ) : (
                <div className="text-center py-12">
                  <Building2 className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <h3 className="text-lg font-medium mb-2">Select an Office</h3>
                  <p className="text-muted-foreground">
                    Choose an office from the selector above to start business planning
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Aggregated Planning Tab */}
        <TabsContent value="aggregated" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5" />
                Company-Wide Business Planning
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                View and manage aggregated business plans across all offices
              </p>
            </CardHeader>
            
            <CardContent>
              <AggregatedPlanView
                offices={offices}
                year={selectedYear}
                onYearChange={handleYearChange}
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Dashboard Tab */}
        <TabsContent value="dashboard" className="space-y-6">
          <PlanningDashboard
            offices={offices}
            selectedOffice={selectedOffice}
            year={selectedYear}
            onYearChange={handleYearChange}
          />
        </TabsContent>

        {/* Simulation Integration Tab */}
        <TabsContent value="simulation" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Play className="h-5 w-5" />
                Scenario Planning Integration
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                Create scenarios using business plans as baselines
              </p>
            </CardHeader>
            
            <CardContent>
              <SimulationIntegration
                offices={offices}
                selectedOffice={selectedOffice}
                year={selectedYear}
                onCreateScenario={handleCreateScenario}
                onCreateAggregatedBaseline={handleCreateAggregatedBaseline}
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Business Planning Settings
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                Configure templates, validation rules, and integration settings
              </p>
            </CardHeader>
            
            <CardContent>
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium mb-4">Planning Templates</h3>
                  <p className="text-muted-foreground mb-4">
                    Manage default templates for new business plans
                  </p>
                  <Button variant="outline" disabled>
                    <PlusCircle className="h-4 w-4 mr-2" />
                    Create Template
                  </Button>
                </div>

                <div>
                  <h3 className="text-lg font-medium mb-4">Validation Rules</h3>
                  <p className="text-muted-foreground mb-4">
                    Configure business rules and validation constraints
                  </p>
                  <Button variant="outline" disabled>
                    <Settings className="h-4 w-4 mr-2" />
                    Configure Rules
                  </Button>
                </div>

                <div>
                  <h3 className="text-lg font-medium mb-4">Integration Settings</h3>
                  <p className="text-muted-foreground mb-4">
                    Configure simulation engine integration and data export
                  </p>
                  <Button variant="outline" disabled>
                    <Settings className="h-4 w-4 mr-2" />
                    Integration Settings
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};