/**
 * Universal Modal System for SimpleSim
 * 
 * Unified modal/dialog system built on shadcn/ui Dialog components.
 * Provides consistent behavior and styling across all modal patterns.
 */
"use client"

import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from "./dialog"
import { 
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger
} from "./alert-dialog"
import { Button } from "./button"
import { cn } from "../../lib/utils"

// Modal size variants
const modalVariants = cva(
  "fixed left-[50%] top-[50%] z-50 grid w-full translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] sm:rounded-lg",
  {
    variants: {
      size: {
        sm: "max-w-sm",
        md: "max-w-md", 
        lg: "max-w-lg",
        xl: "max-w-xl",
        "2xl": "max-w-2xl",
        "3xl": "max-w-3xl",
        "4xl": "max-w-4xl",
        full: "max-w-screen max-h-screen w-screen h-screen"
      }
    },
    defaultVariants: {
      size: "lg"
    }
  }
)

// Base Modal Props
interface BaseModalProps {
  open: boolean
  onClose: () => void
  title?: string
  description?: string
  children?: React.ReactNode
  size?: VariantProps<typeof modalVariants>["size"]
  className?: string
  closeOnOverlayClick?: boolean
  closeOnEscape?: boolean
}

// Generic Modal Component
interface ModalProps extends BaseModalProps {
  trigger?: React.ReactNode
  header?: React.ReactNode
  footer?: React.ReactNode
}

export const Modal: React.FC<ModalProps> = ({ 
  open, 
  onClose, 
  title, 
  description, 
  children, 
  size = "lg",
  className,
  trigger,
  header,
  footer,
  closeOnOverlayClick = true,
  closeOnEscape = true
}) => {
  return (
    <Dialog open={open} onOpenChange={(open) => !open && onClose()}>
      {trigger && <DialogTrigger asChild>{trigger}</DialogTrigger>}
      <DialogContent 
        className={cn(modalVariants({ size }), className)}
        onEscapeKeyDown={closeOnEscape ? undefined : (e) => e.preventDefault()}
        onPointerDownOutside={closeOnOverlayClick ? undefined : (e) => e.preventDefault()}
      >
        {(title || description || header) && (
          <DialogHeader>
            {title && <DialogTitle>{title}</DialogTitle>}
            {description && <DialogDescription>{description}</DialogDescription>}
            {header}
          </DialogHeader>
        )}
        
        {children}
        
        {footer && (
          <DialogFooter>
            {footer}
          </DialogFooter>
        )}
      </DialogContent>
    </Dialog>
  )
}

// Confirmation Dialog Props
interface ConfirmationDialogProps {
  open: boolean
  onClose: () => void
  onConfirm: () => void
  title: string
  description: string
  confirmLabel?: string
  cancelLabel?: string
  destructive?: boolean
  loading?: boolean
  trigger?: React.ReactNode
}

// Confirmation Dialog Component
export const ConfirmationDialog: React.FC<ConfirmationDialogProps> = ({
  open,
  onClose,
  onConfirm,
  title,
  description,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel", 
  destructive = false,
  loading = false,
  trigger
}) => {
  const [confirmEnabled, setConfirmEnabled] = React.useState(!destructive)
  
  React.useEffect(() => {
    if (destructive && open) {
      setConfirmEnabled(false)
      const timer = setTimeout(() => setConfirmEnabled(true), 2000)
      return () => clearTimeout(timer)
    }
  }, [destructive, open])

  return (
    <AlertDialog open={open} onOpenChange={(open) => !open && onClose()}>
      {trigger && <AlertDialogTrigger asChild>{trigger}</AlertDialogTrigger>}
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{title}</AlertDialogTitle>
          <AlertDialogDescription>{description}</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={loading}>{cancelLabel}</AlertDialogCancel>
          <AlertDialogAction
            onClick={onConfirm}
            disabled={loading || !confirmEnabled}
            className={destructive ? "bg-destructive text-destructive-foreground hover:bg-destructive/90" : ""}
          >
            {loading ? "Processing..." : confirmLabel}
            {destructive && !confirmEnabled && " (2s)"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}

// Form Dialog Props
interface FormDialogProps extends BaseModalProps {
  onSubmit?: () => void
  onCancel?: () => void
  submitLabel?: string
  cancelLabel?: string
  loading?: boolean
  submitDisabled?: boolean
  trigger?: React.ReactNode
}

// Form Dialog Component  
export const FormDialog: React.FC<FormDialogProps> = ({
  open,
  onClose,
  onSubmit,
  onCancel,
  title,
  description,
  children,
  size = "lg",
  className,
  submitLabel = "Save",
  cancelLabel = "Cancel",
  loading = false,
  submitDisabled = false,
  trigger
}) => {
  const handleCancel = () => {
    onCancel?.()
    onClose()
  }

  return (
    <Dialog open={open} onOpenChange={(open) => !open && onClose()}>
      {trigger && <DialogTrigger asChild>{trigger}</DialogTrigger>}
      <DialogContent className={cn(modalVariants({ size }), className)}>
        {(title || description) && (
          <DialogHeader>
            {title && <DialogTitle>{title}</DialogTitle>}
            {description && <DialogDescription>{description}</DialogDescription>}
          </DialogHeader>
        )}
        
        <div className="py-4">
          {children}
        </div>
        
        <DialogFooter>
          <Button 
            variant="outline" 
            onClick={handleCancel}
            disabled={loading}
          >
            {cancelLabel}
          </Button>
          <Button 
            onClick={onSubmit}
            disabled={loading || submitDisabled}
          >
            {loading ? "Saving..." : submitLabel}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// Display Dialog Props (read-only content)
interface DisplayDialogProps extends BaseModalProps {
  actions?: React.ReactNode
  trigger?: React.ReactNode
}

// Display Dialog Component
export const DisplayDialog: React.FC<DisplayDialogProps> = ({
  open,
  onClose,
  title,
  description,
  children,
  size = "lg",
  className,
  actions,
  trigger
}) => {
  return (
    <Dialog open={open} onOpenChange={(open) => !open && onClose()}>
      {trigger && <DialogTrigger asChild>{trigger}</DialogTrigger>}
      <DialogContent className={cn(modalVariants({ size }), className)}>
        {(title || description) && (
          <DialogHeader>
            {title && <DialogTitle>{title}</DialogTitle>}
            {description && <DialogDescription>{description}</DialogDescription>}
          </DialogHeader>
        )}
        
        <div className="py-4 max-h-[60vh] overflow-y-auto">
          {children}
        </div>
        
        {actions && (
          <DialogFooter>
            {actions}
          </DialogFooter>
        )}
      </DialogContent>
    </Dialog>
  )
}

// Export all modal components
export {
  type ModalProps,
  type ConfirmationDialogProps,
  type FormDialogProps,
  type DisplayDialogProps
}