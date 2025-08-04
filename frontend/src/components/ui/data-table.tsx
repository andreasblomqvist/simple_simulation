// Clean, minimal DataTable with professional appearance
// Focused on readability with larger text, clean borders, and no visual clutter
// No sorting arrows, filtering, or column toggles - just clean data presentation

// Main export - minimal, clean table design
export { DataTableMinimal as DataTable } from "./data-table-minimal"
export type { DataTableMinimalProps as DataTableProps } from "./data-table-minimal"

// Also export minimal with explicit name for clarity
export { DataTableMinimal } from "./data-table-minimal"
export type { MinimalColumnDef } from "./data-table-minimal"

// Grouped table for hierarchical data (business planning)
export { DataTableGrouped } from "./data-table-grouped"
export type { DataTableGroupedProps, GroupedColumnDef, GroupedDataRow } from "./data-table-grouped"

// Legacy enhanced version still available when specifically needed
export { DataTableEnhanced } from "./data-table-enhanced" 
export type { DataTableProps as DataTableEnhancedProps } from "./data-table-enhanced"