"""
People Initializer - Creates realistic people with career histories.

This service has a single responsibility: initialize people for levels and roles
with realistic career start dates, level start dates, and career progression.
"""
import random
import logging
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

class PeopleInitializer:
    """
    Initializes people with realistic career histories.
    Focused solely on people creation and career timeline generation.
    """
    
    def __init__(self):
        # Career path table for realistic time on level distribution
        self.career_paths = {
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
    
    def initialize_people_for_level_or_role(self, level_or_role: Any, fte_count: int, role_name: str, office_name: str, current_date: str = "2025-01"):
        """
        Initialize people for a level or role with realistic career histories.
        
        Args:
            level_or_role: Level or RoleData object to add people to
            fte_count: Number of people to create
            role_name: Name of the role (e.g., 'Consultant', 'Operations')
            office_name: Name of the office
            current_date: Current date for simulation start (default: "2025-01")
        """
        if fte_count <= 0:
            return
        
        # Base date for simulation start
        base_date = datetime(2025, 1, 1)  # January 2025
        
        for i in range(fte_count):
            if hasattr(level_or_role, 'name') and level_or_role.name in self.career_paths:
                # This is a leveled role - create realistic career history
                self._create_leveled_person(level_or_role, role_name, office_name, base_date)
            else:
                # This is a flat role (Operations) - just distribute start dates
                self._create_flat_person(level_or_role, role_name, office_name, base_date)
    
    def _create_leveled_person(self, level: Any, role_name: str, office_name: str, base_date: datetime):
        """Create a person for a leveled role with realistic career history."""
        level_name = level.name
        career_path = self.career_paths[level_name]
        
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
        person = level.add_new_hire(
            career_start_date.strftime("%Y-%m"),
            role_name,
            office_name
        )
        person.level_start = level_start_date.strftime("%Y-%m")
    
    def _create_flat_person(self, role: Any, role_name: str, office_name: str, base_date: datetime):
        """Create a person for a flat role (Operations) with realistic start date."""
        # Operations people typically have 1-5 years of experience
        months_of_experience = random.randint(6, 60)  # 6 months to 5 years
        start_date = base_date - timedelta(days=months_of_experience * 30)
        
        person = role.add_new_hire(
            start_date.strftime("%Y-%m"),
            role_name,
            office_name
        ) 