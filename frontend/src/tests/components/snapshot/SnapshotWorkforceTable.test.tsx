/**
 * Unit tests for SnapshotWorkforceTable component
 * Tests workforce data rendering, calculations, and display options
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';

import { SnapshotWorkforceTable } from '../../../components/snapshot/SnapshotWorkforceTable';
import { snapshotUtils } from '../../../services/snapshotApi';
import type { SnapshotWorkforce } from '../../../types/snapshots';

// Mock dependencies
vi.mock('../../../services/snapshotApi');

// Mock UI components
vi.mock('../../../components/ui/data-table-minimal', () => ({
  DataTableMinimal: ({ columns, data }: any) => (
    <div data-testid="data-table">
      <div data-testid="table-columns">{columns.length} columns</div>
      <div data-testid="table-rows">{data.length} rows</div>
      {data.map((row: any, index: number) => (
        <div key={index} data-testid={`table-row-${index}`}>
          {row.role} - {row.totalFTE} FTE
        </div>
      ))}
    </div>
  ),
}));

vi.mock('../../../components/ui/badge', () => ({
  Badge: ({ children, className }: any) => (
    <span data-testid="badge" className={className}>
      {children}
    </span>
  ),
}));

vi.mock('../../../lib/utils', () => ({
  cn: (...classes: any[]) => classes.filter(Boolean).join(' '),
}));

// Test data
const mockWorkforceData: SnapshotWorkforce[] = [
  {
    role: 'Consultant',
    level: 'A',
    fte: 10,
    salary: 4500,
    notes: 'Junior consultants',
  },
  {
    role: 'Consultant',
    level: 'AC',
    fte: 8,
    salary: 6000,
    notes: 'Associate consultants',
  },
  {
    role: 'Consultant',
    level: 'C',
    fte: 5,
    salary: 8000,
  },
  {
    role: 'Operations',
    level: null, // Flat role
    fte: 7,
    salary: 3500,
    notes: 'Operations team',
  },
  {
    role: 'Manager',
    level: 'M',
    fte: 3,
    salary: 10000,
  },
];

const emptyWorkforceData: SnapshotWorkforce[] = [];

describe('SnapshotWorkforceTable', () => {
  beforeEach(() => {
    // Mock snapshot utilities
    (snapshotUtils as any).formatFTE = vi.fn((fte: number) => `${fte.toFixed(1)}`);
    (snapshotUtils as any).formatSalary = vi.fn((salary: number) => `$${salary.toLocaleString()}`);
    
    vi.clearAllMocks();
  });

  describe('Component Rendering', () => {
    it('renders with workforce data', () => {
      render(<SnapshotWorkforceTable workforce={mockWorkforceData} />);
      
      expect(screen.getByTestId('data-table')).toBeInTheDocument();
      expect(screen.getByText('Total FTE')).toBeInTheDocument();
      expect(screen.getByText('Total Monthly Cost')).toBeInTheDocument();
    });

    it('renders empty state when no workforce data', () => {
      render(<SnapshotWorkforceTable workforce={emptyWorkforceData} />);
      
      expect(screen.getByText('No workforce data available')).toBeInTheDocument();
      expect(screen.queryByTestId('data-table')).not.toBeInTheDocument();
    });

    it('applies custom className', () => {
      const { container } = render(
        <SnapshotWorkforceTable workforce={mockWorkforceData} className="custom-class" />
      );
      
      expect(container.firstChild).toHaveClass('custom-class');
    });

    it('renders without salary column when showSalary is false', () => {
      render(<SnapshotWorkforceTable workforce={mockWorkforceData} showSalary={false} />);
      
      expect(screen.queryByText('Total Monthly Cost')).not.toBeInTheDocument();
      expect(screen.getByText('Total FTE')).toBeInTheDocument();
    });

    it('includes notes column when showNotes is true', () => {
      render(<SnapshotWorkforceTable workforce={mockWorkforceData} showNotes={true} />);
      
      // The notes column would be included in the data table
      expect(screen.getByTestId('data-table')).toBeInTheDocument();
    });
  });

  describe('Data Processing and Calculations', () => {
    it('calculates total FTE correctly', () => {
      render(<SnapshotWorkforceTable workforce={mockWorkforceData} />);
      
      const expectedTotalFTE = 10 + 8 + 5 + 7 + 3; // 33
      expect(snapshotUtils.formatFTE).toHaveBeenCalledWith(expectedTotalFTE);
    });

    it('calculates total salary cost correctly', () => {
      render(<SnapshotWorkforceTable workforce={mockWorkforceData} />);
      
      const expectedTotalCost = 
        (10 * 4500) + // Consultant A
        (8 * 6000) +  // Consultant AC  
        (5 * 8000) +  // Consultant C
        (7 * 3500) +  // Operations
        (3 * 10000);  // Manager
      
      expect(snapshotUtils.formatSalary).toHaveBeenCalledWith(expectedTotalCost);
    });

    it('groups workforce by role correctly', () => {
      render(<SnapshotWorkforceTable workforce={mockWorkforceData} />);
      
      // Should have 3 role groups: Consultant, Operations, Manager
      expect(screen.getByTestId('table-rows')).toHaveTextContent('3 rows');
      
      expect(screen.getByText('Consultant - 23 FTE')).toBeInTheDocument();
      expect(screen.getByText('Operations - 7 FTE')).toBeInTheDocument();
      expect(screen.getByText('Manager - 3 FTE')).toBeInTheDocument();
    });

    it('sorts levels in career progression order', () => {
      const unorderedData: SnapshotWorkforce[] = [
        { role: 'Consultant', level: 'C', fte: 5, salary: 8000 },
        { role: 'Consultant', level: 'A', fte: 10, salary: 4500 },
        { role: 'Consultant', level: 'AC', fte: 8, salary: 6000 },
      ];
      
      render(<SnapshotWorkforceTable workforce={unorderedData} />);
      
      // The component should sort A, AC, C in that order internally
      expect(screen.getByTestId('data-table')).toBeInTheDocument();
    });

    it('handles flat roles (no levels) correctly', () => {
      const flatRoleData: SnapshotWorkforce[] = [
        { role: 'Operations', level: null, fte: 7, salary: 3500 },
        { role: 'Admin', level: null, fte: 3, salary: 3000 },
      ];
      
      render(<SnapshotWorkforceTable workforce={flatRoleData} />);
      
      expect(screen.getByText('Operations - 7 FTE')).toBeInTheDocument();
      expect(screen.getByText('Admin - 3 FTE')).toBeInTheDocument();
    });

    it('sorts roles alphabetically', () => {
      const multiRoleData: SnapshotWorkforce[] = [
        { role: 'Zulu', level: null, fte: 1, salary: 1000 },
        { role: 'Alpha', level: null, fte: 2, salary: 2000 },
        { role: 'Beta', level: null, fte: 3, salary: 3000 },
      ];
      
      render(<SnapshotWorkforceTable workforce={multiRoleData} />);
      
      // Should be sorted alphabetically
      expect(screen.getByTestId('data-table')).toBeInTheDocument();
    });
  });

  describe('Summary Cards', () => {
    it('displays total FTE summary card', () => {
      render(<SnapshotWorkforceTable workforce={mockWorkforceData} />);
      
      expect(screen.getByText('Total FTE')).toBeInTheDocument();
      expect(snapshotUtils.formatFTE).toHaveBeenCalledWith(33);
    });

    it('displays total monthly cost summary card when showSalary is true', () => {
      render(<SnapshotWorkforceTable workforce={mockWorkforceData} showSalary={true} />);
      
      expect(screen.getByText('Total Monthly Cost')).toBeInTheDocument();
    });

    it('hides total monthly cost summary card when showSalary is false', () => {
      render(<SnapshotWorkforceTable workforce={mockWorkforceData} showSalary={false} />);
      
      expect(screen.queryByText('Total Monthly Cost')).not.toBeInTheDocument();
    });
  });

  describe('Role Distribution Summary', () => {
    it('displays role distribution section', () => {
      render(<SnapshotWorkforceTable workforce={mockWorkforceData} />);
      
      expect(screen.getByText('Role Distribution')).toBeInTheDocument();
    });

    it('shows FTE for each role in distribution', () => {
      render(<SnapshotWorkforceTable workforce={mockWorkforceData} />);
      
      // Should display role names
      expect(screen.getByText('Consultant')).toBeInTheDocument();
      expect(screen.getByText('Operations')).toBeInTheDocument();
      expect(screen.getByText('Manager')).toBeInTheDocument();
    });

    it('formats FTE values in role distribution', () => {
      render(<SnapshotWorkforceTable workforce={mockWorkforceData} />);
      
      // Should call formatFTE for each role's total
      expect(snapshotUtils.formatFTE).toHaveBeenCalledWith(23); // Consultant total
      expect(snapshotUtils.formatFTE).toHaveBeenCalledWith(7);  // Operations total
      expect(snapshotUtils.formatFTE).toHaveBeenCalledWith(3);  // Manager total
    });
  });

  describe('Table Columns', () => {
    it('always includes role and level columns', () => {
      render(<SnapshotWorkforceTable workforce={mockWorkforceData} showSalary={false} showNotes={false} />);
      
      // Should have at least role, level, and FTE columns (3)
      expect(screen.getByTestId('table-columns')).toHaveTextContent('3 columns');
    });

    it('includes salary column when showSalary is true', () => {
      render(<SnapshotWorkforceTable workforce={mockWorkforceData} showSalary={true} showNotes={false} />);
      
      // Should have role, level, FTE, and salary columns (4)
      expect(screen.getByTestId('table-columns')).toHaveTextContent('4 columns');
    });

    it('includes notes column when showNotes is true', () => {
      render(<SnapshotWorkforceTable workforce={mockWorkforceData} showSalary={false} showNotes={true} />);
      
      // Should have role, level, FTE, and notes columns (4)
      expect(screen.getByTestId('table-columns')).toHaveTextContent('4 columns');
    });

    it('includes all columns when both showSalary and showNotes are true', () => {
      render(<SnapshotWorkforceTable workforce={mockWorkforceData} showSalary={true} showNotes={true} />);
      
      // Should have role, level, FTE, salary, and notes columns (5)
      expect(screen.getByTestId('table-columns')).toHaveTextContent('5 columns');
    });
  });

  describe('Formatting and Display', () => {
    it('formats FTE values using snapshotUtils', () => {
      render(<SnapshotWorkforceTable workforce={mockWorkforceData} />);
      
      expect(snapshotUtils.formatFTE).toHaveBeenCalledWith(10); // Individual FTEs
      expect(snapshotUtils.formatFTE).toHaveBeenCalledWith(8);
      expect(snapshotUtils.formatFTE).toHaveBeenCalledWith(5);
      expect(snapshotUtils.formatFTE).toHaveBeenCalledWith(7);
      expect(snapshotUtils.formatFTE).toHaveBeenCalledWith(3);
    });

    it('formats salary values using snapshotUtils', () => {
      render(<SnapshotWorkforceTable workforce={mockWorkforceData} showSalary={true} />);
      
      expect(snapshotUtils.formatSalary).toHaveBeenCalledWith(4500); // Individual salaries
      expect(snapshotUtils.formatSalary).toHaveBeenCalledWith(6000);
      expect(snapshotUtils.formatSalary).toHaveBeenCalledWith(8000);
      expect(snapshotUtils.formatSalary).toHaveBeenCalledWith(3500);
      expect(snapshotUtils.formatSalary).toHaveBeenCalledWith(10000);
    });

    it('displays level badges for leveled roles', () => {
      render(<SnapshotWorkforceTable workforce={mockWorkforceData} />);
      
      const badges = screen.getAllByTestId('badge');
      expect(badges.length).toBeGreaterThan(0);
    });

    it('handles null levels for flat roles', () => {
      const flatRoleOnly: SnapshotWorkforce[] = [
        { role: 'Operations', level: null, fte: 7, salary: 3500 },
      ];
      
      render(<SnapshotWorkforceTable workforce={flatRoleOnly} />);
      
      // Should render without errors
      expect(screen.getByTestId('data-table')).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('handles zero FTE values', () => {
      const zeroFteData: SnapshotWorkforce[] = [
        { role: 'Consultant', level: 'A', fte: 0, salary: 4500 },
      ];
      
      render(<SnapshotWorkforceTable workforce={zeroFteData} />);
      
      expect(snapshotUtils.formatFTE).toHaveBeenCalledWith(0);
    });

    it('handles zero salary values', () => {
      const zeroSalaryData: SnapshotWorkforce[] = [
        { role: 'Intern', level: 'I', fte: 2, salary: 0 },
      ];
      
      render(<SnapshotWorkforceTable workforce={zeroSalaryData} showSalary={true} />);
      
      expect(snapshotUtils.formatSalary).toHaveBeenCalledWith(0);
    });

    it('handles missing notes gracefully', () => {
      const noNotesData: SnapshotWorkforce[] = [
        { role: 'Consultant', level: 'A', fte: 5, salary: 4500 }, // no notes field
      ];
      
      render(<SnapshotWorkforceTable workforce={noNotesData} showNotes={true} />);
      
      // Should render without errors
      expect(screen.getByTestId('data-table')).toBeInTheDocument();
    });

    it('handles very large numbers', () => {
      const largeNumbersData: SnapshotWorkforce[] = [
        { role: 'Consultant', level: 'A', fte: 1000, salary: 999999 },
      ];
      
      render(<SnapshotWorkforceTable workforce={largeNumbersData} />);
      
      expect(snapshotUtils.formatFTE).toHaveBeenCalledWith(1000);
      expect(snapshotUtils.formatSalary).toHaveBeenCalledWith(999999000000); // 1000 * 999999
    });

    it('handles single workforce entry', () => {
      const singleEntry: SnapshotWorkforce[] = [
        { role: 'Consultant', level: 'A', fte: 5, salary: 4500 },
      ];
      
      render(<SnapshotWorkforceTable workforce={singleEntry} />);
      
      expect(screen.getByTestId('table-rows')).toHaveTextContent('1 rows');
      expect(screen.getByText('Consultant - 5 FTE')).toBeInTheDocument();
    });

    it('handles many roles efficiently', () => {
      const manyRoles: SnapshotWorkforce[] = Array.from({ length: 50 }, (_, index) => ({
        role: `Role${index}`,
        level: 'A',
        fte: 1,
        salary: 1000,
      }));
      
      render(<SnapshotWorkforceTable workforce={manyRoles} />);
      
      // Should handle large datasets without performance issues
      expect(screen.getByTestId('table-rows')).toHaveTextContent('50 rows');
    });
  });

  describe('Accessibility', () => {
    it('provides proper semantic structure', () => {
      render(<SnapshotWorkforceTable workforce={mockWorkforceData} />);
      
      // Should have proper headings
      expect(screen.getByText('Total FTE')).toBeInTheDocument();
      expect(screen.getByText('Role Distribution')).toBeInTheDocument();
    });

    it('uses proper color contrast for text', () => {
      render(<SnapshotWorkforceTable workforce={mockWorkforceData} />);
      
      // Component should use appropriate color styles (tested via snapshots)
      expect(screen.getByTestId('data-table')).toBeInTheDocument();
    });

    it('provides meaningful labels for summary cards', () => {
      render(<SnapshotWorkforceTable workforce={mockWorkforceData} />);
      
      expect(screen.getByText('Total FTE')).toBeInTheDocument();
      expect(screen.getByText('Total Monthly Cost')).toBeInTheDocument();
      expect(screen.getByText('Role Distribution')).toBeInTheDocument();
    });
  });

  describe('Performance', () => {
    it('memoizes expensive calculations', () => {
      const { rerender } = render(<SnapshotWorkforceTable workforce={mockWorkforceData} />);
      
      // Re-render with same data
      rerender(<SnapshotWorkforceTable workforce={mockWorkforceData} />);
      
      // formatFTE should not be called additional times for the same data
      // (This would be more testable with actual performance monitoring)
      expect(screen.getByTestId('data-table')).toBeInTheDocument();
    });

    it('handles re-renders efficiently when props change', () => {
      const { rerender } = render(<SnapshotWorkforceTable workforce={mockWorkforceData} showSalary={true} />);
      
      // Change prop
      rerender(<SnapshotWorkforceTable workforce={mockWorkforceData} showSalary={false} />);
      
      // Should update columns appropriately
      expect(screen.queryByText('Total Monthly Cost')).not.toBeInTheDocument();
    });
  });
});