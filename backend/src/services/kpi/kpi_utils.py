"""
KPI Utilities

This module contains shared utility functions used across different KPI calculations.
"""

from typing import Dict, Any, List, Tuple
from ..config_service import ConfigService


def get_baseline_data() -> Dict[str, Any]:
    """Get baseline data from current configuration to avoid using hardcoded values"""
    config_service = ConfigService()
    current_config = config_service.get_configuration()
    
    baseline = {
        'offices': [],
        'total_consultants': 0,
        'total_non_consultants': 0,
        'total_fte': 0
    }
    
    for office_name, office_data in current_config.items():
        office_baseline = {
            'name': office_name,
            'roles': {},
            'consultants': 0,
            'non_consultants': 0,
            'total_fte': office_data.get('total_fte', 0)
        }
        
        # Use the actual roles from current configuration
        for role_name, role_data in office_data.get('roles', {}).items():
            if role_name == 'Operations':
                # Operations is a flat role
                office_baseline['roles']['Operations'] = {
                    'fte': role_data.get('fte', 0),
                    'price_1': role_data.get('price_1', 0),
                    'salary_1': role_data.get('salary_1', 0),
                    'utr_1': role_data.get('utr_1', 0.85)
                }
                office_baseline['non_consultants'] += role_data.get('fte', 0)
            else:
                # Roles with levels (Consultant, Sales, Recruitment)
                office_baseline['roles'][role_name] = {}
                for level_name, level_data in role_data.items():
                    if isinstance(level_data, dict):
                        level_fte = level_data.get('fte', 0)
                        office_baseline['roles'][role_name][level_name] = {
                            'fte': level_fte,
                            'price_1': level_data.get('price_1', 0),
                            'salary_1': level_data.get('salary_1', 0),
                            'utr_1': level_data.get('utr_1', 0.85)
                        }
                        
                        if role_name == 'Consultant':
                            office_baseline['consultants'] += level_fte
                        else:
                            office_baseline['non_consultants'] += level_fte
        
        baseline['offices'].append(office_baseline)
        baseline['total_consultants'] += office_baseline['consultants']
        baseline['total_non_consultants'] += office_baseline['non_consultants']
        baseline['total_fte'] += office_baseline['total_fte']
    
    return baseline


def calculate_fta_weighted_average_hourly_rate(year_data: Dict[str, Any], role_name: str = 'Consultant') -> float:
    """
    Calculate FTE-weighted average hourly rate for a specific role.
    
    Args:
        year_data: Year data from simulation results
        role_name: Role name to calculate for (default: 'Consultant')
        
    Returns:
        FTE-weighted average hourly rate
    """
    total_weighted_rate = 0.0
    total_fte = 0.0
    
    for office_name, office_data in year_data.get('offices', {}).items():
        if 'levels' in office_data and role_name in office_data['levels']:
            role_data = office_data['levels'][role_name]
            
            if isinstance(role_data, dict):
                # Hierarchical role with levels
                for level_name, level_data in role_data.items():
                    if isinstance(level_data, list) and level_data:
                        last_month_data = level_data[-1]
                        fte_count = last_month_data.get('fte', last_month_data.get('total', 0))
                        hourly_rate = last_month_data.get('price', 0)
                        
                        if fte_count > 0 and hourly_rate > 0:
                            total_weighted_rate += hourly_rate * fte_count
                            total_fte += fte_count
    
    return total_weighted_rate / total_fte if total_fte > 0 else 0.0


def extract_office_totals(year_data: Dict[str, Any]) -> Tuple[int, int, int]:
    """
    Extract total FTE counts from year data.
    
    Returns:
        Tuple of (total_fte, total_consultants, total_non_consultants)
    """
    current_total_fte = 0
    current_consultants = 0
    current_non_consultants = 0
    
    for office_name, office_data in year_data.get('offices', {}).items():
        # Check structure type
        if 'levels' in office_data:
            # Complex structure: extract from monthly arrays
            office_levels = office_data.get('levels', {})
            
            for role_name, role_data in office_levels.items():
                if isinstance(role_data, dict):
                    # Role with levels (Consultant, Sales, Recruitment)
                    for level_name, level_data in role_data.items():
                        if isinstance(level_data, list) and level_data:
                            # Get the last month's data
                            last_month_data = level_data[-1]
                            fte_count = last_month_data.get('fte', last_month_data.get('total', 0))
                            current_total_fte += fte_count
                            
                            if role_name == 'Consultant':
                                current_consultants += fte_count
                            else:
                                current_non_consultants += fte_count
                
                elif isinstance(role_data, list) and role_data:
                    # Flat role (Operations)
                    last_month_data = role_data[-1]
                    fte_count = last_month_data.get('fte', last_month_data.get('total', 0))
                    current_total_fte += fte_count
                    current_non_consultants += fte_count
        
        elif 'roles' in office_data:
            # Simple structure: direct access
            office_roles = office_data.get('roles', {})
            
            for role_key, role_data in office_roles.items():
                if isinstance(role_data, dict) and 'fte' in role_data:
                    fte_count = role_data.get('fte', 0)
                    current_total_fte += fte_count
                    
                    # Parse role and level from key
                    if role_key.startswith('Consultant_'):
                        current_consultants += fte_count
                    else:
                        # Non-consultant roles
                        current_non_consultants += fte_count
    
    return current_total_fte, current_consultants, current_non_consultants


def get_journey_mappings() -> Dict[str, List[str]]:
    """Get the mapping of levels to journey categories"""
    return {
        "Journey 1": ["A", "AC", "C"],
        "Journey 2": ["SrC", "AM"],
        "Journey 3": ["M", "SrM"],
        "Journey 4": ["PiP"]
    } 