"""
Scenario Validator - Validates scenario data structure and content.

This service has a single responsibility: validate the structure and completeness
of scenario data from the frontend, providing clear error messages.
"""
import logging
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

class ScenarioValidator:
    """
    Validates scenario data structure and content.
    Focused solely on input validation and error reporting.
    """
    
    def __init__(self):
        pass
    
    def validate_scenario_data(self, scenario_data: Union[Dict[str, Any], BaseModel]) -> None:
        """
        Validate the structure and completeness of the scenario data.
        Raises a ValueError with descriptive message if invalid.
        """
        # Handle Pydantic models
        if isinstance(scenario_data, BaseModel):
            try:
                # Validate the model
                scenario_data.model_validate(scenario_data.model_dump())
                return
            except ValidationError as e:
                raise ValueError(f"Scenario data validation failed: {e}")
        
        # Handle dictionaries (existing logic)
        if not isinstance(scenario_data, dict):
            raise ValueError("Scenario data must be a dictionary or Pydantic model")
        
        # Allow empty scenario data (no validation required)
        if not scenario_data:
            return
        
        # Validate baseline_input structure if present
        if 'baseline_input' in scenario_data:
            baseline = scenario_data.get('baseline_input', {})
            # Handle Pydantic models
            if hasattr(baseline, 'model_dump'):
                baseline = baseline.model_dump()
            elif not isinstance(baseline, dict):
                raise ValueError("baseline_input must be a dictionary or Pydantic model")
            self._validate_baseline_input(baseline)
        
        # Validate levers structure if present
        if 'levers' in scenario_data:
            levers = scenario_data.get('levers', {})
            # Handle Pydantic models
            if hasattr(levers, 'model_dump'):
                levers = levers.model_dump()
            elif not isinstance(levers, dict):
                raise ValueError("levers must be a dictionary or Pydantic model")
            self._validate_levers(levers)
        
        # Validate progression_config if present
        if 'progression_config' in scenario_data:
            progression_config = scenario_data.get('progression_config')
            if progression_config is not None:
                self._validate_progression_config(progression_config)
        
        # Validate cat_curves if present
        if 'cat_curves' in scenario_data:
            cat_curves = scenario_data.get('cat_curves')
            if cat_curves is not None:
                self._validate_cat_curves(cat_curves)
    
    def validate_scenario_definition(self, scenario_def: Union[Dict[str, Any], BaseModel]) -> None:
        """
        Validate a complete scenario definition including all required fields.
        Raises a ValueError with descriptive message if invalid.
        """
        # Handle Pydantic models
        if isinstance(scenario_def, BaseModel):
            try:
                # Validate the model
                scenario_def.model_validate(scenario_def.model_dump())
                return
            except ValidationError as e:
                raise ValueError(f"Scenario definition validation failed: {e}")
        
        # Handle dictionaries (existing logic)
        if not isinstance(scenario_def, dict):
            raise ValueError("Scenario definition must be a dictionary or Pydantic model")
        
        # Validate required fields
        required_fields = ['name', 'description', 'time_range', 'office_scope']
        for field in required_fields:
            if field not in scenario_def:
                raise ValueError(f"Scenario definition must contain {field}")
        
        # Validate name
        name = scenario_def.get('name')
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Scenario name must be a non-empty string")
        
        # Validate description
        description = scenario_def.get('description')
        if not isinstance(description, str):
            raise ValueError("Scenario description must be a string")
        
        # Validate time range
        time_range = scenario_def.get('time_range')
        if time_range:
            self.validate_time_range(time_range)
        
        # Validate office scope
        office_scope = scenario_def.get('office_scope')
        if office_scope:
            self.validate_office_scope(office_scope)
        
        # Validate optional fields
        if 'levers' in scenario_def:
            levers = scenario_def.get('levers')
            if levers is not None:
                self._validate_levers(levers)
        
        if 'economic_params' in scenario_def:
            economic_params = scenario_def.get('economic_params')
            if economic_params is not None:
                self._validate_economic_params(economic_params)
        
        if 'progression_config' in scenario_def:
            progression_config = scenario_def.get('progression_config')
            if progression_config is not None:
                self._validate_progression_config(progression_config)
        
        if 'cat_curves' in scenario_def:
            cat_curves = scenario_def.get('cat_curves')
            if cat_curves is not None:
                self._validate_cat_curves(cat_curves)
    
    def validate_pydantic_model(self, model_instance: BaseModel, model_class: type) -> None:
        """
        Validate a Pydantic model instance against its class definition.
        Raises a ValueError with descriptive message if invalid.
        """
        if not isinstance(model_instance, model_class):
            raise ValueError(f"Model instance must be of type {model_class.__name__}")
        
        try:
            # Validate the model
            model_class.model_validate(model_instance.model_dump())
        except ValidationError as e:
            raise ValueError(f"Model validation failed: {e}")
    
    def _validate_baseline_input(self, baseline: Dict[str, Any]) -> None:
        """Validate baseline_input structure and content."""
        # Check for global baseline
        if 'global' in baseline:
            global_baseline = baseline['global']
            if not isinstance(global_baseline, dict):
                raise ValueError("baseline_input.global must be a dictionary")
            
            # Validate global recruitment and churn
            for metric in ['recruitment', 'churn']:
                if metric in global_baseline:
                    metric_data = global_baseline[metric]
                    if not isinstance(metric_data, dict):
                        raise ValueError(f"baseline_input.global.{metric} must be a dictionary")
                    
                    # Check for role-specific data
                    for role_name, role_data in metric_data.items():
                        if not isinstance(role_data, dict):
                            raise ValueError(f"baseline_input.global.{metric}.{role_name} must be a dictionary")
                        
                        # Check for monthly data
                        for month_key, month_data in role_data.items():
                            if not isinstance(month_data, dict):
                                raise ValueError(f"baseline_input.global.{metric}.{role_name}.{month_key} must be a dictionary")
                            
                            # Check for level-specific values
                            for level_name, value in month_data.items():
                                if not isinstance(value, (int, float)):
                                    raise ValueError(f"Invalid {metric} value for {role_name}.{level_name} in {month_key}")
        
        # Check for office-specific baseline
        if 'offices' in baseline:
            office_baseline = baseline['offices']
            if not isinstance(office_baseline, dict):
                raise ValueError("baseline_input.offices must be a dictionary")
            
            for office_name, office_data in office_baseline.items():
                if not isinstance(office_data, dict):
                    raise ValueError(f"baseline_input.offices.{office_name} must be a dictionary")
                
                # Validate office recruitment and churn
                for metric in ['recruitment', 'churn']:
                    if metric in office_data:
                        metric_data = office_data[metric]
                        if not isinstance(metric_data, dict):
                            raise ValueError(f"baseline_input.offices.{office_name}.{metric} must be a dictionary")
                        
                        # Check for role-specific data
                        for role_name, role_data in metric_data.items():
                            if not isinstance(role_data, dict):
                                raise ValueError(f"baseline_input.offices.{office_name}.{metric}.{role_name} must be a dictionary")
                            
                            # Check for monthly data
                            for month_key, month_data in role_data.items():
                                if not isinstance(month_data, dict):
                                    raise ValueError(f"baseline_input.offices.{office_name}.{metric}.{role_name}.{month_key} must be a dictionary")
                                
                                # Check for level-specific values
                                for level_name, value in month_data.items():
                                    if not isinstance(value, (int, float)):
                                        raise ValueError(f"Invalid {metric} value for {office_name}.{role_name}.{level_name} in {month_key}")

    def _validate_levers(self, levers: Dict[str, Any]) -> None:
        """Validate levers structure and content."""
        # Check for global levers
        if 'global' in levers:
            global_levers = levers['global']
            if not isinstance(global_levers, dict):
                raise ValueError("levers.global must be a dictionary")
            
            # Validate lever types
            for lever_type, lever_data in global_levers.items():
                if lever_type not in ['recruitment', 'churn', 'progression', 'price', 'salary', 'utr']:
                    raise ValueError(f"Unknown lever type: {lever_type}")
                
                if not isinstance(lever_data, dict):
                    raise ValueError(f"levers.global.{lever_type} must be a dictionary")
                
                # Check for level-specific values
                for level_name, value in lever_data.items():
                    if not isinstance(value, (int, float)):
                        raise ValueError(f"Invalid {lever_type} lever value for level {level_name}")
        
        # Check for office-specific levers
        if 'offices' in levers:
            office_levers = levers['offices']
            if not isinstance(office_levers, dict):
                raise ValueError("levers.offices must be a dictionary")
            
            for office_name, office_data in office_levers.items():
                if not isinstance(office_data, dict):
                    raise ValueError(f"levers.offices.{office_name} must be a dictionary")
                
                # Validate lever types
                for lever_type, lever_data in office_data.items():
                    if lever_type not in ['recruitment', 'churn', 'progression', 'price', 'salary', 'utr']:
                        raise ValueError(f"Unknown lever type: {lever_type}")
                    
                    if not isinstance(lever_data, dict):
                        raise ValueError(f"levers.offices.{office_name}.{lever_type} must be a dictionary")
                    
                    # Check for level-specific values
                    for level_name, value in lever_data.items():
                        if not isinstance(value, (int, float)):
                            raise ValueError(f"Invalid {lever_type} lever value for {office_name}.{level_name}")
    
    def _validate_economic_params(self, economic_params: Dict[str, Any]) -> None:
        """Validate economic parameters structure and content."""
        # Convert Pydantic model to dict if needed
        if hasattr(economic_params, 'model_dump'):
            economic_params = economic_params.model_dump()
        
        if not isinstance(economic_params, dict):
            raise ValueError("economic_params must be a dictionary")
        
        # Define valid economic parameter keys and their expected types
        valid_params = {
            'unplanned_absence': (int, float),
            'other_expense': (int, float),
            'employment_cost_rate': (int, float),
            'working_hours_per_month': (int, float),
            'utilization': (int, float),
            'price_increase': (int, float),
            'salary_increase': (int, float)
        }
        
        # Validate each parameter
        for param_name, param_value in economic_params.items():
            if param_name not in valid_params:
                raise ValueError(f"Unknown economic parameter: {param_name}")
            
            expected_type = valid_params[param_name]
            if not isinstance(param_value, expected_type):
                raise ValueError(f"economic_params.{param_name} must be a {expected_type.__name__}")
            
            # Validate ranges for specific parameters
            if param_name == 'unplanned_absence' and not (0 <= param_value <= 1):
                raise ValueError("unplanned_absence must be between 0 and 1")
            elif param_name == 'employment_cost_rate' and not (0 <= param_value <= 1):
                raise ValueError("employment_cost_rate must be between 0 and 1")
            elif param_name == 'utilization' and not (0 <= param_value <= 1):
                raise ValueError("utilization must be between 0 and 1")
            elif param_name == 'working_hours_per_month' and param_value <= 0:
                raise ValueError("working_hours_per_month must be positive")
            elif param_name in ['price_increase', 'salary_increase'] and param_value < 0:
                raise ValueError(f"{param_name} must be non-negative")
    
    def _validate_progression_config(self, progression_config: Dict[str, Any]) -> None:
        """Validate progression configuration structure and content."""
        if not isinstance(progression_config, dict):
            raise ValueError("progression_config must be a dictionary")
        
        # Handle nested structure (progression_config.levels)
        if 'levels' in progression_config:
            levels_config = progression_config['levels']
            if not isinstance(levels_config, dict):
                raise ValueError("progression_config.levels must be a dictionary")
            
            # Validate each level configuration
            for level_name, level_config in levels_config.items():
                if not isinstance(level_name, str):
                    raise ValueError("Level names in progression_config.levels must be strings")
                
                if not isinstance(level_config, dict):
                    raise ValueError(f"progression_config.levels.{level_name} must be a dictionary")
                
                # Validate required fields for each level
                required_fields = ['progression_months', 'time_on_level']
                for field in required_fields:
                    if field not in level_config:
                        raise ValueError(f"progression_config.levels.{level_name} must contain {field}")
                
                # Validate progression_months
                progression_months = level_config.get('progression_months')
                if not isinstance(progression_months, list):
                    raise ValueError(f"progression_config.levels.{level_name}.progression_months must be a list")
                
                for month in progression_months:
                    if not isinstance(month, int) or not (1 <= month <= 12):
                        raise ValueError(f"progression_config.levels.{level_name}.progression_months must contain integers between 1 and 12")
                
                # Validate time_on_level
                time_on_level = level_config.get('time_on_level')
                if not isinstance(time_on_level, int) or time_on_level < 0:
                    raise ValueError(f"progression_config.levels.{level_name}.time_on_level must be a non-negative integer")
                
                # Validate optional fields
                if 'start_tenure' in level_config:
                    start_tenure = level_config.get('start_tenure')
                    if not isinstance(start_tenure, int) or start_tenure < 1:
                        raise ValueError(f"progression_config.levels.{level_name}.start_tenure must be a positive integer")
                
                if 'next_level' in level_config:
                    next_level = level_config.get('next_level')
                    if next_level is not None and not isinstance(next_level, str):
                        raise ValueError(f"progression_config.levels.{level_name}.next_level must be a string or null")
                
                if 'journey' in level_config:
                    journey = level_config.get('journey')
                    if journey is not None and not isinstance(journey, str):
                        raise ValueError(f"progression_config.levels.{level_name}.journey must be a string")
        
        else:
            # Handle flat structure (legacy)
            for level_name, level_config in progression_config.items():
                if not isinstance(level_name, str):
                    raise ValueError("Level names in progression_config must be strings")
                
                if not isinstance(level_config, dict):
                    raise ValueError(f"progression_config.{level_name} must be a dictionary")
                
                # Validate required fields for each level
                required_fields = ['progression_months', 'time_on_level']
                for field in required_fields:
                    if field not in level_config:
                        raise ValueError(f"progression_config.{level_name} must contain {field}")
                
                # Validate progression_months
                progression_months = level_config.get('progression_months')
                if not isinstance(progression_months, list):
                    raise ValueError(f"progression_config.{level_name}.progression_months must be a list")
                
                for month in progression_months:
                    if not isinstance(month, int) or not (1 <= month <= 12):
                        raise ValueError(f"progression_config.{level_name}.progression_months must contain integers between 1 and 12")
                
                # Validate time_on_level
                time_on_level = level_config.get('time_on_level')
                if not isinstance(time_on_level, int) or time_on_level < 0:
                    raise ValueError(f"progression_config.{level_name}.time_on_level must be a non-negative integer")
                
                # Validate optional progression_rate (if provided)
                if 'progression_rate' in level_config:
                    progression_rate = level_config.get('progression_rate')
                    if not isinstance(progression_rate, (int, float)) or not (0 <= progression_rate <= 1):
                        raise ValueError(f"progression_config.{level_name}.progression_rate must be a number between 0 and 1")
                
                # Validate optional journey field
                if 'journey' in level_config:
                    journey = level_config.get('journey')
                    if journey is not None and not isinstance(journey, str):
                        raise ValueError(f"progression_config.{level_name}.journey must be a string")
    
    def _validate_cat_curves(self, cat_curves: Dict[str, Any]) -> None:
        """Validate CAT curves structure and content."""
        if not isinstance(cat_curves, dict):
            raise ValueError("cat_curves must be a dictionary")
        
        # Handle nested structure (cat_curves.curves)
        if 'curves' in cat_curves:
            curves_config = cat_curves['curves']
            if not isinstance(curves_config, dict):
                raise ValueError("cat_curves.curves must be a dictionary")
            
            # Validate each level's CAT curve
            for level_name, level_curves in curves_config.items():
                if not isinstance(level_name, str):
                    raise ValueError("Level names in cat_curves.curves must be strings")
                
                if not isinstance(level_curves, dict):
                    raise ValueError(f"cat_curves.curves.{level_name} must be a dictionary")
                
                # Handle nested curves structure (level_curves.curves)
                if 'curves' in level_curves:
                    cat_probabilities = level_curves['curves']
                    if not isinstance(cat_probabilities, dict):
                        raise ValueError(f"cat_curves.curves.{level_name}.curves must be a dictionary")
                    
                    # Validate each CAT category probability
                    for cat_category, probability in cat_probabilities.items():
                        if not isinstance(cat_category, str):
                            raise ValueError(f"CAT categories in cat_curves.curves.{level_name}.curves must be strings")
                        
                        if not isinstance(probability, (int, float)) or not (0 <= probability <= 1):
                            raise ValueError(f"CAT probability for {level_name}.{cat_category} must be a number between 0 and 1")
                else:
                    # Handle flat structure within level
                    for cat_category, probability in level_curves.items():
                        if not isinstance(cat_category, str):
                            raise ValueError(f"CAT categories in cat_curves.curves.{level_name} must be strings")
                        
                        if not isinstance(probability, (int, float)) or not (0 <= probability <= 1):
                            raise ValueError(f"CAT probability for {level_name}.{cat_category} must be a number between 0 and 1")
        
        else:
            # Handle flat structure (legacy)
            for level_name, level_curves in cat_curves.items():
                if not isinstance(level_name, str):
                    raise ValueError("Level names in cat_curves must be strings")
                
                if not isinstance(level_curves, dict):
                    raise ValueError(f"cat_curves.{level_name} must be a dictionary")
                
                # Validate each CAT category probability
                for cat_category, probability in level_curves.items():
                    if not isinstance(cat_category, str):
                        raise ValueError(f"CAT categories in cat_curves.{level_name} must be strings")
                    
                    if not isinstance(probability, (int, float)) or not (0 <= probability <= 1):
                        raise ValueError(f"CAT probability for {level_name}.{cat_category} must be a number between 0 and 1")
    
    def validate_time_range(self, time_range: Dict[str, Any]) -> None:
        """Validate time range structure and values."""
        # Convert Pydantic model to dict if needed
        if hasattr(time_range, 'model_dump'):
            time_range = time_range.model_dump()
        
        if not isinstance(time_range, dict):
            raise ValueError("time_range must be a dictionary")
        
        required_fields = ['start_year', 'start_month', 'end_year', 'end_month']
        for field in required_fields:
            if field not in time_range:
                raise ValueError(f"time_range must contain {field}")
            
            value = time_range[field]
            if not isinstance(value, int):
                raise ValueError(f"time_range.{field} must be an integer")
        
        # Validate month ranges
        if not (1 <= time_range['start_month'] <= 12):
            raise ValueError("start_month must be between 1 and 12")
        if not (1 <= time_range['end_month'] <= 12):
            raise ValueError("end_month must be between 1 and 12")
        
        # Validate year ranges
        if time_range['start_year'] < 2020 or time_range['start_year'] > 2030:
            raise ValueError("start_year must be between 2020 and 2030")
        if time_range['end_year'] < 2020 or time_range['end_year'] > 2030:
            raise ValueError("end_year must be between 2020 and 2030")
        
        # Validate that end is after start
        start_date = time_range['start_year'] * 12 + time_range['start_month']
        end_date = time_range['end_year'] * 12 + time_range['end_month']
        if end_date <= start_date:
            raise ValueError("End date must be after start date")
    
    def validate_office_scope(self, office_scope: list) -> None:
        """Validate office scope list."""
        if not isinstance(office_scope, list):
            raise ValueError("office_scope must be a list")
        
        for office in office_scope:
            if not isinstance(office, str):
                raise ValueError("All office names in office_scope must be strings")
            if not office.strip():
                raise ValueError("Office names cannot be empty") 