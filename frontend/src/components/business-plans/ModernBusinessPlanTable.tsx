/**
 * Modern Business Plan Table Component
 * 
 * Unified implementation replacing the legacy business plan table
 * Uses the new PlanningDataTable for consistent editing experience
 */
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { LoadingSpinner } from '../ui/loading-states';
import { PlanningDataTable, PlanningRow, PlanningEntry, buildPlanningTableData } from '../ui/planning-data-table';
import { 
  MonthlyBusinessPlan, 
  MonthlyPlanEntry, 
  OfficeConfig, 
  STANDARD_ROLES, 
  STANDARD_LEVELS,
  StandardRole,
  StandardLevel
} from '../../types/office';
import { useBusinessPlanStore } from '../../stores/businessPlanStore';
import { Calendar, Save, RotateCcw, Users, TrendingUp } from 'lucide-react';

interface ModernBusinessPlanTableProps {
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

const MONTHS = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
];

export const ModernBusinessPlanTable: React.FC<ModernBusinessPlanTableProps> = ({
  office,
  year,
  onYearChange
}) => {
  const {
    monthlyPlans,
    currentWorkforce,
    loading,
    error,
    loadBusinessPlans,
    loadWorkforceDistribution,
    updatePlanEntry,
    createMonthlyPlan,
    bulkUpdatePlans,
    clearError
  } = useBusinessPlanStore();

  const [localChanges, setLocalChanges] = useState<Map<string, CellData>>(new Map());
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  // Load data when office or year changes
  useEffect(() => {
    if (office?.id) {
      loadBusinessPlans(office.id, year);
      loadWorkforceDistribution(office.id);
    }
  }, [office?.id, year, loadBusinessPlans, loadWorkforceDistribution]);

  // Create a map of existing plan data for quick lookup
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

  // Build planning table data
  const planningData = useMemo(() => {
    const rows: PlanningRow[] = [];
    let rowIndex = 0;

    STANDARD_ROLES.forEach(role => {
      const levels = role === 'Operations' ? ['General'] : STANDARD_LEVELS.slice(0, 3); // Show first 3 levels
      
      // Add role group row
      const roleRow: PlanningRow = {
        id: `role-${rowIndex++}`,
        role,
        month: 1,
        recruitment: 0,
        churn: 0,
        price: 100,
        utr: 0.75,
        salary: 50000,
        isExpanded: true
      };
      rows.push(roleRow);

      // Add level rows
      levels.forEach(level => {
        const key = `${role}-${level}-1`; // Use January as reference
        const cellData = planDataMap.get(key) || {
          role,
          level,
          month: 1,
          year,
          recruitment: 0,
          churn: 0,
          price: 100,
          utr: 0.75,
          salary: 50000
        };

        const levelRow: PlanningRow = {
          id: `${role}-${level}`,
          role,
          level,
          month: cellData.month,
          recruitment: cellData.recruitment,
          churn: cellData.churn,
          price: cellData.price || 100,
          utr: cellData.utr || 0.75,
          salary: cellData.salary,
          isSubLevel: true,
          isDirty: cellData.isDirty
        };
        rows.push(levelRow);
      });
    });

    return rows;
  }, [planDataMap, year]);

  // Handle cell edits
  const handleCellEdit = useCallback((
    rowId: string, 
    field: keyof PlanningEntry, 
    value: number
  ) => {
    const [role, level] = rowId.split('-');
    
    // Update all months for now (simplified implementation)
    for (let month = 1; month <= 12; month++) {
      const key = `${role}-${level}-${month}`;
      const currentData = planDataMap.get(key) || {
        role: role as StandardRole,
        level: level as StandardLevel,
        month,
        year,
        recruitment: 0,
        churn: 0,
        price: 100,
        utr: 0.75,
        salary: 50000
      };
      
      const updatedData: CellData = {
        ...currentData,
        [field]: value,
        isDirty: true
      };
      
      setLocalChanges(prev => new Map(prev).set(key, updatedData));
    }
    
    setHasUnsavedChanges(true);
  }, [planDataMap, year]);

  // Handle row expansion
  const handleRowExpand = useCallback((rowId: string, expanded: boolean) => {
    // Implementation for row expansion
    console.log('Row expand:', rowId, expanded);
  }, []);

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
          const updatedPlan: MonthlyBusinessPlan = {
            ...existingPlan,
            entries: [...existingPlan.entries.filter(e => 
              !entries.some(ne => ne.role === e.role && ne.level === e.level)
            ), ...entries]
          };
          
          return updatePlanEntry(existingPlan.id, entries[0]); // Simplified - handle all entries
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
      setHasUnsavedChanges(false);
      
      // Reload data
      await loadBusinessPlans(office.id, year);
      
    } catch (error) {
      console.error('Failed to save business plan changes:', error);
    }
  }, [office?.id, localChanges, monthlyPlans, year, updatePlanEntry, createMonthlyPlan, loadBusinessPlans]);

  // Discard local changes
  const handleDiscard = useCallback(() => {
    setLocalChanges(new Map());
    setHasUnsavedChanges(false);
  }, []);

  // Calculate summary statistics
  const summaryStats = useMemo(() => {
    let totalRecruitment = 0;
    let totalChurn = 0;
    let totalRevenue = 0;
    let totalSalaryCost = 0;

    planningData.forEach(row => {
      if (row.isSubLevel) {
        totalRecruitment += row.recruitment;
        totalChurn += row.churn;
        totalRevenue += (row.price || 0) * (row.utr || 0) * 160; // 160 hours/month
        totalSalaryCost += row.salary;
      }
    });

    return {
      totalRecruitment,
      totalChurn,
      totalRevenue,
      totalSalaryCost,
      netGrowth: totalRecruitment - totalChurn,
      grossMargin: totalRevenue > 0 ? ((totalRevenue - totalSalaryCost) / totalRevenue) * 100 : 0
    };
  }, [planningData]);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <LoadingSpinner size="lg" />
        <span className="ml-2">Loading business plan data...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              <CardTitle>Business Plan for {office.name} - {year}</CardTitle>
            </div>
            <div className="flex items-center gap-2">
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => onYearChange(year - 1)}
              >
                Previous Year
              </Button>
              <Badge variant="outline">{year}</Badge>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => onYearChange(year + 1)}
              >
                Next Year
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Summary statistics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{summaryStats.totalRecruitment}</div>
              <div className="text-sm text-muted-foreground">Total Recruitment</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{summaryStats.totalChurn}</div>
              <div className="text-sm text-muted-foreground">Total Churn</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{summaryStats.netGrowth}</div>
              <div className="text-sm text-muted-foreground">Net Growth</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{summaryStats.grossMargin.toFixed(1)}%</div>
              <div className="text-sm text-muted-foreground">Gross Margin</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Planning Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            <CardTitle>Monthly Planning Grid</CardTitle>
            {hasUnsavedChanges && (
              <Badge variant="secondary" className="bg-orange-100 text-orange-800">
                Unsaved Changes
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <PlanningDataTable
            data={planningData}
            months={MONTHS}
            enableEditing={true}
            enableExpansion={true}
            showSubLevels={true}
            onCellEdit={handleCellEdit}
            onRowExpand={handleRowExpand}
            onSave={handleSave}
            onDiscard={handleDiscard}
            hasUnsavedChanges={hasUnsavedChanges}
            className="business-plan-table"
          />
        </CardContent>
      </Card>

      {/* Debug Information */}
      {process.env.NODE_ENV === 'development' && (
        <Card>
          <CardHeader>
            <CardTitle>Debug Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm space-y-2">
              <p><strong>Loading:</strong> {loading.toString()}</p>
              <p><strong>Error:</strong> {error || 'None'}</p>
              <p><strong>Monthly plans:</strong> {monthlyPlans.length}</p>
              <p><strong>Local changes:</strong> {localChanges.size}</p>
              <p><strong>Current workforce:</strong> {currentWorkforce ? 'Loaded' : 'Not loaded'}</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};