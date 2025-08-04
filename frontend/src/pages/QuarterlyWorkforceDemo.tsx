import React from 'react';
import { QuarterlyWorkforceChart, exampleQuarterlyData, type QuarterData } from '../components/v2/QuarterlyWorkforceChart';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';

const QuarterlyWorkforceDemo: React.FC = () => {
  // Alternative smaller dataset for compact view
  const compactData: QuarterData[] = [
    {
      quarter: "Q1 2024",
      period: "Jan-Mar",
      data: [
        { level: "A", recruitment: 8, churn: 2, progression: 1 },
        { level: "C", recruitment: 4, churn: 1, progression: 2 },
        { level: "AM", recruitment: 1, churn: 0, progression: 1 },
        { level: "M", recruitment: 0, churn: 1, progression: 0 }
      ],
      journeyDistribution: {
        journey1: 72.1,
        journey2: 21.3,
        journey3: 4.8,
        journey4: 1.8
      },
      nonDebitRatio: 0.71
    },
    {
      quarter: "Q2 2024", 
      period: "Apr-Jun",
      data: [
        { level: "A", recruitment: 6, churn: 3, progression: 2 },
        { level: "C", recruitment: 3, churn: 0, progression: 1 },
        { level: "AM", recruitment: 2, churn: 1, progression: 0 },
        { level: "M", recruitment: 0, churn: 0, progression: 1 }
      ],
      journeyDistribution: {
        journey1: 68.9,
        journey2: 24.2,
        journey3: 4.7,
        journey4: 2.2
      },
      nonDebitRatio: 0.68
    }
  ];

  return (
    <div className="container mx-auto p-6 space-y-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Quarterly Workforce Analytics
        </h1>
        <p className="text-gray-600">
          Visualizing recruitment, churn, and progression across quarters and levels
        </p>
      </div>

      {/* Full Year View */}
      <Card>
        <CardHeader>
          <CardTitle>Annual Workforce Movement Analysis</CardTitle>
          <CardDescription>
            Complete view showing 4 quarters with recruitment (green), churn (red), and progression (blue) by level
          </CardDescription>
        </CardHeader>
        <CardContent>
          <QuarterlyWorkforceChart yearData={exampleQuarterlyData} />
        </CardContent>
      </Card>

      {/* Compact View */}
      <Card>
        <CardHeader>
          <CardTitle>Compact View - Half Year</CardTitle>
          <CardDescription>
            Simplified view showing 2 quarters for focused analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <QuarterlyWorkforceChart 
            yearData={compactData}
            title="H1 2024 Workforce Analytics"
          />
        </CardContent>
      </Card>

      {/* Without Journey Distribution */}
      <Card>
        <CardHeader>
          <CardTitle>Chart Only View</CardTitle>
          <CardDescription>
            Clean chart view without journey distribution details
          </CardDescription>
        </CardHeader>
        <CardContent>
          <QuarterlyWorkforceChart 
            yearData={compactData}
            showJourneyDistribution={false}
            title="Simplified Workforce Movement"
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
{`import { QuarterlyWorkforceChart } from '@/components/v2/QuarterlyWorkforceChart'

const quarterlyData = [
  {
    quarter: "Q1 2024",
    period: "Jan-Mar",
    data: [
      { level: "A", recruitment: 8, churn: 2, progression: 1 },
      { level: "C", recruitment: 4, churn: 1, progression: 2 }
    ],
    journeyDistribution: {
      journey1: 72.1, journey2: 21.3,
      journey3: 4.8, journey4: 1.8
    },
    nonDebitRatio: 0.71
  }
]

<QuarterlyWorkforceChart yearData={quarterlyData} />`}
            </pre>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-2">Props</h3>
            <div className="space-y-2 text-sm">
              <div><strong>yearData:</strong> QuarterData[] - Array of quarterly workforce data</div>
              <div><strong>className?:</strong> string - Additional CSS classes</div>
              <div><strong>showJourneyDistribution?:</strong> boolean - Show journey breakdown (default: true)</div>
              <div><strong>title?:</strong> string - Chart title (default: "Detailed View by Period")</div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-2">Data Structure</h3>
            <div className="space-y-2 text-sm">
              <div><strong>QuarterData:</strong></div>
              <ul className="ml-4 space-y-1">
                <li>• quarter: string - Quarter label (e.g., "Q1 2024")</li>
                <li>• period: string - Period description (e.g., "Jan-Mar")</li>
                <li>• data: WorkforceData[] - Level-wise workforce changes</li>
                <li>• journeyDistribution?: Journey percentages (1-4)</li>
                <li>• nonDebitRatio?: Non-debit workforce ratio</li>
              </ul>
              <div className="mt-2"><strong>WorkforceData:</strong></div>
              <ul className="ml-4 space-y-1">
                <li>• level: string - Career level (A, AC, C, SrC, etc.)</li>
                <li>• recruitment: number - Positive hires</li>
                <li>• churn: number - Positive departures</li>
                <li>• progression: number - Positive promotions</li>
              </ul>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-2">Features</h3>
            <ul className="space-y-1 text-sm">
              <li>• Stacked bar charts showing workforce changes by level</li>
              <li>• Color-coded: Green (recruitment), Red (churn), Blue (progression)</li>
              <li>• 2x2 or flexible grid layout for quarterly comparison</li>
              <li>• Optional journey distribution percentages</li>
              <li>• Non-debit ratio display</li>
              <li>• Responsive design with clean tooltips</li>
              <li>• Customizable titles and visibility options</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default QuarterlyWorkforceDemo;