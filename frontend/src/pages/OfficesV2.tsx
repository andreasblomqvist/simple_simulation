import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { MinimalColumnDef } from '../components/ui/data-table-minimal'
import { 
  Building2, 
  Plus, 
  Settings, 
  Users, 
  MapPin,
  ArrowLeft,
  Edit,
  Eye,
  TrendingUp
} from 'lucide-react'

import { Button } from '../components/ui/button'
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '../components/ui/card'
import { DataTableMinimal } from '../components/ui/data-table-minimal'
import { Input } from '../components/ui/input'
import { NumericCell, PercentageCell } from '../components/ui/data-table-helpers'

// Import existing stores and types
import { useOfficeStore } from '../stores/officeStore'
import type { OfficeConfig } from '../types/office'

// Import existing office configuration component
import { OfficeConfigPageWrapper } from '../components/office-config/OfficeConfigPageWrapper'

interface OfficesV2Props {}

interface OfficeListItem {
  id: string
  name: string
  total_fte: number
  journey: string
  location?: string
  economic_parameters?: {
    cost_of_living: number
    market_multiplier: number
    tax_rate: number
  }
}

export const OfficesV2: React.FC<OfficesV2Props> = () => {
  const { officeId } = useParams<{ officeId: string }>()
  const navigate = useNavigate()
  const [selectedOffice, setSelectedOffice] = useState<OfficeConfig | null>(null)
  
  console.log('OfficesV2 component rendered with officeId:', officeId);

  const {
    offices,
    currentOffice,
    loading,
    error,
    loadOffices,
    selectOffice
  } = useOfficeStore()

  useEffect(() => {
    loadOffices()
  }, []) // Remove loadOffices from dependency array to prevent infinite loop

  useEffect(() => {
    if (officeId && offices.length > 0) {
      const office = offices.find(o => o.id === officeId)
      if (office) {
        setSelectedOffice(office)
        selectOffice(office.id)
      }
    } else {
      setSelectedOffice(null)
    }
  }, [officeId, offices, selectOffice])

  const handleOfficeSelect = (office: OfficeListItem) => {
    console.log('Row clicked, navigating to:', `/office-overview/${office.id}`);
    console.log('Office object:', office);
    navigate(`/office-overview/${office.id}`)
  }

  const handleBackToList = () => {
    navigate('/offices')
  }


  const formatLocation = (office: OfficeListItem) => {
    return office.location || office.name
  }

  const formatJourney = (journey: string) => {
    const journeyMap: Record<string, string> = {
      'mature': 'Mature',
      'growth': 'Growth', 
      'startup': 'Startup',
      'established': 'Established'
    }
    return journeyMap[journey] || journey
  }

  const columns: MinimalColumnDef<OfficeListItem>[] = [
    {
      accessorKey: "name",
      header: "Office",
      cell: ({ row }) => {
        const office = row.original
        return (
          <div 
            className="space-y-1 cursor-pointer hover:bg-gray-50 p-2 rounded"
            onClick={(e) => {
              e.stopPropagation();
              console.log('Office name clicked:', office.name);
              handleOfficeSelect(office);
            }}
          >
            <div className="font-medium">{office.name}</div>
            <div className="flex items-center text-sm text-muted-foreground">
              <MapPin className="mr-1 h-3 w-3" />
              {formatLocation(office)}
            </div>
          </div>
        )
      },
    },
    {
      accessorKey: "total_fte",
      header: "Total FTE",
      cell: ({ row }) => (
        <div className="flex items-center">
          <Users className="mr-2 h-4 w-4 text-muted-foreground" />
          <NumericCell value={Math.round(row.getValue("total_fte") as number)} />
        </div>
      ),
    },
    {
      accessorKey: "journey",
      header: "Journey",
      cell: ({ row }) => {
        const journey = row.getValue("journey") as string
        return (
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
            journey === 'mature' 
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
              : journey === 'growth'
              ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300'
              : journey === 'startup'
              ? 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300'
              : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
          }`}>
            {formatJourney(journey)}
          </span>
        )
      },
    },
    {
      accessorKey: "economic_parameters",
      header: "Cost of Living",
      cell: ({ row }) => {
        const params = row.getValue("economic_parameters") as any
        return params?.cost_of_living ? (
          <PercentageCell value={params.cost_of_living} decimals={1} />
        ) : (
          <span className="text-sm text-muted-foreground">N/A</span>
        )
      },
    },
    {
      id: "actions",
      enableHiding: false,
      cell: ({ row }) => {
        const office = row.original
        return (
          <div className="flex items-center space-x-2">
            <Button 
              variant="ghost" 
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                navigate(`/office-overview/${office.id}`);
              }}
              title="View Overview"
            >
              <Eye className="h-4 w-4" />
            </Button>
            <Button 
              variant="ghost" 
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                navigate(`/offices/${office.id}`);
              }}
              title="Configure Office"
            >
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        )
      },
    },
  ]

  // If viewing a specific office
  if (selectedOffice) {
    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button variant="outline" size="sm" onClick={handleBackToList}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Offices
            </Button>
            
            <div>
              <h1 className="text-2xl font-bold tracking-tight">
                {selectedOffice.name}
              </h1>
              <p className="text-muted-foreground">
                Office configuration and management
              </p>
            </div>
          </div>

        </div>

        {/* Office Stats */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total FTE</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{Math.round(selectedOffice.total_fte)}</div>
              <p className="text-xs text-muted-foreground">
                Full-time employees
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Journey</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatJourney(selectedOffice.journey)}</div>
              <p className="text-xs text-muted-foreground">
                Office maturity stage
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Cost of Living</CardTitle>
              <Building2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {selectedOffice.economic_parameters?.cost_of_living 
                  ? `${(selectedOffice.economic_parameters.cost_of_living * 100).toFixed(1)}%`
                  : 'N/A'
                }
              </div>
              <p className="text-xs text-muted-foreground">
                Relative to baseline
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Roles</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {selectedOffice.roles ? Object.keys(selectedOffice.roles).length : 0}
              </div>
              <p className="text-xs text-muted-foreground">
                Configured roles
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Office Configuration */}
        <div className="w-full">
          <OfficeConfigPageWrapper 
            office={selectedOffice}
            onOfficeUpdate={(updatedOffice) => {
              setSelectedOffice(updatedOffice)
            }}
          />
        </div>
      </div>
    )
  }

  // Main offices list view
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h2 className="text-2xl font-bold tracking-tight flex items-center">
            <Building2 className="mr-2 h-6 w-6" />
            Offices
          </h2>
          <p className="text-muted-foreground">
            Manage office configurations and view office details across all locations
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button onClick={() => console.log('Add Office button clicked')}>
            <Plus className="mr-2 h-4 w-4" />
            Add Office
          </Button>
          <Button 
            variant="outline" 
            onClick={() => console.log('Test button clicked')}
          >
            Test Click
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Offices</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{offices.length}</div>
            <p className="text-xs text-muted-foreground">
              Across all regions
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total FTE</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Math.round(offices.reduce((sum, office) => sum + office.total_fte, 0))}
            </div>
            <p className="text-xs text-muted-foreground">
              All employees
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average FTE</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {offices.length > 0 
                ? Math.round(offices.reduce((sum, office) => sum + office.total_fte, 0) / offices.length)
                : 0
              }
            </div>
            <p className="text-xs text-muted-foreground">
              Per office
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Offices Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Offices</CardTitle>
          <CardDescription>
            View and manage office configurations
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading offices...</div>
          ) : error ? (
            <div className="text-center text-red-600 py-8">{error}</div>
          ) : (
            <div onClick={() => console.log('Table container clicked')}>
              <DataTableMinimal
                columns={columns}
                data={offices}
                onRowClick={(office) => {
                  console.log('DataTableMinimal row clicked:', office);
                  handleOfficeSelect(office);
                }}
                enablePagination={true}
                pageSize={10}
              />
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}