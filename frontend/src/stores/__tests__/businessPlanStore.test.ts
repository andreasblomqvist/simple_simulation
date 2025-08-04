/**
 * Unit tests for business plan store
 * Tests business plan state management and API interactions
 */
import { describe, it, expect, beforeEach, vi, Mock } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useBusinessPlanStore } from '../businessPlanStore';

// Mock fetch globally
global.fetch = vi.fn();

const mockBusinessPlansResponse = [
  {
    id: 'plan-2025-01',
    office_id: 'stockholm',
    year: 2025,
    month: 1,
    planned_fte: 680,
    planned_revenue: 1200000,
    planned_costs: 800000,
    workforce_entries: [
      {
        role: 'Consultant',
        level: 'A',
        fte: 70,
        notes: 'Growth focus',
      },
      {
        role: 'Consultant',
        level: 'AC',
        fte: 55,
        notes: 'Stable headcount',
      },
    ],
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
  },
  {
    id: 'plan-2025-02',
    office_id: 'stockholm',
    year: 2025,
    month: 2,
    planned_fte: 685,
    planned_revenue: 1250000,
    planned_costs: 820000,
    workforce_entries: [
      {
        role: 'Consultant',
        level: 'A',
        fte: 72,
        notes: 'Continued growth',
      },
      {
        role: 'Consultant',
        level: 'AC',
        fte: 55,
        notes: 'Stable headcount',
      },
    ],
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-15T00:00:00Z',
  },
];

const mockWorkforceDistribution = {
  office_id: 'stockholm',
  start_date: '2025-01-01',
  workforce: [
    {
      role: 'Consultant',
      level: 'A',
      fte: 69,
      notes: 'Current baseline',
    },
    {
      role: 'Consultant',
      level: 'AC',
      fte: 54,
      notes: 'Current baseline',
    },
    {
      role: 'Consultant',
      level: 'C',
      fte: 123,
      notes: 'Current baseline',
    },
  ],
};

const mockOfficeSummary = {
  office_id: 'stockholm',
  monthly_plans: mockBusinessPlansResponse,
  workforce_distribution: mockWorkforceDistribution,
};

describe('Business Plan Store', () => {
  beforeEach(() => {
    // Reset the store state before each test
    const { setState } = useBusinessPlanStore;
    setState({
      monthlyPlans: [],
      workforceDistributions: [],
      currentPlan: null,
      currentWorkforce: null,
      loading: false,
      error: null,
      selectedYear: 2025,
      selectedMonth: 1,
    });
    
    // Reset mocks
    vi.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const { result } = renderHook(() => useBusinessPlanStore());
      
      expect(result.current.monthlyPlans).toEqual([]);
      expect(result.current.workforceDistributions).toEqual([]);
      expect(result.current.currentPlan).toBeNull();
      expect(result.current.currentWorkforce).toBeNull();
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.selectedYear).toBe(2025);
      expect(result.current.selectedMonth).toBe(1);
    });
  });

  describe('loadBusinessPlans', () => {
    it('should load business plans successfully', async () => {
      (fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockBusinessPlansResponse,
      });

      const { result } = renderHook(() => useBusinessPlanStore());

      await act(async () => {
        await result.current.loadBusinessPlans('stockholm');
      });

      expect(fetch).toHaveBeenCalledWith('/api/business-plans?office_id=stockholm');
      expect(result.current.monthlyPlans).toHaveLength(2);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('should load business plans for specific year', async () => {
      (fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockBusinessPlansResponse,
      });

      const { result } = renderHook(() => useBusinessPlanStore());

      await act(async () => {
        await result.current.loadBusinessPlans('stockholm', 2025);
      });

      expect(fetch).toHaveBeenCalledWith('/api/business-plans?office_id=stockholm&year=2025');
      expect(result.current.monthlyPlans).toHaveLength(2);
    });

    it('should handle API errors gracefully', async () => {
      (fetch as Mock).mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useBusinessPlanStore());

      await act(async () => {
        await result.current.loadBusinessPlans('stockholm');
      });

      expect(result.current.monthlyPlans).toEqual([]);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBe('Failed to load business plans: Network error');
    });

    it('should set loading state correctly', async () => {
      let resolvePromise: (value: any) => void;
      const promise = new Promise(resolve => {
        resolvePromise = resolve;
      });

      (fetch as Mock).mockReturnValueOnce(promise);

      const { result } = renderHook(() => useBusinessPlanStore());

      const loadPromise = act(async () => {
        result.current.loadBusinessPlans('stockholm');
      });

      // Check loading state is set
      expect(result.current.loading).toBe(true);

      // Resolve the promise
      resolvePromise!({
        ok: true,
        json: async () => mockBusinessPlansResponse,
      });

      await loadPromise;

      // Check loading state is reset
      expect(result.current.loading).toBe(false);
    });
  });

  describe('loadWorkforceDistribution', () => {
    it('should load workforce distribution successfully', async () => {
      (fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockWorkforceDistribution,
      });

      const { result } = renderHook(() => useBusinessPlanStore());

      await act(async () => {
        await result.current.loadWorkforceDistribution('stockholm');
      });

      expect(fetch).toHaveBeenCalledWith('/api/offices/stockholm/workforce-distribution');
      expect(result.current.currentWorkforce).toEqual(mockWorkforceDistribution);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('should handle API errors gracefully', async () => {
      (fetch as Mock).mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useBusinessPlanStore());

      await act(async () => {
        await result.current.loadWorkforceDistribution('stockholm');
      });

      expect(result.current.currentWorkforce).toBeNull();
      expect(result.current.error).toBe('Failed to load workforce distribution: Network error');
    });
  });

  describe('loadOfficeSummary', () => {
    it('should load office summary successfully', async () => {
      (fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockOfficeSummary,
      });

      const { result } = renderHook(() => useBusinessPlanStore());

      let summary;
      await act(async () => {
        summary = await result.current.loadOfficeSummary('stockholm');
      });

      expect(fetch).toHaveBeenCalledWith('/api/offices/stockholm/summary');
      expect(summary).toEqual(mockOfficeSummary);
      expect(result.current.monthlyPlans).toEqual(mockBusinessPlansResponse);
      expect(result.current.currentWorkforce).toEqual(mockWorkforceDistribution);
    });

    it('should handle API errors gracefully', async () => {
      (fetch as Mock).mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useBusinessPlanStore());

      await expect(async () => {
        await result.current.loadOfficeSummary('stockholm');
      }).rejects.toThrow('Failed to load office summary: Network error');

      expect(result.current.error).toBe('Failed to load office summary: Network error');
    });
  });

  describe('Business Plan Management', () => {
    it('should create business plan successfully', async () => {
      const newPlan = {
        office_id: 'stockholm',
        year: 2025,
        month: 3,
        entries: [
          {
            role: 'Consultant',
            level: 'A',
            recruitment: 5,
            churn: 2,
            price: 1200,
            salary: 65000,
            utr: 0.85,
          },
        ],
      };

      const createdPlan = {
        ...newPlan,
        id: 'plan-2025-03',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
      };

      (fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => createdPlan,
      });

      const { result } = renderHook(() => useBusinessPlanStore());

      let created;
      await act(async () => {
        created = await result.current.createMonthlyPlan(newPlan);
      });

      expect(fetch).toHaveBeenCalledWith('/api/business-plans', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newPlan),
      });
      expect(created).toEqual(createdPlan);
    });

    it('should update business plan successfully', async () => {
      const updatedPlan = {
        id: 'plan-2025-01',
        office_id: 'stockholm',
        year: 2025,
        month: 1,
        entries: [
          {
            role: 'Consultant',
            level: 'A',
            recruitment: 4,
            churn: 1,
            price: 1250,
            salary: 66000,
            utr: 0.87,
          },
        ],
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-15T00:00:00Z',
      };

      (fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => updatedPlan,
      });

      const { result } = renderHook(() => useBusinessPlanStore());

      let updated;
      await act(async () => {
        updated = await result.current.updateMonthlyPlan(updatedPlan);
      });

      expect(fetch).toHaveBeenCalledWith('/api/business-plans/plan-2025-01', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedPlan),
      });
      expect(updated).toEqual(updatedPlan);
    });

    it('should delete business plan successfully', async () => {
      (fetch as Mock).mockResolvedValueOnce({
        ok: true,
      });

      const { result } = renderHook(() => useBusinessPlanStore());

      await act(async () => {
        await result.current.deleteMonthlyPlan('plan-2025-01');
      });

      expect(fetch).toHaveBeenCalledWith('/api/business-plans/plan-2025-01', {
        method: 'DELETE',
      });
    });
  });

  describe('Time Selection', () => {
    it('should set selected year and month', () => {
      const { result } = renderHook(() => useBusinessPlanStore());

      act(() => {
        result.current.setSelectedPeriod(2026, result.current.selectedMonth);
      });

      expect(result.current.selectedYear).toBe(2026);

      act(() => {
        result.current.setSelectedPeriod(result.current.selectedYear, 6);
      });

      expect(result.current.selectedMonth).toBe(6);
    });

    it('should get current plan for selected period', async () => {
      (fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockBusinessPlansResponse,
      });

      const { result } = renderHook(() => useBusinessPlanStore());

      await act(async () => {
        await result.current.loadBusinessPlans('stockholm');
      });

      // Set to January 2025
      act(() => {
        result.current.setSelectedPeriod(2025, 1);
      });

      const currentPlan = result.current.currentPlan;
      expect(currentPlan?.id).toBe('plan-2025-01');
      expect(currentPlan?.month).toBe(1);
      expect(currentPlan?.year).toBe(2025);
    });

    it('should return null for non-existent plan period', async () => {
      (fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockBusinessPlansResponse,
      });

      const { result } = renderHook(() => useBusinessPlanStore());

      await act(async () => {
        await result.current.loadBusinessPlans('stockholm');
      });

      // Set to a period that doesn't exist
      act(() => {
        result.current.setSelectedPeriod(2026, 1);
      });

      const currentPlan = result.current.currentPlan;
      expect(currentPlan).toBeNull();
    });
  });

  describe('clearError', () => {
    it('should clear error state', async () => {
      (fetch as Mock).mockRejectedValueOnce(new Error('Test error'));

      const { result } = renderHook(() => useBusinessPlanStore());

      await act(async () => {
        await result.current.loadBusinessPlans('stockholm');
      });

      expect(result.current.error).toBeTruthy();

      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBeNull();
    });
  });
});