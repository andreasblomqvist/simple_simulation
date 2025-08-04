/**
 * Hooks Export Module
 * 
 * Centralized export point for all custom hooks.
 * Provides clean imports for components.
 */

// Service-based hooks
export { useScenarioForm } from './useScenarioForm';
export type { 
  UseScenarioFormOptions,
  UseScenarioFormReturn
} from './useScenarioForm';

export { usePlanningData } from './usePlanningData';
export type {
  UsePlanningDataOptions,
  UsePlanningDataReturn
} from './usePlanningData';

export { useDataValidation } from './useDataValidation';
export type {
  UseDataValidationOptions,
  UseDataValidationReturn
} from './useDataValidation';

export { useBaselineData, useBaselineDataWithRef } from './useBaselineData';
export type {
  UseBaselineDataOptions,
  UseBaselineDataReturn,
  BaselineDataRef
} from './useBaselineData';

// Re-export existing hooks for compatibility
export * from './simulation';
export * from './yearNavigation';