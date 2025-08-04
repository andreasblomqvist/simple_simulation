/**
 * Simulation Verification Tests
 * 
 * These tests verify that the simulation engine produces reasonable and varying results
 * when given different baseline inputs and lever multipliers.
 */

import { describe, it, expect, beforeAll } from 'vitest';
import { scenarioApi } from '../services/scenarioApi';
import type { ScenarioDefinition, ScenarioResponse } from '../types/unified-data-structures';

// Helper function to create a base scenario
const createBaseScenario = (
  name: string,
  baselineInput: any,
  levers: any
): ScenarioDefinition => ({
  id: `test-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
  name,
  description: `Test scenario: ${name}`,
  time_range: {
    start_year: 2025,
    start_month: 1,
    end_year: 2027,
    end_month: 12
  },
  office_scope: ['Group'],
  baseline_input: baselineInput,
  levers,
  economic_params: {},
  created_at: new Date().toISOString()
});

// Helper function to create baseline input data
const createBaselineInput = (recruitmentMultiplier = 1.0, churnMultiplier = 1.0) => ({
  global_data: {
    recruitment: {
      Consultant: {
        A: Object.fromEntries(
          Array.from({ length: 36 }, (_, i) => {
            const year = 2025 + Math.floor(i / 12);
            const month = (i % 12) + 1;
            const monthKey = `${year}${month.toString().padStart(2, '0')}`;
            return [monthKey, Math.round(20 * recruitmentMultiplier)];
          })
        ),
        AC: Object.fromEntries(
          Array.from({ length: 36 }, (_, i) => {
            const year = 2025 + Math.floor(i / 12);
            const month = (i % 12) + 1;
            const monthKey = `${year}${month.toString().padStart(2, '0')}`;
            return [monthKey, Math.round(8 * recruitmentMultiplier)];
          })
        ),
        C: Object.fromEntries(
          Array.from({ length: 36 }, (_, i) => {
            const year = 2025 + Math.floor(i / 12);
            const month = (i % 12) + 1;
            const monthKey = `${year}${month.toString().padStart(2, '0')}`;
            return [monthKey, Math.round(4 * recruitmentMultiplier)];
          })
        )
      },
      Sales: {},
      Recruitment: {}
    },
    churn: {
      Consultant: {
        A: Object.fromEntries(
          Array.from({ length: 36 }, (_, i) => {
            const year = 2025 + Math.floor(i / 12);
            const month = (i % 12) + 1;
            const monthKey = `${year}${month.toString().padStart(2, '0')}`;
            return [monthKey, Math.round(2 * churnMultiplier)];
          })
        ),
        AC: Object.fromEntries(
          Array.from({ length: 36 }, (_, i) => {
            const year = 2025 + Math.floor(i / 12);
            const month = (i % 12) + 1;
            const monthKey = `${year}${month.toString().padStart(2, '0')}`;
            return [monthKey, Math.round(4 * churnMultiplier)];
          })
        ),
        C: Object.fromEntries(
          Array.from({ length: 36 }, (_, i) => {
            const year = 2025 + Math.floor(i / 12);
            const month = (i % 12) + 1;
            const monthKey = `${year}${month.toString().padStart(2, '0')}`;
            return [monthKey, Math.round(7 * churnMultiplier)];
          })
        )
      },
      Sales: {},
      Recruitment: {}
    }
  }
});

// Helper function to create lever data
const createLevers = (recruitmentMult = 1.0, churnMult = 1.0, progressionMult = 1.0) => ({
  recruitment: {
    A: recruitmentMult,
    AC: recruitmentMult,
    C: recruitmentMult,
    SrC: recruitmentMult,
    AM: recruitmentMult,
    M: recruitmentMult,
    SrM: recruitmentMult,
    Pi: progressionMult,
    P: progressionMult
  },
  churn: {
    A: churnMult,
    AC: churnMult,
    C: churnMult,
    SrC: churnMult,
    AM: churnMult,
    M: churnMult,
    SrM: churnMult,
    Pi: churnMult,
    P: churnMult
  },
  progression: {
    A: progressionMult,
    AC: progressionMult,
    C: progressionMult,
    SrC: progressionMult,
    AM: progressionMult,
    M: progressionMult,
    SrM: progressionMult,
    Pi: progressionMult,
    P: progressionMult
  }
});

// Helper function to extract key metrics from simulation results
const extractMetrics = (response: ScenarioResponse) => {
  if (response.status !== 'success' || !response.results) {
    throw new Error(`Simulation failed: ${response.error_message || 'Unknown error'}`);
  }

  const results = response.results;
  const years = Object.keys(results).sort();
  
  // Extract FTE totals by year
  const fteByYear: Record<string, number> = {};
  
  years.forEach(year => {
    let totalFte = 0;
    const offices = results[year];
    
    Object.values(offices).forEach((office: any) => {
      if (office.roles) {
        Object.values(office.roles).forEach((role: any) => {
          if (Array.isArray(role)) {
            // Flat role structure - sum all months
            totalFte += role.reduce((sum: number, monthValue: number) => sum + (monthValue || 0), 0) / 12;
          } else if (typeof role === 'object' && role !== null) {
            // Leveled role structure
            Object.values(role).forEach((level: any) => {
              if (Array.isArray(level)) {
                totalFte += level.reduce((sum: number, monthValue: number) => sum + (monthValue || 0), 0) / 12;
              }
            });
          }
        });
      }
    });
    
    fteByYear[year] = Math.round(totalFte);
  });

  return {
    fteByYear,
    totalFte2025: fteByYear['2025'] || 0,
    totalFte2026: fteByYear['2026'] || 0,
    totalFte2027: fteByYear['2027'] || 0,
    growthRate2025to2026: fteByYear['2025'] > 0 ? ((fteByYear['2026'] - fteByYear['2025']) / fteByYear['2025'] * 100) : 0,
    growthRate2026to2027: fteByYear['2026'] > 0 ? ((fteByYear['2027'] - fteByYear['2026']) / fteByYear['2026'] * 100) : 0
  };
};

describe('Simulation Verification Tests', () => {
  let baselineScenario: ScenarioDefinition;
  let highRecruitmentScenario: ScenarioDefinition;
  let lowChurnScenario: ScenarioDefinition;
  let fastProgressionScenario: ScenarioDefinition;
  
  beforeAll(() => {
    // Scenario 1: Baseline (1.0 multipliers across the board)
    baselineScenario = createBaseScenario(
      'Baseline Test',
      createBaselineInput(1.0, 1.0),
      createLevers(1.0, 1.0, 1.0)
    );

    // Scenario 2: High recruitment
    highRecruitmentScenario = createBaseScenario(
      'High Recruitment Test',
      createBaselineInput(1.5, 1.0),
      createLevers(1.5, 1.0, 1.0)
    );

    // Scenario 3: Low churn
    lowChurnScenario = createBaseScenario(
      'Low Churn Test',
      createBaselineInput(1.0, 0.5),
      createLevers(1.0, 0.5, 1.0)
    );

    // Scenario 4: Fast progression
    fastProgressionScenario = createBaseScenario(
      'Fast Progression Test',
      createBaselineInput(1.0, 1.0),
      createLevers(1.0, 1.0, 1.5)
    );
  });

  it('should return successful responses for all test scenarios', async () => {
    const scenarios = [baselineScenario, highRecruitmentScenario, lowChurnScenario, fastProgressionScenario];
    
    for (const scenario of scenarios) {
      console.log(`Testing scenario: ${scenario.name}`);
      console.log(`Levers:`, scenario.levers);
      
      const response = await scenarioApi.runScenarioDefinition(scenario);
      
      expect(response.status).toBe('success');
      expect(response.results).toBeDefined();
      expect(response.error_message).toBeUndefined();
      
      console.log(`✓ ${scenario.name} completed successfully`);
    }
  }, 60000); // 60 second timeout for all scenarios

  it('should produce different FTE results for different scenarios', async () => {
    console.log('\n=== Running Comparative Analysis ===');
    
    // Run all scenarios
    const [baselineResponse, highRecruitmentResponse, lowChurnResponse, fastProgressionResponse] = await Promise.all([
      scenarioApi.runScenarioDefinition(baselineScenario),
      scenarioApi.runScenarioDefinition(highRecruitmentScenario),
      scenarioApi.runScenarioDefinition(lowChurnScenario),
      scenarioApi.runScenarioDefinition(fastProgressionScenario)
    ]);

    // Extract metrics
    const baselineMetrics = extractMetrics(baselineResponse);
    const highRecruitmentMetrics = extractMetrics(highRecruitmentResponse);
    const lowChurnMetrics = extractMetrics(lowChurnResponse);
    const fastProgressionMetrics = extractMetrics(fastProgressionResponse);

    console.log('\n=== Results Comparison ===');
    console.log(`Baseline FTE (2025/2026/2027): ${baselineMetrics.totalFte2025}/${baselineMetrics.totalFte2026}/${baselineMetrics.totalFte2027}`);
    console.log(`High Recruitment FTE (2025/2026/2027): ${highRecruitmentMetrics.totalFte2025}/${highRecruitmentMetrics.totalFte2026}/${highRecruitmentMetrics.totalFte2027}`);
    console.log(`Low Churn FTE (2025/2026/2027): ${lowChurnMetrics.totalFte2025}/${lowChurnMetrics.totalFte2026}/${lowChurnMetrics.totalFte2027}`);
    console.log(`Fast Progression FTE (2025/2026/2027): ${fastProgressionMetrics.totalFte2025}/${fastProgressionMetrics.totalFte2026}/${fastProgressionMetrics.totalFte2027}`);

    console.log('\n=== Growth Rates ===');
    console.log(`Baseline Growth (2025→2026): ${baselineMetrics.growthRate2025to2026.toFixed(1)}%`);
    console.log(`High Recruitment Growth (2025→2026): ${highRecruitmentMetrics.growthRate2025to2026.toFixed(1)}%`);
    console.log(`Low Churn Growth (2025→2026): ${lowChurnMetrics.growthRate2025to2026.toFixed(1)}%`);
    console.log(`Fast Progression Growth (2025→2026): ${fastProgressionMetrics.growthRate2025to2026.toFixed(1)}%`);

    // Test expectations
    
    // 1. All scenarios should have non-zero FTE
    expect(baselineMetrics.totalFte2025).toBeGreaterThan(0);
    expect(highRecruitmentMetrics.totalFte2025).toBeGreaterThan(0);
    expect(lowChurnMetrics.totalFte2025).toBeGreaterThan(0);
    expect(fastProgressionMetrics.totalFte2025).toBeGreaterThan(0);

    // 2. High recruitment should lead to higher FTE than baseline
    expect(highRecruitmentMetrics.totalFte2026).toBeGreaterThan(baselineMetrics.totalFte2026);
    expect(highRecruitmentMetrics.totalFte2027).toBeGreaterThan(baselineMetrics.totalFte2027);

    // 3. Low churn should lead to higher FTE than baseline (people stay longer)
    expect(lowChurnMetrics.totalFte2026).toBeGreaterThan(baselineMetrics.totalFte2026);
    expect(lowChurnMetrics.totalFte2027).toBeGreaterThan(baselineMetrics.totalFte2027);

    // 4. Results should show progression over time (not static values)
    const hasGrowth = (metrics: any) => {
      return metrics.totalFte2025 !== metrics.totalFte2026 || 
             metrics.totalFte2026 !== metrics.totalFte2027;
    };

    expect(hasGrowth(baselineMetrics)).toBe(true);
    expect(hasGrowth(highRecruitmentMetrics)).toBe(true);
    expect(hasGrowth(lowChurnMetrics)).toBe(true);

    // 5. Each scenario should produce different results (not identical)
    const allResults = [
      baselineMetrics.totalFte2027,
      highRecruitmentMetrics.totalFte2027,
      lowChurnMetrics.totalFte2027,
      fastProgressionMetrics.totalFte2027
    ];
    
    const uniqueResults = new Set(allResults);
    expect(uniqueResults.size).toBeGreaterThan(1); // Should have at least 2 different results

  }, 120000); // 2 minute timeout for comparative analysis

  it('should show reasonable response to lever changes', async () => {
    console.log('\n=== Testing Lever Sensitivity ===');
    
    // Test extreme scenarios
    const extremeHighRecruitment = createBaseScenario(
      'Extreme High Recruitment',
      createBaselineInput(3.0, 1.0),
      createLevers(3.0, 1.0, 1.0)
    );

    const extremeLowChurn = createBaseScenario(
      'Extreme Low Churn',
      createBaselineInput(1.0, 0.1),
      createLevers(1.0, 0.1, 1.0)
    );

    const [extremeHighResponse, extremeLowResponse] = await Promise.all([
      scenarioApi.runScenarioDefinition(extremeHighRecruitment),
      scenarioApi.runScenarioDefinition(extremeLowChurn)
    ]);

    const extremeHighMetrics = extractMetrics(extremeHighResponse);
    const extremeLowMetrics = extractMetrics(extremeLowResponse);
    const baselineMetrics = extractMetrics(await scenarioApi.runScenarioDefinition(baselineScenario));

    console.log(`Extreme High Recruitment FTE 2027: ${extremeHighMetrics.totalFte2027}`);
    console.log(`Extreme Low Churn FTE 2027: ${extremeLowMetrics.totalFte2027}`);
    console.log(`Baseline FTE 2027: ${baselineMetrics.totalFte2027}`);

    // Extreme changes should produce significantly different results
    expect(Math.abs(extremeHighMetrics.totalFte2027 - baselineMetrics.totalFte2027)).toBeGreaterThan(50);
    expect(Math.abs(extremeLowMetrics.totalFte2027 - baselineMetrics.totalFte2027)).toBeGreaterThan(50);

  }, 60000);

  it('should validate that lever multipliers are being applied correctly', async () => {
    console.log('\n=== Testing Lever Application ===');
    
    // Create two scenarios with known differences
    const doubleRecruitment = createBaseScenario(
      'Double Recruitment',
      createBaselineInput(2.0, 1.0),
      createLevers(2.0, 1.0, 1.0)
    );

    const halfChurn = createBaseScenario(
      'Half Churn',
      createBaselineInput(1.0, 0.5),
      createLevers(1.0, 0.5, 1.0)
    );

    const [doubleResponse, halfResponse, baselineResponse] = await Promise.all([
      scenarioApi.runScenarioDefinition(doubleRecruitment),
      scenarioApi.runScenarioDefinition(halfChurn),
      scenarioApi.runScenarioDefinition(baselineScenario)
    ]);

    const doubleMetrics = extractMetrics(doubleResponse);
    const halfMetrics = extractMetrics(halfResponse);
    const baselineMetrics = extractMetrics(baselineResponse);

    console.log('Lever Application Results:');
    console.log(`Double Recruitment vs Baseline: ${doubleMetrics.totalFte2027} vs ${baselineMetrics.totalFte2027}`);
    console.log(`Half Churn vs Baseline: ${halfMetrics.totalFte2027} vs ${baselineMetrics.totalFte2027}`);

    // Both modifications should result in higher FTE than baseline
    expect(doubleMetrics.totalFte2027).toBeGreaterThan(baselineMetrics.totalFte2027);
    expect(halfMetrics.totalFte2027).toBeGreaterThan(baselineMetrics.totalFte2027);

    // The effects should be substantial
    const doubleIncrease = ((doubleMetrics.totalFte2027 - baselineMetrics.totalFte2027) / baselineMetrics.totalFte2027) * 100;
    const halfIncrease = ((halfMetrics.totalFte2027 - baselineMetrics.totalFte2027) / baselineMetrics.totalFte2027) * 100;

    console.log(`Double recruitment increase: ${doubleIncrease.toFixed(1)}%`);
    console.log(`Half churn increase: ${halfIncrease.toFixed(1)}%`);

    expect(doubleIncrease).toBeGreaterThan(5); // At least 5% increase
    expect(halfIncrease).toBeGreaterThan(5); // At least 5% increase

  }, 60000);
});