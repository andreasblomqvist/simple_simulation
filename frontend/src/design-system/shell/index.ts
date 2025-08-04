/**
 * SimpleSim Application Shell Components
 * 
 * Complete application shell that eliminates UI bloat by providing:
 * - Single navigation system (top nav replaces sidebar)
 * - Consolidated context bar (replaces scattered breadcrumbs/actions)
 * - Clean layout structure (Header + ContextBar + Main + Footer)
 * - Context-aware interfaces
 */

export { AppShell, ContextBarProvider, useContextBar, useSetContextBar } from './AppShell'
export { Header } from './Header'
export { ContextBar, SimpleContextBar } from './ContextBar'
export { Footer } from './Footer'

export type { AppShellProps, ContextBarConfig } from './AppShell'
export type { SimpleContextBarProps } from './ContextBar'