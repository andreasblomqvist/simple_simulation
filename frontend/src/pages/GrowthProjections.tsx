import React from 'react';
import { Card, Row, Col, Typography, Form, InputNumber, Select, Button } from 'antd';

const { Title, Text } = Typography;
const { Option } = Select;

export default function GrowthProjections() {
  return (
    <Card title={<Title level={4} style={{ margin: 0 }}>Growth Projections</Title>}>
      {/* Global Growth Rate Inputs */}
      <Card style={{ marginBottom: 24 }}>
        <Title level={5}>Global Growth Rate Inputs</Title>
        <Form layout="vertical">
          <Row gutter={16}>
            <Col xs={24} md={8}>
              <Form.Item label="New Office Growth Rate (%)">
                <InputNumber min={0} max={100} style={{ width: '100%' }} placeholder="e.g. 10" />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item label="Established Office Growth Rate (%)">
                <InputNumber min={0} max={100} style={{ width: '100%' }} placeholder="e.g. 5" />
              </Form.Item>
            </Col>
            <Col xs={24} md={8}>
              <Form.Item label="Mature Office Growth Rate (%)">
                <InputNumber min={0} max={100} style={{ width: '100%' }} placeholder="e.g. 2" />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Card>
      {/* Office-Specific Growth Rate Inputs */}
      <Card style={{ marginBottom: 24 }}>
        <Title level={5}>Office-Specific Growth Rate Inputs</Title>
        <Form layout="inline">
          <Form.Item>
            <Select style={{ width: 180 }} placeholder="Select Office">
              <Option value="">Select Office</Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <InputNumber min={0} max={100} style={{ width: 180 }} placeholder="Office growth rate (%)" />
          </Form.Item>
          <Form.Item>
            <Button type="primary">Apply</Button>
          </Form.Item>
        </Form>
      </Card>
      {/* Projection Charts and Tables */}
      <Row gutter={16}>
        <Col xs={24} md={12}>
          <Card style={{ height: 260, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#888' }}>
            [Projection Chart]
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card style={{ height: 260, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#888' }}>
            [Projection Table]
          </Card>
        </Col>
      </Row>
    </Card>
  );
} 