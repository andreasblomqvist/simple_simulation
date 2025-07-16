# Simulation Engine Data Structures

This document describes the exact structure of input and output data for the simulation engine, including the distinction between lists and dicts for different role types.

## Table of Contents

1. [Input Data Structures](#input-data-structures)
2. [Output Data Structures](#output-data-structures)
3. [Scenario Service Input/Output](#scenario-service-inputoutput)
4. [Data Flow](#data-flow)
5. [Common Patterns](#common-patterns)
6. [List vs Dict Structures](#list-vs-dict-structures)

## Input Data Structures

### Scenario Definition (Input to `/scenarios/run`)

- **Roles with levels** (e.g., Consultant):
  - Dict of levels, each with FTE, price, salary, recruitment, churn, etc.
- **Flat roles** (e.g., Operations):
  - Dict with FTE, price, salary, recruitment, churn, etc. (no levels)

## Output Data Structures

### High-Level Structure

- `results['years']` → dict keyed by year (e.g., '2024')
  - `['offices']` → dict keyed by office name (e.g., 'Stockholm')
    - `['roles']` → dict keyed by role name (e.g., 'Consultant', 'Operations')
      - **For roles with levels:** dict keyed by level name (e.g., 'A', 'AC', ...)
        - **Each level:** list of 12 dicts (one per month)
      - **For flat roles:** list of 12 dicts (one per month)

### Example: Leveled Role (Consultant)
```python
# Access FTE for Consultant, level 'A', month 1 (January)
fte_jan = results['years']['2024']['offices']['Stockholm']['roles']['Consultant']['A'][0]['fte']
recruitment_jan = results['years']['2024']['offices']['Stockholm']['roles']['Consultant']['A'][0]['recruitment']
churn_jan = results['years']['2024']['offices']['Stockholm']['roles']['Consultant']['A'][0]['churn']

# Loop over months for a level
for month_idx, month_data in enumerate(results['years']['2024']['offices']['Stockholm']['roles']['Consultant']['A']):
    print(f"Month {month_idx+1}: FTE={month_data['fte']}, Recruitment={month_data['recruitment']}, Churn={month_data['churn']}")
```

### Example: Flat Role (Operations)
```python
# Access FTE for Operations, month 1 (January)
fte_jan = results['years']['2024']['offices']['Stockholm']['roles']['Operations'][0]['fte']
recruitment_jan = results['years']['2024']['offices']['Stockholm']['roles']['Operations'][0]['recruitment']
churn_jan = results['years']['2024']['offices']['Stockholm']['roles']['Operations'][0]['churn']

# Loop over months for a flat role
for month_idx, month_data in enumerate(results['years']['2024']['offices']['Stockholm']['roles']['Operations']):
    print(f"Month {month_idx+1}: FTE={month_data['fte']}, Recruitment={month_data['recruitment']}, Churn={month_data['churn']}")
```

### Example: Iterating Over All Roles and Levels
```python
for role_name, role_data in office_data['roles'].items():
    if isinstance(role_data, dict):
        # Leveled role
        for level_name, level_data in role_data.items():
            for month_idx, month_data in enumerate(level_data):
                print(f"Role {role_name} Level {level_name} Month {month_idx+1}: FTE={month_data['fte']}")
    elif isinstance(role_data, list):
        # Flat role
        for month_idx, month_data in enumerate(role_data):
            print(f"Role {role_name} Month {month_idx+1}: FTE={month_data['fte']}")
```

## Scenario Service Input/Output

### SimulationEngine.run_simulation() Method Signature

```python
def run_simulation(self, start_year: int, start_month: int, end_year: int, end_month: int,
                  price_increase: float = 0.0, salary_increase: float = 0.0,
                  lever_plan: Optional[Dict] = None,
                  economic_params: Optional[EconomicParameters] = None) -> Dict:
    """
    Run simulation with lever plan and economic parameters.
    
    Args:
        start_year: Starting year
        start_month: Starting month (1-12)
        end_year: Ending year
        end_month: Ending month (1-12)
        price_increase: Annual price increase percentage
        salary_increase: Annual salary increase percentage
        lever_plan: Optional lever plan to apply
        economic_params: Optional economic parameters for KPI calculations
    
    Returns:
        dict: Simulation results with structure described in Output Data Structures
    """
```

### Scenario Definition Structure (Input)

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
    "economic_params": {},
    "progression_config": null,  # or progression configuration
    "cat_curves": null,  # or CAT curve configuration
    "baseline_input": {
        "global": {
            "recruitment": {
                "Consultant": {
                    "A": {
                        "202501": 20, "202502": 20, "202503": 10, ...  # Monthly values
                    },
                    "AC": {
                        "202501": 8, "202502": 8, "202503": 8, ...
                    },
                    # ... other levels
                },
                "Sales": {
                    # ... similar structure
                }
            },
            "churn": {
                "Consultant": {
                    "A": {
                        "202501": 2, "202502": 2, "202503": 2, ...  # Monthly values
                    },
                    "AC": {
                        "202501": 4, "202502": 4, "202503": 4, ...
                    },
                    # ... other levels
                },
                "Sales": {
                    # ... similar structure
                }
            }
        }
    },
    "created_at": "2025-07-09 11:58:06.620940",
    "updated_at": "2025-07-09T12:00:55.585094"
}
```

### Accessing Scenario Input Data

```python
# Extract time range
start_year = scenario_data['time_range']['start_year']
start_month = scenario_data['time_range']['start_month']
end_year = scenario_data['time_range']['end_year']
end_month = scenario_data['time_range']['end_month']

# Extract recruitment data
baseline_input = scenario_data.get('baseline_input', {})
global_data = baseline_input.get('global', {})
recruitment_data = global_data.get('recruitment', {})

# Access specific recruitment values
consultant_a_recruitment = recruitment_data.get('Consultant', {}).get('A', {})
jan_recruitment = consultant_a_recruitment.get('202501', 0)

# Extract churn data
churn_data = global_data.get('churn', {})
consultant_a_churn = churn_data.get('Consultant', {}).get('A', {})
jan_churn = consultant_a_churn.get('202501', 0)
```

### Running Simulation with Scenario Data (Correct Method)

```python
from services.simulation_engine import SimulationEngine
from services.scenario_service import ScenarioService
from services.config_service import ConfigService

# Initialize services
config_service = ConfigService()
scenario_service = ScenarioService(config_service)
simulation_engine = SimulationEngine()

# Extract time parameters from scenario
time_range = scenario_data['time_range']
start_year = time_range['start_year']
start_month = time_range['start_month']
end_year = time_range['end_year']
end_month = time_range['end_month']

# Resolve scenario data using scenario service
resolved_data = scenario_service.resolve_scenario(scenario_data)

# Run simulation with resolved data
results = simulation_engine.run_simulation_with_offices(
    start_year=start_year,
    start_month=start_month,
    end_year=end_year,
    end_month=end_month,
    offices=resolved_data['offices'],
    progression_config=resolved_data['progression_config'],
    cat_curves=resolved_data['cat_curves']
)
```

### Alternative: Using ScenarioService.run_scenario()

```python
from services.scenario_service import ScenarioService
from services.config_service import ConfigService
from models.scenario_models import ScenarioRequest, ScenarioDefinition

# Initialize services
config_service = ConfigService()
scenario_service = ScenarioService(config_service)

# Create scenario request
scenario_request = ScenarioRequest(
    scenario_definition=scenario_definition,  # Your scenario data
    scenario_id=None  # Set to ID if using existing scenario
)

# Run scenario (this handles all the resolution and simulation internally)
response = scenario_service.run_scenario(scenario_request)
results = response.results
```

## List vs Dict Structures

- **Roles with levels:**
  - `roles['Consultant']` is a dict of levels (e.g., 'A', 'AC', ...)
  - Each level is a **list** of 12 dicts (one per month)
- **Flat roles:**
  - `roles['Operations']` is a **list** of 12 dicts (one per month)

### Dict Structure (Leveled Role)
```python
roles['Consultant'] = {
    'A': [ {month1_dict}, {month2_dict}, ..., {month12_dict} ],
    'AC': [ {month1_dict}, ..., {month12_dict} ],
    ...
}
```

### List Structure (Flat Role)
```python
roles['Operations'] = [ {month1_dict}, {month2_dict}, ..., {month12_dict} ]
```

### Month Dict Example
```python
month_dict = {
    'fte': 69.0,
    'price': 1200.0,
    'salary': 45000.0,
    'recruitment': 5,
    'churn': 2,
    'progression': 0,
    # ... other fields ...
}
```

## Important Notes

- Always check if a role is a dict (leveled) or a list (flat) before iterating.
- Each month is represented by an index (0=January, 11=December) in the list.
- All FTE, recruitment, and churn values are **absolute numbers**.
- This structure is consistent for all offices, years, and roles.
- Scenario input uses YYYYMM format for month keys (e.g., "202501" for January 2025).
- Simulation output uses 0-based month indices in lists.
- **Use ScenarioService to resolve scenario data before passing to SimulationEngine.**

## Data Flow

1. **Input:** Scenario definition with baseline data, progression config, and CAT curves
2. **Resolution:** ScenarioService resolves scenario data into offices, progression config, and CAT curves
3. **Processing:** Simulation engine processes month by month, applying recruitment, churn, and progression
4. **Output:** Results organized by year → office → role → level/month (using dicts and lists as described) 