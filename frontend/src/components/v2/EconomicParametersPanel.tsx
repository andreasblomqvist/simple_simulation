import React, { useId } from 'react';
import { Collapse, Form, Row, Col, InputNumber, Typography, Tooltip } from 'antd';
import { InfoCircleOutlined, DollarOutlined } from '@ant-design/icons';

const { Panel } = Collapse;
const { Text } = Typography;

interface EconomicParametersProps {
  formValues: {
    price_increase: number;
    salary_increase: number;
    unplanned_absence: number;
    hy_working_hours: number;
    other_expense: number;
  };
  onValuesChange: (changedValues: any, allValues: any) => void;
  loading?: boolean;
  className?: string;
}

/**
 * EconomicParametersPanel Component
 * 
 * Collapsible panel for configuring economic and operational parameters:
 * - Price and salary increase rates
 * - Working hours and absence rates
 * - Other operational expenses
 * - Real-time validation and calculation aids
 */
export const EconomicParametersPanel: React.FC<EconomicParametersProps> = ({
  formValues,
  onValuesChange,
  loading = false,
  className = ''
}) => {
  const panelId = useId();
  const formId = useId();
  
  // Calculate derived metrics for user guidance
  const monthlyWorkingDays = Math.round(formValues.hy_working_hours / 8); // Assuming 8-hour days
  const effectiveWorkingHours = formValues.hy_working_hours * (1 - formValues.unplanned_absence / 100);
  const monthlyExpenseFormatted = new Intl.NumberFormat('sv-SE').format(formValues.other_expense);

  return (
    <div className={className} role="region" aria-labelledby={`${panelId}-heading`}>
      <Collapse 
        defaultActiveKey={[]}
        ghost
        size="large"
        expandIconPosition="right"
        aria-label="Economic parameters configuration"
      >
        <Panel
          header={
            <div 
              id={`${panelId}-heading`}
              style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
              role="heading"
              aria-level={3}
            >
              <DollarOutlined aria-hidden="true" />
              <Text strong style={{ fontSize: '16px' }}>Economic Parameters</Text>
              <Tooltip title="Configure financial and operational parameters for the simulation">
                <InfoCircleOutlined 
                  style={{ color: '#8c8c8c', fontSize: '14px' }} 
                  aria-label="Help information for economic parameters"
                  tabIndex={0}
                />
              </Tooltip>
            </div>
          }
          key="economic"
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
            Configure economic parameters including price increases, salary increases, working hours, 
            and operational expenses for the simulation.
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
            {/* Financial Parameters */}
            <fieldset style={{ border: 'none', padding: 0, margin: 0 }}>
              <legend className="sr-only">Financial parameters</legend>
              <Row gutter={[16, 16]}>
                <Col xs={24} sm={12} md={6}>
                  <Form.Item 
                    label={
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <span>Price Increase</span>
                        <Tooltip title="Annual price increase rate for consultant services">
                          <InfoCircleOutlined 
                            style={{ color: '#8c8c8c', fontSize: '12px' }} 
                            aria-label="Help: Annual price increase rate for consultant services"
                            tabIndex={0}
                          />
                        </Tooltip>
                      </div>
                    }
                    name="price_increase"
                    rules={[
                      { required: true, message: 'Please enter price increase' },
                      { type: 'number', min: 0, max: 50, message: 'Price increase must be between 0% and 50%' }
                    ]}
                  >
                    <InputNumber 
                      placeholder="3.0"
                      style={{ width: '100%' }}
                      min={0}
                      max={50}
                      step={0.1}
                      suffix="%"
                      aria-label="Price increase percentage (0-50%)"
                      aria-describedby="price-increase-help"
                    />
                  </Form.Item>
                  <div id="price-increase-help" className="sr-only">
                    Enter annual price increase rate between 0 and 50 percent
                  </div>
                </Col>

              <Col xs={24} sm={12} md={6}>
                <Form.Item 
                  label={
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <span>Salary Increase</span>
                      <Tooltip title="Annual salary increase rate for all employees">
                        <InfoCircleOutlined style={{ color: '#8c8c8c', fontSize: '12px' }} />
                      </Tooltip>
                    </div>
                  }
                  name="salary_increase"
                  rules={[
                    { required: true, message: 'Please enter salary increase' },
                    { type: 'number', min: 0, max: 50, message: 'Salary increase must be between 0% and 50%' }
                  ]}
                >
                  <InputNumber 
                    placeholder="3.0"
                    style={{ width: '100%' }}
                    min={0}
                    max={50}
                    step={0.1}
                    suffix="%"
                  />
                </Form.Item>
              </Col>

              <Col xs={24} sm={12} md={6}>
                <Form.Item 
                  label={
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <span>Unplanned Absence</span>
                      <Tooltip title="Percentage of working time lost due to sick leave, vacations, etc.">
                        <InfoCircleOutlined style={{ color: '#8c8c8c', fontSize: '12px' }} />
                      </Tooltip>
                    </div>
                  }
                  name="unplanned_absence"
                  rules={[
                    { required: true, message: 'Please enter unplanned absence rate' },
                    { type: 'number', min: 0, max: 50, message: 'Unplanned absence must be between 0% and 50%' }
                  ]}
                >
                  <InputNumber 
                    placeholder="5.0"
                    style={{ width: '100%' }}
                    min={0}
                    max={50}
                    step={0.1}
                    suffix="%"
                  />
                </Form.Item>
              </Col>

              <Col xs={24} sm={12} md={6}>
                <Form.Item 
                  label={
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <span>Monthly Working Hours</span>
                      <Tooltip title="Average working hours per month per employee">
                        <InfoCircleOutlined style={{ color: '#8c8c8c', fontSize: '12px' }} />
                      </Tooltip>
                    </div>
                  }
                  name="hy_working_hours"
                  rules={[
                    { required: true, message: 'Please enter working hours' },
                    { type: 'number', min: 80, max: 300, message: 'Working hours must be between 80 and 300' }
                  ]}
                >
                  <InputNumber 
                    placeholder="166.4"
                    style={{ width: '100%' }}
                    min={80}
                    max={300}
                    step={0.1}
                    suffix="hrs"
                  />
                </Form.Item>
              </Col>
            </Row>
            </fieldset>

            {/* Operational Expenses */}
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12} md={8}>
                <Form.Item 
                  label={
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <span>Other Monthly Expenses</span>
                      <Tooltip title="Additional monthly operational expenses (office rent, utilities, etc.)">
                        <InfoCircleOutlined style={{ color: '#8c8c8c', fontSize: '12px' }} />
                      </Tooltip>
                    </div>
                  }
                  name="other_expense"
                  rules={[
                    { required: true, message: 'Please enter other expenses' },
                    { type: 'number', min: 0, message: 'Other expenses must be non-negative' }
                  ]}
                >
                  <InputNumber 
                    placeholder="100000"
                    style={{ width: '100%' }}
                    min={0}
                    step={1000}
                    prefix="SEK"
                  />
                </Form.Item>
              </Col>
            </Row>

            {/* Calculated Metrics Display */}
            <Row gutter={[16, 16]} style={{ marginTop: '16px' }}>
              <Col span={24}>
                <div style={{ 
                  background: '#f0f8ff',
                  border: '1px solid #d6e4ff',
                  borderRadius: '6px',
                  padding: '16px'
                }}>
                  <Text strong style={{ color: '#1890ff', fontSize: '14px', marginBottom: '12px', display: 'block' }}>
                    Calculated Metrics
                  </Text>
                  
                  <Row gutter={[24, 8]}>
                    <Col xs={24} sm={8}>
                      <div>
                        <Text type="secondary" style={{ fontSize: '12px', display: 'block' }}>
                          Effective Working Hours/Month
                        </Text>
                        <Text strong style={{ fontSize: '16px', color: '#1890ff' }}>
                          {effectiveWorkingHours.toFixed(1)} hrs
                        </Text>
                        <Text type="secondary" style={{ fontSize: '11px', display: 'block' }}>
                          (After {formValues.unplanned_absence}% absence)
                        </Text>
                      </div>
                    </Col>
                    
                    <Col xs={24} sm={8}>
                      <div>
                        <Text type="secondary" style={{ fontSize: '12px', display: 'block' }}>
                          Approx. Working Days/Month
                        </Text>
                        <Text strong style={{ fontSize: '16px', color: '#1890ff' }}>
                          {monthlyWorkingDays} days
                        </Text>
                        <Text type="secondary" style={{ fontSize: '11px', display: 'block' }}>
                          (Assuming 8 hrs/day)
                        </Text>
                      </div>
                    </Col>
                    
                    <Col xs={24} sm={8}>
                      <div>
                        <Text type="secondary" style={{ fontSize: '12px', display: 'block' }}>
                          Monthly Other Expenses
                        </Text>
                        <Text strong style={{ fontSize: '16px', color: '#1890ff' }}>
                          {monthlyExpenseFormatted} SEK
                        </Text>
                        <Text type="secondary" style={{ fontSize: '11px', display: 'block' }}>
                          (Annual: {(formValues.other_expense * 12 / 1000000).toFixed(1)}M SEK)
                        </Text>
                      </div>
                    </Col>
                  </Row>
                </div>
              </Col>
            </Row>

            {/* Parameter Guidelines */}
            <Row style={{ marginTop: '16px' }}>
              <Col span={24}>
                <div style={{ 
                  background: '#fffbe6',
                  border: '1px solid #ffe58f',
                  borderRadius: '6px',
                  padding: '12px'
                }}>
                  <Text strong style={{ color: '#d48806', fontSize: '13px' }}>
                    Parameter Guidelines
                  </Text>
                  <div style={{ marginTop: '8px' }}>
                    <Text style={{ fontSize: '12px', display: 'block', marginBottom: '4px' }}>
                      • <strong>Price/Salary Increases:</strong> Typical annual rates are 2-5% in stable markets
                    </Text>
                    <Text style={{ fontSize: '12px', display: 'block', marginBottom: '4px' }}>
                      • <strong>Unplanned Absence:</strong> Industry average is 3-7% (includes sick leave, personal time)
                    </Text>
                    <Text style={{ fontSize: '12px', display: 'block', marginBottom: '4px' }}>
                      • <strong>Working Hours:</strong> Standard is ~166-170 hours/month (40-hour weeks)
                    </Text>
                    <Text style={{ fontSize: '12px', display: 'block' }}>
                      • <strong>Other Expenses:</strong> Include office costs, utilities, equipment, but exclude salaries
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

export default EconomicParametersPanel; 