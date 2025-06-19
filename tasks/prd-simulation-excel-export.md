# Product Requirements Document: Simulation Excel Export

## Introduction/Overview

The Simulation Excel Export feature will enable users to export comprehensive simulation results, parameters, and KPIs to Excel format for offline data analysis, audit trail maintenance, and external reporting. This feature addresses the critical need for operations and data teams to perform detailed analysis outside the web interface and maintain compliance through comprehensive audit trails.

The primary goal is to provide a complete, one-click export solution that captures all simulation data in a structured, Excel-friendly format that supports advanced analysis workflows.

## Goals

1. **Enable Comprehensive Data Analysis**: Provide complete simulation datasets in Excel format for advanced offline analysis
2. **Establish Audit Trail**: Create detailed records of simulation parameters, timestamps, and results for compliance purposes
3. **Support Operations Workflows**: Enable data teams to integrate simulation results with existing Excel-based analysis tools
4. **Ensure Data Completeness**: Export all relevant simulation data including parameters, KPIs, detailed results, and movement logs
5. **Maintain Data Integrity**: Generate fresh exports with accurate, current data every time

## User Stories

1. **As a Data Analyst**, I want to export complete simulation results to Excel so that I can perform advanced pivot table analysis and create custom visualizations beyond what the web interface provides.

2. **As an Operations Manager**, I want to export simulation parameters and results so that I can maintain audit trails for compliance and review what scenarios were analyzed.

3. **As a Finance Team Member**, I want to export financial KPIs and projections so that I can integrate them into our existing financial planning models and board presentations.

4. **As a Business Intelligence Analyst**, I want to export detailed monthly/yearly breakdowns by office so that I can perform cross-functional analysis and identify trends not visible in the web interface.

5. **As a Compliance Officer**, I want to export timestamped simulation records so that I can demonstrate what analysis was performed and when for audit purposes.

## Functional Requirements

### Core Export Functionality
1. The system must provide a one-click "Export to Excel" button in the Simulation Results section
2. The system must generate fresh Excel files on each export request (no caching of export files)
3. The system must include a timestamp in the filename using format: `SimulationExport_YYYY-MM-DD_HH-MM.xlsx`
4. The system must complete export generation within 60 seconds for simulations up to 5 years duration

### Data Content Requirements
5. The system must export all simulation parameters including:
   - Economic parameters (price increase, salary increase, working hours, unplanned absence, other expenses)
   - Applied levers (type, levels, values, scope, application timestamp)
   - Simulation duration and date range
   - User who ran the simulation and execution timestamp

6. The system must export all KPI data including:
   - Financial KPIs (Net Sales, EBITDA, Margin) for each year
   - Growth KPIs (Total Growth %, FTE changes, Non-debit ratios)
   - Journey analysis (Journey 1-4 distributions and changes)
   - Baseline comparisons for all metrics

7. The system must export detailed results including:
   - Office-level data for each month/year
   - Role and level breakdowns (FTE counts, revenue, costs)
   - Movement logs (recruitment, churn, progression data)
   - Monthly progression tracking

### Excel Structure Requirements
8. The system must organize data into multiple sheets:
   - **Summary**: Simulation parameters, overall KPIs, audit information
   - **Financial_KPIs**: Year-over-year financial metrics
   - **Office_Details**: Monthly breakdown by office, role, and level
   - **Journey_Analysis**: Seniority distribution and changes
   - **Movement_Logs**: Detailed recruitment, churn, and progression data
   - **Baseline_Comparison**: Current vs baseline metrics

9. The system must format Excel sheets for professional presentation:
   - Bold headers with background colors
   - Proper number formatting (currency, percentages, integers)
   - Auto-adjusted column widths
   - Freeze panes on header rows

### Data Accuracy Requirements
10. The system must ensure exported data matches exactly with web interface displays
11. The system must include data validation indicators showing calculation formulas where applicable
12. The system must handle missing or zero values appropriately (display as 0 or "N/A" as appropriate)

### Error Handling Requirements
13. The system must display clear error messages if export generation fails
14. The system must validate that simulation results exist before allowing export
15. The system must handle large datasets (up to 10 years, all offices) without memory errors

## Non-Goals (Out of Scope)

1. **Real-time Data Streaming**: Exports are point-in-time snapshots, not live data feeds
2. **Custom Export Configurations**: Users cannot customize which data to include/exclude
3. **Automated Scheduling**: No automatic recurring exports or email delivery
4. **Multiple Format Support**: Only Excel (.xlsx) format, no CSV, PDF, or other formats
5. **Historical Export Storage**: System does not maintain a library of previous exports
6. **Data Transformation**: Raw simulation data only, no custom calculations or aggregations
7. **Integration APIs**: No programmatic access to export functionality
8. **Collaborative Features**: No sharing, commenting, or multi-user export features

## Design Considerations

### User Interface
- Export button should be prominently placed in the Simulation Results card header
- Button should be disabled when no simulation results are available
- Loading state should show progress during export generation
- Success state should automatically trigger file download

### Excel Formatting
- Use company color scheme for headers (blue/white theme)
- Apply conditional formatting for positive/negative changes
- Include data source and generation timestamp in each sheet
- Use consistent decimal places (2 for currency, 1 for percentages)

## Technical Considerations

### Backend Implementation
- Leverage existing `pandas` and `openpyxl` libraries already in the project
- Create new `/api/simulation/export` endpoint
- Reuse existing KPI calculation services
- Implement proper memory management for large datasets

### Frontend Integration
- Add export functionality to existing `SimulationLabV2.tsx` component
- Use browser's native file download mechanism
- Provide clear feedback during export process
- Handle download errors gracefully

### Performance Optimization
- Generate exports server-side to avoid frontend memory limitations
- Implement streaming for large datasets if needed
- Add progress indicators for exports taking >10 seconds

## Success Metrics

1. **Adoption Rate**: 70% of simulation users utilize export feature within first month
2. **Data Accuracy**: 100% accuracy between exported data and web interface displays
3. **Performance**: 95% of exports complete within 30 seconds
4. **Error Rate**: <2% of export attempts result in errors
5. **User Satisfaction**: Users report export meets their analysis needs in user feedback
6. **Audit Compliance**: Export records support compliance requirements as validated by operations team

## Open Questions

1. **File Size Warnings**: Should we warn users when exports will exceed 25MB or take longer than expected?
2. **Access Control**: Should export functionality be available to all users or restricted to specific roles?
3. **Export History**: Would a simple "last exported" timestamp be valuable for audit purposes?
4. **Integration Requirements**: Are there specific Excel versions or features we need to ensure compatibility with?
5. **Data Retention**: How long should users be expected to retain exported files for audit purposes?

## Acceptance Criteria

### Minimum Viable Product (MVP)
- [ ] Export button available in Simulation Results section
- [ ] Generates Excel file with all 6 required sheets
- [ ] Includes complete simulation parameters and KPI data
- [ ] Professional formatting with headers and number formatting
- [ ] File downloads automatically upon generation
- [ ] Export completes within 60 seconds for 3-year simulations
- [ ] Exported data matches web interface accuracy

### Success Criteria
- [ ] Data analysts can perform offline analysis using exported data
- [ ] Operations team can maintain audit trails with exported records
- [ ] Finance team can integrate KPIs into external planning tools
- [ ] Export feature handles edge cases (empty data, large simulations) gracefully
- [ ] User feedback confirms export meets analysis workflow needs 