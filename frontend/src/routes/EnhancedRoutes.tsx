import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { DashboardLayout } from '../components/layout/DashboardLayout'

// Import pages for routing
import { EnhancedDashboardV2 } from '../pages/EnhancedDashboardV2'
import { OfficesV2 } from '../pages/OfficesV2'
import { OfficeOverview } from '../pages/OfficeOverview'
import { OfficeViewWithTabs } from '../components/office/OfficeViewWithTabs'
import { ScenariosV2 } from '../pages/ScenariosV2'
import { ScenarioResultsV2 } from '../pages/ScenarioResultsV2'
import { SimulationLab } from '../pages/SimulationLab'
import { SettingsV2 } from '../pages/SettingsV2'
import { BusinessPlanningV2 } from '../pages/BusinessPlanningV2'
import { AggregatedBusinessPlanningV2 } from '../pages/AggregatedBusinessPlanningV2'
import ScenarioEditorTest from '../pages/ScenarioEditorTest'
import { ScenarioLeversPage } from '../pages/ScenarioLeversPage'
import { ScenarioEditPage } from '../pages/ScenarioEditPage'
import TypographyTest from '../components/TypographyTest'
import ButtonDemo from '../components/demos/ButtonDemo'

export function EnhancedRoutes() {
  return (
    <Routes>
      {/* All routes wrapped in DashboardLayout */}
      <Route path="/" element={<DashboardLayout />}>
        {/* Redirect root to dashboard */}
        <Route index element={<Navigate to="/dashboard" replace />} />
        
        {/* Main application routes */}
        <Route path="dashboard" element={<EnhancedDashboardV2 />} />
        
        {/* Office Management Routes */}
        <Route path="offices" element={<OfficeViewWithTabs />} />
        <Route path="offices/:officeId" element={<OfficesV2 />} />
        <Route path="office-overview/:officeId" element={<OfficeOverview />} />
        
        {/* Business Planning Routes */}
        <Route path="business-planning" element={<BusinessPlanningV2 />} />
        <Route path="business-planning/aggregated" element={<AggregatedBusinessPlanningV2 />} />
        
        {/* Scenario Routes */}
        <Route path="scenarios" element={<ScenariosV2 />} />
        <Route path="scenarios/new" element={<ScenariosV2 />} />
        <Route path="scenarios/:scenarioId/levers" element={<ScenarioLeversPage />} />
        <Route path="scenarios/:scenarioId/edit" element={<ScenarioEditPage />} />
        <Route path="scenarios/:scenarioId/results" element={<ScenarioResultsV2 />} />
        
        {/* Simulation Routes */}
        <Route path="simulation-lab" element={<SimulationLab />} />
        <Route path="simulation" element={<Navigate to="/simulation-lab" replace />} />
        
        {/* Settings Routes */}
        <Route path="settings" element={<SettingsV2 />} />
        
        {/* Development Routes */}
        <Route path="scenario-editor-test" element={<ScenarioEditorTest />} />
        <Route path="typography-test" element={<TypographyTest />} />
        <Route path="button-demo" element={<ButtonDemo />} />
        
        {/* Results Routes - redirect to dashboard for now */}
        <Route path="results" element={<Navigate to="/dashboard" replace />} />
        
        {/* Reports Routes - placeholder */}
        <Route path="reports" element={<Navigate to="/dashboard" replace />} />
        
        {/* Fallback for unmatched routes */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Route>
    </Routes>
  )
}