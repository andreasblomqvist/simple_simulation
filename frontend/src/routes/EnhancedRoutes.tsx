import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'

// Import V2 pages directly
import { DashboardV2 } from '../pages/DashboardV2'
import { EnhancedDashboardV2 } from '../pages/EnhancedDashboardV2'
import { AllOffices } from '../pages/AllOffices'
import { EnhancedAllOffices } from '../components/office-management/EnhancedAllOffices'
import { OfficeManagement } from '../pages/OfficeManagement'
import { Scenarios } from '../pages/Scenarios'
import { ScenariosV2 } from '../pages/ScenariosV2'
import { ScenarioResultsV2 } from '../pages/ScenarioResultsV2'
import { SimulationLab } from '../pages/SimulationLab'
import { Settings } from '../pages/Settings'
import { SettingsV2 } from '../pages/SettingsV2'
import { BusinessPlanningV2 } from '../pages/BusinessPlanningV2'
import ScenarioEditorTest from '../pages/ScenarioEditorTest'
import { ScenarioLeversPage } from '../pages/ScenarioLeversPage'
import { ScenarioEditPage } from '../pages/ScenarioEditPage'

export function EnhancedRoutes() {
  return (
    <Routes>
      {/* Redirect root to dashboard */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      
      {/* Main application routes - using V2 pages directly without double layouts */}
      <Route path="/dashboard" element={<EnhancedDashboardV2 />} />
      
      {/* Office Management Routes */}
      <Route path="/offices" element={<EnhancedAllOffices />} />
      <Route path="/offices/:id" element={<OfficeManagement />} />
      
      {/* Business Planning Routes */}
      <Route path="/business-planning" element={<BusinessPlanningV2 />} />
      
      {/* Scenario Routes */}
      <Route path="/scenarios" element={<ScenariosV2 />} />
      <Route path="/scenarios/:scenarioId/levers" element={<ScenarioLeversPage />} />
      <Route path="/scenarios/:scenarioId/edit" element={<ScenarioEditPage />} />
      <Route path="/scenarios/:scenarioId/results" element={<ScenarioResultsV2 />} />
      
      {/* Simulation Routes */}
      <Route path="/simulation" element={<SimulationLab />} />
      
      {/* Settings Routes */}
      <Route path="/settings" element={<SettingsV2 />} />
      
      {/* Development Routes */}
      <Route path="/scenario-editor-test" element={<ScenarioEditorTest />} />
      
      {/* Reports Routes - placeholder */}
      <Route path="/reports" element={<Navigate to="/dashboard" replace />} />
      
      {/* Fallback for unmatched routes */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}