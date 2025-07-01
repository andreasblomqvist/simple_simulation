# Product Requirements Document: Business Planning

## 1. Introduction/Overview
The Business Planning page will replace the current Planacy system, providing a modern, web-based interface for office managers, sales, recruitment, and office owners to enter, manage, and simulate business plans. Users will be able to input monthly recruitment targets, sales forecasts, cost estimates, and staff plans for each office. The system will support real-time calculations and allow the entered data to be used as the baseline for running organizational simulations. The initial implementation will use a single JSON file to store all office plans for simplicity.

## 2. Goals
- Replace Planacy with an integrated business planning tool in the new system
- Allow users to enter and update monthly recruitment, sales, cost, and staff plans for each office
- Enable real-time calculation of outcomes (e.g., EBITDA, margin) as data is entered
- Support saving and reloading of business plan data
- Allow business plan data to be used as the baseline for running simulations
- Provide an improved, user-friendly UI compared to Planacy

## 3. User Stories
- As an office manager, I want to enter my sales forecast for each month so that I can see projected EBITDA.
- As a recruitment lead, I want to input monthly recruitment targets so I can plan for headcount growth.
- As a sales owner, I want to enter sales and cost estimates so I can track office profitability.
- As an office owner, I want to save and reload my business plan so I can update it over time.
- As a simulation user, I want to use the business plan as the baseline for running simulations.

## 4. Functional Requirements
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

## 5. Non-Goals (Out of Scope)
- Multi-user collaboration or concurrent editing
- Exporting plans to Excel or PDF
- Advanced permissions or role-based access control
- Integration with external systems (e.g., ERP, HRIS)
- Historical versioning of business plans

## 6. Design Considerations
- Use Ant Design Table/Grid components for editable fields
- Provide clear labels, tooltips, and validation for all fields
- Use color-coding and icons to indicate calculated vs. user-entered fields
- Ensure the UI is responsive and accessible (keyboard navigation, screen readers)
- Support dark mode and modern design best practices
- Consider future extensibility for more advanced planning features

## 7. Technical Considerations
- Store all business plan data in a single JSON file for all offices (initial implementation)
- Design the data structure to support easy migration to a database in the future
- Integrate with the simulation engine to use business plan data as the baseline
- Ensure performance is acceptable for multiple offices and years
- Implement clear error handling and data validation

## 8. Success Metrics
- Users can enter, save, and reload business plan data for all offices
- Calculated fields update in real time as data is entered
- Users can use the business plan as the baseline for simulations
- Positive user feedback on UI improvements over Planacy
- No critical errors or data loss during use

## 9. Open Questions
- What fields/categories should be required for each office/month (minimum set)?
- Should there be approval or locking mechanisms for finalized plans in the future?
- Are there any compliance or audit requirements for business plan data?
- Should we support comments or notes per field/month?
- How should we handle data migration if/when moving to a database? 