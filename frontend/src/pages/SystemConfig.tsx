import React, { useState } from 'react';
import { Card, Table, InputNumber, Input, Button, Select, Typography, Space, message } from 'antd';

const { Title } = Typography;

const initialData = [
  { key: 'A', level: 'A', timeOfLevel: 6, startTenure: 0, endTenure: 6, nextLevel: 'AC', levelMonths: '1,4,7,10' },
  { key: 'AC', level: 'AC', timeOfLevel: 9, startTenure: 6, endTenure: 15, nextLevel: 'C', levelMonths: '1,4,7,10' },
  { key: 'C', level: 'C', timeOfLevel: 18, startTenure: 15, endTenure: 33, nextLevel: 'SrC', levelMonths: '1,7' },
  { key: 'SrC', level: 'SrC', timeOfLevel: 18, startTenure: 33, endTenure: 51, nextLevel: 'AM', levelMonths: '1,7' },
  { key: 'AM', level: 'AM', timeOfLevel: 48, startTenure: 51, endTenure: 99, nextLevel: 'M', levelMonths: '1,7' },
  { key: 'M', level: 'M', timeOfLevel: 48, startTenure: 99, endTenure: 147, nextLevel: 'SrM', levelMonths: '1' },
  { key: 'SrM', level: 'SrM', timeOfLevel: 120, startTenure: 147, endTenure: 267, nextLevel: 'Pi', levelMonths: '1' },
  { key: 'Pi', level: 'Pi', timeOfLevel: 12, startTenure: 267, endTenure: 279, nextLevel: 'Pi', levelMonths: '1' },
  { key: 'P', level: 'P', timeOfLevel: 1000, startTenure: 279, endTenure: 1279, nextLevel: 'P', levelMonths: '1' },
  { key: 'X', level: 'X', timeOfLevel: 1279, startTenure: 1279, endTenure: 1279, nextLevel: 'X', levelMonths: '1' },
  { key: 'OPE', level: 'OPE', timeOfLevel: 1000, startTenure: 1279, endTenure: 2279, nextLevel: 'OPE', levelMonths: '1' },
];

export default function SystemConfig() {
  const [data, setData] = useState(initialData);
  const [editingKey, setEditingKey] = useState('');

  const isEditing = (record: any) => record.key === editingKey;

  const edit = (record: any) => {
    setEditingKey(record.key);
  };

  const save = (key: string) => {
    setEditingKey('');
    message.success('Saved! (not yet persisted)');
  };

  const reset = () => {
    setData(initialData);
    setEditingKey('');
    message.info('Reset to initial values');
  };

  const columns = [
    {
      title: 'Level',
      dataIndex: 'level',
      width: 80,
      editable: false,
    },
    {
      title: 'Time of Level',
      dataIndex: 'timeOfLevel',
      width: 120,
      editable: true,
      render: (_: any, record: any) => isEditing(record) ? (
        <InputNumber min={0} value={record.timeOfLevel} onChange={val => handleFieldChange(record.key, 'timeOfLevel', val)} />
      ) : record.timeOfLevel,
    },
    {
      title: 'Start Tenure',
      dataIndex: 'startTenure',
      width: 120,
      editable: true,
      render: (_: any, record: any) => isEditing(record) ? (
        <InputNumber min={0} value={record.startTenure} onChange={val => handleFieldChange(record.key, 'startTenure', val)} />
      ) : record.startTenure,
    },
    {
      title: 'End Tenure',
      dataIndex: 'endTenure',
      width: 120,
      editable: true,
      render: (_: any, record: any) => isEditing(record) ? (
        <InputNumber min={0} value={record.endTenure} onChange={val => handleFieldChange(record.key, 'endTenure', val)} />
      ) : record.endTenure,
    },
    {
      title: 'Next Level',
      dataIndex: 'nextLevel',
      width: 100,
      editable: true,
      render: (_: any, record: any) => isEditing(record) ? (
        <Input value={record.nextLevel} onChange={e => handleFieldChange(record.key, 'nextLevel', e.target.value)} />
      ) : record.nextLevel,
    },
    {
      title: 'Level Months',
      dataIndex: 'levelMonths',
      width: 140,
      editable: true,
      render: (_: any, record: any) => isEditing(record) ? (
        <Input value={record.levelMonths} onChange={e => handleFieldChange(record.key, 'levelMonths', e.target.value)} />
      ) : record.levelMonths,
    },
    {
      title: 'Action',
      dataIndex: 'action',
      width: 120,
      render: (_: any, record: any) => isEditing(record) ? (
        <Space>
          <Button type="primary" size="small" onClick={() => save(record.key)}>Save</Button>
          <Button size="small" onClick={() => setEditingKey('')}>Cancel</Button>
        </Space>
      ) : (
        <Button size="small" onClick={() => edit(record)}>Edit</Button>
      ),
    },
  ];

  function handleFieldChange(key: string, field: string, value: any) {
    setData(prev => prev.map(row => row.key === key ? { ...row, [field]: value } : row));
  }

  return (
    <Card style={{ margin: 32 }}>
      <Title level={3}>⚙️ System Configuration</Title>
      <Table
        dataSource={data}
        columns={columns}
        pagination={false}
        rowKey="key"
        bordered
        size="middle"
      />
      <Space style={{ marginTop: 24 }}>
        <Button type="primary" onClick={() => message.success('Saved! (not yet persisted)')}>Save</Button>
        <Button onClick={reset}>Reset</Button>
        <Button onClick={() => message.info('Import/Export not implemented yet')}>Import/Export</Button>
      </Space>
    </Card>
  );
} 