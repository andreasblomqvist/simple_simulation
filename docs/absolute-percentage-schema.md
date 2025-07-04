# Absolute and Percentage-Based Recruitment/Churn Schema

## Overview

This document defines the data model for supporting both absolute numbers and percentage-based values for recruitment and churn in the simulation engine. The system will support mixing and matching these approaches at the office/role/level/month granularity.

## Schema Definition

### Current Schema (Percentage-Only)

The current system uses percentage-based fields:

```json
{
  "Stockholm": {
    "name": "Stockholm",
    "total_fte": 821,
    "journey": "Mature Office",
    "roles": {
      "Consultant": {
        "A": {
          "fte": 69.0,
          "recruitment_1": 0.04,    // 4% monthly recruitment rate
          "recruitment_2": 0.04,
          "recruitment_3": 0.04,
          "recruitment_4": 0.04,
          "recruitment_5": 0.04,
          "recruitment_6": 0.04,
          "recruitment_7": 0.04,
          "recruitment_8": 0.04,
          "recruitment_9": 0.04,
          "recruitment_10": 0.04,
          "recruitment_11": 0.04,
          "recruitment_12": 0.04,
          "churn_1": 0.02,          // 2% monthly churn rate
          "churn_2": 0.02,
          "churn_3": 0.02,
          "churn_4": 0.02,
          "churn_5": 0.02,
          "churn_6": 0.02,
          "churn_7": 0.02,
          "churn_8": 0.02,
          "churn_9": 0.02,
          "churn_10": 0.02,
          "churn_11": 0.02,
          "churn_12": 0.02,
          "price_1": 1200.0,
          "salary_1": 45000.0,
          "utr_1": 0.85
          // ... other months
        }
      }
    }
  }
}
```

### Enhanced Schema (Absolute + Percentage)

The enhanced system supports both absolute and percentage fields with clear precedence rules:

```json
{
  "Stockholm": {
    "name": "Stockholm",
    "total_fte": 821,
    "journey": "Mature Office",
    "roles": {
      "Consultant": {
        "A": {
          "fte": 69.0,
          
          // Percentage-based recruitment (fallback)
          "recruitment_1": 0.04,    // 4% monthly recruitment rate
          "recruitment_2": 0.04,
          "recruitment_3": 0.04,
          "recruitment_4": 0.04,
          "recruitment_5": 0.04,
          "recruitment_6": 0.04,
          "recruitment_7": 0.04,
          "recruitment_8": 0.04,
          "recruitment_9": 0.04,
          "recruitment_10": 0.04,
          "recruitment_11": 0.04,
          "recruitment_12": 0.04,
          
          // Absolute recruitment (overrides percentage if present)
          "recruitment_abs_1": 3,   // Exactly 3 new hires in January
          "recruitment_abs_2": null, // No absolute value for February (use percentage)
          "recruitment_abs_3": 5,   // Exactly 5 new hires in March
          "recruitment_abs_4": null,
          "recruitment_abs_5": null,
          "recruitment_abs_6": null,
          "recruitment_abs_7": null,
          "recruitment_abs_8": null,
          "recruitment_abs_9": null,
          "recruitment_abs_10": null,
          "recruitment_abs_11": null,
          "recruitment_abs_12": null,
          
          // Percentage-based churn (fallback)
          "churn_1": 0.02,          // 2% monthly churn rate
          "churn_2": 0.02,
          "churn_3": 0.02,
          "churn_4": 0.02,
          "churn_5": 0.02,
          "churn_6": 0.02,
          "churn_7": 0.02,
          "churn_8": 0.02,
          "churn_9": 0.02,
          "churn_10": 0.02,
          "churn_11": 0.02,
          "churn_12": 0.02,
          
          // Absolute churn (overrides percentage if present)
          "churn_abs_1": null,      // No absolute value for January (use percentage)
          "churn_abs_2": 1,         // Exactly 1 person leaves in February
          "churn_abs_3": null,      // No absolute value for March (use percentage)
          "churn_abs_4": null,
          "churn_abs_5": null,
          "churn_abs_6": null,
          "churn_abs_7": null,
          "churn_abs_8": null,
          "churn_abs_9": null,
          "churn_abs_10": null,
          "churn_abs_11": null,
          "churn_abs_12": null,
          
          // Other fields remain unchanged
          "price_1": 1200.0,
          "salary_1": 45000.0,
          "utr_1": 0.85
          // ... other months
        }
      }
    }
  }
}
```

## Field Naming Convention

### Recruitment Fields
- **Percentage-based**: `recruitment_1`, `recruitment_2`, ..., `recruitment_12`
- **Absolute-based**: `recruitment_abs_1`, `recruitment_abs_2`, ..., `recruitment_abs_12`

### Churn Fields
- **Percentage-based**: `churn_1`, `churn_2`, ..., `churn_12`
- **Absolute-based**: `churn_abs_1`, `churn_abs_2`, ..., `churn_abs_12`

## Precedence Rules

1. **Absolute values take precedence**: If both `recruitment_1` and `recruitment_abs_1` are present, use `recruitment_abs_1`
2. **Percentage fallback**: If only `recruitment_1` is present, calculate as `recruitment_1 * current_fte`
3. **Null/None handling**: If `recruitment_abs_1` is `null` or not present, fall back to percentage calculation
4. **Zero handling**: If `recruitment_abs_1` is `0`, use exactly 0 (no recruitment)
5. **Missing both**: If neither field is present, treat as 0 and optionally log a warning

## Data Types

- **Percentage fields**: `float` (0.0 to 1.0, representing 0% to 100%)
- **Absolute fields**: `int` or `null` (whole numbers representing exact headcount)
- **Null values**: Indicate "use percentage fallback"

## Validation Rules

1. **Percentage range**: 0.0 ≤ percentage ≤ 1.0
2. **Absolute range**: 0 ≤ absolute ≤ reasonable_max (e.g., 1000)
3. **Consistency**: If both values present, absolute should be reasonable given percentage and current FTE
4. **Required fields**: At least one value (percentage or absolute) should be present for each month

## Backward Compatibility

- Existing configurations with only percentage fields will continue to work unchanged
- New absolute fields are optional and don't break existing functionality
- The system gracefully handles missing absolute fields by falling back to percentages

## Example Scenarios

### Scenario 1: Mixed Approach
```json
{
  "recruitment_1": 0.04,      // 4% fallback
  "recruitment_abs_1": 3,     // Override: exactly 3 hires
  "recruitment_2": 0.04,      // 4% fallback  
  "recruitment_abs_2": null,  // Use percentage: 4% of current FTE
  "recruitment_3": 0.04,      // 4% fallback
  "recruitment_abs_3": 0      // Override: exactly 0 hires
}
```

### Scenario 2: Percentage-Only (Backward Compatible)
```json
{
  "recruitment_1": 0.04,      // 4% of current FTE
  "recruitment_2": 0.04,      // 4% of current FTE
  "recruitment_3": 0.04       // 4% of current FTE
}
```

### Scenario 3: Absolute-Only
```json
{
  "recruitment_abs_1": 5,     // Exactly 5 hires
  "recruitment_abs_2": 3,     // Exactly 3 hires
  "recruitment_abs_3": 7      // Exactly 7 hires
}
```

## Implementation Notes

1. **Data loading**: Config service should parse both field types
2. **Simulation logic**: Workforce manager should check absolute first, then percentage
3. **Logging**: Track which method was used for each calculation
4. **Validation**: Warn if both values are missing or if values are inconsistent
5. **UI support**: Frontend should allow editing both field types (handled in separate PRD) 