/**
 * Financial Planning Table - Clean Minimalistic Dark Mode
 * 
 * Compact, readable table with minimal colors and clean design
 * Salary and pricing planning - Focus on readability and modern minimal aesthetics
 */
import React, { useState, useCallback, useMemo } from 'react';
import { Badge } from '../../ui/badge';
import { Button } from '../../ui/button';
import { Input } from '../../ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../ui/table';
import { cn } from '../../../lib/utils';
import { DollarSign, Euro, Percent } from 'lucide-react';
import type { OfficeConfig } from '../../../types/office';

interface FinancialPlanningTableProps {
  office: OfficeConfig;
  year: number;
  onDataChange: () => void;
}

interface FinancialData {
  role: string;
  level: string;
  category: 'salary' | 'pricing';
  q1: number;
  q2: number;
  q3: number;
  q4: number;
  average: number;
}

// Clean mock data matching the expected format
const createMockFinancialData = (): FinancialData[] => {
  const data: FinancialData[] = [];
  
  // Consultant levels A, B, C with both salary and pricing
  ['A', 'B', 'C'].forEach(level => {
    // Salary data (in thousands EUR)
    data.push({
      role: 'Consultant',
      level,
      category: 'salary',
      q1: level === 'A' ? 45 : level === 'B' ? 55 : 75,
      q2: level === 'A' ? 46 : level === 'B' ? 56 : 76,
      q3: level === 'A' ? 47 : level === 'B' ? 57 : 77,
      q4: level === 'A' ? 48 : level === 'B' ? 58 : 78,
      average: 0
    });
    
    // Pricing data (EUR per hour)
    data.push({
      role: 'Consultant',
      level,
      category: 'pricing',
      q1: level === 'A' ? 85 : level === 'B' ? 105 : 135,
      q2: level === 'A' ? 87 : level === 'B' ? 107 : 137,
      q3: level === 'A' ? 89 : level === 'B' ? 109 : 139,
      q4: level === 'A' ? 91 : level === 'B' ? 111 : 141,
      average: 0
    });
  });

  // Other roles (only salary, no pricing)
  ['Sales', 'Recruitment', 'Operations'].forEach(role => {
    // Salary data
    data.push({
      role,
      level: '',
      category: 'salary',
      q1: role === 'Sales' ? 52 : role === 'Recruitment' ? 48 : 42,
      q2: role === 'Sales' ? 53 : role === 'Recruitment' ? 49 : 43,
      q3: role === 'Sales' ? 54 : role === 'Recruitment' ? 50 : 44,
      q4: role === 'Sales' ? 55 : role === 'Recruitment' ? 51 : 45,
      average: 0
    });
  });

  // Calculate averages
  data.forEach(item => {
    item.average = (item.q1 + item.q2 + item.q3 + item.q4) / 4;
  });

  return data;
};

export const FinancialPlanningTable: React.FC<FinancialPlanningTableProps> = ({
  office,
  year,
  onDataChange
}) => {
  const [data, setData] = useState<FinancialData[]>(() => createMockFinancialData());

  const handleValueChange = useCallback((index: number, quarter: 'q1' | 'q2' | 'q3' | 'q4', value: string) => {
    const numValue = parseFloat(value) || 0;
    setData(prev => {
      const newData = [...prev];
      newData[index] = {
        ...newData[index],
        [quarter]: numValue,
        average: quarter === 'q1' ? (numValue + newData[index].q2 + newData[index].q3 + newData[index].q4) / 4 :
                 quarter === 'q2' ? (newData[index].q1 + numValue + newData[index].q3 + newData[index].q4) / 4 :
                 quarter === 'q3' ? (newData[index].q1 + newData[index].q2 + numValue + newData[index].q4) / 4 :
                 (newData[index].q1 + newData[index].q2 + newData[index].q3 + numValue) / 4
      };
      return newData;
    });
    onDataChange();
  }, [onDataChange]);

  const summaryData = useMemo(() => {
    const salaries = data.filter(item => item.category === 'salary');
    const pricing = data.filter(item => item.category === 'pricing');
    
    const avgSalary = salaries.reduce((sum, item) => sum + item.average, 0) / salaries.length;
    const avgPricing = pricing.length > 0 ? pricing.reduce((sum, item) => sum + item.average, 0) / pricing.length : 0;
    
    return {
      salary: {
        q1: salaries.reduce((sum, item) => sum + item.q1, 0) / salaries.length,
        q2: salaries.reduce((sum, item) => sum + item.q2, 0) / salaries.length,
        q3: salaries.reduce((sum, item) => sum + item.q3, 0) / salaries.length,
        q4: salaries.reduce((sum, item) => sum + item.q4, 0) / salaries.length,
        average: avgSalary
      },
      pricing: {
        q1: pricing.length > 0 ? pricing.reduce((sum, item) => sum + item.q1, 0) / pricing.length : 0,
        q2: pricing.length > 0 ? pricing.reduce((sum, item) => sum + item.q2, 0) / pricing.length : 0,
        q3: pricing.length > 0 ? pricing.reduce((sum, item) => sum + item.q3, 0) / pricing.length : 0,
        q4: pricing.length > 0 ? pricing.reduce((sum, item) => sum + item.q4, 0) / pricing.length : 0,
        average: avgPricing
      },
      margin: avgPricing > 0 ? ((avgPricing * 1800) - (avgSalary * 1000)) / (avgPricing * 1800) * 100 : 0 // Rough margin calculation
    };
  }, [data]);

  return (
    <div className="financial-planning-table space-y-4 p-4" style={{ backgroundColor: '#111827' }}>
      {/* Clean Header */}
      <div className="flex items-center justify-between pb-2">
        <div className="flex items-center gap-2">
          <DollarSign className="h-4 w-4" style={{ color: '#9ca3af' }} />
          <h3 className="text-base font-medium" style={{ color: '#f3f4f6' }}>
            Plan quarterly salary and pricing by role and level for {office.name} {year}
          </h3>
        </div>
        <Badge variant="outline" className="text-xs" style={{ backgroundColor: '#1f2937', color: '#d1d5db', borderColor: '#4b5563' }}>
          <Percent className="h-3 w-3 mr-1" style={{ color: '#9ca3af' }} />
          Margin: ~{summaryData.margin.toFixed(1)}%
        </Badge>
      </div>

      {/* Summary Cards - Clean & Minimal */}
      <div className="grid grid-cols-2 gap-3">
        <div className="p-3 rounded-lg" style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
          <div className="flex items-center gap-2 mb-1">
            <Euro className="h-3 w-3" style={{ color: '#9ca3af' }} />
            <span className="text-xs font-medium" style={{ color: '#d1d5db' }}>Average Salary</span>
          </div>
          <div className="text-lg font-semibold" style={{ color: '#f3f4f6' }}>€{summaryData.salary.average.toFixed(0)}k</div>
          <div className="text-xs" style={{ color: '#9ca3af' }}>
            Q1: €{summaryData.salary.q1.toFixed(0)}k | Q2: €{summaryData.salary.q2.toFixed(0)}k | Q3: €{summaryData.salary.q3.toFixed(0)}k | Q4: €{summaryData.salary.q4.toFixed(0)}k
          </div>
        </div>

        <div className="p-3 rounded-lg" style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
          <div className="flex items-center gap-2 mb-1">
            <DollarSign className="h-3 w-3" style={{ color: '#9ca3af' }} />
            <span className="text-xs font-medium" style={{ color: '#d1d5db' }}>Average Pricing</span>
          </div>
          <div className="text-lg font-semibold" style={{ color: '#f3f4f6' }}>€{summaryData.pricing.average.toFixed(0)}/h</div>
          <div className="text-xs" style={{ color: '#9ca3af' }}>
            Q1: €{summaryData.pricing.q1.toFixed(0)} | Q2: €{summaryData.pricing.q2.toFixed(0)} | Q3: €{summaryData.pricing.q3.toFixed(0)} | Q4: €{summaryData.pricing.q4.toFixed(0)}
          </div>
        </div>
      </div>

      {/* Clean Table */}
      <div className="rounded-lg overflow-hidden" style={{ border: '1px solid #374151' }}>
        <Table>
          <TableHeader>
            <TableRow style={{ backgroundColor: '#1f2937', borderBottom: '1px solid #374151' }}>
              <TableHead className="text-xs font-medium w-24" style={{ color: '#d1d5db' }}>Role/Level</TableHead>
              <TableHead className="text-xs font-medium w-20" style={{ color: '#d1d5db' }}>Type</TableHead>
              <TableHead className="text-xs font-medium text-center w-16" style={{ color: '#d1d5db' }}>Q1</TableHead>
              <TableHead className="text-xs font-medium text-center w-16" style={{ color: '#d1d5db' }}>Q2</TableHead>
              <TableHead className="text-xs font-medium text-center w-16" style={{ color: '#d1d5db' }}>Q3</TableHead>
              <TableHead className="text-xs font-medium text-center w-16" style={{ color: '#d1d5db' }}>Q4</TableHead>
              <TableHead className="text-xs font-medium text-center w-16" style={{ color: '#d1d5db' }}>Avg</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((item, index) => (
              <TableRow 
                key={`${item.role}-${item.level}-${item.category}`}
                style={{ 
                  backgroundColor: item.category === 'pricing' ? '#0f172a' : '#111827',
                  borderBottom: '1px solid #374151',
                  transition: 'background-color 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#1f2937';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = item.category === 'pricing' ? '#0f172a' : '#111827';
                }}
              >
                <TableCell className="text-xs font-medium" style={{ color: '#f3f4f6' }}>
                  {item.role} {item.level}
                </TableCell>
                <TableCell>
                  <Badge 
                    variant="outline" 
                    className="text-xs px-2 py-0.5"
                    style={{ 
                      backgroundColor: '#374151', 
                      color: '#d1d5db', 
                      borderColor: '#4b5563' 
                    }}
                  >
                    {item.category === 'salary' ? 'Salary' : 'Pricing'}
                  </Badge>
                </TableCell>
                {(['q1', 'q2', 'q3', 'q4'] as const).map(quarter => (
                  <TableCell key={quarter} className="text-center">
                    <Input
                      type="number"
                      value={item[quarter]}
                      onChange={(e) => handleValueChange(index, quarter, e.target.value)}
                      className="w-14 h-7 text-xs text-center"
                      style={{
                        border: '1px solid #374151',
                        backgroundColor: '#111827',
                        color: '#f3f4f6'
                      }}
                      min="0"
                      step={item.category === 'salary' ? "1" : "0.5"}
                    />
                  </TableCell>
                ))}
                <TableCell className="text-center">
                  <span className="text-xs font-medium" style={{ color: '#f3f4f6' }}>
                    {item.category === 'salary' ? `€${item.average.toFixed(0)}k` : `€${item.average.toFixed(0)}`}
                  </span>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Clean Action Bar */}
      <div className="flex items-center justify-between pt-2" style={{ borderTop: '1px solid #374151' }}>
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            className="h-7 px-3 text-xs"
            style={{
              border: '1px solid #374151',
              backgroundColor: '#1f2937',
              color: '#d1d5db'
            }}
          >
            Reset All
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            className="h-7 px-3 text-xs"
            style={{
              border: '1px solid #374151',
              backgroundColor: '#1f2937',
              color: '#d1d5db'
            }}
          >
            Apply Market Rates
          </Button>
        </div>
        
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            className="h-7 px-3 text-xs"
            style={{
              border: '1px solid #374151',
              backgroundColor: '#1f2937',
              color: '#d1d5db'
            }}
          >
            Export
          </Button>
          <Button 
            size="sm" 
            className="h-7 px-3 text-xs"
            style={{
              backgroundColor: '#3b82f6',
              color: '#ffffff',
              border: 'none'
            }}
          >
            Save Changes
          </Button>
        </div>
      </div>
    </div>
  );
};