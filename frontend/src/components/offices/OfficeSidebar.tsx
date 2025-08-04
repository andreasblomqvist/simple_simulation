/**
 * Office navigation sidebar component
 * Groups offices by journey stage with collapsible sections
 */
import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Plus } from 'lucide-react';
import type { OfficeConfig } from '../../types/office';
import { OfficeJourney, JOURNEY_CONFIGS } from '../../types/office';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import { Button } from '../ui/button';
import './OfficeSidebar.css';

interface OfficeSidebarProps {
  offices: OfficeConfig[];
  currentOfficeId?: string;
  onOfficeSelect: (officeId: string) => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
  officesByJourney: Record<OfficeJourney, OfficeConfig[]>;
  loading: boolean;
}

const journeyColors = {
  [OfficeJourney.EMERGING]: '#4caf50',
  [OfficeJourney.ESTABLISHED]: '#2196f3',
  [OfficeJourney.MATURE]: '#9c27b0'
};

const journeyLabels = {
  [OfficeJourney.EMERGING]: 'Emerging',
  [OfficeJourney.ESTABLISHED]: 'Established',
  [OfficeJourney.MATURE]: 'Mature'
};

export const OfficeSidebar: React.FC<OfficeSidebarProps> = ({
  offices,
  currentOfficeId,
  onOfficeSelect,
  collapsed,
  onToggleCollapse,
  officesByJourney,
  loading
}) => {
  const [expandedJourneys, setExpandedJourneys] = useState<Set<OfficeJourney>>(
    new Set([OfficeJourney.EMERGING, OfficeJourney.ESTABLISHED, OfficeJourney.MATURE])
  );

  const toggleJourney = (journey: OfficeJourney) => {
    const newExpanded = new Set(expandedJourneys);
    if (newExpanded.has(journey)) {
      newExpanded.delete(journey);
    } else {
      newExpanded.add(journey);
    }
    setExpandedJourneys(newExpanded);
  };

  const getJourneyIcon = (journey: OfficeJourney) => {
    switch (journey) {
      case OfficeJourney.EMERGING:
        return '🌱';
      case OfficeJourney.ESTABLISHED:
        return '🏢';
      case OfficeJourney.MATURE:
        return '🏛️';
      default:
        return '📍';
    }
  };

  const renderJourneySection = (journey: OfficeJourney) => {
    const journeyOffices = officesByJourney[journey] || [];
    const isExpanded = expandedJourneys.has(journey);
    const journeyConfig = JOURNEY_CONFIGS[journey];
    
    if (journeyOffices.length === 0 && !loading) {
      return null; // Don't show empty sections
    }

    return (
      <div key={journey} className="journey-section">
        <button
          className={`journey-header ${isExpanded ? 'expanded' : ''}`}
          onClick={() => toggleJourney(journey)}
          title={collapsed ? journeyLabels[journey] : undefined}
        >
          <span className="journey-icon">{getJourneyIcon(journey)}</span>
          {!collapsed && (
            <>
              <span className="journey-label">{journeyLabels[journey]}</span>
              <span className="office-count">({journeyOffices.length})</span>
              <span className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>
                ▼
              </span>
            </>
          )}
        </button>

        {isExpanded && !collapsed && (
          <div className="office-list">
            {journeyOffices.map(office => (
              <button
                key={office.id}
                className={`office-item ${currentOfficeId === office.id ? 'active' : ''}`}
                onClick={() => onOfficeSelect(office.id)}
                title={office.name}
              >
                <div className="office-info">
                  <span className="office-name">{office.name}</span>
                  <span className="office-timezone">{office.timezone}</span>
                </div>
                <div 
                  className="journey-indicator"
                  style={{ backgroundColor: journeyColors[journey] }}
                />
              </button>
            ))}
            
            {journeyOffices.length === 0 && loading && (
              <div className="loading-offices">
                <LoadingSpinner size="small" />
              </div>
            )}
          </div>
        )}

        {/* Collapsed mode - show offices as dots */}
        {collapsed && journeyOffices.length > 0 && (
          <div className="office-dots">
            {journeyOffices.map(office => (
              <button
                key={office.id}
                className={`office-dot ${currentOfficeId === office.id ? 'active' : ''}`}
                onClick={() => onOfficeSelect(office.id)}
                title={office.name}
                style={{ backgroundColor: journeyColors[journey] }}
              />
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={`office-sidebar ${collapsed ? 'collapsed' : ''}`}>
      {/* Sidebar header */}
      <div className="sidebar-header">
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggleCollapse}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          className="collapse-button"
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </Button>
        
        {!collapsed && (
          <div className="header-content">
            <h2 className="sidebar-title">Offices</h2>
            <span className="total-count">{offices.length} total</span>
          </div>
        )}
      </div>

      {/* Office navigation */}
      <div className="sidebar-content">
        {loading && offices.length === 0 ? (
          <div className="loading-container">
            <LoadingSpinner size="small" message={collapsed ? undefined : "Loading offices..."} />
          </div>
        ) : (
          <div className="journey-sections">
            {Object.values(OfficeJourney).map(journey => 
              renderJourneySection(journey)
            )}
          </div>
        )}

        {!loading && offices.length === 0 && (
          <div className="empty-sidebar">
            {!collapsed && (
              <>
                <div className="empty-icon">🏢</div>
                <p className="empty-text">No offices found</p>
                <Button 
                  variant="outline"
                  size="sm"
                  className="create-first-office"
                >
                  Create Office
                </Button>
              </>
            )}
          </div>
        )}
      </div>

      {/* Sidebar footer */}
      {!collapsed && (
        <div className="sidebar-footer">
          <Button 
            variant="ghost" 
            size="sm" 
            className="add-office-button"
            icon={<Plus />}
            iconPosition="left"
          >
            Add Office
          </Button>
        </div>
      )}
    </div>
  );
};