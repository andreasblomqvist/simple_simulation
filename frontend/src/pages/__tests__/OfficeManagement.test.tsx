/**
 * Unit tests for OfficeManagement component
 * Tests office management page functionality, routing, and interactions
 */
import React from 'react';
import { describe, it, expect, beforeEach, vi, Mock } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter, MemoryRouter } from 'react-router-dom';
import { OfficeManagement } from '../OfficeManagement';
import { useOfficeStore } from '../../stores/officeStore';
import { OfficeJourney } from '../../types/office';

// Mock the office store
vi.mock('../../stores/officeStore');

// Mock the office components
vi.mock('../../components/offices/OfficeSidebar', () => ({
  OfficeSidebar: ({ onOfficeSelect, selectedOfficeId }: any) => (
    <div data-testid="office-sidebar">
      <button 
        data-testid="select-office-stockholm"
        onClick={() => onOfficeSelect('stockholm')}
      >
        Select Stockholm
      </button>
      <button 
        data-testid="select-office-munich"
        onClick={() => onOfficeSelect('munich')}
      >
        Select Munich
      </button>
      <div data-testid="selected-office">{selectedOfficeId}</div>
    </div>
  ),
}));

vi.mock('../../components/office-config/OfficeConfigPage', () => ({
  OfficeConfigPage: ({ office, onOfficeUpdate }: any) => (
    <div data-testid="office-config">
      <div data-testid="office-name">{office?.name}</div>
      <button 
        data-testid="update-office"
        onClick={() => onOfficeUpdate({ ...office, name: `${office.name} Updated` })}
      >
        Update Office
      </button>
    </div>
  ),
}));

vi.mock('../../components/ui/LoadingSpinner', () => ({
  LoadingSpinner: ({ message }: any) => (
    <div data-testid="loading-spinner">{message}</div>
  ),
}));

vi.mock('../../components/ui/ErrorBoundary', () => ({
  ErrorBoundary: ({ children }: any) => <div>{children}</div>,
}));

const mockOffices = [
  {
    id: 'stockholm',
    name: 'Stockholm',
    journey: OfficeJourney.MATURE,
    timezone: 'Europe/Stockholm',
    economic_parameters: {
      cost_of_living: 1.0,
      market_multiplier: 1.0,
      tax_rate: 0.25,
    },
    total_fte: 679,
    roles: {},
  },
  {
    id: 'munich',
    name: 'Munich',
    journey: OfficeJourney.ESTABLISHED,
    timezone: 'Europe/Berlin',
    economic_parameters: {
      cost_of_living: 1.1,
      market_multiplier: 1.2,
      tax_rate: 0.28,
    },
    total_fte: 332,
    roles: {},
  },
];

const mockUseOfficeStore = useOfficeStore as Mock;

describe('OfficeManagement', () => {
  const mockLoadOffices = vi.fn();
  const mockSelectOffice = vi.fn();
  const mockUpdateOffice = vi.fn();
  const mockClearError = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    
    mockUseOfficeStore.mockReturnValue({
      offices: mockOffices,
      currentOffice: null,
      loading: false,
      error: null,
      officesByJourney: {
        [OfficeJourney.MATURE]: [mockOffices[0]],
        [OfficeJourney.ESTABLISHED]: [mockOffices[1]],
        [OfficeJourney.EMERGING]: [],
      },
      loadOffices: mockLoadOffices,
      selectOffice: mockSelectOffice,
      updateOffice: mockUpdateOffice,
      clearError: mockClearError,
    });
  });

  const renderComponent = (officeId?: string) => {
    const initialEntries = officeId ? [`/offices/${officeId}`] : ['/offices'];
    return render(
      <MemoryRouter initialEntries={initialEntries}>
        <OfficeManagement />
      </MemoryRouter>
    );
  };

  describe('Initial Loading', () => {
    it('should load offices on mount', () => {
      renderComponent();
      expect(mockLoadOffices).toHaveBeenCalledTimes(1);
    });

    it('should show loading spinner while loading', () => {
      mockUseOfficeStore.mockReturnValue({
        offices: [],
        currentOffice: null,
        loading: true,
        error: null,
        officesByJourney: {
          [OfficeJourney.MATURE]: [],
          [OfficeJourney.ESTABLISHED]: [],
          [OfficeJourney.EMERGING]: [],
        },
        loadOffices: mockLoadOffices,
        selectOffice: mockSelectOffice,
        updateOffice: mockUpdateOffice,
        clearError: mockClearError,
      });

      renderComponent();
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
      expect(screen.getByText('Loading offices...')).toBeInTheDocument();
    });

    it('should show error message when there is an error', () => {
      mockUseOfficeStore.mockReturnValue({
        offices: [],
        currentOffice: null,
        loading: false,
        error: 'Failed to load offices',
        officesByJourney: {
          [OfficeJourney.MATURE]: [],
          [OfficeJourney.ESTABLISHED]: [],
          [OfficeJourney.EMERGING]: [],
        },
        loadOffices: mockLoadOffices,
        selectOffice: mockSelectOffice,
        updateOffice: mockUpdateOffice,
        clearError: mockClearError,
      });

      renderComponent();
      expect(screen.getByText('Error Loading Offices')).toBeInTheDocument();
      expect(screen.getByText('Failed to load offices')).toBeInTheDocument();
      expect(screen.getByText('Retry')).toBeInTheDocument();
    });

    it('should retry loading when retry button is clicked', () => {
      mockUseOfficeStore.mockReturnValue({
        offices: [],
        currentOffice: null,
        loading: false,
        error: 'Failed to load offices',
        officesByJourney: {
          [OfficeJourney.MATURE]: [],
          [OfficeJourney.ESTABLISHED]: [],
          [OfficeJourney.EMERGING]: [],
        },
        loadOffices: mockLoadOffices,
        selectOffice: mockSelectOffice,
        updateOffice: mockUpdateOffice,
        clearError: mockClearError,
      });

      renderComponent();
      
      const retryButton = screen.getByText('Retry');
      fireEvent.click(retryButton);
      
      expect(mockLoadOffices).toHaveBeenCalledTimes(2); // Once on mount, once on retry
    });
  });

  describe('Office Selection from URL', () => {
    it('should select office when officeId is in URL', async () => {
      renderComponent('stockholm');
      
      await waitFor(() => {
        expect(mockSelectOffice).toHaveBeenCalledWith('stockholm');
      });
    });

    it('should redirect to first office when requested office is not found', async () => {
      const mockNavigate = vi.fn();
      
      // Mock useNavigate
      vi.mock('react-router-dom', async () => {
        const actual = await vi.importActual('react-router-dom');
        return {
          ...actual,
          useNavigate: () => mockNavigate,
        };
      });

      renderComponent('nonexistent');
      
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/offices/stockholm');
      });
    });
  });

  describe('Office Management Interface', () => {
    it('should show debug information when no office is selected', () => {
      renderComponent();
      
      expect(screen.getByText('Office Management - DEBUG VERSION')).toBeInTheDocument();
      expect(screen.getByText('Debug Information:')).toBeInTheDocument();
      expect(screen.getByText('Offices loaded: 2')).toBeInTheDocument();
      expect(screen.getByText('Current office: None')).toBeInTheDocument();
    });

    it('should show office list with clickable buttons', () => {
      renderComponent();
      
      expect(screen.getByText('Available Offices (2):')).toBeInTheDocument();
      expect(screen.getByText('Stockholm (mature)')).toBeInTheDocument();
      expect(screen.getByText('Munich (established)')).toBeInTheDocument();
    });

    it('should handle office selection through button clicks', () => {
      const mockNavigate = vi.fn();
      
      // Mock useNavigate for this test
      vi.doMock('react-router-dom', async () => {
        const actual = await vi.importActual('react-router-dom');
        return {
          ...actual,
          useNavigate: () => mockNavigate,
        };
      });

      renderComponent();
      
      const stockholmButton = screen.getByText('Stockholm (mature)');
      fireEvent.click(stockholmButton);
      
      expect(mockSelectOffice).toHaveBeenCalledWith('stockholm');
    });

    it('should show selected office details when office is selected', () => {
      mockUseOfficeStore.mockReturnValue({
        offices: mockOffices,
        currentOffice: mockOffices[0], // Stockholm selected
        loading: false,
        error: null,
        officesByJourney: {
          [OfficeJourney.MATURE]: [mockOffices[0]],
          [OfficeJourney.ESTABLISHED]: [mockOffices[1]],
          [OfficeJourney.EMERGING]: [],
        },
        loadOffices: mockLoadOffices,
        selectOffice: mockSelectOffice,
        updateOffice: mockUpdateOffice,
        clearError: mockClearError,
      });

      renderComponent();
      
      expect(screen.getByText('Selected Office: Stockholm')).toBeInTheDocument();
      expect(screen.getByText('Journey: mature')).toBeInTheDocument();
      expect(screen.getByText('Timezone: Europe/Stockholm')).toBeInTheDocument();
      expect(screen.getByTestId('office-config')).toBeInTheDocument();
    });

    it('should handle office updates', () => {
      mockUseOfficeStore.mockReturnValue({
        offices: mockOffices,
        currentOffice: mockOffices[0], // Stockholm selected
        loading: false,
        error: null,
        officesByJourney: {
          [OfficeJourney.MATURE]: [mockOffices[0]],
          [OfficeJourney.ESTABLISHED]: [mockOffices[1]],
          [OfficeJourney.EMERGING]: [],
        },
        loadOffices: mockLoadOffices,
        selectOffice: mockSelectOffice,
        updateOffice: mockUpdateOffice,
        clearError: mockClearError,
      });

      renderComponent();
      
      const updateButton = screen.getByTestId('update-office');
      fireEvent.click(updateButton);
      
      expect(mockUpdateOffice).toHaveBeenCalledWith({
        ...mockOffices[0],
        name: 'Stockholm Updated',
      });
    });
  });

  describe('Responsive Design', () => {
    it('should handle mobile viewport correctly', () => {
      // Mock window.innerWidth for mobile
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 500,
      });

      renderComponent();
      
      // Trigger resize event
      fireEvent(window, new Event('resize'));
      
      // Component should still render correctly on mobile
      expect(screen.getByText('Office Management - DEBUG VERSION')).toBeInTheDocument();
    });
  });

  describe('Empty States', () => {
    it('should show message when no offices are loaded', () => {
      mockUseOfficeStore.mockReturnValue({
        offices: [],
        currentOffice: null,
        loading: false,
        error: null,
        officesByJourney: {
          [OfficeJourney.MATURE]: [],
          [OfficeJourney.ESTABLISHED]: [],
          [OfficeJourney.EMERGING]: [],
        },
        loadOffices: mockLoadOffices,
        selectOffice: mockSelectOffice,
        updateOffice: mockUpdateOffice,
        clearError: mockClearError,
      });

      renderComponent();
      
      expect(screen.getByText('No Offices Found')).toBeInTheDocument();
      expect(screen.getByText('No offices have been loaded. This might indicate an API issue.')).toBeInTheDocument();
      expect(screen.getByText('Reload Offices')).toBeInTheDocument();
    });

    it('should show message when no office is selected but offices are available', () => {
      renderComponent();
      
      expect(screen.getByText('No Office Selected')).toBeInTheDocument();
      expect(screen.getByText('Please select an office from the list above to view its configuration.')).toBeInTheDocument();
    });
  });
});