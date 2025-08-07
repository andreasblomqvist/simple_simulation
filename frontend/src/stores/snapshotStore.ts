/**
 * Snapshot state management with Zustand
 * Handles snapshot data, caching, and API interactions with optimistic updates
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { useCallback } from 'react';
import type { 
  PopulationSnapshot,
  CreateSnapshotRequest,
  UpdateSnapshotRequest,
  ListSnapshotsRequest,
  SnapshotComparison,
  CompareSnapshotsRequest,
  SnapshotStoreState,
  DEFAULT_PAGINATION
} from '../types/snapshots';
import { snapshotApi } from '../services/snapshotApi';

const DEFAULT_PAGINATION_STATE = {
  total: 0,
  offset: 0,
  limit: 10
};

export const useSnapshotStore = create<SnapshotStoreState>()(
  devtools(
    (set, get) => ({
      // Initial state
      snapshots: [],
      snapshotsByOffice: {},
      currentSnapshot: null,
      comparisonResult: null,
      loading: false,
      error: null,
      pagination: DEFAULT_PAGINATION_STATE,

      // Load snapshots with optional filtering and pagination
      loadSnapshots: async (params = {}) => {
        set({ loading: true, error: null });
        
        try {
          const response = await snapshotApi.listSnapshots(params);
          
          set({
            snapshots: response.snapshots,
            pagination: {
              total: response.total,
              offset: response.offset,
              limit: response.limit
            },
            loading: false
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to load snapshots',
            loading: false
          });
        }
      },

      // Load snapshots for a specific office
      loadSnapshotsByOffice: async (officeId: string) => {
        set({ loading: true, error: null });
        
        try {
          const snapshots = await snapshotApi.getSnapshotsByOffice(officeId);
          const currentState = get().snapshotsByOffice;
          
          set({
            snapshotsByOffice: {
              ...currentState,
              [officeId]: snapshots.sort((a, b) => 
                new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
              )
            },
            loading: false
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to load office snapshots',
            loading: false
          });
        }
      },

      // Create new snapshot with optimistic update
      createSnapshot: async (data: CreateSnapshotRequest) => {
        set({ loading: true, error: null });
        
        try {
          const newSnapshot = await snapshotApi.createSnapshot(data);
          
          // Update snapshots list
          const currentSnapshots = get().snapshots;
          const updatedSnapshots = [newSnapshot, ...currentSnapshots];
          
          // Update office-specific snapshots
          const currentOfficeSnapshots = get().snapshotsByOffice;
          const officeSnapshots = currentOfficeSnapshots[data.office_id] || [];
          const updatedOfficeSnapshots = [newSnapshot, ...officeSnapshots];
          
          set({
            snapshots: updatedSnapshots,
            snapshotsByOffice: {
              ...currentOfficeSnapshots,
              [data.office_id]: updatedOfficeSnapshots
            },
            currentSnapshot: newSnapshot,
            loading: false
          });
          
          return newSnapshot;
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to create snapshot',
            loading: false
          });
          throw error;
        }
      },

      // Update existing snapshot
      updateSnapshot: async (id: string, data: UpdateSnapshotRequest) => {
        set({ loading: true, error: null });
        
        try {
          const updatedSnapshot = await snapshotApi.updateSnapshot(id, data);
          
          // Update snapshots in main list
          const currentSnapshots = get().snapshots;
          const updatedSnapshots = currentSnapshots.map(snapshot =>
            snapshot.id === id ? updatedSnapshot : snapshot
          );
          
          // Update office-specific snapshots
          const currentOfficeSnapshots = get().snapshotsByOffice;
          const updatedOfficeSnapshots = { ...currentOfficeSnapshots };
          
          Object.keys(updatedOfficeSnapshots).forEach(officeId => {
            updatedOfficeSnapshots[officeId] = updatedOfficeSnapshots[officeId].map(snapshot =>
              snapshot.id === id ? updatedSnapshot : snapshot
            );
          });
          
          set({
            snapshots: updatedSnapshots,
            snapshotsByOffice: updatedOfficeSnapshots,
            currentSnapshot: get().currentSnapshot?.id === id ? updatedSnapshot : get().currentSnapshot,
            loading: false
          });
          
          return updatedSnapshot;
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to update snapshot',
            loading: false
          });
          throw error;
        }
      },

      // Delete snapshot with optimistic update
      deleteSnapshot: async (id: string) => {
        set({ loading: true, error: null });
        
        try {
          await snapshotApi.deleteSnapshot(id);
          
          // Remove from snapshots list
          const currentSnapshots = get().snapshots;
          const updatedSnapshots = currentSnapshots.filter(snapshot => snapshot.id !== id);
          
          // Remove from office-specific snapshots
          const currentOfficeSnapshots = get().snapshotsByOffice;
          const updatedOfficeSnapshots = { ...currentOfficeSnapshots };
          
          Object.keys(updatedOfficeSnapshots).forEach(officeId => {
            updatedOfficeSnapshots[officeId] = updatedOfficeSnapshots[officeId].filter(
              snapshot => snapshot.id !== id
            );
          });
          
          set({
            snapshots: updatedSnapshots,
            snapshotsByOffice: updatedOfficeSnapshots,
            currentSnapshot: get().currentSnapshot?.id === id ? null : get().currentSnapshot,
            loading: false
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to delete snapshot',
            loading: false
          });
          throw error;
        }
      },

      // Get a specific snapshot
      getSnapshot: async (id: string) => {
        // First check if we already have it in store
        const existingSnapshot = get().getSnapshotById(id);
        if (existingSnapshot) {
          set({ currentSnapshot: existingSnapshot });
          return existingSnapshot;
        }
        
        set({ loading: true, error: null });
        
        try {
          const snapshot = await snapshotApi.getSnapshot(id);
          set({
            currentSnapshot: snapshot,
            loading: false
          });
          return snapshot;
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to load snapshot',
            loading: false
          });
          throw error;
        }
      },

      // Compare two snapshots
      compareSnapshots: async (request: CompareSnapshotsRequest) => {
        set({ loading: true, error: null });
        
        try {
          const comparison = await snapshotApi.compareSnapshots(request);
          set({
            comparisonResult: comparison,
            loading: false
          });
          return comparison;
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to compare snapshots',
            loading: false
          });
          throw error;
        }
      },

      // Clear error state
      clearError: () => set({ error: null }),

      // Set current snapshot
      setCurrentSnapshot: (snapshot: PopulationSnapshot | null) => {
        set({ currentSnapshot: snapshot });
      },

      // Get snapshot by ID from store
      getSnapshotById: (id: string): PopulationSnapshot | undefined => {
        const state = get();
        
        // Check main snapshots array
        const fromMain = state.snapshots.find(snapshot => snapshot.id === id);
        if (fromMain) return fromMain;
        
        // Check office-specific snapshots
        for (const officeSnapshots of Object.values(state.snapshotsByOffice)) {
          const found = officeSnapshots.find(snapshot => snapshot.id === id);
          if (found) return found;
        }
        
        return undefined;
      },
    }),
    {
      name: 'snapshot-store',
      partialize: (state: SnapshotStoreState) => ({
        // Only persist essential data, not loading states or temporary comparisons
        snapshotsByOffice: state.snapshotsByOffice,
        currentSnapshot: state.currentSnapshot,
      }),
    }
  )
);

// Computed selectors for easier access
export const useCurrentSnapshot = () => useSnapshotStore(state => state.currentSnapshot);
export const useSnapshotLoading = () => useSnapshotStore(state => state.loading);
export const useSnapshotError = () => useSnapshotStore(state => state.error);
export const useSnapshotComparison = () => useSnapshotStore(state => state.comparisonResult);

// Office-specific selectors with proper memoization
export const useOfficeSnapshots = (officeId: string) => {
  return useSnapshotStore(
    useCallback(
      (state) => state.snapshotsByOffice[officeId] || [],
      [officeId]
    )
  );
};

export const useLatestOfficeSnapshot = (officeId: string) => 
  useSnapshotStore(state => {
    const officeSnapshots = state.snapshotsByOffice[officeId] || [];
    return officeSnapshots.length > 0 ? officeSnapshots[0] : null;
  });

// Helper hooks for common operations
export const useSnapshotActions = () => {
  const store = useSnapshotStore();
  
  return {
    loadSnapshots: store.loadSnapshots,
    loadSnapshotsByOffice: store.loadSnapshotsByOffice,
    createSnapshot: store.createSnapshot,
    updateSnapshot: store.updateSnapshot,
    deleteSnapshot: store.deleteSnapshot,
    getSnapshot: store.getSnapshot,
    compareSnapshots: store.compareSnapshots,
    clearError: store.clearError,
    setCurrentSnapshot: store.setCurrentSnapshot,
  };
};