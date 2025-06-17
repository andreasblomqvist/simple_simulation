import React, { useState, useCallback } from 'react';
import { Card, Select, InputNumber, Row, Col, Typography, Button, Space, Tooltip, Form, Alert, Checkbox, Divider } from 'antd';
import { InfoCircleOutlined, ExperimentOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;
const { Option } = Select;

// Types for lever configuration
interface LeverConfig {
  lever: string | null;
  level: string | null;
  value: number;
  timePeriod: 'monthly' | 'half-year' | 'yearly';
  month: number;
  applyToAllMonths: boolean;
  applyToAllOffices: boolean;
  selectedOffices: string[];
  selectedOfficeJourney: string;
}

interface SimulationLeversCardProps {
  onApply: (config: LeverConfig) => void;
  onReset: () => void;
  loading?: boolean;
  className?: string;
  lastAppliedSummary?: string[] | null;
}

// Lever definitions with help text
const LEVERS = [
  { 
    key: 'recruitment', 
    label: 'Recruitment Rate', 
    description: 'Monthly recruitment rate as percentage of current headcount',
    defaultValue: 2.5,
    unit: '%',
    range: [0, 10]
  },
  { 
    key: 'churn', 
    label: 'Churn Rate', 
    description: 'Monthly churn rate as percentage of current headcount',
    defaultValue: 1.4,
    unit: '%',
    range: [0, 5]
  },
  { 
    key: 'progression', 
    label: 'Progression Rate', 
    description: 'Percentage of people promoted (typically applied in May/November)',
    defaultValue: 8.0,
    unit: '%',
    range: [0, 20]
  },
  { 
    key: 'utr', 
    label: 'Utilization Rate', 
    description: 'Utilization rate for consultants (billable time ratio)',
    defaultValue: 90,
    unit: '%',
    range: [50, 100]
  },
];

// Level definitions by lever type
const LEVELS_BY_LEVER = {
  recruitment: ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"],
  churn: ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"],
  progression: ["A", "AC", "C", "SrC", "AM", "M", "SrM"], // PiP excluded
  utr: ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"],
};

const MONTHS = [
  { value: 1, label: 'January' },
  { value: 2, label: 'February' },
  { value: 3, label: 'March' },
  { value: 4, label: 'April' },
  { value: 5, label: 'May' },
  { value: 6, label: 'June' },
  { value: 7, label: 'July' },
  { value: 8, label: 'August' },
  { value: 9, label: 'September' },
  { value: 10, label: 'October' },
  { value: 11, label: 'November' },
  { value: 12, label: 'December' }
];

const TIME_PERIODS = [
  { value: 'monthly', label: 'Monthly', description: 'Apply to specific month(s)' },
  { value: 'half-year', label: 'Half Year', description: 'Apply to 6-month period' },
  { value: 'yearly', label: 'Yearly', description: 'Apply to entire year' }
];

const OFFICE_JOURNEYS = [
  { value: 'New Office', label: 'New Office (0-24 FTE)' },
  { value: 'Emerging Office', label: 'Emerging Office (25-199 FTE)' },
  { value: 'Established Office', label: 'Established Office (200-499 FTE)' },
  { value: 'Mature Office', label: 'Mature Office (500+ FTE)' }
];

// Helper to convert yearly/half-year rates to monthly
const convertToMonthlyRate = (value: number, timePeriod: string): number => {
  const rate = value / 100; // Convert percentage to decimal
  
  if (timePeriod === 'yearly') {
    // Convert yearly cumulative to monthly rate
    return 1 - Math.pow(1 - rate, 1 / 12);
  } else if (timePeriod === 'half-year') {
    // Convert half-year cumulative to monthly rate
    return 1 - Math.pow(1 - rate, 1 / 6);
  }
  
  return rate; // Already monthly
};

/**
 * SimulationLeversCard Component
 * 
 * Provides simplified lever configuration with:
 * - Dynamic level selection based on chosen lever
 * - Time period selection (monthly/half-year/yearly)
 * - Office and journey-based targeting
 * - Contextual help and validation
 * - Real-time calculation of effective rates
 */
export const SimulationLeversCard: React.FC<SimulationLeversCardProps> = ({
  onApply,
  onReset,
  loading = false,
  className = '',
  lastAppliedSummary
}) => {
  const [form] = Form.useForm();
  const [config, setConfig] = useState<LeverConfig>({
    lever: null,
    level: null,
    value: 2.5,
    timePeriod: 'monthly',
    month: 1,
    applyToAllMonths: false,
    applyToAllOffices: true,
    selectedOffices: [],
    selectedOfficeJourney: ''
  });

  // Get current lever definition
  const currentLever = LEVERS.find(l => l.key === config.lever);
  const availableLevels = config.lever ? LEVELS_BY_LEVER[config.lever as keyof typeof LEVELS_BY_LEVER] || [] : [];

  // Calculate effective monthly rate for display
  const effectiveMonthlyRate = convertToMonthlyRate(config.value, config.timePeriod);
  const effectiveMonthlyPercent = (effectiveMonthlyRate * 100).toFixed(2);

  // Handle lever selection with smart defaults
  const handleLeverChange = useCallback((leverKey: string) => {
    const lever = LEVERS.find(l => l.key === leverKey);
    
    // Smart defaults based on lever type
    let smartDefaults = {
      lever: leverKey,
      level: null, // Will be set below
      value: lever?.defaultValue || 2.5,
      timePeriod: 'monthly' as 'monthly' | 'half-year' | 'yearly',
      month: 1,
      applyToAllMonths: false,
      applyToAllOffices: true,
      selectedOfficeJourney: '',
      selectedOffices: []
    };

    // Lever-specific smart defaults
    switch (leverKey) {
      case 'recruitment':
        smartDefaults = {
          ...smartDefaults,
          timePeriod: 'monthly',
          applyToAllMonths: true, // Recruitment often applied across time
          applyToAllOffices: false, // Usually targeted by office type
          selectedOfficeJourney: 'New Office' // Default to new offices needing growth
        };
        break;
        
      case 'churn':
        smartDefaults = {
          ...smartDefaults,
          timePeriod: 'monthly',
          applyToAllMonths: false, // Churn spikes often seasonal
          month: 1, // January often high churn
          applyToAllOffices: true // Churn often company-wide
        };
        break;
        
      case 'progression':
        smartDefaults = {
          ...smartDefaults,
          timePeriod: 'monthly',
          applyToAllMonths: false,
          month: 5, // May is typical promotion cycle
          applyToAllOffices: true // Promotions typically company-wide
        };
        break;
        
      case 'utr':
        smartDefaults = {
          ...smartDefaults,
          timePeriod: 'yearly', // UTR often set as annual targets
          applyToAllOffices: false,
          selectedOfficeJourney: 'Established Office' // Focus on established offices
        };
        break;
    }

    setConfig(prev => ({
      ...prev,
      ...smartDefaults
    }));
    
    form.setFieldsValue({ 
      level: null, 
      value: lever?.defaultValue || 2.5,
      timePeriod: smartDefaults.timePeriod
    });
  }, [form]);

  // Handle form value changes
  const handleValueChange = useCallback((field: string, value: any) => {
    setConfig(prev => ({ ...prev, [field]: value }));
  }, []);

  // Handle apply action
  const handleApply = useCallback(() => {
    form.validateFields().then(() => {
      onApply(config);
    }).catch(console.error);
  }, [config, form, onApply]);

  // Validation rules
  const getValidationRules = (lever: any) => {
    if (!lever) return [];
    
    return [
      { required: true, message: 'Please enter a value' },
      { 
        type: 'number' as const, 
        min: lever.range[0], 
        max: lever.range[1], 
        message: `Value must be between ${lever.range[0]} and ${lever.range[1]}` 
      }
    ];
  };

  return (
    <Card 
      className={`simulation-levers-card ${className}`}
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ExperimentOutlined />
          <Title level={4} style={{ margin: 0 }}>Simulation Levers</Title>
        </div>
      }
      style={{ marginBottom: '24px' }}
    >
      <Form form={form} layout="vertical" size="middle">
        {/* Main Lever Configuration */}
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={8} md={8}>
            <Form.Item 
              label="Lever Type" 
              name="lever"
              rules={[{ required: true, message: 'Please select a lever' }]}
            >
              <Select
                placeholder="Choose a lever to modify"
                onChange={handleLeverChange}
                showSearch
                optionFilterProp="children"
              >
                {LEVERS.map(lever => (
                  <Option key={lever.key} value={lever.key}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span>{lever.label}</span>
                      <Tooltip title={lever.description}>
                        <InfoCircleOutlined style={{ color: '#8c8c8c', fontSize: '12px' }} />
                      </Tooltip>
                    </div>
                  </Option>
                ))}
              </Select>
            </Form.Item>
          </Col>

          <Col xs={24} sm={8} md={8}>
            <Form.Item 
              label="Level" 
              name="level"
              rules={[{ required: true, message: 'Please select a level' }]}
            >
              <Select
                placeholder={config.lever ? "Select level" : "Select lever first"}
                disabled={!config.lever}
                mode="multiple"
                onChange={(value) => handleValueChange('level', value)}
              >
                {availableLevels.map(level => (
                  <Option key={level} value={level}>{level}</Option>
                ))}
              </Select>
            </Form.Item>
          </Col>

          <Col xs={24} sm={8} md={8}>
            <Form.Item 
              label={
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <span>Value</span>
                  {currentLever && (
                    <Tooltip title={currentLever.description}>
                      <InfoCircleOutlined style={{ color: '#8c8c8c', fontSize: '12px' }} />
                    </Tooltip>
                  )}
                </div>
              }
              name="value"
              rules={getValidationRules(currentLever)}
            >
              <InputNumber
                placeholder="Enter value"
                style={{ width: '100%' }}
                min={currentLever?.range[0] || 0}
                max={currentLever?.range[1] || 100}
                step={0.1}
                suffix={currentLever?.unit || '%'}
                onChange={(value) => handleValueChange('value', value || 0)}
              />
            </Form.Item>
          </Col>
        </Row>

        {/* Effective Rate Display */}
        {config.timePeriod !== 'monthly' && config.value > 0 && (
          <Alert
            message={
              <div>
                <Text strong>Effective Monthly Rate: </Text>
                <Text code>{effectiveMonthlyPercent}%</Text>
                <Text type="secondary" style={{ marginLeft: '8px' }}>
                  ({config.timePeriod === 'yearly' ? 'Yearly' : 'Half-Year'}: {config.value}% → Monthly: {effectiveMonthlyPercent}%)
                </Text>
              </div>
            }
            type="info"
            showIcon={false}
            style={{ marginBottom: '16px' }}
          />
        )}

        {/* Time Period Configuration */}
        <Divider orientation="left" style={{ fontSize: '14px', fontWeight: 500 }}>
          Time Period & Application Scope
        </Divider>
        
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={8}>
            <Form.Item label="Time Period" name="timePeriod">
              <Select
                value={config.timePeriod}
                onChange={(value) => handleValueChange('timePeriod', value)}
              >
                {TIME_PERIODS.map(period => (
                  <Option key={period.value} value={period.value}>
                    <Tooltip title={period.description} placement="right">
                      {period.label}
                    </Tooltip>
                  </Option>
                ))}
              </Select>
            </Form.Item>
          </Col>

          {config.timePeriod === 'monthly' && (
            <>
              <Col xs={24} sm={12} md={8}>
                <Form.Item label="Month" name="month">
                  <Select
                    value={config.month}
                    onChange={(value) => handleValueChange('month', value)}
                    disabled={config.applyToAllMonths}
                  >
                    {MONTHS.map(month => (
                      <Option key={month.value} value={month.value}>
                        {month.label}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
              
              <Col xs={24} sm={24} md={8}>
                <Form.Item label=" " style={{ marginBottom: 0 }}>
                  <Checkbox
                    checked={config.applyToAllMonths}
                    onChange={(e) => handleValueChange('applyToAllMonths', e.target.checked)}
                  >
                    <Tooltip title="Apply this lever to all 12 months of the simulation">
                      Apply to all months
                    </Tooltip>
                  </Checkbox>
                </Form.Item>
              </Col>
            </>
          )}

          {config.timePeriod === 'half-year' && (
            <Col xs={24} sm={12} md={8}>
              <Form.Item label="Reference Month" name="month">
                <Select
                  value={config.month}
                  onChange={(value) => handleValueChange('month', value)}
                >
                  {MONTHS.map(month => (
                    <Option key={month.value} value={month.value}>
                      {month.label} {month.value <= 6 ? '(First Half)' : '(Second Half)'}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          )}
        </Row>

        {/* Office Selection */}
        <Divider orientation="left" style={{ fontSize: '14px', fontWeight: 500 }}>
          Office Targeting
        </Divider>
        
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={8}>
            <Form.Item label=" " style={{ marginBottom: 0 }}>
              <Checkbox
                checked={config.applyToAllOffices}
                onChange={(e) => handleValueChange('applyToAllOffices', e.target.checked)}
              >
                <Tooltip title="Apply this lever to all offices in the simulation">
                  Apply to all offices
                </Tooltip>
              </Checkbox>
            </Form.Item>
          </Col>
          
          {!config.applyToAllOffices && (
            <>
              <Col xs={24} sm={12} md={8}>
                <Form.Item label="Office Journey" name="selectedOfficeJourney">
                  <Select
                    placeholder="Filter by office journey"
                    allowClear
                    value={config.selectedOfficeJourney || undefined}
                    onChange={(value) => handleValueChange('selectedOfficeJourney', value || '')}
                  >
                    {OFFICE_JOURNEYS.map(journey => (
                      <Option key={journey.value} value={journey.value}>
                        <Tooltip title={`Target offices in the ${journey.value.toLowerCase()} category`}>
                          {journey.label}
                        </Tooltip>
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
              
              <Col xs={24} sm={12} md={8}>
                <Form.Item label="Specific Offices" name="selectedOffices">
                  <Select
                    mode="multiple"
                    placeholder="Select specific offices (optional)"
                    allowClear
                    value={config.selectedOffices}
                    onChange={(value) => handleValueChange('selectedOffices', value || [])}
                    showSearch
                    optionFilterProp="children"
                    disabled={!!config.selectedOfficeJourney}
                  >
                    {/* This would be populated with actual office data in a real implementation */}
                    <Option value="stockholm">Stockholm</Option>
                    <Option value="copenhagen">Copenhagen</Option>
                    <Option value="oslo">Oslo</Option>
                    <Option value="helsinki">Helsinki</Option>
                    <Option value="amsterdam">Amsterdam</Option>
                    <Option value="berlin">Berlin</Option>
                    <Option value="munich">Munich</Option>
                    <Option value="hamburg">Hamburg</Option>
                    <Option value="frankfurt">Frankfurt</Option>
                    <Option value="zurich">Zurich</Option>
                    <Option value="cologne">Cologne</Option>
                  </Select>
                </Form.Item>
              </Col>
            </>
          )}
        </Row>
        
        {!config.applyToAllOffices && config.selectedOfficeJourney && (
          <Alert
            message={
              <Text>
                <Text strong>Targeting: </Text>
                {config.selectedOfficeJourney} offices will be affected by this lever
              </Text>
            }
            type="info"
            showIcon={false}
            style={{ marginBottom: '16px', fontSize: '12px' }}
          />
        )}
        
        {!config.applyToAllOffices && config.selectedOffices.length > 0 && (
          <Alert
            message={
              <Text>
                <Text strong>Targeting: </Text>
                {config.selectedOffices.length} specific office{config.selectedOffices.length > 1 ? 's' : ''} selected
              </Text>
            }
            type="info"
            showIcon={false}
            style={{ marginBottom: '16px', fontSize: '12px' }}
          />
        )}

        {/* Configuration Summary */}
        {config.lever && config.level && config.value > 0 && (
          <>
            <Divider orientation="left" style={{ fontSize: '14px', fontWeight: 500 }}>
              Configuration Summary
            </Divider>
            
            <Alert
              message="Lever Configuration"
              description={
                <div style={{ lineHeight: 1.6 }}>
                  <Text strong>{currentLever?.label}</Text> will be set to{' '}
                  <Text code>{config.value}{currentLever?.unit}</Text>{' '}
                  for levels{' '}
                  <Text code>{Array.isArray(config.level) ? config.level.join(', ') : config.level}</Text>
                  
                  <div style={{ marginTop: '8px' }}>
                    <Text type="secondary">
                      {config.timePeriod === 'monthly' ? (
                        config.applyToAllMonths ? 
                          'Applied to all months' : 
                          `Applied to ${MONTHS.find(m => m.value === config.month)?.label}`
                      ) : config.timePeriod === 'yearly' ? (
                        'Applied for the entire year'
                      ) : (
                        'Applied for half-year period'
                      )}
                      {' • '}
                      {config.applyToAllOffices ? 
                        'All offices' : 
                        config.selectedOfficeJourney ? 
                          `${config.selectedOfficeJourney} offices` :
                          config.selectedOffices.length > 0 ?
                            `${config.selectedOffices.length} specific office${config.selectedOffices.length > 1 ? 's' : ''}` :
                            'No offices selected'
                      }
                    </Text>
                  </div>
                  
                  {config.timePeriod !== 'monthly' && (
                    <div style={{ marginTop: '8px' }}>
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        Effective monthly rate: {effectiveMonthlyPercent}%
                      </Text>
                    </div>
                  )}
                </div>
              }
              type="info"
              showIcon
              style={{ marginBottom: '16px' }}
            />
          </>
        )}

        {/* Action Buttons */}
        <Row justify="end" style={{ marginTop: '24px' }}>
          <Col>
            <Space>
              <Button onClick={onReset} disabled={loading}>
                Reset
              </Button>
              <Button 
                type="primary" 
                onClick={handleApply}
                loading={loading}
                disabled={!config.lever || !config.level || config.value <= 0}
              >
                Apply Lever
              </Button>
            </Space>
          </Col>
        </Row>

        {/* Last Applied Summary */}
        {lastAppliedSummary && lastAppliedSummary.length > 0 && (
          <Alert
            message="Last Applied Changes"
            description={
              <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                {lastAppliedSummary.map((item, idx) => (
                  <li key={idx} style={{ marginBottom: '4px' }}>
                    <Text>{item}</Text>
                  </li>
                ))}
              </ul>
            }
            type="success"
            showIcon
            closable
            style={{ marginTop: '16px' }}
          />
        )}
      </Form>
    </Card>
  );
};

export default SimulationLeversCard; 