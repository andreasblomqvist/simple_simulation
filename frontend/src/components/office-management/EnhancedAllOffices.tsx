import React, { useEffect, useState } from 'react';
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

interface Office {
  id: string;
  name: string;
  total_fte: number;
  journey: string;
  roles: Record<string, Record<string, any>>;
  economic_parameters?: {
    cost_of_living: number;
    market_multiplier: number;
    tax_rate: number;
  };
}

export const EnhancedAllOffices: React.FC = () => {
  const navigate = useNavigate();
  const [offices, setOffices] = useState<Office[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    loadOffices();
  }, []);

  const loadOffices = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/offices');
      if (!response.ok) throw new Error('Failed to fetch offices');
      const data = await response.json();
      setOffices(data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load offices: ' + (error as Error).message,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRowClick = (office: Office) => {
    navigate(`/offices/${office.id}`);
  };

  const handleEdit = (office: Office) => {
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

  const getTotalRoles = (roles: Record<string, Record<string, any>>) => {
    return Object.keys(roles).length;
  };

  const columns: EnhancedColumnDef<Office>[] = [
    {
      key: 'name',
      title: 'Office Name',
      sortable: true,
      render: (value: string, record: Office) => (
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
      ),
    },
    {
      key: 'journey',
      title: 'Journey Stage',
      sortable: true,
      render: (value: string) => (
        <Badge variant={getJourneyVariant(value)}>{value}</Badge>
      ),
    },
    {
      key: 'total_fte',
      title: 'Total Headcount',
      sortable: true,
      render: (value: number) => (
        <div className="flex items-center space-x-2">
          <Users className="h-4 w-4 text-muted-foreground" />
          <span className="font-medium">{value} FTE</span>
        </div>
      ),
    },
    {
      key: 'roles',
      title: 'Role Types',
      render: (roles: Record<string, Record<string, any>>) => (
        <div className="text-sm text-muted-foreground">
          {getTotalRoles(roles)} role types
        </div>
      ),
    },
    {
      key: 'economic_parameters',
      title: 'Economic Metrics',
      render: (params: any) => (
        <div className="space-y-1 text-sm">
          <div>CoL: {params?.cost_of_living?.toFixed(2) || 'N/A'}</div>
          <div>Market: {params?.market_multiplier?.toFixed(2) || 'N/A'}</div>
        </div>
      ),
    },
    {
      key: 'actions',
      title: 'Actions',
      width: '120px',
      render: (_, record: Office) => (
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
      ),
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

  return (
    <div className="space-y-6">
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
        title="Office Management"
        description="Manage your office locations and workforce data"
        searchable
        searchPlaceholder="Search offices..."
        selectable={false}
        onRowClick={handleRowClick}
        pagination
        defaultPageSize={10}
        pageSizeOptions={[5, 10, 25, 50]}
        onRefresh={loadOffices}
        actions={headerActions}
        emptyMessage="No offices found. Add your first office to get started."
        getRowKey={(record) => record.id}
      />
    </div>
  );
};