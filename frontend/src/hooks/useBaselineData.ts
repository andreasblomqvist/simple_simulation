/**
 * Baseline Data Hook
 * 
 * Custom hook for managing baseline input data transformation and state.
 * Bridges DataTransformService to UI components with state management.
 */

import { useState, useCallback, useMemo, useImperativeHandle, forwardRef } from 'react';
import { 
  DataTransformService,
  type MonthlyRoleData,
  type BaselineStructuredData
} from '../services';
import type { StandardRole } from '../types/office';
import { useToast } from '../components/ui/use-toast';

export interface UseBaselineDataOptions {
  initialData?: any;
  onNext?: (data: any) => void;
}

export interface UseBaselineDataReturn {
  // Data state
  recruitmentData: MonthlyRoleData;
  leaversData: MonthlyRoleData;
  selectedRole: StandardRole;
  activeTab: 'recruitment' | 'churn';
  
  // Table data for display
  tableData: Array<{
    month: string;
    [level: string]: any;
  }>;
  
  // Actions
  setSelectedRole: (role: StandardRole) => void;
  setActiveTab: (tab: 'recruitment' | 'churn') => void;
  handleCellChange: (month: string, level: string, value: number | null) => void;
  handleApplyForAllYears: () => void;
  handleNext: () => void;
  
  // Data access
  getCurrentData: () => BaselineStructuredData;
  
  // Utilities
  defaultMonths: string[];
  availableRoles: StandardRole[];
  availableLevels: string[];
}

export function useBaselineData(options: UseBaselineDataOptions = {}): UseBaselineDataReturn {
  const { initialData, onNext } = options;
  const { toast } = useToast();
  
  // Initialize data from service
  const [recruitmentData, setRecruitmentData] = useState<MonthlyRoleData>(() => 
    DataTransformService.initializeFromBaseline(initialData, 'recruitment')
  );
  
  const [leaversData, setLeaversData] = useState<MonthlyRoleData>(() => 
    DataTransformService.initializeFromBaseline(initialData, 'churn')
  );
  
  const [selectedRole, setSelectedRole] = useState<StandardRole>('Consultant');
  const [activeTab, setActiveTab] = useState<'recruitment' | 'churn'>('recruitment');
  
  // Get configuration from service
  const defaultMonths = useMemo(() => 
    DataTransformService.getDefaultMonths(), 
    []
  );
  
  const availableRoles: StandardRole[] = useMemo(() => 
    ['Consultant', 'Sales', 'Operations'], 
    []
  );
  
  const availableLevels = useMemo(() => {
    // This should come from ROLE_LEVELS but we'll use a reasonable default
    const roleLevels: Record<StandardRole, string[]> = {
      'Consultant': ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP'],
      'Sales': ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP'],
      'Operations': ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']
    };
    return roleLevels[selectedRole] || [];
  }, [selectedRole]);
  
  // Handle cell value changes
  const handleCellChange = useCallback((month: string, level: string, value: number | null) => {
    // Sanitize the input value
    const sanitizedValue = DataTransformService.sanitizeMonthlyValue(value);
    
    if (activeTab === 'recruitment') {
      setRecruitmentData(prev => ({
        ...prev,
        [selectedRole]: {
          ...prev[selectedRole],
          [level]: {
            ...prev[selectedRole]?.[level],
            [month]: sanitizedValue
          }
        }
      }));
    } else {
      setLeaversData(prev => ({
        ...prev,
        [selectedRole]: {
          ...prev[selectedRole],
          [level]: {
            ...prev[selectedRole]?.[level],
            [month]: sanitizedValue
          }
        }
      }));
    }
  }, [activeTab, selectedRole]);
  
  // Apply 2025 values to all years
  const handleApplyForAllYears = useCallback(() => {
    const currentData = activeTab === 'recruitment' ? recruitmentData : leaversData;
    const setData = activeTab === 'recruitment' ? setRecruitmentData : setLeaversData;
    
    const updatedData = DataTransformService.applyYear2025ToAllYears(
      currentData,
      selectedRole
    );
    
    setData(updatedData);
    
    toast({
      title: "Values Applied",
      description: `Applied 2025 ${activeTab} values to all years for ${selectedRole}`,
    });
  }, [activeTab, recruitmentData, leaversData, selectedRole, toast]);
  
  // Get current structured data
  const getCurrentData = useCallback((): BaselineStructuredData => {
    return DataTransformService.buildBaselineInputStructure(
      recruitmentData,
      leaversData
    );
  }, [recruitmentData, leaversData]);
  
  // Handle next step
  const handleNext = useCallback(() => {
    const baselineInput = getCurrentData();
    onNext?.(baselineInput);
  }, [getCurrentData, onNext]);
  
  // Transform data for table display
  const tableData = useMemo(() => {
    const currentData = activeTab === 'recruitment' ? recruitmentData : leaversData;
    return DataTransformService.transformDataForTable(currentData, selectedRole);
  }, [activeTab, recruitmentData, leaversData, selectedRole]);
  
  return {
    // Data state
    recruitmentData,
    leaversData,
    selectedRole,
    activeTab,
    
    // Table data
    tableData,
    
    // Actions
    setSelectedRole,
    setActiveTab,
    handleCellChange,
    handleApplyForAllYears,
    handleNext,
    
    // Data access
    getCurrentData,
    
    // Utilities
    defaultMonths,
    availableRoles,
    availableLevels
  };
}

// Create a forwardRef version for imperative handle
export interface BaselineDataRef {
  getCurrentData: () => BaselineStructuredData;
}

export const useBaselineDataWithRef = forwardRef<BaselineDataRef, UseBaselineDataOptions>(
  (options, ref) => {
    const baselineData = useBaselineData(options);
    
    useImperativeHandle(ref, () => ({
      getCurrentData: baselineData.getCurrentData
    }), [baselineData.getCurrentData]);
    
    return baselineData;
  }
);