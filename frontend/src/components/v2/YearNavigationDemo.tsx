import React from 'react';
import { Card, Typography, Space, Button, Alert } from 'antd';
import { YearNavigationProvider, useYearNavigation } from './YearNavigationProvider';
import YearSelector from './YearSelector';
import EnhancedKPICard from './EnhancedKPICard';

const { Title, Text } = Typography;

// Mock simulation data for testing
const mockSimulationData = {
  years: {
    2024: {
      kpis: {
        totalFTE: 1250,
        margin: 15.8,
        netSales: 850000000,
        ebitda: 134300000
      },
      offices: {
        'Stockholm': { totalFTE: 320, journey: 'Mature Office' },
        'Munich': { totalFTE: 180, journey: 'Established Office' },
        'Copenhagen': { totalFTE: 95, journey: 'Emerging Office' }
      }
    },
    2025: {
      kpis: {
        totalFTE: 1380,
        margin: 17.2,
        netSales: 925000000,
        ebitda: 159100000
      },
      offices: {
        'Stockholm': { totalFTE: 350, journey: 'Mature Office' },
        'Munich': { totalFTE: 200, journey: 'Established Office' },
        'Copenhagen': { totalFTE: 110, journey: 'Emerging Office' }
      }
    },
    2026: {
      kpis: {
        totalFTE: 1520,
        margin: 19.1,
        netSales: 1025000000,
        ebitda: 195775000
      },
      offices: {
        'Stockholm': { totalFTE: 385, journey: 'Mature Office' },
        'Munich': { totalFTE: 225, journey: 'Established Office' },
        'Copenhagen': { totalFTE: 130, journey: 'Emerging Office' }
      }
    },
    2027: {
      kpis: {
        totalFTE: 1680,
        margin: 20.4,
        netSales: 1150000000,
        ebitda: 234600000
      },
      offices: {
        'Stockholm': { totalFTE: 420, journey: 'Mature Office' },
        'Munich': { totalFTE: 250, journey: 'Established Office' },
        'Copenhagen': { totalFTE: 155, journey: 'Emerging Office' }
      }
    }
  }
};

// Demo content component that uses the year navigation context
const YearNavigationDemoContent: React.FC = () => {
  const { 
    selectedYear, 
    availableYears, 
    yearData, 
    previousYearData, 
    loading, 
    error,
    setSelectedYear 
  } = useYearNavigation();

  // Get KPI data for current and previous year
  const currentKPIs = yearData?.kpis;
  const previousKPIs = previousYearData?.kpis;

  // Generate sparkline data for trends
  const marginSparklineData = availableYears.map(year => ({
    year,
    value: mockSimulationData.years[year as keyof typeof mockSimulationData.years]?.kpis?.margin || 0
  }));

  const fteSparklineData = availableYears.map(year => ({
    year,
    value: mockSimulationData.years[year as keyof typeof mockSimulationData.years]?.kpis?.totalFTE || 0
  }));

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <Title level={2}>Year Navigation Demo</Title>
      <Text type="secondary" style={{ display: 'block', marginBottom: '24px' }}>
        This demo shows the YearNavigationProvider and YearSelector components working together
        with enhanced KPI cards that display year-over-year changes.
      </Text>

      {/* Year Selector */}
      <YearSelector />

      {/* Error Display */}
      {error && (
        <Alert
          type="error"
          message="Navigation Error"
          description={error}
          style={{ marginBottom: '24px' }}
          showIcon
        />
      )}

      {/* Year Navigation Info */}
      <Card style={{ marginBottom: '24px' }}>
        <Title level={4}>Navigation State</Title>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Text strong>Selected Year: </Text>
            <Text code>{selectedYear}</Text>
          </div>
          <div>
            <Text strong>Available Years: </Text>
            <Text code>{availableYears.join(', ')}</Text>
          </div>
          <div>
            <Text strong>Loading: </Text>
            <Text code>{loading ? 'true' : 'false'}</Text>
          </div>
          <div>
            <Text strong>Has Previous Year Data: </Text>
            <Text code>{previousYearData ? 'true' : 'false'}</Text>
          </div>
        </Space>

        {/* Quick Navigation Buttons */}
        <div style={{ marginTop: '16px' }}>
          <Text strong style={{ marginRight: '12px' }}>Quick Navigation:</Text>
          <Space>
            {availableYears.map(year => (
              <Button
                key={year}
                type={year === selectedYear ? 'primary' : 'default'}
                size="small"
                onClick={() => setSelectedYear(year)}
                loading={loading && year === selectedYear}
              >
                {year}
              </Button>
            ))}
          </Space>
        </div>
      </Card>

      {/* Enhanced KPI Cards */}
      {currentKPIs && (
        <div>
          <Title level={4} style={{ marginBottom: '16px' }}>Enhanced KPI Cards with Year-over-Year Changes</Title>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
            gap: '24px',
            marginBottom: '24px'
          }}>
            {/* Total FTE */}
            <EnhancedKPICard
              title="Total FTE"
              currentValue={currentKPIs.totalFTE}
              previousValue={previousKPIs?.totalFTE}
              unit=""
              target={1800}
              sparklineData={fteSparklineData}
              description="Total full-time equivalent employees across all offices"
              precision={0}
            />

            {/* Margin */}
            <EnhancedKPICard
              title="EBITDA Margin"
              currentValue={currentKPIs.margin}
              previousValue={previousKPIs?.margin}
              unit="%"
              target={20}
              sparklineData={marginSparklineData}
              description="Earnings before interest, taxes, depreciation, and amortization margin"
              precision={1}
            />

            {/* Net Sales */}
            <EnhancedKPICard
              title="Net Sales"
              currentValue={currentKPIs.netSales}
              previousValue={previousKPIs?.netSales}
              unit=" SEK"
              sparklineData={availableYears.map(year => ({
                year,
                value: mockSimulationData.years[year as keyof typeof mockSimulationData.years]?.kpis?.netSales || 0
              }))}
              description="Total revenue from client services"
              precision={0}
            />

            {/* EBITDA */}
            <EnhancedKPICard
              title="EBITDA"
              currentValue={currentKPIs.ebitda}
              previousValue={previousKPIs?.ebitda}
              unit=" SEK"
              sparklineData={availableYears.map(year => ({
                year,
                value: mockSimulationData.years[year as keyof typeof mockSimulationData.years]?.kpis?.ebitda || 0
              }))}
              description="Earnings before interest, taxes, depreciation, and amortization"
              precision={0}
            />
          </div>
        </div>
      )}

      {/* Office Data */}
      {yearData?.offices && (
        <Card>
          <Title level={4}>Office Data for {selectedYear}</Title>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            {Object.entries(yearData.offices).map(([officeName, officeData]: [string, any]) => (
              <div key={officeName} style={{ 
                padding: '12px', 
                border: '1px solid #f0f0f0', 
                borderRadius: '6px',
                background: '#fafafa'
              }}>
                <Text strong style={{ display: 'block', marginBottom: '4px' }}>{officeName}</Text>
                <Text type="secondary" style={{ fontSize: '12px', display: 'block' }}>
                  {officeData.journey}
                </Text>
                <Text style={{ fontSize: '14px', marginTop: '4px', display: 'block' }}>
                  {officeData.totalFTE} FTE
                </Text>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};

/**
 * YearNavigationDemo Component
 * 
 * Demo component that showcases the YearNavigationProvider and related components.
 * This serves as both a test environment and a reference implementation.
 */
export const YearNavigationDemo: React.FC = () => {
  const handleYearChange = (year: number) => {
    console.log(`[Demo] Year changed to: ${year}`);
  };

  return (
    <YearNavigationProvider 
      simulationData={mockSimulationData}
      onYearChange={handleYearChange}
    >
      <YearNavigationDemoContent />
    </YearNavigationProvider>
  );
};

export default YearNavigationDemo; 