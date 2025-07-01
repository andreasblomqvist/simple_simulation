## Relevant Files

- `backend/src/services/simulation_engine.py` - Main simulation engine logic to update for absolute/percentage support.
- `backend/src/services/simulation/workforce.py` - Workforce processing logic for recruitment/churn.
- `backend/src/services/config_service.py` - Data loading/parsing logic for new fields.
- `backend/tests/unit/test_engine_basic.py` - Unit tests for simulation engine.
- `backend/tests/unit/test_monthly_simulation.py` - Unit tests for monthly simulation logic.
- `backend/tests/unit/test_excel_export.py` - Tests for output/export validation.

### Notes
- Unit tests should be placed alongside the code files they are testing.
- Use `pytest` for backend tests.

## Tasks

- [ ] 1.0 Design and Document Data Model Changes
  - [ ] 1.1 Define JSON/YAML schema for supporting both absolute and percentage fields per office/role/level/month
  - [ ] 1.2 Update or create documentation for the new data model
  - [ ] 1.3 Review with stakeholders for feedback and approval

- [ ] 2.0 Update Data Parsing and Validation Logic
  - [ ] 2.1 Update `config_service.py` to parse both absolute and percentage fields
  - [ ] 2.2 Add validation to ensure at least one value is present for each required field
  - [ ] 2.3 Add warnings or errors for missing or conflicting values

- [ ] 3.0 Update Simulation Engine Logic for Recruitment/Churn
  - [ ] 3.1 Refactor `simulation_engine.py` and `workforce.py` to check for absolute values first, then percentage
  - [ ] 3.2 Implement fallback logic and ensure correct precedence
  - [ ] 3.3 Ensure logic is applied for all relevant simulation steps (recruitment, churn, etc.)

- [ ] 4.0 Add Logging and Reporting for Method Used
  - [ ] 4.1 Update engine logging to indicate which method (absolute or percentage) was used for each value
  - [ ] 4.2 Ensure logs are clear and accessible for audit purposes
  - [ ] 4.3 Add reporting to simulation output if needed

- [ ] 5.0 Ensure Backward Compatibility and Fallbacks
  - [ ] 5.1 Test with existing percentage-only configs to ensure no regressions
  - [ ] 5.2 Add fallback logic for missing fields (treat as zero or warn)
  - [ ] 5.3 Document backward compatibility behavior

- [ ] 6.0 Update and Expand Unit/Integration Tests
  - [ ] 6.1 Add unit tests for absolute, percentage, and mixed scenarios
  - [ ] 6.2 Add integration tests for end-to-end simulation runs with new logic
  - [ ] 6.3 Test edge cases (missing data, both values present, etc.)

- [ ] 7.0 Update Documentation and Developer Guides
  - [ ] 7.1 Update developer documentation to describe new logic and data model
  - [ ] 7.2 Add migration guide for users moving from percentage-only to mixed configs
  - [ ] 7.3 Document logging and reporting changes

I have generated the high-level tasks based on the PRD. Ready to generate the sub-tasks? Respond with 'Go' to proceed. 