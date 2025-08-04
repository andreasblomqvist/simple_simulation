/**
 * Workforce Planning Table - Clean Minimalistic Dark Mode
 * 
 * Compact, readable table with minimal colors and clean design
 * Stockholm Office 2025 - Focus on readability and modern minimal aesthetics
 */
import React, { useState, useCallback, useMemo } from 'react';
import { Badge } from '../../ui/badge';
import { Button } from '../../ui/button';
import { Input } from '../../ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../ui/table';
import { cn } from '../../../lib/utils';
import { Users, Plus, Minus } from 'lucide-react';
import type { OfficeConfig } from '../../../types/office';

interface WorkforcePlanningTableProps {
  office: OfficeConfig;
  year: number;
  onDataChange: () => void;
}

interface WorkforceData {
  role: string;
  level: string;
  category: 'recruitment' | 'churn';
  q1: number;
  q2: number;
  q3: number;
  q4: number;
  total: number;
}

// Clean mock data matching the expected format
const createMockWorkforceData = (): WorkforceData[] => {
  const data: WorkforceData[] = [];
  
  // Consultant levels A, B, C
  ['A', 'B', 'C'].forEach(level => {
    // Recruitment
    data.push({
      role: 'Consultant',
      level,
      category: 'recruitment',
      q1: level === 'A' ? 2 : level === 'B' ? 1 : 3,
      q2: level === 'A' ? 3 : level === 'B' ? 2 : 2,
      q3: level === 'A' ? 2 : level === 'B' ? 1 : 4,
      q4: level === 'A' ? 1 : level === 'B' ? 2 : 2,
      total: 0
    });
    
    // Churn
    data.push({
      role: 'Consultant',
      level,
      category: 'churn',
      q1: level === 'A' ? 1 : level === 'B' ? 0 : 2,
      q2: level === 'A' ? 0 : level === 'B' ? 1 : 1,
      q3: level === 'A' ? 1 : level === 'B' ? 0 : 2,
      q4: level === 'A' ? 0 : level === 'B' ? 1 : 1,
      total: 0
    });
  });

  // Other roles
  ['Sales', 'Recruitment', 'Operations'].forEach(role => {
    // Recruitment
    data.push({
      role,
      level: '',
      category: 'recruitment',
      q1: role === 'Sales' ? 1 : role === 'Recruitment' ? 0 : 1,
      q2: role === 'Sales' ? 2 : role === 'Recruitment' ? 1 : 0,
      q3: role === 'Sales' ? 1 : role === 'Recruitment' ? 0 : 1,
      q4: role === 'Sales' ? 0 : role === 'Recruitment' ? 1 : 0,
      total: 0
    });
    
    // Churn
    data.push({
      role,
      level: '',
      category: 'churn',
      q1: 0,
      q2: role === 'Sales' ? 1 : 0,
      q3: 0,
      q4: role === 'Recruitment' ? 0 : 0,
      total: 0
    });
  });

  // Calculate totals
  data.forEach(item => {
    item.total = item.q1 + item.q2 + item.q3 + item.q4;
  });

  return data;
};

export const WorkforcePlanningTable: React.FC<WorkforcePlanningTableProps> = ({
  office,
  year,
  onDataChange
}) => {
  const [data, setData] = useState<WorkforceData[]>(() => createMockWorkforceData());

  const handleValueChange = useCallback((index: number, quarter: 'q1' | 'q2' | 'q3' | 'q4', value: string) => {
    const numValue = parseInt(value) || 0;
    setData(prev => {
      const newData = [...prev];
      newData[index] = {
        ...newData[index],
        [quarter]: numValue,
        total: quarter === 'q1' ? numValue + newData[index].q2 + newData[index].q3 + newData[index].q4 :
               quarter === 'q2' ? newData[index].q1 + numValue + newData[index].q3 + newData[index].q4 :
               quarter === 'q3' ? newData[index].q1 + newData[index].q2 + numValue + newData[index].q4 :
               newData[index].q1 + newData[index].q2 + newData[index].q3 + numValue
      };
      return newData;
    });
    onDataChange();
  }, [onDataChange]);

  const summaryData = useMemo(() => {
    const recruitment = data.filter(item => item.category === 'recruitment');
    const churn = data.filter(item => item.category === 'churn');
    
    const totalRecruitment = recruitment.reduce((sum, item) => sum + item.total, 0);
    const totalChurn = churn.reduce((sum, item) => sum + item.total, 0);
    
    return {
      recruitment: {
        q1: recruitment.reduce((sum, item) => sum + item.q1, 0),
        q2: recruitment.reduce((sum, item) => sum + item.q2, 0),
        q3: recruitment.reduce((sum, item) => sum + item.q3, 0),
        q4: recruitment.reduce((sum, item) => sum + item.q4, 0),
        total: totalRecruitment
      },
      churn: {
        q1: churn.reduce((sum, item) => sum + item.q1, 0),
        q2: churn.reduce((sum, item) => sum + item.q2, 0),
        q3: churn.reduce((sum, item) => sum + item.q3, 0),
        q4: churn.reduce((sum, item) => sum + item.q4, 0),
        total: totalChurn
      },
      net: totalRecruitment - totalChurn
    };
  }, [data]);

  return (
    <div className="workforce-planning-table space-y-4 p-4" style={{ backgroundColor: '#111827' }}>
      {/* Clean Header */}
      <div className="flex items-center justify-between pb-2">
        <div className="flex items-center gap-2">
          <Users className="h-4 w-4" style={{ color: '#9ca3af' }} />
          <h3 className="text-base font-medium" style={{ color: '#f3f4f6' }}>
            Plan quarterly recruitment and churn by role and level for {office.name} {year}
          </h3>
        </div>
        <Badge variant="outline" className="text-xs" style={{ backgroundColor: '#1f2937', color: '#d1d5db', borderColor: '#4b5563' }}>
          <Plus className="h-3 w-3 mr-1" style={{ color: '#9ca3af' }} />
          Net: +{summaryData.net}
        </Badge>
      </div>

      {/* Summary Cards - Force Dark Mode */}
      <div className="grid grid-cols-2 gap-3">
        <div className="p-3 rounded-lg" style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
          <div className="flex items-center gap-2 mb-1">
            <Plus className="h-3 w-3" style={{ color: '#9ca3af' }} />
            <span className="text-xs font-medium" style={{ color: '#d1d5db' }}>Total Recruitment</span>
          </div>
          <div className="text-lg font-semibold" style={{ color: '#f3f4f6' }}>{summaryData.recruitment.total}</div>
          <div className="text-xs" style={{ color: '#9ca3af' }}>
            Q1: {summaryData.recruitment.q1} | Q2: {summaryData.recruitment.q2} | Q3: {summaryData.recruitment.q3} | Q4: {summaryData.recruitment.q4}
          </div>
        </div>

        <div className="p-3 rounded-lg" style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
          <div className="flex items-center gap-2 mb-1">
            <Minus className="h-3 w-3" style={{ color: '#9ca3af' }} />
            <span className="text-xs font-medium" style={{ color: '#d1d5db' }}>Total Churn</span>
          </div>
          <div className="text-lg font-semibold" style={{ color: '#f3f4f6' }}>{summaryData.churn.total}</div>
          <div className="text-xs" style={{ color: '#9ca3af' }}>
            Q1: {summaryData.churn.q1} | Q2: {summaryData.churn.q2} | Q3: {summaryData.churn.q3} | Q4: {summaryData.churn.q4}
          </div>
        </div>
      </div>

      {/* Force Dark Table */}
      <div className="rounded-lg overflow-hidden" style={{ border: '1px solid #374151' }}>
        <Table style={{ backgroundColor: '#111827' }}>
          <TableHeader>
            <TableRow style={{ backgroundColor: '#1f2937', borderBottom: '1px solid #374151' }}>
              <TableHead className="text-xs font-medium text-center w-24" style={{ color: '#d1d5db' }}>Role/Level</TableHead>
              <TableHead className="text-xs font-medium text-center w-20" style={{ color: '#d1d5db' }}>Type</TableHead>
              <TableHead className="text-xs font-medium text-center w-16" style={{ color: '#d1d5db' }}>Q1</TableHead>
              <TableHead className="text-xs font-medium text-center w-16" style={{ color: '#d1d5db' }}>Q2</TableHead>
              <TableHead className="text-xs font-medium text-center w-16" style={{ color: '#d1d5db' }}>Q3</TableHead>
              <TableHead className="text-xs font-medium text-center w-16" style={{ color: '#d1d5db' }}>Q4</TableHead>
              <TableHead className="text-xs font-medium text-center w-16" style={{ color: '#d1d5db' }}>Total</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((item, index) => (
              <TableRow 
                key={`${item.role}-${item.level}-${item.category}`}
                style={{ backgroundColor: '#111827', borderBottom: '1px solid #1f2937' }}
                className="hover:bg-opacity-80"
              >
                <TableCell className="text-xs font-medium" style={{ color: '#f3f4f6' }}>
                  {item.role} {item.level}
                </TableCell>
                <TableCell>
                  <Badge 
                    variant="outline" 
                    className="text-xs px-2 py-0.5"
                    style={{ backgroundColor: '#1f2937', color: '#d1d5db', borderColor: '#4b5563' }}
                  >
                    {item.category === 'recruitment' ? 'Recruitment' : 'Churn'}
                  </Badge>
                </TableCell>
                {(['q1', 'q2', 'q3', 'q4'] as const).map(quarter => (
                  <TableCell key={quarter} className="text-center">
                    <Input
                      type="number"
                      value={item[quarter]}
                      onChange={(e) => handleValueChange(index, quarter, e.target.value)}
                      className="w-12 h-7 text-xs text-center"
                      style={{ backgroundColor: '#1f2937', borderColor: '#4b5563', color: '#f3f4f6' }}
                      min="0"
                    />
                  </TableCell>
                ))}
                <TableCell className="text-center">
                  <span className="text-xs font-medium" style={{ color: '#f3f4f6' }}>
                    {item.total}
                  </span>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Dark Action Bar */}
      <div className="flex items-center justify-between pt-2 border-t border-gray-700">
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="h-7 px-3 text-xs bg-gray-800 text-gray-300 border-gray-600 hover:bg-gray-700">
            Reset All
          </Button>
          <Button variant="outline" size="sm" className="h-7 px-3 text-xs bg-gray-800 text-gray-300 border-gray-600 hover:bg-gray-700">
            Copy Previous Year
          </Button>
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="h-7 px-3 text-xs bg-gray-800 text-gray-300 border-gray-600 hover:bg-gray-700">
            Export
          </Button>
          <Button size="sm" className="h-7 px-3 text-xs bg-gray-100 text-gray-900 hover:bg-gray-200">
            Save Changes
          </Button>
        </div>
      </div>
    </div>
  );
};