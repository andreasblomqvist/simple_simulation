/**
 * Planning Monthly Summary
 * 
 * Summary statistics for a single month in the planning grid
 */
import React from 'react';
import { Badge } from '../ui/badge';
import { Users, DollarSign, TrendingUp, TrendingDown } from 'lucide-react';
import { cn } from '../../lib/utils';

interface SummaryData {
  recruitment: number;
  churn: number;
  netGrowth: number;
  revenue: number;
  cost: number;
  margin: number;
}

interface PlanningMonthlySummaryProps {
  month: number;
  summary: SummaryData;
}

export const PlanningMonthlySummary: React.FC<PlanningMonthlySummaryProps> = ({
  month,
  summary
}) => {
  const getGrowthColorClass = () => {
    if (summary.netGrowth > 0) return 'text-green-600 dark:text-green-400';
    if (summary.netGrowth < 0) return 'text-red-600 dark:text-red-400';
    return 'text-muted-foreground';
  };

  const getMarginColorClass = () => {
    if (summary.margin > 30) return 'text-green-600 dark:text-green-400';
    if (summary.margin > 20) return 'text-yellow-600 dark:text-yellow-400';
    if (summary.margin > 0) return 'text-orange-600 dark:text-orange-400';
    return 'text-red-600 dark:text-red-400';
  };

  return (
    <td className="p-2 text-center border-r bg-muted/20">
      <div className="space-y-1 text-xs">
        {/* Net Growth */}
        <div className={cn("flex items-center justify-center gap-1 font-medium", getGrowthColorClass())}>
          {summary.netGrowth > 0 ? (
            <TrendingUp className="h-3 w-3" />
          ) : summary.netGrowth < 0 ? (
            <TrendingDown className="h-3 w-3" />
          ) : (
            <Users className="h-3 w-3" />
          )}
          <span>{summary.netGrowth}</span>
        </div>

        {/* Recruitment/Churn */}
        <div className="flex items-center justify-center gap-1 text-muted-foreground">
          <span>{summary.recruitment}</span>
          <span>↑</span>
          <span>{summary.churn}</span>
          <span>↓</span>
        </div>

        {/* Margin */}
        <div className={cn("flex items-center justify-center gap-1", getMarginColorClass())}>
          <DollarSign className="h-3 w-3" />
          <span>{Math.round(summary.margin)}%</span>
        </div>

        {/* Revenue (in thousands) */}
        <div className="text-muted-foreground">
          €{Math.round(summary.revenue / 1000)}k
        </div>
      </div>
    </td>
  );
};