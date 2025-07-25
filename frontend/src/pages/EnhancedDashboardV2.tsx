import React from 'react'
import { Link } from 'react-router-dom'
import { 
  Building2, 
  Target, 
  Settings, 
  BarChart3,
  Plus,
  Activity,
  TrendingUp,
  Users,
  Calendar,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react'

import { Button } from '../components/ui/button'
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '../components/ui/card'
import { EnhancedKPICard } from '../components/ui/enhanced-kpi-card'
import { KPIGrid, ContentGrid } from '../components/layout/ResponsiveGrid'
import { Badge } from '../components/ui/badge'

export const EnhancedDashboardV2: React.FC = () => {
  // Mock data for KPI cards with historical trends
  const kpiData = {
    totalOffices: {
      current: 12,
      previous: 11,
      target: 15,
      sparklineData: [
        { period: '2024-01', value: 8 },
        { period: '2024-02', value: 9 },
        { period: '2024-03', value: 10 },
        { period: '2024-04', value: 11 },
        { period: '2024-05', value: 12 }
      ]
    },
    activeScenarios: {
      current: 5,
      previous: 3,
      target: 8,
      sparklineData: [
        { period: '2024-01', value: 2 },
        { period: '2024-02', value: 4 },
        { period: '2024-03', value: 3 },
        { period: '2024-04', value: 3 },
        { period: '2024-05', value: 5 }
      ]
    },
    completedSimulations: {
      current: 23,
      previous: 18,
      target: 30,
      sparklineData: [
        { period: '2024-01', value: 12 },
        { period: '2024-02', value: 15 },
        { period: '2024-03', value: 19 },
        { period: '2024-04', value: 18 },
        { period: '2024-05', value: 23 }
      ]
    },
    totalWorkforce: {
      current: 1247,
      previous: 1189,
      target: 1500,
      sparklineData: [
        { period: '2024-01', value: 1150 },
        { period: '2024-02', value: 1180 },
        { period: '2024-03', value: 1210 },
        { period: '2024-04', value: 1189 },
        { period: '2024-05', value: 1247 }
      ]
    }
  }

  const recentScenarios = [
    { 
      id: '1', 
      name: 'Q4 Growth Analysis', 
      status: 'completed', 
      office: 'Stockholm',
      progress: 100,
      createdAt: '2 days ago'
    },
    { 
      id: '2', 
      name: 'Recruitment Optimization', 
      status: 'running', 
      office: 'Munich',
      progress: 65,
      createdAt: '1 week ago'
    },
    { 
      id: '3', 
      name: 'Cost Reduction Study', 
      status: 'draft', 
      office: 'All Offices',
      progress: 20,
      createdAt: '3 days ago'
    },
    {
      id: '4',
      name: 'Remote Work Impact',
      status: 'completed',
      office: 'London',
      progress: 100,
      createdAt: '1 week ago'
    }
  ]

  const getStatusVariant = (status: string) => {
    switch (status) {
      case 'completed':
        return 'default'
      case 'running':
        return 'secondary'
      case 'draft':
        return 'outline'
      default:
        return 'outline'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 dark:text-green-400'
      case 'running':
        return 'text-blue-600 dark:text-blue-400'
      case 'draft':
        return 'text-gray-600 dark:text-gray-400'
      default:
        return 'text-gray-600'
    }
  }

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Welcome back</h1>
        <p className="text-muted-foreground">
          Here's an overview of your workforce simulation platform activity.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Key Metrics</h2>
          <Button variant="outline" size="sm">
            <BarChart3 className="mr-2 h-4 w-4" />
            View All Reports
          </Button>
        </div>
        
        <KPIGrid>
          <EnhancedKPICard
            title="Total Offices"
            value={kpiData.totalOffices.current}
            previousValue={kpiData.totalOffices.previous}
            target={kpiData.totalOffices.target}
            sparklineData={kpiData.totalOffices.sparklineData}
            description="Number of office locations across all regions"
            formatter={(value) => value.toString()}
          />
          
          <EnhancedKPICard
            title="Active Scenarios"
            value={kpiData.activeScenarios.current}
            previousValue={kpiData.activeScenarios.previous}
            target={kpiData.activeScenarios.target}
            sparklineData={kpiData.activeScenarios.sparklineData}
            description="Currently running simulation scenarios"
            formatter={(value) => value.toString()}
            variant={kpiData.activeScenarios.current > kpiData.activeScenarios.previous ? 'success' : 'default'}
          />
          
          <EnhancedKPICard
            title="Completed Simulations"
            value={kpiData.completedSimulations.current}
            previousValue={kpiData.completedSimulations.previous}
            target={kpiData.completedSimulations.target}
            sparklineData={kpiData.completedSimulations.sparklineData}
            description="Successfully completed simulations this month"
            formatter={(value) => value.toString()}
          />
          
          <EnhancedKPICard
            title="Total Workforce"
            value={kpiData.totalWorkforce.current}
            previousValue={kpiData.totalWorkforce.previous}
            target={kpiData.totalWorkforce.target}
            sparklineData={kpiData.totalWorkforce.sparklineData}
            description="Total employees across all offices"
            formatter={(value) => value.toLocaleString()}
          />
        </KPIGrid>
      </div>

      <ContentGrid>
        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Plus className="h-5 w-5" />
              Quick Actions
            </CardTitle>
            <CardDescription>
              Get started with common tasks
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Link to="/scenarios" className="block">
              <Button className="w-full justify-start" variant="outline">
                <Target className="mr-2 h-4 w-4" />
                Create New Scenario
                <ArrowUpRight className="ml-auto h-4 w-4" />
              </Button>
            </Link>
            
            <Link to="/offices" className="block">
              <Button className="w-full justify-start" variant="outline">
                <Building2 className="mr-2 h-4 w-4" />
                Manage Offices
                <ArrowUpRight className="ml-auto h-4 w-4" />
              </Button>
            </Link>
            
            <Link to="/reports" className="block">
              <Button className="w-full justify-start" variant="outline">
                <BarChart3 className="mr-2 h-4 w-4" />
                View Reports
                <ArrowUpRight className="ml-auto h-4 w-4" />
              </Button>
            </Link>
            
            <Link to="/settings" className="block">
              <Button className="w-full justify-start" variant="outline">
                <Settings className="mr-2 h-4 w-4" />
                Configure Settings
                <ArrowUpRight className="ml-auto h-4 w-4" />
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Recent Scenarios
                </CardTitle>
                <CardDescription>
                  Latest simulation activity
                </CardDescription>
              </div>
              <Badge variant="secondary">
                {recentScenarios.length} active
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentScenarios.map((scenario) => (
                <div key={scenario.id} className="flex items-center justify-between p-3 rounded-lg border bg-muted/50">
                  <div className="flex items-start space-x-3">
                    <Target className="h-5 w-5 text-muted-foreground mt-0.5" />
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium text-foreground">
                          {scenario.name}
                        </p>
                        <Badge variant={getStatusVariant(scenario.status)}>
                          {scenario.status}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {scenario.office} • {scenario.createdAt}
                      </p>
                      {scenario.status === 'running' && (
                        <div className="w-32 bg-background rounded-full h-1.5">
                          <div 
                            className="bg-primary h-1.5 rounded-full transition-all"
                            style={{ width: `${scenario.progress}%` }}
                          />
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {scenario.status === 'running' && (
                      <span className="text-xs font-medium text-muted-foreground">
                        {scenario.progress}%
                      </span>
                    )}
                    <Button variant="ghost" size="sm">
                      <ArrowUpRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-4 pt-4 border-t">
              <Link to="/scenarios">
                <Button variant="ghost" className="w-full">
                  View All Scenarios
                  <ArrowUpRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </ContentGrid>
    </div>
  )
}