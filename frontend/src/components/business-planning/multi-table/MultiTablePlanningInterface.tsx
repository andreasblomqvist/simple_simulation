/**
 * Multi-Table Planning Interface - Clean Minimalistic Dark Mode
 * 
 * Compact, readable interface with minimal colors and clean design
 * Focus on readability and modern minimal aesthetics
 */
import React, { useState, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../ui/tabs';
import { Badge } from '../../ui/badge';
import { Button } from '../../ui/button';
import { Progress } from '../../ui/progress';
import { 
  Users, 
  DollarSign, 
  BarChart3, 
  Zap,
  Save,
  RotateCcw,
  CheckCircle2,
  Clock,
  UserPlus,
  UserMinus,
  ArrowUpRight,
  TrendingUp,
  Target
} from 'lucide-react';
import { WorkforcePlanningTable } from './WorkforcePlanningTable';
import { FinancialPlanningTable } from './FinancialPlanningTable';
import { MonthlyOverviewTable } from './MonthlyOverviewTable';
import { QuickEntryTable } from './QuickEntryTable';
import type { OfficeConfig } from '../../../types/office';
import { cn } from '../../../lib/utils';

interface MultiTablePlanningInterfaceProps {
  office: OfficeConfig;
  year: number;
  onYearChange: (year: number) => void;
}

type TableTab = 'workforce' | 'financial' | 'overview' | 'quick-entry';

// Mock validation results for progress indicators
const mockValidationResults: Record<TableTab, { completed: number; total: number; warnings: number }> = {
  workforce: { completed: 8, total: 12, warnings: 2 },
  financial: { completed: 10, total: 12, warnings: 1 },
  overview: { completed: 12, total: 12, warnings: 0 },
  'quick-entry': { completed: 4, total: 6, warnings: 0 }
};

export const MultiTablePlanningInterface: React.FC<MultiTablePlanningInterfaceProps> = ({
  office,
  year,
  onYearChange
}) => {
  const [activeTab, setActiveTab] = useState<TableTab>('workforce');
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  const handleTabChange = useCallback((value: string) => {
    setActiveTab(value as TableTab);
  }, []);

  const handleSave = useCallback(async () => {
    setIsSaving(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    setHasUnsavedChanges(false);
    setLastSaved(new Date());
    setIsSaving(false);
  }, []);

  const handleDiscard = useCallback(() => {
    setHasUnsavedChanges(false);
  }, []);

  const handleDataChange = useCallback(() => {
    setHasUnsavedChanges(true);
  }, []);

  const getProgressPercentage = (tab: TableTab) => {
    const results = mockValidationResults[tab];
    return Math.round((results.completed / results.total) * 100);
  };

  // Mock KPI data for demonstration - in real implementation, calculate from business plan data
  const mockKpis = {
    totalRecruitment: 48,
    totalChurn: 24,
    netRecruitment: 24,
    netRecruitmentPercent: 15.8,
    netRevenue: 2150000,
    avgPriceIncrease: 5.2,
    avgTargetUTR: 78.5
  };

  const tabs = [
    {
      key: 'workforce' as TableTab,
      label: 'Workforce',
      icon: Users,
      description: 'Recruitment and churn planning'
    },
    {
      key: 'financial' as TableTab,
      label: 'Financial',
      icon: DollarSign,
      description: 'Salary and pricing planning'
    },
    {
      key: 'overview' as TableTab,
      label: 'Overview',
      icon: BarChart3,
      description: 'Summary and validation'
    },
    {
      key: 'quick-entry' as TableTab,
      label: 'Quick Entry',
      icon: Zap,
      description: 'Bulk operations'
    }
  ];

  return (
    <div className="multi-table-planning-interface space-y-3 p-4" style={{ backgroundColor: '#0a0a0a', minHeight: '100vh' }}>
      {/* Clean Header */}
      <div className="flex items-center justify-between py-2">
        <div className="flex items-center gap-3">
          <h2 className="text-lg font-medium" style={{ color: '#f9f9f9' }}>
            {office.name} {year}
          </h2>
          <Badge variant="outline" className="text-xs" style={{ backgroundColor: '#374151', color: '#d1d5db', borderColor: '#4b5563' }}>
            Multi-Table
          </Badge>
        </div>

        <div className="flex items-center gap-3">
          {lastSaved && (
            <div className="flex items-center gap-1.5 text-xs text-gray-400">
              <CheckCircle2 className="h-3 w-3" />
              <span>Saved {lastSaved.toLocaleTimeString()}</span>
            </div>
          )}
          
          {hasUnsavedChanges && (
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="h-5 px-2 text-xs bg-gray-800 text-gray-300 border-gray-600">
                <Clock className="h-3 w-3 mr-1" />
                Unsaved
              </Badge>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handleDiscard}
                className="h-6 px-2 text-xs bg-gray-800 text-gray-300 border-gray-600 hover:bg-gray-700"
              >
                <RotateCcw className="h-3 w-3 mr-1" />
                Discard
              </Button>
              <Button 
                size="sm" 
                onClick={handleSave}
                disabled={isSaving}
                className="h-6 px-2 text-xs bg-gray-100 text-gray-900 hover:bg-gray-200"
              >
                <Save className="h-3 w-3 mr-1" />
                {isSaving ? 'Saving...' : 'Save'}
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Progress Overview - Force Dark Mode */}
      <div className="grid grid-cols-4 gap-3 p-3 rounded-lg" style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
        {tabs.map((tab) => {
          const results = mockValidationResults[tab.key];
          const percentage = getProgressPercentage(tab.key);
          const Icon = tab.icon;
          
          return (
            <div key={tab.key} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Icon className="h-3 w-3" style={{ color: '#9ca3af' }} />
                  <span className="text-xs font-medium" style={{ color: '#f3f4f6' }}>
                    {tab.label}
                  </span>
                </div>
                <span className="text-xs" style={{ color: '#9ca3af' }}>
                  {results.completed}/{results.total}
                </span>
              </div>
              
              <div className="space-y-1">
                <div className="h-1 rounded-full overflow-hidden" style={{ backgroundColor: '#1f2937' }}>
                  <div 
                    className="h-full rounded-full transition-all duration-300"
                    style={{ width: `${percentage}%`, backgroundColor: '#9ca3af' }}
                  />
                </div>
                <span className="text-xs" style={{ color: '#9ca3af' }}>
                  {percentage}%
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* KPI Cards Row */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {/* Total Recruitment */}
        <Card style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
          <CardContent className="p-3" style={{ backgroundColor: '#1f2937' }}>
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <UserPlus className="h-3 w-3 text-green-400" />
                <span className="text-xs font-medium text-gray-400">Total Recruitment</span>
              </div>
              <div className="text-lg font-bold text-white">
                {mockKpis.totalRecruitment.toLocaleString()}
              </div>
              <div className="text-xs text-gray-400">yearly</div>
            </div>
          </CardContent>
        </Card>

        {/* Total Churn */}
        <Card style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
          <CardContent className="p-3" style={{ backgroundColor: '#1f2937' }}>
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <UserMinus className="h-3 w-3 text-red-400" />
                <span className="text-xs font-medium text-gray-400">Total Churn</span>
              </div>
              <div className="text-lg font-bold text-white">
                {mockKpis.totalChurn.toLocaleString()}
              </div>
              <div className="text-xs text-gray-400">yearly</div>
            </div>
          </CardContent>
        </Card>

        {/* Net Recruitment */}
        <Card style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
          <CardContent className="p-3" style={{ backgroundColor: '#1f2937' }}>
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <ArrowUpRight className={`h-3 w-3 ${mockKpis.netRecruitment >= 0 ? 'text-green-400' : 'text-red-400'}`} />
                <span className="text-xs font-medium text-gray-400">Net Recruitment</span>
              </div>
              <div className={`text-lg font-bold ${mockKpis.netRecruitment >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {mockKpis.netRecruitment >= 0 ? '+' : ''}{mockKpis.netRecruitment.toLocaleString()}
              </div>
              <div className={`text-xs ${mockKpis.netRecruitmentPercent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {mockKpis.netRecruitmentPercent >= 0 ? '+' : ''}{mockKpis.netRecruitmentPercent.toFixed(1)}% growth
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Net Revenue */}
        <Card style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
          <CardContent className="p-3" style={{ backgroundColor: '#1f2937' }}>
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <DollarSign className="h-3 w-3 text-blue-400" />
                <span className="text-xs font-medium text-gray-400">Net Revenue</span>
              </div>
              <div className="text-lg font-bold text-white">
                €{Math.round(mockKpis.netRevenue / 1000).toLocaleString()}K
              </div>
              <div className="text-xs text-gray-400">yearly</div>
            </div>
          </CardContent>
        </Card>

        {/* Price Increase */}
        <Card style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
          <CardContent className="p-3" style={{ backgroundColor: '#1f2937' }}>
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-3 w-3 text-purple-400" />
                <span className="text-xs font-medium text-gray-400">Price Increase</span>
              </div>
              <div className="text-lg font-bold text-white">
                {mockKpis.avgPriceIncrease >= 0 ? '+' : ''}{mockKpis.avgPriceIncrease.toFixed(1)}%
              </div>
              <div className="text-xs text-gray-400">vs baseline</div>
            </div>
          </CardContent>
        </Card>

        {/* Target UTR */}
        <Card style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
          <CardContent className="p-3" style={{ backgroundColor: '#1f2937' }}>
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <Target className="h-3 w-3 text-yellow-400" />
                <span className="text-xs font-medium text-gray-400">Target UTR</span>
              </div>
              <div className="text-lg font-bold text-white">
                {mockKpis.avgTargetUTR.toFixed(1)}%
              </div>
              <div className="text-xs text-gray-400">average</div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Clean Tab Navigation */}
      <Tabs value={activeTab} onValueChange={handleTabChange} className="space-y-3">
        <TabsList className="grid w-full grid-cols-4 h-9 p-0.5 rounded-lg" style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const percentage = getProgressPercentage(tab.key);
            return (
              <TabsTrigger 
                key={tab.key}
                value={tab.key}
                className={cn(
                  "flex items-center gap-2 relative h-8 px-3 rounded-md transition-all text-xs font-medium",
                  "data-[state=active]:bg-gray-700 data-[state=active]:text-gray-100",
                  "data-[state=inactive]:text-gray-400 data-[state=inactive]:hover:text-gray-200"
                )}
              >
                <Icon className="h-3 w-3" />
                <span className="hidden sm:inline">{tab.label}</span>
              </TabsTrigger>
            );
          })}
        </TabsList>

        {/* Tab Content - Force Dark Cards */}
        <TabsContent value="workforce">
          <Card className="border-0" style={{ backgroundColor: '#111827', border: '1px solid #374151' }}>
            <CardHeader className="p-3" style={{ borderBottom: '1px solid #374151', backgroundColor: '#1f2937' }}>
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4" style={{ color: '#9ca3af' }} />
                <CardTitle className="text-sm font-medium" style={{ color: '#f3f4f6' }}>
                  Workforce Planning
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <WorkforcePlanningTable
                office={office}
                year={year}
                onDataChange={handleDataChange}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="financial">
          <Card className="border border-gray-700 bg-gray-900">
            <CardHeader className="border-b border-gray-700 bg-gray-800 p-3">
              <div className="flex items-center gap-2">
                <DollarSign className="h-4 w-4 text-gray-400" />
                <CardTitle className="text-sm font-medium text-gray-100">
                  Financial Planning
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <FinancialPlanningTable
                office={office}
                year={year}
                onDataChange={handleDataChange}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="overview">
          <Card className="border border-gray-700 bg-gray-900">
            <CardHeader className="border-b border-gray-700 bg-gray-800 p-3">
              <div className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4 text-gray-400" />
                <CardTitle className="text-sm font-medium text-gray-100">
                  Monthly Overview
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <MonthlyOverviewTable
                office={office}
                year={year}
                onDataChange={handleDataChange}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="quick-entry">
          <Card className="border border-gray-700 bg-gray-900">
            <CardHeader className="border-b border-gray-700 bg-gray-800 p-3">
              <div className="flex items-center gap-2">
                <Zap className="h-4 w-4 text-gray-400" />
                <CardTitle className="text-sm font-medium text-gray-100">
                  Quick Entry
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <QuickEntryTable
                office={office}
                year={year}
                onDataChange={handleDataChange}
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};