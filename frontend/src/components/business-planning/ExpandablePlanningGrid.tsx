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
import { DataTableMinimal, MinimalColumnDef } from '../ui/data-table-minimal';
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



// Data structure for DataTableMinimal with hierarchical grouping
interface PlanningTableRow {
  id: string;
  field: string;
  role: string;
  level: string;
  displayName?: string; // For individual rows to show level name
  jan: number;
  feb: number;
  mar: number;
  apr: number;
  may: number;
  jun: number;
  jul: number;
  aug: number;
  sep: number;
  oct: number;
  nov: number;
  dec: number;
  total: number;
}

// Field categories for top-level grouping
const FIELD_CATEGORIES = {
  starters: ['recruitment'],
  leavers: ['churn'],
  economic: ['salary', 'price', 'utr']
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
  if (role === 'Operations') {
    return ['General']; // Operations is a flat role with no levels
  }
  // Show all levels (A, AC, AM, P) for other roles
  return STANDARD_LEVELS;
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


  const [localChanges, setLocalChanges] = useState<Map<string, CellData>>(new Map());
  const [isDirty, setIsDirty] = useState(false);
  
  // Group expansion state for hierarchical grouping
  const [groupExpanded, setGroupExpanded] = useState<Record<string, boolean>>({});

  const handleGroupToggle = useCallback((groupId: string, expanded: boolean) => {
    setGroupExpanded(prev => ({
      ...prev,
      [groupId]: expanded
    }));
  }, []);

  // Load data when office or year changes
  useEffect(() => {
    if (office?.id) {
      // Check if this is a new business plan creation
      const newPlanData = localStorage.getItem('new-business-plan');
      if (newPlanData) {
        const planData = JSON.parse(newPlanData);
        // If this matches the current office and year, start with empty table
        if (planData.officeId === office.id && planData.year === year && planData.workflow === 'manual') {
          // Clear the stored data and start fresh
          localStorage.removeItem('new-business-plan');
          return; // Don't load existing data, start with empty table
        }
      }
      
      loadBusinessPlans(office.id, year);
    }
  }, [office?.id, year, loadBusinessPlans]);

  // Create stable key for localChanges to avoid unnecessary re-renders
  const localChangesKey = useMemo(() => {
    return Array.from(localChanges.keys()).sort().join('|');
  }, [localChanges]);

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


  // Handle cell value change
  const handleCellChange = useCallback((
    role: StandardRole,
    level: StandardLevel | string,
    month: number,
    field: keyof MonthlyPlanEntry,
    value: number
  ) => {
    const key = `${role}-${level}-${month}`;
    const existing = planDataMap.get(key);
    
    // Get current data with defaults (inline version to avoid getCellData dependency)
    const currentData = existing || {
      role,
      level: level as StandardLevel,
      month,
      year,
      recruitment: 0,
      churn: 0,
      salary: 5000,
      price: isBillableRole(role) ? 100 : 0,
      utr: isBillableRole(role) ? 0.75 : 0
    };
    
    const updatedData: CellData = {
      ...currentData,
      [field]: value
    };
    
    setLocalChanges(prev => new Map(prev).set(key, updatedData));
    setIsDirty(true);
  }, [planDataMap, year]);



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
        const key = `${role}-${level}-${month}`;
        const existing = planDataMap.get(key);
        
        // Get cell data with defaults (inline version to avoid getCellData dependency)
        const cellData = existing || {
          role,
          level: level as StandardLevel,
          month,
          year,
          recruitment: 0,
          churn: 0,
          salary: 5000,
          price: isBillableRole(role) ? 100 : 0,
          utr: isBillableRole(role) ? 0.75 : 0
        };
        
        total += cellData[field] as number;
      });
    });
    return total;
  }, [planDataMap, year]);




  // Prepare data for DataTableMinimal with hierarchical grouping structure
  const tableData: PlanningTableRow[] = useMemo(() => {
    const rows: PlanningTableRow[] = [];
    
    // Create hierarchical structure matching Excel: Category -> Role/Field -> Level
    Object.entries(FIELD_CATEGORIES).forEach(([categoryName, categoryFields]) => {
      if (categoryName === 'starters' || categoryName === 'leavers') {
        // For starters and leavers: Category -> Role -> Level
        ['Consultant', 'Sales', 'Recruitment', 'Operations'].forEach(role => {
          // Get appropriate levels for each role
          const levels = getAvailableLevels(role as StandardRole);
          levels.forEach(level => {
            try {
              const aggregatedData = {
                jan: 0, feb: 0, mar: 0, apr: 0, may: 0, jun: 0,
                jul: 0, aug: 0, sep: 0, oct: 0, nov: 0, dec: 0, total: 0
              };
              
              categoryFields.forEach(field => {
                if (getAvailableFields(role).includes(field)) {
                  for (let month = 1; month <= 12; month++) {
                    const key = `${role}-${level}-${month}`;
                    const existing = planDataMap.get(key);
                    
                    // Get cell data with defaults (inline version of getCellData)
                    const cellData = existing || {
                      role,
                      level: level as StandardLevel,
                      month,
                      year,
                      recruitment: 0,
                      churn: 0,
                      salary: 5000,
                      price: isBillableRole(role) ? 100 : 0,
                      utr: isBillableRole(role) ? 0.75 : 0
                    };
                    
                    const value = (cellData[field as keyof MonthlyPlanEntry] as number) || 0;
                    
                    switch (month) {
                      case 1: aggregatedData.jan += value; break;
                      case 2: aggregatedData.feb += value; break;
                      case 3: aggregatedData.mar += value; break;
                      case 4: aggregatedData.apr += value; break;
                      case 5: aggregatedData.may += value; break;
                      case 6: aggregatedData.jun += value; break;
                      case 7: aggregatedData.jul += value; break;
                      case 8: aggregatedData.aug += value; break;
                      case 9: aggregatedData.sep += value; break;
                      case 10: aggregatedData.oct += value; break;
                      case 11: aggregatedData.nov += value; break;
                      case 12: aggregatedData.dec += value; break;
                    }
                    aggregatedData.total += value;
                  }
                }
              });
              
              const row: PlanningTableRow = {
                id: `${categoryName}-${role}-${level}`,
                field: categoryName,
                role,
                level,
                displayName: level, // Use this for display in individual rows
                ...aggregatedData
              };
              rows.push(row);
            } catch (error) {
              console.error('Error creating row for:', categoryName, role, level, error);
            }
          });
        });
      } else if (categoryName === 'economic') {
        // For economic: Category -> Field -> Level
        categoryFields.forEach(field => {
          // Get all unique levels from all roles
          const allLevels = [...new Set(['Consultant', 'Sales', 'Recruitment', 'Operations']
            .flatMap(role => getAvailableLevels(role as StandardRole)))];
          allLevels.forEach(level => {
            try {
              const aggregatedData = {
                jan: 0, feb: 0, mar: 0, apr: 0, may: 0, jun: 0,
                jul: 0, aug: 0, sep: 0, oct: 0, nov: 0, dec: 0, total: 0
              };
              
              // For economic fields, we need to aggregate across all roles that have this field
              ['Consultant', 'Sales', 'Recruitment', 'Operations'].forEach(role => {
                if (getAvailableFields(role).includes(field)) {
                  for (let month = 1; month <= 12; month++) {
                    const key = `${role}-${level}-${month}`;
                    const existing = planDataMap.get(key);
                    
                    // Get cell data with defaults (inline version of getCellData)
                    const cellData = existing || {
                      role,
                      level: level as StandardLevel,
                      month,
                      year,
                      recruitment: 0,
                      churn: 0,
                      salary: 5000,
                      price: isBillableRole(role) ? 100 : 0,
                      utr: isBillableRole(role) ? 0.75 : 0
                    };
                    
                    const value = (cellData[field as keyof MonthlyPlanEntry] as number) || 0;
                    
                    switch (month) {
                      case 1: aggregatedData.jan += value; break;
                      case 2: aggregatedData.feb += value; break;
                      case 3: aggregatedData.mar += value; break;
                      case 4: aggregatedData.apr += value; break;
                      case 5: aggregatedData.may += value; break;
                      case 6: aggregatedData.jun += value; break;
                      case 7: aggregatedData.jul += value; break;
                      case 8: aggregatedData.aug += value; break;
                      case 9: aggregatedData.sep += value; break;
                      case 10: aggregatedData.oct += value; break;
                      case 11: aggregatedData.nov += value; break;
                      case 12: aggregatedData.dec += value; break;
                    }
                    aggregatedData.total += value;
                  }
                }
              });
              
              const row: PlanningTableRow = {
                id: `${categoryName}-${field}-${level}`,
                field: categoryName,
                role: field, // Use field name as role for economic
                level,
                displayName: level, // Use this for display in individual rows
                ...aggregatedData
              };
              rows.push(row);
            } catch (error) {
              console.error('Error creating row for:', categoryName, field, level, error);
            }
          });
        });
      }
    });
    
    return rows;
  }, [planDataMap, year]);

  // Define columns for DataTableMinimal with hierarchical grouping
  const columns: MinimalColumnDef<PlanningTableRow>[] = useMemo(() => [
    {
      accessorKey: 'field',
      header: 'Category/Role/Level',
      size: 200,
      enableGrouping: true
    },
    {
      accessorKey: 'jan',
      header: 'Jan',
      editable: {
        type: 'number',
        min: 0,
        step: 1,
        onEdit: (rowId, value) => {
          const [categoryName, roleOrField, level] = rowId.split('-');
          let role: string, field: string;
          
          if (categoryName === 'economic') {
            // For economic: categoryName-field-level
            field = roleOrField;
            role = 'Consultant'; // Use a default role for economic fields
          } else {
            // For starters/leavers: categoryName-role-level
            role = roleOrField;
            field = FIELD_CATEGORIES[categoryName as keyof typeof FIELD_CATEGORIES][0];
          }
          
          handleCellChange(role as StandardRole, level as StandardLevel, 1, field as keyof MonthlyPlanEntry, value);
        }
      },
      size: 80
    },
    {
      accessorKey: 'feb',
      header: 'Feb',
      editable: {
        type: 'number',
        min: 0,
        step: 1,
        onEdit: (rowId, value) => {
          const [categoryName, role, level] = rowId.split('-');
          const field = FIELD_CATEGORIES[categoryName as keyof typeof FIELD_CATEGORIES][0];
          handleCellChange(role as StandardRole, level as StandardLevel, 2, field as keyof MonthlyPlanEntry, value);
        }
      },
      size: 80
    },
    {
      accessorKey: 'mar',
      header: 'Mar',
      editable: {
        type: 'number',
        min: 0,
        step: 1,
        onEdit: (rowId, value) => {
          const [categoryName, role, level] = rowId.split('-');
          const field = FIELD_CATEGORIES[categoryName as keyof typeof FIELD_CATEGORIES][0];
          handleCellChange(role as StandardRole, level as StandardLevel, 3, field as keyof MonthlyPlanEntry, value);
        }
      },
      size: 80
    },
    {
      accessorKey: 'apr',
      header: 'Apr',
      editable: {
        type: 'number',
        min: 0,
        step: 1,
        onEdit: (rowId, value) => {
          const [categoryName, role, level] = rowId.split('-');
          const field = FIELD_CATEGORIES[categoryName as keyof typeof FIELD_CATEGORIES][0];
          handleCellChange(role as StandardRole, level as StandardLevel, 4, field as keyof MonthlyPlanEntry, value);
        }
      },
      size: 80
    },
    {
      accessorKey: 'may',
      header: 'May',
      editable: {
        type: 'number',
        min: 0,
        step: 1,
        onEdit: (rowId, value) => {
          const [categoryName, role, level] = rowId.split('-');
          const field = FIELD_CATEGORIES[categoryName as keyof typeof FIELD_CATEGORIES][0];
          handleCellChange(role as StandardRole, level as StandardLevel, 5, field as keyof MonthlyPlanEntry, value);
        }
      },
      size: 80
    },
    {
      accessorKey: 'jun',
      header: 'Jun',
      editable: {
        type: 'number',
        min: 0,
        step: 1,
        onEdit: (rowId, value) => {
          const [categoryName, role, level] = rowId.split('-');
          const field = FIELD_CATEGORIES[categoryName as keyof typeof FIELD_CATEGORIES][0];
          handleCellChange(role as StandardRole, level as StandardLevel, 6, field as keyof MonthlyPlanEntry, value);
        }
      },
      size: 80
    },
    {
      accessorKey: 'jul',
      header: 'Jul',
      editable: {
        type: 'number',
        min: 0,
        step: 1,
        onEdit: (rowId, value) => {
          const [categoryName, role, level] = rowId.split('-');
          const field = FIELD_CATEGORIES[categoryName as keyof typeof FIELD_CATEGORIES][0];
          handleCellChange(role as StandardRole, level as StandardLevel, 7, field as keyof MonthlyPlanEntry, value);
        }
      },
      size: 80
    },
    {
      accessorKey: 'aug',
      header: 'Aug',
      editable: {
        type: 'number',
        min: 0,
        step: 1,
        onEdit: (rowId, value) => {
          const [categoryName, role, level] = rowId.split('-');
          const field = FIELD_CATEGORIES[categoryName as keyof typeof FIELD_CATEGORIES][0];
          handleCellChange(role as StandardRole, level as StandardLevel, 8, field as keyof MonthlyPlanEntry, value);
        }
      },
      size: 80
    },
    {
      accessorKey: 'sep',
      header: 'Sep',
      editable: {
        type: 'number',
        min: 0,
        step: 1,
        onEdit: (rowId, value) => {
          const [categoryName, role, level] = rowId.split('-');
          const field = FIELD_CATEGORIES[categoryName as keyof typeof FIELD_CATEGORIES][0];
          handleCellChange(role as StandardRole, level as StandardLevel, 9, field as keyof MonthlyPlanEntry, value);
        }
      },
      size: 80
    },
    {
      accessorKey: 'oct',
      header: 'Oct',
      editable: {
        type: 'number',
        min: 0,
        step: 1,
        onEdit: (rowId, value) => {
          const [categoryName, role, level] = rowId.split('-');
          const field = FIELD_CATEGORIES[categoryName as keyof typeof FIELD_CATEGORIES][0];
          handleCellChange(role as StandardRole, level as StandardLevel, 10, field as keyof MonthlyPlanEntry, value);
        }
      },
      size: 80
    },
    {
      accessorKey: 'nov',
      header: 'Nov',
      editable: {
        type: 'number',
        min: 0,
        step: 1,
        onEdit: (rowId, value) => {
          const [categoryName, role, level] = rowId.split('-');
          const field = FIELD_CATEGORIES[categoryName as keyof typeof FIELD_CATEGORIES][0];
          handleCellChange(role as StandardRole, level as StandardLevel, 11, field as keyof MonthlyPlanEntry, value);
        }
      },
      size: 80
    },
    {
      accessorKey: 'dec',
      header: 'Dec',
      editable: {
        type: 'number',
        min: 0,
        step: 1,
        onEdit: (rowId, value) => {
          const [categoryName, role, level] = rowId.split('-');
          const field = FIELD_CATEGORIES[categoryName as keyof typeof FIELD_CATEGORIES][0];
          handleCellChange(role as StandardRole, level as StandardLevel, 12, field as keyof MonthlyPlanEntry, value);
        }
      },
      size: 80
    },
    {
      accessorKey: 'total',
      header: 'Total',
      size: 100
    }
  ], [handleCellChange]);

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
          <DataTableMinimal
            columns={columns}
            data={tableData}
            enableEditing={true}
            enablePagination={false}
            enableGrouping={true}
            groupBy={['field', 'role']}
            groupExpanded={groupExpanded}
            onGroupToggle={handleGroupToggle}
            className="business-planning-table"
          />
        </CardContent>
      </Card>
    </div>
  );
};