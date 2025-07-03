import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render, mockScenarioApi, mockScenarioList } from '../../../test/test-utils';
import ScenarioList from '../ScenarioList';
import { scenarioApi } from '../../../services/scenarioApi';

describe('ScenarioList', () => {
  const mockOnNext = vi.fn();
  const mockOnEdit = vi.fn();
  const mockOnDelete = vi.fn();
  const mockOnCompare = vi.fn();
  const mockOnExport = vi.fn();
  const mockOnView = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders empty state when no scenarios', async () => {
    vi.spyOn(scenarioApi, 'listScenarios').mockResolvedValue([]);
    render(
      <ScenarioList
        onNext={mockOnNext}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onCompare={mockOnCompare}
        onExport={mockOnExport}
        onView={mockOnView}
      />
    );

    // Wait for the empty state to appear after loading
    await waitFor(() => {
      expect(screen.getByText(/no scenarios found/i)).toBeInTheDocument();
    });
    expect(screen.getByText(/create your first scenario/i)).toBeInTheDocument();
  });

  it('renders list of scenarios', async () => {
    mockScenarioApi.listScenarios.mockResolvedValue(mockScenarioList);

    render(
      <ScenarioList
        onNext={mockOnNext}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onCompare={mockOnCompare}
        onExport={mockOnExport}
        onView={mockOnView}
      />
    );

    await waitFor(() => {
      expect(mockScenarioApi.listScenarios).toHaveBeenCalled();
    });

    // Check that both scenarios are rendered
    expect(screen.getByText('Growth Scenario 2025')).toBeInTheDocument();
    expect(screen.getByText('Conservative Scenario 2025')).toBeInTheDocument();
    expect(screen.getByText('High growth scenario')).toBeInTheDocument();
    expect(screen.getByText('Conservative growth scenario')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    mockScenarioApi.listScenarios.mockImplementation(() => new Promise(() => {}));

    render(
      <ScenarioList
        onNext={mockOnNext}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onCompare={mockOnCompare}
        onExport={mockOnExport}
        onView={mockOnView}
      />
    );

    expect(screen.getByText(/loading scenarios/i)).toBeInTheDocument();
  });

  it('calls onView when view button is clicked', async () => {
    const user = userEvent.setup();
    mockScenarioApi.listScenarios.mockResolvedValue(mockScenarioList);

    render(
      <ScenarioList
        onNext={mockOnNext}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onCompare={mockOnCompare}
        onExport={mockOnExport}
        onView={mockOnView}
      />
    );

    await waitFor(() => {
      expect(mockScenarioApi.listScenarios).toHaveBeenCalled();
    });

    // Click on the view button for the first scenario
    const viewButtons = screen.getAllByText(/view/i);
    await user.click(viewButtons[0]);

    expect(mockOnView).toHaveBeenCalledWith('scenario-1');
  });

  it('calls onEdit when edit button is clicked', async () => {
    const user = userEvent.setup();
    mockScenarioApi.listScenarios.mockResolvedValue(mockScenarioList);

    render(
      <ScenarioList
        onNext={mockOnNext}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onCompare={mockOnCompare}
        onExport={mockOnExport}
        onView={mockOnView}
      />
    );

    await waitFor(() => {
      expect(mockScenarioApi.listScenarios).toHaveBeenCalled();
    });

    // Click on the edit button for the first scenario
    const editButtons = screen.getAllByText(/edit/i);
    await user.click(editButtons[0]);

    expect(mockOnEdit).toHaveBeenCalledWith('scenario-1');
  });

  it('calls onNext when create button is clicked', async () => {
    const user = userEvent.setup();
    mockScenarioApi.listScenarios.mockResolvedValue([]);

    render(
      <ScenarioList
        onNext={mockOnNext}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onCompare={mockOnCompare}
        onExport={mockOnExport}
        onView={mockOnView}
      />
    );

    await waitFor(() => {
      expect(mockScenarioApi.listScenarios).toHaveBeenCalled();
    });

    await user.click(screen.getByText(/create your first scenario/i));

    expect(mockOnNext).toHaveBeenCalled();
  });

  it('calls onCompare when compare button is clicked', async () => {
    vi.spyOn(scenarioApi, 'listScenarios').mockResolvedValue(mockScenarioList);
    render(
      <ScenarioList
        onNext={mockOnNext}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onCompare={mockOnCompare}
        onExport={mockOnExport}
        onView={mockOnView}
      />
    );

    // Wait for scenarios to load
    await waitFor(() => {
      expect(screen.getByText(mockScenarioList[0].name)).toBeInTheDocument();
    });

    // Select two scenarios (simulate user selection)
    const checkboxes = screen.getAllByRole('checkbox') as HTMLInputElement[];
    await userEvent.click(checkboxes[0]);
    await userEvent.click(checkboxes[1]);

    // Now the button should be enabled
    const compareButton = screen.getByText(/compare scenarios/i).closest('button');
    expect(compareButton).not.toBeDisabled();

    await userEvent.click(compareButton!);
    expect(mockOnCompare).toHaveBeenCalled();
  });

  it('handles delete scenario successfully', async () => {
    const user = userEvent.setup();
    mockScenarioApi.listScenarios.mockResolvedValue(mockScenarioList);
    mockScenarioApi.deleteScenario.mockResolvedValue(undefined);

    render(
      <ScenarioList
        onNext={mockOnNext}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onCompare={mockOnCompare}
        onExport={mockOnExport}
        onView={mockOnView}
      />
    );

    await waitFor(() => {
      expect(mockScenarioApi.listScenarios).toHaveBeenCalled();
    });

    // Click on the delete button for the first scenario
    const deleteButtons = screen.getAllByText(/delete/i);
    await user.click(deleteButtons[0]);

    // Confirm deletion
    await user.click(screen.getByText(/yes/i));

    expect(mockScenarioApi.deleteScenario).toHaveBeenCalledWith('scenario-1');
  });

  it('handles export scenario successfully', async () => {
    vi.spyOn(scenarioApi, 'listScenarios').mockResolvedValue(mockScenarioList);
    vi.spyOn(scenarioApi, 'exportScenarioResults').mockResolvedValue(new Blob(['test'], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }));
    // Mock DOM APIs
    const createElementSpy = vi.spyOn(document, 'createElement').mockImplementation(() => {
      const a = document.createElementNS('http://www.w3.org/1999/xhtml', 'a') as HTMLAnchorElement;
      a.click = vi.fn();
      return a;
    });
    const appendChildSpy = vi.spyOn(document.body, 'appendChild').mockImplementation((node) => document.createElement('div'));
    const removeChildSpy = vi.spyOn(document.body, 'removeChild').mockImplementation((node) => document.createElement('div'));
    const createObjectURLSpy = vi.spyOn(window.URL, 'createObjectURL').mockReturnValue('blob:url');
    const revokeObjectURLSpy = vi.spyOn(window.URL, 'revokeObjectURL').mockImplementation(() => {});

    render(
      <ScenarioList
        onNext={mockOnNext}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onCompare={mockOnCompare}
        onExport={mockOnExport}
        onView={mockOnView}
      />
    );

    await waitFor(() => {
      expect(screen.getByText(mockScenarioList[0].name)).toBeInTheDocument();
    });

    // Click export button for the first scenario
    const exportButton = screen.getAllByText(/export/i)[0].closest('button');
    await userEvent.click(exportButton!);

    expect(scenarioApi.exportScenarioResults).toHaveBeenCalled();
    expect(createElementSpy).toHaveBeenCalled();
    expect(appendChildSpy).toHaveBeenCalled();
    expect(removeChildSpy).toHaveBeenCalled();
    expect(createObjectURLSpy).toHaveBeenCalled();
    expect(revokeObjectURLSpy).toHaveBeenCalled();
  });

  it('handles API errors gracefully', async () => {
    mockScenarioApi.listScenarios.mockRejectedValue(new Error('Failed to load scenarios'));

    render(
      <ScenarioList
        onNext={mockOnNext}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
        onCompare={mockOnCompare}
        onExport={mockOnExport}
        onView={mockOnView}
      />
    );

    await waitFor(() => {
      expect(mockScenarioApi.listScenarios).toHaveBeenCalled();
    });

    // Should still render the component even with errors
    expect(screen.getByText(/scenario runner/i)).toBeInTheDocument();
  });
}); 