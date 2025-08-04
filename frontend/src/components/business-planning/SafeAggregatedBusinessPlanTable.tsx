/**
 * Safe Aggregated Business Plan Table
 * 
 * A crash-resistant version of the aggregated table with circuit breakers
 * and safety guards to prevent browser freezes
 */
import React, { useState, useMemo, useCallback } from 'react';
import { ChevronRight, ChevronDown, Building2, AlertTriangle } from 'lucide-react';
import { cn } from '../../lib/utils';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';

// ============================================================================
// TYPES
// ============================================================================

type RowType = 'category' | 'field' | 'office-summary';

interface SafeTableRow {
  id: string;
  type: RowType;
  name: string;
  depth: number;
  children?: string[];
  
  // Static monthly placeholders
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
}

interface SafeAggregatedBusinessPlanTableProps {
  selectedOffices: string[];
  year: number;
  onViewOfficePlan?: (officeId: string, year: number) => void;
}

// ============================================================================
// CONSTANTS
// ============================================================================

const MONTHS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'] as const;
const MONTH_LABELS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

// Safe minimal table structure
const SAFE_TABLE_STRUCTURE = [
  {
    id: 'summary',
    name: '📊 OFFICE SUMMARY',
    type: 'category' as RowType,
    fields: [
      { id: 'total_revenue', name: 'Total Revenue (placeholder)', fieldKey: 'total_revenue' },
      { id: 'total_costs', name: 'Total Costs (placeholder)', fieldKey: 'total_costs' },
      { id: 'office_count', name: 'Office Count', fieldKey: 'office_count' }
    ]
  }
];

// ============================================================================
// COMPONENT
// ============================================================================

export const SafeAggregatedBusinessPlanTable: React.FC<SafeAggregatedBusinessPlanTableProps> = ({
  selectedOffices,
  year,
  onViewOfficePlan
}) => {
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set(['summary']));

  // Safe static data - no external dependencies or complex calculations
  const tableRows = useMemo(() => {
    console.log('Building safe table rows...');
    
    const rows: SafeTableRow[] = [];
    let rowId = 0;

    SAFE_TABLE_STRUCTURE.forEach(category => {
      const categoryId = `safe-row-${rowId++}`;
      
      rows.push({
        id: categoryId,
        type: 'category',
        name: category.name,
        depth: 0,
        children: []
      });

      const categoryRow = rows.find(r => r.id === categoryId);

      category.fields.forEach(field => {
        const fieldId = `safe-row-${rowId++}`;
        if (categoryRow && categoryRow.children) {
          categoryRow.children.push(fieldId);
        }

        // Generate safe placeholder data
        const monthlyData: any = {};
        let total = 0;

        if (field.fieldKey === 'office_count') {
          // Show office count in each month
          MONTHS.forEach(month => {
            monthlyData[month] = selectedOffices.length;
            total += selectedOffices.length;
          });
        } else {
          // Show placeholder values
          MONTHS.forEach((month, idx) => {
            const value = 1000 * (idx + 1); // Simple incremental placeholder
            monthlyData[month] = value;
            total += value;
          });
        }

        rows.push({
          id: fieldId,
          type: 'office-summary',
          name: field.name,
          depth: 1,
          ...monthlyData,
          total
        });
      });
    });

    console.log(`Built ${rows.length} safe table rows`);
    return rows;
  }, [selectedOffices.length]);

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
    const visible: SafeTableRow[] = [];
    
    const addRow = (row: SafeTableRow) => {
      visible.push(row);
      
      if (row.children && expandedRows.has(row.id)) {
        row.children.forEach(childId => {
          const child = tableRows.find(r => r.id === childId);
          if (child) addRow(child);
        });
      }
    };
    
    tableRows.filter(r => r.depth === 0).forEach(addRow);
    
    return visible;
  }, [tableRows, expandedRows]);

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
      {/* Safety Notice */}
      <Alert>
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          This is a safe fallback view with placeholder data. The original aggregated table had performance issues.
        </AlertDescription>
      </Alert>

      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg border">
        <div>
          <h3 className="font-semibold">
            Safe Aggregated Business Plan - {year}
          </h3>
          <div className="flex items-center gap-2 mt-1">
            <Building2 className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">
              {selectedOffices.length} offices selected
            </span>
          </div>
        </div>
        <Badge variant="secondary">
          Safe mode - placeholder data
        </Badge>
      </div>

      {/* Safe Table */}
      <div className="overflow-hidden rounded-md border border-gray-600 bg-black">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-600 hover:bg-transparent">
              <th className="h-12 px-4 text-left align-middle text-sm font-semibold text-white bg-gray-800 border-r border-gray-600 w-80">
                Category / Field
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
                  row.type === 'category' && "bg-gray-900 font-semibold"
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
                      row.type === 'office-summary' && "text-sm"
                    )}>
                      {row.name}
                    </span>
                  </div>
                </td>
                
                {/* Month cells */}
                {MONTHS.map(month => {
                  const value = row[month];
                  
                  if (row.type === 'category') {
                    return (
                      <td key={month} className="px-4 py-3 align-middle text-base font-medium text-white border-r border-gray-600 last:border-r-0">
                        <span className="text-gray-400">-</span>
                      </td>
                    );
                  }
                  
                  return (
                    <td key={month} className="px-4 py-3 align-middle text-base font-medium text-white border-r border-gray-600 last:border-r-0">
                      <div className="text-center p-1 rounded text-gray-300">
                        {value !== undefined ? value.toString() : '-'}
                      </div>
                    </td>
                  );
                })}
                
                {/* Total cell */}
                <td className="px-4 py-3 align-middle text-base font-medium text-white text-center">
                  <div className="p-1 rounded text-center text-gray-300">
                    {row.total !== undefined ? row.total.toString() : '-'}
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