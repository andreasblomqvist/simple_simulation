import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Select, InputNumber, Checkbox, Button, Space, Collapse, Table, Tabs, Typography, message, Spin, Alert, Input } from 'antd';
import { SettingOutlined, RocketOutlined, TableOutlined, LoadingOutlined, ControlOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { simulationApi } from '../services/simulationApi';
import type { OfficeConfig, SimulationResults } from '../services/simulationApi';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

// Add constants for lever manipulation
const LEVERS = [
  { key: 'recruitment', label: 'Recruitment' },
  { key: 'churn', label: 'Churn' },
  { key: 'progression', label: 'Progression' },
  { key: 'utr', label: 'UTR' },
];

const LEVELS = ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"];

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
  { value: 'monthly', label: 'Monthly' },
  { value: 'half-year', label: 'Half Year' },
  { value: 'yearly', label: 'Yearly' }
];

const OFFICE_JOURNEYS = [
  { value: 'New Office', label: 'New Office (0-24 FTE)' },
  { value: 'Emerging Office', label: 'Emerging Office (25-199 FTE)' },
  { value: 'Established Office', label: 'Established Office (200-499 FTE)' },
  { value: 'Mature Office', label: 'Mature Office (500+ FTE)' }
];

// Helper function to compute monthly rate from cumulative probability
function getMonthlyRateFromCumulative(cumulative: number, months: number) {
  if (cumulative >= 1) cumulative = 0.9999;
  if (cumulative <= 0) return 0;
  return 1 - Math.pow(1 - cumulative, 1 / months);
}

const SimulationLabV2: React.FC = () => {
  // Form state
  const [selectedLever, setSelectedLever] = useState<string | undefined>();
  const [selectedLevel, setSelectedLevel] = useState<string | undefined>();
  const [leverValue, setLeverValue] = useState<number | null>(null);
  const [applyToAllMonths, setApplyToAllMonths] = useState(false);
  const [applyToAllOffices, setApplyToAllOffices] = useState(true);
  const [selectedOffices, setSelectedOffices] = useState<string[]>([]);
  const [activeYear, setActiveYear] = useState('2025');
  
  // Economic parameters
  const [priceIncrease, setPriceIncrease] = useState(2.0);
  const [salaryIncrease, setSalaryIncrease] = useState(2.0);
  const [workingHours, setWorkingHours] = useState(166.4);
  const [otherExpense, setOtherExpense] = useState(10000);
  
  // Simulation duration
  const [simulationDuration, setSimulationDuration] = useState(3); // Default 3 years
  const [selectedDurationUnit, setSelectedDurationUnit] = useState('years');
  
  // API data
  const [officeConfig, setOfficeConfig] = useState<OfficeConfig[]>([]);
  const [simulationResults, setSimulationResults] = useState<SimulationResults | null>(null);
  const [availableYears, setAvailableYears] = useState<string[]>([]);
  
  // Loading states
  const [loading, setLoading] = useState(false);
  const [configLoading, setConfigLoading] = useState(true);
  const [simulationRunning, setSimulationRunning] = useState(false);
  
  // Error states
  const [error, setError] = useState<string | null>(null);

  // Add lever manipulation state
  const [selectedLevers, setSelectedLevers] = useState(['recruitment']);
  const [selectedLevels, setSelectedLevels] = useState(['AM']);
  const [selectedMonth, setSelectedMonth] = useState(1);
  const [selectedTimePeriod, setSelectedTimePeriod] = useState('monthly');
  const [selectedOfficeJourney, setSelectedOfficeJourney] = useState('');

  // Load office configuration on mount
  useEffect(() => {
    const loadOfficeConfig = async () => {
      try {
        setConfigLoading(true);
        const config = await simulationApi.getOfficeConfig();
        setOfficeConfig(config);
        setError(null);
      } catch (err) {
        setError('Failed to load office configuration');
        console.error('Error loading office config:', err);
      } finally {
        setConfigLoading(false);
      }
    };

    loadOfficeConfig();
  }, []);

  // Load available years when simulation results exist
  useEffect(() => {
    const loadAvailableYears = async () => {
      try {
        const years = await simulationApi.getAvailableYears();
        setAvailableYears(years);
        if (years.length > 0 && !years.includes(activeYear)) {
          setActiveYear(years[0]);
        }
      } catch (err) {
        // Ignore error - no simulation results yet
        console.log('No simulation results available yet');
      }
    };

    if (simulationResults) {
      loadAvailableYears();
    }
  }, [simulationResults, activeYear]);

  // Computed data from API
  const leverOptions = officeConfig.length > 0 ? simulationApi.extractLeverOptions(officeConfig) : [];
  const levelOptions = selectedLever && officeConfig.length > 0 
    ? simulationApi.extractLevelOptions(officeConfig, selectedLever) 
    : [];
  const officeOptions = officeConfig.length > 0 ? simulationApi.extractOfficeOptions(officeConfig) : [];
  
  const kpiData = simulationResults && activeYear 
    ? simulationApi.extractKPIData(simulationResults, activeYear)
    : [];
  
  const tableData = simulationResults && activeYear
    ? simulationApi.extractTableData(simulationResults, activeYear)
    : [];
  
  const seniorityData = simulationResults && activeYear
    ? simulationApi.extractSeniorityData(simulationResults, activeYear)
    : [];
  
  const seniorityKPIs = simulationResults && activeYear
    ? simulationApi.extractSeniorityKPIs(simulationResults, activeYear)
    : null;

  // Seniority data updates when year changes

  const handleLeverChange = (value: string) => {
    setSelectedLever(value);
    setSelectedLevel(undefined);
    setLeverValue(null);
  };

  const handleRunSimulation = async () => {
    try {
      setSimulationRunning(true);
      setError(null);
      
      // Prepare simulation parameters
      const startYear = 2025;
      const totalMonths = selectedDurationUnit === 'years' ? simulationDuration * 12 : 
                          selectedDurationUnit === 'half-years' ? simulationDuration * 6 : 
                          simulationDuration;
      const endYear = startYear + Math.ceil(totalMonths / 12) - 1;
      
      const params = {
        start_year: startYear,
        start_month: 1,
        end_year: endYear,
        end_month: 12,
        price_increase: priceIncrease / 100,
        salary_increase: salaryIncrease / 100,
        unplanned_absence: 0.05,
        hy_working_hours: workingHours,
        other_expense: otherExpense,
        office_overrides: {} // TODO: Add lever-specific overrides
      };

      const results = await simulationApi.runSimulation(params);
      setSimulationResults(results);
      
      message.success('Simulation completed successfully!');
      
      // Set active year to first year if not set
      if (!activeYear && results.years) {
        const firstYear = Object.keys(results.years)[0];
        if (firstYear) {
          setActiveYear(firstYear);
        }
      }
      
    } catch (err) {
      setError('Simulation failed');
      message.error('Failed to run simulation');
      console.error('Simulation error:', err);
    } finally {
      setSimulationRunning(false);
    }
  };

  const tableColumns = [
    {
      title: 'Office/Segment/Profile',
      dataIndex: 'office',
      key: 'office',
    },
    {
      title: 'Office Journey',
      dataIndex: 'office_journey',
      key: 'office_journey',
    },
    {
      title: 'FTE',
      dataIndex: 'fte',
      key: 'fte',
    },
    {
      title: 'Delta',
      dataIndex: 'delta',
      key: 'delta',
    },
    {
      title: 'Price',
      dataIndex: 'price',
      key: 'price',
    },
    {
      title: 'Salary',
      dataIndex: 'salary',
      key: 'salary',
    },
    {
      title: 'YTD Change',
      dataIndex: 'ytdChange',
      key: 'ytdChange',
    }
  ];

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Back Navigation */}
      <div style={{ marginBottom: '16px' }}>
        <Link to="/lab">
          <Button type="link" style={{ padding: 0, fontSize: '14px' }}>
            ← Back to Simulation Lab v1
          </Button>
        </Link>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert
          message="Error"
          description={error}
          type="error"
          showIcon
          closable
          onClose={() => setError(null)}
          style={{ marginBottom: '16px' }}
        />
      )}

      {/* Simulation Levers Card */}
      <Card 
        title="Simulation Levers" 
        style={{ marginBottom: '16px' }}
      >
        <Row gutter={16} align="middle" style={{ marginBottom: 16 }}>
          <Col span={6}>
            <Text strong>Lever Type</Text>
            <Select
              style={{ width: '100%', marginTop: '4px' }}
              placeholder="Select lever"
              value={selectedLevers[0]}
              onChange={(value) => setSelectedLevers([value])}
            >
              {LEVERS.map(l => <Select.Option key={l.key} value={l.key}>{l.label}</Select.Option>)}
            </Select>
          </Col>
          <Col span={6}>
            <Text strong>Levels</Text>
            <Select
              mode="multiple"
              style={{ width: '100%', marginTop: '4px' }}
              placeholder="Select levels"
              value={selectedLevels}
              onChange={setSelectedLevels}
            >
              {LEVELS.map(lv => <Select.Option key={lv} value={lv}>{lv}</Select.Option>)}
            </Select>
          </Col>
          <Col span={6}>
            <Text strong>Value (%)</Text>
            <InputNumber
              style={{ width: '100%', marginTop: '4px' }}
              placeholder="Enter percentage"
              min={0}
              max={selectedLevers.includes('utr') ? 100 : 100}
              step={0.1}
              value={leverValue}
              onChange={v => setLeverValue(v ?? 0)}
              suffix="%"
            />
          </Col>
          <Col span={6}>
            <Text strong>Apply to</Text>
            <Select
              style={{ width: '100%', marginTop: '4px' }}
              value={selectedTimePeriod}
              onChange={setSelectedTimePeriod}
            >
              <Select.Option value="monthly">Monthly</Select.Option>
              <Select.Option value="half-year">Half-Yearly</Select.Option>
              <Select.Option value="yearly">Yearly</Select.Option>
            </Select>
          </Col>
        </Row>

        {/* Office Selection Row */}
        <Row gutter={16} align="middle">
          <Col span={8}>
            <Checkbox
              checked={applyToAllOffices}
              onChange={e => {
                setApplyToAllOffices(e.target.checked);
                if (e.target.checked) {
                  setSelectedOfficeJourney('');
                  setSelectedOffices([]);
                }
              }}
            >
              Apply to all offices
            </Checkbox>
          </Col>
          {!applyToAllOffices && (
            <>
              <Col span={8}>
                <Text strong>Office Journey</Text>
                <Select
                  style={{ width: '100%', marginTop: '4px' }}
                  value={selectedOfficeJourney}
                  onChange={(value) => {
                    setSelectedOfficeJourney(value);
                    if (value) setSelectedOffices([]);
                  }}
                  placeholder="Select journey type"
                  allowClear
                >
                  <Select.Option value="New Office">New Office (0-24 FTE)</Select.Option>
                  <Select.Option value="Emerging Office">Emerging Office (25-199 FTE)</Select.Option>
                  <Select.Option value="Established Office">Established Office (200-499 FTE)</Select.Option>
                  <Select.Option value="Mature Office">Mature Office (500+ FTE)</Select.Option>
                </Select>
              </Col>
              {!selectedOfficeJourney && (
                <Col span={8}>
                  <Text strong>Specific Offices</Text>
                  <Select
                    mode="multiple"
                    style={{ width: '100%', marginTop: '4px' }}
                    placeholder="Select offices"
                    value={selectedOffices}
                    onChange={setSelectedOffices}
                  >
                    {officeOptions.map(office => <Select.Option key={office.value} value={office.value}>{office.label}</Select.Option>)}
                  </Select>
                </Col>
              )}
            </>
          )}
        </Row>
      </Card>

      {/* Simulation Scope Card */}
      <Card 
        title="Simulation Scope" 
        style={{ marginBottom: '16px' }}
      >
        {/* Duration Selection */}
        <Row gutter={16} align="middle" style={{ marginBottom: 16 }}>
          <Col span={12}>
            <Text strong>Simulation Duration</Text>
            <Input.Group compact style={{ marginTop: '4px' }}>
              <InputNumber
                style={{ width: '60%' }}
                value={simulationDuration}
                onChange={(value) => setSimulationDuration(value || 1)}
                step={1}
                min={1}
                max={120}
              />
              <Select
                style={{ width: '40%' }}
                value={selectedDurationUnit}
                onChange={setSelectedDurationUnit}
              >
                <Select.Option value="months">Months</Select.Option>
                <Select.Option value="half-years">Half-Years</Select.Option>
                <Select.Option value="years">Years</Select.Option>
              </Select>
            </Input.Group>
            <Text type="secondary" style={{ fontSize: '11px' }}>
              {(() => {
                const totalMonths = selectedDurationUnit === 'years' ? simulationDuration * 12 : 
                                  selectedDurationUnit === 'half-years' ? simulationDuration * 6 : 
                                  simulationDuration;
                const endYear = 2025 + Math.ceil(totalMonths / 12) - 1;
                return totalMonths <= 12 ? '2025' : `2025-${endYear}`;
              })()}
            </Text>
          </Col>
        </Row>


      </Card>

      {/* Economic Parameters Card */}
      <Card 
        title="Economic Parameters" 
        style={{ marginBottom: '24px' }}
      >
        <Row gutter={[16, 16]}>
          <Col span={6}>
            <Text strong>Price Increase (%)</Text>
            <InputNumber
              style={{ width: '100%', marginTop: '4px' }}
              value={priceIncrease}
              onChange={(value) => setPriceIncrease(value || 0)}
              suffix="%"
              step={0.1}
              min={0}
              max={100}
            />
          </Col>
          <Col span={6}>
            <Text strong>Salary Increase (%)</Text>
            <InputNumber
              style={{ width: '100%', marginTop: '4px' }}
              value={salaryIncrease}
              onChange={(value) => setSalaryIncrease(value || 0)}
              suffix="%"
              step={0.1}
              min={0}
              max={100}
            />
          </Col>
          <Col span={6}>
            <Text strong>Working Hours</Text>
            <InputNumber
              style={{ width: '100%', marginTop: '4px' }}
              value={workingHours}
              onChange={(value) => setWorkingHours(value || 0)}
              step={0.1}
              min={0}
            />
          </Col>
          <Col span={6}>
            <Text strong>Other Expense</Text>
            <InputNumber
              style={{ width: '100%', marginTop: '4px' }}
              value={otherExpense}
              onChange={(value) => setOtherExpense(value || 0)}
              formatter={value => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
              step={1000}
              min={0}
            />
          </Col>
        </Row>
      </Card>

      {/* Action Buttons */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={12}>
          <Button 
            type="primary" 
            size="large"
            block
            icon={simulationRunning ? <LoadingOutlined /> : <RocketOutlined />}
            loading={simulationRunning}
            onClick={handleRunSimulation}
            disabled={configLoading}
          >
            {simulationRunning ? 'Running Simulation...' : 'Run Simulation'}
          </Button>
        </Col>
        <Col span={6}>
          <Button size="large" block>Load Config Data</Button>
        </Col>
        <Col span={6}>
          <Button size="large" block>Reset to Config</Button>
        </Col>
      </Row>

      {/* Simulation Results Card */}
      <Card title="Simulation Results">
        {/* Year Selector Tabs */}
        {availableYears.length > 0 ? (
          <Tabs activeKey={activeYear} onChange={setActiveYear} style={{ marginBottom: '24px' }}>
            {availableYears.map(year => (
              <TabPane tab={`Year ${year}`} key={year} />
            ))}
          </Tabs>
        ) : (
          <div style={{ 
            textAlign: 'center', 
            padding: '40px', 
            color: '#8c8c8c',
            marginBottom: '24px'
          }}>
            <Text type="secondary">
              No simulation results available. Run a simulation to see data.
            </Text>
          </div>
        )}

        {/* KPI Cards Grid */}
        <Row gutter={[16, 16]} style={{ marginBottom: '32px' }}>
          {kpiData.map((kpi: any, index: number) => (
            <Col xs={24} sm={12} lg={6} key={index}>
              <Card 
                size="small" 
                style={{ 
                  textAlign: 'center', 
                  height: '140px',
                  border: '1px solid #f0f0f0',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between'
                }}
                bodyStyle={{ 
                  padding: '16px 12px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  height: '100%'
                }}
              >
                {kpi.title && (
                  <>
                    <div>
                      <Text 
                        type="secondary" 
                        style={{ 
                          fontSize: '11px', 
                          display: 'block',
                          marginBottom: '8px',
                          lineHeight: '1.2'
                        }}
                      >
                        {kpi.title}
                      </Text>
                      <div style={{ 
                        fontSize: '22px', 
                        fontWeight: '600', 
                        lineHeight: '1.1',
                        marginBottom: '4px'
                      }}>
                        {kpi.value}
                      </div>
                      <div style={{ 
                        fontSize: '11px', 
                        color: '#8c8c8c',
                        marginBottom: '8px'
                      }}>
                        {kpi.unit} <span style={{ color: '#52c41a', fontWeight: '500' }}>{kpi.trend}</span>
                      </div>
                    </div>
                    {/* Simple sparkline placeholder */}
                    <div style={{ 
                      height: '16px', 
                      background: 'linear-gradient(90deg, #f0f0f0 0%, #d9d9d9 100%)', 
                      borderRadius: '2px',
                      marginTop: 'auto'
                    }}></div>
                  </>
                )}
                {index === 7 && (
                  <div style={{ 
                    height: '100%', 
                    background: '#f5f5f5', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    borderRadius: '4px'
                  }}>
                    <Text type="secondary" style={{ fontSize: '12px' }}>Chart Placeholder</Text>
                  </div>
                )}
              </Card>
            </Col>
          ))}
        </Row>

        {/* Seniority Analysis Panel */}
        <Collapse style={{ marginBottom: '24px' }}>
          <Collapse.Panel header="📊 Seniority Analysis" key="seniority">
            <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
              {/* Seniority KPIs */}
                             <Col xs={24} sm={12} lg={6}>
                 <Card size="small" style={{ textAlign: 'center', height: '120px' }}>
                   <Text type="secondary" style={{ fontSize: '12px' }}>Junior Level Growth</Text>
                   <div style={{ fontSize: '20px', fontWeight: '600', margin: '8px 0' }}>
                     {seniorityKPIs?.juniorGrowth || 'N/A'}
                   </div>
                   <Text type="secondary" style={{ fontSize: '11px', color: '#52c41a' }}>↗ YoY</Text>
                 </Card>
               </Col>
               <Col xs={24} sm={12} lg={6}>
                 <Card size="small" style={{ textAlign: 'center', height: '120px' }}>
                   <Text type="secondary" style={{ fontSize: '12px' }}>Senior Level Growth</Text>
                   <div style={{ fontSize: '20px', fontWeight: '600', margin: '8px 0' }}>
                     {seniorityKPIs?.seniorGrowth || 'N/A'}
                   </div>
                   <Text type="secondary" style={{ fontSize: '11px', color: '#52c41a' }}>↗ YoY</Text>
                 </Card>
               </Col>
               <Col xs={24} sm={12} lg={6}>
                 <Card size="small" style={{ textAlign: 'center', height: '120px' }}>
                   <Text type="secondary" style={{ fontSize: '12px' }}>Progression Rate</Text>
                   <div style={{ fontSize: '20px', fontWeight: '600', margin: '8px 0' }}>
                     {seniorityKPIs?.progressionRate || 'N/A'}
                   </div>
                   <Text type="secondary" style={{ fontSize: '11px', color: '#1890ff' }}>→ Stable</Text>
                 </Card>
               </Col>
               <Col xs={24} sm={12} lg={6}>
                 <Card size="small" style={{ textAlign: 'center', height: '120px' }}>
                   <Text type="secondary" style={{ fontSize: '12px' }}>Seniority Ratio</Text>
                   <div style={{ fontSize: '20px', fontWeight: '600', margin: '8px 0' }}>
                     {seniorityKPIs?.seniorityRatio || 'N/A'}
                   </div>
                   <Text type="secondary" style={{ fontSize: '11px', color: '#faad14' }}>⚡ Jr:Sr</Text>
                 </Card>
               </Col>
            </Row>

            {/* Seniority Distribution Table */}
            <div style={{ marginBottom: '16px' }}>
              <Title level={5}>Seniority Distribution by Office</Title>
              <Table
                size="small"
                pagination={false}
                columns={[
                  { title: 'Office', dataIndex: 'office', key: 'office' },
                  { title: 'Total', dataIndex: 'total', key: 'total', render: (value) => <span style={{ fontWeight: '600' }}>{value}</span> },
                  { title: 'A Level', dataIndex: 'levelA', key: 'levelA' },
                  { title: 'AC Level', dataIndex: 'levelAC', key: 'levelAC' },
                  { title: 'C Level', dataIndex: 'levelC', key: 'levelC' },
                  { title: 'SrC Level', dataIndex: 'levelSrC', key: 'levelSrC' },
                  { title: 'AM Level', dataIndex: 'levelAM', key: 'levelAM' },
                  { title: 'M Level', dataIndex: 'levelM', key: 'levelM' },
                  { title: 'SrM Level', dataIndex: 'levelSrM', key: 'levelSrM' },
                  { title: 'PiP Level', dataIndex: 'levelPiP', key: 'levelPiP' },
                  { title: 'Operations', dataIndex: 'operations', key: 'operations' },
                  { title: 'Non-debit Ratio', dataIndex: 'nonDebitRatio', key: 'nonDebitRatio', render: (value) => <span style={{ fontWeight: '500' }}>{value}%</span> }
                ]}
                                 dataSource={seniorityData}
              />
            </div>
          </Collapse.Panel>
        </Collapse>

        {/* Detailed Data Analysis Table */}
        <div>
          <Title level={4} style={{ marginBottom: '16px' }}>
            <TableOutlined style={{ marginRight: '8px' }} />
            Detailed Data Analysis
          </Title>
          <Table
            columns={tableColumns}
            dataSource={tableData}
            pagination={false}
            size="small"
            bordered
            expandable={{
              expandedRowRender: (record) => (
                <div style={{ padding: '16px' }}>
                  <Row gutter={16}>
                    <Col span={12}>
                      <Text strong>Role Breakdown:</Text>
                      <div style={{ marginTop: '8px' }}>
                        <Text type="secondary">Consultant: {record.consultantFTE || 0} FTE</Text><br/>
                        <Text type="secondary">Sales: {record.salesFTE || 0} FTE</Text><br/>
                        <Text type="secondary">Recruitment: {record.recruitmentFTE || 0} FTE</Text><br/>
                        <Text type="secondary">Operations: {record.operationsFTE || 0} FTE</Text>
                      </div>
                    </Col>
                    <Col span={12}>
                      <Text strong>Financial Details:</Text>
                      <div style={{ marginTop: '8px' }}>
                        <Text type="secondary">Revenue: {record.revenue || 'N/A'}</Text><br/>
                        <Text type="secondary">Gross Margin: {record.grossMargin || 'N/A'}</Text><br/>
                        <Text type="secondary">EBITDA: {record.ebitda || 'N/A'}</Text><br/>
                        <Text type="secondary">Journey: {record.office_journey || 'N/A'}</Text>
                      </div>
                    </Col>
                  </Row>
                </div>
              ),
              rowExpandable: (record) => record.office !== 'No data', // Only expand rows with data
            }}
          />
        </div>
      </Card>
    </div>
  );
};

export default SimulationLabV2; 