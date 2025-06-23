import React, { useState, useEffect } from 'react';
import { Card, Typography, Divider, Button, Spin, Alert, Form, theme, Select } from 'antd';
import { PlayCircleOutlined } from '@ant-design/icons';
import { 
  SimulationParametersForm, 
  KPIDisplays, 
  OfficeDetails,
  QuickScenarios 
} from '../components/insights';

const { Title, Paragraph, Text } = Typography;
const { Option } = Select;
const { useToken } = theme;

const InsightsTab: React.FC = () => {
  const { token } = useToken();
  const [loading, setLoading] = useState(false);
  const [simulationData, setSimulationData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedOffice, setSelectedOffice] = useState<string>('Stockholm');
  const [selectedYear, setSelectedYear] = useState<string>('2025');
  const [form] = Form.useForm();
  
  // Level action state
  const [levelActions, setLevelActions] = useState<{
    churn: Array<{level: string, rate: number}>,
    recruitment: Array<{level: string, rate: number}>
  }>({
    churn: [],
    recruitment: []
  });

  // Action builder state
  const [selectedAction, setSelectedAction] = useState<string>('');
  const [selectedLevels, setSelectedLevels] = useState<string[]>([]);
  const [selectedRate, setSelectedRate] = useState<number>(0);

  // Default simulation parameters
  const defaultParams = {
    start_year: 2025,
    start_month: 1,
    end_year: 2025,
    end_month: 12,
    price_increase: 0.03, // 3%
    salary_increase: 0.025, // 2.5%
    unplanned_absence: 0.16, // 16%
    hy_working_hours: 166.4,
    other_expense: 19000000,
    utr_adjustment: 0.0, // 0% UTR adjustment
    // Level-specific levers as JSON objects
    level_specific_churn: {}, // e.g., {"AM": 0.03, "M": 0.04}
    level_specific_recruitment: {}, // e.g., {"A": 0.04, "AC": 0.03}
  };

  useEffect(() => {
    form.setFieldsValue(defaultParams);
  }, [form]);

  const runSimulation = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const values = await form.validateFields();
      
      const response = await fetch('/api/simulation/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(values),
      });

      if (!response.ok) {
        throw new Error(`Simulation failed: ${response.statusText}`);
      }

      const data = await response.json();
      setSimulationData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (value: number) => {
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M SEK`;
    } else if (value >= 1000) {
      return `${(value / 1000).toFixed(0)}K SEK`;
    }
    return `${value.toFixed(0)} SEK`;
  };

  return (
    <div style={{ padding: 24 }}>
      <Title level={2} style={{ color: token.colorPrimary }}>
        Simulation Insights
      </Title>
      <Paragraph>
        Raw simulation results from the backend engine - no frontend calculations or transformations.
      </Paragraph>
      <Divider />

      {/* Simulation Parameters */}
      <SimulationParametersForm
        form={form}
        levelActions={levelActions}
        setLevelActions={setLevelActions}
        selectedAction={selectedAction}
        setSelectedAction={setSelectedAction}
        selectedLevels={selectedLevels}
        setSelectedLevels={setSelectedLevels}
        selectedRate={selectedRate}
        setSelectedRate={setSelectedRate}
        defaultParams={defaultParams}
      />

      {/* Quick Scenarios */}
      <QuickScenarios
        form={form}
        defaultParams={defaultParams}
        setLevelActions={setLevelActions}
      />

      <div style={{ marginBottom: 24, textAlign: 'center' }}>
        <Button 
          type="primary" 
          icon={<PlayCircleOutlined />} 
          onClick={runSimulation}
          loading={loading}
          size="large"
        >
          Run Simulation
        </Button>
      </div>

      {error && (
        <Alert
          message="Simulation Error"
          description={error}
          type="error"
          style={{ marginBottom: 24 }}
        />
      )}

      {loading && (
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>Running simulation...</div>
        </div>
      )}

      {simulationData && !loading && (
        <>
          {/* Year Selector - Always at the top */}
          {simulationData?.years && Object.keys(simulationData.years).length > 0 && (
            <Card size="small" style={{ marginBottom: 24, textAlign: 'center' }}>
              <Text strong style={{ marginRight: 16 }}>📅 Select Year to View:</Text>
              <Select 
                value={selectedYear} 
                onChange={setSelectedYear}
                style={{ width: 120 }}
                size="large"
              >
                {Object.keys(simulationData.years).sort().map(year => (
                  <Option key={year} value={year}>{year}</Option>
                ))}
              </Select>
              <Text type="secondary" style={{ marginLeft: 16 }}>
                Viewing data for {selectedYear}
              </Text>
            </Card>
          )}
          
          <KPIDisplays 
            simulationData={simulationData}
            formatNumber={formatNumber}
            selectedYear={selectedYear}
            setSelectedYear={setSelectedYear}
          />
          
          <OfficeDetails
            simulationData={simulationData}
            selectedYear={selectedYear}
            selectedOffice={selectedOffice}
            setSelectedOffice={setSelectedOffice}
          />
          
          <Card title="Raw Data (Debug)" style={{ marginTop: 24 }}>
            <Text>
              <pre style={{ fontSize: '12px', maxHeight: '400px', overflow: 'auto' }}>
                {JSON.stringify(simulationData, null, 2)}
              </pre>
            </Text>
          </Card>
        </>
      )}
    </div>
  );
};

export default InsightsTab; 