import React from 'react';
import { Menu, Typography, Button, Divider } from 'antd';
import type { MenuProps } from 'antd';
import { HomeOutlined, ApartmentOutlined, SettingOutlined, BarChartOutlined, TeamOutlined, PlusOutlined, RocketOutlined } from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';
// @ts-ignore
import packageJson from '../../package.json';

const { Title, Text } = Typography;

const officeCategories = [
  {
    label: 'New Offices',
    offices: ['Office A', 'Office B'],
    icon: <TeamOutlined style={{ color: '#52c41a' }} />,
  },
  {
    label: 'Emerging Offices',
    offices: ['Office C'],
    icon: <TeamOutlined style={{ color: '#faad14' }} />,
  },
  {
    label: 'Established Offices',
    offices: ['Office D'],
    icon: <TeamOutlined style={{ color: '#bfbfbf' }} />,
  },
  {
    label: 'Mature Offices',
    offices: ['Office E'],
    icon: <TeamOutlined style={{ color: '#722ed1' }} />,
  },
];

const menuItems: MenuProps['items'] = [
  {
    key: 'dashboard',
    icon: <HomeOutlined />,
    label: <Link to="/">Dashboard</Link>,
    style: { display: 'none' },
  },
  {
    key: 'all-offices',
    icon: <ApartmentOutlined />,
    label: <Link to="/offices">All Offices</Link>,
    style: { display: 'none' },
  },
  {
    key: 'growth',
    icon: <BarChartOutlined />,
    label: <Link to="/growth">Growth Projections</Link>,
    style: { display: 'none' },
  },
  {
    key: 'seniority',
    icon: <TeamOutlined />,
    label: <Link to="/seniority">Seniority Analysis</Link>,
    style: { display: 'none' },
  },
  {
    key: 'config',
    icon: <SettingOutlined />,
    label: <Link to="/config">Configuration</Link>,
  },
  {
    key: 'lab',
    icon: <RocketOutlined />,
    label: <Link to="/lab">Simulation Lab</Link>,
  },

  {
    key: 'settings',
    icon: <SettingOutlined />,
    label: <Link to="/settings">Settings</Link>,
    style: { display: 'none' },
  },
  {
    key: 'offices-section',
    type: 'group',
    label: 'Offices',
    style: { display: 'none' },
    children: officeCategories.map(cat => ({
      key: cat.label,
      icon: cat.icon,
      label: cat.label,
      children: cat.offices.map(office => ({
        key: office,
        label: office,
      })),
    })),
  },
  {
    key: 'add-office',
    icon: <PlusOutlined />,
    label: 'Add Office',
    style: { display: 'none' },
  },
];

export default function Sidebar() {
  const location = useLocation();
  return (
    <>
      <Title level={4} style={{ color: '#fff', margin: 16 }}>Org Growth Sim</Title>
      <Button 
        type="primary" 
        icon={<PlusOutlined />} 
        block 
        style={{ marginBottom: 16, display: 'none' }}
      >
        Add Company
      </Button>
      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        style={{ borderRight: 0 }}
      />
      <Divider style={{ background: '#222', margin: '16px 0' }} />
      <div style={{ 
        padding: '0 16px 16px 16px', 
        textAlign: 'left' 
      }}>
        <Text 
          type="secondary" 
          style={{ 
            fontSize: '11px', 
            color: '#fff',
            opacity: 0.7 
          }}
        >
          Version: {packageJson.version}
        </Text>
      </div>
    </>
  );
} 