/**
 * Planning Grid Toolbar
 * 
 * Toolbar with actions for the planning grid including save, import/export, etc.
 */
import React from 'react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { 
  Save, 
  RotateCcw, 
  Download, 
  Upload, 
  Copy, 
  Calculator,
  Calendar,
  Settings
} from 'lucide-react';
import type { OfficeConfig } from '../../types/office';

interface PlanningGridToolbarProps {
  office: OfficeConfig;
  year: number;
  onYearChange: (year: number) => void;
  isDirty: boolean;
  onSave: () => void;
  onDiscard: () => void;
  onToggleCalculations: () => void;
  showCalculations: boolean;
}

export const PlanningGridToolbar: React.FC<PlanningGridToolbarProps> = ({
  office,
  year,
  onYearChange,
  isDirty,
  onSave,
  onDiscard,
  onToggleCalculations,
  showCalculations
}) => {
  const currentYear = new Date().getFullYear();
  const availableYears = Array.from({ length: 5 }, (_, i) => currentYear + i - 1);

  return (
    <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg border">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <Calendar className="h-4 w-4" />
          <span className="font-medium">{office.name}</span>
          <Badge variant="outline">{year}</Badge>
        </div>

        {isDirty && (
          <Badge variant="secondary" className="animate-pulse">
            Unsaved changes
          </Badge>
        )}
      </div>

      <div className="flex items-center gap-2">
        {/* Year Selector */}
        <select
          value={year}
          onChange={(e) => onYearChange(parseInt(e.target.value))}
          className="px-3 py-1 border rounded-md bg-background text-sm"
        >
          {availableYears.map(y => (
            <option key={y} value={y}>{y}</option>
          ))}
        </select>

        {/* Actions */}
        <Button
          variant="outline"
          size="sm"
          onClick={onToggleCalculations}
        >
          <Calculator className="h-4 w-4 mr-1" />
          {showCalculations ? 'Hide' : 'Show'} Calculations
        </Button>

        <Button
          variant="outline"
          size="sm"
          disabled
        >
          <Copy className="h-4 w-4 mr-1" />
          Copy Template
        </Button>

        <Button
          variant="outline"
          size="sm"
          disabled
        >
          <Download className="h-4 w-4 mr-1" />
          Export
        </Button>

        <Button
          variant="outline"
          size="sm"
          disabled
        >
          <Upload className="h-4 w-4 mr-1" />
          Import
        </Button>

        {/* Save/Discard */}
        {isDirty && (
          <>
            <Button
              variant="outline"
              size="sm"
              onClick={onDiscard}
            >
              <RotateCcw className="h-4 w-4 mr-1" />
              Discard
            </Button>

            <Button
              size="sm"
              onClick={onSave}
            >
              <Save className="h-4 w-4 mr-1" />
              Save Changes
            </Button>
          </>
        )}
      </div>
    </div>
  );
};