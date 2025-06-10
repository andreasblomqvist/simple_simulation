import React, { useEffect, useState } from 'react';

interface Office {
  name: string;
  total_fte: number;
  journey: string;
  levels: {
    [key: string]: {
      total: number;
      price: number;
      salary: number;
    };
  };
  operations: {
    total: number;
    price: number;
    salary: number;
  };
  metrics: {
    journey_percentages: { [key: string]: number };
    non_debit_ratio: number | null;
    growth: number;
    recruitment: number;
    churn: number;
  }[];
}

export default function AllOffices() {
  const [offices, setOffices] = useState<Office[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedOffice, setExpandedOffice] = useState<string | null>(null);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/offices')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch offices');
        return res.json();
      })
      .then(data => {
        setOffices(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const calculateDelta = (office: Office) => {
    if (!office.metrics || office.metrics.length < 2) return 0;
    const current = office.metrics[office.metrics.length - 1];
    const previous = office.metrics[office.metrics.length - 2];
    return current.growth;
  };

  const toggleOfficeExpansion = (officeName: string) => {
    setExpandedOffice(expandedOffice === officeName ? null : officeName);
  };

  return (
    <div className="space-y-8">
      {/* Filters */}
      <div className="flex flex-wrap gap-4 items-center mb-4">
        <select className="p-2 rounded border text-gray-700 dark:bg-gray-900 dark:text-gray-100 dark:border-gray-700">
          <option>Company</option>
        </select>
        <select className="p-2 rounded border text-gray-700 dark:bg-gray-900 dark:text-gray-100 dark:border-gray-700">
          <option>Journey</option>
        </select>
        <select className="p-2 rounded border text-gray-700 dark:bg-gray-900 dark:text-gray-100 dark:border-gray-700">
          <option>Sort: Name</option>
          <option>Sort: Headcount</option>
          <option>Sort: Growth</option>
        </select>
      </div>

      {loading ? (
        <div className="text-center text-gray-500 dark:text-gray-300">Loading offices...</div>
      ) : error ? (
        <div className="text-center text-red-500">{error}</div>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Office</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Journey</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Total FTE</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Delta</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Growth %</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Non-Debit Ratio</th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {offices.map(office => {
                const delta = calculateDelta(office);
                const growthPercentage = office.metrics?.[office.metrics.length - 1]?.growth || 0;
                const nonDebitRatio = office.metrics?.[office.metrics.length - 1]?.non_debit_ratio;
                const isExpanded = expandedOffice === office.name;

                return (
                  <React.Fragment key={office.name}>
                    <tr 
                      className="hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                      onClick={() => toggleOfficeExpansion(office.name)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100">
                        <div className="flex items-center">
                          <span className="mr-2">{isExpanded ? '▼' : '▶'}</span>
                          {office.name}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{office.journey}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{office.total_fte}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`${delta > 0 ? 'text-green-600 dark:text-green-400' : delta < 0 ? 'text-red-600 dark:text-red-400' : 'text-gray-500 dark:text-gray-300'}`}>
                          {delta > 0 ? '+' : ''}{delta}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`${growthPercentage > 0 ? 'text-green-600 dark:text-green-400' : growthPercentage < 0 ? 'text-red-600 dark:text-red-400' : 'text-gray-500 dark:text-gray-300'}`}>
                          {growthPercentage > 0 ? '+' : ''}{growthPercentage.toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">
                        {nonDebitRatio !== null ? nonDebitRatio.toFixed(2) : 'N/A'}
                      </td>
                    </tr>
                    {isExpanded && (
                      <tr className="bg-gray-50 dark:bg-gray-700">
                        <td colSpan={6} className="px-6 py-4">
                          <div className="space-y-4">
                            <div>
                              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Level Breakdown</h4>
                              <div className="grid grid-cols-4 gap-4">
                                {Object.entries(office.levels).map(([level, data]) => (
                                  <div key={level} className="text-sm">
                                    <span className="font-medium text-gray-700 dark:text-gray-300">{level}:</span>
                                    <span className="ml-2 text-gray-500 dark:text-gray-400">{data.total} FTE</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                            <div>
                              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Operations</h4>
                              <div className="text-sm text-gray-500 dark:text-gray-400">
                                Total: {office.operations.total} FTE
                              </div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
} 