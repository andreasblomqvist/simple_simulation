import React, { useCallback, useMemo, useState } from 'react'
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  TooltipProps
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import { 
  Download, 
  Maximize2, 
  TrendingUp, 
  TrendingDown,
  MoreHorizontal,
  Filter
} from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator
} from '../ui/dropdown-menu'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog'
import { cn } from '../../lib/utils'

// Color palette for charts
const CHART_COLORS = [
  'hsl(var(--primary))',
  'hsl(var(--chart-secondary))',
  'hsl(var(--chart-accent))',
  '#8884d8',
  '#82ca9d',
  '#ffc658',
  '#ff7c7c',
  '#8dd1e1'
]

interface BaseChartProps {
  /** Chart data */
  data: any[]
  /** Chart title */
  title?: string
  /** Chart subtitle */
  subtitle?: string
  /** Height of the chart */
  height?: number
  /** Loading state */
  loading?: boolean
  /** Enable export functionality */
  exportable?: boolean
  /** Export handler */
  onExport?: () => void
  /** Additional actions */
  actions?: React.ReactNode
  /** Custom CSS classes */
  className?: string
}

// Custom tooltip component with better styling
const CustomTooltip = ({ active, payload, label, formatter }: TooltipProps<any, any> & { formatter?: (value: any, name: string) => [React.ReactNode, string] }) => {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-lg border bg-background p-3 shadow-md">
        <p className="font-medium text-sm mb-2">{label}</p>
        {payload.map((pld, index) => (
          <div key={index} className="flex items-center gap-2 text-sm">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: pld.color }}
            />
            <span className="text-muted-foreground">{pld.dataKey}:</span>
            <span className="font-medium">
              {formatter ? formatter(pld.value, pld.dataKey || '')[0] : pld.value}
            </span>
          </div>
        ))}
      </div>
    )
  }
  return null
}

// Chart container with common functionality
const ChartContainer: React.FC<BaseChartProps & { children: React.ReactNode }> = ({
  children,
  title,
  subtitle,
  height = 300,
  loading,
  exportable,
  onExport,
  actions,
  className
}) => {
  const [isFullscreen, setIsFullscreen] = useState(false)

  return (
    <>
      <Card className={cn("chart-container", className)}>
        <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
          <div className="space-y-1">
            {title && <CardTitle className="text-base">{title}</CardTitle>}
            {subtitle && <p className="text-sm text-muted-foreground">{subtitle}</p>}
          </div>
          
          <div className="flex items-center gap-2">
            {actions}
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => setIsFullscreen(true)}>
                  <Maximize2 className="mr-2 h-4 w-4" />
                  Fullscreen
                </DropdownMenuItem>
                {exportable && (
                  <DropdownMenuItem onClick={onExport}>
                    <Download className="mr-2 h-4 w-4" />
                    Export
                  </DropdownMenuItem>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </CardHeader>
        
        <CardContent>
          {loading ? (
            <div className="h-[300px] flex items-center justify-center">
              <div className="animate-pulse space-y-3 w-full">
                <div className="h-4 bg-muted rounded w-3/4" />
                <div className="h-40 bg-muted rounded" />
                <div className="h-4 bg-muted rounded w-1/2" />
              </div>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={height}>
              {children}
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      {/* Fullscreen Dialog */}
      <Dialog open={isFullscreen} onOpenChange={setIsFullscreen}>
        <DialogContent className="max-w-6xl max-h-[90vh] overflow-hidden">
          <DialogHeader>
            <DialogTitle>{title}</DialogTitle>
          </DialogHeader>
          <div className="flex-1 overflow-hidden">
            <ResponsiveContainer width="100%" height={600}>
              {children}
            </ResponsiveContainer>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}

// Enhanced Line Chart
interface EnhancedLineChartProps extends BaseChartProps {
  /** X-axis data key */
  xAxisKey: string
  /** Line configurations */
  lines: {
    key: string
    name: string
    color?: string
    strokeWidth?: number
    strokeDasharray?: string
  }[]
  /** Value formatter */
  valueFormatter?: (value: any) => string
}

export function EnhancedLineChart({
  data,
  xAxisKey,
  lines,
  valueFormatter,
  ...props
}: EnhancedLineChartProps) {
  const chart = (
    <LineChart data={data}>
      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--chart-grid))" />
      <XAxis 
        dataKey={xAxisKey} 
        stroke="hsl(var(--muted-foreground))"
        fontSize={12}
      />
      <YAxis 
        stroke="hsl(var(--muted-foreground))"
        fontSize={12}
        tickFormatter={valueFormatter}
      />
      <Tooltip 
        content={<CustomTooltip formatter={valueFormatter} />}
      />
      {lines.map((line, index) => (
        <Line
          key={line.key}
          type="monotone"
          dataKey={line.key}
          stroke={line.color || CHART_COLORS[index % CHART_COLORS.length]}
          strokeWidth={line.strokeWidth || 2}
          strokeDasharray={line.strokeDasharray}
          dot={{ fill: line.color || CHART_COLORS[index % CHART_COLORS.length], strokeWidth: 2 }}
        />
      ))}
    </LineChart>
  )

  return <ChartContainer {...props}>{chart}</ChartContainer>
}

// Enhanced Bar Chart
interface EnhancedBarChartProps extends BaseChartProps {
  /** X-axis data key */
  xAxisKey: string
  /** Bar configurations */
  bars: {
    key: string
    name: string
    color?: string
  }[]
  /** Value formatter */
  valueFormatter?: (value: any) => string
  /** Stack bars */
  stacked?: boolean
}

export function EnhancedBarChart({
  data,
  xAxisKey,
  bars,
  valueFormatter,
  stacked = false,
  ...props
}: EnhancedBarChartProps) {
  const chart = (
    <BarChart data={data}>
      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--chart-grid))" />
      <XAxis 
        dataKey={xAxisKey} 
        stroke="hsl(var(--muted-foreground))"
        fontSize={12}
      />
      <YAxis 
        stroke="hsl(var(--muted-foreground))"
        fontSize={12}
        tickFormatter={valueFormatter}
      />
      <Tooltip 
        content={<CustomTooltip formatter={valueFormatter} />}
      />
      {bars.map((bar, index) => (
        <Bar
          key={bar.key}
          dataKey={bar.key}
          stackId={stacked ? 'a' : undefined}
          fill={bar.color || CHART_COLORS[index % CHART_COLORS.length]}
        />
      ))}
    </BarChart>
  )

  return <ChartContainer {...props}>{chart}</ChartContainer>
}

// Enhanced Area Chart
interface EnhancedAreaChartProps extends BaseChartProps {
  /** X-axis data key */
  xAxisKey: string
  /** Area configurations */
  areas: {
    key: string
    name: string
    color?: string
  }[]
  /** Value formatter */
  valueFormatter?: (value: any) => string
  /** Stack areas */
  stacked?: boolean
}

export function EnhancedAreaChart({
  data,
  xAxisKey,
  areas,
  valueFormatter,
  stacked = false,
  ...props
}: EnhancedAreaChartProps) {
  const chart = (
    <AreaChart data={data}>
      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--chart-grid))" />
      <XAxis 
        dataKey={xAxisKey} 
        stroke="hsl(var(--muted-foreground))"
        fontSize={12}
      />
      <YAxis 
        stroke="hsl(var(--muted-foreground))"
        fontSize={12}
        tickFormatter={valueFormatter}
      />
      <Tooltip 
        content={<CustomTooltip formatter={valueFormatter} />}
      />
      {areas.map((area, index) => (
        <Area
          key={area.key}
          type="monotone"
          dataKey={area.key}
          stackId={stacked ? 'a' : undefined}
          stroke={area.color || CHART_COLORS[index % CHART_COLORS.length]}
          fill={area.color || CHART_COLORS[index % CHART_COLORS.length]}
          fillOpacity={0.6}
        />
      ))}
    </AreaChart>
  )

  return <ChartContainer {...props}>{chart}</ChartContainer>
}

// Enhanced Pie Chart
interface EnhancedPieChartProps extends BaseChartProps {
  /** Data key for values */
  dataKey: string
  /** Name key */
  nameKey: string
  /** Inner radius (for donut charts) */
  innerRadius?: number
  /** Show labels */
  showLabels?: boolean
  /** Value formatter */
  valueFormatter?: (value: any) => string
}

export function EnhancedPieChart({
  data,
  dataKey,
  nameKey,
  innerRadius = 0,
  showLabels = true,
  valueFormatter,
  ...props
}: EnhancedPieChartProps) {
  const chart = (
    <PieChart>
      <Pie
        data={data}
        cx="50%"
        cy="50%"
        innerRadius={innerRadius}
        outerRadius={80}
        fill="#8884d8"
        dataKey={dataKey}
        label={showLabels}
      >
        {data.map((entry, index) => (
          <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
        ))}
      </Pie>
      <Tooltip 
        content={<CustomTooltip formatter={valueFormatter} />}
      />
    </PieChart>
  )

  return <ChartContainer {...props}>{chart}</ChartContainer>
}

// Trend indicator component for charts
interface TrendIndicatorProps {
  value: number
  previousValue: number
  formatter?: (value: number) => string
  className?: string
}

export function TrendIndicator({ value, previousValue, formatter, className }: TrendIndicatorProps) {
  const change = previousValue !== 0 ? ((value - previousValue) / Math.abs(previousValue)) * 100 : 0
  const isPositive = change > 0
  const isNeutral = Math.abs(change) < 0.1

  const Icon = isNeutral ? null : isPositive ? TrendingUp : TrendingDown
  const colorClass = isNeutral 
    ? 'text-muted-foreground' 
    : isPositive 
      ? 'text-green-600 dark:text-green-500' 
      : 'text-red-600 dark:text-red-500'

  return (
    <div className={cn("flex items-center gap-2", className)}>
      <Badge variant={isPositive ? 'default' : isNeutral ? 'secondary' : 'destructive'}>
        {Icon && <Icon className="mr-1 h-3 w-3" />}
        {Math.abs(change).toFixed(1)}%
      </Badge>
      <span className="text-sm text-muted-foreground">
        vs. previous period
      </span>
    </div>
  )
}