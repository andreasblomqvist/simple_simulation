/**
 * SimpleSim Design Tokens (TypeScript)
 * Complete design token implementation for clean, consistent UI
 * Synchronized with unified design-tokens.css
 * Based on design-tokens.md specification
 */

// Colors - Complete system with semantic colors
export const colors = {
  // Base colors
  white: '#ffffff',
  black: '#000000',
  
  // Primary brand colors (Blue)
  primary: {
    50: '#eff6ff',
    100: '#dbeafe',
    200: '#bfdbfe',
    300: '#93c5fd',
    400: '#60a5fa',  
    500: '#3b82f6',
    600: '#2563eb',
    700: '#1d4ed8',
    800: '#1e40af',
    900: '#1e3a8a',
    950: '#172554',
    DEFAULT: '#3b82f6',
  },
  
  // Neutral grays
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
    950: '#030712',
  },
  
  // Semantic colors
  success: {
    50: '#f0fdf4',
    500: '#22c55e',
    600: '#16a34a',
    700: '#15803d',
    900: '#14532d',
    DEFAULT: '#22c55e',
  },
  
  warning: {
    50: '#fffbeb',
    500: '#f59e0b',
    600: '#d97706',
    700: '#b45309',
    900: '#78350f',
    DEFAULT: '#f59e0b',
  },
  
  error: {
    50: '#fef2f2',
    500: '#ef4444',
    600: '#dc2626',
    700: '#b91c1c',
    900: '#7f1d1d',
    DEFAULT: '#ef4444',
  },

  info: {
    50: '#f0f9ff',
    500: '#06b6d4',
    600: '#0891b2',
    900: '#164e63',
    DEFAULT: '#06b6d4',
  },

  // Legacy destructive alias for backward compatibility
  destructive: {
    50: '#fef2f2',
    100: '#fee2e2',
    500: '#ef4444',
    DEFAULT: '#ef4444',
  },

  // Dark mode colors
  dark: {
    background: '#0f172a',
    surface: '#1e293b',
    border: '#334155',
    text: {
      primary: '#f1f5f9',
      secondary: '#cbd5e1',
      muted: '#64748b'
    }
  }
} as const

// Typography - Complete system with semantic scales
export const typography = {
  fontFamily: {
    sans: [
      'Inter', 
      '-apple-system', 
      'BlinkMacSystemFont', 
      'Segoe UI', 
      'Roboto', 
      'sans-serif'
    ],
    mono: [
      'JetBrains Mono',
      'SF Mono', 
      'Monaco', 
      'Consolas', 
      'monospace'
    ],
  },
  
  // Display text (page titles, hero content)
  display: {
    xl: { size: '48px', weight: 700, lineHeight: 1.1, letterSpacing: '-0.02em' },
    lg: { size: '36px', weight: 600, lineHeight: 1.2, letterSpacing: '-0.02em' },
    md: { size: '30px', weight: 600, lineHeight: 1.2, letterSpacing: '-0.01em' },
    sm: { size: '24px', weight: 600, lineHeight: 1.3, letterSpacing: '-0.01em' }
  },

  // Heading text (section titles, card headers)
  heading: {
    xl: { size: '20px', weight: 600, lineHeight: 1.3 },
    lg: { size: '18px', weight: 600, lineHeight: 1.4 },
    md: { size: '16px', weight: 600, lineHeight: 1.4 },
    sm: { size: '14px', weight: 600, lineHeight: 1.4 }
  },

  // Body text (content, descriptions)
  body: {
    lg: { size: '16px', weight: 400, lineHeight: 1.6 },
    md: { size: '14px', weight: 400, lineHeight: 1.5 },
    sm: { size: '12px', weight: 400, lineHeight: 1.5 }
  },

  // Label text (form labels, table headers)
  label: {
    lg: { size: '14px', weight: 500, lineHeight: 1.4 },
    md: { size: '12px', weight: 500, lineHeight: 1.4 },
    sm: { size: '11px', weight: 500, lineHeight: 1.4 }
  },

  // Caption text (help text, metadata)
  caption: {
    lg: { size: '12px', weight: 400, lineHeight: 1.4 },
    md: { size: '11px', weight: 400, lineHeight: 1.4 },
    sm: { size: '10px', weight: 400, lineHeight: 1.4 }
  },
  
  // Legacy fontSize for backward compatibility
  fontSize: {
    xs: ['0.75rem', { lineHeight: '1rem' }],
    sm: ['0.875rem', { lineHeight: '1.25rem' }],
    base: ['1rem', { lineHeight: '1.5rem' }],
    lg: ['1.125rem', { lineHeight: '1.75rem' }],
    xl: ['1.25rem', { lineHeight: '1.75rem' }],
    '2xl': ['1.5rem', { lineHeight: '2rem' }],
    '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
    '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
  },
  
  fontWeight: {
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
  },

  lineHeight: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75,
  }
} as const

// Spacing - 4px base scale as per specification
export const spacing = {
  0: '0px',
  1: '4px',    // xs - tight spacing
  2: '8px',    // sm - compact spacing  
  3: '12px',   // md - standard spacing
  4: '16px',   // lg - comfortable spacing
  5: '20px',   // xl - loose spacing
  6: '24px',   // 2xl - section spacing
  8: '32px',   // 3xl - large section spacing
  10: '40px',  // 4xl - page section spacing
  12: '48px',  // 5xl - major page spacing
  16: '64px',  // 6xl - hero spacing
  20: '80px',  // 7xl - maximum spacing
  24: '96px'   // 8xl - page margins
} as const

// Legacy spacing aliases (rem-based)
export const space = {
  0: '0',
  1: '0.25rem', // 4px
  2: '0.5rem',  // 8px
  3: '0.75rem', // 12px
  4: '1rem',    // 16px
  5: '1.25rem', // 20px
  6: '1.5rem',  // 24px
  8: '2rem',    // 32px
  10: '2.5rem', // 40px
  12: '3rem',   // 48px
  16: '4rem',   // 64px
  20: '5rem',   // 80px
  24: '6rem',   // 96px
} as const

// Semantic spacing aliases
export const layout = {
  containerPadding: spacing[4],     // 16px
  sectionGap: spacing[8],           // 32px
  cardPadding: spacing[6],          // 24px
  buttonPadding: spacing[3],        // 12px
  inputPadding: spacing[3],         // 12px
  tableCell: spacing[3],            // 12px
  listItem: spacing[4]              // 16px
} as const

// Border radius - Updated to match specification
export const borderRadius = {
  none: '0px',
  sm: '4px',    // Small elements (tags, badges)
  md: '8px',    // Standard elements (buttons, inputs)
  lg: '12px',   // Cards, panels
  xl: '16px',   // Large containers
  '2xl': '20px', // Very large containers
  full: '9999px', // Pills, avatars
  
  // Legacy aliases for backward compatibility
  DEFAULT: '8px',
  base: '4px',
} as const

// Shadows & Elevation - Complete system with dark mode support
export const shadows = {
  // Subtle shadows for cards and modals
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  
  // Focus states
  focus: '0 0 0 3px rgb(59 130 246 / 0.1)',
  
  // Dark mode shadows
  dark: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.3)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.4), 0 2px 4px -2px rgb(0 0 0 / 0.3)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.4), 0 4px 6px -4px rgb(0 0 0 / 0.3)'
  },
  
  none: '0 0 #0000',
  // Legacy aliases
  DEFAULT: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  base: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
} as const

// Legacy boxShadow alias for backward compatibility
export const boxShadow = {
  ...shadows,
} as const

// Component-Specific Tokens
export const button = {
  primary: {
    background: colors.primary[500],
    backgroundHover: colors.primary[600],
    backgroundPressed: colors.primary[700],
    text: '#ffffff',
    border: colors.primary[500]
  },
  
  secondary: {
    background: 'transparent',
    backgroundHover: colors.gray[100],
    backgroundPressed: colors.gray[200],
    text: colors.gray[700],
    border: colors.gray[300]
  },
  
  ghost: {
    background: 'transparent',
    backgroundHover: colors.gray[100],
    backgroundPressed: colors.gray[200],
    text: colors.gray[700],
    border: 'transparent'
  },
  
  destructive: {
    background: colors.error[500],
    backgroundHover: colors.error[600],
    backgroundPressed: colors.error[700],
    text: '#ffffff',
    border: colors.error[500]
  }
} as const

export const form = {
  input: {
    background: '#ffffff',
    border: colors.gray[300],
    borderHover: colors.gray[400],
    borderFocus: colors.primary[500],
    text: colors.gray[900],
    placeholder: colors.gray[400],
    shadow: shadows.sm,
    shadowFocus: shadows.focus
  },
  
  label: {
    text: colors.gray[700],
    required: colors.error[500]
  },
  
  help: {
    text: colors.gray[500]
  },
  
  error: {
    text: colors.error[600],
    border: colors.error[300],
    background: colors.error[50]
  }
} as const

export const table = {
  header: {
    background: colors.gray[50],
    text: colors.gray[700],
    border: colors.gray[200]
  },
  
  row: {
    background: '#ffffff',
    backgroundHover: colors.gray[50],
    backgroundSelected: colors.primary[50],
    border: colors.gray[200],
    text: colors.gray[900]
  },
  
  cell: {
    padding: spacing[3]
  }
} as const

// Animation & Timing
export const timing = {
  fast: '150ms',      // Quick interactions (hover, focus)
  normal: '200ms',    // Standard transitions
  slow: '300ms',      // Complex animations
  slower: '500ms'     // Page transitions
} as const

// Legacy aliases
export const duration = {
  fast: timing.fast,
  normal: timing.normal,
  slow: timing.slow,
} as const

export const easing = {
  default: 'cubic-bezier(0.4, 0, 0.2, 1)',     // Smooth standard
  in: 'cubic-bezier(0.4, 0, 1, 1)',            // Accelerating
  out: 'cubic-bezier(0, 0, 0.2, 1)',           // Decelerating  
  inOut: 'cubic-bezier(0.4, 0, 0.2, 1)'        // Smooth in-out
} as const

export const motion = {
  // Hover states - quick and responsive
  hover: {
    duration: timing.fast,
    easing: easing.out
  },
  
  // Focus states - immediate feedback
  focus: {
    duration: timing.fast,
    easing: easing.default
  },
  
  // Loading states - smooth and continuous
  loading: {
    duration: timing.slow,
    easing: easing.inOut
  },
  
  // Page transitions - smooth and purposeful
  page: {
    duration: timing.slower,
    easing: easing.inOut
  }
} as const

// Accessibility Tokens
export const focus = {
  ring: {
    width: '2px',
    color: colors.primary[500],
    style: 'solid',
    offset: '2px'
  },
  
  // High contrast mode
  highContrast: {
    width: '3px',
    color: '#000000',
    style: 'solid'
  }
} as const

export const contrast = {
  // WCAG AA compliance ratios
  normal: 4.5,    // Normal text
  large: 3.0,     // Large text (18px+ or 14px+ bold)
  ui: 3.0,        // UI components
  
  // WCAG AAA compliance ratios  
  enhanced: {
    normal: 7.0,
    large: 4.5,
    ui: 4.5
  }
} as const

// Z-index scale
export const zIndex = {
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modalBackdrop: 1040,
  modal: 1050,
  popover: 1060,
  tooltip: 1070,
} as const

// Component-specific sizing
export const size = {
  input: {
    sm: { height: '2rem', padding: spacing[2] },     // 32px
    md: { height: '2.5rem', padding: spacing[3] },   // 40px
    lg: { height: '3rem', padding: spacing[4] },     // 48px
  },
  
  kpi: {
    card: {
      padding: spacing[6],
      radius: borderRadius.lg,
      shadow: shadows.md
    }
  },
  
  nav: {
    width: '280px',
    widthCollapsed: '80px',
    transition: timing.normal
  }
} as const

// Semantic tokens for simulation-specific use cases
export const simulation = {
  kpi: {
    positive: colors.success[600],
    negative: colors.error[600],
    neutral: colors.gray[500],
  },
  
  chart: {
    primary: colors.primary[500],
    secondary: colors.primary[300],
    accent: colors.info[500],
    grid: colors.gray[200],
  }
} as const

// Export combined tokens
export const designTokens = {
  colors,
  typography,
  spacing,
  space, // Legacy alias
  layout,
  borderRadius,
  shadows,
  boxShadow, // Legacy alias
  button,
  form,
  table,
  timing,
  duration, // Legacy alias
  easing,
  motion,
  focus,
  contrast,
  zIndex,
  size,
  simulation
} as const

export type DesignTokens = typeof designTokens