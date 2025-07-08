"""
KPI Data Models

This module contains all the dataclasses used for KPI calculations and results.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class EconomicParameters:
    """Economic parameters for simulation and KPI calculations"""
    unplanned_absence: float = 0.05  # 5% default
    other_expense: float = 19000000.0  # 19M SEK monthly default
    employment_cost_rate: float = 0.40  # 40% overhead on salary costs
    working_hours_per_month: float = 166.4  # Monthly working hours
    utilization: float = 0.85  # 85% utilization rate default
    price_increase: float = 0.03  # 3% annual price increase default
    salary_increase: float = 0.02  # 2% annual salary increase default
    
    @classmethod
    def from_simulation_request(cls, params) -> 'EconomicParameters':
        """Create EconomicParameters from simulation request"""
        return cls(
            unplanned_absence=getattr(params, 'unplanned_absence', 0.05),
            other_expense=getattr(params, 'other_expense', 19000000.0),
            employment_cost_rate=getattr(params, 'employment_cost_rate', 0.40),
            working_hours_per_month=getattr(params, 'hy_working_hours', 166.4),
            utilization=getattr(params, 'utilization', 0.85),
            price_increase=getattr(params, 'price_increase', 0.03),
            salary_increase=getattr(params, 'salary_increase', 0.02)
        )


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