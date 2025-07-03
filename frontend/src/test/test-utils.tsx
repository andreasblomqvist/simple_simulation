import React from 'react';
import type { ReactElement } from 'react';
import { render } from '@testing-library/react';
import type { RenderOptions } from '@testing-library/react';
import { ConfigProvider } from 'antd';
import { vi } from 'vitest';

// Mock the scenario API
export const mockScenarioApi = {
  createScenario: vi.fn(),
  getScenario: vi.fn(),
  listScenarios: vi.fn(),
  updateScenario: vi.fn(),
  deleteScenario: vi.fn(),
  runScenario: vi.fn(),
  runScenarioById: vi.fn(),
  runScenarioDefinition: vi.fn(),
  compareScenarios: vi.fn(),
  compareTwoScenarios: vi.fn(),
  getAvailableOffices: vi.fn(),
  validateScenario: vi.fn(),
  exportScenarioResults: vi.fn(),
  exportComparison: vi.fn(),
};

// Mock the scenario API module
vi.mock('../services/scenarioApi', () => ({
  scenarioApi: mockScenarioApi,
}));

// Test wrapper component with providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <ConfigProvider>
      {children}
    </ConfigProvider>
  );
};

// Custom render function with providers
const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>,
) => render(ui, { wrapper: AllTheProviders, ...options });

// Re-export everything
export * from '@testing-library/react';
export { customRender as render };

// Mock data for tests
export const mockScenarioDefinition = {
  name: 'Test Scenario',
  description: 'A test scenario for testing',
  time_range: {
    start_year: 2025,
    start_month: 1,
    end_year: 2027,
    end_month: 12,
  },
  office_scope: ['Stockholm', 'Munich'],
  levers: {
    recruitment: {
      A: 1.2,
      AC: 1.1,
    },
    churn: {
      A: 0.9,
      AC: 1.0,
    },
    progression: {
      A: 1.0,
      AC: 1.0,
    },
  },
  economic_params: {
    price_increase: 0.05,
    salary_increase: 0.03,
  },
};

export const mockScenarioResponse = {
  scenario_id: 'test-scenario-id',
  scenario_name: 'Test Scenario',
  execution_time: 2.5,
  results: {
    years: {
      '2025': {
        offices: {
          Stockholm: {
            total_fte: 100,
            roles: {
              Consultant: {
                A: {
                  fte: 50,
                  price_1: 1000,
                  salary_1: 50000,
                },
                AC: {
                  fte: 30,
                  price_1: 1200,
                  salary_1: 60000,
                },
              },
            },
          },
        },
      },
    },
  },
  status: 'success' as const,
};

export const mockScenarioList = [
  {
    id: 'scenario-1',
    name: 'Growth Scenario 2025',
    description: 'High growth scenario',
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
    time_range: {
      start_year: 2025,
      start_month: 1,
      end_year: 2027,
      end_month: 12,
    },
    office_scope: ['Stockholm', 'Munich'],
  },
  {
    id: 'scenario-2',
    name: 'Conservative Scenario 2025',
    description: 'Conservative growth scenario',
    created_at: '2025-01-02T00:00:00Z',
    updated_at: '2025-01-02T00:00:00Z',
    time_range: {
      start_year: 2025,
      start_month: 1,
      end_year: 2027,
      end_month: 12,
    },
    office_scope: ['Stockholm'],
  },
];

export const mockAvailableOffices = [
  'Stockholm',
  'Munich',
  'Amsterdam',
  'Berlin',
  'Copenhagen',
  'Frankfurt',
  'Hamburg',
  'Helsinki',
  'Oslo',
  'Zurich',
  'Colombia',
  'Group',
]; 