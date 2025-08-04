import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { Loader2 } from "lucide-react"

import { cn } from "../../lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground shadow hover:bg-primary/90",
        destructive:
          "bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90",
        outline:
          "border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground",
        secondary:
          "bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-9 px-4 py-2",
        sm: "h-8 rounded-md px-3 text-xs",
        lg: "h-10 rounded-md px-8",
        icon: "h-9 w-9",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
  loading?: boolean
  icon?: React.ReactNode
  iconPosition?: 'left' | 'right'
  fullWidth?: boolean
  rounded?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    className, 
    variant, 
    size, 
    asChild = false, 
    loading = false,
    icon,
    iconPosition = 'left',
    fullWidth = false,
    rounded = false,
    disabled,
    children,
    ...props 
  }, ref) => {
    const Comp = asChild ? Slot : "button"
    
    // Determine if button should be disabled (loading or explicitly disabled)
    const isDisabled = disabled || loading
    
    // Handle loading spinner
    const loadingSpinner = loading && (
      <Loader2 className="h-4 w-4 animate-spin" />
    )
    
    // Handle icon rendering
    const leftIcon = icon && iconPosition === 'left' && !loading ? icon : null
    const rightIcon = icon && iconPosition === 'right' && !loading ? icon : null
    
    // When asChild is true, we need to wrap everything in a single element
    // to satisfy the Slot component's requirement for exactly one child
    const buttonContent = (
      <>
        {loading && loadingSpinner}
        {leftIcon}
        {loading ? (
          <span className="opacity-0">{children}</span>
        ) : (
          children
        )}
        {rightIcon}
      </>
    )

    return (
      <Comp
        className={cn(
          buttonVariants({ variant, size }),
          fullWidth && "w-full",
          rounded && "rounded-full",
          loading && "cursor-wait",
          className
        )}
        ref={ref}
        disabled={isDisabled}
        aria-disabled={isDisabled}
        {...props}
      >
        {asChild ? (
          <div className="inline-flex items-center justify-center">
            {buttonContent}
          </div>
        ) : (
          buttonContent
        )}
      </Comp>
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }