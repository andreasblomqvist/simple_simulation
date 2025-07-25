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
  Calendar
} from 'lucide-react'

import { Button } from '../components/ui/button'
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '../components/ui/card'

interface DashboardV2Props {}

export const DashboardV2: React.FC<DashboardV2Props> = () => {
  // Mock data - would come from API in real implementation
  const stats = {
    totalOffices: 12,
    activeScenarios: 5,
    completedSimulations: 23,
    lastUpdated: '2 hours ago'
  }

  const recentScenarios = [
    { id: '1', name: 'Q4 Growth Analysis', status: 'completed', office: 'Stockholm' },
    { id: '2', name: 'Recruitment Optimization', status: 'running', office: 'Munich' },
    { id: '3', name: 'Cost Reduction Study', status: 'draft', office: 'All Offices' },
  ]

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Welcome to SimpleSim</h2>
        <p className="text-muted-foreground">
          Manage your office simulations and scenarios from this central dashboard.
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Offices</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalOffices}</div>
            <p className="text-xs text-muted-foreground">
              Across all regions
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Scenarios</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeScenarios}</div>
            <p className="text-xs text-muted-foreground">
              Currently running
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed Sims</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.completedSimulations}</div>
            <p className="text-xs text-muted-foreground">
              This month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Last Updated</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Live</div>
            <p className="text-xs text-muted-foreground">
              {stats.lastUpdated}
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Get started with common tasks
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Link to="/scenarios">
              <Button className="w-full justify-start" variant="outline">
                <Plus className="mr-2 h-4 w-4" />
                Create New Scenario
              </Button>
            </Link>
            
            <Link to="/offices">
              <Button className="w-full justify-start" variant="outline">
                <Building2 className="mr-2 h-4 w-4" />
                Manage Offices
              </Button>
            </Link>
            
            <Link to="/reports">
              <Button className="w-full justify-start" variant="outline">
                <BarChart3 className="mr-2 h-4 w-4" />
                View Reports
              </Button>
            </Link>
            
            <Link to="/settings">
              <Button className="w-full justify-start" variant="outline">
                <Settings className="mr-2 h-4 w-4" />
                Configure Settings
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Scenarios</CardTitle>
            <CardDescription>
              Latest simulation activity
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentScenarios.map((scenario) => (
                <div key={scenario.id} className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    <Target className="h-5 w-5 text-muted-foreground" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground truncate">
                      {scenario.name}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {scenario.office}
                    </p>
                  </div>
                  <div className="flex-shrink-0">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      scenario.status === 'completed' 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
                        : scenario.status === 'running'
                        ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300'
                        : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
                    }`}>
                      {scenario.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-4">
              <Link to="/scenarios">
                <Button variant="ghost" className="w-full">
                  View All Scenarios
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}