/**
 * SnapshotSelector Component
 * Dropdown selector for choosing population snapshots with current workforce option
 */

import React, { useEffect, useState } from 'react';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '../ui/select';
import { Label } from '../ui/label';
import { Button } from '../ui/button';
import { Calendar, Clock, Users, RefreshCw } from 'lucide-react';
import { cn } from '../../lib/utils';
import { useOfficeSnapshots, useSnapshotActions, useSnapshotLoading } from '../../stores/snapshotStore';
import { snapshotUtils } from '../../services/snapshotApi';
import type { PopulationSnapshot, SnapshotSelectorProps } from '../../types/snapshots';

export const SnapshotSelector: React.FC<SnapshotSelectorProps> = ({
  officeId,
  selectedSnapshot,
  onSnapshotSelect,
  label = "Snapshot",
  placeholder = "Select snapshot or use current workforce",
  showCurrentOption = true,
  className
}) => {
  const snapshots = useOfficeSnapshots(officeId);
  const loading = useSnapshotLoading();
  const { loadSnapshotsByOffice, clearError } = useSnapshotActions();
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    // Temporarily disabled to fix infinite loop - office IDs are strings but API expects UUIDs
    // TODO: Fix office ID format mismatch between offices API (strings) and snapshots API (UUIDs)
    console.log('🚫 Snapshot loading temporarily disabled for office:', officeId);
    // if (officeId) {
    //   loadSnapshotsByOffice(officeId);
    // }
  }, [officeId]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    clearError();
    try {
      await loadSnapshotsByOffice(officeId);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleSelectionChange = (value: string) => {
    if (value === 'current') {
      onSnapshotSelect(null);
    } else {
      const snapshot = snapshots.find(s => s.id === value);
      onSnapshotSelect(snapshot || null);
    }
  };

  const currentValue = selectedSnapshot ? selectedSnapshot.id : 'current';

  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex items-center justify-between">
        <Label className="text-sm font-medium" style={{ color: '#f3f4f6' }}>
          {label}
        </Label>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleRefresh}
          disabled={loading || isRefreshing}
          className="h-6 w-6 p-0 hover:bg-gray-700"
          style={{ color: '#9ca3af' }}
        >
          <RefreshCw className={cn(
            "h-3 w-3", 
            (loading || isRefreshing) && "animate-spin"
          )} />
        </Button>
      </div>

      <Select value={currentValue} onValueChange={handleSelectionChange}>
        <SelectTrigger 
          className="w-full bg-gray-800 border-gray-600 text-gray-100 hover:bg-gray-700"
          disabled={loading}
        >
          <SelectValue placeholder={placeholder} />
        </SelectTrigger>
        
        <SelectContent className="bg-gray-800 border-gray-600">
          {showCurrentOption && (
            <SelectItem 
              value="current"
              className="text-gray-100 hover:bg-gray-700 focus:bg-gray-700"
            >
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4" style={{ color: '#10b981' }} />
                <div className="flex flex-col">
                  <span className="font-medium">Current Workforce</span>
                  <span className="text-xs" style={{ color: '#9ca3af' }}>
                    Use live workforce data
                  </span>
                </div>
              </div>
            </SelectItem>
          )}
          
          {snapshots.length > 0 && showCurrentOption && (
            <div className="h-px bg-gray-600 my-1" />
          )}

          {snapshots.length === 0 && !loading ? (
            <div className="px-2 py-3 text-center">
              <Clock className="h-8 w-8 mx-auto mb-2" style={{ color: '#6b7280' }} />
              <p className="text-sm font-medium" style={{ color: '#9ca3af' }}>
                No snapshots available
              </p>
              <p className="text-xs" style={{ color: '#6b7280' }}>
                Create a snapshot to get started
              </p>
            </div>
          ) : (
            snapshots.map((snapshot) => (
              <SelectItem 
                key={snapshot.id} 
                value={snapshot.id}
                className="text-gray-100 hover:bg-gray-700 focus:bg-gray-700"
              >
                <div className="flex items-start justify-between w-full">
                  <div className="flex items-center gap-2 min-w-0 flex-1">
                    <Calendar className="h-4 w-4 flex-shrink-0" style={{ color: '#3b82f6' }} />
                    <div className="flex flex-col min-w-0 flex-1">
                      <span className="font-medium truncate">
                        {snapshot.name}
                      </span>
                      <div className="flex items-center gap-3 text-xs" style={{ color: '#9ca3af' }}>
                        <span>
                          {snapshotUtils.formatDate(snapshot.snapshot_date)}
                        </span>
                        <span>
                          {snapshot.metadata.total_fte.toFixed(1)} FTE
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </SelectItem>
            ))
          )}

          {loading && (
            <div className="px-2 py-3 text-center">
              <RefreshCw className="h-4 w-4 mx-auto mb-2 animate-spin" style={{ color: '#6b7280' }} />
              <p className="text-sm" style={{ color: '#9ca3af' }}>Loading snapshots...</p>
            </div>
          )}
        </SelectContent>
      </Select>

      {/* Selected snapshot details */}
      {selectedSnapshot && (
        <div className="mt-2 p-3 rounded-lg" style={{ backgroundColor: '#111827' }}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4" style={{ color: '#3b82f6' }} />
              <span className="text-sm font-medium" style={{ color: '#f3f4f6' }}>
                {selectedSnapshot.name}
              </span>
            </div>
            <div className="text-xs" style={{ color: '#9ca3af' }}>
              {snapshotUtils.formatDate(selectedSnapshot.created_at)}
            </div>
          </div>
          
          {selectedSnapshot.description && (
            <p className="text-xs mt-1 text-gray-400">
              {selectedSnapshot.description}
            </p>
          )}
          
          <div className="flex items-center gap-4 mt-2 text-xs" style={{ color: '#9ca3af' }}>
            <div className="flex items-center gap-1">
              <Users className="h-3 w-3" />
              <span>{selectedSnapshot.metadata.total_fte.toFixed(1)} FTE</span>
            </div>
            <div className="flex items-center gap-1">
              <span>{selectedSnapshot.metadata.role_count} roles</span>
            </div>
            <div className="flex items-center gap-1">
              <span>
                {snapshotUtils.formatSalary(selectedSnapshot.metadata.total_salary_cost)} cost
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Current workforce indicator */}
      {!selectedSnapshot && showCurrentOption && (
        <div className="mt-2 p-3 rounded-lg" style={{ backgroundColor: '#111827' }}>
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4" style={{ color: '#10b981' }} />
            <span className="text-sm font-medium" style={{ color: '#f3f4f6' }}>
              Using Current Workforce
            </span>
          </div>
          <p className="text-xs mt-1" style={{ color: '#9ca3af' }}>
            Displaying live workforce data from office configuration
          </p>
        </div>
      )}
    </div>
  );
};

export default SnapshotSelector;