cna # Year-by-Year Navigation for Simulation Results

## Introduction/Overview
The simulation system currently shows only the end state of a multi-year simulation. This makes it difficult for executives to understand how key metrics evolve over time and make informed decisions about achieving their 20% margin goal. This feature will add year-by-year navigation to help users track the progression of KPIs and make better strategic decisions.

## Goals
1. Enable users to view simulation results year by year
2. Provide clear visualization of KPI progression over time
3. Support executive decision-making for achieving 20% margin target
4. Make it easy to identify trends and inflection points in key metrics

## User Stories
1. As an executive, I want to see how our margin progresses year by year so I can identify when we'll reach our 20% target
2. As an executive, I want to track seniority distribution changes over time to ensure sustainable growth
3. As an executive, I want to compare financial KPIs across years to understand the impact of different strategies
4. As an executive, I want to see growth metrics year by year to validate our expansion plans

## Functional Requirements
1. The system must display a year selector for navigating through simulation results
2. The system must show year-over-year changes in key KPIs:
   - Financial metrics (margin, revenue, costs)
   - Growth metrics (headcount, growth rate)
   - Seniority distribution (journey percentages)
3. The system must provide visual indicators for year-over-year changes (e.g., up/down arrows, percentages)
4. The system must maintain the current detailed view for the selected year
5. The system must support exporting data for specific years

## Non-Goals (Out of Scope)
1. Month-by-month navigation (year level is sufficient)
2. Real-time simulation adjustments
3. Historical data storage for previous simulation runs
4. Complex year-over-year comparisons across different simulation runs

## Design Considerations
1. Year selector should be prominent and easy to use
2. KPI changes should be visually distinct (e.g., green for positive, red for negative)
3. Maintain consistency with existing UI design
4. Use clear visualizations for year-over-year trends
5. Ensure mobile responsiveness for executive review

## Technical Considerations
1. Modify simulation engine to structure data by year
2. Add year-level aggregations for KPIs
3. Ensure efficient data loading for year navigation
4. Maintain backward compatibility with existing API
5. Consider caching for year-level data

## Success Metrics
1. Users can successfully navigate between years
2. Year-over-year KPI changes are clearly visible
3. System performance remains responsive during year navigation
4. Executives can make informed decisions based on year-by-year data

## Open Questions
1. Should we implement any specific year-over-year comparison features?
2. Do we need to support any specific export formats for year data?
3. Should we add any specific visualizations for year-over-year trends?
4. Do we need to implement any specific performance optimizations for large simulations? 