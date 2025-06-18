from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from backend.config.default_config import ACTUAL_OFFICE_LEVEL_DATA, JOURNEY_CLASSIFICATION, BASE_PRICING, BASE_SALARIES

@dataclass
class FinancialKPIs:
    """Financial KPI results"""
    net_sales: float
    net_sales_baseline: float
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
    yearly_kpis: Dict[str, YearlyKPIs]  # Added yearly KPIs

class KPIService:
    """Service for calculating all simulation KPIs"""
    
    def __init__(self):
        self.working_hours_per_month = 166.4  # Standard working hours per month
        self.total_employment_cost_rate = 0.40  # 40% total employment costs (includes social security, pensions, health insurance, vacation accruals, etc.)
    
    def calculate_all_kpis(
        self, 
        simulation_results: Dict[str, Any], 
        simulation_duration_months: int,
        unplanned_absence: float,
        other_expense: float
    ) -> AllKPIs:
        """Calculate all KPIs from simulation results"""
        
        # Get baseline data from config
        baseline_data = self._get_baseline_data()
        
        # Calculate overall KPIs
        financial_kpis = self._calculate_financial_kpis(
            simulation_results, 
            baseline_data,
            simulation_duration_months,
            unplanned_absence,
            other_expense
        )
        
        growth_kpis = self._calculate_growth_kpis(
            simulation_results,
            baseline_data
        )
        
        journey_kpis = self._calculate_journey_kpis(
            simulation_results,
            baseline_data
        )
        
        # Calculate year-specific KPIs
        yearly_kpis = self._calculate_yearly_kpis(
            simulation_results,
            baseline_data,
            unplanned_absence,
            other_expense
        )
        
        return AllKPIs(
            financial=financial_kpis,
            growth=growth_kpis,
            journeys=journey_kpis,
            yearly_kpis=yearly_kpis
        )
    
    def _calculate_yearly_kpis(
        self,
        simulation_results: Dict[str, Any],
        baseline_data: Dict[str, Any],
        unplanned_absence: float,
        other_expense: float
    ) -> Dict[str, YearlyKPIs]:
        """Calculate KPIs for each year in the simulation"""
        yearly_kpis = {}
        
        # Sort years to ensure chronological order
        years = sorted(simulation_results['years'].keys())
        
        for year in years:
            year_data = simulation_results['years'][year]
            
            # Calculate year-specific financial KPIs
            financial_kpis = self._calculate_financial_kpis_for_year(
                year_data,
                baseline_data,
                unplanned_absence,
                other_expense
            )
            
            # Calculate year-specific growth KPIs
            growth_kpis = self._calculate_growth_kpis_for_year(
                year_data,
                baseline_data
            )
            
            # Calculate year-specific journey KPIs
            journey_kpis = self._calculate_journey_kpis_for_year(
                year_data,
                baseline_data
            )
            
            # Calculate year-over-year changes
            year_over_year_growth = 0.0
            year_over_year_margin_change = 0.0
            
            if year != years[0]:  # Not the first year
                prev_year = str(int(year) - 1)
                if prev_year in yearly_kpis:
                    prev_year_data = yearly_kpis[prev_year]
                    
                    # Calculate year-over-year growth
                    year_over_year_growth = (
                        (growth_kpis.current_total_fte - prev_year_data.growth.current_total_fte) /
                        prev_year_data.growth.current_total_fte * 100
                    )
                    
                    # Calculate year-over-year margin change
                    year_over_year_margin_change = (
                        financial_kpis.margin - prev_year_data.financial.margin
                    )
            
            yearly_kpis[year] = YearlyKPIs(
                year=year,
                financial=financial_kpis,
                growth=growth_kpis,
                journeys=journey_kpis,
                year_over_year_growth=year_over_year_growth,
                year_over_year_margin_change=year_over_year_margin_change
            )
        
        return yearly_kpis
    
    def _calculate_financial_kpis_for_year(
        self,
        year_data: Dict[str, Any],
        baseline_data: Dict[str, Any],
        unplanned_absence: float,
        other_expense: float
    ) -> FinancialKPIs:
        """Calculate financial KPIs for a specific year"""
        
        # Calculate current year metrics
        current_metrics = self._calculate_financial_metrics_for_year(
            year_data,
            unplanned_absence,
            other_expense
        )
        
        # Calculate baseline metrics (annualized)
        baseline_metrics = self._calculate_baseline_financial_metrics(
            baseline_data,
            unplanned_absence,
            other_expense,
            12  # Annualized baseline
        )
        
        return FinancialKPIs(
            net_sales=current_metrics['net_sales'],
            net_sales_baseline=baseline_metrics['net_sales'],
            ebitda=current_metrics['ebitda'],
            ebitda_baseline=baseline_metrics['ebitda'],
            margin=current_metrics['margin'],
            margin_baseline=baseline_metrics['margin'],
            total_consultants=current_metrics['total_consultants'],
            total_consultants_baseline=baseline_metrics['total_consultants'],
            avg_hourly_rate=current_metrics['avg_hourly_rate'],
            avg_hourly_rate_baseline=baseline_metrics['avg_hourly_rate'],
            avg_utr=current_metrics['avg_utr']
        )
    
    def _calculate_financial_metrics_for_year(
        self,
        year_data: Dict[str, Any],
        unplanned_absence: float,
        other_expense: float
    ) -> Dict[str, float]:
        """Calculate financial metrics for a specific year"""
        
        total_revenue = 0.0
        total_costs = 0.0
        total_consultants = 0
        total_weighted_price = 0.0
        total_weighted_utr = 0.0
        
        for office_name, office_data in year_data['offices'].items():
            # Only consultants generate revenue
            if 'Consultant' in office_data['levels']:
                consultant_levels = office_data['levels']['Consultant']
                
                for level_name, level_data in consultant_levels.items():
                    # Debug: Check the data type
                    print(f"[DEBUG] Office: {office_name}, Level: {level_name}, Type: {type(level_data)}, Data: {level_data}")
                    
                    # Handle both list and dict structures
                    if isinstance(level_data, list) and len(level_data) > 0:
                        # Use the last month's data for the year
                        last_month_data = level_data[-1]
                        print(f"[DEBUG] Using last month data from list: {last_month_data}")
                    elif isinstance(level_data, dict):
                        # Direct dict access
                        last_month_data = level_data
                        print(f"[DEBUG] Using direct dict data: {last_month_data}")
                    elif isinstance(level_data, int):
                        # Fallback for integer values - create basic structure
                        print(f"[WARNING] Level data is integer, creating fallback structure for {office_name} {level_name}")
                        last_month_data = {
                            'total': level_data,
                            'price': 1000.0,  # Default price
                            'salary': 50000.0  # Default salary
                        }
                        print(f"[DEBUG] Created fallback data: {last_month_data}")
                    else:
                        print(f"[ERROR] Unexpected level_data type: {type(level_data)}")
                        continue
                    
                    # Extract values with detailed logging
                    fte_count = last_month_data['total']
                    hourly_price = last_month_data['price']
                    monthly_salary = last_month_data['salary']
                    
                    print(f"[DEBUG] {office_name} {level_name} - FTE: {fte_count}, Price: {hourly_price} SEK/hr, Salary: {monthly_salary} SEK/month")
                    
                    total_consultants += fte_count
                    total_weighted_price += fte_count * hourly_price
                    total_weighted_utr += fte_count * 0.85  # Assuming 85% UTR
                    
                    # Calculate revenue with detailed logging
                    working_hours = self.working_hours_per_month
                    # Convert unplanned_absence from hours to billable hours per month
                    available_hours = working_hours - unplanned_absence  # Subtract absence hours
                    billable_hours = available_hours * 0.85  # Apply UTR to available hours
                    
                    print(f"[DEBUG] REVENUE CALC {office_name} {level_name}:")
                    print(f"  FTE: {fte_count}")
                    print(f"  Price: {hourly_price} SEK/hr")
                    print(f"  Total working hours/month: {working_hours}")
                    print(f"  Unplanned absence hours: {unplanned_absence}")
                    print(f"  Available hours: {available_hours}")
                    print(f"  Billable hours (85% UTR): {billable_hours}")
                    print(f"  Formula: {fte_count} * ({hourly_price} * {billable_hours}) * 12")
                    
                    revenue = (
                        fte_count *
                        hourly_price *
                        billable_hours *
                        12  # Annualize
                    )
                    
                    print(f"  Result: {revenue:,.0f} SEK")
                    
                    # Calculate costs with detailed logging
                    costs = (
                        fte_count *
                        monthly_salary *
                        (1 + self.total_employment_cost_rate) *
                        12  # Annualize
                    )
                    
                    profit = revenue - costs
                    
                    print(f"[DEBUG] {office_name} {level_name} - Revenue: {revenue:,.0f} SEK, Costs: {costs:,.0f} SEK, Profit: {profit:,.0f} SEK")
                    
                    total_revenue += revenue
                    total_costs += costs
            
            # Add other expenses
            other_expense_annual = other_expense * 12  # Annualize
            total_costs += other_expense_annual
            print(f"[DEBUG] Added other expenses: {other_expense_annual:,.0f} SEK annually")
        
        print(f"[DEBUG] FINAL TOTALS:")
        print(f"[DEBUG] Total Consultants: {total_consultants}")
        print(f"[DEBUG] Total Revenue: {total_revenue:,.0f} SEK")
        print(f"[DEBUG] Total Costs: {total_costs:,.0f} SEK")
        
        # Calculate averages
        avg_hourly_rate = total_weighted_price / total_consultants if total_consultants > 0 else 0.0
        avg_utr = total_weighted_utr / total_consultants if total_consultants > 0 else 0.0
        
        # Calculate EBITDA and margin
        ebitda = total_revenue - total_costs
        margin = (ebitda / total_revenue * 100) if total_revenue > 0 else 0.0
        
        print(f"[DEBUG] EBITDA: {ebitda:,.0f} SEK")
        print(f"[DEBUG] Margin: {margin:.2f}%")
        print(f"[DEBUG] Avg Hourly Rate: {avg_hourly_rate:.2f} SEK")
        print(f"[DEBUG] Avg UTR: {avg_utr:.2f}")
        
        return {
            'net_sales': total_revenue,
            'ebitda': ebitda,
            'margin': margin,
            'total_consultants': total_consultants,
            'avg_hourly_rate': avg_hourly_rate,
            'avg_utr': avg_utr
        }
    
    def _calculate_growth_kpis_for_year(
        self,
        year_data: Dict[str, Any],
        baseline_data: Dict[str, Any]
    ) -> GrowthKPIs:
        """Calculate growth KPIs for a specific year"""
        
        current_total = year_data['summary']['total_fte']
        baseline_total = baseline_data['total_fte']
        
        # Calculate growth metrics
        total_growth_absolute = current_total - baseline_total
        total_growth_percent = (total_growth_absolute / baseline_total * 100) if baseline_total > 0 else 0.0
        
        # Calculate non-debit ratio
        non_debit_ratio = self._calculate_non_debit_ratio_for_year(year_data)
        non_debit_ratio_baseline = self._calculate_baseline_non_debit_ratio(baseline_data)
        non_debit_delta = non_debit_ratio - non_debit_ratio_baseline
        
        return GrowthKPIs(
            total_growth_percent=total_growth_percent,
            total_growth_absolute=total_growth_absolute,
            current_total_fte=current_total,
            baseline_total_fte=baseline_total,
            non_debit_ratio=non_debit_ratio,
            non_debit_ratio_baseline=non_debit_ratio_baseline,
            non_debit_delta=non_debit_delta
        )
    
    def _calculate_journey_kpis_for_year(
        self,
        year_data: Dict[str, Any],
        baseline_data: Dict[str, Any]
    ) -> JourneyKPIs:
        """Calculate journey KPIs for a specific year"""
        
        journey_totals = {}
        journey_percentages = {}
        journey_deltas = {}
        
        total_fte = year_data['summary']['total_fte']
        
        # Calculate journey totals and percentages
        for journey in ['Journey 1', 'Journey 2', 'Journey 3', 'Journey 4']:
            journey_total = 0
            
            # Check if journeys data exists in the expected format
            for office_data in year_data['offices'].values():
                if 'journeys' in office_data and journey in office_data['journeys']:
                    journey_data = office_data['journeys'][journey]
                    if isinstance(journey_data, list) and len(journey_data) > 0:
                        # Use the last entry if it's a list
                        last_entry = journey_data[-1]
                        if isinstance(last_entry, dict):
                            journey_total += last_entry.get('total', 0)
                        elif isinstance(last_entry, int):
                            journey_total += last_entry
                    elif isinstance(journey_data, dict):
                        # Use total directly if it's a dict
                        journey_total += journey_data.get('total', 0)
                    elif isinstance(journey_data, int):
                        # Use value directly if it's an int
                        journey_total += journey_data
            
            journey_totals[journey] = journey_total
            journey_percentages[journey] = (journey_total / total_fte * 100) if total_fte > 0 else 0.0
            
            # Calculate deltas from baseline
            baseline_total = self._get_baseline_journey_total(baseline_data, journey)
            journey_deltas[journey] = journey_total - baseline_total
        
        return JourneyKPIs(
            journey_totals=journey_totals,
            journey_percentages=journey_percentages,
            journey_deltas=journey_deltas
        )
    
    def _calculate_non_debit_ratio_for_year(self, year_data: Dict[str, Any]) -> float:
        """Calculate non-debit ratio for a specific year (non-consultants / total FTE)"""
        total_fte = year_data['summary']['total_fte']
        
        # Non-debit includes Sales, Recruitment, and Operations (all non-consultants)
        non_debit_fte = 0
        for office_data in year_data['offices'].values():
            # Add Sales
            if 'Sales' in office_data['levels']:
                for level_name, level_data in office_data['levels']['Sales'].items():
                    # Handle both list and dict/int structures
                    if isinstance(level_data, list) and len(level_data) > 0:
                        last_month_data = level_data[-1]
                        if isinstance(last_month_data, dict):
                            non_debit_fte += last_month_data.get('total', 0)
                        else:
                            non_debit_fte += last_month_data
                    elif isinstance(level_data, dict):
                        non_debit_fte += level_data.get('total', 0)
                    elif isinstance(level_data, int):
                        non_debit_fte += level_data
            
            # Add Recruitment
            if 'Recruitment' in office_data['levels']:
                for level_name, level_data in office_data['levels']['Recruitment'].items():
                    # Handle both list and dict/int structures
                    if isinstance(level_data, list) and len(level_data) > 0:
                        last_month_data = level_data[-1]
                        if isinstance(last_month_data, dict):
                            non_debit_fte += last_month_data.get('total', 0)
                        else:
                            non_debit_fte += last_month_data
                    elif isinstance(level_data, dict):
                        non_debit_fte += level_data.get('total', 0)
                    elif isinstance(level_data, int):
                        non_debit_fte += level_data
            
            # Add Operations
            if 'Operations' in office_data['levels']:
                operations_data = office_data['levels']['Operations']
                # Handle both list and dict/int structures
                if isinstance(operations_data, list) and len(operations_data) > 0:
                    last_month_data = operations_data[-1]
                    if isinstance(last_month_data, dict):
                        non_debit_fte += last_month_data.get('total', 0)
                    else:
                        non_debit_fte += last_month_data
                elif isinstance(operations_data, dict):
                    non_debit_fte += operations_data.get('total', 0)
                elif isinstance(operations_data, int):
                    non_debit_fte += operations_data
        
        return (non_debit_fte / total_fte * 100) if total_fte > 0 else 0.0
    
    def _get_baseline_journey_total(self, baseline_data: Dict[str, Any], journey: str) -> int:
        """Get baseline total for a specific journey"""
        total = 0
        
        # Get the correct level mapping from JOURNEY_CLASSIFICATION
        journey_levels = JOURNEY_CLASSIFICATION.get(journey, [])
        
        for office in baseline_data['offices']:
            # All journeys come from Consultant roles only
            if 'Consultant' in office['roles']:
                consultant_levels = office['roles']['Consultant']
                for level_name, count in consultant_levels.items():
                    if level_name in journey_levels:
                        total += count
        
        return total
    
    def _get_baseline_data(self) -> Dict[str, Any]:
        """Get baseline data from original config"""
        baseline = {
            'offices': [],
            'total_consultants': 0,
            'total_non_consultants': 0,
            'total_fte': 0
        }
        
        for office_name, office_data in ACTUAL_OFFICE_LEVEL_DATA.items():
            office_baseline = {
                'name': office_name,
                'roles': office_data,
                'consultants': 0,
                'non_consultants': 0,
                'total': 0
            }
            
            # Count consultants
            if 'Consultant' in office_data:
                for level, count in office_data['Consultant'].items():
                    office_baseline['consultants'] += count
                    office_baseline['total'] += count
            
            # Count non-consultants (Sales + Recruitment + Operations)
            for role_name in ['Sales', 'Recruitment']:
                if role_name in office_data:
                    for level, count in office_data[role_name].items():
                        office_baseline['non_consultants'] += count
                        office_baseline['total'] += count
            
            # Operations (single number)
            if 'Operations' in office_data:
                office_baseline['non_consultants'] += office_data['Operations']
                office_baseline['total'] += office_data['Operations']
            
            baseline['offices'].append(office_baseline)
            baseline['total_consultants'] += office_baseline['consultants']
            baseline['total_non_consultants'] += office_baseline['non_consultants']
            baseline['total_fte'] += office_baseline['total']
        
        return baseline
    
    def _calculate_financial_kpis(
        self, 
        simulation_results: Dict[str, Any], 
        baseline_data: Dict[str, Any],
        simulation_duration_months: int,
        unplanned_absence: float,
        other_expense: float
    ) -> FinancialKPIs:
        """Calculate financial KPIs from simulation results"""
        
        # Get the last year's data for overall metrics
        years = sorted(simulation_results['years'].keys())
        last_year = years[-1]
        last_year_data = simulation_results['years'][last_year]
        
        # Calculate current metrics using the last year's data
        current_metrics = self._calculate_financial_metrics_for_year(
            last_year_data,
            unplanned_absence,
            other_expense
        )
        
        # Calculate baseline metrics (annualized)
        baseline_metrics = self._calculate_baseline_financial_metrics(
            baseline_data,
            unplanned_absence,
            other_expense,
            12  # Annualized baseline
        )
        
        return FinancialKPIs(
            net_sales=current_metrics['net_sales'],
            net_sales_baseline=baseline_metrics['net_sales'],
            ebitda=current_metrics['ebitda'],
            ebitda_baseline=baseline_metrics['ebitda'],
            margin=current_metrics['margin'],
            margin_baseline=baseline_metrics['margin'],
            total_consultants=current_metrics['total_consultants'],
            total_consultants_baseline=baseline_metrics['total_consultants'],
            avg_hourly_rate=current_metrics['avg_hourly_rate'],
            avg_hourly_rate_baseline=baseline_metrics['avg_hourly_rate'],
            avg_utr=current_metrics['avg_utr']
        )
    
    def _calculate_growth_kpis(
        self, 
        simulation_results: Dict[str, Any], 
        baseline_data: Dict[str, Any]
    ) -> GrowthKPIs:
        """Calculate growth KPIs from simulation results"""
        
        # Get the first and last year's data
        years = sorted(simulation_results['years'].keys())
        first_year = years[0]
        last_year = years[-1]
        
        first_year_data = simulation_results['years'][first_year]
        last_year_data = simulation_results['years'][last_year]
        
        # Calculate current total from last year
        current_total = last_year_data['summary']['total_fte']
        baseline_total = baseline_data['total_fte']
        
        # Calculate growth metrics
        total_growth_absolute = current_total - baseline_total
        total_growth_percent = (total_growth_absolute / baseline_total * 100) if baseline_total > 0 else 0.0
        
        # Calculate non-debit ratio from last year
        non_debit_ratio = self._calculate_non_debit_ratio_for_year(last_year_data)
        non_debit_ratio_baseline = self._calculate_baseline_non_debit_ratio(baseline_data)
        non_debit_delta = non_debit_ratio - non_debit_ratio_baseline
        
        return GrowthKPIs(
            total_growth_percent=total_growth_percent,
            total_growth_absolute=total_growth_absolute,
            current_total_fte=current_total,
            baseline_total_fte=baseline_total,
            non_debit_ratio=non_debit_ratio,
            non_debit_ratio_baseline=non_debit_ratio_baseline,
            non_debit_delta=non_debit_delta
        )
    
    def _calculate_journey_kpis(
        self, 
        simulation_results: Dict[str, Any], 
        baseline_data: Dict[str, Any]
    ) -> JourneyKPIs:
        """Calculate journey KPIs from simulation results"""
        
        # Get the last year's data
        years = sorted(simulation_results['years'].keys())
        last_year = years[-1]
        last_year_data = simulation_results['years'][last_year]
        
        journey_totals = {}
        journey_percentages = {}
        journey_deltas = {}
        
        total_fte = last_year_data['summary']['total_fte']
        
        # Calculate journey totals and percentages
        for journey in ['Journey 1', 'Journey 2', 'Journey 3', 'Journey 4']:
            journey_total = 0
            
            # Check if journeys data exists in the expected format
            for office_data in last_year_data['offices'].values():
                if 'journeys' in office_data and journey in office_data['journeys']:
                    journey_data = office_data['journeys'][journey]
                    if isinstance(journey_data, list) and len(journey_data) > 0:
                        # Use the last entry if it's a list
                        last_entry = journey_data[-1]
                        if isinstance(last_entry, dict):
                            journey_total += last_entry.get('total', 0)
                        elif isinstance(last_entry, int):
                            journey_total += last_entry
                    elif isinstance(journey_data, dict):
                        # Use total directly if it's a dict
                        journey_total += journey_data.get('total', 0)
                    elif isinstance(journey_data, int):
                        # Use value directly if it's an int
                        journey_total += journey_data
            
            journey_totals[journey] = journey_total
            journey_percentages[journey] = (journey_total / total_fte * 100) if total_fte > 0 else 0.0
            
            # Calculate deltas from baseline
            baseline_total = self._get_baseline_journey_total(baseline_data, journey)
            journey_deltas[journey] = journey_total - baseline_total
        
        return JourneyKPIs(
            journey_totals=journey_totals,
            journey_percentages=journey_percentages,
            journey_deltas=journey_deltas
        )
    
    def _calculate_baseline_financial_metrics(
        self, 
        baseline_data: Dict[str, Any], 
        unplanned_absence: float, 
        other_expense: float,
        duration_months: int = 12  # Default to 12 months for annualization
    ) -> Dict[str, float]:
        """Calculate baseline financial metrics"""
        
        total_revenue = 0.0
        total_costs = 0.0
        total_consultants = 0
        total_weighted_price = 0.0
        total_weighted_utr = 0.0
        
        for office in baseline_data['offices']:
            if 'Consultant' in office['roles']:
                consultant_levels = office['roles']['Consultant']
                
                for level_name, count in consultant_levels.items():
                    # Get price and salary from BASE_PRICING and BASE_SALARIES
                    price = BASE_PRICING[office['name']][level_name]
                    salary = BASE_SALARIES[office['name']][level_name]
                    
                    print(f"[DEBUG] BASELINE {office['name']} {level_name} - FTE: {count}, Price: {price} SEK/hr, Salary: {salary} SEK/month")
                    
                    total_consultants += count
                    total_weighted_price += count * price
                    total_weighted_utr += count * 0.85  # Assuming 85% UTR
                    
                    # Calculate revenue (annualized) with detailed debug
                    working_hours = self.working_hours_per_month
                    # Convert unplanned_absence from hours to billable hours per month
                    available_hours = working_hours - unplanned_absence  # Subtract absence hours
                    billable_hours = available_hours * 0.85  # Apply UTR to available hours
                    
                    print(f"[DEBUG] BASELINE REVENUE CALC {office['name']} {level_name}:")
                    print(f"  FTE: {count}")
                    print(f"  Price: {price} SEK/hr")
                    print(f"  Total working hours/month: {working_hours}")
                    print(f"  Unplanned absence hours: {unplanned_absence}")
                    print(f"  Available hours: {available_hours}")
                    print(f"  Billable hours (85% UTR): {billable_hours}")
                    print(f"  Duration months: {duration_months}")
                    print(f"  Formula: {count} * ({price} * {billable_hours}) * {duration_months}")
                    
                    revenue = (
                        count *
                        price *
                        billable_hours *
                        duration_months  # Annualize by multiplying by 12 months
                    )
                    
                    print(f"  Result: {revenue:,.0f} SEK")
                    total_revenue += revenue
                    
                    # Calculate costs (salary + total employment costs, annualized)
                    costs = (
                        count *
                        salary *
                        (1 + self.total_employment_cost_rate) *
                        duration_months  # Annualize by multiplying by 12 months
                    )
                    total_costs += costs
                    
                    profit = revenue - costs
                    print(f"[DEBUG] BASELINE {office['name']} {level_name} - Revenue: {revenue:,.0f} SEK, Costs: {costs:,.0f} SEK, Profit: {profit:,.0f} SEK")
            
            # Add other expenses (annualized)
            other_expense_total = other_expense * duration_months  # Annualize by multiplying by 12 months
            total_costs += other_expense_total
            print(f"[DEBUG] BASELINE Added other expenses: {other_expense_total:,.0f} SEK")
        
        print(f"[DEBUG] BASELINE FINAL TOTALS:")
        print(f"[DEBUG] BASELINE Total Consultants: {total_consultants}")
        print(f"[DEBUG] BASELINE Total Revenue: {total_revenue:,.0f} SEK")
        print(f"[DEBUG] BASELINE Total Costs: {total_costs:,.0f} SEK")
        
        # Calculate averages
        avg_hourly_rate = total_weighted_price / total_consultants if total_consultants > 0 else 0.0
        avg_utr = total_weighted_utr / total_consultants if total_consultants > 0 else 0.0
        
        # Calculate EBITDA and margin
        ebitda = total_revenue - total_costs
        margin = (ebitda / total_revenue * 100) if total_revenue > 0 else 0.0
        
        print(f"[DEBUG] BASELINE EBITDA: {ebitda:,.0f} SEK")
        print(f"[DEBUG] BASELINE Margin: {margin:.2f}%")
        
        return {
            'net_sales': total_revenue,
            'ebitda': ebitda,
            'margin': margin,
            'total_consultants': total_consultants,
            'avg_hourly_rate': avg_hourly_rate,
            'avg_utr': avg_utr
        }
    
    def _calculate_baseline_non_debit_ratio(self, baseline_data: Dict[str, Any]) -> float:
        """Calculate baseline non-debit ratio (non-consultants / total FTE)"""
        total_fte = baseline_data['total_fte']
        
        # Non-debit includes Sales, Recruitment, and Operations (all non-consultants)
        non_debit_fte = 0
        for office in baseline_data['offices']:
            # Add Sales
            if 'Sales' in office['roles']:
                for level, count in office['roles']['Sales'].items():
                    non_debit_fte += count
            
            # Add Recruitment  
            if 'Recruitment' in office['roles']:
                for level, count in office['roles']['Recruitment'].items():
                    non_debit_fte += count
            
            # Add Operations
            non_debit_fte += office['roles'].get('Operations', 0)
        
        return (non_debit_fte / total_fte * 100) if total_fte > 0 else 0.0 