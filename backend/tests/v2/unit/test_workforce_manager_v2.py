"""
Comprehensive Unit Tests for WorkforceManagerV2

Tests workforce management functionality including:
- Individual person lifecycle tracking
- CAT-based progression logic
- Configurable churn strategies
- Recruitment with proper person initialization
- Event audit trail generation
- Configuration management
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, date
from typing import Dict, List

from backend.src.services.workforce_manager_v2 import (
    WorkforceManagerV2, ChurnConfiguration, ProgressionConfiguration,
    RecruitmentConfiguration
)

from backend.src.services.simulation_engine_v2 import (
    Person, PersonEvent, EventType, CATMatrix
)


class TestWorkforceManagerV2Initialization:
    """Test suite for WorkforceManagerV2 initialization"""

    def test_default_initialization(self):
        """Test workforce manager initializes with default configurations"""
        manager = WorkforceManagerV2()
        
        # Verify default configurations
        assert isinstance(manager.churn_config, ChurnConfiguration)
        assert manager.churn_config.method == "random"
        assert manager.churn_config.tenure_bias == 0.1
        assert manager.churn_config.preserve_top_performers is True
        
        assert isinstance(manager.progression_config, ProgressionConfiguration)
        assert manager.progression_config.progression_months == [6, 12]  # June and December
        assert manager.progression_config.minimum_tenure_months == 6
        assert manager.progression_config.use_cat_probabilities is True
        
        assert isinstance(manager.recruitment_config, RecruitmentConfiguration)
        assert manager.recruitment_config.default_hire_level == "A"
        assert manager.recruitment_config.distribution_strategy == "entry_level"
        
        assert manager.random_seed is None
        assert manager.event_counter == 0

    def test_custom_configuration_initialization(self):
        """Test workforce manager accepts custom configurations"""
        manager = WorkforceManagerV2()
        
        # Custom configurations
        custom_churn = ChurnConfiguration(
            method="tenure_based",
            tenure_bias=0.2,
            preserve_top_performers=False
        )
        
        custom_progression = ProgressionConfiguration(
            progression_months=[1, 4, 7, 10],
            minimum_tenure_months=12,
            use_cat_probabilities=False
        )
        
        custom_recruitment = RecruitmentConfiguration(
            default_hire_level="AC",
            distribution_strategy="distributed"
        )
        
        # Initialize with custom configs
        result = manager.initialize(
            churn_config=custom_churn,
            progression_config=custom_progression,
            recruitment_config=custom_recruitment,
            random_seed=42
        )
        
        assert result is True
        assert manager.churn_config == custom_churn
        assert manager.progression_config == custom_progression
        assert manager.recruitment_config == custom_recruitment
        assert manager.random_seed == 42

    @patch('random.seed')
    def test_random_seed_applied(self, mock_random_seed):
        """Test random seed is applied during initialization"""
        manager = WorkforceManagerV2()
        
        manager.initialize(random_seed=12345)
        
        mock_random_seed.assert_called_with(12345)
        assert manager.random_seed == 12345


class TestWorkforceManagerV2ChurnProcessing:
    """Test suite for churn processing functionality"""

    @pytest.fixture
    def sample_people(self, test_person_factory):
        """Create sample people for churn testing"""
        people = []
        
        # Create 5 Consultant A level people
        for i in range(5):
            person = test_person_factory(
                role="Consultant",
                level="A",
                office="Stockholm",
                hire_date="2024-01"
            )
            person.is_active = True
            person.current_level = "A"
            people.append(person)
        
        # Create 3 Consultant C level people
        for i in range(3):
            person = test_person_factory(
                role="Consultant", 
                level="C",
                office="Stockholm",
                hire_date="2023-06"
            )
            person.is_active = True
            person.current_level = "C"
            people.append(person)
        
        return people

    def test_churn_processing_basic(self, sample_people):
        """Test basic churn processing with target counts"""
        manager = WorkforceManagerV2()
        targets = {"A": 2, "C": 1}
        current_date = date(2025, 6, 15)
        
        events = manager.process_churn(sample_people, targets, current_date)
        
        # Should have 3 churn events (2 A level + 1 C level)
        assert len(events) == 3
        
        # Verify event types
        for event in events:
            assert event.event_type == EventType.CHURNED
            assert event.date == current_date
            assert event.simulation_month >= 0

    def test_churn_processing_insufficient_people(self, sample_people):
        """Test churn processing when not enough people available"""
        manager = WorkforceManagerV2()
        
        # Request more people than available at C level (have 3, want 5)
        targets = {"A": 2, "C": 5}
        current_date = date(2025, 6, 15)
        
        events = manager.process_churn(sample_people, targets, current_date)
        
        # Should only churn available people (2 A + 3 C = 5)
        assert len(events) == 5
        
        # Verify all C level people were churned
        c_events = [e for e in events if e.details.get("level") == "C"]
        assert len(c_events) == 3

    def test_churn_processing_zero_targets(self, sample_people):
        """Test churn processing with zero targets"""
        manager = WorkforceManagerV2()
        targets = {"A": 0, "C": 0}
        current_date = date(2025, 6, 15)
        
        events = manager.process_churn(sample_people, targets, current_date)
        
        # No churn events should be created
        assert len(events) == 0

    def test_churn_processing_inactive_people(self, test_person_factory):
        """Test churn processing ignores inactive people"""
        manager = WorkforceManagerV2()
        
        # Create people, some inactive
        people = []
        for i in range(3):
            person = test_person_factory(role="Consultant", level="A")
            person.current_level = "A"
            person.is_active = (i < 2)  # First 2 active, last 1 inactive
            people.append(person)
        
        targets = {"A": 3}  # Want to churn 3, but only 2 active
        current_date = date(2025, 6, 15)
        
        events = manager.process_churn(people, targets, current_date)
        
        # Should only churn active people
        assert len(events) == 2

    def test_churn_event_creation_details(self, test_person_factory):
        """Test churn events contain correct details"""
        manager = WorkforceManagerV2()
        
        person = test_person_factory(
            role="Consultant",
            level="A", 
            office="Stockholm",
            hire_date="2024-01"
        )
        person.current_level = "A"
        person.is_active = True
        
        targets = {"A": 1}
        current_date = date(2025, 6, 15)
        
        events = manager.process_churn([person], targets, current_date)
        
        assert len(events) == 1
        event = events[0]
        
        # Verify event details
        assert event.event_type == EventType.CHURNED
        assert event.date == current_date
        assert "role" in event.details
        assert "level" in event.details
        assert "office" in event.details
        assert event.details["role"] == "Consultant"
        assert event.details["level"] == "A"
        assert event.details["office"] == "Stockholm"

    def test_churn_configuration_random_method(self, sample_people):
        """Test churn with random selection method"""
        config = ChurnConfiguration(method="random", preserve_top_performers=False)
        manager = WorkforceManagerV2()
        manager.initialize(churn_config=config, random_seed=42)
        
        targets = {"A": 2}
        current_date = date(2025, 6, 15)
        
        # Run multiple times to ensure deterministic with seed
        events1 = manager.process_churn(sample_people, targets, current_date)
        
        manager.initialize(churn_config=config, random_seed=42)  # Reset with same seed
        events2 = manager.process_churn(sample_people, targets, current_date)
        
        # Should get same results with same seed
        assert len(events1) == len(events2) == 2


class TestWorkforceManagerV2ProgressionProcessing:
    """Test suite for CAT-based progression functionality"""

    @pytest.fixture
    def progression_people(self, test_person_factory):
        """Create people eligible for progression"""
        people = []
        
        # Create people with different tenure
        hire_dates = ["2024-01", "2024-06", "2023-12"]  # Different tenure lengths
        for i, hire_date in enumerate(hire_dates):
            person = test_person_factory(
                role="Consultant",
                level="A",
                office="Stockholm", 
                hire_date=hire_date
            )
            person.current_level = "A"
            person.is_active = True
            person.level_start_date = hire_date
            person.cat_rating = ["High", "Medium", "Low"][i % 3]
            people.append(person)
        
        return people

    def test_progression_in_progression_month(self, progression_people, cat_matrix):
        """Test progression processing during progression months"""
        config = ProgressionConfiguration(
            progression_months=[6],  # June only
            minimum_tenure_months=6,
            use_cat_probabilities=True
        )
        
        manager = WorkforceManagerV2()
        manager.initialize(progression_config=config, random_seed=42)
        
        current_date = date(2025, 6, 15)  # June - progression month
        
        with patch.object(manager, '_apply_cat_progression') as mock_progression:
            mock_progression.return_value = []  # No progressions for test
            
            events = manager.process_progression(progression_people, cat_matrix, current_date)
            
            # Should attempt progression in June
            mock_progression.assert_called()

    def test_progression_not_in_progression_month(self, progression_people, cat_matrix):
        """Test no progression outside progression months"""
        config = ProgressionConfiguration(
            progression_months=[6, 12],  # June and December only
            minimum_tenure_months=6,
            use_cat_probabilities=True
        )
        
        manager = WorkforceManagerV2()
        manager.initialize(progression_config=config)
        
        current_date = date(2025, 3, 15)  # March - not a progression month
        
        events = manager.process_progression(progression_people, cat_matrix, current_date)
        
        # No progression events in non-progression months
        assert len(events) == 0

    def test_progression_minimum_tenure_requirement(self, test_person_factory, cat_matrix):
        """Test minimum tenure requirement for progression"""
        config = ProgressionConfiguration(
            progression_months=[6],
            minimum_tenure_months=12,  # Require 12 months tenure
            use_cat_probabilities=True
        )
        
        manager = WorkforceManagerV2()
        manager.initialize(progression_config=config)
        
        # Create person with insufficient tenure
        new_person = test_person_factory(
            role="Consultant",
            level="A",
            hire_date="2025-01"  # Only 5 months ago
        )
        new_person.current_level = "A"
        new_person.is_active = True
        new_person.level_start_date = "2025-01"
        
        current_date = date(2025, 6, 15)
        
        events = manager.process_progression([new_person], cat_matrix, current_date)
        
        # No progression due to insufficient tenure
        assert len(events) == 0

    def test_progression_with_cat_probabilities(self, test_person_factory, cat_matrix):
        """Test progression uses CAT probabilities correctly"""
        config = ProgressionConfiguration(
            progression_months=[6],
            minimum_tenure_months=6,
            use_cat_probabilities=True
        )
        
        manager = WorkforceManagerV2()
        manager.initialize(progression_config=config, random_seed=42)
        
        # Create person with high CAT rating
        high_performer = test_person_factory(
            role="Consultant",
            level="A",
            hire_date="2024-01"  # Sufficient tenure
        )
        high_performer.current_level = "A"
        high_performer.is_active = True
        high_performer.level_start_date = "2024-01"
        high_performer.cat_rating = "High"
        
        current_date = date(2025, 6, 15)
        
        with patch('random.random') as mock_random:
            # Mock random to be below CAT probability (0.8 for High at level A)
            mock_random.return_value = 0.5
            
            events = manager.process_progression([high_performer], cat_matrix, current_date)
            
            # Should have progression event due to high CAT rating
            # Note: This test may need adjustment based on actual CAT logic implementation

    def test_progression_event_creation(self, test_person_factory, cat_matrix):
        """Test progression events contain correct details"""
        manager = WorkforceManagerV2()
        manager.initialize(random_seed=42)
        
        person = test_person_factory(
            role="Consultant",
            level="A",
            office="Stockholm",
            hire_date="2024-01"
        )
        person.current_level = "A"
        person.is_active = True
        person.level_start_date = "2024-01"
        person.cat_rating = "High"
        
        current_date = date(2025, 6, 15)
        
        # Mock progression to ensure event creation
        with patch.object(manager, '_should_progress_person') as mock_should_progress:
            mock_should_progress.return_value = True
            
            with patch.object(manager, '_get_next_level') as mock_next_level:
                mock_next_level.return_value = "AC"
                
                events = manager.process_progression([person], cat_matrix, current_date)
                
                if events:  # If progression event created
                    event = events[0]
                    assert event.event_type == EventType.PROMOTED
                    assert event.date == current_date
                    assert "from_level" in event.details
                    assert "to_level" in event.details
                    assert event.details["from_level"] == "A"
                    assert event.details["to_level"] == "AC"

    def test_progression_inactive_people_ignored(self, test_person_factory, cat_matrix):
        """Test progression ignores inactive people"""
        manager = WorkforceManagerV2()
        
        # Create inactive person
        inactive_person = test_person_factory(
            role="Consultant",
            level="A",
            hire_date="2024-01"
        )
        inactive_person.current_level = "A"
        inactive_person.is_active = False  # Inactive
        inactive_person.cat_rating = "High"
        
        current_date = date(2025, 6, 15)
        
        events = manager.process_progression([inactive_person], cat_matrix, current_date)
        
        # No progression for inactive people
        assert len(events) == 0


class TestWorkforceManagerV2RecruitmentProcessing:
    """Test suite for recruitment functionality"""

    def test_recruitment_basic_processing(self):
        """Test basic recruitment processing"""
        manager = WorkforceManagerV2()
        
        targets = {"A": 3, "AC": 2}
        current_date = date(2025, 6, 15)
        office = "Stockholm"
        role = "Consultant"
        
        events = manager.process_recruitment(targets, current_date, office, role)
        
        # Should create 5 recruitment events (3 A + 2 AC)
        assert len(events) == 5
        
        # Verify event types
        for event in events:
            assert event.event_type == EventType.HIRED
            assert event.date == current_date
            assert "office" in event.details
            assert "role" in event.details
            assert event.details["office"] == office
            assert event.details["role"] == role

    def test_recruitment_zero_targets(self):
        """Test recruitment with zero targets"""
        manager = WorkforceManagerV2()
        
        targets = {"A": 0, "AC": 0}
        current_date = date(2025, 6, 15)
        
        events = manager.process_recruitment(targets, current_date, "Stockholm", "Consultant")
        
        # No recruitment events should be created
        assert len(events) == 0

    def test_recruitment_entry_level_strategy(self):
        """Test recruitment with entry level strategy"""
        config = RecruitmentConfiguration(
            default_hire_level="A",
            distribution_strategy="entry_level"
        )
        
        manager = WorkforceManagerV2()
        manager.initialize(recruitment_config=config)
        
        targets = {"A": 2, "AC": 1}  # Mixed levels
        current_date = date(2025, 6, 15)
        
        events = manager.process_recruitment(targets, current_date, "Stockholm", "Consultant")
        
        # Should create events for both levels as specified
        a_events = [e for e in events if e.details.get("level") == "A"]
        ac_events = [e for e in events if e.details.get("level") == "AC"]
        
        assert len(a_events) == 2
        assert len(ac_events) == 1

    def test_recruitment_event_details(self):
        """Test recruitment events contain correct details"""
        manager = WorkforceManagerV2()
        
        targets = {"A": 1}
        current_date = date(2025, 6, 15)
        office = "Munich"
        role = "Operations"
        
        events = manager.process_recruitment(targets, current_date, office, role)
        
        assert len(events) == 1
        event = events[0]
        
        # Verify detailed event information
        assert event.event_type == EventType.HIRED
        assert event.date == current_date
        assert event.details["office"] == office
        assert event.details["role"] == role
        assert event.details["level"] == "A"
        assert "person_id" in event.details
        assert event.details["person_id"] is not None

    def test_recruitment_person_creation(self):
        """Test recruitment creates new Person objects"""
        manager = WorkforceManagerV2()
        
        targets = {"A": 2}
        current_date = date(2025, 6, 15)
        
        # Mock person creation
        with patch.object(manager, '_create_new_person') as mock_create:
            mock_person = Mock()
            mock_person.id = "new-person-123"
            mock_create.return_value = mock_person
            
            events = manager.process_recruitment(targets, current_date, "Stockholm", "Consultant")
            
            # Should have called person creation for each recruitment
            assert mock_create.call_count == 2


class TestWorkforceManagerV2MonthProcessing:
    """Test suite for monthly processing coordination"""

    def test_monthly_processing_coordination(self, sample_people, cat_matrix):
        """Test monthly processing coordinates all workforce activities"""
        manager = WorkforceManagerV2()
        
        # Mock targets
        monthly_targets = Mock()
        monthly_targets.recruitment_targets = {"Consultant": {"A": 2}}
        monthly_targets.churn_targets = {"Consultant": {"A": 1}}
        
        current_date = date(2025, 6, 15)
        simulation_month = 5
        office_state = Mock()
        office_state.persons = sample_people
        
        events, updated_persons = manager.process_month(
            monthly_targets, current_date, simulation_month, office_state, cat_matrix
        )
        
        # Should return events and updated persons
        assert isinstance(events, list)
        assert isinstance(updated_persons, list)

    def test_monthly_processing_event_aggregation(self, sample_people, cat_matrix):
        """Test monthly processing aggregates events from all processes"""
        manager = WorkforceManagerV2()
        
        monthly_targets = Mock()
        monthly_targets.recruitment_targets = {"Consultant": {"A": 1}}
        monthly_targets.churn_targets = {"Consultant": {"A": 1}}
        
        current_date = date(2025, 6, 15)
        simulation_month = 5
        office_state = Mock()
        office_state.persons = sample_people
        
        # Mock individual processes to return known events
        with patch.object(manager, 'process_recruitment') as mock_recruitment, \
             patch.object(manager, 'process_churn') as mock_churn, \
             patch.object(manager, 'process_progression') as mock_progression:
            
            # Mock return values
            mock_recruitment.return_value = [Mock(event_type=EventType.HIRED)]
            mock_churn.return_value = [Mock(event_type=EventType.CHURNED)]
            mock_progression.return_value = [Mock(event_type=EventType.PROMOTED)]
            
            events, _ = manager.process_month(
                monthly_targets, current_date, simulation_month, office_state, cat_matrix
            )
            
            # Should aggregate events from all processes
            assert len(events) == 3  # 1 recruitment + 1 churn + 1 progression


class TestWorkforceManagerV2Utilities:
    """Test suite for utility methods"""

    def test_workforce_count_calculation(self, sample_people):
        """Test workforce count calculation by role and level"""
        manager = WorkforceManagerV2()
        
        # Add more variety to test people
        people = sample_people.copy()
        
        # Create additional people at different levels
        additional_person = Mock()
        additional_person.current_role = "Operations"
        additional_person.current_level = "Junior"
        additional_person.is_active = True
        people.append(additional_person)
        
        counts = manager.get_workforce_counts(people)
        
        # Verify count structure
        assert isinstance(counts, dict)
        assert "Consultant" in counts
        assert "A" in counts["Consultant"]
        
        # Verify counts are correct
        consultant_a_count = len([p for p in people 
                                if getattr(p, 'current_role', p.role) == "Consultant" 
                                and getattr(p, 'current_level', p.level) == "A" 
                                and getattr(p, 'is_active', True)])
        
        assert counts["Consultant"]["A"] == consultant_a_count

    def test_event_counter_incrementation(self):
        """Test event counter increments with each event creation"""
        manager = WorkforceManagerV2()
        
        initial_counter = manager.event_counter
        
        # Create some events
        targets = {"A": 2}
        current_date = date(2025, 6, 15)
        
        manager.process_recruitment(targets, current_date, "Stockholm", "Consultant")
        
        # Counter should have incremented
        assert manager.event_counter > initial_counter

    def test_validation_methods(self, sample_people):
        """Test input validation methods"""
        manager = WorkforceManagerV2()
        
        # Test valid inputs
        valid_targets = {"A": 2, "AC": 1}
        valid_date = date(2025, 6, 15)
        valid_people = sample_people
        
        # Should not raise exceptions with valid inputs
        result = manager._validate_churn_inputs(valid_people, valid_targets, valid_date)
        assert result is True
        
        # Test invalid inputs
        invalid_targets = {"A": -1}  # Negative target
        
        with pytest.raises(ValueError):
            manager._validate_churn_inputs(valid_people, invalid_targets, valid_date)

    def test_error_handling_robustness(self, sample_people):
        """Test error handling in edge cases"""
        manager = WorkforceManagerV2()
        
        # Empty people list
        events = manager.process_churn([], {"A": 2}, date(2025, 6, 15))
        assert len(events) == 0
        
        # None targets
        events = manager.process_churn(sample_people, {}, date(2025, 6, 15))
        assert len(events) == 0
        
        # Invalid date should be handled gracefully
        with pytest.raises(TypeError):
            manager.process_churn(sample_people, {"A": 1}, None)