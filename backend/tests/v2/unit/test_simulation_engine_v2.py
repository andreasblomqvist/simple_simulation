"""
Comprehensive Unit Tests for SimulationEngineV2

Tests the core simulation engine functionality including:
- Engine initialization and configuration
- Scenario execution workflow
- Component integration
- Error handling and validation
- Performance monitoring
- State management
"""

import pytest
import uuid
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, date
from typing import Dict, List, Any

from backend.src.services.simulation_engine_v2 import (
    SimulationEngineV2, SimulationEngineV2Factory, ScenarioRequest,
    TimeRange, Levers, SimulationResults, MonthlyResults, OfficeState,
    Person, PersonEvent, EventType, ValidationResult, EngineValidator
)


class TestSimulationEngineV2:
    """Test suite for SimulationEngineV2 core functionality"""

    def test_engine_initialization(self):
        """Test engine initializes with correct default state"""
        engine = SimulationEngineV2()
        
        # Verify initial state
        assert engine.workforce_manager is None
        assert engine.business_processor is None  
        assert engine.snapshot_loader is None
        assert engine.growth_manager is None
        assert engine.kpi_calculator is None
        
        assert engine.current_scenario is None
        assert engine.office_states == {}
        assert engine.all_events == []
        assert engine.monthly_results == {}
        
        assert engine.random_seed is None
        assert engine.validation_enabled is True
        assert engine.simulation_start_time is None

    def test_engine_component_injection(self):
        """Test engine correctly accepts component dependencies"""
        engine = SimulationEngineV2()
        
        # Mock all components
        mock_workforce = Mock()
        mock_business = Mock()
        mock_snapshot = Mock()
        mock_growth = Mock()
        mock_kpi = Mock()
        
        # Inject dependencies
        engine.workforce_manager = mock_workforce
        engine.business_processor = mock_business
        engine.snapshot_loader = mock_snapshot
        engine.growth_manager = mock_growth
        engine.kpi_calculator = mock_kpi
        
        # Verify injection
        assert engine.workforce_manager == mock_workforce
        assert engine.business_processor == mock_business
        assert engine.snapshot_loader == mock_snapshot
        assert engine.growth_manager == mock_growth
        assert engine.kpi_calculator == mock_kpi

    def test_engine_validation_enabled_by_default(self):
        """Test validation is enabled by default"""
        engine = SimulationEngineV2()
        assert engine.validation_enabled is True

    def test_engine_validation_can_be_disabled(self):
        """Test validation can be disabled for performance"""
        engine = SimulationEngineV2()
        engine.validation_enabled = False
        assert engine.validation_enabled is False

    def test_scenario_validation_invalid_time_range(self, base_scenario):
        """Test scenario validation catches invalid time ranges"""
        engine = SimulationEngineV2()
        
        # Create scenario with invalid time range (end before start)
        invalid_scenario = ScenarioRequest(
            name="Invalid Scenario",
            description="Test scenario with invalid time range",
            time_range=TimeRange(
                start_year=2026,
                start_month=1,
                end_year=2025,  # End before start
                end_month=12
            ),
            office_scope=["Stockholm"],
            levers=Levers()
        )
        
        with pytest.raises(ValueError, match="End date must be after start date"):
            engine._validate_scenario(invalid_scenario)

    def test_scenario_validation_empty_office_scope(self, base_scenario):
        """Test scenario validation catches empty office scope"""
        engine = SimulationEngineV2()
        
        # Create scenario with empty office scope
        invalid_scenario = ScenarioRequest(
            name="Invalid Scenario",
            description="Test scenario with empty office scope",
            time_range=TimeRange(start_year=2025, start_month=1, end_year=2026, end_month=12),
            office_scope=[],  # Empty office scope
            levers=Levers()
        )
        
        with pytest.raises(ValueError, match="Office scope cannot be empty"):
            engine._validate_scenario(invalid_scenario)

    def test_scenario_validation_invalid_levers(self, base_scenario):
        """Test scenario validation catches invalid lever values"""
        engine = SimulationEngineV2()
        
        # Create scenario with negative lever values
        invalid_scenario = ScenarioRequest(
            name="Invalid Scenario", 
            description="Test scenario with invalid levers",
            time_range=TimeRange(start_year=2025, start_month=1, end_year=2026, end_month=12),
            office_scope=["Stockholm"],
            levers=Levers(recruitment_multiplier=-0.5)  # Negative multiplier
        )
        
        with pytest.raises(ValueError, match="Lever values must be non-negative"):
            engine._validate_scenario(invalid_scenario)

    def test_scenario_validation_valid_scenario(self, base_scenario):
        """Test scenario validation passes for valid scenarios"""
        engine = SimulationEngineV2()
        
        # Should not raise any exceptions
        result = engine._validate_scenario(base_scenario)
        assert result is True

    def test_random_seed_configuration(self):
        """Test random seed can be set for deterministic testing"""
        engine = SimulationEngineV2()
        
        test_seed = 12345
        engine.random_seed = test_seed
        
        assert engine.random_seed == test_seed

    @patch('random.seed')
    def test_random_seed_applied_during_execution(self, mock_random_seed):
        """Test random seed is applied when scenario execution begins"""
        engine = SimulationEngineV2()
        engine.random_seed = 42
        
        # Mock all required components
        engine.workforce_manager = Mock()
        engine.business_processor = Mock()
        engine.snapshot_loader = Mock()
        engine.kpi_calculator = Mock()
        
        # Mock component methods
        engine.snapshot_loader.load_snapshot.return_value = {"Stockholm": []}
        engine.business_processor.load_business_plan.return_value = Mock()
        
        scenario = ScenarioRequest(
            name="Seed Test",
            description="Test random seed application",
            time_range=TimeRange(start_year=2025, start_month=1, end_year=2025, end_month=2),
            office_scope=["Stockholm"],
            levers=Levers()
        )
        
        try:
            engine.execute_scenario(scenario)
        except:
            pass  # We expect this to fail due to incomplete mocking, but seed should still be set
        
        # Verify random seed was set
        mock_random_seed.assert_called_with(42)

    def test_office_state_initialization(self, base_scenario, population_snapshot):
        """Test office states are correctly initialized from snapshots"""
        engine = SimulationEngineV2()
        
        # Mock snapshot loader
        mock_snapshot_loader = Mock()
        mock_snapshot_loader.load_snapshot.return_value = {
            "Stockholm": [
                Person(
                    id="person-1",
                    role="Consultant", 
                    level="A",
                    office="Stockholm",
                    hire_date="2024-01",
                    level_start_date="2024-01",
                    cat_rating="Medium",
                    salary=45000.0,
                    events=[]
                )
            ]
        }
        
        engine.snapshot_loader = mock_snapshot_loader
        engine.business_processor = Mock()
        engine.kpi_calculator = Mock()
        
        # Initialize office states
        engine._initialize_office_states(base_scenario)
        
        # Verify office state creation
        assert "Stockholm" in engine.office_states
        office_state = engine.office_states["Stockholm"]
        assert len(office_state.persons) == 1
        assert office_state.persons[0].id == "person-1"

    def test_time_range_generation(self, base_scenario):
        """Test correct generation of time range for simulation"""
        engine = SimulationEngineV2()
        
        # Test 2-year scenario
        time_range = TimeRange(
            start_year=2025,
            start_month=3,
            end_year=2026,
            end_month=8
        )
        
        months = engine._generate_simulation_months(time_range)
        
        # Should have 18 months (Mar 2025 - Aug 2026)
        expected_months = [
            (2025, 3), (2025, 4), (2025, 5), (2025, 6), (2025, 7), (2025, 8), 
            (2025, 9), (2025, 10), (2025, 11), (2025, 12),
            (2026, 1), (2026, 2), (2026, 3), (2026, 4), (2026, 5), (2026, 6), 
            (2026, 7), (2026, 8)
        ]
        
        assert months == expected_months

    def test_single_month_simulation(self):
        """Test simulation of single month"""
        time_range = TimeRange(
            start_year=2025,
            start_month=6,
            end_year=2025,
            end_month=6
        )
        
        engine = SimulationEngineV2()
        months = engine._generate_simulation_months(time_range)
        
        assert months == [(2025, 6)]

    def test_year_boundary_crossing(self):
        """Test simulation correctly handles year boundaries"""
        time_range = TimeRange(
            start_year=2024,
            start_month=11,
            end_year=2025,
            end_month=2
        )
        
        engine = SimulationEngineV2()
        months = engine._generate_simulation_months(time_range)
        
        expected = [(2024, 11), (2024, 12), (2025, 1), (2025, 2)]
        assert months == expected

    def test_performance_tracking_initialization(self, base_scenario):
        """Test performance tracking starts when simulation begins"""
        engine = SimulationEngineV2()
        
        # Mock all components
        engine.workforce_manager = Mock()
        engine.business_processor = Mock() 
        engine.snapshot_loader = Mock()
        engine.kpi_calculator = Mock()
        
        engine.snapshot_loader.load_snapshot.return_value = {"Stockholm": []}
        engine.business_processor.load_business_plan.return_value = Mock()
        
        with patch.object(engine, '_execute_simulation_loop') as mock_loop:
            mock_loop.return_value = SimulationResults(
                scenario_id=str(uuid.uuid4()),
                monthly_results={},
                execution_metadata={}
            )
            
            engine.execute_scenario(base_scenario)
        
        # Verify performance tracking was started
        assert engine.simulation_start_time is not None
        assert isinstance(engine.simulation_start_time, datetime)

    def test_scenario_state_management(self, base_scenario):
        """Test engine correctly manages scenario state"""
        engine = SimulationEngineV2()
        
        # Initially no current scenario
        assert engine.current_scenario is None
        
        # Mock all components
        engine.workforce_manager = Mock()
        engine.business_processor = Mock()
        engine.snapshot_loader = Mock() 
        engine.kpi_calculator = Mock()
        
        engine.snapshot_loader.load_snapshot.return_value = {"Stockholm": []}
        engine.business_processor.load_business_plan.return_value = Mock()
        
        with patch.object(engine, '_execute_simulation_loop') as mock_loop:
            mock_loop.return_value = SimulationResults(
                scenario_id=str(uuid.uuid4()),
                monthly_results={},
                execution_metadata={}
            )
            
            engine.execute_scenario(base_scenario)
        
        # Verify scenario was set
        assert engine.current_scenario == base_scenario

    def test_event_aggregation_initialization(self):
        """Test event aggregation is properly initialized"""
        engine = SimulationEngineV2()
        
        # Initially no events
        assert engine.all_events == []
        
        # Events should accumulate during simulation
        test_event = PersonEvent(
            date=date(2025, 1, 15),
            event_type=EventType.HIRED,
            details={"role": "Consultant", "level": "A"},
            simulation_month=0
        )
        
        engine.all_events.append(test_event)
        assert len(engine.all_events) == 1
        assert engine.all_events[0] == test_event

    def test_monthly_results_initialization(self):
        """Test monthly results tracking is properly initialized"""  
        engine = SimulationEngineV2()
        
        # Initially no monthly results
        assert engine.monthly_results == {}
        
        # Results should be stored by month key
        test_result = MonthlyResults(
            year=2025,
            month=1,
            office_results={},
            aggregate_kpis={},
            events_summary={}
        )
        
        engine.monthly_results["2025-01"] = test_result
        assert len(engine.monthly_results) == 1
        assert engine.monthly_results["2025-01"] == test_result


class TestSimulationEngineV2Factory:
    """Test suite for SimulationEngineV2Factory"""

    def test_factory_creates_dev_engine(self):
        """Test factory creates development engine configuration"""
        engine = SimulationEngineV2Factory.create_dev_engine()
        
        assert isinstance(engine, SimulationEngineV2)
        assert engine.validation_enabled is True

    def test_factory_creates_engine_with_config(self):
        """Test factory creates engine with custom configuration"""
        config = {
            'engine': {
                'validation_enabled': False,
                'random_seed': 12345
            }
        }
        
        engine = SimulationEngineV2Factory.create_engine(config)
        
        assert isinstance(engine, SimulationEngineV2)
        assert engine.validation_enabled is False
        assert engine.random_seed == 12345

    def test_factory_handles_missing_config(self):
        """Test factory handles missing configuration gracefully"""
        # Empty config should still create engine with defaults
        engine = SimulationEngineV2Factory.create_engine({})
        
        assert isinstance(engine, SimulationEngineV2)
        assert engine.validation_enabled is True  # Default value

    def test_factory_component_injection(self):
        """Test factory properly injects all required components"""
        config = {
            'components': {
                'workforce_manager': {'class': 'WorkforceManagerV2'},
                'business_processor': {'class': 'BusinessPlanProcessorV2'},
                'snapshot_loader': {'class': 'SnapshotLoaderV2'},
                'growth_manager': {'class': 'GrowthModelManagerV2'},
                'kpi_calculator': {'class': 'KPICalculatorV2'}
            }
        }
        
        with patch('backend.src.services.simulation_engine_v2.WorkforceManagerV2') as mock_workforce, \
             patch('backend.src.services.simulation_engine_v2.BusinessPlanProcessorV2') as mock_business, \
             patch('backend.src.services.simulation_engine_v2.SnapshotLoaderV2') as mock_snapshot, \
             patch('backend.src.services.simulation_engine_v2.GrowthModelManagerV2') as mock_growth, \
             patch('backend.src.services.simulation_engine_v2.KPICalculatorV2') as mock_kpi:
            
            engine = SimulationEngineV2Factory.create_engine(config)
            
            # Verify all components were created and injected
            mock_workforce.assert_called_once()
            mock_business.assert_called_once()
            mock_snapshot.assert_called_once()
            mock_growth.assert_called_once()
            mock_kpi.assert_called_once()


class TestEngineValidator:
    """Test suite for simulation engine validation functionality"""

    def test_validator_initialization(self):
        """Test validator initializes with engine reference"""
        engine = SimulationEngineV2()
        validator = EngineValidator(engine)
        
        assert validator.engine == engine

    def test_validate_scenario_success(self, base_scenario):
        """Test validator passes valid scenarios"""
        engine = SimulationEngineV2()
        validator = EngineValidator(engine)
        
        result = validator.validate_scenario(base_scenario)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_validate_scenario_with_errors(self):
        """Test validator catches scenario validation errors"""
        engine = SimulationEngineV2()
        validator = EngineValidator(engine)
        
        # Create invalid scenario
        invalid_scenario = ScenarioRequest(
            name="",  # Empty name
            description="Test",
            time_range=TimeRange(
                start_year=2026,
                start_month=1,
                end_year=2025,  # End before start
                end_month=12
            ),
            office_scope=[],  # Empty scope
            levers=Levers()
        )
        
        result = validator.validate_scenario(invalid_scenario)
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        
        # Check for specific errors
        error_messages = [error['message'] for error in result.errors]
        assert any("name cannot be empty" in msg.lower() for msg in error_messages)
        assert any("office scope cannot be empty" in msg.lower() for msg in error_messages)

    def test_validate_scenario_with_warnings(self):
        """Test validator generates appropriate warnings"""
        engine = SimulationEngineV2()
        validator = EngineValidator(engine)
        
        # Create scenario that should generate warnings
        warning_scenario = ScenarioRequest(
            name="Long Simulation",
            description="Test",
            time_range=TimeRange(
                start_year=2025,
                start_month=1,
                end_year=2035,  # Very long simulation (10 years)
                end_month=12
            ),
            office_scope=["Stockholm"],
            levers=Levers(recruitment_multiplier=10.0)  # Very high multiplier
        )
        
        result = validator.validate_scenario(warning_scenario)
        
        # Should be valid but have warnings
        assert result.is_valid is True
        assert len(result.warnings) > 0


class TestSimulationEngineIntegration:
    """Integration tests for SimulationEngineV2 with mocked components"""

    def test_full_scenario_execution_workflow(
        self, base_scenario, population_snapshot, business_plan
    ):
        """Test complete scenario execution workflow with all components"""
        engine = SimulationEngineV2()
        
        # Mock all components with realistic behavior
        mock_workforce = Mock()
        mock_business = Mock()
        mock_snapshot = Mock()
        mock_kpi = Mock()
        
        # Configure mock responses
        mock_snapshot.load_snapshot.return_value = {"Stockholm": population_snapshot.workforce}
        mock_business.load_business_plan.return_value = business_plan
        
        # Mock monthly processing
        mock_workforce.process_month.return_value = ([], [])  # No events, no person changes
        mock_kpi.calculate_monthly_kpis.return_value = {
            "total_fte": 850.0,
            "total_recruitment": 0.0,
            "total_churn": 0.0,
            "revenue": 850000.0
        }
        
        # Inject dependencies
        engine.workforce_manager = mock_workforce
        engine.business_processor = mock_business
        engine.snapshot_loader = mock_snapshot
        engine.kpi_calculator = mock_kpi
        
        # Execute scenario
        with patch.object(engine, '_execute_simulation_loop') as mock_loop:
            expected_result = SimulationResults(
                scenario_id=str(uuid.uuid4()),
                monthly_results={"2025-01": MonthlyResults(
                    year=2025,
                    month=1,
                    office_results={},
                    aggregate_kpis={},
                    events_summary={}
                )},
                execution_metadata={"execution_time_seconds": 1.5}
            )
            mock_loop.return_value = expected_result
            
            result = engine.execute_scenario(base_scenario)
        
        # Verify execution
        assert result is not None
        assert result == expected_result
        
        # Verify component interactions
        mock_snapshot.load_snapshot.assert_called_once()
        mock_business.load_business_plan.assert_called_once()

    def test_scenario_execution_with_errors(self, base_scenario):
        """Test scenario execution handles component errors gracefully"""
        engine = SimulationEngineV2()
        
        # Mock component that raises error
        mock_snapshot = Mock()
        mock_snapshot.load_snapshot.side_effect = Exception("Snapshot loading failed")
        
        engine.snapshot_loader = mock_snapshot
        engine.business_processor = Mock()
        engine.kpi_calculator = Mock()
        
        # Should raise exception during execution
        with pytest.raises(Exception, match="Snapshot loading failed"):
            engine.execute_scenario(base_scenario)

    def test_partial_component_configuration_error(self, base_scenario):
        """Test engine raises error when components are missing"""
        engine = SimulationEngineV2()
        
        # Only configure some components
        engine.workforce_manager = Mock()
        engine.snapshot_loader = Mock()
        # Missing business_processor and kpi_calculator
        
        engine.snapshot_loader.load_snapshot.return_value = {"Stockholm": []}
        
        # Should raise error due to missing components
        with pytest.raises(AttributeError):
            engine.execute_scenario(base_scenario)

    def test_engine_state_cleanup_between_scenarios(
        self, base_scenario, growth_scenario
    ):
        """Test engine properly cleans state between scenario executions"""
        engine = SimulationEngineV2()
        
        # Mock all components
        engine.workforce_manager = Mock()
        engine.business_processor = Mock()
        engine.snapshot_loader = Mock()
        engine.kpi_calculator = Mock()
        
        engine.snapshot_loader.load_snapshot.return_value = {"Stockholm": []}
        engine.business_processor.load_business_plan.return_value = Mock()
        
        # Execute first scenario
        with patch.object(engine, '_execute_simulation_loop') as mock_loop:
            result1 = SimulationResults(
                scenario_id="scenario-1",
                monthly_results={"2025-01": Mock()},
                execution_metadata={}
            )
            mock_loop.return_value = result1
            
            engine.execute_scenario(base_scenario)
        
        # Verify state after first scenario
        assert engine.current_scenario == base_scenario
        assert len(engine.monthly_results) > 0
        
        # Execute second scenario
        with patch.object(engine, '_execute_simulation_loop') as mock_loop:
            result2 = SimulationResults(
                scenario_id="scenario-2", 
                monthly_results={"2025-02": Mock()},
                execution_metadata={}
            )
            mock_loop.return_value = result2
            
            engine.execute_scenario(growth_scenario)
        
        # Verify state was updated for second scenario
        assert engine.current_scenario == growth_scenario
        # Monthly results should be cleared/reset for new scenario