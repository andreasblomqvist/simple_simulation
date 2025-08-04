/**
 * Individual cell component for business plan table
 * Handles 5-parameter editing (recruitment, churn, price, UTR, salary)
 */
import React, { useState, useRef, useEffect } from 'react';
import { MonthlyPlanEntry } from '../../types/office';
import { Button } from '../ui/button';
import './BusinessPlanCell.css';

interface BusinessPlanCellProps {
  data: MonthlyPlanEntry & { month: number; year: number };
  isSelected: boolean;
  isEditing: boolean;
  hasChanges: boolean;
  onSelect: () => void;
  onEdit: () => void;
  onUpdate: (field: keyof MonthlyPlanEntry, value: number) => void;
  onFinishEdit: () => void;
}

type EditField = 'recruitment' | 'churn' | 'price' | 'utr' | 'salary';

const FIELD_CONFIGS: Record<EditField, { label: string; unit: string; min: number; max: number; step: number; }> = {
  recruitment: { label: 'Recruitment', unit: 'people', min: 0, max: 999, step: 1 },
  churn: { label: 'Churn', unit: 'people', min: 0, max: 999, step: 1 },
  price: { label: 'Price', unit: '$/hr', min: 0, max: 9999, step: 1 },
  utr: { label: 'UTR', unit: '%', min: 0, max: 1, step: 0.01 },
  salary: { label: 'Salary', unit: '$/month', min: 0, max: 99999, step: 100 }
};

const FIELD_ORDER: EditField[] = ['recruitment', 'churn', 'price', 'utr', 'salary'];

export const BusinessPlanCell: React.FC<BusinessPlanCellProps> = ({
  data,
  isSelected,
  isEditing,
  hasChanges,
  onSelect,
  onEdit,
  onUpdate,
  onFinishEdit
}) => {
  const [editingField, setEditingField] = useState<EditField>('recruitment');
  const [tempValues, setTempValues] = useState<Partial<MonthlyPlanEntry>>({});
  const cellRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Initialize temp values when editing starts
  useEffect(() => {
    if (isEditing) {
      setTempValues({
        recruitment: data.recruitment,
        churn: data.churn,
        price: data.price,
        utr: data.utr,
        salary: data.salary
      });
      setEditingField('recruitment');
    }
  }, [isEditing, data]);

  // Focus input when editing starts
  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing, editingField]);

  // Scroll to cell when selected
  useEffect(() => {
    if (isSelected && cellRef.current) {
      cellRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
        inline: 'nearest'
      });
    }
  }, [isSelected]);

  const handleClick = () => {
    onSelect();
    if (isSelected) {
      onEdit();
    }
  };

  const handleDoubleClick = () => {
    if (!isEditing) {
      onEdit();
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (!isEditing) return;

    switch (event.key) {
      case 'Tab':
        event.preventDefault();
        const currentIndex = FIELD_ORDER.indexOf(editingField);
        const nextIndex = event.shiftKey 
          ? (currentIndex - 1 + FIELD_ORDER.length) % FIELD_ORDER.length
          : (currentIndex + 1) % FIELD_ORDER.length;
        setEditingField(FIELD_ORDER[nextIndex]);
        break;
      
      case 'Enter':
        event.preventDefault();
        saveChanges();
        onFinishEdit();
        break;
      
      case 'Escape':
        event.preventDefault();
        setTempValues({});
        onFinishEdit();
        break;
    }
  };

  const handleInputChange = (value: string) => {
    const config = FIELD_CONFIGS[editingField];
    let numValue = parseFloat(value) || 0;
    
    // Apply constraints
    numValue = Math.max(config.min, Math.min(config.max, numValue));
    
    setTempValues(prev => ({
      ...prev,
      [editingField]: numValue
    }));
  };

  const saveChanges = () => {
    Object.entries(tempValues).forEach(([field, value]) => {
      if (value !== undefined && value !== data[field as EditField]) {
        onUpdate(field as EditField, value);
      }
    });
  };

  const handleBlur = () => {
    saveChanges();
    onFinishEdit();
  };

  const formatValue = (field: EditField, value: number): string => {
    const config = FIELD_CONFIGS[field];
    
    switch (field) {
      case 'recruitment':
      case 'churn':
        return value.toString();
      case 'price':
      case 'salary':
        return `$${value.toLocaleString()}`;
      case 'utr':
        return `${(value * 100).toFixed(0)}%`;
      default:
        return value.toString();
    }
  };

  const getDisplayValue = (field: EditField): number => {
    return isEditing ? (tempValues[field] ?? data[field]) : data[field];
  };

  const getCellSummary = () => {
    const recruitment = getDisplayValue('recruitment');
    const churn = getDisplayValue('churn');
    const netChange = recruitment - churn;
    
    return {
      netChange,
      revenue: getDisplayValue('price') * getDisplayValue('utr') * 160, // 160 hours/month
      cost: getDisplayValue('salary')
    };
  };

  const summary = getCellSummary();

  if (isEditing) {
    const config = FIELD_CONFIGS[editingField];
    const currentValue: number = tempValues[editingField] ?? data[editingField];
    
    return (
      <div
        ref={cellRef}
        className={`business-plan-cell editing ${hasChanges ? 'has-changes' : ''}`}
        onKeyDown={handleKeyDown}
      >
        <div className="cell-edit-mode">
          <div className="edit-header">
            <span className="edit-label">{config.label}</span>
            <span className="edit-unit">{config.unit}</span>
          </div>
          
          <input
            ref={inputRef}
            type="number"
            value={editingField === 'utr' ? (currentValue * 100).toFixed(0) : currentValue}
            onChange={(e) => {
              const value = editingField === 'utr' 
                ? (parseFloat(e.target.value) / 100).toString()
                : e.target.value;
              handleInputChange(value);
            }}
            onBlur={handleBlur}
            min={editingField === 'utr' ? config.min * 100 : config.min}
            max={editingField === 'utr' ? config.max * 100 : config.max}
            step={editingField === 'utr' ? config.step * 100 : config.step}
            className="edit-input"
          />
          
          <div className="field-tabs">
            {FIELD_ORDER.map(field => (
              <Button
                key={field}
                variant={field === editingField ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setEditingField(field)}
                className={`field-tab ${field === editingField ? 'active' : ''}`}
              >
                {field.charAt(0).toUpperCase()}
              </Button>
            ))}
          </div>
          
          <div className="edit-help">
            Tab: Next field • Enter: Save • Esc: Cancel
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={cellRef}
      className={`business-plan-cell ${isSelected ? 'selected' : ''} ${hasChanges ? 'has-changes' : ''}`}
      onClick={handleClick}
      onDoubleClick={handleDoubleClick}
      tabIndex={0}
    >
      <div className="cell-content">
        {/* Primary metrics */}
        <div className="primary-metrics">
          <div className="metric recruitment">
            <span className="metric-label">R:</span>
            <span className="metric-value">{data.recruitment}</span>
          </div>
          <div className="metric churn">
            <span className="metric-label">C:</span>
            <span className="metric-value">{data.churn}</span>
          </div>
          <div className={`metric net-change ${summary.netChange >= 0 ? 'positive' : 'negative'}`}>
            <span className="metric-label">N:</span>
            <span className="metric-value">{summary.netChange > 0 ? '+' : ''}{summary.netChange}</span>
          </div>
        </div>

        {/* Secondary metrics */}
        <div className="secondary-metrics">
          <div className="metric price">
            <span className="metric-value">${data.price}</span>
          </div>
          <div className="metric utr">
            <span className="metric-value">{(data.utr * 100).toFixed(0)}%</span>
          </div>
          <div className="metric salary">
            <span className="metric-value">${(data.salary / 1000).toFixed(0)}k</span>
          </div>
        </div>

        {/* Financial summary */}
        <div className="financial-summary">
          <div className="revenue">
            <span className="summary-label">Rev:</span>
            <span className="summary-value">${(summary.revenue / 1000).toFixed(0)}k</span>
          </div>
          <div className="profit">
            <span className="summary-label">Profit:</span>
            <span className={`summary-value ${summary.revenue - summary.cost >= 0 ? 'positive' : 'negative'}`}>
              ${((summary.revenue - summary.cost) / 1000).toFixed(0)}k
            </span>
          </div>
        </div>
      </div>

      {hasChanges && <div className="change-indicator" />}
    </div>
  );
};