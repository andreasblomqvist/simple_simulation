import React, { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  Building2,
  Target,
  PlayCircle,
  BarChart3,
  Settings,
  Menu,
  X,
  ChevronRight,
  Home,
  User,
  Bell,
  Search,
  Command
} from 'lucide-react'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Badge } from '../ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '../ui/dropdown-menu'
import { ThemeToggle } from '../ui/theme-toggle'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../ui/tooltip'
import { cn } from '../../lib/utils'

export interface NavigationItem {
  key: string
  label: string
  path: string
  icon: React.ComponentType<{ className?: string }>
  badge?: {
    text: string
    variant?: 'default' | 'secondary' | 'destructive' | 'outline'
  }
  children?: NavigationItem[]
  disabled?: boolean
}

interface AppNavigationProps {
  /** Navigation items */
  items: NavigationItem[]
  /** Application title */
  title?: string
  /** Application logo/icon */
  logo?: React.ReactNode
  /** User information */
  user?: {
    name: string
    email: string
    avatar?: string
  }
  /** Show search bar */
  searchable?: boolean
  /** Search handler */
  onSearch?: (query: string) => void
  /** Notification count */
  notificationCount?: number
  /** Notification click handler */
  onNotificationClick?: () => void
  /** Additional header actions */
  headerActions?: React.ReactNode
}

const defaultNavigationItems: NavigationItem[] = [
  {
    key: 'dashboard',
    label: 'Dashboard',
    path: '/dashboard',
    icon: LayoutDashboard
  },
  {
    key: 'offices',
    label: 'Office Management',
    path: '/offices',
    icon: Building2
  },
  {
    key: 'office-overview',
    label: 'Office Overview',
    path: '/office-overview',
    icon: Building2
  },
  {
    key: 'scenarios',
    label: 'Scenarios',
    path: '/scenarios',
    icon: Target,
    badge: { text: 'New', variant: 'secondary' }
  },
  {
    key: 'simulation',
    label: 'Simulation Lab',
    path: '/simulation',
    icon: PlayCircle
  },
  {
    key: 'reports',
    label: 'Reports',
    path: '/reports',
    icon: BarChart3
  },
  {
    key: 'settings',
    label: 'Settings',
    path: '/settings',
    icon: Settings
  }
]

export function AppNavigation({
  items = defaultNavigationItems,
  title = 'SimpleSim',
  logo,
  user,
  searchable = true,
  onSearch,
  notificationCount = 0,
  onNotificationClick,
  headerActions
}: AppNavigationProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const location = useLocation()
  const navigate = useNavigate()

  const isActiveRoute = (path: string) => {
    if (path === '/dashboard' && location.pathname === '/') return true
    return location.pathname.startsWith(path)
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (onSearch && searchQuery.trim()) {
      onSearch(searchQuery.trim())
    }
  }

  const NavItem = ({ item, depth = 0 }: { item: NavigationItem; depth?: number }) => {
    const isActive = isActiveRoute(item.path)
    const hasChildren = item.children && item.children.length > 0
    
    const Icon = item.icon
    const paddingLeft = `${1 + depth * 0.5}rem`

    if (hasChildren) {
      return (
        <div className="space-y-1">
          <div
            className={cn(
              "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
              "text-muted-foreground hover:text-foreground hover:bg-accent"
            )}
            style={{ paddingLeft }}
          >
            <Icon className="h-4 w-4 flex-shrink-0" />
            {sidebarOpen && (
              <>
                <span className="flex-1">{item.label}</span>
                {item.badge && (
                  <Badge variant={item.badge.variant || 'default'} className="text-xs">
                    {item.badge.text}
                  </Badge>
                )}
                <ChevronRight className="h-4 w-4 flex-shrink-0" />
              </>
            )}
          </div>
          {sidebarOpen && (
            <div className="space-y-1">
              {item.children?.map(child => (
                <NavItem key={child.key} item={child} depth={depth + 1} />
              ))}
            </div>
          )}
        </div>
      )
    }

    const content = (
      <Link
        to={item.path}
        className={cn(
          "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
          isActive
            ? "bg-primary text-primary-foreground shadow-sm"
            : "text-muted-foreground hover:text-foreground hover:bg-accent",
          item.disabled && "opacity-50 cursor-not-allowed pointer-events-none"
        )}
        style={{ paddingLeft }}
      >
        <Icon className="h-4 w-4 flex-shrink-0" />
        {sidebarOpen && (
          <>
            <span className="flex-1">{item.label}</span>
            {item.badge && (
              <Badge variant={item.badge.variant || 'default'} className="text-xs">
                {item.badge.text}
              </Badge>
            )}
          </>
        )}
      </Link>
    )

    if (!sidebarOpen) {
      return (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              {content}
            </TooltipTrigger>
            <TooltipContent side="right">
              <p>{item.label}</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      )
    }

    return content
  }

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <div className={cn(
        "flex flex-col border-r bg-card transition-all duration-300 ease-in-out",
        sidebarOpen ? "w-64" : "w-16"
      )}>
        {/* Sidebar Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center gap-2">
            {logo}
            {sidebarOpen && (
              <h1 className="text-lg font-semibold text-foreground">{title}</h1>
            )}
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="h-8 w-8"
          >
            {sidebarOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
          </Button>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 space-y-1 p-4 overflow-y-auto">
          {items.map(item => (
            <NavItem key={item.key} item={item} />
          ))}
        </nav>

        {/* Sidebar Footer */}
        <div className="border-t p-4">
          <div className="flex items-center justify-center">
            <ThemeToggle />
            {sidebarOpen && user && (
              <div className="flex items-center gap-2 ml-4">
                <Avatar className="h-6 w-6">
                  <AvatarImage src={user.avatar} />
                  <AvatarFallback className="text-xs">
                    {user.name.substring(0, 2).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <span className="text-xs text-muted-foreground truncate">
                  {user.name}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <header className="flex items-center justify-between px-6 py-4 border-b bg-card">
          <div className="flex items-center gap-4">
            {/* Breadcrumb placeholder - will be implemented in next step */}
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Home className="h-4 w-4" />
              <ChevronRight className="h-4 w-4" />
              <span>Current Page</span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Global Search */}
            {searchable && (
              <form onSubmit={handleSearch} className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <Input
                  type="search"
                  placeholder="Search... (⌘K)"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 w-64"
                />
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-xs font-medium text-muted-foreground opacity-100">
                    <Command className="h-3 w-3" />K
                  </kbd>
                </div>
              </form>
            )}

            {/* Header Actions */}
            {headerActions}

            {/* Notifications */}
            <Button
              variant="ghost"
              size="icon"
              onClick={onNotificationClick}
              className="relative"
            >
              <Bell className="h-4 w-4" />
              {notificationCount > 0 && (
                <Badge
                  variant="destructive"
                  className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 text-xs flex items-center justify-center"
                >
                  {notificationCount > 99 ? '99+' : notificationCount}
                </Badge>
              )}
            </Button>

            {/* User Menu */}
            {user && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={user.avatar} alt={user.name} />
                      <AvatarFallback>
                        {user.name.substring(0, 2).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end">
                  <div className="flex items-center justify-start gap-2 p-2">
                    <div className="flex flex-col space-y-1 leading-none">
                      <p className="font-medium">{user.name}</p>
                      <p className="w-[200px] truncate text-sm text-muted-foreground">
                        {user.email}
                      </p>
                    </div>
                  </div>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => navigate('/profile')}>
                    <User className="mr-2 h-4 w-4" />
                    Profile
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => navigate('/settings')}>
                    <Settings className="mr-2 h-4 w-4" />
                    Settings
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem>
                    Log out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 overflow-auto bg-background">
          {/* Content will be passed as children */}
        </main>
      </div>
    </div>
  )
}