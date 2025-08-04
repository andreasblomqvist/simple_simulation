/**
 * Planning Calculations Panel
 * 
 * Shows detailed financial calculations and projections using PlanningService
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
import { PlanningService, type SummaryData, type CellData } from '../../services';

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
  // Use service for detailed calculations
  const detailedCalculations = useMemo(() => {
    return PlanningService.calculateDetailedPlanningMetrics(
      office,
      year,
      totalSummary,
      getCellData
    );
  }, [office, year, totalSummary, getCellData]);

  // Use service utility functions
  const formatCurrency = PlanningService.formatCurrency;
  const getPerformanceColor = PlanningService.getPerformanceColor;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6" style={{ backgroundColor: '#111827' }}>
      {/* Financial Summary */}
      <Card style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
        <CardHeader style={{ backgroundColor: '#1f2937', borderBottom: '1px solid #374151' }}>
          <CardTitle className="flex items-center gap-2 text-base" style={{ color: '#f3f4f6' }}>
            <DollarSign className="h-5 w-5" style={{ color: '#f3f4f6' }} />
            Financial Summary
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4" style={{ backgroundColor: '#1f2937' }}>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm" style={{ color: '#d1d5db' }}>Total Revenue</span>
              <span className="font-medium" style={{ color: '#f3f4f6' }}>{formatCurrency(detailedCalculations.financial.totalRevenue)}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm" style={{ color: '#d1d5db' }}>Total Costs</span>
              <span className="font-medium" style={{ color: '#f3f4f6' }}>{formatCurrency(detailedCalculations.financial.totalCosts)}</span>
            </div>
            
            <div className="flex justify-between items-center pt-2" style={{ borderTop: '1px solid #374151' }}>
              <span className="text-sm font-medium" style={{ color: '#f3f4f6' }}>Gross Profit</span>
              <span className="font-bold" style={{ 
                color: detailedCalculations.financial.grossProfit > 100000 ? '#10b981' : 
                       detailedCalculations.financial.grossProfit > 50000 ? '#f59e0b' : '#ef4444'
              }}>
                {formatCurrency(detailedCalculations.financial.grossProfit)}
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm" style={{ color: '#d1d5db' }}>Average Margin</span>
              <span 
                className="px-2 py-1 rounded text-xs font-medium"
                style={{
                  backgroundColor: detailedCalculations.financial.averageMargin > 25 ? '#1f2937' : '#374151',
                  color: '#f3f4f6',
                  border: '1px solid #374151'
                }}
              >
                {Math.round(detailedCalculations.financial.averageMargin)}%
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Workforce Summary */}
      <Card style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
        <CardHeader style={{ backgroundColor: '#1f2937', borderBottom: '1px solid #374151' }}>
          <CardTitle className="flex items-center gap-2 text-base" style={{ color: '#f3f4f6' }}>
            <Users className="h-5 w-5" style={{ color: '#f3f4f6' }} />
            Workforce Summary
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4" style={{ backgroundColor: '#1f2937' }}>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm" style={{ color: '#d1d5db' }}>Total Recruitment</span>
              <span className="font-medium" style={{ color: '#10b981' }}>{detailedCalculations.workforce.totalRecruitment}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm" style={{ color: '#d1d5db' }}>Total Churn</span>
              <span className="font-medium" style={{ color: '#ef4444' }}>{detailedCalculations.workforce.totalChurn}</span>
            </div>
            
            <div className="flex justify-between items-center pt-2" style={{ borderTop: '1px solid #374151' }}>
              <span className="text-sm font-medium" style={{ color: '#f3f4f6' }}>Net Growth</span>
              <span className="font-bold" style={{
                color: detailedCalculations.workforce.netGrowth > 10 ? '#10b981' :
                       detailedCalculations.workforce.netGrowth > 5 ? '#f59e0b' : '#ef4444'
              }}>
                {detailedCalculations.workforce.netGrowth > 0 ? '+' : ''}{detailedCalculations.workforce.netGrowth}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Role Breakdown */}
      <Card style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
        <CardHeader style={{ backgroundColor: '#1f2937', borderBottom: '1px solid #374151' }}>
          <CardTitle className="flex items-center gap-2 text-base" style={{ color: '#f3f4f6' }}>
            <PieChart className="h-5 w-5" style={{ color: '#f3f4f6' }} />
            Role Breakdown
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3" style={{ backgroundColor: '#1f2937' }}>
          {Array.from(detailedCalculations.byRole.entries()).map(([role, summary]) => (
            <div key={role} className="flex justify-between items-center">
              <span className="text-sm font-medium" style={{ color: '#f3f4f6' }}>{role}</span>
              <div className="flex items-center gap-2">
                <span 
                  className="px-2 py-1 rounded text-xs font-medium"
                  style={{
                    backgroundColor: '#374151',
                    color: '#f3f4f6',
                    border: '1px solid #4b5563'
                  }}
                >
                  {summary.netGrowth > 0 ? '+' : ''}{summary.netGrowth}
                </span>
                <span className="text-xs" style={{ color: '#9ca3af' }}>
                  {Math.round(summary.margin)}%
                </span>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Monthly Trend */}
      <Card className="lg:col-span-3" style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
        <CardHeader style={{ backgroundColor: '#1f2937', borderBottom: '1px solid #374151' }}>
          <CardTitle className="flex items-center gap-2 text-base" style={{ color: '#f3f4f6' }}>
            <BarChart3 className="h-5 w-5" style={{ color: '#f3f4f6' }} />
            Monthly Trends
          </CardTitle>
        </CardHeader>
        <CardContent style={{ backgroundColor: '#1f2937' }}>
          <div className="grid grid-cols-12 gap-2">
            {detailedCalculations.byMonth.map((month, index) => (
              <div key={month.month} className="text-center">
                <div className="text-xs font-medium mb-2" style={{ color: '#f3f4f6' }}>
                  {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][index]}
                </div>
                
                <div className="space-y-1">
                  <div className="text-xs font-medium" style={{
                    color: month.netGrowth > 2 ? '#10b981' :
                           month.netGrowth > 0 ? '#f59e0b' : '#ef4444'
                  }}>
                    {month.netGrowth > 0 ? '+' : ''}{month.netGrowth}
                  </div>
                  
                  <div className="text-xs" style={{ color: '#9ca3af' }}>
                    {Math.round(month.margin)}%
                  </div>
                  
                  <div className="text-xs" style={{ color: '#9ca3af' }}>
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