## Relevant Files

- `backend/src/services/excel_export_service.py` - Implements the logic for generating Excel exports from simulation data.
- `backend/routers/simulation.py` - API endpoint for triggering the export.
- `frontend/src/pages/SimulationLabV2.tsx` - UI integration for the export button and download logic.
- `frontend/src/services/simulationApi.ts` - Handles API requests for export.
- `backend/tests/unit/test_excel_export.py` - Unit tests for backend export logic.
- `frontend/src/pages/SimulationLabV2.test.tsx` - Frontend tests for export button and download flow.

### Notes

- Unit tests should be placed alongside the code files they are testing.
- Use `npx jest` for frontend tests and `pytest` for backend tests.

## Tasks

- [x] 1.0 Implement Backend Excel Export Service
  - [x] 1.1 Design data schema for Excel export (sheets, columns, formatting)
  - [x] 1.2 Implement data extraction from simulation results and KPIs
  - [x] 1.3 Generate Excel file using `pandas` and `openpyxl`
  - [x] 1.4 Apply professional formatting (headers, colors, number formats, freeze panes)
  - [x] 1.5 Add timestamp and audit info to export
  - [x] 1.6 Optimize for large datasets and memory usage

- [x] 2.0 Add API Endpoint for Simulation Export
  - [x] 2.1 Define `/api/simulation/export` POST endpoint in FastAPI
  - [x] 2.2 Validate simulation results exist before export
  - [x] 2.3 Trigger backend export service and return file as download
  - [x] 2.4 Handle errors and return clear error messages

- [x] 3.0 Integrate Export Button in SimulationLabV2 UI
  - [x] 3.1 Add "Export to Excel" button to Simulation Results section
  - [x] 3.2 Disable button when no results are available
  - [x] 3.3 Show loading/progress state during export
  - [x] 3.4 Trigger API call on button click

- [x] 4.0 Implement Frontend Download and Feedback Logic
  - [x] 4.1 Handle file download in browser (native download)
  - [x] 4.2 Show success and error feedback to user
  - [x] 4.3 Handle large file downloads gracefully

- [ ] 5.0 Ensure Data Accuracy and Professional Formatting
  - [ ] 5.1 Cross-check exported data with web interface for accuracy
  - [ ] 5.2 Add data validation indicators and formulas where needed
  - [ ] 5.3 Handle missing/zero values as 0 or "N/A"
  - [ ] 5.4 Ensure all required sheets and columns are present

- [x] 6.0 Write Unit and Integration Tests
  - [x] 6.1 Write backend unit tests for export logic
  - [ ] 6.2 Write frontend tests for export button and download
  - [ ] 6.3 Add integration test for end-to-end export flow
  - [ ] 6.4 Test error handling and edge cases

- [x] 7.0 Handle Error States and Edge Cases
  - [x] 7.1 Display clear error messages on export failure
  - [x] 7.2 Handle large simulations (up to 10 years, all offices)
  - [x] 7.3 Prevent export if no simulation data exists
  - [ ] 7.4 Warn user if export may exceed 25MB or take >60s

---
I have generated the high-level tasks based on the PRD. Ready to generate the sub-tasks? Respond with 'Go' to proceed. 