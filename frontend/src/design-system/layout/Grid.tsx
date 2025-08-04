import React from 'react'
import { cn } from '@/lib/utils'
import { spacing } from '../tokens'

export interface GridProps extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * Number of columns or auto-sizing mode
   * - number: Fixed number of columns
   * - 'auto-fit': Fit as many columns as possible
   * - 'auto-fill': Fill available space with columns
   * - string: Custom grid-template-columns value
   */
  columns?: number | 'auto-fit' | 'auto-fill' | string
  
  /**
   * Number of rows or auto-sizing mode
   * - number: Fixed number of rows
   * - 'auto': Automatic row sizing
   * - string: Custom grid-template-rows value
   */
  rows?: number | 'auto' | string
  
  /**
   * Gap between grid items using design token scale
   */
  gap?: 'none' | 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'xxl'
  
  /**
   * Column gap (overrides gap for columns)
   */
  columnGap?: 'none' | 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'xxl'
  
  /**
   * Row gap (overrides gap for rows)
   */
  rowGap?: 'none' | 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'xxl'
  
  /**
   * Minimum width for auto-fit/auto-fill columns
   */
  minItemWidth?: string
  
  /**
   * Responsive grid configuration using Tailwind breakpoints
   */
  responsive?: {
    sm?: Partial<Pick<GridProps, 'columns' | 'gap' | 'minItemWidth'>>
    md?: Partial<Pick<GridProps, 'columns' | 'gap' | 'minItemWidth'>>
    lg?: Partial<Pick<GridProps, 'columns' | 'gap' | 'minItemWidth'>>
  }
  
  /**
   * Children elements
   */
  children: React.ReactNode
}

/**
 * Grid component provides CSS Grid layouts with responsive columns and design token spacing.
 * 
 * Based on layout-composition-patterns.md Grid specifications:
 * - Flexible column and row configuration
 * - Auto-fit and auto-fill responsive behavior
 * - Consistent spacing using design tokens
 * - Mobile-first responsive design
 * 
 * @example
 * ```tsx
 * // Fixed 3-column grid
 * <Grid columns={3} gap="lg">
 *   <Card>Item 1</Card>
 *   <Card>Item 2</Card>
 *   <Card>Item 3</Card>
 * </Grid>
 * 
 * // Auto-fit responsive grid
 * <Grid columns="auto-fit" minItemWidth="300px" gap="md">
 *   <StatsCard />
 *   <StatsCard />
 *   <StatsCard />
 * </Grid>
 * 
 * // Responsive grid with Tailwind classes
 * <Grid columns={1} gap="lg" className="md:grid-cols-2 lg:grid-cols-3">
 *   <Card>Item 1</Card>
 *   <Card>Item 2</Card>
 *   <Card>Item 3</Card>
 * </Grid>
 * ```
 */
export const Grid = React.forwardRef<HTMLDivElement, GridProps>(
  ({ 
    columns = 'auto-fit', 
    rows = 'auto',
    gap: gridGap = 'md',
    columnGap,
    rowGap,
    minItemWidth = '300px',
    responsive,
    className, 
    children, 
    ...props 
  }, ref) => {
    // Map spacing values to design tokens
    const spacingMap = {
      none: '0',
      xs: spacing[1],   // 4px
      sm: spacing[2],   // 8px
      md: spacing[3],   // 12px
      lg: spacing[4],   // 16px
      xl: spacing[5],   // 20px
      xxl: spacing[6],  // 24px
    }
    
    // Map spacing to Tailwind gap classes
    const gapClasses = {
      none: 'gap-0',
      xs: 'gap-1',   // 4px
      sm: 'gap-2',   // 8px
      md: 'gap-3',   // 12px
      lg: 'gap-4',   // 16px
      xl: 'gap-5',   // 20px
      xxl: 'gap-6',  // 24px
    }
    
    // Generate grid-template-columns value
    const getColumnsValue = (cols: GridProps['columns'], minWidth?: string) => {
      if (typeof cols === 'number') {
        return `repeat(${cols}, 1fr)`
      }
      if (cols === 'auto-fit') {
        return `repeat(auto-fit, minmax(${minWidth || minItemWidth}, 1fr))`
      }
      if (cols === 'auto-fill') {
        return `repeat(auto-fill, minmax(${minWidth || minItemWidth}, 1fr))`
      }
      return cols || `repeat(auto-fit, minmax(${minItemWidth}, 1fr))`
    }
    
    // Generate grid-template-rows value
    const getRowsValue = (gridRows: GridProps['rows']) => {
      if (typeof gridRows === 'number') {
        return `repeat(${gridRows}, 1fr)`
      }
      if (gridRows === 'auto') {
        return 'auto'
      }
      return gridRows || 'auto'
    }
    
    // Build inline styles for precise control
    const gridStyles: React.CSSProperties = {
      display: 'grid',
      gridTemplateColumns: getColumnsValue(columns, minItemWidth),
      gridTemplateRows: getRowsValue(rows),
      gap: columnGap || rowGap ? undefined : spacingMap[gridGap],
      columnGap: columnGap ? spacingMap[columnGap] : undefined,
      rowGap: rowGap ? spacingMap[rowGap] : undefined,
    }
    
    return (
      <div
        ref={ref}
        className={cn(
          // Base grid class
          'grid',
          
          // Gap classes (Tailwind for consistency, overridden by inline styles if needed)
          !columnGap && !rowGap && gapClasses[gridGap],
          
          className
        )}
        style={gridStyles}
        {...props}
      >
        {children}
      </div>
    )
  }
)

Grid.displayName = 'Grid'

export default Grid