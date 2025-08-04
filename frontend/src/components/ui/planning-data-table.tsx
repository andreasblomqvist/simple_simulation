/**
 * Planning Data Table
 * 
 * Specialized table for business planning data with inline editing
 * Supports role/level hierarchies, monthly data, and real-time editing
 */
import React from 'react'
import { DataTableMinimal, MinimalColumnDef } from './data-table-minimal'
import { Button } from './button'
import { Badge } from './badge'
import { 
  Users, 
  DollarSign, 
  TrendingUp, 
  Clock,
  Calculator
} from 'lucide-react'
import { cn } from '../../lib/utils'

// Planning data types
export interface PlanningEntry {
  role: string
  level?: string
  month: number
  recruitment: number
  churn: number
  price?: number
  utr?: number // Utilization rate
  salary: number
}

export interface PlanningRow extends PlanningEntry {
  id: string
  isExpanded?: boolean
  isSubLevel?: boolean
  isDirty?: boolean
}

interface PlanningDataTableProps {
  data: PlanningRow[]
  months: string[]
  enableEditing?: boolean
  enableExpansion?: boolean
  showSubLevels?: boolean
  onCellEdit?: (rowId: string, field: keyof PlanningEntry, value: number) => void
  onRowExpand?: (rowId: string, expanded: boolean) => void
  onSave?: () => void
  onDiscard?: () => void
  hasUnsavedChanges?: boolean
  className?: string
}

// Field configuration for different types of planning data
const FIELD_CONFIG = {
  recruitment: {
    label: 'Recruitment',
    icon: Users,
    color: 'text-green-600',
    type: 'number' as const,
    min: 0,
    step: 1
  },
  churn: {
    label: 'Churn',
    icon: TrendingUp,
    color: 'text-red-600',
    type: 'number' as const,
    min: 0,
    step: 1
  },
  price: {
    label: 'Price (SEK/h)',
    icon: DollarSign,
    color: 'text-blue-600',
    type: 'number' as const,
    min: 0,
    step: 50
  },
  utr: {
    label: 'UTR (%)',
    icon: Clock,
    color: 'text-purple-600',
    type: 'number' as const,
    min: 0,
    max: 100,
    step: 5
  },
  salary: {
    label: 'Salary (SEK)',
    icon: Calculator,
    color: 'text-orange-600',
    type: 'number' as const,
    min: 0,
    step: 1000
  }
}



// Role/Level display component
const RoleCell: React.FC<{ row: PlanningRow }> = ({ row }) => {
  return (
    <div className={cn(
      'flex items-center gap-2',
      row.isSubLevel && 'pl-6'
    )}>
      <div>
        <div className={cn(
          'font-medium',
          row.isSubLevel ? 'text-sm text-muted-foreground' : 'text-base'
        )}>
          {row.isSubLevel ? row.level : row.role}
        </div>
        {!row.isSubLevel && row.level && (
          <div className="text-xs text-muted-foreground">
            {row.level}
          </div>
        )}
      </div>
      {row.isDirty && (
        <Badge variant="secondary" className="bg-orange-100 text-orange-800">
          Modified
        </Badge>
      )}
    </div>
  )
}

export function PlanningDataTable({
  data,
  months,
  enableEditing = true,
  enableExpansion = true,
  showSubLevels = true,
  onCellEdit,
  onRowExpand,
  onSave,
  onDiscard,
  hasUnsavedChanges = false,
  className
}: PlanningDataTableProps) {

  // Generate columns for the planning table
  const columns: MinimalColumnDef<PlanningRow>[] = React.useMemo(() => {
    const cols: MinimalColumnDef<PlanningRow>[] = []

    // Role/Level column
    cols.push({
      accessorKey: 'role',
      header: 'Role / Level',
      cell: ({ row }) => <RoleCell row={row.original} />,
      size: 200
    })

    // Planning field columns for each month
    months.forEach(month => {
      // Recruitment column
      cols.push({
        id: `${month}-recruitment`,
        header: `${month} Rec`,
        accessorFn: (row) => row.recruitment,
        editable: enableEditing ? {
          type: 'number',
          min: FIELD_CONFIG.recruitment.min,
          step: FIELD_CONFIG.recruitment.step,
          onEdit: (rowId, value) => onCellEdit?.(rowId, 'recruitment', value)
        } : undefined,
        size: 80
      })

      // Churn column
      cols.push({
        id: `${month}-churn`,
        header: `${month} Churn`,
        accessorFn: (row) => row.churn,
        editable: enableEditing ? {
          type: 'number',
          min: FIELD_CONFIG.churn.min,
          step: FIELD_CONFIG.churn.step,
          onEdit: (rowId, value) => onCellEdit?.(rowId, 'churn', value)
        } : undefined,
        size: 80
      })

      // Price column (for billable roles)
      cols.push({
        id: `${month}-price`,
        header: `${month} Price`,
        accessorFn: (row) => row.price || 0,
        editable: enableEditing ? {
          type: 'number',
          min: FIELD_CONFIG.price.min,
          step: FIELD_CONFIG.price.step,
          onEdit: (rowId, value) => onCellEdit?.(rowId, 'price', value)
        } : undefined,
        size: 100
      })

      // UTR column (for billable roles)
      cols.push({
        id: `${month}-utr`,
        header: `${month} UTR`,
        accessorFn: (row) => (row.utr || 0) * 100, // Convert to percentage
        editable: enableEditing ? {
          type: 'number',
          min: FIELD_CONFIG.utr.min,
          max: FIELD_CONFIG.utr.max,
          step: FIELD_CONFIG.utr.step,
          onEdit: (rowId, value) => onCellEdit?.(rowId, 'utr', value / 100) // Convert back to decimal
        } : undefined,
        size: 80
      })

      // Salary column
      cols.push({
        id: `${month}-salary`,
        header: `${month} Salary`,
        accessorFn: (row) => row.salary,
        editable: enableEditing ? {
          type: 'number',
          min: FIELD_CONFIG.salary.min,
          step: FIELD_CONFIG.salary.step,
          onEdit: (rowId, value) => onCellEdit?.(rowId, 'salary', value)
        } : undefined,
        size: 120
      })
    })

    return cols
  }, [months, enableEditing, onCellEdit])

  return (
    <div className={cn('planning-data-table space-y-4', className)}>
      {/* Action bar for save/discard */}
      {hasUnsavedChanges && (
        <div className="flex items-center justify-between p-4 bg-orange-50 dark:bg-orange-950/20 rounded-md border border-orange-200 dark:border-orange-800">
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="bg-orange-100 text-orange-800">
              Unsaved Changes
            </Badge>
            <span className="text-sm text-muted-foreground">
              You have unsaved changes to your business plan
            </span>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={onDiscard}>
              Discard
            </Button>
            <Button size="sm" onClick={onSave}>
              Save Changes
            </Button>
          </div>
        </div>
      )}

      <DataTableMinimal
        columns={columns}
        data={data}
        enableEditing={enableEditing}
        enablePagination={false}
        className="planning-table"
      />
    </div>
  )
}

// Helper function to build planning table data from monthly plans
export const buildPlanningTableData = (
  monthlyPlans: any[],
  showSubLevels = true
): PlanningRow[] => {
  const rows: PlanningRow[] = []
  const roleGroups = new Map<string, Map<string, PlanningEntry[]>>()

  // Group data by role and level
  monthlyPlans.forEach(plan => {
    plan.entries.forEach((entry: PlanningEntry) => {
      if (!roleGroups.has(entry.role)) {
        roleGroups.set(entry.role, new Map())
      }
      const levelMap = roleGroups.get(entry.role)!
      const level = entry.level || 'General'
      if (!levelMap.has(level)) {
        levelMap.set(level, [])
      }
      levelMap.get(level)!.push({
        ...entry,
        month: plan.month
      })
    })
  })

  // Build hierarchical row structure
  let rowIndex = 0
  roleGroups.forEach((levelMap, role) => {
    // Add role header row
    const roleRow: PlanningRow = {
      id: `role-${rowIndex++}`,
      role,
      month: 1, // Default month
      recruitment: 0,
      churn: 0,
      salary: 0,
      isExpanded: false
    }
    rows.push(roleRow)

    // Add level rows if showing sub-levels
    if (showSubLevels) {
      levelMap.forEach((entries, level) => {
        const levelRow: PlanningRow = {
          id: `level-${rowIndex++}`,
          role,
          level,
          month: 1,
          recruitment: entries.reduce((sum, e) => sum + e.recruitment, 0),
          churn: entries.reduce((sum, e) => sum + e.churn, 0),
          price: entries[0]?.price || 0,
          utr: entries[0]?.utr || 0,
          salary: entries.reduce((sum, e) => sum + e.salary, 0),
          isSubLevel: true
        }
        rows.push(levelRow)
      })
    }
  })

  return rows
}