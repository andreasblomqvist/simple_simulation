import React, { useState } from 'react';
import { ScenarioComparisonTable, ScenarioData, ComparisonRow, ScenarioKPI } from '../ui/scenario-comparison-table';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Checkbox } from '../ui/checkbox';
import { Badge } from '../ui/badge';
import { BarChart3, ArrowLeft } from 'lucide-react';

const mockScenarios: ScenarioData[] = [
  { 
    id: '1', 
    name: 'Oslo Growth Plan', 
    description: 'Aggressive growth strategy for Oslo office',
    status: 'completed',
    kpis: { FTE: 1500, 'Growth%': 5, Sales: 3000, EBITDA: 500, 'EBITDA%': 16.7, 'J-1': 38, 'J-2': 50, 'J-3': 12 },
    createdAt: new Date('2025-07-01'),
    completedAt: new Date('2025-07-01')
  },
  { 
    id: '2', 
    name: 'Stockholm Expansion', 
    description: 'Moderate expansion for Stockholm office',
    status: 'completed',
    kpis: { FTE: 1400, 'Growth%': 4, Sales: 2800, EBITDA: 450, 'EBITDA%': 16.1, 'J-1': 36, 'J-2': 52, 'J-3': 12 },
    createdAt: new Date('2025-06-15'),
    completedAt: new Date('2025-06-15')
  },
  { 
    id: '3', 
    name: 'Munich Conservative', 
    description: 'Conservative growth approach for Munich office',
    status: 'completed',
    kpis: { FTE: 1300, 'Growth%': 3, Sales: 2600, EBITDA: 400, 'EBITDA%': 15.4, 'J-1': 34, 'J-2': 54, 'J-3': 12 },
    createdAt: new Date('2025-06-10'),
    completedAt: new Date('2025-06-10')
  },
];

const kpiDefinitions: ScenarioKPI[] = [
  { kpi: 'FTE', unit: 'count', target: 1800, benchmark: 1500 },
  { kpi: 'Growth%', unit: 'percentage', target: 6, benchmark: 4 },
  { kpi: 'Sales', unit: 'currency', target: 3500, benchmark: 3000 },
  { kpi: 'EBITDA', unit: 'currency', target: 700, benchmark: 500 },
  { kpi: 'EBITDA%', unit: 'percentage', target: 20, benchmark: 16 },
  { kpi: 'J-1', unit: 'percentage', target: 35, benchmark: 30 },
  { kpi: 'J-2', unit: 'percentage', target: 50, benchmark: 45 },
  { kpi: 'J-3', unit: 'percentage', target: 15, benchmark: 10 },
];

interface ScenarioComparisonProps {
  onBack: () => void;
}

export default function ScenarioComparison(props: ScenarioComparisonProps) {
  const [selectedScenarios, setSelectedScenarios] = useState<string[]>(['1', '2']);

  const handleScenarioToggle = (scenarioId: string, checked: boolean) => {
    setSelectedScenarios(prev => 
      checked 
        ? [...prev, scenarioId]
        : prev.filter(id => id !== scenarioId)
    );
  };

  // Build comparison data for the table
  const comparisonData: ComparisonRow[] = kpiDefinitions.map(kpiDef => {
    const scenarios: Record<string, any> = {};
    
    selectedScenarios.forEach(scenarioId => {
      const scenario = mockScenarios.find(s => s.id === scenarioId);
      if (scenario && scenario.kpis[kpiDef.kpi] !== undefined) {
        const value = scenario.kpis[kpiDef.kpi];
        const delta = kpiDef.benchmark ? value - kpiDef.benchmark : undefined;
        const percentChange = kpiDef.benchmark ? ((value - kpiDef.benchmark) / kpiDef.benchmark) * 100 : undefined;
        
        let status: 'above_target' | 'below_target' | 'on_target' | undefined;
        if (kpiDef.target) {
          const tolerance = kpiDef.target * 0.05; // 5% tolerance
          if (value > kpiDef.target + tolerance) status = 'above_target';
          else if (value < kpiDef.target - tolerance) status = 'below_target';
          else status = 'on_target';
        }
        
        scenarios[scenarioId] = {
          value,
          delta,
          percentChange,
          status
        };
      }
    });

    return {
      kpi: kpiDef.kpi,
      unit: kpiDef.unit,
      target: kpiDef.target,
      benchmark: kpiDef.benchmark,
      scenarios
    };
  });

  return (
    <div className="space-y-6 p-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Scenario Comparison
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-6">
            <h4 className="font-semibold mb-4">Select scenarios to compare:</h4>
            <div className="space-y-3">
              {mockScenarios.map(scenario => (
                <div key={scenario.id} className="flex items-center space-x-2">
                  <Checkbox
                    id={scenario.id}
                    checked={selectedScenarios.includes(scenario.id)}
                    onCheckedChange={(checked) => handleScenarioToggle(scenario.id, Boolean(checked))}
                  />
                  <label htmlFor={scenario.id} className="flex items-center gap-2 cursor-pointer">
                    <span className="font-medium">{scenario.name}</span>
                    <Badge variant="outline" className="text-xs">
                      {scenario.createdAt.toLocaleDateString()}
                    </Badge>
                    <Badge variant={scenario.status === 'completed' ? 'default' : 'secondary'}>
                      {scenario.status}
                    </Badge>
                  </label>
                </div>
              ))}
            </div>
          </div>

          {selectedScenarios.length > 0 && (
            <ScenarioComparisonTable
              scenarios={mockScenarios.filter(s => selectedScenarios.includes(s.id))}
              comparisonData={comparisonData}
              kpiDefinitions={kpiDefinitions}
              className="scenario-comparison"
            />
          )}

          <div className="mt-6">
            <Button variant="outline" onClick={props.onBack} className="flex items-center gap-2">
              <ArrowLeft className="h-4 w-4" />
              Back
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 