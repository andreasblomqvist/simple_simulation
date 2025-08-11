/**
 * Business Planning Field Definitions & System Configuration
 * 
 * This file contains the complete field registry with role-specific applicability,
 * hierarchical sections, and business logic for the business planning system.
 */

import {
  BusinessPlanningFieldRegistry,
  BusinessPlanningFieldImpl,
  BusinessPlanningSection,
  FieldMetadata,
  FieldLevel,
  FieldCategory,
  FieldType
} from '../types/business-planning-structure';
import { StandardRole } from '../types/office';
import {
  DollarSign,
  Users,
  TrendingUp,
  Clock,
  UserPlus,
  UserMinus,
  Calculator,
  Building2,
  Target,
  ArrowUpRight,
  PieChart,
  BarChart3,
  Calendar
} from 'lucide-react';

// ==========================================
// FIELD DEFINITIONS WITH ROLE APPLICABILITY
// ==========================================

const FIELD_DEFINITIONS: FieldMetadata[] = [
  // ==========================================
  // REVENUE PLANNING FIELDS
  // ==========================================
  {
    id: 'price',
    label: 'Hourly Rate',
    icon: DollarSign,
    type: 'input' as FieldType,
    level: 'role_level' as FieldLevel,
    category: 'revenue' as FieldCategory,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 dark:bg-blue-950/20',
    description: 'Hourly billing rate for billable roles',
    valueType: 'rate',
    currencyCode: 'EUR',
    precision: 0,
    min: 0,
    step: 10,
    applicableRoles: ['Consultant'], // Only consultants have hourly rates
    isEditable: true,
    showInSummary: true,
    aggregateMethod: 'average',
    contributesToRevenue: true,
    isKPI: false
  },
  {
    id: 'utr',
    label: 'Utilization Rate',
    icon: Clock,
    type: 'input' as FieldType,
    level: 'role_level' as FieldLevel,
    category: 'revenue' as FieldCategory,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50 dark:bg-purple-950/20',
    description: 'Target utilization rate (0.0 - 1.0)',
    valueType: 'percentage',
    precision: 1,
    min: 0,
    max: 1,
    step: 0.01,
    applicableRoles: ['Consultant'], // Only consultants have utilization
    isEditable: true,
    showInSummary: true,
    aggregateMethod: 'average',
    contributesToRevenue: true,
    isKPI: true
  },
  {
    id: 'monthly_hours',
    label: 'Monthly Hours',
    icon: Clock,
    type: 'input' as FieldType,
    level: 'office' as FieldLevel,
    category: 'revenue' as FieldCategory,
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-50 dark:bg-indigo-950/20',
    description: 'Available working hours per month (office-wide standard)',
    valueType: 'hours',
    precision: 0,
    min: 0,
    max: 200,
    step: 1,
    isEditable: true,
    showInSummary: false,
    aggregateMethod: 'none',
    contributesToRevenue: true,
    isKPI: false
  },
  {
    id: 'absence',
    label: 'Absence',
    icon: Clock,
    type: 'input' as FieldType,
    level: 'role_level' as FieldLevel,
    category: 'revenue' as FieldCategory,
    color: 'text-red-600',
    bgColor: 'bg-red-50 dark:bg-red-950/20',
    description: 'Absence hours per month',
    valueType: 'hours',
    precision: 0,
    min: 0,
    max: 200,
    step: 1,
    applicableRoles: ['Consultant'],
    isEditable: true,
    showInSummary: false,
    aggregateMethod: 'sum',
    contributesToRevenue: false,
    isKPI: false
  },
  {
    id: 'billable_hours',
    label: 'Billable Hours',
    icon: Clock,
    type: 'calculated' as FieldType,
    level: 'role_level' as FieldLevel,
    category: 'revenue' as FieldCategory,
    color: 'text-green-600',
    bgColor: 'bg-green-50 dark:bg-green-950/20',
    description: 'Billable hours (monthly_hours - absence)',
    valueType: 'hours',
    precision: 0,
    formula: 'monthly_hours - absence',
    dependencies: ['monthly_hours', 'absence'],
    applicableRoles: ['Consultant'],
    isEditable: false,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToRevenue: true,
    isKPI: false
  },
  // ==========================================
  // DETAILED NET SALES FIELDS
  // ==========================================
  {
    id: 'consultant_time',
    label: 'Consultant Time',
    icon: Clock,
    type: 'input' as FieldType,
    level: 'role_level' as FieldLevel,
    category: 'revenue' as FieldCategory,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 dark:bg-blue-950/20',
    description: 'Total available consultant time per month',
    valueType: 'hours',
    precision: 0,
    min: 0,
    max: 200,
    step: 1,
    applicableRoles: ['Consultant'],
    isEditable: true,
    showInSummary: false,
    aggregateMethod: 'sum',
    contributesToRevenue: true,
    isKPI: false
  },
  {
    id: 'planned_absence',
    label: 'Planned Absence',
    icon: Calendar,
    type: 'input' as FieldType,
    level: 'role_level' as FieldLevel,
    category: 'revenue' as FieldCategory,
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-50 dark:bg-yellow-950/20',
    description: 'Planned absence hours (training, meetings)',
    valueType: 'hours',
    precision: 0,
    min: 0,
    max: 100,
    step: 1,
    applicableRoles: ['Consultant'],
    isEditable: true,
    showInSummary: false,
    aggregateMethod: 'sum',
    contributesToRevenue: false,
    isKPI: false
  },
  {
    id: 'unplanned_absence',
    label: 'Unplanned Absence',
    icon: Clock,
    type: 'input' as FieldType,
    level: 'role_level' as FieldLevel,
    category: 'revenue' as FieldCategory,
    color: 'text-red-600',
    bgColor: 'bg-red-50 dark:bg-red-950/20',
    description: 'Unplanned absence hours (sick leave, emergency)',
    valueType: 'hours',
    precision: 0,
    min: 0,
    max: 100,
    step: 1,
    applicableRoles: ['Consultant'],
    isEditable: true,
    showInSummary: false,
    aggregateMethod: 'sum',
    contributesToRevenue: false,
    isKPI: false
  },
  {
    id: 'vacation_withdrawal',
    label: 'Vacation Withdrawal',
    icon: Calendar,
    type: 'input' as FieldType,
    level: 'role_level' as FieldLevel,
    category: 'revenue' as FieldCategory,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50 dark:bg-orange-950/20',
    description: 'Vacation withdrawal hours',
    valueType: 'hours',
    precision: 0,
    min: 0,
    max: 100,
    step: 1,
    applicableRoles: ['Consultant'],
    isEditable: true,
    showInSummary: false,
    aggregateMethod: 'sum',
    contributesToRevenue: false,
    isKPI: false
  },
  {
    id: 'vacation',
    label: 'Vacation',
    icon: Calendar,
    type: 'input' as FieldType,
    level: 'role_level' as FieldLevel,
    category: 'revenue' as FieldCategory,
    color: 'text-green-600',
    bgColor: 'bg-green-50 dark:bg-green-950/20',
    description: 'Regular vacation hours',
    valueType: 'hours',
    precision: 0,
    min: 0,
    max: 100,
    step: 1,
    applicableRoles: ['Consultant'],
    isEditable: true,
    showInSummary: false,
    aggregateMethod: 'sum',
    contributesToRevenue: false,
    isKPI: false
  },
  {
    id: 'available_consultant_time',
    label: 'Available Consultant Time',
    icon: Clock,
    type: 'calculated' as FieldType,
    level: 'role_level' as FieldLevel,
    category: 'revenue' as FieldCategory,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 dark:bg-blue-950/20',
    description: 'Available time after all absences',
    valueType: 'hours',
    precision: 0,
    formula: 'consultant_time - planned_absence - unplanned_absence - vacation_withdrawal - vacation',
    dependencies: ['consultant_time', 'planned_absence', 'unplanned_absence', 'vacation_withdrawal', 'vacation'],
    applicableRoles: ['Consultant'],
    isEditable: false,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToRevenue: true,
    isKPI: true
  },
  {
    id: 'invoiced_time',
    label: 'Invoiced Time',
    icon: DollarSign,
    type: 'calculated' as FieldType,
    level: 'role_level' as FieldLevel,
    category: 'revenue' as FieldCategory,
    color: 'text-green-600',
    bgColor: 'bg-green-50 dark:bg-green-950/20',
    description: 'Billable time that gets invoiced (available_time × utilization_rate)',
    valueType: 'hours',
    precision: 0,
    formula: 'available_consultant_time × utr',
    dependencies: ['available_consultant_time', 'utr'],
    applicableRoles: ['Consultant'],
    isEditable: false,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToRevenue: true,
    isKPI: true
  },
  {
    id: 'utilization_rate_percentage',
    label: 'Utilization Rate (%)',
    icon: Target,
    type: 'calculated' as FieldType,
    level: 'role_level' as FieldLevel,
    category: 'revenue' as FieldCategory,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50 dark:bg-purple-950/20',
    description: 'Utilization as percentage of available time',
    valueType: 'percentage',
    precision: 1,
    formula: '(invoiced_time ÷ available_consultant_time) × 100',
    dependencies: ['invoiced_time', 'available_consultant_time'],
    applicableRoles: ['Consultant'],
    isEditable: false,
    showInSummary: true,
    aggregateMethod: 'average',
    contributesToRevenue: false,
    isKPI: true
  },
  {
    id: 'average_price_hour',
    label: 'Average Price (hour)',
    icon: DollarSign,
    type: 'input' as FieldType,
    level: 'role_level' as FieldLevel,
    category: 'revenue' as FieldCategory,
    color: 'text-green-600',
    bgColor: 'bg-green-50 dark:bg-green-950/20',
    description: 'Average hourly billing rate',
    valueType: 'currency',
    currencyCode: 'EUR',
    precision: 0,
    min: 0,
    step: 10,
    applicableRoles: ['Consultant'],
    isEditable: true,
    showInSummary: true,
    aggregateMethod: 'average',
    contributesToRevenue: true,
    isKPI: true
  },
  {
    id: 'net_sales',
    label: 'Net Sales',
    icon: DollarSign,
    type: 'calculated' as FieldType,
    level: 'role_level' as FieldLevel,
    category: 'revenue' as FieldCategory,
    color: 'text-green-600',
    bgColor: 'bg-green-50 dark:bg-green-950/20',
    description: 'Calculated net sales (invoiced_time × average_price_hour × fte)',
    valueType: 'currency',
    currencyCode: 'EUR',
    precision: 0,
    formula: 'invoiced_time × average_price_hour × fte',
    dependencies: ['invoiced_time', 'average_price_hour', 'fte'],
    applicableRoles: ['Consultant'],
    isEditable: false,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToRevenue: true,
    isKPI: true
  },
  {
    id: 'total_revenue',
    label: 'Total Revenue',
    icon: DollarSign,
    type: 'calculated' as FieldType,
    level: 'office' as FieldLevel,
    category: 'revenue' as FieldCategory,
    color: 'text-green-600',
    bgColor: 'bg-green-50 dark:bg-green-950/20',
    description: 'Total office revenue from all billable roles',
    formula: 'Sum of net_sales for all billable roles',
    dependencies: ['net_sales'],
    isEditable: false,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToRevenue: true,
    isKPI: true
  },

  // ==========================================
  // WORKFORCE PLANNING FIELDS
  // ==========================================
  {
    id: 'fte',
    label: 'FTE Count',
    icon: Users,
    type: 'input' as FieldType,
    level: 'role_level' as FieldLevel,
    category: 'workforce' as FieldCategory,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 dark:bg-blue-950/20',
    description: 'Full-time equivalent headcount',
    min: 0,
    step: 0.1,
    applicableRoles: ['Consultant', 'Sales', 'Recruitment', 'Operations'], // All roles
    isEditable: true,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToRevenue: false,
    isKPI: true
  },
  {
    id: 'recruitment',
    label: 'Recruitment',
    icon: UserPlus,
    type: 'input' as FieldType,
    level: 'role_level' as FieldLevel,
    category: 'workforce' as FieldCategory,
    color: 'text-green-600',
    bgColor: 'bg-green-50 dark:bg-green-950/20',
    description: 'Number of new hires planned',
    min: 0,
    step: 1,
    applicableRoles: ['Consultant', 'Sales', 'Recruitment', 'Operations'], // All roles
    isEditable: true,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToRevenue: false,
    isKPI: true
  },
  {
    id: 'churn',
    label: 'Churn',
    icon: UserMinus,
    type: 'input' as FieldType,
    level: 'role_level' as FieldLevel,
    category: 'workforce' as FieldCategory,
    color: 'text-red-600',
    bgColor: 'bg-red-50 dark:bg-red-950/20',
    description: 'Number of departures expected',
    min: 0,
    step: 1,
    applicableRoles: ['Consultant', 'Sales', 'Recruitment', 'Operations'], // All roles
    isEditable: true,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToRevenue: false,
    isKPI: true
  },
  {
    id: 'net_headcount_change',
    label: 'Net Headcount Change',
    icon: ArrowUpRight,
    type: 'calculated' as FieldType,
    level: 'role_level' as FieldLevel,
    category: 'workforce' as FieldCategory,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 dark:bg-blue-950/20',
    description: 'Net change in headcount (recruitment - churn)',
    formula: 'recruitment - churn',
    dependencies: ['recruitment', 'churn'],
    applicableRoles: ['Consultant', 'Sales', 'Recruitment', 'Operations'], // All roles
    isEditable: false,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToRevenue: false,
    isKPI: true
  },
  {
    id: 'total_fte',
    label: 'Total FTE',
    icon: Users,
    type: 'calculated' as FieldType,
    level: 'office' as FieldLevel,
    category: 'workforce' as FieldCategory,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 dark:bg-blue-950/20',
    description: 'Total office FTE across all roles',
    formula: 'Sum of fte for all roles',
    dependencies: ['fte'],
    isEditable: false,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToRevenue: false,
    isKPI: true
  },

  // ==========================================
  // COMPENSATION FIELDS
  // ==========================================
  {
    id: 'base_salary',
    label: 'Base Salary (€)',
    icon: DollarSign,
    type: 'input' as FieldType,
    level: 'role_level' as FieldLevel,
    category: 'compensation' as FieldCategory,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50 dark:bg-orange-950/20',
    description: 'Annual base salary',
    min: 0,
    step: 1000,
    applicableRoles: ['Consultant', 'Sales', 'Recruitment', 'Operations'], // All roles
    isEditable: true,
    showInSummary: false,
    aggregateMethod: 'average',
    contributesToCosts: true,
    isKPI: false
  },
  {
    id: 'social_security',
    label: 'Social Security (25%)',
    icon: Calculator,
    type: 'calculated' as FieldType,
    level: 'role_level' as FieldLevel,
    category: 'compensation' as FieldCategory,
    color: 'text-gray-600',
    bgColor: 'bg-gray-50 dark:bg-gray-950/20',
    description: 'Social security contribution (25% of base salary)',
    formula: 'base_salary × 0.25',
    dependencies: ['base_salary'],
    applicableRoles: ['Consultant', 'Sales', 'Recruitment', 'Operations'], // All roles
    isEditable: false,
    showInSummary: false,
    aggregateMethod: 'sum',
    contributesToCosts: true,
    isKPI: false
  },
  {
    id: 'pension',
    label: 'Pension (8%)',
    icon: Calculator,
    type: 'calculated' as FieldType,
    level: 'role_level' as FieldLevel,
    category: 'compensation' as FieldCategory,
    color: 'text-gray-600',
    bgColor: 'bg-gray-50 dark:bg-gray-950/20',
    description: 'Pension contribution (8% of base salary)',
    formula: 'base_salary × 0.08',
    dependencies: ['base_salary'],
    applicableRoles: ['Consultant', 'Sales', 'Recruitment', 'Operations'], // All roles
    isEditable: false,
    showInSummary: false,
    aggregateMethod: 'sum',
    contributesToCosts: true,
    isKPI: false
  },
  {
    id: 'bonus_provision',
    label: 'Bonus Provision',
    icon: DollarSign,
    type: 'input' as FieldType,
    level: 'role_level' as FieldLevel,
    category: 'compensation' as FieldCategory,
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-50 dark:bg-yellow-950/20',
    description: 'Annual bonus provision',
    min: 0,
    step: 500,
    applicableRoles: ['Consultant', 'Sales'], // Primarily for revenue-generating roles
    isEditable: true,
    showInSummary: false,
    aggregateMethod: 'sum',
    contributesToCosts: true,
    isKPI: false
  },
  {
    id: 'total_compensation',
    label: 'Total Compensation',
    icon: Calculator,
    type: 'calculated' as FieldType,
    level: 'role_level' as FieldLevel,
    category: 'compensation' as FieldCategory,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50 dark:bg-orange-950/20',
    description: 'Total annual compensation per person',
    formula: 'base_salary + social_security + pension + bonus_provision',
    dependencies: ['base_salary', 'social_security', 'pension', 'bonus_provision'],
    applicableRoles: ['Consultant', 'Sales', 'Recruitment', 'Operations'], // All roles
    isEditable: false,
    showInSummary: true,
    aggregateMethod: 'average',
    contributesToCosts: true,
    isKPI: false
  },
  {
    id: 'total_people_costs',
    label: 'Total People Costs',
    icon: Users,
    type: 'calculated' as FieldType,
    level: 'role_level' as FieldLevel,
    category: 'compensation' as FieldCategory,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50 dark:bg-orange-950/20',
    description: 'Total annual people costs (compensation × fte)',
    formula: 'total_compensation × fte',
    dependencies: ['total_compensation', 'fte'],
    applicableRoles: ['Consultant', 'Sales', 'Recruitment', 'Operations'], // All roles
    isEditable: false,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToCosts: true,
    isKPI: true
  },

  // ==========================================
  // OPERATING EXPENSES (OFFICE LEVEL)
  // ==========================================
  {
    id: 'office_rent',
    label: 'Office Rent',
    icon: Building2,
    type: 'input' as FieldType,
    level: 'office' as FieldLevel,
    category: 'expenses' as FieldCategory,
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-50 dark:bg-indigo-950/20',
    description: 'Monthly office rent and facilities',
    min: 0,
    step: 100,
    isEditable: true,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToCosts: true,
    isKPI: false
  },
  {
    id: 'travel_expenses',
    label: 'Travel Expenses',
    icon: Users,
    type: 'input' as FieldType,
    level: 'office' as FieldLevel,
    category: 'expenses' as FieldCategory,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 dark:bg-blue-950/20',
    description: 'Monthly travel and transportation costs',
    min: 0,
    step: 100,
    isEditable: true,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToCosts: true,
    isKPI: false
  },
  {
    id: 'it_services',
    label: 'IT Services',
    icon: Users,
    type: 'input' as FieldType,
    level: 'office' as FieldLevel,
    category: 'expenses' as FieldCategory,
    color: 'text-gray-600',
    bgColor: 'bg-gray-50 dark:bg-gray-950/20',
    description: 'IT infrastructure and services',
    min: 0,
    step: 100,
    isEditable: true,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToCosts: true,
    isKPI: false
  },
  {
    id: 'training_education',
    label: 'Training & Education',
    icon: Users,
    type: 'input' as FieldType,
    level: 'office' as FieldLevel,
    category: 'expenses' as FieldCategory,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 dark:bg-blue-950/20',
    description: 'Employee training and development',
    min: 0,
    step: 100,
    isEditable: true,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToCosts: true,
    isKPI: false
  },
  {
    id: 'external_services',
    label: 'External Services',
    icon: Users,
    type: 'input' as FieldType,
    level: 'office' as FieldLevel,
    category: 'expenses' as FieldCategory,
    color: 'text-red-600',
    bgColor: 'bg-red-50 dark:bg-red-950/20',
    description: 'External consultants and services',
    min: 0,
    step: 100,
    isEditable: true,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToCosts: true,
    isKPI: false
  },

  // ==========================================
  // ADDITIONAL EXPENSE FIELDS
  // ==========================================
  {
    id: 'client_loss',
    label: 'Client Loss',
    icon: DollarSign,
    type: 'input' as FieldType,
    level: 'office' as FieldLevel,
    category: 'expenses' as FieldCategory,
    color: 'text-red-600',
    bgColor: 'bg-red-50 dark:bg-red-950/20',
    description: 'Client loss and write-offs',
    valueType: 'currency',
    currencyCode: 'EUR',
    precision: 0,
    min: 0,
    step: 1000,
    isEditable: true,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToCosts: true,
    isKPI: false
  },
  {
    id: 'education',
    label: 'Education',
    icon: Users,
    type: 'input' as FieldType,
    level: 'office' as FieldLevel,
    category: 'expenses' as FieldCategory,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 dark:bg-blue-950/20',
    description: 'Education and professional development',
    valueType: 'currency',
    currencyCode: 'EUR',
    precision: 0,
    min: 0,
    step: 500,
    isEditable: true,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToCosts: true,
    isKPI: false
  },
  {
    id: 'external_representation',
    label: 'External Representation',
    icon: Building2,
    type: 'input' as FieldType,
    level: 'office' as FieldLevel,
    category: 'expenses' as FieldCategory,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50 dark:bg-purple-950/20',
    description: 'External representation and client entertainment',
    valueType: 'currency',
    currencyCode: 'EUR',
    precision: 0,
    min: 0,
    step: 500,
    isEditable: true,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToCosts: true,
    isKPI: false
  },
  {
    id: 'internal_representation',
    label: 'Internal Representation',
    icon: Users,
    type: 'input' as FieldType,
    level: 'office' as FieldLevel,
    category: 'expenses' as FieldCategory,
    color: 'text-green-600',
    bgColor: 'bg-green-50 dark:bg-green-950/20',
    description: 'Internal events and employee representation',
    valueType: 'currency',
    currencyCode: 'EUR',
    precision: 0,
    min: 0,
    step: 500,
    isEditable: true,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToCosts: true,
    isKPI: false
  },
  {
    id: 'it_related_staff',
    label: 'IT Related (Staff)',
    icon: Calculator,
    type: 'input' as FieldType,
    level: 'office' as FieldLevel,
    category: 'expenses' as FieldCategory,
    color: 'text-gray-600',
    bgColor: 'bg-gray-50 dark:bg-gray-950/20',
    description: 'IT-related staff costs and equipment',
    valueType: 'currency',
    currencyCode: 'EUR',
    precision: 0,
    min: 0,
    step: 1000,
    isEditable: true,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToCosts: true,
    isKPI: false
  },
  {
    id: 'office_related',
    label: 'Office Related',
    icon: Building2,
    type: 'input' as FieldType,
    level: 'office' as FieldLevel,
    category: 'expenses' as FieldCategory,
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-50 dark:bg-indigo-950/20',
    description: 'Office supplies and miscellaneous office expenses',
    valueType: 'currency',
    currencyCode: 'EUR',
    precision: 0,
    min: 0,
    step: 500,
    isEditable: true,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToCosts: true,
    isKPI: false
  },
  {
    id: 'variable_salary',
    label: 'Variable Salary',
    icon: DollarSign,
    type: 'input' as FieldType,
    level: 'role_level' as FieldLevel,
    category: 'expenses' as FieldCategory,
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-50 dark:bg-yellow-950/20',
    description: 'Variable salary and performance bonuses',
    valueType: 'currency',
    currencyCode: 'EUR',
    precision: 0,
    min: 0,
    step: 1000,
    applicableRoles: ['Consultant', 'Sales', 'Recruitment', 'Operations'],
    isEditable: true,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToCosts: true,
    isKPI: false
  },
  {
    id: 'other_expenses',
    label: 'Other',
    icon: Calculator,
    type: 'input' as FieldType,
    level: 'office' as FieldLevel,
    category: 'expenses' as FieldCategory,
    color: 'text-gray-600',
    bgColor: 'bg-gray-50 dark:bg-gray-950/20',
    description: 'Other miscellaneous expenses',
    valueType: 'currency',
    currencyCode: 'EUR',
    precision: 0,
    min: 0,
    step: 500,
    isEditable: true,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToCosts: true,
    isKPI: false
  },
  {
    id: 'total_operating_expenses',
    label: 'Total Operating Expenses',
    icon: Calculator,
    type: 'calculated' as FieldType,
    level: 'office' as FieldLevel,
    category: 'expenses' as FieldCategory,
    color: 'text-red-600',
    bgColor: 'bg-red-50 dark:bg-red-950/20',
    description: 'Sum of all operating expenses',
    formula: 'office_rent + travel_expenses + it_services + training_education + external_services + client_loss + education + external_representation + internal_representation + it_related_staff + office_related + other_expenses',
    dependencies: ['office_rent', 'travel_expenses', 'it_services', 'training_education', 'external_services', 'client_loss', 'education', 'external_representation', 'internal_representation', 'it_related_staff', 'office_related', 'other_expenses'],
    isEditable: false,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToCosts: true,
    isKPI: true
  },

  // ==========================================
  // SUMMARY & KPI FIELDS
  // ==========================================
  {
    id: 'total_costs',
    label: 'Total Costs',
    icon: Calculator,
    type: 'calculated' as FieldType,
    level: 'office' as FieldLevel,
    category: 'summary' as FieldCategory,
    color: 'text-red-600',
    bgColor: 'bg-red-50 dark:bg-red-950/20',
    description: 'Total costs (people + operating expenses)',
    formula: 'Sum(total_people_costs) + total_operating_expenses',
    dependencies: ['total_people_costs', 'total_operating_expenses'],
    isEditable: false,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToCosts: true,
    isKPI: true
  },
  {
    id: 'ebitda',
    label: 'EBITDA',
    icon: TrendingUp,
    type: 'calculated' as FieldType,
    level: 'office' as FieldLevel,
    category: 'summary' as FieldCategory,
    color: 'text-green-600',
    bgColor: 'bg-green-50 dark:bg-green-950/20',
    description: 'Earnings before interest, taxes, depreciation, and amortization',
    formula: 'total_revenue - total_costs',
    dependencies: ['total_revenue', 'total_costs'],
    isEditable: false,
    showInSummary: true,
    aggregateMethod: 'sum',
    contributesToRevenue: false,
    isKPI: true
  },
  {
    id: 'ebitda_margin',
    label: 'EBITDA Margin %',
    icon: Target,
    type: 'calculated' as FieldType,
    level: 'office' as FieldLevel,
    category: 'summary' as FieldCategory,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50 dark:bg-purple-950/20',
    description: 'EBITDA as percentage of revenue',
    formula: '(ebitda ÷ total_revenue) × 100',
    dependencies: ['ebitda', 'total_revenue'],
    isEditable: false,
    showInSummary: true,
    aggregateMethod: 'average',
    contributesToRevenue: false,
    isKPI: true
  },
  {
    id: 'revenue_per_fte',
    label: 'Revenue per FTE',
    icon: Target,
    type: 'calculated' as FieldType,
    level: 'office' as FieldLevel,
    category: 'summary' as FieldCategory,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 dark:bg-blue-950/20',
    description: 'Annual revenue per full-time equivalent',
    formula: 'total_revenue ÷ total_fte',
    dependencies: ['total_revenue', 'total_fte'],
    isEditable: false,
    showInSummary: true,
    aggregateMethod: 'average',
    contributesToRevenue: false,
    isKPI: true
  }
];

// ==========================================
// HIERARCHICAL SECTIONS CONFIGURATION
// ==========================================

const BUSINESS_PLANNING_SECTIONS: BusinessPlanningSection[] = [
  {
    id: 'sales',
    name: 'Sales',
    description: 'Pricing, utilization, and sales projections',
    icon: DollarSign,
    color: 'text-green-600',
    order: 1,
    aggregatesToOfficeLevel: true,
    summaryFields: ['total_revenue', 'revenue_per_fte'],
    subsections: [
      {
        id: 'pricing_strategy',
        name: 'Pricing Strategy',
        description: 'Hourly rates and pricing structure',
        order: 1,
        fields: ['average_price_hour', 'utr'],
        roleOrganization: 'specific',
        specificRoles: ['Consultant'], // Only billable roles
        levelOrganization: 'all',
        isCollapsible: true,
        defaultExpanded: true,
        showRoleSummaries: true
      },
      {
        id: 'time_calculation',
        name: 'Time Calculation',
        description: 'Detailed time breakdown and availability',
        order: 2,
        fields: ['consultant_time', 'planned_absence', 'unplanned_absence', 'vacation_withdrawal', 'vacation', 'available_consultant_time', 'invoiced_time', 'utilization_rate_percentage'],
        roleOrganization: 'specific',
        specificRoles: ['Consultant'],
        levelOrganization: 'all',
        isCollapsible: true,
        defaultExpanded: true,
        showRoleSummaries: true
      },
      {
        id: 'revenue_calculation',
        name: 'Revenue Calculation',
        description: 'Calculated revenue from billable activities',
        order: 3,
        fields: ['net_sales'],
        roleOrganization: 'specific',
        specificRoles: ['Consultant'],
        levelOrganization: 'all',
        isCollapsible: true,
        defaultExpanded: true,
        showRoleSummaries: true
      },
      {
        id: 'sales_summary',
        name: 'Sales Summary',
        description: 'Office-level sales aggregation',
        order: 3,
        fields: ['total_revenue', 'revenue_per_fte'],
        roleOrganization: 'all',
        levelOrganization: 'all',
        isCollapsible: false,
        defaultExpanded: true,
        showRoleSummaries: false
      }
    ]
  },
  {
    id: 'workforce_planning',
    name: 'Workforce Planning',
    description: 'Headcount, hiring, and workforce changes',
    icon: Users,
    color: 'text-blue-600',
    order: 2,
    aggregatesToOfficeLevel: true,
    summaryFields: ['total_fte', 'net_headcount_change'],
    subsections: [
      {
        id: 'headcount_planning',
        name: 'Current Headcount',
        description: 'Current FTE by role and level',
        order: 1,
        fields: ['fte'],
        roleOrganization: 'all',
        levelOrganization: 'all',
        isCollapsible: true,
        defaultExpanded: true,
        showRoleSummaries: true
      },
      {
        id: 'hiring_planning',
        name: 'Hiring & Departures',
        description: 'Planned starters and leavers',
        order: 2,
        fields: ['recruitment', 'churn', 'net_headcount_change'],
        roleOrganization: 'all',
        levelOrganization: 'all',
        isCollapsible: true,
        defaultExpanded: true,
        showRoleSummaries: true
      },
      {
        id: 'workforce_summary',
        name: 'Workforce Summary',
        description: 'Office-level workforce metrics',
        order: 3,
        fields: ['total_fte'],
        roleOrganization: 'all',
        levelOrganization: 'all',
        isCollapsible: false,
        defaultExpanded: true,
        showRoleSummaries: false
      }
    ]
  },
  {
    id: 'operating_expenses',
    name: 'Operating Expenses',
    description: 'All operational costs including compensation',
    icon: Building2,
    color: 'text-indigo-600',
    order: 3,
    aggregatesToOfficeLevel: true,
    summaryFields: ['total_people_costs', 'total_operating_expenses'],
    subsections: [
      {
        id: 'compensation',
        name: 'Salaries & Related',
        description: 'Base salaries, social security, pension, and variable compensation',
        order: 1,
        fields: ['base_salary', 'variable_salary', 'social_security', 'pension', 'total_compensation', 'total_people_costs'],
        roleOrganization: 'all',
        levelOrganization: 'all',
        isCollapsible: true,
        defaultExpanded: true,
        showRoleSummaries: true
      },
      {
        id: 'facilities_costs',
        name: 'Office & Facilities',
        description: 'Office rent and facility-related expenses',
        order: 2,
        fields: ['office_rent', 'office_related'],
        roleOrganization: 'all',
        levelOrganization: 'all',
        isCollapsible: true,
        defaultExpanded: true,
        showRoleSummaries: false
      },
      {
        id: 'professional_services',
        name: 'Professional Services',
        description: 'External services and professional development',
        order: 3,
        fields: ['external_services', 'education', 'it_related_staff'],
        roleOrganization: 'all',
        levelOrganization: 'all',
        isCollapsible: true,
        defaultExpanded: true,
        showRoleSummaries: false
      },
      {
        id: 'representation_costs',
        name: 'Representation & Events',
        description: 'External and internal representation expenses',
        order: 4,
        fields: ['external_representation', 'internal_representation'],
        roleOrganization: 'all',
        levelOrganization: 'all',
        isCollapsible: true,
        defaultExpanded: true,
        showRoleSummaries: false
      },
      {
        id: 'operational_costs',
        name: 'Other Operating Expenses',
        description: 'Travel, IT services, client losses and other expenses',
        order: 5,
        fields: ['travel_expenses', 'it_services', 'training_education', 'client_loss', 'other_expenses'],
        roleOrganization: 'all',
        levelOrganization: 'all',
        isCollapsible: true,
        defaultExpanded: true,
        showRoleSummaries: false
      },
      {
        id: 'expense_summary',
        name: 'Expense Summary',
        description: 'Total operating expense aggregation',
        order: 6,
        fields: ['total_operating_expenses'],
        roleOrganization: 'all',
        levelOrganization: 'all',
        isCollapsible: false,
        defaultExpanded: true,
        showRoleSummaries: false
      }
    ]
  },
  {
    id: 'financial_summary',
    name: 'Financial Summary & KPIs',
    description: 'Profitability metrics and key performance indicators',
    icon: BarChart3,
    color: 'text-purple-600',
    order: 4,
    aggregatesToOfficeLevel: true,
    summaryFields: ['ebitda', 'ebitda_margin', 'revenue_per_fte'],
    subsections: [
      {
        id: 'profitability',
        name: 'Profitability Analysis',
        description: 'Revenue, costs, and profit calculations',
        order: 1,
        fields: ['total_costs', 'ebitda', 'ebitda_margin'],
        roleOrganization: 'all',
        levelOrganization: 'all',
        isCollapsible: false,
        defaultExpanded: true,
        showRoleSummaries: false
      },
      {
        id: 'efficiency_metrics',
        name: 'Efficiency Metrics',
        description: 'Per-FTE and productivity metrics',
        order: 2,
        fields: ['revenue_per_fte'],
        roleOrganization: 'all',
        levelOrganization: 'all',
        isCollapsible: false,
        defaultExpanded: true,
        showRoleSummaries: false
      }
    ]
  }
];

// ==========================================
// REGISTRY INITIALIZATION
// ==========================================

export function createBusinessPlanningRegistry(): BusinessPlanningFieldRegistry {
  const registry = new BusinessPlanningFieldRegistry();
  
  // Register all fields
  FIELD_DEFINITIONS.forEach(fieldDef => {
    const field = new BusinessPlanningFieldImpl(fieldDef);
    registry.registerField(field);
  });
  
  // Register all sections
  BUSINESS_PLANNING_SECTIONS.forEach(section => {
    registry.registerSection(section);
  });
  
  return registry;
}

// Create and export the singleton registry instance
export const businessPlanningRegistry = createBusinessPlanningRegistry();

// Export field and section definitions for reference
export { FIELD_DEFINITIONS, BUSINESS_PLANNING_SECTIONS };

// ==========================================
// CONVENIENCE FUNCTIONS
// ==========================================

export function getFieldsForRole(role: StandardRole) {
  return businessPlanningRegistry.getApplicableFieldsForRole(role);
}

export function getFieldsByCategory(category: FieldCategory) {
  return businessPlanningRegistry.getFieldsByCategory(category);
}

export function getSectionsHierarchy() {
  return businessPlanningRegistry.getSections();
}

export function validateRoleFieldCombination(fieldId: string, role: StandardRole): boolean {
  return businessPlanningRegistry.validateFieldForRole(fieldId, role);
}

// ==========================================
// ROLE-SPECIFIC CONFIGURATION HELPERS
// ==========================================

export const ROLE_CONFIGURATIONS = {
  Consultant: {
    hasLevels: true,
    isBillable: true,
    applicableFields: ['price', 'utr', 'monthly_hours', 'absence', 'billable_hours', 'fte', 'recruitment', 'churn', 'base_salary', 'bonus_provision'],
    primaryKPIs: ['net_sales', 'utr', 'net_headcount_change'],
    description: 'Revenue-generating consultants with hourly billing'
  },
  Sales: {
    hasLevels: true,
    isBillable: false,
    applicableFields: ['fte', 'recruitment', 'churn', 'base_salary', 'bonus_provision'],
    primaryKPIs: ['net_headcount_change'],
    description: 'Sales professionals with some performance incentives'
  },
  Recruitment: {
    hasLevels: true,
    isBillable: false,
    applicableFields: ['fte', 'recruitment', 'churn', 'base_salary'],
    primaryKPIs: ['net_headcount_change'],
    description: 'Recruitment specialists with standard compensation'
  },
  Operations: {
    hasLevels: false, // Flat role
    isBillable: false,
    applicableFields: ['fte', 'recruitment', 'churn', 'base_salary'],
    primaryKPIs: ['net_headcount_change'],
    description: 'Operations support with flat organizational structure'
  }
} as const;