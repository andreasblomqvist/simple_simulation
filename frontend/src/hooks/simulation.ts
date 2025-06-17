// Type-Safe Hooks for Simulation Data and UI Management
// Custom hooks that leverage our comprehensive type system

import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import type {
  SimulationYear,
  SimulationYearData,
  SimulationConfig,
  OfficeData,
  YearOverYearKPI,
  KPIKey,
  YearNavigationContext,
  SimulationAPIResponse,
  AggregatedData,
  ChartDataPoint,
  MultiYearTrendData,
  DataStatus
} from '../types/simulation';
import type {
  ComponentState,
  AsyncState,
  LoadingState,
  CacheConfig
} from '../types/ui';
// ========================================
// Data Fetching Hooks
// ========================================

/**
 * Hook for fetching and managing simulation data for a specific year
 */
export function useSimulationYearData(
  year: SimulationYear,
  config?: { 
    autoRefresh?: boolean; 
    refreshInterval?: number;
    cache?: boolean;
  }
): AsyncState<SimulationYearData> {
  const [state, setState] = useState<ComponentState<SimulationYearData>>({
    data: null,
    loading: true,
    error: null,
    lastUpdated: null
  });

  const cache = useRef<Map<SimulationYear, SimulationYearData>>(new Map());

  const fetchData = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      // Check cache first if enabled
      if (config?.cache && cache.current.has(year)) {
        const cachedData = cache.current.get(year)!;
        setState({
          data: cachedData,
          loading: false,
          error: null,
          lastUpdated: new Date()
        });
        return;
      }

      // Simulated API call - replace with actual implementation
      const response = await fetch(`/api/simulation/year/${year}`);
      const result: SimulationAPIResponse<SimulationYearData> = await response.json();
      
      if (result.error) {
        throw new Error(result.error.message);
      }

      const data = result.data;
      
      // Update cache if enabled
      if (config?.cache) {
        cache.current.set(year, data);
      }

      setState({
        data,
        loading: false,
        error: null,
        lastUpdated: new Date()
      });
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }));
    }
  }, [year, config?.cache]);

  const retry = useCallback(() => fetchData(), [fetchData]);
  const refresh = useCallback(() => {
    // Clear cache entry and refetch
    if (config?.cache) {
      cache.current.delete(year);
    }
    return fetchData();
  }, [fetchData, year, config?.cache]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Auto-refresh functionality
  useEffect(() => {
    if (config?.autoRefresh && config.refreshInterval) {
      const interval = setInterval(refresh, config.refreshInterval);
      return () => clearInterval(interval);
    }
  }, [config?.autoRefresh, config?.refreshInterval, refresh]);

  return {
    ...state,
    retry,
    refresh
  };
}

/**
 * Hook for managing KPI data with year-over-year comparisons
 */
export function useKPIData(
  year: SimulationYear,
  kpiKeys: KPIKey[]
): AsyncState<Record<KPIKey, YearOverYearKPI>> {
  const [state, setState] = useState<ComponentState<Record<KPIKey, YearOverYearKPI>>>({
    data: null,
    loading: true,
    error: null,
    lastUpdated: null
  });

  const fetchKPIData = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const response = await fetch(`/api/kpis/${year}?keys=${kpiKeys.join(',')}`);
      const result: SimulationAPIResponse<Record<KPIKey, YearOverYearKPI>> = await response.json();
      
      if (result.error) {
        throw new Error(result.error.message);
      }

      setState({
        data: result.data,
        loading: false,
        error: null,
        lastUpdated: new Date()
      });
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }));
    }
  }, [year, kpiKeys]);

  const retry = useCallback(() => fetchKPIData(), [fetchKPIData]);
  const refresh = useCallback(() => fetchKPIData(), [fetchKPIData]);

  useEffect(() => {
    fetchKPIData();
  }, [fetchKPIData]);

  return { ...state, retry, refresh };
}

/**
 * Hook for fetching office list with filtering capabilities
 */
export function useOfficeList(
  filters?: {
    journey?: string[];
    active?: boolean;
    searchTerm?: string;
  }
): AsyncState<OfficeData[]> {
  const [state, setState] = useState<ComponentState<OfficeData[]>>({
    data: null,
    loading: true,
    error: null,
    lastUpdated: null
  });

  const fetchOffices = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const params = new URLSearchParams();
      if (filters?.journey) params.append('journey', filters.journey.join(','));
      if (filters?.active !== undefined) params.append('active', filters.active.toString());
      if (filters?.searchTerm) params.append('search', filters.searchTerm);

      const response = await fetch(`/api/offices?${params}`);
      const result: SimulationAPIResponse<OfficeData[]> = await response.json();
      
      if (result.error) {
        throw new Error(result.error.message);
      }

      setState({
        data: result.data,
        loading: false,
        error: null,
        lastUpdated: new Date()
      });
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }));
    }
  }, [filters]);

  const retry = useCallback(() => fetchOffices(), [fetchOffices]);
  const refresh = useCallback(() => fetchOffices(), [fetchOffices]);

  useEffect(() => {
    fetchOffices();
  }, [fetchOffices]);

  return { ...state, retry, refresh };
}

// ========================================
// UI State Management Hooks
// ========================================

/**
 * Hook for managing year navigation state with caching
 */
export function useYearNavigation(
  initialYear?: SimulationYear,
  cacheConfig?: CacheConfig
): YearNavigationContext {
  const [selectedYear, setSelectedYear] = useState<SimulationYear>(
    initialYear || new Date().getFullYear()
  );
  const [availableYears, setAvailableYears] = useState<SimulationYear[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [preloadingYears, setPreloadingYears] = useState<Set<SimulationYear>>(new Set());

  const cache = useRef<Map<SimulationYear, SimulationYearData>>(new Map());

  // Initialize available years
  useEffect(() => {
    const currentYear = new Date().getFullYear();
    const years = Array.from({ length: 5 }, (_, i) => currentYear + i - 2); // 2 years back, current, 2 years forward
    setAvailableYears(years);
  }, []);

  const preloadYear = useCallback(async (year: SimulationYear) => {
    if (cache.current.has(year) || preloadingYears.has(year)) {
      return;
    }

    setPreloadingYears(prev => new Set(prev).add(year));
    
    try {
      const response = await fetch(`/api/simulation/year/${year}`);
      const result: SimulationAPIResponse<SimulationYearData> = await response.json();
      
      if (!result.error) {
        cache.current.set(year, result.data);
        
                 // Implement cache size limit
         if (cacheConfig?.maxSize && cache.current.size > cacheConfig.maxSize) {
           const firstKey = cache.current.keys().next().value;
           if (firstKey !== undefined) {
             cache.current.delete(firstKey);
           }
         }
      }
    } catch (error) {
      console.warn(`Failed to preload year ${year}:`, error);
    } finally {
      setPreloadingYears(prev => {
        const newSet = new Set(prev);
        newSet.delete(year);
        return newSet;
      });
    }
  }, [cacheConfig?.maxSize, preloadingYears]);

  const handleYearChange = useCallback((year: SimulationYear) => {
    setSelectedYear(year);
    
    // Preload adjacent years
    const currentIndex = availableYears.indexOf(year);
    const adjacentYears = [
      availableYears[currentIndex - 1],
      availableYears[currentIndex + 1]
    ].filter(Boolean);
    
    adjacentYears.forEach(preloadYear);
  }, [availableYears, preloadYear]);

  const clearCache = useCallback(() => {
    cache.current.clear();
  }, []);

  const refreshYear = useCallback(async (year: SimulationYear) => {
    cache.current.delete(year);
    await preloadYear(year);
  }, [preloadYear]);

  return {
    selectedYear,
    availableYears,
    loading,
    error,
    cache: cache.current,
    preloadingYears,
    setSelectedYear: handleYearChange,
    preloadYear,
    clearCache,
    refreshYear
  };
}

/**
 * Hook for managing simulation configuration state
 */
export function useSimulationConfig(
  initialConfig?: Partial<SimulationConfig>
): {
  config: SimulationConfig;
  updateConfig: (updates: Partial<SimulationConfig>) => void;
  resetConfig: () => void;
  isValid: boolean;
  errors: Record<string, string>;
} {
  const defaultConfig: SimulationConfig = {
    levers: [],
    scope: {
      timePeriod: 'month',
      selectedOffices: [],
      applyToAllOffices: false,
      selectedMonths: [],
      applyToAllMonths: false,
      duration: 12
    },
    economicParameters: {
      priceIncrease: 0,
      salaryIncrease: 0,
      workingHours: 168,
      otherExpenses: 0
    },
    duration: 12,
    startDate: new Date(),
    endDate: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000) // 1 year from now
  };

  const [config, setConfig] = useState<SimulationConfig>({
    ...defaultConfig,
    ...initialConfig
  });

  const updateConfig = useCallback((updates: Partial<SimulationConfig>) => {
    setConfig(prev => ({ ...prev, ...updates }));
  }, []);

  const resetConfig = useCallback(() => {
    setConfig({ ...defaultConfig, ...initialConfig });
  }, [initialConfig]);

  // Validation logic
  const { isValid, errors } = useMemo(() => {
    const validationErrors: Record<string, string> = {};

    if (config.duration <= 0) {
      validationErrors.duration = 'Duration must be greater than 0';
    }

    if (config.levers.length === 0) {
      validationErrors.levers = 'At least one lever must be configured';
    }

    if (!config.scope.applyToAllOffices && config.scope.selectedOffices.length === 0) {
      validationErrors.offices = 'At least one office must be selected';
    }

    return {
      isValid: Object.keys(validationErrors).length === 0,
      errors: validationErrors
    };
  }, [config]);

  return {
    config,
    updateConfig,
    resetConfig,
    isValid,
    errors
  };
}

// ========================================
// Chart Data Processing Hooks
// ========================================

/**
 * Hook for processing multi-year trend data for charts
 */
export function useMultiYearTrendData(
  kpiKey: KPIKey,
  years: SimulationYear[]
): AsyncState<MultiYearTrendData> {
  const [state, setState] = useState<ComponentState<MultiYearTrendData>>({
    data: null,
    loading: true,
    error: null,
    lastUpdated: null
  });

  const processData = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const dataPromises = years.map(async (year) => {
        const response = await fetch(`/api/kpis/${year}?keys=${kpiKey}`);
        const result: SimulationAPIResponse<Record<KPIKey, YearOverYearKPI>> = await response.json();
        return { year, data: result.data[kpiKey] };
      });

      const yearData = await Promise.all(dataPromises);
      
      const chartData: ChartDataPoint[] = yearData.map(({ year, data }) => ({
        year,
        value: data.value,
        label: year.toString(),
        isProjected: year > new Date().getFullYear()
      }));

      const trendData: MultiYearTrendData = {
        title: `${kpiKey} Trend`,
        data: chartData,
        yAxisLabel: yearData[0]?.data?.unit || '',
        unit: yearData[0]?.data?.unit || '',
        targetLine: yearData[0]?.data?.target,
        baselineLine: yearData[0]?.data?.baseline
      };

      setState({
        data: trendData,
        loading: false,
        error: null,
        lastUpdated: new Date()
      });
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }));
    }
  }, [kpiKey, years]);

  const retry = useCallback(() => processData(), [processData]);
  const refresh = useCallback(() => processData(), [processData]);

  useEffect(() => {
    processData();
  }, [processData]);

  return { ...state, retry, refresh };
}

// ========================================
// Performance & Optimization Hooks
// ========================================

/**
 * Hook for debounced values (useful for search inputs)
 */
export function useDebounce<T>(value: T, delay: number): T {
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

/**
 * Hook for managing loading states across multiple async operations
 */
export function useLoadingState(): {
  isLoading: boolean;
  startLoading: (key: string) => void;
  stopLoading: (key: string) => void;
  loadingStates: Record<string, boolean>;
} {
  const [loadingStates, setLoadingStates] = useState<Record<string, boolean>>({});

  const startLoading = useCallback((key: string) => {
    setLoadingStates(prev => ({ ...prev, [key]: true }));
  }, []);

  const stopLoading = useCallback((key: string) => {
    setLoadingStates(prev => ({ ...prev, [key]: false }));
  }, []);

  const isLoading = useMemo(() => 
    Object.values(loadingStates).some(Boolean), 
    [loadingStates]
  );

  return {
    isLoading,
    startLoading,
    stopLoading,
    loadingStates
  };
}

/**
 * Hook for intersection observer (useful for lazy loading)
 */
export function useIntersectionObserver(
  elementRef: React.RefObject<Element>,
  options?: IntersectionObserverInit
): boolean {
  const [isIntersecting, setIsIntersecting] = useState<boolean>(false);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsIntersecting(entry.isIntersecting);
      },
      options
    );

    observer.observe(element);

    return () => {
      observer.unobserve(element);
    };
  }, [elementRef, options]);

  return isIntersecting;
}

 