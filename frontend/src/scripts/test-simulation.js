/**
 * Simple test script to verify simulation behavior
 * Run with: node src/scripts/test-simulation.js
 */

const API_BASE = 'http://localhost:8000/scenarios';

// Helper function to make API requests
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      'X-Correlation-ID': Math.random().toString(36).substring(2, 10),
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(`HTTP ${response.status}: ${errorData.detail || response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API request failed for ${endpoint}:`, error.message);
    throw error;
  }
}

// Helper function to run a scenario
async function runScenarioDefinition(scenario) {
  const request = {
    scenario_definition: scenario,
    office_scope: undefined,
  };
  
  console.log('Sending request:', JSON.stringify(request, null, 2));
  
  return apiRequest('/run', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

// Create baseline input data
function createBaselineInput(recruitmentMultiplier = 1.0, churnMultiplier = 1.0) {
  const baseline = {
    global_data: {
      recruitment: {
        Consultant: {},
        Sales: {},
        Recruitment: {}
      },
      churn: {
        Consultant: {},
        Sales: {},
        Recruitment: {}
      }
    }
  };

  // Create data for 3 years (2025-2027)
  for (let year = 2025; year <= 2027; year++) {
    for (let month = 1; month <= 12; month++) {
      const monthKey = `${year}${month.toString().padStart(2, '0')}`;
      
      // Recruitment data
      baseline.global_data.recruitment.Consultant[monthKey] = {
        A: Math.round(20 * recruitmentMultiplier),
        AC: Math.round(8 * recruitmentMultiplier),
        C: Math.round(4 * recruitmentMultiplier),
        SrC: Math.round(1 * recruitmentMultiplier),
        AM: Math.round(1 * recruitmentMultiplier),
        M: 0,
        SrM: 0,
        Pi: 0,
        P: 0
      };

      // Churn data
      baseline.global_data.churn.Consultant[monthKey] = {
        A: Math.round(2 * churnMultiplier),
        AC: Math.round(4 * churnMultiplier),
        C: Math.round(7 * churnMultiplier),
        SrC: Math.round(7 * churnMultiplier),
        AM: Math.round(9 * churnMultiplier),
        M: 1,
        SrM: 0,
        Pi: 0,
        P: 0
      };

      // Empty data for Sales and Recruitment roles
      baseline.global_data.recruitment.Sales[monthKey] = {};
      baseline.global_data.recruitment.Recruitment[monthKey] = {};
      baseline.global_data.churn.Sales[monthKey] = {};
      baseline.global_data.churn.Recruitment[monthKey] = {};
    }
  }

  return baseline;
}

// Create lever data
function createLevers(recruitmentMult = 1.0, churnMult = 1.0, progressionMult = 1.0) {
  const levels = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P'];
  
  return {
    recruitment: Object.fromEntries(levels.map(level => [level, recruitmentMult])),
    churn: Object.fromEntries(levels.map(level => [level, churnMult])),
    progression: Object.fromEntries(levels.map(level => [level, progressionMult]))
  };
}

// Create a test scenario
function createScenario(name, baselineInput, levers) {
  return {
    id: `test-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    name,
    description: `Test scenario: ${name}`,
    time_range: {
      start_year: 2025,
      start_month: 1,
      end_year: 2027,
      end_month: 12
    },
    office_scope: ['Group'],
    baseline_input: baselineInput,
    levers,
    economic_params: {},
    created_at: new Date().toISOString()
  };
}

// Extract key metrics from results
function extractMetrics(response) {
  if (response.status !== 'success' || !response.results) {
    throw new Error(`Simulation failed: ${response.error_message || 'Unknown error'}`);
  }

  const results = response.results;
  const years = Object.keys(results).sort();
  
  console.log('Available years:', years);
  console.log('Sample year structure:', Object.keys(results[years[0]] || {}));
  
  const fteByYear = {};
  
  years.forEach(year => {
    let totalFte = 0;
    const offices = results[year];
    
    Object.values(offices).forEach(office => {
      if (office.roles) {
        Object.values(office.roles).forEach(role => {
          if (Array.isArray(role)) {
            // Flat role structure
            totalFte += role.reduce((sum, monthValue) => sum + (monthValue || 0), 0) / 12;
          } else if (typeof role === 'object' && role !== null) {
            // Leveled role structure
            Object.values(role).forEach(level => {
              if (Array.isArray(level)) {
                totalFte += level.reduce((sum, monthValue) => sum + (monthValue || 0), 0) / 12;
              }
            });
          }
        });
      }
    });
    
    fteByYear[year] = Math.round(totalFte);
  });

  return {
    fteByYear,
    totalFte2025: fteByYear['2025'] || 0,
    totalFte2026: fteByYear['2026'] || 0,
    totalFte2027: fteByYear['2027'] || 0
  };
}

// Main test function
async function runTests() {
  console.log('🚀 Starting Simulation Verification Tests\n');

  try {
    // Test 1: Baseline scenario
    console.log('📊 Test 1: Baseline Scenario');
    const baselineScenario = createScenario(
      'Baseline Test',
      createBaselineInput(1.0, 1.0),
      createLevers(1.0, 1.0, 1.0)
    );
    
    const baselineResponse = await runScenarioDefinition(baselineScenario);
    const baselineMetrics = extractMetrics(baselineResponse);
    
    console.log(`✅ Baseline Results: 2025=${baselineMetrics.totalFte2025}, 2026=${baselineMetrics.totalFte2026}, 2027=${baselineMetrics.totalFte2027}\n`);

    // Test 2: High recruitment scenario
    console.log('📈 Test 2: High Recruitment Scenario (1.5x multiplier)');
    const highRecruitmentScenario = createScenario(
      'High Recruitment Test',
      createBaselineInput(1.5, 1.0),
      createLevers(1.5, 1.0, 1.0)
    );
    
    const highRecruitmentResponse = await runScenarioDefinition(highRecruitmentScenario);
    const highRecruitmentMetrics = extractMetrics(highRecruitmentResponse);
    
    console.log(`✅ High Recruitment Results: 2025=${highRecruitmentMetrics.totalFte2025}, 2026=${highRecruitmentMetrics.totalFte2026}, 2027=${highRecruitmentMetrics.totalFte2027}`);
    
    const recruitmentIncrease = ((highRecruitmentMetrics.totalFte2027 - baselineMetrics.totalFte2027) / baselineMetrics.totalFte2027 * 100);
    console.log(`📊 Increase vs Baseline: ${recruitmentIncrease.toFixed(1)}%\n`);

    // Test 3: Low churn scenario
    console.log('📉 Test 3: Low Churn Scenario (0.5x multiplier)');
    const lowChurnScenario = createScenario(
      'Low Churn Test',
      createBaselineInput(1.0, 0.5),
      createLevers(1.0, 0.5, 1.0)
    );
    
    const lowChurnResponse = await runScenarioDefinition(lowChurnScenario);
    const lowChurnMetrics = extractMetrics(lowChurnResponse);
    
    console.log(`✅ Low Churn Results: 2025=${lowChurnMetrics.totalFte2025}, 2026=${lowChurnMetrics.totalFte2026}, 2027=${lowChurnMetrics.totalFte2027}`);
    
    const churnIncrease = ((lowChurnMetrics.totalFte2027 - baselineMetrics.totalFte2027) / baselineMetrics.totalFte2027 * 100);
    console.log(`📊 Increase vs Baseline: ${churnIncrease.toFixed(1)}%\n`);

    // Analysis
    console.log('🔍 Analysis:');
    console.log(`• Baseline shows ${baselineMetrics.totalFte2025 === baselineMetrics.totalFte2027 ? 'STATIC' : 'DYNAMIC'} values over time`);
    console.log(`• High recruitment ${highRecruitmentMetrics.totalFte2027 > baselineMetrics.totalFte2027 ? 'INCREASES' : 'DOES NOT INCREASE'} FTE`);
    console.log(`• Low churn ${lowChurnMetrics.totalFte2027 > baselineMetrics.totalFte2027 ? 'INCREASES' : 'DOES NOT INCREASE'} FTE`);
    
    const allSame = baselineMetrics.totalFte2027 === highRecruitmentMetrics.totalFte2027 && 
                    baselineMetrics.totalFte2027 === lowChurnMetrics.totalFte2027;
    
    if (allSame) {
      console.log('❌ PROBLEM DETECTED: All scenarios produce identical results!');
      console.log('   This suggests the simulation engine is not applying lever multipliers correctly.');
    } else {
      console.log('✅ SUCCESS: Different scenarios produce different results!');
    }

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.error('Stack trace:', error.stack);
  }
}

// Run the tests
runTests();