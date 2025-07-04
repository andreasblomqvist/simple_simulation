# Simulation Engine Documentation

## Overview
The simulation engine processes three main dynamics for each role and level on a **monthly basis**:
1. **Churn (Attrition)**
2. **Progression (Promotion)**
3. **Recruitment (Hiring)**

## Core Components

### 1. Churn (Attrition)
- Each level has separate churn rates for each month (1-12)
- Churn is applied first in each period
- Formula: `new_total = current_total * (1 - churn_rate)`
- Example: If a level has 100 people and 5% churn, 95 people remain

### 2. Progression (Promotion)
- Each level has separate progression rates for each month (1-12)
- Progression is calculated after churn
- Formula: `progressed = current_total * progression_rate`
- Progressed employees move to the next level
- **Special progression timing rules:**
  - **A-AM levels**: Progression occurs in **May (month 5)** and **November (month 11)** only
  - **M+ levels (M, SrM, PiP)**: Progression occurs in **November (month 11)** only
  - **All other months**: No progression (rate = 0.0)

### 3. Recruitment (Hiring)
- Each level has separate recruitment rates for each month (1-12)
- Recruitment is applied last
- Formula: `new_recruits = current_total * recruitment_rate`
- Special handling for zero FTE:
  - For new offices: minimum 1 recruit
  - For other offices: calculated based on recruitment rate

## Processing Order

For each month, the engine processes levels in this order:

1. Apply churn to current level
2. Calculate and apply progression (only in evaluation months)
3. Move progressed employees to next level
4. Apply recruitment to current level

## Default Rates

### Junior Levels (A, AC)
- Higher progression (15% in May and November, 0% other months)
- Higher churn (4-5% monthly)
- Higher recruitment (15-25% monthly)

### Mid Levels (C, SrC, AM)
- Moderate progression (15% in May and November, 0% other months)
- Lower churn (3% monthly)
- Lower recruitment (10-15% monthly)

### Senior Levels (M, SrM, PiP)
- Lower progression (15% in November only, 0% other months)
- Lowest churn (1-2% monthly)
- Lowest recruitment (5-10% monthly)

## Example Configuration

### Basic Configuration (Percentage-Only)
```python
{
    "A": {
        "total": 10,
        "progression_1": 0.0,   # January - no progression
        "progression_2": 0.0,   # February - no progression
        "progression_3": 0.0,   # March - no progression
        "progression_4": 0.0,   # April - no progression
        "progression_5": 0.15,  # May - 15% progression (evaluation period)
        "progression_6": 0.0,   # June - no progression
        "progression_7": 0.0,   # July - no progression
        "progression_8": 0.0,   # August - no progression
        "progression_9": 0.0,   # September - no progression
        "progression_10": 0.0,  # October - no progression
        "progression_11": 0.15, # November - 15% progression (evaluation period)
        "progression_12": 0.0,  # December - no progression
        "recruitment_1": 0.2,   # 20% recruitment in January
        "recruitment_2": 0.2,   # 20% recruitment in February
        # ... (recruitment_3 through recruitment_12)
        "churn_1": 0.05,        # 5% churn in January
        "churn_2": 0.05,        # 5% churn in February
        # ... (churn_3 through churn_12)
        "utr_1": 0.85,          # 85% UTR in January
        "utr_2": 0.85,          # 85% UTR in February
        # ... (utr_3 through utr_12)
    }
}
```

### Enhanced Configuration (Absolute + Percentage)
The engine now supports both absolute numbers and percentage-based values for recruitment and churn:

```python
{
    "A": {
        "total": 10,
        # Progression rates (unchanged)
        "progression_1": 0.0,   # January - no progression
        "progression_2": 0.0,   # February - no progression
        "progression_3": 0.0,   # March - no progression
        "progression_4": 0.0,   # April - no progression
        "progression_5": 0.15,  # May - 15% progression (evaluation period)
        "progression_6": 0.0,   # June - no progression
        "progression_7": 0.0,   # July - no progression
        "progression_8": 0.0,   # August - no progression
        "progression_9": 0.0,   # September - no progression
        "progression_10": 0.0,  # October - no progression
        "progression_11": 0.15, # November - 15% progression (evaluation period)
        "progression_12": 0.0,  # December - no progression
        
        # Percentage-based recruitment (fallback)
        "recruitment_1": 0.2,   # 20% recruitment in January
        "recruitment_2": 0.2,   # 20% recruitment in February
        "recruitment_3": 0.2,   # 20% recruitment in March
        # ... (recruitment_4 through recruitment_12)
        
        # Absolute recruitment (overrides percentage if present)
        "recruitment_abs_1": 3,   # Exactly 3 new hires in January
        "recruitment_abs_2": null, # No absolute value for February (use percentage)
        "recruitment_abs_3": 5,   # Exactly 5 new hires in March
        "recruitment_abs_4": null,
        "recruitment_abs_5": null,
        "recruitment_abs_6": null,
        "recruitment_abs_7": null,
        "recruitment_abs_8": null,
        "recruitment_abs_9": null,
        "recruitment_abs_10": null,
        "recruitment_abs_11": null,
        "recruitment_abs_12": null,
        
        # Percentage-based churn (fallback)
        "churn_1": 0.05,        # 5% churn in January
        "churn_2": 0.05,        # 5% churn in February
        "churn_3": 0.05,        # 5% churn in March
        # ... (churn_4 through churn_12)
        
        # Absolute churn (overrides percentage if present)
        "churn_abs_1": null,      # No absolute value for January (use percentage)
        "churn_abs_2": 1,         # Exactly 1 person leaves in February
        "churn_abs_3": null,      # No absolute value for March (use percentage)
        "churn_abs_4": null,
        "churn_abs_5": null,
        "churn_abs_6": null,
        "churn_abs_7": null,
        "churn_abs_8": null,
        "churn_abs_9": null,
        "churn_abs_10": null,
        "churn_abs_11": null,
        "churn_abs_12": null,
        
        # Other fields remain unchanged
        "utr_1": 0.85,          # 85% UTR in January
        "utr_2": 0.85,          # 85% UTR in February
        # ... (utr_3 through utr_12)
    }
}
```

### Precedence Rules for Absolute vs Percentage

1. **Absolute values take precedence**: If both `recruitment_1` and `recruitment_abs_1` are present, use `recruitment_abs_1`
2. **Percentage fallback**: If only `recruitment_1` is present, calculate as `recruitment_1 * current_fte`
3. **Null/None handling**: If `recruitment_abs_1` is `null` or not present, fall back to percentage calculation
4. **Zero handling**: If `recruitment_abs_1` is `0`, use exactly 0 (no recruitment)
5. **Missing both**: If neither field is present, treat as 0 and optionally log a warning

For detailed schema documentation, see [Absolute and Percentage-Based Recruitment/Churn Schema](absolute-percentage-schema.md).

## Recruitment Example

### Scenario 1: Normal Recruitment
Let's walk through a recruitment example for Level A in May (progression month):

1. **Initial State**
   - Current FTE: 10
   - Recruitment Rate: 20% (0.2)
   - Churn Rate: 5% (0.05)
   - Progression Rate: 15% (0.15) - May is evaluation period

2. **Process**
   ```
   Step 1: Apply Churn
   - Churned employees = 10 * 0.05 = 0.5 (rounded to 1)
   - Remaining employees = 10 - 1 = 9

   Step 2: Apply Progression (May = evaluation month)
   - Progressed employees = 9 * 0.15 = 1.35 (rounded to 1)
   - Employees after progression = 9 - 1 = 8

   Step 3: Apply Recruitment
   - New recruits = 8 * 0.2 = 1.6 (rounded to 2)
   - Final FTE = 8 + 2 = 10
   ```

### Scenario 2: Non-Evaluation Month
Let's walk through the same example for Level A in January (non-progression month):

1. **Initial State**
   - Current FTE: 10
   - Recruitment Rate: 20% (0.2)
   - Churn Rate: 5% (0.05)
   - Progression Rate: 0% (0.0) - January is NOT evaluation period

2. **Process**
   ```
   Step 1: Apply Churn
   - Churned employees = 10 * 0.05 = 0.5 (rounded to 1)
   - Remaining employees = 10 - 1 = 9

   Step 2: Apply Progression (January = no progression)
   - Progressed employees = 9 * 0.0 = 0
   - Employees after progression = 9 - 0 = 9

   Step 3: Apply Recruitment
   - New recruits = 9 * 0.2 = 1.8 (rounded to 2)
   - Final FTE = 9 + 2 = 11
   ```

### Scenario 3: New Office Recruitment
For a new office with zero FTE:

1. **Initial State**
   - Current FTE: 0
   - Recruitment Rate: 20% (0.2)
   - Office Type: New Office

2. **Process**
   ```
   Step 1: Check Office Type
   - New Office → Minimum 1 recruit

   Step 2: Calculate Recruitment
   - Base calculation = 10 * 0.2 = 2
   - Minimum recruit = 1
   - Final recruits = max(1, 2) = 2
   ```

### Scenario 4: Growth from Zero (Established Office)
For an established office with zero FTE:

1. **Initial State**
   - Current FTE: 0
   - Recruitment Rate: 20% (0.2)
   - Office Type: Established Office

2. **Process**
   ```
   Step 1: Check Office Type
   - Established Office → No minimum recruit requirement

   Step 2: Calculate Recruitment
   - Base calculation = 10 * 0.2 = 2
   - Final recruits = 2
   ```

### Key Points
- Recruitment is always calculated after churn and progression
- New offices have a minimum recruitment of 1 FTE
- Recruitment rates can be different for each month (1-12)
- The base calculation (10 FTE) ensures growth even from zero
- All calculations are rounded to whole numbers

## Progression Timing (Evaluation Periods)

### A-AM Levels (A, AC, C, SrC, AM)
- **May (Month 5)**: Progression occurs (15% rate)
- **November (Month 11)**: Progression occurs (15% rate)
- **All other months**: No progression (0% rate)

### Senior Levels (M, SrM, PiP)
- **November (Month 11)**: Progression occurs (15% rate)
- **All other months**: No progression (0% rate)

### Operations (Flat Role)
- **All months**: No progression (0% rate)

This reflects real-world evaluation cycles where employee promotions happen during specific review periods.

## Special Cases

### 1. New Offices
- Minimum recruitment of 1 FTE even with zero current FTE
- Higher recruitment rates to support growth

### 2. Zero FTE Handling
- Recruitment calculated based on a base of 10 FTE
- Ensures growth even from zero

### 3. Management Levels
- No progression in most months for M, SrM, PiP levels
- Only progress during November evaluation period

### 4. Monthly Cycles
- Engine runs 12 cycles per year instead of 2
- More granular tracking of workforce changes
- Progression only during evaluation months creates realistic "stepping" patterns

## Output Tracking

The system tracks and outputs monthly:
- Total FTE for each level
- Price and salary changes
- Journey totals
- Period-by-period changes
- Progression events (only in evaluation months)

## Office Size Classification

Offices are classified based on total FTE:
- **New Office**: 0-24 FTE
- **Emerging Office**: 25-200 FTE
- **Established Office**: 200-500 FTE
- **Mature Office**: 500+ FTE 