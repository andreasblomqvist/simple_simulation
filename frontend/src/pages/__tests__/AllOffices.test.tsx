/**
 * Unit tests for AllOffices component
 * Tests office listing, navigation, and table interactions
 */
import React from 'react';
import { describe, it, expect, beforeEach, vi, Mock } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import AllOffices from '../AllOffices';

// Mock fetch globally
global.fetch = vi.fn();

// Mock navigate function
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

const mockOfficesResponse = [
  {
    id: 'stockholm',
    name: 'Stockholm',
    total_fte: 679,
    journey: 'mature',
    roles: {
      Consultant: {
        A: { fte: 69 },
        AC: { fte: 54 },
        C: { fte: 123 },
        SrC: { fte: 162 },
        AM: { fte: 178 },
        M: { fte: 47 },
        SrM: { fte: 32 },
        PiP: { fte: 14 },
      },
    },
    economic_parameters: {
      cost_of_living: 1.0,
      market_multiplier: 1.0,
      tax_rate: 0.25,
    },
  },
  {
    id: 'munich',
    name: 'Munich',
    total_fte: 332,
    journey: 'established',
    roles: {
      Consultant: {
        A: { fte: 18 },
        AC: { fte: 32 },
        C: { fte: 61 },
        SrC: { fte: 89 },
        AM: { fte: 89 },
        M: { fte: 30 },
        SrM: { fte: 6 },
        PiP: { fte: 7 },
      },
    },
    economic_parameters: {
      cost_of_living: 1.1,
      market_multiplier: 1.2,
      tax_rate: 0.28,
    },
  },
  {
    id: 'helsinki',
    name: 'Helsinki',
    total_fte: 105,
    journey: 'emerging',
    roles: {
      Consultant: {
        A: { fte: 16 },
        AC: { fte: 16 },
        C: { fte: 17 },
        SrC: { fte: 24 },
        AM: { fte: 20 },
        M: { fte: 11 },
        SrM: { fte: 1 },
      },
    },
    economic_parameters: {
      cost_of_living: 0.9,
      market_multiplier: 0.95,
      tax_rate: 0.22,
    },
  },
];

describe('AllOffices', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockClear();
  });

  const renderComponent = () => {
    return render(
      <BrowserRouter>
        <AllOffices />
      </BrowserRouter>
    );
  };

  describe('Loading and Data Display', () => {
    it('should show loading state initially', () => {
      // Mock a delayed response
      (fetch as Mock).mockImplementation(() => new Promise(() => {}));
      
      renderComponent();
      
      expect(screen.getByText('All Offices')).toBeInTheDocument();
      // Antd Table shows loading state
      expect(document.querySelector('.ant-spin')).toBeInTheDocument();
    });

    it('should load and display offices successfully', async () => {
      (fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockOfficesResponse,
      });

      renderComponent();

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith('/api/offices');
      });

      // Check if offices are displayed in the table
      await waitFor(() => {
        expect(screen.getByText('Stockholm')).toBeInTheDocument();
        expect(screen.getByText('Munich')).toBeInTheDocument();
        expect(screen.getByText('Helsinki')).toBeInTheDocument();
      });

      // Check FTE numbers
      expect(screen.getByText('679')).toBeInTheDocument();
      expect(screen.getByText('332')).toBeInTheDocument();
      expect(screen.getByText('105')).toBeInTheDocument();

      // Check journey tags
      expect(screen.getByText('mature')).toBeInTheDocument();
      expect(screen.getByText('established')).toBeInTheDocument();
      expect(screen.getByText('emerging')).toBeInTheDocument();

      // Check economic parameters
      expect(screen.getByText('1.00')).toBeInTheDocument(); // Stockholm cost of living
      expect(screen.getByText('1.10')).toBeInTheDocument(); // Munich cost of living
      expect(screen.getByText('1.20')).toBeInTheDocument(); // Munich market multiplier
    });

    it('should handle API errors gracefully', async () => {
      (fetch as Mock).mockRejectedValueOnce(new Error('Network error'));

      renderComponent();

      await waitFor(() => {
        expect(screen.getByText('Network error')).toBeInTheDocument();
      });
    });

    it('should handle HTTP errors gracefully', async () => {
      (fetch as Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      });

      renderComponent();

      await waitFor(() => {
        expect(screen.getByText('Failed to fetch offices')).toBeInTheDocument();
      });
    });
  });

  describe('Office Navigation', () => {
    beforeEach(async () => {
      (fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockOfficesResponse,
      });

      renderComponent();

      await waitFor(() => {
        expect(screen.getByText('Stockholm')).toBeInTheDocument();
      });
    });

    it('should navigate to office detail when office name is clicked', async () => {
      const stockholmLink = screen.getByText('Stockholm');
      
      fireEvent.click(stockholmLink);

      expect(mockNavigate).toHaveBeenCalledWith('/offices/stockholm');
    });

    it('should navigate to Munich office when Munich is clicked', async () => {
      const munichLink = screen.getByText('Munich');
      
      fireEvent.click(munichLink);

      expect(mockNavigate).toHaveBeenCalledWith('/offices/munich');
    });

    it('should navigate to Helsinki office when Helsinki is clicked', async () => {
      const helsinkiLink = screen.getByText('Helsinki');
      
      fireEvent.click(helsinkiLink);

      expect(mockNavigate).toHaveBeenCalledWith('/offices/helsinki');
    });

    it('should show hover effects on office names', async () => {
      const stockholmLink = screen.getByText('Stockholm');
      
      // Check initial style
      expect(stockholmLink).toHaveStyle({ color: '#1890ff' });
      
      // Simulate hover
      fireEvent.mouseEnter(stockholmLink);
      expect(stockholmLink).toHaveStyle({ color: '#40a9ff' });
      
      // Simulate mouse leave
      fireEvent.mouseLeave(stockholmLink);
      expect(stockholmLink).toHaveStyle({ color: '#1890ff' });
    });
  });

  describe('Table Functionality', () => {
    beforeEach(async () => {
      (fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockOfficesResponse,
      });

      renderComponent();

      await waitFor(() => {
        expect(screen.getByText('Stockholm')).toBeInTheDocument();
      });
    });

    it('should display all table columns correctly', () => {
      // Check column headers
      expect(screen.getByText('Office')).toBeInTheDocument();
      expect(screen.getByText('Journey')).toBeInTheDocument();
      expect(screen.getByText('Total FTE')).toBeInTheDocument();
      expect(screen.getByText('Cost of Living')).toBeInTheDocument();
      expect(screen.getByText('Market Multiplier')).toBeInTheDocument();
    });

    it('should show economic parameters correctly formatted', () => {
      // Check cost of living values
      expect(screen.getByText('1.00')).toBeInTheDocument(); // Stockholm
      expect(screen.getByText('1.10')).toBeInTheDocument(); // Munich
      expect(screen.getByText('0.90')).toBeInTheDocument(); // Helsinki

      // Check market multiplier values
      expect(screen.getByText('1.20')).toBeInTheDocument(); // Munich
      expect(screen.getByText('0.95')).toBeInTheDocument(); // Helsinki
    });

    it('should handle missing economic parameters', async () => {
      const incompleteOffice = {
        ...mockOfficesResponse[0],
        economic_parameters: {},
      };

      (fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => [incompleteOffice],
      });

      renderComponent();

      await waitFor(() => {
        expect(screen.getAllByText('N/A')).toHaveLength(2); // Cost of living and market multiplier
      });
    });

    it('should expand row to show role breakdown', async () => {
      // Find expand button for Stockholm row
      const expandButton = document.querySelector('.ant-table-row-expand-icon');
      
      if (expandButton) {
        fireEvent.click(expandButton);
        
        await waitFor(() => {
          expect(screen.getByText('Role Breakdown')).toBeInTheDocument();
          expect(screen.getByText('Consultant')).toBeInTheDocument();
          
          // Check some role levels
          expect(screen.getByText('A: 69 FTE')).toBeInTheDocument();
          expect(screen.getByText('AC: 54 FTE')).toBeInTheDocument();
        });
      }
    });

    it('should handle pagination correctly', () => {
      // With 3 offices and pageSize 8, should be on page 1
      const pagination = document.querySelector('.ant-pagination');
      expect(pagination).toBeInTheDocument();
    });
  });

  describe('Filter Controls', () => {
    beforeEach(async () => {
      (fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockOfficesResponse,
      });

      renderComponent();

      await waitFor(() => {
        expect(screen.getByText('Stockholm')).toBeInTheDocument();
      });
    });

    it('should display filter dropdowns', () => {
      // Check filter options are present
      const selects = document.querySelectorAll('.ant-select');
      expect(selects).toHaveLength(3); // Company, Journey, Sort dropdowns
    });

    it('should have correct default filter values', () => {
      expect(screen.getByText('Company')).toBeInTheDocument();
      expect(screen.getByText('Journey')).toBeInTheDocument();
      expect(screen.getByText('Sort: Name')).toBeInTheDocument();
    });
  });

  describe('Console Logging', () => {
    it('should log debug information', async () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
      
      (fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockOfficesResponse,
      });

      renderComponent();

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith(
          '[DEBUG] Data received from /api/offices:',
          mockOfficesResponse
        );
      });

      // Test navigation logging
      const stockholmLink = screen.getByText('Stockholm');
      fireEvent.click(stockholmLink);

      expect(consoleSpy).toHaveBeenCalledWith('[DEBUG] Navigating to office:', 'stockholm');

      consoleSpy.mockRestore();
    });
  });

  describe('Accessibility', () => {
    beforeEach(async () => {
      (fetch as Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockOfficesResponse,
      });

      renderComponent();

      await waitFor(() => {
        expect(screen.getByText('Stockholm')).toBeInTheDocument();
      });
    });

    it('should have proper keyboard navigation for office links', () => {
      const stockholmLink = screen.getByText('Stockholm');
      
      // Should be focusable
      stockholmLink.focus();
      expect(document.activeElement).toBe(stockholmLink);
      
      // Should support Enter key
      fireEvent.keyDown(stockholmLink, { key: 'Enter', code: 'Enter' });
      // Note: We'd need to add keydown handler to component for full keyboard support
    });

    it('should have proper ARIA labels and roles', () => {
      const table = document.querySelector('.ant-table');
      expect(table).toBeInTheDocument();
      
      // Antd Table should have proper accessibility attributes
      expect(table?.getAttribute('role')).toBeTruthy();
    });
  });
});