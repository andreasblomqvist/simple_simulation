import React from 'react';

const navLinks = [
  { name: 'Dashboard', path: '/' },
  { name: 'All Offices', path: '/offices' },
  { name: 'Growth Projections', path: '/growth' },
  { name: 'Seniority Analysis', path: '/seniority' },
  { name: 'Configuration', path: '/config' },
  { name: 'Simulation Lab', path: '/lab' },
  { name: 'Settings', path: '/settings' },
];

export default function Sidebar() {
  return (
    <aside className="w-72 bg-white border-r flex flex-col p-6 min-h-screen dark:bg-gray-800 dark:border-gray-700 dark:text-gray-100">
      <div className="mb-8">
        <div className="text-2xl font-bold text-blue-700 dark:text-blue-400 mb-2">Org Growth Sim</div>
        <select className="w-full mb-2 p-2 rounded border text-gray-700 dark:bg-gray-900 dark:text-gray-100 dark:border-gray-700">
          <option>Company 1</option>
          <option>Company 2</option>
        </select>
        <button className="w-full text-xs text-blue-600 dark:text-blue-300 hover:underline mb-4">+ Add Company</button>
      </div>
      <div className="mb-8">
        <div className="font-semibold text-sm text-gray-600 dark:text-gray-300 mb-2">Offices</div>
        <div className="mb-2">
          <span className="inline-block w-2 h-2 bg-green-500 rounded-full mr-2"></span>
          <span>New Offices</span>
        </div>
        <div className="mb-2 ml-4 text-gray-500 dark:text-gray-400 text-sm">- Office A<br/>- Office B</div>
        <div className="mb-2">
          <span className="inline-block w-2 h-2 bg-yellow-400 rounded-full mr-2"></span>
          <span>Emerging Offices</span>
        </div>
        <div className="mb-2 ml-4 text-gray-500 dark:text-gray-400 text-sm">- Office C</div>
        <div className="mb-2">
          <span className="inline-block w-2 h-2 bg-gray-400 rounded-full mr-2"></span>
          <span>Established Offices</span>
        </div>
        <div className="mb-2 ml-4 text-gray-500 dark:text-gray-400 text-sm">- Office D</div>
        <div className="mb-2">
          <span className="inline-block w-2 h-2 bg-purple-500 rounded-full mr-2"></span>
          <span>Mature Offices</span>
        </div>
        <div className="mb-2 ml-4 text-gray-500 dark:text-gray-400 text-sm">- Office E</div>
        <button className="w-full text-xs text-blue-600 dark:text-blue-300 hover:underline mt-2">+ Add Office</button>
      </div>
      <nav className="flex flex-col gap-2 mt-4">
        {navLinks.map(link => (
          <a key={link.name} href={link.path} className="text-gray-700 dark:text-gray-100 hover:text-blue-700 dark:hover:text-blue-300 font-medium py-1 px-2 rounded hover:bg-blue-50 dark:hover:bg-gray-700">
            {link.name}
          </a>
        ))}
      </nav>
    </aside>
  );
} 