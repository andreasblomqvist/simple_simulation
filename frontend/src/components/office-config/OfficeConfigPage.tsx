/**
 * Main office configuration page component
 * Provides tabs for different office management sections
 */
import React, { useState, useEffect } from 'react';
import type { OfficeConfig } from '../../types/office';
import { useBusinessPlanStore } from '../../stores/businessPlanStore';
import { ModernBusinessPlanTable } from '../business-plans/ModernBusinessPlanTable';
import { OfficeOverviewTab } from './OfficeOverviewTab';
import { WorkforceTab } from './WorkforceTab';
import { SeniorityDistributionTab } from './SeniorityDistributionTab';
import { SalaryLadderTab } from './SalaryLadderTab';
import { ProgressionTab } from './ProgressionTab';
import { OfficeSettingsTab } from './OfficeSettingsTab';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { ErrorBoundary } from '../ui/ErrorBoundary';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import { Button } from '../ui/button';
import { X, BarChart3, Calendar, Users, Clock, DollarSign, TrendingUp, Settings } from 'lucide-react';
import './OfficeConfigPage.css';

interface OfficeConfigPageProps {
  office: OfficeConfig;
  onOfficeUpdate: (office: OfficeConfig) => void;
}

type TabKey = 'overview' | 'business-plans' | 'workforce' | 'seniority' | 'salary' | 'progression' | 'settings';

const tabs = [
  { key: 'overview' as TabKey, label: 'Overview', icon: BarChart3 },
  { key: 'business-plans' as TabKey, label: 'Business Plans', icon: Calendar },
  { key: 'workforce' as TabKey, label: 'Workforce', icon: Users },
  { key: 'seniority' as TabKey, label: 'Seniority', icon: Clock },
  { key: 'salary' as TabKey, label: 'Salary', icon: DollarSign },
  { key: 'progression' as TabKey, label: 'Progression', icon: TrendingUp },
  { key: 'settings' as TabKey, label: 'Settings', icon: Settings },
];

export const OfficeConfigPage: React.FC<OfficeConfigPageProps> = ({
  office,
  onOfficeUpdate
}) => {
  const [activeTab, setActiveTab] = useState<TabKey>('overview');
  const [loading, setLoading] = useState(false);
  
  const {
    loadOfficeSummary,
    loading: businessPlanLoading,
    error: businessPlanError,
    clearError
  } = useBusinessPlanStore();

  // Load office data when office changes
  useEffect(() => {
    if (office?.id) {
      setLoading(true);
      clearError();
      
      loadOfficeSummary(office.id)
        .catch(error => {
          console.error('Failed to load office summary:', error);
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [office?.id, loadOfficeSummary, clearError]);

  const handleTabChange = (tabKey: TabKey) => {
    setActiveTab(tabKey);
  };

  const isLoading = loading || businessPlanLoading;

  const getJourneyBadgeVariant = (journey: string) => {
    switch (journey.toLowerCase()) {
      case 'emerging':
        return 'default';
      case 'established':
        return 'secondary';
      case 'mature':
        return 'outline';
      default:
        return 'default';
    }
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return <OfficeOverviewTab office={office} />;
      case 'business-plans':
        return <BusinessPlansTab office={office} />;
      case 'workforce':
        return <WorkforceTab office={office} />;
      case 'seniority':
        return <SeniorityDistributionTab office={office} />;
      case 'salary':
        return <SalaryLadderTab office={office} />;
      case 'progression':
        return <ProgressionTab office={office} />;
      case 'settings':
        return <OfficeSettingsTab office={office} onUpdate={onOfficeUpdate} />;
      default:
        return <div>Tab content not implemented</div>;
    }
  };

  return (
    <ErrorBoundary>
      <div className="office-config-page">
        {/* Page Header */}
        <Card className="mb-6 border-0 shadow-none">
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <CardTitle className="text-3xl font-semibold">{office.name}</CardTitle>
                <div className="flex items-center gap-3">
                  <Badge variant={getJourneyBadgeVariant(office.journey)}>
                    {office.journey}
                  </Badge>
                  <span className="text-sm text-muted-foreground font-mono">
                    {office.timezone}
                  </span>
                </div>
              </div>
              
              {isLoading && (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <LoadingSpinner size="small" />
                  <span className="text-sm">Loading...</span>
                </div>
              )}
            </div>
          </CardHeader>
        </Card>

        {/* Error Display */}
        {businessPlanError && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription className="flex items-center justify-between">
              <span>{businessPlanError}</span>
              <Button 
                variant="ghost"
                size="icon"
                onClick={clearError}
                className="ml-2 h-6 w-6"
              >
                <X className="h-4 w-4" />
              </Button>
            </AlertDescription>
          </Alert>
        )}

        {/* Tab Navigation */}
        <Tabs value={activeTab} onValueChange={(value) => handleTabChange(value as TabKey)} className="w-full">
          <TabsList className="grid w-full grid-cols-7 mb-6">
            {tabs.map(tab => {
              const IconComponent = tab.icon;
              return (
                <TabsTrigger key={tab.key} value={tab.key} className="flex items-center gap-2">
                  <IconComponent className="h-4 w-4" />
                  <span className="hidden sm:inline">{tab.label}</span>
                </TabsTrigger>
              );
            })}
          </TabsList>

          <TabsContent value={activeTab} className="mt-0">
            {renderTabContent()}
          </TabsContent>
        </Tabs>
      </div>
    </ErrorBoundary>
  );
};

// Tab components are now imported at the top of the file

const BusinessPlansTab: React.FC<{ office: OfficeConfig }> = ({ office }) => {
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [hasError, setHasError] = useState(false);
  
  console.log('[DEBUG] BusinessPlansTab rendered for office:', office?.name);
  
  // Error boundary for BusinessPlanTable
  if (hasError) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center space-y-4">
            <h3 className="text-2xl font-semibold">Business Plans for {office.name}</h3>
            <p className="text-muted-foreground">
              Unable to load business plan data. Please try refreshing the page.
            </p>
            <Button 
              onClick={() => setHasError(false)}
            >
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <div className="h-full">
      <ErrorBoundary onError={(error, errorInfo) => {
        console.error('[DEBUG] BusinessPlanTable error:', error, errorInfo);
        setHasError(true);
      }}>
        <ModernBusinessPlanTable
          office={office}
          year={selectedYear}
          onYearChange={setSelectedYear}
        />
      </ErrorBoundary>
    </div>
  );
};

// All tab components are now imported from separate files