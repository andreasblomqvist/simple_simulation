/**
 * Data Validation Hook
 * 
 * Custom hook for managing data validation across different domains.
 * Bridges ValidationService to UI components with reactive validation.
 */

import { useState, useCallback, useMemo, useEffect } from 'react';
import { 
  ValidationService,
  type ValidationResult,
  type FieldValidation
} from '../services';
import type { 
  ScenarioDefinition
} from '../types/unified-data-structures';
import type { StandardRole, StandardLevel } from '../types/office';

export interface UseDataValidationOptions {
  validateOnChange?: boolean;
  debounceMs?: number;
}

export interface UseDataValidationReturn {
  // Validation state
  validationResults: Map<string, ValidationResult>;
  fieldValidations: Map<string, FieldValidation>;
  isValid: boolean;
  hasWarnings: boolean;
  allErrors: string[];
  allWarnings: string[];
  
  // Validation actions
  validateScenario: (scenario: Partial<ScenarioDefinition>) => Promise<ValidationResult>;
  validateField: (
    field: string,
    value: any,
    constraints?: {
      required?: boolean;
      min?: number;
      max?: number;
      type?: 'string' | 'number' | 'boolean' | 'array' | 'object';
      pattern?: RegExp;
    }
  ) => FieldValidation;
  validatePlanningCell: (
    role: StandardRole,
    level: StandardLevel,
    month: number,
    year: number,
    values: {
      recruitment?: number;
      churn?: number;
      price?: number;
      utr?: number;
      salary?: number;
    }
  ) => ValidationResult;
  validateBatch: <T>(
    items: T[],
    validator: (item: T) => ValidationResult
  ) => ValidationResult;
  
  // Utilities
  clearValidation: (key?: string) => void;
  clearAllValidations: () => void;
  getValidationSummary: () => {
    totalItems: number;
    validItems: number;
    invalidItems: number;
    warningItems: number;
  };
}

export function useDataValidation(
  options: UseDataValidationOptions = {}
): UseDataValidationReturn {
  const { validateOnChange = true, debounceMs = 300 } = options;
  
  const [validationResults, setValidationResults] = useState<Map<string, ValidationResult>>(
    new Map()
  );
  const [fieldValidations, setFieldValidations] = useState<Map<string, FieldValidation>>(
    new Map()
  );
  
  // Debounced validation timer
  const [validationTimer, setValidationTimer] = useState<NodeJS.Timeout | null>(null);
  
  // Clear timer on unmount
  useEffect(() => {
    return () => {
      if (validationTimer) {
        clearTimeout(validationTimer);
      }
    };
  }, [validationTimer]);
  
  // Debounced validation function
  const debouncedValidation = useCallback(
    (key: string, validationFn: () => ValidationResult | Promise<ValidationResult>) => {
      if (validationTimer) {
        clearTimeout(validationTimer);
      }
      
      const timer = setTimeout(async () => {
        const result = await validationFn();
        setValidationResults(prev => new Map(prev.set(key, result)));
      }, debounceMs);
      
      setValidationTimer(timer);
    },
    [validationTimer, debounceMs]
  );
  
  // Validate scenario
  const validateScenario = useCallback(async (
    scenario: Partial<ScenarioDefinition>
  ): Promise<ValidationResult> => {
    const key = 'scenario';
    
    if (validateOnChange) {
      debouncedValidation(key, () => ValidationService.validateScenario(scenario));
      // Return cached result immediately if available
      return validationResults.get(key) || { valid: true, errors: [], warnings: [] };
    } else {
      const result = ValidationService.validateScenario(scenario);
      setValidationResults(prev => new Map(prev.set(key, result)));
      return result;
    }
  }, [validateOnChange, debouncedValidation, validationResults]);
  
  // Validate field
  const validateField = useCallback((
    field: string,
    value: any,
    constraints?: {
      required?: boolean;
      min?: number;
      max?: number;
      type?: 'string' | 'number' | 'boolean' | 'array' | 'object';
      pattern?: RegExp;
    }
  ): FieldValidation => {
    const result = ValidationService.validateField(field, value, constraints);
    
    if (validateOnChange) {
      setFieldValidations(prev => new Map(prev.set(field, result)));
    }
    
    return result;
  }, [validateOnChange]);
  
  // Validate planning cell
  const validatePlanningCell = useCallback((
    role: StandardRole,
    level: StandardLevel,
    month: number,
    year: number,
    values: {
      recruitment?: number;
      churn?: number;
      price?: number;
      utr?: number;
      salary?: number;
    }
  ): ValidationResult => {
    const key = `planning-${role}-${level}-${year}${month.toString().padStart(2, '0')}`;
    
    const validationFn = () => ValidationService.validatePlanningCell(
      role, level, month, year, values
    );
    
    if (validateOnChange) {
      debouncedValidation(key, validationFn);
      // Return cached result immediately if available
      return validationResults.get(key) || { valid: true, errors: [], warnings: [] };
    } else {
      const result = validationFn();
      setValidationResults(prev => new Map(prev.set(key, result)));
      return result;
    }
  }, [validateOnChange, debouncedValidation, validationResults]);
  
  // Validate batch
  const validateBatch = useCallback(<T>(
    items: T[],
    validator: (item: T) => ValidationResult
  ): ValidationResult => {
    return ValidationService.validateBatch(items, validator);
  }, []);
  
  // Clear specific validation
  const clearValidation = useCallback((key?: string) => {
    if (key) {
      setValidationResults(prev => {
        const newMap = new Map(prev);
        newMap.delete(key);
        return newMap;
      });
      setFieldValidations(prev => {
        const newMap = new Map(prev);
        newMap.delete(key);
        return newMap;
      });
    }
  }, []);
  
  // Clear all validations
  const clearAllValidations = useCallback(() => {
    setValidationResults(new Map());
    setFieldValidations(new Map());
  }, []);
  
  // Computed properties
  const isValid = useMemo(() => {
    // Check all validation results
    for (const result of validationResults.values()) {
      if (!result.valid) return false;
    }
    
    // Check all field validations
    for (const field of fieldValidations.values()) {
      if (!field.valid) return false;
    }
    
    return true;
  }, [validationResults, fieldValidations]);
  
  const hasWarnings = useMemo(() => {
    // Check all validation results for warnings
    for (const result of validationResults.values()) {
      if (result.warnings.length > 0) return true;
    }
    
    // Check all field validations for warnings
    for (const field of fieldValidations.values()) {
      if (field.warning) return true;
    }
    
    return false;
  }, [validationResults, fieldValidations]);
  
  const allErrors = useMemo(() => {
    const errors: string[] = [];
    
    // Collect errors from validation results
    validationResults.forEach(result => {
      errors.push(...result.errors);
    });
    
    // Collect errors from field validations
    fieldValidations.forEach(field => {
      if (field.error) {
        errors.push(field.error);
      }
    });
    
    return errors;
  }, [validationResults, fieldValidations]);
  
  const allWarnings = useMemo(() => {
    const warnings: string[] = [];
    
    // Collect warnings from validation results
    validationResults.forEach(result => {
      warnings.push(...result.warnings);
    });
    
    // Collect warnings from field validations
    fieldValidations.forEach(field => {
      if (field.warning) {
        warnings.push(field.warning);
      }
    });
    
    return warnings;
  }, [validationResults, fieldValidations]);
  
  // Get validation summary
  const getValidationSummary = useCallback(() => {
    const totalResults = validationResults.size + fieldValidations.size;
    let validItems = 0;
    let invalidItems = 0;
    let warningItems = 0;
    
    // Count validation results
    validationResults.forEach(result => {
      if (result.valid) {
        validItems++;
      } else {
        invalidItems++;
      }
      if (result.warnings.length > 0) {
        warningItems++;
      }
    });
    
    // Count field validations
    fieldValidations.forEach(field => {
      if (field.valid) {
        validItems++;
      } else {
        invalidItems++;
      }
      if (field.warning) {
        warningItems++;
      }
    });
    
    return {
      totalItems: totalResults,
      validItems,
      invalidItems,
      warningItems
    };
  }, [validationResults, fieldValidations]);
  
  return {
    // Validation state
    validationResults,
    fieldValidations,
    isValid,
    hasWarnings,
    allErrors,
    allWarnings,
    
    // Validation actions
    validateScenario,
    validateField,
    validatePlanningCell,
    validateBatch,
    
    // Utilities
    clearValidation,
    clearAllValidations,
    getValidationSummary
  };
}