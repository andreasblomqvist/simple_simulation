/**
 * Test script with realistic churn values matching the original defaults
 */

const API_BASE = 'http://localhost:8000';

async function testRealisticChurn() {
  console.log('🧪 Testing with Realistic Churn Values\n');

  // Using the exact churn values from leaversDefaults in BaselineInputGrid
  const scenario = {
    id: 'realistic-churn-test',
    name: 'Realistic Churn Test',
    description: 'Testing with original high churn values',
    time_range: {
      start_year: 2025,
      start_month: 1,
      end_year: 2025,
      end_month: 12
    },
    office_scope: ['Stockholm'],
    baseline_input: {
      global_data: {
        recruitment: {
          Consultant: {
            levels: {
              A: {
                recruitment: { values: { '202501': 20, '202502': 20, '202503': 10, '202504': 15, '202505': 10, '202506': 10, '202507': 5, '202508': 20, '202509': 90, '202510': 20, '202511': 15, '202512': 10 } },
                churn: { values: { '202501': 2, '202502': 2, '202503': 2, '202504': 2, '202505': 2, '202506': 2, '202507': 4, '202508': 2, '202509': 2, '202510': 2, '202511': 4, '202512': 2 } }
              },
              AC: {
                recruitment: { values: { '202501': 8, '202502': 8, '202503': 8, '202504': 8, '202505': 8, '202506': 8, '202507': 8, '202508': 8, '202509': 8, '202510': 8, '202511': 8, '202512': 8 } },
                churn: { values: { '202501': 4, '202502': 4, '202503': 4, '202504': 4, '202505': 4, '202506': 4, '202507': 4, '202508': 4, '202509': 4, '202510': 4, '202511': 4, '202512': 4 } }
              },
              C: {
                recruitment: { values: { '202501': 4, '202502': 4, '202503': 4, '202504': 4, '202505': 4, '202506': 4, '202507': 4, '202508': 4, '202509': 4, '202510': 4, '202511': 4, '202512': 4 } },
                churn: { values: { '202501': 7, '202502': 7, '202503': 7, '202504': 7, '202505': 7, '202506': 7, '202507': 7, '202508': 7, '202509': 7, '202510': 7, '202511': 7, '202512': 7 } }
              },
              SrC: {
                recruitment: { values: { '202501': 1, '202502': 1, '202503': 1, '202504': 1, '202505': 1, '202506': 1, '202507': 1, '202508': 1, '202509': 1, '202510': 1, '202511': 1, '202512': 1 } },
                churn: { values: { '202501': 7, '202502': 7, '202503': 7, '202504': 7, '202505': 7, '202506': 7, '202507': 7, '202508': 7, '202509': 7, '202510': 7, '202511': 7, '202512': 7 } }
              },
              AM: {
                recruitment: { values: { '202501': 1, '202502': 1, '202503': 1, '202504': 1, '202505': 1, '202506': 1, '202507': 1, '202508': 1, '202509': 1, '202510': 1, '202511': 1, '202512': 1 } },
                churn: { values: { '202501': 9, '202502': 9, '202503': 9, '202504': 9, '202505': 9, '202506': 9, '202507': 9, '202508': 9, '202509': 9, '202510': 9, '202511': 9, '202512': 9 } }
              }
            }
          }
        },
        churn: {
          Consultant: {
            levels: {
              A: {
                recruitment: { values: { '202501': 20, '202502': 20, '202503': 10, '202504': 15, '202505': 10, '202506': 10, '202507': 5, '202508': 20, '202509': 90, '202510': 20, '202511': 15, '202512': 10 } },
                churn: { values: { '202501': 2, '202502': 2, '202503': 2, '202504': 2, '202505': 2, '202506': 2, '202507': 4, '202508': 2, '202509': 2, '202510': 2, '202511': 4, '202512': 2 } }
              },
              AC: {
                recruitment: { values: { '202501': 8, '202502': 8, '202503': 8, '202504': 8, '202505': 8, '202506': 8, '202507': 8, '202508': 8, '202509': 8, '202510': 8, '202511': 8, '202512': 8 } },
                churn: { values: { '202501': 4, '202502': 4, '202503': 4, '202504': 4, '202505': 4, '202506': 4, '202507': 4, '202508': 4, '202509': 4, '202510': 4, '202511': 4, '202512': 4 } }
              },
              C: {
                recruitment: { values: { '202501': 4, '202502': 4, '202503': 4, '202504': 4, '202505': 4, '202506': 4, '202507': 4, '202508': 4, '202509': 4, '202510': 4, '202511': 4, '202512': 4 } },
                churn: { values: { '202501': 7, '202502': 7, '202503': 7, '202504': 7, '202505': 7, '202506': 7, '202507': 7, '202508': 7, '202509': 7, '202510': 7, '202511': 7, '202512': 7 } }
              },
              SrC: {
                recruitment: { values: { '202501': 1, '202502': 1, '202503': 1, '202504': 1, '202505': 1, '202506': 1, '202507': 1, '202508': 1, '202509': 1, '202510': 1, '202511': 1, '202512': 1 } },
                churn: { values: { '202501': 7, '202502': 7, '202503': 7, '202504': 7, '202505': 7, '202506': 7, '202507': 7, '202508': 7, '202509': 7, '202510': 7, '202511': 7, '202512': 7 } }
              },
              AM: {
                recruitment: { values: { '202501': 1, '202502': 1, '202503': 1, '202504': 1, '202505': 1, '202506': 1, '202507': 1, '202508': 1, '202509': 1, '202510': 1, '202511': 1, '202512': 1 } },
                churn: { values: { '202501': 9, '202502': 9, '202503': 9, '202504': 9, '202505': 9, '202506': 9, '202507': 9, '202508': 9, '202509': 9, '202510': 9, '202511': 9, '202512': 9 } }
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
    economic_params: {}
  };

  console.log('📤 Testing with realistic churn rates:');
  console.log('  • A: 2-4 churn (2 normal, 4 in Jul/Nov)');
  console.log('  • AC: 4 churn (consistent)'); 
  console.log('  • C: 7 churn (high - senior level)');
  console.log('  • SrC: 7 churn (high - senior level)');
  console.log('  • AM: 9 churn (very high - management level)');
  console.log('  • Expected: Much lower net growth due to realistic churn\n');

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
      console.log('✅ Simulation completed');
      
      if (simData.results && simData.results.years && simData.results.years['2025']) {
        const stockholmOffice = simData.results.years['2025'].offices?.Stockholm;
        if (stockholmOffice && stockholmOffice.roles && stockholmOffice.roles.Consultant) {
          console.log('\n📊 Results by Level (Jan 2025):');
          
          ['A', 'AC', 'C', 'SrC', 'AM'].forEach(level => {
            const levelData = stockholmOffice.roles.Consultant[level];
            if (levelData && levelData[0]) {
              const month = levelData[0];
              const netGrowth = month.recruitment - month.churn;
              console.log(`  ${level}: R=${month.recruitment}, C=${month.churn}, Net=${netGrowth > 0 ? '+' : ''}${netGrowth}`);
            }
          });
          
          // Calculate total monthly impact
          let totalRecruitment = 0;
          let totalChurn = 0;
          ['A', 'AC', 'C', 'SrC', 'AM'].forEach(level => {
            const levelData = stockholmOffice.roles.Consultant[level];
            if (levelData && levelData[0]) {
              totalRecruitment += levelData[0].recruitment;
              totalChurn += levelData[0].churn;
            }
          });
          
          const netMonthlyGrowth = totalRecruitment - totalChurn;
          console.log(`\n🎯 Total Monthly Impact (Jan):`);
          console.log(`  • Total Recruitment: ${totalRecruitment}`);
          console.log(`  • Total Churn: ${totalChurn}`);
          console.log(`  • Net Growth: ${netMonthlyGrowth > 0 ? '+' : ''}${netMonthlyGrowth} FTE/month`);
          
          // Check September for peak recruitment
          ['A', 'AC', 'C', 'SrC', 'AM'].forEach(level => {
            const levelData = stockholmOffice.roles.Consultant[level];
            if (levelData && levelData[8]) { // September
              const month = levelData[8];
              if (level === 'A') {
                console.log(`\n📈 September (Peak) - Level A: R=${month.recruitment}, C=${month.churn}, Net=+${month.recruitment - month.churn}`);
              }
            }
          });
          
          console.log(`\n💡 Analysis:`);
          if (netMonthlyGrowth > 0 && netMonthlyGrowth < 10) {
            console.log('  ✅ Realistic growth with proper churn balance');
          } else if (netMonthlyGrowth > 50) {
            console.log('  ⚠️  Growth still too high - churn may not be applied to all levels');
          } else if (netMonthlyGrowth < 0) {
            console.log('  ⚠️  Negative growth - churn exceeds recruitment');
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
testRealisticChurn();