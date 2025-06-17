# Technical Design Specifications: KPI and Data Visualization System

## Overview

This document provides comprehensive technical specifications for implementing an improved KPI and data visualization system for the organization simulation platform. The design prioritizes key performance indicators while maintaining access to supporting data through a modern, interactive dashboard interface built with Ant Design components.

## Architecture Overview

### Component Hierarchy

The KPI dashboard follows a hierarchical component structure that ensures optimal performance and maintainability:

```
KPIDashboard (Container)
├── DashboardHeader (Navigation & Filters)
├── KPICardGrid (Primary KPI Display)
│   ├── KPICard (Individual KPI Component)
│   │   ├── KPIValue (Large Number Display)
│   │   ├── TrendIndicator (Arrow & Percentage)
│   │   └── MiniChart (Sparkline Visualization)
├── VisualizationSection (Charts & Graphs)
│   ├── TrendChart (Time Series Analysis)
│   └── ComparisonChart (Office/Role Comparison)
└── DataTableSection (Detailed Data)
    ├── FilterControls (Search & Filter)
    └── ExpandableTable (Drill-down Data)
```

### State Management Architecture

The application uses a centralized state management approach with React Context and useReducer for complex state operations:

```javascript
const DashboardContext = createContext();

const dashboardReducer = (state, action) => {
  switch (action.type) {
    case 'SET_TIME_PERIOD':
      return { ...state, timePeriod: action.payload };
    case 'SET_SELECTED_KPI':
      return { ...state, selectedKPI: action.payload };
    case 'SET_FILTER_CRITERIA':
      return { ...state, filters: { ...state.filters, ...action.payload } };
    case 'SET_DRILL_DOWN_DATA':
      return { ...state, drillDownData: action.payload };
    default:
      return state;
  }
};
```

## KPI Card Component Specifications

### Component Structure

The KPI card represents the core building block of the dashboard, designed to maximize visual impact while maintaining clarity:

```javascript
const KPICard = ({ 
  title, 
  value, 
  unit, 
  trend, 
  trendPercentage, 
  baseline, 
  target, 
  sparklineData, 
  onClick 
}) => {
  return (
    <Card 
      className="kpi-card"
      hoverable
      onClick={onClick}
      style={{
        height: '180px',
        cursor: 'pointer',
        transition: 'all 0.3s ease'
      }}
    >
      <div className="kpi-header">
        <Text type="secondary" className="kpi-title">{title}</Text>
      </div>
      <div className="kpi-value-section">
        <Text className="kpi-value">{formatValue(value, unit)}</Text>
        <TrendIndicator trend={trend} percentage={trendPercentage} />
      </div>
      <div className="kpi-context">
        <Text type="secondary">Baseline: {formatValue(baseline, unit)}</Text>
        <Text type="secondary">Target: {formatValue(target, unit)}</Text>
      </div>
      <div className="kpi-sparkline">
        <MiniChart data={sparklineData} />
      </div>
    </Card>
  );
};
```

### Styling Specifications

The KPI cards use a carefully designed visual hierarchy that emphasizes the primary value while providing essential context:

```css
.kpi-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #f0f0f0;
  padding: 24px;
  background: #ffffff;
}

.kpi-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.kpi-title {
  font-size: 14px;
  font-weight: 500;
  color: #8c8c8c;
  margin-bottom: 8px;
}

.kpi-value {
  font-size: 32px;
  font-weight: 600;
  color: #1890ff;
  line-height: 1.2;
  margin-bottom: 4px;
}

.kpi-context {
  display: flex;
  justify-content: space-between;
  margin: 12px 0;
  font-size: 12px;
}

.kpi-sparkline {
  height: 40px;
  margin-top: 16px;
}
```

### Responsive Behavior

The KPI cards adapt to different screen sizes while maintaining readability and visual impact:

- **Desktop (≥1200px)**: 3 cards per row, full feature set
- **Tablet (768-1199px)**: 2 cards per row, slightly reduced padding
- **Mobile (<768px)**: 1 card per row, optimized touch targets

## Trend Indicator Component

### Visual Design

The trend indicator provides immediate visual feedback about KPI performance using color coding and directional arrows:

```javascript
const TrendIndicator = ({ trend, percentage }) => {
  const getTrendColor = (trend) => {
    switch (trend) {
      case 'up': return '#52c41a';
      case 'down': return '#f5222d';
      case 'stable': return '#faad14';
      default: return '#8c8c8c';
    }
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'up': return <ArrowUpOutlined />;
      case 'down': return <ArrowDownOutlined />;
      case 'stable': return <MinusOutlined />;
      default: return null;
    }
  };

  return (
    <span 
      className="trend-indicator"
      style={{ color: getTrendColor(trend) }}
    >
      {getTrendIcon(trend)}
      <span className="trend-percentage">{percentage}%</span>
    </span>
  );
};
```

### Accessibility Considerations

The trend indicator includes both visual and textual indicators to ensure accessibility:

- **Color coding** for quick visual recognition
- **Icon symbols** for directional indication
- **Percentage values** for precise measurement
- **ARIA labels** for screen reader compatibility

## Chart Component Specifications

### Trend Chart Implementation

The trend chart displays historical KPI data using Ant Design Charts with interactive features:

```javascript
import { Line } from '@ant-design/plots';

const TrendChart = ({ data, selectedKPI }) => {
  const config = {
    data,
    xField: 'month',
    yField: 'value',
    seriesField: 'metric',
    smooth: true,
    animation: {
      appear: {
        animation: 'path-in',
        duration: 1000,
      },
    },
    color: ['#1890ff', '#52c41a', '#faad14'],
    point: {
      size: 4,
      shape: 'circle',
    },
    tooltip: {
      showMarkers: true,
      shared: true,
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
    <Card title="Trend Analysis" className="chart-container">
      <Line {...config} />
    </Card>
  );
};
```

### Comparison Chart Implementation

The comparison chart shows performance across different offices or organizational levels:

```javascript
import { Column } from '@ant-design/plots';

const ComparisonChart = ({ data, comparisonType }) => {
  const config = {
    data,
    xField: 'office',
    yField: 'value',
    seriesField: 'metric',
    isGroup: true,
    columnStyle: {
      radius: [4, 4, 0, 0],
    },
    color: ['#1890ff', '#52c41a', '#faad14'],
    legend: {
      position: 'top-right',
    },
    tooltip: {
      showMarkers: false,
    },
    interactions: [
      {
        type: 'active-region',
        enable: false,
      },
    ],
    connectedArea: {
      style: (oldStyle, element) => {
        return {
          fill: 'rgba(0,0,0,0.25)',
          stroke: oldStyle.fill,
          lineWidth: 0.5,
        };
      },
    },
  };

  return (
    <Card title={`Performance by ${comparisonType}`} className="chart-container">
      <Column {...config} />
    </Card>
  );
};
```

## Data Table Component Specifications

### Enhanced Table Features

The data table provides comprehensive drill-down capabilities while maintaining performance with large datasets:

```javascript
import { Table, Input, Select, Button } from 'antd';
const { Search } = Input;

const DataTableSection = ({ data, loading, onDrillDown }) => {
  const [filteredData, setFilteredData] = useState(data);
  const [searchText, setSearchText] = useState('');
  const [selectedOffice, setSelectedOffice] = useState('all');

  const columns = [
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
      render: (value) => value.toLocaleString(),
    },
    {
      title: 'Delta',
      dataIndex: 'delta',
      key: 'delta',
      sorter: (a, b) => a.delta - b.delta,
      render: (value) => (
        <span style={{ color: value >= 0 ? '#52c41a' : '#f5222d' }}>
          {value >= 0 ? '+' : ''}{value}
        </span>
      ),
    },
    {
      title: 'Price',
      dataIndex: 'price',
      key: 'price',
      sorter: (a, b) => a.price - b.price,
      render: (value) => `${value.toLocaleString()} SEK`,
    },
    {
      title: 'Salary',
      dataIndex: 'salary',
      key: 'salary',
      sorter: (a, b) => a.salary - b.salary,
      render: (value) => `${value.toLocaleString()} SEK`,
    },
  ];

  return (
    <Card title="Detailed Data Analysis" className="data-table-section">
      <div className="table-controls">
        <Search
          placeholder="Search all fields"
          allowClear
          enterButton="Search"
          size="large"
          onSearch={handleSearch}
          style={{ width: 300, marginBottom: 16 }}
        />
        <Select
          placeholder="Filter by office"
          style={{ width: 200, marginLeft: 16 }}
          onChange={handleOfficeFilter}
          allowClear
        >
          <Option value="all">All Offices</Option>
          <Option value="stockholm">Stockholm</Option>
          <Option value="munich">Munich</Option>
          <Option value="hamburg">Hamburg</Option>
        </Select>
      </div>
      <Table
        columns={columns}
        dataSource={filteredData}
        loading={loading}
        pagination={{
          pageSize: 20,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) => 
            `${range[0]}-${range[1]} of ${total} items`,
        }}
        expandable={{
          expandedRowRender: record => (
            <div style={{ margin: 0 }}>
              <p>Additional details for {record.office}</p>
              <Button onClick={() => onDrillDown(record)}>
                View Detailed Analysis
              </Button>
            </div>
          ),
          rowExpandable: record => record.hasDetails,
        }}
        scroll={{ x: 800 }}
      />
    </Card>
  );
};
```

### Performance Optimization

The data table implements several performance optimization strategies:

- **Virtual scrolling** for large datasets (>1000 rows)
- **Debounced search** to prevent excessive API calls
- **Memoized filtering** to avoid unnecessary re-renders
- **Lazy loading** for expandable row content

## Interactive Features and User Experience

### Drill-Down Navigation

The dashboard implements a sophisticated drill-down system that maintains context while allowing deep exploration:

```javascript
const useDrillDown = () => {
  const [navigationStack, setNavigationStack] = useState([]);
  const [currentView, setCurrentView] = useState('overview');

  const drillDown = (target, filters) => {
    setNavigationStack(prev => [...prev, { view: currentView, filters }]);
    setCurrentView(target);
  };

  const drillUp = () => {
    if (navigationStack.length > 0) {
      const previous = navigationStack[navigationStack.length - 1];
      setCurrentView(previous.view);
      setNavigationStack(prev => prev.slice(0, -1));
    }
  };

  return { currentView, drillDown, drillUp, navigationStack };
};
```

### Real-Time Data Updates

The system supports real-time data updates through WebSocket connections:

```javascript
const useRealTimeData = (endpoint) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8080${endpoint}`);
    
    ws.onmessage = (event) => {
      const newData = JSON.parse(event.data);
      setData(newData);
      setLoading(false);
    };

    ws.onerror = (error) => {
      setError(error);
      setLoading(false);
    };

    return () => ws.close();
  }, [endpoint]);

  return { data, loading, error };
};
```

## Responsive Design Implementation

### Breakpoint System

The dashboard uses a comprehensive breakpoint system that ensures optimal display across all device types:

```css
/* Extra small devices (phones, 600px and down) */
@media only screen and (max-width: 600px) {
  .kpi-card-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .kpi-value {
    font-size: 24px;
  }
  
  .chart-container {
    height: 250px;
  }
}

/* Small devices (portrait tablets and large phones, 600px and up) */
@media only screen and (min-width: 600px) {
  .kpi-card-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
  }
}

/* Medium devices (landscape tablets, 768px and up) */
@media only screen and (min-width: 768px) {
  .kpi-card-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
  }
  
  .chart-container {
    height: 350px;
  }
}

/* Large devices (laptops/desktops, 992px and up) */
@media only screen and (min-width: 992px) {
  .dashboard-layout {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 32px;
  }
}
```

### Touch-Friendly Interactions

Mobile and tablet interfaces include enhanced touch interactions:

- **Larger touch targets** (minimum 44px) for all interactive elements
- **Swipe gestures** for navigating between chart views
- **Pull-to-refresh** functionality for data updates
- **Haptic feedback** for important actions (where supported)

## Accessibility Implementation

### WCAG 2.1 AA Compliance

The dashboard meets WCAG 2.1 AA standards through comprehensive accessibility features:

```javascript
const AccessibleKPICard = ({ title, value, trend, ...props }) => {
  const trendDescription = {
    up: 'increasing',
    down: 'decreasing',
    stable: 'stable'
  };

  return (
    <Card
      role="button"
      tabIndex={0}
      aria-label={`${title}: ${value}, trend is ${trendDescription[trend]}`}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          props.onClick();
        }
      }}
      {...props}
    >
      <div aria-live="polite" aria-atomic="true">
        {/* Card content */}
      </div>
    </Card>
  );
};
```

### Screen Reader Support

All interactive elements include comprehensive screen reader support:

- **Semantic HTML** structure with proper heading hierarchy
- **ARIA labels** for complex interactive elements
- **Live regions** for dynamic content updates
- **Skip navigation** links for keyboard users
- **Focus management** for modal dialogs and overlays

## Performance Specifications

### Loading Performance

The dashboard implements aggressive performance optimization:

- **Code splitting** at the route level reduces initial bundle size
- **Lazy loading** of chart components improves perceived performance
- **Image optimization** with WebP format and responsive sizing
- **CDN delivery** for static assets

### Runtime Performance

Runtime performance is optimized through:

- **React.memo** for expensive component renders
- **useMemo** and **useCallback** for expensive calculations
- **Virtual scrolling** for large data tables
- **Debounced inputs** to prevent excessive API calls

### Memory Management

Memory usage is controlled through:

- **Cleanup functions** in useEffect hooks
- **Event listener removal** on component unmount
- **Data pagination** to limit memory footprint
- **Garbage collection** optimization for large datasets

## Testing Strategy

### Unit Testing

Component testing covers all interactive elements:

```javascript
describe('KPICard Component', () => {
  test('displays correct value and trend', () => {
    render(
      <KPICard 
        title="Net Sales" 
        value={9586545969} 
        trend="up" 
        trendPercentage={175.9} 
      />
    );
    
    expect(screen.getByText('Net Sales')).toBeInTheDocument();
    expect(screen.getByText('9,586,545,969')).toBeInTheDocument();
    expect(screen.getByText('+175.9%')).toBeInTheDocument();
  });

  test('handles click interactions', () => {
    const mockClick = jest.fn();
    render(<KPICard onClick={mockClick} />);
    
    fireEvent.click(screen.getByRole('button'));
    expect(mockClick).toHaveBeenCalled();
  });
});
```

### Integration Testing

Integration tests verify component interactions:

```javascript
describe('Dashboard Integration', () => {
  test('KPI card click updates chart data', async () => {
    render(<KPIDashboard />);
    
    fireEvent.click(screen.getByLabelText(/Net Sales/));
    
    await waitFor(() => {
      expect(screen.getByText('Net Sales Trend')).toBeInTheDocument();
    });
  });
});
```

### Accessibility Testing

Automated accessibility testing ensures compliance:

```javascript
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

test('dashboard has no accessibility violations', async () => {
  const { container } = render(<KPIDashboard />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

This comprehensive technical specification provides the foundation for implementing a modern, accessible, and performant KPI dashboard that prioritizes key metrics while maintaining access to detailed supporting data.

