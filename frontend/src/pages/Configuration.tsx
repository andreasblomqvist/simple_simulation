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
  const [rolesData, setRolesData] = useState<any>({});
  const { setLevers } = useConfig();
  const [loading, setLoading] = useState(false);

  const fetchOffices = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/offices');
      const data = await res.json();
      setRolesData(data);
      setLevers(data);
      setOffices(data.map((o: any) => o.name));
      setSelectedOffice(data[0]?.name || '');
    } catch (err) {
      message.error('Failed to fetch offices');
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchOffices();
  }, []);

  // New table columns - showing only first 3 months for better UX
  const columns = [
    {
      title: 'Role',
      dataIndex: 'role',
      key: 'role',
      render: (text: string, row: any) => (
        <span>{row.level ? '' : row.role}</span>
      ),
    },
    {
      title: 'Level',
      dataIndex: 'level',
      key: 'level',
      render: (text: string) => text || '-',
    },
    {
      title: 'Total FTE',
      dataIndex: 'fte',
      key: 'fte',
      render: (text: any, row: any) => {
        if (row.level) {
          // Child row: show FTE for this level
          return row.total ?? row.fte ?? 0;
        } else if (row.children && row.children.length > 0) {
          // Parent row: sum FTEs of all children
          return row.children.reduce((sum: number, child: any) => sum + (child.total ?? child.fte ?? 0), 0);
        } else {
          // Flat role (Operations)
          return row.total ?? row.fte ?? 0;
        }
      },
    },
    // Show a sample of monthly data (Jan-Mar)
    { title: 'Price Jan', dataIndex: 'price_1', key: 'price_1', render: (val: any) => val ? Number(val).toFixed(2) : '-' },
    { title: 'Price Feb', dataIndex: 'price_2', key: 'price_2', render: (val: any) => val ? Number(val).toFixed(2) : '-' },
    { title: 'Price Mar', dataIndex: 'price_3', key: 'price_3', render: (val: any) => val ? Number(val).toFixed(2) : '-' },
    { title: 'Salary Jan', dataIndex: 'salary_1', key: 'salary_1', render: (val: any) => val ? Number(val).toFixed(2) : '-' },
    { title: 'Salary Feb', dataIndex: 'salary_2', key: 'salary_2', render: (val: any) => val ? Number(val).toFixed(2) : '-' },
    { title: 'Salary Mar', dataIndex: 'salary_3', key: 'salary_3', render: (val: any) => val ? Number(val).toFixed(2) : '-' },
    { title: 'Recruit Jan', dataIndex: 'recruitment_1', key: 'recruitment_1', render: (val: any) => val ? Number(val).toFixed(2) : '-' },
    { title: 'Churn Jan', dataIndex: 'churn_1', key: 'churn_1', render: (val: any) => val ? Number(val).toFixed(2) : '-' },
    { title: 'Progress Jan', dataIndex: 'progression_1', key: 'progression_1', render: (val: any) => val ? Number(val).toFixed(2) : '-' },
    { title: 'UTR Jan', dataIndex: 'utr_1', key: 'utr_1', render: (val: any) => val ? Number(val).toFixed(2) : '-' },
  ];

  // New data transformation for table
  const getTableData = () => {
    if (!selectedOffice || !rolesData || !Array.isArray(rolesData)) return [];
    const office = rolesData.find((o: any) => o.name === selectedOffice);
    if (!office || !office.roles) return [];
    let rows: any[] = [];
    ROLES.forEach(role => {
      const roleData = office.roles[role];
      if (roleData) {
        if (ROLES_WITH_LEVELS.includes(role)) {
          // Role with levels
          const children = LEVELS.map(level => {
            const data = roleData[level] || {};
            // Prepare monthly data for display
            const monthlyData: any = {};
            for (let i = 1; i <= 12; i++) {
              monthlyData[`price_${i}`] = data[`price_${i}`] ?? data[`_${i}`] ?? 0;
              monthlyData[`salary_${i}`] = data[`salary_${i}`] ?? 0;
              monthlyData[`recruitment_${i}`] = data[`recruitment_${i}`] ?? 0;
              monthlyData[`churn_${i}`] = data[`churn_${i}`] ?? 0;
              monthlyData[`progression_${i}`] = data[`progression_${i}`] ?? 0;
              monthlyData[`utr_${i}`] = data[`utr_${i}`] ?? 0;
            }
            return {
              key: `${role}-${level}`,
              role,
              level,
              total: data.total ?? 0,
              ...monthlyData,
            };
          });

          rows.push({
            key: role,
            role,
            children,
          });
        } else {
          // Flat role (Operations)
          const data = roleData || {};
          const monthlyData: any = {};
          for (let i = 1; i <= 12; i++) {
            monthlyData[`price_${i}`] = data[`price_${i}`] ?? data[`_${i}`] ?? 0;
            monthlyData[`salary_${i}`] = data[`salary_${i}`] ?? 0;
            monthlyData[`recruitment_${i}`] = data[`recruitment_${i}`] ?? 0;
            monthlyData[`churn_${i}`] = data[`churn_${i}`] ?? 0;
            monthlyData[`progression_${i}`] = data[`progression_${i}`] ?? 0;
            monthlyData[`utr_${i}`] = data[`utr_${i}`] ?? 0;
          }
          rows.push({
            key: role,
            role,
            total: data.total ?? 0,
            ...monthlyData,
          });
        }
      } else {
        // Role missing in backend, show as zero
        if (ROLES_WITH_LEVELS.includes(role)) {
          const children = LEVELS.map(level => {
            const monthlyData: any = {};
            for (let i = 1; i <= 12; i++) {
              monthlyData[`price_${i}`] = 0;
              monthlyData[`salary_${i}`] = 0;
              monthlyData[`recruitment_${i}`] = 0;
              monthlyData[`churn_${i}`] = 0;
              monthlyData[`progression_${i}`] = 0;
              monthlyData[`utr_${i}`] = 0;
            }
            return {
              key: `${role}-${level}`,
              role,
              level,
              total: 0,
              ...monthlyData,
            };
          });
          rows.push({
            key: role,
            role,
            children,
          });
        } else {
          const monthlyData: any = {};
          for (let i = 1; i <= 12; i++) {
            monthlyData[`price_${i}`] = 0;
            monthlyData[`salary_${i}`] = 0;
            monthlyData[`recruitment_${i}`] = 0;
            monthlyData[`churn_${i}`] = 0;
            monthlyData[`progression_${i}`] = 0;
            monthlyData[`utr_${i}`] = 0;
          }
          rows.push({
            key: role,
            role,
            total: 0,
            ...monthlyData,
          });
        }
      }
    });
    return rows;
  };

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
        fetchOffices();
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
      {/* Office Lever Table */}
      <Card style={{ marginBottom: 24 }}>
        <Row align="middle" gutter={16} style={{ marginBottom: 16 }}>
          <Col><Title level={5} style={{ margin: 0 }}>Office Levers (Monthly Data - Showing Jan-Mar Sample)</Title></Col>
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
          rowKey={row => row.key}
          size="small"
          expandable={{ defaultExpandAllRows: true }}
          scroll={{ x: 1200 }}
        />
        <Text type="secondary" style={{ marginTop: 8, display: 'block' }}>
          Note: This table shows a sample of monthly data (Jan-Mar). The full dataset includes all 12 months for each metric.
        </Text>
      </Card>
    </Card>
  );
} 