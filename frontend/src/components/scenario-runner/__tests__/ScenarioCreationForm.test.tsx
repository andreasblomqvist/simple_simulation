import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render, mockScenarioApi, mockAvailableOffices } from '../../../test/test-utils';
import ScenarioCreationForm from '../ScenarioCreationForm';

describe('ScenarioCreationForm', () => {
  const mockOnNext = vi.fn();
  const mockOnBack = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockScenarioApi.getAvailableOffices.mockResolvedValue(mockAvailableOffices);
  });

  it('renders the form with correct initial values', async () => {
    render(
      <ScenarioCreationForm
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Wait for offices to load
    await waitFor(() => {
      expect(mockScenarioApi.getAvailableOffices).toHaveBeenCalled();
    });

    // Check form elements are present
    expect(screen.getByLabelText(/scenario name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/start year/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/end year/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/start month/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/end month/i)).toBeInTheDocument();
    expect(screen.getByText(/office scope/i)).toBeInTheDocument();
    expect(screen.getByText(/group \(all offices\)/i)).toBeInTheDocument();
    expect(screen.getByText(/individual offices/i)).toBeInTheDocument();
  });

  it('shows loading state while fetching offices', () => {
    mockScenarioApi.getAvailableOffices.mockImplementation(() => new Promise(() => {}));

    render(
      <ScenarioCreationForm
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    expect(screen.getByText(/loading available offices/i)).toBeInTheDocument();
  });

  it('handles office loading error', async () => {
    const errorMessage = 'Failed to load offices';
    mockScenarioApi.getAvailableOffices.mockRejectedValue(new Error(errorMessage));

    render(
      <ScenarioCreationForm
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    await waitFor(() => {
      expect(mockScenarioApi.getAvailableOffices).toHaveBeenCalled();
    });
  });

  it('submits form with group office scope', async () => {
    const user = userEvent.setup();

    render(
      <ScenarioCreationForm
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    await waitFor(() => {
      expect(mockScenarioApi.getAvailableOffices).toHaveBeenCalled();
    });

    // Fill in the form
    await user.type(screen.getByLabelText(/scenario name/i), 'Test Growth Scenario');
    await user.type(screen.getByLabelText(/description/i), 'A test scenario for growth');
    await user.clear(screen.getByLabelText(/start year/i));
    await user.type(screen.getByLabelText(/start year/i), '2025');
    await user.clear(screen.getByLabelText(/end year/i));
    await user.type(screen.getByLabelText(/end year/i), '2027');

    // Submit the form
    await user.click(screen.getByText(/next: configure levers/i));

    // Verify onNext was called with correct data
    expect(mockOnNext).toHaveBeenCalledWith({
      name: 'Test Growth Scenario',
      description: 'A test scenario for growth',
      time_range: {
        start_year: 2025,
        start_month: 1,
        end_year: 2027,
        end_month: 12,
      },
      office_scope: ['Group'],
      levers: {},
      economic_params: {},
    });
  });

  it('submits form with individual office scope', async () => {
    const user = userEvent.setup();

    render(
      <ScenarioCreationForm
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    await waitFor(() => {
      expect(mockScenarioApi.getAvailableOffices).toHaveBeenCalled();
    });

    // Fill in the form
    await user.type(screen.getByLabelText(/scenario name/i), 'Stockholm Growth');
    await user.click(screen.getByText(/individual offices/i));

    // Wait for office selection to appear
    await waitFor(() => {
      expect(screen.getByText(/select offices/i)).toBeInTheDocument();
    });

    // Select offices
    const officeSelect = screen.getByText(/choose offices/i);
    await user.click(officeSelect);
    await user.click(screen.getByText('Stockholm'));
    await user.click(screen.getByText('Munich'));

    // Submit the form
    await user.click(screen.getByText(/next: configure levers/i));

    // Verify onNext was called with correct data
    expect(mockOnNext).toHaveBeenCalledWith({
      name: 'Stockholm Growth',
      description: '',
      time_range: {
        start_year: 2025,
        start_month: 1,
        end_year: 2027,
        end_month: 12,
      },
      office_scope: ['Stockholm', 'Munich'],
      levers: {},
      economic_params: {},
    });
  });

  it('validates required fields', async () => {
    const user = userEvent.setup();

    render(
      <ScenarioCreationForm
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    await waitFor(() => {
      expect(mockScenarioApi.getAvailableOffices).toHaveBeenCalled();
    });

    // Try to submit without filling required fields
    await user.click(screen.getByText(/next: configure levers/i));

    // Should show validation errors
    await waitFor(() => {
      expect(screen.getByText(/please enter a scenario name/i)).toBeInTheDocument();
    });

    // onNext should not be called
    expect(mockOnNext).not.toHaveBeenCalled();
  });

  it('validates time range', async () => {
    const user = userEvent.setup();

    render(
      <ScenarioCreationForm
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    await waitFor(() => {
      expect(mockScenarioApi.getAvailableOffices).toHaveBeenCalled();
    });

    // Fill name but set invalid time range
    await user.type(screen.getByLabelText(/scenario name/i), 'Test Scenario');
    await user.clear(screen.getByLabelText(/start year/i));
    await user.type(screen.getByLabelText(/start year/i), '2027');
    await user.clear(screen.getByLabelText(/end year/i));
    await user.type(screen.getByLabelText(/end year/i), '2025');

    // Submit the form
    await user.click(screen.getByText(/next: configure levers/i));

    // Should show validation error for invalid time range
    await waitFor(() => {
      expect(screen.getByText(/start year required/i)).toBeInTheDocument();
    });
  });

  it('validates individual office selection', async () => {
    const user = userEvent.setup();

    render(
      <ScenarioCreationForm
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    await waitFor(() => {
      expect(mockScenarioApi.getAvailableOffices).toHaveBeenCalled();
    });

    // Fill required fields
    await user.type(screen.getByLabelText(/scenario name/i), 'Test Scenario');
    
    // Switch to individual offices but don't select any
    await user.click(screen.getByText(/individual offices/i));

    await waitFor(() => {
      expect(screen.getByText(/select offices/i)).toBeInTheDocument();
    });

    // Submit the form
    await user.click(screen.getByText(/next: configure levers/i));

    // Should show validation error for office selection
    await waitFor(() => {
      expect(screen.getByText(/select at least one office/i)).toBeInTheDocument();
    });
  });

  it('populates form with existing scenario data', async () => {
    const existingScenario = {
      name: 'Existing Scenario',
      description: 'An existing scenario',
      time_range: {
        start_year: 2024,
        start_month: 6,
        end_year: 2026,
        end_month: 6,
      },
      office_scope: ['Stockholm', 'Munich'],
      levers: {},
      economic_params: {},
    };

    render(
      <ScenarioCreationForm
        scenario={existingScenario}
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    await waitFor(() => {
      expect(mockScenarioApi.getAvailableOffices).toHaveBeenCalled();
    });

    // Check that form is populated with existing data
    expect(screen.getByDisplayValue('Existing Scenario')).toBeInTheDocument();
    expect(screen.getByDisplayValue('An existing scenario')).toBeInTheDocument();
    expect(screen.getByDisplayValue('2024')).toBeInTheDocument();
    expect(screen.getByDisplayValue('2026')).toBeInTheDocument();
    expect(screen.getByText(/individual offices/i)).toBeInTheDocument();
  });

  it('populates form with group scenario data', async () => {
    const groupScenario = {
      name: 'Group Scenario',
      description: 'A group scenario',
      time_range: {
        start_year: 2025,
        start_month: 1,
        end_year: 2027,
        end_month: 12,
      },
      office_scope: ['Group'],
      levers: {},
      economic_params: {},
    };

    render(
      <ScenarioCreationForm
        scenario={groupScenario}
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    await waitFor(() => {
      expect(mockScenarioApi.getAvailableOffices).toHaveBeenCalled();
    });

    // Check that group option is selected
    expect(screen.getByText(/group \(all offices\)/i)).toBeInTheDocument();
  });

  it('calls onBack when back button is clicked', async () => {
    const user = userEvent.setup();

    render(
      <ScenarioCreationForm
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    await waitFor(() => {
      expect(mockScenarioApi.getAvailableOffices).toHaveBeenCalled();
    });

    await user.click(screen.getByText(/back/i));

    expect(mockOnBack).toHaveBeenCalled();
  });

  it('shows loading state when form is submitting', async () => {
    const user = userEvent.setup();

    render(
      <ScenarioCreationForm
        onNext={mockOnNext}
        onBack={mockOnBack}
        loading={true}
      />
    );

    await waitFor(() => {
      expect(mockScenarioApi.getAvailableOffices).toHaveBeenCalled();
    });

    // Fill required fields
    await user.type(screen.getByLabelText(/scenario name/i), 'Test Scenario');

    // Submit button should show loading state
    const submitButton = screen.getByText(/next: configure levers/i);
    expect(submitButton).toBeDisabled();
  });
}); 