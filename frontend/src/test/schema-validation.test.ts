/**
 * Schema Validation Test
 * 
 * This test ensures that the frontend always produces the canonical
 * scenario structure that matches the backend Pydantic models exactly.
 */

import { ScenarioDefinition, BaselineInput, TimeRange, EconomicParameters, Levers } from '../types/unified-data-structures';

describe('Frontend Schema Validation', () => {
  test('should produce valid scenario structure that backend accepts', async () => {
    // Build a minimal but complete scenario using frontend types
    const scenario: ScenarioDefinition = {
      name: 'test_scenario',
      description: 'Test scenario for schema validation',
      time_range: {
        start_year: 2025,
        start_month: 1,
        end_year: 2027,
        end_month: 12
      },
      office_scope: ['Stockholm'],
      levers: {
        recruitment: { 'A': 1.0, 'C': 1.0 },
        churn: { 'A': 1.0, 'C': 1.0 },
        progression: { 'A': 1.0, 'C': 1.0 }
      },
      economic_params: {
        working_hours_per_month: 160.0,
        employment_cost_rate: 0.3,
        unplanned_absence: 0.05,
        other_expense: 1000000.0
      },
      baseline_input: {
        global: {
          recruitment: {
            Consultant: {
              levels: {
                A: {
                  recruitment: { values: { '202501': 5.0, '202502': 3.0 } },
                  churn: { values: { '202501': 1.0, '202502': 1.0 } }
                },
                C: {
                  recruitment: { values: { '202501': 2.0, '202502': 2.0 } },
                  churn: { values: { '202501': 0.5, '202502': 0.5 } }
                }
              }
            }
          },
          churn: {
            Consultant: {
              levels: {
                A: {
                  recruitment: { values: { '202501': 0.0, '202502': 0.0 } },
                  churn: { values: { '202501': 1.0, '202502': 1.0 } }
                },
                C: {
                  recruitment: { values: { '202501': 0.0, '202502': 0.0 } },
                  churn: { values: { '202501': 0.5, '202502': 0.5 } }
                }
              }
            }
          }
        }
      },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    // POST to backend validate endpoint
    const response = await fetch('/api/scenarios/validate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(scenario)
    });

    const result = await response.json();

    // The backend should accept this structure
    expect(response.status).toBe(200);
    expect(result.valid).toBe(true);
    expect(result.errors).toEqual([]);
  });

  test('should reject invalid scenario structure', async () => {
    // Build an invalid scenario (missing required fields)
    const invalidScenario = {
      name: 'invalid_scenario',
      // Missing required fields like time_range, office_scope, etc.
    };

    const response = await fetch('/api/scenarios/validate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(invalidScenario)
    });

    const result = await response.json();

    // The backend should reject this structure
    expect(response.status).toBe(200); // Validate endpoint returns 200 even for invalid data
    expect(result.valid).toBe(false);
    expect(result.errors.length).toBeGreaterThan(0);
  });

  test('should handle monthly values with proper YYYYMM format', async () => {
    const scenario: ScenarioDefinition = {
      name: 'monthly_format_test',
      description: 'Test monthly value format',
      time_range: {
        start_year: 2025,
        start_month: 1,
        end_year: 2025,
        end_month: 12
      },
      office_scope: ['Stockholm'],
      levers: {
        recruitment: { 'A': 1.0 },
        churn: { 'A': 1.0 },
        progression: { 'A': 1.0 }
      },
      economic_params: {
        working_hours_per_month: 160.0,
        employment_cost_rate: 0.3,
        unplanned_absence: 0.05,
        other_expense: 1000000.0
      },
      baseline_input: {
        global: {
          recruitment: {
            Consultant: {
              levels: {
                A: {
                  recruitment: { 
                    values: { 
                      '202501': 1.0, '202502': 2.0, '202503': 3.0,
                      '202504': 4.0, '202505': 5.0, '202506': 6.0,
                      '202507': 7.0, '202508': 8.0, '202509': 9.0,
                      '202510': 10.0, '202511': 11.0, '202512': 12.0
                    } 
                  },
                  churn: { 
                    values: { 
                      '202501': 0.1, '202502': 0.2, '202503': 0.3,
                      '202504': 0.4, '202505': 0.5, '202506': 0.6,
                      '202507': 0.7, '202508': 0.8, '202509': 0.9,
                      '202510': 1.0, '202511': 1.1, '202512': 1.2
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
                  recruitment: { values: { '202501': 0.0 } },
                  churn: { values: { '202501': 0.1 } }
                }
              }
            }
          }
        }
      },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    const response = await fetch('/api/scenarios/validate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(scenario)
    });

    const result = await response.json();

    expect(response.status).toBe(200);
    expect(result.valid).toBe(true);
    expect(result.errors).toEqual([]);
  });
}); 