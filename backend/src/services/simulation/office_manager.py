from typing import Dict, List, Any
from backend.src.services.simulation.models import Office, Level, RoleData, Month, Journey, OfficeJourney
<<<<<<< HEAD
from backend.config.progression_config import PROGRESSION_CONFIG
import random
from datetime import datetime, timedelta
=======
>>>>>>> gitlab/master

class OfficeManager:
    """
    Handles office, role, and level initialization and configuration.
    """
<<<<<<< HEAD
    def __init__(self, config_service, event_logger=None):
        self.config_service = config_service
        self.offices: Dict[str, Office] = {}
        self.level_order: List[str] = []
        self.event_logger = event_logger

    def initialize_offices_from_config(self):
        config_dict = self.config_service.get_config()
=======
    def __init__(self, config_service):
        self.config_service = config_service
        self.offices: Dict[str, Office] = {}
        self.level_order: List[str] = []

    def initialize_offices_from_config(self):
        config_dict = self.config_service.get_configuration()
>>>>>>> gitlab/master
        config_data = [office_config for office_config in config_dict.values()]
        self.level_order = self.determine_level_order(config_data)
        self.offices = {}
        for office_config in config_data:
            office = self._create_office_from_config(office_config)
            self.offices[office.name] = office
        return self.offices

    def _create_office_from_config(self, office_config: Dict[str, Any]) -> Office:
        office_name = office_config.get('name', 'Unknown Office')
        total_fte = office_config.get('total_fte', 0)
        office = Office.create_office(office_name, total_fte)
<<<<<<< HEAD
        
        # Set seed for deterministic results
        random.seed(42)
        
=======
>>>>>>> gitlab/master
        for role_name, role_data in office_config.get('roles', {}).items():
            if role_name == 'Operations':
                op_fte = role_data.get('fte', 0)
                operations_role = RoleData()
                for i in range(1, 13):
                    salary = role_data.get(f'salary_{i}', role_data.get('salary', 40000.0))
                    price = role_data.get(f'price_{i}', role_data.get('price', 0.0))
                    utr = role_data.get(f'utr_{i}', role_data.get('utr', 0.0))
                    setattr(operations_role, f'salary_{i}', salary)
                    setattr(operations_role, f'price_{i}', price)
                    setattr(operations_role, f'utr_{i}', utr)
<<<<<<< HEAD
                
                # Realistic initialization for Operations
                self._initialize_realistic_people(operations_role, int(op_fte), "Operations", office_name, "2025-01")
=======
                initialization_date_str = "2023-01"
                for _ in range(int(op_fte)):
                    operations_role.add_new_hire(initialization_date_str, "Operations", office_name)
>>>>>>> gitlab/master
                office.roles['Operations'] = operations_role
            else:
                office.roles[role_name] = {}
                for level_name, level_config in role_data.items():
                    journey_name = self.get_journey_for_level(level_name)
                    level_attributes = {}
                    for key in ['progression', 'recruitment', 'churn', 'price', 'salary', 'utr']:
                        for i in range(1, 13):
                            monthly_key = f'{key}_{i}'
                            if monthly_key in level_config:
                                level_attributes[monthly_key] = level_config[monthly_key]
                            else:
                                default_value = level_config.get(key, 0.0)
                                level_attributes[monthly_key] = default_value
<<<<<<< HEAD
                    # FIX: Use progression_months from PROGRESSION_CONFIG
                    progression_months = PROGRESSION_CONFIG.get(level_name, {}).get('progression_months', [1])
                    level = Level(
                        name=level_name,
                        journey=journey_name,
                        progression_months=[Month(m) for m in progression_months],
                        **level_attributes
                    )
                    level_fte = level_config.get('fte', 0)
                    
                    # Realistic initialization for leveled roles
                    self._initialize_realistic_people(level, int(level_fte), role_name, office_name, "2025-01")
                    office.roles[role_name][level_name] = level
        return office

    def _initialize_realistic_people(self, level_or_role, fte_count: int, role_name: str, office_name: str, current_date: str):
        """
        Initialize people with realistic start dates and career histories.
        
        For leveled roles, creates people with appropriate time on level that respects progression months.
        For flat roles (Operations), creates people with distributed start dates.
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
                # We want to ensure people can potentially progress in the next valid progression month
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
                
                # Log initial recruitment event if event logger is available
                if self.event_logger:
                    self.event_logger.log_recruitment(
                        person=person,
                        current_date=current_date,
                        role=role_name,
                        office=office_name,
                        recruitment_rate=None  # Initial population, no rate
                    )
                
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
                
                # Log initial recruitment event if event logger is available
                if self.event_logger:
                    self.event_logger.log_recruitment(
                        person=person,
                        current_date=current_date,
                        role=role_name,
                        office=office_name,
                        recruitment_rate=None  # Initial population, no rate
                    )

=======
                    level = Level(
                        name=level_name,
                        journey=journey_name,
                        progression_months=[Month(i) for i in range(1, 13)],
                        **level_attributes
                    )
                    level_fte = level_config.get('fte', 0)
                    initialization_date_str = "2023-01"
                    for _ in range(int(level_fte)):
                        level.add_new_hire(initialization_date_str, role_name, office_name)
                    office.roles[role_name][level_name] = level
        return office

>>>>>>> gitlab/master
    @staticmethod
    def determine_level_order(config_data: List[Dict]) -> List[str]:
        levels = set()
        for office_config in config_data:
            for role_name, role_data in office_config.get('roles', {}).items():
                if role_name != 'Operations':
                    levels.update(role_data.keys())
        standard_order = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']
        sorted_levels = [level for level in standard_order if level in levels]
        return sorted_levels

    @staticmethod
    def get_journey_for_level(level_name: str) -> Journey:
        # Simple journey mapping without default config
        if level_name in ['A', 'AC', 'C']:
            return Journey.JOURNEY_1
        elif level_name in ['SrC', 'AM']:
            return Journey.JOURNEY_2
        elif level_name in ['M', 'SrM']:
            return Journey.JOURNEY_3
        elif level_name == 'PiP':
            return Journey.JOURNEY_4
        else:
            return Journey.JOURNEY_1 