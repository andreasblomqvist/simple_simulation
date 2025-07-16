# PRD: Unified Data Structures for SimpleSim

## Introduction/Overview

The SimpleSim system currently suffers from inconsistent data structures across different components, causing confusion, bugs, and maintenance issues. This feature will establish a single, consistent data structure that flows through the entire system from frontend to backend to simulation engine.

**Problem**: The system has a well-documented data structure in `docs/SIMULATION_DATA_STRUCTURES.md`, but implementation inconsistencies exist:
- Scenario files vs API input vs simulation engine input don't all follow the documented structure
- Different field names (`fte` vs `total`, `price_1` vs `Price_1`) despite documented standards
- Mixed data types (dicts vs objects vs lists) that don't match the documented patterns
- Inconsistent handling of roles with levels vs flat roles despite clear documentation

**Goal**: Ensure all system components consistently implement the well-documented data structure from `docs/SIMULATION_DATA_STRUCTURES.md`.

## Goals

1. **Implement Documented Structure**: Ensure all components follow the structure defined in `docs/SIMULATION_DATA_STRUCTURES.md`
2. **Reduce Bugs**: Consistent field names and types throughout (as documented)
3. **Improve Maintainability**: Clear data contracts between components
4. **Enhance Developer Experience**: Predictable data flow and debugging
5. **Support Future Features**: Extensible structure for new requirements
6. **Eliminate Implementation Gaps**: Bridge the gap between documented structure and actual implementation

## User Stories

- **As a developer**, I want consistent data structures so I can understand how data flows through the system without confusion
- **As a developer**, I want predictable field names so I don't have to remember different naming conventions
- **As a developer**, I want type-safe data structures so I can catch errors at compile time
- **As a user**, I want reliable data handling so my scenarios work consistently
- **As a maintainer**, I want clear data contracts so I can modify components without breaking others

## Functional Requirements

1. **Consistent Implementation**: All components implement the documented structure from `docs/SIMULATION_DATA_STRUCTURES.md`
2. **Unified Field Naming**: Consistent naming convention across all components (as documented)
3. **Type Safety**: Strong typing with validation at all layers
4. **Backward Compatibility**: Existing scenarios continue to work
5. **Clear Data Flow**: Documented transformation between layers (as specified in existing docs)
6. **Validation**: Comprehensive validation at API boundaries
7. **Error Handling**: Clear error messages for data structure issues
8. **List vs Dict Consistency**: Proper handling of leveled vs flat roles as documented
9. **Remove Progression Rate**: Eliminate `progression_rate` field from all progression configurations

## Non-Goals (Out of Scope)

- Changing the simulation engine's internal calculation logic
- Modifying the core business rules or formulas
- Adding new features beyond data structure standardization
- Changing the user interface (this is a backend/data structure change)

## Design Considerations

### Aligning with Existing Documentation

This PRD builds upon the existing `docs/SIMULATION_DATA_STRUCTURES.md` specification, which already defines a comprehensive and well-structured data format. The goal is to ensure **consistent implementation** of this documented structure across all system components.

### Current Documented Structure (from docs/SIMULATION_DATA_STRUCTURES.md)

The existing documentation defines this structure for scenario definitions:

```python
scenario_definition = {
    "id": "uuid-string",
    "name": "Scenario Name", 
    "description": "Scenario description",
    "time_range": {
        "start_year": 2025,
        "start_month": 1,
        "end_year": 2030,
        "end_month": 12
    },
    "office_scope": ["Group"],  # or specific office names
    "levers": {
        "recruitment": {"A": 1, "AC": 1, "C": 1, ...},
        "churn": {"A": 1, "AC": 1, "C": 1, ...},
        "progression": {"A": 1, "AC": 1, "C": 1, ...}
    },
    "economic_params": {
        "working_hours_per_month": 160.0,
        "employment_cost_rate": 0.3,
        "unplanned_absence": 0.05,
        "other_expense": 1000000.0
    },
    "progression_config": {
        "A": {
            "progression_months": [1],
            "start_tenure": 1,
            "time_on_level": 6,
            "next_level": "AC",
            "journey": "J-1"
        },
        "AC": {
            "progression_months": [1],
            "start_tenure": 7,
            "time_on_level": 12,
            "next_level": "C",
            "journey": "J-1"
        }
        // ... other levels
    },
    "cat_curves": {
        "A": {"CAT0": 0.0, "CAT6": 0.919, "CAT12": 0.85, "CAT18": 0.0, "CAT24": 0.0, "CAT30": 0.0},
        "AC": {"CAT0": 0.0, "CAT6": 0.054, "CAT12": 0.759, "CAT18": 0.400, "CAT24": 0.0, "CAT30": 0.0},
        "C": {"CAT0": 0.0, "CAT6": 0.050, "CAT12": 0.442, "CAT18": 0.597, "CAT24": 0.278, "CAT30": 0.643, "CAT36": 0.200, "CAT42": 0.0},
        "SrC": {"CAT0": 0.0, "CAT6": 0.206, "CAT12": 0.438, "CAT18": 0.317, "CAT24": 0.211, "CAT30": 0.206, "CAT36": 0.167, "CAT42": 0.0, "CAT48": 0.0, "CAT54": 0.0, "CAT60": 0.0},
        "AM": {"CAT0": 0.0, "CAT6": 0.0, "CAT12": 0.0, "CAT18": 0.189, "CAT24": 0.197, "CAT30": 0.234, "CAT36": 0.048, "CAT42": 0.0, "CAT48": 0.0, "CAT54": 0.0, "CAT60": 0.0},
        "M": {"CAT0": 0.0, "CAT6": 0.00, "CAT12": 0.01, "CAT18": 0.02, "CAT24": 0.03, "CAT30": 0.04, "CAT36": 0.05, "CAT42": 0.06, "CAT48": 0.07, "CAT54": 0.08, "CAT60": 0.10},
        "SrM": {"CAT0": 0.0, "CAT6": 0.00, "CAT12": 0.005, "CAT18": 0.01, "CAT24": 0.015, "CAT30": 0.02, "CAT36": 0.025, "CAT42": 0.03, "CAT48": 0.04, "CAT54": 0.05, "CAT60": 0.06},
        "Pi": {"CAT0": 0.0},
        "P": {"CAT0": 0.0},
        "X": {"CAT0": 0.0},
        "OPE": {"CAT0": 0.0}
    },
    "baseline_input": {
        "global": {
            "recruitment": {
                "Consultant": {
                    "A": {
                        "202501": 20, "202502": 20, "202503": 10, ...  # Monthly values
                    },
                    "AC": {
                        "202501": 8, "202502": 8, "202503": 8, ...
                    }
                }
            },
            "churn": {
                "Consultant": {
                    "A": {
                        "202501": 2, "202502": 2, "202503": 2, ...  # Monthly values
                    }
                }
            }
        }
    },
    "created_at": "2025-07-09 11:58:06.620940",
    "updated_at": "2025-07-09T12:00:55.585094"
}
```

### Key Principles (from existing documentation)

1. **List vs Dict Structures**: 
   - Roles with levels use dicts of levels, each level is a list of 12 monthly dicts
   - Flat roles use lists of 12 monthly dicts
2. **Consistent Field Names**: All components use the same field names (`fte`, `recruitment`, `churn`, etc.)
3. **Monthly Data Format**: Input uses YYYYMM format, output uses 0-based month indices
4. **Absolute Values**: All FTE, recruitment, and churn values are absolute numbers
5. **Service Resolution**: Use ScenarioService to resolve scenario data before simulation

## Technical Considerations

### Implementation Strategy

1. **Phase 1**: Define the unified data structure and validation
2. **Phase 2**: Update backend services to use the new structure
3. **Phase 3**: Update frontend to use the new structure
4. **Phase 4**: Add migration utilities for existing scenarios
5. **Phase 5**: Remove old data structures

### Migration Plan

- Create adapter functions to convert old formats to new format
- Maintain backward compatibility during transition
- Gradual migration of existing scenarios
- Clear deprecation timeline for old formats

### Validation Rules

- All required fields must be present
- Field types must match expected types
- Office names must exist in configuration
- Role names must exist in configuration
- Level names must be valid for the role
- Numeric values must be within valid ranges

## Success Metrics

1. **Zero Data Structure Bugs**: No more bugs caused by inconsistent data formats
2. **Reduced Development Time**: Faster development due to predictable data structures
3. **Improved Code Quality**: Better type safety and validation
4. **Easier Debugging**: Clear data flow and error messages
5. **Successful Migration**: All existing scenarios work with new structure

## Open Questions

1. Should we support both old and new formats during transition, or force immediate migration?
2. How should we handle validation errors - fail fast or provide warnings?
3. Should we add data versioning to support future structure changes?
4. How should we handle missing optional fields - use defaults or require explicit values?
5. Should we add data transformation logging for debugging purposes? 