import React from 'react'
import { cn } from '@/lib/utils'
import { Container, Stack, Grid } from '../layout'

export interface DashboardTemplateProps extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * KPI row content - typically stat cards
   */
  kpiRow?: React.ReactNode
  
  /**
   * Charts row content - main chart + sidebar chart
   */
  chartsRow?: {
    main: React.ReactNode
    sidebar: React.ReactNode
  }
  
  /**
   * Table row content - full-width data display
   */
  tableRow?: React.ReactNode
  
  /**
   * Container size for the dashboard
   */
  containerSize?: 'fluid' | 'constrained' | 'content'
  
  /**
   * Whether to apply container padding
   */
  containerPadding?: boolean
  
  /**
   * Optional header content above the dashboard
   */
  header?: React.ReactNode
  
  /**
   * Optional footer content below the dashboard
   */
  footer?: React.ReactNode
}

/**
 * Dashboard Layout Template
 * 
 * Provides the standard 3-row dashboard layout pattern:
 * - KPI Row: Auto-fit grid for stat cards with 250px minimum width
 * - Charts Row: 8+4 column layout (main chart + sidebar chart)
 * - Table Row: Full-width data display
 * 
 * Based on layout-composition-patterns.md Dashboard Layout specification:
 * - KPI row uses auto-fit grid with 250px minimum item width
 * - Charts row uses 2fr:1fr grid ratio (8+4 columns)
 * - Table row spans full width
 * - Responsive behavior stacks charts vertically on mobile
 * 
 * @example
 * ```tsx
 * <DashboardTemplate
 *   kpiRow={
 *     <>
 *       <KPICard title="Revenue" value="$1.2M" />
 *       <KPICard title="Users" value="15.3K" />
 *       <KPICard title="Growth" value="+12%" />
 *     </>
 *   }
 *   chartsRow={{
 *     main: <RevenueChart />,
 *     sidebar: <TopCustomersChart />
 *   }}
 *   tableRow={<DataTable data={tableData} />}
 * />
 * ```
 */
export const DashboardTemplate = React.forwardRef<HTMLDivElement, DashboardTemplateProps>(
  ({ 
    kpiRow,
    chartsRow,
    tableRow,
    containerSize = 'constrained',
    containerPadding = true,
    header,
    footer,
    className,
    children,
    ...props 
  }, ref) => {
    return (
      <div ref={ref} className={cn('dashboard-template', className)} {...props}>
        {/* Optional header */}
        {header && (
          <Container size={containerSize} padding={containerPadding}>
            {header}
          </Container>
        )}
        
        <Container size={containerSize} padding={containerPadding}>
          <Stack spacing="xxl" className="dashboard-content">
            {/* KPI Row - Auto-fit grid for stat cards */}
            {kpiRow && (
              <section className="dashboard-kpi-row" aria-labelledby="dashboard-kpis">
                <Grid
                  columns="auto-fit"
                  minItemWidth="250px"
                  gap="lg"
                  className="kpi-grid"
                >
                  {kpiRow}
                </Grid>
              </section>
            )}
            
            {/* Charts Row - 8+4 column layout (2fr + 1fr) */}
            {chartsRow && (chartsRow.main || chartsRow.sidebar) && (
              <section className="dashboard-charts-row" aria-labelledby="dashboard-charts">
                <div className={cn(
                  'grid gap-6',
                  // Desktop: 2fr 1fr (8+4 columns)
                  'grid-cols-1 lg:grid-cols-[2fr_1fr]',
                  // Mobile: stack vertically
                  'space-y-6 lg:space-y-0'
                )}>
                  {/* Main chart area */}
                  {chartsRow.main && (
                    <div className="main-chart">
                      {chartsRow.main}
                    </div>
                  )}
                  
                  {/* Sidebar chart area */}
                  {chartsRow.sidebar && (
                    <div className="sidebar-chart">
                      {chartsRow.sidebar}
                    </div>
                  )}
                </div>
              </section>
            )}
            
            {/* Table Row - Full width data display */}
            {tableRow && (
              <section className="dashboard-table-row" aria-labelledby="dashboard-data">
                <div className="table-container">
                  {tableRow}
                </div>
              </section>
            )}
            
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

DashboardTemplate.displayName = 'DashboardTemplate'

export default DashboardTemplate