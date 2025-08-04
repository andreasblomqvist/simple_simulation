import React from 'react'
import { cn } from '../../lib/utils'

// Base loading spinner
interface LoadingSpinnerProps {
  /** Size of the spinner */
  size?: 'sm' | 'md' | 'lg' | 'xl'
  /** Loading text */
  text?: string
  /** Show in center of container */
  centered?: boolean
  /** Custom CSS classes */
  className?: string
}

const sizeClasses = {
  sm: 'h-4 w-4',
  md: 'h-6 w-6', 
  lg: 'h-8 w-8',
  xl: 'h-12 w-12'
}

export function LoadingSpinner({ 
  size = 'md', 
  text, 
  centered = false, 
  className 
}: LoadingSpinnerProps) {
  const spinner = (
    <div className={cn("flex items-center gap-3", centered && "justify-center", className)}>
      <div className={cn(
        "animate-spin rounded-full border-2 border-muted border-t-primary",
        sizeClasses[size]
      )} />
      {text && (
        <span className="text-sm text-muted-foreground animate-pulse">
          {text}
        </span>
      )}
    </div>
  )

  if (centered) {
    return (
      <div className="flex items-center justify-center min-h-[200px]">
        {spinner}
      </div>
    )
  }

  return spinner
}

// Skeleton loading components
interface SkeletonProps {
  className?: string
  /** Rounded skeleton */
  rounded?: boolean
  /** Animate */
  animate?: boolean
}

export function Skeleton({ className, rounded = false, animate = true }: SkeletonProps) {
  return (
    <div 
      className={cn(
        "bg-muted",
        animate && "animate-pulse",
        rounded ? "rounded-full" : "rounded",
        className
      )}
    />
  )
}

// Card skeleton
export function CardSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn("rounded-lg border bg-card p-6 space-y-3", className)}>
      <Skeleton className="h-4 w-3/4" />
      <Skeleton className="h-10 w-full" />
      <div className="space-y-2">
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-5/6" />
        <Skeleton className="h-3 w-4/6" />
      </div>
    </div>
  )
}

// Table skeleton
export function TableSkeleton({ 
  rows = 5, 
  cols = 4,
  className 
}: { 
  rows?: number
  cols?: number
  className?: string 
}) {
  return (
    <div className={cn("space-y-3", className)}>
      {/* Header */}
      <div className="flex space-x-4">
        {Array.from({ length: cols }).map((_, i) => (
          <Skeleton key={i} className="h-4 flex-1" />
        ))}
      </div>
      
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="flex space-x-4">
          {Array.from({ length: cols }).map((_, colIndex) => (
            <Skeleton 
              key={colIndex} 
              className="h-8 flex-1" 
              style={{ width: `${Math.random() * 40 + 60}%` }}
            />
          ))}
        </div>
      ))}
    </div>
  )
}

// KPI card skeleton
export function KPICardSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn("rounded-lg border bg-card p-6 space-y-4", className)}>
      <div className="flex items-center justify-between">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-4 w-4 rounded-full" />
      </div>
      <div className="space-y-2">
        <Skeleton className="h-8 w-32" />
        <Skeleton className="h-3 w-16" />
      </div>
      <div className="space-y-2">
        <div className="flex justify-between">
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-3 w-12" />
        </div>
        <Skeleton className="h-1 w-full" />
      </div>
    </div>
  )
}

// Chart skeleton
export function ChartSkeleton({ 
  height = 300,
  className 
}: { 
  height?: number
  className?: string 
}) {
  return (
    <div className={cn("rounded-lg border bg-card", className)}>
      <div className="flex items-center justify-between p-4 border-b">
        <div className="space-y-2">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-3 w-32" />
        </div>
        <Skeleton className="h-6 w-6 rounded" />
      </div>
      <div className="p-4">
        <div className="flex items-end justify-center space-x-2" style={{ height }}>
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton 
              key={i} 
              className="w-8" 
              style={{ height: `${Math.random() * 80 + 20}%` }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

// Progressive loading component
interface ProgressiveLoadingProps {
  /** Loading states in order */
  states: {
    text: string
    duration?: number
  }[]
  /** Current state index */
  currentState: number
  /** Custom CSS classes */
  className?: string
}

export function ProgressiveLoading({ 
  states, 
  currentState, 
  className 
}: ProgressiveLoadingProps) {
  const progress = ((currentState + 1) / states.length) * 100

  return (
    <div className={cn("space-y-4", className)}>
      <div className="flex items-center gap-3">
        <LoadingSpinner size="sm" />
        <span className="text-sm font-medium">
          {states[currentState]?.text || 'Loading...'}
        </span>
      </div>
      
      <div className="space-y-2">
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>Step {currentState + 1} of {states.length}</span>
          <span>{Math.round(progress)}%</span>
        </div>
        <div className="w-full bg-muted rounded-full h-2">
          <div 
            className="bg-primary h-2 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
      
      <div className="space-y-1">
        {states.map((state, index) => (
          <div 
            key={index}
            className={cn(
              "flex items-center gap-2 text-xs",
              index < currentState ? "text-green-600" : 
              index === currentState ? "text-primary" : 
              "text-muted-foreground"
            )}
          >
            <div className={cn(
              "h-2 w-2 rounded-full",
              index < currentState ? "bg-green-600" :
              index === currentState ? "bg-primary animate-pulse" :
              "bg-muted"
            )} />
            <span>{state.text}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

// Page transition wrapper
interface PageTransitionProps {
  children: React.ReactNode
  /** Animation type */
  type?: 'fade' | 'slide' | 'scale'
  /** Animation duration */
  duration?: number
  /** Custom CSS classes */
  className?: string
}

export function PageTransition({ 
  children, 
  type = 'fade',
  duration = 300,
  className 
}: PageTransitionProps) {
  const animationClasses = {
    fade: 'animate-in fade-in',
    slide: 'animate-in slide-in-from-right',
    scale: 'animate-in zoom-in-95'
  }

  return (
    <div 
      className={cn(
        animationClasses[type],
        className
      )}
      style={{ 
        animationDuration: `${duration}ms`,
        animationFillMode: 'both'
      }}
    >
      {children}
    </div>
  )
}

// Stagger animation for lists
interface StaggerContainerProps {
  children: React.ReactNode
  /** Stagger delay between items (ms) */
  staggerDelay?: number
  /** Custom CSS classes */
  className?: string
}

export function StaggerContainer({ 
  children, 
  staggerDelay = 50,
  className 
}: StaggerContainerProps) {
  return (
    <div className={className}>
      {React.Children.map(children, (child, index) => (
        <div
          className="animate-in fade-in slide-in-from-bottom-2"
          style={{
            animationDelay: `${index * staggerDelay}ms`,
            animationFillMode: 'both'
          }}
        >
          {child}
        </div>
      ))}
    </div>
  )
}

// Loading overlay
interface LoadingOverlayProps {
  /** Show overlay */
  visible: boolean
  /** Loading text */
  text?: string
  /** Blur background */
  blur?: boolean
  /** Custom CSS classes */
  className?: string
}

export function LoadingOverlay({ 
  visible, 
  text = "Loading...",
  blur = true,
  className 
}: LoadingOverlayProps) {
  if (!visible) return null

  return (
    <div className={cn(
      "fixed inset-0 z-50 flex items-center justify-center bg-background/80",
      blur && "backdrop-blur-sm",
      "animate-in fade-in",
      className
    )}>
      <div className="flex flex-col items-center gap-4 p-8 rounded-lg bg-card border shadow-lg">
        <LoadingSpinner size="lg" />
        <p className="text-sm font-medium">{text}</p>
      </div>
    </div>
  )
}