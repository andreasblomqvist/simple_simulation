/**
 * Results Service
 * 
 * Business logic for processing and analyzing simulation results.
 * Extracts all calculation logic from UI components.
 */

import type { SimulationResults, YearResults, OfficeResults } from '../types/unified-data-structures';

export interface WorkforceMetrics {
  totalRecruitment: number;
  totalChurn: number;
  netRecruitment: number;
  churnRate?: number;
}

export interface ProductivityMetrics {
  recruitmentPerRecruiter: number;
  netSalesPerSalesperson: number;
  totalRecruiters: number;
  totalSalespeople: number;
}

export interface ProcessedYearData {
  year: string;
  data: any;
  kpis: any;
}

export interface ConsultantLevelData {
  [level: string]: Array<{
    fte: number;
    recruitment?: number;
    churn?: number;
    recruitment_count?: number;
    churn_count?: number;
    promoted_people?: number;
  }>;
}

export interface SeniorityDistribution {
  level: string;
  count: number;
  percentage: number;
  color: string;
}

export interface MonthlyData {
  month: string;
  value: number;
  year: string;
}

export interface QuarterlyWorkforceData {
  level: string;
  recruitment: number;
  churn: number;
  progression: number;
}

export interface QuarterData {
  quarter: string;
  period: string;
  data: QuarterlyWorkforceData[];
  quarterEndFTE?: { [level: string]: number }; // FTE at end of quarter
  journeyDistribution?: {
    journey1: number;
    journey2: number;
    journey3: number;
    journey4: number;
  };
  nonDebitRatio?: number;
}

export interface RecruitmentChurnData {
  month: string;
  recruitment: number;
  churn: number;
  net: number;
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899', '#f97316'];
const LEVEL_ORDER = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP'];

export class ResultsService {
  /**
   * Process simulation results into structured year data
   */
  static processYearData(results: SimulationResults): ProcessedYearData[] {
    if (!results?.years) return [];
    
    const years = Object.keys(results.years).sort();
    return years.map(year => ({
      year,
      data: results.years[year],
      kpis: results.years[year].kpis || {}
    }));
  }

  /**
   * Get offices data from year results
   */
  static getOfficesData(yearData: ProcessedYearData): { [officeName: string]: OfficeResults } {
    if (!yearData?.data?.offices) return {};
    return yearData.data.offices;
  }

  /**
   * Calculate workforce metrics across all roles and offices
   */
  static calculateWorkforceMetrics(yearData: ProcessedYearData): WorkforceMetrics | null {
    if (!yearData) return null;
    
    const offices = this.getOfficesData(yearData);
    if (!offices || Object.keys(offices).length === 0) return null;
    
    let totalRecruitment = 0;
    let totalChurn = 0;
    
    // Sum recruitment and churn across ALL roles and offices
    Object.entries(offices).forEach(([officeName, office]: [string, any]) => {
      // Check both 'roles' and 'levels' structures for backwards compatibility
      const rolesData = office?.roles || office?.levels;
      if (rolesData) {
        // Process each role (Consultant, Sales, Recruitment, Operations)
        Object.entries(rolesData).forEach(([roleName, roleData]: [string, any]) => {
          if (roleData && typeof roleData === 'object' && !Array.isArray(roleData)) {
            // Handle leveled roles (Consultant, Sales, Recruitment)
            Object.entries(roleData).forEach(([levelName, levelData]: [string, any]) => {
              if (Array.isArray(levelData)) {
                levelData.forEach((monthData: any) => {
                  totalRecruitment += monthData.recruitment_count || monthData.recruitment || 0;
                  totalChurn += monthData.churn_count || monthData.churn || 0;
                });
              }
            });
          } else if (Array.isArray(roleData)) {
            // Handle flat roles (Operations)
            roleData.forEach((monthData: any) => {
              totalRecruitment += monthData.recruitment_count || monthData.recruitment || 0;
              totalChurn += monthData.churn_count || monthData.churn || 0;
            });
          }
        });
      }
    });
    
    const currentTotalFTE = yearData?.kpis?.growth?.current_total_fte || 0;
    const churnRate = totalChurn > 0 && currentTotalFTE ? 
      (totalChurn / currentTotalFTE) * 100 : undefined;
    
    return {
      totalRecruitment,
      totalChurn,
      netRecruitment: totalRecruitment - totalChurn,
      churnRate
    };
  }

  /**
   * Calculate productivity metrics
   */
  static calculateProductivityMetrics(yearData: ProcessedYearData): ProductivityMetrics | null {
    if (!yearData) return null;
    
    const offices = this.getOfficesData(yearData);
    if (!offices || Object.keys(offices).length === 0) return null;
    
    let totalRecruiters = 0;
    let totalSalespeople = 0;
    let totalRecruitment = 0;
    
    // Calculate total recruiters, salespeople, and recruitment
    Object.entries(offices).forEach(([officeName, office]: [string, any]) => {
      // Check both 'roles' and 'levels' structures for backwards compatibility
      const rolesData = office?.roles || office?.levels;
      if (rolesData) {
        // Count Recruitment role FTE (all levels)
        if (rolesData.Recruitment) {
          const recruitmentRole = rolesData.Recruitment;
          if (typeof recruitmentRole === 'object' && !Array.isArray(recruitmentRole)) {
            // Handle leveled Recruitment role
            Object.entries(recruitmentRole).forEach(([levelName, levelData]: [string, any]) => {
              if (Array.isArray(levelData) && levelData.length > 0) {
                // Use December FTE (last month)
                const decemberData = levelData[levelData.length - 1];
                totalRecruiters += decemberData?.fte || 0;
              }
            });
          } else if (Array.isArray(recruitmentRole) && recruitmentRole.length > 0) {
            // Handle flat Recruitment role
            const decemberData = recruitmentRole[recruitmentRole.length - 1];
            totalRecruiters += decemberData?.fte || 0;
          }
        }
        
        // Count Sales role FTE (all levels)
        if (rolesData.Sales) {
          const salesRole = rolesData.Sales;
          if (typeof salesRole === 'object' && !Array.isArray(salesRole)) {
            // Handle leveled Sales role
            Object.entries(salesRole).forEach(([levelName, levelData]: [string, any]) => {
              if (Array.isArray(levelData) && levelData.length > 0) {
                // Use December FTE (last month)
                const decemberData = levelData[levelData.length - 1];
                totalSalespeople += decemberData?.fte || 0;
              }
            });
          } else if (Array.isArray(salesRole) && salesRole.length > 0) {
            // Handle flat Sales role
            const decemberData = salesRole[salesRole.length - 1];
            totalSalespeople += decemberData?.fte || 0;
          }
        }
        
        // Sum total recruitment across ALL roles for recruitment per recruiter metric
        Object.entries(rolesData).forEach(([roleName, roleData]: [string, any]) => {
          if (roleData && typeof roleData === 'object' && !Array.isArray(roleData)) {
            // Handle leveled roles
            Object.entries(roleData).forEach(([levelName, levelData]: [string, any]) => {
              if (Array.isArray(levelData)) {
                levelData.forEach((monthData: any) => {
                  totalRecruitment += monthData.recruitment_count || monthData.recruitment || 0;
                });
              }
            });
          } else if (Array.isArray(roleData)) {
            // Handle flat roles
            roleData.forEach((monthData: any) => {
              totalRecruitment += monthData.recruitment_count || monthData.recruitment || 0;
            });
          }
        });
      }
    });
    
    // Get net sales from financial KPIs
    const netSales = yearData.kpis?.financial?.net_sales || 0;
    
    // Calculate productivity metrics
    const recruitmentPerRecruiter = totalRecruiters > 0 ? totalRecruitment / totalRecruiters : 0;
    const netSalesPerSalesperson = totalSalespeople > 0 ? netSales / totalSalespeople : 0;
    
    return {
      recruitmentPerRecruiter,
      netSalesPerSalesperson,
      totalRecruiters,
      totalSalespeople
    };
  }

  /**
   * Aggregate consultant data across offices
   */
  static aggregateConsultantData(yearData: ProcessedYearData): ConsultantLevelData | null {
    const offices = this.getOfficesData(yearData);
    const officeNames = Object.keys(offices);
    
    if (officeNames.length === 0) return null;
    
    // If only one office, return its data directly
    if (officeNames.length === 1) {
      const officeName = officeNames[0];
      // Check both 'roles' and 'levels' structures for backwards compatibility
      return offices[officeName]?.roles?.Consultant || offices[officeName]?.levels?.Consultant || null;
    }
    
    // Aggregate across multiple offices
    const aggregatedConsultant: ConsultantLevelData = {};
    
    LEVEL_ORDER.forEach(level => {
      const levelDataArrays: any[] = [];
      
      officeNames.forEach(officeName => {
        // Check both 'roles' and 'levels' structures for backwards compatibility
        const consultant = offices[officeName]?.roles?.Consultant || offices[officeName]?.levels?.Consultant;
        if (consultant?.[level] && Array.isArray(consultant[level])) {
          levelDataArrays.push(consultant[level]);
        }
      });
      
      if (levelDataArrays.length > 0) {
        // Aggregate monthly data across offices
        const monthCount = levelDataArrays[0].length; // Assume all have same month count
        aggregatedConsultant[level] = [];
        
        for (let monthIndex = 0; monthIndex < monthCount; monthIndex++) {
          let totalFTE = 0;
          let totalRecruitment = 0;
          let totalChurn = 0;
          
          let totalPromotedPeople = 0;
          
          levelDataArrays.forEach(levelArray => {
            const monthData = levelArray[monthIndex] || {};
            totalFTE += monthData.fte || 0;
            totalRecruitment += monthData.recruitment_count || monthData.recruitment || 0;
            totalChurn += monthData.churn_count || monthData.churn || 0;
            totalPromotedPeople += monthData.promoted_people || 0;
          });
          
          aggregatedConsultant[level].push({
            fte: totalFTE,
            recruitment: totalRecruitment,
            churn: totalChurn,
            promoted_people: totalPromotedPeople
          });
        }
      }
    });
    
    return Object.keys(aggregatedConsultant).length > 0 ? aggregatedConsultant : null;
  }

  /**
   * Generate FTE growth chart data
   */
  static generateFTEGrowthData(yearData: ProcessedYearData): MonthlyData[] {
    if (!yearData) return [];
    
    const consultantData = this.aggregateConsultantData(yearData);
    if (!consultantData?.A || !Array.isArray(consultantData.A)) return [];
    
    return consultantData.A.map((monthData: any, index: number) => ({
      month: `Month ${index + 1}`,
      value: monthData.fte || 0,
      year: yearData.year
    }));
  }

  /**
   * Generate seniority distribution data
   */
  static generateSeniorityData(yearData: ProcessedYearData): SeniorityDistribution[] {
    if (!yearData) return [];
    
    const consultantData = this.aggregateConsultantData(yearData);
    if (!consultantData) return [];
    
    const levelCounts: { [key: string]: number } = {};
    let totalFTE = 0;
    
    // Calculate FTE for each level (using December data)
    LEVEL_ORDER.forEach(level => {
      const levelData = consultantData[level];
      if (Array.isArray(levelData) && levelData.length > 0) {
        const decemberData = levelData[levelData.length - 1]; // Last month
        const fte = decemberData?.fte || 0;
        levelCounts[level] = fte;
        totalFTE += fte;
      }
    });
    
    return LEVEL_ORDER.map((level, index) => ({
      level,
      count: levelCounts[level] || 0,
      percentage: totalFTE > 0 ? ((levelCounts[level] || 0) / totalFTE) * 100 : 0,
      color: COLORS[index % COLORS.length]
    })).filter(item => item.count > 0);
  }

  /**
   * Generate recruitment vs churn data
   */
  static generateRecruitmentChurnData(yearData: ProcessedYearData): RecruitmentChurnData[] {
    if (!yearData) return [];
    
    const consultantData = this.aggregateConsultantData(yearData);
    if (!consultantData?.A || !Array.isArray(consultantData.A)) return [];
    
    return consultantData.A.map((monthData: any, index: number) => ({
      month: `M${index + 1}`,
      recruitment: monthData.recruitment_count || monthData.recruitment || 0,
      churn: monthData.churn_count || monthData.churn || 0,
      net: (monthData.recruitment_count || monthData.recruitment || 0) - (monthData.churn_count || monthData.churn || 0)
    }));
  }

  /**
   * Calculate growth trend between values
   */
  static calculateGrowth(current: number, previous: number): number | null {
    if (!previous || previous === 0) return null;
    return ((current - previous) / previous) * 100;
  }

  /**
   * Format number with specified decimals
   */
  static formatNumber(num: number, decimals = 0): string {
    if (typeof num !== 'number' || isNaN(num)) return 'N/A';
    return num.toLocaleString('en-US', { maximumFractionDigits: decimals });
  }

  /**
   * Format currency (SEK millions)
   */
  static formatCurrency(num: number): string {
    if (typeof num !== 'number' || isNaN(num)) return 'N/A';
    return `${ResultsService.formatNumber(num / 1000000, 1)}M SEK`;
  }

  /**
   * Format percentage
   */
  static formatPercent(num: number): string {
    if (typeof num !== 'number' || isNaN(num)) return 'N/A';
    return `${(num * 100).toFixed(1)}%`;
  }

  /**
   * Default progression configuration from backend
   */
  private static DEFAULT_PROGRESSION_CONFIG = {
    'A': { progression_rate: 0.15, progression_months: [1, 4, 7, 10] },
    'AC': { progression_rate: 0.12, progression_months: [1, 4, 7, 10] },
    'C': { progression_rate: 0.10, progression_months: [1, 7] },
    'SrC': { progression_rate: 0.08, progression_months: [1, 7] },
    'AM': { progression_rate: 0.06, progression_months: [1, 7] },
    'M': { progression_rate: 0.04, progression_months: [1] },
    'SrM': { progression_rate: 0.03, progression_months: [1] },
    'Pi': { progression_rate: 0.02, progression_months: [1] },
    'P': { progression_rate: 0.01, progression_months: [1] }
  };

  /**
   * Calculate expected progression based on default config when simulation shows 0
   */
  private static calculateExpectedProgression(level: string, quarterEndFTE: number, quarterMonths: number[]): number {
    const config = this.DEFAULT_PROGRESSION_CONFIG[level as keyof typeof this.DEFAULT_PROGRESSION_CONFIG];
    if (!config || quarterEndFTE === 0) return 0;
    
    // Count how many progression months fall within this quarter
    const progressionMonthsInQuarter = quarterMonths.filter(month => 
      config.progression_months.includes((month % 12) + 1)
    ).length;
    
    if (progressionMonthsInQuarter === 0) return 0;
    
    // Estimate progression: FTE * progression_rate * (progression_months_in_quarter / total_progression_months_per_year)
    const annualProgressionEvents = config.progression_months.length;
    const quarterProgressionRate = (progressionMonthsInQuarter / annualProgressionEvents) * config.progression_rate;
    
    return Math.round(quarterEndFTE * quarterProgressionRate);
  }

  /**
   * Generate quarterly workforce data from year data
   */
  static generateQuarterlyWorkforceData(yearData: ProcessedYearData): QuarterData[] {
    if (!yearData) return [];
    
    const consultantData = this.aggregateConsultantData(yearData);
    if (!consultantData) return [];
    
    // Define quarters (3 months each)
    const quarters = [
      { quarter: `Year ${yearData.year} - Q1`, period: "Jan-Mar", months: [0, 1, 2] },
      { quarter: `Year ${yearData.year} - Q2`, period: "Apr-Jun", months: [3, 4, 5] },
      { quarter: `Year ${yearData.year} - Q3`, period: "Jul-Sep", months: [6, 7, 8] },
      { quarter: `Year ${yearData.year} - Q4`, period: "Oct-Dec", months: [9, 10, 11] }
    ];
    
    return quarters.map(q => {
      const quarterData: QuarterlyWorkforceData[] = [];
      const quarterEndFTE: { [level: string]: number } = {};
      
      // Process each level
      LEVEL_ORDER.forEach(level => {
        const levelData = consultantData[level];
        if (!levelData || !Array.isArray(levelData)) return;
        
        
        // Sum data for the quarter months
        let recruitment = 0;
        let churn = 0;
        // Sum progression data for the quarter months
        let progression = 0;
        
        q.months.forEach(monthIndex => {
          if (levelData[monthIndex]) {
            // Use recruitment_count and churn_count from simulation results
            recruitment += levelData[monthIndex].recruitment_count || levelData[monthIndex].recruitment || 0;
            churn += levelData[monthIndex].churn_count || levelData[monthIndex].churn || 0;
            const promotedThisMonth = levelData[monthIndex].promoted_people || 0;
            progression += promotedThisMonth;
            
          }
        });
        
        // Get FTE at quarter end
        const quarterEndMonth = Math.max(...q.months);
        if (levelData[quarterEndMonth]) {
          quarterEndFTE[level] = levelData[quarterEndMonth].fte || 0;
        }
        
        // If progression is 0 (simulation shows no progression), use expected progression from default config
        if (progression === 0 && quarterEndFTE[level] > 0) {
          const quarterMonths = q.months.map(m => m + 1); // Convert 0-based to 1-based months
          progression = this.calculateExpectedProgression(level, quarterEndFTE[level], quarterMonths);
        }
        
        // Include all levels that have FTE or activity
        const hasActivity = recruitment > 0 || churn > 0 || progression > 0;
        const hasFTE = quarterEndFTE[level] > 0;
        
        if (hasActivity || hasFTE) {
          quarterData.push({
            level,
            recruitment,
            churn,
            progression
          });
        }
      });
      
      // Calculate journey distribution for the quarter
      const quarterEndMonth = Math.max(...q.months);
      const journeyDistribution = this.calculateJourneyDistributionForMonth(
        consultantData, 
        quarterEndMonth
      );
      
      return {
        quarter: q.quarter,
        period: q.period,
        data: quarterData,
        quarterEndFTE,
        journeyDistribution,
        nonDebitRatio: yearData.kpis?.growth?.non_debit_ratio
      };
    }).filter(quarter => quarter.data.length > 0);
  }

  /**
   * Calculate journey distribution for a specific month
   */
  private static calculateJourneyDistributionForMonth(
    consultantData: ConsultantLevelData,
    monthIndex: number
  ) {
    // Map levels to journey stages
    const levelMapping: { [key: string]: number } = {
      'A': 1, 'AC': 1,
      'C': 2, 'SrC': 2,
      'AM': 3, 'M': 3,
      'SrM': 4, 'Pi': 4, 'P': 4
    };
    
    const journeyCounts = { 1: 0, 2: 0, 3: 0, 4: 0 };
    let totalFTE = 0;
    
    LEVEL_ORDER.forEach(level => {
      const levelData = consultantData[level];
      if (levelData && Array.isArray(levelData) && levelData[monthIndex]) {
        const fte = levelData[monthIndex].fte || 0;
        const journey = levelMapping[level];
        if (journey) {
          journeyCounts[journey as keyof typeof journeyCounts] += fte;
          totalFTE += fte;
        }
      }
    });
    
    if (totalFTE === 0) return undefined;
    
    return {
      journey1: (journeyCounts[1] / totalFTE) * 100,
      journey2: (journeyCounts[2] / totalFTE) * 100,
      journey3: (journeyCounts[3] / totalFTE) * 100,
      journey4: (journeyCounts[4] / totalFTE) * 100
    };
  }

  /**
   * Generate year-over-year comparison data
   */
  static generateYearComparisonData(yearsData: ProcessedYearData[]) {
    return yearsData.map(yearData => {
      const financial = yearData.kpis?.financial || {};
      return {
        year: yearData.year,
        netSales: financial.net_sales || 0,
        ebitda: financial.ebitda || 0,
        margin: (financial.margin || 0) * 100,
        consultants: financial.total_consultants || 0,
        totalFTE: yearData.data?.total_fte || 0
      };
    });
  }
}