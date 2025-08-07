/**
 * Snapshot components barrel export
 * Provides centralized exports for all snapshot-related components
 */

export { default as SnapshotSelector } from './SnapshotSelector';
export { default as SnapshotManager } from './SnapshotManager';
export { default as CreateSnapshotModal } from './CreateSnapshotModal';
export { default as SnapshotComparison } from './SnapshotComparison';
export { default as SnapshotWorkforceTable } from './SnapshotWorkforceTable';

// Re-export types for convenience
export type {
  PopulationSnapshot,
  SnapshotWorkforce,
  SnapshotComparison,
  CreateSnapshotRequest,
  UpdateSnapshotRequest,
  ListSnapshotsRequest,
  ListSnapshotsResponse,
  CompareSnapshotsRequest,
  SnapshotFormData,
  SnapshotSelectorProps,
  SnapshotManagerProps,
  SnapshotComparisonProps,
  CreateSnapshotModalProps,
  SnapshotWorkforceTableProps
} from '../../types/snapshots';