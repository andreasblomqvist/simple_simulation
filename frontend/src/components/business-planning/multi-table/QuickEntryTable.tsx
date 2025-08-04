/**
 * Quick Entry Table - Clean Minimalistic Dark Mode
 * 
 * Compact, readable table with minimal colors and clean design
 * Bulk operations - Focus on readability and modern minimal aesthetics
 */
import React, { useState, useCallback } from 'react';
import { Badge } from '../../ui/badge';
import { Button } from '../../ui/button';
import { Input } from '../../ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../ui/table';
import { cn } from '../../../lib/utils';
import { Zap, Copy, Upload, RotateCcw } from 'lucide-react';
import type { OfficeConfig } from '../../../types/office';

interface QuickEntryTableProps {
  office: OfficeConfig;
  year: number;
  onDataChange: () => void;
}

interface QuickOperation {
  id: string;
  operation: string;
  scope: string;
  value: string;
  applied: boolean;
}

interface BulkEntryData {
  operation: 'fill' | 'copy' | 'apply';
  source: string;
  target: string;
  value: number;
}

// Quick operations for efficient data entry
const quickOperations: QuickOperation[] = [
  {
    id: 'fill-recruitment',
    operation: 'Fill All Recruitment',
    scope: 'All roles, all quarters',
    value: '2 per quarter',
    applied: false
  },
  {
    id: 'fill-churn',
    operation: 'Fill All Churn',
    scope: 'All roles, all quarters',
    value: '1 per quarter',
    applied: false
  },
  {
    id: 'copy-q1',
    operation: 'Copy Q1 to All',
    scope: 'All quarters',
    value: 'Q1 values',
    applied: false
  },
  {
    id: 'apply-growth',
    operation: 'Apply Growth Pattern',
    scope: 'All data',
    value: '3% quarterly increase',
    applied: false
  }
];

export const QuickEntryTable: React.FC<QuickEntryTableProps> = ({
  office,
  year,
  onDataChange
}) => {
  const [operations, setOperations] = useState<QuickOperation[]>(quickOperations);
  const [bulkValues, setBulkValues] = useState({
    recruitment: '2',
    churn: '1',
    salary: '50',
    pricing: '100'
  });

  const handleValueChange = useCallback((field: string, value: string) => {
    setBulkValues(prev => ({ ...prev, [field]: value }));
  }, []);

  const handleApplyOperation = useCallback((operationId: string) => {
    setOperations(prev => 
      prev.map(op => 
        op.id === operationId ? { ...op, applied: true } : op
      )
    );
    onDataChange();
  }, [onDataChange]);

  const handleResetAll = useCallback(() => {
    setOperations(prev => prev.map(op => ({ ...op, applied: false })));
  }, []);

  return (
    <div className="quick-entry-table space-y-4 p-4" style={{ backgroundColor: '#111827' }}>
      {/* Clean Header */}
      <div className="flex items-center justify-between pb-2">
        <div className="flex items-center gap-2">
          <Zap className="h-4 w-4" style={{ color: '#9ca3af' }} />
          <h3 className="text-base font-medium" style={{ color: '#f3f4f6' }}>
            Quick bulk operations and data entry for {office.name} {year}
          </h3>
        </div>
        <Badge variant="outline" className="text-xs" style={{ backgroundColor: '#1f2937', color: '#d1d5db', borderColor: '#4b5563' }}>
          <Zap className="h-3 w-3 mr-1" style={{ color: '#9ca3af' }} />
          Bulk Mode
        </Badge>
      </div>

      {/* Bulk Entry Values - Clean & Minimal */}
      <div className="grid grid-cols-4 gap-3">
        <div className="p-3 rounded-lg" style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
          <label className="text-xs font-medium mb-1 block" style={{ color: '#d1d5db' }}>Recruitment</label>
          <Input
            type="number"
            value={bulkValues.recruitment}
            onChange={(e) => handleValueChange('recruitment', e.target.value)}
            className="h-7 text-xs"
            style={{
              border: '1px solid #374151',
              backgroundColor: '#111827',
              color: '#f3f4f6'
            }}
            min="0"
          />
        </div>
        <div className="p-3 rounded-lg" style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
          <label className="text-xs font-medium mb-1 block" style={{ color: '#d1d5db' }}>Churn</label>
          <Input
            type="number"
            value={bulkValues.churn}
            onChange={(e) => handleValueChange('churn', e.target.value)}
            className="h-7 text-xs"
            style={{
              border: '1px solid #374151',
              backgroundColor: '#111827',
              color: '#f3f4f6'
            }}
            min="0"
          />
        </div>
        <div className="p-3 rounded-lg" style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
          <label className="text-xs font-medium mb-1 block" style={{ color: '#d1d5db' }}>Salary (€k)</label>
          <Input
            type="number"
            value={bulkValues.salary}
            onChange={(e) => handleValueChange('salary', e.target.value)}
            className="h-7 text-xs"
            style={{
              border: '1px solid #374151',
              backgroundColor: '#111827',
              color: '#f3f4f6'
            }}
            min="0"
          />
        </div>
        <div className="p-3 rounded-lg" style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
          <label className="text-xs font-medium mb-1 block" style={{ color: '#d1d5db' }}>Pricing (€/h)</label>
          <Input
            type="number"
            value={bulkValues.pricing}
            onChange={(e) => handleValueChange('pricing', e.target.value)}
            className="h-7 text-xs"
            style={{
              border: '1px solid #374151',
              backgroundColor: '#111827',
              color: '#f3f4f6'
            }}
            min="0"
          />
        </div>
      </div>

      {/* Quick Operations Table - Clean */}
      <div className="rounded-lg overflow-hidden" style={{ border: '1px solid #374151' }}>
        <Table>
          <TableHeader>
            <TableRow style={{ backgroundColor: '#1f2937', borderBottom: '1px solid #374151' }}>
              <TableHead className="text-xs font-medium w-48" style={{ color: '#d1d5db' }}>Operation</TableHead>
              <TableHead className="text-xs font-medium w-32" style={{ color: '#d1d5db' }}>Scope</TableHead>
              <TableHead className="text-xs font-medium w-32" style={{ color: '#d1d5db' }}>Value</TableHead>
              <TableHead className="text-xs font-medium text-center w-20" style={{ color: '#d1d5db' }}>Status</TableHead>
              <TableHead className="text-xs font-medium text-center w-20" style={{ color: '#d1d5db' }}>Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {operations.map((operation) => (
              <TableRow 
                key={operation.id}
                style={{ 
                  backgroundColor: operation.applied ? '#0f172a' : '#111827',
                  borderBottom: '1px solid #374151',
                  transition: 'background-color 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#1f2937';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = operation.applied ? '#0f172a' : '#111827';
                }}
              >
                <TableCell className="text-xs font-medium" style={{ color: '#f3f4f6' }}>
                  {operation.operation}
                </TableCell>
                <TableCell className="text-xs" style={{ color: '#9ca3af' }}>
                  {operation.scope}
                </TableCell>
                <TableCell className="text-xs" style={{ color: '#f3f4f6' }}>
                  {operation.value}
                </TableCell>
                <TableCell className="text-center">
                  <Badge 
                    variant="outline" 
                    className="text-xs px-2 py-0.5"
                    style={{ 
                      backgroundColor: '#374151', 
                      color: '#d1d5db', 
                      borderColor: '#4b5563' 
                    }}
                  >
                    {operation.applied ? 'Applied' : 'Pending'}
                  </Badge>
                </TableCell>
                <TableCell className="text-center">
                  {!operation.applied && (
                    <Button
                      size="sm"
                      onClick={() => handleApplyOperation(operation.id)}
                      className="h-6 px-2 text-xs"
                      style={{
                        backgroundColor: '#3b82f6',
                        color: '#ffffff',
                        border: 'none'
                      }}
                    >
                      Apply
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Clean Action Bar */}
      <div className="flex items-center justify-between pt-2" style={{ borderTop: '1px solid #374151' }}>
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            className="h-7 px-3 text-xs"
            style={{
              border: '1px solid #374151',
              backgroundColor: '#1f2937',
              color: '#d1d5db'
            }}
          >
            <RotateCcw className="h-3 w-3 mr-1" style={{ color: '#9ca3af' }} />
            Reset All
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            className="h-7 px-3 text-xs"
            style={{
              border: '1px solid #374151',
              backgroundColor: '#1f2937',
              color: '#d1d5db'
            }}
          >
            <Copy className="h-3 w-3 mr-1" style={{ color: '#9ca3af' }} />
            Copy Previous Year
          </Button>
        </div>
        
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            className="h-7 px-3 text-xs"
            style={{
              border: '1px solid #374151',
              backgroundColor: '#1f2937',
              color: '#d1d5db'
            }}
          >
            <Upload className="h-3 w-3 mr-1" style={{ color: '#9ca3af' }} />
            Import
          </Button>
          <Button 
            size="sm" 
            className="h-7 px-3 text-xs"
            style={{
              backgroundColor: '#3b82f6',
              color: '#ffffff',
              border: 'none'
            }}
          >
            Save Changes
          </Button>
        </div>
      </div>
    </div>
  );
};