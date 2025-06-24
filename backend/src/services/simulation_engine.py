from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
import sys
import os
import uuid
import random
import hashlib
from copy import deepcopy
import logging

# Import config from backend.config
from backend.config.default_config import (
    OFFICE_HEADCOUNT,
    ROLE_DISTRIBUTION,
    CONSULTANT_LEVEL_DISTRIBUTION,
    DEFAULT_RATES,
    BASE_PRICING,
    BASE_SALARIES,
    CURRENCY_CONFIG,
    JOURNEY_CLASSIFICATION,
    ACTUAL_OFFICE_LEVEL_DATA
)

# Import KPI service
from backend.src.services.kpi import KPIService, EconomicParameters
from backend.src.services.config_service import config_service
from backend.src.services.simulation.workforce import WorkforceManager
from backend.src.services.simulation.office_manager import OfficeManager
from backend.src.services.simulation.models import Office, Level, RoleData, Month, Journey, OfficeJourney
from backend.src.services.simulation.utils import log_yearly_results, log_office_aggregates_per_year

class Month(Enum):
    JAN = 1
    FEB = 2
    MAR = 3
    APR = 4
    MAY = 5
    JUN = 6
    JUL = 7
    AUG = 8
    SEP = 9
    OCT = 10
    NOV = 11
    DEC = 12

class HalfYear(Enum):
    H1 = "H1"
    H2 = "H2"

class Journey(Enum):
    JOURNEY_1 = "Journey 1"
    JOURNEY_2 = "Journey 2"
    JOURNEY_3 = "Journey 3"
    JOURNEY_4 = "Journey 4"

class OfficeJourney(Enum):
    NEW = "New Office"          # 0-24 FTE
    EMERGING = "Emerging Office"  # 25-199 FTE
    ESTABLISHED = "Established Office"  # 200-499 FTE
    MATURE = "Mature Office"    # 500+ FTE

@dataclass
class Person:
    """Represents an individual employee"""
    id: str
    career_start: str      # "YYYY-MM" when they joined the company
    current_level: str     # "A", "AC", "C", etc.
    level_start: str       # "YYYY-MM" when they joined current level
    role: str              # "Consultant", "Sales", "Recruitment", "Operati"
    office: str            # Office name
    
    def get_career_tenure_months(self, current_date: str) -> int:
        """Get career tenure in months"""
        current_dt = datetime.strptime(current_date, "%Y-%m")
        career_start_dt = datetime.strptime(self.career_start, "%Y-%m")
        return (current_dt.year - career_start_dt.year) * 12 + (current_dt.month - career_start_dt.month)
    
    def get_level_tenure_months(self, current_date: str) -> int:
        """Get time on current level in months"""
        current_dt = datetime.strptime(current_date, "%Y-%m")
        level_start_dt = datetime.strptime(self.level_start, "%Y-%m")
        return (current_dt.year - level_start_dt.year) * 12 + (current_dt.month - level_start_dt.month)
    
    def is_eligible_for_progression(self, current_date: str, minimum_tenure_months: int = 6) -> bool:
        """Check if person is eligible for progression based on minimum tenure for their level"""
        return self.get_level_tenure_months(current_date) >= minimum_tenure_months
    
    def get_cat_category(self, current_date: str) -> str:
        """Get CAT category based on time on current level"""
        tenure_months = self.get_level_tenure_months(current_date)
        
        if tenure_months < 6:
            return 'CAT0'
        else:
            cat_number = min(30, 6 * ((tenure_months // 6)))
            return f'CAT{cat_number}'
    
    def get_progression_probability(self, current_date: str, base_progression_rate: float, level_name: str) -> float:
        """Calculate individual progression probability based on CAT and level"""
        # Import here to avoid circular import
        from backend.config.default_config import DEFAULT_RATES
        
        # Get CAT category
        cat = self.get_cat_category(current_date)
        
        # Get CAT multiplier for this level
        if level_name in DEFAULT_RATES['progression']['cat_curves']:
            cat_multiplier = DEFAULT_RATES['progression']['cat_curves'][level_name].get(cat, 0.0)
        else:
            # Fallback for levels not in cat_curves (like PiP)
            cat_multiplier = 1.0 if cat != 'CAT0' else 0.0
        
        # Calculate actual progression probability
        return base_progression_rate * cat_multiplier

@dataclass
class RoleData:
    # Monthly recruitment rates (1-12)
    recruitment_1: float = 0.0
    recruitment_2: float = 0.0
    recruitment_3: float = 0.0
    recruitment_4: float = 0.0
    recruitment_5: float = 0.0
    recruitment_6: float = 0.0
    recruitment_7: float = 0.0
    recruitment_8: float = 0.0
    recruitment_9: float = 0.0
    recruitment_10: float = 0.0
    recruitment_11: float = 0.0
    recruitment_12: float = 0.0
    # Monthly churn rates (1-12)
    churn_1: float = 0.0
    churn_2: float = 0.0
    churn_3: float = 0.0
    churn_4: float = 0.0
    churn_5: float = 0.0
    churn_6: float = 0.0
    churn_7: float = 0.0
    churn_8: float = 0.0
    churn_9: float = 0.0
    churn_10: float = 0.0
    churn_11: float = 0.0
    churn_12: float = 0.0
    # Monthly prices (1-12)
    price_1: float = 0.0
    price_2: float = 0.0
    price_3: float = 0.0
    price_4: float = 0.0
    price_5: float = 0.0
    price_6: float = 0.0
    price_7: float = 0.0
    price_8: float = 0.0
    price_9: float = 0.0
    price_10: float = 0.0
    price_11: float = 0.0
    price_12: float = 0.0
    # Monthly salaries (1-12)
    salary_1: float = 0.0
    salary_2: float = 0.0
    salary_3: float = 0.0
    salary_4: float = 0.0
    salary_5: float = 0.0
    salary_6: float = 0.0
    salary_7: float = 0.0
    salary_8: float = 0.0
    salary_9: float = 0.0
    salary_10: float = 0.0
    salary_11: float = 0.0
    salary_12: float = 0.0
    # Monthly UTR (1-12)
    utr_1: float = 1.0
    utr_2: float = 1.0
    utr_3: float = 1.0
    utr_4: float = 1.0
    utr_5: float = 1.0
    utr_6: float = 1.0
    utr_7: float = 1.0
    utr_8: float = 1.0
    utr_9: float = 1.0
    utr_10: float = 1.0
    utr_11: float = 1.0
    utr_12: float = 1.0
    # Individual tracking
    people: List[Person] = field(default_factory=list)
    # Fractional accumulation for deterministic results
    fractional_recruitment: float = 0.0
    fractional_churn: float = 0.0
    
    @property
    def total(self) -> int:
        return len(self.people)
    
    def add_new_hire(self, current_date: str, role: str, office: str) -> Person:
        """Add a new external hire"""
        person = Person(
            id=str(uuid.uuid4()),
            career_start=current_date,
            current_level="Operations",  # Operations doesn't have levels
            level_start=current_date,
            role=role,
            office=office
        )
        self.people.append(person)
        return person
    
    def apply_churn(self, churn_count: int) -> List[Person]:
        """Apply churn randomly, return churned people"""
        if churn_count <= 0 or len(self.people) == 0:
            return []
        
        churn_count = min(churn_count, len(self.people))
        churned = random.sample(self.people, churn_count)
        
        for person in churned:
            self.people.remove(person)
        
        return churned
    
    def get_average_career_tenure(self, current_date: str) -> float:
        """Get average career tenure in months"""
        if len(self.people) == 0:
            return 0.0
        return sum(p.get_career_tenure_months(current_date) for p in self.people) / len(self.people)

@dataclass
class Level:
    name: str
    journey: Journey
    # Which months progression occurs
    progression_months: List[Month]
    # Monthly progression rates (1-12)
    progression_1: float  # percentage
    progression_2: float  # percentage
    progression_3: float  # percentage
    progression_4: float  # percentage
    progression_5: float  # percentage
    progression_6: float  # percentage
    progression_7: float  # percentage
    progression_8: float  # percentage
    progression_9: float  # percentage
    progression_10: float  # percentage
    progression_11: float  # percentage
    progression_12: float  # percentage
    # Monthly recruitment rates (1-12)
    recruitment_1: float  # percentage
    recruitment_2: float  # percentage
    recruitment_3: float  # percentage
    recruitment_4: float  # percentage
    recruitment_5: float  # percentage
    recruitment_6: float  # percentage
    recruitment_7: float  # percentage
    recruitment_8: float  # percentage
    recruitment_9: float  # percentage
    recruitment_10: float  # percentage
    recruitment_11: float  # percentage
    recruitment_12: float  # percentage
    # Monthly churn rates (1-12)
    churn_1: float       # percentage
    churn_2: float       # percentage
    churn_3: float       # percentage
    churn_4: float       # percentage
    churn_5: float       # percentage
    churn_6: float       # percentage
    churn_7: float       # percentage
    churn_8: float       # percentage
    churn_9: float       # percentage
    churn_10: float       # percentage
    churn_11: float       # percentage
    churn_12: float       # percentage
    # Monthly prices (1-12)
    price_1: float
    price_2: float
    price_3: float
    price_4: float
    price_5: float
    price_6: float
    price_7: float
    price_8: float
    price_9: float
    price_10: float
    price_11: float
    price_12: float
    # Monthly salaries (1-12)
    salary_1: float
    salary_2: float
    salary_3: float
    salary_4: float
    salary_5: float
    salary_6: float
    salary_7: float
    salary_8: float
    salary_9: float
    salary_10: float
    salary_11: float
    salary_12: float
    # Monthly UTR (1-12)
    utr_1: float        # percentage
    utr_2: float        # percentage
    utr_3: float        # percentage
    utr_4: float        # percentage
    utr_5: float        # percentage
    utr_6: float        # percentage
    utr_7: float        # percentage
    utr_8: float        # percentage
    utr_9: float        # percentage
    utr_10: float       # percentage
    utr_11: float       # percentage
    utr_12: float       # percentage
    # Individual tracking
    people: List[Person] = field(default_factory=list)
    # Fractional accumulation for deterministic results
    fractional_recruitment: float = 0.0
    fractional_churn: float = 0.0
    
    @property
    def total(self) -> int:
        return len(self.people)
    
    def add_new_hire(self, current_date: str, role: str, office: str) -> Person:
        """Add a new external hire"""
        person = Person(
            id=str(uuid.uuid4()),
            career_start=current_date,
            current_level=self.name,
            level_start=current_date,
            role=role,
            office=office
        )
        self.people.append(person)
        return person
    
    def add_promotion(self, person: Person, current_date: str):
        """Add someone promoted from another level"""
        person.current_level = self.name
        person.level_start = current_date
        self.people.append(person)
    
    def get_eligible_for_progression(self, current_date: str) -> List[Person]:
        """Get people eligible for progression based on minimum tenure for this level"""
        # Import here to avoid circular import
        from backend.config.default_config import DEFAULT_RATES
        
        # Get minimum tenure for this level
        minimum_tenure = DEFAULT_RATES['progression']['minimum_tenure'].get(self.name, 6)
        
        return [p for p in self.people if p.is_eligible_for_progression(current_date, minimum_tenure)]
    
    def apply_churn(self, churn_count: int) -> List[Person]:
        """Apply churn randomly, return churned people"""
        if churn_count <= 0 or len(self.people) == 0:
            return []
        
        churn_count = min(churn_count, len(self.people))
        churned = random.sample(self.people, churn_count)
        
        for person in churned:
            self.people.remove(person)
        
        return churned
    
    def apply_progression(self, progression_count: int, current_date: str) -> List[Person]:
        """Legacy method for backward compatibility - now uses CAT-based progression"""
        # Convert to rate and use CAT-based method
        eligible = self.get_eligible_for_progression(current_date)
        if len(eligible) == 0:
            return []
        
        # Calculate implied rate from count
        progression_rate = progression_count / len(eligible) if len(eligible) > 0 else 0.0
        return self.apply_cat_based_progression(progression_rate, current_date)
    
    def apply_cat_based_progression(self, base_progression_rate: float, current_date: str) -> List[Person]:
        """Apply CAT-based progression with individual probabilities, return promoted people"""
        eligible = self.get_eligible_for_progression(current_date)
        
        if base_progression_rate <= 0 or len(eligible) == 0:
            return []
        
        promoted = []
        for person in eligible:
            # Calculate individual progression probability based on CAT
            individual_probability = person.get_progression_probability(
                current_date, base_progression_rate, self.name
            )
            
            # Apply random chance
            if random.random() < individual_probability:
                promoted.append(person)
        
        # Remove promoted people from this level
        for person in promoted:
            self.people.remove(person)
        
        return promoted
    
    def get_average_career_tenure(self, current_date: str) -> float:
        """Get average career tenure in months"""
        if len(self.people) == 0:
            return 0.0
        return sum(p.get_career_tenure_months(current_date) for p in self.people) / len(self.people)
    
    def get_average_level_tenure(self, current_date: str) -> float:
        """Get average time on current level in months"""
        if len(self.people) == 0:
            return 0.0
        return sum(p.get_level_tenure_months(current_date) for p in self.people) / len(self.people)

@dataclass
class Office:
    name: str
    total_fte: int
    journey: OfficeJourney
    roles: Dict[str, Dict[str, Level] or RoleData]  # 'Consultant': {level: Level}, others: RoleData

    @classmethod
    def create_office(cls, name: str, total_fte: int) -> 'Office':
        # Corrected thresholds: 0-24 = New, 25-199 = Emerging, 200-499 = Established, 500+ = Mature
        if total_fte >= 500:
            journey = OfficeJourney.MATURE
        elif total_fte >= 200:
            journey = OfficeJourney.ESTABLISHED
        elif total_fte >= 25:
            journey = OfficeJourney.EMERGING
        else:
            journey = OfficeJourney.NEW # 0-24 FTE
        
        return cls(
            name=name,
            total_fte=total_fte,
            journey=journey,
            roles={}
        )

class SimulationEngine:
    """
    The core simulation engine for SimpleSim.
    This class manages the simulation state and runs the monthly progression,
    recruitment, and churn calculations.
    """

    def __init__(self, config_service_instance=None):
        """
        Initialize the simulation engine.
        - offices: A dictionary of Office objects, keyed by office name.
        - monthly_results: A dictionary to store detailed monthly simulation outputs.
        """
        print("✅ [ENGINE] SimulationEngine created, awaiting initialization.")
        self.config_service = config_service_instance or config_service
        self.offices: Dict[str, Office] = {}
        self.monthly_results: Dict[str, Any] = {}
        self.simulation_results: Optional[Dict[str, Any]] = None
        self.office_manager = OfficeManager(self.config_service)
        
        # Set up yearly logging
        self._setup_yearly_logging()
        
        # Initialize offices from config
        self._initialize_offices_from_config_service()

    def _setup_yearly_logging(self):
        """Set up logging for yearly simulation results"""
        # Create logs directory if it doesn't exist
        os.makedirs('backend/logs', exist_ok=True)
        
        # Configure yearly logging
        self.yearly_logger = logging.getLogger('simulation_yearly')
        self.yearly_logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        for handler in self.yearly_logger.handlers[:]:
            self.yearly_logger.removeHandler(handler)
        
        # Create file handler for yearly log
        yearly_handler = logging.FileHandler('backend/logs/simulation_yearly.log', mode='w')
        yearly_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(message)s')
        yearly_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.yearly_logger.addHandler(yearly_handler)
        
        # Prevent propagation to avoid duplicate logs
        self.yearly_logger.propagate = False

    def reinitialize_with_config(self):
        """Re-initialize the engine with the latest configuration from the service."""
        self.reset_simulation_state()
        self._initialize_offices_from_config_service()
    
    def reset_simulation_state(self):
        """Reset the simulation state to a clean slate."""
        self.offices = {}
        self.monthly_results = {}
        self.simulation_results = None

    def _initialize_offices_from_config_service(self):
        """Initialize offices and their roles/levels from the configuration service."""
        config_dict = self.config_service.get_configuration()
        # Convert dict to list format expected by the rest of the method
        config_data = []
        for office_name, office_config in config_dict.items():
            config_data.append(office_config)
        
        # Determine the level order for progression
        self.level_order = self._determine_level_order(config_data)

        for office_config in config_data:
            office_name = office_config.get('name', 'Unknown Office')
            total_fte = office_config.get('total_fte', 0)
            
            # Create the Office object
            office = Office.create_office(office_name, total_fte)
            
            # Initialize roles and levels
            for role_name, role_data in office_config.get('roles', {}).items():
                if role_name == 'Operations':
                    # Handle flat structure for Operations
                    op_fte = role_data.get('fte', 0)
                    
                    operations_role = RoleData()
                    
                    # Set monthly values from config
                    for i in range(1, 13):
                        # Look for monthly values first, then fall back to base values
                        salary_key = f'salary_{i}'
                        price_key = f'price_{i}'
                        utr_key = f'utr_{i}'
                        
                        salary = role_data.get(salary_key, role_data.get('salary', 40000.0))  # Default ops salary
                        price = role_data.get(price_key, role_data.get('price', 0.0))  # Ops don't generate revenue
                        utr = role_data.get(utr_key, role_data.get('utr', 0.0))  # Ops don't have UTR
                        
                        setattr(operations_role, f'salary_{i}', salary)
                        setattr(operations_role, f'price_{i}', price)
                        setattr(operations_role, f'utr_{i}', utr)

                    # Use a date 2 years before simulation start to ensure people have sufficient tenure
                    initialization_date_str = "2023-01"
                    for _ in range(int(op_fte)):
                        operations_role.add_new_hire(initialization_date_str, "Operations", office_name)
                    
                    office.roles['Operations'] = operations_role
                else:
                    # Handle roles with levels (Consultant, Sales, Recruitment)
                    office.roles[role_name] = {}
                    for level_name, level_config in role_data.items():
                        # Determine progression months (e.g., June and December)
                        progression_months = [Month.JUN, Month.DEC]

                        # Create Level object
                        journey_name = self._get_journey_for_level(level_name)
                        
                        # Build monthly attributes from config
                        level_attributes = {}
                        for key in ['progression', 'recruitment', 'churn', 'price', 'salary', 'utr']:
                            for i in range(1, 13):
                                monthly_key = f'{key}_{i}'
                                config_value = level_config.get(monthly_key, None)
                                if key == 'progression':
                                    # Only use config value if it is not None and not 0.0
                                    if config_value is not None and config_value != 0.0:
                                        level_attributes[monthly_key] = config_value
                                    else:
                                        # Use default progression rates for evaluation months
                                        if i in DEFAULT_RATES['progression']['evaluation_months']:
                                            if level_name == 'C':
                                                progression_rate = DEFAULT_RATES['progression']['base_rates']['C->SrC'] / 2
                                            elif level_name == 'SrC':
                                                progression_rate = DEFAULT_RATES['progression']['base_rates']['SrC->AM'] / 2
                                            elif level_name == 'AM':
                                                progression_rate = DEFAULT_RATES['progression']['base_rates']['AM->M'] / 2
                                            elif level_name == 'M':
                                                progression_rate = DEFAULT_RATES['progression']['base_rates']['M->SrM'] / 2
                                            elif level_name == 'SrM':
                                                progression_rate = DEFAULT_RATES['progression']['base_rates']['SrM->PiP'] / 2
                                            else:
                                                progression_rate = 0.10
                                            level_attributes[monthly_key] = progression_rate
                                        else:
                                            level_attributes[monthly_key] = DEFAULT_RATES['progression']['non_evaluation_rate']
                                elif key == 'utr':
                                    level_attributes[monthly_key] = level_config.get(monthly_key, level_config.get(key, DEFAULT_RATES['utr']))
                                else:
                                    level_attributes[monthly_key] = config_value if config_value is not None else level_config.get(key, 0.0)
                        
                        level = Level(
                            name=level_name,
                            journey=journey_name,
                            progression_months=progression_months,
                            **level_attributes
                        )
                        
                        # Initialize people in this level
                        level_fte = level_config.get('fte', 0)
                        # Use a date 2 years before simulation start to ensure people have sufficient tenure
                        initialization_date_str = "2023-01"
                        for _ in range(int(level_fte)):
                            level.add_new_hire(initialization_date_str, role_name, office_name)
                        
                        office.roles[role_name][level_name] = level

            self.offices[office_name] = office
    
    def _determine_level_order(self, config_data: List[Dict]) -> List[str]:
        """Dynamically determine the level order from configuration."""
        levels = set()
        for office_config in config_data:
            for role_name, role_data in office_config.get('roles', {}).items():
                if role_name != 'Operations':
                    levels.update(role_data.keys())
        
        # Use a standard, sorted progression path
        standard_order = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']
        
        # Filter and sort found levels according to the standard order
        sorted_levels = [level for level in standard_order if level in levels]
        
        return sorted_levels

    def _get_journey_for_level(self, level_name: str) -> Journey:
        """Get the Journey enum for a given level name."""
        for journey, levels in JOURNEY_CLASSIFICATION.items():
            if level_name in levels:
                return Journey(journey)
        return Journey.JOURNEY_1 # Default

    def _initialize_offices(self):
        """Initializes all offices with default data"""
        self.offices = {}
        for office_name, total_fte in OFFICE_HEADCOUNT.items():
            self.offices[office_name] = Office.create_office(office_name, total_fte)

    def _initialize_roles(self):
        """Initializes roles and levels for all offices"""
        for office in self.offices.values():
            office.roles = {} # Clear existing roles
            # Initialize Consultant role with levels
            office.roles['Consultant'] = {}
            for level_name, level_percentage in CONSULTANT_LEVEL_DISTRIBUTION.items():
                # Get journey for this level
                journey = self._get_journey_for_level(level_name)
                # Progression occurs in June and December
                progression_months = [Month.JUN, Month.DEC]
                
                # Calculate progression rates for all 12 months
                progression_rates = {}
                for i in range(1, 13):
                    if i in DEFAULT_RATES['progression']['evaluation_months']:
                        # Get the appropriate base rate for this level
                        progression_rate = 0.0
                        if level_name == 'C':
                            progression_rate = DEFAULT_RATES['progression']['base_rates']['C->SrC'] / 2  # Half-yearly to semi-annual
                        elif level_name == 'SrC':
                            progression_rate = DEFAULT_RATES['progression']['base_rates']['SrC->AM'] / 2
                        elif level_name == 'AM':
                            progression_rate = DEFAULT_RATES['progression']['base_rates']['AM->M'] / 2
                        elif level_name == 'M':
                            progression_rate = DEFAULT_RATES['progression']['base_rates']['M->SrM'] / 2
                        elif level_name == 'SrM':
                            progression_rate = DEFAULT_RATES['progression']['base_rates']['SrM->PiP'] / 2
                        else:
                            progression_rate = 0.10  # Default fallback for A/AC levels
                        
                        progression_rates[f'progression_{i}'] = progression_rate
                    else:
                        # Other months have no progression
                        progression_rates[f'progression_{i}'] = DEFAULT_RATES['progression']['non_evaluation_rate']
                
                level = Level(
                    name=level_name,
                    journey=journey,
                    progression_months=progression_months,
                    # Set progression rates for all 12 months
                    **progression_rates,
                    **{f'recruitment_{i}': 0.0 for i in range(1, 13)},
                    **{f'churn_{i}': 0.0 for i in range(1, 13)},
                    **{f'price_{i}': BASE_PRICING.get(office.name, {}).get(level_name, 0.0) for i in range(1, 13)},
                    **{f'salary_{i}': BASE_SALARIES.get(office.name, {}).get(level_name, 0.0) for i in range(1, 13)},
                    **{f'utr_{i}': 0.0 for i in range(1, 13)}
                )
                
                # Set initial headcount
                consultant_fte = office.total_fte * ROLE_DISTRIBUTION.get('Consultant', 0.8)
                level_fte = int(consultant_fte * level_percentage)
                # Use a date 2 years before simulation start to ensure people have sufficient tenure
                initialization_date_str = "2023-01"
                for _ in range(level_fte):
                    level.add_new_hire(initialization_date_str, "Consultant", office.name)
                    
                office.roles['Consultant'][level_name] = level
            
            # Initialize other roles (flat structure)
            for role_name in ['Sales', 'Recruitment', 'Operations']:
                role_fte = int(office.total_fte * ROLE_DISTRIBUTION.get(role_name, 0.05))
                role_data = RoleData()
                # Use a date 2 years before simulation start to ensure people have sufficient tenure
                initialization_date_str = "2023-01"
                for _ in range(role_fte):
                    role_data.add_new_hire(initialization_date_str, role_name, office.name)
                office.roles[role_name] = role_data

    def _initialize_roles_with_levers(self, lever_plan: Optional[Dict] = None):
        """Initializes roles and levels, applying any levers from the start."""
        if lever_plan is None:
            self._initialize_roles()
            return
            
        # Global levers (apply to all offices)
        global_levers = lever_plan.get('global', {})
        
        for office in self.offices.values():
            office.roles = {} # Clear existing roles
            
            # Get office-specific levers
            office_levers = lever_plan.get('offices', {}).get(office.name, {})
            
            # Initialize Consultant role with levels
            office.roles['Consultant'] = {}
            for level_name, level_percentage in CONSULTANT_LEVEL_DISTRIBUTION.items():
                journey = self._get_journey_for_level(level_name)
                progression_months = [Month.JUN, Month.DEC]
                
                # Combine global, office, and level-specific levers
                level_levers = office_levers.get('Consultant', {}).get(level_name, {})
                global_level_levers = global_levers.get('Consultant', {}).get(level_name, {})

                # Calculate progression rates for all 12 months
                progression_rates = {}
                for i in range(1, 13):
                    # Check if lever overrides the default progression rate
                    lever_progression = level_levers.get(f'progression_{i}', global_level_levers.get(f'progression_{i}', None))
                    
                    if lever_progression is not None:
                        # Use lever value
                        progression_rates[f'progression_{i}'] = lever_progression
                    else:
                        # Calculate default progression rate
                        if i in DEFAULT_RATES['progression']['evaluation_months']:
                            # Get the appropriate base rate for this level
                            progression_rate = 0.0
                            if level_name == 'C':
                                progression_rate = DEFAULT_RATES['progression']['base_rates']['C->SrC'] / 2  # Half-yearly to semi-annual
                            elif level_name == 'SrC':
                                progression_rate = DEFAULT_RATES['progression']['base_rates']['SrC->AM'] / 2
                            elif level_name == 'AM':
                                progression_rate = DEFAULT_RATES['progression']['base_rates']['AM->M'] / 2
                            elif level_name == 'M':
                                progression_rate = DEFAULT_RATES['progression']['base_rates']['M->SrM'] / 2
                            elif level_name == 'SrM':
                                progression_rate = DEFAULT_RATES['progression']['base_rates']['SrM->PiP'] / 2
                            else:
                                progression_rate = 0.10  # Default fallback for A/AC levels
                            
                            progression_rates[f'progression_{i}'] = progression_rate
                        else:
                            # Other months have no progression
                            progression_rates[f'progression_{i}'] = DEFAULT_RATES['progression']['non_evaluation_rate']

                # Create level with combined levers
                level = Level(
                    name=level_name,
                    journey=journey,
                    progression_months=progression_months,
                    # Apply progression rates
                    **progression_rates,
                    **{f'recruitment_{i}': level_levers.get(f'recruitment_{i}', global_level_levers.get(f'recruitment_{i}', 0.0)) for i in range(1, 13)},
                    **{f'churn_{i}': level_levers.get(f'churn_{i}', global_level_levers.get(f'churn_{i}', 0.0)) for i in range(1, 13)},
                    **{f'price_{i}': level_levers.get(f'price_{i}', global_level_levers.get(f'price_{i}', BASE_PRICING.get(office.name, {}).get(level_name, 0.0))) for i in range(1, 13)},
                    **{f'salary_{i}': level_levers.get(f'salary_{i}', global_level_levers.get(f'salary_{i}', BASE_SALARIES.get(office.name, {}).get(level_name, 0.0))) for i in range(1, 13)},
                    **{f'utr_{i}': level_levers.get(f'utr_{i}', global_level_levers.get(f'utr_{i}', 0.0)) for i in range(1, 13)},
                )
                
                # Set initial headcount
                consultant_fte = office.total_fte * ROLE_DISTRIBUTION.get('Consultant', 0.8)
                level_fte = int(consultant_fte * level_percentage)
                # Use a date 2 years before simulation start to ensure people have sufficient tenure
                initialization_date_str = "2023-01"
                for _ in range(level_fte):
                    level.add_new_hire(initialization_date_str, "Consultant", office.name)
                office.roles['Consultant'][level_name] = level
            
            # Initialize other roles
            for role_name in ['Sales', 'Recruitment', 'Operations']:
                role_fte = int(office.total_fte * ROLE_DISTRIBUTION.get(role_name, 0.05))
                role_data = RoleData()
                # Apply levers to flat roles
                role_levers = office_levers.get(role_name, {})
                global_role_levers = global_levers.get(role_name, {})
                for i in range(1, 13):
                    setattr(role_data, f'recruitment_{i}', role_levers.get(f'recruitment_{i}', global_role_levers.get(f'recruitment_{i}', 0.0)))
                    setattr(role_data, f'churn_{i}', role_levers.get(f'churn_{i}', global_role_levers.get(f'churn_{i}', 0.0)))
                
                # Use a date 2 years before simulation start to ensure people have sufficient tenure
                initialization_date_str = "2023-01"
                for _ in range(role_fte):
                    role_data.add_new_hire(initialization_date_str, role_name, office.name)
                office.roles[role_name] = role_data

    def _apply_levers_to_existing_offices(self, lever_plan: Optional[Dict] = None):
        """Applies a lever plan to an already initialized set of offices."""
        if not lever_plan or not self.offices:
            return
            
        global_levers = lever_plan.get('global', {})
        office_levers = lever_plan.get('offices', {})
        
        for office_name, office in self.offices.items():
            current_office_levers = office_levers.get(office_name, {})
            
            for role_name, role_data in office.roles.items():
                if isinstance(role_data, dict): # Leveled roles (Consultant, Sales, Recruitment)
                    for level_name, level in role_data.items():
                        level_levers = current_office_levers.get(role_name, {}).get(level_name, {})
                        global_level_levers = global_levers.get(role_name, {}).get(level_name, {})
                        
                        for i in range(1, 13):
                            # Prioritize office-specific, then global, then default
                            progression_rate = level_levers.get(f'progression_{i}', global_level_levers.get(f'progression_{i}', getattr(level, f'progression_{i}')))
                            recruitment_rate = level_levers.get(f'recruitment_{i}', global_level_levers.get(f'recruitment_{i}', getattr(level, f'recruitment_{i}')))
                            churn_rate = level_levers.get(f'churn_{i}', global_level_levers.get(f'churn_{i}', getattr(level, f'churn_{i}')))
                            price = level_levers.get(f'price_{i}', global_level_levers.get(f'price_{i}', getattr(level, f'price_{i}')))
                            salary = level_levers.get(f'salary_{i}', global_level_levers.get(f'salary_{i}', getattr(level, f'salary_{i}')))
                            utr = level_levers.get(f'utr_{i}', global_level_levers.get(f'utr_{i}', getattr(level, f'utr_{i}')))
                            
                            setattr(level, f'progression_{i}', progression_rate)
                            setattr(level, f'recruitment_{i}', recruitment_rate)
                            setattr(level, f'churn_{i}', churn_rate)
                            setattr(level, f'price_{i}', price)
                            setattr(level, f'salary_{i}', salary)
                            setattr(level, f'utr_{i}', utr)
                else: # Flat roles (Operations only)
                    flat_role_levers = current_office_levers.get(role_name, {})
                    global_flat_role_levers = global_levers.get(role_name, {})
                    for i in range(1, 13):
                        recruitment_rate = flat_role_levers.get(f'recruitment_{i}', global_flat_role_levers.get(f'recruitment_{i}', getattr(role_data, f'recruitment_{i}')))
                        churn_rate = flat_role_levers.get(f'churn_{i}', global_flat_role_levers.get(f'churn_{i}', getattr(role_data, f'churn_{i}')))
                        setattr(role_data, f'recruitment_{i}', recruitment_rate)
                        setattr(role_data, f'churn_{i}', churn_rate)
                        
    def get_offices_by_journey(self, journey: OfficeJourney) -> List[Office]:
        """Returns a list of offices matching a specific journey type"""
        return [o for o in self.offices.values() if o.journey == journey]

    def _get_monthly_attribute(self, obj, attribute_base: str, month: Month):
        """Gets a monthly attribute from an object (e.g., price_1, churn_5)"""
        return getattr(obj, f"{attribute_base}_{month.value}", 0.0)

    def _set_monthly_attribute(self, obj, attribute_base: str, month: Month, value):
        """Sets a monthly attribute on an object"""
        setattr(obj, f"{attribute_base}_{month.value}", value)
    
    def _recalculate_office_total_fte(self, office: Office) -> int:
        """
        Recalculate the total FTE for an office by summing all roles and levels.
        Updates the office.total_fte field and returns the calculated value.
        """
        total_fte = 0
        
        for role_name, role_data in office.roles.items():
            if isinstance(role_data, dict):  # Leveled roles (Consultant, Sales, Recruitment)
                for level_name, level in role_data.items():
                    total_fte += level.total
            else:  # Flat roles (Operations)
                total_fte += role_data.total
        
        # Update the office's total_fte field
        office.total_fte = total_fte
        return total_fte

    def run_simulation(self, start_year: int, start_month: int, end_year: int, end_month: int, 
                      price_increase: float = 0.0, salary_increase: float = 0.0, 
                      lever_plan: Optional[Dict] = None,
                      economic_params: Optional[EconomicParameters] = None) -> Dict:
        """
        Runs the simulation month by month.
        - Applies annual price and salary increases.
        - Calculates recruitment, churn, and progression for each level.
        - Updates the number of people in each level.
        - Stores monthly results.
        """
        print(f"[ENGINE] Starting simulation from {start_year}-{start_month} to {end_year}-{end_month}")
        # Use provided economic parameters or defaults
        econ_params = economic_params or EconomicParameters()
        # Re-initialize state based on config service before every run
        self.reinitialize_with_config()

        # Apply levers if a plan is provided
        if lever_plan:
            self._apply_levers_to_existing_offices(lever_plan)

        # Use a deterministic seed for random operations if provided
        random_seed = lever_plan.get('random_seed') if lever_plan else None
        if random_seed is not None:
            random.seed(random_seed)
            print(f"[ENGINE] Using deterministic random seed: {random_seed}")

        yearly_snapshots = {}
        monthly_office_metrics = {} # To store detailed monthly snapshots for each level
        simulation_start_date_str = f"{start_year}-{start_month}"
        # Initialize WorkforceManager
        workforce_manager = WorkforceManager(self.offices)
        # Main simulation loop
        for year in range(start_year, end_year + 1):
            # Apply annual price and salary increase
            if year > start_year:
                for office in self.offices.values():
                    for role in office.roles.values():
                        if isinstance(role, dict): # Leveled roles
                            for level in role.values():
                                for i in range(1, 13):
                                    current_price = getattr(level, f'price_{i}')
                                    setattr(level, f'price_{i}', current_price * (1 + price_increase))
                                    current_salary = getattr(level, f'salary_{i}')
                                    setattr(level, f'salary_{i}', current_salary * (1 + salary_increase))
                        else: # Flat roles
                             for i in range(1, 13):
                                current_salary = getattr(role, f'salary_{i}')
                                setattr(role, f'salary_{i}', current_salary * (1 + salary_increase))

            for month in range(1, 13):
                if (year == start_year and month < start_month) or \
                   (year == end_year and month > end_month):
                    continue
                current_date_str = f"{year}-{month}"
                print(f"[ENGINE] Simulating: {current_date_str}")
                total_system_fte_before = sum(o.total_fte for o in self.offices.values())
                # Delegate all workforce logic to WorkforceManager
                workforce_manager.process_month(year, month, current_date_str, monthly_office_metrics)
                # Store monthly metrics for analysis
                monthly_results = self.monthly_results.get(current_date_str, {})
                if not monthly_results:
                    self.monthly_results[current_date_str] = {}
                total_system_fte_after = sum(o.total_fte for o in self.offices.values())
                for office in self.offices.values():
                    if office.name not in self.monthly_results[current_date_str]:
                        self.monthly_results[current_date_str][office.name] = {}
                    self.monthly_results[current_date_str][office.name]['total_fte'] = office.total_fte
                print(f"[ENGINE] {current_date_str}: Total FTE Before: {total_system_fte_before:.2f}, After: {total_system_fte_after:.2f}, Change: {total_system_fte_after - total_system_fte_before:.2f}")
            # End of month loop
            
            # After completing all months for the year, recalculate total_fte for each office
            print(f"[ENGINE] Recalculating total FTE for all offices after year {year}")
            for office_name, office in self.offices.items():
                old_total_fte = office.total_fte
                new_total_fte = self._recalculate_office_total_fte(office)
                if old_total_fte != new_total_fte:
                    print(f"[ENGINE] {office_name}: FTE corrected from {old_total_fte} to {new_total_fte}")
            
            # Store a snapshot of the offices at the end of the year
            office_snapshots = {}
            for office_name, office in self.offices.items():
                office_snapshots[office_name] = {
                    'total_fte': office.total_fte,
                    'name': office.name,
                    'journey': office.journey.value,
                    'levels': self._get_office_level_snapshot(office, monthly_office_metrics, simulation_start_date_str, f"{year}-12")
                }
            yearly_snapshots[str(year)] = office_snapshots
            
            # Log detailed yearly results
            self._log_yearly_results(year, yearly_snapshots, monthly_office_metrics, econ_params)
        
        # End of month loop
        
        # Structure results at the end of the simulation
        simulation_results = {
            'start_year': start_year,
            'end_year': end_year,
            'years': {}
        }

        # Create the complex structure that the frontend expects
        print(f"[ENGINE] Creating complex data structure for frontend compatibility...")
        try:
            yearly_results = self._structure_yearly_results(
                yearly_snapshots, 
                monthly_office_metrics, 
                start_year, 
                end_year,
                econ_params
            )
            simulation_results['years'] = yearly_results
            print(f"[ENGINE] ✅ Created complex structure: {len(yearly_results)} years, {len(self.offices)} offices")
            
        except Exception as e:
            print(f"[ENGINE] ❌ Error creating complex structure: {e}")
            import traceback
            traceback.print_exc()
            # Create minimal fallback
            simulation_results['years'] = {
                str(year): {
                    'offices': {},
                    'total_fte': 0,
                    'total_revenue': 0.0,
                    'total_salary_costs': 0.0,
                    'total_employment_costs': 0.0,
                    'total_other_expenses': 0.0,
                    'total_costs': 0.0,
                    'ebitda': 0.0,
                    'margin': 0.0,
                    'avg_hourly_rate': 0.0
                } for year in range(start_year, end_year + 1)
            }

        # Storing results in the instance
        self.simulation_results = simulation_results
        
        simulation_duration_months = ((end_year - start_year) * 12) + (end_month - start_month) + 1

        # Note: KPIs will be calculated separately by the KPI service
        # This maintains separation of concerns - simulation engine handles workforce dynamics only
        simulation_results['kpis'] = None

        print("[ENGINE] Simulation finished.")
        return simulation_results
    
    def _get_office_level_snapshot(self, office: Office, monthly_office_metrics: Dict, start_date_str: str, end_date_str: str) -> Dict[str, Any]:
        """
        Gathers and structures the current state data for each level in an office
        for KPI calculations. Converts the monthly_office_metrics structure into arrays.
        """
        level_snapshots = {}
        
        # Extract all monthly data for this office and convert to arrays
        office_monthly_data = monthly_office_metrics.get(office.name, {})
        
        for role_name, role_data in office.roles.items():
            if isinstance(role_data, dict): # Leveled roles
                level_snapshots[role_name] = {}
                for level_name, level_data in role_data.items():
                    # Collect all monthly data for this level into an array
                    monthly_array = []
                    for date_str in sorted(office_monthly_data.keys()):
                        level_data = office_monthly_data[date_str].get(role_name, {}).get(level_name, {})
                        if level_data:
                            # Transform the structure for KPI service AND preserve movement data
                            monthly_array.append({
                                'total': level_data.get('total_fte', 0),
                                'price': level_data.get('price', 0),
                                'salary': level_data.get('salary', 0),
                                'utr': level_data.get('utr', 0.85),
                                'recruited': level_data.get('recruited', 0),
                                'churned': level_data.get('churned', 0),
                                'progressed_in': level_data.get('progressed_in', 0),
                                'progressed_out': level_data.get('progressed_out', 0)
                            })
                    level_snapshots[role_name][level_name] = monthly_array
            else: # Flat roles (e.g., Operations)
                # Collect all monthly data for this flat role into an array
                monthly_array = []
                for date_str in sorted(office_monthly_data.keys()):
                    role_monthly_data = office_monthly_data[date_str].get(role_name, {})
                    if role_monthly_data:
                        monthly_array.append({
                            'total': role_monthly_data.get('total_fte', 0),
                            'salary': 40000.0,  # Default salary for flat roles
                            'recruited': role_monthly_data.get('recruited', 0),
                            'churned': role_monthly_data.get('churned', 0)
                        })
                level_snapshots[role_name] = monthly_array
        
        return level_snapshots

    def _structure_yearly_results(self, yearly_snapshots: Dict, monthly_office_metrics: Dict, start_year: int, end_year: int, economic_params: EconomicParameters) -> Dict[str, Any]:
        """
        Structures the final results dictionary with detailed monthly level data for each year.
        """
        yearly_results = {}
        
        try:
            for year in range(start_year, end_year + 1):
                year_str = str(year)
                
                # This will contain the structured data for all offices for this year
                yearly_offices_data = {}
                
                # Use the offices state from the end of the year snapshot
                if not self.offices:
                    print(f"[ENGINE ERROR] No offices found when structuring results for year {year}")
                    continue

                # Use the yearly snapshots if available, otherwise fall back to current office state
                if year_str in yearly_snapshots:
                    yearly_offices_data = yearly_snapshots[year_str]
                else:
                    # Fallback: create from current office state
                    for office_name, office in self.offices.items():
                        try:
                            office_levels = self._get_office_level_snapshot(
                                office, 
                                monthly_office_metrics, 
                                f"{year}-01", 
                                f"{year}-12"
                            )
                            
                            yearly_offices_data[office_name] = {
                                'total_fte': office.total_fte, # End of simulation FTE
                                'name': office.name,
                                'journey': office.journey.value,
                                'levels': office_levels
                            }
                        except Exception as e:
                            print(f"[ENGINE ERROR] Failed to get snapshot for office {office_name}: {e}")
                            # Provide minimal structure if snapshot fails
                            yearly_offices_data[office_name] = {
                                'total_fte': office.total_fte,
                                'name': office.name,
                                'journey': office.journey.value,
                                'levels': {}
                            }
                
                # First create the basic year structure
                yearly_results[year_str] = {
                    'offices': yearly_offices_data,
                    'total_fte': sum(office_data['total_fte'] for office_data in yearly_offices_data.values())
                }
                
                # Then calculate complete year-specific KPIs using KPI service
                year_kpis = self._calculate_complete_year_kpis(yearly_results, year_str, economic_params)
                
                # Add the complete KPI structure to the year
                yearly_results[year_str]['kpis'] = year_kpis
                
        except Exception as e:
            print(f"[ENGINE ERROR] Failed to structure yearly results: {e}")
            import traceback
            traceback.print_exc()
            # Return minimal structure to prevent total failure
            for year in range(start_year, end_year + 1):
                year_str = str(year)
                yearly_results[year_str] = {
                    'offices': {},
                    'total_fte': 0,
                    'kpis': {
                        'financial': {
                            'net_sales': 0.0,
                            'net_sales_baseline': 0.0,
                            'ebitda': 0.0,
                            'ebitda_baseline': 0.0,
                            'margin': 0.0,
                            'margin_baseline': 0.0,
                            'avg_hourly_rate': 0.0,
                            'avg_hourly_rate_baseline': 0.0,
                            'total_salary_costs': 0.0,
                            'total_salary_costs_baseline': 0.0
                        },
                        'growth': {
                            'total_fte': 0,
                            'baseline_total_fte': 0,
                            'current_total_fte': 0,
                            'non_debit_ratio': 0.0,
                            'non_debit_ratio_baseline': 0.0
                        },
                        'journeys': {
                            'journey_totals': {},
                            'journey_percentages': {},
                            'journey_totals_baseline': {},
                            'journey_percentages_baseline': {}
                        }
                    }
                }
            
        return yearly_results

    def _calculate_complete_year_kpis(self, yearly_results: Dict[str, Any], target_year: str, economic_params: EconomicParameters) -> Dict[str, Any]:
        """Calculate complete year-specific KPIs including financial, growth, and journey metrics"""
        try:
            # Create a temporary simulation results structure for the KPI service
            temp_simulation_results = {
                'years': yearly_results
            }
            
            # Use the existing KPI service
            kpi_service = KPIService(economic_params=economic_params)
            year_kpis = kpi_service.calculate_kpis_for_year(
                temp_simulation_results,
                target_year,
                simulation_duration_months=12,  # Always use 12 months for annual calculations
                economic_params=economic_params
            )
            
            # Convert dataclasses to dicts for JSON serialization
            def to_dict(data):
                if hasattr(data, '__dataclass_fields__'):
                    return {k: to_dict(getattr(data, k)) for k in data.__dataclass_fields__}
                elif isinstance(data, dict):
                    return {k: to_dict(v) for k, v in data.items()}
                elif isinstance(data, list):
                    return [to_dict(i) for i in data]
                else:
                    return data
            
            # Return the complete KPI structure
            return to_dict(year_kpis)
            
        except Exception as e:
            print(f"[ENGINE ERROR] Failed to calculate complete year KPIs: {e}")
            import traceback
            traceback.print_exc()
            # Return zero values as fallback
            return {
                'financial': {
                    'net_sales': 0.0,
                    'net_sales_baseline': 0.0,
                    'ebitda': 0.0,
                    'ebitda_baseline': 0.0,
                    'margin': 0.0,
                    'margin_baseline': 0.0,
                    'avg_hourly_rate': 0.0,
                    'avg_hourly_rate_baseline': 0.0,
                    'total_salary_costs': 0.0,
                    'total_salary_costs_baseline': 0.0
                },
                'growth': {
                    'total_fte': 0,
                    'baseline_total_fte': 0,
                    'current_total_fte': 0,
                    'non_debit_ratio': 0.0,
                    'non_debit_ratio_baseline': 0.0
                },
                'journeys': {
                    'journey_totals': {},
                    'journey_percentages': {},
                    'journey_totals_baseline': {},
                    'journey_percentages_baseline': {}
                }
            }
        
    def get_simulation_results(self) -> Optional[Dict[str, Any]]:
        """Return the latest simulation results"""
        return self.simulation_results

    def calculate_kpis_for_simulation(
        self, 
        results: Dict[str, Any], 
        simulation_duration_months: int,
        unplanned_absence: float = 0.05,
        other_expense: float = 100000.0
    ) -> Dict[str, Any]:
        """Calculate KPIs using the KPI service"""
        kpi_service = KPIService()
        
        # Convert dataclasses to dicts for JSON serialization
        all_kpis_dataclass = kpi_service.calculate_all_kpis(
            results,
            simulation_duration_months,
            unplanned_absence,
            other_expense
        )
        
        def to_dict(data):
            if hasattr(data, '__dataclass_fields__'):
                return {k: to_dict(getattr(data, k)) for k in data.__dataclass_fields__}
            elif isinstance(data, dict):
                return {k: to_dict(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [to_dict(i) for i in data]
            else:
                return data

        return to_dict(all_kpis_dataclass)

    def _get_next_level_name(self, current_level: str) -> Optional[str]:
        """Get the name of the next level in the progression path"""
        progression_path = self.level_order
        try:
            current_index = progression_path.index(current_level)
            if current_index + 1 < len(progression_path):
                return progression_path[current_index + 1]
            return None
        except ValueError:
            return None

    def _get_next_level(self, current_level: str, role_name: str, office_roles: Dict[str, Dict[str, 'Level'] or 'RoleData']) -> Optional['Level']:
        """Get the next Level object in the progression path"""
        next_level_name = self._get_next_level_name(current_level)
        if next_level_name and role_name in office_roles and isinstance(office_roles[role_name], dict):
            return office_roles[role_name].get(next_level_name)
        return None

    def _log_yearly_results(self, year: int, yearly_snapshots: Dict, monthly_office_metrics: Dict, economic_params: EconomicParameters):
        year_str = str(year)
        if year_str not in yearly_snapshots:
            self.yearly_logger.info("No data available for this year")
            return
        year_data = yearly_snapshots[year_str]
        log_office_aggregates_per_year(self.yearly_logger, year, year_data, economic_params)
        # Remove or comment out detailed per-office logging
        # for office_name, office_data in year_data.items():
        #     self._log_office_kpis(office_name, office_data, economic_params)
        # self._log_system_kpis(year_data, economic_params)

    def _log_office_kpis(self, office_name: str, office_data: Dict, economic_params: EconomicParameters):
        log_office_kpis(self.yearly_logger, office_name, office_data, economic_params)

    def _log_system_kpis(self, year_data: Dict, economic_params: EconomicParameters):
        log_system_kpis(self.yearly_logger, year_data, economic_params)

def calculate_configuration_checksum(offices: Dict[str, Office]) -> str:
    """
    Calculates a checksum for the initial office configuration to detect changes.
    This helps in deciding whether to re-run a baseline simulation.
    """
    # Create a deep copy to avoid modifying the original data
    offices_copy = deepcopy(offices)

    # Convert the configuration to a JSON string for hashing
    # Using a custom serializer to handle dataclasses
    def json_default(o):
        if hasattr(o, '__dict__'):
            return o.__dict__
        if isinstance(o, (datetime,)):
            return o.isoformat()
        if isinstance(o, Enum):
            return o.value
        raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

    config_string = json.dumps(
        {name: office for name, office in offices_copy.items()}, 
        sort_keys=True, 
        default=json_default
    )

    return hashlib.md5(config_string.encode('utf-8')).hexdigest()


def validate_configuration_completeness(offices: Dict[str, Office]) -> Dict[str, Any]:
    """
    Validates that the configuration for all offices, roles, and levels is complete.
    Checks for missing rates, salaries, prices, etc. for all 12 months.
    """
    issues = {}
    
    for office_name, office in offices.items():
        office_issues = {}
        for role_name, role_data in office.roles.items():
            role_issues = {}
            if isinstance(role_data, dict): # Leveled roles
                for level_name, level in role_data.items():
                    level_issues = []
                    for i in range(1, 13):
                        for key in ['progression', 'recruitment', 'churn', 'price', 'salary', 'utr']:
                            if not hasattr(level, f'{key}_{i}'):
                                level_issues.append(f"Missing '{key}' for month {i}")
                    if level_issues:
                        role_issues[level_name] = level_issues
            else: # Flat roles
                flat_role_issues = []
                for i in range(1, 13):
                    for key in ['recruitment', 'churn']:
                        if not hasattr(role_data, f'{key}_{i}'):
                            flat_role_issues.append(f"Missing '{key}' for month {i}")
                if flat_role_issues:
                    role_issues['base'] = flat_role_issues
            
            if role_issues:
                office_issues[role_name] = role_issues
        
        if office_issues:
            issues[office_name] = office_issues
            
    return {
        'is_complete': not issues,
        'issues': issues
    }