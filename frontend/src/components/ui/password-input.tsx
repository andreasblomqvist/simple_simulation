import * as React from "react"
import { Eye, EyeOff } from "lucide-react"
import { Input, type InputProps } from "./input"
import { cn } from "../../lib/utils"

export interface PasswordInputProps extends Omit<InputProps, 'type' | 'rightIcon'> {
  // Show/hide password toggle
  showToggle?: boolean
  
  // Custom toggle icon
  showIcon?: React.ReactNode
  hideIcon?: React.ReactNode
  
  // Accessibility labels
  showLabel?: string
  hideLabel?: string
}

const PasswordInput = React.forwardRef<HTMLInputElement, PasswordInputProps>(
  ({ 
    showToggle = true,
    showIcon,
    hideIcon,
    showLabel = "Show password",
    hideLabel = "Hide password",
    className,
    ...props 
  }, ref) => {
    const [showPassword, setShowPassword] = React.useState(false)
    
    const togglePassword = () => {
      setShowPassword(!showPassword)
    }
    
    const ToggleButton = ({ onClick, 'aria-label': ariaLabel, children }: {
      onClick: () => void
      'aria-label': string
      children: React.ReactNode
    }) => (
      <button
        type="button"
        onClick={onClick}
        aria-label={ariaLabel}
        className={cn(
          "flex items-center justify-center transition-colors",
          "hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1 rounded-sm",
          "disabled:pointer-events-none disabled:opacity-50"
        )}
        tabIndex={0}
      >
        {children}
      </button>
    )
    
    if (!showToggle) {
      return (
        <Input
          {...props}
          ref={ref}
          type="password"
          className={className}
        />
      )
    }
    
    return (
      <Input
        {...props}
        ref={ref}
        type={showPassword ? "text" : "password"}
        className={className}
        rightIcon={
          <ToggleButton
            onClick={togglePassword}
            aria-label={showPassword ? hideLabel : showLabel}
          >
            {showPassword ? (
              hideIcon || <EyeOff className="h-4 w-4" />
            ) : (
              showIcon || <Eye className="h-4 w-4" />
            )}
          </ToggleButton>
        }
      />
    )
  }
)
PasswordInput.displayName = "PasswordInput"

export { PasswordInput }