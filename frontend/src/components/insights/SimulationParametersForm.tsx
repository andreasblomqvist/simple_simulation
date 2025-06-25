import React from 'react';
import { Row, Col, Card, Typography, Divider, Button, Select, Form, InputNumber, theme } from 'antd';
import { SettingOutlined } from '@ant-design/icons';

const { Text } = Typography;
const { Option } = Select;
const { useToken } = theme;

interface SimulationParametersFormProps {
  form: any;
  levelActions: {
    churn: Array<{level: string, rate: number}>;
    recruitment: Array<{level: string, rate: number}>;
  };
  setLevelActions: (actions: any) => void;
  selectedAction: string;
  setSelectedAction: (action: string) => void;
  selectedLevels: string[];
  setSelectedLevels: (levels: string[]) => void;
  selectedRate: number;
  setSelectedRate: (rate: number) => void;
  defaultParams: any;
}

const SimulationParametersForm: React.FC<SimulationParametersFormProps> = ({
  form,
  levelActions,
  setLevelActions,
  selectedAction,
  setSelectedAction,
  selectedLevels,
  setSelectedLevels,
  selectedRate,
  setSelectedRate,
  defaultParams
}) => {
  const { token } = useToken();

  return (
    <Card 
      title={
        <span>
          <SettingOutlined style={{ marginRight: 8 }} />
          Simulation Parameters
        </span>
      } 
      style={{ marginBottom: 24 }}
    >
      <Form
        form={form}
        layout="vertical"
      >
        <Row gutter={16}>
          <Col xs={24} sm={12} md={6}>
            <Form.Item
              label="Start Year"
              name="start_year"
              rules={[{ required: true, message: 'Please enter start year' }]}
            >
              <InputNumber 
                min={2020} 
                max={2030} 
                style={{ width: '100%' }}
              />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Form.Item
              label="Start Month"
              name="start_month"
              rules={[{ required: true, message: 'Please select start month' }]}
            >
              <Select style={{ width: '100%' }}>
                {Array.from({ length: 12 }, (_, i) => (
                  <Option key={i + 1} value={i + 1}>
                    {new Date(0, i).toLocaleString('default', { month: 'long' })}
                  </Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Form.Item
              label="End Year"
              name="end_year"
              rules={[{ required: true, message: 'Please enter end year' }]}
            >
              <InputNumber 
                min={2020} 
                max={2030} 
                style={{ width: '100%' }}
              />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Form.Item
              label="End Month"
              name="end_month"
              rules={[{ required: true, message: 'Please select end month' }]}
            >
              <Select style={{ width: '100%' }}>
                {Array.from({ length: 12 }, (_, i) => (
                  <Option key={i + 1} value={i + 1}>
                    {new Date(0, i).toLocaleString('default', { month: 'long' })}
                  </Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col xs={24} sm={12} md={8}>
            <Form.Item
              label="Price Increase (%)"
              name="price_increase"
              rules={[{ required: true, message: 'Please enter price increase' }]}
            >
              <InputNumber 
                min={-0.5} 
                max={0.5} 
                step={0.001}
                formatter={value => `${((value || 0) * 100).toFixed(1)}%`}
                parser={value => (parseFloat(value?.replace('%', '') || '0') / 100) as any}
                style={{ width: '100%' }}
              />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Form.Item
              label="Salary Increase (%)"
              name="salary_increase"
              rules={[{ required: true, message: 'Please enter salary increase' }]}
            >
              <InputNumber 
                min={-0.5} 
                max={0.5} 
                step={0.001}
                formatter={value => `${((value || 0) * 100).toFixed(1)}%`}
                parser={value => (parseFloat(value?.replace('%', '') || '0') / 100) as any}
                style={{ width: '100%' }}
              />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Form.Item
              label="Unplanned Absence (%)"
              name="unplanned_absence"
              rules={[{ required: true, message: 'Please enter unplanned absence' }]}
            >
              <InputNumber 
                min={0} 
                max={0.5} 
                step={0.001}
                formatter={value => `${((value || 0) * 100).toFixed(1)}%`}
                parser={value => (parseFloat(value?.replace('%', '') || '0') / 100) as any}
                style={{ width: '100%' }}
              />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col xs={24} sm={12}>
            <Form.Item
              label="Working Hours per Month"
              name="hy_working_hours"
              rules={[{ required: true, message: 'Please enter working hours' }]}
            >
              <InputNumber 
                min={100} 
                max={300} 
                step={0.1}
                style={{ width: '100%' }}
              />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12}>
            <Form.Item
              label="Other Expenses (SEK)"
              name="other_expense"
              rules={[{ required: true, message: 'Please enter other expenses' }]}
            >
              <InputNumber 
                min={0} 
                max={100000000} 
                step={1000000}
                formatter={value => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                parser={value => parseInt(value?.replace(/\$\s?|(,*)/g, '') || '0') as any}
                style={{ width: '100%' }}
              />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col xs={24} sm={12}>
            <Form.Item
              label="UTR Adjustment (%)"
              name="utr_adjustment"
              rules={[{ required: true, message: 'Please enter UTR adjustment' }]}
              tooltip="Global adjustment to utilization rates (positive = increase, negative = decrease)"
            >
              <InputNumber 
                min={-0.5} 
                max={0.5} 
                step={0.001}
                formatter={value => `${((value || 0) * 100).toFixed(1)}%`}
                parser={value => (parseFloat(value?.replace('%', '') || '0') / 100) as any}
                style={{ width: '100%' }}
              />
            </Form.Item>
          </Col>
        </Row>

        <Divider orientation="left" style={{ marginTop: 32, marginBottom: 16 }}>
          <Text strong style={{ color: token.colorSuccess }}>Level-Specific Actions</Text>
          <br />
          <Text type="secondary" style={{ fontSize: '12px' }}>Apply targeted actions to specific levels</Text>
        </Divider>

        {/* Level Action Builder */}
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col xs={24} sm={6}>
            <Text strong style={{ fontSize: '13px' }}>Action Type:</Text>
            <Select
              placeholder="Select action"
              value={selectedAction}
              onChange={setSelectedAction}
              style={{ width: '100%', marginTop: 4 }}
              options={[
                { value: 'churn', label: '🎯 Increase Churn' },
                { value: 'recruitment', label: '📈 Increase Recruitment' }
              ]}
            />
          </Col>
          <Col xs={24} sm={6}>
            <Text strong style={{ fontSize: '13px' }}>Target Level:</Text>
            <Select
              mode="multiple"
              placeholder="Select levels"
              value={selectedLevels}
              onChange={setSelectedLevels}
              style={{ width: '100%', marginTop: 4 }}
              options={[
                { value: 'A', label: 'A (Entry)' },
                { value: 'AC', label: 'AC (Associate Consultant)' },
                { value: 'C', label: 'C (Consultant)' },
                { value: 'SrC', label: 'SrC (Senior Consultant)' },
                { value: 'AM', label: 'AM (Associate Manager)' },
                { value: 'M', label: 'M (Manager)' },
                { value: 'SrM', label: 'SrM (Senior Manager)' },
                { value: 'PiP', label: 'PiP (Partner in Progress)' }
              ]}
            />
          </Col>
          <Col xs={24} sm={6}>
            <Text strong style={{ fontSize: '13px' }}>Rate (%/month):</Text>
            <InputNumber
              min={0}
              max={20}
              step={0.1}
              placeholder="2.5"
              value={selectedRate}
              onChange={(value) => setSelectedRate(value || 0)}
              style={{ width: '100%', marginTop: 4 }}
              formatter={value => `${value}%`}
              parser={value => parseFloat(value?.replace('%', '') || '0') as any}
            />
          </Col>
          <Col xs={24} sm={6}>
            <Text strong style={{ fontSize: '13px' }}>&nbsp;</Text>
            <Button 
              type="primary" 
              style={{ width: '100%', marginTop: 4 }}
              disabled={!selectedAction || selectedLevels.length === 0 || selectedRate < 0}
              onClick={() => {
                if (!selectedAction || selectedLevels.length === 0 || selectedRate < 0) return;
                
                const newActions = { ...levelActions };
                
                selectedLevels.forEach(level => {
                  const newAction = { level, rate: selectedRate };
                  
                  if (selectedAction === 'churn') {
                    // Remove existing churn action for this level
                    newActions.churn = newActions.churn.filter(a => a.level !== level);
                    newActions.churn.push(newAction);
                  } else if (selectedAction === 'recruitment') {
                    // Remove existing recruitment action for this level
                    newActions.recruitment = newActions.recruitment.filter(a => a.level !== level);
                    newActions.recruitment.push(newAction);
                  }
                });
                
                setLevelActions(newActions);
                
                // Clear form
                setSelectedAction('');
                setSelectedLevels([]);
                setSelectedRate(0);
              }}
            >
              {selectedRate === 0 ? 'Set to Zero' : 'Add Action'}
            </Button>
          </Col>
        </Row>

        {/* Current Actions Display */}
        <Card size="small" style={{ marginTop: 16, backgroundColor: token.colorSuccessBg }}>
          <Text strong style={{ fontSize: '13px' }}>Applied Level Actions:</Text>
          <div style={{ marginTop: 8 }}>
            {levelActions.churn.length === 0 && levelActions.recruitment.length === 0 ? (
              <Text type="secondary" style={{ fontSize: '12px' }}>
                No level-specific actions applied. Use the controls above to add targeted churn or recruitment actions.
              </Text>
            ) : (
              <>
                {levelActions.churn.map((action, index) => (
                  <div key={`churn-${index}`} style={{ marginBottom: 4, display: 'flex', alignItems: 'center' }}>
                    <span style={{ color: token.colorError, marginRight: 8 }}>🎯</span>
                    <Text style={{ flex: 1 }}>
                      {action.level} Churn: {action.rate}%/month
                      {action.rate === 0 && <span style={{ color: token.colorWarning, marginLeft: 4 }}>(Zeroed)</span>}
                    </Text>
                    <Button 
                      type="link" 
                      size="small" 
                      style={{ color: token.colorError, padding: '0 4px' }}
                      onClick={() => {
                        const newActions = { ...levelActions };
                        newActions.churn.splice(index, 1);
                        setLevelActions(newActions);
                      }}
                    >
                      ✕
                    </Button>
                  </div>
                ))}
                {levelActions.recruitment.map((action, index) => (
                  <div key={`recruitment-${index}`} style={{ marginBottom: 4, display: 'flex', alignItems: 'center' }}>
                    <span style={{ color: token.colorSuccess, marginRight: 8 }}>📈</span>
                    <Text style={{ flex: 1 }}>
                      {action.level} Recruitment: {action.rate}%/month
                      {action.rate === 0 && <span style={{ color: token.colorWarning, marginLeft: 4 }}>(Zeroed)</span>}
                    </Text>
                    <Button 
                      type="link" 
                      size="small" 
                      style={{ color: token.colorError, padding: '0 4px' }}
                      onClick={() => {
                        const newActions = { ...levelActions };
                        newActions.recruitment.splice(index, 1);
                        setLevelActions(newActions);
                      }}
                    >
                      ✕
                    </Button>
                  </div>
                ))}
              </>
            )}
            
            {/* Clear All Actions Button */}
            {(levelActions.churn.length > 0 || levelActions.recruitment.length > 0) && (
              <div style={{ marginTop: 12, paddingTop: 8, borderTop: `1px solid ${token.colorBorder}` }}>
                <Button 
                  size="small" 
                  onClick={() => setLevelActions({ churn: [], recruitment: [] })}
                >
                  Clear All Actions
                </Button>
              </div>
            )}
          </div>
        </Card>
      </Form>
    </Card>
  );
};

export default SimulationParametersForm; 