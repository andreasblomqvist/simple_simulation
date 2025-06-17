// UI-Specific Types for Enhanced Components
// Complementary types for user interface components and interactions

import type { ReactNode } from 'react';
import type { 
  SimulationYear, 
  OfficeCode, 
  TrendDirection,
  YearOverYearKPI,
  ChartDataPoint 
} from './simulation';

// ========================================
// Theme & Design System Types
// ========================================

export type ColorScheme = 'light' | 'dark' | 'auto';
export type ComponentSize = 'small' | 'medium' | 'large';
export type ElevationLevel = 'none' | 'low' | 'medium' | 'high';
export type SpacingSize = 'xs' | 'small' | 'medium' | 'large' | 'xl';

export interface ThemeConfig {
  colorScheme: ColorScheme;
  primaryColor: string;
  borderRadius: number;
  spacing: {
    xs: number;
    small: number;
    medium: number;
    large: number;
    xl: number;
  };
  shadows: {
    low: string;
    medium: string;
    high: string;
  };
}

// ========================================
// Component State Types
// ========================================

export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface ComponentState<T = any> {
  data: T | null;
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

export interface AsyncState<T = any> extends ComponentState<T> {
  retry: () => Promise<void>;
  refresh: () => Promise<void>;
}

// ========================================
// Interaction & Event Types
// ========================================

export interface ClickableProps {
  onClick?: (event: React.MouseEvent) => void;
  onDoubleClick?: (event: React.MouseEvent) => void;
  disabled?: boolean;
  loading?: boolean;
}

export interface HoverableProps {
  onMouseEnter?: (event: React.MouseEvent) => void;
  onMouseLeave?: (event: React.MouseEvent) => void;
  hoverDelay?: number;
}

export interface FocusableProps {
  onFocus?: (event: React.FocusEvent) => void;
  onBlur?: (event: React.FocusEvent) => void;
  autoFocus?: boolean;
  tabIndex?: number;
}

export interface KeyboardProps {
  onKeyDown?: (event: React.KeyboardEvent) => void;
  onKeyUp?: (event: React.KeyboardEvent) => void;
  shortcuts?: Record<string, () => void>;
}

// ========================================
// Layout & Positioning Types
// ========================================

export type FlexDirection = 'row' | 'column' | 'row-reverse' | 'column-reverse';
export type FlexAlign = 'flex-start' | 'flex-end' | 'center' | 'baseline' | 'stretch';
export type FlexJustify = 'flex-start' | 'flex-end' | 'center' | 'space-between' | 'space-around' | 'space-evenly';

export interface FlexLayoutProps {
  direction?: FlexDirection;
  align?: FlexAlign;
  justify?: FlexJustify;
  wrap?: boolean;
  gap?: SpacingSize;
}

export interface GridLayoutProps {
  columns?: number;
  rows?: number;
  gap?: SpacingSize;
  templateColumns?: string;
  templateRows?: string;
}

export interface ResponsiveLayoutProps {
  mobile?: number | { span?: number; offset?: number };
  tablet?: number | { span?: number; offset?: number };
  desktop?: number | { span?: number; offset?: number };
  largeDesktop?: number | { span?: number; offset?: number };
}

// ========================================
// Animation & Transition Types
// ========================================

export type AnimationType = 'fade' | 'slide' | 'scale' | 'bounce' | 'flip';
export type AnimationDirection = 'up' | 'down' | 'left' | 'right' | 'in' | 'out';

export interface AnimationConfig {
  type: AnimationType;
  direction?: AnimationDirection;
  duration?: number;
  delay?: number;
  easing?: string;
}

export interface TransitionProps {
  enter?: AnimationConfig;
  exit?: AnimationConfig;
  appear?: boolean;
  mountOnEnter?: boolean;
  unmountOnExit?: boolean;
}

// ========================================
// Data Visualization UI Types
// ========================================

export interface ChartUIConfig {
  showLegend?: boolean;
  showGrid?: boolean;
  showTooltip?: boolean;
  showAxes?: boolean;
  interactive?: boolean;
  responsive?: boolean;
  theme?: 'light' | 'dark';
  height?: number;
  width?: number;
}

export interface TooltipConfig {
  show?: boolean;
  format?: (value: any, context: any) => ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right' | 'auto';
  delay?: number;
  className?: string;
}

export interface LegendConfig {
  show?: boolean;
  position?: 'top' | 'bottom' | 'left' | 'right';
  align?: 'start' | 'center' | 'end';
  itemSpacing?: number;
  maxHeight?: number;
}

// ========================================
// KPI Card Specific UI Types
// ========================================

export interface KPIDisplayConfig {
  showValue?: boolean;
  showTrend?: boolean;
  showSparkline?: boolean;
  showTarget?: boolean;
  showBaseline?: boolean;
  showTooltip?: boolean;
  compactMode?: boolean;
}

export interface TrendIndicatorConfig {
  showIcon?: boolean;
  showPercentage?: boolean;
  showAbsolute?: boolean;
  colorCoded?: boolean;
  iconPosition?: 'left' | 'right' | 'top' | 'bottom';
}

export interface SparklineConfig extends ChartUIConfig {
  showPoints?: boolean;
  showArea?: boolean;
  highlightPeaks?: boolean;
  highlightCurrent?: boolean;
  smoothing?: boolean;
}

// ========================================
// Form & Input UI Types
// ========================================

export type InputVariant = 'default' | 'filled' | 'outlined' | 'borderless';
export type InputStatus = 'default' | 'error' | 'warning' | 'success';

export interface InputUIProps {
  variant?: InputVariant;
  status?: InputStatus;
  size?: ComponentSize;
  prefix?: ReactNode;
  suffix?: ReactNode;
  placeholder?: string;
  helpText?: string;
  errorText?: string;
  showCount?: boolean;
  allowClear?: boolean;
}

export interface SelectUIProps extends InputUIProps {
  searchable?: boolean;
  multiSelect?: boolean;
  showArrow?: boolean;
  showSearch?: boolean;
  optionHeight?: number;
  dropdownHeight?: number;
  loading?: boolean;
}

// ========================================
// Navigation & Routing UI Types
// ========================================

export interface BreadcrumbItem {
  title: ReactNode;
  href?: string;
  onClick?: () => void;
  icon?: ReactNode;
  disabled?: boolean;
}

export interface TabItem {
  key: string;
  label: ReactNode;
  icon?: ReactNode;
  disabled?: boolean;
  closable?: boolean;
  content?: ReactNode;
}

export interface MenuItemConfig {
  key: string;
  label: ReactNode;
  icon?: ReactNode;
  disabled?: boolean;
  danger?: boolean;
  children?: MenuItemConfig[];
  onClick?: () => void;
}

// ========================================
// Modal & Overlay UI Types
// ========================================

export interface ModalConfig {
  title?: ReactNode;
  content?: ReactNode;
  footer?: ReactNode;
  width?: number;
  height?: number;
  closable?: boolean;
  maskClosable?: boolean;
  keyboard?: boolean;
  centered?: boolean;
  destroyOnClose?: boolean;
  zIndex?: number;
}

export interface DrawerConfig {
  title?: ReactNode;
  placement?: 'top' | 'right' | 'bottom' | 'left';
  width?: number | string;
  height?: number | string;
  level?: number;
  push?: boolean;
  keyboard?: boolean;
  maskClosable?: boolean;
}

export interface PopoverConfig {
  content?: ReactNode;
  title?: ReactNode;
  trigger?: 'hover' | 'click' | 'focus' | 'contextMenu';
  placement?: 'top' | 'bottom' | 'left' | 'right' | 'topLeft' | 'topRight' | 'bottomLeft' | 'bottomRight';
  arrow?: boolean;
  autoAdjustOverflow?: boolean;
}

// ========================================
// Table UI Configuration Types
// ========================================

export interface TableUIConfig {
  bordered?: boolean;
  striped?: boolean;
  hoverable?: boolean;
  compact?: boolean;
  loading?: boolean;
  scrollable?: boolean;
  stickyHeader?: boolean;
  showHeader?: boolean;
  showPagination?: boolean;
  pageSize?: number;
  pageSizeOptions?: number[];
}

export interface ColumnUIConfig {
  width?: number | string;
  minWidth?: number;
  maxWidth?: number;
  fixed?: 'left' | 'right';
  resizable?: boolean;
  sortable?: boolean;
  filterable?: boolean;
  searchable?: boolean;
  align?: 'left' | 'center' | 'right';
  ellipsis?: boolean;
}

// ========================================
// Accessibility Types
// ========================================

export interface AccessibilityProps {
  'aria-label'?: string;
  'aria-labelledby'?: string;
  'aria-describedby'?: string;
  'aria-expanded'?: boolean;
  'aria-hidden'?: boolean;
  'aria-disabled'?: boolean;
  'aria-selected'?: boolean;
  'aria-current'?: boolean | 'page' | 'step' | 'location' | 'date' | 'time';
  role?: string;
}

export interface KeyboardNavigationConfig {
  focusable?: boolean;
  tabIndex?: number;
  arrowKeyNavigation?: boolean;
  enterKeyActivation?: boolean;
  escapeKeyClose?: boolean;
  homeEndNavigation?: boolean;
}

// ========================================
// Performance & Optimization Types
// ========================================

export interface VirtualizationConfig {
  enabled?: boolean;
  itemHeight?: number;
  bufferSize?: number;
  threshold?: number;
  scrollThreshold?: number;
}

export interface LazyLoadingConfig {
  enabled?: boolean;
  threshold?: number;
  rootMargin?: string;
  placeholder?: ReactNode;
  fallback?: ReactNode;
}

export interface CacheConfig {
  enabled?: boolean;
  ttl?: number; // time to live in milliseconds
  maxSize?: number;
  strategy?: 'lru' | 'fifo' | 'lfu';
}

// ========================================
// Error Handling UI Types
// ========================================

export interface ErrorBoundaryConfig {
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: any) => void;
  retry?: boolean;
  retryText?: string;
  level?: 'component' | 'page' | 'application';
}

export interface ErrorDisplayConfig {
  showStack?: boolean;
  showDetails?: boolean;
  allowRetry?: boolean;
  allowReport?: boolean;
  level?: 'info' | 'warning' | 'error' | 'critical';
}

// ========================================
// Utility UI Types
// ========================================

export type ClassNameProp = string | string[] | Record<string, boolean>;

export interface StyleProps {
  className?: ClassNameProp;
  style?: React.CSSProperties;
}

export interface TestProps {
  'data-testid'?: string;
  'data-test'?: string;
}

export interface CommonUIProps extends StyleProps, TestProps, AccessibilityProps {
  id?: string;
  children?: ReactNode;
}

// ========================================
// Component Composition Types
// ========================================

export interface WithTooltipProps {
  tooltip?: string | TooltipConfig;
}

export interface WithLoadingProps {
  loading?: boolean;
  loadingText?: string;
  loadingIcon?: ReactNode;
}

export interface WithErrorProps {
  error?: string | null;
  showError?: boolean;
  errorDisplay?: ErrorDisplayConfig;
}

export interface EnhancedComponentProps extends 
  CommonUIProps, 
  WithTooltipProps, 
  WithLoadingProps, 
  WithErrorProps {}

// ========================================
// Export Utility Types
// ========================================

export type UIComponent<P = {}> = React.FC<P & EnhancedComponentProps>;

export type StyledComponent<P = {}> = React.FC<P & StyleProps>;

export type InteractiveComponent<P = {}> = React.FC<P & ClickableProps & HoverableProps>;

export type FormComponent<T = any> = React.FC<{
  value?: T;
  onChange?: (value: T) => void;
  onBlur?: () => void;
} & InputUIProps>;

export type ChartComponent<T = ChartDataPoint[]> = React.FC<{
  data: T;
  config?: ChartUIConfig;
} & CommonUIProps>; 