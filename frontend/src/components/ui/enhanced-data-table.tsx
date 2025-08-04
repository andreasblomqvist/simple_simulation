/**
 * Enhanced DataTable Component
 * 
 * Unified table implementation consolidating all table functionality across SimpleSim
 * Built on TanStack Table with shadcn/ui components
 * 
 * Features:
 * - Sorting, filtering, pagination, column visibility
 * - Row selection and expansion
 * - Custom cells (financial, editable, delta)
 * - Keyboard navigation
 * - Loading states and error handling
 * - Accessibility compliance
 */
import * as React from "react"
import {
  ColumnDef,
  ColumnFiltersState,
  SortingState,
  VisibilityState,
  Row,
  Table as TanStackTable,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  getExpandedRowModel,
  useReactTable,
} from "@tanstack/react-table"
import { 
  ChevronDown, 
  ChevronUp, 
  ChevronRight,
  MoreHorizontal, 
  Settings2,
  ArrowUpDown
} from "lucide-react"

import { Button } from "./button"
import { Checkbox } from "./checkbox"
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./dropdown-menu"
import { Input } from "./input"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "./table"
import { LoadingSpinner } from "./LoadingSpinner"
import { cn } from "../../lib/utils"

// Enhanced column definition with custom cell types
export interface EnhancedColumnDef<TData, TValue = unknown> extends ColumnDef<TData, TValue> {
  cellType?: 'default' | 'financial' | 'percentage' | 'delta' | 'editable' | 'expandable'
  format?: {
    type?: 'currency' | 'percentage' | 'number'
    decimals?: number
    prefix?: string
    suffix?: string
    largeNumber?: boolean // Use M/B formatting
  }
  editable?: {
    type: 'number' | 'text' | 'select'
    min?: number
    max?: number
    step?: number
    options?: Array<{ label: string; value: any }>
    onEdit?: (rowId: string, value: any) => void
  }
  delta?: {
    baselineAccessor: string | ((row: TData) => number)
    isPercentage?: boolean
  }
}

export interface EnhancedDataTableProps<TData, TValue> {
  columns: EnhancedColumnDef<TData, TValue>[]
  data: TData[]
  
  // Search and filtering
  searchable?: boolean
  searchPlaceholder?: string
  searchColumn?: string
  globalFilter?: boolean
  
  // Selection and interaction
  enableSelection?: boolean
  enableExpansion?: boolean
  onRowClick?: (row: TData) => void
  onRowSelect?: (selectedRows: TData[]) => void
  
  // Pagination
  enablePagination?: boolean
  pageSize?: number
  
  // Appearance
  enableColumnToggle?: boolean
  size?: 'sm' | 'md' | 'lg'
  bordered?: boolean
  striped?: boolean
  
  // State management
  loading?: boolean
  error?: string | null
  emptyMessage?: string
  
  // Accessibility
  caption?: string
  
  // Custom styling
  className?: string
  tableClassName?: string
  
  // Advanced features
  enableSorting?: boolean
  enableFiltering?: boolean
  enableKeyboardNavigation?: boolean
  
  // Callbacks
  onSortingChange?: (sorting: SortingState) => void
  onColumnFiltersChange?: (filters: ColumnFiltersState) => void
}

// Custom cell renderers
export const FinancialCell: React.FC<{
  value: number
  format?: {
    type?: 'currency' | 'percentage' | 'number'
    decimals?: number
    prefix?: string
    suffix?: string
    largeNumber?: boolean
  }
}> = ({ value, format = {} }) => {
  const {
    type = 'number',
    decimals = 0,
    prefix = '',
    suffix = '',
    largeNumber = false
  } = format

  const formatValue = (num: number) => {
    if (largeNumber && Math.abs(num) >= 1_000_000) {
      if (Math.abs(num) >= 1_000_000_000) {
        return (num / 1_000_000_000).toFixed(2).replace(/\.00$/, '') + 'B'
      }
      if (Math.abs(num) >= 1_000_000) {
        return (num / 1_000_000).toFixed(2).replace(/\.00$/, '') + 'M'
      }
    }
    
    if (type === 'currency') {
      return num.toLocaleString(undefined, {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
      })
    }
    
    if (type === 'percentage') {
      return `${num.toFixed(decimals)}%`
    }
    
    return num.toLocaleString(undefined, {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    })
  }

  return (
    <span className="font-mono text-right">
      {prefix}{formatValue(value)}{suffix}
    </span>
  )
}

export const DeltaCell: React.FC<{
  value: number
  baseline: number
  isPercentage?: boolean
}> = ({ value, baseline, isPercentage = false }) => {
  const delta = value - baseline
  const percentChange = baseline !== 0 ? (delta / baseline) * 100 : 0
  const color = delta > 0 ? 'text-green-600' : delta < 0 ? 'text-red-600' : 'text-gray-500'
  
  const deltaStr = isPercentage 
    ? `${delta > 0 ? '+' : ''}${delta.toFixed(1)}%`
    : `${delta > 0 ? '+' : ''}${delta.toFixed(0)}`
  
  const percentStr = `(${percentChange > 0 ? '+' : ''}${percentChange.toFixed(1)}%)`

  return (
    <span className={cn('text-sm font-mono', color)}>
      {deltaStr} <span className="text-xs text-muted-foreground">{percentStr}</span>
    </span>
  )
}

export const EditableCell: React.FC<{
  value: any
  onEdit: (newValue: any) => void
  config: NonNullable<EnhancedColumnDef<any>['editable']>
}> = ({ value, onEdit, config }) => {
  const [isEditing, setIsEditing] = React.useState(false)
  const [editValue, setEditValue] = React.useState(value)
  const inputRef = React.useRef<HTMLInputElement>(null)

  React.useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus()
      inputRef.current.select()
    }
  }, [isEditing])

  const handleSave = () => {
    onEdit(editValue)
    setIsEditing(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSave()
    } else if (e.key === 'Escape') {
      setEditValue(value)
      setIsEditing(false)
    }
  }

  if (isEditing) {
    return (
      <Input
        ref={inputRef}
        type={config.type}
        value={editValue}
        onChange={(e) => setEditValue(config.type === 'number' ? Number(e.target.value) : e.target.value)}
        onBlur={handleSave}
        onKeyDown={handleKeyDown}
        min={config.min}
        max={config.max}
        step={config.step}
        className="h-8 w-full"
      />
    )
  }

  return (
    <div 
      className="cursor-pointer hover:bg-muted/50 p-1 rounded"
      onClick={() => setIsEditing(true)}
      title="Click to edit"
    >
      {value}
    </div>
  )
}

// Sortable header component
export const SortableHeader: React.FC<{
  column: any
  children: React.ReactNode
}> = ({ column, children }) => {
  if (!column.getCanSort()) {
    return <div>{children}</div>
  }

  return (
    <Button
      variant="ghost"
      onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
      className="h-auto p-0 font-medium hover:bg-transparent"
    >
      {children}
      <ArrowUpDown className="ml-2 h-4 w-4" />
    </Button>
  )
}

export function EnhancedDataTable<TData, TValue>({
  columns,
  data,
  searchable = true,
  searchPlaceholder = "Search...",
  searchColumn,
  globalFilter = false,
  enableSelection = false,
  enableExpansion = false,
  enablePagination = true,
  enableColumnToggle = true,
  enableSorting = true,
  enableFiltering = true,
  enableKeyboardNavigation = false,
  pageSize = 10,
  size = 'md',
  bordered = true,
  striped = false,
  loading = false,
  error = null,
  emptyMessage = "No data available",
  caption,
  onRowClick,
  onRowSelect,
  className,
  tableClassName,
}: EnhancedDataTableProps<TData, TValue>) {
  const [sorting, setSorting] = React.useState<SortingState>([])
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([])
  const [columnVisibility, setColumnVisibility] = React.useState<VisibilityState>({})
  const [rowSelection, setRowSelection] = React.useState({})
  const [expanded, setExpanded] = React.useState({})
  const [globalFilterValue, setGlobalFilterValue] = React.useState("")

  // Enhanced columns with selection and expansion
  const enhancedColumns = React.useMemo(() => {
    let cols = [...columns]

    // Add selection column
    if (enableSelection) {
      const selectionColumn: EnhancedColumnDef<TData, TValue> = {
        id: "select",
        header: ({ table }) => (
          <Checkbox
            checked={table.getIsAllPageRowsSelected()}
            onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
            aria-label="Select all"
          />
        ),
        cell: ({ row }) => (
          <Checkbox
            checked={row.getIsSelected()}
            onCheckedChange={(value) => row.toggleSelected(!!value)}
            aria-label="Select row"
          />
        ),
        enableSorting: false,
        enableHiding: false,
      }
      cols = [selectionColumn, ...cols]
    }

    // Add expansion column
    if (enableExpansion) {
      const expansionColumn: EnhancedColumnDef<TData, TValue> = {
        id: "expand",
        header: "",
        cell: ({ row }) => (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => row.toggleExpanded()}
            className="h-6 w-6 p-0"
          >
            {row.getIsExpanded() ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
          </Button>
        ),
        enableSorting: false,
        enableHiding: false,
      }
      cols = [expansionColumn, ...cols]
    }

    // Process columns for custom cell types
    return cols.map(col => ({
      ...col,
      cell: col.cell || (({ row, column }) => {
        const value = row.getValue(column.id)
        const columnDef = col as EnhancedColumnDef<TData, TValue>
        
        // Handle custom cell types
        switch (columnDef.cellType) {
          case 'financial':
            return <FinancialCell value={value as number} format={columnDef.format} />
          
          case 'percentage':
            return <FinancialCell value={value as number} format={{ type: 'percentage', ...columnDef.format }} />
          
          case 'delta':
            if (columnDef.delta) {
              const baseline = typeof columnDef.delta.baselineAccessor === 'function'
                ? columnDef.delta.baselineAccessor(row.original)
                : row.getValue(columnDef.delta.baselineAccessor)
              return (
                <DeltaCell 
                  value={value as number} 
                  baseline={baseline as number}
                  isPercentage={columnDef.delta.isPercentage}
                />
              )
            }
            return String(value)
          
          case 'editable':
            if (columnDef.editable) {
              return (
                <EditableCell
                  value={value}
                  onEdit={(newValue) => {
                    columnDef.editable?.onEdit?.(row.id, newValue)
                  }}
                  config={columnDef.editable}
                />
              )
            }
            return String(value)
          
          default:
            return String(value ?? '')
        }
      })
    }))
  }, [columns, enableSelection, enableExpansion])

  const table = useReactTable({
    data,
    columns: enhancedColumns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: enablePagination ? getPaginationRowModel() : undefined,
    getSortedRowModel: enableSorting ? getSortedRowModel() : undefined,
    getFilteredRowModel: enableFiltering ? getFilteredRowModel() : undefined,
    getExpandedRowModel: enableExpansion ? getExpandedRowModel() : undefined,
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: setRowSelection,
    onExpandedChange: enableExpansion ? setExpanded : undefined,
    state: {
      sorting: enableSorting ? sorting : [],
      columnFilters: enableFiltering ? columnFilters : [],
      columnVisibility,
      rowSelection: enableSelection ? rowSelection : {},
      expanded: enableExpansion ? expanded : {},
      globalFilter: globalFilter ? globalFilterValue : undefined,
    },
    initialState: {
      pagination: {
        pageSize,
      },
    },
  })

  // Handle row selection callback
  React.useEffect(() => {
    if (enableSelection && onRowSelect) {
      const selectedRows = table.getFilteredSelectedRowModel().rows.map(row => row.original)
      onRowSelect(selectedRows)
    }
  }, [rowSelection, onRowSelect, enableSelection, table])

  const sizeClasses = {
    sm: "text-xs",
    md: "text-sm", 
    lg: "text-base"
  }

  const cellPadding = {
    sm: "p-2",
    md: "p-4",
    lg: "p-6"
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <LoadingSpinner size="lg" />
        <span className="ml-2">Loading...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center p-8 text-red-600">
        <p>Error: {error}</p>
      </div>
    )
  }

  return (
    <div className={cn("space-y-4", sizeClasses[size], className)}>
      {/* Toolbar */}
      <div className="flex items-center justify-between">
        <div className="flex flex-1 items-center space-x-2">
          {searchable && (
            <Input
              placeholder={searchPlaceholder}
              value={
                globalFilter
                  ? globalFilterValue
                  : (searchColumn ? (table.getColumn(searchColumn)?.getFilterValue() as string) ?? "" : "")
              }
              onChange={(event) => {
                const value = event.target.value
                if (globalFilter) {
                  setGlobalFilterValue(value)
                  table.setGlobalFilter(value)
                } else if (searchColumn) {
                  table.getColumn(searchColumn)?.setFilterValue(value)
                }
              }}
              className="h-8 w-[150px] lg:w-[250px]"
            />
          )}
        </div>
        {enableColumnToggle && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="ml-auto h-8">
                <Settings2 className="mr-2 h-4 w-4" />
                Columns
                <ChevronDown className="ml-2 h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-[150px]">
              <DropdownMenuLabel>Toggle columns</DropdownMenuLabel>
              <DropdownMenuSeparator />
              {table
                .getAllColumns()
                .filter(
                  (column) =>
                    typeof column.accessorFn !== "undefined" && column.getCanHide()
                )
                .map((column) => {
                  return (
                    <DropdownMenuCheckboxItem
                      key={column.id}
                      className="capitalize"
                      checked={column.getIsVisible()}
                      onCheckedChange={(value) =>
                        column.toggleVisibility(!!value)
                      }
                    >
                      {column.id}
                    </DropdownMenuCheckboxItem>
                  )
                })}
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>

      {/* Table */}
      <div className={cn("rounded-md", bordered && "border")}>
        <Table className={tableClassName}>
          {caption && <caption className="sr-only">{caption}</caption>}
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id} className={cellPadding[size]}>
                      {header.isPlaceholder ? null : (
                        <SortableHeader column={header.column}>
                          {flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                        </SortableHeader>
                      )}
                    </TableHead>
                  )
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                  className={cn(
                    onRowClick && "cursor-pointer",
                    striped && "even:bg-muted/20"
                  )}
                  onClick={() => onRowClick?.(row.original)}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id} className={cellPadding[size]}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={enhancedColumns.length}
                  className="h-24 text-center text-muted-foreground"
                >
                  {emptyMessage}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      {enablePagination && (
        <div className="flex items-center justify-end space-x-2 py-4">
          <div className="flex-1 text-sm text-muted-foreground">
            {enableSelection && (
              <>
                {table.getFilteredSelectedRowModel().rows.length} of{" "}
                {table.getFilteredRowModel().rows.length} row(s) selected.
              </>
            )}
          </div>
          <div className="space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

// Convenience exports for common table types
export * from "./data-table"