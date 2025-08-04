/**
 * CAT Progression Configuration Tab Component
 * Handles progression curve configuration for all levels
 */
import React, { useState, useEffect } from 'react';
import { 
  OfficeConfig, 
  ProgressionConfig, 
  ProgressionCurve, 
  ProgressionPoint,
  STANDARD_LEVELS,
  StandardLevel
} from '../../types/office';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import './ProgressionTab.css';

interface ProgressionTabProps {
  office: OfficeConfig;
}

const CURVE_TYPES = [
  { value: ProgressionCurve.LINEAR, label: 'Linear', description: 'Constant rate throughout the year' },
  { value: ProgressionCurve.EXPONENTIAL, label: 'Exponential', description: 'Increasing rate over time' },
  { value: ProgressionCurve.CUSTOM, label: 'Custom', description: 'Define specific rates for each month' }
];

const MONTHS = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
];

export const ProgressionTab: React.FC<ProgressionTabProps> = ({ office }) => {
  const [progressionConfigs, setProgressionConfigs] = useState<ProgressionConfig[]>([]);
  const [originalConfigs, setOriginalConfigs] = useState<ProgressionConfig[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [isDirty, setIsDirty] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedLevel, setSelectedLevel] = useState<StandardLevel>('A');

  // Initialize progression configs
  useEffect(() => {
    const initializeConfigs = () => {
      const configs: ProgressionConfig[] = STANDARD_LEVELS.map(level => ({
        id: `temp-${level}`,
        office_id: office.id,
        level,
        monthly_rate: getDefaultRate(level),
        curve_type: ProgressionCurve.LINEAR,
        custom_points: []
      }));
      
      setProgressionConfigs(configs);
      setOriginalConfigs(JSON.parse(JSON.stringify(configs)));
      setIsDirty(false);
    };

    if (office?.id) {
      setLoading(true);
      // TODO: Load actual progression configs from API
      // For now, initialize with defaults
      setTimeout(() => {
        initializeConfigs();
        setLoading(false);
      }, 500);
    }
  }, [office?.id]);

  // Check if data has changed
  useEffect(() => {
    const hasChanges = progressionConfigs.some((config, index) => {
      const original = originalConfigs[index];
      if (!original) return true;
      
      return (
        config.monthly_rate !== original.monthly_rate ||
        config.curve_type !== original.curve_type ||
        JSON.stringify(config.custom_points) !== JSON.stringify(original.custom_points)
      );
    });
    setIsDirty(hasChanges);
  }, [progressionConfigs, originalConfigs]);

  const getDefaultRate = (level: StandardLevel): number => {
    const rates: Record<StandardLevel, number> = {
      'A': 0.08,
      'AC': 0.07,
      'C': 0.06,
      'SrC': 0.05,
      'AM': 0.04,
      'M': 0.03,
      'SrM': 0.02,
      'PiP': 0.01
    };
    return rates[level] || 0.05;
  };

  const handleRateChange = (level: StandardLevel, rate: number) => {
    setProgressionConfigs(prev => prev.map(config =>
      config.level === level 
        ? { ...config, monthly_rate: Math.max(0, Math.min(1, rate)) }
        : config
    ));
  };

  const handleCurveTypeChange = (level: StandardLevel, curveType: ProgressionCurve) => {
    setProgressionConfigs(prev => prev.map(config =>
      config.level === level 
        ? { 
            ...config, 
            curve_type: curveType,
            custom_points: curveType === ProgressionCurve.CUSTOM ? 
              generateDefaultCustomPoints(config.monthly_rate) : []
          }
        : config
    ));
  };

  const handleCustomPointChange = (level: StandardLevel, month: number, rate: number) => {
    setProgressionConfigs(prev => prev.map(config => {
      if (config.level !== level) return config;
      
      const newPoints = [...config.custom_points];
      const existingIndex = newPoints.findIndex(point => point.month === month);
      
      if (existingIndex >= 0) {
        newPoints[existingIndex] = { month, rate: Math.max(0, Math.min(1, rate)) };
      } else {
        newPoints.push({ month, rate: Math.max(0, Math.min(1, rate)) });
        newPoints.sort((a, b) => a.month - b.month);
      }
      
      return { ...config, custom_points: newPoints };
    }));
  };

  const generateDefaultCustomPoints = (baseRate: number): ProgressionPoint[] => {
    return Array.from({ length: 12 }, (_, i) => ({
      month: i + 1,
      rate: baseRate
    }));
  };

  const getEffectiveRate = (config: ProgressionConfig, month: number): number => {
    switch (config.curve_type) {
      case ProgressionCurve.LINEAR:
        return config.monthly_rate;
      case ProgressionCurve.EXPONENTIAL:
        return config.monthly_rate * Math.pow(1.1, month - 1);
      case ProgressionCurve.CUSTOM:
        const customPoint = config.custom_points.find(point => point.month === month);
        return customPoint ? customPoint.rate : config.monthly_rate;
      default:
        return config.monthly_rate;
    }
  };

  const handleSave = async () => {
    if (!isDirty) return;
    
    setSaving(true);
    setError(null);
    
    try {
      // TODO: Implement actual API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      console.log('Saving progression configs:', progressionConfigs);
      
      setOriginalConfigs(JSON.parse(JSON.stringify(progressionConfigs)));
      setIsDirty(false);
      
    } catch (err) {
      setError('Failed to save progression configurations');
      console.error('Error saving progression configs:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleDiscard = () => {
    setProgressionConfigs(JSON.parse(JSON.stringify(originalConfigs)));
    setIsDirty(false);
  };

  const handleApplyToAll = () => {
    const selectedConfig = progressionConfigs.find(config => config.level === selectedLevel);
    if (!selectedConfig) return;
    
    setProgressionConfigs(prev => prev.map(config => ({
      ...config,
      curve_type: selectedConfig.curve_type,
      monthly_rate: selectedConfig.monthly_rate,
      custom_points: selectedConfig.curve_type === ProgressionCurve.CUSTOM 
        ? [...selectedConfig.custom_points] 
        : []
    })));
  };

  const selectedConfig = progressionConfigs.find(config => config.level === selectedLevel);

  if (loading) {
    return (
      <div className="progression-tab-loading">
        <LoadingSpinner size="large" message="Loading progression configurations..." />
      </div>
    );
  }

  return (
    <div className="progression-tab">
      {/* Header */}
      <div className="progression-header">
        <div className="header-info">
          <h2>CAT Progression Configuration</h2>
          <p>Configure progression curves for career advancement tracks in {office.name}</p>
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

      {/* Level Selector */}
      <div className="level-selector">
        <div className="level-tabs">
          {STANDARD_LEVELS.map(level => (
            <button
              key={level}
              className={`level-tab ${selectedLevel === level ? 'active' : ''}`}
              onClick={() => setSelectedLevel(level)}
            >
              <span className="level-name">{level}</span>
              <span className="level-rate">
                {(progressionConfigs.find(c => c.level === level)?.monthly_rate * 100 || 0).toFixed(1)}%
              </span>
            </button>
          ))}
        </div>
        
        <button 
          className="apply-to-all-button"
          onClick={handleApplyToAll}
          disabled={!selectedConfig}
        >
          Apply to All Levels
        </button>
      </div>

      {/* Configuration Panel */}
      {selectedConfig && (
        <div className="config-panel">
          <div className="config-left">
            {/* Basic Settings */}
            <div className="config-section">
              <h3>Basic Configuration</h3>
              
              <div className="config-row">
                <label htmlFor="monthly-rate">Base Monthly Rate:</label>
                <div className="rate-input-group">
                  <input
                    id="monthly-rate"
                    type="number"
                    value={(selectedConfig.monthly_rate * 100).toFixed(1)}
                    onChange={(e) => handleRateChange(selectedLevel, parseFloat(e.target.value) / 100 || 0)}
                    min="0"
                    max="100"
                    step="0.1"
                    className="rate-input"
                  />
                  <span className="rate-unit">%</span>
                </div>
              </div>

              <div className="config-row">
                <label htmlFor="curve-type">Progression Curve:</label>
                <select
                  id="curve-type"
                  value={selectedConfig.curve_type}
                  onChange={(e) => handleCurveTypeChange(selectedLevel, e.target.value as ProgressionCurve)}
                  className="curve-select"
                >
                  {CURVE_TYPES.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="curve-description">
                {CURVE_TYPES.find(type => type.value === selectedConfig.curve_type)?.description}
              </div>
            </div>

            {/* Custom Points (if custom curve) */}
            {selectedConfig.curve_type === ProgressionCurve.CUSTOM && (
              <div className="config-section">
                <h3>Monthly Rates</h3>
                <div className="custom-points-grid">
                  {MONTHS.map((month, index) => {
                    const monthNumber = index + 1;
                    const existingPoint = selectedConfig.custom_points.find(point => point.month === monthNumber);
                    const rate = existingPoint ? existingPoint.rate : selectedConfig.monthly_rate;
                    
                    return (
                      <div key={month} className="custom-point">
                        <label className="point-label">{month}:</label>
                        <div className="point-input-group">
                          <input
                            type="number"
                            value={(rate * 100).toFixed(1)}
                            onChange={(e) => handleCustomPointChange(
                              selectedLevel, 
                              monthNumber, 
                              parseFloat(e.target.value) / 100 || 0
                            )}
                            min="0"
                            max="100"
                            step="0.1"
                            className="point-input"
                          />
                          <span className="point-unit">%</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Visualization */}
          <div className="config-right">
            <div className="config-section">
              <h3>Progression Visualization</h3>
              
              <div className="chart-container">
                <div className="chart-header">
                  <span className="chart-title">Monthly Progression Rates - {selectedLevel}</span>
                  <span className="chart-subtitle">
                    Annual Average: {(
                      Array.from({ length: 12 }, (_, i) => getEffectiveRate(selectedConfig, i + 1))
                        .reduce((sum, rate) => sum + rate, 0) / 12 * 100
                    ).toFixed(1)}%
                  </span>
                </div>
                
                <div className="chart-area">
                  <div className="chart-y-axis">
                    <span>10%</span>
                    <span>7.5%</span>
                    <span>5%</span>
                    <span>2.5%</span>
                    <span>0%</span>
                  </div>
                  
                  <div className="chart-bars">
                    {MONTHS.map((month, index) => {
                      const monthNumber = index + 1;
                      const rate = getEffectiveRate(selectedConfig, monthNumber);
                      const percentage = Math.min((rate / 0.1) * 100, 100); // Scale to 10% max
                      
                      return (
                        <div key={month} className="chart-bar-container">
                          <div 
                            className="chart-bar"
                            style={{ height: `${Math.max(percentage, 2)}%` }}
                            title={`${month}: ${(rate * 100).toFixed(1)}%`}
                          />
                          <span className="chart-month">{month}</span>
                          <span className="chart-value">{(rate * 100).toFixed(1)}%</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>

            {/* Summary Stats */}
            <div className="config-section">
              <h3>Annual Summary</h3>
              <div className="summary-stats">
                <div className="stat-item">
                  <span className="stat-label">Average Rate:</span>
                  <span className="stat-value">
                    {(Array.from({ length: 12 }, (_, i) => getEffectiveRate(selectedConfig, i + 1))
                      .reduce((sum, rate) => sum + rate, 0) / 12 * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Total Annual:</span>
                  <span className="stat-value">
                    {(Array.from({ length: 12 }, (_, i) => getEffectiveRate(selectedConfig, i + 1))
                      .reduce((sum, rate) => sum + rate, 0) * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Peak Month:</span>
                  <span className="stat-value">
                    {(() => {
                      const rates = Array.from({ length: 12 }, (_, i) => getEffectiveRate(selectedConfig, i + 1));
                      const maxRate = Math.max(...rates);
                      const maxIndex = rates.indexOf(maxRate);
                      return `${MONTHS[maxIndex]} (${(maxRate * 100).toFixed(1)}%)`;
                    })()}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* All Levels Overview */}
      <div className="overview-section">
        <h3>All Levels Overview</h3>
        <div className="overview-table">
          <div className="overview-header">
            <span>Level</span>
            <span>Curve Type</span>
            <span>Base Rate</span>
            <span>Annual Total</span>
            <span>Peak Rate</span>
          </div>
          {progressionConfigs.map(config => {
            const annualTotal = Array.from({ length: 12 }, (_, i) => getEffectiveRate(config, i + 1))
              .reduce((sum, rate) => sum + rate, 0);
            const peakRate = Math.max(...Array.from({ length: 12 }, (_, i) => getEffectiveRate(config, i + 1)));
            
            return (
              <div key={config.level} className="overview-row">
                <span className="overview-level">{config.level}</span>
                <span className="overview-curve">{config.curve_type}</span>
                <span className="overview-rate">{(config.monthly_rate * 100).toFixed(1)}%</span>
                <span className="overview-annual">{(annualTotal * 100).toFixed(1)}%</span>
                <span className="overview-peak">{(peakRate * 100).toFixed(1)}%</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Help Section */}
      <div className="progression-help">
        <h4>Progression Configuration Tips:</h4>
        <ul>
          <li><strong>Linear:</strong> Use for consistent, predictable progression rates throughout the year</li>
          <li><strong>Exponential:</strong> Use for accelerating progression, common in performance-based roles</li>
          <li><strong>Custom:</strong> Use for seasonal patterns or specific organizational needs</li>
          <li><strong>Typical Ranges:</strong> Junior levels (5-8%), Mid levels (3-5%), Senior levels (1-3%)</li>
          <li><strong>Apply to All:</strong> Use this to quickly set the same curve pattern across all levels</li>
        </ul>
      </div>
    </div>
  );
};