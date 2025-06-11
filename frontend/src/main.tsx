import React, { useState } from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './index.css';
import Layout from './components/Layout';
import App from './App';
import Dashboard from './pages/Dashboard';
import AllOffices from './pages/AllOffices';
import GrowthProjections from './pages/GrowthProjections';
import SeniorityAnalysis from './pages/SeniorityAnalysis';
import Configuration from './pages/Configuration';
import SimulationLab from './pages/SimulationLab';
import Settings from './pages/Settings';
import { ThemeProvider } from './components/ThemeContext';
import 'antd/dist/reset.css';
import { ConfigProvider, theme, Button, App as AntdApp } from 'antd';

function Placeholder({ title }: { title: string }) {
  return <div className="text-2xl text-gray-400 text-center mt-20">[{title} page coming soon]</div>;
}

function MainApp() {
  const [isDark, setIsDark] = useState(true);
  return (
    <ConfigProvider theme={{ algorithm: isDark ? theme.darkAlgorithm : theme.defaultAlgorithm }}>
      <ThemeProvider>
        <BrowserRouter>
          <div style={{ position: 'fixed', top: 16, right: 16, zIndex: 1000 }}>
            <Button onClick={() => setIsDark(d => !d)}>
              Switch to {isDark ? 'Light' : 'Dark'} Mode
            </Button>
          </div>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/offices" element={<AllOffices />} />
              <Route path="/growth" element={<GrowthProjections />} />
              <Route path="/seniority" element={<SeniorityAnalysis />} />
              <Route path="/config" element={<Configuration />} />
              <Route path="/lab" element={<SimulationLab />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Layout>
        </BrowserRouter>
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
