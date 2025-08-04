import React, { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { 
  Building2, 
  Users, 
  UserCheck, 
  ShoppingCart, 
  Settings,
  TrendingUp,
  PieChart
} from 'lucide-react';
import type { OfficeConfig } from '../../types/office';

interface OfficeViewProps {
  office: OfficeConfig;
}

interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
}

const KPICard: React.FC<KPICardProps> = ({ title, value, subtitle, icon, trend }) => (
  <Card>
    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium">{title}</CardTitle>
      <div className="text-muted-foreground">{icon}</div>
    </CardHeader>
    <CardContent>
      <div className="text-2xl font-bold">{value}</div>
      {subtitle && <p className="text-xs text-muted-foreground">{subtitle}</p>}
      {trend && (
        <div className={`flex items-center text-xs ${trend.isPositive ? 'text-green-600' : 'text-red-600'}`}>
          <TrendingUp className={`h-3 w-3 mr-1 ${trend.isPositive ? '' : 'rotate-180'}`} />
          {trend.value}%
        </div>
      )}
    </CardContent>
  </Card>
);

const PyramidChart: React.FC<{ data: { label: string; value: number; color: string }[] }> = ({ data }) => {
  const maxValue = Math.max(...data.map(d => d.value));
  
  return (
    <div className="flex flex-col items-center space-y-2">
      <h3 className="text-lg font-semibold mb-4">Journey Distribution</h3>
      <div className="flex flex-col items-center space-y-1">
        {data.map((item, index) => (
          <div key={item.label} className="flex items-center space-x-2">
            <div 
              className="h-6 rounded"
              style={{
                width: `${(item.value / maxValue) * 200}px`,
                backgroundColor: item.color,
                minWidth: '40px'
              }}
            />
            <span className="text-sm font-medium min-w-[60px]">{item.label}</span>
            <span className="text-sm text-muted-foreground">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export const OfficeView: React.FC<OfficeViewProps> = ({ office }) => {
  const officeStats = useMemo(() => {
    const roles = office.roles || {};
    
    // Calculate role counts
    const recruiters = Object.values(roles).reduce((sum, role) => {
      if (typeof role === 'object' && role !== null) {
        return sum + Object.values(role).reduce((roleSum, level) => {
          if (typeof level === 'object' && level !== null && 'fte' in level) {
            return roleSum + (level.fte || 0);
          }
          return roleSum;
        }, 0);
      }
      return sum;
    }, 0);

    const sales = roles.Sales ? Object.values(roles.Sales).reduce((sum, level) => {
      if (typeof level === 'object' && level !== null && 'fte' in level) {
        return sum + (level.fte || 0);
      }
      return sum;
    }, 0) : 0;

    const operations = roles.Operations ? Object.values(roles.Operations).reduce((sum, level) => {
      if (typeof level === 'object' && level !== null && 'fte' in level) {
        return sum + (level.fte || 0);
      }
      return sum;
    }, 0) : 0;

    const totalEmployees = office.total_fte || 0;
    
    // Calculate percentages
    const recruitersPercent = totalEmployees > 0 ? (recruiters / totalEmployees) * 100 : 0;
    const salesPercent = totalEmployees > 0 ? (sales / totalEmployees) * 100 : 0;
    const operationsPercent = totalEmployees > 0 ? (operations / totalEmployees) * 100 : 0;

    // Mock journey distribution (you'll need to get this from your data)
    const journeyDistribution = [
      { label: 'J1', value: 25, color: '#3B82F6' },
      { label: 'J2', value: 35, color: '#10B981' },
      { label: 'J3', value: 30, color: '#F59E0B' },
      { label: 'J4', value: 10, color: '#EF4444' }
    ];

    // Mock non-debit ratio (you'll need to calculate this from your data)
    const nonDebitRatio = 0.85; // 85%

    return {
      totalEmployees,
      recruiters,
      sales,
      operations,
      recruitersPercent,
      salesPercent,
      operationsPercent,
      journeyDistribution,
      nonDebitRatio
    };
  }, [office]);

  const populationData = useMemo(() => {
    const roles = office.roles || {};
    const data: Array<{ role: string; level: string; fte: number }> = [];

    Object.entries(roles).forEach(([roleName, roleData]) => {
      if (typeof roleData === 'object' && roleData !== null) {
        Object.entries(roleData).forEach(([levelName, levelData]) => {
          if (typeof levelData === 'object' && levelData !== null && 'fte' in levelData) {
            data.push({
              role: roleName,
              level: levelName,
              fte: levelData.fte || 0
            });
          }
        });
      }
    });

    return data.filter(item => item.fte > 0);
  }, [office]);

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Building2 className="h-8 w-8 text-blue-600" />
        <div>
          <h1 className="text-3xl font-bold">{office.name}</h1>
          <p className="text-muted-foreground">Office Overview</p>
        </div>
        <Badge variant="outline" className="ml-auto">
          {office.journey}
        </Badge>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <KPICard
          title="Total Employees"
          value={officeStats.totalEmployees}
          icon={<Users className="h-4 w-4" />}
        />
        <KPICard
          title="Recruiters"
          value={officeStats.recruiters}
          subtitle={`${officeStats.recruitersPercent.toFixed(1)}% of total`}
          icon={<UserCheck className="h-4 w-4" />}
        />
        <KPICard
          title="Sales"
          value={officeStats.sales}
          subtitle={`${officeStats.salesPercent.toFixed(1)}% of total`}
          icon={<ShoppingCart className="h-4 w-4" />}
        />
        <KPICard
          title="Operations"
          value={officeStats.operations}
          subtitle={`${officeStats.operationsPercent.toFixed(1)}% of total`}
          icon={<Settings className="h-4 w-4" />}
        />
        <KPICard
          title="Non-Debit Ratio"
          value={`${(officeStats.nonDebitRatio * 100).toFixed(1)}%`}
          icon={<PieChart className="h-4 w-4" />}
        />
      </div>

      {/* Journey Distribution and Population Table */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Journey Distribution Pyramid Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Journey Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <PyramidChart data={officeStats.journeyDistribution} />
          </CardContent>
        </Card>

        {/* Population Table */}
        <Card>
          <CardHeader>
            <CardTitle>Population by Role & Level</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Role</TableHead>
                  <TableHead>Level</TableHead>
                  <TableHead className="text-right">FTE</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {populationData.map((item, index) => (
                  <TableRow key={index}>
                    <TableCell className="font-medium">{item.role}</TableCell>
                    <TableCell>{item.level}</TableCell>
                    <TableCell className="text-right">{item.fte}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}; 