import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { scenarioApi } from '../scenarioApi';
import { mockScenarioDefinition, mockScenarioResponse, mockScenarioList } from '../../test/test-utils';

// Mock fetch globally
global.fetch = vi.fn();

describe('ScenarioApiService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('createScenario', () => {
    it('creates a scenario successfully', async () => {
      const mockResponse = { scenario_id: 'test-id' };
      (fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await scenarioApi.createScenario(mockScenarioDefinition);

      expect(fetch).toHaveBeenCalledWith('/api/scenarios/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ scenario_definition: mockScenarioDefinition }),
      });
      expect(result).toEqual(mockResponse);
    });

    it('handles creation error', async () => {
      const errorMessage = 'Failed to create scenario';
      (fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: async () => ({ detail: errorMessage }),
      });

      await expect(scenarioApi.createScenario(mockScenarioDefinition)).rejects.toThrow(errorMessage);
    });
  });

  describe('getScenario', () => {
    it('retrieves a scenario successfully', async () => {
      (fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockScenarioDefinition,
      });

      const result = await scenarioApi.getScenario('test-id');

      expect(fetch).toHaveBeenCalledWith('/api/scenarios/test-id', {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      expect(result).toEqual(mockScenarioDefinition);
    });

    it('handles retrieval error', async () => {
      const errorMessage = 'Scenario not found';
      (fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: async () => ({ detail: errorMessage }),
      });

      await expect(scenarioApi.getScenario('nonexistent-id')).rejects.toThrow(errorMessage);
    });
  });

  describe('listScenarios', () => {
    it('lists scenarios successfully', async () => {
      const mockResponse = { scenarios: mockScenarioList };
      (fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await scenarioApi.listScenarios();

      expect(fetch).toHaveBeenCalledWith('/api/scenarios/list', {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      expect(result).toEqual(mockScenarioList);
    });

    it('handles list error', async () => {
      const errorMessage = 'Failed to list scenarios';
      (fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({ detail: errorMessage }),
      });

      await expect(scenarioApi.listScenarios()).rejects.toThrow(errorMessage);
    });
  });

  describe('updateScenario', () => {
    it('updates a scenario successfully', async () => {
      (fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      });

      await scenarioApi.updateScenario('test-id', mockScenarioDefinition);

      expect(fetch).toHaveBeenCalledWith('/api/scenarios/test-id', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ scenario_definition: mockScenarioDefinition }),
      });
    });

    it('handles update error', async () => {
      const errorMessage = 'Failed to update scenario';
      (fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: async () => ({ detail: errorMessage }),
      });

      await expect(scenarioApi.updateScenario('test-id', mockScenarioDefinition)).rejects.toThrow(errorMessage);
    });
  });

  describe('deleteScenario', () => {
    it('deletes a scenario successfully', async () => {
      (fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      });

      await scenarioApi.deleteScenario('test-id');

      expect(fetch).toHaveBeenCalledWith('/api/scenarios/test-id', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });
    });

    it('handles deletion error', async () => {
      const errorMessage = 'Failed to delete scenario';
      (fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: async () => ({ detail: errorMessage }),
      });

      await expect(scenarioApi.deleteScenario('nonexistent-id')).rejects.toThrow(errorMessage);
    });
  });

  describe('runScenario', () => {
    it('runs a scenario successfully', async () => {
      const request = { scenario_id: 'test-id' };
      (fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockScenarioResponse,
      });

      const result = await scenarioApi.runScenario(request);

      expect(fetch).toHaveBeenCalledWith('/api/scenarios/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });
      expect(result).toEqual(mockScenarioResponse);
    });

    it('handles run error', async () => {
      const request = { scenario_id: 'test-id' };
      const errorMessage = 'Failed to run scenario';
      (fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({ detail: errorMessage }),
      });

      await expect(scenarioApi.runScenario(request)).rejects.toThrow(errorMessage);
    });
  });

  describe('runScenarioById', () => {
    it('runs a scenario by ID successfully', async () => {
      (fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockScenarioResponse,
      });

      const result = await scenarioApi.runScenarioById('test-id', ['Stockholm']);

      expect(fetch).toHaveBeenCalledWith('/api/scenarios/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          scenario_id: 'test-id',
          office_scope: ['Stockholm'],
        }),
      });
      expect(result).toEqual(mockScenarioResponse);
    });
  });

  describe('runScenarioDefinition', () => {
    it('runs a scenario with definition successfully', async () => {
      (fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockScenarioResponse,
      });

      const result = await scenarioApi.runScenarioDefinition(mockScenarioDefinition, ['Stockholm']);

      expect(fetch).toHaveBeenCalledWith('/api/scenarios/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          scenario_definition: mockScenarioDefinition,
          office_scope: ['Stockholm'],
        }),
      });
      expect(result).toEqual(mockScenarioResponse);
    });
  });

  describe('compareScenarios', () => {
    it('compares scenarios successfully', async () => {
      const request = {
        scenario_ids: ['scenario-1', 'scenario-2'],
        comparison_type: 'side_by_side' as const,
      };
      const mockComparisonResponse = {
        comparison_id: 'comp-123',
        scenarios: {},
        comparison_data: {},
        metadata: {},
      };
      (fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockComparisonResponse,
      });

      const result = await scenarioApi.compareScenarios(request);

      expect(fetch).toHaveBeenCalledWith('/api/scenarios/compare', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });
      expect(result).toEqual(mockComparisonResponse);
    });
  });

  describe('compareTwoScenarios', () => {
    it('compares two scenarios successfully', async () => {
      const mockComparisonResponse = {
        comparison_id: 'comp-123',
        scenarios: {},
        comparison_data: {},
        metadata: {},
      };
      (fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockComparisonResponse,
      });

      const result = await scenarioApi.compareTwoScenarios('scenario-1', 'scenario-2', 'overlay');

      expect(fetch).toHaveBeenCalledWith('/api/scenarios/compare', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          scenario_ids: ['scenario-1', 'scenario-2'],
          comparison_type: 'overlay',
        }),
      });
      expect(result).toEqual(mockComparisonResponse);
    });
  });

  describe('getAvailableOffices', () => {
    it('returns available offices', async () => {
      const result = await scenarioApi.getAvailableOffices();

      expect(result).toEqual([
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
        'Group',
      ]);
    });
  });

  describe('validateScenario', () => {
    it('validates scenario successfully', async () => {
      const result = await scenarioApi.validateScenario(mockScenarioDefinition);

      expect(result).toEqual({
        valid: true,
        errors: [],
      });
    });

    it('returns validation errors for invalid scenario', async () => {
      const invalidScenario = {
        ...mockScenarioDefinition,
        name: '',
      };

      const result = await scenarioApi.validateScenario(invalidScenario);

      expect(result).toEqual({
        valid: false,
        errors: ['Scenario name is required'],
      });
    });
  });

  describe('exportScenarioResults', () => {
    it('exports scenario results successfully', async () => {
      const mockBlob = new Blob(['test data']);
      (fetch as any).mockResolvedValueOnce({
        ok: true,
        blob: async () => mockBlob,
      });

      const result = await scenarioApi.exportScenarioResults('test-id');

      expect(fetch).toHaveBeenCalledWith('/api/scenarios/test-id/export', {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      expect(result).toEqual(mockBlob);
    });
  });

  describe('exportComparison', () => {
    it('exports comparison successfully', async () => {
      const mockBlob = new Blob(['test data']);
      (fetch as any).mockResolvedValueOnce({
        ok: true,
        blob: async () => mockBlob,
      });

      const result = await scenarioApi.exportComparison('comp-123');

      expect(fetch).toHaveBeenCalledWith('/api/scenarios/compare/comp-123/export', {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      expect(result).toEqual(mockBlob);
    });
  });

  describe('error handling', () => {
    it('handles network errors', async () => {
      (fetch as any).mockRejectedValueOnce(new Error('Network error'));

      await expect(scenarioApi.listScenarios()).rejects.toThrow('Network error');
    });

    it('handles JSON parsing errors', async () => {
      (fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => {
          throw new Error('Invalid JSON');
        },
      });

      await expect(scenarioApi.listScenarios()).rejects.toThrow('HTTP 500: Internal Server Error');
    });

    it('handles missing error detail', async () => {
      (fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({}),
      });

      await expect(scenarioApi.listScenarios()).rejects.toThrow('HTTP 500: Internal Server Error');
    });
  });
}); 