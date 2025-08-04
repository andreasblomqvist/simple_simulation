/**
 * Monthly Overview Table - Clean Minimalistic Dark Mode
 * 
 * Compact, readable table with minimal colors and clean design
 * Summary and validation - Focus on readability and modern minimal aesthetics
 */
import React, { useState, useMemo } from 'react';
import { Badge } from '../../ui/badge';
import { Button } from '../../ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../ui/table';
import { cn } from '../../../lib/utils';
import { BarChart3, TrendingUp, CheckCircle, AlertCircle } from 'lucide-react';
import type { OfficeConfig } from '../../../types/office';

interface MonthlyOverviewTableProps {
  office: OfficeConfig;
  year: number;
  onDataChange: () => void;
}

interface OverviewData {
  month: string;
  recruitment: number;
  churn: number;
  netChange: number;
  validationStatus: 'complete' | 'warning' | 'incomplete';
  completeness: number;
}

// Clean mock data matching the expected format
const createMockOverviewData = (): OverviewData[] => {
  const months = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
  ];

  return months.map((month, index) => {
    const recruitment = index < 6 ? 2 : index < 9 ? 3 : 1;
    const churn = index % 4 === 0 ? 1 : index % 6 === 0 ? 2 : 0;
    const netChange = recruitment - churn;
    const completeness = index < 3 ? 100 : index < 6 ? 85 : index < 9 ? 70 : 45;
    const validationStatus: 'complete' | 'warning' | 'incomplete' = 
      completeness === 100 ? 'complete' :
      completeness >= 80 ? 'warning' : 'incomplete';

    return {
      month,
      recruitment,
      churn,
      netChange,
      validationStatus,
      completeness
    };
  });
};

interface QuarterSummary {
  quarter: string;
  totalRecruitment: number;
  totalChurn: number;
  netChange: number;
  avgCompleteness: number;
  status: 'complete' | 'warning' | 'incomplete';
}

export const MonthlyOverviewTable: React.FC<MonthlyOverviewTableProps> = ({
  office,
  year,
  onDataChange
}) => {
  const [data] = useState<OverviewData[]>(() => createMockOverviewData());

  const quarterSummaries = useMemo((): QuarterSummary[] => {
    const quarters = [
      { quarter: 'Q1', months: [0, 1, 2] },
      { quarter: 'Q2', months: [3, 4, 5] },
      { quarter: 'Q3', months: [6, 7, 8] },
      { quarter: 'Q4', months: [9, 10, 11] }
    ];

    return quarters.map(({ quarter, months }) => {
      const quarterData = months.map(i => data[i]);
      const totalRecruitment = quarterData.reduce((sum, month) => sum + month.recruitment, 0);
      const totalChurn = quarterData.reduce((sum, month) => sum + month.churn, 0);
      const netChange = totalRecruitment - totalChurn;
      const avgCompleteness = quarterData.reduce((sum, month) => sum + month.completeness, 0) / quarterData.length;
      
      const status: 'complete' | 'warning' | 'incomplete' = 
        avgCompleteness === 100 ? 'complete' :
        avgCompleteness >= 80 ? 'warning' : 'incomplete';

      return {
        quarter,
        totalRecruitment,
        totalChurn,
        netChange,
        avgCompleteness: Math.round(avgCompleteness),
        status
      };
    });
  }, [data]);

  const summaryData = useMemo(() => {
    const totalRecruitment = data.reduce((sum, month) => sum + month.recruitment, 0);
    const totalChurn = data.reduce((sum, month) => sum + month.churn, 0);
    const avgCompleteness = data.reduce((sum, month) => sum + month.completeness, 0) / data.length;
    const completeMonths = data.filter(month => month.validationStatus === 'complete').length;
    
    return {
      totalRecruitment,
      totalChurn,
      netChange: totalRecruitment - totalChurn,
      avgCompleteness: Math.round(avgCompleteness),
      completeMonths
    };
  }, [data]);

  const getStatusIcon = (status: 'complete' | 'warning' | 'incomplete') => {
    switch (status) {
      case 'complete':
        return <CheckCircle className="h-3 w-3" style={{ color: '#9ca3af' }} />;
      case 'warning':
        return <AlertCircle className="h-3 w-3" style={{ color: '#9ca3af' }} />;
      case 'incomplete':
        return <AlertCircle className="h-3 w-3" style={{ color: '#9ca3af' }} />;
    }
  };

  return (
    <div className="monthly-overview-table space-y-4 p-4" style={{ backgroundColor: '#111827' }}>
      {/* Clean Header */}
      <div className="flex items-center justify-between pb-2">
        <div className="flex items-center gap-2">
          <BarChart3 className="h-4 w-4" style={{ color: '#9ca3af' }} />
          <h3 className="text-base font-medium" style={{ color: '#f3f4f6' }}>
            Monthly overview and validation summary for {office.name} {year}
          </h3>
        </div>
        <Badge variant="outline" className="text-xs" style={{ backgroundColor: '#1f2937', color: '#d1d5db', borderColor: '#4b5563' }}>
          <CheckCircle className="h-3 w-3 mr-1" style={{ color: '#9ca3af' }} />
          {summaryData.completeMonths}/12 Complete
        </Badge>
      </div>

      {/* Summary Cards - Clean & Minimal */}
      <div className="grid grid-cols-2 gap-3">
        <div className="p-3 rounded-lg" style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
          <div className="flex items-center gap-2 mb-1">
            <TrendingUp className="h-3 w-3" style={{ color: '#9ca3af' }} />
            <span className="text-xs font-medium" style={{ color: '#d1d5db' }}>Net Growth</span>
          </div>
          <div className="text-lg font-semibold" style={{ color: '#f3f4f6' }}>+{summaryData.netChange}</div>
          <div className="text-xs" style={{ color: '#9ca3af' }}>
            {summaryData.totalRecruitment} hired, {summaryData.totalChurn} departures
          </div>
        </div>

        <div className="p-3 rounded-lg" style={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}>
          <div className="flex items-center gap-2 mb-1">
            <BarChart3 className="h-3 w-3" style={{ color: '#9ca3af' }} />
            <span className="text-xs font-medium" style={{ color: '#d1d5db' }}>Plan Completeness</span>
          </div>
          <div className="text-lg font-semibold" style={{ color: '#f3f4f6' }}>{summaryData.avgCompleteness}%</div>
          <div className="text-xs" style={{ color: '#9ca3af' }}>
            {summaryData.completeMonths} of 12 months complete
          </div>
        </div>
      </div>

      {/* Quarterly Summary - Clean Table */}
      <div className="rounded-lg overflow-hidden" style={{ border: '1px solid #374151' }}>
        <Table>
          <TableHeader>
            <TableRow style={{ backgroundColor: '#1f2937', borderBottom: '1px solid #374151' }}>
              <TableHead className="text-xs font-medium w-16" style={{ color: '#d1d5db' }}>Quarter</TableHead>
              <TableHead className="text-xs font-medium text-center w-20" style={{ color: '#d1d5db' }}>Hired</TableHead>
              <TableHead className="text-xs font-medium text-center w-20" style={{ color: '#d1d5db' }}>Departures</TableHead>
              <TableHead className="text-xs font-medium text-center w-20" style={{ color: '#d1d5db' }}>Net</TableHead>
              <TableHead className="text-xs font-medium text-center w-24" style={{ color: '#d1d5db' }}>Complete %</TableHead>
              <TableHead className="text-xs font-medium text-center w-20" style={{ color: '#d1d5db' }}>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {quarterSummaries.map((quarter) => (
              <TableRow 
                key={quarter.quarter}
                style={{ 
                  backgroundColor: '#111827',
                  borderBottom: '1px solid #374151',
                  transition: 'background-color 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#1f2937';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#111827';
                }}
              >
                <TableCell className="text-xs font-medium" style={{ color: '#f3f4f6' }}>
                  {quarter.quarter}
                </TableCell>
                <TableCell className="text-center">
                  <span className="text-xs font-medium" style={{ color: '#f3f4f6' }}>
                    {quarter.totalRecruitment}
                  </span>
                </TableCell>
                <TableCell className="text-center">
                  <span className="text-xs font-medium" style={{ color: '#f3f4f6' }}>
                    {quarter.totalChurn}
                  </span>
                </TableCell>
                <TableCell className="text-center">
                  <span className="text-xs font-medium" style={{ color: '#f3f4f6' }}>
                    {quarter.netChange > 0 ? '+' : ''}{quarter.netChange}
                  </span>
                </TableCell>
                <TableCell className="text-center">
                  <span className="text-xs font-medium" style={{ color: '#f3f4f6' }}>
                    {quarter.avgCompleteness}%
                  </span>
                </TableCell>
                <TableCell className="text-center">
                  <Badge 
                    variant="outline" 
                    className="text-xs px-2 py-0.5"
                    style={{ 
                      backgroundColor: '#374151', 
                      color: '#d1d5db', 
                      borderColor: '#4b5563' 
                    }}
                  >
                    {getStatusIcon(quarter.status)}
                    <span className="ml-1">{quarter.status}</span>
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Monthly Detail Table - Clean */}
      <div className="rounded-lg overflow-hidden" style={{ border: '1px solid #374151' }}>
        <Table>
          <TableHeader>
            <TableRow style={{ backgroundColor: '#1f2937', borderBottom: '1px solid #374151' }}>
              <TableHead className="text-xs font-medium w-16" style={{ color: '#d1d5db' }}>Month</TableHead>
              <TableHead className="text-xs font-medium text-center w-20" style={{ color: '#d1d5db' }}>Hired</TableHead>
              <TableHead className="text-xs font-medium text-center w-20" style={{ color: '#d1d5db' }}>Departures</TableHead>
              <TableHead className="text-xs font-medium text-center w-20" style={{ color: '#d1d5db' }}>Net</TableHead>
              <TableHead className="text-xs font-medium text-center w-24" style={{ color: '#d1d5db' }}>Complete %</TableHead>
              <TableHead className="text-xs font-medium text-center w-20" style={{ color: '#d1d5db' }}>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((month, index) => (
              <TableRow 
                key={month.month}
                style={{ 
                  backgroundColor: '#111827',
                  borderBottom: index % 3 === 2 ? '2px solid #374151' : '1px solid #374151',
                  transition: 'background-color 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#1f2937';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#111827';
                }}
              >
                <TableCell className="text-xs font-medium" style={{ color: '#f3f4f6' }}>
                  {month.month}
                </TableCell>
                <TableCell className="text-center">
                  <span className="text-xs font-medium" style={{ color: '#f3f4f6' }}>
                    {month.recruitment}
                  </span>
                </TableCell>
                <TableCell className="text-center">
                  <span className="text-xs font-medium" style={{ color: '#f3f4f6' }}>
                    {month.churn}
                  </span>
                </TableCell>
                <TableCell className="text-center">
                  <span className="text-xs font-medium" style={{ color: '#f3f4f6' }}>
                    {month.netChange > 0 ? '+' : ''}{month.netChange}
                  </span>
                </TableCell>
                <TableCell className="text-center">
                  <span className="text-xs font-medium" style={{ color: '#f3f4f6' }}>
                    {month.completeness}%
                  </span>
                </TableCell>
                <TableCell className="text-center">
                  <Badge 
                    variant="outline" 
                    className="text-xs px-2 py-0.5"
                    style={{ 
                      backgroundColor: '#374151', 
                      color: '#d1d5db', 
                      borderColor: '#4b5563' 
                    }}
                  >
                    {getStatusIcon(month.validationStatus)}
                    <span className="ml-1">{month.validationStatus}</span>
                  </Badge>
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
            Validate All
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
            Generate Report
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