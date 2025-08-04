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
  TrendingDown,
  Users,
  Calendar,
  ArrowUpRight,
  ArrowDownRight,
  Clock,
  PlayCircle,
  PauseCircle,
  CheckCircle,
  FileText,
  Zap
} from 'lucide-react'

import { Button } from '../components/ui/button'
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Progress } from '../components/ui/progress'

// Import design system components
import { DashboardTemplate } from '../design-system/templates'
import { Stack, Grid } from '../design-system/layout'
import { Heading, Text } from '../design-system/typography'
import { useSetContextBar } from '../design-system/shell'

export const EnhancedDashboardV2: React.FC = () => {
  // Configure context bar for dashboard
  useSetContextBar({
    breadcrumb: {
      items: [
        { label: 'Dashboard', current: true }
      ]
    },
    primaryAction: {
      label: 'Create Scenario',
      onClick: () => window.location.href = '/scenarios',
      variant: 'primary',
      icon: <Plus className="h-4 w-4" />
    },
    secondaryActions: [
      {
        label: 'View Reports',
        onClick: () => window.location.href = '/reports',
        icon: <BarChart3 className="h-4 w-4" />
      }
    ]
  })

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

  // Modern KPI Card Component (shadcn dashboard-01 pattern)
  const ModernKPICard = ({ 
    title, 
    value, 
    change, 
    changeType, 
    icon: Icon 
  }: {
    title: string
    value: string | number
    change: string
    changeType: 'positive' | 'negative' | 'neutral'
    icon: React.ComponentType<{ className?: string }>
  }) => {
    const formatValue = (val: string | number): string => {
      if (typeof val === 'number') {
        if (val >= 1000000) return `${(val / 1000000).toFixed(1)}M`
        if (val >= 1000) return `${(val / 1000).toFixed(1)}K`
        return val.toString()
      }
      return val
    }

    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {title}
          </CardTitle>
          <Icon className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{formatValue(value)}</div>
          <p className={`text-xs flex items-center gap-1 ${
            changeType === 'positive' 
              ? 'text-green-600 dark:text-green-400' 
              : changeType === 'negative'
              ? 'text-red-600 dark:text-red-400'
              : 'text-muted-foreground'
          }`}>
            {changeType === 'positive' && <TrendingUp className="h-3 w-3" />}
            {changeType === 'negative' && <TrendingDown className="h-3 w-3" />}
            {change}
          </p>
        </CardContent>
      </Card>
    )
  }

  // Create KPI row component
  const kpiRow = (
    <>
      <ModernKPICard
        title="Total Offices"
        value={kpiData.totalOffices.current}
        change={`+${((kpiData.totalOffices.current - kpiData.totalOffices.previous) / kpiData.totalOffices.previous * 100).toFixed(1)}% from last month`}
        changeType="positive"
        icon={Building2}
      />
      
      <ModernKPICard
        title="Active Scenarios"
        value={kpiData.activeScenarios.current}
        change={`+${((kpiData.activeScenarios.current - kpiData.activeScenarios.previous) / kpiData.activeScenarios.previous * 100).toFixed(1)}% from last month`}
        changeType="positive"
        icon={Target}
      />
      
      <ModernKPICard
        title="Completed Simulations"
        value={kpiData.completedSimulations.current}
        change={`+${((kpiData.completedSimulations.current - kpiData.completedSimulations.previous) / kpiData.completedSimulations.previous * 100).toFixed(1)}% from last month`}
        changeType="positive"
        icon={CheckCircle}
      />
      
      <ModernKPICard
        title="Total Workforce"
        value={kpiData.totalWorkforce.current}
        change={`+${((kpiData.totalWorkforce.current - kpiData.totalWorkforce.previous) / kpiData.totalWorkforce.previous * 100).toFixed(1)}% from last month`}
        changeType="positive"
        icon={Users}
      />
    </>
  )

  // Create charts row components
  const chartsRow = {
    main: (
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Get started with common workforce simulation tasks
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-2">
          <Link to="/scenarios" className="group">
            <Card className="transition-all duration-200 hover:shadow-md cursor-pointer border-dashed">
              <CardContent className="flex items-center justify-center p-6">
                <div className="text-center space-y-2">
                  <div className="mx-auto w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Target className="h-6 w-6 text-primary" />
                  </div>
                  <div className="space-y-1">
                    <h3 className="font-semibold">Create Scenario</h3>
                    <p className="text-sm text-muted-foreground">Start a new workforce simulation</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </Link>
          
          <Link to="/offices" className="group">
            <Card className="transition-all duration-200 hover:shadow-md cursor-pointer">
              <CardContent className="flex items-center justify-center p-6">
                <div className="text-center space-y-2">
                  <div className="mx-auto w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Building2 className="h-6 w-6 text-blue-500" />
                  </div>
                  <div className="space-y-1">
                    <h3 className="font-semibold">Manage Offices</h3>
                    <p className="text-sm text-muted-foreground">Configure office settings</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </Link>
          
          <Link to="/reports" className="group">
            <Card className="transition-all duration-200 hover:shadow-md cursor-pointer">
              <CardContent className="flex items-center justify-center p-6">
                <div className="text-center space-y-2">
                  <div className="mx-auto w-12 h-12 bg-green-500/10 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                    <BarChart3 className="h-6 w-6 text-green-500" />
                  </div>
                  <div className="space-y-1">
                    <h3 className="font-semibold">View Reports</h3>
                    <p className="text-sm text-muted-foreground">Analyze simulation results</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </Link>
          
          <Link to="/settings" className="group">
            <Card className="transition-all duration-200 hover:shadow-md cursor-pointer">
              <CardContent className="flex items-center justify-center p-6">
                <div className="text-center space-y-2">
                  <div className="mx-auto w-12 h-12 bg-orange-500/10 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Settings className="h-6 w-6 text-orange-500" />
                  </div>
                  <div className="space-y-1">
                    <h3 className="font-semibold">Settings</h3>
                    <p className="text-sm text-muted-foreground">Configure platform settings</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </Link>
        </CardContent>
      </Card>
    ),
    sidebar: (
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>
            Latest scenarios and simulations
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {recentScenarios.map((scenario) => (
            <div key={scenario.id} className="flex items-start space-x-4 rounded-lg border p-3 transition-colors hover:bg-muted/50">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-muted">
                {scenario.status === 'completed' && <CheckCircle className="h-4 w-4 text-green-500" />}
                {scenario.status === 'running' && <PlayCircle className="h-4 w-4 text-blue-500" />}
                {scenario.status === 'draft' && <FileText className="h-4 w-4 text-gray-500" />}
              </div>
              <div className="flex-1 space-y-1">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium leading-none">
                    {scenario.name}
                  </p>
                  <Badge 
                    variant={scenario.status === 'completed' ? 'default' : scenario.status === 'running' ? 'secondary' : 'outline'}
                    className="ml-2 capitalize"
                  >
                    {scenario.status}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground">
                  {scenario.office}
                </p>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Clock className="h-3 w-3" />
                  {scenario.createdAt}
                </div>
                {scenario.status === 'running' && (
                  <div className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">Progress</span>
                      <span className="font-medium">{scenario.progress}%</span>
                    </div>
                    <Progress value={scenario.progress} className="h-2" />
                  </div>
                )}
              </div>
            </div>
          ))}
          
          <div className="pt-4 border-t">
            <Link to="/scenarios">
              <Button variant="outline" className="w-full justify-between">
                View All Scenarios
                <ArrowUpRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Create header with design system typography
  const header = (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <Zap className="h-8 w-8 text-primary" />
        <Heading level={1} className="text-3xl font-bold tracking-tight">
          Dashboard
        </Heading>
      </div>
      <Text variant="body-sm" color="muted" className="text-base">
        Welcome back! Here's an overview of your workforce simulation activity.
      </Text>
    </div>
  )

  // Modern data table for recent activity
  const tableRow = (
    <Card>
      <CardHeader>
        <CardTitle>System Overview</CardTitle>
        <CardDescription>
          Current status across all offices and scenarios
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <p className="text-sm font-medium text-muted-foreground">Active Simulations</p>
              <p className="text-2xl font-bold">3</p>
              <div className="flex items-center text-xs text-green-600">
                <TrendingUp className="mr-1 h-3 w-3" />
                Running smoothly
              </div>
            </div>
            <div className="space-y-2">
              <p className="text-sm font-medium text-muted-foreground">Processing Queue</p>
              <p className="text-2xl font-bold">0</p>
              <div className="flex items-center text-xs text-muted-foreground">
                <CheckCircle className="mr-1 h-3 w-3" />
                All clear
              </div>
            </div>
            <div className="space-y-2">
              <p className="text-sm font-medium text-muted-foreground">System Health</p>
              <p className="text-2xl font-bold text-green-600">Excellent</p>
              <div className="flex items-center text-xs text-muted-foreground">
                <Zap className="mr-1 h-3 w-3" />
                All systems operational
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )

  return (
    <DashboardTemplate
      header={header}
      kpiRow={kpiRow}
      chartsRow={chartsRow}
      tableRow={tableRow}
    />
  )
}