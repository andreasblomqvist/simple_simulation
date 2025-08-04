/**
 * Clean Business Plan Table
 * 
 * A simplified hierarchical table for business planning with:
 * - Category → Field → Role → Level structure (4 levels)
 * - Office-level fields (no role/level breakdown)
 * - Calculated fields (read-only)
 * - Expandable/collapsible groups
 */
import React, { useState, useMemo, useCallback, useEffect } from 'react';
import { ChevronRight, ChevronDown } from 'lucide-react';
import { cn } from '../../lib/utils';
import { useBusinessPlanStore } from '../../stores/businessPlanStore';
import type { OfficeConfig, MonthlyPlanEntry, StandardRole, StandardLevel } from '../../types/office';

// ============================================================================
// TYPES
// ============================================================================

type RowType = 'category' | 'field' | 'role' | 'level' | 'office-field';

interface TableRow {
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
  
  // Monthly values (only for data rows)
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
  
  // Hierarchy
  parentId?: string;
  children?: string[];
}

interface CleanBusinessPlanTableProps {
  office: OfficeConfig;
  year: number;
  // Optional props for aggregated view
  isAggregated?: boolean;
  selectedOffices?: string[];
  aggregatedData?: Map<string, number>;
}

// ============================================================================
// CONSTANTS
// ============================================================================

const MONTHS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'] as const;
const MONTH_LABELS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

// Table structure configuration
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
        roles: ['Consultant'] // Only consultants have pricing
      },
      {
        id: 'utr',
        name: 'Utilization Rate (%)',
        fieldKey: 'utr',
        hasRoles: true,
        roles: ['Consultant'] // Only consultants have utilization
      }
    ]
  },
  {
    id: 'costs',
    name: '💸 OPERATING COSTS',
    type: 'category' as RowType,
    fields: [
      {
        id: 'office_rent',
        name: 'Office Rent',
        fieldKey: 'office_rent',
        hasRoles: false, // Office-level field
        defaultValue: 50000
      },
      {
        id: 'it_services',
        name: 'IT Services',
        fieldKey: 'it_services',
        hasRoles: false, // Office-level field
        defaultValue: 8000
      },
      {
        id: 'travel',
        name: 'Travel',
        fieldKey: 'travel',
        hasRoles: false, // Office-level field
        defaultValue: 5000
      },
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
      },
      {
        id: 'ebitda_margin',
        name: 'EBITDA Margin %',
        fieldKey: 'ebitda_margin',
        hasRoles: false,
        isCalculated: true
      }
    ]
  }
];

// Role levels configuration
const ROLE_LEVELS: Record<string, string[]> = {
  Consultant: ['A', 'AC', 'AM', 'P'],
  Sales: ['A', 'AC', 'AM', 'P'],
  Recruitment: ['A', 'AC', 'AM', 'P'],
  Operations: ['General'] // Flat role
};

// ============================================================================
// COMPONENT
// ============================================================================

export const CleanBusinessPlanTable: React.FC<CleanBusinessPlanTableProps> = ({
  office,
  year,
  isAggregated = false,
  selectedOffices = [],
  aggregatedData
}) => {
  const {
    monthlyPlans,
    loading,
    loadBusinessPlans,
    createMonthlyPlan,
    updateMonthlyPlan
  } = useBusinessPlanStore();

  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set(['workforce', 'revenue', 'costs', 'summary']));
  const [editingCell, setEditingCell] = useState<string | null>(null);
  const [localChanges, setLocalChanges] = useState<Map<string, number>>(new Map());

  // Load data on mount (skip for aggregated view)
  useEffect(() => {
    if (office?.id && !isAggregated) {
      loadBusinessPlans(office.id, year);
    }
  }, [office?.id, year, loadBusinessPlans, isAggregated]);

  // Build plan data map for quick lookup
  const planDataMap = useMemo(() => {
    const map = new Map<string, MonthlyPlanEntry>();
    
    monthlyPlans.forEach(plan => {
      plan.entries.forEach(entry => {
        const key = `${entry.role}-${entry.level}-${plan.month}`;
        map.set(key, entry);
      });
    });
    
    return map;
  }, [monthlyPlans]);

  // Get value from plan data or local changes
  const getValue = useCallback((role: string, level: string, month: number, field: string): number => {
    // For aggregated view, use provided aggregated data
    if (isAggregated && aggregatedData) {
      const aggregatedKey = `${role}-${level}-${month}-${field}`;
      const aggregatedValue = aggregatedData.get(aggregatedKey);
      if (aggregatedValue !== undefined) {
        return aggregatedValue;
      }
      
      // Generate sample data for aggregated view if not provided
      const seed = role.length + level.length + month + field.length;
      const random = (seed * 9301 + 49297) % 233280;
      const normalized = random / 233280;
      const officeMultiplier = Math.min(selectedOffices.length, 5);
      
      switch (field) {
        case 'recruitment':
          return Math.floor(normalized * 4 + 1) * officeMultiplier;
        case 'churn':
          return Math.floor(normalized * 2) * officeMultiplier;
        case 'price':
          return role === 'Consultant' ? Math.floor(1200 + normalized * 300) : 0;
        case 'utr':
          return role === 'Consultant' ? Math.round((0.7 + normalized * 0.2) * 100) / 100 : 0;
        case 'salary':
          return Math.floor(50000 + normalized * 40000);
        default:
          return 0;
      }
    }

    // For single office view, use existing logic
    const changeKey = `${role}-${level}-${month}-${field}`;
    if (localChanges.has(changeKey)) {
      return localChanges.get(changeKey)!;
    }

    const planKey = `${role}-${level}-${month}`;
    const planEntry = planDataMap.get(planKey);
    
    if (planEntry && field in planEntry) {
      return (planEntry as any)[field] || 0;
    }
    
    // Default values
    if (field === 'price') return 1200;
    if (field === 'utr') return 0.75;
    if (field === 'salary') return 65000;
    return 0;
  }, [planDataMap, localChanges, isAggregated, aggregatedData, selectedOffices]);

  // Calculate summary fields
  const calculateSummaryFields = useCallback((month: number) => {
    let totalRevenue = 0;
    let totalCosts = 0;

    const officeMultiplier = isAggregated ? Math.min(selectedOffices.length, 5) : 1;

    // Calculate revenue (only for Consultants)
    const consultantLevels = ROLE_LEVELS.Consultant || ['A', 'AC', 'AM', 'P'];
    consultantLevels.forEach(level => {
      const price = getValue('Consultant', level, month, 'price');
      const utr = getValue('Consultant', level, month, 'utr');
      const monthlyHours = 160; // Standard working hours
      const fte = isAggregated ? 2 : 1; // More FTE for aggregated view
      
      totalRevenue += price * utr * monthlyHours * fte * officeMultiplier;
    });

    // Calculate costs
    // Office-level costs (scale by number of offices for aggregated view)
    totalCosts += 50000 * officeMultiplier; // Office rent
    totalCosts += 8000 * officeMultiplier;  // IT services
    totalCosts += 5000 * officeMultiplier;  // Travel

    // Salary costs for all roles
    Object.entries(ROLE_LEVELS).forEach(([role, levels]) => {
      levels.forEach(level => {
        const salary = getValue(role, level, month, 'salary');
        const monthlyPortion = salary / 12;
        const fteCount = isAggregated ? (role === 'Operations' ? 1 : 2) : 1;
        totalCosts += monthlyPortion * fteCount * officeMultiplier;
      });
    });

    const ebitda = totalRevenue - totalCosts;
    const ebitdaMargin = totalRevenue > 0 ? (ebitda / totalRevenue) * 100 : 0;

    return { totalRevenue, totalCosts, ebitda, ebitdaMargin };
  }, [getValue, isAggregated, selectedOffices]);

  // Build table rows
  const tableRows = useMemo(() => {
    const rows: TableRow[] = [];
    let rowId = 0;

    TABLE_STRUCTURE.forEach(category => {
      const categoryId = `row-${rowId++}`;
      
      // Add category row
      const categoryRow = {
        id: categoryId,
        type: 'category',
        name: category.name,
        depth: 0,
        isEditable: false,
        isCalculated: false,
        children: []
      };
      rows.push(categoryRow);

      category.fields.forEach(field => {
        const fieldId = `row-${rowId++}`;
        categoryRow.children.push(fieldId);

        if (field.hasRoles) {
          // Field with role/level breakdown
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

              // Create monthly data
              const monthlyData: any = {};
              let total = 0;

              MONTHS.forEach((month, idx) => {
                const value = getValue(role, level, idx + 1, field.fieldKey);
                monthlyData[month] = value;
                total += value;
              });

              rows.push({
                id: levelId,
                type: 'level',
                name: level,
                depth: 3,
                isEditable: !field.isCalculated, // Show as editable but handle clicks differently
                isCalculated: !!field.isCalculated,
                parentId: roleId,
                fieldKey: field.fieldKey,
                role: role as StandardRole,
                level: level as StandardLevel,
                ...monthlyData,
                total
              });
            });
          });
        } else {
          // Office-level field (no role breakdown)
          const monthlyData: any = {};
          let total = 0;

          MONTHS.forEach((month, idx) => {
            let value = 0;
            
            if (field.isCalculated) {
              // Calculate summary fields
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
                case 'ebitda_margin':
                  value = summary.ebitdaMargin;
                  break;
              }
            } else {
              // Use default value for office-level fields
              value = field.defaultValue || 0;
            }
            
            monthlyData[month] = value;
            total += value;
          });

          rows.push({
            id: fieldId,
            type: 'office-field',
            name: field.name,
            depth: 1,
            isEditable: !field.isCalculated, // Show as editable but handle clicks differently
            isCalculated: !!field.isCalculated,
            parentId: categoryId,
            fieldKey: field.fieldKey,
            ...monthlyData,
            total
          });
        }
      });
    });

    return rows;
  }, [getValue, calculateSummaryFields]);

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

  // Handle cell edit
  const handleCellEdit = useCallback((rowId: string, month: string, value: number) => {
    const row = tableRows.find(r => r.id === rowId);
    if (!row || !row.isEditable) return;

    const monthIndex = MONTHS.indexOf(month as any) + 1;
    const changeKey = `${row.role}-${row.level}-${monthIndex}-${row.fieldKey}`;
    
    setLocalChanges(prev => new Map(prev).set(changeKey, value));
  }, [tableRows]);

  // Save changes
  const handleSave = useCallback(async () => {
    if (!office?.id || localChanges.size === 0) return;

    // Group changes by month
    const changesByMonth = new Map<number, Map<string, MonthlyPlanEntry>>();

    localChanges.forEach((value, key) => {
      const [role, level, month, field] = key.split('-');
      const monthNum = parseInt(month);
      
      if (!changesByMonth.has(monthNum)) {
        changesByMonth.set(monthNum, new Map());
      }
      
      const monthChanges = changesByMonth.get(monthNum)!;
      const entryKey = `${role}-${level}`;
      
      if (!monthChanges.has(entryKey)) {
        const existing = planDataMap.get(`${role}-${level}-${monthNum}`);
        monthChanges.set(entryKey, {
          role: role as StandardRole,
          level: level as StandardLevel,
          recruitment: existing?.recruitment || 0,
          churn: existing?.churn || 0,
          salary: existing?.salary || 65000,
          price: existing?.price || 1200,
          utr: existing?.utr || 0.75
        });
      }
      
      const entry = monthChanges.get(entryKey)!;
      (entry as any)[field] = value;
    });

    // Save all changes
    const promises: Promise<any>[] = [];
    
    changesByMonth.forEach((entries, month) => {
      const entriesArray = Array.from(entries.values());
      const existingPlan = monthlyPlans.find(p => p.month === month && p.year === year);
      
      if (existingPlan) {
        promises.push(updateMonthlyPlan({
          ...existingPlan,
          entries: entriesArray
        }));
      } else {
        promises.push(createMonthlyPlan({
          office_id: office.id,
          year,
          month,
          entries: entriesArray
        }));
      }
    });

    await Promise.all(promises);
    
    // Clear local changes and reload
    setLocalChanges(new Map());
    await loadBusinessPlans(office.id, year);
  }, [office?.id, localChanges, planDataMap, monthlyPlans, year, updateMonthlyPlan, createMonthlyPlan, loadBusinessPlans]);

  // Filter visible rows based on expansion state
  const visibleRows = useMemo(() => {
    const visible: TableRow[] = [];
    
    const addRow = (row: TableRow) => {
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading business plan data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg border">
        <h3 className="font-semibold">
          {isAggregated ? `Aggregated (${selectedOffices.length} offices)` : office.name} - {year} Business Plan
        </h3>
        <div className="flex gap-2">
          {!isAggregated && localChanges.size > 0 && (
            <>
              <button
                onClick={() => setLocalChanges(new Map())}
                className="px-3 py-1 text-sm border rounded hover:bg-muted"
              >
                Discard Changes
              </button>
              <button
                onClick={handleSave}
                className="px-3 py-1 text-sm bg-primary text-primary-foreground rounded hover:bg-primary/90"
              >
                Save Changes ({localChanges.size})
              </button>
            </>
          )}
          {isAggregated && (
            <div className="px-3 py-1 text-sm text-muted-foreground">
              Read-only aggregated data
            </div>
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
                  </div>
                </td>
                
                {/* Month cells */}
                {MONTHS.map(month => {
                  const cellKey = `${row.id}-${month}`;
                  const value = row[month];
                  const isEditing = editingCell === cellKey;
                  
                  // Non-data rows show empty cells
                  if (row.type === 'category' || row.type === 'field' || row.type === 'role') {
                    return (
                      <td key={month} className="px-4 py-3 align-middle text-base font-medium text-white border-r border-gray-600 last:border-r-0">
                        <span className="text-gray-400">-</span>
                      </td>
                    );
                  }
                  
                  return (
                    <td key={month} className="px-4 py-3 align-middle text-base font-medium text-white border-r border-gray-600 last:border-r-0">
                      {isEditing && row.isEditable ? (
                        <input
                          type="number"
                          defaultValue={value}
                          onBlur={(e) => {
                            handleCellEdit(row.id, month, parseFloat(e.target.value) || 0);
                            setEditingCell(null);
                          }}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') {
                              handleCellEdit(row.id, month, parseFloat(e.currentTarget.value) || 0);
                              setEditingCell(null);
                            }
                            if (e.key === 'Escape') {
                              setEditingCell(null);
                            }
                          }}
                          className="h-8 w-full bg-gray-700 text-white border-gray-500 text-center text-xs focus:outline-none focus:ring-2 focus:ring-primary [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                          autoFocus
                        />
                      ) : (
                        <div
                          onClick={() => row.isEditable && !isAggregated && setEditingCell(cellKey)}
                          className={cn(
                            "text-center p-1 rounded",
                            row.isEditable && "cursor-pointer hover:bg-gray-700 border border-yellow-400/70 hover:border-yellow-400",
                            !row.isEditable && "text-gray-500 cursor-not-allowed",
                            row.isCalculated && "text-green-300 font-medium",
                            isAggregated && row.isEditable && "cursor-default", // Override cursor for aggregated
                            localChanges.has(`${row.role}-${row.level}-${MONTHS.indexOf(month) + 1}-${row.fieldKey}`) && 
                              "bg-blue-950/30"
                          )}
                          title={isAggregated ? "Read-only aggregated data" : (row.isEditable ? "Click to edit" : "Read-only field")}
                        >
                          {value !== undefined ? formatValue(value, row.fieldKey) : '-'}
                        </div>
                      )}
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

// ============================================================================
// HELPERS
// ============================================================================

function formatValue(value: number, fieldKey?: string): string {
  if (fieldKey === 'utr') {
    return `${Math.round(value * 100)}%`;
  }
  if (fieldKey === 'ebitda_margin') {
    return `${value.toFixed(1)}%`;
  }
  if (fieldKey === 'price' || fieldKey?.includes('cost') || fieldKey?.includes('revenue') || fieldKey?.includes('ebitda')) {
    return value >= 1000 ? `${Math.round(value / 1000)}k` : value.toString();
  }
  return Math.round(value).toString();
}