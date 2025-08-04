/**
 * Summary component for business plan statistics
 * Shows annual and monthly aggregated metrics
 */
import React, { useState } from 'react';
import { ChevronDown, ChevronUp, TrendingUp, TrendingDown, DollarSign, Users } from 'lucide-react';
import { WorkforceDistribution } from '../../types/office';
import { Button } from '../ui/button';
import './BusinessPlanSummary.css';

interface BusinessPlanSummaryProps {
  stats: {
    totalRecruitment: number;
    totalChurn: number;
    totalRevenue: number;
    totalSalaryCost: number;
    byMonth: Array<{
      month: number;
      recruitment: number;
      churn: number;
      revenue: number;
      cost: number;
    }>;
  };
  year: number;
  currentWorkforce?: WorkforceDistribution | null;
}

const MONTH_NAMES = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
];

export const BusinessPlanSummary: React.FC<BusinessPlanSummaryProps> = ({
  stats,
  year,
  currentWorkforce
}) => {
  const [expanded, setExpanded] = useState(false);
  const [selectedMetric, setSelectedMetric] = useState<'recruitment' | 'churn' | 'revenue' | 'cost'>('recruitment');

  const netChange = stats.totalRecruitment - stats.totalChurn;
  const grossMargin = stats.totalRevenue > 0 
    ? ((stats.totalRevenue - stats.totalSalaryCost) / stats.totalRevenue) * 100 
    : 0;
  const currentWorkforceCount = currentWorkforce?.workforce.reduce((sum, entry) => sum + entry.fte, 0) || 0;
  const projectedEndCount = currentWorkforceCount + netChange;

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercentage = (value: number): string => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(1)}%`;
  };

  const getMetricValue = (monthData: typeof stats.byMonth[0], metric: string): number => {
    switch (metric) {
      case 'recruitment': return monthData.recruitment;
      case 'churn': return monthData.churn;
      case 'revenue': return monthData.revenue;
      case 'cost': return monthData.cost;
      default: return 0;
    }
  };

  const getMetricTotal = (metric: string): number => {
    switch (metric) {
      case 'recruitment': return stats.totalRecruitment;
      case 'churn': return stats.totalChurn;
      case 'revenue': return stats.totalRevenue;
      case 'cost': return stats.totalSalaryCost;
      default: return 0;
    }
  };

  const formatMetricValue = (value: number, metric: string): string => {
    if (metric === 'revenue' || metric === 'cost') {
      return formatCurrency(value);
    }
    return value.toString();
  };

  return (
    <div className={`business-plan-summary ${expanded ? 'expanded' : ''}`}>
      {/* Summary Header */}
      <div className="summary-header">
        <Button 
          variant="ghost"
          onClick={() => setExpanded(!expanded)}
          aria-label={expanded ? 'Collapse summary' : 'Expand summary'}
          className="summary-toggle"
          icon={expanded ? <ChevronUp /> : <ChevronDown />}
          iconPosition="right"
        >
          <span className="summary-title">Business Plan Summary - {year}</span>
        </Button>
      </div>

      {/* Quick Stats */}
      <div className="quick-stats">
        <div className="stat-group workforce">
          <div className="stat-item">
            <span className="stat-label">Current Workforce</span>
            <span className="stat-value">{currentWorkforceCount}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Projected End</span>
            <span className="stat-value">{projectedEndCount}</span>
          </div>
          <div className={`stat-item net-change ${netChange >= 0 ? 'positive' : 'negative'}`}>
            <span className="stat-label">Net Change</span>
            <span className="stat-value">{netChange > 0 ? '+' : ''}{netChange}</span>
          </div>
        </div>

        <div className="stat-group financial">
          <div className="stat-item">
            <span className="stat-label">Annual Revenue</span>
            <span className="stat-value">{formatCurrency(stats.totalRevenue)}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Annual Cost</span>
            <span className="stat-value">{formatCurrency(stats.totalSalaryCost)}</span>
          </div>
          <div className={`stat-item margin ${grossMargin >= 0 ? 'positive' : 'negative'}`}>
            <span className="stat-label">Gross Margin</span>
            <span className="stat-value">{formatPercentage(grossMargin)}</span>
          </div>
        </div>

        <div className="stat-group hiring">
          <div className="stat-item">
            <span className="stat-label">Total Recruitment</span>
            <span className="stat-value">{stats.totalRecruitment}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Total Churn</span>
            <span className="stat-value">{stats.totalChurn}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Turnover Rate</span>
            <span className="stat-value">
              {currentWorkforceCount > 0 ? formatPercentage((stats.totalChurn / currentWorkforceCount) * 100) : '0%'}
            </span>
          </div>
        </div>
      </div>

      {/* Expanded Details */}
      {expanded && (
        <div className="summary-details">
          {/* Metric Selector */}
          <div className="metric-selector">
            <span className="selector-label">View by:</span>
            <div className="metric-buttons">
              {[
                { key: 'recruitment', label: 'Recruitment', icon: <TrendingUp className="h-4 w-4" /> },
                { key: 'churn', label: 'Churn', icon: <TrendingDown className="h-4 w-4" /> },
                { key: 'revenue', label: 'Revenue', icon: <DollarSign className="h-4 w-4" /> },
                { key: 'cost', label: 'Cost', icon: <DollarSign className="h-4 w-4" /> }
              ].map(metric => (
                <Button
                  key={metric.key}
                  variant={selectedMetric === metric.key ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setSelectedMetric(metric.key as any)}
                  className="metric-button"
                  icon={metric.icon}
                  iconPosition="left"
                >
                  {metric.label}
                </Button>
              ))}
            </div>
          </div>

          {/* Monthly Chart */}
          <div className="monthly-chart">
            <div className="chart-header">
              <h4 className="chart-title">Monthly {selectedMetric.charAt(0).toUpperCase() + selectedMetric.slice(1)}</h4>
              <span className="chart-total">
                Total: {formatMetricValue(getMetricTotal(selectedMetric), selectedMetric)}
              </span>
            </div>
            
            <div className="chart-bars">
              {stats.byMonth.map((monthData, index) => {
                const value = getMetricValue(monthData, selectedMetric);
                const maxValue = Math.max(...stats.byMonth.map(m => getMetricValue(m, selectedMetric)));
                const percentage = maxValue > 0 ? (value / maxValue) * 100 : 0;
                
                return (
                  <div key={index} className="chart-bar-container">
                    <div className="chart-bar-wrapper">
                      <div 
                        className={`chart-bar ${selectedMetric}`}
                        style={{ height: `${Math.max(percentage, 5)}%` }}
                        title={`${MONTH_NAMES[index]}: ${formatMetricValue(value, selectedMetric)}`}
                      />
                    </div>
                    <div className="chart-month-label">{MONTH_NAMES[index]}</div>
                    <div className="chart-month-value">
                      {formatMetricValue(value, selectedMetric)}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Summary Table */}
          <div className="summary-table">
            <div className="table-header">
              <div className="header-cell">Month</div>
              <div className="header-cell">Recruitment</div>
              <div className="header-cell">Churn</div>
              <div className="header-cell">Net</div>
              <div className="header-cell">Revenue</div>
              <div className="header-cell">Cost</div>
              <div className="header-cell">Profit</div>
            </div>
            
            <div className="table-body">
              {stats.byMonth.map((monthData, index) => {
                const net = monthData.recruitment - monthData.churn;
                const profit = monthData.revenue - monthData.cost;
                
                return (
                  <div key={index} className="table-row">
                    <div className="table-cell month">{MONTH_NAMES[index]}</div>
                    <div className="table-cell recruitment">{monthData.recruitment}</div>
                    <div className="table-cell churn">{monthData.churn}</div>
                    <div className={`table-cell net ${net >= 0 ? 'positive' : 'negative'}`}>
                      {net > 0 ? '+' : ''}{net}
                    </div>
                    <div className="table-cell revenue">{formatCurrency(monthData.revenue)}</div>
                    <div className="table-cell cost">{formatCurrency(monthData.cost)}</div>
                    <div className={`table-cell profit ${profit >= 0 ? 'positive' : 'negative'}`}>
                      {formatCurrency(profit)}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};