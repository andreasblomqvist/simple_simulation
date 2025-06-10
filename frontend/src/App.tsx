import React from 'react';
import ConfigPanel from './components/ConfigPanel';
import ScenarioComparison from './components/ScenarioComparison';
import OfficeSelector from './components/OfficeSelector';
import ResultsDisplay from './components/ResultsDisplay';

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-8">
      <h1 className="text-4xl font-bold text-blue-700 mb-4">SimpleSim Workforce Simulation</h1>
      <p className="text-lg text-gray-700 mb-8 text-center max-w-2xl">Configure and run workforce simulations, compare scenarios, and explore results by office or group.</p>
      <ConfigPanel />
      <ScenarioComparison />
      <OfficeSelector />
      <ResultsDisplay />
    </div>
  );
} 