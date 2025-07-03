import { test, expect } from '@playwright/test';

/**
 * E2E tests for Scenario Comparison functionality
 */

test.describe('Scenario Comparison', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to scenario runner page
    await page.goto('/scenario-runner');
    
    // Wait for the page to load
    await page.waitForSelector('h2:has-text("Scenario Runner")', { timeout: 10000 });
  });

  test('should create multiple scenarios for comparison', async ({ page }) => {
    // Create first scenario
    await page.click('button:has-text("Create New Scenario")');
    await page.waitForSelector('h4:has-text("Create New Scenario")');
    
    await page.fill('input[placeholder*="scenario name"]', 'Growth Scenario A');
    await page.fill('textarea[placeholder*="Describe the scenario"]', 'High growth scenario');
    await page.fill('input[type="number"]:nth-of-type(1)', '2025');
    await page.fill('input[type="number"]:nth-of-type(2)', '2027');
    await page.click('input[type="radio"][value="group"]');
    await page.click('button:has-text("Next: Configure Levers")');
    
    await page.waitForSelector('h4:has-text("Configure Levers")', { timeout: 10000 });
    await page.click('button:has-text("Save Scenario")');
    await page.waitForSelector('text=Scenario created successfully', { timeout: 15000 });
    
    // Create second scenario
    await page.click('button:has-text("Create New Scenario")');
    await page.waitForSelector('h4:has-text("Create New Scenario")');
    
    await page.fill('input[placeholder*="scenario name"]', 'Conservative Scenario B');
    await page.fill('textarea[placeholder*="Describe the scenario"]', 'Conservative growth scenario');
    await page.fill('input[type="number"]:nth-of-type(1)', '2025');
    await page.fill('input[type="number"]:nth-of-type(2)', '2026');
    await page.click('input[type="radio"][value="group"]');
    await page.click('button:has-text("Next: Configure Levers")');
    
    await page.waitForSelector('h4:has-text("Configure Levers")', { timeout: 10000 });
    await page.click('button:has-text("Save Scenario")');
    await page.waitForSelector('text=Scenario created successfully', { timeout: 15000 });
    
    // Verify both scenarios are in the list
    await expect(page.locator('text=Growth Scenario A')).toBeVisible();
    await expect(page.locator('text=Conservative Scenario B')).toBeVisible();
  });

  test('should compare scenarios side by side', async ({ page }) => {
    // Wait for scenarios to load
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Check if we have at least 2 scenarios
    const scenarioRows = page.locator('tbody tr');
    const count = await scenarioRows.count();
    
    if (count >= 2) {
      // Select first two scenarios for comparison
      await page.locator('input[type="checkbox"]').nth(0).check();
      await page.locator('input[type="checkbox"]').nth(1).check();
      
      // Click compare button
      await page.click('button:has-text("Compare Scenarios")');
      
      // Wait for comparison view
      await page.waitForSelector('h2:has-text("Scenario Comparison")', { timeout: 10000 });
      
      // Verify comparison elements are present
      await expect(page.locator('text=Scenario Comparison')).toBeVisible();
      
      // Go back to scenarios list
      await page.click('button:has-text("Back to Scenarios")');
      await page.waitForSelector('h2:has-text("Scenario Runner")');
    } else {
      console.log('Not enough scenarios for comparison test');
    }
  });

  test('should run scenarios and view results', async ({ page }) => {
    // Wait for scenarios to load
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Click Run button on first scenario (if exists)
    const runButton = page.locator('button:has-text("Run")').first();
    
    if (await runButton.isVisible()) {
      await runButton.click();
      
      // Wait for simulation to complete
      await page.waitForSelector('text=Simulation completed', { timeout: 30000 });
      
      // Verify results are displayed
      await expect(page.locator('text=Results')).toBeVisible();
      
      // Check for key metrics
      await expect(page.locator('text=Total FTE')).toBeVisible();
      await expect(page.locator('text=Revenue')).toBeVisible();
      await expect(page.locator('text=Costs')).toBeVisible();
      
      // Go back to scenarios list
      await page.click('button:has-text("Back to Scenarios")');
      await page.waitForSelector('h2:has-text("Scenario Runner")');
    } else {
      console.log('No scenarios available to run');
    }
  });

  test('should export comparison results', async ({ page }) => {
    // Wait for scenarios to load
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Check if we have at least 2 scenarios
    const scenarioRows = page.locator('tbody tr');
    const count = await scenarioRows.count();
    
    if (count >= 2) {
      // Select scenarios and go to comparison
      await page.locator('input[type="checkbox"]').nth(0).check();
      await page.locator('input[type="checkbox"]').nth(1).check();
      await page.click('button:has-text("Compare Scenarios")');
      await page.waitForSelector('h2:has-text("Scenario Comparison")', { timeout: 10000 });
      
      // Look for export button in comparison view
      const exportButton = page.locator('button:has-text("Export Comparison")');
      
      if (await exportButton.isVisible()) {
        // Set up download listener
        const downloadPromise = page.waitForEvent('download');
        
        await exportButton.click();
        
        // Wait for download to start
        const download = await downloadPromise;
        
        // Verify download filename
        expect(download.suggestedFilename()).toMatch(/comparison-.*\.xlsx/);
        
        console.log(`Downloaded comparison: ${download.suggestedFilename()}`);
      }
    } else {
      console.log('Not enough scenarios for comparison export test');
    }
  });

  test('should handle scenario selection states', async ({ page }) => {
    // Wait for scenarios to load
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Check if scenarios exist
    const scenarioRows = page.locator('tbody tr');
    const count = await scenarioRows.count();
    
    if (count > 0) {
      // Test single selection
      await page.locator('input[type="checkbox"]').first().check();
      
      // Compare button should be disabled (need at least 2)
      const compareButton = page.locator('button:has-text("Compare Scenarios")');
      await expect(compareButton).toBeDisabled();
      
      // Select second scenario if available
      if (count >= 2) {
        await page.locator('input[type="checkbox"]').nth(1).check();
        
        // Compare button should now be enabled
        await expect(compareButton).toBeEnabled();
      }
      
      // Deselect all
      await page.locator('input[type="checkbox"]').first().uncheck();
      if (count >= 2) {
        await page.locator('input[type="checkbox"]').nth(1).uncheck();
      }
      
      // Compare button should be disabled again
      await expect(compareButton).toBeDisabled();
    } else {
      console.log('No scenarios available for selection test');
    }
  });
}); 