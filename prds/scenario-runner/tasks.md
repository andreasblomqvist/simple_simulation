# Task List: Scenario Runner Implementation

## Absolute Input Data UI (Baseline)

- [x] 0.0 Absolute Input Data UI
  - [x] 0.1 Design spreadsheet-like grid component for absolute starters/leavers input
  - [x] 0.2 Implement tabs for 'Recruitment (Starters)' and 'Leavers (Churn)'
  - [ ] 0.3 Add import (Excel/CSV), paste, and clear functionality
  - [x] 0.4 Add validation for numeric input, no negatives, highlight errors
  - [x] 0.5 Add summary row (totals per role, optional)
  - [ ] 0.6 Implement 'Load from Service' button to fetch baseline data from backend
  - [ ] 0.7 Implement 'Save Baseline' to persist input data to backend
  - [x] 0.8 Integrate baseline input step into Scenario Runner flow (step 1)
  - [ ] 0.9 Ensure baseline is referenced by all scenarios and warn if changed
  - [ ] 0.10 Add unit tests for grid component and data service

## Results Table (All Years, All KPIs, Per Office)

- [ ] 1.0 Results Table Implementation
  - [ ] 1.1 Update backend to return all KPIs (financial and journey) for each office and for 'Group' (company-wide) for all years
  - [ ] 1.2 Update frontend to render a spreadsheet-style table:
    - [ ] 1.2.1 Rows: Each KPI (FTE, Growth%, Sales, EBITDA, EBITDA%, J-1, J-2, J-3, etc.) for each office and for 'Group'
    - [ ] 1.2.2 Columns: Each year in the scenario
    - [ ] 1.2.3 Office column: 'Group' for company-wide, then each office
    - [ ] 1.2.4 KPI column: All relevant KPIs
  - [ ] 1.3 Ensure table is easy to scan, copy, and compare
  - [ ] 1.4 (Optional) Add expand/collapse for offices if many exist
  - [ ] 1.5 Add unit/integration tests for results table rendering

## Relevant Files

- `frontend/src/pages/ScenarioRunner.tsx` - Main scenario runner page component
- `frontend/src/components/scenario-runner/BaselineInputGrid.tsx` - Baseline input table for recruitment/leavers
- `frontend/src/components/scenario-runner/ResultsTable.tsx` - (To be created) Results table for all years, all KPIs, per office
- `frontend/src/services/scenarioApi.ts` - API service for scenario management
- `frontend/src/types/scenarios.ts` - TypeScript types for scenario data structures
- `backend/routers/scenarios.py` - Backend API endpoints for scenario management/results
- `backend/src/services/scenario_service.py` - Backend service for scenario operations/results
- `backend/tests/unit/test_scenario_service.py` - Unit tests for scenario service
- `backend/tests/integration/test_scenario_endpoints.py` - Integration tests for API endpoints

### Notes
- 'Group' is used for company-wide summary rows in the results table.
- All years in the scenario time range are shown as columns.
- All KPIs (financial and journey) are included as rows for each office and for 'Group'.
- Table should be simple, spreadsheet-like, and easy to copy/export.
- Add new tasks as needed for additional features or improvements.

## Tasks

- [ ] 1.0 Backend Infrastructure Setup
  - [ ] 1.1 Create scenario data models and types in Python
  - [ ] 1.2 Create scenario service with CRUD operations
  - [ ] 1.3 Create scenario router with API endpoints
  - [ ] 1.4 Set up scenario data storage directory structure
  - [ ] 1.5 Add scenario endpoints to main FastAPI app
  - [ ] 1.6 Create scenario validation logic for lever inputs
- [ ] 2.0 Frontend Core Components
  - [ ] 2.1 Create TypeScript types for scenario data structures
  - [ ] 2.2 Create main ScenarioRunner page component
  - [ ] 2.3 Create ScenarioEditor component with form controls
  - [ ] 2.4 Create ScenarioList component for saved scenarios
  - [ ] 2.5 Create ScenarioResults component for displaying outcomes
  - [ ] 2.6 Create scenario API service for backend communication
- [ ] 3.0 Scenario Management System
  - [ ] 3.1 Implement scenario creation with name, description, and settings
  - [ ] 3.2 Implement level-specific lever controls (recruitment, churn, progression)
  - [ ] 3.3 Implement bulk edit functionality for quick adjustments
  - [ ] 3.4 Implement scenario saving with JSON persistence
  - [ ] 3.5 Implement scenario loading and editing capabilities
  - [ ] 3.6 Implement scenario deletion and history management
- [ ] 4.0 Results Display and Comparison
  - [ ] 4.1 Integrate with existing simulation engine for scenario execution
  - [ ] 4.2 Display journey distribution results prominently
  - [ ] 4.3 Display growth metrics with clear visualizations
  - [ ] 4.4 Display EBITDA as primary financial metric
  - [ ] 4.5 Implement side-by-side scenario comparison
  - [ ] 4.6 Add export functionality for scenario results
- [ ] 5.0 Integration and Testing
  - [ ] 5.1 Add navigation to ScenarioRunner from main app
  - [ ] 5.2 Implement error handling and user feedback
  - [ ] 5.3 Add loading states and progress indicators
  - [ ] 5.4 Write unit tests for all components and services
  - [ ] 5.5 Write integration tests for API endpoints
  - [ ] 5.6 Perform end-to-end testing of complete scenario workflow 