import React from 'react'
import { cn } from '../../lib/utils'

// Helper components for common table cell types with enhanced readability

interface NumericCellProps {
  value: number
  decimals?: number
  className?: string
}

export const NumericCell: React.FC<NumericCellProps> = ({ 
  value, 
  decimals = 0, 
  className 
}) => (
  <span className={cn("font-mono text-base font-bold tabular-nums", className)}>
    {value.toLocaleString('en-US', { maximumFractionDigits: decimals })}
  </span>
)

interface CurrencyCellProps {
  value: number
  currency?: string
  className?: string
}

export const CurrencyCell: React.FC<CurrencyCellProps> = ({ 
  value, 
  currency = 'SEK',
  className 
}) => (
  <span className={cn("font-mono text-base font-bold tabular-nums", className)}>
    {value.toLocaleString('en-US', { 
      style: 'currency', 
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    })}
  </span>
)

interface PercentageCellProps {
  value: number
  decimals?: number
  className?: string
}

export const PercentageCell: React.FC<PercentageCellProps> = ({ 
  value, 
  decimals = 1,
  className 
}) => (
  <span className={cn("font-mono text-base font-bold tabular-nums", className)}>
    {(value * 100).toFixed(decimals)}%
  </span>
)

interface KPICellProps {
  value: number
  decimals?: number
  className?: string
}

export const KPICell: React.FC<KPICellProps> = ({ 
  value, 
  decimals = 0,
  className 
}) => (
  <span className={cn("font-mono text-lg font-bold tabular-nums", className)}>
    {value.toLocaleString('en-US', { maximumFractionDigits: decimals })}
  </span>
)

// Utility function to create numeric column definitions
export const createNumericColumn = (
  accessorKey: string,
  header: string,
  options: {
    decimals?: number
    type?: 'number' | 'currency' | 'percentage' | 'kpi'
    currency?: string
    className?: string
  } = {}
) => ({
  accessorKey,
  header,
  cell: ({ row }: any) => {
    const value = row.getValue(accessorKey) as number
    
    switch (options.type) {
      case 'currency':
        return <CurrencyCell value={value} currency={options.currency} className={options.className} />
      case 'percentage':
        return <PercentageCell value={value} decimals={options.decimals} className={options.className} />
      case 'kpi':
        return <KPICell value={value} decimals={options.decimals} className={options.className} />
      default:
        return <NumericCell value={value} decimals={options.decimals} className={options.className} />
    }
  },
})

// Text cell with enhanced readability
interface TextCellProps {
  children: React.ReactNode
  size?: 'sm' | 'base' | 'lg'
  weight?: 'normal' | 'medium' | 'semibold' | 'bold'
  className?: string
}

export const TextCell: React.FC<TextCellProps> = ({ 
  children, 
  size = 'base',
  weight = 'medium',
  className 
}) => {
  const sizeClasses = {
    sm: 'text-sm',
    base: 'text-base',
    lg: 'text-lg'
  }
  
  const weightClasses = {
    normal: 'font-normal',
    medium: 'font-medium',
    semibold: 'font-semibold',
    bold: 'font-bold'
  }
  
  return (
    <span className={cn(sizeClasses[size], weightClasses[weight], className)}>
      {children}
    </span>
  )
}