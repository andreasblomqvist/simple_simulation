# Organization Simulation Analysis Report

## Executive Summary

This report analyzes the organization simulation results provided and identifies significant discrepancies in the growth calculations. The analysis reveals major inconsistencies between the calculated values from the raw simulation data and the values presented in the screenshot summary.

## Key Findings

### 1. Major Data Discrepancies Identified

The analysis reveals substantial differences between calculated and reported values:

- **FTE (Full-Time Equivalent) Values**: The calculated FTE values are 5-50 times higher than those shown in the screenshot
- **Recruitment Rates**: Calculated recruitment rates are significantly higher than reported rates
- **Churn Rates**: Calculated churn rates also show major discrepancies
- **Net Growth Calculations**: The percentage calculations appear to be fundamentally flawed

### 2. Scale of the Problem

The discrepancies are not minor rounding errors but represent fundamental calculation issues:

| Level | Screenshot FTE | Calculated FTE | Ratio |
|-------|----------------|----------------|-------|
| A     | 163.0          | 5,143.2        | 31.5x |
| AC    | 231.0          | 12,874.3       | 55.7x |
| AM    | 418.0          | 17,356.8       | 41.5x |
| C     | 356.0          | 3,186.6        | 8.9x  |
| M     | 156.0          | 5,373.7        | 34.4x |

## Detailed Analysis

### Data Structure Investigation

The simulation data contains:
- **12 offices** across multiple locations (Stockholm, Munich, Hamburg, Helsinki, Oslo, Berlin, Copenhagen, Zurich, Frankfurt, Amsterdam, Cologne, Toronto)
- **Multiple roles** including Consultant, Operations, Recruitment, and Sales
- **8 levels** (A, AC, AM, C, M, PiP, SrC, SrM)
- **Monthly data** for 12 months (72 months total across 6 years)

### Hypothesis Testing Results

#### Hypothesis 1: Screenshot Shows Single Office Data
**Result**: REJECTED
- Even individual office data shows values much smaller than screenshot values
- No single office matches the screenshot pattern

#### Hypothesis 2: Screenshot Shows Single Role Data
**Result**: PARTIALLY SUPPORTED
- Consultant-only data is closer but still significantly higher than screenshot values
- Suggests screenshot may be showing a subset of roles

#### Hypothesis 3: Screenshot Shows Different Time Period
**Result**: INCONCLUSIVE
- December snapshot data is closer to screenshot values but still 5-10x higher
- Suggests potential time period mismatch

#### Hypothesis 4: Units or Calculation Method Mismatch
**Result**: HIGHLY LIKELY
- The consistent ratio differences suggest a systematic calculation error
- Possible issues include:
  - Incorrect aggregation method
  - Wrong time period averaging
  - Missing data filtering
  - Incorrect percentage calculations

### Specific Calculation Issues

#### 1. Recruitment Percentage Calculations
The screenshot shows recruitment percentages that don't match the mathematical relationship:
- Level A: 2.076 FTE/month ÷ 163.0 FTE = 1.27% (matches screenshot)
- However, calculated data: 747.423 FTE/month ÷ 5,143.2 FTE = 14.53%

#### 2. Churn Percentage Calculations
Similar issues exist with churn calculations:
- Screenshot shows much lower churn rates than mathematically possible given the absolute numbers

#### 3. Net Growth Calculations
The net growth percentages in the screenshot appear to be calculated correctly as:
Net Growth % = Recruitment % - Churn %

However, the underlying recruitment and churn values appear to be incorrect.

## Root Cause Analysis

### Most Likely Causes

1. **Data Filtering Issue**: The screenshot may be showing data for a specific subset that wasn't identified in the analysis
2. **Time Period Mismatch**: The screenshot might represent a different time period or calculation method
3. **Aggregation Error**: The simulation data might be double-counting or incorrectly aggregating across dimensions
4. **Display Units Error**: The screenshot values might be in different units (e.g., percentages vs. absolute numbers)

### Evidence Supporting Each Cause

**Data Filtering Issue**:
- Consistent ratios across all levels suggest systematic filtering
- No single office or role combination matches exactly

**Time Period Mismatch**:
- December snapshot data is closer but still significantly different
- Possible the screenshot shows a different year or quarter

**Aggregation Error**:
- The 72 months of data (6 years × 12 months) suggests potential over-aggregation
- Multiple offices and roles being summed incorrectly

## Recommendations

### Immediate Actions Required

1. **Verify Data Source**: Confirm which subset of data the screenshot represents
2. **Check Calculation Logic**: Review the formulas used to generate the screenshot values
3. **Validate Time Periods**: Ensure both datasets represent the same time period
4. **Audit Aggregation Rules**: Verify how data is being summed across offices, roles, and time periods

### Technical Recommendations

1. **Implement Data Validation**: Add checks to ensure FTE calculations are reasonable
2. **Create Audit Trail**: Track how each value in the summary is derived from raw data
3. **Add Unit Tests**: Implement automated tests for percentage calculations
4. **Document Assumptions**: Clearly document which data subsets and time periods are being used

### Process Improvements

1. **Standardize Reporting**: Ensure all stakeholders use the same calculation methods
2. **Regular Reconciliation**: Implement monthly reconciliation between raw data and summaries
3. **Clear Documentation**: Document exactly what each metric represents and how it's calculated

## Conclusion

The analysis reveals significant discrepancies that suggest fundamental issues with either the data processing or the calculation methodology used to generate the screenshot summary. The scale of the differences (5-50x) indicates this is not a minor error but a systematic problem that requires immediate attention.

The most likely explanation is that the screenshot represents a specific subset of the data (possibly a single office, role, or time period) that differs from the full dataset analysis. However, without additional context about how the screenshot values were generated, it's impossible to definitively identify the root cause.

**Priority**: HIGH - These discrepancies could lead to incorrect business decisions if not resolved immediately.

---

*Analysis conducted on: December 30, 2025*  
*Data source: simulation_results_20250630_161229.json*

