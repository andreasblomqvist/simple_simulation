import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { useYearNavigation } from '../components/v2/YearNavigationProvider';
import type { 
  SimulationYearData, 
  OfficeData, 
  YearOverYearKPI, 
  SimulationConfig,
  SimulationAPIResponse,
  YearDataAPIResponse,
  KPIAPIResponse 
} from '../types/simulation';

// ========================================
// Performance Utilities
// ========================================

// Debounce hook for performance optimization
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

// ========================================
// API Client
// ========================================

// Configuration for simulation API
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// API client with error handling
const apiClient = {
  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`);
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    return response.json();
  },

  async post<T>(endpoint: string, data: any): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    return response.json();
  }
};

// ========================================
// Year-Aware Data Fetching Hooks
// ========================================

// Hook for fetching year-specific simulation data
export const useYearData = (year?: number) => {
  const { selectedYear, loading: contextLoading } = useYearNavigation();
  const targetYear = year || selectedYear;
  
  const [data, setData] = useState<SimulationYearData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastFetched, setLastFetched] = useState<Date | null>(null);

  // Debounce year changes to prevent excessive API calls
  const debouncedYear = useDebounce(targetYear, 300);

  const fetchYearData = useCallback(async (yearToFetch: number) => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.get<{ data: SimulationYearData }>(
        `/api/simulation/years/${yearToFetch}`
      );
      
      setData(response.data);
      setLastFetched(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch year data');
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch data when debounced year changes
  useEffect(() => {
    if (debouncedYear) {
      fetchYearData(debouncedYear);
    }
  }, [debouncedYear, fetchYearData]);

  const refresh = useCallback(() => {
    fetchYearData(targetYear);
  }, [fetchYearData, targetYear]);

  return {
    data,
    loading: loading || contextLoading,
    error,
    lastFetched,
    refresh,
    isStale: lastFetched ? Date.now() - lastFetched.getTime() > 5 * 60 * 1000 : false // 5 min
  };
};

// Hook for fetching office-specific data with year awareness
export const useOfficeYearData = (officeCode: string, year?: number) => {
  const { selectedYear } = useYearNavigation();
  const targetYear = year || selectedYear;
  
  const [data, setData] = useState<OfficeData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const debouncedOffice = useDebounce(officeCode, 200);
  const debouncedYear = useDebounce(targetYear, 300);

  const fetchOfficeData = useCallback(async (office: string, yearToFetch: number) => {
    if (!office) return;
    
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.get<{ data: OfficeData }>(
        `/api/simulation/offices/${office}/years/${yearToFetch}`
      );
      
      setData(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch office data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchOfficeData(debouncedOffice, debouncedYear);
  }, [debouncedOffice, debouncedYear, fetchOfficeData]);

  return {
    data,
    loading,
    error,
    refresh: () => fetchOfficeData(officeCode, targetYear)
  };
};

// Hook for fetching KPI data with year-over-year comparisons
export const useYearKPIData = (kpiKeys?: string[], year?: number) => {
  const { selectedYear } = useYearNavigation();
  const targetYear = year || selectedYear;
  
  const [data, setData] = useState<Record<string, YearOverYearKPI>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const debouncedKPIs = useDebounce(kpiKeys, 200);
  const debouncedYear = useDebounce(targetYear, 300);

  const fetchKPIData = useCallback(async (keys: string[], yearToFetch: number) => {
    setLoading(true);
    setError(null);

    try {
      const queryParams = keys.length > 0 ? `?kpis=${keys.join(',')}` : '';
      const response = await apiClient.get<{ data: Record<string, YearOverYearKPI> }>(
        `/api/simulation/kpis/years/${yearToFetch}${queryParams}`
      );
      
      setData(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch KPI data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const keys = debouncedKPIs || [];
    fetchKPIData(keys, debouncedYear);
  }, [debouncedKPIs, debouncedYear, fetchKPIData]);

  return {
    data,
    loading,
    error,
    refresh: () => fetchKPIData(kpiKeys || [], targetYear)
  };
};

// Hook for running simulations with optimistic updates
export const useSimulationRunner = () => {
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [lastConfig, setLastConfig] = useState<SimulationConfig | null>(null);

  const runSimulation = useCallback(async (config: SimulationConfig) => {
    setRunning(true);
    setProgress(0);
    setError(null);
    setLastConfig(config);

    try {
      // Simulate progress updates (replace with actual WebSocket or polling)
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const response = await apiClient.post<{ data: any }>(
        '/api/simulation/run',
        config
      );

      clearInterval(progressInterval);
      setProgress(100);

      // Wait a bit to show completion
      setTimeout(() => {
        setProgress(0);
        setRunning(false);
      }, 500);

      return response.data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Simulation failed');
      setRunning(false);
      setProgress(0);
      throw err;
    }
  }, []);

  return {
    running,
    progress,
    error,
    lastConfig,
    runSimulation
  };
};

// Hook for preloading adjacent years for smooth navigation
export const useYearPreloader = () => {
  const { selectedYear, availableYears, preloadYear } = useYearNavigation();
  const preloadedYears = useRef(new Set<number>());

  const preloadAdjacentYears = useCallback(async (currentYear: number) => {
    const adjacentYears = [currentYear - 1, currentYear + 1].filter(year => 
      availableYears.includes(year) && !preloadedYears.current.has(year)
    );

    // Preload in background
    adjacentYears.forEach(async year => {
      try {
        await preloadYear(year);
        preloadedYears.current.add(year);
      } catch (err) {
        console.warn(`Failed to preload year ${year}:`, err);
      }
    });
  }, [availableYears, preloadYear]);

  useEffect(() => {
    // Preload when selected year changes
    preloadAdjacentYears(selectedYear);
  }, [selectedYear, preloadAdjacentYears]);

  return {
    preloadedYears: preloadedYears.current,
    preloadAdjacentYears
  };
};

// Hook for managing multiple year comparisons
export const useYearComparison = (years: number[]) => {
  const [data, setData] = useState<Record<number, SimulationYearData>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchComparisonData = useCallback(async (yearsToFetch: number[]) => {
    setLoading(true);
    setError(null);

    try {
      const promises = yearsToFetch.map(year =>
        apiClient.get<{ data: SimulationYearData }>(`/api/simulation/years/${year}`)
          .then(response => ({ year, data: response.data }))
      );

      const results = await Promise.all(promises);
      const newData = results.reduce((acc, { year, data }) => {
        acc[year] = data;
        return acc;
      }, {} as Record<number, SimulationYearData>);

      setData(newData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch comparison data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (years.length > 0) {
      fetchComparisonData(years);
    }
  }, [years, fetchComparisonData]);

  // Memoized comparison calculations
  const comparison = useMemo(() => {
    const yearKeys = Object.keys(data).map(Number).sort();
    if (yearKeys.length < 2) return null;

    return {
      years: yearKeys,
      data,
      getYearOverYearChange: (year: number, kpi: string) => {
        const currentData = data[year];
        const previousData = data[year - 1];
        
        if (!currentData || !previousData) return null;
        
        // This would need to be implemented based on actual data structure
        return {
          absolute: 0, // Calculate actual difference
          percentage: 0 // Calculate actual percentage change
        };
      }
    };
  }, [data]);

  return {
    data,
    loading,
    error,
    comparison,
    refresh: () => fetchComparisonData(years)
  };
};

// Hook for managing simulation state across the application
export const useGlobalSimulationState = () => {
  const { selectedYear, availableYears } = useYearNavigation();
  const [config, setConfig] = useState<SimulationConfig | null>(null);
  const [results, setResults] = useState<SimulationYearData | null>(null);

  // Auto-save config to localStorage
  useEffect(() => {
    if (config) {
      localStorage.setItem('simulation-config', JSON.stringify(config));
    }
  }, [config]);

  // Load config from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('simulation-config');
    if (saved) {
      try {
        setConfig(JSON.parse(saved));
      } catch (err) {
        console.warn('Failed to load saved config:', err);
      }
    }
  }, []);

  return {
    selectedYear,
    availableYears,
    config,
    setConfig,
    results,
    setResults,
    clearConfig: () => {
      setConfig(null);
      localStorage.removeItem('simulation-config');
    }
  };
}; 