# Accessibility Guidelines & WCAG Compliance

## Accessibility Philosophy

### **Universal Design Principles**
1. **Inclusive by Default**: All features accessible to all users from the start
2. **Progressive Enhancement**: Core functionality works without advanced features
3. **Multiple Interaction Methods**: Support keyboard, mouse, touch, and assistive technologies
4. **Clear Communication**: Information conveyed through multiple channels (visual, auditory, haptic)

### **WCAG 2.1 Compliance Targets**
- **Level AA**: Minimum standard for all components and features
- **Level AAA**: Target for critical user flows (scenario creation, data entry)
- **Section 508**: Federal accessibility requirements compliance

## WCAG 2.1 Guidelines Implementation

### **1. Perceivable**

#### **Text Alternatives (1.1)**
```typescript
interface ImageProps {
  src: string
  alt: string           // Required, descriptive alternative text
  decorative?: boolean  // If true, alt="" for decorative images
  longDesc?: string    // For complex images (charts, graphs)
}

// Chart accessibility
<Chart 
  data={scenarioData}
  alt="Bar chart showing FTE growth across 5 offices from Q1 to Q4 2024"
  longDesc="Detailed data table available below chart"
/>

// Decorative images
<Image 
  src="/decorative-pattern.svg" 
  alt=""                    // Empty alt for decorative
  decorative={true}
  aria-hidden="true"
/>
```

#### **Time-based Media (1.2)**
```typescript
// Video content requirements
interface VideoProps {
  src: string
  captions?: string        // WebVTT file for captions
  transcript?: string      // Full transcript URL
  audioDescription?: string // Audio description track
}

// Not applicable to SimpleSim (no video content planned)
```

#### **Adaptable Content (1.3)**
```typescript
// Semantic HTML structure
const SemanticLayout = () => (
  <main>
    <header>
      <h1>Workforce Planning Dashboard</h1>
      <nav aria-label="Main navigation">
        <ul>
          <li><a href="/scenarios">Scenarios</a></li>
          <li><a href="/offices">Offices</a></li>
        </ul>
      </nav>
    </header>
    
    <section aria-labelledby="recent-scenarios">
      <h2 id="recent-scenarios">Recent Scenarios</h2>
      <table aria-describedby="scenario-table-desc">
        <caption id="scenario-table-desc">
          List of recently created workforce scenarios with status and actions
        </caption>
        {/* Table content */}
      </table>
    </section>
  </main>
)

// Reading order preservation
interface SkipLinkProps {
  href: string
  children: ReactNode
}

const SkipLink: React.FC<SkipLinkProps> = ({ href, children }) => (
  <a 
    href={href}
    className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-white focus:rounded"
  >
    {children}
  </a>
)
```

#### **Distinguishable Content (1.4)**
```typescript
// Color contrast requirements
const colorContrast = {
  // WCAG AA: 4.5:1 for normal text, 3:1 for large text
  normalText: {
    minimumRatio: 4.5,
    examples: {
      'text-gray-900 on bg-white': 16.75,    // ✓ Excellent
      'text-gray-600 on bg-white': 4.54,     // ✓ AA compliant
      'text-gray-500 on bg-white': 3.94,     // ✗ Fails AA
      'text-primary-600 on bg-white': 4.91   // ✓ AA compliant
    }
  },
  
  largeText: {
    minimumRatio: 3.0,
    definition: '18px+ or 14px+ bold',
    examples: {
      'text-gray-500 on bg-white': 3.94      // ✓ AA compliant for large text
    }
  },
  
  // WCAG AAA: 7:1 for normal text, 4.5:1 for large text (target for critical UI)
  enhanced: {
    normalText: 7.0,
    largeText: 4.5
  }
}

// Color not the only visual means
interface StatusIndicatorProps {
  status: 'success' | 'warning' | 'error' | 'info'
  children: ReactNode
}

const StatusIndicator: React.FC<StatusIndicatorProps> = ({ status, children }) => (
  <div className={`status-${status}`}>
    <Icon name={getStatusIcon(status)} aria-hidden="true" />
    <span>{children}</span>
    <span className="sr-only">{getStatusText(status)}</span>
  </div>
)

// Text resize support (up to 200% without horizontal scrolling)
const responsiveText = {
  // Use relative units (rem, em) not pixels
  fontSize: 'text-base',  // 1rem = 16px default, scales with user settings
  lineHeight: 'leading-relaxed', // 1.625 for good readability
  maxWidth: '65ch',       // Optimal reading line length
}
```

### **2. Operable**

#### **Keyboard Accessible (2.1)**
```typescript
// Keyboard navigation support
interface KeyboardNavigationProps {
  onKeyDown?: (event: KeyboardEvent) => void
  tabIndex?: number
  'aria-label'?: string
}

const DataTable: React.FC<DataTableProps> = ({ data, columns, onRowClick }) => {
  const handleKeyDown = (event: KeyboardEvent, rowIndex: number) => {
    switch (event.key) {
      case 'Enter':
      case ' ':
        event.preventDefault()
        onRowClick?.(data[rowIndex])
        break
      case 'ArrowDown':
        event.preventDefault()
        focusRow(rowIndex + 1)
        break
      case 'ArrowUp':
        event.preventDefault()
        focusRow(rowIndex - 1)
        break
    }
  }
  
  return (
    <table>
      <tbody>
        {data.map((row, index) => (
          <tr 
            key={row.id}
            tabIndex={0}
            onClick={() => onRowClick?.(row)}
            onKeyDown={(e) => handleKeyDown(e, index)}
            aria-label={`Scenario ${row.name}, click to view details`}
          >
            {/* Row content */}
          </tr>
        ))}
      </tbody>
    </table>
  )
}

// Focus management
const Modal: React.FC<ModalProps> = ({ open, onClose, children }) => {
  const modalRef = useRef<HTMLDivElement>(null)
  const previousFocusRef = useRef<HTMLElement>()
  
  useEffect(() => {
    if (open) {
      // Store previous focus
      previousFocusRef.current = document.activeElement as HTMLElement
      
      // Focus modal
      modalRef.current?.focus()
      
      // Trap focus within modal
      const trapFocus = (e: KeyboardEvent) => {
        if (e.key === 'Tab') {
          const focusableElements = modalRef.current?.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
          )
          // Focus trapping logic
        }
      }
      
      document.addEventListener('keydown', trapFocus)
      return () => document.removeEventListener('keydown', trapFocus)
    } else {
      // Restore previous focus
      previousFocusRef.current?.focus()
    }
  }, [open])
  
  return open ? (
    <div 
      ref={modalRef}
      role="dialog"
      aria-modal="true"
      tabIndex={-1}
    >
      {children}
    </div>
  ) : null
}
```

#### **No Seizures (2.3)**
```typescript
// Animation safety
const safeAnimations = {
  // Respect user's motion preferences
  respectMotionPreference: true,
  
  // Avoid flashing more than 3 times per second
  flashingLimit: 3,
  
  // Provide controls for auto-playing content
  autoPlayControls: true
}

// CSS implementation
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

// React hook for motion preference
const useReducedMotion = () => {
  const [reducedMotion, setReducedMotion] = useState(false)
  
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setReducedMotion(mediaQuery.matches)
    
    const handleChange = () => setReducedMotion(mediaQuery.matches)
    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])
  
  return reducedMotion
}
```

#### **Navigable (2.4)**
```typescript
// Page titles
const usePageTitle = (title: string) => {
  useEffect(() => {
    const fullTitle = `${title} - SimpleSim Workforce Planning`
    document.title = fullTitle
  }, [title])
}

// Skip links
const SkipNavigation = () => (
  <>
    <SkipLink href="#main-content">Skip to main content</SkipLink>
    <SkipLink href="#navigation">Skip to navigation</SkipLink>
    <SkipLink href="#search">Skip to search</SkipLink>
  </>
)

// Logical heading structure
const HeadingStructure = () => (
  <main>
    <h1>Workforce Planning Dashboard</h1>
    
    <section>
      <h2>Recent Scenarios</h2>
      <article>
        <h3>Q1 2024 Growth Plan</h3>
        <h4>Office Breakdown</h4>
      </article>
    </section>
    
    <section>
      <h2>Performance Metrics</h2>
      {/* No h3 without content, no skipping levels */}
    </section>
  </main>
)

// Focus indicators
const focusStyles = {
  // Visible focus indicator
  focusRing: 'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
  
  // Custom focus styles
  customFocus: 'focus:bg-primary-50 focus:border-primary-500 focus:text-primary-700'
}
```

### **3. Understandable**

#### **Readable (3.1)**
```typescript
// Language identification
const LanguageSupport = () => (
  <html lang="en">
    <head>
      <title>SimpleSim Workforce Planning</title>
    </head>
    <body>
      <main>
        <section>
          <h2>Growth Scenarios</h2>
          <p>Create and analyze workforce growth scenarios for your organization.</p>
          
          {/* Foreign language content */}
          <blockquote lang="sv">
            <p>Tillväxtscenarier för Stockholm-kontoret</p>
          </blockquote>
        </section>
      </main>
    </body>
  </html>
)

// Plain language guidelines
const contentGuidelines = {
  readingLevel: 'Grade 8-9 equivalent',
  sentenceLength: 'Maximum 25 words',
  paragraphLength: 'Maximum 5 sentences',
  jargonUsage: 'Define technical terms on first use',
  activeVoice: 'Prefer active over passive voice'
}
```

#### **Predictable (3.2)**
```typescript
// Consistent navigation
interface NavigationConsistency {
  // Same navigation order across pages
  navigationOrder: ['Dashboard', 'Scenarios', 'Offices', 'Reports', 'Settings']
  
  // Consistent interaction patterns
  buttonBehavior: 'always-same-for-same-action'
  linkBehavior: 'external-links-open-new-window-with-warning'
  formBehavior: 'validation-on-blur-submission-on-explicit-action'
}

// Context changes only on explicit user action
const ContextChangeRules = {
  automaticRedirect: false,          // No auto-redirects
  automaticRefresh: false,           // No auto-refresh
  automaticPopups: false,            // No unexpected popups
  focusChange: 'only-on-user-action' // Don't move focus unexpectedly
}

// Error identification and suggestions
interface FormValidation {
  errorIdentification: {
    location: 'inline-with-field-and-summary-at-top',
    timing: 'on-blur-and-on-submit',
    format: 'clear-description-of-problem'
  }
  
  errorSuggestion: {
    format: 'specific-suggestion-for-correction',
    examples: 'provide-valid-format-examples',
    recovery: 'clear-path-to-fix-error'
  }
}

const FormField: React.FC<FormFieldProps> = ({ 
  name, 
  label, 
  validation, 
  value, 
  onChange 
}) => {
  const [error, setError] = useState<string>()
  
  const validateField = (val: string) => {
    if (validation.required && !val) {
      return 'This field is required'
    }
    if (validation.pattern && !validation.pattern.test(val)) {
      return `Please enter a valid ${label.toLowerCase()}. Example: ${validation.example}`
    }
    return undefined
  }
  
  return (
    <div>
      <label htmlFor={name}>
        {label} {validation.required && <span aria-label="required">*</span>}
      </label>
      
      <input
        id={name}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onBlur={(e) => setError(validateField(e.target.value))}
        aria-invalid={!!error}
        aria-describedby={error ? `${name}-error` : undefined}
      />
      
      {error && (
        <div id={`${name}-error`} role="alert" className="error">
          {error}
        </div>
      )}
    </div>
  )
}
```

### **4. Robust**

#### **Compatible (4.1)**
```typescript
// Valid HTML structure
const ValidHTML = () => (
  // Ensure all elements have required attributes
  <form>
    <fieldset>
      <legend>Scenario Configuration</legend>
      
      <label htmlFor="scenario-name">Scenario Name</label>
      <input 
        id="scenario-name"
        type="text"
        name="name"
        required
        aria-describedby="name-help"
      />
      <div id="name-help">
        Choose a descriptive name for your scenario
      </div>
    </fieldset>
  </form>
)

// Assistive technology compatibility
interface ARIASupport {
  // Proper ARIA labels and descriptions
  labels: 'aria-label-or-aria-labelledby-for-all-interactive-elements'
  descriptions: 'aria-describedby-for-additional-context'
  
  // Live regions for dynamic content
  liveRegions: 'aria-live-for-status-updates'
  
  // Proper roles for custom components
  roles: 'role-attribute-for-custom-widgets'
}

const LoadingButton: React.FC<LoadingButtonProps> = ({ 
  loading, 
  children, 
  onClick 
}) => (
  <button 
    onClick={onClick}
    disabled={loading}
    aria-describedby={loading ? 'loading-status' : undefined}
  >
    {children}
    {loading && (
      <span 
        id="loading-status"
        aria-live="polite"
        aria-label="Loading"
        className="spinner"
      />
    )}
  </button>
)
```

## Assistive Technology Support

### **Screen Readers**
```typescript
// Screen reader optimizations
interface ScreenReaderSupport {
  // Descriptive link text
  linkText: 'descriptive-not-click-here'
  
  // Table headers
  tableHeaders: 'th-elements-with-scope-attribute'
  
  // Form labels
  formLabels: 'explicit-label-for-every-input'
  
  // Alternative text
  altText: 'descriptive-alt-text-for-images'
  
  // Skip links
  skipLinks: 'skip-to-main-content-and-navigation'
}

// Complex table with proper headers
const AccessibleDataTable = ({ data, columns }) => (
  <table>
    <caption>
      Workforce scenarios with status, creation date, and available actions
    </caption>
    <thead>
      <tr>
        {columns.map(column => (
          <th 
            key={column.id}
            scope="col"
            aria-sort={getSortDirection(column.id)}
          >
            {column.header}
          </th>
        ))}
      </tr>
    </thead>
    <tbody>
      {data.map(row => (
        <tr key={row.id}>
          <th scope="row">{row.name}</th>
          <td>{row.status}</td>
          <td>{row.createdDate}</td>
          <td>
            <button aria-label={`Edit scenario ${row.name}`}>
              Edit
            </button>
          </td>
        </tr>
      ))}
    </tbody>
  </table>
)
```

### **Voice Control**
```typescript
// Voice control considerations
interface VoiceControlSupport {
  // Descriptive button text
  buttonLabels: 'use-visible-text-as-accessible-name'
  
  // Voice commands mapping
  voiceCommands: {
    'create scenario': 'maps-to-create-scenario-button',
    'edit office': 'maps-to-edit-button-in-context',
    'go to dashboard': 'maps-to-dashboard-link'
  }
  
  // Avoid voice conflicts
  uniqueLabels: 'ensure-unique-interactive-element-names'
}
```

### **Switch Navigation**
```typescript
// Switch navigation support
interface SwitchNavigationSupport {
  // Logical tab order
  tabOrder: 'sequential-logical-order'
  
  // Focus indicators
  focusVisible: 'clear-focus-indicators'
  
  // Timing considerations
  timing: 'no-time-limits-on-interactions'
  
  // Error recovery
  errorRecovery: 'easy-way-to-correct-mistakes'
}
```

## Testing Strategy

### **Automated Testing**
```typescript
// Accessibility testing tools
const a11yTestingTools = {
  // Unit/component testing
  'jest-axe': 'automated-accessibility-testing-in-jest',
  '@testing-library/jest-dom': 'accessibility-focused-assertions',
  
  // Integration testing
  'cypress-axe': 'e2e-accessibility-testing',
  'pa11y': 'command-line-accessibility-testing',
  
  // Browser extensions
  'axe-devtools': 'in-browser-accessibility-testing',
  'lighthouse': 'accessibility-audit-in-chrome-devtools'
}

// Example test
import { axe, toHaveNoViolations } from 'jest-axe'

expect.extend(toHaveNoViolations)

test('Button component should be accessible', async () => {
  const { container } = render(
    <Button onClick={() => {}}>Click me</Button>
  )
  
  const results = await axe(container)
  expect(results).toHaveNoViolations()
})
```

### **Manual Testing**
```typescript
const manualTestingChecklist = {
  keyboardTesting: [
    'Tab through all interactive elements',
    'Activate elements with Enter/Space',
    'Navigate tables with arrow keys',
    'Escape closes modals',
    'Focus indicators are visible'
  ],
  
  screenReaderTesting: [
    'Test with NVDA (Windows)',
    'Test with JAWS (Windows)', 
    'Test with VoiceOver (macOS)',
    'Test with Orca (Linux)',
    'Verify announcements are logical'
  ],
  
  visualTesting: [
    'Zoom to 200% without horizontal scroll',
    'Test in high contrast mode',
    'Verify color contrast ratios',
    'Test with custom colors',
    'Check focus indicators'
  ]
}
```

### **User Testing**
```typescript
const userTestingStrategy = {
  participants: [
    'users-with-visual-impairments',
    'users-with-motor-impairments', 
    'users-with-cognitive-impairments',
    'users-with-hearing-impairments'
  ],
  
  scenarios: [
    'create-new-scenario-task',
    'compare-scenarios-task',
    'configure-office-task',
    'export-results-task'
  ],
  
  assistiveTechnology: [
    'screen-readers',
    'voice-control-software',
    'switch-navigation',
    'magnification-software'
  ]
}
```

This comprehensive accessibility implementation ensures SimpleSim is usable by all users, regardless of their abilities or the assistive technologies they use.