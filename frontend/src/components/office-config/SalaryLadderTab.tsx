/**
 * Salary Ladder Tab Component
 * Displays salary KPIs and compensation structure
 */
import React from 'react';
import { OfficeConfig, STANDARD_LEVELS, STANDARD_ROLES } from '../../types/office';
import { KPICard } from './KPICard';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Badge } from '../ui/badge';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { DollarSign, TrendingUp, Wallet, PiggyBank } from 'lucide-react';

interface SalaryLadderTabProps {
  office: OfficeConfig;
}

export const SalaryLadderTab: React.FC<SalaryLadderTabProps> = ({ office }) => {
  // Extract salary data from office configuration
  const getSalaryData = () => {
    if (!office?.roles) return [];

    const salaryData: Array<{
      role: string;
      level: string;
      salary: number;
      isLeveled: boolean;
    }> = [];

    Object.entries(office.roles).forEach(([role, roleData]) => {
      if (typeof roleData === 'object' && roleData !== null) {
        // Check if this is a leveled role (has level structure)
        const firstKey = Object.keys(roleData)[0];
        const firstValue = roleData[firstKey];
        
        if (typeof firstValue === 'object' && firstValue !== null && 'salary_1' in firstValue) {
          // Leveled role - extract salary from first month
          Object.entries(roleData).forEach(([level, levelData]) => {
            if (typeof levelData === 'object' && levelData !== null && 'salary_1' in levelData) {
              salaryData.push({
                role,
                level,
                salary: (levelData as any).salary_1 || 0,
                isLeveled: true
              });
            }
          });
        } else if (typeof firstValue === 'number') {
          // Flat role - might have direct salary data
          // For now, we'll skip flat roles as they don't typically have salary_1 format
        }
      }
    });

    return salaryData.sort((a, b) => {
      // Sort by role first, then by level
      if (a.role !== b.role) {
        return STANDARD_ROLES.indexOf(a.role as any) - STANDARD_ROLES.indexOf(b.role as any);
      }
      return STANDARD_LEVELS.indexOf(a.level as any) - STANDARD_LEVELS.indexOf(b.level as any);
    });
  };

  // Calculate salary KPIs
  const getSalaryKPIs = () => {
    const salaryData = getSalaryData();
    
    const salaryByRole = STANDARD_ROLES.reduce((acc, role) => {
      const roleSalaries = salaryData.filter(item => item.role === role);
      const totalSalary = roleSalaries.reduce((sum, item) => sum + item.salary, 0);
      acc[role] = totalSalary;
      return acc;
    }, {} as Record<string, number>);

    return {
      consultant: salaryByRole['Consultant'] || 0,
      sales: salaryByRole['Sales'] || 0,
      recruitment: salaryByRole['Recruitment'] || 0,
      operations: salaryByRole['Operations'] || 0
    };
  };

  // Format currency
  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  // Get salary range for a role
  const getSalaryRange = (role: string) => {
    const roleSalaries = getSalaryData()
      .filter(item => item.role === role)
      .map(item => item.salary)
      .filter(salary => salary > 0);
    
    if (roleSalaries.length === 0) return { min: 0, max: 0 };
    
    return {
      min: Math.min(...roleSalaries),
      max: Math.max(...roleSalaries)
    };
  };

  const salaryData = getSalaryData();
  const salaryKPIs = getSalaryKPIs();

  if (salaryData.length === 0) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {STANDARD_ROLES.slice(0, 4).map((role) => (
            <KPICard
              key={role}
              title={`${role} Total`}
              value={0}
              subtitle="No salary data"
              variant="default"
            />
          ))}
        </div>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="h-5 w-5" />
              Salary Ladder
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8 text-muted-foreground">
              <Wallet className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No salary data available</p>
              <p className="text-sm mt-1">Office configuration does not contain salary information</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Salary KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Consultant Total"
          value={formatCurrency(salaryKPIs.consultant)}
          subtitle={`Range: ${formatCurrency(getSalaryRange('Consultant').min)} - ${formatCurrency(getSalaryRange('Consultant').max)}`}
          variant={salaryKPIs.consultant > 0 ? 'success' : 'default'}
        />
        <KPICard
          title="Sales Total"
          value={formatCurrency(salaryKPIs.sales)}
          subtitle={`Range: ${formatCurrency(getSalaryRange('Sales').min)} - ${formatCurrency(getSalaryRange('Sales').max)}`}
          variant={salaryKPIs.sales > 0 ? 'success' : 'default'}
        />
        <KPICard
          title="Recruitment Total"
          value={formatCurrency(salaryKPIs.recruitment)}
          subtitle={`Range: ${formatCurrency(getSalaryRange('Recruitment').min)} - ${formatCurrency(getSalaryRange('Recruitment').max)}`}
          variant={salaryKPIs.recruitment > 0 ? 'success' : 'default'}
        />
        <KPICard
          title="Operations Total"
          value={formatCurrency(salaryKPIs.operations)}
          subtitle={`Range: ${formatCurrency(getSalaryRange('Operations').min)} - ${formatCurrency(getSalaryRange('Operations').max)}`}
          variant={salaryKPIs.operations > 0 ? 'success' : 'default'}
        />
      </div>

      {/* Salary Ladder Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            Salary Ladder
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Role</TableHead>
                <TableHead>Level</TableHead>
                <TableHead className="text-right">Base Salary</TableHead>
                <TableHead className="text-right">Monthly</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {salaryData.map((item, index) => (
                <TableRow key={`${item.role}-${item.level}`}>
                  <TableCell className="font-medium">{item.role}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{item.level}</Badge>
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {formatCurrency(item.salary)}
                  </TableCell>
                  <TableCell className="text-right font-mono text-muted-foreground">
                    {formatCurrency(item.salary / 12)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Salary Analysis */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Salary Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h4 className="font-medium">Compensation Overview</h4>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• {salaryData.length} salary bands configured</li>
                <li>• {STANDARD_ROLES.filter(role => getSalaryRange(role).max > 0).length} roles with salary data</li>
                <li>• Salaries range from {formatCurrency(Math.min(...salaryData.map(s => s.salary)))} to {formatCurrency(Math.max(...salaryData.map(s => s.salary)))}</li>
                <li>• Average progression steps: {Math.round(salaryData.length / STANDARD_ROLES.length)}</li>
              </ul>
            </div>
            <div className="space-y-3">
              <h4 className="font-medium">Market Position</h4>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• Consultant salaries competitive for {office.journey} office</li>
                <li>• Clear progression path across levels</li>
                <li>• Regular salary reviews recommended</li>
                <li>• Consider market benchmarking for optimization</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};