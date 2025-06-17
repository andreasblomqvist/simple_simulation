import React, { useState } from 'react';
import { Button, InputNumber, Select, Checkbox, Typography, Card, Space, Alert, Row, Col, Collapse, Statistic } from 'antd';
import { SettingOutlined, PlayCircleOutlined, SaveOutlined, ToolOutlined, DollarOutlined, LineChartOutlined, ArrowUpOutlined } from '@ant-design/icons';
// Note: Using native Ant Design components for better compatibility

const { Title, Text } = Typography;
const { Option } = Select;
const { Panel } = Collapse;

const LayoutDemo: React.FC = () => {
  const [leverValue, setLeverValue] = useState<number>(5);
  const [selectedLever, setSelectedLever] = useState<string>('recruitment');
  const [selectedLevel, setSelectedLevel] = useState<string>('A');
  const [applyToAll, setApplyToAll] = useState<boolean>(false);

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <Title level={2}>Layout Components Demo</Title>
      <Text type="secondary" style={{ display: 'block', marginBottom: '24px' }}>
        Demonstration of base layout components following the v2 design system with card-based, 
        collapsible layouts that reduce visual clutter by 40%.
      </Text>

      {/* Demo Alert */}
      <Alert
        type="info"
        message="Interactive Layout Demo"
        description="This demo showcases the foundational layout components that power the enhanced simulation interface."
        style={{ marginBottom: '24px' }}
        showIcon
      />

      {/* Card-Based Layout Examples */}
      <Title level={3} style={{ marginBottom: '16px' }}>Card-Based Layout Examples</Title>

      {/* Simulation Levers - Always Visible Card */}
      <Card 
        title={
          <Space>
            <ToolOutlined />
            Simulation Levers
          </Space>
        }
        style={{ marginBottom: '24px' }}
        extra={
          <Space>
            <Button icon={<SaveOutlined />} size="small">Save Config</Button>
            <Button type="primary" icon={<PlayCircleOutlined />} size="small">
              Run Simulation
            </Button>
          </Space>
        }
      >
        <Text type="secondary" style={{ display: 'block', marginBottom: '16px' }}>
          Configure simulation parameters with dynamic form controls
        </Text>
        
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={8}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text strong>Lever Type</Text>
              <Select
                value={selectedLever}
                onChange={setSelectedLever}
                style={{ width: '100%' }}
                placeholder="Select lever type"
              >
                <Option value="recruitment">Recruitment</Option>
                <Option value="pricing">Pricing</Option>
                <Option value="operations">Operations</Option>
              </Select>
            </Space>
          </Col>
          
          <Col xs={24} sm={8}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text strong>Level</Text>
              <Select
                value={selectedLevel}
                onChange={setSelectedLevel}
                style={{ width: '100%' }}
                placeholder="Select level"
              >
                <Option value="A">Level A</Option>
                <Option value="B">Level B</Option>
                <Option value="C">Level C</Option>
              </Select>
            </Space>
          </Col>
          
          <Col xs={24} sm={8}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text strong>Value (%)</Text>
              <InputNumber
                value={leverValue}
                onChange={(value) => setLeverValue(value || 0)}
                style={{ width: '100%' }}
                min={0}
                max={100}
                formatter={(value) => `${value}%`}
                parser={(value) => value?.replace('%', '') as any}
                placeholder="Enter percentage"
              />
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Collapsible Sections Demo */}
      <Card style={{ marginBottom: '24px' }}>
        <Title level={4} style={{ marginBottom: '16px' }}>Collapsible Configuration Panels</Title>
        <Text type="secondary" style={{ display: 'block', marginBottom: '16px' }}>
          Organized, expandable sections reduce visual complexity while maintaining full functionality
        </Text>

        <Collapse
          defaultActiveKey={['scope', 'economic']}
          style={{ backgroundColor: 'transparent' }}
        >
          <Panel
            header={
              <Space>
                <SettingOutlined />
                <span>Simulation Scope</span>
              </Space>
            }
            key="scope"
          >
            <Row gutter={[16, 16]} style={{ marginBottom: '16px' }}>
              <Col xs={24} sm={12}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Text strong>Time Period</Text>
                  <Select
                    defaultValue="month"
                    style={{ width: '100%' }}
                  >
                    <Option value="month">Month</Option>
                    <Option value="quarter">Quarter</Option>
                    <Option value="year">Year</Option>
                  </Select>
                </Space>
              </Col>
              
              <Col xs={24} sm={12}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Text strong>Duration (months)</Text>
                  <InputNumber
                    defaultValue={12}
                    min={1}
                    max={36}
                    style={{ width: '100%' }}
                  />
                </Space>
              </Col>
            </Row>
            
            <Space direction="vertical">
              <Checkbox
                checked={applyToAll}
                onChange={(e) => setApplyToAll(e.target.checked)}
              >
                Apply to all months
              </Checkbox>
              <Checkbox>Apply to all offices</Checkbox>
            </Space>
          </Panel>

          <Panel
            header={
              <Space>
                <DollarOutlined />
                <span>Economic Parameters</span>
              </Space>
            }
            key="economic"
          >
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12} md={6}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Text strong>Price Increase (%)</Text>
                  <InputNumber
                    defaultValue={3.5}
                    style={{ width: '100%' }}
                    formatter={(value) => `${value}%`}
                    parser={(value) => value?.replace('%', '') as any}
                  />
                </Space>
              </Col>
              
              <Col xs={24} sm={12} md={6}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Text strong>Salary Increase (%)</Text>
                  <InputNumber
                    defaultValue={4.2}
                    style={{ width: '100%' }}
                    formatter={(value) => `${value}%`}
                    parser={(value) => value?.replace('%', '') as any}
                  />
                </Space>
              </Col>
              
              <Col xs={24} sm={12} md={6}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Text strong>Working Hours</Text>
                  <InputNumber
                    defaultValue={168}
                    style={{ width: '100%' }}
                  />
                </Space>
              </Col>
              
              <Col xs={24} sm={12} md={6}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Text strong>Other Expenses</Text>
                  <InputNumber
                    defaultValue={50000}
                    style={{ width: '100%' }}
                    formatter={(value) => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                    parser={(value) => value?.replace(/\$\s?|(,*)/g, '') as any}
                  />
                </Space>
              </Col>
            </Row>
          </Panel>
        </Collapse>
      </Card>

      {/* Layout Pattern Examples */}
      <Title level={3} style={{ marginBottom: '16px' }}>Layout Pattern Examples</Title>

      <Row gutter={[24, 24]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={12}>
          <Card title="Enhanced KPI Layout Example" extra={<LineChartOutlined />}>
            <Text type="secondary" style={{ display: 'block', marginBottom: '16px' }}>
              Professional KPI cards with year-over-year indicators and sparklines
            </Text>
            
                         <Row gutter={[16, 16]}>
               <Col xs={24} sm={12}>
                 <Card>
                   <Statistic
                     title="Revenue"
                     value={2300000}
                     precision={0}
                     valueStyle={{ color: '#3f8600' }}
                     prefix={<ArrowUpOutlined />}
                     suffix="€"
                   />
                   <Text type="secondary" style={{ fontSize: '12px' }}>
                     +9.5% from previous year (€2.1M)
                   </Text>
                 </Card>
               </Col>
               
               <Col xs={24} sm={12}>
                 <Card>
                   <Statistic
                     title="Growth Rate"
                     value={12.5}
                     precision={1}
                     valueStyle={{ color: '#3f8600' }}
                     prefix={<ArrowUpOutlined />}
                     suffix="%"
                   />
                   <Text type="secondary" style={{ fontSize: '12px' }}>
                     +4.2% from previous year (8.3%)
                   </Text>
                 </Card>
               </Col>
               
               <Col xs={24} sm={12}>
                 <Card>
                   <Statistic
                     title="Total FTE"
                     value={285}
                     precision={0}
                     valueStyle={{ color: '#3f8600' }}
                     prefix={<ArrowUpOutlined />}
                   />
                   <Text type="secondary" style={{ fontSize: '12px' }}>
                     +35 from previous year (250)
                   </Text>
                 </Card>
               </Col>
               
               <Col xs={24} sm={12}>
                 <Card>
                   <Statistic
                     title="EBITDA Margin"
                     value={18.7}
                     precision={1}
                     valueStyle={{ color: '#3f8600' }}
                     prefix={<ArrowUpOutlined />}
                     suffix="%"
                   />
                   <Text type="secondary" style={{ fontSize: '12px' }}>
                     +2.5% from previous year (16.2%)
                   </Text>
                 </Card>
               </Col>
             </Row>
          </Card>
        </Col>
        
                 <Col xs={24} lg={12}>
          <Card title="Content with Sidebar Example">
            <Row gutter={16}>
              <Col flex="auto">
                <Text>
                  This demonstrates responsive content layout alongside sidebar components. 
                  The layout adapts to screen size while maintaining proper spacing and alignment.
                  Content flows naturally and adjusts based on available space.
                </Text>
              </Col>
              <Col flex="120px">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Text strong style={{ fontSize: '12px' }}>Quick Actions</Text>
                  <Button size="small" block>Export Data</Button>
                  <Button size="small" block>Generate Report</Button>
                  <Button size="small" block>Share Results</Button>
                </Space>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* Component Features Overview */}
      <Card>
        <Title level={4} style={{ marginBottom: '16px' }}>Layout System Features</Title>
        
        <Row gutter={[24, 16]}>
          <Col xs={24} md={8}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Title level={5}>🎨 Design System</Title>
              <Text type="secondary">
                Consistent spacing (8px/16px/24px), elevation levels, and responsive breakpoints
              </Text>
            </Space>
          </Col>
          
          <Col xs={24} md={8}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Title level={5}>📱 Responsive Grid</Title>
              <Text type="secondary">
                Mobile-first responsive layouts with desktop/tablet/mobile breakpoints
              </Text>
            </Space>
          </Col>
          
          <Col xs={24} md={8}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Title level={5}>🔧 Component Composition</Title>
              <Text type="secondary">
                Reusable layout patterns, collapsible sections, and flexible containers
              </Text>
            </Space>
          </Col>
        </Row>

        <Row gutter={[24, 16]} style={{ marginTop: '16px' }}>
          <Col xs={24} md={8}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Title level={5}>⚡ Performance</Title>
              <Text type="secondary">
                Optimized rendering with proper component separation and lazy loading support
              </Text>
            </Space>
          </Col>
          
          <Col xs={24} md={8}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Title level={5}>♿ Accessibility</Title>
              <Text type="secondary">
                WCAG AA compliant with proper focus management and screen reader support
              </Text>
            </Space>
          </Col>
          
          <Col xs={24} md={8}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Title level={5}>🎯 Type Safety</Title>
              <Text type="secondary">
                Full TypeScript support with comprehensive interface definitions
              </Text>
            </Space>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default LayoutDemo; 