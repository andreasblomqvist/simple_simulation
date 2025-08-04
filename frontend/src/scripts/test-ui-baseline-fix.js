/**
 * Test script to verify the UI baseline_input structure fix
 * This simulates what the UI should now generate
 */

const API_BASE = 'http://localhost:8000';

async function testUIBaselineStructure() {
  console.log('🧪 Testing UI Baseline Structure Fix\n');

  // This is the structure the fixed BaselineInputGrid should now generate
  const scenario = {
    id: 'ui-test-fixed-structure',
    name: 'UI Test - Fixed Structure',
    description: 'Testing UI with corrected nested baseline_input structure',
    time_range: {
      start_year: 2025,
      start_month: 1,
      end_year: 2025,
      end_month: 3
    },
    office_scope: ['Stockholm'],
    baseline_input: {
      global_data: {
        recruitment: {
          Consultant: {
            levels: {
              A: {
                recruitment: {
                  values: {
                    '202501': 20.0,
                    '202502': 20.0,
                    '202503': 20.0
                  }
                },
                churn: {
                  values: {
                    '202501': 2.0,
                    '202502': 2.0,
                    '202503': 2.0
                  }
                }
              }
            }
          }
        },
        churn: {
          Consultant: {
            levels: {
              A: {
                recruitment: {
                  values: {
                    '202501': 20.0,
                    '202502': 20.0,
                    '202503': 20.0
                  }
                },
                churn: {
                  values: {
                    '202501': 2.0,
                    '202502': 2.0,
                    '202503': 2.0
                  }
                }
              }
            }
          }
        }
      }
    },
    levers: {
      recruitment: { A: 2.0, AC: 1.0, C: 1.0 },
      churn: { A: 0.5, AC: 1.0, C: 1.0 },
      progression: { A: 1.0, AC: 1.0, C: 1.0 }
    },
    economic_params: {}
  };

  console.log('📤 Sending UI scenario with fixed structure:');
  console.log('  • Using global_data format (not global)');
  console.log('  • Using levels → A → recruitment/churn → values structure');
  console.log('  • Baseline recruitment A: 20/month');
  console.log('  • Baseline churn A: 2/month');
  console.log('  • Levers: A recruitment x2.0, A churn x0.5');
  console.log('  • Expected: A recruitment=40, A churn=1\n');

  try {
    console.log('🚀 Running simulation...');
    
    const request = { scenario_definition: scenario };
    const simResponse = await fetch(`${API_BASE}/scenarios/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });

    if (simResponse.ok) {
      const simData = await simResponse.json();
      console.log('✅ Simulation completed successfully');
      
      // Analyze results
      if (simData.results && simData.results.years && simData.results.years['2025']) {
        const stockholmOffice = simData.results.years['2025'].offices?.Stockholm;
        if (stockholmOffice && stockholmOffice.roles && stockholmOffice.roles.Consultant) {
          const consultantA = stockholmOffice.roles.Consultant.A;
          if (consultantA && consultantA.length > 0) {
            console.log('\n📈 Simulation Results - Consultant Level A:');
            consultantA.slice(0, 3).forEach((month, i) => {
              console.log(`  Month ${i+1}: FTE=${month.fte}, Recruitment=${month.recruitment}, Churn=${month.churn}`);
            });
            
            // Check if lever effects applied
            const firstMonth = consultantA[0];
            const expectedRecruitment = 20 * 2.0; // baseline * lever
            const expectedChurn = 2 * 0.5; // baseline * lever
            
            console.log('\n🎯 Verification:');
            console.log(`  • Expected recruitment: ${expectedRecruitment} (20 * 2.0 lever)`);
            console.log(`  • Actual recruitment: ${firstMonth.recruitment}`);
            console.log(`  • Expected churn: ${expectedChurn} (2 * 0.5 lever)`);
            console.log(`  • Actual churn: ${firstMonth.churn}`);
            
            const recruitmentMatch = Math.abs(firstMonth.recruitment - expectedRecruitment) < 0.1;
            const churnMatch = Math.abs(firstMonth.churn - expectedChurn) < 0.1;
            
            if (recruitmentMatch && churnMatch) {
              console.log('\n🎉 SUCCESS: UI baseline_input structure fix WORKS!');
              console.log('   Levers are now properly applied to simulation results.');
            } else {
              console.log('\n❌ ISSUE: Results still don\'t match expected values');
              console.log('   UI structure may need further fixes or backend processing issue.');
            }
          }
        }
      }
    } else {
      console.log('❌ Simulation failed:', simResponse.status);
      try {
        const errorData = await simResponse.json();
        console.log('Error details:', JSON.stringify(errorData, null, 2));
      } catch (e) {
        console.log('Could not parse error response');
      }
    }

  } catch (error) {
    console.error('❌ Test failed:', error.message);
  }
}

// Run the test
testUIBaselineStructure();