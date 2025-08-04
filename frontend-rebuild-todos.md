# SimpleSim UI Rebuild - Implementation Todos

## Foundation Tasks (Weeks 1-3) - HIGH PRIORITY

### foundation-1: Set up shadcn/ui dashboard-01 base template
**Status:** In Progress  
**Priority:** High  
**Description:** Install dashboard-01 template, configure with existing Tailwind theme, remove AppShell/AppLayoutV2 dual systems

### foundation-2: Consolidate routing system
**Status:** Pending  
**Priority:** High  
**Description:** Remove dual AppRoutes/EnhancedRoutes, implement single unified routing system

### foundation-3: Complete component inventory audit
**Status:** Pending  
**Priority:** High  
**Description:** Map all V2 vs legacy components, identify duplicates, create consolidation plan

### foundation-4: Implement unified design token system
**Status:** Pending  
**Priority:** High  
**Description:** Consolidate design tokens from design/ folder into single source of truth

### foundation-5: Extract business logic from UI components
**Status:** Pending  
**Priority:** High  
**Description:** Separate ScenarioWizardV2 logic, create service layer for simulation operations

## Component Consolidation (Weeks 4-7) - MEDIUM PRIORITY

### component-1: Consolidate table implementations
**Status:** Pending  
**Priority:** Medium  
**Description:** Replace all table variations with single shadcn DataTable component

### component-2: Standardize button implementations
**Status:** Pending  
**Priority:** Medium  
**Description:** Remove button duplicates, use single shadcn Button with variants

### component-3: Consolidate modal/dialog implementations
**Status:** Pending  
**Priority:** Medium  
**Description:** Replace all modal variations with single shadcn Dialog component

## Feature Rebuilding (Weeks 4-7) - MEDIUM PRIORITY

### feature-1: Rebuild main dashboard
**Status:** Pending  
**Priority:** Medium  
**Description:** Implement shadcn dashboard-01 pattern with KPI cards and navigation sidebar

### feature-2: Rebuild scenario management
**Status:** Pending  
**Priority:** Medium  
**Description:** Consolidate ScenariosV2 and ScenarioWizardV2 into unified scenario interface

### feature-3: Rebuild business planning interface
**Status:** Pending  
**Priority:** Medium  
**Description:** Modernize BusinessPlanningV2 with expandable grid using shadcn components

## Quality & Cleanup - LOW PRIORITY

### quality-1: Clean up state management
**Status:** Pending  
**Priority:** Low  
**Description:** Consolidate Zustand stores, remove unused state management code

## Notes

- All foundation tasks must be completed before component consolidation
- Component consolidation must be completed before feature rebuilding
- Business logic separation is critical for maintainable architecture
- Each task must preserve 100% existing functionality during migration