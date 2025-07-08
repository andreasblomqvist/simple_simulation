# Simulation Engine Specification

## Overview

This document defines the exact input/output contract for the SimpleSim simulation engine. The frontend should be adapted to match this specification, not the other way around.

## Engine Function Signature

```python
def run_simulation_with_offices(
    start_year: int,
    start_month: int, 
    end_year: int,
    end_month: int,
    offices: Dict[str, Office],
    progression_config: Dict[str, Any],
    cat_curves: Dict[str, Any],
    price_increase: float = 0.0,
    salary_increase: float = 0.0,
    economic_params: Optional[EconomicParameters] = None
) -> Dict[str, Any]:
```

## Input Specification

### 1. Time Range Parameters
- **start_year**: Simulation start year (e.g., 2025)
- **start_month**: Simulation start month (1-12)
- **end_year**: Simulation end year (e.g., 2027)
- **end_month**: Simulation end month (1-12)

### 2. Offices Data Structure

The `offices` parameter is a dictionary where each key is an office name and each value is an `Office` object:

```python
offices = {
    "Stockholm": Office(...),
    "Berlin": Office(...),
    "Oslo": Office(...)
}
```

#### Office Object Structure
```python
@dataclass
class Office:
    name: str                    # Office name (e.g., "Stockholm")
    total_fte: float            # Total FTE for the office
    journey: str                # Journey classification (e.g., "Mature Office")
    roles: Dict[str, Any]       # Dictionary of roles
```

#### Roles Structure
```python
roles = {
    "Consultant": {
        "A": Level(...),        # Level A
        "AC": Level(...),       # Level AC
        "C": Level(...),        # Level C
        "SrC": Level(...),      # Level SrC
        "AM": Level(...),       # Level AM
        "M": Level(...),        # Level M
        "SrM": Level(...),      # Level SrM
        "Pi": Level(...),       # Level Pi
        "P": Level(...)         # Level P
    },
    "Sales": {
        "A": Level(...),
        "AC": Level(...),
        # ... other sales levels
    },
    "Operations": RoleData(...)  # Flat role (no levels)
}
```

#### Level Object Structure
```python
@dataclass
class Level:
    name: str                   # Level name (e.g., "A")
    fte: float                  # Current FTE count
    price_1: float             # Price for month 1
    price_2: float             # Price for month 2
    # ... price_3 through price_12
    salary_1: float            # Salary for month 1
    salary_2: float            # Salary for month 2
    # ... salary_3 through salary_12
    
    # Monthly recruitment rates (ABSOLUTE numbers, not percentages)
    recruitment_1: float       # January recruitment (absolute number of people)
    recruitment_2: float       # February recruitment (absolute number of people)
    # ... recruitment_3 through recruitment_12
    
    # Monthly churn rates (ABSOLUTE numbers, not percentages)
    churn_1: float            # January churn (absolute number of people)
    churn_2: float            # February churn (absolute number of people)
    # ... churn_3 through churn_12
    
    # Monthly progression rates (MULTIPLIERS applied to CAT progression matrix)
    progression_1: float      # January progression multiplier (e.g., 1.2 = 20% increase)
    progression_2: float      # February progression multiplier (e.g., 1.2 = 20% increase)
    # ... progression_3 through progression_12
    
    # Optional: Absolute recruitment/churn (overrides percentage if present)
    recruitment_abs_1: Optional[float]  # Absolute recruits in January
    recruitment_abs_2: Optional[float]  # Absolute recruits in February
    # ... recruitment_abs_3 through recruitment_abs_12
    
    churn_abs_1: Optional[float]       # Absolute churn in January
    churn_abs_2: Optional[float]       # Absolute churn in February
    # ... churn_abs_3 through churn_abs_12
```

#### RoleData Object Structure (for flat roles like Operations)
```python
@dataclass
class RoleData:
    name: str                   # Role name (e.g., "Operations")
    fte: float                  # Current FTE count
    price_1: float             # Price for month 1
    # ... price_2 through price_12
    salary_1: float            # Salary for month 1
    # ... salary_2 through salary_12
    recruitment_1: float       # January recruitment (absolute number of people)
    # ... recruitment_2 through recruitment_12
    churn_1: float            # January churn (absolute number of people)
    # ... churn_2 through churn_12
```

### 3. Progression Configuration

```python
progression_config = {
    "Consultant": {
        "A": {
            "next_level": "AC",
            "progression_months": [5, 11],  # May and November
            "progression_rate": 0.15        # 15% progression rate
        },
        "AC": {
            "next_level": "C",
            "progression_months": [5, 11],
            "progression_rate": 0.12
        },
        # ... other levels
    },
    "Sales": {
        # ... sales progression rules
    }
}
```

### 4. CAT Curves

```python
cat_curves = {
    "Consultant": {
        "A": {
            "progression_probability": 0.8,  # 80% chance of progression when eligible
            "retention_probability": 0.95    # 95% retention rate
        },
        # ... other levels
    }
}
```

### 5. Economic Parameters

```python
@dataclass
class EconomicParameters:
    unplanned_absence: float = 0.05        # 5% unplanned absence
    other_expense: float = 19000000.0      # 19M SEK monthly other expenses
    employment_cost_rate: float = 0.40     # 40% overhead on salary costs
    working_hours_per_month: float = 166.4 # Monthly working hours
    utilization: float = 0.85              # 85% utilization rate
    price_increase: float = 0.0            # Annual price increase (0-1)
    salary_increase: float = 0.0           # Annual salary increase (0-1)
```

## Output Specification

The engine returns a dictionary with the following structure:

```python
{
    "years": {
        "2025": {
            "offices": {
                "Stockholm": {
                    "levels": {
                        "Consultant": {
                            "A": [
                                {
                                    "month": "2025-01",
                                    "fte": 69.0,
                                    "price": 1200.0,
                                    "salary": 480.0,
                                    "recruitment": 3.45,  # 5% of 69
                                    "churn": 1.38,        # 2% of 69
                                    "progression": 0.0,   # No progression in Jan
                                    "total": 69.0
                                },
                                # ... one entry per month
                            ],
                            "AC": [
                                # ... monthly data for AC level
                            ]
                        },
                        "Operations": [
                            # ... monthly data for Operations
                        ]
                    },
                    "total_fte": 821,
                    "total_salary_costs": 39408000.0,
                    "total_revenue": 98520000.0,
                    "ebitda": 59112000.0,
                    "margin": 0.60
                }
            },
            "system_totals": {
                "total_fte": 1642,
                "total_salary_costs": 78816000.0,
                "total_revenue": 197040000.0,
                "total_ebitda": 118224000.0,
                "average_margin": 0.60
            }
        },
        "2026": {
            # ... same structure for 2026
        }
    },
    "monthly_data": {
        "2025-01": {
            "Stockholm": {
                "Consultant": {
                    "A": {
                        "fte": 69.0,
                        "price": 1200.0,
                        "salary": 480.0,
                        "recruitment": 3.45,
                        "churn": 1.38,
                        "progression": 0.0
                    }
                }
            }
        }
        # ... one entry per month
    },
    "kpis": {
        "financial": {
            "net_sales": 197040000.0,
            "total_salary_costs": 78816000.0,
            "ebitda": 118224000.0,
            "margin": 0.60
        },
        "growth": {
            "total_growth_percent": 15.2,
            "total_growth_absolute": 216,
            "current_total_fte": 1642,
            "baseline_total_fte": 1426
        },
        "journeys": {
            "journey_totals": {
                "Journey 1": 456,
                "Journey 2": 789,
                "Journey 3": 397
            },
            "journey_percentages": {
                "Journey 1": 27.8,
                "Journey 2": 48.0,
                "Journey 3": 24.2
            }
        }
    }
}
```

## Frontend Adaptation Requirements

### 1. Scenario Definition Format

The frontend should send scenario definitions in this format:

```json
{
  "scenario_definition": {
    "name": "Growth Scenario",
    "description": "High recruitment, low churn",
    "time_range": {
      "start_year": 2025,
      "start_month": 1,
      "end_year": 2027,
      "end_month": 12
    },
    "office_scope": ["Stockholm", "Berlin"],
    "levers": {
      "Stockholm": {
        "Consultant": {
          "A": {
            "recruitment_1": 3,      // 3 people recruited in January
            "recruitment_2": 3,      // 3 people recruited in February
            // ... all 12 months
            "churn_1": 1,            // 1 person leaves in January
            "churn_2": 1,            // 1 person leaves in February
            // ... all 12 months
            "progression_1": 1.0,    // No change to progression in January
            "progression_2": 1.0,    // No change to progression in February
            // ... all 12 months
          }
        }
      }
    },
    "economic_params": {
      "price_increase": 0.03,        // 3% annual price increase
      "salary_increase": 0.02,       // 2% annual salary increase
      "unplanned_absence": 0.05,
      "other_expense": 19000000.0,
      "employment_cost_rate": 0.40,
      "working_hours_per_month": 166.4,
      "utilization": 0.85
    }
  }
}
```

### 2. Key Differences from Current Frontend

1. **Monthly Values**: Frontend must specify values for all 12 months, not just annual multipliers
2. **Office-Role-Level Structure**: Levers must be organized by office → role → level → month
3. **Absolute Numbers**: Recruitment and churn values are absolute numbers of people, not percentages
4. **Progression Multipliers**: Progression values are multipliers applied to the CAT progression matrix
5. **Missing Office/Role Context**: Frontend doesn't specify which offices/roles the levers apply to

### 3. Data Assembly Responsibility

The backend adapter layer is responsible for:
- Loading baseline office/role/level data from configuration
- Applying lever modifications to baseline data
- Assembling complete Office objects with all required fields
- Validating data completeness before calling the engine

## Validation Rules

1. **FTE Values**: Must be >= 0
2. **Recruitment/Churn**: Must be >= 0 (absolute numbers of people)
3. **Progression Multipliers**: Must be >= 0 (multipliers applied to CAT matrix)
4. **Prices/Salaries**: Must be > 0
5. **Time Range**: End date must be after start date
6. **Office Scope**: Must reference valid office names
7. **Level Names**: Must match expected level names (A, AC, C, SrC, AM, M, SrM, Pi, P)

## Error Handling

The engine will raise ValueError for:
- Empty offices dictionary
- Missing required fields in Level/RoleData objects
- Invalid time ranges
- Negative FTE values
- Invalid rate values (outside 0-1 range)

## Performance Characteristics

- **Deterministic**: Same input always produces same output
- **Monthly Processing**: Simulates month-by-month progression
- **Memory Usage**: Scales linearly with number of offices × roles × levels × months
- **Execution Time**: Typically 1-5 seconds for 3-year simulations with multiple offices 