// Test script to validate backend API FTE data flow
// Run with: node test-backend-api.js

const fetch = require('node-fetch');

async function testBackendAPI() {
  console.log('=== Testing Backend API FTE Data Flow ===\n');
  
  try {
    // Test 1: Check if backend is running
    console.log('1. Checking if backend is running...');
    const healthResponse = await fetch('http://localhost:8000/health');
    if (!healthResponse.ok) {
      throw new Error(`Backend health check failed: ${healthResponse.status}`);
    }
    console.log('✅ Backend is running\n');
    
    // Test 2: Get office configuration
    console.log('2. Getting office configuration...');
    const configResponse = await fetch('http://localhost:8000/offices/config');
    if (!configResponse.ok) {
      throw new Error(`Failed to get office config: ${configResponse.status}`);
    }
    const officeConfig = await configResponse.json();
    console.log(`✅ Found ${officeConfig.length} offices in configuration`);
    console.log(`   Total FTE: ${officeConfig.reduce((sum, office) => sum + (office.total_fte || 0), 0)}\n`);
    
    // Test 3: Run a simulation
    console.log('3. Running simulation...');
    const simulationPayload = {
      start_year: 2025,
      start_month: 1,
      end_year: 2027,
      end_month: 12,
      price_increase: 0,
      salary_increase: 0,
      unplanned_absence: 0.05,
      hy_working_hours: 166.4,
      other_expense: 19000000.0,
      employment_cost_rate: 0.40,
      office_overrides: {}
    };
    
    const simulationResponse = await fetch('http://localhost:8000/simulation/run', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(simulationPayload),
    });
    
    if (!simulationResponse.ok) {
      const errorText = await simulationResponse.text();
      throw new Error(`Simulation failed: ${simulationResponse.status} - ${errorText}`);
    }
    
    const simulationResults = await simulationResponse.json();
    console.log('✅ Simulation completed successfully\n');
    
    // Test 4: Analyze FTE data in results
    console.log('4. Analyzing FTE data in simulation results...');
    analyzeFTEData(simulationResults);
    
    // Test 5: Validate data structure
    console.log('\n5. Validating data structure...');
    validateDataStructure(simulationResults);
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    process.exit(1);
  }
}

function analyzeFTEData(results) {
  if (!results.years) {
    console.log('❌ No years data found in results');
    return;
  }
  
  const years = Object.keys(results.years);
  console.log(`   Found ${years.length} years: ${years.join(', ')}`);
  
  years.forEach(year => {
    const yearData = results.years[year];
    if (!yearData.offices) {
      console.log(`   ❌ No offices data found for year ${year}`);
      return;
    }
    
    const offices = Object.keys(yearData.offices);
    console.log(`   Year ${year}: ${offices.length} offices`);
    
    let totalFTE = 0;
    let officesWithFTE = 0;
    
    offices.forEach(officeName => {
      const officeData = yearData.offices[officeName];
      
      // Check for FTE fields
      const fte = officeData.fte;
      const totalFte = officeData.total_fte;
      const baselineTotalFte = officeData.baseline_total_fte;
      const currentTotalFte = officeData.current_total_fte;
      
      const officeFTE = fte || totalFte || currentTotalFte || baselineTotalFte || 0;
      
      if (officeFTE > 0) {
        officesWithFTE++;
        totalFTE += officeFTE;
      }
      
      console.log(`     ${officeName}: fte=${fte}, total_fte=${totalFte}, baseline_total_fte=${baselineTotalFte}, current_total_fte=${currentTotalFte}`);
    });
    
    console.log(`   Year ${year} Summary: ${officesWithFTE}/${offices.length} offices have FTE data, Total FTE: ${totalFTE}`);
  });
}

function validateDataStructure(results) {
  const issues = [];
  
  // Check required top-level properties
  if (!results.years) issues.push('Missing "years" property');
  if (!results.kpis) issues.push('Missing "kpis" property');
  
  if (issues.length > 0) {
    console.log('   ❌ Data structure issues:');
    issues.forEach(issue => console.log(`     - ${issue}`));
  } else {
    console.log('   ✅ Basic data structure is valid');
  }
  
  // Check years structure
  if (results.years) {
    const years = Object.keys(results.years);
    if (years.length === 0) {
      console.log('   ❌ No years found in results');
    } else {
      console.log(`   ✅ Found ${years.length} years with data`);
      
      // Check first year structure
      const firstYear = years[0];
      const firstYearData = results.years[firstYear];
      
      if (!firstYearData.offices) {
        console.log('   ❌ No offices data in first year');
      } else {
        const offices = Object.keys(firstYearData.offices);
        console.log(`   ✅ First year has ${offices.length} offices`);
        
        if (offices.length > 0) {
          const firstOffice = firstYearData.offices[offices[0]];
          const officeKeys = Object.keys(firstOffice);
          console.log(`   ✅ First office has keys: ${officeKeys.join(', ')}`);
          
          // Check for FTE-related keys
          const fteKeys = officeKeys.filter(key => key.includes('fte') || key.includes('FTE'));
          if (fteKeys.length > 0) {
            console.log(`   ✅ FTE-related keys found: ${fteKeys.join(', ')}`);
          } else {
            console.log('   ⚠️  No FTE-related keys found in office data');
          }
        }
      }
    }
  }
}

// Run the test
testBackendAPI().catch(console.error); 