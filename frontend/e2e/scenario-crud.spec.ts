import { test, expect } from '@playwright/test';

/**
 * Comprehensive E2E tests for Scenario CRUD operations
 * Tests Create, Read, Update, Delete functionality in the browser
 */

test.describe('Scenario CRUD Operations', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to scenario runner page
    await page.goto('/scenario-runner');
    
    // Wait for the page to load
    await page.waitForSelector('h2:has-text("Scenario Runner")', { timeout: 10000 });
  });

  test('should create a new scenario successfully', async ({ page }) => {
    // Click create new scenario button
    await page.click('button:has-text("Create New Scenario")');
    
    // Wait for the creation form to appear
    await page.waitForSelector('h4:has-text("Create New Scenario")');
    
    // Fill in scenario details
    await page.fill('input[placeholder*="scenario name"]', 'Test Growth Scenario 2025-2027');
    await page.fill('textarea[placeholder*="Describe the scenario"]', 'Testing scenario creation functionality');
    
    // Set time range
    await page.fill('input[type="number"]:nth-of-type(1)', '2025'); // Start year
    await page.selectOption('select:has-text("1")', '1'); // Start month
    await page.fill('input[type="number"]:nth-of-type(2)', '2027'); // End year
    await page.selectOption('select:has-text("12")', '12'); // End month
    
    // Select office scope (Group)
    await page.click('input[type="radio"][value="group"]');
    
    // Click Next to proceed to lever configuration
    await page.click('button:has-text("Next: Configure Levers")');
    
    // Wait for lever configuration page
    await page.waitForSelector('h4:has-text("Configure Levers")', { timeout: 10000 });
    
    // Configure some basic levers (Stockholm office)
    await page.click('text=Stockholm');
    await page.click('text=Consultant');
    await page.click('text=A');
    
    // Set recruitment rate
    await page.fill('input[placeholder*="recruitment rate"]', '0.05');
    await page.fill('input[placeholder*="churn rate"]', '0.02');
    
    // Save the scenario
    await page.click('button:has-text("Save Scenario")');
    
    // Wait for success message or redirect
    await page.waitForSelector('text=Scenario created successfully', { timeout: 15000 });
    
    // Verify scenario appears in the list
    await expect(page.locator('text=Test Growth Scenario 2025-2027')).toBeVisible();
  });

  test('should list existing scenarios', async ({ page }) => {
    // Wait for scenarios to load
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Check if scenarios table is visible
    const table = page.locator('table');
    await expect(table).toBeVisible();
    
    // Check table headers
    await expect(page.locator('th:has-text("Name")')).toBeVisible();
    await expect(page.locator('th:has-text("Description")')).toBeVisible();
    await expect(page.locator('th:has-text("Scope")')).toBeVisible();
    await expect(page.locator('th:has-text("Duration")')).toBeVisible();
    await expect(page.locator('th:has-text("Created")')).toBeVisible();
    await expect(page.locator('th:has-text("Updated")')).toBeVisible();
    await expect(page.locator('th:has-text("Actions")')).toBeVisible();
  });

  test('should view scenario details', async ({ page }) => {
    // Wait for scenarios to load
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Click View button on first scenario (if exists)
    const viewButton = page.locator('button:has-text("View")').first();
    
    if (await viewButton.isVisible()) {
      await viewButton.click();
      
      // Wait for scenario details page
      await page.waitForSelector('h2:has-text("Scenario Details")', { timeout: 10000 });
      
      // Verify scenario details are displayed
      await expect(page.locator('text=Scenario Details')).toBeVisible();
      
      // Go back to list
      await page.click('button:has-text("Back to Scenarios")');
      await page.waitForSelector('h2:has-text("Scenario Runner")');
    } else {
      // If no scenarios exist, this test passes (no scenarios to view)
      console.log('No scenarios available to view');
    }
  });

  test('should edit existing scenario', async ({ page }) => {
    // Wait for scenarios to load
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Click Edit button on first scenario (if exists)
    const editButton = page.locator('button:has-text("Edit")').first();
    
    if (await editButton.isVisible()) {
      await editButton.click();
      
      // Wait for edit form
      await page.waitForSelector('h4:has-text("Edit Scenario")', { timeout: 10000 });
      
      // Modify scenario name
      const nameInput = page.locator('input[placeholder*="scenario name"]');
      await nameInput.clear();
      await nameInput.fill('Updated Test Scenario');
      
      // Modify description
      const descInput = page.locator('textarea[placeholder*="Describe the scenario"]');
      await descInput.clear();
      await descInput.fill('Updated description for testing');
      
      // Save changes
      await page.click('button:has-text("Save Changes")');
      
      // Wait for success message
      await page.waitForSelector('text=Scenario updated successfully', { timeout: 15000 });
      
      // Verify updated name appears in list
      await expect(page.locator('text=Updated Test Scenario')).toBeVisible();
    } else {
      // If no scenarios exist, create one first then edit
      console.log('No scenarios available to edit, creating one first...');
      
      // Create a scenario first
      await page.click('button:has-text("Create New Scenario")');
      await page.waitForSelector('h4:has-text("Create New Scenario")');
      
      // Fill basic details
      await page.fill('input[placeholder*="scenario name"]', 'Scenario to Edit');
      await page.fill('textarea[placeholder*="Describe the scenario"]', 'Scenario for editing test');
      await page.fill('input[type="number"]:nth-of-type(1)', '2025');
      await page.fill('input[type="number"]:nth-of-type(2)', '2026');
      await page.click('input[type="radio"][value="group"]');
      await page.click('button:has-text("Next: Configure Levers")');
      
      // Quick save
      await page.waitForSelector('h4:has-text("Configure Levers")', { timeout: 10000 });
      await page.click('button:has-text("Save Scenario")');
      await page.waitForSelector('text=Scenario created successfully', { timeout: 15000 });
      
      // Now edit it
      await page.click('button:has-text("Edit")');
      await page.waitForSelector('h4:has-text("Edit Scenario")', { timeout: 10000 });
      
      const nameInput = page.locator('input[placeholder*="scenario name"]');
      await nameInput.clear();
      await nameInput.fill('Edited Scenario');
      
      await page.click('button:has-text("Save Changes")');
      await page.waitForSelector('text=Scenario updated successfully', { timeout: 15000 });
      
      await expect(page.locator('text=Edited Scenario')).toBeVisible();
    }
  });

  test('should delete scenario', async ({ page }) => {
    // Wait for scenarios to load
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Click Delete button on first scenario (if exists)
    const deleteButton = page.locator('button:has-text("Delete")').first();
    
    if (await deleteButton.isVisible()) {
      // Get the scenario name before deletion for verification
      const scenarioName = await page.locator('td:first-child').first().textContent();
      
      await deleteButton.click();
      
      // Confirm deletion in popup
      await page.waitForSelector('.ant-popconfirm');
      await page.click('button:has-text("Yes")');
      
      // Wait for success message
      await page.waitForSelector('text=Scenario deleted successfully', { timeout: 15000 });
      
      // Verify scenario is removed from list
      if (scenarioName) {
        await expect(page.locator(`text=${scenarioName}`)).not.toBeVisible();
      }
    } else {
      // If no scenarios exist, create one first then delete
      console.log('No scenarios available to delete, creating one first...');
      
      // Create a scenario first
      await page.click('button:has-text("Create New Scenario")');
      await page.waitForSelector('h4:has-text("Create New Scenario")');
      
      // Fill basic details
      await page.fill('input[placeholder*="scenario name"]', 'Scenario to Delete');
      await page.fill('textarea[placeholder*="Describe the scenario"]', 'Scenario for deletion test');
      await page.fill('input[type="number"]:nth-of-type(1)', '2025');
      await page.fill('input[type="number"]:nth-of-type(2)', '2026');
      await page.click('input[type="radio"][value="group"]');
      await page.click('button:has-text("Next: Configure Levers")');
      
      // Quick save
      await page.waitForSelector('h4:has-text("Configure Levers")', { timeout: 10000 });
      await page.click('button:has-text("Save Scenario")');
      await page.waitForSelector('text=Scenario created successfully', { timeout: 15000 });
      
      // Now delete it
      await page.click('button:has-text("Delete")');
      await page.waitForSelector('.ant-popconfirm');
      await page.click('button:has-text("Yes")');
      await page.waitForSelector('text=Scenario deleted successfully', { timeout: 15000 });
      
      await expect(page.locator('text=Scenario to Delete')).not.toBeVisible();
    }
  });

  test('should export scenario results', async ({ page }) => {
    // Wait for scenarios to load
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Click Export button on first scenario (if exists)
    const exportButton = page.locator('button:has-text("Export")').first();
    
    if (await exportButton.isVisible()) {
      // Set up download listener
      const downloadPromise = page.waitForEvent('download');
      
      await exportButton.click();
      
      // Wait for download to start
      const download = await downloadPromise;
      
      // Verify download filename
      expect(download.suggestedFilename()).toMatch(/scenario-.*\.xlsx/);
      
      console.log(`Downloaded: ${download.suggestedFilename()}`);
    } else {
      console.log('No scenarios available to export');
    }
  });

  test('should handle empty state gracefully', async ({ page }) => {
    // If no scenarios exist, should show empty state
    const emptyState = page.locator('.ant-empty');
    
    if (await emptyState.isVisible()) {
      await expect(page.locator('text=No scenarios found')).toBeVisible();
      await expect(page.locator('button:has-text("Create Your First Scenario")')).toBeVisible();
    }
  });

  test('should validate form inputs', async ({ page }) => {
    // Click create new scenario button
    await page.click('button:has-text("Create New Scenario")');
    await page.waitForSelector('h4:has-text("Create New Scenario")');
    
    // Try to submit without required fields
    await page.click('button:has-text("Next: Configure Levers")');
    
    // Should show validation errors
    await expect(page.locator('.ant-form-item-explain-error')).toBeVisible();
    
    // Fill required fields
    await page.fill('input[placeholder*="scenario name"]', 'Valid Scenario');
    await page.fill('input[type="number"]:nth-of-type(1)', '2025');
    await page.fill('input[type="number"]:nth-of-type(2)', '2027');
    
    // Try to submit again
    await page.click('button:has-text("Next: Configure Levers")');
    
    // Should proceed to next step
    await page.waitForSelector('h4:has-text("Configure Levers")', { timeout: 10000 });
  });

  test('should handle individual office selection', async ({ page }) => {
    // Click create new scenario button
    await page.click('button:has-text("Create New Scenario")');
    await page.waitForSelector('h4:has-text("Create New Scenario")');
    
    // Fill basic details
    await page.fill('input[placeholder*="scenario name"]', 'Individual Offices Scenario');
    await page.fill('textarea[placeholder*="Describe the scenario"]', 'Testing individual office selection');
    await page.fill('input[type="number"]:nth-of-type(1)', '2025');
    await page.fill('input[type="number"]:nth-of-type(2)', '2026');
    
    // Select individual offices
    await page.click('input[type="radio"][value="individual"]');
    
    // Wait for office selection dropdown
    await page.waitForSelector('select[placeholder*="Choose offices"]');
    
    // Select specific offices
    await page.selectOption('select[placeholder*="Choose offices"]', ['Stockholm', 'Oslo']);
    
    // Proceed to next step
    await page.click('button:has-text("Next: Configure Levers")');
    
    // Should proceed to lever configuration
    await page.waitForSelector('h4:has-text("Configure Levers")', { timeout: 10000 });
  });
}); 