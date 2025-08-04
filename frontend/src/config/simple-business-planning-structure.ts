/**
 * Simple, Clear Business Planning Structure
 * 
 * This structure makes it crystal clear:
 * 1. What sections exist and in what order
 * 2. What fields belong to each section  
 * 3. Whether fields are office-wide or per role/level
 * 4. What roles/levels each field applies to
 * 5. What kind of values they contain
 */

import { StandardRole, StandardLevel } from '../types/office';
import { DollarSign, Users, Clock, UserPlus, UserMinus, Building2, Calculator, Target, TrendingUp } from 'lucide-react';

// Simple field types
export type SimpleFieldType = 'input' | 'calculated';
export type SimpleFieldLevel = 'office' | 'role_level';
export type SimpleValueType = 'currency' | 'percentage' | 'hours' | 'count' | 'rate';

// Crystal clear field definition
export interface SimpleField {
  id: string;
  label: string;
  icon: any;
  
  // Scope - makes it obvious how to render
  level: SimpleFieldLevel;
  applicableRoles?: StandardRole[]; // if undefined, applies to all roles
  
  // Value info - makes formatting obvious  
  type: SimpleFieldType;
  valueType: SimpleValueType;
  
  // UI hints
  color: string;
  isKPI?: boolean;
}

// Subcategory within a section
export interface SimpleSubcategory {
  id: string;
  name: string;
  order: number;
  fields: SimpleField[];
}

// Section with clear field organization - supports both direct fields and subcategories
export interface SimpleSection {
  id: string;
  name: string;
  icon: any;
  color: string;
  order: number;
  fields?: SimpleField[];        // Direct fields (for simple sections)
  subcategories?: SimpleSubcategory[];  // Subcategories (for complex sections)
}

// THE COMPLETE STRUCTURE - easy to understand at a glance
export const BUSINESS_PLANNING_STRUCTURE: SimpleSection[] = [
  {
    id: 'sales',
    name: 'Sales',
    icon: DollarSign,
    color: 'text-green-600',
    order: 1,
    fields: [
      {
        id: 'price',
        label: 'Hourly Rate (€/h)',
        icon: DollarSign,
        level: 'role_level',
        applicableRoles: ['Consultant'], // Only consultants have hourly rates
        type: 'input',
        valueType: 'currency',
        color: 'text-blue-600'
      },
      {
        id: 'utr',
        label: 'Utilization Rate',
        icon: Clock,
        level: 'role_level', 
        applicableRoles: ['Consultant'], // Only consultants have utilization
        type: 'input',
        valueType: 'percentage',
        color: 'text-purple-600'
      },
      {
        id: 'monthly_hours',
        label: 'Monthly Hours',
        icon: Clock,
        level: 'office', // Office-wide standard - single value for all
        type: 'input',
        valueType: 'hours',
        color: 'text-indigo-600'
      },
      {
        id: 'absence',
        label: 'Absence Hours',
        icon: Clock,
        level: 'role_level',
        applicableRoles: ['Consultant'],
        type: 'input',
        valueType: 'hours',  
        color: 'text-red-600'
      },
      {
        id: 'billable_hours',
        label: 'Billable Hours',
        icon: Clock,
        level: 'role_level',
        applicableRoles: ['Consultant'],
        type: 'calculated', // monthly_hours - absence
        valueType: 'hours',
        color: 'text-green-600'
      },
      {
        id: 'net_sales',
        label: 'Net Sales',
        icon: DollarSign,
        level: 'role_level',
        applicableRoles: ['Consultant'],
        type: 'calculated', // price × utr × billable_hours × fte
        valueType: 'currency',
        color: 'text-green-600',
        isKPI: true
      }
    ]
  },
  
  {
    id: 'workforce_planning',
    name: 'Workforce Planning',
    icon: Users,
    color: 'text-blue-600', 
    order: 2,
    fields: [
      {
        id: 'fte',
        label: 'FTE Count',
        icon: Users,
        level: 'role_level', // Each role/level has its own FTE
        // No applicableRoles = applies to all roles
        type: 'input',
        valueType: 'count',
        color: 'text-blue-600',
        isKPI: true
      },
      {
        id: 'recruitment',
        label: 'Recruitment',
        icon: UserPlus,
        level: 'role_level', // Each role/level can have recruitment
        type: 'input',
        valueType: 'count',
        color: 'text-green-600',
        isKPI: true
      },
      {
        id: 'churn',
        label: 'Churn',
        icon: UserMinus,
        level: 'role_level', // Each role/level can have churn
        type: 'input',
        valueType: 'count',
        color: 'text-red-600',
        isKPI: true
      },
      {
        id: 'net_headcount_change',
        label: 'Net Headcount Change',
        icon: TrendingUp,
        level: 'role_level',
        type: 'calculated', // recruitment - churn
        valueType: 'count',
        color: 'text-blue-600',
        isKPI: true
      }
    ]
  },

  {
    id: 'operating_expenses',
    name: 'Operating Expenses',
    icon: Building2,
    color: 'text-indigo-600',
    order: 3,
    subcategories: [
      {
        id: 'compensation',
        name: 'Compensation & Benefits',
        order: 1,
        fields: [
          {
            id: 'base_salary',
            label: 'Base Salary (€)',
            icon: DollarSign,
            level: 'role_level', // Each role/level has different salary
            type: 'input',
            valueType: 'currency',
            color: 'text-orange-600'
          },
          {
            id: 'social_security',
            label: 'Social Security (25%)',
            icon: Calculator,
            level: 'role_level',
            type: 'calculated', // base_salary × 0.25
            valueType: 'currency',
            color: 'text-gray-600'
          },
          {
            id: 'total_people_costs',
            label: 'Total People Costs',
            icon: Calculator,
            level: 'role_level',
            type: 'calculated', // base_salary + social_security
            valueType: 'currency',
            color: 'text-orange-600',
            isKPI: true
          }
        ]
      },
      {
        id: 'facilities',
        name: 'Facilities & Infrastructure',
        order: 2,
        fields: [
          {
            id: 'office_rent',
            label: 'Office Rent (€)',
            icon: Building2,
            level: 'office', // Office-wide expense
            type: 'input',
            valueType: 'currency',
            color: 'text-indigo-600'
          },
          {
            id: 'utilities',
            label: 'Utilities (€)',
            icon: Building2,
            level: 'office',
            type: 'input',
            valueType: 'currency',
            color: 'text-blue-600'
          }
        ]
      },
      {
        id: 'expense_summary',
        name: 'Expense Summary',
        order: 3,
        fields: [
          {
            id: 'total_operating_expenses',
            label: 'Total Operating Expenses',
            icon: Calculator,
            level: 'office', // Office-wide total
            type: 'calculated',
            valueType: 'currency',
            color: 'text-red-600',
            isKPI: true
          }
        ]
      }
    ]
  },

  {
    id: 'financial_summary',
    name: 'Financial Summary',
    icon: Target,
    color: 'text-purple-600',
    order: 4,
    fields: [
      {
        id: 'total_revenue',
        label: 'Total Revenue',
        icon: DollarSign,
        level: 'office', // Office-wide total
        type: 'calculated',
        valueType: 'currency',
        color: 'text-green-600',
        isKPI: true
      },
      {
        id: 'ebitda',
        label: 'EBITDA',
        icon: TrendingUp,
        level: 'office', // Office-wide metric
        type: 'calculated',
        valueType: 'currency',
        color: 'text-green-600',
        isKPI: true
      },
      {
        id: 'ebitda_margin',
        label: 'EBITDA Margin %',
        icon: Target,
        level: 'office', // Office-wide percentage
        type: 'calculated',
        valueType: 'percentage',
        color: 'text-purple-600',
        isKPI: true
      }
    ]
  }
];

// HELPER FUNCTIONS - make frontend rendering super simple

// Helper to get all fields from a section (handles both direct fields and subcategories)
function getAllFieldsFromSection(section: SimpleSection): SimpleField[] {
  const fields: SimpleField[] = [];
  
  // Add direct fields if they exist
  if (section.fields) {
    fields.push(...section.fields);
  }
  
  // Add fields from subcategories if they exist
  if (section.subcategories) {
    section.subcategories.forEach(subcategory => {
      fields.push(...subcategory.fields);
    });
  }
  
  return fields;
}

export function getOfficeFields(): SimpleField[] {
  return BUSINESS_PLANNING_STRUCTURE
    .flatMap(section => getAllFieldsFromSection(section))
    .filter(field => field.level === 'office');
}

export function getRoleLevelFields(): SimpleField[] {
  return BUSINESS_PLANNING_STRUCTURE
    .flatMap(section => getAllFieldsFromSection(section))
    .filter(field => field.level === 'role_level');
}

export function getFieldsForRole(role: StandardRole): SimpleField[] {
  return getRoleLevelFields().filter(field => 
    !field.applicableRoles || field.applicableRoles.includes(role)
  );
}

export function getFieldById(fieldId: string): SimpleField | undefined {
  return BUSINESS_PLANNING_STRUCTURE
    .flatMap(section => getAllFieldsFromSection(section))
    .find(field => field.id === fieldId);
}

export function getSection(sectionId: string): SimpleSection | undefined {
  return BUSINESS_PLANNING_STRUCTURE.find(section => section.id === sectionId);
}

// VALUE FORMATTING - simple and clear
export function formatFieldValue(field: SimpleField, value: number): string {
  switch (field.valueType) {
    case 'currency':
      return `€${Math.round(value).toLocaleString()}`;
    case 'percentage':
      return `${(value * 100).toFixed(1)}%`;
    case 'hours':
      return `${Math.round(value)}h`;
    case 'count':
      return Math.round(value).toString();
    case 'rate':
      return `€${Math.round(value)}/h`;
    default:
      return value.toString();
  }
}

// ORGANIZATIONAL STRUCTURE HELPERS
export const LEVELED_ROLES: StandardRole[] = ['Consultant', 'Sales', 'Recruitment']; // Salary ladder with A, B, C levels
export const FLAT_ROLES: StandardRole[] = ['Operations']; // Fixed salary, no levels
export const ALL_ROLES: StandardRole[] = [...LEVELED_ROLES, ...FLAT_ROLES];

export function getRoleLevels(role: StandardRole): StandardLevel[] {
  return LEVELED_ROLES.includes(role) ? ['A', 'B', 'C'] : ['General'];
}

export function isLeveledRole(role: StandardRole): boolean {
  return LEVELED_ROLES.includes(role);
}

// RENDERING LOGIC - crystal clear how to build the table
export interface TableRow {
  id: string;
  sectionName: string;
  fieldName: string;
  role?: StandardRole;
  level?: StandardLevel;
  displayName: string;
  isOfficeLevel: boolean;
  values: {
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
  };
}

export function generateTableRows(): TableRow[] {
  const rows: TableRow[] = [];

  BUSINESS_PLANNING_STRUCTURE.forEach(section => {
    // Handle sections with direct fields
    if (section.fields) {
      section.fields.forEach(field => {
        addFieldRows(rows, section, field, section.name);
      });
    }
    
    // Handle sections with subcategories
    if (section.subcategories) {
      section.subcategories.forEach(subcategory => {
        subcategory.fields.forEach(field => {
          addFieldRows(rows, section, field, `${section.name} - ${subcategory.name}`);
        });
      });
    }
  });

  return rows;
}

// Helper function to add field rows (office-level or role-level)
function addFieldRows(rows: TableRow[], section: SimpleSection, field: SimpleField, categoryName: string): void {
  if (field.level === 'office') {
    // Office-level field - single row
    rows.push({
      id: `${section.id}-${field.id}`,
      sectionName: section.name,
      fieldName: field.label,
      displayName: field.label,
      isOfficeLevel: true,
      values: {
        jan: 0, feb: 0, mar: 0, apr: 0, may: 0, jun: 0,
        jul: 0, aug: 0, sep: 0, oct: 0, nov: 0, dec: 0, total: 0
      }
    });
  } else {
    // Role/level field - multiple rows based on organizational structure
    ALL_ROLES.forEach(role => {
      // Check if field applies to this role
      if (!field.applicableRoles || field.applicableRoles.includes(role)) {
        const roleLevels = getRoleLevels(role); // Uses organizational structure
        
        roleLevels.forEach(level => {
          rows.push({
            id: `${section.id}-${field.id}-${role}-${level}`,
            sectionName: categoryName,
            fieldName: field.label,
            role,
            level: level as StandardLevel,
            displayName: `${field.label} - ${role} ${level}`,
            isOfficeLevel: false,
            values: {
              jan: 0, feb: 0, mar: 0, apr: 0, may: 0, jun: 0,
              jul: 0, aug: 0, sep: 0, oct: 0, nov: 0, dec: 0, total: 0
            }
          });
        });
      }
    });
  }
}