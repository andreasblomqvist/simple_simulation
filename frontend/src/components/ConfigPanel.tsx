import React from 'react';
import { Card, Typography } from 'antd';

const { Title, Text } = Typography;

export default function ConfigPanel() {
  return (
    <Card style={{ marginBottom: 24 }}>
      <Title level={4}>Simulation Configuration</Title>
      <Text type="secondary">[Configuration controls will go here]</Text>
    </Card>
  );
} 