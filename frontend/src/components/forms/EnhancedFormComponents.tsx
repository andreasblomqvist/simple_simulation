import React, { useState, useId } from 'react'
import { Controller, useFormContext, FieldPath, FieldValues } from 'react-hook-form'
import { 
  Check, 
  ChevronDown, 
  AlertCircle, 
  Eye, 
  EyeOff, 
  Calendar,
  Upload,
  X,
  Info,
  Search
} from 'lucide-react'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Label } from '../ui/label'
import { Textarea } from '../ui/textarea'
import { Checkbox } from '../ui/checkbox'
import { Badge } from '../ui/badge'
import { Card, CardContent } from '../ui/card'
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '../ui/select'
import { Calendar as CalendarComponent } from '../ui/calendar'
import { Popover, PopoverContent, PopoverTrigger } from '../ui/popover'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../ui/tooltip'
import { Progress } from '../ui/progress'
import { cn } from '../../lib/utils'
import { format } from 'date-fns'

// Base form field props
interface BaseFieldProps {
  /** Field name */
  name: string
  /** Field label */
  label?: string
  /** Field description/help text */
  description?: string
  /** Required field indicator */
  required?: boolean
  /** Disabled state */
  disabled?: boolean
  /** Custom CSS classes */
  className?: string
  /** Tooltip text */
  tooltip?: string
}

// Field wrapper component
interface FieldWrapperProps {
  label?: string
  description?: string
  required?: boolean
  error?: string
  htmlFor?: string
  children: React.ReactNode
  className?: string
  tooltip?: string
}

const FieldWrapper: React.FC<FieldWrapperProps> = ({
  label,
  description,
  required,
  error,
  htmlFor,
  children,
  className,
  tooltip
}) => {
  return (
    <div className={cn("space-y-2", className)}>
      {label && (
        <div className="flex items-center gap-2">
          <Label htmlFor={htmlFor} className={cn("text-sm font-medium", required && "after:content-['*'] after:ml-0.5 after:text-red-500")}>
            {label}
          </Label>
          {tooltip && (
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger>
                  <Info className="h-4 w-4 text-muted-foreground" />
                </TooltipTrigger>
                <TooltipContent>
                  <p className="max-w-xs">{tooltip}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          )}
        </div>
      )}
      
      {children}
      
      {description && !error && (
        <p className="text-xs text-muted-foreground">{description}</p>
      )}
      
      {error && (
        <div className="flex items-center gap-2 text-sm text-red-600 dark:text-red-400">
          <AlertCircle className="h-4 w-4" />
          <span>{error}</span>
        </div>
      )}
    </div>
  )
}

// Enhanced Text Input
interface TextFieldProps extends BaseFieldProps {
  type?: 'text' | 'email' | 'password' | 'number'
  placeholder?: string
  /** Show character count */
  showCount?: boolean
  /** Maximum characters */
  maxLength?: number
  /** Input prefix */
  prefix?: React.ReactNode
  /** Input suffix */
  suffix?: React.ReactNode
  /** Auto-complete */
  autoComplete?: string
}

export function TextField({
  name,
  label,
  description,
  required,
  disabled,
  className,
  tooltip,
  type = 'text',
  placeholder,
  showCount,
  maxLength,
  prefix,
  suffix,
  autoComplete
}: TextFieldProps) {
  const { control, formState: { errors } } = useFormContext()
  const [showPassword, setShowPassword] = useState(false)
  const fieldId = useId()
  const error = errors[name]?.message as string

  return (
    <Controller
      name={name}
      control={control}
      render={({ field }) => {
        const inputType = type === 'password' ? (showPassword ? 'text' : 'password') : type
        const value = field.value || ''
        
        return (
          <FieldWrapper
            label={label}
            description={description}
            required={required}
            error={error}
            htmlFor={fieldId}
            className={className}
            tooltip={tooltip}
          >
            <div className="relative">
              {prefix && (
                <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground">
                  {prefix}
                </div>
              )}
              
              <Input
                {...field}
                id={fieldId}
                type={inputType}
                placeholder={placeholder}
                disabled={disabled}
                maxLength={maxLength}
                autoComplete={autoComplete}
                className={cn(
                  prefix && "pl-10",
                  suffix && "pr-10",
                  (showCount || type === 'password') && "pr-16",
                  error && "border-red-500 focus-visible:ring-red-500"
                )}
              />
              
              {type === 'password' && (
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 h-6 w-6 p-0"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </Button>
              )}
              
              {suffix && !showCount && type !== 'password' && (
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground">
                  {suffix}
                </div>
              )}
            </div>
            
            {showCount && maxLength && (
              <div className="flex justify-end">
                <span className={cn(
                  "text-xs",
                  value.length > maxLength * 0.9 ? "text-amber-600" : "text-muted-foreground",
                  value.length >= maxLength && "text-red-600"
                )}>
                  {value.length}/{maxLength}
                </span>
              </div>
            )}
          </FieldWrapper>
        )
      }}
    />
  )
}

// Enhanced Textarea
interface TextareaFieldProps extends BaseFieldProps {
  placeholder?: string
  rows?: number
  showCount?: boolean
  maxLength?: number
  /** Auto-resize */
  autoResize?: boolean
}

export function TextareaField({
  name,
  label,
  description,
  required,
  disabled,
  className,
  tooltip,
  placeholder,
  rows = 3,
  showCount,
  maxLength,
  autoResize
}: TextareaFieldProps) {
  const { control, formState: { errors } } = useFormContext()
  const fieldId = useId()
  const error = errors[name]?.message as string

  return (
    <Controller
      name={name}
      control={control}
      render={({ field }) => {
        const value = field.value || ''
        
        return (
          <FieldWrapper
            label={label}
            description={description}
            required={required}
            error={error}
            htmlFor={fieldId}
            className={className}
            tooltip={tooltip}
          >
            <Textarea
              {...field}
              id={fieldId}
              placeholder={placeholder}
              disabled={disabled}
              rows={rows}
              maxLength={maxLength}
              className={cn(
                error && "border-red-500 focus-visible:ring-red-500",
                autoResize && "resize-none"
              )}
            />
            
            {showCount && maxLength && (
              <div className="flex justify-end">
                <span className={cn(
                  "text-xs",
                  value.length > maxLength * 0.9 ? "text-amber-600" : "text-muted-foreground",
                  value.length >= maxLength && "text-red-600"
                )}>
                  {value.length}/{maxLength}
                </span>
              </div>
            )}
          </FieldWrapper>
        )
      }}
    />
  )
}

// Enhanced Select Field
interface SelectOption {
  value: string
  label: string
  disabled?: boolean
}

interface SelectFieldProps extends BaseFieldProps {
  options: SelectOption[]
  placeholder?: string
  /** Allow clearing selection */
  clearable?: boolean
  /** Custom option renderer */
  renderOption?: (option: SelectOption) => React.ReactNode
}

export function SelectField({
  name,
  label,
  description,
  required,
  disabled,
  className,
  tooltip,
  options,
  placeholder,
  clearable
}: SelectFieldProps) {
  const { control, formState: { errors } } = useFormContext()
  const fieldId = useId()
  const error = errors[name]?.message as string

  return (
    <Controller
      name={name}
      control={control}
      render={({ field }) => (
        <FieldWrapper
          label={label}
          description={description}
          required={required}
          error={error}
          htmlFor={fieldId}
          className={className}
          tooltip={tooltip}
        >
          <Select
            value={field.value}
            onValueChange={field.onChange}
            disabled={disabled}
          >
            <SelectTrigger className={cn(error && "border-red-500")}>
              <SelectValue placeholder={placeholder} />
            </SelectTrigger>
            <SelectContent>
              {clearable && field.value && (
                <SelectItem value="" className="text-muted-foreground">
                  Clear selection
                </SelectItem>
              )}
              {options.map((option) => (
                <SelectItem 
                  key={option.value} 
                  value={option.value}
                  disabled={option.disabled}
                >
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </FieldWrapper>
      )}
    />
  )
}

// Enhanced Multi-Select Field
interface MultiSelectFieldProps extends BaseFieldProps {
  options: SelectOption[]
  placeholder?: string
  /** Maximum selections */
  maxSelections?: number
}

export function MultiSelectField({
  name,
  label,
  description,
  required,
  disabled,
  className,
  tooltip,
  options,
  placeholder,
  maxSelections
}: MultiSelectFieldProps) {
  const { control, formState: { errors }, setValue, watch } = useFormContext()
  const fieldId = useId()
  const error = errors[name]?.message as string
  const selectedValues = watch(name) || []

  const handleToggle = (value: string) => {
    const currentValues = selectedValues || []
    let newValues
    
    if (currentValues.includes(value)) {
      newValues = currentValues.filter((v: string) => v !== value)
    } else {
      if (maxSelections && currentValues.length >= maxSelections) {
        return // Don't allow more selections
      }
      newValues = [...currentValues, value]
    }
    
    setValue(name, newValues)
  }

  const removeValue = (valueToRemove: string) => {
    const newValues = selectedValues.filter((v: string) => v !== valueToRemove)
    setValue(name, newValues)
  }

  return (
    <FieldWrapper
      label={label}
      description={description}
      required={required}
      error={error}
      htmlFor={fieldId}
      className={className}
      tooltip={tooltip}
    >
      <div className="space-y-2">
        {/* Selected values */}
        {selectedValues.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {selectedValues.map((value: string) => {
              const option = options.find(opt => opt.value === value)
              return (
                <Badge key={value} variant="secondary" className="text-xs">
                  {option?.label || value}
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="h-4 w-4 p-0 ml-1 hover:bg-destructive hover:text-destructive-foreground"
                    onClick={() => removeValue(value)}
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </Badge>
              )
            })}
          </div>
        )}
        
        {/* Options */}
        <div className="grid gap-2">
          {options.map((option) => {
            const isSelected = selectedValues.includes(option.value)
            const isDisabled = disabled || option.disabled || 
              (maxSelections && selectedValues.length >= maxSelections && !isSelected)
            
            return (
              <div key={option.value} className="flex items-center space-x-2">
                <Checkbox
                  id={`${fieldId}-${option.value}`}
                  checked={isSelected}
                  onCheckedChange={() => handleToggle(option.value)}
                  disabled={isDisabled}
                />
                <Label
                  htmlFor={`${fieldId}-${option.value}`}
                  className={cn(
                    "text-sm font-normal cursor-pointer",
                    isDisabled && "cursor-not-allowed opacity-50"
                  )}
                >
                  {option.label}
                </Label>
              </div>
            )
          })}
        </div>
        
        {maxSelections && (
          <p className="text-xs text-muted-foreground">
            {selectedValues.length}/{maxSelections} selected
          </p>
        )}
      </div>
    </FieldWrapper>
  )
}

// Enhanced Date Field
interface DateFieldProps extends BaseFieldProps {
  placeholder?: string
  /** Disable dates before this date */
  disableBefore?: Date
  /** Disable dates after this date */
  disableAfter?: Date
}

export function DateField({
  name,
  label,
  description,
  required,
  disabled,
  className,
  tooltip,
  placeholder = "Select date",
  disableBefore,
  disableAfter
}: DateFieldProps) {
  const { control, formState: { errors } } = useFormContext()
  const fieldId = useId()
  const error = errors[name]?.message as string

  return (
    <Controller
      name={name}
      control={control}
      render={({ field }) => (
        <FieldWrapper
          label={label}
          description={description}
          required={required}
          error={error}
          htmlFor={fieldId}
          className={className}
          tooltip={tooltip}
        >
          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                className={cn(
                  "w-full justify-start text-left font-normal",
                  !field.value && "text-muted-foreground",
                  error && "border-red-500"
                )}
                disabled={disabled}
              >
                <Calendar className="mr-2 h-4 w-4" />
                {field.value ? format(field.value, "PPP") : placeholder}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <CalendarComponent
                mode="single"
                selected={field.value}
                onSelect={field.onChange}
                disabled={(date) => {
                  if (disableBefore && date < disableBefore) return true
                  if (disableAfter && date > disableAfter) return true
                  return false
                }}
                initialFocus
              />
            </PopoverContent>
          </Popover>
        </FieldWrapper>
      )}
    />
  )
}

// Form Section Component
interface FormSectionProps {
  title?: string
  description?: string
  children: React.ReactNode
  className?: string
  /** Collapsible section */
  collapsible?: boolean
  /** Default collapsed state */
  defaultCollapsed?: boolean
}

export function FormSection({
  title,
  description,
  children,
  className,
  collapsible = false,
  defaultCollapsed = false
}: FormSectionProps) {
  const [collapsed, setCollapsed] = useState(defaultCollapsed)

  return (
    <Card className={cn("form-section", className)}>
      {(title || description) && (
        <div 
          className={cn(
            "flex items-center justify-between p-4 border-b",
            collapsible && "cursor-pointer"
          )}
          onClick={collapsible ? () => setCollapsed(!collapsed) : undefined}
        >
          <div>
            {title && <h3 className="text-lg font-medium">{title}</h3>}
            {description && <p className="text-sm text-muted-foreground mt-1">{description}</p>}
          </div>
          {collapsible && (
            <ChevronDown className={cn(
              "h-4 w-4 transition-transform",
              collapsed && "transform rotate-180"
            )} />
          )}
        </div>
      )}
      
      {(!collapsible || !collapsed) && (
        <CardContent className="p-4">
          <div className="space-y-4">
            {children}
          </div>
        </CardContent>
      )}
    </Card>
  )
}

// Form Progress Component
interface FormProgressProps {
  steps: string[]
  currentStep: number
  className?: string
}

export function FormProgress({ steps, currentStep, className }: FormProgressProps) {
  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>Step {currentStep + 1} of {steps.length}</span>
        <span>{Math.round(((currentStep + 1) / steps.length) * 100)}%</span>
      </div>
      <Progress value={((currentStep + 1) / steps.length) * 100} />
      <div className="flex justify-between text-sm">
        {steps.map((step, index) => (
          <span
            key={step}
            className={cn(
              index <= currentStep ? "text-foreground font-medium" : "text-muted-foreground"
            )}
          >
            {step}
          </span>
        ))}
      </div>
    </div>
  )
}