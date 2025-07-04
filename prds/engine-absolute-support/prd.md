# Product Requirements Document: Engine Support for Absolute and Percentage-Based Recruitment/Churn

## 1. Introduction/Overview
This enhancement will update the simulation engine to support both absolute numbers and percentage-based values for recruitment and churn at the office/role/level/month granularity. The goal is to provide maximum flexibility for business planning and simulation, allowing users to specify exact numbers where needed and fallback to percentages elsewhere. This will enable seamless integration with business planning tools that operate with actual numbers, while maintaining backward compatibility with existing percentage-based configurations.

## 2. Goals
- Allow the simulation engine to accept both absolute and percentage-based values for recruitment and churn
- Enable per-field, per-period, per-role/level specification (mix and match as needed)
- Ensure clear precedence: absolute values override percentages if both are present
- Maintain backward compatibility with existing configs
- Provide clear reporting/logging of which method was used for each value

## 3. User Stories
- As a planner, I want to specify exact recruitment and churn numbers for some roles/months, and use percentages for others, so I can match my business plan
- As a simulation user, I want the engine to use my absolute numbers if present, and fallback to percentages if not
- As a data analyst, I want to see in the simulation output which method was used for each value, for auditability
- As a developer, I want the engine to remain compatible with existing percentage-based configs

## 4. Functional Requirements
1. The engine must accept both `recruitment` (absolute) and `recruitment_pct` (percentage) fields for each office/role/level/month
2. The engine must accept both `churn` (absolute) and `churn_pct` (percentage) fields for each office/role/level/month
3. If both absolute and percentage values are present for a field, the engine must use the absolute value
4. If only the percentage is present, the engine must calculate the value as `percentage * fte`
5. If neither is present, the engine must treat the value as zero (and optionally log a warning)
6. The engine must log or output which method was used for each value in each period (for auditability)
7. The engine must maintain backward compatibility with existing configs that only use percentages
8. The engine must support this logic for all relevant simulation steps (recruitment, churn, etc.)
9. The engine must validate input and warn if both fields are missing for a required value
10. The engine must be extensible for future fields (e.g., promotions, transfers)

## 5. Non-Goals (Out of Scope)
- UI changes for entering both values (handled in business planning PRD)
- Support for other fields (e.g., salary, price) in this enhancement
- Multi-user or real-time collaboration
- Data migration for historical runs

## 6. Design Considerations
- Data model should allow both fields per period, per role/level
- Engine logic should be clear and easy to maintain
- Logging should be detailed enough for audit but not overly verbose
- Consider future extensibility for other absolute/percentage fields

## 7. Technical Considerations
- Update data parsing and simulation logic to check for both fields
- Ensure all relevant simulation steps (recruitment, churn) use the new logic
- Add logging/reporting for method used per value
- Add validation and error handling for missing fields
- Maintain backward compatibility with existing configs and tests

## 8. Success Metrics
- Users can mix and match absolute and percentage values in the same simulation
- Engine always uses the correct value according to precedence rules
- Simulation output/logs clearly indicate which method was used
- No regressions or errors in existing percentage-based simulations
- Positive feedback from planners and analysts

## 9. Open Questions
- Should the engine warn or error if both fields are missing for a required value?
- Should the engine support specifying both values in the UI, or just one per field?
- Are there any edge cases where fallback logic should be different?
- Should this logic be extended to other fields in the future (e.g., promotions, transfers)? 