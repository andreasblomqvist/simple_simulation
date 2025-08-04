/**
 * End-to-end tests for Office Management functionality
 * Tests complete user workflows including navigation, office selection, and management
 */
import { test, expect, Page } from '@playwright/test';

// Test configuration
// Use baseURL from Playwright config instead of hardcoded URL
const FRONTEND_URL = '';
const BACKEND_URL = 'http://localhost:8000';

// Helper functions
async function waitForOfficesLoad(page: Page) {
  // Wait for offices to load by checking for known office names
  await page.waitForSelector('text=Stockholm', { timeout: 10000 });
}

async function navigateToOffices(page: Page) {
  await page.goto(`${FRONTEND_URL}/offices`);
  await waitForOfficesLoad(page);
}

async function mockOfficesAPI(page: Page) {
  // Mock the offices API for consistent testing
  await page.route('**/api/offices', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 'stockholm',
          name: 'Stockholm',
          journey: 'mature',
          timezone: 'Europe/Stockholm',
          economic_parameters: {
            cost_of_living: 1.0,
            market_multiplier: 1.0,
            tax_rate: 0.25,
          },
          total_fte: 679,
          roles: {
            Consultant: {
              A: { fte: 69 },
              AC: { fte: 54 },
              C: { fte: 123 },
            },
          },
        },
        {
          id: 'munich',
          name: 'Munich',
          journey: 'established',
          timezone: 'Europe/Berlin',
          economic_parameters: {
            cost_of_living: 1.1,
            market_multiplier: 1.2,
            tax_rate: 0.28,
          },
          total_fte: 332,
          roles: {
            Consultant: {
              A: { fte: 18 },
              AC: { fte: 32 },
              C: { fte: 61 },
            },
          },
        },
      ]),
    });
  });
}

test.describe('Office Management E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Set up API mocking for consistent test environment
    await mockOfficesAPI(page);
  });

  test.describe('Office List Page', () => {
    test('should display list of offices with correct information', async ({ page }) => {
      await navigateToOffices(page);

      // Check page title
      await expect(page.locator('text=All Offices')).toBeVisible();

      // Check office names are displayed
      await expect(page.locator('text=Stockholm')).toBeVisible();
      await expect(page.locator('text=Munich')).toBeVisible();

      // Check FTE numbers
      await expect(page.locator('text=679')).toBeVisible();
      await expect(page.locator('text=332')).toBeVisible();

      // Check journey tags
      await expect(page.locator('text=mature')).toBeVisible();
      await expect(page.locator('text=established')).toBeVisible();

      // Check economic parameters
      await expect(page.locator('text=1.00')).toBeVisible(); // Stockholm cost of living
      await expect(page.locator('text=1.10')).toBeVisible(); // Munich cost of living
    });

    test('should show filter controls', async ({ page }) => {
      await navigateToOffices(page);

      // Check filter dropdowns are present
      const companyFilter = page.locator('.ant-select').filter({ hasText: 'Company' });
      const journeyFilter = page.locator('.ant-select').filter({ hasText: 'Journey' });
      const sortFilter = page.locator('.ant-select').filter({ hasText: 'Sort: Name' });

      await expect(companyFilter).toBeVisible();
      await expect(journeyFilter).toBeVisible();
      await expect(sortFilter).toBeVisible();
    });

    test('should expand office row to show role breakdown', async ({ page }) => {
      await navigateToOffices(page);

      // Find and click the expand button for the first row
      const expandButton = page.locator('.ant-table-row-expand-icon').first();
      await expandButton.click();

      // Check if role breakdown is shown
      await expect(page.locator('text=Role Breakdown')).toBeVisible();
      await expect(page.locator('text=Consultant')).toBeVisible();
      await expect(page.locator('text=A: 69 FTE')).toBeVisible();
      await expect(page.locator('text=AC: 54 FTE')).toBeVisible();
    });

    test('should handle pagination correctly', async ({ page }) => {
      await navigateToOffices(page);

      // Check pagination exists
      const pagination = page.locator('.ant-pagination');
      await expect(pagination).toBeVisible();

      // With only 2 offices, should be on page 1
      const currentPage = page.locator('.ant-pagination-item-active');
      await expect(currentPage).toContainText('1');
    });
  });

  test.describe('Office Navigation', () => {
    test('should navigate to office detail page when office name is clicked', async ({ page }) => {
      await navigateToOffices(page);

      // Click on Stockholm office name
      const stockholmLink = page.locator('text=Stockholm').first();
      await expect(stockholmLink).toBeVisible();
      await stockholmLink.click();

      // Check URL changed to office detail page
      await expect(page).toHaveURL(`${FRONTEND_URL}/offices/stockholm`);
    });

    test('should navigate to Munich office correctly', async ({ page }) => {
      await navigateToOffices(page);

      // Click on Munich office name
      const munichLink = page.locator('text=Munich').first();
      await munichLink.click();

      // Check URL changed
      await expect(page).toHaveURL(`${FRONTEND_URL}/offices/munich`);
    });

    test('should show hover effects on office names', async ({ page }) => {
      await navigateToOffices(page);

      const stockholmLink = page.locator('text=Stockholm').first();
      
      // Check initial styling
      await expect(stockholmLink).toHaveCSS('color', 'rgb(24, 144, 255)');
      
      // Hover over the link
      await stockholmLink.hover();
      
      // Check hover styling (Note: actual hover effects may vary)
      await expect(stockholmLink).toHaveCSS('cursor', 'pointer');
    });
  });

  test.describe('Office Detail Page', () => {
    test('should display office management interface for Stockholm', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/offices/stockholm`);

      // Wait for office data to load
      await expect(page.locator('text=Stockholm')).toBeVisible({ timeout: 10000 });

      // Check debug interface is shown
      await expect(page.locator('text=Office Management - DEBUG VERSION')).toBeVisible();
      await expect(page.locator('text=Debug Information:')).toBeVisible();
      
      // Check office selection info
      await expect(page.locator('text=Office ID from URL: stockholm')).toBeVisible();
      await expect(page.locator('text=Current office: Stockholm')).toBeVisible();
    });

    test('should show office configuration when office is selected', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/offices/stockholm`);

      // Wait for office selection
      await expect(page.locator('text=Selected Office: Stockholm')).toBeVisible({ timeout: 10000 });
      
      // Check office details
      await expect(page.locator('text=Journey: mature')).toBeVisible();
      await expect(page.locator('text=Timezone: Europe/Stockholm')).toBeVisible();
      
      // Check office configuration component is present
      // Note: This depends on the actual implementation of OfficeConfigPage
      await expect(page.locator('[data-testid="office-config"]')).toBeVisible();
    });

    test('should allow switching between offices', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/offices/stockholm`);
      
      // Wait for Stockholm to load
      await expect(page.locator('text=Selected Office: Stockholm')).toBeVisible({ timeout: 10000 });
      
      // Click Munich button
      const munichButton = page.locator('text=Munich (established)');
      await munichButton.click();
      
      // Check URL changed
      await expect(page).toHaveURL(`${FRONTEND_URL}/offices/munich`);
      
      // Check Munich is now selected
      await expect(page.locator('text=Selected Office: Munich')).toBeVisible();
    });

    test('should handle direct navigation to Munich office', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/offices/munich`);

      // Wait for Munich office to load
      await expect(page.locator('text=Selected Office: Munich')).toBeVisible({ timeout: 10000 });
      
      // Check Munich-specific details
      await expect(page.locator('text=Journey: established')).toBeVisible();
      await expect(page.locator('text=Office ID from URL: munich')).toBeVisible();
    });
  });

  test.describe('Error Handling', () => {
    test('should handle API errors gracefully', async ({ page }) => {
      // Mock API to return error
      await page.route('**/api/offices', async route => {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Internal Server Error' }),
        });
      });

      await page.goto(`${FRONTEND_URL}/offices`);

      // Should show error message
      await expect(page.locator('text=Failed to fetch offices')).toBeVisible({ timeout: 10000 });
    });

    test('should handle non-existent office navigation', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/offices/nonexistent`);

      // Should redirect to first available office or show error
      await page.waitForTimeout(2000); // Wait for navigation logic
      
      // Either redirected to valid office or shows appropriate message
      const url = page.url();
      const hasValidOffice = url.includes('/stockholm') || url.includes('/munich');
      const hasError = await page.locator('text=Office not found').isVisible();
      
      expect(hasValidOffice || hasError).toBe(true);
    });

    test('should show loading state while offices are loading', async ({ page }) => {
      // Mock delayed API response
      await page.route('**/api/offices', async route => {
        await new Promise(resolve => setTimeout(resolve, 2000));
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([]),
        });
      });

      await page.goto(`${FRONTEND_URL}/offices`);

      // Should show loading state
      await expect(page.locator('.ant-spin')).toBeVisible();
    });

    test('should show retry option on error', async ({ page }) => {
      // Mock initial error
      let callCount = 0;
      await page.route('**/api/offices', async route => {
        callCount++;
        if (callCount === 1) {
          await route.fulfill({
            status: 500,
            contentType: 'application/json',
            body: JSON.stringify({ error: 'Server Error' }),
          });
        } else {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify([
              {
                id: 'stockholm',
                name: 'Stockholm',
                journey: 'mature',
                total_fte: 679,
                economic_parameters: { cost_of_living: 1.0, market_multiplier: 1.0, tax_rate: 0.25 },
                roles: {},
              },
            ]),
          });
        }
      });

      await page.goto(`${FRONTEND_URL}/offices/stockholm`);

      // Should show error initially
      await expect(page.locator('text=Error Loading Offices')).toBeVisible({ timeout: 10000 });
      
      // Click retry button
      const retryButton = page.locator('text=Retry');
      await retryButton.click();
      
      // Should succeed on retry
      await expect(page.locator('text=Stockholm')).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe('Responsive Design', () => {
    test('should work correctly on mobile viewport', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      
      await navigateToOffices(page);

      // Should still display offices
      await expect(page.locator('text=All Offices')).toBeVisible();
      await expect(page.locator('text=Stockholm')).toBeVisible();
      
      // Table should be responsive
      const table = page.locator('.ant-table');
      await expect(table).toBeVisible();
    });

    test('should work correctly on tablet viewport', async ({ page }) => {
      // Set tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });
      
      await navigateToOffices(page);

      // Should display all content properly
      await expect(page.locator('text=All Offices')).toBeVisible();
      await expect(page.locator('text=Stockholm')).toBeVisible();
      await expect(page.locator('text=Munich')).toBeVisible();
    });

    test('should handle office management page on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      
      await page.goto(`${FRONTEND_URL}/offices/stockholm`);

      // Should load office management interface
      await expect(page.locator('text=Office Management')).toBeVisible({ timeout: 10000 });
      
      // Office selection should work on mobile
      await expect(page.locator('text=Stockholm')).toBeVisible();
    });
  });

  test.describe('Performance', () => {
    test('should load office list within reasonable time', async ({ page }) => {
      const startTime = Date.now();
      
      await navigateToOffices(page);
      
      const loadTime = Date.now() - startTime;
      
      // Should load within 5 seconds
      expect(loadTime).toBeLessThan(5000);
    });

    test('should navigate between offices quickly', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/offices/stockholm`);
      await expect(page.locator('text=Stockholm')).toBeVisible({ timeout: 10000 });
      
      const startTime = Date.now();
      
      // Navigate to Munich
      const munichButton = page.locator('text=Munich (established)');
      await munichButton.click();
      
      await expect(page.locator('text=Selected Office: Munich')).toBeVisible();
      
      const navigationTime = Date.now() - startTime;
      
      // Navigation should be fast
      expect(navigationTime).toBeLessThan(2000);
    });
  });

  test.describe('Accessibility', () => {
    test('should have proper keyboard navigation', async ({ page }) => {
      await navigateToOffices(page);

      // Tab to office links
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      
      // Should be able to navigate to offices with keyboard
      const focusedElement = page.locator(':focus');
      await expect(focusedElement).toBeVisible();
    });

    test('should have proper ARIA labels', async ({ page }) => {
      await navigateToOffices(page);

      // Check table has proper ARIA attributes
      const table = page.locator('.ant-table table');
      await expect(table).toHaveAttribute('role');
    });

    test('should support screen readers', async ({ page }) => {
      await navigateToOffices(page);

      // Check important elements have proper text content
      await expect(page.locator('text=All Offices')).toBeVisible();
      await expect(page.locator('text=Office')).toBeVisible(); // Table header
      await expect(page.locator('text=Total FTE')).toBeVisible(); // Table header
    });
  });
});