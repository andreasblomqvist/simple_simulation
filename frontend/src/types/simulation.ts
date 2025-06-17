// Simulation Types for Enhanced UI with Year-by-Year Navigation
// Comprehensive type definitions for v2 components and data structures

// ========================================
// Base Types & Enums
// ========================================

export type SimulationYear = number;
export type OfficeCode = string;
export type LeverType = 'recruitment' | 'pricing' | 'operations' | 'sales' | 'attrition';
export type LevelType = 'A' | 'B' | 'C' | 'SrC' | 'M' | 'SrM' | 'PiP' | 'AM+';
export type JourneyType = 'Journey 1' | 'Journey 2' | 'Journey 3' | 'Journey 4';
export type TimePeriodType = 'month' | 'quarter' | 'year';
export type TrendDirection = 'up' | 'down' | 'stable';
export type DataStatus = 'loading' | 'success' | 'error' | 'cached';

// ========================================
// Year Navigation Types
// ========================================

export interface YearNavigationState {
  selectedYear: SimulationYear;
  availableYears: SimulationYear[];
  loading: boolean;
  error: string | null;
  cache: Map<SimulationYear, SimulationYearData>;
  preloadingYears: Set<SimulationYear>;
}

export interface YearNavigationActions {
  setSelectedYear: (year: SimulationYear) => void;
  preloadYear: (year: SimulationYear) => Promise<void>;
  clearCache: () => void;
  refreshYear: (year: SimulationYear) => Promise<void>;
}

export interface YearNavigationContext extends YearNavigationState, YearNavigationActions {}

// ========================================
// KPI & Financial Data Types
// ========================================

export interface BaseKPI {
  value: number;
  unit: 'currency' | 'percentage' | 'count' | 'hours';
  displayFormat?: string;
  target?: number;
  baseline?: number;
}

export interface KPIWithTrend extends BaseKPI {
  trend: TrendDirection;
  trendPercentage: number;
  previousValue?: number;
  changeFromBaseline?: number;
  changeFromTarget?: number;
}

export interface YearOverYearKPI extends KPIWithTrend {
  yearOverYearChange: number;
  yearOverYearPercentage: number;
  sparklineData: SparklineDataPoint[];
  historicalValues: Record<SimulationYear, number>;
}

export interface SparklineDataPoint {
  year: SimulationYear;
  month?: number;
  value: number;
  isProjected?: boolean;
  isHighlight?: boolean;
}

// ========================================
// Office & Organizational Data Types
// ========================================

export interface OfficeData {
  code: OfficeCode;
  name: string;
  journey: JourneyType;
  headcount: HeadcountData;
  financial: FinancialData;
  growth: GrowthData;
  location: {
    city: string;
    country: string;
    timezone: string;
  };
  isActive: boolean;
}

export interface HeadcountData {
  total: number;
  byLevel: Record<LevelType, number>;
  byDepartment: Record<string, number>;
  utilizationRate: number;
  billableHours: number;
}

export interface FinancialData {
  revenue: YearOverYearKPI;
  expenses: YearOverYearKPI;
  ebitda: YearOverYearKPI;
  ebitdaMargin: YearOverYearKPI;
  averagePrice: YearOverYearKPI;
  salaryExpenses: YearOverYearKPI;
  otherExpenses: YearOverYearKPI;
}

export interface GrowthData {
  totalGrowth: YearOverYearKPI;
  netHiring: YearOverYearKPI;
  attrition: YearOverYearKPI;
  recruitmentRate: YearOverYearKPI;
  byLevel: Record<LevelType, GrowthMetrics>;
}

export interface GrowthMetrics {
  hired: number;
  left: number;
  net: number;
  rate: number;
}

// ========================================
// Simulation Configuration Types
// ========================================

export interface SimulationConfig {
  levers: SimulationLever[];
  scope: SimulationScope;
  economicParameters: EconomicParameters;
  duration: number; // months
  startDate: Date;
  endDate: Date;
}

export interface SimulationLever {
  type: LeverType;
  level: LevelType;
  value: number;
  unit: 'percentage' | 'absolute' | 'rate';
  applyToAll: {
    months: boolean;
    offices: boolean;
  };
  targetOffices?: OfficeCode[];
  targetMonths?: number[];
  description?: string;
  constraints?: {
    min: number;
    max: number;
    step: number;
  };
}

export interface SimulationScope {
  timePeriod: TimePeriodType;
  selectedOffices: OfficeCode[];
  applyToAllOffices: boolean;
  selectedMonths: number[];
  applyToAllMonths: boolean;
  duration: number;
}

export interface EconomicParameters {
  priceIncrease: number; // percentage
  salaryIncrease: number; // percentage
  workingHours: number; // per month
  otherExpenses: number; // absolute value
  inflationRate?: number;
  exchangeRates?: Record<string, number>;
}

// ========================================
// Simulation Results & Data Types
// ========================================

export interface SimulationYearData {
  year: SimulationYear;
  offices: Record<OfficeCode, OfficeData>;
  aggregated: AggregatedData;
  metadata: SimulationMetadata;
  dataStatus: DataStatus;
  lastUpdated: Date;
}

export interface AggregatedData {
  financial: FinancialData;
  headcount: HeadcountData;
  growth: GrowthData;
  kpis: Record<string, YearOverYearKPI>;
  summary: SimulationSummary;
}

export interface SimulationSummary {
  totalRevenue: number;
  totalExpenses: number;
  totalEbitda: number;
  totalHeadcount: number;
  averageMargin: number;
  topPerformingOffices: OfficeCode[];
  keyInsights: string[];
}

export interface SimulationMetadata {
  generatedAt: Date;
  configHash: string;
  version: string;
  processingTime: number;
  dataQuality: {
    completeness: number; // percentage
    accuracy: number; // percentage
    freshness: number; // hours since last update
  };
}

// ========================================
// UI Component Prop Types
// ========================================

export interface EnhancedKPICardProps {
  title: string;
  kpi: YearOverYearKPI;
  size?: 'small' | 'medium' | 'large';
  showSparkline?: boolean;
  showYearOverYear?: boolean;
  interactive?: boolean;
  onClick?: () => void;
  className?: string;
  loading?: boolean;
}

export interface YearSelectorProps {
  selectedYear: SimulationYear;
  availableYears: SimulationYear[];
  onYearChange: (year: SimulationYear) => void;
  loading?: boolean;
  disabled?: boolean;
  size?: 'small' | 'medium' | 'large';
  type?: 'tabs' | 'dropdown' | 'buttons';
  showYearRange?: boolean;
  className?: string;
}

export interface SimulationLeversCardProps {
  config: SimulationConfig;
  onConfigChange: (config: SimulationConfig) => void;
  availableLevers: LeverType[];
  availableLevels: Record<LeverType, LevelType[]>;
  availableOffices: OfficeData[];
  loading?: boolean;
  disabled?: boolean;
  showHelp?: boolean;
  className?: string;
}

export interface CollapsiblePanelProps {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
  disabled?: boolean;
  extra?: React.ReactNode;
  className?: string;
  onToggle?: (open: boolean) => void;
}

// ========================================
// Chart & Visualization Types
// ========================================

export interface ChartDataPoint {
  year: SimulationYear;
  month?: number;
  value: number;
  label?: string;
  color?: string;
  isProjected?: boolean;
  metadata?: Record<string, any>;
}

export interface MultiYearTrendData {
  title: string;
  data: ChartDataPoint[];
  yAxisLabel: string;
  unit: string;
  targetLine?: number;
  baselineLine?: number;
  annotations?: ChartAnnotation[];
}

export interface ChartAnnotation {
  year: SimulationYear;
  month?: number;
  text: string;
  type: 'milestone' | 'warning' | 'info' | 'success';
  position: 'top' | 'bottom' | 'left' | 'right';
}

export interface YearOverYearComparisonData {
  categories: string[];
  currentYear: {
    year: SimulationYear;
    values: number[];
  };
  previousYear: {
    year: SimulationYear;
    values: number[];
  };
  changes: {
    absolute: number[];
    percentage: number[];
  };
}

// ========================================
// Data Table Types
// ========================================

export interface EnhancedTableColumn {
  key: string;
  title: string;
  dataIndex: string;
  width?: number;
  fixed?: 'left' | 'right';
  sortable?: boolean;
  filterable?: boolean;
  yearOverYear?: boolean;
  render?: (value: any, record: any, index: number) => React.ReactNode;
  yearOverYearRender?: (current: number, previous: number) => React.ReactNode;
}

export interface EnhancedTableData {
  key: string;
  [field: string]: any;
  yearOverYearData?: Record<string, any>;
  metadata?: {
    hasDetails: boolean;
    office?: OfficeCode;
    level?: LevelType;
    year?: SimulationYear;
  };
}

export interface TablePaginationConfig {
  current: number;
  pageSize: number;
  total: number;
  showSizeChanger: boolean;
  showQuickJumper: boolean;
  showTotal: (total: number, range: [number, number]) => string;
}

// ========================================
// API Response Types
// ========================================

export interface SimulationAPIResponse<T = any> {
  data: T;
  metadata: {
    timestamp: string;
    requestId: string;
    processingTime: number;
    cacheHit: boolean;
  };
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

export interface YearDataAPIResponse extends SimulationAPIResponse<SimulationYearData> {}

export interface OfficeListAPIResponse extends SimulationAPIResponse<OfficeData[]> {}

export interface KPIAPIResponse extends SimulationAPIResponse<Record<string, YearOverYearKPI>> {}

// ========================================
// Utility Types
// ========================================

export type PartialSimulationConfig = Partial<SimulationConfig>;

export type KPIKey = keyof FinancialData | keyof GrowthData | 'headcount' | 'utilization';

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

export type WithTimestamp<T> = T & { timestamp: Date };

export type WithLoading<T> = T & { loading: boolean };

export type WithError<T> = T & { error: string | null };

// ========================================
// Form & Validation Types
// ========================================

export interface FormValidationRule {
  required?: boolean;
  min?: number;
  max?: number;
  pattern?: RegExp;
  validator?: (value: any) => Promise<string | void>;
  message?: string;
}

export interface FormFieldConfig {
  name: string;
  label: string;
  type: 'input' | 'select' | 'number' | 'checkbox' | 'radio' | 'date';
  placeholder?: string;
  defaultValue?: any;
  options?: Array<{ label: string; value: any }>;
  rules?: FormValidationRule[];
  disabled?: boolean;
  tooltip?: string;
  dependencies?: string[]; // other field names this field depends on
}

export interface FormConfig {
  fields: FormFieldConfig[];
  layout?: 'horizontal' | 'vertical' | 'inline';
  submitText?: string;
  resetText?: string;
  showReset?: boolean;
  onSubmit?: (values: any) => void;
  onReset?: () => void;
  onChange?: (changedFields: any, allFields: any) => void;
}

// ========================================
// Export All Types
// ========================================

export type {
  // Re-export commonly used types for convenience
  YearNavigationContext as YearNavigation,
  SimulationYearData as YearData,
  YearOverYearKPI as KPIData,
  OfficeData as Office,
  SimulationConfig as Config,
  EnhancedKPICardProps as KPICardProps,
}; 