/**
 * Clean Business Plan Table
 * 
 * A simplified hierarchical table for business planning with:
 * - Category → Field → Role → Level structure (4 levels)
 * - Office-level fields (no role/level breakdown)
 * - Calculated fields (read-only)
 * - Expandable/collapsible groups
 */
import React, { useState, useMemo, useCallback, useEffect } from 'react';
import { ChevronRight, ChevronDown } from 'lucide-react';
import { cn } from '../../lib/utils';
import { useBusinessPlanStore } from '../../stores/businessPlanStore';
import { PlanningKPICards } from './PlanningKPICards';
import type { OfficeConfig, MonthlyPlanEntry, StandardRole, StandardLevel } from '../../types/office';

// ============================================================================
// TYPES
// ============================================================================

type RowType = 'category' | 'field' | 'role' | 'level' | 'office-field';

interface TableRow {
  id: string;
  type: RowType;
  name: string;
  depth: number;
  isEditable: boolean;
  isCalculated: boolean;
  isSubtotal?: boolean;
  
  // Data for leaf nodes
  fieldKey?: string;
  role?: StandardRole;
  level?: StandardLevel;
  
  // Monthly values (only for data rows)
  jan?: number;
  feb?: number;
  mar?: number;
  apr?: number;
  may?: number;
  jun?: number;
  jul?: number;
  aug?: number;
  sep?: number;
  oct?: number;
  nov?: number;
  dec?: number;
  total?: number;
  
  // Hierarchy
  parentId?: string;
  children?: string[];
}

interface CleanBusinessPlanTableProps {
  office: OfficeConfig;
  year: number;
  // Optional props for aggregated view
  isAggregated?: boolean;
  selectedOffices?: string[];
  aggregatedData?: Map<string, number>;
}

// ============================================================================
// CONSTANTS
// ============================================================================

const MONTHS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'] as const;
const MONTH_LABELS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

// Table structure configuration
const TABLE_STRUCTURE = [
  {
    id: 'workforce',
    name: '📊 WORKFORCE',
    type: 'category' as RowType,
    fields: [
      {
        id: 'starting_fte',
        name: 'Starting FTE (Population)',
        fieldKey: 'starting_fte',
        hasRoles: true,
        roles: ['Consultant', 'Sales', 'Recruitment', 'Operations']
      },
      {
        id: 'recruitment',
        name: 'Recruitment (+)',
        fieldKey: 'recruitment',
        hasRoles: true,
        roles: ['Consultant', 'Sales', 'Recruitment', 'Operations']
      },
      {
        id: 'churn',
        name: 'Churn (-)',
        fieldKey: 'churn',
        hasRoles: true,
        roles: ['Consultant', 'Sales', 'Recruitment', 'Operations']
      },
      {
        id: 'ending_fte',
        name: 'Ending FTE',
        fieldKey: 'ending_fte',
        hasRoles: true,
        roles: ['Consultant', 'Sales', 'Recruitment', 'Operations'],
        isCalculated: true
      },
      // Category subtotals
      {
        id: 'total_workforce',
        name: '🔢 Total Workforce',
        fieldKey: 'total_workforce',
        hasRoles: false,
        isCalculated: true,
        isSubtotal: true
      }
    ]
  },
  {
    id: 'net_sales',
    name: '⏱️ NET SALES',
    type: 'category' as RowType,
    fields: [
      {
        id: 'consultant_time',
        name: 'Consultant Time',
        fieldKey: 'consultant_time',
        hasRoles: false,
        defaultValue: 160
      },
      {
        id: 'planned_absence',
        name: 'Planned Absence',
        fieldKey: 'planned_absence',
        hasRoles: false,
        defaultValue: 20
      },
      {
        id: 'unplanned_absence',
        name: 'Unplanned Absence',
        fieldKey: 'unplanned_absence',
        hasRoles: false,
        defaultValue: 10
      },
      {
        id: 'vacation_withdrawal',
        name: 'Vacation Withdrawal',
        fieldKey: 'vacation_withdrawal',
        hasRoles: false,
        defaultValue: 0
      },
      {
        id: 'vacation',
        name: 'Vacation',
        fieldKey: 'vacation',
        hasRoles: false,
        defaultValue: 16
      },
      {
        id: 'available_consultant_time',
        name: 'Available Consultant Time',
        fieldKey: 'available_consultant_time',
        hasRoles: false,
        isCalculated: true
      },
      {
        id: 'invoiced_time',
        name: 'Invoiced Time',
        fieldKey: 'invoiced_time',
        hasRoles: false,
        defaultValue: 110
      },
      {
        id: 'utilization_rate',
        name: 'Utilization Rate (%)',
        fieldKey: 'utilization_rate',
        hasRoles: false,
        defaultValue: 0.85
      },
      {
        id: 'average_price',
        name: 'Average Price (hour)',
        fieldKey: 'average_price',
        hasRoles: false,
        defaultValue: 1200
      },
      // Category subtotal
      {
        id: 'total_net_sales',
        name: '💰 Total Net Sales',
        fieldKey: 'total_net_sales',
        hasRoles: false,
        isCalculated: true,
        isSubtotal: true
      }
    ]
  },
  {
    id: 'salary',
    name: '💰 SALARY',
    type: 'category' as RowType,
    fields: [
      {
        id: 'salary',
        name: 'Base Salary',
        fieldKey: 'salary',
        hasRoles: true,
        roles: ['Consultant', 'Sales', 'Recruitment', 'Operations']
      },
      {
        id: 'variable_salary',
        name: 'Variable Salary',
        fieldKey: 'variable_salary',
        hasRoles: true,
        roles: ['Consultant', 'Sales', 'Recruitment', 'Operations']
      },
      {
        id: 'social_security',
        name: 'Social Security',
        fieldKey: 'social_security',
        hasRoles: true,
        roles: ['Consultant', 'Sales', 'Recruitment', 'Operations']
      },
      {
        id: 'pension',
        name: 'Pension',
        fieldKey: 'pension',
        hasRoles: true,
        roles: ['Consultant', 'Sales', 'Recruitment', 'Operations']
      },
      // Category subtotal
      {
        id: 'total_salary_costs',
        name: '👥 Total Salary Costs',
        fieldKey: 'total_salary_costs',
        hasRoles: false,
        isCalculated: true,
        isSubtotal: true
      }
    ]
  },
  {
    id: 'costs',
    name: '💸 OPERATING COSTS',
    type: 'category' as RowType,
    fields: [
      // Expenses Category
      {
        id: 'client_loss',
        name: 'Client Loss',
        fieldKey: 'client_loss',
        hasRoles: false,
        defaultValue: 0
      },
      {
        id: 'education',
        name: 'Education',
        fieldKey: 'education',
        hasRoles: false,
        defaultValue: 10000
      },
      {
        id: 'external_representation',
        name: 'External Representation',
        fieldKey: 'external_representation',
        hasRoles: false,
        defaultValue: 5000
      },
      {
        id: 'external_services',
        name: 'External Services',
        fieldKey: 'external_services',
        hasRoles: false,
        defaultValue: 15000
      },
      {
        id: 'internal_representation',
        name: 'Internal Representation',
        fieldKey: 'internal_representation',
        hasRoles: false,
        defaultValue: 3000
      },
      {
        id: 'it_related_staff',
        name: 'IT Related (Staff)',
        fieldKey: 'it_related_staff',
        hasRoles: false,
        defaultValue: 20000
      },
      {
        id: 'office_related',
        name: 'Office Related',
        fieldKey: 'office_related',
        hasRoles: false,
        defaultValue: 5000
      },
      {
        id: 'office_rent',
        name: 'Office Rent',
        fieldKey: 'office_rent',
        hasRoles: false,
        defaultValue: 50000
      },
      {
        id: 'other_expenses',
        name: 'Other',
        fieldKey: 'other_expenses',
        hasRoles: false,
        defaultValue: 5000
      },
      // Category subtotal
      {
        id: 'total_expenses',
        name: '💸 Total Expenses',
        fieldKey: 'total_expenses',
        hasRoles: false,
        isCalculated: true,
        isSubtotal: true
      },
      {
        id: 'total_operating_costs',
        name: '💰 Total Operating Costs',
        fieldKey: 'total_operating_costs',
        hasRoles: false,
        isCalculated: true,
        isSubtotal: true
      }
    ]
  },
  {
    id: 'summary',
    name: '📈 SUMMARY',
    type: 'category' as RowType,
    fields: [
      {
        id: 'total_revenue',
        name: 'Total Revenue',
        fieldKey: 'total_revenue',
        hasRoles: false,
        isCalculated: true
      },
      {
        id: 'total_salary_cost',
        name: 'Total Salary Cost',
        fieldKey: 'total_salary_cost',
        hasRoles: false,
        isCalculated: true
      },
      {
        id: 'total_costs',
        name: 'Total Costs',
        fieldKey: 'total_costs',
        hasRoles: false,
        isCalculated: true
      },
      {
        id: 'ebitda',
        name: 'EBITDA',
        fieldKey: 'ebitda',
        hasRoles: false,
        isCalculated: true
      },
      {
        id: 'ebitda_margin',
        name: 'EBITDA Margin %',
        fieldKey: 'ebitda_margin',
        hasRoles: false,
        isCalculated: true
      }
    ]
  }
];

// Role levels configuration
const ROLE_LEVELS: Record<string, string[]> = {
  Consultant: ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P'],
  Sales: ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P'],
  Recruitment: ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P'],
  Operations: ['General'] // Flat role
};

// ============================================================================
// COMPONENT
// ============================================================================

export const CleanBusinessPlanTable: React.FC<CleanBusinessPlanTableProps> = ({
  office,
  year,
  isAggregated = false,
  selectedOffices = [],
  aggregatedData
}) => {
  const {
    monthlyPlans,
    loading,
    loadBusinessPlans,
    createMonthlyPlan,
    updateMonthlyPlan
  } = useBusinessPlanStore();

  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set(['workforce', 'net_sales', 'salary', 'costs', 'summary']));
  const [editingCell, setEditingCell] = useState<string | null>(null);
  const [localChanges, setLocalChanges] = useState<Map<string, number>>(new Map());

  // Load data on mount (skip for aggregated view)
  useEffect(() => {
    if (office?.id && !isAggregated) {
      loadBusinessPlans(office.id, year);
    }
  }, [office?.id, year, loadBusinessPlans, isAggregated]);

  // Build plan data map for quick lookup
  const planDataMap = useMemo(() => {
    const map = new Map<string, MonthlyPlanEntry>();
    
    monthlyPlans.forEach(plan => {
      plan.entries.forEach(entry => {
        const key = `${entry.role}-${entry.level}-${plan.month}`;
        map.set(key, entry);
      });
    });
    
    return map;
  }, [monthlyPlans]);

  // Get value from plan data or local changes
  const getValue = useCallback((role: string, level: string, month: number, field: string): number => {
    // For aggregated view, use provided aggregated data
    if (isAggregated && aggregatedData) {
      const aggregatedKey = `${role}-${level}-${month}-${field}`;
      const aggregatedValue = aggregatedData.get(aggregatedKey);
      if (aggregatedValue !== undefined) {
        return aggregatedValue;
      }
      
      // Generate sample data for aggregated view if not provided
      const seed = role.length + level.length + month + field.length;
      const random = (seed * 9301 + 49297) % 233280;
      const normalized = random / 233280;
      const officeMultiplier = Math.min(selectedOffices.length, 5);
      
      switch (field) {
        case 'recruitment':
          return Math.floor(normalized * 4 + 1) * officeMultiplier;
        case 'churn':
          return Math.floor(normalized * 2) * officeMultiplier;
        case 'price':
          return role === 'Consultant' ? Math.floor(1200 + normalized * 300) : 0;
        case 'utr':
          return role === 'Consultant' ? Math.round((0.7 + normalized * 0.2) * 100) / 100 : 0;
        case 'salary':
          return Math.floor(50000 + normalized * 40000);
        default:
          return 0;
      }
    }

    // For single office view, use existing logic
    const changeKey = `${role}-${level}-${month}-${field}`;
    if (localChanges.has(changeKey)) {
      return localChanges.get(changeKey)!;
    }

    const planKey = `${role}-${level}-${month}`;
    const planEntry = planDataMap.get(planKey);
    
    if (planEntry) {
      // Check for exact field match first
      if (field in planEntry && (planEntry as any)[field] !== undefined) {
        const value = (planEntry as any)[field];
        // For salary-related fields, only return non-zero values (0 means "use default")
        if (['salary', 'variable_salary', 'social_security', 'pension'].includes(field) && value === 0) {
          // Fall through to default values
        } else {
          return value;
        }
      }
      
      // Check for legacy field mappings for backward compatibility
      if (field === 'utilization_rate' && 'utr' in planEntry && (planEntry as any).utr !== undefined) {
        return (planEntry as any).utr;
      }
      if (field === 'average_price' && 'price' in planEntry && (planEntry as any).price !== undefined) {
        return (planEntry as any).price;
      }
    }
    
    // Default values for starting FTE based on Oslo office data
    if (field === 'starting_fte') {
      // Get starting FTE from office configuration for Oslo
      // Total: 85 consultants (not 96 - that was total with other roles)
      if (role === 'Consultant') {
        const osloConsultantFTE: Record<string, number> = {
          'A': 5,
          'AC': 10,
          'C': 20,
          'SrC': 18,
          'AM': 18,
          'M': 9,
          'SrM': 4,
          'Pi': 1,
          'P': 0
        };
        return osloConsultantFTE[level] || 0;
      }
      if (role === 'Sales') {
        // Estimated based on typical distribution
        const salesFTE: Record<string, number> = {
          'A': 2,
          'AC': 2,
          'C': 2,
          'SrC': 1,
          'AM': 1,
          'M': 1,
          'SrM': 0,
          'Pi': 0,
          'P': 0
        };
        return salesFTE[level] || 0;
      }
      if (role === 'Recruitment') {
        const recruitmentFTE: Record<string, number> = {
          'A': 1,
          'AC': 1,
          'C': 1,
          'SrC': 1,
          'AM': 0,
          'M': 0,
          'SrM': 0,
          'Pi': 0,
          'P': 0
        };
        return recruitmentFTE[level] || 0;
      }
      if (role === 'Operations') {
        return 1; // Operations General
      }
      return 0;
    }
    
    // Calculate ending FTE
    if (field === 'ending_fte') {
      const starting = getValue(role, level, month, 'starting_fte');
      const recruitment = getValue(role, level, month, 'recruitment');
      const churn = getValue(role, level, month, 'churn');
      return Math.max(0, starting + recruitment - churn);
    }
    
    // Other default values
    if (field === 'price') return 1200;
    if (field === 'utr') return 0.75;
    if (field === 'salary') {
      // Use 2025 Oslo BASE salary ladder as default values - same for Consultant, Sales, and Recruitment
      const oslo2025BaseSalaries: Record<string, Record<string, number>> = {
        'Consultant': {
          'A': 640000 / 12,      // 53,333/month base
          'AC': 670000 / 12,     // 55,833/month base
          'C': 750000 / 12,      // 62,500/month base
          'SrC': 800000 / 12,    // 66,667/month base
          'AM': 860000 / 12,     // 71,667/month base
          'M': 920000 / 12,      // 76,667/month base
          'SrM': 1050000 / 12,   // 87,500/month base
          'Pi': 1240000 / 12,    // 103,333/month base
          'P': 1548000 / 12      // 129,000/month base
        },
        'Sales': {
          // Same base salary structure as Consultant
          'A': 640000 / 12,      
          'AC': 670000 / 12,     
          'C': 750000 / 12,      
          'SrC': 800000 / 12,    
          'AM': 860000 / 12,     
          'M': 920000 / 12,     
          'SrM': 1050000 / 12,
          'Pi': 1240000 / 12,
          'P': 1548000 / 12
        },
        'Recruitment': {
          // Same base salary structure as Consultant
          'A': 640000 / 12,      
          'AC': 670000 / 12,     
          'C': 750000 / 12,      
          'SrC': 800000 / 12,    
          'AM': 860000 / 12,     
          'M': 920000 / 12,     
          'SrM': 1050000 / 12,
          'Pi': 1240000 / 12,
          'P': 1548000 / 12
        },
        'Operations': { 'General': 640000 / 12 }
      };
      return oslo2025BaseSalaries[role]?.[level] || (640000 / 12);
    }
    if (field === 'variable_salary') {
      // Use 2025 Oslo VARIABLE salary ladder as default values - same for Consultant, Sales, and Recruitment
      const oslo2025VariableSalaries: Record<string, Record<string, number>> = {
        'Consultant': {
          'A': 0 / 12,           // 0/month variable
          'AC': 20000 / 12,      // 1,667/month variable
          'C': 50000 / 12,       // 4,167/month variable
          'SrC': 80000 / 12,     // 6,667/month variable
          'AM': 120000 / 12,     // 10,000/month variable
          'M': 170000 / 12,      // 14,167/month variable
          'SrM': 250000 / 12,    // 20,833/month variable
          'Pi': 330000 / 12,     // 27,500/month variable
          'P': 408000 / 12       // 34,000/month variable
        },
        'Sales': {
          // Same variable salary structure as Consultant
          'A': 0 / 12,
          'AC': 20000 / 12,
          'C': 50000 / 12,
          'SrC': 80000 / 12,
          'AM': 120000 / 12,
          'M': 170000 / 12,
          'SrM': 250000 / 12,
          'Pi': 330000 / 12,
          'P': 408000 / 12
        },
        'Recruitment': {
          // Same variable salary structure as Consultant
          'A': 0 / 12,
          'AC': 20000 / 12,
          'C': 50000 / 12,
          'SrC': 80000 / 12,
          'AM': 120000 / 12,
          'M': 170000 / 12,
          'SrM': 250000 / 12,
          'Pi': 330000 / 12,
          'P': 408000 / 12
        },
        'Operations': { 'General': 0 / 12 } // No variable for operations
      };
      return oslo2025VariableSalaries[role]?.[level] || 0;
    }
    if (field === 'social_security') {
      // Norwegian employer social security contributions (NAV) - typically 14.1% of gross salary
      // Calculate based on base + variable salary for the role/level
      const baseSalary = getValue(role, level, month, 'salary') || 
        getValue(role, level, month, 'salary'); // Get base salary
      const variableSalary = getValue(role, level, month, 'variable_salary') || 0;
      
      // If we have salary data, calculate 14.1% of gross
      if (baseSalary && baseSalary > 0) {
        const totalGross = baseSalary + variableSalary;
        return totalGross * 0.141; // 14.1% social security rate
      }
      
      // Fallback: use default based on 2025 salary ladder
      const defaultBaseSalaries: Record<string, Record<string, number>> = {
        'Consultant': { 'A': 640000/12, 'AC': 670000/12, 'C': 750000/12, 'SrC': 800000/12, 'AM': 860000/12, 'M': 920000/12, 'SrM': 1050000/12, 'Pi': 1240000/12, 'P': 1548000/12 },
        'Sales': { 'A': 640000/12, 'AC': 670000/12, 'C': 750000/12, 'SrC': 800000/12, 'AM': 860000/12, 'M': 920000/12, 'SrM': 1050000/12, 'Pi': 1240000/12, 'P': 1548000/12 },
        'Recruitment': { 'A': 640000/12, 'AC': 670000/12, 'C': 750000/12, 'SrC': 800000/12, 'AM': 860000/12, 'M': 920000/12, 'SrM': 1050000/12, 'Pi': 1240000/12, 'P': 1548000/12 },
        'Operations': { 'General': 640000/12 }
      };
      const defaultVariableSalaries: Record<string, Record<string, number>> = {
        'Consultant': { 'A': 0, 'AC': 20000/12, 'C': 50000/12, 'SrC': 80000/12, 'AM': 120000/12, 'M': 170000/12, 'SrM': 250000/12, 'Pi': 330000/12, 'P': 408000/12 },
        'Sales': { 'A': 0, 'AC': 20000/12, 'C': 50000/12, 'SrC': 80000/12, 'AM': 120000/12, 'M': 170000/12, 'SrM': 250000/12, 'Pi': 330000/12, 'P': 408000/12 },
        'Recruitment': { 'A': 0, 'AC': 20000/12, 'C': 50000/12, 'SrC': 80000/12, 'AM': 120000/12, 'M': 170000/12, 'SrM': 250000/12, 'Pi': 330000/12, 'P': 408000/12 },
        'Operations': { 'General': 0 }
      };
      
      const defaultBase = defaultBaseSalaries[role]?.[level] || (640000/12);
      const defaultVariable = defaultVariableSalaries[role]?.[level] || 0;
      const defaultGross = defaultBase + defaultVariable;
      return defaultGross * 0.141; // 14.1% social security rate
    }
    if (field === 'pension') {
      // Norwegian pension contributions from salary ladder: 0G-7.1G = 4.5%, 7.1G-12G = 8.5%
      // Calculate based on base + variable salary for the role/level
      const baseSalary = getValue(role, level, month, 'salary') || 0;
      const variableSalary = getValue(role, level, month, 'variable_salary') || 0;
      
      if (baseSalary > 0) {
        const totalGross = baseSalary + variableSalary;
        const annualGross = totalGross * 12;
        
        // Norwegian G-value for 2025 is approximately 124,028 NOK
        const gValue = 124028;
        const threshold1 = 7.1 * gValue; // ~880,599 NOK
        
        if (annualGross <= threshold1) {
          return (totalGross * 0.045); // 4.5% for lower bracket
        } else {
          // 4.5% on first 7.1G, 8.5% on amount above
          const lowerAmount = threshold1 / 12; // Monthly threshold
          const lowerPension = lowerAmount * 0.045;
          const upperAmount = totalGross - lowerAmount;
          const upperPension = upperAmount * 0.085;
          return lowerPension + upperPension;
        }
      }
      
      // Fallback: use default based on 2025 salary ladder
      const defaultBaseSalaries: Record<string, Record<string, number>> = {
        'Consultant': { 'A': 640000/12, 'AC': 670000/12, 'C': 750000/12, 'SrC': 800000/12, 'AM': 860000/12, 'M': 920000/12, 'SrM': 1050000/12, 'Pi': 1240000/12, 'P': 1548000/12 },
        'Sales': { 'A': 640000/12, 'AC': 670000/12, 'C': 750000/12, 'SrC': 800000/12, 'AM': 860000/12, 'M': 920000/12, 'SrM': 1050000/12, 'Pi': 1240000/12, 'P': 1548000/12 },
        'Recruitment': { 'A': 640000/12, 'AC': 670000/12, 'C': 750000/12, 'SrC': 800000/12, 'AM': 860000/12, 'M': 920000/12, 'SrM': 1050000/12, 'Pi': 1240000/12, 'P': 1548000/12 },
        'Operations': { 'General': 640000/12 }
      };
      const defaultVariableSalaries: Record<string, Record<string, number>> = {
        'Consultant': { 'A': 0, 'AC': 20000/12, 'C': 50000/12, 'SrC': 80000/12, 'AM': 120000/12, 'M': 170000/12, 'SrM': 250000/12, 'Pi': 330000/12, 'P': 408000/12 },
        'Sales': { 'A': 0, 'AC': 20000/12, 'C': 50000/12, 'SrC': 80000/12, 'AM': 120000/12, 'M': 170000/12, 'SrM': 250000/12, 'Pi': 330000/12, 'P': 408000/12 },
        'Recruitment': { 'A': 0, 'AC': 20000/12, 'C': 50000/12, 'SrC': 80000/12, 'AM': 120000/12, 'M': 170000/12, 'SrM': 250000/12, 'Pi': 330000/12, 'P': 408000/12 },
        'Operations': { 'General': 0 }
      };
      
      const defaultBase = defaultBaseSalaries[role]?.[level] || (640000/12);
      const defaultVariable = defaultVariableSalaries[role]?.[level] || 0;
      const defaultGross = defaultBase + defaultVariable;
      const defaultAnnualGross = defaultGross * 12;
      
      const gValue = 124028;
      const threshold1 = 7.1 * gValue;
      
      if (defaultAnnualGross <= threshold1) {
        return defaultGross * 0.045; // 4.5%
      } else {
        const lowerAmount = threshold1 / 12;
        const lowerPension = lowerAmount * 0.045;
        const upperAmount = defaultGross - lowerAmount;
        const upperPension = upperAmount * 0.085;
        return lowerPension + upperPension;
      }
    }
    if (field === 'utilization_rate') return 0.85;
    if (field === 'consultant_time') return 160;
    if (field === 'planned_absence') return 20;
    if (field === 'unplanned_absence') return 10;
    if (field === 'vacation') return 16;
    if (field === 'invoiced_time') return 110;
    if (field === 'average_price') return 1200;
    return 0;
  }, [planDataMap, localChanges, isAggregated, aggregatedData, selectedOffices]);

  // Calculate summary fields
  const calculateSummaryFields = useCallback((month: number) => {
    let totalRevenue = 0;
    let totalSalaryCost = 0;
    let totalCosts = 0;

    const officeMultiplier = isAggregated ? Math.min(selectedOffices.length, 5) : 1;

    // Calculate revenue from consultants using ending FTE (total workforce) 
    const consultantLevels = ROLE_LEVELS.Consultant || ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P'];
    consultantLevels.forEach(level => {
      // Get the ending FTE (total workforce for this level)
      const endingFTE = getValue('Consultant', level, month, 'ending_fte');
      
      if (endingFTE > 0) {
        // Get utilization rate and pricing
        const utilizationRate = getValue('Consultant', level, month, 'utilization_rate') || getValue('Consultant', level, month, 'utr') || 0.85;
        const monthlyHours = 160; // Standard working hours per month
        const invoicedTime = monthlyHours * utilizationRate; // Actual billable hours
        
        // Get average price - check both field names
        let averagePrice = getValue('Consultant', level, month, 'average_price') || getValue('Consultant', level, month, 'price');
        
        // If no price found or too low, use defaults based on level
        // Target: 12-15M revenue with 96 consultants at 85% utilization
        // Average needed: ~1,300-1,600 NOK/hour
        if (!averagePrice || averagePrice < 500) {
          const defaultPrices: Record<string, number> = {
            'A': 1200,    // Junior
            'AC': 1300,   // Associate Consultant
            'C': 1400,    // Consultant  
            'SrC': 1500,  // Senior Consultant
            'AM': 1600,   // Associate Manager
            'M': 1750,    // Manager
            'SrM': 1900,  // Senior Manager
            'Pi': 2100,   // Principal
            'P': 2400     // Partner
          };
          averagePrice = defaultPrices[level] || 1400;
        }
        
        // Calculate revenue: FTE count × billable hours × hourly rate
        const levelRevenue = endingFTE * invoicedTime * averagePrice;
        totalRevenue += levelRevenue;
      }
    });

    // Calculate salary costs using ending FTE for all roles
    Object.entries(ROLE_LEVELS).forEach(([role, levels]) => {
      levels.forEach(level => {
        // Get the ending FTE (total workforce for this role/level)
        const endingFTE = getValue(role, level, month, 'ending_fte');
        
        if (endingFTE > 0) {
          // Get salary - prioritize saved business plan data, fallback to 2025 Oslo salary ladder defaults
          let monthlySalary = getValue(role, level, month, 'salary');
          
          // If no saved business plan data, use 2025 Oslo salary ladder as defaults
          if (!monthlySalary || monthlySalary === 0) {
            // 2025 Oslo BASE salary ladder (excluding variable) - same for Consultant, Sales, and Recruitment
            const oslo2025BaseSalaries: Record<string, Record<string, number>> = {
              'Consultant': {
                'A': 640000 / 12,      // 640,000 NOK/year base = 53,333/month
                'AC': 670000 / 12,     // 670,000 NOK/year base = 55,833/month  
                'C': 750000 / 12,      // 750,000 NOK/year base = 62,500/month
                'SrC': 800000 / 12,    // 800,000 NOK/year base = 66,667/month
                'AM': 860000 / 12,     // 860,000 NOK/year base = 71,667/month
                'M': 920000 / 12,      // 920,000 NOK/year base = 76,667/month
                'SrM': 1050000 / 12,   // 1,050,000 NOK/year base = 87,500/month
                'Pi': 1240000 / 12,    // 1,240,000 NOK/year base = 103,333/month (Principal)
                'P': 1548000 / 12      // 1,548,000 NOK/year base = 129,000/month (Partner)
              },
              'Sales': {
                // Same base salary structure as Consultant
                'A': 640000 / 12,      
                'AC': 670000 / 12,     
                'C': 750000 / 12,      
                'SrC': 800000 / 12,    
                'AM': 860000 / 12,     
                'M': 920000 / 12,     
                'SrM': 1050000 / 12,
                'Pi': 1240000 / 12,
                'P': 1548000 / 12
              },
              'Recruitment': {
                // Same base salary structure as Consultant
                'A': 640000 / 12,      
                'AC': 670000 / 12,     
                'C': 750000 / 12,      
                'SrC': 800000 / 12,    
                'AM': 860000 / 12,     
                'M': 920000 / 12,     
                'SrM': 1050000 / 12,
                'Pi': 1240000 / 12,
                'P': 1548000 / 12
              },
              'Operations': {
                'General': 640000 / 12 // Use Analyst level base salary
              }
            };
            monthlySalary = oslo2025BaseSalaries[role]?.[level] || (640000 / 12);
          }
          
          // Get additional salary components or use defaults
          let variableSalary = getValue(role, level, month, 'variable_salary');
          let socialSecurity = getValue(role, level, month, 'social_security');
          let pension = getValue(role, level, month, 'pension');
          
          // If no values found in data, use 2025 Oslo variable salary structure - same for all roles
          if (!variableSalary || variableSalary === 0) {
            const oslo2025VariableSalaries: Record<string, Record<string, number>> = {
              'Consultant': {
                'A': 0 / 12,           // 0 variable
                'AC': 20000 / 12,      // 20,000 variable yearly
                'C': 50000 / 12,       // 50,000 variable yearly
                'SrC': 80000 / 12,     // 80,000 variable yearly
                'AM': 120000 / 12,     // 120,000 variable yearly
                'M': 170000 / 12,      // 170,000 variable yearly
                'SrM': 250000 / 12,    // 250,000 variable yearly
                'Pi': 330000 / 12,     // 330,000 variable yearly
                'P': 408000 / 12       // 408,000 variable yearly
              },
              'Sales': {
                // Same variable structure as Consultant
                'A': 0 / 12,
                'AC': 20000 / 12,
                'C': 50000 / 12,
                'SrC': 80000 / 12,
                'AM': 120000 / 12,
                'M': 170000 / 12,
                'SrM': 250000 / 12,
                'Pi': 330000 / 12,
                'P': 408000 / 12
              },
              'Recruitment': {
                // Same variable structure as Consultant
                'A': 0 / 12,
                'AC': 20000 / 12,
                'C': 50000 / 12,
                'SrC': 80000 / 12,
                'AM': 120000 / 12,
                'M': 170000 / 12,
                'SrM': 250000 / 12,
                'Pi': 330000 / 12,
                'P': 408000 / 12
              },
              'Operations': {
                'General': 0 / 12  // No variable for operations
              }
            };
            variableSalary = oslo2025VariableSalaries[role]?.[level] || 0;
          }
          if (!socialSecurity || socialSecurity === 0) {
            socialSecurity = monthlySalary * 0.17;
          }
          if (!pension || pension === 0) {
            pension = monthlySalary * 0.05;
          }
          
          // Additional costs from actual data
          const other = 350; // ~350 NOK per FTE per month
          const vacation = (monthlySalary * 0.12); // Vacation pay provision
          const groupService = 1636; // ~1636 NOK per FTE per month
          
          // Calculate total salary cost for this role/level including all components
          const levelSalaryCost = endingFTE * (
            monthlySalary +     // Base salary
            variableSalary +    // Variable/bonus
            socialSecurity +    // Social security  
            pension +           // Pension
            other +             // Other costs
            vacation +          // Vacation provision
            groupService        // Group services
          );
          totalSalaryCost += levelSalaryCost;
          
          // Debug logging for salary calculations
          if (month === 1 && endingFTE > 0) {
            console.log(`Salary calculation for ${role}-${level}:`, {
              endingFTE,
              monthlySalary: Math.round(monthlySalary),
              variableSalary: Math.round(variableSalary),
              socialSecurity: Math.round(socialSecurity),
              pension: Math.round(pension),
              levelSalaryCost: Math.round(levelSalaryCost),
              totalSalaryCostSoFar: Math.round(totalSalaryCost)
            });
          }
        }
      });
    });

    // Calculate operating costs
    let operatingCosts = 0;
    const currentMonthPlan = monthlyPlans.find(p => p.month === month && p.year === year);
    
    // Calculate total FTE for scaling costs
    let totalFTE = 0;
    Object.entries(ROLE_LEVELS).forEach(([role, levels]) => {
      levels.forEach(level => {
        totalFTE += getValue(role, level, month, 'ending_fte');
      });
    });
    
    if (currentMonthPlan && currentMonthPlan.entries.length > 0) {
      // Sum up operating costs from all entries (avoiding double counting)
      const firstEntry = currentMonthPlan.entries[0];
      
      // Office-level costs (only count once, not per person)
      operatingCosts += (firstEntry as any).office_rent || 450000; // Monthly office rent
      operatingCosts += (firstEntry as any).it_related_staff || 150000; // IT costs
      operatingCosts += (firstEntry as any).office_related || 50000; // Office supplies
      operatingCosts += (firstEntry as any).external_services || 100000; // External services
      operatingCosts += (firstEntry as any).education || 30000; // Training/education
      operatingCosts += (firstEntry as any).external_representation || 20000; // External representation
      operatingCosts += (firstEntry as any).internal_representation || 15000; // Internal representation
      operatingCosts += (firstEntry as any).other_expenses || 35000; // Other
      operatingCosts += (firstEntry as any).client_loss || 0; // Client losses if any
    } else {
      // Realistic default operating costs scaled to actual FTE
      // Based on Oslo office data: should be realistic for the actual headcount
      const baseCosts = {
        office_rent: 450000,        // Fixed monthly rent
        it_related_staff: 150000,   // IT infrastructure
        office_related: 50000,      // Office supplies
        external_services: 100000,  // External consulting/services
        education: 30000,           // Training per month
        external_representation: 20000, // Client entertainment
        internal_representation: 15000, // Internal events
        other_expenses: 35000       // Miscellaneous
      };
      
      // Sum all base costs
      operatingCosts = Object.values(baseCosts).reduce((sum, cost) => sum + cost, 0);
      
      // Add variable costs that scale with headcount (beyond the base office)
      if (totalFTE > 50) {
        const extraFTE = totalFTE - 50;
        operatingCosts += extraFTE * 2000; // Additional ~2k NOK per extra FTE for supplies, etc.
      }
    }
    
    // Debug logging for operating costs
    if (month === 1) {
      console.log(`Operating costs for month ${month}:`, {
        totalFTE,
        operatingCosts: Math.round(operatingCosts),
        hasCurrentMonthPlan: !!currentMonthPlan
      });
    }

    totalCosts = totalSalaryCost + operatingCosts;
    const ebitda = totalRevenue - totalCosts;
    const ebitdaMargin = totalRevenue > 0 ? (ebitda / totalRevenue) * 100 : 0;
    
    // Debug logging for checking calculations
    if (month === 1) {
      console.log('Financial Summary for month', month, ':', {
        totalRevenue: Math.round(totalRevenue).toLocaleString('no-NO'),
        totalSalaryCost: Math.round(totalSalaryCost).toLocaleString('no-NO'),
        operatingCosts: Math.round(operatingCosts).toLocaleString('no-NO'),
        totalCosts: Math.round(totalCosts).toLocaleString('no-NO'),
        ebitda: Math.round(ebitda).toLocaleString('no-NO'),
        ebitdaMargin: ebitdaMargin.toFixed(1) + '%',
        totalFTE
      });
    }

    // Calculate category subtotals
    let totalWorkforce = 0;
    let totalNetSales = 0;
    let totalExpenses = 0;
    let totalSalaryCosts = 0;
    let totalOperatingCosts = 0;
    
    // Calculate total workforce (ending FTE across all roles/levels)
    ['Consultant', 'Sales', 'Recruitment', 'Operations'].forEach(role => {
      const levels = ROLE_LEVELS[role] || ['General'];
      levels.forEach(level => {
        totalWorkforce += getValue(role, level, month, 'ending_fte');
      });
    });
    
    // Total Net Sales = Revenue
    totalNetSales = totalRevenue;
    
    // Total Expenses (non-salary operating costs)
    const expenseFields = [
      'client_loss', 'education', 'external_representation', 'external_services',
      'internal_representation', 'it_related_staff', 'office_related', 'office_rent',
      'other_expenses'
    ];
    expenseFields.forEach(fieldKey => {
      totalExpenses += getValue('Consultant', 'A', month, fieldKey) * officeMultiplier;
    });
    
    // Total Salary Costs (salary-related costs)
    totalSalaryCosts = totalSalaryCost;
    
    // Total Operating Costs = Expenses + Salaries
    totalOperatingCosts = totalExpenses + totalSalaryCosts;

    return { 
      totalRevenue, 
      totalSalaryCost, 
      totalCosts, 
      ebitda, 
      ebitdaMargin,
      totalWorkforce,
      totalNetSales,
      totalExpenses,
      totalSalaryCosts,
      totalOperatingCosts
    };
  }, [getValue, isAggregated, selectedOffices, monthlyPlans, year]);

  // Build table rows
  const tableRows = useMemo(() => {
    const rows: TableRow[] = [];
    let rowId = 0;

    TABLE_STRUCTURE.forEach(category => {
      const categoryId = `row-${rowId++}`;
      
      // Add category row
      const categoryRow = {
        id: categoryId,
        type: 'category',
        name: category.name,
        depth: 0,
        isEditable: false,
        isCalculated: false,
        children: []
      };
      rows.push(categoryRow);

      category.fields.forEach(field => {
        const fieldId = `row-${rowId++}`;
        categoryRow.children.push(fieldId);

        if (field.hasRoles) {
          // Field with role/level breakdown
          rows.push({
            id: fieldId,
            type: 'field',
            name: field.name,
            depth: 1,
            isEditable: false,
            isCalculated: false,
            parentId: categoryId,
            children: []
          });

          field.roles!.forEach(role => {
            const roleId = `row-${rowId++}`;
            const fieldRow = rows.find(r => r.id === fieldId);
            if (fieldRow && fieldRow.children) {
              fieldRow.children.push(roleId);
            }

            const roleRow = {
              id: roleId,
              type: 'role' as RowType,
              name: role,
              depth: 2,
              isEditable: false,
              isCalculated: false,
              parentId: fieldId,
              children: [] as string[]
            };
            rows.push(roleRow);

            const levels = ROLE_LEVELS[role] || ['A'];
            levels.forEach(level => {
              const levelId = `row-${rowId++}`;
              roleRow.children.push(levelId);

              // Create monthly data
              const monthlyData: any = {};
              let total = 0;

              MONTHS.forEach((month, idx) => {
                const value = getValue(role, level, idx + 1, field.fieldKey);
                monthlyData[month] = value;
                total += value;
              });

              rows.push({
                id: levelId,
                type: 'level',
                name: level,
                depth: 3,
                isEditable: !field.isCalculated, // Show as editable but handle clicks differently
                isCalculated: !!field.isCalculated,
                parentId: roleId,
                fieldKey: field.fieldKey,
                role: role as StandardRole,
                level: level as StandardLevel,
                ...monthlyData,
                total
              });
            });
          });
        } else {
          // Office-level field (no role breakdown)
          const monthlyData: any = {};
          let total = 0;

          MONTHS.forEach((month, idx) => {
            let value = 0;
            
            if (field.isCalculated) {
              // Calculate summary fields and time-based calculations
              const summary = calculateSummaryFields(idx + 1);
              switch (field.fieldKey) {
                case 'total_revenue':
                  value = summary.totalRevenue;
                  break;
                case 'total_salary_cost':
                  value = summary.totalSalaryCost;
                  break;
                case 'total_costs':
                  value = summary.totalCosts;
                  break;
                case 'ebitda':
                  value = summary.ebitda;
                  break;
                case 'ebitda_margin':
                  value = summary.ebitdaMargin;
                  break;
                case 'total_workforce':
                  value = summary.totalWorkforce;
                  break;
                case 'total_net_sales':
                  value = summary.totalNetSales;
                  break;
                case 'total_expenses':
                  value = summary.totalExpenses;
                  break;
                case 'total_salary_costs':
                  value = summary.totalSalaryCosts;
                  break;
                case 'total_operating_costs':
                  value = summary.totalOperatingCosts;
                  break;
                case 'available_consultant_time':
                  // Calculate from actual time fields from business plan data
                  let totalConsultantTime = 0;
                  let totalPlannedAbsence = 0;
                  let totalUnplannedAbsence = 0;
                  let totalVacation = 0;
                  let totalVacationWithdrawal = 0;
                  
                  // Get data from current month's plan
                  const currentMonthPlan = monthlyPlans.find(p => p.month === idx + 1 && p.year === year);
                  if (currentMonthPlan) {
                    currentMonthPlan.entries.forEach(entry => {
                      if (entry.role === 'Consultant') {
                        totalConsultantTime += (entry as any).consultant_time || 160;
                        totalPlannedAbsence += (entry as any).planned_absence || 0;
                        totalUnplannedAbsence += (entry as any).unplanned_absence || 0;
                        totalVacation += (entry as any).vacation || 0;
                        totalVacationWithdrawal += (entry as any).vacation_withdrawal || 0;
                      }
                    });
                  }
                  
                  value = totalConsultantTime - totalPlannedAbsence - totalUnplannedAbsence - totalVacation + totalVacationWithdrawal;
                  break;
              }
            } else {
              // For office-level fields, check if we have data from business plan entries
              const currentMonthPlan = monthlyPlans.find(p => p.month === idx + 1 && p.year === year);
              if (currentMonthPlan && currentMonthPlan.entries.length > 0) {
                // Try to get value from first entry (office-level fields apply to all)
                const firstEntry = currentMonthPlan.entries[0];
                if (firstEntry && field.fieldKey) {
                  // Check for exact field match first
                  if (field.fieldKey in firstEntry && (firstEntry as any)[field.fieldKey] !== undefined) {
                    value = (firstEntry as any)[field.fieldKey];
                  }
                  // Check for legacy field mappings
                  else if (field.fieldKey === 'utilization_rate' && 'utr' in firstEntry && (firstEntry as any).utr !== undefined) {
                    value = (firstEntry as any).utr;
                  }
                  else if (field.fieldKey === 'average_price' && 'price' in firstEntry && (firstEntry as any).price !== undefined) {
                    value = (firstEntry as any).price;
                  }
                  else {
                    value = field.defaultValue || 0;
                  }
                } else {
                  value = field.defaultValue || 0;
                }
              } else {
                // Use default value for office-level fields when no plan data
                value = field.defaultValue || 0;
              }
            }
            
            monthlyData[month] = value;
            total += value;
          });

          rows.push({
            id: fieldId,
            type: 'office-field',
            name: field.name,
            depth: 1,
            isEditable: !field.isCalculated, // Show as editable but handle clicks differently
            isCalculated: !!field.isCalculated,
            isSubtotal: !!(field as any).isSubtotal,
            parentId: categoryId,
            fieldKey: field.fieldKey,
            ...monthlyData,
            total
          });
        }
      });
    });

    return rows;
  }, [getValue, calculateSummaryFields]);

  // Toggle row expansion
  const toggleRow = useCallback((rowId: string) => {
    setExpandedRows(prev => {
      const next = new Set(prev);
      if (next.has(rowId)) {
        next.delete(rowId);
      } else {
        next.add(rowId);
      }
      return next;
    });
  }, []);

  // Handle cell edit
  const handleCellEdit = useCallback((rowId: string, month: string, value: number) => {
    const row = tableRows.find(r => r.id === rowId);
    if (!row || !row.isEditable) return;

    const monthIndex = MONTHS.indexOf(month as any) + 1;
    const changeKey = `${row.role}-${row.level}-${monthIndex}-${row.fieldKey}`;
    
    setLocalChanges(prev => new Map(prev).set(changeKey, value));
  }, [tableRows]);

  // Save changes
  const handleSave = useCallback(async () => {
    if (!office?.id || localChanges.size === 0) return;

    // Group changes by month
    const changesByMonth = new Map<number, Map<string, MonthlyPlanEntry>>();

    localChanges.forEach((value, key) => {
      const [role, level, month, field] = key.split('-');
      const monthNum = parseInt(month);
      
      if (!changesByMonth.has(monthNum)) {
        changesByMonth.set(monthNum, new Map());
      }
      
      const monthChanges = changesByMonth.get(monthNum)!;
      const entryKey = `${role}-${level}`;
      
      if (!monthChanges.has(entryKey)) {
        const existing = planDataMap.get(`${role}-${level}-${monthNum}`);
        monthChanges.set(entryKey, {
          role: role as StandardRole,
          level: level as StandardLevel,
          recruitment: existing?.recruitment || 0,
          churn: existing?.churn || 0,
          salary: existing?.salary || getValue(role, level, monthNum, 'salary'),
          price: existing?.price || 1200,
          utr: existing?.utr || 0.75
        });
      }
      
      const entry = monthChanges.get(entryKey)!;
      (entry as any)[field] = value;
    });

    // Save all changes
    const promises: Promise<any>[] = [];
    
    changesByMonth.forEach((entries, month) => {
      const entriesArray = Array.from(entries.values());
      const existingPlan = monthlyPlans.find(p => p.month === month && p.year === year);
      
      if (existingPlan) {
        promises.push(updateMonthlyPlan({
          ...existingPlan,
          entries: entriesArray
        }));
      } else {
        promises.push(createMonthlyPlan({
          office_id: office.id,
          year,
          month,
          entries: entriesArray
        }));
      }
    });

    await Promise.all(promises);
    
    // Clear local changes and reload
    setLocalChanges(new Map());
    await loadBusinessPlans(office.id, year);
  }, [office?.id, localChanges, planDataMap, monthlyPlans, year, updateMonthlyPlan, createMonthlyPlan, loadBusinessPlans]);

  // Filter visible rows based on expansion state
  const visibleRows = useMemo(() => {
    const visible: TableRow[] = [];
    
    const addRow = (row: TableRow) => {
      visible.push(row);
      
      if (row.children && expandedRows.has(row.id)) {
        row.children.forEach(childId => {
          const child = tableRows.find(r => r.id === childId);
          if (child) addRow(child);
        });
      }
    };
    
    tableRows.filter(r => !r.parentId).forEach(addRow);
    
    return visible;
  }, [tableRows, expandedRows]);

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
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg border">
        <h3 className="font-semibold">
          {isAggregated ? `Aggregated (${selectedOffices.length} offices)` : office.name} - {year} Business Plan
        </h3>
        <div className="flex gap-2">
          {!isAggregated && localChanges.size > 0 && (
            <>
              <button
                onClick={() => setLocalChanges(new Map())}
                className="px-3 py-1 text-sm border rounded hover:bg-muted"
              >
                Discard Changes
              </button>
              <button
                onClick={handleSave}
                className="px-3 py-1 text-sm bg-primary text-primary-foreground rounded hover:bg-primary/90"
              >
                Save Changes ({localChanges.size})
              </button>
            </>
          )}
          {isAggregated && (
            <div className="px-3 py-1 text-sm text-muted-foreground">
              Read-only aggregated data
            </div>
          )}
        </div>
      </div>

      {/* KPI Cards */}
      <PlanningKPICards 
        kpis={{
          totalRecruitment: 48,
          totalChurn: 24,
          netRecruitment: 24,
          netRecruitmentPercent: 15.8,
          netRevenue: 2150000,
          avgPriceIncrease: 5.2,
          avgTargetUTR: 78.5
        }}
        className="mb-4"
      />

      {/* Table */}
      <div className="overflow-hidden rounded-md border border-gray-600 bg-black">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-600 hover:bg-transparent">
              <th className="h-12 px-4 text-left align-middle text-sm font-semibold text-white bg-gray-800 border-r border-gray-600 w-80">
                Category / Field / Role / Level
              </th>
              {MONTH_LABELS.map(month => (
                <th key={month} className="h-12 px-4 text-center align-middle text-sm font-semibold text-white bg-gray-800 border-r border-gray-600 w-20">
                  {month}
                </th>
              ))}
              <th className="h-12 px-4 text-center align-middle text-sm font-semibold text-white bg-gray-800 w-24">
                Total
              </th>
            </tr>
          </thead>
          <tbody>
            {visibleRows.map(row => (
              <tr
                key={row.id}
                className={cn(
                  "border-b border-gray-600 transition-colors hover:bg-gray-800",
                  row.type === 'category' && "bg-gray-900 font-semibold",
                  row.type === 'office-field' && row.isCalculated && !row.isSubtotal && "bg-green-950/20",
                  row.isSubtotal && "bg-blue-950/30 border-blue-500/30 font-semibold"
                )}
              >
                <td className="px-4 py-3 align-middle text-base font-medium text-white border-r border-gray-600">
                  <div
                    className="flex items-center gap-2"
                    style={{ paddingLeft: `${row.depth * 20}px` }}
                  >
                    {row.children && row.children.length > 0 && (
                      <button
                        onClick={() => toggleRow(row.id)}
                        className="h-6 w-6 p-0 hover:bg-gray-700 rounded"
                      >
                        {expandedRows.has(row.id) ? (
                          <ChevronDown className="h-4 w-4 text-white" />
                        ) : (
                          <ChevronRight className="h-4 w-4 text-white" />
                        )}
                      </button>
                    )}
                    <span className={cn(
                      "font-semibold",
                      row.type === 'category' && "text-base",
                      row.type === 'field' && "text-sm font-medium",
                      row.type === 'role' && "text-sm",
                      row.type === 'level' && "text-sm text-gray-400",
                      row.type === 'office-field' && "text-sm"
                    )}>
                      {row.name}
                    </span>
                  </div>
                </td>
                
                {/* Month cells */}
                {MONTHS.map(month => {
                  const cellKey = `${row.id}-${month}`;
                  const value = row[month];
                  const isEditing = editingCell === cellKey;
                  
                  // Non-data rows show empty cells
                  if (row.type === 'category' || row.type === 'field' || row.type === 'role') {
                    return (
                      <td key={month} className="px-4 py-3 align-middle text-base font-medium text-white border-r border-gray-600 last:border-r-0">
                        <span className="text-gray-400">-</span>
                      </td>
                    );
                  }
                  
                  return (
                    <td key={month} className="px-4 py-3 align-middle text-base font-medium text-white border-r border-gray-600 last:border-r-0">
                      {isEditing && row.isEditable ? (
                        <input
                          type="number"
                          defaultValue={value}
                          onBlur={(e) => {
                            handleCellEdit(row.id, month, parseFloat(e.target.value) || 0);
                            setEditingCell(null);
                          }}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') {
                              handleCellEdit(row.id, month, parseFloat(e.currentTarget.value) || 0);
                              setEditingCell(null);
                            }
                            if (e.key === 'Escape') {
                              setEditingCell(null);
                            }
                          }}
                          className="h-8 w-full bg-gray-700 text-white border-gray-500 text-center text-xs focus:outline-none focus:ring-2 focus:ring-primary [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                          autoFocus
                        />
                      ) : (
                        <div
                          onClick={() => row.isEditable && !isAggregated && setEditingCell(cellKey)}
                          className={cn(
                            "text-center p-1 rounded",
                            row.isEditable && "cursor-pointer hover:bg-gray-700 border border-yellow-400/70 hover:border-yellow-400",
                            !row.isEditable && "text-gray-500 cursor-not-allowed",
                            row.isCalculated && "text-green-300 font-medium",
                            isAggregated && row.isEditable && "cursor-default", // Override cursor for aggregated
                            localChanges.has(`${row.role}-${row.level}-${MONTHS.indexOf(month) + 1}-${row.fieldKey}`) && 
                              "bg-blue-950/30"
                          )}
                          title={isAggregated ? "Read-only aggregated data" : (row.isEditable ? "Click to edit" : "Read-only field")}
                        >
                          {value !== undefined ? formatValue(value, row.fieldKey) : '-'}
                        </div>
                      )}
                    </td>
                  );
                })}
                
                {/* Total cell */}
                <td className="px-4 py-3 align-middle text-base font-medium text-white text-center">
                  <div className={cn(
                    "p-1 rounded text-center",
                    row.type === 'level' || row.type === 'office-field' ? (
                      row.isCalculated ? "text-green-300 font-medium" : "text-gray-500"
                    ) : "text-gray-500"
                  )}>
                    {row.total !== undefined ? formatValue(row.total, row.fieldKey) : '-'}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// ============================================================================
// HELPERS
// ============================================================================

function formatValue(value: number, fieldKey?: string): string {
  if (fieldKey === 'utr' || fieldKey === 'utilization_rate') {
    return `${Math.round(value * 100)}%`;
  }
  if (fieldKey === 'ebitda_margin') {
    return `${value.toFixed(1)}%`;
  }
  // Format currency fields with NOK
  if (fieldKey === 'price' || fieldKey === 'average_price') {
    return `${Math.round(value).toLocaleString('no-NO')} kr`;
  }
  if (fieldKey?.includes('cost') || fieldKey?.includes('salary') || fieldKey?.includes('revenue') || fieldKey?.includes('ebitda') || fieldKey?.includes('rent') || fieldKey?.includes('education') || fieldKey?.includes('services') || fieldKey?.includes('expenses') || fieldKey?.includes('operating') || fieldKey?.includes('sales')) {
    return value >= 1000 ? `${Math.round(value / 1000).toLocaleString('no-NO')}k kr` : `${Math.round(value).toLocaleString('no-NO')} kr`;
  }
  if (fieldKey?.includes('workforce') && fieldKey !== 'total_workforce') {
    return Math.round(value).toString() + ' FTE';
  }
  if (fieldKey === 'total_workforce') {
    return `${Math.round(value)} Total FTE`;
  }
  return Math.round(value).toString();
}