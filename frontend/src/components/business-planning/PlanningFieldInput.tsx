/**
 * Planning Field Input Component
 * 
 * Specialized input component for business planning fields
 * with proper formatting and validation
 */
import React, { useState, useEffect } from 'react';
import { Input } from '../ui/input';
import { cn } from '../../lib/utils';

interface PlanningFieldInputProps {
  value: number;
  onChange: (value: number) => void;
  field: 'recruitment' | 'churn' | 'price' | 'utr' | 'salary';
  isDirty?: boolean;
  className?: string;
}

const FIELD_CONFIGS = {
  recruitment: {
    min: 0,
    step: 1,
    format: (val: number) => val.toString(),
    parse: (str: string) => parseInt(str) || 0,
    bgColor: 'focus:bg-green-50 dark:focus:bg-green-950/20'
  },
  churn: {
    min: 0,
    step: 1,
    format: (val: number) => val.toString(),
    parse: (str: string) => parseInt(str) || 0,
    bgColor: 'focus:bg-red-50 dark:focus:bg-red-950/20'
  },
  price: {
    min: 0,
    step: 1,
    format: (val: number) => val.toString(),
    parse: (str: string) => parseFloat(str) || 0,
    bgColor: 'focus:bg-blue-50 dark:focus:bg-blue-950/20'
  },
  utr: {
    min: 0,
    max: 1,
    step: 0.01,
    format: (val: number) => (val * 100).toFixed(0),
    parse: (str: string) => (parseFloat(str) || 0) / 100,
    bgColor: 'focus:bg-purple-50 dark:focus:bg-purple-950/20',
    suffix: '%'
  },
  salary: {
    min: 0,
    step: 100,
    format: (val: number) => Math.round(val).toString(),
    parse: (str: string) => parseFloat(str) || 0,
    bgColor: 'focus:bg-orange-50 dark:focus:bg-orange-950/20'
  }
};

export const PlanningFieldInput: React.FC<PlanningFieldInputProps> = ({
  value,
  onChange,
  field,
  isDirty = false,
  className
}) => {
  const config = FIELD_CONFIGS[field];
  const [displayValue, setDisplayValue] = useState(config.format(value));
  const [isFocused, setIsFocused] = useState(false);

  // Update display value when prop changes (and not focused)
  useEffect(() => {
    if (!isFocused) {
      setDisplayValue(config.format(value));
    }
  }, [value, config, isFocused]);

  const handleFocus = () => {
    setIsFocused(true);
    // Show raw value when focused (for UTR, show decimal)
    if (field === 'utr') {
      setDisplayValue(value.toFixed(2));
    }
  };

  const handleBlur = () => {
    setIsFocused(false);
    const numericValue = config.parse(displayValue);
    
    // Validate range
    let validValue = numericValue;
    if (config.min !== undefined && validValue < config.min) {
      validValue = config.min;
    }
    if (config.max !== undefined && validValue > config.max) {
      validValue = config.max;
    }
    
    onChange(validValue);
    setDisplayValue(config.format(validValue));
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setDisplayValue(e.target.value);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.currentTarget.blur();
    }
  };

  return (
    <div className="relative">
      <Input
        type="number"
        value={displayValue}
        onChange={handleChange}
        onFocus={handleFocus}
        onBlur={handleBlur}
        onKeyDown={handleKeyDown}
        min={config.min}
        max={config.max}
        step={config.step}
        placeholder="0"
        className={cn(
          "h-8 text-xs text-center border border-transparent bg-transparent",
          "hover:bg-muted/30 focus:bg-background focus:border-primary transition-colors",
          "focus:ring-2 focus:ring-primary/20",
          config.bgColor,
          isDirty && "bg-yellow-100 dark:bg-yellow-950/30 ring-1 ring-yellow-400",
          className
        )}
      />
      {config.suffix && !isFocused && (
        <span className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-muted-foreground pointer-events-none">
          {config.suffix}
        </span>
      )}
    </div>
  );
};