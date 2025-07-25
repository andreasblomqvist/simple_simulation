/**
 * Simulation Lab page
 */
import React from 'react';
import { Card, Typography, Button } from 'antd';
import { ExperimentOutlined, PlayCircleOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

export const SimulationLab: React.FC = () => {
  return (
    <Card 
      title={
        <Title level={4} style={{ margin: 0 }}>
          <ExperimentOutlined style={{ marginRight: 8 }} />
          Simulation Lab
        </Title>
      }
    >
      <div style={{ textAlign: 'center', padding: '60px 20px' }}>
        <ExperimentOutlined style={{ fontSize: '64px', color: '#52c41a', marginBottom: '16px' }} />
        <Title level={3}>Simulation Laboratory</Title>
        <Text type="secondary">
          Run simulations and experiments to test different scenarios and analyze their outcomes.
        </Text>
        <div style={{ marginTop: '24px' }}>
          <Button type="primary" size="large" icon={<PlayCircleOutlined />}>
            Start Simulation
          </Button>
        </div>
      </div>
    </Card>
  );
};