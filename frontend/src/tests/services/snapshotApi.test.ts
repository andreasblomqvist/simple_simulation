/**
 * Unit tests for snapshot API service
 * Tests HTTP client, error handling, data formatting, and utility functions
 */

import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { snapshotApi, SnapshotApiService, snapshotUtils } from '../../services/snapshotApi';
import type { 
  PopulationSnapshot,
  CreateSnapshotRequest,
  UpdateSnapshotRequest,
  ListSnapshotsRequest,
  CompareSnapshotsRequest,
  SnapshotAPIError
} from '../../types/snapshots';

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Test data
const mockSnapshot: PopulationSnapshot = {
  id: 'snapshot-1',
  name: 'Test Snapshot',
  description: 'Test description',
  office_id: 'office-1',
  snapshot_date: '2025-03-31T14:30:00Z',
  workforce: [
    { role: 'Consultant', level: 'A', fte: 10, salary: 4500 },
    { role: 'Consultant', level: 'AC', fte: 8, salary: 6000 },
    { role: 'Operations', level: null, fte: 5, salary: 3500 },
  ],
  metadata: {
    total_fte: 23,
    total_salary_cost: 122500,
    role_count: 2,
  },
  created_at: '2025-01-15T10:30:00Z',
  updated_at: '2025-01-15T10:30:00Z',
};

const mockSnapshot2: PopulationSnapshot = {
  id: 'snapshot-2',
  name: 'Test Snapshot 2',
  description: 'Second test snapshot',
  office_id: 'office-1',
  snapshot_date: '2025-06-30T14:30:00Z',
  workforce: [
    { role: 'Consultant', level: 'A', fte: 12, salary: 4500 },
    { role: 'Consultant', level: 'AC', fte: 10, salary: 6000 },
    { role: 'Operations', level: null, fte: 7, salary: 3500 },
  ],
  metadata: {
    total_fte: 29,
    total_salary_cost: 138500,
    role_count: 2,
  },
  created_at: '2025-01-20T10:30:00Z',
  updated_at: '2025-01-20T10:30:00Z',
};

describe('SnapshotApiService', () => {
  let apiService: SnapshotApiService;

  beforeEach(() => {
    apiService = new SnapshotApiService();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('Response Handling', () => {
    it('handles successful JSON response', async () => {
      const mockData = { test: 'data' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify(mockData)),
      });

      const result = await apiService['handleResponse'](await fetch('/test'));
      expect(result).toEqual(mockData);
    });

    it('handles empty response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(''),
      });

      const result = await apiService['handleResponse'](await fetch('/test'));
      expect(result).toEqual({});
    });

    it('throws error for HTTP error status', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: () => Promise.resolve('Resource not found'),
      });

      await expect(apiService['handleResponse'](await fetch('/test')))
        .rejects.toThrow('Resource not found');
    });

    it('handles structured error response', async () => {
      const errorData = { detail: 'Validation failed', code: 'VALIDATION_ERROR' };
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        text: () => Promise.resolve(JSON.stringify(errorData)),
      });

      try {
        await apiService['handleResponse'](await fetch('/test'));
      } catch (error) {
        expect(error.message).toBe('Validation failed');
        expect((error as SnapshotAPIError).status).toBe(400);
        expect((error as SnapshotAPIError).name).toBe('SnapshotAPIError');
      }
    });

    it('handles invalid JSON response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve('invalid json {'),
      });

      await expect(apiService['handleResponse'](await fetch('/test')))
        .rejects.toThrow('Invalid JSON response');
    });

    it('handles network errors gracefully', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: () => Promise.reject(new Error('Network error')),
      });

      await expect(apiService['handleResponse'](await fetch('/test')))
        .rejects.toThrow('HTTP 500: Internal Server Error');
    });
  });

  describe('List Snapshots', () => {
    it('lists snapshots without parameters', async () => {
      const mockResponse = {
        snapshots: [mockSnapshot],
        total: 1,
        offset: 0,
        limit: 50,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify(mockResponse)),
      });

      const result = await apiService.listSnapshots();

      expect(mockFetch).toHaveBeenCalledWith('/api/snapshots/?');
      expect(result).toEqual(mockResponse);
    });

    it('lists snapshots with all parameters', async () => {
      const params: ListSnapshotsRequest = {
        office_id: 'office-1',
        limit: 10,
        offset: 20,
        sort_by: 'created_at',
        sort_order: 'desc',
        search: 'test query',
        tags: ['quarterly', 'approved'],
      };

      const mockResponse = {
        snapshots: [mockSnapshot],
        total: 1,
        offset: 20,
        limit: 10,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify(mockResponse)),
      });

      const result = await apiService.listSnapshots(params);

      expect(mockFetch).toHaveBeenCalledWith(
        '/api/snapshots/?office_id=office-1&limit=10&offset=20&sort_by=created_at&sort_order=desc&search=test+query&tags=quarterly%2Capproved'
      );
      expect(result).toEqual(mockResponse);
    });

    it('handles empty tags array', async () => {
      const params: ListSnapshotsRequest = {
        tags: [],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify({ snapshots: [], total: 0, offset: 0, limit: 50 })),
      });

      await apiService.listSnapshots(params);

      expect(mockFetch).toHaveBeenCalledWith('/api/snapshots/?');
    });

    it('handles special characters in search', async () => {
      const params: ListSnapshotsRequest = {
        search: 'test & query with spaces',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify({ snapshots: [], total: 0, offset: 0, limit: 50 })),
      });

      await apiService.listSnapshots(params);

      expect(mockFetch).toHaveBeenCalledWith('/api/snapshots/?search=test+%26+query+with+spaces');
    });
  });

  describe('Get Snapshots by Office', () => {
    it('gets snapshots for specific office', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify([mockSnapshot])),
      });

      const result = await apiService.getSnapshotsByOffice('office-1');

      expect(mockFetch).toHaveBeenCalledWith('/api/snapshots/office/office-1');
      expect(result).toEqual([mockSnapshot]);
    });

    it('handles empty office snapshots', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify([])),
      });

      const result = await apiService.getSnapshotsByOffice('office-1');

      expect(result).toEqual([]);
    });
  });

  describe('Get Single Snapshot', () => {
    it('gets snapshot by ID', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify(mockSnapshot)),
      });

      const result = await apiService.getSnapshot('snapshot-1');

      expect(mockFetch).toHaveBeenCalledWith('/api/snapshots/snapshot-1');
      expect(result).toEqual(mockSnapshot);
    });

    it('handles snapshot not found', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: () => Promise.resolve('Snapshot not found'),
      });

      await expect(apiService.getSnapshot('nonexistent-id'))
        .rejects.toThrow('Snapshot not found');
    });
  });

  describe('Create Snapshot', () => {
    it('creates snapshot successfully', async () => {
      const createRequest: CreateSnapshotRequest = {
        name: 'New Snapshot',
        office_id: 'office-1',
        description: 'Test snapshot creation',
        tags: ['test'],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify(mockSnapshot)),
      });

      const result = await apiService.createSnapshot(createRequest);

      expect(mockFetch).toHaveBeenCalledWith('/api/snapshots', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(createRequest),
      });
      expect(result).toEqual(mockSnapshot);
    });

    it('handles create validation error', async () => {
      const createRequest: CreateSnapshotRequest = {
        name: '',
        office_id: 'office-1',
      };

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 422,
        statusText: 'Unprocessable Entity',
        text: () => Promise.resolve(JSON.stringify({
          detail: 'Name is required'
        })),
      });

      await expect(apiService.createSnapshot(createRequest))
        .rejects.toThrow('Name is required');
    });
  });

  describe('Update Snapshot', () => {
    it('updates snapshot successfully', async () => {
      const updateRequest: UpdateSnapshotRequest = {
        name: 'Updated Name',
        description: 'Updated description',
      };

      const updatedSnapshot = { ...mockSnapshot, ...updateRequest };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify(updatedSnapshot)),
      });

      const result = await apiService.updateSnapshot('snapshot-1', updateRequest);

      expect(mockFetch).toHaveBeenCalledWith('/api/snapshots/snapshot-1', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateRequest),
      });
      expect(result).toEqual(updatedSnapshot);
    });

    it('handles update error', async () => {
      const updateRequest: UpdateSnapshotRequest = {
        name: 'Updated Name',
      };

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        text: () => Promise.resolve('Update failed'),
      });

      await expect(apiService.updateSnapshot('snapshot-1', updateRequest))
        .rejects.toThrow('Update failed');
    });
  });

  describe('Delete Snapshot', () => {
    it('deletes snapshot successfully', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(''),
      });

      await apiService.deleteSnapshot('snapshot-1');

      expect(mockFetch).toHaveBeenCalledWith('/api/snapshots/snapshot-1', {
        method: 'DELETE',
      });
    });

    it('handles delete error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: () => Promise.resolve('Snapshot not found'),
      });

      await expect(apiService.deleteSnapshot('nonexistent-id'))
        .rejects.toThrow('Snapshot not found');
    });
  });

  describe('Compare Snapshots', () => {
    it('compares snapshots successfully', async () => {
      const compareRequest: CompareSnapshotsRequest = {
        baseline_id: 'snapshot-1',
        comparison_id: 'snapshot-2',
      };

      const mockComparison = {
        baseline: mockSnapshot,
        comparison: mockSnapshot2,
        workforce_changes: [
          {
            role: 'Consultant',
            level: 'A',
            change_type: 'modified' as const,
            baseline_fte: 10,
            comparison_fte: 12,
            fte_change: 2,
            salary_change: 9000,
          },
        ],
        summary: {
          total_fte_change: 6,
          total_salary_change: 16000,
          roles_added: 0,
          roles_removed: 0,
          roles_modified: 2,
          net_change_percentage: 26.1,
        },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify(mockComparison)),
      });

      const result = await apiService.compareSnapshots(compareRequest);

      expect(mockFetch).toHaveBeenCalledWith('/api/snapshots/compare', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(compareRequest),
      });
      expect(result).toEqual(mockComparison);
    });

    it('handles comparison error', async () => {
      const compareRequest: CompareSnapshotsRequest = {
        baseline_id: 'snapshot-1',
        comparison_id: 'nonexistent',
      };

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: () => Promise.resolve('One or both snapshots not found'),
      });

      await expect(apiService.compareSnapshots(compareRequest))
        .rejects.toThrow('One or both snapshots not found');
    });
  });

  describe('Get Tags', () => {
    it('gets all tags', async () => {
      const mockTags = ['quarterly', 'approved', 'baseline', 'simulation'];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify(mockTags)),
      });

      const result = await apiService.getTags();

      expect(mockFetch).toHaveBeenCalledWith('/api/snapshots/tags?');
      expect(result).toEqual(mockTags);
    });

    it('gets tags for specific office', async () => {
      const mockTags = ['quarterly', 'approved'];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify(mockTags)),
      });

      const result = await apiService.getTags('office-1');

      expect(mockFetch).toHaveBeenCalledWith('/api/snapshots/tags?office_id=office-1');
      expect(result).toEqual(mockTags);
    });
  });

  describe('Export Snapshot', () => {
    it('exports snapshot as CSV', async () => {
      const mockBlob = new Blob(['csv,data'], { type: 'text/csv' });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        blob: () => Promise.resolve(mockBlob),
      });

      const result = await apiService.exportSnapshot('snapshot-1', 'csv');

      expect(mockFetch).toHaveBeenCalledWith('/api/snapshots/snapshot-1/export?format=csv');
      expect(result).toEqual(mockBlob);
    });

    it('exports snapshot as JSON', async () => {
      const mockBlob = new Blob(['{"data": "json"}'], { type: 'application/json' });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        blob: () => Promise.resolve(mockBlob),
      });

      const result = await apiService.exportSnapshot('snapshot-1', 'json');

      expect(mockFetch).toHaveBeenCalledWith('/api/snapshots/snapshot-1/export?format=json');
      expect(result).toEqual(mockBlob);
    });

    it('handles export error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        text: () => Promise.resolve('Snapshot not found'),
      });

      await expect(apiService.exportSnapshot('nonexistent-id'))
        .rejects.toThrow('Export failed: Snapshot not found');
    });
  });

  describe('Get Snapshot Stats', () => {
    it('gets office snapshot statistics', async () => {
      const mockStats = {
        total_snapshots: 5,
        latest_snapshot: mockSnapshot,
        avg_fte: 23.4,
        fte_trend: 12.5,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify(mockStats)),
      });

      const result = await apiService.getSnapshotStats('office-1');

      expect(mockFetch).toHaveBeenCalledWith('/api/snapshots/office/office-1/stats');
      expect(result).toEqual(mockStats);
    });
  });

  describe('Validate Snapshot', () => {
    it('validates snapshot data successfully', async () => {
      const createRequest: CreateSnapshotRequest = {
        name: 'Valid Snapshot',
        office_id: 'office-1',
      };

      const mockValidation = {
        is_valid: true,
        errors: [],
        warnings: ['Consider adding description'],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify(mockValidation)),
      });

      const result = await apiService.validateSnapshot(createRequest);

      expect(mockFetch).toHaveBeenCalledWith('/api/snapshots/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(createRequest),
      });
      expect(result).toEqual(mockValidation);
    });

    it('returns validation errors', async () => {
      const createRequest: CreateSnapshotRequest = {
        name: '',
        office_id: 'invalid-office',
      };

      const mockValidation = {
        is_valid: false,
        errors: ['Name is required', 'Office does not exist'],
        warnings: [],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify(mockValidation)),
      });

      const result = await apiService.validateSnapshot(createRequest);

      expect(result).toEqual(mockValidation);
      expect(result.is_valid).toBe(false);
      expect(result.errors).toHaveLength(2);
    });
  });
});

describe('Snapshot API Singleton', () => {
  it('exports singleton instance', () => {
    expect(snapshotApi).toBeInstanceOf(SnapshotApiService);
  });

  it('singleton methods work correctly', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      text: () => Promise.resolve(JSON.stringify([mockSnapshot])),
    });

    const result = await snapshotApi.getSnapshotsByOffice('office-1');
    expect(result).toEqual([mockSnapshot]);
  });
});

describe('Snapshot Utils', () => {
  describe('formatDate', () => {
    it('formats date correctly', () => {
      const dateString = '2025-03-15T14:30:00Z';
      const formatted = snapshotUtils.formatDate(dateString);
      
      expect(formatted).toMatch(/Mar 15, 2025/);
      expect(formatted).toMatch(/\d{2}:\d{2}/); // Should include time
    });

    it('handles invalid dates gracefully', () => {
      const invalidDate = 'invalid-date';
      
      expect(() => snapshotUtils.formatDate(invalidDate)).not.toThrow();
    });
  });

  describe('formatFTE', () => {
    it('formats FTE with one decimal place', () => {
      expect(snapshotUtils.formatFTE(23.456)).toBe('23.5');
      expect(snapshotUtils.formatFTE(10)).toBe('10.0');
      expect(snapshotUtils.formatFTE(0)).toBe('0.0');
    });

    it('handles edge cases', () => {
      expect(snapshotUtils.formatFTE(0.1)).toBe('0.1');
      expect(snapshotUtils.formatFTE(999.999)).toBe('1000.0');
    });
  });

  describe('formatSalary', () => {
    it('formats salary as EUR currency', () => {
      expect(snapshotUtils.formatSalary(4500)).toMatch(/€4,500|4.500/); // Different locales
      expect(snapshotUtils.formatSalary(1000000)).toMatch(/€1,000,000|1.000.000/);
    });

    it('handles zero and negative values', () => {
      expect(snapshotUtils.formatSalary(0)).toMatch(/€0/);
      expect(snapshotUtils.formatSalary(-100)).toMatch(/-€100|€-100/);
    });
  });

  describe('formatChange', () => {
    it('formats positive changes with plus sign', () => {
      expect(snapshotUtils.formatChange(5.7)).toBe('+5.7');
      expect(snapshotUtils.formatChange(15.3, true)).toBe('+15.3%');
    });

    it('formats negative changes', () => {
      expect(snapshotUtils.formatChange(-3.2)).toBe('-3.2');
      expect(snapshotUtils.formatChange(-8.9, true)).toBe('-8.9%');
    });

    it('handles zero change', () => {
      expect(snapshotUtils.formatChange(0)).toBe('+0.0');
      expect(snapshotUtils.formatChange(0, true)).toBe('+0.0%');
    });
  });

  describe('calculateTotalFTE', () => {
    it('calculates total FTE correctly', () => {
      const workforce = [
        { fte: 10.5 },
        { fte: 8.0 },
        { fte: 5.5 },
      ];

      expect(snapshotUtils.calculateTotalFTE(workforce)).toBe(24);
    });

    it('handles empty workforce', () => {
      expect(snapshotUtils.calculateTotalFTE([])).toBe(0);
    });

    it('handles decimal precision', () => {
      const workforce = [
        { fte: 0.1 },
        { fte: 0.2 },
        { fte: 0.3 },
      ];

      expect(snapshotUtils.calculateTotalFTE(workforce)).toBeCloseTo(0.6);
    });
  });

  describe('calculateTotalSalaryCost', () => {
    it('calculates total salary cost correctly', () => {
      const workforce = [
        { fte: 2, salary: 5000 }, // 10,000
        { fte: 1.5, salary: 4000 }, // 6,000
        { fte: 3, salary: 6000 }, // 18,000
      ];

      expect(snapshotUtils.calculateTotalSalaryCost(workforce)).toBe(34000);
    });

    it('handles empty workforce', () => {
      expect(snapshotUtils.calculateTotalSalaryCost([])).toBe(0);
    });

    it('handles zero values', () => {
      const workforce = [
        { fte: 0, salary: 5000 },
        { fte: 2, salary: 0 },
        { fte: 1, salary: 3000 },
      ];

      expect(snapshotUtils.calculateTotalSalaryCost(workforce)).toBe(3000);
    });
  });

  describe('groupByRole', () => {
    it('groups workforce by role correctly', () => {
      const workforce = [
        { role: 'Consultant', level: 'A', fte: 10 },
        { role: 'Consultant', level: 'AC', fte: 8 },
        { role: 'Operations', level: null, fte: 5 },
        { role: 'Consultant', level: 'C', fte: 6 },
      ];

      const grouped = snapshotUtils.groupByRole(workforce);

      expect(grouped).toEqual({
        Consultant: [
          { level: 'A', fte: 10 },
          { level: 'AC', fte: 8 },
          { level: 'C', fte: 6 },
        ],
        Operations: [
          { level: null, fte: 5 },
        ],
      });
    });

    it('handles empty workforce', () => {
      expect(snapshotUtils.groupByRole([])).toEqual({});
    });

    it('handles single role', () => {
      const workforce = [
        { role: 'Manager', level: 'M1', fte: 3 },
      ];

      const grouped = snapshotUtils.groupByRole(workforce);

      expect(grouped).toEqual({
        Manager: [
          { level: 'M1', fte: 3 },
        ],
      });
    });
  });

  describe('generateSummary', () => {
    it('generates correct summary', () => {
      const summary = snapshotUtils.generateSummary(mockSnapshot);
      
      expect(summary).toContain('23.0 FTE');
      expect(summary).toContain('2 roles');
      expect(summary).toMatch(/Mar \d+, 2025/);
    });

    it('handles zero values', () => {
      const zeroSnapshot = {
        ...mockSnapshot,
        metadata: {
          total_fte: 0,
          total_salary_cost: 0,
          role_count: 0,
        },
      };

      const summary = snapshotUtils.generateSummary(zeroSnapshot);
      
      expect(summary).toContain('0.0 FTE');
      expect(summary).toContain('0 roles');
    });

    it('handles fractional values', () => {
      const fractionalSnapshot = {
        ...mockSnapshot,
        metadata: {
          total_fte: 23.7,
          total_salary_cost: 122500,
          role_count: 2,
        },
      };

      const summary = snapshotUtils.generateSummary(fractionalSnapshot);
      
      expect(summary).toContain('23.7 FTE');
    });
  });

  describe('Utility Function Edge Cases', () => {
    it('handles very large numbers', () => {
      const largeNumber = 999999999.99;
      
      expect(snapshotUtils.formatFTE(largeNumber)).toBe('1000000000.0');
      expect(snapshotUtils.formatSalary(largeNumber)).toMatch(/€1,000,000,000|1.000.000.000/);
    });

    it('handles very small numbers', () => {
      const smallNumber = 0.001;
      
      expect(snapshotUtils.formatFTE(smallNumber)).toBe('0.0');
      expect(snapshotUtils.formatChange(smallNumber)).toBe('+0.0');
    });

    it('handles NaN and Infinity', () => {
      expect(snapshotUtils.formatFTE(NaN)).toBe('NaN');
      expect(snapshotUtils.formatFTE(Infinity)).toBe('Infinity');
      expect(snapshotUtils.formatChange(NaN)).toBe('+NaN');
    });

    it('handles undefined and null gracefully', () => {
      expect(() => snapshotUtils.calculateTotalFTE(null as any)).toThrow();
      expect(() => snapshotUtils.calculateTotalSalaryCost(undefined as any)).toThrow();
    });
  });
});