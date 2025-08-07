/**
 * SnapshotManager Component
 * Full management interface for population snapshots
 */

import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { DataTableMinimal, MinimalColumnDef } from '../ui/data-table-minimal';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import { 
  Plus, 
  Search, 
  Calendar, 
  Users, 
  MoreHorizontal,
  Eye,
  Edit,
  Trash2,
  Download,
  GitCompare,
  RefreshCw,
  Camera,
  Filter,
  SortAsc,
  SortDesc
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { 
  useOfficeSnapshots, 
  useSnapshotActions, 
  useSnapshotLoading, 
  useSnapshotError 
} from '../../stores/snapshotStore';
import { snapshotApi, snapshotUtils } from '../../services/snapshotApi';
import type { PopulationSnapshot, SnapshotManagerProps } from '../../types/snapshots';
import CreateSnapshotModal from './CreateSnapshotModal';
import SnapshotComparison from './SnapshotComparison';
import SnapshotWorkforceTable from './SnapshotWorkforceTable';

type ViewMode = 'list' | 'comparison' | 'details';
type SortField = 'name' | 'created_at' | 'snapshot_date' | 'total_fte';
type SortOrder = 'asc' | 'desc';

export const SnapshotManager: React.FC<SnapshotManagerProps> = ({
  officeId,
  onSnapshotCreated,
  onSnapshotDeleted
}) => {
  const snapshots = useOfficeSnapshots(officeId);
  const loading = useSnapshotLoading();
  const error = useSnapshotError();
  const { loadSnapshotsByOffice, deleteSnapshot, clearError } = useSnapshotActions();

  // Component state
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedSnapshot, setSelectedSnapshot] = useState<PopulationSnapshot | null>(null);
  const [comparisonSnapshots, setComparisonSnapshots] = useState<{
    baseline: PopulationSnapshot | null;
    comparison: PopulationSnapshot | null;
  }>({ baseline: null, comparison: null });
  const [deleteConfirm, setDeleteConfirm] = useState<PopulationSnapshot | null>(null);

  // Filters and sorting
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState<SortField>('created_at');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);

  // Load data on mount and office change
  useEffect(() => {
    if (officeId) {
      loadSnapshotsByOffice(officeId);
    }
  }, [officeId, loadSnapshotsByOffice]);

  // Filtered and sorted snapshots
  const filteredSnapshots = useMemo(() => {
    let filtered = [...snapshots];

    // Apply search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(snapshot => 
        snapshot.name.toLowerCase().includes(term) ||
        snapshot.description?.toLowerCase().includes(term) ||
        snapshot.metadata.tags?.some(tag => tag.toLowerCase().includes(term))
      );
    }

    // Apply tag filter
    if (selectedTags.length > 0) {
      filtered = filtered.filter(snapshot =>
        selectedTags.every(tag => 
          snapshot.metadata.tags?.includes(tag)
        )
      );
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sortField) {
        case 'name':
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
          break;
        case 'created_at':
          aValue = new Date(a.created_at).getTime();
          bValue = new Date(b.created_at).getTime();
          break;
        case 'snapshot_date':
          aValue = new Date(a.snapshot_date).getTime();
          bValue = new Date(b.snapshot_date).getTime();
          break;
        case 'total_fte':
          aValue = a.metadata.total_fte;
          bValue = b.metadata.total_fte;
          break;
        default:
          return 0;
      }

      if (sortOrder === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });

    return filtered;
  }, [snapshots, searchTerm, selectedTags, sortField, sortOrder]);

  // Available tags for filtering
  const availableTags = useMemo(() => {
    const tags = new Set<string>();
    snapshots.forEach(snapshot => {
      snapshot.metadata.tags?.forEach(tag => tags.add(tag));
    });
    return Array.from(tags).sort();
  }, [snapshots]);

  const handleCreateSnapshot = (snapshot: PopulationSnapshot) => {
    setShowCreateModal(false);
    onSnapshotCreated?.(snapshot);
  };

  const handleDeleteSnapshot = async (snapshot: PopulationSnapshot) => {
    try {
      await deleteSnapshot(snapshot.id);
      setDeleteConfirm(null);
      onSnapshotDeleted?.(snapshot.id);
    } catch (error) {
      // Error handled by store
      console.error('Failed to delete snapshot:', error);
    }
  };

  const handleExportSnapshot = async (snapshot: PopulationSnapshot) => {
    try {
      const blob = await snapshotApi.exportSnapshot(snapshot.id, 'csv');
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${snapshot.name.replace(/[^a-zA-Z0-9]/g, '_')}_${snapshot.snapshot_date}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export snapshot:', error);
    }
  };

  const handleStartComparison = (snapshot: PopulationSnapshot) => {
    if (!comparisonSnapshots.baseline) {
      setComparisonSnapshots({ baseline: snapshot, comparison: null });
    } else if (!comparisonSnapshots.comparison) {
      setComparisonSnapshots(prev => ({ ...prev, comparison: snapshot }));
      setViewMode('comparison');
    } else {
      setComparisonSnapshots({ baseline: snapshot, comparison: null });
    }
  };

  const handleToggleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  const columns: MinimalColumnDef<PopulationSnapshot>[] = useMemo(() => [
    {
      accessorKey: "name",
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => handleToggleSort('name')}
          className="h-auto p-0 font-medium hover:bg-transparent"
          style={{ color: '#f3f4f6' }}
        >
          Name
          {sortField === 'name' && (
            sortOrder === 'asc' ? <SortAsc className="ml-2 h-4 w-4" /> : <SortDesc className="ml-2 h-4 w-4" />
          )}
        </Button>
      ),
      cell: ({ row }) => {
        const snapshot = row.original;
        const isInComparison = comparisonSnapshots.baseline?.id === snapshot.id || 
                              comparisonSnapshots.comparison?.id === snapshot.id;
        
        return (
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="font-medium" style={{ color: '#f3f4f6' }}>
                {snapshot.name}
              </span>
              {isInComparison && (
                <Badge variant="outline" className="text-xs bg-blue-900 text-blue-100 border-blue-700">
                  {comparisonSnapshots.baseline?.id === snapshot.id ? 'Baseline' : 'Comparison'}
                </Badge>
              )}
            </div>
            {snapshot.description && (
              <p className="text-xs text-gray-400 line-clamp-2">
                {snapshot.description}
              </p>
            )}
            {snapshot.metadata.tags && snapshot.metadata.tags.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {snapshot.metadata.tags.slice(0, 3).map(tag => (
                  <Badge key={tag} variant="secondary" className="text-xs bg-gray-700 text-gray-300">
                    {tag}
                  </Badge>
                ))}
                {snapshot.metadata.tags.length > 3 && (
                  <Badge variant="secondary" className="text-xs bg-gray-700 text-gray-300">
                    +{snapshot.metadata.tags.length - 3}
                  </Badge>
                )}
              </div>
            )}
          </div>
        );
      }
    },
    {
      accessorKey: "snapshot_date",
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => handleToggleSort('snapshot_date')}
          className="h-auto p-0 font-medium hover:bg-transparent"
          style={{ color: '#f3f4f6' }}
        >
          Date
          {sortField === 'snapshot_date' && (
            sortOrder === 'asc' ? <SortAsc className="ml-2 h-4 w-4" /> : <SortDesc className="ml-2 h-4 w-4" />
          )}
        </Button>
      ),
      cell: ({ row }) => (
        <div className="text-sm">
          <div style={{ color: '#f3f4f6' }}>
            {snapshotUtils.formatDate(row.original.snapshot_date)}
          </div>
          <div className="text-xs" style={{ color: '#9ca3af' }}>
            Created {snapshotUtils.formatDate(row.original.created_at)}
          </div>
        </div>
      )
    },
    {
      accessorKey: "metadata",
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => handleToggleSort('total_fte')}
          className="h-auto p-0 font-medium hover:bg-transparent"
          style={{ color: '#f3f4f6' }}
        >
          Workforce
          {sortField === 'total_fte' && (
            sortOrder === 'asc' ? <SortAsc className="ml-2 h-4 w-4" /> : <SortDesc className="ml-2 h-4 w-4" />
          )}
        </Button>
      ),
      cell: ({ row }) => (
        <div className="text-sm space-y-1">
          <div className="flex items-center gap-2" style={{ color: '#f3f4f6' }}>
            <Users className="h-4 w-4" />
            <span className="font-mono">{snapshotUtils.formatFTE(row.original.metadata.total_fte)}</span>
          </div>
          <div className="text-xs" style={{ color: '#9ca3af' }}>
            {row.original.metadata.role_count} roles
          </div>
        </div>
      )
    },
    {
      id: "actions",
      enableHiding: false,
      cell: ({ row }) => {
        const snapshot = row.original;
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0 hover:bg-gray-700">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="bg-gray-800 border-gray-600">
              <DropdownMenuLabel style={{ color: '#f3f4f6' }}>Actions</DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-gray-600" />
              <DropdownMenuItem 
                onClick={() => {
                  setSelectedSnapshot(snapshot);
                  setViewMode('details');
                }}
                className="text-gray-100 hover:bg-gray-700"
              >
                <Eye className="mr-2 h-4 w-4" />
                View Details
              </DropdownMenuItem>
              <DropdownMenuItem 
                onClick={() => handleStartComparison(snapshot)}
                className="text-gray-100 hover:bg-gray-700"
              >
                <GitCompare className="mr-2 h-4 w-4" />
                {comparisonSnapshots.baseline?.id === snapshot.id ? 'Remove from Comparison' : 
                 comparisonSnapshots.baseline && !comparisonSnapshots.comparison ? 'Compare with' : 
                 'Add to Comparison'}
              </DropdownMenuItem>
              <DropdownMenuItem 
                onClick={() => handleExportSnapshot(snapshot)}
                className="text-gray-100 hover:bg-gray-700"
              >
                <Download className="mr-2 h-4 w-4" />
                Export CSV
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-gray-600" />
              <DropdownMenuItem 
                onClick={() => setDeleteConfirm(snapshot)}
                className="text-red-400 hover:bg-gray-700 hover:text-red-300"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ], [sortField, sortOrder, comparisonSnapshots]);

  if (viewMode === 'comparison' && comparisonSnapshots.baseline && comparisonSnapshots.comparison) {
    return (
      <SnapshotComparison
        baseline={comparisonSnapshots.baseline}
        comparison={comparisonSnapshots.comparison}
        onClose={() => {
          setViewMode('list');
          setComparisonSnapshots({ baseline: null, comparison: null });
        }}
      />
    );
  }

  if (viewMode === 'details' && selectedSnapshot) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-2xl font-bold flex items-center gap-2" style={{ color: '#f3f4f6' }}>
              <Calendar className="h-6 w-6" style={{ color: '#3b82f6' }} />
              {selectedSnapshot.name}
            </h3>
            <p className="text-sm mt-1" style={{ color: '#d1d5db' }}>
              {snapshotUtils.formatDate(selectedSnapshot.snapshot_date)}
            </p>
          </div>
          <Button
            variant="outline"
            onClick={() => setViewMode('list')}
            className="bg-gray-700 border-gray-600 text-gray-100 hover:bg-gray-600"
          >
            Back to List
          </Button>
        </div>

        <SnapshotWorkforceTable
          workforce={selectedSnapshot.workforce}
          showSalary={true}
          showNotes={false}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header and Controls */}
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-2xl font-bold flex items-center gap-2" style={{ color: '#f3f4f6' }}>
            <Camera className="h-6 w-6" style={{ color: '#3b82f6' }} />
            Population Snapshots
          </h3>
          <p className="text-sm mt-1" style={{ color: '#d1d5db' }}>
            Manage historical workforce snapshots for analysis and comparison
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => loadSnapshotsByOffice(officeId)}
            disabled={loading}
            className="bg-gray-700 border-gray-600 text-gray-100 hover:bg-gray-600"
          >
            <RefreshCw className={cn("h-4 w-4 mr-2", loading && "animate-spin")} />
            Refresh
          </Button>
          <Button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 text-white hover:bg-blue-700"
          >
            <Plus className="h-4 w-4 mr-2" />
            Create Snapshot
          </Button>
        </div>
      </div>

      {/* Filters and Search */}
      <Card className="border-0 shadow-md" style={{ backgroundColor: '#1f2937' }}>
        <CardContent className="p-4">
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4" style={{ color: '#9ca3af' }} />
                <Input
                  placeholder="Search snapshots..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-gray-800 border-gray-600 text-gray-100 placeholder-gray-400"
                />
              </div>
            </div>
            {availableTags.length > 0 && (
              <div className="flex items-center gap-2">
                <Filter className="h-4 w-4" style={{ color: '#9ca3af' }} />
                <div className="flex flex-wrap gap-1">
                  {availableTags.slice(0, 5).map(tag => (
                    <Badge
                      key={tag}
                      variant={selectedTags.includes(tag) ? "default" : "secondary"}
                      className={cn(
                        "cursor-pointer text-xs",
                        selectedTags.includes(tag) 
                          ? "bg-blue-600 text-white hover:bg-blue-700" 
                          : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                      )}
                      onClick={() => {
                        setSelectedTags(prev =>
                          prev.includes(tag)
                            ? prev.filter(t => t !== tag)
                            : [...prev, tag]
                        );
                      }}
                    >
                      {tag}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          {comparisonSnapshots.baseline && (
            <div className="mt-3 p-2 rounded bg-blue-900/20 border border-blue-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm" style={{ color: '#93c5fd' }}>
                  <GitCompare className="h-4 w-4" />
                  <span>
                    {comparisonSnapshots.baseline.name}
                    {comparisonSnapshots.comparison ? ` vs ${comparisonSnapshots.comparison.name}` : ' - Select another snapshot to compare'}
                  </span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setComparisonSnapshots({ baseline: null, comparison: null })}
                  className="text-blue-300 hover:text-blue-100"
                >
                  Clear
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Snapshots Table */}
      <Card className="border-0 shadow-md" style={{ backgroundColor: '#1f2937' }}>
        <CardContent className="p-0">
          {error ? (
            <div className="text-center py-12">
              <div className="text-red-400 mb-4">Error loading snapshots</div>
              <div className="text-sm" style={{ color: '#9ca3af' }}>{error}</div>
              <Button
                variant="outline"
                className="mt-4 bg-gray-700 border-gray-600 text-gray-100 hover:bg-gray-600"
                onClick={() => {
                  clearError();
                  loadSnapshotsByOffice(officeId);
                }}
              >
                Retry
              </Button>
            </div>
          ) : filteredSnapshots.length === 0 ? (
            <div className="text-center py-12">
              <Camera className="h-12 w-12 mx-auto mb-4" style={{ color: '#9ca3af' }} />
              <h3 className="text-lg font-medium mb-2" style={{ color: '#f3f4f6' }}>
                {snapshots.length === 0 ? 'No snapshots yet' : 'No snapshots match your filters'}
              </h3>
              <p style={{ color: '#9ca3af' }}>
                {snapshots.length === 0 
                  ? 'Create your first snapshot to capture the current workforce state'
                  : 'Try adjusting your search or filter criteria'
                }
              </p>
              {snapshots.length === 0 && (
                <Button
                  className="mt-4 bg-blue-600 text-white hover:bg-blue-700"
                  onClick={() => setShowCreateModal(true)}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Create First Snapshot
                </Button>
              )}
            </div>
          ) : (
            <DataTableMinimal
              columns={columns}
              data={filteredSnapshots}
              enablePagination={true}
              pageSize={10}
              className="snapshots-table"
            />
          )}
        </CardContent>
      </Card>

      {/* Create Snapshot Modal */}
      <CreateSnapshotModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSnapshotCreated={handleCreateSnapshot}
        officeId={officeId}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!deleteConfirm} onOpenChange={() => setDeleteConfirm(null)}>
        <DialogContent className="bg-gray-800 border-gray-600 text-gray-100">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Trash2 className="h-5 w-5" style={{ color: '#ef4444' }} />
              Delete Snapshot
            </DialogTitle>
            <DialogDescription style={{ color: '#d1d5db' }}>
              Are you sure you want to delete "{deleteConfirm?.name}"? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteConfirm(null)}
              className="bg-gray-700 border-gray-600 text-gray-100 hover:bg-gray-600"
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => deleteConfirm && handleDeleteSnapshot(deleteConfirm)}
              disabled={loading}
              className="bg-red-600 text-white hover:bg-red-700"
            >
              {loading ? 'Deleting...' : 'Delete'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default SnapshotManager;