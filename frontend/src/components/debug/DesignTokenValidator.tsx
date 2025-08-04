/**
 * Design Token Validation Component
 * Tests the unified design token system integration
 * Use this component to validate that design tokens are properly loaded
 */

import React from 'react';

export const DesignTokenValidator: React.FC = () => {
  return (
    <div className="p-8 space-y-8 bg-background text-foreground">
      <div className="space-y-4">
        <h1 className="text-display-lg font-bold">Design Token Validation</h1>
        <p className="text-body-md text-muted-foreground">
          This component validates that the unified design token system is working correctly.
        </p>
      </div>

      {/* Typography Scale */}
      <section className="space-y-4">
        <h2 className="text-heading-xl border-b border-border pb-2">Typography System</h2>
        <div className="space-y-2">
          <div className="text-display-xl">Display XL - Page Titles</div>
          <div className="text-display-lg">Display LG - Hero Content</div>
          <div className="text-heading-xl">Heading XL - Section Titles</div>
          <div className="text-heading-lg">Heading LG - Card Headers</div>
          <div className="text-body-lg">Body LG - Content Text (16px)</div>
          <div className="text-body-md">Body MD - Standard Text (14px)</div>
          <div className="text-label-lg">Label LG - Form Labels</div>
          <div className="text-caption-md text-muted-foreground">Caption MD - Help Text</div>
        </div>
      </section>

      {/* Color System */}
      <section className="space-y-4">
        <h2 className="text-heading-xl border-b border-border pb-2">Color System</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {/* Primary Colors */}
          <div className="space-y-2">
            <h3 className="text-heading-sm">Primary</h3>
            <div className="bg-primary-500 h-12 rounded-ss-md flex items-center justify-center text-white text-caption-lg">
              500
            </div>
            <div className="flex gap-1">
              <div className="bg-primary-100 h-6 w-6 rounded-ss-sm"></div>
              <div className="bg-primary-300 h-6 w-6 rounded-ss-sm"></div>
              <div className="bg-primary-600 h-6 w-6 rounded-ss-sm"></div>
              <div className="bg-primary-900 h-6 w-6 rounded-ss-sm"></div>
            </div>
          </div>

          {/* Semantic Colors */}
          <div className="space-y-2">
            <h3 className="text-heading-sm">Success</h3>
            <div className="bg-success-500 h-12 rounded-ss-md flex items-center justify-center text-white text-caption-lg">
              Success
            </div>
          </div>

          <div className="space-y-2">
            <h3 className="text-heading-sm">Warning</h3>
            <div className="bg-warning-500 h-12 rounded-ss-md flex items-center justify-center text-white text-caption-lg">
              Warning
            </div>
          </div>

          <div className="space-y-2">
            <h3 className="text-heading-sm">Error</h3>
            <div className="bg-error-500 h-12 rounded-ss-md flex items-center justify-center text-white text-caption-lg">
              Error
            </div>
          </div>
        </div>
      </section>

      {/* Simulation Colors */}
      <section className="space-y-4">
        <h2 className="text-heading-xl border-b border-border pb-2">Simulation Colors</h2>
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-kpi-positive text-white p-4 rounded-ss-lg text-center">
            <div className="text-heading-sm">KPI Positive</div>
            <div className="text-caption-md opacity-80">Growth metrics</div>
          </div>
          <div className="bg-kpi-negative text-white p-4 rounded-ss-lg text-center">
            <div className="text-heading-sm">KPI Negative</div>
            <div className="text-caption-md opacity-80">Decline metrics</div>
          </div>
          <div className="bg-kpi-neutral text-white p-4 rounded-ss-lg text-center">
            <div className="text-heading-sm">KPI Neutral</div>
            <div className="text-caption-md opacity-80">Stable metrics</div>
          </div>
        </div>
      </section>

      {/* Spacing System */}
      <section className="space-y-4">
        <h2 className="text-heading-xl border-b border-border pb-2">Spacing System</h2>
        <div className="space-y-2">
          <div className="bg-muted p-1 inline-block rounded-ss-sm">
            <span className="text-caption-md">spacing-1 (4px)</span>
          </div>
          <div className="bg-muted p-2 inline-block rounded-ss-sm">
            <span className="text-caption-md">spacing-2 (8px)</span>
          </div>
          <div className="bg-muted p-3 inline-block rounded-ss-sm">
            <span className="text-caption-md">spacing-3 (12px)</span>
          </div>
          <div className="bg-muted p-4 inline-block rounded-ss-sm">
            <span className="text-caption-md">spacing-4 (16px)</span>
          </div>
          <div className="bg-muted p-6 inline-block rounded-ss-sm">
            <span className="text-caption-md">spacing-6 (24px)</span>
          </div>
        </div>
      </section>

      {/* Border Radius */}
      <section className="space-y-4">
        <h2 className="text-heading-xl border-b border-border pb-2">Border Radius</h2>
        <div className="flex gap-4 items-center">
          <div className="bg-muted p-4 rounded-ss-sm">
            <span className="text-caption-md">Small (4px)</span>
          </div>
          <div className="bg-muted p-4 rounded-ss-md">
            <span className="text-caption-md">Medium (8px)</span>
          </div>
          <div className="bg-muted p-4 rounded-ss-lg">
            <span className="text-caption-md">Large (12px)</span>
          </div>
          <div className="bg-muted p-4 rounded-ss-xl">
            <span className="text-caption-md">XL (16px)</span>
          </div>
        </div>
      </section>

      {/* Shadows */}
      <section className="space-y-4">
        <h2 className="text-heading-xl border-b border-border pb-2">Shadows</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-card p-4 rounded-ss-md shadow-sm border">
            <span className="text-caption-md">Small</span>
          </div>
          <div className="bg-card p-4 rounded-ss-md shadow-md border">
            <span className="text-caption-md">Medium</span>
          </div>
          <div className="bg-card p-4 rounded-ss-md shadow-lg border">
            <span className="text-caption-md">Large</span>
          </div>
          <div className="bg-card p-4 rounded-ss-md shadow-xl border">
            <span className="text-caption-md">XL</span>
          </div>
        </div>
      </section>

      {/* Interactive Elements */}
      <section className="space-y-4">
        <h2 className="text-heading-xl border-b border-border pb-2">Interactive Elements</h2>
        <div className="flex gap-4 items-center">
          <button className="bg-primary text-primary-foreground px-4 py-2 rounded-ss-md hover:bg-primary/90 ss-transition-fast">
            Primary Button
          </button>
          <button className="bg-secondary text-secondary-foreground px-4 py-2 rounded-ss-md hover:bg-secondary/80 ss-transition-fast border">
            Secondary Button
          </button>
          <button className="bg-destructive text-destructive-foreground px-4 py-2 rounded-ss-md hover:bg-destructive/90 ss-transition-fast">
            Destructive Button
          </button>
        </div>
      </section>

      {/* CSS Custom Properties Test */}
      <section className="space-y-4">
        <h2 className="text-heading-xl border-b border-border pb-2">CSS Custom Properties</h2>
        <div className="space-y-2 text-caption-md font-mono">
          <div>Primary Color: <span style={{ color: 'var(--color-primary-500)' }}>var(--color-primary-500)</span></div>
          <div>Card Background: <span style={{ backgroundColor: 'var(--card)', padding: '2px 4px', borderRadius: 'var(--radius-sm)' }}>var(--card)</span></div>
          <div>Border: <span style={{ border: '1px solid var(--border)', padding: '2px 4px', borderRadius: 'var(--radius-sm)' }}>var(--border)</span></div>
          <div>Spacing: <span style={{ backgroundColor: 'var(--muted)', padding: 'var(--spacing-2)', borderRadius: 'var(--radius-sm)' }}>var(--spacing-2)</span></div>
        </div>
      </section>

      {/* Theme Toggle Test */}
      <section className="space-y-4">
        <h2 className="text-heading-xl border-b border-border pb-2">Theme Integration</h2>
        <div className="p-4 border rounded-ss-lg bg-card">
          <p className="text-body-md mb-2">
            This card should adapt to light/dark theme changes automatically.
          </p>
          <p className="text-caption-md text-muted-foreground">
            Use the theme toggle in the app header to test theme switching.
          </p>
        </div>
      </section>

      <div className="pt-4 border-t border-border">
        <p className="text-caption-md text-muted-foreground">
          If all elements above display correctly with proper styling, colors, and spacing,
          the design token consolidation is working properly.
        </p>
      </div>
    </div>
  );
};

export default DesignTokenValidator;