import React from 'react'
import { cn } from '@/lib/utils'
import { Container, Stack } from '../layout'

export interface DetailViewTemplateProps extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * Header section content - typically title, metadata, and actions
   */
  headerSection?: React.ReactNode
  
  /**
   * Main content area
   */
  content: React.ReactNode
  
  /**
   * Sidebar content - supplementary information, actions, or related data
   */
  sidebar?: React.ReactNode
  
  /**
   * Container size for the detail view
   */
  containerSize?: 'fluid' | 'constrained' | 'content'
  
  /**
   * Whether to apply container padding
   */
  containerPadding?: boolean
  
  /**
   * Optional header content above the detail view
   */
  header?: React.ReactNode
  
  /**
   * Optional footer content below the detail view
   */
  footer?: React.ReactNode
  
  /**
   * Whether to enable responsive stacking (sidebar moves below content on tablet)
   */
  responsiveStacking?: boolean
  
  /**
   * Custom sidebar width (default: 320px)
   */
  sidebarWidth?: string
}

/**
 * Detail View Layout Template
 * 
 * Provides the standard detail view layout pattern:
 * - Header Section: Title, metadata, and actions with space-between layout
 * - Content Section: Main content (8 columns) + sidebar (4 columns)
 * - Responsive stacking: Sidebar moves below content on smaller screens
 * 
 * Based on layout-composition-patterns.md Detail View Layout specification:
 * - Header section with space-between justification and bottom border
 * - Content section uses 1fr + 320px grid (approximately 8+4 columns)
 * - Responsive behavior stacks sidebar below content on tablet and below
 * - 40px gap between main content and sidebar on desktop
 * 
 * @example
 * ```tsx
 * <DetailViewTemplate
 *   headerSection={
 *     <div className="flex justify-between items-start">
 *       <div>
 *         <Heading size="xl">Project Details</Heading>
 *         <Text color="secondary">Created 2 days ago</Text>
 *       </div>
 *       <div className="flex gap-2">
 *         <Button variant="secondary">Edit</Button>
 *         <Button variant="destructive">Delete</Button>
 *       </div>
 *     </div>
 *   }
 *   content={
 *     <Stack spacing="lg">
 *       <Section title="Overview">
 *         <ProjectOverview />
 *       </Section>
 *       <Section title="Timeline">
 *         <ProjectTimeline />
 *       </Section>
 *     </Stack>
 *   }
 *   sidebar={
 *     <Stack spacing="lg">
 *       <Card title="Team Members">
 *         <TeamMembersList />
 *       </Card>
 *       <Card title="Recent Activity">
 *         <ActivityFeed />
 *       </Card>
 *     </Stack>
 *   }
 * />
 * ```
 */
export const DetailViewTemplate = React.forwardRef<HTMLDivElement, DetailViewTemplateProps>(
  ({ 
    headerSection,
    content,
    sidebar,
    containerSize = 'constrained',
    containerPadding = true,
    header,
    footer,
    responsiveStacking = true,
    sidebarWidth = '320px',
    className,
    children,
    ...props 
  }, ref) => {
    return (
      <div ref={ref} className={cn('detail-view-template', className)} {...props}>
        {/* Optional header */}
        {header && (
          <Container size={containerSize} padding={containerPadding}>
            {header}
          </Container>
        )}
        
        <Container size={containerSize} padding={containerPadding}>
          <Stack spacing="xxl" className="detail-view-content">
            {/* Header Section */}
            {headerSection && (
              <section className="detail-view-header-section" aria-labelledby="detail-header">
                <div className={cn(
                  'flex justify-between items-start',
                  'py-6 border-b border-gray-200',
                  'mb-8'
                )}>
                  {headerSection}
                </div>
              </section>
            )}
            
            {/* Content Section with Sidebar */}
            <section className="detail-view-content-section" aria-label="Main content">
              {sidebar ? (
                <div 
                  className={cn(
                    'grid gap-10',
                    // Responsive grid: stack on tablet, side-by-side on desktop
                    responsiveStacking 
                      ? 'grid-cols-1 lg:grid-cols-[1fr_auto]'
                      : `grid-cols-[1fr_${sidebarWidth}]`
                  )}
                  style={{
                    // Custom CSS properties for precise sidebar width control
                    '--sidebar-width': sidebarWidth,
                  } as React.CSSProperties}
                >
                  {/* Main content area */}
                  <main className="detail-view-main" role="main">
                    {content}
                  </main>
                  
                  {/* Sidebar area */}
                  <aside 
                    className={cn(
                      'detail-view-sidebar',
                      // Responsive sidebar behavior
                      responsiveStacking && 'lg:w-[var(--sidebar-width)]'
                    )}
                    style={{ width: responsiveStacking ? undefined : sidebarWidth }}
                  >
                    {sidebar}
                  </aside>
                </div>
              ) : (
                // No sidebar - full width content
                <main className="detail-view-main" role="main">
                  {content}
                </main>
              )}
            </section>
            
            {/* Additional children content */}
            {children}
          </Stack>
        </Container>
        
        {/* Optional footer */}
        {footer && (
          <Container size={containerSize} padding={containerPadding}>
            {footer}
          </Container>
        )}
      </div>
    )
  }
)

DetailViewTemplate.displayName = 'DetailViewTemplate'

export default DetailViewTemplate