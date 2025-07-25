import React, { useState, useEffect } from 'react';
import { Card, Input, Select, DatePicker, Button, Row, Col, Table, InputNumber, Tabs, Space, Typography, Divider, Form } from 'antd';
import { PlusOutlined, PlayCircleOutlined, SaveOutlined, DeleteOutlined } from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import dayjs from 'dayjs';
import type { 
  ScenarioDefinition, 
  TimeRange, 
  EconomicParameters, 
  Levers, 
  BaselineInput,
  MonthlyValues,
  LevelData,
  LeveledRoleData
} from '../../types/unified-data-structures';
import { DEFAULT_ECONOMIC_PARAMETERS } from '../../types/unified-data-structures';
import { scenarioApi } from '../../services/scenarioApi';
import SimulationResultsDisplay from './SimulationResultsDisplay';
import { showMessage } from '../../utils/message';

const { Option } = Select;
const { RangePicker } = DatePicker;
const { TextArea } = Input;
const { Title, Text } = Typography;

// Level definitions for the simulation
const LEVELS = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P'];
const OFFICE_OPTIONS = ['Group', 'Stockholm', 'Munich', 'Amsterdam', 'Berlin', 'Copenhagen', 'Frankfurt', 'Hamburg', 'Helsinki', 'Oslo', 'Zurich', 'Colombia'];

// Default scenario definition
const DEFAULT_SCENARIO: ScenarioDefinition = {
  name: '',
  description: '',
  time_range: {
    start_year: 2025,
    start_month: 1,
    end_year: 2027,
    end_month: 12
  },
  office_scope: ['Group'],
  levers: {
    recruitment: { A: 1.0, AC: 1.0, C: 1.0, SrC: 1.0, AM: 1.0, M: 1.0, SrM: 1.0, Pi: 1.0, P: 1.0 },
    churn: { A: 1.0, AC: 1.0, C: 1.0, SrC: 1.0, AM: 1.0, M: 1.0, SrM: 1.0, Pi: 1.0, P: 1.0 },
    progression: { A: 1.0, AC: 1.0, C: 1.0, SrC: 1.0, AM: 1.0, M: 1.0, SrM: 1.0, Pi: 1.0, P: 1.0 }
  },
  economic_params: DEFAULT_ECONOMIC_PARAMETERS,
  baseline_input: {
    global: {
      recruitment: {
        Consultant: {
          levels: {
            A: { recruitment: { values: { '202501': 20 } }, churn: { values: { '202501': 2 } } },
            AC: { recruitment: { values: { '202501': 8 } }, churn: { values: { '202501': 4 } } },
            C: { recruitment: { values: { '202501': 4 } }, churn: { values: { '202501': 7 } } },
            SrC: { recruitment: { values: { '202501': 1 } }, churn: { values: { '202501': 7 } } },
            AM: { recruitment: { values: { '202501': 1 } }, churn: { values: { '202501': 9 } } },
            M: { recruitment: { values: { '202501': 0 } }, churn: { values: { '202501': 1 } } },
            SrM: { recruitment: { values: { '202501': 0 } }, churn: { values: { '202501': 0 } } },
            Pi: { recruitment: { values: { '202501': 0 } }, churn: { values: { '202501': 0 } } },
            P: { recruitment: { values: { '202501': 0 } }, churn: { values: { '202501': 0 } } }
          }
        }
      },
      churn: {
        Consultant: {
          levels: {
            A: { recruitment: { values: { '202501': 20 } }, churn: { values: { '202501': 2 } } },
            AC: { recruitment: { values: { '202501': 8 } }, churn: { values: { '202501': 4 } } },
            C: { recruitment: { values: { '202501': 4 } }, churn: { values: { '202501': 7 } } },
            SrC: { recruitment: { values: { '202501': 1 } }, churn: { values: { '202501': 7 } } },
            AM: { recruitment: { values: { '202501': 1 } }, churn: { values: { '202501': 9 } } },
            M: { recruitment: { values: { '202501': 0 } }, churn: { values: { '202501': 1 } } },
            SrM: { recruitment: { values: { '202501': 0 } }, churn: { values: { '202501': 0 } } },
            Pi: { recruitment: { values: { '202501': 0 } }, churn: { values: { '202501': 0 } } },
            P: { recruitment: { values: { '202501': 0 } }, churn: { values: { '202501': 0 } } }
          }
        }
      }
    }
  },
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString()
};

interface ScenarioBuilderProps {
  onCancel?: () => void;
  onComplete?: () => void;
}

const ScenarioBuilder: React.FC<ScenarioBuilderProps> = ({ onCancel, onComplete }) => {
  const { id } = useParams<{ id?: string }>();
  const navigate = useNavigate();
  const [scenario, setScenario] = useState<ScenarioDefinition>(DEFAULT_SCENARIO);
  const [loading, setLoading] = useState(false);
  const [simulating, setSimulating] = useState(false);
  const [simulationResult, setSimulationResult] = useState<any>(null);

  // Load existing scenario if editing
  useEffect(() => {
    if (id) {
      loadScenario(id);
    }
  }, [id]);

  const loadScenario = async (scenarioId: string) => {
    try {
      setLoading(true);
      const loadedScenario = await scenarioApi.getScenario(scenarioId);
      
      // Ensure the scenario has all required fields with defaults
      const safeScenario: ScenarioDefinition = {
        ...DEFAULT_SCENARIO,
        ...loadedScenario,
        time_range: {
          ...DEFAULT_SCENARIO.time_range,
          ...loadedScenario.time_range
        },
        levers: {
          ...DEFAULT_SCENARIO.levers,
          ...loadedScenario.levers
        },
        economic_params: {
          ...DEFAULT_SCENARIO.economic_params,
          ...loadedScenario.economic_params
        },
        baseline_input: {
          ...DEFAULT_SCENARIO.baseline_input,
          ...loadedScenario.baseline_input
        }
      };
      
      setScenario(safeScenario);
    } catch (error) {
      showMessage.error('Failed to load scenario');
      console.error('Load scenario error:', error);
      // Fall back to default scenario if loading fails
      setScenario(DEFAULT_SCENARIO);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      
      if (id) {
        await scenarioApi.updateScenario(id, scenario);
        showMessage.success('Scenario updated successfully');
      } else {
        const newId = await scenarioApi.createScenario(scenario);
        showMessage.success('Scenario created successfully');
        navigate(`/scenario-runner/edit/${newId}`);
      }
      
      if (onComplete) onComplete();
    } catch (error) {
      showMessage.error('Failed to save scenario');
      console.error('Save error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRunSimulation = async () => {
    try {
      setSimulating(true);
      setSimulationResult(null);
      
      // Validate scenario before running
      if (!scenario.name.trim()) {
        showMessage.error('Please enter a scenario name');
        return;
      }
      
      console.log('Running simulation with scenario:', scenario);
      const result = await scenarioApi.runScenarioDefinition(scenario);
      console.log('Simulation result:', result);
      
      if (result.status === 'success') {
        setSimulationResult(result);
        showMessage.success('Simulation completed successfully');
        console.log('Simulation result structure:', {
          status: result.status,
          executionTime: result.execution_time,
          hasResults: !!result.results,
          resultsType: typeof result.results,
          resultsKeys: result.results ? Object.keys(result.results) : 'no results',
          firstFewChars: result.results ? JSON.stringify(result.results).substring(0, 200) : 'no results'
        });
      } else {
        showMessage.error(`Simulation failed: ${result.error_message || 'Unknown error'}`);
        console.error('Simulation failed:', result);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      showMessage.error(`Failed to run simulation: ${errorMessage}`);
      console.error('Simulation error:', error);
    } finally {
      setSimulating(false);
    }
  };

  const handleDelete = async () => {
    if (!id) return;
    
    try {
      await scenarioApi.deleteScenario(id);
      showMessage.success('Scenario deleted successfully');
      navigate('/scenario-runner');
    } catch (error) {
      showMessage.error('Failed to delete scenario');
    }
  };

  // Helper function to get baseline value for a level
  const getBaselineValue = (level: string, type: 'recruitment' | 'churn'): number => {
    try {
      const roleData = scenario.baseline_input.global[type]?.Consultant;
      if (roleData && 'levels' in roleData) {
        const levelData = roleData.levels[level];
        if (levelData) {
          const values = levelData[type].values;
          const firstMonth = Object.values(values)[0];
          return firstMonth || 0;
        }
      }
    } catch (error) {
      console.error(`Error getting baseline ${type} for level ${level}:`, error);
    }
    return 0;
  };

  // Helper function to sanitize monthly values
  const sanitizeMonthlyValue = (value: any): number => {
    if (value === null || value === undefined || value === '' || isNaN(value)) {
      return 0;
    }
    const numValue = Number(value);
    return isNaN(numValue) ? 0 : Math.max(0, numValue);
  };

  // Helper function to set baseline value for a level
  const setBaselineValue = (level: string, type: 'recruitment' | 'churn', value: number) => {
    setScenario(prev => {
      const newScenario = { ...prev };
      
      // Ensure the structure exists
      if (!newScenario.baseline_input.global[type]) {
        newScenario.baseline_input.global[type] = {};
      }
      if (!newScenario.baseline_input.global[type].Consultant) {
        newScenario.baseline_input.global[type].Consultant = { levels: {} };
      }
      if (!newScenario.baseline_input.global[type].Consultant.levels[level]) {
        newScenario.baseline_input.global[type].Consultant.levels[level] = {
          recruitment: { values: { '202501': 0 } },
          churn: { values: { '202501': 0 } }
        };
      }
      
      // Set the value for all months in the time range
      const months = [];
      for (let year = prev.time_range.start_year; year <= prev.time_range.end_year; year++) {
        const startMonth = year === prev.time_range.start_year ? prev.time_range.start_month : 1;
        const endMonth = year === prev.time_range.end_year ? prev.time_range.end_month : 12;
        
        for (let month = startMonth; month <= endMonth; month++) {
          months.push(`${year}${month.toString().padStart(2, '0')}`);
        }
      }
      
      months.forEach(month => {
        const roleData = newScenario.baseline_input.global[type].Consultant;
        if ('levels' in roleData && roleData.levels[level]) {
          roleData.levels[level][type].values[month] = sanitizeMonthlyValue(value);
        }
      });
      
      return newScenario;
    });
  };

  // Baseline table columns
  const baselineColumns = [
    { title: 'Level', dataIndex: 'level', key: 'level', width: 80 },
    {
      title: 'Recruitment',
      dataIndex: 'recruitment',
      key: 'recruitment',
      render: (value: number, record: any) => (
        <InputNumber
          min={0}
          value={getBaselineValue(record.level, 'recruitment')}
          onChange={(val) => setBaselineValue(record.level, 'recruitment', sanitizeMonthlyValue(val))}
        />
      )
    },
    {
      title: 'Churn',
      dataIndex: 'churn',
      key: 'churn',
      render: (value: number, record: any) => (
        <InputNumber
          min={0}
          value={getBaselineValue(record.level, 'churn')}
          onChange={(val) => setBaselineValue(record.level, 'churn', sanitizeMonthlyValue(val))}
        />
      )
    }
  ];

  // Levers table columns
  const leversColumns = [
    { title: 'Level', dataIndex: 'level', key: 'level', width: 80 },
    {
      title: 'Recruitment Multiplier',
      dataIndex: 'recruitment',
      key: 'recruitment',
      render: (value: number, record: any) => (
        <InputNumber
          min={0}
          step={0.1}
          value={scenario.levers?.recruitment?.[record.level] || 1.0}
          onChange={(val) => {
            const sanitizedValue = sanitizeMonthlyValue(val);
            setScenario(prev => ({
              ...prev,
              levers: {
                ...prev.levers,
                recruitment: { ...prev.levers.recruitment, [record.level]: sanitizedValue || 1.0 }
              }
            }));
          }}
        />
      )
    },
    {
      title: 'Churn Multiplier',
      dataIndex: 'churn',
      key: 'churn',
      render: (value: number, record: any) => (
        <InputNumber
          min={0}
          step={0.1}
          value={scenario.levers?.churn?.[record.level] || 1.0}
          onChange={(val) => {
            const sanitizedValue = sanitizeMonthlyValue(val);
            setScenario(prev => ({
              ...prev,
              levers: {
                ...prev.levers,
                churn: { ...prev.levers.churn, [record.level]: sanitizedValue || 1.0 }
              }
            }));
          }}
        />
      )
    },
    {
      title: 'Progression Multiplier',
      dataIndex: 'progression',
      key: 'progression',
      render: (value: number, record: any) => (
        <InputNumber
          min={0}
          step={0.1}
          value={scenario.levers?.progression?.[record.level] || 1.0}
          onChange={(val) => {
            const sanitizedValue = sanitizeMonthlyValue(val);
            setScenario(prev => ({
              ...prev,
              levers: {
                ...prev.levers,
                progression: { ...prev.levers.progression, [record.level]: sanitizedValue || 1.0 }
              }
            }));
          }}
        />
      )
    }
  ];

  // Prepare table data
  const tableData = LEVELS.map(level => ({
    key: level,
    level,
    recruitment: getBaselineValue(level, 'recruitment'),
    churn: getBaselineValue(level, 'churn')
  }));

  const leversData = LEVELS.map(level => ({
    key: level,
    level,
    recruitment: scenario.levers?.recruitment?.[level] || 1.0,
    churn: scenario.levers?.churn?.[level] || 1.0,
    progression: scenario.levers?.progression?.[level] || 1.0
  }));

  return (
    <div style={{ padding: 24, maxWidth: 1200, margin: '0 auto' }}>
      <Card>
        <div style={{ marginBottom: 24 }}>
          <Title level={2}>
            {id ? 'Edit Scenario' : 'Create New Scenario'}
          </Title>
          
          {/* Scenario Basics */}
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={12}>
              <Text strong>Scenario Name</Text>
              <Input
                placeholder="Enter scenario name"
                value={scenario.name}
                onChange={(e) => setScenario(prev => ({ ...prev, name: e.target.value }))}
                style={{ marginTop: 4 }}
              />
            </Col>
            <Col span={12}>
              <Text strong>Office Scope</Text>
              <Select
                mode="multiple"
                placeholder="Select offices"
                value={scenario.office_scope}
                onChange={(value) => setScenario(prev => ({ ...prev, office_scope: value }))}
                style={{ width: '100%', marginTop: 4 }}
              >
                {OFFICE_OPTIONS.map(office => (
                  <Option key={office} value={office}>{office}</Option>
                ))}
              </Select>
            </Col>
          </Row>

          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={12}>
              <Text strong>Description</Text>
              <TextArea
                placeholder="Enter scenario description"
                value={scenario.description}
                onChange={(e) => setScenario(prev => ({ ...prev, description: e.target.value }))}
                rows={3}
                style={{ marginTop: 4 }}
              />
            </Col>
            <Col span={12}>
              <Text strong>Time Range</Text>
              <RangePicker
                picker="month"
                value={[
                  dayjs(`${scenario.time_range?.start_year || 2025}-${(scenario.time_range?.start_month || 1).toString().padStart(2, '0')}`),
                  dayjs(`${scenario.time_range?.end_year || 2027}-${(scenario.time_range?.end_month || 12).toString().padStart(2, '0')}`)
                ]}
                onChange={(dates) => {
                  if (dates && dates[0] && dates[1]) {
                    setScenario(prev => ({
                      ...prev,
                      time_range: {
                        start_year: dates[0]!.year(),
                        start_month: dates[0]!.month() + 1,
                        end_year: dates[1]!.year(),
                        end_month: dates[1]!.month() + 1
                      }
                    }));
                  }
                }}
                style={{ width: '100%', marginTop: 4 }}
              />
            </Col>
          </Row>

          <Divider />

          {/* Data Tables */}
          <Tabs 
            defaultActiveKey="baseline"
            items={[
              {
                key: 'baseline',
                label: 'Baseline Values',
                children: (
                  <div>
                    <Text type="secondary">
                      Set the baseline monthly values for recruitment and churn at each level.
                    </Text>
                    <Table
                      columns={baselineColumns}
                      dataSource={tableData}
                      pagination={false}
                      size="small"
                      style={{ marginTop: 16 }}
                    />
                  </div>
                ),
              },
              {
                key: 'levers',
                label: 'Scenario Levers',
                children: (
                  <div>
                    <Text type="secondary">
                      Adjust multipliers to see how changes affect the simulation. Values above 1.0 increase, below 1.0 decrease.
                    </Text>
                    <Table
                      columns={leversColumns}
                      dataSource={leversData}
                      pagination={false}
                      size="small"
                      style={{ marginTop: 16 }}
                    />
                  </div>
                ),
              },
              {
                key: 'economic',
                label: 'Economic Parameters',
                children: (
                  <div>
                    <Text type="secondary">
                      Configure economic parameters that affect the simulation calculations.
                    </Text>
                    <Row gutter={16} style={{ marginTop: 16 }}>
                      <Col span={12}>
                        <Form.Item label="Working Hours per Month">
                          <InputNumber
                            min={0}
                            step={0.1}
                            value={scenario.economic_params?.working_hours_per_month || 160.0}
                            onChange={(val) => {
                              setScenario(prev => ({
                                ...prev,
                                economic_params: {
                                  ...prev.economic_params,
                                  working_hours_per_month: val || 160.0
                                }
                              }));
                            }}
                            style={{ width: '100%' }}
                          />
                        </Form.Item>
                      </Col>
                      <Col span={12}>
                        <Form.Item label="Employment Cost Rate (%)">
                          <InputNumber
                            min={0}
                            max={100}
                            step={0.1}
                            value={scenario.economic_params?.employment_cost_rate ? scenario.economic_params.employment_cost_rate * 100 : 30}
                            onChange={(val) => {
                              setScenario(prev => ({
                                ...prev,
                                economic_params: {
                                  ...prev.economic_params,
                                  employment_cost_rate: (val || 0) / 100
                                }
                              }));
                            }}
                            addonAfter="%"
                            style={{ width: '100%' }}
                          />
                        </Form.Item>
                      </Col>
                    </Row>
                    <Row gutter={16}>
                      <Col span={12}>
                        <Form.Item label="Unplanned Absence (%)">
                          <InputNumber
                            min={0}
                            max={100}
                            step={0.1}
                            value={scenario.economic_params?.unplanned_absence ? scenario.economic_params.unplanned_absence * 100 : 5}
                            onChange={(val) => {
                              setScenario(prev => ({
                                ...prev,
                                economic_params: {
                                  ...prev.economic_params,
                                  unplanned_absence: (val || 0) / 100
                                }
                              }));
                            }}
                            addonAfter="%"
                            style={{ width: '100%' }}
                          />
                        </Form.Item>
                      </Col>
                      <Col span={12}>
                        <Form.Item label="Other Expense (SEK/month)">
                          <InputNumber
                            min={0}
                            step={1000000}
                            value={scenario.economic_params?.other_expense || 1000000}
                            onChange={(val) => {
                              setScenario(prev => ({
                                ...prev,
                                economic_params: {
                                  ...prev.economic_params,
                                  other_expense: val || 1000000
                                }
                              }));
                            }}
                            formatter={(value) => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                            parser={(value) => Number(value!.replace(/\$\s?|(,*)/g, ''))}
                            style={{ width: '100%' }}
                          />
                        </Form.Item>
                      </Col>
                    </Row>
                  </div>
                ),
              },
            ]}
          />

          {/* Action Buttons */}
          <div style={{ marginTop: 24, textAlign: 'right' }}>
            <Space>
              {id && (
                <Button 
                  danger 
                  icon={<DeleteOutlined />}
                  onClick={handleDelete}
                >
                  Delete
                </Button>
              )}
              {onCancel && (
                <Button onClick={onCancel}>
                  Cancel
                </Button>
              )}
              <Button 
                type="primary" 
                icon={<SaveOutlined />}
                onClick={handleSave}
                loading={loading}
              >
                Save Scenario
              </Button>
              <Button 
                type="primary" 
                icon={<PlayCircleOutlined />}
                onClick={handleRunSimulation}
                loading={simulating}
                style={{ backgroundColor: '#52c41a', borderColor: '#52c41a' }}
              >
                Run Simulation
              </Button>
            </Space>
          </div>

          {/* Simulation Results */}
          {simulationResult && (
            <div style={{ marginTop: 24 }}>
              <SimulationResultsDisplay result={simulationResult} />
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

export default ScenarioBuilder;