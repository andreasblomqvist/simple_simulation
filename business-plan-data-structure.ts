/**
 * Comprehensive Business Plan Data Structure
 * 
 * Hierarchical structure for Norwegian consulting company workforce planning
 * and financial modeling with clear separation of input/calculated fields.
 */

// ============================================================================
// CORE TYPES & ENUMS
// ============================================================================

export type RoleType = 'Consultant' | 'Sales' | 'Recruitment' | 'Operations';
export type LevelType = 'A' | 'B' | 'C' | 'D';
export type MonthKey = string; // Format: "YYYY-MM"

export interface MonthlyData {
  [monthKey: MonthKey]: number;
}

export interface RoleLevel {
  role: RoleType;
  level: LevelType;
  isBillable: boolean;
}

// ============================================================================
// BUSINESS PLAN STRUCTURE
// ============================================================================

export interface BusinessPlan {
  // Meta Information
  id: string;
  name: string;
  description?: string;
  planPeriod: {
    startMonth: MonthKey;
    endMonth: MonthKey;
  };
  office: string;
  
  // Core Business Planning Sections
  workforce: WorkforcePlan;
  revenue: RevenuePlan;
  expenses: ExpensePlan;
  financials: FinancialSummary; // Calculated fields only
  
  // Metadata
  createdAt: string;
  updatedAt: string;
  version: number;
}

// ============================================================================
// WORKFORCE PLANNING
// ============================================================================

export interface WorkforcePlan {
  // Input Fields
  baseline: WorkforceBaseline;
  planning: WorkforcePlanning;
  
  // Calculated Fields (derived from inputs)
  calculated: WorkforceCalculated;
}

export interface WorkforceBaseline {
  // Starting FTE by role/level
  startingFte: {
    [role in RoleType]: {
      [level in LevelType]?: number;
    };
  };
}

export interface WorkforcePlanning {
  // Monthly planning inputs
  recruitment: {
    [role in RoleType]: {
      [level in LevelType]?: MonthlyData;
    };
  };
  
  churn: {
    [role in RoleType]: {
      [level in LevelType]?: MonthlyData;
    };
  };
  
  // Promotion/progression between levels (optional)
  promotions?: {
    [role in RoleType]: {
      [fromLevel in LevelType]: {
        [toLevel in LevelType]?: MonthlyData;
      };
    };
  };
}

export interface WorkforceCalculated {
  // Monthly workforce metrics (auto-calculated)
  monthlyFte: {
    [role in RoleType]: {
      [level in LevelType]?: MonthlyData;
    };
  };
  
  // Aggregated metrics
  totalFte: MonthlyData;
  billableFte: MonthlyData;
  nonBillableFte: MonthlyData;
  
  // Movement metrics
  totalRecruitment: MonthlyData;
  totalChurn: MonthlyData;
  netHeadcountChange: MonthlyData;
}

// ============================================================================
// REVENUE PLANNING
// ============================================================================

export interface RevenuePlan {
  // Input Fields
  billing: BillingInputs;
  
  // Calculated Fields
  calculated: RevenueCalculated;
}

export interface BillingInputs {
  // Billing rates by role/level
  hourlyRates: {
    [role in RoleType]: {
      [level in LevelType]?: MonthlyData; // Rates can change monthly
    };
  };
  
  // Utilization targets
  utilizationTargets: {
    [role in RoleType]: {
      [level in LevelType]?: MonthlyData; // Percentage (0-100)
    };
  };
  
  // Working hours per month (typically constant but can vary)
  workingHoursPerMonth: MonthlyData;
}

export interface RevenueCalculated {
  // Billable hours and revenue by role/level
  billableHours: {
    [role in RoleType]: {
      [level in LevelType]?: MonthlyData;
    };
  };
  
  revenue: {
    [role in RoleType]: {
      [level in LevelType]?: MonthlyData;
    };
  };
  
  // Aggregated revenue metrics
  totalRevenue: MonthlyData;
  totalBillableHours: MonthlyData;
  averageHourlyRate: MonthlyData;
  
  // Performance metrics
  utilizationRate: MonthlyData; // Actual vs target utilization
  revenuePerFte: MonthlyData;
}

// ============================================================================
// EXPENSE PLANNING
// ============================================================================

export interface ExpensePlan {
  // Input Fields
  personnel: PersonnelExpenseInputs;
  operations: OperationalExpenseInputs;
  
  // Calculated Fields
  calculated: ExpenseCalculated;
}

export interface PersonnelExpenseInputs {
  // Base salaries by role/level
  baseSalaries: {
    [role in RoleType]: {
      [level in LevelType]?: MonthlyData;
    };
  };
  
  // Norwegian-specific personnel costs
  socialSecurityRate: MonthlyData; // Percentage (typically ~14.1%)
  pensionRate: MonthlyData; // Percentage (typically ~2-7%)
  
  // Variable compensation
  bonusAndIncentives?: {
    [role in RoleType]: {
      [level in LevelType]?: MonthlyData;
    };
  };
}

export interface OperationalExpenseInputs {
  // Fixed operational costs
  officeRent: MonthlyData;
  utilities: MonthlyData;
  insurance: MonthlyData;
  
  // Variable operational costs
  travel: MonthlyData;
  externalServices: MonthlyData;
  marketing: MonthlyData;
  training: MonthlyData;
  
  // Equipment and technology
  equipment: MonthlyData;
  software: MonthlyData;
  
  // Other expenses
  other: MonthlyData;
}

export interface ExpenseCalculated {
  // Personnel expense calculations
  grossSalaries: {
    [role in RoleType]: {
      [level in LevelType]?: MonthlyData;
    };
  };
  
  socialSecurityCosts: {
    [role in RoleType]: {
      [level in LevelType]?: MonthlyData;
    };
  };
  
  pensionCosts: {
    [role in RoleType]: {
      [level in LevelType]?: MonthlyData;
    };
  };
  
  totalPersonnelCosts: {
    [role in RoleType]: {
      [level in LevelType]?: MonthlyData;
    };
  };
  
  // Aggregated expense metrics
  totalSalaryExpenses: MonthlyData;
  totalOperationalExpenses: MonthlyData;
  totalExpenses: MonthlyData;
  
  // Cost per FTE metrics
  costPerFte: MonthlyData;
  salaryExpenseRatio: MonthlyData; // Personnel costs as % of total expenses
}

// ============================================================================
// FINANCIAL SUMMARY (ALL CALCULATED)
// ============================================================================

export interface FinancialSummary {
  // Core financial metrics (all calculated)
  grossRevenue: MonthlyData;
  totalExpenses: MonthlyData;
  ebit: MonthlyData; // Earnings Before Interest and Tax
  ebitda: MonthlyData; // EBIT + Depreciation/Amortization
  
  // Profitability metrics
  grossMargin: MonthlyData; // (Revenue - Direct Costs) / Revenue
  ebitMargin: MonthlyData; // EBIT / Revenue
  ebitdaMargin: MonthlyData; // EBITDA / Revenue
  
  // Efficiency metrics
  revenuePerFte: MonthlyData;
  costPerFte: MonthlyData;
  profitPerFte: MonthlyData;
  
  // Cash flow indicators
  operatingCashFlow: MonthlyData;
  
  // Growth metrics
  revenueGrowthRate: MonthlyData; // Month-over-month growth
  fteGrowthRate: MonthlyData;
  
  // Key performance indicators
  utilizationRate: MonthlyData;
  chargeabilityRate: MonthlyData; // Billable FTE / Total FTE
}

// ============================================================================
// CALCULATION HELPERS
// ============================================================================

export interface CalculationContext {
  businessPlan: BusinessPlan;
  roleConfig: RoleConfiguration;
}

export interface RoleConfiguration {
  roles: {
    [role in RoleType]: {
      levels: LevelType[];
      isBillable: boolean;
      description: string;
    };
  };
}

// ============================================================================
// VALIDATION & BUSINESS RULES
// ============================================================================

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

export interface ValidationError {
  field: string;
  message: string;
  severity: 'error' | 'warning';
}

export interface ValidationWarning {
  field: string;
  message: string;
  recommendation?: string;
}

// ============================================================================
// BUSINESS PLAN OPERATIONS
// ============================================================================

export interface BusinessPlanOperations {
  // Calculation functions
  calculateWorkforceMetrics(plan: BusinessPlan): WorkforceCalculated;
  calculateRevenueMetrics(plan: BusinessPlan): RevenueCalculated;
  calculateExpenseMetrics(plan: BusinessPlan): ExpenseCalculated;
  calculateFinancialSummary(plan: BusinessPlan): FinancialSummary;
  
  // Validation functions
  validateBusinessPlan(plan: BusinessPlan): ValidationResult;
  validateWorkforcePlan(workforce: WorkforcePlan): ValidationResult;
  validateRevenuePlan(revenue: RevenuePlan): ValidationResult;
  validateExpensePlan(expenses: ExpensePlan): ValidationResult;
  
  // Utility functions
  aggregateByRole(data: any, role: RoleType): MonthlyData;
  aggregateByLevel(data: any, level: LevelType): MonthlyData;
  aggregateTotal(data: any): MonthlyData;
  
  // Data transformation
  convertToDisplayFormat(plan: BusinessPlan): BusinessPlanDisplay;
  exportToCSV(plan: BusinessPlan): string;
  exportToExcel(plan: BusinessPlan): Blob;
}

// ============================================================================
// DISPLAY & UI HELPERS
// ============================================================================

export interface BusinessPlanDisplay {
  // Formatted data for UI display
  summary: {
    totalFte: number;
    totalRevenue: number;
    totalExpenses: number;
    ebitMargin: number;
  };
  
  // Chart-ready data
  charts: {
    fteByRole: ChartData;
    revenueByMonth: ChartData;
    expensesByCategory: ChartData;
    profitabilityTrend: ChartData;
  };
  
  // Table-ready data
  tables: {
    workforceByRole: TableData;
    revenueByRole: TableData;
    expensesByCategory: TableData;
    monthlyFinancials: TableData;
  };
}

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string;
    borderColor?: string;
  }[];
}

export interface TableData {
  headers: string[];
  rows: (string | number)[][];
}

// ============================================================================
// EXAMPLE USAGE & FACTORY FUNCTIONS
// ============================================================================

export interface BusinessPlanFactory {
  createEmpty(office: string, startMonth: MonthKey, endMonth: MonthKey): BusinessPlan;
  createFromTemplate(template: BusinessPlanTemplate): BusinessPlan;
  createFromPrevious(previousPlan: BusinessPlan, newPeriod: { startMonth: MonthKey; endMonth: MonthKey }): BusinessPlan;
}

export interface BusinessPlanTemplate {
  name: string;
  description: string;
  workforce: Partial<WorkforcePlan>;
  revenue: Partial<RevenuePlan>;
  expenses: Partial<ExpensePlan>;
}

// ============================================================================
// INTEGRATION WITH EXISTING SIMULATION
// ============================================================================

export interface SimulationIntegration {
  // Convert business plan to simulation scenario
  toSimulationScenario(plan: BusinessPlan): any; // Replace 'any' with actual scenario type
  
  // Import simulation results into business plan
  fromSimulationResults(results: any): Partial<BusinessPlan>; // Replace 'any' with actual results type
  
  // Sync baseline data
  syncBaselineFromOfficeConfig(plan: BusinessPlan, officeConfig: any): BusinessPlan;
}