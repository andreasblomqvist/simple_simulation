/**
 * Scenario Service
 * 
 * Handles scenario workflow management, validation, and state transitions.
 * Extracted from ScenarioWizardV2 to separate business logic from UI.
 */

import type { 
  ScenarioDefinition, 
  ScenarioResponse, 
  ErrorResponse,
  BaselineInput,
  ProgressionConfig,
  CATCurves
} from '../types/unified-data-structures';
import { scenarioApi } from './scenarioApi';

export interface ScenarioValidationResult {
  valid: boolean;
  errors: string[];
}

export interface ScenarioFormData {
  scenario: Partial<ScenarioDefinition>;
  baselineData: any;
  leversData: any;
}

export interface ScenarioWorkflowState {
  current: number;
  scenario: Partial<ScenarioDefinition>;
  scenarioId: string;
  baselineData: any;
  saving: boolean;
  simulating: boolean;
  simulationResult: ScenarioResponse | null;
  simulationError: ErrorResponse | string | null;
  validationErrors: string[];
  validationLoading: boolean;
}

export class ScenarioService {
  /**
   * Initialize workflow state for scenario creation/editing
   */
  static createInitialState(initialScenario?: Partial<ScenarioDefinition>): ScenarioWorkflowState {
    return {
      current: 0,
      scenario: initialScenario || {},
      scenarioId: '',
      baselineData: null,
      saving: false,
      simulating: false,
      simulationResult: null,
      simulationError: null,
      validationErrors: [],
      validationLoading: false,
    };
  }

  /**
   * Load existing scenario for editing
   */
  static async loadScenario(id: string): Promise<{
    scenario: ScenarioDefinition;
    baselineData: any;
  }> {
    const data = await scenarioApi.getScenario(id);
    console.log('[DEBUG] Loaded scenario data:', data);
    
    const actualScenario = data;
    
    let baselineData;
    if (actualScenario?.baseline_input) {
      baselineData = actualScenario.baseline_input;
    } else {
      baselineData = {
        global: {
          recruitment: {},
          churn: {}
        }
      };
    }

    return {
      scenario: actualScenario,
      baselineData
    };
  }

  /**
   * Validate scenario data structure and business rules
   */
  static async validateScenario(scenarioData: ScenarioDefinition): Promise<ScenarioValidationResult> {
    try {
      const validation = await scenarioApi.validateScenario(scenarioData);
      return {
        valid: validation.valid,
        errors: validation.errors
      };
    } catch (error) {
      console.warn('Validation endpoint not available, skipping validation');
      return {
        valid: true,
        errors: []
      };
    }
  }

  /**
   * Fetch default progression configuration from backend
   */
  static async getDefaultProgressionConfig(): Promise<{
    progression_config: ProgressionConfig;
    cat_curves: CATCurves;
  }> {
    try {
      // Fetch from the progression config endpoint or use defaults
      const response = await fetch('/api/config/progression');
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.warn('Could not fetch progression config from backend, using defaults:', error);
    }

    // Default progression configuration (from backend/config/progression_config.py)
    const defaultProgressionConfig: ProgressionConfig = {
      'A': {
        progression_months: [1, 4, 7, 10],
        start_tenure: 1,
        time_on_level: 6,
        next_level: 'AC',
        journey: 'J-1'
      },
      'AC': {
        progression_months: [1, 4, 7, 10],
        start_tenure: 6,
        time_on_level: 9,
        next_level: 'C',
        journey: 'J-1'
      },
      'C': {
        progression_months: [1, 7],
        start_tenure: 15,
        time_on_level: 12,
        next_level: 'SrC',
        journey: 'J-1'
      },
      'SrC': {
        progression_months: [1, 7],
        start_tenure: 27,
        time_on_level: 18,
        next_level: 'AM',
        journey: 'J-2'
      },
      'AM': {
        progression_months: [1, 7],
        start_tenure: 45,
        time_on_level: 30,
        next_level: 'M',
        journey: 'J-2'
      },
      'M': {
        progression_months: [1],
        start_tenure: 75,
        time_on_level: 24,
        next_level: 'SrM',
        journey: 'J-3'
      },
      'SrM': {
        progression_months: [1],
        start_tenure: 99,
        time_on_level: 120,
        next_level: 'Pi',
        journey: 'J-3'
      },
      'Pi': {
        progression_months: [1],
        start_tenure: 219,
        time_on_level: 12,
        next_level: 'P',
        journey: 'J-3'
      },
      'P': {
        progression_months: [1],
        start_tenure: 231,
        time_on_level: 1000,
        next_level: 'X',
        journey: 'J-3'
      },
      'X': {
        progression_months: [1],
        start_tenure: 1231,
        time_on_level: 1000,
        next_level: 'X',
        journey: 'J-3'
      },
      'OPE': {
        progression_months: [1],
        start_tenure: 1279,
        time_on_level: 1000,
        next_level: 'OPE',
        journey: 'J-3'
      }
    };

    // Default CAT curves (from backend/config/progression_config.py)
    const defaultCATCurves: CATCurves = {
      'A': { 'CAT0': 0.0, 'CAT6': 0.919, 'CAT12': 0.85, 'CAT18': 0.0, 'CAT24': 0.0, 'CAT30': 0.0 },
      'AC': { 'CAT0': 0.0, 'CAT6': 0.054, 'CAT12': 0.759, 'CAT18': 0.400, 'CAT24': 0.0, 'CAT30': 0.0 },
      'C': { 'CAT0': 0.0, 'CAT6': 0.050, 'CAT12': 0.442, 'CAT18': 0.597, 'CAT24': 0.278, 'CAT30': 0.643, 'CAT36': 0.200, 'CAT42': 0.0 },
      'SrC': { 'CAT0': 0.0, 'CAT6': 0.206, 'CAT12': 0.438, 'CAT18': 0.317, 'CAT24': 0.211, 'CAT30': 0.206, 'CAT36': 0.167, 'CAT42': 0.0, 'CAT48': 0.0, 'CAT54': 0.0, 'CAT60': 0.0 },
      'AM': { 'CAT0': 0.0, 'CAT6': 0.0, 'CAT12': 0.0, 'CAT18': 0.189, 'CAT24': 0.197, 'CAT30': 0.234, 'CAT36': 0.048, 'CAT42': 0.0, 'CAT48': 0.0, 'CAT54': 0.0, 'CAT60': 0.0 },
      'M': { 'CAT0': 0.0, 'CAT6': 0.00, 'CAT12': 0.01, 'CAT18': 0.02, 'CAT24': 0.03, 'CAT30': 0.04, 'CAT36': 0.05, 'CAT42': 0.06, 'CAT48': 0.07, 'CAT54': 0.08, 'CAT60': 0.10 },
      'SrM': { 'CAT0': 0.0, 'CAT6': 0.00, 'CAT12': 0.005, 'CAT18': 0.01, 'CAT24': 0.015, 'CAT30': 0.02, 'CAT36': 0.025, 'CAT42': 0.03, 'CAT48': 0.04, 'CAT54': 0.05, 'CAT60': 0.06 },
      'Pi': { 'CAT0': 0.0 },
      'P': { 'CAT0': 0.0 },
      'X': { 'CAT0': 0.0 },
      'OPE': { 'CAT0': 0.0 }
    };

    return {
      progression_config: {
        levels: defaultProgressionConfig
      },
      cat_curves: {
        curves: Object.entries(defaultCATCurves).reduce((acc, [level, curves]) => {
          acc[level] = { curves };
          return acc;
        }, {} as Record<string, { curves: Record<string, number> }>)
      }
    };
  }

  /**
   * Build complete scenario definition from form data
   */
  static async buildScenarioDefinition(formData: ScenarioFormData): Promise<ScenarioDefinition> {
    const { scenario, baselineData, leversData } = formData;
    
    // Ensure we have valid baseline input
    const baselineInput = baselineData || {
      global: {
        recruitment: {},
        churn: {}
      }
    };

    // Structure levers data consistently
    const levers = {
      recruitment: leversData?.recruitment || {},
      churn: leversData?.churn || {},
      progression: leversData?.progression || {}
    };

    // Get default progression configuration if not already provided
    let progressionConfig = scenario.progression_config;
    let catCurves = scenario.cat_curves;
    
    if (!progressionConfig || !catCurves) {
      const defaultProgression = await this.getDefaultProgressionConfig();
      progressionConfig = progressionConfig || defaultProgression.progression_config;
      catCurves = catCurves || defaultProgression.cat_curves;
    }

    return {
      ...scenario,
      description: scenario.description || 'No description provided',
      baseline_input: baselineInput,
      levers,
      economic_params: scenario.economic_params || {},
      progression_config: progressionConfig,
      cat_curves: catCurves
    } as ScenarioDefinition;
  }

  /**
   * Save scenario (create or update)
   */
  static async saveScenario(
    formData: ScenarioFormData,
    editingId?: string
  ): Promise<{
    success: boolean;
    scenarioId?: string;
    error?: string;
  }> {
    try {
      const scenarioWithData = await this.buildScenarioDefinition(formData);
      
      // Validate before saving
      const validation = await this.validateScenario(scenarioWithData);
      if (!validation.valid) {
        return {
          success: false,
          error: `Validation failed: ${validation.errors.join(', ')}`
        };
      }
      
      if (editingId) {
        await scenarioApi.updateScenario(editingId, scenarioWithData);
        return {
          success: true,
          scenarioId: editingId
        };
      } else {
        const newScenarioId = await scenarioApi.createScenario(scenarioWithData);
        return {
          success: true,
          scenarioId: newScenarioId
        };
      }
    } catch (error) {
      let errorMessage: string;
      try {
        const errorData = JSON.parse((error as Error).message);
        errorMessage = errorData.detail;
      } catch {
        errorMessage = (error as Error).message;
      }
      
      return {
        success: false,
        error: errorMessage
      };
    }
  }

  /**
   * Run scenario simulation
   */
  static async runSimulation(formData: ScenarioFormData): Promise<{
    success: boolean;
    result?: ScenarioResponse;
    error?: ErrorResponse | string;
  }> {
    try {
      const scenarioWithData = await this.buildScenarioDefinition(formData);
      
      const result = await scenarioApi.runScenarioDefinition(scenarioWithData);
      
      if (result.status === 'success') {
        return {
          success: true,
          result
        };
      } else {
        return {
          success: false,
          error: result.error_message || 'Simulation failed'
        };
      }
    } catch (error) {
      let parsedError: ErrorResponse | string;
      try {
        parsedError = JSON.parse((error as Error).message);
      } catch {
        parsedError = (error as Error).message;
      }
      
      return {
        success: false,
        error: parsedError
      };
    }
  }

  /**
   * Extract data from component refs safely
   */
  static extractRefData(refs: {
    baselineGridRef?: any;
    leversRef?: any;
  }): {
    baselineData: any;
    leversData: any;
  } {
    let baselineData = {
      global: {
        recruitment: {},
        churn: {}
      }
    };
    
    if (refs.baselineGridRef?.current?.getCurrentData) {
      const gridData = refs.baselineGridRef.current.getCurrentData();
      if (gridData && gridData.global) {
        baselineData = gridData;
      }
    }
    
    let leversData = {};
    if (refs.leversRef?.current?.getCurrentData) {
      leversData = refs.leversRef.current.getCurrentData();
    }
    
    return {
      baselineData,
      leversData
    };
  }
}