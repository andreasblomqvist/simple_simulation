/**
 * Planning Service
 * 
 * Handles business planning calculations, financial projections, and aggregations.
 * Extracted from business planning components to separate calculation logic from UI.
 */

import type { OfficeConfig, StandardRole, StandardLevel } from '../types/office';

export interface SummaryData {
  recruitment: number;
  churn: number;
  netGrowth: number;
  revenue: number;
  cost: number;
  margin: number;
}

export interface CellData {
  role: StandardRole;
  level: StandardLevel;
  month: number;
  year: number;
  recruitment: number;
  churn: number;
  price: number;
  utr: number;
  salary: number;
}

export interface MonthlyCalculation {
  month: number;
  recruitment: number;
  churn: number;
  netGrowth: number;
  revenue: number;
  cost: number;
  margin: number;
}

export interface RoleSummary extends SummaryData {
  role: StandardRole;
}

export interface FinancialMetrics {
  totalRevenue: number;
  totalCosts: number;
  grossProfit: number;
  averageMargin: number;
  averageUTR: number;
  averageRate: number;
}

export interface WorkforceMetrics {
  totalRecruitment: number;
  totalChurn: number;
  netGrowth: number;
  growthRate: number;
  churnRate: number;
}

export interface DetailedCalculations {
  byRole: Map<StandardRole, SummaryData>;
  byMonth: MonthlyCalculation[];
  financial: FinancialMetrics;
  workforce: WorkforceMetrics;
}

export class PlanningService {
  private static readonly STANDARD_ROLES: StandardRole[] = ['Consultant', 'Sales', 'Operations'];
  private static readonly STANDARD_LEVELS: StandardLevel[] = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP'];
  private static readonly HOURS_PER_MONTH = 160;

  /**
   * Format currency values using EUR formatting
   */
  static formatCurrency(value: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  }

  /**
   * Get performance color class based on value and thresholds
   */
  static getPerformanceColor(
    value: number, 
    thresholds: { good: number; warning: number }
  ): string {
    if (value >= thresholds.good) return 'text-green-600 dark:text-green-400';
    if (value >= thresholds.warning) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  }

  /**
   * Calculate monthly revenue for a specific cell
   */
  static calculateMonthlyRevenue(cellData: CellData): number {
    return cellData.price * cellData.utr * this.HOURS_PER_MONTH;
  }

  /**
   * Calculate role-level summary from cell data
   */
  static calculateRoleSummary(
    role: StandardRole,
    getCellData: (role: StandardRole, level: StandardLevel, month: number) => CellData
  ): SummaryData {
    const summary: SummaryData = {
      recruitment: 0,
      churn: 0,
      netGrowth: 0,
      revenue: 0,
      cost: 0,
      margin: 0
    };

    this.STANDARD_LEVELS.forEach(level => {
      for (let month = 1; month <= 12; month++) {
        const cellData = getCellData(role, level, month);
        const monthRevenue = this.calculateMonthlyRevenue(cellData);
        
        summary.recruitment += cellData.recruitment;
        summary.churn += cellData.churn;
        summary.revenue += monthRevenue;
        summary.cost += cellData.salary;
      }
    });

    summary.netGrowth = summary.recruitment - summary.churn;
    summary.margin = summary.revenue > 0 ? 
      ((summary.revenue - summary.cost) / summary.revenue) * 100 : 0;

    return summary;
  }

  /**
   * Calculate monthly breakdown across all roles
   */
  static calculateMonthlyBreakdown(
    getCellData: (role: StandardRole, level: StandardLevel, month: number) => CellData
  ): MonthlyCalculation[] {
    const monthlyData: MonthlyCalculation[] = Array.from({ length: 12 }, (_, i) => ({
      month: i + 1,
      recruitment: 0,
      churn: 0,
      netGrowth: 0,
      revenue: 0,
      cost: 0,
      margin: 0
    }));

    this.STANDARD_ROLES.forEach(role => {
      this.STANDARD_LEVELS.forEach(level => {
        for (let month = 1; month <= 12; month++) {
          const cellData = getCellData(role, level, month);
          const monthRevenue = this.calculateMonthlyRevenue(cellData);
          
          const monthCalc = monthlyData[month - 1];
          monthCalc.recruitment += cellData.recruitment;
          monthCalc.churn += cellData.churn;
          monthCalc.revenue += monthRevenue;
          monthCalc.cost += cellData.salary;
        }
      });
    });

    // Calculate derived values for each month
    monthlyData.forEach(month => {
      month.netGrowth = month.recruitment - month.churn;
      month.margin = month.revenue > 0 ? 
        ((month.revenue - month.cost) / month.revenue) * 100 : 0;
    });

    return monthlyData;
  }

  /**
   * Calculate comprehensive planning metrics
   */
  static calculateDetailedPlanningMetrics(
    office: OfficeConfig,
    year: number,
    totalSummary: SummaryData,
    getCellData: (role: StandardRole, level: StandardLevel, month: number) => CellData
  ): DetailedCalculations {
    const calculations: DetailedCalculations = {
      byRole: new Map<StandardRole, SummaryData>(),
      byMonth: this.calculateMonthlyBreakdown(getCellData),
      financial: {
        totalRevenue: 0,
        totalCosts: 0,
        grossProfit: 0,
        averageMargin: 0,
        averageUTR: 0,
        averageRate: 0
      },
      workforce: {
        totalRecruitment: 0,
        totalChurn: 0,
        netGrowth: 0,
        growthRate: 0,
        churnRate: 0
      }
    };

    // Calculate by role
    this.STANDARD_ROLES.forEach(role => {
      const roleSummary = this.calculateRoleSummary(role, getCellData);
      calculations.byRole.set(role, roleSummary);
    });

    // Calculate financial totals
    calculations.financial.totalRevenue = totalSummary.revenue;
    calculations.financial.totalCosts = totalSummary.cost;
    calculations.financial.grossProfit = totalSummary.revenue - totalSummary.cost;
    calculations.financial.averageMargin = totalSummary.margin;

    // Calculate workforce totals
    calculations.workforce.totalRecruitment = totalSummary.recruitment;
    calculations.workforce.totalChurn = totalSummary.churn;
    calculations.workforce.netGrowth = totalSummary.netGrowth;

    return calculations;
  }

  /**
   * Calculate aggregated financial summary
   */
  static calculateFinancialSummary(
    calculations: DetailedCalculations
  ): {
    totalRevenue: string;
    totalCosts: string;
    grossProfit: string;
    averageMargin: string;
  } {
    return {
      totalRevenue: this.formatCurrency(calculations.financial.totalRevenue),
      totalCosts: this.formatCurrency(calculations.financial.totalCosts),
      grossProfit: this.formatCurrency(calculations.financial.grossProfit),
      averageMargin: `${Math.round(calculations.financial.averageMargin)}%`
    };
  }

  /**
   * Calculate workforce metrics summary
   */
  static calculateWorkforceSummary(
    calculations: DetailedCalculations
  ): {
    totalRecruitment: number;
    totalChurn: number;
    netGrowth: number;
    growthColor: string;
  } {
    return {
      totalRecruitment: calculations.workforce.totalRecruitment,
      totalChurn: calculations.workforce.totalChurn,
      netGrowth: calculations.workforce.netGrowth,
      growthColor: this.getPerformanceColor(
        calculations.workforce.netGrowth,
        { good: 10, warning: 5 }
      )
    };
  }

  /**
   * Calculate role performance breakdown
   */
  static calculateRoleBreakdown(
    calculations: DetailedCalculations
  ): Array<{
    role: StandardRole;
    netGrowth: number;
    margin: number;
    revenue: number;
  }> {
    return Array.from(calculations.byRole.entries()).map(([role, summary]) => ({
      role,
      netGrowth: summary.netGrowth,
      margin: Math.round(summary.margin),
      revenue: summary.revenue
    }));
  }

  /**
   * Calculate monthly trend data for charts
   */
  static calculateMonthlyTrends(
    calculations: DetailedCalculations
  ): Array<{
    month: string;
    shortMonth: string;
    netGrowth: number;
    margin: number;
    revenue: number;
    netGrowthColor: string;
  }> {
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    return calculations.byMonth.map((month, index) => ({
      month: monthNames[index],
      shortMonth: monthNames[index],
      netGrowth: month.netGrowth,
      margin: Math.round(month.margin),
      revenue: Math.round(month.revenue / 1000), // Convert to K
      netGrowthColor: this.getPerformanceColor(
        month.netGrowth,
        { good: 2, warning: 0 }
      )
    }));
  }

  /**
   * Validate planning data integrity
   */
  static validatePlanningData(
    getCellData: (role: StandardRole, level: StandardLevel, month: number) => CellData
  ): {
    valid: boolean;
    errors: string[];
    warnings: string[];
  } {
    const errors: string[] = [];
    const warnings: string[] = [];

    this.STANDARD_ROLES.forEach(role => {
      this.STANDARD_LEVELS.forEach(level => {
        for (let month = 1; month <= 12; month++) {
          const cellData = getCellData(role, level, month);
          
          // Check for negative values
          if (cellData.recruitment < 0) {
            errors.push(`${role} ${level} Month ${month}: Negative recruitment`);
          }
          if (cellData.churn < 0) {
            errors.push(`${role} ${level} Month ${month}: Negative churn`);
          }
          if (cellData.salary < 0) {
            errors.push(`${role} ${level} Month ${month}: Negative salary`);
          }
          
          // Check for unrealistic values
          if (cellData.utr > 1) {
            warnings.push(`${role} ${level} Month ${month}: UTR > 100%`);
          }
          if (cellData.recruitment > 100) {
            warnings.push(`${role} ${level} Month ${month}: Very high recruitment (${cellData.recruitment})`);
          }
        }
      });
    });

    return {
      valid: errors.length === 0,
      errors,
      warnings
    };
  }

  /**
   * Export planning data to structured format
   */
  static exportPlanningData(
    getCellData: (role: StandardRole, level: StandardLevel, month: number) => CellData
  ): {
    summary: DetailedCalculations;
    rawData: CellData[];
    metadata: {
      exportDate: string;
      totalCells: number;
      roles: StandardRole[];
      levels: StandardLevel[];
    };
  } {
    const rawData: CellData[] = [];
    
    this.STANDARD_ROLES.forEach(role => {
      this.STANDARD_LEVELS.forEach(level => {
        for (let month = 1; month <= 12; month++) {
          rawData.push(getCellData(role, level, month));
        }
      });
    });

    // Create dummy total summary for detailed calculations
    const totalSummary: SummaryData = {
      recruitment: 0,
      churn: 0,
      netGrowth: 0,
      revenue: 0,
      cost: 0,
      margin: 0
    };

    rawData.forEach(cell => {
      totalSummary.recruitment += cell.recruitment;
      totalSummary.churn += cell.churn;
      totalSummary.revenue += this.calculateMonthlyRevenue(cell);
      totalSummary.cost += cell.salary;
    });

    totalSummary.netGrowth = totalSummary.recruitment - totalSummary.churn;
    totalSummary.margin = totalSummary.revenue > 0 ? 
      ((totalSummary.revenue - totalSummary.cost) / totalSummary.revenue) * 100 : 0;

    return {
      summary: this.calculateDetailedPlanningMetrics(
        {} as OfficeConfig,
        new Date().getFullYear(),
        totalSummary,
        getCellData
      ),
      rawData,
      metadata: {
        exportDate: new Date().toISOString(),
        totalCells: rawData.length,
        roles: this.STANDARD_ROLES,
        levels: this.STANDARD_LEVELS
      }
    };
  }
}