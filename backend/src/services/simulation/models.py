"""
Core data models for the simulation engine.

This module contains all the fundamental data structures used by the simulation:
- Enums for months, journeys, and office types
- Dataclasses for Person, RoleData, Level, and Office
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid
import random
import sys
import os
# Import from config since we're running from backend directory with PYTHONPATH=.
from config.laf_progression import LAF_PROGRESSION, PROGRESSION_LEVER

# Forward references for type hints
ProgressionConfig = 'ProgressionConfig'
CATCurves = 'CATCurves'

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
    
    def get_progression_probability(self, current_date: str, level_name: str, cat_curves: Dict[str, Any]) -> float:
        """
        Calculate progression probability using CAT curves.
        
        Args:
            current_date: Current date in YYYY-MM format
            level_name: Name of the level (e.g., "A", "C", "AM")
            cat_curves: CAT curves dict (required)
        """
        tenure_months = self.get_level_tenure_months(current_date)
        # CAT0 should always return 0.0 (no progression for < 6 months)
        if tenure_months < 6:
            return 0.0
        # Determine CAT group
        cat_number = 6 * ((tenure_months // 6))
        cat = f'CAT{cat_number}'
        # Lookup probability from CAT curves
        prob = cat_curves.get(level_name, {}).get(cat, 0.0)
        return min(prob, 1.0)

@dataclass
class RoleData:
    """Represents a flat role (like Operations) without levels"""
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
    # Absolute recruitment and churn (1-12) - only absolute values supported
    recruitment_abs_1: Optional[float] = None
    recruitment_abs_2: Optional[float] = None
    recruitment_abs_3: Optional[float] = None
    recruitment_abs_4: Optional[float] = None
    recruitment_abs_5: Optional[float] = None
    recruitment_abs_6: Optional[float] = None
    recruitment_abs_7: Optional[float] = None
    recruitment_abs_8: Optional[float] = None
    recruitment_abs_9: Optional[float] = None
    recruitment_abs_10: Optional[float] = None
    recruitment_abs_11: Optional[float] = None
    recruitment_abs_12: Optional[float] = None
    churn_abs_1: Optional[float] = None
    churn_abs_2: Optional[float] = None
    churn_abs_3: Optional[float] = None
    churn_abs_4: Optional[float] = None
    churn_abs_5: Optional[float] = None
    churn_abs_6: Optional[float] = None
    churn_abs_7: Optional[float] = None
    churn_abs_8: Optional[float] = None
    churn_abs_9: Optional[float] = None
    churn_abs_10: Optional[float] = None
    churn_abs_11: Optional[float] = None
    churn_abs_12: Optional[float] = None
    # Individual tracking
    people: List[Person] = field(default_factory=list)
    # Fractional accumulation for deterministic results
    fractional_recruitment: float = 0.0
    fractional_churn: float = 0.0
    
    @property
    def fte(self) -> int:
        """Full-time equivalent count - standardized field name"""
        return len(self.people)
    
    @property
    def total(self) -> int:
        """Legacy property for backward compatibility"""
        return self.fte
    
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
    # Absolute recruitment and churn (1-12) - only absolute values supported
    recruitment_abs_1: Optional[float] = None
    recruitment_abs_2: Optional[float] = None
    recruitment_abs_3: Optional[float] = None
    recruitment_abs_4: Optional[float] = None
    recruitment_abs_5: Optional[float] = None
    recruitment_abs_6: Optional[float] = None
    recruitment_abs_7: Optional[float] = None
    recruitment_abs_8: Optional[float] = None
    recruitment_abs_9: Optional[float] = None
    recruitment_abs_10: Optional[float] = None
    recruitment_abs_11: Optional[float] = None
    recruitment_abs_12: Optional[float] = None
    churn_abs_1: Optional[float] = None
    churn_abs_2: Optional[float] = None
    churn_abs_3: Optional[float] = None
    churn_abs_4: Optional[float] = None
    churn_abs_5: Optional[float] = None
    churn_abs_6: Optional[float] = None
    churn_abs_7: Optional[float] = None
    churn_abs_8: Optional[float] = None
    churn_abs_9: Optional[float] = None
    churn_abs_10: Optional[float] = None
    churn_abs_11: Optional[float] = None
    churn_abs_12: Optional[float] = None
    # Individual tracking
    people: List[Person] = field(default_factory=list)
    # Fractional accumulation for deterministic results
    fractional_recruitment: float = 0.0
    fractional_churn: float = 0.0
    
    @property
    def fte(self) -> int:
        """Full-time equivalent count - standardized field name"""
        return len(self.people)
    
    @property
    def total(self) -> int:
        """Legacy property for backward compatibility"""
        return self.fte
    
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
    
    def is_progression_month(self, current_month: int, progression_config: Union[Dict[str, Any], 'ProgressionConfig']) -> bool:
        """
        Check if the given month is a progression month for this level.
        
        Args:
            current_month: Month number (1-12)
            progression_config: Progression rules dict or ProgressionConfig object
        """
        # Handle ProgressionConfig object
        if hasattr(progression_config, 'is_progression_month'):
            return progression_config.is_progression_month(self.name, current_month)
        
        # Handle legacy dict format
        if self.name in progression_config:
            progression_months = progression_config[self.name]['progression_months']
            return current_month in progression_months
        
        # No fallback - progression config must be provided
        return False

    def get_minimum_tenure(self, progression_config: Union[Dict[str, Any], 'ProgressionConfig']) -> int:
        """Get minimum tenure required for progression from progression config"""
        # Handle ProgressionConfig object
        if hasattr(progression_config, 'get_minimum_tenure'):
            return progression_config.get_minimum_tenure(self.name)
        
        # Handle legacy dict format
        return progression_config.get(self.name, {}).get('time_on_level', 6)

    def get_journey(self, progression_config: Union[Dict[str, Any], 'ProgressionConfig']) -> str:
        """Get journey for this level from progression config"""
        # Handle ProgressionConfig object
        if hasattr(progression_config, 'get_level_config'):
            level_config = progression_config.get_level_config(self.name)
            return level_config.journey if level_config else None
        
        # Handle legacy dict format
        return progression_config.get(self.name, {}).get('journey', None)

    def get_eligible_for_progression(self, current_date: str, progression_config: Union[Dict[str, Any], 'ProgressionConfig']):
        """
        Get people eligible for progression based on minimum tenure and progression months.
        
        Args:
            current_date: Current date in YYYY-MM format
            progression_config: Progression rules dict or ProgressionConfig object
        """
        # Check if this is a progression month
        current_month = int(current_date.split('-')[1])
        if not self.is_progression_month(current_month, progression_config):
            return []
        
        # Get minimum tenure from progression config
        min_tenure = self.get_minimum_tenure(progression_config)
        
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
        # This method is deprecated - use apply_cat_based_progression with explicit config parameters
        raise NotImplementedError(
            "apply_progression is deprecated. Use apply_cat_based_progression(current_date, progression_config, cat_curves) instead. "
            "The engine no longer loads config files directly - all config must be passed as parameters."
        )
    
    def apply_cat_based_progression(self, current_date: str, progression_config: Union[Dict[str, Any], 'ProgressionConfig'], cat_curves: Union[Dict[str, Any], 'CATCurves']):
        """
        Apply CAT-based progression with individual probabilities, return promoted people and their CAT info.
        
        Args:
            current_date: Current date in YYYY-MM format
            progression_config: Progression rules dict or ProgressionConfig object
            cat_curves: CAT curves dict or CATCurves object
        """
        eligible = self.get_eligible_for_progression(current_date, progression_config)
        if len(eligible) == 0:
            return []
        
        promoted = []
        current_month = int(current_date.split('-')[1])
        
        for person in eligible:
            # Calculate individual progression probability based on CAT curves
            tenure_months = person.get_level_tenure_months(current_date)
            
            # Determine CAT category
            if tenure_months < 6:
                cat = 'CAT0'
                cat_number = 0
            else:
                cat_number = min(60, 6 * ((tenure_months // 6)))
                cat = f'CAT{cat_number}'
            
            # Get probability from CAT curve
            if hasattr(cat_curves, 'get_probability'):
                # Handle CATCurves object
                individual_probability = cat_curves.get_probability(self.name, cat)
            else:
                # Handle legacy dict format
                if self.name in cat_curves:
                    individual_probability = cat_curves[self.name].get(cat, 0.0)
                else:
                    individual_probability = 0.0
            
            if random.random() < individual_probability:
                promoted.append((person, tenure_months, cat_number))
        
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
