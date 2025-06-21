import React, { useState, useEffect } from 'react';
import { Menu, Typography, Button, Divider, Tag, Tooltip } from 'antd';
import type { MenuProps } from 'antd';
import { SettingOutlined, RocketOutlined, CheckCircleOutlined, ExclamationCircleOutlined, PlusOutlined } from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';
// @ts-ignore
import packageJson from '../../package.json';

const { Title, Text } = Typography;

const menuItems: MenuProps['items'] = [
  {
    key: '/config',
    icon: <SettingOutlined />,
    label: <Link to="/config">Configuration</Link>,
  },
  {
    key: '/lab',
    icon: <RocketOutlined />,
    label: <Link to="/lab">Simulation Lab</Link>,
  },
];

export default function Sidebar() {
  const location = useLocation();
  const [configStatus, setConfigStatus] = useState<{
    checksum: string;
    status: string;
    summary?: any;
  } | null>(null);
  const [loading, setLoading] = useState(false);

  // Fetch configuration status
  const fetchConfigStatus = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/simulation/config/validation');
      if (response.ok) {
        const data = await response.json();
        setConfigStatus({
          checksum: data.checksum,
          status: data.status,
          summary: data.summary
        });
      } else {
        console.error('Failed to fetch config status');
      }
    } catch (error) {
      console.error('Error fetching config status:', error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch config status on mount and set up polling
  useEffect(() => {
    fetchConfigStatus();
    
    // Poll every 10 seconds for updates
    const interval = setInterval(fetchConfigStatus, 10000);
    
    return () => clearInterval(interval);
  }, []);

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
      
      {/* Configuration Status */}
      <div style={{ marginBottom: '16px' }}>
        <Text style={{ color: '#8c8c8c', fontSize: '12px', display: 'block', marginBottom: '8px' }}>
          Configuration Status
        </Text>
        
        {loading ? (
          <div style={{ padding: '8px', background: '#1f1f1f', borderRadius: '4px' }}>
            <Text style={{ color: '#8c8c8c', fontSize: '11px' }}>Loading...</Text>
          </div>
        ) : configStatus ? (
          <div style={{ padding: '8px', background: '#1f1f1f', borderRadius: '4px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
              {configStatus.status === 'complete' ? (
                <CheckCircleOutlined style={{ color: '#52c41a', fontSize: '12px' }} />
              ) : (
                <ExclamationCircleOutlined style={{ color: '#faad14', fontSize: '12px' }} />
              )}
              <Text style={{ color: '#fff', fontSize: '11px', fontFamily: 'monospace' }}>
                {configStatus.checksum}
              </Text>
            </div>
            
            {configStatus.summary && (
              <div style={{ fontSize: '10px', color: '#8c8c8c' }}>
                <div>{configStatus.summary.total_offices} offices • {configStatus.summary.total_fte} FTE</div>
                {configStatus.summary.missing_data_count > 0 && (
                  <div style={{ color: '#faad14' }}>
                    ⚠️ {configStatus.summary.missing_data_count} missing rates
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          <div style={{ padding: '8px', background: '#1f1f1f', borderRadius: '4px' }}>
            <Text style={{ color: '#ff4d4f', fontSize: '11px' }}>Failed to load</Text>
          </div>
        )}
        
        <Button 
          type="text" 
          size="small" 
          onClick={fetchConfigStatus}
          style={{ 
            color: '#8c8c8c', 
            fontSize: '10px', 
            height: 'auto', 
            padding: '2px 0',
            marginTop: '4px'
          }}
        >
          Refresh
        </Button>
      </div>

      <Divider style={{ background: '#222', margin: '16px 0' }} />

      <div style={{ position: 'absolute', bottom: '16px', left: '16px', right: '16px' }}>
        <Text style={{ color: '#8c8c8c', fontSize: '11px', display: 'block', textAlign: 'center' }}>
          Organizational growth simulation platform
        </Text>
      </div>
    </div>
  );
} 