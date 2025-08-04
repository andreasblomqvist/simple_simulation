import React from 'react'
import { cn } from '@/lib/utils'
import { Container, Stack } from '../layout'

export interface FormTemplateProps extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * Form header content - typically title, description, and navigation
   */
  formHeader?: React.ReactNode
  
  /**
   * Main form content
   */
  children: React.ReactNode
  
  /**
   * Form footer content - typically submit buttons and actions
   */
  formFooter?: React.ReactNode
  
  /**
   * Container size for the form
   */
  containerSize?: 'fluid' | 'constrained' | 'content'
  
  /**
   * Whether to apply container padding
   */
  containerPadding?: boolean
  
  /**
   * Optional header content above the form
   */
  header?: React.ReactNode
  
  /**
   * Optional footer content below the form
   */
  footer?: React.ReactNode
  
  /**
   * Maximum width for the form content (default: 600px)
   */
  maxWidth?: string
  
  /**
   * Whether to center the form horizontally
   */
  centered?: boolean
  
  /**
   * Form element props (for proper form submission)
   */
  formProps?: React.FormHTMLAttributes<HTMLFormElement>
}

export interface FieldGroupProps extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * Field group title
   */
  title?: string
  
  /**
   * Field group description
   */
  description?: string
  
  /**
   * Layout variant for fields within the group
   */
  layout?: 'singleColumn' | 'twoColumn'
  
  /**
   * Children fields
   */
  children: React.ReactNode
}

/**
 * Field Group Component
 * 
 * Groups related form fields together with consistent spacing and optional title/description.
 */
export const FieldGroup = React.forwardRef<HTMLDivElement, FieldGroupProps>(
  ({ title, description, layout = 'singleColumn', className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'field-group',
          'p-6 border border-gray-200 rounded-lg',
          className
        )}
        {...props}
      >
        {/* Field group header */}
        {(title || description) && (
          <div className="field-group-header mb-6">
            {title && (
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {title}
              </h3>
            )}
            {description && (
              <p className="text-sm text-gray-600">
                {description}
              </p>
            )}
          </div>
        )}
        
        {/* Field group content */}
        <div className={cn(
          'field-group-content',
          {
            'space-y-6': layout === 'singleColumn',
            'grid grid-cols-1 md:grid-cols-2 gap-6': layout === 'twoColumn'
          }
        )}>
          {children}
        </div>
      </div>
    )
  }
)

FieldGroup.displayName = 'FieldGroup'

/**
 * Form Layout Template
 * 
 * Provides the standard form layout pattern:
 * - Form Header: Centered title, description, and navigation
 * - Form Content: Centered content with max width constraint (600px default)
 * - Form Footer: Action buttons and additional controls
 * 
 * Based on layout-composition-patterns.md Form Layout specification:
 * - Form header with centered text alignment
 * - Form content constrained to 600px max width and centered
 * - Support for single column and two column field layouts
 * - Field groups with borders and consistent spacing
 * 
 * @example
 * ```tsx
 * <FormTemplate
 *   formHeader={
 *     <div className="text-center">
 *       <Heading size="xl">Create Account</Heading>
 *       <Text color="secondary">Fill in your details to get started</Text>
 *     </div>
 *   }
 *   formFooter={
 *     <div className="flex justify-between">
 *       <Button variant="secondary">Cancel</Button>
 *       <Button type="submit">Create Account</Button>
 *     </div>
 *   }
 * >
 *   <FieldGroup title="Personal Information" layout="twoColumn">
 *     <Field label="First Name" required>
 *       <Input name="firstName" />
 *     </Field>
 *     <Field label="Last Name" required>
 *       <Input name="lastName" />
 *     </Field>
 *   </FieldGroup>
 *   
 *   <FieldGroup title="Account Details">
 *     <Field label="Email" required>
 *       <Input type="email" name="email" />
 *     </Field>
 *     <Field label="Password" required>
 *       <Input type="password" name="password" />
 *     </Field>
 *   </FieldGroup>
 * </FormTemplate>
 * ```
 */
export const FormTemplate = React.forwardRef<HTMLDivElement, FormTemplateProps>(
  ({ 
    formHeader,
    formFooter,
    containerSize = 'constrained',
    containerPadding = true,
    header,
    footer,
    maxWidth = '600px',
    centered = true,
    formProps,
    className,
    children,
    ...props 
  }, ref) => {
    return (
      <div ref={ref} className={cn('form-template', className)} {...props}>
        {/* Optional header */}
        {header && (
          <Container size={containerSize} padding={containerPadding}>
            {header}
          </Container>
        )}
        
        <Container size={containerSize} padding={containerPadding}>
          <div 
            className={cn(
              'form-container',
              centered && 'mx-auto',
              'px-6'
            )}
            style={{ maxWidth }}
          >
            {/* Form Header */}
            {formHeader && (
              <header className="form-header text-center py-8 border-b border-gray-200 mb-10">
                {formHeader}
              </header>
            )}
            
            {/* Form Content */}
            <form className="form-content" {...formProps}>
              <Stack spacing="xxl">
                {children}
                
                {/* Form Footer */}
                {formFooter && (
                  <footer className="form-footer pt-8 border-t border-gray-200">
                    {formFooter}
                  </footer>
                )}
              </Stack>
            </form>
          </div>
        </Container>
        
        {/* Optional footer */}
        {footer && (
          <Container size={containerSize} padding={containerPadding}>
            {footer}
          </Container>
        )}
      </div>
    )
  }
)

FormTemplate.displayName = 'FormTemplate'

export default FormTemplate