# Scenario System Redesign

## Overview

This document outlines the complete redesign of the SimpleSim scenario system to address user experience issues and support different user personas (Office Owners and Executives).

## Table of Contents

1. [Current Problems](#current-problems)
2. [User Personas](#user-personas)
3. [Proposed Solution](#proposed-solution)
4. [UI/UX Design](#uiux-design)
5. [User Stories](#user-stories)
6. [Data Flow & Architecture](#data-flow--architecture)
7. [Technical Implementation](#technical-implementation)
8. [Migration Plan](#migration-plan)

## Current Problems

### 1. Confusing Data Flow
- **Baseline Input**: Monthly recruitment/churn numbers (absolute values)
- **Levers**: Multipliers that modify the baseline
- **Config**: Base office configuration with FTE, prices, etc.
- **Progression**: CAT curves for career advancement

### 2. Unclear User Mental Model
- Users don't understand the difference between "baseline input" and "levers"
- The relationship between absolute numbers and multipliers is confusing
- Progression levers affect CAT curves, which is not intuitive

### 3. Complex Data Structures
```typescript
// Current messy structure
{
  baseline_input: {
    global: {
      recruitment: { Consultant: { '202501': { A: 20, AC: 8 } } },
      churn: { Consultant: { '202501': { A: 2, AC: 4 } } }
    }
  },
  levers: {
    recruitment: { A: 1.2, AC: 1.1 },
    churn: { A: 0.8, AC: 0.9 },
    progression: { A: 1.1, AC: 1.05 }
  }
}
```

### 4. No User Persona Support
- Single interface for all users
- No distinction between office-level and company-level planning
- Missing approval workflows and collaboration features

## User Personas

### Office Owner
- **Focus**: Their specific office(s)
- **Goal**: Create detailed business plans
- **Data**: Granular, office-specific numbers
- **Actions**: Enter actual values, see detailed outcomes
- **Permissions**: Can edit their office data, create business plans

### Executive
- **Focus**: Multi-office, company-wide view
- **Goal**: Strategic scenario planning
- **Data**: High-level KPIs and trends
- **Actions**: Apply broad adjustments, compare scenarios
- **Permissions**: Can view all offices, create company scenarios, approve plans

## Proposed Solution

### 1. Simplified User Mental Model

Instead of confusing "baseline input" vs "levers", use a more intuitive approach:

#### A. "Current State" (Baseline)
- Show current FTE, recruitment rates, churn rates
- Users can modify these directly
- This becomes the "baseline" for the simulation

#### B. "Scenario Adjustments" (Levers)
- Simple sliders that adjust the baseline
- Clear labels: "Increase/Decrease Recruitment by X%"
- Immediate visual feedback showing the impact

### 2. Cleaner Data Structure

```typescript
// New simplified structure
{
  current_state: {
    offices: {
      "Stockholm": {
        roles: {
          "Consultant": {
            "A": {
              fte: 50,
              monthly_recruitment: 5,  // Average per month
              monthly_churn: 0.02,     // Rate (2%)
              progression_rate: 0.1    // Rate (10%)
            }
          }
        }
      }
    }
  },
  adjustments: {
    recruitment: { "Consultant": { "A": 1.10 } }, // +10% recruitment
    churn: { "Consultant": { "A": 0.95 } },       // -5% churn
    progression: { "Consultant": { "A": 1.20 } }  // +20% progression
  }
}
```

## UI/UX Design

### Office Owner Interface

#### Dashboard View
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Business Plan Builder - Stockholm Office                    [User: Anna]    │
├─────────────────────────────────────────────────────────────────────────────┤
│ [Stockholm ▼] [Berlin] [Amsterdam] [View All Offices]                      │
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ Current Status - Stockholm Office                                       │ │
│ │ Total FTE: 100 | Revenue: €500K | Margin: 15% | Growth: +5%            │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ My Business Plans                                                       │ │
│ │ [Create New Plan] [Import from Excel]                                   │ │
│ │                                                                         │ │
│ │ ┌─────────────────────────────────────────────────────────────────────┐ │ │
│ │ │ Q1 2025 Growth Plan                    [Edit] [Run] [Share] [Delete]│ │
│ │ │ Target: +20 FTE | Status: Draft | Created: 2 days ago              │ │
│ │ └─────────────────────────────────────────────────────────────────────┘ │ │
│ │                                                                         │ │
│ │ ┌─────────────────────────────────────────────────────────────────────┐ │ │
│ │ │ Consultant Expansion Plan             [Edit] [Run] [Share] [Delete]│ │
│ │ │ Target: +15 FTE | Status: Approved | Created: 1 week ago           │ │
│ │ └─────────────────────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Business Plan Editor
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Business Plan: Q1 2025 Growth Plan - Stockholm                            │
│ [Save Draft] [Run Plan] [Share with Executive] [Export]                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ Current State & Targets                                                 │ │
│ │ [Edit Mode: ON] [Reset to System Default] [Import from Excel]          │ │
│ │                                                                         │ │
│ │ Role       │ Level │ Current │ Target │ Recruit │ Churn │ Progression │ │
│ │            │       │   FTE   │  FTE   │ (per mo)│  (%)  │     (%)     │ │
│ ├────────────┼───────┼─────────┼────────┼─────────┼───────┼─────────────┤ │ │
│ │ Consultant │   A   │   50    │  [60]  │   [6]   │ [2.0] │   [10.0]   │ │ │
│ │ Consultant │  AC   │   30    │  [35]  │   [3]   │ [3.0] │    [8.0]   │ │ │
│ │ Consultant │   C   │   15    │  [18]  │   [2]   │ [5.0] │    [6.0]   │ │ │
│ │ Sales      │   A   │   20    │  [25]  │   [2]   │ [4.0] │   [12.0]   │ │ │
│ │ Sales      │  AM   │   10    │  [12]  │   [1]   │ [6.0] │   [15.0]   │ │ │
│ │ Operations │   A   │    5    │   [6]  │   [1]   │ [3.0] │    [5.0]   │ │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ Assumptions & Constraints                                               │ │
│ │ Revenue per FTE: [€5,000] | Cost per FTE: [€3,500] | Utilization: [85%]│ │
│ │ Max recruitment capacity: [15/month] | Budget constraint: [€100K]      │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Executive Interface

#### Executive Dashboard
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Scenario Simulator - Company Overview                     [User: CEO]      │
├─────────────────────────────────────────────────────────────────────────────┤
│ [All Offices] [Mature Offices] [Growth Offices] [Filter by Region]         │
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ Company Overview                                                        │ │
│ │ Total FTE: 1,240 | Revenue: €6.2M | Margin: 14.5% | Growth: +12%       │ │
│ │                                                                         │ │
│ │ Office      │ FTE │ Growth │ Revenue │ Margin │ Status │ Actions       │ │
│ ├─────────────┼─────┼────────┼─────────┼────────┼────────┼───────────────┤ │ │
│ │ Stockholm   │ 100 │  +5%   │ €500K   │  15%   │ ✅     │ [View] [Plan] │ │
│ │ Berlin      │ 180 │ +12%   │ €900K   │  14%   │ ✅     │ [View] [Plan] │ │
│ │ Amsterdam   │ 120 │ +20%   │ €600K   │  13%   │ ⚠️     │ [View] [Plan] │ │
│ │ Munich      │  80 │  +8%   │ €400K   │  15%   │ ✅     │ [View] [Plan] │ │
│ │ Copenhagen  │  60 │ +15%   │ €300K   │  14%   │ ✅     │ [View] [Plan] │ │
│ │ ...         │ ... │  ...   │   ...   │  ...   │ ...    │ ...            │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ Strategic Scenarios                                                     │ │
│ │ [Create New Scenario] [Compare Scenarios] [View Recommendations]       │ │
│ │                                                                         │ │
│ │ ┌─────────────────────────────────────────────────────────────────────┐ │ │
│ │ │ Aggressive Growth Q1 2025              [Edit] [Run] [Share] [Delete]│ │ │
│ │ │ +15% recruitment, -10% churn | Status: Approved | Impact: +€800K   │ │
│ │ └─────────────────────────────────────────────────────────────────────┘ │ │
│ │                                                                         │ │
│ │ ┌─────────────────────────────────────────────────────────────────────┐ │ │
│ │ │ Conservative Growth Q1 2025           [Edit] [Run] [Share] [Delete]│ │ │
│ │ │ +5% recruitment, -5% churn | Status: Draft | Impact: +€300K        │ │
│ │ └─────────────────────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

## User Stories

### Office Owner User Stories

#### Story 1: Create Q1 Business Plan
**As an Office Owner (Anna)**
**I want to create a detailed business plan for Q1 2025**
**So that I can plan growth and get executive approval**

**Acceptance Criteria:**
- Can select my office (Stockholm)
- Can see current FTE, revenue, and KPIs
- Can set target FTE for each role/level
- Can adjust recruitment and churn assumptions
- Can run the plan and see projected outcomes
- Can save the plan as a draft
- Can share the plan with executives

**User Flow:**
1. Anna logs in and sees Stockholm office dashboard
2. Clicks "Create New Plan" → "Q1 2025 Growth Plan"
3. Reviews current state (100 FTE, €500K revenue)
4. Sets targets: 120 FTE (+20), adjusts recruitment to 6/month
5. Runs plan and sees: 118 FTE achieved, €590K revenue
6. Saves plan and shares with CEO

#### Story 2: Adjust Plan Based on Constraints
**As an Office Owner (Anna)**
**I want to adjust my business plan when I hit constraints**
**So that I can create a realistic plan**

**Acceptance Criteria:**
- Can see constraints (budget, recruitment capacity)
- Can adjust targets when constraints are hit
- Can see impact of adjustments in real-time
- Can save multiple versions of the plan

#### Story 3: Compare Different Scenarios
**As an Office Owner (Anna)**
**I want to compare different growth scenarios**
**So that I can choose the best approach**

**Acceptance Criteria:**
- Can create multiple scenarios (conservative, aggressive)
- Can compare scenarios side-by-side
- Can see the trade-offs between scenarios
- Can recommend the best scenario

### Executive User Stories

#### Story 4: Review Office Business Plans
**As an Executive (CEO)**
**I want to review business plans from all offices**
**So that I can approve or provide feedback**

**Acceptance Criteria:**
- Can see all office business plans in one view
- Can drill down into specific office details
- Can approve, reject, or request changes
- Can see the aggregated impact of all plans

#### Story 5: Create Strategic Scenarios
**As an Executive (CEO)**
**I want to create company-wide growth scenarios**
**So that I can plan strategic initiatives**

**Acceptance Criteria:**
- Can apply global adjustments to all offices
- Can set office-specific adjustments
- Can see the aggregated impact across all offices
- Can compare different strategic approaches

#### Story 6: Monitor Plan Execution
**As an Executive (CEO)**
**I want to monitor the execution of approved plans**
**So that I can ensure we're on track**

**Acceptance Criteria:**
- Can see progress against approved plans
- Can identify offices that are behind schedule
- Can see aggregated progress across all offices
- Can take corrective action if needed

## Data Flow & Architecture

### Current Architecture (To Be Replaced)

```
Frontend → API Router → ScenarioService → Focused Services → Simulation Engine
```

### New Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Office Owner  │    │    Executive    │    │   System Admin  │
│     Interface   │    │    Interface    │    │    Interface    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   API Gateway   │
                    │  (Permission    │
                    │   Based)        │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Business Logic │
                    │     Layer       │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Business Plan   │    │   Scenario      │    │   User &        │
│   Service       │    │   Service       │    │   Permission    │
│                 │    │                 │    │   Service       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Data Layer     │
                    │                 │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Business Plan   │    │   Scenario      │    │   User          │
│   Storage       │    │   Storage       │    │   Storage       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Flow Diagrams

#### Office Owner Data Flow
```
1. Office Owner logs in
   ↓
2. System loads office data (FTE, revenue, etc.)
   ↓
3. Office Owner creates/edits business plan
   ↓
4. System validates plan against constraints
   ↓
5. Office Owner runs plan simulation
   ↓
6. System generates results and saves plan
   ↓
7. Office Owner shares plan with executive
   ↓
8. System notifies executive of pending approval
```

#### Executive Data Flow
```
1. Executive logs in
   ↓
2. System loads company overview (all offices)
   ↓
3. Executive reviews pending business plans
   ↓
4. Executive approves/rejects/requests changes
   ↓
5. System notifies office owners of decisions
   ↓
6. Executive creates strategic scenarios
   ↓
7. System applies scenarios to all offices
   ↓
8. Executive compares scenarios and makes decisions
```

#### Plan Approval Workflow
```
1. Office Owner submits plan
   ↓
2. System validates plan
   ↓
3. Executive receives notification
   ↓
4. Executive reviews plan
   ↓
5. Executive approves/rejects/requests changes
   ↓
6. System notifies office owner
   ↓
7. If changes requested, office owner updates plan
   ↓
8. Process repeats until approved
```

## Technical Implementation

### New Data Models

#### Business Plan Model
```typescript
interface BusinessPlan {
  id: string;
  name: string;
  office_id: string;
  created_by: string;
  created_at: Date;
  updated_at: Date;
  status: 'draft' | 'submitted' | 'approved' | 'rejected' | 'in_progress' | 'completed';
  
  // Current state (baseline)
  current_state: {
    roles: {
      [role: string]: {
        [level: string]: {
          fte: number;
          monthly_recruitment: number;
          monthly_churn_rate: number;
          progression_rate: number;
          revenue_per_fte: number;
          cost_per_fte: number;
        }
      }
    }
  };
  
  // Target state
  target_state: {
    roles: {
      [role: string]: {
        [level: string]: {
          target_fte: number;
          target_recruitment: number;
          target_churn_rate: number;
          target_progression_rate: number;
        }
      }
    }
  };
  
  // Assumptions and constraints
  assumptions: {
    revenue_per_fte: number;
    cost_per_fte: number;
    utilization_rate: number;
    max_recruitment_capacity: number;
    budget_constraint: number;
  };
  
  // Results (after simulation)
  results?: {
    achieved_fte: number;
    achieved_revenue: number;
    achieved_margin: number;
    monthly_breakdown: Array<{
      month: string;
      fte: number;
      revenue: number;
      margin: number;
    }>;
    kpis: {
      growth_rate: number;
      roi: number;
      risk_level: 'low' | 'medium' | 'high';
    };
  };
  
  // Approval workflow
  approval?: {
    submitted_at: Date;
    reviewed_by: string;
    reviewed_at: Date;
    status: 'pending' | 'approved' | 'rejected';
    comments: string;
    requested_changes?: string[];
  };
}
```

#### Executive Scenario Model
```typescript
interface ExecutiveScenario {
  id: string;
  name: string;
  created_by: string;
  created_at: Date;
  updated_at: Date;
  status: 'draft' | 'active' | 'archived';
  
  // Global adjustments (apply to all offices)
  global_adjustments: {
    recruitment_multiplier: number;
    churn_multiplier: number;
    progression_multiplier: number;
    revenue_multiplier: number;
    cost_multiplier: number;
  };
  
  // Office-specific adjustments (override global)
  office_adjustments: {
    [office_id: string]: {
      recruitment_multiplier?: number;
      churn_multiplier?: number;
      progression_multiplier?: number;
      revenue_multiplier?: number;
      cost_multiplier?: number;
    }
  };
  
  // Role-specific adjustments (override office)
  role_adjustments: {
    [role: string]: {
      recruitment_multiplier?: number;
      churn_multiplier?: number;
      progression_multiplier?: number;
    }
  };
  
  // Results (after simulation)
  results?: {
    total_fte: number;
    total_revenue: number;
    total_margin: number;
    growth_rate: number;
    office_results: {
      [office_id: string]: {
        fte: number;
        revenue: number;
        margin: number;
        growth_rate: number;
      }
    };
    monthly_breakdown: Array<{
      month: string;
      total_fte: number;
      total_revenue: number;
      total_margin: number;
    }>;
  };
}
```

#### User and Permission Model
```typescript
interface User {
  id: string;
  email: string;
  name: string;
  role: 'office_owner' | 'executive' | 'admin';
  office_ids: string[];  // For office owners
  permissions: Permission[];
  created_at: Date;
  updated_at: Date;
}

interface Permission {
  id: string;
  name: string;
  description: string;
  resource: 'business_plan' | 'scenario' | 'office' | 'user';
  action: 'create' | 'read' | 'update' | 'delete' | 'approve';
  scope: 'own' | 'office' | 'all';
}

interface Office {
  id: string;
  name: string;
  region: string;
  status: 'active' | 'inactive';
  office_owner_id: string;
  created_at: Date;
  updated_at: Date;
}
```

### New Service Architecture

#### Business Plan Service
```typescript
class BusinessPlanService {
  // CRUD operations
  createPlan(plan: BusinessPlan): Promise<string>;
  getPlan(planId: string): Promise<BusinessPlan>;
  updatePlan(planId: string, plan: BusinessPlan): Promise<boolean>;
  deletePlan(planId: string): Promise<boolean>;
  listPlans(officeId?: string, status?: string): Promise<BusinessPlan[]>;
  
  // Business logic
  validatePlan(plan: BusinessPlan): Promise<ValidationResult>;
  runPlan(planId: string): Promise<BusinessPlanResults>;
  submitForApproval(planId: string): Promise<boolean>;
  approvePlan(planId: string, approverId: string, comments?: string): Promise<boolean>;
  rejectPlan(planId: string, approverId: string, comments: string): Promise<boolean>;
  
  // Constraints and validation
  checkConstraints(plan: BusinessPlan): Promise<ConstraintResult[]>;
  suggestAdjustments(plan: BusinessPlan, constraints: ConstraintResult[]): Promise<BusinessPlan>;
}
```

#### Scenario Service
```typescript
class ScenarioService {
  // CRUD operations
  createScenario(scenario: ExecutiveScenario): Promise<string>;
  getScenario(scenarioId: string): Promise<ExecutiveScenario>;
  updateScenario(scenarioId: string, scenario: ExecutiveScenario): Promise<boolean>;
  deleteScenario(scenarioId: string): Promise<boolean>;
  listScenarios(): Promise<ExecutiveScenario[]>;
  
  // Business logic
  runScenario(scenarioId: string): Promise<ScenarioResults>;
  compareScenarios(scenarioIds: string[]): Promise<ComparisonResult>;
  applyScenarioToPlans(scenarioId: string, planIds: string[]): Promise<boolean>;
  
  // Aggregation
  aggregateOfficePlans(officeIds: string[]): Promise<AggregatedResults>;
  calculateCompanyKPIs(officeIds: string[]): Promise<CompanyKPIs>;
}
```

#### User and Permission Service
```typescript
class UserService {
  // User management
  createUser(user: User): Promise<string>;
  getUser(userId: string): Promise<User>;
  updateUser(userId: string, user: User): Promise<boolean>;
  deleteUser(userId: string): Promise<boolean>;
  listUsers(): Promise<User[]>;
  
  // Permission management
  checkPermission(userId: string, resource: string, action: string, scope?: string): Promise<boolean>;
  getUserPermissions(userId: string): Promise<Permission[]>;
  assignPermission(userId: string, permissionId: string): Promise<boolean>;
  revokePermission(userId: string, permissionId: string): Promise<boolean>;
  
  // Office management
  getOfficesForUser(userId: string): Promise<Office[]>;
  assignOfficeToUser(userId: string, officeId: string): Promise<boolean>;
  removeOfficeFromUser(userId: string, officeId: string): Promise<boolean>;
}
```

### API Endpoints

#### Business Plan Endpoints
```typescript
// Office Owner endpoints
POST   /api/business-plans                    // Create new plan
GET    /api/business-plans                    // List plans for user
GET    /api/business-plans/{planId}           // Get specific plan
PUT    /api/business-plans/{planId}           // Update plan
DELETE /api/business-plans/{planId}           // Delete plan
POST   /api/business-plans/{planId}/run       // Run plan simulation
POST   /api/business-plans/{planId}/submit    // Submit for approval
POST   /api/business-plans/{planId}/validate  // Validate plan

// Executive endpoints
GET    /api/business-plans/pending            // List pending approvals
POST   /api/business-plans/{planId}/approve   // Approve plan
POST   /api/business-plans/{planId}/reject    // Reject plan
GET    /api/business-plans/aggregated         // Get aggregated view
```

#### Scenario Endpoints
```typescript
// Executive endpoints
POST   /api/scenarios                         // Create new scenario
GET    /api/scenarios                         // List scenarios
GET    /api/scenarios/{scenarioId}            // Get specific scenario
PUT    /api/scenarios/{scenarioId}            // Update scenario
DELETE /api/scenarios/{scenarioId}            // Delete scenario
POST   /api/scenarios/{scenarioId}/run        // Run scenario
POST   /api/scenarios/compare                 // Compare scenarios
GET    /api/scenarios/company-overview        // Get company overview
```

#### User and Permission Endpoints
```typescript
// Admin endpoints
POST   /api/users                             // Create user
GET    /api/users                             // List users
GET    /api/users/{userId}                    // Get user
PUT    /api/users/{userId}                    // Update user
DELETE /api/users/{userId}                    // Delete user
POST   /api/users/{userId}/permissions        // Assign permission
DELETE /api/users/{userId}/permissions/{permId} // Revoke permission
GET    /api/offices                           // List offices
POST   /api/offices                           // Create office
PUT    /api/offices/{officeId}                // Update office
```

## Migration Plan

### Phase 1: Foundation (Week 1-2)
1. **Create new data models** (BusinessPlan, ExecutiveScenario, User, Permission)
2. **Implement new services** (BusinessPlanService, ScenarioService, UserService)
3. **Create new API endpoints** with proper permission checks
4. **Set up database migrations** for new tables

### Phase 2: Office Owner Interface (Week 3-4)
1. **Build Office Owner dashboard** with office selection
2. **Create Business Plan Builder** with current state editor
3. **Implement plan validation** and constraint checking
4. **Add plan simulation** and results display

### Phase 3: Executive Interface (Week 5-6)
1. **Build Executive dashboard** with company overview
2. **Create Scenario Builder** with global and office-specific adjustments
3. **Implement scenario comparison** and recommendation engine
4. **Add approval workflow** for business plans

### Phase 4: Integration & Testing (Week 7-8)
1. **Integrate new system** with existing simulation engine
2. **Add comprehensive testing** for all user flows
3. **Performance optimization** and load testing
4. **User acceptance testing** with real users

### Phase 5: Deployment & Training (Week 9-10)
1. **Deploy new system** alongside existing system
2. **Data migration** from old system to new system
3. **User training** for Office Owners and Executives
4. **Documentation** and support materials

### Phase 6: Cleanup (Week 11-12)
1. **Deprecate old system** and remove legacy code
2. **Performance monitoring** and optimization
3. **User feedback** collection and improvements
4. **Final documentation** and handover

## Success Metrics

### User Experience
- **Reduced confusion**: 90% of users understand the new interface within 1 week
- **Faster plan creation**: 50% reduction in time to create a business plan
- **Better collaboration**: 80% of plans are approved within 3 days

### Technical Performance
- **Response time**: < 2 seconds for all API calls
- **Simulation speed**: < 30 seconds for complex scenarios
- **System uptime**: > 99.9% availability

### Business Impact
- **Plan accuracy**: 95% of plans are within 10% of actual results
- **Decision speed**: 40% faster strategic decision making
- **User adoption**: 90% of target users actively using the system

## Conclusion

This redesign addresses the core issues with the current system:

1. **Clear user mental model**: Separates current state from adjustments
2. **User persona support**: Different interfaces for different user types
3. **Simplified data flow**: Clear separation of concerns
4. **Better collaboration**: Approval workflows and sharing
5. **Improved UX**: Intuitive interfaces with immediate feedback

The new system will be more maintainable, scalable, and user-friendly while providing the same powerful simulation capabilities. 