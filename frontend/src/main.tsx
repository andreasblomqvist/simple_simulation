import React, { useState } from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './index.css';
import Layout from './components/Layout';

import Dashboard from './pages/Dashboard';
import AllOffices from './pages/AllOffices';
import GrowthProjections from './pages/GrowthProjections';
import SeniorityAnalysis from './pages/SeniorityAnalysis';
import Configuration from './pages/Configuration';
import SimulationLabV2 from './pages/SimulationLabV2';
import Settings from './pages/Settings';
import InsightsTab from './pages/InsightsTab';
import SystemConfig from './pages/SystemConfig';
import ScenarioRunner from './pages/ScenarioRunner';

import { ThemeProvider } from './components/ThemeContext';
import { YearNavigationProvider } from './components/v2/YearNavigationProvider';
import 'antd/dist/reset.css';
import { ConfigProvider, theme, Button, App as AntdApp } from 'antd';
import { ConfigProvider as CustomConfigProvider } from './components/ConfigContext';

// Stagewise imports removed - packages not available

function MainApp() {
  const [isDark, setIsDark] = useState(true);
  return (
    <ConfigProvider theme={{ algorithm: isDark ? theme.darkAlgorithm : theme.defaultAlgorithm }}>
      <ThemeProvider>
        <CustomConfigProvider>
          <BrowserRouter>
            {/* Stagewise Toolbar removed - packages not available */}
            
            <div style={{ position: 'fixed', top: 16, right: 16, zIndex: 1000 }}>
              <Button onClick={() => setIsDark(d => !d)}>
                Switch to {isDark ? 'Light' : 'Dark'} Mode
              </Button>
            </div>
            <YearNavigationProvider>
              <Layout>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/offices" element={<AllOffices />} />
                  <Route path="/growth" element={<GrowthProjections />} />
                  <Route path="/seniority" element={<SeniorityAnalysis />} />
                  <Route path="/config" element={<Configuration />} />
                  <Route path="/lab" element={<SimulationLabV2 />} />
                  <Route path="/settings" element={<Settings />} />
                  <Route path="/insights" element={<InsightsTab />} />
                  <Route path="/scenario-runner" element={<ScenarioRunner />} />
                  <Route path="/system-config" element={<SystemConfig />} />
                </Routes>
              </Layout>
            </YearNavigationProvider>
          </BrowserRouter>
        </CustomConfigProvider>
      </ThemeProvider>
    </ConfigProvider>
  );
}

ReactDOM.createRoot(document.getElementById('app')!).render(
  <React.StrictMode>
    <AntdApp>
      <MainApp />
    </AntdApp>
  </React.StrictMode>
);
