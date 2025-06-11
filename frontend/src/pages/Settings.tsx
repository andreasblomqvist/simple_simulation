import React from 'react';
import { Card, Row, Col, Typography, Form, Input, Button, Switch } from 'antd';
import { useTheme } from '../components/ThemeContext';

const { Title, Text } = Typography;

export default function Settings() {
  const { darkMode, setDarkMode } = useTheme();

  return (
    <Card title={<Title level={4} style={{ margin: 0 }}>Settings</Title>}>
      {/* Theme Switcher */}
      <Card style={{ marginBottom: 24 }}>
        <Row align="middle" gutter={16}>
          <Col><Text strong>Theme</Text></Col>
          <Col>
            <Switch
              checked={darkMode}
              checkedChildren="Dark"
              unCheckedChildren="Light"
              onChange={setDarkMode}
            />
          </Col>
        </Row>
      </Card>
      {/* API/Backend Config */}
      <Card style={{ marginBottom: 24 }}>
        <Title level={5}>API/Backend Config</Title>
        <Form layout="vertical">
          <Form.Item label="API URL">
            <Input placeholder="API URL" />
          </Form.Item>
        </Form>
      </Card>
      {/* User Preferences */}
      <Card>
        <Title level={5}>User Preferences</Title>
        <Text type="secondary">[User preferences UI here]</Text>
      </Card>
    </Card>
  );
} 