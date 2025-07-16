"""
Scenario Resolver - Maps frontend scenario data to simulation engine format.

This service has a single responsibility: transform frontend scenario data
into the format expected by the simulation engine, including:
- Mapping baseline input to absolute recruitment/churn values
- Applying levers to config
- Loading progression and CAT curve data
"""
import copy
import logging
from typing import Dict, Any, Optional, Union

from .config_service import config_service
from config.progression_config import PROGRESSION_CONFIG, CAT_CURVES
from .unified_data_models import (
    BaselineInput, Levers, ProgressionConfig, CATCurves, TimeRange
)

logger = logging.getLogger(__name__)

class ScenarioResolver:
    """
    Resolves scenario data into simulation engine format.
    Focused solely on data transformation and mapping.
    """
    
    def __init__(self, config_service):
        self.config_service = config_service
    
    def resolve_scenario(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point: resolves scenario data into engine-ready format.
        Returns: {'offices_config', 'progression_config', 'cat_curves'}
        """
        # Load base config
        base_config = self.config_service.get_config()
        
        # Filter offices based on office_scope
        filtered_config = self._filter_offices_by_scope(base_config, scenario_data.get('office_scope', []))
        
        # Apply baseline input (absolute recruitment/churn values)
        config_with_baseline = self._apply_baseline_input(filtered_config, scenario_data)
        
        # Apply levers (multipliers)
        config_with_levers = self._apply_levers(config_with_baseline, scenario_data.get('levers', {}))
        
        # Load progression and CAT data (can be overridden by input)
        progression_config = self._load_progression_config(scenario_data)
        cat_curves = self._load_cat_curves(scenario_data)
        
        # Apply progression levers to CAT curves
        adjusted_cat_curves = self._adjust_cat_curves_by_levers(cat_curves, scenario_data.get('levers', {}))
        
        return {
            'offices_config': config_with_levers,
            'progression_config': progression_config,
            'cat_curves': adjusted_cat_curves
        }

    def resolve_scenario_with_models(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve scenario data using Pydantic models for type safety.
        Returns: {'offices_config', 'progression_config', 'cat_curves'}
        """
        # Load base config
        base_config = self.config_service.get_config()
        
        # Filter offices based on office_scope
        filtered_config = self._filter_offices_by_scope(base_config, scenario_data.get('office_scope', []))
        
        # Apply baseline input (absolute recruitment/churn values)
        config_with_baseline = self._apply_baseline_input_with_models(filtered_config, scenario_data)
        
        # Apply levers (multipliers)
        config_with_levers = self._apply_levers_with_models(config_with_baseline, scenario_data.get('levers', {}))
        
        # Load progression and CAT data (can be overridden by input)
        progression_config = self._load_progression_config_with_models(scenario_data)
        cat_curves = self._load_cat_curves_with_models(scenario_data)
        
        # Apply progression levers to CAT curves
        adjusted_cat_curves = self._adjust_cat_curves_by_levers_with_models(cat_curves, scenario_data.get('levers', {}))
        
        return {
            'offices_config': config_with_levers,
            'progression_config': progression_config,
            'cat_curves': adjusted_cat_curves
        }
    
    def _apply_baseline_input(self, base_config: Dict[str, Any], scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply baseline input to set absolute recruitment/churn values and economic data."""
        config = copy.deepcopy(base_config)
        baseline_input = scenario_data.get('baseline_input', {})
        
        if not baseline_input:
            return config
        
        # Calculate total FTE across all offices
        total_fte_all_offices = sum(office.get('total_fte', 0) for office in config.values())
        
        for office_name in config:
            config[office_name] = self._map_baseline_to_absolute_values(
                config[office_name], baseline_input, total_fte_all_offices, scenario_data.get('time_range')
            )
        
        return config
    
    def _map_baseline_to_absolute_values(self, office_config: Dict[str, Any], baseline_input: Dict[str, Any], total_fte_all_offices: float = None, time_range: Dict[str, Any] = None) -> Dict[str, Any]:
        """Map baseline input to absolute recruitment/churn fields and economic data."""
        office_config = copy.deepcopy(office_config)
        office_name = office_config.get('name', 'Unknown')
        
        # Handle both global and offices structures
        global_data = baseline_input.get('global', {})
        offices_data = baseline_input.get('offices', {})
        
        # If we have office-specific data, use it directly
        if office_name in offices_data:
            office_baseline = offices_data[office_name]
            return self._apply_office_baseline_data(office_config, office_baseline, time_range)
        
        # Otherwise, use global data with distribution
        if not global_data:
            return office_config

        # Calculate total FTE across all offices if not provided
        if total_fte_all_offices is None:
            total_fte_all_offices = office_config.get('total_fte', 0)

        office_fte = office_config.get('total_fte', 0)
        office_weight = office_fte / total_fte_all_offices if total_fte_all_offices else 0

        # Determine simulation time range
        if time_range is not None:
            start_year = time_range.get('start_year', 2025)
            start_month = time_range.get('start_month', 1)
            end_year = time_range.get('end_year', 2025)
            end_month = time_range.get('end_month', 12)
        else:
            start_year, start_month, end_year, end_month = 2025, 1, 2025, 12

        # Store original FTE values to ensure they're preserved
        original_fte_values = {}
        for role_name, role_data in office_config.get('roles', {}).items():
            if isinstance(role_data, dict):
                for level_name, level_config in role_data.items():
                    if isinstance(level_config, dict) and 'fte' in level_config:
                        original_fte_values[f"{role_name}.{level_name}"] = level_config['fte']

        for role_name, role_data in office_config.get('roles', {}).items():
            if isinstance(role_data, dict):
                for level_name, level_config in role_data.items():
                    if isinstance(level_config, dict):
                        # Ensure baseline FTE is preserved
                        level_key = f"{role_name}.{level_name}"
                        if level_key in original_fte_values:
                            level_config['fte'] = original_fte_values[level_key]

                        # Map recruitment data
                        if 'recruitment' in global_data and role_name in global_data['recruitment']:
                            recruitment_data = global_data['recruitment'][role_name]
                            if level_name in recruitment_data:
                                level_recruitment_data = recruitment_data[level_name]
                                # Loop over all years and months in the simulation time range
                                for year in range(start_year, end_year + 1):
                                    for month in range(1, 13):
                                        # Only include months within the simulation window
                                        if (year == start_year and month < start_month) or (year == end_year and month > end_month):
                                            continue
                                        month_key = f"{year}{month:02d}"
                                        global_value = level_recruitment_data.get(month_key, 0.0)
                                        distributed_value = global_value * office_weight
                                        field_name = f'recruitment_{month}'
                                        abs_field_name = f'recruitment_abs_{month}'
                                        # Set for each month of each year (engine expects per-year config, so overwrite for each year)
                                        level_config[field_name] = distributed_value
                                        level_config[abs_field_name] = distributed_value

                        # Map churn data
                        if 'churn' in global_data and role_name in global_data['churn']:
                            churn_data = global_data['churn'][role_name]
                            if level_name in churn_data:
                                level_churn_data = churn_data[level_name]
                                for year in range(start_year, end_year + 1):
                                    for month in range(1, 13):
                                        if (year == start_year and month < start_month) or (year == end_year and month > end_month):
                                            continue
                                        month_key = f"{year}{month:02d}"
                                        global_value = level_churn_data.get(month_key, 0.0)
                                        distributed_value = global_value * office_weight
                                        field_name = f'churn_{month}'
                                        abs_field_name = f'churn_abs_{month}'
                                        level_config[field_name] = distributed_value
                                        level_config[abs_field_name] = distributed_value

        return office_config
    
    def _apply_office_baseline_data(self, office_config: Dict[str, Any], office_baseline: Dict[str, Any], time_range: Dict[str, Any] = None) -> Dict[str, Any]:
        """Apply office-specific baseline data directly."""
        office_config = copy.deepcopy(office_config)
        
        # Determine simulation time range
        if time_range is not None:
            start_year = time_range.get('start_year', 2025)
            start_month = time_range.get('start_month', 1)
            end_year = time_range.get('end_year', 2025)
            end_month = time_range.get('end_month', 12)
        else:
            start_year, start_month, end_year, end_month = 2025, 1, 2025, 12
        
        # Apply office-level data
        if 'total_fte' in office_baseline:
            office_config['total_fte'] = office_baseline['total_fte']
        
        if 'journey' in office_baseline:
            office_config['journey'] = office_baseline['journey']
        
        # Apply role and level data
        baseline_roles = office_baseline.get('roles', {})
        
        for role_name, role_data in baseline_roles.items():
            if role_name not in office_config.get('roles', {}):
                continue
                
            office_role = office_config['roles'][role_name]
            
            # Check if this is a leveled role (Consultant, Sales, etc.) or flat role (Operations)
            if isinstance(role_data, dict) and any(isinstance(v, dict) for v in role_data.values()):
                # Leveled role (Consultant, Sales, etc.)
                for level_name, level_data in role_data.items():
                    if not isinstance(level_data, dict):
                        continue
                    if level_name not in office_role:
                        continue
                        
                    office_level = office_role[level_name]
                    
                    # Apply FTE
                    if 'fte' in level_data:
                        office_level['fte'] = level_data['fte']
                    
                    # Apply economic data (prices, salaries, UTR)
                    for month in range(1, 13):
                        # Only include months within the simulation window
                        if (start_year == end_year and (month < start_month or month > end_month)):
                            continue
                            
                        # Apply price data
                        if 'price_1' in level_data:
                            office_level[f'price_{month}'] = level_data['price_1']
                        
                        # Apply salary data
                        if 'salary_1' in level_data:
                            office_level[f'salary_{month}'] = level_data['salary_1']
                        
                        # Apply UTR data
                        if 'utr_1' in level_data:
                            office_level[f'utr_{month}'] = level_data['utr_1']
                        
                        # Apply recruitment data (absolute values)
                        for rec_key, rec_value in level_data.items():
                            if isinstance(rec_key, str) and rec_key.startswith('recruitment_abs_'):
                                try:
                                    month_num = int(rec_key.split('_')[-1])
                                    if start_year == end_year and (month_num < start_month or month_num > end_month):
                                        continue
                                    office_level[rec_key] = rec_value
                                    # Also set the percentage version for compatibility
                                    if 'fte' in level_data and level_data['fte'] > 0:
                                        office_level[rec_key.replace('_abs_', '_')] = (rec_value / level_data['fte']) * 100
                                except (ValueError, IndexError):
                                    continue
                        
                        # Apply churn data (absolute values)
                        for churn_key, churn_value in level_data.items():
                            if isinstance(churn_key, str) and churn_key.startswith('churn_abs_'):
                                try:
                                    month_num = int(churn_key.split('_')[-1])
                                    if start_year == end_year and (month_num < start_month or month_num > end_month):
                                        continue
                                    office_level[churn_key] = churn_value
                                    # Also set the percentage version for compatibility
                                    if 'fte' in level_data and level_data['fte'] > 0:
                                        office_level[churn_key.replace('_abs_', '_')] = (churn_value / level_data['fte']) * 100
                                except (ValueError, IndexError):
                                    continue
            else:
                # Flat role (Operations) - role_data is a dict with direct values
                if isinstance(role_data, dict) and isinstance(office_role, dict):
                    # Apply FTE
                    if 'fte' in role_data:
                        office_role['fte'] = role_data['fte']
                    
                    # Apply economic data
                    for month in range(1, 13):
                        if (start_year == end_year and (month < start_month or month > end_month)):
                            continue
                            
                        if 'price_1' in role_data:
                            office_role[f'price_{month}'] = role_data['price_1']
                        
                        if 'salary_1' in role_data:
                            office_role[f'salary_{month}'] = role_data['salary_1']
                        
                        if 'utr_1' in role_data:
                            office_role[f'utr_{month}'] = role_data['utr_1']
                        
                        # Apply recruitment and churn data
                        for key, value in role_data.items():
                            if isinstance(key, str) and key.startswith('recruitment_abs_'):
                                try:
                                    month_num = int(key.split('_')[-1])
                                    if start_year == end_year and (month_num < start_month or month_num > end_month):
                                        continue
                                    office_role[key] = value
                                    if 'fte' in role_data and role_data['fte'] > 0:
                                        office_role[key.replace('_abs_', '_')] = (value / role_data['fte']) * 100
                                except (ValueError, IndexError):
                                    continue
                            
                            elif isinstance(key, str) and key.startswith('churn_abs_'):
                                try:
                                    month_num = int(key.split('_')[-1])
                                    if start_year == end_year and (month_num < start_month or month_num > end_month):
                                        continue
                                    office_role[key] = value
                                    if 'fte' in role_data and role_data['fte'] > 0:
                                        office_role[key.replace('_abs_', '_')] = (value / role_data['fte']) * 100
                                except (ValueError, IndexError):
                                    continue
        
        return office_config
    
    def _filter_offices_by_scope(self, base_config: Dict[str, Any], office_scope: list) -> Dict[str, Any]:
        """
        Filter offices based on office_scope parameter.
        If office_scope is empty or None, return all offices.
        If office_scope contains specific offices, return only those offices.
        """
        if not office_scope:
            # No office scope specified, return all offices
            return base_config
        
        # Filter to only include offices in the scope
        filtered_config = {}
        for office_name, office_config in base_config.items():
            if office_name in office_scope:
                filtered_config[office_name] = office_config
        
        logger.info(f"Filtered offices by scope: {office_scope}. "
                   f"Original offices: {list(base_config.keys())}, "
                   f"Filtered offices: {list(filtered_config.keys())}")
        
        return filtered_config
    
    def _apply_levers(self, config: Dict[str, Any], levers: Dict[str, Any]) -> Dict[str, Any]:
        """Apply levers (multipliers) to the config."""
        if not levers:
            return config
        
        config = copy.deepcopy(config)
        
        # Apply to all offices
        for office_name in config:
            config[office_name] = self._apply_levers_to_office(config[office_name], levers)
        
        return config
    
    def _apply_levers_to_office(self, office_config: Dict[str, Any], levers: Dict[str, Any]) -> Dict[str, Any]:
        """Apply levers to a single office config."""
        office_config = copy.deepcopy(office_config)
        
        # Get global levers
        global_levers = levers.get('global', {})
        if not global_levers:
            return office_config
        
        # Apply global levers to all offices
        for role_name, role_config in office_config.get('roles', {}).items():
            if not isinstance(role_config, dict):
                continue
                
            for level_name, level_config in role_config.items():
                if not isinstance(level_config, dict):
                    continue
                
                # Apply price levers
                if 'price' in global_levers and level_name in global_levers['price']:
                    price_value = global_levers['price'][level_name]
                    for month in range(1, 13):
                        level_config[f'price_{month}'] = price_value
                
                # Apply salary levers
                if 'salary' in global_levers and level_name in global_levers['salary']:
                    salary_value = global_levers['salary'][level_name]
                    for month in range(1, 13):
                        level_config[f'salary_{month}'] = salary_value
                
                # Apply recruitment levers
                if 'recruitment' in global_levers and level_name in global_levers['recruitment']:
                    recruitment_multiplier = global_levers['recruitment'][level_name]
                    for month in range(1, 13):
                        # Multiply both percentage and absolute recruitment values
                        if f'recruitment_{month}' in level_config:
                            level_config[f'recruitment_{month}'] *= recruitment_multiplier
                        if f'recruitment_abs_{month}' in level_config:
                            level_config[f'recruitment_abs_{month}'] *= recruitment_multiplier
                
                # Apply churn levers
                if 'churn' in global_levers and level_name in global_levers['churn']:
                    churn_multiplier = global_levers['churn'][level_name]
                    for month in range(1, 13):
                        # Multiply both percentage and absolute churn values
                        if f'churn_{month}' in level_config:
                            level_config[f'churn_{month}'] *= churn_multiplier
                        if f'churn_abs_{month}' in level_config:
                            level_config[f'churn_abs_{month}'] *= churn_multiplier
        
        return office_config
    
    def _load_progression_config(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Load progression configuration from input or fallback to default."""
        # Check if progression config is provided in scenario data and is not None
        if 'progression_config' in scenario_data and scenario_data['progression_config'] is not None:
            logger.info("[DEBUG] Using progression config from scenario data")
            return scenario_data['progression_config']
        
        # Fallback to default config
        logger.info("[DEBUG] Using default progression config")
        return PROGRESSION_CONFIG
    
    def _load_cat_curves(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Load CAT progression curves from input or fallback to default."""
        # Check if CAT curves are provided in scenario data and is not None
        if 'cat_curves' in scenario_data and scenario_data['cat_curves'] is not None:
            logger.info("[DEBUG] Using CAT curves from scenario data")
            return scenario_data['cat_curves']
        
        # Fallback to default curves
        logger.info("[DEBUG] Using default CAT curves")
        return CAT_CURVES
    
    def _adjust_cat_curves_by_levers(self, cat_curves: Dict[str, Any], levers: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust CAT curves by progression levers."""
        progression_levers = levers.get('progression', {})
        
        if not progression_levers:
            return cat_curves
        
        # Create a copy to avoid modifying the original
        adjusted_curves = copy.deepcopy(cat_curves)
        
        # Apply progression multipliers if specified
        if 'multiplier' in progression_levers:
            multiplier = progression_levers['multiplier']
            for level_name, level_curves in adjusted_curves.items():
                for cat_category in level_curves:
                    if isinstance(level_curves[cat_category], (int, float)):
                        level_curves[cat_category] *= multiplier
        
        return adjusted_curves

    # ========================================
    # Pydantic Model Methods
    # ========================================

    def _apply_baseline_input_with_models(self, base_config: Dict[str, Any], scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply baseline input using Pydantic models for type safety."""
        config = copy.deepcopy(base_config)
        baseline_input = scenario_data.get('baseline_input')
        
        if not baseline_input:
            return config
        
        # Convert Pydantic model to dict if needed
        if hasattr(baseline_input, 'model_dump'):
            baseline_input = baseline_input.model_dump()
        
        # Calculate total FTE across all offices
        total_fte_all_offices = sum(office.get('total_fte', 0) for office in config.values())
        
        for office_name in config:
            config[office_name] = self._map_baseline_to_absolute_values(
                config[office_name], baseline_input, total_fte_all_offices, scenario_data.get('time_range')
            )
        
        return config

    def _apply_levers_with_models(self, config: Dict[str, Any], levers: Union[Dict[str, Any], Levers]) -> Dict[str, Any]:
        """Apply levers using Pydantic models for type safety."""
        if not levers:
            return config
        
        # Convert Pydantic model to dict if needed
        if hasattr(levers, 'model_dump'):
            levers = levers.model_dump()
        
        return self._apply_levers(config, levers)

    def _load_progression_config_with_models(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Load progression configuration using Pydantic models for type safety."""
        progression_config = scenario_data.get('progression_config')
        
        if progression_config is not None:
            # Convert Pydantic model to dict if needed
            if hasattr(progression_config, 'model_dump'):
                progression_config = progression_config.model_dump()
            logger.info("[DEBUG] Using progression config from scenario data")
            return progression_config
        
        # Fallback to default config
        logger.info("[DEBUG] Using default progression config")
        return PROGRESSION_CONFIG

    def _load_cat_curves_with_models(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Load CAT curves using Pydantic models for type safety."""
        cat_curves = scenario_data.get('cat_curves')
        
        if cat_curves is not None:
            # Convert Pydantic model to dict if needed
            if hasattr(cat_curves, 'model_dump'):
                cat_curves = cat_curves.model_dump()
            logger.info("[DEBUG] Using CAT curves from scenario data")
            return cat_curves
        
        # Fallback to default curves
        logger.info("[DEBUG] Using default CAT curves")
        return CAT_CURVES

    def _adjust_cat_curves_by_levers_with_models(self, cat_curves: Dict[str, Any], levers: Union[Dict[str, Any], Levers]) -> Dict[str, Any]:
        """Adjust CAT curves by progression levers using Pydantic models for type safety."""
        # Convert Pydantic model to dict if needed
        if hasattr(levers, 'model_dump'):
            levers = levers.model_dump()
        
        return self._adjust_cat_curves_by_levers(cat_curves, levers) 