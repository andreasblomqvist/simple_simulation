import React from 'react';

export default function Configuration() {
  return (
    <div className="space-y-8">
      {/* Company Management Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="font-semibold text-blue-700 dark:text-blue-400 mb-4">Company Management</div>
        <div className="flex flex-col md:flex-row gap-4">
          <select className="p-2 rounded border text-gray-700 dark:bg-gray-900 dark:text-gray-100 dark:border-gray-700">
            <option>Select Company</option>
          </select>
          <button className="px-4 py-2 rounded bg-blue-100 dark:bg-gray-700 text-blue-700 dark:text-blue-300 font-semibold">Add Company</button>
          <button className="px-4 py-2 rounded bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 font-semibold">Edit</button>
          <button className="px-4 py-2 rounded bg-red-100 dark:bg-red-700 text-red-700 dark:text-red-200 font-semibold">Delete</button>
        </div>
      </div>
      {/* Office Management Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="font-semibold text-blue-700 dark:text-blue-400 mb-4">Office Management</div>
        <div className="flex flex-col md:flex-row gap-4 mb-4">
          <select className="p-2 rounded border text-gray-700 dark:bg-gray-900 dark:text-gray-100 dark:border-gray-700">
            <option>Select Office</option>
          </select>
          <button className="px-4 py-2 rounded bg-blue-100 dark:bg-gray-700 text-blue-700 dark:text-blue-300 font-semibold">Add Office</button>
          <button className="px-4 py-2 rounded bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 font-semibold">Edit</button>
          <button className="px-4 py-2 rounded bg-red-100 dark:bg-red-700 text-red-700 dark:text-red-200 font-semibold">Delete</button>
        </div>
        <div className="text-gray-400 dark:text-gray-300">[Office Detailed Config Form]</div>
      </div>
      {/* Level/Role/Promotion/Churn Configs */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="font-semibold text-blue-700 dark:text-blue-400 mb-4">Level/Role/Promotion/Churn Configs</div>
        <div className="text-gray-400 dark:text-gray-300">[Level/Role/Promotion/Churn config UI here]</div>
      </div>
    </div>
  );
} 