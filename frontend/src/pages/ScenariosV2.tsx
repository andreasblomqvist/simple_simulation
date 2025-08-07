import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { 
  MoreHorizontal, 
  Plus, 
  Eye, 
  Edit, 
  Trash2, 
  Play, 
  BarChart3,
  Target,
  Calendar,
  Building2,
  Settings,
  Camera,
  Database
} from 'lucide-react'

import { Button } from '../components/ui/button'
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '../components/ui/card'
import { DataTableMinimal, MinimalColumnDef } from '../components/ui/data-table-minimal'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../components/ui/dropdown-menu'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../components/ui/dialog'

// Import existing types and services
import type { ScenarioListItem, ScenarioId } from '../types/unified-data-structures'
import { scenarioApi } from '../services/scenarioApi'
import { showMessage } from '../utils/message'
import { Badge } from '../components/ui/badge'

// Import existing components for modal/drawer content
import ScenarioWizardV2 from '../components/scenario-runner/ScenarioWizardV2'

interface ScenariosV2Props {}

export const ScenariosV2: React.FC<ScenariosV2Props> = () => {
  const [scenarios, setScenarios] = useState<ScenarioListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedScenarios, setSelectedScenarios] = useState<ScenarioId[]>([])
  const [showWizard, setShowWizard] = useState(false)
  const [editingScenario, setEditingScenario] = useState<ScenarioListItem | null>(null)
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    loadScenarios()
  }, [])

  // Auto-open wizard for /scenarios/new path
  useEffect(() => {
    if (location.pathname === '/scenarios/new') {
      setShowWizard(true)
    }
  }, [location.pathname])

  const loadScenarios = async () => {
    try {
      setLoading(true)
      const scenarioList = await scenarioApi.listScenarios()
      setScenarios(scenarioList)
    } catch (error) {
      showMessage.error('Failed to load scenarios: ' + (error as Error).message)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (scenarioId: ScenarioId) => {
    try {
      await scenarioApi.deleteScenario(scenarioId)
      showMessage.success('Scenario deleted successfully')
      loadScenarios()
    } catch (error) {
      showMessage.error('Failed to delete scenario: ' + (error as Error).message)
    }
  }

  const handleEdit = (scenario: ScenarioListItem) => {
    setEditingScenario(scenario)
    setShowWizard(true)
  }

  const handleView = (scenarioId: ScenarioId) => {
    navigate(`/scenarios/${scenarioId}/levers`)
  }

  const handleViewResults = (scenarioId: ScenarioId) => {
    navigate(`/scenarios/${scenarioId}/results`)
  }

  const handleRun = async (scenarioId: ScenarioId) => {
    try {
      showMessage.info('Starting simulation...')
      const result = await scenarioApi.runScenarioById(scenarioId)
      showMessage.success('Simulation completed successfully')
      navigate(`/scenarios/${scenarioId}/results`)
    } catch (error) {
      showMessage.error('Failed to run simulation: ' + (error as Error).message)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const formatOfficeScope = (scope: string[]) => {
    if (scope.length === 1 && scope[0] === 'Group') {
      return 'All Offices'
    }
    return scope.length === 1 ? scope[0] : `${scope.length} offices`
  }

  const columns: MinimalColumnDef<ScenarioListItem>[] = [
    {
      accessorKey: "name",
      header: "Name",
      cell: ({ row }) => {
        const scenario = row.original
        return (
          <div className="space-y-1">
            <div className="font-medium">{scenario.name}</div>
            <div className="text-sm text-muted-foreground line-clamp-2">
              {scenario.description}
            </div>
          </div>
        )
      },
    },
    {
      accessorKey: "office_scope",
      header: "Scope",
      cell: ({ row }) => {
        const scope = row.getValue("office_scope") as string[]
        return (
          <div className="flex items-center space-x-2">
            <Building2 className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm">{formatOfficeScope(scope)}</span>
          </div>
        )
      },
    },
    {
      accessorKey: "time_range",
      header: "Time Range",
      cell: ({ row }) => {
        const timeRange = row.getValue("time_range") as { start_year: number; start_month: number; end_year: number; end_month: number }
        return (
          <div className="flex items-center space-x-2">
            <Calendar className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm">
              {timeRange.start_month}/{timeRange.start_year} - {timeRange.end_month}/{timeRange.end_year}
            </span>
          </div>
        )
      },
    },
    {
      accessorKey: "baseline_snapshot",
      header: "Baseline",
      cell: ({ row }) => {
        // Check if scenario has snapshot baseline information
        const scenario = row.original;
        const hasSnapshot = scenario.baseline_input && 
                           typeof scenario.baseline_input === 'object' &&
                           'snapshot_id' in scenario.baseline_input;
        
        return (
          <div className="flex items-center space-x-2">
            {hasSnapshot ? (
              <>
                <Camera className="h-4 w-4 text-blue-500" />
                <Badge variant="outline" className="text-xs">
                  Snapshot
                </Badge>
              </>
            ) : (
              <>
                <Database className="h-4 w-4 text-muted-foreground" />
                <span className="text-xs text-muted-foreground">
                  Current Data
                </span>
              </>
            )}
          </div>
        );
      },
    },
    {
      accessorKey: "created_at",
      header: "Created",
      cell: ({ row }) => (
        <span className="text-sm text-muted-foreground">
          {formatDate(row.getValue("created_at"))}
        </span>
      ),
    },
    {
      id: "actions",
      enableHiding: false,
      cell: ({ row }) => {
        const scenario = row.original

        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0">
                <span className="sr-only">Open menu</span>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>Actions</DropdownMenuLabel>
              <DropdownMenuItem onClick={() => handleView(scenario.id)}>
                <Settings className="mr-2 h-4 w-4" />
                View Levers
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleViewResults(scenario.id)}>
                <Eye className="mr-2 h-4 w-4" />
                View Results
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleRun(scenario.id)}>
                <Play className="mr-2 h-4 w-4" />
                Run Simulation
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => handleEdit(scenario)}>
                <Edit className="mr-2 h-4 w-4" />
                Edit Scenario
              </DropdownMenuItem>
              <DropdownMenuItem 
                onClick={() => handleDelete(scenario.id)}
                className="text-destructive"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )
      },
    },
  ]


  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h2 className="text-2xl font-bold tracking-tight flex items-center">
            <Target className="mr-2 h-6 w-6" />
            Scenarios
          </h2>
          <p className="text-muted-foreground">
            Create and manage simulation scenarios to model different business conditions
          </p>
        </div>
        <Button onClick={() => setShowWizard(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Create Scenario
        </Button>
      </div>

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Scenarios</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{scenarios.length}</div>
            <p className="text-xs text-muted-foreground">
              Available scenarios
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Snapshot Based</CardTitle>
            <Camera className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {scenarios.filter(s => 
                s.baseline_input && 
                typeof s.baseline_input === 'object' &&
                'snapshot_id' in s.baseline_input
              ).length}
            </div>
            <p className="text-xs text-muted-foreground">
              Using historical snapshots
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Simulations</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-muted-foreground">
              Currently running
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Scenarios Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Scenarios</CardTitle>
          <CardDescription>
            Manage your simulation scenarios and view results
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DataTableMinimal
            columns={columns}
            data={scenarios}
            onRowClick={(scenario) => handleView(scenario.id)}
          />
        </CardContent>
      </Card>

      {/* Scenario Dialog */}
      <Dialog open={showWizard} onOpenChange={setShowWizard}>
        <DialogContent className="max-w-[95vw] max-h-[95vh] overflow-hidden p-0">
          <DialogHeader className="border-b border-border pb-4 px-6 pt-6">
            <DialogTitle className="text-xl">
              {editingScenario ? 'Edit Scenario' : 'Create Scenario'}
            </DialogTitle>
            <DialogDescription>
              {editingScenario ? 'Modify your simulation scenario' : 'Set up a new simulation scenario'}
            </DialogDescription>
          </DialogHeader>
          
          <div className="flex-1 overflow-y-auto max-h-[calc(95vh-8rem)]">
            <ScenarioWizardV2
              scenario={editingScenario}
              id={editingScenario?.id}
              onCancel={() => {
                setShowWizard(false)
                setEditingScenario(null)
              }}
              onComplete={() => {
                setShowWizard(false)
                setEditingScenario(null)
                loadScenarios()
              }}
            />
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}