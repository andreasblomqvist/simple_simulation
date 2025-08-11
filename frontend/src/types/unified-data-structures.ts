/**
 * Unified Data Structure Types for SimpleSim Frontend
 * 
 * This file defines TypeScript interfaces that match the documented
 * data structures and backend unified models exactly.
 * 
 * Based on cursor_rules/SIMULATION_DATA_STRUCTURES.md
 */

// Basic types
export type YearMonth = string; // Format: "YYYYMM" (e.g., "202501")
export type OfficeScope = string[] | ["Group"];
export type ScenarioId = string;
export type OfficeName = string;
export type LevelType = 'A' | 'AC' | 'C' | 'SrC' | 'AM' | 'M' | 'SrM' | 'PiP';
export type LeverType = 'recruitment' | 'churn' | 'progression';
export type ComparisonType = 'side_by_side' | 'overlay' | 'difference';

// Role constants
export const ROLES = ['Consultant', 'Sales', 'Recruitment', 'Operations'] as const;
export const ROLES_WITH_LEVELS = ['Consultant', 'Sales', 'Recruitment'] as const;
export const DEFAULT_ROLE = 'Consultant';

// Role levels mapping
export const ROLE_LEVELS = {
  Consultant: ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP'],
  Sales: ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP'],
  Recruitment: ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP'],
  Operations: ['N/A'], // Operations is a flat role without levels
} as const;

// Utility function to generate month keys in YYYYMM format
export function generateMonthKeys(startYear: number, startMonth: number, endYear: number, endMonth: number): string[] {
  const months: string[] = [];
  let currentYear = startYear;
  let currentMonth = startMonth;
  
  while (currentYear < endYear || (currentYear === endYear && currentMonth <= endMonth)) {
    const monthKey = `${currentYear}${currentMonth.toString().padStart(2, '0')}`;
    months.push(monthKey);
    
    currentMonth++;
    if (currentMonth > 12) {
      currentMonth = 1;
      currentYear++;
    }
  }
  
  return months;
}

// Time range interface
export interface TimeRange {
  start_year: number;
  start_month: number; // 1-12
  end_year: number;
  end_month: number; // 1-12
}

// Economic parameters
export interface EconomicParameters {
  working_hours_per_month: number; // Default: 160.0
  employment_cost_rate: number; // Default: 0.3 (0-1)
  unplanned_absence: number; // Default: 0.05 (0-1)
  other_expense: number; // Default: 1000000.0
}

// Default values matching backend exactly
export const DEFAULT_ECONOMIC_PARAMETERS: EconomicParameters = {
  working_hours_per_month: 160.0,
  employment_cost_rate: 0.3,
  unplanned_absence: 0.05,
  other_expense: 1000000.0,
};

// Monthly values using YYYYMM format
export interface MonthlyValues {
  [monthKey: string]: number; // Key format: "YYYYMM"
}

// Level data for recruitment/churn
export interface LevelData {
  recruitment: { values: MonthlyValues };
  churn: { values: MonthlyValues };
}

// Role data - can be leveled (with levels) or flat (direct monthly values)
export interface LeveledRoleData {
  levels: {
    [levelName: string]: LevelData;
  };
}

export interface FlatRoleData {
  recruitment: MonthlyValues;
  churn: MonthlyValues;
}

export type RoleData = LeveledRoleData | FlatRoleData;

// Type guard to check if role data is leveled
export function isLeveledRoleData(roleData: RoleData): roleData is LeveledRoleData {
  return 'levels' in roleData;
}

// Baseline input structure
export interface BaselineInput {
  global: {
    recruitment: {
      [roleName: string]: RoleData;
    };
    churn: {
      [roleName: string]: RoleData;
    };
  };
}

// Lever multipliers
export interface Levers {
  recruitment: { [levelName: string]: number };
  churn: { [levelName: string]: number };
  progression: { [levelName: string]: number };
}

// Progression configuration
export interface ProgressionLevelConfig {
  progression_months: number[]; // Months 1-12 when progression can occur
  start_tenure: number; // Starting tenure in months
  time_on_level: number; // Minimum time on level in months
  next_level?: string; // Next level in progression path
  journey: string; // Journey identifier (e.g., "J-1")
}

export interface ProgressionConfig {
  [levelName: string]: ProgressionLevelConfig;
}

// CAT curves configuration
export interface CATCurveLevel {
  [catKey: string]: number; // e.g., "CAT0": 0.0, "CAT6": 0.919
}

export interface CATCurves {
  [levelName: string]: CATCurveLevel;
}

// Complete scenario definition
export interface ScenarioDefinition {
  id?: string;
  name: string;
  description: string;
  time_range: TimeRange;
  office_scope: OfficeScope;
  levers: Levers;
  economic_params: EconomicParameters;
  progression_config?: ProgressionConfig;
  cat_curves?: CATCurves;
  baseline_input?: BaselineInput;
  business_plan_id?: string; // ID of business plan to use as baseline
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
}

// Simulation Results Structure (Output)

// Monthly result data
export interface MonthlyResult {
  fte: number; // Standardized field name (not "total")
  price: number;
  salary: number;
  recruitment: number;
  churn: number;
  progression?: number;
}

// Results for a single level - array of 12 monthly results
export interface LevelResults {
  months: MonthlyResult[]; // Exactly 12 months (0-indexed)
}

// Results for a role - either leveled (dict) or flat (list)
export interface LeveledRoleResults {
  levels: {
    [levelName: string]: LevelResults;
  };
}

export interface FlatRoleResults {
  months: MonthlyResult[]; // Exactly 12 months (0-indexed)
}

export type RoleResults = LeveledRoleResults | FlatRoleResults;

// Type guard for role results
export function isLeveledRoleResults(roleResults: RoleResults): roleResults is LeveledRoleResults {
  return 'levels' in roleResults;
}

// Results for a single office
export interface OfficeResults {
  roles: {
    [roleName: string]: RoleResults;
  };
}

// Results for a single year
export interface YearResults {
  offices: {
    [officeName: string]: OfficeResults;
  };
  kpis?: {
    year: string;
    financial: {
      net_sales: number;
      net_sales_baseline: number;
      total_salary_costs: number;
      total_salary_costs_baseline: number;
      ebitda: number;
      ebitda_baseline: number;
      margin: number;
      margin_baseline: number;
      total_consultants: number;
      total_consultants_baseline: number;
      avg_hourly_rate: number;
      avg_hourly_rate_baseline: number;
      avg_utr: number;
    };
    growth: {
      total_growth_percent: number;
      total_growth_absolute: number;
      current_total_fte: number;
      baseline_total_fte: number;
      non_debit_ratio: number;
      non_debit_ratio_baseline: number;
      non_debit_delta: number;
    };
    journeys: {
      journey_totals: Record<string, number>;
      journey_percentages: Record<string, number>;
      journey_deltas: Record<string, number>;
      journey_totals_baseline: Record<string, number>;
      journey_percentages_baseline: Record<string, number>;
    };
    year_over_year_growth: number;
    year_over_year_margin_change: number;
  };
}

// Complete simulation results
export interface SimulationResults {
  years: {
    [yearString: string]: YearResults;
  };
}

// Office configuration interface
export interface Office {
  name: string;
  total_fte: number;
  journey: string;
  roles: {
    [roleName: string]: RoleData;
  };
}

// API Request/Response Types

export interface ScenarioRequest {
  scenario_id?: string;
  scenario_definition?: ScenarioDefinition;
  office_scope?: OfficeScope;
}

export interface ScenarioResponse {
  scenario_id: string;
  scenario_name: string;
  execution_time: number;
  results: SimulationResults;
  status: 'success' | 'error';
  error_message?: string;
}

export interface ScenarioListItem {
  id: ScenarioId;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
  time_range: TimeRange;
  office_scope: OfficeScope;
  business_plan_id?: string;
}

export interface ScenarioListResponse {
  scenarios: ScenarioListItem[];
  total_count: number;
}

// Error handling types
export interface ErrorResponse {
  detail: string;
  correlation_id?: string;
  error_type?: string;
  context?: Record<string, any>;
}

// API Response wrapper
export interface ApiResponse<T> {
  data: T;
  correlation_id?: string;
  metadata?: {
    processing_time?: number;
    warnings?: string[];
  };
}

// Validation Types

export interface ValidationResponse {
  valid: boolean;
  errors: string[];
  warnings?: string[];
  correlation_id?: string;
}

export interface ValidationError {
  field: string;
  message: string;
  value?: any;
}

// Scenario comparison types
export interface ScenarioComparisonRequest {
  scenario_ids: ScenarioId[];
  comparison_type: ComparisonType;
  include_monthly_data?: boolean;
}

export interface ScenarioComparisonResponse {
  comparison_id: string;
  scenarios: Record<ScenarioId, ScenarioResponse>;
  comparison_data: any;
  metadata: any;
}