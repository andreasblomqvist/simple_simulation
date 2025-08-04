/**
 * Text Component - Core typography primitive
 * 
 * Provides semantic typography variants using design tokens.
 * Replaces scattered typography usage throughout the application.
 */

import * as React from 'react'
import { cn } from '../../lib/utils'
import { typography, colors } from '../tokens'

// Available semantic variants from design tokens
type TypographyVariant = 
  | 'display-xl' | 'display-lg' | 'display-md' | 'display-sm'
  | 'heading-xl' | 'heading-lg' | 'heading-md' | 'heading-sm'  
  | 'body-lg' | 'body-md' | 'body-sm'
  | 'label-lg' | 'label-md' | 'label-sm'
  | 'caption-lg' | 'caption-md' | 'caption-sm'

// Semantic HTML elements that can be rendered
type TextElement = 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'p' | 'span' | 'div' | 'label'

// Color options using design tokens
type TextColor = 
  | 'primary' | 'secondary' | 'muted' | 'accent' | 'destructive'
  | 'success' | 'warning' | 'error'
  | 'inherit'

// Weight options
type FontWeight = 'light' | 'normal' | 'medium' | 'semibold' | 'bold'

export interface TextProps {
  children: React.ReactNode
  variant?: TypographyVariant
  as?: TextElement  
  color?: TextColor
  weight?: FontWeight
  className?: string
  align?: 'left' | 'center' | 'right' | 'justify'
  truncate?: boolean
  transform?: 'uppercase' | 'lowercase' | 'capitalize' | 'none'
  
  // Accessibility
  'aria-label'?: string
  'aria-describedby'?: string
  id?: string
  
  // Event handlers
  onClick?: (event: React.MouseEvent<HTMLElement>) => void
  onMouseEnter?: (event: React.MouseEvent<HTMLElement>) => void
  onMouseLeave?: (event: React.MouseEvent<HTMLElement>) => void
}

// Variant to semantic element mapping
const defaultElementMap: Record<TypographyVariant, TextElement> = {
  'display-xl': 'h1',
  'display-lg': 'h1', 
  'display-md': 'h2',
  'display-sm': 'h3',
  'heading-xl': 'h2',
  'heading-lg': 'h3',
  'heading-md': 'h4',
  'heading-sm': 'h5',
  'body-lg': 'p',
  'body-md': 'p',
  'body-sm': 'p',
  'label-lg': 'label',
  'label-md': 'label', 
  'label-sm': 'label',
  'caption-lg': 'span',
  'caption-md': 'span',
  'caption-sm': 'span'
}

// Typography styles from design tokens
const getVariantStyles = (variant: TypographyVariant) => {
  const [category, size] = variant.split('-') as [keyof typeof typography, string]
  const categoryStyles = typography[category]
  
  if (!categoryStyles || typeof categoryStyles !== 'object') {
    console.warn(`Unknown typography category: ${category}`)
    return typography.body.md // fallback
  }
  
  const tokenStyles = (categoryStyles as any)[size]
  
  if (!tokenStyles) {
    console.warn(`Unknown typography variant: ${variant}`)
    return typography.body.md // fallback
  }
  
  return tokenStyles
}

// Color styles using design tokens
const getColorStyles = (color: TextColor) => {
  switch (color) {
    case 'primary':
      return 'text-gray-900 dark:text-gray-50'
    case 'secondary':
      return 'text-gray-600 dark:text-gray-400'
    case 'muted':
      return 'text-gray-500 dark:text-gray-500'
    case 'accent':
      return 'text-primary-600 dark:text-primary-400'
    case 'destructive':
      return 'text-red-600 dark:text-red-400'
    case 'success':
      return 'text-green-600 dark:text-green-400'
    case 'warning':
      return 'text-yellow-600 dark:text-yellow-400'
    case 'error':
      return 'text-red-600 dark:text-red-400'
    case 'inherit':
      return 'text-inherit'
    default:
      return 'text-gray-900 dark:text-gray-50'
  }
}

// Font weight styles
const getWeightStyles = (weight: FontWeight) => {
  switch (weight) {
    case 'light':
      return 'font-light'
    case 'normal':
      return 'font-normal'
    case 'medium':
      return 'font-medium'
    case 'semibold':
      return 'font-semibold'
    case 'bold':
      return 'font-bold'
    default:
      return ''
  }
}

// Transform styles
const getTransformStyles = (transform?: TextProps['transform']) => {
  switch (transform) {
    case 'uppercase':
      return 'uppercase'
    case 'lowercase':
      return 'lowercase'
    case 'capitalize':
      return 'capitalize'
    case 'none':
      return 'normal-case'
    default:
      return ''
  }
}

// Alignment styles
const getAlignStyles = (align?: TextProps['align']) => {
  switch (align) {
    case 'left':
      return 'text-left'
    case 'center':
      return 'text-center'
    case 'right':
      return 'text-right'
    case 'justify':
      return 'text-justify'
    default:
      return ''
  }
}

export const Text = React.forwardRef<HTMLElement, TextProps>(({
  children,
  variant = 'body-md',
  as,
  color = 'primary',
  weight,
  className,
  align,
  truncate = false,
  transform,
  ...props
}, ref) => {
  // Determine the element to render
  const Element = as || defaultElementMap[variant]
  
  // Get typography styles from design tokens
  const variantStyles = getVariantStyles(variant)
  
  // Build dynamic styles based on design tokens
  const dynamicStyles = {
    fontSize: variantStyles.size,
    fontWeight: weight ? (typography.fontWeight as any)[weight] : variantStyles.weight,
    lineHeight: variantStyles.lineHeight,
    letterSpacing: variantStyles.letterSpacing || 'normal',
    fontFamily: typography.fontFamily.sans.join(', ')
  }
  
  // Combine all CSS classes
  const classes = cn(
    // Base typography
    'font-sans',
    
    // Color
    getColorStyles(color),
    
    // Weight override if specified
    weight && getWeightStyles(weight),
    
    // Alignment
    getAlignStyles(align),
    
    // Transform
    getTransformStyles(transform),
    
    // Truncation
    truncate && 'truncate',
    
    // Custom classes
    className
  )

  return (
    <Element
      ref={ref as any}
      className={classes}
      style={dynamicStyles}
      {...props}
    >
      {children}
    </Element>
  )
})

Text.displayName = 'Text'

export default Text