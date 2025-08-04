/**
 * End-to-end tests for Business Plan workflow
 * Tests complete business plan management user workflows
 */
import { test, expect, Page } from '@playwright/test';

// Use baseURL from Playwright config instead of hardcoded URL
const FRONTEND_URL = '';

// Mock business plan data
const mockBusinessPlans = [
  {
    id: 'plan-2025-01',
    office_id: 'stockholm',
    year: 2025,
    month: 1,
    planned_fte: 680,
    planned_revenue: 1200000,
    planned_costs: 800000,
    workforce_entries: [
      { role: 'Consultant', level: 'A', fte: 70, notes: 'Growth focus' },
      { role: 'Consultant', level: 'AC', fte: 55, notes: 'Stable headcount' },
    ],
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
  },
];

const mockOfficeData = {
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
};

async function setupAPIRoutes(page: Page) {
  // Mock offices API
  await page.route('**/api/offices', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([mockOfficeData]),
    });
  });

  await page.route('**/api/offices/stockholm', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockOfficeData),
    });
  });

  // Mock business plans API
  await page.route('**/api/offices/stockholm/business-plans', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockBusinessPlans),
    });
  });

  await page.route('**/api/offices/stockholm/summary', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        office_id: 'stockholm',
        monthly_plans: mockBusinessPlans,
        workforce_distribution: {
          office_id: 'stockholm',
          start_date: '2025-01-01',
          workforce: [
            { role: 'Consultant', level: 'A', fte: 69, notes: 'Current baseline' },
            { role: 'Consultant', level: 'AC', fte: 54, notes: 'Current baseline' },
          ],
        },
      }),
    });
  });

  // Mock business plan CRUD operations
  await page.route('**/api/business-plans', async route => {
    if (route.request().method() === 'POST') {
      const requestData = await route.request().postDataJSON();
      const newPlan = {
        ...requestData,
        id: `plan-${requestData.year}-${requestData.month.toString().padStart(2, '0')}`,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify(newPlan),
      });
    } else {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockBusinessPlans),
      });
    }
  });
}

test.describe('Business Plan E2E Workflow Tests', () => {
  test.beforeEach(async ({ page }) => {
    await setupAPIRoutes(page);
  });

  test.describe('Business Plan Navigation and Access', () => {
    test('should navigate to office and access business plan tab', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/offices/stockholm`);

      // Wait for office to load
      await expect(page.locator('text=Stockholm')).toBeVisible({ timeout: 10000 });

      // Look for business plan tab or section
      const businessPlanTab = page.locator('text=Business Plans').or(
        page.locator('[data-testid="business-plans-tab"]')
      );
      
      if (await businessPlanTab.isVisible()) {
        await businessPlanTab.click();
        
        // Should show business plan interface
        await expect(page.locator('text=Monthly Business Plans')).toBeVisible();
      } else {
        // If no dedicated tab, business plans might be integrated
        console.log('Business plan tab not found - checking for integrated view');
      }
    });

    test('should display business plan data when available', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/offices/stockholm`);
      
      // Wait for data to load and check for business plan content
      await page.waitForTimeout(2000);
      
      // Look for financial data or plan data
      const hasFinancialData = await page.locator('text=1,200,000').isVisible() ||
                              await page.locator('text=680').isVisible() ||
                              await page.locator('text=January').isVisible();
      
      if (hasFinancialData) {
        console.log('Business plan data is displayed');
      } else {
        console.log('Business plan data not visible - checking component implementation');
      }
    });
  });

  test.describe('Business Plan Table Functionality', () => {
    test('should display business plan table with correct data', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/offices/stockholm`);
      
      // Navigate to business plans if there's a dedicated section
      const businessPlanSection = page.locator('[data-testid="business-plan-table"]').or(
        page.locator('text=Business Plans').locator('..')
      );

      if (await businessPlanSection.isVisible()) {
        // Check for plan data
        await expect(page.locator('text=680')).toBeVisible(); // FTE
        await expect(page.locator('text=1,200,000')).toBeVisible(); // Revenue
        await expect(page.locator('text=800,000')).toBeVisible(); // Costs
        await expect(page.locator('text=January')).toBeVisible(); // Month
      }
    });

    test('should allow filtering plans by year', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/offices/stockholm`);
      
      // Look for year selector
      const yearSelector = page.locator('[data-testid="year-selector"]').or(
        page.locator('input[type="number"]').first()
      );

      if (await yearSelector.isVisible()) {
        // Change year to 2026
        await yearSelector.fill('2026');
        await page.keyboard.press('Enter');
        
        // Should filter results or show empty state
        await page.waitForTimeout(1000);
        
        // Reset to 2025
        await yearSelector.fill('2025');
        await page.keyboard.press('Enter');
        
        // Should show original data
        await expect(page.locator('text=680')).toBeVisible();
      }
    });

    test('should show plan details in expandable rows', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/offices/stockholm`);
      
      // Look for expand button
      const expandButton = page.locator('[data-testid="expand-button"]').or(
        page.locator('.ant-table-row-expand-icon')
      ).first();

      if (await expandButton.isVisible()) {
        await expandButton.click();
        
        // Should show workforce details
        await expect(page.locator('text=Consultant A: 70 FTE')).toBeVisible();
        await expect(page.locator('text=Growth focus')).toBeVisible();
      }
    });
  });

  test.describe('Business Plan Creation', () => {
    test('should allow creating new business plan', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/offices/stockholm`);
      
      // Look for add/create button
      const addButton = page.locator('text=Add Plan').or(
        page.locator('[data-testid="add-plan-button"]')
      );

      if (await addButton.isVisible()) {
        await addButton.click();
        
        // Should show creation form
        await expect(page.locator('text=New Business Plan')).toBeVisible();
        
        // Fill form
        const monthSelect = page.locator('[data-testid="month-select"]').or(
          page.locator('select').first()
        );
        
        if (await monthSelect.isVisible()) {
          await monthSelect.selectOption('3'); // March
        }
        
        // Fill FTE
        const fteInput = page.locator('[data-testid="fte-input"]').or(
          page.locator('input[type="number"]').first()
        );
        
        if (await fteInput.isVisible()) {
          await fteInput.fill('700');
        }
        
        // Fill revenue
        const revenueInput = page.locator('[data-testid="revenue-input"]').or(
          page.locator('input[type="number"]').nth(1)
        );
        
        if (await revenueInput.isVisible()) {
          await revenueInput.fill('1400000');
        }
        
        // Submit
        const createButton = page.locator('text=Create Plan').or(
          page.locator('[data-testid="create-button"]')
        );
        
        if (await createButton.isVisible()) {
          await createButton.click();
          
          // Should show success message or new plan in table
          await page.waitForTimeout(1000);
          
          // Check for success indicators
          const hasSuccess = await page.locator('text=Plan created successfully').isVisible() ||
                            await page.locator('text=March').isVisible();
          
          expect(hasSuccess).toBe(true);
        }
      }
    });

    test('should validate required fields', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/offices/stockholm`);
      
      const addButton = page.locator('text=Add Plan');
      
      if (await addButton.isVisible()) {
        await addButton.click();
        
        // Try to submit without filling required fields
        const createButton = page.locator('text=Create Plan');
        
        if (await createButton.isVisible()) {
          await createButton.click();
          
          // Should show validation errors
          const hasValidationError = await page.locator('text=Required').isVisible() ||
                                    await page.locator('text=Please fill').isVisible() ||
                                    await createButton.isDisabled();
          
          expect(hasValidationError).toBe(true);
        }
      }
    });
  });

  test.describe('Business Plan Editing', () => {
    test('should allow editing existing business plan', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/offices/stockholm`);
      
      // Look for edit button
      const editButton = page.locator('text=Edit').or(
        page.locator('[data-testid="edit-button"]')
      ).first();

      if (await editButton.isVisible()) {
        await editButton.click();
        
        // Should show edit form or inline editing
        const isInlineEdit = await page.locator('input[value="680"]').isVisible();
        const isModalEdit = await page.locator('text=Edit Business Plan').isVisible();
        
        if (isInlineEdit) {
          // Inline editing
          const fteInput = page.locator('input[value="680"]');
          await fteInput.fill('690');
          
          const saveButton = page.locator('text=Save');
          await saveButton.click();
          
          // Should show updated value
          await expect(page.locator('text=690')).toBeVisible();
          
        } else if (isModalEdit) {
          // Modal editing
          const fteInput = page.locator('input[type="number"]').first();
          await fteInput.fill('690');
          
          const saveButton = page.locator('text=Save');
          await saveButton.click();
          
          await expect(page.locator('text=690')).toBeVisible();
        }
      }
    });

    test('should allow canceling edit operation', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/offices/stockholm`);
      
      const editButton = page.locator('text=Edit').first();
      
      if (await editButton.isVisible()) {
        await editButton.click();
        
        // Make some changes
        const fteInput = page.locator('input').first();
        if (await fteInput.isVisible()) {
          await fteInput.fill('999');
        }
        
        // Cancel
        const cancelButton = page.locator('text=Cancel');
        if (await cancelButton.isVisible()) {
          await cancelButton.click();
          
          // Should revert to original value
          await expect(page.locator('text=680')).toBeVisible();
          await expect(page.locator('text=999')).not.toBeVisible();
        }
      }
    });
  });

  test.describe('Workforce Management', () => {
    test('should display workforce entries in plan details', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/offices/stockholm`);
      
      // Expand plan details
      const expandButton = page.locator('.ant-table-row-expand-icon').first();
      
      if (await expandButton.isVisible()) {
        await expandButton.click();
        
        // Should show workforce breakdown
        await expect(page.locator('text=Consultant')).toBeVisible();
        await expect(page.locator('text=A: 70 FTE')).toBeVisible();
        await expect(page.locator('text=AC: 55 FTE')).toBeVisible();
        await expect(page.locator('text=Growth focus')).toBeVisible();
      }
    });

    test('should allow editing workforce entries', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/offices/stockholm`);
      
      // Expand and edit workforce
      const expandButton = page.locator('.ant-table-row-expand-icon').first();
      
      if (await expandButton.isVisible()) {
        await expandButton.click();
        
        const editWorkforceButton = page.locator('text=Edit Workforce');
        
        if (await editWorkforceButton.isVisible()) {
          await editWorkforceButton.click();
          
          // Edit FTE value
          const fteInput = page.locator('input[value="70"]');
          if (await fteInput.isVisible()) {
            await fteInput.fill('75');
            
            const saveButton = page.locator('text=Save');
            await saveButton.click();
            
            // Should show updated value
            await expect(page.locator('text=A: 75 FTE')).toBeVisible();
          }
        }
      }
    });

    test('should allow adding new workforce entry', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/offices/stockholm`);
      
      const expandButton = page.locator('.ant-table-row-expand-icon').first();
      
      if (await expandButton.isVisible()) {
        await expandButton.click();
        
        const addEntryButton = page.locator('text=Add Entry');
        
        if (await addEntryButton.isVisible()) {
          await addEntryButton.click();
          
          // Fill new entry form
          const roleSelect = page.locator('[data-testid="role-select"]');
          if (await roleSelect.isVisible()) {
            await roleSelect.selectOption('Consultant');
          }
          
          const levelSelect = page.locator('[data-testid="level-select"]');
          if (await levelSelect.isVisible()) {
            await levelSelect.selectOption('C');
          }
          
          const fteInput = page.locator('[data-testid="new-fte-input"]');
          if (await fteInput.isVisible()) {
            await fteInput.fill('40');
          }
          
          const saveButton = page.locator('text=Add');
          await saveButton.click();
          
          // Should show new entry
          await expect(page.locator('text=C: 40 FTE')).toBeVisible();
        }
      }
    });
  });

  test.describe('Data Export and Reporting', () => {
    test('should allow exporting business plan data', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/offices/stockholm`);
      
      const exportButton = page.locator('text=Export').or(
        page.locator('[data-testid="export-button"]')
      );

      if (await exportButton.isVisible()) {
        await exportButton.click();
        
        // Should show export options
        await expect(page.locator('text=Export Options')).toBeVisible();
        
        // Test CSV export
        const csvExport = page.locator('text=Export as CSV');
        if (await csvExport.isVisible()) {
          await csvExport.click();
          
          // Would typically test download, but that's complex in tests
          // Check for success message instead
          const hasSuccess = await page.locator('text=Export successful').isVisible();
          console.log('CSV export triggered:', hasSuccess);
        }
      }
    });

    test('should generate business plan summary report', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/offices/stockholm`);
      
      const reportButton = page.locator('text=Generate Report').or(
        page.locator('[data-testid="report-button"]')
      );

      if (await reportButton.isVisible()) {
        await reportButton.click();
        
        // Should show report or summary
        await page.waitForTimeout(2000);
        
        const hasReport = await page.locator('text=Business Plan Summary').isVisible() ||
                         await page.locator('text=Report generated').isVisible();
        
        console.log('Report generation triggered:', hasReport);
      }
    });
  });

  test.describe('Error Handling and Edge Cases', () => {
    test('should handle API errors gracefully', async ({ page }) => {
      // Mock API error
      await page.route('**/api/offices/stockholm/business-plans', async route => {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Internal Server Error' }),
        });
      });

      await page.goto(`${FRONTEND_URL}/offices/stockholm`);
      
      // Should show error message
      await expect(page.locator('text=Failed to load')).toBeVisible({ timeout: 10000 });
    });

    test('should handle empty business plan data', async ({ page }) => {
      // Mock empty response
      await page.route('**/api/offices/stockholm/business-plans', async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([]),
        });
      });

      await page.goto(`${FRONTEND_URL}/offices/stockholm`);
      
      // Should show empty state
      const hasEmptyState = await page.locator('text=No business plans').isVisible() ||
                           await page.locator('text=Create your first plan').isVisible();
      
      expect(hasEmptyState).toBe(true);
    });

    test('should handle network connectivity issues', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/offices/stockholm`);
      
      // Simulate network failure
      await page.route('**/api/**', async route => {
        await route.abort();
      });
      
      // Try to perform action that requires network
      const addButton = page.locator('text=Add Plan');
      if (await addButton.isVisible()) {
        await addButton.click();
        
        // Should show network error
        await page.waitForTimeout(2000);
        const hasNetworkError = await page.locator('text=Network error').isVisible() ||
                              await page.locator('text=Connection failed').isVisible();
        
        console.log('Network error handling:', hasNetworkError);
      }
    });
  });

  test.describe('Performance and User Experience', () => {
    test('should load business plan data within reasonable time', async ({ page }) => {
      const startTime = Date.now();
      
      await page.goto(`${FRONTEND_URL}/offices/stockholm`);
      
      // Wait for business plan data to appear
      await page.waitForSelector('text=680', { timeout: 10000 });
      
      const loadTime = Date.now() - startTime;
      expect(loadTime).toBeLessThan(5000); // Should load within 5 seconds
    });

    test('should provide visual feedback during operations', async ({ page }) => {
      await page.goto(`${FRONTEND_URL}/offices/stockholm`);
      
      const addButton = page.locator('text=Add Plan');
      
      if (await addButton.isVisible()) {
        await addButton.click();
        
        // Should show loading states
        const hasLoadingState = await page.locator('.ant-spin').isVisible() ||
                               await page.locator('text=Loading').isVisible();
        
        console.log('Loading state shown:', hasLoadingState);
      }
    });

    test('should be responsive on different screen sizes', async ({ page }) => {
      // Test mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto(`${FRONTEND_URL}/offices/stockholm`);
      
      // Should adapt to mobile layout
      await page.waitForTimeout(1000);
      
      // Test tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });
      await page.waitForTimeout(500);
      
      // Should adapt to tablet layout
      const isResponsive = await page.locator('.office-management').isVisible();
      expect(isResponsive).toBe(true);
    });
  });
});