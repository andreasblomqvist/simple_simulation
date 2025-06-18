## Relevant Files

- `frontend/src/pages/InsightsTab.tsx` - Main React component for the Insights tab UI and logic.
- `frontend/src/components/WorkforcePyramidChart.tsx` - Pyramid chart for workforce levels and journeys.
- `frontend/src/components/LevelChangeStackedBar.tsx` - Stacked bar chart for recruitment, churn, progression per level.
- `frontend/src/components/KPICards.tsx` - KPI summary cards for growth, non-debit ratio, net revenue, EBITDA, and margin.
- `frontend/src/services/insightsApi.ts` - API service for fetching simulation results and insights data.
- `frontend/src/types/insights.ts` - TypeScript types for insights data structures.
- `frontend/src/components/__tests__/WorkforcePyramidChart.test.tsx` - Unit tests for the pyramid chart component.
- `frontend/src/components/__tests__/LevelChangeStackedBar.test.tsx` - Unit tests for the stacked bar chart component.
- `frontend/src/components/__tests__/KPICards.test.tsx` - Unit tests for the KPI cards component.

### Notes

- Unit tests should be placed alongside the code files they are testing.
- Use `npx jest` to run tests.

## Tasks

- [ ] 1.0 Design Insights Tab Layout and Navigation
  - [x] 1.1 Create wireframe/mockup for Insights Tab layout (global and per-office views)
  - [x] 1.2 Define navigation pattern (tab, menu, or button) to access Insights Tab
  - [x] 1.3 Specify Ant Design layout components to use (Row, Col, Card, Tabs, etc.)
  - [x] 1.4 Review with stakeholders for feedback

- [ ] 2.0 Implement Workforce Pyramid Chart (per year, per office)
  - [ ] 2.1 Define TypeScript types for pyramid chart data (`insights.ts`)
  - [ ] 2.2 Implement `WorkforcePyramidChart.tsx` using Ant Design Charts Pyramid/Funnel
  - [ ] 2.3 Add color-coding for journeys and level labels
  - [ ] 2.4 Add tooltips and data labels for FTE and journey breakdown
  - [ ] 2.5 Integrate with InsightsTab to update on year/office change
  - [ ] 2.6 Write unit tests for pyramid chart rendering and data mapping

- [x] 2.0 Implement combined stacked bar chart for recruitment, churn, and progression
  - [x] 2.1 Design the chart components and layout for the combined stacked bar chart (recruitment, churn, progression)
  - [x] 2.2 Implement combined stacked bar chart component (recruitment, churn, progression in one chart)
  - [x] 2.3 Integrate combined stacked bar chart into Insights tab UI
  - [x] 2.4 Add helper texts, tooltips, and legends for clarity
  - [x] 2.5 Ensure chart is responsive and supports dark mode
  - [x] 2.6 Write unit and integration tests for the combined chart component

- [ ] 4.0 Implement KPI Cards Panel (per year, per office) using existing EnhancedKPICard component
  - [x] 4.1 Identify and prepare KPI data for Insights tab (growth, non-debit ratio, net revenue, EBITDA, margin)
  - [x] 4.2 Render KPI cards using EnhancedKPICard for each metric
  - [ ] 4.3 Add tooltips, helper texts, and year-over-year indicators
  - [ ] 4.4 Ensure layout matches Insights tab design and is responsive
  - [ ] 4.5 Write unit and integration tests for KPI Cards Panel

- [ ] 5.0 Integrate Office/Year Selection and Data Fetching
  - [ ] 5.1 Implement year and office selector UI in InsightsTab
  - [ ] 5.2 Implement `insightsApi.ts` to fetch and transform simulation results for insights
  - [ ] 5.3 Ensure all charts and KPIs update reactively on selection change
  - [ ] 5.4 Handle loading and error states for data fetching

- [ ] 6.0 Ensure Responsive Design, Dark Mode, and Executive-Friendly UI
  - [ ] 6.1 Apply Ant Design responsive layout (Grid, Card, etc.)
  - [ ] 6.2 Ensure all charts and cards support dark mode
  - [ ] 6.3 Use clear, accessible color schemes and font sizes
  - [ ] 6.4 Test on different screen sizes and devices

- [ ] 7.0 Add Error Handling and Graceful No-Data States
  - [ ] 7.1 Show user-friendly messages when data is missing or incomplete
  - [ ] 7.2 Add fallback UI for empty charts or KPIs
  - [ ] 7.3 Log errors for debugging and support

- [ ] 8.0 Write Unit Tests for All New Components
  - [ ] 8.1 Write tests for InsightsTab layout and navigation
  - [ ] 8.2 Ensure 80%+ code coverage for new components
  - [ ] 8.3 Add tests for edge cases (no data, large data, etc.)


I have generated the high-level tasks based on the PRD. Ready to generate the sub-tasks? Respond with 'Go' to proceed. 