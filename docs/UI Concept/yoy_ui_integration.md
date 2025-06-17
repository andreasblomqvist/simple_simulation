# Year-over-Year Navigation UI Integration

## UI Placement Options for Year Selector

### Option 1: Header Navigation (Recommended)
- **Location**: Top of the dashboard, integrated with the main navigation
- **Design**: Horizontal tab-style selector or dropdown showing available years
- **Benefits**: Always visible, doesn't interfere with existing content, follows common navigation patterns
- **Implementation**: Ant Design `Tabs` or `Select` component in the header area

### Option 2: Floating Control Panel
- **Location**: Fixed position overlay (top-right or bottom-right corner)
- **Design**: Compact year selector with previous/next navigation arrows
- **Benefits**: Doesn't take up permanent screen space, can be minimized when not needed
- **Implementation**: Ant Design `FloatButton` with `Select` dropdown

### Option 3: Integrated with KPI Section
- **Location**: Above or within the KPI card grid
- **Design**: Year selector with prominent year-over-year change indicators
- **Benefits**: Directly connected to the data it affects, contextually relevant
- **Implementation**: Custom component combining `Select` with trend indicators

### Option 4: Sidebar Navigation
- **Location**: Left or right sidebar with year timeline
- **Design**: Vertical timeline showing all simulation years
- **Benefits**: Visual representation of progression, easy to see current position
- **Implementation**: Custom timeline component with Ant Design styling

## Enhanced KPI Cards with Year-over-Year Changes

### Updated KPI Card Structure
The existing KPI cards will be enhanced to show:
1. **Current Year Value**: Large, prominent display (unchanged)
2. **Year-over-Year Change**: New indicator showing change from previous year
3. **Trend Direction**: Visual arrow indicating positive/negative change
4. **Percentage Change**: Numerical representation of year-over-year change
5. **Multi-year Sparkline**: Extended to show progression across all years

### Visual Indicators for Year-over-Year Changes
- **Positive Changes**: Green color (#52c41a), upward arrow (↗)
- **Negative Changes**: Red color (#f5222d), downward arrow (↘)
- **No Change**: Gray color (#8c8c8c), horizontal arrow (→)
- **Significant Changes**: Bold styling for changes above certain thresholds

## Updated Chart Visualizations

### Enhanced Trend Charts
- **Multi-year Timeline**: X-axis now spans multiple years instead of months
- **Year Markers**: Clear demarcation of year boundaries
- **Current Year Highlight**: Visual emphasis on the currently selected year
- **Comparison Lines**: Optional overlay showing target progression

### New Year-over-Year Comparison Charts
- **Year-over-Year Bar Chart**: Comparing key metrics across consecutive years
- **Progression Waterfall Chart**: Showing how metrics build up or decline year by year
- **Target vs Actual**: Comparing planned progression with actual simulation results

## Data Table Enhancements

### Year-Specific Data Display
- **Year Filter Integration**: Table automatically filters to show data for selected year
- **Year-over-Year Columns**: Additional columns showing changes from previous year
- **Expandable Year Comparison**: Ability to expand rows to see multi-year progression
- **Export by Year**: Enhanced export functionality for year-specific data

### Progressive Disclosure
- **Summary View**: Default view shows current year data
- **Comparison View**: Toggle to show year-over-year changes
- **Historical View**: Full multi-year data table for detailed analysis

## Navigation Flow and User Experience

### Primary Navigation Flow
1. **Default View**: Dashboard loads showing the final year of simulation
2. **Year Selection**: User selects different year from header navigation
3. **Data Update**: All KPIs, charts, and tables update to reflect selected year
4. **Comparison Mode**: Optional toggle to show year-over-year changes
5. **Export**: Year-specific data export functionality

### Secondary Navigation Features
- **Previous/Next Buttons**: Quick navigation between consecutive years
- **Year Overview**: Modal or sidebar showing summary of all years
- **Bookmark Years**: Ability to mark important years for quick access
- **Animation Transitions**: Smooth transitions when switching between years

## Mobile and Responsive Considerations

### Mobile-First Year Navigation
- **Swipe Navigation**: Horizontal swipe to navigate between years
- **Compact Year Selector**: Dropdown or bottom sheet for year selection
- **Simplified KPI Display**: Prioritize most important year-over-year changes
- **Collapsible Sections**: Year comparison data in expandable sections

### Tablet Optimization
- **Split View**: Side-by-side comparison of different years
- **Touch-Friendly Controls**: Larger touch targets for year navigation
- **Gesture Support**: Pinch-to-zoom for detailed chart analysis

This integration approach ensures that year-over-year navigation enhances the existing UI without disrupting the established user experience while providing the functionality required by the PRD.

