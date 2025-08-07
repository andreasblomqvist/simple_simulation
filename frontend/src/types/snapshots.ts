/**
 * TypeScript types for population snapshots functionality
 * Mirrors the backend Pydantic models and provides UI-specific interfaces
 */

import type { OfficeConfig } from './office';

// Base snapshot interfaces
export interface SnapshotWorkforce {
  role: string;
  level: string | null; // null for flat roles like Operations
  fte: number;
  salary: number;
  notes?: string;
}

export interface PopulationSnapshot {
  id: string;
  name: string;
  description?: string;
  office_id: string;
  snapshot_date: string; // ISO date string
  workforce: SnapshotWorkforce[];
  metadata: {
    total_fte: number;
    total_salary_cost: number;
    role_count: number;
    created_by?: string;
    tags?: string[];
  };
  created_at: string;
  updated_at: string;
}

// Comparison interfaces
export interface SnapshotComparison {
  baseline: PopulationSnapshot;
  comparison: PopulationSnapshot;
  workforce_changes: WorkforceChange[];
  summary: ComparisonSummary;
}

export interface WorkforceChange {
  role: string;
  level: string | null;
  change_type: 'added' | 'removed' | 'modified';
  baseline_fte: number;
  comparison_fte: number;
  fte_change: number;
  salary_change: number;
}

export interface ComparisonSummary {
  total_fte_change: number;
  total_salary_change: number;
  roles_added: number;
  roles_removed: number;
  roles_modified: number;
  net_change_percentage: number;
}

// API request/response types
export interface CreateSnapshotRequest {
  name: string;
  description?: string;
  office_id: string;
  snapshot_date?: string; // Optional, defaults to current date
  tags?: string[];
}

export interface UpdateSnapshotRequest {
  name?: string;
  description?: string;
  tags?: string[];
}

export interface ListSnapshotsRequest {
  office_id?: string;
  limit?: number;
  offset?: number;
  sort_by?: 'created_at' | 'name' | 'snapshot_date';
  sort_order?: 'asc' | 'desc';
  search?: string;
  tags?: string[];
}

export interface ListSnapshotsResponse {
  snapshots: PopulationSnapshot[];
  total: number;
  offset: number;
  limit: number;
}

export interface CompareSnapshotsRequest {
  baseline_id: string;
  comparison_id: string;
}

// UI-specific types
export interface SnapshotFormData {
  name: string;
  description: string;
  office_id: string;
  snapshot_date: Date;
  tags: string[];
}

export interface SnapshotSelectorProps {
  officeId: string;
  selectedSnapshot?: PopulationSnapshot | null;
  onSnapshotSelect: (snapshot: PopulationSnapshot | null) => void;
  label?: string;
  placeholder?: string;
  showCurrentOption?: boolean;
  className?: string;
}

export interface SnapshotManagerProps {
  officeId: string;
  onSnapshotCreated?: (snapshot: PopulationSnapshot) => void;
  onSnapshotDeleted?: (snapshotId: string) => void;
}

export interface SnapshotComparisonProps {
  baseline: PopulationSnapshot;
  comparison: PopulationSnapshot;
  onClose?: () => void;
}

export interface CreateSnapshotModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSnapshotCreated: (snapshot: PopulationSnapshot) => void;
  officeId: string;
  officeName?: string;
}

export interface SnapshotWorkforceTableProps {
  workforce: SnapshotWorkforce[];
  showSalary?: boolean;
  showNotes?: boolean;
  className?: string;
}

// Store state interfaces
export interface SnapshotStoreState {
  // Data state
  snapshots: PopulationSnapshot[];
  snapshotsByOffice: Record<string, PopulationSnapshot[]>;
  currentSnapshot: PopulationSnapshot | null;
  comparisonResult: SnapshotComparison | null;
  
  // UI state
  loading: boolean;
  error: string | null;
  
  // Pagination
  pagination: {
    total: number;
    offset: number;
    limit: number;
  };
  
  // Actions
  loadSnapshots: (params?: ListSnapshotsRequest) => Promise<void>;
  loadSnapshotsByOffice: (officeId: string) => Promise<void>;
  createSnapshot: (data: CreateSnapshotRequest) => Promise<PopulationSnapshot>;
  updateSnapshot: (id: string, data: UpdateSnapshotRequest) => Promise<PopulationSnapshot>;
  deleteSnapshot: (id: string) => Promise<void>;
  getSnapshot: (id: string) => Promise<PopulationSnapshot>;
  compareSnapshots: (request: CompareSnapshotsRequest) => Promise<SnapshotComparison>;
  
  // Utils
  clearError: () => void;
  setCurrentSnapshot: (snapshot: PopulationSnapshot | null) => void;
  getSnapshotById: (id: string) => PopulationSnapshot | undefined;
}

// Error handling
export class SnapshotAPIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string
  ) {
    super(message);
    this.name = 'SnapshotAPIError';
  }
}

// Constants
export const SNAPSHOT_SORT_OPTIONS = [
  { value: 'created_at', label: 'Created Date' },
  { value: 'name', label: 'Name' },
  { value: 'snapshot_date', label: 'Snapshot Date' }
] as const;

export const SNAPSHOT_SORT_ORDERS = [
  { value: 'desc', label: 'Newest First' },
  { value: 'asc', label: 'Oldest First' }
] as const;

// Default values
export const DEFAULT_PAGINATION = {
  total: 0,
  offset: 0,
  limit: 10
};

export const DEFAULT_LIST_PARAMS: ListSnapshotsRequest = {
  limit: 10,
  offset: 0,
  sort_by: 'created_at',
  sort_order: 'desc'
};

// Helper types for form validation
export interface SnapshotValidationResult {
  isValid: boolean;
  errors: Record<string, string>;
  warnings: string[];
}

// UI state enums
export enum SnapshotViewMode {
  LIST = 'list',
  COMPARISON = 'comparison',
  DETAILS = 'details'
}

export enum SnapshotFilterType {
  ALL = 'all',
  RECENT = 'recent',
  BY_DATE = 'by_date',
  BY_TAG = 'by_tag'
}

// Integration with existing types
export interface SnapshotAwareOffice extends OfficeConfig {
  latest_snapshot?: PopulationSnapshot;
  snapshot_count?: number;
}

// Utility functions types
export type SnapshotFormatter = {
  formatDate: (date: string) => string;
  formatFTE: (fte: number) => string;
  formatSalary: (salary: number) => string;
  formatChange: (change: number, isPercentage?: boolean) => string;
  formatWorkforce: (workforce: SnapshotWorkforce[]) => string;
};