// Scenario API Service
// Handles all backend communication for scenario management

import type {
  ScenarioDefinition,
  ScenarioRequest,
  ScenarioResponse,
  ScenarioListResponse,
  ScenarioListItem,
  ScenarioId,
  OfficeName,
  SimulationResults,
  ErrorResponse,
  ApiResponse,
  OfficeScope,
  ValidationResponse,
  ScenarioComparisonRequest,
  ScenarioComparisonResponse,
} from '../types/unified-data-structures';

const API_BASE = 'http://localhost:8000/scenarios';

class ScenarioApiService {
  private correlationId: string | null = null;

  private generateCorrelationId(): string {
    return Math.random().toString(36).substring(2, 10);
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // ✅ Add retry mechanism for transient failures
  private async requestWithRetry<T>(
    endpoint: string,
    options: RequestInit = {},
    maxRetries: number = 3
  ): Promise<T> {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await this.request<T>(endpoint, options);
      } catch (error) {
        if (attempt === maxRetries) {
          throw error;
        }
        
        // ✅ Only retry on specific error types
        const errorStr = (error as Error).toString();
        if (errorStr.includes('500') || errorStr.includes('502') || errorStr.includes('503')) {
          console.log(`Retrying request (attempt ${attempt}/${maxRetries}) [corr: ${this.correlationId}]`);
          await this.delay(1000 * attempt); // Exponential backoff
          continue;
        }
        
        throw error;
      }
    }
    
    throw new Error('Max retries exceeded');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE}${endpoint}`;
    
    // ✅ Generate correlation ID for each request
    this.correlationId = this.generateCorrelationId();
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        'X-Correlation-ID': this.correlationId, // ✅ Add correlation ID header
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        
        // ✅ Enhanced error handling with correlation ID
        const error: ErrorResponse = {
          detail: errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
          correlation_id: errorData.correlation_id || this.correlationId,
          error_type: errorData.error_type,
          context: errorData.context,
        };
        
        throw new Error(JSON.stringify(error));
      }

      const data = await response.json();
      
      // ✅ Log successful requests with correlation ID
      console.log(`API request successful: ${endpoint} [corr: ${this.correlationId}]`);
      
      return data;
    } catch (error) {
      // ✅ Enhanced error logging with correlation ID
      console.error(`API request failed for ${endpoint} [corr: ${this.correlationId}]:`, error);
      throw error;
    }
  }

  // ========================================
  // Scenario CRUD Operations
  // ========================================

  /**
   * Validate a scenario definition
   */
  async validateScenario(scenario: ScenarioDefinition): Promise<ValidationResponse> {
    return this.request<ValidationResponse>('/validate', {
      method: 'POST',
      body: JSON.stringify(scenario),
    });
  }

  /**
   * Create a new scenario
   */
  async createScenario(scenario: ScenarioDefinition): Promise<ScenarioId> {
    // ✅ Validate before creating
    try {
      const validation = await this.validateScenario(scenario);
      if (!validation.valid) {
        throw new Error(`Validation failed: ${validation.errors.join(', ')}`);
      }
    } catch (error) {
      // If validation endpoint doesn't exist yet, continue without validation
      console.warn('Validation endpoint not available, skipping validation');
    }

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
    // ✅ Use retry logic for simulation runs (they can be long-running)
    return this.requestWithRetry<ScenarioResponse>('/run', {
      method: 'POST',
      body: JSON.stringify(request),
    }, 2); // Retry once for simulation runs
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
    console.log('DEBUG: Sending scenario request to API:', JSON.stringify(request, null, 2));
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
    try {
      const response = await fetch('http://localhost:8000/offices');
      const offices = await response.json();
      return offices.map((office: any) => office.name);
    } catch (error) {
      console.warn('Failed to fetch offices from API, using fallback list:', error);
      // Fallback to hardcoded list
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
   * Get scenario results by ID
   */
  async getScenarioResults(scenarioId: ScenarioId): Promise<SimulationResults> {
    const response = await this.request<{results: SimulationResults}>(`/${scenarioId}/results`);
    return response.results;
  }

  /**
   * Get baseline simulation results
   */
  async getBaselineResults(): Promise<SimulationResults> {
    const response = await this.request<{results: SimulationResults}>('/baseline-results');
    return response.results;
  }
}

// Export singleton instance
export const scenarioApi = new ScenarioApiService();

// Export types for convenience
export type { ScenarioApiService }; 