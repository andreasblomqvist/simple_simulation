# Product Requirements Document: Scenario Runner

## Introduction/Overview

The Scenario Runner is a simplified, executive-friendly interface for creating and running different organizational growth scenarios. It allows executives to quickly model different strategies by adjusting key levers (recruitment, churn, progression) and compare results to make informed decisions about growth strategy.

**Problem:** Executives need a simple way to explore different organizational growth scenarios without getting lost in technical details or complex interfaces.

**Goal:** Provide an intuitive, high-level interface for scenario planning that focuses on key business metrics and strategic decisions.

## Goals

1. **Simplify Scenario Creation:** Enable executives to create and run scenarios in under 2 minutes
2. **Focus on Key Metrics:** Prioritize EBITDA, growth, and journey distribution as primary outputs
3. **Enable Comparison:** Allow easy comparison between different scenarios
4. **Preserve Flexibility:** Maintain option for granular control while providing simple defaults
5. **Support Decision Making:** Provide clear insights for growth strategy decisions

## User Stories

1. **As an executive**, I want to create different growth scenarios so that I can compare strategies and make informed decisions about organizational growth.

2. **As an executive**, I want to save scenario results so that I can reference them later and share with stakeholders.

3. **As an executive**, I want to adjust recruitment/churn/progression levers so that I can model different organizational changes and their impact on EBITDA.

4. **As an executive**, I want to see clear comparisons between scenarios so that I can understand the trade-offs between different strategies.

5. **As an executive**, I want to focus on all offices and yearly results so that I can get a high-level view of organizational performance.

## Functional Requirements

1. **Scenario Creation Interface**
   - The system must provide a simple form for creating new scenarios
   - The system must allow users to set a scenario name and description
   - The system must allow users to select time range (years, not months)
   - The system must allow users to select scope (All Offices by default, with option for individual offices)

2. **Lever Controls**
   - The system must provide level-specific controls for recruitment rates
   - The system must provide level-specific controls for churn rates  
   - The system must provide level-specific controls for progression rates (defaulting to 1.0)
   - The system must provide bulk edit options for quick adjustments
   - The system must validate lever values to prevent unrealistic scenarios

3. **Scenario Execution**
   - The system must run scenarios using the existing simulation engine
   - The system must display progress indicators during scenario execution
   - The system must handle errors gracefully and provide clear error messages
   - The system must not modify the existing simulation engine unless explicitly requested

4. **Results Display**
   - The system must display journey distribution results prominently
   - The system must display growth metrics clearly
   - The system must display EBITDA as the primary financial metric
   - The system must provide visual comparisons between scenarios
   - The system must allow export of results

5. **Scenario Management**
   - The system must allow users to save scenarios (inputs and results)
   - The system must provide a scenario history/list view
   - The system must allow users to load and modify existing scenarios
   - The system must allow users to delete scenarios
   - The system must allow users to compare multiple scenarios side-by-side

6. **User Experience**
   - The system must provide a clean, executive-friendly interface
   - The system must use clear, non-technical language
   - The system must provide helpful tooltips and guidance
   - The system must maintain consistency with existing UI patterns

## Non-Goals (Out of Scope)

1. **Replacement of Existing Interface:** This feature will not replace the existing detailed simulation interface
2. **Technical Complexity:** Users should not need technical knowledge to use this feature
3. **Advanced Financial Modeling:** The feature will not include complex financial modeling beyond the current system capabilities
4. **Automatic Changes:** The system will not automatically modify the simulation engine without user approval
5. **Real-time Collaboration:** The feature will not include real-time collaboration or sharing capabilities
6. **Advanced Analytics:** The feature will not include complex statistical analysis or predictive modeling

## Design Considerations

### Wireframe Structure (from our conversation):
```
┌─────────────────────────────────────────────────────────────┐
│ Scenario Runner                                             │
├─────────────────────────────────────────────────────────────┤
│ [Scenario List] [Scenario Editor] [Results] [History]      │
├─────────────────────────────────────────────────────────────┤
│ Scenario Editor:                                            │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│ │ Basic Settings  │ │ Level Levers    │ │ Bulk Edit       │ │
│ │ • Name          │ │ • Recruitment   │ │ • Apply to All  │ │
│ │ • Description   │ │ • Churn         │ │ • Reset to 1.0  │ │
│ │ • Time Range    │ │ • Progression   │ │ • Copy from...  │ │
│ │ • Office Scope  │ │ (per level)     │ │                 │ │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘ │
│                                                             │
│ [Run Scenario] [Save Scenario] [Cancel]                    │
└─────────────────────────────────────────────────────────────┘
```

### Key UI Principles:
- Clean, executive-friendly interface
- Focus on EBITDA as primary metric
- Clear visual hierarchy
- Consistent with existing design patterns
- Responsive design for different screen sizes

## Technical Considerations

1. **Backend Integration:** 
   - Use existing simulation engine without modification unless required
   - Create new API endpoints for scenario management
   - Maintain separation between scenario data and core simulation logic

2. **Data Storage:**
   - Store scenario definitions and results in JSON format
   - Implement versioning for scenario data
   - Ensure data persistence across sessions

3. **Performance:**
   - Optimize scenario execution for reasonable response times
   - Implement caching for frequently accessed scenarios
   - Handle large result sets efficiently

4. **Error Handling:**
   - Provide clear error messages for invalid inputs
   - Handle simulation engine failures gracefully
   - Implement validation for all user inputs

## Success Metrics

1. **User Adoption:** Number of scenarios created and run by executives
2. **Time to Value:** Time from scenario creation to actionable insights
3. **User Satisfaction:** Feedback on ease of use and usefulness of results
4. **Decision Impact:** Evidence that scenario results influenced strategic decisions
5. **System Performance:** Scenario execution time and system reliability

## Open Questions

1. **Data Retention:** How long should scenario data be retained?
2. **Access Control:** Should scenarios be shared across users or kept private?
3. **Export Formats:** What formats should be supported for scenario results export?
4. **Advanced Features:** What additional features might be needed in future iterations?
5. **Integration:** How should this integrate with other planning or reporting tools? 