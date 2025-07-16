import React, { useState, forwardRef, useImperativeHandle } from 'react';
import { Tabs, Alert, Button, Select, Table, InputNumber, Typography, Space, message } from 'antd';
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

const { TabPane } = Tabs;
const { Option } = Select;
const { Text } = Typography;

// Generate months for 3-year simulation using unified month key generator
const DEFAULT_MONTHS = generateMonthKeys(2025, 1, 2027, 12);

// Default values for recruitment and leavers (churn) per role/level/month
const recruitmentDefaults: Record<string, Record<string, Record<string, number | undefined>>> = {
  Consultant: {
    '202501': { A: 20, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
    '202502': { A: 20, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
    '202503': { A: 10, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
    '202504': { A: 15, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
    '202505': { A: 10, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
    '202506': { A: 10, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
    '202507': { A: 5, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
    '202508': { A: 20, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
    '202509': { A: 90, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
    '202510': { A: 20, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
    '202511': { A: 15, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
    '202512': { A: 10, AC: 8, C: 4, SrC: 1, AM: 1, M: undefined, SrM: undefined, PiP: undefined },
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

// Fill Sales and Recruitment with 0s for all months/levels
ROLES.forEach(role => {
  if (role === 'Sales' || role === 'Recruitment') {
    DEFAULT_MONTHS.forEach(month => {
      recruitmentDefaults[role][month] = {};
      leaversDefaults[role][month] = {};
      ROLE_LEVELS[role].forEach(level => {
        recruitmentDefaults[role][month][level] = 0;
        leaversDefaults[role][month][level] = 0;
      });
    });
  }
});

// Extend Consultant defaults to all years (2026, 2027) by copying 2025 values
const extendDefaultsToAllYears = () => {
  // For each year after 2025
  for (let year = 2026; year <= 2027; year++) {
    // For each month in that year
    for (let month = 1; month <= 12; month++) {
      const targetMonth = `${year}${month.toString().padStart(2, '0')}`;
      const sourceMonth = `2025${month.toString().padStart(2, '0')}`;
      
      // Copy recruitment defaults
      if (recruitmentDefaults.Consultant[sourceMonth]) {
        recruitmentDefaults.Consultant[targetMonth] = { ...recruitmentDefaults.Consultant[sourceMonth] };
      }
      
      // Copy churn defaults
      if (leaversDefaults.Consultant[sourceMonth]) {
        leaversDefaults.Consultant[targetMonth] = { ...leaversDefaults.Consultant[sourceMonth] };
      }
    }
  }
};

// Extend defaults to all years
extendDefaultsToAllYears();

// Helper to initialize recruitment/churn data structure with defaults
const initRoleData = () => {
  const data: Record<string, Record<string, Record<string, number | undefined>>> = {};
  ROLES.forEach(role => {
    data[role] = {};
    ROLE_LEVELS[role].forEach(level => {
      data[role][level] = {};
      DEFAULT_MONTHS.forEach(month => {
        // Use defaults if available, else undefined
        data[role][level][month] =
          (role in recruitmentDefaults && month in recruitmentDefaults[role] && level in recruitmentDefaults[role][month])
            ? recruitmentDefaults[role][month][level]
            : undefined;
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
        // Use defaults if available, else undefined
        data[role][level][month] =
          (role in leaversDefaults && month in leaversDefaults[role] && level in leaversDefaults[role][month])
            ? leaversDefaults[role][month][level]
            : undefined;
      });
    });
  });
  return data;
};

interface BaselineInputGridProps {
  onNext: (data: any) => void;
}

const BaselineInputGrid = forwardRef<any, BaselineInputGridProps>(({ onNext }, ref) => {
  const [activeTab, setActiveTab] = useState('recruitment');
  const [selectedRole, setSelectedRole] = useState(DEFAULT_ROLE);
  const [recruitmentData, setRecruitmentData] = useState(initRoleData());
  const [leaversData, setLeaversData] = useState(initLeaverRoleData());

  useImperativeHandle(ref, () => ({
    getCurrentData: () => {
      const data = {
        global: {
          recruitment: recruitmentData,
          churn: leaversData,
        }
      };
      console.log('[DEBUG][BaselineInputGrid] getCurrentData() returning:', data);
      console.log('[DEBUG][BaselineInputGrid] recruitmentData structure:', recruitmentData);
      if (recruitmentData.Consultant && recruitmentData.Consultant.A) {
        console.log('[DEBUG][BaselineInputGrid] Consultant A recruitment data:', recruitmentData.Consultant.A);
      }
      return data;
    }
  }));

  const handleCellChange = (month: string, level: string, value: number | null) => {
    if (activeTab === 'recruitment') {
      setRecruitmentData(prev => ({
        ...prev,
        [selectedRole]: {
          ...prev[selectedRole],
          [level]: {
            ...prev[selectedRole][level],
            [month]: value === null ? undefined : value
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
            [month]: value === null ? undefined : value
          }
        }
      }));
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
            
            newData[selectedRole][level][targetMonth] = year2025Values[level][sourceMonth];
          });
        }
      }
      
      return newData;
    });

    message.success(`Applied 2025 ${activeTab} values to all years for ${selectedRole}`);
  };

  const handleNext = () => {
    const baselineInput = {
      global: {
        recruitment: recruitmentData,
        churn: leaversData,
      }
    };
    onNext(baselineInput);
  };

  // Build Ant Design Table columns
  const levels = ROLE_LEVELS[selectedRole];
  const columns = [
    {
      title: <Text strong>Month</Text>,
      dataIndex: 'month',
      key: 'month',
      fixed: 'left' as const,
      width: 90,
      align: 'center' as const,
      render: (month: string) => <Text>{month}</Text>,
    },
    ...levels.map(level => ({
      title: <Text strong>{level}</Text>,
      dataIndex: level,
      key: level,
      width: 90,
      align: 'center' as const,
      render: (value: number | undefined, row: any) => (
        <InputNumber
          min={0}
          value={value}
          onChange={val => handleCellChange(row.month, level, val === null ? null : Number(val))}
          style={{ width: 70 }}
        />
      ),
    })),
  ];

  // Prepare table data
  const tableData = DEFAULT_MONTHS.map(month => ({
    key: month,
    month,
    ...levels.reduce((acc, level) => {
      acc[level] = activeTab === 'recruitment' 
        ? recruitmentData[selectedRole]?.[level]?.[month]
        : leaversData[selectedRole]?.[level]?.[month];
      return acc;
    }, {} as Record<string, number | undefined>),
  }));

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ marginBottom: '20px' }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div>
            <Text strong style={{ fontSize: '18px' }}>
              Baseline Input Configuration
            </Text>
            <Text type="secondary" style={{ marginLeft: '10px' }}>
              Configure monthly recruitment and churn values for each role and level
            </Text>
          </div>
          
          <Alert
            message="Apply for All Years"
            description="Click the button below to copy all 2025 values to subsequent years (2026, 2027, etc.). This ensures the simulation has complete data for all years."
            type="info"
            showIcon
            action={
              <Button 
                type="primary" 
                onClick={handleApplyForAllYears}
                size="small"
              >
                Apply 2025 Values to All Years
              </Button>
            }
          />
        </Space>
      </div>

      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab="Recruitment" key="recruitment">
          <div style={{ marginBottom: '16px' }}>
            <Space>
              <Text strong>Role:</Text>
              <Select
                value={selectedRole}
                onChange={setSelectedRole}
                style={{ width: 150 }}
              >
                {ROLES.map(role => (
                  <Option key={role} value={role}>{role}</Option>
                ))}
              </Select>
            </Space>
          </div>
          
          <Table
            columns={columns}
            dataSource={tableData}
            pagination={false}
            scroll={{ x: 'max-content' }}
            size="small"
            bordered
          />
        </TabPane>
        
        <TabPane tab="Churn (Leavers)" key="churn">
          <div style={{ marginBottom: '16px' }}>
            <Space>
              <Text strong>Role:</Text>
              <Select
                value={selectedRole}
                onChange={setSelectedRole}
                style={{ width: 150 }}
              >
                {ROLES.map(role => (
                  <Option key={role} value={role}>{role}</Option>
                ))}
              </Select>
            </Space>
          </div>
          
          <Table
            columns={columns}
            dataSource={tableData}
            pagination={false}
            scroll={{ x: 'max-content' }}
            size="small"
            bordered
          />
        </TabPane>
      </Tabs>

      <div style={{ marginTop: '20px', textAlign: 'right' }}>
        <Button type="primary" onClick={handleNext}>
          Next
        </Button>
      </div>
    </div>
  );
});

export default BaselineInputGrid; 