# Task List: Scenario Runner Implementation

## Relevant Files

- `frontend/src/pages/ScenarioRunner.tsx` - Main scenario runner page component
- `frontend/src/components/scenarios/ScenarioEditor.tsx` - Scenario creation and editing interface
- `frontend/src/components/scenarios/ScenarioList.tsx` - List view of saved scenarios
- `frontend/src/components/scenarios/ScenarioResults.tsx` - Results display and comparison component
- `frontend/src/services/scenarioApi.ts` - API service for scenario management
- `frontend/src/types/scenarios.ts` - TypeScript types for scenario data structures
- `backend/routers/scenarios.py` - Backend API endpoints for scenario management
- `backend/src/services/scenario_service.py` - Backend service for scenario operations
- `backend/config/scenarios/` - Directory for storing scenario data files
- `frontend/src/pages/ScenarioRunner.test.tsx` - Unit tests for main component
- `backend/tests/unit/test_scenario_service.py` - Unit tests for scenario service
- `backend/tests/integration/test_scenario_endpoints.py` - Integration tests for API endpoints

### Notes

- Unit tests should typically be placed alongside the code files they are testing (e.g., `ScenarioRunner.tsx` and `ScenarioRunner.test.tsx` in the same directory).
- Use `npx jest [optional/path/to/test/file]` to run tests. Running without a path executes all tests found by the Jest configuration.

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