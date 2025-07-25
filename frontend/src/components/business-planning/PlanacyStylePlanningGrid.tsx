/**
 * Planacy-Style Planning Grid
 * 
 * Professional spreadsheet-style interface for business planning
 * Matches Planacy's design with modern React implementation
 */
import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import { 
  Save, 
  RotateCcw, 
  Copy, 
  Trash2, 
  Calculator,
  TrendingUp,
  DollarSign,
  Users
} from 'lucide-react';
import { useBusinessPlanStore } from '../../stores/businessPlanStore';
import { PlanningGridToolbar } from './PlanningGridToolbar';
import { PlanningCell } from './PlanningCell';
import { PlanningRoleRow } from './PlanningRoleRow';
import { PlanningMonthlySummary } from './PlanningMonthlySummary';
import { PlanningCalculations } from './PlanningCalculations';
import type { OfficeConfig, MonthlyPlanEntry, StandardRole, StandardLevel } from '../../types/office';
import { STANDARD_ROLES, STANDARD_LEVELS } from '../../types/office';

interface PlanacyStylePlanningGridProps {
  office: OfficeConfig;
  year: number;
  onYearChange: (year: number) => void;
}

interface CellData extends MonthlyPlanEntry {
  planId?: string;
  month: number;
  year: number;
  isDirty?: boolean;
}

interface SummaryData {
  recruitment: number;
  churn: number;
  netGrowth: number;
  revenue: number;
  cost: number;
  margin: number;
}

const MONTHS = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
];

const CELL_FIELDS = [
  { key: 'recruitment' as const, label: 'Recruitment', type: 'number', min: 0 },
  { key: 'churn' as const, label: 'Churn', type: 'number', min: 0 },
  { key: 'price' as const, label: 'Price (€/h)', type: 'number', min: 0 },
  { key: 'utr' as const, label: 'UTR', type: 'number', min: 0, max: 1, step: 0.01 },
  { key: 'salary' as const, label: 'Salary (€)', type: 'number', min: 0 }
];

export const PlanacyStylePlanningGrid: React.FC<PlanacyStylePlanningGridProps> = ({
  office,
  year,
  onYearChange
}) => {
  const {
    monthlyPlans,
    loading,
    error,
    loadBusinessPlans,
    createMonthlyPlan,
    updateMonthlyPlan,
    clearError
  } = useBusinessPlanStore();

  const [localChanges, setLocalChanges] = useState<Map<string, CellData>>(new Map());
  const [selectedCell, setSelectedCell] = useState<{ role: string; level: string; month: number; field: string } | null>(null);
  const [isDirty, setIsDirty] = useState(false);
  const [showCalculations, setShowCalculations] = useState(true);

  // Load data when office or year changes
  useEffect(() => {
    if (office?.id) {
      loadBusinessPlans(office.id, year);
    }
  }, [office?.id, year, loadBusinessPlans]);

  // Create data map for quick lookup
  const planDataMap = useMemo(() => {
    const map = new Map<string, CellData>();
    
    monthlyPlans.forEach(plan => {
      plan.entries.forEach(entry => {
        const key = `${entry.role}-${entry.level}-${plan.month}`;
        map.set(key, {
          ...entry,
          planId: plan.id,
          month: plan.month,
          year: plan.year
        });
      });
    });
    
    // Apply local changes
    localChanges.forEach((cellData, key) => {
      map.set(key, { ...cellData, isDirty: true });
    });
    
    return map;
  }, [monthlyPlans, localChanges]);

  // Get cell data with defaults
  const getCellData = useCallback((role: StandardRole, level: StandardLevel, month: number): CellData => {
    const key = `${role}-${level}-${month}`;
    const existing = planDataMap.get(key);
    
    if (existing) {
      return existing;
    }
    
    // Return default values based on office configuration
    const officeRoleData = office.roles?.[role];
    const levelData = officeRoleData?.[level];
    
    return {
      role,
      level,
      month,
      year,
      recruitment: 0,
      churn: 0,
      price: levelData?.hourlyRate || 100,
      utr: levelData?.utilization || 0.75,
      salary: levelData?.monthlySalary || 5000
    };
  }, [planDataMap, year, office.roles]);

  // Calculate summary for a month
  const getMonthSummary = useCallback((month: number): SummaryData => {
    let recruitment = 0;
    let churn = 0;
    let revenue = 0;
    let cost = 0;

    STANDARD_ROLES.forEach(role => {
      STANDARD_LEVELS.forEach(level => {
        const cellData = getCellData(role, level, month);
        recruitment += cellData.recruitment;
        churn += cellData.churn;
        revenue += cellData.price * cellData.utr * 160; // 160 hours/month
        cost += cellData.salary;
      });
    });

    const margin = revenue > 0 ? ((revenue - cost) / revenue) * 100 : 0;

    return {
      recruitment,
      churn,
      netGrowth: recruitment - churn,
      revenue,
      cost,
      margin
    };
  }, [getCellData]);

  // Calculate role summary across all months
  const getRoleSummary = useCallback((role: StandardRole, level: StandardLevel): SummaryData => {
    let recruitment = 0;
    let churn = 0;
    let revenue = 0;
    let cost = 0;

    for (let month = 1; month <= 12; month++) {
      const cellData = getCellData(role, level, month);
      recruitment += cellData.recruitment;
      churn += cellData.churn;
      revenue += cellData.price * cellData.utr * 160;
      cost += cellData.salary;
    }

    const margin = revenue > 0 ? ((revenue - cost) / revenue) * 100 : 0;

    return {
      recruitment,
      churn,
      netGrowth: recruitment - churn,
      revenue,
      cost,
      margin
    };
  }, [getCellData]);

  // Handle cell value change
  const handleCellChange = useCallback((
    role: StandardRole,
    level: StandardLevel,
    month: number,
    field: keyof MonthlyPlanEntry,
    value: number
  ) => {
    const key = `${role}-${level}-${month}`;
    const currentData = getCellData(role, level, month);
    
    const updatedData: CellData = {
      ...currentData,
      [field]: value
    };
    
    setLocalChanges(prev => new Map(prev).set(key, updatedData));
    setIsDirty(true);
  }, [getCellData]);

  // Save changes to backend
  const handleSave = useCallback(async () => {
    if (!office?.id || localChanges.size === 0) return;
    
    try {
      // Group changes by month
      const changesByMonth = new Map<number, MonthlyPlanEntry[]>();
      
      localChanges.forEach((cellData, key) => {
        const month = cellData.month;
        if (!changesByMonth.has(month)) {
          changesByMonth.set(month, []);
        }
        
        const entries = changesByMonth.get(month)!;
        entries.push({
          role: cellData.role,
          level: cellData.level,
          recruitment: cellData.recruitment,
          churn: cellData.churn,
          price: cellData.price,
          utr: cellData.utr,
          salary: cellData.salary
        });
      });
      
      // Create or update plans for each month
      const planPromises = Array.from(changesByMonth.entries()).map(async ([month, entries]) => {
        const existingPlan = monthlyPlans.find(p => p.month === month && p.year === year);
        
        if (existingPlan) {
          // Update existing plan
          const updatedPlan = {
            ...existingPlan,
            entries: [
              ...existingPlan.entries.filter(e => 
                !entries.some(ne => ne.role === e.role && ne.level === e.level)
              ),
              ...entries
            ]
          };
          
          return updateMonthlyPlan(updatedPlan);
        } else {
          // Create new plan
          return createMonthlyPlan({
            office_id: office.id,
            year,
            month,
            entries
          });
        }
      });
      
      await Promise.all(planPromises);
      
      // Clear local changes
      setLocalChanges(new Map());
      setIsDirty(false);
      
      // Reload data
      await loadBusinessPlans(office.id, year);
      
    } catch (error) {
      console.error('Failed to save business plan changes:', error);
    }
  }, [office?.id, localChanges, monthlyPlans, year, updateMonthlyPlan, createMonthlyPlan, loadBusinessPlans]);

  // Discard changes
  const handleDiscard = useCallback(() => {
    setLocalChanges(new Map());
    setIsDirty(false);
    setSelectedCell(null);
  }, []);

  // Calculate total summary
  const totalSummary = useMemo(() => {
    let recruitment = 0;
    let churn = 0;
    let revenue = 0;
    let cost = 0;

    for (let month = 1; month <= 12; month++) {
      const monthSummary = getMonthSummary(month);
      recruitment += monthSummary.recruitment;
      churn += monthSummary.churn;
      revenue += monthSummary.revenue;
      cost += monthSummary.cost;
    }

    const margin = revenue > 0 ? ((revenue - cost) / revenue) * 100 : 0;

    return {
      recruitment,
      churn,
      netGrowth: recruitment - churn,
      revenue,
      cost,
      margin
    };
  }, [getMonthSummary]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading business plan data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="planacy-style-grid space-y-4">
      {/* Toolbar */}
      <PlanningGridToolbar
        office={office}
        year={year}
        onYearChange={onYearChange}
        isDirty={isDirty}
        onSave={handleSave}
        onDiscard={handleDiscard}
        onToggleCalculations={() => setShowCalculations(!showCalculations)}
        showCalculations={showCalculations}
      />

      {/* Error Display */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>
            {error}
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

      {/* Main Grid */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              {/* Header */}
              <thead className="bg-muted/50 sticky top-0 z-10">
                <tr>
                  <th className="text-left p-3 border-r font-medium min-w-[100px]">Role</th>
                  <th className="text-left p-3 border-r font-medium min-w-[80px]">Level</th>
                  {MONTHS.map(month => (
                    <th key={month} className="text-center p-2 border-r font-medium min-w-[120px]">
                      {month}
                    </th>
                  ))}
                  <th className="text-center p-3 font-medium min-w-[120px]">Total</th>
                </tr>
              </thead>

              {/* Body */}
              <tbody>
                {STANDARD_ROLES.map(role => 
                  STANDARD_LEVELS.map(level => (
                    <tr key={`${role}-${level}`} className="border-b hover:bg-muted/30">
                      <td className="p-3 border-r font-medium">{role}</td>
                      <td className="p-3 border-r">
                        <Badge variant="outline" className="text-xs">{level}</Badge>
                      </td>
                      {Array.from({ length: 12 }, (_, monthIndex) => {
                        const month = monthIndex + 1;
                        const cellData = getCellData(role, level, month);
                        return (
                          <PlanningCell
                            key={month}
                            role={role}
                            level={level}
                            month={month}
                            field="recruitment"
                            value={cellData.recruitment}
                            onChange={(value) => handleCellChange(role, level, month, 'recruitment', value)}
                            isDirty={cellData.isDirty}
                            type="number"
                          />
                        );
                      })}
                      <td className="p-3 text-center border-l-2">
                        <div className="text-sm font-medium">
                          {getRoleSummary(role, level).netGrowth}
                        </div>
                      </td>
                    </tr>
                  ))
                )}

                {/* Monthly Summary Row */}
                <tr className="bg-muted/30 border-t-2">
                  <td className="p-3 font-medium border-r" colSpan={2}>
                    Monthly Totals
                  </td>
                  {Array.from({ length: 12 }, (_, monthIndex) => {
                    const month = monthIndex + 1;
                    const summary = getMonthSummary(month);
                    return (
                      <PlanningMonthlySummary
                        key={month}
                        month={month}
                        summary={summary}
                      />
                    );
                  })}
                  
                  {/* Total Summary */}
                  <td className="p-3 text-center border-l-2">
                    <div className="space-y-1 text-sm">
                      <div className="flex items-center justify-center gap-1">
                        <Users className="h-3 w-3" />
                        <span className="font-medium">{totalSummary.netGrowth}</span>
                      </div>
                      <div className="flex items-center justify-center gap-1">
                        <DollarSign className="h-3 w-3" />
                        <span>{Math.round(totalSummary.margin)}%</span>
                      </div>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Calculations Panel */}
      {showCalculations && (
        <PlanningCalculations
          office={office}
          year={year}
          totalSummary={totalSummary}
          getCellData={getCellData}
        />
      )}

      {/* Dirty State Indicator */}
      {isDirty && (
        <div className="fixed bottom-4 right-4 bg-background border rounded-lg shadow-lg p-4 flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 bg-yellow-500 rounded-full animate-pulse"></div>
            <span className="text-sm font-medium">Unsaved changes</span>
          </div>
          
          <div className="flex gap-2">
            <Button size="sm" onClick={handleSave}>
              <Save className="h-4 w-4 mr-1" />
              Save
            </Button>
            <Button size="sm" variant="outline" onClick={handleDiscard}>
              <RotateCcw className="h-4 w-4 mr-1" />
              Discard
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};