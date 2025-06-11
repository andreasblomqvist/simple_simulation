import React from 'react';
import { Card, Row, Col, Typography, Form, Input } from 'antd';

const { Title, Text } = Typography;

export default function SeniorityAnalysis() {
  return (
    <Card title={<Title level={4} style={{ margin: 0 }}>Seniority Analysis</Title>}>
      {/* Seniority Distribution Chart */}
      <Card style={{ marginBottom: 24, height: 180, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#888' }}>
        [Seniority Distribution Chart]
      </Card>
      {/* Seniority Breakdown Table */}
      <Card style={{ marginBottom: 24 }}>
        <Title level={5}>Seniority Breakdown Table</Title>
        <Text type="secondary">[Seniority breakdown table here]</Text>
      </Card>
      {/* Scenario Controls */}
      <Card>
        <Title level={5}>Scenario Controls</Title>
        <Form layout="inline">
          <Form.Item>
            <Input placeholder="Target Spreads" style={{ width: 180 }} />
          </Form.Item>
          <Form.Item>
            <Input placeholder="Timelines" style={{ width: 180 }} />
          </Form.Item>
        </Form>
      </Card>
    </Card>
  );
} 