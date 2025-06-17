# Detailed Design Specifications

## Component Architecture

### 1. Overall Layout Structure
```
<div className="simulation-lab-container">
  <Card className="simulation-levers-card">
    // Simulation Levers Section
  </Card>
  
  <Collapse defaultActiveKey={['scope', 'economic']}>
    <Panel key="scope" header="Simulation Scope">
      // Scope controls
    </Panel>
    <Panel key="economic" header="Economic Parameters">
      // Economic parameter inputs
    </Panel>
  </Collapse>
  
  <div className="action-buttons">
    // Primary and secondary action buttons
  </div>
</div>
```

### 2. Ant Design Components Mapping

#### Simulation Levers Section
- **Container**: `Card` component with title "Simulation Levers"
- **Lever Selection**: `Select` component with options for different levers
- **Level Selection**: `Select` component (dynamic options based on lever)
- **Value Input**: `InputNumber` component with percentage formatter
- **Layout**: `Row` and `Col` components for responsive grid (8-8-8 columns)

#### Simulation Scope Section
- **Container**: `Collapse.Panel` component
- **Time Period**: `Select` component with time period options
- **Month Input**: `InputNumber` component with month validation
- **Checkboxes**: `Checkbox` components for "Apply to all months" and "Apply to all offices"
- **Office Selection**: `Select` component with multi-select capability
- **Duration**: `InputNumber` component with "months" suffix

#### Economic Parameters Section
- **Container**: `Collapse.Panel` component
- **Input Grid**: `Row` and `Col` components (6-6-6-6 columns on desktop, 12-12-12-12 on mobile)
- **Price/Salary Increase**: `InputNumber` components with percentage formatter
- **Working Hours**: `InputNumber` component with decimal support
- **Other Expense**: `InputNumber` component with currency formatting

#### Action Buttons
- **Primary Action**: `Button` component with `type="primary"` and `size="large"`
- **Secondary Actions**: `Button` components with `type="default"` and smaller size

## Interaction Flows

### 1. Lever Configuration Flow
```
1. User selects a lever from dropdown
   → Trigger: onChange event on lever Select
   → Action: Update available levels in levels dropdown
   → Effect: Clear current level and value selections

2. User selects a level
   → Trigger: onChange event on level Select
   → Action: Enable value input field
   → Effect: Show contextual help text for the selected lever/level combination

3. User enters value
   → Trigger: onChange event on value InputNumber
   → Action: Validate input range and format
   → Effect: Show real-time calculation of monthly impact
```

### 2. Scope Configuration Flow
```
1. User toggles "Apply to all months"
   → Trigger: onChange event on checkbox
   → Action: Enable/disable month input field
   → Effect: Show/hide month selection

2. User toggles "Apply to all offices"
   → Trigger: onChange event on checkbox
   → Action: Enable/disable office selection dropdown
   → Effect: Show/hide specific office selection
```

### 3. Simulation Execution Flow
```
1. User clicks "Run Simulation"
   → Trigger: onClick event on primary button
   → Action: Validate all required fields
   → Effect: Show loading state and execute simulation
   → Success: Navigate to results view
   → Error: Show validation messages inline
```

## Responsive Design Specifications

### Desktop (≥1200px)
- **Lever Section**: 3-column layout (Lever: 8 cols, Level: 8 cols, Value: 8 cols)
- **Scope Section**: 2-column layout for inputs, full-width for checkboxes
- **Economic Section**: 4-column layout for parameter inputs
- **Actions**: Right-aligned button group

### Tablet (768px - 1199px)
- **Lever Section**: 2-column layout (Lever+Level: 16 cols, Value: 8 cols)
- **Scope Section**: 2-column layout maintained
- **Economic Section**: 2-column layout (2x2 grid)
- **Actions**: Center-aligned button group

### Mobile (<768px)
- **All Sections**: Single-column layout (24 cols each)
- **Collapsible Sections**: Accordion behavior with one section open at a time
- **Actions**: Full-width primary button, stacked secondary buttons

## Styling Specifications

### Color Palette
- **Primary Blue**: #1890ff (Ant Design primary)
- **Success Green**: #52c41a
- **Warning Orange**: #faad14
- **Error Red**: #f5222d
- **Neutral Gray**: #f0f0f0 (backgrounds)
- **Text Primary**: #262626
- **Text Secondary**: #8c8c8c

### Typography
- **Headers**: 16px, font-weight: 600
- **Labels**: 14px, font-weight: 500
- **Input Text**: 14px, font-weight: 400
- **Help Text**: 12px, font-weight: 400, color: #8c8c8c

### Spacing
- **Card Padding**: 24px
- **Section Margins**: 16px bottom
- **Input Margins**: 8px bottom
- **Button Margins**: 8px right for secondary, 16px top for primary

### Animations
- **Collapse Transitions**: 0.3s ease-in-out
- **Button Hover**: 0.2s ease-in-out
- **Input Focus**: 0.2s ease-in-out
- **Loading States**: Ant Design Spin component

## Accessibility Specifications

### Keyboard Navigation
- **Tab Order**: Logical flow from top to bottom, left to right
- **Focus Indicators**: Visible focus rings on all interactive elements
- **Escape Key**: Close dropdowns and modals
- **Enter Key**: Submit forms and activate primary actions

### Screen Reader Support
- **ARIA Labels**: Descriptive labels for all form controls
- **ARIA Descriptions**: Help text associated with inputs
- **Live Regions**: Announce validation errors and success messages
- **Semantic HTML**: Proper heading hierarchy and landmark roles

### Visual Accessibility
- **Color Contrast**: WCAG AA compliance (4.5:1 ratio minimum)
- **Focus Indicators**: 2px solid outline with sufficient contrast
- **Error States**: Both color and icon indicators
- **Text Scaling**: Support up to 200% zoom without horizontal scrolling

## Implementation Notes

### State Management
```javascript
const [leverConfig, setLeverConfig] = useState({
  lever: null,
  level: null,
  value: null
});

const [scopeConfig, setScopeConfig] = useState({
  timePeriod: 'monthly',
  month: null,
  applyToAllMonths: false,
  applyToAllOffices: true,
  selectedOffices: []
});

const [economicParams, setEconomicParams] = useState({
  priceIncrease: 3.0,
  salaryIncrease: 3.0,
  workingHours: 166.4,
  otherExpense: 100000
});
```

### Validation Rules
- **Lever**: Required field
- **Level**: Required when lever is selected
- **Value**: Required, must be numeric, range 0-100 for percentages
- **Month**: Required when "Apply to all months" is false
- **Working Hours**: Must be positive number, max 744 (31 days × 24 hours)
- **Expenses**: Must be non-negative numbers

### Performance Considerations
- **Debounced Inputs**: 300ms delay for value calculations
- **Memoized Components**: Use React.memo for expensive renders
- **Lazy Loading**: Load office data only when needed
- **Optimistic Updates**: Show immediate feedback for user actions

