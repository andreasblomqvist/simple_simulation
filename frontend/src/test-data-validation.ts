// Data Validation Test for FTE Flow
// This file helps debug the FTE data flow from backend to frontend

interface TestOfficeData {
  name: string;
  fte?: number;
  total_fte?: number;
  baseline_total_fte?: number;
  current_total_fte?: number;
  financial?: any;
  growth?: any;
  kpis?: any;
  levels?: any;
}

interface TestSimulationResults {
  years: Record<string, {
    offices: Record<string, TestOfficeData>;
  }>;
  kpis?: any;
}

// Test 1: Validate Backend API Response Structure
export function validateBackendResponse(apiResponse: any): {
  isValid: boolean;
  issues: string[];
  fteValues: Record<string, number>;
} {
  const issues: string[] = [];
  const fteValues: Record<string, number> = {};

  try {
    // Check if response has the expected structure
    if (!apiResponse.years) {
      issues.push("Missing 'years' property in API response");
      return { isValid: false, issues, fteValues };
    }

    const years = Object.keys(apiResponse.years);
    if (years.length === 0) {
      issues.push("No years found in API response");
      return { isValid: false, issues, fteValues };
    }

    // Check each year's data
    years.forEach(year => {
      const yearData = apiResponse.years[year];
      if (!yearData.offices) {
        issues.push(`Missing 'offices' property in year ${year}`);
        return;
      }

      const offices = Object.keys(yearData.offices);
      if (offices.length === 0) {
        issues.push(`No offices found in year ${year}`);
        return;
      }

      // Check each office's FTE data
      offices.forEach(officeName => {
        const officeData = yearData.offices[officeName];
        const officeKey = `${officeName}_${year}`;

        // Check for FTE fields
        const fte = officeData.fte;
        const totalFte = officeData.total_fte;
        const baselineTotalFte = officeData.baseline_total_fte;
        const currentTotalFte = officeData.current_total_fte;

        // Log what we found
        console.log(`Office ${officeName} (${year}):`, {
          fte,
          total_fte: totalFte,
          baseline_total_fte: baselineTotalFte,
          current_total_fte: currentTotalFte
        });

        // Store the first non-zero FTE value we find
        if (fte !== undefined && fte !== null) {
          fteValues[officeKey] = fte;
        } else if (totalFte !== undefined && totalFte !== null) {
          fteValues[officeKey] = totalFte;
        } else if (currentTotalFte !== undefined && currentTotalFte !== null) {
          fteValues[officeKey] = currentTotalFte;
        } else if (baselineTotalFte !== undefined && baselineTotalFte !== null) {
          fteValues[officeKey] = baselineTotalFte;
        } else {
          issues.push(`No FTE data found for ${officeName} in ${year}`);
        }

        // Check if FTE values are reasonable (not zero for all offices)
        if (fte === 0 && totalFte === 0 && currentTotalFte === 0 && baselineTotalFte === 0) {
          issues.push(`All FTE values are zero for ${officeName} in ${year}`);
        }
      });
    });

  } catch (error) {
    issues.push(`Error parsing API response: ${error}`);
  }

  return {
    isValid: issues.length === 0,
    issues,
    fteValues
  };
}

// Test 2: Validate Frontend Data Processing
export function validateFrontendProcessing(
  apiResponse: any,
  processedData: any
): {
  isValid: boolean;
  issues: string[];
  comparison: Record<string, { api: number; frontend: number; match: boolean }>;
} {
  const issues: string[] = [];
  const comparison: Record<string, { api: number; frontend: number; match: boolean }> = {};

  try {
    // Extract FTE values from API response
    const apiFteValues: Record<string, number> = {};
    const years = Object.keys(apiResponse.years || {});
    
    years.forEach(year => {
      const yearData = apiResponse.years[year];
      const offices = Object.keys(yearData.offices || {});
      
      offices.forEach(officeName => {
        const officeData = yearData.offices[officeName];
        const key = `${officeName}_${year}`;
        
        // Get FTE from API response (prioritize fte, then total_fte, then current_total_fte)
        const apiFte = officeData.fte ?? officeData.total_fte ?? officeData.current_total_fte ?? 0;
        apiFteValues[key] = apiFte;
      });
    });

    // Extract FTE values from processed frontend data
    const frontendFteValues: Record<string, number> = {};
    
    if (processedData && Array.isArray(processedData)) {
      processedData.forEach((row: any) => {
        if (row.office && row.total) {
          // Extract office name and year from the processed data
          const officeMatch = row.office.match(/(.+) Office/);
          if (officeMatch) {
            const officeName = officeMatch[1];
            // Try to extract year from the data structure
            const year = Object.keys(apiResponse.years || {})[0] || 'unknown';
            const key = `${officeName}_${year}`;
            
            // Extract numeric value from the formatted string
            const totalStr = String(row.total);
            const numericMatch = totalStr.match(/(\d+(?:\.\d+)?)/);
            if (numericMatch) {
              frontendFteValues[key] = parseFloat(numericMatch[1]);
            }
          }
        }
      });
    }

    // Compare API vs Frontend values
    Object.keys(apiFteValues).forEach(key => {
      const apiValue = apiFteValues[key];
      const frontendValue = frontendFteValues[key] || 0;
      const match = Math.abs(apiValue - frontendValue) < 0.1; // Allow small rounding differences
      
      comparison[key] = {
        api: apiValue,
        frontend: frontendValue,
        match
      };

      if (!match) {
        issues.push(`FTE mismatch for ${key}: API=${apiValue}, Frontend=${frontendValue}`);
      }
    });

  } catch (error) {
    issues.push(`Error in frontend processing validation: ${error}`);
  }

  return {
    isValid: issues.length === 0,
    issues,
    comparison
  };
}

// Test 3: Simulate the exact data flow
export function simulateDataFlow(apiResponse: any): {
  step1_backendResponse: any;
  step2_frontendExtraction: any;
  step3_tableDisplay: any;
  issues: string[];
} {
  const issues: string[] = [];
  
  try {
    // Step 1: Backend Response (what we receive from API)
    const step1_backendResponse = apiResponse;
    
    // Step 2: Frontend Extraction (how ResultsTable.tsx processes it)
    const step2_frontendExtraction: Record<string, number> = {};
    const years = Object.keys(apiResponse.years || {});
    
    years.forEach(year => {
      const yearData = apiResponse.years[year];
      const offices = Object.keys(yearData.offices || {});
      
      offices.forEach(officeName => {
        const officeData = yearData.offices[officeName];
        const key = `${officeName}_${year}`;
        
        // This is exactly what ResultsTable.tsx does in getKPIValue function
        const fteValue = officeData.fte || officeData.total_fte || 0;
        step2_frontendExtraction[key] = fteValue;
        
        if (fteValue === 0) {
          issues.push(`Zero FTE extracted for ${key} - available fields: ${Object.keys(officeData).join(', ')}`);
        }
      });
    });
    
    // Step 3: Table Display (what gets shown in the UI)
    const step3_tableDisplay: Record<string, string> = {};
    Object.keys(step2_frontendExtraction).forEach(key => {
      const value = step2_frontendExtraction[key];
      // Format like the frontend does
      step3_tableDisplay[key] = value >= 1_000_000 
        ? `${(value / 1_000_000).toFixed(2).replace(/\.00$/, '')}M`
        : value.toLocaleString();
    });

  } catch (error) {
    issues.push(`Error in data flow simulation: ${error}`);
  }

  return {
    step1_backendResponse: apiResponse,
    step2_frontendExtraction: {},
    step3_tableDisplay: {},
    issues
  };
}

// Test 4: Run all validations
export function runAllValidations(apiResponse: any, processedData?: any): {
  backendValidation: ReturnType<typeof validateBackendResponse>;
  frontendValidation?: ReturnType<typeof validateFrontendProcessing>;
  dataFlowSimulation: ReturnType<typeof simulateDataFlow>;
  summary: {
    totalIssues: number;
    criticalIssues: string[];
    recommendations: string[];
  };
} {
  console.log("=== FTE Data Flow Validation ===");
  
  const backendValidation = validateBackendResponse(apiResponse);
  const frontendValidation = processedData ? validateFrontendProcessing(apiResponse, processedData) : undefined;
  const dataFlowSimulation = simulateDataFlow(apiResponse);
  
  // Collect all issues
  const allIssues = [
    ...backendValidation.issues,
    ...(frontendValidation?.issues || []),
    ...dataFlowSimulation.issues
  ];
  
  const criticalIssues = allIssues.filter(issue => 
    issue.includes("Missing") || 
    issue.includes("No FTE data") || 
    issue.includes("Zero FTE")
  );
  
  const recommendations: string[] = [];
  
  if (backendValidation.issues.length > 0) {
    recommendations.push("Fix backend API response structure");
  }
  
  if (frontendValidation?.issues.length) {
    recommendations.push("Check frontend data processing logic");
  }
  
  if (dataFlowSimulation.issues.length > 0) {
    recommendations.push("Verify data transformation between backend and frontend");
  }
  
  if (criticalIssues.length === 0) {
    recommendations.push("Data flow appears correct - check UI rendering");
  }

  const summary = {
    totalIssues: allIssues.length,
    criticalIssues,
    recommendations
  };

  console.log("Validation Summary:", summary);
  console.log("Backend FTE Values:", backendValidation.fteValues);
  
  return {
    backendValidation,
    frontendValidation,
    dataFlowSimulation,
    summary
  };
}

// Utility function to log API response structure
export function logApiResponseStructure(apiResponse: any): void {
  console.log("=== API Response Structure Analysis ===");
  
  if (!apiResponse) {
    console.log("❌ No API response provided");
    return;
  }
  
  console.log("✅ API response received");
  console.log("Response keys:", Object.keys(apiResponse));
  
  if (apiResponse.years) {
    const years = Object.keys(apiResponse.years);
    console.log(`✅ Found ${years.length} years:`, years);
    
    years.forEach(year => {
      const yearData = apiResponse.years[year];
      if (yearData.offices) {
        const offices = Object.keys(yearData.offices);
        console.log(`  Year ${year}: ${offices.length} offices:`, offices);
        
        // Sample first office structure
        if (offices.length > 0) {
          const firstOffice = yearData.offices[offices[0]];
          console.log(`  Sample office (${offices[0]}) keys:`, Object.keys(firstOffice));
          console.log(`  Sample office FTE fields:`, {
            fte: firstOffice.fte,
            total_fte: firstOffice.total_fte,
            baseline_total_fte: firstOffice.baseline_total_fte,
            current_total_fte: firstOffice.current_total_fte
          });
        }
      } else {
        console.log(`  ❌ Year ${year}: No offices found`);
      }
    });
  } else {
    console.log("❌ No 'years' property found in API response");
  }
} 