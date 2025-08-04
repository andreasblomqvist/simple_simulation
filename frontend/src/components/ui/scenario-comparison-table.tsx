/**
 * Scenario Comparison Table
 * 
 * Specialized table for comparing multiple scenarios side by side
 * Shows KPIs, deltas, and performance indicators across scenarios
 */
import React from 'react'
import { EnhancedDataTable, EnhancedColumnDef, FinancialCell, DeltaCell } from './enhanced-data-table'
import { Badge } from './badge'
import { Button } from './button'
import { Card, CardContent, CardHeader, CardTitle } from './card'
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  Target,
  AlertTriangle,
  CheckCircle
} from 'lucide-react'
import { cn } from '../../lib/utils'

// Scenario comparison data types
export interface ScenarioKPI {
  kpi: string
  unit: 'currency' | 'percentage' | 'count' | 'number'
  target?: number
  benchmark?: number
}

export interface ScenarioData {
  id: string
  name: string
  description?: string
  status: 'completed' | 'running' | 'failed'
  kpis: Record<string, number>
  createdAt: Date
  completedAt?: Date
}

export interface ComparisonRow {
  kpi: string
  unit: ScenarioKPI['unit']
  target?: number
  benchmark?: number
  scenarios: Record<string, {
    value: number
    delta?: number
    percentChange?: number
    status?: 'above_target' | 'below_target' | 'on_target'
  }>
}

interface ScenarioComparisonTableProps {
  scenarios: ScenarioData[]
  kpis: ScenarioKPI[]
  baselineScenarioId?: string
  showTargets?: boolean
  showBenchmarks?: boolean
  onScenarioSelect?: (scenarioId: string) => void
  onExportComparison?: () => void
  className?: string
}

// Performance indicator component
const PerformanceIndicator: React.FC<{
  value: number
  target?: number
  benchmark?: number
  unit: ScenarioKPI['unit']
}> = ({ value, target, benchmark, unit }) => {
  let status: 'good' | 'warning' | 'poor' | 'neutral' = 'neutral'
  let icon = Minus
  
  if (target !== undefined) {
    const targetDiff = value - target
    const threshold = Math.abs(target * 0.05) // 5% threshold
    
    if (Math.abs(targetDiff) <= threshold) {
      status = 'good'
      icon = Target
    } else if (targetDiff > 0) {
      status = unit === 'currency' || unit === 'count' ? 'good' : 'warning'
      icon = TrendingUp
    } else {
      status = unit === 'currency' || unit === 'count' ? 'warning' : 'good'
      icon = TrendingDown
    }
  }
  
  const statusStyles = {
    good: 'text-green-600 bg-green-50',
    warning: 'text-yellow-600 bg-yellow-50',
    poor: 'text-red-600 bg-red-50',
    neutral: 'text-gray-600 bg-gray-50'
  }
  
  const Icon = icon
  
  return (
    <div className={cn('inline-flex items-center justify-center w-6 h-6 rounded-full', statusStyles[status])}>
      <Icon className="w-3 h-3" />
    </div>
  )
}

// Scenario header component
const ScenarioHeader: React.FC<{
  scenario: ScenarioData
  isBaseline?: boolean
  onSelect?: () => void
}> = ({ scenario, isBaseline, onSelect }) => {
  const statusIcons = {
    completed: CheckCircle,
    running: TrendingUp,
    failed: AlertTriangle
  }
  
  const statusColors = {
    completed: 'text-green-600',
    running: 'text-blue-600', 
    failed: 'text-red-600'
  }
  
  const StatusIcon = statusIcons[scenario.status]
  
  return (
    <div className="text-center space-y-2">
      <div className="flex items-center justify-center gap-2">
        <StatusIcon className={cn('w-4 h-4', statusColors[scenario.status])} />
        <Button
          variant="ghost"
          size="sm"
          onClick={onSelect}
          className="font-medium hover:bg-muted/50"
        >
          {scenario.name}
        </Button>
        {isBaseline && (
          <Badge variant="secondary" className="text-xs">
            Baseline
          </Badge>
        )}
      </div>
      {scenario.description && (
        <div className="text-xs text-muted-foreground max-w-[120px] truncate">
          {scenario.description}
        </div>
      )}
      <div className="text-xs text-muted-foreground">
        {scenario.completedAt ? (
          `Completed ${scenario.completedAt.toLocaleDateString()}`
        ) : (
          `Created ${scenario.createdAt.toLocaleDateString()}`
        )}
      </div>
    </div>
  )
}

// Delta comparison cell
const ComparisonCell: React.FC<{
  value: number
  baseline?: number
  target?: number
  unit: ScenarioKPI['unit']
  currency?: string
}> = ({ value, baseline, target, unit, currency = 'SEK' }) => {
  const formatValue = (val: number) => {
    switch (unit) {
      case 'currency':
        return `${currency} ${val.toLocaleString()}`
      case 'percentage':
        return `${val.toFixed(1)}%`
      case 'count':
        return val.toLocaleString()
      default:
        return val.toLocaleString()
    }
  }

  return (
    <div className="text-right space-y-1">
      <div className="font-mono text-sm">
        {formatValue(value)}
      </div>
      {baseline !== undefined && baseline !== value && (
        <DeltaCell
          value={value}
          baseline={baseline}
          isPercentage={unit === 'percentage'}
        />
      )}
      <div className="flex justify-end">
        <PerformanceIndicator
          value={value}
          target={target}
          unit={unit}
        />
      </div>
    </div>
  )
}

export function ScenarioComparisonTable({
  scenarios,
  kpis,
  baselineScenarioId,
  showTargets = true,
  showBenchmarks = false,
  onScenarioSelect,
  onExportComparison,
  className
}: ScenarioComparisonTableProps) {
  
  // Build comparison data
  const comparisonData: ComparisonRow[] = React.useMemo(() => {
    return kpis.map(kpi => {
      const row: ComparisonRow = {
        kpi: kpi.kpi,
        unit: kpi.unit,
        target: kpi.target,
        benchmark: kpi.benchmark,
        scenarios: {}
      }
      
      const baselineScenario = scenarios.find(s => s.id === baselineScenarioId)
      const baselineValue = baselineScenario?.kpis[kpi.kpi]
      
      scenarios.forEach(scenario => {
        const value = scenario.kpis[kpi.kpi] || 0
        const delta = baselineValue !== undefined ? value - baselineValue : undefined
        const percentChange = baselineValue && baselineValue !== 0 
          ? (delta! / baselineValue) * 100 
          : undefined
        
        let status: 'above_target' | 'below_target' | 'on_target' | undefined
        if (kpi.target !== undefined) {
          const diff = Math.abs(value - kpi.target)
          const threshold = Math.abs(kpi.target * 0.05)
          if (diff <= threshold) {
            status = 'on_target'
          } else {
            status = value > kpi.target ? 'above_target' : 'below_target'
          }
        }
        
        row.scenarios[scenario.id] = {
          value,
          delta,
          percentChange,
          status
        }
      })
      
      return row
    })
  }, [scenarios, kpis, baselineScenarioId])

  // Generate table columns
  const columns: EnhancedColumnDef<ComparisonRow>[] = React.useMemo(() => {
    const cols: EnhancedColumnDef<ComparisonRow>[] = [
      {
        accessorKey: 'kpi',
        header: 'KPI',
        cell: ({ row }) => (
          <div className="font-medium">
            {row.getValue('kpi')}
          </div>
        ),
        size: 150
      }
    ]

    // Add target column if enabled
    if (showTargets) {
      cols.push({
        accessorKey: 'target',
        header: 'Target',
        cell: ({ row }) => {
          const target = row.original.target
          const unit = row.original.unit
          if (target === undefined) return <span className="text-muted-foreground">-</span>
          
          return (
            <FinancialCell
              value={target}
              format={{
                type: unit === 'currency' ? 'currency' : unit === 'percentage' ? 'percentage' : 'number',
                largeNumber: unit === 'currency'
              }}
            />
          )
        },
        size: 100
      })
    }

    // Add benchmark column if enabled
    if (showBenchmarks) {
      cols.push({
        accessorKey: 'benchmark',
        header: 'Benchmark',
        cell: ({ row }) => {
          const benchmark = row.original.benchmark
          const unit = row.original.unit
          if (benchmark === undefined) return <span className="text-muted-foreground">-</span>
          
          return (
            <FinancialCell
              value={benchmark}
              format={{
                type: unit === 'currency' ? 'currency' : unit === 'percentage' ? 'percentage' : 'number',
                largeNumber: unit === 'currency'
              }}
            />
          )
        },
        size: 100
      })
    }

    // Add scenario columns
    scenarios.forEach(scenario => {
      cols.push({
        id: scenario.id,
        header: () => (
          <ScenarioHeader
            scenario={scenario}
            isBaseline={scenario.id === baselineScenarioId}
            onSelect={() => onScenarioSelect?.(scenario.id)}
          />
        ),
        cell: ({ row }) => {
          const scenarioData = row.original.scenarios[scenario.id]
          const baseline = baselineScenarioId 
            ? row.original.scenarios[baselineScenarioId]?.value
            : undefined
          
          if (!scenarioData) return <span className="text-muted-foreground">-</span>
          
          return (
            <ComparisonCell
              value={scenarioData.value}
              baseline={baseline}
              target={row.original.target}
              unit={row.original.unit}
            />
          )
        },
        size: 140
      })
    })

    return cols
  }, [scenarios, baselineScenarioId, showTargets, showBenchmarks, onScenarioSelect])

  return (
    <div className={cn('scenario-comparison-table space-y-4', className)}>
      {/* Header with summary and actions */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Scenario Comparison</CardTitle>
              <p className="text-sm text-muted-foreground mt-1">
                Comparing {scenarios.length} scenarios across {kpis.length} KPIs
              </p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={onExportComparison}>
                Export Comparison
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Scenario status summary */}
          <div className="flex gap-4 text-xs">
            <div className="flex items-center gap-1">
              <CheckCircle className="w-3 h-3 text-green-600" />
              {scenarios.filter(s => s.status === 'completed').length} Completed
            </div>
            <div className="flex items-center gap-1">
              <TrendingUp className="w-3 h-3 text-blue-600" />
              {scenarios.filter(s => s.status === 'running').length} Running
            </div>
            <div className="flex items-center gap-1">
              <AlertTriangle className="w-3 h-3 text-red-600" />
              {scenarios.filter(s => s.status === 'failed').length} Failed
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Comparison table */}
      <EnhancedDataTable
        columns={columns}
        data={comparisonData}
        searchable={true}
        searchPlaceholder="Search KPIs..."
        searchColumn="kpi"
        enableSelection={false}
        enablePagination={false}
        enableColumnToggle={false}
        bordered={true}
        striped={false}
        size="sm"
        className="comparison-table"
        tableClassName="comparison-table-inner"
      />
    </div>
  )
}

// Helper function to build scenario comparison data
export const buildScenarioComparisonData = (
  scenarioResults: any[],
  kpiDefinitions: ScenarioKPI[]
): { scenarios: ScenarioData[], kpis: ScenarioKPI[] } => {
  const scenarios: ScenarioData[] = scenarioResults.map(result => ({
    id: result.id,
    name: result.name || `Scenario ${result.id}`,
    description: result.description,
    status: result.status || 'completed',
    kpis: extractKPIsFromResults(result),
    createdAt: new Date(result.created_at || Date.now()),
    completedAt: result.completed_at ? new Date(result.completed_at) : undefined
  }))

  return {
    scenarios,
    kpis: kpiDefinitions
  }
}

// Helper to extract KPIs from simulation results
const extractKPIsFromResults = (results: any): Record<string, number> => {
  // This would extract KPIs from the simulation results structure
  // Implementation depends on the actual results format
  return {
    FTE: results.fte || 0,
    Revenue: results.revenue || 0,
    EBITDA: results.ebitda || 0,
    'EBITDA%': results.ebitda_margin || 0,
    'Growth%': results.growth_rate || 0
  }
}