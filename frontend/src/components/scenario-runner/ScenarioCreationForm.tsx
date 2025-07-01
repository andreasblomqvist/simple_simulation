import React, { useState } from 'react';
import { Card, Form, Input, Button, Radio, Select, Typography, Space } from 'antd';

const { Title } = Typography;
const { TextArea } = Input;
const { Option } = Select;

const mockOffices = [
  { label: 'Stockholm', value: 'stockholm' },
  { label: 'Oslo', value: 'oslo' },
  { label: 'Munich', value: 'munich' },
  { label: 'Copenhagen', value: 'copenhagen' },
];

interface ScenarioCreationFormProps {
  onNext: (values: any) => void;
  onBack: () => void;
}

const ScenarioCreationForm: React.FC<ScenarioCreationFormProps> = ({ onNext, onBack }) => {
  const [form] = Form.useForm();
  const [officeScope, setOfficeScope] = useState<'group' | 'individual'>('group');

  const handleFinish = (values: any) => {
    onNext(values);
  };

  return (
    <Card title={<Title level={4} style={{ margin: 0 }}>Create New Scenario</Title>} style={{ maxWidth: 1000, margin: '0 auto' }}>
      <Form
        form={form}
        layout="vertical"
        onFinish={handleFinish}
        initialValues={{
          name: '',
          description: '',
          startYear: 2025,
          endYear: 2027,
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
          rules={[{ required: true, message: 'Please enter a description' }]}
        >
          <TextArea rows={2} placeholder="Describe the scenario..." />
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
            label="End Year"
            name="endYear"
            rules={[{ required: true, message: 'End year required' }]}
          >
            <Input type="number" min={2020} max={2100} style={{ width: 100 }} />
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
              {mockOffices.map(o => (
                <Option key={o.value} value={o.value}>{o.label}</Option>
              ))}
            </Select>
          </Form.Item>
        )}
        <Form.Item style={{ marginTop: 24 }}>
          <Button onClick={onBack} style={{ marginRight: 8 }}>Back</Button>
          <Button type="primary" htmlType="submit">Next: Baseline Input</Button>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default ScenarioCreationForm; 