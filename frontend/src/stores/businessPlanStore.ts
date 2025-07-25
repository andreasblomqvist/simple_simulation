/**
 * Business plan state management with Zustand
 * Handles monthly business plan data and operations
 */
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { 
  MonthlyBusinessPlan, 
  MonthlyPlanEntry, 
  WorkforceDistribution,
  OfficeBusinessPlanSummary 
} from '../types/office';

interface BusinessPlanStoreState {
  // Data state
  monthlyPlans: MonthlyBusinessPlan[];
  workforceDistributions: WorkforceDistribution[];
  currentPlan: MonthlyBusinessPlan | null;
  currentWorkforce: WorkforceDistribution | null;
  
  // UI state
  loading: boolean;
  error: string | null;
  selectedYear: number;
  selectedMonth: number;
  
  // Actions
  loadBusinessPlans: (officeId: string, year?: number) => Promise<void>;
  loadWorkforceDistribution: (officeId: string) => Promise<void>;
  loadOfficeSummary: (officeId: string) => Promise<OfficeBusinessPlanSummary>;
  
  createMonthlyPlan: (plan: Omit<MonthlyBusinessPlan, 'id' | 'created_at' | 'updated_at'>) => Promise<MonthlyBusinessPlan>;
  updateMonthlyPlan: (plan: MonthlyBusinessPlan) => Promise<MonthlyBusinessPlan>;
  updatePlanEntry: (planId: string, entry: MonthlyPlanEntry) => Promise<void>;
  deleteMonthlyPlan: (planId: string) => Promise<void>;
  
  copyPlanTemplate: (sourceOfficeId: string, targetOfficeId: string, year: number, month: number) => Promise<void>;
  bulkUpdatePlans: (officeId: string, plans: MonthlyBusinessPlan[]) => Promise<void>;
  
  // UI actions
  setSelectedPeriod: (year: number, month: number) => void;
  clearError: () => void;
  
  // Utils
  getPlanForMonth: (year: number, month: number) => MonthlyBusinessPlan | undefined;
  getPlansForYear: (year: number) => MonthlyBusinessPlan[];
  getAvailableYears: () => number[];
}

const API_BASE = '/business-plans';

export const useBusinessPlanStore = create<BusinessPlanStoreState>()(
  devtools(
    (set, get) => ({
      // Initial state
      monthlyPlans: [],
      workforceDistributions: [],
      currentPlan: null,
      currentWorkforce: null,
      loading: false,
      error: null,
      selectedYear: new Date().getFullYear(),
      selectedMonth: new Date().getMonth() + 1,

      // Load business plans for an office
      loadBusinessPlans: async (officeId: string, year?: number) => {
        set({ loading: true, error: null });
        
        try {
          const params = new URLSearchParams({ office_id: officeId });
          if (year) {
            params.append('year', year.toString());
          }
          
          const response = await fetch(`${API_BASE}?${params}`);
          if (!response.ok) {
            throw new Error(`Failed to load business plans: ${response.statusText}`);
          }
          
          const plans: MonthlyBusinessPlan[] = await response.json();
          
          set({ 
            monthlyPlans: plans,
            loading: false 
          });
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to load business plans',
            loading: false 
          });
        }
      },

      // Load workforce distribution for an office
      loadWorkforceDistribution: async (officeId: string) => {
        set({ loading: true, error: null });
        
        try {
          const response = await fetch(`/offices/${officeId}/workforce`);
          if (!response.ok) {
            throw new Error(`Failed to load workforce: ${response.statusText}`);
          }
          
          const workforce: WorkforceDistribution = await response.json();
          
          set({ 
            currentWorkforce: workforce,
            loading: false 
          });
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to load workforce',
            loading: false 
          });
        }
      },

      // Load complete office summary
      loadOfficeSummary: async (officeId: string) => {
        set({ loading: true, error: null });
        
        try {
          const response = await fetch(`/offices/${officeId}/summary`);
          if (!response.ok) {
            throw new Error(`Failed to load office summary: ${response.statusText}`);
          }
          
          const summary: OfficeBusinessPlanSummary = await response.json();
          
          set({ 
            monthlyPlans: summary.monthly_plans || [],
            currentWorkforce: summary.workforce_distribution || null,
            loading: false 
          });
          
          return summary;
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to load office summary',
            loading: false 
          });
          throw error;
        }
      },

      // Create new monthly plan
      createMonthlyPlan: async (planData) => {
        set({ loading: true, error: null });
        
        try {
          const response = await fetch(API_BASE, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(planData),
          });
          
          if (!response.ok) {
            throw new Error(`Failed to create business plan: ${response.statusText}`);
          }
          
          const newPlan: MonthlyBusinessPlan = await response.json();
          
          const currentPlans = get().monthlyPlans;
          const updatedPlans = [...currentPlans, newPlan];
          
          set({ 
            monthlyPlans: updatedPlans,
            currentPlan: newPlan,
            loading: false 
          });
          
          return newPlan;
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to create business plan',
            loading: false 
          });
          throw error;
        }
      },

      // Update existing monthly plan
      updateMonthlyPlan: async (plan) => {
        set({ loading: true, error: null });
        
        try {
          const response = await fetch(`${API_BASE}/${plan.id}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(plan),
          });
          
          if (!response.ok) {
            throw new Error(`Failed to update business plan: ${response.statusText}`);
          }
          
          const updatedPlan: MonthlyBusinessPlan = await response.json();
          
          const currentPlans = get().monthlyPlans;
          const updatedPlans = currentPlans.map(p => 
            p.id === updatedPlan.id ? updatedPlan : p
          );
          
          set({ 
            monthlyPlans: updatedPlans,
            currentPlan: get().currentPlan?.id === updatedPlan.id ? updatedPlan : get().currentPlan,
            loading: false 
          });
          
          return updatedPlan;
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to update business plan',
            loading: false 
          });
          throw error;
        }
      },

      // Update a specific plan entry
      updatePlanEntry: async (planId: string, entry: MonthlyPlanEntry) => {
        const currentPlans = get().monthlyPlans;
        const planIndex = currentPlans.findIndex(p => p.id === planId);
        
        if (planIndex === -1) {
          throw new Error('Plan not found');
        }
        
        const plan = currentPlans[planIndex];
        const entryIndex = plan.entries.findIndex(e => 
          e.role === entry.role && e.level === entry.level
        );
        
        if (entryIndex === -1) {
          // Add new entry
          plan.entries.push(entry);
        } else {
          // Update existing entry
          plan.entries[entryIndex] = entry;
        }
        
        // Update the plan
        await get().updateMonthlyPlan(plan);
      },

      // Delete monthly plan
      deleteMonthlyPlan: async (planId: string) => {
        set({ loading: true, error: null });
        
        try {
          const response = await fetch(`${API_BASE}/${planId}`, {
            method: 'DELETE',
          });
          
          if (!response.ok) {
            throw new Error(`Failed to delete business plan: ${response.statusText}`);
          }
          
          const currentPlans = get().monthlyPlans;
          const updatedPlans = currentPlans.filter(p => p.id !== planId);
          
          set({ 
            monthlyPlans: updatedPlans,
            currentPlan: get().currentPlan?.id === planId ? null : get().currentPlan,
            loading: false 
          });
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to delete business plan',
            loading: false 
          });
          throw error;
        }
      },

      // Copy plan template between offices
      copyPlanTemplate: async (sourceOfficeId: string, targetOfficeId: string, year: number, month: number) => {
        set({ loading: true, error: null });
        
        try {
          const response = await fetch(`${API_BASE}/copy-template`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              source_office_id: sourceOfficeId,
              target_office_id: targetOfficeId,
              year,
              month,
            }),
          });
          
          if (!response.ok) {
            throw new Error(`Failed to copy template: ${response.statusText}`);
          }
          
          const newPlan: MonthlyBusinessPlan = await response.json();
          
          // Reload plans if targeting current office
          const currentPlans = get().monthlyPlans;
          if (currentPlans.length > 0 && currentPlans[0].office_id === targetOfficeId) {
            await get().loadBusinessPlans(targetOfficeId);
          }
          
          set({ loading: false });
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to copy template',
            loading: false 
          });
          throw error;
        }
      },

      // Bulk update multiple plans
      bulkUpdatePlans: async (officeId: string, plans: MonthlyBusinessPlan[]) => {
        set({ loading: true, error: null });
        
        try {
          const response = await fetch(`${API_BASE}/bulk-update`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              office_id: officeId,
              plans,
            }),
          });
          
          if (!response.ok) {
            throw new Error(`Failed to bulk update plans: ${response.statusText}`);
          }
          
          const updatedPlans: MonthlyBusinessPlan[] = await response.json();
          
          set({ 
            monthlyPlans: updatedPlans,
            loading: false 
          });
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to bulk update plans',
            loading: false 
          });
          throw error;
        }
      },

      // Set selected time period
      setSelectedPeriod: (year: number, month: number) => {
        set({ selectedYear: year, selectedMonth: month });
        
        // Update current plan if available
        const plan = get().getPlanForMonth(year, month);
        set({ currentPlan: plan || null });
      },

      // Clear error state
      clearError: () => set({ error: null }),

      // Get plan for specific month
      getPlanForMonth: (year: number, month: number) => {
        return get().monthlyPlans.find(plan => 
          plan.year === year && plan.month === month
        );
      },

      // Get all plans for a year
      getPlansForYear: (year: number) => {
        return get().monthlyPlans.filter(plan => plan.year === year);
      },

      // Get all available years
      getAvailableYears: () => {
        const years = get().monthlyPlans.map(plan => plan.year);
        return [...new Set(years)].sort((a, b) => b - a); // Descending order
      },
    }),
    {
      name: 'business-plan-store',
      partialize: (state) => ({
        // Only persist essential data
        selectedYear: state.selectedYear,
        selectedMonth: state.selectedMonth,
      }),
    }
  )
);

// Computed selectors for easier access
export const useCurrentBusinessPlan = () => useBusinessPlanStore(state => state.currentPlan);
export const useBusinessPlanLoading = () => useBusinessPlanStore(state => state.loading);
export const useBusinessPlanError = () => useBusinessPlanStore(state => state.error);
export const useSelectedPeriod = () => useBusinessPlanStore(state => ({ 
  year: state.selectedYear, 
  month: state.selectedMonth 
}));
export const useCurrentWorkforce = () => useBusinessPlanStore(state => state.currentWorkforce);