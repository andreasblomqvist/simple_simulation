import React, { useState, forwardRef, useImperativeHandle, useRef, useEffect } from 'react';
import { Tabs, Alert, Button, Select, Table, InputNumber, Typography, Space, message, Card, Row, Col, Divider } from 'antd';
import { 
  ROLE_LEVELS, 
  ROLES, 
  DEFAULT_ROLE,
  generateMonthKeys,
} from '../../types/unified-data-structures';
import type {
  LevelType,
  YearMonth,
  BaselineInputData,
  MonthlyValues,
} from '../../types/unified-data-structures';

// Removed TabPane destructuring as it's deprecated
const { Option } = Select;
const { Text } = Typography;

// Generate months for 3-year simulation using unified month key generator
const DEFAULT_MONTHS = generateMonthKeys(2025, 1, 2027, 12);

// Utility function to sanitize monthly values
const sanitizeMonthlyValue = (value: any): number => {
  // Convert to number and handle invalid cases
  if (value === null || value === undefined || value === '' || isNaN(value)) {
    return 0;
  }
  const numValue = Number(value);
  return isNaN(numValue) ? 0 : Math.max(0, numValue); // Ensure non-negative
};

// Utility function to sanitize all monthly values in a data structure
const sanitizeMonthlyData = (data: any): any => {
  if (!data || typeof data !== 'object') {
    return {};
  }
  
  const sanitized: any = {};
  
  Object.keys(data).forEach(role => {
    if (data[role] && typeof data[role] === 'object') {
      sanitized[role] = {};
      
      Object.keys(data[role]).forEach(level => {
        if (data[role][level] && typeof data[role][level] === 'object') {
          sanitized[role][level] = {};
          
          Object.keys(data[role][level]).forEach(month => {
            const value = data[role][level][month];
            sanitized[role][level][month] = sanitizeMonthlyValue(value);
          });
        }
      });
    }
  });
  
  return sanitized;
};

// Default values for recruitment and leavers (churn) per role/level/month
const recruitmentDefaults: Record<string, Record<string, Record<string, number | undefined>>> = {
  Consultant: {
    '202501': { A: 20, AC: 8, C: 4, SrC: 1, AM: 1, M: 0, SrM: 0, PiP: 0 },
    '202502': { A: 20, AC: 8, C: 4, SrC: 1, AM: 1, M: 1, SrM: 0, PiP: 0 },
    '202503': { A: 10, AC: 8, C: 4, SrC: 1, AM: 1, M: 0, SrM: 0, PiP: 0 },
    '202504': { A: 15, AC: 8, C: 4, SrC: 1, AM: 1, M: 0, SrM: 0, PiP: 0 },
    '202505': { A: 10, AC: 8, C: 4, SrC: 1, AM: 1, M: 0, SrM: 0, PiP: 0 },
    '202506': { A: 10, AC: 8, C: 4, SrC: 1, AM: 1, M: 1, SrM: 0, PiP: 0 },
    '202507': { A: 5, AC: 8, C: 4, SrC: 1, AM: 1, M: 0, SrM: 0, PiP: 0 },
    '202508': { A: 20, AC: 8, C: 4, SrC: 1, AM: 1, M: 1, SrM: 0, PiP: 0 },
    '202509': { A: 90, AC: 8, C: 4, SrC: 1, AM: 1, M: 0, SrM: 1, PiP: 0 },
    '202510': { A: 20, AC: 8, C: 4, SrC: 1, AM: 1, M: 0, SrM: 0, PiP: 0 },
    '202511': { A: 15, AC: 8, C: 4, SrC: 1, AM: 1, M: 0, SrM: 0, PiP: 0 },
    '202512': { A: 10, AC: 8, C: 4, SrC: 1, AM: 1, M: 1, SrM: 0, PiP: 0 },
  },
  Sales: {},
  Recruitment: {},
};
const leaversDefaults: Record<string, Record<string, Record<string, number | undefined>>> = {
  Consultant: {
    '202501': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 0, PiP: 0 },
    '202502': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, PiP: 0 },
    '202503': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 0, PiP: 1 },
    '202504': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 0, PiP: 0 },
    '202505': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 0, PiP: 0 },
    '202506': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, PiP: 0 },
    '202507': { A: 4, AC: 4, C: 7, SrC: 7, AM: 9, M: 2, SrM: 0, PiP: 0 },
    '202508': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, PiP: 1 },
    '202509': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 2, PiP: 0 },
    '202510': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, PiP: 1 },
    '202511': { A: 4, AC: 4, C: 7, SrC: 7, AM: 9, M: 2, SrM: 1, PiP: 1 },
    '202512': { A: 2, AC: 4, C: 7, SrC: 7, AM: 9, M: 1, SrM: 1, PiP: 0 },
  },
  Sales: {},
  Recruitment: {},
};

// Add realistic defaults for Sales and Recruitment roles
const salesRecruitmentDefaults = {
  A: 5, AC: 3, C: 2, SrC: 1, AM: 0, M: 0, SrM: 0, PiP: 0
};
const salesChurnDefaults = {
  A: 1, AC: 2, C: 3, SrC: 2, AM: 1, M: 0, SrM: 0, PiP: 0
};

const recruitmentRecruitmentDefaults = {
  A: 3, AC: 2, C: 1, SrC: 0, AM: 0, M: 0, SrM: 0, PiP: 0
};
const recruitmentChurnDefaults = {
  A: 1, AC: 1, C: 2, SrC: 1, AM: 0, M: 0, SrM: 0, PiP: 0
};

// Add defaults for Operations (flat role - no levels)
const operationsDefaults = {
  recruitment: 2, // Monthly operations recruitment
  churn: 1        // Monthly operations churn
};

// Fill Sales, Recruitment, and Operations with realistic defaults
ROLES.forEach(role => {
  if (role === 'Sales' || role === 'Recruitment') {
    DEFAULT_MONTHS.forEach(month => {
      recruitmentDefaults[role][month] = {};
      leaversDefaults[role][month] = {};
      ROLE_LEVELS[role].forEach(level => {
        if (role === 'Sales') {
          recruitmentDefaults[role][month][level] = salesRecruitmentDefaults[level] || 0;
          leaversDefaults[role][month][level] = salesChurnDefaults[level] || 0;
        } else if (role === 'Recruitment') {
          recruitmentDefaults[role][month][level] = recruitmentRecruitmentDefaults[level] || 0;
          leaversDefaults[role][month][level] = recruitmentChurnDefaults[level] || 0;
        }
      });
    });
  } else if (role === 'Operations') {
    // Operations is a flat role, so we handle it differently
    DEFAULT_MONTHS.forEach(month => {
      if (!recruitmentDefaults[role]) recruitmentDefaults[role] = {};
      if (!leaversDefaults[role]) leaversDefaults[role] = {};
      
      // For flat roles, we store the values directly under the month key
      recruitmentDefaults[role][month] = { 'N/A': operationsDefaults.recruitment };
      leaversDefaults[role][month] = { 'N/A': operationsDefaults.churn };
    });
  }
});

// Extend defaults to all years (2026, 2027) by copying 2025 values for all roles
const extendDefaultsToAllYears = () => {
  // For each year after 2025
  for (let year = 2026; year <= 2027; year++) {
    // For each month in that year
    for (let month = 1; month <= 12; month++) {
      const targetMonth = `${year}${month.toString().padStart(2, '0')}`;
      const sourceMonth = `2025${month.toString().padStart(2, '0')}`;
      
      // Extend for all roles
      ROLES.forEach(role => {
        // Copy recruitment defaults
        if (recruitmentDefaults[role] && recruitmentDefaults[role][sourceMonth]) {
          if (!recruitmentDefaults[role][targetMonth]) {
            recruitmentDefaults[role][targetMonth] = { ...recruitmentDefaults[role][sourceMonth] };
          }
        }
        
        // Copy churn defaults  
        if (leaversDefaults[role] && leaversDefaults[role][sourceMonth]) {
          if (!leaversDefaults[role][targetMonth]) {
            leaversDefaults[role][targetMonth] = { ...leaversDefaults[role][sourceMonth] };
          }
        }
      });
    }
  }
};

// Extend defaults to all years
extendDefaultsToAllYears();

// Helper to initialize recruitment data structure with defaults
const initRoleData = () => {
  const data: Record<string, Record<string, Record<string, number | undefined>>> = {};
  ROLES.forEach(role => {
    data[role] = {};
    ROLE_LEVELS[role].forEach(level => {
      data[role][level] = {};
      DEFAULT_MONTHS.forEach(month => {
        // Always use defaults if available (changed from undefined fallback)
        data[role][level][month] =
          (role in recruitmentDefaults && month in recruitmentDefaults[role] && level in recruitmentDefaults[role][month])
            ? recruitmentDefaults[role][month][level]
            : 0; // Default to 0 instead of undefined for better UX
      });
    });
  });
  return data;
};

const initLeaverRoleData = () => {
  const data: Record<string, Record<string, Record<string, number | undefined>>> = {};
  ROLES.forEach(role => {
    data[role] = {};
    ROLE_LEVELS[role].forEach(level => {
      data[role][level] = {};
      DEFAULT_MONTHS.forEach(month => {
        // Always use defaults if available (changed from undefined fallback)
        data[role][level][month] =
          (role in leaversDefaults && month in leaversDefaults[role] && level in leaversDefaults[role][month])
            ? leaversDefaults[role][month][level]
            : 0; // Default to 0 instead of undefined for better UX
      });
    });
  });
  return data;
};

interface BaselineInputGridProps {
  onNext: (data: any) => void;
  initialData?: any;
}

// Function to initialize data from existing baseline input
const initializeFromBaseline = (initialData: any, dataType: 'recruitment' | 'churn') => {
  // Handle both old 'global' and new 'global_data' formats
  if (!initialData?.global_data?.[dataType] && !initialData?.global?.[dataType]) {
    return dataType === 'recruitment' ? initRoleData() : initLeaverRoleData();
  }
  
  // Try new format first, then fall back to old format
  const sourceData = initialData?.global_data?.[dataType] || initialData?.global?.[dataType];
  
  // sourceData: { Consultant: { levels: { A: { recruitment: { values: { '202501': 10, ... } }, churn: ... }, ... } }, ... }
  const data: any = {};
  ROLES.forEach(role => {
    data[role] = {};
    const roleLevels = sourceData[role]?.levels || {};
    ROLE_LEVELS[role as keyof typeof ROLE_LEVELS]?.forEach(level => {
      // Default to empty object if missing
      const levelData = roleLevels[level] || {};
      // For recruitment: levelData.recruitment?.values; for churn: levelData.churn?.values
      const values = (dataType === 'recruitment')
        ? levelData.recruitment?.values || {}
        : levelData.churn?.values || {};
      data[role][level] = {};
      DEFAULT_MONTHS.forEach(month => {
        data[role][level][month] = values[month] !== undefined ? values[month] : undefined;
      });
    });
  });
  return data;
};

const BaselineInputGrid = forwardRef<any, BaselineInputGridProps>(({ onNext, initialData }, ref) => {
  const [activeTab, setActiveTab] = useState('recruitment');
  const [selectedRole, setSelectedRole] = useState(DEFAULT_ROLE);
  const [recruitmentData, setRecruitmentData] = useState(() => initializeFromBaseline(initialData, 'recruitment'));
  const [leaversData, setLeaversData] = useState(() => initializeFromBaseline(initialData, 'churn'));
  const inputRefs = useRef<Record<string, any>>({});

  useImperativeHandle(ref, () => ({
    getCurrentData: () => {
      // Build structure that matches unified_data_models.py exactly
      // BaselineInput { global_data: Dict[str, Dict[str, RoleData]] }
      // RoleData { levels: Dict[str, LevelData] }
      // LevelData { recruitment: MonthlyValues, churn: MonthlyValues }
      // MonthlyValues { values: Dict[str, float] }
      
      const buildRoleData = () => {
        const result: any = {};
        
        // Get all roles from both datasets
        const allRoles = new Set([...Object.keys(recruitmentData), ...Object.keys(leaversData)]);
        
        allRoles.forEach(role => {
          const roleLevels = ROLE_LEVELS[role] || [];
          
          // Only add role if it has data
          const roleHasData = roleLevels.some(level => 
            (recruitmentData[role] && recruitmentData[role][level]) ||
            (leaversData[role] && leaversData[role][level])
          );
          
          if (roleHasData) {
            result[role] = {
              levels: {}
            };
            
            roleLevels.forEach(level => {
              const hasRecruitmentData = recruitmentData[role] && recruitmentData[role][level];
              const hasChurnData = leaversData[role] && leaversData[role][level];
              
              if (hasRecruitmentData || hasChurnData) {
                result[role].levels[level] = {
                  recruitment: {
                    values: hasRecruitmentData ? recruitmentData[role][level] : {}
                  },
                  churn: {
                    values: hasChurnData ? leaversData[role][level] : {}
                  }
                };
              }
            });
          }
        });
        
        return result;
      };

      const roleData = buildRoleData();

      // Both recruitment and churn sections contain the same role data 
      // (each role has both recruitment and churn values in its levels)
      return {
        global_data: {
          recruitment: roleData,
          churn: roleData,
        }
      };
    }
  }));

  // Helper function to format month display
  const formatMonth = (month: string) => {
    const year = month.slice(0, 4);
    const monthNum = month.slice(4, 6);
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return `${monthNames[parseInt(monthNum) - 1]} ${year}`;
  };

  // Helper function to get quarter for grouping
  const getQuarter = (month: string) => {
    const year = month.slice(0, 4);
    const monthNum = parseInt(month.slice(4, 6));
    const quarter = Math.ceil(monthNum / 3);
    return `Q${quarter} ${year}`;
  };

  // Group months by quarters for better organization
  const groupMonthsByQuarter = (months: string[]) => {
    const groups: Record<string, string[]> = {};
    months.forEach(month => {
      const quarter = getQuarter(month);
      if (!groups[quarter]) groups[quarter] = [];
      groups[quarter].push(month);
    });
    return groups;
  };

  const handleCellChange = (month: string, level: string, value: number | null) => {
    // Sanitize the input value
    const sanitizedValue = sanitizeMonthlyValue(value);
    
    if (activeTab === 'recruitment') {
      setRecruitmentData(prev => ({
        ...prev,
        [selectedRole]: {
          ...prev[selectedRole],
          [level]: {
            ...prev[selectedRole][level],
            [month]: sanitizedValue
          }
        }
      }));
    } else {
      setLeaversData(prev => ({
        ...prev,
        [selectedRole]: {
          ...prev[selectedRole],
          [level]: {
            ...prev[selectedRole][level],
            [month]: sanitizedValue
          }
        }
      }));
    }
  };

  // Enhanced input navigation
  const handleInputKeyDown = (e: React.KeyboardEvent, month: string, level: string, levels: string[], months: string[]) => {
    if (e.key === 'Tab' || e.key === 'Enter') {
      e.preventDefault();
      
      const currentLevelIndex = levels.indexOf(level);
      const currentMonthIndex = months.indexOf(month);
      
      let nextMonth = month;
      let nextLevel = level;
      
      if (e.key === 'Tab' && !e.shiftKey) {
        // Move to next level or next month
        if (currentLevelIndex < levels.length - 1) {
          nextLevel = levels[currentLevelIndex + 1];
        } else if (currentMonthIndex < months.length - 1) {
          nextLevel = levels[0];
          nextMonth = months[currentMonthIndex + 1];
        }
      } else if (e.key === 'Tab' && e.shiftKey) {
        // Move to previous level or previous month
        if (currentLevelIndex > 0) {
          nextLevel = levels[currentLevelIndex - 1];
        } else if (currentMonthIndex > 0) {
          nextLevel = levels[levels.length - 1];
          nextMonth = months[currentMonthIndex - 1];
        }
      } else if (e.key === 'Enter') {
        // Move to next month, same level
        if (currentMonthIndex < months.length - 1) {
          nextMonth = months[currentMonthIndex + 1];
        }
      }
      
      // Focus the next input
      const nextInputKey = `${nextMonth}-${nextLevel}`;
      if (inputRefs.current[nextInputKey]) {
        setTimeout(() => {
          inputRefs.current[nextInputKey]?.focus();
        }, 50);
      }
    }
  };

  // Function to apply 2025 values to all years
  const handleApplyForAllYears = () => {
    const currentData = activeTab === 'recruitment' ? recruitmentData : leaversData;
    const setData = activeTab === 'recruitment' ? setRecruitmentData : setLeaversData;
    
    // Get 2025 values for the selected role
    const year2025Values: Record<string, Record<string, number | undefined>> = {};
    ROLE_LEVELS[selectedRole].forEach(level => {
      year2025Values[level] = {};
      // Get all 2025 months (202501-202512)
      for (let month = 1; month <= 12; month++) {
        const monthKey = `2025${month.toString().padStart(2, '0')}`;
        year2025Values[level][monthKey] = currentData[selectedRole]?.[level]?.[monthKey];
      }
    });

    // Apply 2025 values to all subsequent years (2026, 2027, etc.)
    setData(prev => {
      const newData = { ...prev };
      
      // For each year after 2025
      for (let year = 2026; year <= 2027; year++) {
        // For each month in that year
        for (let month = 1; month <= 12; month++) {
          const targetMonth = `${year}${month.toString().padStart(2, '0')}`;
          const sourceMonth = `2025${month.toString().padStart(2, '0')}`;
          
          // Copy values for each level
          ROLE_LEVELS[selectedRole].forEach(level => {
            if (!newData[selectedRole]) newData[selectedRole] = {};
            if (!newData[selectedRole][level]) newData[selectedRole][level] = {};
            
            newData[selectedRole][level][targetMonth] = sanitizeMonthlyValue(year2025Values[level][sourceMonth]);
          });
        }
      }
      
      return newData;
    });

    message.success(`Applied 2025 ${activeTab} values to all years for ${selectedRole}`);
  };

  const handleNext = () => {
    // Sanitize all data before sending to parent
    const sanitizedRecruitmentData = sanitizeMonthlyData(recruitmentData);
    const sanitizedLeaversData = sanitizeMonthlyData(leaversData);
    
    // Use the same structure as getCurrentData that matches unified_data_models.py
    const buildRoleData = () => {
      const result: any = {};
      
      // Get all roles from both datasets
      const allRoles = new Set([...Object.keys(sanitizedRecruitmentData), ...Object.keys(sanitizedLeaversData)]);
      
      allRoles.forEach(role => {
        const roleLevels = ROLE_LEVELS[role] || [];
        
        // Only add role if it has data
        const roleHasData = roleLevels.some(level => 
          (sanitizedRecruitmentData[role] && sanitizedRecruitmentData[role][level]) ||
          (sanitizedLeaversData[role] && sanitizedLeaversData[role][level])
        );
        
        if (roleHasData) {
          result[role] = {
            levels: {}
          };
          
          roleLevels.forEach(level => {
            const hasRecruitmentData = sanitizedRecruitmentData[role] && sanitizedRecruitmentData[role][level];
            const hasChurnData = sanitizedLeaversData[role] && sanitizedLeaversData[role][level];
            
            if (hasRecruitmentData || hasChurnData) {
              result[role].levels[level] = {
                recruitment: {
                  values: hasRecruitmentData ? sanitizedRecruitmentData[role][level] : {}
                },
                churn: {
                  values: hasChurnData ? sanitizedLeaversData[role][level] : {}
                }
              };
            }
          });
        }
      });
      
      return result;
    };
    
    const roleData = buildRoleData();
    
    const baselineInput = {
      global_data: {
        recruitment: roleData,
        churn: roleData,
      }
    };
    onNext(baselineInput);
  };

  // Enhanced input rendering with better UX
  const renderEnhancedInput = (month: string, level: string, levels: string[], months: string[]) => {
    const currentData = activeTab === 'recruitment' ? recruitmentData : leaversData;
    const value = currentData[selectedRole]?.[level]?.[month];
    const inputKey = `${month}-${level}`;
    
    // Get placeholder based on defaults
    const placeholderValue = activeTab === 'recruitment' 
      ? recruitmentDefaults[selectedRole]?.[month]?.[level]
      : leaversDefaults[selectedRole]?.[month]?.[level];
    
    return (
      <InputNumber
        ref={el => inputRefs.current[inputKey] = el}
        min={0}
        value={value}
        onChange={val => handleCellChange(month, level, val === null ? null : Number(val))}
        onKeyDown={e => handleInputKeyDown(e, month, level, levels, months)}
        placeholder={placeholderValue !== undefined ? `${placeholderValue}` : '0'}
        style={{ 
          width: '100%', 
          minWidth: 80,
        }}
        size="large"
        autoFocus={month === months[0] && level === levels[0]}
      />
    );
  };

  const levels = ROLE_LEVELS[selectedRole];
  const quarterGroups = groupMonthsByQuarter(DEFAULT_MONTHS);

  return (
    <div style={{ padding: '0' }}>
      <div style={{ marginBottom: '16px' }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div>
            <Text strong style={{ fontSize: '18px' }}>
              Baseline Input Configuration
            </Text>
            <Text type="secondary" style={{ marginLeft: '10px' }}>
              Configure monthly {activeTab} values for each role and level. Use Tab or Enter to navigate between fields.
            </Text>
          </div>
          
          <Alert
            message="Navigation Tips"
            description="• Use Tab to move to next level, Shift+Tab for previous level • Use Enter to move to next month • Placeholder values show suggested defaults • Apply 2025 values to all years for complete simulation data"
            type="info"
            showIcon
            action={
              <Button 
                type="primary" 
                onClick={handleApplyForAllYears}
                size="small"
              >
                Apply 2025 to All Years
              </Button>
            }
          />
        </Space>
      </div>

      <Tabs 
        activeKey={activeTab} 
        onChange={setActiveTab}
        size="large"
        items={[
          {
            key: 'recruitment',
            label: (
              <span style={{ fontSize: '16px', fontWeight: 500 }}>
                📈 Recruitment
              </span>
            ),
            children: (
              <div>
                <div style={{ marginBottom: '16px' }}>
                  <Space size="large">
                    <div>
                      <Text strong style={{ marginRight: 8 }}>Role:</Text>
                      <Select
                        value={selectedRole}
                        onChange={setSelectedRole}
                        style={{ width: 180 }}
                        size="large"
                      >
                        {ROLES.map(role => (
                          <Option key={role} value={role}>{role}</Option>
                        ))}
                      </Select>
                    </div>
                    <Text type="secondary">
                      Enter monthly recruitment numbers for {selectedRole} role
                    </Text>
                  </Space>
                </div>
                
                {Object.entries(quarterGroups).map(([quarter, months], quarterIndex) => (
                  <Card 
                    key={quarter} 
                    title={
                      <Text strong style={{ fontSize: '16px' }}>
                        {quarter}
                      </Text>
                    }
                    style={{ 
                      marginBottom: '20px',
                      borderRadius: '8px',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                    }}
                    headStyle={{ backgroundColor: '#fafafa' }}
                  >
                    <div style={{ display: 'grid', gap: '16px' }}>
                      {/* Headers */}
                      <Row gutter={[12, 8]} align="middle">
                        <Col span={4}>
                          <Text strong>Month</Text>
                        </Col>
                        {levels.map(level => (
                          <Col key={level} span={Math.floor(20 / levels.length)}>
                            <Text strong>{level}</Text>
                          </Col>
                        ))}
                      </Row>
                      
                      <Divider style={{ margin: '8px 0' }} />
                      
                      {/* Input rows */}
                      {months.map((month, monthIndex) => (
                        <Row key={month} gutter={[12, 8]} align="middle">
                          <Col span={4}>
                            <Text strong style={{ color: '#1890ff' }}>
                              {formatMonth(month)}
                            </Text>
                          </Col>
                          {levels.map(level => (
                            <Col key={level} span={Math.floor(20 / levels.length)}>
                              {renderEnhancedInput(month, level, levels, DEFAULT_MONTHS)}
                            </Col>
                          ))}
                        </Row>
                      ))}
                    </div>
                  </Card>
                ))}
              </div>
            ),
          },
          {
            key: 'churn',
            label: (
              <span style={{ fontSize: '16px', fontWeight: 500 }}>
                📉 Churn (Leavers)
              </span>
            ),
            children: (
              <div>
                <div style={{ marginBottom: '16px' }}>
                  <Space size="large">
                    <div>
                      <Text strong style={{ marginRight: 8 }}>Role:</Text>
                      <Select
                        value={selectedRole}
                        onChange={setSelectedRole}
                        style={{ width: 180 }}
                        size="large"
                      >
                        {ROLES.map(role => (
                          <Option key={role} value={role}>{role}</Option>
                        ))}
                      </Select>
                    </div>
                    <Text type="secondary">
                      Enter monthly churn/leaving numbers for {selectedRole} role
                    </Text>
                  </Space>
                </div>
                
                {Object.entries(quarterGroups).map(([quarter, months], quarterIndex) => (
                  <Card 
                    key={quarter} 
                    title={
                      <Text strong style={{ fontSize: '16px' }}>
                        {quarter}
                      </Text>
                    }
                    style={{ 
                      marginBottom: '20px',
                      borderRadius: '8px',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                    }}
                    headStyle={{ backgroundColor: '#fafafa' }}
                  >
                    <div style={{ display: 'grid', gap: '16px' }}>
                      {/* Headers */}
                      <Row gutter={[12, 8]} align="middle">
                        <Col span={4}>
                          <Text strong>Month</Text>
                        </Col>
                        {levels.map(level => (
                          <Col key={level} span={Math.floor(20 / levels.length)}>
                            <Text strong>{level}</Text>
                          </Col>
                        ))}
                      </Row>
                      
                      <Divider style={{ margin: '8px 0' }} />
                      
                      {/* Input rows */}
                      {months.map((month, monthIndex) => (
                        <Row key={month} gutter={[12, 8]} align="middle">
                          <Col span={4}>
                            <Text strong style={{ color: '#1890ff' }}>
                              {formatMonth(month)}
                            </Text>
                          </Col>
                          {levels.map(level => (
                            <Col key={level} span={Math.floor(20 / levels.length)}>
                              {renderEnhancedInput(month, level, levels, DEFAULT_MONTHS)}
                            </Col>
                          ))}
                        </Row>
                      ))}
                    </div>
                  </Card>
                ))}
              </div>
            ),
          },
        ]}
      />

      <div style={{ marginTop: '16px', textAlign: 'right' }}>
        <Button type="primary" size="large" onClick={handleNext}>
          Next Step
        </Button>
      </div>
    </div>
  );
});

export default BaselineInputGrid; 