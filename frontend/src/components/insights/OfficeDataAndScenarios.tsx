import React from 'react';
import { Row, Col, Card, Typography, Select, Button, Table } from 'antd';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

interface QuickScenariosProps {
  form: any;
  defaultParams: any;
  setLevelActions: (actions: any) => void;
}

interface OfficeDetailsProps {
  simulationData: any;
  selectedYear: string;
  selectedOffice: string;
  setSelectedOffice: (office: string) => void;
}

export const QuickScenarios: React.FC<QuickScenariosProps> = ({
  form,
  defaultParams,
  setLevelActions
}) => {
  return (
    <Card 
      title="Quick Scenarios" 
      size="small" 
      style={{ marginBottom: 16 }}
    >
      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', justifyContent: 'center' }}>
        <Button 
          size="small" 
          onClick={() => {
            form.setFieldsValue({
              ...defaultParams,
              recruitment_rate: 0.0,
              churn_rate: 0.0,
              utr_adjustment: 0.0,
              progression_rate: 0.0
            });
          }}
        >
          🔄 Reset to Baseline
        </Button>
        <Button 
          size="small" 
          onClick={() => {
            // Growth scenario via level actions
            setLevelActions({
              churn: [],
              recruitment: [
                { level: 'A', rate: 3.0 },
                { level: 'AC', rate: 2.0 },
                { level: 'C', rate: 1.0 }
              ]
            });
          }}
        >
          📈 Growth Scenario
        </Button>
        <Button 
          size="small" 
          onClick={() => {
            // Conservative scenario via level actions
            setLevelActions({
              churn: [
                { level: 'M', rate: 2.0 },
                { level: 'SrM', rate: 2.5 }
              ],
              recruitment: [
                { level: 'A', rate: 1.0 }
              ]
            });
          }}
        >
          📉 Conservative Scenario
        </Button>
        <Button 
          size="small" 
          onClick={() => {
            const current = form.getFieldsValue();
            form.setFieldsValue({
              ...current,
              utr_adjustment: 0.05, // +5% UTR
              price_increase: 0.05, // +5% prices
              salary_increase: 0.02 // +2% salaries
            });
          }}
        >
          💰 Profitability Focus
        </Button>
        <Button 
          size="small" 
          onClick={() => {
            // Set up seniority rebalance actions
            setLevelActions({
              churn: [
                { level: 'AM', rate: 3.0 },
                { level: 'M', rate: 4.0 },
                { level: 'SrM', rate: 5.0 },
                { level: 'PiP', rate: 6.0 }
              ],
              recruitment: [
                { level: 'A', rate: 4.0 },
                { level: 'AC', rate: 3.0 },
                { level: 'C', rate: 2.0 }
              ]
            });
          }}
        >
          🎯 Seniority Rebalance
        </Button>
      </div>
    </Card>
  );
};

const OfficeDetails: React.FC<OfficeDetailsProps> = ({
  simulationData,
  selectedYear,
  selectedOffice,
  setSelectedOffice
}) => {
  const renderOfficeData = () => {
    if (!simulationData?.years?.[selectedYear]?.offices) return null;

    const offices = simulationData.years[selectedYear].offices;
    const officeNames = Object.keys(offices);

    // Prepare table data for the selected office
    const getTableData = () => {
      if (!selectedOffice || !offices[selectedOffice]?.levels) return [];

      const officeData = offices[selectedOffice];
      const tableData: any[] = [];

      Object.entries(officeData.levels).forEach(([roleName, roleData]: [string, any]) => {
        if (typeof roleData === 'object' && !Array.isArray(roleData)) {
          // Hierarchical role (has levels like A, AC, C, etc.)
          Object.entries(roleData).forEach(([levelName, levelArray]: [string, any]) => {
            if (Array.isArray(levelArray) && levelArray.length > 0) {
              const yearData = levelArray.filter((month: any) => month.month.startsWith(selectedYear));
              if (yearData.length > 0) {
                // Get last month data for the year (December or latest available)
                const lastMonth = yearData[yearData.length - 1];
                
                // Calculate totals for the year
                const totalRecruited = yearData.reduce((sum: number, month: any) => sum + (month.recruited || 0), 0);
                const totalChurned = yearData.reduce((sum: number, month: any) => sum + (month.churned || 0), 0);
                const totalProgressedIn = yearData.reduce((sum: number, month: any) => sum + (month.progressed_in || 0), 0);
                const totalProgressedOut = yearData.reduce((sum: number, month: any) => sum + (month.progressed_out || 0), 0);
                const netChange = totalRecruited + totalProgressedIn - totalChurned - totalProgressedOut;

                tableData.push({
                  key: `${roleName}-${levelName}`,
                  role: roleName,
                  level: levelName,
                  currentFte: lastMonth.total || 0,
                  recruited: totalRecruited,
                  churned: totalChurned,
                  progressedIn: totalProgressedIn,
                  progressedOut: totalProgressedOut,
                  netChange: netChange,
                  hourlyRate: lastMonth.price ? `${Math.round(lastMonth.price)} SEK` : '-',
                  utr: lastMonth.utr ? `${Math.round(lastMonth.utr * 100)}%` : '-'
                });
              }
            }
          });
        } else if (Array.isArray(roleData) && roleData.length > 0) {
          // Flat role (like Operations)
          const yearData = roleData.filter((month: any) => month.month.startsWith(selectedYear));
          if (yearData.length > 0) {
            const lastMonth = yearData[yearData.length - 1];
            
            const totalRecruited = yearData.reduce((sum: number, month: any) => sum + (month.recruited || 0), 0);
            const totalChurned = yearData.reduce((sum: number, month: any) => sum + (month.churned || 0), 0);
            const totalProgressedIn = yearData.reduce((sum: number, month: any) => sum + (month.progressed_in || 0), 0);
            const totalProgressedOut = yearData.reduce((sum: number, month: any) => sum + (month.progressed_out || 0), 0);
            const netChange = totalRecruited + totalProgressedIn - totalChurned - totalProgressedOut;

            tableData.push({
              key: roleName,
              role: roleName,
              level: '-',
              currentFte: lastMonth.total || 0,
              recruited: totalRecruited,
              churned: totalChurned,
              progressedIn: totalProgressedIn,
              progressedOut: totalProgressedOut,
              netChange: netChange,
              hourlyRate: lastMonth.price ? `${Math.round(lastMonth.price)} SEK` : (lastMonth.salary ? `${Math.round(lastMonth.salary)} SEK/month` : '-'),
              utr: lastMonth.utr ? `${Math.round(lastMonth.utr * 100)}%` : '-'
            });
          }
        }
      });

      return tableData.sort((a, b) => {
        if (a.role !== b.role) return a.role.localeCompare(b.role);
        return a.level.localeCompare(b.level);
      });
    };

    const columns = [
      {
        title: 'Role',
        dataIndex: 'role',
        key: 'role',
        width: 120,
      },
      {
        title: 'Level',
        dataIndex: 'level',
        key: 'level',
        width: 80,
      },
      {
        title: 'Current FTE',
        dataIndex: 'currentFte',
        key: 'currentFte',
        width: 100,
        render: (value: number) => <Text strong>{value}</Text>
      },
      {
        title: 'Recruited',
        dataIndex: 'recruited',
        key: 'recruited',
        width: 90,
        render: (value: number) => <Text style={{ color: value > 0 ? '#52c41a' : undefined }}>+{value}</Text>
      },
      {
        title: 'Churned',
        dataIndex: 'churned',
        key: 'churned',
        width: 80,
        render: (value: number) => <Text style={{ color: value > 0 ? '#ff4d4f' : undefined }}>{value > 0 ? `-${value}` : value}</Text>
      },
      {
        title: 'Progressed In',
        dataIndex: 'progressedIn',
        key: 'progressedIn',
        width: 110,
        render: (value: number) => <Text style={{ color: value > 0 ? '#1890ff' : undefined }}>+{value}</Text>
      },
      {
        title: 'Progressed Out',
        dataIndex: 'progressedOut',
        key: 'progressedOut',
        width: 120,
        render: (value: number) => <Text style={{ color: value > 0 ? '#fa8c16' : undefined }}>{value > 0 ? `-${value}` : value}</Text>
      },
      {
        title: 'Net Change',
        dataIndex: 'netChange',
        key: 'netChange',
        width: 100,
        render: (value: number) => {
          const color = value > 0 ? '#52c41a' : value < 0 ? '#ff4d4f' : undefined;
          const sign = value > 0 ? '+' : '';
          return <Text strong style={{ color }}>{sign}{value}</Text>;
        }
      },
      {
        title: 'Rate',
        dataIndex: 'hourlyRate',
        key: 'hourlyRate',
        width: 120,
      },
      {
        title: 'UTR',
        dataIndex: 'utr',
        key: 'utr',
        width: 70,
      }
    ];

    const tableData = getTableData();
    const totalFte = tableData.reduce((sum, row) => sum + row.currentFte, 0);
    const totalRecruited = tableData.reduce((sum, row) => sum + row.recruited, 0);
    const totalChurned = tableData.reduce((sum, row) => sum + row.churned, 0);
    const totalProgressedIn = tableData.reduce((sum, row) => sum + row.progressedIn, 0);
    const totalProgressedOut = tableData.reduce((sum, row) => sum + row.progressedOut, 0);
    const totalNetChange = tableData.reduce((sum, row) => sum + row.netChange, 0);

    return (
      <Card title={`Office Details for ${selectedYear}`} style={{ marginBottom: 24 }}>
        <div style={{ marginBottom: 16 }}>
          <Text>Select Office: </Text>
          <Select 
            value={selectedOffice} 
            onChange={setSelectedOffice}
            style={{ width: 200, marginLeft: 8 }}
          >
            {officeNames.map(name => (
              <Option key={name} value={name}>{name}</Option>
            ))}
          </Select>
        </div>

        {selectedOffice && offices[selectedOffice] && (
          <div>
            <div style={{ marginBottom: 16 }}>
              <Title level={4}>{selectedOffice} - {selectedYear}</Title>
              <Text>
                <strong>Total FTE:</strong> {totalFte} | 
                <Text style={{ color: '#52c41a', marginLeft: 8 }}>Recruited: +{totalRecruited}</Text> | 
                <Text style={{ color: '#ff4d4f', marginLeft: 8 }}>Churned: -{totalChurned}</Text> | 
                <Text style={{ color: '#1890ff', marginLeft: 8 }}>Prog. In: +{totalProgressedIn}</Text> | 
                <Text style={{ color: '#fa8c16', marginLeft: 8 }}>Prog. Out: -{totalProgressedOut}</Text> | 
                <Text strong style={{ color: totalNetChange > 0 ? '#52c41a' : totalNetChange < 0 ? '#ff4d4f' : undefined, marginLeft: 8 }}>
                  Net: {totalNetChange > 0 ? '+' : ''}{totalNetChange}
                </Text>
              </Text>
            </div>
            
            <Table
              dataSource={tableData}
              columns={columns}
              pagination={false}
              size="small"
              scroll={{ x: 'max-content' }}
              style={{ marginTop: 16 }}
            />
          </div>
        )}
      </Card>
    );
  };

  return renderOfficeData();
};

export default OfficeDetails; 