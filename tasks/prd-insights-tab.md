# Product Requirements Document: Insights Tab

## 1. Introduction/Overview
The Insights Tab provides executives with a high-level, visual summary of simulation results for each year, supporting strategic decision-making without requiring users to drill into excessive detail. It offers a global view by default, with the option to focus on individual offices.

## 2. Goals
- Enable executives to quickly understand key workforce and financial trends from simulation results.
- Present clear, visually engaging charts and KPIs for each simulation year.
- Allow switching between global (all offices) and per-office views.
- Ensure the UI is consistent with the rest of the application (Ant Design, dark mode, etc.).

## 3. User Stories
- As an executive, I want to see a workforce pyramid for each year so I can understand changes in the company's structure.
- As an executive, I want to see stacked bar charts showing recruitment, churn, and progression by level, so I can identify where changes are happening.
- As an executive, I want to see key KPIs (growth, non-debit ratio, net revenue, EBITDA, margin) for each year, so I can assess company performance at a glance.
- As an executive, I want to switch between a global view and individual offices, so I can compare performance across the company.

## 4. Functional Requirements
1. The system must display a pyramid chart for each year, showing the number of employees at each level, color-coded by journey.
2. The system must display stacked bar charts for each year, showing changes per level (recruitment, churn, progression).
3. The system must display KPI cards for each year, including:
   - Growth (absolute and %)
   - Non-debit ratio
   - Net revenue
   - EBITDA
   - Margin
4. The system must default to a global (all offices) view.
5. The system must allow the user to select an individual office to view office-specific insights.
6. The system must update all charts and KPIs when the year or office selection changes.
7. The system must use the existing Ant Design and Ant Design Charts libraries, and support dark mode.
8. The system must handle years or offices with missing or incomplete data gracefully (e.g., show "No data available").
9. The system must present all charts and KPIs in a layout that is clear and executive-friendly.

## 5. Non-Goals (Out of Scope)
- Editing or drilling down into raw simulation data.
- Exporting charts or data to PDF/CSV.
- Customizing chart types or KPI formulas.
- Showing data below the office level (e.g., by team or individual).

## 6. Design Considerations
- Use Ant Design Charts' Pyramid/Funnel and Stacked Bar components.
- Ensure all charts are responsive and visually consistent with the app.
- Use clear legends, tooltips, and axis labels.
- Support dark mode and executive-friendly color schemes.

## 7. Technical Considerations
- Integrate with the existing simulation results data structure.
- Ensure performance is acceptable for large simulations (e.g., many years/offices).
- Use memoization or virtualization if needed for chart rendering.

## 8. Success Metrics
- Executives can answer key questions about workforce and financial trends without drilling into raw data.
- All charts and KPIs update correctly when the year or office is changed.
- Feature adoption by executive users (qualitative feedback or usage metrics).

## 9. Open Questions
- Should the Insights tab be accessible to all users, or only to executives?
- Should there be any export or sharing functionality in the future?
- Are there any specific accessibility requirements (e.g., screen reader support?) 