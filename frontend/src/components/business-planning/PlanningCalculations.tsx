/**
 * Planning Calculations Panel
 * 
 * Shows detailed financial calculations and projections
 */
import React, { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { 
  DollarSign, 
  TrendingUp, 
  Users, 
  Calculator,
  PieChart,
  BarChart3
} from 'lucide-react';
import type { OfficeConfig, StandardRole, StandardLevel } from '../../types/office';

interface SummaryData {
  recruitment: number;
  churn: number;
  netGrowth: number;
  revenue: number;
  cost: number;
  margin: number;
}

interface CellData {
  role: StandardRole;
  level: StandardLevel;
  month: number;
  year: number;
  recruitment: number;
  churn: number;
  price: number;
  utr: number;
  salary: number;
}

interface PlanningCalculationsProps {
  office: OfficeConfig;
  year: number;
  totalSummary: SummaryData;
  getCellData: (role: StandardRole, level: StandardLevel, month: number) => CellData;
}

export const PlanningCalculations: React.FC<PlanningCalculationsProps> = ({
  office,
  year,
  totalSummary,
  getCellData
}) => {
  const detailedCalculations = useMemo(() => {
    const calculations = {
      byRole: new Map<StandardRole, SummaryData>(),
      byMonth: Array.from({ length: 12 }, (_, i) => ({
        month: i + 1,
        recruitment: 0,
        churn: 0,
        netGrowth: 0,
        revenue: 0,
        cost: 0,
        margin: 0
      })),
      financial: {
        totalRevenue: 0,
        totalCosts: 0,
        grossProfit: 0,
        averageMargin: 0,
        averageUTR: 0,
        averageRate: 0
      },
      workforce: {
        totalRecruitment: 0,
        totalChurn: 0,
        netGrowth: 0,
        growthRate: 0,
        churnRate: 0
      }
    };

    // Calculate by role and month - using the actual types from office.ts
    const roles: StandardRole[] = ['Consultant', 'Sales', 'Operations'];
    const levels: StandardLevel[] = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP'];

    roles.forEach(role => {
      const roleSummary: SummaryData = {
        recruitment: 0,
        churn: 0,
        netGrowth: 0,
        revenue: 0,
        cost: 0,
        margin: 0
      };

      levels.forEach(level => {
        for (let month = 1; month <= 12; month++) {
          const cellData = getCellData(role, level, month);
          const monthRevenue = cellData.price * cellData.utr * 160; // 160 hours/month
          
          roleSummary.recruitment += cellData.recruitment;
          roleSummary.churn += cellData.churn;
          roleSummary.revenue += monthRevenue;
          roleSummary.cost += cellData.salary;

          // Add to monthly totals
          const monthCalc = calculations.byMonth[month - 1];
          monthCalc.recruitment += cellData.recruitment;
          monthCalc.churn += cellData.churn;
          monthCalc.revenue += monthRevenue;
          monthCalc.cost += cellData.salary;
        }
      });

      roleSummary.netGrowth = roleSummary.recruitment - roleSummary.churn;
      roleSummary.margin = roleSummary.revenue > 0 ? 
        ((roleSummary.revenue - roleSummary.cost) / roleSummary.revenue) * 100 : 0;

      calculations.byRole.set(role, roleSummary);
    });

    // Calculate monthly margins and net growth
    calculations.byMonth.forEach(month => {
      month.netGrowth = month.recruitment - month.churn;
      month.margin = month.revenue > 0 ? 
        ((month.revenue - month.cost) / month.revenue) * 100 : 0;
    });

    // Calculate financial totals
    calculations.financial.totalRevenue = totalSummary.revenue;
    calculations.financial.totalCosts = totalSummary.cost;
    calculations.financial.grossProfit = totalSummary.revenue - totalSummary.cost;
    calculations.financial.averageMargin = totalSummary.margin;

    // Calculate workforce totals
    calculations.workforce.totalRecruitment = totalSummary.recruitment;
    calculations.workforce.totalChurn = totalSummary.churn;
    calculations.workforce.netGrowth = totalSummary.netGrowth;

    return calculations;
  }, [totalSummary, getCellData]);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const getPerformanceColor = (value: number, thresholds: { good: number; warning: number }) => {
    if (value >= thresholds.good) return 'text-green-600 dark:text-green-400';
    if (value >= thresholds.warning) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Financial Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <DollarSign className="h-5 w-5" />
            Financial Summary
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Total Revenue</span>
              <span className="font-medium">{formatCurrency(detailedCalculations.financial.totalRevenue)}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Total Costs</span>
              <span className="font-medium">{formatCurrency(detailedCalculations.financial.totalCosts)}</span>
            </div>
            
            <div className="flex justify-between items-center border-t pt-2">
              <span className="text-sm font-medium">Gross Profit</span>
              <span className={`font-bold ${getPerformanceColor(detailedCalculations.financial.grossProfit, { good: 100000, warning: 50000 })}`}>
                {formatCurrency(detailedCalculations.financial.grossProfit)}
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Average Margin</span>
              <Badge variant={detailedCalculations.financial.averageMargin > 25 ? 'default' : 'secondary'}>
                {Math.round(detailedCalculations.financial.averageMargin)}%
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Workforce Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Users className="h-5 w-5" />
            Workforce Summary
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Total Recruitment</span>
              <span className="font-medium text-green-600">{detailedCalculations.workforce.totalRecruitment}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Total Churn</span>
              <span className="font-medium text-red-600">{detailedCalculations.workforce.totalChurn}</span>
            </div>
            
            <div className="flex justify-between items-center border-t pt-2">
              <span className="text-sm font-medium">Net Growth</span>
              <span className={`font-bold ${getPerformanceColor(detailedCalculations.workforce.netGrowth, { good: 10, warning: 5 })}`}>
                {detailedCalculations.workforce.netGrowth > 0 ? '+' : ''}{detailedCalculations.workforce.netGrowth}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Role Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <PieChart className="h-5 w-5" />
            Role Breakdown
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {Array.from(detailedCalculations.byRole.entries()).map(([role, summary]) => (
            <div key={role} className="flex justify-between items-center">
              <span className="text-sm font-medium">{role}</span>
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-xs">
                  {summary.netGrowth > 0 ? '+' : ''}{summary.netGrowth}
                </Badge>
                <span className="text-xs text-muted-foreground">
                  {Math.round(summary.margin)}%
                </span>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Monthly Trend */}
      <Card className="lg:col-span-3">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <BarChart3 className="h-5 w-5" />
            Monthly Trends
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-12 gap-2">
            {detailedCalculations.byMonth.map((month, index) => (
              <div key={month.month} className="text-center">
                <div className="text-xs font-medium mb-2">
                  {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][index]}
                </div>
                
                <div className="space-y-1">
                  <div className={`text-xs font-medium ${getPerformanceColor(month.netGrowth, { good: 2, warning: 0 })}`}>
                    {month.netGrowth > 0 ? '+' : ''}{month.netGrowth}
                  </div>
                  
                  <div className="text-xs text-muted-foreground">
                    {Math.round(month.margin)}%
                  </div>
                  
                  <div className="text-xs text-muted-foreground">
                    €{Math.round(month.revenue / 1000)}k
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};