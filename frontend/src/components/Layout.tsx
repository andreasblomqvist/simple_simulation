import React from 'react';
import Sidebar from './Sidebar';

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-900 dark:text-gray-100">
      <Sidebar />
      <main className="flex-1 p-8 overflow-y-auto bg-gray-50 dark:bg-gray-900 dark:text-gray-100">
        {children}
      </main>
    </div>
  );
} 