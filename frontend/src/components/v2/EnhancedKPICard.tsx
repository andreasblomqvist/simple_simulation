import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { Text } from '../../design-system/typography';
import { Container } from '../../design-system/layout';

interface KPIData {
  current: number;
  previous: number;
  target: number;
  sparklineData?: Array<{ period: string; value: number }>;
}

interface EnhancedKPICardProps {
  title: string;
  data: KPIData;
  icon?: React.ComponentType<any>;
  className?: string;
}

const EnhancedKPICard: React.FC<EnhancedKPICardProps> = ({
  title,
  data,
  icon: Icon,
  className = ''
}) => {
  const change = data.current - data.previous;
  const changePercent = data.previous > 0 ? (change / data.previous) * 100 : 0;
  const isPositive = change > 0;
  const isNegative = change < 0;
  const isNeutral = change === 0;

  const formatValue = (value: number): string => {
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `${(value / 1000).toFixed(1)}K`;
    }
    return value.toString();
  };

  const getChangeIcon = () => {
    if (isPositive) return <TrendingUp className="h-4 w-4 text-green-600" />;
    if (isNegative) return <TrendingDown className="h-4 w-4 text-red-600" />;
    return <Minus className="h-4 w-4 text-gray-500" />;
  };

  const getBadgeVariant = () => {
    if (isPositive) return 'default';
    if (isNegative) return 'destructive';
    return 'secondary';
  };

  return (
    <Card className={`${className}`} data-testid="kpi-card">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {Icon && <Icon className="h-4 w-4 text-muted-foreground" />}
      </CardHeader>
      <CardContent>
        <Text variant="display-lg" className="font-bold" data-testid="kpi-value">
          {formatValue(data.current)}
        </Text>
        <div className="flex items-center space-x-2 mt-1">
          {getChangeIcon()}
          <Text 
            variant="body-sm" 
            className={isPositive ? 'text-green-600' : isNegative ? 'text-red-600' : 'text-gray-500'}
          >
            {isPositive ? '+' : ''}{formatValue(Math.abs(change))} ({isPositive ? '+' : ''}{changePercent.toFixed(1)}%)
          </Text>
          <Text variant="body-sm" className="text-muted-foreground">
            vs last period
          </Text>
        </div>
        {data.target && (
          <Container className="mt-3">
            <Text variant="body-sm" className="text-muted-foreground">
              Target: {formatValue(data.target)}
            </Text>
            <div className="mt-1 h-2 bg-gray-200 rounded-full">
              <div 
                className="h-2 bg-blue-600 rounded-full transition-all duration-300"
                style={{ width: `${Math.min((data.current / data.target) * 100, 100)}%` }}
              />
            </div>
          </Container>
        )}
      </CardContent>
    </Card>
  );
};

export default EnhancedKPICard; 