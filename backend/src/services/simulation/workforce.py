from typing import Dict, Any, List, Tuple, Optional
from .models import Office, Level, RoleData, Month
from .utils import get_monthly_attribute, get_next_level_name, determine_level_order
import logging
import uuid
from .event_logger import EventLogger
import json
import os
from datetime import datetime
from dataclasses import dataclass

# Set up debug logging
debug_logger = logging.getLogger('workforce_debug')
debug_logger.setLevel(logging.DEBUG)

# Create debug file handler
debug_file = f"debug_simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
debug_handler = logging.FileHandler(debug_file, mode='w')
debug_handler.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
debug_handler.setFormatter(formatter)
debug_logger.addHandler(debug_handler)

# Also log to console for immediate feedback
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
debug_logger.addHandler(console_handler)

def get_effective_recruitment_value(obj, month: int) -> int:
    """
    Get effective recruitment value for the given month.
    Only absolute values are supported. Returns the absolute value or 0 if not present.
    """
    abs_field = f"recruitment_abs_{month}"
    abs_value = getattr(obj, abs_field, None)
    if abs_value is not None:
        return int(abs_value)
    # If not present, return 0 (or raise error if strict)
    return 0

def get_effective_churn_value(obj, month: int) -> int:
    """
    Get effective churn value for the given month.
    Only absolute values are supported. Returns the absolute value or 0 if not present.
    """
    abs_field = f"churn_abs_{month}"
    abs_value = getattr(obj, abs_field, None)
    if abs_value is not None:
        return int(abs_value)
    # If not present, return 0 (or raise error if strict)
    return 0

@dataclass
class WorkforceLevel:
    """Represents a workforce level with FTE and tenure tracking"""
    fte: float
    tenure_months: List[int]  # List of tenure months for each person
    
    def add_fte(self, amount: float, tenure: int = 0):
        """Add FTE with specified tenure"""
        self.fte += amount
        # Add tenure months for new FTE (simplified: assume new hires have 0 tenure)
        for _ in range(int(amount)):
            self.tenure_months.append(tenure)
    
    def remove_fte(self, amount: float):
        """Remove FTE (simplified: remove from end of tenure list)"""
        if amount > self.fte:
            amount = self.fte
        self.fte -= amount
        # Remove tenure entries (simplified: remove from end)
        for _ in range(int(amount)):
            if self.tenure_months:
                self.tenure_months.pop()
    
    def get_tenure_distribution(self) -> Dict[str, int]:
        """Get tenure distribution for progression calculations"""
        if not self.tenure_months:
            return {}
        
        distribution = {}
        for tenure in self.tenure_months:
            cat = self._get_tenure_category(tenure)
            distribution[cat] = distribution.get(cat, 0) + 1
        return distribution
    
    def _get_tenure_category(self, tenure: int) -> str:
        """Convert tenure months to category"""
        if tenure < 6:
            return "CAT6"
        elif tenure < 12:
            return "CAT12"
        elif tenure < 18:
            return "CAT18"
        elif tenure < 24:
            return "CAT24"
        elif tenure < 30:
            return "CAT30"
        else:
            return "CAT30+"

class WorkforceManager:
    """
    Handles all workforce dynamics: progression, recruitment, churn, and people movement.
    """
    def __init__(self, offices: Dict[str, Office], run_id: str = None):
        self.offices = offices
        self.run_id = run_id or str(uuid.uuid4())
        self.event_logger = EventLogger(self.run_id)
        self.levels: Dict[str, WorkforceLevel] = {}

    def set_run_id(self):
        self.run_id = str(uuid.uuid4())

    def get_event_logger(self):
        """Return the event logger instance for external access"""
        return self.event_logger

    def get_events_summary(self):
        """Return a summary of all logged events"""
        return self.event_logger.get_events_summary() if self.event_logger else {}

    def get_all_events(self):
        """Return all logged events as a list"""
        return self.event_logger.get_all_events() if self.event_logger else []

    def process_month(self, year: int, month: int, current_date_str: str, monthly_office_metrics: Dict[str, Any]):
        """
        Process a single month for all offices:
        - Progression (CAT-based)
        - Churn
        - Recruitment
        - Update office FTEs and metrics
        """
        current_month_enum = Month(month)
        for office in self.offices.values():
            if office.name not in monthly_office_metrics:
                monthly_office_metrics[office.name] = {}
            monthly_office_metrics[office.name][current_date_str] = {}
            office_total_fte = 0

            # 1. Progression (CAT-based)
            self.process_progression(office, current_month_enum, current_date_str, monthly_office_metrics)

            # 2. Churn and Recruitment
            self.process_churn_and_recruitment(office, current_month_enum, current_date_str, monthly_office_metrics)

            # 3. Update office FTE
            for role_name, role_data in office.roles.items():
                if isinstance(role_data, dict):
                    for level in role_data.values():
                        office_total_fte += level.total
                else:
                    office_total_fte += role_data.total
            office.total_fte = office_total_fte
            monthly_office_metrics[office.name][current_date_str]['total_fte'] = office.total_fte

    def process_progression(self, office: Office, current_month_enum: Month, current_date_str: str, monthly_office_metrics: Dict[str, Any]):
        """
        Process progression for all roles/levels in an office for the given month.
        Handles promotions and tracks movement between levels.
        """
        for role_name, role_data in office.roles.items():
            if isinstance(role_data, dict):  # Leveled roles
                promotions_this_month = {}
                for level_name, level in role_data.items():
                    # Check if this is a progression month for this level
                    if level.is_progression_month(current_month_enum.value):
                        eligible = len(level.get_eligible_for_progression(current_date_str))
                        
                        if eligible > 0:
                            promotions = level.apply_cat_based_progression(current_date_str)
                            if promotions:
                                promotions_this_month[level_name] = promotions
                                promoted = len(promotions)
                                
                                # Store detailed promotion info for test script
                                if 'promotion_details' not in monthly_office_metrics[office.name][current_date_str]:
                                    monthly_office_metrics[office.name][current_date_str]['promotion_details'] = []
                                for person, months_on_level, cat_number in promotions:
                                    monthly_office_metrics[office.name][current_date_str]['promotion_details'].append({
                                        'role': role_name,
                                        'level': level_name,
                                        'months_on_level': months_on_level,
                                        'cat': cat_number,
                                        'date': current_date_str
                                    })
                                    
                                    # Log promotion event
                                    next_level_name = get_next_level_name(level_name, list(role_data.keys()))
                                    if next_level_name:
                                        self.event_logger.log_promotion(
                                            person=person,
                                            current_date=current_date_str,
                                            from_level=level_name,
                                            to_level=next_level_name,
                                            role=role_name,
                                            office=office.name,
                                            cat_category=f"CAT{cat_number}",
                                            progression_probability=None  # Could be calculated if needed
                                        )
                        else:
                            pass
                    else:
                        pass
                    
                # Handle promotions to next levels
                promoted_into_levels = {level_name: 0 for level_name in role_data.keys()}
                for level_name, promoted_people in promotions_this_month.items():
                    # Find next level using proper level order
                    level_order = determine_level_order([{'roles': {role_name: role_data}}])
                    next_level_name = get_next_level_name(level_name, level_order)
                    
                    next_level = role_data.get(next_level_name) if next_level_name else None
                    if next_level:
                        for person, _, _ in promoted_people:
                            next_level.add_promotion(person, current_date_str)
                        promoted_into_levels[next_level_name] = len(promoted_people)
                    else:
                        # Top level - people graduate/leave the cohort
                        # Log these as churn events so they don't disappear without tracking
                        for person, _, _ in promoted_people:
                            self.event_logger.log_churn(
                                person=person,
                                current_date=current_date_str,
                                role=role_name,
                                office=office.name,
                                churn_rate=None  # Graduation, not churn
                            )
                
                # Store promotion metrics for each level in the correct nested structure
                for level_name, level in role_data.items():
                    if office.name not in monthly_office_metrics:
                        monthly_office_metrics[office.name] = {}
                    if current_date_str not in monthly_office_metrics[office.name]:
                        monthly_office_metrics[office.name][current_date_str] = {}
                    if role_name not in monthly_office_metrics[office.name][current_date_str]:
                        monthly_office_metrics[office.name][current_date_str][role_name] = {}
                    monthly_office_metrics[office.name][current_date_str][role_name][level_name] = {
                        'progressed_out': len(promotions_this_month.get(level_name, [])),
                        'progressed_in': promoted_into_levels.get(level_name, 0),
                    }
                    
        # Log office total
        office_total_fte = 0
        for role_name, role_data in office.roles.items():
            if isinstance(role_data, dict):
                for level in role_data.values():
                    office_total_fte += level.total
            else:
                office_total_fte += role_data.total
        

    def process_churn_and_recruitment(self, office: Office, current_month_enum: Month, current_date_str: str, monthly_office_metrics: Dict[str, Any]):
        """
        Process churn and recruitment for all roles/levels in an office for the given month.
        Updates FTE and stores metrics.
        """
        for role_name, role_data in office.roles.items():
            if isinstance(role_data, dict):  # Leveled roles
                for level_name, level in role_data.items():
                    # Churn - using new absolute/percentage logic
                    churn_to_apply = get_effective_churn_value(level, current_month_enum.value)
                    
                    churned = level.apply_churn(churn_to_apply)
                    
                    # Log churn events
                    for person in churned:
                        self.event_logger.log_churn(
                            person=person,
                            current_date=current_date_str,
                            role=role_name,
                            office=office.name,
                            churn_rate=None  # Method used is tracked separately
                        )
                    
                    # Recruitment - using new absolute/percentage logic
                    recruits_to_add = get_effective_recruitment_value(level, current_month_enum.value)
                    
                    for _ in range(recruits_to_add):
                        new_person = level.add_new_hire(current_date_str, role_name, office.name)
                        # Log recruitment event
                        self.event_logger.log_recruitment(
                            person=new_person,
                            current_date=current_date_str,
                            role=role_name,
                            office=office.name,
                            recruitment_rate=None  # Method used is tracked separately
                        )
                    
                    # Update metrics
                    if office.name not in monthly_office_metrics:
                        monthly_office_metrics[office.name] = {}
                    if current_date_str not in monthly_office_metrics[office.name]:
                        monthly_office_metrics[office.name][current_date_str] = {}
                    if role_name not in monthly_office_metrics[office.name][current_date_str]:
                        monthly_office_metrics[office.name][current_date_str][role_name] = {}
                    if level_name not in monthly_office_metrics[office.name][current_date_str][role_name]:
                        monthly_office_metrics[office.name][current_date_str][role_name][level_name] = {}
                    monthly_office_metrics[office.name][current_date_str][role_name][level_name].update({
                        'total_fte': level.total,
                        'recruited': recruits_to_add,
                        'recruitment_method': 'absolute', # Always absolute
                        'recruitment_details': {'absolute_value': recruits_to_add},
                        'churned': churn_to_apply,
                        'churn_method': 'absolute', # Always absolute
                        'churn_details': {'absolute_value': churn_to_apply},
                        'price': get_monthly_attribute(level, 'price', current_month_enum),
                        'salary': get_monthly_attribute(level, 'salary', current_month_enum),
                        'utr': get_monthly_attribute(level, 'utr', current_month_enum),
                    })
            else:  # Flat roles
                # Churn - using new absolute/percentage logic
                churn_to_apply = get_effective_churn_value(role_data, current_month_enum.value)
                
                churned = role_data.apply_churn(churn_to_apply)
                
                # Log churn events
                for person in churned:
                    self.event_logger.log_churn(
                        person=person,
                        current_date=current_date_str,
                        role=role_name,
                        office=office.name,
                        churn_rate=None  # Method used is tracked separately
                    )
                
                # Recruitment - using new absolute/percentage logic
                recruits_to_add = get_effective_recruitment_value(role_data, current_month_enum.value)
                
                for _ in range(recruits_to_add):
                    new_person = role_data.add_new_hire(current_date_str, role_name, office.name)
                    # Log recruitment event
                    self.event_logger.log_recruitment(
                        person=new_person,
                        current_date=current_date_str,
                        role=role_name,
                        office=office.name,
                        recruitment_rate=None  # Method used is tracked separately
                    )
                
                # Update metrics
                if office.name not in monthly_office_metrics:
                    monthly_office_metrics[office.name] = {}
                if current_date_str not in monthly_office_metrics[office.name]:
                    monthly_office_metrics[office.name][current_date_str] = {}
                monthly_office_metrics[office.name][current_date_str][role_name] = {
                    'total_fte': role_data.total,
                    'recruited': recruits_to_add,
                    'recruitment_method': 'absolute', # Always absolute
                    'recruitment_details': {'absolute_value': recruits_to_add},
                    'churned': churn_to_apply,
                    'churn_method': 'absolute', # Always absolute
                    'churn_details': {'absolute_value': churn_to_apply}
                }
        
        # Log office total
        office_total_fte = 0
        for role_name, role_data in office.roles.items():
            if isinstance(role_data, dict):
                for level in role_data.values():
                    office_total_fte += level.total
            else:
                office_total_fte += role_data.total
        

    # Add more helper methods as needed for CAT-based progression, churn, recruitment, etc. 

class WorkforceSimulation:
    def run_simulation(self, *args, **kwargs):
        self.run_id = uuid.uuid4()
        # ... existing code ...
        # Pass self.run_id to all functions that log progression
        # ... existing code ... 