/**
 * Simple test to verify lever and baseline data application
 * This focuses on the core issue: backend not applying the input data
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

  const response = await fetch(url, config);
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(`HTTP ${response.status}: ${errorData.detail || response.statusText}`);
  }

  return await response.json();
}

// Simple test with minimal data
async function testBasicScenario() {
  console.log('🧪 Testing Basic Scenario with Minimal Data\n');

  const scenario = {
    id: 'simple-test-123',
    name: 'Simple Test',
    description: 'Minimal test scenario',
    time_range: {
      start_year: 2025,
      start_month: 1,
      end_year: 2025,
      end_month: 3
    },
    office_scope: ['Group'],
    baseline_input: {
      global_data: {
        recruitment: {
          Consultant: {
            '202501': { A: 10, AC: 5, C: 2 },
            '202502': { A: 10, AC: 5, C: 2 },
            '202503': { A: 10, AC: 5, C: 2 }
          },
          Sales: {
            '202501': {},
            '202502': {},
            '202503': {}
          },
          Recruitment: {
            '202501': {},
            '202502': {},
            '202503': {}
          }
        },
        churn: {
          Consultant: {
            '202501': { A: 1, AC: 2, C: 3 },
            '202502': { A: 1, AC: 2, C: 3 },
            '202503': { A: 1, AC: 2, C: 3 }
          },
          Sales: {
            '202501': {},
            '202502': {},
            '202503': {}
          },
          Recruitment: {
            '202501': {},
            '202502': {},
            '202503': {}
          }
        }
      }
    },
    levers: {
      recruitment: { A: 2.0, AC: 1.5, C: 1.0 }, // 2x recruitment for A, 1.5x for AC
      churn: { A: 0.5, AC: 1.0, C: 1.0 }, // Half churn for A
      progression: { A: 1.0, AC: 1.0, C: 1.0 }
    },
    economic_params: {}
  };

  console.log('📤 Sending scenario with:');
  console.log('  • Baseline recruitment A: 10/month, AC: 5/month, C: 2/month');
  console.log('  • Baseline churn A: 1/month, AC: 2/month, C: 3/month');
  console.log('  • Levers: A recruitment x2.0, A churn x0.5');
  console.log('  • Expected: A should have 20 recruitment, 0.5 churn per month\n');

  try {
    const request = {
      scenario_definition: scenario
    };

    console.log('⏳ Running simulation...');
    const response = await apiRequest('/run', {
      method: 'POST',
      body: JSON.stringify(request),
    });

    console.log('✅ Simulation completed');
    console.log('📊 Response status:', response.status || response.scenario_id ? 'success' : 'unknown');

    // Check if we have results
    if (response.results && response.results.years) {
      const year2025 = response.results.years['2025'];
      
      if (year2025 && year2025.offices) {
        console.log('\n🔍 Analyzing Results:');
        
        // Look at any office (Stockholm is usually first)
        const office = Object.values(year2025.offices)[0];
        
        if (office.roles && office.roles.Consultant) {
          const consultantA = office.roles.Consultant.A;
          
          if (consultantA && consultantA.length > 0) {
            console.log('\n📈 Consultant Level A Results:');
            consultantA.slice(0, 3).forEach((month, i) => {
              console.log(`  Month ${i+1}: FTE=${month.fte}, Recruitment=${month.recruitment}, Churn=${month.churn}`);
            });

            // Check if recruitment/churn are being applied
            const hasRecruitment = consultantA.some(m => m.recruitment > 0);
            const hasChurn = consultantA.some(m => m.churn > 0);
            
            console.log('\n🎯 Key Findings:');
            console.log(`  • Recruitment applied: ${hasRecruitment ? '✅ YES' : '❌ NO'}`);
            console.log(`  • Churn applied: ${hasChurn ? '✅ YES' : '❌ NO'}`);
            
            if (!hasRecruitment && !hasChurn) {
              console.log('\n❌ CRITICAL ISSUE CONFIRMED:');
              console.log('   The simulation engine is NOT applying baseline input data or levers!');
              console.log('   All recruitment and churn values are 0, indicating the data is ignored.');
            } else {
              console.log('\n✅ SUCCESS: Simulation engine is processing the input data!');
            }
          } else {
            console.log('❌ No Consultant A data found in results');
          }
        } else {
          console.log('❌ No Consultant roles found in results');
        }
      } else {
        console.log('❌ No offices found in results');
      }
    } else {
      console.log('❌ No results found in response');
    }

  } catch (error) {
    console.error('❌ Test failed:', error.message);
  }
}

// Run the test
testBasicScenario();