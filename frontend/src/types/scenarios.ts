// Scenario Types for Scenario Runner
// TypeScript definitions matching backend Pydantic models

// ========================================
// Base Types & Enums
// ========================================

export type ScenarioId = string;
export type OfficeName = string;
export type LevelType = 'A' | 'AC' | 'C' | 'SrC' | 'M' | 'SrM' | 'PiP' | 'AM+';
export type LeverType = 'recruitment' | 'churn' | 'progression';
export type ComparisonType = 'side_by_side' | 'overlay' | 'difference';

// ========================================
// Core Scenario Types
// ========================================

export interface TimeRange {
  start_year: number;
  start_month: number;
  end_year: number;
  end_month: number;
}

export type LeverMultipliers = Partial<Record<LevelType, number>>;

export type ScenarioLevers = Partial<Record<LeverType, LeverMultipliers>>;

export interface EconomicParams {
  price_increase?: number;
  salary_increase?: number;
  unplanned_absence?: number;
  working_hours_per_month?: number;
  other_expense?: number;
  employment_cost_rate?: number;
  utilization?: number;
}

export interface ScenarioDefinition {
  name: string;
  description?: string;
  time_range: TimeRange;
  office_scope: OfficeName[];
  levers: ScenarioLevers;
  economic_params?: EconomicParams;
  created_at?: string | Date;
  updated_at?: string | Date;
}

// ========================================
// API Request/Response Types
// ========================================

export interface ScenarioRequest {
  scenario_id?: ScenarioId;
  scenario_definition?: ScenarioDefinition;
  office_scope?: OfficeName[];
}

export interface ScenarioResponse {
  scenario_id: ScenarioId;
  scenario_name: string;
  execution_time: number;
  results: SimulationResults;
  status: 'success' | 'error';
  error_message?: string;
}

export interface ScenarioListResponse {
  scenarios: ScenarioListItem[];
}

export interface ScenarioListItem {
  id: ScenarioId;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  time_range: TimeRange;
  office_scope: OfficeName[];
}

// ========================================
// Simulation Results Types
// ========================================

export interface SimulationResults {
  years: Record<string, YearData>;
  kpis?: KPIData;
  metadata?: SimulationMetadata;
}

export interface YearData {
  offices: Record<OfficeName, OfficeData>;
  aggregated?: AggregatedData;
}

export interface OfficeData {
  total_fte: number;
  roles: Record<string, RoleData>;
  financial?: FinancialData;
  growth?: GrowthData;
  kpis?: KPIData;
}

export interface RoleData {
  [level: string]: {
    fte: number;
    price_1?: number;
    price_2?: number;
    price_3?: number;
    price_4?: number;
    price_5?: number;
    price_6?: number;
    price_7?: number;
    price_8?: number;
    price_9?: number;
    price_10?: number;
    price_11?: number;
    price_12?: number;
    recruitment_1?: number;
    recruitment_2?: number;
    recruitment_3?: number;
    recruitment_4?: number;
    recruitment_5?: number;
    recruitment_6?: number;
    recruitment_7?: number;
    recruitment_8?: number;
    recruitment_9?: number;
    recruitment_10?: number;
    recruitment_11?: number;
    recruitment_12?: number;
    churn_1?: number;
    churn_2?: number;
    churn_3?: number;
    churn_4?: number;
    churn_5?: number;
    churn_6?: number;
    churn_7?: number;
    churn_8?: number;
    churn_9?: number;
    churn_10?: number;
    churn_11?: number;
    churn_12?: number;
  };
}

export interface FinancialData {
  net_sales: number;
  total_salary_costs: number;
  ebitda: number;
  margin: number;
  avg_hourly_rate: number;
  avg_utr: number;
}

export interface GrowthData {
  total_growth_percent: number;
  total_growth_absolute: number;
  non_debit_ratio: number;
}

export interface AggregatedData {
  total_fte: number;
  financial: FinancialData;
  growth: GrowthData;
}

export interface KPIData {
  financial: FinancialKPIs;
  growth: GrowthKPIs;
  journeys: JourneyKPIs;
  yearly_kpis: Record<string, YearlyKPIs>;
}

export interface FinancialKPIs {
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
}

export interface GrowthKPIs {
  total_growth_percent: number;
  total_growth_absolute: number;
  current_total_fte: number;
  baseline_total_fte: number;
  non_debit_ratio: number;
  non_debit_ratio_baseline: number;
  non_debit_delta: number;
}

export interface JourneyKPIs {
  journey_totals: Record<string, number>;
  journey_percentages: Record<string, number>;
  journey_deltas: Record<string, number>;
  journey_totals_baseline: Record<string, number>;
  journey_percentages_baseline: Record<string, number>;
}

export interface YearlyKPIs {
  year: string;
  financial: FinancialKPIs;
  growth: GrowthKPIs;
  journeys: JourneyKPIs;
  year_over_year_growth: number;
  year_over_year_margin_change: number;
}

export interface SimulationMetadata {
  generated_at: string;
  processing_time: number;
  version: string;
}

// ========================================
// Comparison Types
// ========================================

export interface ScenarioComparisonRequest {
  scenario_ids: ScenarioId[];
  comparison_type: ComparisonType;
  include_monthly_data?: boolean;
}

export interface ScenarioComparisonResponse {
  comparison_id: string;
  scenarios: Record<ScenarioId, ScenarioResponse>;
  comparison_data: ComparisonData;
  metadata: ComparisonMetadata;
}

export interface ComparisonData {
  differences: Record<string, ComparisonDifference>;
  summary: ComparisonSummary;
}

export interface ComparisonDifference {
  field: string;
  scenario1_value: number;
  scenario2_value: number;
  absolute_difference: number;
  percentage_difference: number;
  significance: 'high' | 'medium' | 'low';
}

export interface ComparisonSummary {
  total_differences: number;
  significant_differences: number;
  key_insights: string[];
  recommendations: string[];
}

export interface ComparisonMetadata {
  compared_at: string;
  comparison_type: ComparisonType;
  processing_time: number;
}

// ========================================
// Form & UI Types
// ========================================

export interface ScenarioFormData {
  name: string;
  description: string;
  time_range: TimeRange;
  office_scope: OfficeName[];
  levers: ScenarioLevers;
  economic_params: EconomicParams;
}

export type LeverFormData = Record<LeverType, Record<LevelType, number>>;

export interface ScenarioFormValidation {
  name: boolean;
  time_range: boolean;
  office_scope: boolean;
  levers: boolean;
}

// ========================================
// Component Props Types
// ========================================

export interface ScenarioListProps {
  scenarios: ScenarioListItem[];
  loading?: boolean;
  onSelect: (scenarioId: ScenarioId) => void;
  onEdit: (scenarioId: ScenarioId) => void;
  onDelete: (scenarioId: ScenarioId) => void;
  onCompare: (scenarioIds: ScenarioId[]) => void;
  onExport: (scenarioId: ScenarioId) => void;
}

export interface ScenarioEditorProps {
  scenario?: ScenarioDefinition;
  offices: OfficeName[];
  onSave: (scenario: ScenarioDefinition) => void;
  onCancel: () => void;
  loading?: boolean;
}

export interface ScenarioResultsProps {
  results: SimulationResults;
  scenario: ScenarioDefinition;
  onExport: () => void;
  onCompare: () => void;
  loading?: boolean;
}

export interface ScenarioComparisonProps {
  comparison: ScenarioComparisonResponse;
  onBack: () => void;
  onExport: () => void;
  loading?: boolean;
}

// ========================================
// Utility Types
// ========================================

export type PartialScenarioDefinition = Partial<ScenarioDefinition>;
export type ScenarioStatus = 'draft' | 'saved' | 'running' | 'completed' | 'error';
export type ScenarioVisibility = 'private' | 'shared' | 'public';

export interface ScenarioMetadata {
  id: ScenarioId;
  name: string;
  description?: string;
  status: ScenarioStatus;
  visibility: ScenarioVisibility;
  created_by: string;
  created_at: Date;
  updated_at: Date;
  tags: string[];
  version: number;
} 