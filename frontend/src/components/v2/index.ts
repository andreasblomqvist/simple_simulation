// V2 Components - Enhanced UI with Year-by-Year Navigation
// 
// This directory contains the next generation of simulation components
// designed with improved UX, year navigation, and reduced visual clutter.

// Base Layout Components
export { default as BaseCard } from './BaseCard';
export { 
  CollapsibleSection
} from './CollapsibleSection';

// Core Navigation & State
export { YearNavigationProvider, useYearNavigation } from './YearNavigationProvider';
export { default as YearSelector } from './YearSelector';

// Enhanced UI Components
export { default as EnhancedKPICard } from './EnhancedKPICard';
export { default as SimulationLeversCard } from './SimulationLeversCard';
export { default as SimulationScopePanel } from './SimulationScopePanel';
export { default as EconomicParametersPanel } from './EconomicParametersPanel';
export { PyramidChart, exampleCareerJourneyData } from './PyramidChart';
export { QuarterlyWorkforceChart, exampleQuarterlyData } from './QuarterlyWorkforceChart';

// Multi-Year Charts & Visualization (Task 7.0)
// Note: Chart components will be exported once implementation is complete
// export { default as MultiYearTrendChart } from './MultiYearTrendChart';
// export { default as YearOverYearComparisonChart } from './YearOverYearComparisonChart';

// Enhanced Data Table (Task 8.0)
// TODO: Implement EnhancedDataTable and VirtualizedDataTable
// export { default as EnhancedDataTable } from './EnhancedDataTable';
// export { default as VirtualizedDataTable } from './VirtualizedDataTable';

// Chart Utilities and Interactive Components
export {
  InteractiveAnnotation,
  CustomChartTooltip,
  createYearHighlight,
  exportChartData,
  getResponsiveChartDimensions,
  createChartAnimation
} from './ChartUtilities';

// Chart-related Type Exports
export type {
  // Chart Utilities Types
  ChartAnnotation,
  TooltipData,
  TooltipItem,
  YearHighlight
} from './ChartUtilities';

// Enhanced Data Table Type Exports
// TODO: Add types when EnhancedDataTable is implemented
// export type {
//   TableDataRow,
//   TableFilterState,
//   TableViewSettings
// } from './EnhancedDataTable';

// Demo & Testing
export { default as YearNavigationDemo } from './YearNavigationDemo';
// TODO: Implement LayoutDemo
// export { default as LayoutDemo } from './LayoutDemo';

// Component Types (for external consumption)
export type { default as YearNavigationProviderProps } from './YearNavigationProvider';

// TypeScript Types & Interfaces
export type * from '../../types/simulation';
export type * from '../../types/ui';

// Custom Hooks
export * from '../../hooks/simulation';
export * from '../../hooks/yearNavigation';

// TODO: Add these components as they are implemented
// export { default as MultiYearTrendChart } from './MultiYearTrendChart';
// export { default as YearOverYearComparisonChart } from './YearOverYearComparisonChart';
// export { default as EnhancedDataTable } from './EnhancedDataTable'; 

// CSS imports for chart responsiveness
import './ResponsiveCharts.css';

/**
 * Multi-Year Charts Module
 * 
 * This module provides comprehensive multi-year data visualization components
 * designed for the Simple Simulation project. It includes:
 * 
 * 1. MultiYearTrendChart - Interactive trend visualization across multiple years
 * 2. YearOverYearComparisonChart - Side-by-side year comparisons
 * 3. Interactive annotations with customizable tooltips
 * 4. Responsive design for mobile, tablet, and desktop
 * 5. Export functionality for chart data
 * 6. Accessibility compliance (WCAG AA)
 * 
 * Key Features:
 * - Native React/SVG implementation (no external charting dependencies)
 * - Full TypeScript support with comprehensive type definitions
 * - Integration with YearNavigationProvider for consistent year management
 * - Professional styling with Ant Design components
 * - Dark mode and high contrast support
 * - Touch-friendly mobile interface
 * - Animation and transition effects
 * - Print optimization
 * 
 * Usage Example:
 * ```tsx
 * import { MultiYearTrendChart, YearOverYearComparisonChart } from '@/components/v2';
 * 
 * const trendData = {
 *   title: "Revenue Growth Trend",
 *   data: [
 *     { year: 2022, value: 100, isProjected: false },
 *     { year: 2023, value: 120, isProjected: false },
 *     { year: 2024, value: 150, isProjected: true }
 *   ],
 *   yAxisLabel: "Revenue",
 *   unit: "M SEK"
 * };
 * 
 * <MultiYearTrendChart data={trendData} />
 * ```
 */ 