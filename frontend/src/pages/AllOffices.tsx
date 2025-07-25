import React, { useEffect, useState } from 'react';
import { Table, Card, Select, Typography, Collapse, Row, Col, Tag } from 'antd';
import { useNavigate } from 'react-router-dom';

const { Option } = Select;
const { Title, Text } = Typography;
const { Panel } = Collapse;

interface Office {
  id: string;
  name: string;
  total_fte: number;
  journey: string;
  roles: Record<string, Record<string, any>>;
  economic_parameters?: {
    cost_of_living: number;
    market_multiplier: number;
    tax_rate: number;
  };
}

export function AllOffices() {
  const navigate = useNavigate();
  const [offices, setOffices] = useState<Office[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedRowKeys, setExpandedRowKeys] = useState<string[]>([]);

  useEffect(() => {
    fetch('/api/offices')
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

  const columns = [
    {
      title: 'Office',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: Office) => (
        <Text 
          strong 
          style={{ 
            cursor: 'pointer', 
            color: '#1890ff',
            textDecoration: 'underline'
          }}
          onClick={() => navigate(`/offices/${record.id}`)}
          onMouseEnter={(e) => {
            e.currentTarget.style.color = '#40a9ff';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.color = '#1890ff';
          }}
        >
          {text}
        </Text>
      ),
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
      title: 'Cost of Living',
      key: 'cost_of_living',
      render: (_: any, office: Office) => {
        const col = office.economic_parameters?.cost_of_living;
        return col ? col.toFixed(2) : 'N/A';
      },
    },
    {
      title: 'Market Multiplier',
      key: 'market_multiplier',
      render: (_: any, office: Office) => {
        const mm = office.economic_parameters?.market_multiplier;
        return mm ? mm.toFixed(2) : 'N/A';
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
        rowKey="id"
        expandable={{
          expandedRowRender: (office: Office) => (
            <div>
              <Title level={5} style={{ marginBottom: 8 }}>Role Breakdown</Title>
              <Row gutter={16} style={{ marginBottom: 8 }}>
                {Object.entries(office.roles).map(([role, levels]) => (
                  <Col key={role} span={8}>
                    <Card size="small" style={{ marginBottom: 8 }}>
                      <Text strong>{role}</Text>
                      <div>
                        {Object.entries(levels).map(([level, data]) => (
                          <div key={level}>
                            <Text>{level}: {data.fte || 0} FTE</Text>
                          </div>
                        ))}
                      </div>
                    </Card>
                  </Col>
                ))}
              </Row>
            </div>
          ),
          expandedRowKeys,
          onExpand: (expanded, record) => {
            setExpandedRowKeys(expanded ? [record.id] : []);
          },
        }}
        pagination={{ pageSize: 8 }}
      />
    </Card>
  );
} 