## Relevant Files

- `backend/src/services/kpi/kpi_models.py` - Contains EconomicParameters model that needs to be updated.
- `backend/src/services/simulation_engine.py` - Main simulation engine that needs to be refactored to pure function.
- `backend/src/services/scenario_service.py` - Adapter layer that needs to assemble complete data objects.
- `backend/src/services/scenario_resolver.py` - Resolves scenario data and may need updates for object assembly.
- `backend/src/services/office_builder.py` - Builds office objects and may need updates.
- `backend/src/services/simulation/models.py` - Contains Office, Level, RoleData models used by the engine.
- `backend/src/services/simulation/progression_models.py` - NEW: Will contain ProgressionConfig and CATCurves models.
- `backend/tests/unit/test_simulation_engine.py` - Unit tests for simulation engine that need updating.
- `backend/tests/unit/test_scenario_service.py` - Unit tests for scenario service that need updating.
- `tests/archive/test_engine_validation.py` - Validation tests that need updating for pure function approach.

### Notes

- Unit tests should typically be placed alongside the code files they are testing (e.g., `simulation_engine.py` and `test_simulation_engine.py` in the same directory).
- Use `python -m pytest backend/tests/unit/test_simulation_engine.py` to run tests. Running without a path executes all tests found by the pytest configuration.
- The engine correctly uses `Dict[str, Office]` as a container for Office objects - this is the intended design.
- We need to create proper models for progression_config and cat_curves to complete the object-based approach.

## Tasks

- [x] 1.0 Update EconomicParameters Model
  - [x] 1.1 Add price_increase and salary_increase fields to EconomicParameters
  - [x] 1.2 Update EconomicParameters default values and validation
  - [x] 1.3 Update _create_economic_params method in scenario service

- [x] 2.0 Refactor Simulation Engine to Pure Function
  - [x] 2.1 Update run_simulation() function signature to accept complete office objects
  - [x] 2.2 Remove all config loading and external dependencies from engine
  - [x] 2.3 Update engine to use EconomicParameters for price/salary increases
  - [x] 2.4 Ensure engine accepts Dict[str, Office] for offices parameter

- [x] 3.0 Create Data Assembly Utilities
  - [x] 3.1 Create utilities to build complete Office objects from config data
  - [x] 3.2 Create utilities to build complete Level and RoleData objects
  - [x] 3.3 Create utilities to assemble EconomicParameters objects
  - [x] 3.4 Add validation for all assembled objects

- [x] 4.0 Update Scenario Service Adapter Layer
  - [x] 4.1 Update scenario service to assemble complete data before calling engine
  - [x] 4.2 Ensure scenario service handles all data transformation
  - [x] 4.3 Update scenario service to use new engine function signature
  - [x] 4.4 Maintain backward compatibility with existing API endpoints

- [x] 5.0 Create Progression and CAT Models
  - [x] 5.1 Create ProgressionConfig dataclass for progression rules
  - [x] 5.2 Create CATCurves dataclass for progression probabilities
  - [x] 5.3 Update engine function signature to use new models instead of Dict[str, Any]
  - [x] 5.4 Update scenario service to assemble new model objects

- [x] 6.0 Update Tests and Validation
  - [x] 6.1 Update simulation engine unit tests to use pure function approach
  - [x] 6.2 Update scenario service tests to verify data assembly
  - [x] 6.3 Update validation tests to use new object-based approach
  - [x] 6.4 Add integration tests to verify end-to-end functionality 