/**
 * Financial Data Table
 * 
 * Specialized table for financial/KPI data display
 * Pre-configured for financial formatting, delta calculations, and KPI presentation
 */
import React from 'react'
import { EnhancedDataTable, EnhancedColumnDef, FinancialCell, DeltaCell } from './enhanced-data-table'
import { Badge } from './badge'
import { cn } from '../../lib/utils'

// Common financial data types
export interface FinancialKPI {
  kpi: string
  value: number
  unit: 'currency' | 'percentage' | 'count' | 'number'
  change?: number
  baseline?: number
  target?: number
  status?: 'good' | 'warning' | 'poor'
}

export interface YearlyFinancialData {
  [year: string]: number
}

export interface FinancialRow {
  kpi: string
  isDelta?: boolean
  [year: string]: any
}

interface FinancialDataTableProps<TData = FinancialRow> {
  data: TData[]
  years?: string[]
  enableDelta?: boolean
  enableTargets?: boolean
  showStatus?: boolean
  currency?: string
  onRowClick?: (row: TData) => void
  className?: string
}

// Status indicator component
const StatusBadge: React.FC<{ status: FinancialKPI['status'] }> = ({ status }) => {
  if (!status) return null
  
  const variants = {
    good: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800', 
    poor: 'bg-red-100 text-red-800'
  }
  
  return (
    <Badge variant="secondary" className={cn(variants[status])}>
      {status}
    </Badge>
  )
}

// KPI formatting helper
export const formatKPIValue = (value: number, unit: FinancialKPI['unit'], currency = 'SEK') => {
  switch (unit) {
    case 'currency':
      return `${currency} ${formatLargeNumber(value)}`
    case 'percentage':
      return `${value.toFixed(1)}%`
    case 'count':
      return formatLargeNumber(value)
    default:
      return value.toLocaleString()
  }
}

const formatLargeNumber = (num: number) => {
  if (Math.abs(num) >= 1_000_000_000) {
    return (num / 1_000_000_000).toFixed(2).replace(/\.00$/, '') + 'B'
  }
  if (Math.abs(num) >= 1_000_000) {
    return (num / 1_000_000).toFixed(2).replace(/\.00$/, '') + 'M'
  }
  return num.toLocaleString()
}

export function FinancialDataTable<TData extends FinancialRow>({
  data,
  years = [],
  enableDelta = true,
  enableTargets = false,
  showStatus = true,
  currency = 'SEK',
  onRowClick,
  className
}: FinancialDataTableProps<TData>) {
  
  // Generate columns based on available years
  const columns: EnhancedColumnDef<TData>[] = React.useMemo(() => {
    const cols: EnhancedColumnDef<TData>[] = [
      {
        accessorKey: 'kpi',
        header: 'KPI',
        cell: ({ row }) => {
          const isDelta = (row.original as any).isDelta
          return (
            <div className={cn(
              'font-medium',
              isDelta && 'text-sm text-muted-foreground pl-4'
            )}>
              {isDelta ? 'Δ Change' : row.getValue('kpi')}
            </div>
          )
        },
        enableSorting: false,
      }
    ]

    // Add year columns
    years.forEach(year => {
      cols.push({
        accessorKey: year,
        header: year,
        cellType: 'financial',
        format: {
          type: 'currency',
          largeNumber: true,
          prefix: `${currency} `
        },
        cell: ({ row }) => {
          const value = row.getValue(year) as number
          const isDelta = (row.original as any).isDelta
          
          if (isDelta) {
            // For delta rows, show change with color coding
            const color = value > 0 ? 'text-green-600' : value < 0 ? 'text-red-600' : 'text-gray-500'
            return (
              <span className={cn('font-mono text-sm', color)}>
                {value > 0 ? '+' : ''}{formatLargeNumber(value)}
              </span>
            )
          }
          
          return <FinancialCell value={value} format={{ type: 'currency', largeNumber: true, prefix: `${currency} ` }} />
        },
        meta: {
          align: 'right'
        }
      })
    })

    // Add status column if enabled
    if (showStatus) {
      cols.push({
        accessorKey: 'status',
        header: 'Status',
        cell: ({ row }) => {
          const status = (row.original as any).status
          return <StatusBadge status={status} />
        },
        enableSorting: false,
      })
    }

    return cols
  }, [years, currency, showStatus])

  return (
    <EnhancedDataTable
      columns={columns}
      data={data}
      searchable={false}
      enablePagination={false}
      enableColumnToggle={false}
      bordered={true}
      striped={false}
      size="md"
      onRowClick={onRowClick}
      className={cn('financial-data-table', className)}
      tableClassName="financial-table"
    />
  )
}

// Helper function to build financial table data from simulation results
export const buildFinancialTableData = (
  kpiData: Record<string, YearlyFinancialData>,
  enableDelta = true
): FinancialRow[] => {
  const rows: FinancialRow[] = []
  const years = Object.keys(Object.values(kpiData)[0] || {}).sort()
  const baselineYear = years[0]

  Object.entries(kpiData).forEach(([kpi, yearData]) => {
    // Main KPI row
    const mainRow: FinancialRow = { kpi }
    years.forEach(year => {
      mainRow[year] = yearData[year] || 0
    })
    rows.push(mainRow)

    // Delta row if enabled
    if (enableDelta && baselineYear) {
      const deltaRow: FinancialRow = { kpi: 'Δ', isDelta: true }
      const baselineValue = yearData[baselineYear] || 0
      years.forEach(year => {
        const currentValue = yearData[year] || 0
        deltaRow[year] = currentValue - baselineValue
      })
      rows.push(deltaRow)
    }
  })

  return rows
}