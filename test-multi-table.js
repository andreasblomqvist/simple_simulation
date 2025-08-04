/**
 * Quick test for multi-table interface
 */

const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  // Listen for console errors
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.error('Console error:', msg.text());
    }
  });

  // Listen for page errors
  page.on('pageerror', error => {
    console.error('Page error:', error.message);
  });

  try {
    console.log('🚀 Testing Multi-Table Interface...');
    
    // Navigate to Business Planning page
    console.log('📍 Navigating to Business Planning...');
    await page.goto('http://localhost:3000/business-planning');
    await page.waitForLoadState('networkidle');
    
    // Check if page loads without errors
    const title = await page.title();
    console.log('✅ Page loaded:', title);
    
    // Look for the toggle button
    const toggleButton = await page.locator('button:has-text("Expandable")').first();
    const toggleExists = await toggleButton.count() > 0;
    console.log('🔘 Toggle button exists:', toggleExists);
    
    if (toggleExists) {
      console.log('🎯 Clicking toggle to switch to Multi-Table interface...');
      await toggleButton.click();
      await page.waitForTimeout(1000); // Wait for interface to switch
      
      // Check if multi-table interface loaded
      const multiTableInterface = await page.locator('div.multi-table-planning-interface').first();
      const interfaceExists = await multiTableInterface.count() > 0;
      console.log('📊 Multi-Table interface loaded:', interfaceExists);
      
      if (interfaceExists) {
        // Check for tab navigation
        const workforceTab = await page.locator('button[data-state="active"]:has-text("Workforce")').first();
        const workforceTabActive = await workforceTab.count() > 0;
        console.log('👥 Workforce tab active:', workforceTabActive);
        
        // Check for progress bars
        const progressBars = await page.locator('.progress-bar, [role="progressbar"]').count();
        console.log('📈 Progress indicators found:', progressBars);
        
        // Test tab switching
        const financialTab = await page.locator('button:has-text("Financial")').first();
        if (await financialTab.count() > 0) {
          console.log('💰 Switching to Financial tab...');
          await financialTab.click();
          await page.waitForTimeout(500);
          
          const financialTable = await page.locator('.financial-planning-table').first();
          const financialTableExists = await financialTable.count() > 0;
          console.log('💰 Financial table loaded:', financialTableExists);
        }
        
        console.log('✅ Multi-Table interface test completed successfully!');
      } else {
        console.log('❌ Multi-Table interface failed to load');
      }
    } else {
      console.log('❌ Toggle button not found - interface may not be integrated correctly');
    }
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
  } finally {
    await browser.close();
  }
})();