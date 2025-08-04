/**
 * Page Layout Templates
 * 
 * Standardized page templates that eliminate layout inconsistencies
 * and provide a consistent foundation across the SimpleSim application.
 * 
 * Based on layout-composition-patterns.md specifications.
 */

// Dashboard Layout - KPI cards, charts, and data tables
export { 
  DashboardTemplate,
  type DashboardTemplateProps 
} from './DashboardTemplate'

// List View Layout - Filters, content area, optional sidebar
export { 
  ListViewTemplate,
  type ListViewTemplateProps 
} from './ListViewTemplate'

// Detail View Layout - Header section, main content + sidebar
export { 
  DetailViewTemplate,
  type DetailViewTemplateProps 
} from './DetailViewTemplate'

// Form Layout - Centered form content, header, field layouts
export { 
  FormTemplate,
  FieldGroup,
  type FormTemplateProps,
  type FieldGroupProps 
} from './FormTemplate'

// Editor Layout - Sticky toolbar, content area, split view variants
export { 
  EditorTemplate,
  type EditorTemplateProps 
} from './EditorTemplate'

/**
 * Template Usage Guidelines
 * 
 * 1. Choose the appropriate template based on page content:
 *    - DashboardTemplate: Metrics, charts, and data overview pages
 *    - ListViewTemplate: Data lists, search results, catalog pages
 *    - DetailViewTemplate: Item details, profile pages, single entity views
 *    - FormTemplate: Create/edit forms, settings pages, wizards
 *    - EditorTemplate: Content editing, code editing, document creation
 * 
 * 2. Use design system layout primitives (Container, Stack, Grid) within templates
 * 
 * 3. Apply consistent spacing using design tokens
 * 
 * 4. Ensure responsive behavior is tested across breakpoints
 * 
 * 5. Follow accessibility guidelines for semantic structure
 * 
 * Example import usage:
 * ```tsx
 * import { DashboardTemplate, ListViewTemplate } from '@/design-system/templates'
 * 
 * // Dashboard page
 * <DashboardTemplate
 *   kpiRow={<KPICards />}
 *   chartsRow={{ main: <MainChart />, sidebar: <SideChart /> }}
 *   tableRow={<DataTable />}
 * />
 * 
 * // List page
 * <ListViewTemplate
 *   filtersBar={<SearchAndFilters />}
 *   content={<ItemsList />}
 *   variant="cardGrid"
 * />
 * ```
 */