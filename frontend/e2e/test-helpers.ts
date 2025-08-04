import { Page, expect } from '@playwright/test';

/**
 * Test helper utilities for SimpleSim E2E tests
 */

export interface ScenarioConfig {
  name: string;
  description?: string;
  startYear: string;
  endYear: string;
  startMonth: string;
  endMonth: string;
  scope: 'group' | 'individual';
  offices?: string[];
}

export interface LeverConfig {
  office: string;
  role: string;
  level?: string;
  recruitment: string;
  churn: string;
}

/**
 * Creates a scenario with the given configuration
 */
export async function createScenario(
  page: Page, 
  config: ScenarioConfig, 
  levers: LeverConfig[] = []
): Promise<void> {
  // Navigate to scenarios page
  await page.goto('/scenarios');
  await page.waitForSelector('h2:has-text("Scenarios")');

  // Open creation dialog
  await page.click('button:has-text("Create Scenario")');
  await page.waitForSelector('[role="dialog"]');

  // Fill basic information
  await page.fill('input[placeholder*="scenario name"]', config.name);
  
  if (config.description) {
    await page.fill('textarea[placeholder*="description"]', config.description);
  }

  // Set time range
  await page.fill('input[aria-label="Start Year"]', config.startYear);
  await page.selectOption('select[aria-label="Start Month"]', config.startMonth);
  await page.fill('input[aria-label="End Year"]', config.endYear);
  await page.selectOption('select[aria-label="End Month"]', config.endMonth);

  // Set office scope
  await page.click(`input[type="radio"][value="${config.scope}"]`);

  if (config.scope === 'individual' && config.offices) {
    // Select specific offices
    const officeSelector = page.locator('select[placeholder*="offices"], .ant-select-selector');
    await officeSelector.click();
    
    for (const office of config.offices) {
      await page.click(`.ant-select-item-option:has-text("${office}")`);
    }
    
    // Click outside to close dropdown
    await page.click('body');
  }

  // Proceed to lever configuration
  await page.click('button:has-text("Next")');
  await page.waitForSelector('h3:has-text("Configure Simulation Levers")');

  // Configure levers if provided
  for (const lever of levers) {
    await configureLever(page, lever);
  }

  // Save scenario
  await page.click('button:has-text("Save Scenario")');
  await page.waitForSelector('.ant-message-success', { timeout: 15000 });
}

/**
 * Configures a single simulation lever
 */
export async function configureLever(page: Page, lever: LeverConfig): Promise<void> {
  // Select office
  await page.click(`text=${lever.office}`);
  await page.waitForTimeout(300);

  // Select role
  await page.click(`text=${lever.role}`);
  await page.waitForTimeout(300);

  // Select level if provided (for leveled roles)
  if (lever.level) {
    await page.click(`text=${lever.level}`);
    await page.waitForTimeout(300);
  }

  // Set recruitment rate
  const recruitmentInput = page.locator('input[placeholder*="recruitment"]').first();
  await recruitmentInput.clear();
  await recruitmentInput.fill(lever.recruitment);

  // Set churn rate
  const churnInput = page.locator('input[placeholder*="churn"]').first();
  await churnInput.clear();
  await churnInput.fill(lever.churn);

  await page.waitForTimeout(300);
}

/**
 * Runs a scenario simulation by name
 */
export async function runScenario(page: Page, scenarioName: string): Promise<void> {
  await page.goto('/scenarios');
  await page.waitForSelector('table');

  // Find scenario row and click Run button
  const scenarioRow = page.locator(`tr:has-text("${scenarioName}")`);
  await expect(scenarioRow).toBeVisible();
  
  const runButton = scenarioRow.locator('button:has-text("Run")');
  await runButton.click();

  // Wait for simulation to complete
  await page.waitForSelector('h1:has-text("Simulation Results")', { timeout: 30000 });
}

/**
 * Navigates to a specific year in the results view
 */
export async function navigateToYear(page: Page, targetYear: string): Promise<void> {
  const currentYearElement = page.locator('[data-testid="current-year"]');
  
  let attempts = 0;
  const maxAttempts = 10;
  
  while (attempts < maxAttempts) {
    const currentYear = await currentYearElement.textContent();
    
    if (currentYear === targetYear) {
      break;
    }
    
    if (parseInt(currentYear || '0') < parseInt(targetYear)) {
      await page.click('[data-testid="next-year-button"]');
    } else {
      await page.click('[data-testid="previous-year-button"]');
    }
    
    await page.waitForTimeout(500);
    attempts++;
  }
  
  // Verify we reached the target year
  const finalYear = await currentYearElement.textContent();
  expect(finalYear).toBe(targetYear);
}

/**
 * Extracts numeric values from KPI cards
 */
export async function getKpiValues(page: Page): Promise<number[]> {
  const kpiCards = page.locator('[data-testid="kpi-card"]');
  const kpiCount = await kpiCards.count();
  const values: number[] = [];

  for (let i = 0; i < kpiCount; i++) {
    const valueElement = kpiCards.nth(i).locator('[data-testid="kpi-value"]');
    const valueText = await valueElement.textContent();
    const numericValue = parseFloat(valueText?.replace(/[^\d.-]/g, '') || '0');
    values.push(numericValue);
  }

  return values;
}

/**
 * Validates that all KPI values are non-zero
 */
export async function validateNonZeroKpis(page: Page): Promise<void> {
  const kpiValues = await getKpiValues(page);
  
  expect(kpiValues.length).toBeGreaterThan(0);
  
  for (let i = 0; i < kpiValues.length; i++) {
    expect(kpiValues[i]).not.toBe(0);
    expect(kpiValues[i]).not.toBeNaN();
  }
}

/**
 * Validates that table cells contain non-zero data
 */
export async function validateTableData(page: Page, tableSelector: string): Promise<void> {
  const table = page.locator(tableSelector);
  await expect(table).toBeVisible();

  const dataCells = table.locator('tbody td:not(:first-child)'); // Skip label columns
  const cellCount = await dataCells.count();
  expect(cellCount).toBeGreaterThan(0);

  let nonZeroCount = 0;
  const maxCellsToCheck = Math.min(cellCount, 20); // Limit for performance

  for (let i = 0; i < maxCellsToCheck; i++) {
    const cellText = await dataCells.nth(i).textContent();
    const value = parseFloat(cellText?.replace(/[^\d.-]/g, '') || '0');
    
    if (!isNaN(value) && value !== 0) {
      nonZeroCount++;
    }
  }

  expect(nonZeroCount).toBeGreaterThan(0);
}

/**
 * Validates that charts contain data elements
 */
export async function validateChartData(page: Page): Promise<void> {
  const chartSvgs = page.locator('svg:has(path), svg:has(rect), svg:has(circle)');
  const chartCount = await chartSvgs.count();
  expect(chartCount).toBeGreaterThan(0);

  // Check first few charts for data elements
  const chartsToCheck = Math.min(chartCount, 5);
  
  for (let i = 0; i < chartsToCheck; i++) {
    const chart = chartSvgs.nth(i);
    const dataElements = chart.locator('path[d*="M"], rect[height], circle[r]');
    const elementCount = await dataElements.count();
    expect(elementCount).toBeGreaterThan(0);
  }
}

/**
 * Deletes a scenario by name (cleanup utility)
 */
export async function deleteScenario(page: Page, scenarioName: string): Promise<void> {
  try {
    await page.goto('/scenarios');
    await page.waitForSelector('table');

    const scenarioRow = page.locator(`tr:has-text("${scenarioName}")`);
    
    if (await scenarioRow.isVisible()) {
      const deleteButton = scenarioRow.locator('button:has-text("Delete")');
      await deleteButton.click();
      
      // Confirm deletion
      await page.click('button:has-text("Yes")');
      await page.waitForSelector('.ant-message-success', { timeout: 10000 });
    }
  } catch (error) {
    console.log(`Failed to delete scenario ${scenarioName}:`, error);
  }
}

/**
 * Waits for the application to be fully loaded
 */
export async function waitForAppReady(page: Page): Promise<void> {
  await page.goto('/');
  await page.waitForLoadState('networkidle');
  await page.waitForSelector('body', { timeout: 10000 });
  
  // Wait for any loading spinners to disappear
  const loadingElements = page.locator('.ant-spin, .loading, [data-testid="loading"]');
  await loadingElements.first().waitFor({ state: 'hidden', timeout: 5000 }).catch(() => {
    // Ignore if no loading elements found
  });
}

/**
 * Default scenario configuration for testing
 */
export const DEFAULT_TEST_SCENARIO: ScenarioConfig = {
  name: `Test Scenario ${Date.now()}`,
  description: 'Automated test scenario',
  startYear: '2025',
  endYear: '2027',
  startMonth: '1',
  endMonth: '12',
  scope: 'group'
};

/**
 * Default lever configuration for realistic results
 */
export const DEFAULT_TEST_LEVERS: LeverConfig[] = [
  {
    office: 'Stockholm',
    role: 'Consultant',
    level: 'A',
    recruitment: '0.08',
    churn: '0.03'
  },
  {
    office: 'Stockholm',
    role: 'Consultant', 
    level: 'B',
    recruitment: '0.05',
    churn: '0.025'
  }
];