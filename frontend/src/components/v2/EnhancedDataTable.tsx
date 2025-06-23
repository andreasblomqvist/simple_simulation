import React, { useState, useMemo, useCallback, useRef, useEffect } from 'react';
import { 
  Table, 
  Card, 
  Input, 
  Select, 
  Button, 
  Space, 
  Switch, 
  Tooltip, 
  Tag, 
  Typography,
  Dropdown,
  Menu,
  Checkbox,
  Progress,
  Row,
  Col,
  message
} from 'antd';
import { 
  SearchOutlined, 
  FilterOutlined, 
  DownloadOutlined, 
  ExpandAltOutlined,
  ShrinkOutlined,
  TableOutlined,
  BarChartOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  MinusOutlined,
  InfoCircleOutlined,
  EyeOutlined,
  EyeInvisibleOutlined,
  SettingOutlined
} from '@ant-design/icons';
import type { ColumnsType, TableProps } from 'antd/es/table';
import { useYearNavigation } from './YearNavigationProvider';
import { exportChartData } from './ChartUtilities';

const { Search } = Input;
const { Option } = Select;
const { Text, Title } = Typography;

// Enhanced data types for the table
export interface TableDataRow {
  key: string;
  id: string;
  category: string;
  subCategory?: string;
  office?: string;
  journey?: string;
  level?: string;
  currentYear: {
    year: number;
    value: number;
    unit: string;
    formatted: string;
  };
  previousYear?: {
    year: number;
    value: number;
    unit: string;
    formatted: string;
  };
  change?: {
    absolute: number;
    percentage: number;
    trend: 'up' | 'down' | 'stable';
    significance: 'high' | 'medium' | 'low';
  };
  multiYear?: {
    [year: number]: {
      value: number;
      formatted: string;
    };
  };
  metadata?: {
    source?: string;
    lastUpdated?: string;
    confidence?: number;
    projected?: boolean;
  };
}

export interface TableFilterState {
  searchText: string;
  category: string[];
  office: string[];
  journey: string[];
  level: string[];
  trendFilter: 'all' | 'up' | 'down' | 'stable';
  significanceFilter: 'all' | 'high' | 'medium' | 'low';
  projectedOnly: boolean;
}

export interface TableViewSettings {
  showYoYColumns: boolean;
  showMultiYearProgression: boolean;
  showChangeIndicators: boolean;
  showMetadata: boolean;
  compactView: boolean;
  expandedRows: string[];
  columnVisibility: { [key: string]: boolean };
}

interface EnhancedDataTableProps {
  data: any[];
  baselineData?: any[];
  loading?: boolean;
  title?: string;
  className?: string;
  height?: number;
  virtualized?: boolean;
  exportFileName?: string;
  onRowClick?: (record: any) => void;
  onFilterChange?: (filters: TableFilterState) => void;
  customColumns?: ColumnsType<any>;
  showAdvancedFilters?: boolean;
}

const processDataForTable = (kpiData: any[], baselineConfig: any[]) => {
  if (!kpiData || kpiData.length === 0) return [];

  const baselineMap = new Map(baselineConfig.map(office => [office.name, office]));

  return kpiData.map((office: any) => {
    const baselineOffice = baselineMap.get(office.office);
    const officeData: any = { ...office };
    
    const officeBaselineFTE = baselineOffice ? baselineOffice.total_fte || 0 : 0;
    officeData.totalDelta = office.total - officeBaselineFTE;

    const levels = office.levels ? Object.keys(office.levels) : Object.keys(office).filter(k => !['key', 'office', 'total', 'totalDelta', 'Non-debit Ratio'].includes(k) && !k.endsWith('Delta'));

    levels.forEach((levelName: string) => {
      let levelBaselineFTE = 0;
      if (baselineOffice && baselineOffice.roles) {
        if (levelName === 'Operations' && baselineOffice.roles.Operations) {
          const opsBaseline = baselineOffice.roles.Operations;
          if (opsBaseline && 'fte' in opsBaseline) {
            levelBaselineFTE = opsBaseline.fte;
          }
        } else if (baselineOffice.roles.Consultant && baselineOffice.roles.Consultant[levelName]) {
          const baselineLevel = baselineOffice.roles.Consultant[levelName];
          if (baselineLevel && 'fte' in baselineLevel) {
            levelBaselineFTE = baselineLevel.fte;
          }
        }
      }
      const currentFTE = office.levels ? office.levels[levelName] : office[levelName];
      officeData[`${levelName}Delta`] = currentFTE - levelBaselineFTE;
    });

    return officeData;
  });
};

/**
 * EnhancedDataTable Component
 * 
 * Professional data table with advanced features:
 * - Year-specific filtering and navigation integration
 * - Toggle-able YoY comparison columns
 * - Expandable rows for multi-year progression
 * - Advanced search and filtering capabilities
 * - Export functionality with customizable formats
 * - Table virtualization for large datasets
 * - Responsive design with mobile optimization
 */
export const EnhancedDataTable: React.FC<EnhancedDataTableProps> = ({
  data,
  baselineData = [],
  loading = false,
  title = "Simulation Data",
  className = '',
  height = 600,
  virtualized = false,
  exportFileName = 'simulation_data',
  onRowClick,
  onFilterChange,
  customColumns,
  showAdvancedFilters = true
}) => {
  const { selectedYear, availableYears } = useYearNavigation();
  const tableRef = useRef<any>(null);

  // State management
  const [filters, setFilters] = useState<TableFilterState>({
    searchText: '',
    category: [],
    office: [],
    journey: [],
    level: [],
    trendFilter: 'all',
    significanceFilter: 'all',
    projectedOnly: false
  });

  const [viewSettings, setViewSettings] = useState<TableViewSettings>({
    showYoYColumns: true,
    showMultiYearProgression: false,
    showChangeIndicators: true,
    showMetadata: false,
    compactView: false,
    expandedRows: [],
    columnVisibility: {}
  });

  const [selectedRows, setSelectedRows] = useState<string[]>([]);
  const [columnSorter, setColumnSorter] = useState<{ field?: string; order?: 'ascend' | 'descend' }>({});

  const processedData = useMemo(() => {
    if (!baselineData || baselineData.length === 0) {
      return data.map((d: any) => {
        const levels = d.levels ? Object.keys(d.levels) : Object.keys(d).filter(k => !['key', 'office', 'total', 'Non-debit Ratio'].includes(k));
        const deltas = levels.reduce((acc: any, key: string) => {
          acc[`${key}Delta`] = d.levels ? d.levels[key] : d[key];
          return acc;
        }, {} as any);
        return {
          ...d,
          totalDelta: d.total,
          ...deltas
        };
      });
    }
    return processDataForTable(data, baselineData);
  }, [data, baselineData]);

  // Filter data based on current filters
  const filteredData = useMemo(() => {
    return processedData.filter((row: any) => {
      // Search text filter
      if (filters.searchText) {
        const searchLower = filters.searchText.toLowerCase();
        const searchableFields = [
          row.category,
          row.subCategory,
          row.office,
          row.journey,
          row.level
        ].filter(Boolean).join(' ').toLowerCase();
        
        if (!searchableFields.includes(searchLower)) return false;
      }

      // Category filter
      if (filters.category.length > 0 && !filters.category.includes(row.category)) {
        return false;
      }

      // Office filter
      if (filters.office.length > 0 && row.office && !filters.office.includes(row.office)) {
        return false;
      }

      // Journey filter
      if (filters.journey.length > 0 && row.journey && !filters.journey.includes(row.journey)) {
        return false;
      }

      // Level filter
      if (filters.level.length > 0 && row.level && !filters.level.includes(row.level)) {
        return false;
      }

      // Trend filter
      if (filters.trendFilter !== 'all' && row.change?.trend !== filters.trendFilter) {
        return false;
      }

      // Significance filter
      if (filters.significanceFilter !== 'all' && row.change?.significance !== filters.significanceFilter) {
        return false;
      }

      // Projected only filter
      if (filters.projectedOnly && !row.metadata?.projected) {
        return false;
      }

      return true;
    });
  }, [processedData, filters]);

  // Get unique values for filter options
  const filterOptions = useMemo(() => {
    const categories = [...new Set(processedData.map((row: any) => row.category))];
    const offices = [...new Set(processedData.map((row: any) => row.office).filter(Boolean))];
    const journeys = [...new Set(processedData.map((row: any) => row.journey).filter(Boolean))];
    const levels = [...new Set(processedData.map((row: any) => row.level).filter(Boolean))];

    return { categories, offices, journeys, levels };
  }, [processedData]);

  // Handle filter changes
  const handleFilterChange = useCallback((newFilters: Partial<TableFilterState>) => {
    const updatedFilters = { ...filters, ...newFilters };
    setFilters(updatedFilters);
    onFilterChange?.(updatedFilters);
  }, [filters, onFilterChange]);

  // Handle view settings changes
  const handleViewSettingChange = useCallback((setting: keyof TableViewSettings, value: any) => {
    setViewSettings(prev => ({ ...prev, [setting]: value }));
  }, []);

  const getColumnSearchProps = (dataIndex: string) => ({
    filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters }: any) => (
      <div style={{ padding: 8 }}>
        <Input
          placeholder={`Search ${dataIndex}`}
          value={selectedKeys[0]}
          onChange={e => setSelectedKeys(e.target.value ? [e.target.value] : [])}
          onPressEnter={() => confirm()}
          style={{ marginBottom: 8, display: 'block' }}
        />
        <Space>
          <Button
            type="primary"
            onClick={() => confirm()}
            icon={<SearchOutlined />}
            size="small"
            style={{ width: 90 }}
          >
            Search
          </Button>
          <Button onClick={() => clearFilters()} size="small" style={{ width: 90 }}>
            Reset
          </Button>
        </Space>
      </div>
    ),
    filterIcon: (filtered: boolean) => <SearchOutlined style={{ color: filtered ? '#1890ff' : undefined }} />,
    onFilter: (value: any, record: any) =>
      record[dataIndex]
        ? record[dataIndex].toString().toLowerCase().includes(value.toLowerCase())
        : '',
  });

  const formatChangeIndicator = (change?: TableDataRow['change']) => {
    if (!change) return null;
    const { absolute, percentage, trend } = change;
    const color = trend === 'up' ? 'green' : trend === 'down' ? 'red' : 'gray';
    const icon = trend === 'up' ? <ArrowUpOutlined /> : trend === 'down' ? <ArrowDownOutlined /> : <MinusOutlined />;

    return (
      <Tag color={color} icon={icon}>
        {absolute.toFixed(2)} ({percentage.toFixed(1)}%)
      </Tag>
    );
  };
  
  // --- Define Columns ---
  const columns: ColumnsType<any> = useMemo(() => {
    if (!processedData || processedData.length === 0) return [];

    const baseColumns: ColumnsType<any> = [
      {
        title: 'Office',
        dataIndex: 'office',
        key: 'office',
        fixed: 'left',
        width: 150,
        sorter: (a, b) => a.office.localeCompare(b.office),
      },
      {
        title: 'Total',
        dataIndex: 'total',
        key: 'total',
        width: 120,
        sorter: (a, b) => a.total - b.total,
        render: (value, record) => (
          <div>
            <Text strong>{value != null ? value.toFixed(1) : '-'}</Text><br />
            <Text type="secondary" style={{ color: record.totalDelta >= 0 ? 'green' : 'red' }}>
              ({record.totalDelta >= 0 ? '+' : ''}{record.totalDelta != null ? record.totalDelta.toFixed(1) : '-'})
            </Text>
          </div>
        )
      }
    ];
    
    const levelColumns: ColumnsType<any> = [];
    const sampleRow = processedData[0];
    const levels = sampleRow.levels ? Object.keys(sampleRow.levels) : Object.keys(sampleRow).filter(k => !['key', 'office', 'total', 'totalDelta', 'Non-debit Ratio'].includes(k) && !k.endsWith('Delta'));
    
    levels.forEach((level: string) => {
      levelColumns.push({
        title: level,
        dataIndex: ['levels', level],
        key: level,
        width: 100,
        sorter: (a, b) => ((a.levels?.[level] || a[level] || 0) - (b.levels?.[level] || b[level] || 0)),
        render: (value, record) => {
          const currentValue = record.levels ? record.levels[level] : record[level];
          const deltaValue = record[`${level}Delta`];
          return (
            <div>
              <Text>{currentValue != null ? currentValue.toFixed(1) : '-'}</Text><br/>
              <Text type="secondary" style={{ color: deltaValue >= 0 ? 'green' : 'red' }}>
                ({deltaValue >= 0 ? '+' : ''}{deltaValue != null ? deltaValue.toFixed(1) : '-'})
              </Text>
            </div>
          );
        }
      });
    });

    const ratioColumn = {
        title: 'Non-debit Ratio',
        dataIndex: 'Non-debit Ratio',
        key: 'non_debit_ratio',
        width: 120,
    };

    return [...baseColumns, ...levelColumns, ratioColumn];
  }, [processedData, columnSorter]);

  const handleRowClick = (record: any) => {
    if (onRowClick) {
      onRowClick(record);
    }
  };
  
  const finalColumns = customColumns || columns;
  
  const handleExport = (format: 'csv' | 'json' = 'csv') => {
    exportChartData(
      filteredData, 
      `${exportFileName}_${selectedYear}`,
      format
    );
    message.success(`Data exported as ${format.toUpperCase()}`);
  };

  const tableSettingsMenu = (
    <Menu>
      <Menu.Item key="compact">
        <Switch 
          checked={viewSettings.compactView} 
          onChange={(checked) => handleViewSettingChange('compactView', checked)} 
          size="small"
        />
        <Text style={{ marginLeft: 8 }}>Compact View</Text>
      </Menu.Item>
      <Menu.Item key="yoy">
        <Switch 
          checked={viewSettings.showYoYColumns} 
          onChange={(checked) => handleViewSettingChange('showYoYColumns', checked)} 
          size="small"
        />
        <Text style={{ marginLeft: 8 }}>Show YoY Change</Text>
      </Menu.Item>
      <Menu.Item key="indicators">
        <Switch 
          checked={viewSettings.showChangeIndicators} 
          onChange={(checked) => handleViewSettingChange('showChangeIndicators', checked)} 
          size="small"
        />
        <Text style={{ marginLeft: 8 }}>Show Trend Indicators</Text>
      </Menu.Item>
    </Menu>
  );

  return (
    <Card 
      title={title}
      className={className}
      variant="borderless"
      extra={
        <Space>
          <Search
            placeholder="Search..."
            onSearch={value => handleFilterChange({ searchText: value })}
            style={{ width: 200 }}
          />
          {showAdvancedFilters && (
            <Dropdown overlay={
              <Menu>
                <Menu.SubMenu title="Filter by Office">
                  <Select
                    mode="multiple"
                    allowClear
                    style={{ width: '100%' }}
                    placeholder="Select offices"
                    onChange={(value) => handleFilterChange({ office: value })}
                    options={filterOptions.offices.map(o => ({ label: o, value: o }))}
                  />
                </Menu.SubMenu>
              </Menu>
            } trigger={['click']}>
              <Button icon={<FilterOutlined />}>Filters</Button>
            </Dropdown>
          )}
          <Dropdown overlay={tableSettingsMenu} trigger={['click']}>
            <Button icon={<SettingOutlined />}>View</Button>
          </Dropdown>
          <Button 
            icon={<DownloadOutlined />}
            onClick={() => handleExport('csv')}
          >
            Export
          </Button>
        </Space>
      }
    >
      <Table<any>
        ref={tableRef}
        columns={finalColumns}
        dataSource={filteredData}
        loading={loading}
        size={viewSettings.compactView ? 'small' : 'middle'}
        rowKey="key"
        scroll={ height ? { y: height } : {}}
        pagination={{ pageSize: 20, showSizeChanger: true }}
        onRow={(record) => ({
          onClick: () => handleRowClick(record),
        })}
        sortDirections={['descend', 'ascend']}
        onChange={(pagination, filters, sorter: any) => {
          setColumnSorter({ field: sorter.field, order: sorter.order });
        }}
      />
    </Card>
  );
};

export default EnhancedDataTable; 