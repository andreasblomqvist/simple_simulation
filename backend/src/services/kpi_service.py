from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from backend.config.default_config import ACTUAL_OFFICE_LEVEL_DATA, JOURNEY_CLASSIFICATION, BASE_PRICING, BASE_SALARIES

@dataclass
class FinancialKPIs:
    """Financial KPI results"""
    net_sales: float
    net_sales_baseline: float
    total_salary_costs: float
    total_salary_costs_baseline: float
    ebitda: float
    ebitda_baseline: float
    margin: float
    margin_baseline: float
    total_consultants: int
    total_consultants_baseline: int
    avg_hourly_rate: float
    avg_hourly_rate_baseline: float
    avg_utr: float

@dataclass
class GrowthKPIs:
    """Growth and headcount KPI results"""
    total_growth_percent: float
    total_growth_absolute: int
    current_total_fte: int
    baseline_total_fte: int
    non_debit_ratio: float
    non_debit_ratio_baseline: float
    non_debit_delta: float

@dataclass
class JourneyKPIs:
    """Career journey distribution KPIs"""
    journey_totals: Dict[str, int]
    journey_percentages: Dict[str, float]
    journey_deltas: Dict[str, float]
    journey_totals_baseline: Dict[str, int]
    journey_percentages_baseline: Dict[str, float]

@dataclass
class YearlyKPIs:
    """Year-specific KPI results"""
    year: str
    financial: FinancialKPIs
    growth: GrowthKPIs
    journeys: JourneyKPIs
    year_over_year_growth: float
    year_over_year_margin_change: float

@dataclass
class AllKPIs:
    """Combined KPI results"""
    financial: FinancialKPIs
    growth: GrowthKPIs
    journeys: JourneyKPIs
    yearly_kpis: Dict[str, YearlyKPIs]

class KPIService:
    """Service for calculating all simulation KPIs"""
    
    def __init__(self):
        self.working_hours_per_month = 166.4  # Actual working hours per month
        self.total_employment_cost_rate = 0.5  # 50% overhead on salary costs
        self.default_other_expense = 19000000.0  # 19 million SEK per month globally
    
    def calculate_all_kpis(
        self, 
        simulation_results: Dict[str, Any], 
        simulation_duration_months: int,
        unplanned_absence: float = 0.05,
        other_expense: float = None
    ) -> AllKPIs:
        """Calculate all KPIs from simulation results"""
        print(f"[KPI] Starting KPI calculation for {simulation_duration_months} months...")
        
        # Use default other expense if not provided
        if other_expense is None:
            other_expense = self.default_other_expense
        
        try:
            # Get baseline data from hardcoded config (avoid circular dependency)
            baseline_data = self._get_baseline_data()
            
            # Calculate baseline financial metrics
            baseline_financial = self._calculate_baseline_financial_metrics(
                baseline_data, 
                unplanned_absence, 
                other_expense,
                duration_months=simulation_duration_months
            )
            
            # Extract final year data for comparison
            years = list(simulation_results.get('years', {}).keys())
            if not years:
                raise ValueError("No simulation years found in results")
            
            final_year = max(years)
            final_year_data = simulation_results['years'][final_year]
            
            # Calculate current year financial metrics
            current_financial = self._calculate_current_financial_metrics(
                final_year_data,
                unplanned_absence,
                other_expense,
                duration_months=simulation_duration_months
            )
            
            # Calculate growth metrics
            growth_metrics = self._calculate_growth_metrics(
                baseline_data,
                final_year_data
            )
            
            # Calculate journey distribution
            journey_metrics = self._calculate_journey_metrics(final_year_data)
            
            # Create yearly KPIs for each year
            yearly_kpis = {}
            for year, year_data in simulation_results['years'].items():
                yearly_financial = self._calculate_current_financial_metrics(
                    year_data,
                    unplanned_absence,
                    other_expense,
                    duration_months=simulation_duration_months
                )
                
                # Create a simplified yearly KPI
                yearly_kpis[year] = YearlyKPIs(
                    year=year,
                    financial=FinancialKPIs(
                        net_sales=yearly_financial['total_revenue'],
                        net_sales_baseline=baseline_financial['total_revenue'],
                        total_salary_costs=yearly_financial['total_salary_costs'],
                        total_salary_costs_baseline=baseline_financial['total_salary_costs'],
                        ebitda=yearly_financial['ebitda'],
                        ebitda_baseline=baseline_financial['ebitda'],
                        margin=yearly_financial['margin'],
                        margin_baseline=baseline_financial['margin'],
                        total_consultants=yearly_financial.get('total_consultants', 0),
                        total_consultants_baseline=baseline_financial.get('total_consultants', 0),
                        avg_hourly_rate=yearly_financial['avg_hourly_rate'],
                        avg_hourly_rate_baseline=baseline_financial['avg_hourly_rate'],
                        avg_utr=0.85
                    ),
                    growth=growth_metrics,
                    journeys=journey_metrics,
                    year_over_year_growth=0.0,
                    year_over_year_margin_change=0.0
                )
            
            # Create financial KPIs
            financial_kpis = FinancialKPIs(
                net_sales=current_financial['total_revenue'],
                net_sales_baseline=baseline_financial['total_revenue'],
                total_salary_costs=current_financial['total_salary_costs'],
                total_salary_costs_baseline=baseline_financial['total_salary_costs'],
                ebitda=current_financial['ebitda'],
                ebitda_baseline=baseline_financial['ebitda'],
                margin=current_financial['margin'],
                margin_baseline=baseline_financial['margin'],
                total_consultants=current_financial.get('total_consultants', 0),
                total_consultants_baseline=baseline_financial.get('total_consultants', 0),
                avg_hourly_rate=current_financial['avg_hourly_rate'],
                avg_hourly_rate_baseline=baseline_financial['avg_hourly_rate'],
                avg_utr=0.85
            )
            
            print(f"[KPI DEBUG] =================== FINAL FINANCIAL CALCULATION ===================")
            print(f"[KPI DEBUG] Total Revenue: {current_financial['total_revenue']:,.0f} SEK")
            print(f"[KPI DEBUG] Total Salary Costs: {current_financial['total_salary_costs']:,.0f} SEK")
            print(f"[KPI DEBUG] Total Costs: {current_financial['total_costs']:,.0f} SEK")
            print(f"[KPI DEBUG] EBITDA: {current_financial['ebitda']:,.0f} SEK")
            print(f"[KPI DEBUG] Margin: {current_financial['margin']:.2%}")
            print(f"[KPI DEBUG] Avg Hourly Rate: {current_financial['avg_hourly_rate']:.2f} SEK")
            print(f"[KPI DEBUG] Baseline Total Revenue: {baseline_financial['total_revenue']:,.0f} SEK")
            print(f"[KPI DEBUG] Baseline Total Salary Costs: {baseline_financial['total_salary_costs']:,.0f} SEK")
            print(f"[KPI DEBUG] Baseline Total Costs: {baseline_financial['total_costs']:,.0f} SEK")
            print(f"[KPI DEBUG] Baseline EBITDA: {baseline_financial['ebitda']:,.0f} SEK")
            print(f"[KPI DEBUG] Baseline Margin: {baseline_financial['margin']:.2%}")
            print(f"[KPI DEBUG] ================================================================")
            
            return AllKPIs(
                financial=financial_kpis,
                growth=growth_metrics,
                journeys=journey_metrics,
                yearly_kpis=yearly_kpis
            )
            
        except Exception as e:
            import traceback
            print(f"[KPI ERROR] Exception in calculate_all_kpis: {e}")
            print(f"[KPI ERROR] Traceback: {traceback.format_exc()}")
            raise e
    
    def _get_baseline_data(self) -> Dict[str, Any]:
        """Get baseline data from hardcoded config to avoid circular dependency"""
        baseline = {
            'offices': [],
            'total_consultants': 0,
            'total_non_consultants': 0,
            'total_fte': 0
        }
        
        for office_name, office_data in ACTUAL_OFFICE_LEVEL_DATA.items():
            office_baseline = {
                'name': office_name,
                'roles': {},
                'consultants': 0,
                'non_consultants': 0,
                'total_fte': 0
            }
            
            for role_name, role_data in office_data.items():
                if role_name == 'Operations':
                    # Operations is a flat role with integer value
                    operations_fte = role_data  # role_data is directly an integer
                    office_baseline['roles']['Operations'] = {
                        'fte': operations_fte,
                        'price_1': 80.0,  # Default operations pricing
                        'salary_1': 40000.0,  # Default operations salary
                        'utr_1': 0.85
                    }
                    office_baseline['non_consultants'] += operations_fte
                    office_baseline['total_fte'] += operations_fte
                else:
                    # Roles with levels (Consultant, Sales, Recruitment)
                    office_baseline['roles'][role_name] = {}
                    for level_name, level_fte in role_data.items():
                        # level_fte is directly an integer, not a dict
                        # Get pricing from BASE_PRICING or use defaults
                        default_price = BASE_PRICING.get(office_name, {}).get(level_name, 1000.0)
                        default_salary = BASE_SALARIES.get(office_name, {}).get(level_name, 40000.0) # Use actual monthly salary
                        
                        office_baseline['roles'][role_name][level_name] = {
                            'fte': level_fte,
                            'price_1': default_price,
                            'salary_1': default_salary,
                            'utr_1': 0.85
                        }
                        
                        if role_name == 'Consultant':
                            office_baseline['consultants'] += level_fte
                        else:
                            office_baseline['non_consultants'] += level_fte
                        office_baseline['total_fte'] += level_fte
            
            baseline['offices'].append(office_baseline)
            baseline['total_consultants'] += office_baseline['consultants']
            baseline['total_non_consultants'] += office_baseline['non_consultants']
            baseline['total_fte'] += office_baseline['total_fte']
        
        return baseline
    
    def _calculate_baseline_financial_metrics(
        self, 
        baseline_data: Dict[str, Any], 
        unplanned_absence: float, 
        other_expense: float,
        duration_months: int = 12
    ) -> Dict[str, float]:
        """Calculate financial metrics for the baseline year based on architecture doc"""
        total_revenue = 0
        total_salary_costs = 0
        total_consultants = 0
        
        for office in baseline_data['offices']:
            for role_name, role_data in office['roles'].items():
                
                # Determine levels to process (handles both flat and leveled roles)
                levels_to_process = {None: role_data} if 'fte' in role_data else role_data

                for level_name, level_data in levels_to_process.items():
                    fte = level_data.get('fte', 0)
                    if fte == 0: continue

                    # Financial calculations per FTE
                    price = level_data.get('price_1', 0)
                    salary = level_data.get('salary_1', 0)
                    utr = level_data.get('utr_1', 0.85)

                    # Revenue is only generated by consultants
                    if role_name == 'Consultant':
                        monthly_revenue_per_fte = price * utr * self.working_hours_per_month * (1 - unplanned_absence)
                        total_revenue += fte * monthly_revenue_per_fte
                        total_consultants += fte
                    
                    # Salary costs are for all roles
                    monthly_salary_cost_per_fte = salary * (1 + self.total_employment_cost_rate)
                    total_salary_costs += fte * monthly_salary_cost_per_fte

        # Annualize for the full simulation period
        total_revenue *= duration_months
        total_salary_costs *= duration_months
        
        # Final calculations
        total_costs = total_salary_costs + (other_expense * duration_months)
        ebitda = total_revenue - total_costs
        margin = (ebitda / total_revenue) if total_revenue > 0 else 0
        avg_hourly_rate = (total_revenue / total_consultants / self.working_hours_per_month / duration_months) if total_consultants > 0 else 0

        return {
            'total_revenue': total_revenue,
            'total_salary_costs': total_salary_costs,
            'total_costs': total_costs,
            'ebitda': ebitda,
            'margin': margin,
            'total_consultants': total_consultants,
            'avg_hourly_rate': avg_hourly_rate
        }
    
    def _calculate_current_financial_metrics(
        self, 
        year_data: Dict[str, Any],
        unplanned_absence: float,
        other_expense: float,
        duration_months: int = 12
    ) -> Dict[str, float]:
        """Calculate financial metrics for current simulation data"""
        
        total_revenue = 0.0
        total_costs = 0.0
        total_salary_costs = 0.0  # Track salary costs separately
        total_consultants = 0
        total_weighted_price = 0.0
        
        # Process each office
        for office_name, office_data in year_data.get('offices', {}).items():
            office_levels = office_data.get('levels', {})
            
            # Only consultants generate revenue
            if 'Consultant' in office_levels:
                consultant_levels = office_levels['Consultant']
                for level_name, level_results in consultant_levels.items():
                    if level_results:  # Check if there are results for this level
                        # Debug: Print the data structure
                        print(f"[KPI DEBUG] {office_name} {level_name}: level_results type = {type(level_results)}, value = {level_results}")
                        
                        # Get the latest month's data
                        if isinstance(level_results, list) and len(level_results) > 0:
                            latest_data = level_results[-1]
                            print(f"[KPI DEBUG] {office_name} {level_name}: latest_data type = {type(latest_data)}, value = {latest_data}")
                        else:
                            print(f"[KPI DEBUG] {office_name} {level_name}: level_results is not a list or is empty")
                            latest_data = {}
                        
                        fte_count = latest_data.get('total', 0) if isinstance(latest_data, dict) else 0
                        hourly_rate = latest_data.get('price', 0) if isinstance(latest_data, dict) else 0
                        salary = latest_data.get('salary', 0) if isinstance(latest_data, dict) else 0
                        
                        if fte_count > 0:
                            # Calculate revenue (assume 85% UTR for now)
                            utr = 0.85
                            available_hours = self.working_hours_per_month * (1 - unplanned_absence)
                            billable_hours = available_hours * utr
                            monthly_revenue_per_person = hourly_rate * billable_hours
                            level_total_revenue = fte_count * monthly_revenue_per_person * duration_months
                            total_revenue += level_total_revenue
                            
                            # Calculate costs
                            base_salary_cost = fte_count * salary * duration_months
                            total_employment_cost = base_salary_cost * (1 + self.total_employment_cost_rate)
                            total_costs += total_employment_cost
                            total_salary_costs += base_salary_cost  # Track salary costs separately
                            
                            # Track for weighted averages
                            total_consultants += fte_count
                            total_weighted_price += hourly_rate * fte_count
            
            # Calculate costs for all other roles
            for role_name, role_data in office_levels.items():
                if role_name != 'Consultant':
                    if isinstance(role_data, list):
                        # Flat role like Operations
                        if role_data:
                            latest_data = role_data[-1]
                            fte_count = latest_data.get('total', 0)
                            salary = latest_data.get('salary', 0)
                            if fte_count > 0:
                                base_salary_cost = fte_count * salary * duration_months
                                total_employment_cost = base_salary_cost * (1 + self.total_employment_cost_rate)
                                total_costs += total_employment_cost
                                total_salary_costs += base_salary_cost  # Track salary costs separately
                    else:
                        # Role with levels
                        for level_name, level_results in role_data.items():
                            if level_results:
                                latest_data = level_results[-1]
                                fte_count = latest_data.get('total', 0)
                                salary = latest_data.get('salary', 0)
                                if fte_count > 0:
                                    base_salary_cost = fte_count * salary * duration_months
                                    total_employment_cost = base_salary_cost * (1 + self.total_employment_cost_rate)
                                    total_costs += total_employment_cost
                                    total_salary_costs += base_salary_cost  # Track salary costs separately
        
        # Add other expenses (global monthly cost, not per office)
        group_other_expenses = other_expense * duration_months
        total_costs += group_other_expenses
        
        # Calculate final metrics
        ebitda = total_revenue - total_costs
        margin = ebitda / total_revenue if total_revenue > 0 else 0.0
        avg_hourly_rate = total_weighted_price / total_consultants if total_consultants > 0 else 0.0
        
        print(f"[KPI DEBUG] CURRENT FINAL TOTALS:")
        print(f"[KPI DEBUG] Total Consultants: {total_consultants}")
        print(f"[KPI DEBUG] Total Revenue: {total_revenue:,.0f} SEK")
        print(f"[KPI DEBUG] Total Salary Costs: {total_salary_costs:,.0f} SEK")
        print(f"[KPI DEBUG] Total Costs (including overhead): {total_costs:,.0f} SEK")
        print(f"[KPI DEBUG] Other Expenses: {group_other_expenses:,.0f} SEK")
        print(f"[KPI DEBUG] EBITDA: {ebitda:,.0f} SEK")
        print(f"[KPI DEBUG] Margin: {margin:.2%}")
        
        return {
            'total_revenue': total_revenue,
            'total_costs': total_costs,
            'total_salary_costs': total_salary_costs,
            'ebitda': ebitda,
            'margin': margin,
            'avg_hourly_rate': avg_hourly_rate,
            'total_consultants': total_consultants
        }
    
    def _calculate_growth_metrics(self, baseline_data: Dict[str, Any], final_year_data: Dict[str, Any]) -> GrowthKPIs:
        """Calculate growth metrics comparing baseline to final year"""
        
        # Calculate baseline totals
        baseline_total_fte = baseline_data.get('total_fte', 0)
        baseline_consultants = baseline_data.get('total_consultants', 0)
        baseline_non_consultants = baseline_data.get('total_non_consultants', 0)
        
        # Calculate current totals from final year
        current_total_fte = 0
        current_consultants = 0
        current_non_consultants = 0
        senior_consultants = 0  # M, SrM, PiP levels
        
        for office_name, office_data in final_year_data.get('offices', {}).items():
            office_levels = office_data.get('levels', {})
            
            # Count consultants
            if 'Consultant' in office_levels:
                consultant_levels = office_levels['Consultant']
                for level_name, level_results in consultant_levels.items():
                    if level_results:
                        latest_data = level_results[-1] if level_results else {}
                        fte_count = latest_data.get('total', 0)
                        current_consultants += fte_count
                        current_total_fte += fte_count
                        
                        # Count senior levels
                        if level_name in ['M', 'SrM', 'PiP']:
                            senior_consultants += fte_count
            
            # Count other roles
            for role_name, role_data in office_levels.items():
                if role_name != 'Consultant':
                    if isinstance(role_data, list):
                        # Flat role like Operations
                        if role_data:
                            latest_data = role_data[-1]
                            fte_count = latest_data.get('total', 0)
                            current_non_consultants += fte_count
                            current_total_fte += fte_count
                    else:
                        # Role with levels
                        for level_name, level_results in role_data.items():
                            if level_results:
                                latest_data = level_results[-1] if level_results else {}
                                fte_count = latest_data.get('total', 0)
                                current_non_consultants += fte_count
                                current_total_fte += fte_count
        
        # Calculate growth rates
        total_growth_rate = ((current_total_fte - baseline_total_fte) / baseline_total_fte * 100) if baseline_total_fte > 0 else 0.0
        
        # Calculate non-debit ratio (senior consultants / total consultants)
        current_non_debit_ratio = (senior_consultants / current_consultants * 100) if current_consultants > 0 else 0.0
        baseline_senior = 0
        
        # Calculate baseline senior consultants
        for office in baseline_data.get('offices', []):
            if 'Consultant' in office.get('roles', {}):
                consultant_roles = office['roles']['Consultant']
                for level_name, level_data in consultant_roles.items():
                    if level_name in ['M', 'SrM', 'PiP']:
                        baseline_senior += level_data.get('fte', 0)
        
        baseline_non_debit_ratio = (baseline_senior / baseline_consultants * 100) if baseline_consultants > 0 else 0.0
        
        return GrowthKPIs(
            total_growth_percent=total_growth_rate,
            total_growth_absolute=current_total_fte - baseline_total_fte,
            current_total_fte=current_total_fte,
            baseline_total_fte=baseline_total_fte,
            non_debit_ratio=current_non_debit_ratio,
            non_debit_ratio_baseline=baseline_non_debit_ratio,
            non_debit_delta=current_non_debit_ratio - baseline_non_debit_ratio
        )
    
    def _calculate_journey_metrics(self, final_year_data: Dict[str, Any]) -> JourneyKPIs:
        """Calculate journey distribution metrics"""
        
        # Get baseline data for comparison
        baseline_data = self._get_baseline_data()
        
        # Calculate baseline journey totals
        baseline_journey_totals = {
            "Journey 1": 0,  # A, AC, C
            "Journey 2": 0,  # SrC, AM
            "Journey 3": 0,  # M, SrM
            "Journey 4": 0   # PiP
        }
        
        # Journey level mappings
        journey_mappings = {
            "Journey 1": ["A", "AC", "C"],
            "Journey 2": ["SrC", "AM"],
            "Journey 3": ["M", "SrM"],
            "Journey 4": ["PiP"]
        }
        
        # Calculate baseline journey totals from baseline data
        for office in baseline_data.get('offices', []):
            office_roles = office.get('roles', {})
            for role_name, role_data in office_roles.items():
                if role_name in ['Consultant', 'Sales', 'Recruitment']:
                    for level_name, level_data in role_data.items():
                        level_fte = level_data.get('fte', 0)
                        # Map level to journey
                        for journey_name, levels in journey_mappings.items():
                            if level_name in levels:
                                baseline_journey_totals[journey_name] += level_fte
        
        print(f"[KPI DEBUG] BASELINE Journey totals: {baseline_journey_totals}")
        
        # Calculate current journey totals by aggregating from all levels across all offices
        current_journey_totals = {
            "Journey 1": 0,
            "Journey 2": 0,
            "Journey 3": 0,
            "Journey 4": 0
        }
        
        # Aggregate journey totals from all office levels
        for office_name, office_data in final_year_data.get('offices', {}).items():
            office_levels = office_data.get('levels', {})
            
            # Process all roles that have levels
            for role_name, role_data in office_levels.items():
                if role_name in ['Consultant', 'Sales', 'Recruitment']:
                    for level_name, level_results in role_data.items():
                        if level_results:  # Check if there are results for this level
                            # Get the latest month's data
                            if isinstance(level_results, list) and len(level_results) > 0:
                                latest_data = level_results[-1]
                                fte_count = latest_data.get('total', 0) if isinstance(latest_data, dict) else 0
                                
                                # Map level to journey and add to totals
                                for journey_name, levels in journey_mappings.items():
                                    if level_name in levels:
                                        current_journey_totals[journey_name] += fte_count
                                        print(f"[KPI DEBUG] {office_name} {role_name} {level_name}: {fte_count} FTE → {journey_name}")
        
        print(f"[KPI DEBUG] CURRENT Journey totals: {current_journey_totals}")
        
        total_current_fte = sum(current_journey_totals.values())
        total_baseline_fte = sum(baseline_journey_totals.values())
        
        # Calculate percentages
        current_percentages = {}
        baseline_percentages = {}
        journey_deltas = {}
        
        for journey_name in current_journey_totals.keys():
            current_total = current_journey_totals[journey_name]
            baseline_total = baseline_journey_totals[journey_name]
            
            current_pct = (current_total / total_current_fte * 100) if total_current_fte > 0 else 0.0
            baseline_pct = (baseline_total / total_baseline_fte * 100) if total_baseline_fte > 0 else 0.0
            
            current_percentages[journey_name] = current_pct
            baseline_percentages[journey_name] = baseline_pct
            journey_deltas[journey_name] = current_total - baseline_total
        
        print(f"[KPI DEBUG] Journey percentages - Current: {current_percentages}, Baseline: {baseline_percentages}")
        print(f"[KPI DEBUG] Journey deltas: {journey_deltas}")
        
        return JourneyKPIs(
            journey_totals=current_journey_totals,
            journey_percentages=current_percentages,
            journey_deltas=journey_deltas,
            journey_totals_baseline=baseline_journey_totals,
            journey_percentages_baseline=baseline_percentages
        )
    
    def calculate_kpis_for_year(
        self, 
        simulation_results: Dict[str, Any], 
        target_year: str,
        simulation_duration_months: int,
        unplanned_absence: float = 0.05,
        other_expense: float = None
    ) -> AllKPIs:
        """
        Calculate KPIs for a specific year only (not aggregated across all years).
        This enables year-by-year comparison in the frontend.
        """
        if other_expense is None:
            other_expense = self.default_other_expense
        
        try:
            # Get baseline data from hardcoded config (avoid circular dependency)
            baseline_data = self._get_baseline_data()
            
            # Calculate baseline financial metrics (always 12 months for comparison)
            baseline_financial = self._calculate_baseline_financial_metrics(
                baseline_data, 
                unplanned_absence, 
                other_expense,
                duration_months=12  # Always use 12 months for baseline
            )
            
            # Extract target year data
            if target_year not in simulation_results.get('years', {}):
                raise ValueError(f"Year {target_year} not found in simulation results")
            
            target_year_data = simulation_results['years'][target_year]
            
            # Calculate current year financial metrics (12 months for annual comparison)
            current_financial = self._calculate_current_financial_metrics(
                target_year_data,
                unplanned_absence,
                other_expense,
                duration_months=12  # Always use 12 months for annual comparison
            )
            
            # Calculate growth metrics
            growth_metrics = self._calculate_growth_metrics(
                baseline_data,
                target_year_data
            )
            
            # Calculate journey distribution
            journey_metrics = self._calculate_journey_metrics(target_year_data)
            
            # Create financial KPIs
            financial_kpis = FinancialKPIs(
                net_sales=current_financial['total_revenue'],
                net_sales_baseline=baseline_financial['total_revenue'],
                total_salary_costs=current_financial['total_salary_costs'],
                total_salary_costs_baseline=baseline_financial['total_salary_costs'],
                ebitda=current_financial['ebitda'],
                ebitda_baseline=baseline_financial['ebitda'],
                margin=current_financial['margin'],
                margin_baseline=baseline_financial['margin'],
                total_consultants=current_financial.get('total_consultants', 0),
                total_consultants_baseline=baseline_financial.get('total_consultants', 0),
                avg_hourly_rate=current_financial['avg_hourly_rate'],
                avg_hourly_rate_baseline=baseline_financial['avg_hourly_rate'],
                avg_utr=0.85
            )
            
            print(f"[KPI DEBUG] =================== YEAR {target_year} FINANCIAL CALCULATION ===================")
            print(f"[KPI DEBUG] Total Revenue: {current_financial['total_revenue']:,.0f} SEK")
            print(f"[KPI DEBUG] Total Salary Costs: {current_financial['total_salary_costs']:,.0f} SEK")
            print(f"[KPI DEBUG] Total Costs: {current_financial['total_costs']:,.0f} SEK")
            print(f"[KPI DEBUG] EBITDA: {current_financial['ebitda']:,.0f} SEK")
            print(f"[KPI DEBUG] Margin: {current_financial['margin']:.2%}")
            print(f"[KPI DEBUG] Avg Hourly Rate: {current_financial['avg_hourly_rate']:.2f} SEK")
            print(f"[KPI DEBUG] ================================================================")
            
            return AllKPIs(
                financial=financial_kpis,
                growth=growth_metrics,
                journeys=journey_metrics,
                yearly_kpis={}  # Not needed for single year calculation
            )
            
        except Exception as e:
            import traceback
            print(f"[KPI ERROR] Exception in calculate_kpis_for_year: {e}")
            print(f"[KPI ERROR] Traceback: {traceback.format_exc()}")
            raise e 