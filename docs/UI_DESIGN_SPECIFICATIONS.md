# UI Design Specifications: Office Business Planning System

## Design Philosophy

### Core Principles
- **Office-Centric Navigation**: Each office should feel like a separate workspace
- **Data-Dense Tables**: Efficiently display and edit large amounts of monthly data
- **Journey-Based Organization**: Visual hierarchy based on office maturity
- **Progressive Disclosure**: Show complexity only when needed
- **Responsive Design**: Works effectively on tablets and desktops

### Visual Hierarchy
1. **Journey Groups** (Primary navigation)
2. **Individual Offices** (Secondary navigation)
3. **Configuration Sections** (Tertiary organization)
4. **Monthly Data** (Detail level)

## Layout Architecture

### Main Layout Structure
```
┌─────────────────────────────────────────────────────────────┐
│ Header: Global Navigation & User Controls                   │
├─────────────┬───────────────────────────────────────────────┤
│ Office      │ Office Configuration Content                  │
│ Sidebar     │                                               │
│             │ ┌─ Office Info Section                        │
│ Journey 1   │ ├─ Initial Population Table                   │
│ • Office A  │ ├─ Monthly Business Plan Table                │
│ • Office B  │ ├─ CAT Progression Configuration              │
│             │ └─ Simulation Controls                        │
│ Journey 2   │                                               │
│ • Office C  │                                               │
│ • Office D  │                                               │
│             │                                               │
│ Journey 3   │                                               │
│ • Office E  │                                               │
│             │                                               │
└─────────────┴───────────────────────────────────────────────┘
```

## Component Design Specifications

### 1. Office Sidebar

#### Visual Design
- **Width**: 280px fixed, collapsible to 60px
- **Background**: Light gray (#F8F9FA) with subtle border
- **Journey Groups**: Expandable sections with colored indicators

#### Journey Group Styling
```css
.journey-group {
  margin-bottom: 16px;
  border-radius: 8px;
  overflow: hidden;
}

.journey-header {
  padding: 12px 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.journey-emerging { background: #E3F2FD; color: #1565C0; }
.journey-established { background: #F3E5F5; color: #7B1FA2; }
.journey-mature { background: #E8F5E8; color: #2E7D32; }
```

#### Office Navigation Items
```css
.office-nav-item {
  padding: 8px 24px;
  cursor: pointer;
  transition: background-color 0.2s;
  border-left: 3px solid transparent;
}

.office-nav-item:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.office-nav-item.active {
  background-color: rgba(0, 0, 0, 0.08);
  border-left-color: var(--journey-color);
  font-weight: 500;
}
```

### 2. Business Plan Table

#### Table Structure
- **Dimensions**: 12 columns (months) × 24 rows (role/level combinations)
- **Cell Size**: 120px width × 80px height (accommodates 5 fields)
- **Scrolling**: Horizontal and vertical scroll with sticky headers
- **Virtualization**: Only render visible cells for performance

#### Cell Design
```css
.business-plan-cell {
  position: relative;
  border: 1px solid #E0E0E0;
  padding: 4px;
  min-height: 80px;
  background: white;
}

.business-plan-cell:hover {
  border-color: #2196F3;
  box-shadow: 0 0 0 1px #2196F3;
}

.business-plan-cell.editing {
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px #4CAF50;
}

.business-plan-cell.error {
  border-color: #F44336;
  background-color: #FFEBEE;
}
```

#### Field Layout within Cell
```
┌─────────────────────┐
│ Rec: [____] 🟢      │ <- Recruitment (green indicator)
│ Churn: [____] 🔴    │ <- Churn (red indicator)  
│ Price: [____] 💰    │ <- Price (currency icon)
│ UTR: [____] ⚡      │ <- Utilization rate (lightning)
│ Salary: [____] 💼  │ <- Salary (briefcase icon)
└─────────────────────┘
```

#### Table Headers
```css
.table-header-month {
  background: #F5F5F5;
  font-weight: 600;
  text-align: center;
  padding: 12px 8px;
  border-bottom: 2px solid #BDBDBD;
  position: sticky;
  top: 0;
  z-index: 10;
}

.table-header-role-level {
  background: #FAFAFA;
  font-weight: 500;
  padding: 8px 12px;
  border-right: 2px solid #BDBDBD;
  position: sticky;
  left: 0;
  z-index: 10;
  min-width: 150px;
}
```

### 3. Editable Cell Component

#### Multi-Field Editor
```css
.cell-editor {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: white;
  border: 2px solid #4CAF50;
  border-radius: 4px;
  padding: 8px;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.field-input {
  width: 100%;
  padding: 4px 8px;
  border: 1px solid #CCCCCC;
  border-radius: 3px;
  font-size: 12px;
  margin-bottom: 4px;
}

.field-input:focus {
  outline: none;
  border-color: #2196F3;
}

.field-label {
  font-size: 10px;
  font-weight: 500;
  color: #666666;
  margin-bottom: 2px;
}
```

### 4. Initial Population Table

#### Workforce Distribution Grid
```
┌─────────────┬─────────┬─────────┬─────────┬─────────┐
│ Role\Level  │    A    │   AC    │    C    │  SrC    │
├─────────────┼─────────┼─────────┼─────────┼─────────┤
│ Consultant  │ [___25] │ [___18] │ [___12] │ [____8] │
│ Sales       │ [____5] │ [____3] │ [____2] │ [____1] │  
│ Operations  │ [____2] │ [____1] │ [____1] │ [____0] │
├─────────────┼─────────┼─────────┼─────────┼─────────┤
│ TOTAL       │    32   │    22   │    15   │     9   │
└─────────────┴─────────┴─────────┴─────────┴─────────┘
```

#### Styling
```css
.population-table {
  margin: 24px 0;
  border-collapse: collapse;
  width: 100%;
}

.population-cell {
  border: 1px solid #E0E0E0;
  padding: 12px;
  text-align: center;
}

.population-input {
  width: 80px;
  padding: 8px;
  text-align: center;
  border: 1px solid #CCCCCC;
  border-radius: 4px;
}

.population-total {
  background-color: #F5F5F5;
  font-weight: 600;
}
```

### 5. CAT Progression Configuration

#### Progression Curve Interface
```css
.progression-config {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 24px;
  margin: 24px 0;
}

.progression-levels {
  background: #FAFAFA;
  padding: 16px;
  border-radius: 8px;
}

.progression-level {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #E0E0E0;
}

.progression-rate {
  width: 80px;
  padding: 4px 8px;
  text-align: right;
}

.progression-curve {
  background: white;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #E0E0E0;
}
```

### 6. Validation & Error States

#### Error Indicators
```css
.validation-error {
  border-color: #F44336 !important;
  background-color: #FFEBEE;
}

.validation-warning {
  border-color: #FF9800 !important;
  background-color: #FFF3E0;
}

.validation-success {
  border-color: #4CAF50 !important;
  background-color: #E8F5E8;
}

.error-tooltip {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #F44336;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  z-index: 200;
}
```

### 7. Responsive Design Breakpoints

#### Desktop (1200px+)
- Full sidebar visible
- Complete table with all columns
- Side-by-side configuration sections

#### Tablet (768px - 1199px)
- Collapsible sidebar
- Horizontal scroll for table
- Stacked configuration sections

#### Mobile (< 768px)
- Hidden sidebar (overlay when needed)
- Single column table view
- Accordion-style configuration

```css
@media (max-width: 768px) {
  .office-sidebar {
    position: fixed;
    left: -280px;
    transition: left 0.3s ease;
    z-index: 1000;
  }
  
  .office-sidebar.open {
    left: 0;
  }
  
  .business-plan-table {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
  }
  
  .office-config-sections {
    display: block;
  }
  
  .office-config-section {
    margin-bottom: 24px;
  }
}
```

## Interaction Design

### 1. Cell Editing Workflow
1. **Single Click**: Select cell, show field values
2. **Double Click**: Enter edit mode with focused first field
3. **Tab Navigation**: Move between fields within cell
4. **Enter**: Save changes and move to next row
5. **Escape**: Cancel changes and exit edit mode

### 2. Bulk Operations
1. **Range Selection**: Click and drag to select multiple cells
2. **Keyboard Shortcuts**: Ctrl+C, Ctrl+V for copy/paste
3. **Fill Down**: Double-click fill handle to copy to range
4. **Bulk Edit**: Right-click selected range for bulk operations

### 3. Navigation Patterns
1. **Breadcrumbs**: Office journey > Office name > Section
2. **Quick Search**: Filter offices by name or journey
3. **Recent Offices**: Show last 5 accessed offices
4. **Keyboard Navigation**: Arrow keys, Tab, Enter for table navigation

## Performance Considerations

### 1. Table Virtualization
- Render only visible cells (viewport + buffer)
- Lazy load data as user scrolls
- Debounce cell updates to avoid excessive API calls

### 2. Data Loading
- Progressive loading of office data
- Cached business plans with optimistic updates
- Background data synchronization

### 3. Memory Management
- Unload non-visible office data
- Efficient state updates with minimal re-renders
- Memoized calculations for validation

## Accessibility Guidelines

### 1. Keyboard Navigation
- Full keyboard accessibility for all interactions
- Logical tab order through form fields
- Arrow key navigation in tables

### 2. Screen Reader Support
- Proper ARIA labels for complex table structures
- Descriptive text for validation states
- Announced changes for dynamic content

### 3. Visual Accessibility
- High contrast mode support
- Scalable fonts and interface elements
- Clear focus indicators

## Animation & Transitions

### 1. Micro-Interactions
```css
.cell-transition {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-transition {
  transition: transform 0.3s ease-out;
}

.loading-animation {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}
```

### 2. Page Transitions
- Smooth transitions between offices
- Loading states for data operations
- Progressive disclosure animations

This comprehensive UI design specification provides the foundation for creating an intuitive, efficient, and visually appealing office business planning interface that scales from individual cell editing to organization-wide simulation management.