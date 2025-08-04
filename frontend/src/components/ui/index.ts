export { Button, buttonVariants } from './button'
export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent } from './card'
export { ThemeToggle } from './theme-toggle'
// Enhanced Input System
export { Input, inputVariants, type InputProps } from './input'
export { InputGroup, InputGroupAddon, InputGroupInput, type InputGroupProps, type InputGroupAddonProps, type InputGroupInputProps } from './input-group'
export { PasswordInput, type PasswordInputProps } from './password-input'
export { SearchInput, type SearchInputProps } from './search-input'
export { FormField, FormLabel, FormMessage, FormDescription, type FormFieldProps, type FormLabelProps, type FormMessageProps, type FormDescriptionProps } from './form-field'
export { Checkbox } from './checkbox'
export { Badge } from './badge'
export { 
  Table, 
  TableHeader, 
  TableBody, 
  TableFooter, 
  TableHead, 
  TableRow, 
  TableCell, 
  TableCaption 
} from './table'
export {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuCheckboxItem,
  DropdownMenuRadioItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuGroup,
  DropdownMenuPortal,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuRadioGroup,
} from './dropdown-menu'
// Enhanced DataTable System with modular architecture
export { 
  DataTable, 
  DataTableColumnHeader, 
  DataTableToolbar, 
  DataTablePagination,
  type DataTableProps 
} from './data-table'

// Enhanced table system
export { 
  EnhancedDataTable, 
  FinancialCell, 
  DeltaCell, 
  EditableCell, 
  SortableHeader,
  type EnhancedColumnDef,
  type EnhancedDataTableProps 
} from './enhanced-data-table'
export { 
  FinancialDataTable, 
  formatKPIValue, 
  buildFinancialTableData,
  type FinancialKPI,
  type FinancialRow 
} from './financial-data-table'
export { 
  PlanningDataTable, 
  buildPlanningTableData,
  type PlanningEntry,
  type PlanningRow 
} from './planning-data-table'
export { 
  ScenarioComparisonTable, 
  buildScenarioComparisonData,
  type ScenarioKPI,
  type ScenarioData,
  type ComparisonRow 
} from './scenario-comparison-table'
export {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from './dialog'
export {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from './alert-dialog'
export {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
  SheetClose,
} from './sheet'

// Unified Modal System
export {
  Modal,
  ConfirmationDialog,
  FormDialog,
  DisplayDialog,
  type ModalProps,
  type ConfirmationDialogProps,
  type FormDialogProps,
  type DisplayDialogProps,
} from './modal'

// Business-Specific Modals
export {
  ScenarioDeleteDialog,
  OfficeDeleteDialog,
  ImportDialog,
  ExportDialog,
  QuickActionsSheet,
  type ScenarioDeleteDialogProps,
  type OfficeDeleteDialogProps,
  type ImportDialogProps,
  type ExportDialogProps,
  type QuickActionsSheetProps,
} from './business-modals'
export { useToast } from './use-toast'

// Enhanced Components (Modern shadcn/ui versions)
// TODO: Implement these components when needed
// export { EnhancedKPICard as ModernKPICard } from './enhanced-kpi-card'
// export { EnhancedDataTable as ModernDataTable } from './enhanced-data-table'
// export { EnhancedKPICard } from './enhanced-kpi-card' // Keep for backward compatibility
// export { EnhancedDataTable } from './enhanced-data-table' // Keep for backward compatibility

// Loading States
export {
  LoadingSpinner,
  Skeleton,
  CardSkeleton,
  TableSkeleton,
  KPICardSkeleton,
  ChartSkeleton,
  ProgressiveLoading,
  PageTransition,
  StaggerContainer,
  LoadingOverlay
} from './loading-states'

// Accessibility
export {
  ScreenReaderOnly,
  FocusTrap,
  SkipLink,
  LiveRegion,
  useHighContrast,
  useReducedMotion,
  AccessibleBadge,
  KeyboardNavigation,
  AccessibleProgress
} from './accessibility'