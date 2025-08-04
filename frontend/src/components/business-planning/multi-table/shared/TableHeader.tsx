/**
 * Modern Shared Table Header Component
 * 
 * Enhanced header structure for all multi-table planning tables
 * Features modern styling, dark/light mode support, and premium aesthetics
 */
import React from 'react';
import { Badge } from '../../../ui/badge';
import { Button } from '../../../ui/button';
import { 
  MoreHorizontal, 
  Filter, 
  Download,
  Settings,
  ChevronDown
} from 'lucide-react';
import { cn } from '../../../../lib/utils';

interface TableHeaderProps {
  title: string;
  subtitle?: string;
  itemCount?: number;
  showFilters?: boolean;
  showExport?: boolean;
  showSettings?: boolean;
  children?: React.ReactNode;
}

export const TableHeader: React.FC<TableHeaderProps> = ({
  title,
  subtitle,
  itemCount,
  showFilters = true,
  showExport = true,
  showSettings = false,
  children
}) => {
  return (
    <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-gray-50 to-gray-100/50 dark:from-gray-800 dark:to-gray-900/50">
      <div className="flex items-center gap-4">
        <div className="space-y-1">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{title}</h3>
          {subtitle && (
            <p className="text-sm text-gray-600 dark:text-gray-400">{subtitle}</p>
          )}
        </div>
        {itemCount !== undefined && (
          <Badge className="h-6 px-2.5 bg-blue-100 hover:bg-blue-200 text-blue-700 border-blue-300 dark:bg-blue-900 dark:hover:bg-blue-800 dark:text-blue-300 dark:border-blue-700">
            <span className="text-xs font-medium">{itemCount} items</span>
          </Badge>
        )}
      </div>

      <div className="flex items-center gap-2">
        {children}
        
        {showFilters && (
          <Button 
            variant="ghost" 
            size="sm"
            className="h-8 px-3 text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-100 dark:hover:bg-gray-800"
          >
            <Filter className="h-4 w-4 mr-1.5" />
            <span className="text-xs font-medium">Filter</span>
            <ChevronDown className="h-3 w-3 ml-1" />
          </Button>
        )}
        
        {showExport && (
          <Button 
            variant="ghost" 
            size="sm"
            className="h-8 px-3 text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-100 dark:hover:bg-gray-800"
          >
            <Download className="h-4 w-4 mr-1.5" />
            <span className="text-xs font-medium">Export</span>
          </Button>
        )}
        
        {showSettings && (
          <Button 
            variant="ghost" 
            size="sm"
            className="h-8 px-3 text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-100 dark:hover:bg-gray-800"
          >
            <Settings className="h-4 w-4 mr-1.5" />
            <span className="text-xs font-medium">Settings</span>
          </Button>
        )}
        
        <Button 
          variant="ghost" 
          size="sm"
          className="h-8 w-8 p-0 text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-100 dark:hover:bg-gray-800"
        >
          <MoreHorizontal className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
};