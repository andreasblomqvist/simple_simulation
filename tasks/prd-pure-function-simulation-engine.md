# PRD: Pure Function Simulation Engine with Object-Based Input/Output

## Introduction/Overview

The simulation engine currently has dependencies on configuration services and file loading, which violates the architectural principle of keeping it as a pure function. This feature will refactor the engine to accept all data as input parameters (as objects, not JSON/dicts) and return results without any side effects or external dependencies.

## Goals

1. **Eliminate all external dependencies** from the simulation engine
2. **Make the engine a pure function** that receives complete data structures as input
3. **Use proper Python objects** instead of JSON/dicts for type safety and validation
4. **Centralize data assembly** in the adapter/service layer
5. **Maintain backward compatibility** with existing API endpoints

## User Stories

- As a **developer**, I want the simulation engine to be a pure function so that I can test it reliably without external dependencies
- As a **developer**, I want to pass complete office/role/level data as objects so that I have type safety and validation
- As a **developer**, I want all economic parameters (including price/salary increases) in one place so that the API is cleaner
- As a **developer**, I want the adapter layer to assemble all data so that the engine remains focused on calculations

## Functional Requirements

1. **Update EconomicParameters model** to include price_increase and salary_increase fields
2. **Refactor engine.run_simulation()** to accept complete office objects with all FTE and configuration data
3. **Remove all config loading** from the simulation engine
4. **Update engine function signature** to use EconomicParameters instead of separate price/salary parameters
5. **Create data assembly utilities** in the adapter/service layer to build complete input objects
6. **Update scenario service** to assemble complete data before calling the engine
7. **Add validation** for all input objects using Pydantic models
8. **Update tests** to use the new pure function approach

## Non-Goals (Out of Scope)

- Changing the frontend API contract
- Modifying the existing scenario storage format
- Adding new simulation features
- Changing the results format

## Design Considerations

- Use existing Pydantic models (Office, Level, RoleData, EconomicParameters)
- Maintain the same simulation logic and calculations
- Keep the adapter layer thin as per architecture guidelines
- Ensure all data validation happens at the object level

## Technical Considerations

- The engine should accept Dict[str, Office] for offices parameter
- EconomicParameters should include price_increase and salary_increase as global values
- All FTE values should be included in the Office/Level objects passed to the engine
- The adapter layer should handle all data assembly from config files, scenario definitions, etc.

## Success Metrics

- All simulation engine tests pass with the new pure function approach
- No external dependencies in the simulation engine
- Type safety and validation for all input parameters
- Backward compatibility maintained for existing API endpoints
- Performance remains the same or better

## Open Questions

- Should we add per-office price/salary increase support in the future?
- Do we need to support partial office data updates or always require complete office objects? 