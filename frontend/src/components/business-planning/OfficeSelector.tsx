/**
 * Office Selector Component
 * 
 * Dropdown selector for choosing which office to plan for
 * Includes search and multi-office management features
 */
import React, { useState, useMemo } from 'react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
// import {
//   Popover,
//   PopoverContent,
//   PopoverTrigger,
// } from '../ui/popover';
import { 
  Building2, 
  Search, 
  Check, 
  MapPin,
  Users,
  TrendingUp
} from 'lucide-react';
import { cn } from '../../lib/utils';
import type { OfficeConfig } from '../../types/office';

interface OfficeSelectorProps {
  offices: OfficeConfig[];
  selectedOfficeId: string | null;
  onOfficeChange: (officeId: string) => void;
  disabled?: boolean;
  showStats?: boolean;
  allowMultiple?: boolean;
  selectedOfficeIds?: string[];
  onMultipleOfficeChange?: (officeIds: string[]) => void;
}

export const OfficeSelector: React.FC<OfficeSelectorProps> = ({
  offices,
  selectedOfficeId,
  onOfficeChange,
  disabled = false,
  showStats = true,
  allowMultiple = false,
  selectedOfficeIds = [],
  onMultipleOfficeChange
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [open, setOpen] = useState(false);

  const filteredOffices = useMemo(() => {
    if (!searchTerm) return offices;
    
    return offices.filter(office => 
      office.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [offices, searchTerm]);

  const selectedOffice = useMemo(() => 
    offices.find(office => office.id === selectedOfficeId),
    [offices, selectedOfficeId]
  );

  const handleOfficeSelect = (officeId: string) => {
    if (allowMultiple && onMultipleOfficeChange) {
      const isSelected = selectedOfficeIds.includes(officeId);
      if (isSelected) {
        onMultipleOfficeChange(selectedOfficeIds.filter(id => id !== officeId));
      } else {
        onMultipleOfficeChange([...selectedOfficeIds, officeId]);
      }
    } else {
      onOfficeChange(officeId);
      setOpen(false);
    }
  };

  const getOfficeStats = (office: OfficeConfig) => {
    const totalFTE = office.total_fte || 0;
    const roleCount = Object.keys(office.roles || {}).length;

    return {
      totalFTE: Math.round(totalFTE),
      roleCount,
      levelCount: roleCount * 4 // Approximate levels per role
    };
  };

  if (allowMultiple) {
    // Simplified multi-select - using basic dropdown for now
    return (
      <div className="w-[280px]">
        <Button 
          variant="outline" 
          className="w-full justify-between"
          disabled={disabled}
        >
          <div className="flex items-center gap-2">
            <Building2 className="h-4 w-4" />
            {selectedOfficeIds.length === 0 && "Select offices..."}
            {selectedOfficeIds.length === 1 && 
              offices.find(o => o.id === selectedOfficeIds[0])?.name
            }
            {selectedOfficeIds.length > 1 && 
              `${selectedOfficeIds.length} offices selected`
            }
          </div>
        </Button>
      </div>
    );
  }

  return (
    <Select 
      value={selectedOfficeId || ''} 
      onValueChange={onOfficeChange}
      disabled={disabled}
    >
      <SelectTrigger className="w-[280px]">
        <SelectValue placeholder="Select an office">
          {selectedOffice && (
            <div className="flex items-center gap-2">
              <Building2 className="h-4 w-4" />
              <span>{selectedOffice.name}</span>
              <Badge variant="outline" className="ml-auto text-xs">
                {selectedOffice.journey}
              </Badge>
            </div>
          )}
        </SelectValue>
      </SelectTrigger>
      
      <SelectContent>
        {offices.map((office) => {
          const stats = getOfficeStats(office);
          
          return (
            <SelectItem key={office.id} value={office.id}>
              <div className="flex items-center justify-between w-full">
                <div className="flex items-center gap-2">
                  <span className="font-medium">{office.name}</span>
                  <Badge variant="outline" className="text-xs">
                    {office.journey}
                  </Badge>
                </div>
                
                {showStats && (
                  <div className="flex items-center gap-2 ml-auto text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Users className="h-3 w-3" />
                      {stats.totalFTE}
                    </span>
                  </div>
                )}
              </div>
            </SelectItem>
          );
        })}
        
        {offices.length === 0 && (
          <div className="p-6 text-center text-muted-foreground">
            <Building2 className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>No offices available</p>
          </div>
        )}
      </SelectContent>
    </Select>
  );
};