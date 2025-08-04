/**
 * Simple Business Plan Table
 * 
 * Clean hierarchical table with the requested structure:
 * 📊 Starters (category group row)
 *   📄 Consultant (role group row)  
 *     📄 A, AC, C, SrC levels (individual data rows)
 *   📄 Sales (role group row)
 *     📄 A, AC, C, SrC levels (individual data rows)
 * 📊 Leavers (category group row) 
 *   📄 Consultant (role group row)
 *     📄 A, AC, C, SrC levels (individual data rows)
 * 📊 Economic (category group row)
 *   📄 Price (field group row)
 *     📄 A, AC, C, SrC levels (individual data rows)
 */
import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import { 
  Save, 
  RotateCcw,
  Users,
  DollarSign,
  TrendingUp,
  Clock,
  Calculator,
  ChevronDown,
  ChevronRight,
  BarChart3,
  FileText
} from 'lucide-react';
import { useBusinessPlanStore } from '../../stores/businessPlanStore';
import { cn } from '../../lib/utils';
import type { OfficeConfig, MonthlyPlanEntry, StandardRole, StandardLevel } from '../../types/office';

interface SimpleBusinessPlanTableProps {
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

const ROLES = ['Consultant', 'Sales', 'Recruitment', 'Operations'];
const LEVELS = ['A', 'AC', 'C', 'SrC'];

// Field categories for grouping
const FIELD_CATEGORIES = [
  {
    key: 'starters',
    label: 'Starters',
    icon: Users,
    fields: ['recruitment'],
    roles: ROLES
  },
  {
    key: 'leavers', 
    label: 'Leavers',
    icon: TrendingUp,
    fields: ['churn'],
    roles: ROLES
  },
  {
    key: 'economic',
    label: 'Economic',
    icon: DollarSign,
    fields: ['salary', 'price', 'utr'],
    roles: ['Consultant', 'Sales'] // Only billable roles
  }
];

export const SimpleBusinessPlanTable: React.FC<SimpleBusinessPlanTableProps> = ({
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
  const [isDirty, setIsDirty] = useState(false);
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({
    'starters': true,
    'leavers': true,
    'economic': true
  });

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
  const getCellData = useCallback((role: string, level: string, month: number): CellData => {
    const key = `${role}-${level}-${month}`;
    const existing = planDataMap.get(key);
    
    if (existing) {
      return existing;
    }
    
    return {
      role: role as StandardRole,
      level: level as StandardLevel,
      month,
      year,
      recruitment: 0,
      churn: 0,
      salary: 50000,
      price: 100,
      utr: 0.75
    };
  }, [planDataMap, year]);

  // Handle cell value change
  const handleCellChange = useCallback((
    role: string,
    level: string,
    month: number,
    field: keyof MonthlyPlanEntry,
    value: any
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

  // Toggle group expansion
  const toggleGroup = useCallback((groupKey: string) => {
    setExpandedGroups(prev => ({
      ...prev,
      [groupKey]: !prev[groupKey]
    }));
  }, []);

  // Save changes
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
  }, []);

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
    <div className="simple-business-plan-table space-y-4">
      {/* Toolbar */}
      <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg border">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Calculator className="h-4 w-4" />
            <span className="font-medium">{office.name} - {year}</span>
          </div>
          {isDirty && (
            <Badge variant="secondary" className="animate-pulse">
              Unsaved changes
            </Badge>
          )}
        </div>

        <div className="flex items-center gap-2">
          {isDirty && (
            <>
              <Button variant="outline" size="sm" onClick={handleDiscard}>
                <RotateCcw className="h-4 w-4 mr-1" />
                Discard
              </Button>
              <Button size="sm" onClick={handleSave}>
                <Save className="h-4 w-4 mr-1" />
                Save Changes
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Hierarchical Table */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-auto">
            <table className="w-full">
              <thead className="bg-muted/30 border-b border-border sticky top-0">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-semibold w-48">Category/Role/Level</th>
                  {MONTHS.map(month => (
                    <th key={month} className="px-2 py-3 text-center text-sm font-semibold w-20">{month}</th>
                  ))}
                  <th className="px-2 py-3 text-center text-sm font-semibold w-20">Total</th>
                </tr>
              </thead>
              <tbody>
                {FIELD_CATEGORIES.map(category => {
                  const isExpanded = expandedGroups[category.key];
                  const Icon = category.icon;
                  
                  return (
                    <React.Fragment key={category.key}>
                      {/* Category Group Row */}
                      <tr className="bg-muted/20 border-b border-border">
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => toggleGroup(category.key)}
                              className="h-6 w-6 p-0"
                            >
                              {isExpanded ? (
                                <ChevronDown className="h-4 w-4" />
                              ) : (
                                <ChevronRight className="h-4 w-4" />
                              )}
                            </Button>
                            <BarChart3 className="h-4 w-4 text-muted-foreground" />
                            <span className="font-semibold">{category.label}</span>
                          </div>
                        </td>
                        {MONTHS.map(month => (
                          <td key={month} className="px-2 py-3 text-center text-sm text-muted-foreground">-</td>
                        ))}
                        <td className="px-2 py-3 text-center text-sm text-muted-foreground">-</td>
                      </tr>

                      {/* Role and Level Rows */}
                      {isExpanded && category.roles.map(role => (
                        <React.Fragment key={`${category.key}-${role}`}>
                          {/* Role Group Row */}
                          <tr className="bg-muted/10 border-b border-border">
                            <td className="px-8 py-2">
                              <div className="flex items-center gap-2">
                                <FileText className="h-4 w-4 text-muted-foreground" />
                                <span className="font-medium text-sm">{role}</span>
                              </div>
                            </td>
                            {MONTHS.map(month => (
                              <td key={month} className="px-2 py-2 text-center text-sm text-muted-foreground">-</td>
                            ))}
                            <td className="px-2 py-2 text-center text-sm text-muted-foreground">-</td>
                          </tr>

                          {/* Level Data Rows */}
                          {(role === 'Operations' ? ['General'] : LEVELS).map(level => (
                            <tr key={`${category.key}-${role}-${level}`} className="border-b border-border hover:bg-muted/30">
                              <td className="px-12 py-2">
                                <div className="flex items-center gap-2">
                                  <FileText className="h-3 w-3 text-muted-foreground" />
                                  <span className="text-sm">{level}</span>
                                </div>
                              </td>
                              {MONTHS.map((month, monthIndex) => {
                                const monthNum = monthIndex + 1;
                                const cellData = getCellData(role, level, monthNum);
                                const fieldKey = category.fields[0]; // Use first field for now
                                const value = cellData[fieldKey as keyof MonthlyPlanEntry] as number;
                                
                                return (
                                  <td key={month} className="px-1 py-1">
                                    <Input
                                      type="number"
                                      value={value || 0}
                                      onChange={(e) => handleCellChange(
                                        role, 
                                        level, 
                                        monthNum, 
                                        fieldKey as keyof MonthlyPlanEntry, 
                                        Number(e.target.value)
                                      )}
                                      className="h-8 w-16 text-xs text-center border-none bg-transparent hover:bg-muted/50 focus:bg-background"
                                    />
                                  </td>
                                );
                              })}
                              <td className="px-2 py-2 text-center text-sm font-mono">
                                {MONTHS.reduce((total, _, monthIndex) => {
                                  const cellData = getCellData(role, level, monthIndex + 1);
                                  const fieldKey = category.fields[0];
                                  return total + (cellData[fieldKey as keyof MonthlyPlanEntry] as number || 0);
                                }, 0)}
                              </td>
                            </tr>
                          ))}
                        </React.Fragment>
                      ))}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};