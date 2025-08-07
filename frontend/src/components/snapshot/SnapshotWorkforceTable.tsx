/**
 * SnapshotWorkforceTable Component
 * Table displaying snapshot workforce data with role/level breakdown
 */

import React, { useMemo } from 'react';
import { DataTableMinimal, MinimalColumnDef } from '../ui/data-table-minimal';
import { Badge } from '../ui/badge';
import { cn } from '../../lib/utils';
import { snapshotUtils } from '../../services/snapshotApi';
import type { SnapshotWorkforceTableProps, SnapshotWorkforce } from '../../types/snapshots';

export const SnapshotWorkforceTable: React.FC<SnapshotWorkforceTableProps> = ({
  workforce,
  showSalary = true,
  showNotes = false,
  className
}) => {
  const { tableData, totals } = useMemo(() => {
    // Group workforce by role and calculate totals
    const roleGroups: Record<string, SnapshotWorkforce[]> = {};
    let totalFTE = 0;
    let totalSalaryCost = 0;

    workforce.forEach(item => {
      if (!roleGroups[item.role]) {
        roleGroups[item.role] = [];
      }
      roleGroups[item.role].push(item);
      totalFTE += item.fte;
      totalSalaryCost += item.fte * item.salary;
    });

    // Convert to table format
    const tableData = Object.entries(roleGroups).map(([role, items]) => {
      const roleTotalFTE = items.reduce((sum, item) => sum + item.fte, 0);
      const roleTotalSalaryCost = items.reduce((sum, item) => sum + (item.fte * item.salary), 0);
      
      return {
        role,
        items: items.sort((a, b) => {
          // Sort levels in career progression order
          const levelOrder = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P'];
          const aIndex = a.level ? levelOrder.indexOf(a.level) : -1;
          const bIndex = b.level ? levelOrder.indexOf(b.level) : -1;
          return aIndex - bIndex;
        }),
        totalFTE: roleTotalFTE,
        totalSalaryCost: roleTotalSalaryCost
      };
    }).sort((a, b) => a.role.localeCompare(b.role));

    return {
      tableData,
      totals: {
        totalFTE,
        totalSalaryCost
      }
    };
  }, [workforce]);

  const columns: MinimalColumnDef<any>[] = useMemo(() => [
    {
      accessorKey: "role",
      header: "Role",
      cell: ({ row }) => (
        <div className="font-medium" style={{ color: '#f3f4f6' }}>
          {row.original.role}
        </div>
      )
    },
    {
      accessorKey: "level",
      header: "Level",
      cell: ({ row }) => (
        <div className="space-y-1">
          {row.original.items.map((item: SnapshotWorkforce, index: number) => (
            <div key={index} className="flex items-center gap-2">
              {item.level ? (
                <Badge 
                  variant="outline" 
                  className="text-xs bg-blue-900 text-blue-100 border-blue-700"
                >
                  {item.level}
                </Badge>
              ) : (
                <span className="text-xs px-2 py-1 rounded bg-gray-700 text-gray-300">
                  N/A
                </span>
              )}
            </div>
          ))}
        </div>
      )
    },
    {
      accessorKey: "fte",
      header: "FTE",
      cell: ({ row }) => (
        <div className="space-y-1">
          {row.original.items.map((item: SnapshotWorkforce, index: number) => (
            <div key={index} className="font-mono text-sm" style={{ color: '#f3f4f6' }}>
              {snapshotUtils.formatFTE(item.fte)}
            </div>
          ))}
          <div className="pt-1 mt-1 border-t border-gray-600">
            <div className="font-mono text-sm font-bold" style={{ color: '#10b981' }}>
              {snapshotUtils.formatFTE(row.original.totalFTE)}
            </div>
          </div>
        </div>
      )
    },
    ...(showSalary ? [{
      accessorKey: "salary",
      header: "Monthly Salary",
      cell: ({ row }: { row: any }) => (
        <div className="space-y-1">
          {row.original.items.map((item: SnapshotWorkforce, index: number) => (
            <div key={index} className="font-mono text-sm" style={{ color: '#f3f4f6' }}>
              {snapshotUtils.formatSalary(item.salary)}
            </div>
          ))}
          <div className="pt-1 mt-1 border-t border-gray-600">
            <div className="font-mono text-sm font-bold" style={{ color: '#10b981' }}>
              {snapshotUtils.formatSalary(row.original.totalSalaryCost)}
            </div>
          </div>
        </div>
      )
    }] : []),
    ...(showNotes ? [{
      accessorKey: "notes",
      header: "Notes",
      cell: ({ row }: { row: any }) => (
        <div className="space-y-1">
          {row.original.items.map((item: SnapshotWorkforce, index: number) => (
            <div key={index} className="text-sm" style={{ color: '#9ca3af' }}>
              {item.notes ? (
                <span className="italic">{item.notes}</span>
              ) : (
                <span>—</span>
              )}
            </div>
          ))}
        </div>
      )
    }] : [])
  ], [showSalary, showNotes]);

  if (workforce.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="text-gray-400 text-sm">No workforce data available</div>
      </div>
    );
  }

  return (
    <div className={cn("space-y-4", className)}>
      {/* Summary Cards */}
      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 rounded-lg" style={{ backgroundColor: '#111827' }}>
          <div className="text-sm font-medium mb-1" style={{ color: '#9ca3af' }}>
            Total FTE
          </div>
          <div className="text-2xl font-bold" style={{ color: '#10b981' }}>
            {snapshotUtils.formatFTE(totals.totalFTE)}
          </div>
        </div>
        
        {showSalary && (
          <div className="p-4 rounded-lg" style={{ backgroundColor: '#111827' }}>
            <div className="text-sm font-medium mb-1" style={{ color: '#9ca3af' }}>
              Total Monthly Cost
            </div>
            <div className="text-2xl font-bold" style={{ color: '#10b981' }}>
              {snapshotUtils.formatSalary(totals.totalSalaryCost)}
            </div>
          </div>
        )}
      </div>

      {/* Workforce Table */}
      <div className="rounded-lg border border-gray-600 overflow-hidden">
        <DataTableMinimal
          columns={columns}
          data={tableData}
          enablePagination={false}
          className="bg-gray-800"
        />
      </div>

      {/* Role Distribution Summary */}
      <div className="p-4 rounded-lg" style={{ backgroundColor: '#111827' }}>
        <h4 className="text-sm font-medium mb-3" style={{ color: '#f3f4f6' }}>
          Role Distribution
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {tableData.map(({ role, totalFTE }) => (
            <div key={role} className="flex items-center justify-between p-2 rounded bg-gray-800">
              <span className="text-xs font-medium" style={{ color: '#d1d5db' }}>
                {role}
              </span>
              <Badge 
                variant="secondary" 
                className="text-xs bg-blue-900 text-blue-100"
              >
                {snapshotUtils.formatFTE(totalFTE)}
              </Badge>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SnapshotWorkforceTable;