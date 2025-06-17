import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import type { ReactNode } from 'react';

// Types for year navigation
interface YearData {
  [year: number]: any; // Will be replaced with proper simulation data types
}

interface YearNavigationContextType {
  selectedYear: number;
  availableYears: number[];
  yearData: any; // Current year's data
  previousYearData: any; // Previous year's data for comparison
  loading: boolean;
  error: string | null;
  setSelectedYear: (year: number) => void;
  preloadYear: (year: number) => Promise<void>;
  clearCache: () => void;
}

// Create the context
const YearNavigationContext = createContext<YearNavigationContextType | undefined>(undefined);

// Custom hook for using year navigation
export const useYearNavigation = (): YearNavigationContextType => {
  const context = useContext(YearNavigationContext);
  if (!context) {
    throw new Error('useYearNavigation must be used within a YearNavigationProvider');
  }
  return context;
};

// Provider component props
interface YearNavigationProviderProps {
  children: ReactNode;
  simulationData?: any; // Initial simulation data
  onYearChange?: (year: number) => void; // Callback for year changes
}

// LRU Cache implementation for year data
class YearDataCache {
  private cache = new Map<number, any>();
  private maxSize: number;

  constructor(maxSize = 5) {
    this.maxSize = maxSize;
  }

  get(year: number): any {
    const data = this.cache.get(year);
    if (data) {
      // Move to end (most recently used)
      this.cache.delete(year);
      this.cache.set(year, data);
    }
    return data;
  }

  set(year: number, data: any): void {
    if (this.cache.has(year)) {
      this.cache.delete(year);
    } else if (this.cache.size >= this.maxSize) {
      // Remove least recently used (first item)
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    this.cache.set(year, data);
  }

  clear(): void {
    this.cache.clear();
  }
}

// Main provider component
export const YearNavigationProvider: React.FC<YearNavigationProviderProps> = ({
  children,
  simulationData,
  onYearChange
}) => {
  // State management
  const [selectedYear, setSelectedYearState] = useState<number>(2025); // Default to latest year
  const [yearCache] = useState(new YearDataCache());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Derive available years from simulation data
  const availableYears = simulationData?.years ? Object.keys(simulationData.years).map(Number).sort() : [2025];

  // Get current year data from cache or simulation data
  const yearData = yearCache.get(selectedYear) || simulationData?.years?.[selectedYear];
  const previousYearData = yearCache.get(selectedYear - 1) || simulationData?.years?.[selectedYear - 1];

  // Preload year data (placeholder for actual API call)
  const preloadYear = useCallback(async (year: number): Promise<void> => {
    // TODO: Replace with actual API call to fetch year-specific data
    // For now, simulate API delay
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // TODO: Replace with actual data fetching logic
    // const yearData = await fetchYearData(year);
    // yearCache.set(year, yearData);
    
    console.log(`[YearNavigationProvider] Preloaded data for year ${year}`);
  }, [yearCache]);

  // Initialize with simulation data if provided
  useEffect(() => {
    if (simulationData?.years) {
      Object.entries(simulationData.years).forEach(([year, data]) => {
        yearCache.set(Number(year), data);
      });
      
      // Set selected year to the latest available year
      if (availableYears.length > 0) {
        const latestYear = Math.max(...availableYears);
        if (isFinite(latestYear) && latestYear !== selectedYear) {
          setSelectedYearState(latestYear);
        }
      }
    }
  }, [simulationData]);

  // Handle year selection with caching and preloading
  const setSelectedYear = useCallback(async (year: number) => {
    if (year === selectedYear) return;

    setLoading(true);
    setError(null);

    try {
      // If data is not in cache, fetch it
      if (!yearCache.get(year)) {
        await preloadYear(year);
      }

      setSelectedYearState(year);
      
      // Preload adjacent years for smooth navigation
      const adjacentYears = [year - 1, year + 1].filter((y): y is number => 
        typeof y === 'number' && availableYears.includes(y) && !yearCache.get(y)
      );
      
      // Preload in background without blocking UI
      adjacentYears.forEach(adjacentYear => {
        preloadYear(adjacentYear).catch(console.warn);
      });

      // Call the optional callback
      onYearChange?.(year);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load year data');
    } finally {
      setLoading(false);
    }
  }, [selectedYear, yearCache, availableYears, onYearChange, preloadYear]);

  // Clear cache utility
  const clearCache = useCallback(() => {
    yearCache.clear();
  }, [yearCache]);

  // Context value
  const contextValue: YearNavigationContextType = {
    selectedYear,
    availableYears,
    yearData,
    previousYearData,
    loading,
    error,
    setSelectedYear,
    preloadYear,
    clearCache
  };

  return (
    <YearNavigationContext.Provider value={contextValue}>
      {children}
    </YearNavigationContext.Provider>
  );
};

export default YearNavigationProvider; 