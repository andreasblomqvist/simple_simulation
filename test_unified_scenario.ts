// Test script to verify unified scenario structure
import fetch from 'node-fetch';

const API_BASE = 'http://localhost:8000';

// Create a minimal test scenario with unified structure
const testScenario = {
  name: "Test Unified Scenario",
  description: "Testing unified data structure",
  time_range: {
    start_year: 2025,
    start_month: 1,
    end_year: 2025,
    end_month: 12
  },
  office_scope: ["Group"],
  levers: {
    recruitment: { A: 1.0, AC: 1.0, C: 1.0, SrC: 1.0, AM: 1.0, M: 1.0, SrM: 1.0, Pi: 1.0, P: 1.0 },
    churn: { A: 1.0, AC: 1.0, C: 1.0, SrC: 1.0, AM: 1.0, M: 1.0, SrM: 1.0, Pi: 1.0, P: 1.0 },
    progression: { A: 1.0, AC: 1.0, C: 1.0, SrC: 1.0, AM: 1.0, M: 1.0, SrM: 1.0, Pi: 1.0, P: 1.0 }
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
            A: { recruitment: { '202501': 20 }, churn: { '202501': 2 } },
            AC: { recruitment: { '202501': 8 }, churn: { '202501': 4 } },
            C: { recruitment: { '202501': 4 }, churn: { '202501': 7 } },
            SrC: { recruitment: { '202501': 1 }, churn: { '202501': 7 } },
            AM: { recruitment: { '202501': 1 }, churn: { '202501': 9 } },
            M: { recruitment: { '202501': 0 }, churn: { '202501': 1 } },
            SrM: { recruitment: { '202501': 0 }, churn: { '202501': 0 } },
            Pi: { recruitment: { '202501': 0 }, churn: { '202501': 0 } },
            P: { recruitment: { '202501': 0 }, churn: { '202501': 0 } }
          }
        }
      },
      churn: {
        Consultant: {
          levels: {
            A: { recruitment: { '202501': 20 }, churn: { '202501': 2 } },
            AC: { recruitment: { '202501': 8 }, churn: { '202501': 4 } },
            C: { recruitment: { '202501': 4 }, churn: { '202501': 7 } },
            SrC: { recruitment: { '202501': 1 }, churn: { '202501': 7 } },
            AM: { recruitment: { '202501': 1 }, churn: { '202501': 9 } },
            M: { recruitment: { '202501': 0 }, churn: { '202501': 1 } },
            SrM: { recruitment: { '202501': 0 }, churn: { '202501': 0 } },
            Pi: { recruitment: { '202501': 0 }, churn: { '202501': 0 } },
            P: { recruitment: { '202501': 0 }, churn: { '202501': 0 } }
          }
        }
      }
    }
  },
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString()
};

async function testUnifiedScenario() {
  try {
    console.log('Testing unified scenario structure...');
    
    // Test 1: Create scenario
    console.log('\n1. Creating scenario...');
    const createResponse = await fetch(`${API_BASE}/scenarios/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(testScenario)
    });
    
    if (!createResponse.ok) {
      const errorText = await createResponse.text();
      console.error('Create failed:', createResponse.status, errorText);
      return;
    }
    
    const createResult = await createResponse.json();
    console.log('✅ Scenario created successfully:', createResult);
    
    const scenarioId = createResult.scenario_id;
    
    // Test 2: Get scenario
    console.log('\n2. Getting scenario...');
    const getResponse = await fetch(`${API_BASE}/scenarios/${scenarioId}`);
    
    if (!getResponse.ok) {
      const errorText = await getResponse.text();
      console.error('Get failed:', getResponse.status, errorText);
      return;
    }
    
    const getResult = await getResponse.json();
    console.log('✅ Scenario retrieved successfully');
    console.log('Name:', getResult.name);
    console.log('Time range:', getResult.time_range);
    console.log('Office scope:', getResult.office_scope);
    
    // Test 3: Run simulation
    console.log('\n3. Running simulation...');
    const runResponse = await fetch(`${API_BASE}/scenarios/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        scenario_id: scenarioId,
        office_scope: ["Group"]
      })
    });
    
    if (!runResponse.ok) {
      const errorText = await runResponse.text();
      console.error('Run failed:', runResponse.status, errorText);
      return;
    }
    
    const runResult = await runResponse.json();
    console.log('✅ Simulation completed successfully');
    console.log('Status:', runResult.status);
    console.log('Execution time:', runResult.execution_time);
    console.log('Has results:', !!runResult.results);
    
    if (runResult.results && runResult.results.years) {
      const years = Object.keys(runResult.results.years);
      console.log('Years in results:', years);
      
      if (years.length > 0) {
        const firstYear = years[0];
        const yearData = runResult.results.years[firstYear];
        const offices = Object.keys(yearData.offices || {});
        console.log('Offices in results:', offices);
      }
    }
    
    // Test 4: List scenarios
    console.log('\n4. Listing scenarios...');
    const listResponse = await fetch(`${API_BASE}/scenarios/list`);
    
    if (!listResponse.ok) {
      const errorText = await listResponse.text();
      console.error('List failed:', listResponse.status, errorText);
      return;
    }
    
    const listResult = await listResponse.json();
    console.log('✅ Scenarios listed successfully');
    console.log('Total scenarios:', listResult.total_count);
    console.log('Scenario names:', listResult.scenarios.map((s: any) => s.name));
    
    // Test 5: Delete scenario
    console.log('\n5. Deleting scenario...');
    const deleteResponse = await fetch(`${API_BASE}/scenarios/${scenarioId}`, {
      method: 'DELETE'
    });
    
    if (!deleteResponse.ok) {
      const errorText = await deleteResponse.text();
      console.error('Delete failed:', deleteResponse.status, errorText);
      return;
    }
    
    console.log('✅ Scenario deleted successfully');
    
    console.log('\n🎉 All tests passed! Unified scenario structure is working correctly.');
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  }
}

testUnifiedScenario(); 