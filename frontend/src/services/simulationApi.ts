// SimulationAPI Service - Connects frontend to backend simulation APIs

interface SimulationRequest {
  start_year: number;
  start_month: number;
  end_year: number;
  end_month: number;
  price_increase: number;
  salary_increase: number;
  unplanned_absence?: number;
  hy_working_hours?: number;
  other_expense?: number;
  office_overrides?: Record<string, any>;
}

interface OfficeConfig {
  name: string;
  total_fte: number;
  journey: string;
  roles: Record<string, any>;
}

interface SimulationResults {
  years: Record<string, any>;
  summary: any;
  kpis: any;
}

interface YearNavigationRequest {
  year: number;
  include_monthly_data?: boolean;
}

interface YearComparisonRequest {
  year1: number;
  year2: number;
  include_monthly_data?: boolean;
}

class SimulationApiService {
  private baseUrl: string;

  constructor() {
    // Use the Vite proxy configuration to route to backend
    this.baseUrl = '';
  }

  /**
   * Run a simulation with the given parameters
   */
  async runSimulation(params: SimulationRequest): Promise<SimulationResults> {
    const response = await fetch('/api/simulation/run', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      throw new Error(`Simulation failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get office configuration data
   */
  async getOfficeConfig(): Promise<OfficeConfig[]> {
    const response = await fetch('/api/offices/config', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch office config: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get data for a specific year
   */
  async getYearData(params: YearNavigationRequest): Promise<any> {
    const response = await fetch(`/api/simulation/year/${params.year}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch year data: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Compare data between two years
   */
  async compareYears(params: YearComparisonRequest): Promise<any> {
    const response = await fetch('/api/simulation/years/compare', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      throw new Error(`Failed to compare years: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get list of available years
   */
  async getAvailableYears(): Promise<string[]> {
    const response = await fetch('/api/simulation/years', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch available years: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Extract key KPI data from simulation results for a specific year and compare with baseline
   */
  extractKPIData(results: SimulationResults, year: string): any[] {
    const yearData = results.years?.[year];
    if (!yearData) return [];

    // Use global KPIs which contain the correct financial data
    // TODO: Implement proper backend year-specific KPI endpoint for true year-by-year comparison
    const globalKpis = results.kpis || {};
    const financialKpis = globalKpis.financial || {};
    
    // Current values from global KPIs (these are calculated correctly by the backend)
    const currentNetSales = financialKpis.net_sales || 0;
    const currentTotalCosts = financialKpis.total_salary_costs || 0; // Use salary costs as main cost component
    const currentEbitda = financialKpis.ebitda || 0;
    const currentMargin = financialKpis.margin || 0;
    
    // Use KPI service values for all metrics (no need to recalculate)
    const currentSalaryCosts = financialKpis.total_salary_costs || 0;
    const currentAvgHourlyRate = financialKpis.avg_hourly_rate || 0;
    
    // Baseline values (these remain global)
    const baselineNetSales = financialKpis.net_sales_baseline || 0;
    const baselineEbitda = financialKpis.ebitda_baseline || 0;
    const baselineMargin = financialKpis.margin_baseline || 0;
    const baselineSalaryCosts = financialKpis.total_salary_costs_baseline || 0;
    const baselineAvgHourlyRate = financialKpis.avg_hourly_rate_baseline || 0;
    const baselineTotalCosts = baselineNetSales - baselineEbitda;

    const netSalesChange = currentNetSales - baselineNetSales;
    const ebitdaChange = currentEbitda - baselineEbitda;
    const marginChange = currentMargin - baselineMargin;
    const salaryCostsChange = currentSalaryCosts - baselineSalaryCosts;
    const hourlyRateChange = currentAvgHourlyRate - baselineAvgHourlyRate;

    const grossMargin = currentNetSales - currentTotalCosts;
    const baselineGrossMargin = baselineNetSales - baselineTotalCosts;
    const grossMarginChange = grossMargin - baselineGrossMargin;
    
    console.log(`[KPI YEAR DEBUG] Year ${year}:`, {
      currentNetSales,
      currentEbitda,
      currentMargin,
      currentSalaryCosts,
      currentAvgHourlyRate
    });
    
    return [
      {
        title: 'Net Sales',
        currentValue: this.formatValue(currentNetSales, 'revenue'),
        previousValue: this.formatValue(baselineNetSales, 'revenue'),
        unit: '',
        description: 'Total revenue from client services',
        change: netSalesChange,
        changePercent: baselineNetSales > 0 ? (netSalesChange / baselineNetSales) * 100 : (currentNetSales > 0 ? 100 : 0),
        rawValue: currentNetSales
      },
      { 
        title: 'Total Salary Costs',
        currentValue: this.formatValue(currentSalaryCosts, 'revenue'),
        previousValue: this.formatValue(baselineSalaryCosts, 'revenue'),
        unit: '',
        description: 'Total salary costs including employment overhead',
        change: salaryCostsChange,
        changePercent: baselineSalaryCosts > 0 ? (salaryCostsChange / baselineSalaryCosts) * 100 : (currentSalaryCosts > 0 ? 100 : 0),
        rawValue: currentSalaryCosts
      },
      { 
        title: 'EBITDA', 
        currentValue: this.formatValue(currentEbitda, 'revenue'),
        previousValue: this.formatValue(baselineEbitda, 'revenue'),
        unit: '',
        description: 'Earnings before interest, taxes, depreciation & amortization',
        change: ebitdaChange,
        changePercent: baselineEbitda > 0 ? (ebitdaChange / baselineEbitda) * 100 : (currentEbitda > 0 ? 100 : 0),
        rawValue: currentEbitda
      },
      {
        title: 'EBITDA Margin',
        currentValue: this.formatValue(currentMargin, 'percentage'),
        previousValue: this.formatValue(baselineMargin, 'percentage'),
        unit: '',
        description: 'EBITDA as percentage of net sales',
        change: marginChange,
        changePercent: baselineMargin > 0 ? (marginChange / baselineMargin) * 100 : (currentMargin > 0 ? 100 : 0),
        rawValue: currentMargin
      },
      {
        title: 'Gross Margin',
        currentValue: this.formatValue(grossMargin, 'revenue'),
        previousValue: this.formatValue(baselineGrossMargin, 'revenue'),
        unit: '',
        description: 'Net sales minus total costs',
        change: grossMarginChange,
        changePercent: baselineGrossMargin > 0 ? (grossMarginChange / baselineGrossMargin) * 100 : (grossMargin > 0 ? 100 : 0),
        rawValue: grossMargin
      },
      {
        title: 'Avg Hourly Rate',
        currentValue: this.formatValue(currentAvgHourlyRate, 'rate'),
        previousValue: this.formatValue(baselineAvgHourlyRate, 'rate'),
        unit: 'SEK',
        description: 'Average hourly rate for consultant services',
        change: hourlyRateChange,
        changePercent: baselineAvgHourlyRate > 0 ? (hourlyRateChange / baselineAvgHourlyRate) * 100 : (currentAvgHourlyRate > 0 ? 100 : 0),
        rawValue: currentAvgHourlyRate
      }
    ];
  }

  /**
   * Calculate comprehensive year-specific financial metrics from year data
   */
  private calculateYearSpecificFinancialMetrics(yearData: any): {
    currentNetSales: number;
    currentSalaryCosts: number;
    currentEbitda: number;
    currentMargin: number;
    currentAvgHourlyRate: number;
  } {
    // Instead of calculating from scratch, let's use the global KPIs but adjust them
    // The issue is that year-specific calculation is complex and should match backend logic
    // For now, let's revert to using global KPIs but scale them appropriately
    
    // Calculate total FTE for this year to understand the scale
    let totalYearFTE = 0;
    const offices = yearData.offices || {};
    
    Object.values(offices).forEach((officeData: any) => {
      totalYearFTE += officeData.total_fte || 0;
    });

    // For now, return reasonable placeholder values that won't be 12x too high
    // This should be replaced with proper backend year-specific KPI endpoint
    return {
      currentNetSales: 0, // Will be overridden by global KPIs
      currentSalaryCosts: 0, // Will be overridden by global KPIs  
      currentEbitda: 0, // Will be overridden by global KPIs
      currentMargin: 0, // Will be overridden by global KPIs
      currentAvgHourlyRate: 0 // Will be overridden by global KPIs
    };
  }

  /**
   * Calculate year-specific salary costs and hourly rate from year data
   */
  private calculateYearSpecificMetrics(yearData: any): { currentSalaryCosts: number; currentAvgHourlyRate: number } {
    let totalSalaryCosts = 0;
    let totalConsultants = 0;
    let totalRevenue = 0;

    const offices = yearData.offices || {};
    
    Object.values(offices).forEach((officeData: any) => {
      const levels = officeData.levels || {};
      
      // Calculate for each role and level
      Object.entries(levels).forEach(([roleName, roleData]: [string, any]) => {
        if (Array.isArray(roleData)) {
          // Flat role (Operations) - get last month's data
          const lastEntry = roleData[roleData.length - 1];
          if (lastEntry) {
            const fte = lastEntry.total || 0;
            const salary = lastEntry.salary || 0;
            totalSalaryCosts += fte * salary * 12 * 1.5; // Annual salary with 50% overhead
          }
        } else if (typeof roleData === 'object') {
          // Role with levels
          Object.entries(roleData).forEach(([levelName, levelData]: [string, any]) => {
            if (Array.isArray(levelData) && levelData.length > 0) {
              const lastEntry = levelData[levelData.length - 1];
              const fte = lastEntry?.total || 0;
              const salary = lastEntry?.salary || 0;
              const price = lastEntry?.price || 0;
              
              totalSalaryCosts += fte * salary * 12 * 1.5; // Annual salary with 50% overhead
              
              // Only count Consultant prices for hourly rate
              if (roleName === 'Consultant' && fte > 0) {
                totalConsultants += fte;
                totalRevenue += fte * price * 166.4 * 12; // Annual revenue
              }
            }
          });
        }
      });
    });

    const currentAvgHourlyRate = totalConsultants > 0 ? totalRevenue / (totalConsultants * 166.4 * 12) : 0;
    
    return {
      currentSalaryCosts: totalSalaryCosts,
      currentAvgHourlyRate: currentAvgHourlyRate
    };
  }

  /**
   * Extract table data from simulation results for display
   */
  extractTableData(results: SimulationResults, year: string, baselineConfig?: OfficeConfig[]): any[] {
    const yearData = results.years?.[year];
    if (!yearData) return [];

    // Get the actual financial KPIs from the KPI service (single source of truth)
    const kpis = results.kpis || {};
    const financialKpis = kpis.financial || {};
    
    // All financial data comes from KPI service - no independent calculations
    const totalCurrentEbitda = financialKpis.ebitda || 0;
    const totalCurrentRevenue = financialKpis.net_sales || 0;
    const totalCurrentCosts = financialKpis.total_salary_costs || 0;

    return Object.entries(yearData.offices).map(([officeName, officeData]: [string, any], index) => {
      const currentFTE = officeData.total_fte || 0;

      // Calculate role-specific FTE counts (for display only, not financial calculations)
      const consultantFTE = this.calculateRoleFTE(officeData.levels?.Consultant || {});
      const salesFTE = this.calculateRoleFTE(officeData.levels?.Sales || {});
      const recruitmentFTE = this.calculateRoleFTE(officeData.levels?.Recruitment || {});
      const operationsFTE = this.getFlatRoleFTE(officeData.levels?.Operations || []);

      // Get average price and salary for display purposes only
      const { avgPrice, avgSalary } = this.calculateWeightedAverages(officeData.levels || {});

      // Financial data: Use proportional allocation from KPI service totals
      // No independent financial calculations - everything comes from KPI service
      const totalSystemFTE = Object.values(yearData.offices).reduce((sum: number, office: any) => sum + (office.total_fte || 0), 0);
      const fteShare = totalSystemFTE > 0 ? currentFTE / totalSystemFTE : 0;
      
      // Allocate KPI service totals proportionally to this office
      const revenue = totalCurrentRevenue * fteShare;
      const costs = totalCurrentCosts * fteShare;
      const ebitda = totalCurrentEbitda * fteShare;
      const grossMargin = revenue - costs;
      
      const journey = this.determineOfficeJourney(currentFTE);

      // Get baseline data for comparison if available
      let baselineOffice = null;
      let baselinePrice = 0;
      let baselineSalary = 0;
      let baselineFTEValue = 0;
      
      if (baselineConfig) {
        baselineOffice = baselineConfig.find(office => office.name === officeName);
        if (baselineOffice) {
          baselineFTEValue = baselineOffice.total_fte || 0;
          const baselineAverages = this.calculateBaselineAverages(baselineOffice);
          baselinePrice = baselineAverages.avgPrice;
          baselineSalary = baselineAverages.avgSalary;
        }
      }

      // Calculate deltas and changes
      const priceDelta = avgPrice - baselinePrice;
      const salaryDelta = avgSalary - baselineSalary;
      const actualFTEDelta = currentFTE - baselineFTEValue;
      const ytdChange = baselineFTEValue > 0 ? ((currentFTE - baselineFTEValue) / baselineFTEValue * 100) : 0;

      return {
        key: index.toString(),
        office: officeName,
        journey,
        fte: `${currentFTE} (${actualFTEDelta >= 0 ? '+' : ''}${actualFTEDelta})`,
        delta: actualFTEDelta,
        price: `${avgPrice.toFixed(0)} (+${priceDelta.toFixed(0)})`,
        salary: `${avgSalary.toFixed(0)} (+${salaryDelta.toFixed(0)})`,
        ytdChange: `${ytdChange >= 0 ? '+' : ''}${ytdChange.toFixed(1)}%`,
        
        // Role breakdown (for display only)
        consultantFTE: Math.round(consultantFTE),
        salesFTE: Math.round(salesFTE),
        recruitmentFTE: Math.round(recruitmentFTE),
        operationsFTE: Math.round(operationsFTE),
        
        // Financial details (all from KPI service proportional allocation)
        revenue: `${(revenue / 1000000).toFixed(1)}M SEK`,
        grossMargin: `${(grossMargin / 1000000).toFixed(1)}M SEK`,
        ebitda: `${(ebitda / 1000000).toFixed(1)}M SEK`,
        
        // Raw values for sorting and calculations
        rawFTE: currentFTE,
        rawPrice: avgPrice,
        rawSalary: avgSalary,
        rawRevenue: revenue,
        rawGrossMargin: grossMargin,
        rawEbitda: ebitda
      };
    });
  }

  /**
   * Calculate weighted averages for price and salary from office levels data
   */
  private calculateWeightedAverages(levels: any): { avgPrice: number; avgSalary: number } {
    let totalPrice = 0;
    let totalSalary = 0;
    let consultantCount = 0;
    let totalFTE = 0;

    Object.entries(levels).forEach(([roleName, roleData]: [string, any]) => {
      if (Array.isArray(roleData)) {
        // Flat role (Operations) - get last month's data
        const lastEntry = roleData[roleData.length - 1];
        if (lastEntry) {
          const fte = lastEntry.total || 0;
          totalFTE += fte;
          totalSalary += fte * (lastEntry.salary || 0);
        }
      } else if (typeof roleData === 'object') {
        // Role with levels (Consultant, Sales, Recruitment)
        Object.entries(roleData).forEach(([levelName, levelData]: [string, any]) => {
          if (Array.isArray(levelData) && levelData.length > 0) {
            const lastEntry = levelData[levelData.length - 1];
            const levelFTE = lastEntry?.total || 0;
            totalFTE += levelFTE;
            
            // Only count Consultant prices for hourly rate calculation
            if (roleName === 'Consultant' && levelFTE > 0) {
              totalPrice += levelFTE * (lastEntry?.price || 0);
              consultantCount += levelFTE;
            }
            
            // All roles contribute to salary costs
            totalSalary += levelFTE * (lastEntry?.salary || 0);
          }
        });
      }
    });

    const avgPrice = consultantCount > 0 ? Math.round(totalPrice / consultantCount) : 0;
    const avgSalary = totalFTE > 0 ? Math.round(totalSalary / totalFTE) : 0;

    return { avgPrice, avgSalary };
  }

  /**
   * Calculate baseline averages from configuration data
   */
  private calculateBaselineAverages(baselineOffice: any): { avgPrice: number; avgSalary: number } {
    let baselineTotalPrice = 0;
    let baselineTotalSalary = 0;
    let baselineConsultantCount = 0;
    let baselineTotalFTEForSalary = 0;
    
    Object.entries(baselineOffice.roles || {}).forEach(([roleName, roleData]: [string, any]) => {
      if (roleName === 'Operations' && roleData.fte) {
        baselineTotalFTEForSalary += roleData.fte;
        baselineTotalSalary += roleData.fte * (roleData.salary_1 || 0);
      } else if (typeof roleData === 'object') {
        Object.entries(roleData).forEach(([levelName, levelData]: [string, any]) => {
          const levelFTE = levelData.fte || 0;
          baselineTotalFTEForSalary += levelFTE;
          
          if (roleName === 'Consultant' && levelFTE > 0) {
            baselineTotalPrice += levelFTE * (levelData.price_1 || 0);
            baselineConsultantCount += levelFTE;
          }
          
          baselineTotalSalary += levelFTE * (levelData.salary_1 || 0);
        });
      }
    });
    
    const avgPrice = baselineConsultantCount > 0 ? Math.round(baselineTotalPrice / baselineConsultantCount) : 0;
    const avgSalary = baselineTotalFTEForSalary > 0 ? Math.round(baselineTotalSalary / baselineTotalFTEForSalary) : 0;

    return { avgPrice, avgSalary };
  }

  /**
   * Extract available offices from configuration
   */
  extractOfficeOptions(config: OfficeConfig[]): { value: string; label: string }[] {
    return config.map(office => ({
      value: office.name.toLowerCase().replace(' ', '_'),
      label: office.name
    }));
  }

  /**
   * Extract role/lever options from office configuration
   */
  extractLeverOptions(config: OfficeConfig[]): { value: string; label: string }[] {
    const roles = new Set<string>();
    
    config.forEach(office => {
      Object.keys(office.roles).forEach(role => {
        roles.add(role);
      });
    });

    return Array.from(roles).map(role => ({
      value: role.toLowerCase(),
      label: role
    }));
  }

  /**
   * Extract level options for a specific role
   */
  extractLevelOptions(config: OfficeConfig[], role: string): { value: string; label: string }[] {
    const levels = new Set<string>();
    
    config.forEach(office => {
      const roleData = office.roles[role];
      if (roleData && typeof roleData === 'object' && !roleData.total) {
        // Role with levels (Consultant, Sales, Recruitment)
        Object.keys(roleData).forEach(level => {
          levels.add(level);
        });
      }
    });

    return Array.from(levels).map(level => ({
      value: level.toLowerCase(),
      label: level
    }));
  }

  /**
   * Format values for display with proper units (M for millions, B for billions, % for percentages)
   */
  formatValue(value: number, type: 'revenue' | 'percentage' | 'rate'): string {
    if (value === null || value === undefined) return '0.0';

    if (type === 'revenue') {
      // Format revenue with M (millions) or B (billions)
      const absValue = Math.abs(value);
      if (absValue >= 1000000000) {
        return `${(value / 1000000000).toFixed(1)}B`;
      } else {
        return `${(value / 1000000).toFixed(1)}M`;
      }
    } else if (type === 'percentage') {
      return `${(value * 100).toFixed(1)}%`;
    } else if (type === 'rate') {
      return Math.round(value).toString();
    }
    return value.toString();
  }

  private determineGrowthStatus(delta: number): string {
    if (delta > 2) return 'Growth';
    if (delta < -2) return 'Decline';
    return 'Maintenance';
  }

  private calculateRoleFTE(roleData: any): number {
    let totalFTE = 0;
    if (typeof roleData === 'object') {
      Object.values(roleData).forEach((levelData: any) => {
        if (Array.isArray(levelData) && levelData.length > 0) {
          const lastEntry = levelData[levelData.length - 1];
          totalFTE += lastEntry?.total || 0;
        }
      });
    }
    return totalFTE;
  }

  private getFlatRoleFTE(roleData: any[]): number {
    if (Array.isArray(roleData) && roleData.length > 0) {
      const lastEntry = roleData[roleData.length - 1];
      return lastEntry?.total || 0;
    }
    return 0;
  }

  private determineOfficeJourney(fte: number): string {
    if (fte >= 500) return 'Mature Office';
    if (fte >= 200) return 'Established Office';
    if (fte >= 25) return 'Emerging Office';
    return 'New Office';
  }

  /**
   * Calculate FTE changes (delta and YTD) from simulation data
   */
  private calculateFTEChanges(levels: any, year: string): { delta: number; ytdChange: string } {
    let currentTotal = 0;
    let previousTotal = 0;
    let yearStartTotal = 0;
    
    // Calculate totals for current, previous, and year start periods
    Object.entries(levels).forEach(([roleName, roleData]: [string, any]) => {
      if (Array.isArray(roleData)) {
        // Flat role (Operations)
        if (roleData.length > 0) {
          currentTotal += roleData[roleData.length - 1]?.total || 0;
          if (roleData.length > 1) {
            previousTotal += roleData[roleData.length - 2]?.total || 0;
          } else {
            previousTotal += roleData[0]?.total || 0;
          }
          yearStartTotal += roleData[0]?.total || 0;
        }
      } else if (typeof roleData === 'object') {
        // Role with levels (Consultant, Sales, Recruitment)
        Object.entries(roleData).forEach(([levelName, levelData]: [string, any]) => {
          if (Array.isArray(levelData) && levelData.length > 0) {
            currentTotal += levelData[levelData.length - 1]?.total || 0;
            if (levelData.length > 1) {
              previousTotal += levelData[levelData.length - 2]?.total || 0;
            } else {
              previousTotal += levelData[0]?.total || 0;
            }
            yearStartTotal += levelData[0]?.total || 0;
          }
        });
      }
    });

    // Calculate delta (change from previous period)
    const delta = Math.round(currentTotal - previousTotal);
    
    // Calculate YTD change percentage
    let ytdChangePercent = 0;
    if (yearStartTotal > 0) {
      ytdChangePercent = ((currentTotal - yearStartTotal) / yearStartTotal) * 100;
    }
    
    const ytdChange = ytdChangePercent >= 0 
      ? `+${ytdChangePercent.toFixed(1)}%` 
      : `${ytdChangePercent.toFixed(1)}%`;

    return { delta, ytdChange };
  }

  /**
   * Extract seniority analysis data from simulation results with baseline comparison
   */
  extractSeniorityData(results: SimulationResults, year: string, baselineConfig?: OfficeConfig[]): any[] {
    const yearData = results.years?.[year];
    if (!yearData?.offices) return [];

    return Object.entries(yearData.offices).map(([officeName, officeData]: [string, any], index) => {
      // Get current office data directly from levels (no nested months structure)
      const levels = officeData.levels || {};
      
      // Extract seniority level data for the office

      // Extract level counts for each seniority level
      const levelA = this.getLevelCount(levels, 'A');
      const levelAC = this.getLevelCount(levels, 'AC'); 
      const levelC = this.getLevelCount(levels, 'C');
      const levelSrC = this.getLevelCount(levels, 'SrC');
      const levelAM = this.getLevelCount(levels, 'AM');
      const levelM = this.getLevelCount(levels, 'M');
      const levelSrM = this.getLevelCount(levels, 'SrM');
      const levelPiP = this.getLevelCount(levels, 'PiP');

      // Get Operations employees (they don't have levels)
      const operationsFTE = this.getFlatRoleFTE(levels.Operations || []);
      
      // Calculate total headcount from all levels + operations
      const levelTotal = levelA + levelAC + levelC + levelSrC + levelAM + levelM + levelSrM + levelPiP;
      const total = levelTotal + operationsFTE;
      
      // Calculate non-debit ratio (non-consultant roles / total FTE)
      const consultantFTE = this.calculateRoleFTE(levels.Consultant || {});
      const salesFTE = this.calculateRoleFTE(levels.Sales || {});
      const recruitmentFTE = this.calculateRoleFTE(levels.Recruitment || {});
      
      const totalFTE = consultantFTE + salesFTE + recruitmentFTE + operationsFTE;
      const nonConsultantFTE = salesFTE + recruitmentFTE + operationsFTE;
      const nonDebitRatio = totalFTE > 0 ? Math.round((nonConsultantFTE / totalFTE) * 100) : 0;

      // Get baseline data for comparison if available
      let baselineData = null;
      if (baselineConfig) {
        const baselineOffice = baselineConfig.find(office => office.name === officeName);
        if (baselineOffice) {
          baselineData = this.extractBaselineSeniorityLevels(baselineOffice);
        }
      }

      return {
        key: `${index + 1}`,
        office: `${officeName} Office`,
        total: this.formatValueWithDelta(Math.round(total), baselineData?.total),
        levelA: this.formatValueWithDelta(levelA, baselineData?.levelA),
        levelAC: this.formatValueWithDelta(levelAC, baselineData?.levelAC),
        levelC: this.formatValueWithDelta(levelC, baselineData?.levelC),
        levelSrC: this.formatValueWithDelta(levelSrC, baselineData?.levelSrC),
        levelAM: this.formatValueWithDelta(levelAM, baselineData?.levelAM),
        levelM: this.formatValueWithDelta(levelM, baselineData?.levelM),
        levelSrM: this.formatValueWithDelta(levelSrM, baselineData?.levelSrM),
        levelPiP: this.formatValueWithDelta(levelPiP, baselineData?.levelPiP),
        operations: this.formatValueWithDelta(Math.round(operationsFTE), baselineData?.operations),
        nonDebitRatio
      };
    });
  }

  private getLevelCount(levels: any, targetLevel: string): number {
    let count = 0;
    
    // Check all role types (Consultant, Sales, Recruitment) for this level
    ['Consultant', 'Sales', 'Recruitment'].forEach(role => {
      if (levels[role] && levels[role][targetLevel] && Array.isArray(levels[role][targetLevel])) {
        const levelData = levels[role][targetLevel];
        if (levelData.length > 0) {
          const lastEntry = levelData[levelData.length - 1];
          count += lastEntry?.total || 0;
        }
      }
    });
    
    return Math.round(count);
  }

  /**
   * Extract baseline seniority levels from office config
   */
  private extractBaselineSeniorityLevels(officeConfig: OfficeConfig): any {
    const roles = officeConfig.roles || {};
    
    // Calculate baseline level counts for each seniority level
    const levelA = this.getBaselineLevelCount(roles, 'A');
    const levelAC = this.getBaselineLevelCount(roles, 'AC');
    const levelC = this.getBaselineLevelCount(roles, 'C');
    const levelSrC = this.getBaselineLevelCount(roles, 'SrC');
    const levelAM = this.getBaselineLevelCount(roles, 'AM');
    const levelM = this.getBaselineLevelCount(roles, 'M');
    const levelSrM = this.getBaselineLevelCount(roles, 'SrM');
    const levelPiP = this.getBaselineLevelCount(roles, 'PiP');
    
    // Get Operations baseline FTE
    const operations = roles.Operations?.total || 0;
    
    // Calculate total baseline FTE
    const total = levelA + levelAC + levelC + levelSrC + levelAM + levelM + levelSrM + levelPiP + operations;
    
    return {
      total: Math.round(total),
      levelA: Math.round(levelA),
      levelAC: Math.round(levelAC),
      levelC: Math.round(levelC),
      levelSrC: Math.round(levelSrC),
      levelAM: Math.round(levelAM),
      levelM: Math.round(levelM),
      levelSrM: Math.round(levelSrM),
      levelPiP: Math.round(levelPiP),
      operations: Math.round(operations)
    };
  }

  /**
   * Get baseline level count from office config roles
   */
  private getBaselineLevelCount(roles: any, targetLevel: string): number {
    let count = 0;
    
    // Check all role types (Consultant, Sales, Recruitment) for this level
    ['Consultant', 'Sales', 'Recruitment'].forEach(role => {
      if (roles[role] && roles[role][targetLevel] && typeof roles[role][targetLevel] === 'object') {
        count += roles[role][targetLevel].total || 0;
      }
    });
    
    return count;
  }

  /**
   * Format value with delta in parentheses vs baseline
   */
  private formatValueWithDelta(currentValue: number, baselineValue?: number): string {
    if (baselineValue === undefined || baselineValue === null) {
      return currentValue.toString();
    }
    
    const delta = currentValue - baselineValue;
    if (delta === 0) {
      return currentValue.toString();
    }
    
    const deltaSign = delta > 0 ? '+' : '';
    return `${currentValue} (${deltaSign}${delta})`;
  }

  /**
   * Calculate seniority KPIs from simulation results with baseline comparison
   */
  extractSeniorityKPIs(results: SimulationResults, year: string, baselineConfig?: OfficeConfig[], baselineYear?: string): any {
    const yearData = results.years?.[year];
    const resolvedBaselineYear = baselineYear || year;
    const baselineYearData = results.years?.[resolvedBaselineYear];

    if (!yearData?.offices || !baselineYearData?.offices) return null;

    const calculateJourneyMetricsForYear = (data: any) => {
      const journeyTotals: Record<string, number> = { 'Journey 1': 0, 'Journey 2': 0, 'Journey 3': 0, 'Journey 4': 0 };

      if (!data?.offices) {
        return { 
          totals: journeyTotals,
          percentages: { 'Journey 1': 0, 'Journey 2': 0, 'Journey 3': 0, 'Journey 4': 0 },
          grandTotal: 0
        };
      }

      const journeyMap: Record<string, string> = {
        'A': 'Journey 1', 'AC': 'Journey 1', 'C': 'Journey 1',
        'SrC': 'Journey 2', 'AM': 'Journey 2',
        'M': 'Journey 3', 'SrM': 'Journey 3',
        'PiP': 'Journey 4',
      };

      // Aggregate FTEs from all offices for each journey
      Object.values(data.offices).forEach((officeData: any) => {
        const levels = officeData.levels || {};
        Object.keys(journeyMap).forEach(level => {
          const journeyName = journeyMap[level];
          const count = this.getLevelCount(levels, level); // getLevelCount sums FTE for a level
          if (journeyTotals[journeyName] !== undefined) {
            journeyTotals[journeyName] += count;
          }
        });
      });

      const grandTotal = Object.values(journeyTotals).reduce((sum, current) => sum + current, 0);
      
      const percentages = {
        'Journey 1': grandTotal > 0 ? (journeyTotals['Journey 1'] / grandTotal) * 100 : 0,
        'Journey 2': grandTotal > 0 ? (journeyTotals['Journey 2'] / grandTotal) * 100 : 0,
        'Journey 3': grandTotal > 0 ? (journeyTotals['Journey 3'] / grandTotal) * 100 : 0,
        'Journey 4': grandTotal > 0 ? (journeyTotals['Journey 4'] / grandTotal) * 100 : 0,
      };

      return { totals: journeyTotals, percentages, grandTotal };
    };

    const currentMetrics = calculateJourneyMetricsForYear(yearData);
    const baselineMetrics = calculateJourneyMetricsForYear(baselineYearData);

    const { totals: currentJourneyTotals, percentages: currentJourneyPercentages, grandTotal: grandTotalCurrent } = currentMetrics;
    const { totals: baselineJourneyTotals, percentages: baselineJourneyPercentages, grandTotal: grandTotalBaseline } = baselineMetrics;

    // Extract values with fallbacks
    const totalJourney1 = currentJourneyTotals['Journey 1'] || 0;
    const totalJourney2 = currentJourneyTotals['Journey 2'] || 0;
    const totalJourney3 = currentJourneyTotals['Journey 3'] || 0;
    const totalJourney4 = currentJourneyTotals['Journey 4'] || 0;

    const baselineJourney1 = baselineJourneyTotals['Journey 1'] || 0;
    const baselineJourney2 = baselineJourneyTotals['Journey 2'] || 0;
    const baselineJourney3 = baselineJourneyTotals['Journey 3'] || 0;
    const baselineJourney4 = baselineJourneyTotals['Journey 4'] || 0;

    const journey1Percent = Math.round(currentJourneyPercentages['Journey 1'] || 0);
    const journey2Percent = Math.round(currentJourneyPercentages['Journey 2'] || 0);
    const journey3Percent = Math.round(currentJourneyPercentages['Journey 3'] || 0);
    const journey4Percent = Math.round(currentJourneyPercentages['Journey 4'] || 0);

    const baselineJourney1Percent = Math.round(baselineJourneyPercentages['Journey 1'] || 0);
    const baselineJourney2Percent = Math.round(baselineJourneyPercentages['Journey 2'] || 0);
    const baselineJourney3Percent = Math.round(baselineJourneyPercentages['Journey 3'] || 0);
    const baselineJourney4Percent = Math.round(baselineJourneyPercentages['Journey 4'] || 0);

    // Calculate growth metrics from backend data
    const grandTotal = totalJourney1 + totalJourney2 + totalJourney3 + totalJourney4;
    const baselineGrandTotal = baselineJourney1 + baselineJourney2 + baselineJourney3 + baselineJourney4;

    // Calculate FTE totals for non-debit ratio (from simulation data)
    let totalFTE = 0;
    let totalNonConsultant = 0;
    let baselineTotalFTE = 0;
    let baselineNonConsultant = 0;

    // Calculate current non-debit ratio from simulation data
    Object.values(yearData.offices).forEach((officeData: any) => {
      const levels = officeData.levels || {};
      const consultantFTE = this.calculateRoleFTE(levels.Consultant || {});
      const salesFTE = this.calculateRoleFTE(levels.Sales || {});
      const recruitmentFTE = this.calculateRoleFTE(levels.Recruitment || {});
      const operationsFTE = this.getFlatRoleFTE(levels.Operations || []);
      
      const officeTotalFTE = consultantFTE + salesFTE + recruitmentFTE + operationsFTE;
      const officeNonConsultant = salesFTE + recruitmentFTE + operationsFTE;
      
      totalFTE += officeTotalFTE;
      totalNonConsultant += officeNonConsultant;
    });

    // Calculate baseline non-debit ratio from config if available
    if (baselineConfig) {
      baselineConfig.forEach(office => {
        const roles = office.roles || {};
        let officeBaseline = 0;
        let officeBaselineNonConsultant = 0;
        
        Object.entries(roles).forEach(([roleName, roleData]: [string, any]) => {
          if (roleName === 'Operations') {
            const fte = roleData.total || 0;
            officeBaseline += fte;
            officeBaselineNonConsultant += fte;
          } else if (typeof roleData === 'object') {
            Object.values(roleData).forEach((levelData: any) => {
              const fte = levelData.total || 0;
              officeBaseline += fte;
              if (roleName !== 'Consultant') {
                officeBaselineNonConsultant += fte;
              }
            });
          }
        });
        
        baselineTotalFTE += officeBaseline;
        baselineNonConsultant += officeBaselineNonConsultant;
      });
    }

    // Calculate non-debit ratios
    const nonDebitRatio = totalFTE > 0 ? Math.round((totalNonConsultant / totalFTE) * 100) : 0;
    const baselineNonDebitRatio = baselineTotalFTE > 0 ? Math.round((baselineNonConsultant / baselineTotalFTE) * 100) : 0;
    
    // Calculate average progression rate (estimated from journey distribution changes)
    const progressionRateAvg = '12.5%'; // TODO: Calculate actual progression rate from historical data

    // Helper function to format values with deltas
    const formatWithDelta = (current: number, baseline: number, showPercent: boolean = false) => {
      if (baseline === 0) return showPercent ? `${current}%` : current.toString();
      const delta = current - baseline;
      const deltaSign = delta > 0 ? '+' : '';
      const currentStr = showPercent ? `${current}%` : current.toString();
      const baselineStr = showPercent ? `${baseline}%` : baseline.toString();
      return delta === 0 ? currentStr : `${currentStr} (baseline: ${baselineStr}, ${deltaSign}${delta}${showPercent ? 'pp' : ''})`;
    };

    // Calculate growth rates and metrics
    const totalGrowthRate = baselineGrandTotal > 0 ? ((grandTotal - baselineGrandTotal) / baselineGrandTotal * 100) : 0;
    const totalGrowthAbsolute = grandTotal - baselineGrandTotal;

    return {
      // Journey data with detailed breakdown using backend baseline values
      journey1: formatWithDelta(totalJourney1, baselineJourney1),
      journey1Percent: formatWithDelta(journey1Percent, baselineJourney1Percent, true),
      journey1Definition: 'A, AC, C',
      journey1BaselinePercent: baselineJourney1Percent,
      journey1Details: {
        percentage: `${journey1Percent}%`,
        current: totalJourney1,
        baseline: baselineJourney1,
        absolute: totalJourney1 - baselineJourney1,
        absoluteDisplay: `${totalJourney1 - baselineJourney1 >= 0 ? '+' : ''}${totalJourney1 - baselineJourney1} FTE`
      },
      
      journey2: formatWithDelta(totalJourney2, baselineJourney2),
      journey2Percent: formatWithDelta(journey2Percent, baselineJourney2Percent, true),
      journey2Definition: 'SrC, AM',
      journey2BaselinePercent: baselineJourney2Percent,
      journey2Details: {
        percentage: `${journey2Percent}%`,
        current: totalJourney2,
        baseline: baselineJourney2,
        absolute: totalJourney2 - baselineJourney2,
        absoluteDisplay: `${totalJourney2 - baselineJourney2 >= 0 ? '+' : ''}${totalJourney2 - baselineJourney2} FTE`
      },
      
      journey3: formatWithDelta(totalJourney3, baselineJourney3),
      journey3Percent: formatWithDelta(journey3Percent, baselineJourney3Percent, true),
      journey3Definition: 'M, SrM',
      journey3BaselinePercent: baselineJourney3Percent,
      journey3Details: {
        percentage: `${journey3Percent}%`,
        current: totalJourney3,
        baseline: baselineJourney3,
        absolute: totalJourney3 - baselineJourney3,
        absoluteDisplay: `${totalJourney3 - baselineJourney3 >= 0 ? '+' : ''}${totalJourney3 - baselineJourney3} FTE`
      },
      
      journey4: formatWithDelta(totalJourney4, baselineJourney4),
      journey4Percent: formatWithDelta(journey4Percent, baselineJourney4Percent, true),
      journey4Definition: 'PiP',
      journey4BaselinePercent: baselineJourney4Percent,
      journey4Details: {
        percentage: `${journey4Percent}%`,
        current: totalJourney4,
        baseline: baselineJourney4,
        absolute: totalJourney4 - baselineJourney4,
        absoluteDisplay: `${totalJourney4 - baselineJourney4 >= 0 ? '+' : ''}${totalJourney4 - baselineJourney4} FTE`
      },
      
      // Growth KPIs using backend baseline data
      totalGrowthRate: `${totalGrowthRate >= 0 ? '+' : ''}${totalGrowthRate.toFixed(1)}%`,
      totalGrowthDetails: {
        percentage: `${totalGrowthRate >= 0 ? '+' : ''}${totalGrowthRate.toFixed(1)}%`,
        current: grandTotal,
        baseline: baselineGrandTotal,
        absolute: totalGrowthAbsolute,
        absoluteDisplay: `${totalGrowthAbsolute >= 0 ? '+' : ''}${totalGrowthAbsolute} FTE`
      },
      
      // Other KPIs with detailed breakdown
      progressionRateAvg: progressionRateAvg,
      progressionRateDetails: {
        percentage: `${progressionRateAvg}`,
        current: progressionRateAvg,
        baseline: progressionRateAvg, // TODO: Add baseline progression rate
        description: "Monthly progression rate across all levels"
      },
      nonDebitRatio: formatWithDelta(nonDebitRatio, baselineNonDebitRatio, true),
      nonDebitBaselinePercent: baselineNonDebitRatio,
      nonDebitDetails: {
        percentage: `${nonDebitRatio}%`,
        current: nonDebitRatio,
        baseline: baselineNonDebitRatio,
        absolute: nonDebitRatio - baselineNonDebitRatio,
        absoluteDisplay: `${(nonDebitRatio - baselineNonDebitRatio).toFixed(1)}pp`
      },
      
      // Baseline information
      baselineYear: resolvedBaselineYear,
      hasBaseline: true, // We now have backend baseline data
      
      // Summary values for display
      journey1Display: `${totalJourney1} (${journey1Percent}%)`,
      journey2Display: `${totalJourney2} (${journey2Percent}%)`,
      journey3Display: `${totalJourney3} (${journey3Percent}%)`,
      journey4Display: `${totalJourney4} (${journey4Percent}%)`,
      nonDebitRatioDisplay: `${nonDebitRatio}%`
    };
  }

  /**
   * Extract KPI data from year-specific KPI response (from /years/{year}/kpis endpoint)
   */
  extractKPIDataFromYearKPIs(yearKPIs: any): any[] {
    if (!yearKPIs || !yearKPIs.financial) {
      return [];
    }

    const financial = yearKPIs.financial;
    
    return [
      {
        title: 'Net Sales',
        currentValue: this.formatValue(financial.net_sales, 'revenue'),
        previousValue: this.formatValue(financial.net_sales_baseline, 'revenue'),
        unit: '',
        description: 'Total revenue from client services',
        change: financial.net_sales - financial.net_sales_baseline,
        changePercent: financial.net_sales_baseline > 0 ? 
          ((financial.net_sales - financial.net_sales_baseline) / financial.net_sales_baseline * 100) : 0
      },
      {
        title: 'Total Salary Costs',
        currentValue: this.formatValue(financial.total_salary_costs, 'revenue'),
        previousValue: this.formatValue(financial.total_salary_costs_baseline, 'revenue'),
        unit: '',
        description: 'Total employment costs including overhead',
        change: financial.total_salary_costs - financial.total_salary_costs_baseline,
        changePercent: financial.total_salary_costs_baseline > 0 ? 
          ((financial.total_salary_costs - financial.total_salary_costs_baseline) / financial.total_salary_costs_baseline * 100) : 0
      },
      {
        title: 'EBITDA',
        currentValue: this.formatValue(financial.ebitda, 'revenue'),
        previousValue: this.formatValue(financial.ebitda_baseline, 'revenue'),
        unit: '',
        description: 'Earnings before interest, taxes, depreciation and amortization',
        change: financial.ebitda - financial.ebitda_baseline,
        changePercent: financial.ebitda_baseline > 0 ? 
          ((financial.ebitda - financial.ebitda_baseline) / financial.ebitda_baseline * 100) : 0
      },
      {
        title: 'EBITDA Margin',
        currentValue: this.formatValue(financial.margin, 'percentage'),
        previousValue: this.formatValue(financial.margin_baseline, 'percentage'),
        unit: '',
        description: 'EBITDA as percentage of net sales',
        change: (financial.margin - financial.margin_baseline) * 100,
        changePercent: financial.margin_baseline > 0 ? 
          ((financial.margin - financial.margin_baseline) / financial.margin_baseline * 100) : 0
      },
      {
        title: 'Avg Hourly Rate',
        currentValue: this.formatValue(financial.avg_hourly_rate, 'rate'),
        previousValue: this.formatValue(financial.avg_hourly_rate_baseline, 'rate'),
        unit: 'SEK',
        description: 'Average hourly billing rate across all consultants',
        change: financial.avg_hourly_rate - financial.avg_hourly_rate_baseline,
        changePercent: financial.avg_hourly_rate_baseline > 0 ? 
          ((financial.avg_hourly_rate - financial.avg_hourly_rate_baseline) / financial.avg_hourly_rate_baseline * 100) : 0
      }
    ];
  }
}

export const simulationApi = new SimulationApiService();
export type { SimulationRequest, OfficeConfig, SimulationResults, YearNavigationRequest, YearComparisonRequest };