import React, { useState } from 'react';
import { Card, Button, Typography, Space, Input, Alert, Divider } from 'antd';
import { runAllValidations, logApiResponseStructure } from '../test-data-validation';

const { Title, Text } = Typography;
const { TextArea } = Input;

interface DataValidationTestProps {
  onValidationComplete?: (results: any) => void;
}

const DataValidationTest: React.FC<DataValidationTestProps> = ({ onValidationComplete }) => {
  const [apiResponse, setApiResponse] = useState<string>('');
  const [validationResults, setValidationResults] = useState<any>(null);
  const [isValidating, setIsValidating] = useState(false);

  const handleValidate = async () => {
    if (!apiResponse.trim()) {
      alert('Please paste the API response JSON first');
      return;
    }

    setIsValidating(true);
    
    try {
      const parsedResponse = JSON.parse(apiResponse);
      
      // Log the API response structure
      logApiResponseStructure(parsedResponse);
      
      // Run all validations
      const results = runAllValidations(parsedResponse);
      setValidationResults(results);
      
      if (onValidationComplete) {
        onValidationComplete(results);
      }
      
    } catch (error) {
      alert(`Error parsing JSON: ${error}`);
    } finally {
      setIsValidating(false);
    }
  };

  const handleClear = () => {
    setApiResponse('');
    setValidationResults(null);
  };

  const renderValidationResults = () => {
    if (!validationResults) return null;

    const { backendValidation, dataFlowSimulation, summary } = validationResults;

    return (
      <div style={{ marginTop: 16 }}>
        <Title level={4}>Validation Results</Title>
        
        {/* Summary */}
        <Alert
          message={`Validation Complete: ${summary.totalIssues} issues found`}
          description={
            <div>
              <Text strong>Critical Issues: {summary.criticalIssues.length}</Text>
              <br />
              <Text>Recommendations:</Text>
              <ul>
                {summary.recommendations.map((rec: string, index: number) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>
          }
          type={summary.criticalIssues.length > 0 ? 'error' : 'success'}
          showIcon
          style={{ marginBottom: 16 }}
        />

        {/* Backend Validation */}
        <Card title="Backend API Response Validation" size="small" style={{ marginBottom: 16 }}>
          <Text strong>Status: </Text>
          <Text type={backendValidation.isValid ? 'success' : 'danger'}>
            {backendValidation.isValid ? '✅ Valid' : '❌ Invalid'}
          </Text>
          
          {backendValidation.issues.length > 0 && (
            <div style={{ marginTop: 8 }}>
              <Text strong>Issues:</Text>
              <ul>
                {backendValidation.issues.map((issue: string, index: number) => (
                  <li key={index} style={{ color: '#ff4d4f' }}>{issue}</li>
                ))}
              </ul>
            </div>
          )}
          
          {Object.keys(backendValidation.fteValues).length > 0 && (
            <div style={{ marginTop: 8 }}>
              <Text strong>FTE Values Found:</Text>
              <pre style={{ fontSize: 12, backgroundColor: '#f5f5f5', padding: 8, marginTop: 4 }}>
                {JSON.stringify(backendValidation.fteValues, null, 2)}
              </pre>
            </div>
          )}
        </Card>

        {/* Data Flow Simulation */}
        <Card title="Data Flow Simulation" size="small" style={{ marginBottom: 16 }}>
          {dataFlowSimulation.issues.length > 0 ? (
            <div>
              <Text strong>Issues in Data Flow:</Text>
              <ul>
                {dataFlowSimulation.issues.map((issue: string, index: number) => (
                  <li key={index} style={{ color: '#ff4d4f' }}>{issue}</li>
                ))}
              </ul>
            </div>
          ) : (
            <Text type="success">✅ Data flow simulation completed without issues</Text>
          )}
        </Card>

        {/* Critical Issues */}
        {summary.criticalIssues.length > 0 && (
          <Alert
            message="Critical Issues Detected"
            description={
              <ul>
                {summary.criticalIssues.map((issue: string, index: number) => (
                  <li key={index}>{issue}</li>
                ))}
              </ul>
            }
            type="error"
            showIcon
          />
        )}
      </div>
    );
  };

  return (
    <Card title="FTE Data Flow Validation Test" style={{ margin: 16 }}>
      <div>
        <Text>
          This tool helps validate the FTE data flow from backend API response to frontend display.
          Paste your API response JSON below and click "Validate" to run the tests.
        </Text>
        
        <Divider />
        
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Text strong>API Response JSON:</Text>
            <TextArea
              value={apiResponse}
              onChange={(e) => setApiResponse(e.target.value)}
              placeholder="Paste your API response JSON here..."
              rows={10}
              style={{ marginTop: 8 }}
            />
          </div>
          
          <Space>
            <Button 
              type="primary" 
              onClick={handleValidate}
              loading={isValidating}
            >
              {isValidating ? 'Validating...' : 'Validate Data Flow'}
            </Button>
            <Button onClick={handleClear}>
              Clear
            </Button>
          </Space>
        </Space>

        {renderValidationResults()}
      </div>
    </Card>
  );
};

export default DataValidationTest; 