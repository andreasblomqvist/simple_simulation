import React, { useState, forwardRef, useImperativeHandle } from 'react';
import { Tabs, Alert, Button, Select, Table, InputNumber, Typography } from 'antd';

const { TabPane } = Tabs;
const { Option } = Select;
const { Text } = Typography;

// Define roles and their levels (excluding Operations)
const ROLE_LEVELS: Record<string, string[]> = {
  Consultant: ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP'],
  Sales: ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP'],
  Recruitment: ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP'],
  // Add more roles/levels as needed
};
const ROLES = Object.keys(ROLE_LEVELS);
const DEFAULT_ROLE = 'Consultant';

const MONTHS = [
  '202501', '202502', '202503', '202504', '202505', '202506',
  '202507', '202508', '202509', '202510', '202511', '202512',
];

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
    MONTHS.forEach(month => {
      recruitmentDefaults[role][month] = {};
      leaversDefaults[role][month] = {};
      ROLE_LEVELS[role].forEach(level => {
        recruitmentDefaults[role][month][level] = 0;
        leaversDefaults[role][month][level] = 0;
      });
    });
  }
});

// Helper to initialize recruitment/churn data structure with defaults
const initRoleData = () => {
  const data: Record<string, Record<string, Record<string, number | undefined>>> = {};
  ROLES.forEach(role => {
    data[role] = {};
    ROLE_LEVELS[role].forEach(level => {
      data[role][level] = {};
      MONTHS.forEach(month => {
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
      MONTHS.forEach(month => {
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

  // Build dataSource for Table
  const dataSource = MONTHS.map(month => {
    const row: any = { month };
    levels.forEach(level => {
      if (activeTab === 'recruitment') {
        row[level] = recruitmentData[selectedRole][level][month];
      } else {
        row[level] = leaversData[selectedRole][level][month];
      }
    });
    return row;
  });

  return (
    <div>
      <Alert
        message="Baseline Input Configuration"
        description="Configure the baseline recruitment and churn (leaver) numbers for each role and level."
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />
      <div style={{ marginBottom: 16 }}>
        <span style={{ marginRight: 8, fontWeight: 500 }}>Select Role:</span>
        <Select value={selectedRole} onChange={setSelectedRole} style={{ minWidth: 180 }}>
          {ROLES.map(role => (
            <Option key={role} value={role}>{role}</Option>
          ))}
        </Select>
      </div>
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab="Recruitment" key="recruitment">
          <Table
            columns={columns}
            dataSource={dataSource}
            pagination={false}
            bordered
            size="middle"
            scroll={{ x: true }}
            rowKey="month"
            style={{ background: 'inherit' }}
          />
        </TabPane>
        <TabPane tab="Leavers (Churn)" key="leavers">
          <Table
            columns={columns}
            dataSource={dataSource}
            pagination={false}
            bordered
            size="middle"
            scroll={{ x: true }}
            rowKey="month"
            style={{ background: 'inherit' }}
          />
        </TabPane>
      </Tabs>
    </div>
  );
});

export default BaselineInputGrid; 