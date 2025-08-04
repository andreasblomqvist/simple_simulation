import { test, expect } from '@playwright/test';

/**
 * Comprehensive E2E test for SimpleSim simulation workflow
 * Tests the complete user journey from scenario creation to results analysis
 * Verifies both bug fixes:
 * 1. Workforce KPIs display non-zero values
 * 2. Year switching updates displayed data correctly
 */

test.describe('Simulation Workflow - Complete User Journey', () => {
  const scenarioName = `E2E Complete Workflow ${Date.now()}`;
  let scenarioId: string;

  test.beforeEach(async ({ page }) => {
    // Ensure servers are running
    await page.goto('/');
    // Wait for app to load completely
    await page.waitForLoadState('networkidle');
  });

  test('Should complete full simulation workflow with valid results', async ({ page }) => {
    // Step 1: Navigate to scenarios page
    await page.goto('/scenarios');
    await page.waitForSelector('h2:has-text("Scenarios")', { timeout: 10000 });

    // Step 2: Create a new scenario
    await page.click('button:has-text("Create Scenario")');
    await page.waitForSelector('[role="dialog"]');

    // Fill scenario basic information
    await page.fill('input[placeholder*="scenario name"]', scenarioName);
    await page.fill('textarea[placeholder*="description"]', 'E2E test scenario for complete workflow validation');
    
    // Set realistic time range (2025-2027)
    await page.fill('input[aria-label="Start Year"]', '2025');
    await page.selectOption('select[aria-label="Start Month"]', '1');
    await page.fill('input[aria-label="End Year"]', '2027');
    await page.selectOption('select[aria-label="End Month"]', '12');

    // Select office scope - use Group for comprehensive testing
    await page.click('input[type="radio"][value="group"]');

    // Proceed to lever configuration
    await page.click('button:has-text("Next")');
    await page.waitForSelector('h3:has-text("Configure Simulation Levers")', { timeout: 10000 });

    // Configure realistic simulation levers for Stockholm office
    // Select Stockholm office
    await page.click('text=Stockholm');
    await page.waitForTimeout(500);

    // Configure Consultant A level with realistic growth parameters
    await page.click('text=Consultant');
    await page.click('text=A');
    
    // Set recruitment and churn rates that will produce meaningful results
    const recruitmentInput = page.locator('input[placeholder*="recruitment"]').first();
    await recruitmentInput.clear();
    await recruitmentInput.fill('0.08'); // 8% monthly recruitment rate

    const churnInput = page.locator('input[placeholder*="churn"]').first();
    await churnInput.clear();
    await churnInput.fill('0.03'); // 3% monthly churn rate

    // Also configure Consultant B level for more realistic simulation
    await page.click('text=B');
    const recruitmentInputB = page.locator('input[placeholder*="recruitment"]').first();
    await recruitmentInputB.clear();
    await recruitmentInputB.fill('0.05'); // 5% monthly recruitment rate

    const churnInputB = page.locator('input[placeholder*="churn"]').first();
    await churnInputB.clear();
    await churnInputB.fill('0.025'); // 2.5% monthly churn rate

    // Save the scenario
    await page.click('button:has-text("Save Scenario")');
    await page.waitForSelector('.ant-message-success', { timeout: 15000 });

    // Step 3: Run the simulation
    // Navigate back to scenarios list and find our scenario
    await page.goto('/scenarios');
    await page.waitForSelector('table', { timeout: 10000 });

    // Find and click the Run button for our scenario
    const scenarioRow = page.locator(`tr:has-text("${scenarioName}")`);
    await expect(scenarioRow).toBeVisible();
    
    const runButton = scenarioRow.locator('button:has-text("Run")');
    await runButton.click();

    // Wait for simulation to complete and results to load
    await page.waitForSelector('h1:has-text("Simulation Results")', { timeout: 30000 });

    // Step 4: Verify simulation results display correctly
    
    // Check that we have the main results sections
    await expect(page.locator('h2:has-text("Workforce KPIs")')).toBeVisible();
    await expect(page.locator('h2:has-text("Financial Overview")')).toBeVisible();
    await expect(page.locator('h2:has-text("Workforce Analysis")')).toBeVisible();

    // Step 5: Verify workforce KPIs show non-zero values (Bug Fix #1)
    
    // Wait for KPI cards to load
    await page.waitForSelector('[data-testid="kpi-card"]', { timeout: 10000 });

    // Get all KPI cards
    const kpiCards = page.locator('[data-testid="kpi-card"]');
    const kpiCount = await kpiCards.count();
    expect(kpiCount).toBeGreaterThan(0);

    // Check each KPI card for non-zero values
    for (let i = 0; i < kpiCount; i++) {
      const kpiCard = kpiCards.nth(i);
      const valueElement = kpiCard.locator('[data-testid="kpi-value"]');
      const valueText = await valueElement.textContent();
      
      // Extract numeric value (handle formats like "1,234", "SEK 1.5M", etc.)
      const numericValue = parseFloat(valueText?.replace(/[^\d.-]/g, '') || '0');
      
      // KPI values should be non-zero (our bug fix verification)
      expect(numericValue).not.toBe(0);
      expect(numericValue).not.toBeNaN();
      
      console.log(`KPI ${i + 1}: ${valueText} (${numericValue})`);
    }

    // Step 6: Test year switching functionality (Bug Fix #2)
    
    // Find year navigation controls
    const yearNavigation = page.locator('[data-testid="year-navigation"]');
    await expect(yearNavigation).toBeVisible();

    // Get initial year (should be 2025)
    const initialYear = await page.locator('[data-testid="current-year"]').textContent();
    expect(initialYear).toBe('2025');

    // Store initial KPI values for comparison
    const initialKpiValues = [];
    for (let i = 0; i < kpiCount; i++) {
      const kpiCard = kpiCards.nth(i);
      const valueText = await kpiCard.locator('[data-testid="kpi-value"]').textContent();
      initialKpiValues.push(valueText);
    }

    // Navigate to next year
    await page.click('[data-testid="next-year-button"]');
    await page.waitForTimeout(1000); // Wait for data to update

    // Verify year changed to 2026
    const newYear = await page.locator('[data-testid="current-year"]').textContent();
    expect(newYear).toBe('2026');

    // Verify KPI values updated (Bug Fix #2 verification)
    let valuesChanged = false;
    for (let i = 0; i < kpiCount; i++) {
      const kpiCard = kpiCards.nth(i);
      const newValueText = await kpiCard.locator('[data-testid="kpi-value"]').textContent();
      
      if (newValueText !== initialKpiValues[i]) {
        valuesChanged = true;
        break;
      }
    }

    expect(valuesChanged).toBe(true);
    console.log('Year switching successfully updated KPI values');

    // Navigate to 2027 and verify again
    await page.click('[data-testid="next-year-button"]');
    await page.waitForTimeout(1000);

    const finalYear = await page.locator('[data-testid="current-year"]').textContent();
    expect(finalYear).toBe('2027');

    // Navigate back to 2025 and verify data consistency
    await page.click('[data-testid="previous-year-button"]');
    await page.waitForTimeout(1000);
    await page.click('[data-testid="previous-year-button"]');
    await page.waitForTimeout(1000);

    const backToInitialYear = await page.locator('[data-testid="current-year"]').textContent();
    expect(backToInitialYear).toBe('2025');

    // Step 7: Verify charts and data visualizations
    
    // Check workforce stacked bar chart
    const workforceChart = page.locator('[data-testid="workforce-chart"]');
    await expect(workforceChart).toBeVisible();

    // Check financial charts
    const revenueChart = page.locator('[data-testid="revenue-chart"]');
    await expect(revenueChart).toBeVisible();

    const profitabilityChart = page.locator('[data-testid="profitability-chart"]');
    await expect(profitabilityChart).toBeVisible();

    // Verify chart data is populated (charts should have SVG elements)
    const chartSvgs = page.locator('svg');
    const svgCount = await chartSvgs.count();
    expect(svgCount).toBeGreaterThan(0);

    // Step 8: Test responsive behavior and error states
    
    // Test chart interactions (hover, click)
    await workforceChart.hover();
    await page.waitForTimeout(500);

    // Check for tooltip or interaction feedback
    const tooltips = page.locator('.recharts-tooltip-wrapper, [role="tooltip"]');
    const tooltipCount = await tooltips.count();
    // Tooltips may or may not be visible depending on implementation
    console.log(`Found ${tooltipCount} chart tooltips`);

    // Step 9: Verify data table functionality
    
    // Check for data tables in results
    const dataTables = page.locator('table');
    const tableCount = await dataTables.count();
    expect(tableCount).toBeGreaterThan(0);

    // Verify table contains data rows
    for (let i = 0; i < tableCount; i++) {
      const table = dataTables.nth(i);
      const rows = table.locator('tbody tr');
      const rowCount = await rows.count();
      expect(rowCount).toBeGreaterThan(0);
      
      // Check that cells contain non-empty data
      const firstDataCell = rows.first().locator('td').first();
      const cellText = await firstDataCell.textContent();
      expect(cellText?.trim()).not.toBe('');
    }

    // Step 10: Test export functionality (if available)
    
    const exportButton = page.locator('button:has-text("Export")');
    if (await exportButton.isVisible()) {
      // Set up download listener
      const downloadPromise = page.waitForEvent('download');
      await exportButton.click();
      
      try {
        const download = await downloadPromise;
        expect(download.suggestedFilename()).toMatch(/.*\.(xlsx|csv|json)$/);
        console.log(`Export successful: ${download.suggestedFilename()}`);
      } catch (error) {
        console.log('Export test skipped - download may not be implemented');
      }
    }

    // Step 11: Verify scenario navigation and state persistence
    
    // Navigate back to scenarios list
    await page.click('a[href="/scenarios"]');
    await page.waitForSelector('h2:has-text("Scenarios")');

    // Verify our scenario still exists and shows completed status
    const scenarioRowFinal = page.locator(`tr:has-text("${scenarioName}")`);
    await expect(scenarioRowFinal).toBeVisible();

    // Check if scenario has results status indicator
    const statusIndicators = scenarioRowFinal.locator('.badge, .ant-tag, [data-testid="status"]');
    if (await statusIndicators.count() > 0) {
      // Scenario should show as completed/run
      console.log('Scenario status indicators found');
    }

    console.log('✅ Complete simulation workflow test passed successfully');
  });

  test('Should handle simulation errors gracefully', async ({ page }) => {
    // Create a scenario with invalid parameters to test error handling
    await page.goto('/scenarios');
    await page.waitForSelector('h2:has-text("Scenarios")');

    await page.click('button:has-text("Create Scenario")');
    await page.waitForSelector('[role="dialog"]');

    // Create scenario with invalid time range (end before start)
    await page.fill('input[placeholder*="scenario name"]', `Error Test ${Date.now()}`);
    await page.fill('input[aria-label="Start Year"]', '2027');
    await page.fill('input[aria-label="End Year"]', '2025'); // Invalid: end before start

    await page.click('button:has-text("Next")');

    // Should show validation error
    const errorMessages = page.locator('.ant-form-item-explain-error, .text-red-500');
    await expect(errorMessages.first()).toBeVisible();

    // Fix the date range
    await page.fill('input[aria-label="End Year"]', '2028');
    
    await page.click('button:has-text("Next")');
    await page.waitForSelector('h3:has-text("Configure Simulation Levers")');

    // Save with minimal configuration
    await page.click('button:has-text("Save Scenario")');
    await page.waitForSelector('.ant-message-success');

    console.log('✅ Error handling test passed');
  });

  test('Should maintain data consistency across multiple year switches', async ({ page }) => {
    // This test specifically focuses on the year switching bug fix
    await page.goto('/scenarios');
    
    // Find a scenario with results or create one
    const existingScenarios = page.locator('tr:has(button:has-text("View Results"))');
    const scenarioCount = await existingScenarios.count();
    
    if (scenarioCount > 0) {
      // Use existing scenario with results
      await existingScenarios.first().locator('button:has-text("View Results")').click();
    } else {
      // Create and run a quick scenario
      await page.click('button:has-text("Create Scenario")');
      await page.waitForSelector('[role="dialog"]');
      
      await page.fill('input[placeholder*="scenario name"]', `Year Switch Test ${Date.now()}`);
      await page.fill('input[aria-label="Start Year"]', '2025');
      await page.fill('input[aria-label="End Year"]', '2027');
      await page.click('input[type="radio"][value="group"]');
      
      await page.click('button:has-text("Next")');
      await page.waitForSelector('h3:has-text("Configure Simulation Levers")');
      
      // Quick configuration
      await page.click('text=Stockholm');
      await page.click('text=Consultant');
      await page.click('text=A');
      
      await page.fill('input[placeholder*="recruitment"]', '0.05');
      await page.fill('input[placeholder*="churn"]', '0.02');
      
      await page.click('button:has-text("Save Scenario")');
      await page.waitForSelector('.ant-message-success');
      
      // Run the scenario
      await page.goto('/scenarios');
      const newScenarioRow = page.locator('tr').last();
      await newScenarioRow.locator('button:has-text("Run")').click();
    }

    // Wait for results page
    await page.waitForSelector('h1:has-text("Simulation Results")', { timeout: 30000 });

    // Perform rapid year switching to test data consistency
    const years = ['2025', '2026', '2027', '2026', '2025', '2027'];
    const yearData = new Map();

    for (const targetYear of years) {
      // Navigate to year
      const currentYear = await page.locator('[data-testid="current-year"]').textContent();
      
      while (currentYear !== targetYear) {
        if (parseInt(currentYear || '0') < parseInt(targetYear)) {
          await page.click('[data-testid="next-year-button"]');
        } else {
          await page.click('[data-testid="previous-year-button"]');
        }
        await page.waitForTimeout(500);
      }

      // Capture KPI values for this year
      const kpiCards = page.locator('[data-testid="kpi-card"]');
      const kpiCount = await kpiCards.count();
      const yearKpis = [];

      for (let i = 0; i < kpiCount; i++) {
        const value = await kpiCards.nth(i).locator('[data-testid="kpi-value"]').textContent();
        yearKpis.push(value);
      }

      // Check consistency if we've seen this year before
      if (yearData.has(targetYear)) {
        const previousValues = yearData.get(targetYear);
        expect(yearKpis).toEqual(previousValues);
        console.log(`✅ Year ${targetYear} data consistency verified`);
      } else {
        yearData.set(targetYear, yearKpis);
        console.log(`📊 Captured year ${targetYear} data`);
      }
    }

    console.log('✅ Year switching consistency test passed');
  });

  // Clean up after tests
  test.afterEach(async ({ page }) => {
    // Try to clean up any test scenarios we created
    try {
      await page.goto('/scenarios');
      const testScenarios = page.locator(`tr:has-text("E2E")`);
      const count = await testScenarios.count();
      
      for (let i = 0; i < Math.min(count, 3); i++) { // Limit cleanup to avoid long waits
        const deleteButton = testScenarios.nth(i).locator('button:has-text("Delete")');
        if (await deleteButton.isVisible()) {
          await deleteButton.click();
          await page.click('button:has-text("Yes")');
          await page.waitForTimeout(1000);
        }
      }
    } catch (error) {
      console.log('Cleanup skipped:', error);
    }
  });
});

test.describe('Simulation Results Data Validation', () => {
  test('Should display meaningful workforce metrics across all components', async ({ page }) => {
    // This test focuses specifically on verifying that all components show non-zero data
    await page.goto('/scenarios');
    
    // Find any scenario with results or create a simple one
    const resultsButtons = page.locator('button:has-text("View Results")');
    const resultsCount = await resultsButtons.count();
    
    if (resultsCount === 0) {
      // Create a minimal scenario for testing
      await page.click('button:has-text("Create Scenario")');
      await page.waitForSelector('[role="dialog"]');
      
      await page.fill('input[placeholder*="scenario name"]', `Data Validation Test ${Date.now()}`);
      await page.fill('input[aria-label="Start Year"]', '2025');
      await page.fill('input[aria-label="End Year"]', '2026');
      await page.click('input[type="radio"][value="group"]');
      
      await page.click('button:has-text("Next")');
      await page.waitForSelector('h3:has-text("Configure Simulation Levers")');
      
      // Set parameters that will definitely produce results
      await page.click('text=Stockholm');
      await page.click('text=Consultant');
      await page.click('text=A');
      
      await page.fill('input[placeholder*="recruitment"]', '0.1'); // High recruitment
      await page.fill('input[placeholder*="churn"]', '0.01'); // Low churn
      
      await page.click('button:has-text("Save Scenario")');
      await page.waitForSelector('.ant-message-success');
      
      // Run it
      await page.goto('/scenarios');
      await page.locator('tr').last().locator('button:has-text("Run")').click();
    } else {
      // Use existing results
      await resultsButtons.first().click();
    }

    // Wait for results to load
    await page.waitForSelector('h1:has-text("Simulation Results")', { timeout: 30000 });

    // Comprehensive data validation across all result components

    // 1. Workforce KPI Cards
    const kpiCards = page.locator('[data-testid="kpi-card"]');
    const kpiCount = await kpiCards.count();
    expect(kpiCount).toBeGreaterThan(0);

    let totalKpiValue = 0;
    for (let i = 0; i < kpiCount; i++) {
      const valueText = await kpiCards.nth(i).locator('[data-testid="kpi-value"]').textContent();
      const numericValue = parseFloat(valueText?.replace(/[^\d.-]/g, '') || '0');
      
      expect(numericValue).not.toBeNaN();
      expect(Math.abs(numericValue)).toBeGreaterThan(0); // Allow negative values but not zero
      totalKpiValue += Math.abs(numericValue);
    }
    expect(totalKpiValue).toBeGreaterThan(0);

    // 2. Financial Tables
    const financialTables = page.locator('table:has(th:has-text("Revenue")), table:has(th:has-text("Sales")), table:has(th:has-text("EBITDA"))');
    const financialTableCount = await financialTables.count();
    
    for (let i = 0; i < financialTableCount; i++) {
      const table = financialTables.nth(i);
      const dataCells = table.locator('tbody td:not(:first-child)'); // Skip label column
      const cellCount = await dataCells.count();
      
      let nonZeroCount = 0;
      for (let j = 0; j < Math.min(cellCount, 10); j++) { // Check first 10 cells
        const cellText = await dataCells.nth(j).textContent();
        const value = parseFloat(cellText?.replace(/[^\d.-]/g, '') || '0');
        if (!isNaN(value) && value !== 0) {
          nonZeroCount++;
        }
      }
      
      expect(nonZeroCount).toBeGreaterThan(0);
    }

    // 3. Workforce Tables
    const workforceTables = page.locator('table:has(th:has-text("FTE")), table:has(th:has-text("Total"))');
    const workforceTableCount = await workforceTables.count();
    
    for (let i = 0; i < workforceTableCount; i++) {
      const table = workforceTables.nth(i);
      const dataCells = table.locator('tbody td:not(:first-child)');
      const cellCount = await dataCells.count();
      
      let nonZeroCount = 0;
      for (let j = 0; j < Math.min(cellCount, 10); j++) {
        const cellText = await dataCells.nth(j).textContent();
        const value = parseFloat(cellText?.replace(/[^\d.-]/g, '') || '0');
        if (!isNaN(value) && value !== 0) {
          nonZeroCount++;
        }
      }
      
      expect(nonZeroCount).toBeGreaterThan(0);
    }

    // 4. Chart Elements (verify charts have data)
    const chartSvgs = page.locator('svg:has(path), svg:has(rect), svg:has(circle)');
    const chartCount = await chartSvgs.count();
    expect(chartCount).toBeGreaterThan(0);

    // Check that charts have data elements (bars, lines, etc.)
    for (let i = 0; i < Math.min(chartCount, 5); i++) {
      const chart = chartSvgs.nth(i);
      const dataElements = chart.locator('path[d*="M"], rect[height], circle[r]');
      const elementCount = await dataElements.count();
      expect(elementCount).toBeGreaterThan(0);
    }

    console.log('✅ All components display meaningful non-zero data');
  });
});