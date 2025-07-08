import React, { useState, useEffect } from 'react';
import { Menu, Typography, Button, Divider, Tag, Tooltip } from 'antd';
import type { MenuProps } from 'antd';
import { SettingOutlined, RocketOutlined, CheckCircleOutlined, ExclamationCircleOutlined, PlusOutlined, BarChartOutlined, EditOutlined } from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';
// @ts-ignore
import packageJson from '../../package.json';

const { Title, Text } = Typography;

const menuItems: MenuProps['items'] = [
  {
    key: '/system-config',
    icon: <SettingOutlined />,
    label: <Link to="/system-config">System Config</Link>,
  },
  {
    key: '/config',
    icon: <SettingOutlined />,
    label: <Link to="/config">Configuration</Link>,
  },
  {
    key: '/insights',
    icon: <BarChartOutlined />,
    label: <Link to="/insights">Insights</Link>,
  },
  {
    key: '/scenario-runner',
    icon: <RocketOutlined />,
    label: <Link to="/scenario-runner">Scenario Runner</Link>,
  },
  {
    key: '/scenario-editor',
    icon: <EditOutlined />,
    label: <Link to="/scenario-editor">Scenario Editor</Link>,
  },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <div style={{ height: '100vh', background: '#141414', padding: '16px' }}>
      <div style={{ marginBottom: '32px' }}>
        <Title level={4} style={{ color: '#fff', margin: 0 }}>
          SimpleSim
        </Title>
        <Text style={{ color: '#8c8c8c', fontSize: '12px' }}>
          v{packageJson.version}
        </Text>
      </div>

      <Menu
        mode="inline"
        selectedKeys={[location.pathname]}
        style={{ background: 'transparent', border: 'none' }}
        theme="dark"
        items={menuItems}
      />
      
      <Divider style={{ background: '#222', margin: '16px 0' }} />

      <Divider style={{ background: '#222', margin: '16px 0' }} />

      <div style={{ position: 'absolute', bottom: '16px', left: '16px', right: '16px' }}>
        <Text style={{ color: '#8c8c8c', fontSize: '11px', display: 'block', textAlign: 'center' }}>
          Organizational growth simulation platform
        </Text>
      </div>
    </div>
  );
} 