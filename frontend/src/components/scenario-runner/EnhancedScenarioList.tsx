import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Edit, Trash2, Download, Eye, Play } from 'lucide-react'
import { EnhancedDataTable, EnhancedColumnDef } from '../ui/enhanced-data-table'
import { Button } from '../ui/button'
import { Badge } from '../ui/badge'
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '../ui/dropdown-menu'
import { ScenarioDeleteDialog } from '../ui/business-modals'
import { LoadingSpinner } from '../ui/loading-states'
import { useToast } from '../ui/use-toast'
import type { ScenarioListItem, ScenarioId } from '../../types/unified-data-structures'
import { scenarioApi } from '../../services/scenarioApi'

interface EnhancedScenarioListProps {
  onNext: () => void
  onEdit?: (id: ScenarioId) => void
  onDelete?: (id: ScenarioId) => void
  onCompare?: () => void
  onExport?: () => void
  onView?: (id: ScenarioId) => void
  hideHeader?: boolean
  scenarios: ScenarioListItem[]
  setScenarios: React.Dispatch<React.SetStateAction<ScenarioListItem[]>>
}

export const EnhancedScenarioList: React.FC<EnhancedScenarioListProps> = ({
  onNext,
  onEdit,
  onDelete,
  onCompare,
  onExport,
  onView,
  hideHeader,
  scenarios,
  setScenarios
}) => {
  const [loading, setLoading] = useState(true)
  const [selectedRows, setSelectedRows] = useState<Set<string | number>>(new Set())
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [scenarioToDelete, setScenarioToDelete] = useState<ScenarioId | null>(null)
  const navigate = useNavigate()
  const { toast } = useToast()

  useEffect(() => {
    loadScenarios()
  }, [])

  const loadScenarios = async () => {
    try {
      setLoading(true)
      const scenarioList = await scenarioApi.listScenarios()
      setScenarios(scenarioList)
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load scenarios: ' + (error as Error).message,
        variant: 'destructive'
      })
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (scenarioId: ScenarioId) => {
    try {
      if (!scenarioId || scenarioId === 'undefined' || scenarioId === 'null') {
        toast({
          title: 'Error',
          description: 'Invalid scenario ID',
          variant: 'destructive'
        })
        return
      }
      
      await scenarioApi.deleteScenario(scenarioId)
      toast({
        title: 'Success',
        description: 'Scenario deleted successfully'
      })
      loadScenarios()
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete scenario: ' + (error as Error).message,
        variant: 'destructive'
      })
    }
  }

  const handleExport = async (scenarioId: ScenarioId) => {
    try {
      if (!scenarioId || scenarioId === 'undefined' || scenarioId === 'null') {
        toast({
          title: 'Error',
          description: 'Invalid scenario ID',
          variant: 'destructive'
        })
        return
      }
      
      const blob = await scenarioApi.exportScenarioResults(scenarioId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `scenario-${scenarioId}.xlsx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      toast({
        title: 'Success',
        description: 'Scenario exported successfully'
      })
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to export scenario: ' + (error as Error).message,
        variant: 'destructive'
      })
    }
  }

  const confirmDelete = (scenarioId: ScenarioId) => {
    setScenarioToDelete(scenarioId)
    setDeleteDialogOpen(true)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const getStatusVariant = (status: string) => {
    // Add status mapping logic here based on your scenario statuses
    return 'secondary'
  }

  const columns: EnhancedColumnDef<ScenarioListItem>[] = [
    {
      key: 'name',
      title: 'Scenario Name',
      sortable: true,
      render: (value: string, record: ScenarioListItem) => (
        <div className="space-y-1">
          <div className="font-medium">{value}</div>
          {record.description && (
            <div className="text-sm text-muted-foreground line-clamp-2">
              {record.description}
            </div>
          )}
        </div>
      )
    },
    {
      key: 'office_scope',
      title: 'Office Scope',
      sortable: true,
      render: (scope: string[] | undefined) => {
        if (!scope || scope.length === 0) return <span className="text-muted-foreground">—</span>
        
        const displayScope = Array.isArray(scope)
          ? (scope.includes('Group') ? 'Group' : scope.join(', '))
          : String(scope)
          
        return <Badge variant="outline">{displayScope}</Badge>
      }
    },
    {
      key: 'time_range',
      title: 'Duration',
      sortable: true,
      render: (tr: any) => {
        if (!tr) return <span className="text-muted-foreground">—</span>
        return (
          <div className="text-sm">
            {tr.start_year}-{String(tr.start_month).padStart(2, '0')} to{' '}
            {tr.end_year}-{String(tr.end_month).padStart(2, '0')}
          </div>
        )
      }
    },
    {
      key: 'created_at',
      title: 'Created',
      sortable: true,
      render: (date: string) => (
        <div className="text-sm text-muted-foreground">
          {formatDate(date)}
        </div>
      )
    },
    {
      key: 'updated_at',
      title: 'Updated',
      sortable: true,
      render: (date: string) => (
        <div className="text-sm text-muted-foreground">
          {formatDate(date)}
        </div>
      )
    },
    {
      key: 'actions',
      title: 'Actions',
      width: '120px',
      render: (_, record: ScenarioListItem) => (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm">
              Actions
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem
              onClick={() => {
                if (record.id && record.id !== 'undefined' && record.id !== 'null') {
                  navigate(`/scenario-runner/${record.id}`)
                }
              }}
            >
              <Eye className="mr-2 h-4 w-4" />
              View Details
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => {
                if (record.id && record.id !== 'undefined' && record.id !== 'null') {
                  navigate(`/simulation/${record.id}`)
                }
              }}
            >
              <Play className="mr-2 h-4 w-4" />
              Run Simulation
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => {
                if (record.id && record.id !== 'undefined' && record.id !== 'null') {
                  onEdit?.(record.id)
                }
              }}
            >
              <Edit className="mr-2 h-4 w-4" />
              Edit
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => {
                if (record.id && record.id !== 'undefined' && record.id !== 'null') {
                  handleExport(record.id)
                }
              }}
            >
              <Download className="mr-2 h-4 w-4" />
              Export
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => {
                if (record.id && record.id !== 'undefined' && record.id !== 'null') {
                  confirmDelete(record.id)
                }
              }}
              className="text-destructive"
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      )
    }
  ]

  const handleRowClick = (record: ScenarioListItem) => {
    if (record.id && record.id !== 'undefined' && record.id !== 'null') {
      navigate(`/scenario-runner/${record.id}`)
    }
  }

  const handleBulkExport = () => {
    if (selectedRows.size === 0) return
    
    // Export selected scenarios
    toast({
      title: 'Export Started',
      description: `Exporting ${selectedRows.size} scenarios...`
    })
  }

  const handleBulkDelete = () => {
    if (selectedRows.size === 0) return
    
    // Delete selected scenarios
    toast({
      title: 'Delete Confirmation',
      description: `Are you sure you want to delete ${selectedRows.size} scenarios?`
    })
  }

  const headerActions = (
    <div className="flex items-center gap-2">
      {selectedRows.size > 0 && (
        <>
          <Button variant="outline" size="sm" onClick={handleBulkExport}>
            <Download className="mr-2 h-4 w-4" />
            Export Selected
          </Button>
          <Button variant="outline" size="sm" onClick={handleBulkDelete}>
            <Trash2 className="mr-2 h-4 w-4" />
            Delete Selected
          </Button>
        </>
      )}
      <Button onClick={onNext}>
        Create New Scenario
      </Button>
    </div>
  )

  return (
    <>
      <EnhancedDataTable
        data={scenarios}
        columns={columns}
        loading={loading}
        title={hideHeader ? undefined : "Scenario Management"}
        description={hideHeader ? undefined : "Create and compare different organizational growth scenarios"}
        searchable
        searchPlaceholder="Search scenarios..."
        selectable
        selectedRows={selectedRows}
        onSelectionChange={setSelectedRows}
        onRowClick={handleRowClick}
        pagination
        defaultPageSize={10}
        pageSizeOptions={[5, 10, 25, 50]}
        exportable
        onExport={onExport}
        onRefresh={loadScenarios}
        getRowKey={(record) => record.id || ''}
        actions={headerActions}
        emptyMessage="No scenarios found. Create your first scenario to get started."
      />

      {/* Delete Confirmation Dialog */}
      <ScenarioDeleteDialog
        open={deleteDialogOpen}
        onClose={() => {
          setDeleteDialogOpen(false)
          setScenarioToDelete(null)
        }}
        onConfirm={() => {
          if (scenarioToDelete) {
            handleDelete(scenarioToDelete)
            setDeleteDialogOpen(false)
            setScenarioToDelete(null)
          }
        }}
        scenarioName={
          scenarioToDelete 
            ? scenarios.find(s => s.id === scenarioToDelete)?.name || 'this scenario'
            : 'this scenario'
        }
        loading={loading}
      />
    </>
  )
}