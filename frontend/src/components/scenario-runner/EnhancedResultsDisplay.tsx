import React, { useState, useMemo } from 'react';
import { Card, Table, Descriptions, Typography, Tabs, Row, Col, Statistic, Progress, Tag } from 'antd';
import { LineChart, Line, AreaChart, Area, PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { RiseOutlined, FallOutlined, UserOutlined, DollarOutlined, TeamOutlined } from '@ant-design/icons';
import type { ScenarioResponse } from '../../types/unified-data-structures';

const { Title, Text } = Typography;

interface EnhancedResultsDisplayProps {
  result: ScenarioResponse;
}

interface YearData {
  year: string;
  data: any;
  kpis: any;
}

interface ChartDataPoint {
  month: string;
  value: number;
  year: string;
}

interface SeniorityData {
  level: string;
  count: number;
  percentage: number;
}

interface RecruitmentChurnData {
  month: string;
  recruitment: number;
  churn: number;
  net: number;
}

const COLORS = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#13c2c2', '#eb2f96', '#fa8c16'];

const LEVEL_ORDER = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP'];

const EnhancedResultsDisplay: React.FC<EnhancedResultsDisplayProps> = ({ result }) => {
  const [selectedYear, setSelectedYear] = useState<string>('');

  // Process simulation results
  const yearsData = useMemo((): YearData[] => {
    if (!result?.results?.years) return [];
    
    const years = Object.keys(result.results.years).sort();
    return years.map(year => ({
      year,
      data: result.results.years[year],
      kpis: result.results.years[year].kpis || {}
    }));
  }, [result]);

  // Set initial selected year
  React.useEffect(() => {
    if (yearsData.length > 0 && !selectedYear) {
      setSelectedYear(yearsData[0].year);
    }
  }, [yearsData, selectedYear]);

  const currentYearData = yearsData.find(y => y.year === selectedYear);

  // Format numbers with Swedish locale
  const formatNumber = (num: number, decimals = 0) => {
    if (typeof num !== 'number' || isNaN(num)) return 'N/A';
    return num.toLocaleString('sv-SE', { maximumFractionDigits: decimals });
  };

  const formatCurrency = (num: number) => {
    if (typeof num !== 'number' || isNaN(num)) return 'N/A';
    return `${formatNumber(num / 1000000, 1)}M SEK`;
  };

  const formatPercent = (num: number) => {
    if (typeof num !== 'number' || isNaN(num)) return 'N/A';
    return `${(num * 100).toFixed(1)}%`;
  };

  // Calculate growth trend between years
  const calculateGrowth = (current: number, previous: number) => {
    if (!previous || previous === 0) return null;
    return ((current - previous) / previous) * 100;
  };

  // Generate FTE growth chart data
  const fteGrowthData = useMemo((): ChartDataPoint[] => {
    if (!currentYearData?.data?.offices) return [];
    
    const stockholmOffice = currentYearData.data.offices.Stockholm;
    if (!stockholmOffice?.roles?.Consultant?.A || !Array.isArray(stockholmOffice.roles.Consultant.A)) return [];
    
    return stockholmOffice.roles.Consultant.A.map((monthData: any, index: number) => ({
      month: `Month ${index + 1}`,
      value: monthData.fte || 0,
      year: currentYearData.year
    }));
  }, [currentYearData]);

  // Generate seniority distribution data
  const seniorityData = useMemo((): SeniorityData[] => {
    if (!currentYearData?.data?.offices) return [];
    
    const stockholmOffice = currentYearData.data.offices.Stockholm;
    if (!stockholmOffice?.roles?.Consultant) return [];
    
    const levelCounts: { [key: string]: number } = {};
    let totalFTE = 0;
    
    // Calculate FTE for each level (using December data)
    LEVEL_ORDER.forEach(level => {
      const levelData = stockholmOffice.roles.Consultant[level];
      if (Array.isArray(levelData) && levelData.length > 0) {
        const decemberData = levelData[levelData.length - 1]; // Last month
        const fte = decemberData?.fte || 0;
        levelCounts[level] = fte;
        totalFTE += fte;
      }
    });
    
    return LEVEL_ORDER.map(level => ({
      level,
      count: levelCounts[level] || 0,
      percentage: totalFTE > 0 ? ((levelCounts[level] || 0) / totalFTE) * 100 : 0
    })).filter(item => item.count > 0);
  }, [currentYearData]);

  // Generate recruitment vs churn data
  const recruitmentChurnData = useMemo((): RecruitmentChurnData[] => {
    if (!currentYearData?.data?.offices) return [];
    
    const stockholmOffice = currentYearData.data.offices.Stockholm;
    if (!stockholmOffice?.roles?.Consultant?.A || !Array.isArray(stockholmOffice.roles.Consultant.A)) return [];
    
    return stockholmOffice.roles.Consultant.A.map((monthData: any, index: number) => ({
      month: `M${index + 1}`,
      recruitment: monthData.recruitment || 0,
      churn: monthData.churn || 0,
      net: (monthData.recruitment || 0) - (monthData.churn || 0)
    }));
  }, [currentYearData]);

  // Financial KPIs Cards
  const renderFinancialKPIs = () => {
    if (!currentYearData?.kpis?.financial) return null;
    
    const financial = currentYearData.kpis.financial;
    const previousYear = yearsData.find(y => parseInt(y.year) === parseInt(currentYearData.year) - 1);
    const previousFinancial = previousYear?.kpis?.financial;
    
    const kpiCards = [
      {
        title: 'Net Sales',
        value: formatCurrency(financial.net_sales),
        rawValue: financial.net_sales,
        previousValue: previousFinancial?.net_sales,
        icon: <DollarOutlined />,
        color: '#1890ff'
      },
      {
        title: 'EBITDA',
        value: formatCurrency(financial.ebitda),
        rawValue: financial.ebitda,
        previousValue: previousFinancial?.ebitda,
        icon: <RiseOutlined />,
        color: '#52c41a'
      },
      {
        title: 'Margin',
        value: formatPercent(financial.margin),
        rawValue: financial.margin * 100,
        previousValue: previousFinancial?.margin ? previousFinancial.margin * 100 : undefined,
        icon: <RiseOutlined />,
        color: '#faad14'
      },
      {
        title: 'Total Consultants',
        value: formatNumber(financial.total_consultants, 1),
        rawValue: financial.total_consultants,
        previousValue: previousFinancial?.total_consultants,
        icon: <TeamOutlined />,
        color: '#722ed1'
      }
    ];
    
    return (
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {kpiCards.map((kpi, index) => {
          const growth = kpi.previousValue ? calculateGrowth(kpi.rawValue, kpi.previousValue) : null;
          
          return (
            <Col xs={24} sm={12} lg={6} key={index}>
              <Card>
                <Statistic
                  title={kpi.title}
                  value={kpi.value}
                  prefix={kpi.icon}
                  valueStyle={{ color: kpi.color }}
                />
                {growth !== null && (
                  <div style={{ marginTop: 8 }}>
                    <Text type={growth >= 0 ? 'success' : 'danger'} style={{ fontSize: 12 }}>
                      {growth >= 0 ? <RiseOutlined /> : <FallOutlined />}
                      {' '}{Math.abs(growth).toFixed(1)}% vs previous year
                    </Text>
                  </div>
                )}
              </Card>
            </Col>
          );
        })}
      </Row>
    );
  };

  // FTE Growth Chart
  const renderFTEGrowthChart = () => (
    <Card title="FTE Growth Over Time" style={{ marginBottom: 24 }}>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={fteGrowthData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip formatter={(value) => [formatNumber(value as number), 'FTE']} />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="value" 
            stroke="#1890ff" 
            strokeWidth={2}
            dot={{ fill: '#1890ff', strokeWidth: 2, r: 4 }}
            name="Consultant FTE"
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );

  // Seniority Distribution Chart
  const renderSeniorityChart = () => (
    <Card title="Seniority Distribution" style={{ marginBottom: 24 }}>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={seniorityData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            paddingAngle={2}
            dataKey="count"
          >
            {seniorityData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(value, name, props) => [
            `${formatNumber(value as number)} FTE (${props.payload?.percentage.toFixed(1)}%)`,
            `Level ${name}`
          ]} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
      <Row gutter={[8, 8]} style={{ marginTop: 16 }}>
        {seniorityData.map((item, index) => (
          <Col span={6} key={item.level}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ 
                width: 12, 
                height: 12, 
                backgroundColor: COLORS[index % COLORS.length],
                display: 'inline-block',
                marginRight: 4,
                borderRadius: 2
              }} />
              <Text strong>{item.level}</Text>
              <br />
              <Text type="secondary">{formatNumber(item.count)} FTE</Text>
            </div>
          </Col>
        ))}
      </Row>
    </Card>
  );

  // Recruitment vs Churn Chart
  const renderRecruitmentChurnChart = () => (
    <Card title="Monthly Recruitment vs Churn" style={{ marginBottom: 24 }}>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={recruitmentChurnData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="recruitment" fill="#52c41a" name="Recruitment" />
          <Bar dataKey="churn" fill="#f5222d" name="Churn" />
          <Bar dataKey="net" fill="#1890ff" name="Net Growth" />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );

  // Recruitment & Churn Details Table
  const renderRecruitmentTable = () => {
    if (!currentYearData?.data?.offices) return null;
    
    const stockholmOffice = currentYearData.data.offices.Stockholm;
    if (!stockholmOffice?.roles?.Consultant) return null;
    
    const tableData = LEVEL_ORDER.map(level => {
      const levelData = stockholmOffice.roles.Consultant[level];
      if (!Array.isArray(levelData) || levelData.length === 0) return null;
      
      // Calculate totals for the year
      const totalRecruitment = levelData.reduce((sum, month) => sum + (month.recruitment || 0), 0);
      const totalChurn = levelData.reduce((sum, month) => sum + (month.churn || 0), 0);
      const netGrowth = totalRecruitment - totalChurn;
      const currentFTE = levelData[levelData.length - 1]?.fte || 0;
      
      return {
        level,
        currentFTE,
        totalRecruitment,
        totalChurn,
        netGrowth,
        growthRate: currentFTE > 0 ? (netGrowth / currentFTE) * 100 : 0
      };
    }).filter(Boolean);

    const columns = [
      {
        title: 'Level',
        dataIndex: 'level',
        key: 'level',
        render: (level: string) => <Tag color="blue">{level}</Tag>
      },
      {
        title: 'Current FTE',
        dataIndex: 'currentFTE',
        key: 'currentFTE',
        render: (value: number) => formatNumber(value, 1),
        sorter: (a: any, b: any) => a.currentFTE - b.currentFTE
      },
      {
        title: 'Total Recruitment',
        dataIndex: 'totalRecruitment',
        key: 'totalRecruitment',
        render: (value: number) => <Text style={{ color: '#52c41a' }}>{formatNumber(value)}</Text>,
        sorter: (a: any, b: any) => a.totalRecruitment - b.totalRecruitment
      },
      {
        title: 'Total Churn',
        dataIndex: 'totalChurn',
        key: 'totalChurn',
        render: (value: number) => <Text style={{ color: '#f5222d' }}>{formatNumber(value)}</Text>,
        sorter: (a: any, b: any) => a.totalChurn - b.totalChurn
      },
      {
        title: 'Net Growth',
        dataIndex: 'netGrowth',
        key: 'netGrowth',
        render: (value: number) => (
          <Text style={{ color: value >= 0 ? '#52c41a' : '#f5222d' }}>
            {value >= 0 ? '+' : ''}{formatNumber(value)}
          </Text>
        ),
        sorter: (a: any, b: any) => a.netGrowth - b.netGrowth
      },
      {
        title: 'Growth Rate',
        dataIndex: 'growthRate',
        key: 'growthRate',
        render: (value: number) => (
          <Text style={{ color: value >= 0 ? '#52c41a' : '#f5222d' }}>
            {value >= 0 ? '+' : ''}{value.toFixed(1)}%
          </Text>
        ),
        sorter: (a: any, b: any) => a.growthRate - b.growthRate
      }
    ];

    return (
      <Card title="Recruitment & Churn Summary by Level" style={{ marginBottom: 24 }}>
        <Table 
          dataSource={tableData} 
          columns={columns} 
          pagination={false}
          size="small"
          rowKey="level"
        />
      </Card>
    );
  };

  // Year-over-Year Comparison
  const renderYearComparison = () => {
    if (yearsData.length < 2) return null;
    
    const comparisonData = yearsData.map(yearData => {
      const financial = yearData.kpis?.financial || {};
      return {
        year: yearData.year,
        netSales: financial.net_sales || 0,
        ebitda: financial.ebitda || 0,
        margin: (financial.margin || 0) * 100,
        consultants: financial.total_consultants || 0,
        totalFTE: yearData.data?.total_fte || 0
      };
    });
    
    return (
      <Card title="Year-over-Year Comparison" style={{ marginBottom: 24 }}>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={comparisonData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip 
              formatter={(value, name) => {
                if (name === 'Net Sales' || name === 'EBITDA') {
                  return [formatCurrency(value as number), name];
                }
                return [formatNumber(value as number, 1), name];
              }}
            />
            <Legend />
            <Area
              yAxisId="left"
              type="monotone"
              dataKey="netSales"
              stackId="1"
              stroke="#1890ff"
              fill="#1890ff"
              fillOpacity={0.3}
              name="Net Sales"
            />
            <Area
              yAxisId="right"
              type="monotone"
              dataKey="consultants"
              stackId="2"
              stroke="#52c41a"
              fill="#52c41a"
              fillOpacity={0.3}
              name="Total Consultants"
            />
          </AreaChart>
        </ResponsiveContainer>
      </Card>
    );
  };

  if (!result || !yearsData.length) {
    return (
      <Card>
        <Text type="secondary">No simulation results available</Text>
      </Card>
    );
  }

  const tabItems = yearsData.map(yearData => ({
    key: yearData.year,
    label: `Year ${yearData.year}`,
    children: (
      <div>
        {renderFinancialKPIs()}
        <Row gutter={[16, 0]}>
          <Col xs={24} lg={12}>
            {renderFTEGrowthChart()}
          </Col>
          <Col xs={24} lg={12}>
            {renderSeniorityChart()}
          </Col>
        </Row>
        <Row gutter={[16, 0]}>
          <Col xs={24} lg={12}>
            {renderRecruitmentChurnChart()}
          </Col>
          <Col xs={24} lg={12}>
            {renderRecruitmentTable()}
          </Col>
        </Row>
      </div>
    )
  }));

  return (
    <div>
      <Title level={3} style={{ marginBottom: 24 }}>Simulation Results Dashboard</Title>
      
      {yearsData.length > 1 && renderYearComparison()}
      
      <Tabs
        activeKey={selectedYear}
        onChange={setSelectedYear}
        items={tabItems}
        type="card"
      />
    </div>
  );
};

export default EnhancedResultsDisplay;