/**
 * Reusable Cell Input Component
 * 
 * Handles input validation, formatting, and interaction states
 */
import React, { useState, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Input } from '../../../ui/input';
import { Badge } from '../../../ui/badge';
import { AnimatedInput } from '../../../ui/animated-input';
import { cn } from '../../../../lib/utils';
import { CheckCircle, AlertTriangle, TrendingUp, TrendingDown } from 'lucide-react';

interface CellInputProps {
  value: number;
  onChange: (value: number) => void;
  type?: 'number' | 'currency' | 'percentage';
  min?: number;
  max?: number;
  step?: number;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  showValidation?: boolean;
  showTrend?: boolean;
  previousValue?: number;
  suggestions?: number[];
  formatValue?: (value: number) => string;
  parseValue?: (value: string) => number;
}

export const CellInput: React.FC<CellInputProps> = ({
  value,
  onChange,
  type = 'number',
  min = 0,
  max,
  step = 1,
  placeholder,
  disabled = false,
  className,
  showValidation = false,
  showTrend = false,
  previousValue,
  suggestions = [],
  formatValue,
  parseValue
}) => {
  const [localValue, setLocalValue] = useState<string>('');
  const [isFocused, setIsFocused] = useState(false);
  const [isValid, setIsValid] = useState(true);
  const [showCelebration, setShowCelebration] = useState(false);

  // Format value for display
  const formatDisplayValue = useCallback((num: number): string => {
    if (formatValue) {
      return formatValue(num);
    }

    switch (type) {
      case 'currency':
        return `€${num.toLocaleString()}`;
      case 'percentage':
        return `${(num * 100).toFixed(1)}%`;
      default:
        return num.toString();
    }
  }, [type, formatValue]);

  // Parse string value to number
  const parseStringValue = useCallback((str: string): number => {
    if (parseValue) {
      return parseValue(str);
    }

    // Remove currency symbols and formatting
    const cleaned = str.replace(/[€,%\s]/g, '');
    const parsed = parseFloat(cleaned);
    
    if (type === 'percentage') {
      return parsed / 100;
    }
    
    return isNaN(parsed) ? 0 : parsed;
  }, [type, parseValue]);

  // Update local value when external value changes
  useEffect(() => {
    if (!isFocused) {
      setLocalValue(value.toString());
    }
  }, [value, isFocused]);

  // Initialize local value
  useEffect(() => {
    setLocalValue(value.toString());
  }, []);

  const handleFocus = useCallback(() => {
    setIsFocused(true);
    setLocalValue(value.toString());
  }, [value]);

  const handleBlur = useCallback(() => {
    setIsFocused(false);
    const parsed = parseStringValue(localValue);
    
    // Validate against min/max
    let validatedValue = parsed;
    if (min !== undefined && parsed < min) validatedValue = min;
    if (max !== undefined && parsed > max) validatedValue = max;
    
    setIsValid(validatedValue === parsed);
    onChange(validatedValue);
    setLocalValue(validatedValue.toString());
  }, [localValue, parseStringValue, min, max, onChange]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setLocalValue(e.target.value);
  }, []);

  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.currentTarget.blur();
    }
  }, []);

  // Calculate trend
  const trend = showTrend && previousValue !== undefined 
    ? value > previousValue ? 'up' : value < previousValue ? 'down' : 'stable'
    : null;

  // Get validation state
  const validationState = showValidation 
    ? isValid && value > 0 ? 'valid' : 'warning'
    : null;

  return (
    <div className={cn('relative group', className)}>
      <Input
        value={isFocused ? localValue : formatDisplayValue(value)}
        onChange={handleChange}
        onFocus={handleFocus}
        onBlur={handleBlur}
        onKeyDown={handleKeyDown}
        type={isFocused ? 'text' : 'text'}
        step={step}
        min={min}
        max={max}
        placeholder={placeholder}
        disabled={disabled}
        className={cn(
          'h-9 px-3 text-center text-sm font-medium rounded-lg transition-all duration-200',
          'border-gray-200 dark:border-gray-700',
          'bg-white dark:bg-gray-900',
          'text-gray-900 dark:text-gray-100',
          'hover:border-gray-300 dark:hover:border-gray-600',
          'focus:border-blue-500 dark:focus:border-blue-400',
          'focus:ring-2 focus:ring-blue-500/20 dark:focus:ring-blue-400/20',
          'placeholder:text-gray-400 dark:placeholder:text-gray-500',
          validationState === 'valid' && 'border-emerald-300 dark:border-emerald-600 bg-emerald-50/50 dark:bg-emerald-950/30',
          validationState === 'warning' && 'border-amber-300 dark:border-amber-600 bg-amber-50/50 dark:bg-amber-950/30',
          !isValid && 'border-red-300 dark:border-red-600 bg-red-50/50 dark:bg-red-950/30',
          disabled && 'opacity-50 cursor-not-allowed bg-gray-100 dark:bg-gray-800'
        )}
      />

      {/* Enhanced Validation indicator */}
      {showValidation && !isFocused && (
        <div className="absolute -top-1.5 -right-1.5 z-10">
          {validationState === 'valid' && (
            <div className="w-4 h-4 rounded-full bg-emerald-500 dark:bg-emerald-400 flex items-center justify-center shadow-sm">
              <CheckCircle className="h-2.5 w-2.5 text-white" />
            </div>
          )}
          {validationState === 'warning' && (
            <div className="w-4 h-4 rounded-full bg-amber-500 dark:bg-amber-400 flex items-center justify-center shadow-sm">
              <AlertTriangle className="h-2.5 w-2.5 text-white" />
            </div>
          )}
        </div>
      )}

      {/* Enhanced Trend indicator */}
      {showTrend && trend && trend !== 'stable' && !isFocused && (
        <div className="absolute -bottom-1.5 -right-1.5 z-10">
          {trend === 'up' && (
            <div className="w-4 h-4 rounded-full bg-emerald-500 dark:bg-emerald-400 flex items-center justify-center shadow-sm">
              <TrendingUp className="h-2.5 w-2.5 text-white" />
            </div>
          )}
          {trend === 'down' && (
            <div className="w-4 h-4 rounded-full bg-red-500 dark:bg-red-400 flex items-center justify-center shadow-sm">
              <TrendingDown className="h-2.5 w-2.5 text-white" />
            </div>
          )}
        </div>
      )}

      {/* Enhanced Suggestions tooltip */}
      {suggestions.length > 0 && isFocused && (
        <div className="absolute top-full left-0 right-0 mt-2 p-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg z-20">
          <div className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">Suggestions:</div>
          <div className="flex gap-2 flex-wrap">
            {suggestions.slice(0, 3).map((suggestion, index) => (
              <Badge
                key={index}
                variant="outline"
                className="cursor-pointer text-xs px-2 py-1 rounded-lg border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                onClick={() => {
                  onChange(suggestion);
                  setLocalValue(suggestion.toString());
                }}
              >
                {formatDisplayValue(suggestion)}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Celebration Effect */}
      <AnimatePresence>
        {showCelebration && (
          <motion.div
            className="absolute inset-0 pointer-events-none flex items-center justify-center"
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
          >
            <div className="text-green-500 text-sm">✓</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};