from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
import sys
import os
import uuid
import random

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
from backend.src.services.kpi_service import KPIService

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
    NEW = "New Office"          # 0-25 FTE
    EMERGING = "Emerging Office"  # 25-200 FTE
    ESTABLISHED = "Established Office"  # 200-500 FTE
    MATURE = "Mature Office"    # 500+ FTE

@dataclass
class Person:
    """Represents an individual employee"""
    id: str
    career_start: str      # "YYYY-MM" when they joined the company
    current_level: str     # "A", "AC", "C", etc.
    level_start: str       # "YYYY-MM" when they joined current level
    role: str              # "Consultant", "Sales", "Recruitment"
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
    
    def is_eligible_for_progression(self, current_date: str) -> bool:
        """Check if person is eligible for progression (6+ months on current level)"""
        return self.get_level_tenure_months(current_date) >= 6

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
        """Get people eligible for progression (6+ months on current level)"""
        return [p for p in self.people if p.is_eligible_for_progression(current_date)]
    
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
        """Apply progression to eligible people, return promoted people"""
        eligible = self.get_eligible_for_progression(current_date)
        
        if progression_count <= 0 or len(eligible) == 0:
            return []
        
        progression_count = min(progression_count, len(eligible))
        # Use oldest on level first (FIFO)
        eligible.sort(key=lambda p: p.level_start)
        promoted = eligible[:progression_count]
        
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
            journey = OfficeJourney.NEW
        return cls(
            name=name,
            total_fte=total_fte,
            journey=journey,
            roles={}
        )

class SimulationEngine:
    def __init__(self):
        self.offices: Dict[str, Office] = {}
        self.kpi_service = KPIService()
        self._last_simulation_results: Optional[Dict[str, Any]] = None
        self._initialize_offices()
        self._initialize_roles()

    def _initialize_offices(self):
        """Initialize offices with their journeys based on real FTE data"""
        for office_name, fte in OFFICE_HEADCOUNT.items():
            if fte >= 500:
                journey = OfficeJourney.MATURE
            elif fte >= 200:
                journey = OfficeJourney.ESTABLISHED
            elif fte >= 25:
                journey = OfficeJourney.EMERGING
            else:
                journey = OfficeJourney.NEW
            
            self.offices[office_name] = Office(
                name=office_name,
                total_fte=fte,
                journey=journey,
                roles={}
            )

    def _initialize_roles(self):
        """Initialize roles with real headcount data"""
        print("[INFO] Initializing roles with real headcount data")
        print(f"[DEBUG] DEFAULT_RATES churn: {DEFAULT_RATES['churn']}")
        print(f"[DEBUG] DEFAULT_RATES Consultant A recruitment: {DEFAULT_RATES['recruitment']['Consultant']['A']}")
        print(f"[DEBUG] DEFAULT_RATES Operations recruitment: {DEFAULT_RATES['recruitment']['Operations']}")
        
        for office_name, office in self.offices.items():
            office.roles["Consultant"] = {}
            office.roles["Sales"] = {}
            office.roles["Recruitment"] = {}
            
            # Get actual office data
            office_data = ACTUAL_OFFICE_LEVEL_DATA.get(office_name, {})
            
            # Process each role with levels
            for role_name in ["Consultant", "Sales", "Recruitment"]:
                role_levels = office_data.get(role_name, {})
                
                for level_name, level_fte in role_levels.items():
                    if level_fte > 0:  # Only create levels with actual FTE
                        # Use office and level to get base price and salary
                        base_prices = BASE_PRICING.get(office_name, BASE_PRICING['Stockholm'])
                        base_salaries = BASE_SALARIES.get(office_name, BASE_SALARIES['Stockholm'])
                        price = base_prices.get(level_name, 0.0)
                        salary = base_salaries.get(level_name, 0.0)
                        
                        # Determine journey and progression months for this level
                        level_journey = Journey.JOURNEY_1  # default
                        for journey_name, levels in JOURNEY_CLASSIFICATION.items():
                            if level_name in levels:
                                if journey_name == 'Journey 1':
                                    level_journey = Journey.JOURNEY_1
                                elif journey_name == 'Journey 2':
                                    level_journey = Journey.JOURNEY_2
                                elif journey_name == 'Journey 3':
                                    level_journey = Journey.JOURNEY_3
                                elif journey_name == 'Journey 4':
                                    level_journey = Journey.JOURNEY_4
                                break
                        
                        # Set progression months based on level
                        if level_name in ['M', 'SrM', 'PiP']:
                            # M+ levels only progress in November
                            progression_months = [Month.NOV]
                        else:
                            # A-AM levels progress in May and November
                            progression_months = [Month.MAY, Month.NOV]
                        
                        # Create level with monthly fields
                        office.roles[role_name][level_name] = Level(
                            name=level_name,
                            journey=level_journey,
                            progression_months=progression_months,
                            progression_1=0.0, progression_2=0.0, progression_3=0.0, progression_4=0.0, progression_5=0.0, progression_6=0.0, progression_7=0.0, progression_8=0.0, progression_9=0.0, progression_10=0.0, progression_11=0.0, progression_12=0.0,
                            recruitment_1=0.0, recruitment_2=0.0, recruitment_3=0.0, recruitment_4=0.0, recruitment_5=0.0, recruitment_6=0.0, recruitment_7=0.0, recruitment_8=0.0, recruitment_9=0.0, recruitment_10=0.0, recruitment_11=0.0, recruitment_12=0.0,
                            churn_1=0.0, churn_2=0.0, churn_3=0.0, churn_4=0.0, churn_5=0.0, churn_6=0.0, churn_7=0.0, churn_8=0.0, churn_9=0.0, churn_10=0.0, churn_11=0.0, churn_12=0.0,
                            utr_1=1.0, utr_2=1.0, utr_3=1.0, utr_4=1.0, utr_5=1.0, utr_6=1.0, utr_7=1.0, utr_8=1.0, utr_9=1.0, utr_10=1.0, utr_11=1.0, utr_12=1.0,
                            price_1=price, price_2=price, price_3=price, price_4=price, price_5=price, price_6=price, price_7=price, price_8=price, price_9=price, price_10=price, price_11=price, price_12=price,
                            salary_1=salary, salary_2=salary, salary_3=salary, salary_4=salary, salary_5=salary, salary_6=salary, salary_7=salary, salary_8=salary, salary_9=salary, salary_10=salary, salary_11=salary, salary_12=salary
                        )
                        
                        # Create individual Person objects for existing headcount
                        # Assume existing people have been there 12+ months (eligible for progression)
                        base_date = "2023-01"  # 12+ months ago from 2024 simulation start
                        for i in range(level_fte):
                            person = Person(
                                id=str(uuid.uuid4()),
                                career_start=base_date,
                                current_level=level_name,
                                level_start=base_date,
                                role=role_name,
                                office=office_name
                            )
                            office.roles[role_name][level_name].people.append(person)
                        
                        # Set default rates with monthly variations
                        for month in range(1, 13):
                            # Add slight monthly increase (0.25% per month)
                            monthly_price = price * (1 + 0.0025 * (month - 1))
                            monthly_salary = salary * (1 + 0.0025 * (month - 1))
                            setattr(office.roles[role_name][level_name], f'price_{month}', monthly_price)
                            setattr(office.roles[role_name][level_name], f'salary_{month}', monthly_salary)
                            # Get recruitment rate for this role and level
                            if role_name in DEFAULT_RATES['recruitment'] and isinstance(DEFAULT_RATES['recruitment'][role_name], dict):
                                recruitment_rate = DEFAULT_RATES['recruitment'][role_name].get(level_name, 0.01)
                            else:
                                recruitment_rate = 0.01  # Default fallback
                            setattr(office.roles[role_name][level_name], f'recruitment_{month}', recruitment_rate)
                            # Get churn rate for this role and level
                            if role_name in DEFAULT_RATES['churn'] and isinstance(DEFAULT_RATES['churn'][role_name], dict):
                                churn_rate = DEFAULT_RATES['churn'][role_name].get(level_name, 0.014)
                            elif role_name in DEFAULT_RATES['churn']:
                                churn_rate = DEFAULT_RATES['churn'][role_name]
                            else:
                                churn_rate = 0.014  # Default fallback
                            setattr(office.roles[role_name][level_name], f'churn_{month}', churn_rate)
                            
                            # Set progression rate based on level and month
                            if month in DEFAULT_RATES['progression']['evaluation_months']:
                                if level_name in ['M', 'SrM', 'PiP']:
                                    # M+ levels only progress in November
                                    if month == 11:
                                        progression_rate = DEFAULT_RATES['progression']['M_plus_rate']
                                    else:
                                        progression_rate = DEFAULT_RATES['progression']['non_evaluation_rate']
                                else:
                                    # A-AM levels progress in May and November
                                    progression_rate = DEFAULT_RATES['progression']['A_AM_rate']
                            else:
                                progression_rate = DEFAULT_RATES['progression']['non_evaluation_rate']
                            
                            setattr(office.roles[role_name][level_name], f'progression_{month}', progression_rate)
                            setattr(office.roles[role_name][level_name], f'utr_{month}', DEFAULT_RATES['utr'])
            
            # Initialize Operations role using real data
            operations_fte = office_data.get('Operations', 0)
            if operations_fte > 0:
                base_prices = BASE_PRICING.get(office_name, BASE_PRICING['Stockholm'])
                base_salaries = BASE_SALARIES.get(office_name, BASE_SALARIES['Stockholm'])
                op_price = base_prices.get('Operations', 80.0)  # Default fallback
                op_salary = base_salaries.get('Operations', 40000.0)  # Default fallback
                
                # Get Operations recruitment rate
                operations_recruitment = DEFAULT_RATES['recruitment'].get('Operations', 0.008)
                
                # Get Operations churn rate
                operations_churn = DEFAULT_RATES['churn'].get('Operations', 0.014)
                
                office.roles["Operations"] = RoleData(
                    recruitment_1=operations_recruitment, recruitment_2=operations_recruitment, recruitment_3=operations_recruitment, recruitment_4=operations_recruitment, recruitment_5=operations_recruitment, recruitment_6=operations_recruitment, recruitment_7=operations_recruitment, recruitment_8=operations_recruitment, recruitment_9=operations_recruitment, recruitment_10=operations_recruitment, recruitment_11=operations_recruitment, recruitment_12=operations_recruitment,
                    churn_1=operations_churn, churn_2=operations_churn, churn_3=operations_churn, churn_4=operations_churn, churn_5=operations_churn, churn_6=operations_churn, churn_7=operations_churn, churn_8=operations_churn, churn_9=operations_churn, churn_10=operations_churn, churn_11=operations_churn, churn_12=operations_churn,
                    price_1=op_price, price_2=op_price, price_3=op_price, price_4=op_price, price_5=op_price, price_6=op_price, price_7=op_price, price_8=op_price, price_9=op_price, price_10=op_price, price_11=op_price, price_12=op_price,
                    salary_1=op_salary, salary_2=op_salary, salary_3=op_salary, salary_4=op_salary, salary_5=op_salary, salary_6=op_salary,
                    utr_1=DEFAULT_RATES['utr'], utr_2=DEFAULT_RATES['utr'], utr_3=DEFAULT_RATES['utr'], utr_4=DEFAULT_RATES['utr'], utr_5=DEFAULT_RATES['utr'], utr_6=DEFAULT_RATES['utr'], utr_7=DEFAULT_RATES['utr'], utr_8=DEFAULT_RATES['utr'], utr_9=DEFAULT_RATES['utr'], utr_10=DEFAULT_RATES['utr'], utr_11=DEFAULT_RATES['utr'], utr_12=DEFAULT_RATES['utr']
                )
                
                # Create individual Person objects for existing Operations headcount
                base_date = "2023-01"  # 12+ months ago from 2024 simulation start
                for i in range(operations_fte):
                    person = Person(
                        id=str(uuid.uuid4()),
                        career_start=base_date,
                        current_level="Operations",
                        level_start=base_date,
                        role="Operations",
                        office=office_name
                    )
                    office.roles["Operations"].people.append(person)

    def get_offices_by_journey(self, journey: OfficeJourney) -> List[Office]:
        """Get all offices in a specific journey"""
        return [office for office in self.offices.values() if office.journey == journey]
    
    def _get_monthly_attribute(self, obj, attribute_base: str, month: Month):
        """Helper function to get the correct monthly attribute"""
        return getattr(obj, f"{attribute_base}_{month.value}")
    
    def _set_monthly_attribute(self, obj, attribute_base: str, month: Month, value):
        """Helper function to set the correct monthly attribute"""
        setattr(obj, f"{attribute_base}_{month.value}", value)
    
    def run_simulation(self, start_year: int, start_month: int, end_year: int, end_month: int, 
                      price_increase: float = 0.0, salary_increase: float = 0.0, 
                      lever_plan: Optional[Dict] = None) -> Dict:
        """Run simulation from start_month to end_month"""
        print(f"[DEBUG] Running simulation from {start_year}-{start_month} to {end_year}-{end_month}")
        print(f"[DEBUG] Price increase: {price_increase}, Salary increase: {salary_increase}")
        print(f"[DEBUG] Lever plan provided: {lever_plan is not None}")
        if lever_plan:
            print(f"[DEBUG] Lever plan offices: {list(lever_plan.keys())}")
            if 'Stockholm' in lever_plan:
                print(f"[DEBUG] Stockholm lever roles: {list(lever_plan['Stockholm'].keys())}")
                if 'Consultant' in lever_plan['Stockholm']:
                    print(f"[DEBUG] Stockholm Consultant lever levels: {list(lever_plan['Stockholm']['Consultant'].keys())}")
                    if 'A' in lever_plan['Stockholm']['Consultant']:
                        a_levers = lever_plan['Stockholm']['Consultant']['A']
                        print(f"[DEBUG] Stockholm Consultant A levers: {a_levers}")
        
        # Convert month numbers to Month enum
        start_month_enum = Month(start_month)
        end_month_enum = Month(end_month)
        
        # Initialize results structure with years
        results = {
            "years": {}
        }
        
        # Simulation loop through months
        current_year = start_year
        current_month = start_month_enum

        while (current_year < end_year or 
               (current_year == end_year and current_month.value <= end_month_enum.value)):
            
            print(f"[DEBUG] Period: {current_year} {current_month.name}")
            
            # Initialize year if not exists
            if str(current_year) not in results["years"]:
                results["years"][str(current_year)] = {
                    "months": [],
                    "offices": {},
                    "summary": {
                        "total_fte": 0,
                        "total_revenue": 0.0,
                        "total_costs": 0.0,
                        "total_profit": 0.0,
                        "average_margin": 0.0,
                        "growth_rate": 0.0
                    }
                }
            
            # Record period
            results["years"][str(current_year)]["months"].append(current_month.name)
            
            # Current month key for individual tracking
            current_month_key = f"{current_year}-{current_month.value:02d}"
            
            # Process each office
            for office_name, office in self.offices.items():
                # Initialize office in year if not exists
                if office_name not in results["years"][str(current_year)]["offices"]:
                    results["years"][str(current_year)]["offices"][office_name] = {
                        "levels": {},
                        "metrics": [],
                        "operations": [],
                        "journeys": {
                            "Journey 1": [],
                            "Journey 2": [],
                            "Journey 3": [],
                            "Journey 4": []
                        }
                    }
                    # Initialize level results for both roles with levels and flat roles
                    for role_name, role_data in office.roles.items():
                        if isinstance(role_data, dict):
                            results["years"][str(current_year)]["offices"][office_name]["levels"][role_name] = {}
                            for level_name in role_data:
                                results["years"][str(current_year)]["offices"][office_name]["levels"][role_name][level_name] = []
                        else:
                            results["years"][str(current_year)]["offices"][office_name]["levels"][role_name] = []
                
                office_results = results["years"][str(current_year)]["offices"][office_name]
                previous_total = sum(getattr(level, 'total', 0) for role_data in office.roles.values() 
                                   for level in (role_data.values() if isinstance(role_data, dict) else [role_data]))
                
                # Apply levers and simulate roles with levels
                for role_name, role_data in office.roles.items():
                    if isinstance(role_data, dict):  # Roles with levels
                        
                        # PHASE 1: Recruitment for all levels first
                        for level_name, level in role_data.items():
                            # Check for levers
                            levers = {}
                            if lever_plan and office_name in lever_plan and role_name in lever_plan[office_name]:
                                levers = lever_plan[office_name][role_name].get(level_name, {})
                            
                            # Apply recruitment
                            recruitment_key = f'recruitment_{current_month.value}'
                            default_recruitment = getattr(level, recruitment_key)
                            lever_recruitment = levers.get(recruitment_key) if levers else None
                            recruitment_rate = lever_recruitment if lever_recruitment is not None else default_recruitment
                            
                            if level.total == 0 and recruitment_rate > 0:
                                new_recruits = max(1, int(recruitment_rate * 10))
                            else:
                                # Deterministic fractional accumulation
                                exact_recruits = level.total * recruitment_rate
                                level.fractional_recruitment += exact_recruits
                                new_recruits = int(level.fractional_recruitment)
                                level.fractional_recruitment -= new_recruits
                            
                            # Debug Oslo A level
                            if office_name == 'Oslo' and role_name == 'Consultant' and level_name == 'A':
                                print(f"[DEBUG] Oslo A recruitment: {level.total} * {recruitment_rate} = {new_recruits}")
                            
                            # Add new hires
                            for _ in range(new_recruits):
                                level.add_new_hire(current_month_key, role_name, office_name)
                        
                        # PHASE 2: Churn for all levels
                        for level_name, level in role_data.items():
                            # Check for levers
                            levers = {}
                            if lever_plan and office_name in lever_plan and role_name in lever_plan[office_name]:
                                levers = lever_plan[office_name][role_name].get(level_name, {})
                            
                            # Apply churn
                            churn_key = f'churn_{current_month.value}'
                            default_churn = getattr(level, churn_key)
                            lever_churn = levers.get(churn_key) if levers else None
                            churn_rate = lever_churn if lever_churn is not None else default_churn
                            
                            # Deterministic fractional accumulation for churn
                            exact_churn = level.total * churn_rate
                            level.fractional_churn += exact_churn
                            churn_count = int(level.fractional_churn)
                            level.fractional_churn -= churn_count
                            
                            # Debug Oslo A level
                            if office_name == 'Oslo' and role_name == 'Consultant' and level_name == 'A':
                                print(f"[DEBUG] Oslo A churn: {level.total} * {churn_rate} = {churn_count}")
                            
                            churned_people = level.apply_churn(churn_count)
                        
                        # PHASE 3: Calculate all progressions (but don't apply yet)
                        progression_plan = {}
                        for level_name, level in role_data.items():
                            # Check for levers
                            levers = {}
                            if lever_plan and office_name in lever_plan and role_name in lever_plan[office_name]:
                                levers = lever_plan[office_name][role_name].get(level_name, {})
                            
                            # Calculate progression based on eligible people (6+ months on level)
                            progression_key = f'progression_{current_month.value}'
                            if current_month in level.progression_months:
                                progression_rate = levers.get(progression_key) if levers.get(progression_key) is not None else getattr(level, progression_key)
                            else:
                                progression_rate = 0.0
                            
                            if progression_rate > 0:
                                eligible_people = level.get_eligible_for_progression(current_month_key)
                                progressed = int(len(eligible_people) * progression_rate)
                                if progressed > 0:
                                    next_level_name = self._get_next_level_name(level_name)
                                    if next_level_name and next_level_name in role_data:
                                        progression_plan[level_name] = {
                                            'to_level': next_level_name,
                                            'count': progressed
                                        }
                        
                        # PHASE 4: Apply all progressions simultaneously
                        for from_level_name, move in progression_plan.items():
                            from_level = role_data[from_level_name]
                            to_level = role_data[move['to_level']]
                            
                            # Remove people from source level
                            promoted_people = from_level.apply_progression(move['count'], current_month_key)
                            
                            # Add to target level
                            for person in promoted_people:
                                to_level.add_promotion(person, current_month_key)
                        
                        # Store level results
                        for level_name, level in role_data.items():
                            office_results['levels'][role_name][level_name].append({
                                'total': level.total,
                                'price': getattr(level, f'price_{current_month.value}'),
                                'salary': getattr(level, f'salary_{current_month.value}')
                            })
                    else:
                        # Flat roles (Operations)
                        level = role_data
                        # Check for levers
                        levers = {}
                        if lever_plan and office_name in lever_plan and role_name in lever_plan[office_name]:
                            levers = lever_plan[office_name][role_name]
                        
                        # PHASE 1: Recruitment
                        recruitment_key = f'recruitment_{current_month.value}'
                        default_recruitment = getattr(level, recruitment_key)
                        lever_recruitment = levers.get(recruitment_key) if levers else None
                        recruitment_rate = lever_recruitment if lever_recruitment is not None else default_recruitment
                        
                        if level.total == 0 and recruitment_rate > 0:
                            new_recruits = max(1, int(recruitment_rate * 10))
                        else:
                            # Deterministic fractional accumulation
                            exact_recruits = level.total * recruitment_rate
                            level.fractional_recruitment += exact_recruits
                            new_recruits = int(level.fractional_recruitment)
                            level.fractional_recruitment -= new_recruits
                        
                        # Add new hires
                        for _ in range(new_recruits):
                            level.add_new_hire(current_month_key, role_name, office_name)
                        
                        # PHASE 2: Churn
                        churn_key = f'churn_{current_month.value}'
                        default_churn = getattr(level, churn_key)
                        lever_churn = levers.get(churn_key) if levers else None
                        churn_rate = lever_churn if lever_churn is not None else default_churn
                        
                        # Deterministic fractional accumulation for churn
                        exact_churn = level.total * churn_rate
                        level.fractional_churn += exact_churn
                        churn_count = int(level.fractional_churn)
                        level.fractional_churn -= churn_count
                        
                        # Debug Oslo A level
                        if office_name == 'Oslo' and role_name == 'Consultant' and level_name == 'A':
                            print(f"[DEBUG] Oslo A churn: {level.total} * {churn_rate} = {churn_count}")
                        
                        churned_people = level.apply_churn(churn_count)
                        
                        # Store flat role results
                        office_results['levels'][role_name].append({
                            'total': level.total,
                            'price': getattr(level, f'price_{current_month.value}'),
                            'salary': getattr(level, f'salary_{current_month.value}')
                        })
                
                # Store operations results (for flat roles only)
                if 'Operations' in office.roles:
                    op = office.roles['Operations']
                    office_results['operations'].append({
                        'total': op.total,
                        'price': getattr(op, f'price_{current_month.value}'),
                        'salary': getattr(op, f'salary_{current_month.value}')
                    })
                else:
                    office_results['operations'].append(None)
                
                # Calculate journey totals by aggregating levels based on their journey assignments
                journey_totals = {"Journey 1": 0, "Journey 2": 0, "Journey 3": 0, "Journey 4": 0}
                
                for role_name, role_data in office.roles.items():
                    if isinstance(role_data, dict):  # Roles with levels
                        for level_name, level in role_data.items():
                            journey_name = level.journey.value
                            journey_totals[journey_name] += level.total
                
                # Store journey results
                for journey_name, total in journey_totals.items():
                    results["years"][str(current_year)]["offices"][office_name]["journeys"][journey_name].append({
                        'total': total
                    })
                
                # Calculate and store metrics
                office_results['metrics'].append({
                    'growth': self.calculate_growth(previous_total, current_year),
                    'recruitment': self.calculate_recruitment(office, current_month),
                    'non_debit_ratio': self.calculate_non_debit_ratio(office, current_month),
                    'churn': self.calculate_churn(office, current_month),
                    'progression': self.calculate_progression(office, current_month),
                    'revenue': self.calculate_revenue(office, current_month),
                    'costs': self.calculate_costs(office, current_month),
                    'profit': self.calculate_profit(office, current_month),
                    'profit_margin': self.calculate_profit_margin(office, current_month)
                })
                
                # Update year summary
                year_summary = results["years"][str(current_year)]["summary"]
                year_summary["total_fte"] += sum(getattr(level, 'total', 0) for role_data in office.roles.values() 
                                               for level in (role_data.values() if isinstance(role_data, dict) else [role_data]))
                year_summary["total_revenue"] += self.calculate_revenue(office, current_month)
                year_summary["total_costs"] += self.calculate_costs(office, current_month)
                year_summary["total_profit"] = year_summary["total_revenue"] - year_summary["total_costs"]
                year_summary["average_margin"] = year_summary["total_profit"] / year_summary["total_revenue"] if year_summary["total_revenue"] > 0 else 0.0
                
                # Calculate year-over-year growth rate
                if current_year > start_year:
                    previous_year_fte = results["years"][str(current_year - 1)]["summary"]["total_fte"]
                    year_summary["growth_rate"] = (year_summary["total_fte"] - previous_year_fte) / previous_year_fte if previous_year_fte > 0 else 0.0
                
                # Update prices and salaries at the end of each year
                if current_month == Month.DEC:
                    for role_data in office.roles.values():
                        if isinstance(role_data, dict):
                            for level in role_data.values():
                                for month in range(1, 13):
                                    price_attr = f'price_{month}'
                                    salary_attr = f'salary_{month}'
                                    setattr(level, price_attr, getattr(level, price_attr) * (1 + price_increase))
                                    setattr(level, salary_attr, getattr(level, salary_attr) * (1 + salary_increase))
                        else:
                            for month in range(1, 13):
                                price_attr = f'price_{month}'
                                salary_attr = f'salary_{month}'
                                setattr(role_data, price_attr, getattr(role_data, price_attr) * (1 + price_increase))
                                setattr(role_data, salary_attr, getattr(role_data, salary_attr) * (1 + salary_increase))
            
            # Move to next month
            if current_month.value == 12:
                current_year += 1
                current_month = Month.JAN
            else:
                current_month = Month(current_month.value + 1)
        
        # Store results for later retrieval
        self._last_simulation_results = results
        
        return results
    
    def get_simulation_results(self) -> Optional[Dict[str, Any]]:
        """Get the last simulation results"""
        return self._last_simulation_results
    
    def calculate_kpis_for_simulation(
        self, 
        results: Dict[str, Any], 
        simulation_duration_months: int,
        unplanned_absence: float = 0.05,
        other_expense: float = 100000.0
    ) -> Dict[str, Any]:
        """Calculate KPIs for simulation results and add them to the results"""
        
        try:
            # Calculate all KPIs using the KPI service
            all_kpis = self.kpi_service.calculate_all_kpis(
                results,
                simulation_duration_months,
                unplanned_absence,
                other_expense
            )
            
            # Add KPIs to results with frontend-compatible field names
            results['kpis'] = {
                'financial': {
                    'current_net_sales': all_kpis.financial.net_sales,
                    'baseline_net_sales': all_kpis.financial.net_sales_baseline,
                    'net_sales_delta': all_kpis.financial.net_sales - all_kpis.financial.net_sales_baseline,
                    'current_ebitda': all_kpis.financial.ebitda,
                    'baseline_ebitda': all_kpis.financial.ebitda_baseline,
                    'ebitda_delta': all_kpis.financial.ebitda - all_kpis.financial.ebitda_baseline,
                    'current_margin': all_kpis.financial.margin,
                    'baseline_margin': all_kpis.financial.margin_baseline,
                    'margin_delta': all_kpis.financial.margin - all_kpis.financial.margin_baseline,
                    'total_consultants': all_kpis.financial.total_consultants,
                    'total_consultants_baseline': all_kpis.financial.total_consultants_baseline,
                    'avg_hourly_rate': all_kpis.financial.avg_hourly_rate,
                    'avg_hourly_rate_baseline': all_kpis.financial.avg_hourly_rate_baseline,
                    'avg_utr': all_kpis.financial.avg_utr
                },
                'growth': {
                    'total_growth_percent': all_kpis.growth.total_growth_percent,
                    'total_growth_absolute': all_kpis.growth.total_growth_absolute,
                    'current_total_fte': all_kpis.growth.current_total_fte,
                    'baseline_total_fte': all_kpis.growth.baseline_total_fte,
                    'non_debit_ratio': all_kpis.growth.non_debit_ratio,
                    'non_debit_ratio_baseline': all_kpis.growth.non_debit_ratio_baseline,
                    'non_debit_delta': all_kpis.growth.non_debit_delta
                },
                'journeys': {
                    'journey_totals': all_kpis.journeys.journey_totals,
                    'journey_percentages': all_kpis.journeys.journey_percentages,
                    'journey_deltas': all_kpis.journeys.journey_deltas
                }
            }
            
            print(f"[DEBUG] KPIs calculated successfully")
            print(f"[DEBUG] Financial - Net Sales: {all_kpis.financial.net_sales:,.0f} (Baseline: {all_kpis.financial.net_sales_baseline:,.0f})")
            print(f"[DEBUG] Growth - Total Growth: {all_kpis.growth.total_growth_percent:.1f}% ({all_kpis.growth.total_growth_absolute:+d} FTE)")
            print(f"[DEBUG] Growth - Non-Debit Ratio: {all_kpis.growth.non_debit_ratio:.1f}% (Baseline: {all_kpis.growth.non_debit_ratio_baseline:.1f}%)")
            
        except Exception as e:
            print(f"[ERROR] Failed to calculate KPIs: {e}")
            # Add empty KPIs structure to avoid frontend errors
            results['kpis'] = {
                'financial': {},
                'growth': {},
                'journeys': {}
            }
        
        return results
    
    def _get_next_level_name(self, current_level: str) -> Optional[str]:
        """Get the next level name in the progression path"""
        if current_level == "PiP":
            return None
        level_order = ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"]
        current_index = level_order.index(current_level)
        return level_order[current_index + 1]
    
    def _get_next_level(self, current_level: str, role_name: str, office_roles: Dict[str, Dict[str, Level] or RoleData]) -> Optional[Level]:
        """Get the next level object in the progression path (for compatibility)"""
        next_level_name = self._get_next_level_name(current_level)
        if next_level_name and role_name in office_roles and isinstance(office_roles[role_name], dict):
            if next_level_name in office_roles[role_name]:
                return office_roles[role_name][next_level_name]
        return None

    def calculate_growth(self, previous_total: int, current_year: int) -> float:
        """Calculate growth rate between periods"""
        if previous_total == 0:
            return 0.0
        current_total = sum(level.total for role_data in self.offices.values() 
                          for role_data in role_data.roles.values() 
                          if isinstance(role_data, dict) 
                          for level in role_data.values())
        return (current_total - previous_total) / previous_total

    def calculate_recruitment(self, office: Office, current_month: Month) -> float:
        """Calculate recruitment rate for an office"""
        total_recruited = 0
        total_employees = 0
        for role_data in office.roles.values():
            if isinstance(role_data, dict):
                for level in role_data.values():
                    recruitment_rate = getattr(level, f'recruitment_{current_month.value}')
                    recruited = int(level.total * recruitment_rate)
                    total_recruited += recruited
                    total_employees += level.total
            else:
                recruitment_rate = getattr(role_data, f'recruitment_{current_month.value}')
                recruited = int(role_data.total * recruitment_rate)
                total_recruited += recruited
                total_employees += role_data.total
        return total_recruited / total_employees if total_employees > 0 else 0.0

    def calculate_non_debit_ratio(self, office: Office, current_month: Month) -> float:
        """Calculate non-debit ratio (Senior levels / Total)"""
        senior_count = 0
        total_count = 0
        for role_data in office.roles.values():
            if isinstance(role_data, dict):
                for level_name, level in role_data.items():
                    total_count += level.total
                    if level_name in ["M", "SrM", "PiP"]:
                        senior_count += level.total
        return senior_count / total_count if total_count > 0 else 0.0

    def calculate_churn(self, office: Office, current_month: Month) -> float:
        """Calculate churn rate for an office"""
        total_churned = 0
        total_employees = 0
        for role_data in office.roles.values():
            if isinstance(role_data, dict):
                for level in role_data.values():
                    churn_rate = getattr(level, f'churn_{current_month.value}')
                    churned = int(level.total * churn_rate)
                    total_churned += churned
                    total_employees += level.total
            else:
                churn_rate = getattr(role_data, f'churn_{current_month.value}')
                churned = int(role_data.total * churn_rate)
                total_churned += churned
                total_employees += role_data.total
        return total_churned / total_employees if total_employees > 0 else 0.0

    def calculate_progression(self, office: Office, current_month: Month) -> float:
        """Calculate progression rate for an office"""
        total_progressed = 0
        total_employees = 0
        for role_data in office.roles.values():
            if isinstance(role_data, dict):
                for level_name, level in role_data.items():
                    # Check if progression occurs this month based on level configuration
                    if current_month in level.progression_months:
                        progression_rate = getattr(level, f'progression_{current_month.value}')
                    else:
                        progression_rate = 0.0
                    total_progressed += int(level.total * progression_rate)
                    total_employees += level.total
        return total_progressed / total_employees if total_employees > 0 else 0.0

    def calculate_revenue(self, office: Office, current_month: Month) -> float:
        """Calculate revenue for an office - only consultants generate revenue"""
        total_revenue = 0
        working_hours_per_month = 160  # Standard working hours per month (20 days * 8 hours)
        
        # Only consultants generate revenue (billable to clients)
        if 'Consultant' in office.roles:
            consultant_roles = office.roles['Consultant']
            if isinstance(consultant_roles, dict):
                for level in consultant_roles.values():
                    hourly_rate = getattr(level, f'price_{current_month.value}')
                    utr = getattr(level, f'utr_{current_month.value}')
                    # Convert hourly rate to monthly revenue
                    monthly_revenue_per_person = hourly_rate * working_hours_per_month * utr
                    total_revenue += level.total * monthly_revenue_per_person
        
        # Sales, Recruitment, and Operations are cost centers (no revenue)
        return total_revenue

    def calculate_costs(self, office: Office, current_month: Month) -> float:
        """Calculate costs for an office"""
        total_costs = 0
        for role_data in office.roles.values():
            if isinstance(role_data, dict):
                for level in role_data.values():
                    total_costs += level.total * getattr(level, f'salary_{current_month.value}')
            else:
                total_costs += role_data.total * getattr(role_data, f'salary_{current_month.value}')
        return total_costs

    def calculate_profit(self, office: Office, current_month: Month) -> float:
        """Calculate profit for an office"""
        return self.calculate_revenue(office, current_month) - self.calculate_costs(office, current_month)

    def calculate_profit_margin(self, office: Office, current_month: Month) -> float:
        """Calculate profit margin for an office"""
        revenue = self.calculate_revenue(office, current_month)
        return self.calculate_profit(office, current_month) / revenue if revenue > 0 else 0.0 