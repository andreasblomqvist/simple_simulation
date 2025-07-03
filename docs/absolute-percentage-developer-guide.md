# Developer Guide: Absolute and Percentage-Based Recruitment/Churn Support

## Overview

This guide explains how to implement and use the new absolute and percentage-based recruitment/churn support in the SimpleSim simulation engine. This feature allows mixing and matching absolute numbers and percentage-based values for maximum flexibility in business planning.

## Architecture

### Data Model Changes

The simulation engine now supports both absolute and percentage fields for recruitment and churn:

#### RoleData Class
```python
@dataclass
class RoleData:
    # Percentage-based recruitment (existing)
    recruitment_1: float = 0.0
    recruitment_2: float = 0.0
    # ... recruitment_3 through recruitment_12
    
    # Absolute-based recruitment (new)
    recruitment_abs_1: Optional[int] = None
    recruitment_abs_2: Optional[int] = None
    # ... recruitment_abs_3 through recruitment_abs_12
    
    # Percentage-based churn (existing)
    churn_1: float = 0.0
    churn_2: float = 0.0
    # ... churn_3 through churn_12
    
    # Absolute-based churn (new)
    churn_abs_1: Optional[int] = None
    churn_abs_2: Optional[int] = None
    # ... churn_abs_3 through churn_abs_12
```

#### Level Class
The `Level` class has the same structure as `RoleData` for recruitment and churn fields.

### Precedence Rules

1. **Absolute values take precedence**: If both `recruitment_1` and `recruitment_abs_1` are present, use `recruitment_abs_1`
2. **Percentage fallback**: If only `recruitment_1` is present, calculate as `recruitment_1 * current_fte`
3. **Null/None handling**: If `recruitment_abs_1` is `null` or not present, fall back to percentage calculation
4. **Zero handling**: If `recruitment_abs_1` is `0`, use exactly 0 (no recruitment)
5. **Missing both**: If neither field is present, treat as 0 and log a warning

## Implementation Details

### Helper Functions

The core logic is implemented in two helper functions in `workforce.py`:

#### `get_effective_recruitment_value(obj, month, current_fte)`
```python
def get_effective_recruitment_value(obj, month: int, current_fte: int) -> Tuple[int, str, Dict[str, Any]]:
    """
    Get effective recruitment value based on precedence rules.
    Returns (value, method_used, details) where method_used is 'absolute' or 'percentage'.
    """
    # Check for absolute value first
    abs_field = f"recruitment_abs_{month}"
    abs_value = getattr(obj, abs_field, None)
    
    if abs_value is not None:
        details = {
            "method": "absolute",
            "absolute_value": abs_value,
            "percentage_value": getattr(obj, f"recruitment_{month}", None),
            "current_fte": current_fte,
            "field_used": abs_field
        }
        return int(abs_value), "absolute", details
    
    # Fall back to percentage calculation
    pct_field = f"recruitment_{month}"
    pct_value = getattr(obj, pct_field, 0.0)
    calculated_value = int(pct_value * current_fte)
    
    details = {
        "method": "percentage",
        "absolute_value": None,
        "percentage_value": pct_value,
        "current_fte": current_fte,
        "calculated_value": calculated_value,
        "field_used": pct_field
    }
    
    # Log warning if neither field is present
    if pct_value == 0.0 and not hasattr(obj, pct_field):
        debug_logger.warning(f"No recruitment value found for month {month}, using 0")
        details["warning"] = f"No recruitment_{month} field found, defaulting to 0"
    
    return calculated_value, "percentage", details
```

#### `get_effective_churn_value(obj, month, current_fte)`
Similar structure to recruitment function but for churn values.

### Integration with Workforce Processing

The workforce processing logic in `process_churn_and_recruitment()` has been updated to use these helper functions:

```python
# Churn - using new absolute/percentage logic
churn_to_apply, churn_method, churn_details = get_effective_churn_value(level, current_month_enum.value, level.total)
debug_logger.info(f"    Churn method: {churn_method}")
debug_logger.info(f"    Churn details: {churn_details}")
debug_logger.info(f"    Churn to apply: {churn_to_apply}")

# Recruitment - using new absolute/percentage logic
recruits_to_add, recruitment_method, recruitment_details = get_effective_recruitment_value(level, current_month_enum.value, level.total)
debug_logger.info(f"    Recruitment method: {recruitment_method}")
debug_logger.info(f"    Recruitment details: {recruitment_details}")
debug_logger.info(f"    Recruits to add: {recruits_to_add}")
```

### Metrics and Logging

The simulation now tracks which method was used for each calculation:

```python
monthly_office_metrics[office.name][current_date_str][role_name][level_name].update({
    'total_fte': level.total,
    'recruited': recruits_to_add,
    'recruitment_method': recruitment_method,
    'recruitment_details': recruitment_details,
    'churned': churn_to_apply,
    'churn_method': churn_method,
    'churn_details': churn_details,
    # ... other fields
})
```

## Configuration Examples

### Basic Configuration (Percentage-Only)
```json
{
  "Stockholm": {
    "name": "Stockholm",
    "total_fte": 100,
    "journey": "Mature Office",
    "roles": {
      "Consultant": {
        "A": {
          "fte": 50,
          "recruitment_1": 0.1,  // 10% recruitment
          "recruitment_2": 0.1,  // 10% recruitment
          "churn_1": 0.05,       // 5% churn
          "churn_2": 0.05        // 5% churn
        }
      }
    }
  }
}
```

### Enhanced Configuration (Absolute + Percentage)
```json
{
  "Stockholm": {
    "name": "Stockholm",
    "total_fte": 100,
    "journey": "Mature Office",
    "roles": {
      "Consultant": {
        "A": {
          "fte": 50,
          // Percentage-based recruitment (fallback)
          "recruitment_1": 0.1,      // 10% recruitment
          "recruitment_2": 0.1,      // 10% recruitment
          
          // Absolute recruitment (overrides percentage if present)
          "recruitment_abs_1": 5,    // Exactly 5 new hires in January
          "recruitment_abs_2": null, // No absolute value for February (use percentage)
          
          // Percentage-based churn (fallback)
          "churn_1": 0.05,           // 5% churn
          "churn_2": 0.05,           // 5% churn
          
          // Absolute churn (overrides percentage if present)
          "churn_abs_1": null,       // No absolute value for January (use percentage)
          "churn_abs_2": 2           // Exactly 2 people leave in February
        }
      }
    }
  }
}
```

## Validation

The `ConfigService` includes validation for the new fields:

```python
def validate_absolute_percentage_fields(self, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate absolute and percentage fields for recruitment and churn.
    Returns validation results with warnings and errors.
    """
    # Implementation details...
```

### Validation Rules

1. **Percentage range**: 0.0 ≤ percentage ≤ 1.0
2. **Absolute range**: 0 ≤ absolute ≤ 1000
3. **Consistency**: If both values present, absolute should be reasonable given percentage and current FTE
4. **Required fields**: At least one value (percentage or absolute) should be present for each month

## Testing

### Unit Tests

Unit tests are available in `backend/tests/unit/test_absolute_percentage_support.py`:

```python
def test_recruitment_absolute_takes_precedence(self):
    """Test that absolute recruitment values take precedence over percentage."""
    role_data = RoleData()
    role_data.recruitment_1 = 0.1  # 10% recruitment
    role_data.recruitment_abs_1 = 5  # 5 absolute recruits
    role_data.fte = 100  # 100 FTE
    
    value, method, details = get_effective_recruitment_value(role_data, 1, 100)
    
    assert value == 5
    assert method == "absolute"
    assert details["absolute_value"] == 5
```

### Integration Tests

Integration tests are available in `backend/tests/integration/test_absolute_percentage_integration.py`:

```python
def test_simulation_with_mixed_absolute_percentage_config(self):
    """Test end-to-end simulation with mixed absolute and percentage values."""
    # Test implementation...
```

## Backward Compatibility

The implementation maintains full backward compatibility:

- Existing configurations with only percentage fields continue to work unchanged
- New absolute fields are optional and don't break existing functionality
- The system gracefully handles missing absolute fields by falling back to percentages

## Migration Guide

### For Existing Users

No migration is required. Existing percentage-only configurations will continue to work exactly as before.

### For New Features

To add absolute values to existing configurations:

1. **Add absolute fields**: Include `recruitment_abs_X` and `churn_abs_X` fields where needed
2. **Set to null**: Use `null` values to indicate "use percentage fallback"
3. **Set to zero**: Use `0` to indicate "no recruitment/churn"
4. **Set to number**: Use positive integers for exact recruitment/churn counts

### Example Migration

**Before (Percentage-only)**:
```json
{
  "recruitment_1": 0.1,
  "churn_1": 0.05
}
```

**After (Mixed approach)**:
```json
{
  "recruitment_1": 0.1,      // Fallback percentage
  "recruitment_abs_1": 5,    // Override with absolute
  "churn_1": 0.05,          // Fallback percentage
  "churn_abs_1": null       // Use percentage
}
```

## Troubleshooting

### Common Issues

1. **Missing fields**: If neither absolute nor percentage fields are present, the system defaults to 0 and logs a warning
2. **Invalid ranges**: Validation will catch percentage values outside [0,1] and absolute values outside [0,1000]
3. **Inconsistent values**: Warnings are logged when absolute and percentage values differ significantly

### Debug Information

The simulation logs detailed information about which method was used:

```
Churn method: absolute
Churn details: {'method': 'absolute', 'absolute_value': 3, 'percentage_value': 0.05, 'current_fte': 100, 'field_used': 'churn_abs_1'}
Churn to apply: 3
```

### Validation Output

The config service validation provides detailed feedback:

```python
results = config_service.validate_absolute_percentage_fields(config)
print(f"Warnings: {results['warnings']}")
print(f"Errors: {results['errors']}")
```

## Future Enhancements

The architecture is designed to be extensible for future fields:

1. **Promotions**: Could add `progression_abs_X` fields
2. **Transfers**: Could add `transfer_abs_X` fields
3. **Other metrics**: Could add absolute values for other workforce dynamics

The helper function pattern can be easily extended to support these new fields. 