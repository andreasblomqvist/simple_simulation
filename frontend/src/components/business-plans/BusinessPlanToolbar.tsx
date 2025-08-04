/**
 * Toolbar component for business plan table
 * Handles year selection, save/discard actions, and additional controls
 */
import React, { useState } from 'react';
import { ChevronDown, ChevronUp, X, Undo2, Save, MoreHorizontal } from 'lucide-react';
import type { OfficeConfig } from '../../types/office';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { Button } from '../ui/button';
import './BusinessPlanToolbar.css';

interface BusinessPlanToolbarProps {
  office: OfficeConfig;
  year: number;
  onYearChange: (year: number) => void;
  isDirty: boolean;
  onSave: () => Promise<void>;
  onDiscard: () => void;
  loading: boolean;
}

export const BusinessPlanToolbar: React.FC<BusinessPlanToolbarProps> = ({
  office,
  year,
  onYearChange,
  isDirty,
  onSave,
  onDiscard,
  loading
}) => {
  const [saving, setSaving] = useState(false);
  const [showYearPicker, setShowYearPicker] = useState(false);

  // Generate year options (current year ± 5 years)
  const currentYear = new Date().getFullYear();
  const yearOptions = Array.from(
    { length: 11 }, 
    (_, i) => currentYear - 5 + i
  );

  const handleSave = async () => {
    if (!isDirty || saving) return;
    
    setSaving(true);
    try {
      await onSave();
    } catch (error) {
      console.error('Save failed:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleYearSelect = (selectedYear: number) => {
    if (isDirty) {
      const confirmChange = window.confirm(
        'You have unsaved changes. Changing the year will discard them. Continue?'
      );
      if (!confirmChange) {
        setShowYearPicker(false);
        return;
      }
      onDiscard();
    }
    onYearChange(selectedYear);
    setShowYearPicker(false);
  };

  const getStatusMessage = () => {
    if (saving) return 'Saving changes...';
    if (loading) return 'Loading data...';
    if (isDirty) return 'You have unsaved changes';
    return 'All changes saved';
  };

  const getStatusIcon = () => {
    if (saving || loading) return <LoadingSpinner size="small" />;
    if (isDirty) return '⚠️';
    return '✅';
  };

  return (
    <div className="business-plan-toolbar">
      <div className="toolbar-section left">
        <div className="office-info">
          <h2 className="office-name">{office.name}</h2>
          <span className="business-plan-subtitle">Business Plan</span>
        </div>

        <div className="year-selector">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowYearPicker(!showYearPicker)}
            disabled={loading || saving}
            className="year-button"
            icon={showYearPicker ? <ChevronUp /> : <ChevronDown />}
            iconPosition="right"
          >
            <span className="year-label">Year:</span>
            <span className="year-value">{year}</span>
          </Button>

          {showYearPicker && (
            <div className="year-dropdown">
              <div className="year-dropdown-header">
                <span>Select Year</span>
                <Button 
                  variant="ghost"
                  size="icon"
                  onClick={() => setShowYearPicker(false)}
                  className="close-dropdown"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              <div className="year-options">
                {yearOptions.map(yearOption => (
                  <button
                    key={yearOption}
                    className={`year-option ${yearOption === year ? 'selected' : ''}`}
                    onClick={() => handleYearSelect(yearOption)}
                  >
                    {yearOption}
                    {yearOption === currentYear && (
                      <span className="current-year-badge">Current</span>
                    )}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="toolbar-section center">
        <div className="status-display">
          <div className="status-icon">{getStatusIcon()}</div>
          <span className="status-message">{getStatusMessage()}</span>
        </div>
      </div>

      <div className="toolbar-section right">
        <div className="action-buttons">
          {isDirty && (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={onDiscard}
                disabled={saving || loading}
                icon={<Undo2 />}
                iconPosition="left"
                className="discard-button"
              >
                Discard
              </Button>
              
              <Button
                variant="default"
                size="sm"
                onClick={handleSave}
                disabled={saving || loading}
                loading={saving}
                icon={!saving ? <Save /> : undefined}
                iconPosition="left"
                className="save-button"
              >
                {saving ? 'Saving...' : 'Save Changes'}
              </Button>
            </>
          )}

          <div className="toolbar-menu">
            <Button 
              variant="ghost"
              size="icon"
              disabled={loading || saving}
              className="menu-button"
            >
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Year picker overlay */}
      {showYearPicker && (
        <div 
          className="year-picker-overlay"
          onClick={() => setShowYearPicker(false)}
        />
      )}
    </div>
  );
};