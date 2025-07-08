import React from 'react';
import DataValidationTest from '../components/DataValidationTest';

const DataValidationPage: React.FC = () => {
  return (
    <div style={{ padding: 16 }}>
      <h1>FTE Data Flow Validation</h1>
      <p>
        Use this tool to validate the FTE data flow from your backend API response to the frontend display.
        This will help identify where FTE values might be getting lost or transformed incorrectly.
      </p>
      
      <DataValidationTest 
        onValidationComplete={(results) => {
          console.log('Validation completed:', results);
        }}
      />
    </div>
  );
};

export default DataValidationPage; 