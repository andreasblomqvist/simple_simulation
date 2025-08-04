/**
 * Unit tests for office store
 * Tests Zustand store functionality, state management, and API interactions
 */
import { describe, it, expect, beforeEach, vi, Mock } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useOfficeStore } from '../officeStore';
import { OfficeJourney } from '../../types/office';

// Mock fetch globally
global.fetch = vi.fn();

const mockOfficesResponse = [
  {
    id: 'stockholm',
    name: 'Stockholm',
    journey: OfficeJourney.MATURE,
    timezone: 'Europe/Stockholm',
    economic_parameters: {
      cost_of_living: 1.0,
      market_multiplier: 1.0,
      tax_rate: 0.25,
    },
    total_fte: 679,
    roles: {
      Consultant: {
        A: { fte: 69 },
        AC: { fte: 54 },
        C: { fte: 123 },
      },
    },
  },
  {
    id: 'munich',
    name: 'Munich',
    journey: OfficeJourney.ESTABLISHED,
    timezone: 'Europe/Berlin',
    economic_parameters: {
      cost_of_living: 1.1,
      market_multiplier: 1.2,
      tax_rate: 0.28,
    },
    total_fte: 332,
    roles: {
      Consultant: {
        A: { fte: 18 },
        AC: { fte: 32 },
        C: { fte: 61 },
      },
    },
  },
  {
    id: 'helsinki',
    name: 'Helsinki',
    journey: OfficeJourney.EMERGING,
    timezone: 'Europe/Helsinki',
    economic_parameters: {
      cost_of_living: 0.9,
      market_multiplier: 0.95,
      tax_rate: 0.22,
    },
    total_fte: 105,
    roles: {
      Consultant: {
        A: { fte: 16 },
        AC: { fte: 16 },
        C: { fte: 17 },
      },
    },
  },
];

describe('Office Store', () => {
  beforeEach(() => {
    // Reset the store state before each test
    const { setState } = useOfficeStore;
    setState({
      offices: [],
      currentOffice: null,
      officesByJourney: {
        [OfficeJourney.EMERGING]: [],
        [OfficeJourney.ESTABLISHED]: [],
        [OfficeJourney.MATURE]: [],
      },
      loading: false,
      error: null,
    });
    
    // Reset mocks
    vi.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const { result } = renderHook(() => useOfficeStore());
      
      expect(result.current.offices).toEqual([]);
      expect(result.current.currentOffice).toBeNull();
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.officesByJourney).toEqual({
        [OfficeJourney.EMERGING]: [],
        [OfficeJourney.ESTABLISHED]: [],
        [OfficeJourney.MATURE]: [],
      });
    });
  });

  describe('loadOffices', () => {
    it('should load offices successfully', async () => {
      (fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockOfficesResponse,
      });

      const { result } = renderHook(() => useOfficeStore());

      await act(async () => {
        await result.current.loadOffices();
      });

      expect(fetch).toHaveBeenCalledWith('/api/offices');
      expect(result.current.offices).toHaveLength(3);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
      
      // Check grouped offices by journey
      expect(result.current.officesByJourney[OfficeJourney.MATURE]).toHaveLength(1);
      expect(result.current.officesByJourney[OfficeJourney.ESTABLISHED]).toHaveLength(1);
      expect(result.current.officesByJourney[OfficeJourney.EMERGING]).toHaveLength(1);
    });

    it('should handle API errors gracefully', async () => {
      (fetch as Mock).mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useOfficeStore());

      await act(async () => {
        await result.current.loadOffices();
      });

      expect(result.current.offices).toEqual([]);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBe('Failed to load offices: Network error');
    });

    it('should handle non-ok responses', async () => {
      (fetch as Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      });

      const { result } = renderHook(() => useOfficeStore());

      await act(async () => {
        await result.current.loadOffices();
      });

      expect(result.current.error).toBe('Failed to load offices: 500 Internal Server Error');
    });

    it('should set loading state correctly', async () => {
      let resolvePromise: (value: any) => void;
      const promise = new Promise(resolve => {
        resolvePromise = resolve;
      });

      (fetch as Mock).mockReturnValueOnce(promise);

      const { result } = renderHook(() => useOfficeStore());

      const loadPromise = act(async () => {
        result.current.loadOffices();
      });

      // Check loading state is set
      expect(result.current.loading).toBe(true);

      // Resolve the promise
      resolvePromise!({
        ok: true,
        json: async () => mockOfficesResponse,
      });

      await loadPromise;

      // Check loading state is reset
      expect(result.current.loading).toBe(false);
    });
  });

  describe('selectOffice', () => {
    beforeEach(async () => {
      (fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockOfficesResponse,
      });

      const { result } = renderHook(() => useOfficeStore());
      await act(async () => {
        await result.current.loadOffices();
      });
    });

    it('should select office by ID', async () => {
      const { result } = renderHook(() => useOfficeStore());

      await act(async () => {
        await result.current.selectOffice('munich');
      });

      expect(result.current.currentOffice?.id).toBe('munich');
      expect(result.current.currentOffice?.name).toBe('Munich');
    });

    it('should handle selecting non-existent office', async () => {
      const { result } = renderHook(() => useOfficeStore());

      await act(async () => {
        await result.current.selectOffice('nonexistent');
      });

      expect(result.current.currentOffice).toBeNull();
      expect(result.current.error).toBe('Office with ID nonexistent not found');
    });
  });

  describe('getOfficeById', () => {
    beforeEach(async () => {
      (fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockOfficesResponse,
      });

      const { result } = renderHook(() => useOfficeStore());
      await act(async () => {
        await result.current.loadOffices();
      });
    });

    it('should return office by ID', () => {
      const { result } = renderHook(() => useOfficeStore());
      
      const office = result.current.getOfficeById('stockholm');
      expect(office?.name).toBe('Stockholm');
      expect(office?.journey).toBe(OfficeJourney.MATURE);
    });

    it('should return undefined for non-existent office', () => {
      const { result } = renderHook(() => useOfficeStore());
      
      const office = result.current.getOfficeById('nonexistent');
      expect(office).toBeUndefined();
    });
  });

  describe('clearError', () => {
    it('should clear error state', async () => {
      (fetch as Mock).mockRejectedValueOnce(new Error('Test error'));

      const { result } = renderHook(() => useOfficeStore());

      await act(async () => {
        await result.current.loadOffices();
      });

      expect(result.current.error).toBeTruthy();

      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('Office Grouping', () => {
    beforeEach(async () => {
      (fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockOfficesResponse,
      });

      const { result } = renderHook(() => useOfficeStore());
      await act(async () => {
        await result.current.loadOffices();
      });
    });

    it('should group offices by journey correctly', () => {
      const { result } = renderHook(() => useOfficeStore());
      
      expect(result.current.officesByJourney[OfficeJourney.MATURE]).toHaveLength(1);
      expect(result.current.officesByJourney[OfficeJourney.MATURE][0].name).toBe('Stockholm');
      
      expect(result.current.officesByJourney[OfficeJourney.ESTABLISHED]).toHaveLength(1);
      expect(result.current.officesByJourney[OfficeJourney.ESTABLISHED][0].name).toBe('Munich');
      
      expect(result.current.officesByJourney[OfficeJourney.EMERGING]).toHaveLength(1);
      expect(result.current.officesByJourney[OfficeJourney.EMERGING][0].name).toBe('Helsinki');
    });

    it('should sort offices within journey groups by name', () => {
      const { result } = renderHook(() => useOfficeStore());
      
      // Add more offices to test sorting
      const additionalOffices = [
        ...mockOfficesResponse,
        {
          id: 'oslo',
          name: 'Oslo',
          journey: OfficeJourney.EMERGING,
          timezone: 'Europe/Oslo',
          economic_parameters: {
            cost_of_living: 1.2,
            market_multiplier: 1.0,
            tax_rate: 0.25,
          },
          total_fte: 85,
          roles: {},
        },
        {
          id: 'amsterdam',
          name: 'Amsterdam',
          journey: OfficeJourney.EMERGING,
          timezone: 'Europe/Amsterdam',
          economic_parameters: {
            cost_of_living: 1.1,
            market_multiplier: 1.1,
            tax_rate: 0.24,
          },
          total_fte: 95,
          roles: {},
        },
      ];

      (fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => additionalOffices,
      });

      act(async () => {
        await result.current.loadOffices();
      });

      const emergingOffices = result.current.officesByJourney[OfficeJourney.EMERGING];
      expect(emergingOffices).toHaveLength(3);
      expect(emergingOffices[0].name).toBe('Amsterdam');
      expect(emergingOffices[1].name).toBe('Helsinki');
      expect(emergingOffices[2].name).toBe('Oslo');
    });
  });

  describe('CRUD Operations', () => {
    it('should create office successfully', async () => {
      const newOffice = {
        name: 'Berlin',
        journey: OfficeJourney.EMERGING,
        timezone: 'Europe/Berlin',
        economic_parameters: {
          cost_of_living: 1.0,
          market_multiplier: 1.0,
          tax_rate: 0.25,
        },
        total_fte: 50,
        roles: {},
      };

      const createdOffice = {
        ...newOffice,
        id: 'berlin',
      };

      (fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => createdOffice,
      });

      const { result } = renderHook(() => useOfficeStore());

      let created;
      await act(async () => {
        created = await result.current.createOffice(newOffice);
      });

      expect(fetch).toHaveBeenCalledWith('/api/offices', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newOffice),
      });
      expect(created).toEqual(createdOffice);
    });

    it('should update office successfully', async () => {
      const updatedOffice = {
        id: 'stockholm',
        name: 'Stockholm Updated',
        journey: OfficeJourney.MATURE,
        timezone: 'Europe/Stockholm',
        economic_parameters: {
          cost_of_living: 1.1,
          market_multiplier: 1.1,
          tax_rate: 0.26,
        },
        total_fte: 700,
        roles: {},
      };

      (fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => updatedOffice,
      });

      const { result } = renderHook(() => useOfficeStore());

      let updated;
      await act(async () => {
        updated = await result.current.updateOffice(updatedOffice);
      });

      expect(fetch).toHaveBeenCalledWith('/api/offices/stockholm', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedOffice),
      });
      expect(updated).toEqual(updatedOffice);
    });

    it('should delete office successfully', async () => {
      (fetch as Mock).mockResolvedValueOnce({
        ok: true,
      });

      const { result } = renderHook(() => useOfficeStore());

      await act(async () => {
        await result.current.deleteOffice('stockholm');
      });

      expect(fetch).toHaveBeenCalledWith('/api/offices/stockholm', {
        method: 'DELETE',
      });
    });
  });
});