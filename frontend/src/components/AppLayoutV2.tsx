/**
 * Main application layout V2 with shadcn/ui components and dark mode support
 */
import React, { useState } from 'react'
import { Link, useLocation, useNavigate, Outlet } from 'react-router-dom'
import { 
  Building2, 
  Target, 
  Settings, 
  Menu,
  Home,
  ChevronRight,
  Search,
  Bell,
  User,
  Command,
  X,
  FlaskConical,
  Calendar
} from 'lucide-react'

import { Button } from './ui/button'
import { Input } from './ui/input'
import { Badge } from './ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from './ui/dropdown-menu'
import { ThemeToggle } from './ui/theme-toggle'
import { cn } from '../lib/utils'

interface AppLayoutV2Props {
  children?: React.ReactNode
}

const navigation = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: Home,
    current: false,
  },
  {
    name: 'Offices',
    href: '/offices',
    icon: Building2,
    current: false,
  },
  {
    name: 'Business Planning',
    href: '/business-planning',
    icon: Calendar,
    current: false,
  },
  {
    name: 'Scenarios',
    href: '/scenarios',
    icon: Target,
    current: false,
  },
  {
    name: 'Scenario Editor Test',
    href: '/scenario-editor-test',
    icon: FlaskConical,
    current: false,
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
    current: false,
  },
]

// Mock user data - this would come from authentication context
const mockUser = {
  name: 'John Doe',
  email: 'john.doe@simplesim.com',
  avatar: undefined
}

// Generate breadcrumbs based on current path
const getBreadcrumbs = (pathname: string) => {
  const segments = pathname.split('/').filter(Boolean)
  const breadcrumbs = [{ label: 'Dashboard', path: '/dashboard', current: false }]
  
  if (segments.length > 0 && segments[0] !== 'dashboard') {
    const currentPage = navigation.find(item => item.href.includes(segments[0]))
    if (currentPage) {
      breadcrumbs.push({ 
        label: currentPage.name, 
        path: currentPage.href,
        current: segments.length === 1 
      })
      
      // Add scenario-specific breadcrumb if viewing results
      if (segments[0] === 'scenarios' && segments.length > 2 && segments[2] === 'results') {
        breadcrumbs.push({ 
          label: 'Results', 
          path: pathname,
          current: true 
        })
        breadcrumbs[breadcrumbs.length - 2].current = false
      }
    }
  } else {
    breadcrumbs[0].current = true
  }
  
  return breadcrumbs
}

export const AppLayoutV2: React.FC<AppLayoutV2Props> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const location = useLocation()
  const navigate = useNavigate()

  const currentNavigation = navigation.map(item => ({
    ...item,
    current: location.pathname === item.href || location.pathname.startsWith(item.href + '/')
  }))

  const breadcrumbs = getBreadcrumbs(location.pathname)

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      console.log('Search:', searchQuery.trim())
      // TODO: Implement search functionality
    }
  }

  return (
    <div className="h-screen flex overflow-hidden bg-background w-full">
      {/* Sidebar */}
      <div className={cn(
        "fixed inset-y-0 left-0 z-50 w-64 bg-card border-r border-border transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0",
        sidebarOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center h-16 px-6 border-b border-border">
            <h1 className="text-xl font-bold text-foreground">SimpleSim</h1>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
            {currentNavigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  "flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors",
                  item.current
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:text-foreground hover:bg-accent"
                )}
                onClick={() => setSidebarOpen(false)}
              >
                <item.icon className="mr-3 h-5 w-5 flex-shrink-0" />
                {item.name}
              </Link>
            ))}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-border">
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">v2.0.0</span>
              <ThemeToggle />
            </div>
          </div>
        </div>
      </div>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden lg:ml-1">
        {/* Enhanced Top Header */}
        <header className="bg-card border-b border-border px-4 py-3 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            {/* Mobile menu button + Breadcrumbs */}
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                className="lg:hidden"
                onClick={() => setSidebarOpen(true)}
              >
                <Menu className="h-5 w-5" />
              </Button>
              
              {/* Breadcrumbs */}
              <nav className="hidden sm:flex items-center gap-2 text-sm text-muted-foreground">
                {breadcrumbs.map((crumb, index) => (
                  <React.Fragment key={crumb.path}>
                    {index > 0 && <ChevronRight className="h-4 w-4" />}
                    {crumb.current ? (
                      <span className="text-foreground font-medium">{crumb.label}</span>
                    ) : (
                      <Link 
                        to={crumb.path} 
                        className="hover:text-foreground transition-colors"
                      >
                        {crumb.label}
                      </Link>
                    )}
                  </React.Fragment>
                ))}
              </nav>
            </div>
            
            {/* Right side actions */}
            <div className="flex items-center gap-4">
              {/* Global Search */}
              <form onSubmit={handleSearch} className="relative hidden md:block">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <Input
                  type="search"
                  placeholder="Search... (⌘K)"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 w-64 h-9"
                />
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-xs font-medium text-muted-foreground opacity-100">
                    <Command className="h-3 w-3" />K
                  </kbd>
                </div>
              </form>

              {/* Notifications */}
              <Button
                variant="ghost"
                size="icon"
                className="relative h-9 w-9"
                onClick={() => console.log('Notifications clicked')}
              >
                <Bell className="h-4 w-4" />
                <Badge
                  variant="destructive"
                  className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 text-xs flex items-center justify-center"
                >
                  3
                </Badge>
              </Button>

              {/* User Menu */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-9 w-9 rounded-full">
                    <Avatar className="h-9 w-9">
                      <AvatarImage src={mockUser.avatar} alt={mockUser.name} />
                      <AvatarFallback>
                        {mockUser.name.substring(0, 2).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end">
                  <div className="flex items-center justify-start gap-2 p-2">
                    <div className="flex flex-col space-y-1 leading-none">
                      <p className="font-medium">{mockUser.name}</p>
                      <p className="w-[200px] truncate text-sm text-muted-foreground">
                        {mockUser.email}
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
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          <div className="p-0">
            {children || <Outlet />}
          </div>
        </main>
      </div>
    </div>
  )
}