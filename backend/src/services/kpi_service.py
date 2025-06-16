from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from backend.config.default_config import ACTUAL_OFFICE_LEVEL_DATA

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
class AllKPIs:
    """Combined KPI results"""
    financial: FinancialKPIs
    growth: GrowthKPIs
    journeys: JourneyKPIs

class KPIService:
    """Service for calculating all simulation KPIs"""
    
    def __init__(self):
        self.working_hours_per_month = 166.4  # Standard working hours per month
        self.social_cost_rate = 0.25  # 25% social costs
    
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
        
        # Calculate financial KPIs
        financial_kpis = self._calculate_financial_kpis(
            simulation_results, 
            baseline_data,
            simulation_duration_months,
            unplanned_absence,
            other_expense
        )
        
        # Calculate growth KPIs
        growth_kpis = self._calculate_growth_kpis(
            simulation_results,
            baseline_data
        )
        
        # Calculate journey KPIs
        journey_kpis = self._calculate_journey_kpis(
            simulation_results,
            baseline_data
        )
        
        return AllKPIs(
            financial=financial_kpis,
            growth=growth_kpis,
            journeys=journey_kpis
        )
    
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
        """Calculate financial KPIs"""
        
        # Current simulation financial metrics
        current_metrics = self._calculate_financial_metrics(
            simulation_results['offices'], 
            simulation_duration_months, 
            unplanned_absence, 
            other_expense,
            is_baseline=False
        )
        
        # Baseline financial metrics (annualized for comparison)
        baseline_metrics = self._calculate_baseline_financial_metrics(
            baseline_data, 
            unplanned_absence, 
            other_expense,
            12  # Annualized baseline (12 months) for proper comparison
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
    
    def _calculate_financial_metrics(
        self, 
        offices_data: Dict[str, Any], 
        duration_months: int, 
        unplanned_absence: float, 
        other_expense: float,
        is_baseline: bool = False
    ) -> Dict[str, float]:
        """Calculate financial metrics for simulation data"""
        
        total_revenue = 0.0
        total_costs = 0.0
        total_consultants = 0
        total_weighted_price = 0.0
        total_weighted_utr = 0.0
        
        # Get the last period index
        periods = list(offices_data.values())[0]['levels']['Consultant']['A'] if offices_data else []
        last_idx = len(periods) - 1 if periods else 0
        
        for office_name, office_data in offices_data.items():
            # Only consultants generate revenue
            if 'Consultant' in office_data['levels']:
                consultant_levels = office_data['levels']['Consultant']
                
                for level_name, level_data in consultant_levels.items():
                    if level_data and last_idx < len(level_data):
                        level_info = level_data[last_idx]
                        fte_count = level_info['total']
                        hourly_rate = level_info['price']
                        
                        # Calculate revenue (assuming 85% UTR for now)
                        utr = 0.85
                        monthly_revenue = fte_count * hourly_rate * self.working_hours_per_month * utr * (1 - unplanned_absence)
                        total_revenue += monthly_revenue * duration_months
                        
                        # Track consultant metrics
                        total_consultants += fte_count
                        total_weighted_price += fte_count * hourly_rate
                        total_weighted_utr += fte_count * utr
            
            # All roles contribute to costs
            for role_name, role_levels in office_data['levels'].items():
                if isinstance(role_levels, dict):  # Roles with levels
                    for level_name, level_data in role_levels.items():
                        if level_data and last_idx < len(level_data):
                            level_info = level_data[last_idx]
                            fte_count = level_info['total']
                            monthly_salary = level_info['salary']
                            
                            # Calculate total cost including social costs
                            monthly_cost = fte_count * monthly_salary * (1 + self.social_cost_rate)
                            total_costs += monthly_cost * duration_months
            
            # Operations costs
            if 'operations' in office_data and office_data['operations']:
                ops_data = office_data['operations']
                if last_idx < len(ops_data) and ops_data[last_idx]:
                    ops_info = ops_data[last_idx]
                    fte_count = ops_info['total']
                    monthly_salary = ops_info['salary']
                    
                    monthly_cost = fte_count * monthly_salary * (1 + self.social_cost_rate)
                    total_costs += monthly_cost * duration_months
        
        # Add other expenses
        total_costs += other_expense * duration_months
        
        # Calculate derived metrics
        ebitda = total_revenue - total_costs
        margin = (ebitda / total_revenue * 100) if total_revenue > 0 else 0.0
        avg_hourly_rate = (total_weighted_price / total_consultants) if total_consultants > 0 else 0.0
        avg_utr = (total_weighted_utr / total_consultants) if total_consultants > 0 else 0.0
        
        return {
            'net_sales': total_revenue,
            'ebitda': ebitda,
            'margin': margin,
            'total_consultants': total_consultants,
            'avg_hourly_rate': avg_hourly_rate,
            'avg_utr': avg_utr
        }
    
    def _calculate_baseline_financial_metrics(
        self, 
        baseline_data: Dict[str, Any], 
        unplanned_absence: float, 
        other_expense: float,
        duration_months: int = 1
    ) -> Dict[str, float]:
        """Calculate financial metrics for baseline data"""
        
        # Import pricing data
        from backend.config.default_config import BASE_PRICING, BASE_SALARIES
        
        total_revenue = 0.0
        total_costs = 0.0
        total_consultants = 0
        total_weighted_price = 0.0
        total_weighted_utr = 0.0
        
        for office_baseline in baseline_data['offices']:
            office_name = office_baseline['name']
            office_roles = office_baseline['roles']
            
            # Get pricing for this office
            office_pricing = BASE_PRICING.get(office_name, BASE_PRICING['Stockholm'])
            office_salaries = BASE_SALARIES.get(office_name, BASE_SALARIES['Stockholm'])
            
            # Only consultants generate revenue
            if 'Consultant' in office_roles:
                consultant_levels = office_roles['Consultant']
                
                for level_name, fte_count in consultant_levels.items():
                    hourly_rate = office_pricing.get(level_name, 0.0)
                    
                    # Calculate revenue (assuming 85% UTR)
                    utr = 0.85
                    monthly_revenue = fte_count * hourly_rate * self.working_hours_per_month * utr * (1 - unplanned_absence)
                    total_revenue += monthly_revenue * duration_months  # Scale to simulation duration
                    
                    # Track consultant metrics
                    total_consultants += fte_count
                    total_weighted_price += fte_count * hourly_rate
                    total_weighted_utr += fte_count * utr
            
            # All roles contribute to costs
            for role_name in ['Consultant', 'Sales', 'Recruitment']:
                if role_name in office_roles:
                    role_levels = office_roles[role_name]
                    for level_name, fte_count in role_levels.items():
                        monthly_salary = office_salaries.get(level_name, 0.0)
                        monthly_cost = fte_count * monthly_salary * (1 + self.social_cost_rate)
                        total_costs += monthly_cost * duration_months  # Scale to simulation duration
            
            # Operations costs
            if 'Operations' in office_roles:
                fte_count = office_roles['Operations']
                monthly_salary = office_salaries.get('Operations', 40000.0)
                monthly_cost = fte_count * monthly_salary * (1 + self.social_cost_rate)
                total_costs += monthly_cost * duration_months  # Scale to simulation duration
        
        # Add other expenses (operational costs: rent, equipment, software, etc.)
        # Scale to simulation duration
        total_costs += other_expense * duration_months
        
        # Calculate derived metrics
        ebitda = total_revenue - total_costs
        margin = (ebitda / total_revenue * 100) if total_revenue > 0 else 0.0
        avg_hourly_rate = (total_weighted_price / total_consultants) if total_consultants > 0 else 0.0
        avg_utr = (total_weighted_utr / total_consultants) if total_consultants > 0 else 0.0
        
        return {
            'net_sales': total_revenue,
            'ebitda': ebitda,
            'margin': margin,
            'total_consultants': total_consultants,
            'avg_hourly_rate': avg_hourly_rate,
            'avg_utr': avg_utr
        }
    
    def _calculate_growth_kpis(
        self, 
        simulation_results: Dict[str, Any], 
        baseline_data: Dict[str, Any]
    ) -> GrowthKPIs:
        """Calculate growth and headcount KPIs"""
        
        # Get current totals from simulation
        current_totals = self._get_current_totals(simulation_results['offices'])
        
        # Calculate growth metrics
        baseline_total = baseline_data['total_fte']
        current_total = current_totals['total_fte']
        
        growth_absolute = current_total - baseline_total
        growth_percent = (growth_absolute / baseline_total * 100) if baseline_total > 0 else 0.0
        
        # Calculate non-debit ratios
        current_non_debit_ratio = (current_totals['total_non_consultants'] / current_total * 100) if current_total > 0 else 0.0
        baseline_non_debit_ratio = (baseline_data['total_non_consultants'] / baseline_total * 100) if baseline_total > 0 else 0.0
        non_debit_delta = current_non_debit_ratio - baseline_non_debit_ratio
        
        return GrowthKPIs(
            total_growth_percent=growth_percent,
            total_growth_absolute=growth_absolute,
            current_total_fte=current_total,
            baseline_total_fte=baseline_total,
            non_debit_ratio=current_non_debit_ratio,
            non_debit_ratio_baseline=baseline_non_debit_ratio,
            non_debit_delta=non_debit_delta
        )
    
    def _calculate_journey_kpis(
        self, 
        simulation_results: Dict[str, Any], 
        baseline_data: Dict[str, Any]
    ) -> JourneyKPIs:
        """Calculate career journey distribution KPIs"""
        
        # Get current journey totals
        journey_totals = {"Journey 1": 0, "Journey 2": 0, "Journey 3": 0, "Journey 4": 0}
        
        offices_data = simulation_results['offices']
        if offices_data:
            # Get the last period index
            periods = list(offices_data.values())[0]['journeys']['Journey 1'] if offices_data else []
            last_idx = len(periods) - 1 if periods else 0
            
            for office_name, office_data in offices_data.items():
                if 'journeys' in office_data:
                    for journey_name in journey_totals.keys():
                        journey_data = office_data['journeys'].get(journey_name, [])
                        if journey_data and last_idx < len(journey_data):
                            journey_totals[journey_name] += journey_data[last_idx]['total']
        
        # Calculate percentages
        total_journey_fte = sum(journey_totals.values())
        journey_percentages = {}
        for journey_name, total in journey_totals.items():
            journey_percentages[journey_name] = (total / total_journey_fte * 100) if total_journey_fte > 0 else 0.0
        
        # For now, set deltas to 0 (could calculate from baseline if needed)
        journey_deltas = {journey: 0.0 for journey in journey_totals.keys()}
        
        return JourneyKPIs(
            journey_totals=journey_totals,
            journey_percentages=journey_percentages,
            journey_deltas=journey_deltas
        )
    
    def _get_current_totals(self, offices_data: Dict[str, Any]) -> Dict[str, int]:
        """Get current total FTE counts from simulation data"""
        
        total_consultants = 0
        total_non_consultants = 0
        
        if not offices_data:
            return {'total_consultants': 0, 'total_non_consultants': 0, 'total_fte': 0}
        
        # Get the last period index
        periods = list(offices_data.values())[0]['levels']['Consultant']['A'] if offices_data else []
        last_idx = len(periods) - 1 if periods else 0
        
        for office_name, office_data in offices_data.items():
            # Count consultants
            if 'Consultant' in office_data['levels']:
                consultant_levels = office_data['levels']['Consultant']
                for level_name, level_data in consultant_levels.items():
                    if level_data and last_idx < len(level_data):
                        total_consultants += level_data[last_idx]['total']
            
            # Count non-consultants (Sales + Recruitment)
            for role_name in ['Sales', 'Recruitment']:
                if role_name in office_data['levels']:
                    role_levels = office_data['levels'][role_name]
                    for level_name, level_data in role_levels.items():
                        if level_data and last_idx < len(level_data):
                            total_non_consultants += level_data[last_idx]['total']
            
            # Count Operations
            if 'operations' in office_data and office_data['operations']:
                ops_data = office_data['operations']
                if last_idx < len(ops_data) and ops_data[last_idx]:
                    total_non_consultants += ops_data[last_idx]['total']
        
        return {
            'total_consultants': total_consultants,
            'total_non_consultants': total_non_consultants,
            'total_fte': total_consultants + total_non_consultants
        } 