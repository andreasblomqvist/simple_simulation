/**
 * Unified Data Structure Types for SimpleSim Frontend
 * 
 * This file defines TypeScript interfaces that match the documented
 * data structures and backend unified models exactly.
 * 
 * Based on docs/SIMULATION_DATA_STRUCTURES.md
 */

// Basic types
export type YearMonth = string; // Format: "YYYYMM" (e.g., "202501")
export type OfficeScope = string[] | ["Group"];
export type ScenarioId = string;
export type OfficeName = string;
export type LevelType = 'A' | 'AC' | 'C' | 'SrC' | 'AM' | 'M' | 'SrM' | 'PiP';
export type LeverType = 'recruitment' | 'churn' | 'progression';
export type ComparisonType = 'side_by_side' | 'overlay' | 'difference';

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
  recruitment: MonthlyValues;
  churn: MonthlyValues;
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
  baseline_input: BaselineInput;
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
}

// Complete simulation results
export interface SimulationResults {
  years: {
    [yearString: string]: YearResults;
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

export interface ValidationReport {
  timestamp: string;
  overall_status: 'valid' | 'valid_with_warnings' | 'invalid';
  scenario_validation: {
    is_valid: boolean;
    errors: string[];
  };
  baseline_input_validation: {
    is_valid: boolean;
    errors: string[];
  };
  field_name_validation: {
    issues_found: number;
    issues: string[];
  };
  summary: {
    total_errors: number;
    total_warnings: number;
    critical_issues: string[];
    recommendations: string[];
  };
}

// Utility Types for Frontend Components

// For BaselineInputGrid component
export interface BaselineInputData {
  recruitment: {
    [roleName: string]: {
      [levelName: string]: MonthlyValues;
    };
  };
  churn: {
    [roleName: string]: {
      [levelName: string]: MonthlyValues;
    };
  };
}

// For form handling
export interface ScenarioFormData {
  name: string;
  description: string;
  time_range: TimeRange;
  office_scope: OfficeScope;
  levers: Levers;
  economic_params: EconomicParameters;
  baseline_input: BaselineInputData;
}

// Migration utilities
export interface LegacyScenarioData {
  // Old structure with inconsistent field names
  [key: string]: any;
}

// Month key utilities matching backend validation
export const MONTH_KEY_REGEX = /^\d{4}(0[1-9]|1[0-2])$/;

export function isValidMonthKey(key: string): boolean {
  return MONTH_KEY_REGEX.test(key);
}

export function parseMonthKey(key: YearMonth): { year: number; month: number } {
  if (!isValidMonthKey(key)) {
    throw new Error(`Invalid month key format: ${key}. Expected YYYYMM format.`);
  }
  return {
    year: parseInt(key.substring(0, 4)),
    month: parseInt(key.substring(4, 6))
  };
}

export function formatMonthKey(year: number, month: number): YearMonth {
  if (year < 2020 || year > 2040) {
    throw new Error(`Year must be between 2020 and 2040: ${year}`);
  }
  if (month < 1 || month > 12) {
    throw new Error(`Month must be between 1 and 12: ${month}`);
  }
  return `${year}${month.toString().padStart(2, '0')}`;
}

export function generateMonthKeys(
  startYear: number, 
  startMonth: number, 
  endYear: number, 
  endMonth: number
): YearMonth[] {
  const months: YearMonth[] = [];
  let currentYear = startYear;
  let currentMonth = startMonth;
  
  while (currentYear < endYear || (currentYear === endYear && currentMonth <= endMonth)) {
    months.push(formatMonthKey(currentYear, currentMonth));
    
    currentMonth++;
    if (currentMonth > 12) {
      currentMonth = 1;
      currentYear++;
    }
  }
  
  return months;
}

// Helper functions for data transformation
export interface DataTransformationUtils {
  convertLegacyToUnified: (legacy: LegacyScenarioData) => ScenarioDefinition;
  validateScenarioData: (data: any) => ValidationReport;
}

// Role and level constants matching backend
export const ROLE_LEVELS: Record<string, LevelType[]> = {
  Consultant: ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP'],
  Sales: ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP'],
  Recruitment: ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP'],
} as const;

export const ROLES = Object.keys(ROLE_LEVELS);
export const DEFAULT_ROLE = 'Consultant' as const;

// Constants for validation
export const VALIDATION_CONSTANTS = {
  MIN_YEAR: 2020,
  MAX_YEAR: 2040,
  MIN_MONTH: 1,
  MAX_MONTH: 12,
  MONTH_KEY_REGEX: /^\d{4}(0[1-9]|1[0-2])$/,
  REQUIRED_BASELINE_SECTIONS: ['recruitment', 'churn'],
  KNOWN_LEVER_TYPES: ['recruitment', 'churn', 'progression'],
  DEPRECATED_FIELDS: ['total', 'progression_rate', 'Price_1', 'Price_2'],
} as const;

// Legacy Office type for backwards compatibility
export interface Office {
  name: string;
  total_fte: number;
  levels: Record<string, Level>;
  operations: {
    total: number;
    price: number;
    salary: number;
    recruitment_h1: number;
    recruitment_h2: number;
    churn_h1: number;
    churn_h2: number;
    growth_h1: number;
    growth_h2: number;
  };
}

export interface Level {
  total: number;
  price: number;
  salary: number;
  recruitment_h1: number;
  recruitment_h2: number;
  churn_h1: number;
  churn_h2: number;
  growth_h1: number;
  growth_h2: number;
}

// Missing comparison types for API compatibility
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