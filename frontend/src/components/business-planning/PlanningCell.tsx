/**
 * Planning Cell Component
 * 
 * Individual editable cell for business planning grid
 * Supports inline editing with validation and keyboard navigation
 */
import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { cn } from '../../lib/utils';
import type { MonthlyPlanEntry, StandardRole, StandardLevel } from '../../types/office';

interface PlanningCellProps {
  role: StandardRole;
  level: StandardLevel;
  month: number;
  field: keyof MonthlyPlanEntry;
  value: number;
  onChange: (value: number) => void;
  isSelected?: boolean;
  isEditing?: boolean;
  onSelect?: () => void;
  onEdit?: () => void;
  onFinishEdit?: () => void;
  isDirty?: boolean;
  placeholder?: string;
  min?: number;
  max?: number;
  step?: number;
  type?: 'number' | 'currency' | 'percentage';
}

export const PlanningCell: React.FC<PlanningCellProps> = ({
  role,
  level,
  month,
  field,
  value,
  onChange,
  isSelected = false,
  isEditing = false,
  onSelect,
  onEdit,
  onFinishEdit,
  isDirty = false,
  placeholder,
  min = 0,
  max,
  step,
  type = 'number'
}) => {
  const [localValue, setLocalValue] = useState(value.toString());
  const inputRef = useRef<HTMLInputElement>(null);

  // Update local value when prop changes
  useEffect(() => {
    if (!isEditing) {
      setLocalValue(value.toString());
    }
  }, [value, isEditing]);

  // Focus input when editing starts
  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const handleClick = useCallback(() => {
    onSelect?.();
  }, [onSelect]);

  const handleDoubleClick = useCallback(() => {
    onEdit?.();
  }, [onEdit]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (!isEditing) {
      if (e.key === 'Enter' || e.key === 'F2' || e.key === ' ') {
        e.preventDefault();
        onEdit?.();
      }
      return;
    }

    if (e.key === 'Enter' || e.key === 'Tab') {
      e.preventDefault();
      handleFinishEdit();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      setLocalValue(value.toString());
      onFinishEdit?.();
    }
  }, [isEditing, onEdit, onFinishEdit, value]);

  const handleFinishEdit = useCallback(() => {
    const numericValue = parseFloat(localValue);
    if (!isNaN(numericValue) && numericValue >= min && (max === undefined || numericValue <= max)) {
      onChange(numericValue);
    } else {
      setLocalValue(value.toString());
    }
    onFinishEdit?.();
  }, [localValue, onChange, onFinishEdit, value, min, max]);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setLocalValue(e.target.value);
  }, []);

  const handleInputBlur = useCallback(() => {
    if (isEditing) {
      handleFinishEdit();
    }
  }, [isEditing, handleFinishEdit]);

  const formatDisplayValue = useCallback((val: number): string => {
    switch (type) {
      case 'currency':
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'EUR',
          minimumFractionDigits: 0,
          maximumFractionDigits: 0
        }).format(val);
      
      case 'percentage':
        return `${(val * 100).toFixed(1)}%`;
      
      default:
        if (val === 0) return '0';
        if (val >= 1000) {
          return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
          }).format(val);
        }
        return val.toString();
    }
  }, [type]);

  const getCellColorClass = useCallback(() => {
    if (isDirty) return 'bg-yellow-50 border-yellow-200 dark:bg-yellow-950/20 dark:border-yellow-800';
    if (isSelected) return 'bg-blue-50 border-blue-200 dark:bg-blue-950/20 dark:border-blue-800';
    if (value > 0) return 'bg-green-50 border-green-200 dark:bg-green-950/20 dark:border-green-800';
    return 'hover:bg-muted/50';
  }, [isDirty, isSelected, value]);

  const getFieldIcon = useCallback(() => {
    switch (field) {
      case 'recruitment':
        return '👥';
      case 'churn':
        return '👋';
      case 'price':
        return '💰';
      case 'utr':
        return '⏰';
      case 'salary':
        return '💳';
      default:
        return '';
    }
  }, [field]);

  if (isEditing) {
    return (
      <td className={cn(
        'p-1 border-r relative',
        'bg-white dark:bg-background',
        'border-2 border-blue-500'
      )}>
        <Input
          ref={inputRef}
          type="number"
          value={localValue}
          onChange={handleInputChange}
          onBlur={handleInputBlur}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          min={min}
          max={max}
          step={step}
          className="w-full h-8 text-sm border-none p-1 focus:ring-0"
        />
      </td>
    );
  }

  return (
    <td 
      className={cn(
        'p-2 border-r cursor-pointer transition-colors',
        'hover:bg-muted/70',
        getCellColorClass(),
        'min-w-[80px] text-center'
      )}
      onClick={handleClick}
      onDoubleClick={handleDoubleClick}
      onKeyDown={handleKeyDown}
      tabIndex={0}
      role="gridcell"
      aria-label={`${field} for ${role} ${level} in month ${month}: ${formatDisplayValue(value)}`}
    >
      <div className="flex flex-col items-center gap-1">
        <div className="flex items-center gap-1">
          <span className="text-xs opacity-60">{getFieldIcon()}</span>
          <span className="font-medium text-sm">
            {formatDisplayValue(value)}
          </span>
        </div>
        
        {isDirty && (
          <Badge variant="secondary" className="h-4 px-1 text-xs">
            Modified
          </Badge>
        )}
      </div>
    </td>
  );
};