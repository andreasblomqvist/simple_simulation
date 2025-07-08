// Utility to normalize baseline_input to level-first format
// Converts recruitment[role][month][level] to recruitment[role][level][month]

export function normalizeBaselineInput(baselineInput: any): any {
  if (!baselineInput || !baselineInput.global) return baselineInput;
  const { recruitment, churn } = baselineInput.global;
  const roles = Object.keys(recruitment || {});
  const normalizedRecruitment: any = {};
  const normalizedChurn: any = {};

  for (const role of roles) {
    const roleData = recruitment[role];
    if (!roleData) continue;
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
        for (const level of Object.keys(roleData[month] || {})) {
          levels.add(level);
        }
      }
      for (const level of levels) {
        normalizedRecruitment[role][level] = {};
        for (const month of Object.keys(roleData)) {
          const value = roleData[month][level];
          if (value !== undefined) {
            normalizedRecruitment[role][level][month] = value;
          }
        }
      }
    }
  }

  // Repeat for churn
  for (const role of Object.keys(churn || {})) {
    const roleData = churn[role];
    if (!roleData) continue;
    normalizedChurn[role] = {};
    const firstKey = Object.keys(roleData)[0];
    const firstVal = roleData[firstKey];
    const isLevelFirst = typeof firstVal === 'object' && firstVal && Object.keys(firstVal)[0]?.startsWith('2025');
    if (isLevelFirst) {
      normalizedChurn[role] = roleData;
    } else {
      const levels = new Set<string>();
      for (const month of Object.keys(roleData)) {
        for (const level of Object.keys(roleData[month] || {})) {
          levels.add(level);
        }
      }
      for (const level of levels) {
        normalizedChurn[role][level] = {};
        for (const month of Object.keys(roleData)) {
          const value = roleData[month][level];
          if (value !== undefined) {
            normalizedChurn[role][level][month] = value;
          }
        }
      }
    }
  }

  return {
    ...baselineInput,
    global: {
      ...baselineInput.global,
      recruitment: normalizedRecruitment,
      churn: normalizedChurn,
    },
  };
} 