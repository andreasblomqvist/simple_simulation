/**
 * Aggregated Business Plan Table
 * 
 * Extends CleanBusinessPlanTable to show aggregated data across multiple offices
 * Uses the same hierarchical structure and styling
 */
import React, { useState, useMemo, useCallback, useEffect } from 'react';
import { ChevronRight, ChevronDown, Building2 } from 'lucide-react';
import { cn } from '../../lib/utils';
import { Badge } from '../ui/badge';
import { useBusinessPlanStore } from '../../stores/businessPlanStore';
import { useOfficeStore } from '../../stores/officeStore';
import type { OfficeConfig, MonthlyPlanEntry, StandardRole, StandardLevel } from '../../types/office';

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

interface AggregatedBusinessPlanTableProps {
  selectedOffices: string[];
  year: number;
  onViewOfficePlan?: (officeId: string, year: number) => void;
}

// ============================================================================
// CONSTANTS
// ============================================================================

const MONTHS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'] as const;
const MONTH_LABELS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

// Same table structure as CleanBusinessPlanTable
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

export const AggregatedBusinessPlanTable: React.FC<AggregatedBusinessPlanTableProps> = ({
  selectedOffices,
  year,
  onViewOfficePlan
}) => {
  const {
    monthlyPlans,
    loading,
    loadBusinessPlans
  } = useBusinessPlanStore();

  const { offices } = useOfficeStore();

  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set(['workforce', 'revenue', 'costs', 'summary']));

  // Load data for all selected offices
  useEffect(() => {
    if (selectedOffices.length === 0) return;
    
    const loadPromises = selectedOffices.map(officeId => loadBusinessPlans(officeId, year));
    Promise.all(loadPromises).catch(console.error);
  }, [selectedOffices, year]);

  // Aggregate data across offices
  const aggregatedData = useMemo(() => {
    if (!monthlyPlans || monthlyPlans.length === 0 || selectedOffices.length === 0) {
      return new Map<string, { values: number[], officeCount: number }>();
    }

    const aggregatedMap = new Map<string, { values: number[], officeCount: number }>();

    try {
      selectedOffices.forEach(officeId => {
        // Get plans for this office
        const officePlans = monthlyPlans.filter(plan => {
          // Assuming monthlyPlans have an office_id field - adjust if different
          return plan.office_id === officeId && plan.year === year;
        });

        officePlans.forEach(plan => {
          if (!plan.entries || !Array.isArray(plan.entries)) return;
          
          plan.entries.forEach(entry => {
            if (!entry || typeof entry !== 'object') return;
            
            // For each field in the entry
            Object.keys(entry).forEach(fieldKey => {
              if (fieldKey === 'role' || fieldKey === 'level') return;
              
              const value = (entry as any)[fieldKey];
              if (value === undefined || value === null) return;
              
              const aggregationKey = `${entry.role}-${entry.level}-${plan.month}-${fieldKey}`;
              
              if (!aggregatedMap.has(aggregationKey)) {
                aggregatedMap.set(aggregationKey, { values: [], officeCount: 0 });
              }
              
              const agg = aggregatedMap.get(aggregationKey)!;
              agg.values.push(Number(value) || 0);
              agg.officeCount = Math.max(agg.officeCount, selectedOffices.length);
            });
          });
        });
      });
    } catch (error) {
      console.error('Error aggregating data:', error);
      return new Map<string, { values: number[], officeCount: number }>();
    }

    return aggregatedMap;
  }, [monthlyPlans, selectedOffices, year]);

  // Get aggregated value
  const getAggregatedValue = useCallback((role: string, level: string, month: number, field: string): number => {
    const key = `${role}-${level}-${month}-${field}`;
    const agg = aggregatedData.get(key);
    
    if (!agg || agg.values.length === 0) {
      // Default values based on field type
      if (field === 'price') return 1200;
      if (field === 'utr') return 0.75;
      if (field === 'salary') return 65000;
      return 0;
    }
    
    // Sum for additive fields, average for rates/percentages
    if (field === 'utr') {
      return agg.values.reduce((sum, val) => sum + val, 0) / agg.values.length;
    }
    
    return agg.values.reduce((sum, val) => sum + val, 0);
  }, [aggregatedData]);

  // Calculate summary fields
  const calculateSummaryFields = useCallback((month: number) => {
    let totalRevenue = 0;
    let totalCosts = 0;

    // Calculate revenue (only for Consultants)
    const consultantLevels = ROLE_LEVELS.Consultant || ['A', 'AC', 'AM', 'P'];
    consultantLevels.forEach(level => {
      const price = getAggregatedValue('Consultant', level, month, 'price');
      const utr = getAggregatedValue('Consultant', level, month, 'utr');
      const monthlyHours = 160;
      const fte = 1; // Simplified
      
      totalRevenue += price * utr * monthlyHours * fte;
    });

    // Calculate costs - just salary costs for aggregated view
    Object.entries(ROLE_LEVELS).forEach(([role, levels]) => {
      levels.forEach(level => {
        const salary = getAggregatedValue(role, level, month, 'salary');
        const monthlyPortion = salary / 12;
        totalCosts += monthlyPortion;
      });
    });

    const ebitda = totalRevenue - totalCosts;

    return { totalRevenue, totalCosts, ebitda };
  }, [getAggregatedValue]);

  // Build table rows (same structure as CleanBusinessPlanTable)
  const tableRows = useMemo(() => {
    console.log('Building table rows for aggregated view...'); // Debug log
    
    if (!selectedOffices.length) {
      console.log('No offices selected, returning empty rows');
      return [];
    }

    const rows: AggregatedTableRow[] = [];
    let rowId = 0;

    try {
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
                  try {
                    const value = getAggregatedValue(role, level, idx + 1, field.fieldKey);
                    monthlyData[month] = isFinite(value) ? value : 0;
                    total += isFinite(value) ? value : 0;
                  } catch (error) {
                    console.warn(`Error calculating value for ${role} ${level} ${month}:`, error);
                    monthlyData[month] = 0;
                  }
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
                  officeCount: selectedOffices.length,
                  ...monthlyData,
                  total: isFinite(total) ? total : 0
                });
              });
            });
          } else {
            // Office-level calculated fields
            const monthlyData: any = {};
            let total = 0;

            MONTHS.forEach((month, idx) => {
              let value = 0;
              
              try {
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
              } catch (error) {
                console.warn(`Error calculating summary field ${field.fieldKey} for month ${idx + 1}:`, error);
                value = 0;
              }
              
              monthlyData[month] = isFinite(value) ? value : 0;
              total += isFinite(value) ? value : 0;
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
              officeCount: selectedOffices.length,
              ...monthlyData,
              total: isFinite(total) ? total : 0
            });
          }
        });
      });

      console.log(`Built ${rows.length} table rows successfully`);
      return rows;
    } catch (error) {
      console.error('Error building table rows:', error);
      return [];
    }
  }, [getAggregatedValue, calculateSummaryFields, selectedOffices.length]);

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

  // Filter visible rows based on expansion state
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
    return selectedOffices.map(id => {
      const office = offices.find(o => o.id === id);
      return office ? office.name : id;
    }).join(', ');
  }, [selectedOffices, offices]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading aggregated business plan data...</p>
        </div>
      </div>
    );
  }

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
              {selectedOffices.length} offices: {officeNames}
            </span>
          </div>
        </div>
        <Badge variant="secondary">
          Read-only aggregated data
        </Badge>
      </div>

      {/* Table with same styling as CleanBusinessPlanTable */}
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
                        "text-center p-1 rounded text-gray-300",
                        row.isCalculated && "text-green-300 font-medium"
                      )}>
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
                      row.isCalculated ? "text-green-300 font-medium" : "text-gray-300"
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

// Helper function to format values (same as CleanBusinessPlanTable)
function formatValue(value: number, fieldKey?: string): string {
  if (fieldKey === 'utr') {
    return `${Math.round(value * 100)}%`;
  }
  if (fieldKey?.includes('cost') || fieldKey?.includes('revenue') || fieldKey?.includes('ebitda')) {
    return value >= 1000 ? `${Math.round(value / 1000)}k` : value.toString();
  }
  return Math.round(value).toString();
}