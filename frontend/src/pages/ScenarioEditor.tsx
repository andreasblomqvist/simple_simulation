import React, { useState, useEffect, useRef } from 'react';
import {
  Card,
  Button,
  message,
  Tabs,
  Space,
  Typography,
  Divider,
  Row,
  Col,
  Select,
  Input,
  Form,
  Spin,
  Alert,
  Modal,
  Popconfirm,
  Tag,
  Tooltip,
  Badge
} from 'antd';
import {
  PlusOutlined,
  PlayCircleOutlined,
  SaveOutlined,
  CopyOutlined,
  DeleteOutlined,
  EyeOutlined,
  EditOutlined,
  DownloadOutlined,
  ReloadOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import type { TabsProps } from 'antd';

import type {
  ScenarioDefinition,
  ScenarioResponse,
  ScenarioListItem,
  ScenarioId,
  OfficeName,
  SimulationResults
} from '../types/unified-data-structures';
import { scenarioApi } from '../services/scenarioApi';
import { normalizeBaselineInput } from '../utils/normalizeBaselineInput';

// Import existing components
import ScenarioCreationForm from '../components/scenario-runner/ScenarioCreationForm';
import BaselineInputGrid from '../components/scenario-runner/BaselineInputGrid';
import ScenarioLevers from '../components/scenario-runner/ScenarioLevers';
import type { ScenarioLeversRef } from '../components/scenario-runner/ScenarioLevers';
import ResultsTable from '../components/scenario-runner/ResultsTable';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

interface ScenarioEditorProps {
  scenarioId?: string;
}

function validateScenario(scenario: any): string[] {
  const errors: string[] = [];
  // Handle both direct scenario and nested definition structure
  const scenarioData = scenario?.definition || scenario;
  if (!scenarioData.name || typeof scenarioData.name !== 'string' || !scenarioData.name.trim()) {
    errors.push('Scenario name is required.');
  }
  if (!scenarioData.time_range) {
    errors.push('Time range is required.');
  } else {
    const { start_year, start_month, end_year, end_month } = scenarioData.time_range;
    if (
      typeof start_year !== 'number' ||
      typeof start_month !== 'number' ||
      typeof end_year !== 'number' ||
      typeof end_month !== 'number'
    ) {
      errors.push('Time range fields must be numbers.');
    }
  }
  if (!Array.isArray(scenarioData.office_scope) || scenarioData.office_scope.length === 0) {
    errors.push('At least one office must be selected.');
  }
  if (!scenarioData.levers || typeof scenarioData.levers !== 'object') {
    errors.push('Levers are required.');
  }
  if (!scenarioData.baseline_input || typeof scenarioData.baseline_input !== 'object') {
    errors.push('Baseline input is required.');
  }
  return errors;
}

const ScenarioEditor: React.FC<ScenarioEditorProps> = ({ scenarioId: propScenarioId }) => {
  const navigate = useNavigate();
  const { id: urlScenarioId } = useParams<{ id?: string }>();
  const scenarioId = propScenarioId || urlScenarioId;

  // State management
  const [scenarios, setScenarios] = useState<ScenarioListItem[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<ScenarioDefinition | null>(null);
  const [scenario, setScenario] = useState<Partial<ScenarioDefinition>>({});
  const [baselineData, setBaselineData] = useState<any>(null);
  const [simulationResult, setSimulationResult] = useState<ScenarioResponse | null>(null);
  const [simulationError, setSimulationError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [simulating, setSimulating] = useState(false);
  const [activeTab, setActiveTab] = useState('editor');
  const [availableOffices, setAvailableOffices] = useState<OfficeName[]>([]);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  // Refs for child components
  const baselineGridRef = useRef<any>(null);
  const leversRef = useRef<ScenarioLeversRef>(null);

  // Load initial data
  useEffect(() => {
    loadScenarios();
    loadAvailableOffices();
    if (scenarioId) {
      console.log('[DEBUG][ScenarioEditor] Loading scenario with ID:', scenarioId);
      loadScenario(scenarioId);
    }
  }, [scenarioId]);

  const loadScenarios = async () => {
    try {
      const scenariosList = await scenarioApi.listScenarios();
      setScenarios(scenariosList);
    } catch (error) {
      message.error('Failed to load scenarios');
    }
  };

  const loadAvailableOffices = async () => {
    try {
      const offices = await scenarioApi.getAvailableOffices();
      setAvailableOffices(offices);
    } catch (error) {
      message.error('Failed to load offices');
    }
  };

  const loadScenario = async (id: string) => {
    setLoading(true);
    try {
      console.log('[DEBUG][ScenarioEditor] loadScenario called with ID:', id);
      const scenarioData = await scenarioApi.getScenario(id);
      // Handle both direct scenario and nested definition structure
      const actualScenario = scenarioData?.definition || scenarioData;
      setScenario(actualScenario);
      setSelectedScenario(scenarioData);
      setBaselineData(actualScenario.baseline_input || {});
      console.log('[DEBUG][ScenarioEditor] Scenario loaded:', scenarioData);
    } catch (error) {
      message.error('Failed to load scenario');
    } finally {
      setLoading(false);
    }
  };

  // Scenario management functions
  const handleCreateNew = () => {
    setScenario({});
    setSelectedScenario(null);
    setBaselineData({});
    setSimulationResult(null);
    setSimulationError(null);
    setActiveTab('editor');
  };

  const handleSelectScenario = (id: string) => {
    console.log('[DEBUG][ScenarioEditor] handleSelectScenario called with ID:', id);
    loadScenario(id);
    setActiveTab('editor');
  };

  const handleSaveScenario = async () => {
    if (saving) return;
    setSaving(true);
    setValidationErrors([]);
    try {
      // Always get latest data from grid ref
      let baselineInput = {};
      if (baselineGridRef.current?.getCurrentData) {
        baselineInput = baselineGridRef.current.getCurrentData();
        baselineInput = normalizeBaselineInput(baselineInput);
      }
      let leversData = {};
      if (leversRef.current?.getCurrentData) {
        leversData = leversRef.current.getCurrentData();
      }
      const scenarioWithData = {
        ...scenario,
        baseline_input: baselineInput,
        levers: leversData
      } as ScenarioDefinition;
      // Debug log
      console.log('[DEBUG][handleSaveScenario] scenarioWithData:', scenarioWithData);
      // Validate before sending
      const errors = validateScenario(scenarioWithData);
      if (errors.length > 0) {
        setValidationErrors(errors);
        setSaving(false);
        return;
      }
      if (selectedScenario?.id) {
        await scenarioApi.updateScenario(selectedScenario.id, scenarioWithData);
        message.success('Scenario updated successfully!');
      } else {
        const newId = await scenarioApi.createScenario(scenarioWithData);
        message.success('Scenario created successfully!');
        setSelectedScenario({ ...scenarioWithData, id: newId });
      }
      await loadScenarios(); // Refresh list
    } catch (error) {
      message.error('Failed to save scenario: ' + (error as Error).message);
    } finally {
      setSaving(false);
    }
  };

  const handleDuplicateScenario = async () => {
    if (!selectedScenario) return;
    
    const duplicatedScenario = {
      ...selectedScenario,
      name: `${selectedScenario.name} (Copy)`,
      description: selectedScenario.description ? `${selectedScenario.description} (Copy)` : undefined,
      id: undefined
    };
    
    setScenario(duplicatedScenario);
    setSelectedScenario(null);
    setActiveTab('editor');
    message.info('Scenario duplicated - edit and save to create new version');
  };

  const handleDeleteScenario = async () => {
    if (!selectedScenario?.id) return;
    
    try {
      await scenarioApi.deleteScenario(selectedScenario.id);
      message.success('Scenario deleted successfully!');
      await loadScenarios();
      handleCreateNew();
    } catch (error) {
      message.error('Failed to delete scenario');
    }
  };

  const handleRunSimulation = async () => {
    setSimulating(true);
    setSimulationError(null);
    setSimulationResult(null);
    
    try {
      // Always get latest data from grid ref
      let baselineInput = {};
      if (baselineGridRef.current?.getCurrentData) {
        baselineInput = baselineGridRef.current.getCurrentData();
        baselineInput = normalizeBaselineInput(baselineInput);
      }

      let leversData = {};
      if (leversRef.current?.getCurrentData) {
        leversData = leversRef.current.getCurrentData();
      }

      const scenarioWithData = {
        ...scenario,
        baseline_input: baselineInput,
        levers: leversData
      } as ScenarioDefinition;
      // Debug log
      console.log('[DEBUG][handleRunSimulation] scenarioWithData:', scenarioWithData);

      const result = await scenarioApi.runScenarioDefinition(scenarioWithData);
      
      if (result.status === 'success') {
        setSimulationResult(result);
        setActiveTab('results');
        message.success('Simulation completed successfully!');
      } else {
        setSimulationError(result.error_message || 'Simulation failed');
        message.error('Simulation failed');
      }
    } catch (error) {
      setSimulationError((error as Error).message);
      message.error('Simulation failed: ' + (error as Error).message);
    } finally {
      setSimulating(false);
    }
  };

  const handleExportResults = async () => {
    if (!simulationResult?.scenario_id) return;
    
    try {
      const blob = await scenarioApi.exportScenarioResults(simulationResult.scenario_id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `scenario-results-${simulationResult.scenario_id}.xlsx`;
      a.click();
      window.URL.revokeObjectURL(url);
      message.success('Results exported successfully!');
    } catch (error) {
      message.error('Failed to export results');
    }
  };

  // Form handlers
  const handleDetailsNext = (data: { scenarioId: string; scenario: ScenarioDefinition }) => {
    setScenario(data.scenario);
  };

  const handleBaselineNext = (data: any) => {
    setBaselineData(data);
  };

  // Tab configuration
  const tabItems: TabsProps['items'] = [
    {
      key: 'editor',
      label: (
        <span>
          <EditOutlined />
          Editor
        </span>
      ),
      children: (
        <div style={{ padding: '24px 0' }}>
          <Row gutter={[24, 24]}>
            <Col span={16}>
              <Card title="Scenario Configuration" size="small">
                <ScenarioCreationForm
                  scenario={scenario as ScenarioDefinition}
                  onNext={handleDetailsNext}
                  onBack={() => {}}
                />
              </Card>
              
              <Card title="Baseline Input" size="small" style={{ marginTop: 16 }}>
                <BaselineInputGrid onNext={handleBaselineNext} ref={baselineGridRef} />
              </Card>
              
              <Card title="Simulation Levers" size="small" style={{ marginTop: 16 }}>
                <ScenarioLevers onNext={() => {}} onBack={() => {}} ref={leversRef} />
              </Card>
            </Col>
            
            <Col span={8}>
              <Card title="Actions" size="small">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Button
                    type="primary"
                    icon={<SaveOutlined />}
                    loading={saving}
                    onClick={handleSaveScenario}
                    block
                  >
                    Save Scenario
                  </Button>
                  
                  {!(selectedScenario?.id || scenario?.id) ? (
                    <Tooltip title="Please save the scenario before running simulation.">
                      <span>
                        <Button icon={<PlayCircleOutlined />} block disabled>Run Simulation</Button>
                      </span>
                    </Tooltip>
                  ) : (
                    <Button
                      icon={<PlayCircleOutlined />}
                      loading={simulating}
                      onClick={handleRunSimulation}
                      block
                    >
                      Run Simulation
                    </Button>
                  )}
                  
                  {selectedScenario && (
                    <>
                      <Button
                        icon={<CopyOutlined />}
                        onClick={handleDuplicateScenario}
                        block
                      >
                        Duplicate
                      </Button>
                      
                      <Popconfirm
                        title="Delete Scenario"
                        description="Are you sure you want to delete this scenario?"
                        onConfirm={handleDeleteScenario}
                        okText="Yes"
                        cancelText="No"
                      >
                        <Button
                          danger
                          icon={<DeleteOutlined />}
                          block
                        >
                          Delete
                        </Button>
                      </Popconfirm>
                    </>
                  )}
                </Space>
              </Card>
              
              {validationErrors.length > 0 && (
                <Alert
                  message="Please fix the following errors before saving:"
                  description={<ul>{validationErrors.map((err, i) => <li key={i}>{err}</li>)}</ul>}
                  type="error"
                  showIcon
                  style={{ marginBottom: 16 }}
                />
              )}
              
              {simulationError && (
                <Card title="Simulation Error" size="small" style={{ marginTop: 16 }}>
                  <Alert
                    message="Simulation Failed"
                    description={simulationError}
                    type="error"
                    showIcon
                  />
                </Card>
              )}
            </Col>
          </Row>
        </div>
      ),
    },
    {
      key: 'results',
      label: (
        <span>
          <EyeOutlined />
          Results
          {simulationResult && <Badge count="✓" style={{ backgroundColor: '#52c41a' }} />}
        </span>
      ),
      disabled: !(selectedScenario?.id || scenario?.id),
      children: (
        <div style={{ padding: '24px 0' }}>
          {simulationResult ? (
            <ResultsTable scenarioId={
              simulationResult.scenario_id || selectedScenario?.id || scenario?.id || ''
            } />
          ) : (
            <Card>
              <Text>Please save the scenario before viewing results.</Text>
            </Card>
          )}
        </div>
      ),
    },
    {
      key: 'scenarios',
      label: (
        <span>
          <ReloadOutlined />
          Scenarios ({scenarios.length})
        </span>
      ),
      children: (
        <div style={{ padding: '24px 0' }}>
          <Card title="Available Scenarios">
            <Space direction="vertical" style={{ width: '100%' }}>
              {scenarios.map((scenario) => (
                <Card
                  key={scenario.id}
                  size="small"
                  style={{
                    cursor: 'pointer',
                    border: selectedScenario?.id === scenario.id ? '2px solid #1890ff' : '1px solid #d9d9d9'
                  }}
                  onClick={() => handleSelectScenario(scenario.id)}
                >
                  <Row justify="space-between" align="middle">
                    <Col>
                      <Title level={5} style={{ margin: 0 }}>{scenario.name}</Title>
                      <Text type="secondary">{scenario.description}</Text>
                      <br />
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        Created: {new Date(scenario.created_at).toLocaleDateString()}
                      </Text>
                    </Col>
                    <Col>
                      <Space>
                        <Tag color="blue">{scenario.office_scope?.length || 0} offices</Tag>
                        <Tag color="green">
                          {scenario.time_range?.start_year}-{scenario.time_range?.start_month} to {scenario.time_range?.end_year}-{scenario.time_range?.end_month}
                        </Tag>
                      </Space>
                    </Col>
                  </Row>
                </Card>
              ))}
              
              {scenarios.length === 0 && (
                <Text type="secondary">No scenarios found. Create your first scenario to get started.</Text>
              )}
            </Space>
          </Card>
        </div>
      ),
    },
  ];

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
          <Col>
            <Title level={2} style={{ margin: 0 }}>
              Scenario Editor
            </Title>
            <Text type="secondary">
              {selectedScenario ? `Editing: ${selectedScenario.name}` : 'Create a new scenario'}
            </Text>
          </Col>
          <Col>
            <Space>
              <Button icon={<PlusOutlined />} onClick={handleCreateNew}>
                New Scenario
              </Button>
              <Button onClick={() => navigate('/scenario-runner')}>
                Back to Runner
              </Button>
            </Space>
          </Col>
        </Row>

        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={tabItems}
          type="card"
        />
      </Card>
    </div>
  );
};

export default ScenarioEditor; 