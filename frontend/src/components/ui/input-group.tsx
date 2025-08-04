import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../../lib/utils"

const inputGroupVariants = cva(
  "flex items-center overflow-hidden rounded-md border bg-background",
  {
    variants: {
      size: {
        sm: "h-8",
        md: "h-10",
        lg: "h-12"
      },
      state: {
        default: "border-input hover:border-gray-400 focus-within:border-primary focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2",
        error: "border-error focus-within:border-error focus-within:ring-error/20",
        success: "border-success focus-within:border-success focus-within:ring-success/20",
        warning: "border-warning focus-within:border-warning focus-within:ring-warning/20"
      }
    },
    defaultVariants: {
      size: "md",
      state: "default"
    }
  }
)

const inputGroupAddonVariants = cva(
  "flex items-center justify-center text-sm text-muted-foreground bg-muted/50 border-r border-border",
  {
    variants: {
      size: {
        sm: "px-2 text-xs",
        md: "px-3 text-sm",
        lg: "px-4 text-base"
      }
    },
    defaultVariants: {
      size: "md"
    }
  }
)

export interface InputGroupProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof inputGroupVariants> {
  // Validation props
  error?: string
  success?: string
  
  children: React.ReactNode
}

export interface InputGroupAddonProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof inputGroupAddonVariants> {
  children: React.ReactNode
}

export interface InputGroupInputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  // Custom onChange that provides string value
  onValueChange?: (value: string) => void
}

const InputGroup = React.forwardRef<HTMLDivElement, InputGroupProps>(
  ({ className, size, state, error, success, children, ...props }, ref) => {
    // Determine validation state automatically if not provided
    const validationState = state || (error ? "error" : success ? "success" : "default")
    
    return (
      <div
        ref={ref}
        className={cn(inputGroupVariants({ size, state: validationState }), className)}
        {...props}
      >
        {children}
      </div>
    )
  }
)
InputGroup.displayName = "InputGroup"

const InputGroupAddon = React.forwardRef<HTMLDivElement, InputGroupAddonProps>(
  ({ className, size, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(inputGroupAddonVariants({ size }), className)}
        {...props}
      >
        {children}
      </div>
    )
  }
)
InputGroupAddon.displayName = "InputGroupAddon"

const InputGroupInput = React.forwardRef<HTMLInputElement, InputGroupInputProps>(
  ({ className, onValueChange, onChange, ...props }, ref) => {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      onChange?.(e)
      onValueChange?.(e.target.value)
    }

    return (
      <input
        ref={ref}
        className={cn(
          "flex-1 bg-transparent px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none disabled:cursor-not-allowed disabled:opacity-50",
          className
        )}
        onChange={handleChange}
        {...props}
      />
    )
  }
)
InputGroupInput.displayName = "InputGroupInput"

export { InputGroup, InputGroupAddon, InputGroupInput }