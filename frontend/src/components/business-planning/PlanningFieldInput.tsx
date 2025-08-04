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

interface FieldConfig {
  min: number;
  max?: number;
  step: number;
  format: (val: number) => string;
  parse: (str: string) => number;
  bgColor: string;
  suffix?: string;
}

const FIELD_CONFIGS: Record<'recruitment' | 'churn' | 'price' | 'utr' | 'salary', FieldConfig> = {
  recruitment: {
    min: 0,
    step: 1,
    format: (val: number) => Math.round(val).toString(),
    parse: (str: string) => parseInt(str) || 0,
    bgColor: '' // Will use inline styles
  },
  churn: {
    min: 0,
    step: 1,
    format: (val: number) => Math.round(val).toString(),
    parse: (str: string) => parseInt(str) || 0,
    bgColor: '' // Will use inline styles
  },
  price: {
    min: 0,
    step: 1,
    format: (val: number) => Math.round(val).toString(),
    parse: (str: string) => parseFloat(str) || 0,
    bgColor: '' // Will use inline styles
  },
  utr: {
    min: 0,
    max: 1,
    step: 0.01,
    format: (val: number) => (val * 100).toFixed(1),
    parse: (str: string) => (parseFloat(str) || 0) / 100,
    bgColor: '', // Will use inline styles
    suffix: '%'
  },
  salary: {
    min: 0,
    step: 100,
    format: (val: number) => Math.round(val).toString(),
    parse: (str: string) => parseFloat(str) || 0,
    bgColor: '' // Will use inline styles
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

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.currentTarget.blur();
    }
  };

  // Get field-specific focus colors
  const getFocusStyle = (field: string) => {
    switch (field) {
      case 'recruitment':
        return { backgroundColor: isFocused ? '#065f46' : '#1f2937' }; // Green focus
      case 'churn':
        return { backgroundColor: isFocused ? '#7f1d1d' : '#1f2937' }; // Red focus
      case 'price':
        return { backgroundColor: isFocused ? '#1e3a8a' : '#1f2937' }; // Blue focus
      case 'utr':
        return { backgroundColor: isFocused ? '#581c87' : '#1f2937' }; // Purple focus
      case 'salary':
        return { backgroundColor: isFocused ? '#9a3412' : '#1f2937' }; // Orange focus
      default:
        return { backgroundColor: '#1f2937' };
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
        style={{
          height: '32px',
          fontSize: '12px',
          textAlign: 'center',
          border: isFocused ? '2px solid #3b82f6' : '1px solid #374151',
          color: '#f3f4f6',
          transition: 'all 0.2s ease',
          ...getFocusStyle(field),
          ...(isDirty && {
            backgroundColor: '#451a03',
            border: '1px solid #f59e0b'
          })
        }}
        className={cn(
          "transition-colors",
          className
        )}
      />
      {config.suffix && !isFocused && (
        <span 
          className="absolute right-2 top-1/2 -translate-y-1/2 text-xs pointer-events-none"
          style={{ 
            color: '#9ca3af',
            transform: 'translateY(-50%)' 
          }}
        >
          {config.suffix}
        </span>
      )}
    </div>
  );
};