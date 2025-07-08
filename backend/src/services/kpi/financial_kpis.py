"""
Financial KPI Calculations

This module contains all financial KPI calculation logic including revenue, costs, EBITDA, and margins.
"""

from typing import Dict, Any
from .kpi_models import EconomicParameters, FinancialKPIs
from .kpi_utils import get_baseline_data, calculate_fta_weighted_average_hourly_rate


class FinancialKPICalculator:
    """Calculator for financial KPIs"""
    
    def __init__(self, economic_params: EconomicParameters):
        self.economic_params = economic_params
        self.working_hours_per_month = economic_params.working_hours_per_month
        self.total_employment_cost_rate = economic_params.employment_cost_rate
    
    def calculate_baseline_financial_metrics(
        self, 
        baseline_data: Dict[str, Any], 
        unplanned_absence: float, 
        other_expense: float,
        duration_months: int = 12
    ) -> Dict[str, float]:
        """Calculate baseline financial metrics for comparison"""
        
        total_revenue = 0
        total_salary_costs = 0
        total_consultants = 0
        total_costs = 0

        # Available hours after accounting for unplanned absence
        available_hours_per_month = self.working_hours_per_month * (1 - unplanned_absence)

        # Distribute other_expense proportionally across offices based on their FTE
        total_system_fte = sum(office_data.get('total_fte', 0) for office_data in baseline_data.get('offices', []))

        office_count = 0
        for office_data in baseline_data.get('offices', []):
            office_count += 1
            office_name = office_data.get('name', f'Office_{office_count}')
            
            office_revenue = 0
            office_salary_costs = 0
            office_fte = office_data.get('total_fte', 0)
            
            for role_name, role_data in office_data.get('roles', {}).items():
                
                if role_name == 'Consultant':
                    consultant_levels = role_data
                    
                    for level_name, level_data in consultant_levels.items():
                        if level_data:
                            fte_count = level_data.get('fte', 0)
                            hourly_rate = level_data.get('price_1', 0)
                            salary = level_data.get('salary_1', 0)
                            utr = level_data.get('utr_1', 0.85)
                            
                            if fte_count > 0:
                                # Calculate revenue
                                billable_hours = available_hours_per_month * utr
                                monthly_revenue_per_person = hourly_rate * billable_hours
                                level_total_revenue = fte_count * monthly_revenue_per_person * duration_months
                                office_revenue += level_total_revenue
                                
                                # Calculate costs
                                base_salary_cost = fte_count * salary * duration_months
                                office_salary_costs += base_salary_cost
                                
                                # Track for weighted averages
                                total_consultants += fte_count
                else:
                    if isinstance(role_data, dict) and 'fte' in role_data:
                        # Flat role like Operations
                        fte_count = role_data.get('fte', 0)
                        salary = role_data.get('salary_1', 0)
                        
                        if fte_count > 0:
                            base_salary_cost = fte_count * salary * duration_months
                            office_salary_costs += base_salary_cost
                    else:
                        # Role with levels
                        for level_name, level_data in role_data.items():
                            if level_data:
                                fte_count = level_data.get('fte', 0)
                                salary = level_data.get('salary_1', 0)
                                
                                if fte_count > 0:
                                    base_salary_cost = fte_count * salary * duration_months
                                    office_salary_costs += base_salary_cost
            
            # Calculate total costs for the office
            office_total_employment_cost = office_salary_costs * (1 + self.total_employment_cost_rate)
            
            # Allocate a portion of other_expense to this office (annualized)
            office_other_expense = 0
            if total_system_fte > 0:
                office_other_expense = (office_fte / total_system_fte) * other_expense * duration_months
            
            office_total_costs = office_total_employment_cost + office_other_expense
            
            # Add office totals to global totals
            total_revenue += office_revenue
            total_costs += office_total_costs
            total_salary_costs += office_salary_costs
        
        # Calculate FTE-weighted average hourly rate using the same method as current calculation
        weighted_sum = 0.0
        total_fte = 0.0
        for office_data in baseline_data.get('offices', []):
            office_name = office_data.get('name', 'Unknown')
            for role_name, role_data in office_data.get('roles', {}).items():
                if role_name == 'Consultant':
                    for level_name, level_data in role_data.items():
                        if level_data:
                            # Use price_1 for baseline (same as current calculation uses first month)
                            hourly_rate = level_data.get('price_1', 0)
                            level_fte = level_data.get('fte', 0)
                            if hourly_rate > 0 and level_fte > 0:
                                weighted_sum += hourly_rate * level_fte
                                total_fte += level_fte
        avg_hourly_rate = weighted_sum / total_fte if total_fte > 0 else 0

        # Final calculations
        ebitda = total_revenue - total_costs
        margin = (ebitda / total_revenue) if total_revenue > 0 else 0

        return {
            'total_revenue': total_revenue,
            'total_salary_costs': total_salary_costs,
            'total_costs': total_costs,
            'ebitda': ebitda,
            'margin': margin,
            'total_consultants': total_consultants,
            'avg_hourly_rate': avg_hourly_rate
        }
    
    def calculate_current_financial_metrics(
        self, 
        year_data: Dict[str, Any],
        unplanned_absence: float,
        other_expense: float,
        duration_months: int = 12
    ) -> Dict[str, float]:
        """Calculate financial metrics for current simulation data, with proportional expense allocation."""
        
        total_revenue = 0.0
        total_costs = 0.0
        total_salary_costs = 0.0
        total_consultants = 0

        # Calculate total FTE for the year to use for expense allocation
        total_system_fte = sum(office.get('total_fte', 0) for office in year_data.get('offices', {}).values())
        
        office_count = 0
        # Process each office
        for office_name, office_data in year_data.get('offices', {}).items():
            office_count += 1
            
            office_revenue = 0.0
            office_salary_costs = 0.0
            
            office_fte = office_data.get('total_fte', 0)
            
            # This logic handles the complex data structure from the simulation engine
            if 'levels' in office_data:
                office_levels = office_data.get('levels', {})
                
                for role_name, role_data in office_levels.items():
                    
                    if isinstance(role_data, dict): # Hierarchical roles
                        for level_name, level_data in role_data.items():
                            if isinstance(level_data, list) and level_data:
                                last_month_data = level_data[-1]
                                fte_count = last_month_data.get('fte', 0)
                                hourly_rate = last_month_data.get('price', 0)
                                salary = last_month_data.get('salary', 0)
                                utr = last_month_data.get('utr', 0.85)
                                
                                if fte_count > 0:
                                    if role_name == 'Consultant':
                                        available_hours = self.working_hours_per_month * (1 - unplanned_absence)
                                        billable_hours = available_hours * utr
                                        monthly_revenue_per_person = hourly_rate * billable_hours
                                        level_total_revenue = fte_count * monthly_revenue_per_person * duration_months
                                        office_revenue += level_total_revenue
                                        total_consultants += fte_count
                                    
                                    base_salary_cost = fte_count * salary * duration_months
                                    office_salary_costs += base_salary_cost
                                    
                    elif isinstance(role_data, list) and role_data: # Flat roles
                        last_month_data = role_data[-1]
                        fte_count = last_month_data.get('fte', 0)
                        salary = last_month_data.get('salary', 0) if 'salary' in last_month_data else 40000.0
                        
                        if fte_count > 0:
                            base_salary_cost = fte_count * salary * duration_months
                            office_salary_costs += base_salary_cost
            
            # Calculate total costs for the office
            office_total_employment_cost = office_salary_costs * (1 + self.total_employment_cost_rate)
            
            # Annualize the allocated portion of other_expense
            office_other_expense = 0
            if total_system_fte > 0:
                office_other_expense = (office_fte / total_system_fte) * other_expense * duration_months
            
            office_total_costs = office_total_employment_cost + office_other_expense
            
            # Add office totals to global totals
            total_revenue += office_revenue
            total_costs += office_total_costs
            total_salary_costs += office_salary_costs
        
        # Calculate FTE-weighted average hourly rate
        avg_hourly_rate_year = calculate_fta_weighted_average_hourly_rate(year_data, 'Consultant')
        
        # Calculate final metrics
        ebitda = total_revenue - total_costs
        margin = ebitda / total_revenue if total_revenue > 0 else 0.0
        
        return {
            'total_revenue': total_revenue,
            'total_costs': total_costs,
            'total_salary_costs': total_salary_costs,
            'ebitda': ebitda,
            'margin': margin,
            'avg_hourly_rate': avg_hourly_rate_year,
            'total_consultants': total_consultants
        } 