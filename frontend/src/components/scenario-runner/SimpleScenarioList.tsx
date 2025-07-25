import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Space, Popconfirm, Typography } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { scenarioApi } from '../../services/scenarioApi';
import type { ScenarioListItem } from '../../types/unified-data-structures';
import { showMessage } from '../../utils/message';

const { Title } = Typography;

const SimpleScenarioList: React.FC = () => {
  const navigate = useNavigate();
  const [scenarios, setScenarios] = useState<ScenarioListItem[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadScenarios();
  }, []);

  const loadScenarios = async () => {
    try {
      setLoading(true);
      const data = await scenarioApi.listScenarios();
      console.log('Loaded scenarios:', data);
      setScenarios(data);
    } catch (error) {
      showMessage.error('Failed to load scenarios');
      console.error('Load scenarios error:', error);
      if (error instanceof Error) {
        console.error('Error message:', error.message);
        console.error('Error stack:', error.stack);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await scenarioApi.deleteScenario(id);
      showMessage.success('Scenario deleted successfully');
      loadScenarios();
    } catch (error) {
      showMessage.error('Failed to delete scenario');
    }
  };

  const handleRunSimulation = async (id: string) => {
    try {
      const result = await scenarioApi.runScenarioById(id);
      
      if (result.status === 'success') {
        showMessage.success('Simulation completed successfully');
        // Navigate to results view or show results modal
      } else {
        showMessage.error(`Simulation failed: ${result.error_message}`);
      }
    } catch (error) {
      showMessage.error('Failed to run simulation');
    }
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: ScenarioListItem) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>{text}</div>
          <div style={{ fontSize: '12px', color: '#666' }}>{record.description}</div>
        </div>
      ),
    },
    {
      title: 'Office Scope',
      dataIndex: 'office_scope',
      key: 'office_scope',
      render: (offices: string[]) => offices.join(', '),
    },
    {
      title: 'Updated',
      dataIndex: 'updated_at',
      key: 'updated_at',
      render: (date: string) => {
        if (!date) return '-';
        // Just return the raw date string for debugging
        return date;
      },
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 200,
      render: (_: any, record: ScenarioListItem) => (
        <Space>
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            size="small"
            onClick={() => handleRunSimulation(record.id)}
          >
            Run
          </Button>
          <Button
            icon={<EditOutlined />}
            size="small"
            onClick={() => navigate(`/scenario-builder/${record.id}`)}
          >
            Edit
          </Button>
          <Popconfirm
            title="Are you sure you want to delete this scenario?"
            onConfirm={() => handleDelete(record.id)}
            okText="Yes"
            cancelText="No"
          >
            <Button danger icon={<DeleteOutlined />} size="small">
              Delete
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Card>
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={2}>Scenarios</Title>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => navigate('/scenario-builder')}
          >
            Create New Scenario
          </Button>
        </div>
        
        <Table
          columns={columns}
          dataSource={scenarios}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
          }}
        />
      </Card>
    </div>
  );
};

export default SimpleScenarioList;