/**
 * Layout Components - SimpleSim Design System
 * 
 * Essential layout primitives for consistent page structure and component composition.
 * All components use design tokens for spacing and follow the specifications in
 * layout-composition-patterns.md and component-api-specifications.md.
 */

export { Container, type ContainerProps } from './Container'
export { Stack, type StackProps } from './Stack' 
export { Grid, type GridProps } from './Grid'

// Re-export default components for convenience
export { default as DefaultContainer } from './Container'
export { default as DefaultStack } from './Stack'
export { default as DefaultGrid } from './Grid'