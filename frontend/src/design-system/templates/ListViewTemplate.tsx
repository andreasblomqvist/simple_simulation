import React from 'react'
import { cn } from '@/lib/utils'
import { Container, Stack, Grid } from '../layout'

export interface ListViewTemplateProps extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * Filters bar content - typically search, filters, and actions
   */
  filtersBar?: React.ReactNode
  
  /**
   * Main content area
   */
  content: React.ReactNode
  
  /**
   * Optional sidebar content for additional filters or info
   */
  sidebar?: React.ReactNode
  
  /**
   * Layout variant for content area
   */
  variant?: 'list' | 'cardGrid' | 'withSidebar'
  
  /**
   * Container size for the list view
   */
  containerSize?: 'fluid' | 'constrained' | 'content'
  
  /**
   * Whether to apply container padding
   */
  containerPadding?: boolean
  
  /**
   * Optional header content above the list view
   */
  header?: React.ReactNode
  
  /**
   * Optional footer content below the list view
   */
  footer?: React.ReactNode
  
  /**
   * Card grid configuration (when variant is 'cardGrid')
   */
  cardGridConfig?: {
    minItemWidth?: string
    gap?: 'none' | 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'xxl'
  }
}

/**
 * List View Layout Template
 * 
 * Provides the standard list view layout pattern:
 * - Filters Bar: Horizontal bar with search, filters, and actions
 * - Content Area: Main content with multiple layout variants
 * - Optional Sidebar: Additional filters or information panel
 * 
 * Based on layout-composition-patterns.md List View Layout specification:
 * - Filters bar with space-between layout
 * - Content area with flexible variants (list, card grid, with sidebar)
 * - Sidebar variant uses 280px fixed width + flexible content
 * - Card grid uses auto-fit with 320px minimum item width
 * 
 * @example
 * ```tsx
 * // Basic list view
 * <ListViewTemplate
 *   filtersBar={
 *     <div className="flex justify-between items-center">
 *       <SearchInput />
 *       <div className="flex gap-2">
 *         <FilterDropdown />
 *         <Button>Add Item</Button>
 *       </div>
 *     </div>
 *   }
 *   content={<DataTable data={items} />}
 * />
 * 
 * // Card grid variant
 * <ListViewTemplate
 *   variant="cardGrid"
 *   cardGridConfig={{ minItemWidth: '300px', gap: 'lg' }}
 *   content={
 *     <>
 *       <Card>Item 1</Card>
 *       <Card>Item 2</Card>
 *       <Card>Item 3</Card>
 *     </>
 *   }
 * />
 * 
 * // With sidebar variant
 * <ListViewTemplate
 *   variant="withSidebar"
 *   sidebar={<FilterPanel />}
 *   content={<ItemsList />}
 * />
 * ```
 */
export const ListViewTemplate = React.forwardRef<HTMLDivElement, ListViewTemplateProps>(
  ({ 
    filtersBar,
    content,
    sidebar,
    variant = 'list',
    containerSize = 'constrained',
    containerPadding = true,
    header,
    footer,
    cardGridConfig = { minItemWidth: '320px', gap: 'lg' },
    className,
    children,
    ...props 
  }, ref) => {
    return (
      <div ref={ref} className={cn('list-view-template', className)} {...props}>
        {/* Optional header */}
        {header && (
          <Container size={containerSize} padding={containerPadding}>
            {header}
          </Container>
        )}
        
        <Container size={containerSize} padding={containerPadding}>
          <Stack spacing="lg" className="list-view-content">
            {/* Filters Bar */}
            {filtersBar && (
              <section className="list-view-filters-bar" aria-label="Filters and actions">
                <div className={cn(
                  'flex justify-between items-center',
                  'py-4 border-b border-gray-200',
                  'mb-6'
                )}>
                  {filtersBar}
                </div>
              </section>
            )}
            
            {/* Content Area with Variants */}
            <section className="list-view-content-area" aria-label="Main content">
              {variant === 'withSidebar' ? (
                // Sidebar variant: 280px sidebar + flexible content
                <div className={cn(
                  'grid gap-8',
                  'grid-cols-1 lg:grid-cols-[280px_1fr]'
                )}>
                  {/* Sidebar */}
                  {sidebar && (
                    <aside className="list-view-sidebar">
                      {sidebar}
                    </aside>
                  )}
                  
                  {/* Main content */}
                  <main className="list-view-main">
                    <Stack spacing="md">
                      {content}
                    </Stack>
                  </main>
                </div>
              ) : variant === 'cardGrid' ? (
                // Card grid variant: Auto-fit responsive grid
                <Grid
                  columns="auto-fit"
                  minItemWidth={cardGridConfig.minItemWidth}
                  gap={cardGridConfig.gap}
                  className="card-grid"
                >
                  {content}
                </Grid>
              ) : (
                // Default list variant: Vertical stack
                <Stack spacing="md" className="list-content">
                  {content}
                </Stack>
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

ListViewTemplate.displayName = 'ListViewTemplate'

export default ListViewTemplate