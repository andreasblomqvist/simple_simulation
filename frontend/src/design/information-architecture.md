# Information Architecture - SimpleSim Design System

## User Mental Models & Task-Oriented Organization

### **Core User Mental Model**
SimpleSim users think in terms of **business outcomes**, not technical features. The information architecture reflects this by organizing around user goals rather than system capabilities.

### **Primary User Journeys**

#### **1. Growth Planner Journey**
```
Goal: Plan organizational growth
Mental Model: "I need to model different growth scenarios"

Task Flow:
1. Review current state → Dashboard
2. Create scenario → Scenario Builder  
3. Configure parameters → Office Settings
4. Run simulation → Results Analysis
5. Compare options → Comparison View
6. Make decisions → Export/Share
```

#### **2. Business Analyst Journey**
```
Goal: Analyze workforce metrics and trends
Mental Model: "I need to understand what the data tells me"

Task Flow:
1. View KPIs → Executive Dashboard
2. Drill into details → Data Tables
3. Compare periods → Trend Analysis
4. Identify patterns → Interactive Charts
5. Generate insights → Reports
6. Share findings → Export Tools
```

#### **3. Office Manager Journey**
```
Goal: Configure and manage office operations
Mental Model: "I need to set up and maintain my office"

Task Flow:
1. Access office → Office Selection
2. Review setup → Office Overview
3. Update plans → Business Planning
4. Configure rules → Settings
5. Test changes → Simulation Preview
6. Apply changes → Save/Publish
```

### **Information Hierarchy**

#### **Level 1: Primary Navigation (Global Context)**
```typescript
interface PrimaryNavigation {
  dashboard: {
    label: "Dashboard"
    purpose: "Current state overview and quick actions"
    icon: "home"
    priority: 1
  }
  scenarios: {
    label: "Scenarios"  
    purpose: "Create, manage, and compare growth scenarios"
    icon: "trending-up"
    priority: 2
  }
  offices: {
    label: "Offices"
    purpose: "Configure and manage office operations"
    icon: "building"
    priority: 3
  }
  results: {
    label: "Results"
    purpose: "Analyze outcomes and trends"
    icon: "bar-chart"
    priority: 4
  }
}
```

#### **Level 2: Context Bar (Page Context)**
```typescript
interface ContextBar {
  breadcrumb: string         // Current location context
  primaryAction: Action      // Most important action for this context
  secondaryActions: Action[] // Supporting actions (max 3-4)
  filters?: Filter[]         // Context-specific filtering
  status?: StatusIndicator   // Current state/health
}
```

#### **Level 3: Content Organization**
Progressive disclosure based on user needs:

1. **Essential First**: Most critical information visible immediately
2. **Secondary on Demand**: Details available via expansion or navigation
3. **Advanced Hidden**: Complex features behind clear entry points

### **Content Strategy**

#### **Writing Principles**
- **Action-Oriented**: Use verbs that describe what users accomplish
- **Business Language**: Use terminology from workforce planning domain
- **Progressive Complexity**: Start simple, offer advanced options
- **Contextual Help**: Guidance appears when and where needed

#### **Content Hierarchy**
```typescript
interface ContentPriority {
  critical: {
    description: "Must be visible immediately"
    examples: ["Current headcount", "Growth targets", "Key metrics"]
    treatment: "Prominent placement, high contrast"
  }
  important: {
    description: "Needed for task completion"
    examples: ["Historical data", "Comparison metrics", "Action buttons"]
    treatment: "Clear hierarchy, accessible within 1 click"
  }
  supporting: {
    description: "Helpful but not essential"
    examples: ["Technical details", "Advanced settings", "Help text"]
    treatment: "Progressive disclosure, tooltips, help sections"
  }
}
```

#### **Labeling System**

**Consistent Terminology**:
- **Scenario** (not "simulation" or "model")
- **Office** (not "location" or "site")
- **Growth Plan** (not "forecast" or "projection")
- **Baseline** (not "current state" or "starting point")

**Action Labels**:
- **Create** → "Create New [Item]"
- **Edit** → "Edit [Specific Item Name]"
- **View** → "View Details" or "See Full Results"
- **Compare** → "Compare with Baseline" or "Compare Scenarios"
- **Export** → "Export to Excel" or "Download PDF"

### **Navigation Patterns**

#### **Hub and Spoke Model**
```
Dashboard (Hub)
├── Quick Create Scenario → Scenario Builder
├── View Recent Results → Results Detail  
├── Manage Offices → Office Configuration
└── System Status → Settings/Admin
```

Each spoke returns to the hub for different tasks, avoiding deep nesting.

#### **Context Switching**
Instead of breadcrumbs, use context switching:

```typescript
interface ContextSwitcher {
  currentContext: {
    type: 'scenario' | 'office' | 'result'
    name: string
    id: string
  }
  availableContexts: Context[]
  switchAction: (context: Context) => void
}
```

#### **Smart Routing**
URLs reflect user intent, not technical structure:

```
Good URLs (Task-Oriented):
/create-scenario/office-selection
/compare-scenarios/growth-vs-baseline
/configure-office/london/business-plan

Bad URLs (Feature-Oriented):
/scenarios/new/step/2
/comparison/scenarios/123/456
/offices/456/config/business-plans
```

### **Search and Discovery**

#### **Global Search Strategy**
```typescript
interface SearchCapabilities {
  quickSearch: {
    scope: "Recent items, favorites, key actions"
    trigger: "Cmd+K or search icon"
    results: "Instant, predictive"
  }
  contextualSearch: {
    scope: "Within current page/section"
    trigger: "Filter controls, search bars"
    results: "Filtered list views"
  }
  advancedSearch: {
    scope: "Full database with complex criteria"
    trigger: "Advanced search link"
    results: "Detailed search results page"
  }
}
```

#### **Findability Principles**
1. **Predictable Locations**: Similar items in similar places
2. **Multiple Pathways**: More than one way to reach important content
3. **Visual Scanning**: Layout supports quick visual scanning
4. **Search Integration**: Search works across all content types

### **Error Prevention and Recovery**

#### **Information Scent**
Provide clear indicators of what users will find:

```typescript
interface InformationScent {
  preview: "Show sample of what clicking will reveal"
  counts: "Indicate quantity of items (5 scenarios, 12 offices)"
  status: "Show current state (Running, Complete, Error)"
  timestamps: "Show recency (2 hours ago, Last week)"
}
```

#### **Error Prevention**
- **Validation**: Real-time feedback during data entry
- **Confirmation**: Clear confirmation for destructive actions
- **Auto-save**: Prevent loss of work
- **Clear Defaults**: Smart defaults reduce errors

#### **Error Recovery**
- **Clear Error Messages**: Explain what went wrong and how to fix
- **Undo Actions**: Allow reversal of recent actions
- **Alternative Paths**: Provide different ways to accomplish goals
- **Help Integration**: Contextual help for error resolution

### **Mobile and Responsive Considerations**

#### **Desktop-First Approach**
SimpleSim is primarily a desktop application, but responsive principles apply:

1. **Progressive Enhancement**: Core functionality works on smaller screens
2. **Touch Targets**: Minimum 44px touch targets for tablet use
3. **Readable Text**: Minimum 16px font size on all devices
4. **Simplified Navigation**: Collapse complex navigation on smaller screens

#### **Content Prioritization**
On smaller screens, show only:
1. Most critical metrics and actions
2. Current context and navigation
3. Primary content area
4. Essential controls

### **Accessibility and Inclusive Design**

#### **Cognitive Accessibility**
- **Clear Language**: Plain language, defined terms, consistent vocabulary
- **Logical Flow**: Information follows predictable patterns
- **Reduced Cognitive Load**: Don't make users remember information across screens
- **Error Prevention**: Design prevents mistakes rather than requiring correction

#### **Keyboard Navigation**
- **Logical Tab Order**: Navigation follows visual layout
- **Skip Links**: Allow skipping repetitive navigation
- **Focus Indicators**: Clear visual focus indicators
- **Shortcuts**: Keyboard shortcuts for power users

### **Content Maintenance Strategy**

#### **Content Governance**
- **Single Source of Truth**: Each piece of content has one authoritative location
- **Regular Review**: Quarterly review of content accuracy and relevance
- **User Feedback**: Mechanisms for users to report content issues
- **Version Control**: Track changes to important content

#### **Localization Readiness**
- **Text Externalization**: All user-facing text in language files
- **Cultural Considerations**: UI patterns that work across cultures
- **RTL Support**: Layout considerations for right-to-left languages
- **Number Formatting**: Locale-aware number and date formatting

---

## Implementation Guidelines

### **Content Creation Checklist**
- [ ] Content supports primary user goals
- [ ] Terminology is consistent with domain language
- [ ] Information hierarchy is clear and logical
- [ ] Content can be found through multiple pathways
- [ ] Error states and edge cases are handled
- [ ] Content works for both expert and novice users

### **Navigation Design Checklist**
- [ ] Navigation reflects user mental models, not system architecture
- [ ] Primary actions are immediately accessible
- [ ] Context is clear at all times
- [ ] Users can easily return to key areas
- [ ] Deep linking works for shareable content
- [ ] Navigation scales from few to many items

### **Testing Information Architecture**
- **Card Sorting**: Validate categorization and grouping
- **Tree Testing**: Test findability without visual design
- **First Click Testing**: Validate initial navigation choices
- **Task Analysis**: Observe users completing real tasks
- **Mental Model Interviews**: Understand user expectations and vocabulary