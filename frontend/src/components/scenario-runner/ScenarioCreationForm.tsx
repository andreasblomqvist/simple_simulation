import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Radio, Select, Typography, Space, message, Spin } from 'antd';
import type { ScenarioDefinition, TimeRange, OfficeName } from '../../types/unified-data-structures';
import { scenarioApi } from '../../services/scenarioApi';

const { Title } = Typography;
const { TextArea } = Input;
const { Option } = Select;

interface ScenarioCreationFormProps {
  scenario?: ScenarioDefinition;
  onNext: (result: { scenarioId: string; scenario: ScenarioDefinition }) => void;
  onBack: () => void;
  loading?: boolean;
}

const ScenarioCreationForm: React.FC<ScenarioCreationFormProps> = ({ scenario, onNext, onBack, loading = false }) => {
  const [form] = Form.useForm();
  const [officeScope, setOfficeScope] = useState<'group' | 'individual'>('group');
  const [availableOffices, setAvailableOffices] = useState<OfficeName[]>([]);
  const [loadingOffices, setLoadingOffices] = useState(true);

  useEffect(() => {
    loadAvailableOffices();
  }, []);

  useEffect(() => {
    // Use scenario directly - no nested definition structure
    const scenarioData = scenario;
    if (scenarioData && scenarioData.time_range) {
      form.setFieldsValue({
        name: scenarioData.name,
        description: scenarioData.description || '',
        startYear: scenarioData.time_range.start_year,
        endYear: scenarioData.time_range.end_year,
        startMonth: scenarioData.time_range.start_month,
        endMonth: scenarioData.time_range.end_month,
        officeScope: scenarioData.office_scope && scenarioData.office_scope.includes('Group') ? 'group' : 'individual',
        offices: scenarioData.office_scope ? scenarioData.office_scope.filter(office => office !== 'Group') : [],
      });
      setOfficeScope(scenarioData.office_scope && scenarioData.office_scope.includes('Group') ? 'group' : 'individual');
    }
  }, [scenario, form]);

  const loadAvailableOffices = async () => {
    try {
      setLoadingOffices(true);
      const offices = await scenarioApi.getAvailableOffices();
      setAvailableOffices(offices);
    } catch (error) {
      message.error('Failed to load available offices: ' + (error as Error).message);
    } finally {
      setLoadingOffices(false);
    }
  };

  const handleFinish = async (values: any) => {
    const timeRange: TimeRange = {
      start_year: values.startYear,
      start_month: values.startMonth || 1,
      end_year: values.endYear,
      end_month: values.endMonth || 12,
    };

    const officeScopeList: OfficeName[] = officeScope === 'group' 
      ? ['Group'] 
      : values.offices || [];

    const scenarioDefinition: ScenarioDefinition = {
      name: values.name,
      description: values.description,
      time_range: timeRange,
      office_scope: officeScopeList,
      levers: {}, // Will be populated in the next step
      economic_params: {}, // Will be populated in the next step
    };

    // Don't create scenario yet, just pass the data to next step
    onNext({ scenarioId: '', scenario: scenarioDefinition });
  };

  if (loadingOffices) {
    return (
      <div style={{ padding: '50px 0' }}>
        <div style={{ textAlign: 'center' }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>Loading available offices...</div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <Title level={4} style={{ margin: 0, marginBottom: 24 }}>Create New Scenario</Title>
      <Form
        form={form}
        layout="vertical"
        onFinish={handleFinish}
        initialValues={{
          name: '',
          description: '',
          startYear: 2025,
          endYear: 2027,
          startMonth: 1,
          endMonth: 12,
          officeScope: 'group',
          offices: [],
        }}
      >
        <Form.Item
          label="Scenario Name"
          name="name"
          rules={[{ required: true, message: 'Please enter a scenario name' }]}
        >
          <Input placeholder="e.g. Oslo Growth Plan 2025-2027" />
        </Form.Item>
        
        <Form.Item
          label="Description"
          name="description"
        >
          <TextArea rows={2} placeholder="Describe the scenario (optional)" />
        </Form.Item>
        
        <Space style={{ display: 'flex', marginBottom: 16 }}>
          <Form.Item
            label="Start Year"
            name="startYear"
            rules={[{ required: true, message: 'Start year required' }]}
            style={{ marginRight: 16 }}
          >
            <Input type="number" min={2020} max={2100} style={{ width: 100 }} />
          </Form.Item>
          <Form.Item
            label="Start Month"
            name="startMonth"
            rules={[{ required: true, message: 'Start month required' }]}
            style={{ marginRight: 16 }}
          >
            <Select style={{ width: 100 }}>
              {Array.from({ length: 12 }, (_, i) => (
                <Option key={i + 1} value={i + 1}>{i + 1}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            label="End Year"
            name="endYear"
            rules={[{ required: true, message: 'End year required' }]}
            style={{ marginRight: 16 }}
          >
            <Input type="number" min={2020} max={2100} style={{ width: 100 }} />
          </Form.Item>
          <Form.Item
            label="End Month"
            name="endMonth"
            rules={[{ required: true, message: 'End month required' }]}
          >
            <Select style={{ width: 100 }}>
              {Array.from({ length: 12 }, (_, i) => (
                <Option key={i + 1} value={i + 1}>{i + 1}</Option>
              ))}
            </Select>
          </Form.Item>
        </Space>
        
        <Form.Item label="Office Scope" name="officeScope">
          <Radio.Group
            onChange={e => setOfficeScope(e.target.value)}
            value={officeScope}
          >
            <Radio value="group">Group (all offices)</Radio>
            <Radio value="individual">Individual Offices</Radio>
          </Radio.Group>
        </Form.Item>
        
        {officeScope === 'individual' && (
          <Form.Item
            label="Select Offices"
            name="offices"
            rules={[{ required: true, message: 'Select at least one office' }]}
          >
            <Select mode="multiple" placeholder="Choose offices">
              {availableOffices.filter(office => office !== 'Group').map(office => (
                <Option key={office} value={office}>{office}</Option>
              ))}
            </Select>
          </Form.Item>
        )}
        
        <Form.Item style={{ marginTop: 24 }}>
          <Button onClick={onBack} style={{ marginRight: 8 }}>Back</Button>
          <Button type="primary" htmlType="submit" loading={loading}>
            Next: Configure Baseline Input
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
};

export default ScenarioCreationForm; 