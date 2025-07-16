# Simulation Engine Data Structures

This document describes the exact structure of input and output data for the simulation engine, including the distinction between lists and dicts for different role types.

## Table of Contents

1. [Input Data Structures](#input-data-structures)
2. [Output Data Structures](#output-data-structures)
3. [Data Flow](#data-flow)
4. [Common Patterns](#common-patterns)
5. [List vs Dict Structures](#list-vs-dict-structures)

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

## Data Flow

1. **Input:** Scenario definition with baseline data, progression config, and CAT curves
2. **Processing:** Simulation engine processes month by month, applying recruitment, churn, and progression
3. **Output:** Results organized by year → office → role → level/month (using dicts and lists as described) 