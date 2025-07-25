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
  Building2
} from 'lucide-react';
import type { ScenarioResponse } from '../../types/unified-data-structures';

interface ModernResultsDisplayProps {
  result: ScenarioResponse;
}

interface YearData {
  year: string;
  data: any;
  kpis: any;
}

interface ChartDataPoint {
  month: string;
  value: number;
  year: string;
}

interface SeniorityData {
  level: string;
  count: number;
  percentage: number;
  color: string;
}

interface RecruitmentChurnData {
  month: string;
  recruitment: number;
  churn: number;
  net: number;
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899', '#f97316'];
const LEVEL_ORDER = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP'];

const ModernResultsDisplay: React.FC<ModernResultsDisplayProps> = ({ result }) => {
  const [selectedYear, setSelectedYear] = useState<string>('');

  // Process simulation results
  const yearsData = useMemo((): YearData[] => {
    if (!result?.results?.years) return [];
    
    const years = Object.keys(result.results.years).sort();
    return years.map(year => ({
      year,
      data: result.results.years[year],
      kpis: result.results.years[year].kpis || {}
    }));
  }, [result]);

  // Set initial selected year
  React.useEffect(() => {
    if (yearsData.length > 0 && !selectedYear) {
      setSelectedYear(yearsData[0].year);
    }
  }, [yearsData, selectedYear]);

  const currentYearData = yearsData.find(y => y.year === selectedYear);

  // Helper function to get all offices data or specific office
  const getOfficesData = (yearData: YearData) => {
    if (!yearData?.data?.offices) return {};
    return yearData.data.offices;
  };

  // Memoized function to aggregate consultant data across offices
  const aggregateConsultantData = useMemo(() => (yearData: YearData) => {
    const offices = getOfficesData(yearData);
    const officeNames = Object.keys(offices);
    
    
    if (officeNames.length === 0) return null;
    
    // If only one office, return its data directly
    if (officeNames.length === 1) {
      const officeName = officeNames[0];
      return offices[officeName]?.roles?.Consultant || null;
    }
    
    // Aggregate across multiple offices
    const aggregatedConsultant: any = {};
    
    LEVEL_ORDER.forEach(level => {
      const levelDataArrays: any[] = [];
      
      officeNames.forEach(officeName => {
        const consultant = offices[officeName]?.roles?.Consultant;
        if (consultant?.[level] && Array.isArray(consultant[level])) {
          levelDataArrays.push(consultant[level]);
        }
      });
      
      if (levelDataArrays.length > 0) {
        // Aggregate monthly data across offices
        const monthCount = levelDataArrays[0].length; // Assume all have same month count
        aggregatedConsultant[level] = [];
        
        for (let monthIndex = 0; monthIndex < monthCount; monthIndex++) {
          let totalFTE = 0;
          let totalRecruitment = 0;
          let totalChurn = 0;
          
          levelDataArrays.forEach(levelArray => {
            const monthData = levelArray[monthIndex] || {};
            totalFTE += monthData.fte || 0;
            totalRecruitment += monthData.recruitment || 0;
            totalChurn += monthData.churn || 0;
          });
          
          aggregatedConsultant[level].push({
            fte: totalFTE,
            recruitment: totalRecruitment,
            churn: totalChurn
          });
        }
      }
    });
    
    return Object.keys(aggregatedConsultant).length > 0 ? aggregatedConsultant : null;
  }, []);

  // Format numbers
  const formatNumber = (num: number, decimals = 0) => {
    if (typeof num !== 'number' || isNaN(num)) return 'N/A';
    return num.toLocaleString('en-US', { maximumFractionDigits: decimals });
  };

  const formatCurrency = (num: number) => {
    if (typeof num !== 'number' || isNaN(num)) return 'N/A';
    return `${formatNumber(num / 1000000, 1)}M SEK`;
  };

  const formatPercent = (num: number) => {
    if (typeof num !== 'number' || isNaN(num)) return 'N/A';
    return `${(num * 100).toFixed(1)}%`;
  };

  // Calculate growth trend between years
  const calculateGrowth = (current: number, previous: number) => {
    if (!previous || previous === 0) return null;
    return ((current - previous) / previous) * 100;
  };

  // Generate FTE growth chart data
  const fteGrowthData = useMemo((): ChartDataPoint[] => {
    if (!currentYearData) return [];
    
    const consultantData = aggregateConsultantData(currentYearData);
    if (!consultantData?.A || !Array.isArray(consultantData.A)) return [];
    
    return consultantData.A.map((monthData: any, index: number) => ({
      month: `Month ${index + 1}`,
      value: monthData.fte || 0,
      year: currentYearData.year
    }));
  }, [currentYearData]);

  // Generate seniority distribution data
  const seniorityData = useMemo((): SeniorityData[] => {
    if (!currentYearData) return [];
    
    const consultantData = aggregateConsultantData(currentYearData);
    if (!consultantData) return [];
    
    const levelCounts: { [key: string]: number } = {};
    let totalFTE = 0;
    
    // Calculate FTE for each level (using December data)
    LEVEL_ORDER.forEach(level => {
      const levelData = consultantData[level];
      if (Array.isArray(levelData) && levelData.length > 0) {
        const decemberData = levelData[levelData.length - 1]; // Last month
        const fte = decemberData?.fte || 0;
        levelCounts[level] = fte;
        totalFTE += fte;
      }
    });
    
    return LEVEL_ORDER.map((level, index) => ({
      level,
      count: levelCounts[level] || 0,
      percentage: totalFTE > 0 ? ((levelCounts[level] || 0) / totalFTE) * 100 : 0,
      color: COLORS[index % COLORS.length]
    })).filter(item => item.count > 0);
  }, [currentYearData]);

  // Generate recruitment vs churn data
  const recruitmentChurnData = useMemo((): RecruitmentChurnData[] => {
    if (!currentYearData) return [];
    
    const consultantData = aggregateConsultantData(currentYearData);
    if (!consultantData?.A || !Array.isArray(consultantData.A)) return [];
    
    return consultantData.A.map((monthData: any, index: number) => ({
      month: `M${index + 1}`,
      recruitment: monthData.recruitment || 0,
      churn: monthData.churn || 0,
      net: (monthData.recruitment || 0) - (monthData.churn || 0)
    }));
  }, [currentYearData]);

  // Calculate workforce metrics across ALL roles
  const calculateWorkforceMetrics = (yearData?: YearData) => {
    const targetYear = yearData || currentYearData;
    if (!targetYear) return null;
    
    const offices = getOfficesData(targetYear);
    if (!offices || Object.keys(offices).length === 0) return null;
    
    let totalRecruitment = 0;
    let totalChurn = 0;
    
    // Sum recruitment and churn across ALL roles and offices
    Object.values(offices).forEach((office: any) => {
      if (office?.levels) {
        // Process each role (Consultant, Sales, Recruitment, Operations)
        Object.entries(office.levels).forEach(([roleName, roleData]: [string, any]) => {
          if (roleData && typeof roleData === 'object') {
            // Handle leveled roles (Consultant, Sales, Recruitment)
            Object.entries(roleData).forEach(([levelName, levelData]: [string, any]) => {
              if (Array.isArray(levelData)) {
                levelData.forEach((monthData: any) => {
                  totalRecruitment += monthData.recruitment || 0;
                  totalChurn += monthData.churn || 0;
                });
              }
            });
          } else if (Array.isArray(roleData)) {
            // Handle flat roles (Operations)
            roleData.forEach((monthData: any) => {
              totalRecruitment += monthData.recruitment || 0;
              totalChurn += monthData.churn || 0;
            });
          }
        });
      }
    });
    
    return {
      totalRecruitment,
      totalChurn,
      netRecruitment: totalRecruitment - totalChurn
    };
  };

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
    
    
    const workforceMetrics = calculateWorkforceMetrics(targetYear);
    if (!workforceMetrics) return null;
    
    const previousYear = yearsData.find(y => parseInt(y.year) === parseInt(targetYear.year) - 1);
    let previousWorkforce = null;
    
    if (previousYear) {
      previousWorkforce = calculateWorkforceMetrics(previousYear);
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
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
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
    
    // Generate FTE growth data for this specific year
    const fteData = useMemo((): ChartDataPoint[] => {
      if (!targetYear) return [];
      
      const consultantData = aggregateConsultantData(targetYear);
      if (!consultantData?.A || !Array.isArray(consultantData.A)) return [];
      
      return consultantData.A.map((monthData: any, index: number) => ({
        month: `Month ${index + 1}`,
        value: monthData.fte || 0,
        year: targetYear.year
      }));
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

  // Seniority Distribution Chart
  const renderSeniorityChart = (yearData?: YearData) => {
    const targetYear = yearData || currentYearData;
    
    // Generate seniority data for this specific year
    const seniorityDataForYear = useMemo((): SeniorityData[] => {
      if (!targetYear) return [];
      
      const consultantData = aggregateConsultantData(targetYear);
      if (!consultantData) return [];
      
      const levelCounts: { [key: string]: number } = {};
      let totalFTE = 0;
      
      // Calculate FTE for each level (using December data)
      LEVEL_ORDER.forEach(level => {
        const levelData = consultantData[level];
        if (Array.isArray(levelData) && levelData.length > 0) {
          const decemberData = levelData[levelData.length - 1]; // Last month
          const fte = decemberData?.fte || 0;
          levelCounts[level] = fte;
          totalFTE += fte;
        }
      });
      
      return LEVEL_ORDER.map((level, index) => ({
        level,
        count: levelCounts[level] || 0,
        percentage: totalFTE > 0 ? ((levelCounts[level] || 0) / totalFTE) * 100 : 0,
        color: COLORS[index % COLORS.length]
      })).filter(item => item.count > 0);
    }, [targetYear]);

    return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle>Seniority Distribution</CardTitle>
        <CardDescription>Current headcount by seniority level</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={seniorityDataForYear}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={100}
              paddingAngle={2}
              dataKey="count"
            >
              {seniorityDataForYear.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip 
              formatter={(value, name, props) => [
                `${formatNumber(value as number)} FTE (${props.payload?.percentage.toFixed(1)}%)`,
                `Level ${name}`
              ]}
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                border: '1px solid hsl(var(--border))',
                borderRadius: '6px'
              }}
            />
          </PieChart>
        </ResponsiveContainer>
        <div className="grid grid-cols-4 gap-2 mt-4">
          {seniorityDataForYear.map((item, index) => (
            <div key={item.level} className="flex items-center space-x-2">
              <div 
                className="w-3 h-3 rounded-sm flex-shrink-0" 
                style={{ backgroundColor: item.color }}
              />
              <div className="text-xs">
                <div className="font-medium">{item.level}</div>
                <div className="text-muted-foreground">{formatNumber(item.count)} FTE</div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
    );
  };

  // Recruitment vs Churn Chart
  const renderRecruitmentChurnChart = (yearData?: YearData) => {
    const targetYear = yearData || currentYearData;
    
    // Generate recruitment vs churn data for this specific year
    const recruitmentChurnDataForYear = useMemo((): RecruitmentChurnData[] => {
      if (!targetYear) return [];
      
      const consultantData = aggregateConsultantData(targetYear);
      if (!consultantData?.A || !Array.isArray(consultantData.A)) return [];
      
      return consultantData.A.map((monthData: any, index: number) => ({
        month: `M${index + 1}`,
        recruitment: monthData.recruitment || 0,
        churn: monthData.churn || 0,
        net: (monthData.recruitment || 0) - (monthData.churn || 0)
      }));
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

  // Year-over-Year Comparison
  const renderYearComparison = () => {
    if (yearsData.length < 2) return null;
    
    const comparisonData = yearsData.map(yearData => {
      const financial = yearData.kpis?.financial || {};
      return {
        year: yearData.year,
        netSales: financial.net_sales || 0,
        ebitda: financial.ebitda || 0,
        margin: (financial.margin || 0) * 100,
        consultants: financial.total_consultants || 0,
        totalFTE: yearData.data?.total_fte || 0
      };
    });
    
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
    const offices = getOfficesData(currentYearData);
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
        <TabsList className="grid w-full grid-cols-3">
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
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
};

export default ModernResultsDisplay;