import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Typography, Form, Select, Button, InputNumber, Table, Upload, message, Tag, Space, Tooltip, Divider, Checkbox } from 'antd';
import { UploadOutlined, DownloadOutlined, SaveOutlined, ReloadOutlined, EditOutlined, CalendarOutlined } from '@ant-design/icons';
import { useConfig } from '../components/ConfigContext';

const { Title, Text } = Typography;
const { Option } = Select;

const ROLES = ['Consultant', 'Sales', 'Recruitment', 'Operations'];
const ROLES_WITH_LEVELS = ['Consultant', 'Sales', 'Recruitment'];
const LEVELS = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP'];

const MONTHS = [
  { value: 1, label: 'January', short: 'Jan' },
  { value: 2, label: 'February', short: 'Feb' },
  { value: 3, label: 'March', short: 'Mar' },
  { value: 4, label: 'April', short: 'Apr' },
  { value: 5, label: 'May', short: 'May' },
  { value: 6, label: 'June', short: 'Jun' },
  { value: 7, label: 'July', short: 'Jul' },
  { value: 8, label: 'August', short: 'Aug' },
  { value: 9, label: 'September', short: 'Sep' },
  { value: 10, label: 'October', short: 'Oct' },
  { value: 11, label: 'November', short: 'Nov' },
  { value: 12, label: 'December', short: 'Dec' }
];

const LEVER_GROUPS = [
  { 
    key: 'headcount', 
    label: 'Headcount', 
    icon: '👥',
    defaultMonth: 1,
    columns: [
      { key: 'total', label: 'FTE', formatter: 'number' }
    ]
  },
  { 
    key: 'financial', 
    label: 'Financial', 
    icon: '💰',
    defaultMonth: 1,
    columns: [
      { key: 'price', label: 'Price', formatter: 'currency' },
      { key: 'salary', label: 'Salary', formatter: 'currency' }
    ]
  },
  { 
    key: 'hr_metrics', 
    label: 'HR Metrics', 
    icon: '📊',
    defaultMonth: 1,
    columns: [
      { key: 'recruitment', label: 'Recruitment', formatter: 'percentage' },
      { key: 'churn', label: 'Churn', formatter: 'percentage' }
    ]
  },
  { 
    key: 'progression', 
    label: 'Progression', 
    icon: '📈',
    defaultMonth: 5,
    columns: [
      { key: 'progression', label: 'Progression', formatter: 'percentage' }
    ]
  },
  { 
    key: 'operations', 
    label: 'Operations', 
    icon: '⚙️',
    defaultMonth: 1,
    columns: [
      { key: 'utr', label: 'UTR', formatter: 'percentage' }
    ]
  }
];

export default function Configuration() {
  const [offices, setOffices] = useState<string[]>([]);
  const [selectedOffice, setSelectedOffice] = useState<string>('');
  const [officeData, setOfficeData] = useState<any>({});
  const [originalData, setOriginalData] = useState<any>({});
  const [draftChanges, setDraftChanges] = useState<any>({});
  const [hasChanges, setHasChanges] = useState(false);
  const { setLevers } = useConfig();
  const [loading, setLoading] = useState(false);
  const [expandedGroups, setExpandedGroups] = useState<string[]>(['headcount', 'financial']);
  const [applyToAllMonths, setApplyToAllMonths] = useState(false);
  
  // Month selection state per group
  const [selectedMonths, setSelectedMonths] = useState<Record<string, number>>(() => {
    const initialMonths: Record<string, number> = {};
    LEVER_GROUPS.forEach(group => {
      initialMonths[group.key] = group.defaultMonth;
    });
    return initialMonths;
  });

  const fetchOffices = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/offices/config');
      const data = await response.json();
      
      setOffices(data.map((office: any) => office.name));
      if (data.length > 0) {
        setSelectedOffice(data[0].name);
      }
      
      // Convert to office data structure
      const officeMap: any = {};
      data.forEach((office: any) => {
        officeMap[office.name] = office;
      });
      setOfficeData(officeMap);
      setOriginalData(JSON.parse(JSON.stringify(officeMap)));
      setLevers(data);
    } catch (error) {
      console.error('Failed to fetch offices:', error);
      message.error('Failed to load office data');
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchOffices();
  }, []);

  // Helper to get value from either draft changes or original data
  const getValue = (role: string, level: string | null, field: string, month: number) => {
    // Special case for 'total' field - it doesn't have month variants
    const isTotal = field === 'total';
    const monthSuffix = isTotal ? '' : `_${month}`;
    const fieldWithMonth = `${field}${monthSuffix}`;
    const draftPath = `${selectedOffice}.${role}${level ? `.${level}` : ''}.${fieldWithMonth}`;
    
    if (draftChanges[draftPath] !== undefined) {
      return draftChanges[draftPath];
    }
    
    const office = officeData[selectedOffice];
    if (!office?.roles?.[role]) return '';
    
    if (level && office.roles[role][level]) {
      return office.roles[role][level][fieldWithMonth] ?? office.roles[role][level][field] ?? '';
    } else if (!level) {
      return office.roles[role][fieldWithMonth] ?? office.roles[role][field] ?? '';
    }
    return '';
  };

  // Helper to set value in draft changes
  const setValue = (role: string, level: string | null, field: string, month: number, value: number) => {
    // Special case for 'total' field - it doesn't have month variants
    const isTotal = field === 'total';
    
    if (applyToAllMonths && !isTotal) {
      // Apply to all 12 months
      const newDraftChanges: any = {};
      for (let m = 1; m <= 12; m++) {
        const monthSuffix = `_${m}`;
        const fieldWithMonth = `${field}${monthSuffix}`;
        const draftPath = `${selectedOffice}.${role}${level ? `.${level}` : ''}.${fieldWithMonth}`;
        newDraftChanges[draftPath] = value;
      }
      setDraftChanges((prev: any) => ({
        ...prev,
        ...newDraftChanges
      }));
    } else {
      // Apply to selected month only
      const monthSuffix = isTotal ? '' : `_${month}`;
      const fieldWithMonth = `${field}${monthSuffix}`;
      const draftPath = `${selectedOffice}.${role}${level ? `.${level}` : ''}.${fieldWithMonth}`;
      setDraftChanges((prev: any) => ({
        ...prev,
        [draftPath]: value
      }));
    }
    setHasChanges(true);
  };

  // Helper to check if value has changed
  const hasChanged = (role: string, level: string | null, field: string, month: number) => {
    // Special case for 'total' field - it doesn't have month variants
    const isTotal = field === 'total';
    const monthSuffix = isTotal ? '' : `_${month}`;
    const fieldWithMonth = `${field}${monthSuffix}`;
    const draftPath = `${selectedOffice}.${role}${level ? `.${level}` : ''}.${fieldWithMonth}`;
    return draftChanges[draftPath] !== undefined;
  };

  // Apply changes to office data
  const handleApplyChanges = () => {
    const updatedOfficeData = JSON.parse(JSON.stringify(officeData));
    
    Object.entries(draftChanges).forEach(([path, value]) => {
      const pathParts = path.split('.');
      const [office, role, ...rest] = pathParts;
      
      if (rest.length === 1) {
        // Operations: office.role.field
        const field = rest[0];
        if (!updatedOfficeData[office].roles[role]) {
          updatedOfficeData[office].roles[role] = {};
        }
        updatedOfficeData[office].roles[role][field] = value;
      } else {
        // Has level: office.role.level.field
        const [level, field] = rest;
        if (!updatedOfficeData[office].roles[role]) {
          updatedOfficeData[office].roles[role] = {};
        }
        if (!updatedOfficeData[office].roles[role][level]) {
          updatedOfficeData[office].roles[role][level] = {};
        }
        updatedOfficeData[office].roles[role][level][field] = value;
      }
    });

    setOfficeData(updatedOfficeData);
    setDraftChanges({});
    setHasChanges(false);
    message.success('Changes applied successfully');
  };

  // Reset changes
  const handleResetChanges = () => {
    setDraftChanges({});
    setHasChanges(false);
    message.info('Changes discarded');
  };

  // Reset to original data
  const handleResetToOriginal = () => {
    setOfficeData(JSON.parse(JSON.stringify(originalData)));
    setDraftChanges({});
    setHasChanges(false);
    message.info('Reset to original configuration');
  };

  // Export current configuration
  const handleExportConfig = () => {
    try {
      // Create a deep copy of the current office data
      const currentData = JSON.parse(JSON.stringify(officeData));

      // Apply any draft changes to the copy
      Object.entries(draftChanges).forEach(([path, value]) => {
        const pathParts = path.split('.');
        const [office, role, ...rest] = pathParts;
        
        // Ensure the office and role exist in the data structure
        if (!currentData[office]) currentData[office] = { roles: {} };
        if (!currentData[office].roles) currentData[office].roles = {};
        if (!currentData[office].roles[role]) currentData[office].roles[role] = {};
        
        if (rest.length === 1) {
          // Operations: office.role.field
          const field = rest[0];
          currentData[office].roles[role][field] = value;
        } else {
          // Has level: office.role.level.field
          const [level, field] = rest;
          if (!currentData[office].roles[role][level]) {
            currentData[office].roles[role][level] = {};
          }
          currentData[office].roles[role][level][field] = value;
        }
      });

      // Create export data with metadata
      const exportData = {
        metadata: {
          exportedAt: new Date().toISOString(),
          exportedBy: 'SimulationLab Configuration Matrix',
          selectedOffice: selectedOffice,
          hasUnsavedChanges: hasChanges,
          unsavedChangeCount: Object.keys(draftChanges).length,
          selectedMonths: selectedMonths
        },
        configuration: currentData
      };

      // Create and download the file
      const jsonString = JSON.stringify(exportData, null, 2);
      const blob = new Blob([jsonString], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = `office-config-${selectedOffice}-${new Date().toISOString().split('T')[0]}.json`;
      a.style.display = 'none';
      
      document.body.appendChild(a);
      a.click();
      
      // Clean up
      setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }, 100);

      // Show success message with file info
      const fileSizeKB = Math.round(blob.size / 1024);
      message.success({
        content: `✅ Configuration exported successfully! File: ${a.download} (${fileSizeKB} KB)`,
        duration: 5
      });

      console.log('Export completed:', {
        fileName: a.download,
        fileSize: `${fileSizeKB} KB`,
        officesCount: Object.keys(currentData).length,
        hasChanges: hasChanges,
        selectedOffice: selectedOffice
      });

    } catch (error) {
      console.error('Export failed:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      message.error({
        content: `❌ Export failed: ${errorMessage}`,
        duration: 8
      });
    }
  };

  // Update month selection for a group
  const handleMonthChange = (groupKey: string, month: number) => {
    setSelectedMonths(prev => ({
      ...prev,
      [groupKey]: month
    }));
  };

  // Format value based on type
  const formatValue = (value: any, formatter: string) => {
    if (!value && value !== 0) return '';
    
    switch (formatter) {
      case 'currency':
        return `${Number(value).toLocaleString()} SEK`;
      case 'percentage':
        return `${(Number(value) * 100).toFixed(1)}%`;
      case 'number':
      default:
        return String(value);
    }
  };

  // Parse value based on type
  const parseValue = (str: string, formatter: string) => {
    if (!str) return 0;
    const num = Number(str.replace(/[^\d.-]/g, ''));
    if (formatter === 'percentage') {
      return num / 100;
    }
    return num;
  };

  // Helper to calculate aggregated FTE for a role
  const getAggregatedFTE = (roleName: string) => {
    const office = officeData[selectedOffice];
    if (!office?.roles?.[roleName]) return 0;
    
    const roleData = office.roles[roleName];
    let total = 0;
    
    LEVELS.forEach(levelName => {
      const levelData = roleData[levelName];
      if (levelData && levelData.total) {
        total += levelData.total;
      }
    });
    
    return total;
  };

  // Generate table data with grouped structure
  const getTableData = () => {
    if (!selectedOffice || !officeData[selectedOffice]) {
      return [];
    }

    const office = officeData[selectedOffice];
    const rows: any[] = [];

    // Add roles with levels (Consultant, Sales, Recruitment)
    ROLES_WITH_LEVELS.forEach(roleName => {
      const roleData = office.roles[roleName];
      if (!roleData) return;

      // Parent row for role
      const roleRow: any = {
        key: roleName,
        role: roleName,
        level: null,
        isParent: true,
        children: []
      };

      // Add aggregated values for parent row (used when collapsed)
      LEVER_GROUPS.forEach(group => {
        group.columns.forEach(col => {
          if (col.key === 'total') {
            // For FTE, show aggregated total
            roleRow[`${col.key}_${group.key}`] = getAggregatedFTE(roleName);
          } else {
            // For other metrics, don't show values at parent level
            roleRow[`${col.key}_${group.key}`] = null;
          }
        });
      });

      // Child rows for levels
      LEVELS.forEach(levelName => {
        const levelData = roleData[levelName];
        const hasData = levelData && (
          (levelData.total && levelData.total > 0) || 
          Object.keys(levelData).some(key => 
            hasChanged(roleName, levelName, key.replace(/_\d+$/, ''), selectedMonths[LEVER_GROUPS.find(g => g.columns.some(c => key.startsWith(c.key)))?.key || 'headcount'] || 1)
          )
        );
        
        if (hasData) {
          const childRow: any = {
            key: `${roleName}-${levelName}`,
            role: roleName,
            level: levelName,
            isParent: false
          };

          // Add all lever values for each group
          LEVER_GROUPS.forEach(group => {
            group.columns.forEach(col => {
              const month = selectedMonths[group.key];
              childRow[`${col.key}_${group.key}`] = getValue(roleName, levelName, col.key, month);
            });
          });

          roleRow.children.push(childRow);
        }
      });

      if (roleRow.children.length > 0) {
        rows.push(roleRow);
      }
    });

    // Add Operations (flat role)
    if (office.roles.Operations) {
      const opsRow: any = {
        key: 'Operations',
        role: 'Operations',
        level: null,
        isParent: false
      };

      // Add all lever values for Operations
      LEVER_GROUPS.forEach(group => {
        group.columns.forEach(col => {
          const month = selectedMonths[group.key];
          opsRow[`${col.key}_${group.key}`] = getValue('Operations', null, col.key, month);
        });
      });

      rows.push(opsRow);
    }

    return rows;
  };

  // Generate table columns with grouped headers and month selectors
  const getTableColumns = () => {
    const columns: any[] = [
      {
        title: 'Role / Level',
        dataIndex: 'role',
        key: 'role',
        width: 150,
        fixed: 'left',
        render: (text: string, record: any) => (
          <div>
            <div style={{ fontWeight: record.level ? 'normal' : 'bold' }}>
              {record.level ? `${record.level}` : record.role}
            </div>
            {record.level && <Text type="secondary" style={{ fontSize: '12px' }}>{record.role}</Text>}
          </div>
        ),
      }
    ];

    // Add grouped columns with month selectors
    LEVER_GROUPS.forEach(group => {
      if (!expandedGroups.includes(group.key)) {
        // Collapsed group - show only first column with month selector
        const firstCol = group.columns[0];
        const month = selectedMonths[group.key];
        const monthLabel = MONTHS.find(m => m.value === month)?.short || 'Jan';
        
        columns.push({
          title: (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                <span>{group.icon} {group.label}</span>
                <Button 
                  type="text" 
                  size="small"
                  icon={<EditOutlined />}
                  onClick={() => setExpandedGroups((prev: string[]) => [...prev, group.key])}
                />
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <CalendarOutlined style={{ fontSize: '10px' }} />
                <Select
                  size="small"
                  value={month}
                  onChange={(value) => handleMonthChange(group.key, value)}
                  style={{ width: '60px' }}
                  dropdownMatchSelectWidth={80}
                >
                  {MONTHS.map(m => (
                    <Option key={m.value} value={m.value}>{m.short}</Option>
                  ))}
                </Select>
              </div>
              <Text type="secondary" style={{ fontSize: '10px' }}>{firstCol.label}</Text>
            </div>
          ),
          dataIndex: `${firstCol.key}_${group.key}`,
          key: `${firstCol.key}_${group.key}`,
          width: 140,
          render: (val: any, record: any) => {
            const month = selectedMonths[group.key];
            
            // For parent rows, show aggregated totals (read-only)
            if (record.isParent) {
              if (firstCol.key === 'total' && val !== null && val !== undefined) {
                return (
                  <div style={{ 
                    padding: '4px 8px', 
                    textAlign: 'right',
                    fontWeight: 'bold',
                    color: '#1890ff'
                  }}>
                    {formatValue(val, firstCol.formatter)}
                  </div>
                );
              }
              return null;
            }
            
            const isChanged = hasChanged(record.role, record.level, firstCol.key, month);
            
            return (
              <InputNumber
                size="small"
                value={val || 0}
                onChange={(value) => setValue(record.role, record.level, firstCol.key, month, value || 0)}
                style={{ 
                  width: '100%', 
                  borderColor: isChanged ? '#ffa940' : undefined
                }}
                precision={firstCol.formatter === 'currency' ? 0 : 3}
                formatter={val => formatValue(val, firstCol.formatter)}
                parser={str => parseValue(String(str), firstCol.formatter)}
              />
            );
          }
        });
      } else {
        // Expanded group - show all columns with shared month selector
        const month = selectedMonths[group.key];
        const monthLabel = MONTHS.find(m => m.value === month)?.short || 'Jan';
        
        const groupColumns = group.columns.map(col => ({
          title: col.label,
          dataIndex: `${col.key}_${group.key}`,
          key: `${col.key}_${group.key}`,
          width: 100,
          render: (val: any, record: any) => {
            const month = selectedMonths[group.key];
            
            // For parent rows, show aggregated totals (read-only)
            if (record.isParent) {
              if (col.key === 'total' && val !== null && val !== undefined) {
                return (
                  <div style={{ 
                    padding: '4px 8px', 
                    textAlign: 'right',
                    fontWeight: 'bold',
                    color: '#1890ff'
                  }}>
                    {formatValue(val, col.formatter)}
                  </div>
                );
              }
              return null;
            }
            
            const isChanged = hasChanged(record.role, record.level, col.key, month);
            
            return (
              <InputNumber
                size="small"
                value={val || 0}
                onChange={(value) => setValue(record.role, record.level, col.key, month, value || 0)}
                style={{ 
                  width: '100%', 
                  borderColor: isChanged ? '#ffa940' : undefined
                }}
                precision={col.formatter === 'currency' ? 0 : 3}
                formatter={val => formatValue(val, col.formatter)}
                parser={str => parseValue(String(str), col.formatter)}
              />
            );
          }
        }));

        columns.push({
          title: (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                <span>{group.icon} {group.label}</span>
                <Button 
                  type="text" 
                  size="small"
                  onClick={() => setExpandedGroups((prev: string[]) => prev.filter(g => g !== group.key))}
                >
                  Collapse
                </Button>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <CalendarOutlined style={{ fontSize: '10px' }} />
                <Select
                  size="small"
                  value={month}
                  onChange={(value) => handleMonthChange(group.key, value)}
                  style={{ width: '60px' }}
                  dropdownMatchSelectWidth={80}
                >
                  {MONTHS.map(m => (
                    <Option key={m.value} value={m.value}>{m.short}</Option>
                  ))}
                </Select>
                <Text type="secondary" style={{ fontSize: '10px' }}>({monthLabel})</Text>
              </div>
            </div>
          ),
          children: groupColumns
        });
      }
    });

    return columns;
  };

  const uploadProps = {
    name: 'file',
    accept: '.xlsx,.xls,.csv,.json',
    showUploadList: false,
    customRequest: async (options: any) => {
      const formData = new FormData();
      formData.append('file', options.file);
      try {
        const res = await fetch('/api/import-office-levers', {
          method: 'POST',
          body: formData,
        });
        if (!res.ok) throw new Error('Upload failed');
        message.success('Office config imported successfully!');
        fetchOffices(); // Refetch data after import
      } catch (err: any) {
        message.error('Import failed: ' + err.message);
      }
      options.onSuccess();
    },
  };

  return (
    <div>
      <Card title={<Title level={4} style={{ margin: 0 }}>🔧 Lever Configuration Matrix</Title>}>
        {/* Header Controls */}
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col>
            <Upload {...uploadProps}>
              <Button icon={<UploadOutlined />}>📤 Import Config</Button>
            </Upload>
          </Col>
          <Col>
            <Button 
              icon={<DownloadOutlined />} 
              onClick={handleExportConfig}
            >
              📥 Export Config
            </Button>
          </Col>
          <Col flex="auto" />
          <Col>
            <Space>
              {hasChanges && (
                <>
                  <Button 
                    type="primary" 
                    icon={<SaveOutlined />}
                    onClick={handleApplyChanges}
                  >
                    💾 Apply Changes
                  </Button>
                  <Button 
                    icon={<ReloadOutlined />}
                    onClick={handleResetChanges}
                  >
                    🔄 Discard Changes
                  </Button>
                </>
              )}
              <Button 
                onClick={handleResetToOriginal}
                danger
              >
                ⚠️ Reset to Original
              </Button>
            </Space>
          </Col>
        </Row>

        {/* Office Selector and Status */}
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col>
            <span style={{ marginRight: 8 }}>Office:</span>
            <Select 
              value={selectedOffice} 
              onChange={setSelectedOffice} 
              style={{ width: 200 }}
              loading={loading}
            >
              {offices.map(office => (
                <Option key={office} value={office}>{office}</Option>
              ))}
            </Select>
          </Col>
          <Col>
            <Checkbox 
              checked={applyToAllMonths}
              onChange={(e) => setApplyToAllMonths(e.target.checked)}
              style={{ fontWeight: applyToAllMonths ? 'bold' : 'normal' }}
            >
              🔄 Apply to All Months
            </Checkbox>
          </Col>
          <Col>
            {hasChanges && (
              <Tag color="orange">
                🔄 {Object.keys(draftChanges).length} unsaved changes
              </Tag>
            )}
            {loading && (
              <Tag color="blue">
                📊 Loading office data...
              </Tag>
            )}
          </Col>
        </Row>

        {/* Instructions */}
        <Row style={{ marginBottom: 16 }}>
          <Col span={24}>
            <Text type="secondary">
              • <strong>Orange highlights</strong> indicate modified values
              • <strong>Click group headers</strong> to expand/collapse columns  
              • <strong>Month dropdowns</strong> 📅 control which month's data is shown/edited
              • <strong>"Apply to All Months"</strong> checkbox: when checked, value changes apply to all 12 months
              • <strong>Financial values</strong> in SEK, <strong>rates</strong> as percentages
              • Changes are saved in draft until you click "Apply Changes"
            </Text>
          </Col>
        </Row>

        <Divider />

        {/* Configuration Table */}
        <Card 
          size="small"
          title={
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>📊 Configuration Matrix - {selectedOffice}</span>
              <Space>
                <Button 
                  size="small"
                  onClick={() => setExpandedGroups(LEVER_GROUPS.map(g => g.key))}
                >
                  📖 Expand All
                </Button>
                <Button 
                  size="small"
                  onClick={() => setExpandedGroups(['headcount'])}
                >
                  📑 Collapse All
                </Button>
              </Space>
            </div>
          }
        >
          <Table
            columns={getTableColumns()}
            dataSource={getTableData()}
            pagination={false}
            rowKey={record => record.key}
            size="small"
            scroll={{ x: 1200, y: 600 }}
            expandable={{ 
              defaultExpandAllRows: true,
              indentSize: 20
            }}
            loading={loading}
          />
        </Card>

        {/* Help Section */}
        <Card title="💡 Help & Tips" size="small" style={{ marginTop: 16 }}>
          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Title level={5}>Column Groups:</Title>
              <ul>
                <li><strong>👥 Headcount:</strong> Current FTE levels</li>
                <li><strong>💰 Financial:</strong> Price & Salary for selected month</li>
                <li><strong>📊 HR Metrics:</strong> Recruitment & Churn rates for selected month</li>
                <li><strong>📈 Progression:</strong> Progression rates (typically May/November)</li>
                <li><strong>⚙️ Operations:</strong> Utilization rates for selected month</li>
              </ul>
            </Col>
            <Col xs={24} md={12}>
              <Title level={5}>Value Formats:</Title>
              <ul>
                <li><strong>FTE:</strong> Whole numbers (e.g., 15)</li>
                <li><strong>Prices/Salaries:</strong> SEK amounts (e.g., 120,000)</li>
                <li><strong>Rates:</strong> Percentages (e.g., 2.5% for recruitment)</li>
                <li><strong>UTR:</strong> Utilization percentage (e.g., 85%)</li>
              </ul>
            </Col>
          </Row>
          <Divider />
          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Title level={5}>Month Selection:</Title>
              <ul>
                <li><strong>📅 Each column group</strong> can show data from any month</li>
                <li><strong>Default months:</strong> January for most metrics, May for progression</li>
                <li><strong>Independent selection:</strong> Each group can show different months</li>
                <li><strong>🔄 Apply to All Months:</strong> When checked, changes apply to all 12 months instead of just the selected month</li>
                <li><strong>Real-time updates:</strong> Changes immediately reflect in the table</li>
              </ul>
            </Col>
            <Col xs={24} md={12}>
              <Title level={5}>Advanced Features:</Title>
              <ul>
                <li><strong>Draft mode:</strong> All changes are saved as drafts until applied</li>
                <li><strong>Group expand/collapse:</strong> Focus on specific metrics</li>
                <li><strong>Export functionality:</strong> Save current configuration with all changes</li>
                <li><strong>Reset options:</strong> Discard changes or reset to original</li>
              </ul>
            </Col>
          </Row>
        </Card>
      </Card>
    </div>
  );
} 