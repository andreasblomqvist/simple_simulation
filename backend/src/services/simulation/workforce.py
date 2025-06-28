from typing import Dict, Any
from backend.src.services.simulation.models import Office, Level, RoleData, Month
from backend.src.services.simulation.utils import get_monthly_attribute, get_next_level_name
from backend.src.services.simulation.event_logger import EventLogger
import logging
import uuid

class WorkforceManager:
    """
    Handles all workforce dynamics: progression, recruitment, churn, and people movement.
    """
    def __init__(self, offices: Dict[str, Office]):
        self.offices = offices
        self.event_logger = None  # Will be initialized when run_id is set

    def set_run_id(self):
        self.run_id = str(uuid.uuid4())
        self.event_logger = EventLogger(self.run_id)

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
        logger = logging.getLogger("simplesim")  # Use same logger as main.py
        run_id = getattr(self, 'run_id', 'NO_RUN_ID')
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
                                    # Log promotion event
                                    if self.event_logger:
                                        cat_category = f"CAT{cat_number}"
                                        # Get progression probability from CAT curves
                                        from backend.config.progression_config import CAT_CURVES
                                        if level_name in CAT_CURVES:
                                            cat = f"CAT{cat_number}"
                                            progression_probability = CAT_CURVES[level_name].get(cat, 0.0)
                                        else:
                                            progression_probability = 0.0
                                        
                                        next_level_name = get_next_level_name(level_name, list(role_data.keys()))
                                        self.event_logger.log_promotion(
                                            person=person,
                                            current_date=current_date_str,
                                            from_level=level_name,
                                            to_level=next_level_name,
                                            role=role_name,
                                            office=office.name,
                                            cat_category=cat_category,
                                            progression_probability=progression_probability
                                        )
                                    
                                    monthly_office_metrics[office.name][current_date_str]['promotion_details'].append({
                                        'role': role_name,
                                        'level': level_name,
                                        'months_on_level': months_on_level,
                                        'cat': cat_number,
                                        'date': current_date_str
                                    })
                    # Removed PROGRESSION_DEBUG logging for skipped cases
                    
                    # Track progression metrics
                    # Note: Progression metrics are stored in the nested structure below, not in flat structure
                    # The flat structure was incorrect and caused the 189 vs 34 discrepancy
                
                # Handle promotions to next levels
                promoted_into_levels = {level_name: 0 for level_name in role_data.keys()}
                for level_name, promoted_people in promotions_this_month.items():
                    # Find next level using progression config
                    next_level_name = get_next_level_name(level_name, list(role_data.keys()))
                    next_level = role_data.get(next_level_name) if next_level_name else None
                    if next_level:
                        for person, _, _ in promoted_people:
                            next_level.add_promotion(person, current_date_str)
                        promoted_into_levels[next_level_name] = len(promoted_people)
                    # else: top level, people leave the cohort
                
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

    def process_churn_and_recruitment(self, office: Office, current_month_enum: Month, current_date_str: str, monthly_office_metrics: Dict[str, Any]):
        """
        Process churn and recruitment for all roles/levels in an office for the given month.
        Updates FTE and stores metrics.
        """
        for role_name, role_data in office.roles.items():
            if isinstance(role_data, dict):  # Leveled roles
                for level_name, level in role_data.items():
                    # Churn
                    churn_rate = get_monthly_attribute(level, 'churn', current_month_enum)
                    level.fractional_churn += level.total * churn_rate
                    churn_to_apply = int(level.fractional_churn)
                    level.fractional_churn -= churn_to_apply
                    churned = level.apply_churn(churn_to_apply)
                    
                    # Log churn events
                    if self.event_logger and churned:
                        for person in churned:
                            self.event_logger.log_churn(
                                person=person,
                                current_date=current_date_str,
                                role=role_name,
                                office=office.name,
                                churn_rate=churn_rate
                            )
                    
                    # Recruitment
                    recruitment_rate = get_monthly_attribute(level, 'recruitment', current_month_enum)
                    level.fractional_recruitment += level.total * recruitment_rate
                    recruits_to_add = int(level.fractional_recruitment)
                    level.fractional_recruitment -= recruits_to_add
                    recruited_people = []
                    for _ in range(recruits_to_add):
                        person = level.add_new_hire(current_date_str, role_name, office.name)
                        recruited_people.append(person)
                    
                    # Log recruitment events
                    if self.event_logger and recruited_people:
                        for person in recruited_people:
                            self.event_logger.log_recruitment(
                                person=person,
                                current_date=current_date_str,
                                role=role_name,
                                office=office.name,
                                recruitment_rate=recruitment_rate
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
                        'churned': churn_to_apply,
                        'price': get_monthly_attribute(level, 'price', current_month_enum),
                        'salary': get_monthly_attribute(level, 'salary', current_month_enum),
                        'utr': get_monthly_attribute(level, 'utr', current_month_enum),
                    })
            else:  # Flat roles
                # Churn
                churn_rate = get_monthly_attribute(role_data, 'churn', current_month_enum)
                role_data.fractional_churn += role_data.total * churn_rate
                churn_to_apply = int(role_data.fractional_churn)
                role_data.fractional_churn -= churn_to_apply
                churned = role_data.apply_churn(churn_to_apply)
                
                # Log churn events for flat roles
                if self.event_logger and churned:
                    for person in churned:
                        self.event_logger.log_churn(
                            person=person,
                            current_date=current_date_str,
                            role=role_name,
                            office=office.name,
                            churn_rate=churn_rate
                        )
                
                # Recruitment
                recruitment_rate = get_monthly_attribute(role_data, 'recruitment', current_month_enum)
                role_data.fractional_recruitment += role_data.total * recruitment_rate
                recruits_to_add = int(role_data.fractional_recruitment)
                role_data.fractional_recruitment -= recruits_to_add
                recruited_people = []
                for _ in range(recruits_to_add):
                    person = role_data.add_new_hire(current_date_str, role_name, office.name)
                    recruited_people.append(person)
                
                # Log recruitment events for flat roles
                if self.event_logger and recruited_people:
                    for person in recruited_people:
                        self.event_logger.log_recruitment(
                            person=person,
                            current_date=current_date_str,
                            role=role_name,
                            office=office.name,
                            recruitment_rate=recruitment_rate
                        )
                
                # Update metrics
                if office.name not in monthly_office_metrics:
                    monthly_office_metrics[office.name] = {}
                if current_date_str not in monthly_office_metrics[office.name]:
                    monthly_office_metrics[office.name][current_date_str] = {}
                monthly_office_metrics[office.name][current_date_str][role_name] = {
                    'total_fte': role_data.total,
                    'recruited': recruits_to_add,
                    'churned': churn_to_apply
                }

    def get_event_logger(self) -> EventLogger:
        """Get the event logger instance"""
        return self.event_logger

    # Add more helper methods as needed for CAT-based progression, churn, recruitment, etc. 

class WorkforceSimulation:
    def run_simulation(self, *args, **kwargs):
        self.run_id = uuid.uuid4()
        # ... existing code ...
        # Pass self.run_id to all functions that log progression
        # ... existing code ... 