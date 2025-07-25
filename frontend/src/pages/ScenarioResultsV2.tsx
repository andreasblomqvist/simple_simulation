import React, { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { 
  ArrowLeft,
  Download,
  RefreshCw,
  Calendar,
  Building2,
  Target
} from 'lucide-react'

import { Button } from '../components/ui/button'
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '../components/ui/card'

// Import existing types and services
import type { ScenarioId, SimulationResults } from '../types/unified-data-structures'
import { scenarioApi } from '../services/scenarioApi'
import { showMessage } from '../utils/message'

// Import modern results component
import ModernResultsDisplay from '../components/scenario-runner/ModernResultsDisplay'

interface ScenarioResultsV2Props {}

export const ScenarioResultsV2: React.FC<ScenarioResultsV2Props> = () => {
  const { scenarioId } = useParams<{ scenarioId: string }>()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [scenario, setScenario] = useState<any>(null)
  const [results, setResults] = useState<SimulationResults | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (scenarioId) {
      loadScenarioAndResults(scenarioId)
    }
  }, [scenarioId])

  const loadScenarioAndResults = async (id: ScenarioId) => {
    try {
      setLoading(true)
      setError(null)
      
      // Load scenario details
      const scenarioData = await scenarioApi.getScenario(id)
      setScenario(scenarioData)

      // Try to load results
      try {
        const resultsData = await scenarioApi.getScenarioResults(id)
        setResults(resultsData)
      } catch (resultsError) {
        console.warn('No results found for scenario:', id)
        setResults(null)
      }
    } catch (error) {
      setError('Failed to load scenario: ' + (error as Error).message)
      showMessage.error('Failed to load scenario: ' + (error as Error).message)
    } finally {
      setLoading(false)
    }
  }

  const handleRunSimulation = async () => {
    if (!scenarioId) return
    
    try {
      showMessage.info('Starting simulation...')
      setLoading(true)
      await scenarioApi.runScenarioById(scenarioId)
      showMessage.success('Simulation completed successfully')
      // Reload results
      await loadScenarioAndResults(scenarioId)
    } catch (error) {
      showMessage.error('Failed to run simulation: ' + (error as Error).message)
    } finally {
      setLoading(false)
    }
  }

  const handleExport = () => {
    showMessage.info('Export functionality coming soon')
  }

  if (loading && !scenario) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2">
          <RefreshCw className="h-4 w-4 animate-spin" />
          <span>Loading scenario...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center space-x-4">
          <Link to="/scenarios">
            <Button variant="outline" size="sm">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Scenarios
            </Button>
          </Link>
        </div>
        
        <Card>
          <CardContent className="pt-6">
            <div className="text-center text-red-600">
              <p>{error}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }


  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link to="/scenarios">
            <Button variant="outline" size="sm">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Scenarios
            </Button>
          </Link>
          
          <div>
            <h1 className="text-2xl font-bold tracking-tight">
              {scenario?.name || 'Scenario Results'}
            </h1>
            <p className="text-muted-foreground">
              {scenario?.description || 'Simulation results and analysis'}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {results && (
            <Button variant="outline" onClick={handleExport}>
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
          )}
          <Button onClick={handleRunSimulation} disabled={loading}>
            {loading ? (
              <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Target className="mr-2 h-4 w-4" />
            )}
            {results ? 'Re-run Simulation' : 'Run Simulation'}
          </Button>
        </div>
      </div>

      {/* Scenario Info */}
      {scenario && (
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Time Range</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-lg font-bold">
                {scenario.time_range?.start_month}/{scenario.time_range?.start_year} - {scenario.time_range?.end_month}/{scenario.time_range?.end_year}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Office Scope</CardTitle>
              <Building2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-lg font-bold">
                {scenario.office_scope?.length === 1 && scenario.office_scope[0] === 'Group' 
                  ? 'All Offices'
                  : scenario.office_scope?.length === 1 
                    ? scenario.office_scope[0]
                    : `${scenario.office_scope?.length || 0} offices`
                }
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Status</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-lg font-bold">
                {results ? 'Complete' : 'Not Run'}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {!results ? (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <Target className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">No Results Available</h3>
              <p className="text-muted-foreground mb-4">
                This scenario hasn't been run yet. Click "Run Simulation" to generate results.
              </p>
              <Button onClick={handleRunSimulation} disabled={loading}>
                {loading ? (
                  <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Target className="mr-2 h-4 w-4" />
                )}
                Run Simulation
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <ModernResultsDisplay result={{
          scenario_id: scenarioId || '',
          scenario_name: scenario?.name || '',
          execution_time: 0,
          results: results || {},
          status: 'success'
        }} />
      )}
    </div>
  )
}