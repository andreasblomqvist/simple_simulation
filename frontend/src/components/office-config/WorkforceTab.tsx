/**
 * Workforce Management Tab Component
 * Handles initial workforce distribution setup and management
 */
import React, { useState, useEffect } from 'react';
import { 
  OfficeConfig, 
  WorkforceDistribution, 
  WorkforceEntry, 
  STANDARD_ROLES, 
  STANDARD_LEVELS,
  StandardRole,
  StandardLevel
} from '../../types/office';
import { useBusinessPlanStore } from '../../stores/businessPlanStore';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import './WorkforceTab.css';

interface WorkforceTabProps {
  office: OfficeConfig;
}

export const WorkforceTab: React.FC<WorkforceTabProps> = ({ office }) => {
  const [workforceData, setWorkforceData] = useState<WorkforceEntry[]>([]);
  const [originalData, setOriginalData] = useState<WorkforceEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [isDirty, setIsDirty] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { loadWorkforceDistribution, currentWorkforce } = useBusinessPlanStore();

  // Load workforce data
  useEffect(() => {
    const loadData = async () => {
      if (!office?.id) return;
      
      setLoading(true);
      setError(null);
      
      try {
        await loadWorkforceDistribution(office.id);
      } catch (err) {
        setError('Failed to load workforce data');
        console.error('Error loading workforce:', err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [office?.id, loadWorkforceDistribution]);

  // Initialize workforce data from store
  useEffect(() => {
    if (currentWorkforce?.workforce) {
      setWorkforceData([...currentWorkforce.workforce]);
      setOriginalData([...currentWorkforce.workforce]);
      setIsDirty(false);
    } else {
      // Initialize with empty data for all role/level combinations
      const emptyWorkforce: WorkforceEntry[] = [];
      STANDARD_ROLES.forEach(role => {
        STANDARD_LEVELS.forEach(level => {
          emptyWorkforce.push({
            role,
            level,
            fte: 0,
            notes: ''
          });
        });
      });
      setWorkforceData(emptyWorkforce);
      setOriginalData(emptyWorkforce);
      setIsDirty(false);
    }
  }, [currentWorkforce]);

  // Check if data has changed
  useEffect(() => {
    const hasChanges = workforceData.some((entry, index) => {
      const original = originalData[index];
      if (!original) return true;
      return entry.fte !== original.fte || entry.notes !== original.notes;
    });
    setIsDirty(hasChanges);
  }, [workforceData, originalData]);

  const handleFteChange = (role: StandardRole, level: StandardLevel, fte: number) => {
    setWorkforceData(prev => prev.map(entry => 
      entry.role === role && entry.level === level 
        ? { ...entry, fte: Math.max(0, fte) }
        : entry
    ));
  };

  const handleNotesChange = (role: StandardRole, level: StandardLevel, notes: string) => {
    setWorkforceData(prev => prev.map(entry => 
      entry.role === role && entry.level === level 
        ? { ...entry, notes }
        : entry
    ));
  };

  const handleSave = async () => {
    if (!office?.id || !isDirty) return;
    
    setSaving(true);
    setError(null);
    
    try {
      // Filter out entries with 0 FTE to keep data clean
      const filteredWorkforce = workforceData.filter(entry => entry.fte > 0);
      
      const workforceDistribution: Omit<WorkforceDistribution, 'id' | 'created_at' | 'updated_at'> = {
        office_id: office.id,
        start_date: new Date().toISOString().split('T')[0], // Today's date
        workforce: filteredWorkforce
      };

      // TODO: Implement actual API call when backend endpoint is available
      // For now, simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      console.log('Saving workforce distribution:', workforceDistribution);
      
      setOriginalData([...workforceData]);
      setIsDirty(false);
      
      // Reload data to ensure consistency
      await loadWorkforceDistribution(office.id);
      
    } catch (err) {
      setError('Failed to save workforce data');
      console.error('Error saving workforce:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleDiscard = () => {
    setWorkforceData([...originalData]);
    setIsDirty(false);
  };

  const handleQuickFill = (role: StandardRole, totalFte: number) => {
    const roleLevels = STANDARD_LEVELS;
    const ftePerLevel = Math.floor(totalFte / roleLevels.length);
    const remainder = totalFte % roleLevels.length;
    
    setWorkforceData(prev => prev.map(entry => {
      if (entry.role === role) {
        const levelIndex = roleLevels.indexOf(entry.level as StandardLevel);
        const fte = ftePerLevel + (levelIndex < remainder ? 1 : 0);
        return { ...entry, fte };
      }
      return entry;
    }));
  };

  const getTotalFte = () => workforceData.reduce((sum, entry) => sum + entry.fte, 0);
  const getRoleFte = (role: StandardRole) => 
    workforceData.filter(entry => entry.role === role).reduce((sum, entry) => sum + entry.fte, 0);
  const getLevelFte = (level: StandardLevel) => 
    workforceData.filter(entry => entry.level === level).reduce((sum, entry) => sum + entry.fte, 0);

  if (loading) {
    return (
      <div className="workforce-tab-loading">
        <LoadingSpinner size="large" message="Loading workforce data..." />
      </div>
    );
  }

  return (
    <div className="workforce-tab">
      {/* Header */}
      <div className="workforce-header">
        <div className="header-info">
          <h2>Workforce Distribution</h2>
          <p>Configure the initial workforce distribution for {office.name}</p>
        </div>
        
        <div className="header-actions">
          {isDirty && (
            <>
              <button 
                className="discard-button"
                onClick={handleDiscard}
                disabled={saving}
              >
                Discard Changes
              </button>
              <button 
                className="save-button"
                onClick={handleSave}
                disabled={saving}
              >
                {saving ? (
                  <>
                    <LoadingSpinner size="small" />
                    Saving...
                  </>
                ) : (
                  'Save Changes'
                )}
              </button>
            </>
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-banner">
          <span className="error-text">{error}</span>
          <button onClick={() => setError(null)} className="error-dismiss">✕</button>
        </div>
      )}

      {/* Summary Stats */}
      <div className="workforce-summary">
        <div className="summary-card total">
          <span className="summary-label">Total Workforce</span>
          <span className="summary-value">{Math.round(getTotalFte())}</span>
          <span className="summary-unit">FTE</span>
        </div>
        
        {STANDARD_ROLES.map(role => (
          <div key={role} className="summary-card role">
            <span className="summary-label">{role}</span>
            <span className="summary-value">{Math.round(getRoleFte(role))}</span>
            <span className="summary-unit">FTE</span>
          </div>
        ))}
      </div>

      {/* Quick Fill Tools */}
      <div className="quick-fill-section">
        <h3>Quick Fill Tools</h3>
        <div className="quick-fill-controls">
          {STANDARD_ROLES.map(role => (
            <div key={role} className="quick-fill-role">
              <span className="role-label">{role}:</span>
              <input
                type="number"
                placeholder="Total FTE"
                min="0"
                max="999"
                className="quick-fill-input"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    const value = parseInt((e.target as HTMLInputElement).value) || 0;
                    handleQuickFill(role, value);
                    (e.target as HTMLInputElement).value = '';
                  }
                }}
              />
              <button
                className="quick-fill-button"
                onClick={() => {
                  const input = document.querySelector(
                    `.quick-fill-role:nth-child(${STANDARD_ROLES.indexOf(role) + 1}) .quick-fill-input`
                  ) as HTMLInputElement;
                  const value = parseInt(input.value) || 0;
                  handleQuickFill(role, value);
                  input.value = '';
                }}
              >
                Distribute
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Workforce Grid */}
      <div className="workforce-grid">
        <div className="grid-header">
          <div className="header-cell role-header">Role</div>
          {STANDARD_LEVELS.map(level => (
            <div key={level} className="header-cell level-header">
              <span className="level-name">{level}</span>
              <span className="level-total">{Math.round(getLevelFte(level))}</span>
            </div>
          ))}
          <div className="header-cell total-header">Total</div>
        </div>

        {STANDARD_ROLES.map(role => (
          <div key={role} className="grid-row">
            <div className="role-cell">
              <span className="role-name">{role}</span>
              <span className="role-total">{Math.round(getRoleFte(role))} FTE</span>
            </div>
            
            {STANDARD_LEVELS.map(level => {
              const entry = workforceData.find(e => e.role === role && e.level === level);
              const fte = entry?.fte || 0;
              const notes = entry?.notes || '';
              
              return (
                <div key={`${role}-${level}`} className="workforce-cell">
                  <input
                    type="number"
                    value={fte}
                    onChange={(e) => handleFteChange(role, level, parseInt(e.target.value) || 0)}
                    min="0"
                    max="999"
                    className="fte-input"
                    placeholder="0"
                  />
                  <textarea
                    value={notes}
                    onChange={(e) => handleNotesChange(role, level, e.target.value)}
                    placeholder="Notes (optional)"
                    className="notes-input"
                    rows={2}
                  />
                </div>
              );
            })}
            
            <div className="total-cell">
              <span className="total-value">{Math.round(getRoleFte(role))}</span>
            </div>
          </div>
        ))}

        {/* Level Totals Row */}
        <div className="grid-row totals-row">
          <div className="role-cell">
            <span className="role-name">Total</span>
          </div>
          {STANDARD_LEVELS.map(level => (
            <div key={level} className="total-cell">
              <span className="total-value">{Math.round(getLevelFte(level))}</span>
            </div>
          ))}
          <div className="total-cell grand-total">
            <span className="total-value">{Math.round(getTotalFte())}</span>
          </div>
        </div>
      </div>

      {/* Help Text */}
      <div className="workforce-help">
        <h4>Tips:</h4>
        <ul>
          <li>Use the Quick Fill tools to distribute FTE evenly across levels for each role</li>
          <li>Enter numbers directly in the grid for precise control</li>
          <li>Add notes to document specific requirements or assumptions</li>
          <li>Changes are saved automatically when you click "Save Changes"</li>
        </ul>
      </div>
    </div>
  );
};