import React, { useState, forwardRef, useImperativeHandle } from 'react';
import { ColumnDef } from "@tanstack/react-table";
import { Info, RotateCcw } from 'lucide-react';
import { DataTable } from '../ui/data-table';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Slider } from '../ui/slider';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../ui/tooltip';
import { cn } from '../../lib/utils';

const ROLES = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P'];
const LEVERS = ['recruitment', 'churn', 'progression'] as const;
const LEVELS = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P'];

type LeverType = typeof LEVERS[number];

type LeverState = Record<LeverType, Record<string, number>>;

const defaultValue = 1.0;
const min = 0.0;
const max = 2.0;
const step = 0.01;

// Mock baseline values for each role and lever
const baselineValues: Record<LeverType, Record<string, number>> = {
  recruitment: { A: 20, AC: 8, C: 4, SrC: 1, AM: 1, M: 0, SrM: 0, Pi: 0, P: 0 },
  churn: { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 0, Pi: 0, P: 0 },
  progression: { A: 1, AC: 1, C: 1, SrC: 1, AM: 1, M: 1, SrM: 1, Pi: 1, P: 1 },
};

// Function to get complete levers data
export function getCompleteLevers(leversData?: any): LeverState {
  if (!leversData || typeof leversData !== 'object') {
    return baselineValues;
  }

  const result: LeverState = {
    recruitment: { ...baselineValues.recruitment },
    churn: { ...baselineValues.churn },
    progression: { ...baselineValues.progression }
  };

  // Process recruitment levers
  if (leversData.recruitment && typeof leversData.recruitment === 'object') {
    Object.entries(leversData.recruitment).forEach(([level, value]) => {
      if (typeof value === 'number' && !isNaN(value)) {
        result.recruitment[level] = value;
      }
    });
  }

  // Process churn levers
  if (leversData.churn && typeof leversData.churn === 'object') {
    Object.entries(leversData.churn).forEach(([level, value]) => {
      if (typeof value === 'number' && !isNaN(value)) {
        result.churn[level] = value;
      }
    });
  }

  // Process progression levers
  if (leversData.progression && typeof leversData.progression === 'object') {
    Object.entries(leversData.progression).forEach(([level, value]) => {
      if (typeof value === 'number' && !isNaN(value)) {
        result.progression[level] = value;
      }
    });
  }

  return result;
}

// Mock CAT progression probabilities (from progression_config.py)
const catProgressionData: Record<string, Record<string, number>> = {
  'A': { 'CAT0': 0.0, 'CAT6': 0.919, 'CAT12': 0.85, 'CAT18': 0.0, 'CAT24': 0.0, 'CAT30': 0.0 },
  'AC': { 'CAT0': 0.0, 'CAT6': 0.054, 'CAT12': 0.759, 'CAT18': 0.400, 'CAT24': 0.0, 'CAT30': 0.0 },
  'C': { 'CAT0': 0.0, 'CAT6': 0.050, 'CAT12': 0.442, 'CAT18': 0.597, 'CAT24': 0.278, 'CAT30': 0.643 },
  'SrC': { 'CAT0': 0.0, 'CAT6': 0.206, 'CAT12': 0.438, 'CAT18': 0.317, 'CAT24': 0.211, 'CAT30': 0.206 },
  'AM': { 'CAT0': 0.0, 'CAT6': 0.0, 'CAT12': 0.0, 'CAT18': 0.189, 'CAT24': 0.197, 'CAT30': 0.234 },
  'M': { 'CAT0': 0.0, 'CAT6': 0.00, 'CAT12': 0.01, 'CAT18': 0.02, 'CAT24': 0.03, 'CAT30': 0.04 },
  'SrM': { 'CAT0': 0.0, 'CAT6': 0.00, 'CAT12': 0.005, 'CAT18': 0.01, 'CAT24': 0.015, 'CAT30': 0.02 },
  'Pi': { 'CAT0': 0.0 },
  'P': { 'CAT0': 0.0 },
};

interface ScenarioLeversProps {
  onNext?: () => void;
  onBack?: () => void;
  onRunSimulation?: () => void;
  levers?: LeverState;
  readOnly?: boolean;
  baselineValues?: Record<LeverType, Record<string, number>>;
  baselineData?: any;
  saving?: boolean;
  simulating?: boolean;
}

export interface ScenarioLeversRef {
  getCurrentData: () => LeverState;
}

interface LeverRowData {
  level: string;
  recruitment: number;
  recruitmentActual: number;
  churn: number;
  churnActual: number;
  progression: number;
  progressionMaxChange: number;
  progressionExpectedTime: string;
}

const ScenarioLeversV2 = forwardRef<ScenarioLeversRef, ScenarioLeversProps>(({ 
  onNext, 
  onBack, 
  onRunSimulation,
  levers: externalLevers, 
  readOnly = false, 
  baselineValues: propBaselineValues, 
  baselineData,
  saving = false,
  simulating = false
}, ref) => {
  const [levers, setLevers] = useState<LeverState>(() => {
    if (externalLevers) {
      return externalLevers;
    }
    // Initialize with default multipliers of 1.0 for all levers
    const defaultLevers: LeverState = {
      recruitment: {},
      churn: {},
      progression: {}
    };
    
    LEVERS.forEach(leverType => {
      LEVELS.forEach(level => {
        defaultLevers[leverType][level] = defaultValue;
      });
    });
    
    return defaultLevers;
  });

  // Expose current data to parent via ref
  useImperativeHandle(ref, () => ({
    getCurrentData: () => {
      console.log('DEBUG: ScenarioLeversV2 getCurrentData called, returning:', levers);
      return levers;
    }
  }));

  // If externalLevers changes, update state
  React.useEffect(() => {
    if (externalLevers) {
      // Merge external levers with defaults to ensure all levels are present
      const mergedLevers: LeverState = {
        recruitment: {},
        churn: {},
        progression: {}
      };
      
      LEVERS.forEach(leverType => {
        LEVELS.forEach(level => {
          mergedLevers[leverType][level] = externalLevers[leverType]?.[level] ?? defaultValue;
        });
      });
      
      setLevers(mergedLevers);
    }
  }, [externalLevers]);

  // Helper function to sanitize lever values
  const sanitizeLeverValue = (value: any): number => {
    if (value === null || value === undefined || value === '' || isNaN(value)) {
      return 1.0;
    }
    const numValue = Number(value);
    return isNaN(numValue) ? 1.0 : Math.max(0, numValue);
  };

  const handleSlider = (lever: LeverType, role: string, value: number[]) => {
    const sanitizedValue = sanitizeLeverValue(value[0]);
    setLevers(prev => ({
      ...prev,
      [lever]: { ...prev[lever], [role]: sanitizedValue },
    }));
  };

  const handleReset = (lever: LeverType) => {
    setLevers(prev => ({
      ...prev,
      [lever]: ROLES.reduce((racc, role) => {
        racc[role] = defaultValue;
        return racc;
      }, {} as Record<string, number>),
    }));
  };

  const getProgressionImpact = (role: string, multiplier: number) => {
    const catData = catProgressionData[role] || {};
    const impact: Record<string, { original: number; adjusted: number }> = {};
    
    Object.entries(catData).forEach(([cat, originalProb]) => {
      impact[cat] = {
        original: originalProb,
        adjusted: Math.min(originalProb * multiplier, 1.0)
      };
    });
    
    return impact;
  };

  const getMaxProgressionChange = (role: string) => {
    const multiplier = levers.progression[role];
    const impact = getProgressionImpact(role, multiplier);
    let maxChange = 0;
    let sign = '=';
    Object.values(impact).forEach(({ original, adjusted }) => {
      const diff = adjusted - original;
      if (Math.abs(diff) > Math.abs(maxChange)) {
        maxChange = diff;
        sign = diff > 0 ? '+' : diff < 0 ? '-' : '=';
      }
    });
    return { maxChange, sign };
  };

  const getExpectedTime = (role: string) => {
    const multiplier = levers.progression[role];
    const impact = getProgressionImpact(role, multiplier);
    let maxProb = 0;
    let maxOrigProb = 0;
    Object.values(impact).forEach(({ original, adjusted }) => {
      if (adjusted > maxProb) maxProb = adjusted;
      if (original > maxOrigProb) maxOrigProb = original;
    });
    
    let value = 'N/A';
    let origValue = '';
    if (maxProb > 0) {
      const expectedPeriods = 1 / maxProb;
      const expectedMonths = Math.round(expectedPeriods * 6);
      value = `${expectedMonths} mo`;
      if (multiplier !== 1.0 && maxOrigProb > 0) {
        const origPeriods = 1 / maxOrigProb;
        const origMonths = Math.round(origPeriods * 6);
        origValue = `${origMonths} mo`;
      }
    }
    return { value, origValue };
  };

  const columns: ColumnDef<LeverRowData>[] = [
    {
      accessorKey: "level",
      header: "Level",
      cell: ({ row }) => (
        <div className="font-medium">{row.getValue("level")}</div>
      ),
    },
    // Recruitment columns
    {
      accessorKey: "recruitment",
      header: ({ table }) => (
        <div className="flex items-center justify-between min-w-[200px]">
          <div className="flex items-center space-x-2">
            <span>Recruitment Multiplier</span>
          </div>
          {!readOnly && (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => handleReset('recruitment')}
              className="h-7"
            >
              <RotateCcw className="h-3 w-3 mr-1" />
              Reset
            </Button>
          )}
        </div>
      ),
      cell: ({ row }) => {
        const level = row.getValue("level") as string;
        const value = levers.recruitment[level];
        return readOnly ? (
          <span className="font-mono">{value.toFixed(2)}</span>
        ) : (
          <div className="flex items-center space-x-3">
            <Slider
              value={[value]}
              onValueChange={(val) => handleSlider('recruitment', level, val)}
              min={min}
              max={max}
              step={step}
              className="w-32"
            />
            <span className="font-mono w-12 text-right">{value.toFixed(2)}</span>
          </div>
        );
      },
    },
    {
      accessorKey: "recruitmentActual",
      header: "Recruitment Actual (avg/month)",
      cell: ({ row }) => {
        const level = row.getValue("level") as string;
        const baseline = baselineValues.recruitment[level] || 0;
        const multiplier = levers.recruitment[level];
        const actual = baseline * multiplier;
        const color = multiplier > 1 ? 'text-green-600' : multiplier < 1 ? 'text-red-600' : 'text-foreground';
        return <span className={cn("font-medium", color)}>{actual.toFixed(2)}</span>;
      },
    },
    // Churn columns
    {
      accessorKey: "churn",
      header: ({ table }) => (
        <div className="flex items-center justify-between min-w-[200px]">
          <div className="flex items-center space-x-2">
            <span>Churn Multiplier</span>
          </div>
          {!readOnly && (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => handleReset('churn')}
              className="h-7"
            >
              <RotateCcw className="h-3 w-3 mr-1" />
              Reset
            </Button>
          )}
        </div>
      ),
      cell: ({ row }) => {
        const level = row.getValue("level") as string;
        const value = levers.churn[level];
        return readOnly ? (
          <span className="font-mono">{value.toFixed(2)}</span>
        ) : (
          <div className="flex items-center space-x-3">
            <Slider
              value={[value]}
              onValueChange={(val) => handleSlider('churn', level, val)}
              min={min}
              max={max}
              step={step}
              className="w-32"
            />
            <span className="font-mono w-12 text-right">{value.toFixed(2)}</span>
          </div>
        );
      },
    },
    {
      accessorKey: "churnActual",
      header: "Churn Actual (avg/month)",
      cell: ({ row }) => {
        const level = row.getValue("level") as string;
        const baseline = baselineValues.churn[level] || 0;
        const multiplier = levers.churn[level];
        const actual = baseline * multiplier;
        const color = multiplier > 1 ? 'text-green-600' : multiplier < 1 ? 'text-red-600' : 'text-foreground';
        return <span className={cn("font-medium", color)}>{actual.toFixed(2)}</span>;
      },
    },
    // Progression columns
    {
      accessorKey: "progression",
      header: ({ table }) => (
        <div className="flex items-center justify-between min-w-[200px]">
          <div className="flex items-center space-x-2">
            <span>Progression Multiplier</span>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger>
                  <Info className="h-4 w-4 text-muted-foreground" />
                </TooltipTrigger>
                <TooltipContent>
                  <p>Progression multiplier affects CAT-based progression probabilities.</p>
                  <p>Values &lt; 1 slow progression, &gt; 1 accelerate it.</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
          {!readOnly && (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => handleReset('progression')}
              className="h-7"
            >
              <RotateCcw className="h-3 w-3 mr-1" />
              Reset
            </Button>
          )}
        </div>
      ),
      cell: ({ row }) => {
        const level = row.getValue("level") as string;
        const value = levers.progression[level];
        return readOnly ? (
          <span className="font-mono">{value.toFixed(2)}</span>
        ) : (
          <div className="flex items-center space-x-3">
            <Slider
              value={[value]}
              onValueChange={(val) => handleSlider('progression', level, val)}
              min={min}
              max={max}
              step={step}
              className="w-32"
            />
            <span className="font-mono w-12 text-right">{value.toFixed(2)}</span>
          </div>
        );
      },
    },
    {
      accessorKey: "progressionMaxChange",
      header: "Max Change",
      cell: ({ row }) => {
        const level = row.getValue("level") as string;
        const { maxChange, sign } = getMaxProgressionChange(level);
        const color = maxChange > 0 ? 'text-green-600' : maxChange < 0 ? 'text-red-600' : 'text-muted-foreground';
        const formatted = `${sign} ${(Math.abs(maxChange) * 100).toFixed(1)}%`;
        return <span className={cn("font-medium", color)}>{formatted}</span>;
      },
    },
    {
      accessorKey: "progressionExpectedTime",
      header: "Expected Time on Level",
      cell: ({ row }) => {
        const level = row.getValue("level") as string;
        const { value, origValue } = getExpectedTime(level);
        return (
          <div>
            <span className="font-medium">{value}</span>
            {origValue && (
              <span className="text-muted-foreground text-xs ml-2">(was {origValue})</span>
            )}
          </div>
        );
      },
    },
  ];

  // Prepare table data
  const tableData: LeverRowData[] = LEVELS.map(level => ({
    level,
    recruitment: levers.recruitment[level],
    recruitmentActual: baselineValues.recruitment[level] * levers.recruitment[level],
    churn: levers.churn[level],
    churnActual: baselineValues.churn[level] * levers.churn[level],
    progression: levers.progression[level],
    progressionMaxChange: 0, // Calculated in cell
    progressionExpectedTime: '', // Calculated in cell
  }));

  const renderLeverSection = (leverType: LeverType, title: string, colorClass: string) => (
    <Card className={`${colorClass} border-2`}>
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg text-white">{title}</CardTitle>
          {!readOnly && (
            <Button 
              variant="secondary" 
              size="sm" 
              onClick={() => handleReset(leverType)}
              className="h-8 bg-white/20 hover:bg-white/30 text-white border-white/30"
            >
              <RotateCcw className="h-3 w-3 mr-1" />
              Reset to 1.0
            </Button>
          )}
        </div>
        <CardDescription className="text-white/80">
          Adjust {leverType} rates by level (1.0 = baseline, 0.5 = half, below 1.0 to decrease, and above 1.0 to increase).
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 gap-4">
          {LEVELS.map(level => {
            const value = levers[leverType]?.[level] ?? defaultValue;
            const baseline = baselineValues[leverType][level] || 0;
            const actual = baseline * (value ?? defaultValue);
            
            return (
              <div key={level} className="bg-gray-900 p-4 rounded-lg border border-gray-700">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-white text-sm">{level}</span>
                  <span className="text-white/60 text-xs">Baseline</span>
                </div>
                
                {readOnly ? (
                  <div className="text-center">
                    <span className="font-mono text-white text-lg">{(value ?? defaultValue).toFixed(2)}</span>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <Slider
                      value={[value]}
                      onValueChange={(val) => handleSlider(leverType, level, val)}
                      min={min}
                      max={max}
                      step={step}
                      className="w-full"
                    />
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-white">{(value ?? defaultValue).toFixed(2)}</span>
                      <select className="bg-gray-800 text-white text-xs border border-gray-600 rounded px-1 py-0.5">
                        <option>Custom</option>
                      </select>
                    </div>
                  </div>
                )}
                
                {leverType !== 'progression' && (
                  <div className="mt-2 text-center">
                    <span className={cn(
                      "text-xs font-medium",
                      (value ?? defaultValue) > 1 ? 'text-green-400' : (value ?? defaultValue) < 1 ? 'text-red-400' : 'text-white/80'
                    )}>
                      {(actual ?? 0).toFixed(2)}
                    </span>
                  </div>
                )}
                
                {leverType === 'progression' && (
                  <div className="mt-2 text-center">
                    <div className={cn(
                      "text-xs font-medium",
                      (value ?? defaultValue) > 1 ? 'text-green-400' : (value ?? defaultValue) < 1 ? 'text-red-400' : 'text-white/80'
                    )}>
                      {getExpectedTime(level).value}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-white">Scenario Levers</h2>
        <p className="text-white/80">Configure multipliers and run simulation</p>
        <div className="text-sm text-white/60">Step 2 of 2</div>
        <div className="w-full bg-gray-700 rounded-full h-2 mb-6">
          <div className="bg-blue-500 h-2 rounded-full" style={{ width: '100%' }}></div>
        </div>
      </div>

      {/* Three-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {renderLeverSection('recruitment', 'Recruitment Multipliers', 'bg-green-800 border-green-600')}
        {renderLeverSection('churn', 'Churn Multipliers', 'bg-red-800 border-red-600')}
        {renderLeverSection('progression', 'Progression Multipliers', 'bg-blue-800 border-blue-600')}
      </div>

      {/* Test Your Scenario Section */}
      <Card className="bg-gray-800 border-gray-700">
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold text-white mb-2">Test Your Scenario</h3>
          <p className="text-white/80 mb-4">
            Run a simulation to preview the results before saving your scenario.
          </p>
          <Button 
            onClick={onRunSimulation} 
            className="bg-blue-600 hover:bg-blue-700 text-white"
            disabled={!onRunSimulation}
          >
            Run Simulation
          </Button>
        </CardContent>
      </Card>

      {/* Navigation */}
      {(!readOnly && (onNext || onBack)) && (
        <div className="flex justify-between">
          {onBack && (
            <Button variant="outline" onClick={onBack}>
              ← Back
            </Button>
          )}
          <div className="space-x-2">
            {onRunSimulation && (
              <Button onClick={onRunSimulation} variant="secondary" disabled={saving || simulating}>
                {simulating ? '🚀 Running...' : '🚀 Run & View Results'}
              </Button>
            )}
            {onNext && (
              <Button onClick={onNext} disabled={saving || simulating}>
                {saving ? 'Saving...' : 'Save Scenario'}
              </Button>
            )}
          </div>
        </div>
      )}
    </div>
  );
});

ScenarioLeversV2.displayName = 'ScenarioLeversV2';

export default ScenarioLeversV2;
export { baselineValues };