import React from 'react';

export default function Dashboard() {
  return (
    <div className="space-y-8">
      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1,2,3,4].map(i => (
          <div key={i} className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 flex flex-col items-center">
            <div className="text-2xl font-bold text-blue-700 dark:text-blue-400 mb-2">KPI {i}</div>
            <div className="text-gray-500 dark:text-gray-300">[Value]</div>
          </div>
        ))}
      </div>
      {/* Charts Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 h-64 flex items-center justify-center text-gray-400 dark:text-gray-300">[Chart 1]</div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 h-64 flex items-center justify-center text-gray-400 dark:text-gray-300">[Chart 2]</div>
      </div>
      {/* Level Breakdown Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="font-semibold text-blue-700 dark:text-blue-400 mb-2">Level Breakdown</div>
        <div className="text-gray-400 dark:text-gray-300">[Level breakdown table here]</div>
      </div>
      {/* Growth Drivers */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="font-semibold text-blue-700 dark:text-blue-400 mb-2">Growth Drivers</div>
        <div className="space-y-2">
          {[1,2,3].map(i => (
            <div key={i}>
              <div className="flex justify-between text-sm text-gray-600 dark:text-gray-300 mb-1">
                <span>Driver {i}</span>
                <span>[Value]</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${30 + i*20}%` }}></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
} 