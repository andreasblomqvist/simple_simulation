/**
 * Business Planning Calculation Engine
 * 
 * Handles automatic calculation of derived fields based on dependencies
 * Uses the field configuration from ExpandablePlanningGrid to determine relationships
 */

import type { StandardRole, StandardLevel } from '../../types/office';

// Monthly data structure for calculations
export interface MonthlyValue {
  jan: number;
  feb: number;
  mar: number;
  apr: number;
  may: number;
  jun: number;
  jul: number;
  aug: number;
  sep: number;
  oct: number;
  nov: number;
  dec: number;
  total: number;
}

// Office-level data (no role/level breakdown)
export interface OfficeData {
  [fieldName: string]: MonthlyValue;
}

// Role/level data structure
export interface RoleLevelData {
  [fieldName: string]: {
    [role in StandardRole]?: {
      [level in StandardLevel]?: MonthlyValue;
    };
  };
}

// Complete business planning data
export interface BusinessPlanningData {
  officeLevel: OfficeData;
  roleLevel: RoleLevelData;
}

// Calculation context for dependency resolution
export interface CalculationContext {
  data: BusinessPlanningData;
  constants: {
    socialSecurityRate: number; // ~14.1% in Norway
    pensionRate: number; // ~2% employer contribution
    vatRate: number; // 25% in Norway
    workingHours: number; // Standard monthly working hours
    workingDaysPerMonth: number; // Average working days
  };
}

/**
 * Business Planning Calculation Engine
 */
export class BusinessPlanningCalculations {
  private static defaultConstants = {
    socialSecurityRate: 0.141, // 14.1% social security contribution
    pensionRate: 0.02, // 2% pension contribution
    vatRate: 0.25, // 25% VAT
    workingHours: 160, // ~20 working days * 8 hours
    workingDaysPerMonth: 20
  };

  /**
   * Calculate all derived fields based on dependencies
   */
  static calculateDerivedFields(
    inputData: BusinessPlanningData,
    constants: Partial<typeof BusinessPlanningCalculations.defaultConstants> = {}
  ): BusinessPlanningData {
    const context: CalculationContext = {
      data: { ...inputData },
      constants: { ...this.defaultConstants, ...constants }
    };

    // Calculate in dependency order
    this.calculateSalaryDerivedFields(context);
    this.calculateRevenueDerivedFields(context);
    this.calculateExpenseDerivedFields(context);
    this.calculateFinancialSummaryFields(context);

    return context.data;
  }

  /**
   * Calculate salary-related derived fields
   */
  private static calculateSalaryDerivedFields(context: CalculationContext): void {
    const { data, constants } = context;

    // Social Security = Gross Salary * 14.1%
    this.calculateRoleLevelField(
      context,
      'social_security',
      (role, level) => {
        const grossSalary = this.getRoleLevelMonthlyValue(data, 'gross_salary', role, level);
        return this.multiplyByConstant(grossSalary, constants.socialSecurityRate);
      }
    );

    // Pension = Gross Salary * 2%
    this.calculateRoleLevelField(
      context,
      'pension',
      (role, level) => {
        const grossSalary = this.getRoleLevelMonthlyValue(data, 'gross_salary', role, level);
        return this.multiplyByConstant(grossSalary, constants.pensionRate);
      }
    );

    // Total Salary Cost = Gross Salary + Social Security + Pension
    this.calculateRoleLevelField(
      context,
      'total_salary_cost',
      (role, level) => {
        const grossSalary = this.getRoleLevelMonthlyValue(data, 'gross_salary', role, level);
        const socialSecurity = this.getRoleLevelMonthlyValue(data, 'social_security', role, level);
        const pension = this.getRoleLevelMonthlyValue(data, 'pension', role, level);
        return this.addMonthlyValues([grossSalary, socialSecurity, pension]);
      }
    );
  }

  /**
   * Calculate revenue-related derived fields
   */
  private static calculateRevenueDerivedFields(context: CalculationContext): void {
    const { data } = context;

    // Net Sales = sum of (price × utr × hours × fte) for all roles
    const netSales = this.createEmptyMonthlyValue();
    
    // Iterate through all roles and levels to calculate revenue
    const roles: StandardRole[] = ['Consultant', 'Sales', 'Recruitment', 'Operations'];
    const levels: StandardLevel[] = ['A', 'B', 'C', 'D'];

    roles.forEach(role => {
      levels.forEach(level => {
        const price = this.getRoleLevelMonthlyValue(data, 'price', role, level);
        const utr = this.getRoleLevelMonthlyValue(data, 'utr', role, level);
        const hours = this.getRoleLevelMonthlyValue(data, 'hours', role, level);
        const fte = this.getRoleLevelMonthlyValue(data, 'fte', role, level);

        // Revenue = price × utr × hours × fte
        const roleRevenue = this.multiplyMonthlyValues([price, utr, hours, fte]);
        this.addToMonthlyValue(netSales, roleRevenue);
      });
    });

    // Set calculated net sales at office level
    data.officeLevel.net_sales = netSales;
    this.calculateTotal(data.officeLevel.net_sales);
  }

  /**
   * Calculate expense-related derived fields
   */
  private static calculateExpenseDerivedFields(context: CalculationContext): void {
    const { data } = context;

    // Total Salary Expenses = sum of total_salary_cost for all roles/levels
    const totalSalaryExpenses = this.createEmptyMonthlyValue();
    
    const roles: StandardRole[] = ['Consultant', 'Sales', 'Recruitment', 'Operations'];
    const levels: StandardLevel[] = ['A', 'B', 'C', 'D'];

    roles.forEach(role => {
      levels.forEach(level => {
        const salaryCost = this.getRoleLevelMonthlyValue(data, 'total_salary_cost', role, level);
        const fte = this.getRoleLevelMonthlyValue(data, 'fte', role, level);
        
        // Total cost = salary cost × FTE count
        const totalCost = this.multiplyMonthlyValues([salaryCost, fte]);
        this.addToMonthlyValue(totalSalaryExpenses, totalCost);
      });
    });

    data.officeLevel.total_salary_expenses = totalSalaryExpenses;
    this.calculateTotal(data.officeLevel.total_salary_expenses);

    // Total Operating Expenses = Office Rent + Severance + Education + External Services + IT Related + External Representation + Depreciation + Travel
    const operatingExpenseFields = [
      'office_rent', 'severance', 'education', 'external_services', 
      'it_related', 'external_representation', 'depreciation', 'travel'
    ];

    const totalOperatingExpenses = this.createEmptyMonthlyValue();
    operatingExpenseFields.forEach(field => {
      const fieldValue = data.officeLevel[field] || this.createEmptyMonthlyValue();
      this.addToMonthlyValue(totalOperatingExpenses, fieldValue);
    });

    data.officeLevel.total_operating_expenses = totalOperatingExpenses;
    this.calculateTotal(data.officeLevel.total_operating_expenses);
  }

  /**
   * Calculate financial summary fields
   */
  private static calculateFinancialSummaryFields(context: CalculationContext): void {
    const { data } = context;

    // EBITDA = Net Sales - Total Salary Expenses - Total Operating Expenses
    const netSales = data.officeLevel.net_sales || this.createEmptyMonthlyValue();
    const totalSalaryExpenses = data.officeLevel.total_salary_expenses || this.createEmptyMonthlyValue();
    const totalOperatingExpenses = data.officeLevel.total_operating_expenses || this.createEmptyMonthlyValue();

    const ebitda = this.subtractMonthlyValues(
      netSales,
      this.addMonthlyValues([totalSalaryExpenses, totalOperatingExpenses])
    );

    data.officeLevel.ebitda = ebitda;
    this.calculateTotal(data.officeLevel.ebitda);

    // EBITDA Margin = (EBITDA / Net Sales) * 100
    const ebitdaMargin = this.createEmptyMonthlyValue();
    const months: (keyof MonthlyValue)[] = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'];
    
    months.forEach(month => {
      const salesValue = netSales[month] || 0;
      const ebitdaValue = ebitda[month] || 0;
      ebitdaMargin[month] = salesValue > 0 ? (ebitdaValue / salesValue) * 100 : 0;
    });

    this.calculateTotal(ebitdaMargin);
    data.officeLevel.ebitda_margin = ebitdaMargin;

    // EBIT = EBITDA - Depreciation
    const depreciation = data.officeLevel.depreciation || this.createEmptyMonthlyValue();
    const ebit = this.subtractMonthlyValues(ebitda, depreciation);
    
    data.officeLevel.ebit = ebit;
    this.calculateTotal(data.officeLevel.ebit);
  }

  /**
   * Calculate a role/level field for all role/level combinations
   */
  private static calculateRoleLevelField(
    context: CalculationContext,
    fieldName: string,
    calculator: (role: StandardRole, level: StandardLevel) => MonthlyValue
  ): void {
    const { data } = context;
    
    if (!data.roleLevel[fieldName]) {
      data.roleLevel[fieldName] = {};
    }

    const roles: StandardRole[] = ['Consultant', 'Sales', 'Recruitment', 'Operations'];
    const levels: StandardLevel[] = ['A', 'B', 'C', 'D'];

    roles.forEach(role => {
      if (!data.roleLevel[fieldName][role]) {
        data.roleLevel[fieldName][role] = {};
      }

      levels.forEach(level => {
        const calculatedValue = calculator(role, level);
        this.calculateTotal(calculatedValue);
        data.roleLevel[fieldName][role]![level] = calculatedValue;
      });
    });
  }

  /**
   * Get monthly value for a specific role/level field
   */
  private static getRoleLevelMonthlyValue(
    data: BusinessPlanningData,
    fieldName: string,
    role: StandardRole,
    level: StandardLevel
  ): MonthlyValue {
    return data.roleLevel[fieldName]?.[role]?.[level] || this.createEmptyMonthlyValue();
  }

  /**
   * Create empty monthly value structure
   */
  private static createEmptyMonthlyValue(): MonthlyValue {
    return {
      jan: 0, feb: 0, mar: 0, apr: 0, may: 0, jun: 0,
      jul: 0, aug: 0, sep: 0, oct: 0, nov: 0, dec: 0,
      total: 0
    };
  }

  /**
   * Multiply monthly value by constant
   */
  private static multiplyByConstant(value: MonthlyValue, constant: number): MonthlyValue {
    return {
      jan: value.jan * constant,
      feb: value.feb * constant,
      mar: value.mar * constant,
      apr: value.apr * constant,
      may: value.may * constant,
      jun: value.jun * constant,
      jul: value.jul * constant,
      aug: value.aug * constant,
      sep: value.sep * constant,
      oct: value.oct * constant,
      nov: value.nov * constant,
      dec: value.dec * constant,
      total: 0 // Will be calculated separately
    };
  }

  /**
   * Multiply multiple monthly values together
   */
  private static multiplyMonthlyValues(values: MonthlyValue[]): MonthlyValue {
    if (values.length === 0) return this.createEmptyMonthlyValue();

    const result = this.createEmptyMonthlyValue();
    const months: (keyof MonthlyValue)[] = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'];

    months.forEach(month => {
      result[month] = values.reduce((product, value) => product * (value[month] || 0), 1);
    });

    return result;
  }

  /**
   * Add multiple monthly values together
   */
  private static addMonthlyValues(values: MonthlyValue[]): MonthlyValue {
    const result = this.createEmptyMonthlyValue();
    const months: (keyof MonthlyValue)[] = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'];

    months.forEach(month => {
      result[month] = values.reduce((sum, value) => sum + (value[month] || 0), 0);
    });

    return result;
  }

  /**
   * Subtract second value from first value
   */
  private static subtractMonthlyValues(value1: MonthlyValue, value2: MonthlyValue): MonthlyValue {
    return {
      jan: value1.jan - value2.jan,
      feb: value1.feb - value2.feb,
      mar: value1.mar - value2.mar,
      apr: value1.apr - value2.apr,
      may: value1.may - value2.may,
      jun: value1.jun - value2.jun,
      jul: value1.jul - value2.jul,
      aug: value1.aug - value2.aug,
      sep: value1.sep - value2.sep,
      oct: value1.oct - value2.oct,
      nov: value1.nov - value2.nov,
      dec: value1.dec - value2.dec,
      total: 0 // Will be calculated separately
    };
  }

  /**
   * Add second value to first value (mutates first value)
   */
  private static addToMonthlyValue(target: MonthlyValue, source: MonthlyValue): void {
    target.jan += source.jan;
    target.feb += source.feb;
    target.mar += source.mar;
    target.apr += source.apr;
    target.may += source.may;
    target.jun += source.jun;
    target.jul += source.jul;
    target.aug += source.aug;
    target.sep += source.sep;
    target.oct += source.oct;
    target.nov += source.nov;
    target.dec += source.dec;
  }

  /**
   * Calculate total for monthly value
   */
  private static calculateTotal(value: MonthlyValue): void {
    value.total = value.jan + value.feb + value.mar + value.apr + value.may + value.jun +
                  value.jul + value.aug + value.sep + value.oct + value.nov + value.dec;
  }

  /**
   * Format currency for display
   */
  static formatCurrency(value: number): string {
    return new Intl.NumberFormat('no-NO', {
      style: 'currency',
      currency: 'NOK',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  }

  /**
   * Format percentage for display
   */
  static formatPercentage(value: number): string {
    return `${value.toFixed(1)}%`;
  }

  /**
   * Get sample data for testing calculations
   */
  static getSampleData(): BusinessPlanningData {
    const sampleMonthlyValue = (baseValue: number): MonthlyValue => ({
      jan: baseValue, feb: baseValue, mar: baseValue, apr: baseValue,
      may: baseValue, jun: baseValue, jul: baseValue, aug: baseValue,
      sep: baseValue, oct: baseValue, nov: baseValue, dec: baseValue,
      total: baseValue * 12
    });

    return {
      officeLevel: {
        office_rent: sampleMonthlyValue(50000),
        severance: sampleMonthlyValue(10000),
        education: sampleMonthlyValue(5000),
        external_services: sampleMonthlyValue(15000),
        it_related: sampleMonthlyValue(8000),
        external_representation: sampleMonthlyValue(3000),
        depreciation: sampleMonthlyValue(12000),
        travel: sampleMonthlyValue(7000)
      },
      roleLevel: {
        gross_salary: {
          Consultant: {
            A: sampleMonthlyValue(65000),
            B: sampleMonthlyValue(75000),
            C: sampleMonthlyValue(85000),
            D: sampleMonthlyValue(95000)
          },
          Sales: {
            A: sampleMonthlyValue(55000),
            B: sampleMonthlyValue(65000),
            C: sampleMonthlyValue(75000),
            D: sampleMonthlyValue(85000)
          }
        },
        price: {
          Consultant: {
            A: sampleMonthlyValue(1200),
            B: sampleMonthlyValue(1400),
            C: sampleMonthlyValue(1600),
            D: sampleMonthlyValue(1800)
          }
        },
        utr: {
          Consultant: {
            A: sampleMonthlyValue(0.75),
            B: sampleMonthlyValue(0.80),
            C: sampleMonthlyValue(0.85),
            D: sampleMonthlyValue(0.90)
          }
        },
        hours: {
          Consultant: {
            A: sampleMonthlyValue(160),
            B: sampleMonthlyValue(160),
            C: sampleMonthlyValue(160),
            D: sampleMonthlyValue(160)
          }
        },
        fte: {
          Consultant: {
            A: sampleMonthlyValue(3),
            B: sampleMonthlyValue(2),
            C: sampleMonthlyValue(1),
            D: sampleMonthlyValue(1)
          }
        }
      }
    };
  }
}