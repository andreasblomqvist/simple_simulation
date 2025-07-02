import React from 'react';
import { Button, List, Typography, Space, Popconfirm } from 'antd';

const { Title, Paragraph, Text } = Typography;

// Mock scenario data
const mockScenarios = [
  {
    id: 1,
    name: 'Oslo Growth Plan',
    created: '2025-07-01',
    description: 'Aggressive expansion strategy for Oslo office',
  },
  {
    id: 2,
    name: 'Stockholm Expansion',
    created: '2025-06-15',
    description: 'Steady growth for Stockholm',
  },
  {
    id: 3,
    name: 'Munich Conservative',
    created: '2025-06-10',
    description: 'Conservative scenario for Munich',
  },
];

interface ScenarioListProps {
  onNext: () => void;
  onEdit?: (id: number) => void;
  onDelete?: (id: number) => void;
  onCompare?: () => void;
  onExport?: () => void;
  onView?: (id: number) => void;
}

const ScenarioList: React.FC<ScenarioListProps> = ({ onNext, onEdit, onDelete, onCompare, onExport, onView }) => {
  return (
    <div style={{ marginLeft: 24, marginRight: 24 }}>
      <Title level={4} style={{ margin: 0 }}>Scenario Runner</Title>
      <Paragraph>
        Create and compare different organizational growth scenarios to make informed decisions about your growth strategy.
      </Paragraph>
      <List
        itemLayout="horizontal"
        dataSource={mockScenarios}
        style={{ marginBottom: 24 }}
        renderItem={item => (
          <List.Item
            actions={[
              <Button key="view" onClick={() => onView && onView(item.id)}>View</Button>,
              <Button key="edit" type="link" onClick={() => onEdit && onEdit(item.id)}>Edit</Button>,
              <Popconfirm
                key="delete"
                title="Delete this scenario?"
                onConfirm={() => onDelete && onDelete(item.id)}
                okText="Yes"
                cancelText="No"
              >
                <Button type="link" danger>Delete</Button>
              </Popconfirm>,
            ]}
          >
            <List.Item.Meta
              title={<Text strong>{item.name}</Text>}
              description={<>
                <Text type="secondary">Created: {item.created}</Text><br />
                <Text>{item.description}</Text>
              </>}
            />
          </List.Item>
        )}
      />
      <Space style={{ marginBottom: 16 }}>
        <Button type="primary" onClick={onNext}>Create New Scenario</Button>
        <Button onClick={onCompare}>Compare Scenarios</Button>
        <Button onClick={onExport}>Export Results</Button>
      </Space>
    </div>
  );
};

export default ScenarioList; 