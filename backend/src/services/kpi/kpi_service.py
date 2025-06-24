"""
KPI Service Orchestration

This module provides the main KPIService class, orchestrating all KPI calculations using the submodules.
"""

from typing import Dict, Any, Optional
from .kpi_models import EconomicParameters, FinancialKPIs, GrowthKPIs, JourneyKPIs, YearlyKPIs, AllKPIs
from .financial_kpis import FinancialKPICalculator
from .growth_kpis import calculate_growth_metrics
from .journey_kpis import calculate_journey_metrics
from .kpi_utils import get_baseline_data


class KPIService:
    """Service for calculating all simulation KPIs"""
    
    def __init__(self, economic_params: Optional[EconomicParameters] = None):
        self.economic_params = economic_params or EconomicParameters()
        self.financial_calculator = FinancialKPICalculator(self.economic_params)

    def calculate_all_kpis(
        self, 
        simulation_results: Dict[str, Any], 
        simulation_duration_months: int,
        economic_params: Optional[EconomicParameters] = None
    ) -> AllKPIs:
        params = economic_params or self.economic_params
        self.financial_calculator = FinancialKPICalculator(params)

        # Determine which year to use for current KPIs
        years = list(simulation_results['years'].keys())
        if len(years) == 1:
            # Single year simulation - use that year
            current_year = years[0]
        else:
            # Multi-year simulation - use first year for consistency with baseline
            first_year = min(years)
            current_year = first_year
        
        # Get current year data
        current_year_data = simulation_results['years'][current_year]
        
        baseline_data = get_baseline_data()
        
        baseline_financial = self.financial_calculator.calculate_baseline_financial_metrics(
            baseline_data, params.unplanned_absence, params.other_expense, duration_months=12
        )
        current_financial = self.financial_calculator.calculate_current_financial_metrics(
            current_year_data, params.unplanned_absence, params.other_expense, duration_months=12
        )
        growth_metrics = calculate_growth_metrics(baseline_data, current_year_data)
        journey_metrics = calculate_journey_metrics(current_year_data)

        yearly_kpis = {}
        for year, year_data in simulation_results['years'].items():
            yearly_financial = self.financial_calculator.calculate_current_financial_metrics(
                year_data, params.unplanned_absence, params.other_expense, duration_months=12
            )
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

        return AllKPIs(
            financial=financial_kpis,
            growth=growth_metrics,
            journeys=journey_metrics,
            yearly_kpis=yearly_kpis
        )

    def calculate_kpis_for_year(
        self, 
        simulation_results: Dict[str, Any], 
        target_year: str,
        simulation_duration_months: int,
        economic_params: Optional[EconomicParameters] = None
    ) -> AllKPIs:
        params = economic_params or self.economic_params
        self.financial_calculator = FinancialKPICalculator(params)
        baseline_data = get_baseline_data()
        baseline_financial = self.financial_calculator.calculate_baseline_financial_metrics(
            baseline_data, params.unplanned_absence, params.other_expense, duration_months=12
        )
        if target_year not in simulation_results.get('years', {}):
            raise ValueError(f"Year {target_year} not found in simulation results")
        target_year_data = simulation_results['years'][target_year]
        current_financial = self.financial_calculator.calculate_current_financial_metrics(
            target_year_data, params.unplanned_absence, params.other_expense, duration_months=12
        )
        growth_metrics = calculate_growth_metrics(baseline_data, target_year_data)
        journey_metrics = calculate_journey_metrics(target_year_data)
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
        return AllKPIs(
            financial=financial_kpis,
            growth=growth_metrics,
            journeys=journey_metrics,
            yearly_kpis={}
        ) 