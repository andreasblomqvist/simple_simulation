"""
Journey KPI Calculations

This module contains all journey distribution KPI calculation logic.
"""

from typing import Dict, Any
from .kpi_models import JourneyKPIs
from .kpi_utils import get_baseline_data, get_journey_mappings


def calculate_journey_metrics(final_year_data: Dict[str, Any]) -> JourneyKPIs:
    """Calculate journey distribution metrics"""
    baseline_data = get_baseline_data()
    journey_mappings = get_journey_mappings()

    # Calculate baseline journey totals
    baseline_journey_totals = {k: 0 for k in journey_mappings}
    for office in baseline_data.get('offices', []):
        office_roles = office.get('roles', {})
        for role_name, role_data in office_roles.items():
            if role_name in ['Consultant', 'Sales', 'Recruitment']:
                for level_name, level_data in role_data.items():
                    level_fte = level_data.get('fte', 0)
                    for journey_name, levels in journey_mappings.items():
                        if level_name in levels:
                            baseline_journey_totals[journey_name] += level_fte

    # Calculate current journey totals
    current_journey_totals = {k: 0 for k in journey_mappings}
    for office_name, office_data in final_year_data.get('offices', {}).items():
        if 'roles' in office_data:
            office_roles = office_data.get('roles', {})
            for role_name, role_data in office_roles.items():
                if isinstance(role_data, dict) and role_name in ['Consultant', 'Sales', 'Recruitment']:
                    for level_name, level_data in role_data.items():
                        if isinstance(level_data, list) and level_data:
                            last_month_data = level_data[-1]
                            fte_count = last_month_data.get('total', 0)
                            for journey_name, levels in journey_mappings.items():
                                if level_name in levels:
                                    current_journey_totals[journey_name] += fte_count
                                    break
        elif 'roles' in office_data:
            office_roles = office_data.get('roles', {})
            for role_key, role_data in office_roles.items():
                if isinstance(role_data, dict) and 'fte' in role_data:
                    fte_count = role_data.get('fte', 0)
                    if '_' in role_key:
                        role_name, level_name = role_key.split('_', 1)
                        if role_name in ['Consultant', 'Sales', 'Recruitment']:
                            for journey_name, levels in journey_mappings.items():
                                if level_name in levels:
                                    current_journey_totals[journey_name] += fte_count
                                    break

    total_current_fte = sum(current_journey_totals.values())
    total_baseline_fte = sum(baseline_journey_totals.values())

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

    return JourneyKPIs(
        journey_totals=current_journey_totals,
        journey_percentages=current_percentages,
        journey_deltas=journey_deltas,
        journey_totals_baseline=baseline_journey_totals,
        journey_percentages_baseline=baseline_percentages
    ) 