/**
 * Import/Export Tools Component
 * 
 * Tools for importing and exporting business plan data
 */
import React from 'react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Download, Upload, FileSpreadsheet, FileText } from 'lucide-react';
import type { OfficeConfig } from '../../types/office';

interface ImportExportToolsProps {
  selectedOffice: OfficeConfig | undefined;
  selectedYear: number;
}

export const ImportExportTools: React.FC<ImportExportToolsProps> = ({
  selectedOffice,
  selectedYear
}) => {
  return (
    <div className="flex items-center gap-2">
      <Button 
        variant="outline" 
        size="sm"
        disabled
      >
        <Download className="h-4 w-4 mr-2" />
        Export Excel
      </Button>
      
      <Button 
        variant="outline" 
        size="sm"
        disabled
      >
        <Upload className="h-4 w-4 mr-2" />
        Import Excel
      </Button>

      <Badge variant="secondary" className="text-xs">
        Coming Soon
      </Badge>
    </div>
  );
};