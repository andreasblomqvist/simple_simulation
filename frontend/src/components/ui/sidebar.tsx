/**
 * Sidebar Component
 * 
 * Dashboard sidebar navigation following shadcn dashboard-01 pattern
 */
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { cn } from '../../lib/utils';
import { Button } from './button';
import { ScrollArea } from './scroll-area';
import { 
  Home,
  Building,
  Users,
  BarChart3,
  Settings,
  FileText,
  Calculator,
  Beaker,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

interface SidebarProps extends React.HTMLAttributes<HTMLDivElement> {
  collapsed?: boolean;
  onToggle?: () => void;
}

const navigation = [
  {
    name: 'Dashboard',
    href: '/',
    icon: Home,
    description: 'Overview and key metrics'
  },
  {
    name: 'Scenarios',
    href: '/scenarios',
    icon: BarChart3,
    description: 'Scenario management and comparison'
  },
  {
    name: 'Business Planning',
    href: '/business-planning',
    icon: Calculator,
    description: 'Workforce and financial planning'
  },
  {
    name: 'Offices',
    href: '/offices',
    icon: Building,
    description: 'Office management and configuration'
  },
  {
    name: 'Simulation Lab',
    href: '/simulation-lab',
    icon: Beaker,
    description: 'Advanced simulation experiments'
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
    description: 'Application settings and configuration'
  }
];

export function Sidebar({ collapsed = false, onToggle, className, ...props }: SidebarProps) {
  const location = useLocation();

  return (
    <div 
      className={cn(
        "relative flex h-full flex-col border-r bg-background transition-all duration-300",
        collapsed ? "w-16" : "w-64",
        className
      )}
      {...props}
    >
      {/* Header */}
      <div className="flex h-16 items-center border-b px-4">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <BarChart3 className="h-4 w-4" />
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-semibold">SimpleSim</span>
              <span className="text-xs text-muted-foreground">Workforce Planning</span>
            </div>
          </div>
        )}
        
        {/* Toggle Button */}
        {onToggle && (
          <Button
            variant="ghost"
            size="sm"
            className={cn(
              "h-8 w-8 p-0",
              collapsed ? "ml-2" : "ml-auto"
            )}
            onClick={onToggle}
          >
            {collapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <ChevronLeft className="h-4 w-4" />
            )}
          </Button>
        )}
      </div>

      {/* Navigation */}
      <ScrollArea className="flex-1 px-3 py-4">
        <nav className="space-y-2">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.href || 
              (item.href !== '/' && location.pathname.startsWith(item.href));

            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  "group flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors hover:bg-accent hover:text-accent-foreground",
                  isActive 
                    ? "bg-accent text-accent-foreground font-medium" 
                    : "text-muted-foreground"
                )}
              >
                <Icon className={cn(
                  "h-4 w-4 transition-colors",
                  isActive ? "text-accent-foreground" : "text-muted-foreground"
                )} />
                {!collapsed && (
                  <div className="flex flex-col">
                    <span>{item.name}</span>
                    {!isActive && (
                      <span className="text-xs text-muted-foreground group-hover:text-accent-foreground">
                        {item.description}
                      </span>
                    )}
                  </div>
                )}
              </Link>
            );
          })}
        </nav>
      </ScrollArea>

      {/* Footer */}
      <div className="border-t p-4">
        {!collapsed && (
          <div className="text-xs text-muted-foreground">
            <div>Version 2.0.0</div>
            <div>© 2024 SimpleSim</div>
          </div>
        )}
      </div>
    </div>
  );
}