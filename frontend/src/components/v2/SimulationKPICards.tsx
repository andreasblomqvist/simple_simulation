import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { TrendingUp, TrendingDown, Users, DollarSign, Target, PieChart, Minus } from 'lucide-react';
import type { SimulationResults } from '../../types/unified-data-structures';

interface KPICard {
  title: string;
  value: string;
  previousValue?: string;
  change?: number;
  changeType?: 'increase' | 'decrease' | 'neutral';
  icon: React.ComponentType<any>;
  color: string;
  unit?: 'currency' | 'percentage' | 'count';
}

interface SimulationKPICardsProps {
  results: SimulationResults;
  selectedYear: string;
  selectedOffice: string | 'Group';
  className?: string;
}

export const SimulationKPICards: React.FC<SimulationKPICardsProps> = ({
  results,
  selectedYear,
  selectedOffice,
  className
}) => {
  // Helper function to get KPI value from simulation results
  const getKPIValue = (kpiKey: string, year: string, office: string | 'Group'): number => {
    if (!results?.years?.[year]) return 0;

    const yearData = results.years[year];

    if (office === 'Group') {
      // Use group-level KPIs
      const kpis = yearData.kpis;
      if (!kpis) return 0;

      const financial = kpis.financial;
      const growth = kpis.growth;
      const journeys = kpis.journeys;

      switch (kpiKey) {
        case 'FTE':
          return financial?.total_consultants || 0;
        case 'Sales':
          return financial?.net_sales || 0;
        case 'EBITDA':
          return financial?.ebitda || 0;
        case 'EBITDA%':
          return financial?.margin ? financial.margin * 100 : 0;
        case 'Growth%':
          return growth?.total_growth_percent || 0;
        case 'J-1':
          return journeys?.journey_percentages?.["Journey 1"] || 0;
        case 'J-2':
          return journeys?.journey_percentages?.["Journey 2"] || 0;
        case 'J-3':
          return journeys?.journey_percentages?.["Journey 3"] || 0;
        case 'J-4':
          return journeys?.journey_percentages?.["Journey 4"] || 0;
        default:
          return 0;
      }
    } else {
      // Use office-level data
      const officeData = yearData.offices?.[office];
      if (!officeData) return 0;

      const financial = officeData.financial || {};
      const growth = officeData.growth || {};
      const journeys = officeData.journeys || {};

      switch (kpiKey) {
        case 'FTE':
          return officeData.total_fte || 0;
        case 'Sales':
          return financial.net_sales || 0;
        case 'EBITDA':
          return financial.ebitda || 0;
        case 'EBITDA%':
          return financial.margin ? financial.margin * 100 : 0;
        case 'Growth%':
          return growth.total_growth_percent || 0;
        case 'J-1':
          return journeys.journey_percentages?.["Journey 1"] || 0;
        case 'J-2':
          return journeys.journey_percentages?.["Journey 2"] || 0;
        case 'J-3':
          return journeys.journey_percentages?.["Journey 3"] || 0;
        case 'J-4':
          return journeys.journey_percentages?.["Journey 4"] || 0;
        default:
          return 0;
      }
    }
  };

  // Helper function to format values
  const formatValue = (value: number, unit?: 'currency' | 'percentage' | 'count'): string => {
    if (!unit) return String(value);

    const formatLargeNumber = (num: number) => {
      if (Math.abs(num) >= 1_000_000_000) {
        return (num / 1_000_000_000).toFixed(2).replace(/\.00$/, '') + 'B';
      }
      if (Math.abs(num) >= 1_000_000) {
        return (num / 1_000_000).toFixed(2).replace(/\.00$/, '') + 'M';
      }
      if (Math.abs(num) >= 1_000) {
        return (num / 1_000).toFixed(1).replace(/\.0$/, '') + 'K';
      }
      return num.toLocaleString();
    };

    switch (unit) {
      case 'percentage':
        return `${value.toFixed(1)}%`;
      case 'currency':
        return `SEK ${formatLargeNumber(value)}`;
      case 'count':
        return formatLargeNumber(value);
      default:
        return String(value);
    }
  };

  // Calculate change from previous year
  const calculateChange = (kpiKey: string, currentYear: string): { change: number; changeType: 'increase' | 'decrease' | 'neutral' } => {
    const availableYears = Object.keys(results?.years || {}).sort();
    const currentYearIndex = availableYears.indexOf(currentYear);
    
    if (currentYearIndex <= 0) {
      return { change: 0, changeType: 'neutral' };
    }

    const previousYear = availableYears[currentYearIndex - 1];
    const currentValue = getKPIValue(kpiKey, currentYear, selectedOffice);
    const previousValue = getKPIValue(kpiKey, previousYear, selectedOffice);

    if (previousValue === 0) {
      return { change: 0, changeType: 'neutral' };
    }

    const change = ((currentValue - previousValue) / previousValue) * 100;
    let changeType: 'increase' | 'decrease' | 'neutral' = 'neutral';
    
    if (Math.abs(change) > 0.1) { // Only show change if greater than 0.1%
      changeType = change > 0 ? 'increase' : 'decrease';
    }

    return { change: Math.abs(change), changeType };
  };

  // Generate KPI cards data
  const generateKPICards = (): KPICard[] => {
    const kpis = [
      {
        key: 'FTE',
        title: 'Total FTE',
        icon: Users,
        color: 'blue',
        unit: 'count' as const
      },
      {
        key: 'Growth%',
        title: 'Growth Rate',
        icon: TrendingUp,
        color: 'green',
        unit: 'percentage' as const
      },
      {
        key: 'Sales',
        title: 'Net Sales',
        icon: DollarSign,
        color: 'yellow',
        unit: 'currency' as const
      },
      {
        key: 'EBITDA',
        title: 'EBITDA',
        icon: Target,
        color: 'purple',
        unit: 'currency' as const
      },
      {
        key: 'EBITDA%',
        title: 'EBITDA Margin',
        icon: PieChart,
        color: 'orange',
        unit: 'percentage' as const
      }
    ];

    return kpis.map(kpi => {
      const value = getKPIValue(kpi.key, selectedYear, selectedOffice);
      const { change, changeType } = calculateChange(kpi.key, selectedYear);

      return {
        title: kpi.title,
        value: formatValue(value, kpi.unit),
        change: change,
        changeType: changeType,
        icon: kpi.icon,
        color: kpi.color,
        unit: kpi.unit
      };
    });
  };

  const kpiCards = generateKPICards();

  // Render trend icon based on change type
  const renderTrendIcon = (changeType: 'increase' | 'decrease' | 'neutral', change: number) => {
    if (changeType === 'neutral' || change < 0.1) {
      return <Minus className="h-3 w-3 text-muted-foreground" />;
    }
    
    if (changeType === 'increase') {
      return <TrendingUp className="h-3 w-3 text-green-600" />;
    } else {
      return <TrendingDown className="h-3 w-3 text-red-600" />;
    }
  };

  // Get badge variant based on change type
  const getBadgeVariant = (changeType: 'increase' | 'decrease' | 'neutral') => {
    switch (changeType) {
      case 'increase':
        return 'default'; // Green variant
      case 'decrease':
        return 'destructive'; // Red variant
      default:
        return 'secondary'; // Neutral variant
    }
  };

  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 ${className || ''}`}>
      {kpiCards.map((kpi, index) => (
        <Card key={index} className="relative overflow-hidden">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {kpi.title}
            </CardTitle>
            <kpi.icon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{kpi.value}</div>
            {kpi.change !== undefined && kpi.change > 0.1 && (
              <div className="flex items-center space-x-1 mt-1">
                {renderTrendIcon(kpi.changeType!, kpi.change)}
                <Badge 
                  variant={getBadgeVariant(kpi.changeType!)}
                  className="text-xs px-1.5 py-0.5"
                >
                  {kpi.change.toFixed(1)}%
                </Badge>
                <span className="text-xs text-muted-foreground">vs prev year</span>
              </div>
            )}
            {(kpi.change === undefined || kpi.change <= 0.1) && (
              <div className="flex items-center space-x-1 mt-1">
                <Minus className="h-3 w-3 text-muted-foreground" />
                <Badge variant="secondary" className="text-xs px-1.5 py-0.5">
                  No change
                </Badge>
              </div>
            )}
          </CardContent>
          
          {/* Color accent bar */}
          <div 
            className={`absolute bottom-0 left-0 right-0 h-1 bg-${kpi.color}-500`}
            style={{
              backgroundColor: kpi.color === 'blue' ? '#3b82f6' :
                              kpi.color === 'green' ? '#10b981' :
                              kpi.color === 'yellow' ? '#f59e0b' :
                              kpi.color === 'purple' ? '#8b5cf6' :
                              kpi.color === 'orange' ? '#f97316' : '#6b7280'
            }}
          />
        </Card>
      ))}
    </div>
  );
};