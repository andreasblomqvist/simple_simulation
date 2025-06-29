import React, { useEffect, useState, useCallback } from 'react';
import { Card, Row, Col, Typography, Form, Select, Button, InputNumber, Table, Upload, message, Tag, Space, Tooltip, Divider, Checkbox, Modal } from 'antd';
import { UploadOutlined, DownloadOutlined, SaveOutlined, ReloadOutlined, EditOutlined, CalendarOutlined, GlobalOutlined } from '@ant-design/icons';

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

  const [loading, setLoading] = useState(false);
  const [expandedGroups, setExpandedGroups] = useState<string[]>(['headcount', 'financial']);
  const [applyToAllMonths, setApplyToAllMonths] = useState(false);
  
  // Add state for import/refresh feedback
  const [importing, setImporting] = useState(false);
  const [lastRefreshTime, setLastRefreshTime] = useState<Date | null>(null);
  
  // Global configuration modal state
  const [showGlobalModal, setShowGlobalModal] = useState(false);
  const [globalForm] = Form.useForm();
  
  // Month selection state per group
  const [selectedMonths, setSelectedMonths] = useState<Record<string, number>>(() => {
    const initialMonths: Record<string, number> = {};
    LEVER_GROUPS.forEach(group => {
      initialMonths[group.key] = group.defaultMonth;
    });
    return initialMonths;
  });

  // Transform office data structure for UI consumption
  const transformOfficeDataForUI = (office: any) => {
    return {
      name: office.name,
      total_fte: office.total_fte,
      journey: office.journey,
      roles: office.roles || {}
    };
  };

  const fetchOffices = useCallback(async () => {
    setLoading(true);
    try {
      // ALWAYS use pure configuration data (engine should never modify config)
      const response = await fetch('/api/offices/config');
      const data = await response.json();
      
      console.log('[CONFIG] 🎛️  Using pure configuration service (engine never modifies config)');
      console.log('[CONFIG] 📥 Received data:', { type: Array.isArray(data), length: data.length, offices: data.map((o: any) => o.name) });
      
      // Validate data structure
      if (!Array.isArray(data) || data.length === 0) {
        console.log('[CONFIG] ⚠️  No office data received or invalid format');
        setOffices([]);
        setSelectedOffice('');
        setOfficeData({});
        setOriginalData({});
        message.warning('No office configurations found. Please upload an Excel file.');
        return;
      }
      
      // Extract office names and set the first one as selected if none is
      const officeNames = data.map((office: any) => office.name).sort();
      console.log('[CONFIG] 🏢 Office names extracted:', officeNames);
      setOffices(officeNames);
      
      // Always set the first office as selected if no office is currently selected
      // or if the currently selected office is not in the new list
      const targetOffice = selectedOffice && officeNames.includes(selectedOffice) 
        ? selectedOffice 
        : officeNames[0];
      
      console.log('[CONFIG] 🎯 Office selection:', { 
        currentSelected: selectedOffice, 
        availableOffices: officeNames, 
        targetOffice: targetOffice 
      });
      
      if (!selectedOffice || !officeNames.includes(selectedOffice)) {
        setSelectedOffice(targetOffice);
        console.log('[CONFIG] ✅ Set selected office to:', targetOffice);
      }
      
      // Transform all offices data for UI consumption and store in a dictionary
      const allOfficesData = data.reduce((acc: any, office: any) => {
        acc[office.name] = transformOfficeDataForUI(office);
        return acc;
      }, {});
      
      console.log('[CONFIG] 🔄 Transformed office data:', Object.keys(allOfficesData));
      
      setOfficeData(allOfficesData);
      setOriginalData(JSON.parse(JSON.stringify(allOfficesData))); // Deep copy
      
      // Clear any draft changes since we're loading fresh data
      setDraftChanges({});
      setHasChanges(false);
      
      console.log(`[CONFIG] 📊 Loaded data for ${data.length} offices. Currently viewing: ${targetOffice}`);
      
      // Update refresh timestamp
      setLastRefreshTime(new Date());
      
    } catch (error) {
      console.error('[CONFIG] ❌ Error fetching offices:', error);
      message.error('Failed to load office data. Please check the server connection.');
    } finally {
      setLoading(false);
    }
  }, [selectedOffice]);

  // Fetch offices on mount
  useEffect(() => {
    fetchOffices();
  }, []); // Remove fetchOffices from dependency array to prevent re-fetch on every render

  // Re-fetch data ONLY when selectedOffice changes AND its data is not already loaded
  // This logic is now handled by the main fetchOffices, which gets all data at once.
  // We just need to ensure the component re-renders if the selected office changes.
  useEffect(() => {
    if (selectedOffice && officeData[selectedOffice]) {
      console.log(`[CONFIG] 🔄 Switched view to: ${selectedOffice}`);
      // No need to re-fetch, data is already in state.
      // We could reset draft changes here if desired when switching offices.
      setDraftChanges({});
      setHasChanges(false);
    }
  }, [selectedOffice]);

  // Helper to get value from either draft changes or original data
  const getValue = (role: string, level: string | null, field: string, month: number) => {
    // Special case for 'total' field - it doesn't have month variants and maps to 'fte' in backend
    const isTotal = field === 'total';
    const backendField = isTotal ? 'fte' : field; // Map 'total' to 'fte' for backend compatibility
    const monthSuffix = isTotal ? '' : `_${month}`;
    const fieldWithMonth = `${backendField}${monthSuffix}`;
    const draftPath = `${selectedOffice}.${role}${level ? `.${level}` : ''}.${fieldWithMonth}`;
    
    if (draftChanges[draftPath] !== undefined) {
      return draftChanges[draftPath];
    }
    
    const currentOfficeData = officeData[selectedOffice];
    if (!currentOfficeData?.roles?.[role]) return '';
    
    if (level && currentOfficeData.roles[role][level]) {
      return currentOfficeData.roles[role][level][fieldWithMonth] ?? currentOfficeData.roles[role][level][backendField] ?? '';
    } else if (!level) {
      return currentOfficeData.roles[role][fieldWithMonth] ?? currentOfficeData.roles[role][backendField] ?? '';
    }
    return '';
  };

  // Helper to set value in draft changes
  const setValue = (role: string, level: string | null, field: string, month: number, value: number) => {
    // Special case for 'total' field - it doesn't have month variants and maps to 'fte' in backend
    const isTotal = field === 'total';
    const backendField = isTotal ? 'fte' : field; // Map 'total' to 'fte' for backend compatibility
    
    if (applyToAllMonths && !isTotal) {
      // Apply to all 12 months
      const newDraftChanges: any = {};
      for (let m = 1; m <= 12; m++) {
        const monthSuffix = `_${m}`;
        const fieldWithMonth = `${backendField}${monthSuffix}`;
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
      const fieldWithMonth = `${backendField}${monthSuffix}`;
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
    // Special case for 'total' field - it doesn't have month variants and maps to 'fte' in backend
    const isTotal = field === 'total';
    const backendField = isTotal ? 'fte' : field; // Map 'total' to 'fte' for backend compatibility
    const monthSuffix = isTotal ? '' : `_${month}`;
    const fieldWithMonth = `${backendField}${monthSuffix}`;
    const draftPath = `${selectedOffice}.${role}${level ? `.${level}` : ''}.${fieldWithMonth}`;
    return draftChanges[draftPath] !== undefined;
  };

  // Apply changes to configuration service
  const handleApplyChanges = async () => {
    try {
      setLoading(true);
      
      const response = await fetch('/api/offices/config/update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(draftChanges),
      });
      
      if (!response.ok) {
        throw new Error('Failed to apply configuration changes');
      }
      
      const result = await response.json();
      
      message.success(`✅ Changes applied successfully! Updated ${result.updated_count} configuration values.`);
      console.log(`[CONFIG] 🎯 Applied ${result.updated_count} changes to configuration service`);
      
      // Clear draft changes and refresh data
      setDraftChanges({});
      await fetchOffices();
      
    } catch (error) {
      console.error('[CONFIG] ❌ Error applying changes:', error);
      message.error('Failed to apply configuration changes');
    } finally {
      setLoading(false);
    }
  };

  // Handle file upload to configuration service
  const handleFileUpload = async (file: File) => {
    try {
      setLoading(true);
      
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('/api/offices/config/import', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error('Failed to import configuration file');
      }
      
      const result = await response.json();
      
      message.success(`✅ Import successful! Updated ${result.updated} configuration values from ${result.rows} rows.`);
      console.log(`[CONFIG] 📁 Imported ${result.updated} changes from Excel file`);
      
      // Refresh data after import
      await fetchOffices();
      
    } catch (error) {
      console.error('[CONFIG] ❌ Error importing file:', error);
      message.error('Failed to import configuration file');
    } finally {
      setLoading(false);
    }
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
  const handleExportConfig = async () => {
    try {
      setLoading(true);
      
      // Call the backend Excel export endpoint
      const response = await fetch('/api/offices/config/export', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          includeUnsavedChanges: hasChanges,
          unsavedChanges: draftChanges,
          exportMetadata: {
            exportedAt: new Date().toISOString(),
            exportedBy: 'Configuration Matrix',
            exportScope: 'All Offices',
            currentlyViewedOffice: selectedOffice,
            hasUnsavedChanges: hasChanges,
            unsavedChangeCount: Object.keys(draftChanges).length,
            selectedMonths: selectedMonths
          }
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to export configuration');
      }

      // Get the blob from the response
      const blob = await response.blob();
      
      // Create download link
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `all-offices-config-${new Date().toISOString().split('T')[0]}.xlsx`;
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
        content: `✅ All offices configuration exported successfully! File: ${a.download} (${fileSizeKB} KB Excel file)`,
        duration: 5
      });

      console.log('Excel export completed:', {
        fileName: a.download,
        fileSize: `${fileSizeKB} KB`,
        hasChanges: hasChanges,
        currentlyViewedOffice: selectedOffice,
        exportFormat: 'Excel'
      });

    } catch (error) {
      console.error('Export failed:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      message.error({
        content: `❌ Export failed: ${errorMessage}`,
        duration: 8
      });
    } finally {
      setLoading(false);
    }
  };

  // Update month selection for a group
  const handleMonthChange = (groupKey: string, month: number) => {
    setSelectedMonths(prev => ({
      ...prev,
      [groupKey]: month
    }));
  };

  // Handle global configuration change
  const handleGlobalChange = async (values: any) => {
    try {
      const { role, levels, field, month, value, targetOffices } = values;
      if (!value && value !== 0) {
        message.error('Please enter a value');
        return;
      }
      const newDraftChanges: any = {};
      const officeList = targetOffices && targetOffices.includes('ALL_OFFICES') 
        ? offices 
        : targetOffices && targetOffices.length > 0 
          ? targetOffices.filter((office: string) => office !== 'ALL_OFFICES')
          : offices;
      const levelList = levels && levels.length > 0 ? levels : [null];
      const isTotal = field === 'total';
      const backendField = isTotal ? 'fte' : field;
      // Detect if the field is a percentage
      const group = LEVER_GROUPS.find(g => g.columns.some(c => c.key === field));
      const col = group?.columns.find(c => c.key === field);
      let backendValue = value;
      if (col?.formatter === 'percentage') {
        backendValue = value / 100;
      }
      officeList.forEach((officeName: string) => {
        levelList.forEach((level: string | null) => {
          if (month === 0 && !isTotal) {
            for (let m = 1; m <= 12; m++) {
              const monthSuffix = `_${m}`;
              const fieldWithMonth = `${backendField}${monthSuffix}`;
              const draftPath = `${officeName}.${role}${level ? `.${level}` : ''}.${fieldWithMonth}`;
              newDraftChanges[draftPath] = backendValue;
            }
          } else {
            const monthSuffix = isTotal ? '' : `_${month}`;
            const fieldWithMonth = `${backendField}${monthSuffix}`;
            const draftPath = `${officeName}.${role}${level ? `.${level}` : ''}.${fieldWithMonth}`;
            newDraftChanges[draftPath] = backendValue;
          }
        });
      });
      setDraftChanges((prev: any) => ({
        ...prev,
        ...newDraftChanges
      }));
      setHasChanges(true);
      setShowGlobalModal(false);
      globalForm.resetFields();
      const changesCount = Object.keys(newDraftChanges).length;
      const levelText = levels && levels.length > 0 ? ` across ${levels.length} level(s)` : '';
      const monthsText = month === 0 && !isTotal ? ' (all months)' : '';
      const officeText = targetOffices && targetOffices.includes('ALL_OFFICES') 
        ? `all ${officeList.length} offices` 
        : `${officeList.length} office(s)`;
      message.success(`✅ Applied ${formatValue(value, LEVER_GROUPS.find(g => g.columns.some(c => c.key === field))?.columns.find(c => c.key === field)?.formatter || 'number')} globally to ${officeText}${levelText}${monthsText}. ${changesCount} changes added to draft.`);
    } catch (error) {
      console.error('[CONFIG] ❌ Error applying global change:', error);
      message.error('Failed to apply global configuration change');
    }
  };

  // Format value based on type
  const formatValue = (value: any, formatter: string) => {
    if (value === null || value === undefined || value === '') return '-';
    const numValue = Number(value);
    if (isNaN(numValue)) {
      return value;
    }
    switch (formatter) {
      case 'currency':
        return `${(numValue / 1000).toFixed(0)}k SEK`;
      case 'percentage':
        // If value is <= 1, treat as decimal (0.05 -> 5%), else treat as percent (5 -> 5%)
        return `${(numValue <= 1 ? numValue * 100 : numValue).toFixed(1)}%`;
      case 'number':
        return numValue.toFixed(1);
      default:
        return value;
    }
  };

  // Parse value based on type
  const parseValue = (str: string, formatter: string) => {
    // Remove all non-numeric and non-dot characters
    const cleaned = str.replace(/[^0-9.]/g, '');
    if (cleaned === '') return 0;
    const num = parseFloat(cleaned);
    if (isNaN(num)) return 0;
    switch (formatter) {
      case 'currency':
        return num * 1000;
      case 'percentage':
        // Always interpret as percent: 5 => 0.05, 5% => 0.05
        return num / 100;
      default:
        return num;
    }
  };

  // Helper to calculate aggregated FTE for a role
  const getAggregatedFTE = (roleName: string) => {
    const currentOfficeData = officeData[selectedOffice];
    if (!currentOfficeData || !currentOfficeData.roles || !currentOfficeData.roles[roleName]) {
      return 0;
    }
    
    const roleData = currentOfficeData.roles[roleName];
    
    // Handle 'Operations' which has a flat structure
    if (roleName === 'Operations') {
      return roleData.fte || 0;
    }

    // Handle roles with levels
    return Object.values(roleData).reduce((acc: number, level: any) => acc + (level.fte || 0), 0);
  };

  // Generate table data with grouped structure
  const getTableData = () => {
    if (!officeData[selectedOffice]) return [];

    const currentOfficeData = officeData[selectedOffice];
    const rows: any[] = [];

    // --- 1. Handle Roles with Levels (e.g., Consultant, Sales) ---
    ROLES_WITH_LEVELS.forEach(roleName => {
      const roleData = currentOfficeData.roles[roleName];
      if (!roleData) return;

      // Create a parent row for the role itself
      const parentRow: any = {
        key: roleName,
        role: roleName,
        isParent: true,
        children: []
      };

      // Set aggregated total for the parent row's FTE
      parentRow[`total_headcount`] = getAggregatedFTE(roleName);
      
      // Create child rows for each level within the role
      LEVELS.forEach(levelName => {
        const levelData = roleData[levelName];
        // Always show the row, even if FTE is 0
        const childRow: any = {
          key: `${roleName}-${levelName}`,
          role: levelName,
          isParent: false
        };
        // Populate data for each column in the group
        LEVER_GROUPS.forEach(group => {
          group.columns.forEach(col => {
            childRow[`${col.key}_${group.key}`] = getValue(roleName, levelName, col.key, selectedMonths[group.key]);
          });
        });
        parentRow.children.push(childRow);
      });
      // Always push the parent row (even if all children are zero)
      rows.push(parentRow);
    });

    // --- 2. Handle Roles without Levels (e.g., Operations) ---
    const operationsRoleName = 'Operations';
    const operationsData = currentOfficeData.roles[operationsRoleName];
    if (operationsData) {
      const operationsRow: any = {
        key: operationsRoleName,
        role: operationsRoleName,
        isParent: false, // Treat as a single row, not expandable
      };
      LEVER_GROUPS.forEach(group => {
        group.columns.forEach(col => {
          operationsRow[`${col.key}_${group.key}`] = getValue(operationsRoleName, null, col.key, selectedMonths[group.key]);
        });
      });
      rows.push(operationsRow);
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
                  popupMatchSelectWidth={80}
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
                  popupMatchSelectWidth={80}
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

  return (
    <div>
      <Card title={<Title level={4} style={{ margin: 0 }}>🔧 Lever Configuration Matrix</Title>}>
        {/* Header Controls */}
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col>
            <Upload
              beforeUpload={(file) => {
                handleFileUpload(file);
                return false; // Prevent default upload
              }}
              accept=".xlsx,.xls"
              showUploadList={false}
            >
              <Button icon={<UploadOutlined />} loading={loading}>
                Import Excel Configuration
              </Button>
            </Upload>
          </Col>
          <Col>
            <Button 
              icon={<DownloadOutlined />} 
              onClick={handleExportConfig}
              disabled={importing || loading}
              loading={loading}
            >
              �� Export All Offices (Excel)
            </Button>
          </Col>
          <Col>
            <Button 
              type="primary"
              icon={<GlobalOutlined />} 
              onClick={() => setShowGlobalModal(true)}
              disabled={importing || loading || offices.length === 0}
            >
              🌍 Global Configuration
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
                    disabled={importing}
                  >
                    💾 Apply Changes
                  </Button>
                  <Button 
                    icon={<ReloadOutlined />}
                    onClick={handleResetChanges}
                    disabled={importing}
                  >
                    🔄 Discard Changes
                  </Button>
                </>
              )}
              <Button 
                onClick={handleResetToOriginal}
                danger
                disabled={importing}
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
              disabled={importing}
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
              disabled={importing}
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
            {importing && (
              <Tag color="green">
                📤 Importing configuration...
              </Tag>
            )}
            {lastRefreshTime && !loading && !importing && (
              <Tag color="default">
                ✅ Last updated: {lastRefreshTime.toLocaleTimeString()}
              </Tag>
            )}
          </Col>
        </Row>

        {/* Instructions */}
        <Row style={{ marginBottom: 16 }}>
          <Col span={24}>
            <Text type="secondary">
              • <strong>Orange highlights</strong> indicate modified values
              • <strong>🌍 Global Configuration:</strong> Set values across multiple offices and levels at once (e.g., recruitment rate for levels A, AC, C = 3%)
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
            loading={loading || importing}
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
                <li><strong>🌍 Global Configuration:</strong> Apply values to multiple offices simultaneously</li>
                <li><strong>Draft mode:</strong> All changes are saved as drafts until applied</li>
                <li><strong>Group expand/collapse:</strong> Focus on specific metrics</li>
                <li><strong>Export functionality:</strong> Save current configuration with all changes</li>
                <li><strong>Reset options:</strong> Discard changes or reset to original</li>
              </ul>
            </Col>
          </Row>
        </Card>

        {/* Global Configuration Modal */}
        <Modal
          title="🌍 Global Configuration"
          open={showGlobalModal}
          onCancel={() => {
            setShowGlobalModal(false);
            globalForm.resetFields();
          }}
          onOk={() => globalForm.submit()}
          okText="Apply Globally"
          cancelText="Cancel"
          width={600}
        >
          <Form
            form={globalForm}
            layout="vertical"
            onFinish={handleGlobalChange}
          >
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  label="Role"
                  name="role"
                  rules={[{ required: true, message: 'Please select a role' }]}
                >
                  <Select placeholder="Select role">
                    {ROLES.map(role => (
                      <Option key={role} value={role}>{role}</Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  label="Levels (Optional)"
                  name="levels"
                  tooltip="Select multiple levels or leave empty for Operations role or to apply to all levels"
                >
                  <Select 
                    mode="multiple"
                    placeholder="Select levels (optional)" 
                    allowClear
                  >
                    {LEVELS.map(level => (
                      <Option key={level} value={level}>{level}</Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  label="Field"
                  name="field"
                  rules={[{ required: true, message: 'Please select a field' }]}
                >
                  <Select placeholder="Select field to change">
                    {LEVER_GROUPS.flatMap(group => 
                      group.columns.map(col => (
                        <Option key={col.key} value={col.key}>
                          {group.icon} {col.label} ({group.label})
                        </Option>
                      ))
                    )}
                  </Select>
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  label="Month"
                  name="month"
                  dependencies={['applyToAllMonthsGlobal']}
                  rules={[
                    {
                      required: true,
                      validator: (_, value) => {
                        if (!value && value !== 0) {
                          return Promise.reject(new Error('Please select a month'));
                        }
                        return Promise.resolve();
                      },
                    },
                  ]}
                  tooltip="Select specific month or 'All months'. For FTE values, month is ignored."
                >
                  <Select placeholder="Select month">
                    <Option key={0} value={0}>All months</Option>
                    {MONTHS.map(month => (
                      <Option key={month.value} value={month.value}>
                        {month.label}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  label="Value"
                  name="value"
                  rules={[{ required: true, message: 'Please enter a value' }]}
                  tooltip="Enter in display format (e.g., 3% for recruitment, 120k for salary)"
                >
                  <InputNumber 
                    placeholder="Enter value"
                    style={{ width: '100%' }}
                    precision={3}
                  />
                </Form.Item>
              </Col>
                             <Col span={12}>
                 <Form.Item
                   label="Target Offices"
                   name="targetOffices"
                   tooltip="Select specific offices or choose 'All Offices'"
                 >
                   <Select
                     mode="multiple"
                     placeholder="Select offices"
                     allowClear
                   >
                     <Option key="ALL_OFFICES" value="ALL_OFFICES">
                       🌍 All Offices ({offices.length} offices)
                     </Option>
                     {offices.map(office => (
                       <Option key={office} value={office}>{office}</Option>
                     ))}
                   </Select>
                 </Form.Item>
               </Col>
            </Row>

            <Card size="small" bodyStyle={{ background: '#222', color: '#eee' }} style={{ marginTop: 16, borderRadius: 6 }} bordered={false}>
              <Text style={{ color: '#eee' }}>
                <strong>💡 Examples:</strong><br/>
                • Set recruitment rate for level A to 3% - select "�� All Offices"<br/>
                • Update price for levels AC, C, SrC to 1500 SEK globally<br/>
                • Change churn rate for all consultant levels (leave levels empty)<br/>
                • Set UTR for Operations to 85% for specific offices (Stockholm, Munich)<br/>
                • Apply salary changes to multiple levels (A, AC, C) across all offices
              </Text>
            </Card>
          </Form>
        </Modal>
      </Card>
    </div>
  );
} 