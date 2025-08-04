import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { cn } from '../../lib/utils';

export interface QuarterlyWorkforceData {
  level: string;
  recruitment: number;
  churn: number;
  progression: number;
}

export interface QuarterData {
  quarter: string;
  period: string;
  data: QuarterlyWorkforceData[];
  quarterEndFTE?: { [level: string]: number }; // FTE at end of quarter
  journeyDistribution?: {
    journey1: number;
    journey2: number;
    journey3: number;
    journey4: number;
  };
  nonDebitRatio?: number;
}

export interface QuarterlyWorkforceChartProps {
  yearData: QuarterData[];
  className?: string;
  showJourneyDistribution?: boolean;
  title?: string;
}

const LEVELS = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P'];

// Custom tooltip to show proper formatting
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
        <p className="font-medium text-gray-900">{`Level ${label}`}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} style={{ color: entry.color }} className="text-sm">
            {`${entry.dataKey}: ${Math.abs(entry.value)}`}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export function QuarterlyWorkforceChart({
  yearData,
  className,
  showJourneyDistribution = true,
  title = "Detailed View by Period"
}: QuarterlyWorkforceChartProps) {
  // Transform data for stacked bar chart
  const transformDataForChart = (quarterData: QuarterlyWorkforceData[], quarterEndFTE: { [level: string]: number }) => {
    return LEVELS.map(level => {
      const levelData = quarterData.find(d => d.level === level);
      const existingFTE = quarterEndFTE[level] || 0;
      const recruitment = levelData?.recruitment || 0;
      const churn = levelData?.churn || 0;
      const progression = levelData?.progression || 0;
      
      // Calculate baseline (existing workforce minus movements)
      const baseline = Math.max(0, existingFTE - recruitment + churn - progression);
      
      return {
        level,
        existing: baseline, // Gray base - existing workforce
        churn: -churn, // Red - negative (below axis)
        recruitment: recruitment, // Green - positive (above baseline)
        progression: progression, // Blue - positive (above recruitment)
      };
    }).filter(item => 
      item.existing > 0 || item.recruitment > 0 || item.churn < 0 || item.progression > 0
    );
  };

  const formatJourneyDistribution = (distribution?: QuarterData['journeyDistribution']) => {
    if (!distribution) return null;
    
    return [
      `${distribution.journey1.toFixed(1)}% Journey 1 (A-C)`,
      `${distribution.journey2.toFixed(1)}% Journey 2 (SrC-AM)`, 
      `${distribution.journey3.toFixed(1)}% Journey 3 (M)`,
      `${distribution.journey4.toFixed(1)}% Journey 4 (SrM+)`
    ];
  };

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-center">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-6">
          {yearData.map((quarter, index) => {
            const chartData = transformDataForChart(quarter.data, quarter.quarterEndFTE || {});
            const journeyDist = formatJourneyDistribution(quarter.journeyDistribution);
            
            return (
              <div key={quarter.quarter} className="space-y-4">
                {/* Quarter Title */}
                <div className="text-center">
                  <h3 className="font-medium text-white">
                    {quarter.quarter}
                  </h3>
                  <p className="text-sm text-gray-300">
                    {quarter.period}
                  </p>
                </div>

                {/* Bar Chart */}
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={chartData}
                      margin={{ top: 20, right: 10, left: 10, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200" />
                      <XAxis 
                        dataKey="level" 
                        tick={{ fontSize: 12, fill: 'white' }}
                        axisLine={false}
                        tickLine={false}
                      />
                      <YAxis 
                        tick={{ fontSize: 12, fill: 'white' }}
                        axisLine={false}
                        tickLine={false}
                      />
                      <Tooltip content={<CustomTooltip />} />
                      
                      {/* Churn (red, negative - below axis) */}
                      <Bar 
                        dataKey="churn" 
                        fill="#EF4444" 
                        name="Churn"
                      />
                      
                      {/* Existing workforce base (gray) */}
                      <Bar 
                        dataKey="existing" 
                        stackId="positive"
                        fill="#E5E7EB" 
                        name="Existing"
                      />
                      
                      {/* Recruitment (green, positive - stacked on existing) */}
                      <Bar 
                        dataKey="recruitment" 
                        stackId="positive"
                        fill="#10B981" 
                        name="Recruitment"
                      />
                      
                      {/* Progression (blue, positive - stacked on recruitment) */}
                      <Bar 
                        dataKey="progression" 
                        stackId="positive"
                        fill="#3B82F6" 
                        name="Progression"
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Journey Distribution */}
                {showJourneyDistribution && journeyDist && (
                  <div className="text-xs text-gray-300 space-y-1">
                    <p className="font-medium">Journey Distribution:</p>
                    {journeyDist.map((dist, idx) => (
                      <p key={idx}>{dist}</p>
                    ))}
                    {quarter.nonDebitRatio && (
                      <p className="mt-2">
                        <span className="font-medium">Non-Debit Ratio:</span> {(quarter.nonDebitRatio * 100).toFixed(1)}%
                      </p>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Legend */}
        <div className="mt-6 flex justify-center space-x-6 text-sm text-white">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-gray-300 rounded"></div>
            <span>Existing</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded"></div>
            <span>Recruitment</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-blue-500 rounded"></div>
            <span>Progression</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-red-500 rounded"></div>
            <span>Churn</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Example data for testing
export const exampleQuarterlyData: QuarterData[] = [
  {
    quarter: "Year 0.5 - Period 6",
    period: "Q2",
    data: [
      { level: "A", recruitment: 5, churn: 2, progression: 1 },
      { level: "AC", recruitment: 3, churn: 1, progression: 2 },
      { level: "C", recruitment: 2, churn: 1, progression: 1 },
      { level: "SrC", recruitment: 1, churn: 0, progression: 1 },
      { level: "AM", recruitment: 0, churn: 1, progression: 0 },
      { level: "M", recruitment: 0, churn: 0, progression: 1 }
    ],
    quarterEndFTE: {
      "A": 45, "AC": 25, "C": 18, "SrC": 12, "AM": 8, "M": 5
    },
    journeyDistribution: {
      journey1: 68.3,
      journey2: 26.8,
      journey3: 2.9,
      journey4: 2.0
    },
    nonDebitRatio: 0.65
  },
  {
    quarter: "Year 0.5 - Period 1",
    period: "Q1", 
    data: [
      { level: "A", recruitment: 4, churn: 1, progression: 2 },
      { level: "AC", recruitment: 2, churn: 2, progression: 1 },
      { level: "C", recruitment: 3, churn: 0, progression: 2 },
      { level: "SrC", recruitment: 1, churn: 1, progression: 0 },
      { level: "AM", recruitment: 1, churn: 0, progression: 1 },
      { level: "M", recruitment: 0, churn: 0, progression: 0 }
    ],
    quarterEndFTE: {
      "A": 42, "AC": 23, "C": 20, "SrC": 10, "AM": 6, "M": 4
    },
    journeyDistribution: {
      journey1: 64.2,
      journey2: 29.1, 
      journey3: 4.2,
      journey4: 2.5
    },
    nonDebitRatio: 0.68
  },
  {
    quarter: "Year 1.5 - Period 3",
    period: "Q3",
    data: [
      { level: "A", recruitment: 6, churn: 3, progression: 0 },
      { level: "AC", recruitment: 4, churn: 1, progression: 3 },
      { level: "C", recruitment: 2, churn: 2, progression: 1 },
      { level: "SrC", recruitment: 1, churn: 0, progression: 2 },
      { level: "AM", recruitment: 0, churn: 1, progression: 0 },
      { level: "M", recruitment: 1, churn: 0, progression: 1 }
    ],
    quarterEndFTE: {
      "A": 48, "AC": 28, "C": 16, "SrC": 14, "AM": 7, "M": 6
    },
    journeyDistribution: {
      journey1: 65.3,
      journey2: 27.4,
      journey3: 4.8,
      journey4: 2.5
    },
    nonDebitRatio: 0.62
  },
  {
    quarter: "Year 1.5 - Period 4", 
    period: "Q4",
    data: [
      { level: "A", recruitment: 3, churn: 2, progression: 1 },
      { level: "AC", recruitment: 2, churn: 0, progression: 2 },
      { level: "C", recruitment: 1, churn: 1, progression: 0 },
      { level: "SrC", recruitment: 2, churn: 1, progression: 1 },
      { level: "AM", recruitment: 0, churn: 0, progression: 1 },
      { level: "M", recruitment: 0, churn: 1, progression: 0 },
      { level: "SrM", recruitment: 1, churn: 0, progression: 0 }
    ],
    quarterEndFTE: {
      "A": 50, "AC": 30, "C": 18, "SrC": 15, "AM": 8, "M": 5, "SrM": 3
    },
    journeyDistribution: {
      journey1: 62.7,
      journey2: 28.9,
      journey3: 5.2,
      journey4: 3.2
    },
    nonDebitRatio: 0.69
  }
];