import React, { createContext, useContext, useState } from 'react';

// Type for the levers/config state (can be improved with your actual types)
export type LeversState = Record<string, any>;

interface ConfigContextType {
  levers: LeversState;
  setLevers: React.Dispatch<React.SetStateAction<LeversState>>;
}

const ConfigContext = createContext<ConfigContextType | undefined>(undefined);

export function ConfigProvider({ children }: { children: React.ReactNode }) {
  const [levers, setLevers] = useState<LeversState>({});
  return (
    <ConfigContext.Provider value={{ levers, setLevers }}>
      {children}
    </ConfigContext.Provider>
  );
}

export function useConfig() {
  const ctx = useContext(ConfigContext);
  if (!ctx) throw new Error('useConfig must be used within a ConfigProvider');
  return ctx;
} 