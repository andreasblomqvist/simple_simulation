/**
 * AppShell - Simplified Application Shell
 * 
 * Eliminates UI bloat by providing a clean, single-navigation structure:
 * - Header: Logo + Top Navigation + User Menu (64px, fixed)
 * - ContextBar: Breadcrumb + Actions + Filters (56px, sticky) 
 * - Main: Content area with proper spacing
 * - Footer: Status + Help + Quick Actions (48px)
 * 
 * Replaces AppLayoutV2's complex sidebar + breadcrumbs + multiple headers
 */

import React from 'react'
import { Outlet } from 'react-router-dom'
import { Header } from './Header'
import { ContextBar } from './ContextBar'
import { Footer } from './Footer'
import { cn } from '../../lib/utils'

export interface AppShellProps {
  children?: React.ReactNode
  className?: string
}

export interface ContextBarConfig {
  breadcrumb?: {
    items: Array<{
      label: string
      href?: string
      current?: boolean
    }>
  }
  primaryAction?: {
    label: string
    onClick: () => void
    variant?: 'primary' | 'secondary'
    icon?: React.ReactNode
  }
  secondaryActions?: Array<{
    label: string
    onClick: () => void
    icon?: React.ReactNode
  }>
  filters?: Array<{
    label: string
    value: string
    options: Array<{ label: string; value: string }>
    onChange: (value: string) => void
  }>
  status?: {
    label: string
    variant: 'success' | 'warning' | 'error' | 'info'
  }
}

export const AppShell: React.FC<AppShellProps> = ({ 
  children, 
  className 
}) => {
  return (
    <div className={cn(
      "min-h-screen flex flex-col bg-background",
      className
    )}>
      {/* Fixed Header - 64px height */}
      <Header />
      
      {/* Sticky Context Bar - 56px height, positioned below header */}
      <ContextBar />
      
      {/* Main Content Area - accounts for header + context bar height */}
      <main className="flex-1 pt-[120px] min-h-[calc(100vh-120px)]">
        <div className="h-full">
          {children || <Outlet />}
        </div>
      </main>
      
      {/* Footer - 48px height */}
      <Footer />
    </div>
  )
}

/**
 * Context Provider for ContextBar configuration
 * Allows pages to configure the context bar content
 */
import { createContext, useContext } from 'react'

const ContextBarContext = createContext<{
  config: ContextBarConfig | null
  setConfig: (config: ContextBarConfig | null) => void
}>({
  config: null,
  setConfig: () => {}
})

export const ContextBarProvider: React.FC<{
  children: React.ReactNode
}> = ({ children }) => {
  const [config, setConfig] = React.useState<ContextBarConfig | null>(null)
  
  return (
    <ContextBarContext.Provider value={{ config, setConfig }}>
      {children}
    </ContextBarContext.Provider>
  )
}

export const useContextBar = () => {
  const context = useContext(ContextBarContext)
  if (!context) {
    throw new Error('useContextBar must be used within ContextBarProvider')
  }
  return context
}

// Hook for pages to easily configure the context bar
export const useSetContextBar = (config: ContextBarConfig | null) => {
  const { setConfig } = useContextBar()
  
  React.useEffect(() => {
    setConfig(config)
    return () => setConfig(null) // Cleanup on unmount
  }, [config, setConfig])
}