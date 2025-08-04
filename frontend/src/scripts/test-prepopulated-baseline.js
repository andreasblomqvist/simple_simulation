/**
 * Test script to verify prepopulated baseline values work correctly
 * This simulates creating a new scenario with default baseline values
 */

const API_BASE = 'http://localhost:8000';

async function testPrepopulatedBaseline() {
  console.log('🧪 Testing Prepopulated Baseline Values\n');

  // This simulates what the UI should generate with default prepopulated values
  const scenario = {
    id: 'prepopulated-test-123',
    name: 'Prepopulated Baseline Test',
    description: 'Testing prepopulated baseline values from UI defaults',
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
                    '202501': 20,  // From recruitmentDefaults
                    '202502': 20,
                    '202503': 10
                  }
                },
                churn: {
                  values: {
                    '202501': 2,   // From leaversDefaults
                    '202502': 2,
                    '202503': 2
                  }
                }
              },
              AC: {
                recruitment: {
                  values: {
                    '202501': 8,
                    '202502': 8,
                    '202503': 8
                  }
                },
                churn: {
                  values: {
                    '202501': 4,
                    '202502': 4,
                    '202503': 4
                  }
                }
              }
            }
          },
          Sales: {
            levels: {
              A: {
                recruitment: {
                  values: {
                    '202501': 5,   // From salesRecruitmentDefaults
                    '202502': 5,
                    '202503': 5
                  }
                },
                churn: {
                  values: {
                    '202501': 1,   // From salesChurnDefaults
                    '202502': 1,
                    '202503': 1
                  }
                }
              }
            }
          },
          Recruitment: {
            levels: {
              A: {
                recruitment: {
                  values: {
                    '202501': 3,   // From recruitmentRecruitmentDefaults
                    '202502': 3,
                    '202503': 3
                  }
                },
                churn: {
                  values: {
                    '202501': 1,   // From recruitmentChurnDefaults
                    '202502': 1,
                    '202503': 1
                  }
                }
              }
            }
          }
        },
        churn: {
          // Same structure as recruitment (as per our BaselineInputGrid implementation)
          Consultant: {
            levels: {
              A: {
                recruitment: {
                  values: {
                    '202501': 20,
                    '202502': 20,
                    '202503': 10
                  }
                },
                churn: {
                  values: {
                    '202501': 2,
                    '202502': 2,
                    '202503': 2
                  }
                }
              },
              AC: {
                recruitment: {
                  values: {
                    '202501': 8,
                    '202502': 8,
                    '202503': 8
                  }
                },
                churn: {
                  values: {
                    '202501': 4,
                    '202502': 4,
                    '202503': 4
                  }
                }
              }
            }
          },
          Sales: {
            levels: {
              A: {
                recruitment: {
                  values: {
                    '202501': 5,
                    '202502': 5,
                    '202503': 5
                  }
                },
                churn: {
                  values: {
                    '202501': 1,
                    '202502': 1,
                    '202503': 1
                  }
                }
              }
            }
          },
          Recruitment: {
            levels: {
              A: {
                recruitment: {
                  values: {
                    '202501': 3,
                    '202502': 3,
                    '202503': 3
                  }
                },
                churn: {
                  values: {
                    '202501': 1,
                    '202502': 1,
                    '202503': 1
                  }
                }
              }
            }
          }
        }
      }
    },
    levers: {
      recruitment: { A: 1.0, AC: 1.0, C: 1.0 },
      churn: { A: 1.0, AC: 1.0, C: 1.0 },
      progression: { A: 1.0, AC: 1.0, C: 1.0 }
    },
    economic_params: {}
  };

  console.log('📤 Sending scenario with prepopulated baseline values:');
  console.log('  • Consultant A: 20 recruitment, 2 churn');
  console.log('  • Consultant AC: 8 recruitment, 4 churn');
  console.log('  • Sales A: 5 recruitment, 1 churn');
  console.log('  • Recruitment A: 3 recruitment, 1 churn');
  console.log('  • No levers applied (all 1.0x)');
  console.log('  • Expected: Results should match baseline values\n');

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
      
      // Analyze results for different roles
      if (simData.results && simData.results.years && simData.results.years['2025']) {
        const stockholmOffice = simData.results.years['2025'].offices?.Stockholm;
        if (stockholmOffice && stockholmOffice.roles) {
          console.log('\n📈 Simulation Results Summary:');
          
          // Check Consultant results
          const consultantA = stockholmOffice.roles.Consultant?.A?.[0];
          if (consultantA) {
            console.log(`  • Consultant A - Recruitment: ${consultantA.recruitment}, Churn: ${consultantA.churn}`);
          }
          
          const consultantAC = stockholmOffice.roles.Consultant?.AC?.[0];
          if (consultantAC) {
            console.log(`  • Consultant AC - Recruitment: ${consultantAC.recruitment}, Churn: ${consultantAC.churn}`);
          }
          
          // Check Sales results
          const salesA = stockholmOffice.roles.Sales?.A?.[0];
          if (salesA) {
            console.log(`  • Sales A - Recruitment: ${salesA.recruitment}, Churn: ${salesA.churn}`);
          }
          
          // Check Recruitment results
          const recruitmentA = stockholmOffice.roles.Recruitment?.A?.[0];
          if (recruitmentA) {
            console.log(`  • Recruitment A - Recruitment: ${recruitmentA.recruitment}, Churn: ${recruitmentA.churn}`);
          }
          
          console.log('\n🎯 Verification:');
          
          // Verify that baseline values are being used correctly
          const consultantOk = consultantA && consultantA.recruitment === 20 && consultantA.churn === 2;
          const salesOk = salesA && salesA.recruitment === 5 && salesA.churn === 1;
          const recruitmentOk = recruitmentA && recruitmentA.recruitment === 3 && recruitmentA.churn === 1;
          
          console.log(`  • Consultant baseline values: ${consultantOk ? '✅ CORRECT' : '❌ INCORRECT'}`);
          console.log(`  • Sales baseline values: ${salesOk ? '✅ CORRECT' : '❌ INCORRECT'}`);
          console.log(`  • Recruitment baseline values: ${recruitmentOk ? '✅ CORRECT' : '❌ INCORRECT'}`);
          
          if (consultantOk && salesOk && recruitmentOk) {
            console.log('\n🎉 SUCCESS: Prepopulated baseline values are working correctly!');
          } else {
            console.log('\n⚠️  Some baseline values may need adjustment');
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
testPrepopulatedBaseline();