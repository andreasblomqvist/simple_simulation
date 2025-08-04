/**
 * Modern Results Table
 * 
 * Unified implementation replacing the legacy Ant Design ResultsTable
 * Uses the new FinancialDataTable for consistent KPI display
 */
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { LoadingSpinner } from '../ui/loading-states';
import { AlertTriangle, Building2, TrendingUp } from 'lucide-react';
import { FinancialDataTable, FinancialRow, buildFinancialTableData, formatKPIValue } from '../ui/financial-data-table';
import type { SimulationResults, ScenarioDefinition, OfficeName } from '../../types/unified-data-structures';
import { scenarioApi } from '../../services/scenarioApi';

// KPI definitions with proper typing
const KPI_DEFINITIONS = [
  { key: 'FTE', label: 'FTE', unit: 'count' as const },
  { key: 'Growth%', label: 'Growth%', unit: 'percentage' as const },
  { key: 'Sales', label: 'Sales', unit: 'currency' as const },
  { key: 'EBITDA', label: 'EBITDA', unit: 'currency' as const },
  { key: 'EBITDA%', label: 'EBITDA%', unit: 'percentage' as const },
  { key: 'J-1', label: 'J-1', unit: 'percentage' as const },
  { key: 'J-2', label: 'J-2', unit: 'percentage' as const },
  { key: 'J-3', label: 'J-3', unit: 'percentage' as const },
  { key: 'J-4', label: 'J-4', unit: 'percentage' as const },
];

interface ModernResultsTableProps {
  scenarioId: string;
  onNext?: () => void;
  onBack?: () => void;
}

// Helper function to get available offices from simulation results
function getAvailableOffices(data: SimulationResults | null): string[] {
  if (!data || !data.years) return [];
  
  const firstYear = Object.keys(data.years)[0];
  if (!firstYear) return [];
  
  return Object.keys(data.years[firstYear].offices);
}

// Helper function to extract KPI value from simulation results
function getKPIValue(data: SimulationResults | null, office: OfficeName, kpiKey: string, year: number): number {
  if (!data || !data.years[year.toString()]) return 0;
  
  const yearData = data.years[year.toString()];
  
  // Find the actual office name in the results (case-insensitive)
  const availableOffices = Object.keys(yearData.offices);
  const actualOfficeName = availableOffices.find(name => 
    name.toLowerCase() === office.toLowerCase()
  );
  
  if (!actualOfficeName) {
    console.log(`[DEBUG][ModernResultsTable] Office '${office}' not found in results. Available offices:`, availableOffices);
    return 0;
  }
  
  const officeData = yearData.offices[actualOfficeName];
  if (!officeData) return 0;
  
  // Access data directly from officeData
  const financial = officeData.financial || {};
  const growth = officeData.growth || {};
  const journeys = officeData.journeys || {};

  let value = 0;
  switch (kpiKey) {
    case 'FTE':
      value = officeData.total_fte || 0;
      break;
    case 'Sales':
      value = financial.net_sales || 0;
      break;
    case 'EBITDA':
      value = financial.ebitda || 0;
      break;
    case 'EBITDA%':
      value = financial.margin ? financial.margin * 100 : 0;
      break;
    case 'Growth%':
      value = growth.total_growth_percent || 0;
      break;
    case 'J-1':
      value = journeys.journey_percentages?.["Journey 1"] || 0;
      break;
    case 'J-2':
      value = journeys.journey_percentages?.["Journey 2"] || 0;
      break;
    case 'J-3':
      value = journeys.journey_percentages?.["Journey 3"] || 0;
      break;
    case 'J-4':
      value = journeys.journey_percentages?.["Journey 4"] || 0;
      break;
    default:
      value = 0;
  }
  
  // Fallback to group-level KPIs if office-level data is zero
  if (value === 0 && yearData.kpis) {
    const yearlyKpis = yearData.kpis.yearly_kpis?.[year.toString()];
    const financial = yearlyKpis?.financial || yearData.kpis.financial;
    const growth = yearlyKpis?.growth || yearData.kpis.growth;
    const journeys = yearlyKpis?.journeys || yearData.kpis.journeys;
    
    switch (kpiKey) {
      case 'FTE':
        value = financial?.total_consultants || 0;
        break;
      case 'Sales':
        value = financial?.net_sales || 0;
        break;
      case 'EBITDA':
        value = financial?.ebitda || 0;
        break;
      case 'EBITDA%':
        value = financial?.margin ? financial.margin * 100 : 0;
        break;
      case 'Growth%':
        value = growth?.total_growth_percent || 0;
        break;
      case 'J-1':
        value = journeys?.journey_percentages?.["Journey 1"] || 0;
        break;
      case 'J-2':
        value = journeys?.journey_percentages?.["Journey 2"] || 0;
        break;
      case 'J-3':
        value = journeys?.journey_percentages?.["Journey 3"] || 0;
        break;
      case 'J-4':
        value = journeys?.journey_percentages?.["Journey 4"] || 0;
        break;
    }
  }
  
  return value;
}

// Helper function to extract Group/global KPI value from simulation results
function getGroupKPIValue(data: SimulationResults | null, kpiKey: string, year: number): number {
  if (!data || !data.years[year.toString()]) return 0;
  
  const yearData = data.years[year.toString()];
  const kpis = yearData.kpis;
  
  if (!kpis) {
    console.log(`[DEBUG][ModernResultsTable] No KPIs found for year ${year}`);
    return 0;
  }
  
  const yearlyKpis = kpis.yearly_kpis?.[year.toString()];
  const financial = yearlyKpis?.financial || kpis.financial;
  const growth = yearlyKpis?.growth || kpis.growth;
  const journeys = yearlyKpis?.journeys || kpis.journeys;
  
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
}

// Build table data from simulation results
function buildKPITableData(
  scenarioData: SimulationResults | null,
  office: OfficeName | 'Group'
): Record<string, Record<string, number>> {
  if (!scenarioData || !scenarioData.years) {
    return {};
  }

  const kpiData: Record<string, Record<string, number>> = {};
  const years = Object.keys(scenarioData.years).sort();
  
  KPI_DEFINITIONS.forEach(kpi => {
    kpiData[kpi.label] = {};
    years.forEach(year => {
      const yearNum = parseInt(year);
      let value = 0;
      if (office === 'Group') {
        value = getGroupKPIValue(scenarioData, kpi.key, yearNum);
      } else {
        value = getKPIValue(scenarioData, office, kpi.key, yearNum);
      }
      kpiData[kpi.label][year] = value;
    });
  });

  return kpiData;
}

export const ModernResultsTable: React.FC<ModernResultsTableProps> = ({ 
  scenarioId, 
  onNext, 
  onBack 
}) => {
  const [scenarioData, setScenarioData] = useState<SimulationResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedOffice, setSelectedOffice] = useState<OfficeName>('Stockholm');
  const [availableOffices, setAvailableOffices] = useState<OfficeName[]>([]);

  // Load scenario results
  useEffect(() => {
    const loadResults = async () => {
      try {
        setLoading(true);
        setError(null);
        
        console.log('[DEBUG][ModernResultsTable] Loading scenario results for ID:', scenarioId);
        
        const results = await scenarioApi.getScenarioResults(scenarioId);
        
        console.log('[DEBUG][ModernResultsTable] Loaded results:', results);
        
        setScenarioData(results);
        
        // Update available offices from the results
        const offices = getAvailableOffices(results);
        setAvailableOffices(offices as OfficeName[]);
        
        // Set the first available office as selected
        if (offices.length > 0 && !offices.includes(selectedOffice as any)) {
          setSelectedOffice(offices[0] as OfficeName);
        }
        
      } catch (err) {
        console.error('[DEBUG][ModernResultsTable] Error loading results:', err);
        setError(err instanceof Error ? err.message : 'Failed to load results');
      } finally {
        setLoading(false);
      }
    };

    if (scenarioId) {
      loadResults();
    }
  }, [scenarioId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <LoadingSpinner size="lg" />
        <span className="ml-2">Loading scenario results...</span>
      </div>
    );
  }

  if (error) {
    const notFound = error.toLowerCase().includes('not found');
    return (
      <div className="text-center p-8">
        <AlertTriangle className="mx-auto h-12 w-12 text-red-500 mb-4" />
        <p className="text-lg font-semibold mb-2">
          {notFound ? 'Scenario Not Found' : 'Error Loading Results'}
        </p>
        <p className="text-muted-foreground mb-4">
          {notFound ? 'This scenario does not exist. Please save your scenario first.' : error}
        </p>
        {onBack && <Button onClick={onBack}>Back</Button>}
      </div>
    );
  }

  if (!scenarioData || !scenarioData.years) {
    return (
      <div className="text-center p-8">
        <AlertTriangle className="mx-auto h-12 w-12 text-yellow-500 mb-4" />
        <p className="text-lg font-semibold mb-2">No Data Available</p>
        <p className="text-muted-foreground mb-4">
          Simulation results are empty. The simulation may have failed or returned no data.
        </p>
        {onBack && <Button onClick={onBack}>Back</Button>}
      </div>
    );
  }

  const years = Object.keys(scenarioData.years).sort();
  const groupKPIData = buildKPITableData(scenarioData, 'Group');
  const officeKPIData = buildKPITableData(scenarioData, selectedOffice);

  return (
    <div className="space-y-6">
      {/* Group Results */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Building2 className="h-5 w-5" />
            <CardTitle>Group Results</CardTitle>
            <Badge variant="secondary">Key Metrics</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <FinancialDataTable
            data={buildFinancialTableData(groupKPIData, true)}
            years={years}
            enableDelta={true}
            currency="SEK"
            className="group-results-table"
          />
        </CardContent>
      </Card>

      {/* Office Selection */}
      {availableOffices.length > 1 && (
        <div className="flex items-center gap-4">
          <label className="font-medium">Select Office:</label>
          <Select value={selectedOffice} onValueChange={(value) => setSelectedOffice(value as OfficeName)}>
            <SelectTrigger className="w-48">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {availableOffices.filter(office => office !== 'Group').map(office => (
                <SelectItem key={office} value={office}>
                  {office}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}

      {/* Office Results */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            <CardTitle>{selectedOffice} Results</CardTitle>
            <Badge variant="secondary">Key Metrics</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <FinancialDataTable
            data={buildFinancialTableData(officeKPIData, true)}
            years={years}
            enableDelta={true}
            currency="SEK"
            className="office-results-table"
          />
        </CardContent>
      </Card>

      {/* Navigation */}
      {(onBack || onNext) && (
        <div className="flex gap-2">
          {onBack && (
            <Button variant="outline" onClick={onBack}>
              Back
            </Button>
          )}
          {onNext && (
            <Button onClick={onNext}>
              Next: Compare Scenarios
            </Button>
          )}
        </div>
      )}
    </div>
  );
};

export default ModernResultsTable;