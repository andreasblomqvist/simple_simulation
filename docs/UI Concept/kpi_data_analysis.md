
# KPI and Data Display Analysis

## Current KPI Display

From the provided screenshots, the Key Performance Indicators (KPIs) are displayed in a section titled "Key Performance Indicators" with two main sub-sections: "Financial Performance" and "Growth & Headcount Performance".

### Financial Performance KPIs:
- **Net Sales**: Displays current value, percentage change, and baseline/target values.
- **EBITDA**: Displays current value, percentage change, and baseline/target values.
- **Margin**: Displays current value, percentage change, and baseline/target values.

### Growth & Headcount Performance KPIs:
- **Total Growth**: Displays current value, percentage change, and baseline/target values.
- **Non-Debit Ratio**: Displays current value, percentage change, and baseline/target values.
- **Consultant Growth**: Displays current value, percentage change, and baseline/target values.

Each KPI card shows:
- A prominent current value.
- A small indicator for percentage change (e.g., +175.9%).
- Baseline and target values below the current value.

## Current Data Results Display

The data results are displayed in a table format below the KPI section. The table has columns such as:
- **Office / Level / Role**
- **Journey**
- **FTE**
- **Delta**
- **Price**
- **Salary**

This table appears to be expandable, showing details for different offices (e.g., Stockholm, Munich, Hamburg). The data seems to be a detailed breakdown supporting the aggregated KPIs.

## Observations and Initial Thoughts on Current Display:
- **KPIs are present but could be more visually impactful.** The current display is functional but lacks strong visual hierarchy or graphical representation to quickly convey trends or performance against targets.
- **Data table is detailed but might overwhelm.** While necessary for detailed analysis, the table can be dense and might not be the primary focus for a user interested in high-level KPIs.
- **Connection between KPIs and detailed data is implicit.** It's not immediately clear how the detailed table data contributes to each specific KPI.

## Reference Design Analysis (Ant Design Visualization Page)

The provided Ant Design visualization page (https://github.com/ant-design/ant-design/blob/master/docs/spec/visualization-page.en-US.md) showcases several key principles and patterns that can be applied:

1.  **Emphasis on Visuals**: The page heavily uses charts and graphs (line charts, bar charts, pie charts) to represent data, making it easier to grasp trends and comparisons at a glance.
2.  **Clear Hierarchy**: Information is presented with a clear visual hierarchy, often starting with key summary numbers, followed by trends, and then detailed breakdowns.
3.  **Interactive Elements**: Many examples show interactive elements like tooltips on hover, filtering options, and drill-down capabilities.
4.  **Consistent Styling**: Uses Ant Design's consistent color palette, typography, and spacing, contributing to a clean and professional look.
5.  **Contextual Information**: Data is often presented with context, such as comparisons to previous periods or targets.
6.  **Dashboard-like Layout**: The examples suggest a dashboard approach where multiple visualizations are arranged to provide a comprehensive overview.

## Key Elements and Patterns from Reference Design to Apply:

-   **Prominent KPI Cards**: Use larger, more visually distinct cards for each key KPI, potentially with a small sparkline or trend indicator directly on the card.
-   **Trend Visualizations**: Incorporate line charts or bar charts to show historical trends for each KPI, allowing users to see performance over time.
-   **Comparison to Target/Baseline**: Clearly visualize how current performance compares to baseline or target values, perhaps using progress bars or color-coded indicators.
-   **Interactive Data Tables**: While keeping the detailed table, enhance it with sorting, filtering, and potentially conditional formatting to highlight important data points.
-   **Drill-down Capability**: Allow users to click on a KPI or a data point in a chart to view more granular details in the table or a new view.
-   **Unified Dashboard View**: Arrange KPIs and relevant visualizations in a cohesive dashboard layout that guides the user's eye from high-level summaries to detailed insights.
-   **Ant Design Charts**: Leverage Ant Design's charting libraries (e.g., Ant Design Charts) for consistent and visually appealing data representations.

This analysis will form the basis for designing an improved KPI and data display.

