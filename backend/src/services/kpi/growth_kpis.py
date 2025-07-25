"""
Growth KPI Calculations

This module contains all growth and headcount KPI calculation logic.
"""

from typing import Dict, Any
from .kpi_models import GrowthKPIs


def calculate_growth_metrics(baseline_data: Dict[str, Any], final_year_data: Dict[str, Any]) -> GrowthKPIs:
    """Calculate growth metrics comparing baseline to final year"""
    baseline_total_fte = baseline_data.get('total_fte', 0)
    baseline_consultants = baseline_data.get('total_consultants', 0)
    baseline_non_consultants = baseline_data.get('total_non_consultants', 0)

    current_total_fte = 0
    current_consultants = 0
    current_non_consultants = 0

    for office_name, office_data in final_year_data.get('offices', {}).items():
        if 'roles' in office_data:
            office_roles = office_data.get('roles', {})
            for role_name, role_data in office_roles.items():
                if isinstance(role_data, dict):
                    for level_name, level_data in role_data.items():
                        if isinstance(level_data, list) and level_data:
                            last_month_data = level_data[-1]
                            fte_count = last_month_data.get('fte', 0)
                            current_total_fte += fte_count
                            if role_name == 'Consultant':
                                current_consultants += fte_count
                            else:
                                current_non_consultants += fte_count
                elif isinstance(role_data, list) and role_data:
                    last_month_data = role_data[-1]
                    fte_count = last_month_data.get('fte', 0)
                    current_total_fte += fte_count
                    current_non_consultants += fte_count
        elif 'roles' in office_data:
            office_roles = office_data.get('roles', {})
            for role_key, role_data in office_roles.items():
                if isinstance(role_data, dict) and 'fte' in role_data:
                    fte_count = role_data.get('fte', 0)
                    current_total_fte += fte_count
                    if role_key.startswith('Consultant_'):
                        current_consultants += fte_count
                    else:
                        current_non_consultants += fte_count

    total_growth_rate = ((current_total_fte - baseline_total_fte) / baseline_total_fte * 100) if baseline_total_fte > 0 else 0.0
    current_non_debit_ratio = (current_non_consultants / current_total_fte) if current_total_fte > 0 else 0.0
    baseline_non_debit_ratio = (baseline_non_consultants / baseline_total_fte) if baseline_total_fte > 0 else 0.0

    return GrowthKPIs(
        total_growth_percent=total_growth_rate,
        total_growth_absolute=current_total_fte - baseline_total_fte,
        current_total_fte=current_total_fte,
        baseline_total_fte=baseline_total_fte,
        non_debit_ratio=current_non_debit_ratio,
        non_debit_ratio_baseline=baseline_non_debit_ratio,
        non_debit_delta=current_non_debit_ratio - baseline_non_debit_ratio
    ) 