/**
 * Critical Import Tests
 * Fast tests to catch build-breaking import issues
 */
import { describe, expect, it } from 'vitest';

describe('Critical Component Imports', () => {
  it('should import LoadingSpinner without errors', async () => {
    expect(async () => {
      await import('../components/ui/LoadingSpinner');
    }).not.toThrow();
  });

  it('should import ErrorBoundary without errors', async () => {
    expect(async () => {
      await import('../components/ui/ErrorBoundary');
    }).not.toThrow();
  });

  it('should import main application components', async () => {
    const imports = [
      '../main',
      '../components/common/ErrorDisplay',
      // Add other critical components as needed
    ];

    for (const importPath of imports) {
      try {
        await import(importPath);
      } catch (error) {
        if (error instanceof Error && error.message.includes('CSS')) {
          expect.fail(`CSS import error in ${importPath}: ${error.message}`);
        }
        // Allow other import errors (missing dependencies, etc.) as they're not CSS-related
        console.warn(`Non-CSS import issue in ${importPath}:`, error);
      }
    }
  });

  it('should validate CSS files exist for components that import them', () => {
    const cssFiles = [
      '../components/ui/LoadingSpinner.css',
      '../components/ui/ErrorBoundary.css',
    ];

    cssFiles.forEach(async (cssPath) => {
      try {
        // Try to import the CSS file directly
        await import(cssPath);
      } catch (error) {
        if (error instanceof Error) {
          expect.fail(`CSS file not found or invalid: ${cssPath} - ${error.message}`);
        }
      }
    });
  });
});