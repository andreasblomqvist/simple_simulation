/**
 * Debug script to check what the scenario resolver produces
 * This will help us understand if baseline_input is being processed correctly
 */

const API_BASE = 'http://localhost:8000';

async function debugScenarioResolver() {
  console.log('🔍 Debugging Scenario Resolver Output\n');

  const scenario = {
    id: 'debug-test-123',
    name: 'Debug Test',
    description: 'Debug scenario resolver',
    time_range: {
      start_year: 2025,
      start_month: 1,
      end_year: 2025,
      end_month: 3
    },
    office_scope: ['Stockholm'],  // Use specific office instead of Group
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
              },
              AC: {
                recruitment: {
                  values: {
                    '202501': 10.0,
                    '202502': 10.0,
                    '202503': 10.0
                  }
                },
                churn: {
                  values: {
                    '202501': 4.0,
                    '202502': 4.0,
                    '202503': 4.0
                  }
                }
              },
              C: {
                recruitment: {
                  values: {
                    '202501': 5.0,
                    '202502': 5.0,
                    '202503': 5.0
                  }
                },
                churn: {
                  values: {
                    '202501': 6.0,
                    '202502': 6.0,
                    '202503': 6.0
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
              },
              AC: {
                recruitment: {
                  values: {
                    '202501': 10.0,
                    '202502': 10.0,
                    '202503': 10.0
                  }
                },
                churn: {
                  values: {
                    '202501': 4.0,
                    '202502': 4.0,
                    '202503': 4.0
                  }
                }
              },
              C: {
                recruitment: {
                  values: {
                    '202501': 5.0,
                    '202502': 5.0,
                    '202503': 5.0
                  }
                },
                churn: {
                  values: {
                    '202501': 6.0,
                    '202502': 6.0,
                    '202503': 6.0
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

  console.log('📤 Sending debug scenario:');
  console.log('  • Office scope: Stockholm (single office for clearer debugging)');
  console.log('  • Baseline recruitment A: 20/month');
  console.log('  • Baseline churn A: 2/month');
  console.log('  • Levers: A recruitment x2.0, A churn x0.5');
  console.log('  • Expected after levers: A recruitment=40, A churn=1\n');

  try {
    console.log('🚀 Running simulation with detailed baseline_input...');
    
    const request = { scenario_definition: scenario };
    const simResponse = await fetch(`${API_BASE}/scenarios/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });

    if (simResponse.ok) {
      const simData = await simResponse.json();
      console.log('✅ Simulation completed');
      
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
            
            // Check if any recruitment or churn happened
            const hasRecruitment = consultantA.some(m => m.recruitment > 0);
            const hasChurn = consultantA.some(m => m.churn > 0);
            
            console.log('\n🎯 Final Analysis:');
            console.log(`  • Recruitment applied: ${hasRecruitment ? '✅ YES' : '❌ NO'}`);
            console.log(`  • Churn applied: ${hasChurn ? '✅ YES' : '❌ NO'}`);
            
            if (!hasRecruitment && !hasChurn) {
              console.log('\n❌ SIMULATION ENGINE ISSUE CONFIRMED:');
              console.log('   Either the scenario resolver is not setting recruitment_abs/churn_abs fields,');
              console.log('   or the simulation engine is not reading them correctly.');
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

// Run the debug test
debugScenarioResolver();