/** @type {import('tailwindcss').Config} */

// Unified Design System Colors
// Using CSS variables for theme switching and consistency
const designSystemColors = {
  // Primary brand colors
  primary: {
    50: 'var(--color-primary-50)',
    100: 'var(--color-primary-100)',
    200: 'var(--color-primary-200)',
    300: 'var(--color-primary-300)',
    400: 'var(--color-primary-400)',
    500: 'var(--color-primary-500)',
    600: 'var(--color-primary-600)',
    700: 'var(--color-primary-700)',
    800: 'var(--color-primary-800)',
    900: 'var(--color-primary-900)',
    950: 'var(--color-primary-950)',
    DEFAULT: 'var(--color-primary)',
  },
  
  // Neutral grays  
  gray: {
    50: 'var(--color-gray-50)',
    100: 'var(--color-gray-100)',
    200: 'var(--color-gray-200)',
    300: 'var(--color-gray-300)',
    400: 'var(--color-gray-400)',
    500: 'var(--color-gray-500)',
    600: 'var(--color-gray-600)',
    700: 'var(--color-gray-700)',
    800: 'var(--color-gray-800)',
    900: 'var(--color-gray-900)',
    950: 'var(--color-gray-950)',
  },
  
  // Semantic colors
  success: {
    50: 'var(--color-success-50)',
    500: 'var(--color-success-500)',
    600: 'var(--color-success-600)',
    700: 'var(--color-success-700)',
    900: 'var(--color-success-900)',
    DEFAULT: 'var(--color-success)',
  },
  
  warning: {
    50: 'var(--color-warning-50)',
    500: 'var(--color-warning-500)',
    600: 'var(--color-warning-600)',
    700: 'var(--color-warning-700)',
    900: 'var(--color-warning-900)',
    DEFAULT: 'var(--color-warning)',
  },
  
  error: {
    50: 'var(--color-error-50)',
    500: 'var(--color-error-500)',
    600: 'var(--color-error-600)',
    700: 'var(--color-error-700)',
    900: 'var(--color-error-900)',
    DEFAULT: 'var(--color-error)',
  },

  info: {
    50: 'var(--color-info-50)',
    500: 'var(--color-info-500)',
    600: 'var(--color-info-600)',
    900: 'var(--color-info-900)',
    DEFAULT: 'var(--color-info)',
  },
  
  // Legacy destructive alias for shadcn/ui compatibility
  destructive: {
    50: 'var(--color-destructive-50)',
    100: 'var(--color-destructive-100)',
    500: 'var(--color-destructive-500)',
    DEFAULT: 'var(--color-destructive)',
  },
}

module.exports = {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        // shadcn/ui CSS variables - these must come first for compatibility
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        
        // Simulation-specific semantic colors
        'kpi-positive': 'var(--kpi-positive)',
        'kpi-negative': 'var(--kpi-negative)',
        'kpi-neutral': 'var(--kpi-neutral)',
        
        'chart-primary': 'var(--chart-primary)',
        'chart-secondary': 'var(--chart-secondary)',
        'chart-accent': 'var(--chart-accent)',
        'chart-grid': 'var(--chart-grid)',
        
        // Unified design system colors (preserves shadcn/ui compatibility)
        ...Object.fromEntries(
          Object.entries(designSystemColors).filter(([key]) => 
            !['primary', 'secondary', 'destructive'].includes(key)
          )
        ),
        

      },
      
      fontFamily: {
        sans: 'var(--font-sans)'.split(','),
        mono: 'var(--font-mono)'.split(','),
      },
      
      fontSize: {
        // Legacy Tailwind scale using design tokens
        xs: ['var(--font-size-xs)', { lineHeight: '1rem' }],
        sm: ['var(--font-size-sm)', { lineHeight: '1.25rem' }],
        base: ['var(--font-size-base)', { lineHeight: '1.5rem' }],
        lg: ['var(--font-size-lg)', { lineHeight: '1.75rem' }],
        xl: ['var(--font-size-xl)', { lineHeight: '1.75rem' }],
        '2xl': ['var(--font-size-2xl)', { lineHeight: '2rem' }],
        '3xl': ['var(--font-size-3xl)', { lineHeight: '2.25rem' }],
        '4xl': ['var(--font-size-4xl)', { lineHeight: '2.5rem' }],
        
        // Design system semantic scales using CSS variables
        'display-xl': ['var(--text-display-xl-size)', {
          fontWeight: 'var(--text-display-xl-weight)',
          lineHeight: 'var(--text-display-xl-line-height)',
          letterSpacing: 'var(--text-display-xl-letter-spacing)',
        }],
        'display-lg': ['var(--text-display-lg-size)', {
          fontWeight: 'var(--text-display-lg-weight)',
          lineHeight: 'var(--text-display-lg-line-height)',
          letterSpacing: 'var(--text-display-lg-letter-spacing)',
        }],
        'display-md': ['var(--text-display-md-size)', {
          fontWeight: 'var(--text-display-md-weight)',
          lineHeight: 'var(--text-display-md-line-height)',
          letterSpacing: 'var(--text-display-md-letter-spacing)',
        }],
        'display-sm': ['var(--text-display-sm-size)', {
          fontWeight: 'var(--text-display-sm-weight)',
          lineHeight: 'var(--text-display-sm-line-height)',
          letterSpacing: 'var(--text-display-sm-letter-spacing)',
        }],
        'heading-xl': ['var(--text-heading-xl-size)', {
          fontWeight: 'var(--text-heading-xl-weight)',
          lineHeight: 'var(--text-heading-xl-line-height)',
        }],
        'heading-lg': ['var(--text-heading-lg-size)', {
          fontWeight: 'var(--text-heading-lg-weight)',
          lineHeight: 'var(--text-heading-lg-line-height)',
        }],
        'heading-md': ['var(--text-heading-md-size)', {
          fontWeight: 'var(--text-heading-md-weight)',
          lineHeight: 'var(--text-heading-md-line-height)',
        }],
        'heading-sm': ['var(--text-heading-sm-size)', {
          fontWeight: 'var(--text-heading-sm-weight)',
          lineHeight: 'var(--text-heading-sm-line-height)',
        }],
        'body-lg': ['var(--text-body-lg-size)', {
          fontWeight: 'var(--text-body-lg-weight)',
          lineHeight: 'var(--text-body-lg-line-height)',
        }],
        'body-md': ['var(--text-body-md-size)', {
          fontWeight: 'var(--text-body-md-weight)',
          lineHeight: 'var(--text-body-md-line-height)',
        }],
        'body-sm': ['var(--text-body-sm-size)', {
          fontWeight: 'var(--text-body-sm-weight)',
          lineHeight: 'var(--text-body-sm-line-height)',
        }],
        'label-lg': ['var(--text-label-lg-size)', {
          fontWeight: 'var(--text-label-lg-weight)',
          lineHeight: 'var(--text-label-lg-line-height)',
        }],
        'label-md': ['var(--text-label-md-size)', {
          fontWeight: 'var(--text-label-md-weight)',
          lineHeight: 'var(--text-label-md-line-height)',
        }],
        'label-sm': ['var(--text-label-sm-size)', {
          fontWeight: 'var(--text-label-sm-weight)',
          lineHeight: 'var(--text-label-sm-line-height)',
        }],
        'caption-lg': ['var(--text-caption-lg-size)', {
          fontWeight: 'var(--text-caption-lg-weight)',
          lineHeight: 'var(--text-caption-lg-line-height)',
        }],
        'caption-md': ['var(--text-caption-md-size)', {
          fontWeight: 'var(--text-caption-md-weight)',
          lineHeight: 'var(--text-caption-md-line-height)',
        }],
        'caption-sm': ['var(--text-caption-sm-size)', {
          fontWeight: 'var(--text-caption-sm-weight)',
          lineHeight: 'var(--text-caption-sm-line-height)',
        }],
      },
      
      fontWeight: {
        normal: 'var(--font-weight-normal)',
        medium: 'var(--font-weight-medium)',
        semibold: 'var(--font-weight-semibold)',
        bold: 'var(--font-weight-bold)',
      },
      
      spacing: {
        0: 'var(--spacing-0)',
        1: 'var(--spacing-1)',  // 4px
        2: 'var(--spacing-2)',  // 8px
        3: 'var(--spacing-3)',  // 12px
        4: 'var(--spacing-4)',  // 16px
        5: 'var(--spacing-5)',  // 20px
        6: 'var(--spacing-6)',  // 24px
        8: 'var(--spacing-8)',  // 32px
        10: 'var(--spacing-10)', // 40px
        12: 'var(--spacing-12)', // 48px
        16: 'var(--spacing-16)', // 64px
        20: 'var(--spacing-20)', // 80px
        24: 'var(--spacing-24)', // 96px
      },
      
      borderRadius: {
        // shadcn/ui compatibility
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
        
        // Unified design system values
        none: 'var(--radius-none)',
        DEFAULT: 'var(--radius)',
        full: 'var(--radius-full)',
        
        // Design system semantic values
        'ss-sm': 'var(--radius-sm)',   // 4px - Small elements
        'ss-md': 'var(--radius-md)',   // 8px - Standard elements  
        'ss-lg': 'var(--radius-lg)',   // 12px - Cards, panels
        'ss-xl': 'var(--radius-xl)',   // 16px - Large containers
        'ss-2xl': 'var(--radius-2xl)', // 20px - Very large containers
      },
      
      boxShadow: {
        sm: 'var(--shadow-sm)',
        DEFAULT: 'var(--shadow)',
        md: 'var(--shadow-md)',
        lg: 'var(--shadow-lg)',
        xl: 'var(--shadow-xl)',
        focus: 'var(--shadow-focus)',
        none: 'var(--shadow-none)',
      },
      
      transitionDuration: {
        fast: 'var(--timing-fast)',       // 150ms
        normal: 'var(--timing-normal)',   // 200ms
        slow: 'var(--timing-slow)',       // 300ms
        slower: 'var(--timing-slower)',   // 500ms
      },
      
      transitionTimingFunction: {
        'ss-default': 'var(--easing-default)',
        'ss-in': 'var(--easing-in)',
        'ss-out': 'var(--easing-out)', 
        'ss-in-out': 'var(--easing-in-out)',
      },
      
      zIndex: {
        dropdown: 'var(--z-dropdown)',
        sticky: 'var(--z-sticky)',
        fixed: 'var(--z-fixed)',
        'modal-backdrop': 'var(--z-modal-backdrop)',
        modal: 'var(--z-modal)',
        popover: 'var(--z-popover)',
        tooltip: 'var(--z-tooltip)',
      },
      
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}