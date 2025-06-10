import React from 'react';
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

function Placeholder({ title }: { title: string }) {
  return <div className="text-2xl text-gray-400 text-center mt-20">[{title} page coming soon]</div>;
}

ReactDOM.createRoot(document.getElementById('app')!).render(
  <React.StrictMode>
    <ThemeProvider>
      <BrowserRouter>
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
  </React.StrictMode>
);
