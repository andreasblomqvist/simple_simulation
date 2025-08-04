import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { ChevronRight, Home } from 'lucide-react'
import { cn } from '../../lib/utils'

export interface BreadcrumbItem {
  /** Display label */
  label: string
  /** Route path - omit for non-clickable items */
  path?: string
  /** Icon component */
  icon?: React.ComponentType<{ className?: string }>
  /** Whether this item is the current page */
  current?: boolean
}

interface BreadcrumbProps {
  /** Breadcrumb items */
  items: BreadcrumbItem[]
  /** Show home icon */
  showHome?: boolean
  /** Home path */
  homePath?: string
  /** Custom separator */
  separator?: React.ReactNode
  /** Custom CSS classes */
  className?: string
  /** Max items to show before truncation */
  maxItems?: number
}

// Route to breadcrumb mapping for auto-generation
const routeBreadcrumbMap: Record<string, BreadcrumbItem[]> = {
  '/': [{ label: 'Dashboard', path: '/', icon: Home, current: true }],
  '/dashboard': [{ label: 'Dashboard', path: '/dashboard', icon: Home, current: true }],
  '/offices': [
    { label: 'Dashboard', path: '/dashboard', icon: Home },
    { label: 'Office Management', current: true }
  ],
  '/offices/new': [
    { label: 'Dashboard', path: '/dashboard', icon: Home },
    { label: 'Office Management', path: '/offices' },
    { label: 'New Office', current: true }
  ],
  '/scenarios': [
    { label: 'Dashboard', path: '/dashboard', icon: Home },
    { label: 'Scenarios', current: true }
  ],
  '/scenarios/new': [
    { label: 'Dashboard', path: '/dashboard', icon: Home },
    { label: 'Scenarios', path: '/scenarios' },
    { label: 'New Scenario', current: true }
  ],
  '/scenarios/:id': [
    { label: 'Dashboard', path: '/dashboard', icon: Home },
    { label: 'Scenarios', path: '/scenarios' },
    { label: 'Scenario Details', current: true }
  ],
  '/simulation': [
    { label: 'Dashboard', path: '/dashboard', icon: Home },
    { label: 'Simulation Lab', current: true }
  ],
  '/reports': [
    { label: 'Dashboard', path: '/dashboard', icon: Home },
    { label: 'Reports', current: true }
  ],
  '/settings': [
    { label: 'Dashboard', path: '/dashboard', icon: Home },
    { label: 'Settings', current: true }
  ],
  '/settings/profile': [
    { label: 'Dashboard', path: '/dashboard', icon: Home },
    { label: 'Settings', path: '/settings' },
    { label: 'Profile', current: true }
  ]
}

/**
 * Auto-generate breadcrumbs from current route
 */
function useAutoBreadcrumbs(): BreadcrumbItem[] {
  const location = useLocation()
  const pathname = location.pathname

  // Try exact match first
  if (routeBreadcrumbMap[pathname]) {
    return routeBreadcrumbMap[pathname]
  }

  // Try pattern matching for dynamic routes
  for (const [pattern, breadcrumbs] of Object.entries(routeBreadcrumbMap)) {
    const regex = new RegExp('^' + pattern.replace(/:\w+/g, '[^/]+') + '$')
    if (regex.test(pathname)) {
      return breadcrumbs.map(item => ({
        ...item,
        current: item.current && pathname === location.pathname
      }))
    }
  }

  // Fallback: generate from path segments
  const segments = pathname.split('/').filter(Boolean)
  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Dashboard', path: '/dashboard', icon: Home }
  ]

  let currentPath = ''
  segments.forEach((segment, index) => {
    currentPath += `/${segment}`
    const isLast = index === segments.length - 1
    
    breadcrumbs.push({
      label: segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' '),
      path: isLast ? undefined : currentPath,
      current: isLast
    })
  })

  return breadcrumbs
}

export function Breadcrumb({
  items,
  showHome = true,
  homePath = '/dashboard',
  separator,
  className,
  maxItems = 5
}: BreadcrumbProps) {
  const autoBreadcrumbs = useAutoBreadcrumbs()
  const breadcrumbItems = items || autoBreadcrumbs

  // Truncate if too many items
  const displayItems = React.useMemo(() => {
    if (breadcrumbItems.length <= maxItems) {
      return breadcrumbItems
    }

    const first = breadcrumbItems[0]
    const last = breadcrumbItems[breadcrumbItems.length - 1]
    const middle = breadcrumbItems.slice(-2, -1) // Show one item before last

    return [
      first,
      { label: '...', path: undefined }, // Ellipsis
      ...middle,
      last
    ].filter(Boolean)
  }, [breadcrumbItems, maxItems])

  const defaultSeparator = separator || <ChevronRight className="h-4 w-4 text-muted-foreground" />

  return (
    <nav className={cn("flex items-center space-x-1 text-sm", className)} aria-label="Breadcrumb">
      <ol className="flex items-center space-x-1">
        {displayItems.map((item, index) => {
          const isLast = index === displayItems.length - 1
          const Icon = item.icon
          
          return (
            <li key={`${item.label}-${index}`} className="flex items-center">
              {index > 0 && (
                <span className="mx-2" aria-hidden="true">
                  {defaultSeparator}
                </span>
              )}
              
              <div className={cn(
                "flex items-center gap-1.5",
                isLast 
                  ? "text-foreground font-medium" 
                  : "text-muted-foreground hover:text-foreground transition-colors"
              )}>
                {Icon && (
                  <Icon className={cn(
                    "h-4 w-4",
                    index === 0 && "text-primary" // Home icon in primary color
                  )} />
                )}
                
                {item.path && !isLast ? (
                  <Link 
                    to={item.path} 
                    className="hover:underline"
                    aria-current={isLast ? 'page' : undefined}
                  >
                    {item.label}
                  </Link>
                ) : (
                  <span aria-current={isLast ? 'page' : undefined}>
                    {item.label}
                  </span>
                )}
              </div>
            </li>
          )
        })}
      </ol>
    </nav>
  )
}

/**
 * Hook to manually set breadcrumbs for complex pages
 */
export function useBreadcrumbs(items: BreadcrumbItem[]) {
  // This would be implemented with context in a real application
  // For now, return the items as-is
  return items
}

/**
 * Higher-order component to automatically add breadcrumbs to a page
 */
export function withBreadcrumbs<P extends object>(
  Component: React.ComponentType<P>,
  breadcrumbItems: BreadcrumbItem[] | ((props: P) => BreadcrumbItem[])
) {
  return function BreadcrumbWrapper(props: P) {
    const items = typeof breadcrumbItems === 'function' 
      ? breadcrumbItems(props) 
      : breadcrumbItems

    return (
      <div className="space-y-4">
        <Breadcrumb items={items} />
        <Component {...props} />
      </div>
    )
  }
}