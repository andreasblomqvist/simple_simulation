"""
Core data models for the simulation engine.

This module contains all the fundamental data structures used by the simulation:
- Enums for months, journeys, and office types
- Dataclasses for Person, RoleData, Level, and Office
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid
import random
from backend.config.default_config import DEFAULT_RATES
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../config'))
from backend.config.laf_progression import LAF_PROGRESSION, PROGRESSION_LEVER
from backend.config.progression_config import PROGRESSION_CONFIG, CAT_CURVES

class Month(Enum):
    """Enumeration for months of the year"""
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
    """Enumeration for half-year periods"""
    H1 = "H1"
    H2 = "H2"

class Journey(Enum):
    """Enumeration for career journey stages"""
    JOURNEY_1 = "Journey 1"
    JOURNEY_2 = "Journey 2"
    JOURNEY_3 = "Journey 3"
    JOURNEY_4 = "Journey 4"

class OfficeJourney(Enum):
    """Enumeration for office maturity stages"""
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
    role: str              # "Consultant", "Sales", "Recruitment", "Operations"
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
    
    def get_progression_probability(self, current_date: str, level_name: str) -> float:
        """Calculate progression probability using CAT_CURVES from progression_config.py"""
        tenure_months = self.get_level_tenure_months(current_date)
        # CAT0 should always return 0.0 (no progression for < 6 months)
        if tenure_months < 6:
            return 0.0
        # Determine CAT group
        cat_number = 6 * ((tenure_months // 6))
        cat = f'CAT{cat_number}'
        # Lookup probability from CAT_CURVES
        prob = CAT_CURVES.get(level_name, {}).get(cat, 0.0)
        return min(prob, 1.0)

@dataclass
class RoleData:
    """Represents a flat role (like Operations) without levels"""
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
    """Represents a level within a role (like Consultant A, C, SrC, etc.)"""
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
    
    def is_progression_month(self, current_month: int) -> bool:
        months = PROGRESSION_CONFIG.get(self.name, {}).get('progression_months', [1])
        return current_month in months

    def get_minimum_tenure(self) -> int:
        return PROGRESSION_CONFIG.get(self.name, {}).get('start_tenure', 0)

    def get_journey(self) -> str:
        return PROGRESSION_CONFIG.get(self.name, {}).get('journey', None)

    def get_eligible_for_progression(self, current_date: str):
        # Only allow progression in configured months
        month = int(current_date.split('-')[1])
        if not self.is_progression_month(month):
            return []
        min_tenure = self.get_minimum_tenure()
        # Only allow people with tenure >= min_tenure
        return [p for p in self.people if p.get_level_tenure_months(current_date) >= min_tenure]
    
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
        return self.apply_cat_based_progression(current_date)
    
    def apply_cat_based_progression(self, current_date: str):
        """Apply LAF-based progression with individual probabilities, return promoted people and their CAT info"""
        eligible = self.get_eligible_for_progression(current_date)
        if len(eligible) == 0:
            return []
        promoted = []
        current_month = int(current_date.split('-')[1])
        is_valid_month = current_month in [m.value for m in self.progression_months]
        for person in eligible:
            individual_probability = person.get_progression_probability(current_date, self.name)
            if random.random() < individual_probability:
                months_on_level = person.get_level_tenure_months(current_date)
                cat_number = 6 * ((months_on_level // 6))
                promoted.append((person, months_on_level, cat_number))
                if self.name == 'AM':
                    print(f"[AM PROMOTION DEBUG] Month={current_month}, Allowed={is_valid_month}, MonthsOnLevel={months_on_level}, CAT=CAT{cat_number}, Prob={individual_probability}")
        if promoted:
            print(f"[DEBUG] Promotion: Level={self.name}, Month={current_month}, Allowed={is_valid_month}, Promoted={len(promoted)}")
        for person, _, _ in promoted:
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
    """Represents an office with its roles and levels"""
    name: str
    total_fte: int
    journey: OfficeJourney
    roles: Dict[str, Dict[str, Level] or RoleData]  # 'Consultant': {level: Level}, others: RoleData

    @classmethod
    def create_office(cls, name: str, total_fte: int) -> 'Office':
        """Create an office with the appropriate journey based on FTE count"""
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