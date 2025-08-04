import * as React from "react"
import { Search, X } from "lucide-react"
import { Input, type InputProps } from "./input"
import { cn } from "../../lib/utils"

export interface SearchInputProps extends Omit<InputProps, 'type' | 'leftIcon' | 'rightIcon'> {
  // Search functionality
  onSearch?: (value: string) => void
  onClear?: () => void
  
  // Debounce delay for search (ms)
  debounceDelay?: number
  
  // Show clear button when there's content
  showClearButton?: boolean
  
  // Custom icons
  searchIcon?: React.ReactNode
  clearIcon?: React.ReactNode
  
  // Accessibility labels
  clearLabel?: string
  searchLabel?: string
}

const SearchInput = React.forwardRef<HTMLInputElement, SearchInputProps>(
  ({ 
    onSearch,
    onClear,
    debounceDelay = 300,
    showClearButton = true,
    searchIcon,
    clearIcon,
    clearLabel = "Clear search",
    searchLabel = "Search",
    placeholder = "Search...",
    value,
    defaultValue,
    onValueChange,
    onChange,
    className,
    ...props 
  }, ref) => {
    const [internalValue, setInternalValue] = React.useState(
      (value !== undefined ? value : defaultValue || "") as string
    )
    const searchTimeoutRef = React.useRef<NodeJS.Timeout>()
    
    // Use controlled value if provided, otherwise use internal state
    const currentValue = value !== undefined ? value : internalValue
    const hasValue = Boolean(currentValue && String(currentValue).length > 0)
    
    // Debounced search effect
    React.useEffect(() => {
      if (onSearch && debounceDelay > 0) {
        if (searchTimeoutRef.current) {
          clearTimeout(searchTimeoutRef.current)
        }
        
        searchTimeoutRef.current = setTimeout(() => {
          onSearch(currentValue as string)
        }, debounceDelay)
        
        return () => {
          if (searchTimeoutRef.current) {
            clearTimeout(searchTimeoutRef.current)
          }
        }
      } else if (onSearch) {
        onSearch(currentValue as string)
      }
    }, [currentValue, onSearch, debounceDelay])
    
    const handleValueChange = (newValue: string) => {
      if (value === undefined) {
        setInternalValue(newValue)
      }
      onValueChange?.(newValue)
    }
    
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = e.target.value
      handleValueChange(newValue)
      onChange?.(e)
    }
    
    const handleClear = () => {
      const newValue = ""
      handleValueChange(newValue)
      onClear?.()
      
      // Focus the input after clearing
      if (ref && typeof ref === 'object' && ref.current) {
        ref.current.focus()
      }
    }
    
    const ClearButton = ({ onClick, 'aria-label': ariaLabel }: {
      onClick: () => void
      'aria-label': string
    }) => (
      <button
        type="button"
        onClick={onClick}
        aria-label={ariaLabel}
        className={cn(
          "flex items-center justify-center transition-colors",
          "hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1 rounded-sm",
          "disabled:pointer-events-none disabled:opacity-50"
        )}
        tabIndex={0}
      >
        {clearIcon || <X className="h-4 w-4" />}
      </button>
    )
    
    return (
      <Input
        {...props}
        ref={ref}
        type="search"
        value={currentValue}
        onChange={handleChange}
        placeholder={placeholder}
        className={className}
        aria-label={searchLabel}
        leftIcon={searchIcon || <Search className="h-4 w-4" />}
        rightIcon={
          showClearButton && hasValue ? (
            <ClearButton
              onClick={handleClear}
              aria-label={clearLabel}
            />
          ) : undefined
        }
      />
    )
  }
)
SearchInput.displayName = "SearchInput"

export { SearchInput }