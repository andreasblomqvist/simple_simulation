"""
Scenario Service - Thin adapter layer between frontend scenario runner and simulation engine.

This service follows the architectural principle of being a thin adapter that:
- Translates scenario runner payloads into simulation engine lever plan format
- Validates inputs but does not recalculate business logic
- Maintains single source of truth (all calculations in simulation engine)
- Provides scenario persistence and management
"""
import json
import os
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import copy

from .scenario_models import (
    ScenarioDefinition, 
    ScenarioRequest, 
    ScenarioResponse, 
    LeverPlan
)
from .config_service import config_service
from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.kpi import KPIService, EconomicParameters
from backend.config.progression_config import PROGRESSION_CONFIG, CAT_CURVES
from backend.src.services.simulation.office_manager import OfficeManager
from backend.src.services.simulation.models import Office, Level, RoleData, Journey, OfficeJourney, Month
from backend.src.services.scenario_storage import ScenarioStorageService

logger = logging.getLogger(__name__)

class ScenarioService:
    """
    Mid-layer service to resolve scenario data into complete Office objects and progression rules for the simulation engine.
    Handles loading base config, applying scenario baseline/levers, and providing all data needed for a pure simulation run.
    """
    def __init__(self, config_service):
        """Initialize with a config service dependency."""
        self.config_service = config_service
        self.storage_service = ScenarioStorageService('data/scenarios')

    def resolve_scenario(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point: resolves scenario data into offices, progression config, and CAT curves.
        Returns a dict with keys: 'offices', 'progression_config', 'cat_curves'.
        """
        self.validate_scenario_data(scenario_data)
        base_config = self.config_service.get_config()
        config_with_baseline = self.apply_scenario_baseline(base_config, scenario_data)
        config_with_levers = self.apply_scenario_levers(config_with_baseline, scenario_data.get('levers', {}))
        progression_config = self.load_progression_config()
        cat_curves = self.load_cat_curves()
        offices = self.create_offices_from_config(config_with_levers, progression_config)
        return {
            'offices': offices,
            'progression_config': progression_config,
            'cat_curves': cat_curves
        }

    def apply_scenario_baseline(self, base_config: Dict[str, Any], scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply scenario baseline input (e.g., recruitment/churn overrides) to the base config.
        Returns a new config dict.
        """
        config = copy.deepcopy(base_config)
        baseline_input = scenario_data.get('baseline_input', {})
        print("DEBUG: baseline_input =", baseline_input)
        if not baseline_input:
            return config
        
        # Apply global baseline overrides
        global_baseline = baseline_input.get('global', {})
        if global_baseline:
            for office_name in config:
                print(f"DEBUG: Calling _apply_baseline_to_office for office '{office_name}' with global_baseline: {global_baseline}")
                config[office_name] = self._apply_baseline_to_office(
                    config[office_name], global_baseline
                )
        
        # Apply office-specific baseline overrides
        office_baseline = baseline_input.get('offices', {})
        for office_name, office_overrides in office_baseline.items():
            if office_name in config:
                config[office_name] = self._apply_baseline_to_office(
                    config[office_name], office_overrides
                )
        
        return config

    def apply_scenario_levers(self, config: Dict[str, Any], levers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply scenario levers (additional overrides) to the config.
        Returns a new config dict.
        """
        if not levers:
            return config
        
        config = copy.deepcopy(config)
        
        # Apply global levers
        global_levers = levers.get('global', {})
        if global_levers:
            for office_name in config:
                config[office_name] = self._apply_levers_to_office(
                    config[office_name], global_levers
                )
        
        # Apply office-specific levers
        office_levers = levers.get('offices', {})
        for office_name, office_overrides in office_levers.items():
            if office_name in config:
                config[office_name] = self._apply_levers_to_office(
                    config[office_name], office_overrides
                )
        
        return config

    def _apply_baseline_to_office(self, office_config: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
        """Apply baseline overrides to a single office config."""
        logger.warning(f"DEBUG: _apply_baseline_to_office called with baseline: {baseline}")
        office_config = copy.deepcopy(office_config)
        
        # Apply recruitment/churn overrides
        recruitment_overrides = baseline.get('recruitment', {})
        churn_overrides = baseline.get('churn', {})
        
        for role_name, role_data in office_config.get('roles', {}).items():
            # Check if this is a leveled role (has nested levels) or flat role
            is_leveled_role = (
                isinstance(role_data, dict) and 
                any(isinstance(value, dict) for value in role_data.values())
            )
            
            if is_leveled_role:  # Leveled roles
                for level_name, level_data in role_data.items():
                    if not isinstance(level_data, dict):
                        continue  # skip if not a dict
                    # Apply recruitment overrides
                    logger.warning(f"DEBUG: Checking level_name='{level_name}' against recruitment_overrides keys: {list(recruitment_overrides.keys())}")
                    if level_name in recruitment_overrides:
                        level_recruitment = recruitment_overrides[level_name]
                        for month in range(1, 13):
                            key = f'recruitment_{month}'
                            if key in level_recruitment:
                                old_val = level_data.get(key, None)
                                level_data[key] = level_recruitment[key]
                                logger.warning(f"Override: {role_name}.{level_name}.{key}: {old_val} -> {level_recruitment[key]}")
                    
                    # Apply churn overrides
                    if level_name in churn_overrides:
                        level_churn = churn_overrides[level_name]
                        for month in range(1, 13):
                            key = f'churn_{month}'
                            if key in level_churn:
                                level_data[key] = level_churn[key]
            else:  # Flat roles (Operations)
                # Apply recruitment overrides
                if role_name in recruitment_overrides:
                    role_recruitment = recruitment_overrides[role_name]
                    for month in range(1, 13):
                        key = f'recruitment_{month}'
                        if key in role_recruitment:
                            role_data[key] = role_recruitment[key]
                
                # Apply churn overrides
                if role_name in churn_overrides:
                    role_churn = churn_overrides[role_name]
                    for month in range(1, 13):
                        key = f'churn_{month}'
                        if key in role_churn:
                            role_data[key] = role_churn[key]
        
        return office_config

    def _apply_levers_to_office(self, office_config: Dict[str, Any], levers: Dict[str, Any]) -> Dict[str, Any]:
        """Apply lever overrides to a single office config."""
        office_config = copy.deepcopy(office_config)
        
        # Apply various lever types
        for lever_type, lever_data in levers.items():
            if lever_type in ['recruitment', 'churn', 'price', 'salary', 'utr']:
                for role_name, role_data in office_config.get('roles', {}).items():
                    if isinstance(role_data, dict):  # Leveled roles
                        for level_name, level_data in role_data.items():
                            if not isinstance(level_data, dict):
                                continue  # skip if not a dict
                            if level_name in lever_data:
                                for month in range(1, 13):
                                    key = f'{lever_type}_{month}'
                                    if key in lever_data[level_name]:
                                        level_data[key] = lever_data[level_name][key]
                    else:  # Flat roles
                        if role_name in lever_data:
                            for month in range(1, 13):
                                key = f'{lever_type}_{month}'
                                if key in lever_data[role_name]:
                                    role_data[key] = lever_data[role_name][key]
        
        return office_config

    def create_offices_from_config(self, config: Dict[str, Any], progression_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert the resolved config dict into Office objects, using the provided progression config.
        Returns a dict of office name to Office object.
        """
        offices = {}
        
        # Create offices using the passed config data
        for office_name, office_config in config.items():
            office = self._create_office_from_config(office_config, progression_config)
            offices[office_name] = office
        
        return offices

    def _create_office_from_config(self, office_config: Dict[str, Any], progression_config: Dict[str, Any]) -> Any:
        """
        Create an Office object from config data using the provided progression config.
        This is a refactored version that doesn't depend on config service.
        """
        from backend.src.services.simulation.models import Office, Level, RoleData, Journey, OfficeJourney
        
        # Create office with journey classification
        office_name = office_config.get('name', 'Unknown Office')
        total_fte = office_config.get('total_fte', 0)
        journey_name = office_config.get('journey', 'New Office')
        
        # Map journey name to enum
        journey_map = {
            'New Office': OfficeJourney.NEW,
            'Emerging Office': OfficeJourney.EMERGING,
            'Mature Office': OfficeJourney.MATURE,
            'Established Office': OfficeJourney.ESTABLISHED
        }
        journey = journey_map.get(journey_name, OfficeJourney.NEW)
        
        # Create office
        office = Office(
            name=office_name,
            total_fte=total_fte,
            journey=journey,
            roles={}
        )
        
        # Create roles and levels
        roles_config = office_config.get('roles', {})
        for role_name, role_data in roles_config.items():
            # Check if this is a leveled role (has nested levels) or flat role
            is_leveled_role = (
                isinstance(role_data, dict) and 
                any(isinstance(value, dict) for value in role_data.values())
            )
            
            if is_leveled_role:  # Leveled roles (Consultant, Sales, Recruitment)
                office.roles[role_name] = {}
                for level_name, level_config in role_data.items():
                    if not isinstance(level_config, dict):
                        logger.warning(f"level_config for {role_name}.{level_name} is not a dict: type={type(level_config)}, value={level_config}")
                        continue  # skip if not a dict
                    # Create level with realistic people
                    level_fte = level_config.get('fte', 0)
                    if level_fte > 0:
                        level = Level(
                            name=level_name,
                            journey=self._get_journey_for_level(level_name),
                            progression_months=[Month(1), Month(4), Month(7), Month(10)],  # Default progression months
                            progression_1=0.0, progression_2=0.0, progression_3=0.0, progression_4=0.0,
                            progression_5=0.0, progression_6=0.0, progression_7=0.0, progression_8=0.0,
                            progression_9=0.0, progression_10=0.0, progression_11=0.0, progression_12=0.0,
                            recruitment_1=0.0, recruitment_2=0.0, recruitment_3=0.0, recruitment_4=0.0,
                            recruitment_5=0.0, recruitment_6=0.0, recruitment_7=0.0, recruitment_8=0.0,
                            recruitment_9=0.0, recruitment_10=0.0, recruitment_11=0.0, recruitment_12=0.0,
                            churn_1=0.0, churn_2=0.0, churn_3=0.0, churn_4=0.0,
                            churn_5=0.0, churn_6=0.0, churn_7=0.0, churn_8=0.0,
                            churn_9=0.0, churn_10=0.0, churn_11=0.0, churn_12=0.0,
                            price_1=0.0, price_2=0.0, price_3=0.0, price_4=0.0,
                            price_5=0.0, price_6=0.0, price_7=0.0, price_8=0.0,
                            price_9=0.0, price_10=0.0, price_11=0.0, price_12=0.0,
                            salary_1=0.0, salary_2=0.0, salary_3=0.0, salary_4=0.0,
                            salary_5=0.0, salary_6=0.0, salary_7=0.0, salary_8=0.0,
                            salary_9=0.0, salary_10=0.0, salary_11=0.0, salary_12=0.0,
                            utr_1=1.0, utr_2=1.0, utr_3=1.0, utr_4=1.0,
                            utr_5=1.0, utr_6=1.0, utr_7=1.0, utr_8=1.0,
                            utr_9=1.0, utr_10=1.0, utr_11=1.0, utr_12=1.0
                        )
                        level.fte = level_fte
                        # Set level attributes from config
                        for key, value in level_config.items():
                            if hasattr(level, key):
                                setattr(level, key, value)
                        # Realistic initialization for leveled roles
                        self._initialize_realistic_people(level, int(level_fte), role_name, office_name, "2025-01")
                        office.roles[role_name][level_name] = level
            else:  # Flat roles (Operations)
                # Create flat role
                role_fte = role_data.get('fte', 0)
                if role_fte > 0:
                    role = RoleData()
                    # Set role attributes from config
                    for key, value in role_data.items():
                        if hasattr(role, key):
                            setattr(role, key, value)
                    # Realistic initialization for flat roles
                    self._initialize_realistic_people(role, int(role_fte), role_name, office_name, "2025-01")
                    office.roles[role_name] = role
        
        return office

    def _get_journey_for_level(self, level_name: str) -> Journey:
        """Get the Journey enum for a given level name."""
        if level_name in ['A', 'AC', 'C']:
            return Journey.JOURNEY_1
        elif level_name in ['SrC', 'AM']:
            return Journey.JOURNEY_2
        elif level_name in ['M', 'SrM', 'Pi']:
            return Journey.JOURNEY_3
        elif level_name == 'P':
            return Journey.JOURNEY_4
        else:
            return Journey.JOURNEY_1

    def _initialize_realistic_people(self, level_or_role, fte_count: int, role_name: str, office_name: str, current_date: str):
        """
        Initialize people with realistic start dates and career histories.
        Copied from OfficeManager for now - will be refactored later.
        """
        if fte_count <= 0:
            return
            
        # Base date for simulation start (current state)
        base_date = datetime(2025, 1, 1)  # January 2025
        
        # Career path table for realistic time on level distribution
        career_paths = {
            'A': {'time_on_level': 6, 'start_tenure': 0, 'end_tenure': 6, 'progression_months': [1, 4, 7, 10]},
            'AC': {'time_on_level': 9, 'start_tenure': 6, 'end_tenure': 15, 'progression_months': [1, 4, 7, 10]},
            'C': {'time_on_level': 18, 'start_tenure': 15, 'end_tenure': 33, 'progression_months': [1, 7]},
            'SrC': {'time_on_level': 18, 'start_tenure': 33, 'end_tenure': 51, 'progression_months': [1, 7]},
            'AM': {'time_on_level': 48, 'start_tenure': 51, 'end_tenure': 99, 'progression_months': [1, 7]},
            'M': {'time_on_level': 48, 'start_tenure': 99, 'end_tenure': 147, 'progression_months': [1]},
            'SrM': {'time_on_level': 120, 'start_tenure': 147, 'end_tenure': 267, 'progression_months': [1]},
            'Pi': {'time_on_level': 12, 'start_tenure': 267, 'end_tenure': 279, 'progression_months': [1]},
            'P': {'time_on_level': 1000, 'start_tenure': 279, 'end_tenure': 1279, 'progression_months': [1]},
            'X': {'time_on_level': 1000, 'start_tenure': 1279, 'end_tenure': 1279, 'progression_months': [1]},
            'OPE': {'time_on_level': 1000, 'start_tenure': 1279, 'end_tenure': 2279, 'progression_months': [13]},
        }
        
        for i in range(fte_count):
            if hasattr(level_or_role, 'name') and level_or_role.name in career_paths:
                # This is a leveled role - create realistic career history
                level_name = level_or_role.name
                career_path = career_paths[level_name]
                
                # Generate realistic total tenure within the range for this level
                start_tenure = career_path['start_tenure']
                end_tenure = career_path['end_tenure']
                
                if end_tenure > start_tenure:
                    total_tenure = random.randint(start_tenure, end_tenure)
                else:
                    total_tenure = start_tenure
                
                # Generate realistic time on level that respects progression months
                progression_months = career_path['progression_months']
                max_time_on_level = career_path['time_on_level']
                
                # Calculate the maximum time on level that would allow progression in a valid month
                current_month = 1  # January 2025
                valid_time_on_levels = []
                
                # Check what time on level would be needed to progress in each valid month
                for prog_month in progression_months:
                    if prog_month >= current_month:
                        # This progression month is in the future, so we can have any time on level
                        valid_time_on_levels.extend(range(0, max_time_on_level + 1))
                    else:
                        # This progression month is in the past, so we need to have progressed already
                        # or be close to the next valid month
                        months_since_prog = (current_month - prog_month) % 12
                        if months_since_prog == 0:
                            # We're in a progression month, so we can have any time on level
                            valid_time_on_levels.extend(range(0, max_time_on_level + 1))
                        else:
                            # We're between progression months, so we can have time on level
                            # that would allow progression in the next valid month
                            next_prog_month = min([m for m in progression_months if m > current_month], default=progression_months[0])
                            months_to_next = next_prog_month - current_month
                            if months_to_next < 0:
                                months_to_next += 12
                            valid_time_on_levels.extend(range(0, max_time_on_level + 1))
                
                # Remove duplicates and ensure we have valid options
                valid_time_on_levels = list(set(valid_time_on_levels))
                if not valid_time_on_levels:
                    valid_time_on_levels = [0]  # Fallback
                
                # Choose a realistic time on level
                time_on_level = random.choice(valid_time_on_levels)
                
                # Ensure time on level doesn't exceed total tenure minus minimum required to reach this level
                min_tenure_for_level = career_path['start_tenure']
                max_allowed_time_on_level = total_tenure - min_tenure_for_level
                time_on_level = min(time_on_level, max_allowed_time_on_level)
                time_on_level = max(0, time_on_level)  # Ensure non-negative
                
                # Calculate career start date (total tenure ago)
                career_start_date = base_date - timedelta(days=total_tenure * 30)
                
                # Calculate level start date (time on level ago)
                level_start_date = base_date - timedelta(days=time_on_level * 30)
                
                # Ensure level start is after career start
                if level_start_date < career_start_date:
                    level_start_date = career_start_date
                
                # Create person with realistic dates
                person = level_or_role.add_new_hire(
                    career_start_date.strftime("%Y-%m"),
                    role_name,
                    office_name
                )
                person.level_start = level_start_date.strftime("%Y-%m")
                
            else:
                # This is a flat role (Operations) - just distribute start dates
                # Operations people typically have 1-5 years of experience
                months_of_experience = random.randint(6, 60)  # 6 months to 5 years
                start_date = base_date - timedelta(days=months_of_experience * 30)
                
                person = level_or_role.add_new_hire(
                    start_date.strftime("%Y-%m"),
                    role_name,
                    office_name
                )

    def load_progression_config(self) -> Dict[str, Any]:
        """
        Load progression configuration rules.
        Currently loads from static config, but can be extended to load from config service.
        Returns a dict of progression rules by level.
        """
        # For now, return the static config
        # TODO: Extend to load from config service or scenario-specific config
        return PROGRESSION_CONFIG

    def load_cat_curves(self) -> Dict[str, Any]:
        """
        Load CAT progression curves.
        Currently loads from static config, but can be extended to load from config service.
        Returns a dict of CAT curves.
        """
        # For now, return the static config
        # TODO: Extend to load from config service or scenario-specific config
        return CAT_CURVES

    def validate_scenario_data(self, scenario_data: Dict[str, Any]) -> None:
        """
        Validate the structure and completeness of the scenario data.
        Raises a ValueError with descriptive message if invalid.
        """
        if not isinstance(scenario_data, dict):
            raise ValueError("Scenario data must be a dictionary")
        
        # Allow empty scenario data (no validation required)
        if not scenario_data:
            return
        
        # Validate baseline_input structure if present
        if 'baseline_input' in scenario_data:
            baseline = scenario_data.get('baseline_input', {})
            if not isinstance(baseline, dict):
                raise ValueError("baseline_input must be a dictionary")
            self._validate_baseline_input(baseline)
        
        # Validate levers structure if present
        if 'levers' in scenario_data:
            levers = scenario_data.get('levers', {})
            if not isinstance(levers, dict):
                raise ValueError("levers must be a dictionary")
            self._validate_levers(levers)

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
                    
                    # Check for level-specific monthly values
                    for level_name, level_data in metric_data.items():
                        if not isinstance(level_data, dict):
                            raise ValueError(f"baseline_input.global.{metric}.{level_name} must be a dictionary")
                        
                        # Check for monthly values (1-12)
                        for month in range(1, 13):
                            month_key = f"{metric}_{month}"
                            if month_key in level_data:
                                value = level_data[month_key]
                                if not isinstance(value, (int, float)):
                                    raise ValueError(f"Invalid {metric} value")
        
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
                        
                        # Check for level-specific monthly values
                        for level_name, level_data in metric_data.items():
                            if not isinstance(level_data, dict):
                                raise ValueError(f"baseline_input.offices.{office_name}.{metric}.{level_name} must be a dictionary")
                            
                            # Check for monthly values (1-12)
                            for month in range(1, 13):
                                month_key = f"{metric}_{month}"
                                if month_key in level_data:
                                    value = level_data[month_key]
                                    if not isinstance(value, (int, float)):
                                        raise ValueError(f"Invalid {metric} value")

    def _validate_levers(self, levers: Dict[str, Any]) -> None:
        """Validate levers structure and content."""
        # Check for global levers
        if 'global' in levers:
            global_levers = levers['global']
            if not isinstance(global_levers, dict):
                raise ValueError("levers.global must be a dictionary")
            
            # Validate lever types
            for lever_type, lever_data in global_levers.items():
                if lever_type not in ['recruitment', 'churn', 'price', 'salary', 'utr']:
                    raise ValueError(f"Unknown lever type: {lever_type}")
                
                if not isinstance(lever_data, dict):
                    raise ValueError(f"levers.global.{lever_type} must be a dictionary")
                
                # Check for level-specific monthly values
                for level_name, level_data in lever_data.items():
                    if not isinstance(level_data, dict):
                        raise ValueError(f"levers.global.{lever_type}.{level_name} must be a dictionary")
                    
                    # Check for monthly values (1-12)
                    for month in range(1, 13):
                        month_key = f"{lever_type}_{month}"
                        if month_key in level_data:
                            value = level_data[month_key]
                            if not isinstance(value, (int, float)):
                                raise ValueError(f"Invalid {lever_type} value")
        
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
                    if lever_type not in ['recruitment', 'churn', 'price', 'salary', 'utr']:
                        raise ValueError(f"Unknown lever type: {lever_type}")
                    
                    if not isinstance(lever_data, dict):
                        raise ValueError(f"levers.offices.{office_name}.{lever_type} must be a dictionary")
                    
                    # Check for level-specific monthly values
                    for level_name, level_data in lever_data.items():
                        if not isinstance(level_data, dict):
                            raise ValueError(f"levers.offices.{office_name}.{lever_type}.{level_name} must be a dictionary")
                        
                        # Check for monthly values (1-12)
                        for month in range(1, 13):
                            month_key = f"{lever_type}_{month}"
                            if month_key in level_data:
                                value = level_data[month_key]
                                if not isinstance(value, (int, float)):
                                    raise ValueError(f"Invalid {lever_type} value")

    def list_scenarios(self) -> list:
        """
        List all saved scenarios using the storage service. Returns a list of scenario metadata dictionaries with IDs.
        """
        try:
            # Use the storage service to list scenarios (now includes IDs)
            scenarios = self.storage_service.list_scenarios()
            # Scenarios are already dictionaries with IDs included
            return scenarios
        except Exception as e:
            logger.error(f"Error listing scenarios: {e}")
            return []

    def create_scenario(self, scenario_def: ScenarioDefinition) -> str:
        """
        Create and save a new scenario definition using ScenarioStorageService.
        """
        return self.storage_service.create_scenario(scenario_def)

    def get_scenario(self, scenario_id: str) -> Optional[dict]:
        """
        Retrieve a scenario definition by ID and return as a dictionary, or None if not found.
        """
        scenario = self.storage_service.get_scenario(scenario_id)
        if scenario is not None:
            return scenario.model_dump()
        return None

    def delete_scenario(self, scenario_id: str) -> bool:
        """Delete a scenario definition and its results."""
        return self.storage_service.delete_scenario(scenario_id)

    def update_scenario(self, scenario_id: str, scenario_def: ScenarioDefinition) -> bool:
        """
        Update an existing scenario by ID. Returns True if successful, False if not found.
        """
        try:
            return self.storage_service.update_scenario(scenario_id, scenario_def)
        except Exception as e:
            logger.error(f"Error updating scenario {scenario_id}: {e}")
            return False

    def scenario_name_exists(self, name: str, exclude_id: str = None) -> bool:
        """
        Check if a scenario with the given name already exists.
        Optionally exclude a specific scenario ID (for updates).
        """
        try:
            scenarios = self.storage_service.list_scenarios()
            for scenario in scenarios:
                if scenario.name == name and (exclude_id is None or scenario.id != exclude_id):
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking scenario name existence: {e}")
            return False

    def run_scenario(self, request: ScenarioRequest) -> ScenarioResponse:
        """
        Run a scenario and return the results.
        This is the main entry point for scenario execution.
        """
        try:
            start_time = datetime.now()
            
            # Get scenario definition - either from request or load from storage
            scenario_def = request.scenario_definition
            if not scenario_def and request.scenario_id:
                # Load scenario definition from storage
                scenario = self.storage_service.get_scenario(request.scenario_id)
                if not scenario:
                    return ScenarioResponse(
                        status="error",
                        error_message=f"Scenario not found: {request.scenario_id}",
                        scenario_id=request.scenario_id,
                        scenario_name="",
                        execution_time=0,
                        results={}
                    )
                scenario_def = scenario
            elif not scenario_def:
                return ScenarioResponse(
                    status="error",
                    error_message="No scenario definition provided",
                    scenario_id="",
                    scenario_name="",
                    execution_time=0,
                    results={}
                )
            
            # Resolve scenario data into simulation-ready format
            resolved_data = self.resolve_scenario({
                'time_range': scenario_def.time_range,
                'office_scope': scenario_def.office_scope,
                'levers': scenario_def.levers or {},
                'baseline_input': getattr(scenario_def, 'baseline_input', None) or {}
            })
            
            # Create economic parameters
            economic_params = self._create_economic_params(scenario_def)
            
            # Run simulation through engine
            results = self._call_simulation_engine(scenario_def, resolved_data, economic_params)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Save results using storage service
            scenario_id = request.scenario_id or str(uuid.uuid4())
            self.storage_service.save_scenario_results(scenario_id, results)
            
            return ScenarioResponse(
                scenario_id=scenario_id,
                scenario_name=scenario_def.name,
                execution_time=execution_time,
                results=results,
                status="success"
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error running scenario: {e}")
            return ScenarioResponse(
                status="error",
                error_message=str(e),
                scenario_id=request.scenario_id or "",
                scenario_name=request.scenario_definition.name if request.scenario_definition else "",
                execution_time=execution_time,
                results={}
            )
    
    def _create_economic_params(self, scenario_def: ScenarioDefinition) -> EconomicParameters:
        """Create economic parameters for the simulation."""
        # Use default values if economic_params is not provided
        economic_params = scenario_def.economic_params or {}
        # Only keep valid keys
        valid_keys = {
            'unplanned_absence',
            'other_expense',
            'employment_cost_rate',
            'working_hours_per_month',
            'utilization'
        }
        filtered_params = {k: v for k, v in economic_params.items() if k in valid_keys}
        
        return EconomicParameters(
            unplanned_absence=filtered_params.get('unplanned_absence', 0.05),
            other_expense=filtered_params.get('other_expense', 19000000.0),
            employment_cost_rate=filtered_params.get('employment_cost_rate', 0.40),
            working_hours_per_month=filtered_params.get('working_hours_per_month', 166.4),
            utilization=filtered_params.get('utilization', 0.85)
        )
    
    def _call_simulation_engine(self, scenario_def: ScenarioDefinition, resolved_data: Dict[str, Any], economic_params: EconomicParameters) -> Dict[str, Any]:
        """Call the simulation engine with the prepared data."""
        try:
            # Extract time range from scenario definition
            start_year = scenario_def.time_range['start_year']
            start_month = scenario_def.time_range['start_month']
            end_year = scenario_def.time_range['end_year']
            end_month = scenario_def.time_range['end_month']

            # Create simulation engine
            engine = SimulationEngine()
            
            # Run simulation using the correct arguments
            # Note: We pass the lever_plan separately, not as resolved_data
            lever_plan = scenario_def.levers or {}
            
            results = engine.run_simulation(
                start_year=start_year,
                start_month=start_month,
                end_year=end_year,
                end_month=end_month,
                lever_plan=lever_plan,
                economic_params=economic_params
            )
            
            # Convert results to serializable format
            def to_dict(data):
                if hasattr(data, 'model_dump'):
                    return data.model_dump()
                elif isinstance(data, dict):
                    return {k: to_dict(v) for k, v in data.items()}
                elif isinstance(data, list):
                    return [to_dict(item) for item in data]
                else:
                    return data
            
            serializable_results = to_dict(results)
            
            # Clean up any non-serializable data
            def clean_for_serialization(data):
                if isinstance(data, dict):
                    return {k: clean_for_serialization(v) for k, v in data.items() if k is not None}
                elif isinstance(data, list):
                    return [clean_for_serialization(item) for item in data]
                elif isinstance(data, (int, float, str, bool, type(None))):
                    return data
                else:
                    return str(data)
            
            final_results = clean_for_serialization(serializable_results)
            
            logger.info(f"Simulation completed successfully for scenario: {scenario_def.name}")
            return final_results
            
        except Exception as e:
            logger.error(f"Simulation engine error: {e}")
            raise

    def get_scenario_results(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """
        Get saved results for a specific scenario.
        """
        try:
            return self.storage_service.get_scenario_results(scenario_id)
        except Exception as e:
            logger.error(f"Error getting scenario results for {scenario_id}: {e}")
            return None 