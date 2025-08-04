/**
 * Debug script to examine the actual data structure passed to KPI calculations
 */

const API_BASE = 'http://localhost:8000';

async function debugKPIData() {
  console.log('🔬 DEBUGGING KPI DATA STRUCTURE\n');

  // Simple 2-year scenario to examine data structure
  const scenario = {
    id: 'kpi-debug-test',
    name: 'KPI Debug Test',
    description: 'Examining KPI calculation data structure',
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
                    '202501': 10, '202502': 10, '202503': 10, '202504': 10,
                    '202505': 10, '202506': 10, '202507': 10, '202508': 10,
                    '202509': 10, '202510': 10, '202511': 10, '202512': 10,
                    '202601': 20, '202602': 20, '202603': 20, '202604': 20,
                    '202605': 20, '202606': 20, '202607': 20, '202608': 20,
                    '202609': 20, '202610': 20, '202611': 20, '202612': 20
                  }
                },
                churn: {
                  values: {
                    '202501': 2, '202502': 2, '202503': 2, '202504': 2,
                    '202505': 2, '202506': 2, '202507': 2, '202508': 2,
                    '202509': 2, '202510': 2, '202511': 2, '202512': 2,
                    '202601': 2, '202602': 2, '202603': 2, '202604': 2,
                    '202605': 2, '202606': 2, '202607': 2, '202608': 2,
                    '202609': 2, '202610': 2, '202611': 2, '202612': 2
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
                    '202501': 10, '202502': 10, '202503': 10, '202504': 10,
                    '202505': 10, '202506': 10, '202507': 10, '202508': 10,
                    '202509': 10, '202510': 10, '202511': 10, '202512': 10,
                    '202601': 20, '202602': 20, '202603': 20, '202604': 20,
                    '202605': 20, '202606': 20, '202607': 20, '202608': 20,
                    '202609': 20, '202610': 20, '202611': 20, '202612': 20
                  }
                },
                churn: {
                  values: {
                    '202501': 2, '202502': 2, '202503': 2, '202504': 2,
                    '202505': 2, '202506': 2, '202507': 2, '202508': 2,
                    '202509': 2, '202510': 2, '202511': 2, '202512': 2,
                    '202601': 2, '202602': 2, '202603': 2, '202604': 2,
                    '202605': 2, '202606': 2, '202607': 2, '202608': 2,
                    '202609': 2, '202610': 2, '202611': 2, '202612': 2
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

  console.log('📊 TESTING PATTERN:');
  console.log('  • 2025: Net +8 FTE/month (R=10, C=2)');
  console.log('  • 2026: Net +18 FTE/month (R=20, C=2)');
  console.log('  • Expected: Different FTE values in each year\n');

  try {
    console.log('🚀 Running debug scenario...');
    
    const request = { scenario_definition: scenario };
    const response = await fetch(`${API_BASE}/scenarios/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });

    if (response.ok) {
      const data = await response.json();
      console.log('✅ Simulation completed\n');
      
      if (data.results && data.results.years) {
        const years = Object.keys(data.results.years).sort();
        
        console.log('🔍 DETAILED DATA STRUCTURE ANALYSIS:');
        console.log('=====================================\n');
        
        years.forEach(year => {
          const yearData = data.results.years[year];
          console.log(`📅 ${year} DATA STRUCTURE:`);
          console.log(`   Top-level keys: [${Object.keys(yearData).join(', ')}]`);
          console.log(`   Total FTE: ${yearData.total_fte}`);
          
          if (yearData.offices && yearData.offices.Stockholm) {
            const stockholm = yearData.offices.Stockholm;
            console.log(`   Stockholm keys: [${Object.keys(stockholm).join(', ')}]`);
            console.log(`   Stockholm total_fte: ${stockholm.total_fte}`);
            
            if (stockholm.roles && stockholm.roles.Consultant && stockholm.roles.Consultant.A) {
              const consultantA = stockholm.roles.Consultant.A;
              console.log(`   Consultant A data type: ${Array.isArray(consultantA) ? 'Array' : typeof consultantA}`);
              console.log(`   Consultant A length: ${consultantA.length}`);
              
              if (Array.isArray(consultantA) && consultantA.length > 0) {
                console.log(`   Sample months:`);
                [0, 5, 11].forEach(monthIndex => {
                  if (consultantA[monthIndex]) {
                    const month = consultantA[monthIndex];
                    const monthName = ['Jan', 'Jun', 'Dec'][monthIndex === 0 ? 0 : monthIndex === 5 ? 1 : 2];
                    console.log(`      ${monthName}: FTE=${month.fte}, R=${month.recruitment}, C=${month.churn}, Price=${month.price}, Salary=${month.salary}`);
                  }
                });
              }
            }
          }
          
          // Show KPI data for comparison
          if (yearData.kpis && yearData.kpis.financial) {
            const fin = yearData.kpis.financial;
            console.log(`   KPI Financial:`);
            console.log(`      Net Sales: ${(fin.net_sales / 1000000).toFixed(1)}M SEK`);
            console.log(`      Total Consultants: ${fin.total_consultants}`);
            console.log(`      Avg Hourly Rate: ${fin.avg_hourly_rate} SEK`);
          }
          console.log('');
        });
        
        // Compare the December FTE values that KPIs likely use
        console.log('🎯 DECEMBER FTE COMPARISON (Data likely used by KPIs):');
        console.log('======================================================\n');
        
        years.forEach(year => {
          const yearData = data.results.years[year];
          const stockholmA = yearData.offices?.Stockholm?.roles?.Consultant?.A;
          
          if (stockholmA && stockholmA.length >= 12) {
            const decData = stockholmA[11]; // December (0-indexed)
            console.log(`${year} December:`);
            console.log(`   FTE: ${decData.fte}`);
            console.log(`   Price: ${decData.price} SEK/hour`);
            console.log(`   Salary: ${decData.salary} SEK/month`);
            console.log(`   UTR: ${decData.utr}`);
            console.log('');
          }
        });
        
      } else {
        console.log('❌ No yearly results found');
      }
    } else {
      console.log('❌ Simulation failed:', response.status);
      const errorText = await response.text();
      console.log('Error:', errorText);
    }

  } catch (error) {
    console.error('❌ Debug failed:', error.message);
  }
}

// Run the debug analysis
debugKPIData();