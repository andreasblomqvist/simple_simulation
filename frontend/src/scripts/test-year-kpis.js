/**
 * Test script to verify that KPIs are included in each year's simulation results
 * This addresses the user's correction that "simulation results include kpis for each year"
 */

const API_BASE = 'http://localhost:8000';

async function testYearKPIs() {
  console.log('🔍 Testing Year-Specific KPI Generation\n');

  // Use the exact structure that BaselineInputGrid generates after our fix
  const scenario = {
    id: 'year-kpi-test',
    name: 'Year KPI Test',
    description: 'Testing KPIs embedded in yearly results',
    time_range: {
      start_year: 2025,
      start_month: 1,
      end_year: 2026,
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
                    '202501': 20, '202502': 20, '202503': 10, '202504': 15,
                    '202505': 10, '202506': 10, '202507': 5, '202508': 20,
                    '202509': 90, '202510': 20, '202511': 15, '202512': 10,
                    '202601': 20, '202602': 20, '202603': 10, '202604': 15,
                    '202605': 10, '202606': 10, '202607': 5, '202608': 20,
                    '202609': 90, '202610': 20, '202611': 15, '202612': 10
                  }
                },
                churn: {
                  values: {
                    '202501': 2, '202502': 2, '202503': 2, '202504': 2,
                    '202505': 2, '202506': 2, '202507': 4, '202508': 2,
                    '202509': 2, '202510': 2, '202511': 4, '202512': 2,
                    '202601': 2, '202602': 2, '202603': 2, '202604': 2,
                    '202605': 2, '202606': 2, '202607': 4, '202608': 2,
                    '202609': 2, '202610': 2, '202611': 4, '202612': 2
                  }
                }
              },
              AC: {
                recruitment: {
                  values: {
                    '202501': 8, '202502': 8, '202503': 8, '202504': 8,
                    '202505': 8, '202506': 8, '202507': 8, '202508': 8,
                    '202509': 8, '202510': 8, '202511': 8, '202512': 8,
                    '202601': 8, '202602': 8, '202603': 8, '202604': 8,
                    '202605': 8, '202606': 8, '202607': 8, '202608': 8,
                    '202609': 8, '202610': 8, '202611': 8, '202612': 8
                  }
                },
                churn: {
                  values: {
                    '202501': 4, '202502': 4, '202503': 4, '202504': 4,
                    '202505': 4, '202506': 4, '202507': 4, '202508': 4,
                    '202509': 4, '202510': 4, '202511': 4, '202512': 4,
                    '202601': 4, '202602': 4, '202603': 4, '202604': 4,
                    '202605': 4, '202606': 4, '202607': 4, '202608': 4,
                    '202609': 4, '202610': 4, '202611': 4, '202612': 4
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
                    '202501': 20, '202502': 20, '202503': 10, '202504': 15,
                    '202505': 10, '202506': 10, '202507': 5, '202508': 20,
                    '202509': 90, '202510': 20, '202511': 15, '202512': 10,
                    '202601': 20, '202602': 20, '202603': 10, '202604': 15,
                    '202605': 10, '202606': 10, '202607': 5, '202608': 20,
                    '202609': 90, '202610': 20, '202611': 15, '202612': 10
                  }
                },
                churn: {
                  values: {
                    '202501': 2, '202502': 2, '202503': 2, '202504': 2,
                    '202505': 2, '202506': 2, '202507': 4, '202508': 2,
                    '202509': 2, '202510': 2, '202511': 4, '202512': 2,
                    '202601': 2, '202602': 2, '202603': 2, '202604': 2,
                    '202605': 2, '202606': 2, '202607': 4, '202608': 2,
                    '202609': 2, '202610': 2, '202611': 4, '202612': 2
                  }
                }
              },
              AC: {
                recruitment: {
                  values: {
                    '202501': 8, '202502': 8, '202503': 8, '202504': 8,
                    '202505': 8, '202506': 8, '202507': 8, '202508': 8,
                    '202509': 8, '202510': 8, '202511': 8, '202512': 8,
                    '202601': 8, '202602': 8, '202603': 8, '202604': 8,
                    '202605': 8, '202606': 8, '202607': 8, '202608': 8,
                    '202609': 8, '202610': 8, '202611': 8, '202612': 8
                  }
                },
                churn: {
                  values: {
                    '202501': 4, '202502': 4, '202503': 4, '202504': 4,
                    '202505': 4, '202506': 4, '202507': 4, '202508': 4,
                    '202509': 4, '202510': 4, '202511': 4, '202512': 4,
                    '202601': 4, '202602': 4, '202603': 4, '202604': 4,
                    '202605': 4, '202606': 4, '202607': 4, '202608': 4,
                    '202609': 4, '202610': 4, '202611': 4, '202612': 4
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

  console.log('📤 Testing KPI structure in yearly results:');
  console.log('  • Net growth: A=+18/month, AC=+4/month (+22 total)');
  console.log('  • Multi-year: 2025-2026 (2 years)');
  console.log('  • Expected: KPIs embedded in each year data\n');

  try {
    console.log('🚀 Running scenario...');
    
    const request = { scenario_definition: scenario };
    const simResponse = await fetch(`${API_BASE}/scenarios/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });

    if (simResponse.ok) {
      const simData = await simResponse.json();
      console.log('✅ Simulation completed');
      
      // Check the top-level structure
      console.log('\n🔍 Response Structure Analysis:');
      console.log('Response keys:', Object.keys(simData));
      
      // Look for years and KPIs within them
      if (simData.results && simData.results.years) {
        const years = Object.keys(simData.results.years).sort();
        console.log(`\n📅 Years found: ${years.join(', ')}`);
        
        years.forEach(year => {
          const yearData = simData.results.years[year];
          console.log(`\n📊 ${year} Analysis:`);
          console.log(`   Structure keys: [${Object.keys(yearData).join(', ')}]`);
          
          if (yearData.kpis) {
            console.log('   ✅ KPIs found in year data');
            console.log(`   KPI categories: [${Object.keys(yearData.kpis).join(', ')}]`);
            
            // Show financial KPIs if available
            if (yearData.kpis.financial) {
              const financial = yearData.kpis.financial;
              console.log(`   💰 Financial KPIs:`);
              console.log(`      • Net Sales: ${financial.net_sales?.toLocaleString('sv-SE') || 'N/A'} SEK`);
              console.log(`      • EBITDA: ${financial.ebitda?.toLocaleString('sv-SE') || 'N/A'} SEK`);
              console.log(`      • Margin: ${(financial.margin * 100)?.toFixed(1) || 'N/A'}%`);
              console.log(`      • Total Consultants: ${financial.total_consultants || 'N/A'}`);
            }
            
            // Show growth KPIs if available
            if (yearData.kpis.growth) {
              const growth = yearData.kpis.growth;
              console.log(`   📈 Growth KPIs:`);
              console.log(`      • FTE Growth: ${(growth.fte_growth * 100)?.toFixed(1) || 'N/A'}%`);
              console.log(`      • Revenue Growth: ${(growth.revenue_growth * 100)?.toFixed(1) || 'N/A'}%`);
            }
            
          } else {
            console.log('   ❌ No KPIs found in year data');
            console.log('   Available keys:', Object.keys(yearData));
          }
        });
        
        // Overall assessment
        const hasKPIs = years.every(year => simData.results.years[year].kpis);
        if (hasKPIs) {
          console.log('\n🎉 SUCCESS: KPIs are correctly embedded in each year\'s results!');
        } else {
          console.log('\n❌ ISSUE: Some years are missing KPI data');
        }
      } else {
        console.log('\n❌ No yearly results found in response');
        console.log('Full response structure:', JSON.stringify(simData, null, 2));
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

// Run the test
testYearKPIs();