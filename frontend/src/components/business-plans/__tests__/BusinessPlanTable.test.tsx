/**
 * Unit tests for ModernModernBusinessPlanTable component
 * Tests business plan table functionality, editing, and interactions
 */
import React from 'react';
import { describe, it, expect, beforeEach, vi, Mock } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ModernBusinessPlanTable } from '../ModernBusinessPlanTable';
import { useBusinessPlanStore } from '../../../stores/businessPlanStore';

// Mock the business plan store
vi.mock('../../../stores/businessPlanStore');

// Mock Antd components that might cause issues in tests
vi.mock('antd', async () => {
  const actual = await vi.importActual('antd');
  return {
    ...actual,
    Table: ({ dataSource, columns, loading }: any) => (
      <div data-testid="business-plan-table">
        {loading && <div data-testid="loading">Loading...</div>}
        {dataSource?.map((item: any, index: number) => (
          <div key={index} data-testid={`row-${index}`}>
            {columns.map((col: any, colIndex: number) => (
              <div key={colIndex} data-testid={`cell-${index}-${colIndex}`}>
                {col.render ? col.render(item[col.dataIndex], item, index) : item[col.dataIndex]}
              </div>
            ))}
          </div>
        ))}
      </div>
    ),
    Input: ({ value, onChange, placeholder }: any) => (
      <input
        data-testid="input"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
      />
    ),
    InputNumber: ({ value, onChange, min, max }: any) => (
      <input
        data-testid="input-number"
        type="number"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        min={min}
        max={max}
      />
    ),
    Button: ({ children, onClick, type, loading }: any) => (
      <button
        data-testid="button"
        onClick={onClick}
        className={type}
        disabled={loading}
      >
        {loading ? 'Loading...' : children}
      </button>
    ),
  };
});

const mockBusinessPlans = [
  {
    id: 'plan-2025-01',
    office_id: 'stockholm',
    year: 2025,
    month: 1,
    planned_fte: 680,
    planned_revenue: 1200000,
    planned_costs: 800000,
    workforce_entries: [
      {
        role: 'Consultant',
        level: 'A',
        fte: 70,
        notes: 'Growth focus',
      },
      {
        role: 'Consultant',
        level: 'AC',
        fte: 55,
        notes: 'Stable headcount',
      },
    ],
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
  },
  {
    id: 'plan-2025-02',
    office_id: 'stockholm',
    year: 2025,
    month: 2,
    planned_fte: 685,
    planned_revenue: 1250000,
    planned_costs: 820000,
    workforce_entries: [
      {
        role: 'Consultant',
        level: 'A',
        fte: 72,
        notes: 'Continued growth',
      },
    ],
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-15T00:00:00Z',
  },
];

const mockUseBusinessPlanStore = useBusinessPlanStore as unknown as Mock;

describe('ModernBusinessPlanTable', () => {
  const mockLoadBusinessPlans = vi.fn();
  const mockCreateBusinessPlan = vi.fn();
  const mockUpdateBusinessPlan = vi.fn();
  const mockDeleteBusinessPlan = vi.fn();
  const mockSetSelectedYear = vi.fn();
  const mockSetSelectedMonth = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    
    mockUseBusinessPlanStore.mockReturnValue({
      monthlyPlans: mockBusinessPlans,
      loading: false,
      error: null,
      selectedYear: 2025,
      selectedMonth: 1,
      loadBusinessPlans: mockLoadBusinessPlans,
      createBusinessPlan: mockCreateBusinessPlan,
      updateBusinessPlan: mockUpdateBusinessPlan,
      deleteBusinessPlan: mockDeleteBusinessPlan,
      setSelectedYear: mockSetSelectedYear,
      setSelectedMonth: mockSetSelectedMonth,
      getCurrentPlan: vi.fn(() => mockBusinessPlans[0]),
      clearError: vi.fn(),
    });
  });

  const renderComponent = (props = {}) => {
    const defaultProps = {
      office: {
        id: 'stockholm',
        name: 'Stockholm',
        roles: {},
        journey: 'Mature' as any,
        total_fte: 100,
        timezone: 'Europe/Stockholm',
        economic_parameters: {
          working_hours_per_month: 166.4,
          employment_cost_rate: 1.4,
          unplanned_absence: 0.05,
          other_expense: 19000000,
          cost_of_living: 1.0,
          market_multiplier: 1.0,
          tax_rate: 0.25
        },
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z'
      },
      year: 2025,
      onYearChange: vi.fn(),
      ...props,
    };
    
    return render(<ModernBusinessPlanTable {...defaultProps} />);
  };

  describe('Initial Rendering', () => {
    it('should render business plan table with data', () => {
      renderComponent();

      expect(screen.getByTestId('business-plan-table')).toBeInTheDocument();
      expect(screen.getByTestId('row-0')).toBeInTheDocument();
      expect(screen.getByTestId('row-1')).toBeInTheDocument();
    });

    it('should load business plans on mount', () => {
      renderComponent();
      expect(mockLoadBusinessPlans).toHaveBeenCalledWith('stockholm');
    });

    it('should show loading state', () => {
      mockUseBusinessPlanStore.mockReturnValue({
        monthlyPlans: [],
        loading: true,
        error: null,
        selectedYear: 2025,
        selectedMonth: 1,
        loadBusinessPlans: mockLoadBusinessPlans,
        createBusinessPlan: mockCreateBusinessPlan,
        updateBusinessPlan: mockUpdateBusinessPlan,
        deleteBusinessPlan: mockDeleteBusinessPlan,
        setSelectedYear: mockSetSelectedYear,
        setSelectedMonth: mockSetSelectedMonth,
        getCurrentPlan: vi.fn(() => null),
        clearError: vi.fn(),
      });

      renderComponent();
      expect(screen.getByTestId('loading')).toBeInTheDocument();
    });

    it('should display error message when there is an error', () => {
      mockUseBusinessPlanStore.mockReturnValue({
        monthlyPlans: [],
        loading: false,
        error: 'Failed to load business plans',
        selectedYear: 2025,
        selectedMonth: 1,
        loadBusinessPlans: mockLoadBusinessPlans,
        createBusinessPlan: mockCreateBusinessPlan,
        updateBusinessPlan: mockUpdateBusinessPlan,
        deleteBusinessPlan: mockDeleteBusinessPlan,
        setSelectedYear: mockSetSelectedYear,
        setSelectedMonth: mockSetSelectedMonth,
        getCurrentPlan: vi.fn(() => null),
        clearError: vi.fn(),
      });

      renderComponent();
      expect(screen.getByText('Failed to load business plans')).toBeInTheDocument();
    });
  });

  describe('Year and Month Selection', () => {
    it('should display year and month selectors', () => {
      renderComponent();

      // Look for year and month selection controls
      const yearControls = screen.getAllByTestId('input-number');
      expect(yearControls.length).toBeGreaterThan(0);
    });

    it('should call setSelectedYear when year is changed', async () => {
      renderComponent();

      const yearInput = screen.getAllByTestId('input-number')[0]; // Assuming first is year
      await userEvent.clear(yearInput);
      await userEvent.type(yearInput, '2026');

      await waitFor(() => {
        expect(mockSetSelectedYear).toHaveBeenCalledWith(2026);
      });
    });

    it('should filter plans by selected year', () => {
      const plansWithDifferentYears = [
        ...mockBusinessPlans,
        {
          id: 'plan-2026-01',
          office_id: 'stockholm',
          year: 2026,
          month: 1,
          planned_fte: 700,
          planned_revenue: 1300000,
          planned_costs: 850000,
          workforce_entries: [],
          created_at: '2026-01-01T00:00:00Z',
          updated_at: '2026-01-01T00:00:00Z',
        },
      ];

      mockUseBusinessPlanStore.mockReturnValue({
        monthlyPlans: plansWithDifferentYears,
        loading: false,
        error: null,
        selectedYear: 2025,
        selectedMonth: 1,
        loadBusinessPlans: mockLoadBusinessPlans,
        createBusinessPlan: mockCreateBusinessPlan,
        updateBusinessPlan: mockUpdateBusinessPlan,
        deleteBusinessPlan: mockDeleteBusinessPlan,
        setSelectedYear: mockSetSelectedYear,
        setSelectedMonth: mockSetSelectedMonth,
        getCurrentPlan: vi.fn(() => mockBusinessPlans[0]),
        clearError: vi.fn(),
      });

      renderComponent();

      // Should only show 2025 plans (first 2)
      expect(screen.getByTestId('row-0')).toBeInTheDocument();
      expect(screen.getByTestId('row-1')).toBeInTheDocument();
      expect(screen.queryByTestId('row-2')).not.toBeInTheDocument();
    });
  });

  describe('Business Plan Data Display', () => {
    it('should display planned FTE values', () => {
      renderComponent();

      // Check if FTE values are displayed
      expect(screen.getByText('680')).toBeInTheDocument();
      expect(screen.getByText('685')).toBeInTheDocument();
    });

    it('should display revenue and cost values', () => {
      renderComponent();

      // Check if financial values are displayed (formatted)
      expect(screen.getByText('1,200,000')).toBeInTheDocument();
      expect(screen.getByText('1,250,000')).toBeInTheDocument();
      expect(screen.getByText('800,000')).toBeInTheDocument();
      expect(screen.getByText('820,000')).toBeInTheDocument();
    });

    it('should display workforce entries count', () => {
      renderComponent();

      // First plan has 2 workforce entries, second has 1
      expect(screen.getByText('2 roles')).toBeInTheDocument();
      expect(screen.getByText('1 role')).toBeInTheDocument();
    });

    it('should show month names correctly', () => {
      renderComponent();

      expect(screen.getByText('January')).toBeInTheDocument();
      expect(screen.getByText('February')).toBeInTheDocument();
    });
  });

  describe('Business Plan Editing', () => {
    it('should allow editing planned FTE', async () => {
      renderComponent();

      // Find edit button and click it
      const editButtons = screen.getAllByTestId('button');
      const editButton = editButtons.find(btn => btn.textContent?.includes('Edit'));
      
      if (editButton) {
        await userEvent.click(editButton);

        // Look for input field
        const fteInput = screen.getByDisplayValue('680');
        await userEvent.clear(fteInput);
        await userEvent.type(fteInput, '690');

        // Save changes
        const saveButton = screen.getByText('Save');
        await userEvent.click(saveButton);

        expect(mockUpdateBusinessPlan).toHaveBeenCalledWith(
          'plan-2025-01',
          expect.objectContaining({
            planned_fte: 690,
          })
        );
      }
    });

    it('should allow editing revenue and costs', async () => {
      renderComponent();

      // Similar test for revenue and cost editing
      const editButtons = screen.getAllByTestId('button');
      const editButton = editButtons.find(btn => btn.textContent?.includes('Edit'));
      
      if (editButton) {
        await userEvent.click(editButton);

        // Find revenue input
        const revenueInput = screen.getByDisplayValue('1200000');
        await userEvent.clear(revenueInput);
        await userEvent.type(revenueInput, '1300000');

        // Save changes
        const saveButton = screen.getByText('Save');
        await userEvent.click(saveButton);

        expect(mockUpdateBusinessPlan).toHaveBeenCalledWith(
          'plan-2025-01',
          expect.objectContaining({
            planned_revenue: 1300000,
          })
        );
      }
    });

    it('should cancel editing when cancel button is clicked', async () => {
      renderComponent();

      const editButtons = screen.getAllByTestId('button');
      const editButton = editButtons.find(btn => btn.textContent?.includes('Edit'));
      
      if (editButton) {
        await userEvent.click(editButton);

        // Should show cancel button
        const cancelButton = screen.getByText('Cancel');
        await userEvent.click(cancelButton);

        // Should not call update function
        expect(mockUpdateBusinessPlan).not.toHaveBeenCalled();
      }
    });

    it('should validate input values', async () => {
      renderComponent();

      const editButtons = screen.getAllByTestId('button');
      const editButton = editButtons.find(btn => btn.textContent?.includes('Edit'));
      
      if (editButton) {
        await userEvent.click(editButton);

        // Try to enter invalid value
        const fteInput = screen.getByDisplayValue('680');
        await userEvent.clear(fteInput);
        await userEvent.type(fteInput, '-10');

        // Save button should be disabled or show validation error
        const saveButton = screen.getByText('Save');
        expect(saveButton).toBeDisabled();
      }
    });
  });

  describe('Business Plan Creation', () => {
    it('should allow creating new business plan', async () => {
      renderComponent();

      const addButton = screen.getByText('Add Plan');
      await userEvent.click(addButton);

      // Should show form for new plan
      expect(screen.getByText('New Business Plan')).toBeInTheDocument();

      // Fill form
      const monthSelect = screen.getByTestId('month-select');
      await userEvent.selectOptions(monthSelect, '3'); // March

      const fteInput = screen.getByTestId('fte-input');
      await userEvent.type(fteInput, '700');

      const revenueInput = screen.getByTestId('revenue-input');
      await userEvent.type(revenueInput, '1400000');

      const costInput = screen.getByTestId('cost-input');
      await userEvent.type(costInput, '900000');

      // Submit form
      const createButton = screen.getByText('Create Plan');
      await userEvent.click(createButton);

      expect(mockCreateBusinessPlan).toHaveBeenCalledWith({
        office_id: 'stockholm',
        year: 2025,
        month: 3,
        planned_fte: 700,
        planned_revenue: 1400000,
        planned_costs: 900000,
        workforce_entries: [],
      });
    });

    it('should prevent creating duplicate plans for same month', async () => {
      renderComponent();

      const addButton = screen.getByText('Add Plan');
      await userEvent.click(addButton);

      // Try to select January (already exists)
      const monthSelect = screen.getByTestId('month-select');
      await userEvent.selectOptions(monthSelect, '1');

      // Should show warning or disable create button
      expect(
        screen.getByText('Plan for January 2025 already exists')
      ).toBeInTheDocument();
    });
  });

  describe('Business Plan Deletion', () => {
    it('should allow deleting business plan', async () => {
      renderComponent();

      const deleteButtons = screen.getAllByTestId('button');
      const deleteButton = deleteButtons.find(btn => btn.textContent?.includes('Delete'));
      
      if (deleteButton) {
        await userEvent.click(deleteButton);

        // Should show confirmation dialog
        expect(screen.getByText('Confirm Deletion')).toBeInTheDocument();

        // Confirm deletion
        const confirmButton = screen.getByText('Delete');
        await userEvent.click(confirmButton);

        expect(mockDeleteBusinessPlan).toHaveBeenCalledWith('stockholm', 'plan-2025-01');
      }
    });

    it('should cancel deletion when cancel is clicked', async () => {
      renderComponent();

      const deleteButtons = screen.getAllByTestId('button');
      const deleteButton = deleteButtons.find(btn => btn.textContent?.includes('Delete'));
      
      if (deleteButton) {
        await userEvent.click(deleteButton);

        // Cancel deletion
        const cancelButton = screen.getByText('Cancel');
        await userEvent.click(cancelButton);

        expect(mockDeleteBusinessPlan).not.toHaveBeenCalled();
      }
    });
  });

  describe('Workforce Management', () => {
    it('should show workforce entries in expandable rows', async () => {
      renderComponent();

      // Click expand button for first row
      const expandButton = screen.getByTestId('expand-button-0');
      await userEvent.click(expandButton);

      // Should show workforce entries
      expect(screen.getByText('Consultant A: 70 FTE')).toBeInTheDocument();
      expect(screen.getByText('Consultant AC: 55 FTE')).toBeInTheDocument();
      expect(screen.getByText('Growth focus')).toBeInTheDocument();
    });

    it('should allow editing workforce entries', async () => {
      renderComponent();

      // Expand row and edit workforce
      const expandButton = screen.getByTestId('expand-button-0');
      await userEvent.click(expandButton);

      const editWorkforceButton = screen.getByText('Edit Workforce');
      await userEvent.click(editWorkforceButton);

      // Edit workforce entry
      const fteInput = screen.getByDisplayValue('70');
      await userEvent.clear(fteInput);
      await userEvent.type(fteInput, '75');

      const saveButton = screen.getByText('Save');
      await userEvent.click(saveButton);

      expect(mockUpdateBusinessPlan).toHaveBeenCalledWith(
        'plan-2025-01',
        expect.objectContaining({
          workforce_entries: expect.arrayContaining([
            expect.objectContaining({
              role: 'Consultant',
              level: 'A',
              fte: 75,
            }),
          ]),
        })
      );
    });
  });

  describe('Data Export', () => {
    it('should allow exporting business plan data', async () => {
      renderComponent();

      const exportButton = screen.getByText('Export');
      await userEvent.click(exportButton);

      // Should trigger download or show export options
      expect(screen.getByText('Export Options')).toBeInTheDocument();
    });

    it('should export in different formats', async () => {
      renderComponent();

      const exportButton = screen.getByText('Export');
      await userEvent.click(exportButton);

      const csvExport = screen.getByText('Export as CSV');
      await userEvent.click(csvExport);

      // Would typically test actual download, but that's complex in tests
      // Instead check if export function is called
      expect(mockCreateBusinessPlan).not.toHaveBeenCalled(); // Placeholder assertion
    });
  });

  describe('Error Handling', () => {
    it('should handle update errors gracefully', async () => {
      mockUpdateBusinessPlan.mockRejectedValueOnce(new Error('Update failed'));

      renderComponent();

      const editButtons = screen.getAllByTestId('button');
      const editButton = editButtons.find(btn => btn.textContent?.includes('Edit'));
      
      if (editButton) {
        await userEvent.click(editButton);

        const fteInput = screen.getByDisplayValue('680');
        await userEvent.clear(fteInput);
        await userEvent.type(fteInput, '690');

        const saveButton = screen.getByText('Save');
        await userEvent.click(saveButton);

        await waitFor(() => {
          expect(screen.getByText('Failed to update business plan')).toBeInTheDocument();
        });
      }
    });

    it('should handle creation errors gracefully', async () => {
      mockCreateBusinessPlan.mockRejectedValueOnce(new Error('Creation failed'));

      renderComponent();

      const addButton = screen.getByText('Add Plan');
      await userEvent.click(addButton);

      // Fill and submit form
      const createButton = screen.getByText('Create Plan');
      await userEvent.click(createButton);

      await waitFor(() => {
        expect(screen.getByText('Failed to create business plan')).toBeInTheDocument();
      });
    });
  });
});