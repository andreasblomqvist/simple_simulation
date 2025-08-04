/**
 * ContextBar - Contextual Action and Navigation Bar
 * 
 * Consolidates scattered UI elements into a single context-aware bar:
 * - Breadcrumb navigation (replaces complex breadcrumb systems)
 * - Primary and secondary actions (eliminates scattered buttons)
 * - Filters and search (contextual to current page)
 * - Status indicators (current state awareness)
 * 
 * Sticky positioned below header (56px height)
 */

import React from 'react'
import { Link } from 'react-router-dom'
import { ChevronRight, Filter, MoreHorizontal } from 'lucide-react'

import { Button } from '../../components/ui/button'
import { Badge } from '../../components/ui/badge'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from '../../components/ui/dropdown-menu'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../components/ui/select'
import { useContextBar } from './AppShell'
import { cn } from '../../lib/utils'

export const ContextBar: React.FC = () => {
  const { config } = useContextBar()
  
  // Don't render if no configuration is provided
  if (!config) {
    return null
  }

  const { breadcrumb, primaryAction, secondaryActions, filters, status } = config

  return (
    <div className="sticky top-16 z-40 bg-muted/30 border-b border-border h-14">
      <div className="h-full max-w-full px-6">
        <div className="flex items-center justify-between h-full">
          
          {/* Left Section: Breadcrumb + Status */}
          <div className="flex items-center space-x-4 flex-1 min-w-0">
            
            {/* Breadcrumb Navigation */}
            {breadcrumb && (
              <nav className="flex items-center space-x-2 text-sm text-muted-foreground min-w-0">
                {breadcrumb.items.map((item, index) => (
                  <React.Fragment key={`${item.label}-${index}`}>
                    {index > 0 && <ChevronRight className="h-4 w-4 flex-shrink-0" />}
                    {item.current ? (
                      <span className="text-foreground font-medium truncate">
                        {item.label}
                      </span>
                    ) : item.href ? (
                      <Link 
                        to={item.href} 
                        className="hover:text-foreground transition-colors truncate"
                      >
                        {item.label}
                      </Link>
                    ) : (
                      <span className="truncate">{item.label}</span>
                    )}
                  </React.Fragment>
                ))}
              </nav>
            )}

            {/* Status Indicator */}
            {status && (
              <Badge 
                variant={
                  status.variant === 'success' ? 'default' :
                  status.variant === 'warning' ? 'secondary' :
                  status.variant === 'error' ? 'destructive' :
                  'outline'
                }
                className="flex-shrink-0"
              >
                {status.label}
              </Badge>
            )}
          </div>

          {/* Center Section: Filters */}
          {filters && filters.length > 0 && (
            <div className="flex items-center space-x-3 px-4">
              <Filter className="h-4 w-4 text-muted-foreground" />
              {filters.map((filter) => (
                <Select
                  key={filter.label}
                  value={filter.value}
                  onValueChange={filter.onChange}
                >
                  <SelectTrigger className="w-auto min-w-[120px] h-8">
                    <SelectValue placeholder={filter.label} />
                  </SelectTrigger>
                  <SelectContent>
                    {filter.options.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              ))}
            </div>
          )}

          {/* Right Section: Actions */}
          <div className="flex items-center space-x-2 flex-shrink-0">
            
            {/* Secondary Actions - show first 2, rest in dropdown */}
            {secondaryActions && secondaryActions.length > 0 && (
              <>
                {secondaryActions.slice(0, 2).map((action, index) => (
                  <Button
                    key={`${action.label}-${index}`}
                    variant="ghost"
                    size="sm"
                    onClick={action.onClick}
                    className="h-8"
                  >
                    {action.icon}
                    <span className="ml-1">{action.label}</span>
                  </Button>
                ))}
                
                {/* More actions dropdown */}
                {secondaryActions.length > 2 && (
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      {secondaryActions.slice(2).map((action, index) => (
                        <DropdownMenuItem
                          key={`more-${action.label}-${index}`}
                          onClick={action.onClick}
                        >
                          {action.icon}
                          <span className="ml-2">{action.label}</span>
                        </DropdownMenuItem>
                      ))}
                    </DropdownMenuContent>
                  </DropdownMenu>
                )}
              </>
            )}

            {/* Primary Action */}
            {primaryAction && (
              <Button
                variant={primaryAction.variant || 'primary'}
                size="sm"
                onClick={primaryAction.onClick}
                className="h-8"
              >
                {primaryAction.icon}
                <span className={cn(primaryAction.icon && "ml-1")}>
                  {primaryAction.label}
                </span>
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

/**
 * Utility component for pages that need a simple context bar
 * without using the hook system
 */
export interface SimpleContextBarProps {
  title: string
  breadcrumbs?: Array<{
    label: string
    href?: string
  }>
  primaryAction?: {
    label: string
    onClick: () => void
    variant?: 'primary' | 'secondary'
    icon?: React.ReactNode
  }
  actions?: Array<{
    label: string
    onClick: () => void
    icon?: React.ReactNode
  }>
  status?: {
    label: string
    variant: 'success' | 'warning' | 'error' | 'info'
  }
}

export const SimpleContextBar: React.FC<SimpleContextBarProps> = ({
  title,
  breadcrumbs = [],
  primaryAction,
  actions = [],
  status
}) => {
  const breadcrumbItems = [
    ...breadcrumbs,
    { label: title, current: true }
  ]

  return (
    <div className="sticky top-16 z-40 bg-muted/30 border-b border-border h-14">
      <div className="h-full max-w-full px-6">
        <div className="flex items-center justify-between h-full">
          
          {/* Breadcrumb */}
          <div className="flex items-center space-x-4 flex-1 min-w-0">
            <nav className="flex items-center space-x-2 text-sm text-muted-foreground min-w-0">
              {breadcrumbItems.map((item, index) => (
                <React.Fragment key={`${item.label}-${index}`}>
                  {index > 0 && <ChevronRight className="h-4 w-4 flex-shrink-0" />}
                  {item.current ? (
                    <span className="text-foreground font-medium truncate">
                      {item.label}
                    </span>
                  ) : item.href ? (
                    <Link 
                      to={item.href} 
                      className="hover:text-foreground transition-colors truncate"
                    >
                      {item.label}
                    </Link>
                  ) : (
                    <span className="truncate">{item.label}</span>
                  )}
                </React.Fragment>
              ))}
            </nav>

            {status && (
              <Badge 
                variant={
                  status.variant === 'success' ? 'default' :
                  status.variant === 'warning' ? 'secondary' :
                  status.variant === 'error' ? 'destructive' :
                  'outline'
                }
                className="flex-shrink-0"
              >
                {status.label}
              </Badge>
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-2 flex-shrink-0">
            {actions.slice(0, 2).map((action, index) => (
              <Button
                key={`${action.label}-${index}`}
                variant="ghost"
                size="sm"
                onClick={action.onClick}
                className="h-8"
              >
                {action.icon}
                <span className={cn(action.icon && "ml-1")}>{action.label}</span>
              </Button>
            ))}
            
            {primaryAction && (
              <Button
                variant={primaryAction.variant || 'primary'}
                size="sm"
                onClick={primaryAction.onClick}
                className="h-8"
              >
                {primaryAction.icon}
                <span className={cn(primaryAction.icon && "ml-1")}>
                  {primaryAction.label}
                </span>
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}