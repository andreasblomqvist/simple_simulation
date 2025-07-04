// Scenario API Service
// Handles all backend communication for scenario management

import type {
  ScenarioDefinition,
  ScenarioRequest,
  ScenarioResponse,
  ScenarioListResponse,
  ScenarioListItem,
  ScenarioComparisonRequest,
  ScenarioComparisonResponse,
  ScenarioId,
  OfficeName,
  SimulationResults,
} from '../types/scenarios';

const API_BASE = '/api/scenarios';

class ScenarioApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE}${endpoint}`;
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // ========================================
  // Scenario CRUD Operations
  // ========================================

  /**
   * Create a new scenario
   */
  async createScenario(scenario: ScenarioDefinition): Promise<ScenarioId> {
    const response = await this.request<{scenario_id: string}>('/create', {
      method: 'POST',
      body: JSON.stringify(scenario),
    });
    return response.scenario_id;
  }

  /**
   * Get a scenario by ID
   */
  async getScenario(scenarioId: ScenarioId): Promise<ScenarioDefinition> {
    return this.request<ScenarioDefinition>(`/${scenarioId}`);
  }

  /**
   * List all scenarios
   */
  async listScenarios(): Promise<ScenarioListItem[]> {
    const response = await this.request<ScenarioListResponse>('/list');
    return response.scenarios;
  }

  /**
   * Update an existing scenario
   */
  async updateScenario(scenarioId: ScenarioId, scenario: ScenarioDefinition): Promise<void> {
    return this.request<void>(`/${scenarioId}`, {
      method: 'PUT',
      body: JSON.stringify(scenario),
    });
  }

  /**
   * Delete a scenario
   */
  async deleteScenario(scenarioId: ScenarioId): Promise<void> {
    return this.request<void>(`/${scenarioId}`, {
      method: 'DELETE',
    });
  }

  // ========================================
  // Scenario Execution
  // ========================================

  /**
   * Run a scenario simulation
   */
  async runScenario(request: ScenarioRequest): Promise<ScenarioResponse> {
    return this.request<ScenarioResponse>('/run', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * Run a scenario by ID
   */
  async runScenarioById(scenarioId: ScenarioId, officeScope?: OfficeName[]): Promise<ScenarioResponse> {
    const request: ScenarioRequest = {
      scenario_id: scenarioId,
      office_scope: officeScope,
    };
    return this.runScenario(request);
  }

  /**
   * Run a scenario with definition
   */
  async runScenarioDefinition(scenario: ScenarioDefinition, officeScope?: OfficeName[]): Promise<ScenarioResponse> {
    const request: ScenarioRequest = {
      scenario_definition: scenario,
      office_scope: officeScope,
    };
    return this.runScenario(request);
  }

  // ========================================
  // Scenario Comparison
  // ========================================

  /**
   * Compare multiple scenarios
   */
  async compareScenarios(request: ScenarioComparisonRequest): Promise<ScenarioComparisonResponse> {
    return this.request<ScenarioComparisonResponse>('/compare', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * Compare two scenarios side by side
   */
  async compareTwoScenarios(
    scenarioId1: ScenarioId,
    scenarioId2: ScenarioId,
    comparisonType: 'side_by_side' | 'overlay' | 'difference' = 'side_by_side'
  ): Promise<ScenarioComparisonResponse> {
    const request: ScenarioComparisonRequest = {
      scenario_ids: [scenarioId1, scenarioId2],
      comparison_type: comparisonType,
    };
    return this.compareScenarios(request);
  }

  // ========================================
  // Utility Methods
  // ========================================

  /**
   * Get available offices for scenario scope
   */
  async getAvailableOffices(): Promise<OfficeName[]> {
    // This would typically come from a configuration endpoint
    // For now, return a hardcoded list based on the backend config
    return [
      'Stockholm',
      'Munich',
      'Amsterdam',
      'Berlin',
      'Copenhagen',
      'Frankfurt',
      'Hamburg',
      'Helsinki',
      'Oslo',
      'Zurich',
      'Colombia',
      'Group'
    ];
  }

  /**
   * Validate scenario definition before saving
   */
  async validateScenario(scenario: ScenarioDefinition): Promise<{ valid: boolean; errors: string[] }> {
    try {
      // For now, do basic client-side validation
      const errors: string[] = [];

      if (!scenario.name.trim()) {
        errors.push('Scenario name is required');
      }

      if (!scenario.time_range) {
        errors.push('Time range is required');
      } else {
        const { start_year, start_month, end_year, end_month } = scenario.time_range;
        if (start_year > end_year || (start_year === end_year && start_month > end_month)) {
          errors.push('End date must be after start date');
        }
      }

      if (!scenario.office_scope || scenario.office_scope.length === 0) {
        errors.push('At least one office must be selected');
      }

      if (!scenario.levers || Object.keys(scenario.levers).length === 0) {
        errors.push('At least one lever must be configured');
      }

      return {
        valid: errors.length === 0,
        errors,
      };
    } catch (error) {
      return {
        valid: false,
        errors: ['Validation failed: ' + (error as Error).message],
      };
    }
  }

  /**
   * Export scenario results to Excel
   */
  async exportScenarioResults(scenarioId: ScenarioId): Promise<Blob> {
    const response = await fetch(`${API_BASE}/${scenarioId}/export/excel`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error(`Export failed: ${response.statusText}`);
    }

    return response.blob();
  }

  /**
   * Export scenario comparison to Excel
   */
  async exportComparison(comparisonId: string): Promise<Blob> {
    const response = await fetch(`${API_BASE}/compare/${comparisonId}/export`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error(`Export failed: ${response.statusText}`);
    }

    return response.blob();
  }

  /**
   * Get baseline simulation results
   */
  async getBaselineResults(): Promise<SimulationResults> {
    return this.request<SimulationResults>('/baseline-results');
  }
}

// Export singleton instance
export const scenarioApi = new ScenarioApiService();

// Export types for convenience
export type { ScenarioApiService }; 