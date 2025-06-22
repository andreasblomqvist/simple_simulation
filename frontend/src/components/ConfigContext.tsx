import React, { createContext, useContext, useState, useEffect } from 'react';

// Types for configuration data
interface OfficeConfig {
  name: string;
  roles: {
    [roleName: string]: {
      [levelName: string]: {
        [key: string]: any;
      };
    };
  };
}

interface ConfigStatus {
  checksum: string;
  status: 'complete' | 'incomplete';
  summary?: {
    total_offices: number;
    total_roles: number;
    total_levels: number;
    total_fte: number;
    missing_data_count: number;
  };
  timestamp?: string;
}

interface ConfigContextType {
  // Configuration data from Excel/backend
  offices: OfficeConfig[];
  setOffices: (offices: OfficeConfig[]) => void;
  
  // Lever overrides for simulation
  leverOverrides: Record<string, any>;
  setLeverOverrides: (overrides: Record<string, any>) => void;
  updateLeverOverride: (officeName: string, roleName: string, levelName: string, key: string, value: any) => void;
  
  // Configuration status
  configStatus: ConfigStatus | null;
  setConfigStatus: (status: ConfigStatus | null) => void;
  refreshConfigStatus: () => Promise<void>;
  
  // Loading states
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  
  // Helper functions
  getOfficeData: (officeName: string) => OfficeConfig | undefined;
  hasConfigData: () => boolean;
  buildSimulationOverrides: () => Record<string, any>;
}

const ConfigContext = createContext<ConfigContextType | undefined>(undefined);

export const ConfigProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [offices, setOffices] = useState<OfficeConfig[]>([]);
  const [leverOverrides, setLeverOverrides] = useState<Record<string, any>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [configStatus, setConfigStatus] = useState<ConfigStatus | null>(null);

  // Helper function to get specific office data
  const getOfficeData = (officeName: string): OfficeConfig | undefined => {
    return offices.find(office => office.name === officeName);
  };

  // Check if we have configuration data loaded
  const hasConfigData = (): boolean => {
    return offices.length > 0;
  };

  // Update a specific lever override
  const updateLeverOverride = (
    officeName: string, 
    roleName: string, 
    levelName: string, 
    key: string, 
    value: any
  ) => {
    setLeverOverrides(prev => {
      const newOverrides = { ...prev };
      
      if (!newOverrides[officeName]) {
        newOverrides[officeName] = { roles: {} };
      }
      if (!newOverrides[officeName].roles[roleName]) {
        newOverrides[officeName].roles[roleName] = {};
      }
      if (!newOverrides[officeName].roles[roleName][levelName]) {
        newOverrides[officeName].roles[roleName][levelName] = {};
      }
      
      newOverrides[officeName].roles[roleName][levelName][key] = value;
      
      return newOverrides;
    });
  };

  // Build simulation overrides in the format expected by the backend
  const buildSimulationOverrides = (): Record<string, any> => {
    if (Object.keys(leverOverrides).length === 0) {
      return {};
    }
    return leverOverrides;
  };

  // Fetch configuration status from API
  const refreshConfigStatus = async () => {
    try {
      const response = await fetch('/api/offices/config/validation');
      if (response.ok) {
        const data = await response.json();
        setConfigStatus({
          checksum: data.checksum,
          status: data.status,
          summary: data.summary,
          timestamp: data.timestamp
        });
      } else {
        console.error('Failed to fetch config status:', response.statusText);
        setConfigStatus(null);
      }
    } catch (error) {
      console.error('Error fetching config status:', error);
      setConfigStatus(null);
    }
  };

  // Auto-refresh configuration status
  useEffect(() => {
    refreshConfigStatus();
    // Refresh every 30 seconds
    const interval = setInterval(refreshConfigStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  // Refresh config status when offices change
  useEffect(() => {
    if (offices.length > 0) {
      console.log('[CONFIG] Office data loaded:', offices.length, 'offices');
      // Refresh status after a short delay to let the backend process the changes
      setTimeout(refreshConfigStatus, 1000);
    }
  }, [offices]);

  // Log state changes for debugging
  useEffect(() => {
    if (offices.length > 0) {
      console.log('[CONFIG] Office data loaded:', offices.length, 'offices');
    }
  }, [offices]);

  useEffect(() => {
    if (Object.keys(leverOverrides).length > 0) {
      console.log('[CONFIG] Lever overrides updated:', leverOverrides);
    }
  }, [leverOverrides]);

  const value: ConfigContextType = {
    offices,
    setOffices,
    leverOverrides,
    setLeverOverrides,
    updateLeverOverride,
    configStatus,
    setConfigStatus,
    refreshConfigStatus,
    isLoading,
    setIsLoading,
    getOfficeData,
    hasConfigData,
    buildSimulationOverrides
  };

  return (
    <ConfigContext.Provider value={value}>
      {children}
    </ConfigContext.Provider>
  );
};

export const useConfig = (): ConfigContextType => {
  const context = useContext(ConfigContext);
  if (!context) {
    throw new Error('useConfig must be used within a ConfigProvider');
  }
  return context;
};

export default ConfigContext; 