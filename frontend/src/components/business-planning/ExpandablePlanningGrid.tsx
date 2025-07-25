/**
 * Expandable Planning Grid
 * 
 * Professional table with expandable rows for roles and levels
 * Shows recruitment, churn, price, UTR for each role/level combination
 */
import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import { 
  ChevronDown, 
  ChevronRight, 
  Save, 
  RotateCcw,
  Users,
  DollarSign,
  TrendingUp,
  Clock,
  Calculator
} from 'lucide-react';
import { useBusinessPlanStore } from '../../stores/businessPlanStore';
import { PlanningFieldInput } from './PlanningFieldInput';
import { cn } from '../../lib/utils';
import type { OfficeConfig, MonthlyPlanEntry, StandardRole, StandardLevel } from '../../types/office';
import { 
  STANDARD_ROLES, 
  STANDARD_LEVELS, 
  LEVELED_ROLES, 
  FLAT_ROLES, 
  BILLABLE_ROLES, 
  NON_BILLABLE_ROLES 
} from '../../types/office';

interface ExpandablePlanningGridProps {
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

interface RoleExpansion {
  [role: string]: boolean;
}

interface LevelExpansion {
  [key: string]: boolean; // role-level combination
}

const MONTHS = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
];

// Helper functions
const isLeveledRole = (role: StandardRole) => LEVELED_ROLES.includes(role as any);
const isFlatRole = (role: StandardRole) => FLAT_ROLES.includes(role as any);
const isBillableRole = (role: StandardRole) => BILLABLE_ROLES.includes(role as any);
const isNonBillableRole = (role: StandardRole) => NON_BILLABLE_ROLES.includes(role as any);

// Get available fields for a role
const getAvailableFields = (role: StandardRole) => {
  const baseFields = ['recruitment', 'churn', 'salary'];
  if (isBillableRole(role)) {
    return [...baseFields, 'price', 'utr'];
  }
  return baseFields;
};

// Get available levels for a role
const getAvailableLevels = (role: StandardRole) => {
  if (isLeveledRole(role)) {
    return STANDARD_LEVELS;
  }
  return ['General']; // Flat roles use a single "General" level
};

const FIELD_CONFIG = {
  recruitment: {
    label: 'Recruitment',
    icon: Users,
    color: 'text-green-600',
    bgColor: 'bg-green-50 dark:bg-green-950/20',
    type: 'number' as const,
    min: 0,
    step: 1
  },
  churn: {
    label: 'Churn',
    icon: TrendingUp,
    color: 'text-red-600',
    bgColor: 'bg-red-50 dark:bg-red-950/20',
    type: 'number' as const,
    min: 0,
    step: 1
  },
  price: {
    label: 'Price (€/h)',
    icon: DollarSign,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 dark:bg-blue-950/20',
    type: 'number' as const,
    min: 0,
    step: 1
  },
  utr: {
    label: 'UTR',
    icon: Clock,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50 dark:bg-purple-950/20',
    type: 'number' as const,
    min: 0,
    max: 1,
    step: 0.01
  },
  salary: {
    label: 'Salary (€)',
    icon: DollarSign,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50 dark:bg-orange-950/20',
    type: 'number' as const,
    min: 0,
    step: 100
  }
};

export const ExpandablePlanningGrid: React.FC<ExpandablePlanningGridProps> = ({
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

  const [roleExpansion, setRoleExpansion] = useState<RoleExpansion>({});
  const [levelExpansion, setLevelExpansion] = useState<LevelExpansion>({});
  const [localChanges, setLocalChanges] = useState<Map<string, CellData>>(new Map());
  const [isDirty, setIsDirty] = useState(false);

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
  const getCellData = useCallback((role: StandardRole, level: StandardLevel | string, month: number): CellData => {
    const key = `${role}-${level}-${month}`;
    const existing = planDataMap.get(key);
    
    if (existing) {
      return existing;
    }
    
    // Return default values based on role type
    const baseData = {
      role,
      level: level as StandardLevel,
      month,
      year,
      recruitment: 0,
      churn: 0,
      salary: 5000
    };

    // Add price/UTR only for billable roles
    if (isBillableRole(role)) {
      return {
        ...baseData,
        price: 100,
        utr: 0.75
      };
    }

    return {
      ...baseData,
      price: 0,
      utr: 0
    };
  }, [planDataMap, year]);

  // Handle cell value change
  const handleCellChange = useCallback((
    role: StandardRole,
    level: StandardLevel | string,
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

  // Toggle role expansion
  const toggleRoleExpansion = useCallback((role: StandardRole) => {
    setRoleExpansion(prev => ({
      ...prev,
      [role]: !prev[role]
    }));
  }, []);

  // Toggle level expansion
  const toggleLevelExpansion = useCallback((role: StandardRole, level: StandardLevel) => {
    const key = `${role}-${level}`;
    setLevelExpansion(prev => ({
      ...prev,
      [key]: !prev[key]
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

  // Calculate monthly summary for a field
  const getMonthlyFieldSummary = useCallback((month: number, field: keyof MonthlyPlanEntry) => {
    let total = 0;
    STANDARD_ROLES.forEach(role => {
      getAvailableLevels(role).forEach(level => {
        const cellData = getCellData(role, level as StandardLevel, month);
        total += cellData[field] as number;
      });
    });
    return total;
  }, [getCellData]);


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
    <div className="expandable-planning-grid space-y-4">
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

      {/* Main Grid */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse table-fixed">
              {/* Header */}
              <thead className="bg-muted/50 sticky top-0 z-10">
                <tr>
                  <th className="text-left p-3 border-r font-medium w-24">Role</th>
                  <th className="text-left p-3 border-r font-medium w-16">Level</th>
                  <th className="text-left p-3 border-r font-medium w-24">Field</th>
                  {MONTHS.map(month => (
                    <th key={month} className="text-center p-2 border-r font-medium w-24 min-w-[100px]">
                      {month}
                    </th>
                  ))}
                  <th className="text-center p-3 font-medium w-20">Total</th>
                </tr>
              </thead>

              {/* Body */}
              <tbody>
                {STANDARD_ROLES.map(role => {
                  const isRoleExpanded = roleExpansion[role];
                  
                  return (
                    <React.Fragment key={role}>
                      {/* Role Header Row */}
                      <tr className="bg-muted/20 border-b-2">
                        <td 
                          className="p-3 border-r font-medium cursor-pointer hover:bg-muted/40"
                          onClick={() => toggleRoleExpansion(role)}
                        >
                          <div className="flex items-center gap-2">
                            {isRoleExpanded ? (
                              <ChevronDown className="h-4 w-4" />
                            ) : (
                              <ChevronRight className="h-4 w-4" />
                            )}
                            <span>{role}</span>
                          </div>
                        </td>
                        <td className="p-3 border-r text-muted-foreground">
                          {getAvailableLevels(role).length} level{getAvailableLevels(role).length > 1 ? 's' : ''}
                        </td>
                        <td className="p-3 border-r text-muted-foreground">
                          {getAvailableFields(role).length} fields
                        </td>
                        {MONTHS.map((month, monthIndex) => (
                          <td key={month} className="p-2 border-r text-center">
                            <div className="text-xs font-medium">
                              {/* Show role summary */}
                              {getAvailableLevels(role).reduce((sum, level) => {
                                const cellData = getCellData(role, level as StandardLevel, monthIndex + 1);
                                return sum + (cellData.recruitment - cellData.churn);
                              }, 0)}
                            </div>
                          </td>
                        ))}
                        <td className="p-3 text-center border-l-2">
                          <div className="text-sm font-medium">
                            {/* Show role total */}
                            {Array.from({ length: 12 }, (_, i) => i + 1).reduce((sum, month) => {
                              return sum + getAvailableLevels(role).reduce((levelSum, level) => {
                                const cellData = getCellData(role, level as StandardLevel, month);
                                return levelSum + (cellData.recruitment - cellData.churn);
                              }, 0);
                            }, 0)}
                          </div>
                        </td>
                      </tr>

                      {/* Level Rows (when role is expanded) */}
                      {isRoleExpanded && getAvailableLevels(role).map(level => {
                        const levelKey = `${role}-${level}`;
                        const isLevelExpanded = levelExpansion[levelKey];
                        
                        return (
                          <React.Fragment key={levelKey}>
                            {/* Level Header Row */}
                            <tr className="bg-muted/10 border-b">
                              <td className="p-2 border-r"></td>
                              <td 
                                className="p-2 border-r cursor-pointer hover:bg-muted/30"
                                onClick={() => toggleLevelExpansion(role, level)}
                              >
                                <div className="flex items-center gap-2">
                                  {isLevelExpanded ? (
                                    <ChevronDown className="h-3 w-3" />
                                  ) : (
                                    <ChevronRight className="h-3 w-3" />
                                  )}
                                  <Badge variant="outline" className="text-xs">
                                    {level}
                                  </Badge>
                                </div>
                              </td>
                              <td className="p-2 border-r text-muted-foreground text-xs">
                                {getAvailableFields(role).length} fields
                              </td>
                              {MONTHS.map((month, monthIndex) => (
                                <td key={month} className="p-1 border-r text-center">
                                  <div className="text-xs">
                                    {/* Show level summary */}
                                    {(() => {
                                      const cellData = getCellData(role, level, monthIndex + 1);
                                      return cellData.recruitment - cellData.churn;
                                    })()}
                                  </div>
                                </td>
                              ))}
                              <td className="p-2 text-center border-l-2">
                                <div className="text-xs">
                                  {/* Show level total */}
                                  {Array.from({ length: 12 }, (_, i) => i + 1).reduce((sum, month) => {
                                    const cellData = getCellData(role, level, month);
                                    return sum + (cellData.recruitment - cellData.churn);
                                  }, 0)}
                                </div>
                              </td>
                            </tr>

                            {/* Field Rows (when level is expanded) */}
                            {isLevelExpanded && getAvailableFields(role).map(field => {
                              const config = FIELD_CONFIG[field as keyof typeof FIELD_CONFIG];
                              if (!config) {
                                console.warn(`Missing field config for: ${field}`);
                                return null;
                              }
                              const Icon = config.icon;
                              
                              return (
                                <tr key={`${levelKey}-${field}`} className="hover:bg-muted/20">
                                  <td className="p-1 border-r"></td>
                                  <td className="p-1 border-r"></td>
                                  <td className="p-2 border-r">
                                    <div className="flex items-center gap-2">
                                      <Icon className={cn("h-3 w-3", config.color)} />
                                      <span className="text-xs font-medium">
                                        {config.label}
                                      </span>
                                    </div>
                                  </td>
                                  {MONTHS.map((month, monthIndex) => (
                                    <td key={`${role}-${level}-${monthIndex + 1}-${field}`} className="p-1 border-r min-w-[100px] hover:bg-muted/20 transition-colors cursor-pointer">
                                      <PlanningFieldInput
                                        value={(getCellData(role, level, monthIndex + 1)[field as keyof MonthlyPlanEntry] as number)}
                                        onChange={(newValue) => handleCellChange(role, level, monthIndex + 1, field as keyof MonthlyPlanEntry, newValue)}
                                        field={field as 'recruitment' | 'churn' | 'price' | 'utr' | 'salary'}
                                        isDirty={getCellData(role, level, monthIndex + 1).isDirty}
                                      />
                                    </td>
                                  ))}
                                  <td className="p-2 text-center border-l-2">
                                    <div className="text-xs font-medium">
                                      {/* Show field total */}
                                      {Array.from({ length: 12 }, (_, i) => i + 1).reduce((sum, month) => {
                                        const cellData = getCellData(role, level, month);
                                        return sum + (cellData[field as keyof MonthlyPlanEntry] as number);
                                      }, 0).toFixed(field === 'utr' ? 2 : 0)}
                                    </div>
                                  </td>
                                </tr>
                              );
                            })}
                          </React.Fragment>
                        );
                      })}
                    </React.Fragment>
                  );
                })}

                {/* Monthly Totals Row */}
                <tr className="bg-muted/30 border-t-2">
                  <td className="p-3 font-medium border-r" colSpan={3}>
                    Monthly Totals (Net Growth)
                  </td>
                  {MONTHS.map((month, monthIndex) => (
                    <td key={month} className="p-2 text-center border-r">
                      <div className="text-sm font-medium">
                        {getMonthlyFieldSummary(monthIndex + 1, 'recruitment') - 
                         getMonthlyFieldSummary(monthIndex + 1, 'churn')}
                      </div>
                    </td>
                  ))}
                  <td className="p-3 text-center border-l-2">
                    <div className="text-sm font-bold">
                      {Array.from({ length: 12 }, (_, i) => i + 1).reduce((sum, month) => {
                        return sum + (getMonthlyFieldSummary(month, 'recruitment') - 
                                     getMonthlyFieldSummary(month, 'churn'));
                      }, 0)}
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};