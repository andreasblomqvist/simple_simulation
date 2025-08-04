import React from 'react'
import { PyramidChart, exampleCareerJourneyData, type PyramidStage } from '../components/v2/PyramidChart'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'

const PyramidChartDemo: React.FC = () => {
  // Alternative data sets for demonstration
  const skillLevelData: PyramidStage[] = [
    { stage: 1, label: "Journey 1", percentage: 25, description: "Learning basics" },
    { stage: 2, label: "Journey 2", percentage: 45, description: "Building competence" },
    { stage: 3, label: "Journey 3", percentage: 20, description: "Expert level" },
    { stage: 4, label: "Journey 4", percentage: 10, description: "Teaching others" }
  ]

  const organizationData: PyramidStage[] = [
    { stage: 1, label: "Journey 1", percentage: 60 },
    { stage: 2, label: "Journey 2", percentage: 25 },
    { stage: 3, label: "Journey 3", percentage: 12 },
    { stage: 4, label: "Journey 4", percentage: 3 }
  ]

  return (
    <div className="container mx-auto p-6 space-y-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Pyramid Chart Component Demo
        </h1>
        <p className="text-gray-600">
          Visualizing hierarchical data with responsive pyramid diagrams
        </p>
      </div>

      {/* Career Journey Example */}
      <Card>
        <CardHeader>
          <CardTitle>Career Journey Distribution</CardTitle>
          <CardDescription>
            Shows the distribution of employees across different career stages
          </CardDescription>
        </CardHeader>
        <CardContent>
          <PyramidChart 
            stages={exampleCareerJourneyData}
            colors={['bg-red-500', 'bg-yellow-500', 'bg-green-500', 'bg-blue-500']}
          />
        </CardContent>
      </Card>

      {/* Skill Level Example */}
      <Card>
        <CardHeader>
          <CardTitle>Skill Level Distribution</CardTitle>
          <CardDescription>
            Technical skill progression across the organization
          </CardDescription>
        </CardHeader>
        <CardContent>
          <PyramidChart 
            stages={skillLevelData}
            colors={['bg-orange-500', 'bg-purple-500', 'bg-blue-500', 'bg-emerald-500']}
          />
        </CardContent>
      </Card>

      {/* Organization Hierarchy Example */}
      <Card>
        <CardHeader>
          <CardTitle>Organization Hierarchy</CardTitle>
          <CardDescription>
            Employee distribution across organizational levels
          </CardDescription>
        </CardHeader>
        <CardContent>
          <PyramidChart 
            stages={organizationData}
            colors={['bg-gray-800', 'bg-gray-700', 'bg-gray-600', 'bg-slate-500']}
            showLabels={false}
          />
        </CardContent>
      </Card>

      {/* Compact Version */}
      <Card>
        <CardHeader>
          <CardTitle>Compact Version</CardTitle>
          <CardDescription>
            Minimal pyramid chart without descriptions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <PyramidChart 
            stages={exampleCareerJourneyData.map(stage => ({ ...stage, description: undefined }))}
            className="max-w-lg"
            showPercentages={false}
          />
        </CardContent>
      </Card>

      {/* Implementation Guide */}
      <Card>
        <CardHeader>
          <CardTitle>Implementation Guide</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold mb-2">Basic Usage</h3>
            <pre className="bg-gray-100 p-4 rounded-md text-sm overflow-x-auto">
{`import { PyramidChart, exampleCareerJourneyData } from '@/components/v2/PyramidChart'

const data = [
  { stage: 1, label: "New", percentage: 15 },
  { stage: 2, label: "Emerging", percentage: 69 },
  { stage: 3, label: "Established", percentage: 8 },
  { stage: 4, label: "Mature", percentage: 8 }
]

<PyramidChart stages={data} />`}
            </pre>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-2">Props</h3>
            <div className="space-y-2 text-sm">
              <div><strong>stages:</strong> PyramidStage[] - Array of stages with stage number, label, and percentage</div>
              <div><strong>colors?:</strong> string[] - Custom Tailwind color classes for each stage</div>
              <div><strong>showLabels?:</strong> boolean - Show/hide "Journey X" labels (default: true)</div>
              <div><strong>showPercentages?:</strong> boolean - Show/hide percentage values (default: true)</div>
              <div><strong>className?:</strong> string - Additional CSS classes</div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-2">Features</h3>
            <ul className="space-y-1 text-sm">
              <li>• Responsive design that adapts to container width</li>
              <li>• Customizable colors with Tailwind CSS classes</li>
              <li>• Automatic width calculation based on percentage values</li>
              <li>• Optional labels, percentages, and descriptions</li>
              <li>• Hover effects with smooth transitions</li>
              <li>• Legend showing all stages</li>
              <li>• TypeScript support with full type definitions</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default PyramidChartDemo