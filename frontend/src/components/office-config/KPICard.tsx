/**
 * Reusable KPI Card Component
 * Used across office tabs to display key performance indicators
 */
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { cn } from '../../lib/utils';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface KPICardProps {
  title: string;
  value: string | number;
  unit?: string;
  subtitle?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  variant?: 'default' | 'success' | 'warning' | 'destructive';
  className?: string;
  loading?: boolean;
}

export const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  unit,
  subtitle,
  trend,
  trendValue,
  variant = 'default',
  className,
  loading = false
}) => {
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'down':
        return <TrendingDown className="h-4 w-4 text-red-600" />;
      case 'neutral':
        return <Minus className="h-4 w-4 text-gray-500" />;
      default:
        return null;
    }
  };

  const getTrendBadgeVariant = () => {
    switch (trend) {
      case 'up':
        return 'default';  // Green
      case 'down':
        return 'destructive';  // Red
      case 'neutral':
        return 'secondary';  // Gray
      default:
        return 'outline';
    }
  };

  const getCardVariant = () => {
    switch (variant) {
      case 'success':
        return 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950';
      case 'warning':
        return 'border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-950';
      case 'destructive':
        return 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950';
      default:
        return '';
    }
  };

  if (loading) {
    return (
      <Card className={cn("h-full", getCardVariant(), className)}>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {title}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded mb-2"></div>
            {subtitle && <div className="h-4 bg-gray-200 rounded w-2/3"></div>}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn("h-full", getCardVariant(), className)}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center space-x-2">
          <div className="text-2xl font-bold">
            {typeof value === 'number' && !isNaN(value) 
              ? value.toLocaleString() 
              : value}
            {unit && <span className="text-lg font-medium text-muted-foreground ml-1">{unit}</span>}
          </div>
          {trend && trendValue && (
            <Badge variant={getTrendBadgeVariant()} className="flex items-center gap-1">
              {getTrendIcon()}
              <span className="text-xs">{trendValue}</span>
            </Badge>
          )}
        </div>
        {subtitle && (
          <p className="text-xs text-muted-foreground mt-1">
            {subtitle}
          </p>
        )}
      </CardContent>
    </Card>
  );
};