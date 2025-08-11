import React, { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Alert, AlertDescription } from '../components/ui/alert'
import { ArrowLeft, Play, Settings, Edit, Eye, AlertCircle } from 'lucide-react'
import ScenarioLeversV2, { ScenarioLeversRef } from '../components/scenario-runner/ScenarioLeversV2'
import { scenarioApi } from '../services/scenarioApi'
import { showMessage } from '../utils/message'
import type { ScenarioDefinition, ScenarioResponse } from '../types/unified-data-structures'

export const ScenarioLeversPage: React.FC = () => {
  const { scenarioId } = useParams<{ scenarioId: string }>()
  const navigate = useNavigate()
  const leversRef = useRef<ScenarioLeversRef>(null)
  
  const [scenario, setScenario] = useState<ScenarioDefinition | null>(null)
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const redirectedRef = useRef(false)

  useEffect(() => {
    if (scenarioId && !redirectedRef.current) {
      loadScenario()
    }
  }, [scenarioId])

  const loadScenario = async () => {
    if (!scenarioId) return

    try {
      setLoading(true)
      setError(null)
      const scenarioData = await scenarioApi.getScenario(scenarioId)
      console.log('DEBUG: Loaded scenario data:', scenarioData)
      console.log('DEBUG: Scenario levers:', scenarioData.levers)
      setScenario(scenarioData)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load scenario'
      console.log('Error loading scenario:', errorMessage)
      
      // If scenario not found (404), redirect to scenarios list
      if (errorMessage.includes('Scenario not found') || errorMessage.includes('404')) {
        if (!redirectedRef.current) {
          console.log('Scenario not found, redirecting to scenarios list')
          redirectedRef.current = true
          showMessage.error('Scenario not found, redirecting to scenarios list')
          navigate('/scenarios')
        }
        return
      }
      
      setError(errorMessage)
      showMessage.error('Failed to load scenario')
    } finally {
      setLoading(false)
    }
  }

  const handleRunSimulation = async () => {
    if (!scenarioId || !leversRef.current) return

    try {
      setRunning(true)
      const leversData = leversRef.current.getCurrentData()
      
      console.log('DEBUG: Levers data from component:', leversData)
      
      // Update scenario with current lever values before running
      const updatedScenario = {
        ...scenario,
        levers: leversData
      }
      
      console.log('DEBUG: Updated scenario being sent:', updatedScenario)
      
      showMessage.info('Starting simulation...')
      const result = await scenarioApi.runScenarioDefinition(updatedScenario as ScenarioDefinition)
      showMessage.success('Simulation completed successfully')
      navigate(`/scenarios/${scenarioId}/results`)
    } catch (err) {
      showMessage.error('Failed to run simulation: ' + (err instanceof Error ? err.message : 'Unknown error'))
    } finally {
      setRunning(false)
    }
  }

  const handleEditScenario = () => {
    navigate(`/scenarios/${scenarioId}/edit`)
  }

  const handleViewResults = () => {
    navigate(`/scenarios/${scenarioId}/results`)
  }

  const handleBack = () => {
    navigate('/scenarios')
  }

  const formatTimeRange = (scenario: ScenarioDefinition) => {
    const { start_year, start_month, end_year, end_month } = scenario.time_range
    return `${start_month}/${start_year} - ${end_month}/${end_year}`
  }

  const formatOfficeScope = (scope: string[]) => {
    if (scope.length === 1 && scope[0] === 'Group') {
      return 'All Offices'
    }
    return scope.length === 1 ? scope[0] : `${scope.length} offices`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center space-y-2">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Loading scenario...</p>
        </div>
      </div>
    )
  }

  if (error || !scenario) {
    return (
      <div className="space-y-6">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" onClick={handleBack}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Scenarios
          </Button>
        </div>
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error || 'Scenario not found'}
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" onClick={handleBack}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Scenarios
          </Button>
          <div className="space-y-1">
            <h1 className="text-2xl font-bold flex items-center">
              <Settings className="mr-2 h-6 w-6" />
              {scenario.name}
            </h1>
            <p className="text-muted-foreground">{scenario.description}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={handleViewResults}>
            <Eye className="h-4 w-4 mr-2" />
            View Results
          </Button>
          <Button variant="outline" onClick={handleEditScenario}>
            <Edit className="h-4 w-4 mr-2" />
            Edit
          </Button>
          <Button onClick={handleRunSimulation} disabled={running}>
            {running ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                Running...
              </>
            ) : (
              <>
                <Play className="h-4 w-4 mr-2" />
                Run Simulation
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Scenario Info */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Scenario Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-sm font-medium text-muted-foreground">Time Range</label>
              <p className="text-sm">{formatTimeRange(scenario)}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Office Scope</label>
              <p className="text-sm">{formatOfficeScope(scenario.office_scope)}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Created</label>
              <p className="text-sm">
                {scenario.created_at ? new Date(scenario.created_at).toLocaleDateString() : 'N/A'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Scenario Levers */}
      <ScenarioLeversV2
        ref={leversRef}
        levers={scenario.levers}
        readOnly={false}
        onRunSimulation={handleRunSimulation}
      />
    </div>
  )
}