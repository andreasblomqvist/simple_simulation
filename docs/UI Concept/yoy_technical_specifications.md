# Updated Design Specifications: Year-over-Year Navigation Integration

## Overview

This document provides comprehensive technical specifications for integrating year-over-year navigation functionality into the existing organization simulation dashboard. The updated design maintains the previously established KPI-focused approach while adding temporal navigation capabilities that allow users to track performance progression across multiple simulation years.

## Year Navigation Component Architecture

### Primary Navigation Component

The year navigation system is implemented as a header-level component that provides global context for the entire dashboard. The component architecture follows a hierarchical structure that ensures consistent state management across all child components:

```javascript
const YearNavigationProvider = ({ children, simulationData }) => {
  const [selectedYear, setSelectedYear] = useState(simulationData.finalYear);
  const [yearData, setYearData] = useState({});
  const [loading, setLoading] = useState(false);

  const yearNavigationContext = {
    selectedYear,
    availableYears: simulationData.years,
    yearData: yearData[selectedYear],
    previousYearData: yearData[selectedYear - 1],
    setSelectedYear: handleYearChange,
    loading
  };

  return (
    <YearNavigationContext.Provider value={yearNavigationContext}>
      <YearSelector />
      {children}
    </YearNavigationContext.Provider>
  );
};
```

The year navigation provider manages the global state for year selection and ensures that all dashboard components receive consistent data for the selected year. The provider implements intelligent caching mechanisms to prevent unnecessary data fetching when users navigate between previously loaded years.

### Year Selector Component Implementation

The year selector component utilizes Ant Design's Tab component to provide an intuitive interface for year navigation. The implementation includes visual indicators for data availability and loading states:

```javascript
import { Tabs, Badge, Spin } from 'antd';

const YearSelector = () => {
  const { selectedYear, availableYears, setSelectedYear, loading } = useYearNavigation();

  const yearTabs = availableYears.map(year => ({
    key: year.toString(),
    label: (
      <div className="year-tab">
        <span>Year {year}</span>
        {year === selectedYear && loading && <Spin size="small" />}
        {year > selectedYear && <Badge status="default" />}
        {year < selectedYear && <Badge status="success" />}
      </div>
    ),
  }));

  return (
    <div className="year-navigation-header">
      <Tabs
        activeKey={selectedYear.toString()}
        onChange={(key) => setSelectedYear(parseInt(key))}
        items={yearTabs}
        size="large"
        type="card"
        className="year-selector-tabs"
      />
    </div>
  );
};
```

The year selector provides visual feedback about the current position within the simulation timeline. Years that have been completed show success indicators, while future years display neutral badges. The active year includes a loading spinner during data transitions to provide immediate feedback to users.

## Enhanced KPI Card Component Specifications

### Year-over-Year Change Integration

The KPI cards have been significantly enhanced to display year-over-year changes alongside the primary metrics. The updated component structure incorporates trend analysis and comparative visualization:

```javascript
const EnhancedKPICard = ({ 
  title, 
  currentValue, 
  previousValue, 
  unit, 
  target,
  sparklineData,
  formatValue,
  onClick 
}) => {
  const yearOverYearChange = calculateYoYChange(currentValue, previousValue);
  const trendDirection = yearOverYearChange > 0 ? 'up' : yearOverYearChange < 0 ? 'down' : 'stable';
  
  return (
    <Card 
      className="enhanced-kpi-card"
      hoverable
      onClick={onClick}
      style={{
        height: '220px',
        cursor: 'pointer',
        transition: 'all 0.3s ease'
      }}
    >
      <div className="kpi-header">
        <Text type="secondary" className="kpi-title">{title}</Text>
      </div>
      
      <div className="kpi-value-section">
        <Text className="kpi-value">{formatValue(currentValue, unit)}</Text>
        <YearOverYearIndicator 
          change={yearOverYearChange}
          direction={trendDirection}
          previousValue={previousValue}
        />
      </div>
      
      <div className="kpi-context">
        <Text type="secondary">Previous Year: {formatValue(previousValue, unit)}</Text>
        <Text type="secondary">Target: {formatValue(target, unit)}</Text>
      </div>
      
      <div className="kpi-sparkline">
        <MultiYearSparkline data={sparklineData} currentYear={selectedYear} />
      </div>
    </Card>
  );
};
```

The enhanced KPI card maintains the visual prominence of the primary value while adding contextual information about year-over-year performance. The component automatically calculates percentage changes and provides appropriate visual indicators based on the direction and magnitude of change.

### Year-over-Year Indicator Component

The year-over-year indicator provides immediate visual feedback about performance changes between consecutive years. The component uses color coding and directional arrows to communicate trends effectively:

```javascript
const YearOverYearIndicator = ({ change, direction, previousValue }) => {
  const getIndicatorStyle = (direction) => {
    const baseStyle = {
      display: 'flex',
      alignItems: 'center',
      fontSize: '14px',
      fontWeight: '600',
      marginTop: '4px'
    };

    switch (direction) {
      case 'up':
        return { ...baseStyle, color: '#52c41a' };
      case 'down':
        return { ...baseStyle, color: '#f5222d' };
      default:
        return { ...baseStyle, color: '#8c8c8c' };
    }
  };

  const getArrowIcon = (direction) => {
    switch (direction) {
      case 'up':
        return <ArrowUpOutlined style={{ marginRight: '4px' }} />;
      case 'down':
        return <ArrowDownOutlined style={{ marginRight: '4px' }} />;
      default:
        return <MinusOutlined style={{ marginRight: '4px' }} />;
    }
  };

  const formatChangeText = (change, previousValue) => {
    if (previousValue === 0) return 'N/A';
    const percentage = Math.abs(change);
    const prefix = change > 0 ? '+' : change < 0 ? '-' : '';
    return `${prefix}${percentage.toFixed(1)}%`;
  };

  return (
    <div style={getIndicatorStyle(direction)} className="yoy-indicator">
      {getArrowIcon(direction)}
      <span>{formatChangeText(change, previousValue)}</span>
      <Tooltip title={`Change from previous year: ${previousValue} → ${currentValue}`}>
        <InfoCircleOutlined style={{ marginLeft: '4px', fontSize: '12px' }} />
      </Tooltip>
    </div>
  );
};
```

The indicator component includes tooltips that provide additional context about the specific values being compared. This approach ensures that users can quickly understand both the magnitude and direction of changes while having access to detailed information when needed.

## Multi-Year Chart Component Specifications

### Enhanced Trend Visualization

The chart components have been redesigned to accommodate multi-year data visualization while maintaining the ability to focus on specific years. The implementation uses Ant Design Charts with custom configurations for temporal data:

```javascript
import { Line, Column } from '@ant-design/plots';

const MultiYearTrendChart = ({ data, selectedYear, metric }) => {
  const processedData = data.map(item => ({
    ...item,
    isCurrentYear: item.year === selectedYear,
    isHistorical: item.year < selectedYear,
    isFuture: item.year > selectedYear
  }));

  const config = {
    data: processedData,
    xField: 'year',
    yField: 'value',
    seriesField: 'metric',
    smooth: true,
    point: {
      size: (datum) => datum.isCurrentYear ? 8 : 4,
      shape: 'circle',
      style: (datum) => ({
        fill: datum.isCurrentYear ? '#1890ff' : datum.isHistorical ? '#52c41a' : '#d9d9d9',
        stroke: datum.isCurrentYear ? '#ffffff' : 'transparent',
        strokeWidth: datum.isCurrentYear ? 2 : 0
      })
    },
    lineStyle: (datum) => ({
      stroke: datum.isHistorical ? '#52c41a' : datum.isFuture ? '#d9d9d9' : '#1890ff',
      lineWidth: 2,
      lineDash: datum.isFuture ? [4, 4] : []
    }),
    annotations: [
      {
        type: 'line',
        start: [selectedYear, 'min'],
        end: [selectedYear, 'max'],
        style: {
          stroke: '#1890ff',
          lineWidth: 2,
          lineDash: [2, 2]
        }
      }
    ],
    tooltip: {
      showMarkers: true,
      shared: true,
      customContent: (title, items) => {
        const year = parseInt(title);
        const isCurrentYear = year === selectedYear;
        const yearLabel = isCurrentYear ? `${title} (Current)` : title;
        
        return `
          <div class="custom-tooltip">
            <h4>Year ${yearLabel}</h4>
            ${items.map(item => `
              <div class="tooltip-item">
                <span class="tooltip-marker" style="background-color: ${item.color}"></span>
                <span class="tooltip-name">${item.name}:</span>
                <span class="tooltip-value">${item.value}</span>
              </div>
            `).join('')}
          </div>
        `;
      }
    },
    legend: {
      position: 'top-right',
    },
    interactions: [
      {
        type: 'marker-active',
      },
      {
        type: 'brush-filter',
      },
    ],
  };

  return (
    <Card title={`${metric} Progression`} className="multi-year-chart">
      <Line {...config} />
    </Card>
  );
};
```

The multi-year trend chart provides visual distinction between historical data, current year data, and future projections. The chart includes interactive annotations that highlight the currently selected year and provides contextual tooltips that explain the temporal relationship of data points.

### Year-over-Year Comparison Chart

A dedicated comparison chart component visualizes year-over-year changes across multiple metrics simultaneously. This component helps users identify patterns and correlations in performance changes:

```javascript
const YearOverYearComparisonChart = ({ data, selectedYear }) => {
  const comparisonData = data.filter(item => 
    item.year === selectedYear || item.year === selectedYear - 1
  ).map(item => ({
    ...item,
    yearLabel: item.year === selectedYear ? 'Current Year' : 'Previous Year',
    isCurrentYear: item.year === selectedYear
  }));

  const config = {
    data: comparisonData,
    xField: 'metric',
    yField: 'value',
    seriesField: 'yearLabel',
    isGroup: true,
    columnStyle: {
      radius: [4, 4, 0, 0],
    },
    color: (datum) => datum.isCurrentYear ? '#1890ff' : '#91d5ff',
    label: {
      position: 'top',
      formatter: (datum) => {
        if (datum.yearLabel === 'Current Year' && datum.previousValue) {
          const change = ((datum.value - datum.previousValue) / datum.previousValue * 100).toFixed(1);
          return change > 0 ? `+${change}%` : `${change}%`;
        }
        return '';
      },
      style: {
        fill: (datum) => {
          if (datum.yearLabel === 'Current Year' && datum.previousValue) {
            const change = (datum.value - datum.previousValue) / datum.previousValue;
            return change > 0 ? '#52c41a' : change < 0 ? '#f5222d' : '#8c8c8c';
          }
          return '#262626';
        }
      }
    },
    tooltip: {
      shared: true,
      customContent: (title, items) => {
        const currentItem = items.find(item => item.data.isCurrentYear);
        const previousItem = items.find(item => !item.data.isCurrentYear);
        
        if (currentItem && previousItem) {
          const change = ((currentItem.value - previousItem.value) / previousItem.value * 100).toFixed(1);
          const changeColor = change > 0 ? '#52c41a' : change < 0 ? '#f5222d' : '#8c8c8c';
          
          return `
            <div class="comparison-tooltip">
              <h4>${title}</h4>
              <div>Previous Year: ${previousItem.value}</div>
              <div>Current Year: ${currentItem.value}</div>
              <div style="color: ${changeColor}; font-weight: bold;">
                Change: ${change > 0 ? '+' : ''}${change}%
              </div>
            </div>
          `;
        }
        return null;
      }
    },
    legend: {
      position: 'top-right',
    },
  };

  return (
    <Card title="Year-over-Year Comparison" className="yoy-comparison-chart">
      <Column {...config} />
    </Card>
  );
};
```

The comparison chart automatically calculates and displays percentage changes as labels above the current year bars. The tooltip provides detailed information about the specific values and changes, enabling users to understand both absolute and relative performance differences.

## Enhanced Data Table Specifications

### Year-Specific Data Display

The data table component has been enhanced to support year-specific filtering and year-over-year comparison columns. The implementation maintains the existing functionality while adding temporal context:

```javascript
const EnhancedDataTable = ({ data, selectedYear, loading }) => {
  const [showYoYComparison, setShowYoYComparison] = useState(false);
  const [filteredData, setFilteredData] = useState([]);

  const processTableData = useCallback(() => {
    const currentYearData = data.filter(item => item.year === selectedYear);
    const previousYearData = data.filter(item => item.year === selectedYear - 1);
    
    const processedData = currentYearData.map(currentItem => {
      const previousItem = previousYearData.find(prev => 
        prev.office === currentItem.office && prev.role === currentItem.role
      );
      
      return {
        ...currentItem,
        previousYearFTE: previousItem?.fte || 0,
        previousYearPrice: previousItem?.price || 0,
        previousYearSalary: previousItem?.salary || 0,
        fteChange: previousItem ? currentItem.fte - previousItem.fte : currentItem.fte,
        priceChange: previousItem ? 
          ((currentItem.price - previousItem.price) / previousItem.price * 100) : 0,
        salaryChange: previousItem ? 
          ((currentItem.salary - previousItem.salary) / previousItem.salary * 100) : 0
      };
    });
    
    setFilteredData(processedData);
  }, [data, selectedYear]);

  useEffect(() => {
    processTableData();
  }, [processTableData]);

  const baseColumns = [
    {
      title: 'Office / Level / Role',
      dataIndex: 'office',
      key: 'office',
      sorter: (a, b) => a.office.localeCompare(b.office),
      filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters }) => (
        <div style={{ padding: 8 }}>
          <Search
            placeholder="Search office"
            value={selectedKeys[0]}
            onChange={e => setSelectedKeys(e.target.value ? [e.target.value] : [])}
            onSearch={() => confirm()}
            style={{ width: 188, marginBottom: 8, display: 'block' }}
          />
        </div>
      ),
      onFilter: (value, record) => 
        record.office.toLowerCase().includes(value.toLowerCase()),
    },
    {
      title: 'Journey',
      dataIndex: 'journey',
      key: 'journey',
      sorter: (a, b) => a.journey.localeCompare(b.journey),
    },
    {
      title: 'FTE',
      dataIndex: 'fte',
      key: 'fte',
      sorter: (a, b) => a.fte - b.fte,
      render: (value, record) => (
        <div className="fte-cell">
          <span className="current-value">{value.toLocaleString()}</span>
          {showYoYComparison && record.fteChange !== 0 && (
            <span className={`change-indicator ${record.fteChange > 0 ? 'positive' : 'negative'}`}>
              ({record.fteChange > 0 ? '+' : ''}{record.fteChange})
            </span>
          )}
        </div>
      ),
    },
    {
      title: 'Price',
      dataIndex: 'price',
      key: 'price',
      sorter: (a, b) => a.price - b.price,
      render: (value, record) => (
        <div className="price-cell">
          <span className="current-value">{value.toLocaleString()} SEK</span>
          {showYoYComparison && record.priceChange !== 0 && (
            <span className={`change-indicator ${record.priceChange > 0 ? 'positive' : 'negative'}`}>
              ({record.priceChange > 0 ? '+' : ''}{record.priceChange.toFixed(1)}%)
            </span>
          )}
        </div>
      ),
    },
    {
      title: 'Salary',
      dataIndex: 'salary',
      key: 'salary',
      sorter: (a, b) => a.salary - b.salary,
      render: (value, record) => (
        <div className="salary-cell">
          <span className="current-value">{value.toLocaleString()} SEK</span>
          {showYoYComparison && record.salaryChange !== 0 && (
            <span className={`change-indicator ${record.salaryChange > 0 ? 'positive' : 'negative'}`}>
              ({record.salaryChange > 0 ? '+' : ''}{record.salaryChange.toFixed(1)}%)
            </span>
          )}
        </div>
      ),
    },
  ];

  const yoyColumns = showYoYComparison ? [
    {
      title: 'YoY FTE Change',
      key: 'fteChange',
      sorter: (a, b) => a.fteChange - b.fteChange,
      render: (_, record) => (
        <span className={`yoy-change ${record.fteChange > 0 ? 'positive' : record.fteChange < 0 ? 'negative' : 'neutral'}`}>
          {record.fteChange > 0 ? '+' : ''}{record.fteChange}
        </span>
      ),
    },
    {
      title: 'YoY Price Change',
      key: 'priceChange',
      sorter: (a, b) => a.priceChange - b.priceChange,
      render: (_, record) => (
        <span className={`yoy-change ${record.priceChange > 0 ? 'positive' : record.priceChange < 0 ? 'negative' : 'neutral'}`}>
          {record.priceChange > 0 ? '+' : ''}{record.priceChange.toFixed(1)}%
        </span>
      ),
    },
    {
      title: 'YoY Salary Change',
      key: 'salaryChange',
      sorter: (a, b) => a.salaryChange - b.salaryChange,
      render: (_, record) => (
        <span className={`yoy-change ${record.salaryChange > 0 ? 'positive' : record.salaryChange < 0 ? 'negative' : 'neutral'}`}>
          {record.salaryChange > 0 ? '+' : ''}{record.salaryChange.toFixed(1)}%
        </span>
      ),
    },
  ] : [];

  const columns = [...baseColumns, ...yoyColumns];

  return (
    <Card 
      title={`Detailed Data Analysis - Year ${selectedYear}`}
      className="enhanced-data-table"
      extra={
        <Switch
          checkedChildren="Show YoY"
          unCheckedChildren="Current Only"
          checked={showYoYComparison}
          onChange={setShowYoYComparison}
        />
      }
    >
      <Table
        columns={columns}
        dataSource={filteredData}
        loading={loading}
        pagination={{
          pageSize: 20,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) => 
            `${range[0]}-${range[1]} of ${total} items (Year ${selectedYear})`,
        }}
        expandable={{
          expandedRowRender: record => (
            <YearComparisonDetails 
              record={record} 
              selectedYear={selectedYear}
              allYearData={data}
            />
          ),
          rowExpandable: record => record.hasHistoricalData,
        }}
        scroll={{ x: 1200 }}
      />
    </Card>
  );
};
```

The enhanced data table provides a toggle switch that allows users to show or hide year-over-year comparison data. When comparison mode is enabled, additional columns display the changes from the previous year, and inline indicators show the direction and magnitude of changes within the existing columns.

## State Management and Data Flow

### Year Navigation State Management

The year navigation system implements a sophisticated state management approach that ensures consistent data availability and optimal performance across all dashboard components:

```javascript
const useYearNavigationState = (simulationData) => {
  const [state, dispatch] = useReducer(yearNavigationReducer, {
    selectedYear: simulationData.finalYear,
    yearData: {},
    loading: false,
    error: null,
    cachedYears: new Set()
  });

  const loadYearData = useCallback(async (year) => {
    if (state.cachedYears.has(year)) {
      dispatch({ type: 'SET_SELECTED_YEAR', payload: year });
      return;
    }

    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      const yearData = await fetchYearData(year, simulationData.id);
      dispatch({ 
        type: 'LOAD_YEAR_SUCCESS', 
        payload: { year, data: yearData } 
      });
    } catch (error) {
      dispatch({ 
        type: 'LOAD_YEAR_ERROR', 
        payload: error.message 
      });
    }
  }, [state.cachedYears, simulationData.id]);

  const preloadAdjacentYears = useCallback((currentYear) => {
    const adjacentYears = [currentYear - 1, currentYear + 1].filter(year => 
      year >= simulationData.startYear && 
      year <= simulationData.endYear &&
      !state.cachedYears.has(year)
    );

    adjacentYears.forEach(year => {
      fetchYearData(year, simulationData.id).then(data => {
        dispatch({ 
          type: 'CACHE_YEAR_DATA', 
          payload: { year, data } 
        });
      });
    });
  }, [state.cachedYears, simulationData]);

  return {
    ...state,
    loadYearData,
    preloadAdjacentYears
  };
};
```

The state management system implements intelligent caching and preloading strategies to ensure smooth navigation between years. When a user selects a year, the system automatically preloads data for adjacent years to minimize loading times for subsequent navigation actions.

### Data Transformation and Aggregation

The system includes comprehensive data transformation utilities that convert raw simulation data into the formats required by different dashboard components:

```javascript
const transformYearData = (rawData, selectedYear) => {
  const yearData = rawData.filter(item => item.year === selectedYear);
  const previousYearData = rawData.filter(item => item.year === selectedYear - 1);

  const kpiData = calculateKPIs(yearData, previousYearData);
  const chartData = prepareChartData(rawData, selectedYear);
  const tableData = prepareTableData(yearData, previousYearData);

  return {
    kpis: kpiData,
    charts: chartData,
    table: tableData,
    metadata: {
      year: selectedYear,
      hasComparison: previousYearData.length > 0,
      recordCount: yearData.length
    }
  };
};

const calculateKPIs = (currentData, previousData) => {
  const currentKPIs = aggregateKPIs(currentData);
  const previousKPIs = previousData.length > 0 ? aggregateKPIs(previousData) : {};

  return Object.keys(currentKPIs).reduce((acc, key) => {
    const current = currentKPIs[key];
    const previous = previousKPIs[key] || 0;
    const change = previous > 0 ? ((current - previous) / previous) * 100 : 0;

    acc[key] = {
      current,
      previous,
      change,
      trend: change > 0 ? 'up' : change < 0 ? 'down' : 'stable'
    };

    return acc;
  }, {});
};
```

The data transformation system ensures that all components receive consistently formatted data that includes both current values and year-over-year comparison metrics. The system handles edge cases such as missing previous year data and division by zero scenarios.

This comprehensive technical specification provides the foundation for implementing year-over-year navigation functionality that seamlessly integrates with the existing dashboard architecture while providing the temporal analysis capabilities required by executive users.



## Data Structures and API Specifications

### Year-Specific Data Structure

The API responses for year-specific data follow a standardized structure that supports both individual year queries and multi-year aggregations:

```javascript
// Individual Year Data Response
{
  "year": 3,
  "simulationId": "sim_12345",
  "kpis": {
    "netSales": {
      "value": 9586545969,
      "unit": "SEK",
      "target": 10000000000,
      "baseline": 8500000000
    },
    "ebitda": {
      "value": 4448967673,
      "unit": "SEK",
      "target": 4500000000,
      "baseline": 3800000000
    },
    "margin": {
      "value": 46.4,
      "unit": "percentage",
      "target": 50.0,
      "baseline": 44.7
    },
    "totalGrowth": {
      "value": 19.2,
      "unit": "percentage",
      "target": 20.0,
      "baseline": 15.0
    },
    "consultantGrowth": {
      "value": 81.0,
      "unit": "percentage",
      "target": 85.0,
      "baseline": 75.0
    },
    "nonDebitRatio": {
      "value": 18.9,
      "unit": "percentage",
      "target": 20.0,
      "baseline": 16.5
    }
  },
  "detailedData": [
    {
      "office": "Stockholm",
      "level": "AM",
      "role": "Associate Manager",
      "journey": "970 (821)",
      "fte": 149,
      "delta": 25,
      "price": 850000,
      "salary": 650000
    }
    // ... additional records
  ],
  "metadata": {
    "recordCount": 156,
    "lastUpdated": "2024-01-15T10:30:00Z",
    "dataQuality": "complete"
  }
}

// Multi-Year Comparison Response
{
  "simulationId": "sim_12345",
  "yearRange": {
    "start": 1,
    "end": 5
  },
  "yearlyData": [
    {
      "year": 1,
      "kpis": { /* KPI data for year 1 */ },
      "summary": {
        "totalFTE": 2351,
        "totalRevenue": 7500000000,
        "averageMargin": 42.1
      }
    },
    {
      "year": 2,
      "kpis": { /* KPI data for year 2 */ },
      "summary": {
        "totalFTE": 2580,
        "totalRevenue": 8200000000,
        "averageMargin": 43.8
      }
    }
    // ... additional years
  ],
  "trends": {
    "netSales": [
      { "year": 1, "value": 7500000000 },
      { "year": 2, "value": 8200000000 },
      { "year": 3, "value": 9586545969 },
      { "year": 4, "value": 10800000000 },
      { "year": 5, "value": 12100000000 }
    ],
    "margin": [
      { "year": 1, "value": 42.1 },
      { "year": 2, "value": 43.8 },
      { "year": 3, "value": 46.4 },
      { "year": 4, "value": 48.2 },
      { "year": 5, "value": 50.1 }
    ]
    // ... additional KPI trends
  }
}
```

### API Endpoint Specifications

The year navigation functionality requires several API endpoints to support efficient data retrieval and caching:

```javascript
// Get data for a specific year
GET /api/simulations/{simulationId}/years/{year}
Response: Individual Year Data Response

// Get summary data for all years
GET /api/simulations/{simulationId}/years/summary
Response: Multi-Year Comparison Response

// Get trend data for specific KPIs across all years
GET /api/simulations/{simulationId}/trends?kpis=netSales,margin,totalGrowth
Response: {
  "trends": {
    "netSales": [/* yearly values */],
    "margin": [/* yearly values */],
    "totalGrowth": [/* yearly values */]
  }
}

// Get year-over-year comparison for specific year
GET /api/simulations/{simulationId}/years/{year}/comparison
Response: {
  "currentYear": { /* current year data */ },
  "previousYear": { /* previous year data */ },
  "changes": {
    "kpis": {
      "netSales": {
        "absolute": 1086545969,
        "percentage": 12.8,
        "trend": "up"
      }
      // ... other KPI changes
    },
    "detailedData": [
      {
        "office": "Stockholm",
        "fteChange": 25,
        "priceChange": 8.5,
        "salaryChange": 5.2
      }
      // ... other office changes
    ]
  }
}
```

### Caching Strategy

The client-side caching strategy optimizes performance by storing frequently accessed year data and implementing intelligent preloading:

```javascript
class YearDataCache {
  constructor(maxSize = 10) {
    this.cache = new Map();
    this.maxSize = maxSize;
    this.accessOrder = [];
  }

  get(year) {
    if (this.cache.has(year)) {
      this.updateAccessOrder(year);
      return this.cache.get(year);
    }
    return null;
  }

  set(year, data) {
    if (this.cache.size >= this.maxSize && !this.cache.has(year)) {
      const leastRecentYear = this.accessOrder.shift();
      this.cache.delete(leastRecentYear);
    }

    this.cache.set(year, {
      data,
      timestamp: Date.now(),
      accessCount: 1
    });

    this.updateAccessOrder(year);
  }

  updateAccessOrder(year) {
    const index = this.accessOrder.indexOf(year);
    if (index > -1) {
      this.accessOrder.splice(index, 1);
    }
    this.accessOrder.push(year);

    if (this.cache.has(year)) {
      this.cache.get(year).accessCount++;
    }
  }

  preload(years) {
    return Promise.all(
      years.map(year => {
        if (!this.cache.has(year)) {
          return this.fetchYearData(year);
        }
        return Promise.resolve();
      })
    );
  }
}
```

The caching system implements a Least Recently Used (LRU) eviction policy and tracks access patterns to optimize preloading decisions. The system automatically preloads adjacent years when a user selects a specific year, reducing perceived loading times for navigation actions.

