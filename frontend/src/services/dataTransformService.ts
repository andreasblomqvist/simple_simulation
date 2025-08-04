/**
 * Data Transformation Service
 * 
 * Handles data sanitization, transformation, and structure conversion.
 * Extracted from BaselineInputGridV2 to separate data logic from UI.
 */

import { 
  ROLE_LEVELS, 
  ROLES, 
  generateMonthKeys
} from '../types/unified-data-structures';
import type { StandardRole, StandardLevel } from '../types/office';

// Generate months for 3-year simulation using unified month key generator
const DEFAULT_MONTHS = generateMonthKeys(2025, 1, 2027, 12);

export interface RoleDefaults {
  [role: string]: {
    [month: string]: {
      [level: string]: number | undefined;
    };
  };
}

export interface MonthlyRoleData {
  [role: string]: {
    [level: string]: {
      [month: string]: number | undefined;
    };
  };
}

export interface BaselineStructuredData {
  global: {
    recruitment: MonthlyRoleData;
    churn: MonthlyRoleData;
  };
}

export class DataTransformService {
  /**
   * Sanitize a single monthly value - ensures non-negative numbers
   */
  static sanitizeMonthlyValue(value: any): number {
    // Convert to number and handle invalid cases
    if (value === null || value === undefined || value === '' || isNaN(value)) {
      return 0;
    }
    const numValue = Number(value);
    return isNaN(numValue) ? 0 : Math.max(0, numValue); // Ensure non-negative
  }

  /**
   * Sanitize all monthly values in a nested data structure
   */
  static sanitizeMonthlyData(data: any): MonthlyRoleData {
    if (!data || typeof data !== 'object') {
      return {};
    }
    
    const sanitized: MonthlyRoleData = {};
    
    Object.keys(data).forEach(role => {
      if (data[role] && typeof data[role] === 'object') {
        sanitized[role] = {};
        
        Object.keys(data[role]).forEach(level => {
          if (data[role][level] && typeof data[role][level] === 'object') {
            sanitized[role][level] = {};
            
            Object.keys(data[role][level]).forEach(month => {
              const value = data[role][level][month];
              sanitized[role][level][month] = this.sanitizeMonthlyValue(value);
            });
          }
        });
      }
    });
    
    return sanitized;
  }

  /**
   * Get default recruitment values (predefined business data)
   */
  static getRecruitmentDefaults(): RoleDefaults {
    const recruitmentDefaults: RoleDefaults = {
      Consultant: {
        '202501': { A: 20, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
        '202502': { A: 20, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
        '202503': { A: 10, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
        '202504': { A: 15, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
        '202505': { A: 10, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
        '202506': { A: 10, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
        '202507': { A: 5, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
        '202508': { A: 20, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
        '202509': { A: 90, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
        '202510': { A: 20, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
        '202511': { A: 15, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
        '202512': { A: 10, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
      },
      Sales: {},
      Recruitment: {},
    };

    // Fill Sales and Recruitment with 0s for all months/levels
    ROLES.forEach(role => {
      if (role === 'Sales' || role === 'Recruitment') {
        DEFAULT_MONTHS.forEach(month => {
          recruitmentDefaults[role][month] = {};
          ROLE_LEVELS[role].forEach(level => {
            recruitmentDefaults[role][month][level] = 0;
          });
        });
      }
    });

    // Extend Consultant defaults to all years (2026, 2027) by copying 2025 values
    this.extendDefaultsToAllYears(recruitmentDefaults);

    return recruitmentDefaults;
  }

  /**
   * Get default churn (leavers) values (predefined business data)
   */
  static getLeaversDefaults(): RoleDefaults {
    const leaversDefaults: RoleDefaults = {
      Consultant: {
        '202501': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 0, PiP: 0 },
        '202502': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, PiP: 0 },
        '202503': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 0, PiP: 1 },
        '202504': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 0, PiP: 0 },
        '202505': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 0, PiP: 0 },
        '202506': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, PiP: 0 },
        '202507': { A: 4, AC: 4, C: 7, SrC: 7, AM: 9, M: 2, SrM: 0, PiP: 0 },
        '202508': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, PiP: 1 },
        '202509': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 2, PiP: 0 },
        '202510': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, PiP: 1 },
        '202511': { A: 4, AC: 4, C: 7, SrC: 7, AM: 9, M: 2, SrM: 1, PiP: 1 },
        '202512': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, PiP: 0 },
      },
      Sales: {},
      Recruitment: {},
    };

    // Fill Sales and Recruitment with 0s for all months/levels
    ROLES.forEach(role => {
      if (role === 'Sales' || role === 'Recruitment') {
        DEFAULT_MONTHS.forEach(month => {
          leaversDefaults[role][month] = {};
          ROLE_LEVELS[role].forEach(level => {
            leaversDefaults[role][month][level] = 0;
          });
        });
      }
    });

    // Extend Consultant defaults to all years
    this.extendDefaultsToAllYears(leaversDefaults);

    return leaversDefaults;
  }

  /**
   * Extend defaults from 2025 to all subsequent years
   */
  private static extendDefaultsToAllYears(defaults: RoleDefaults): void {
    // For each year after 2025
    for (let year = 2026; year <= 2027; year++) {
      // For each month in that year
      for (let month = 1; month <= 12; month++) {
        const targetMonth = `${year}${month.toString().padStart(2, '0')}`;
        const sourceMonth = `2025${month.toString().padStart(2, '0')}`;
        
        // Copy defaults for Consultant
        if (defaults.Consultant[sourceMonth]) {
          defaults.Consultant[targetMonth] = { ...defaults.Consultant[sourceMonth] };
        }
      }
    }
  }

  /**
   * Initialize role data structure with defaults
   */
  static initRoleData(defaults: RoleDefaults): MonthlyRoleData {
    const data: MonthlyRoleData = {};
    ROLES.forEach(role => {
      data[role] = {};
      ROLE_LEVELS[role].forEach(level => {
        data[role][level] = {};
        DEFAULT_MONTHS.forEach(month => {
          // Use defaults if available, else undefined
          data[role][level][month] =
            (role in defaults && month in defaults[role] && level in defaults[role][month])
              ? defaults[role][month][level]
              : undefined;
        });
      });
    });
    return data;
  }

  /**
   * Initialize data from existing baseline input
   */
  static initializeFromBaseline(initialData: any, dataType: 'recruitment' | 'churn'): MonthlyRoleData {
    // Always expect unified nested structure
    if (!initialData?.global?.[dataType]) {
      const defaults = dataType === 'recruitment' 
        ? this.getRecruitmentDefaults() 
        : this.getLeaversDefaults();
      return this.initRoleData(defaults);
    }

    const sourceData = initialData.global[dataType];
    // sourceData: { Consultant: { levels: { A: { recruitment: { values: { '202501': 10, ... } }, churn: ... }, ... } }, ... }
    const data: MonthlyRoleData = {};
    
    ROLES.forEach(role => {
      data[role] = {};
      const roleLevels = sourceData[role]?.levels || {};
      ROLE_LEVELS[role as keyof typeof ROLE_LEVELS]?.forEach(level => {
        // Default to empty object if missing
        const levelData = roleLevels[level] || {};
        // For recruitment: levelData.recruitment?.values; for churn: levelData.churn?.values
        const values = (dataType === 'recruitment')
          ? levelData.recruitment?.values || {}
          : levelData.churn?.values || {};
        data[role][level] = {};
        DEFAULT_MONTHS.forEach(month => {
          data[role][level][month] = values[month] !== undefined ? values[month] : undefined;
        });
      });
    });
    return data;
  }

  /**
   * Apply 2025 values to all subsequent years for a specific role
   */
  static applyYear2025ToAllYears(
    currentData: MonthlyRoleData,
    selectedRole: StandardRole
  ): MonthlyRoleData {
    // Get 2025 values for the selected role
    const year2025Values: Record<string, Record<string, number | undefined>> = {};
    ROLE_LEVELS[selectedRole].forEach(level => {
      year2025Values[level] = {};
      // Get all 2025 months (202501-202512)
      for (let month = 1; month <= 12; month++) {
        const monthKey = `2025${month.toString().padStart(2, '0')}`;
        year2025Values[level][monthKey] = currentData[selectedRole]?.[level]?.[monthKey];
      }
    });

    // Apply 2025 values to all subsequent years (2026, 2027, etc.)
    const newData = { ...currentData };
    
    // For each year after 2025
    for (let year = 2026; year <= 2027; year++) {
      // For each month in that year
      for (let month = 1; month <= 12; month++) {
        const targetMonth = `${year}${month.toString().padStart(2, '0')}`;
        const sourceMonth = `2025${month.toString().padStart(2, '0')}`;
        
        // Copy values for each level
        ROLE_LEVELS[selectedRole].forEach(level => {
          if (!newData[selectedRole]) newData[selectedRole] = {};
          if (!newData[selectedRole][level]) newData[selectedRole][level] = {};
          
          newData[selectedRole][level][targetMonth] = this.sanitizeMonthlyValue(year2025Values[level][sourceMonth]);
        });
      }
    }
    
    return newData;
  }

  /**
   * Build final baseline input structure for API
   */
  static buildBaselineInputStructure(
    recruitmentData: MonthlyRoleData,
    leaversData: MonthlyRoleData
  ): BaselineStructuredData {
    return {
      global: {
        recruitment: this.sanitizeMonthlyData(recruitmentData),
        churn: this.sanitizeMonthlyData(leaversData),
      }
    };
  }

  /**
   * Get default months array
   */
  static getDefaultMonths(): string[] {
    return DEFAULT_MONTHS;
  }

  /**
   * Transform data for table display
   */
  static transformDataForTable(
    data: MonthlyRoleData,
    selectedRole: StandardRole
  ): Array<{
    month: string;
    [level: string]: any;
  }> {
    const levels = ROLE_LEVELS[selectedRole];
    
    return DEFAULT_MONTHS.map(month => ({
      month,
      ...levels.reduce((acc, level) => {
        acc[level] = data[selectedRole]?.[level]?.[month];
        return acc;
      }, {} as Record<string, number | undefined>),
    }));
  }
}