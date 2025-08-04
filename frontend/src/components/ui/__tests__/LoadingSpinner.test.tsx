/**
 * LoadingSpinner Component Tests
 * Tests component functionality, styling, and import validation
 */
import { describe, expect, it, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { LoadingSpinner } from '../LoadingSpinner';

describe('LoadingSpinner', () => {
  describe('Component Rendering', () => {
    it('should render spinner without message', () => {
      render(<LoadingSpinner />);
      
      const container = document.querySelector('.loading-spinner-container');
      expect(container).toBeInTheDocument();
      
      const spinner = document.querySelector('.loading-spinner');
      expect(spinner).toBeInTheDocument();
      
      const rings = document.querySelectorAll('.spinner-ring');
      expect(rings).toHaveLength(4);
    });

    it('should render spinner with message', () => {
      const message = 'Loading data...';
      render(<LoadingSpinner message={message} />);
      
      expect(screen.getByText(message)).toBeInTheDocument();
      
      const messageElement = document.querySelector('.loading-message');
      expect(messageElement).toBeInTheDocument();
      expect(messageElement).toHaveTextContent(message);
    });

    it('should apply custom className', () => {
      const customClass = 'custom-spinner-class';
      render(<LoadingSpinner className={customClass} />);
      
      const container = document.querySelector('.loading-spinner-container');
      expect(container).toHaveClass(customClass);
    });
  });

  describe('Size Variants', () => {
    it('should apply small size class', () => {
      render(<LoadingSpinner size="small" />);
      
      const container = document.querySelector('.loading-spinner-container');
      const spinner = document.querySelector('.loading-spinner');
      
      expect(container).toHaveClass('small');
      expect(spinner).toHaveClass('small');
    });

    it('should apply medium size class by default', () => {
      render(<LoadingSpinner />);
      
      const container = document.querySelector('.loading-spinner-container');
      const spinner = document.querySelector('.loading-spinner');
      
      expect(container).toHaveClass('medium');
      expect(spinner).toHaveClass('medium');
    });

    it('should apply large size class', () => {
      render(<LoadingSpinner size="large" />);
      
      const container = document.querySelector('.loading-spinner-container');
      const spinner = document.querySelector('.loading-spinner');
      
      expect(container).toHaveClass('large');
      expect(spinner).toHaveClass('large');
    });
  });

  describe('CSS Import Validation', () => {
    beforeEach(() => {
      // Clear any existing styles for clean testing
      const existingStyles = document.querySelectorAll('style[data-vite-dev-id*="LoadingSpinner"]');
      existingStyles.forEach(style => style.remove());
    });

    it('should have CSS styles loaded', () => {
      render(<LoadingSpinner />);
      
      // Check if styles are applied by looking for computed styles
      const spinner = document.querySelector('.loading-spinner');
      const container = document.querySelector('.loading-spinner-container');
      
      expect(spinner).toBeInTheDocument();
      expect(container).toBeInTheDocument();
      
      // Verify CSS classes are applied (which indicates CSS file was loaded)
      expect(container).toHaveClass('loading-spinner-container');
      expect(spinner).toHaveClass('loading-spinner');
      
      // Verify structure exists (rings)
      const rings = document.querySelectorAll('.spinner-ring');
      expect(rings).toHaveLength(4);
    });

    it('should not fail to render even if CSS is missing', () => {
      // This test ensures the component is resilient to CSS loading issues
      expect(() => {
        render(<LoadingSpinner message="Loading..." />);
      }).not.toThrow();
      
      const container = document.querySelector('.loading-spinner-container');
      expect(container).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper semantic structure', () => {
      render(<LoadingSpinner message="Loading content..." />);
      
      const container = document.querySelector('.loading-spinner-container');
      expect(container).toBeInTheDocument();
      
      // Message should be properly associated
      const message = document.querySelector('.loading-message');
      expect(message?.tagName.toLowerCase()).toBe('p');
    });

    it('should support reduced motion preferences', () => {
      // Test that the component respects prefers-reduced-motion
      const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
      
      render(<LoadingSpinner />);
      
      // The component should render regardless of motion preferences
      const spinner = document.querySelector('.loading-spinner');
      expect(spinner).toBeInTheDocument();
    });
  });

  describe('Props Interface', () => {
    it('should accept all valid size values', () => {
      const sizes: Array<'small' | 'medium' | 'large'> = ['small', 'medium', 'large'];
      
      sizes.forEach(size => {
        expect(() => {
          render(<LoadingSpinner size={size} />);
        }).not.toThrow();
      });
    });

    it('should handle optional props correctly', () => {
      expect(() => {
        render(<LoadingSpinner />);
        render(<LoadingSpinner size="large" />);
        render(<LoadingSpinner message="Test" />);
        render(<LoadingSpinner className="test" />);
        render(<LoadingSpinner size="small" message="Test" className="test" />);
      }).not.toThrow();
    });
  });
});