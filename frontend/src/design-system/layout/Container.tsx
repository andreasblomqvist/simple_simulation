import React from 'react'
import { cn } from '@/lib/utils'
import { spacing, layout } from '../tokens'

export interface ContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * Container size variants
   * - fluid: Full width with padding, no max width
   * - constrained: Centered with max width of 1280px  
   * - content: Centered with max width of 768px for reading
   */
  size?: 'fluid' | 'constrained' | 'content'
  
  /**
   * Apply container padding
   */
  padding?: boolean
  
  /**
   * Center the container horizontally
   */
  centered?: boolean
  
  /**
   * Children elements
   */
  children: React.ReactNode
}

/**
 * Container component provides consistent page-level containers with standardized sizing and spacing.
 * 
 * Based on layout-composition-patterns.md Container specifications:
 * - fluid: Full width container with responsive padding
 * - constrained: Centered container with 1280px max width
 * - content: Content-width container with 768px max width
 * 
 * @example
 * ```tsx
 * // Full width container
 * <Container size="fluid" padding>
 *   <PageContent />
 * </Container>
 * 
 * // Centered constrained container
 * <Container size="constrained" padding>
 *   <DashboardContent />
 * </Container>
 * 
 * // Content reading width
 * <Container size="content" padding>
 *   <ArticleContent />
 * </Container>
 * ```
 */
export const Container = React.forwardRef<HTMLDivElement, ContainerProps>(
  ({ size = 'constrained', padding = true, centered = true, className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          // Base container styles
          'w-full',
          
          // Size variants
          {
            // Fluid: Full width, no max width constraint
            'max-w-none': size === 'fluid',
            
            // Constrained: Centered with 1280px max width
            'max-w-7xl': size === 'constrained',
            
            // Content: Centered with 768px max width for reading
            'max-w-3xl': size === 'content',
          },
          
          // Centering
          {
            'mx-auto': centered && size !== 'fluid',
          },
          
          // Responsive padding based on design tokens
          {
            // Mobile: 16px, Tablet: 24px, Desktop: 32px, Wide: 40px
            'px-4 sm:px-6 md:px-8 lg:px-10': padding,
          },
          
          className
        )}
        style={{
          // Custom CSS properties for more precise control if needed
          ...(size === 'constrained' && { maxWidth: '1280px' }),
          ...(size === 'content' && { maxWidth: '768px' }),
        }}
        {...props}
      >
        {children}
      </div>
    )
  }
)

Container.displayName = 'Container'

export default Container