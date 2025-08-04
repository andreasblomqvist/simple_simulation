import * as React from "react"
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  getGroupedRowModel,
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
import { ChevronDown, ChevronRight } from "lucide-react"

// Enhanced column definition with editing support
export interface MinimalColumnDef<TData, TValue = unknown> extends ColumnDef<TData, TValue> {
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
  config: NonNullable<MinimalColumnDef<any>['editable']>
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
        className="h-8 w-full bg-gray-700 text-white border-gray-500"
      />
    )
  }

  return (
    <div 
      className="cursor-pointer hover:bg-gray-700 p-1 rounded text-white"
      onClick={() => setIsEditing(true)}
      title="Click to edit"
    >
      {value}
    </div>
  )
}

// Group row component
const GroupRow: React.FC<{
  row: any
  columns: MinimalColumnDef<any>[]
  onToggle: () => void
}> = ({ row, columns, onToggle }) => {
  const isExpanded = row.getIsExpanded()
  const groupBy = row.groupBy || []
  
  // Try different ways to get the group value
  let groupValue = 'Unknown Group'
  if (groupBy.length > 0) {
    try {
      groupValue = row.getValue(groupBy[0]) || 'Unknown Group'
    } catch (error) {
      console.error('Error getting group value:', error)
      // Try to get it from the original data
      if (row.original && row.original[groupBy[0]]) {
        groupValue = row.original[groupBy[0]]
      }
    }
  }
  
  const depth = row.depth

  return (
    <TableRow className="border-b border-gray-600 hover:bg-gray-800">
      <TableCell 
        className="px-4 py-3 align-middle text-base font-medium text-white border-r border-gray-600"
        style={{ paddingLeft: `${depth * 20 + 16}px` }}
      >
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggle}
            className="h-6 w-6 p-0 hover:bg-gray-700"
          >
            {isExpanded ? (
              <ChevronDown className="h-4 w-4 text-white" />
            ) : (
              <ChevronRight className="h-4 w-4 text-white" />
            )}
          </Button>
          <span className="font-semibold">{groupValue}</span>
          <span className="text-gray-400 text-sm">
            ({(row.subRows || []).length} items)
          </span>
        </div>
      </TableCell>
      {/* Fill remaining cells */}
      {columns.slice(1).map((column, index) => (
        <TableCell 
          key={index}
          className="px-4 py-3 align-middle text-base font-medium text-white border-r border-gray-600 last:border-r-0"
        >
          {/* Show aggregated values for numeric columns */}
          {column.accessorKey && typeof row.getValue(column.accessorKey) === 'number' ? (
            <span className="text-gray-400">
              {(row.subRows || []).reduce((sum: number, subRow: any) => {
                const value = subRow.getValue(column.accessorKey)
                return sum + (typeof value === 'number' ? value : 0)
              }, 0).toFixed(column.accessorKey === 'utr' ? 2 : 0)}
            </span>
          ) : null}
        </TableCell>
      ))}
    </TableRow>
  )
}

export interface DataTableMinimalProps<TData, TValue> {
  columns: MinimalColumnDef<TData, TValue>[]
  data: TData[]
  onRowClick?: (row: TData) => void
  className?: string
  enablePagination?: boolean
  pageSize?: number
  enableEditing?: boolean
  enableGrouping?: boolean
  groupBy?: string[]
  getRowCanGroup?: (row: TData) => boolean
  groupExpanded?: Record<string, boolean>
  onGroupToggle?: (groupId: string, expanded: boolean) => void
}

export function DataTableMinimal<TData, TValue>({
  columns,
  data,
  onRowClick,
  className,
  enablePagination = true,
  pageSize = 10,
  enableEditing = false,
  enableGrouping = false,
  groupBy = [],
  getRowCanGroup,
  groupExpanded = {},
  onGroupToggle,
}: DataTableMinimalProps<TData, TValue>) {
  // Debug logging removed - table issue was fixed by adding explicit pageIndex: 0 to pagination state
  
  // Three-level hierarchical grouping logic
  const groupedData = React.useMemo(() => {
    if (!enableGrouping || groupBy.length === 0) {
      return data.map(item => ({ type: 'row', data: item, depth: 0 }))
    }
    
    const result: Array<{ type: 'group' | 'row', data: any, groupKey?: string, depth: number }> = []
    
    // First level grouping (by first groupBy field - Field Category)
    const firstLevelGroups: Record<string, TData[]> = {}
    data.forEach(item => {
      const firstLevelKey = (item as any)[groupBy[0]]
      if (!firstLevelGroups[firstLevelKey]) {
        firstLevelGroups[firstLevelKey] = []
      }
      firstLevelGroups[firstLevelKey].push(item)
    })
    
    Object.entries(firstLevelGroups).forEach(([firstLevelKey, items]) => {
      const firstLevelExpanded = groupExpanded[firstLevelKey] === true // Default to collapsed
      
      // Add first level group
      result.push({
        type: 'group',
        data: { 
          groupKey: firstLevelKey, 
          groupValue: firstLevelKey, 
          itemCount: items.length,
          level: 1
        },
        groupKey: firstLevelKey,
        depth: 0
      })
      
      if (firstLevelExpanded && groupBy.length > 1) {
        // Second level grouping (by second groupBy field - Role)
        const secondLevelGroups: Record<string, TData[]> = {}
        items.forEach(item => {
          const secondLevelKey = `${firstLevelKey}-${(item as any)[groupBy[1]]}`
          if (!secondLevelGroups[secondLevelKey]) {
            secondLevelGroups[secondLevelKey] = []
          }
          secondLevelGroups[secondLevelKey].push(item)
        })
        
        Object.entries(secondLevelGroups).forEach(([secondLevelKey, subItems]) => {
          const secondLevelExpanded = groupExpanded[secondLevelKey] === true
          const secondLevelValue = (subItems[0] as any)[groupBy[1]]
          
          // Add second level group
          result.push({
            type: 'group',
            data: { 
              groupKey: secondLevelKey, 
              groupValue: secondLevelValue, 
              itemCount: subItems.length,
              level: 2
            },
            groupKey: secondLevelKey,
            depth: 1
          })
          
          if (secondLevelExpanded && groupBy.length > 2) {
            // Third level grouping (by third groupBy field - Level)
            const thirdLevelGroups: Record<string, TData[]> = {}
            subItems.forEach(item => {
              const thirdLevelKey = `${secondLevelKey}-${(item as any)[groupBy[2]]}`
              if (!thirdLevelGroups[thirdLevelKey]) {
                thirdLevelGroups[thirdLevelKey] = []
              }
              thirdLevelGroups[thirdLevelKey].push(item)
            })
            
            Object.entries(thirdLevelGroups).forEach(([thirdLevelKey, thirdItems]) => {
              const thirdLevelExpanded = groupExpanded[thirdLevelKey] === true
              const thirdLevelValue = (thirdItems[0] as any)[groupBy[2]]
              
              // Add third level group
              result.push({
                type: 'group',
                data: { 
                  groupKey: thirdLevelKey, 
                  groupValue: thirdLevelValue, 
                  itemCount: thirdItems.length,
                  level: 3
                },
                groupKey: thirdLevelKey,
                depth: 2
              })
              
              // Don't show individual field rows - stop at level groups
              // The level groups already contain the aggregated data
            })
          } else if (secondLevelExpanded) {
            // If no third level grouping, just show rows directly
            subItems.forEach(item => {
              result.push({ 
                type: 'row', 
                data: item, 
                depth: 2 
              })
            })
          }
        })
      } else if (firstLevelExpanded) {
        // If no second level grouping, just show rows directly
        items.forEach(item => {
          result.push({ 
            type: 'row', 
            data: item, 
            depth: 1 
          })
        })
      }
    })
    
    return result
  }, [data, enableGrouping, groupBy, groupExpanded])
  
  // Disable sorting on all columns to ensure minimal appearance
  const columnsWithoutSorting = React.useMemo(
    () => columns.map(col => ({ ...col, enableSorting: false })),
    [columns]
  )

  let table;
  try {
    table = useReactTable({
      data: enableGrouping ? groupedData.map(item => item.data) : data,
      columns: columnsWithoutSorting,
      getCoreRowModel: getCoreRowModel(),
      getPaginationRowModel: enablePagination ? getPaginationRowModel() : undefined,
      enableSorting: false,
      enableColumnFilters: false,
      enableGlobalFilter: false,
      enableRowSelection: false,
      enableMultiRowSelection: false,
      state: {
        pagination: {
          pageIndex: 0,
          pageSize,
        },
      },
    })
    
    // Table created successfully with explicit pageIndex: 0 in pagination state
    
  } catch (error) {
    console.error('❌ Error creating table:', error)
    throw error
  }

  return (
    <div className={cn("space-y-4", className)}>
      {/* Minimal table with clean styling */}
      {/* Tight minimal table with black background and white text */}
      <div className="overflow-hidden rounded-md border border-gray-600 bg-black">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id} className="border-b border-gray-600 hover:bg-transparent">
                {headerGroup.headers.map((header) => (
                  <TableHead 
                    key={header.id}
                    className="h-12 px-4 text-left align-middle text-sm font-semibold text-white bg-gray-800 border-r border-gray-600 last:border-r-0"
                  >
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
            {enableGrouping ? (
              // Custom grouped rendering
              groupedData.map((item, index) => {
                if (item.type === 'group') {
                  const { groupKey, groupValue, itemCount, level } = item.data
                  const isExpanded = groupExpanded[groupKey!] === true
                  const paddingLeft = item.depth * 20 + 16
                  
                  return (
                    <TableRow key={`group-${groupKey}`} className="border-b border-gray-600 hover:bg-gray-800">
                      <TableCell 
                        className="px-4 py-3 align-middle text-base font-medium text-white border-r border-gray-600"
                        style={{ paddingLeft: `${paddingLeft}px` }}
                      >
                        <div className="flex items-center gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onGroupToggle?.(groupKey!, !isExpanded)}
                            className="h-6 w-6 p-0 hover:bg-gray-700"
                          >
                            {isExpanded ? (
                              <ChevronDown className="h-4 w-4 text-white" />
                            ) : (
                              <ChevronRight className="h-4 w-4 text-white" />
                            )}
                          </Button>
                          <span className="font-semibold">{groupValue}</span>
                          <span className="text-gray-400 text-sm">
                            ({itemCount} items)
                          </span>
                        </div>
                      </TableCell>
                      {/* Fill remaining cells with aggregated values */}
                      {columns.slice(1).map((column, colIndex) => (
                        <TableCell 
                          key={colIndex}
                          className="px-4 py-3 align-middle text-base font-medium text-white border-r border-gray-600 last:border-r-0"
                        >
                          {/* Show aggregated values for numeric columns */}
                          {column.accessorKey && typeof column.accessorKey === 'string' ? (
                            <span className="text-gray-400">
                              {(() => {
                                let groupItems: TData[] = []
                                
                                if (level === 1) {
                                  // First level group - aggregate all items for this field category
                                  groupItems = data.filter(d => (d as any)[groupBy[0]] === groupKey)
                                } else if (level === 2) {
                                  // Second level group - aggregate items for this field-role combination
                                  const [fieldKey, roleKey] = groupKey!.split('-')
                                  groupItems = data.filter(d => 
                                    (d as any)[groupBy[0]] === fieldKey && 
                                    (d as any)[groupBy[1]] === roleKey
                                  )
                                } else if (level === 3) {
                                  // Third level group - aggregate items for this field-role-level combination
                                  const [fieldKey, roleKey, levelKey] = groupKey!.split('-')
                                  groupItems = data.filter(d => 
                                    (d as any)[groupBy[0]] === fieldKey && 
                                    (d as any)[groupBy[1]] === roleKey && 
                                    (d as any)[groupBy[2]] === levelKey
                                  )
                                }
                                
                                const sum = groupItems.reduce((acc, d) => {
                                  const value = (d as any)[column.accessorKey!]
                                  return acc + (typeof value === 'number' ? value : 0)
                                }, 0)
                                
                                // Format numbers properly based on column type
                                if (column.accessorKey === 'utr') {
                                  return (sum * 100).toFixed(1) + '%'
                                } else if (column.accessorKey === 'price' || column.accessorKey === 'salary') {
                                  return Math.round(sum).toLocaleString()
                                } else {
                                  return Math.round(sum).toString()
                                }
                              })()}
                            </span>
                          ) : null}
                        </TableCell>
                      ))}
                    </TableRow>
                  )
                } else {
                  // Regular row
                  const rowData = item.data
                  const paddingLeft = item.depth * 20 + 16
                  
                  return (
                    <TableRow
                      key={`row-${index}`}
                      className={cn(
                        "border-b border-gray-600 transition-colors hover:bg-gray-800",
                        onRowClick && "cursor-pointer"
                      )}
                      onClick={() => onRowClick?.(rowData)}
                    >
                      {columns.map((column, colIndex) => {
                        let value = (rowData as any)[column.accessorKey!]
                        
                        // For the first column, use displayName if available (for individual level rows)
                        if (colIndex === 0 && (rowData as any).displayName) {
                          value = (rowData as any).displayName
                        }
                        
                        return (
                          <TableCell 
                            key={colIndex}
                            className="px-4 py-3 align-middle text-base font-medium text-white border-r border-gray-600 last:border-r-0"
                            style={colIndex === 0 ? { paddingLeft: `${paddingLeft}px` } : undefined}
                          >
                            {enableEditing && column.editable ? (
                              <EditableCell
                                value={value}
                                onEdit={(newValue) => column.editable?.onEdit?.(rowData.id || `row-${index}`, newValue)}
                                config={column.editable}
                              />
                            ) : (
                              colIndex === 0 && (rowData as any).displayName ? 
                                (rowData as any).displayName :
                                // Format numbers for individual row cells
                                typeof value === 'number' && colIndex > 0 ? (
                                  column.accessorKey === 'utr' ? 
                                    (value * 100).toFixed(1) + '%' :
                                  column.accessorKey === 'price' || column.accessorKey === 'salary' ?
                                    Math.round(value).toLocaleString() :
                                    Math.round(value).toString()
                                ) : value
                            )}
                          </TableCell>
                        )
                      })}
                    </TableRow>
                  )
                }
              })
            ) : (
              // Original non-grouped rendering
              (enablePagination ? table.getRowModel() : table.getCoreRowModel()).rows?.length ? (
                (enablePagination ? table.getRowModel() : table.getCoreRowModel()).rows.map((row) => (
                  <TableRow
                    key={row.id}
                    className={cn(
                      "border-b border-gray-600 transition-colors hover:bg-gray-800",
                      onRowClick && "cursor-pointer"
                    )}
                    onClick={() => onRowClick?.(row.original)}
                  >
                    {row.getVisibleCells().map((cell, cellIndex) => {
                      const column = cell.column.columnDef as MinimalColumnDef<TData, TValue>
                      let value = cell.getValue()
                      
                      // For the first column, use displayName if available (for individual level rows)
                      if (cellIndex === 0 && (row.original as any).displayName) {
                        value = (row.original as any).displayName
                      }
                      
                      return (
                        <TableCell 
                          key={cell.id}
                          className="px-4 py-3 align-middle text-base font-medium text-white border-r border-gray-600 last:border-r-0"
                        >
                          {enableEditing && column.editable ? (
                            <EditableCell
                              value={value}
                              onEdit={(newValue) => column.editable?.onEdit?.(row.original.id || row.id, newValue)}
                              config={column.editable}
                            />
                          ) : (
                            cellIndex === 0 && (row.original as any).displayName ? 
                              (row.original as any).displayName :
                              // Format numbers for individual cells in non-grouped view
                              typeof value === 'number' && cellIndex > 0 ? (
                                column.accessorKey === 'utr' ? 
                                  (value * 100).toFixed(1) + '%' :
                                column.accessorKey === 'price' || column.accessorKey === 'salary' ?
                                  Math.round(value).toLocaleString() :
                                  Math.round(value).toString()
                              ) : flexRender(
                                cell.column.columnDef.cell,
                                cell.getContext()
                              )
                          )}
                        </TableCell>
                      )
                    })}
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell
                    colSpan={columns.length}
                    className="h-24 text-center text-sm text-gray-400"
                  >
                    No data available
                  </TableCell>
                </TableRow>
              )
            )}
          </TableBody>
        </Table>
      </div>

      {/* Compact pagination */}
      {enablePagination && table.getPageCount() > 1 && (
        <div className="flex items-center justify-between px-1">
          <div className="text-xs text-gray-400">
            {table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1}-{Math.min((table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize, table.getFilteredRowModel().rows.length)} of {table.getFilteredRowModel().rows.length}
          </div>
          <div className="flex items-center space-x-1">
            <Button
              variant="outline"
              size="sm"
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
              className="h-7 px-2 text-xs"
            >
              Previous
            </Button>
            <div className="text-xs text-gray-400 px-2">
              {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
              className="h-7 px-2 text-xs"
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}