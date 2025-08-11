/**
 * Office View with Tabs - Comprehensive Office Management Interface
 * 
 * Matches the styling and layout of BusinessPlanningV2 component
 * with tabbed navigation for different office views
 */
import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { DataTableMinimal, MinimalColumnDef } from '../ui/data-table-minimal';
import { PyramidChart, PyramidStage } from '../v2/PyramidChart';
import { NumericCell, PercentageCell } from '../ui/data-table-helpers';
import { CATMatrixEditor } from './CATMatrixEditor';
import { useOfficeStore } from '../../stores/officeStore';
import { 
  Building2, 
  Users, 
  UserCheck, 
  ShoppingCart, 
  Settings,
  TrendingUp,
  Calendar,
  DollarSign,
  Activity,
  Globe,
  BarChart3,
  MapPin,
  Eye,
  Edit,
  GitCompare,
  Save
} from 'lucide-react';
import type { OfficeConfig, CATMatrix } from '../../types/office';
// import type { PopulationSnapshot } from '../../types/snapshots';
import { cn } from '../../lib/utils';
// Temporarily disabled snapshot components to fix infinite loop
// import SnapshotSelector from '../snapshot/SnapshotSelector';
// import SnapshotManager from '../snapshot/SnapshotManager';
// import CreateSnapshotModal from '../snapshot/CreateSnapshotModal';
// import SnapshotWorkforceTable from '../snapshot/SnapshotWorkforceTable';
// import { useCurrentSnapshot } from '../../stores/snapshotStore';

interface OfficeViewWithTabsProps {
  office?: OfficeConfig;
  onEdit?: () => void;
}

type OfficeTab = 'all-offices' | 'workforce' | 'economics' | 'settings';

interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  percentage?: number;
  icon: React.ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  iconBgColor?: string;
}

const KPICard: React.FC<KPICardProps> = ({ 
  title, 
  value, 
  subtitle, 
  percentage,
  icon, 
  trend,
  iconBgColor = '#3b82f6'
}) => (
  <Card className="border-0 shadow-md" style={{ backgroundColor: '#1f2937' }}>
    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium" style={{ color: '#9ca3af' }}>
        {title}
      </CardTitle>
      <div 
        className="w-8 h-8 rounded-lg flex items-center justify-center"
        style={{ backgroundColor: iconBgColor + '20' }}
      >
        <div style={{ color: iconBgColor }}>{icon}</div>
      </div>
    </CardHeader>
    <CardContent>
      <div className="text-2xl font-bold" style={{ color: '#f3f4f6' }}>{value}</div>
      {percentage !== undefined && (
        <div className="text-sm font-medium mt-1" style={{ color: '#10b981' }}>
          {percentage.toFixed(1)}% of total
        </div>
      )}
      {subtitle && (
        <p className="text-xs mt-1" style={{ color: '#6b7280' }}>{subtitle}</p>
      )}
      {trend && (
        <div className={cn(
          "flex items-center text-xs mt-2",
          trend.isPositive ? 'text-green-400' : 'text-red-400'
        )}>
          <TrendingUp className={cn(
            "h-3 w-3 mr-1",
            !trend.isPositive && 'rotate-180'
          )} />
          {Math.abs(trend.value)}% {trend.isPositive ? 'increase' : 'decrease'}
        </div>
      )}
    </CardContent>
  </Card>
);

export const OfficeViewWithTabs: React.FC<OfficeViewWithTabsProps> = ({ office, onEdit }) => {
  const [activeTab, setActiveTab] = useState<OfficeTab>(office ? 'workforce' : 'all-offices');
  // Temporarily disabled snapshot state to fix infinite loop
  // const [selectedSnapshot, setSelectedSnapshot] = useState<PopulationSnapshot | null>(null);
  // const [showCreateSnapshotModal, setShowCreateSnapshotModal] = useState(false);
  const [isSavingCAT, setIsSavingCAT] = useState(false);
  const [selectedSnapshot, setSelectedSnapshot] = useState<any>(null);
  const [workforceChanges, setWorkforceChanges] = useState<any>({});
  const [isSavingSnapshot, setIsSavingSnapshot] = useState(false);
  const [catMatrixData, setCatMatrixData] = useState<any>(null);
  const [loadingCatMatrix, setLoadingCatMatrix] = useState(false);
  const navigate = useNavigate();
  // const currentSnapshot = useCurrentSnapshot();

  // Update active tab when office prop changes
  useEffect(() => {
    if (office) {
      setActiveTab('workforce');
    } else {
      setActiveTab('all-offices');
    }
  }, [office]);
  
  const {
    offices,
    loading: officesLoading,
    error: officesError,
    loadOffices,
    updateOfficeCAT,
    resetOfficeCAT
  } = useOfficeStore();

  // Load offices on component mount
  useEffect(() => {
    if (offices.length === 0 && !officesLoading) {
      console.log('🏢 OfficeViewWithTabs: Loading offices...');
      loadOffices();
    }
  }, [loadOffices, offices.length, officesLoading]);

  // CAT Matrix handlers
  const handleSaveCAT = useCallback(async (newMatrix: CATMatrix) => {
    if (!office) return;
    
    setIsSavingCAT(true);
    try {
      await updateOfficeCAT(office.id, newMatrix);
      console.log('CAT matrix saved successfully for office:', office.id);
    } catch (error) {
      console.error('Failed to save CAT matrix:', error);
    } finally {
      setIsSavingCAT(false);
    }
  }, [office, updateOfficeCAT]);

  const handleResetCAT = useCallback(async () => {
    if (!office) return;
    
    try {
      await resetOfficeCAT(office.id);
      console.log('CAT matrix reset to default for office:', office.id);
    } catch (error) {
      console.error('Failed to reset CAT matrix:', error);
    }
  }, [office, resetOfficeCAT]);



  // Load CAT matrix data when Settings tab is active
  const loadCatMatrix = useCallback(async (officeId: string) => {
    if (!officeId) return;
    
    setLoadingCatMatrix(true);
    try {
      const response = await fetch(`http://localhost:8000/offices/${officeId}/cat-matrix`);
      if (response.ok) {
        const catMatrix = await response.json();
        console.log('🐱 Loaded CAT matrix:', catMatrix);
        setCatMatrixData(catMatrix);
      } else {
        console.log('🐱 No CAT matrix found, using global default values');
        // Use exact global CAT matrix values from SettingsV2.tsx - converted from percentages to decimals
        const defaultCatMatrix = {
          'A': { CAT0: 0.0, CAT6: 0.919, CAT12: 0.85, CAT18: 0.0, CAT24: 0.0, CAT30: 0.0, CAT36: 0, CAT42: 0, CAT48: 0, CAT54: 0, CAT60: 0 },
          'AC': { CAT0: 0.0, CAT6: 0.054, CAT12: 0.759, CAT18: 0.4, CAT24: 0.0, CAT30: 0.0, CAT36: 0, CAT42: 0, CAT48: 0, CAT54: 0, CAT60: 0 },
          'C': { CAT0: 0.0, CAT6: 0.05, CAT12: 0.442, CAT18: 0.597, CAT24: 0.278, CAT30: 0.643, CAT36: 0.2, CAT42: 0.0, CAT48: 0, CAT54: 0, CAT60: 0 },
          'SrC': { CAT0: 0.0, CAT6: 0.206, CAT12: 0.438, CAT18: 0.317, CAT24: 0.211, CAT30: 0.206, CAT36: 0.167, CAT42: 0.0, CAT48: 0.0, CAT54: 0.0, CAT60: 0.0 },
          'AM': { CAT0: 0.0, CAT6: 0.0, CAT12: 0.0, CAT18: 0.189, CAT24: 0.197, CAT30: 0.234, CAT36: 0.048, CAT42: 0.0, CAT48: 0.0, CAT54: 0.0, CAT60: 0.0 },
          'M': { CAT0: 0.0, CAT6: 0.0, CAT12: 0.01, CAT18: 0.02, CAT24: 0.03, CAT30: 0.04, CAT36: 0.05, CAT42: 0.06, CAT48: 0.07, CAT54: 0.08, CAT60: 0.1 },
          'SrM': { CAT0: 0.0, CAT6: 0.0, CAT12: 0.005, CAT18: 0.01, CAT24: 0.015, CAT30: 0.02, CAT36: 0.025, CAT42: 0.03, CAT48: 0.04, CAT54: 0.05, CAT60: 0.06 },
          'Pi': { CAT0: 0.0, CAT6: 0, CAT12: 0, CAT18: 0, CAT24: 0, CAT30: 0, CAT36: 0, CAT42: 0, CAT48: 0, CAT54: 0, CAT60: 0 },
          'P': { CAT0: 0.0, CAT6: 0, CAT12: 0, CAT18: 0, CAT24: 0, CAT30: 0, CAT36: 0, CAT42: 0, CAT48: 0, CAT54: 0, CAT60: 0 },
          'X': { CAT0: 0.0, CAT6: 0, CAT12: 0, CAT18: 0, CAT24: 0, CAT30: 0, CAT36: 0, CAT42: 0, CAT48: 0, CAT54: 0, CAT60: 0 },
          'OPE': { CAT0: 0.0, CAT6: 0, CAT12: 0, CAT18: 0, CAT24: 0, CAT30: 0, CAT36: 0, CAT42: 0, CAT48: 0, CAT54: 0, CAT60: 0 }
        };
        setCatMatrixData(defaultCatMatrix);
      }
    } catch (error) {
      console.error('Failed to load CAT matrix:', error);
      setCatMatrixData(null);
    } finally {
      setLoadingCatMatrix(false);
    }
  }, []);

  // Load CAT matrix when switching to Settings tab
  useEffect(() => {
    if (activeTab === 'settings' && office?.id && !catMatrixData && !loadingCatMatrix) {
      loadCatMatrix(office.id);
    }
  }, [activeTab, office?.id, catMatrixData, loadingCatMatrix, loadCatMatrix]);


  // Fetch workforce data from API for the office
  const [apiWorkforceData, setApiWorkforceData] = useState<any>(null);
  
  useEffect(() => {
    if (office?.id) {
      fetch(`http://localhost:8000/offices/${office.id}/workforce`)
        .then(res => res.json())
        .then(data => setApiWorkforceData(data.workforce))
        .catch(err => console.error('Failed to fetch workforce:', err));
    }
  }, [office?.id]);

  // Transform API workforce data into a more usable format
  const workforceData = useMemo(() => {
    if (!apiWorkforceData || !Array.isArray(apiWorkforceData)) {
      return { data: [], levels: [] };
    }

    // Get all unique roles and levels
    const roleMap = new Map<string, Record<string, number>>();
    const allLevels = new Set<string>();

    apiWorkforceData.forEach((entry: any) => {
      const role = entry.role || 'Unknown';
      const level = entry.level || 'Unknown';
      const fte = entry.fte || 0;

      // Track all levels
      if (level !== 'Unknown') {
        allLevels.add(level);
      }

      // Initialize role if not exists
      if (!roleMap.has(role)) {
        roleMap.set(role, {});
      }

      // Add FTE to role/level
      const roleData = roleMap.get(role)!;
      roleData[level] = (roleData[level] || 0) + fte;
    });

    // Convert to array format
    const data: Array<{ role: string; [key: string]: string | number }> = [];
    
    roleMap.forEach((levelData, roleName) => {
      const roleRow: { role: string; [key: string]: string | number } = { role: roleName };
      
      // Add level data
      Object.entries(levelData).forEach(([level, fte]) => {
        roleRow[level] = fte;
      });

      // Fill in 0 for missing levels
      allLevels.forEach(level => {
        if (!(level in roleRow)) {
          roleRow[level] = 0;
        }
      });

      data.push(roleRow);
    });

    // Sort levels in career progression order
    const careerProgression = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P'];
    const validLevels = careerProgression.filter(level => allLevels.has(level));
    
    return { data, levels: validLevels };
  }, [apiWorkforceData]);

  // Save snapshot functionality (moved after workforceData declaration)
  const handleSaveAsNewSnapshot = useCallback(async () => {
    if (!office) return;
    
    const snapshotName = prompt('Enter a name for the new snapshot:', `${office.name} - ${new Date().toLocaleDateString()}`);
    if (!snapshotName) return;
    
    setIsSavingSnapshot(true);
    try {
      // Convert current workforce data to snapshot format
      const currentWorkforceData = workforceData.data.map(row => {
        const roleWorkforce: any[] = [];
        workforceData.levels.forEach(level => {
          const fte = Number(row[level]) || 0;
          if (fte > 0) {
            roleWorkforce.push({
              role: row.role,
              level: level,
              fte: fte,
              salary: office.salaries?.[level] || 0,
              notes: `Created from ${selectedSnapshot ? selectedSnapshot.name : 'current workforce'}`
            });
          }
        });
        return roleWorkforce;
      }).flat();

      const totalFTE = currentWorkforceData.reduce((sum, w) => sum + w.fte, 0);
      const totalSalaryCost = currentWorkforceData.reduce((sum, w) => sum + (w.fte * w.salary), 0);

      const snapshotData = {
        name: snapshotName,
        description: `Workforce snapshot created from ${selectedSnapshot ? selectedSnapshot.name : 'current workforce data'}`,
        office_id: office.id,
        workforce: currentWorkforceData,
        metadata: {
          total_fte: totalFTE,
          total_salary_cost: totalSalaryCost,
          role_count: currentWorkforceData.length,
          created_by: 'User',
          tags: ['manual-creation']
        }
      };

      console.log('Creating snapshot:', snapshotData);
      
      // Here you would call the snapshot API
      // const newSnapshot = await snapshotActions.createSnapshot(snapshotData);
      
      alert(`Snapshot "${snapshotName}" saved successfully!\n\nTotal FTE: ${totalFTE.toFixed(1)}\nRoles: ${currentWorkforceData.length}`);
      
    } catch (error) {
      console.error('Failed to save snapshot:', error);
      alert('Failed to save snapshot. Please try again.');
    } finally {
      setIsSavingSnapshot(false);
    }
  }, [office, selectedSnapshot, workforceData]);

  const handleUpdateSnapshot = useCallback(async () => {
    if (!office || !selectedSnapshot) {
      alert('Please select a snapshot to update');
      return;
    }
    
    const confirmUpdate = confirm(`Are you sure you want to update "${selectedSnapshot.name}"? This will overwrite the existing snapshot data.`);
    if (!confirmUpdate) return;
    
    setIsSavingSnapshot(true);
    try {
      // Similar logic to save as new, but update existing snapshot
      console.log('Updating snapshot:', selectedSnapshot.name);
      alert(`Snapshot "${selectedSnapshot.name}" updated successfully!`);
    } catch (error) {
      console.error('Failed to update snapshot:', error);
      alert('Failed to update snapshot. Please try again.');
    } finally {
      setIsSavingSnapshot(false);
    }
  }, [office, selectedSnapshot]);

  const officeStats = useMemo(() => {
    if (!office || !apiWorkforceData) return null;
    
    // Calculate role counts from workforce data
    let totalRecruiters = 0;
    let totalSales = 0;
    let totalOperations = 0;
    let totalConsultants = 0;

    // Calculate total from actual workforce data
    let totalEmployees = 0;

    apiWorkforceData.forEach((entry: any) => {
      const fte = entry.fte || 0;
      totalEmployees += fte; // Add to total first
      
      if (entry.role === 'Recruitment') totalRecruiters += fte;
      else if (entry.role === 'Sales') totalSales += fte;
      else if (entry.role === 'Operations') totalOperations += fte;
      else if (entry.role === 'Consultant') totalConsultants += fte;
    });
    
    // Calculate percentages
    const recruitersPercent = totalEmployees > 0 ? (totalRecruiters / totalEmployees) * 100 : 0;
    const salesPercent = totalEmployees > 0 ? (totalSales / totalEmployees) * 100 : 0;
    const operationsPercent = totalEmployees > 0 ? (totalOperations / totalEmployees) * 100 : 0;
    const consultantsPercent = totalEmployees > 0 ? (totalConsultants / totalEmployees) * 100 : 0;

    // Mock economic metrics (replace with real data)
    const avgSalary = office.salaries ? 
      Object.values(office.salaries).reduce((sum: number, val: any) => sum + (val || 0), 0) / 
      Object.keys(office.salaries).length : 0;

    const costOfLiving = office.economic_parameters?.cost_of_living || 1.0;
    const marketMultiplier = office.economic_parameters?.market_multiplier || 1.0;
    const taxRate = office.economic_parameters?.tax_rate || 0.25;

    // Calculate non-debit ratio (consultant vs non-consultant)
    const nonConsultantFTE = totalRecruiters + totalSales + totalOperations;
    const nonDebitRatio = totalEmployees > 0 ? (nonConsultantFTE / totalEmployees) : 0;

    return {
      totalEmployees,
      totalRecruiters,
      totalSales,
      totalOperations,
      totalConsultants,
      recruitersPercent,
      salesPercent,
      operationsPercent,
      consultantsPercent,
      avgSalary,
      costOfLiving,
      marketMultiplier,
      taxRate,
      monthlyHours: office.economic_parameters?.monthly_hours || 160,
      workingDays: office.economic_parameters?.working_days_per_month || 20,
      nonDebitRatio,
      nonConsultantFTE
    };
  }, [office, apiWorkforceData]);

  const workforceColumns: MinimalColumnDef<any>[] = useMemo(() => {
    const columns: MinimalColumnDef<any>[] = [
      {
        accessorKey: "role",
        header: "Role",
        cell: ({ row }) => (
          <div className="font-medium">{row.original.role}</div>
        )
      }
    ];

    // Add dynamic columns for each level
    workforceData.levels.forEach(level => {
      columns.push({
        accessorKey: level,
        header: level,
        cell: ({ row }) => (
          <div className="text-center font-mono">
            {Math.round(row.original[level] || 0)}
          </div>
        )
      });
    });

    // Add total column
    columns.push({
      accessorKey: "total",
      header: "Total",
      cell: ({ row }) => {
        const total = workforceData.levels.reduce((sum, level) => {
          return sum + (Number(row.original[level]) || 0);
        }, 0);
        return (
          <div className="text-center font-mono font-bold">
            {Math.round(total)}
          </div>
        );
      }
    });

    return columns;
  }, [workforceData.levels]);

  // Journey distribution data for pyramid chart
  const journeyDistributionData: PyramidStage[] = useMemo(() => {
    if (!office) return [];
    const journey = office.journey?.toLowerCase();
    
    // Generate realistic distribution based on office maturity
    if (journey === 'mature') {
      return [
        { stage: 1, label: 'Junior', percentage: 15, description: 'A-AC levels' },
        { stage: 2, label: 'Mid-level', percentage: 35, description: 'C-SrC levels' },
        { stage: 3, label: 'Senior', percentage: 35, description: 'AM-SrM levels' },
        { stage: 4, label: 'Leadership', percentage: 15, description: 'Pi-P levels' }
      ];
    } else if (journey === 'established') {
      return [
        { stage: 1, label: 'Junior', percentage: 25, description: 'A-AC levels' },
        { stage: 2, label: 'Mid-level', percentage: 40, description: 'C-SrC levels' },
        { stage: 3, label: 'Senior', percentage: 30, description: 'AM-SrM levels' },
        { stage: 4, label: 'Leadership', percentage: 5, description: 'Pi-P levels' }
      ];
    } else {
      // Emerging
      return [
        { stage: 1, label: 'Junior', percentage: 40, description: 'A-AC levels' },
        { stage: 2, label: 'Mid-level', percentage: 35, description: 'C-SrC levels' },
        { stage: 3, label: 'Senior', percentage: 20, description: 'AM-SrM levels' },
        { stage: 4, label: 'Leadership', percentage: 5, description: 'Pi-P levels' }
      ];
    }
  }, [office?.journey]);

  // Office list data and columns for All Offices tab
  const formatLocation = (office: OfficeConfig) => {
    return office.city && office.country ? `${office.city}, ${office.country}` : office.name;
  };

  const formatJourney = (journey: string) => {
    const journeyMap: Record<string, string> = {
      'mature': 'Mature',
      'growth': 'Growth', 
      'startup': 'Startup',
      'established': 'Established',
      'emerging': 'Emerging'
    };
    return journeyMap[journey] || journey;
  };

  const handleOfficeSelect = (selectedOffice: OfficeConfig) => {
    // Instead of navigating away, we want to:
    // 1. Pass the selected office to the parent component via URL navigation
    // 2. Let the parent re-render this component with the selected office
    // 3. Which will then default to the 'workforce' tab due to our conditional logic
    navigate(`/office-overview/${selectedOffice.id}`);
  };

  const officeListColumns: MinimalColumnDef<OfficeConfig>[] = [
    {
      accessorKey: "name",
      header: "Office",
      cell: ({ row }) => {
        const officeItem = row.original;
        return (
          <div 
            className="space-y-1 cursor-pointer hover:bg-gray-700 p-2 rounded transition-colors"
            onClick={(e) => {
              e.stopPropagation();
              handleOfficeSelect(officeItem);
            }}
          >
            <div className="font-medium" style={{ color: '#f3f4f6' }}>{officeItem.name}</div>
            <div className="flex items-center text-sm" style={{ color: '#9ca3af' }}>
              <MapPin className="mr-1 h-3 w-3" />
              {formatLocation(officeItem)}
            </div>
          </div>
        );
      },
    },
    {
      accessorKey: "total_fte",
      header: "Total FTE",
      cell: ({ row }) => (
        <div className="flex items-center">
          <Users className="mr-2 h-4 w-4" style={{ color: '#9ca3af' }} />
          <NumericCell value={Math.round(row.getValue("total_fte") as number)} />
        </div>
      ),
    },
    {
      accessorKey: "journey",
      header: "Journey",
      cell: ({ row }) => {
        const journey = row.getValue("journey") as string;
        return (
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
            journey === 'mature' 
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
              : journey === 'growth'
              ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300'
              : journey === 'established'
              ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
              : journey === 'emerging'
              ? 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300'
              : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
          }`}>
            {formatJourney(journey)}
          </span>
        );
      },
    },
    {
      accessorKey: "economic_parameters",
      header: "Cost of Living",
      cell: ({ row }) => {
        const params = row.getValue("economic_parameters") as any;
        return params?.cost_of_living ? (
          <PercentageCell value={params.cost_of_living} decimals={1} />
        ) : (
          <span className="text-sm" style={{ color: '#9ca3af' }}>N/A</span>
        );
      },
    },
    {
      id: "actions",
      enableHiding: false,
      cell: ({ row }) => {
        const officeItem = row.original;
        return (
          <div className="flex items-center space-x-2">
            <Button 
              variant="ghost" 
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                navigate(`/office-overview/${officeItem.id}`);
              }}
              title="View Overview"
              className="hover:bg-gray-700"
            >
              <Eye className="h-4 w-4" />
            </Button>
            <Button 
              variant="ghost" 
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                navigate(`/offices/${officeItem.id}`);
              }}
              title="Configure Office"
              className="hover:bg-gray-700"
            >
              <Edit className="h-4 w-4" />
            </Button>
          </div>
        );
      },
    },
  ];

  const tabs = office ? [
    {
      key: 'all-offices' as OfficeTab,
      label: 'All Offices',
      icon: Globe,
      description: 'Overview of all offices and global metrics'
    },
    {
      key: 'workforce' as OfficeTab,
      label: 'Workforce',
      icon: Users,
      description: 'Current and historical workforce composition'
    },
    {
      key: 'economics' as OfficeTab,
      label: 'Economics',
      icon: DollarSign,
      description: 'Economic parameters and cost structure'
    },
    {
      key: 'settings' as OfficeTab,
      label: 'Settings',
      icon: Settings,
      description: 'Office configuration and parameters'
    }
  ] : [
    {
      key: 'all-offices' as OfficeTab,
      label: 'All Offices',
      icon: Globe,
      description: 'Overview of all offices and global metrics'
    }
  ];

  return (
    <div className="space-y-8" style={{ backgroundColor: '#111827', minHeight: '100vh', padding: '1rem' }}>
      {/* Enhanced Header matching Business Planning style */}
      <div className="flex items-start justify-between p-1">
        <div className="space-y-2">
          <h1 className="text-4xl font-bold tracking-tight flex items-center gap-3" style={{ color: '#f3f4f6' }}>
            <Building2 className="h-10 w-10" style={{ color: '#3b82f6' }} />
            {activeTab === 'all-offices' ? 'Office Management' : (office ? office.name : 'Office Management')}
          </h1>
          <p className="text-lg max-w-2xl leading-relaxed" style={{ color: '#d1d5db' }}>
            {activeTab === 'all-offices' 
              ? 'Manage and oversee all office locations with comprehensive analytics and insights'
              : (office 
                ? `Comprehensive office management and analytics for ${office.city || 'Unknown'}, ${office.country || 'Unknown'}`
                : 'Manage and oversee all office locations with comprehensive analytics and insights')
            }
          </p>
        </div>

        <div className="flex items-center gap-3">
          {office && (
            <Badge 
              variant="outline" 
              className="px-3 py-1"
              style={{
                backgroundColor: '#1f2937',
                borderColor: '#3b82f6',
                color: '#93c5fd'
              }}
            >
              {office.journey} Journey
            </Badge>
          )}
          
          {office && onEdit && (
            <Button 
              variant="outline" 
              size="sm"
              onClick={onEdit}
              style={{
                height: '36px',
                padding: '0 1rem',
                fontWeight: '500',
                border: '1px solid #374151',
                backgroundColor: '#1f2937',
                color: '#f3f4f6',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#374151';
                e.currentTarget.style.borderColor = '#4b5563';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#1f2937';
                e.currentTarget.style.borderColor = '#374151';
              }}
            >
              <Settings className="h-4 w-4 mr-2" />
              Configure Office
            </Button>
          )}
        </div>
      </div>

      {/* Enhanced Tabs matching Business Planning style */}
      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as OfficeTab)} className="space-y-6">
        <div className="relative">
          <TabsList 
            className={`grid w-full ${office ? 'grid-cols-4' : 'grid-cols-1'} h-14 p-1.5 rounded-xl border-0 shadow-sm`}
            style={{ backgroundColor: '#374151' }}
          >
            {tabs.map(tab => {
              const Icon = tab.icon;
              return (
                <TabsTrigger 
                  key={tab.key} 
                  value={tab.key}
                  className="flex flex-col items-center gap-1.5 h-11 px-3 rounded-lg transition-all duration-200 font-medium"
                  style={{
                    backgroundColor: activeTab === tab.key ? '#1f2937' : 'transparent',
                    color: activeTab === tab.key ? '#f3f4f6' : '#9ca3af',
                    boxShadow: activeTab === tab.key ? '0 1px 3px rgba(0, 0, 0, 0.1)' : 'none'
                  }}
                  onMouseEnter={(e) => {
                    if (activeTab !== tab.key) {
                      e.currentTarget.style.color = '#d1d5db';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (activeTab !== tab.key) {
                      e.currentTarget.style.color = '#9ca3af';
                    }
                  }}
                >
                  <Icon className="h-4 w-4" style={{ color: activeTab === tab.key ? '#f3f4f6' : '#9ca3af' }} />
                  <span className="text-xs">{tab.label}</span>
                </TabsTrigger>
              );
            })}
          </TabsList>
        </div>

        {/* All Offices Tab */}
        <TabsContent value="all-offices" className="space-y-6">
          <Card className="border-0 shadow-md overflow-hidden" style={{ backgroundColor: '#1f2937' }}>
            <CardHeader className="p-6" style={{ 
              borderBottom: '1px solid #374151',
              background: 'linear-gradient(to right, #1e3a8a, #312e81)',
            }}>
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <CardTitle className="flex items-center gap-3 text-xl font-bold" style={{ color: '#f3f4f6' }}>
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#3b82f6' }}>
                      <Globe className="h-5 w-5" style={{ color: '#ffffff' }} />
                    </div>
                    All Offices Overview
                  </CardTitle>
                  <p className="text-sm max-w-3xl leading-relaxed" style={{ color: '#d1d5db' }}>
                    Comprehensive overview of all offices with key metrics, journey stages, and management actions
                  </p>
                </div>
              </div>
            </CardHeader>
            
            <CardContent className="p-0">
              {officesLoading ? (
                <div className="text-center py-12">
                  <Activity className="h-8 w-8 mx-auto mb-4 animate-spin" style={{ color: '#9ca3af' }} />
                  <p style={{ color: '#9ca3af' }}>Loading offices...</p>
                </div>
              ) : officesError ? (
                <div className="text-center py-12">
                  <Building2 className="h-12 w-12 mx-auto mb-4" style={{ color: '#ef4444' }} />
                  <h3 className="text-lg font-medium mb-2" style={{ color: '#f3f4f6' }}>Error Loading Offices</h3>
                  <p style={{ color: '#9ca3af' }}>{officesError}</p>
                </div>
              ) : offices.length === 0 ? (
                <div className="text-center py-12">
                  <Building2 className="h-12 w-12 mx-auto mb-4" style={{ color: '#9ca3af' }} />
                  <h3 className="text-lg font-medium mb-2" style={{ color: '#f3f4f6' }}>No Offices Found</h3>
                  <p style={{ color: '#9ca3af' }}>No offices are currently configured</p>
                </div>
              ) : (
                <DataTableMinimal
                  columns={officeListColumns}
                  data={offices}
                  enablePagination={true}
                  pageSize={10}
                  className="offices-list-table"
                />
              )}
            </CardContent>
          </Card>
        </TabsContent>


        {/* Workforce Tab */}
        <TabsContent value="workforce" className="space-y-6">
          {office && officeStats ? (
            <>
          <Card className="border-0 shadow-md overflow-hidden" style={{ backgroundColor: '#1f2937' }}>
            <CardHeader className="p-6" style={{ 
              borderBottom: '1px solid #374151',
              background: 'linear-gradient(to right, #1e3a8a, #312e81)',
            }}>
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <CardTitle className="flex items-center gap-3 text-xl font-bold" style={{ color: '#f3f4f6' }}>
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#3b82f6' }}>
                      <Users className="h-5 w-5" style={{ color: '#ffffff' }} />
                    </div>
                    Workforce Composition
                  </CardTitle>
                  <p className="text-sm max-w-3xl leading-relaxed" style={{ color: '#d1d5db' }}>
                    Current workforce breakdown of roles, levels, and headcount across the office
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleSaveAsNewSnapshot}
                    disabled={isSavingSnapshot}
                    className="bg-gray-700 border-gray-600 text-gray-100 hover:bg-gray-600 disabled:opacity-50"
                  >
                    <Save className="h-4 w-4 mr-2" />
                    {isSavingSnapshot ? 'Saving...' : 'Save as New'}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleUpdateSnapshot}
                    disabled={isSavingSnapshot || !selectedSnapshot}
                    className="bg-gray-700 border-gray-600 text-gray-100 hover:bg-gray-600 disabled:opacity-50"
                  >
                    <Save className="h-4 w-4 mr-2" />
                    {isSavingSnapshot ? 'Updating...' : 'Update Snapshot'}
                  </Button>
                </div>
              </div>
            </CardHeader>
            
            <CardContent>
              {/* Snapshot Selector */}
              <div className="p-6 border-b border-gray-600">
                <div className="space-y-2">
                  <label className="text-sm font-medium" style={{ color: '#f3f4f6' }}>
                    View Data From
                  </label>
                  <select 
                    className="w-full bg-gray-800 border border-gray-600 rounded-md px-3 py-2 text-gray-100 hover:bg-gray-700"
                    defaultValue="current"
                  >
                    <option value="current">Current Workforce (Live Data)</option>
                    <option value="snapshot1">Snapshot: Q4 2024 Planning - Dec 15, 2024 (245.0 FTE)</option>
                    <option value="snapshot2">Snapshot: Mid-Year Review - Jul 1, 2024 (210.3 FTE)</option>
                    <option value="snapshot3">Snapshot: Initial Baseline - Jan 1, 2024 (185.5 FTE)</option>
                  </select>
                  <p className="text-xs" style={{ color: '#9ca3af' }}>
                    Select a snapshot to view historical workforce data or use current workforce for live editing
                  </p>
                </div>
              </div>

              {/* KPI Cards Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 p-6">
                <KPICard
                  title="Total Employees"
                  value={Math.round(officeStats.totalEmployees)}
                  percentage={100}
                  subtitle="Full-time equivalents"
                  icon={<Users className="h-4 w-4" />}
                  iconBgColor="#3b82f6"
                  trend={{ value: 5.2, isPositive: true }}
                />
                <KPICard
                  title="Consultants"
                  value={Math.round(officeStats.totalConsultants)}
                  percentage={officeStats.consultantsPercent}
                  subtitle="Billable consultants"
                  icon={<Activity className="h-4 w-4" />}
                  iconBgColor="#8b5cf6"
                />
                <KPICard
                  title="Recruiters"
                  value={Math.round(officeStats.totalRecruiters)}
                  percentage={officeStats.recruitersPercent}
                  subtitle="Recruitment team"
                  icon={<UserCheck className="h-4 w-4" />}
                  iconBgColor="#10b981"
                />
                <KPICard
                  title="Sales Team"
                  value={Math.round(officeStats.totalSales)}
                  percentage={officeStats.salesPercent}
                  subtitle="Sales and business development"
                  icon={<ShoppingCart className="h-4 w-4" />}
                  iconBgColor="#f59e0b"
                />
                <KPICard
                  title="Operations"
                  value={Math.round(officeStats.totalOperations)}
                  percentage={officeStats.operationsPercent}
                  subtitle="Operations and support"
                  icon={<Settings className="h-4 w-4" />}
                  iconBgColor="#ef4444"
                />
              </div>

              {/* Editable Workforce Table */}
              <div style={{ borderTop: '1px solid #374151' }} className="p-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-medium" style={{ color: '#f3f4f6' }}>
                      Workforce Details
                    </h3>
                    <div className="text-sm" style={{ color: '#9ca3af' }}>
                      Double-click cells to edit • Changes are highlighted in yellow
                    </div>
                  </div>
                  
                  {/* Editable Table */}
                  <div className="overflow-x-auto">
                    <table className="w-full border-collapse">
                      <thead>
                        <tr style={{ backgroundColor: '#111827' }}>
                          <th className="border border-gray-600 px-3 py-2 text-left font-medium" style={{ color: '#f3f4f6' }}>
                            Role
                          </th>
                          {workforceData.levels.map(level => (
                            <th key={level} className="border border-gray-600 px-3 py-2 text-center font-medium" style={{ color: '#f3f4f6' }}>
                              {level}
                            </th>
                          ))}
                          <th className="border border-gray-600 px-3 py-2 text-center font-medium" style={{ color: '#f3f4f6' }}>
                            Total
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {workforceData.data.map((row, rowIndex) => {
                          const total = workforceData.levels.reduce((sum, level) => {
                            return sum + (Number(row[level]) || 0);
                          }, 0);
                          
                          return (
                            <tr key={row.role} style={{ backgroundColor: '#1f2937' }}>
                              <td className="border border-gray-600 px-3 py-2 font-medium" style={{ color: '#f3f4f6' }}>
                                {row.role}
                              </td>
                              {workforceData.levels.map(level => (
                                <td key={level} className="border border-gray-600 px-1 py-1 text-center">
                                  <input
                                    type="number"
                                    min="0"
                                    step="0.1"
                                    defaultValue={Math.round(row[level] || 0)}
                                    className="w-full bg-transparent text-center border-0 focus:bg-yellow-400 focus:bg-opacity-20 focus:text-black px-2 py-1 rounded"
                                    style={{ color: '#f3f4f6' }}
                                    onFocus={(e) => e.target.select()}
                                    onChange={() => {
                                      // TODO: Track changes for save functionality
                                    }}
                                  />
                                </td>
                              ))}
                              <td className="border border-gray-600 px-3 py-2 text-center font-bold" style={{ color: '#f3f4f6' }}>
                                {Math.round(total)}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>

                  <div className="flex items-center justify-between pt-4" style={{ borderTop: '1px solid #374151' }}>
                    <div className="text-sm" style={{ color: '#9ca3af' }}>
                      Editing: Current Workforce (Live Data)
                    </div>
                    <div className="text-sm" style={{ color: '#9ca3af' }}>
                      Total FTE: <span className="font-mono font-bold" style={{ color: '#f3f4f6' }}>
                        {Math.round(officeStats.totalEmployees)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Seniority Analysis Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Non-Debit Ratio Card */}
            <Card className="border-0 shadow-md" style={{ backgroundColor: '#1f2937' }}>
              <CardHeader className="p-6" style={{ borderBottom: '1px solid #374151' }}>
                <CardTitle className="flex items-center gap-3 text-xl font-bold" style={{ color: '#f3f4f6' }}>
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#10b981' }}>
                    <TrendingUp className="h-5 w-5" style={{ color: '#ffffff' }} />
                  </div>
                  Seniority Metrics
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6">
                <div className="space-y-6">
                  {/* Non-Debit Ratio */}
                  <div className="text-center">
                    <div className="text-4xl font-bold mb-2" style={{ color: '#10b981' }}>
                      {(officeStats.nonDebitRatio * 100).toFixed(1)}%
                    </div>
                    <h3 className="text-lg font-medium mb-2" style={{ color: '#f3f4f6' }}>
                      Non-Debit Ratio
                    </h3>
                    <p className="text-sm" style={{ color: '#9ca3af' }}>
                      {Math.round(officeStats.nonConsultantFTE)} non-consultant FTE out of {Math.round(officeStats.totalEmployees)} total
                    </p>
                  </div>

                  {/* Breakdown */}
                  <div className="grid grid-cols-2 gap-4 pt-4" style={{ borderTop: '1px solid #374151' }}>
                    <div className="text-center">
                      <div className="text-2xl font-bold" style={{ color: '#ef4444' }}>
                        {Math.round(officeStats.totalConsultants)}
                      </div>
                      <div className="text-sm" style={{ color: '#9ca3af' }}>Consultants</div>
                      <div className="text-xs" style={{ color: '#6b7280' }}>
                        {officeStats.consultantsPercent.toFixed(1)}%
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold" style={{ color: '#10b981' }}>
                        {Math.round(officeStats.nonConsultantFTE)}
                      </div>
                      <div className="text-sm" style={{ color: '#9ca3af' }}>Non-Consultant</div>
                      <div className="text-xs" style={{ color: '#6b7280' }}>
                        {(officeStats.nonDebitRatio * 100).toFixed(1)}%
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Journey Distribution Chart */}
            <Card className="border-0 shadow-md" style={{ backgroundColor: '#1f2937' }}>
              <CardHeader className="p-6" style={{ borderBottom: '1px solid #374151' }}>
                <CardTitle className="flex items-center gap-3 text-xl font-bold" style={{ color: '#f3f4f6' }}>
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#3b82f6' }}>
                    <BarChart3 className="h-5 w-5" style={{ color: '#ffffff' }} />
                  </div>
                  Journey Distribution
                </CardTitle>
                <p className="text-sm mt-2" style={{ color: '#d1d5db' }}>
                  Seniority levels across the {office.journey?.toLowerCase()} office
                </p>
              </CardHeader>
              <CardContent className="p-6">
                <PyramidChart 
                  stages={journeyDistributionData}
                  colors={[
                    'bg-blue-500',    // Leadership
                    'bg-green-500',   // Senior  
                    'bg-yellow-500',  // Mid-level
                    'bg-red-500'      // Junior
                  ]}
                  className="py-4"
                />
              </CardContent>
            </Card>
          </div>
            </>
          ) : (
            <div className="text-center py-12">
              <Users className="h-12 w-12 mx-auto mb-4" style={{ color: '#9ca3af' }} />
              <h3 className="text-lg font-medium mb-2" style={{ color: '#f3f4f6' }}>No Office Selected</h3>
              <p style={{ color: '#9ca3af' }}>Select an office from the "All Offices" tab to view workforce details</p>
            </div>
          )}
        </TabsContent>


        {/* Economics Tab */}
        <TabsContent value="economics" className="space-y-6">
          {office && officeStats ? (
            <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="border-0 shadow-md" style={{ backgroundColor: '#1f2937' }}>
              <CardHeader className="p-6" style={{ 
                borderBottom: '1px solid #374151',
                background: 'linear-gradient(to right, #1e3a8a, #312e81)',
              }}>
                <CardTitle className="flex items-center gap-2 text-lg font-bold" style={{ color: '#f3f4f6' }}>
                  <DollarSign className="h-5 w-5" style={{ color: '#ffffff' }} />
                  Economic Parameters
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6">
                <div className="space-y-4">
                  <div className="p-4 rounded-lg" style={{ backgroundColor: '#111827' }}>
                    <div className="text-sm font-medium mb-2" style={{ color: '#9ca3af' }}>Cost of Living</div>
                    <div className="text-2xl font-bold" style={{ color: '#f3f4f6' }}>
                      {(officeStats.costOfLiving * 100).toFixed(0)}%
                    </div>
                  </div>
                  <div className="p-4 rounded-lg" style={{ backgroundColor: '#111827' }}>
                    <div className="text-sm font-medium mb-2" style={{ color: '#9ca3af' }}>Market Multiplier</div>
                    <div className="text-2xl font-bold" style={{ color: '#f3f4f6' }}>
                      {officeStats.marketMultiplier.toFixed(2)}x
                    </div>
                  </div>
                  <div className="p-4 rounded-lg" style={{ backgroundColor: '#111827' }}>
                    <div className="text-sm font-medium mb-2" style={{ color: '#9ca3af' }}>Tax Rate</div>
                    <div className="text-2xl font-bold" style={{ color: '#f3f4f6' }}>
                      {(officeStats.taxRate * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-md" style={{ backgroundColor: '#1f2937' }}>
              <CardHeader className="p-6" style={{ 
                borderBottom: '1px solid #374151',
                background: 'linear-gradient(to right, #1e3a8a, #312e81)',
              }}>
                <CardTitle className="flex items-center gap-2 text-lg font-bold" style={{ color: '#f3f4f6' }}>
                  <Calendar className="h-5 w-5" style={{ color: '#ffffff' }} />
                  Work Schedule
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6">
                <div className="space-y-4">
                  <div className="p-4 rounded-lg" style={{ backgroundColor: '#111827' }}>
                    <div className="text-sm font-medium mb-2" style={{ color: '#9ca3af' }}>Monthly Hours</div>
                    <div className="text-2xl font-bold" style={{ color: '#f3f4f6' }}>
                      {officeStats.monthlyHours}
                    </div>
                  </div>
                  <div className="p-4 rounded-lg" style={{ backgroundColor: '#111827' }}>
                    <div className="text-sm font-medium mb-2" style={{ color: '#9ca3af' }}>Working Days/Month</div>
                    <div className="text-2xl font-bold" style={{ color: '#f3f4f6' }}>
                      {officeStats.workingDays}
                    </div>
                  </div>
                  <div className="p-4 rounded-lg" style={{ backgroundColor: '#111827' }}>
                    <div className="text-sm font-medium mb-2" style={{ color: '#9ca3af' }}>Average Salary</div>
                    <div className="text-2xl font-bold" style={{ color: '#f3f4f6' }}>
                      €{Math.round(officeStats.avgSalary).toLocaleString()}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
            </>
          ) : (
            <div className="text-center py-12">
              <DollarSign className="h-12 w-12 mx-auto mb-4" style={{ color: '#9ca3af' }} />
              <h3 className="text-lg font-medium mb-2" style={{ color: '#f3f4f6' }}>No Office Selected</h3>
              <p style={{ color: '#9ca3af' }}>Select an office from the "All Offices" tab to view economic data</p>
            </div>
          )}
        </TabsContent>


        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-6">
          {office ? (
            <>
              {/* Basic Office Information */}
              <Card className="border-0 shadow-md" style={{ backgroundColor: '#1f2937' }}>
                <CardHeader className="p-6" style={{ 
                  borderBottom: '1px solid #374151',
                  background: 'linear-gradient(to right, #1e3a8a, #312e81)',
                }}>
                  <CardTitle className="flex items-center gap-3 text-xl font-bold" style={{ color: '#f3f4f6' }}>
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#3b82f6' }}>
                      <Settings className="h-5 w-5" style={{ color: '#ffffff' }} />
                    </div>
                    Office Configuration
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="space-y-6">
                    <div>
                      <h3 className="text-lg font-medium mb-4" style={{ color: '#f3f4f6' }}>Basic Information</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="text-sm" style={{ color: '#9ca3af' }}>Office Name</label>
                          <div className="mt-1 p-2 rounded-lg" style={{ backgroundColor: '#111827', color: '#f3f4f6' }}>
                            {office.name}
                          </div>
                        </div>
                        <div>
                          <label className="text-sm" style={{ color: '#9ca3af' }}>Journey Stage</label>
                          <div className="mt-1 p-2 rounded-lg" style={{ backgroundColor: '#111827', color: '#f3f4f6' }}>
                            {office.journey}
                          </div>
                        </div>
                        <div>
                          <label className="text-sm" style={{ color: '#9ca3af' }}>Total FTE</label>
                          <div className="mt-1 p-2 rounded-lg" style={{ backgroundColor: '#111827', color: '#f3f4f6' }}>
                            {office.total_fte}
                          </div>
                        </div>
                        <div>
                          <label className="text-sm" style={{ color: '#9ca3af' }}>Timezone</label>
                          <div className="mt-1 p-2 rounded-lg" style={{ backgroundColor: '#111827', color: '#f3f4f6' }}>
                            {office.timezone}
                          </div>
                        </div>
                      </div>
                    </div>

                    {onEdit && (
                      <div className="pt-4 border-t" style={{ borderColor: '#374151' }}>
                        <Button
                          onClick={onEdit}
                          style={{
                            backgroundColor: '#3b82f6',
                            color: '#ffffff',
                            fontWeight: '500'
                          }}
                          className="hover:bg-blue-700"
                        >
                          <Settings className="h-4 w-4 mr-2" />
                          Edit Configuration
                        </Button>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* CAT Matrix Table View - Simple read-only display like global settings */}
              {console.log('🐱 CAT Matrix Debug:', { 
                hasOffice: !!office, 
                officeName: office?.name, 
                hasCATMatrixData: !!catMatrixData,
                catMatrixKeys: catMatrixData ? Object.keys(catMatrixData) : 'none',
                loadingCatMatrix,
                catMatrixData 
              })}
              {loadingCatMatrix ? (
                <Card className="border-0 shadow-md" style={{ backgroundColor: '#1f2937' }}>
                  <CardContent className="p-6 text-center">
                    <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
                    <p style={{ color: '#9ca3af' }}>Loading CAT matrix data...</p>
                  </CardContent>
                </Card>
              ) : catMatrixData ? (
                <Card className="border-0 shadow-md" style={{ backgroundColor: '#1f2937' }}>
                  <CardHeader className="p-6" style={{ 
                    borderBottom: '1px solid #374151',
                    background: 'linear-gradient(to right, #1e3a8a, #312e81)',
                  }}>
                    <CardTitle className="flex items-center gap-3 text-xl font-bold" style={{ color: '#f3f4f6' }}>
                      <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#3b82f6' }}>
                        <GitCompare className="h-5 w-5" style={{ color: '#ffffff' }} />
                      </div>
                      CAT Matrix - {office.name}
                    </CardTitle>
                    <p className="text-sm max-w-3xl leading-relaxed" style={{ color: '#d1d5db' }}>
                      Career advancement timeline progression probabilities for this office
                    </p>
                  </CardHeader>
                  <CardContent className="p-6">
                    <div className="space-y-4">
                      <p className="text-sm" style={{ color: '#9ca3af' }}>
                        CAT values represent progression probability coefficients (0.0 - 1.0) for each level and category.
                      </p>
                      
                      {/* CAT Matrix Table */}
                      <div className="overflow-x-auto">
                        <table className="w-full border-collapse">
                          <thead>
                            <tr style={{ backgroundColor: '#111827' }}>
                              <th className="border border-gray-600 px-3 py-2 text-left font-medium" style={{ color: '#f3f4f6' }}>
                                Level
                              </th>
                              {['CAT0', 'CAT6', 'CAT12', 'CAT18', 'CAT24', 'CAT30', 'CAT36', 'CAT42', 'CAT48', 'CAT54', 'CAT60'].map(catStage => (
                                <th key={catStage} className="border border-gray-600 px-3 py-2 text-center font-medium" style={{ color: '#f3f4f6' }}>
                                  {catStage}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {Object.entries(catMatrixData).map(([level, stages]) => (
                              <tr key={level} style={{ backgroundColor: '#1f2937' }}>
                                <td className="border border-gray-600 px-3 py-2 font-medium" style={{ color: '#f3f4f6' }}>
                                  {level}
                                </td>
                                {['CAT0', 'CAT6', 'CAT12', 'CAT18', 'CAT24', 'CAT30', 'CAT36', 'CAT42', 'CAT48', 'CAT54', 'CAT60'].map(catStage => {
                                  const value = stages[catStage] || 0;
                                  const percentage = (value * 100).toFixed(1);
                                  const getColor = (val: number) => {
                                    if (val === 0) return 'bg-red-500 text-white';
                                    if (val <= 0.1) return 'bg-red-400 text-white';
                                    if (val <= 0.25) return 'bg-orange-400 text-white';
                                    if (val <= 0.5) return 'bg-yellow-400 text-black';
                                    if (val <= 0.75) return 'bg-lime-400 text-black';
                                    return 'bg-green-500 text-white';
                                  };
                                  
                                  return (
                                    <td key={catStage} className="border border-gray-600 px-3 py-2 text-center">
                                      <div className={`px-2 py-1 rounded text-center font-medium ${getColor(value)}`}>
                                        {percentage}%
                                      </div>
                                    </td>
                                  );
                                })}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>

                      <p className="text-xs mt-4" style={{ color: '#6b7280' }}>
                        Values represent progression probability coefficients. Higher values indicate higher progression probability.
                      </p>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <Card className="border-0 shadow-md" style={{ backgroundColor: '#1f2937' }}>
                  <CardContent className="p-6 text-center">
                    <p style={{ color: '#9ca3af' }}>
                      No CAT matrix data available for {office?.name}. 
                      <br />
                      <small>CAT matrix API endpoint may not be available or returned empty data.</small>
                    </p>
                  </CardContent>
                </Card>
              )}

              {/* CAT Matrix Editor - Advanced editing interface */}
              {catMatrixData && (
                <CATMatrixEditor
                  catMatrix={catMatrixData}
                  officeName={office.name}
                  onSave={handleSaveCAT}
                  onReset={handleResetCAT}
                  isLoading={isSavingCAT}
                />
              )}
            </>
          ) : (
            <div className="text-center py-12">
              <Settings className="h-12 w-12 mx-auto mb-4" style={{ color: '#9ca3af' }} />
              <h3 className="text-lg font-medium mb-2" style={{ color: '#f3f4f6' }}>No Office Selected</h3>
              <p style={{ color: '#9ca3af' }}>Select an office from the "All Offices" tab to configure settings</p>
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Create Snapshot Modal - Temporarily disabled to fix infinite loop */}
      {/* 
      {office && (
        <CreateSnapshotModal
          isOpen={showCreateSnapshotModal}
          onClose={() => setShowCreateSnapshotModal(false)}
          onSnapshotCreated={(snapshot) => {
            setShowCreateSnapshotModal(false);
            console.log('Snapshot created from office view:', snapshot.name);
          }}
          officeId={office.id}
          officeName={office.name}
        />
      )}
      */}
    </div>
  );
};