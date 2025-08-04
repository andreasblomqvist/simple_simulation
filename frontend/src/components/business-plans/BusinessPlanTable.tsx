/**
 * Business Plan Table Component
 * 12×24 matrix for monthly business planning with 5-parameter editing per cell
 */
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  MonthlyBusinessPlan, 
  MonthlyPlanEntry, 
  OfficeConfig, 
  STANDARD_ROLES, 
  STANDARD_LEVELS,
  StandardRole,
  StandardLevel
} from '../../types/office';
import { useBusinessPlanStore } from '../../stores/businessPlanStore';
import { BusinessPlanCell } from './BusinessPlanCell';
import { BusinessPlanToolbar } from './BusinessPlanToolbar';
import { BusinessPlanSummary } from './BusinessPlanSummary';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import './BusinessPlanTable.css';

interface BusinessPlanTableProps {
  office: OfficeConfig;
  year: number;
  onYearChange: (year: number) => void;
}

interface CellPosition {
  role: StandardRole;
  level: StandardLevel;
  month: number;
}

interface CellData extends MonthlyPlanEntry {
  planId?: string;
  month: number;
  year: number;
}

const MONTHS = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
];

export const BusinessPlanTable: React.FC<BusinessPlanTableProps> = ({
  office,
  year,
  onYearChange
}) => {
  const {
    monthlyPlans,
    currentWorkforce,
    loading,
    error,
    loadBusinessPlans,
    loadWorkforceDistribution,
    updatePlanEntry,
    createMonthlyPlan,
    bulkUpdatePlans,
    clearError
  } = useBusinessPlanStore();

  const [selectedCell, setSelectedCell] = useState<CellPosition | null>(null);
  const [editingCell, setEditingCell] = useState<CellPosition | null>(null);
  const [isDirty, setIsDirty] = useState(false);
  const [localChanges, setLocalChanges] = useState<Map<string, CellData>>(new Map());

  // Load data when office or year changes
  useEffect(() => {
    if (office?.id) {
      loadBusinessPlans(office.id, year);
      loadWorkforceDistribution(office.id);
    }
  }, [office?.id, year, loadBusinessPlans, loadWorkforceDistribution]);

  // Create a map of existing plan data for quick lookup
  const planDataMap = useMemo(() => {
    const map = new Map<string, CellData>();
    
    monthlyPlans.forEach(plan => {
      plan.entries.forEach(entry => {
        const key = `${entry.role}-${entry.level}-${plan.month}`;
        map.set(key, {
          ...entry,
          planId: plan.id,
          month: plan.month,
          year: plan.year
        });
      });
    });
    
    // Apply local changes
    localChanges.forEach((cellData, key) => {
      map.set(key, cellData);
    });
    
    return map;
  }, [monthlyPlans, localChanges]);

  // Get cell data with default values
  const getCellData = useCallback((role: StandardRole, level: StandardLevel, month: number): CellData => {
    const key = `${role}-${level}-${month}`;
    const existing = planDataMap.get(key);
    
    if (existing) {
      return existing;
    }
    
    // Return default values
    return {
      role,
      level,
      month,
      year,
      recruitment: 0,
      churn: 0,
      price: 100,
      utr: 0.75,
      salary: 5000
    };
  }, [planDataMap, year]);

  // Handle cell value updates
  const handleCellUpdate = useCallback((
    role: StandardRole, 
    level: StandardLevel, 
    month: number, 
    field: keyof MonthlyPlanEntry,
    value: number
  ) => {
    const key = `${role}-${level}-${month}`;
    const currentData = getCellData(role, level, month);
    
    const updatedData: CellData = {
      ...currentData,
      [field]: value
    };
    
    setLocalChanges(prev => new Map(prev).set(key, updatedData));
    setIsDirty(true);
  }, [getCellData]);

  // Save changes to backend
  const handleSave = useCallback(async () => {
    if (!office?.id || localChanges.size === 0) return;
    
    try {
      // Group changes by month
      const changesByMonth = new Map<number, MonthlyPlanEntry[]>();
      
      localChanges.forEach((cellData, key) => {
        const month = cellData.month;
        if (!changesByMonth.has(month)) {
          changesByMonth.set(month, []);
        }
        
        const entries = changesByMonth.get(month)!;
        entries.push({
          role: cellData.role,
          level: cellData.level,
          recruitment: cellData.recruitment,
          churn: cellData.churn,
          price: cellData.price,
          utr: cellData.utr,
          salary: cellData.salary
        });
      });
      
      // Create or update plans for each month
      const planPromises = Array.from(changesByMonth.entries()).map(async ([month, entries]) => {
        const existingPlan = monthlyPlans.find(p => p.month === month && p.year === year);
        
        if (existingPlan) {
          // Update existing plan
          const updatedPlan: MonthlyBusinessPlan = {
            ...existingPlan,
            entries: [...existingPlan.entries.filter(e => 
              !entries.some(ne => ne.role === e.role && ne.level === e.level)
            ), ...entries]
          };
          
          return updatePlanEntry(existingPlan.id, entries[0]); // Will handle all entries
        } else {
          // Create new plan
          return createMonthlyPlan({
            office_id: office.id,
            year,
            month,
            entries
          });
        }
      });
      
      await Promise.all(planPromises);
      
      // Clear local changes
      setLocalChanges(new Map());
      setIsDirty(false);
      
      // Reload data
      await loadBusinessPlans(office.id, year);
      
    } catch (error) {
      console.error('Failed to save business plan changes:', error);
    }
  }, [office?.id, localChanges, monthlyPlans, year, updatePlanEntry, createMonthlyPlan, loadBusinessPlans]);

  // Discard local changes
  const handleDiscard = useCallback(() => {
    setLocalChanges(new Map());
    setIsDirty(false);
    setSelectedCell(null);
    setEditingCell(null);
  }, []);

  // Handle keyboard navigation
  const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
    if (!selectedCell) return;
    
    const { role, level, month } = selectedCell;
    let newPosition: CellPosition | null = null;
    
    switch (event.key) {
      case 'ArrowUp':
        const currentLevelIndex = STANDARD_LEVELS.indexOf(level);
        if (currentLevelIndex > 0) {
          newPosition = { role, level: STANDARD_LEVELS[currentLevelIndex - 1], month };
        }
        break;
      case 'ArrowDown':
        const nextLevelIndex = STANDARD_LEVELS.indexOf(level);
        if (nextLevelIndex < STANDARD_LEVELS.length - 1) {
          newPosition = { role, level: STANDARD_LEVELS[nextLevelIndex + 1], month };
        }
        break;
      case 'ArrowLeft':
        if (month > 1) {
          newPosition = { role, level, month: month - 1 };
        }
        break;
      case 'ArrowRight':
        if (month < 12) {
          newPosition = { role, level, month: month + 1 };
        }
        break;
      case 'Enter':
      case 'F2':
        setEditingCell(selectedCell);
        event.preventDefault();
        break;
      case 'Escape':
        setEditingCell(null);
        break;
    }
    
    if (newPosition) {
      setSelectedCell(newPosition);
      event.preventDefault();
    }
  }, [selectedCell]);

  // Calculate summary statistics
  const summaryStats = useMemo(() => {
    const stats = {
      totalRecruitment: 0,
      totalChurn: 0,
      totalRevenue: 0,
      totalSalaryCost: 0,
      byMonth: Array.from({ length: 12 }, (_, i) => ({
        month: i + 1,
        recruitment: 0,
        churn: 0,
        revenue: 0,
        cost: 0
      }))
    };
    
    STANDARD_ROLES.forEach(role => {
      STANDARD_LEVELS.forEach(level => {
        for (let month = 1; month <= 12; month++) {
          const cellData = getCellData(role, level, month);
          const monthStats = stats.byMonth[month - 1];
          
          monthStats.recruitment += cellData.recruitment;
          monthStats.churn += cellData.churn;
          monthStats.revenue += cellData.price * cellData.utr * 160; // 160 hours/month
          monthStats.cost += cellData.salary;
          
          stats.totalRecruitment += cellData.recruitment;
          stats.totalChurn += cellData.churn;
        }
      });
    });
    
    stats.totalRevenue = stats.byMonth.reduce((sum, month) => sum + month.revenue, 0);
    stats.totalSalaryCost = stats.byMonth.reduce((sum, month) => sum + month.cost, 0);
    
    return stats;
  }, [getCellData]);

  if (loading) {
    return (
      <div className="business-plan-loading">
        <LoadingSpinner size="large" message="Loading business plan data..." />
      </div>
    );
  }

  console.log('[DEBUG] BusinessPlanTable rendering with loading:', loading, 'error:', error);

  return (
    <div className="business-plan-table-container">
      <div style={{ padding: '20px' }}>
        <h2>Business Plan for {office.name} - {year}</h2>
        <p>Loading status: {loading ? 'Loading...' : 'Loaded'}</p>
        <p>Error: {error || 'None'}</p>
        <p>Monthly plans: {monthlyPlans.length}</p>
        <p>Current workforce: {currentWorkforce ? 'Loaded' : 'Not loaded'}</p>
        
        <div style={{ marginTop: '20px' }}>
          <h3>Simple Business Plan Table</h3>
          <table style={{ borderCollapse: 'collapse', width: '100%' }}>
            <thead>
              <tr>
                <th>Role</th>
                <th>Level</th>
                <th>Jan</th>
                <th>Feb</th>
                <th>Mar</th>
                <th>Apr</th>
                <th>May</th>
                <th>Jun</th>
                <th>Jul</th>
                <th>Aug</th>
                <th>Sep</th>
                <th>Oct</th>
                <th>Nov</th>
                <th>Dec</th>
              </tr>
            </thead>
            <tbody>
              {STANDARD_ROLES.slice(0, 1).map(role => (
                STANDARD_LEVELS.slice(0, 3).map(level => (
                  <tr key={`${role}-${level}`}>
                    <td>{role}</td>
                    <td>{level}</td>
                    {Array.from({ length: 12 }, (_, monthIndex) => {
                      const month = monthIndex + 1;
                      const cellData = getCellData(role, level, month);
                      return (
                        <td key={month} style={{ border: '1px solid #ccc', padding: '4px', textAlign: 'center' }}>
                          {Math.round(cellData.recruitment)}
                        </td>
                      );
                    })}
                  </tr>
                ))
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};