// Utility to normalize baseline_input to level-first format
// Converts recruitment[role][month][level] to recruitment[role][level][month]

export function normalizeBaselineInput(baselineInput: any): any {
  if (!baselineInput) {
    // Return empty but valid structure
    return {
      global: {
        recruitment: {},
        churn: {}
      }
    };
  }

  // Handle case where baseline_input doesn't have global structure
  if (!baselineInput.global) {
    baselineInput = {
      global: baselineInput
    };
  }

  const { recruitment, churn } = baselineInput.global || {};
  
  // Handle null/undefined values by creating empty structures
  const normalizedRecruitment: any = {};
  const normalizedChurn: any = {};

  // Process recruitment data
  if (recruitment && typeof recruitment === 'object') {
    const roles = Object.keys(recruitment);
    for (const role of roles) {
      const roleData = recruitment[role];
      if (!roleData || typeof roleData !== 'object') {
        // Create empty structure for null/undefined role data
        normalizedRecruitment[role] = {};
        continue;
      }
      
      normalizedRecruitment[role] = {};
      
      // Detect if already level-first
      const firstKey = Object.keys(roleData)[0];
      const firstVal = roleData[firstKey];
      const isLevelFirst = typeof firstVal === 'object' && firstVal && Object.keys(firstVal)[0]?.startsWith('2025');
      
      if (isLevelFirst) {
        normalizedRecruitment[role] = roleData;
      } else {
        // month-first: {month: {level: value}}
        // convert to {level: {month: value}}
        const levels = new Set<string>();
        for (const month of Object.keys(roleData)) {
          const monthData = roleData[month];
          if (monthData && typeof monthData === 'object') {
            for (const level of Object.keys(monthData)) {
              levels.add(level);
            }
          }
        }
        
        for (const level of levels) {
          normalizedRecruitment[role][level] = {};
          for (const month of Object.keys(roleData)) {
            const monthData = roleData[month];
            if (monthData && typeof monthData === 'object') {
              const value = monthData[level];
              if (value !== undefined && value !== null) {
                normalizedRecruitment[role][level][month] = value;
              }
            }
          }
        }
      }
    }
  }

  // Process churn data
  if (churn && typeof churn === 'object') {
    const roles = Object.keys(churn);
    for (const role of roles) {
      const roleData = churn[role];
      if (!roleData || typeof roleData !== 'object') {
        // Create empty structure for null/undefined role data
        normalizedChurn[role] = {};
        continue;
      }
      
      normalizedChurn[role] = {};
      
      const firstKey = Object.keys(roleData)[0];
      const firstVal = roleData[firstKey];
      const isLevelFirst = typeof firstVal === 'object' && firstVal && Object.keys(firstVal)[0]?.startsWith('2025');
      
      if (isLevelFirst) {
        normalizedChurn[role] = roleData;
      } else {
        const levels = new Set<string>();
        for (const month of Object.keys(roleData)) {
          const monthData = roleData[month];
          if (monthData && typeof monthData === 'object') {
            for (const level of Object.keys(monthData)) {
              levels.add(level);
            }
          }
        }
        
        for (const level of levels) {
          normalizedChurn[role][level] = {};
          for (const month of Object.keys(roleData)) {
            const monthData = roleData[month];
            if (monthData && typeof monthData === 'object') {
              const value = monthData[level];
              if (value !== undefined && value !== null) {
                normalizedChurn[role][level][month] = value;
              }
            }
          }
        }
      }
    }
  }

  return {
    global: {
      recruitment: normalizedRecruitment,
      churn: normalizedChurn,
    },
  };
} 