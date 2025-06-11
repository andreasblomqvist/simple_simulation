import React from 'react';
import { Menu, Typography, Button, Divider } from 'antd';
import { HomeOutlined, ApartmentOutlined, SettingOutlined, BarChartOutlined, ExperimentOutlined, TeamOutlined, PlusOutlined } from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';

const { Title } = Typography;

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

const menuItems = [
  {
    key: 'dashboard',
    icon: <HomeOutlined />,
    label: <Link to="/">Dashboard</Link>,
  },
  {
    key: 'all-offices',
    icon: <ApartmentOutlined />,
    label: <Link to="/offices">All Offices</Link>,
  },
  {
    key: 'growth',
    icon: <BarChartOutlined />,
    label: <Link to="/growth">Growth Projections</Link>,
  },
  {
    key: 'seniority',
    icon: <TeamOutlined />,
    label: <Link to="/seniority">Seniority Analysis</Link>,
  },
  {
    key: 'config',
    icon: <SettingOutlined />,
    label: <Link to="/config">Configuration</Link>,
  },
  {
    key: 'lab',
    icon: <ExperimentOutlined />,
    label: <Link to="/lab">Simulation Lab</Link>,
  },
  {
    key: 'settings',
    icon: <SettingOutlined />,
    label: <Link to="/settings">Settings</Link>,
  },
  {
    key: 'offices-section',
    type: 'group',
    label: 'Offices',
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
  },
];

export default function Sidebar() {
  const location = useLocation();
  return (
    <>
      <Title level={4} style={{ color: '#fff', margin: 16 }}>Org Growth Sim</Title>
      <Button type="primary" icon={<PlusOutlined />} block style={{ marginBottom: 16 }}>
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
    </>
  );
} 