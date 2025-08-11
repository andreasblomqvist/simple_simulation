"""
Workforce Manager V2 - Individual Tracking Component

Handles all workforce dynamics with complete individual event tracking:
- Person lifecycle management
- CAT-based progression logic
- Churn processing with individual selection
- Recruitment with proper person initialization
- Complete event audit trail
"""

from typing import Dict, List, Optional, Tuple, Set, Any
from datetime import datetime, date
import uuid
import random
import logging
from dataclasses import dataclass

from .simulation_engine_v2 import (
    Person, PersonEvent, EventType, CATMatrix, MonthlyTargets,
    WorkforceManagerInterface, ValidationResult, EngineValidator
)

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class ChurnConfiguration:
    """Configuration for churn processing"""
    method: str = "random"  # "random", "tenure_based", "performance_based"
    tenure_bias: float = 0.1  # Higher values bias toward newer employees
    preserve_top_performers: bool = True


@dataclass
class ProgressionConfiguration:
    """Configuration for progression processing"""
    progression_months: List[int]  # Months when progression occurs (1-12)
    minimum_tenure_months: int = 6  # Minimum tenure required
    use_cat_probabilities: bool = True


@dataclass
class RecruitmentConfiguration:
    """Configuration for recruitment processing"""
    default_hire_level: str = "A"  # Default entry level
    distribution_strategy: str = "entry_level"  # "entry_level", "distributed"


class WorkforceManagerV2(WorkforceManagerInterface):
    """
    Manages workforce dynamics with complete individual tracking
    
    Key capabilities:
    - Individual person lifecycle management
    - CAT-based progression with event tracking
    - Configurable churn strategies
    - Complete audit trail for all workforce changes
    """
    
    def __init__(self):
        self.churn_config = ChurnConfiguration()
        self.progression_config = ProgressionConfiguration([6, 12])  # Default: June and December
        self.recruitment_config = RecruitmentConfiguration()
        self.level_progression_months = {}  # Will be loaded from config
        self.random_seed: Optional[int] = None
        self.event_counter = 0
    
    def initialize(self, **kwargs) -> bool:
        """Initialize workforce manager with configuration"""
        if 'churn_config' in kwargs:
            self.churn_config = kwargs['churn_config']
        if 'progression_config' in kwargs:
            self.progression_config = kwargs['progression_config']
        if 'recruitment_config' in kwargs:
            self.recruitment_config = kwargs['recruitment_config']
        if 'random_seed' in kwargs:
            self.random_seed = kwargs['random_seed']
            random.seed(self.random_seed)
        
        # Load level-specific progression months from config
        if 'level_progression_config' in kwargs:
            self.level_progression_months = kwargs['level_progression_config']
        else:
            # Load from progression_config.py if available
            try:
                import sys
                from pathlib import Path
                # Add backend to path if needed
                backend_path = Path(__file__).parent.parent.parent
                if str(backend_path) not in sys.path:
                    sys.path.insert(0, str(backend_path))
                from config.progression_config import PROGRESSION_CONFIG
                self.level_progression_months = {
                    level: config.get('progression_months', [])
                    for level, config in PROGRESSION_CONFIG.items()
                }
                logger.info(f"Loaded progression months for {len(self.level_progression_months)} levels")
            except ImportError as e:
                # Keep empty if config not available
                logger.warning(f"Could not load progression config: {e}, using empty level progression months")
        
        logger.info("WorkforceManagerV2 initialized successfully")
        return True
    
    def process_churn(self, people: List[Person], targets: Dict[str, int], current_date: date) -> List[PersonEvent]:
        """
        Process churn for given people with individual selection
        
        Args:
            people: List of people eligible for churn
            targets: Churn targets by level {"A": 2, "C": 1}
            current_date: Current simulation date
        
        Returns:
            List of PersonEvent objects for churned individuals
        """
        events = []
        
        for level, target_count in targets.items():
            # Get people at this level
            level_people = [p for p in people if p.current_level == level and p.is_active]
            
            if not level_people or target_count <= 0:
                continue
            
            # Select people to churn based on configuration
            churned_people = self._select_people_for_churn(level_people, target_count)
            
            # Create events and update person state
            for person in churned_people:
                event = self._create_churn_event(person, current_date)
                person.add_event(event)
                events.append(event)
                
                logger.debug(f"Churned person {person.id} from {person.current_role} {person.current_level}")
        
        return events
    
    def process_progression(self, people: List[Person], cat_matrix: CATMatrix, current_date: date) -> List[PersonEvent]:
        """
        Process CAT-based progression for given people
        
        Args:
            people: List of people eligible for progression
            cat_matrix: CAT matrix with progression probabilities
            current_date: Current simulation date
        
        Returns:
            List of PersonEvent objects for promoted individuals
        """
        events = []
        
        # Group people by role and level for processing
        role_level_groups = self._group_people_by_role_level(people)
        
        for (role, level), level_people in role_level_groups.items():
            # Check if current month is a progression month for this level
            level_progression_months = self.level_progression_months.get(level, [])
            if not level_progression_months or current_date.month not in level_progression_months:
                continue  # Skip this level if not a progression month
            
            # Get eligible people (minimum tenure requirement)
            eligible_people = [
                p for p in level_people 
                if (p.is_active and 
                    p.get_level_tenure_months(current_date) >= self.progression_config.minimum_tenure_months)
            ]
            
            if not eligible_people:
                continue
            
            # Process individual progression probabilities
            for person in eligible_people:
                if self._should_person_progress(person, level, cat_matrix, current_date):
                    # Determine next level using progression config
                    next_level = self._get_next_level(person.current_role, level)
                    if next_level:
                        event = self._create_promotion_event(person, level, next_level, current_date, cat_matrix)
                        person.add_event(event)
                        events.append(event)
                        
                        logger.debug(f"Promoted person {person.id} from {level} to {next_level}")
        
        return events
    
    def process_recruitment(self, targets: Dict[str, int], role: str, level: str, office: str, current_date: date) -> List[Person]:
        """
        Process recruitment for specific role/level
        
        Args:
            targets: Recruitment targets by level {"A": 5, "C": 2}
            role: Role name (e.g., "Consultant")
            level: Level name (e.g., "A")
            office: Office name
            current_date: Current simulation date
        
        Returns:
            List of newly hired Person objects
        """
        new_people = []
        
        target_count = targets.get(level, 0)
        if target_count <= 0:
            return new_people
        
        # Create new hires - simple integer recruitment
        for _ in range(target_count):
            person = self._create_new_hire(role, level, office, current_date)
            
            # Create hire event
            hire_event = self._create_hire_event(person, current_date)
            person.add_event(hire_event)
            
            new_people.append(person)
            logger.debug(f"Hired new person {person.id} as {role} {level} in {office}")
        
        if target_count > 0:
            logger.info(f"Recruited {target_count} {role} {level} in {office}")
        
        return new_people
    
    def calculate_cat_probability(self, person: Person, cat_matrix: CATMatrix, current_date: date = None) -> float:
        """Calculate CAT progression probability for individual based on tenure"""
        if current_date is None:
            current_date = date.today()
        
        # Check if person meets minimum tenure requirement
        tenure_months = person.get_level_tenure_months(current_date)
        if tenure_months < self.progression_config.minimum_tenure_months:
            return 0.0
        
        # Determine CAT category based on tenure
        cat_category = self._get_cat_category(tenure_months)
        
        # Get probability from CAT matrix for this level and category
        level_probabilities = cat_matrix.progression_probabilities.get(person.current_level, {})
        probability = level_probabilities.get(cat_category, 0.0)
        
        return probability
    
    def get_person_statistics(self, people: List[Person], current_date: date) -> Dict[str, Any]:
        """Get comprehensive statistics for a group of people"""
        if not people:
            return {}
        
        active_people = [p for p in people if p.is_active]
        
        return {
            "total_people": len(people),
            "active_people": len(active_people),
            "average_tenure_months": sum(p.get_tenure_months(current_date) for p in active_people) / len(active_people) if active_people else 0,
            "average_level_tenure_months": sum(p.get_level_tenure_months(current_date) for p in active_people) / len(active_people) if active_people else 0,
            "tenure_distribution": self._get_tenure_distribution(active_people, current_date),
            "level_distribution": self._get_level_distribution(active_people),
            "total_events": sum(len(p.events) for p in people)
        }
    
    # ========================================================================
    # Private Helper Methods
    # ========================================================================
    
    def _select_people_for_churn(self, people: List[Person], target_count: int) -> List[Person]:
        """Select people for churn based on configuration"""
        target_count = min(target_count, len(people))
        
        if self.churn_config.method == "random":
            return random.sample(people, target_count)
        
        elif self.churn_config.method == "tenure_based":
            # Bias toward newer employees (shorter tenure)
            people_with_weights = []
            current_date = date.today()
            
            for person in people:
                tenure_months = person.get_tenure_months(current_date)
                # Weight inversely proportional to tenure (newer = higher weight)
                weight = 1.0 / (tenure_months + 1) if tenure_months > 0 else 1.0
                people_with_weights.append((person, weight))
            
            # Weighted random selection
            selected = []
            for _ in range(target_count):
                total_weight = sum(weight for _, weight in people_with_weights)
                if total_weight == 0:
                    break
                
                r = random.random() * total_weight
                cumulative = 0
                for person, weight in people_with_weights:
                    cumulative += weight
                    if r <= cumulative:
                        selected.append(person)
                        people_with_weights.remove((person, weight))
                        break
            
            return selected
        
        else:
            # Default to random
            return random.sample(people, target_count)
    
    def _should_person_progress(self, person: Person, level: str, cat_matrix: CATMatrix, current_date: date) -> bool:
        """Determine if individual person should progress based on CAT probability"""
        if not self.progression_config.use_cat_probabilities:
            return False
        
        probability = self.calculate_cat_probability(person, cat_matrix, current_date)
        return random.random() < probability
    
    def _get_cat_category(self, tenure_months: int) -> str:
        """Get CAT category based on tenure months"""
        if tenure_months < 6:
            return "CAT0"
        elif tenure_months < 12:
            return "CAT6" 
        elif tenure_months < 18:
            return "CAT12"
        elif tenure_months < 24:
            return "CAT18"
        elif tenure_months < 30:
            return "CAT24"
        else:
            return "CAT30+"
    
    def _get_next_level(self, role: str, current_level: str) -> Optional[str]:
        """Get next level for progression (simplified - would use actual progression rules)"""
        # Simplified progression mapping - would be configurable in real implementation
        level_progressions = {
            "Consultant": {
                "A": "AC",
                "AC": "C", 
                "C": "SrC",
                "SrC": "M",
                "M": "SrM",
                "SrM": None  # Top level
            },
            "Sales": {
                "A": "AC",
                "AC": "C",
                "C": "SrC", 
                "SrC": None
            }
        }
        
        return level_progressions.get(role, {}).get(current_level)
    
    def _create_new_hire(self, role: str, level: str, office: str, current_date: date) -> Person:
        """Create new hire Person object"""
        return Person(
            id=str(uuid.uuid4()),
            current_role=role,
            current_level=level,
            current_office=office,
            hire_date=current_date,
            current_level_start=current_date,
            events=[],
            is_active=True
        )
    
    def _create_hire_event(self, person: Person, current_date: date) -> PersonEvent:
        """Create hire event"""
        self.event_counter += 1
        return PersonEvent(
            date=current_date,
            event_type=EventType.HIRED,
            details={
                "role": person.current_role,
                "level": person.current_level,
                "office": person.current_office
            },
            simulation_month=self.event_counter,
            from_state=None,
            to_state={
                "role": person.current_role,
                "level": person.current_level,
                "office": person.current_office
            }
        )
    
    def _create_churn_event(self, person: Person, current_date: date) -> PersonEvent:
        """Create churn event"""
        self.event_counter += 1
        return PersonEvent(
            date=current_date,
            event_type=EventType.CHURNED,
            details={
                "role": person.current_role,
                "level": person.current_level,
                "office": person.current_office,
                "tenure_months": person.get_tenure_months(current_date),
                "level_tenure_months": person.get_level_tenure_months(current_date)
            },
            simulation_month=self.event_counter,
            from_state={
                "role": person.current_role,
                "level": person.current_level,
                "office": person.current_office
            },
            to_state=None
        )
    
    def _create_promotion_event(self, person: Person, from_level: str, to_level: str, 
                              current_date: date, cat_matrix: CATMatrix) -> PersonEvent:
        """Create promotion event"""
        self.event_counter += 1
        probability_used = self.calculate_cat_probability(person, cat_matrix, current_date)
        
        return PersonEvent(
            date=current_date,
            event_type=EventType.PROMOTED,
            details={
                "role": person.current_role,
                "from_level": from_level,
                "to_level": to_level,
                "office": person.current_office,
                "tenure_months": person.get_tenure_months(current_date),
                "level_tenure_months": person.get_level_tenure_months(current_date),
                "cat_category": self._get_cat_category(person.get_level_tenure_months(current_date))
            },
            simulation_month=self.event_counter,
            from_state={
                "role": person.current_role,
                "level": from_level,
                "office": person.current_office
            },
            to_state={
                "role": person.current_role,
                "level": to_level,
                "office": person.current_office
            },
            probability_used=probability_used
        )
    
    def _get_next_level_from_matrix(self, current_level: str, cat_matrix: CATMatrix) -> Optional[str]:
        """Select next level from CAT matrix based on progression probabilities"""
        import random
        
        # Get all possible progressions from current level
        current_level_progressions = cat_matrix.progression_probabilities.get(current_level, {})
        
        if not current_level_progressions:
            return None
        
        # If only one progression option, return it
        if len(current_level_progressions) == 1:
            return list(current_level_progressions.keys())[0]
        
        # Multiple progression options - choose randomly based on relative probabilities
        levels = list(current_level_progressions.keys())
        probabilities = list(current_level_progressions.values())
        
        # Normalize probabilities to relative weights
        total_prob = sum(probabilities)
        if total_prob == 0:
            return None
        
        weights = [prob / total_prob for prob in probabilities]
        
        # Random selection based on weights
        rand = random.random()
        cumulative = 0.0
        for i, weight in enumerate(weights):
            cumulative += weight
            if rand <= cumulative:
                return levels[i]
        
        # Fallback to first level if something goes wrong
        return levels[0]
    
    def _group_people_by_role_level(self, people: List[Person]) -> Dict[Tuple[str, str], List[Person]]:
        """Group people by (role, level) tuples"""
        groups = {}
        for person in people:
            key = (person.current_role, person.current_level)
            if key not in groups:
                groups[key] = []
            groups[key].append(person)
        return groups
    
    def _get_tenure_distribution(self, people: List[Person], current_date: date) -> Dict[str, int]:
        """Get tenure distribution for people"""
        distribution = {"0-6": 0, "6-12": 0, "12-24": 0, "24+": 0}
        
        for person in people:
            tenure_months = person.get_tenure_months(current_date)
            if tenure_months < 6:
                distribution["0-6"] += 1
            elif tenure_months < 12:
                distribution["6-12"] += 1
            elif tenure_months < 24:
                distribution["12-24"] += 1
            else:
                distribution["24+"] += 1
        
        return distribution
    
    def _get_level_distribution(self, people: List[Person]) -> Dict[str, int]:
        """Get level distribution for people"""
        distribution = {}
        for person in people:
            level = person.current_level
            distribution[level] = distribution.get(level, 0) + 1
        return distribution


# ============================================================================
# Workforce Analytics Component
# ============================================================================

class WorkforceAnalytics:
    """Analytics component for workforce insights"""
    
    @staticmethod
    def analyze_progression_patterns(events: List[PersonEvent]) -> Dict[str, Any]:
        """Analyze progression patterns from events"""
        promotion_events = [e for e in events if e.event_type == EventType.PROMOTED]
        
        if not promotion_events:
            return {"total_promotions": 0}
        
        # Analyze by level
        level_promotions = {}
        probability_stats = {}
        
        for event in promotion_events:
            from_level = event.details.get("from_level")
            to_level = event.details.get("to_level")
            probability = event.probability_used
            
            if from_level:
                level_promotions[from_level] = level_promotions.get(from_level, 0) + 1
                
                if probability is not None:
                    if from_level not in probability_stats:
                        probability_stats[from_level] = []
                    probability_stats[from_level].append(probability)
        
        # Calculate average probabilities
        avg_probabilities = {}
        for level, probs in probability_stats.items():
            avg_probabilities[level] = sum(probs) / len(probs)
        
        return {
            "total_promotions": len(promotion_events),
            "promotions_by_level": level_promotions,
            "average_promotion_probabilities": avg_probabilities
        }
    
    @staticmethod
    def analyze_churn_patterns(events: List[PersonEvent]) -> Dict[str, Any]:
        """Analyze churn patterns from events"""
        churn_events = [e for e in events if e.event_type == EventType.CHURNED]
        
        if not churn_events:
            return {"total_churn": 0}
        
        # Analyze by level and tenure
        level_churn = {}
        tenure_churn = {"0-6": 0, "6-12": 0, "12-24": 0, "24+": 0}
        
        for event in churn_events:
            level = event.details.get("level")
            tenure_months = event.details.get("tenure_months", 0)
            
            if level:
                level_churn[level] = level_churn.get(level, 0) + 1
            
            # Categorize by tenure
            if tenure_months < 6:
                tenure_churn["0-6"] += 1
            elif tenure_months < 12:
                tenure_churn["6-12"] += 1
            elif tenure_months < 24:
                tenure_churn["12-24"] += 1
            else:
                tenure_churn["24+"] += 1
        
        return {
            "total_churn": len(churn_events),
            "churn_by_level": level_churn,
            "churn_by_tenure": tenure_churn
        }


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    'WorkforceManagerV2',
    'ChurnConfiguration',
    'ProgressionConfiguration', 
    'RecruitmentConfiguration',
    'WorkforceAnalytics'
]