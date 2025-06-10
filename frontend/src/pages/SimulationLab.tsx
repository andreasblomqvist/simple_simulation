import React, { useState } from 'react';

const LEVELS = ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"];

export default function SimulationLab() {
  const [form, setForm] = useState({
    start_year: 2024,
    start_half: 'H1',
    end_year: 2025,
    end_half: 'H2',
    price_increase: 0.03,
    salary_increase: 0.03,
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch('http://127.0.0.1:8000/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...form,
          start_year: Number(form.start_year),
          end_year: Number(form.end_year),
          price_increase: Number(form.price_increase),
          salary_increase: Number(form.salary_increase),
        }),
      });
      if (!res.ok) throw new Error('Simulation failed');
      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Helper to extract the first and last period's data for each office
  const getOfficeKPIData = () => {
    if (!result || !result.offices) return [];
    const offices = result.offices;
    const periods = result.periods || [];
    const firstIdx = 0;
    const lastIdx = periods.length - 1;
    return Object.entries(offices).map(([officeName, officeData]: any) => {
      const levels = officeData.levels;
      const operations = officeData.operations;
      const metrics = officeData.metrics;
      // Get values for each level
      const levelTotalsFirst: { [key: string]: number } = {};
      const levelTotalsLast: { [key: string]: number } = {};
      LEVELS.forEach(level => {
        levelTotalsFirst[level] = levels[level]?.[firstIdx]?.total ?? 0;
        levelTotalsLast[level] = levels[level]?.[lastIdx]?.total ?? 0;
      });
      // Get operations
      const opsTotalFirst = operations?.[firstIdx]?.total ?? 0;
      const opsTotalLast = operations?.[lastIdx]?.total ?? 0;
      // Get metrics
      const firstMetrics = metrics?.[firstIdx] || {};
      const lastMetrics = metrics?.[lastIdx] || {};
      // Calculate total FTEs
      const totalFTEFirst = Object.values(levelTotalsFirst).reduce((a, b) => a + b, 0) + opsTotalFirst;
      const totalFTELast = Object.values(levelTotalsLast).reduce((a, b) => a + b, 0) + opsTotalLast;
      // Delta
      const delta = totalFTELast - totalFTEFirst;
      // Use office_journey if present, else fallback
      const journeyName = officeData.office_journey || '';
      return {
        name: officeName,
        journey: journeyName,
        total_fte: totalFTELast,
        delta,
        levelTotals: levelTotalsLast,
        opsTotal: opsTotalLast,
        kpis: {
          growth: lastMetrics.growth ?? 0,
          recruitment: lastMetrics.recruitment ?? 0,
          churn: lastMetrics.churn ?? 0,
          non_debit_ratio: lastMetrics.non_debit_ratio ?? null,
        },
      };
    });
  };

  const officeKPIData = getOfficeKPIData();

  // Aggregate KPIs for cards
  const getAggregatedKPIs = () => {
    if (!result || !result.offices) return null;
    const offices = result.offices;
    const periods = result.periods || [];
    const lastIdx = periods.length - 1;
    // Aggregate journey totals
    const journeyTotals: { 'Journey 1': number; 'Journey 2': number; 'Journey 3': number; 'Journey 4': number } = { 'Journey 1': 0, 'Journey 2': 0, 'Journey 3': 0, 'Journey 4': 0 };
    let totalConsultants = 0;
    let totalNonConsultants = 0;
    (['Journey 1', 'Journey 2', 'Journey 3', 'Journey 4'] as const).forEach(j => { journeyTotals[j] = 0; });
    Object.values(offices).forEach((officeData: any) => {
      // Sum journeys
      if (officeData.journeys) {
        (['Journey 1', 'Journey 2', 'Journey 3', 'Journey 4'] as const).forEach(j => {
          const arr = officeData.journeys[j];
          if (arr && arr[lastIdx]) {
            journeyTotals[j] += arr[lastIdx].total || 0;
          }
        });
      }
      // For non-debit ratio: sum all consultants and non-consultants
      if (officeData.metrics && officeData.metrics[lastIdx]) {
        // Recompute for accuracy: sum all levels except operations
        if (officeData.levels) {
          Object.entries(officeData.levels).forEach(([level, arr]: any) => {
            if (arr && arr[lastIdx]) totalConsultants += arr[lastIdx].total || 0;
          });
        }
        if (officeData.operations && officeData.operations[lastIdx]) {
          totalNonConsultants += officeData.operations[lastIdx].total || 0;
        }
      }
    });
    const totalJourney = journeyTotals['Journey 1'] + journeyTotals['Journey 2'] + journeyTotals['Journey 3'] + journeyTotals['Journey 4'];
    const overallNonDebitRatio = totalNonConsultants > 0 ? (totalConsultants / totalNonConsultants) : null;
    return { journeyTotals, totalJourney, overallNonDebitRatio };
  };

  const aggregatedKPIs = getAggregatedKPIs();

  return (
    <div className="space-y-8">
      {/* Scenario Tabs */}
      <div className="flex gap-2 mb-4">
        <button className="px-4 py-2 rounded bg-blue-100 dark:bg-gray-700 text-blue-700 dark:text-blue-300 font-semibold">Current Pyramid</button>
        <button className="px-4 py-2 rounded bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 font-semibold">Target Pyramid</button>
        <button className="px-4 py-2 rounded bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 font-semibold">Step-by-Step</button>
      </div>
      {/* Simulation Form */}
      <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 space-y-4">
        <div className="font-semibold text-blue-700 dark:text-blue-400 mb-4">Simulation Parameters</div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-gray-600 dark:text-gray-300 mb-1">Start Year</label>
            <input name="start_year" type="number" value={form.start_year} onChange={handleChange} className="p-2 rounded border w-full dark:bg-gray-900 dark:text-gray-100 dark:border-gray-700" />
          </div>
          <div>
            <label className="block text-gray-600 dark:text-gray-300 mb-1">Start Half</label>
            <select name="start_half" value={form.start_half} onChange={handleChange} className="p-2 rounded border w-full dark:bg-gray-900 dark:text-gray-100 dark:border-gray-700">
              <option value="H1">H1</option>
              <option value="H2">H2</option>
            </select>
          </div>
          <div>
            <label className="block text-gray-600 dark:text-gray-300 mb-1">End Year</label>
            <input name="end_year" type="number" value={form.end_year} onChange={handleChange} className="p-2 rounded border w-full dark:bg-gray-900 dark:text-gray-100 dark:border-gray-700" />
          </div>
          <div>
            <label className="block text-gray-600 dark:text-gray-300 mb-1">End Half</label>
            <select name="end_half" value={form.end_half} onChange={handleChange} className="p-2 rounded border w-full dark:bg-gray-900 dark:text-gray-100 dark:border-gray-700">
              <option value="H1">H1</option>
              <option value="H2">H2</option>
            </select>
          </div>
          <div>
            <label className="block text-gray-600 dark:text-gray-300 mb-1">Price Increase (%)</label>
            <input name="price_increase" type="number" step="0.01" value={form.price_increase} onChange={handleChange} className="p-2 rounded border w-full dark:bg-gray-900 dark:text-gray-100 dark:border-gray-700" />
          </div>
          <div>
            <label className="block text-gray-600 dark:text-gray-300 mb-1">Salary Increase (%)</label>
            <input name="salary_increase" type="number" step="0.01" value={form.salary_increase} onChange={handleChange} className="p-2 rounded border w-full dark:bg-gray-900 dark:text-gray-100 dark:border-gray-700" />
          </div>
        </div>
        <button type="submit" className="px-6 py-3 rounded bg-blue-600 dark:bg-blue-800 text-white font-bold shadow" disabled={loading}>
          {loading ? 'Running...' : 'Run Simulation'}
        </button>
        {error && <div className="text-red-500 mt-2">{error}</div>}
      </form>
      {/* KPI Cards */}
      {aggregatedKPIs && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-blue-100 dark:bg-blue-900 rounded-lg p-4 flex flex-col items-center">
            <div className="text-xs text-gray-500 dark:text-gray-300 mb-1">Journey 1</div>
            <div className="text-2xl font-bold text-blue-700 dark:text-blue-200">{aggregatedKPIs.journeyTotals['Journey 1']}</div>
            <div className="text-xs text-gray-500 dark:text-gray-300">{aggregatedKPIs.totalJourney > 0 ? ((aggregatedKPIs.journeyTotals['Journey 1'] / aggregatedKPIs.totalJourney) * 100).toFixed(1) : '0.0'}%</div>
          </div>
          <div className="bg-yellow-100 dark:bg-yellow-900 rounded-lg p-4 flex flex-col items-center">
            <div className="text-xs text-gray-500 dark:text-gray-300 mb-1">Journey 2</div>
            <div className="text-2xl font-bold text-yellow-700 dark:text-yellow-200">{aggregatedKPIs.journeyTotals['Journey 2']}</div>
            <div className="text-xs text-gray-500 dark:text-gray-300">{aggregatedKPIs.totalJourney > 0 ? ((aggregatedKPIs.journeyTotals['Journey 2'] / aggregatedKPIs.totalJourney) * 100).toFixed(1) : '0.0'}%</div>
          </div>
          <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-4 flex flex-col items-center">
            <div className="text-xs text-gray-500 dark:text-gray-300 mb-1">Journey 3</div>
            <div className="text-2xl font-bold text-gray-700 dark:text-gray-200">{aggregatedKPIs.journeyTotals['Journey 3']}</div>
            <div className="text-xs text-gray-500 dark:text-gray-300">{aggregatedKPIs.totalJourney > 0 ? ((aggregatedKPIs.journeyTotals['Journey 3'] / aggregatedKPIs.totalJourney) * 100).toFixed(1) : '0.0'}%</div>
          </div>
          <div className="bg-purple-100 dark:bg-purple-900 rounded-lg p-4 flex flex-col items-center">
            <div className="text-xs text-gray-500 dark:text-gray-300 mb-1">Journey 4</div>
            <div className="text-2xl font-bold text-purple-700 dark:text-purple-200">{aggregatedKPIs.journeyTotals['Journey 4']}</div>
            <div className="text-xs text-gray-500 dark:text-gray-300">{aggregatedKPIs.totalJourney > 0 ? ((aggregatedKPIs.journeyTotals['Journey 4'] / aggregatedKPIs.totalJourney) * 100).toFixed(1) : '0.0'}%</div>
          </div>
          <div className="bg-green-100 dark:bg-green-900 rounded-lg p-4 flex flex-col items-center">
            <div className="text-xs text-gray-500 dark:text-gray-300 mb-1">Non-Debit Ratio</div>
            <div className="text-2xl font-bold text-green-700 dark:text-green-200">{aggregatedKPIs.overallNonDebitRatio !== null ? aggregatedKPIs.overallNonDebitRatio.toFixed(2) : 'N/A'}</div>
          </div>
        </div>
      )}
      {/* Results Table with KPIs and Deltas */}
      {officeKPIData.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mt-4 overflow-x-auto">
          <div className="font-semibold text-blue-700 dark:text-blue-400 mb-2">Simulation Results (KPIs & Deltas)</div>
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700 text-xs">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-2 py-2 text-left font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Office</th>
                <th className="px-2 py-2 text-left font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Journey</th>
                <th className="px-2 py-2 text-left font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Total FTE</th>
                <th className="px-2 py-2 text-left font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Delta</th>
                <th className="px-2 py-2 text-left font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Growth %</th>
                <th className="px-2 py-2 text-left font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Recruitment</th>
                <th className="px-2 py-2 text-left font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Churn</th>
                <th className="px-2 py-2 text-left font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Non-Debit Ratio</th>
                {LEVELS.map(level => (
                  <th key={level} className="px-2 py-2 text-left font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{level}</th>
                ))}
                <th className="px-2 py-2 text-left font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Ops</th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {officeKPIData.map(office => (
                <tr key={office.name}>
                  <td className="px-2 py-2 whitespace-nowrap font-medium text-gray-900 dark:text-gray-100">{office.name}</td>
                  <td className="px-2 py-2 whitespace-nowrap text-gray-500 dark:text-gray-300">{office.journey}</td>
                  <td className="px-2 py-2 whitespace-nowrap text-gray-500 dark:text-gray-300">{office.total_fte}</td>
                  <td className={`px-2 py-2 whitespace-nowrap ${office.delta > 0 ? 'text-green-600 dark:text-green-400' : office.delta < 0 ? 'text-red-600 dark:text-red-400' : 'text-gray-500 dark:text-gray-300'}`}>{office.delta > 0 ? '+' : ''}{office.delta}</td>
                  <td className={`px-2 py-2 whitespace-nowrap ${office.kpis.growth > 0 ? 'text-green-600 dark:text-green-400' : office.kpis.growth < 0 ? 'text-red-600 dark:text-red-400' : 'text-gray-500 dark:text-gray-300'}`}>{office.kpis.growth?.toFixed(1)}%</td>
                  <td className="px-2 py-2 whitespace-nowrap text-gray-500 dark:text-gray-300">{office.kpis.recruitment}</td>
                  <td className="px-2 py-2 whitespace-nowrap text-gray-500 dark:text-gray-300">{office.kpis.churn}</td>
                  <td className="px-2 py-2 whitespace-nowrap text-gray-500 dark:text-gray-300">{office.kpis.non_debit_ratio !== null ? office.kpis.non_debit_ratio.toFixed(2) : 'N/A'}</td>
                  {LEVELS.map(level => (
                    <td key={level} className="px-2 py-2 whitespace-nowrap text-gray-500 dark:text-gray-300">{office.levelTotals[level]}</td>
                  ))}
                  <td className="px-2 py-2 whitespace-nowrap text-gray-500 dark:text-gray-300">{office.opsTotal}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {/* Results: Raw JSON for reference */}
      {result && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mt-4 overflow-x-auto">
          <div className="font-semibold text-blue-700 dark:text-blue-400 mb-2">Simulation Results (Raw)</div>
          <pre className="text-xs text-gray-700 dark:text-gray-200 whitespace-pre-wrap break-all max-h-96 overflow-y-auto">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
} 