/**
 * Aggregated Plan View Component
 * 
 * Shows company-wide aggregated business plans across all offices
 */
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Globe, Building2, TrendingUp, DollarSign, Users } from 'lucide-react';
import type { OfficeConfig } from '../../types/office';

interface AggregatedPlanViewProps {
  offices: OfficeConfig[];
  year: number;
  onYearChange: (year: number) => void;
}

export const AggregatedPlanView: React.FC<AggregatedPlanViewProps> = ({
  offices,
  year,
  onYearChange
}) => {
  return (
    <div className="space-y-6">
      <div className="text-center py-12">
        <Globe className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
        <h3 className="text-xl font-semibold mb-2">Aggregated Business Planning</h3>
        <p className="text-muted-foreground mb-6 max-w-md mx-auto">
          This feature will allow you to view and manage business plans across all offices, 
          creating company-wide baselines for scenario planning.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto">
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <Building2 className="h-8 w-8 mx-auto text-primary mb-2" />
                <h4 className="font-medium">Multi-Office View</h4>
                <p className="text-sm text-muted-foreground">
                  Compare plans across all offices
                </p>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <TrendingUp className="h-8 w-8 mx-auto text-primary mb-2" />
                <h4 className="font-medium">Global Baseline</h4>
                <p className="text-sm text-muted-foreground">
                  Create company-wide scenario baselines
                </p>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <DollarSign className="h-8 w-8 mx-auto text-primary mb-2" />
                <h4 className="font-medium">Consolidated Analytics</h4>
                <p className="text-sm text-muted-foreground">
                  Company-wide financial projections
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        <Badge variant="secondary" className="mt-6">
          Coming Soon
        </Badge>
      </div>
    </div>
  );
};