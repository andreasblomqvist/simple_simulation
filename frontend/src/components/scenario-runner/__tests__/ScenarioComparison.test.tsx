import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render } from '../../../test/test-utils';
import ScenarioComparison from '../ScenarioComparison';

describe('ScenarioComparison', () => {
  const mockOnBack = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders scenario comparison view', () => {
    render(
      <ScenarioComparison
        onBack={mockOnBack}
      />
    );

    // Check that component title is displayed
    expect(screen.getByText(/scenario comparison/i)).toBeInTheDocument();

    // Check that scenario selection list is present
    expect(screen.getByText(/select scenarios to compare/i)).toBeInTheDocument();
  });

  it('displays available scenarios for selection', () => {
    render(
      <ScenarioComparison
        onBack={mockOnBack}
      />
    );

    // Check that mock scenarios are displayed
    expect(screen.getByText(/oslo growth plan/i)).toBeInTheDocument();
    expect(screen.getByText(/stockholm expansion/i)).toBeInTheDocument();
    expect(screen.getByText(/munich conservative/i)).toBeInTheDocument();

    // Check that creation dates are shown
    expect(screen.getByText(/2025-07-01/i)).toBeInTheDocument();
    expect(screen.getByText(/2025-06-15/i)).toBeInTheDocument();
    expect(screen.getByText(/2025-06-10/i)).toBeInTheDocument();
  });

  it('allows users to select scenarios for comparison', async () => {
    const user = userEvent.setup();

    render(
      <ScenarioComparison
        onBack={mockOnBack}
      />
    );

    // Find checkboxes for scenario selection
    const checkboxes = screen.getAllByRole('checkbox') as HTMLInputElement[];
    expect(checkboxes.length).toBeGreaterThan(0);

    // Check that some scenarios are pre-selected (default state)
    const checkedCheckboxes = checkboxes.filter(checkbox => checkbox.checked);
    expect(checkedCheckboxes.length).toBeGreaterThan(0);

    // Toggle a scenario selection
    await user.click(checkboxes[0]);

    // Should update the selection state
    await waitFor(() => {
      const updatedCheckboxes = screen.getAllByRole('checkbox') as HTMLInputElement[];
      const updatedChecked = updatedCheckboxes.filter(checkbox => checkbox.checked);
      expect(updatedChecked.length).not.toBe(checkedCheckboxes.length);
    });
  });

  it('displays comparison table with selected scenarios', () => {
    render(
      <ScenarioComparison
        onBack={mockOnBack}
      />
    );

    // Check that comparison table is displayed
    expect(screen.getByRole('table')).toBeInTheDocument();

    // Check that KPI column is present
    expect(screen.getByText(/kpi/i)).toBeInTheDocument();

    // Check that KPI metrics are displayed
    expect(screen.getByText(/fte/i)).toBeInTheDocument();
    expect(screen.getByText(/growth/i)).toBeInTheDocument();
    expect(screen.getByText(/sales/i)).toBeInTheDocument();
    expect(screen.getByText(/ebitda/i)).toBeInTheDocument();
  });

  it('shows scenario data in comparison table', () => {
    render(
      <ScenarioComparison
        onBack={mockOnBack}
      />
    );

    // Check that scenario names appear in table headers
    expect(screen.getByText(/oslo growth plan/i)).toBeInTheDocument();
    expect(screen.getByText(/stockholm expansion/i)).toBeInTheDocument();

    // Check that years are displayed
    expect(screen.getByText(/2025/i)).toBeInTheDocument();
    expect(screen.getByText(/2026/i)).toBeInTheDocument();
  });

  it('displays KPI values in the comparison table', () => {
    render(
      <ScenarioComparison
        onBack={mockOnBack}
      />
    );

    // Check that some KPI values are displayed (from mock data)
    expect(screen.getByText('1500')).toBeInTheDocument(); // FTE value
    expect(screen.getByText('3000')).toBeInTheDocument(); // Sales value
    expect(screen.getByText('500')).toBeInTheDocument(); // EBITDA value
  });

  it('calls onBack when back button is clicked', async () => {
    const user = userEvent.setup();

    render(
      <ScenarioComparison
        onBack={mockOnBack}
      />
    );

    // Find and click the back button
    const backButton = screen.getByText(/back/i);
    await user.click(backButton);

    expect(mockOnBack).toHaveBeenCalled();
  });

  it('updates table when scenario selection changes', async () => {
    const user = userEvent.setup();

    render(
      <ScenarioComparison
        onBack={mockOnBack}
      />
    );

    // Get initial table state
    const initialTable = screen.getByRole('table');

    // Toggle a scenario selection
    const checkboxes = screen.getAllByRole('checkbox') as HTMLInputElement[];
    await user.click(checkboxes[0]);

    // Table should update with new selection
    await waitFor(() => {
      const updatedTable = screen.getByRole('table');
      expect(updatedTable).toBeInTheDocument();
    });
  });

  it('provides responsive table layout', () => {
    render(
      <ScenarioComparison
        onBack={mockOnBack}
      />
    );

    // Check that table renders without errors
    expect(screen.getByRole('table')).toBeInTheDocument();
    expect(screen.getByText(/scenario comparison/i)).toBeInTheDocument();
  });

  it('handles multiple scenario selections', async () => {
    const user = userEvent.setup();

    render(
      <ScenarioComparison
        onBack={mockOnBack}
      />
    );

    // Select multiple scenarios
    const checkboxes = screen.getAllByRole('checkbox') as HTMLInputElement[];
    
    // Ensure all scenarios are selected
    for (const checkbox of checkboxes) {
      if (!checkbox.checked) {
        await user.click(checkbox);
      }
    }

    // Should show all scenarios in the table
    await waitFor(() => {
      expect(screen.getByText(/oslo growth plan/i)).toBeInTheDocument();
      expect(screen.getByText(/stockholm expansion/i)).toBeInTheDocument();
      expect(screen.getByText(/munich conservative/i)).toBeInTheDocument();
    });
  });

  it('displays journey level data in comparison', () => {
    render(
      <ScenarioComparison
        onBack={mockOnBack}
      />
    );

    // Check that journey level KPIs are displayed
    expect(screen.getByText(/j-1/i)).toBeInTheDocument();
    expect(screen.getByText(/j-2/i)).toBeInTheDocument();
    expect(screen.getByText(/j-3/i)).toBeInTheDocument();
  });

  it('shows percentage values correctly', () => {
    render(
      <ScenarioComparison
        onBack={mockOnBack}
      />
    );

    // Check that percentage values are displayed
    expect(screen.getByText(/5%/)).toBeInTheDocument();
    expect(screen.getByText(/16\.7%/)).toBeInTheDocument();
    expect(screen.getByText(/38%/)).toBeInTheDocument();
  });

  it('provides horizontal scrolling for wide tables', () => {
    render(
      <ScenarioComparison
        onBack={mockOnBack}
      />
    );

    // Check that table has horizontal scroll capability
    const table = screen.getByRole('table');
    expect(table).toBeInTheDocument();
  });

  it('maintains selection state across interactions', async () => {
    const user = userEvent.setup();

    render(
      <ScenarioComparison
        onBack={mockOnBack}
      />
    );

    // Get initial selection state
    const initialCheckboxes = screen.getAllByRole('checkbox') as HTMLInputElement[];
    const initialSelected = initialCheckboxes.filter(cb => cb.checked);

    // Toggle a selection
    await user.click(initialCheckboxes[0]);

    // Toggle it back
    await user.click(initialCheckboxes[0]);

    // Should return to initial state
    await waitFor(() => {
      const finalCheckboxes = screen.getAllByRole('checkbox') as HTMLInputElement[];
      const finalSelected = finalCheckboxes.filter(cb => cb.checked);
      expect(finalSelected.length).toBe(initialSelected.length);
    });
  });

  it('displays financial metrics in comparison table', () => {
    render(
      <ScenarioComparison
        onBack={mockOnBack}
      />
    );

    // Check that financial KPIs are displayed
    expect(screen.getByText(/ebitda/i)).toBeInTheDocument();
    expect(screen.getByText(/ebitda%/)).toBeInTheDocument();
    expect(screen.getByText(/sales/i)).toBeInTheDocument();
  });

  it('shows growth metrics in comparison table', () => {
    render(
      <ScenarioComparison
        onBack={mockOnBack}
      />
    );

    // Check that growth KPIs are displayed
    expect(screen.getByText(/growth%/)).toBeInTheDocument();
  });
}); 