/**
 * Table Switcher Component
 * 
 * Navigation component for switching between different table views
 * Provides context and progress information
 */
import React from 'react';
import { Badge } from '../../ui/badge';
import { Button } from '../../ui/button';
import { Progress } from '../../ui/progress';
import { cn } from '../../../lib/utils';
import { 
  Users, 
  DollarSign, 
  BarChart3, 
  Zap,
  ChevronLeft,
  ChevronRight,
  MoreHorizontal
} from 'lucide-react';

interface TableSwitcherProps {
  activeTable: string;
  onTableChange: (table: string) => void;
  progress?: { [key: string]: number };
  className?: string;
}

interface TableConfig {
  key: string;
  label: string;
  shortLabel: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
  color: string;
}

const tables: TableConfig[] = [
  {
    key: 'workforce',
    label: 'Workforce Planning',
    shortLabel: 'Workforce',
    icon: Users,
    description: 'Recruitment and churn planning',
    color: 'blue'
  },
  {
    key: 'financial',
    label: 'Financial Planning',
    shortLabel: 'Financial',
    icon: DollarSign,
    description: 'Salary, price, and UTR planning',
    color: 'green'
  },
  {
    key: 'overview',
    label: 'Monthly Overview',
    shortLabel: 'Overview',
    icon: BarChart3,
    description: 'Summary and validation',
    color: 'purple'
  },
  {
    key: 'quick-entry',
    label: 'Quick Entry',
    shortLabel: 'Quick',
    icon: Zap,
    description: 'Bulk operations and patterns',
    color: 'amber'
  }
];

export const TableSwitcher: React.FC<TableSwitcherProps> = ({
  activeTable,
  onTableChange,
  progress = {},
  className
}) => {
  const activeIndex = tables.findIndex(table => table.key === activeTable);
  
  const handlePrevious = () => {
    if (activeIndex > 0) {
      onTableChange(tables[activeIndex - 1].key);
    }
  };

  const handleNext = () => {
    if (activeIndex < tables.length - 1) {
      onTableChange(tables[activeIndex + 1].key);
    }
  };

  const getColorClasses = (color: string, active: boolean) => {
    const baseClasses = active ? 'border-2' : 'border';
    
    switch (color) {
      case 'blue':
        return cn(
          baseClasses,
          active 
            ? 'border-blue-500 bg-blue-50 text-blue-700' 
            : 'border-blue-200 hover:border-blue-300 hover:bg-blue-50/50'
        );
      case 'green':
        return cn(
          baseClasses,
          active 
            ? 'border-green-500 bg-green-50 text-green-700' 
            : 'border-green-200 hover:border-green-300 hover:bg-green-50/50'
        );
      case 'purple':
        return cn(
          baseClasses,
          active 
            ? 'border-purple-500 bg-purple-50 text-purple-700' 
            : 'border-purple-200 hover:border-purple-300 hover:bg-purple-50/50'
        );
      case 'amber':
        return cn(
          baseClasses,
          active 
            ? 'border-amber-500 bg-amber-50 text-amber-700' 
            : 'border-amber-200 hover:border-amber-300 hover:bg-amber-50/50'
        );
      default:
        return cn(
          baseClasses,
          active 
            ? 'border-gray-500 bg-gray-50 text-gray-700' 
            : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50/50'
        );
    }
  };

  return (
    <div className={cn('table-switcher', className)}>
      {/* Navigation Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handlePrevious}
            disabled={activeIndex === 0}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          
          <span className="text-sm text-muted-foreground">
            {activeIndex + 1} of {tables.length}
          </span>
          
          <Button
            variant="outline"
            size="sm"
            onClick={handleNext}
            disabled={activeIndex === tables.length - 1}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>

        <Button variant="ghost" size="sm">
          <MoreHorizontal className="h-4 w-4" />
        </Button>
      </div>

      {/* Table Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
        {tables.map((table) => {
          const Icon = table.icon;
          const isActive = table.key === activeTable;
          const progressValue = progress[table.key] || 0;

          return (
            <div
              key={table.key}
              className={cn(
                'p-4 rounded-lg cursor-pointer transition-all',
                getColorClasses(table.color, isActive)
              )}
              onClick={() => onTableChange(table.key)}
            >
              <div className="space-y-3">
                {/* Header */}
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <Icon className="h-5 w-5" />
                    <span className="font-medium text-sm">{table.shortLabel}</span>
                  </div>
                  {isActive && (
                    <Badge variant="secondary" className="text-xs">
                      Active
                    </Badge>
                  )}
                </div>

                {/* Description */}
                <p className="text-xs text-muted-foreground">
                  {table.description}
                </p>

                {/* Progress */}
                {progressValue > 0 && (
                  <div className="space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">Progress</span>
                      <span className="text-xs font-medium">{progressValue}%</span>
                    </div>
                    <Progress value={progressValue} className="h-1" />
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Active Table Details */}
      {activeIndex >= 0 && (
        <div className="mt-4 p-3 bg-muted/30 rounded-lg">
          <div className="flex items-center gap-2 mb-1">
            {React.createElement(tables[activeIndex].icon, { className: "h-4 w-4" })}
            <span className="font-medium text-sm">{tables[activeIndex].label}</span>
          </div>
          <p className="text-xs text-muted-foreground">
            {tables[activeIndex].description}
          </p>
        </div>
      )}
    </div>
  );
};