# Product Requirements Document: Business Planning

## 1. Introduction/Overview
The Business Planning page will replace the current Planacy system, providing a modern, web-based interface for office managers, sales, recruitment, and office owners to enter, manage, and simulate business plans. Users will be able to input monthly recruitment targets, sales forecasts, cost estimates, and staff plans for each office. The system will support real-time calculations and allow the entered data to be used as the baseline for running organizational simulations. The initial implementation will use a single JSON file to store all office plans for simplicity.

**NEW**: The system will support two distinct user personas - Office Owners who create detailed business plans for their offices, and Executives who review plans and create company-wide strategic scenarios. This includes an approval workflow and enhanced collaboration features.

## 2. Goals
- Replace Planacy with an integrated business planning tool in the new system
- Allow users to enter and update monthly recruitment, sales, cost, and staff plans for each office
- Enable real-time calculation of outcomes (e.g., EBITDA, margin) as data is entered
- Support saving and reloading of business plan data
- Allow business plan data to be used as the baseline for running simulations
- Provide an improved, user-friendly UI compared to Planacy
- **NEW**: Support Office Owner and Executive user personas with role-specific interfaces
- **NEW**: Implement approval workflow for business plan review and approval
- **NEW**: Enable Executive scenarios for company-wide strategic planning

## 3. User Stories

### Office Owner User Stories
- As an office manager, I want to enter my sales forecast for each month so that I can see projected EBITDA.
- As a recruitment lead, I want to input monthly recruitment targets so I can plan for headcount growth.
- As a sales owner, I want to enter sales and cost estimates so I can track office profitability.
- As an office owner, I want to save and reload my business plan so I can update it over time.
- As an office owner, I want to submit my business plan for executive approval so that I can get feedback and approval.
- As an office owner, I want to see the current state of my office and set realistic targets so that I can create achievable plans.

### Executive User Stories
- **NEW**: As an executive, I want to review business plans from all offices so that I can approve or provide feedback.
- **NEW**: As an executive, I want to see a company-wide overview of all offices so that I can understand the overall business state.
- **NEW**: As an executive, I want to create strategic scenarios that apply to all offices so that I can plan company-wide initiatives.
- **NEW**: As an executive, I want to compare different strategic scenarios so that I can make informed decisions.
- **NEW**: As an executive, I want to monitor the execution of approved plans so that I can ensure we're on track.

### Simulation User Stories
- As a simulation user, I want to use the business plan as the baseline for running simulations.

## 4. Functional Requirements

### Core Business Planning Requirements
1. The system must provide a dedicated "Business Planning" page accessible from the main navigation.
2. The page must display a table/grid for each office, with editable fields for each month and category (recruitment, sales, cost, staff, etc.).
3. The system must allow users to enter and edit data for each field and month.
4. The system must perform real-time calculations and update outcome fields (e.g., EBITDA, margin) as data is entered.
5. The system must allow users to save and reload business plan data (initially to/from a single JSON file).
6. The system must allow switching between offices to view/edit their plans.
7. The system must provide clear feedback when data is saved or errors occur.
8. The system must allow the current business plan to be set as the simulation baseline.
9. The UI must be user-friendly, responsive, and improve upon the Planacy experience (e.g., better navigation, tooltips, validation, accessibility).
10. The system must handle missing or incomplete data gracefully (e.g., show warnings, prevent simulation if required fields are missing).

### NEW: User Persona and Permission Requirements
11. **NEW**: The system must support different interfaces for Office Owners and Executives based on user roles.
12. **NEW**: Office Owners must be able to view and edit only their assigned office(s).
13. **NEW**: Executives must be able to view all offices and business plans.
14. **NEW**: The system must implement role-based access control for all business planning features.

### NEW: Business Plan Approval Workflow
15. **NEW**: Office Owners must be able to submit business plans for executive approval.
16. **NEW**: Executives must be able to review, approve, reject, or request changes to business plans.
17. **NEW**: The system must notify users when plans are submitted, approved, or rejected.
18. **NEW**: The system must track the approval status and history of each business plan.

### NEW: Executive Scenario Planning
19. **NEW**: Executives must be able to create company-wide strategic scenarios with global adjustments.
20. **NEW**: The system must allow executives to apply office-specific adjustments within scenarios.
21. **NEW**: The system must support scenario comparison and recommendation features.
22. **NEW**: The system must provide aggregated views of all offices for executive decision-making.

### NEW: Simplified User Experience
23. **NEW**: The system must present a clear "Current State" vs "Target State" model for business planning.
24. **NEW**: The system must provide intuitive sliders and controls for scenario adjustments.
25. **NEW**: The system must offer immediate visual feedback for all user actions.

## 5. Non-Goals (Out of Scope)
- Multi-user collaboration or concurrent editing
- Exporting plans to Excel or PDF
- Advanced permissions or role-based access control (beyond basic Office Owner/Executive roles)
- Integration with external systems (e.g., ERP, HRIS)
- Historical versioning of business plans
- **UPDATED**: Multi-user collaboration is now in scope for the approval workflow
- **UPDATED**: Basic role-based access control is now in scope

## 6. Design Considerations
- Use Ant Design Table/Grid components for editable fields
- Provide clear labels, tooltips, and validation for all fields
- Use color-coding and icons to indicate calculated vs. user-entered fields
- Ensure the UI is responsive and accessible (keyboard navigation, screen readers)
- Support dark mode and modern design best practices
- Consider future extensibility for more advanced planning features
- **NEW**: Design separate interfaces for Office Owners and Executives
- **NEW**: Implement clear approval workflow UI with status indicators
- **NEW**: Create intuitive scenario adjustment controls with immediate feedback

## 7. Technical Considerations
- Store all business plan data in a single JSON file for all offices (initial implementation)
- Design the data structure to support easy migration to a database in the future
- Integrate with the simulation engine to use business plan data as the baseline
- Ensure performance is acceptable for multiple offices and years
- Implement clear error handling and data validation
- **NEW**: Implement user authentication and role-based permissions
- **NEW**: Design data structures to support approval workflow and scenario planning
- **NEW**: Plan for database migration to support multi-user features

## 8. Success Metrics
- Users can enter, save, and reload business plan data for all offices
- Calculated fields update in real time as data is entered
- Users can use the business plan as the baseline for simulations
- Positive user feedback on UI improvements over Planacy
- No critical errors or data loss during use
- **NEW**: Office Owners can successfully submit plans for approval
- **NEW**: Executives can efficiently review and approve multiple plans
- **NEW**: Executive scenarios provide valuable insights for strategic planning
- **NEW**: Approval workflow reduces plan review time by 50%

## 9. Open Questions
- What fields/categories should be required for each office/month (minimum set)?
- Should there be approval or locking mechanisms for finalized plans in the future?
- Are there any compliance or audit requirements for business plan data?
- Should we support comments or notes per field/month?
- How should we handle data migration if/when moving to a database?
- **NEW**: What specific permissions should Office Owners vs Executives have?
- **NEW**: How should the approval workflow handle partial approvals or conditional approvals?
- **NEW**: What level of detail should Executive scenarios provide vs Office Owner plans?
- **NEW**: How should we handle conflicts between approved plans and executive scenarios? 