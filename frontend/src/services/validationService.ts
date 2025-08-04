/**
 * Validation Service
 * 
 * Handles business rule validation, data integrity checks, and constraint validation.
 * Provides centralized validation logic for all business domains.
 */

import type { 
  ScenarioDefinition
} from '../types/unified-data-structures';
import type { OfficeConfig, StandardRole, StandardLevel } from '../types/office';

export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

export interface FieldValidation {
  field: string;
  value: any;
  valid: boolean;
  error?: string;
  warning?: string;
}

export interface BusinessRuleValidation {
  rule: string;
  valid: boolean;
  message: string;
  severity: 'error' | 'warning' | 'info';
}

export class ValidationService {
  /**
   * Validate a complete scenario definition
   */
  static validateScenario(scenario: Partial<ScenarioDefinition>): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Required fields validation
    if (!scenario.name || scenario.name.trim().length === 0) {
      errors.push('Scenario name is required');
    }

    if (!scenario.time_range?.start_year || scenario.time_range.start_year < 2020 || scenario.time_range.start_year > 2030) {
      errors.push('Start year must be between 2020 and 2030');
    }

    if (!scenario.time_range?.end_year || scenario.time_range.end_year < scenario.time_range.start_year) {
      errors.push('End year must be after start year');
    }

    if (!scenario.office_scope || !Array.isArray(scenario.office_scope) || scenario.office_scope.length === 0) {
      errors.push('At least one office must be selected');
    }

    // Baseline input validation
    if (scenario.baseline_input) {
      const baselineValidation = this.validateBaselineInput(scenario.baseline_input);
      errors.push(...baselineValidation.errors);
      warnings.push(...baselineValidation.warnings);
    } else {
      warnings.push('No baseline input provided - using defaults');
    }

    // Levers validation
    if (scenario.levers) {
      const leversValidation = this.validateLevers(scenario.levers);
      errors.push(...leversValidation.errors);
      warnings.push(...leversValidation.warnings);
    }

    // Business logic validation
    const businessValidation = this.validateScenarioBusinessRules(scenario);
    errors.push(...businessValidation.errors);
    warnings.push(...businessValidation.warnings);

    return {
      valid: errors.length === 0,
      errors,
      warnings
    };
  }

  /**
   * Validate baseline input data structure and values
   */
  static validateBaselineInput(baselineInput: any): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    if (!baselineInput.global) {
      errors.push('Baseline input must have global data');
      return { valid: false, errors, warnings };
    }

    const { global } = baselineInput;

    // Validate recruitment data
    if (global.recruitment) {
      const recruitmentValidation = this.validateMonthlyRoleData(
        global.recruitment,
        'recruitment'
      );
      errors.push(...recruitmentValidation.errors);
      warnings.push(...recruitmentValidation.warnings);
    }

    // Validate churn data
    if (global.churn) {
      const churnValidation = this.validateMonthlyRoleData(
        global.churn,
        'churn'
      );
      errors.push(...churnValidation.errors);
      warnings.push(...churnValidation.warnings);
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings
    };
  }

  /**
   * Validate monthly role data structure
   */
  private static validateMonthlyRoleData(
    data: any,
    dataType: string
  ): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    if (!data || typeof data !== 'object') {
      errors.push(`${dataType} data must be an object`);
      return { valid: false, errors, warnings };
    }

    const validRoles = ['Consultant', 'Sales', 'Operations'];
    const validLevels = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP'];

    Object.keys(data).forEach(role => {
      if (!validRoles.includes(role)) {
        warnings.push(`Unknown role: ${role}`);
      }

      const roleData = data[role];
      if (!roleData || typeof roleData !== 'object') {
        errors.push(`${dataType} data for ${role} must be an object`);
        return;
      }

      Object.keys(roleData).forEach(level => {
        if (!validLevels.includes(level)) {
          warnings.push(`Unknown level: ${level} for role ${role}`);
        }

        const levelData = roleData[level];
        if (!levelData || typeof levelData !== 'object') {
          errors.push(`${dataType} data for ${role}.${level} must be an object`);
          return;
        }

        // Validate monthly values
        Object.keys(levelData).forEach(month => {
          const value = levelData[month];
          
          // Check month format (YYYYMM)
          if (!/^\d{6}$/.test(month)) {
            errors.push(`Invalid month format: ${month} (expected YYYYMM)`);
          }

          // Check value is a number
          if (value !== undefined && value !== null) {
            const numValue = Number(value);
            if (isNaN(numValue)) {
              errors.push(`${dataType} value for ${role}.${level}.${month} must be a number`);
            } else if (numValue < 0) {
              errors.push(`${dataType} value for ${role}.${level}.${month} cannot be negative`);
            } else if (numValue > 1000) {
              warnings.push(`Very high ${dataType} value: ${numValue} for ${role}.${level}.${month}`);
            }
          }
        });
      });
    });

    return {
      valid: errors.length === 0,
      errors,
      warnings
    };
  }

  /**
   * Validate scenario levers
   */
  static validateLevers(levers: any): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    if (!levers || typeof levers !== 'object') {
      errors.push('Levers must be an object');
      return { valid: false, errors, warnings };
    }

    // Validate recruitment levers
    if (levers.recruitment) {
      const validation = this.validateLeverData(levers.recruitment, 'recruitment');
      errors.push(...validation.errors);
      warnings.push(...validation.warnings);
    }

    // Validate churn levers
    if (levers.churn) {
      const validation = this.validateLeverData(levers.churn, 'churn');
      errors.push(...validation.errors);
      warnings.push(...validation.warnings);
    }

    // Validate progression levers
    if (levers.progression) {
      const validation = this.validateProgressionLevers(levers.progression);
      errors.push(...validation.errors);
      warnings.push(...validation.warnings);
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings
    };
  }

  /**
   * Validate lever data (recruitment/churn multipliers)
   */
  private static validateLeverData(data: any, leverType: string): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    if (typeof data !== 'object') {
      errors.push(`${leverType} levers must be an object`);
      return { valid: false, errors, warnings };
    }

    Object.keys(data).forEach(key => {
      const value = data[key];
      
      if (typeof value === 'number') {
        if (value < 0.1 || value > 10) {
          warnings.push(`${leverType} lever ${key} has extreme value: ${value} (recommended: 0.1-10)`);
        }
      } else if (typeof value === 'object' && value !== null) {
        // Nested lever structure
        Object.keys(value).forEach(subKey => {
          const subValue = value[subKey];
          if (typeof subValue === 'number') {
            if (subValue < 0.1 || subValue > 10) {
              warnings.push(`${leverType} lever ${key}.${subKey} has extreme value: ${subValue}`);
            }
          }
        });
      }
    });

    return {
      valid: errors.length === 0,
      errors,
      warnings
    };
  }

  /**
   * Validate progression levers
   */
  private static validateProgressionLevers(progression: any): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    if (typeof progression !== 'object') {
      errors.push('Progression levers must be an object');
      return { valid: false, errors, warnings };
    }

    Object.keys(progression).forEach(key => {
      const value = progression[key];
      
      if (typeof value === 'number') {
        if (value < 0 || value > 1) {
          errors.push(`Progression lever ${key} must be between 0 and 1 (percentage)`);
        }
      }
    });

    return {
      valid: errors.length === 0,
      errors,
      warnings
    };
  }

  /**
   * Validate scenario business rules
   */
  private static validateScenarioBusinessRules(scenario: Partial<ScenarioDefinition>): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Time range validation
    if (scenario.time_range?.start_year && scenario.time_range?.end_year) {
      const yearRange = scenario.time_range.end_year - scenario.time_range.start_year;
      if (yearRange > 10) {
        warnings.push('Simulation span exceeds 10 years - consider shorter timeframes for accuracy');
      }
      if (yearRange < 1) {
        errors.push('Simulation must span at least 1 full year');
      }
    }

    // Office scope validation
    if (scenario.office_scope && scenario.office_scope.length > 10) {
      warnings.push('Large number of offices selected - simulation may be slow');
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings
    };
  }

  /**
   * Validate individual field values
   */
  static validateField(
    field: string,
    value: any,
    constraints?: {
      required?: boolean;
      min?: number;
      max?: number;
      type?: 'string' | 'number' | 'boolean' | 'array' | 'object';
      pattern?: RegExp;
    }
  ): FieldValidation {
    const result: FieldValidation = {
      field,
      value,
      valid: true
    };

    if (!constraints) {
      return result;
    }

    // Required validation
    if (constraints.required && (value === null || value === undefined || value === '')) {
      result.valid = false;
      result.error = `${field} is required`;
      return result;
    }

    // Skip further validation if value is empty and not required
    if (value === null || value === undefined || value === '') {
      return result;
    }

    // Type validation
    if (constraints.type) {
      const actualType = Array.isArray(value) ? 'array' : typeof value;
      if (actualType !== constraints.type) {
        result.valid = false;
        result.error = `${field} must be of type ${constraints.type}`;
        return result;
      }
    }

    // Numeric constraints
    if (constraints.type === 'number' && typeof value === 'number') {
      if (constraints.min !== undefined && value < constraints.min) {
        result.valid = false;
        result.error = `${field} must be at least ${constraints.min}`;
        return result;
      }
      if (constraints.max !== undefined && value > constraints.max) {
        result.valid = false;
        result.error = `${field} must be at most ${constraints.max}`;
        return result;
      }
    }

    // Pattern validation
    if (constraints.pattern && typeof value === 'string') {
      if (!constraints.pattern.test(value)) {
        result.valid = false;
        result.error = `${field} format is invalid`;
        return result;
      }
    }

    return result;
  }

  /**
   * Validate business planning cell data
   */
  static validatePlanningCell(
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
  ): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    const cellId = `${role}.${level}.${year}${month.toString().padStart(2, '0')}`;

    // Validate recruitment
    if (values.recruitment !== undefined) {
      if (values.recruitment < 0) {
        errors.push(`${cellId}: Recruitment cannot be negative`);
      }
      if (values.recruitment > 100) {
        warnings.push(`${cellId}: Very high recruitment value (${values.recruitment})`);
      }
    }

    // Validate churn
    if (values.churn !== undefined) {
      if (values.churn < 0) {
        errors.push(`${cellId}: Churn cannot be negative`);
      }
      if (values.churn > 50) {
        warnings.push(`${cellId}: Very high churn value (${values.churn})`);
      }
    }

    // Validate UTR (Utilization Rate)
    if (values.utr !== undefined) {
      if (values.utr < 0 || values.utr > 1) {
        errors.push(`${cellId}: UTR must be between 0 and 1`);
      }
      if (values.utr < 0.3) {
        warnings.push(`${cellId}: Very low UTR (${values.utr})`);
      }
    }

    // Validate price
    if (values.price !== undefined) {
      if (values.price < 0) {
        errors.push(`${cellId}: Price cannot be negative`);
      }
      if (values.price > 2000) {
        warnings.push(`${cellId}: Very high hourly rate (${values.price})`);
      }
    }

    // Validate salary
    if (values.salary !== undefined) {
      if (values.salary < 0) {
        errors.push(`${cellId}: Salary cannot be negative`);
      }
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings
    };
  }

  /**
   * Batch validate multiple items
   */
  static validateBatch<T>(
    items: T[],
    validator: (item: T) => ValidationResult
  ): ValidationResult {
    const allErrors: string[] = [];
    const allWarnings: string[] = [];

    items.forEach((item, index) => {
      const result = validator(item);
      allErrors.push(...result.errors.map(err => `Item ${index + 1}: ${err}`));
      allWarnings.push(...result.warnings.map(warn => `Item ${index + 1}: ${warn}`));
    });

    return {
      valid: allErrors.length === 0,
      errors: allErrors,
      warnings: allWarnings
    };
  }
}