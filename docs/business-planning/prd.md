# Product Requirements Document: Business Planning

## 1. Introduction/Overview

The Business Planning system is a comprehensive replacement for Planacy that provides a modern, web-based interface for creating, managing, and executing business plans within SimpleSim. The system enables users to create detailed monthly recruitment targets, sales forecasts, cost estimates, and workforce plans that serve as baseline inputs for organizational simulations.

**Core Vision**: Create a version of Planacy where users can create business plans that will serve as baseline input to scenarios, including functionality for aggregated business plans that combine all offices' plans into one global baseline for scenario input.

### Current Implementation Status
- **Backend**: 70% complete with full API infrastructure, data models, and business logic
- **Frontend**: 40% complete with basic components and state management
- **Integration**: Business plans can serve as simulation baselines (existing capability)

## 2. Goals

### Primary Goals
- **Replace Planacy Integration**: Eliminate dependency on external Planacy system
- **Simulation Baseline Creation**: Enable business plans to serve as baseline input for scenarios
- **Office-Level Planning**: Support detailed monthly planning for individual offices
- **Aggregated Global Planning**: Combine multiple office plans into company-wide baselines
- **Professional UI Experience**: Match or exceed Planacy's usability and visual polish

### Technical Goals
- **Seamless Integration**: Business plan data flows directly into simulation engine
- **Real-time Calculations**: Live updates of financial metrics and KPIs as data is entered
- **Data Persistence**: Reliable storage and retrieval of business plan data
- **Performance**: Support planning for 10+ offices with 12+ months of data

## 3. User Stories

### Office Manager User Stories
- As an office manager, I want to create a detailed business plan for my office so that I can set realistic growth targets
- As an office manager, I want to enter monthly recruitment targets by role and level so that I can plan workforce growth
- As an office manager, I want to set pricing and utilization targets so that I can project revenue accurately
- As an office manager, I want to see real-time calculations of EBITDA and margin so that I can validate my plan
- As an office manager, I want to copy successful plans between months so that I can efficiently create consistent forecasts
- As an office manager, I want to use my business plan as a scenario baseline so that I can test different growth strategies

### Executive User Stories
- As an executive, I want to view business plans from all offices so that I can understand company-wide growth plans
- As an executive, I want to create aggregated business plans so that I can run company-wide strategic scenarios
- As an executive, I want to compare office plans side-by-side so that I can identify opportunities and risks
- As an executive, I want to use aggregated plans as simulation baselines so that I can model enterprise-wide scenarios

### Data Integration User Stories
- As a simulation user, I want business plan data to automatically populate scenario baselines so that scenarios reflect realistic starting points
- As a simulation user, I want to compare scenario results against business plan targets so that I can measure plan effectiveness
- As a data analyst, I want to export business plan data so that I can perform external analysis

## 4. Functional Requirements

### Core Business Planning (✅ 70% Complete)

#### Data Management
1. **Monthly Plan Creation**: Users must be able to create monthly business plans for any office
2. **Plan Entry Management**: Users must be able to enter/edit recruitment, churn, pricing, UTR, and salary data by role and level
3. **Data Persistence**: All business plan data must be saved automatically and reliably
4. **Plan Templates**: Users must be able to copy plans between months and offices
5. **Bulk Operations**: Users must be able to update multiple months/roles simultaneously

#### Financial Calculations (✅ Complete)
6. **Real-time Calculations**: System must calculate revenue, costs, EBITDA, and margin in real-time
7. **Workforce Projections**: System must project total FTE and growth rates based on recruitment/churn
8. **Cost Analysis**: System must calculate total salary costs and operational expenses
9. **Validation**: System must validate plan feasibility against workforce constraints

### User Interface Requirements (❌ 40% Complete)

#### Planacy-Style Interface
10. **Spreadsheet-Style Grid**: Implement 12-month × N-role matrix interface matching Planacy design
11. **Professional Styling**: Clean, modern interface with proper typography, spacing, and visual hierarchy
12. **Cell Editing**: Advanced in-line editing with dropdowns, validation, and keyboard navigation
13. **Summary Rows/Columns**: Display calculated totals and averages for each month and role
14. **Toolbar Features**: Year/month navigation, import/export, template operations

#### Multi-Office Management (❌ Not Implemented)
15. **Office Selector**: Dropdown/tabs for switching between offices
16. **Office Comparison**: Side-by-side view of multiple office plans
17. **Global Dashboard**: Overview of all offices with key metrics
18. **Template Sharing**: UI for copying plans between offices

### Simulation Integration (❌ Not Implemented)

#### Baseline Creation
19. **Individual Office Baselines**: Convert office business plans to simulation baseline format
20. **Aggregated Baselines**: Combine multiple office plans into single global baseline
21. **Baseline Selection**: UI for choosing business plan as scenario starting point
22. **Data Validation**: Ensure business plan data meets simulation engine requirements

#### Scenario Workflow
23. **Plan-to-Scenario Flow**: Seamless transition from business planning to scenario creation
24. **Results Comparison**: Compare scenario outcomes against business plan targets
25. **Feedback Loop**: Update business plans based on simulation insights

### Advanced Features (❌ Not Implemented)

#### Import/Export Capabilities
26. **Excel Import**: Support uploading business plans from Excel templates
27. **Excel Export**: Download business plans in Excel format for offline editing
28. **CSV Support**: Basic CSV import/export for data exchange
29. **Template Generation**: Create standardized templates for office planning

#### Analytics and Reporting
30. **Plan Analytics**: Dashboard showing plan health, growth rates, and financial projections
31. **Year-over-Year Comparison**: Compare current plans against historical data
32. **Variance Analysis**: Track actual performance against planned targets
33. **Executive Summaries**: High-level reports for leadership review

## 5. Technical Architecture

### Data Models (✅ Complete)
- **MonthlyBusinessPlan**: Core plan structure with office, year, month identification
- **MonthlyPlanEntry**: Individual role/level entries with 5-parameter data model
- **OfficeBusinessPlanSummary**: Aggregated view with calculated metrics
- **WorkforceDistribution**: Current state data for plan validation

### API Layer (✅ Complete)
- **Full REST API**: Complete CRUD operations for business plans
- **Bulk Operations**: Efficient multi-plan updates and template copying
- **Validation Engine**: Business rule enforcement and data quality checks
- **Integration Endpoints**: Simulation baseline generation and data export

### Frontend Architecture (🔄 In Progress)
- **State Management**: Zustand store with complete business plan operations
- **Component Library**: Reusable business plan UI components
- **Integration Layer**: API client with error handling and caching
- **Type Safety**: Full TypeScript definitions matching backend models

### Simulation Integration (❌ Needs Implementation)
- **Data Transformation**: Convert business plans to simulation baseline format
- **Aggregation Logic**: Combine multiple office plans into global baselines
- **Validation Pipeline**: Ensure plan data compatibility with simulation engine

## 6. Implementation Roadmap

### Phase 1: UI Polish and Completion (4 weeks)
- **Week 1-2**: Complete Planacy-style grid interface with professional styling
- **Week 3**: Implement multi-office management and navigation
- **Week 4**: Add import/export capabilities and advanced editing features

### Phase 2: Simulation Integration (3 weeks)
- **Week 1**: Implement business plan to simulation baseline conversion
- **Week 2**: Build aggregated baseline functionality for global planning
- **Week 3**: Create seamless plan-to-scenario workflow in UI

### Phase 3: Advanced Features (2 weeks)
- **Week 1**: Add analytics dashboard and reporting capabilities
- **Week 2**: Implement Excel integration and template management

### Phase 4: Testing and Polish (1 week)
- **Week 1**: Comprehensive testing, bug fixes, and performance optimization

## 7. Success Metrics

### User Experience Metrics
- **Adoption Rate**: 90% of office managers actively use business planning within 3 months
- **Time Efficiency**: 50% reduction in business plan creation time vs. Planacy
- **User Satisfaction**: 4.5/5 average rating in user feedback surveys
- **Data Quality**: <5% error rate in business plan data entry and calculations

### Technical Performance Metrics
- **System Performance**: <2 second load time for 12-month business plans
- **Data Reliability**: 99.9% uptime with zero data loss incidents
- **Integration Success**: 100% of business plans successfully convert to simulation baselines
- **Calculation Accuracy**: 100% accuracy in financial calculations and projections

### Business Impact Metrics
- **Planning Efficiency**: 25% improvement in planning cycle time
- **Scenario Quality**: Business plan baselines improve scenario realism by 40%
- **Decision Quality**: 30% improvement in strategic decision confidence scores

## 8. Implementation Notes

### Key Technical Considerations
- **Leverage Existing Backend**: 70% of required API functionality already implemented
- **Component Reuse**: Extend existing business plan components rather than rebuilding
- **Performance Optimization**: Implement virtualization for large datasets
- **Mobile Responsiveness**: Ensure business planning works on tablets and mobile devices

### Integration Requirements
- **Simulation Engine**: Business plan data must match expected baseline input format
- **Office Configuration**: Plans must integrate with existing office setup and role definitions
- **User Authentication**: Respect existing user roles and permissions system

### Data Migration Strategy
- **Planacy Export**: Support importing existing Planacy data for transition
- **Backup Strategy**: Implement robust backup and recovery for business plan data
- **Version Control**: Track changes to business plans for audit and rollback capabilities

## 9. Out of Scope

### Excluded Features
- **Multi-user Collaborative Editing**: Real-time collaboration on same plan
- **Advanced Approval Workflows**: Complex approval chains with delegation
- **External System Integration**: Direct integration with ERP, HRIS, or financial systems
- **Advanced Analytics**: Machine learning predictions and trend analysis
- **Mobile App**: Native mobile application (responsive web interface only)

### Future Considerations
- **Advanced Forecasting**: AI-powered recruitment and revenue predictions
- **Resource Planning**: Integration with project and resource management
- **Financial Integration**: Direct connection to accounting systems
- **Advanced Reporting**: Custom report builder and dashboard creation

## 10. Appendix

### Current Implementation Status
The business planning system has a solid foundation with comprehensive backend API, data models, and basic frontend components. The primary work required is UI enhancement, simulation integration, and feature completion to achieve Planacy replacement goals.

### Referenced Systems
- **Planacy Screenshots**: UI design reference for professional interface standards
- **SimpleSim Simulation Engine**: Target integration for baseline data consumption
- **Office Configuration System**: Source of role definitions and organizational structure

This PRD reflects both the current implementation state and the vision for a complete Planacy replacement that seamlessly integrates with SimpleSim's scenario planning capabilities.