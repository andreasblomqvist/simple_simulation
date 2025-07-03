# Refactor Simulation Engine Architecture

## Overview

Refactor the simulation engine to be a pure function that receives all data as input, eliminating config service dependencies and making the system more testable, predictable, and maintainable.

## Goals

1. **Decouple engine from config service** - Engine should receive all data as input
2. **Make engine pure and testable** - No side effects or external dependencies
3. **Improve data flow control** - Mid-layer resolves config + scenario before passing to engine
4. **Maintain existing good architecture** - Leverage existing workforce, event_logger, and models
5. **Enable scenario flexibility** - Support different progression models per scenario

## Current Architecture Issues

- Engine loads config internally via config service
- Models import progression config directly
- OfficeManager depends on config service
- Hard to test with different configurations
- Risk of stale config data
- Tight coupling between engine and data sources

## Proposed Architecture

```
API → ScenarioService (resolves config + scenario) → SimulationEngine (pure function) → Results
```

### Key Changes

1. **ScenarioService** (new mid-layer)
   - Loads base config from config service
   - Loads progression rules from config service
   - Applies scenario baseline input and levers
   - Creates Office objects with complete state
   - Returns everything needed by engine

2. **SimulationEngine** (refactored)
   - Receives offices, progression rules, and all data as input
   - No config service dependencies
   - Pure function with no side effects
   - Maintains existing workforce and event_logger integration

3. **Models** (refactored)
   - Remove direct progression config imports
   - Accept progression rules as method parameters
   - Maintain existing data structures

## Relevant Files

- `backend/src/services/simulation_engine.py` - Main engine class to refactor
- `backend/src/services/simulation/models.py` - Remove config imports, add parameter-based methods
- `backend/src/services/simulation/office_manager.py` - Remove config service dependency
- `backend/src/services/simulation/workforce.py` - Already good, minimal changes needed
- `backend/src/services/simulation/event_logger.py` - Already good, no changes needed
- `backend/src/services/simulation/utils.py` - Already good, no changes needed
- `backend/src/services/scenario_service.py` - New service to create (mid-layer)
- `backend/routers/simulation.py` - Update to use new architecture
- `backend/src/services/simulation/__init__.py` - Update exports
- `tests/unit/test_simulation_engine.py` - Update tests for pure engine
- `tests/unit/test_scenario_service.py` - New tests for scenario service
- `tests/unit/test_models.py` - Update tests for parameter-based methods

### Notes

- Unit tests should be placed alongside the code files they are testing
- Use `pytest` to run tests: `pytest tests/unit/test_simulation_engine.py`
- Integration tests should verify the complete data flow from API to results
- Maintain backward compatibility during transition period

## Tasks

- [ ] 1.0 Create ScenarioService (Mid-Layer)
  - [ ] 1.1 Create ScenarioService class with config service dependency
  - [ ] 1.2 Implement resolve_scenario method to load base config and progression rules
  - [ ] 1.3 Implement apply_scenario_baseline method for recruitment/churn overrides
  - [ ] 1.4 Implement apply_scenario_levers method for additional overrides
  - [ ] 1.5 Implement create_offices_from_config method to build Office objects
  - [ ] 1.6 Add helper methods for loading progression config and CAT curves
  - [ ] 1.7 Add validation for scenario data structure and completeness
- [ ] 2.0 Refactor Models to Remove Config Dependencies
  - [ ] 2.1 Remove direct imports of PROGRESSION_CONFIG and CAT_CURVES from models.py
  - [ ] 2.2 Update Level.apply_cat_based_progression to accept progression_config and cat_curves parameters
  - [ ] 2.3 Update Level.get_eligible_for_progression to accept progression_config parameter
  - [ ] 2.4 Update Level.is_progression_month to accept progression_config parameter
  - [ ] 2.5 Update Person.get_progression_probability to accept cat_curves parameter
  - [ ] 2.6 Add fallback logic for when progression rules are not provided
  - [ ] 2.7 Update method signatures to maintain backward compatibility during transition
- [ ] 3.0 Refactor OfficeManager to Remove Config Service Dependency
  - [ ] 3.1 Remove config_service parameter from OfficeManager constructor
  - [ ] 3.2 Rename initialize_offices_from_config to create_offices_from_data
  - [ ] 3.3 Update create_offices_from_data to accept office_data list instead of loading from config
  - [ ] 3.4 Update _create_office_from_config to accept progression_config parameter
  - [ ] 3.5 Remove config service calls and replace with passed data
  - [ ] 3.6 Update _initialize_realistic_people to work with new structure
  - [ ] 3.7 Add validation for office data completeness
- [ ] 4.0 Refactor SimulationEngine to be Pure Function
  - [ ] 4.1 Create new run_simulation_with_offices method that accepts all data as input
  - [ ] 4.2 Update constructor to remove config_service dependency
  - [ ] 4.3 Move config loading logic from engine to ScenarioService
  - [ ] 4.4 Update run_simulation_with_offices to use passed progression rules
  - [ ] 4.5 Maintain existing run_simulation method for backward compatibility
  - [ ] 4.6 Update _initialize_offices_from_config_service to use passed office data
  - [ ] 4.7 Ensure WorkforceManager integration remains unchanged
  - [ ] 4.8 Add validation for input data completeness
- [ ] 5.0 Update API Layer to Use New Architecture
  - [ ] 5.1 Update simulation router to use ScenarioService
  - [ ] 5.2 Modify run_simulation endpoint to resolve scenario before calling engine
  - [ ] 5.3 Update SimulationRequest model to include scenario data structure
  - [ ] 5.4 Add scenario validation in API layer
  - [ ] 5.5 Update error handling for new data flow
  - [ ] 5.6 Maintain backward compatibility for existing API calls
  - [ ] 5.7 Update API documentation to reflect new architecture
- [ ] 6.0 Update Tests and Documentation
  - [ ] 6.1 Create comprehensive tests for ScenarioService
  - [ ] 6.2 Update SimulationEngine tests to use pure function approach
  - [ ] 6.3 Update Models tests to use parameter-based methods
  - [ ] 6.4 Update OfficeManager tests to remove config service dependency
  - [ ] 6.5 Create integration tests for complete data flow
  - [ ] 6.6 Update API endpoint tests for new scenario structure
  - [ ] 6.7 Update simulation module __init__.py exports
  - [ ] 6.8 Update architecture documentation
  - [ ] 6.9 Add migration guide for existing code 