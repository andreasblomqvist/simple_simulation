/**
 * Application settings page
 */
import React from 'react';
import { Card, Typography, Button, Row, Col, Switch, Select } from 'antd';
import { SettingOutlined, SaveOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;
const { Option } = Select;

export const Settings: React.FC = () => {
  return (
    <Card 
      title={
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Title level={4} style={{ margin: 0 }}>
            <SettingOutlined style={{ marginRight: 8 }} />
            Settings
          </Title>
          <Button type="primary" icon={<SaveOutlined />}>
            Save Settings
          </Button>
        </div>
      }
    >
      <Row gutter={[24, 24]}>
        <Col span={12}>
          <Card size="small" title="General Settings">
            <div style={{ marginBottom: '16px' }}>
              <Text strong>Default Currency</Text>
              <Select defaultValue="SEK" style={{ width: '100%', marginTop: '8px' }}>
                <Option value="SEK">Swedish Krona (SEK)</Option>
                <Option value="EUR">Euro (EUR)</Option>
                <Option value="USD">US Dollar (USD)</Option>
              </Select>
            </div>
            
            <div style={{ marginBottom: '16px' }}>
              <Text strong>Default Timezone</Text>
              <Select defaultValue="Europe/Stockholm" style={{ width: '100%', marginTop: '8px' }}>
                <Option value="Europe/Stockholm">Stockholm</Option>
                <Option value="Europe/Oslo">Oslo</Option>
                <Option value="Europe/Helsinki">Helsinki</Option>
              </Select>
            </div>
          </Card>
        </Col>
        
        <Col span={12}>
          <Card size="small" title="Simulation Settings">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <Text strong>Auto-save scenarios</Text>
              <Switch defaultChecked />
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <Text strong>Enable debug logging</Text>
              <Switch />
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <Text strong>Dark mode</Text>
              <Switch />
            </div>
          </Card>
        </Col>
      </Row>
    </Card>
  );
};