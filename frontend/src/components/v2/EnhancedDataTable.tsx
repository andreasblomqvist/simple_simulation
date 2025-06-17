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
  Col
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
  data: TableDataRow[];
  loading?: boolean;
  title?: string;
  className?: string;
  height?: number;
  virtualized?: boolean;
  exportFileName?: string;
  onRowClick?: (record: TableDataRow) => void;
  onFilterChange?: (filters: TableFilterState) => void;
  customColumns?: ColumnsType<TableDataRow>;
  showAdvancedFilters?: boolean;
}

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

  // Filter data based on current filters
  const filteredData = useMemo(() => {
    return data.filter(row => {
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
  }, [data, filters]);

  // Get unique values for filter options
  const filterOptions = useMemo(() => {
    const categories = [...new Set(data.map(row => row.category))];
    const offices = [...new Set(data.map(row => row.office).filter(Boolean))];
    const journeys = [...new Set(data.map(row => row.journey).filter(Boolean))];
    const levels = [...new Set(data.map(row => row.level).filter(Boolean))];

    return { categories, offices, journeys, levels };
  }, [data]);

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

  // Format change indicator
  const formatChangeIndicator = (change?: TableDataRow['change']) => {
    if (!change) return null;

    const { percentage, trend, significance } = change;
    const color = trend === 'up' ? '#52c41a' : trend === 'down' ? '#ff4d4f' : '#8c8c8c';
    const icon = trend === 'up' ? <ArrowUpOutlined /> : trend === 'down' ? <ArrowDownOutlined /> : <MinusOutlined />;
    
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
        <span style={{ color }}>{icon}</span>
        <Text style={{ color, fontWeight: significance === 'high' ? 'bold' : 'normal' }}>
          {percentage > 0 ? '+' : ''}{percentage.toFixed(1)}%
        </Text>
        {significance === 'high' && (
          <Tooltip title="Statistically significant change">
            <InfoCircleOutlined style={{ fontSize: '12px', color: '#faad14' }} />
          </Tooltip>
        )}
      </div>
    );
  };

  // Define base columns
  const baseColumns: ColumnsType<TableDataRow> = [
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      width: 150,
      fixed: 'left',
      sorter: (a, b) => a.category.localeCompare(b.category),
      filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters }) => (
        <div style={{ padding: 8 }}>
          <Select
            mode="multiple"
            style={{ width: 200 }}
            placeholder="Select categories"
            value={selectedKeys as string[]}
            onChange={(values) => setSelectedKeys(values)}
            options={filterOptions.categories.map(cat => ({ label: cat, value: cat }))}
          />
          <div style={{ marginTop: 8 }}>
            <Button
              type="primary"
              size="small"
              onClick={() => confirm()}
              style={{ marginRight: 8 }}
            >
              Filter
            </Button>
            <Button size="small" onClick={() => clearFilters?.()}>
              Reset
            </Button>
          </div>
        </div>
      ),
      render: (text, record) => (
        <div>
          <Text strong>{text}</Text>
          {record.subCategory && (
            <div>
              <Text type="secondary" style={{ fontSize: '12px' }}>
                {record.subCategory}
              </Text>
            </div>
          )}
        </div>
      )
    },
    {
      title: 'Office',
      dataIndex: 'office',
      key: 'office',
      width: 100,
      sorter: (a, b) => (a.office || '').localeCompare(b.office || ''),
      render: (text) => text ? <Tag color="blue">{text}</Tag> : '-'
    },
    {
      title: 'Journey',
      dataIndex: 'journey',
      key: 'journey',
      width: 100,
      sorter: (a, b) => (a.journey || '').localeCompare(b.journey || ''),
      render: (text) => text ? <Tag color="purple">{text}</Tag> : '-'
    },
    {
      title: 'Level',
      dataIndex: 'level',
      key: 'level',
      width: 80,
      sorter: (a, b) => (a.level || '').localeCompare(b.level || ''),
      render: (text) => text ? <Tag color="green">{text}</Tag> : '-'
    },
    {
      title: `${selectedYear} Value`,
      dataIndex: ['currentYear', 'formatted'],
      key: 'currentValue',
      width: 120,
      align: 'right',
      sorter: (a, b) => a.currentYear.value - b.currentYear.value,
      render: (text, record) => (
        <div>
          <Text strong>{text}</Text>
          {record.metadata?.projected && (
            <div>
              <Tag color="orange" size="small">Projected</Tag>
            </div>
          )}
        </div>
      )
    }
  ];

  // Add YoY comparison columns if enabled
  if (viewSettings.showYoYColumns && selectedYear > availableYears[0]) {
    baseColumns.push(
      {
        title: `${selectedYear - 1} Value`,
        dataIndex: ['previousYear', 'formatted'],
        key: 'previousValue',
        width: 120,
        align: 'right',
        render: (text) => text || '-'
      },
      {
        title: 'Change',
        dataIndex: 'change',
        key: 'change',
        width: 100,
        align: 'center',
        sorter: (a, b) => (a.change?.percentage || 0) - (b.change?.percentage || 0),
        render: (change) => formatChangeIndicator(change)
      }
    );
  }

  // Add multi-year progression column if enabled
  if (viewSettings.showMultiYearProgression) {
    baseColumns.push({
      title: 'Multi-Year Trend',
      key: 'multiYearTrend',
      width: 150,
      render: (_, record) => {
        if (!record.multiYear) return '-';
        
        const years = Object.keys(record.multiYear).sort();
        const values = years.map(year => record.multiYear![parseInt(year)].value);
        
        // Simple trend visualization using progress bars
        const maxValue = Math.max(...values);
        
        return (
          <div style={{ padding: '4px 0' }}>
            {years.slice(-3).map(year => {
              const yearInt = parseInt(year);
              const value = record.multiYear![yearInt].value;
              const percentage = maxValue > 0 ? (value / maxValue) * 100 : 0;
              
              return (
                <div key={year} style={{ marginBottom: '2px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px' }}>
                    <span>{year}</span>
                    <span>{record.multiYear![yearInt].formatted}</span>
                  </div>
                  <Progress 
                    percent={percentage} 
                    size="small" 
                    showInfo={false}
                    strokeColor={yearInt === selectedYear ? '#1890ff' : '#d9d9d9'}
                  />
                </div>
              );
            })}
          </div>
        );
      }
    });
  }

  // Merge with custom columns
  const finalColumns = customColumns ? [...baseColumns, ...customColumns] : baseColumns;

  // Export functionality
  const handleExport = (format: 'csv' | 'json' = 'csv') => {
    const exportData = filteredData.map(row => ({
      Category: row.category,
      SubCategory: row.subCategory || '',
      Office: row.office || '',
      Journey: row.journey || '',
      Level: row.level || '',
      CurrentYear: row.currentYear.year,
      CurrentValue: row.currentYear.value,
      CurrentFormatted: row.currentYear.formatted,
      PreviousYear: row.previousYear?.year || '',
      PreviousValue: row.previousYear?.value || '',
      PreviousFormatted: row.previousYear?.formatted || '',
      ChangeAbsolute: row.change?.absolute || '',
      ChangePercentage: row.change?.percentage || '',
      ChangeTrend: row.change?.trend || '',
      Significance: row.change?.significance || '',
      Projected: row.metadata?.projected || false
    }));

    exportChartData(exportData, `${exportFileName}_${selectedYear}`, format);
  };

  // Row selection configuration
  const rowSelection: TableProps<TableDataRow>['rowSelection'] = {
    selectedRowKeys: selectedRows,
    onChange: (selectedRowKeys) => {
      setSelectedRows(selectedRowKeys as string[]);
    },
    type: 'checkbox',
  };

  // Expandable row configuration
  const expandable = viewSettings.showMultiYearProgression ? {
    expandedRowKeys: viewSettings.expandedRows,
    onExpand: (expanded: boolean, record: TableDataRow) => {
      const newExpandedRows = expanded 
        ? [...viewSettings.expandedRows, record.key]
        : viewSettings.expandedRows.filter(key => key !== record.key);
      
      handleViewSettingChange('expandedRows', newExpandedRows);
    },
    expandedRowRender: (record: TableDataRow) => {
      if (!record.multiYear) return <div>No multi-year data available</div>;
      
      const years = Object.keys(record.multiYear).sort();
      
      return (
        <div style={{ padding: '16px', background: '#f6f6f6' }}>
          <Title level={5}>Multi-Year Progression for {record.category}</Title>
          <Row gutter={[16, 8]}>
            {years.map(year => {
              const yearInt = parseInt(year);
              const yearData = record.multiYear![yearInt];
              const isCurrentYear = yearInt === selectedYear;
              
              return (
                <Col key={year} span={6}>
                  <Card 
                    size="small" 
                    style={{ 
                      background: isCurrentYear ? '#e6f7ff' : 'white',
                      border: isCurrentYear ? '2px solid #1890ff' : '1px solid #d9d9d9'
                    }}
                  >
                    <div style={{ textAlign: 'center' }}>
                      <Text type="secondary">{year}</Text>
                      <br />
                      <Text strong style={{ fontSize: '16px' }}>
                        {yearData.formatted}
                      </Text>
                    </div>
                  </Card>
                </Col>
              );
            })}
          </Row>
        </div>
      );
    }
  } : undefined;

  return (
    <Card 
      className={`enhanced-data-table ${className}`}
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <TableOutlined />
          <Title level={4} style={{ margin: 0 }}>{title}</Title>
          <Text type="secondary">({filteredData.length} records)</Text>
        </div>
      }
      extra={
        <Space>
          <Tooltip title="Toggle YoY Columns">
            <Switch
              checked={viewSettings.showYoYColumns}
              onChange={(checked) => handleViewSettingChange('showYoYColumns', checked)}
              checkedChildren="YoY"
              unCheckedChildren="YoY"
              size="small"
            />
          </Tooltip>
          
          <Tooltip title="Show Multi-Year Progression">
            <Switch
              checked={viewSettings.showMultiYearProgression}
              onChange={(checked) => handleViewSettingChange('showMultiYearProgression', checked)}
              checkedChildren={<BarChartOutlined />}
              unCheckedChildren={<BarChartOutlined />}
              size="small"
            />
          </Tooltip>
          
          <Dropdown
            overlay={
              <Menu>
                <Menu.Item key="csv" onClick={() => handleExport('csv')}>
                  Export as CSV
                </Menu.Item>
                <Menu.Item key="json" onClick={() => handleExport('json')}>
                  Export as JSON
                </Menu.Item>
              </Menu>
            }
          >
            <Button 
              icon={<DownloadOutlined />} 
              size="small"
              disabled={filteredData.length === 0}
            >
              Export
            </Button>
          </Dropdown>
        </Space>
      }
    >
      {/* Advanced Filters */}
      {showAdvancedFilters && (
        <div style={{ marginBottom: '16px', padding: '16px', background: '#f6f6f6', borderRadius: '6px' }}>
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12} md={8}>
              <Search
                placeholder="Search categories, offices..."
                value={filters.searchText}
                onChange={(e) => handleFilterChange({ searchText: e.target.value })}
                style={{ width: '100%' }}
                allowClear
              />
            </Col>
            
            <Col xs={12} sm={6} md={4}>
              <Select
                mode="multiple"
                placeholder="Categories"
                value={filters.category}
                onChange={(values) => handleFilterChange({ category: values })}
                style={{ width: '100%' }}
                maxTagCount={1}
              >
                {filterOptions.categories.map(cat => (
                  <Option key={cat} value={cat}>{cat}</Option>
                ))}
              </Select>
            </Col>
            
            <Col xs={12} sm={6} md={4}>
              <Select
                mode="multiple"
                placeholder="Offices"
                value={filters.office}
                onChange={(values) => handleFilterChange({ office: values })}
                style={{ width: '100%' }}
                maxTagCount={1}
              >
                {filterOptions.offices.map(office => (
                  <Option key={office} value={office}>{office}</Option>
                ))}
              </Select>
            </Col>
            
            <Col xs={12} sm={6} md={4}>
              <Select
                placeholder="Trend"
                value={filters.trendFilter}
                onChange={(value) => handleFilterChange({ trendFilter: value })}
                style={{ width: '100%' }}
              >
                <Option value="all">All Trends</Option>
                <Option value="up">↗️ Increasing</Option>
                <Option value="down">↘️ Decreasing</Option>
                <Option value="stable">➡️ Stable</Option>
              </Select>
            </Col>
            
            <Col xs={12} sm={6} md={4}>
              <Checkbox
                checked={filters.projectedOnly}
                onChange={(e) => handleFilterChange({ projectedOnly: e.target.checked })}
              >
                Projected Only
              </Checkbox>
            </Col>
          </Row>
        </div>
      )}

      {/* Data Table */}
      <Table<TableDataRow>
        ref={tableRef}
        columns={finalColumns}
        dataSource={filteredData}
        loading={loading}
        rowSelection={rowSelection}
        expandable={expandable}
        scroll={{ 
          x: 'max-content', 
          y: virtualized ? height - 200 : undefined 
        }}
        pagination={{
          total: filteredData.length,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) => 
            `${range[0]}-${range[1]} of ${total} items`,
          pageSizeOptions: ['10', '20', '50', '100', '200'],
          defaultPageSize: 20
        }}
        size={viewSettings.compactView ? 'small' : 'middle'}
        onChange={(pagination, filters, sorter) => {
          setColumnSorter(Array.isArray(sorter) ? sorter[0] : sorter);
        }}
        onRow={(record) => ({
          onClick: () => onRowClick?.(record),
          style: { cursor: onRowClick ? 'pointer' : 'default' }
        })}
        rowClassName={(record) => {
          if (record.metadata?.projected) return 'row-projected';
          if (record.change?.significance === 'high') return 'row-significant';
          return '';
        }}
      />

      {/* Selection Summary */}
      {selectedRows.length > 0 && (
        <div style={{ 
          marginTop: '16px', 
          padding: '12px', 
          background: '#e6f7ff', 
          borderRadius: '6px',
          border: '1px solid #91d5ff'
        }}>
          <Text>
            <strong>{selectedRows.length}</strong> rows selected
          </Text>
          <Button 
            type="link" 
            size="small"
            onClick={() => setSelectedRows([])}
          >
            Clear Selection
          </Button>
        </div>
      )}

      {/* Table Styles */}
      <style jsx>{`
        .enhanced-data-table .ant-table-tbody > tr.row-projected > td {
          background-color: #fff7e6 !important;
        }
        
        .enhanced-data-table .ant-table-tbody > tr.row-significant > td {
          background-color: #f6ffed !important;
        }
        
        .enhanced-data-table .ant-table-tbody > tr:hover > td {
          background-color: #e6f7ff !important;
        }

        .enhanced-data-table .ant-table-thead > tr > th {
          background-color: #fafafa;
          font-weight: 600;
        }

        .enhanced-data-table .ant-table-tbody > tr > td {
          transition: background-color 0.2s ease;
        }
      `}</style>
    </Card>
  );
};

export default EnhancedDataTable; 