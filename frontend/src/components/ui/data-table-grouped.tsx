import * as React from "react"
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  useReactTable,
} from "@tanstack/react-table"

import { Button } from "./button"
import { Input } from "./input"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "./table"
import { cn } from "../../lib/utils"
import { ChevronDown, ChevronRight, BarChart3, FileText } from "lucide-react"

// Enhanced column definition with editing support
export interface GroupedColumnDef<TData, TValue = unknown> extends Omit<ColumnDef<TData, TValue>, 'enableSorting'> {
  editable?: {
    type: 'number' | 'text'
    min?: number
    max?: number
    step?: number
    onEdit?: (rowId: string, value: any) => void
  }
}

// Editable cell component
const EditableCell: React.FC<{
  value: any
  onEdit: (newValue: any) => void
  config: NonNullable<GroupedColumnDef<any>['editable']>
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

// Types for hierarchical data structure
export interface GroupedDataRow {
  type: 'category' | 'role' | 'data'
  groupKey: string
  groupValue: string
  depth: number
  itemCount?: number
  data?: any
  isExpanded?: boolean
}

export interface DataTableGroupedProps<TData, TValue> {
  columns: GroupedColumnDef<TData, TValue>[]
  data: TData[]
  onRowClick?: (row: TData) => void
  className?: string
  enablePagination?: boolean
  pageSize?: number
  enableEditing?: boolean
  groupBy?: string[]
  groupExpanded?: Record<string, boolean>
  onGroupToggle?: (groupId: string, expanded: boolean) => void
}

export function DataTableGrouped<TData, TValue>({
  columns,
  data,
  onRowClick,
  className,
  enablePagination = true,
  pageSize = 10,
  enableEditing = false,
  groupBy = [],
  groupExpanded = {},
  onGroupToggle,
}: DataTableGroupedProps<TData, TValue>) {
  
  // Create hierarchical data structure for business planning
  const hierarchicalData = React.useMemo(() => {
    if (groupBy.length === 0) {
      return data.map(item => ({
        type: 'data' as const,
        groupKey: '',
        groupValue: '',
        depth: 0,
        data: item
      }))
    }
    
    const result: GroupedDataRow[] = []
    
    // Group by first level (Field Category)
    const categoryGroups: Record<string, TData[]> = {}
    data.forEach(item => {
      const categoryKey = (item as any)[groupBy[0]]
      if (!categoryGroups[categoryKey]) {
        categoryGroups[categoryKey] = []
      }
      categoryGroups[categoryKey].push(item)
    })
    
    Object.entries(categoryGroups).forEach(([categoryKey, categoryItems]) => {
      const categoryExpanded = groupExpanded[categoryKey] !== false
      
      // Add category group row
      result.push({
        type: 'category',
        groupKey: categoryKey,
        groupValue: categoryKey,
        depth: 0,
        itemCount: categoryItems.length,
        isExpanded: categoryExpanded
      })
      
      if (categoryExpanded && groupBy.length > 1) {
        // Group by second level (Role)
        const roleGroups: Record<string, TData[]> = {}
        categoryItems.forEach(item => {
          const roleKey = `${categoryKey}-${(item as any)[groupBy[1]]}`
          if (!roleGroups[roleKey]) {
            roleGroups[roleKey] = []
          }
          roleGroups[roleKey].push(item)
        })
        
        Object.entries(roleGroups).forEach(([roleKey, roleItems]) => {
          const roleExpanded = groupExpanded[roleKey] !== false
          const roleValue = (roleItems[0] as any)[groupBy[1]]
          
          // Add role group row
          result.push({
            type: 'role',
            groupKey: roleKey,
            groupValue: roleValue,
            depth: 1,
            itemCount: roleItems.length,
            isExpanded: roleExpanded
          })
          
          if (roleExpanded) {
            // Add individual data rows
            roleItems.forEach(item => {
              result.push({
                type: 'data',
                groupKey: '',
                groupValue: '',
                depth: 2,
                data: item
              })
            })
          }
        })
      } else if (categoryExpanded) {
        // If no second level grouping, show data directly
        categoryItems.forEach(item => {
          result.push({
            type: 'data',
            groupKey: '',
            groupValue: '',
            depth: 1,
            data: item
          })
        })
      }
    })
    
    return result
  }, [data, groupBy, groupExpanded])
  
  // Simple table setup for rendering hierarchical data
  const table = useReactTable({
    data: hierarchicalData as any[],
    columns: columns.map(col => ({ ...col, enableSorting: false })) as ColumnDef<any>[],
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: enablePagination ? getPaginationRowModel() : undefined,
    enableSorting: false,
    enableColumnFilters: false,
    enableGlobalFilter: false,
    initialState: {
      pagination: {
        pageSize,
      },
    },
  })

  const getGroupIcon = (type: 'category' | 'role' | 'data') => {
    switch (type) {
      case 'category':
        return <BarChart3 className="h-4 w-4 text-muted-foreground" />
      case 'role':
        return <FileText className="h-4 w-4 text-muted-foreground" />
      default:
        return null
    }
  }

  return (
    <div className={cn("space-y-4", className)}>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {hierarchicalData.map((item, index) => {
              if (item.type === 'category' || item.type === 'role') {
                // Group row
                const paddingLeft = item.depth * 20 + 16
                const isExpanded = item.isExpanded
                
                return (
                  <TableRow key={`group-${item.groupKey}`} className="bg-muted/30">
                    <TableCell 
                      className="font-medium"
                      style={{ paddingLeft: `${paddingLeft}px` }}
                    >
                      <div className="flex items-center gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onGroupToggle?.(item.groupKey, !isExpanded)}
                          className="h-6 w-6 p-0"
                        >
                          {isExpanded ? (
                            <ChevronDown className="h-4 w-4" />
                          ) : (
                            <ChevronRight className="h-4 w-4" />
                          )}
                        </Button>
                        {getGroupIcon(item.type)}
                        <span className="font-semibold">{item.groupValue}</span>
                        <span className="text-muted-foreground text-sm">
                          ({item.itemCount} items)
                        </span>
                      </div>
                    </TableCell>
                    {/* Fill remaining cells with aggregated values */}
                    {columns.slice(1).map((column, colIndex) => (
                      <TableCell key={colIndex} className="text-muted-foreground">
{((column as any).accessorKey && typeof (column as any).accessorKey === 'string') ? (
                          (() => {
                            // Calculate aggregated values for this group
                            let groupItems: TData[] = []
                            
                            if (item.type === 'category') {
                              groupItems = data.filter(d => (d as any)[groupBy[0]] === item.groupKey)
                            } else if (item.type === 'role') {
                              const [categoryKey, roleKey] = item.groupKey.split('-')
                              groupItems = data.filter(d => 
                                (d as any)[groupBy[0]] === categoryKey && 
                                (d as any)[groupBy[1]] === roleKey
                              )
                            }
                            
                            const sum = groupItems.reduce((acc, d) => {
                              const value = (d as any)[(column as any).accessorKey!]
                              return acc + (typeof value === 'number' ? value : 0)
                            }, 0)
                            
                            return sum.toFixed((column as any).accessorKey === 'utr' ? 2 : 0)
                          })()
                        ) : null}
                      </TableCell>
                    ))}
                  </TableRow>
                )
              } else {
                // Data row
                const paddingLeft = item.depth * 20 + 16
                const rowData = item.data
                
                return (
                  <TableRow
                    key={`data-${index}`}
                    className={cn(
                      "transition-colors",
                      onRowClick && "cursor-pointer"
                    )}
                    onClick={() => onRowClick?.(rowData)}
                  >
                    {columns.map((column, colIndex) => {
                      const value = (rowData as any)[(column as any).accessorKey!]
                      
                      return (
                        <TableCell 
                          key={colIndex}
                          style={colIndex === 0 ? { paddingLeft: `${paddingLeft}px` } : undefined}
                        >
                          {enableEditing && column.editable ? (
                            <EditableCell
                              value={value}
                              onEdit={(newValue) => column.editable?.onEdit?.(rowData.id || `row-${index}`, newValue)}
                              config={column.editable}
                            />
                          ) : (
                            <div className="flex items-center gap-2">
                              {colIndex === 0 && <FileText className="h-4 w-4 text-muted-foreground" />}
                              {value}
                            </div>
                          )}
                        </TableCell>
                      )
                    })}
                  </TableRow>
                )
              }
            })}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      {enablePagination && table.getPageCount() > 1 && (
        <div className="flex items-center justify-end space-x-2 py-4">
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