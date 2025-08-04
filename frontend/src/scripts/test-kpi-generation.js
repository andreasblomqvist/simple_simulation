/**
 * Test script to verify KPI generation is working correctly
 * This will examine all KPI values and their calculations
 */

const API_BASE = 'http://localhost:8000';

async function testKPIGeneration() {
  console.log('📊 Testing KPI Generation\n');

  // Use a simple 2-year scenario to test KPI calculations
  const scenario = {
    id: 'kpi-test-scenario',
    name: 'KPI Generation Test',
    description: 'Testing if KPIs are calculated correctly',
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
                recruitment: { values: { '202501': 20, '202502': 20, '202503': 20, '202504': 20, '202505': 20, '202506': 20, '202507': 20, '202508': 20, '202509': 20, '202510': 20, '202511': 20, '202512': 20 } },
                churn: { values: { '202501': 2, '202502': 2, '202503': 2, '202504': 2, '202505': 2, '202506': 2, '202507': 2, '202508': 2, '202509': 2, '202510': 2, '202511': 2, '202512': 2 } }
              },
              AC: {
                recruitment: { values: { '202501': 8, '202502': 8, '202503': 8, '202504': 8, '202505': 8, '202506': 8, '202507': 8, '202508': 8, '202509': 8, '202510': 8, '202511': 8, '202512': 8 } },
                churn: { values: { '202501': 4, '202502': 4, '202503': 4, '202504': 4, '202505': 4, '202506': 4, '202507': 4, '202508': 4, '202509': 4, '202510': 4, '202511': 4, '202512': 4 } }
              }
            }
          }
        },
        churn: {
          Consultant: {
            levels: {
              A: {
                recruitment: { values: { '202501': 20, '202502': 20, '202503': 20, '202504': 20, '202505': 20, '202506': 20, '202507': 20, '202508': 20, '202509': 20, '202510': 20, '202511': 20, '202512': 20 } },
                churn: { values: { '202501': 2, '202502': 2, '202503': 2, '202504': 2, '202505': 2, '202506': 2, '202507': 2, '202508': 2, '202509': 2, '202510': 2, '202511': 2, '202512': 2 } }
              },
              AC: {
                recruitment: { values: { '202501': 8, '202502': 8, '202503': 8, '202504': 8, '202505': 8, '202506': 8, '202507': 8, '202508': 8, '202509': 8, '202510': 8, '202511': 8, '202512': 8 } },
                churn: { values: { '202501': 4, '202502': 4, '202503': 4, '202504': 4, '202505': 4, '202506': 4, '202507': 4, '202508': 4, '202509': 4, '202510': 4, '202511': 4, '202512': 4 } }
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

  console.log('📤 Running KPI test scenario:');
  console.log('  • Consistent recruitment: A=20/month, AC=8/month');
  console.log('  • Consistent churn: A=2/month, AC=4/month');  
  console.log('  • Expected net growth: +22 FTE/month (+264 FTE/year)');
  console.log('  • Time range: 2025-2026 (2 years)');
  console.log('  • Should show clear growth pattern in KPIs\n');

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
      
      // Check if KPIs are included in the response
      console.log('\n🔍 Analyzing Response Structure:');
      console.log('Response keys:', Object.keys(simData));
      
      if (simData.kpis) {
        console.log('✅ KPIs found in response');
        console.log('KPI keys:', Object.keys(simData.kpis));
        
        // Analyze KPI values
        console.log('\n📊 KPI Analysis:');
        console.log('KPIs:', JSON.stringify(simData.kpis, null, 2));
        
      } else {
        console.log('❌ No KPIs found in response');
      }
      
      // Check if aggregate data exists
      if (simData.aggregate_data) {
        console.log('✅ Aggregate data found');
        console.log('Aggregate keys:', Object.keys(simData.aggregate_data));
        console.log('Aggregate data:', JSON.stringify(simData.aggregate_data, null, 2));
      } else {
        console.log('❌ No aggregate data found');
      }
      
      // Analyze detailed results to calculate expected KPIs manually
      if (simData.results && simData.results.years) {
        console.log('\n📈 Manual KPI Calculation:');
        
        const years = Object.keys(simData.results.years).sort();
        let totalFTE = {};
        let totalRevenue = {};
        
        years.forEach(year => {
          const yearData = simData.results.years[year];
          let yearFTE = 0;
          let yearRevenue = 0;
          
          if (yearData.offices) {
            Object.values(yearData.offices).forEach(office => {
              if (office.roles && office.roles.Consultant) {
                ['A', 'AC'].forEach(level => {
                  const levelData = office.roles.Consultant[level];
                  if (levelData && Array.isArray(levelData)) {
                    // Get December FTE (last month of year)
                    const decemberData = levelData[11];
                    if (decemberData) {
                      yearFTE += decemberData.fte;
                      yearRevenue += decemberData.price * decemberData.fte;
                    }
                  }
                });
              }
            });
          }
          
          totalFTE[year] = yearFTE;
          totalRevenue[year] = yearRevenue;
          
          console.log(`  ${year}: FTE=${yearFTE}, Revenue=${yearRevenue.toLocaleString('sv-SE')} SEK`);
        });
        
        // Calculate growth rates
        if (years.length >= 2) {
          const startYear = years[0];
          const endYear = years[years.length - 1];
          const fteGrowth = ((totalFTE[endYear] - totalFTE[startYear]) / totalFTE[startYear] * 100);
          const revenueGrowth = ((totalRevenue[endYear] - totalRevenue[startYear]) / totalRevenue[startYear] * 100);
          
          console.log(`\n🎯 Expected KPI Values:`);
          console.log(`  • FTE Growth: ${fteGrowth.toFixed(1)}%`);
          console.log(`  • Revenue Growth: ${revenueGrowth.toFixed(1)}%`);
          console.log(`  • Total FTE (${endYear}): ${totalFTE[endYear]}`);
          console.log(`  • Total Revenue (${endYear}): ${totalRevenue[endYear].toLocaleString('sv-SE')} SEK`);
        }
      }
      
      // Check what endpoint structure we're getting
      console.log('\n🔧 Full Response Structure:');
      console.log('Top-level keys:', Object.keys(simData));
      
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

// Run the KPI test
testKPIGeneration();