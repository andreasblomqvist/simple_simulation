/**
 * Heading Component - Specialized typography for headings
 * 
 * Wrapper around Text component optimized for heading use cases.
 * Provides semantic HTML structure and proper heading hierarchy.
 */

import * as React from 'react'
import { Text, TextProps } from './Text'

// Heading-specific variants
type HeadingVariant = 
  | 'display-xl' | 'display-lg' | 'display-md' | 'display-sm'
  | 'heading-xl' | 'heading-lg' | 'heading-md' | 'heading-sm'

// Heading-specific elements
type HeadingElement = 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6'

// Level-based heading mapping for semantic structure
type HeadingLevel = 1 | 2 | 3 | 4 | 5 | 6

export interface HeadingProps extends Omit<TextProps, 'variant' | 'as'> {
  variant?: HeadingVariant
  level?: HeadingLevel
  as?: HeadingElement
}

// Map heading levels to default variants (can be overridden)
const levelToVariantMap: Record<HeadingLevel, HeadingVariant> = {
  1: 'display-lg',
  2: 'display-md', 
  3: 'heading-xl',
  4: 'heading-lg',
  5: 'heading-md',
  6: 'heading-sm'
}

// Map levels to semantic elements
const levelToElementMap: Record<HeadingLevel, HeadingElement> = {
  1: 'h1',
  2: 'h2',
  3: 'h3', 
  4: 'h4',
  5: 'h5',
  6: 'h6'
}

export const Heading = React.forwardRef<HTMLElement, HeadingProps>(({
  variant,
  level,
  as,
  children,
  ...rest
}, ref) => {
  // Determine variant: explicit > level-based > default
  const resolvedVariant = variant || (level ? levelToVariantMap[level] : 'heading-lg')
  
  // Determine element: explicit > level-based > default based on variant
  let resolvedElement: HeadingElement
  if (as) {
    resolvedElement = as
  } else if (level) {
    resolvedElement = levelToElementMap[level]
  } else {
    // Default element based on variant
    if (resolvedVariant.startsWith('display-')) {
      resolvedElement = resolvedVariant === 'display-xl' ? 'h1' : 'h2'
    } else {
      resolvedElement = 'h3' // Default for heading variants
    }
  }

  return (
    <Text
      ref={ref}
      variant={resolvedVariant}
      as={resolvedElement}
      {...rest}
    >
      {children}
    </Text>
  )
})

Heading.displayName = 'Heading'

// Convenience components for specific heading levels
export const H1 = React.forwardRef<HTMLElement, Omit<HeadingProps, 'level' | 'as'>>((props, ref) => (
  <Heading ref={ref} level={1} {...props} />
))
H1.displayName = 'H1'

export const H2 = React.forwardRef<HTMLElement, Omit<HeadingProps, 'level' | 'as'>>((props, ref) => (
  <Heading ref={ref} level={2} {...props} />
))
H2.displayName = 'H2'

export const H3 = React.forwardRef<HTMLElement, Omit<HeadingProps, 'level' | 'as'>>((props, ref) => (
  <Heading ref={ref} level={3} {...props} />
))
H3.displayName = 'H3'

export const H4 = React.forwardRef<HTMLElement, Omit<HeadingProps, 'level' | 'as'>>((props, ref) => (
  <Heading ref={ref} level={4} {...props} />
))
H4.displayName = 'H4'

export const H5 = React.forwardRef<HTMLElement, Omit<HeadingProps, 'level' | 'as'>>((props, ref) => (
  <Heading ref={ref} level={5} {...props} />
))
H5.displayName = 'H5'

export const H6 = React.forwardRef<HTMLElement, Omit<HeadingProps, 'level' | 'as'>>((props, ref) => (
  <Heading ref={ref} level={6} {...props} />
))
H6.displayName = 'H6'

export default Heading