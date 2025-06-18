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
  extractSeniorityKPIs(results: SimulationResults, year: string, baselineConfig?: OfficeConfig[], baselineYear: string = '2025'): any {
    const yearData = results.years?.[year];
    if (!yearData?.offices) return null;

    // Journey definitions (from backend config)
    const journeyDefinitions = {
      'Journey 1': ['A', 'AC', 'C'],    // A-C
      'Journey 2': ['SrC', 'AM'],       // SrC-AM
      'Journey 3': ['M', 'SrM'],        // M-SrM
      'Journey 4': ['PiP']              // PiP
    };

    let totalJourney1 = 0;
    let totalJourney2 = 0;
    let totalJourney3 = 0;
    let totalJourney4 = 0;
    let totalFTE = 0;
    let totalNonConsultant = 0;

    // Calculate baseline values if config is provided
    let baselineJourney1 = 0;
    let baselineJourney2 = 0;
    let baselineJourney3 = 0;
    let baselineJourney4 = 0;
    let baselineTotalFTE = 0;
    let baselineNonConsultant = 0;

    if (baselineConfig) {
      baselineConfig.forEach(office => {
        const roles = office.roles || {};
        
        // Calculate baseline journey totals based on definitions
        Object.entries(journeyDefinitions).forEach(([journeyName, levels]) => {
          let journeyTotal = 0;
          levels.forEach(level => {
            ['Consultant', 'Sales', 'Recruitment'].forEach(role => {
              if (roles[role] && roles[role][level]) {
                journeyTotal += roles[role][level].total || 0;
              }
            });
          });
          
          if (journeyName === 'Journey 1') baselineJourney1 += journeyTotal;
          else if (journeyName === 'Journey 2') baselineJourney2 += journeyTotal;
          else if (journeyName === 'Journey 3') baselineJourney3 += journeyTotal;
          else if (journeyName === 'Journey 4') baselineJourney4 += journeyTotal;
        });

        // Calculate baseline FTE and non-consultant totals
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

    Object.values(yearData.offices).forEach((officeData: any) => {
      // Calculate journey totals directly from levels data
      const officeLevels = officeData.levels || {};
      
      // Calculate current journey totals based on definitions
      Object.entries(journeyDefinitions).forEach(([journeyName, levelsList]) => {
        let journeyTotal = 0;
        levelsList.forEach(level => {
          journeyTotal += this.getLevelCount(officeLevels, level);
        });
        
        if (journeyName === 'Journey 1') totalJourney1 += journeyTotal;
        else if (journeyName === 'Journey 2') totalJourney2 += journeyTotal;
        else if (journeyName === 'Journey 3') totalJourney3 += journeyTotal;
        else if (journeyName === 'Journey 4') totalJourney4 += journeyTotal;
      });

      // Calculate non-debit ratio (non-consultant FTE / total FTE)
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

    // Calculate totals and percentages
    const grandTotal = totalJourney1 + totalJourney2 + totalJourney3 + totalJourney4;
    const baselineGrandTotal = baselineJourney1 + baselineJourney2 + baselineJourney3 + baselineJourney4;
    
    // Calculate journey percentages
    const journey1Percent = grandTotal > 0 ? Math.round((totalJourney1 / grandTotal) * 100) : 0;
    const journey2Percent = grandTotal > 0 ? Math.round((totalJourney2 / grandTotal) * 100) : 0;
    const journey3Percent = grandTotal > 0 ? Math.round((totalJourney3 / grandTotal) * 100) : 0;
    const journey4Percent = grandTotal > 0 ? Math.round((totalJourney4 / grandTotal) * 100) : 0;
    
    // Calculate baseline percentages
    const baselineJourney1Percent = baselineGrandTotal > 0 ? Math.round((baselineJourney1 / baselineGrandTotal) * 100) : 0;
    const baselineJourney2Percent = baselineGrandTotal > 0 ? Math.round((baselineJourney2 / baselineGrandTotal) * 100) : 0;
    const baselineJourney3Percent = baselineGrandTotal > 0 ? Math.round((baselineJourney3 / baselineGrandTotal) * 100) : 0;
    const baselineJourney4Percent = baselineGrandTotal > 0 ? Math.round((baselineJourney4 / baselineGrandTotal) * 100) : 0;
    
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
    const journey1GrowthRate = baselineJourney1 > 0 ? ((totalJourney1 - baselineJourney1) / baselineJourney1 * 100) : 0;
    const journey2GrowthRate = baselineJourney2 > 0 ? ((totalJourney2 - baselineJourney2) / baselineJourney2 * 100) : 0;
    const journey3GrowthRate = baselineJourney3 > 0 ? ((totalJourney3 - baselineJourney3) / baselineJourney3 * 100) : 0;
    const journey4GrowthRate = baselineJourney4 > 0 ? ((totalJourney4 - baselineJourney4) / baselineJourney4 * 100) : 0;

    return {
      // Journey data with detailed breakdown like Total Growth
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
      
      // Growth KPIs
      totalGrowthRate: `${totalGrowthRate >= 0 ? '+' : ''}${totalGrowthRate.toFixed(1)}%`,
      totalGrowthDetails: {
        percentage: `${totalGrowthRate >= 0 ? '+' : ''}${totalGrowthRate.toFixed(1)}%`,
        current: grandTotal,
        baseline: baselineGrandTotal,
        absolute: totalGrowthAbsolute,
        absoluteDisplay: `${totalGrowthAbsolute >= 0 ? '+' : ''}${totalGrowthAbsolute} FTE`
      },
      journey1GrowthRate: `${journey1GrowthRate >= 0 ? '+' : ''}${journey1GrowthRate.toFixed(1)}%`,
      journey2GrowthRate: `${journey2GrowthRate >= 0 ? '+' : ''}${journey2GrowthRate.toFixed(1)}%`,
      journey3GrowthRate: `${journey3GrowthRate >= 0 ? '+' : ''}${journey3GrowthRate.toFixed(1)}%`,
      journey4GrowthRate: `${journey4GrowthRate >= 0 ? '+' : ''}${journey4GrowthRate.toFixed(1)}%`,
      
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
        absoluteDisplay: `${nonDebitRatio - baselineNonDebitRatio >= 0 ? '+' : ''}${(nonDebitRatio - baselineNonDebitRatio).toFixed(1)}pp`
      },
      
      // Baseline information
      baselineYear: baselineYear,
      hasBaseline: !!baselineConfig,
      
      // Summary values for display
      journey1Display: `${totalJourney1} (${journey1Percent}%)`,
      journey2Display: `${totalJourney2} (${journey2Percent}%)`,
      journey3Display: `${totalJourney3} (${journey3Percent}%)`,
      journey4Display: `${totalJourney4} (${journey4Percent}%)`,
      nonDebitRatioDisplay: `${nonDebitRatio}%`
    };
  }
}

export const simulationApi = new SimulationApiService();
export type { SimulationRequest, OfficeConfig, SimulationResults, YearNavigationRequest, YearComparisonRequest }; 