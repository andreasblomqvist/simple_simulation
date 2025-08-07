/**
 * End-to-end tests for population snapshot workflows
 * Tests complete user journeys from snapshot creation to analysis
 */

import { test, expect, Page } from '@playwright/test';

test.describe('Population Snapshot Workflows', () => {
  let page: Page;

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
    
    // Start servers if needed
    // await page.goto('http://localhost:3000');
    await page.goto('/');
    
    // Wait for app to load
    await page.waitForLoadState('networkidle');
  });

  test.afterEach(async () => {
    await page.close();
  });

  test.describe('Snapshot Creation Workflows', () => {
    test('creates snapshot from current workforce', async () => {
      // Navigate to office management
      await page.click('[data-testid="nav-offices"]');
      await page.waitForSelector('[data-testid="office-card"]');
      
      // Select first office
      await page.click('[data-testid="office-card"]:first-child');
      await page.waitForSelector('[data-testid="office-overview"]');
      
      // Open snapshot manager
      await page.click('[data-testid="create-snapshot-button"]');
      await page.waitForSelector('[data-testid="snapshot-modal"]');
      
      // Fill snapshot form
      await page.fill('[data-testid="snapshot-name-input"]', 'E2E Test Snapshot');
      await page.fill('[data-testid="snapshot-description-input"]', 'Created via E2E test');
      await page.fill('[data-testid="snapshot-tags-input"]', 'e2e, test, current');
      
      // Create snapshot
      await page.click('[data-testid="create-snapshot-submit"]');
      
      // Wait for creation to complete
      await page.waitForSelector('[data-testid="snapshot-success-message"]');
      await expect(page.locator('[data-testid="snapshot-success-message"]')).toContainText('Snapshot created successfully');
      
      // Verify snapshot appears in list
      await page.click('[data-testid="close-modal"]');
      await page.waitForSelector('[data-testid="snapshot-list"]');
      await expect(page.locator('[data-testid="snapshot-item"]').first()).toContainText('E2E Test Snapshot');
    });

    test('validates snapshot creation form', async () => {
      // Navigate to create snapshot
      await page.click('[data-testid="nav-offices"]');
      await page.click('[data-testid="office-card"]:first-child');
      await page.click('[data-testid="create-snapshot-button"]');
      
      // Try to submit empty form
      await page.click('[data-testid="create-snapshot-submit"]');
      
      // Check validation messages
      await expect(page.locator('[data-testid="error-snapshot-name"]')).toContainText('Name is required');
      
      // Fill invalid data
      await page.fill('[data-testid="snapshot-name-input"]', 'x'.repeat(201)); // Too long
      await page.click('[data-testid="create-snapshot-submit"]');
      
      await expect(page.locator('[data-testid="error-snapshot-name"]')).toContainText('Name is too long');
    });

    test('creates snapshot with different sources', async () => {
      // Test creating from simulation results
      await page.goto('/scenarios');
      await page.waitForSelector('[data-testid="scenario-list"]');
      
      // Run a scenario first
      await page.click('[data-testid="create-scenario-button"]');
      await page.fill('[data-testid="scenario-name-input"]', 'Test Scenario for Snapshot');
      await page.selectOption('[data-testid="scenario-office-select"]', { index: 0 });
      await page.click('[data-testid="scenario-submit"]');
      
      await page.waitForSelector('[data-testid="scenario-results"]');
      
      // Create snapshot from results
      await page.click('[data-testid="create-snapshot-from-results"]');
      await page.fill('[data-testid="snapshot-name-input"]', 'Simulation Snapshot');
      await page.selectOption('[data-testid="snapshot-date-select"]', '202506'); // June 2025
      
      await page.click('[data-testid="create-snapshot-submit"]');
      await expect(page.locator('[data-testid="snapshot-success-message"]')).toBeVisible();
    });
  });

  test.describe('Snapshot Management Workflows', () => {
    test('updates snapshot information', async () => {
      // Navigate to snapshots
      await page.goto('/snapshots');
      await page.waitForSelector('[data-testid="snapshot-list"]');
      
      // Select first snapshot
      await page.click('[data-testid="snapshot-item"]:first-child');
      await page.waitForSelector('[data-testid="snapshot-details"]');
      
      // Edit snapshot
      await page.click('[data-testid="edit-snapshot-button"]');
      await page.waitForSelector('[data-testid="edit-snapshot-modal"]');
      
      // Update fields
      const newName = 'Updated Snapshot Name';
      await page.fill('[data-testid="snapshot-name-input"]', newName);
      await page.fill('[data-testid="snapshot-description-input"]', 'Updated description');
      
      // Save changes
      await page.click('[data-testid="save-snapshot-button"]');
      await page.waitForSelector('[data-testid="snapshot-success-message"]');
      
      // Verify changes
      await page.click('[data-testid="close-modal"]');
      await expect(page.locator('[data-testid="snapshot-name"]')).toContainText(newName);
    });

    test('sets default snapshot', async () => {
      // Navigate to office with snapshots
      await page.goto('/offices');
      await page.click('[data-testid="office-card"]:first-child');
      
      // View snapshots tab
      await page.click('[data-testid="snapshots-tab"]');
      await page.waitForSelector('[data-testid="snapshot-list"]');
      
      // Set second snapshot as default
      await page.click('[data-testid="snapshot-menu"]:nth-child(2)');
      await page.click('[data-testid="set-default-option"]');
      
      // Confirm action
      await page.click('[data-testid="confirm-set-default"]');
      await expect(page.locator('[data-testid="success-message"]')).toContainText('Default snapshot updated');
      
      // Verify default indicator
      await expect(page.locator('[data-testid="snapshot-item"]:nth-child(2) [data-testid="default-badge"]')).toBeVisible();
    });

    test('deletes snapshot with confirmation', async () => {
      // Navigate to snapshots
      await page.goto('/snapshots');
      await page.waitForSelector('[data-testid="snapshot-list"]');
      
      const initialCount = await page.locator('[data-testid="snapshot-item"]').count();
      
      // Delete snapshot
      await page.click('[data-testid="snapshot-menu"]:first-child');
      await page.click('[data-testid="delete-option"]');
      
      // Confirm deletion
      await page.waitForSelector('[data-testid="delete-confirmation"]');
      await expect(page.locator('[data-testid="delete-confirmation"]')).toContainText('permanently delete');
      
      await page.click('[data-testid="confirm-delete"]');
      await page.waitForSelector('[data-testid="success-message"]');
      
      // Verify snapshot was deleted
      const finalCount = await page.locator('[data-testid="snapshot-item"]').count();
      expect(finalCount).toBe(initialCount - 1);
    });

    test('prevents deletion of default snapshot', async () => {
      // Navigate to office with default snapshot
      await page.goto('/offices');
      await page.click('[data-testid="office-card"]:first-child');
      await page.click('[data-testid="snapshots-tab"]');
      
      // Try to delete default snapshot
      await page.click('[data-testid="default-snapshot"] [data-testid="snapshot-menu"]');
      
      // Delete option should be disabled or show warning
      const deleteOption = page.locator('[data-testid="delete-option"]');
      if (await deleteOption.isVisible()) {
        await deleteOption.click();
        await expect(page.locator('[data-testid="error-message"]')).toContainText('Cannot delete default snapshot');
      } else {
        expect(await deleteOption.isDisabled()).toBe(true);
      }
    });
  });

  test.describe('Snapshot Comparison Workflows', () => {
    test('compares two snapshots', async () => {
      // Navigate to snapshots
      await page.goto('/snapshots');
      await page.waitForSelector('[data-testid="snapshot-list"]');
      
      // Ensure we have at least 2 snapshots
      const snapshotCount = await page.locator('[data-testid="snapshot-item"]').count();
      if (snapshotCount < 2) {
        test.skip('Need at least 2 snapshots for comparison test');
      }
      
      // Start comparison
      await page.click('[data-testid="compare-snapshots-button"]');
      await page.waitForSelector('[data-testid="comparison-modal"]');
      
      // Select baseline snapshot
      await page.selectOption('[data-testid="baseline-snapshot-select"]', { index: 0 });
      
      // Select comparison snapshot
      await page.selectOption('[data-testid="comparison-snapshot-select"]', { index: 1 });
      
      // Run comparison
      await page.click('[data-testid="run-comparison-button"]');
      await page.waitForSelector('[data-testid="comparison-results"]');
      
      // Verify comparison results
      await expect(page.locator('[data-testid="comparison-summary"]')).toBeVisible();
      await expect(page.locator('[data-testid="workforce-changes"]')).toBeVisible();
      await expect(page.locator('[data-testid="fte-delta"]')).toBeVisible();
      
      // Check insights
      const insights = page.locator('[data-testid="comparison-insights"] li');
      expect(await insights.count()).toBeGreaterThan(0);
    });

    test('handles invalid snapshot comparison', async () => {
      // Try to compare snapshot with itself
      await page.goto('/snapshots');
      await page.click('[data-testid="compare-snapshots-button"]');
      
      // Select same snapshot for both
      await page.selectOption('[data-testid="baseline-snapshot-select"]', { index: 0 });
      await page.selectOption('[data-testid="comparison-snapshot-select"]', { index: 0 });
      
      await page.click('[data-testid="run-comparison-button"]');
      
      // Should show error message
      await expect(page.locator('[data-testid="error-message"]')).toContainText('Cannot compare snapshot with itself');
    });

    test('exports comparison results', async () => {
      // Complete a comparison first
      await page.goto('/snapshots');
      await page.click('[data-testid="compare-snapshots-button"]');
      
      await page.selectOption('[data-testid="baseline-snapshot-select"]', { index: 0 });
      await page.selectOption('[data-testid="comparison-snapshot-select"]', { index: 1 });
      await page.click('[data-testid="run-comparison-button"]');
      
      await page.waitForSelector('[data-testid="comparison-results"]');
      
      // Export results
      const downloadPromise = page.waitForEvent('download');
      await page.click('[data-testid="export-comparison-button"]');
      const download = await downloadPromise;
      
      expect(download.suggestedFilename()).toMatch(/comparison.*\.csv/);
    });
  });

  test.describe('Snapshot Integration Workflows', () => {
    test('uses snapshot in scenario planning', async () => {
      // Navigate to scenarios
      await page.goto('/scenarios');
      await page.click('[data-testid="create-scenario-button"]');
      
      // Fill scenario form
      await page.fill('[data-testid="scenario-name-input"]', 'Test Scenario with Snapshot');
      await page.selectOption('[data-testid="scenario-office-select"]', { index: 0 });
      
      // Select a snapshot as baseline
      await page.click('[data-testid="use-snapshot-baseline"]');
      await page.waitForSelector('[data-testid="snapshot-selector"]');
      
      await page.selectOption('[data-testid="baseline-snapshot-select"]', { index: 0 });
      
      // Configure scenario parameters
      await page.fill('[data-testid="scenario-duration-input"]', '12');
      await page.selectOption('[data-testid="scenario-type-select"]', 'growth');
      
      // Run scenario
      await page.click('[data-testid="run-scenario-button"]');
      await page.waitForSelector('[data-testid="scenario-results"]');
      
      // Verify results include baseline information
      await expect(page.locator('[data-testid="baseline-info"]')).toBeVisible();
      await expect(page.locator('[data-testid="baseline-info"]')).toContainText('snapshot');
    });

    test('uses snapshot in business planning', async () => {
      // Navigate to business planning
      await page.goto('/business-planning');
      await page.waitForLoadState('networkidle');
      
      // Create new business plan
      await page.click('[data-testid="create-plan-button"]');
      await page.fill('[data-testid="plan-name-input"]', 'Plan with Snapshot Baseline');
      
      // Set snapshot as starting point
      await page.click('[data-testid="use-snapshot-baseline"]');
      await page.selectOption('[data-testid="baseline-snapshot-select"]', { index: 0 });
      
      // Configure plan parameters
      await page.fill('[data-testid="plan-duration-input"]', '24');
      await page.click('[data-testid="save-plan-button"]');
      
      // Verify plan uses snapshot data
      await page.waitForSelector('[data-testid="plan-baseline-info"]');
      await expect(page.locator('[data-testid="plan-baseline-info"]')).toContainText('Based on snapshot');
    });

    test('creates snapshot from business plan', async () => {
      // Navigate to existing business plan
      await page.goto('/business-planning');
      await page.click('[data-testid="plan-item"]:first-child');
      
      // Navigate to specific month
      await page.click('[data-testid="month-tab"][data-month="202506"]');
      
      // Create snapshot from current plan state
      await page.click('[data-testid="create-snapshot-from-plan"]');
      await page.waitForSelector('[data-testid="snapshot-modal"]');
      
      await page.fill('[data-testid="snapshot-name-input"]', 'June 2025 Plan Snapshot');
      await page.fill('[data-testid="snapshot-description-input"]', 'Captured from business plan');
      
      await page.click('[data-testid="create-snapshot-submit"]');
      await expect(page.locator('[data-testid="snapshot-success-message"]')).toBeVisible();
    });
  });

  test.describe('Snapshot Data Validation Workflows', () => {
    test('displays workforce data accurately', async () => {
      // Navigate to snapshot details
      await page.goto('/snapshots');
      await page.click('[data-testid="snapshot-item"]:first-child');
      
      // Verify workforce table
      await page.waitForSelector('[data-testid="workforce-table"]');
      
      // Check table headers
      await expect(page.locator('[data-testid="table-header-role"]')).toBeVisible();
      await expect(page.locator('[data-testid="table-header-level"]')).toBeVisible();
      await expect(page.locator('[data-testid="table-header-fte"]')).toBeVisible();
      
      // Check data rows
      const rows = page.locator('[data-testid="workforce-row"]');
      expect(await rows.count()).toBeGreaterThan(0);
      
      // Verify FTE totals
      const totalFTE = await page.locator('[data-testid="total-fte"]').textContent();
      expect(totalFTE).toMatch(/\d+\.\d/); // Should be a decimal number
    });

    test('validates FTE calculations', async () => {
      // Navigate to snapshot with known data
      await page.goto('/snapshots');
      await page.click('[data-testid="snapshot-item"]:first-child');
      
      // Get individual FTE values
      const fteValues = await page.locator('[data-testid="fte-value"]').allTextContents();
      const individualTotal = fteValues
        .map(val => parseFloat(val.replace(/[^\d.]/g, '')))
        .reduce((sum, val) => sum + val, 0);
      
      // Get displayed total
      const displayedTotal = await page.locator('[data-testid="total-fte"]').textContent();
      const calculatedTotal = parseFloat(displayedTotal.replace(/[^\d.]/g, ''));
      
      // Verify calculations match
      expect(Math.abs(individualTotal - calculatedTotal)).toBeLessThan(0.1);
    });

    test('handles empty workforce data', async () => {
      // Create snapshot with no workforce (edge case)
      await page.goto('/offices');
      await page.click('[data-testid="office-card"]:last-child'); // Assume last office might be empty
      
      await page.click('[data-testid="create-snapshot-button"]');
      await page.fill('[data-testid="snapshot-name-input"]', 'Empty Workforce Test');
      
      await page.click('[data-testid="create-snapshot-submit"]');
      
      // Should handle gracefully
      if (await page.locator('[data-testid="empty-workforce-message"]').isVisible()) {
        await expect(page.locator('[data-testid="empty-workforce-message"]')).toContainText('No workforce data');
      }
    });
  });

  test.describe('Snapshot Search and Filtering', () => {
    test('searches snapshots by name', async () => {
      // Navigate to snapshots
      await page.goto('/snapshots');
      await page.waitForSelector('[data-testid="snapshot-list"]');
      
      const initialCount = await page.locator('[data-testid="snapshot-item"]').count();
      
      // Search for specific snapshot
      await page.fill('[data-testid="search-snapshots-input"]', 'Test');
      await page.press('[data-testid="search-snapshots-input"]', 'Enter');
      
      await page.waitForTimeout(1000); // Wait for search
      
      const filteredCount = await page.locator('[data-testid="snapshot-item"]').count();
      expect(filteredCount).toBeLessThanOrEqual(initialCount);
      
      // Verify all results contain search term
      const snapshotNames = await page.locator('[data-testid="snapshot-name"]').allTextContents();
      snapshotNames.forEach(name => {
        expect(name.toLowerCase()).toContain('test');
      });
    });

    test('filters snapshots by tags', async () => {
      // Navigate and apply tag filter
      await page.goto('/snapshots');
      await page.click('[data-testid="filter-by-tags-button"]');
      
      // Select a tag
      await page.click('[data-testid="tag-filter-quarterly"]');
      await page.click('[data-testid="apply-filters-button"]');
      
      // Verify filtered results
      await page.waitForSelector('[data-testid="filtered-results"]');
      const snapshots = page.locator('[data-testid="snapshot-item"]');
      
      for (let i = 0; i < await snapshots.count(); i++) {
        const tags = snapshots.nth(i).locator('[data-testid="snapshot-tags"]');
        await expect(tags).toContainText('quarterly');
      }
    });

    test('filters snapshots by date range', async () => {
      // Navigate and set date filter
      await page.goto('/snapshots');
      await page.click('[data-testid="filter-by-date-button"]');
      
      // Set date range
      await page.fill('[data-testid="date-from-input"]', '2025-01-01');
      await page.fill('[data-testid="date-to-input"]', '2025-06-30');
      await page.click('[data-testid="apply-date-filter"]');
      
      // Verify all snapshots fall within range
      const snapshotDates = await page.locator('[data-testid="snapshot-date"]').allTextContents();
      snapshotDates.forEach(dateStr => {
        const date = new Date(dateStr);
        expect(date.getTime()).toBeGreaterThanOrEqual(new Date('2025-01-01').getTime());
        expect(date.getTime()).toBeLessThanOrEqual(new Date('2025-06-30').getTime());
      });
    });

    test('combines multiple filters', async () => {
      await page.goto('/snapshots');
      
      // Apply search
      await page.fill('[data-testid="search-snapshots-input"]', 'Quarterly');
      
      // Apply tag filter
      await page.click('[data-testid="filter-by-tags-button"]');
      await page.click('[data-testid="tag-filter-approved"]');
      await page.click('[data-testid="apply-filters-button"]');
      
      // Apply office filter
      await page.selectOption('[data-testid="office-filter-select"]', { index: 0 });
      
      // Verify combined filtering works
      await page.waitForSelector('[data-testid="filtered-results"]');
      const results = page.locator('[data-testid="snapshot-item"]');
      
      // Each result should match all filters
      for (let i = 0; i < await results.count(); i++) {
        const name = await results.nth(i).locator('[data-testid="snapshot-name"]').textContent();
        expect(name.toLowerCase()).toContain('quarterly');
        
        const tags = await results.nth(i).locator('[data-testid="snapshot-tags"]').textContent();
        expect(tags).toContain('approved');
      }
    });

    test('clears all filters', async () => {
      await page.goto('/snapshots');
      
      // Apply filters
      await page.fill('[data-testid="search-snapshots-input"]', 'Test');
      await page.click('[data-testid="filter-by-tags-button"]');
      await page.click('[data-testid="tag-filter-quarterly"]');
      await page.click('[data-testid="apply-filters-button"]');
      
      const filteredCount = await page.locator('[data-testid="snapshot-item"]').count();
      
      // Clear all filters
      await page.click('[data-testid="clear-all-filters"]');
      await page.waitForSelector('[data-testid="all-snapshots-loaded"]');
      
      const unfilteredCount = await page.locator('[data-testid="snapshot-item"]').count();
      expect(unfilteredCount).toBeGreaterThanOrEqual(filteredCount);
    });
  });

  test.describe('Error Handling and Recovery', () => {
    test('handles network errors gracefully', async () => {
      // Intercept API calls to simulate network error
      await page.route('/api/snapshots', route => {
        route.abort('failed');
      });
      
      await page.goto('/snapshots');
      
      // Should show error message
      await expect(page.locator('[data-testid="network-error"]')).toBeVisible();
      await expect(page.locator('[data-testid="retry-button"]')).toBeVisible();
      
      // Remove route interception and retry
      await page.unroute('/api/snapshots');
      await page.click('[data-testid="retry-button"]');
      
      // Should load successfully
      await page.waitForSelector('[data-testid="snapshot-list"]');
    });

    test('recovers from API errors', async () => {
      // Simulate server error
      await page.route('/api/snapshots', route => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Internal server error' })
        });
      });
      
      await page.goto('/snapshots');
      await expect(page.locator('[data-testid="error-message"]')).toContainText('Internal server error');
      
      // Fix the route and retry
      await page.unroute('/api/snapshots');
      await page.reload();
      
      await page.waitForSelector('[data-testid="snapshot-list"]');
    });

    test('handles concurrent operations', async () => {
      // Navigate to snapshot
      await page.goto('/snapshots');
      await page.click('[data-testid="snapshot-item"]:first-child');
      
      // Start two concurrent edits (simulate race condition)
      await page.click('[data-testid="edit-snapshot-button"]');
      await page.fill('[data-testid="snapshot-name-input"]', 'Concurrent Edit 1');
      
      // Open second tab with same snapshot
      const page2 = await page.context().newPage();
      await page2.goto(page.url());
      await page2.click('[data-testid="edit-snapshot-button"]');
      await page2.fill('[data-testid="snapshot-name-input"]', 'Concurrent Edit 2');
      
      // Save both
      await page.click('[data-testid="save-snapshot-button"]');
      await page2.click('[data-testid="save-snapshot-button"]');
      
      // One should succeed, one should show conflict message
      const success1 = await page.locator('[data-testid="success-message"]').isVisible();
      const error2 = await page2.locator('[data-testid="conflict-error"]').isVisible();
      
      expect(success1 || error2).toBe(true);
      
      await page2.close();
    });
  });

  test.describe('Performance and Load Testing', () => {
    test('handles large snapshot lists efficiently', async () => {
      // Navigate to snapshots page
      await page.goto('/snapshots');
      
      // Measure initial load time
      const startTime = Date.now();
      await page.waitForSelector('[data-testid="snapshot-list"]');
      const loadTime = Date.now() - startTime;
      
      // Should load within reasonable time (adjust threshold as needed)
      expect(loadTime).toBeLessThan(5000); // 5 seconds
      
      // Check that pagination works with large datasets
      if (await page.locator('[data-testid="pagination"]').isVisible()) {
        await page.click('[data-testid="next-page"]');
        await page.waitForSelector('[data-testid="snapshot-list"]');
        
        // Should load next page quickly
        const pageLoadStart = Date.now();
        await page.click('[data-testid="next-page"]');
        await page.waitForSelector('[data-testid="snapshot-list"]');
        const pageLoadTime = Date.now() - pageLoadStart;
        
        expect(pageLoadTime).toBeLessThan(2000); // 2 seconds for page navigation
      }
    });

    test('handles rapid user interactions', async () => {
      await page.goto('/snapshots');
      await page.waitForSelector('[data-testid="snapshot-list"]');
      
      // Rapidly click through multiple snapshots
      const snapshots = page.locator('[data-testid="snapshot-item"]');
      const count = Math.min(5, await snapshots.count());
      
      for (let i = 0; i < count; i++) {
        await snapshots.nth(i).click();
        // Don't wait for full load, just check basic UI response
        await expect(page.locator('[data-testid="snapshot-details"]')).toBeVisible();
      }
      
      // UI should remain responsive
      await expect(page.locator('[data-testid="loading-spinner"]')).not.toBeVisible();
    });
  });

  test.describe('Accessibility and Usability', () => {
    test('supports keyboard navigation', async () => {
      await page.goto('/snapshots');
      await page.waitForSelector('[data-testid="snapshot-list"]');
      
      // Tab through snapshot items
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      
      // Should be able to select with Enter
      await page.keyboard.press('Enter');
      await expect(page.locator('[data-testid="snapshot-details"]')).toBeVisible();
      
      // Tab to action buttons
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      
      // Should be able to trigger actions with Enter/Space
      await page.keyboard.press('Enter');
    });

    test('provides proper aria labels and roles', async () => {
      await page.goto('/snapshots');
      
      // Check for proper semantic elements
      await expect(page.locator('[role="main"]')).toBeVisible();
      await expect(page.locator('[role="navigation"]')).toBeVisible();
      
      // Check aria labels on interactive elements
      const searchInput = page.locator('[data-testid="search-snapshots-input"]');
      await expect(searchInput).toHaveAttribute('aria-label');
      
      // Check table accessibility
      await page.click('[data-testid="snapshot-item"]:first-child');
      const table = page.locator('[data-testid="workforce-table"]');
      await expect(table).toHaveAttribute('role', 'table');
    });

    test('maintains focus management in modals', async () => {
      await page.goto('/snapshots');
      await page.click('[data-testid="create-snapshot-button"]');
      
      // Focus should be in the modal
      const modal = page.locator('[data-testid="snapshot-modal"]');
      await expect(modal).toBeVisible();
      
      // First input should be focused
      const nameInput = page.locator('[data-testid="snapshot-name-input"]');
      await expect(nameInput).toBeFocused();
      
      // Escape should close modal
      await page.keyboard.press('Escape');
      await expect(modal).not.toBeVisible();
      
      // Focus should return to trigger button
      await expect(page.locator('[data-testid="create-snapshot-button"]')).toBeFocused();
    });

    test('provides clear visual feedback for actions', async () => {
      await page.goto('/snapshots');
      await page.click('[data-testid="snapshot-item"]:first-child');
      
      // Edit action should show loading state
      await page.click('[data-testid="edit-snapshot-button"]');
      await page.fill('[data-testid="snapshot-name-input"]', 'Updated Name');
      
      const saveButton = page.locator('[data-testid="save-snapshot-button"]');
      await saveButton.click();
      
      // Button should show loading state
      await expect(saveButton).toHaveAttribute('disabled');
      await expect(page.locator('[data-testid="saving-indicator"]')).toBeVisible();
      
      // Success message should appear
      await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    });
  });
});