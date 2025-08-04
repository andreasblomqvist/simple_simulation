import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../../lib/utils"

// Input variants using CVA for consistent styling
const inputVariants = cva(
  // Base styles
  "flex w-full rounded-md border bg-background text-sm ring-offset-background transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
  {
    variants: {
      // Size variants matching button sizes
      size: {
        sm: "h-8 px-2 py-1 text-xs",
        md: "h-10 px-3 py-2 text-sm", // Default
        lg: "h-12 px-4 py-3 text-base"
      },
      // Validation state variants
      state: {
        default: "border-input hover:border-gray-400 focus-visible:border-primary",
        error: "border-error bg-error/5 focus-visible:border-error focus-visible:ring-error/20 text-error-foreground",
        success: "border-success bg-success/5 focus-visible:border-success focus-visible:ring-success/20",
        warning: "border-warning bg-warning/5 focus-visible:border-warning focus-visible:ring-warning/20"
      },
      // Visual variants
      variant: {
        default: "border-input",
        filled: "bg-muted border-muted",
        borderless: "border-transparent bg-muted hover:bg-muted/80"
      }
    },
    defaultVariants: {
      size: "md",
      state: "default",
      variant: "default"
    }
  }
)

export interface InputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'>,
    VariantProps<typeof inputVariants> {
  // Validation props
  error?: string
  success?: string
  helperText?: string
  
  // Icon support
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
  
  // Loading state
  loading?: boolean
  
  // Custom onChange that provides string value
  onValueChange?: (value: string) => void
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ 
    className, 
    type = "text", 
    size, 
    state, 
    variant,
    error, 
    success, 
    helperText,
    leftIcon, 
    rightIcon, 
    loading,
    onValueChange,
    onChange,
    ...props 
  }, ref) => {
    
    // Determine validation state automatically if not provided
    const validationState = state || (error ? "error" : success ? "success" : "default")
    
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      onChange?.(e)
      onValueChange?.(e.target.value)
    }

    // Input wrapper for icons
    if (leftIcon || rightIcon || loading) {
      return (
        <div className="relative">
          {leftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
              {leftIcon}
            </div>
          )}
          
          <input
            type={type}
            className={cn(
              inputVariants({ size, state: validationState, variant }),
              leftIcon && "pl-10",
              (rightIcon || loading) && "pr-10",
              className
            )}
            ref={ref}
            onChange={handleChange}
            aria-invalid={error ? "true" : "false"}
            aria-describedby={
              error ? `${props.id}-error` : 
              success ? `${props.id}-success` : 
              helperText ? `${props.id}-help` : undefined
            }
            {...props}
          />
          
          {(rightIcon || loading) && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">
              {loading ? (
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-muted-foreground border-t-transparent" />
              ) : (
                rightIcon
              )}
            </div>
          )}
        </div>
      )
    }

    // Simple input without icons
    return (
      <input
        type={type}
        className={cn(
          inputVariants({ size, state: validationState, variant }),
          className
        )}
        ref={ref}
        onChange={handleChange}
        aria-invalid={error ? "true" : "false"}
        aria-describedby={
          error ? `${props.id}-error` : 
          success ? `${props.id}-success` : 
          helperText ? `${props.id}-help` : undefined
        }
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

export { Input, inputVariants }