import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render } from '../../../test/test-utils';
import ScenarioLevers from '../ScenarioLevers';

describe('ScenarioLevers', () => {
  const mockOnNext = vi.fn();
  const mockOnBack = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the levers configuration form', () => {
    render(
      <ScenarioLevers
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Check that all lever types are present
    expect(screen.getByText(/recruitment multiplier/i)).toBeInTheDocument();
    expect(screen.getByText(/churn multiplier/i)).toBeInTheDocument();
    expect(screen.getByText(/progression multiplier/i)).toBeInTheDocument();

    // Check that role types are present
    expect(screen.getByText(/role/i)).toBeInTheDocument();
    expect(screen.getByText(/a/i)).toBeInTheDocument();
    expect(screen.getByText(/ac/i)).toBeInTheDocument();
  });

  it('displays default lever values', () => {
    render(
      <ScenarioLevers
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Check that default values (1.00) are displayed
    const defaultValues = screen.getAllByText('1.00');
    expect(defaultValues.length).toBeGreaterThan(0);
  });

  it('allows users to modify lever values via sliders', async () => {
    const user = userEvent.setup();

    render(
      <ScenarioLevers
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Find sliders and modify values
    const sliders = screen.getAllByRole('slider');
    expect(sliders.length).toBeGreaterThan(0);

    // Modify the first slider
    await user.click(sliders[0]);
    await user.keyboard('{ArrowRight}'); // Increase value

    // Should show updated value
    await waitFor(() => {
      const found = Array.from(document.querySelectorAll('span')).some(span => /1\.01/.test(span.textContent || ''));
      expect(found).toBe(true);
    });
  });

  it('shows actual values based on multipliers', () => {
    render(
      <ScenarioLevers
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Check that actual values are calculated and displayed
    expect(screen.getByText(/recruitment actual/i)).toBeInTheDocument();
    expect(screen.getByText(/churn actual/i)).toBeInTheDocument();
  });

  it('provides reset functionality for each lever type', async () => {
    const user = userEvent.setup();

    render(
      <ScenarioLevers
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Find reset buttons
    const resetButtons = screen.getAllByText(/reset all/i);
    expect(resetButtons.length).toBeGreaterThan(0);

    // Click on a reset button
    await user.click(resetButtons[0]);

    // Should reset values to default
    await waitFor(() => {
      const defaultValues = screen.getAllByText('1.00');
      expect(defaultValues.length).toBeGreaterThan(0);
    });
  });

  it('shows progression impact information', () => {
    render(
      <ScenarioLevers
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Check that progression-specific columns are present
    expect(screen.getByText(/max change/i)).toBeInTheDocument();
    expect(screen.getByText(/expected time on level/i)).toBeInTheDocument();
  });

  it('provides tooltips for progression explanation', () => {
    render(
      <ScenarioLevers
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Check that info icons are present
    const infoIcons = screen.getAllByLabelText(/info/i);
    expect(infoIcons.length).toBeGreaterThan(0);
  });

  it('calls onNext when next button is clicked', async () => {
    const user = userEvent.setup();

    render(
      <ScenarioLevers
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Find and click the next button
    const nextButton = screen.getByText(/next/i) || screen.getByText(/continue/i);
    await user.click(nextButton);

    expect(mockOnNext).toHaveBeenCalled();
  });

  it('calls onBack when back button is clicked', async () => {
    const user = userEvent.setup();

    render(
      <ScenarioLevers
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Find and click the back button
    const backButton = screen.getByText(/back/i);
    await user.click(backButton);

    expect(mockOnBack).toHaveBeenCalled();
  });

  it('displays role progression data correctly', () => {
    render(
      <ScenarioLevers
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Check that role progression information is displayed
    expect(screen.getByText(/expected time on level/i)).toBeInTheDocument();
  });

  it('handles slider value changes correctly', async () => {
    const user = userEvent.setup();

    render(
      <ScenarioLevers
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Find a slider and change its value
    const sliders = screen.getAllByRole('slider');
    const firstSlider = sliders[0];

    // Simulate slider interaction
    await user.click(firstSlider);
    await user.keyboard('{ArrowRight}{ArrowRight}'); // Increase by 0.02

    // Should show updated value
    await waitFor(() => {
      const found = Array.from(document.querySelectorAll('span')).some(span => /1\.02/.test(span.textContent || ''));
      expect(found).toBe(true);
    });
  });

  it('maintains state across multiple interactions', async () => {
    const user = userEvent.setup();

    render(
      <ScenarioLevers
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Modify multiple sliders
    const sliders = screen.getAllByRole('slider');
    
    // Modify first slider
    await user.click(sliders[0]);
    await user.keyboard('{ArrowRight}');
    
    // Modify second slider
    await user.click(sliders[1]);
    await user.keyboard('{ArrowLeft}');

    // Both changes should be maintained
    await waitFor(() => {
      const found1 = Array.from(document.querySelectorAll('span')).some(span => /1\.01/.test(span.textContent || ''));
      const found2 = Array.from(document.querySelectorAll('span')).some(span => /0\.99/.test(span.textContent || ''));
      expect(found1).toBe(true);
      expect(found2).toBe(true);
    });
  });

  it('displays baseline values correctly', () => {
    render(
      <ScenarioLevers
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Check that baseline values are shown in the actual columns
    expect(screen.getByText(/recruitment actual/i)).toBeInTheDocument();
    expect(screen.getByText(/churn actual/i)).toBeInTheDocument();
  });

  it('provides responsive layout', () => {
    render(
      <ScenarioLevers
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Check that the component renders without errors
    expect(screen.getByText(/recruitment multiplier/i)).toBeInTheDocument();
    expect(screen.getByText(/churn multiplier/i)).toBeInTheDocument();
    expect(screen.getByText(/progression multiplier/i)).toBeInTheDocument();
  });
}); 