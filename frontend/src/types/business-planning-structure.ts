/**
 * Sophisticated Business Planning Data Structure & Field Applicability System
 * 
 * This system provides:
 * 1. Role-specific field applicability with metadata
 * 2. Hierarchical UI structure with proper parent-child nesting
 * 3. Clean aggregation strategy for office-level summaries
 * 4. Eliminates frontend complexity through declarative configuration
 */

import { StandardRole, StandardLevel } from './office';
import { DollarSign, Users, TrendingUp, Clock, UserPlus, UserMinus, Calculator, Building2, Target, ArrowUpRight } from 'lucide-react';
import { CurrencyFormatter, type CurrencyCode as UtilsCurrencyCode } from '../utils/currency';

// ==========================================
// CORE TYPE DEFINITIONS
// ==========================================

export type FieldType = 'input' | 'calculated' | 'display';
export type FieldLevel = 'office' | 'role' | 'role_level';
export type FieldCategory = 'revenue' | 'workforce' | 'compensation' | 'expenses' | 'summary';
export type ValueType = 'currency' | 'percentage' | 'count' | 'fte' | 'hours' | 'rate' | 'ratio' | 'days' | 'months';
export type CurrencyCode = UtilsCurrencyCode;

export interface FieldMetadata {
  id: string;
  label: string;
  icon: any; // Lucide icon component
  type: FieldType;
  level: FieldLevel;
  category: FieldCategory;
  color: string;
  bgColor: string;
  description?: string;
  
  // Value type and formatting
  valueType: ValueType;
  currencyCode?: CurrencyCode;
  precision?: number; // Decimal places for display
  suffix?: string; // Unit suffix (e.g., '/hour', '%', 'people')
  prefix?: string; // Unit prefix (e.g., '€', '$', '#')
  
  // Field constraints
  min?: number;
  max?: number;
  step?: number;
  
  // Role applicability - key innovation for clean separation
  applicableRoles?: StandardRole[];
  excludedRoles?: StandardRole[];
  
  // Level applicability
  applicableLevels?: StandardLevel[];
  excludedLevels?: StandardLevel[];
  
  // Calculation metadata
  formula?: string;
  dependencies?: string[];
  
  // UI behavior
  isEditable?: boolean;
  showInSummary?: boolean;
  aggregateMethod?: 'sum' | 'average' | 'weighted_average' | 'none';
  
  // Business rules
  contributesToRevenue?: boolean;
  contributesToCosts?: boolean;
  isKPI?: boolean;
}

export interface BusinessPlanningField {
  metadata: FieldMetadata;
  
  // Methods for role/level checking - encapsulated logic
  isApplicableToRole(role: StandardRole): boolean;
  isApplicableToLevel(level: StandardLevel): boolean;
  isApplicableToRoleLevel(role: StandardRole, level: StandardLevel): boolean;
  
  // Value calculation methods
  calculateValue?(inputs: Record<string, number>): number;
  validateValue?(value: number): boolean;
  formatValue?(value: number): string;
  
  // Value type utilities
  getDisplayValue?(value: number): string;
  parseInputValue?(input: string): number | null;
  getValidationMessage?(value: number): string | null;
}

// ==========================================
// HIERARCHICAL STRUCTURE DEFINITIONS
// ==========================================

export interface BusinessPlanningSection {
  id: string;
  name: string;
  description: string;
  icon: any;
  color: string;
  order: number;
  
  // Hierarchical organization
  subsections: BusinessPlanningSubsection[];
  
  // Aggregation behavior
  aggregatesToOfficeLevel: boolean;
  summaryFields: string[]; // Field IDs to show in office summary
}

export interface BusinessPlanningSubsection {
  id: string;
  name: string;
  description: string;
  order: number;
  
  // Field organization
  fields: string[]; // Field IDs in this subsection
  
  // Role organization - controls which roles appear
  roleOrganization: 'all' | 'billable_only' | 'non_billable_only' | 'specific';
  specificRoles?: StandardRole[];
  
  // Level organization
  levelOrganization: 'all' | 'leveled_only' | 'flat_only' | 'specific';
  specificLevels?: StandardLevel[];
  
  // Display behavior
  isCollapsible: boolean;
  defaultExpanded: boolean;
  showRoleSummaries: boolean;
}

// ==========================================
// DATA VALUE STRUCTURES
// ==========================================

export interface MonthlyValues {
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

export interface FieldValue {
  fieldId: string;
  values: MonthlyValues;
  isCalculated: boolean;
  lastUpdated: Date;
  source?: 'user_input' | 'calculation' | 'import';
}

export interface RoleLevelData {
  role: StandardRole;
  level: StandardLevel;
  fields: Map<string, FieldValue>;
  
  // Metadata
  baselineFte: number;
  isActive: boolean;
}

export interface RoleData {
  role: StandardRole;
  levels: Map<StandardLevel, RoleLevelData>;
  
  // Role-level aggregations
  aggregatedFields: Map<string, FieldValue>;
  
  // Metadata
  totalFte: number;
  isBillable: boolean;
  hasLevels: boolean;
}

export interface OfficeData {
  officeId: string;
  year: number;
  
  // Hierarchical data organization
  roles: Map<StandardRole, RoleData>;
  officeLevelFields: Map<string, FieldValue>;
  
  // Calculated summaries
  sectionSummaries: Map<string, FieldValue>; // Section ID -> aggregated values
  kpis: Map<string, number>;
  
  // Metadata
  lastCalculated: Date;
  isDirty: boolean;
}

// ==========================================
// FIELD REGISTRY & BUSINESS RULES
// ==========================================

export class BusinessPlanningFieldRegistry {
  private fields = new Map<string, BusinessPlanningField>();
  private sections = new Map<string, BusinessPlanningSection>();
  
  // Register a field with full metadata and business rules
  registerField(field: BusinessPlanningField): void {
    this.fields.set(field.metadata.id, field);
  }
  
  // Register a section with hierarchical structure
  registerSection(section: BusinessPlanningSection): void {
    this.sections.set(section.id, section);
  }
  
  // Query methods for clean frontend usage
  getField(fieldId: string): BusinessPlanningField | undefined {
    return this.fields.get(fieldId);
  }
  
  getApplicableFieldsForRole(role: StandardRole): BusinessPlanningField[] {
    return Array.from(this.fields.values()).filter(field => 
      field.isApplicableToRole(role)
    );
  }
  
  getApplicableFieldsForRoleLevel(role: StandardRole, level: StandardLevel): BusinessPlanningField[] {
    return Array.from(this.fields.values()).filter(field => 
      field.isApplicableToRoleLevel(role, level)
    );
  }
  
  getFieldsByCategory(category: FieldCategory): BusinessPlanningField[] {
    return Array.from(this.fields.values()).filter(field => 
      field.metadata.category === category
    );
  }
  
  getFieldsByLevel(level: FieldLevel): BusinessPlanningField[] {
    return Array.from(this.fields.values()).filter(field => 
      field.metadata.level === level
    );
  }
  
  // Hierarchical structure queries
  getSections(): BusinessPlanningSection[] {
    return Array.from(this.sections.values()).sort((a, b) => a.order - b.order);
  }
  
  getSection(sectionId: string): BusinessPlanningSection | undefined {
    return this.sections.get(sectionId);
  }
  
  getFieldsInSection(sectionId: string): BusinessPlanningField[] {
    const section = this.sections.get(sectionId);
    if (!section) return [];
    
    const allFields: BusinessPlanningField[] = [];
    section.subsections.forEach(subsection => {
      subsection.fields.forEach(fieldId => {
        const field = this.fields.get(fieldId);
        if (field) allFields.push(field);
      });
    });
    
    return allFields;
  }
  
  // Business rule validation
  validateFieldForRole(fieldId: string, role: StandardRole): boolean {
    const field = this.fields.get(fieldId);
    return field ? field.isApplicableToRole(role) : false;
  }
  
  validateFieldForRoleLevel(fieldId: string, role: StandardRole, level: StandardLevel): boolean {
    const field = this.fields.get(fieldId);
    return field ? field.isApplicableToRoleLevel(role, level) : false;
  }
}

// ==========================================
// FIELD IMPLEMENTATION CLASS
// ==========================================

export class BusinessPlanningFieldImpl implements BusinessPlanningField {
  constructor(public metadata: FieldMetadata) {}
  
  isApplicableToRole(role: StandardRole): boolean {
    // Exclusion takes precedence
    if (this.metadata.excludedRoles?.includes(role)) {
      return false;
    }
    
    // If applicableRoles is specified, role must be in the list
    if (this.metadata.applicableRoles) {
      return this.metadata.applicableRoles.includes(role);
    }
    
    // Default: applicable to all roles if no restrictions
    return true;
  }
  
  isApplicableToLevel(level: StandardLevel): boolean {
    // Exclusion takes precedence
    if (this.metadata.excludedLevels?.includes(level)) {
      return false;
    }
    
    // If applicableLevels is specified, level must be in the list
    if (this.metadata.applicableLevels) {
      return this.metadata.applicableLevels.includes(level);
    }
    
    // Default: applicable to all levels if no restrictions
    return true;
  }
  
  isApplicableToRoleLevel(role: StandardRole, level: StandardLevel): boolean {
    return this.isApplicableToRole(role) && this.isApplicableToLevel(level);
  }
  
  calculateValue?(inputs: Record<string, number>): number {
    // Default implementation - can be overridden for specific fields
    if (this.metadata.type !== 'calculated' || !this.metadata.dependencies) {
      return 0;
    }
    
    // Basic sum calculation for most cases
    return this.metadata.dependencies.reduce((sum, dep) => sum + (inputs[dep] || 0), 0);
  }
  
  validateValue?(value: number): boolean {
    if (this.metadata.min !== undefined && value < this.metadata.min) {
      return false;
    }
    if (this.metadata.max !== undefined && value > this.metadata.max) {
      return false;
    }
    return true;
  }
  
  formatValue?(value: number): string {
    return this.getDisplayValue(value);
  }
  
  getDisplayValue(value: number): string {
    // Use advanced currency formatting for proper localization
    const currencyCode = this.metadata.currencyCode || 'EUR';
    const formatter = new CurrencyFormatter(currencyCode);
    
    // Apply value type specific formatting
    switch (this.metadata.valueType) {
      case 'currency':
        const precision = this.metadata.precision ?? 0; // Default to 0 decimals for currency
        return formatter.format(value, { 
          precision,
          showSymbol: true,
          compact: value >= 1000000 // Use compact format for large numbers
        });
        
      case 'percentage':
        const percentPrecision = this.metadata.precision ?? 1;
        const percentValue = value * 100; // Convert decimal to percentage
        return `${percentValue.toLocaleString('en-US', {
          minimumFractionDigits: percentPrecision,
          maximumFractionDigits: percentPrecision
        })}%`;
        
      case 'fte':
        const ftePrecision = this.metadata.precision ?? 1;
        return `${value.toLocaleString('en-US', {
          minimumFractionDigits: ftePrecision,
          maximumFractionDigits: ftePrecision
        })} FTE`;
        
      case 'hours':
        const hoursPrecision = this.metadata.precision ?? 0;
        return `${value.toLocaleString('en-US', {
          minimumFractionDigits: hoursPrecision,
          maximumFractionDigits: hoursPrecision
        })}h`;
        
      case 'rate':
        const ratePrecision = this.metadata.precision ?? 0;
        const rateFormatted = formatter.format(value, { 
          precision: ratePrecision,
          showSymbol: true
        });
        return `${rateFormatted}/h`;
        
      case 'count':
        return `${Math.round(value)} people`;
        
      case 'days':
        const daysPrecision = this.metadata.precision ?? 0;
        return `${value.toLocaleString('en-US', {
          minimumFractionDigits: daysPrecision,
          maximumFractionDigits: daysPrecision
        })} days`;
        
      case 'months':
        const monthsPrecision = this.metadata.precision ?? 1;
        return `${value.toLocaleString('en-US', {
          minimumFractionDigits: monthsPrecision,
          maximumFractionDigits: monthsPrecision
        })} months`;
        
      case 'ratio':
        const ratioPrecision = this.metadata.precision ?? 2;
        return value.toLocaleString('en-US', {
          minimumFractionDigits: ratioPrecision,
          maximumFractionDigits: ratioPrecision
        });
        
      default:
        // Default formatting with custom prefix/suffix
        const defaultPrecision = this.metadata.precision ?? 2;
        let result = value.toLocaleString('en-US', {
          minimumFractionDigits: defaultPrecision,
          maximumFractionDigits: defaultPrecision
        });
        
        // Apply prefix and suffix
        if (this.metadata.prefix) {
          result = this.metadata.prefix + result;
        }
        if (this.metadata.suffix) {
          result = result + this.metadata.suffix;
        }
        
        return result;
    }
  }
  
  parseInputValue(input: string): number | null {
    if (!input || typeof input !== 'string') {
      return null;
    }

    const currencyCode = this.metadata.currencyCode || 'EUR';
    const formatter = new CurrencyFormatter(currencyCode);

    // Handle value type specific parsing
    switch (this.metadata.valueType) {
      case 'currency':
      case 'rate':
        return formatter.parse(input);
        
      case 'percentage':
        // Remove % symbol and parse
        const percentCleaned = input.replace(/%/g, '').trim();
        const percentParsed = parseFloat(percentCleaned);
        if (isNaN(percentParsed)) return null;
        
        // Convert percentage to decimal (e.g., 25% -> 0.25)
        return percentParsed > 1 && percentParsed <= 100 ? percentParsed / 100 : percentParsed;
        
      case 'fte':
      case 'count':
      case 'hours':
      case 'days':
      case 'months':
      case 'ratio':
        // Remove any unit suffixes and parse as number
        const numericCleaned = input.replace(/[FTE\s%hdays,months,people]/gi, '').trim();
        const numericParsed = parseFloat(numericCleaned);
        return isNaN(numericParsed) ? null : numericParsed;
        
      default:
        // Generic number parsing with thousand separator handling
        const cleaned = input.replace(/[,\s]/g, ''); // Remove commas and spaces
        const parsed = parseFloat(cleaned);
        return isNaN(parsed) ? null : parsed;
    }
  }
  
  getValidationMessage(value: number): string | null {
    if (!this.validateValue?.(value)) {
      if (this.metadata.min !== undefined && value < this.metadata.min) {
        return `Value must be at least ${this.getDisplayValue(this.metadata.min)}`;
      }
      if (this.metadata.max !== undefined && value > this.metadata.max) {
        return `Value must be no more than ${this.getDisplayValue(this.metadata.max)}`;
      }
    }
    
    // Value type specific validation
    switch (this.metadata.valueType) {
      case 'percentage':
        if (value < 0 || value > 1) {
          return 'Percentage must be between 0% and 100%';
        }
        break;
        
      case 'fte':
      case 'count':
        if (value < 0) {
          return 'Count cannot be negative';
        }
        break;
        
      case 'currency':
        if (value < 0) {
          return 'Currency amount cannot be negative';
        }
        break;
    }
    
    return null;
  }
  
  private getDefaultPrecision(): number {
    switch (this.metadata.valueType) {
      case 'currency':
        return 0; // Whole currency units
      case 'percentage':
        return 1; // One decimal place for percentages
      case 'fte':
        return 1; // One decimal place for FTE
      case 'rate':
        return 0; // Whole currency units for rates
      case 'hours':
        return 0; // Whole hours
      case 'count':
        return 0; // Whole people
      default:
        return 2;
    }
  }
  
  /**
   * Get formatted input value for editing (without formatting for easier input)
   */
  formatForInput(value: number): string {
    const currencyCode = this.metadata.currencyCode || 'EUR';
    const formatter = new CurrencyFormatter(currencyCode);
    
    switch (this.metadata.valueType) {
      case 'currency':
      case 'rate':
        return formatter.formatForInput(value);
        
      case 'percentage':
        // Show as percentage (25% instead of 0.25)
        return (value * 100).toString();
        
      default:
        const precision = this.metadata.precision ?? this.getDefaultPrecision();
        return value.toFixed(precision);
    }
  }
}

// ==========================================
// AGGREGATION ENGINE
// ==========================================

export class BusinessPlanningAggregator {
  constructor(private registry: BusinessPlanningFieldRegistry) {}
  
  // Aggregate role-level data to office level
  aggregateRoleToOffice(roleData: Map<StandardRole, RoleData>, fieldId: string): FieldValue | null {
    const field = this.registry.getField(fieldId);
    if (!field || field.metadata.level !== 'office') {
      return null;
    }
    
    const aggregatedValues: MonthlyValues = {
      jan: 0, feb: 0, mar: 0, apr: 0, may: 0, jun: 0,
      jul: 0, aug: 0, sep: 0, oct: 0, nov: 0, dec: 0, total: 0
    };
    
    roleData.forEach((role) => {
      role.levels.forEach((levelData) => {
        const fieldValue = levelData.fields.get(fieldId);
        if (fieldValue && field.isApplicableToRoleLevel(levelData.role, levelData.level)) {
          // Apply aggregation method
          switch (field.metadata.aggregateMethod) {
            case 'sum':
            default:
              aggregatedValues.jan += fieldValue.values.jan;
              aggregatedValues.feb += fieldValue.values.feb;
              aggregatedValues.mar += fieldValue.values.mar;
              aggregatedValues.apr += fieldValue.values.apr;
              aggregatedValues.may += fieldValue.values.may;
              aggregatedValues.jun += fieldValue.values.jun;
              aggregatedValues.jul += fieldValue.values.jul;
              aggregatedValues.aug += fieldValue.values.aug;
              aggregatedValues.sep += fieldValue.values.sep;
              aggregatedValues.oct += fieldValue.values.oct;
              aggregatedValues.nov += fieldValue.values.nov;
              aggregatedValues.dec += fieldValue.values.dec;
              aggregatedValues.total += fieldValue.values.total;
              break;
              
            case 'average':
              // Implementation for average aggregation
              break;
              
            case 'weighted_average':
              // Implementation for weighted average (e.g., by FTE)
              break;
          }
        }
      });
    });
    
    return {
      fieldId,
      values: aggregatedValues,
      isCalculated: true,
      lastUpdated: new Date(),
      source: 'calculation'
    };
  }
  
  // Calculate derived fields (e.g., revenue = price × utr × hours × fte)
  calculateDerivedField(data: OfficeData, fieldId: string): FieldValue | null {
    const field = this.registry.getField(fieldId);
    if (!field || field.metadata.type !== 'calculated') {
      return null;
    }
    
    // Implementation depends on specific field calculation rules
    // This would be expanded with specific calculation logic for each derived field
    return null;
  }
  
  // Calculate KPIs
  calculateKPIs(data: OfficeData): Map<string, number> {
    const kpis = new Map<string, number>();
    
    // Total Recruitment
    const recruitmentField = data.officeLevelFields.get('total_recruitment');
    if (recruitmentField) {
      kpis.set('total_recruitment', recruitmentField.values.total);
    }
    
    // Total Churn
    const churnField = data.officeLevelFields.get('total_churn');
    if (churnField) {
      kpis.set('total_churn', churnField.values.total);
    }
    
    // Net Recruitment
    const totalRecruitment = kpis.get('total_recruitment') || 0;
    const totalChurn = kpis.get('total_churn') || 0;
    kpis.set('net_recruitment', totalRecruitment - totalChurn);
    
    // Revenue per FTE, margin calculations, etc.
    // ...additional KPI calculations
    
    return kpis;
  }
}

// ==========================================
// UI DATA TRANSFORMATION
// ==========================================

export interface UITableRow {
  id: string;
  type: 'section_header' | 'subsection_header' | 'field_office' | 'field_role' | 'field_role_level' | 'section_separator';
  
  // Hierarchical positioning
  level: number; // 0 = section, 1 = subsection, 2 = field, 3 = role, 4 = role_level
  parentId?: string;
  
  // Display data
  label: string;
  icon?: any;
  color?: string;
  bgColor?: string;
  
  // Field data
  fieldId?: string;
  role?: StandardRole;
  level_name?: StandardLevel;
  
  // Values
  values: MonthlyValues;
  isEditable: boolean;
  isCalculated: boolean;
  
  // UI behavior
  isCollapsible: boolean;
  isExpanded?: boolean;
  hasChildren: boolean;
  
  // Section separator properties
  isSectionSeparator?: boolean;
}

export class UIDataTransformer {
  constructor(private registry: BusinessPlanningFieldRegistry) {}
  
  // Transform business planning data into hierarchical UI structure
  transformToUIRows(data: OfficeData): UITableRow[] {
    const rows: UITableRow[] = [];
    const sections = this.registry.getSections();
    
    sections.forEach((section, sectionIndex) => {
      // Add section separator before each section (except the first one)
      if (sectionIndex > 0) {
        rows.push(this.createSectionSeparatorRow(section.id));
      }
      
      // Add section header
      rows.push(this.createSectionHeaderRow(section));
      
      section.subsections.forEach(subsection => {
        // Add subsection header
        rows.push(this.createSubsectionHeaderRow(subsection, section.id));
        
        subsection.fields.forEach(fieldId => {
          const field = this.registry.getField(fieldId);
          if (!field) return;
          
          if (field.metadata.level === 'office') {
            // Office-level field
            rows.push(this.createOfficeLevelFieldRow(field, data, subsection.id));
          } else {
            // Role/level fields - create hierarchy
            this.addRoleLevelFieldRows(rows, field, data, subsection);
          }
        });
      });
    });
    
    return rows;
  }
  
  private createSectionSeparatorRow(sectionId: string): UITableRow {
    return {
      id: `separator-${sectionId}`,
      type: 'section_separator',
      level: -1, // Special level for separators
      label: '',
      values: this.getEmptyMonthlyValues(),
      isEditable: false,
      isCalculated: false,
      isCollapsible: false,
      hasChildren: false,
      isSectionSeparator: true
    };
  }

  private createSectionHeaderRow(section: BusinessPlanningSection): UITableRow {
    return {
      id: `section-${section.id}`,
      type: 'section_header',
      level: 0,
      label: section.name,
      icon: section.icon,
      color: section.color,
      values: this.getEmptyMonthlyValues(),
      isEditable: false,
      isCalculated: false,
      isCollapsible: true,
      hasChildren: true
    };
  }
  
  private createSubsectionHeaderRow(subsection: BusinessPlanningSubsection, parentId: string): UITableRow {
    return {
      id: `subsection-${subsection.id}`,
      type: 'subsection_header',
      level: 1,
      parentId: `section-${parentId}`,
      label: subsection.name,
      values: this.getEmptyMonthlyValues(),
      isEditable: false,
      isCalculated: false,
      isCollapsible: subsection.isCollapsible,
      isExpanded: subsection.defaultExpanded,
      hasChildren: true
    };
  }
  
  private createOfficeLevelFieldRow(field: BusinessPlanningField, data: OfficeData, parentId: string): UITableRow {
    const fieldValue = data.officeLevelFields.get(field.metadata.id);
    
    return {
      id: `office-${field.metadata.id}`,
      type: 'field_office',
      level: 2,
      parentId: `subsection-${parentId}`,
      label: field.metadata.label,
      icon: field.metadata.icon,
      color: field.metadata.color,
      bgColor: field.metadata.bgColor,
      fieldId: field.metadata.id,
      values: fieldValue?.values || this.getEmptyMonthlyValues(),
      isEditable: field.metadata.type === 'input',
      isCalculated: field.metadata.type === 'calculated',
      isCollapsible: false,
      hasChildren: false
    };
  }
  
  private addRoleLevelFieldRows(rows: UITableRow[], field: BusinessPlanningField, data: OfficeData, subsection: BusinessPlanningSubsection): void {
    // Group by role first, then by level
    data.roles.forEach((roleData, role) => {
      if (!field.isApplicableToRole(role)) return;
      
      // Add role header if field applies to multiple levels
      if (roleData.hasLevels) {
        rows.push({
          id: `role-${field.metadata.id}-${role}`,
          type: 'field_role',
          level: 2,
          parentId: `subsection-${subsection.id}`,
          label: `${field.metadata.label} - ${role}`,
          icon: field.metadata.icon,
          color: field.metadata.color,
          role,
          values: this.getEmptyMonthlyValues(), // Could be aggregated
          isEditable: false,
          isCalculated: false,
          isCollapsible: true,
          hasChildren: true
        });
        
        // Add level rows
        roleData.levels.forEach((levelData, level) => {
          if (!field.isApplicableToLevel(level)) return;
          
          const fieldValue = levelData.fields.get(field.metadata.id);
          rows.push({
            id: `role-level-${field.metadata.id}-${role}-${level}`,
            type: 'field_role_level',
            level: 3,
            parentId: `role-${field.metadata.id}-${role}`,
            label: `${level}`,
            fieldId: field.metadata.id,
            role,
            level_name: level,
            values: fieldValue?.values || this.getEmptyMonthlyValues(),
            isEditable: field.metadata.type === 'input',
            isCalculated: field.metadata.type === 'calculated',
            isCollapsible: false,
            hasChildren: false
          });
        });
      } else {
        // Single row for flat roles
        const levelData = roleData.levels.values().next().value;
        if (levelData) {
          const fieldValue = levelData.fields.get(field.metadata.id);
          rows.push({
            id: `role-${field.metadata.id}-${role}`,
            type: 'field_role',
            level: 2,
            parentId: `subsection-${subsection.id}`,
            label: `${field.metadata.label} - ${role}`,
            icon: field.metadata.icon,
            color: field.metadata.color,
            fieldId: field.metadata.id,
            role,
            values: fieldValue?.values || this.getEmptyMonthlyValues(),
            isEditable: field.metadata.type === 'input',
            isCalculated: field.metadata.type === 'calculated',
            isCollapsible: false,
            hasChildren: false
          });
        }
      }
    });
  }
  
  private getEmptyMonthlyValues(): MonthlyValues {
    return {
      jan: 0, feb: 0, mar: 0, apr: 0, may: 0, jun: 0,
      jul: 0, aug: 0, sep: 0, oct: 0, nov: 0, dec: 0, total: 0
    };
  }
}

// ==========================================
// EXPORTS (classes are exported inline above)
// ==========================================