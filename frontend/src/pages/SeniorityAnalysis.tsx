import React from 'react';

export default function SeniorityAnalysis() {
  return (
    <div className="space-y-8">
      {/* Seniority Distribution Chart */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 h-64 flex items-center justify-center text-gray-400 dark:text-gray-300">
        [Seniority Distribution Chart]
      </div>
      {/* Seniority Breakdown Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="font-semibold text-blue-700 dark:text-blue-400 mb-2">Seniority Breakdown Table</div>
        <div className="text-gray-400 dark:text-gray-300">[Seniority breakdown table here]</div>
      </div>
      {/* Scenario Controls */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="font-semibold text-blue-700 dark:text-blue-400 mb-2">Scenario Controls</div>
        <div className="flex flex-col md:flex-row gap-4">
          <input type="text" className="p-2 rounded border w-full dark:bg-gray-900 dark:text-gray-100 dark:border-gray-700" placeholder="Target Spreads" />
          <input type="text" className="p-2 rounded border w-full dark:bg-gray-900 dark:text-gray-100 dark:border-gray-700" placeholder="Timelines" />
        </div>
      </div>
    </div>
  );
} 