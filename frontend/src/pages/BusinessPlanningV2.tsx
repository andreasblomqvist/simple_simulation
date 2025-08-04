/**
 * Business Planning V2 - Main Business Planning Page
 * 
 * Comprehensive business planning interface that serves as Planacy replacement
 * Supports multi-office planning, aggregated baselines, and simulation integration
 */
import React, { useState, useEffect, useMemo, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
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
  Settings,
  Bot,
  Sparkles
} from 'lucide-react';
import { useOfficeStore } from '../stores/officeStore';
import { useBusinessPlanStore } from '../stores/businessPlanStore';
import { ExpandablePlanningGrid } from '../components/business-planning/ExpandablePlanningGrid';
import { CleanBusinessPlanTable } from '../components/business-planning/CleanBusinessPlanTable';
import { SimpleAIPlanningInterface } from '../components/business-planning/SimpleAIPlanningInterface';
import { BusinessPlansList } from '../components/business-planning/BusinessPlansList';
import { OfficeSelector } from '../components/business-planning/OfficeSelector';
import { SimulationIntegration } from '../components/business-planning/SimulationIntegration';
import { ImportExportTools } from '../components/business-planning/ImportExportTools';
import type { OfficeConfig } from '../types/office';
import { cn } from '../lib/utils';
import '../components/business-planning/business-planning.css';

type PlanningTab = 'plans-list' | 'office-planning' | 'ai-planning' | 'aggregated' | 'simulation' | 'settings';

export const BusinessPlanningV2: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState<PlanningTab>('plans-list');
  const [selectedOfficeId, setSelectedOfficeId] = useState<string | null>(null);
  const [selectedYear, setSelectedYear] = useState<number>(new Date().getFullYear());
  const lastUrlStateRef = useRef<string>('');
  const [showAggregatedView, setShowAggregatedView] = useState(false);
  const [useAIInterface, setUseAIInterface] = useState(false);
  const [showAIDemo, setShowAIDemo] = useState(true);

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

    if (tab && ['plans-list', 'office-planning', 'ai-planning', 'aggregated', 'simulation', 'settings'].includes(tab)) {
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

  // Temporarily disable URL updating to prevent SecurityError
  // TODO: Re-implement URL sync without causing infinite loops
  /*
  useEffect(() => {
    const currentTab = searchParams.get('tab');
    const currentOffice = searchParams.get('office');
    const currentYear = searchParams.get('year');
    
    if (currentTab !== activeTab || 
        currentOffice !== selectedOfficeId || 
        currentYear !== selectedYear.toString()) {
      const params = new URLSearchParams();
      params.set('tab', activeTab);
      if (selectedOfficeId) params.set('office', selectedOfficeId);
      params.set('year', selectedYear.toString());
      setSearchParams(params, { replace: true });
    }
  }, [activeTab, selectedOfficeId, selectedYear, setSearchParams]);
  */

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

  // Business Plan CRUD handlers
  const handleCreateNewPlan = (data: {
    name: string;
    officeId: string;
    year: number;
    workflow: 'ai' | 'manual';
  }) => {
    // Store the new plan data for creation
    localStorage.setItem('new-business-plan', JSON.stringify({
      ...data,
      timestamp: new Date().toISOString()
    }));

    // Set the selected office and year
    setSelectedOfficeId(data.officeId);
    setSelectedYear(data.year);

    // Navigate to appropriate tab based on workflow
    if (data.workflow === 'ai') {
      setActiveTab('ai-planning');
    } else {
      setActiveTab('office-planning');
    }
  };

  const handleEditPlan = (planId: string) => {
    // In a real implementation, load the plan data and navigate to edit mode
    console.log('Edit plan:', planId);
    setActiveTab('office-planning');
    // TODO: Load plan data and populate form
  };

  const handleViewPlan = (planId: string) => {
    // In a real implementation, load the plan data and navigate to view mode
    console.log('View plan:', planId);
    setActiveTab('office-planning');
    // TODO: Load plan data in read-only mode
  };

  const handleDeletePlan = (planId: string) => {
    // In a real implementation, call API to delete the plan
    console.log('Delete plan:', planId);
    // TODO: Call delete API and refresh list
  };

  const handleDuplicatePlan = (planId: string) => {
    // In a real implementation, duplicate the plan and open in edit mode
    console.log('Duplicate plan:', planId);
    setActiveTab('office-planning');
    // TODO: Duplicate plan data and open for editing
  };

  const handleMarkOfficial = (planId: string) => {
    // In a real implementation, this would:
    // 1. Find the plan and its office/year
    // 2. Check if another plan is already official for that office/year
    // 3. If so, ask user to confirm unmarking the current official plan
    // 4. Update the plan's official status via API
    // 5. Refresh the plans list
    
    console.log('Toggle official status for plan:', planId);
    
    // For now, show a confirmation dialog
    const confirmed = confirm('This will mark this plan as the official plan for its office. Any existing official plan for the same office and year will be unmarked. Continue?');
    
    if (confirmed) {
      // TODO: Call API to update official status with validation
      // API should ensure only one official plan per office per year
      console.log('Confirmed: Marking plan as official:', planId);
    }
  };

  const handleViewOfficePlan = (officeId: string, year: number) => {
    // Navigate to office planning tab with the selected office and year
    setSelectedOfficeId(officeId);
    setSelectedYear(year);
    setActiveTab('office-planning');
  };

  const tabs = [
    {
      key: 'plans-list' as PlanningTab,
      label: 'All Plans',
      icon: PlusCircle,
      description: 'View and manage all business plans with CRUD operations'
    },
    {
      key: 'office-planning' as PlanningTab,
      label: 'Office Planning',
      icon: Building2,
      description: 'Create detailed business plans for individual offices'
    },
    {
      key: 'ai-planning' as PlanningTab,
      label: 'AI Planning',
      icon: Bot,
      description: 'AI-facilitated conversational business planning with live simulation'
    },
    {
      key: 'aggregated' as PlanningTab,
      label: 'Company-Wide',
      icon: Globe,
      description: 'View and manage aggregated business plans across all offices'
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
    <div className="business-planning-v2 space-y-8" style={{ backgroundColor: '#111827', minHeight: '100vh', padding: '1rem' }}>
      {/* Enhanced Header with Modern Styling */}
      <div className="flex items-start justify-between p-1">
        <div className="space-y-2">
          <h1 className="text-4xl font-bold tracking-tight" style={{ color: '#f3f4f6' }}>
            Business Planning
          </h1>
          <p className="text-lg max-w-2xl leading-relaxed" style={{ color: '#d1d5db' }}>
            Create and manage sophisticated business plans that serve as intelligent simulation baselines for strategic workforce planning.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Enhanced Quick Actions */}
          <Button 
            variant="outline" 
            size="sm"
            onClick={handleCreateScenario}
            disabled={!selectedOffice}
            style={{
              height: '36px',
              padding: '0 1rem',
              fontWeight: '500',
              border: '1px solid #374151',
              backgroundColor: '#1f2937',
              color: '#f3f4f6',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#374151';
              e.currentTarget.style.borderColor = '#4b5563';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#1f2937';
              e.currentTarget.style.borderColor = '#374151';
            }}
          >
            <Play className="h-4 w-4 mr-2" style={{ color: '#f3f4f6' }} />
            Create Scenario
          </Button>
          
          <Button 
            variant="outline" 
            size="sm"
            onClick={handleCreateAggregatedBaseline}
            style={{
              height: '36px',
              padding: '0 1rem',
              fontWeight: '500',
              border: '1px solid #374151',
              backgroundColor: '#1f2937',
              color: '#f3f4f6',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#374151';
              e.currentTarget.style.borderColor = '#4b5563';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#1f2937';
              e.currentTarget.style.borderColor = '#374151';
            }}
          >
            <Globe className="h-4 w-4 mr-2" style={{ color: '#f3f4f6' }} />
            Aggregated Baseline
          </Button>

          <ImportExportTools 
            selectedOffice={selectedOffice}
            selectedYear={selectedYear}
          />
        </div>
      </div>

      {/* Enhanced Error Display */}
      {plansError && (
        <Alert variant="destructive" style={{ border: '1px solid #dc2626', backgroundColor: '#7f1d1d' }}>
          <AlertDescription style={{ color: '#fef2f2' }}>
            {plansError}
            <Button 
              variant="link" 
              size="sm" 
              onClick={clearError}
              style={{
                marginLeft: '12px',
                padding: '0',
                height: 'auto',
                color: '#fca5a5',
                fontWeight: '500'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.color = '#fed7d7';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.color = '#fca5a5';
              }}
            >
              Dismiss
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Enhanced Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={handleTabChange} className="space-y-6">
        <div className="relative">
          <TabsList 
            className="grid w-full grid-cols-6 h-14 p-1.5 rounded-xl border-0 shadow-sm"
            style={{ backgroundColor: '#374151' }}
          >
            {tabs.map(tab => {
              const Icon = tab.icon;
              return (
                <TabsTrigger 
                  key={tab.key} 
                  value={tab.key}
                  className="flex flex-col items-center gap-1.5 h-11 px-3 rounded-lg transition-all duration-200 font-medium"
                  style={{
                    backgroundColor: activeTab === tab.key ? '#1f2937' : 'transparent',
                    color: activeTab === tab.key ? '#f3f4f6' : '#9ca3af',
                    boxShadow: activeTab === tab.key ? '0 1px 3px rgba(0, 0, 0, 0.1)' : 'none'
                  }}
                  onMouseEnter={(e) => {
                    if (activeTab !== tab.key) {
                      e.currentTarget.style.color = '#d1d5db';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (activeTab !== tab.key) {
                      e.currentTarget.style.color = '#9ca3af';
                    }
                  }}
                >
                  <Icon className="h-4 w-4" style={{ color: activeTab === tab.key ? '#f3f4f6' : '#9ca3af' }} />
                  <span className="text-xs hidden sm:inline">{tab.label}</span>
                </TabsTrigger>
              );
            })}
          </TabsList>
        </div>

        {/* Business Plans List Tab */}
        <TabsContent value="plans-list" className="space-y-6">
          <Card className="border-0 shadow-md overflow-hidden" style={{ backgroundColor: '#1f2937' }}>
            <CardHeader className="p-6" style={{ 
              borderBottom: '1px solid #374151',
              background: 'linear-gradient(to right, #1e3a8a, #312e81)',
            }}>
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <CardTitle className="flex items-center gap-3 text-xl font-bold" style={{ color: '#f3f4f6' }}>
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#3b82f6' }}>
                      <PlusCircle className="h-5 w-5" style={{ color: '#ffffff' }} />
                    </div>
                    All Business Plans
                  </CardTitle>
                  <p className="text-sm max-w-3xl leading-relaxed" style={{ color: '#d1d5db' }}>
                    Manage and organize business plans across all offices with comprehensive CRUD operations and workflow management.
                  </p>
                </div>
                
                <div className="flex items-center gap-4">
                  <Button 
                    onClick={() => {
                      // Trigger the create modal by calling the handleCreateNewPlan function
                      handleCreateNewPlan({
                        name: '',
                        officeId: selectedOfficeId || offices[0]?.id || '',
                        year: selectedYear,
                        workflow: 'manual'
                      });
                    }}
                    style={{
                      height: '36px',
                      padding: '0 1rem',
                      fontWeight: '500',
                      backgroundColor: '#374151',
                      color: '#e5e7eb',
                      border: '2px solid #6b7280',
                      borderRadius: '8px',
                      transition: 'all 0.2s ease',
                      boxShadow: '0 2px 4px rgba(0, 0, 0, 0.2)'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = '#4b5563';
                      e.currentTarget.style.borderColor = '#9ca3af';
                      e.currentTarget.style.color = '#ffffff';
                      e.currentTarget.style.transform = 'translateY(-1px)';
                      e.currentTarget.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.25)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = '#374151';
                      e.currentTarget.style.borderColor = '#6b7280';
                      e.currentTarget.style.color = '#e5e7eb';
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.2)';
                    }}
                  >
                    <PlusCircle className="h-4 w-4 mr-2" style={{ color: '#e5e7eb' }} />
                    Create New Plan
                  </Button>
                </div>
              </div>
            </CardHeader>
            
            <CardContent className="p-0" style={{ backgroundColor: '#1f2937' }}>
              <BusinessPlansList
                offices={offices}
                onCreateNew={handleCreateNewPlan}
                onEditPlan={handleEditPlan}
                onViewPlan={handleViewPlan}
                onDeletePlan={handleDeletePlan}
                onDuplicatePlan={handleDuplicatePlan}
                onMarkOfficial={handleMarkOfficial}
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Enhanced Office Planning Tab */}
        <TabsContent value="office-planning" className="space-y-6">
          <Card className="border-0 shadow-md overflow-hidden" style={{ backgroundColor: '#1f2937' }}>
            <CardHeader className="p-6" style={{ 
              borderBottom: '1px solid #374151',
              background: 'linear-gradient(to right, #1e3a8a, #312e81)',
            }}>
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <CardTitle className="flex items-center gap-3 text-xl font-bold" style={{ color: '#f3f4f6' }}>
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#3b82f6' }}>
                      <Building2 className="h-5 w-5" style={{ color: '#ffffff' }} />
                    </div>
                    Office Business Planning
                  </CardTitle>
                  <p className="text-sm max-w-3xl leading-relaxed" style={{ color: '#d1d5db' }}>
                    Create detailed monthly plans with expandable rows for each role and level. Input recruitment, churn, price, and UTR for every role/level combination with precision and ease.
                  </p>
                </div>
                
                <div className="flex items-center gap-4">
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
                      style={{
                        height: '36px',
                        padding: '0 12px',
                        fontSize: '14px',
                        fontWeight: '500',
                        border: '1px solid #374151',
                        borderRadius: '8px',
                        backgroundColor: '#1f2937',
                        color: '#f3f4f6',
                        transition: 'all 0.2s ease'
                      }}
                      disabled={isLoading}
                    >
                      {availableYears.map(year => (
                        <option key={year} value={year}>{year}</option>
                      ))}
                    </select>
                  </div>

                </div>
              </div>
            </CardHeader>
            
            <CardContent>
              {selectedOffice ? (
                <CleanBusinessPlanTable
                  office={selectedOffice}
                  year={selectedYear}
                />
              ) : (
                <div className="text-center py-12">
                  <Building2 className="h-12 w-12 mx-auto mb-4" style={{ color: '#9ca3af' }} />
                  <h3 className="text-lg font-medium mb-2" style={{ color: '#f3f4f6' }}>Select an Office</h3>
                  <p style={{ color: '#9ca3af' }}>
                    Choose an office from the selector above to start business planning
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI Planning Tab */}
        <TabsContent value="ai-planning" className="space-y-6">
          <Card className="border-0 shadow-md overflow-hidden" style={{ backgroundColor: '#1f2937' }}>
            <CardHeader className="p-6" style={{ 
              borderBottom: '1px solid #374151',
              background: 'linear-gradient(to right, #1e3a8a, #312e81)',
            }}>
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <CardTitle className="flex items-center gap-3 text-xl font-bold" style={{ color: '#f3f4f6' }}>
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#3b82f6' }}>
                      <Bot className="h-5 w-5" style={{ color: '#ffffff' }} />
                    </div>
                    AI-Facilitated Business Planning
                  </CardTitle>
                  <p className="text-sm max-w-3xl leading-relaxed" style={{ color: '#d1d5db' }}>
                    Simple AI-guided conversations for business planning. Get historical data context while discussing recruitment targets, 
                    sales goals, and pricing strategies through focused question flows.
                  </p>
                </div>
                
                <div className="flex items-center gap-4">
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
                      style={{
                        height: '36px',
                        padding: '0 12px',
                        fontSize: '14px',
                        fontWeight: '500',
                        border: '1px solid #374151',
                        borderRadius: '8px',
                        backgroundColor: '#1f2937',
                        color: '#f3f4f6',
                        transition: 'all 0.2s ease'
                      }}
                      disabled={isLoading}
                    >
                      {availableYears.map(year => (
                        <option key={year} value={year}>{year}</option>
                      ))}
                    </select>
                  </div>

                  <div className="flex items-center gap-3 pl-4" style={{ borderLeft: '1px solid #374151' }}>
                    <Badge variant="outline" className="border-blue-400 text-blue-400">
                      <Sparkles className="h-3 w-3 mr-1" />
                      AI-Powered
                    </Badge>
                  </div>
                </div>
              </div>
            </CardHeader>
            
            <CardContent className="p-0">
              {selectedOffice ? (
                <SimpleAIPlanningInterface
                  office={selectedOffice}
                  year={selectedYear}
                  onYearChange={handleYearChange}
                  onTabChange={handleTabChange}
                />
              ) : (
                <div className="text-center py-12">
                  <Bot className="h-12 w-12 mx-auto mb-4" style={{ color: '#9ca3af' }} />
                  <h3 className="text-lg font-medium mb-2" style={{ color: '#f3f4f6' }}>Select an Office</h3>
                  <p style={{ color: '#9ca3af' }}>
                    Choose an office from the selector above to start AI-facilitated planning
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Aggregated Planning Tab */}
        <TabsContent value="aggregated" className="space-y-6">
          <Card className="border-0 shadow-md overflow-hidden" style={{ backgroundColor: '#1f2937' }}>
            <CardHeader className="p-6" style={{ 
              borderBottom: '1px solid #374151',
              background: 'linear-gradient(to right, #1e3a8a, #312e81)',
            }}>
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <CardTitle className="flex items-center gap-3 text-xl font-bold" style={{ color: '#f3f4f6' }}>
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#3b82f6' }}>
                      <Globe className="h-5 w-5" style={{ color: '#ffffff' }} />
                    </div>
                    Company-Wide Business Planning
                  </CardTitle>
                  <p className="text-sm max-w-3xl leading-relaxed" style={{ color: '#d1d5db' }}>
                    View and manage aggregated business plans across all offices with unified metrics and consolidated insights.
                  </p>
                </div>
              </div>
            </CardHeader>
            
            <CardContent className="p-6" style={{ backgroundColor: '#1f2937' }}>
              <CleanBusinessPlanTable
                office={{
                  id: 'aggregated',
                  name: 'Aggregated View',
                  country: 'Multiple',
                  city: 'Multiple',
                  currency: 'EUR',
                  timezone: 'UTC',
                  isActive: true,
                  createdAt: new Date().toISOString(),
                  updatedAt: new Date().toISOString(),
                  baseline_fte: {},
                  salaries: {},
                  economic_parameters: {
                    monthly_hours: 160,
                    working_days_per_month: 20,
                    revenue_recognition_delay_months: 0,
                    churn_rate_annual: 0.15,
                    recruitment_cost_per_hire: 5000,
                    onboarding_time_months: 3
                  }
                }}
                year={selectedYear}
                isAggregated={true}
                selectedOffices={offices.slice(0, 3).map(office => office.id)}
              />
            </CardContent>
          </Card>
        </TabsContent>


        {/* Simulation Integration Tab */}
        <TabsContent value="simulation" className="space-y-6">
          <Card className="border-0 shadow-md overflow-hidden" style={{ backgroundColor: '#1f2937' }}>
            <CardHeader className="p-6" style={{ 
              borderBottom: '1px solid #374151',
              background: 'linear-gradient(to right, #1e3a8a, #312e81)',
            }}>
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <CardTitle className="flex items-center gap-3 text-xl font-bold" style={{ color: '#f3f4f6' }}>
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#3b82f6' }}>
                      <Play className="h-5 w-5" style={{ color: '#ffffff' }} />
                    </div>
                    Scenario Planning Integration
                  </CardTitle>
                  <p className="text-sm max-w-3xl leading-relaxed" style={{ color: '#d1d5db' }}>
                    Create scenarios using business plans as baselines for advanced workforce simulation and strategic planning.
                  </p>
                </div>
              </div>
            </CardHeader>
            
            <CardContent style={{ backgroundColor: '#1f2937' }}>
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
          <Card className="border-0 shadow-md overflow-hidden" style={{ backgroundColor: '#1f2937' }}>
            <CardHeader className="p-6" style={{ 
              borderBottom: '1px solid #374151',
              background: 'linear-gradient(to right, #1e3a8a, #312e81)',
            }}>
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <CardTitle className="flex items-center gap-3 text-xl font-bold" style={{ color: '#f3f4f6' }}>
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#3b82f6' }}>
                      <Settings className="h-5 w-5" style={{ color: '#ffffff' }} />
                    </div>
                    Business Planning Settings
                  </CardTitle>
                  <p className="text-sm max-w-3xl leading-relaxed" style={{ color: '#d1d5db' }}>
                    Configure templates, validation rules, and integration settings for enhanced business planning workflows.
                  </p>
                </div>
              </div>
            </CardHeader>
            
            <CardContent style={{ backgroundColor: '#1f2937' }}>
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium mb-4" style={{ color: '#f3f4f6' }}>Planning Templates</h3>
                  <p className="mb-4" style={{ color: '#9ca3af' }}>
                    Manage default templates for new business plans
                  </p>
                  <Button variant="outline" disabled>
                    <PlusCircle className="h-4 w-4 mr-2" />
                    Create Template
                  </Button>
                </div>

                <div>
                  <h3 className="text-lg font-medium mb-4" style={{ color: '#f3f4f6' }}>Validation Rules</h3>
                  <p className="mb-4" style={{ color: '#9ca3af' }}>
                    Configure business rules and validation constraints
                  </p>
                  <Button variant="outline" disabled>
                    <Settings className="h-4 w-4 mr-2" />
                    Configure Rules
                  </Button>
                </div>

                <div>
                  <h3 className="text-lg font-medium mb-4" style={{ color: '#f3f4f6' }}>Integration Settings</h3>
                  <p className="mb-4" style={{ color: '#9ca3af' }}>
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