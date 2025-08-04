/**
 * Aggregated Planning Grid
 * 
 * Shows aggregated business plans across multiple offices using data-table-minimal component
 * Supports filtering by office selection, journey type, and date ranges
 */
import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { DataTableMinimal, MinimalColumnDef } from '../ui/data-table-minimal';
import { 
  Building2,
  Users,
  DollarSign,
  TrendingUp,
  Clock,
  Calculator,
  Globe,
  Calendar,
  ExternalLink,
  UserPlus,
  UserMinus,
  ArrowUpRight,
  Target,
  Percent
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { 
  STANDARD_ROLES, 
  STANDARD_LEVELS, 
  LEVELED_ROLES, 
  FLAT_ROLES, 
  BILLABLE_ROLES, 
  NON_BILLABLE_ROLES 
} from '../../types/office';
import { 
  BUSINESS_PLANNING_STRUCTURE,
  getOfficeFields,
  getRoleLevelFields,
  getFieldsForRole,
  getFieldById,
  formatFieldValue,
  ALL_ROLES,
  getRoleLevels,
  generateTableRows
} from '../../config/simple-business-planning-structure';
import { CurrencyFormatter } from '../../utils/currency';
import { FieldCategory } from '../../types/business-planning-structure';

interface AggregatedPlanEntry {
  role: string;
  level: string;
  recruitment: number;
  churn: number;
  price: number;
  utr: number;
  salary: number;
}

interface AggregatedMonthlyPlan {
  month: number;
  year: number;
  entries: AggregatedPlanEntry[];
  offices_included: string[];
  source_plans_count: number;
}

interface AggregatedPlanSummary {
  total_offices: number;
  total_months: number;
  total_entries: number;
  offices_included: string[];
  date_range: string;
  roles_covered: string[];
  aggregation_type: string;
  filters_applied: {
    year: number | null;
    office_ids: string[] | null;
    journey: string | null;
  };
}

interface AggregatedPlanData {
  aggregated_plans: AggregatedMonthlyPlan[];
  summary: AggregatedPlanSummary;
}

interface AggregatedPlanningGridProps {
  year: number;
  onYearChange: (year: number) => void;
  selectedOffices?: string[];
  onOfficesChange?: (offices: string[]) => void;
  journeyFilter?: string;
  onJourneyFilterChange?: (journey: string | undefined) => void;
  onViewOfficePlan?: (officeId: string, year: number) => void;
}

// Data structure for DataTableMinimal with hierarchical grouping
interface AggregatedTableRow {
  id: string;
  field: string;
  role: string;
  level: string;
  displayName?: string;
  totalFte: number;
  total: number;
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
}

// Note: Field categories are now defined in the simplified business planning structure

// Currency formatter instance
const currencyFormatter = new CurrencyFormatter('EUR');

const MONTHS = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
];

// Helper functions
const isLeveledRole = (role: string) => LEVELED_ROLES.includes(role as any);
const isFlatRole = (role: string) => FLAT_ROLES.includes(role as any);
const isBillableRole = (role: string) => BILLABLE_ROLES.includes(role as any);
const isNonBillableRole = (role: string) => NON_BILLABLE_ROLES.includes(role as any);

// Get available fields for a role
const getAvailableFields = (role: string) => {
  const baseFields = ['recruitment', 'churn', 'salary'];
  if (isBillableRole(role)) {
    return [...baseFields, 'price', 'utr'];
  }
  return baseFields;
};

// Get available levels for a role
const getAvailableLevels = (role: string) => {
  if (isLeveledRole(role)) {
    return STANDARD_LEVELS;
  }
  return ['General']; // Flat roles use a single "General" level
};

// Get field configuration from simplified structure
function getFieldConfig(fieldId: string) {
  const field = getFieldById(fieldId);
  if (!field) {
    // Fallback for legacy fields
    return {
      label: fieldId,
      icon: Calculator,
      color: 'text-gray-600',
      format: (val: number) => val.toString()
    };
  }
  
  return {
    label: field.label,
    icon: field.icon,
    color: field.color,
    format: (val: number) => formatFieldValue(field, val)
  };
}

export const AggregatedPlanningGrid: React.FC<AggregatedPlanningGridProps> = ({
  year,
  onYearChange,
  selectedOffices = [],
  onOfficesChange,
  journeyFilter,
  onJourneyFilterChange,
  onViewOfficePlan
}) => {
  const [data, setData] = useState<AggregatedPlanData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Group expansion state for hierarchical grouping (collapsed by default)
  const [groupExpanded, setGroupExpanded] = useState<Record<string, boolean>>(() => {
    const initialState: Record<string, boolean> = {};
    BUSINESS_PLANNING_STRUCTURE.forEach(section => {
      initialState[section.id] = false; // All sections collapsed by default
      
      // Also collapse subcategories if they exist
      if (section.subcategories) {
        section.subcategories.forEach(subcategory => {
          initialState[`${section.id}-${subcategory.id}`] = false;
        });
      }
    });
    return initialState;
  });

  const handleGroupToggle = useCallback((groupId: string, expanded: boolean) => {
    setGroupExpanded(prev => ({
      ...prev,
      [groupId]: expanded
    }));
  }, []);

  // Load aggregated data
  const loadAggregatedData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams();
      if (year) params.append('year', year.toString());
      if (selectedOffices.length > 0) params.append('office_ids', selectedOffices.join(','));
      if (journeyFilter) params.append('journey', journeyFilter);
      // Only include official plans in aggregation
      params.append('official_only', 'true');
      
      const response = await fetch(`/api/business-plans/aggregated?${params}`);
      if (!response.ok) {
        throw new Error('Failed to load aggregated business plans');
      }
      
      const aggregatedData = await response.json();
      setData(aggregatedData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }, [year, selectedOffices, journeyFilter]);

  // Load data when parameters change
  useEffect(() => {
    loadAggregatedData();
  }, [loadAggregatedData]);

  // Create data map for quick lookup
  const planDataMap = useMemo(() => {
    if (!data) return new Map();
    
    const map = new Map<string, AggregatedPlanEntry>();
    
    data.aggregated_plans.forEach(plan => {
      plan.entries.forEach(entry => {
        const key = `${entry.role}-${entry.level}-${plan.month}`;
        map.set(key, entry);
      });
    });
    
    return map;
  }, [data]);

  // Get cell data with defaults
  const getCellData = useCallback((role: string, level: string, month: number): AggregatedPlanEntry => {
    const key = `${role}-${level}-${month}`;
    const existing = planDataMap.get(key);
    
    if (existing) {
      return existing;
    }
    
    // Return default values
    const baseData = {
      role,
      level,
      recruitment: 0,
      churn: 0,
      salary: 0,
      price: 0,
      utr: 0
    };

    return baseData;
  }, [planDataMap]);

  // Calculate yearly KPIs from aggregated data
  const kpis = useMemo(() => {
    if (!data || !data.aggregated_plans.length) {
      return {
        totalRecruitment: 0,
        totalChurn: 0,
        netRecruitment: 0,
        netRecruitmentPercent: 0,
        netRevenue: 0,
        avgPriceIncrease: 0,
        avgTargetUTR: 0
      };
    }

    let yearlyRecruitment = 0;
    let yearlyChurn = 0;
    let yearlyRevenue = 0;
    let priceSum = 0;
    let utrSum = 0;
    let entryCount = 0;
    let baselineRecruitment = 0;

    // Sum data across all months (aggregated_plans contains monthly data)
    data.aggregated_plans.forEach(plan => {
      plan.entries.forEach(entry => {
        // Sum monthly values to get yearly totals
        yearlyRecruitment += (entry.recruitment || 0);
        yearlyChurn += (entry.churn || 0);
        
        if (entry.price && entry.utr) {
          // Monthly revenue calculation
          yearlyRevenue += (entry.price * entry.utr * 8 * 21); // 8 hours/day, 21 days/month
          priceSum += entry.price;
          utrSum += entry.utr;
          entryCount++;
        }
        
        // Use first month's recruitment as baseline for percentage calculation
        if (plan.month === 1) {
          baselineRecruitment += entry.recruitment || 0;
        }
      });
    });

    const netRecruitment = yearlyRecruitment - yearlyChurn;
    const netRecruitmentPercent = baselineRecruitment > 0 ? (netRecruitment / baselineRecruitment) * 100 : 0;
    const avgPrice = entryCount > 0 ? priceSum / entryCount : 0;
    const avgUTR = entryCount > 0 ? utrSum / entryCount : 0;

    return {
      totalRecruitment: yearlyRecruitment,
      totalChurn: yearlyChurn,
      netRecruitment,
      netRecruitmentPercent,
      netRevenue: yearlyRevenue,
      avgPriceIncrease: avgPrice > 0 ? ((avgPrice - 100) / 100) * 100 : 0, // Assuming 100 as baseline
      avgTargetUTR: avgUTR * 100 // Convert to percentage
    };
  }, [data]);

  // Helper function to add field rows to the table data
  const addFieldToRows = useCallback((rows: AggregatedTableRow[], section: any, field: any, categoryName: string) => {
    const fieldConfig = getFieldConfig(field.id);
    
    if (field.level === 'office') {
      // Office-level field - single row, no role/level breakdown
      const aggregatedData = {
        jan: 0, feb: 0, mar: 0, apr: 0, may: 0, jun: 0,
        jul: 0, aug: 0, sep: 0, oct: 0, nov: 0, dec: 0, total: 0
      };
      
      // For office-level fields, use mock data
      let mockValue = 0;
      if (field.id === 'monthly_hours') mockValue = 168; // Standard work month
      else if (field.id === 'total_revenue') mockValue = 150000; // Mock total revenue
      else if (field.id === 'total_operating_expenses') mockValue = 25000; // Mock expenses
      else if (field.id === 'office_rent') mockValue = 5000; // Mock rent
      else if (field.id === 'utilities') mockValue = 1200; // Mock utilities
      
      // Set the same value for all months
      aggregatedData.jan = aggregatedData.feb = aggregatedData.mar = aggregatedData.apr = 
      aggregatedData.may = aggregatedData.jun = aggregatedData.jul = aggregatedData.aug = 
      aggregatedData.sep = aggregatedData.oct = aggregatedData.nov = aggregatedData.dec = mockValue;
      aggregatedData.total = mockValue * 12;
      
      const row: AggregatedTableRow = {
        id: `${section.id}-${field.id}`,
        field: fieldConfig.label,
        role: 'Office', // Indicate this is office-level
        level: 'All',
        displayName: fieldConfig.label,
        totalFte: 0, // Office-level fields don't have FTE breakdown
        ...aggregatedData
      };
      rows.push(row);
    } else {
      // Role/level field - show breakdown by role and level
      ALL_ROLES.forEach(role => {
        // Check if field applies to this role
        if (!field.applicableRoles || field.applicableRoles.includes(role)) {
          getRoleLevels(role).forEach(level => {
            const aggregatedData = {
              jan: 0, feb: 0, mar: 0, apr: 0, may: 0, jun: 0,
              jul: 0, aug: 0, sep: 0, oct: 0, nov: 0, dec: 0, total: 0
            };
            
            // Mock FTE data - in real implementation, get from office data
            const mockFteByRoleLevel: Record<string, Record<string, number>> = {
              'Consultant': { 'A': 15, 'B': 25, 'C': 12 },
              'Sales': { 'A': 8, 'B': 12, 'C': 6 },
              'Recruitment': { 'A': 3, 'B': 4, 'C': 2 },
              'Operations': { 'General': 8 }
            };
            const totalFte = mockFteByRoleLevel[role]?.[level] || 0;
            
            for (let month = 1; month <= 12; month++) {
              const cellData = getCellData(role, level, month);
              let value = 0;
              
              // Map field IDs to actual data or mock values
              switch (field.id) {
                case 'recruitment':
                  value = cellData.recruitment || 0;
                  break;
                case 'churn':
                  value = cellData.churn || 0;
                  break;
                case 'fte':
                  value = totalFte;
                  break;
                case 'net_headcount_change':
                  value = (cellData.recruitment || 0) - (cellData.churn || 0);
                  break;
                case 'price':
                  value = cellData.price || 0;
                  break;
                case 'utr':
                  value = cellData.utr || 0;
                  break;
                case 'base_salary':
                  value = cellData.salary || 0;
                  break;
                case 'absence':
                  value = 8; // Mock absence hours
                  break;
                case 'billable_hours':
                  value = 160; // Mock billable hours (monthly_hours - absence)
                  break;
                case 'net_sales':
                  value = (cellData.price || 0) * (cellData.utr || 0) * 160; // Mock calculation
                  break;
                case 'social_security':
                  value = (cellData.salary || 0) * 0.25; // 25% of base salary
                  break;
                case 'total_people_costs':
                  value = (cellData.salary || 0) * 1.25; // base_salary + social_security
                  break;
                default:
                  value = (cellData[field.id as keyof AggregatedPlanEntry] as number) || 0;
              }
              
              switch (month) {
                case 1: aggregatedData.jan += value; break;
                case 2: aggregatedData.feb += value; break;
                case 3: aggregatedData.mar += value; break;
                case 4: aggregatedData.apr += value; break;
                case 5: aggregatedData.may += value; break;
                case 6: aggregatedData.jun += value; break;
                case 7: aggregatedData.jul += value; break;
                case 8: aggregatedData.aug += value; break;
                case 9: aggregatedData.sep += value; break;
                case 10: aggregatedData.oct += value; break;
                case 11: aggregatedData.nov += value; break;
                case 12: aggregatedData.dec += value; break;
              }
              aggregatedData.total += value;
            }
            
            const row: AggregatedTableRow = {
              id: `${section.id}-${field.id}-${role}-${level}`,
              field: fieldConfig.label,
              role,
              level,
              displayName: `${fieldConfig.label} - ${role} ${level}`,
              totalFte: field.id === 'fte' ? totalFte : 0, // Only show FTE for FTE field
              ...aggregatedData
            };
            rows.push(row);
          });
        }
      });
    }
  }, [getCellData]);

  // Prepare data for DataTableMinimal using simplified structure
  const tableData: AggregatedTableRow[] = useMemo(() => {
    if (!data) return [];
    
    const rows: AggregatedTableRow[] = [];
    
    // Use the simplified business planning structure
    BUSINESS_PLANNING_STRUCTURE.forEach(section => {
      // Handle sections with direct fields
      if (section.fields) {
        section.fields.forEach(field => {
          addFieldToRows(rows, section, field, section.name);
        });
      }
      
      // Handle sections with subcategories
      if (section.subcategories) {
        section.subcategories.forEach(subcategory => {
          subcategory.fields.forEach(field => {
            addFieldToRows(rows, section, field, `${section.name} - ${subcategory.name}`);
          });
        });
      }
    });
    
    return rows;
  }, [data, addFieldToRows]);

  // Define columns for DataTableMinimal with hierarchical grouping
  const columns = useMemo(() => [
    {
      accessorKey: 'field',
      header: 'Field/Role/Level',
      size: 200
    },
    {
      accessorKey: 'totalFte',
      header: 'Existing FTE',
      size: 100,
      cell: ({ getValue }: { getValue: () => any }) => {
        const value = getValue() as number;
        return Math.round(value).toString();
      }
    },
    {
      accessorKey: 'total',
      header: 'Total',
      size: 100
    },
    {
      accessorKey: 'jan',
      header: 'Jan',
      size: 80
    },
    {
      accessorKey: 'feb',
      header: 'Feb',
      size: 80
    },
    {
      accessorKey: 'mar',
      header: 'Mar',
      size: 80
    },
    {
      accessorKey: 'apr',
      header: 'Apr',
      size: 80
    },
    {
      accessorKey: 'may',
      header: 'May',
      size: 80
    },
    {
      accessorKey: 'jun',
      header: 'Jun',
      size: 80
    },
    {
      accessorKey: 'jul',
      header: 'Jul',
      size: 80
    },
    {
      accessorKey: 'aug',
      header: 'Aug',
      size: 80
    },
    {
      accessorKey: 'sep',
      header: 'Sep',
      size: 80
    },
    {
      accessorKey: 'oct',
      header: 'Oct',
      size: 80
    },
    {
      accessorKey: 'nov',
      header: 'Nov',
      size: 80
    },
    {
      accessorKey: 'dec',
      header: 'Dec',
      size: 80
    }
  ] as unknown as MinimalColumnDef<AggregatedTableRow>[], []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading aggregated business plan data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-red-600 mb-4">Error: {error}</p>
          <Button onClick={loadAggregatedData} variant="outline">
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">No aggregated data available</p>
      </div>
    );
  }

  return (
    <div className="aggregated-planning-grid space-y-4">
      {/* Summary Stats */}
      {data && (
        <Card style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
          <CardContent className="p-4" style={{ backgroundColor: '#1f2937' }}>
            <div className="flex flex-wrap gap-4 text-sm">
              <div className="flex items-center gap-2">
                <Building2 className="h-4 w-4" style={{ color: '#9ca3af' }} />
                <span style={{ color: '#9ca3af' }}>{data.summary.total_offices} offices</span>
              </div>
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4" style={{ color: '#9ca3af' }} />
                <span style={{ color: '#9ca3af' }}>{data.summary.roles_covered.length} roles</span>
              </div>
              <div className="flex items-center gap-2">
                <Calculator className="h-4 w-4" style={{ color: '#9ca3af' }} />
                <span style={{ color: '#9ca3af' }}>{data.summary.total_entries} total entries</span>
              </div>
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4" style={{ color: '#9ca3af' }} />
                <span style={{ color: '#9ca3af' }}>{year}</span>
              </div>
              <Badge variant="outline" className="border-blue-400 text-blue-400">
                {data.summary.aggregation_type.replace('_', ' ')}
              </Badge>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Offices Included - Clickable Buttons */}
      {data && (
        <Card style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
          <CardContent className="p-4" style={{ backgroundColor: '#1f2937' }}>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium" style={{ color: '#9ca3af' }}>Offices included:</span>
                {onViewOfficePlan && (
                  <span className="text-xs" style={{ color: '#6b7280' }}>Click office to view individual plan</span>
                )}
              </div>
              <div className="flex flex-wrap gap-2">
                {data.summary.offices_included.map(office => (
                  onViewOfficePlan ? (
                    <Button
                      key={office}
                      variant="outline"
                      size="sm"
                      onClick={() => onViewOfficePlan(office.toLowerCase(), year)}
                      className="h-8 px-3 capitalize border-gray-600 text-gray-300 hover:bg-gray-700 hover:text-white hover:border-blue-400 transition-all duration-200"
                      title={`View ${office} business plan`}
                    >
                      <Building2 className="h-3 w-3 mr-1" />
                      {office}
                    </Button>
                  ) : (
                    <Badge key={office} variant="secondary" className="capitalize border-gray-600 text-gray-300">
                      {office}
                    </Badge>
                  )
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* KPI Cards Row */}
      {data && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {/* Total Recruitment */}
          <Card style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
            <CardContent className="p-4" style={{ backgroundColor: '#1f2937' }}>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <UserPlus className="h-4 w-4 text-green-400" />
                  <span className="text-xs font-medium text-gray-400">Total Recruitment</span>
                </div>
                <div className="text-xl font-bold text-white">
                  {Math.round(kpis.totalRecruitment).toLocaleString()}
                </div>
                <div className="text-xs text-gray-400">yearly</div>
              </div>
            </CardContent>
          </Card>

          {/* Total Churn */}
          <Card style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
            <CardContent className="p-4" style={{ backgroundColor: '#1f2937' }}>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <UserMinus className="h-4 w-4 text-red-400" />
                  <span className="text-xs font-medium text-gray-400">Total Churn</span>
                </div>
                <div className="text-xl font-bold text-white">
                  {Math.round(kpis.totalChurn).toLocaleString()}
                </div>
                <div className="text-xs text-gray-400">yearly</div>
              </div>
            </CardContent>
          </Card>

          {/* Net Recruitment */}
          <Card style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
            <CardContent className="p-4" style={{ backgroundColor: '#1f2937' }}>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <ArrowUpRight className={`h-4 w-4 ${kpis.netRecruitment >= 0 ? 'text-green-400' : 'text-red-400'}`} />
                  <span className="text-xs font-medium text-gray-400">Net Recruitment</span>
                </div>
                <div className={`text-xl font-bold ${kpis.netRecruitment >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {kpis.netRecruitment >= 0 ? '+' : ''}{Math.round(kpis.netRecruitment).toLocaleString()}
                </div>
                <div className={`text-xs ${kpis.netRecruitmentPercent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {kpis.netRecruitmentPercent >= 0 ? '+' : ''}{kpis.netRecruitmentPercent.toFixed(1)}% growth
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Net Revenue */}
          <Card style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
            <CardContent className="p-4" style={{ backgroundColor: '#1f2937' }}>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <DollarSign className="h-4 w-4 text-blue-400" />
                  <span className="text-xs font-medium text-gray-400">Net Revenue</span>
                </div>
                <div className="text-xl font-bold text-white">
                  €{Math.round(kpis.netRevenue / 1000).toLocaleString()}K
                </div>
                <div className="text-xs text-gray-400">yearly</div>
              </div>
            </CardContent>
          </Card>

          {/* Price Increase */}
          <Card style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
            <CardContent className="p-4" style={{ backgroundColor: '#1f2937' }}>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-purple-400" />
                  <span className="text-xs font-medium text-gray-400">Price Increase</span>
                </div>
                <div className="text-xl font-bold text-white">
                  {kpis.avgPriceIncrease >= 0 ? '+' : ''}{kpis.avgPriceIncrease.toFixed(1)}%
                </div>
                <div className="text-xs text-gray-400">vs baseline</div>
              </div>
            </CardContent>
          </Card>

          {/* Target UTR */}
          <Card style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
            <CardContent className="p-4" style={{ backgroundColor: '#1f2937' }}>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Target className="h-4 w-4 text-yellow-400" />
                  <span className="text-xs font-medium text-gray-400">Target UTR</span>
                </div>
                <div className="text-xl font-bold text-white">
                  {kpis.avgTargetUTR.toFixed(1)}%
                </div>
                <div className="text-xs text-gray-400">average</div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Grid using DataTableMinimal */}
      <Card style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
        <CardContent className="p-0" style={{ backgroundColor: '#1f2937' }}>
          <DataTableMinimal
            columns={columns}
            data={tableData}
            enableEditing={false}
            enablePagination={false}
            enableGrouping={true}
            groupBy={['field', 'role']}
            groupExpanded={groupExpanded}
            onGroupToggle={handleGroupToggle}
            className="aggregated-planning-table"
          />
        </CardContent>
      </Card>
    </div>
  );
};