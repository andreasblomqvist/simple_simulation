import React from 'react';

export default function GrowthProjections() {
  return (
    <div className="space-y-8">
      {/* Global Growth Rate Inputs */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="font-semibold text-blue-700 dark:text-blue-400 mb-4">Global Growth Rate Inputs</div>
        <div className="flex flex-col gap-4 md:flex-row md:gap-8">
          <div>
            <label className="block text-gray-600 dark:text-gray-300 mb-1">New Office Growth Rate (%)</label>
            <input type="number" className="p-2 rounded border w-full dark:bg-gray-900 dark:text-gray-100 dark:border-gray-700" placeholder="e.g. 10" />
          </div>
          <div>
            <label className="block text-gray-600 dark:text-gray-300 mb-1">Established Office Growth Rate (%)</label>
            <input type="number" className="p-2 rounded border w-full dark:bg-gray-900 dark:text-gray-100 dark:border-gray-700" placeholder="e.g. 5" />
          </div>
          <div>
            <label className="block text-gray-600 dark:text-gray-300 mb-1">Mature Office Growth Rate (%)</label>
            <input type="number" className="p-2 rounded border w-full dark:bg-gray-900 dark:text-gray-100 dark:border-gray-700" placeholder="e.g. 2" />
          </div>
        </div>
      </div>
      {/* Office-Specific Growth Rate Inputs */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="font-semibold text-blue-700 dark:text-blue-400 mb-4">Office-Specific Growth Rate Inputs</div>
        <div className="flex flex-col md:flex-row gap-4">
          <select className="p-2 rounded border text-gray-700 dark:bg-gray-900 dark:text-gray-100 dark:border-gray-700">
            <option>Select Office</option>
          </select>
          <input type="number" className="p-2 rounded border w-full dark:bg-gray-900 dark:text-gray-100 dark:border-gray-700" placeholder="Office growth rate (%)" />
        </div>
      </div>
      {/* Projection Charts and Tables */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 h-64 flex items-center justify-center text-gray-400 dark:text-gray-300">[Projection Chart]</div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 h-64 flex items-center justify-center text-gray-400 dark:text-gray-300">[Projection Table]</div>
      </div>
    </div>
  );
} 