import React, { useEffect, useState } from 'react';
import { Table, Card, Typography } from 'antd';
import type { Office } from '../types';

const { Title } = Typography;

const Offices: React.FC = () => {
  const [offices, setOffices] = useState<Office[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOffices = async () => {
      try {
        const response = await fetch('/api/offices');
        const data = await response.json();
        setOffices(data);
      } catch (error) {
        console.error('Error fetching offices:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchOffices();
  }, []);

  const columns = [
    {
      title: 'Office',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Total FTE',
      dataIndex: 'total_fte',
      key: 'total_fte',
    },
    {
      title: 'Levels',
      dataIndex: 'levels',
      key: 'levels',
      render: (levels: Record<string, any>) => (
        <ul>
          {Object.entries(levels).map(([level, data]) => (
            <li key={level}>
              {level}: {data.total} FTE
            </li>
          ))}
        </ul>
      ),
    },
  ];

  return (
    <div>
      <Title level={2}>Offices</Title>
      <Card>
        <Table
          dataSource={offices}
          columns={columns}
          loading={loading}
          rowKey="name"
        />
      </Card>
    </div>
  );
};

export default Offices; 