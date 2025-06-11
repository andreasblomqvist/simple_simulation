import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Typography, Form, Select, Button, InputNumber, Table, Upload, message, Tag } from 'antd';
import { UploadOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;
const { Option } = Select;

const ROLES = ['Consultant', 'Sales', 'Recruitment', 'Operations'];
const ROLES_WITH_LEVELS = ['Consultant', 'Sales', 'Recruitment'];
const LEVELS = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP'];
const LEVER_KEYS = [
  { key: 'fte', label: 'FTE' },
  { key: 'price_h1', label: 'Price H1' },
  { key: 'price_h2', label: 'Price H2' },
  { key: 'salary_h1', label: 'Salary H1' },
  { key: 'salary_h2', label: 'Salary H2' },
  { key: 'recruitment_h1', label: 'Recruitment H1' },
  { key: 'recruitment_h2', label: 'Recruitment H2' },
  { key: 'churn_h1', label: 'Churn H1' },
  { key: 'churn_h2', label: 'Churn H2' },
  { key: 'progression_h1', label: 'Progression H1' },
  { key: 'progression_h2', label: 'Progression H2' },
  { key: 'utr_h1', label: 'UTR H1' },
  { key: 'utr_h2', label: 'UTR H2' },
];

export default function Configuration() {
  const [offices, setOffices] = useState<string[]>([]);
  const [selectedOffice, setSelectedOffice] = useState<string>('');
  const [rolesData, setRolesData] = useState<any>({});

  const fetchOffices = () => {
    fetch('/api/offices')
      .then(res => res.json())
      .then(data => {
        setOffices(data.map((o: any) => o.name));
        setSelectedOffice(data[0]?.name || '');
        const officeMap: any = {};
        data.forEach((o: any) => {
          officeMap[o.name] = o.roles;
        });
        setRolesData(officeMap);
      });
  };

  useEffect(() => {
    fetchOffices();
  }, []);

  // New table columns
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
    ...LEVER_KEYS.filter(lv => lv.key !== 'fte').map(lv => ({
      title: lv.label,
      dataIndex: lv.key,
      key: lv.key,
      render: (val: any) => val !== undefined && val !== null ? val : '-',
    })),
  ];

  // New data transformation for table
  const getTableData = () => {
    if (!selectedOffice || !rolesData[selectedOffice]) return [];
    const roles = rolesData[selectedOffice];
    let rows: any[] = [];
    ROLES.forEach(role => {
      if (roles[role]) {
        if (ROLES_WITH_LEVELS.includes(role)) {
          // Role with levels
          const children = LEVELS.map(level => {
            const data = roles[role][level] || {};
            return {
              key: `${role}-${level}`,
              role,
              level,
              total: data.total ?? 0,
              ...data,
            };
          });
          rows.push({
            key: role,
            role,
            children,
          });
        } else {
          // Flat role (Operations)
          const data = roles[role] || {};
          rows.push({
            key: role,
            role,
            total: data.total ?? 0,
            ...data,
          });
        }
      } else {
        // Role missing in backend, show as zero
        if (ROLES_WITH_LEVELS.includes(role)) {
          const children = LEVELS.map(level => ({
            key: `${role}-${level}`,
            role,
            level,
            total: 0,
          }));
          rows.push({
            key: role,
            role,
            children,
          });
        } else {
          rows.push({
            key: role,
            role,
            total: 0,
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
          <Col><Title level={5} style={{ margin: 0 }}>Office Levers</Title></Col>
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
        />
      </Card>
    </Card>
  );
} 