"""
Scenario Resolver - Maps frontend scenario data to simulation engine format.

This service has a single responsibility: transform frontend scenario data
into the format expected by the simulation engine, including:
- Mapping baseline input to absolute recruitment/churn values
- Applying levers to config
- Loading progression and CAT curve data
"""
import copy
import json
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
        """Apply baseline input to set absolute recruitment/churn values with exact distribution."""
        config = copy.deepcopy(base_config)
        baseline_input = scenario_data.get('baseline_input', {})
        business_plan_id = scenario_data.get('business_plan_id')
        
        logger.info(f"[DEBUG] _apply_baseline_input called with baseline_input: {baseline_input is not None}, business_plan_id: {business_plan_id}")
        
        # If no baseline_input but we have a business_plan_id, fetch from business plan
        if not baseline_input and business_plan_id:
            logger.info(f"[DEBUG] Fetching baseline from business plan: {business_plan_id}")
            baseline_input = self._fetch_baseline_from_business_plan(business_plan_id, scenario_data)
        
        if baseline_input:
            logger.info(f"[DEBUG] baseline_input keys: {list(baseline_input.keys())}")
        
        if not baseline_input:
            logger.info("[DEBUG] No baseline_input provided and no business plan, using default baseline")
            # Generate a default baseline with reasonable values
            baseline_input = self._generate_default_baseline(scenario_data)
        
        # Apply exact distribution to preserve total FTE
        config = self._apply_exact_distribution(config, baseline_input, scenario_data.get('time_range'))
        
        return config
    
    def _apply_exact_distribution(self, config: Dict[str, Any], baseline_input: Dict[str, Any], time_range: Dict[str, Any] = None) -> Dict[str, Any]:
        """Apply exact distribution using largest remainder method to preserve total FTE."""
        # Handle None baseline_input
        if baseline_input is None:
            logger.info("[DEBUG] baseline_input is None, returning config unchanged")
            return config
            
        global_data = baseline_input.get('global', baseline_input.get('global_data', {}))
        offices_data = baseline_input.get('offices', {})
        
        logger.info(f"[DEBUG] baseline_input keys: {list(baseline_input.keys())}")
        logger.info(f"[DEBUG] global_data keys: {list(global_data.keys()) if global_data else 'None'}")
        logger.info(f"[DEBUG] offices_data keys: {list(offices_data.keys()) if offices_data else 'None'}")
        
        # If we have office-specific data, use it directly
        for office_name in config:
            if office_name in offices_data:
                office_baseline = offices_data[office_name]
                config[office_name] = self._apply_office_baseline_data(config[office_name], office_baseline, time_range)
        
        # Apply global data with exact distribution
        if global_data:
            config = self._distribute_global_values_exactly(config, global_data, time_range)
        
        return config
    
    def _distribute_global_values_exactly(self, config: Dict[str, Any], global_data: Dict[str, Any], time_range: Dict[str, Any] = None) -> Dict[str, Any]:
        """Distribute global values using largest remainder method to preserve exact totals."""
        # Calculate total FTE across all offices
        total_fte_all_offices = sum(office.get('total_fte', 0) for office in config.values())
        
        # Determine simulation time range
        if time_range is not None:
            # Handle both dict and Pydantic model
            if hasattr(time_range, 'get'):
                start_year = time_range.get('start_year', 2025)
                start_month = time_range.get('start_month', 1)
                end_year = time_range.get('end_year', 2025)
                end_month = time_range.get('end_month', 12)
            else:
                # Pydantic model
                start_year = getattr(time_range, 'start_year', 2025)
                start_month = getattr(time_range, 'start_month', 1)
                end_year = getattr(time_range, 'end_year', 2025)
                end_month = getattr(time_range, 'end_month', 12)
        else:
            start_year, start_month, end_year, end_month = 2025, 1, 2025, 12
        
        # Process recruitment and churn data (unified nested structure)
        for data_type in ['recruitment', 'churn']:
            if data_type in global_data:
                type_data = global_data[data_type]
                for role_name, role_data in type_data.items():
                    # Skip null role_data
                    if role_data is None:
                        continue
                    # Handle both nested and flat structures
                    if 'levels' in role_data and role_data['levels'] is not None:
                        # Nested structure: role -> levels -> levelName -> recruitment/churn -> values
                        for level_name, level_data in role_data['levels'].items():
                            # Skip null level_data
                            if level_data is None:
                                continue
                            if data_type in level_data and 'values' in level_data[data_type] and level_data[data_type]['values'] is not None:
                                level_values = level_data[data_type]['values']
                                for year in range(start_year, end_year + 1):
                                    for month in range(1, 13):
                                        if (year == start_year and month < start_month) or (year == end_year and month > end_month):
                                            continue
                                        month_key = f"{year}{month:02d}"
                                        global_value = level_values.get(month_key, 0.0)
                                        
                                        if global_value > 0:
                                            # Apply exact distribution
                                            distributed_values = self._exact_distribute_value(
                                                global_value, config, role_name, level_name, total_fte_all_offices
                                            )
                                            
                                            # Apply distributed values to offices
                                            for office_name, office_value in distributed_values.items():
                                                if office_name in config:
                                                    office_config = config[office_name]
                                                    if 'roles' in office_config and role_name in office_config['roles']:
                                                        role_config = office_config['roles'][role_name]
                                                        if isinstance(role_config, dict) and level_name in role_config:
                                                            level_config = role_config[level_name]
                                                            if isinstance(level_config, dict):
                                                                # Only set absolute field, not percentage
                                                                abs_field_name = f'{data_type}_abs_{month}'
                                                                level_config[abs_field_name] = office_value
                    else:
                        # Flat structure: role -> monthKey -> levelName -> value
                        logger.info(f"[DEBUG] Processing flat structure for {data_type}.{role_name}")
                        logger.info(f"[DEBUG] role_data keys: {list(role_data.keys())}")
                        for month_key, month_data in role_data.items():
                            if isinstance(month_data, dict):
                                logger.info(f"[DEBUG] Processing month {month_key} with data: {month_data}")
                                for level_name, value in month_data.items():
                                    if isinstance(value, (int, float)) and value > 0:
                                        logger.info(f"[DEBUG] Setting {data_type}_abs for {role_name}.{level_name} month {month_key} = {value}")
                                        # Parse month from month_key (e.g., "202501" -> month 1)
                                        try:
                                            if len(month_key) == 6:  # Format: YYYYMM
                                                year = int(month_key[:4])
                                                month = int(month_key[4:6])
                                                
                                                # Check if month is within simulation window
                                                if (year == start_year and month < start_month) or (year == end_year and month > end_month):
                                                    continue
                                                
                                                # Apply exact distribution
                                                distributed_values = self._exact_distribute_value(
                                                    value, config, role_name, level_name, total_fte_all_offices
                                                )
                                                
                                                # Apply distributed values to offices
                                                for office_name, office_value in distributed_values.items():
                                                    if office_name in config:
                                                        office_config = config[office_name]
                                                        if 'roles' in office_config and role_name in office_config['roles']:
                                                            role_config = office_config['roles'][role_name]
                                                            if isinstance(role_config, dict) and level_name in role_config:
                                                                level_config = role_config[level_name]
                                                                if isinstance(level_config, dict):
                                                                    # Only set absolute field, not percentage
                                                                    abs_field_name = f'{data_type}_abs_{month}'
                                                                    level_config[abs_field_name] = office_value
                                                                    logger.info(f"[DEBUG] Successfully set {office_name}.{role_name}.{level_name}.{abs_field_name} = {office_value}")
                                        except (ValueError, IndexError):
                                            # Skip invalid month keys
                                            continue
        
        return config
    
    def _exact_distribute_value(self, total_value: float, config: Dict[str, Any], role_name: str, level_name: str, total_fte_all_offices: float) -> Dict[str, float]:
        """Distribute a value exactly using largest remainder method based on total role FTE (not role/level)."""
        if total_value == 0:
            return {office_name: 0.0 for office_name in config.keys()}
        
        # Calculate total FTE for this role across all offices (sum of all levels)
        total_role_fte = 0
        office_role_ftes = {}
        
        for office_name, office_config in config.items():
            office_role_fte = 0
            
            # Get total FTE for this role in this office (sum all levels)
            if ('roles' in office_config and 
                role_name in office_config['roles']):
                
                role_config = office_config['roles'][role_name]
                
                if isinstance(role_config, dict):
                    # Leveled role (Consultant, Sales, etc.) - sum all levels
                    for level_config in role_config.values():
                        if isinstance(level_config, dict):
                            office_role_fte += level_config.get('fte', 0)
                else:
                    # Flat role (Operations) - use direct FTE
                    office_role_fte = role_config.get('fte', 0)
            
            office_role_ftes[office_name] = office_role_fte
            total_role_fte += office_role_fte
        
        # If no FTE exists for this role, return zeros
        if total_role_fte == 0:
            return {office_name: 0.0 for office_name in config.keys()}
        
        # Calculate proportional values and quotas based on total role FTE
        office_quotas = {}
        office_remainders = {}
        total_distributed = 0
        
        for office_name, office_role_fte in office_role_ftes.items():
            office_weight = office_role_fte / total_role_fte if total_role_fte > 0 else 0
            
            proportional_value = total_value * office_weight
            quota = round(proportional_value)
            remainder = proportional_value - quota
            
            office_quotas[office_name] = quota
            office_remainders[office_name] = remainder
            total_distributed += quota
        
        # Distribute the remaining FTE using largest remainder method
        # Handle fractional values properly by working with the actual remainder
        remaining_fte = total_value - total_distributed
        
        # Sort offices by remainder in descending order (only include offices with non-zero FTE)
        sorted_offices = sorted(
            [(name, remainder) for name, remainder in office_remainders.items() 
             if office_role_ftes[name] > 0],
            key=lambda x: x[1], reverse=True
        )
        
        # Distribute remaining FTE to offices with largest remainders
        # For fractional values, we need to round to nearest integer distribution
        remaining_fte_int = round(remaining_fte)
        for i in range(remaining_fte_int):
            if i < len(sorted_offices):
                office_name = sorted_offices[i][0]
                office_quotas[office_name] += 1
        
        return {office_name: float(quota) for office_name, quota in office_quotas.items()}
    
    def _map_baseline_to_absolute_values(self, office_config: Dict[str, Any], baseline_input: Dict[str, Any], total_fte_all_offices: float = None, time_range: Dict[str, Any] = None) -> Dict[str, Any]:
        """Map baseline input to absolute recruitment/churn fields and economic data."""
        office_config = copy.deepcopy(office_config)
        office_name = office_config.get('name', 'Unknown')
        
        # Handle both global and offices structures
        global_data = baseline_input.get('global', baseline_input.get('global_data', {}))
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
        # For single office scenarios, use full weight (1.0)
        # For multi-office scenarios, use proportional weight
        if total_fte_all_offices == office_fte:
            office_weight = 1.0
        else:
            office_weight = office_fte / total_fte_all_offices if total_fte_all_offices else 0

        # Determine simulation time range
        if time_range is not None:
            # Handle both dict and Pydantic model
            if hasattr(time_range, 'get'):
                start_year = time_range.get('start_year', 2025)
                start_month = time_range.get('start_month', 1)
                end_year = time_range.get('end_year', 2025)
                end_month = time_range.get('end_month', 12)
            else:
                # Pydantic model
                start_year = getattr(time_range, 'start_year', 2025)
                start_month = getattr(time_range, 'start_month', 1)
                end_year = getattr(time_range, 'end_year', 2025)
                end_month = getattr(time_range, 'end_month', 12)
        else:
            start_year, start_month, end_year, end_month = 2025, 1, 2025, 12

        # Store original FTE values to ensure they're preserved
        original_fte_values = {}
        for role_name, role_data in office_config.get('roles', {}).items():
            if isinstance(role_data, dict):
                for level_name, level_config in role_data.items():
                    if isinstance(level_config, dict) and 'fte' in level_config:
                        original_fte_values[f"{role_name}.{level_name}"] = level_config['fte']

        # Apply exact distribution to preserve total FTE
        for role_name, role_data in office_config.get('roles', {}).items():
            if isinstance(role_data, dict):
                for level_name, level_config in role_data.items():
                    if isinstance(level_config, dict):
                        # Ensure baseline FTE is preserved
                        level_key = f"{role_name}.{level_name}"
                        if level_key in original_fte_values:
                            level_config['fte'] = original_fte_values[level_key]

                        # Map recruitment data with exact distribution (unified nested structure)
                        if 'recruitment' in global_data and role_name in global_data['recruitment']:
                            role_recruitment_data = global_data['recruitment'][role_name]
                            # Handle nested structure: role -> levels -> levelName -> recruitment -> values
                            if 'levels' in role_recruitment_data and level_name in role_recruitment_data['levels']:
                                level_data = role_recruitment_data['levels'][level_name]
                                if 'recruitment' in level_data and 'values' in level_data['recruitment']:
                                    level_recruitment_values = level_data['recruitment']['values']
                                    # Loop over all years and months in the simulation time range
                                    for year in range(start_year, end_year + 1):
                                        for month in range(1, 13):
                                            # Only include months within the simulation window
                                            if (year == start_year and month < start_month) or (year == end_year and month > end_month):
                                                continue
                                            month_key = f"{year}{month:02d}"
                                            global_value = level_recruitment_values.get(month_key, 0.0)
                                            distributed_value = global_value * office_weight
                                            # Only set absolute field, not percentage
                                            abs_field_name = f'recruitment_abs_{month}'
                                            level_config[abs_field_name] = distributed_value

                        # Map churn data with exact distribution (unified nested structure)
                        if 'churn' in global_data and role_name in global_data['churn']:
                            role_churn_data = global_data['churn'][role_name]
                            # Handle nested structure: role -> levels -> levelName -> churn -> values
                            if 'levels' in role_churn_data and level_name in role_churn_data['levels']:
                                level_data = role_churn_data['levels'][level_name]
                                if 'churn' in level_data and 'values' in level_data['churn']:
                                    level_churn_values = level_data['churn']['values']
                                    for year in range(start_year, end_year + 1):
                                        for month in range(1, 13):
                                            if (year == start_year and month < start_month) or (year == end_year and month > end_month):
                                                continue
                                            month_key = f"{year}{month:02d}"
                                            global_value = level_churn_values.get(month_key, 0.0)
                                            distributed_value = global_value * office_weight
                                            # Only set absolute field, not percentage
                                            abs_field_name = f'churn_abs_{month}'
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
                        
                        # Apply recruitment data (absolute values only)
                        for rec_key, rec_value in level_data.items():
                            if isinstance(rec_key, str) and rec_key.startswith('recruitment_abs_'):
                                try:
                                    month_num = int(rec_key.split('_')[-1])
                                    if start_year == end_year and (month_num < start_month or month_num > end_month):
                                        continue
                                    office_level[rec_key] = rec_value
                                    # Do NOT set percentage version - only use absolute
                                except (ValueError, IndexError):
                                    continue
                        
                        # Apply churn data (absolute values only)
                        for churn_key, churn_value in level_data.items():
                            if isinstance(churn_key, str) and churn_key.startswith('churn_abs_'):
                                try:
                                    month_num = int(churn_key.split('_')[-1])
                                    if start_year == end_year and (month_num < start_month or month_num > end_month):
                                        continue
                                    office_level[churn_key] = churn_value
                                    # Do NOT set percentage version - only use absolute
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
                        
                        # Apply recruitment and churn data (absolute values only)
                        for key, value in role_data.items():
                            if isinstance(key, str) and key.startswith('recruitment_abs_'):
                                try:
                                    month_num = int(key.split('_')[-1])
                                    if start_year == end_year and (month_num < start_month or month_num > end_month):
                                        continue
                                    office_role[key] = value
                                    # Do NOT set percentage version - only use absolute
                                except (ValueError, IndexError):
                                    continue
                            
                            elif isinstance(key, str) and key.startswith('churn_abs_'):
                                try:
                                    month_num = int(key.split('_')[-1])
                                    if start_year == end_year and (month_num < start_month or month_num > end_month):
                                        continue
                                    office_role[key] = value
                                    # Do NOT set percentage version - only use absolute
                                except (ValueError, IndexError):
                                    continue
        
        return office_config
    
    def _filter_offices_by_scope(self, base_config: Dict[str, Any], office_scope: list) -> Dict[str, Any]:
        """
        Filter offices based on office_scope parameter.
        If office_scope is empty or None, return all offices.
        If office_scope contains 'Group', return all offices.
        If office_scope contains specific offices, return only those offices.
        """
        if not office_scope:
            # No office scope specified, return all offices
            return base_config
        
        # Check if 'Group' is in scope (meaning all offices)
        if 'Group' in office_scope:
            logger.info(f"Office scope contains 'Group', returning all offices: {list(base_config.keys())}")
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
        
        # Handle both direct levers (from frontend) and global levers (legacy)
        # Frontend sends: { recruitment: {A: 1.2}, churn: {A: 0.9} }
        # Legacy format: { global: { recruitment: {A: 1.2}, churn: {A: 0.9} } }
        direct_levers = levers
        global_levers = levers.get('global', {})
        
        # Use direct levers if available, otherwise fall back to global
        effective_levers = direct_levers if any(k in direct_levers for k in ['recruitment', 'churn', 'progression', 'price', 'salary']) else global_levers
        
        if not effective_levers:
            return office_config
        
        # Apply levers to all offices
        for role_name, role_config in office_config.get('roles', {}).items():
            if not isinstance(role_config, dict):
                continue
                
            for level_name, level_config in role_config.items():
                if not isinstance(level_config, dict):
                    continue
                
                # Apply price levers
                if 'price' in effective_levers and level_name in effective_levers['price']:
                    price_value = effective_levers['price'][level_name]
                    for month in range(1, 13):
                        level_config[f'price_{month}'] = price_value
                
                # Apply salary levers
                if 'salary' in effective_levers and level_name in effective_levers['salary']:
                    salary_value = effective_levers['salary'][level_name]
                    for month in range(1, 13):
                        level_config[f'salary_{month}'] = salary_value
                
                # Apply recruitment levers (absolute values only)
                if 'recruitment' in effective_levers and level_name in effective_levers['recruitment']:
                    recruitment_multiplier = effective_levers['recruitment'][level_name]
                    for month in range(1, 13):
                        # Only multiply absolute recruitment values, not percentage
                        if f'recruitment_abs_{month}' in level_config:
                            level_config[f'recruitment_abs_{month}'] *= recruitment_multiplier
                
                # Apply churn levers (absolute values only)
                if 'churn' in effective_levers and level_name in effective_levers['churn']:
                    churn_multiplier = effective_levers['churn'][level_name]
                    for month in range(1, 13):
                        # Only multiply absolute churn values, not percentage
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
        
        # Fallback to default curves - transform flat structure to nested structure
        logger.info("[DEBUG] Using default CAT curves")
        return self._transform_flat_cat_curves_to_nested(CAT_CURVES)
    
    def _transform_flat_cat_curves_to_nested(self, flat_cat_curves: Dict[str, Any]) -> Dict[str, Any]:
        """Transform flat CAT curves structure to nested structure expected by unified data models."""
        nested_curves = {}
        
        for level_name, level_curves in flat_cat_curves.items():
            # Each level should have a 'curves' key containing the CAT probabilities
            nested_curves[level_name] = {
                'curves': level_curves
            }
        
        return {
            'curves': nested_curves
        }
    
    def _adjust_cat_curves_by_levers(self, cat_curves: Dict[str, Any], levers: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust CAT curves by progression levers."""
        progression_levers = levers.get('progression', {})
        
        if not progression_levers:
            return cat_curves
        
        # Create a copy to avoid modifying the original
        adjusted_curves = copy.deepcopy(cat_curves)
        
        # Handle both flat and nested CAT curves structures
        if 'curves' in adjusted_curves:
            # Nested structure - loop through curves.level_name.curves
            curves_data = adjusted_curves['curves']
            for level_name, level_data in curves_data.items():
                if 'curves' in level_data:
                    level_curves = level_data['curves']
                    self._apply_progression_multipliers_to_level_curves(level_curves, progression_levers)
        else:
            # Flat structure - level_name directly contains curves
            for level_name, level_curves in adjusted_curves.items():
                if isinstance(level_curves, dict):
                    self._apply_progression_multipliers_to_level_curves(level_curves, progression_levers)
        
        return adjusted_curves
    
    def _apply_progression_multipliers_to_level_curves(self, level_curves: Dict[str, Any], progression_levers: Dict[str, Any]) -> None:
        """Apply progression multipliers to level curves."""
        # Apply global multiplier if specified
        if 'multiplier' in progression_levers:
            multiplier = progression_levers['multiplier']
            for cat_category in level_curves:
                if isinstance(level_curves[cat_category], (int, float)):
                    level_curves[cat_category] = min(level_curves[cat_category] * multiplier, 1.0)
        
        # Apply individual level multipliers if specified
        for level_name, level_multiplier in progression_levers.items():
            if level_name != 'multiplier' and isinstance(level_multiplier, (int, float)):
                # This would be used for level-specific multipliers in the future
                pass

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
        
        # Fallback to default curves - transform flat structure to nested structure
        logger.info("[DEBUG] Using default CAT curves")
        return self._transform_flat_cat_curves_to_nested(CAT_CURVES)

    def _adjust_cat_curves_by_levers_with_models(self, cat_curves: Dict[str, Any], levers: Union[Dict[str, Any], Levers]) -> Dict[str, Any]:
        """Adjust CAT curves by progression levers using Pydantic models for type safety."""
        # Convert Pydantic model to dict if needed
        if hasattr(levers, 'model_dump'):
            levers = levers.model_dump()
        
        return self._adjust_cat_curves_by_levers(cat_curves, levers)
    
    def _fetch_baseline_from_business_plan(self, business_plan_id: str, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch baseline data from business plan storage."""
        try:
            from .business_plan_storage import business_plan_storage
            
            # Extract office scope and time range from scenario
            office_scope = scenario_data.get('office_scope', [])
            time_range = scenario_data.get('time_range', {})
            
            # Get time range details
            if hasattr(time_range, 'get'):
                start_year = time_range.get('start_year', 2025)
                start_month = time_range.get('start_month', 1)
                end_year = time_range.get('end_year', 2025)
                end_month = time_range.get('end_month', 12)
            else:
                # Pydantic model
                start_year = time_range.start_year
                start_month = time_range.start_month
                end_year = time_range.end_year
                end_month = time_range.end_month
            
            # For now, use the first year of the time range for business plan
            # In future, could aggregate across multiple years
            year = start_year
            
            # If multiple offices, get aggregated plan
            if len(office_scope) > 1 or 'Group' in office_scope:
                baseline = business_plan_storage.export_aggregated_as_simulation_baseline(
                    year=year,
                    office_ids=None if 'Group' in office_scope else office_scope,
                    start_month=start_month,
                    end_month=min(end_month, 12) if year == start_year else 12
                )
            else:
                # Single office
                office_id = office_scope[0] if office_scope else 'Stockholm'
                baseline = business_plan_storage.export_as_simulation_baseline(
                    office_id=office_id,
                    year=year,
                    start_month=start_month,
                    end_month=min(end_month, 12) if year == start_year else 12
                )
            
            logger.info(f"[DEBUG] Successfully fetched baseline from business plan {business_plan_id}")
            return baseline
            
        except Exception as e:
            logger.error(f"[DEBUG] Failed to fetch baseline from business plan: {e}")
            return {}
    
    def _generate_default_baseline(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a default baseline with reasonable values for all offices."""
        time_range = scenario_data.get('time_range', {})
        
        # Get time range details
        if hasattr(time_range, 'get'):
            start_year = time_range.get('start_year', 2025)
            start_month = time_range.get('start_month', 1)
        else:
            # Pydantic model
            start_year = time_range.start_year if hasattr(time_range, 'start_year') else 2025
            start_month = time_range.start_month if hasattr(time_range, 'start_month') else 1
        
        # Create a default baseline with typical values
        month_str = f"{start_year}{start_month:02d}"
        
        default_baseline = {
            "global": {
                "recruitment": {
                    "Consultant": {
                        "levels": {
                            "A": {"recruitment": {"values": {month_str: 10.0}}, "churn": {"values": {month_str: 2.0}}},
                            "AC": {"recruitment": {"values": {month_str: 5.0}}, "churn": {"values": {month_str: 3.0}}},
                            "C": {"recruitment": {"values": {month_str: 3.0}}, "churn": {"values": {month_str: 4.0}}},
                            "SrC": {"recruitment": {"values": {month_str: 1.0}}, "churn": {"values": {month_str: 3.0}}},
                            "AM": {"recruitment": {"values": {month_str: 1.0}}, "churn": {"values": {month_str: 2.0}}},
                            "M": {"recruitment": {"values": {month_str: 0.5}}, "churn": {"values": {month_str: 1.0}}},
                            "SrM": {"recruitment": {"values": {month_str: 0.2}}, "churn": {"values": {month_str: 0.5}}},
                            "Pi": {"recruitment": {"values": {month_str: 0.1}}, "churn": {"values": {month_str: 0.2}}},
                            "P": {"recruitment": {"values": {month_str: 0.1}}, "churn": {"values": {month_str: 0.1}}}
                        }
                    }
                },
                "churn": {
                    "Consultant": {
                        "levels": {
                            "A": {"recruitment": {"values": {month_str: 10.0}}, "churn": {"values": {month_str: 2.0}}},
                            "AC": {"recruitment": {"values": {month_str: 5.0}}, "churn": {"values": {month_str: 3.0}}},
                            "C": {"recruitment": {"values": {month_str: 3.0}}, "churn": {"values": {month_str: 4.0}}},
                            "SrC": {"recruitment": {"values": {month_str: 1.0}}, "churn": {"values": {month_str: 3.0}}},
                            "AM": {"recruitment": {"values": {month_str: 1.0}}, "churn": {"values": {month_str: 2.0}}},
                            "M": {"recruitment": {"values": {month_str: 0.5}}, "churn": {"values": {month_str: 1.0}}},
                            "SrM": {"recruitment": {"values": {month_str: 0.2}}, "churn": {"values": {month_str: 0.5}}},
                            "Pi": {"recruitment": {"values": {month_str: 0.1}}, "churn": {"values": {month_str: 0.2}}},
                            "P": {"recruitment": {"values": {month_str: 0.1}}, "churn": {"values": {month_str: 0.1}}}
                        }
                    }
                }
            }
        }
        
        logger.info("[DEBUG] Generated default baseline with reasonable values")
        return default_baseline 