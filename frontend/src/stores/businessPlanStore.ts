/**
 * Business plan state management with Zustand
 * Handles comprehensive business plan data and operations with new structure
 */
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { 
  MonthlyBusinessPlan, 
  MonthlyPlanEntry, 
  WorkforceDistribution,
  OfficeBusinessPlanSummary 
} from '../types/office';
import {
  BusinessPlanData,
  BusinessPlanMetadata,
  BusinessPlanStatus,
  BusinessPlanType,
  FormattedValue,
  createEmptyBusinessPlan
} from '../types/business-plan';
import { CurrencyCode, CurrencyFormatter } from '../utils/currency';

interface BusinessPlanStoreState {
  // Legacy monthly plan data (maintained for compatibility)
  monthlyPlans: MonthlyBusinessPlan[];
  workforceDistributions: WorkforceDistribution[];
  currentPlan: MonthlyBusinessPlan | null;
  currentWorkforce: WorkforceDistribution | null;
  
  // Comprehensive business plan data (new structure)
  businessPlans: BusinessPlanData[];
  currentBusinessPlan: BusinessPlanData | null;
  selectedBusinessPlanId: string | null;
  
  // UI state
  loading: boolean;
  error: string | null;
  selectedYear: number;
  selectedMonth: number;
  defaultCurrency: CurrencyCode;
  
  // Legacy actions (maintained for compatibility)
  loadBusinessPlans: (officeId: string, year?: number) => Promise<void>;
  loadWorkforceDistribution: (officeId: string) => Promise<void>;
  loadOfficeSummary: (officeId: string) => Promise<OfficeBusinessPlanSummary>;
  
  createMonthlyPlan: (plan: Omit<MonthlyBusinessPlan, 'id' | 'created_at' | 'updated_at'>) => Promise<MonthlyBusinessPlan>;
  updateMonthlyPlan: (plan: MonthlyBusinessPlan) => Promise<MonthlyBusinessPlan>;
  updatePlanEntry: (planId: string, entry: MonthlyPlanEntry) => Promise<void>;
  deleteMonthlyPlan: (planId: string) => Promise<void>;
  
  copyPlanTemplate: (sourceOfficeId: string, targetOfficeId: string, year: number, month: number) => Promise<void>;
  bulkUpdatePlans: (officeId: string, plans: MonthlyBusinessPlan[]) => Promise<void>;
  
  // Comprehensive business plan actions (new structure)
  loadComprehensiveBusinessPlans: (officeId?: string) => Promise<void>;
  createBusinessPlan: (metadata: Omit<BusinessPlanMetadata, 'id' | 'createdAt' | 'lastUpdated'>) => Promise<BusinessPlanData>;
  updateBusinessPlan: (businessPlan: BusinessPlanData) => Promise<BusinessPlanData>;
  deleteBusinessPlan: (businessPlanId: string) => Promise<void>;
  duplicateBusinessPlan: (businessPlanId: string, newName: string) => Promise<BusinessPlanData>;
  
  // Field value operations
  updateFieldValue: (businessPlanId: string, fieldPath: string, value: FormattedValue) => Promise<void>;
  updateSectionData: (businessPlanId: string, sectionId: string, sectionData: Record<string, FormattedValue>) => Promise<void>;
  calculateDerivedFields: (businessPlanId: string) => Promise<void>;
  
  // Business plan selection and management
  setCurrentBusinessPlan: (businessPlanId: string | null) => void;
  getBusinessPlan: (businessPlanId: string) => BusinessPlanData | undefined;
  getBusinessPlansByOffice: (officeId: string) => BusinessPlanData[];
  getBusinessPlansByStatus: (status: BusinessPlanStatus) => BusinessPlanData[];
  
  // Currency operations
  setDefaultCurrency: (currency: CurrencyCode) => void;
  convertBusinessPlanCurrency: (businessPlanId: string, targetCurrency: CurrencyCode) => Promise<BusinessPlanData>;
  
  // UI actions
  setSelectedPeriod: (year: number, month: number) => void;
  clearError: () => void;
  
  // Legacy utils (maintained for compatibility)
  getPlanForMonth: (year: number, month: number) => MonthlyBusinessPlan | undefined;
  getPlansForYear: (year: number) => MonthlyBusinessPlan[];
  getAvailableYears: () => number[];
  
  // Comprehensive business plan utils
  getFormattedValue: (businessPlanId: string, fieldPath: string, currency?: CurrencyCode) => string;
  validateBusinessPlan: (businessPlanId: string) => { isValid: boolean; errors: string[] };
  exportBusinessPlan: (businessPlanId: string, format: 'json' | 'csv' | 'excel') => Promise<Blob>;
}

const API_BASE = '/api/business-plans';
const COMPREHENSIVE_API_BASE = '/api/comprehensive-business-plans';

export const useBusinessPlanStore = create<BusinessPlanStoreState>()(
  devtools(
    (set, get) => ({
      // Legacy initial state (maintained for compatibility)
      monthlyPlans: [],
      workforceDistributions: [],
      currentPlan: null,
      currentWorkforce: null,
      
      // Comprehensive business plan initial state
      businessPlans: [],
      currentBusinessPlan: null,
      selectedBusinessPlanId: null,
      
      // UI state
      loading: false,
      error: null,
      selectedYear: new Date().getFullYear(),
      selectedMonth: new Date().getMonth() + 1,
      defaultCurrency: 'EUR' as CurrencyCode,

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
          const response = await fetch(`http://localhost:8000/offices/${officeId}/workforce`);
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
          const response = await fetch(`http://localhost:8000/offices/${officeId}/summary`);
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

      // ==========================================
      // COMPREHENSIVE BUSINESS PLAN ACTIONS
      // ==========================================

      // Load comprehensive business plans
      loadComprehensiveBusinessPlans: async (officeId?: string) => {
        set({ loading: true, error: null });
        
        try {
          const params = new URLSearchParams();
          if (officeId) {
            params.append('office_id', officeId);
          }
          
          const response = await fetch(`${COMPREHENSIVE_API_BASE}?${params}`);
          if (!response.ok) {
            throw new Error(`Failed to load business plans: ${response.statusText}`);
          }
          
          const businessPlans: BusinessPlanData[] = await response.json();
          
          set({ 
            businessPlans,
            loading: false 
          });
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to load business plans',
            loading: false 
          });
        }
      },

      // Create new comprehensive business plan
      createBusinessPlan: async (metadata) => {
        set({ loading: true, error: null });
        
        try {
          // Convert metadata to CreateBusinessPlanRequest format
          const request = {
            planName: metadata.planName,
            description: metadata.description,
            office: metadata.office,
            year: metadata.year,
            planType: metadata.planType,
            currencyCode: metadata.currencyCode
          };
          const newBusinessPlan = createEmptyBusinessPlan(request, 'system', 'System User');
          
          const response = await fetch(COMPREHENSIVE_API_BASE, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(newBusinessPlan),
          });
          
          if (!response.ok) {
            throw new Error(`Failed to create business plan: ${response.statusText}`);
          }
          
          const createdPlan: BusinessPlanData = await response.json();
          
          const currentPlans = get().businessPlans;
          const updatedPlans = [...currentPlans, createdPlan];
          
          set({ 
            businessPlans: updatedPlans,
            currentBusinessPlan: createdPlan,
            selectedBusinessPlanId: createdPlan.metadata.id,
            loading: false 
          });
          
          return createdPlan;
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to create business plan',
            loading: false 
          });
          throw error;
        }
      },

      // Update comprehensive business plan
      updateBusinessPlan: async (businessPlan) => {
        set({ loading: true, error: null });
        
        try {
          // Update lastUpdated timestamp
          businessPlan.metadata.lastUpdated = new Date();
          
          const response = await fetch(`${COMPREHENSIVE_API_BASE}/${businessPlan.metadata.id}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(businessPlan),
          });
          
          if (!response.ok) {
            throw new Error(`Failed to update business plan: ${response.statusText}`);
          }
          
          const updatedPlan: BusinessPlanData = await response.json();
          
          const currentPlans = get().businessPlans;
          const updatedPlans = currentPlans.map(p => 
            p.metadata.id === updatedPlan.metadata.id ? updatedPlan : p
          );
          
          set({ 
            businessPlans: updatedPlans,
            currentBusinessPlan: get().currentBusinessPlan?.metadata.id === updatedPlan.metadata.id ? updatedPlan : get().currentBusinessPlan,
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

      // Delete comprehensive business plan
      deleteBusinessPlan: async (businessPlanId: string) => {
        set({ loading: true, error: null });
        
        try {
          const response = await fetch(`${COMPREHENSIVE_API_BASE}/${businessPlanId}`, {
            method: 'DELETE',
          });
          
          if (!response.ok) {
            throw new Error(`Failed to delete business plan: ${response.statusText}`);
          }
          
          const currentPlans = get().businessPlans;
          const updatedPlans = currentPlans.filter(p => p.metadata.id !== businessPlanId);
          
          set({ 
            businessPlans: updatedPlans,
            currentBusinessPlan: get().currentBusinessPlan?.metadata.id === businessPlanId ? null : get().currentBusinessPlan,
            selectedBusinessPlanId: get().selectedBusinessPlanId === businessPlanId ? null : get().selectedBusinessPlanId,
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

      // Duplicate comprehensive business plan
      duplicateBusinessPlan: async (businessPlanId: string, newName: string) => {
        set({ loading: true, error: null });
        
        try {
          const sourcePlan = get().businessPlans.find(p => p.metadata.id === businessPlanId);
          if (!sourcePlan) {
            throw new Error('Source business plan not found');
          }

          // Create duplicate with new metadata
          const duplicateMetadata = {
            ...sourcePlan.metadata,
            planName: newName,
            status: 'draft' as BusinessPlanStatus,
            progress: 0,
            isOfficial: false,
            createdAt: new Date(),
            lastUpdated: new Date(),
          };
          
          // Convert metadata to CreateBusinessPlanRequest format
          const duplicateRequest = {
            planName: duplicateMetadata.planName,
            description: duplicateMetadata.description,
            office: duplicateMetadata.office,
            year: duplicateMetadata.year,
            planType: duplicateMetadata.planType,
            currencyCode: duplicateMetadata.currencyCode
          };
          const duplicatePlan = createEmptyBusinessPlan(duplicateRequest, 'system', 'System User');
          // Copy over the section data
          duplicatePlan.sectionData = { ...sourcePlan.sectionData };
          
          const response = await fetch(COMPREHENSIVE_API_BASE, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(duplicatePlan),
          });
          
          if (!response.ok) {
            throw new Error(`Failed to duplicate business plan: ${response.statusText}`);
          }
          
          const createdPlan: BusinessPlanData = await response.json();
          
          const currentPlans = get().businessPlans;
          const updatedPlans = [...currentPlans, createdPlan];
          
          set({ 
            businessPlans: updatedPlans,
            loading: false 
          });
          
          return createdPlan;
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to duplicate business plan',
            loading: false 
          });
          throw error;
        }
      },

      // Update field value in business plan
      updateFieldValue: async (businessPlanId: string, fieldPath: string, value: FormattedValue) => {
        const businessPlan = get().businessPlans.find(p => p.metadata.id === businessPlanId);
        if (!businessPlan) {
          throw new Error('Business plan not found');
        }

        // Update the field value in the section data
        const pathParts = fieldPath.split('.');
        let current: any = businessPlan.sectionData;
        
        for (let i = 0; i < pathParts.length - 1; i++) {
          if (!current[pathParts[i]]) {
            current[pathParts[i]] = {};
          }
          current = current[pathParts[i]];
        }
        
        current[pathParts[pathParts.length - 1]] = value;
        
        // Update the business plan
        await get().updateBusinessPlan(businessPlan);
      },

      // Update section data in business plan
      updateSectionData: async (businessPlanId: string, sectionId: string, sectionData: Record<string, FormattedValue>) => {
        const businessPlan = get().businessPlans.find(p => p.metadata.id === businessPlanId);
        if (!businessPlan) {
          throw new Error('Business plan not found');
        }

        // Update section data
        if (!businessPlan.sectionData[sectionId as keyof typeof businessPlan.sectionData]) {
          // Initialize section if it doesn't exist (this shouldn't normally happen)
          console.warn(`Section ${sectionId} not found in business plan`);
          return;
        }
        
        // Update the section's field data
        const section = businessPlan.sectionData[sectionId as keyof typeof businessPlan.sectionData];
        Object.entries(sectionData).forEach(([fieldId, value]) => {
          // Update field values in the section's field maps
          if (section.officeLevelFields.has(fieldId)) {
            section.officeLevelFields.set(fieldId, value);
          } else {
            // For role-level fields, we need to determine which role and level to update
            // This would require additional parameters or a different approach
            // For now, we'll just store it as an office-level field
            section.officeLevelFields.set(fieldId, value);
          }
        });
        
        // Update the business plan
        await get().updateBusinessPlan(businessPlan);
      },

      // Calculate derived fields for business plan
      calculateDerivedFields: async (businessPlanId: string) => {
        set({ loading: true, error: null });
        
        try {
          const response = await fetch(`${COMPREHENSIVE_API_BASE}/${businessPlanId}/calculate`, {
            method: 'POST',
          });
          
          if (!response.ok) {
            throw new Error(`Failed to calculate derived fields: ${response.statusText}`);
          }
          
          const updatedPlan: BusinessPlanData = await response.json();
          
          const currentPlans = get().businessPlans;
          const updatedPlans = currentPlans.map(p => 
            p.metadata.id === updatedPlan.metadata.id ? updatedPlan : p
          );
          
          set({ 
            businessPlans: updatedPlans,
            currentBusinessPlan: get().currentBusinessPlan?.metadata.id === updatedPlan.metadata.id ? updatedPlan : get().currentBusinessPlan,
            loading: false 
          });
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to calculate derived fields',
            loading: false 
          });
          throw error;
        }
      },

      // Business plan selection and management
      setCurrentBusinessPlan: (businessPlanId: string | null) => {
        const businessPlan = businessPlanId ? get().businessPlans.find(p => p.metadata.id === businessPlanId) : null;
        set({ 
          selectedBusinessPlanId: businessPlanId,
          currentBusinessPlan: businessPlan || null 
        });
      },

      getBusinessPlan: (businessPlanId: string) => {
        return get().businessPlans.find(p => p.metadata.id === businessPlanId);
      },

      getBusinessPlansByOffice: (officeId: string) => {
        return get().businessPlans.filter(p => p.metadata.office === officeId);
      },

      getBusinessPlansByStatus: (status: BusinessPlanStatus) => {
        return get().businessPlans.filter(p => p.metadata.status === status);
      },

      // Currency operations
      setDefaultCurrency: (currency: CurrencyCode) => {
        set({ defaultCurrency: currency });
      },

      convertBusinessPlanCurrency: async (businessPlanId: string, targetCurrency: CurrencyCode) => {
        set({ loading: true, error: null });
        
        try {
          const response = await fetch(`${COMPREHENSIVE_API_BASE}/${businessPlanId}/convert-currency`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ targetCurrency }),
          });
          
          if (!response.ok) {
            throw new Error(`Failed to convert currency: ${response.statusText}`);
          }
          
          const convertedPlan: BusinessPlanData = await response.json();
          
          const currentPlans = get().businessPlans;
          const updatedPlans = currentPlans.map(p => 
            p.metadata.id === convertedPlan.metadata.id ? convertedPlan : p
          );
          
          set({ 
            businessPlans: updatedPlans,
            currentBusinessPlan: get().currentBusinessPlan?.metadata.id === convertedPlan.metadata.id ? convertedPlan : get().currentBusinessPlan,
            loading: false 
          });
          
          return convertedPlan;
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to convert currency',
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

      // ==========================================
      // COMPREHENSIVE BUSINESS PLAN UTILS
      // ==========================================

      // Get formatted value from business plan
      getFormattedValue: (businessPlanId: string, fieldPath: string, currency?: CurrencyCode) => {
        const businessPlan = get().businessPlans.find(p => p.metadata.id === businessPlanId);
        if (!businessPlan) {
          return '0';
        }

        const pathParts = fieldPath.split('.');
        let current: any = businessPlan.sectionData;
        
        for (const part of pathParts) {
          if (!current || !current[part]) {
            return '0';
          }
          current = current[part];
        }

        // Format the value if it's a FormattedValue
        if (current && typeof current === 'object' && 'raw' in current && 'formatted' in current) {
          const formattedValue = current as FormattedValue;
          const targetCurrency = currency || businessPlan.metadata.currencyCode;
          const formatter = new CurrencyFormatter(targetCurrency);
          
          switch (formattedValue.valueType) {
            case 'currency':
              return formatter.format(formattedValue.raw, { showSymbol: true });
            case 'percentage':
              return `${(formattedValue.raw * 100).toFixed(1)}%`;
            case 'count':
              return Math.round(formattedValue.raw).toString();
            case 'fte':
              return `${formattedValue.raw.toFixed(1)} FTE`;
            default:
              return formattedValue.raw.toString();
          }
        }

        return current?.toString() || '0';
      },

      // Validate business plan completeness and data integrity
      validateBusinessPlan: (businessPlanId: string) => {
        const businessPlan = get().businessPlans.find(p => p.metadata.id === businessPlanId);
        if (!businessPlan) {
          return { isValid: false, errors: ['Business plan not found'] };
        }

        const errors: string[] = [];

        // Check required metadata
        if (!businessPlan.metadata.planName.trim()) {
          errors.push('Plan name is required');
        }
        if (!businessPlan.metadata.office.trim()) {
          errors.push('Office selection is required');
        }
        if (businessPlan.metadata.year < new Date().getFullYear() - 5) {
          errors.push('Plan year seems too far in the past');
        }

        // Check section data completeness
        const requiredSections: (keyof typeof businessPlan.sectionData)[] = ['revenue', 'workforce', 'compensation', 'expenses'];
        for (const sectionId of requiredSections) {
          const section = businessPlan.sectionData[sectionId];
          if (!section || (section.officeLevelFields.size === 0 && section.roleLevelFields.size === 0)) {
            errors.push(`${sectionId} section is incomplete`);
          }
        }

        // Validate data consistency
        const revenueSection = businessPlan.sectionData.revenue;
        const workforceSection = businessPlan.sectionData.workforce;
        
        if (revenueSection && workforceSection) {
          // Check if revenue projections align with workforce plans
          const totalRevenue = revenueSection.yearlyTotal;
          const totalFte = workforceSection.yearlyTotal;
          
          if (totalRevenue && totalFte && totalRevenue.raw > 0 && totalFte.raw > 0) {
            const revenuePerFte = totalRevenue.raw / totalFte.raw;
            if (revenuePerFte > 500000) { // Sanity check: >500k per FTE seems high
              errors.push('Revenue per FTE seems unusually high - please verify calculations');
            }
          }
        }

        return {
          isValid: errors.length === 0,
          errors
        };
      },

      // Export business plan in various formats
      exportBusinessPlan: async (businessPlanId: string, format: 'json' | 'csv' | 'excel') => {
        const businessPlan = get().businessPlans.find(p => p.metadata.id === businessPlanId);
        if (!businessPlan) {
          throw new Error('Business plan not found');
        }

        try {
          const response = await fetch(`${COMPREHENSIVE_API_BASE}/${businessPlanId}/export`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ format }),
          });

          if (!response.ok) {
            throw new Error(`Failed to export business plan: ${response.statusText}`);
          }

          const blob = await response.blob();
          return blob;
        } catch (error) {
          throw new Error(`Failed to export business plan: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
      },
    }),
    {
      name: 'business-plan-store',
      partialize: (state: BusinessPlanStoreState) => ({
        // Only persist essential UI state
        selectedYear: state.selectedYear,
        selectedMonth: state.selectedMonth,
        selectedBusinessPlanId: state.selectedBusinessPlanId,
        defaultCurrency: state.defaultCurrency,
      }),
    }
  )
);

// ==========================================
// LEGACY SELECTORS (maintained for compatibility)
// ==========================================
export const useCurrentBusinessPlan = () => useBusinessPlanStore(state => state.currentPlan);
export const useBusinessPlanLoading = () => useBusinessPlanStore(state => state.loading);
export const useBusinessPlanError = () => useBusinessPlanStore(state => state.error);
export const useSelectedPeriod = () => useBusinessPlanStore(state => ({ 
  year: state.selectedYear, 
  month: state.selectedMonth 
}));
export const useCurrentWorkforce = () => useBusinessPlanStore(state => state.currentWorkforce);

// ==========================================
// COMPREHENSIVE BUSINESS PLAN SELECTORS
// ==========================================

// Main business plan selectors
export const useComprehensiveBusinessPlans = () => useBusinessPlanStore(state => state.businessPlans);
export const useCurrentComprehensiveBusinessPlan = () => useBusinessPlanStore(state => state.currentBusinessPlan);
export const useSelectedBusinessPlanId = () => useBusinessPlanStore(state => state.selectedBusinessPlanId);

// Business plan management selectors
export const useBusinessPlanActions = () => useBusinessPlanStore(state => ({
  loadComprehensiveBusinessPlans: state.loadComprehensiveBusinessPlans,
  createBusinessPlan: state.createBusinessPlan,
  updateBusinessPlan: state.updateBusinessPlan,
  deleteBusinessPlan: state.deleteBusinessPlan,
  duplicateBusinessPlan: state.duplicateBusinessPlan,
  setCurrentBusinessPlan: state.setCurrentBusinessPlan,
}));

// Field and data management selectors
export const useBusinessPlanDataActions = () => useBusinessPlanStore(state => ({
  updateFieldValue: state.updateFieldValue,
  updateSectionData: state.updateSectionData,
  calculateDerivedFields: state.calculateDerivedFields,
  getFormattedValue: state.getFormattedValue,
  validateBusinessPlan: state.validateBusinessPlan,
}));

// Filtering and search selectors
export const useBusinessPlanFilters = () => useBusinessPlanStore(state => ({
  getBusinessPlansForOffice: state.getBusinessPlansByOffice,
  getBusinessPlansByStatus: state.getBusinessPlansByStatus,
  getBusinessPlan: state.getBusinessPlan,
}));

// Currency management selectors
export const useCurrencyManagement = () => useBusinessPlanStore(state => ({
  defaultCurrency: state.defaultCurrency,
  setDefaultCurrency: state.setDefaultCurrency,
  convertBusinessPlanCurrency: state.convertBusinessPlanCurrency,
}));

// Export and utility selectors
export const useBusinessPlanUtils = () => useBusinessPlanStore(state => ({
  exportBusinessPlan: state.exportBusinessPlan,
  validateBusinessPlan: state.validateBusinessPlan,
  getFormattedValue: state.getFormattedValue,
}));

// Convenience hooks for common use cases
export const useBusinessPlanMetadata = (businessPlanId?: string) => 
  useBusinessPlanStore(state => {
    if (!businessPlanId) return null;
    const plan = state.businessPlans.find(p => p.metadata.id === businessPlanId);
    return plan?.metadata || null;
  });

export const useBusinessPlanValidation = (businessPlanId?: string) => 
  useBusinessPlanStore(state => {
    if (!businessPlanId) return { isValid: false, errors: ['No business plan selected'] };
    return state.validateBusinessPlan(businessPlanId);
  });

export const useOfficePlans = (officeId: string) => 
  useBusinessPlanStore(state => 
    state.businessPlans.filter(p => p.metadata.office === officeId)
  );

export const useOfficialPlans = () => 
  useBusinessPlanStore(state => 
    state.businessPlans.filter(p => p.metadata.isOfficial)
  );

export const useDraftPlans = () => 
  useBusinessPlanStore(state => 
    state.businessPlans.filter(p => p.metadata.status === 'draft')
  );

export const useApprovedPlans = () => 
  useBusinessPlanStore(state => 
    state.businessPlans.filter(p => p.metadata.status === 'approved')
  );