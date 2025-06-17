# Simplified UI Design Proposal

## Design Principles

Based on the analysis of the current UI, the simplified design will follow these principles:

1. **Visual Hierarchy:** Clear grouping of related controls with proper spacing and typography
2. **Progressive Disclosure:** Show only relevant controls based on user selections
3. **Logical Flow:** Organize controls in the order users typically interact with them
4. **Reduced Cognitive Load:** Minimize the number of visible options at any given time
5. **Ant Design Consistency:** Leverage Ant Design components for familiar interactions

## Proposed Layout Structure

### Option 1: Tabbed Interface
- **Tab 1: Simulation Levers** - All lever-related controls (Levers, Levels, Value)
- **Tab 2: Scope & Duration** - Time period, office selection, simulation duration
- **Tab 3: Global Parameters** - Price increase, salary increase, working hours, etc.

### Option 2: Collapsible Sections (Recommended)
- **Section 1: Simulation Levers** (Always expanded)
  - Dynamic form that shows relevant levels based on selected lever
  - Clear value input with immediate feedback
- **Section 2: Simulation Scope** (Collapsible)
  - Time period and office selection grouped together
  - Duration setting prominently displayed
- **Section 3: Economic Parameters** (Collapsible)
  - Price and salary increases
  - Working hours and other expenses
- **Section 4: Actions** (Always visible)
  - Single prominent "Run Simulation" button
  - Secondary actions (Load Config, Reset) as smaller buttons

### Option 3: Wizard-Style Interface
- **Step 1:** Choose simulation lever and configure values
- **Step 2:** Set scope (time period, offices)
- **Step 3:** Configure global parameters
- **Step 4:** Review and run simulation

## Key Improvements

1. **Dynamic Lever Configuration:** When a lever is selected, only show relevant levels and provide contextual help
2. **Smart Defaults:** Pre-populate common values to reduce input burden
3. **Visual Feedback:** Show immediate preview of how settings affect the simulation
4. **Simplified Actions:** Single "Run Simulation" button that applies all current settings
5. **Better Grouping:** Related controls are visually grouped using Ant Design Cards or Collapse components

## Wireframe Concepts

I'll now create visual wireframes for the recommended collapsible sections approach.

