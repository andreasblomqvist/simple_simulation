import React from 'react'
import { cn } from '../../lib/utils'

interface ResponsiveGridProps {
  children: React.ReactNode
  /** Grid configuration for different breakpoints */
  cols?: {
    default?: number
    sm?: number
    md?: number
    lg?: number
    xl?: number
    '2xl'?: number
  }
  /** Gap between grid items */
  gap?: 'none' | 'sm' | 'md' | 'lg' | 'xl'
  /** Custom CSS classes */
  className?: string
}

interface GridItemProps {
  children: React.ReactNode
  /** Column span for different breakpoints */
  colSpan?: {
    default?: number
    sm?: number
    md?: number
    lg?: number
    xl?: number
    '2xl'?: number
  }
  /** Row span */
  rowSpan?: number
  /** Custom CSS classes */
  className?: string
}

const gapClasses = {
  none: 'gap-0',
  sm: 'gap-2',
  md: 'gap-4',
  lg: 'gap-6',
  xl: 'gap-8'
}

const colClasses = {
  1: 'grid-cols-1',
  2: 'grid-cols-2',
  3: 'grid-cols-3',
  4: 'grid-cols-4',
  5: 'grid-cols-5',
  6: 'grid-cols-6',
  7: 'grid-cols-7',
  8: 'grid-cols-8',
  9: 'grid-cols-9',
  10: 'grid-cols-10',
  11: 'grid-cols-11',
  12: 'grid-cols-12'
}

const responsiveColClasses = {
  sm: {
    1: 'sm:grid-cols-1',
    2: 'sm:grid-cols-2',
    3: 'sm:grid-cols-3',
    4: 'sm:grid-cols-4',
    5: 'sm:grid-cols-5',
    6: 'sm:grid-cols-6',
    7: 'sm:grid-cols-7',
    8: 'sm:grid-cols-8',
    9: 'sm:grid-cols-9',
    10: 'sm:grid-cols-10',
    11: 'sm:grid-cols-11',
    12: 'sm:grid-cols-12'
  },
  md: {
    1: 'md:grid-cols-1',
    2: 'md:grid-cols-2',
    3: 'md:grid-cols-3',
    4: 'md:grid-cols-4',
    5: 'md:grid-cols-5',
    6: 'md:grid-cols-6',
    7: 'md:grid-cols-7',
    8: 'md:grid-cols-8',
    9: 'md:grid-cols-9',
    10: 'md:grid-cols-10',
    11: 'md:grid-cols-11',
    12: 'md:grid-cols-12'
  },
  lg: {
    1: 'lg:grid-cols-1',
    2: 'lg:grid-cols-2',
    3: 'lg:grid-cols-3',
    4: 'lg:grid-cols-4',
    5: 'lg:grid-cols-5',
    6: 'lg:grid-cols-6',
    7: 'lg:grid-cols-7',
    8: 'lg:grid-cols-8',
    9: 'lg:grid-cols-9',
    10: 'lg:grid-cols-10',
    11: 'lg:grid-cols-11',
    12: 'lg:grid-cols-12'
  },
  xl: {
    1: 'xl:grid-cols-1',
    2: 'xl:grid-cols-2',
    3: 'xl:grid-cols-3',
    4: 'xl:grid-cols-4',
    5: 'xl:grid-cols-5',
    6: 'xl:grid-cols-6',
    7: 'xl:grid-cols-7',
    8: 'xl:grid-cols-8',
    9: 'xl:grid-cols-9',
    10: 'xl:grid-cols-10',
    11: 'xl:grid-cols-11',
    12: 'xl:grid-cols-12'
  },
  '2xl': {
    1: '2xl:grid-cols-1',
    2: '2xl:grid-cols-2',
    3: '2xl:grid-cols-3',
    4: '2xl:grid-cols-4',
    5: '2xl:grid-cols-5',
    6: '2xl:grid-cols-6',
    7: '2xl:grid-cols-7',
    8: '2xl:grid-cols-8',
    9: '2xl:grid-cols-9',
    10: '2xl:grid-cols-10',
    11: '2xl:grid-cols-11',
    12: '2xl:grid-cols-12'
  }
}

const colSpanClasses = {
  1: 'col-span-1',
  2: 'col-span-2',
  3: 'col-span-3',
  4: 'col-span-4',
  5: 'col-span-5',
  6: 'col-span-6',
  7: 'col-span-7',
  8: 'col-span-8',
  9: 'col-span-9',
  10: 'col-span-10',
  11: 'col-span-11',
  12: 'col-span-12'
}

const responsiveColSpanClasses = {
  sm: {
    1: 'sm:col-span-1',
    2: 'sm:col-span-2',
    3: 'sm:col-span-3',
    4: 'sm:col-span-4',
    5: 'sm:col-span-5',
    6: 'sm:col-span-6',
    7: 'sm:col-span-7',
    8: 'sm:col-span-8',
    9: 'sm:col-span-9',
    10: 'sm:col-span-10',
    11: 'sm:col-span-11',
    12: 'sm:col-span-12'
  },
  md: {
    1: 'md:col-span-1',
    2: 'md:col-span-2',
    3: 'md:col-span-3',
    4: 'md:col-span-4',
    5: 'md:col-span-5',
    6: 'md:col-span-6',
    7: 'md:col-span-7',
    8: 'md:col-span-8',
    9: 'md:col-span-9',
    10: 'md:col-span-10',
    11: 'md:col-span-11',
    12: 'md:col-span-12'
  },
  lg: {
    1: 'lg:col-span-1',
    2: 'lg:col-span-2',
    3: 'lg:col-span-3',
    4: 'lg:col-span-4',
    5: 'lg:col-span-5',
    6: 'lg:col-span-6',
    7: 'lg:col-span-7',
    8: 'lg:col-span-8',
    9: 'lg:col-span-9',
    10: 'lg:col-span-10',
    11: 'lg:col-span-11',
    12: 'lg:col-span-12'
  },
  xl: {
    1: 'xl:col-span-1',
    2: 'xl:col-span-2',
    3: 'xl:col-span-3',
    4: 'xl:col-span-4',
    5: 'xl:col-span-5',
    6: 'xl:col-span-6',
    7: 'xl:col-span-7',
    8: 'xl:col-span-8',
    9: 'xl:col-span-9',
    10: 'xl:col-span-10',
    11: 'xl:col-span-11',
    12: 'xl:col-span-12'
  },
  '2xl': {
    1: '2xl:col-span-1',
    2: '2xl:col-span-2',
    3: '2xl:col-span-3',
    4: '2xl:col-span-4',
    5: '2xl:col-span-5',
    6: '2xl:col-span-6',
    7: '2xl:col-span-7',
    8: '2xl:col-span-8',
    9: '2xl:col-span-9',
    10: '2xl:col-span-10',
    11: '2xl:col-span-11',
    12: '2xl:col-span-12'
  }
}

export function ResponsiveGrid({
  children,
  cols = { default: 1, md: 2, lg: 3 },
  gap = 'md',
  className
}: ResponsiveGridProps) {
  const gridClasses = [
    'grid',
    gapClasses[gap]
  ]

  // Add responsive column classes
  if (cols.default) gridClasses.push(colClasses[cols.default as keyof typeof colClasses])
  if (cols.sm) gridClasses.push(responsiveColClasses.sm[cols.sm as keyof typeof responsiveColClasses.sm])
  if (cols.md) gridClasses.push(responsiveColClasses.md[cols.md as keyof typeof responsiveColClasses.md])
  if (cols.lg) gridClasses.push(responsiveColClasses.lg[cols.lg as keyof typeof responsiveColClasses.lg])
  if (cols.xl) gridClasses.push(responsiveColClasses.xl[cols.xl as keyof typeof responsiveColClasses.xl])
  if (cols['2xl']) gridClasses.push(responsiveColClasses['2xl'][cols['2xl'] as keyof typeof responsiveColClasses['2xl']])

  return (
    <div className={cn(gridClasses.join(' '), className)}>
      {children}
    </div>
  )
}

export function GridItem({
  children,
  colSpan,
  rowSpan,
  className
}: GridItemProps) {
  const itemClasses = []

  // Add column span classes
  if (colSpan?.default) itemClasses.push(colSpanClasses[colSpan.default as keyof typeof colSpanClasses])
  if (colSpan?.sm) itemClasses.push(responsiveColSpanClasses.sm[colSpan.sm as keyof typeof responsiveColSpanClasses.sm])
  if (colSpan?.md) itemClasses.push(responsiveColSpanClasses.md[colSpan.md as keyof typeof responsiveColSpanClasses.md])
  if (colSpan?.lg) itemClasses.push(responsiveColSpanClasses.lg[colSpan.lg as keyof typeof responsiveColSpanClasses.lg])
  if (colSpan?.xl) itemClasses.push(responsiveColSpanClasses.xl[colSpan.xl as keyof typeof responsiveColSpanClasses.xl])
  if (colSpan?.['2xl']) itemClasses.push(responsiveColSpanClasses['2xl'][colSpan['2xl'] as keyof typeof responsiveColSpanClasses['2xl']])

  // Add row span class
  if (rowSpan) itemClasses.push(`row-span-${rowSpan}`)

  return (
    <div className={cn(itemClasses.join(' '), className)}>
      {children}
    </div>
  )
}

// Pre-configured grid layouts for common use cases
export function DashboardGrid({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <ResponsiveGrid
      cols={{ default: 1, md: 2, lg: 3, xl: 4 }}
      gap="lg"
      className={className}
    >
      {children}
    </ResponsiveGrid>
  )
}

export function KPIGrid({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <ResponsiveGrid
      cols={{ default: 1, sm: 2, lg: 4 }}
      gap="md"
      className={className}
    >
      {children}
    </ResponsiveGrid>
  )
}

export function ContentGrid({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <ResponsiveGrid
      cols={{ default: 1, lg: 2 }}
      gap="lg"
      className={className}
    >
      {children}
    </ResponsiveGrid>
  )
}

export function DetailGrid({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <ResponsiveGrid
      cols={{ default: 1, md: 3 }}
      gap="md"
      className={className}
    >
      {children}
    </ResponsiveGrid>
  )
}