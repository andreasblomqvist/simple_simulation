/**
 * Create a comprehensive test scenario with full baseline data and progression configuration
 */

import fetch from 'node-fetch';

const API_BASE = 'http://localhost:8000';

// Create comprehensive baseline data
function createTestBaselineData() {
  return {
    global: {
      recruitment: {
        Consultant: {
          levels: {
            A: {
              recruitment: {
                values: {
                  "202501": 5, "202502": 4, "202503": 6, "202504": 5,
                  "202505": 4, "202506": 3, "202507": 5, "202508": 4,
                  "202509": 6, "202510": 5, "202511": 4, "202512": 3
                }
              },
              churn: {
                values: {
                  "202501": 1, "202502": 2, "202503": 1, "202504": 1,
                  "202505": 2, "202506": 1, "202507": 1, "202508": 2,
                  "202509": 1, "202510": 1, "202511": 2, "202512": 1
                }
              }
            },
            AC: {
              recruitment: {
                values: {
                  "202501": 3, "202502": 2, "202503": 4, "202504": 3,
                  "202505": 2, "202506": 2, "202507": 3, "202508": 2,
                  "202509": 4, "202510": 3, "202511": 2, "202512": 2
                }
              },
              churn: {
                values: {
                  "202501": 1, "202502": 1, "202503": 0, "202504": 1,
                  "202505": 1, "202506": 0, "202507": 1, "202508": 1,
                  "202509": 0, "202510": 1, "202511": 1, "202512": 0
                }
              }
            },
            C: {
              recruitment: {
                values: {
                  "202501": 2, "202502": 1, "202503": 2, "202504": 2,
                  "202505": 1, "202506": 1, "202507": 2, "202508": 1,
                  "202509": 2, "202510": 2, "202511": 1, "202512": 1
                }
              },
              churn: {
                values: {
                  "202501": 0, "202502": 1, "202503": 0, "202504": 0,
                  "202505": 1, "202506": 0, "202507": 0, "202508": 1,
                  "202509": 0, "202510": 0, "202511": 1, "202512": 0
                }
              }
            },
            SrC: {
              recruitment: {
                values: {
                  "202501": 1, "202502": 0, "202503": 1, "202504": 1,
                  "202505": 0, "202506": 1, "202507": 1, "202508": 0,
                  "202509": 1, "202510": 1, "202511": 0, "202512": 1
                }
              },
              churn: {
                values: {
                  "202501": 0, "202502": 0, "202503": 0, "202504": 0,
                  "202505": 0, "202506": 0, "202507": 0, "202508": 0,
                  "202509": 0, "202510": 0, "202511": 0, "202512": 0
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
                  "202501": 2, "202502": 1, "202503": 2, "202504": 2,
                  "202505": 1, "202506": 1, "202507": 2, "202508": 1,
                  "202509": 2, "202510": 2, "202511": 1, "202512": 1
                }
              },
              churn: {
                values: {
                  "202501": 0, "202502": 1, "202503": 0, "202504": 0,
                  "202505": 1, "202506": 0, "202507": 0, "202508": 1,
                  "202509": 0, "202510": 0, "202511": 1, "202512": 0
                }
              }
            },
            AC: {
              recruitment: {
                values: {
                  "202501": 1, "202502": 1, "202503": 1, "202504": 1,
                  "202505": 1, "202506": 0, "202507": 1, "202508": 1,
                  "202509": 1, "202510": 1, "202511": 1, "202512": 0
                }
              },
              churn: {
                values: {
                  "202501": 0, "202502": 0, "202503": 0, "202504": 0,
                  "202505": 0, "202506": 0, "202507": 0, "202508": 0,
                  "202509": 0, "202510": 0, "202511": 0, "202512": 0
                }
              }
            }
          }
        },
        Operations: {
          recruitment: {
            values: {
              "202501": 1, "202502": 0, "202503": 1, "202504": 1,
              "202505": 0, "202506": 0, "202507": 1, "202508": 0,
              "202509": 1, "202510": 1, "202511": 0, "202512": 0
            }
          },
          churn: {
            values: {
              "202501": 0, "202502": 0, "202503": 0, "202504": 0,
              "202505": 0, "202506": 0, "202507": 0, "202508": 0,
              "202509": 0, "202510": 0, "202511": 0, "202512": 0
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
                  "202501": 5, "202502": 4, "202503": 6, "202504": 5,
                  "202505": 4, "202506": 3, "202507": 5, "202508": 4,
                  "202509": 6, "202510": 5, "202511": 4, "202512": 3
                }
              },
              churn: {
                values: {
                  "202501": 1, "202502": 2, "202503": 1, "202504": 1,
                  "202505": 2, "202506": 1, "202507": 1, "202508": 2,
                  "202509": 1, "202510": 1, "202511": 2, "202512": 1
                }
              }
            },
            AC: {
              recruitment: {
                values: {
                  "202501": 3, "202502": 2, "202503": 4, "202504": 3,
                  "202505": 2, "202506": 2, "202507": 3, "202508": 2,
                  "202509": 4, "202510": 3, "202511": 2, "202512": 2
                }
              },
              churn: {
                values: {
                  "202501": 1, "202502": 1, "202503": 0, "202504": 1,
                  "202505": 1, "202506": 0, "202507": 1, "202508": 1,
                  "202509": 0, "202510": 1, "202511": 1, "202512": 0
                }
              }
            },
            C: {
              recruitment: {
                values: {
                  "202501": 2, "202502": 1, "202503": 2, "202504": 2,
                  "202505": 1, "202506": 1, "202507": 2, "202508": 1,
                  "202509": 2, "202510": 2, "202511": 1, "202512": 1
                }
              },
              churn: {
                values: {
                  "202501": 0, "202502": 1, "202503": 0, "202504": 0,
                  "202505": 1, "202506": 0, "202507": 0, "202508": 1,
                  "202509": 0, "202510": 0, "202511": 1, "202512": 0
                }
              }
            },
            SrC: {
              recruitment: {
                values: {
                  "202501": 1, "202502": 0, "202503": 1, "202504": 1,
                  "202505": 0, "202506": 1, "202507": 1, "202508": 0,
                  "202509": 1, "202510": 1, "202511": 0, "202512": 1
                }
              },
              churn: {
                values: {
                  "202501": 0, "202502": 0, "202503": 0, "202504": 0,
                  "202505": 0, "202506": 0, "202507": 0, "202508": 0,
                  "202509": 0, "202510": 0, "202511": 0, "202512": 0
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
                  "202501": 2, "202502": 1, "202503": 2, "202504": 2,
                  "202505": 1, "202506": 1, "202507": 2, "202508": 1,
                  "202509": 2, "202510": 2, "202511": 1, "202512": 1
                }
              },
              churn: {
                values: {
                  "202501": 0, "202502": 1, "202503": 0, "202504": 0,
                  "202505": 1, "202506": 0, "202507": 0, "202508": 1,
                  "202509": 0, "202510": 0, "202511": 1, "202512": 0
                }
              }
            },
            AC: {
              recruitment: {
                values: {
                  "202501": 1, "202502": 1, "202503": 1, "202504": 1,
                  "202505": 1, "202506": 0, "202507": 1, "202508": 1,
                  "202509": 1, "202510": 1, "202511": 1, "202512": 0
                }
              },
              churn: {
                values: {
                  "202501": 0, "202502": 0, "202503": 0, "202504": 0,
                  "202505": 0, "202506": 0, "202507": 0, "202508": 0,
                  "202509": 0, "202510": 0, "202511": 0, "202512": 0
                }
              }
            }
          }
        },
        Operations: {
          recruitment: {
            values: {
              "202501": 1, "202502": 0, "202503": 1, "202504": 1,
              "202505": 0, "202506": 0, "202507": 1, "202508": 0,
              "202509": 1, "202510": 1, "202511": 0, "202512": 0
            }
          },
          churn: {
            values: {
              "202501": 0, "202502": 0, "202503": 0, "202504": 0,
              "202505": 0, "202506": 0, "202507": 0, "202508": 0,
              "202509": 0, "202510": 0, "202511": 0, "202512": 0
            }
          }
        }
      }
    }
  };
}

// Create progression configuration
function createProgressionConfig() {
  return {
    'A': {
      progression_months: [1, 4, 7, 10],
      start_tenure: 0,
      time_on_level: 6,
      next_level: 'AC',
      journey: 'J-1'
    },
    'AC': {
      progression_months: [1, 4, 7, 10],
      start_tenure: 6,
      time_on_level: 9,
      next_level: 'C',
      journey: 'J-1'
    },
    'C': {
      progression_months: [1, 7],
      start_tenure: 15,
      time_on_level: 12,
      next_level: 'SrC',
      journey: 'J-1'
    },
    'SrC': {
      progression_months: [1, 7],
      start_tenure: 27,
      time_on_level: 18,
      next_level: 'AM',
      journey: 'J-2'
    },
    'AM': {
      progression_months: [1, 7],
      start_tenure: 45,
      time_on_level: 30,
      next_level: 'M',
      journey: 'J-2'
    },
    'M': {
      progression_months: [1],
      start_tenure: 75,
      time_on_level: 24,
      next_level: 'SrM',
      journey: 'J-3'
    },
    'SrM': {
      progression_months: [1],
      start_tenure: 99,
      time_on_level: 120,
      next_level: 'Pi',
      journey: 'J-3'
    }
  };
}

// Create CAT curves
function createCATCurves() {
  return {
    'A': { 'CAT0': 0.0, 'CAT6': 0.919, 'CAT12': 0.85, 'CAT18': 0.0, 'CAT24': 0.0, 'CAT30': 0.0 },
    'AC': { 'CAT0': 0.0, 'CAT6': 0.054, 'CAT12': 0.759, 'CAT18': 0.400, 'CAT24': 0.0, 'CAT30': 0.0 },
    'C': { 'CAT0': 0.0, 'CAT6': 0.050, 'CAT12': 0.442, 'CAT18': 0.597, 'CAT24': 0.278, 'CAT30': 0.643, 'CAT36': 0.200, 'CAT42': 0.0 },
    'SrC': { 'CAT0': 0.0, 'CAT6': 0.206, 'CAT12': 0.438, 'CAT18': 0.317, 'CAT24': 0.211, 'CAT30': 0.206, 'CAT36': 0.167, 'CAT42': 0.0, 'CAT48': 0.0, 'CAT54': 0.0, 'CAT60': 0.0 },
    'AM': { 'CAT0': 0.0, 'CAT6': 0.0, 'CAT12': 0.0, 'CAT18': 0.189, 'CAT24': 0.197, 'CAT30': 0.234, 'CAT36': 0.048, 'CAT42': 0.0, 'CAT48': 0.0, 'CAT54': 0.0, 'CAT60': 0.0 },
    'M': { 'CAT0': 0.0, 'CAT6': 0.00, 'CAT12': 0.01, 'CAT18': 0.02, 'CAT24': 0.03, 'CAT30': 0.04, 'CAT36': 0.05, 'CAT42': 0.06, 'CAT48': 0.07, 'CAT54': 0.08, 'CAT60': 0.10 },
    'SrM': { 'CAT0': 0.0, 'CAT6': 0.00, 'CAT12': 0.005, 'CAT18': 0.01, 'CAT24': 0.015, 'CAT30': 0.02, 'CAT36': 0.025, 'CAT42': 0.03, 'CAT48': 0.04, 'CAT54': 0.05, 'CAT60': 0.06 }
  };
}

// Create test levers
function createTestLevers() {
  return {
    recruitment: {
      A: 1.2,
      AC: 1.1,
      C: 1.0,
      SrC: 0.9
    },
    churn: {
      A: 0.8,
      AC: 0.9,
      C: 1.0,
      SrC: 1.1
    },
    progression: {
      A: 1.1,
      AC: 1.0,
      C: 1.0,
      SrC: 0.9
    }
  };
}

// Create the complete test scenario
function createTestScenario() {
  return {
    name: "Comprehensive Test Scenario with Progression",
    description: "Full test scenario with complete baseline data, progression configuration, and CAT curves to verify all functionality works correctly",
    time_range: {
      start_year: 2025,
      start_month: 1,
      end_year: 2027,
      end_month: 12
    },
    office_scope: ["Group"],
    baseline_input: createTestBaselineData(),
    levers: createTestLevers(),
    progression_config: createProgressionConfig(),
    cat_curves: createCATCurves(),
    economic_params: {
      cost_of_living: 1.0,
      market_multiplier: 1.0,
      tax_rate: 0.25
    },
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };
}

// Main function to create and run the test scenario
async function main() {
  console.log('🧪 Creating comprehensive test scenario...');
  
  const scenario = createTestScenario();
  
  try {
    // Create the scenario
    console.log('📝 Creating scenario via API...');
    const createResponse = await fetch(`${API_BASE}/api/scenarios/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(scenario)
    });
    
    if (!createResponse.ok) {
      const errorText = await createResponse.text();
      throw new Error(`Failed to create scenario: ${createResponse.status} ${errorText}`);
    }
    
    const createResult = await createResponse.json();
    const scenarioId = createResult.scenario_id;
    
    console.log(`✅ Scenario created successfully with ID: ${scenarioId}`);
    
    // Run the simulation
    console.log('🚀 Running simulation...');
    const runResponse = await fetch(`${API_BASE}/api/scenarios/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(scenario)
    });
    
    if (!runResponse.ok) {
      const errorText = await runResponse.text();
      throw new Error(`Failed to run simulation: ${runResponse.status} ${errorText}`);
    }
    
    const simulationResult = await runResponse.json();
    
    console.log('✅ Simulation completed successfully!');
    console.log('📊 Simulation status:', simulationResult.status);
    
    if (simulationResult.results && simulationResult.results.years) {
      const years = Object.keys(simulationResult.results.years);
      console.log(`📈 Simulation data available for ${years.length} years:`, years.join(', '));
      
      // Check if progression data exists
      const firstYear = simulationResult.results.years[years[0]];
      if (firstYear && firstYear.Group && firstYear.Group.roles) {
        const consultant = firstYear.Group.roles.Consultant;
        if (consultant && consultant.levels) {
          const levelA = consultant.levels.A;
          if (levelA && levelA.months && levelA.months[0]) {
            const hasProgression = 'promoted_people' in levelA.months[0];
            console.log(`🎯 Progression data included: ${hasProgression ? 'YES' : 'NO'}`);
            
            if (hasProgression) {
              const promotedPeople = levelA.months[0].promoted_people || 0;
              console.log(`📊 Promoted people in first month: ${promotedPeople}`);
            }
          }
        }
      }
    }
    
    console.log('\n🎉 Test scenario creation and simulation complete!');
    console.log(`📋 Scenario ID: ${scenarioId}`);
    console.log('🔍 You can now view this scenario in the frontend to verify progression data is working.');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

// Run the script
main();