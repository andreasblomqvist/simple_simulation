/**
 * Simulation Lab page
 */
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Beaker, Play } from 'lucide-react';

export const SimulationLab: React.FC = () => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Beaker className="h-5 w-5" />
          Simulation Lab
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <Beaker className="h-16 w-16 text-green-500 mb-4" />
          <h3 className="text-2xl font-semibold mb-2">Simulation Laboratory</h3>
          <p className="text-muted-foreground mb-6 max-w-md">
            Run simulations and experiments to test different scenarios and analyze their outcomes.
          </p>
          <Button size="lg">
            <Play className="mr-2 h-4 w-4" />
            Start Simulation
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};