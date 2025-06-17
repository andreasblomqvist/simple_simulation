import React, { useId } from 'react';
import { Collapse, Form, Row, Col, InputNumber, Select, Typography, Tooltip } from 'antd';
import { InfoCircleOutlined, ClockCircleOutlined } from '@ant-design/icons';

const { Panel } = Collapse;
const { Text } = Typography;
const { Option } = Select;

interface SimulationScopeProps {
  formValues: {
    duration_value: number;
    duration_unit: 'months' | 'years';
    start_year: number;
    start_month: number;
  };
  onValuesChange: (changedValues: any, allValues: any) => void;
  loading?: boolean;
  className?: string;
}

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

const YEARS = Array.from({ length: 10 }, (_, i) => 2024 + i);

/**
 * SimulationScopePanel Component
 * 
 * Collapsible panel for configuring simulation scope and duration:
 * - Simulation duration (months/years)
 * - Start date configuration
 * - Automatic end date calculation
 * - Real-time validation and feedback
 */
export const SimulationScopePanel: React.FC<SimulationScopeProps> = ({
  formValues,
  onValuesChange,
  loading = false,
  className = ''
}) => {
  const panelId = useId();
  const formId = useId();
  
  // Calculate end date based on duration
  const calculateEndDate = () => {
    const { duration_value, duration_unit, start_year, start_month } = formValues;
    const durationMonths = duration_unit === 'years' ? duration_value * 12 : duration_value;
    
    const totalMonths = start_month + durationMonths - 1;
    const endYear = start_year + Math.floor((totalMonths - 1) / 12);
    const endMonth = ((totalMonths - 1) % 12) + 1;
    
    const endMonthName = MONTHS.find(m => m.value === endMonth)?.label || '';
    
    return {
      year: endYear,
      month: endMonth,
      monthName: endMonthName,
      totalMonths: durationMonths
    };
  };

  const endDate = calculateEndDate();

  return (
    <div className={className} role="region" aria-labelledby={`${panelId}-heading`}>
      <Collapse 
        defaultActiveKey={['scope']}
        ghost
        size="large"
        expandIconPosition="right"
        aria-label="Simulation scope configuration"
      >
        <Panel
          header={
            <div 
              id={`${panelId}-heading`}
              style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
              role="heading"
              aria-level={3}
            >
              <ClockCircleOutlined aria-hidden="true" />
              <Text strong style={{ fontSize: '16px' }}>Simulation Scope</Text>
              <Tooltip title="Configure the time period and duration for your simulation">
                <InfoCircleOutlined 
                  style={{ color: '#8c8c8c', fontSize: '14px' }} 
                  aria-label="Help information for simulation scope"
                  tabIndex={0}
                />
              </Tooltip>
            </div>
          }
          key="scope"
          style={{ 
            background: '#fafafa', 
            borderRadius: '8px',
            border: '1px solid #f0f0f0',
            marginBottom: '16px'
          }}
          aria-describedby={`${panelId}-description`}
        >
          <div 
            id={`${panelId}-description`} 
            className="sr-only"
            aria-hidden="true"
          >
            Configure the simulation time period including start date and duration. 
            End date will be calculated automatically based on your inputs.
          </div>
          
          <Form
            id={formId}
            layout="vertical"
            initialValues={formValues}
            onValuesChange={onValuesChange}
            disabled={loading}
            size="middle"
            aria-labelledby={`${panelId}-heading`}
            aria-describedby={`${panelId}-description`}
            role="form"
          >
            {/* Start Date Configuration */}
            <fieldset style={{ border: 'none', padding: 0, margin: 0 }}>
              <legend className="sr-only">Simulation start date configuration</legend>
              <Row gutter={[16, 16]}>
                <Col xs={24} sm={12} md={8}>
                  <Form.Item 
                    label="Start Year" 
                    name="start_year"
                    rules={[{ required: true, message: 'Please select start year' }]}
                  >
                    <Select 
                      placeholder="Select start year"
                      aria-label="Select simulation start year"
                      showSearch
                      optionFilterProp="children"
                      filterOption={(input, option) =>
                        (option?.children ?? '').toString().toLowerCase().includes(input.toLowerCase())
                      }
                    >
                      {YEARS.map(year => (
                        <Option key={year} value={year} aria-label={`Year ${year}`}>
                          {year}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>

                <Col xs={24} sm={12} md={8}>
                  <Form.Item 
                    label="Start Month" 
                    name="start_month"
                    rules={[{ required: true, message: 'Please select start month' }]}
                  >
                    <Select 
                      placeholder="Select start month"
                      aria-label="Select simulation start month"
                      showSearch
                      optionFilterProp="children"
                      filterOption={(input, option) =>
                        (option?.children ?? '').toString().toLowerCase().includes(input.toLowerCase())
                      }
                    >
                      {MONTHS.map(month => (
                        <Option 
                          key={month.value} 
                          value={month.value}
                          aria-label={`${month.label} (month ${month.value})`}
                        >
                          {month.label}
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
              </Row>
            </fieldset>

            {/* Duration Configuration */}
            <fieldset style={{ border: 'none', padding: 0, margin: 0 }}>
              <legend className="sr-only">Simulation duration configuration</legend>
              <Row gutter={[16, 16]} align="bottom">
                <Col xs={24} sm={12} md={8}>
                  <Form.Item 
                    label={
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <span>Duration</span>
                        <Tooltip title="How long should the simulation run">
                          <InfoCircleOutlined 
                            style={{ color: '#8c8c8c', fontSize: '12px' }} 
                            aria-label="Help: How long should the simulation run"
                            tabIndex={0}
                          />
                        </Tooltip>
                      </div>
                    }
                    name="duration_value"
                    rules={[
                      { required: true, message: 'Please enter duration' },
                      { type: 'number', min: 1, max: 120, message: 'Duration must be between 1 and 120' }
                    ]}
                  >
                    <InputNumber 
                      placeholder="Enter duration"
                      style={{ width: '100%' }}
                      min={1}
                      max={120}
                      aria-label="Simulation duration value (1-120)"
                      aria-describedby="duration-help"
                    />
                  </Form.Item>
                  <div id="duration-help" className="sr-only">
                    Enter a number between 1 and 120 for the simulation duration
                  </div>
                </Col>

                <Col xs={24} sm={12} md={8}>
                  <Form.Item 
                    label="Duration Unit" 
                    name="duration_unit"
                    rules={[{ required: true, message: 'Please select duration unit' }]}
                  >
                    <Select 
                      placeholder="Select unit"
                      aria-label="Select duration unit (months or years)"
                    >
                      <Option value="months" aria-label="Duration in months">Months</Option>
                      <Option value="years" aria-label="Duration in years">Years</Option>
                    </Select>
                  </Form.Item>
                </Col>

              {/* End Date Display */}
              <Col xs={24} sm={24} md={8}>
                <div 
                  style={{ 
                    background: '#f0f8ff',
                    border: '1px solid #d6e4ff',
                    borderRadius: '6px',
                    padding: '12px',
                    marginBottom: '24px'
                  }}
                  role="status"
                  aria-live="polite"
                  aria-label="Calculated simulation end date"
                >
                  <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginBottom: '4px' }}>
                    Calculated End Date
                  </Text>
                  <Text strong style={{ fontSize: '14px', color: '#1890ff' }}>
                    {endDate.monthName} {endDate.year}
                  </Text>
                  <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: '2px' }}>
                    ({endDate.totalMonths} total months)
                  </Text>
                </div>
              </Col>
            </Row>
            </fieldset>

            {/* Summary Information */}
            <Row>
              <Col span={24}>
                <div style={{ 
                  background: '#f6ffed',
                  border: '1px solid #b7eb8f',
                  borderRadius: '6px',
                  padding: '12px'
                }}>
                  <Text strong style={{ color: '#389e0d', fontSize: '14px' }}>
                    Simulation Period Summary
                  </Text>
                  <div style={{ marginTop: '8px' }}>
                    <Text style={{ fontSize: '13px' }}>
                      <strong>Start:</strong> {MONTHS.find(m => m.value === formValues.start_month)?.label} {formValues.start_year}
                      {' | '}
                      <strong>End:</strong> {endDate.monthName} {endDate.year}
                      {' | '}
                      <strong>Duration:</strong> {formValues.duration_value} {formValues.duration_unit} ({endDate.totalMonths} months)
                    </Text>
                  </div>
                </div>
              </Col>
            </Row>
          </Form>
        </Panel>
      </Collapse>
    </div>
  );
};

export default SimulationScopePanel; 