import { test, expect } from '@playwright/test';

/**
 * Debug test to understand the actual UI structure of the scenarios page
 */

test.describe('Debug Scenarios UI', () => {
  test('Should inspect scenarios page UI elements', async ({ page }) => {
    await page.goto('/scenarios');
    await page.waitForTimeout(3000);
    
    // Get page title
    const title = await page.title();
    console.log('Page title:', title);
    
    // Get all button text
    const buttons = await page.locator('button').all();
    console.log(`Found ${buttons.length} buttons:`);
    
    for (let i = 0; i < Math.min(buttons.length, 20); i++) {
      const buttonText = await buttons[i].textContent();
      const buttonRole = await buttons[i].getAttribute('role');
      const buttonClass = await buttons[i].getAttribute('class');
      console.log(`  Button ${i}: "${buttonText}" (role: ${buttonRole}, class: ${buttonClass?.substring(0, 50)})`);
    }
    
    // Get all text that might be headings
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
    console.log(`Found ${headings.length} headings:`);
    
    for (let i = 0; i < headings.length; i++) {
      const headingText = await headings[i].textContent();
      const tagName = await headings[i].evaluate(el => el.tagName);
      console.log(`  ${tagName}: "${headingText}"`);
    }
    
    // Look for any clickable elements with "create", "new", "add" text
    const createElements = await page.locator('button, a, [role="button"], [data-testid*="create"], [data-testid*="new"]').all();
    console.log(`Found ${createElements.length} potential create elements:`);
    
    for (let i = 0; i < Math.min(createElements.length, 10); i++) {
      const elementText = await createElements[i].textContent();
      const tagName = await createElements[i].evaluate(el => el.tagName);
      const testId = await createElements[i].getAttribute('data-testid');
      console.log(`  ${tagName}: "${elementText}" (testId: ${testId})`);
    }
    
    // Look for any modal triggers or form containers
    const modalTriggers = await page.locator('[data-modal], [data-dialog], [data-trigger]').all();
    console.log(`Found ${modalTriggers.length} modal triggers`);
    
    // Check for any table or list content
    const tables = await page.locator('table').count();
    const lists = await page.locator('ul, ol').count();
    const cards = await page.locator('[class*="card"], [data-testid*="card"]').count();
    
    console.log(`Content counts: ${tables} tables, ${lists} lists, ${cards} cards`);
    
    // Take a screenshot for manual inspection
    await page.screenshot({ path: 'test-results/scenarios-page-debug.png', fullPage: true });
    console.log('Screenshot saved: test-results/scenarios-page-debug.png');
    
    // Get some sample text content to understand the page
    const bodyText = await page.textContent('body');
    const relevantText = bodyText?.substring(0, 500) + '...' || '';
    console.log('Sample page text:', relevantText);
  });
});