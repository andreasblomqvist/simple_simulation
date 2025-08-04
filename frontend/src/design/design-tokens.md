# Design Tokens Specification

## Visual Identity Foundation

### **Color System**

#### **Primary Brand Colors**
```typescript
const colors = {
  // Brand Primary (Blue)
  primary: {
    50: '#eff6ff',   // Very light backgrounds
    100: '#dbeafe',  // Light backgrounds, borders
    200: '#bfdbfe',  // Subtle UI elements
    300: '#93c5fd',  // Disabled states
    400: '#60a5fa',  // Hover states
    500: '#3b82f6',  // Primary brand color
    600: '#2563eb',  // Primary hover, active
    700: '#1d4ed8',  // Primary pressed
    800: '#1e40af',  // High contrast text
    900: '#1e3a8a'   // Maximum contrast
  },

  // Semantic Colors
  success: {
    50: '#f0fdf4',
    500: '#22c55e',  // Success states, positive metrics
    600: '#16a34a',  // Success hover
    700: '#15803d'   // Success pressed
  },

  warning: {
    50: '#fffbeb',
    500: '#f59e0b',  // Warning states, attention needed
    600: '#d97706',  // Warning hover
    700: '#b45309'   // Warning pressed
  },

  error: {
    50: '#fef2f2',
    500: '#ef4444',  // Error states, destructive actions
    600: '#dc2626',  // Error hover
    700: '#b91c1c'   // Error pressed
  },

  // Neutral Grays
  gray: {
    50: '#f9fafb',   // Background subtle
    100: '#f3f4f6',  // Background light
    200: '#e5e7eb',  // Borders light
    300: '#d1d5db',  // Borders standard
    400: '#9ca3af',  // Text disabled
    500: '#6b7280',  // Text secondary
    600: '#4b5563',  // Text primary
    700: '#374151',  // Text emphasis
    800: '#1f2937',  // Text strong
    900: '#111827'   // Text maximum contrast
  }
}
```

#### **Dark Mode Support**
```typescript
const darkColors = {
  background: '#0f172a',      // Dark background
  surface: '#1e293b',        // Card/panel backgrounds
  border: '#334155',         // Borders in dark mode
  text: {
    primary: '#f1f5f9',      // Primary text
    secondary: '#cbd5e1',    // Secondary text
    muted: '#64748b'         // Muted/disabled text
  }
}
```

### **Typography System**

#### **Font Stack**
```typescript
const fonts = {
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
  ]
}
```

#### **Type Scale**
```typescript
const typography = {
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
  }
}
```

### **Spacing System**

#### **Base Scale**
```typescript
const spacing = {
  // Base scale (4px increments)
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
}

// Semantic spacing aliases
const layout = {
  containerPadding: spacing[4],     // 16px
  sectionGap: spacing[8],           // 32px
  cardPadding: spacing[6],          // 24px
  buttonPadding: spacing[3],        // 12px
  inputPadding: spacing[3],         // 12px
  tableCell: spacing[3],            // 12px
  listItem: spacing[4]              // 16px
}
```

### **Border Radius**
```typescript
const radius = {
  none: '0px',
  sm: '4px',    // Small elements (tags, badges)
  md: '8px',    // Standard elements (buttons, inputs)
  lg: '12px',   // Cards, panels
  xl: '16px',   // Large containers
  full: '9999px' // Pills, avatars
}
```

### **Shadows & Elevation**
```typescript
const shadows = {
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
  }
}
```

## Component-Specific Tokens

### **Button Variants**
```typescript
const button = {
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
}
```

### **Form Controls**
```typescript
const form = {
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
}
```

### **Data Display**
```typescript
const table = {
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
}
```

## Animation & Timing

### **Transition Timing**
```typescript
const timing = {
  fast: '150ms',      // Quick interactions (hover, focus)
  normal: '200ms',    // Standard transitions
  slow: '300ms',      // Complex animations
  slower: '500ms'     // Page transitions
}

const easing = {
  default: 'cubic-bezier(0.4, 0, 0.2, 1)',     // Smooth standard
  in: 'cubic-bezier(0.4, 0, 1, 1)',            // Accelerating
  out: 'cubic-bezier(0, 0, 0.2, 1)',           // Decelerating  
  inOut: 'cubic-bezier(0.4, 0, 0.2, 1)'        // Smooth in-out
}
```

### **Motion Principles**
```typescript
const motion = {
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
}
```

## Accessibility Tokens

### **Focus Indicators**
```typescript
const focus = {
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
}
```

### **Color Contrast Requirements**
```typescript
const contrast = {
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
}
```

## Implementation

### **CSS Custom Properties**
```css
:root {
  /* Colors */
  --color-primary-500: #3b82f6;
  --color-primary-600: #2563eb;
  --color-gray-50: #f9fafb;
  --color-gray-900: #111827;
  
  /* Typography */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --text-display-lg: 36px;
  --text-body-md: 14px;
  
  /* Spacing */
  --spacing-1: 4px;
  --spacing-4: 16px;
  --spacing-8: 32px;
  
  /* Shadows */
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-focus: 0 0 0 3px rgb(59 130 246 / 0.1);
}

/* Dark mode overrides */
@media (prefers-color-scheme: dark) {
  :root {
    --color-background: #0f172a;
    --color-surface: #1e293b;
    --color-text-primary: #f1f5f9;
  }
}
```

### **TypeScript Tokens Export**
```typescript
export const designTokens = {
  colors,
  typography,
  spacing,
  layout,
  radius,
  shadows,
  button,
  form,
  table,
  timing,
  easing,
  motion,
  focus,
  contrast
} as const

export type DesignTokens = typeof designTokens
```

This comprehensive token system provides the foundation for consistent, accessible, and maintainable UI design across the entire SimpleSim application.