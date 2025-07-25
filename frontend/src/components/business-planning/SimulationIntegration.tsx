/**
 * Simulation Integration Component
 * 
 * Interface for creating scenarios using business plans as baselines
 */
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Play, Globe, ArrowRight, Zap } from 'lucide-react';
import type { OfficeConfig } from '../../types/office';

interface SimulationIntegrationProps {
  offices: OfficeConfig[];
  selectedOffice: OfficeConfig | undefined;
  year: number;
  onCreateScenario: () => void;
  onCreateAggregatedBaseline: () => void;
}

export const SimulationIntegration: React.FC<SimulationIntegrationProps> = ({
  offices,
  selectedOffice,
  year,
  onCreateScenario,
  onCreateAggregatedBaseline
}) => {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Office Scenario Creation */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Play className="h-5 w-5" />
              Office Scenario
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Create a scenario using {selectedOffice?.name || 'an office'}'s business plan as the baseline.
              This will use the planned recruitment, pricing, and targets as starting values.
            </p>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Office:</span>
                <span className="font-medium">{selectedOffice?.name || 'None selected'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Year:</span>
                <span className="font-medium">{year}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Baseline:</span>
                <Badge variant="outline">Business Plan</Badge>
              </div>
            </div>

            <Button 
              onClick={onCreateScenario}
              disabled={!selectedOffice}
              className="w-full"
            >
              <Play className="h-4 w-4 mr-2" />
              Create Office Scenario
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </CardContent>
        </Card>

        {/* Aggregated Scenario Creation */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="h-5 w-5" />
              Company-Wide Scenario
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Create a scenario using aggregated business plans from all offices.
              This combines all office plans into a single baseline.
            </p>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Offices:</span>
                <span className="font-medium">{offices.length} offices</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Year:</span>
                <span className="font-medium">{year}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Baseline:</span>
                <Badge variant="outline">Aggregated Plans</Badge>
              </div>
            </div>

            <Button 
              onClick={onCreateAggregatedBaseline}
              disabled={offices.length === 0}
              className="w-full"
            >
              <Globe className="h-4 w-4 mr-2" />
              Create Global Scenario
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Integration Features */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Integration Features
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 border rounded-lg">
              <div className="flex items-center justify-center w-12 h-12 mx-auto mb-3 bg-primary/10 rounded-lg">
                <Play className="h-6 w-6 text-primary" />
              </div>
              <h4 className="font-medium mb-2">Seamless Transition</h4>
              <p className="text-sm text-muted-foreground">
                Business plan data flows directly into scenario setup
              </p>
            </div>

            <div className="text-center p-4 border rounded-lg">
              <div className="flex items-center justify-center w-12 h-12 mx-auto mb-3 bg-primary/10 rounded-lg">
                <ArrowRight className="h-6 w-6 text-primary" />
              </div>
              <h4 className="font-medium mb-2">Baseline Validation</h4>
              <p className="text-sm text-muted-foreground">
                Automatic validation ensures data compatibility
              </p>
            </div>

            <div className="text-center p-4 border rounded-lg">
              <div className="flex items-center justify-center w-12 h-12 mx-auto mb-3 bg-primary/10 rounded-lg">
                <Globe className="h-6 w-6 text-primary" />
              </div>
              <h4 className="font-medium mb-2">Results Comparison</h4>
              <p className="text-sm text-muted-foreground">
                Compare scenario outcomes against plan targets
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};