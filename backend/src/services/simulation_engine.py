from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json
import sys
import os

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
class RoleData:
    total: int = 0
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
    utr_10: float        # percentage
    utr_11: float        # percentage
    utr_12: float        # percentage
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
    total: int = 0

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
                            total=level_fte,
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
                            setattr(office.roles[role_name][level_name], f'churn_{month}', DEFAULT_RATES['churn'])
                            
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
                
                office.roles["Operations"] = RoleData(
                    total=operations_fte,
                    recruitment_1=operations_recruitment, recruitment_2=operations_recruitment, recruitment_3=operations_recruitment, recruitment_4=operations_recruitment, recruitment_5=operations_recruitment, recruitment_6=operations_recruitment, recruitment_7=operations_recruitment, recruitment_8=operations_recruitment, recruitment_9=operations_recruitment, recruitment_10=operations_recruitment, recruitment_11=operations_recruitment, recruitment_12=operations_recruitment,
                    churn_1=DEFAULT_RATES['churn'], churn_2=DEFAULT_RATES['churn'], churn_3=DEFAULT_RATES['churn'], churn_4=DEFAULT_RATES['churn'], churn_5=DEFAULT_RATES['churn'], churn_6=DEFAULT_RATES['churn'], churn_7=DEFAULT_RATES['churn'], churn_8=DEFAULT_RATES['churn'], churn_9=DEFAULT_RATES['churn'], churn_10=DEFAULT_RATES['churn'], churn_11=DEFAULT_RATES['churn'], churn_12=DEFAULT_RATES['churn'],
                    price_1=op_price, price_2=op_price, price_3=op_price, price_4=op_price, price_5=op_price, price_6=op_price, price_7=op_price, price_8=op_price, price_9=op_price, price_10=op_price, price_11=op_price, price_12=op_price,
                    salary_1=op_salary, salary_2=op_salary, salary_3=op_salary, salary_4=op_salary, salary_5=op_salary, salary_6=op_salary, salary_7=op_salary, salary_8=op_salary, salary_9=op_salary, salary_10=op_salary, salary_11=op_salary, salary_12=op_salary,
                    utr_1=DEFAULT_RATES['utr'], utr_2=DEFAULT_RATES['utr'], utr_3=DEFAULT_RATES['utr'], utr_4=DEFAULT_RATES['utr'], utr_5=DEFAULT_RATES['utr'], utr_6=DEFAULT_RATES['utr'], utr_7=DEFAULT_RATES['utr'], utr_8=DEFAULT_RATES['utr'], utr_9=DEFAULT_RATES['utr'], utr_10=DEFAULT_RATES['utr'], utr_11=DEFAULT_RATES['utr'], utr_12=DEFAULT_RATES['utr']
                )
                for month in range(1, 13):
                    # Add slight monthly increase (0.25% per month)
                    monthly_op_price = op_price * (1 + 0.0025 * (month - 1))
                    monthly_op_salary = op_salary * (1 + 0.0025 * (month - 1))
                    setattr(office.roles["Operations"], f'price_{month}', monthly_op_price)
                    setattr(office.roles["Operations"], f'salary_{month}', monthly_op_salary)

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
        
        # Convert month numbers to Month enum
        start_month_enum = Month(start_month)
        end_month_enum = Month(end_month)
        
        # Initialize results structure
        results = {
            "periods": [],
            "offices": {}
        }
        
        # Initialize office results
        for office_name, office in self.offices.items():
            results["offices"][office_name] = {
                "levels": {},
                "operations": [],
                "metrics": [],
                "office_journey": office.journey.value,
                "journeys": {
                    "Journey 1": [],
                    "Journey 2": [],
                    "Journey 3": [],
                    "Journey 4": []
                }
            }
            
            # Initialize level tracking
            for role_name, role_data in office.roles.items():
                if isinstance(role_data, dict):  # Roles with levels
                    results["offices"][office_name]["levels"][role_name] = {}
                    for level_name in role_data.keys():
                        results["offices"][office_name]["levels"][role_name][level_name] = []
        
        # Simulation loop through months
        current_year = start_year
        current_month = start_month_enum

        while (current_year < end_year or 
               (current_year == end_year and current_month.value <= end_month_enum.value)):
            
            print(f"[DEBUG] Period: {current_year} {current_month.name}")
            stock = self.offices['Stockholm'].roles['Consultant']
            print(f"[DEBUG] Stockholm Consultant A BEFORE: {stock['A'].total}")
            print(f"[DEBUG] Stockholm Consultant AC BEFORE: {stock['AC'].total}")
            
            # Record period
            results["periods"].append(f"{current_year}-{current_month.name}")
            
            # Process each office
            for office_name, office in self.offices.items():
                office_results = results["offices"][office_name]
                previous_total = sum(getattr(level, 'total', 0) for role_data in office.roles.values() 
                                   for level in (role_data.values() if isinstance(role_data, dict) else [role_data]))
                
                # Apply levers and simulate roles with levels
                for role_name, role_data in office.roles.items():
                    if isinstance(role_data, dict):  # Roles with levels
                        
                        # PHASE 1: Calculate churn for all levels first
                        for level_name, level in role_data.items():
                            # Check for levers
                            levers = {}
                            if lever_plan and office_name in lever_plan and role_name in lever_plan[office_name]:
                                levers = lever_plan[office_name][role_name].get(level_name, {})
                            
                            # Apply churn
                            churn_key = f'churn_{current_month.value}'
                            churn_rate = levers.get(churn_key) if levers.get(churn_key) is not None else getattr(level, churn_key)
                            if office_name == 'Stockholm' and role_name == 'Consultant' and level_name in ['A', 'AC']:
                                print(f"[DEBUG] {office_name} {role_name} {level_name} CHURN RATE: {churn_rate}")
                            level.total = int(level.total * (1 - churn_rate))
                            if office_name == 'Stockholm' and role_name == 'Consultant' and level_name in ['A', 'AC']:
                                print(f"[DEBUG] {office_name} {role_name} {level_name} AFTER CHURN: {level.total}")
                        
                        # PHASE 2: Calculate all progressions (but don't apply yet)
                        progression_plan = {}
                        for level_name, level in role_data.items():
                            # Check for levers
                            levers = {}
                            if lever_plan and office_name in lever_plan and role_name in lever_plan[office_name]:
                                levers = lever_plan[office_name][role_name].get(level_name, {})
                            
                            # Calculate progression based on CURRENT headcount (after churn, before any moves)
                            progression_key = f'progression_{current_month.value}'
                            if current_month in level.progression_months:
                                progression_rate = levers.get(progression_key) if levers.get(progression_key) is not None else getattr(level, progression_key)
                            else:
                                progression_rate = 0.0
                            

                            if progression_rate > 0:
                                progressed = int(level.total * progression_rate)
                                if progressed > 0:
                                    next_level_name = self._get_next_level_name(level_name)
                                    if next_level_name and next_level_name in role_data:
                                        progression_plan[level_name] = {
                                            'to_level': next_level_name,
                                            'count': progressed
                                        }
                                        if office_name == 'Stockholm' and role_name == 'Consultant' and level_name in ['A', 'AC']:
                                            print(f"[DEBUG] PLANNED PROGRESSION: {level_name} -> {next_level_name}, count: {progressed}")
                        
                        # PHASE 3: Apply all progressions simultaneously
                        for from_level_name, move in progression_plan.items():
                            from_level = role_data[from_level_name]
                            to_level = role_data[move['to_level']]
                            
                            from_level.total -= move['count']
                            to_level.total += move['count']
                            
                            if office_name == 'Stockholm' and role_name == 'Consultant' and from_level_name in ['A', 'AC']:
                                print(f"[DEBUG] APPLIED PROGRESSION: {from_level_name} -> {move['to_level']}, moved: {move['count']}")
                        
                        # PHASE 4: Apply recruitment
                        for level_name, level in role_data.items():
                            # Check for levers
                            levers = {}
                            if lever_plan and office_name in lever_plan and role_name in lever_plan[office_name]:
                                levers = lever_plan[office_name][role_name].get(level_name, {})
                            
                            # Recruitment
                            recruitment_key = f'recruitment_{current_month.value}'
                            recruitment_rate = levers.get(recruitment_key) if levers.get(recruitment_key) is not None else getattr(level, recruitment_key)
                            if office_name == 'Stockholm' and role_name == 'Consultant' and level_name == 'A':
                                print(f"[DEBUG] {office_name} {role_name} {level_name} RECRUITMENT RATE: {recruitment_rate}")
                                print(f"[DEBUG] {office_name} {role_name} {level_name} BEFORE RECRUITMENT: {level.total}")
                            if level.total == 0:
                                new_recruits = int(recruitment_rate * 10)
                                if office_name == 'Stockholm' and role_name == 'Consultant' and level_name == 'A':
                                    print(f"[DEBUG] Zero FTE case: {new_recruits} recruits")
                            else:
                                new_recruits = int(level.total * recruitment_rate)
                                if office_name == 'Stockholm' and role_name == 'Consultant' and level_name == 'A':
                                    print(f"[DEBUG] Normal case: {level.total} * {recruitment_rate} = {new_recruits} recruits")
                            level.total += new_recruits
                            if office_name == 'Stockholm' and role_name == 'Consultant' and level_name == 'A':
                                print(f"[DEBUG] {office_name} {role_name} {level_name} AFTER RECRUITMENT: {level.total}")
                            
                            # Store level results
                            office_results['levels'][role_name][level_name].append({
                                'total': level.total,
                                'price': getattr(level, f'price_{current_month.value}'),
                                'salary': getattr(level, f'salary_{current_month.value}')
                            })
                    else:
                        # Flat role
                        levers = {}
                        if lever_plan and office_name in lever_plan and role_name in lever_plan[office_name]:
                            levers = lever_plan[office_name][role_name]
                        churn_rate = levers.get(f'churn_{current_month.value}', getattr(role_data, f'churn_{current_month.value}'))
                        role_data.total = int(role_data.total * (1 - churn_rate))
                        recruitment_rate = levers.get(f'recruitment_{current_month.value}', getattr(role_data, f'recruitment_{current_month.value}'))
                        if role_data.total == 0:
                            new_recruits = int(recruitment_rate * 10)
                        else:
                            new_recruits = int(role_data.total * recruitment_rate)
                        role_data.total += new_recruits
                
                # Store operations results (for flat roles only)
                if 'Operations' in office.roles:
                    op = office.roles['Operations']
                    office_results['operations'].append({
                        'total': op.total,
                        'price': getattr(op, f'price_{current_month.value}'),
                        'salary': getattr(op, f'salary_{current_month.value}')
                    })
                
                # Calculate journey totals by aggregating levels based on their journey assignments
                journey_totals = {"Journey 1": 0, "Journey 2": 0, "Journey 3": 0, "Journey 4": 0}
                
                for role_name, role_data in office.roles.items():
                    if isinstance(role_data, dict):  # Roles with levels
                        for level_name, level in role_data.items():
                            journey_name = level.journey.value
                            journey_totals[journey_name] += level.total
                
                # Store journey results
                for journey_name, total in journey_totals.items():
                    results["offices"][office_name]["journeys"][journey_name].append({
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
            
            print(f"[DEBUG] Stockholm Consultant A AFTER: {self.offices['Stockholm'].roles['Consultant']['A'].total}")
            print(f"[DEBUG] Stockholm Consultant AC AFTER: {self.offices['Stockholm'].roles['Consultant']['AC'].total}")
            
            # Move to next month
            if current_month.value == 12:
                current_year += 1
                current_month = Month.JAN
            else:
                current_month = Month(current_month.value + 1)
        
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
        """Calculate revenue for an office"""
        total_revenue = 0
        for role_data in office.roles.values():
            if isinstance(role_data, dict):
                for level in role_data.values():
                    price = getattr(level, f'price_{current_month.value}')
                    utr = getattr(level, f'utr_{current_month.value}')
                    total_revenue += level.total * price * utr
            else:
                price = getattr(role_data, f'price_{current_month.value}')
                utr = getattr(role_data, f'utr_{current_month.value}')
                total_revenue += role_data.total * price * utr
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