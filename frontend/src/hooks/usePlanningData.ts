/**
 * Planning Data Hook
 * 
 * Custom hook for managing business planning data and calculations.
 * Bridges PlanningService to UI components with state management.
 */

import { useState, useCallback, useMemo } from 'react';
import { 
  PlanningService,
  type SummaryData,
  type CellData,
  type DetailedCalculations
} from '../services';
import type { OfficeConfig, StandardRole, StandardLevel } from '../types/office';

export interface UsePlanningDataOptions {
  office: OfficeConfig;
  year: number;
  initialData?: CellData[];
}

export interface UsePlanningDataReturn {
  // Data
  cellData: Map<string, CellData>;
  totalSummary: SummaryData;
  detailedCalculations: DetailedCalculations;
  
  // Formatted data for display
  formattedSummary: {
    totalRevenue: string;
    totalCosts: string;
    grossProfit: string;
    averageMargin: string;
  };
  workforceSummary: {
    totalRecruitment: number;
    totalChurn: number;
    netGrowth: number;
    growthColor: string;
  };
  roleBreakdown: Array<{
    role: StandardRole;
    netGrowth: number;
    margin: number;
    revenue: number;
  }>;
  monthlyTrends: Array<{
    month: string;
    shortMonth: string;
    netGrowth: number;
    margin: number;
    revenue: number;
    netGrowthColor: string;
  }>;
  
  // Actions
  updateCellData: (
    role: StandardRole,
    level: StandardLevel,
    month: number,
    data: Partial<CellData>
  ) => void;
  getCellData: (role: StandardRole, level: StandardLevel, month: number) => CellData;
  validateData: () => {
    valid: boolean;
    errors: string[];
    warnings: string[];
  };
  exportData: () => {
    summary: DetailedCalculations;
    rawData: CellData[];
    metadata: any;
  };
  
  // State
  loading: boolean;
  error: string | null;
}

export function usePlanningData(options: UsePlanningDataOptions): UsePlanningDataReturn {
  const { office, year, initialData = [] } = options;
  
  const [cellData, setCellData] = useState<Map<string, CellData>>(() => {
    const map = new Map<string, CellData>();
    initialData.forEach(cell => {
      const key = `${cell.role}-${cell.level}-${cell.month}`;
      map.set(key, cell);
    });
    return map;
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Generate cell key for consistent data access
  const getCellKey = useCallback((role: StandardRole, level: StandardLevel, month: number) => {
    return `${role}-${level}-${month}`;
  }, []);
  
  // Get cell data with defaults
  const getCellData = useCallback((
    role: StandardRole, 
    level: StandardLevel, 
    month: number
  ): CellData => {
    const key = getCellKey(role, level, month);
    const existing = cellData.get(key);
    
    if (existing) {
      return existing;
    }
    
    // Return default cell data
    return {
      role,
      level,
      month,
      year,
      recruitment: 0,
      churn: 0,
      price: office?.economic_params?.default_rates?.[role]?.[level] || 100,
      utr: 0.8, // Default 80% utilization
      salary: office?.salaries?.[role]?.[level] || 5000
    };
  }, [cellData, getCellKey, year, office]);
  
  // Update cell data
  const updateCellData = useCallback((
    role: StandardRole,
    level: StandardLevel,
    month: number,
    data: Partial<CellData>
  ) => {
    const key = getCellKey(role, level, month);
    const existing = getCellData(role, level, month);
    
    const updated: CellData = {
      ...existing,
      ...data,
      role,
      level,
      month,
      year
    };
    
    setCellData(prev => new Map(prev.set(key, updated)));
  }, [getCellKey, getCellData, year]);
  
  // Calculate total summary
  const totalSummary = useMemo((): SummaryData => {
    let recruitment = 0;
    let churn = 0;
    let revenue = 0;
    let cost = 0;
    
    // Sum all cell data
    cellData.forEach(cell => {
      recruitment += cell.recruitment;
      churn += cell.churn;
      revenue += PlanningService.calculateMonthlyRevenue(cell);
      cost += cell.salary;
    });
    
    const netGrowth = recruitment - churn;
    const margin = revenue > 0 ? ((revenue - cost) / revenue) * 100 : 0;
    
    return {
      recruitment,
      churn,
      netGrowth,
      revenue,
      cost,
      margin
    };
  }, [cellData]);
  
  // Calculate detailed metrics
  const detailedCalculations = useMemo((): DetailedCalculations => {
    return PlanningService.calculateDetailedPlanningMetrics(
      office,
      year,
      totalSummary,
      getCellData
    );
  }, [office, year, totalSummary, getCellData]);
  
  // Formatted summary for display
  const formattedSummary = useMemo(() => {
    return PlanningService.calculateFinancialSummary(detailedCalculations);
  }, [detailedCalculations]);
  
  // Workforce summary
  const workforceSummary = useMemo(() => {
    return PlanningService.calculateWorkforceSummary(detailedCalculations);
  }, [detailedCalculations]);
  
  // Role breakdown
  const roleBreakdown = useMemo(() => {
    return PlanningService.calculateRoleBreakdown(detailedCalculations);
  }, [detailedCalculations]);
  
  // Monthly trends
  const monthlyTrends = useMemo(() => {
    return PlanningService.calculateMonthlyTrends(detailedCalculations);
  }, [detailedCalculations]);
  
  // Validate data
  const validateData = useCallback(() => {
    return PlanningService.validatePlanningData(getCellData);
  }, [getCellData]);
  
  // Export data
  const exportData = useCallback(() => {
    return PlanningService.exportPlanningData(getCellData);
  }, [getCellData]);
  
  return {
    // Data
    cellData,
    totalSummary,
    detailedCalculations,
    
    // Formatted data
    formattedSummary,
    workforceSummary,
    roleBreakdown,
    monthlyTrends,
    
    // Actions
    updateCellData,
    getCellData,
    validateData,
    exportData,
    
    // State
    loading,
    error
  };
}