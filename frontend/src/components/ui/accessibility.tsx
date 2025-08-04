import React, { useEffect, useRef } from 'react'
import { AlertTriangle, CheckCircle, Info, XCircle } from 'lucide-react'
import { cn } from '../../lib/utils'

// Screen reader only text
interface ScreenReaderOnlyProps {
  children: React.ReactNode
}

export function ScreenReaderOnly({ children }: ScreenReaderOnlyProps) {
  return (
    <span className="sr-only">
      {children}
    </span>
  )
}

// Focus trap for modals and dialogs
interface FocusTrapProps {
  children: React.ReactNode
  /** Enable focus trap */
  enabled?: boolean
  /** Initial focus element selector */
  initialFocus?: string
  /** Return focus element selector */
  returnFocus?: string
}

export function FocusTrap({ 
  children, 
  enabled = true, 
  initialFocus,
  returnFocus 
}: FocusTrapProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const lastActiveElementRef = useRef<Element | null>(null)

  useEffect(() => {
    if (!enabled) return

    // Store the currently focused element
    lastActiveElementRef.current = document.activeElement

    const container = containerRef.current
    if (!container) return

    // Get all focusable elements
    const getFocusableElements = () => {
      return container.querySelectorAll(
        'a[href], button, input, textarea, select, details, [tabindex]:not([tabindex="-1"])'
      )
    }

    const focusableElements = getFocusableElements()
    const firstFocusable = focusableElements[0] as HTMLElement
    const lastFocusable = focusableElements[focusableElements.length - 1] as HTMLElement

    // Focus initial element or first focusable
    if (initialFocus) {
      const initialElement = container.querySelector(initialFocus) as HTMLElement
      initialElement?.focus()
    } else {
      firstFocusable?.focus()
    }

    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return

      if (e.shiftKey) {
        if (document.activeElement === firstFocusable) {
          e.preventDefault()
          lastFocusable?.focus()
        }
      } else {
        if (document.activeElement === lastFocusable) {
          e.preventDefault()
          firstFocusable?.focus()
        }
      }
    }

    document.addEventListener('keydown', handleTabKey)

    return () => {
      document.removeEventListener('keydown', handleTabKey)
      
      // Return focus to original element
      if (returnFocus) {
        const returnElement = document.querySelector(returnFocus) as HTMLElement
        returnElement?.focus()
      } else if (lastActiveElementRef.current instanceof HTMLElement) {
        lastActiveElementRef.current.focus()
      }
    }
  }, [enabled, initialFocus, returnFocus])

  return (
    <div ref={containerRef}>
      {children}
    </div>
  )
}

// Skip to content link
interface SkipLinkProps {
  /** Target element ID */
  targetId: string
  /** Link text */
  text?: string
  /** Custom CSS classes */
  className?: string
}

export function SkipLink({ 
  targetId, 
  text = "Skip to main content",
  className 
}: SkipLinkProps) {
  return (
    <a
      href={`#${targetId}`}
      className={cn(
        "absolute left-4 top-4 z-50 px-4 py-2 rounded-md",
        "bg-primary text-primary-foreground font-medium",
        "transform -translate-y-16 focus:translate-y-0",
        "transition-transform duration-200",
        "focus:outline-none focus:ring-2 focus:ring-ring",
        className
      )}
    >
      {text}
    </a>
  )
}

// Live region for announcing dynamic content
interface LiveRegionProps {
  /** Content to announce */
  children: React.ReactNode
  /** Announcement priority */
  priority?: 'polite' | 'assertive'
  /** Atomic updates */
  atomic?: boolean
  /** Clear after announcement */
  clearAfter?: number
}

export function LiveRegion({ 
  children, 
  priority = 'polite',
  atomic = false,
  clearAfter 
}: LiveRegionProps) {
  const [content, setContent] = React.useState(children)

  useEffect(() => {
    setContent(children)
    
    if (clearAfter) {
      const timer = setTimeout(() => {
        setContent('')
      }, clearAfter)
      
      return () => clearTimeout(timer)
    }
  }, [children, clearAfter])

  return (
    <div
      aria-live={priority}
      aria-atomic={atomic}
      className="sr-only"
    >
      {content}
    </div>
  )
}

// High contrast mode detection
export function useHighContrast() {
  const [isHighContrast, setIsHighContrast] = React.useState(false)

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-contrast: high)')
    setIsHighContrast(mediaQuery.matches)

    const handleChange = (e: MediaQueryListEvent) => {
      setIsHighContrast(e.matches)
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  return isHighContrast
}

// Reduced motion detection
export function useReducedMotion() {
  const [prefersReducedMotion, setPrefersReducedMotion] = React.useState(false)

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setPrefersReducedMotion(mediaQuery.matches)

    const handleChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches)
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  return prefersReducedMotion
}

// Color contrast safe badge
interface AccessibleBadgeProps {
  children: React.ReactNode
  variant?: 'success' | 'warning' | 'error' | 'info' | 'default'
  /** Force high contrast colors */
  highContrast?: boolean
  className?: string
}

const badgeVariants = {
  default: {
    bg: 'bg-muted',
    text: 'text-muted-foreground',
    icon: null
  },
  success: {
    bg: 'bg-green-100 dark:bg-green-900/20 border-green-200 dark:border-green-800',
    text: 'text-green-800 dark:text-green-200',
    icon: CheckCircle
  },
  warning: {
    bg: 'bg-yellow-100 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800',
    text: 'text-yellow-800 dark:text-yellow-200',
    icon: AlertTriangle
  },
  error: {
    bg: 'bg-red-100 dark:bg-red-900/20 border-red-200 dark:border-red-800',
    text: 'text-red-800 dark:text-red-200',
    icon: XCircle
  },
  info: {
    bg: 'bg-blue-100 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800',
    text: 'text-blue-800 dark:text-blue-200',
    icon: Info
  }
}

export function AccessibleBadge({ 
  children, 
  variant = 'default',
  highContrast = false,
  className 
}: AccessibleBadgeProps) {
  const isHighContrast = useHighContrast()
  const useHighContrastColors = highContrast || isHighContrast
  
  const variantConfig = badgeVariants[variant]
  const Icon = variantConfig.icon

  return (
    <span className={cn(
      "inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium border",
      useHighContrastColors ? 
        `${variantConfig.bg} ${variantConfig.text} border-current` :
        variantConfig.bg + ' ' + variantConfig.text,
      className
    )}>
      {Icon && <Icon className="h-3 w-3" />}
      {children}
    </span>
  )
}

// Keyboard navigation helper
interface KeyboardNavigationProps {
  children: React.ReactNode
  /** Enable arrow key navigation */
  arrowKeys?: boolean
  /** Enable home/end keys */
  homeEnd?: boolean
  /** Wrap around at edges */
  wrap?: boolean
  /** Orientation */
  orientation?: 'horizontal' | 'vertical' | 'both'
  /** Custom CSS classes */
  className?: string
}

export function KeyboardNavigation({ 
  children, 
  arrowKeys = true,
  homeEnd = true,
  wrap = true,
  orientation = 'both',
  className 
}: KeyboardNavigationProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const container = containerRef.current
    if (!container || !arrowKeys) return

    const handleKeyDown = (e: KeyboardEvent) => {
      const focusableElements = container.querySelectorAll(
        '[tabindex]:not([tabindex="-1"]), button:not([disabled]), a[href]'
      ) as NodeListOf<HTMLElement>

      if (focusableElements.length === 0) return

      const currentIndex = Array.from(focusableElements).indexOf(document.activeElement as HTMLElement)
      let nextIndex = currentIndex

      const canMoveVertical = orientation === 'vertical' || orientation === 'both'
      const canMoveHorizontal = orientation === 'horizontal' || orientation === 'both'

      switch (e.key) {
        case 'ArrowDown':
          if (canMoveVertical) {
            e.preventDefault()
            nextIndex = currentIndex + 1
            if (nextIndex >= focusableElements.length && wrap) {
              nextIndex = 0
            }
          }
          break
        case 'ArrowUp':
          if (canMoveVertical) {
            e.preventDefault()
            nextIndex = currentIndex - 1
            if (nextIndex < 0 && wrap) {
              nextIndex = focusableElements.length - 1
            }
          }
          break
        case 'ArrowRight':
          if (canMoveHorizontal) {
            e.preventDefault()
            nextIndex = currentIndex + 1
            if (nextIndex >= focusableElements.length && wrap) {
              nextIndex = 0
            }
          }
          break
        case 'ArrowLeft':
          if (canMoveHorizontal) {
            e.preventDefault()
            nextIndex = currentIndex - 1
            if (nextIndex < 0 && wrap) {
              nextIndex = focusableElements.length - 1
            }
          }
          break
        case 'Home':
          if (homeEnd) {
            e.preventDefault()
            nextIndex = 0
          }
          break
        case 'End':
          if (homeEnd) {
            e.preventDefault()
            nextIndex = focusableElements.length - 1
          }
          break
        default:
          return
      }

      if (nextIndex >= 0 && nextIndex < focusableElements.length && nextIndex !== currentIndex) {
        focusableElements[nextIndex].focus()
      }
    }

    container.addEventListener('keydown', handleKeyDown)
    return () => container.removeEventListener('keydown', handleKeyDown)
  }, [arrowKeys, homeEnd, wrap, orientation])

  return (
    <div ref={containerRef} className={className}>
      {children}
    </div>
  )
}

// Progress indicator with accessibility
interface AccessibleProgressProps {
  /** Current value */
  value: number
  /** Maximum value */
  max?: number
  /** Progress label */
  label?: string
  /** Show percentage */
  showPercentage?: boolean
  /** Custom CSS classes */
  className?: string
}

export function AccessibleProgress({ 
  value, 
  max = 100,
  label,
  showPercentage = false,
  className 
}: AccessibleProgressProps) {
  const percentage = Math.round((value / max) * 100)

  return (
    <div className={cn("space-y-2", className)}>
      {(label || showPercentage) && (
        <div className="flex justify-between text-sm">
          {label && <span>{label}</span>}
          {showPercentage && <span>{percentage}%</span>}
        </div>
      )}
      <div 
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={max}
        aria-label={label}
        className="w-full bg-muted rounded-full h-2"
      >
        <div 
          className="bg-primary h-2 rounded-full transition-all duration-300 ease-in-out"
          style={{ width: `${percentage}%` }}
        />
      </div>
      <ScreenReaderOnly>
        Progress: {value} of {max} ({percentage}%)
      </ScreenReaderOnly>
    </div>
  )
}