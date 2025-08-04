/**
 * Footer - Application Footer
 * 
 * Simple footer component for status, help, and quick actions:
 * - System status and version info
 * - Help and support links
 * - Quick actions for power users
 * - 48px height, minimal visual weight
 */

import React from 'react'
import { Link } from 'react-router-dom'
import { HelpCircle, ExternalLink, Zap } from 'lucide-react'

import { Button } from '../../components/ui/button'
import { Badge } from '../../components/ui/badge'
import { Separator } from '../../components/ui/separator'

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-border bg-muted/30 h-12 flex-shrink-0">
      <div className="h-full max-w-full px-6">
        <div className="flex items-center justify-between h-full">
          
          {/* Left Section: Status and Version */}
          <div className="flex items-center space-x-4 text-xs text-muted-foreground">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full" />
              <span>All systems operational</span>
            </div>
            
            <Separator orientation="vertical" className="h-4" />
            
            <div className="flex items-center space-x-2">
              <span>SimpleSim v2.1.0</span>
              <Badge variant="outline" className="h-5 text-xs">
                Beta
              </Badge>
            </div>
          </div>

          {/* Center Section: Quick Stats (optional) */}
          <div className="flex items-center space-x-4 text-xs text-muted-foreground">
            <span>Last sync: 2 min ago</span>
            <Separator orientation="vertical" className="h-4" />
            <span>3 scenarios running</span>
          </div>

          {/* Right Section: Help and Quick Actions */}
          <div className="flex items-center space-x-2">
            
            {/* Help Button */}
            <Button
              variant="ghost"
              size="sm"
              className="h-8 text-xs text-muted-foreground hover:text-foreground"
              onClick={() => console.log('Help clicked')}
            >
              <div className="inline-flex items-center">
                <HelpCircle className="w-3 h-3 mr-1" />
                Help
              </div>
            </Button>

            {/* Documentation Link */}
            <Button
              variant="ghost"
              size="sm"
              className="h-8 text-xs text-muted-foreground hover:text-foreground"
              asChild
            >
              <Link to="/docs" target="_blank" rel="noopener noreferrer">
                <div className="inline-flex items-center">
                  <ExternalLink className="w-3 h-3 mr-1" />
                  Docs
                </div>
              </Link>
            </Button>

            {/* Power User Actions (keyboard shortcut indicator) */}
            <Button
              variant="ghost"
              size="sm"
              className="h-8 text-xs text-muted-foreground hover:text-foreground"
              onClick={() => console.log('Keyboard shortcuts')}
            >
              <div className="inline-flex items-center">
                <Zap className="w-3 h-3 mr-1" />
                <kbd className="pointer-events-none inline-flex h-4 select-none items-center gap-0.5 rounded border bg-muted px-1 font-mono text-[10px] font-medium text-muted-foreground opacity-100">
                  ?
                </kbd>
              </div>
            </Button>
          </div>
        </div>
      </div>
    </footer>
  )
}