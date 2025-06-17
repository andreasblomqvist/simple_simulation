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
   * Extract KPI data from simulation results for display
   */
  extractKPIData(results: SimulationResults, year: string): any[] {
    const yearData = results.years?.[year];
    if (!yearData) return [];

    const summary = yearData.summary || {};
    const kpis = results.kpis || {};

    // Calculate derived metrics from available data
    const totalRevenue = summary.total_revenue || 0;
    const totalCosts = summary.total_costs || 0;
    const totalProfit = summary.total_profit || 0;
    const averageMargin = summary.average_margin || 0;
    
    // Calculate gross margin (revenue - costs)
    const grossMargin = totalRevenue - totalCosts;
    
    // Calculate staff costs percentage
    const staffCostsPct = totalRevenue > 0 ? (totalCosts / totalRevenue) * 100 : 0;
    
    // Use KPI data if available (from successful KPI calculation)
    const financialKpis = kpis.financial || {};
    const currentEbitda = financialKpis.current_ebitda || totalProfit;
    const currentMargin = financialKpis.current_margin || (averageMargin * 100);

    return [
      {
        title: 'Net Sales',
        value: this.formatValue(totalRevenue, 'revenue'),
        unit: 'mSEK',
        trend: '↗',
        rawValue: totalRevenue
      },
      {
        title: 'Gross Margin',
        value: this.formatValue(grossMargin, 'revenue'),
        unit: 'mSEK',
        trend: '↗',
        rawValue: grossMargin
      },
      {
        title: 'EBITDA',
        value: this.formatValue(currentMargin, 'percentage'),
        unit: '%',
        trend: '↗',
        rawValue: currentMargin
      },
      {
        title: 'Total EBITDA',
        value: this.formatValue(currentEbitda, 'revenue'),
        unit: 'mSEK',
        trend: '↗',
        rawValue: currentEbitda
      },
      {
        title: 'Staff Costs',
        value: this.formatValue(staffCostsPct, 'percentage'),
        unit: '%',
        trend: '↗',
        rawValue: staffCostsPct
      },
      {
        title: 'Other Costs',
        value: this.formatValue(0, 'percentage'), // TODO: Add other costs calculation
        unit: '%',
        trend: '↗',
        rawValue: 0
      },
      {
        title: 'Commission EBITDA',
        value: this.formatValue(0, 'percentage'), // TODO: Add commission EBITDA calculation
        unit: '%',
        trend: '↗',
        rawValue: 0
      }
    ];
  }

  /**
   * Extract table data from simulation results for display
   */
  extractTableData(results: SimulationResults, year: string): any[] {
    const yearData = results.years?.[year];
    if (!yearData?.offices) return [];

    return Object.entries(yearData.offices).map(([officeName, officeData]: [string, any], index) => {
      // Calculate total FTE from all levels
      let currentFTE = 0;
      let totalPrice = 0;
      let totalSalary = 0;
      let consultantCount = 0;

      // Sum up FTE from all roles and levels
      if (officeData.levels) {
        Object.entries(officeData.levels).forEach(([roleName, roleData]: [string, any]) => {
          if (Array.isArray(roleData)) {
            // Flat role (Operations) - get last month's data
            const lastEntry = roleData[roleData.length - 1];
            if (lastEntry) {
              currentFTE += lastEntry.total || 0;
              if (roleName === 'Operations') {
                totalSalary += (lastEntry.total || 0) * (lastEntry.salary || 0);
              }
            }
          } else if (typeof roleData === 'object') {
            // Role with levels (Consultant, Sales, Recruitment)
            Object.entries(roleData).forEach(([levelName, levelData]: [string, any]) => {
              if (Array.isArray(levelData) && levelData.length > 0) {
                const lastEntry = levelData[levelData.length - 1];
                const levelFTE = lastEntry?.total || 0;
                currentFTE += levelFTE;
                
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
      }

      // Calculate averages
      const avgPrice = consultantCount > 0 ? Math.round(totalPrice / consultantCount) : 0;
      const avgSalary = currentFTE > 0 ? Math.round(totalSalary / currentFTE) : 0;

      // Calculate delta and YTD change from simulation data
      const { delta, ytdChange } = this.calculateFTEChanges(officeData.levels || {}, year);

      // Extract role-specific FTE counts for expanded view
      const consultantFTE = this.calculateRoleFTE(officeData.levels?.Consultant || {});
      const salesFTE = this.calculateRoleFTE(officeData.levels?.Sales || {});
      const recruitmentFTE = this.calculateRoleFTE(officeData.levels?.Recruitment || {});
      const operationsFTE = this.getFlatRoleFTE(officeData.levels?.Operations || []);

      // Calculate financial metrics (estimates for now)
      const revenue = consultantCount * avgPrice * 166.4 * 12 || 0; // Estimated annual revenue
      const grossMargin = revenue - (currentFTE * avgSalary * 12) || 0; // Revenue - salary costs
      const ebitda = grossMargin * 0.17 || 0; // Estimated 17% EBITDA margin
      const journey = this.determineOfficeJourney(currentFTE);

      return {
        key: `${index + 1}`,
        office: `${officeName} Office`,
        monthlyRate: this.determineGrowthStatus(delta),
        fte: currentFTE,
        delta: delta,
        price: avgPrice,
        salary: avgSalary,
        ytdChange: ytdChange,
        // Additional fields for expanded view
        consultantFTE: Math.round(consultantFTE),
        salesFTE: Math.round(salesFTE),
        recruitmentFTE: Math.round(recruitmentFTE),
        operationsFTE: Math.round(operationsFTE),
        revenue: revenue > 0 ? `${(revenue / 1000000).toFixed(1)}M SEK` : 'N/A',
        grossMargin: grossMargin > 0 ? `${(grossMargin / 1000000).toFixed(1)}M SEK` : 'N/A',
        ebitda: ebitda > 0 ? `${(ebitda / 1000000).toFixed(1)}M SEK` : 'N/A',
        office_journey: journey,
      };
    });
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

  private formatValue(value: number, type: 'revenue' | 'percentage'): string {
    if (type === 'revenue') {
      return (value / 1000000).toFixed(1); // Convert to millions
    } else if (type === 'percentage') {
      return value.toFixed(1);
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
   * Extract seniority analysis data from simulation results
   */
  extractSeniorityData(results: SimulationResults, year: string): any[] {
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

      return {
        key: `${index + 1}`,
        office: `${officeName} Office`,
        total: Math.round(total),
        levelA,
        levelAC,
        levelC,
        levelSrC,
        levelAM,
        levelM,
        levelSrM,
        levelPiP,
        operations: Math.round(operationsFTE),
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
   * Calculate seniority KPIs from simulation results
   */
  extractSeniorityKPIs(results: SimulationResults, year: string): any {
    const yearData = results.years?.[year];
    if (!yearData?.offices) return null;

    let totalJunior = 0;
    let totalSenior = 0;
    let totalProgression = 0;
    let officeCount = 0;

    Object.values(yearData.offices).forEach((officeData: any) => {
      // Get data directly from levels (no nested months structure)
      const levels = officeData.levels || {};

      // Count junior levels (A, AC, C)
      const juniorCount = this.getLevelCount(levels, 'A') + 
                         this.getLevelCount(levels, 'AC') + 
                         this.getLevelCount(levels, 'C');

      // Count senior levels (SrC, AM, M, SrM, PiP)
      const seniorCount = this.getLevelCount(levels, 'SrC') + 
                         this.getLevelCount(levels, 'AM') + 
                         this.getLevelCount(levels, 'M') + 
                         this.getLevelCount(levels, 'SrM') + 
                         this.getLevelCount(levels, 'PiP');

      totalJunior += juniorCount;
      totalSenior += seniorCount;
      officeCount++;
    });

    const totalHeadcount = totalJunior + totalSenior;
    const juniorPercent = totalHeadcount > 0 ? Math.round((totalJunior / totalHeadcount) * 100) : 0;
    const seniorPercent = totalHeadcount > 0 ? Math.round((totalSenior / totalHeadcount) * 100) : 0;

    return {
      juniorGrowth: '+15.2%', // TODO: Calculate from historical data
      seniorGrowth: '+8.7%',  // TODO: Calculate from historical data  
      progressionRate: '12.5%', // TODO: Calculate from progression data
      seniorityRatio: `${juniorPercent}:${seniorPercent}`
    };
  }
}

export const simulationApi = new SimulationApiService();
export type { SimulationRequest, OfficeConfig, SimulationResults, YearNavigationRequest, YearComparisonRequest }; 