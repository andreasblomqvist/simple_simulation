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
      render: (val: any) => {
        if (val === undefined || val === null) return '-';
        if (['price_h1', 'price_h2', 'salary_h1', 'salary_h2'].includes(lv.key)) {
          const num = Number(val);
          if (!isNaN(num)) return num.toFixed(2);
        }
        return val;
      },
    })),
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
            // Format price and salary as value (start) if both available
            const price = (data.price !== undefined && data.price_start !== undefined)
              ? `${Number(data.price).toFixed(2)} (${Number(data.price_start).toFixed(2)})`
              : data.price !== undefined ? Number(data.price).toFixed(2) : data.price_start !== undefined ? `(${Number(data.price_start).toFixed(2)})` : '-';
            const salary = (data.salary !== undefined && data.salary_start !== undefined)
              ? `${Number(data.salary).toFixed(2)} (${Number(data.salary_start).toFixed(2)})`
              : data.salary !== undefined ? Number(data.salary).toFixed(2) : data.salary_start !== undefined ? `(${Number(data.salary_start).toFixed(2)})` : '-';
            // Format all lever columns
            const levers: any = {};
            LEVER_KEYS.forEach(lv => {
              if (lv.key !== 'fte') {
                const v = data[lv.key];
                levers[lv.key] = v !== undefined && v !== null && !isNaN(Number(v)) ? Number(v).toFixed(2) : v ?? '-';
              }
            });
            return {
              key: `${role}-${level}`,
              role,
              level,
              total: data.total ?? 0,
              price,
              salary,
              ...levers,
            };
          });
          // Compute averages for price and salary for parent row
          const validPrices = children.map(c => parseFloat((c.price || '').toString().split(' ')[0])).filter(n => !isNaN(n));
          const validStartPrices = children.map(c => {
            const match = (c.price || '').toString().match(/\(([^)]+)\)/);
            return match ? parseFloat(match[1]) : NaN;
          }).filter(n => !isNaN(n));
          const avgPrice = validPrices.length ? (validPrices.reduce((a, b) => a + b, 0) / validPrices.length) : null;
          const avgStartPrice = validStartPrices.length ? (validStartPrices.reduce((a, b) => a + b, 0) / validStartPrices.length) : null;
          const price = (avgPrice !== null && avgStartPrice !== null)
            ? `${avgPrice.toFixed(2)} (${avgStartPrice.toFixed(2)})`
            : avgPrice !== null ? avgPrice.toFixed(2) : avgStartPrice !== null ? `(${avgStartPrice.toFixed(2)})` : '-';
          const validSalaries = children.map(c => parseFloat((c.salary || '').toString().split(' ')[0])).filter(n => !isNaN(n));
          const validStartSalaries = children.map(c => {
            const match = (c.salary || '').toString().match(/\(([^)]+)\)/);
            return match ? parseFloat(match[1]) : NaN;
          }).filter(n => !isNaN(n));
          const avgSalary = validSalaries.length ? (validSalaries.reduce((a, b) => a + b, 0) / validSalaries.length) : null;
          const avgStartSalary = validStartSalaries.length ? (validStartSalaries.reduce((a, b) => a + b, 0) / validStartSalaries.length) : null;
          const salary = (avgSalary !== null && avgStartSalary !== null)
            ? `${avgSalary.toFixed(2)} (${avgStartSalary.toFixed(2)})`
            : avgSalary !== null ? avgSalary.toFixed(2) : avgStartSalary !== null ? `(${avgStartSalary.toFixed(2)})` : '-';
          rows.push({
            key: role,
            role,
            price,
            salary,
            children,
          });
        } else {
          // Flat role (Operations)
          const data = roleData || {};
          const price = (data.price !== undefined && data.price_start !== undefined)
            ? `${Number(data.price).toFixed(2)} (${Number(data.price_start).toFixed(2)})`
            : data.price !== undefined ? Number(data.price).toFixed(2) : data.price_start !== undefined ? `(${Number(data.price_start).toFixed(2)})` : '-';
          const salary = (data.salary !== undefined && data.salary_start !== undefined)
            ? `${Number(data.salary).toFixed(2)} (${Number(data.salary_start).toFixed(2)})`
            : data.salary !== undefined ? Number(data.salary).toFixed(2) : data.salary_start !== undefined ? `(${Number(data.salary_start).toFixed(2)})` : '-';
          // Format all lever columns
          const levers: any = {};
          LEVER_KEYS.forEach(lv => {
            if (lv.key !== 'fte') {
              const v = data[lv.key];
              levers[lv.key] = v !== undefined && v !== null && !isNaN(Number(v)) ? Number(v).toFixed(2) : v ?? '-';
            }
          });
          rows.push({
            key: role,
            role,
            price,
            salary,
            ...levers,
            total: data.total ?? 0,
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
            price: '-',
            salary: '-',
            ...Object.fromEntries(LEVER_KEYS.filter(lv => lv.key !== 'fte').map(lv => [lv.key, '-'])),
          }));
          rows.push({
            key: role,
            role,
            price: '-',
            salary: '-',
            children,
          });
        } else {
          rows.push({
            key: role,
            role,
            price: '-',
            salary: '-',
            ...Object.fromEntries(LEVER_KEYS.filter(lv => lv.key !== 'fte').map(lv => [lv.key, '-'])),
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