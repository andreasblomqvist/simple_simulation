import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Typography, Form, Select, Button, InputNumber, Table, Upload, message, Tag } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { useConfig } from '../components/ConfigContext';

const { Title, Text } = Typography;
const { Option } = Select;

const ROLES = ['Consultant', 'Sales', 'Recruitment', 'Operations'];
const ROLES_WITH_LEVELS = ['Consultant', 'Sales', 'Recruitment'];
const LEVELS = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP'];
const LEVER_KEYS = [
  { key: 'fte', label: 'FTE' },
  { key: 'price_1', label: 'Price Jan' },
  { key: 'price_2', label: 'Price Feb' },
  { key: 'price_3', label: 'Price Mar' },
  { key: 'price_4', label: 'Price Apr' },
  { key: 'price_5', label: 'Price May' },
  { key: 'price_6', label: 'Price Jun' },
  { key: 'price_7', label: 'Price Jul' },
  { key: 'price_8', label: 'Price Aug' },
  { key: 'price_9', label: 'Price Sep' },
  { key: 'price_10', label: 'Price Oct' },
  { key: 'price_11', label: 'Price Nov' },
  { key: 'price_12', label: 'Price Dec' },
  { key: 'salary_1', label: 'Salary Jan' },
  { key: 'salary_2', label: 'Salary Feb' },
  { key: 'salary_3', label: 'Salary Mar' },
  { key: 'salary_4', label: 'Salary Apr' },
  { key: 'salary_5', label: 'Salary May' },
  { key: 'salary_6', label: 'Salary Jun' },
  { key: 'salary_7', label: 'Salary Jul' },
  { key: 'salary_8', label: 'Salary Aug' },
  { key: 'salary_9', label: 'Salary Sep' },
  { key: 'salary_10', label: 'Salary Oct' },
  { key: 'salary_11', label: 'Salary Nov' },
  { key: 'salary_12', label: 'Salary Dec' },
  { key: 'recruitment_1', label: 'Recruitment Jan' },
  { key: 'recruitment_2', label: 'Recruitment Feb' },
  { key: 'recruitment_3', label: 'Recruitment Mar' },
  { key: 'recruitment_4', label: 'Recruitment Apr' },
  { key: 'recruitment_5', label: 'Recruitment May' },
  { key: 'recruitment_6', label: 'Recruitment Jun' },
  { key: 'recruitment_7', label: 'Recruitment Jul' },
  { key: 'recruitment_8', label: 'Recruitment Aug' },
  { key: 'recruitment_9', label: 'Recruitment Sep' },
  { key: 'recruitment_10', label: 'Recruitment Oct' },
  { key: 'recruitment_11', label: 'Recruitment Nov' },
  { key: 'recruitment_12', label: 'Recruitment Dec' },
  { key: 'churn_1', label: 'Churn Jan' },
  { key: 'churn_2', label: 'Churn Feb' },
  { key: 'churn_3', label: 'Churn Mar' },
  { key: 'churn_4', label: 'Churn Apr' },
  { key: 'churn_5', label: 'Churn May' },
  { key: 'churn_6', label: 'Churn Jun' },
  { key: 'churn_7', label: 'Churn Jul' },
  { key: 'churn_8', label: 'Churn Aug' },
  { key: 'churn_9', label: 'Churn Sep' },
  { key: 'churn_10', label: 'Churn Oct' },
  { key: 'churn_11', label: 'Churn Nov' },
  { key: 'churn_12', label: 'Churn Dec' },
  { key: 'progression_1', label: 'Progression Jan' },
  { key: 'progression_2', label: 'Progression Feb' },
  { key: 'progression_3', label: 'Progression Mar' },
  { key: 'progression_4', label: 'Progression Apr' },
  { key: 'progression_5', label: 'Progression May' },
  { key: 'progression_6', label: 'Progression Jun' },
  { key: 'progression_7', label: 'Progression Jul' },
  { key: 'progression_8', label: 'Progression Aug' },
  { key: 'progression_9', label: 'Progression Sep' },
  { key: 'progression_10', label: 'Progression Oct' },
  { key: 'progression_11', label: 'Progression Nov' },
  { key: 'progression_12', label: 'Progression Dec' },
  { key: 'utr_1', label: 'UTR Jan' },
  { key: 'utr_2', label: 'UTR Feb' },
  { key: 'utr_3', label: 'UTR Mar' },
  { key: 'utr_4', label: 'UTR Apr' },
  { key: 'utr_5', label: 'UTR May' },
  { key: 'utr_6', label: 'UTR Jun' },
  { key: 'utr_7', label: 'UTR Jul' },
  { key: 'utr_8', label: 'UTR Aug' },
  { key: 'utr_9', label: 'UTR Sep' },
  { key: 'utr_10', label: 'UTR Oct' },
  { key: 'utr_11', label: 'UTR Nov' },
  { key: 'utr_12', label: 'UTR Dec' },
];

export default function Configuration() {
  const [offices, setOffices] = useState<string[]>([]);
  const [selectedOffice, setSelectedOffice] = useState<string>('');
  const [officeData, setOfficeData] = useState<any>({});
  const { setLevers } = useConfig();
  const [loading, setLoading] = useState(false);

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

  // Generate table data similar to Simulation page
  const getTableData = () => {
    if (!selectedOffice || !officeData[selectedOffice]) {
      return [];
    }

    const office = officeData[selectedOffice];
    const rows: any[] = [];

    // Add roles with levels (Consultant, Sales, Recruitment)
    ['Consultant', 'Sales', 'Recruitment'].forEach(roleName => {
      const roleData = office.roles[roleName];
      if (!roleData) return;

      // Parent row for role
      const roleRow: any = {
        key: roleName,
        role: roleName,
        level: null,
        fte: Object.values(roleData).reduce((sum: number, level: any) => sum + (level.total || 0), 0),
        children: []
      };

      // Child rows for levels
      Object.entries(roleData).forEach(([levelName, levelData]: [string, any]) => {
        if (levelData.total > 0) {
          roleRow.children.push({
            key: `${roleName}-${levelName}`,
            role: roleName,
            level: levelName,
            fte: levelData.total,
            // Monthly data (showing sample months)
            price_1: levelData.price_1,
            price_2: levelData.price_2,
            price_3: levelData.price_3,
            salary_1: levelData.salary_1,
            salary_2: levelData.salary_2,
            salary_3: levelData.salary_3,
            recruitment_1: levelData.recruitment_1,
            recruitment_2: levelData.recruitment_2,
            recruitment_3: levelData.recruitment_3,
            churn_1: levelData.churn_1,
            churn_2: levelData.churn_2,
            churn_3: levelData.churn_3,
            progression_1: levelData.progression_1,
            progression_2: levelData.progression_2,
            progression_3: levelData.progression_3,
          });
        }
      });

      if (roleRow.children.length > 0) {
        rows.push(roleRow);
      }
    });

    // Add Operations (flat role)
    if (office.roles.Operations && office.roles.Operations.total > 0) {
      rows.push({
        key: 'Operations',
        role: 'Operations',
        level: null,
        fte: office.roles.Operations.total,
        price_1: office.roles.Operations.price_1,
        price_2: office.roles.Operations.price_2,
        price_3: office.roles.Operations.price_3,
        salary_1: office.roles.Operations.salary_1,
        salary_2: office.roles.Operations.salary_2,
        salary_3: office.roles.Operations.salary_3,
        recruitment_1: office.roles.Operations.recruitment_1,
        recruitment_2: office.roles.Operations.recruitment_2,
        recruitment_3: office.roles.Operations.recruitment_3,
        churn_1: office.roles.Operations.churn_1,
        churn_2: office.roles.Operations.churn_2,
        churn_3: office.roles.Operations.churn_3,
        progression_1: office.roles.Operations.progression_1,
        progression_2: office.roles.Operations.progression_2,
        progression_3: office.roles.Operations.progression_3,
      });
    }

    return rows;
  };

  // Table columns similar to Simulation page
  const columns = [
    {
      title: 'Role / Level',
      key: 'role',
      width: 150,
      render: (text: string, record: any) => (
        <div>
          <div style={{ fontWeight: record.level ? 'normal' : 'bold' }}>
            {record.level ? `${record.level}` : record.role}
          </div>
          {record.level && <Text type="secondary" style={{ fontSize: '12px' }}>{record.role}</Text>}
        </div>
      ),
    },
    {
      title: 'FTE',
      dataIndex: 'fte',
      key: 'fte',
      width: 80,
      render: (val: number) => val?.toFixed(0) || '0',
    },
    {
      title: 'Price (Jan)',
      dataIndex: 'price_1',
      key: 'price_1',
      width: 100,
      render: (val: number) => val ? `${val.toFixed(0)} SEK` : '-',
    },
    {
      title: 'Price (Feb)',
      dataIndex: 'price_2',
      key: 'price_2',
      width: 100,
      render: (val: number) => val ? `${val.toFixed(0)} SEK` : '-',
    },
    {
      title: 'Price (Mar)',
      dataIndex: 'price_3',
      key: 'price_3',
      width: 100,
      render: (val: number) => val ? `${val.toFixed(0)} SEK` : '-',
    },
    {
      title: 'Salary (Jan)',
      dataIndex: 'salary_1',
      key: 'salary_1',
      width: 100,
      render: (val: number) => val ? `${val.toFixed(0)} SEK` : '-',
    },
    {
      title: 'Salary (Feb)',
      dataIndex: 'salary_2',
      key: 'salary_2',
      width: 100,
      render: (val: number) => val ? `${val.toFixed(0)} SEK` : '-',
    },
    {
      title: 'Salary (Mar)',
      dataIndex: 'salary_3',
      key: 'salary_3',
      width: 100,
      render: (val: number) => val ? `${val.toFixed(0)} SEK` : '-',
    },
    {
      title: 'Recruitment (Jan)',
      dataIndex: 'recruitment_1',
      key: 'recruitment_1',
      width: 120,
      render: (val: number) => val ? `${(val * 100).toFixed(1)}%` : '-',
    },
    {
      title: 'Churn (Jan)',
      dataIndex: 'churn_1',
      key: 'churn_1',
      width: 100,
      render: (val: number) => val ? `${(val * 100).toFixed(1)}%` : '-',
    },
    {
      title: 'Progression (Jan)',
      dataIndex: 'progression_1',
      key: 'progression_1',
      width: 120,
      render: (val: number) => val ? `${(val * 100).toFixed(1)}%` : '-',
    },
  ];

  const uploadProps = {
    name: 'file',
    accept: '.xlsx,.xls,.csv',
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
    <Card title={<Title level={4} style={{ margin: 0 }}>Configuration</Title>}>
      {/* Import Button */}
      <Row style={{ marginBottom: 16 }}>
        <Col>
          <Upload {...uploadProps}>
            <Button icon={<UploadOutlined />}>Import Office Config (Excel)</Button>
          </Upload>
        </Col>
      </Row>
      
      {/* Office Configuration Table */}
      <Card style={{ marginBottom: 24 }}>
        <Row align="middle" gutter={16} style={{ marginBottom: 16 }}>
          <Col><Title level={5} style={{ margin: 0 }}>Office Configuration (Sample: Jan-Mar)</Title></Col>
          <Col>
            <Select value={selectedOffice} onChange={setSelectedOffice} style={{ width: 200 }}>
              {offices.map(office => <Option key={office} value={office}>{office}</Option>)}
            </Select>
          </Col>
        </Row>
        <Table
          columns={columns}
          dataSource={getTableData()}
          pagination={false}
          rowKey={record => record.key}
          size="small"
          expandable={{ 
            defaultExpandAllRows: true,
            indentSize: 20
          }}
          scroll={{ x: 1200 }}
        />
        <Text type="secondary" style={{ marginTop: 8, display: 'block' }}>
          Note: This table shows a sample of monthly data (Jan-Mar). The full dataset includes all 12 months for each metric.
        </Text>
      </Card>
    </Card>
  );
} 