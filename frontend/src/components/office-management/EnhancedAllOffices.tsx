import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Building2, Users, TrendingUp, MapPin, Eye, Edit } from 'lucide-react';
import { EnhancedDataTable, EnhancedColumnDef } from '../ui/enhanced-data-table';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { useToast } from '../ui/use-toast';
import { useOfficeStore } from '../../stores/officeStore';
import { OfficeConfig } from '../../types/office';

export const EnhancedAllOffices: React.FC = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  
  // Use the office store instead of local state
  const { offices, loading, error, loadOffices } = useOfficeStore();

  useEffect(() => {
    loadOffices();
  }, [loadOffices]);

  const handleRowClick = (office: OfficeConfig) => {
    navigate(`/offices/${office.id}`);
  };

  const handleEdit = (office: OfficeConfig) => {
    navigate(`/offices/${office.id}/edit`);
  };

  const getJourneyVariant = (journey: string) => {
    switch (journey.toLowerCase()) {
      case 'growth':
        return 'default';
      case 'stable':
        return 'secondary';
      case 'mature':
        return 'outline';
      default:
        return 'secondary';
    }
  };


  const columns: EnhancedColumnDef<OfficeConfig>[] = [
    {
      accessorKey: 'name',
      header: 'Office Name',
      enableSorting: true,
      cell: ({ getValue, row }) => {
        const value = getValue<string>();
        const record = row.original;
        return (
          <div className="flex items-center space-x-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
              <Building2 className="h-5 w-5 text-primary" />
            </div>
            <div>
              <div className="font-medium text-foreground">{value}</div>
              <div className="text-sm text-muted-foreground">
                <MapPin className="inline h-3 w-3 mr-1" />
                Office ID: {record.id}
              </div>
            </div>
          </div>
        );
      },
    },
    {
      accessorKey: 'journey',
      header: 'Journey Stage',
      enableSorting: true,
      cell: ({ getValue }) => {
        const value = getValue<string>();
        return <Badge variant={getJourneyVariant(value)}>{value}</Badge>;
      },
    },
    {
      accessorKey: 'total_fte',
      header: 'Total Headcount',
      enableSorting: true,
      cell: ({ getValue }) => {
        const value = getValue<number>();
        return (
          <div className="flex items-center space-x-2">
            <Users className="h-4 w-4 text-muted-foreground" />
            <span className="font-medium">{value} FTE</span>
          </div>
        );
      },
    },
    {
      accessorKey: 'economic_parameters',
      header: 'Economic Metrics',
      cell: ({ getValue }) => {
        const params = getValue<any>();
        return (
          <div className="space-y-1 text-sm">
            <div>CoL: {params?.cost_of_living?.toFixed(2) || 'N/A'}</div>
            <div>Market: {params?.market_multiplier?.toFixed(2) || 'N/A'}</div>
          </div>
        );
      },
    },
    {
      id: 'actions',
      header: 'Actions',
      enableSorting: false,
      cell: ({ row }) => {
        const record = row.original;
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm">
                Actions
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => navigate(`/offices/${record.id}`)}>
                <Eye className="mr-2 h-4 w-4" />
                View Details
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleEdit(record)}>
                <Edit className="mr-2 h-4 w-4" />
                Edit Office
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ];

  // Calculate summary stats
  const totalOffices = offices.length;
  const totalHeadcount = offices.reduce((sum, office) => sum + office.total_fte, 0);
  const avgHeadcount = totalOffices > 0 ? Math.round(totalHeadcount / totalOffices) : 0;

  const headerActions = (
    <div className="flex items-center gap-2">
      <Button onClick={() => navigate('/offices/new')}>
        <Building2 className="mr-2 h-4 w-4" />
        Add Office
      </Button>
    </div>
  );

  if (error) {
    return (
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Error Loading Offices</CardTitle>
            <CardDescription>{error}</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => loadOffices()}>Retry</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Debug Display */}
      <div className="p-4 bg-gray-100 rounded">
        <h3>Debug: Office Data</h3>
        {offices.slice(0, 3).map(office => (
          <div key={office.id}>
            {office.name}: {office.total_fte || 0} FTE ({office.journey})
          </div>
        ))}
      </div>
      
      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Offices</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalOffices}</div>
            <p className="text-xs text-muted-foreground">
              Office locations
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Headcount</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalHeadcount.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              Full-time equivalents
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Size</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{avgHeadcount}</div>
            <p className="text-xs text-muted-foreground">
              FTE per office
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Offices Table */}
      <EnhancedDataTable
        data={offices}
        columns={columns}
        loading={loading}
        searchable={true}
        searchPlaceholder="Search offices..."
        searchColumn="name"
        enableSelection={false}
        onRowClick={handleRowClick}
        enablePagination={true}
        pageSize={10}
        emptyMessage="No offices found. Add your first office to get started."
      />
    </div>
  );
};