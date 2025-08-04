import React, { useState } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import type { SimulationResults } from '../../types/unified-data-structures';

interface SimulationChartsProps {
  results: SimulationResults;
  selectedOffice: string | 'Group';
  className?: string;
}

type ChartType = 'line' | 'area' | 'bar';
type MetricType = 'FTE' | 'Sales' | 'EBITDA' | 'Growth' | 'Journeys';

export const SimulationCharts: React.FC<SimulationChartsProps> = ({
  results,
  selectedOffice,
  className
}) => {
  const [chartType, setChartType] = useState<ChartType>('line');
  const [selectedMetric, setSelectedMetric] = useState<MetricType>('FTE');

  // Helper function to get KPI value from simulation results
  const getKPIValue = (kpiKey: string, year: string, office: string | 'Group'): number => {
    if (!results?.years?.[year]) return 0;

    const yearData = results.years[year];

    if (office === 'Group') {
      const kpis = yearData.kpis;
      if (!kpis) return 0;

      const financial = kpis.financial;
      const growth = kpis.growth;
      const journeys = kpis.journeys;

      switch (kpiKey) {
        case 'FTE':
          return financial?.total_consultants || 0;
        case 'Sales':
          return financial?.net_sales || 0;
        case 'EBITDA':
          return financial?.ebitda || 0;
        case 'EBITDA%':
          return financial?.margin ? financial.margin * 100 : 0;
        case 'Growth%':
          return growth?.total_growth_percent || 0;
        case 'J-1':
          return journeys?.journey_percentages?.["Journey 1"] || 0;
        case 'J-2':
          return journeys?.journey_percentages?.["Journey 2"] || 0;
        case 'J-3':
          return journeys?.journey_percentages?.["Journey 3"] || 0;
        case 'J-4':
          return journeys?.journey_percentages?.["Journey 4"] || 0;
        default:
          return 0;
      }
    } else {
      const officeData = yearData.offices?.[office];
      if (!officeData) return 0;

      const financial = officeData.financial || {};
      const growth = officeData.growth || {};
      const journeys = officeData.journeys || {};

      switch (kpiKey) {
        case 'FTE':
          return officeData.total_fte || 0;
        case 'Sales':
          return financial.net_sales || 0;
        case 'EBITDA':
          return financial.ebitda || 0;
        case 'EBITDA%':
          return financial.margin ? financial.margin * 100 : 0;
        case 'Growth%':
          return growth.total_growth_percent || 0;
        case 'J-1':
          return journeys.journey_percentages?.["Journey 1"] || 0;
        case 'J-2':
          return journeys.journey_percentages?.["Journey 2"] || 0;
        case 'J-3':
          return journeys.journey_percentages?.["Journey 3"] || 0;
        case 'J-4':
          return journeys.journey_percentages?.["Journey 4"] || 0;
        default:
          return 0;
      }
    }
  };

  // Prepare chart data
  const prepareChartData = (metric: MetricType) => {
    const years = Object.keys(results?.years || {}).sort();
    
    switch (metric) {
      case 'FTE':
        return years.map(year => ({
          year,
          FTE: getKPIValue('FTE', year, selectedOffice)
        }));
      
      case 'Sales':
        return years.map(year => ({
          year,
          Sales: getKPIValue('Sales', year, selectedOffice),
          EBITDA: getKPIValue('EBITDA', year, selectedOffice)
        }));
      
      case 'EBITDA':
        return years.map(year => ({
          year,
          EBITDA: getKPIValue('EBITDA', year, selectedOffice),
          'EBITDA%': getKPIValue('EBITDA%', year, selectedOffice)
        }));
      
      case 'Growth':
        return years.map(year => ({
          year,
          'Growth%': getKPIValue('Growth%', year, selectedOffice)
        }));
      
      case 'Journeys':
        return years.map(year => ({
          year,
          'J-1': getKPIValue('J-1', year, selectedOffice),
          'J-2': getKPIValue('J-2', year, selectedOffice),
          'J-3': getKPIValue('J-3', year, selectedOffice),
          'J-4': getKPIValue('J-4', year, selectedOffice)
        }));
      
      default:
        return [];
    }
  };

  // Prepare pie chart data for journeys
  const prepareJourneyPieData = () => {
    const years = Object.keys(results?.years || {}).sort();
    const latestYear = years[years.length - 1];
    
    if (!latestYear) return [];

    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6'];
    
    return ['J-1', 'J-2', 'J-3', 'J-4'].map((journey, index) => ({
      name: journey,
      value: getKPIValue(journey, latestYear, selectedOffice),
      color: colors[index]
    })).filter(item => item.value > 0);
  };

  // Format value based on metric
  const formatValue = (value: number, metric: string): string => {
    const formatLargeNumber = (num: number) => {
      if (Math.abs(num) >= 1_000_000_000) {
        return (num / 1_000_000_000).toFixed(1) + 'B';
      }
      if (Math.abs(num) >= 1_000_000) {
        return (num / 1_000_000).toFixed(1) + 'M';
      }
      if (Math.abs(num) >= 1_000) {
        return (num / 1_000).toFixed(1) + 'K';
      }
      return num.toFixed(0);
    };

    if (metric.includes('%')) {
      return `${value.toFixed(1)}%`;
    }
    if (metric === 'Sales' || metric === 'EBITDA') {
      return `SEK ${formatLargeNumber(value)}`;
    }
    return formatLargeNumber(value);
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium text-sm mb-2">{`Year: ${label}`}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {`${entry.dataKey}: ${formatValue(entry.value, entry.dataKey)}`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  // Render chart based on type and metric
  const renderChart = (data: any[], metric: MetricType) => {
    const chartHeight = 300;
    
    if (metric === 'Journeys' && chartType === 'line') {
      return (
        <ResponsiveContainer width="100%" height={chartHeight}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" />
            <YAxis />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line type="monotone" dataKey="J-1" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} />
            <Line type="monotone" dataKey="J-2" stroke="#10b981" strokeWidth={2} dot={{ r: 4 }} />
            <Line type="monotone" dataKey="J-3" stroke="#f59e0b" strokeWidth={2} dot={{ r: 4 }} />
            <Line type="monotone" dataKey="J-4" stroke="#8b5cf6" strokeWidth={2} dot={{ r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      );
    }

    if (metric === 'Sales') {
      switch (chartType) {
        case 'line':
          return (
            <ResponsiveContainer width="100%" height={chartHeight}>
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Line type="monotone" dataKey="Sales" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} />
                <Line type="monotone" dataKey="EBITDA" stroke="#10b981" strokeWidth={2} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          );
        case 'area':
          return (
            <ResponsiveContainer width="100%" height={chartHeight}>
              <AreaChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Area type="monotone" dataKey="Sales" stackId="1" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
                <Area type="monotone" dataKey="EBITDA" stackId="2" stroke="#10b981" fill="#10b981" fillOpacity={0.3} />
              </AreaChart>
            </ResponsiveContainer>
          );
        case 'bar':
          return (
            <ResponsiveContainer width="100%" height={chartHeight}>
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Bar dataKey="Sales" fill="#3b82f6" />
                <Bar dataKey="EBITDA" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          );
      }
    }

    if (metric === 'EBITDA') {
      const dataKey1 = 'EBITDA';
      const dataKey2 = 'EBITDA%';
      
      switch (chartType) {
        case 'line':
          return (
            <ResponsiveContainer width="100%" height={chartHeight}>
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Line yAxisId="left" type="monotone" dataKey={dataKey1} stroke="#8b5cf6" strokeWidth={2} dot={{ r: 4 }} />
                <Line yAxisId="right" type="monotone" dataKey={dataKey2} stroke="#f59e0b" strokeWidth={2} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          );
        case 'area':
          return (
            <ResponsiveContainer width="100%" height={chartHeight}>
              <AreaChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Area type="monotone" dataKey={dataKey1} stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.3} />
              </AreaChart>
            </ResponsiveContainer>
          );
        case 'bar':
          return (
            <ResponsiveContainer width="100%" height={chartHeight}>
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Bar dataKey={dataKey1} fill="#8b5cf6" />
              </BarChart>
            </ResponsiveContainer>
          );
      }
    }

    // Default single metric chart
    const dataKeys = Object.keys(data[0] || {}).filter(key => key !== 'year');
    const primaryDataKey = dataKeys[0];
    
    if (!primaryDataKey) return null;

    switch (chartType) {
      case 'line':
        return (
          <ResponsiveContainer width="100%" height={chartHeight}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip content={<CustomTooltip />} />
              <Line type="monotone" dataKey={primaryDataKey} stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        );
      case 'area':
        return (
          <ResponsiveContainer width="100%" height={chartHeight}>
            <AreaChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey={primaryDataKey} stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
            </AreaChart>
          </ResponsiveContainer>
        );
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={chartHeight}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey={primaryDataKey} fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        );
    }
  };

  const chartData = prepareChartData(selectedMetric);
  const journeyPieData = prepareJourneyPieData();

  return (
    <div className={className} data-testid="simulation-charts">
      <Tabs defaultValue="trends" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="trends">Trends Over Time</TabsTrigger>
          <TabsTrigger value="distribution">Journey Distribution</TabsTrigger>
        </TabsList>

        <TabsContent value="trends" className="space-y-4">
          <Card data-testid="revenue-chart">
            <CardHeader className="pb-3">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
                <CardTitle className="text-lg">Performance Trends</CardTitle>
                <div className="flex flex-col sm:flex-row gap-2">
                  <Select value={selectedMetric} onValueChange={(value: MetricType) => setSelectedMetric(value)}>
                    <SelectTrigger className="w-[140px]">
                      <SelectValue placeholder="Select metric" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="FTE">FTE</SelectItem>
                      <SelectItem value="Sales">Sales & EBITDA</SelectItem>
                      <SelectItem value="EBITDA">EBITDA Analysis</SelectItem>
                      <SelectItem value="Growth">Growth Rate</SelectItem>
                      <SelectItem value="Journeys">Journey Mix</SelectItem>
                    </SelectContent>
                  </Select>
                  
                  <Select value={chartType} onValueChange={(value: ChartType) => setChartType(value)}>
                    <SelectTrigger className="w-[100px]">
                      <SelectValue placeholder="Chart type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="line">Line</SelectItem>
                      <SelectItem value="area">Area</SelectItem>
                      <SelectItem value="bar">Bar</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Badge variant="outline">{selectedOffice === 'Group' ? 'Group View' : selectedOffice}</Badge>
                <Badge variant="secondary">{selectedMetric}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              {chartData.length > 0 ? (
                renderChart(chartData, selectedMetric)
              ) : (
                <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                  No data available for the selected metric
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="distribution" className="space-y-4">
          <Card data-testid="profitability-chart">
            <CardHeader>
              <CardTitle className="text-lg">Journey Distribution</CardTitle>
              <div className="flex items-center space-x-2">
                <Badge variant="outline">{selectedOffice === 'Group' ? 'Group View' : selectedOffice}</Badge>
                <Badge variant="secondary">Latest Year</Badge>
              </div>
            </CardHeader>
            <CardContent>
              {journeyPieData.length > 0 ? (
                <ResponsiveContainer width="100%" height={350}>
                  <PieChart>
                    <Pie
                      data={journeyPieData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                      outerRadius={120}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {journeyPieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip 
                      formatter={(value: number) => [`${value.toFixed(1)}%`, 'Percentage']}
                    />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-[350px] text-muted-foreground">
                  No journey data available
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};