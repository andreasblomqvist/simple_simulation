import React from 'react';
import { useTheme } from '../components/ThemeContext';

export default function Settings() {
  const { darkMode, setDarkMode } = useTheme();

  return (
    <div className="space-y-8">
      {/* Theme Switcher */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 flex items-center gap-4">
        <div className="font-semibold text-blue-700 dark:text-blue-400">Theme</div>
        <button
          className={`px-4 py-2 rounded font-semibold ${!darkMode ? 'bg-blue-600 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200'}`}
          onClick={() => setDarkMode(false)}
        >
          Light
        </button>
        <button
          className={`px-4 py-2 rounded font-semibold ${darkMode ? 'bg-blue-600 text-white' : 'bg-gray-800 dark:bg-gray-900 text-white'}`}
          onClick={() => setDarkMode(true)}
        >
          Dark
        </button>
      </div>
      {/* API/Backend Config */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="font-semibold text-blue-700 dark:text-blue-400 mb-2">API/Backend Config</div>
        <input type="text" className="p-2 rounded border w-full dark:bg-gray-900 dark:text-gray-100 dark:border-gray-700" placeholder="API URL" />
      </div>
      {/* User Preferences */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="font-semibold text-blue-700 dark:text-blue-400 mb-2">User Preferences</div>
        <div className="text-gray-400 dark:text-gray-300">[User preferences UI here]</div>
      </div>
    </div>
  );
} 