# Scenario CRUD E2E Tests

This directory contains comprehensive end-to-end (E2E) tests for the Scenario Runner functionality using Playwright.

## 🧪 Test Coverage

### 1. **Scenario CRUD Operations** (`scenario-crud.spec.ts`)
- ✅ **Create**: New scenario creation with form validation
- ✅ **Read**: List scenarios, view scenario details
- ✅ **Update**: Edit existing scenarios
- ✅ **Delete**: Remove scenarios with confirmation
- ✅ **Export**: Download scenario results as Excel
- ✅ **Form Validation**: Required fields, date validation, office selection
- ✅ **Empty State**: Handle no scenarios gracefully

### 2. **Scenario Comparison** (`scenario-comparison.spec.ts`)
- ✅ **Multiple Scenarios**: Create scenarios for comparison
- ✅ **Side-by-Side Comparison**: Compare selected scenarios
- ✅ **Scenario Execution**: Run scenarios and view results
- ✅ **Export Comparison**: Download comparison results
- ✅ **Selection States**: Handle scenario selection logic

### 3. **Error Handling** (`scenario-error-handling.spec.ts`)
- ✅ **Network Errors**: Handle offline/connection issues
- ✅ **Form Validation**: Invalid inputs and edge cases
- ✅ **Concurrent Operations**: Multiple users editing same scenario
- ✅ **Large Datasets**: Performance with many offices/time ranges
- ✅ **Dependencies**: Handle scenario deletion with results
- ✅ **Browser Issues**: Refresh during creation, slow networks

## 🚀 Running Tests

### Prerequisites
1. **Backend Server**: Must be running on `http://localhost:8000`
2. **Frontend Server**: Must be running on `http://localhost:3000`

### Quick Start
```bash
# Navigate to frontend directory
cd frontend

# Run all E2E tests with headed browser (visible)
npm run test:e2e:headed

# Run tests in headless mode (faster)
npm run test:e2e

# Run with UI mode (interactive)
npm run test:e2e:ui

# Debug mode (step through tests)
npm run test:e2e:debug

# View test report
npm run test:e2e:report
```

### Using PowerShell Script
```powershell
# Run comprehensive test suite with health checks
.\e2e\run-all-tests.ps1
```

## 📋 Test Commands

| Command | Description |
|---------|-------------|
| `npm run test:e2e` | Run all tests in headless mode |
| `npm run test:e2e:headed` | Run tests with visible browser |
| `npm run test:e2e:ui` | Run with Playwright UI |
| `npm run test:e2e:debug` | Debug mode with step-through |
| `npm run test:e2e:report` | Show HTML test report |

## 🎯 Test Scenarios

### Basic CRUD Flow
1. **Create Scenario**
   - Fill scenario name, description, time range
   - Select office scope (Group or Individual)
   - Configure levers (recruitment, churn rates)
   - Save and verify success

2. **List Scenarios**
   - Verify table headers and data display
   - Check scenario information accuracy

3. **View Scenario**
   - Click view button
   - Verify details page loads
   - Navigate back to list

4. **Edit Scenario**
   - Modify scenario name/description
   - Update lever configurations
   - Save and verify changes

5. **Delete Scenario**
   - Click delete with confirmation
   - Verify removal from list

### Advanced Features
- **Export**: Download Excel files
- **Comparison**: Select multiple scenarios
- **Validation**: Form error handling
- **Performance**: Large datasets
- **Error Recovery**: Network issues

## 🔧 Configuration

### Playwright Config (`playwright.config.ts`)
- **Browsers**: Chrome, Firefox, Safari, Mobile
- **Base URL**: `http://localhost:3000`
- **Timeouts**: 10-30 seconds for operations
- **Screenshots**: On failure
- **Videos**: On failure
- **Traces**: On retry

### Test Structure
```typescript
test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup: navigate to page
  });

  test('should do something', async ({ page }) => {
    // Test steps with assertions
  });
});
```

## 🐛 Debugging

### Common Issues
1. **Server Not Running**
   ```bash
   # Start backend
   $env:PYTHONPATH="."; python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   
   # Start frontend
   cd frontend; npm run dev
   ```

2. **Test Failures**
   - Check browser console for errors
   - Verify API endpoints are working
   - Check network connectivity

3. **Slow Tests**
   - Use headless mode for faster execution
   - Reduce timeouts if appropriate
   - Check for unnecessary waits

### Debug Mode
```bash
npm run test:e2e:debug
```
- Opens browser with step-through debugging
- Pause on each action
- Inspect elements and state

## 📊 Test Reports

After running tests, view detailed reports:
```bash
npm run test:e2e:report
```

Reports include:
- ✅ Pass/fail status
- 📸 Screenshots on failure
- 🎥 Video recordings
- 📈 Performance metrics
- 🔍 Trace files for debugging

## 🎯 Best Practices

1. **Isolation**: Each test is independent
2. **Cleanup**: Tests clean up after themselves
3. **Reliability**: Handle async operations properly
4. **Readability**: Clear test descriptions
5. **Maintainability**: Reusable selectors and helpers

## 🔄 Continuous Integration

These tests can be integrated into CI/CD pipelines:
```yaml
# Example GitHub Actions
- name: Run E2E Tests
  run: |
    cd frontend
    npm run test:e2e
```

## 📝 Adding New Tests

1. Create new test file: `new-feature.spec.ts`
2. Follow existing patterns
3. Add descriptive test names
4. Include proper assertions
5. Handle edge cases
6. Update this README

## 🆘 Support

If tests fail:
1. Check server status
2. Review error messages
3. Use debug mode
4. Check browser console
5. Verify API responses 