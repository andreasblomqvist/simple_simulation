/**
 * Office Settings Tab Component
 * Handles office configuration, economic parameters, and general settings
 */
import React, { useState, useEffect } from 'react';
import type { OfficeConfig } from '../../types/office';
import { OfficeJourney, JOURNEY_CONFIGS } from '../../types/office';
import { useOfficeStore } from '../../stores/officeStore';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import './OfficeSettingsTab.css';

interface OfficeSettingsTabProps {
  office: OfficeConfig;
  onUpdate: (office: OfficeConfig) => void;
}

const TIMEZONE_OPTIONS = [
  'UTC',
  'America/New_York',
  'America/Chicago',
  'America/Denver',
  'America/Los_Angeles',
  'Europe/London',
  'Europe/Paris',
  'Europe/Berlin',
  'Europe/Stockholm',
  'Asia/Tokyo',
  'Asia/Shanghai',
  'Asia/Singapore',
  'Australia/Sydney'
];

export const OfficeSettingsTab: React.FC<OfficeSettingsTabProps> = ({
  office,
  onUpdate
}) => {
  const [formData, setFormData] = useState<OfficeConfig>(office);
  const [originalData, setOriginalData] = useState<OfficeConfig>(office);
  const [isDirty, setIsDirty] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deleteConfirmation, setDeleteConfirmation] = useState('');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const { updateOffice, deleteOffice } = useOfficeStore();

  // Update form data when office prop changes
  useEffect(() => {
    setFormData(office);
    setOriginalData(office);
    setIsDirty(false);
  }, [office]);

  // Check if form has changes
  useEffect(() => {
    const hasChanges = JSON.stringify(formData) !== JSON.stringify(originalData);
    setIsDirty(hasChanges);
  }, [formData, originalData]);

  const handleInputChange = (field: keyof OfficeConfig, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleEconomicParameterChange = (field: keyof OfficeConfig['economic_parameters'], value: number) => {
    setFormData(prev => ({
      ...prev,
      economic_parameters: {
        ...prev.economic_parameters,
        [field]: value
      }
    }));
  };

  const handleSave = async () => {
    if (!isDirty) return;
    
    setSaving(true);
    setError(null);
    
    try {
      const updatedOffice = await updateOffice(formData);
      setOriginalData(updatedOffice);
      setIsDirty(false);
      onUpdate(updatedOffice);
    } catch (err) {
      setError('Failed to save office settings');
      console.error('Error saving office:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleDiscard = () => {
    setFormData(originalData);
    setIsDirty(false);
    setError(null);
  };

  const handleDelete = async () => {
    if (deleteConfirmation !== office.name) {
      setError('Office name confirmation does not match');
      return;
    }
    
    setSaving(true);
    setError(null);
    
    try {
      await deleteOffice(office.id);
      // Navigate will be handled by the parent component
    } catch (err) {
      setError('Failed to delete office');
      console.error('Error deleting office:', err);
      setSaving(false);
    }
  };

  const journeyConfig = JOURNEY_CONFIGS[formData.journey];

  return (
    <div className="office-settings-tab">
      {/* Header */}
      <div className="settings-header">
        <div className="header-info">
          <h2>Office Settings</h2>
          <p>Configure {office.name} settings and parameters</p>
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

      <div className="settings-content">
        {/* Basic Information */}
        <div className="settings-section">
          <h3>Basic Information</h3>
          
          <div className="form-row">
            <label htmlFor="office-name">Office Name:</label>
            <input
              id="office-name"
              type="text"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              placeholder="Enter office name"
              className="form-input"
              maxLength={100}
            />
          </div>

          <div className="form-row">
            <label htmlFor="office-journey">Journey Stage:</label>
            <select
              id="office-journey"
              value={formData.journey}
              onChange={(e) => handleInputChange('journey', e.target.value as OfficeJourney)}
              className="form-select"
            >
              {Object.values(OfficeJourney).map(journey => (
                <option key={journey} value={journey}>
                  {journey.charAt(0).toUpperCase() + journey.slice(1)}
                </option>
              ))}
            </select>
          </div>

          <div className="form-row">
            <label htmlFor="office-timezone">Timezone:</label>
            <select
              id="office-timezone"
              value={formData.timezone}
              onChange={(e) => handleInputChange('timezone', e.target.value)}
              className="form-select"
            >
              {TIMEZONE_OPTIONS.map(tz => (
                <option key={tz} value={tz}>{tz}</option>
              ))}
            </select>
          </div>

          <div className="journey-info">
            <h4>Journey Characteristics</h4>
            <div className="journey-details">
              <div className="journey-detail">
                <span className="detail-label">Typical Size:</span>
                <span className="detail-value">
                  {journeyConfig.typical_size_range[0]} - {journeyConfig.typical_size_range[1]} FTE
                </span>
              </div>
              <div className="journey-detail">
                <span className="detail-label">Expected Growth:</span>
                <span className="detail-value">
                  {(journeyConfig.growth_expectations.recruitment_rate * 100).toFixed(1)}% recruitment, {(journeyConfig.growth_expectations.churn_rate * 100).toFixed(1)}% churn
                </span>
              </div>
              <div className="journey-indicators">
                <span className="indicators-label">Indicators:</span>
                <ul>
                  {journeyConfig.maturity_indicators.map((indicator, index) => (
                    <li key={index}>{indicator}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Economic Parameters */}
        <div className="settings-section">
          <h3>Economic Parameters</h3>
          
          <div className="form-row">
            <label htmlFor="cost-of-living">Cost of Living Multiplier:</label>
            <div className="parameter-input-group">
              <input
                id="cost-of-living"
                type="number"
                value={formData.economic_parameters.cost_of_living.toFixed(2)}
                onChange={(e) => handleEconomicParameterChange('cost_of_living', parseFloat(e.target.value) || 0)}
                min="0.1"
                max="3.0"
                step="0.1"
                className="form-input parameter-input"
              />
              <span className="parameter-unit">×</span>
            </div>
            <div className="parameter-help">
              Adjusts salary costs based on local cost of living (0.1 - 3.0)
            </div>
          </div>

          <div className="form-row">
            <label htmlFor="market-multiplier">Market Rate Multiplier:</label>
            <div className="parameter-input-group">
              <input
                id="market-multiplier"
                type="number"
                value={formData.economic_parameters.market_multiplier.toFixed(2)}
                onChange={(e) => handleEconomicParameterChange('market_multiplier', parseFloat(e.target.value) || 0)}
                min="0.1"
                max="3.0"
                step="0.1"
                className="form-input parameter-input"
              />
              <span className="parameter-unit">×</span>
            </div>
            <div className="parameter-help">
              Adjusts billing rates based on local market conditions (0.1 - 3.0)
            </div>
          </div>

          <div className="form-row">
            <label htmlFor="tax-rate">Tax Rate:</label>
            <div className="parameter-input-group">
              <input
                id="tax-rate"
                type="number"
                value={(formData.economic_parameters.tax_rate * 100).toFixed(1)}
                onChange={(e) => handleEconomicParameterChange('tax_rate', (parseFloat(e.target.value) || 0) / 100)}
                min="0"
                max="70"
                step="0.1"
                className="form-input parameter-input"
              />
              <span className="parameter-unit">%</span>
            </div>
            <div className="parameter-help">
              Corporate tax rate for financial calculations (0% - 70%)
            </div>
          </div>

          <div className="economic-preview">
            <h4>Economic Impact Preview</h4>
            <div className="preview-grid">
              <div className="preview-item">
                <span className="preview-label">Base Salary ($5,000)</span>
                <span className="preview-value">
                  ${(5000 * formData.economic_parameters.cost_of_living).toLocaleString()}
                </span>
              </div>
              <div className="preview-item">
                <span className="preview-label">Base Rate ($100/hr)</span>
                <span className="preview-value">
                  ${(100 * formData.economic_parameters.market_multiplier).toFixed(0)}/hr
                </span>
              </div>
              <div className="preview-item">
                <span className="preview-label">Net Rate (after tax)</span>
                <span className="preview-value">
                  ${(100 * formData.economic_parameters.market_multiplier * (1 - formData.economic_parameters.tax_rate)).toFixed(0)}/hr
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Advanced Settings */}
        <div className="settings-section">
          <h3>Advanced Settings</h3>
          
          <div className="form-row">
            <label>Office ID:</label>
            <div className="readonly-field">
              <code>{formData.id}</code>
            </div>
          </div>

          <div className="form-row">
            <label>Created:</label>
            <div className="readonly-field">
              {formData.created_at ? new Date(formData.created_at).toLocaleString() : 'Not available'}
            </div>
          </div>

          <div className="form-row">
            <label>Last Updated:</label>
            <div className="readonly-field">
              {formData.updated_at ? new Date(formData.updated_at).toLocaleString() : 'Not available'}
            </div>
          </div>
        </div>

        {/* Danger Zone */}
        <div className="settings-section danger-zone">
          <h3>Danger Zone</h3>
          
          <div className="danger-content">
            <div className="danger-info">
              <h4>Delete Office</h4>
              <p>
                Permanently delete this office and all associated data including workforce, 
                business plans, and progression configurations. This action cannot be undone.
              </p>
            </div>
            
            {!showDeleteConfirm ? (
              <button 
                className="danger-button"
                onClick={() => setShowDeleteConfirm(true)}
                disabled={saving}
              >
                Delete Office
              </button>
            ) : (
              <div className="delete-confirmation">
                <p>
                  Type the office name <strong>{office.name}</strong> to confirm deletion:
                </p>
                <input
                  type="text"
                  value={deleteConfirmation}
                  onChange={(e) => setDeleteConfirmation(e.target.value)}
                  placeholder={office.name}
                  className="confirmation-input"
                />
                <div className="confirmation-actions">
                  <button 
                    className="cancel-button"
                    onClick={() => {
                      setShowDeleteConfirm(false);
                      setDeleteConfirmation('');
                    }}
                    disabled={saving}
                  >
                    Cancel
                  </button>
                  <button 
                    className="confirm-delete-button"
                    onClick={handleDelete}
                    disabled={saving || deleteConfirmation !== office.name}
                  >
                    {saving ? (
                      <>
                        <LoadingSpinner size="small" />
                        Deleting...
                      </>
                    ) : (
                      'Delete Forever'
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};