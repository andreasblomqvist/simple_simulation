import React from 'react';
import { Layout as AntLayout } from 'antd';
import Sidebar from './Sidebar';

const { Sider, Content } = AntLayout;

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider width={280} theme="dark">
        <Sidebar />
      </Sider>
      <AntLayout>
        <Content style={{ margin: 0, padding: 24, minHeight: 280 }}>
          {children}
        </Content>
      </AntLayout>
    </AntLayout>
  );
} 