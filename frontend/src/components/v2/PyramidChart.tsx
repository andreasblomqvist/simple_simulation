import * as React from "react"
import { cn } from "../../lib/utils"

export interface PyramidStage {
  stage: number
  label: string
  percentage: number
  description?: string
}

export interface PyramidChartProps {
  stages: PyramidStage[]
  className?: string
  colors?: string[]
  showLabels?: boolean
  showPercentages?: boolean
}

export function PyramidChart({
  stages,
  className,
  colors = [
    'bg-blue-500',
    'bg-green-500', 
    'bg-yellow-500',
    'bg-red-500'
  ],
  showLabels = true,
  showPercentages = true
}: PyramidChartProps) {
  // Sort stages by stage number in REVERSE order (4 at top, 1 at bottom)
  const sortedStages = [...stages].sort((a, b) => b.stage - a.stage)
  
  // Calculate widths based on percentages for visual hierarchy
  const maxPercentage = Math.max(...sortedStages.map(s => s.percentage))
  
  return (
    <div className={cn("w-full max-w-2xl mx-auto", className)}>
      <div className="space-y-2">
        {sortedStages.map((stage, index) => {
          // Calculate relative width (minimum 20% for visibility)
          const relativeWidth = Math.max(20, (stage.percentage / maxPercentage) * 100)
          const colorClass = colors[index % colors.length]
          
          return (
            <div key={stage.stage} className="flex items-center space-x-4">
              {/* Stage pyramid block */}
              <div className="flex-1 flex justify-center">
                <div 
                  className={cn(
                    "relative rounded-sm py-3 px-6 text-white font-medium text-sm transition-all duration-200 hover:shadow-lg",
                    colorClass
                  )}
                  style={{ width: `${relativeWidth}%` }}
                >
                  <div className="text-center">
                    {showLabels && (
                      <div className="font-semibold">
                        Journey {stage.stage}
                      </div>
                    )}
                    <div className="text-xs opacity-90">
                      {stage.label}
                    </div>
                    {showPercentages && (
                      <div className="text-lg font-bold mt-1">
                        {stage.percentage}%
                      </div>
                    )}
                  </div>
                </div>
              </div>
              
              {/* Optional description */}
              {stage.description && (
                <div className="text-xs text-gray-600 w-24 text-right">
                  {stage.description}
                </div>
              )}
            </div>
          )
        })}
      </div>
      
      {/* Legend */}
      <div className="mt-6 flex justify-center space-x-6 text-xs text-gray-600">
        {[...stages].sort((a, b) => a.stage - b.stage).map((stage, index) => {
          // Find the color index for this stage in the visual pyramid
          const visualIndex = sortedStages.findIndex(s => s.stage === stage.stage)
          return (
            <div key={stage.stage} className="flex items-center space-x-2">
              <div 
                className={cn("w-3 h-3 rounded-sm", colors[visualIndex % colors.length])}
              />
              <span>Journey {stage.stage}: {stage.label}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// Example usage data
export const exampleCareerJourneyData: PyramidStage[] = [
  {
    stage: 1,
    label: "Journey 1",
    percentage: 15,
    description: "Entry level"
  },
  {
    stage: 2, 
    label: "Journey 2",
    percentage: 69,
    description: "Mid level"
  },
  {
    stage: 3,
    label: "Journey 3", 
    percentage: 8,
    description: "Senior level"
  },
  {
    stage: 4,
    label: "Journey 4",
    percentage: 8,
    description: "Leadership level"
  }
]