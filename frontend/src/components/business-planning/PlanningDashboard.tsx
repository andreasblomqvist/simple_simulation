/**
 * Planning Dashboard Component
 * 
 * Analytics and insights for business planning performance
 */
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { TrendingUp, BarChart3, PieChart, Target } from 'lucide-react';
import type { OfficeConfig } from '../../types/office';

interface PlanningDashboardProps {
  offices: OfficeConfig[];
  selectedOffice: OfficeConfig | undefined;
  year: number;
  onYearChange: (year: number) => void;
}

export const PlanningDashboard: React.FC<PlanningDashboardProps> = ({
  offices,
  selectedOffice,
  year,
  onYearChange
}) => {
  return (
    <div className="space-y-6">
      <div className="text-center py-12">
        <BarChart3 className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
        <h3 className="text-xl font-semibold mb-2">Business Planning Analytics</h3>
        <p className="text-muted-foreground mb-6 max-w-md mx-auto">
          Comprehensive analytics and insights for your business planning performance,
          including trends, forecasts, and variance analysis.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 max-w-4xl mx-auto">
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <TrendingUp className="h-8 w-8 mx-auto text-primary mb-2" />
                <h4 className="font-medium">Growth Trends</h4>
                <p className="text-sm text-muted-foreground">
                  Historical and projected growth
                </p>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <Target className="h-8 w-8 mx-auto text-primary mb-2" />
                <h4 className="font-medium">Target vs Actual</h4>
                <p className="text-sm text-muted-foreground">
                  Performance against targets
                </p>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <PieChart className="h-8 w-8 mx-auto text-primary mb-2" />
                <h4 className="font-medium">Office Breakdown</h4>
                <p className="text-sm text-muted-foreground">
                  Performance by office
                </p>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <BarChart3 className="h-8 w-8 mx-auto text-primary mb-2" />
                <h4 className="font-medium">Financial KPIs</h4>
                <p className="text-sm text-muted-foreground">
                  Revenue, margin, and costs
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