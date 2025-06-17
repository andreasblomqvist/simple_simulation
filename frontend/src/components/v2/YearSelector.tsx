import React from 'react';
import { Tabs, Badge, Spin, Typography } from 'antd';
import { useYearNavigation } from './YearNavigationProvider';
import './YearSelector.css'; // We'll create this for custom styling

const { Text } = Typography;

interface YearSelectorProps {
  className?: string;
  size?: 'small' | 'middle' | 'large';
  type?: 'line' | 'card';
}

/**
 * YearSelector Component
 * 
 * Provides tab-based navigation between simulation years with visual indicators:
 * - Loading spinner for active year during transitions
 * - Success badge for completed years (before current)
 * - Default badge for future years (after current)
 * - Error states for failed data loading
 * 
 * Features:
 * - Single-click year navigation
 * - Visual feedback for data availability
 * - Responsive design for mobile/tablet
 * - Keyboard navigation support
 */
export const YearSelector: React.FC<YearSelectorProps> = ({
  className = '',
  size = 'large',
  type = 'card'
}) => {
  const { 
    selectedYear, 
    availableYears, 
    loading, 
    error,
    setSelectedYear 
  } = useYearNavigation();

  // Handle year change
  const handleYearChange = (yearKey: string) => {
    const year = parseInt(yearKey, 10);
    if (!isNaN(year) && year !== selectedYear) {
      setSelectedYear(year);
    }
  };

  // Generate tab items for each available year
  const yearTabs = availableYears.map(year => {
    const isSelected = year === selectedYear;
    const isPast = year < selectedYear;
    const isFuture = year > selectedYear;
    
    // Determine badge status
    let badgeStatus: 'success' | 'default' | 'error' | 'warning' = 'default';
    if (isPast) badgeStatus = 'success';
    if (isFuture) badgeStatus = 'default';
    if (error && isSelected) badgeStatus = 'error';

    return {
      key: year.toString(),
      label: (
        <div className={`year-tab ${isSelected ? 'year-tab--active' : ''}`}>
          <div className="year-tab__content">
            <Text strong={isSelected} className="year-tab__label">
              Year {year}
            </Text>
            
            <div className="year-tab__indicators">
              {/* Loading spinner for active year */}
              {isSelected && loading && (
                <Spin size="small" className="year-tab__spinner" />
              )}
              
              {/* Status badge */}
              {!loading && (
                <Badge 
                  status={badgeStatus} 
                  className="year-tab__badge"
                  title={
                    isPast ? 'Data available' :
                    isFuture ? 'Future year' :
                    error ? 'Error loading data' :
                    'Current year'
                  }
                />
              )}
            </div>
          </div>
          
          {/* Error indicator */}
          {error && isSelected && (
            <div className="year-tab__error">
              <Text type="danger" style={{ fontSize: '11px' }}>
                Error
              </Text>
            </div>
          )}
        </div>
      ),
      disabled: loading && isSelected, // Disable during loading
    };
  });

  return (
    <div className={`year-navigation-header ${className}`}>
      <div className="year-navigation-header__content">
        <Text type="secondary" className="year-navigation-header__title">
          Simulation Years
        </Text>
        
        <Tabs
          activeKey={selectedYear.toString()}
          onChange={handleYearChange}
          items={yearTabs}
          size={size}
          type={type}
          className="year-selector-tabs"
          tabBarGutter={8}
          // Accessibility
          tabBarExtraContent={
            error && (
              <Text type="danger" style={{ fontSize: '12px' }}>
                {error}
              </Text>
            )
          }
        />
      </div>
      
      {/* Navigation hints for keyboard users */}
      <div className="year-navigation-header__hints" style={{ display: 'none' }}>
        <Text type="secondary" style={{ fontSize: '11px' }}>
          Use arrow keys to navigate between years
        </Text>
      </div>
    </div>
  );
};

export default YearSelector; 