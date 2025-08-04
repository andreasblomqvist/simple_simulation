# SimpleSim Modal System Guide

## Overview

The SimpleSim application now uses a unified modal/dialog system built on shadcn/ui components. This system eliminates modal variations and provides consistent user experiences across the application.

## Architecture

### Base Components (shadcn/ui)
- **Dialog**: Basic dialog foundation
- **AlertDialog**: Confirmation dialogs
- **Sheet**: Side panels and drawers

### Unified Modal System (`modal.tsx`)
- **Modal**: Generic modal with flexible content
- **ConfirmationDialog**: Standardized confirmation dialogs
- **FormDialog**: Form-specific modals with submit/cancel actions
- **DisplayDialog**: Read-only content display modals

### Business-Specific Components (`business-modals.tsx`)
- **ScenarioDeleteDialog**: Scenario deletion with 2-second delay
- **OfficeDeleteDialog**: Office deletion with scenario warnings
- **ImportDialog**: File import with drag-and-drop and validation
- **ExportDialog**: Export with format and option selection
- **QuickActionsSheet**: Right-side action panel

## Usage Examples

### Confirmation Dialog
```tsx
import { ConfirmationDialog } from '@/components/ui/modal'

const [deleteOpen, setDeleteOpen] = useState(false)

<ConfirmationDialog
  open={deleteOpen}
  onClose={() => setDeleteOpen(false)}
  onConfirm={handleDelete}
  title="Delete Item"
  description="This action cannot be undone."
  destructive={true}
  loading={isDeleting}
/>
```

### Form Dialog
```tsx
import { FormDialog } from '@/components/ui/modal'

<FormDialog
  open={formOpen}
  onClose={() => setFormOpen(false)}
  onSubmit={handleSubmit}
  title="Create New Scenario"
  description="Configure your workforce scenario"
  size="lg"
  loading={isSubmitting}
>
  <ScenarioForm />
</FormDialog>
```

### Business-Specific Modal
```tsx
import { ScenarioDeleteDialog } from '@/components/ui/business-modals'

<ScenarioDeleteDialog
  open={deleteOpen}
  onClose={() => setDeleteOpen(false)}
  onConfirm={handleDelete}
  scenarioName={scenario.name}
  loading={isDeleting}
/>
```

### Import Dialog
```tsx
import { ImportDialog } from '@/components/ui/business-modals'

<ImportDialog
  open={importOpen}
  onClose={() => setImportOpen(false)}
  onImport={handleFileImport}
  title="Import Business Plan"
  acceptedTypes=".xlsx,.csv"
  maxSize={10}
  loading={isImporting}
/>
```

### Quick Actions Sheet
```tsx
import { QuickActionsSheet } from '@/components/ui/business-modals'

<QuickActionsSheet
  open={actionsOpen}
  onClose={() => setActionsOpen(false)}
  title="Scenario Actions"
  actions={[
    {
      label: "Edit Scenario",
      icon: <Edit className="h-4 w-4" />,
      onClick: handleEdit
    },
    {
      label: "Export Results", 
      icon: <Download className="h-4 w-4" />,
      onClick: handleExport
    },
    {
      label: "Delete Scenario",
      icon: <Trash2 className="h-4 w-4" />,
      onClick: handleDelete,
      destructive: true
    }
  ]}
/>
```

## Design System Compliance

### Animation Standards
- **Opening**: Fade in background (200ms), scale up modal
- **Closing**: Scale down modal, fade out background (150ms)
- **Consistent easing**: All modals use same animation curves

### Size Variants
- `sm`: 384px max width
- `md`: 448px max width  
- `lg`: 512px max width (default)
- `xl`: 576px max width
- `2xl`: 672px max width
- `3xl`: 768px max width
- `4xl`: 896px max width
- `full`: Full screen

### Accessibility Features
- **Focus Management**: Auto-focus first interactive element
- **Keyboard Navigation**: Tab cycling within modal only
- **Screen Reader Support**: Proper ARIA labels and descriptions
- **Escape Key**: Closes modal (unless disabled)
- **Backdrop Click**: Closes modal (unless disabled)

### Destructive Actions
- **2-second delay**: Confirm button disabled for 2 seconds
- **Clear labeling**: Specific action descriptions
- **Warning styling**: Red/destructive color scheme
- **Consequence explanation**: Clear description of what will happen

## Migration from Legacy Modals

### Before (AlertDialog)
```tsx
import { AlertDialog, AlertDialogContent, ... } from './alert-dialog'

<AlertDialog open={open} onOpenChange={setOpen}>
  <AlertDialogContent>
    <AlertDialogHeader>
      <AlertDialogTitle>Delete Item</AlertDialogTitle>
      <AlertDialogDescription>Are you sure?</AlertDialogDescription>
    </AlertDialogHeader>
    <AlertDialogFooter>
      <AlertDialogCancel>Cancel</AlertDialogCancel>
      <AlertDialogAction onClick={handleDelete}>Delete</AlertDialogAction>
    </AlertDialogFooter>
  </AlertDialogContent>
</AlertDialog>
```

### After (Unified System)
```tsx
import { ConfirmationDialog } from './modal'

<ConfirmationDialog
  open={open}
  onClose={() => setOpen(false)}
  onConfirm={handleDelete}
  title="Delete Item"
  description="Are you sure you want to delete this item?"
  destructive={true}
/>
```

## Best Practices

### Modal Usage
1. **Use appropriate modal type**: Don't use generic Modal when business-specific component exists
2. **Provide clear titles**: Be specific about the action or content
3. **Include descriptions**: Explain consequences for destructive actions
4. **Handle loading states**: Show progress during async operations
5. **Proper sizing**: Use appropriate size variant for content

### State Management
1. **Single source of truth**: One state variable per modal
2. **Clean up on close**: Reset form data and clear errors
3. **Handle edge cases**: Check for data availability before opening
4. **Prevent double-actions**: Disable buttons during loading

### Accessibility
1. **Focus management**: Ensure proper focus flow
2. **Screen reader support**: Use semantic HTML and ARIA labels
3. **Keyboard navigation**: Support Tab, Escape, and Enter keys
4. **Color contrast**: Ensure sufficient contrast for all text

## Performance Considerations

### Lazy Loading
- Modal content rendered only when open
- Heavy components loaded on-demand
- Form validation delayed until interaction

### Bundle Size
- Tree-shakeable imports
- Shared dependencies across modal types
- Minimal runtime overhead

## Future Enhancements

### Planned Features
- **Multi-step modals**: Wizard-style flows
- **Modal stacking**: Support for modal-over-modal scenarios
- **Mobile optimization**: Full-screen on mobile devices
- **Animation customization**: Per-modal animation overrides
- **Keyboard shortcuts**: Global shortcut support

### Extension Points
- Custom modal sizes via CSS variables
- Theme-aware color schemes
- Custom validation patterns
- Integration with form libraries