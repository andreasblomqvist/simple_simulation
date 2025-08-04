/**
 * Debug script to test current UI-generated baseline_input structure
 * This should help us understand why the simulation results are still static
 */

const API_BASE = 'http://localhost:8000';

async function debugUIStructure() {
  console.log('🔍 Debugging UI-Generated Baseline Structure\n');

  // This matches exactly what our updated BaselineInputGrid should generate
  const scenario = {
    id: 'ui-debug-structure',
    name: 'UI Debug Structure',
    description: 'Testing UI-generated structure with debug logging',
    time_range: {
      start_year: 2025,
      start_month: 1,
      end_year: 2027,
      end_month: 12
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
                    '202501': 20,
                    '202502': 20,
                    '202503': 10,
                    '202504': 15,
                    '202505': 10,
                    '202506': 10,
                    '202507': 5,
                    '202508': 20,
                    '202509': 90,
                    '202510': 20,
                    '202511': 15,
                    '202512': 10
                  }
                },
                churn: {
                  values: {
                    '202501': 2,
                    '202502': 2,
                    '202503': 2,
                    '202504': 2,
                    '202505': 2,
                    '202506': 2,
                    '202507': 4,
                    '202508': 2,
                    '202509': 2,
                    '202510': 2,
                    '202511': 4,
                    '202512': 2
                  }
                }
              },
              AC: {
                recruitment: {
                  values: {
                    '202501': 8,
                    '202502': 8,
                    '202503': 8,
                    '202504': 8,
                    '202505': 8,
                    '202506': 8,
                    '202507': 8,
                    '202508': 8,
                    '202509': 8,
                    '202510': 8,
                    '202511': 8,
                    '202512': 8
                  }
                },
                churn: {
                  values: {
                    '202501': 4,
                    '202502': 4,
                    '202503': 4,
                    '202504': 4,
                    '202505': 4,
                    '202506': 4,
                    '202507': 4,
                    '202508': 4,
                    '202509': 4,
                    '202510': 4,
                    '202511': 4,
                    '202512': 4
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
                    '202501': 20,
                    '202502': 20,
                    '202503': 10,
                    '202504': 15,
                    '202505': 10,
                    '202506': 10,
                    '202507': 5,
                    '202508': 20,
                    '202509': 90,
                    '202510': 20,
                    '202511': 15,
                    '202512': 10
                  }
                },
                churn: {
                  values: {
                    '202501': 2,
                    '202502': 2,
                    '202503': 2,
                    '202504': 2,
                    '202505': 2,
                    '202506': 2,
                    '202507': 4,
                    '202508': 2,
                    '202509': 2,
                    '202510': 2,
                    '202511': 4,
                    '202512': 2
                  }
                }
              },
              AC: {
                recruitment: {
                  values: {
                    '202501': 8,
                    '202502': 8,
                    '202503': 8,
                    '202504': 8,
                    '202505': 8,
                    '202506': 8,
                    '202507': 8,
                    '202508': 8,
                    '202509': 8,
                    '202510': 8,
                    '202511': 8,
                    '202512': 8
                  }
                },
                churn: {
                  values: {
                    '202501': 4,
                    '202502': 4,
                    '202503': 4,
                    '202504': 4,
                    '202505': 4,
                    '202506': 4,
                    '202507': 4,
                    '202508': 4,
                    '202509': 4,
                    '202510': 4,
                    '202511': 4,
                    '202512': 4
                  }
                }
              }
            }
          }
        }
      }
    },
    levers: {
      recruitment: { A: 1.0, AC: 1.0, C: 1.0, SrC: 1.0, AM: 1.0, M: 1.0, SrM: 1.0, PiP: 1.0 },
      churn: { A: 1.0, AC: 1.0, C: 1.0, SrC: 1.0, AM: 1.0, M: 1.0, SrM: 1.0, PiP: 1.0 },
      progression: { A: 1.0, AC: 1.0, C: 1.0, SrC: 1.0, AM: 1.0, M: 1.0, SrM: 1.0, PiP: 1.0 }
    },
    economic_params: {
      working_hours_per_month: 160.0,
      employment_cost_rate: 0.3,
      unplanned_absence: 0.05,
      other_expense: 1000000.0
    }
  };

  console.log('📤 Sending UI-style scenario with full multi-year data:');
  console.log('  • Structure matches BaselineInputGrid output');
  console.log('  • Contains realistic monthly patterns (Sep: 90, Mar: 10, etc.)');
  console.log('  • Time range: 2025-2027 (3 years)');
  console.log('  • Expected: Should see significant growth with recruitment > churn\\n');

  try {
    console.log('🚀 Running simulation with debug logging...');
    
    const request = { scenario_definition: scenario };
    const simResponse = await fetch(`${API_BASE}/scenarios/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });

    if (simResponse.ok) {
      const simData = await simResponse.json();
      console.log('✅ Simulation completed');
      
      // Analyze key results
      if (simData.results && simData.results.years) {
        const years = Object.keys(simData.results.years).sort();
        console.log('\\n📊 Multi-Year Analysis:');
        
        years.forEach(year => {
          const yearData = simData.results.years[year];
          const stockholmOffice = yearData.offices?.Stockholm;
          if (stockholmOffice && stockholmOffice.roles && stockholmOffice.roles.Consultant) {
            const consultantA = stockholmOffice.roles.Consultant.A;
            if (consultantA && consultantA.length > 0) {
              // Check first and last month of the year for growth
              const firstMonth = consultantA[0];
              const lastMonth = consultantA[consultantA.length - 1];
              const yearlyGrowth = lastMonth.fte - firstMonth.fte;
              
              console.log(`  ${year}: Start FTE=${firstMonth.fte}, End FTE=${lastMonth.fte}, Growth=${yearlyGrowth}`);
              console.log(`         Jan: R=${firstMonth.recruitment}, C=${firstMonth.churn}`);
              
              // Check September (should have high recruitment = 90)
              if (consultantA.length >= 9) {
                const september = consultantA[8]; // 0-indexed, so 8 = September
                console.log(`         Sep: R=${september.recruitment}, C=${september.churn} (should be R=90)`);
              }
            }
          }
        });
        
        // Overall growth check
        const firstYear = years[0];
        const lastYear = years[years.length - 1];
        const startFTE = simData.results.years[firstYear]?.offices?.Stockholm?.roles?.Consultant?.A?.[0]?.fte || 0;
        const endFTE = simData.results.years[lastYear]?.offices?.Stockholm?.roles?.Consultant?.A?.[11]?.fte || 0;
        const totalGrowth = endFTE - startFTE;
        
        console.log('\\n🎯 Overall Assessment:');
        console.log(`  • Start FTE (${firstYear} Jan): ${startFTE}`);
        console.log(`  • End FTE (${lastYear} Dec): ${endFTE}`);
        console.log(`  • Total Growth: ${totalGrowth} (+${((totalGrowth/startFTE)*100).toFixed(1)}%)`);
        
        if (totalGrowth > 100) {
          console.log('\\n🎉 SUCCESS: Simulation is processing baseline data correctly!');
          console.log('   The UI structure fix is working.');
        } else if (totalGrowth > 0) {
          console.log('\\n⚠️  PARTIAL: Some growth detected, but may need adjustment');
        } else {
          console.log('\\n❌ ISSUE: No growth detected - baseline data not being processed');
          console.log('   Check backend logs for scenario resolver debug output');
        }
      }
    } else {
      console.log('❌ Simulation failed:', simResponse.status);
      try {
        const errorData = await simResponse.json();
        console.log('Error details:', JSON.stringify(errorData, null, 2));
      } catch (e) {
        const text = await simResponse.text();
        console.log('Error response:', text);
      }
    }

  } catch (error) {
    console.error('❌ Test failed:', error.message);
  }
}

// Run the debug test
debugUIStructure();