/**
 * Clean Aggregated Business Plan Table
 * 
 * Simple, stable version without complex dependencies
 */
import React, { useState, useMemo, useCallback } from 'react';
import { ChevronRight, ChevronDown, Building2 } from 'lucide-react';
import { cn } from '../../lib/utils';
import { Badge } from '../ui/badge';
import { useOfficeStore } from '../../stores/officeStore';
import type { StandardRole, StandardLevel } from '../../types/office';

// ============================================================================
// TYPES
// ============================================================================

type RowType = 'category' | 'field' | 'role' | 'level' | 'office-field';

interface AggregatedTableRow {
  id: string;
  type: RowType;
  name: string;
  depth: number;
  isEditable: boolean;
  isCalculated: boolean;
  
  // Data for leaf nodes
  fieldKey?: string;
  role?: StandardRole;
  level?: StandardLevel;
  
  // Monthly values (aggregated across offices)
  jan?: number;
  feb?: number;
  mar?: number;
  apr?: number;
  may?: number;
  jun?: number;
  jul?: number;
  aug?: number;
  sep?: number;
  oct?: number;
  nov?: number;
  dec?: number;
  total?: number;
  
  // Office count for this aggregation
  officeCount?: number;
  
  // Hierarchy
  parentId?: string;
  children?: string[];
}

interface CleanAggregatedTableProps {
  selectedOffices: string[];
  year: number;
  onViewOfficePlan?: (officeId: string, year: number) => void;
}

// ============================================================================
// CONSTANTS
// ============================================================================

const MONTHS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'] as const;
const MONTH_LABELS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

// Complete table structure
const TABLE_STRUCTURE = [
  {
    id: 'workforce',
    name: '📊 WORKFORCE',
    type: 'category' as RowType,
    fields: [
      {
        id: 'recruitment',
        name: 'Recruitment',
        fieldKey: 'recruitment',
        hasRoles: true,
        roles: ['Consultant', 'Sales', 'Recruitment', 'Operations']
      },
      {
        id: 'churn',
        name: 'Churn',
        fieldKey: 'churn',
        hasRoles: true,
        roles: ['Consultant', 'Sales', 'Recruitment', 'Operations']
      }
    ]
  },
  {
    id: 'revenue',
    name: '💰 REVENUE',
    type: 'category' as RowType,
    fields: [
      {
        id: 'price',
        name: 'Price (€/h)',
        fieldKey: 'price',
        hasRoles: true,
        roles: ['Consultant']
      },
      {
        id: 'utr',
        name: 'Utilization Rate (%)',
        fieldKey: 'utr',
        hasRoles: true,
        roles: ['Consultant']
      }
    ]
  },
  {
    id: 'costs',
    name: '💸 OPERATING COSTS',
    type: 'category' as RowType,
    fields: [
      {
        id: 'salary',
        name: 'Salaries',
        fieldKey: 'salary',
        hasRoles: true,
        roles: ['Consultant', 'Sales', 'Recruitment', 'Operations']
      }
    ]
  },
  {
    id: 'summary',
    name: '📈 SUMMARY',
    type: 'category' as RowType,
    fields: [
      {
        id: 'total_revenue',
        name: 'Total Revenue',
        fieldKey: 'total_revenue',
        hasRoles: false,
        isCalculated: true
      },
      {
        id: 'total_costs',
        name: 'Total Costs',
        fieldKey: 'total_costs',
        hasRoles: false,
        isCalculated: true
      },
      {
        id: 'ebitda',
        name: 'EBITDA',
        fieldKey: 'ebitda',
        hasRoles: false,
        isCalculated: true
      }
    ]
  }
];

const ROLE_LEVELS: Record<string, string[]> = {
  Consultant: ['A', 'AC', 'AM', 'P'],
  Sales: ['A', 'AC', 'AM', 'P'],
  Recruitment: ['A', 'AC', 'AM', 'P'],
  Operations: ['General']
};

// ============================================================================
// COMPONENT
// ============================================================================

export const CleanAggregatedTable: React.FC<CleanAggregatedTableProps> = ({
  selectedOffices,
  year,
  onViewOfficePlan
}) => {
  const { offices } = useOfficeStore();
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set(['workforce', 'revenue', 'costs', 'summary']));

  // Simple data generation
  const getSampleValue = useCallback((role: string, level: string, month: number, field: string): number => {
    // Generate consistent sample data based on inputs
    const seed = role.length + level.length + month + field.length;
    const random = (seed * 9301 + 49297) % 233280; // Simple PRNG
    const normalized = random / 233280;
    
    switch (field) {
      case 'recruitment':
        return Math.floor(normalized * 4) + 1; // 1-4 people
      case 'churn':
        return Math.floor(normalized * 2); // 0-1 people
      case 'price':
        return role === 'Consultant' ? Math.floor(1200 + normalized * 300) : 0; // €1200-1500/h
      case 'utr':
        return role === 'Consultant' ? Math.round((0.7 + normalized * 0.2) * 100) / 100 : 0; // 70-90%
      case 'salary':
        return Math.floor(50000 + normalized * 40000); // €50k-90k
      default:
        return 0;
    }
  }, []);

  // Calculate summary fields
  const calculateSummaryFields = useCallback((month: number) => {
    let totalRevenue = 0;
    let totalCosts = 0;

    const officeMultiplier = Math.min(selectedOffices.length, 5);

    // Revenue calculation (Consultants only)
    ROLE_LEVELS.Consultant.forEach(level => {
      const price = getSampleValue('Consultant', level, month, 'price');
      const utr = getSampleValue('Consultant', level, month, 'utr');
      const monthlyHours = 160;
      const fte = 2; // Assume 2 FTE per level
      
      totalRevenue += (price * utr * monthlyHours * fte * officeMultiplier);
    });

    // Cost calculation (all roles)
    Object.entries(ROLE_LEVELS).forEach(([role, levels]) => {
      levels.forEach(level => {
        const salary = getSampleValue(role, level, month, 'salary');
        const monthlyPortion = salary / 12;
        const fte = role === 'Operations' ? 1 : 2; // Assume FTE counts
        totalCosts += (monthlyPortion * fte * officeMultiplier);
      });
    });

    const ebitda = totalRevenue - totalCosts;

    return { totalRevenue, totalCosts, ebitda };
  }, [getSampleValue, selectedOffices.length]);

  // Build table rows
  const tableRows = useMemo(() => {
    const rows: AggregatedTableRow[] = [];
    let rowId = 0;

    TABLE_STRUCTURE.forEach(category => {
      const categoryId = `row-${rowId++}`;
      
      rows.push({
        id: categoryId,
        type: 'category',
        name: category.name,
        depth: 0,
        isEditable: false,
        isCalculated: false,
        children: []
      });

      const categoryRow = rows.find(r => r.id === categoryId);

      category.fields.forEach(field => {
        const fieldId = `row-${rowId++}`;
        if (categoryRow && categoryRow.children) {
          categoryRow.children.push(fieldId);
        }

        if (field.hasRoles) {
          rows.push({
            id: fieldId,
            type: 'field',
            name: field.name,
            depth: 1,
            isEditable: false,
            isCalculated: false,
            parentId: categoryId,
            children: []
          });

          field.roles!.forEach(role => {
            const roleId = `row-${rowId++}`;
            const fieldRow = rows.find(r => r.id === fieldId);
            if (fieldRow && fieldRow.children) {
              fieldRow.children.push(roleId);
            }

            const roleRow = {
              id: roleId,
              type: 'role' as RowType,
              name: role,
              depth: 2,
              isEditable: false,
              isCalculated: false,
              parentId: fieldId,
              children: [] as string[]
            };
            rows.push(roleRow);

            const levels = ROLE_LEVELS[role] || ['A'];
            levels.forEach(level => {
              const levelId = `row-${rowId++}`;
              roleRow.children.push(levelId);

              const monthlyData: any = {};
              let total = 0;

              MONTHS.forEach((month, idx) => {
                const value = getSampleValue(role, level, idx + 1, field.fieldKey);
                const aggregatedValue = value * Math.min(selectedOffices.length, 5); // Multiply by office count
                monthlyData[month] = aggregatedValue;
                total += aggregatedValue;
              });

              rows.push({
                id: levelId,
                type: 'level',
                name: level,
                depth: 3,
                isEditable: false, // Aggregated data is read-only
                isCalculated: false,
                parentId: roleId,
                fieldKey: field.fieldKey,
                role: role as StandardRole,
                level: level as StandardLevel,
                officeCount: Math.min(selectedOffices.length, 5),
                ...monthlyData,
                total
              });
            });
          });
        } else {
          // Office-level calculated fields
          const monthlyData: any = {};
          let total = 0;

          MONTHS.forEach((month, idx) => {
            let value = 0;
            
            if (field.isCalculated) {
              const summary = calculateSummaryFields(idx + 1);
              switch (field.fieldKey) {
                case 'total_revenue':
                  value = summary.totalRevenue;
                  break;
                case 'total_costs':
                  value = summary.totalCosts;
                  break;
                case 'ebitda':
                  value = summary.ebitda;
                  break;
              }
            }
            
            monthlyData[month] = value;
            total += value;
          });

          rows.push({
            id: fieldId,
            type: 'office-field',
            name: field.name,
            depth: 1,
            isEditable: false,
            isCalculated: !!field.isCalculated,
            parentId: categoryId,
            fieldKey: field.fieldKey,
            officeCount: Math.min(selectedOffices.length, 5),
            ...monthlyData,
            total
          });
        }
      });
    });

    return rows;
  }, [getSampleValue, calculateSummaryFields, selectedOffices.length]);

  // Toggle row expansion
  const toggleRow = useCallback((rowId: string) => {
    setExpandedRows(prev => {
      const next = new Set(prev);
      if (next.has(rowId)) {
        next.delete(rowId);
      } else {
        next.add(rowId);
      }
      return next;
    });
  }, []);

  // Filter visible rows
  const visibleRows = useMemo(() => {
    const visible: AggregatedTableRow[] = [];
    
    const addRow = (row: AggregatedTableRow) => {
      visible.push(row);
      
      if (row.children && expandedRows.has(row.id)) {
        row.children.forEach(childId => {
          const child = tableRows.find(r => r.id === childId);
          if (child) addRow(child);
        });
      }
    };
    
    tableRows.filter(r => !r.parentId).forEach(addRow);
    
    return visible;
  }, [tableRows, expandedRows]);

  // Get office names for display
  const officeNames = useMemo(() => {
    const maxDisplay = Math.min(selectedOffices.length, 5);
    const displayOffices = selectedOffices.slice(0, maxDisplay);
    
    return displayOffices.map(id => {
      const office = offices.find(o => o.id === id);
      return office ? office.name : id;
    }).join(', ') + (selectedOffices.length > maxDisplay ? ` (+${selectedOffices.length - maxDisplay} more)` : '');
  }, [selectedOffices, offices]);

  if (selectedOffices.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-muted-foreground">No offices selected for aggregation</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg border">
        <div>
          <h3 className="font-semibold">
            Aggregated Business Plan - {year}
          </h3>
          <div className="flex items-center gap-2 mt-1">
            <Building2 className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">
              {Math.min(selectedOffices.length, 5)} offices: {officeNames}
            </span>
          </div>
        </div>
        <div className="flex gap-2">
          <Badge variant="secondary">
            Sample aggregated data
          </Badge>
          {selectedOffices.length > 5 && (
            <Badge variant="outline">
              Limited to 5 offices
            </Badge>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="overflow-hidden rounded-md border border-gray-600 bg-black">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-600 hover:bg-transparent">
              <th className="h-12 px-4 text-left align-middle text-sm font-semibold text-white bg-gray-800 border-r border-gray-600 w-80">
                Category / Field / Role / Level
              </th>
              {MONTH_LABELS.map(month => (
                <th key={month} className="h-12 px-4 text-center align-middle text-sm font-semibold text-white bg-gray-800 border-r border-gray-600 w-20">
                  {month}
                </th>
              ))}
              <th className="h-12 px-4 text-center align-middle text-sm font-semibold text-white bg-gray-800 w-24">
                Total
              </th>
            </tr>
          </thead>
          <tbody>
            {visibleRows.map(row => (
              <tr
                key={row.id}
                className={cn(
                  "border-b border-gray-600 transition-colors hover:bg-gray-800",
                  row.type === 'category' && "bg-gray-900 font-semibold",
                  row.type === 'office-field' && row.isCalculated && "bg-green-950/20"
                )}
              >
                <td className="px-4 py-3 align-middle text-base font-medium text-white border-r border-gray-600">
                  <div
                    className="flex items-center gap-2"
                    style={{ paddingLeft: `${row.depth * 20}px` }}
                  >
                    {row.children && row.children.length > 0 && (
                      <button
                        onClick={() => toggleRow(row.id)}
                        className="h-6 w-6 p-0 hover:bg-gray-700 rounded"
                      >
                        {expandedRows.has(row.id) ? (
                          <ChevronDown className="h-4 w-4 text-white" />
                        ) : (
                          <ChevronRight className="h-4 w-4 text-white" />
                        )}
                      </button>
                    )}
                    <span className={cn(
                      "font-semibold",
                      row.type === 'category' && "text-base",
                      row.type === 'field' && "text-sm font-medium",
                      row.type === 'role' && "text-sm",
                      row.type === 'level' && "text-sm text-gray-400",
                      row.type === 'office-field' && "text-sm"
                    )}>
                      {row.name}
                    </span>
                    {row.officeCount && row.type === 'level' && (
                      <Badge variant="outline" className="text-xs">
                        {row.officeCount} offices
                      </Badge>
                    )}
                  </div>
                </td>
                
                {/* Month cells */}
                {MONTHS.map(month => {
                  const value = row[month];
                  
                  if (row.type === 'category' || row.type === 'field' || row.type === 'role') {
                    return (
                      <td key={month} className="px-4 py-3 align-middle text-base font-medium text-white border-r border-gray-600 last:border-r-0">
                        <span className="text-gray-400">-</span>
                      </td>
                    );
                  }
                  
                  return (
                    <td key={month} className="px-4 py-3 align-middle text-base font-medium text-white border-r border-gray-600 last:border-r-0">
                      <div className={cn(
                        "text-center p-1 rounded",
                        row.isEditable && "cursor-pointer hover:bg-gray-700 border border-yellow-400/70 hover:border-yellow-400",
                        !row.isEditable && "text-gray-500 cursor-not-allowed",
                        row.isCalculated && "text-green-300 font-medium"
                      )}
                      title="Read-only aggregated data">
                        {value !== undefined ? formatValue(value, row.fieldKey) : '-'}
                      </div>
                    </td>
                  );
                })}
                
                {/* Total cell */}
                <td className="px-4 py-3 align-middle text-base font-medium text-white text-center">
                  <div className={cn(
                    "p-1 rounded text-center",
                    row.type === 'level' || row.type === 'office-field' ? (
                      row.isCalculated ? "text-green-300 font-medium" : "text-gray-500"
                    ) : "text-gray-500"
                  )}>
                    {row.total !== undefined ? formatValue(row.total, row.fieldKey) : '-'}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// Helper function to format values
function formatValue(value: number, fieldKey?: string): string {
  if (fieldKey === 'utr') {
    return `${Math.round(value * 100)}%`;
  }
  if (fieldKey?.includes('cost') || fieldKey?.includes('revenue') || fieldKey?.includes('ebitda')) {
    return value >= 1000 ? `${Math.round(value / 1000)}k` : value.toString();
  }
  return Math.round(value).toString();
}