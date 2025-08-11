/**
 * TypeScript types for office management system
 * Mirrors the Pydantic models from the backend
 */

export enum OfficeJourney {
  EMERGING = 'emerging',
  ESTABLISHED = 'established',
  MATURE = 'mature'
}

export enum ProgressionCurve {
  LINEAR = 'linear',
  EXPONENTIAL = 'exponential',
  CUSTOM = 'custom'
}

export interface EconomicParameters {
  cost_of_living: number;
  market_multiplier: number;
  tax_rate: number;
}

export interface CATMatrix {
  [level: string]: {
    [catStage: string]: number; // CAT0, CAT6, CAT12, etc. -> probability (0.0 to 1.0)
  };
}

export interface PopulationSnapshot {
  id: string;
  name: string;
  snapshot_date: string;
  description?: string;
  total_fte: number;
  created_at: string;
  is_default: boolean;
}

export interface BusinessPlan {
  id: string;
  name: string;
  plan_date: string;
  description?: string;
  created_at: string;
  is_active: boolean;
}

export interface OfficeConfig {
  id: string;
  name: string;
  journey: OfficeJourney;
  timezone: string;
  economic_parameters: EconomicParameters;
  cat_matrix?: CATMatrix;
  snapshots: PopulationSnapshot[];
  business_plans: BusinessPlan[];
  current_snapshot_id?: string;
  active_business_plan_id?: string;
  created_at?: string;
  updated_at?: string;
  // Frontend computed property for convenience (extracted from snapshots[0].total_fte)
  total_fte?: number;
}

export interface WorkforceEntry {
  role: string;
  level: string;
  fte: number;
  notes?: string;
}

export interface WorkforceDistribution {
  id: string;
  office_id: string;
  start_date: string;
  workforce: WorkforceEntry[];
  created_at?: string;
  updated_at?: string;
}

export interface MonthlyPlanEntry {
  role: string;
  level: string;
  recruitment: number;
  churn: number;
  price: number;
  utr: number;
  salary: number;
}

export interface MonthlyBusinessPlan {
  id: string;
  office_id: string;
  year: number;
  month: number;
  entries: MonthlyPlanEntry[];
  created_at?: string;
  updated_at?: string;
}

export interface ProgressionPoint {
  month: number;
  rate: number;
}

export interface ProgressionConfig {
  id: string;
  office_id: string;
  level: string;
  monthly_rate: number;
  curve_type: ProgressionCurve;
  custom_points: ProgressionPoint[];
  created_at?: string;
  updated_at?: string;
}

export interface OfficeBusinessPlanSummary {
  office: OfficeConfig;
  workforce_distribution?: WorkforceDistribution;
  monthly_plans: MonthlyBusinessPlan[];
  progression_configs: ProgressionConfig[];
}

// Standard roles and levels for the system
export const STANDARD_ROLES = ['Consultant', 'Sales', 'Recruitment', 'Operations'] as const;
export const STANDARD_LEVELS = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP'] as const;

// Roles that have hierarchical levels
export const LEVELED_ROLES = ['Consultant', 'Sales', 'Recruitment'] as const;

// Roles that are flat (no levels)
export const FLAT_ROLES = ['Operations'] as const;

// Roles that have price/UTR (billable)
export const BILLABLE_ROLES = ['Consultant'] as const;

// Roles that only have recruitment/churn/salary (no price/UTR)
export const NON_BILLABLE_ROLES = ['Sales', 'Recruitment', 'Operations'] as const;

export type StandardRole = typeof STANDARD_ROLES[number];
export type StandardLevel = typeof STANDARD_LEVELS[number];
export type LeveledRole = typeof LEVELED_ROLES[number];
export type FlatRole = typeof FLAT_ROLES[number];
export type BillableRole = typeof BILLABLE_ROLES[number];
export type NonBillableRole = typeof NON_BILLABLE_ROLES[number];

// UI-specific types
export interface OfficeFormData {
  name: string;
  journey: OfficeJourney;
  timezone: string;
  economic_parameters: EconomicParameters;
}

export interface BusinessPlanTableCell {
  role: string;
  level: string;
  month: number;
  year: number;
  recruitment: number;
  churn: number;
  price: number;
  utr: number;
  salary: number;
}

export interface ValidationResult {
  errors: string[];
  warnings: string[];
  info: string[];
}

// API response types
export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

// Error types
export class OfficeAPIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string
  ) {
    super(message);
    this.name = 'OfficeAPIError';
  }
}

// Utility types for form handling
export type CreateOfficeRequest = Omit<OfficeConfig, 'id' | 'created_at' | 'updated_at'>;
export type UpdateOfficeRequest = Partial<Omit<OfficeConfig, 'id' | 'created_at' | 'updated_at'>>;

export type CreateBusinessPlanRequest = Omit<MonthlyBusinessPlan, 'id' | 'created_at' | 'updated_at'>;
export type UpdateBusinessPlanRequest = Partial<Omit<MonthlyBusinessPlan, 'id' | 'created_at' | 'updated_at'>>;

export type CreateWorkforceRequest = Omit<WorkforceDistribution, 'id' | 'created_at' | 'updated_at'>;
export type UpdateWorkforceRequest = Partial<Omit<WorkforceDistribution, 'id' | 'created_at' | 'updated_at'>>;

// Business calculation helpers
export interface MonthlyCalculations {
  total_recruitment: number;
  total_churn: number;
  net_change: number;
  revenue_potential: number;
  salary_cost: number;
  profit_margin: number;
}

export interface AnnualSummary {
  year: number;
  total_recruitment: number;
  total_churn: number;
  net_change: number;
  months_planned: number;
  average_monthly_revenue: number;
  average_monthly_cost: number;
}

// Journey-specific configuration
export interface JourneyConfig {
  journey: OfficeJourney;
  typical_size_range: [number, number]; // [min_fte, max_fte]
  common_roles: StandardRole[];
  growth_expectations: {
    recruitment_rate: number;
    churn_rate: number;
  };
  maturity_indicators: string[];
}

export const JOURNEY_CONFIGS: Record<OfficeJourney, JourneyConfig> = {
  [OfficeJourney.EMERGING]: {
    journey: OfficeJourney.EMERGING,
    typical_size_range: [5, 25],
    common_roles: ['Consultant'],
    growth_expectations: {
      recruitment_rate: 0.15, // 15% monthly growth
      churn_rate: 0.08, // 8% monthly churn
    },
    maturity_indicators: [
      'Rapid hiring',
      'High growth rate',
      'Limited role diversity',
      'Establishing processes'
    ]
  },
  [OfficeJourney.ESTABLISHED]: {
    journey: OfficeJourney.ESTABLISHED,
    typical_size_range: [25, 75],
    common_roles: ['Consultant', 'Sales'],
    growth_expectations: {
      recruitment_rate: 0.08, // 8% monthly growth
      churn_rate: 0.05, // 5% monthly churn
    },
    maturity_indicators: [
      'Steady growth',
      'Multiple roles',
      'Established processes',
      'Market presence'
    ]
  },
  [OfficeJourney.MATURE]: {
    journey: OfficeJourney.MATURE,
    typical_size_range: [75, 200],
    common_roles: ['Consultant', 'Sales', 'Operations'],
    growth_expectations: {
      recruitment_rate: 0.03, // 3% monthly growth
      churn_rate: 0.03, // 3% monthly churn
    },
    maturity_indicators: [
      'Stable operations',
      'Full role coverage',
      'Optimized processes',
      'Market leadership'
    ]
  }
};