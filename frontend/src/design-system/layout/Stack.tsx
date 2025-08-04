import React from 'react'
import { cn } from '@/lib/utils'
import { spacing } from '../tokens'

export interface StackProps extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * Direction of the stack
   */
  direction?: 'vertical' | 'horizontal'
  
  /**
   * Spacing between children using design token scale
   * - none: 0px
   * - xs: 4px
   * - sm: 8px  
   * - md: 12px
   * - lg: 16px
   * - xl: 20px
   * - xxl: 24px
   */
  spacing?: 'none' | 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'xxl'
  
  /**
   * Alignment of children along the cross axis
   */
  align?: 'start' | 'center' | 'end' | 'stretch'
  
  /**
   * Justification of children along the main axis
   */
  justify?: 'start' | 'center' | 'end' | 'between' | 'around' | 'evenly'
  
  /**
   * Responsive behavior - stack vertically on mobile
   */
  responsive?: boolean
  
  /**
   * Breakpoint for responsive stacking
   */
  breakpoint?: 'sm' | 'md' | 'lg'
  
  /**
   * Children elements
   */
  children: React.ReactNode
}

/**
 * Stack component provides consistent vertical or horizontal layouts with design token spacing.
 * 
 * Based on layout-composition-patterns.md Stack specifications:
 * - Consistent spacing using design tokens
 * - Flexible alignment and justification
 * - Responsive behavior with mobile stacking
 * 
 * @example
 * ```tsx
 * // Vertical stack with large spacing
 * <Stack direction="vertical" spacing="lg" align="center">
 *   <Heading>Page Title</Heading>
 *   <Text>Description</Text>
 *   <Button>Primary Action</Button>
 * </Stack>
 * 
 * // Horizontal stack with space between
 * <Stack direction="horizontal" spacing="md" justify="between">
 *   <Logo />
 *   <Navigation />
 *   <UserMenu />
 * </Stack>
 * 
 * // Responsive stack that becomes vertical on mobile
 * <Stack direction="horizontal" spacing="lg" responsive breakpoint="md">
 *   <Card>Item 1</Card>
 *   <Card>Item 2</Card>
 * </Stack>
 * ```
 */
export const Stack = React.forwardRef<HTMLDivElement, StackProps>(
  ({ 
    direction = 'vertical', 
    spacing: stackSpacing = 'md', 
    align = 'stretch', 
    justify = 'start',
    responsive = false,
    breakpoint = 'md',
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
    
    // Map spacing to Tailwind classes for CSS-based spacing
    const spacingClasses = {
      none: 'gap-0',
      xs: 'gap-1',   // 4px
      sm: 'gap-2',   // 8px
      md: 'gap-3',   // 12px
      lg: 'gap-4',   // 16px
      xl: 'gap-5',   // 20px
      xxl: 'gap-6',  // 24px
    }
    
    // Map alignment values
    const alignMap = {
      start: 'items-start',
      center: 'items-center',
      end: 'items-end',
      stretch: 'items-stretch'
    }
    
    // Map justification values
    const justifyMap = {
      start: 'justify-start',
      center: 'justify-center',
      end: 'justify-end',
      between: 'justify-between',
      around: 'justify-around',
      evenly: 'justify-evenly'
    }
    
    // Map responsive breakpoints
    const breakpointMap = {
      sm: 'sm',
      md: 'md', 
      lg: 'lg'
    }
    
    return (
      <div
        ref={ref}
        className={cn(
          // Base flexbox
          'flex',
          
          // Direction
          {
            'flex-col': direction === 'vertical',
            'flex-row': direction === 'horizontal',
          },
          
          // Responsive direction (stack vertically on mobile)
          responsive && {
            'flex-col': true,
            [`${breakpointMap[breakpoint]}:flex-row`]: direction === 'horizontal',
          },
          
          // Spacing
          spacingClasses[stackSpacing],
          
          // Alignment
          alignMap[align],
          
          // Justification
          justifyMap[justify],
          
          className
        )}
        style={{
          // Custom CSS properties for precise spacing control if needed
          gap: spacingMap[stackSpacing],
        }}
        {...props}
      >
        {children}
      </div>
    )
  }
)

Stack.displayName = 'Stack'

export default Stack