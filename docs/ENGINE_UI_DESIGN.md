# Engine UI Design - Complete Data Entry Form

## Overview

This document describes a comprehensive UI that allows users to input all data required by the simulation engine. The form will be organized in logical sections to make data entry manageable and clear.

## UI Structure

### 1. Simulation Parameters Section

```
┌─────────────────────────────────────────────────────────────┐
│ SIMULATION PARAMETERS                                        │
├─────────────────────────────────────────────────────────────┤
│ Start Date: [2025] [January ▼]    End Date: [2027] [December▼] │
│                                                                 │
│ Economic Parameters:                                           │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Price Increase: [3.0] %    Salary Increase: [2.0] %         │ │
│ │ Unplanned Absence: [5.0] %  Other Expense: [19,000,000] SEK │ │
│ │ Employment Cost Rate: [40.0] %  Working Hours: [166.4] hrs  │ │
│ │ Utilization Rate: [85.0] %                                  │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 2. Office Selection Section

```
┌─────────────────────────────────────────────────────────────┐
│ OFFICE SELECTION                                             │
├─────────────────────────────────────────────────────────────┤
│ Select Offices to Include:                                   │
│ ☑ Stockholm  ☑ Berlin  ☑ Oslo  ☑ Copenhagen  ☐ Helsinki    │
│                                                                 │
│ Journey Classification:                                       │
│ Stockholm: [Mature Office ▼]  Berlin: [Emerging Office ▼]    │
└─────────────────────────────────────────────────────────────┘
```

### 3. Role and Level Configuration Section

```
┌─────────────────────────────────────────────────────────────┐
│ ROLE & LEVEL CONFIGURATION                                   │
├─────────────────────────────────────────────────────────────┤
│ Office: [Stockholm ▼]  Role: [Consultant ▼]  Level: [A ▼]   │
│                                                                 │
│ Current State:                                                │
│ FTE: [69]  Base Price: [1200] SEK/hr  Base Salary: [480] SEK/hr │
│                                                                 │
│ Monthly Recruitment (Absolute Numbers):                      │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Jan: [3] Feb: [3] Mar: [4] Apr: [3] May: [4] Jun: [3]      │ │
│ │ Jul: [3] Aug: [4] Sep: [3] Oct: [4] Nov: [3] Dec: [3]      │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ Monthly Churn (Absolute Numbers):                            │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Jan: [1] Feb: [1] Mar: [2] Apr: [1] May: [1] Jun: [2]      │ │
│ │ Jul: [1] Aug: [1] Sep: [2] Oct: [1] Nov: [1] Dec: [2]      │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ Monthly Progression Multipliers:                              │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Jan: [1.0] Feb: [1.0] Mar: [1.0] Apr: [1.0] May: [1.2] Jun: [1.0] │
│ │ Jul: [1.0] Aug: [1.0] Sep: [1.0] Oct: [1.0] Nov: [1.2] Dec: [1.0] │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ [Save Level Config] [Copy to Other Offices] [Copy to Other Levels] │
└─────────────────────────────────────────────────────────────┘
```

### 4. Bulk Operations Section

```
┌─────────────────────────────────────────────────────────────┐
│ BULK OPERATIONS                                              │
├─────────────────────────────────────────────────────────────┤
│ Apply to: [All Offices ▼] [All Roles ▼] [All Levels ▼]     │
│                                                                 │
│ Recruitment Pattern:                                          │
│ ☑ Uniform: [3] people per month                             │
│ ☐ Seasonal: Peak [5] in [Q2], Base [2] in [Q4]             │
│ ☐ Growth: Start [2], End [6], Linear increase               │
│                                                                 │
│ Churn Pattern:                                                │
│ ☑ Uniform: [1] person per month                             │
│ ☐ Seasonal: Peak [3] in [Q4], Base [0] in [Q1]             │
│ ☐ Declining: Start [3], End [0], Linear decrease            │
│                                                                 │
│ Progression Pattern:                                          │
│ ☑ Standard: [1.0] base, [1.2] in [May, November]           │
│ ☐ Enhanced: [1.3] in evaluation months                     │
│ ☐ Custom: [Define pattern...]                               │
│                                                                 │
│ [Apply Bulk Settings] [Reset to Defaults]                   │
└─────────────────────────────────────────────────────────────┘
```

### 5. Progression Rules Section

```
┌─────────────────────────────────────────────────────────────┐
│ PROGRESSION RULES                                            │
├─────────────────────────────────────────────────────────────┤
│ Role: [Consultant ▼]                                         │
│                                                                 │
│ Level Progression Path:                                       │
│ A → AC → C → SrC → AM → M → SrM → Pi → P                    │
│                                                                 │
│ Progression Months (Evaluation Periods):                     │
│ A: [May, November]  AC: [May, November]  C: [May, November] │
│ SrC: [May, November]  AM: [May, November]  M: [May, November] │
│ SrM: [May, November]  Pi: [May, November]  P: [May, November] │
│                                                                 │
│ Progression Rates:                                            │
│ A: [15]%  AC: [12]%  C: [10]%  SrC: [8]%  AM: [6]%          │
│ M: [5]%  SrM: [4]%  Pi: [3]%  P: [2]%                       │
└─────────────────────────────────────────────────────────────┘
```

### 6. CAT Curves Section

```
┌─────────────────────────────────────────────────────────────┐
│ CAT CURVES (Progression Probabilities)                      │
├─────────────────────────────────────────────────────────────┤
│ Role: [Consultant ▼]                                         │
│                                                                 │
│ Progression Probabilities:                                   │
│ A: [80]%  AC: [75]%  C: [70]%  SrC: [65]%  AM: [60]%        │
│ M: [55]%  SrM: [50]%  Pi: [45]%  P: [40]%                   │
│                                                                 │
│ Retention Probabilities:                                     │
│ A: [95]%  AC: [96]%  C: [97]%  SrC: [98]%  AM: [98]%        │
│ M: [99]%  SrM: [99]%  Pi: [99]%  P: [99]%                   │
└─────────────────────────────────────────────────────────────┘
```

### 7. Data Import/Export Section

```
┌─────────────────────────────────────────────────────────────┐
│ DATA MANAGEMENT                                              │
├─────────────────────────────────────────────────────────────┤
│ [Import from Excel] [Export to Excel] [Load Template]       │
│ [Save Configuration] [Load Configuration] [Reset All]       │
│                                                                 │
│ Template Types:                                               │
│ • Baseline (Current State)                                   │
│ • Growth Scenario (High Recruitment)                         │
│ • Efficiency Scenario (Low Churn)                            │
│ • Custom Template                                            │
└─────────────────────────────────────────────────────────────┘
```

### 8. Validation and Run Section

```
┌─────────────────────────────────────────────────────────────┐
│ VALIDATION & EXECUTION                                       │
├─────────────────────────────────────────────────────────────┤
│ [Validate Configuration] [Show Validation Report]           │
│                                                                 │
│ Validation Status: ☑ All fields complete  ☑ Data valid      │
│ Warnings: 2 offices have incomplete progression data        │
│                                                                 │
│ [Run Simulation] [Save as Scenario] [Cancel]                │
└─────────────────────────────────────────────────────────────┘
```

## Results Display Section

### 9. Simulation Results Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│ SIMULATION RESULTS                                           │
├─────────────────────────────────────────────────────────────┤
│ Simulation: "Growth Scenario" | Duration: 2025-01 to 2027-12 │
│ Execution Time: 2.3 seconds | Status: ✅ Completed          │
│                                                                 │
│ [Export Results] [Save Scenario] [Compare Scenarios] [New Run] │
└─────────────────────────────────────────────────────────────┘
```

### 10. Summary Metrics Section

```
┌─────────────────────────────────────────────────────────────┐
│ SUMMARY METRICS (2025-2027)                                 │
├─────────────────────────────────────────────────────────────┤
│ Financial KPIs:                                              │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Net Sales: 2,364,480,000 SEK    (+15.2% vs baseline)       │ │
│ │ Total Salary Costs: 945,792,000 SEK  (+12.8% vs baseline)  │ │
│ │ EBITDA: 1,418,688,000 SEK       (+16.8% vs baseline)       │ │
│ │ Margin: 60.0%                   (+1.2% vs baseline)        │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ Growth KPIs:                                                   │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Total Growth: +216 FTE        (+15.2% vs baseline)          │ │
│ │ Current Total FTE: 1,642      (Baseline: 1,426)             │ │
│ │ Non-Debit Ratio: 78.5%        (+2.1% vs baseline)           │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ Journey Distribution:                                          │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Journey 1 (Junior): 456 FTE (27.8%)    [+45 vs baseline]   │ │
│ │ Journey 2 (Mid): 789 FTE (48.0%)       [+89 vs baseline]   │ │
│ │ Journey 3 (Senior): 397 FTE (24.2%)    [+82 vs baseline]   │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 11. Monthly Trend Charts Section

```
┌─────────────────────────────────────────────────────────────┐
│ MONTHLY TRENDS                                               │
├─────────────────────────────────────────────────────────────┤
│ Chart Type: [FTE Growth ▼] [Revenue ▼] [EBITDA ▼] [Margin ▼] │
│ Office: [All Offices ▼]  Role: [All Roles ▼]  Level: [All Levels ▼] │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │                                                             │ │
│ │    FTE Growth Over Time                                     │ │
│ │    1800 ┤                                                    │ │
│ │    1700 ┤    ╭───╮                                          │ │
│ │    1600 ┤   ╱     ╲                                         │ │
│ │    1500 ┤  ╱       ╲                                        │ │
│ │    1400 ┤ ╱         ╲                                       │ │
│ │         ┼───────────────────────────────────────────────── │ │
│ │    2025 │ 2026 │ 2027 │ 2028 │ 2029 │ 2030 │ 2031 │ 2032 │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ [Download Chart] [Full Screen] [Export Data]                  │
└─────────────────────────────────────────────────────────────┘
```

### 12. Detailed Monthly Data Section

```
┌─────────────────────────────────────────────────────────────┐
│ DETAILED MONTHLY DATA                                        │
├─────────────────────────────────────────────────────────────┤
│ Office: [Stockholm ▼]  Role: [Consultant ▼]  Level: [A ▼]   │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Month      │ FTE │ Revenue │ Salary │ EBITDA │ Margin │ Growth │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ 2025-01    │ 69  │ 8.28M   │ 3.31M  │ 4.97M  │ 60.0%  │ +3     │ │
│ │ 2025-02    │ 71  │ 8.52M   │ 3.41M  │ 5.11M  │ 60.0%  │ +2     │ │
│ │ 2025-03    │ 73  │ 8.76M   │ 3.50M  │ 5.26M  │ 60.0%  │ +2     │ │
│ │ 2025-04    │ 75  │ 9.00M   │ 3.60M  │ 5.40M  │ 60.0%  │ +2     │ │
│ │ 2025-05    │ 78  │ 9.36M   │ 3.74M  │ 5.62M  │ 60.0%  │ +3     │ │
│ │ 2025-06    │ 80  │ 9.60M   │ 3.84M  │ 5.76M  │ 60.0%  │ +2     │ │
│ │ ...        │ ... │ ...     │ ...    │ ...    │ ...    │ ...    │ │
│ │ 2027-12    │ 95  │ 11.40M  │ 4.56M  │ 6.84M  │ 60.0%  │ +2     │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ [Export to Excel] [Show All Months] [Filter Data]             │
└─────────────────────────────────────────────────────────────┘
```

### 13. Office Comparison Section

```
┌─────────────────────────────────────────────────────────────┐
│ OFFICE COMPARISON                                            │
├─────────────────────────────────────────────────────────────┤
│ Metric: [Total FTE ▼] [EBITDA ▼] [Margin ▼] [Growth Rate ▼] │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Office     │ Baseline │ Current │ Change │ % Change │       │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ Stockholm  │ 821      │ 945     │ +124   │ +15.1%   │ ████████ │ │
│ │ Berlin     │ 456      │ 523     │ +67    │ +14.7%   │ ███████  │ │
│ │ Oslo       │ 149      │ 174     │ +25    │ +16.8%   │ ████████ │ │
│ │ Total      │ 1,426    │ 1,642   │ +216   │ +15.2%   │ ████████ │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ [Sort by Column] [Export Comparison] [Show Details]           │
└─────────────────────────────────────────────────────────────┘
```

### 14. Role and Level Breakdown Section

```
┌─────────────────────────────────────────────────────────────┐
│ ROLE & LEVEL BREAKDOWN                                       │
├─────────────────────────────────────────────────────────────┤
│ Office: [Stockholm ▼]  Year: [2027 ▼]                       │
│                                                                 │
│ Consultant Levels:                                            │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Level │ Baseline │ Current │ Change │ % of Total │ Trend   │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ A     │ 69       │ 95      │ +26    │ 10.1%      │ ↗↗↗     │ │
│ │ AC    │ 45       │ 62      │ +17    │ 6.6%       │ ↗↗      │ │
│ │ C     │ 38       │ 52      │ +14    │ 5.5%       │ ↗↗      │ │
│ │ SrC   │ 32       │ 44      │ +12    │ 4.7%       │ ↗↗      │ │
│ │ AM    │ 28       │ 38      │ +10    │ 4.0%       │ ↗       │ │
│ │ M     │ 25       │ 34      │ +9     │ 3.6%       │ ↗       │ │
│ │ SrM   │ 22       │ 30      │ +8     │ 3.2%       │ ↗       │ │
│ │ Pi    │ 18       │ 25      │ +7     │ 2.6%       │ ↗       │ │
│ │ P     │ 15       │ 21      │ +6     │ 2.2%       │ ↗       │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ Operations: 12 FTE (1.3% of total)                            │
│ Sales: 34 FTE (3.6% of total)                                 │
│                                                                 │
│ [Show All Offices] [Export Breakdown] [Chart View]           │
└─────────────────────────────────────────────────────────────┘
```

### 15. Scenario Comparison Section

```
┌─────────────────────────────────────────────────────────────┐
│ SCENARIO COMPARISON                                          │
├─────────────────────────────────────────────────────────────┤
│ Compare: [Growth Scenario ▼] vs [Baseline ▼] vs [Efficiency ▼] │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Metric        │ Baseline │ Growth │ Efficiency │ Best      │ │
│ ├─────────────────────────────────────────────────────────────┤ │
│ │ Total FTE     │ 1,426    │ 1,642  │ 1,389      │ Growth    │ │
│ │ EBITDA        │ 1,214M   │ 1,419M │ 1,198M     │ Growth    │ │
│ │ Margin        │ 58.8%    │ 60.0%  │ 59.2%      │ Growth    │ │
│ │ Growth Rate   │ 2.1%     │ 15.2%  │ -2.6%      │ Growth    │ │
│ │ Non-Debit     │ 76.4%    │ 78.5%  │ 75.1%      │ Growth    │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ [Side-by-Side Charts] [Export Comparison] [Create New Scenario] │
└─────────────────────────────────────────────────────────────┘
```

### 16. Export and Sharing Section

```
┌─────────────────────────────────────────────────────────────┐
│ EXPORT & SHARING                                             │
├─────────────────────────────────────────────────────────────┤
│ Export Format: [Excel ▼] [PDF ▼] [CSV ▼] [JSON ▼]           │
│                                                                 │
│ Export Options:                                               │
│ ☑ Summary Metrics    ☑ Monthly Data    ☑ Office Comparison  │
│ ☑ Role Breakdown     ☑ Charts          ☑ Raw Data           │
│                                                                 │
│ [Generate Report] [Email Results] [Save to Library]          │
│                                                                 │
│ Report Preview:                                               │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Executive Summary                                           │ │
│ │ • 15.2% FTE growth over 3 years                            │ │
│ │ • 16.8% EBITDA improvement                                 │ │
│ │ • 60.0% margin maintained                                  │ │
│ │ • Strong growth in junior levels (Journey 1)               │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Key UI Features

### 1. Smart Defaults
- Pre-populate with current configuration data
- Suggest reasonable values based on industry standards
- Auto-calculate derived values (e.g., total FTE)

### 2. Bulk Operations
- Apply patterns across multiple offices/roles/levels
- Copy configurations between similar entities
- Template-based configuration

### 3. Validation
- Real-time validation as user types
- Clear error messages and suggestions
- Visual indicators for missing or invalid data

### 4. Data Import/Export
- Excel import/export for bulk data entry
- Configuration templates for common scenarios
- Save/load configurations

### 5. Progressive Disclosure
- Start with basic parameters
- Expand to detailed monthly data as needed
- Collapsible sections for advanced users

## Data Flow

1. **User fills form** → All required engine data captured
2. **Validation** → Ensures data completeness and validity
3. **Data assembly** → Converts form data to engine objects
4. **Engine call** → Direct call to `run_simulation_with_offices()`
5. **Results display** → Show monthly and yearly results

## Benefits

- **Complete data capture**: No missing fields
- **Direct engine compatibility**: No mapping required
- **User-friendly**: Logical organization and smart defaults
- **Flexible**: Supports both simple and complex scenarios
- **Validated**: Ensures data quality before engine execution

This UI design ensures that users can input exactly what the engine needs, eliminating the mapping and data mismatch issues we've been experiencing. 

This comprehensive results display ensures users can:
- **Understand the impact** of their scenario changes
- **Compare different scenarios** effectively
- **Export results** for presentations and analysis
- **Drill down** into specific details as needed
- **Share insights** with stakeholders 