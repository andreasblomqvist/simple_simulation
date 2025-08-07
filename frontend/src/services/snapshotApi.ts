/**
 * API service for population snapshots
 * Provides typed HTTP client functions for snapshot operations
 */

import type { 
  PopulationSnapshot,
  CreateSnapshotRequest,
  UpdateSnapshotRequest,
  ListSnapshotsRequest,
  ListSnapshotsResponse,
  CompareSnapshotsRequest,
  SnapshotComparison,
  SnapshotAPIError
} from '../types/snapshots';

const API_BASE = '/api/snapshots';

class SnapshotApiService {
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown error');
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      
      try {
        const errorData = JSON.parse(errorText);
        errorMessage = errorData.message || errorData.detail || errorMessage;
      } catch {
        if (errorText) {
          errorMessage = errorText;
        }
      }
      
      const error = new Error(errorMessage) as SnapshotAPIError;
      error.name = 'SnapshotAPIError';
      error.status = response.status;
      throw error;
    }
    
    const text = await response.text();
    if (!text) {
      return {} as T;
    }
    
    try {
      return JSON.parse(text);
    } catch (error) {
      throw new Error(`Invalid JSON response: ${text}`);
    }
  }

  /**
   * List snapshots with optional filtering and pagination
   */
  async listSnapshots(params: ListSnapshotsRequest = {}): Promise<ListSnapshotsResponse> {
    const searchParams = new URLSearchParams();
    
    if (params.office_id) searchParams.set('office_id', params.office_id);
    if (params.limit !== undefined) searchParams.set('limit', params.limit.toString());
    if (params.offset !== undefined) searchParams.set('offset', params.offset.toString());
    if (params.sort_by) searchParams.set('sort_by', params.sort_by);
    if (params.sort_order) searchParams.set('sort_order', params.sort_order);
    if (params.search) searchParams.set('search', params.search);
    if (params.tags?.length) searchParams.set('tags', params.tags.join(','));

    const response = await fetch(`${API_BASE}/?${searchParams}`);
    return this.handleResponse<ListSnapshotsResponse>(response);
  }

  /**
   * Get snapshots for a specific office
   */
  async getSnapshotsByOffice(officeId: string): Promise<PopulationSnapshot[]> {
    const response = await fetch(`${API_BASE}/office/${officeId}`);
    return this.handleResponse<PopulationSnapshot[]>(response);
  }

  /**
   * Get a specific snapshot by ID
   */
  async getSnapshot(id: string): Promise<PopulationSnapshot> {
    const response = await fetch(`${API_BASE}/${id}`);
    return this.handleResponse<PopulationSnapshot>(response);
  }

  /**
   * Create a new snapshot from current office workforce
   */
  async createSnapshot(data: CreateSnapshotRequest): Promise<PopulationSnapshot> {
    const response = await fetch(API_BASE, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return this.handleResponse<PopulationSnapshot>(response);
  }

  /**
   * Update an existing snapshot
   */
  async updateSnapshot(id: string, data: UpdateSnapshotRequest): Promise<PopulationSnapshot> {
    const response = await fetch(`${API_BASE}/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return this.handleResponse<PopulationSnapshot>(response);
  }

  /**
   * Delete a snapshot
   */
  async deleteSnapshot(id: string): Promise<void> {
    const response = await fetch(`${API_BASE}/${id}`, {
      method: 'DELETE',
    });
    await this.handleResponse<void>(response);
  }

  /**
   * Compare two snapshots
   */
  async compareSnapshots(request: CompareSnapshotsRequest): Promise<SnapshotComparison> {
    const response = await fetch(`${API_BASE}/compare`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    return this.handleResponse<SnapshotComparison>(response);
  }

  /**
   * Get available tags for snapshots (for filtering)
   */
  async getTags(officeId?: string): Promise<string[]> {
    const searchParams = new URLSearchParams();
    if (officeId) searchParams.set('office_id', officeId);
    
    const response = await fetch(`${API_BASE}/tags?${searchParams}`);
    return this.handleResponse<string[]>(response);
  }

  /**
   * Export snapshot data as CSV
   */
  async exportSnapshot(id: string, format: 'csv' | 'json' = 'csv'): Promise<Blob> {
    const response = await fetch(`${API_BASE}/${id}/export?format=${format}`);
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown error');
      throw new Error(`Export failed: ${errorText}`);
    }
    
    return response.blob();
  }

  /**
   * Get snapshot statistics for an office
   */
  async getSnapshotStats(officeId: string): Promise<{
    total_snapshots: number;
    latest_snapshot: PopulationSnapshot | null;
    avg_fte: number;
    fte_trend: number; // percentage change from first to last snapshot
  }> {
    const response = await fetch(`${API_BASE}/office/${officeId}/stats`);
    return this.handleResponse(response);
  }

  /**
   * Validate snapshot data before creation
   */
  async validateSnapshot(data: CreateSnapshotRequest): Promise<{
    is_valid: boolean;
    errors: string[];
    warnings: string[];
  }> {
    const response = await fetch(`${API_BASE}/validate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return this.handleResponse(response);
  }
}

// Create and export singleton instance
export const snapshotApi = new SnapshotApiService();

// Also export the class for testing purposes
export { SnapshotApiService };

// Helper functions for working with snapshot data
export const snapshotUtils = {
  /**
   * Format snapshot date for display
   */
  formatDate: (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  },

  /**
   * Format FTE value for display
   */
  formatFTE: (fte: number): string => {
    return fte.toFixed(1);
  },

  /**
   * Format salary value for display
   */
  formatSalary: (salary: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(salary);
  },

  /**
   * Format change value with sign and color indication
   */
  formatChange: (change: number, isPercentage = false): string => {
    const formatted = isPercentage 
      ? `${change > 0 ? '+' : ''}${change.toFixed(1)}%`
      : `${change > 0 ? '+' : ''}${change.toFixed(1)}`;
    return formatted;
  },

  /**
   * Calculate total FTE from workforce array
   */
  calculateTotalFTE: (workforce: Array<{ fte: number }>): number => {
    return workforce.reduce((total, item) => total + item.fte, 0);
  },

  /**
   * Calculate total salary cost from workforce array
   */
  calculateTotalSalaryCost: (workforce: Array<{ fte: number; salary: number }>): number => {
    return workforce.reduce((total, item) => total + (item.fte * item.salary), 0);
  },

  /**
   * Group workforce by role
   */
  groupByRole: (workforce: Array<{ role: string; level: string | null; fte: number }>) => {
    const grouped: Record<string, Array<{ level: string | null; fte: number }>> = {};
    
    workforce.forEach(item => {
      if (!grouped[item.role]) {
        grouped[item.role] = [];
      }
      grouped[item.role].push({ level: item.level, fte: item.fte });
    });
    
    return grouped;
  },

  /**
   * Generate summary text for a snapshot
   */
  generateSummary: (snapshot: PopulationSnapshot): string => {
    const totalFTE = snapshot.metadata.total_fte;
    const roleCount = snapshot.metadata.role_count;
    const date = snapshotUtils.formatDate(snapshot.snapshot_date);
    
    return `${totalFTE.toFixed(1)} FTE across ${roleCount} roles (${date})`;
  }
};