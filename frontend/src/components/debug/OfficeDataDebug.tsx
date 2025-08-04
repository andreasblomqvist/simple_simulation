import React, { useEffect, useState } from 'react';

export const OfficeDataDebug: React.FC = () => {
  const [officeData, setOfficeData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchOfficeData = async () => {
      try {
        const response = await fetch('http://localhost:8000/offices');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setOfficeData(data[0]); // Get first office
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      }
    };

    fetchOfficeData();
  }, []);

  if (error) {
    return <div className="p-4 bg-red-100 text-red-800">Error: {error}</div>;
  }

  if (!officeData) {
    return <div className="p-4">Loading office data...</div>;
  }

  return (
    <div className="fixed top-4 left-4 bg-white dark:bg-gray-800 p-4 border rounded-lg shadow-lg max-w-md z-50">
      <h3 className="font-bold mb-2">Office Data Structure Debug</h3>
      <div className="text-xs space-y-2">
        <div><strong>Name:</strong> {officeData.name}</div>
        <div><strong>Journey:</strong> {officeData.journey}</div>
        <div><strong>Total FTE:</strong> {officeData.total_fte}</div>
        
        <div><strong>Economic Parameters:</strong></div>
        <div className="pl-4">
          <div>Cost of Living: {officeData.economic_parameters?.cost_of_living}</div>
          <div>Market Multiplier: {officeData.economic_parameters?.market_multiplier}</div>
          <div>Tax Rate: {officeData.economic_parameters?.tax_rate}</div>
        </div>
        
        <div><strong>Roles Count:</strong> {officeData.roles ? Object.keys(officeData.roles).length : 0}</div>
        
        <pre className="text-xs bg-gray-100 dark:bg-gray-700 p-2 rounded overflow-auto max-h-32">
          {JSON.stringify(officeData, null, 2)}
        </pre>
      </div>
    </div>
  );
};