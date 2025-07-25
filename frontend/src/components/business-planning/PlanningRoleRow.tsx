/**
 * Planning Role Row Component
 * 
 * Represents a row for a specific role/level combination in the planning grid
 * Contains all 12 months of data and summary calculations
 */
import React, { useCallback } from 'react';
import { Badge } from '../ui/badge';
import { cn } from '../../lib/utils';
import { PlanningCell } from './PlanningCell';
import { Users, DollarSign, TrendingUp } from 'lucide-react';
import type { StandardRole, StandardLevel, MonthlyPlanEntry } from '../../types/office';

interface CellData extends MonthlyPlanEntry {
  planId?: string;
  month: number;
  year: number;
  isDirty?: boolean;
}

interface SummaryData {
  recruitment: number;
  churn: number;
  netGrowth: number;
  revenue: number;
  cost: number;
  margin: number;
}

interface PlanningRoleRowProps {
  role: StandardRole;
  level: StandardLevel;
  year: number;
  getCellData: (role: StandardRole, level: StandardLevel, month: number) => CellData;
  getRoleSummary: () => SummaryData;
  onCellChange: (role: StandardRole, level: StandardLevel, month: number, field: keyof MonthlyPlanEntry, value: number) => void;
  selectedCell: { role: string; level: string; month: number; field: string } | null;
  onCellSelect: (selection: { role: string; level: string; month: number; field: string } | null) => void;
}

const CELL_FIELDS = [
  { key: 'recruitment' as const, label: 'Rec', type: 'number', min: 0 },
  { key: 'churn' as const, label: 'Churn', type: 'number', min: 0 },
  { key: 'price' as const, label: 'Price', type: 'currency', min: 0 },
  { key: 'utr' as const, label: 'UTR', type: 'percentage', min: 0, max: 1, step: 0.01 },
  { key: 'salary' as const, label: 'Salary', type: 'currency', min: 0 }
];

export const PlanningRoleRow: React.FC<PlanningRoleRowProps> = ({
  role,
  level,
  year,
  getCellData,
  getRoleSummary,
  onCellChange,
  selectedCell,
  onCellSelect
}) => {
  const summary = getRoleSummary();

  const getRoleColorClass = useCallback(() => {
    switch (role) {
      case 'Consultant':
        return 'bg-blue-50 border-blue-200 dark:bg-blue-950/20 dark:border-blue-800';
      case 'Sales':
        return 'bg-green-50 border-green-200 dark:bg-green-950/20 dark:border-green-800';
      case 'Operations':
        return 'bg-orange-50 border-orange-200 dark:bg-orange-950/20 dark:border-orange-800';
      default:
        return 'bg-gray-50 border-gray-200 dark:bg-gray-950/20 dark:border-gray-800';
    }
  }, [role]);

  const getLevelBadgeVariant = useCallback(() => {
    switch (level) {
      case 'A':
      case 'AC':
        return 'secondary';
      case 'C':
      case 'AM':
        return 'default';
      case 'SrC':
      case 'M':
        return 'outline';
      case 'SrM':
      case 'PiP':
        return 'destructive';
      default:
        return 'default';
    }
  }, [level]);

  const handleCellSelect = useCallback((month: number, field: keyof MonthlyPlanEntry) => {
    onCellSelect({ role, level, month, field });
  }, [role, level, onCellSelect]);

  const isSelectedRow = selectedCell?.role === role && selectedCell?.level === level;

  return (
    <>
      {CELL_FIELDS.map((field, fieldIndex) => (
        <tr 
          key={`${role}-${level}-${field.key}`}
          className={cn(
            'border-b hover:bg-muted/30 transition-colors',
            isSelectedRow && 'bg-muted/20',
            fieldIndex === 0 && getRoleColorClass()
          )}
        >
          {/* Role/Level column - only show on first field */}
          {fieldIndex === 0 && (
            <>
              <td className="p-3 border-r font-medium" rowSpan={CELL_FIELDS.length}>
                <div className="flex items-center gap-2">
                  <span className="text-sm">{role}</span>
                </div>
              </td>
              <td className="p-3 border-r" rowSpan={CELL_FIELDS.length}>
                <Badge variant={getLevelBadgeVariant()} className="text-xs">
                  {level}
                </Badge>
              </td>
            </>
          )}

          {/* Field label */}
          <td className="p-2 border-r text-xs font-medium text-muted-foreground bg-muted/30">
            {field.label}
          </td>

          {/* Monthly cells */}
          {Array.from({ length: 12 }, (_, monthIndex) => {
            const month = monthIndex + 1;
            const cellData = getCellData(role, level, month);
            const fieldValue = cellData[field.key] as number;
            
            const isSelected = selectedCell?.role === role && 
                             selectedCell?.level === level && 
                             selectedCell?.month === month && 
                             selectedCell?.field === field.key;

            return (
              <PlanningCell
                key={`${role}-${level}-${month}-${field.key}`}
                role={role}
                level={level}
                month={month}
                field={field.key}
                value={fieldValue}
                onChange={(value) => onCellChange(role, level, month, field.key, value)}
                isSelected={isSelected}
                onSelect={() => handleCellSelect(month, field.key)}
                isDirty={cellData.isDirty}
                min={field.min}
                max={field.max}
                step={field.step}
                type={field.type as 'number' | 'currency' | 'percentage'}
              />
            );
          })}

          {/* Summary cell - only show on first field */}
          {fieldIndex === 0 && (
            <td className="p-3 text-center border-l-2" rowSpan={CELL_FIELDS.length}>
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-center gap-1">
                  <Users className="h-3 w-3" />
                  <span className="font-medium">{summary.netGrowth}</span>
                </div>
                <div className="flex items-center justify-center gap-1">
                  <TrendingUp className="h-3 w-3" />
                  <span>{summary.recruitment}</span>
                  <span className="text-muted-foreground">↑</span>
                </div>
                <div className="flex items-center justify-center gap-1">
                  <span>{summary.churn}</span>
                  <span className="text-muted-foreground">↓</span>
                </div>
                <div className="flex items-center justify-center gap-1">
                  <DollarSign className="h-3 w-3" />
                  <span>{Math.round(summary.margin)}%</span>
                </div>
                <div className="text-xs text-muted-foreground">
                  €{Math.round(summary.revenue / 1000)}k
                </div>
              </div>
            </td>
          )}
        </tr>
      ))}
    </>
  );
};