/**
 * Comprehensive analysis of simulation engine results and KPI calculations
 * Tests FTE progression and KPI accuracy across multiple years
 */

const API_BASE = 'http://localhost:8000';

async function analyzeEngineResults() {
  console.log('🔬 COMPREHENSIVE ENGINE ANALYSIS\n');

  // Create a 3-year scenario with clear growth patterns
  const scenario = {
    id: 'engine-analysis-test',
    name: 'Engine Analysis Test',
    description: 'Comprehensive test of engine results and KPI calculations',
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
                    // 2025: Conservative growth
                    '202501': 10, '202502': 10, '202503': 10, '202504': 10,
                    '202505': 10, '202506': 10, '202507': 10, '202508': 10,
                    '202509': 10, '202510': 10, '202511': 10, '202512': 10,
                    // 2026: Moderate growth
                    '202601': 15, '202602': 15, '202603': 15, '202604': 15,
                    '202605': 15, '202606': 15, '202607': 15, '202608': 15,
                    '202609': 15, '202610': 15, '202611': 15, '202612': 15,
                    // 2027: Aggressive growth
                    '202701': 25, '202702': 25, '202703': 25, '202704': 25,
                    '202705': 25, '202706': 25, '202707': 25, '202708': 25,
                    '202709': 25, '202710': 25, '202711': 25, '202712': 25
                  }
                },
                churn: {
                  values: {
                    // Consistent low churn across all years
                    '202501': 2, '202502': 2, '202503': 2, '202504': 2,
                    '202505': 2, '202506': 2, '202507': 2, '202508': 2,
                    '202509': 2, '202510': 2, '202511': 2, '202512': 2,
                    '202601': 2, '202602': 2, '202603': 2, '202604': 2,
                    '202605': 2, '202606': 2, '202607': 2, '202608': 2,
                    '202609': 2, '202610': 2, '202611': 2, '202612': 2,
                    '202701': 2, '202702': 2, '202703': 2, '202704': 2,
                    '202705': 2, '202706': 2, '202707': 2, '202708': 2,
                    '202709': 2, '202710': 2, '202711': 2, '202712': 2
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
                    // Same as above - duplicated for churn section
                    '202501': 10, '202502': 10, '202503': 10, '202504': 10,
                    '202505': 10, '202506': 10, '202507': 10, '202508': 10,
                    '202509': 10, '202510': 10, '202511': 10, '202512': 10,
                    '202601': 15, '202602': 15, '202603': 15, '202604': 15,
                    '202605': 15, '202606': 15, '202607': 15, '202608': 15,
                    '202609': 15, '202610': 15, '202611': 15, '202612': 15,
                    '202701': 25, '202702': 25, '202703': 25, '202704': 25,
                    '202705': 25, '202706': 25, '202707': 25, '202708': 25,
                    '202709': 25, '202710': 25, '202711': 25, '202712': 25
                  }
                },
                churn: {
                  values: {
                    '202501': 2, '202502': 2, '202503': 2, '202504': 2,
                    '202505': 2, '202506': 2, '202507': 2, '202508': 2,
                    '202509': 2, '202510': 2, '202511': 2, '202512': 2,
                    '202601': 2, '202602': 2, '202603': 2, '202604': 2,
                    '202605': 2, '202606': 2, '202607': 2, '202608': 2,
                    '202609': 2, '202610': 2, '202611': 2, '202612': 2,
                    '202701': 2, '202702': 2, '202703': 2, '202704': 2,
                    '202705': 2, '202706': 2, '202707': 2, '202708': 2,
                    '202709': 2, '202710': 2, '202711': 2, '202712': 2
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
  console.log('  • 2026: Net +13 FTE/month (R=15, C=2)');
  console.log('  • 2027: Net +23 FTE/month (R=25, C=2)');
  console.log('  • Expected: Clear year-over-year FTE and revenue growth\n');

  try {
    console.log('🚀 Running comprehensive analysis...');
    
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
        
        console.log('📈 YEAR-BY-YEAR ANALYSIS:');
        console.log('===============================\n');
        
        let yearlyData = {};
        
        // Collect data for each year
        years.forEach(year => {
          const yearData = data.results.years[year];
          const stockholmOffice = yearData.offices?.Stockholm;
          
          if (stockholmOffice && stockholmOffice.roles && stockholmOffice.roles.Consultant) {
            const consultantA = stockholmOffice.roles.Consultant.A;
            
            if (consultantA && consultantA.length > 0) {
              // Get January and December data
              const janData = consultantA[0];   // January
              const decData = consultantA[11];  // December
              
              yearlyData[year] = {
                jan_fte: janData.fte,
                dec_fte: decData.fte,
                yearly_growth: decData.fte - janData.fte,
                jan_recruitment: janData.recruitment,
                jan_churn: janData.churn,
                jan_net: janData.recruitment - janData.churn,
                kpis: yearData.kpis || {}
              };
            }
          }
        });
        
        // Display yearly analysis
        years.forEach(year => {
          const data = yearlyData[year];
          if (data) {
            console.log(`📅 ${year} RESULTS:`);
            console.log(`   🔢 FTE Progression: ${data.jan_fte} → ${data.dec_fte} (+${data.yearly_growth})`);
            console.log(`   📊 Monthly Pattern: R=${data.jan_recruitment}, C=${data.jan_churn}, Net=+${data.jan_net}`);
            
            if (data.kpis.financial) {
              const fin = data.kpis.financial;
              console.log(`   💰 Financial KPIs:`);
              console.log(`      • Net Sales: ${(fin.net_sales / 1000000).toFixed(1)}M SEK`);
              console.log(`      • EBITDA: ${(fin.ebitda / 1000000).toFixed(1)}M SEK`);
              console.log(`      • Margin: ${(fin.margin * 100).toFixed(1)}%`);
              console.log(`      • Total Consultants: ${fin.total_consultants}`);
            }
            
            if (data.kpis.growth) {
              const growth = data.kpis.growth;
              console.log(`   📈 Growth KPIs:`);
              console.log(`      • FTE Growth: ${isNaN(growth.fte_growth) ? 'N/A' : (growth.fte_growth * 100).toFixed(1) + '%'}`);
              console.log(`      • Revenue Growth: ${isNaN(growth.revenue_growth) ? 'N/A' : (growth.revenue_growth * 100).toFixed(1) + '%'}`);
            }
            console.log('');
          }
        });
        
        // Cross-year comparison
        console.log('🔍 CROSS-YEAR COMPARISON:');
        console.log('==========================\n');
        
        if (years.length >= 2) {
          for (let i = 1; i < years.length; i++) {
            const currentYear = years[i];
            const previousYear = years[i-1];
            
            const current = yearlyData[currentYear];
            const previous = yearlyData[previousYear];
            
            if (current && previous) {
              const fteDiff = current.dec_fte - previous.dec_fte;
              const fteGrowthRate = ((current.dec_fte - previous.dec_fte) / previous.dec_fte * 100);
              
              console.log(`📊 ${previousYear} → ${currentYear}:`);
              console.log(`   🔢 FTE Change: ${previous.dec_fte} → ${current.dec_fte} (+${fteDiff}, +${fteGrowthRate.toFixed(1)}%)`);
              
              if (current.kpis.financial && previous.kpis.financial) {
                const currentRevenue = current.kpis.financial.net_sales;
                const previousRevenue = previous.kpis.financial.net_sales;
                const revenueDiff = currentRevenue - previousRevenue;
                const revenueGrowthRate = (revenueDiff / previousRevenue * 100);
                
                console.log(`   💰 Revenue Change: ${(previousRevenue/1000000).toFixed(1)}M → ${(currentRevenue/1000000).toFixed(1)}M (+${(revenueDiff/1000000).toFixed(1)}M, +${revenueGrowthRate.toFixed(1)}%)`);
              }
              console.log('');
            }
          }
          
          // Overall assessment
          console.log('🎯 OVERALL ASSESSMENT:');
          console.log('=======================\n');
          
          const firstYear = yearlyData[years[0]];
          const lastYear = yearlyData[years[years.length - 1]];
          
          if (firstYear && lastYear) {
            const totalFTEGrowth = lastYear.dec_fte - firstYear.jan_fte;
            const totalGrowthRate = (totalFTEGrowth / firstYear.jan_fte * 100);
            
            console.log(`📈 Total FTE Growth: ${firstYear.jan_fte} → ${lastYear.dec_fte} (+${totalFTEGrowth}, +${totalGrowthRate.toFixed(1)}%)`);
            
            if (firstYear.kpis.financial && lastYear.kpis.financial) {
              const firstRevenue = firstYear.kpis.financial.net_sales;
              const lastRevenue = lastYear.kpis.financial.net_sales;
              const totalRevenueDiff = lastRevenue - firstRevenue;
              const totalRevenueGrowthRate = (totalRevenueDiff / firstRevenue * 100);
              
              console.log(`💰 Total Revenue Growth: ${(firstRevenue/1000000).toFixed(1)}M → ${(lastRevenue/1000000).toFixed(1)}M (+${(totalRevenueDiff/1000000).toFixed(1)}M, +${totalRevenueGrowthRate.toFixed(1)}%)`);
            }
            
            // Validate expected patterns
            console.log('\n✅ VALIDATION CHECKS:');
            
            // Check FTE growth
            if (totalFTEGrowth > 100) {
              console.log('   ✅ FTE Growth: PASS - Significant growth detected');
            } else {
              console.log('   ❌ FTE Growth: FAIL - Insufficient growth');
            }
            
            // Check year-over-year progression
            let yearOverYearValid = true;
            for (let i = 1; i < years.length; i++) {
              const current = yearlyData[years[i]];
              const previous = yearlyData[years[i-1]];
              if (current.dec_fte <= previous.dec_fte) {
                yearOverYearValid = false;
                break;
              }
            }
            
            if (yearOverYearValid) {
              console.log('   ✅ Year-over-Year Growth: PASS - Each year shows growth');
            } else {
              console.log('   ❌ Year-over-Year Growth: FAIL - Some years show decline');
            }
            
            // Check KPI variation
            const revenueValues = years.map(year => yearlyData[year].kpis.financial?.net_sales).filter(Boolean);
            const uniqueRevenues = new Set(revenueValues);
            
            if (uniqueRevenues.size > 1) {
              console.log('   ✅ KPI Variation: PASS - Revenue values differ between years');
            } else {
              console.log('   ❌ KPI Variation: FAIL - Revenue values are identical across years');
              console.log(`      Revenue values found: ${Array.from(uniqueRevenues).map(r => (r/1000000).toFixed(1) + 'M').join(', ')}`);
            }
          }
        }
      } else {
        console.log('❌ No yearly results found in response');
        console.log('Response structure:', Object.keys(data));
      }
    } else {
      console.log('❌ Simulation failed:', response.status);
      const errorText = await response.text();
      console.log('Error:', errorText);
    }

  } catch (error) {
    console.error('❌ Analysis failed:', error.message);
  }
}

// Run the comprehensive analysis
analyzeEngineResults();