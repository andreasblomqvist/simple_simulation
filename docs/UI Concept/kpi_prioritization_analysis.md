# KPI Prioritization and Data Support Analysis

## How KPIs are Prioritized in the New Design

### 1. Visual Hierarchy
- **Primary Position**: KPI cards occupy the top section of the dashboard, immediately visible without scrolling
- **Large Typography**: KPI values use significantly larger font sizes (24-32px) compared to supporting text (12-14px)
- **Color Emphasis**: KPI values use primary brand colors (blue #1890ff) while supporting data uses neutral grays
- **Card Elevation**: KPI cards have subtle shadows and white backgrounds to create visual separation from other content

### 2. Information Density
- **Focused Content**: Each KPI card contains only essential information: current value, trend indicator, and mini-chart
- **Reduced Clutter**: Removed excessive decimal places and unnecessary labels to focus on the key number
- **Progressive Disclosure**: Detailed breakdowns are available on-demand rather than always visible

### 3. Interactive Priority
- **Click Targets**: KPI cards are large, clickable areas that lead to detailed analysis
- **Hover States**: Enhanced hover effects draw attention to KPIs as interactive elements
- **Quick Actions**: Primary actions (like drilling down) are associated with KPI cards

## How Data Results Support KPIs Effectively

### 1. Contextual Relationship
- **Linked Interactions**: Clicking a KPI card filters the data table to show relevant supporting data
- **Visual Connections**: Charts and tables use consistent color coding that matches KPI trend indicators
- **Breadcrumb Navigation**: Clear path showing how detailed data relates back to specific KPIs

### 2. Meaningful Aggregation
- **Summary Metrics**: Data table includes summary rows that roll up to KPI values
- **Conditional Formatting**: Table cells are color-coded to highlight values that significantly impact KPIs
- **Trend Indicators**: Individual data rows show mini-trends that contribute to overall KPI trends

### 3. Drill-Down Capability
- **Office Breakdown**: Users can see how each office contributes to overall KPI performance
- **Time Series**: Historical data shows how current KPI values compare to past performance
- **Role Analysis**: Detailed breakdown by role/level shows which segments drive KPI changes

## Specific KPI-Data Relationships

### Net Sales KPI → Supporting Data
- **Primary Value**: Total sales across all offices and time periods
- **Supporting Table**: Sales by office, role, and time period
- **Trend Chart**: Monthly sales progression showing seasonality and growth
- **Drill-Down**: Click to see which offices/roles contribute most to sales growth

### EBITDA KPI → Supporting Data
- **Primary Value**: Current EBITDA margin and absolute value
- **Supporting Table**: Revenue and cost breakdown by office
- **Trend Chart**: EBITDA margin over time with cost structure analysis
- **Drill-Down**: Expense categories and their impact on profitability

### Growth Metrics → Supporting Data
- **Primary Values**: Total growth, consultant growth, headcount changes
- **Supporting Table**: Hiring, departures, and net growth by office and role
- **Trend Chart**: Growth trajectory with hiring pipeline indicators
- **Drill-Down**: Individual office growth rates and capacity utilization

## Design Elements That Reinforce KPI Priority

### 1. Layout Structure
```
[KPI Cards - Always Visible, Top Priority]
[Interactive Charts - Secondary, Support KPIs]
[Data Tables - Tertiary, Detailed Support]
```

### 2. Visual Weight Distribution
- **60% of visual attention** goes to KPI cards through size, color, and positioning
- **25% of visual attention** goes to trend charts that explain KPI movements
- **15% of visual attention** goes to detailed data tables for deep analysis

### 3. Interaction Flow
1. **User sees KPIs first** - immediate understanding of performance
2. **User explores trends** - understands why KPIs are at current levels
3. **User drills into data** - finds specific areas for action or investigation

## Benefits of This Approach

### For Executive Users
- **Quick Overview**: Can assess overall performance in seconds
- **Exception Management**: Problematic KPIs are immediately visible through color coding
- **Strategic Focus**: Attention is directed to metrics that matter most for business decisions

### For Analytical Users
- **Guided Analysis**: KPIs provide starting points for deeper investigation
- **Contextual Data**: Supporting data is always relevant to the KPI being explored
- **Efficient Workflow**: Can quickly move from high-level insights to detailed analysis

### For All Users
- **Reduced Cognitive Load**: Clear hierarchy eliminates confusion about what's important
- **Faster Decision Making**: Key insights are immediately apparent
- **Scalable Detail**: Can access as much or as little detail as needed for the task at hand

This design ensures that KPIs remain the primary focus while making supporting data easily accessible and meaningful for users who need deeper analysis.

