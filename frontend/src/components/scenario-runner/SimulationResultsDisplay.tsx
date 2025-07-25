import React from 'react';
import { Card, Table, Descriptions, Typography, Tabs, Empty } from 'antd';
import type { ScenarioResponse } from '../../types/unified-data-structures';

const { Title, Text } = Typography;

interface SimulationResultsDisplayProps {
  result: ScenarioResponse;
}

const SimulationResultsDisplay: React.FC<SimulationResultsDisplayProps> = ({ result }) => {
  if (!result) {
    return <Empty description="No simulation results" />;
  }

  // Try to extract meaningful data from results
  const renderResults = () => {
    if (!result.results) {
      return <Text type="secondary">No results data available</Text>;
    }

    try {
      // If results is already an object
      if (typeof result.results === 'object') {
        // Check if it's simulation results with years structure (unified format)
        if (result.results.years && typeof result.results.years === 'object') {
          return renderStructuredResults(result.results);
        }
        
        // Otherwise show as formatted JSON
        return (
          <pre style={{ 
            background: '#f5f5f5', 
            color: '#333',
            padding: 16, 
            borderRadius: 4, 
            overflow: 'auto',
            maxHeight: 400
          }}>
            {JSON.stringify(result.results, null, 2)}
          </pre>
        );
      }

      // If results is a string, try to parse it
      if (typeof result.results === 'string') {
        try {
          const parsed = JSON.parse(result.results);
          return renderStructuredResults(parsed);
        } catch {
          return <Text>{result.results}</Text>;
        }
      }

      return <Text>Unexpected result format</Text>;
    } catch (error) {
      console.error('Error rendering results:', error);
      return <Text type="danger">Error displaying results</Text>;
    }
  };

  const renderStructuredResults = (data: any) => {
    // Handle different result structures
    const actualResults = data.results || data;

    // Check if this has a 'years' structure (new unified format)
    if (actualResults.years && typeof actualResults.years === 'object') {
      const years = Object.keys(actualResults.years);
      
      if (years.length === 1) {
        // Single year - show offices directly
        const yearData = actualResults.years[years[0]];
        if (yearData.offices) {
          return (
            <div>
              <Text strong style={{ display: 'block', marginBottom: 16 }}>
                Year: {years[0]}
              </Text>
              {yearData.kpis && renderYearKPIs(yearData.kpis)}
              {renderOfficeResults(yearData.offices)}
            </div>
          );
        }
      } else {
        // Multiple years - show year tabs
        const yearItems = years.map(year => ({
          key: year,
          label: `Year ${year}`,
          children: actualResults.years[year].offices ? 
            <div>
              {actualResults.years[year].kpis && renderYearKPIs(actualResults.years[year].kpis)}
              {renderOfficeResults(actualResults.years[year].offices)}
            </div> :
            <pre>{JSON.stringify(actualResults.years[year], null, 2)}</pre>
        }));
        
        return <Tabs items={yearItems} />;
      }
    }

    // Legacy format - direct office structure
    if (actualResults.offices) {
      return renderOfficeResults(actualResults.offices);
    }

    if (actualResults.Group || actualResults.Stockholm) {
      return renderOfficeResults(actualResults);
    }

    // Fallback to JSON display
    return (
      <pre style={{ 
        background: '#f5f5f5', 
        color: '#333',
        padding: 16, 
        borderRadius: 4, 
        overflow: 'auto',
        maxHeight: 400
      }}>
        {JSON.stringify(actualResults, null, 2)}
      </pre>
    );
  };

  const renderYearKPIs = (kpis: any) => {
    if (!kpis) return null;

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

    return (
      <Card title="Key Performance Indicators" size="small" style={{ marginBottom: 16 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
          {kpis.financial && (
            <div>
              <Text strong style={{ display: 'block', marginBottom: 8 }}>Financial KPIs</Text>
              <Descriptions size="small" column={1}>
                <Descriptions.Item label="Net Sales">{formatCurrency(kpis.financial.net_sales)}</Descriptions.Item>
                <Descriptions.Item label="EBITDA">{formatCurrency(kpis.financial.ebitda)}</Descriptions.Item>
                <Descriptions.Item label="Margin">{formatPercent(kpis.financial.margin)}</Descriptions.Item>
                <Descriptions.Item label="Total Consultants">{formatNumber(kpis.financial.total_consultants, 1)}</Descriptions.Item>
                <Descriptions.Item label="Avg Hourly Rate">{formatNumber(kpis.financial.avg_hourly_rate)} SEK</Descriptions.Item>
              </Descriptions>
            </div>
          )}
          {kpis.growth && (
            <div>
              <Text strong style={{ display: 'block', marginBottom: 8 }}>Growth KPIs</Text>
              <Descriptions size="small" column={1}>
                <Descriptions.Item label="FTE Growth">{formatPercent(kpis.growth.fte_growth)}</Descriptions.Item>
                <Descriptions.Item label="Revenue Growth">{formatPercent(kpis.growth.revenue_growth)}</Descriptions.Item>
                <Descriptions.Item label="Consultant Growth">{formatPercent(kpis.growth.consultant_growth)}</Descriptions.Item>
              </Descriptions>
            </div>
          )}
        </div>
      </Card>
    );
  };

  const renderOfficeResults = (offices: any) => {
    const officeNames = Object.keys(offices);
    
    if (officeNames.length === 0) {
      return <Text type="secondary">No office data available</Text>;
    }

    // Create tabs for each office
    const tabItems = officeNames.map(officeName => {
      const officeData = offices[officeName];
      
      return {
        key: officeName,
        label: officeName,
        children: renderOfficeData(officeData)
      };
    });

    return <Tabs items={tabItems} />;
  };

  const renderOfficeData = (officeData: any) => {
    if (!officeData || typeof officeData !== 'object') {
      return <Text type="secondary">No data for this office</Text>;
    }

    // Check if this office has a 'roles' property (new structure)
    if (officeData.roles && typeof officeData.roles === 'object') {
      return (
        <div>
          <div style={{ marginBottom: 16 }}>
            <Descriptions size="small" column={2}>
              <Descriptions.Item label="Office Name">{officeData.name}</Descriptions.Item>
              <Descriptions.Item label="Total FTE">{officeData.total_fte}</Descriptions.Item>
              <Descriptions.Item label="Journey">{officeData.journey}</Descriptions.Item>
            </Descriptions>
          </div>
          {renderRoleData(officeData.roles)}
        </div>
      );
    }

    // Check if this is direct role-based data (legacy structure)
    const roles = Object.keys(officeData);
    const hasRoleData = roles.some(role => 
      officeData[role] && typeof officeData[role] === 'object'
    );

    if (hasRoleData) {
      return renderRoleData(officeData);
    }

    // Fallback to JSON display
    return (
      <pre style={{ 
        background: '#f5f5f5', 
        color: '#333',
        padding: 12, 
        borderRadius: 4, 
        fontSize: 12
      }}>
        {JSON.stringify(officeData, null, 2)}
      </pre>
    );
  };

  const renderRoleData = (roleData: any) => {
    const roles = Object.keys(roleData);
    
    return (
      <div>
        {roles.map(roleName => {
          const data = roleData[roleName];
          if (!data || typeof data !== 'object') return null;

          return (
            <Card key={roleName} title={roleName} size="small" style={{ marginBottom: 16 }}>
              {renderLevelData(data)}
            </Card>
          );
        })}
      </div>
    );
  };

  const renderLevelData = (levelData: any) => {
    // Check if this is level-based data (object with level keys)
    if (typeof levelData === 'object' && !Array.isArray(levelData)) {
      const levels = Object.keys(levelData);
      const hasLevelData = levels.some(level => 
        Array.isArray(levelData[level]) || typeof levelData[level] === 'object'
      );

      if (hasLevelData) {
        return (
          <Tabs size="small" items={levels.map(level => ({
            key: level,
            label: level,
            children: renderMonthlyData(levelData[level])
          }))} />
        );
      }
    }

    // Fallback to JSON display
    return (
      <pre style={{ 
        background: '#fafafa', 
        color: '#333',
        padding: 8, 
        borderRadius: 4, 
        fontSize: 11,
        maxHeight: 200,
        overflow: 'auto'
      }}>
        {JSON.stringify(levelData, null, 2)}
      </pre>
    );
  };

  const renderMonthlyData = (monthlyData: any) => {
    // If it's an array of monthly results, display as table
    if (Array.isArray(monthlyData)) {
      const columns = [
        { title: 'Month', dataIndex: 'month', key: 'month', width: 60 },
        { title: 'FTE', dataIndex: 'fte', key: 'fte', width: 60 },
        { title: 'Price', dataIndex: 'price', key: 'price', width: 80 },
        { title: 'Salary', dataIndex: 'salary', key: 'salary', width: 80 },
        { title: 'Recruitment', dataIndex: 'recruitment', key: 'recruitment', width: 80 },
        { title: 'Churn', dataIndex: 'churn', key: 'churn', width: 60 },
        { title: 'Progression', dataIndex: 'promoted_people', key: 'progression', width: 80 }
      ];

      const tableData = monthlyData.map((monthData, index) => ({
        key: index,
        month: index + 1,
        fte: monthData.fte || 0,
        price: monthData.price || 0,
        salary: monthData.salary || 0,
        recruitment: monthData.recruitment || 0,
        churn: monthData.churn || 0,
        promoted_people: monthData.promoted_people || 0
      }));

      return (
        <Table 
          columns={columns} 
          dataSource={tableData} 
          pagination={false} 
          size="small"
          scroll={{ x: 600 }}
        />
      );
    }

    // Fallback to JSON display
    return (
      <pre style={{ 
        background: '#fafafa', 
        color: '#333',
        padding: 8, 
        borderRadius: 4, 
        fontSize: 11,
        maxHeight: 200,
        overflow: 'auto'
      }}>
        {JSON.stringify(monthlyData, null, 2)}
      </pre>
    );
  };

  return (
    <Card title="Simulation Results">
      <Descriptions column={2} size="small" style={{ marginBottom: 16 }}>
        <Descriptions.Item label="Status">{result.status}</Descriptions.Item>
        <Descriptions.Item label="Execution Time">
          {result.execution_time?.toFixed(2)}s
        </Descriptions.Item>
        <Descriptions.Item label="Scenario">{result.scenario_name}</Descriptions.Item>
        <Descriptions.Item label="Scenario ID">{result.scenario_id}</Descriptions.Item>
      </Descriptions>

      {result.error_message && (
        <div style={{ marginBottom: 16 }}>
          <Text type="danger">Error: {result.error_message}</Text>
        </div>
      )}

      <div>
        <Title level={5}>Results Data</Title>
        {renderResults()}
      </div>
    </Card>
  );
};

export default SimulationResultsDisplay;