import React, { useEffect, useState } from 'react';
import { Table, Card, Select, Typography, Collapse, Row, Col, Tag } from 'antd';

const { Option } = Select;
const { Title, Text } = Typography;
const { Panel } = Collapse;

interface Office {
  name: string;
  total_fte: number;
  journey: string;
  levels: {
    [key: string]: {
      total: number;
      price: number;
      salary: number;
    };
  };
  operations: {
    total: number;
    price: number;
    salary: number;
  };
  metrics: {
    journey_percentages: { [key: string]: number };
    non_debit_ratio: number | null;
    growth: number;
    recruitment: number;
    churn: number;
  }[];
}

export default function AllOffices() {
  const [offices, setOffices] = useState<Office[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedRowKeys, setExpandedRowKeys] = useState<string[]>([]);

  useEffect(() => {
    fetch('/api/offices/config')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch offices');
        return res.json();
      })
      .then(data => {
        console.log('[DEBUG] Data received from /api/offices:', data);
        setOffices(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const calculateDelta = (office: Office) => {
    if (!office.metrics || office.metrics.length < 2) return 0;
    const current = office.metrics[office.metrics.length - 1];
    return current.growth;
  };

  const columns = [
    {
      title: 'Office',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <Text strong>{text}</Text>,
    },
    {
      title: 'Journey',
      dataIndex: 'journey',
      key: 'journey',
      render: (journey: string) => <Tag>{journey}</Tag>,
    },
    {
      title: 'Total FTE',
      dataIndex: 'total_fte',
      key: 'total_fte',
    },
    {
      title: 'Delta',
      key: 'delta',
      render: (_: any, office: Office) => {
        const delta = calculateDelta(office);
        return <span style={{ color: delta > 0 ? '#52c41a' : delta < 0 ? '#ff4d4f' : '#bfbfbf' }}>{delta > 0 ? '+' : ''}{delta}</span>;
      },
    },
    {
      title: 'Growth %',
      key: 'growth',
      render: (_: any, office: Office) => {
        const growth = office.metrics?.[office.metrics.length - 1]?.growth || 0;
        return <span style={{ color: growth > 0 ? '#52c41a' : growth < 0 ? '#ff4d4f' : '#bfbfbf' }}>{growth > 0 ? '+' : ''}{growth.toFixed(1)}%</span>;
      },
    },
    {
      title: 'Non-Debit Ratio',
      key: 'ndr',
      render: (_: any, office: Office) => {
        const ndr = office.metrics?.[office.metrics.length - 1]?.non_debit_ratio;
        return ndr !== null && ndr !== undefined ? ndr.toFixed(2) : 'N/A';
      },
    },
  ];

  return (
    <Card title={<Title level={4} style={{ margin: 0 }}>All Offices</Title>}>
      {/* Filters */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col><Select defaultValue="Company" style={{ width: 120 }}><Option value="Company">Company</Option></Select></Col>
        <Col><Select defaultValue="Journey" style={{ width: 120 }}><Option value="Journey">Journey</Option></Select></Col>
        <Col><Select defaultValue="Sort: Name" style={{ width: 140 }}>
          <Option value="Sort: Name">Sort: Name</Option>
          <Option value="Sort: Headcount">Sort: Headcount</Option>
          <Option value="Sort: Growth">Sort: Growth</Option>
        </Select></Col>
      </Row>
      {error && <Text type="danger">{error}</Text>}
      <Table
        columns={columns}
        dataSource={offices}
        loading={loading}
        rowKey="name"
        expandable={{
          expandedRowRender: (office: Office) => (
            <div>
              <Title level={5} style={{ marginBottom: 8 }}>Level Breakdown</Title>
              <Row gutter={16} style={{ marginBottom: 8 }}>
                {Object.entries(office.levels).map(([level, data]) => (
                  <Col key={level} span={4}>
                    <Card size="small" style={{ marginBottom: 8 }}>
                      <Text strong>{level}</Text>: <Text>{data.total} FTE</Text>
                    </Card>
                  </Col>
                ))}
              </Row>
              <Title level={5} style={{ marginBottom: 8 }}>Operations</Title>
              <Text>Total: {office.operations.total} FTE</Text>
            </div>
          ),
          expandedRowKeys,
          onExpand: (expanded, record) => {
            setExpandedRowKeys(expanded ? [record.name] : []);
          },
        }}
        pagination={{ pageSize: 8 }}
      />
    </Card>
  );
} 