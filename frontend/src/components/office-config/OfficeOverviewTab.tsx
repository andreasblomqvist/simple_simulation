/**
 * Office Overview Tab Component
 * Displays comprehensive office summary with key metrics and visualizations
 */
import React, { useEffect, useState } from 'react';
import type { OfficeConfig, OfficeBusinessPlanSummary } from '../../types/office';
import { JOURNEY_CONFIGS } from '../../types/office';
import { useBusinessPlanStore } from '../../stores/businessPlanStore';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Separator } from '../ui/separator';
import { Users, DollarSign, TrendingUp, Building2, ChevronUp, ChevronDown, BarChart3, Settings } from 'lucide-react';

interface OfficeOverviewTabProps {
  office: OfficeConfig;
}

export const OfficeOverviewTab: React.FC<OfficeOverviewTabProps> = ({ office }) => {
  const [officeSummary, setOfficeSummary] = useState<OfficeBusinessPlanSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  
  const { loadOfficeSummary } = useBusinessPlanStore();

  useEffect(() => {
    const loadData = async () => {
      if (!office?.id) return;
      
      setLoading(true);
      try {
        const summary = await loadOfficeSummary(office.id);
        setOfficeSummary(summary);
      } catch (error) {
        console.error('Failed to load office summary:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [office?.id, loadOfficeSummary]);

  const journeyConfig = JOURNEY_CONFIGS[office.journey];
  const currentWorkforce = officeSummary?.workforce_distribution;
  const totalWorkforce = currentWorkforce?.workforce.reduce((sum, entry) => sum + entry.fte, 0) || 0;
  
  // Calculate annual metrics
  const annualMetrics = officeSummary?.monthly_plans
    .filter(plan => plan.year === selectedYear)
    .reduce((acc, plan) => {
      const recruitment = plan.entries.reduce((sum, entry) => sum + entry.recruitment, 0);
      const churn = plan.entries.reduce((sum, entry) => sum + entry.churn, 0);
      const revenue = plan.entries.reduce((sum, entry) => sum + (entry.price * entry.utr * 160), 0);
      const cost = plan.entries.reduce((sum, entry) => sum + entry.salary, 0);
      
      return {
        recruitment: acc.recruitment + recruitment,
        churn: acc.churn + churn,
        revenue: acc.revenue + revenue,
        cost: acc.cost + cost,
        months: acc.months + 1
      };
    }, { recruitment: 0, churn: 0, revenue: 0, cost: 0, months: 0 }) || 
    { recruitment: 0, churn: 0, revenue: 0, cost: 0, months: 0 };

  const netGrowth = annualMetrics.recruitment - annualMetrics.churn;
  const grossMargin = annualMetrics.revenue > 0 ? ((annualMetrics.revenue - annualMetrics.cost) / annualMetrics.revenue) * 100 : 0;
  const turnoverRate = totalWorkforce > 0 ? (annualMetrics.churn / totalWorkforce) * 100 : 0;

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="large" message="Loading office overview..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Office Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <CardTitle className="text-2xl">{office.name}</CardTitle>
              <div className="flex items-center gap-3">
                <Badge variant="outline">
                  {journeyConfig.journey.charAt(0).toUpperCase() + journeyConfig.journey.slice(1)}
                </Badge>
                <span className="text-sm text-muted-foreground font-mono">{office.timezone}</span>
                <span className="text-sm text-muted-foreground">{totalWorkforce} FTE</span>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">Year:</span>
              <Select value={selectedYear.toString()} onValueChange={(value) => setSelectedYear(parseInt(value))}>
                <SelectTrigger className="w-24">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - 2 + i).map(year => (
                    <SelectItem key={year} value={year.toString()}>{year}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Workforce</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalWorkforce}</div>
            <p className="text-xs text-muted-foreground">Current FTE</p>
            <Separator className="my-3" />
            <div className="space-y-1">
              <div className="flex justify-between text-sm">
                <span>Net Growth ({selectedYear}):</span>
                <span className={`font-medium ${netGrowth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {netGrowth > 0 ? '+' : ''}{netGrowth}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Turnover Rate:</span>
                <span className="font-medium">{turnoverRate.toFixed(1)}%</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Revenue ({selectedYear})</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(annualMetrics.revenue)}</div>
            <p className="text-xs text-muted-foreground">Annual Revenue</p>
            <Separator className="my-3" />
            <div className="space-y-1">
              <div className="flex justify-between text-sm">
                <span>Monthly Average:</span>
                <span className="font-medium">
                  {formatCurrency(annualMetrics.months > 0 ? annualMetrics.revenue / annualMetrics.months : 0)}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Gross Margin:</span>
                <span className={`font-medium ${grossMargin >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {grossMargin.toFixed(1)}%
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Costs ({selectedYear})</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(annualMetrics.cost)}</div>
            <p className="text-xs text-muted-foreground">Annual Salary Cost</p>
            <Separator className="my-3" />
            <div className="space-y-1">
              <div className="flex justify-between text-sm">
                <span>Monthly Average:</span>
                <span className="font-medium">
                  {formatCurrency(annualMetrics.months > 0 ? annualMetrics.cost / annualMetrics.months : 0)}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Cost per FTE:</span>
                <span className="font-medium">
                  {formatCurrency(totalWorkforce > 0 ? annualMetrics.cost / totalWorkforce : 0)}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Hiring ({selectedYear})</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{annualMetrics.recruitment}</div>
            <p className="text-xs text-muted-foreground">Total Recruitment</p>
            <Separator className="my-3" />
            <div className="space-y-1">
              <div className="flex justify-between text-sm">
                <span>Monthly Average:</span>
                <span className="font-medium">
                  {annualMetrics.months > 0 ? (annualMetrics.recruitment / annualMetrics.months).toFixed(1) : '0'}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Churn:</span>
                <span className="font-medium">{annualMetrics.churn}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Office Journey Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            Office Journey: {journeyConfig.journey.charAt(0).toUpperCase() + journeyConfig.journey.slice(1)}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h4 className="font-semibold">Maturity Indicators</h4>
              <ul className="space-y-2">
                {journeyConfig.maturity_indicators.map((indicator, index) => (
                  <li key={index} className="flex items-center gap-2 text-sm">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    {indicator}
                  </li>
                ))}
              </ul>
            </div>
            
            <div className="space-y-4">
              <h4 className="font-semibold">Expected Performance</h4>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm">Size Range:</span>
                  <span className="text-sm font-medium">{journeyConfig.typical_size_range[0]} - {journeyConfig.typical_size_range[1]} FTE</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Monthly Recruitment Rate:</span>
                  <span className="text-sm font-medium">{journeyConfig.growth_expectations.recruitment_rate}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Monthly Churn Rate:</span>
                  <span className="text-sm font-medium">{journeyConfig.growth_expectations.churn_rate}%</span>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Office Size</span>
                  <span>{totalWorkforce} FTE</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ 
                      width: `${Math.min(100, Math.max(0, ((totalWorkforce - journeyConfig.typical_size_range[0]) / (journeyConfig.typical_size_range[1] - journeyConfig.typical_size_range[0])) * 100))}%` 
                    }}
                  ></div>
                </div>
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>{journeyConfig.typical_size_range[0]}</span>
                  <span>{journeyConfig.typical_size_range[1]}</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Economic Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Economic Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Cost of Living Multiplier</label>
              <div className="text-2xl font-bold">{office.economic_parameters?.cost_of_living?.toFixed(2) || '1.00'}x</div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Market Rate Multiplier</label>
              <div className="text-2xl font-bold">{office.economic_parameters?.market_multiplier?.toFixed(2) || '1.00'}x</div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Tax Rate</label>
              <div className="text-2xl font-bold">{office.economic_parameters?.tax_rate ? (office.economic_parameters.tax_rate * 100).toFixed(1) : '25.0'}%</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Workforce Distribution Table */}
      {currentWorkforce && (
        <Card>
          <CardHeader>
            <CardTitle>Current Workforce Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 font-medium">Role</th>
                    <th className="text-left py-2 font-medium">Level</th>
                    <th className="text-right py-2 font-medium">FTE</th>
                    <th className="text-right py-2 font-medium">Percentage</th>
                  </tr>
                </thead>
                <tbody>
                  {currentWorkforce.workforce.map((entry, index) => (
                    <tr key={index} className="border-b border-border/50">
                      <td className="py-2">{entry.role}</td>
                      <td className="py-2">{entry.level}</td>
                      <td className="py-2 text-right">{entry.fte}</td>
                      <td className="py-2 text-right">{(entry.fte / totalWorkforce * 100).toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <button className="flex items-center justify-center gap-2 p-4 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors">
              <BarChart3 className="h-4 w-4" />
              <span>View Business Plans</span>
            </button>
            <button className="flex items-center justify-center gap-2 p-4 border border-border rounded-lg hover:bg-accent transition-colors">
              <Users className="h-4 w-4" />
              <span>Edit Workforce</span>
            </button>
            <button className="flex items-center justify-center gap-2 p-4 border border-border rounded-lg hover:bg-accent transition-colors">
              <TrendingUp className="h-4 w-4" />
              <span>Configure Progression</span>
            </button>
            <button className="flex items-center justify-center gap-2 p-4 border border-border rounded-lg hover:bg-accent transition-colors">
              <Settings className="h-4 w-4" />
              <span>Office Settings</span>
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};