/**
 * Services Export Module
 * 
 * Centralized export point for all business services.
 * Provides clean imports for components and hooks.
 */

export { ScenarioService } from './scenarioService';
export type { 
  ScenarioValidationResult,
  ScenarioFormData,
  ScenarioWorkflowState
} from './scenarioService';

export { DataTransformService } from './dataTransformService';
export type {
  RoleDefaults,
  MonthlyRoleData,
  BaselineStructuredData
} from './dataTransformService';

export { PlanningService } from './planningService';
export type {
  SummaryData,
  CellData,
  MonthlyCalculation,
  RoleSummary,
  FinancialMetrics,
  WorkforceMetrics,
  DetailedCalculations
} from './planningService';

export { ValidationService } from './validationService';
export type {
  ValidationResult,
  FieldValidation,
  BusinessRuleValidation
} from './validationService';

export { ResultsService } from './resultsService';
export type {
  WorkforceMetrics as ResultsWorkforceMetrics,
  ProcessedYearData,
  ConsultantLevelData,
  SeniorityDistribution,
  MonthlyData,
  RecruitmentChurnData
} from './resultsService';

// Re-export existing API services for compatibility
export { scenarioApi } from './scenarioApi';
export { simulationApi } from './simulationApi';
export { default as SimulationApi } from './simulationApi';
export type { SimulationApiService } from './simulationApi';