/**
 * Office state management with Zustand
 * Handles office data, selection, and API interactions
 */
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type { OfficeConfig, OfficeBusinessPlanSummary, CATMatrix } from '../types/office';
import { OfficeJourney } from '../types/office';

interface OfficeStoreState {
  // Data state
  offices: OfficeConfig[];
  currentOffice: OfficeConfig | null;
  officesByJourney: Record<OfficeJourney, OfficeConfig[]>;
  
  // UI state
  loading: boolean;
  error: string | null;
  
  // Actions
  loadOffices: () => Promise<void>;
  selectOffice: (officeId: string) => Promise<void>;
  createOffice: (office: Omit<OfficeConfig, 'id' | 'created_at' | 'updated_at'>) => Promise<OfficeConfig>;
  updateOffice: (office: OfficeConfig) => Promise<OfficeConfig>;
  deleteOffice: (officeId: string) => Promise<void>;
  
  // CAT Matrix operations
  updateOfficeCAT: (officeId: string, catMatrix: CATMatrix) => Promise<void>;
  resetOfficeCAT: (officeId: string) => Promise<void>;
  
  // Utils
  clearError: () => void;
  getOfficeById: (officeId: string) => OfficeConfig | undefined;
}

const API_BASE = '/api/offices';

// Helper function to group offices by journey
const groupOfficesByJourney = (offices: OfficeConfig[]): Record<OfficeJourney, OfficeConfig[]> => {
  const grouped: Record<OfficeJourney, OfficeConfig[]> = {
    [OfficeJourney.EMERGING]: [],
    [OfficeJourney.ESTABLISHED]: [],
    [OfficeJourney.MATURE]: [],
  };
  
  offices.forEach(office => {
    grouped[office.journey].push(office);
  });
  
  // Sort offices within each journey by name
  Object.keys(grouped).forEach(journey => {
    grouped[journey as OfficeJourney].sort((a, b) => a.name.localeCompare(b.name));
  });
  
  return grouped;
};

export const useOfficeStore = create<OfficeStoreState>()(
  devtools(
    (set, get) => ({
      // Initial state
      offices: [],
      currentOffice: null,
      officesByJourney: {
        [OfficeJourney.EMERGING]: [],
        [OfficeJourney.ESTABLISHED]: [],
        [OfficeJourney.MATURE]: [],
      },
      loading: false,
      error: null,

      // Load all offices
      loadOffices: async () => {
        console.log('🏢 Loading offices from:', API_BASE);
        set({ loading: true, error: null });
        
        try {
          const response = await fetch(API_BASE);
          console.log('🏢 Response status:', response.status, response.statusText);
          if (!response.ok) {
            throw new Error(`Failed to load offices: ${response.statusText}`);
          }
          
          const offices: OfficeConfig[] = await response.json();
          console.log('🏢 Loaded offices:', offices.length, 'offices');
          console.log('🏢 First office:', offices[0]?.name);
          const officesByJourney = groupOfficesByJourney(offices);
          
          set({ 
            offices, 
            officesByJourney,
            loading: false 
          });
        } catch (error) {
          console.error('🏢 Error loading offices:', error);
          set({ 
            error: error instanceof Error ? error.message : 'Failed to load offices',
            loading: false 
          });
        }
      },

      // Select a specific office
      selectOffice: async (officeId: string) => {
        const office = get().getOfficeById(officeId);
        
        if (office) {
          set({ currentOffice: office });
          return;
        }
        
        // Office not in current list, try to fetch it
        set({ loading: true, error: null });
        
        try {
          const response = await fetch(`${API_BASE}/${officeId}`);
          if (!response.ok) {
            throw new Error(`Office not found: ${response.statusText}`);
          }
          
          const fetchedOffice: OfficeConfig = await response.json();
          set({ 
            currentOffice: fetchedOffice,
            loading: false 
          });
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to load office',
            loading: false 
          });
        }
      },

      // Create new office
      createOffice: async (officeData) => {
        set({ loading: true, error: null });
        
        try {
          const response = await fetch(API_BASE, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(officeData),
          });
          
          if (!response.ok) {
            throw new Error(`Failed to create office: ${response.statusText}`);
          }
          
          const newOffice: OfficeConfig = await response.json();
          
          const currentOffices = get().offices;
          const updatedOffices = [...currentOffices, newOffice];
          const officesByJourney = groupOfficesByJourney(updatedOffices);
          
          set({ 
            offices: updatedOffices,
            officesByJourney,
            currentOffice: newOffice,
            loading: false 
          });
          
          return newOffice;
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to create office',
            loading: false 
          });
          throw error;
        }
      },

      // Update existing office
      updateOffice: async (office) => {
        set({ loading: true, error: null });
        
        try {
          const response = await fetch(`${API_BASE}/${office.id}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(office),
          });
          
          if (!response.ok) {
            throw new Error(`Failed to update office: ${response.statusText}`);
          }
          
          const updatedOffice: OfficeConfig = await response.json();
          
          const currentOffices = get().offices;
          const updatedOffices = currentOffices.map(o => 
            o.id === updatedOffice.id ? updatedOffice : o
          );
          const officesByJourney = groupOfficesByJourney(updatedOffices);
          
          set({ 
            offices: updatedOffices,
            officesByJourney,
            currentOffice: get().currentOffice?.id === updatedOffice.id ? updatedOffice : get().currentOffice,
            loading: false 
          });
          
          return updatedOffice;
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to update office',
            loading: false 
          });
          throw error;
        }
      },

      // Delete office
      deleteOffice: async (officeId) => {
        set({ loading: true, error: null });
        
        try {
          const response = await fetch(`${API_BASE}/${officeId}`, {
            method: 'DELETE',
          });
          
          if (!response.ok) {
            throw new Error(`Failed to delete office: ${response.statusText}`);
          }
          
          const currentOffices = get().offices;
          const updatedOffices = currentOffices.filter(o => o.id !== officeId);
          const officesByJourney = groupOfficesByJourney(updatedOffices);
          
          set({ 
            offices: updatedOffices,
            officesByJourney,
            currentOffice: get().currentOffice?.id === officeId ? null : get().currentOffice,
            loading: false 
          });
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to delete office',
            loading: false 
          });
          throw error;
        }
      },

      // Clear error state
      clearError: () => set({ error: null }),

      // Get office by ID
      getOfficeById: (officeId: string) => {
        return get().offices.find(office => office.id === officeId);
      },

      // Update office CAT matrix
      updateOfficeCAT: async (officeId: string, catMatrix: CATMatrix) => {
        set({ loading: true, error: null });
        
        try {
          const response = await fetch(`${API_BASE}/${officeId}/cat-matrix`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ cat_matrix: catMatrix }),
          });
          
          if (!response.ok) {
            throw new Error(`Failed to update CAT matrix: ${response.statusText}`);
          }
          
          // Update office in state
          const currentOffices = get().offices;
          const updatedOffices = currentOffices.map(office => 
            office.id === officeId 
              ? { ...office, cat_matrix: catMatrix }
              : office
          );
          const officesByJourney = groupOfficesByJourney(updatedOffices);
          
          set({ 
            offices: updatedOffices,
            officesByJourney,
            currentOffice: get().currentOffice?.id === officeId 
              ? { ...get().currentOffice!, cat_matrix: catMatrix }
              : get().currentOffice,
            loading: false 
          });
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to update CAT matrix',
            loading: false 
          });
          throw error;
        }
      },

      // Reset office CAT matrix to default
      resetOfficeCAT: async (officeId: string) => {
        set({ loading: true, error: null });
        
        try {
          const response = await fetch(`${API_BASE}/${officeId}/cat-matrix/reset`, {
            method: 'POST',
          });
          
          if (!response.ok) {
            throw new Error(`Failed to reset CAT matrix: ${response.statusText}`);
          }
          
          const resetMatrix: CATMatrix = await response.json();
          
          // Update office in state
          const currentOffices = get().offices;
          const updatedOffices = currentOffices.map(office => 
            office.id === officeId 
              ? { ...office, cat_matrix: resetMatrix }
              : office
          );
          const officesByJourney = groupOfficesByJourney(updatedOffices);
          
          set({ 
            offices: updatedOffices,
            officesByJourney,
            currentOffice: get().currentOffice?.id === officeId 
              ? { ...get().currentOffice!, cat_matrix: resetMatrix }
              : get().currentOffice,
            loading: false 
          });
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to reset CAT matrix',
            loading: false 
          });
          throw error;
        }
      },
    }),
    {
      name: 'office-store',
      partialize: (state: OfficeStoreState) => ({
        // Only persist essential data, not loading states
        offices: state.offices,
        currentOffice: state.currentOffice,
      }),
    }
  )
);

// Computed selectors for easier access
export const useCurrentOffice = () => useOfficeStore(state => state.currentOffice);
export const useOfficeLoading = () => useOfficeStore(state => state.loading);
export const useOfficeError = () => useOfficeStore(state => state.error);
export const useOfficesByJourney = () => useOfficeStore(state => state.officesByJourney);