import { test, expect } from '@playwright/test';

/**
 * E2E tests for Scenario Error Handling and Edge Cases
 */

test.describe('Scenario Error Handling', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to scenario runner page
    await page.goto('/scenario-runner');
    
    // Wait for the page to load
    await page.waitForSelector('h2:has-text("Scenario Runner")', { timeout: 10000 });
  });

  test('should handle network errors gracefully', async ({ page }) => {
    // Simulate network error by going offline
    await page.context().setOffline(true);
    
    // Try to create a scenario
    await page.click('button:has-text("Create New Scenario")');
    await page.waitForSelector('h4:has-text("Create New Scenario")');
    
    // Fill form and try to save
    await page.fill('input[placeholder*="scenario name"]', 'Network Error Test');
    await page.fill('input[type="number"]:nth-of-type(1)', '2025');
    await page.fill('input[type="number"]:nth-of-type(2)', '2026');
    await page.click('input[type="radio"][value="group"]');
    await page.click('button:has-text("Next: Configure Levers")');
    
    await page.waitForSelector('h4:has-text("Configure Levers")', { timeout: 10000 });
    await page.click('button:has-text("Save Scenario")');
    
    // Should show error message
    await expect(page.locator('text=Failed to create scenario')).toBeVisible();
    
    // Go back online
    await page.context().setOffline(false);
  });

  test('should validate form inputs properly', async ({ page }) => {
    // Click create new scenario button
    await page.click('button:has-text("Create New Scenario")');
    await page.waitForSelector('h4:has-text("Create New Scenario")');
    
    // Test empty name
    await page.click('button:has-text("Next: Configure Levers")');
    await expect(page.locator('.ant-form-item-explain-error')).toBeVisible();
    
    // Test invalid year range (end before start)
    await page.fill('input[placeholder*="scenario name"]', 'Invalid Date Test');
    await page.fill('input[type="number"]:nth-of-type(1)', '2027'); // Start year
    await page.fill('input[type="number"]:nth-of-type(2)', '2025'); // End year (before start)
    await page.click('button:has-text("Next: Configure Levers")');
    
    // Should show validation error
    await expect(page.locator('text=End date must be after start date')).toBeVisible();
    
    // Test individual office selection without selecting offices
    await page.fill('input[type="number"]:nth-of-type(1)', '2025');
    await page.fill('input[type="number"]:nth-of-type(2)', '2027');
    await page.click('input[type="radio"][value="individual"]');
    await page.click('button:has-text("Next: Configure Levers")');
    
    // Should show validation error for office selection
    await expect(page.locator('text=Select at least one office')).toBeVisible();
  });

  test('should handle invalid lever configurations', async ({ page }) => {
    // Create scenario and go to lever configuration
    await page.click('button:has-text("Create New Scenario")');
    await page.waitForSelector('h4:has-text("Create New Scenario")');
    
    await page.fill('input[placeholder*="scenario name"]', 'Invalid Lever Test');
    await page.fill('input[type="number"]:nth-of-type(1)', '2025');
    await page.fill('input[type="number"]:nth-of-type(2)', '2026');
    await page.click('input[type="radio"][value="group"]');
    await page.click('button:has-text("Next: Configure Levers")');
    
    await page.waitForSelector('h4:has-text("Configure Levers")', { timeout: 10000 });
    
    // Try to set invalid recruitment rate (negative)
    await page.click('text=Stockholm');
    await page.click('text=Consultant');
    await page.click('text=A');
    await page.fill('input[placeholder*="recruitment rate"]', '-0.1');
    
    // Should show validation error
    await expect(page.locator('text=Recruitment rate must be positive')).toBeVisible();
    
    // Try to set invalid churn rate (> 1)
    await page.fill('input[placeholder*="churn rate"]', '1.5');
    
    // Should show validation error
    await expect(page.locator('text=Churn rate must be between 0 and 1')).toBeVisible();
  });

  test('should handle concurrent scenario operations', async ({ page }) => {
    // Create a scenario first
    await page.click('button:has-text("Create New Scenario")');
    await page.waitForSelector('h4:has-text("Create New Scenario")');
    
    await page.fill('input[placeholder*="scenario name"]', 'Concurrent Test');
    await page.fill('input[type="number"]:nth-of-type(1)', '2025');
    await page.fill('input[type="number"]:nth-of-type(2)', '2026');
    await page.click('input[type="radio"][value="group"]');
    await page.click('button:has-text("Next: Configure Levers")');
    
    await page.waitForSelector('h4:has-text("Configure Levers")', { timeout: 10000 });
    await page.click('button:has-text("Save Scenario")');
    await page.waitForSelector('text=Scenario created successfully', { timeout: 15000 });
    
    // Try to edit the same scenario from multiple places
    const editButtons = page.locator('button:has-text("Edit")');
    if (await editButtons.count() > 0) {
      // Click edit button
      await editButtons.first().click();
      await page.waitForSelector('h4:has-text("Edit Scenario")', { timeout: 10000 });
      
      // Try to click edit again (should be disabled or show warning)
      await page.goBack();
      await page.waitForSelector('h2:has-text("Scenario Runner")');
      
      // Try to edit again
      await editButtons.first().click();
      
      // Should handle gracefully (either show warning or allow edit)
      await expect(page.locator('h4:has-text("Edit Scenario")')).toBeVisible();
    }
  });

  test('should handle large data sets', async ({ page }) => {
    // Create scenario with many offices
    await page.click('button:has-text("Create New Scenario")');
    await page.waitForSelector('h4:has-text("Create New Scenario")');
    
    await page.fill('input[placeholder*="scenario name"]', 'Large Dataset Test');
    await page.fill('input[type="number"]:nth-of-type(1)', '2025');
    await page.fill('input[type="number"]:nth-of-type(2)', '2030'); // Long time range
    await page.click('input[type="radio"][value="individual"]');
    
    // Select many offices
    await page.waitForSelector('select[placeholder*="Choose offices"]');
    await page.selectOption('select[placeholder*="Choose offices"]', [
      'Stockholm', 'Munich', 'Amsterdam', 'Berlin', 'Copenhagen', 
      'Frankfurt', 'Hamburg', 'Helsinki', 'Oslo', 'Zurich'
    ]);
    
    await page.click('button:has-text("Next: Configure Levers")');
    await page.waitForSelector('h4:has-text("Configure Levers")', { timeout: 10000 });
    
    // Configure levers for multiple offices
    const offices = ['Stockholm', 'Munich', 'Amsterdam'];
    for (const office of offices) {
      await page.click(`text=${office}`);
      await page.click('text=Consultant');
      await page.click('text=A');
      await page.fill('input[placeholder*="recruitment rate"]', '0.05');
      await page.fill('input[placeholder*="churn rate"]', '0.02');
    }
    
    // Save should work without performance issues
    await page.click('button:has-text("Save Scenario")');
    await page.waitForSelector('text=Scenario created successfully', { timeout: 30000 });
  });

  test('should handle scenario deletion with dependencies', async ({ page }) => {
    // Wait for scenarios to load
    await page.waitForSelector('table', { timeout: 10000 });
    
    // Try to delete a scenario that might have results
    const deleteButton = page.locator('button:has-text("Delete")').first();
    
    if (await deleteButton.isVisible()) {
      await deleteButton.click();
      
      // Should show confirmation dialog
      await page.waitForSelector('.ant-popconfirm');
      
      // Check if there's a warning about dependencies
      const warningText = page.locator('.ant-popconfirm-message');
      if (await warningText.isVisible()) {
        const warning = await warningText.textContent();
        console.log('Deletion warning:', warning);
      }
      
      // Confirm deletion
      await page.click('button:has-text("Yes")');
      
      // Should handle gracefully (either delete or show error)
      try {
        await page.waitForSelector('text=Scenario deleted successfully', { timeout: 10000 });
      } catch {
        // If deletion fails due to dependencies, should show appropriate error
        await expect(page.locator('text=Cannot delete scenario')).toBeVisible();
      }
    }
  });

  test('should handle malformed scenario data', async ({ page }) => {
    // This test would require backend API testing
    // For now, test that the UI handles API errors gracefully
    
    // Try to access a non-existent scenario
    await page.goto('/scenario-runner/non-existent-id');
    
    // Should show 404 or error page
    await expect(page.locator('text=Scenario not found')).toBeVisible();
  });

  test('should handle browser refresh during scenario creation', async ({ page }) => {
    // Start creating a scenario
    await page.click('button:has-text("Create New Scenario")');
    await page.waitForSelector('h4:has-text("Create New Scenario")');
    
    // Fill some data
    await page.fill('input[placeholder*="scenario name"]', 'Refresh Test');
    await page.fill('input[type="number"]:nth-of-type(1)', '2025');
    await page.fill('input[type="number"]:nth-of-type(2)', '2026');
    
    // Refresh the page
    await page.reload();
    
    // Should handle gracefully (either show warning or redirect)
    await expect(page.locator('h2:has-text("Scenario Runner")')).toBeVisible();
  });

  test('should handle slow network conditions', async ({ page }) => {
    // Simulate slow network
    await page.route('**/*', route => {
      // Add delay to all requests
      setTimeout(() => route.continue(), 2000);
    });
    
    // Try to create a scenario
    await page.click('button:has-text("Create New Scenario")');
    await page.waitForSelector('h4:has-text("Create New Scenario")');
    
    await page.fill('input[placeholder*="scenario name"]', 'Slow Network Test');
    await page.fill('input[type="number"]:nth-of-type(1)', '2025');
    await page.fill('input[type="number"]:nth-of-type(2)', '2026');
    await page.click('input[type="radio"][value="group"]');
    await page.click('button:has-text("Next: Configure Levers")');
    
    // Should show loading state
    await expect(page.locator('.ant-spin')).toBeVisible();
    
    // Wait for completion
    await page.waitForSelector('h4:has-text("Configure Levers")', { timeout: 30000 });
  });
}); 