/**
 * SnapshotComparison Component
 * Side-by-side comparison view for population snapshots
 */

import React, { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { DataTableMinimal, MinimalColumnDef } from '../ui/data-table-minimal';
import { 
  X, 
  TrendingUp, 
  TrendingDown, 
  Calendar, 
  Users, 
  DollarSign,
  Plus,
  Minus,
  Equal,
  ArrowRight
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { snapshotUtils } from '../../services/snapshotApi';
import type { SnapshotComparisonProps, WorkforceChange } from '../../types/snapshots';

export const SnapshotComparison: React.FC<SnapshotComparisonProps> = ({
  baseline,
  comparison,
  onClose
}) => {
  const comparisonData = useMemo(() => {
    // Create workforce change analysis
    const baselineWorkforce = new Map<string, { fte: number; salary: number }>();
    const comparisonWorkforce = new Map<string, { fte: number; salary: number }>();

    // Build baseline map
    baseline.workforce.forEach(item => {
      const key = `${item.role}${item.level ? `-${item.level}` : ''}`;
      baselineWorkforce.set(key, { fte: item.fte, salary: item.salary });
    });

    // Build comparison map
    comparison.workforce.forEach(item => {
      const key = `${item.role}${item.level ? `-${item.level}` : ''}`;
      comparisonWorkforce.set(key, { fte: item.fte, salary: item.salary });
    });

    // Calculate changes
    const changes: WorkforceChange[] = [];
    const allKeys = new Set([...baselineWorkforce.keys(), ...comparisonWorkforce.keys()]);

    allKeys.forEach(key => {
      const [role, level] = key.split('-');
      const baselineData = baselineWorkforce.get(key) || { fte: 0, salary: 0 };
      const comparisonData = comparisonWorkforce.get(key) || { fte: 0, salary: 0 };

      const fteChange = comparisonData.fte - baselineData.fte;
      const salaryChange = (comparisonData.fte * comparisonData.salary) - (baselineData.fte * baselineData.salary);

      let changeType: 'added' | 'removed' | 'modified' = 'modified';
      if (baselineData.fte === 0) changeType = 'added';
      else if (comparisonData.fte === 0) changeType = 'removed';

      if (fteChange !== 0 || changeType !== 'modified') {
        changes.push({
          role,
          level: level || null,
          change_type: changeType,
          baseline_fte: baselineData.fte,
          comparison_fte: comparisonData.fte,
          fte_change: fteChange,
          salary_change: salaryChange
        });
      }
    });

    // Calculate summary
    const totalFTEChange = comparison.metadata.total_fte - baseline.metadata.total_fte;
    const totalSalaryChange = comparison.metadata.total_salary_cost - baseline.metadata.total_salary_cost;
    const rolesAdded = changes.filter(c => c.change_type === 'added').length;
    const rolesRemoved = changes.filter(c => c.change_type === 'removed').length;
    const rolesModified = changes.filter(c => c.change_type === 'modified').length;
    const netChangePercentage = baseline.metadata.total_fte > 0 
      ? (totalFTEChange / baseline.metadata.total_fte) * 100 
      : 0;

    return {
      changes: changes.sort((a, b) => Math.abs(b.fte_change) - Math.abs(a.fte_change)),
      summary: {
        total_fte_change: totalFTEChange,
        total_salary_change: totalSalaryChange,
        roles_added: rolesAdded,
        roles_removed: rolesRemoved,
        roles_modified: rolesModified,
        net_change_percentage: netChangePercentage
      }
    };
  }, [baseline, comparison]);

  const changeColumns: MinimalColumnDef<WorkforceChange>[] = useMemo(() => [
    {
      accessorKey: "role",
      header: "Role",
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <span className="font-medium" style={{ color: '#f3f4f6' }}>
            {row.original.role}
          </span>
          {row.original.level && (
            <Badge variant="outline" className="text-xs bg-blue-900 text-blue-100 border-blue-700">
              {row.original.level}
            </Badge>
          )}
        </div>
      )
    },
    {
      accessorKey: "change_type",
      header: "Change",
      cell: ({ row }) => {
        const { change_type } = row.original;
        const icons = {
          added: <Plus className="h-4 w-4" />,
          removed: <Minus className="h-4 w-4" />,
          modified: <Equal className="h-4 w-4" />
        };
        const colors = {
          added: '#10b981',
          removed: '#ef4444',
          modified: '#f59e0b'
        };
        
        return (
          <div className="flex items-center gap-2">
            <div style={{ color: colors[change_type] }}>
              {icons[change_type]}
            </div>
            <span className="text-xs capitalize" style={{ color: colors[change_type] }}>
              {change_type}
            </span>
          </div>
        );
      }
    },
    {
      accessorKey: "baseline_fte",
      header: "Baseline FTE",
      cell: ({ row }) => (
        <div className="font-mono text-sm" style={{ color: '#9ca3af' }}>
          {snapshotUtils.formatFTE(row.original.baseline_fte)}
        </div>
      )
    },
    {
      accessorKey: "comparison_fte",
      header: "Comparison FTE",
      cell: ({ row }) => (
        <div className="font-mono text-sm" style={{ color: '#f3f4f6' }}>
          {snapshotUtils.formatFTE(row.original.comparison_fte)}
        </div>
      )
    },
    {
      accessorKey: "fte_change",
      header: "FTE Change",
      cell: ({ row }) => {
        const change = row.original.fte_change;
        return (
          <div className={cn(
            "flex items-center gap-1 font-mono text-sm font-medium",
            change > 0 ? 'text-green-400' : change < 0 ? 'text-red-400' : 'text-gray-400'
          )}>
            {change > 0 && <TrendingUp className="h-3 w-3" />}
            {change < 0 && <TrendingDown className="h-3 w-3" />}
            {snapshotUtils.formatChange(change)}
          </div>
        );
      }
    },
    {
      accessorKey: "salary_change",
      header: "Salary Impact",
      cell: ({ row }) => {
        const change = row.original.salary_change;
        return (
          <div className={cn(
            "flex items-center gap-1 font-mono text-sm",
            change > 0 ? 'text-green-400' : change < 0 ? 'text-red-400' : 'text-gray-400'
          )}>
            {change > 0 && <TrendingUp className="h-3 w-3" />}
            {change < 0 && <TrendingDown className="h-3 w-3" />}
            {snapshotUtils.formatSalary(Math.abs(change))}
          </div>
        );
      }
    }
  ], []);

  return (
    <div className="space-y-6" style={{ backgroundColor: '#111827', padding: '1rem' }}>
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-3" style={{ color: '#f3f4f6' }}>
            <ArrowRight className="h-6 w-6" style={{ color: '#3b82f6' }} />
            Snapshot Comparison
          </h2>
          <p className="text-sm mt-1" style={{ color: '#d1d5db' }}>
            Comparing workforce changes between snapshots
          </p>
        </div>
        {onClose && (
          <Button variant="ghost" size="sm" onClick={onClose} className="hover:bg-gray-700">
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Snapshot Headers */}
      <div className="grid grid-cols-2 gap-6">
        {/* Baseline Snapshot */}
        <Card className="border-0 shadow-md" style={{ backgroundColor: '#1f2937' }}>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Calendar className="h-5 w-5" style={{ color: '#6b7280' }} />
              Baseline: {baseline.name}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center gap-2 text-sm" style={{ color: '#9ca3af' }}>
              <Calendar className="h-4 w-4" />
              {snapshotUtils.formatDate(baseline.snapshot_date)}
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="text-center p-2 rounded" style={{ backgroundColor: '#111827' }}>
                <div className="text-lg font-bold" style={{ color: '#f3f4f6' }}>
                  {snapshotUtils.formatFTE(baseline.metadata.total_fte)}
                </div>
                <div className="text-xs" style={{ color: '#9ca3af' }}>FTE</div>
              </div>
              <div className="text-center p-2 rounded" style={{ backgroundColor: '#111827' }}>
                <div className="text-lg font-bold" style={{ color: '#f3f4f6' }}>
                  {snapshotUtils.formatSalary(baseline.metadata.total_salary_cost)}
                </div>
                <div className="text-xs" style={{ color: '#9ca3af' }}>Cost</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Comparison Snapshot */}
        <Card className="border-0 shadow-md" style={{ backgroundColor: '#1f2937' }}>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Calendar className="h-5 w-5" style={{ color: '#3b82f6' }} />
              Comparison: {comparison.name}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center gap-2 text-sm" style={{ color: '#9ca3af' }}>
              <Calendar className="h-4 w-4" />
              {snapshotUtils.formatDate(comparison.snapshot_date)}
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="text-center p-2 rounded" style={{ backgroundColor: '#111827' }}>
                <div className="text-lg font-bold" style={{ color: '#f3f4f6' }}>
                  {snapshotUtils.formatFTE(comparison.metadata.total_fte)}
                </div>
                <div className="text-xs" style={{ color: '#9ca3af' }}>FTE</div>
              </div>
              <div className="text-center p-2 rounded" style={{ backgroundColor: '#111827' }}>
                <div className="text-lg font-bold" style={{ color: '#f3f4f6' }}>
                  {snapshotUtils.formatSalary(comparison.metadata.total_salary_cost)}
                </div>
                <div className="text-xs" style={{ color: '#9ca3af' }}>Cost</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Summary Metrics */}
      <Card className="border-0 shadow-md" style={{ backgroundColor: '#1f2937' }}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" style={{ color: '#10b981' }} />
            Change Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 rounded" style={{ backgroundColor: '#111827' }}>
              <div className={cn(
                "text-2xl font-bold flex items-center justify-center gap-1",
                comparisonData.summary.total_fte_change > 0 ? 'text-green-400' : 
                comparisonData.summary.total_fte_change < 0 ? 'text-red-400' : 'text-gray-400'
              )}>
                {comparisonData.summary.total_fte_change > 0 && <TrendingUp className="h-5 w-5" />}
                {comparisonData.summary.total_fte_change < 0 && <TrendingDown className="h-5 w-5" />}
                {snapshotUtils.formatChange(comparisonData.summary.total_fte_change)}
              </div>
              <div className="text-xs mt-1" style={{ color: '#9ca3af' }}>FTE Change</div>
              <div className="text-xs" style={{ color: '#6b7280' }}>
                ({snapshotUtils.formatChange(comparisonData.summary.net_change_percentage, true)})
              </div>
            </div>

            <div className="text-center p-3 rounded" style={{ backgroundColor: '#111827' }}>
              <div className={cn(
                "text-2xl font-bold flex items-center justify-center gap-1",
                comparisonData.summary.total_salary_change > 0 ? 'text-green-400' : 
                comparisonData.summary.total_salary_change < 0 ? 'text-red-400' : 'text-gray-400'
              )}>
                {comparisonData.summary.total_salary_change > 0 && <TrendingUp className="h-5 w-5" />}
                {comparisonData.summary.total_salary_change < 0 && <TrendingDown className="h-5 w-5" />}
                {snapshotUtils.formatSalary(Math.abs(comparisonData.summary.total_salary_change))}
              </div>
              <div className="text-xs mt-1" style={{ color: '#9ca3af' }}>Salary Impact</div>
            </div>

            <div className="text-center p-3 rounded" style={{ backgroundColor: '#111827' }}>
              <div className="text-2xl font-bold" style={{ color: '#10b981' }}>
                {comparisonData.summary.roles_added}
              </div>
              <div className="text-xs mt-1" style={{ color: '#9ca3af' }}>Roles Added</div>
            </div>

            <div className="text-center p-3 rounded" style={{ backgroundColor: '#111827' }}>
              <div className="text-2xl font-bold" style={{ color: '#ef4444' }}>
                {comparisonData.summary.roles_removed}
              </div>
              <div className="text-xs mt-1" style={{ color: '#9ca3af' }}>Roles Removed</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Detailed Changes Table */}
      {comparisonData.changes.length > 0 && (
        <Card className="border-0 shadow-md" style={{ backgroundColor: '#1f2937' }}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" style={{ color: '#3b82f6' }} />
              Detailed Changes ({comparisonData.changes.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <DataTableMinimal
              columns={changeColumns}
              data={comparisonData.changes}
              enablePagination={true}
              pageSize={10}
              className="detailed-changes-table"
            />
          </CardContent>
        </Card>
      )}

      {comparisonData.changes.length === 0 && (
        <Card className="border-0 shadow-md" style={{ backgroundColor: '#1f2937' }}>
          <CardContent className="text-center py-8">
            <Equal className="h-12 w-12 mx-auto mb-4" style={{ color: '#9ca3af' }} />
            <h3 className="text-lg font-medium mb-2" style={{ color: '#f3f4f6' }}>
              No Changes Detected
            </h3>
            <p style={{ color: '#9ca3af' }}>
              The workforce composition is identical between these two snapshots.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default SnapshotComparison;