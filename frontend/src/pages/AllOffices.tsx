import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { EnhancedDataTable, EnhancedColumnDef } from '../components/ui/enhanced-data-table';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Building2, Users, TrendingUp } from 'lucide-react';

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

export function AllOffices() {
  const navigate = useNavigate();
  const [offices, setOffices] = useState<Office[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedRowKeys, setExpandedRowKeys] = useState<string[]>([]);

  useEffect(() => {
    fetch('/api/offices')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch offices');
        return res.json();
      })
      .then(data => {
        console.log('[DEBUG] Data received from /api/offices:', data);
        setOffices(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const columns: EnhancedColumnDef<Office>[] = [
    {
      accessorKey: 'name',
      header: 'Office',
      cell: ({ row }) => (
        <Button
          variant="link"
          className="p-0 h-auto font-semibold text-blue-600 hover:text-blue-800"
          onClick={() => navigate(`/offices/${row.original.id}`)}
        >
          <Building2 className="mr-2 h-4 w-4" />
          {row.original.name}
        </Button>
      ),
    },
    {
      accessorKey: 'journey',
      header: 'Journey',
      cell: ({ row }) => (
        <Badge variant="secondary">{row.original.journey}</Badge>
      ),
    },
    {
      accessorKey: 'total_fte',
      header: 'Total FTE',
      cellType: 'default',
      cell: ({ row }) => (
        <div className="flex items-center">
          <Users className="mr-2 h-4 w-4 text-muted-foreground" />
          <span className="font-mono">{row.original.total_fte}</span>
        </div>
      ),
    },
    {
      id: 'cost_of_living',
      header: 'Cost of Living',
      cell: ({ row }) => {
        const col = row.original.economic_parameters?.cost_of_living;
        return col ? col.toFixed(2) : 'N/A';
      },
    },
    {
      id: 'market_multiplier', 
      header: 'Market Multiplier',
      cell: ({ row }) => {
        const mm = row.original.economic_parameters?.market_multiplier;
        return mm ? mm.toFixed(2) : 'N/A';
      },
    },
  ];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5" />
            All Offices
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* Filters */}
          <div className="flex gap-4 mb-6">
            <Select defaultValue="Company">
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Company">Company</SelectItem>
              </SelectContent>
            </Select>
            
            <Select defaultValue="Journey">
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Journey">Journey</SelectItem>
              </SelectContent>
            </Select>
            
            <Select defaultValue="Sort: Name">
              <SelectTrigger className="w-36">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Sort: Name">Sort: Name</SelectItem>
                <SelectItem value="Sort: Headcount">Sort: Headcount</SelectItem>
                <SelectItem value="Sort: Growth">Sort: Growth</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          {error && (
            <div className="text-red-600 mb-4">{error}</div>
          )}

          <EnhancedDataTable
            columns={columns}
            data={offices}
            loading={loading}
            searchable={true}
            searchPlaceholder="Search offices..."
            searchColumn="name"
            enableSelection={false}
            enableExpansion={true}
            enablePagination={true}
            pageSize={8}
            bordered={true}
            striped={true}
            onRowClick={(office) => navigate(`/offices/${office.id}`)}
            className="offices-table"
          />
        </CardContent>
      </Card>
    </div>
  );
} 