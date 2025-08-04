# Office-Specific Business Planning & Scenario Integration

## Overview

This document outlines tasks for implementing comprehensive office-specific business planning and configuration system that integrates with the existing scenario system. Based on the comprehensive design documents:
- `docs/PRD_Office_Business_Planning.md` (Product Requirements)
- `docs/IMPLEMENTATION_TASKS.md` (Detailed implementation breakdown)
- `docs/UI_DESIGN_SPECIFICATIONS.md` (UI/UX design specifications)
- `docs/OFFICE_SCENARIO_INTEGRATION.md` (Scenario system integration design)

## Relevant Files

- `backend/src/services/scenario_resolver.py` - **FIXED: Integer truncation bug on line 272**
- `backend/src/models/office.py` - Office configuration models (to be created)
- `backend/src/models/office_business_plan.py` - Business plan models (to be created)
- `backend/src/routes/offices.py` - Office management APIs (to be created)
- `backend/src/routes/business_plans.py` - Business plan APIs (to be created)
- `backend/src/services/office_service.py` - Office management service (to be created)
- `backend/src/services/business_plan_service.py` - Business plan service (to be created)
- `frontend/src/pages/OfficeManagement.tsx` - Main office management interface (to be created)
- `frontend/src/components/offices/OfficeSidebar.tsx` - Office navigation (to be created)
- `frontend/src/components/business-plan/BusinessPlanTable.tsx` - Editable planning table (to be created)
- `frontend/src/stores/officeStore.ts` - Office state management (to be created)
- `frontend/src/stores/businessPlanStore.ts` - Business plan state (to be created)

### Architecture References
- `docs/PRD_Office_Business_Planning.md` - Complete product requirements
- `docs/IMPLEMENTATION_TASKS.md` - Detailed implementation breakdown  
- `docs/UI_DESIGN_SPECIFICATIONS.md` - UI/UX design specifications
- `docs/OFFICE_SCENARIO_INTEGRATION.md` - Scenario system integration design

### Notes
- **CRITICAL BUG FIXED**: Integer truncation in scenario_resolver.py that caused 8/12 offices to receive 0 churn
- Office system focuses on absolute values rather than proportional distribution
- Business plans become baseline input for scenarios (individual or aggregated)
- Journey-based organization: Emerging, Established, Mature offices
- Monthly business planning with 5 parameters per role/level combination

## Critical Bug Fix (Immediate Priority)

- [x] **URGENT: Fix integer truncation bug in scenario_resolver.py line 272**
  - **Issue**: `int(proportional_value)` causes systematic distribution failure
  - **Impact**: 8 out of 12 offices receive 0 churn despite having workforce
  - **Fix**: Replace `int()` with `round()` for more accurate distribution
  - **Status**: COMPLETED - Fix applied to scenario_resolver.py

## Phase 1: Backend Foundation (Weeks 1-3)

### 1.0 Database Schema & Models
- [ ] 1.1 Create comprehensive database schema for office management
  - [ ] Create `offices` table with journey enum (emerging, established, mature)
  - [ ] Create `office_workforce` table for initial population distribution
  - [ ] Create `office_business_plans` table for monthly planning data
  - [ ] Create `office_progressions` table for CAT progression configuration
  - [ ] Add proper indexes and foreign key constraints
  - [ ] Create migration scripts with rollback capability

- [ ] 1.2 Implement Pydantic models for office configuration
  - [ ] Create `OfficeConfig` model with comprehensive validation
  - [ ] Create `WorkforceDistribution` model for initial population
  - [ ] Create `MonthlyBusinessPlan` model for 12-month planning
  - [ ] Create `ProgressionConfig` model for CAT progression
  - [ ] Add cross-model validation rules for data consistency

### 2.0 Core Office Management APIs
- [ ] 2.1 Implement office CRUD endpoints
  - [ ] `GET /api/offices` (list with journey grouping)
  - [ ] `GET /api/offices/{id}` (office details with full configuration)
  - [ ] `POST /api/offices` (create office with validation)
  - [ ] `PUT /api/offices/{id}` (update office configuration)
  - [ ] `DELETE /api/offices/{id}` (delete with dependency checks)

- [ ] 2.2 Implement business plan management APIs
  - [ ] `GET /api/offices/{id}/business-plan` (monthly planning data)
  - [ ] `PUT /api/offices/{id}/business-plan` (bulk update with validation)
  - [ ] `POST /api/offices/{id}/business-plan/copy` (copy from template/office)
  - [ ] `POST /api/offices/{id}/business-plan/validate` (comprehensive validation)
  - [ ] Add batch update capabilities for efficient table operations

- [ ] 2.3 Implement workforce and progression APIs
  - [ ] `GET/PUT /api/offices/{id}/population` (initial workforce setup)
  - [ ] `GET/PUT /api/offices/{id}/progression` (CAT progression config)
  - [ ] Add workforce consistency validation across plans
  - [ ] Create progression calculation utilities

### 3.0 Simulation Engine Integration
- [ ] 3.1 Modify simulation engine for office-specific inputs
  - [ ] Update `SimulationEngine` to accept office configurations
  - [ ] Modify scenario resolver to handle office-specific absolute values
  - [ ] Ensure backward compatibility with global baseline scenarios
  - [ ] Add office-specific economic parameter support

- [ ] 3.2 Create office-specific simulation endpoints
  - [ ] `POST /api/simulation/office/{id}` (single office simulation)
  - [ ] `POST /api/simulation/aggregated` (multi-office simulation)
  - [ ] `GET /api/simulation/results/{id}` (enhanced results with office breakdown)
  - [ ] Add comparison and analysis endpoints for office performance

## Phase 2: Frontend Foundation (Weeks 4-6)

### 4.0 Component Architecture & Navigation
- [ ] 4.1 Create office management layout and navigation
  - [ ] Create `OfficeManagement` main layout component
  - [ ] Build `OfficeSidebar` with journey-based grouping
  - [ ] Implement `JourneyGroup` and `OfficeNavItem` components
  - [ ] Add responsive design for tablet/desktop/mobile
  - [ ] Create office routing structure with deep linking

- [ ] 4.2 Implement state management with Zustand
  - [ ] Create `useOfficeStore` with office CRUD operations
  - [ ] Create `useBusinessPlanStore` for plan editing and validation
  - [ ] Add optimistic updates and error handling
  - [ ] Implement validation state management with real-time feedback

### 5.0 Business Plan Interface
- [ ] 5.1 Build comprehensive business plan table
  - [ ] Create `BusinessPlanTable` with 12 months × 24 roles/levels matrix
  - [ ] Implement `EditableCell` with 5-field editing (recruitment, churn, price, UTR, salary)
  - [ ] Add keyboard navigation and bulk editing capabilities
  - [ ] Create table virtualization for performance with large datasets
  - [ ] Add copy/paste functionality for efficient data entry

- [ ] 5.2 Implement advanced editing features
  - [ ] Create multi-field cell editor with validation
  - [ ] Add real-time validation with contextual error display
  - [ ] Implement undo/redo capabilities for editing operations
  - [ ] Add formula support for calculated fields
  - [ ] Create range selection and bulk operations

### 6.0 Office Configuration Pages
- [ ] 6.1 Create comprehensive office configuration interface
  - [ ] Build `OfficeConfigPage` main container with section navigation
  - [ ] Create `OfficeInfoSection` for basic settings and economic parameters
  - [ ] Build `InitialPopulationTable` for workforce distribution setup
  - [ ] Create `CATProgressionConfig` for progression curve configuration
  - [ ] Add `SimulationControls` for running and comparing simulations

- [ ] 6.2 Implement templates and utilities
  - [ ] Build template selection interface for journey-based plans
  - [ ] Create plan copying functionality between offices
  - [ ] Add export/import capabilities for business plans
  - [ ] Implement comprehensive plan validation dashboard
  - [ ] Create plan comparison tools and variance analysis

## Phase 3: Scenario System Integration (Week 7)

### 7.0 Enhanced Scenario Creation
- [ ] 7.1 Extend scenario builder for office business plans
  - [ ] Add business plan source selection (global baseline vs office plans)
  - [ ] Create office scope configuration (single, multiple, journey-based, all)
  - [ ] Implement business plan selection interface with preview
  - [ ] Add aggregation method selection (sum, proportional, custom)
  - [ ] Create baseline preview component showing generated values

- [ ] 7.2 Implement business plan to baseline transformation
  - [ ] Create transformation service for single office plans
  - [ ] Implement multi-office aggregation with different methods
  - [ ] Add mixed baseline resolution (office plans + global fallback)
  - [ ] Create validation for transformed baseline input
  - [ ] Add lineage tracking from business plans to scenarios

### 8.0 Enhanced Scenario Execution
- [ ] 8.1 Implement office-based scenario execution pipeline
  - [ ] Create business plan resolution logic for scenarios
  - [ ] Implement office configuration assembly from business plans
  - [ ] Add simulation engine execution with office-specific absolute values
  - [ ] Create results aggregation for individual and combined office results
  - [ ] Add comparison metrics between offices and aggregated results

## Phase 4: Advanced Features & Polish (Week 8)

### 9.0 Enhanced User Experience
- [ ] 9.1 Implement advanced UX features
  - [ ] Add bulk editing with intelligent range selection
  - [ ] Create what-if scenario analysis tools
  - [ ] Build comprehensive plan comparison visualization
  - [ ] Add keyboard shortcuts and hotkeys for power users
  - [ ] Implement auto-save functionality with conflict resolution

- [ ] 9.2 Create enhanced results and analytics
  - [ ] Build office-specific results dashboard with KPIs
  - [ ] Create comparison views for multiple offices
  - [ ] Add interactive charts and visualizations
  - [ ] Implement results export functionality
  - [ ] Create executive summary views with key insights

### 10.0 Testing & Quality Assurance
- [ ] 10.1 Comprehensive backend testing
  - [ ] Unit tests for all office models and validators
  - [ ] Integration tests for API endpoints with edge cases
  - [ ] Performance tests for simulation engine with office data
  - [ ] Database migration testing with rollback scenarios
  - [ ] API documentation with comprehensive examples

- [ ] 10.2 Frontend testing and quality
  - [ ] Unit tests for all office management components
  - [ ] Integration tests for complete office workflows
  - [ ] E2E tests for business plan editing and simulation
  - [ ] Performance testing for large business plan tables
  - [ ] Accessibility testing and compliance improvements

### 11.0 Documentation & Deployment
- [ ] 11.1 Technical documentation
  - [ ] API documentation with interactive examples
  - [ ] Database schema documentation with relationships
  - [ ] Component architecture documentation
  - [ ] Deployment and configuration guides

- [ ] 11.2 User documentation
  - [ ] Office manager user guide with workflows
  - [ ] Business plan creation tutorial with best practices
  - [ ] Simulation configuration guide
  - [ ] Troubleshooting guide and FAQ

## Success Criteria

### Functional Requirements
- [ ] Users can create and edit monthly business plans for each office (12 months × 24 role/level combinations)
- [ ] Office navigation works efficiently with journey-based grouping
- [ ] Simulations execute correctly using office-specific absolute values
- [ ] CAT progression is configurable per office with custom curves
- [ ] Business plans can be transformed into scenario baseline input
- [ ] Mixed baseline resolution works (office plans + global fallback)

### Technical Requirements  
- [ ] API response times < 200ms for office operations
- [ ] Business plan tables handle large datasets efficiently with virtualization
- [ ] Real-time validation provides feedback within 100ms
- [ ] Data consistency maintained across all office configurations
- [ ] Responsive design works seamlessly on tablets and desktops
- [ ] System maintains backward compatibility with existing scenarios

### User Experience
- [ ] Intuitive navigation between offices with smooth transitions
- [ ] Efficient bulk editing capabilities for large data entry
- [ ] Clear, contextual validation feedback for all inputs
- [ ] Fast simulation execution with progress indicators
- [ ] Reliable data persistence with conflict resolution
- [ ] Comprehensive error handling with helpful messages

## Risk Mitigation

### Technical Risks
- **Complex Table Performance**: Implement table virtualization and efficient rendering
- **Data Consistency**: Use database transactions and comprehensive validation
- **Simulation Complexity**: Gradual migration from global to office-specific inputs
- **State Management**: Use immutable updates and optimistic UI patterns

### UX Risks
- **Overwhelming Interface**: Implement progressive disclosure and smart defaults
- **Data Entry Fatigue**: Provide templates, bulk operations, and intelligent copying
- **Validation Complexity**: Create clear, contextual error messages with suggestions
- **Learning Curve**: Add guided onboarding and contextual help

## Future Enhancements (Post-V1)
- Multi-year business planning with trend analysis
- Advanced analytics and forecasting capabilities
- Office performance benchmarking and best practice sharing
- Automated plan optimization using simulation results
- Integration with external business systems and data sources
- Mobile application for office managers and executives
- Advanced collaboration features for multi-office planning
- Machine learning-powered planning assistance and recommendations

---

This comprehensive task list provides a structured approach to implementing the complete office business planning and scenario integration system, addressing the current simulation accuracy issues while building a foundation for advanced business planning capabilities.