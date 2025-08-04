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
  Calculator,
  UserPlus,
  UserMinus,
  ArrowUpRight,
  Target,
  Building2
} from 'lucide-react';
import { useBusinessPlanStore } from '../../stores/businessPlanStore';
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
import { PlanningKPICards } from './PlanningKPICards';

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
  totalFte: number;
  fieldType?: 'input' | 'calculated' | 'display' | 'separator'; // Add separator type
  isEditable?: boolean;
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

// Comprehensive business planning field categories with proper office/role-level structure
const FIELD_CATEGORIES = {
  sales_metrics: {
    office_level: ['net_sales', 'ebitda', 'ebitda_margin'],
    role_level: ['price', 'utr', 'hours']
  },
  workforce_planning: {
    office_level: [],
    role_level: ['starters', 'leavers', 'net_headcount_change', 'fte']
  },
  operating_expenses: {
    office_level: [
      // Salary & Compensation Expenses
      'total_salary_expenses',
      // Office & Operational Expenses  
      'office_rent', 'travel', 'external_representation', 'it_related', 
      'education', 'external_services', 'severance', 'depreciation',
      // Total
      'total_operating_expenses'
    ],
    role_level: [
      // Individual salary components per role/level
      'gross_salary', 'social_security', 'pension', 'bonus_provision', 'total_salary_cost'
    ]
  },
  financial_summary: {
    office_level: ['ebit', 'total_revenue', 'total_expenses'],
    role_level: []
  }
}

// Field configuration with calculation types, styling, and hierarchy
const FIELD_CONFIG = {
  // Sales Metrics
  net_sales: {
    label: 'Net Sales',
    icon: DollarSign,
    color: 'text-green-600',
    bgColor: 'bg-green-50 dark:bg-green-950/20',
    type: 'calculated',
    level: 'office', // office-level field
    formula: 'sum of (price × utr × hours × fte) for all roles',
    dependencies: ['price', 'utr']
  },
  ebitda: {
    label: 'EBITDA',
    icon: TrendingUp,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 dark:bg-blue-950/20',
    type: 'calculated',
    level: 'office',
    formula: 'total_revenue - total_expenses',
    dependencies: ['total_revenue', 'total_expenses']
  },
  ebitda_margin: {
    label: 'EBITDA Margin %',
    icon: Target,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50 dark:bg-purple-950/20',
    type: 'calculated',
    level: 'office',
    formula: 'ebitda ÷ net_sales × 100',
    dependencies: ['ebitda', 'net_sales']
  },
  price: {
    label: 'Price (€/h)',
    icon: DollarSign,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 dark:bg-blue-950/20',
    type: 'input',
    level: 'role_level', // role and level specific
    min: 0,
    step: 1,
    applicableRoles: ['Consultant', 'Sales']
  },
  utr: {
    label: 'UTR',
    icon: Clock,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50 dark:bg-purple-950/20',
    type: 'input',
    level: 'role_level',
    min: 0,
    max: 1,
    step: 0.01,
    applicableRoles: ['Consultant', 'Sales']
  },
  
  // Workforce Planning
  starters: {
    label: 'Starters',
    icon: UserPlus,
    color: 'text-green-600',
    bgColor: 'bg-green-50 dark:bg-green-950/20',
    type: 'input',
    level: 'role_level',
    min: 0,
    step: 1,
    applicableRoles: ['Consultant', 'Sales', 'Recruitment', 'Operations']
  },
  leavers: {
    label: 'Leavers',
    icon: UserMinus,
    color: 'text-red-600',
    bgColor: 'bg-red-50 dark:bg-red-950/20',
    type: 'input',
    level: 'role_level',
    min: 0,
    step: 1,
    applicableRoles: ['Consultant', 'Sales', 'Recruitment', 'Operations']
  },
  net_headcount_change: {
    label: 'Net Headcount Change',
    icon: ArrowUpRight,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 dark:bg-blue-950/20',
    type: 'calculated',
    level: 'role_level',
    formula: 'starters - leavers',
    dependencies: ['starters', 'leavers'],
    applicableRoles: ['Consultant', 'Sales', 'Recruitment', 'Operations']
  },
  
  // Compensation & Benefits
  base_salary: {
    label: 'Base Salary (€)',
    icon: DollarSign,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50 dark:bg-orange-950/20',
    type: 'input',
    level: 'role_level',
    min: 0,
    step: 100,
    applicableRoles: ['Consultant', 'Sales', 'Recruitment', 'Operations']
  },
  social_security: {
    label: 'Social Security (25%)',
    icon: Calculator,
    color: 'text-gray-600',
    bgColor: 'bg-gray-50 dark:bg-gray-950/20',
    type: 'calculated',
    level: 'role_level',
    formula: 'base_salary × 0.25',
    dependencies: ['base_salary'],
    applicableRoles: ['Consultant', 'Sales', 'Recruitment', 'Operations']
  },
  pension: {
    label: 'Pension (8%)',
    icon: Calculator,
    color: 'text-gray-600',
    bgColor: 'bg-gray-50 dark:bg-gray-950/20',
    type: 'calculated',
    level: 'role_level',
    formula: 'base_salary × 0.08',
    dependencies: ['base_salary'],
    applicableRoles: ['Consultant', 'Sales', 'Recruitment', 'Operations']
  },
  bonus_provision: {
    label: 'Bonus Provision',
    icon: DollarSign,
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-50 dark:bg-yellow-950/20',
    type: 'input',
    level: 'role_level',
    min: 0,
    step: 100,
    applicableRoles: ['Consultant', 'Sales', 'Recruitment', 'Operations']
  },
  total_salary_cost: {
    label: 'Total Salary Cost',
    icon: Calculator,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50 dark:bg-orange-950/20',
    type: 'calculated',
    level: 'role_level',
    formula: 'base_salary + social_security + pension + bonus_provision',
    dependencies: ['base_salary', 'social_security', 'pension', 'bonus_provision'],
    applicableRoles: ['Consultant', 'Sales', 'Recruitment', 'Operations']
  },
  
  // Operating Expenses (Office-level only)
  office_rent: {
    label: 'Office Rent',
    icon: Building2,
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-50 dark:bg-indigo-950/20',
    type: 'input',
    level: 'office',
    min: 0,
    step: 100
  },
  travel: {
    label: 'Travel',
    icon: Users,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 dark:bg-blue-950/20',
    type: 'input',
    level: 'office',
    min: 0,
    step: 100
  },
  internal_rep: {
    label: 'Internal Representation',
    icon: Users,
    color: 'text-green-600',
    bgColor: 'bg-green-50 dark:bg-green-950/20',
    type: 'input',
    level: 'office',
    min: 0,
    step: 100
  },
  external_rep: {
    label: 'External Representation',
    icon: Users,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50 dark:bg-purple-950/20',
    type: 'input',
    level: 'office',
    min: 0,
    step: 100
  },
  conference_cost: {
    label: 'Conference Cost',
    icon: Users,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50 dark:bg-orange-950/20',
    type: 'input',
    level: 'office',
    min: 0,
    step: 100
  },
  it_services: {
    label: 'IT Services',
    icon: Users,
    color: 'text-gray-600',
    bgColor: 'bg-gray-50 dark:bg-gray-950/20',
    type: 'input',
    level: 'office',
    min: 0,
    step: 100
  },
  education: {
    label: 'Education',
    icon: Users,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 dark:bg-blue-950/20',
    type: 'input',
    level: 'office',
    min: 0,
    step: 100
  },
  external_services: {
    label: 'External Services',
    icon: Users,
    color: 'text-red-600',
    bgColor: 'bg-red-50 dark:bg-red-950/20',
    type: 'input',
    level: 'office',
    min: 0,
    step: 100
  },
  severance: {
    label: 'Severance',
    icon: Users,
    color: 'text-red-600',
    bgColor: 'bg-red-50 dark:bg-red-950/20',
    type: 'input',
    level: 'office',
    min: 0,
    step: 100
  },
  
  // Financial Summary (Office-level calculations)
  total_revenue: {
    label: 'Total Revenue',
    icon: DollarSign,
    color: 'text-green-600',
    bgColor: 'bg-green-50 dark:bg-green-950/20',
    type: 'calculated',
    level: 'office',
    formula: 'sum of all net_sales',
    dependencies: ['net_sales']
  },
  total_people_costs: {
    label: 'Total People Costs',
    icon: Users,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50 dark:bg-orange-950/20',
    type: 'calculated',
    level: 'office',
    formula: 'sum of all total_salary_cost',
    dependencies: ['total_salary_cost']
  },
  total_operating_costs: {
    label: 'Total Operating Costs',
    icon: Building2,
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-50 dark:bg-indigo-950/20',
    type: 'calculated',
    level: 'office',
    formula: 'total_operating_expenses',
    dependencies: ['total_operating_expenses']
  },
  total_expenses: {
    label: 'Total Expenses',
    icon: Calculator,
    color: 'text-red-600',
    bgColor: 'bg-red-50 dark:bg-red-950/20',
    type: 'calculated',
    level: 'office',
    formula: 'total_people_costs + total_operating_costs',
    dependencies: ['total_people_costs', 'total_operating_costs']
  },
  final_ebitda: {
    label: 'EBITDA',
    icon: TrendingUp,
    color: 'text-green-600',
    bgColor: 'bg-green-50 dark:bg-green-950/20',
    type: 'calculated',
    level: 'office',
    formula: 'total_revenue - total_expenses',
    dependencies: ['total_revenue', 'total_expenses']
  },
  revenue_per_fte: {
    label: 'Revenue per FTE',
    icon: Target,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 dark:bg-blue-950/20',
    type: 'calculated',
    level: 'office',
    formula: 'total_revenue ÷ total_fte',
    dependencies: ['total_revenue']
  },
  cost_per_fte: {
    label: 'Cost per FTE',
    icon: Target,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50 dark:bg-purple-950/20',
    type: 'calculated',
    level: 'office',
    formula: 'total_expenses ÷ total_fte',
    dependencies: ['total_expenses']
  },
  
  // Missing fields for role/level
  hours: {
    label: 'Monthly Hours',
    icon: Clock,
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-50 dark:bg-indigo-950/20',
    type: 'input',
    level: 'role_level',
    min: 0,
    max: 200,
    step: 1,
    applicableRoles: ['Consultant', 'Sales', 'Recruitment', 'Operations']
  },
  fte: {
    label: 'FTE Count',
    icon: Users,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 dark:bg-blue-950/20',
    type: 'input',
    level: 'role_level',
    min: 0,
    step: 1,
    applicableRoles: ['Consultant', 'Sales', 'Recruitment', 'Operations']
  },
  
  // Missing office-level expense totals
  total_salary_expenses: {
    label: 'Total Salary Expenses',
    icon: Calculator,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50 dark:bg-orange-950/20',
    type: 'calculated',
    level: 'office',
    formula: 'sum of (total_salary_cost × fte) for all roles/levels',
    dependencies: ['total_salary_cost', 'fte']
  },
  total_operating_expenses: {
    label: 'Total Operating Expenses',
    icon: Calculator,
    color: 'text-red-600',
    bgColor: 'bg-red-50 dark:bg-red-950/20',
    type: 'calculated',
    level: 'office',
    formula: 'office_rent + travel + external_representation + it_related + education + external_services + severance + depreciation + total_salary_expenses',
    dependencies: ['office_rent', 'travel', 'external_representation', 'it_related', 'education', 'external_services', 'severance', 'depreciation', 'total_salary_expenses']
  }
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




  // Mock FTE data - in real implementation, get from office data
  const mockFteByRoleLevel: Record<string, Record<string, number>> = useMemo(() => ({
    'Consultant': { 'A': 15, 'B': 25, 'C': 12 },
    'Sales': { 'A': 8, 'B': 12, 'C': 6 },
    'Recruitment': { 'General': 5 },
    'Operations': { 'General': 8 }
  }), []);

  // Mock calculated data for now - in real implementation, calculate from business plan data
  const calculatedData = useMemo(() => {
    return {
      revenue: { total: 2500000 },
      grossProfit: { total: 1800000 },
      netProfit: { total: 300000 }
    };
  }, [office, localChangesKey]);

  // Prepare data for DataTableMinimal with comprehensive business planning structure
  const tableData: PlanningTableRow[] = useMemo(() => {
    const rows: PlanningTableRow[] = [];
    
    // Category name mapping for display
    const categoryDisplayNames = {
      sales_metrics: 'Sales Metrics',
      workforce_planning: 'Workforce Planning', 
      compensation: 'Compensation & Benefits',
      operating_expenses: 'Operating Expenses',
      financial_summary: 'Financial Summary'
    };
    
    // Create hierarchical structure: Category Header -> Field -> Role/Level (where applicable)
    Object.entries(FIELD_CATEGORIES).forEach(([categoryName, categoryStructure], categoryIndex) => {
      // Add section separator before each category (except the first one)
      if (categoryIndex > 0) {
        const separatorRow: PlanningTableRow = {
          id: `separator-${categoryName}`,
          field: '',
          role: 'SECTION_SEPARATOR',
          level: 'SEPARATOR',
          displayName: '',
          totalFte: 0,
          fieldType: 'separator',
          isEditable: false,
          jan: 0, feb: 0, mar: 0, apr: 0, may: 0, jun: 0,
          jul: 0, aug: 0, sep: 0, oct: 0, nov: 0, dec: 0, total: 0
        };
        rows.push(separatorRow);
      }
      
      // Add category header row
      const categoryHeaderRow: PlanningTableRow = {
        id: `category-${categoryName}`,
        field: categoryDisplayNames[categoryName as keyof typeof categoryDisplayNames] || categoryName,
        role: 'CATEGORY_HEADER',
        level: 'HEADER',
        displayName: categoryDisplayNames[categoryName as keyof typeof categoryDisplayNames] || categoryName,
        totalFte: 0,
        fieldType: 'display',
        isEditable: false,
        jan: 0, feb: 0, mar: 0, apr: 0, may: 0, jun: 0,
        jul: 0, aug: 0, sep: 0, oct: 0, nov: 0, dec: 0, total: 0
      };
      rows.push(categoryHeaderRow);
      
      // Add office-level fields first
      categoryStructure.office_level.forEach(fieldName => {
        const fieldConfig = FIELD_CONFIG[fieldName as keyof typeof FIELD_CONFIG];
        if (!fieldConfig) return;
        
        // Check if field is office-level or role/level specific
        if (fieldConfig.level === 'office') {
          // Office-level field (no role/level breakdown)
          const aggregatedData = {
            jan: 0, feb: 0, mar: 0, apr: 0, may: 0, jun: 0,
            jul: 0, aug: 0, sep: 0, oct: 0, nov: 0, dec: 0, total: 0
          };
          
          // Use calculated data from calculation engine
          const calculatedFieldData = calculatedData.officeLevel[fieldName];
          if (calculatedFieldData) {
            aggregatedData.jan = calculatedFieldData.jan;
            aggregatedData.feb = calculatedFieldData.feb;
            aggregatedData.mar = calculatedFieldData.mar;
            aggregatedData.apr = calculatedFieldData.apr;
            aggregatedData.may = calculatedFieldData.may;
            aggregatedData.jun = calculatedFieldData.jun;
            aggregatedData.jul = calculatedFieldData.jul;
            aggregatedData.aug = calculatedFieldData.aug;
            aggregatedData.sep = calculatedFieldData.sep;
            aggregatedData.oct = calculatedFieldData.oct;
            aggregatedData.nov = calculatedFieldData.nov;
            aggregatedData.dec = calculatedFieldData.dec;
            aggregatedData.total = calculatedFieldData.total;
          }
          
          // For office-level fields, just create one summary row
          const row: PlanningTableRow = {
            id: `${categoryName}-${fieldName}-office`,
            field: fieldConfig.label,
            role: 'OFFICE_LEVEL',
            level: 'Total',
            displayName: fieldConfig.label,
            totalFte: 0, // Office-level fields don't have specific FTE
            fieldType: fieldConfig.type,
            isEditable: fieldConfig.type === 'input',
            ...aggregatedData
          };
          rows.push(row);
        }
      });
      
      // Add role/level fields with proper hierarchy
      categoryStructure.role_level.forEach(fieldName => {
        const fieldConfig = FIELD_CONFIG[fieldName as keyof typeof FIELD_CONFIG];
        if (!fieldConfig) return;
        
        if (fieldConfig.level === 'role_level' && fieldConfig.applicableRoles) {
          // Role/level specific fields
          fieldConfig.applicableRoles.forEach(role => {
            const levels = getAvailableLevels(role as StandardRole);
            levels.forEach(level => {
              try {
                const aggregatedData = {
                  jan: 0, feb: 0, mar: 0, apr: 0, may: 0, jun: 0,
                  jul: 0, aug: 0, sep: 0, oct: 0, nov: 0, dec: 0, total: 0
                };
                
                const totalFte = mockFteByRoleLevel[role]?.[level] || 0;
                
                // For input fields, get data from planDataMap
                if (fieldConfig.type === 'input') {
                  for (let month = 1; month <= 12; month++) {
                    const key = `${role}-${level}-${month}`;
                    const existing = planDataMap.get(key);
                    
                    // Get cell data with defaults
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
                    
                    // Map field names to MonthlyPlanEntry fields
                    let value = 0;
                    switch (fieldName) {
                      case 'starters':
                        value = cellData.recruitment || 0;
                        break;
                      case 'leavers':
                        value = cellData.churn || 0;
                        break;
                      case 'base_salary':
                        value = cellData.salary || 0;
                        break;
                      case 'price':
                        value = cellData.price || 0;
                        break;
                      case 'utr':
                        value = cellData.utr || 0;
                        break;
                      default:
                        value = 0;
                    }
                    
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
                // For calculated fields, implement calculation logic here
                else if (fieldConfig.type === 'calculated') {
                  // Implement specific calculations based on field
                  // For now, just set to 0 - will be calculated in real implementation
                }
                
                const row: PlanningTableRow = {
                  id: `${categoryName}-${fieldName}-${role}-${level}`,
                  field: fieldConfig.label,
                  role,
                  level,
                  displayName: `${role} ${level}`,
                  totalFte,
                  ...aggregatedData
                };
                rows.push(row);
              } catch (error) {
                console.error('Error creating row for:', categoryName, fieldName, role, level, error);
              }
            });
          });
        }
      });
    });
    
    return rows;
  }, [planDataMap, year, mockFteByRoleLevel, calculatedData]);

  // Helper function to create month cell styling
  const createMonthCell = () => ({ row, getValue }: any) => {
    const value = getValue() as number;
    const fieldType = row.original.fieldType;
    const role = row.original.role;
    
    // Category headers have empty cells
    if (role === 'CATEGORY_HEADER') {
      return (
        <div className="px-2 py-1 text-center bg-slate-100 dark:bg-slate-800">
          <span className="text-slate-400">—</span>
        </div>
      );
    }
    
    return (
      <div className={cn(
        'px-2 py-1 rounded text-center',
        fieldType === 'input' && 'bg-blue-50 dark:bg-blue-950/10 border border-blue-200 dark:border-blue-800',
        fieldType === 'calculated' && 'bg-green-50 dark:bg-green-950/10 border border-green-200 dark:border-green-800 italic',
        fieldType === 'display' && 'bg-gray-50 dark:bg-gray-950/10'
      )}>
        {value > 0 ? value.toLocaleString() : '—'}
      </div>
    );
  };

  // Define columns for DataTableMinimal with hierarchical grouping
  const columns: MinimalColumnDef<PlanningTableRow>[] = useMemo(() => [
    {
      accessorKey: 'field',
      header: 'Category/Role/Level',
      size: 200,
      enableGrouping: true,
      cell: ({ row, getValue }) => {
        const value = getValue() as string;
        const fieldType = row.original.fieldType;
        const isEditable = row.original.isEditable;
        const role = row.original.role;
        
        // Special styling for section separators
        if (role === 'SECTION_SEPARATOR') {
          return (
            <div className="w-full h-4 flex items-center">
              <div className="w-full h-px bg-gradient-to-r from-transparent via-slate-300 dark:via-slate-600 to-transparent"></div>
            </div>
          );
        }
        
        // Special styling for category headers
        if (role === 'CATEGORY_HEADER') {
          return (
            <div className="flex items-center gap-2 px-3 py-2 bg-slate-100 dark:bg-slate-800 rounded-lg border-l-4 border-slate-600">
              <span className="font-bold text-slate-700 dark:text-slate-200 text-sm uppercase tracking-wide">
                {value}
              </span>
            </div>
          );
        }
        
        // Special styling for office-level fields
        if (role === 'OFFICE_LEVEL') {
          return (
            <div className={cn(
              'flex items-center gap-2 px-3 py-1 rounded ml-4',
              fieldType === 'input' && 'border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-950/20',
              fieldType === 'calculated' && 'border-l-4 border-green-500 bg-green-50 dark:bg-green-950/20',
              fieldType === 'display' && 'border-l-4 border-gray-500 bg-gray-50 dark:bg-gray-950/20'
            )}>
              <span className={cn(
                'font-medium',
                fieldType === 'input' && 'text-blue-700 dark:text-blue-300',
                fieldType === 'calculated' && 'text-green-700 dark:text-green-300',
                fieldType === 'display' && 'text-gray-700 dark:text-gray-300'
              )}>
                {value}
              </span>
              {isEditable && (
                <span className="text-xs text-blue-500 font-medium">✏️</span>
              )}
              {fieldType === 'calculated' && (
                <span className="text-xs text-green-500 font-medium">🔢</span>
              )}
            </div>
          );
        }
        
        // Regular role/level fields
        return (
          <div className={cn(
            'flex items-center gap-2 px-2 py-1 rounded ml-8',
            fieldType === 'input' && 'border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-950/20',
            fieldType === 'calculated' && 'border-l-4 border-green-500 bg-green-50 dark:bg-green-950/20',
            fieldType === 'display' && 'border-l-4 border-gray-500 bg-gray-50 dark:bg-gray-950/20'
          )}>
            <span className={cn(
              'font-medium text-sm',
              fieldType === 'input' && 'text-blue-700 dark:text-blue-300',
              fieldType === 'calculated' && 'text-green-700 dark:text-green-300',
              fieldType === 'display' && 'text-gray-700 dark:text-gray-300'
            )}>
              {value}
            </span>
            {isEditable && (
              <span className="text-xs text-blue-500 font-medium">✏️</span>
            )}
            {fieldType === 'calculated' && (
              <span className="text-xs text-green-500 font-medium">🔢</span>
            )}
          </div>
        );
      }
    },
    {
      accessorKey: 'totalFte',
      header: 'Existing FTE',
      size: 100,
      cell: ({ getValue }) => {
        const value = getValue() as number;
        return Math.round(value).toString();
      }
    },
    {
      accessorKey: 'jan',
      header: 'Jan',
      editable: {
        type: 'number',
        min: 0,
        step: 1,
        onEdit: (rowId, value) => {
          const parts = rowId.split('-');
          if (parts.length >= 4) {
            // Format: categoryName-fieldName-role-level
            const [categoryName, fieldName, role, level] = parts;
            
            // Map field names to MonthlyPlanEntry fields
            let planField: keyof MonthlyPlanEntry;
            switch (fieldName) {
              case 'starters':
                planField = 'recruitment';
                break;
              case 'leavers':
                planField = 'churn';
                break;
              case 'base_salary':
                planField = 'salary';
                break;
              case 'price':
                planField = 'price';
                break;
              case 'utr':
                planField = 'utr';
                break;
              default:
                return; // Skip unsupported fields
            }
            
            handleCellChange(role as StandardRole, level as StandardLevel, 1, planField, value);
          }
        }
      },
      size: 80,
      cell: ({ row, getValue }) => {
        const value = getValue() as number;
        const fieldType = row.original.fieldType;
        const role = row.original.role;
        
        // Special handling for section separators
        if (role === 'SECTION_SEPARATOR') {
          return (
            <div className="w-full h-4 flex items-center">
              <div className="w-full h-px bg-gradient-to-r from-transparent via-slate-300 dark:via-slate-600 to-transparent"></div>
            </div>
          );
        }
        
        return (
          <div className={cn(
            'px-2 py-1 rounded text-center',
            fieldType === 'input' && 'bg-blue-50 dark:bg-blue-950/10 border border-blue-200 dark:border-blue-800',
            fieldType === 'calculated' && 'bg-green-50 dark:bg-green-950/10 border border-green-200 dark:border-green-800 italic',
            fieldType === 'display' && 'bg-gray-50 dark:bg-gray-950/10'
          )}>
            {value.toLocaleString()}
          </div>
        );
      }
    },
    {
      accessorKey: 'feb',
      header: 'Feb',
      editable: {
        type: 'number',
        min: 0,
        step: 1,
        condition: (row) => row.original.isEditable,
        onEdit: (rowId, value) => {
          const parts = rowId.split('-');
          if (parts.length >= 4) {
            const [categoryName, fieldName, role, level] = parts;
            let planField: keyof MonthlyPlanEntry;
            switch (fieldName) {
              case 'starters': planField = 'recruitment'; break;
              case 'leavers': planField = 'churn'; break;
              case 'base_salary': planField = 'salary'; break;
              case 'price': planField = 'price'; break;
              case 'utr': planField = 'utr'; break;
              default: return;
            }
            handleCellChange(role as StandardRole, level as StandardLevel, 2, planField, value);
          }
        }
      },
      size: 80,
      cell: createMonthCell()
    },
    {
      accessorKey: 'mar',
      header: 'Mar',
      editable: {
        type: 'number',
        min: 0,
        step: 1,
        condition: (row) => row.original.isEditable,
        onEdit: (rowId, value) => {
          const parts = rowId.split('-');
          if (parts.length >= 4) {
            const [categoryName, fieldName, role, level] = parts;
            let planField: keyof MonthlyPlanEntry;
            switch (fieldName) {
              case 'starters': planField = 'recruitment'; break;
              case 'leavers': planField = 'churn'; break;
              case 'base_salary': planField = 'salary'; break;
              case 'price': planField = 'price'; break;
              case 'utr': planField = 'utr'; break;
              default: return;
            }
            handleCellChange(role as StandardRole, level as StandardLevel, 3, planField, value);
          }
        }
      },
      size: 80,
      cell: createMonthCell()
    },
    {
      accessorKey: 'apr',
      header: 'Apr',
      editable: {
        type: 'number',
        min: 0,
        step: 1,
        condition: (row) => row.original.isEditable,
        onEdit: (rowId, value) => {
          const parts = rowId.split('-');
          if (parts.length >= 4) {
            const [categoryName, fieldName, role, level] = parts;
            let planField: keyof MonthlyPlanEntry;
            switch (fieldName) {
              case 'starters': planField = 'recruitment'; break;
              case 'leavers': planField = 'churn'; break;
              case 'base_salary': planField = 'salary'; break;
              case 'price': planField = 'price'; break;
              case 'utr': planField = 'utr'; break;
              default: return;
            }
            handleCellChange(role as StandardRole, level as StandardLevel, 4, planField, value);
          }
        }
      },
      size: 80,
      cell: createMonthCell()
    },
    {
      accessorKey: 'may',
      header: 'May',
      editable: {
        type: 'number',
        min: 0,
        step: 1,
        condition: (row) => row.original.isEditable,
        onEdit: (rowId, value) => {
          const parts = rowId.split('-');
          if (parts.length >= 4) {
            const [categoryName, fieldName, role, level] = parts;
            let planField: keyof MonthlyPlanEntry;
            switch (fieldName) {
              case 'starters': planField = 'recruitment'; break;
              case 'leavers': planField = 'churn'; break;
              case 'base_salary': planField = 'salary'; break;
              case 'price': planField = 'price'; break;
              case 'utr': planField = 'utr'; break;
              default: return;
            }
            handleCellChange(role as StandardRole, level as StandardLevel, 5, planField, value);
          }
        }
      },
      size: 80,
      cell: createMonthCell()
    },
    {
      accessorKey: 'jun',
      header: 'Jun',
      editable: {
        type: 'number',
        min: 0,
        step: 1,
        condition: (row) => row.original.isEditable,
        onEdit: (rowId, value) => {
          const parts = rowId.split('-');
          if (parts.length >= 4) {
            const [categoryName, fieldName, role, level] = parts;
            let planField: keyof MonthlyPlanEntry;
            switch (fieldName) {
              case 'starters': planField = 'recruitment'; break;
              case 'leavers': planField = 'churn'; break;
              case 'base_salary': planField = 'salary'; break;
              case 'price': planField = 'price'; break;
              case 'utr': planField = 'utr'; break;
              default: return;
            }
            handleCellChange(role as StandardRole, level as StandardLevel, 6, planField, value);
          }
        }
      },
      size: 80,
      cell: createMonthCell()
    },
    {
      accessorKey: 'jul',
      header: 'Jul',
      editable: {
        type: 'number',
        min: 0,
        step: 1,
        condition: (row) => row.original.isEditable,
        onEdit: (rowId, value) => {
          const parts = rowId.split('-');
          if (parts.length >= 4) {
            const [categoryName, fieldName, role, level] = parts;
            let planField: keyof MonthlyPlanEntry;
            switch (fieldName) {
              case 'starters': planField = 'recruitment'; break;
              case 'leavers': planField = 'churn'; break;
              case 'base_salary': planField = 'salary'; break;
              case 'price': planField = 'price'; break;
              case 'utr': planField = 'utr'; break;
              default: return;
            }
            handleCellChange(role as StandardRole, level as StandardLevel, 7, planField, value);
          }
        }
      },
      size: 80,
      cell: createMonthCell()
    },
    {
      accessorKey: 'aug',
      header: 'Aug',
      editable: {
        type: 'number',
        min: 0,
        step: 1,
        condition: (row) => row.original.isEditable,
        onEdit: (rowId, value) => {
          const parts = rowId.split('-');
          if (parts.length >= 4) {
            const [categoryName, fieldName, role, level] = parts;
            let planField: keyof MonthlyPlanEntry;
            switch (fieldName) {
              case 'starters': planField = 'recruitment'; break;
              case 'leavers': planField = 'churn'; break;
              case 'base_salary': planField = 'salary'; break;
              case 'price': planField = 'price'; break;
              case 'utr': planField = 'utr'; break;
              default: return;
            }
            handleCellChange(role as StandardRole, level as StandardLevel, 8, planField, value);
          }
        }
      },
      size: 80,
      cell: createMonthCell()
    },
    {
      accessorKey: 'sep',
      header: 'Sep',
      editable: {
        type: 'number',
        min: 0,
        step: 1,
        condition: (row) => row.original.isEditable,
        onEdit: (rowId, value) => {
          const parts = rowId.split('-');
          if (parts.length >= 4) {
            const [categoryName, fieldName, role, level] = parts;
            let planField: keyof MonthlyPlanEntry;
            switch (fieldName) {
              case 'starters': planField = 'recruitment'; break;
              case 'leavers': planField = 'churn'; break;
              case 'base_salary': planField = 'salary'; break;
              case 'price': planField = 'price'; break;
              case 'utr': planField = 'utr'; break;
              default: return;
            }
            handleCellChange(role as StandardRole, level as StandardLevel, 9, planField, value);
          }
        }
      },
      size: 80,
      cell: createMonthCell()
    },
    {
      accessorKey: 'oct',
      header: 'Oct',
      editable: {
        type: 'number',
        min: 0,
        step: 1,
        condition: (row) => row.original.isEditable,
        onEdit: (rowId, value) => {
          const parts = rowId.split('-');
          if (parts.length >= 4) {
            const [categoryName, fieldName, role, level] = parts;
            let planField: keyof MonthlyPlanEntry;
            switch (fieldName) {
              case 'starters': planField = 'recruitment'; break;
              case 'leavers': planField = 'churn'; break;
              case 'base_salary': planField = 'salary'; break;
              case 'price': planField = 'price'; break;
              case 'utr': planField = 'utr'; break;
              default: return;
            }
            handleCellChange(role as StandardRole, level as StandardLevel, 10, planField, value);
          }
        }
      },
      size: 80,
      cell: createMonthCell()
    },
    {
      accessorKey: 'nov',
      header: 'Nov',
      editable: {
        type: 'number',
        min: 0,
        step: 1,
        condition: (row) => row.original.isEditable,
        onEdit: (rowId, value) => {
          const parts = rowId.split('-');
          if (parts.length >= 4) {
            const [categoryName, fieldName, role, level] = parts;
            let planField: keyof MonthlyPlanEntry;
            switch (fieldName) {
              case 'starters': planField = 'recruitment'; break;
              case 'leavers': planField = 'churn'; break;
              case 'base_salary': planField = 'salary'; break;
              case 'price': planField = 'price'; break;
              case 'utr': planField = 'utr'; break;
              default: return;
            }
            handleCellChange(role as StandardRole, level as StandardLevel, 11, planField, value);
          }
        }
      },
      size: 80,
      cell: createMonthCell()
    },
    {
      accessorKey: 'dec',
      header: 'Dec',
      editable: {
        type: 'number',
        min: 0,
        step: 1,
        condition: (row) => row.original.isEditable,
        onEdit: (rowId, value) => {
          const parts = rowId.split('-');
          if (parts.length >= 4) {
            const [categoryName, fieldName, role, level] = parts;
            let planField: keyof MonthlyPlanEntry;
            switch (fieldName) {
              case 'starters': planField = 'recruitment'; break;
              case 'leavers': planField = 'churn'; break;
              case 'base_salary': planField = 'salary'; break;
              case 'price': planField = 'price'; break;
              case 'utr': planField = 'utr'; break;
              default: return;
            }
            handleCellChange(role as StandardRole, level as StandardLevel, 12, planField, value);
          }
        }
      },
      size: 80,
      cell: createMonthCell()
    },
    {
      accessorKey: 'total',
      header: 'Total',
      size: 100,
      cell: ({ row, getValue }) => {
        const value = getValue() as number;
        const fieldType = row.original.fieldType;
        const role = row.original.role;
        
        // Category headers have empty total cells
        if (role === 'CATEGORY_HEADER') {
          return (
            <div className="px-2 py-1 text-center bg-slate-100 dark:bg-slate-800">
              <span className="text-slate-400 font-semibold">—</span>
            </div>
          );
        }
        
        return (
          <div className={cn(
            'px-2 py-1 rounded text-center font-semibold',
            fieldType === 'input' && 'bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300',
            fieldType === 'calculated' && 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300',
            fieldType === 'display' && 'bg-gray-100 dark:bg-gray-900/20 text-gray-700 dark:text-gray-300'
          )}>
            {value > 0 ? value.toLocaleString() : '—'}
          </div>
        );
      }
    }
  ], [handleCellChange]);

  // Calculate yearly KPIs from office business plan data
  const kpis = useMemo(() => {
    let yearlyRecruitment = 0;
    let yearlyChurn = 0;
    let yearlyRevenue = 0;
    let priceSum = 0;
    let utrSum = 0;
    let entryCount = 0;
    let baselineRecruitment = 0;

    // Sum data across all months for this office
    for (let month = 1; month <= 12; month++) {
      STANDARD_ROLES.forEach(role => {
        getAvailableLevels(role).forEach(level => {
          const key = `${role}-${level}-${month}`;
          const existing = planDataMap.get(key);
          
          // Get cell data with defaults
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
          
          // Sum values for KPIs
          yearlyRecruitment += cellData.recruitment || 0;
          yearlyChurn += cellData.churn || 0;
          
          if (cellData.price && cellData.utr) {
            // Monthly revenue calculation
            yearlyRevenue += (cellData.price * cellData.utr * 8 * 21); // 8 hours/day, 21 days/month
            priceSum += cellData.price;
            utrSum += cellData.utr;
            entryCount++;
          }
          
          // Use first month's recruitment as baseline for percentage calculation
          if (month === 1) {
            baselineRecruitment += cellData.recruitment || 0;
          }
        });
      });
    }

    const netRecruitment = yearlyRecruitment - yearlyChurn;
    const netRecruitmentPercent = baselineRecruitment > 0 ? (netRecruitment / baselineRecruitment) * 100 : 0;
    const avgPrice = entryCount > 0 ? priceSum / entryCount : 0;
    const avgUTR = entryCount > 0 ? utrSum / entryCount : 0;

    return {
      totalRecruitment: yearlyRecruitment,
      totalChurn: yearlyChurn,
      netRecruitment,
      netRecruitmentPercent,
      netRevenue: yearlyRevenue,
      avgPriceIncrease: avgPrice > 0 ? ((avgPrice - 100) / 100) * 100 : 0, // Assuming 100 as baseline
      avgTargetUTR: avgUTR * 100 // Convert to percentage
    };
  }, [planDataMap, year]);

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

      {/* KPI Cards Row */}
      <PlanningKPICards 
        kpis={{
          totalRecruitment: Math.round(kpis.totalRecruitment),
          totalChurn: Math.round(kpis.totalChurn),
          netRecruitment: Math.round(kpis.netRecruitment),
          netRecruitmentPercent: kpis.netRecruitmentPercent,
          netRevenue: Math.round(kpis.netRevenue),
          avgPriceIncrease: kpis.avgPriceIncrease,
          avgTargetUTR: kpis.avgTargetUTR
        }}
        className="mb-4"
      />

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