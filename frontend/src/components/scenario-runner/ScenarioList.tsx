import React, { useState, useEffect } from 'react';
import { Button, Typography, Space, Popconfirm, message, Spin, Empty, Table } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined, BarChartOutlined, ExportOutlined } from '@ant-design/icons';
import type { ScenarioListItem, ScenarioId } from '../../types/scenarios';
import { scenarioApi } from '../../services/scenarioApi';
import { useNavigate } from 'react-router-dom';

const { Title, Paragraph, Text } = Typography;

interface ScenarioListProps {
  onNext: () => void;
  onEdit?: (id: ScenarioId) => void;
  onDelete?: (id: ScenarioId) => void;
  onCompare?: () => void;
  onExport?: () => void;
  onView?: (id: ScenarioId) => void;
  hideHeader?: boolean;
  scenarios: ScenarioListItem[];
  setScenarios: React.Dispatch<React.SetStateAction<ScenarioListItem[]>>;
}

const ScenarioList: React.FC<ScenarioListProps> = ({ onNext, onEdit, onDelete, onCompare, onExport, onView, hideHeader, scenarios, setScenarios }) => {
  const [loading, setLoading] = useState(true);
  const [selectedScenarios, setSelectedScenarios] = useState<ScenarioId[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    loadScenarios();
  }, []);

  const loadScenarios = async () => {
    try {
      setLoading(true);
      const scenarioList = await scenarioApi.listScenarios();
      setScenarios(scenarioList);
    } catch (error) {
      message.error('Failed to load scenarios: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (scenarioId: ScenarioId) => {
    try {
      await scenarioApi.deleteScenario(scenarioId);
      message.success('Scenario deleted successfully');
      loadScenarios(); // Reload the list
    } catch (error) {
      message.error('Failed to delete scenario: ' + (error as Error).message);
    }
  };

  const handleExport = async (scenarioId: ScenarioId) => {
    try {
      const blob = await scenarioApi.exportScenarioResults(scenarioId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `scenario-${scenarioId}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      message.success('Scenario exported successfully');
    } catch (error) {
      message.error('Failed to export scenario: ' + (error as Error).message);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>Loading scenarios...</div>
      </div>
    );
  }

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: ScenarioListItem) => (
        <Text strong>{text}</Text>
      ),
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      render: (text: string) => text || <Text type="secondary">No description</Text>,
    },
    {
      title: 'Scope',
      dataIndex: 'office_scope',
      key: 'office_scope',
      render: (scope: string[] | undefined) =>
        Array.isArray(scope)
          ? (scope.includes('Group') ? 'Group' : scope.join(', '))
          : '',
    },
    {
      title: 'Duration',
      dataIndex: 'time_range',
      key: 'time_range',
      render: (tr: any) => tr ? `${tr.start_year}-${String(tr.start_month).padStart(2, '0')} to ${tr.end_year}-${String(tr.end_month).padStart(2, '0')}` : '',
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => formatDate(date),
    },
    {
      title: 'Updated',
      dataIndex: 'updated_at',
      key: 'updated_at',
      render: (date: string) => formatDate(date),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, item: ScenarioListItem) => (
        <Space>
          <Button 
            key="view" 
            icon={<EyeOutlined />}
            onClick={() => navigate(`/scenario-runner/${item.id}`)}
          >
            View
          </Button>
          <Button 
            key="edit" 
            type="link" 
            icon={<EditOutlined />}
            onClick={() => onEdit && onEdit(item.id)}
          >
            Edit
          </Button>
          <Button 
            key="export" 
            type="link" 
            icon={<ExportOutlined />}
            onClick={() => handleExport(item.id)}
          >
            Export
          </Button>
          <Popconfirm
            key="delete"
            title="Delete this scenario?"
            description="This action cannot be undone."
            onConfirm={() => handleDelete(item.id)}
            okText="Yes"
            cancelText="No"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              Delete
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ marginLeft: 24, marginRight: 24 }}>
      {!hideHeader && (
        <>
          <Title level={4} style={{ margin: 0 }}>Scenario Runner</Title>
          <Paragraph>
            Create and compare different organizational growth scenarios to make informed decisions about your growth strategy.
          </Paragraph>
        </>
      )}
      {scenarios.length === 0 ? (
        <Empty
          description="No scenarios found"
          style={{ margin: '40px 0' }}
        >
          <Button type="primary" icon={<PlusOutlined />} onClick={onNext}>
            Create Your First Scenario
          </Button>
        </Empty>
      ) : (
        <Table
          dataSource={scenarios}
          columns={columns}
          rowKey="id"
          pagination={false}
          bordered
          size="middle"
          style={{ marginBottom: 24 }}
        />
      )}
      <Space style={{ marginBottom: 16 }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={onNext}>
          Create New Scenario
        </Button>
        <Button 
          icon={<BarChartOutlined />} 
          onClick={onCompare}
          disabled={selectedScenarios.length < 2}
        >
          Compare Scenarios
        </Button>
      </Space>
    </div>
  );
};

export default ScenarioList; 