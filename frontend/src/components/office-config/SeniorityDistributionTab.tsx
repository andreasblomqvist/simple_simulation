/**
 * Seniority Distribution Tab Component
 * Displays seniority KPIs and distribution charts
 */
import React from 'react';
import { OfficeConfig, STANDARD_LEVELS, STANDARD_ROLES } from '../../types/office';
import { useBusinessPlanStore } from '../../stores/businessPlanStore';
import { KPICard } from './KPICard';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { TrendingUp, Users, Clock, Award } from 'lucide-react';

interface SeniorityDistributionTabProps {
  office: OfficeConfig;
}

export const SeniorityDistributionTab: React.FC<SeniorityDistributionTabProps> = ({ office }) => {
  const { currentWorkforce, loading } = useBusinessPlanStore();

  // Calculate seniority metrics
  const getSeniorityMetrics = () => {
    if (!currentWorkforce?.workforce) {
      return {
        averageTenure: 0,
        seniorRatio: 0,
        juniorRatio: 0,
        promotionRate: 0
      };
    }

    const workforce = currentWorkforce.workforce;
    const totalFte = workforce.reduce((sum, entry) => sum + entry.fte, 0);

    if (totalFte === 0) {
      return {
        averageTenure: 0,
        seniorRatio: 0,
        juniorRatio: 0,
        promotionRate: 0
      };
    }

    // Define seniority levels (simplified logic for demonstration)
    const seniorLevels = ['SrC', 'AM', 'M', 'SrM', 'PiP'];
    const juniorLevels = ['A', 'AC', 'C'];

    const seniorFte = workforce
      .filter(entry => seniorLevels.includes(entry.level))
      .reduce((sum, entry) => sum + entry.fte, 0);

    const juniorFte = workforce
      .filter(entry => juniorLevels.includes(entry.level))
      .reduce((sum, entry) => sum + entry.fte, 0);

    return {
      averageTenure: 2.5, // Mock data - would need historical data
      seniorRatio: Math.round((seniorFte / totalFte) * 100),
      juniorRatio: Math.round((juniorFte / totalFte) * 100),
      promotionRate: 15 // Mock data - would calculate from progression data
    };
  };

  // Get level distribution for chart
  const getLevelDistribution = () => {
    if (!currentWorkforce?.workforce) return [];

    const distribution = STANDARD_LEVELS.map(level => {
      const levelFte = currentWorkforce.workforce
        .filter(entry => entry.level === level)
        .reduce((sum, entry) => sum + entry.fte, 0);
      
      return {
        level,
        fte: levelFte,
        percentage: levelFte > 0 ? Math.round((levelFte / currentWorkforce.workforce.reduce((sum, entry) => sum + entry.fte, 0)) * 100) : 0
      };
    }).filter(item => item.fte > 0);

    return distribution;
  };

  const seniorityMetrics = getSeniorityMetrics();
  const levelDistribution = getLevelDistribution();

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <KPICard key={i} title="Loading..." value={0} loading={true} />
          ))}
        </div>
        <Card>
          <CardHeader>
            <CardTitle>Loading seniority data...</CardTitle>
          </CardHeader>
          <CardContent>
            <LoadingSpinner size="large" />
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Seniority KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Average Tenure"
          value={seniorityMetrics.averageTenure}
          unit="years"
          subtitle="Company-wide average"
          trend="neutral"
          variant="default"
        />
        <KPICard
          title="Senior Ratio"
          value={seniorityMetrics.seniorRatio}
          unit="%"
          subtitle="SrC+ levels"
          trend={seniorityMetrics.seniorRatio > 40 ? 'up' : 'neutral'}
          variant={seniorityMetrics.seniorRatio > 40 ? 'success' : 'default'}
        />
        <KPICard
          title="Junior Ratio"
          value={seniorityMetrics.juniorRatio}
          unit="%"
          subtitle="A-C levels"
          trend={seniorityMetrics.juniorRatio < 60 ? 'down' : 'neutral'}
          variant={seniorityMetrics.juniorRatio < 60 ? 'warning' : 'default'}
        />
        <KPICard
          title="Promotion Rate"
          value={seniorityMetrics.promotionRate}
          unit="%"
          subtitle="Annual promotions"
          trend="up"
          trendValue="+2%"
          variant="success"
        />
      </div>

      {/* Level Distribution */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Seniority Distribution
          </CardTitle>
        </CardHeader>
        <CardContent>
          {levelDistribution.length > 0 ? (
            <div className="space-y-4">
              {/* Simple bar chart visualization */}
              <div className="space-y-3">
                {levelDistribution.map((item) => (
                  <div key={item.level} className="flex items-center space-x-4">
                    <div className="w-8 text-sm font-medium text-right">
                      {item.level}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-4">
                          <div
                            className="bg-blue-600 h-4 rounded-full transition-all duration-300"
                            style={{ width: `${Math.max(item.percentage, 2)}%` }}
                          />
                        </div>
                        <div className="text-sm font-medium w-12 text-right">
                          {item.fte}
                        </div>
                        <div className="text-xs text-muted-foreground w-8 text-right">
                          {item.percentage}%
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Legend */}
              <div className="flex items-center justify-center space-x-6 text-xs text-muted-foreground mt-6 pt-4 border-t">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
                  <span>Current Distribution</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No seniority data available</p>
              <p className="text-sm mt-1">Configure workforce distribution to see seniority analysis</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Seniority Insights */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Award className="h-5 w-5" />
            Seniority Insights
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h4 className="font-medium">Current Status</h4>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• {seniorityMetrics.seniorRatio}% senior consultants (SrC+)</li>
                <li>• {seniorityMetrics.juniorRatio}% junior consultants (A-C)</li>
                <li>• {seniorityMetrics.promotionRate}% annual promotion rate</li>
                <li>• {seniorityMetrics.averageTenure} years average tenure</li>
              </ul>
            </div>
            <div className="space-y-3">
              <h4 className="font-medium">Recommendations</h4>
              <ul className="text-sm space-y-1 text-muted-foreground">
                {seniorityMetrics.seniorRatio < 30 && (
                  <li>• Consider hiring more senior talent</li>
                )}
                {seniorityMetrics.juniorRatio > 70 && (
                  <li>• High junior ratio - focus on retention & development</li>
                )}
                {seniorityMetrics.promotionRate > 20 && (
                  <li>• High promotion rate - ensure quality standards</li>
                )}
                <li>• Monitor progression curves for optimal growth</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};