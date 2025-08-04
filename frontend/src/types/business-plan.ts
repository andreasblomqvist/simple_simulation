/**
 * Comprehensive Business Plan Data Structure
 * 
 * Integrates with the comprehensive business planning field system,
 * currency formatting, and hierarchical organization established in
 * business-planning-structure.ts and business-planning-fields.ts
 */

import { CurrencyCode } from '../utils/currency';
import { StandardRole, StandardLevel, BillableRole, NonBillableRole } from './office';
import { 
  BusinessPlanningFieldRegistry, 
  OfficeData, 
  MonthlyValues,
  BusinessPlanningField,
  FieldCategory,
  FieldLevel
} from './business-planning-structure';

// ==========================================
// BUSINESS PLAN METADATA & STATUS
// ==========================================

export type BusinessPlanStatus = 'draft' | 'under_review' | 'approved' | 'published' | 'archived';
export type BusinessPlanType = 'annual' | 'quarterly' | 'strategic' | 'budget';
export type ApprovalLevel = 'team_lead' | 'department_head' | 'c_level' | 'board';

/**
 * Core business plan metadata matching the overview table structure
 * from the user's image: Plan Name, Office, Year, Status, Progress, 
 * Target Revenue, Headcount, Official, Last Updated, Actions
 */
export interface BusinessPlanMetadata {
  id: string;
  planName: string; // Primary identifier from overview table
  description?: string;
  
  // Context & Scope (from overview table)
  office: string; // Office ID or name
  year: number; // Planning year
  planType: BusinessPlanType;
  
  // Status & Progress (from overview table)
  status: BusinessPlanStatus; // Draft, Under Review, Approved, etc.
  progress: number; // 0-100 percentage completion
  
  // Key Metrics (from overview table)
  targetRevenue: number; // Target Revenue column
  headcount: number; // Headcount column
  isOfficial: boolean; // Official column - whether this is the official plan
  
  // Timestamps (from overview table)
  createdAt: Date;
  lastUpdated: Date; // Last Updated column
  publishedAt?: Date;
  
  // Configuration
  currencyCode: CurrencyCode;
  
  // Approval Workflow
  approvals: BusinessPlanApproval[];
  requiredApprovalLevel: ApprovalLevel;
  
  // Collaboration
  createdBy: string; // User ID
  lastModifiedBy: string; // User ID
  collaborators: string[]; // User IDs with edit access
  
  // Versioning
  version: number;
  parentPlanId?: string; // For revisions
  
  // Integration
  linkedScenarioIds: string[]; // Scenarios this plan is based on
  
  // Tags & Classification
  tags: string[];
  category?: string;
}

export interface BusinessPlanApproval {
  id: string;
  approverUserId: string;
  approverName: string;
  level: ApprovalLevel;
  status: 'pending' | 'approved' | 'rejected';
  approvedAt?: Date;
  comments?: string;
}

// Re-export MonthlyValues from business-planning-structure for consistency
export type MonthlyData = MonthlyValues;
export const MONTH_NAMES = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'] as const;
export type MonthName = typeof MONTH_NAMES[number];

/**
 * Creates an empty MonthlyData object with all months set to 0
 */
export function createEmptyMonthlyData(): MonthlyData {
  return {
    jan: 0, feb: 0, mar: 0, apr: 0, may: 0, jun: 0,
    jul: 0, aug: 0, sep: 0, oct: 0, nov: 0, dec: 0,
    total: 0
  };
}

/**
 * Calculates the total for a MonthlyData object
 */
export function calculateMonthlyTotal(data: Omit<MonthlyData, 'total'>): MonthlyData {
  const total = data.jan + data.feb + data.mar + data.apr + data.may + data.jun +
                data.jul + data.aug + data.sep + data.oct + data.nov + data.dec;
  return { ...data, total };
}

// ==========================================
// BUSINESS PLAN DATA STRUCTURE
// ==========================================

/**
 * Complete business plan data structure integrating with
 * the comprehensive field system and currency formatting
 */
export interface BusinessPlanData {
  metadata: BusinessPlanMetadata;
  
  // Core Planning Data (integrated with business-planning-structure.ts)
  officeData: OfficeData;
  
  // Field Registry for validation and calculations (uses comprehensive field system)
  fieldRegistry: BusinessPlanningFieldRegistry;
  
  // Comprehensive section data organized by categories
  sectionData: {
    revenue: BusinessPlanSection;
    workforce: BusinessPlanSection;
    compensation: BusinessPlanSection;
    expenses: BusinessPlanSection;
    summary: BusinessPlanSection;
  };
  
  // Calculation Cache with currency-aware formatting
  calculationCache: {
    lastCalculated: Date;
    kpis: Record<string, FormattedValue>;
    sectionSummaries: Record<string, FormattedMonthlyValues>;
    validationResults: BusinessPlanValidation;
  };
  
  // Scenario Integration
  baselineScenario?: {
    scenarioId: string;
    scenarioName: string;
    importedAt: Date;
    fieldsImported: string[]; // Which fields were imported from scenario
  };
  
  // Comments & Notes
  comments: BusinessPlanComment[];
  
  // Change History
  changeHistory: BusinessPlanChange[];
}

/**
 * Section data structure for hierarchical business planning
 */
export interface BusinessPlanSection {
  id: string;
  name: string;
  category: FieldCategory;
  order: number;
  
  // Field organization
  officeLevelFields: Map<string, FormattedValue>;
  roleLevelFields: Map<StandardRole, Map<StandardLevel, Map<string, FormattedValue>>>;
  
  // Section summaries
  monthlySummary: FormattedMonthlyValues;
  yearlyTotal: FormattedValue;
  
  // Section metadata
  lastUpdated: Date;
  completeness: number; // 0-100 percentage
  hasErrors: boolean;
}

/**
 * Currency-aware formatted value
 */
export interface FormattedValue {
  raw: number; // Raw numeric value
  formatted: string; // Formatted display value with currency/units
  currencyCode?: CurrencyCode;
  valueType: 'currency' | 'percentage' | 'count' | 'fte' | 'hours' | 'rate' | 'ratio' | 'days' | 'months';
  precision: number;
}

/**
 * Currency-aware formatted monthly values
 */
export interface FormattedMonthlyValues {
  raw: MonthlyValues; // Raw numeric values
  formatted: {
    jan: string; feb: string; mar: string; apr: string;
    may: string; jun: string; jul: string; aug: string;
    sep: string; oct: string; nov: string; dec: string;
    total: string;
  };
  currencyCode?: CurrencyCode;
  valueType: 'currency' | 'percentage' | 'count' | 'fte' | 'hours' | 'rate' | 'ratio' | 'days' | 'months';
  precision: number;
}

/**
 * Legacy business plan entry structure for backward compatibility
 * @deprecated Use BusinessPlanData with comprehensive field system instead
 */
export interface BusinessPlanEntry {
  // Identification
  role: StandardRole;
  level: StandardLevel;
  
  // Input Fields - Core Business Data
  recruitment: MonthlyData;        // Number of new hires per month
  churn: MonthlyData;             // Number of departures per month
  salary: MonthlyData;            // Average monthly salary cost per FTE
  
  // Input Fields - Revenue Data (Consultant role only)
  price?: MonthlyData;            // Hourly billing rate (Consultants only)
  utr?: MonthlyData;              // Utilization rate 0-1 (Consultants only)
  
  // Calculated Fields - Workforce Metrics
  opening_fte: MonthlyData;       // FTE at start of month
  closing_fte: MonthlyData;       // FTE at end of month
  average_fte: MonthlyData;       // Average FTE during month
  net_recruitment: MonthlyData;   // recruitment - churn
  
  // Calculated Fields - Financial Metrics
  revenue: MonthlyData;           // Monthly revenue (price * utr * avg_fte * hours)
  total_salary_cost: MonthlyData; // salary * average_fte
  contribution: MonthlyData;      // revenue - total_salary_cost
  
  // Calculated Fields - Performance Metrics
  cumulative_fte: MonthlyData;    // Running total of FTE changes
  recruitment_rate: MonthlyData;  // recruitment / opening_fte
  churn_rate: MonthlyData;        // churn / opening_fte
  
  // Meta Information
  is_billable: boolean;           // Whether this role generates revenue
  is_leveled: boolean;            // Whether this role has hierarchical levels
  last_modified: string;          // ISO timestamp of last update
}

/**
 * Legacy aggregated business plan data for backward compatibility
 * @deprecated Use BusinessPlanData with comprehensive field system instead
 */
export interface OfficeBusinesPlan {
  // Meta Information
  id: string;
  office_id: string;
  office_name: string;
  year: number;
  status: BusinessPlanStatus;
  
  // Business Plan Entries
  entries: BusinessPlanEntry[];   // All role/level combinations
  
  // Office-Level Aggregations
  totals: {
    workforce: {
      total_recruitment: MonthlyData;
      total_churn: MonthlyData;
      net_recruitment: MonthlyData;
      opening_fte: MonthlyData;
      closing_fte: MonthlyData;
      average_fte: MonthlyData;
    };
    
    financial: {
      total_revenue: MonthlyData;
      total_salary_cost: MonthlyData;
      total_contribution: MonthlyData;
      contribution_margin: MonthlyData; // contribution / revenue
    };
    
    performance: {
      overall_recruitment_rate: MonthlyData;
      overall_churn_rate: MonthlyData;
      revenue_per_fte: MonthlyData;
      cost_per_fte: MonthlyData;
    };
  };
  
  // Role-Level Aggregations
  role_summaries: {
    [role in StandardRole]?: {
      total_fte: MonthlyData;
      total_recruitment: MonthlyData;
      total_churn: MonthlyData;
      total_revenue: MonthlyData;
      total_salary_cost: MonthlyData;
      level_breakdown: {
        [level: string]: {
          fte: MonthlyData;
          recruitment: MonthlyData;
          churn: MonthlyData;
          revenue: MonthlyData;
          salary_cost: MonthlyData;
        };
      };
    };
  };
  
  // Timestamps
  created_at: string;
  updated_at: string;
  approved_at?: string;
  approved_by?: string;
}

// ==========================================
// VALIDATION & QUALITY ASSURANCE
// ==========================================

export interface BusinessPlanValidation {
  isValid: boolean;
  errors: ValidationIssue[];
  warnings: ValidationIssue[];
  suggestions: ValidationIssue[];
  completeness: {
    requiredFieldsCompleted: number;
    totalRequiredFields: number;
    percentage: number;
  };
  consistency: {
    formulaValidation: boolean;
    crossReferenceValidation: boolean;
    totalValidation: boolean;
  };
}

export interface ValidationIssue {
  id: string;
  severity: 'error' | 'warning' | 'suggestion';
  category: 'data_integrity' | 'business_logic' | 'completeness' | 'consistency';
  fieldId?: string;
  role?: StandardRole;
  level?: StandardLevel;
  month?: number;
  message: string;
  suggestion?: string;
  affectedValues?: string[];
}

// ==========================================
// COLLABORATION & CHANGE TRACKING
// ==========================================

export interface BusinessPlanComment {
  id: string;
  authorUserId: string;
  authorName: string;
  createdAt: Date;
  updatedAt?: Date;
  
  // Context
  fieldId?: string;
  role?: StandardRole;
  level?: StandardLevel;
  month?: number;
  
  // Content
  content: string;
  type: 'general' | 'question' | 'suggestion' | 'approval_note';
  
  // Thread
  parentCommentId?: string;
  replies: BusinessPlanComment[];
  
  // Status
  isResolved: boolean;
  resolvedBy?: string;
  resolvedAt?: Date;
}

export interface BusinessPlanChange {
  id: string;
  timestamp: Date;
  userId: string;
  userName: string;
  
  // Change Details
  changeType: 'field_update' | 'approval' | 'status_change' | 'metadata_update' | 'bulk_import';
  
  // Field-specific changes
  fieldId?: string;
  role?: StandardRole;
  level?: StandardLevel;
  month?: number;
  
  // Values
  oldValue?: FormattedValue;
  newValue?: FormattedValue;
  
  // Context
  description: string;
  affectedFields?: string[];
  
  // Approval changes
  approvalChange?: {
    fromStatus: BusinessPlanStatus;
    toStatus: BusinessPlanStatus;
    approvalLevel: ApprovalLevel;
  };
}

// ==========================================
// EXPORT & REPORTING
// ==========================================

export interface BusinessPlanExportOptions {
  format: 'excel' | 'pdf' | 'csv' | 'json';
  includeComments: boolean;
  includeChangeHistory: boolean;
  includeValidation: boolean;
  
  // Data selection
  sections?: string[]; // If specified, only export these sections
  roles?: StandardRole[]; // If specified, only export these roles
  months?: number[]; // If specified, only export these months
  
  // Formatting (integrates with currency system)
  currencyCode?: CurrencyCode;
  locale?: string;
  precision?: number;
  useCompactNotation?: boolean; // For large numbers (1.2M vs 1,200,000)
  
  // Template
  templateId?: string;
  customTemplate?: ExportTemplate;
}

export interface ExportTemplate {
  id: string;
  name: string;
  description: string;
  
  // Layout
  layout: 'detailed' | 'summary' | 'executive' | 'financial';
  sections: ExportSection[];
  
  // Styling
  branding?: {
    logo?: string;
    colors?: Record<string, string>;
    fonts?: Record<string, string>;
  };
}

export interface ExportSection {
  id: string;
  title: string;
  type: 'table' | 'chart' | 'kpi_cards' | 'text' | 'summary';
  
  // Data selection
  fields?: string[];
  roles?: StandardRole[];
  calculations?: string[];
  
  // Display options
  groupBy?: 'role' | 'level' | 'month' | 'category';
  sortBy?: string;
  showTotals?: boolean;
  showPercentages?: boolean;
  
  // Chart options (if type === 'chart')
  chartType?: 'bar' | 'line' | 'pie' | 'area' | 'waterfall';
  chartConfig?: Record<string, any>;
}

/**
 * Business plan template for creating new plans
 * @deprecated Legacy template structure
 */
export interface BusinessPlanTemplate {
  id: string;
  name: string;
  description: string;
  source_office_id?: string;    // If copied from another office
  source_year?: number;         // If copied from another year
  template_data: {
    default_entries: Partial<BusinessPlanEntry>[];
    economic_assumptions: {
      inflation_rate: number;
      growth_rate: number;
      market_multiplier: number;
    };
    role_defaults: {
      [role in StandardRole]?: {
        [level: string]: {
          default_salary: number;
          default_price?: number;
          default_utr?: number;
          recruitment_seasonality?: number[]; // 12 month multipliers
          churn_seasonality?: number[];       // 12 month multipliers
        };
      };
    };
  };
  created_at: string;
  created_by: string;
}

// ==========================================
// INTEGRATION & IMPORT/EXPORT
// ==========================================

export interface BusinessPlanImportData {
  source: 'scenario' | 'previous_plan' | 'excel' | 'csv' | 'external_system';
  sourceId?: string;
  sourceName?: string;
  importedAt: Date;
  importedBy: string;
  
  // Field mapping (integrates with field registry)
  fieldMappings: Record<string, string>; // source field -> target field
  roleMappings: Record<string, StandardRole>; // source role -> target role
  
  // Import options
  overwriteExisting: boolean;
  validateBeforeImport: boolean;
  
  // Results
  importResults: {
    totalRecords: number;
    successCount: number;
    errorCount: number;
    warningCount: number;
    errors: ValidationIssue[];
    warnings: ValidationIssue[];
  };
}

/**
 * Legacy business plan comparison structure
 * @deprecated Use BusinessPlanData comparison methods instead
 */
export interface BusinessPlanComparison {
  comparison_id: string;
  plans: {
    baseline: OfficeBusinesPlan;
    comparison: OfficeBusinesPlan;
  };
  
  differences: {
    workforce: {
      fte_variance: MonthlyData;         // comparison - baseline
      recruitment_variance: MonthlyData;
      churn_variance: MonthlyData;
    };
    
    financial: {
      revenue_variance: MonthlyData;
      cost_variance: MonthlyData;
      contribution_variance: MonthlyData;
      margin_variance: MonthlyData;
    };
    
    performance: {
      recruitment_rate_variance: MonthlyData;
      churn_rate_variance: MonthlyData;
      revenue_per_fte_variance: MonthlyData;
    };
  };
  
  summary: {
    total_fte_change: number;
    total_revenue_change: number;
    total_cost_change: number;
    margin_impact: number;
    key_variances: string[];          // Narrative summary of major differences
  };
  
  created_at: string;
}

// ==========================================
// API INTERFACES
// ==========================================

export interface CreateBusinessPlanRequest {
  planName: string;
  description?: string;
  office: string;
  year: number;
  planType: BusinessPlanType;
  currencyCode: CurrencyCode;
  
  // Optional initialization
  templateId?: string;
  baselineScenarioId?: string;
  copyFromPlanId?: string;
  
  // Collaboration
  collaborators?: string[];
  requiredApprovalLevel?: ApprovalLevel;
}

export interface UpdateBusinessPlanRequest {
  planName?: string;
  description?: string;
  status?: BusinessPlanStatus;
  targetRevenue?: number;
  headcount?: number;
  
  // Field updates (currency-aware)
  fieldUpdates?: Array<{
    fieldId: string;
    role?: StandardRole;
    level?: StandardLevel;
    month?: number;
    value: number | FormattedValue;
  }>;
  
  // Bulk updates
  bulkUpdates?: {
    operation: 'multiply' | 'add' | 'set';
    fields: string[];
    roles?: StandardRole[];
    levels?: StandardLevel[];
    months?: number[];
    value: number;
  };
}

export interface BusinessPlanResponse {
  plan: BusinessPlanData;
  permissions: {
    canEdit: boolean;
    canApprove: boolean;
    canPublish: boolean;
    canDelete: boolean;
    requiredApprovalLevel?: ApprovalLevel;
  };
}

export interface BusinessPlanListResponse {
  plans: BusinessPlanMetadata[];
  pagination: {
    page: number;
    pageSize: number;
    totalCount: number;
    totalPages: number;
  };
  filters: {
    offices: string[];
    years: number[];
    statuses: BusinessPlanStatus[];
    planTypes: BusinessPlanType[];
  };
}

// ==========================================
// UTILITY TYPES
// ==========================================

export type BusinessPlanField = keyof BusinessPlanData['officeData']['officeLevelFields'] | 
                               keyof BusinessPlanData['officeData']['roles'];

export type BusinessPlanQueryFilter = {
  office?: string;
  year?: number;
  status?: BusinessPlanStatus;
  planType?: BusinessPlanType;
  createdBy?: string;
  tag?: string;
  search?: string; // Free text search across plan name and description
};

export type BusinessPlanSortOption = 
  | 'planName'
  | 'year'
  | 'status'
  | 'progress'
  | 'lastUpdated'
  | 'targetRevenue'
  | 'headcount';

/**
 * Legacy field metadata for backward compatibility
 * @deprecated Use BusinessPlanningFieldRegistry from business-planning-structure.ts instead
 */
export interface BusinessPlanFieldMetadata {
  field_name: keyof BusinessPlanEntry;
  display_name: string;
  description: string;
  field_type: 'input' | 'calculated';
  data_type: 'number' | 'percentage' | 'currency';
  is_required: boolean;
  applies_to_roles: StandardRole[];
  applies_to_billable_only: boolean;
  validation_rules: {
    min_value?: number;
    max_value?: number;
    decimal_places?: number;
    required_if?: string;  // Field dependencies
  };
  formatting: {
    prefix?: string;       // e.g., "$", "£"
    suffix?: string;       // e.g., "%", "hrs"
    thousands_separator: boolean;
    decimal_places: number;
  };
  help_text: string;
  example_values: number[];
}

// ==========================================
// FACTORY FUNCTIONS
// ==========================================

/**
 * Create an empty business plan with the comprehensive field system
 * and proper currency integration
 */
export function createEmptyBusinessPlan(
  request: CreateBusinessPlanRequest,
  userId: string,
  userName: string
): BusinessPlanData {
  const now = new Date();
  const emptyMonthlyValues: MonthlyValues = {
    jan: 0, feb: 0, mar: 0, apr: 0, may: 0, jun: 0,
    jul: 0, aug: 0, sep: 0, oct: 0, nov: 0, dec: 0, total: 0
  };
  
  return {
    metadata: {
      id: `bp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      planName: request.planName,
      description: request.description,
      office: request.office,
      year: request.year,
      planType: request.planType,
      status: 'draft',
      progress: 0,
      targetRevenue: 0,
      headcount: 0,
      isOfficial: false,
      createdAt: now,
      lastUpdated: now,
      currencyCode: request.currencyCode,
      approvals: [],
      requiredApprovalLevel: request.requiredApprovalLevel || 'department_head',
      createdBy: userId,
      lastModifiedBy: userId,
      collaborators: request.collaborators || [],
      version: 1,
      linkedScenarioIds: request.baselineScenarioId ? [request.baselineScenarioId] : [],
      tags: [],
    },
    officeData: {
      officeId: request.office,
      year: request.year,
      roles: new Map(),
      officeLevelFields: new Map(),
      sectionSummaries: new Map(),
      kpis: new Map(),
      lastCalculated: now,
      isDirty: false
    },
    fieldRegistry: new BusinessPlanningFieldRegistry(), // Will be populated with comprehensive fields
    sectionData: {
      revenue: {
        id: 'revenue',
        name: 'Revenue Planning',
        category: 'revenue',
        order: 1,
        officeLevelFields: new Map(),
        roleLevelFields: new Map(),
        monthlySummary: {
          raw: emptyMonthlyValues,
          formatted: {
            jan: '€0', feb: '€0', mar: '€0', apr: '€0', may: '€0', jun: '€0',
            jul: '€0', aug: '€0', sep: '€0', oct: '€0', nov: '€0', dec: '€0', total: '€0'
          },
          currencyCode: request.currencyCode,
          valueType: 'currency',
          precision: 0
        },
        yearlyTotal: {
          raw: 0,
          formatted: '€0',
          currencyCode: request.currencyCode,
          valueType: 'currency',
          precision: 0
        },
        lastUpdated: now,
        completeness: 0,
        hasErrors: false
      },
      workforce: {
        id: 'workforce',
        name: 'Workforce Planning',
        category: 'workforce',
        order: 2,
        officeLevelFields: new Map(),
        roleLevelFields: new Map(),
        monthlySummary: {
          raw: emptyMonthlyValues,
          formatted: {
            jan: '0', feb: '0', mar: '0', apr: '0', may: '0', jun: '0',
            jul: '0', aug: '0', sep: '0', oct: '0', nov: '0', dec: '0', total: '0'
          },
          valueType: 'count',
          precision: 0
        },
        yearlyTotal: {
          raw: 0,
          formatted: '0',
          valueType: 'count',
          precision: 0
        },
        lastUpdated: now,
        completeness: 0,
        hasErrors: false
      },
      compensation: {
        id: 'compensation',
        name: 'Compensation & Benefits',
        category: 'compensation',
        order: 3,
        officeLevelFields: new Map(),
        roleLevelFields: new Map(),
        monthlySummary: {
          raw: emptyMonthlyValues,
          formatted: {
            jan: '€0', feb: '€0', mar: '€0', apr: '€0', may: '€0', jun: '€0',
            jul: '€0', aug: '€0', sep: '€0', oct: '€0', nov: '€0', dec: '€0', total: '€0'
          },
          currencyCode: request.currencyCode,
          valueType: 'currency',
          precision: 0
        },
        yearlyTotal: {
          raw: 0,
          formatted: '€0',
          currencyCode: request.currencyCode,
          valueType: 'currency',
          precision: 0
        },
        lastUpdated: now,
        completeness: 0,
        hasErrors: false
      },
      expenses: {
        id: 'expenses',
        name: 'Operating Expenses',
        category: 'expenses',
        order: 4,
        officeLevelFields: new Map(),
        roleLevelFields: new Map(),
        monthlySummary: {
          raw: emptyMonthlyValues,
          formatted: {
            jan: '€0', feb: '€0', mar: '€0', apr: '€0', may: '€0', jun: '€0',
            jul: '€0', aug: '€0', sep: '€0', oct: '€0', nov: '€0', dec: '€0', total: '€0'
          },
          currencyCode: request.currencyCode,
          valueType: 'currency',
          precision: 0
        },
        yearlyTotal: {
          raw: 0,
          formatted: '€0',
          currencyCode: request.currencyCode,
          valueType: 'currency',
          precision: 0
        },
        lastUpdated: now,
        completeness: 0,
        hasErrors: false
      },
      summary: {
        id: 'summary',
        name: 'Financial Summary & KPIs',
        category: 'summary',
        order: 5,
        officeLevelFields: new Map(),
        roleLevelFields: new Map(),
        monthlySummary: {
          raw: emptyMonthlyValues,
          formatted: {
            jan: '€0', feb: '€0', mar: '€0', apr: '€0', may: '€0', jun: '€0',
            jul: '€0', aug: '€0', sep: '€0', oct: '€0', nov: '€0', dec: '€0', total: '€0'
          },
          currencyCode: request.currencyCode,
          valueType: 'currency',
          precision: 0
        },
        yearlyTotal: {
          raw: 0,
          formatted: '€0',
          currencyCode: request.currencyCode,
          valueType: 'currency',
          precision: 0
        },
        lastUpdated: now,
        completeness: 0,
        hasErrors: false
      }
    },
    calculationCache: {
      lastCalculated: now,
      kpis: {},
      sectionSummaries: {},
      validationResults: {
        isValid: true,
        errors: [],
        warnings: [],
        suggestions: [],
        completeness: {
          requiredFieldsCompleted: 0,
          totalRequiredFields: 0,
          percentage: 0
        },
        consistency: {
          formulaValidation: true,
          crossReferenceValidation: true,
          totalValidation: true
        }
      }
    },
    comments: [],
    changeHistory: [{
      id: `change_${Date.now()}`,
      timestamp: now,
      userId,
      userName,
      changeType: 'metadata_update',
      description: 'Business plan created',
      newValue: {
        raw: 0,
        formatted: 'draft',
        valueType: 'count',
        precision: 0
      }
    }]
  };
}

// ==========================================
// LEGACY SUPPORT & STORE INTERFACES
// ==========================================

/**
 * Legacy business plan calculation parameters
 * @deprecated Use BusinessPlanningFieldRegistry for validation rules instead
 */
export interface BusinessPlanCalculationParams {
  // Economic Parameters
  working_hours_per_month: number;    // Default: 160
  employment_cost_multiplier: number; // Default: 1.3 (30% overhead)
  
  // FTE Calculation Settings
  opening_fte_source: 'previous_month' | 'baseline' | 'manual';
  seasonality_adjustments: boolean;
  
  // Revenue Calculation Settings
  revenue_recognition: 'monthly' | 'quarterly';
  price_escalation_rate: number;      // Annual price increase %
  
  // Validation Rules
  max_monthly_churn_rate: number;     // Maximum allowable churn rate
  max_monthly_recruitment_rate: number; // Maximum allowable recruitment rate
  min_utilization_rate: number;      // Minimum UTR for consultants
  max_utilization_rate: number;      // Maximum UTR for consultants
}

/**
 * Enhanced Zustand store state for comprehensive business planning
 */
export interface BusinessPlanStoreState {
  // Current Data (enhanced with comprehensive system)
  current_plan: BusinessPlanData | null;
  current_validation: BusinessPlanValidation | null;
  field_registry: BusinessPlanningFieldRegistry;
  
  // Legacy support
  legacy_plan: OfficeBusinesPlan | null;
  calculation_params: BusinessPlanCalculationParams;
  
  // All Plans
  plans: BusinessPlanMetadata[];
  templates: BusinessPlanTemplate[];
  
  // UI State
  loading: boolean;
  error: string | null;
  selected_office_id: string | null;
  selected_year: number;
  active_comparison: BusinessPlanComparison | null;
  
  // Enhanced View Options
  view_mode: 'monthly' | 'quarterly' | 'annual';
  show_calculated_fields: boolean;
  group_by_role: boolean;
  currency_code: CurrencyCode;
  
  // Enhanced Actions
  loadBusinessPlan: (office_id: string, year: number) => Promise<void>;
  createBusinessPlan: (request: CreateBusinessPlanRequest) => Promise<BusinessPlanData>;
  updateBusinessPlan: (plan_id: string, updates: UpdateBusinessPlanRequest) => Promise<void>;
  validateBusinessPlan: (plan: BusinessPlanData) => Promise<BusinessPlanValidation>;
  
  // Legacy Actions (for backward compatibility)
  createLegacyBusinessPlan: (request: { office_id: string; year: number }) => Promise<OfficeBusinesPlan>;
  updateBusinessPlanEntry: (plan_id: string, entry: BusinessPlanEntry) => Promise<void>;
  calculatePlanTotals: (plan: OfficeBusinesPlan) => OfficeBusinesPlan;
  
  // Template Management
  loadTemplates: () => Promise<void>;
  createTemplate: (template: Omit<BusinessPlanTemplate, 'id' | 'created_at'>) => Promise<void>;
  
  // Comparison
  comparePlans: (baseline_id: string, comparison_id: string) => Promise<BusinessPlanComparison>;
  
  // Utility
  setSelectedOffice: (office_id: string) => void;
  setSelectedYear: (year: number) => void;
  setCurrencyCode: (currency: CurrencyCode) => void;
  clearError: () => void;
}

// ==========================================
// UTILITY CONSTANTS
// ==========================================

/**
 * Default calculation parameters (legacy support)
 */
export const DEFAULT_CALCULATION_PARAMS: BusinessPlanCalculationParams = {
  working_hours_per_month: 160,
  employment_cost_multiplier: 1.3,
  opening_fte_source: 'previous_month',
  seasonality_adjustments: true,
  revenue_recognition: 'monthly',
  price_escalation_rate: 0.03,  // 3% annual
  max_monthly_churn_rate: 0.25,  // 25%
  max_monthly_recruitment_rate: 0.50, // 50%
  min_utilization_rate: 0.60,    // 60%
  max_utilization_rate: 0.95     // 95%
};

/**
 * Field metadata definitions for all business plan fields
 */
export const BUSINESS_PLAN_FIELD_METADATA: Record<string, BusinessPlanFieldMetadata> = {
  recruitment: {
    field_name: 'recruitment',
    display_name: 'Monthly Recruitment',
    description: 'Number of new hires planned for each month',
    field_type: 'input',
    data_type: 'number',
    is_required: true,
    applies_to_roles: ['Consultant', 'Sales', 'Recruitment', 'Operations'],
    applies_to_billable_only: false,
    validation_rules: {
      min_value: 0,
      decimal_places: 1
    },
    formatting: {
      thousands_separator: false,
      decimal_places: 1
    },
    help_text: 'Enter the number of people you plan to hire each month. Can include fractional FTE.',
    example_values: [2, 5, 1.5, 0]
  },
  
  churn: {
    field_name: 'churn',
    display_name: 'Monthly Churn',
    description: 'Number of departures planned for each month',
    field_type: 'input',
    data_type: 'number',
    is_required: true,
    applies_to_roles: ['Consultant', 'Sales', 'Recruitment', 'Operations'],
    applies_to_billable_only: false,
    validation_rules: {
      min_value: 0,
      decimal_places: 1
    },
    formatting: {
      thousands_separator: false,
      decimal_places: 1
    },
    help_text: 'Enter the number of people expected to leave each month. Include resignations, terminations, and transfers.',
    example_values: [1, 2, 0.5, 0]
  },
  
  salary: {
    field_name: 'salary',
    display_name: 'Average Monthly Salary',
    description: 'Average salary cost per FTE per month',
    field_type: 'input',
    data_type: 'currency',
    is_required: true,
    applies_to_roles: ['Consultant', 'Sales', 'Recruitment', 'Operations'],
    applies_to_billable_only: false,
    validation_rules: {
      min_value: 1000,
      max_value: 50000,
      decimal_places: 0
    },
    formatting: {
      prefix: 'NOK ',
      thousands_separator: true,
      decimal_places: 0
    },
    help_text: 'Average monthly salary including benefits and overhead costs.',
    example_values: [45000, 55000, 65000, 75000]
  },
  
  price: {
    field_name: 'price',
    display_name: 'Hourly Rate',
    description: 'Client billing rate per hour',
    field_type: 'input',
    data_type: 'currency',
    is_required: false,
    applies_to_roles: ['Consultant'],
    applies_to_billable_only: true,
    validation_rules: {
      min_value: 500,
      max_value: 3000,
      decimal_places: 0,
      required_if: 'role === Consultant'
    },
    formatting: {
      prefix: 'NOK ',
      thousands_separator: true,
      decimal_places: 0
    },
    help_text: 'Hourly billing rate charged to clients. Only applies to billable roles.',
    example_values: [1200, 1500, 1800, 2200]
  },
  
  utr: {
    field_name: 'utr',
    display_name: 'Utilization Rate',
    description: 'Billable time as percentage of total time',
    field_type: 'input',
    data_type: 'percentage',
    is_required: false,
    applies_to_roles: ['Consultant'],
    applies_to_billable_only: true,
    validation_rules: {
      min_value: 0.4,
      max_value: 0.95,
      decimal_places: 2,
      required_if: 'role === Consultant'
    },
    formatting: {
      suffix: '%',
      thousands_separator: false,
      decimal_places: 1
    },
    help_text: 'Percentage of working time that is billable to clients. Typical range: 60-85%.',
    example_values: [0.75, 0.80, 0.85, 0.70]
  }
};

/**
 * Type exports are defined inline above
 */