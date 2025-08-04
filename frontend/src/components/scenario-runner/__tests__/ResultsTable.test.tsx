import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render } from '../../../test/test-utils';
import { ModernModernResultsTable } from '../ModernModernResultsTable';
import { scenarioApi } from '../../../services/scenarioApi';

// Mock the scenarioApi
vi.mock('../../../services/scenarioApi', () => ({
  scenarioApi: {
    getScenarioResults: vi.fn(),
  },
}));

// Mock simulation results data - Updated for ModernModernResultsTable format
const mockSimulationResults = {
  years: {
    '2025': {
      offices: {
        Stockholm: {
          total_fte: 100,
          roles: {},
          financial: {
            net_sales: 1000000,
            total_salary_costs: 800000,
            ebitda: 200000,
            margin: 0.20,
            avg_hourly_rate: 1200,
            avg_utr: 0.85,
          },
          growth: {
            total_growth_percent: 20.0,
            total_growth_absolute: 20,
            non_debit_ratio: 0.15,
          },
          journeys: {
            journey_percentages: {
              "Journey 1": 25.0,
              "Journey 2": 30.0,
              "Journey 3": 25.0,
              "Journey 4": 20.0,
            }
          },
        },
      },
      kpis: {
        financial: {
          total_consultants: 100,
          net_sales: 1000000,
          ebitda: 200000,
          margin: 0.20,
        },
        growth: {
          total_growth_percent: 20.0,
        },
        journeys: {
          journey_percentages: {
            "Journey 1": 25.0,
            "Journey 2": 30.0,
            "Journey 3": 25.0,
            "Journey 4": 20.0,
          }
        }
      }
    },
    '2026': {
      offices: {
        Stockholm: {
          total_fte: 120,
          roles: {},
          financial: {
            net_sales: 1200000,
            total_salary_costs: 960000,
            ebitda: 240000,
            margin: 0.20,
            avg_hourly_rate: 1200,
            avg_utr: 0.85,
          },
          growth: {
            total_growth_percent: 20.0,
            total_growth_absolute: 20,
            non_debit_ratio: 0.15,
          },
          journeys: {
            journey_percentages: {
              "Journey 1": 25.0,
              "Journey 2": 30.0,
              "Journey 3": 25.0,
              "Journey 4": 20.0,
            }
          },
        },
      },
      kpis: {
        financial: {
          total_consultants: 120,
          net_sales: 1200000,
          ebitda: 240000,
          margin: 0.20,
        },
        growth: {
          total_growth_percent: 20.0,
        },
        journeys: {
          journey_percentages: {
            "Journey 1": 25.0,
            "Journey 2": 30.0,
            "Journey 3": 25.0,
            "Journey 4": 20.0,
          }
        }
      }
    },
  },
};

describe('ModernModernResultsTable', () => {
  const mockOnNext = vi.fn();
  const mockOnBack = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    // Mock the API response
    vi.mocked(scenarioApi.getScenarioResults).mockResolvedValue(mockSimulationResults);
  });

  it('renders simulation results table', async () => {
    render(
      <ModernModernResultsTable
        scenarioId="test-scenario-123"
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText(/kpi/i)).toBeInTheDocument();
    });

    // Check that scenario data is displayed
    expect(screen.getByText('2025')).toBeInTheDocument();
    expect(screen.getByText('2026')).toBeInTheDocument();
  });

  it('displays KPI metrics correctly', async () => {
    render(
      <ModernResultsTable
        scenarioId="test-scenario-123"
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText(/fte/i)).toBeInTheDocument();
    });

    // Check that KPI metrics are displayed
    expect(screen.getByText(/fte/i)).toBeInTheDocument();
    expect(screen.getByText(/sales/i)).toBeInTheDocument();
    expect(screen.getByText(/ebitda/i)).toBeInTheDocument();
    expect(screen.getByText(/growth/i)).toBeInTheDocument();
  });

  it('formats financial values correctly', async () => {
    render(
      <ModernResultsTable
        scenarioId="test-scenario-123"
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText(/kpi/i)).toBeInTheDocument();
    });

    // Check that financial values are formatted
    expect(screen.getByText(/1,000,000/)).toBeInTheDocument(); // Sales
    expect(screen.getByText(/200,000/)).toBeInTheDocument(); // EBITDA
    expect(screen.getByText(/20\.0%/)).toBeInTheDocument(); // Margin
  });

  it('shows loading state while fetching data', () => {
    // Mock a slow API response
    vi.mocked(scenarioApi.getScenarioResults).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve(mockSimulationResults), 100))
    );

    render(
      <ModernResultsTable
        scenarioId="test-scenario-123"
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Should show loading indicator
    expect(screen.getByRole('progressbar') || screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    // Mock API error
    vi.mocked(scenarioApi.getScenarioResults).mockRejectedValue(new Error('API Error'));

    render(
      <ModernResultsTable
        scenarioId="test-scenario-123"
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Wait for error to be displayed
    await waitFor(() => {
      expect(screen.getByText(/error/i) || screen.getByText(/failed/i)).toBeInTheDocument();
    });
  });

  it('calls onNext when next button is clicked', async () => {
    const user = userEvent.setup();

    render(
      <ModernResultsTable
        scenarioId="test-scenario-123"
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText(/kpi/i)).toBeInTheDocument();
    });

    // Find and click the next button
    const nextButton = screen.getByText(/next/i) || screen.getByText(/continue/i);
    await user.click(nextButton);

    expect(mockOnNext).toHaveBeenCalled();
  });

  it('calls onBack when back button is clicked', async () => {
    const user = userEvent.setup();

    render(
      <ModernResultsTable
        scenarioId="test-scenario-123"
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText(/kpi/i)).toBeInTheDocument();
    });

    // Find and click the back button
    const backButton = screen.getByText(/back/i);
    await user.click(backButton);

    expect(mockOnBack).toHaveBeenCalled();
  });

  it('allows office selection when multiple offices are available', async () => {
    // Mock data with multiple offices
    const multiOfficeResults = {
      ...mockSimulationResults,
      years: {
        '2025': {
          offices: {
            Stockholm: mockSimulationResults.years['2025'].offices.Stockholm,
            Gothenburg: {
              total_fte: 80,
              roles: {},
              financial: {
                net_sales: 800000,
                total_salary_costs: 640000,
                ebitda: 160000,
                margin: 0.20,
                avg_hourly_rate: 1200,
                avg_utr: 0.85,
              },
              growth: {
                total_growth_percent: 15.0,
                total_growth_absolute: 15,
                non_debit_ratio: 0.15,
              },
              journeys: {
                journey_percentages: {
                  "Journey 1": 30.0,
                  "Journey 2": 25.0,
                  "Journey 3": 25.0,
                  "Journey 4": 20.0,
                }
              },
            },
          },
          kpis: mockSimulationResults.years['2025'].kpis,
        },
      },
    };

    vi.mocked(scenarioApi.getScenarioResults).mockResolvedValue(multiOfficeResults);

    render(
      <ModernResultsTable
        scenarioId="test-scenario-123"
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText(/kpi/i)).toBeInTheDocument();
    });

    // Check that office selector is present
    const officeSelect = screen.getByRole('combobox');
    expect(officeSelect).toBeInTheDocument();
  });

  it('handles empty scenario data gracefully', async () => {
    // Mock empty results
    const emptyResults = {
      years: {},
    };

    vi.mocked(scenarioApi.getScenarioResults).mockResolvedValue(emptyResults);

    render(
      <ModernResultsTable
        scenarioId="empty-scenario"
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Wait for component to handle empty data
    await waitFor(() => {
      expect(screen.getByText(/no data/i) || screen.getByText(/empty/i)).toBeInTheDocument();
    });
  });

  it('provides responsive table layout', async () => {
    render(
      <ModernResultsTable
        scenarioId="test-scenario-123"
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText(/kpi/i)).toBeInTheDocument();
    });

    // Check that table renders without errors
    expect(screen.getByText('2025')).toBeInTheDocument();
    expect(screen.getByText('2026')).toBeInTheDocument();
  });

  it('handles invalid scenario ID', async () => {
    // Mock API error for invalid scenario
    vi.mocked(scenarioApi.getScenarioResults).mockRejectedValue(new Error('Scenario not found'));

    render(
      <ModernResultsTable
        scenarioId="invalid-scenario-id"
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Wait for error to be displayed
    await waitFor(() => {
      expect(screen.getByText(/error/i) || screen.getByText(/not found/i)).toBeInTheDocument();
    });
  });

  it('updates when scenario ID changes', async () => {
    const { rerender } = render(
      <ModernResultsTable
        scenarioId="test-scenario-123"
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Wait for first scenario to load
    await waitFor(() => {
      expect(screen.getByText(/kpi/i)).toBeInTheDocument();
    });

    // Change scenario ID
    rerender(
      <ModernResultsTable
        scenarioId="test-scenario-456"
        onNext={mockOnNext}
        onBack={mockOnBack}
      />
    );

    // Should call API again with new scenario ID
    expect(scenarioApi.getScenarioResults).toHaveBeenCalledWith('test-scenario-456');
  });
}); 