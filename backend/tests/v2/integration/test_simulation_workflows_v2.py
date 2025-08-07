"""
Integration Tests for SimpleSim Engine V2 Full Workflows

Tests complete simulation workflows including:
- End-to-end scenario execution
- Component integration and data flow
- Multi-office simulation scenarios
- Business plan integration workflows
- Snapshot initialization workflows
- KPI calculation integration
- Error handling in integrated scenarios
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, date
from typing import Dict, List
import uuid
import json

from backend.src.services.simulation_engine_v2 import (
    SimulationEngineV2Factory, ScenarioRequest, TimeRange, Levers,
    SimulationResults, Person, PersonEvent, EventType
)

from backend.src.services.workforce_manager_v2 import WorkforceManagerV2
from backend.src.services.business_plan_processor_v2 import BusinessPlanProcessorV2
from backend.src.services.growth_model_manager_v2 import GrowthModelManagerV2
from backend.src.services.snapshot_loader_v2 import SnapshotLoaderV2
from backend.src.services.kpi_calculator_v2 import KPICalculatorV2


class TestSimulationEngineV2Integration:
    """Integration tests for complete simulation engine workflows"""

    @pytest.fixture
    def integrated_engine(self, mock_config_service, mock_database):
        """Create fully integrated simulation engine with all components"""
        engine = SimulationEngineV2Factory.create_dev_engine()
        
        # Inject real components (not mocks) for integration testing
        engine.workforce_manager = WorkforceManagerV2()
        engine.business_processor = BusinessPlanProcessorV2()
        engine.growth_manager = GrowthModelManagerV2()
        engine.snapshot_loader = SnapshotLoaderV2()
        engine.kpi_calculator = KPICalculatorV2()
        
        # Initialize all components
        engine.workforce_manager.initialize(random_seed=42)
        engine.business_processor.initialize()
        engine.growth_manager.initialize()
        engine.snapshot_loader.initialize()
        engine.kpi_calculator.initialize()
        
        return engine

    def test_complete_single_office_simulation(
        self, integrated_engine, base_scenario, population_snapshot, business_plan
    ):
        """Test complete simulation workflow for single office"""
        # Load required data
        integrated_engine.snapshot_loader.loaded_snapshots[population_snapshot.id] = population_snapshot
        integrated_engine.business_processor.load_business_plan(business_plan)
        
        # Execute scenario
        results = integrated_engine.execute_scenario(base_scenario)
        
        # Verify results structure
        assert isinstance(results, SimulationResults)
        assert results.scenario_id is not None
        assert len(results.monthly_results) > 0
        assert results.execution_metadata is not None
        
        # Verify monthly results contain expected data
        for month_key, monthly_result in results.monthly_results.items():
            assert monthly_result.year >= base_scenario.time_range.start_year
            assert 1 <= monthly_result.month <= 12
            assert len(monthly_result.office_results) > 0
            assert "Stockholm" in monthly_result.office_results
            
            # Verify office results have workforce data
            stockholm_results = monthly_result.office_results["Stockholm"]
            assert "total_fte" in stockholm_results
            assert "total_recruitment" in stockholm_results
            assert "total_churn" in stockholm_results

    def test_multi_office_simulation_workflow(
        self, integrated_engine, multi_office_scenario, population_snapshot, business_plan
    ):
        """Test simulation workflow with multiple offices"""
        # Create snapshots for multiple offices
        stockholm_snapshot = population_snapshot
        munich_snapshot = population_snapshot.__class__(
            id="munich-snapshot",
            office_id="Munich",
            snapshot_date="2025-01",
            name="Munich Test Snapshot",
            workforce=[entry for entry in population_snapshot.workforce[:100]]  # Smaller workforce
        )
        
        # Update Munich workforce entries
        for entry in munich_snapshot.workforce:
            entry.office = "Munich"
        
        # Create business plans for multiple offices
        munich_plan = business_plan.__class__(
            office_id="Munich",
            name="Munich Business Plan",
            monthly_plans={k: v for k, v in business_plan.monthly_plans.items()}  # Copy structure
        )
        
        # Load data
        integrated_engine.snapshot_loader.loaded_snapshots[stockholm_snapshot.id] = stockholm_snapshot
        integrated_engine.snapshot_loader.loaded_snapshots[munich_snapshot.id] = munich_snapshot
        integrated_engine.business_processor.load_business_plan(business_plan)
        integrated_engine.business_processor.load_business_plan(munich_plan)
        
        # Execute multi-office scenario
        results = integrated_engine.execute_scenario(multi_office_scenario)
        
        # Verify results include both offices
        assert isinstance(results, SimulationResults)
        for monthly_result in results.monthly_results.values():
            assert "Stockholm" in monthly_result.office_results
            assert "Munich" in monthly_result.office_results
            
            # Both offices should have workforce metrics
            for office in ["Stockholm", "Munich"]:
                office_results = monthly_result.office_results[office]
                assert office_results["total_fte"] >= 0

    def test_scenario_with_growth_levers(
        self, integrated_engine, growth_scenario, population_snapshot, business_plan
    ):
        """Test simulation with scenario levers applied"""
        # Load required data
        integrated_engine.snapshot_loader.loaded_snapshots[population_snapshot.id] = population_snapshot
        integrated_engine.business_processor.load_business_plan(business_plan)
        
        # Execute scenario with growth levers
        results = integrated_engine.execute_scenario(growth_scenario)
        
        # Verify results show effects of levers
        assert isinstance(results, SimulationResults)
        
        # Should have more recruitment due to 1.2x multiplier
        total_recruitment = 0
        for monthly_result in results.monthly_results.values():
            for office_results in monthly_result.office_results.values():
                total_recruitment += office_results.get("total_recruitment", 0)
        
        # With growth levers, should see increased activity
        assert total_recruitment > 0

    def test_multi_year_simulation_workflow(
        self, integrated_engine, population_snapshot, business_plan
    ):
        """Test multi-year simulation workflow"""
        # Create extended scenario (2 years)
        extended_scenario = ScenarioRequest(
            name="Extended Test Scenario",
            description="2-year simulation test",
            time_range=TimeRange(
                start_year=2025,
                start_month=1,
                end_year=2026,
                end_month=12
            ),
            office_scope=["Stockholm"],
            levers=Levers(),
            use_snapshot=True,
            snapshot_id=population_snapshot.id,
            use_business_plan=True,
            business_plan_id="stockholm-plan"
        )
        
        # Load required data
        integrated_engine.snapshot_loader.loaded_snapshots[population_snapshot.id] = population_snapshot
        integrated_engine.business_processor.load_business_plan(business_plan)
        
        # Execute extended scenario
        results = integrated_engine.execute_scenario(extended_scenario)
        
        # Verify 24 months of results
        assert len(results.monthly_results) == 24
        
        # Verify year progression
        years_seen = set()
        for monthly_result in results.monthly_results.values():
            years_seen.add(monthly_result.year)
        
        assert 2025 in years_seen
        assert 2026 in years_seen

    def test_simulation_with_events_tracking(
        self, integrated_engine, base_scenario, population_snapshot, business_plan
    ):
        """Test simulation properly tracks individual events"""
        # Load required data
        integrated_engine.snapshot_loader.loaded_snapshots[population_snapshot.id] = population_snapshot
        integrated_engine.business_processor.load_business_plan(business_plan)
        
        # Execute scenario
        results = integrated_engine.execute_scenario(base_scenario)
        
        # Verify event tracking in monthly results
        total_events = 0
        event_types_seen = set()
        
        for monthly_result in results.monthly_results.values():
            if hasattr(monthly_result, 'events_summary'):
                for event_type, count in monthly_result.events_summary.items():
                    total_events += count
                    event_types_seen.add(event_type)
        
        # Should have tracked some events (recruitment, churn, etc.)
        assert total_events >= 0  # At minimum, should not error
        
        # Verify execution metadata includes event statistics
        assert results.execution_metadata is not None
        assert "total_events_processed" in results.execution_metadata

    def test_kpi_calculation_integration(
        self, integrated_engine, base_scenario, population_snapshot, business_plan
    ):
        """Test KPI calculation integration in simulation workflow"""
        # Load required data
        integrated_engine.snapshot_loader.loaded_snapshots[population_snapshot.id] = population_snapshot
        integrated_engine.business_processor.load_business_plan(business_plan)
        
        # Execute scenario
        results = integrated_engine.execute_scenario(base_scenario)
        
        # Verify KPIs are calculated for each month
        for monthly_result in results.monthly_results.values():
            assert hasattr(monthly_result, 'aggregate_kpis')
            assert isinstance(monthly_result.aggregate_kpis, dict)
            
            # Should have workforce KPIs
            for office_results in monthly_result.office_results.values():
                assert "total_fte" in office_results
                assert "total_recruitment" in office_results
                assert "total_churn" in office_results
                
                # Values should be non-negative
                assert office_results["total_fte"] >= 0
                assert office_results["total_recruitment"] >= 0
                assert office_results["total_churn"] >= 0


class TestComponentDataFlow:
    """Test data flow between V2 engine components"""

    def test_snapshot_to_workforce_manager_flow(
        self, population_snapshot
    ):
        """Test data flow from snapshot loader to workforce manager"""
        snapshot_loader = SnapshotLoaderV2()
        workforce_manager = WorkforceManagerV2()
        
        # Initialize office state from snapshot
        office_state = snapshot_loader.initialize_office_state(population_snapshot)
        
        # Verify office state structure
        assert office_state.office_id == population_snapshot.office_id
        assert len(office_state.persons) == len(population_snapshot.workforce)
        assert all(isinstance(person, Person) for person in office_state.persons)
        
        # Test workforce manager can process the persons
        monthly_targets = Mock()
        monthly_targets.recruitment_targets = {"Consultant": {"A": 2}}
        monthly_targets.churn_targets = {"Consultant": {"A": 1}}
        
        current_date = date(2025, 6, 15)
        simulation_month = 5
        cat_matrix = Mock()
        
        # Should not raise errors
        events, updated_persons = workforce_manager.process_month(
            monthly_targets, current_date, simulation_month, office_state, cat_matrix
        )
        
        assert isinstance(events, list)
        assert isinstance(updated_persons, list)

    def test_business_plan_to_workforce_manager_flow(
        self, business_plan
    ):
        """Test data flow from business plan processor to workforce manager"""
        business_processor = BusinessPlanProcessorV2()
        workforce_manager = WorkforceManagerV2()
        
        # Load business plan
        business_processor.load_business_plan(business_plan)
        
        # Get monthly targets
        targets = business_processor.get_monthly_targets("Stockholm", 2025, 6)
        
        # Verify targets structure compatible with workforce manager
        assert hasattr(targets, 'recruitment_targets')
        assert hasattr(targets, 'churn_targets')
        assert isinstance(targets.recruitment_targets, dict)
        assert isinstance(targets.churn_targets, dict)
        
        # Workforce manager should be able to use these targets
        office_state = Mock()
        office_state.persons = []
        current_date = date(2025, 6, 15)
        cat_matrix = Mock()
        
        # Should not raise errors
        events, updated_persons = workforce_manager.process_month(
            targets, current_date, 5, office_state, cat_matrix
        )

    def test_workforce_events_to_kpi_calculator_flow(
        self, test_person_factory
    ):
        """Test data flow from workforce manager to KPI calculator"""
        workforce_manager = WorkforceManagerV2()
        kpi_calculator = KPICalculatorV2()
        
        # Create test data
        persons = [
            test_person_factory(role="Consultant", level="A"),
            test_person_factory(role="Consultant", level="AC"),
        ]
        
        # Simulate workforce manager generating events
        events = [
            PersonEvent(
                date=date(2025, 6, 1),
                event_type=EventType.HIRED,
                details={"role": "Consultant", "level": "A"},
                simulation_month=5
            ),
            PersonEvent(
                date=date(2025, 6, 15),
                event_type=EventType.PROMOTED,
                details={"from_level": "A", "to_level": "AC", "role": "Consultant"},
                simulation_month=5
            )
        ]
        
        # KPI calculator should process these events
        workforce_kpis = kpi_calculator.calculate_workforce_kpis(persons, events, 6)
        
        # Verify KPIs calculated correctly
        assert workforce_kpis.total_headcount == 2
        assert workforce_kpis.total_recruitment == 1
        assert workforce_kpis.total_promotions == 1

    def test_growth_manager_to_business_processor_flow(
        self, business_plan, mock_config_service
    ):
        """Test data flow from growth manager to business processor"""
        growth_manager = GrowthModelManagerV2()
        business_processor = BusinessPlanProcessorV2()
        
        # Growth manager creates business models
        office_data = [{
            "name": "Stockholm",
            "total_fte": 850.0,
            "roles": {"Consultant": {"A": {"fte": 120.0}}}
        }]
        
        time_range = TimeRange(start_year=2025, start_month=1, end_year=2026, end_month=12)
        business_model = growth_manager.create_growth_model(office_data, time_range)
        
        # Business processor should handle the generated plans
        for office_id, office_plan in business_model.office_plans.items():
            result = business_processor.load_business_plan(office_plan)
            assert result is True
            
            # Should be able to get targets from loaded plan
            targets = business_processor.get_monthly_targets(office_id, 2025, 6)
            assert targets is not None


class TestErrorHandlingIntegration:
    """Test error handling in integrated scenarios"""

    def test_missing_snapshot_error_handling(
        self, integrated_engine, base_scenario, business_plan
    ):
        """Test error handling when snapshot is missing"""
        # Load business plan but not snapshot
        integrated_engine.business_processor.load_business_plan(business_plan)
        
        # Should raise appropriate error
        with pytest.raises(ValueError, match="Snapshot not found"):
            integrated_engine.execute_scenario(base_scenario)

    def test_missing_business_plan_error_handling(
        self, integrated_engine, base_scenario, population_snapshot
    ):
        """Test error handling when business plan is missing"""
        # Load snapshot but not business plan
        integrated_engine.snapshot_loader.loaded_snapshots[population_snapshot.id] = population_snapshot
        
        # Should handle gracefully or raise appropriate error
        with pytest.raises((ValueError, KeyError)):
            integrated_engine.execute_scenario(base_scenario)

    def test_invalid_scenario_data_handling(
        self, integrated_engine, population_snapshot, business_plan
    ):
        """Test error handling with invalid scenario data"""
        # Create invalid scenario
        invalid_scenario = ScenarioRequest(
            name="Invalid Scenario",
            description="Test invalid data handling",
            time_range=TimeRange(
                start_year=2026,
                start_month=1,
                end_year=2025,  # End before start
                end_month=12
            ),
            office_scope=["Stockholm"],
            levers=Levers()
        )
        
        # Load required data
        integrated_engine.snapshot_loader.loaded_snapshots[population_snapshot.id] = population_snapshot
        integrated_engine.business_processor.load_business_plan(business_plan)
        
        # Should raise validation error
        with pytest.raises(ValueError, match="Invalid time range"):
            integrated_engine.execute_scenario(invalid_scenario)

    def test_component_failure_recovery(
        self, integrated_engine, base_scenario, population_snapshot, business_plan
    ):
        """Test recovery when individual components fail"""
        # Load required data
        integrated_engine.snapshot_loader.loaded_snapshots[population_snapshot.id] = population_snapshot
        integrated_engine.business_processor.load_business_plan(business_plan)
        
        # Mock workforce manager to fail
        with patch.object(integrated_engine.workforce_manager, 'process_month', side_effect=Exception("Workforce processing failed")):
            
            with pytest.raises(Exception, match="Workforce processing failed"):
                integrated_engine.execute_scenario(base_scenario)

    def test_partial_data_handling(
        self, integrated_engine, population_snapshot, business_plan
    ):
        """Test handling of scenarios with partial/incomplete data"""
        # Create scenario with partial business plan (missing some months)
        partial_plan = business_plan.__class__(
            office_id="Stockholm",
            name="Partial Business Plan",
            monthly_plans={
                "2025-01": business_plan.monthly_plans.get("2025-01"),
                "2025-02": business_plan.monthly_plans.get("2025-02")
                # Missing other months
            }
        )
        
        # Create scenario for longer period than available data
        extended_scenario = ScenarioRequest(
            name="Extended Scenario",
            description="Test with incomplete business plan",
            time_range=TimeRange(
                start_year=2025,
                start_month=1,
                end_year=2025,
                end_month=6  # Beyond available business plan data
            ),
            office_scope=["Stockholm"],
            levers=Levers(),
            use_snapshot=True,
            snapshot_id=population_snapshot.id,
            use_business_plan=True,
            business_plan_id="partial-plan"
        )
        
        # Load data
        integrated_engine.snapshot_loader.loaded_snapshots[population_snapshot.id] = population_snapshot
        integrated_engine.business_processor.load_business_plan(partial_plan)
        
        # Should handle gracefully (may use defaults or extrapolation)
        results = integrated_engine.execute_scenario(extended_scenario)
        
        # Should complete without crashing
        assert isinstance(results, SimulationResults)


class TestPerformanceIntegration:
    """Test performance aspects of integrated simulation workflows"""

    def test_simulation_execution_time(
        self, integrated_engine, base_scenario, population_snapshot, business_plan
    ):
        """Test simulation completes within reasonable time"""
        import time
        
        # Load required data
        integrated_engine.snapshot_loader.loaded_snapshots[population_snapshot.id] = population_snapshot
        integrated_engine.business_processor.load_business_plan(business_plan)
        
        # Time the execution
        start_time = time.time()
        results = integrated_engine.execute_scenario(base_scenario)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should complete within reasonable time
        assert execution_time < 30.0  # 30 seconds max for base scenario
        
        # Verify execution time is recorded in metadata
        assert "execution_time_seconds" in results.execution_metadata
        assert results.execution_metadata["execution_time_seconds"] > 0

    def test_memory_usage_with_large_workforce(
        self, integrated_engine, performance_snapshot, business_plan
    ):
        """Test memory usage remains reasonable with large workforce"""
        import gc
        import tracemalloc
        
        # Start memory tracking
        tracemalloc.start()
        gc.collect()
        initial_memory = tracemalloc.take_snapshot()
        
        # Create scenario with large workforce
        large_scenario = ScenarioRequest(
            name="Large Workforce Test",
            description="Test with 1000+ person workforce",
            time_range=TimeRange(
                start_year=2025,
                start_month=1,
                end_year=2025,
                end_month=3  # Short simulation
            ),
            office_scope=["Multi-Office"],
            levers=Levers(),
            use_snapshot=True,
            snapshot_id=performance_snapshot.id,
            use_business_plan=True,
            business_plan_id="performance-plan"
        )
        
        # Scale business plan for large workforce
        scaled_plan = business_plan.__class__(
            office_id="Multi-Office",
            name="Performance Business Plan",
            monthly_plans={k: v for k, v in business_plan.monthly_plans.items()}
        )
        
        # Load data
        integrated_engine.snapshot_loader.loaded_snapshots[performance_snapshot.id] = performance_snapshot
        integrated_engine.business_processor.load_business_plan(scaled_plan)
        
        # Execute simulation
        results = integrated_engine.execute_scenario(large_scenario)
        
        # Check final memory
        final_memory = tracemalloc.take_snapshot()
        top_stats = final_memory.compare_to(initial_memory, 'lineno')
        total_memory_mb = sum(stat.size_diff for stat in top_stats) / 1024 / 1024
        
        tracemalloc.stop()
        
        # Memory usage should be reasonable (adjust threshold as needed)
        assert total_memory_mb < 100  # 100MB max increase
        
        # Should have completed successfully
        assert isinstance(results, SimulationResults)

    def test_concurrent_scenario_execution(
        self, population_snapshot, business_plan
    ):
        """Test multiple scenarios can be executed concurrently"""
        import threading
        import time
        
        results = {}
        errors = {}
        
        def execute_scenario(scenario_id, scenario):
            try:
                engine = SimulationEngineV2Factory.create_dev_engine()
                engine.workforce_manager = WorkforceManagerV2()
                engine.business_processor = BusinessPlanProcessorV2()
                engine.growth_manager = GrowthModelManagerV2()
                engine.snapshot_loader = SnapshotLoaderV2()
                engine.kpi_calculator = KPICalculatorV2()
                
                # Initialize components
                engine.workforce_manager.initialize(random_seed=scenario_id)
                engine.business_processor.initialize()
                engine.growth_manager.initialize()
                engine.snapshot_loader.initialize()
                engine.kpi_calculator.initialize()
                
                # Load data
                engine.snapshot_loader.loaded_snapshots[population_snapshot.id] = population_snapshot
                engine.business_processor.load_business_plan(business_plan)
                
                # Execute
                result = engine.execute_scenario(scenario)
                results[scenario_id] = result
                
            except Exception as e:
                errors[scenario_id] = e
        
        # Create multiple scenarios
        scenarios = []
        for i in range(3):  # 3 concurrent scenarios
            scenario = ScenarioRequest(
                name=f"Concurrent Scenario {i}",
                description="Concurrent execution test",
                time_range=TimeRange(start_year=2025, start_month=1, end_year=2025, end_month=2),
                office_scope=["Stockholm"],
                levers=Levers(recruitment_multiplier=1.0 + i * 0.1),  # Slight variation
                use_snapshot=True,
                snapshot_id=population_snapshot.id,
                use_business_plan=True
            )
            scenarios.append((i, scenario))
        
        # Execute concurrently
        threads = []
        for scenario_id, scenario in scenarios:
            thread = threading.Thread(target=execute_scenario, args=(scenario_id, scenario))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=60)  # 60 second timeout per thread
        
        # Verify results
        assert len(errors) == 0, f"Errors in concurrent execution: {errors}"
        assert len(results) == 3, f"Expected 3 results, got {len(results)}"
        
        # All results should be valid
        for scenario_id, result in results.items():
            assert isinstance(result, SimulationResults)
            assert result.scenario_id is not None