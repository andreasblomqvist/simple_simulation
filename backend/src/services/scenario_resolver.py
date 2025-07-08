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
from typing import Dict, Any, Optional

from .config_service import config_service
from config.progression_config import PROGRESSION_CONFIG, CAT_CURVES

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
        
        # Apply baseline input (absolute recruitment/churn values)
        config_with_baseline = self._apply_baseline_input(base_config, scenario_data)
        
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
    
    def _apply_baseline_input(self, base_config: Dict[str, Any], scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply baseline input to set absolute recruitment/churn values."""
        config = copy.deepcopy(base_config)
        baseline_input = scenario_data.get('baseline_input', {})
        
        if not baseline_input:
            return config
        
        # Apply to all offices
        for office_name in config:
            config[office_name] = self._map_baseline_to_absolute_values(
                config[office_name], baseline_input
            )
        
        return config
    
    def _map_baseline_to_absolute_values(self, office_config: Dict[str, Any], baseline_input: Dict[str, Any]) -> Dict[str, Any]:
        """Map baseline input to absolute recruitment/churn fields."""
        office_config = copy.deepcopy(office_config)
        
        # Get global baseline data
        global_data = baseline_input.get('global', {})
        if not global_data:
            return office_config
        
        # Process each role and level
        for role_name, role_data in office_config.get('roles', {}).items():
            if isinstance(role_data, dict):
                for level_name, level_config in role_data.items():
                    if isinstance(level_config, dict):
                        # Map recruitment data
                        if 'recruitment' in global_data and role_name in global_data['recruitment']:
                            recruitment_data = global_data['recruitment'][role_name]
                            if level_name in recruitment_data:
                                level_recruitment_data = recruitment_data[level_name]
                                for month in range(1, 13):
                                    month_key = f"2025{month:02d}"
                                    value = level_recruitment_data.get(month_key, 0.0)
                                    field_name = f'recruitment_{month}'
                                    abs_field_name = f'recruitment_abs_{month}'
                                    level_config[field_name] = value
                                    level_config[abs_field_name] = value
                        
                        # Map churn data
                        if 'churn' in global_data and role_name in global_data['churn']:
                            churn_data = global_data['churn'][role_name]
                            if level_name in churn_data:
                                level_churn_data = churn_data[level_name]
                                for month in range(1, 13):
                                    month_key = f"2025{month:02d}"
                                    value = level_churn_data.get(month_key, 0.0)
                                    field_name = f'churn_{month}'
                                    abs_field_name = f'churn_abs_{month}'
                                    level_config[field_name] = value
                                    level_config[abs_field_name] = value
        
        return office_config
    
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