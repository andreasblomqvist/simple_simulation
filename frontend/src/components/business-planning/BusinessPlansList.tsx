/**
 * Business Plans List Component
 * 
 * Landing page showing all business plans with CRUD actions using DataTableMinimal
 */
import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { 
  Plus, 
  Eye, 
  Edit, 
  Trash2, 
  Download,
  Upload,
  Calendar,
  Building2,
  Bot,
  MoreHorizontal,
  Search,
  Star,
  StarOff
} from 'lucide-react';
import { DataTableMinimal, MinimalColumnDef } from '../ui/data-table-minimal';
import { Input } from '../ui/input';
import { CreateBusinessPlanModal } from './CreateBusinessPlanModal';
import { cn } from '../../lib/utils';
import { useBusinessPlanStore } from '../../stores/businessPlanStore';
import type { OfficeConfig } from '../../types/office';

interface BusinessPlan {
  id: string;
  name: string;
  office: {
    id: string;
    name: string;
  };
  year: number;
  status: 'draft' | 'active' | 'archived' | 'template';
  createdBy: 'manual' | 'ai_conversation' | 'imported';
  createdAt: Date;
  updatedAt: Date;
  description?: string;
  totalBudget?: number;
  targetRevenue?: number;
  headcountTarget?: number;
  completionPercentage: number;
  isOfficial: boolean;
  monthlyPlansCount?: number;
}

interface Props {
  offices: OfficeConfig[];
  onCreateNew: (data: {
    name: string;
    officeId: string;
    year: number;
    workflow: 'ai' | 'manual';
  }) => void;
  onEditPlan: (planId: string) => void;
  onViewPlan: (planId: string) => void;
  onDeletePlan: (planId: string) => void;
  onDuplicatePlan: (planId: string) => void;
  onMarkOfficial: (planId: string) => void;
}

// Create stable date objects outside component to prevent re-render loops
const STABLE_DATES = {
  plan1Created: new Date('2025-06-15'),
  plan1Updated: new Date('2025-07-20'),
  plan2Created: new Date('2025-07-01'),
  plan2Updated: new Date('2025-07-25'),
  plan3Created: new Date('2025-05-20'),
  plan3Updated: new Date('2025-07-18'),
  plan4Created: new Date('2025-04-10'),
  plan4Updated: new Date('2025-06-15'),
  plan5Created: new Date('2024-10-01'),
  plan5Updated: new Date('2024-12-30')
};

// Mock data for demonstration
const mockBusinessPlans: BusinessPlan[] = [
  {
    id: 'plan-1',
    name: 'Stockholm Q3 2025 Growth Plan',
    office: { id: 'stockholm', name: 'Stockholm' },
    year: 2025,
    status: 'active',
    createdBy: 'ai_conversation',
    createdAt: STABLE_DATES.plan1Created,
    updatedAt: STABLE_DATES.plan1Updated,
    description: 'AI-generated plan focusing on Senior Consultant hiring',
    totalBudget: 490000,
    targetRevenue: 2100000,
    headcountTarget: 50,
    completionPercentage: 75,
    isOfficial: true
  },
  {
    id: 'plan-2',
    name: 'Oslo 2025 Expansion Strategy',
    office: { id: 'oslo', name: 'Oslo' },
    year: 2025,
    status: 'draft',
    createdBy: 'manual',
    createdAt: STABLE_DATES.plan2Created,
    updatedAt: STABLE_DATES.plan2Updated,
    description: 'Manual plan for Norwegian market expansion',
    totalBudget: 320000,
    targetRevenue: 1800000,
    headcountTarget: 35,
    completionPercentage: 30,
    isOfficial: true
  },
  {
    id: 'plan-3',
    name: 'Copenhagen Digital Transformation',
    office: { id: 'copenhagen', name: 'Copenhagen' },
    year: 2025,
    status: 'active',
    createdBy: 'imported',
    createdAt: STABLE_DATES.plan3Created,
    updatedAt: STABLE_DATES.plan3Updated,
    description: 'Imported from legacy Planacy system',
    totalBudget: 580000,
    targetRevenue: 2500000,
    headcountTarget: 60,
    completionPercentage: 90,
    isOfficial: true
  },
  {
    id: 'plan-4',
    name: 'Standard Nordic Office Template',
    office: { id: 'template', name: 'Template' },
    year: 2025,
    status: 'template',
    createdBy: 'manual',
    createdAt: STABLE_DATES.plan4Created,
    updatedAt: STABLE_DATES.plan4Updated,
    description: 'Reusable template for new office planning',
    completionPercentage: 100,
    isOfficial: false
  },
  {
    id: 'plan-5',
    name: 'Helsinki Q4 2024 Review',
    office: { id: 'helsinki', name: 'Helsinki' },
    year: 2024,
    status: 'archived',
    createdBy: 'manual',
    createdAt: STABLE_DATES.plan5Created,
    updatedAt: STABLE_DATES.plan5Updated,
    description: 'Archived plan from previous year',
    totalBudget: 280000,
    targetRevenue: 1600000,
    headcountTarget: 32,
    completionPercentage: 100,
    isOfficial: true
  }
];

const STATUS_CONFIG = {
  draft: { label: 'Draft', color: 'bg-gray-600 text-gray-100' },
  active: { label: 'Active', color: 'bg-green-600 text-white' },
  archived: { label: 'Archived', color: 'bg-blue-600 text-white' },
  template: { label: 'Template', color: 'bg-purple-600 text-white' }
};

const CREATED_BY_CONFIG = {
  manual: { label: 'Manual', icon: Edit },
  ai_conversation: { label: 'AI Assistant', icon: Bot },
  imported: { label: 'Imported', icon: Upload }
};

// Helper functions for formatting (moved outside component to prevent re-creation)
const formatCurrency = (amount?: number) => {
  if (!amount) return '-';
  return new Intl.NumberFormat('no-NO', {
    style: 'currency',
    currency: 'NOK',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount);
};

const formatDate = (date: Date) => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(date);
};

// Create stable columns definition outside component to prevent re-creation
const createColumns = (handleActionClick: (action: string, planId: string, event: React.MouseEvent) => void): MinimalColumnDef<BusinessPlan>[] => [
  {
    accessorKey: 'name',
    header: 'Plan Name',
    size: 300,
    cell: ({ row }) => {
      const plan = row.original;
      const CreatedByIcon = CREATED_BY_CONFIG[plan.createdBy].icon;
      
      return (
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="font-medium text-white">{plan.name}</span>
            <CreatedByIcon className="h-3 w-3 text-gray-400" />
          </div>
          {plan.description && (
            <div className="text-xs text-gray-400 line-clamp-1">
              {plan.description}
            </div>
          )}
        </div>
      );
    }
  },
  {
    accessorKey: 'office.name',
    header: 'Office',
    size: 120,
    cell: ({ row }) => {
      const plan = row.original;
      return (
        <div className="flex items-center gap-2">
          <Building2 className="h-4 w-4 text-gray-400" />
          <span className="text-white">{plan.office.name}</span>
        </div>
      );
    }
  },
  {
    accessorKey: 'year',
    header: 'Year',
    size: 80,
    cell: ({ row }) => (
      <span className="text-white">{row.original.year}</span>
    )
  },
  {
    accessorKey: 'status',
    header: 'Status',
    size: 100,
    cell: ({ row }) => {
      const status = row.original.status;
      const config = STATUS_CONFIG[status];
      return (
        <Badge className={cn("text-xs", config.color)}>
          {config.label}
        </Badge>
      );
    }
  },
  {
    accessorKey: 'completionPercentage',
    header: 'Progress',
    size: 120,
    cell: ({ row }) => {
      const percentage = row.original.completionPercentage;
      return (
        <div className="space-y-1">
          <div className="flex justify-between text-xs">
            <span className="text-gray-400">Progress</span>
            <span className="text-white">{percentage}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-1.5">
            <div 
              className="bg-blue-500 h-1.5 rounded-full transition-all duration-300"
              style={{ width: `${percentage}%` }}
            />
          </div>
        </div>
      );
    }
  },
  {
    accessorKey: 'targetRevenue',
    header: 'Target Revenue',
    size: 130,
    cell: ({ row }) => (
      <span className="text-white">{formatCurrency(row.original.targetRevenue)}</span>
    )
  },
  {
    accessorKey: 'headcountTarget',
    header: 'Headcount',
    size: 100,
    cell: ({ row }) => {
      const target = row.original.headcountTarget;
      return target ? (
        <span className="text-white">{target} FTE</span>
      ) : (
        <span className="text-gray-400">-</span>
      );
    }
  },
  {
    accessorKey: 'isOfficial',
    header: 'Official',
    size: 80,
    cell: ({ row }) => {
      const plan = row.original;
      return (
        <div className="flex items-center gap-1">
          {plan.isOfficial ? (
            <div className="flex items-center gap-1">
              <Star className="h-4 w-4 text-yellow-400 fill-yellow-400" />
              <span className="text-yellow-400 text-sm font-medium">Official</span>
            </div>
          ) : (
            <span className="text-gray-400 text-sm">-</span>
          )}
        </div>
      );
    }
  },
  {
    accessorKey: 'updatedAt',
    header: 'Last Updated',
    size: 120,
    cell: ({ row }) => (
      <span className="text-gray-300 text-sm">{formatDate(row.original.updatedAt)}</span>
    )
  },
  {
    accessorKey: 'actions',
    header: 'Actions',
    size: 120,
    cell: ({ row }) => {
      const plan = row.original;
      return (
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => handleActionClick('view', plan.id, e)}
            className="h-7 w-7 p-0 hover:bg-gray-700"
            title="View Plan"
          >
            <Eye className="h-3 w-3 text-gray-400" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => handleActionClick('edit', plan.id, e)}
            className="h-7 w-7 p-0 hover:bg-gray-700"
            title="Edit Plan"
          >
            <Edit className="h-3 w-3 text-gray-400" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => handleActionClick('duplicate', plan.id, e)}
            className="h-7 w-7 p-0 hover:bg-gray-700"
            title="Duplicate Plan"
          >
            <Download className="h-3 w-3 text-gray-400" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => handleActionClick('toggleOfficial', plan.id, e)}
            className={cn(
              "h-7 w-7 p-0 hover:bg-gray-700",
              plan.isOfficial ? "text-yellow-400 hover:text-yellow-300" : "text-gray-400 hover:text-yellow-400"
            )}
            title={plan.isOfficial ? "Remove Official Status" : "Mark as Official"}
          >
            {plan.isOfficial ? (
              <Star className="h-3 w-3 fill-current" />
            ) : (
              <StarOff className="h-3 w-3" />
            )}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => handleActionClick('delete', plan.id, e)}
            className="h-7 w-7 p-0 hover:bg-gray-700 hover:text-red-400"
            title="Delete Plan"
          >
            <Trash2 className="h-3 w-3 text-gray-400" />
          </Button>
        </div>
      );
    }
  }
];

export const BusinessPlansList: React.FC<Props> = ({
  offices,
  onCreateNew,
  onEditPlan,
  onViewPlan,
  onDeletePlan,
  onDuplicatePlan,
  onMarkOfficial
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [yearFilter, setYearFilter] = useState<string>('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [businessPlans, setBusinessPlans] = useState<BusinessPlan[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch business plans from backend
  useEffect(() => {
    const fetchBusinessPlans = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8000/business-plans');
        const data = await response.json();
        
        console.log('Fetched business plans:', data.length, 'plans');
        
        // Transform backend data to match BusinessPlan interface
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        
        // Group monthly plans by office and year to create yearly business plans
        const groupedPlans: { [key: string]: any[] } = {};
        
        data.forEach((plan: any) => {
          const key = `${plan.office_id}-${plan.year}`;
          if (!groupedPlans[key]) {
            groupedPlans[key] = [];
          }
          groupedPlans[key].push(plan);
        });
        
        const transformedPlans: BusinessPlan[] = Object.entries(groupedPlans).map(([key, monthlyPlans]) => {
          // Get the first plan for basic info
          const firstPlan = monthlyPlans[0];
          const office_id = firstPlan.office_id;
          const year = firstPlan.year;
          
          // Aggregate across all months
          let totalSalaryBudget = 0;
          let totalRevenue = 0;
          let totalHeadcount = 0;
          let totalOperatingCosts = 0;
          let monthsWithData = new Set<number>();
          
          monthlyPlans.forEach((plan: any) => {
            monthsWithData.add(plan.month);
            
            plan.entries?.forEach((entry: any) => {
              // Calculate monthly salary costs
              const monthlySalary = (entry.salary || 0) / 12;
              const variableSalary = entry.variable_salary || 0;
              const socialSecurity = entry.social_security || 0;
              const pension = entry.pension || 0;
              totalSalaryBudget += monthlySalary + variableSalary + socialSecurity + pension;
              
              // Calculate revenue (only for consultants with billable time)
              if (entry.role === 'Consultant' && entry.invoiced_time && entry.average_price) {
                totalRevenue += entry.invoiced_time * entry.average_price;
              }
              
              // Calculate headcount (recruitment - churn for this month)
              const netHeadcount = (entry.recruitment || 0) - (entry.churn || 0);
              totalHeadcount += Math.max(0, netHeadcount);
              
              // Calculate operating costs
              const operatingCosts = (entry.client_loss || 0) + 
                                   (entry.education || 0) + 
                                   (entry.external_representation || 0) + 
                                   (entry.external_services || 0) + 
                                   (entry.internal_representation || 0) + 
                                   (entry.it_related_staff || 0) + 
                                   (entry.office_related || 0) + 
                                   (entry.office_rent || 0) + 
                                   (entry.other_expenses || 0);
              totalOperatingCosts += operatingCosts;
            });
          });
          
          const totalBudget = totalSalaryBudget + totalOperatingCosts;
          const completionPercentage = (monthsWithData.size / 12) * 100; // Based on how many months have data
          
          // Find the most recent plan for timestamps
          const latestPlan = monthlyPlans.reduce((latest, current) => {
            return new Date(current.updated_at) > new Date(latest.updated_at) ? current : latest;
          });
          
          return {
            id: key, // Use office-year as the unified ID
            name: `${office_id} ${year} Business Plan`,
            office: {
              id: office_id,
              name: offices.find(o => o.id === office_id)?.name || office_id
            },
            year: year,
            status: completionPercentage === 100 ? 'active' : 'draft' as const,
            createdBy: 'manual' as const,
            createdAt: new Date(firstPlan.created_at),
            updatedAt: new Date(latestPlan.updated_at),
            description: `Annual business plan for ${office_id} covering ${monthsWithData.size} months`,
            totalBudget: Math.round(totalBudget),
            targetRevenue: Math.round(totalRevenue),
            headcountTarget: Math.round(totalHeadcount * 10) / 10,
            completionPercentage: Math.round(completionPercentage),
            isOfficial: false,
            monthlyPlansCount: monthlyPlans.length
          };
        });
        
        console.log('Transformed plans:', transformedPlans.length, 'plans');
        setBusinessPlans(transformedPlans);
      } catch (error) {
        console.error('Failed to fetch business plans:', error);
        console.log('Error details:', error);
        // Fallback to mock data on error
        console.log('Using mock data as fallback');
        setBusinessPlans(mockBusinessPlans);
      } finally {
        setLoading(false);
      }
    };

    fetchBusinessPlans();
  }, [offices]);

  // Filter data based on search and filters
  const filteredData = useMemo(() => {
    console.log('Filtering data:', {
      businessPlansCount: businessPlans.length,
      searchTerm,
      statusFilter, 
      yearFilter
    });
    
    const filtered = businessPlans.filter(plan => {
      const matchesSearch = plan.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           plan.office.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           (plan.description?.toLowerCase().includes(searchTerm.toLowerCase()) ?? false);
      
      const matchesStatus = statusFilter === 'all' || plan.status === statusFilter;
      const matchesYear = yearFilter === 'all' || plan.year.toString() === yearFilter;
      
      const matches = matchesSearch && matchesStatus && matchesYear;
      return matches;
    });
    
    console.log('Filtered result:', filtered.length, 'plans');
    return filtered;
  }, [businessPlans, searchTerm, statusFilter, yearFilter]);

  // Get unique years for filter
  const availableYears = useMemo(() => {
    const years = Array.from(new Set(businessPlans.map(plan => plan.year))).sort((a, b) => b - a);
    return years;
  }, [businessPlans]);


  const handleActionClick = (action: string, planId: string, event: React.MouseEvent) => {
    event.stopPropagation(); // Prevent row click
    
    switch (action) {
      case 'view':
        onViewPlan(planId);
        break;
      case 'edit':
        onEditPlan(planId);
        break;
      case 'delete':
        console.log('Delete button clicked for plan:', planId);
        if (window.confirm('Are you sure you want to delete this business plan?')) {
          console.log('User confirmed deletion for plan:', planId);
          onDeletePlan(planId);
        } else {
          console.log('User cancelled deletion for plan:', planId);
        }
        break;
      case 'duplicate':
        onDuplicatePlan(planId);
        break;
      case 'toggleOfficial':
        onMarkOfficial(planId);
        break;
    }
  };

  // Get stable columns definition using useCallback to prevent re-creation
  const columns = useMemo(() => createColumns(handleActionClick), []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading business plans...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="business-plans-list space-y-6 p-6">

      {/* Filters and Search */}
      <Card className="bg-gray-800 border-gray-600">
        <CardContent className="p-4">
          <div className="flex items-center gap-4">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search plans, offices, or descriptions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-gray-700 border-gray-600 text-white placeholder-gray-400"
              />
            </div>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
            >
              <option value="all">All Status</option>
              <option value="draft">Draft</option>
              <option value="active">Active</option>
              <option value="archived">Archived</option>
              <option value="template">Template</option>
            </select>

            {/* Year Filter */}
            <select
              value={yearFilter}
              onChange={(e) => setYearFilter(e.target.value)}
              className="px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white text-sm"
            >
              <option value="all">All Years</option>
              {availableYears.map(year => (
                <option key={year} value={year.toString()}>{year}</option>
              ))}
            </select>

            {/* Results Count */}
            <div className="text-sm text-gray-400 whitespace-nowrap">
              {filteredData.length} of {businessPlans.length} plans
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Table */}
      <Card className="bg-gray-800 border-gray-600">
        <CardContent className="p-0">
          <DataTableMinimal
            columns={columns}
            data={filteredData}
            onRowClick={(plan) => onViewPlan(plan.id)}
            enablePagination={true}
            pageSize={10}
            className="business-plans-table"
          />
        </CardContent>
      </Card>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card className="bg-gray-800 border-gray-600">
          <CardContent className="p-4">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500"></div>
                <span className="text-sm text-gray-400">Active Plans</span>
              </div>
              <div className="text-2xl font-bold text-white">
                {businessPlans.filter(p => p.status === 'active').length}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800 border-gray-600">
          <CardContent className="p-4">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-gray-500"></div>
                <span className="text-sm text-gray-400">Draft Plans</span>
              </div>
              <div className="text-2xl font-bold text-white">
                {businessPlans.filter(p => p.status === 'draft').length}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800 border-gray-600">
          <CardContent className="p-4">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Bot className="w-4 h-4 text-blue-400" />
                <span className="text-sm text-gray-400">AI Generated</span>
              </div>
              <div className="text-2xl font-bold text-white">
                {businessPlans.filter(p => p.createdBy === 'ai_conversation').length}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800 border-gray-600">
          <CardContent className="p-4">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-purple-400" />
                <span className="text-sm text-gray-400">Current Year</span>
              </div>
              <div className="text-2xl font-bold text-white">
                {businessPlans.filter(p => p.year === new Date().getFullYear()).length}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-800 border-gray-600">
          <CardContent className="p-4">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                <span className="text-sm text-gray-400">Official Plans</span>
              </div>
              <div className="text-2xl font-bold text-white">
                {businessPlans.filter(p => p.isOfficial).length}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Create Business Plan Modal */}
      <CreateBusinessPlanModal
        open={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        offices={offices}
        onCreatePlan={onCreateNew}
      />
    </div>
  );
};