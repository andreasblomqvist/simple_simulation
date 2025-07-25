import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Button } from '../components/ui/button'
import { Alert, AlertDescription } from '../components/ui/alert'
import { ArrowLeft, AlertCircle } from 'lucide-react'
import ScenarioWizardV2 from '../components/scenario-runner/ScenarioWizardV2'
import { scenarioApi } from '../services/scenarioApi'
import { showMessage } from '../utils/message'
import type { ScenarioDefinition } from '../types/unified-data-structures'

export const ScenarioEditPage: React.FC = () => {
  const { scenarioId } = useParams<{ scenarioId: string }>()
  const navigate = useNavigate()
  
  const [scenario, setScenario] = useState<ScenarioDefinition | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (scenarioId) {
      loadScenario()
    }
  }, [scenarioId])

  const loadScenario = async () => {
    if (!scenarioId) return

    try {
      setLoading(true)
      setError(null)
      const scenarioData = await scenarioApi.getScenario(scenarioId)
      setScenario(scenarioData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load scenario')
      showMessage.error('Failed to load scenario')
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    navigate(`/scenarios/${scenarioId}/levers`)
  }

  const handleComplete = () => {
    showMessage.success('Scenario updated successfully')
    navigate(`/scenarios/${scenarioId}/levers`)
  }

  const handleBack = () => {
    navigate('/scenarios')
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
      <div className="flex items-center space-x-4">
        <Button variant="ghost" onClick={handleBack}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Scenarios
        </Button>
        <div className="space-y-1">
          <h1 className="text-2xl font-bold">Edit Scenario</h1>
          <p className="text-muted-foreground">Modify your simulation scenario</p>
        </div>
      </div>

      {/* Scenario Wizard */}
      <ScenarioWizardV2
        scenario={scenario}
        id={scenarioId}
        onCancel={handleCancel}
        onComplete={handleComplete}
      />
    </div>
  )
}