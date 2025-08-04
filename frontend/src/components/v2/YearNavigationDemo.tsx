import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Alert, AlertDescription } from '../ui/alert';
import { YearNavigationProvider, useYearNavigation } from './YearNavigationProvider';
import YearSelector from './YearSelector';
import EnhancedKPICard from './EnhancedKPICard';

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
    <div className="p-6 max-w-6xl mx-auto">
      <h2 className="text-3xl font-bold tracking-tight mb-2">Year Navigation Demo</h2>
      <p className="text-muted-foreground mb-6">
        This demo shows the YearNavigationProvider and YearSelector components working together
        with enhanced KPI cards that display year-over-year changes.
      </p>

      {/* Year Selector */}
      <YearSelector />

      {/* Error Display */}
      {error && (
        <Alert className="mb-6">
          <AlertDescription>
            <strong>Navigation Error:</strong> {error}
          </AlertDescription>
        </Alert>
      )}

      {/* Year Navigation Info */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Navigation State</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div>
            <span className="font-semibold">Selected Year: </span>
            <code className="bg-muted px-1.5 py-0.5 rounded text-sm">{selectedYear}</code>
          </div>
          <div>
            <span className="font-semibold">Available Years: </span>
            <code className="bg-muted px-1.5 py-0.5 rounded text-sm">{availableYears.join(', ')}</code>
          </div>
          <div>
            <span className="font-semibold">Loading: </span>
            <code className="bg-muted px-1.5 py-0.5 rounded text-sm">{loading ? 'true' : 'false'}</code>
          </div>
          <div>
            <span className="font-semibold">Has Previous Year Data: </span>
            <code className="bg-muted px-1.5 py-0.5 rounded text-sm">{previousYearData ? 'true' : 'false'}</code>
          </div>

          {/* Quick Navigation Buttons */}
          <div className="pt-4">
            <span className="font-semibold mr-3">Quick Navigation:</span>
            <div className="flex gap-2 flex-wrap">
              {availableYears.map(year => (
                <Button
                  key={year}
                  variant={year === selectedYear ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedYear(year)}
                  disabled={loading && year === selectedYear}
                >
                  {year}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Enhanced KPI Cards */}
      {currentKPIs && (
        <div>
          <h4 className="text-xl font-semibold mb-4">Enhanced KPI Cards with Year-over-Year Changes</h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
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
          <CardHeader>
            <CardTitle>Office Data for {selectedYear}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(yearData.offices).map(([officeName, officeData]: [string, any]) => (
                <div key={officeName} className="p-3 border border-border rounded-lg bg-muted/50">
                  <div className="font-semibold text-sm mb-1">{officeName}</div>
                  <div className="text-xs text-muted-foreground mb-1">
                    {officeData.journey}
                  </div>
                  <div className="text-sm">
                    {officeData.totalFTE} FTE
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
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