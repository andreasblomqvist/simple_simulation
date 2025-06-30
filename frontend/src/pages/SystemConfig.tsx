import React, { useState, useEffect } from 'react';
import { Card, Table, InputNumber, Input, Button, Select, Typography, Space, message, Tabs } from 'antd';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

// CAT categories and their descriptions
const CAT_CATEGORIES = [
  { key: 'CAT0', label: 'CAT0', description: '0-6 months' },
  { key: 'CAT6', label: 'CAT6', description: '6-12 months' },
  { key: 'CAT12', label: 'CAT12', description: '12-18 months' },
  { key: 'CAT18', label: 'CAT18', description: '18-24 months' },
  { key: 'CAT24', label: 'CAT24', description: '24-30 months' },
  { key: 'CAT30', label: 'CAT30', description: '30+ months' },
  { key: 'CAT36', label: 'CAT36', description: '36+ months' },
  { key: 'CAT42', label: 'CAT42', description: '42+ months' },
  { key: 'CAT48', label: 'CAT48', description: '48+ months' },
  { key: 'CAT54', label: 'CAT54', description: '54+ months' },
  { key: 'CAT60', label: 'CAT60', description: '60+ months' },
];

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
  const [catData, setCatData] = useState<any[]>([]);
  const [editingKey, setEditingKey] = useState('');
  const [editingCatKey, setEditingCatKey] = useState('');
  const [loading, setLoading] = useState(true);

  const isEditing = (record: any) => record.key === editingKey;
  const isEditingCat = (record: any) => record.key === editingCatKey;

  const edit = (record: any) => {
    setEditingKey(record.key);
  };

  const editCat = (record: any) => {
    setEditingCatKey(record.key);
  };

  const save = (key: string) => {
    setEditingKey('');
    message.success('Saved! (not yet persisted)');
  };

  const saveCat = (key: string) => {
    setEditingCatKey('');
    message.success('CAT progression saved! (not yet persisted)');
  };

  const reset = () => {
    setData(initialData);
    loadCatProgression(); // Reload from backend instead of using hardcoded values
    setEditingKey('');
    setEditingCatKey('');
    message.info('Reset to initial values');
  };

  // Load CAT progression data from backend
  const loadCatProgression = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/simulation/system/cat-progression');
      if (response.ok) {
        const backendData = await response.json();
        setCatData(backendData);
        console.log('✅ Loaded CAT progression data from backend:', backendData.length, 'levels');
      } else {
        message.error('Failed to load CAT progression data from backend');
        console.error('Failed to load CAT progression data:', response.statusText);
      }
    } catch (error) {
      message.error('Error loading CAT progression data from backend');
      console.error('Error loading CAT progression data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Save CAT progression data to backend
  const saveCatProgression = async () => {
    try {
      const response = await fetch('/api/simulation/system/cat-progression', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(catData),
      });
      
      if (response.ok) {
        const result = await response.json();
        message.success(`CAT progression saved to backend! Updated ${result.updated_levels?.length || 0} levels`);
        console.log('✅ CAT progression saved to backend:', result);
      } else {
        const errorText = await response.text();
        message.error(`Failed to save CAT progression: ${errorText}`);
        console.error('Failed to save CAT progression:', response.statusText);
      }
    } catch (error) {
      message.error('Error saving CAT progression to backend');
      console.error('Error saving CAT progression:', error);
    }
  };

  useEffect(() => {
    loadCatProgression();
  }, []);

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

  // Create CAT progression columns
  const catColumns = [
    {
      title: 'Level',
      dataIndex: 'level',
      width: 80,
      fixed: 'left' as const,
    },
    ...CAT_CATEGORIES.map(cat => ({
      title: (
        <div style={{ textAlign: 'center' }}>
          <div>{cat.label}</div>
          <div style={{ fontSize: '10px', color: '#666' }}>{cat.description}</div>
        </div>
      ),
      dataIndex: cat.key,
      width: 100,
      render: (_: any, record: any) => {
        const value = record[cat.key] || 0;
        return isEditingCat(record) ? (
          <InputNumber
            min={0}
            max={1}
            step={0.001}
            value={value}
            onChange={val => handleCatFieldChange(record.key, cat.key, val)}
            style={{ width: '80px' }}
          />
        ) : (
          <span style={{ color: value > 0 ? '#1890ff' : '#999' }}>
            {(value * 100).toFixed(1)}%
          </span>
        );
      },
    })),
    {
      title: 'Action',
      dataIndex: 'action',
      width: 120,
      fixed: 'right' as const,
      render: (_: any, record: any) => isEditingCat(record) ? (
        <Space>
          <Button type="primary" size="small" onClick={() => saveCat(record.key)}>Save</Button>
          <Button size="small" onClick={() => setEditingCatKey('')}>Cancel</Button>
        </Space>
      ) : (
        <Button size="small" onClick={() => editCat(record)}>Edit</Button>
      ),
    },
  ];

  function handleFieldChange(key: string, field: string, value: any) {
    setData(prev => prev.map(row => row.key === key ? { ...row, [field]: value } : row));
  }

  function handleCatFieldChange(key: string, field: string, value: any) {
    setCatData(prev => prev.map(row => row.key === key ? { ...row, [field]: value } : row));
  }

  return (
    <Card style={{ margin: 32 }}>
      <Title level={3}>⚙️ System Configuration</Title>
      
      <Tabs defaultActiveKey="progression" style={{ marginTop: 16 }}>
        <TabPane tab="Progression Config" key="progression">
          <div style={{ marginBottom: 16 }}>
            <Text type="secondary">
              Configure progression timing and requirements for each level
            </Text>
          </div>
          <Table
            dataSource={data}
            columns={columns}
            pagination={false}
            rowKey="key"
            bordered
            size="middle"
            scroll={{ x: 'max-content' }}
          />
        </TabPane>
        
        <TabPane tab="CAT Progression" key="cat">
          <div style={{ marginBottom: 16 }}>
            <Text type="secondary">
              Configure CAT-based progression probabilities for each level and tenure category
            </Text>
            {loading && <Text type="secondary">Loading CAT progression data from backend...</Text>}
          </div>
          <Table
            dataSource={catData}
            columns={catColumns}
            pagination={false}
            rowKey="key"
            bordered
            size="middle"
            scroll={{ x: 'max-content' }}
            loading={loading}
          />
        </TabPane>
      </Tabs>
      
      <Space style={{ marginTop: 24 }}>
        <Button type="primary" onClick={() => message.success('Saved! (not yet persisted)')}>Save Progression</Button>
        <Button type="primary" onClick={saveCatProgression} disabled={loading}>Save CAT Progression</Button>
        <Button onClick={reset} disabled={loading}>Reset All</Button>
        <Button onClick={() => message.info('Import/Export not implemented yet')}>Import/Export</Button>
      </Space>
    </Card>
  );
} 