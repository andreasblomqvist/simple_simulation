import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Progress } from '../ui/progress';
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  PieChart, 
  Pie, 
  Cell, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  DollarSign, 
  Target,
  Building2,
  UserPlus,
  Activity
} from 'lucide-react';
import type { ScenarioResponse } from '../../types/unified-data-structures';
import { ResultsService, type ProcessedYearData, type ResultsWorkforceMetrics } from '../../services';
import { PyramidChart, type PyramidStage } from '../v2/PyramidChart';
import { QuarterlyWorkforceChart } from '../v2/QuarterlyWorkforceChart';

interface ModernResultsDisplayProps {
  result: ScenarioResponse;
}

// Use types from ResultsService
type YearData = ProcessedYearData;

const ModernResultsDisplay: React.FC<ModernResultsDisplayProps> = ({ result }) => {
  const [selectedYear, setSelectedYear] = useState<string>('');

  // Process simulation results using service
  const yearsData = useMemo((): YearData[] => {
    if (!result?.results) return [];
    return ResultsService.processYearData(result.results);
  }, [result]);

  // Set initial selected year
  React.useEffect(() => {
    if (yearsData.length > 0 && !selectedYear) {
      setSelectedYear(yearsData[0].year);
    }
  }, [yearsData, selectedYear]);


  const currentYearData = yearsData.find(y => y.year === selectedYear);

  // Use service formatting functions (static methods)
  const formatNumber = ResultsService.formatNumber;
  const formatCurrency = ResultsService.formatCurrency;
  const formatPercent = ResultsService.formatPercent;
  const calculateGrowth = ResultsService.calculateGrowth;

  // Generate chart data using service
  const fteGrowthData = useMemo(() => {
    if (!currentYearData) return [];
    return ResultsService.generateFTEGrowthData(currentYearData);
  }, [currentYearData]);

  const seniorityData = useMemo(() => {
    if (!currentYearData) return [];
    return ResultsService.generateSeniorityData(currentYearData);
  }, [currentYearData]);

  const recruitmentChurnData = useMemo(() => {
    if (!currentYearData) return [];
    return ResultsService.generateRecruitmentChurnData(currentYearData);
  }, [currentYearData]);

  const quarterlyWorkforceData = useMemo(() => {
    if (!currentYearData) return [];
    return ResultsService.generateQuarterlyWorkforceData(currentYearData);
  }, [currentYearData]);


  // Financial Panel
  const renderFinancialPanel = (yearData?: YearData) => {
    const targetYear = yearData || currentYearData;
    if (!targetYear?.kpis?.financial) return null;
    
    
    const financial = targetYear.kpis.financial;
    const previousYear = yearsData.find(y => parseInt(y.year) === parseInt(targetYear.year) - 1);
    const previousFinancial = previousYear?.kpis?.financial;
    
    const financialCards = [
      {
        title: 'Net Sales',
        value: formatCurrency(financial.net_sales),
        rawValue: financial.net_sales,
        previousValue: previousFinancial?.net_sales,
        icon: DollarSign,
        description: 'Total revenue generated'
      },
      {
        title: 'EBITDA',
        value: formatCurrency(financial.ebitda),
        rawValue: financial.ebitda,
        previousValue: previousFinancial?.ebitda,
        icon: TrendingUp,
        description: 'Earnings before interest, taxes, depreciation'
      },
      {
        title: 'EBITDA Margin',
        value: formatPercent(financial.margin),
        rawValue: financial.margin * 100,
        previousValue: previousFinancial?.margin ? previousFinancial.margin * 100 : undefined,
        icon: Target,
        description: 'Profitability percentage'
      },
      {
        title: 'Avg Hourly Rate',
        value: `${formatNumber(financial.avg_hourly_rate)} SEK/h`,
        rawValue: financial.avg_hourly_rate,
        previousValue: previousFinancial?.avg_hourly_rate,
        icon: DollarSign,
        description: 'Average billing rate per hour'
      }
    ];
    
    return (
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <DollarSign className="h-5 w-5" />
            <span>Financial Performance</span>
          </CardTitle>
          <CardDescription>Revenue, profitability, and financial metrics</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {financialCards.map((kpi, index) => {
              const growth = kpi.previousValue ? calculateGrowth(kpi.rawValue, kpi.previousValue) : null;
              const Icon = kpi.icon;
              
              return (
                <Card key={index}>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">{kpi.title}</CardTitle>
                    <Icon className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{kpi.value}</div>
                    {growth !== null && (
                      <div className="flex items-center space-x-1 text-xs mt-1">
                        {growth >= 0 ? (
                          <TrendingUp className="h-3 w-3 text-green-500" />
                        ) : (
                          <TrendingDown className="h-3 w-3 text-red-500" />
                        )}
                        <span className={growth >= 0 ? 'text-green-600' : 'text-red-600'}>
                          {Math.abs(growth).toFixed(1)}% vs previous year
                        </span>
                      </div>
                    )}
                    <p className="text-xs text-muted-foreground mt-1">
                      {kpi.description}
                    </p>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </CardContent>
      </Card>
    );
  };

  // Growth Panel
  const renderGrowthPanel = (yearData?: YearData) => {
    const targetYear = yearData || currentYearData;
    if (!targetYear?.kpis) return null;
    
    const { growth, financial } = targetYear.kpis;
    const previousYear = yearsData.find(y => parseInt(y.year) === parseInt(targetYear.year) - 1);
    const previousKpis = previousYear?.kpis;
    
    const growthCards = [
      {
        title: 'FTE Growth Rate',
        value: growth?.total_growth_percent ? `${growth.total_growth_percent.toFixed(1)}%` : 'N/A',
        rawValue: growth?.total_growth_percent || 0,
        previousValue: previousKpis?.growth?.total_growth_percent,
        icon: TrendingUp,
        description: 'Year-over-year FTE growth percentage'
      },
      {
        title: 'Revenue Growth',
        value: previousKpis?.financial?.net_sales ? 
          `${calculateGrowth(financial?.net_sales || 0, previousKpis.financial.net_sales).toFixed(1)}%` : 'N/A',
        rawValue: financial?.net_sales || 0,
        previousValue: previousKpis?.financial?.net_sales,
        icon: DollarSign,
        description: 'Year-over-year revenue growth'
      },
      {
        title: 'Total FTE',
        value: formatNumber(growth?.current_total_fte || 0),
        rawValue: growth?.current_total_fte || 0,
        previousValue: previousKpis?.growth?.current_total_fte,
        icon: Users,
        description: 'Current total workforce'
      },
      {
        title: 'Utilization Rate',
        value: formatPercent(financial?.avg_utr || 0),
        rawValue: (financial?.avg_utr || 0) * 100,
        previousValue: previousKpis?.financial?.avg_utr ? previousKpis.financial.avg_utr * 100 : undefined,
        icon: Target,
        description: 'Average consultant utilization'
      }
    ];
    
    return (
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <TrendingUp className="h-5 w-5" />
            <span>Growth Metrics</span>
          </CardTitle>
          <CardDescription>Growth rates and expansion indicators</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {growthCards.map((kpi, index) => {
              const growth = kpi.previousValue ? calculateGrowth(kpi.rawValue, kpi.previousValue) : null;
              const Icon = kpi.icon;
              
              return (
                <Card key={index}>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">{kpi.title}</CardTitle>
                    <Icon className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{kpi.value}</div>
                    {growth !== null && (
                      <div className="flex items-center space-x-1 text-xs mt-1">
                        {growth >= 0 ? (
                          <TrendingUp className="h-3 w-3 text-green-500" />
                        ) : (
                          <TrendingDown className="h-3 w-3 text-red-500" />
                        )}
                        <span className={growth >= 0 ? 'text-green-600' : 'text-red-600'}>
                          {Math.abs(growth).toFixed(1)}% vs previous year
                        </span>
                      </div>
                    )}
                    <p className="text-xs text-muted-foreground mt-1">
                      {kpi.description}
                    </p>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </CardContent>
      </Card>
    );
  };

  // Workforce Analysis Panel
  const renderWorkforcePanel = (yearData?: YearData) => {
    const targetYear = yearData || currentYearData;
    if (!targetYear) return null;
    
    
    const workforceMetrics = ResultsService.calculateWorkforceMetrics(targetYear);
    const productivityMetrics = ResultsService.calculateProductivityMetrics(targetYear);
    if (!workforceMetrics) return null;
    
    // Check if metrics are all zero (indicating missing baseline data)
    const hasZeroMetrics = workforceMetrics.totalRecruitment === 0 && 
                          workforceMetrics.totalChurn === 0 && 
                          workforceMetrics.netRecruitment === 0;
    
    const previousYear = yearsData.find(y => parseInt(y.year) === parseInt(targetYear.year) - 1);
    let previousWorkforce = null;
    
    if (previousYear) {
      previousWorkforce = ResultsService.calculateWorkforceMetrics(previousYear);
    }
    
    // Calculate non-debit metrics
    const currentTotalFTE = targetYear?.kpis?.growth?.current_total_fte || 0;
    const nonDebitRatio = targetYear?.kpis?.growth?.non_debit_ratio || 0;
    const nonDebitAbsolute = Math.round(currentTotalFTE * nonDebitRatio);
    
    const previousTotalFTE = previousYear?.kpis?.growth?.current_total_fte || 0;
    const previousNonDebitRatio = previousYear?.kpis?.growth?.non_debit_ratio || 0;
    const previousNonDebitAbsolute = Math.round(previousTotalFTE * previousNonDebitRatio);

    const workforceCards = [
      {
        title: 'Total Recruitment',
        value: formatNumber(workforceMetrics.totalRecruitment),
        rawValue: workforceMetrics.totalRecruitment,
        previousValue: previousWorkforce?.totalRecruitment,
        icon: Users,
        description: 'Total hires during the year'
      },
      {
        title: 'Total Churn',
        value: formatNumber(workforceMetrics.totalChurn),
        rawValue: workforceMetrics.totalChurn,
        previousValue: previousWorkforce?.totalChurn,
        icon: TrendingDown,
        description: 'Total departures during the year'
      },
      {
        title: 'Net Recruitment',
        value: formatNumber(workforceMetrics.netRecruitment),
        rawValue: workforceMetrics.netRecruitment,
        previousValue: previousWorkforce?.netRecruitment,
        icon: TrendingUp,
        description: 'Net workforce growth (hires - departures)'
      },
      {
        title: 'Non-Debit Ratio',
        value: `${(nonDebitRatio * 100).toFixed(1)}% (${formatNumber(nonDebitAbsolute)} FTE)`,
        rawValue: nonDebitRatio * 100,
        previousValue: previousNonDebitRatio * 100,
        icon: Building2,
        description: 'Sales, Recruitment & Operations as % of total workforce'
      },
      {
        title: 'Churn Rate',
        value: workforceMetrics.totalChurn > 0 && currentTotalFTE ? 
          `${((workforceMetrics.totalChurn / currentTotalFTE) * 100).toFixed(1)}%` : 'N/A',
        rawValue: workforceMetrics.totalChurn > 0 && currentTotalFTE ? 
          (workforceMetrics.totalChurn / currentTotalFTE) * 100 : 0,
        previousValue: previousWorkforce && previousTotalFTE ? 
          (previousWorkforce.totalChurn / previousTotalFTE) * 100 : undefined,
        icon: Target,
        description: 'Annual churn rate percentage'
      }
    ];

    // Add productivity metrics if available
    if (productivityMetrics) {
      const monthlyRecruitmentPerRecruiter = productivityMetrics.recruitmentPerRecruiter / 12;
      const monthlySalesPerSalesperson = productivityMetrics.netSalesPerSalesperson / 12;
      
      workforceCards.push(
        {
          title: 'Recruitment per Recruiter',
          value: productivityMetrics.recruitmentPerRecruiter > 0 
            ? `${formatNumber(productivityMetrics.recruitmentPerRecruiter, 1)}/year`
            : 'N/A',
          rawValue: productivityMetrics.recruitmentPerRecruiter,
          previousValue: undefined, // TODO: Calculate previous year productivity if needed
          icon: UserPlus,
          description: `${formatNumber(monthlyRecruitmentPerRecruiter, 1)}/month • ${formatNumber(productivityMetrics.totalRecruiters)} recruiters`
        },
        {
          title: 'Net Sales per Salesperson',
          value: productivityMetrics.netSalesPerSalesperson > 0 
            ? `${formatCurrency(productivityMetrics.netSalesPerSalesperson)}/year`
            : 'N/A',
          rawValue: productivityMetrics.netSalesPerSalesperson,
          previousValue: undefined, // TODO: Calculate previous year productivity if needed
          icon: Activity,
          description: `${formatCurrency(monthlySalesPerSalesperson)}/month • ${formatNumber(productivityMetrics.totalSalespeople)} salespeople`
        }
      );
    }
    
    return (
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Users className="h-5 w-5" />
            <span>Workforce Analysis</span>
          </CardTitle>
          <CardDescription>Recruitment, churn, and workforce dynamics</CardDescription>
        </CardHeader>
        <CardContent>
          {hasZeroMetrics && (
            <div className="mb-4 p-3 bg-yellow-50 border-l-4 border-yellow-400 rounded">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-yellow-700">
                    <strong>Limited baseline data:</strong> This scenario may have insufficient recruitment/churn baseline data, resulting in zero values. Consider updating the scenario with proper baseline inputs for more realistic workforce projections.
                  </p>
                </div>
              </div>
            </div>
          )}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {workforceCards.map((kpi, index) => {
              const growth = kpi.previousValue ? calculateGrowth(kpi.rawValue, kpi.previousValue) : null;
              const Icon = kpi.icon;
              
              return (
                <Card key={index}>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">{kpi.title}</CardTitle>
                    <Icon className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{kpi.value}</div>
                    {growth !== null && (
                      <div className="flex items-center space-x-1 text-xs mt-1">
                        {growth >= 0 ? (
                          <TrendingUp className="h-3 w-3 text-green-500" />
                        ) : (
                          <TrendingDown className="h-3 w-3 text-red-500" />
                        )}
                        <span className={growth >= 0 ? 'text-green-600' : 'text-red-600'}>
                          {Math.abs(growth).toFixed(1)}% vs previous year
                        </span>
                      </div>
                    )}
                    <p className="text-xs text-muted-foreground mt-1">
                      {kpi.description}
                    </p>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </CardContent>
      </Card>
    );
  };


  // FTE Growth Chart
  const renderFTEGrowthChart = (yearData?: YearData) => {
    const targetYear = yearData || currentYearData;
    
    // Generate FTE growth data using service
    const fteData = useMemo(() => {
      if (!targetYear) return [];
      return ResultsService.generateFTEGrowthData(targetYear);
    }, [targetYear]);

    return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle>FTE Growth Over Time</CardTitle>
        <CardDescription>Monthly consultant FTE progression</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={fteData}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis 
              dataKey="month" 
              className="text-xs"
              tick={{ fontSize: 12 }}
            />
            <YAxis 
              className="text-xs"
              tick={{ fontSize: 12 }}
            />
            <Tooltip 
              formatter={(value) => [formatNumber(value as number), 'FTE']}
              labelClassName="text-sm"
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '6px'
              }}
            />
            <Line 
              type="monotone" 
              dataKey="value" 
              stroke="hsl(var(--primary))" 
              strokeWidth={2}
              dot={{ fill: 'hsl(var(--primary))', strokeWidth: 2, r: 4 }}
              name="Consultant FTE"
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
    );
  };

  // Seniority Distribution Chart (Pyramid)
  const renderSeniorityChart = (yearData?: YearData) => {
    const targetYear = yearData || currentYearData;
    
    // Generate seniority data using service and transform to pyramid stages
    const pyramidStages = useMemo((): PyramidStage[] => {
      if (!targetYear) return [];
      
      const seniorityData = ResultsService.generateSeniorityData(targetYear);
      if (!seniorityData.length) return [];
      
      // Map seniority levels to career journey stages
      const levelMapping: { [key: string]: { stage: number; description: string } } = {
        'A': { stage: 1, description: 'Associate level' },
        'AC': { stage: 1, description: 'Associate Consultant' },
        'C': { stage: 2, description: 'Consultant level' },
        'SrC': { stage: 2, description: 'Senior Consultant' },
        'AM': { stage: 3, description: 'Associate Manager' },
        'M': { stage: 3, description: 'Manager level' },
        'SrM': { stage: 4, description: 'Senior Manager' },
        'Pi': { stage: 4, description: 'Principal level' },
        'P': { stage: 4, description: 'Partner level' }
      };
      
      // Aggregate by career journey stage
      const stageData: { [key: number]: { count: number; totalPercentage: number } } = {};
      
      seniorityData.forEach(item => {
        const mapping = levelMapping[item.level];
        if (mapping) {
          if (!stageData[mapping.stage]) {
            stageData[mapping.stage] = { count: 0, totalPercentage: 0 };
          }
          stageData[mapping.stage].count += item.count;
          stageData[mapping.stage].totalPercentage += item.percentage;
        }
      });
      
      // Convert to PyramidStage format
      return Object.entries(stageData)
        .map(([stage, data]) => {
          const stageNum = parseInt(stage);
          return {
            stage: stageNum,
            label: `Journey ${stageNum}`,
            percentage: Math.round(data.totalPercentage * 10) / 10, // Round to 1 decimal
            description: `${formatNumber(data.count)} FTE`
          };
        })
        .sort((a, b) => a.stage - b.stage);
    }, [targetYear]);

    return (
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Career Journey Distribution</CardTitle>
          <CardDescription>Workforce distribution across career stages</CardDescription>
        </CardHeader>
        <CardContent>
          {pyramidStages.length > 0 ? (
            <PyramidChart 
              stages={pyramidStages}
              colors={['bg-orange-500', 'bg-yellow-500', 'bg-green-500', 'bg-blue-500']}
              className="max-w-3xl"
            />
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No seniority data available for this year</p>
            </div>
          )}
        </CardContent>
      </Card>
    );
  };

  // Recruitment vs Churn Chart
  const renderRecruitmentChurnChart = (yearData?: YearData) => {
    const targetYear = yearData || currentYearData;
    
    // Generate recruitment vs churn data using service
    const recruitmentChurnDataForYear = useMemo(() => {
      if (!targetYear) return [];
      return ResultsService.generateRecruitmentChurnData(targetYear);
    }, [targetYear]);

    return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle>Monthly Recruitment vs Churn</CardTitle>
        <CardDescription>Hiring and departure trends</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={recruitmentChurnDataForYear}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis 
              dataKey="month" 
              className="text-xs"
              tick={{ fontSize: 12 }}
            />
            <YAxis 
              className="text-xs"
              tick={{ fontSize: 12 }}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '6px'
              }}
            />
            <Legend />
            <Bar dataKey="recruitment" fill="#10b981" name="Recruitment" />
            <Bar dataKey="churn" fill="#ef4444" name="Churn" />
            <Bar dataKey="net" fill="hsl(var(--primary))" name="Net Growth" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
    );
  };

  // Quarterly Workforce Analytics Chart
  const renderQuarterlyWorkforceChart = (yearData?: YearData) => {
    const targetYear = yearData || currentYearData;
    
    // Generate quarterly workforce data using service
    const quarterlyDataForYear = useMemo(() => {
      if (!targetYear) return [];
      return ResultsService.generateQuarterlyWorkforceData(targetYear);
    }, [targetYear]);

    if (!quarterlyDataForYear.length) return null;

    return (
      <Card className="mb-6">
        <CardContent className="p-0">
          <QuarterlyWorkforceChart 
            yearData={quarterlyDataForYear}
            title={`Year ${targetYear.year} - Workforce Movement by Quarter`}
          />
        </CardContent>
      </Card>
    );
  };

  // Year-over-Year Comparison
  const renderYearComparison = () => {
    if (yearsData.length < 2) return null;
    
    const comparisonData = ResultsService.generateYearComparisonData(yearsData);
    
    return (
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Year-over-Year Comparison</CardTitle>
          <CardDescription>Multi-year performance trends</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={comparisonData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis 
                dataKey="year" 
                className="text-xs"
                tick={{ fontSize: 12 }}
              />
              <YAxis 
                yAxisId="left" 
                className="text-xs"
                tick={{ fontSize: 12 }}
              />
              <YAxis 
                yAxisId="right" 
                orientation="right" 
                className="text-xs"
                tick={{ fontSize: 12 }}
              />
              <Tooltip 
                formatter={(value, name) => {
                  if (name === 'Net Sales' || name === 'EBITDA') {
                    return [formatCurrency(value as number), name];
                  }
                  return [formatNumber(value as number, 1), name];
                }}
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '6px'
                }}
              />
              <Legend />
              <Area
                yAxisId="left"
                type="monotone"
                dataKey="netSales"
                stackId="1"
                stroke="hsl(var(--primary))"
                fill="hsl(var(--primary))"
                fillOpacity={0.3}
                name="Net Sales"
              />
              <Area
                yAxisId="right"
                type="monotone"
                dataKey="consultants"
                stackId="2"
                stroke="#10b981"
                fill="#10b981"
                fillOpacity={0.3}
                name="Total Consultants"
              />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    );
  };

  if (!result || !yearsData.length) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center text-muted-foreground">
            No simulation results available
          </div>
        </CardContent>
      </Card>
    );
  }

  // Debug office information
  const getOfficeInfo = () => {
    if (!currentYearData) return { offices: [], count: 0 };
    const offices = ResultsService.getOfficesData(currentYearData);
    const officeNames = Object.keys(offices);
    return { offices: officeNames, count: officeNames.length };
  };

  const officeInfo = getOfficeInfo();

  return (
    <div className="space-y-6">
      {/* Office Information */}
      {currentYearData && (
        <Card className="mb-4">
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Building2 className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">
                  Office Scope: 
                </span>
                <span className="text-sm text-muted-foreground">
                  {officeInfo.count === 1 
                    ? officeInfo.offices[0]
                    : officeInfo.count > 1 
                      ? `${officeInfo.count} offices (${officeInfo.offices.join(', ')})`
                      : 'No offices selected'
                  }
                </span>
              </div>
              <div className="text-xs text-muted-foreground">
                Aggregated consultant data across selected offices
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Year-over-Year Comparison (if multiple years) */}
      {yearsData.length > 1 && renderYearComparison()}
      
      {/* Year Tabs */}
      <Tabs value={selectedYear} onValueChange={setSelectedYear}>
        <TabsList className={`grid w-full ${yearsData.length <= 3 ? `grid-cols-${yearsData.length}` : 'grid-cols-3'}`}>
          {yearsData.map(yearData => (
            <TabsTrigger key={yearData.year} value={yearData.year}>
              Year {yearData.year}
            </TabsTrigger>
          ))}
        </TabsList>
        
        {yearsData.map(yearData => (
          <TabsContent key={yearData.year} value={yearData.year} className="space-y-6">
            {/* Financial Panel */}
            {renderFinancialPanel(yearData)}
            
            {/* Growth Panel */}
            {renderGrowthPanel(yearData)}
            
            {/* Workforce Analysis Panel */}
            {renderWorkforcePanel(yearData)}
            
            {/* Charts Grid */}
            <div className="grid gap-6 md:grid-cols-2">
              <div>{renderFTEGrowthChart(yearData)}</div>
              <div>{renderSeniorityChart(yearData)}</div>
            </div>
            
            <div>{renderRecruitmentChurnChart(yearData)}</div>
            
            {/* Quarterly Workforce Analytics */}
            <div>{renderQuarterlyWorkforceChart(yearData)}</div>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
};

export default ModernResultsDisplay;