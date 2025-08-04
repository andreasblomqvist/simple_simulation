# SimpleSim UI Design System

## Current UI Problems Identified

### **Bloat Issues**
- Duplicate page headers (breadcrumbs + page titles + section titles)
- Multiple navigation systems (sidebar + tabs + action buttons)
- Redundant action buttons (multiple "Edit", "View", "Configure" buttons)
- Excessive white space and padding
- Too many nested containers and cards

### **Inconsistency Issues**
- Inconsistent button styles and placement
- Mixed typography hierarchy
- Inconsistent spacing and layout patterns
- Different data table implementations
- Varying modal and dialog patterns

## Design Principles

### **1. Progressive Disclosure**
- Show only what's immediately needed
- Layer complexity behind clear entry points
- Use contextual actions instead of always-visible options

### **2. Single Source of Truth**
- One primary action per screen
- Single navigation system
- Unified header/title system
- Consistent data patterns

### **3. Context Over Navigation**
- Actions follow user intent, not feature structure
- Contextual toolbars instead of scattered buttons
- Smart defaults based on user role/task

## Layout System

### **Application Shell**
```
┌─────────────────────────────────────────────────────┐
│ App Header: Logo + Context + User Menu              │
├─────────────────────────────────────────────────────┤
│ Contextual Toolbar: Actions + Filters + Status     │
├─────────────────────────────────────────────────────┤
│                                                     │
│ Main Content Area                                   │
│ (No duplicate headers or excessive nesting)         │
│                                                     │
├─────────────────────────────────────────────────────┤
│ Footer: Status + Help + Quick Actions              │
└─────────────────────────────────────────────────────┘
```

### **No More:**
- Sidebar navigation (except for complex configuration)
- Breadcrumbs (use context switching instead)
- Nested card headers
- Multiple "Back" buttons

### **Instead:**
- Context-aware top navigation
- Inline editing where possible
- Progressive disclosure for complex features
- Smart routing that maintains context

## Component Hierarchy

### **Level 1: Page Templates**
```typescript
// Single template with variants
interface PageTemplate {
  type: 'dashboard' | 'list' | 'detail' | 'editor'
  title: string
  primaryAction?: Action
  secondaryActions?: Action[]
  filters?: Filter[]
  content: ReactNode
}
```

### **Level 2: Content Blocks**
```typescript
// Reusable content patterns
interface ContentBlock {
  type: 'stats' | 'table' | 'form' | 'chart' | 'summary'
  title?: string
  data: any
  actions?: Action[]
  variant?: 'compact' | 'standard' | 'detailed'
}
```

### **Level 3: UI Components**
- Single button component with clear variants
- Single table component with consistent behavior
- Single form component with validation patterns
- Single modal/dialog component

## Navigation Redesign

### **Current Problems:**
- Sidebar → Page Header → Tab Navigation → Card Headers
- Multiple "Configure" / "View" / "Edit" buttons
- Unclear hierarchy and relationships

### **New System:**

#### **Top Navigation Bar**
```
[SimpleSim Logo] [Scenarios] [Offices] [Reports] [Settings] ... [User Menu]
```

#### **Contextual Action Bar**
```
[Current Context] | [Primary Action] [Secondary Actions...] [Filters] [Status]
```

#### **Content Area**
- Single focused content block
- No nested headers
- Actions contextual to content

### **Example: Scenario Management**
```
Top Nav: Scenarios (active)
Action Bar: "Growth Scenarios Q1 2024" | [Create Scenario] [Compare] [Export] [Filter: All]
Content: Scenario cards with inline actions
```

## Standardized Components

### **1. Action System**
```typescript
interface Action {
  id: string
  label: string
  variant: 'primary' | 'secondary' | 'ghost' | 'destructive'
  icon?: IconName
  shortcut?: string
  disabled?: boolean
  loading?: boolean
}

// Usage: Only one primary action per context
// Secondary actions grouped logically
// Destructive actions require confirmation
```

### **2. Data Display System**
```typescript
interface DataDisplay {
  type: 'table' | 'cards' | 'stats' | 'chart'
  data: any[]
  columns?: Column[]
  actions?: RowAction[]
  selection?: 'none' | 'single' | 'multiple'
  density?: 'compact' | 'comfortable' | 'spacious'
}
```

### **3. Form System**
```typescript
interface FormField {
  type: 'text' | 'number' | 'select' | 'checkbox' | 'textarea'
  label: string
  required?: boolean
  validation?: ValidationRule[]
  help?: string
  inline?: boolean
}
```

## Page Templates

### **Dashboard Template**
- Hero stats section
- Quick actions section
- Recent activity section
- No navigation redundancy

### **List Template**
- Search/filter bar
- Data display (table/cards)
- Bulk actions when applicable
- Pagination if needed

### **Detail Template**
- Object header with key info
- Tabbed sections for related data
- Contextual actions in header
- No nested navigation

### **Editor Template**
- Form sections with clear hierarchy
- Save/cancel actions
- Validation feedback
- Auto-save where possible

## Specific UI Fixes Needed

### **1. Office Management**
**Current:** Multiple nested views with duplicate headers
**New:** Single office page with contextual sections

### **2. Scenario Creation**
**Current:** Complex multi-step flow with many buttons
**New:** Guided flow with progressive disclosure

### **3. Business Planning**
**Current:** Complex grid buried in tabs
**New:** Dedicated planning workspace with smart defaults

### **4. Results Viewing**
**Current:** Scattered across multiple pages
**New:** Unified results dashboard with drill-down

## Implementation Strategy

### **Phase 1: Design Tokens**
```typescript
// colors, typography, spacing, shadows
const designTokens = {
  colors: {
    primary: { 50: '...', 500: '...', 900: '...' },
    semantic: { success: '...', warning: '...', error: '...' }
  },
  typography: {
    display: { size: '...', weight: '...', lineHeight: '...' },
    body: { size: '...', weight: '...', lineHeight: '...' }
  },
  spacing: { xs: '4px', sm: '8px', md: '16px', lg: '24px', xl: '32px' },
  radius: { sm: '4px', md: '8px', lg: '12px' },
  shadows: { sm: '...', md: '...', lg: '...' }
}
```

### **Phase 2: Component Library**
```typescript
// Standardized components with consistent APIs
export { Button, Table, Form, Modal, Card, Stats, Chart }
```

### **Phase 3: Page Templates**
```typescript
// Reusable page layouts
export { DashboardPage, ListPage, DetailPage, EditorPage }
```

### **Phase 4: Application Shell**
```typescript
// Single app layout with context switching
export { AppShell, Navigation, ActionBar, Content }
```

## Success Metrics

### **Reduction Targets:**
- 50% fewer navigation elements
- 40% fewer duplicate buttons/actions
- 60% fewer nested headers
- 30% reduction in clicks to complete tasks

### **Consistency Targets:**
- Single button component used everywhere
- Single table component used everywhere
- Consistent spacing throughout
- Unified action patterns

### **User Experience Targets:**
- Clear primary action on every screen
- Maximum 3 clicks to reach any feature
- Consistent interaction patterns
- Context-aware interfaces

This design system should eliminate the UI bloat while creating a more cohesive, efficient user experience.