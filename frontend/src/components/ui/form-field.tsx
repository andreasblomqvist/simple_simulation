import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../../lib/utils"

const formFieldVariants = cva(
  "space-y-2",
  {
    variants: {
      layout: {
        vertical: "flex flex-col",
        horizontal: "flex items-start gap-4",
        inline: "flex items-center gap-2"
      }
    },
    defaultVariants: {
      layout: "vertical"
    }
  }
)

const labelVariants = cva(
  "text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70",
  {
    variants: {
      layout: {
        vertical: "",
        horizontal: "min-w-0 flex-shrink-0",
        inline: "min-w-0 flex-shrink-0"
      },
      required: {
        true: "after:content-['*'] after:ml-1 after:text-destructive",
        false: ""
      }
    },
    defaultVariants: {
      layout: "vertical",
      required: false
    }
  }
)

const messageVariants = cva(
  "text-sm flex items-center gap-1",
  {
    variants: {
      type: {
        error: "text-destructive",
        success: "text-green-600",
        warning: "text-yellow-600",
        help: "text-muted-foreground"
      }
    },
    defaultVariants: {
      type: "help"
    }
  }
)

export interface FormFieldProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof formFieldVariants> {
  // Field definition
  name?: string
  label?: string
  description?: string
  required?: boolean
  
  // Validation
  error?: string
  success?: string
  helperText?: string
  
  // Layout
  labelWidth?: string
  
  children: React.ReactNode
}

export interface FormLabelProps
  extends React.LabelHTMLAttributes<HTMLLabelElement>,
    VariantProps<typeof labelVariants> {
  children: React.ReactNode
}

export interface FormMessageProps
  extends React.HTMLAttributes<HTMLParagraphElement>,
    VariantProps<typeof messageVariants> {
  children: React.ReactNode
}

export interface FormDescriptionProps
  extends React.HTMLAttributes<HTMLParagraphElement> {
  children: React.ReactNode
}

const FormField = React.forwardRef<HTMLDivElement, FormFieldProps>(
  ({ 
    className, 
    layout = "vertical",
    name,
    label, 
    description, 
    required = false,
    error, 
    success, 
    helperText,
    labelWidth,
    children, 
    ...props 
  }, ref) => {
    const fieldId = name || props.id || `field-${React.useId()}`
    
    // Clone children to add proper IDs and aria attributes
    const childrenWithProps = React.Children.map(children, (child) => {
      if (React.isValidElement(child)) {
        return React.cloneElement(child, {
          id: fieldId,
          name: name || child.props.name,
          'aria-invalid': error ? 'true' : 'false',
          'aria-describedby': [
            error && `${fieldId}-error`,
            success && `${fieldId}-success`, 
            helperText && `${fieldId}-help`,
            description && `${fieldId}-description`
          ].filter(Boolean).join(' ') || undefined,
          ...child.props
        })
      }
      return child
    })

    const LabelComponent = label ? (
      <FormLabel 
        htmlFor={fieldId}
        layout={layout}
        required={required}
        style={labelWidth ? { width: labelWidth } : undefined}
      >
        {label}
      </FormLabel>
    ) : null

    const DescriptionComponent = description ? (
      <FormDescription id={`${fieldId}-description`}>
        {description}
      </FormDescription>
    ) : null

    const ErrorComponent = error ? (
      <FormMessage id={`${fieldId}-error`} type="error">
        {error}
      </FormMessage>
    ) : null

    const SuccessComponent = success ? (
      <FormMessage id={`${fieldId}-success`} type="success">
        {success}
      </FormMessage>
    ) : null

    const HelpComponent = helperText ? (
      <FormMessage id={`${fieldId}-help`} type="help">
        {helperText}
      </FormMessage>
    ) : null

    if (layout === "horizontal") {
      return (
        <div
          ref={ref}
          className={cn(formFieldVariants({ layout }), className)}
          {...props}
        >
          <div className="flex flex-col space-y-1">
            {LabelComponent}
            {DescriptionComponent}
          </div>
          <div className="flex-1 space-y-2">
            {childrenWithProps}
            {ErrorComponent || SuccessComponent || HelpComponent}
          </div>
        </div>
      )
    }

    if (layout === "inline") {
      return (
        <div
          ref={ref}
          className={cn(formFieldVariants({ layout }), className)}
          {...props}
        >
          {LabelComponent}
          {childrenWithProps}
          {ErrorComponent || SuccessComponent || HelpComponent}
        </div>
      )
    }

    // Vertical layout (default)
    return (
      <div
        ref={ref}
        className={cn(formFieldVariants({ layout }), className)}
        {...props}
      >
        {LabelComponent}
        {DescriptionComponent}
        {childrenWithProps}
        {ErrorComponent || SuccessComponent || HelpComponent}
      </div>
    )
  }
)
FormField.displayName = "FormField"

const FormLabel = React.forwardRef<HTMLLabelElement, FormLabelProps>(
  ({ className, layout, required, children, ...props }, ref) => {
    return (
      <label
        ref={ref}
        className={cn(labelVariants({ layout, required }), className)}
        {...props}
      >
        {children}
      </label>
    )
  }
)
FormLabel.displayName = "FormLabel"

const FormMessage = React.forwardRef<HTMLParagraphElement, FormMessageProps>(
  ({ className, type, children, ...props }, ref) => {
    return (
      <p
        ref={ref}
        className={cn(messageVariants({ type }), className)}
        {...props}
      >
        {children}
      </p>
    )
  }
)
FormMessage.displayName = "FormMessage"

const FormDescription = React.forwardRef<HTMLParagraphElement, FormDescriptionProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <p
        ref={ref}
        className={cn("text-sm text-muted-foreground", className)}
        {...props}
      >
        {children}
      </p>
    )
  }
)
FormDescription.displayName = "FormDescription"

export { FormField, FormLabel, FormMessage, FormDescription }