"""
Performance Tests for SimpleSim Engine V2

Tests performance characteristics including:
- Load testing with large datasets (1000+ persons)
- Multi-year simulation performance
- Memory usage monitoring and optimization
- Execution time benchmarks
- Concurrent simulation performance
- Component performance profiling
- Scalability testing
"""

import pytest
import time
import threading
import gc
import psutil
import os
from unittest.mock import Mock, patch
from datetime import datetime, date
import statistics

from backend.src.services.simulation_engine_v2 import (
    SimulationEngineV2Factory, ScenarioRequest, TimeRange, Levers
)


class TestSimulationEngineV2Performance:
    """Performance tests for simulation engine execution"""

    @pytest.fixture
    def performance_engine(self):
        """Create optimized engine for performance testing"""
        engine = SimulationEngineV2Factory.create_dev_engine()
        
        # Disable validation for performance
        engine.validation_enabled = False
        
        # Enable caching for optimal performance
        if hasattr(engine.kpi_calculator, 'cache_enabled'):
            engine.kpi_calculator.cache_enabled = True
            
        return engine

    def test_large_workforce_simulation_performance(
        self, performance_engine, performance_snapshot, business_plan
    ):
        """Test performance with large workforce (1000+ persons)"""
        # Create large simulation scenario
        large_scenario = ScenarioRequest(
            name="Large Workforce Performance Test",
            description="Performance test with 1000+ person workforce",
            time_range=TimeRange(
                start_year=2025,
                start_month=1,
                end_year=2025,
                end_month=6  # 6 months for performance test
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
        performance_engine.snapshot_loader.loaded_snapshots[performance_snapshot.id] = performance_snapshot
        performance_engine.business_processor.load_business_plan(scaled_plan)
        
        # Measure execution time
        start_time = time.time()
        results = performance_engine.execute_scenario(large_scenario)
        end_time = time.time()
        
        execution_time = end_time - start_time
        workforce_size = len(performance_snapshot.workforce)
        
        # Performance assertions
        assert execution_time < 60.0  # Should complete within 60 seconds
        assert results is not None
        assert len(results.monthly_results) == 6
        
        # Calculate performance metrics
        persons_per_second = workforce_size / execution_time
        months_per_second = 6 / execution_time
        
        print(f"\nPerformance Metrics:")
        print(f"Workforce size: {workforce_size} persons")
        print(f"Execution time: {execution_time:.2f} seconds")
        print(f"Throughput: {persons_per_second:.0f} persons/second")
        print(f"Monthly processing rate: {months_per_second:.2f} months/second")
        
        # Performance targets
        assert persons_per_second > 50   # At least 50 persons per second
        assert months_per_second > 0.15  # At least 0.15 months per second

    def test_multi_year_simulation_performance(
        self, performance_engine, population_snapshot, business_plan
    ):
        """Test performance for multi-year simulations"""
        # Create 3-year simulation
        long_scenario = ScenarioRequest(
            name="Multi-Year Performance Test",
            description="Performance test for 3-year simulation",
            time_range=TimeRange(
                start_year=2025,
                start_month=1,
                end_year=2027,
                end_month=12
            ),
            office_scope=["Stockholm"],
            levers=Levers(),
            use_snapshot=True,
            snapshot_id=population_snapshot.id,
            use_business_plan=True,
            business_plan_id="long-term-plan"
        )
        
        # Load data
        performance_engine.snapshot_loader.loaded_snapshots[population_snapshot.id] = population_snapshot
        performance_engine.business_processor.load_business_plan(business_plan)
        
        # Measure execution time
        start_time = time.time()
        results = performance_engine.execute_scenario(long_scenario)
        end_time = time.time()
        
        execution_time = end_time - start_time
        total_months = 36  # 3 years
        
        # Performance assertions
        assert execution_time < 180.0  # Should complete within 3 minutes
        assert len(results.monthly_results) == total_months
        
        # Verify linear scaling (roughly)
        months_per_second = total_months / execution_time
        
        print(f"\nMulti-Year Performance:")
        print(f"Total months simulated: {total_months}")
        print(f"Execution time: {execution_time:.2f} seconds")
        print(f"Processing rate: {months_per_second:.3f} months/second")
        
        assert months_per_second > 0.2  # At least 0.2 months per second

    def test_memory_usage_monitoring(
        self, performance_engine, performance_snapshot, business_plan, memory_profiler
    ):
        """Test memory usage during simulation execution"""
        # Create memory-intensive scenario
        memory_scenario = ScenarioRequest(
            name="Memory Usage Test",
            description="Monitor memory usage during simulation",
            time_range=TimeRange(
                start_year=2025,
                start_month=1,
                end_year=2025,
                end_month=12
            ),
            office_scope=["Multi-Office"],
            levers=Levers(),
            use_snapshot=True,
            snapshot_id=performance_snapshot.id,
            use_business_plan=True
        )
        
        # Scale business plan
        scaled_plan = business_plan.__class__(
            office_id="Multi-Office",
            name="Memory Test Plan",
            monthly_plans={k: v for k, v in business_plan.monthly_plans.items()}
        )
        
        # Load data
        performance_engine.snapshot_loader.loaded_snapshots[performance_snapshot.id] = performance_snapshot
        performance_engine.business_processor.load_business_plan(scaled_plan)
        
        # Profile memory usage
        results, memory_usage = memory_profiler(
            performance_engine.execute_scenario,
            memory_scenario
        )
        
        # Memory assertions
        memory_mb = memory_usage / (1024 * 1024)  # Convert to MB
        workforce_size = len(performance_snapshot.workforce)
        memory_per_person = memory_mb / workforce_size
        
        print(f"\nMemory Usage:")
        print(f"Peak memory usage: {memory_mb:.1f} MB")
        print(f"Memory per person: {memory_per_person:.3f} MB/person")
        
        # Performance targets
        assert memory_mb < 200  # Should use less than 200MB
        assert memory_per_person < 0.2  # Less than 0.2 MB per person
        assert results is not None

    def test_concurrent_simulation_performance(
        self, population_snapshot, business_plan
    ):
        """Test performance with concurrent simulations"""
        num_concurrent = 3
        results = {}
        errors = {}
        execution_times = []
        
        def run_simulation(sim_id):
            try:
                # Create independent engine for each thread
                engine = SimulationEngineV2Factory.create_dev_engine()
                engine.validation_enabled = False
                
                # Initialize components
                engine.workforce_manager.initialize(random_seed=sim_id)
                engine.business_processor.initialize()
                engine.growth_manager.initialize()
                engine.snapshot_loader.initialize()
                engine.kpi_calculator.initialize()
                
                scenario = ScenarioRequest(
                    name=f"Concurrent Test {sim_id}",
                    description="Concurrent performance test",
                    time_range=TimeRange(start_year=2025, start_month=1, end_year=2025, end_month=3),
                    office_scope=["Stockholm"],
                    levers=Levers(recruitment_multiplier=1.0 + sim_id * 0.1),
                    use_snapshot=True,
                    snapshot_id=population_snapshot.id,
                    use_business_plan=True
                )
                
                # Load data
                engine.snapshot_loader.loaded_snapshots[population_snapshot.id] = population_snapshot
                engine.business_processor.load_business_plan(business_plan)
                
                # Execute with timing
                start_time = time.time()
                result = engine.execute_scenario(scenario)
                end_time = time.time()
                
                execution_times.append(end_time - start_time)
                results[sim_id] = result
                
            except Exception as e:
                errors[sim_id] = e
        
        # Run concurrent simulations
        threads = []
        for i in range(num_concurrent):
            thread = threading.Thread(target=run_simulation, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=120)  # 2 minute timeout per thread
        
        # Analyze results
        assert len(errors) == 0, f"Errors in concurrent execution: {errors}"
        assert len(results) == num_concurrent
        assert len(execution_times) == num_concurrent
        
        avg_execution_time = statistics.mean(execution_times)
        max_execution_time = max(execution_times)
        
        print(f"\nConcurrent Performance:")
        print(f"Concurrent simulations: {num_concurrent}")
        print(f"Average execution time: {avg_execution_time:.2f} seconds")
        print(f"Maximum execution time: {max_execution_time:.2f} seconds")
        
        # Performance targets
        assert avg_execution_time < 30.0  # Average under 30 seconds
        assert max_execution_time < 45.0  # Max under 45 seconds

    def test_cpu_usage_monitoring(
        self, performance_engine, population_snapshot, business_plan
    ):
        """Test CPU usage during simulation execution"""
        # Create CPU-intensive scenario
        cpu_scenario = ScenarioRequest(
            name="CPU Usage Test",
            description="Monitor CPU usage during simulation",
            time_range=TimeRange(
                start_year=2025,
                start_month=1,
                end_year=2025,
                end_month=6
            ),
            office_scope=["Stockholm"],
            levers=Levers(),
            use_snapshot=True,
            snapshot_id=population_snapshot.id,
            use_business_plan=True
        )
        
        # Load data
        performance_engine.snapshot_loader.loaded_snapshots[population_snapshot.id] = population_snapshot
        performance_engine.business_processor.load_business_plan(business_plan)
        
        # Monitor CPU usage
        process = psutil.Process(os.getpid())
        cpu_samples = []
        
        def monitor_cpu():
            while monitoring:
                cpu_samples.append(process.cpu_percent())
                time.sleep(0.1)
        
        # Start monitoring
        monitoring = True
        monitor_thread = threading.Thread(target=monitor_cpu)
        monitor_thread.start()
        
        try:
            # Execute simulation
            start_time = time.time()
            results = performance_engine.execute_scenario(cpu_scenario)
            end_time = time.time()
            
        finally:
            # Stop monitoring
            monitoring = False
            monitor_thread.join(timeout=1)
        
        if cpu_samples:
            avg_cpu = statistics.mean(cpu_samples)
            max_cpu = max(cpu_samples)
            
            print(f"\nCPU Usage:")
            print(f"Average CPU usage: {avg_cpu:.1f}%")
            print(f"Peak CPU usage: {max_cpu:.1f}%")
            print(f"Execution time: {end_time - start_time:.2f} seconds")
            
            # CPU usage should be reasonable
            assert avg_cpu < 80.0  # Average under 80%
            assert max_cpu < 95.0  # Peak under 95%
        
        assert results is not None


class TestComponentPerformance:
    """Performance tests for individual components"""

    def test_workforce_manager_performance(
        self, sample_workforce_entries, cat_matrix
    ):
        """Test workforce manager performance with large datasets"""
        from backend.src.services.workforce_manager_v2 import WorkforceManagerV2
        
        manager = WorkforceManagerV2()
        manager.initialize(random_seed=42)
        
        # Create large person dataset
        persons = []
        for i in range(1000):
            person = Mock()
            person.id = f"person-{i}"
            person.current_role = "Consultant"
            person.current_level = "A"
            person.is_active = True
            person.office = "Stockholm"
            persons.append(person)
        
        # Test churn processing performance
        targets = {"A": 50}  # Churn 50 people
        current_date = date(2025, 6, 15)
        
        start_time = time.time()
        events = manager.process_churn(persons, targets, current_date)
        end_time = time.time()
        
        churn_time = end_time - start_time
        
        print(f"\nWorkforce Manager Performance:")
        print(f"Churn processing time: {churn_time:.3f} seconds")
        print(f"Persons processed: {len(persons)}")
        print(f"Processing rate: {len(persons)/churn_time:.0f} persons/second")
        
        assert churn_time < 1.0  # Should complete in under 1 second
        assert len(events) == 50
        
        # Test recruitment performance
        recruitment_targets = {"A": 100}  # Recruit 100 people
        
        start_time = time.time()
        recruitment_events = manager.process_recruitment(
            recruitment_targets, current_date, "Stockholm", "Consultant"
        )
        end_time = time.time()
        
        recruitment_time = end_time - start_time
        
        print(f"Recruitment processing time: {recruitment_time:.3f} seconds")
        print(f"Recruitment rate: {len(recruitment_events)/recruitment_time:.0f} recruitments/second")
        
        assert recruitment_time < 0.5  # Should complete in under 0.5 seconds
        assert len(recruitment_events) == 100

    def test_kpi_calculator_performance(self, test_person_factory):
        """Test KPI calculator performance with large datasets"""
        from backend.src.services.kpi_calculator_v2 import KPICalculatorV2
        
        calculator = KPICalculatorV2()
        calculator.initialize(cache_enabled=True)
        
        # Create large dataset
        persons = []
        events = []
        
        for i in range(2000):  # Large workforce
            person = test_person_factory(
                role="Consultant", 
                level=["A", "AC", "C"][i % 3],
                office=["Stockholm", "Munich", "London"][i % 3]
            )
            persons.append(person)
            
            # Add some events
            if i < 100:  # Some recruitment events
                event = Mock()
                event.event_type = "hired"
                event.details = {"role": "Consultant", "level": "A"}
                events.append(event)
        
        # Test workforce KPI calculation performance
        start_time = time.time()
        workforce_kpis = calculator.calculate_workforce_kpis(persons, events, 6)
        end_time = time.time()
        
        kpi_time = end_time - start_time
        
        print(f"\nKPI Calculator Performance:")
        print(f"Workforce KPI calculation time: {kpi_time:.3f} seconds")
        print(f"Persons analyzed: {len(persons)}")
        print(f"Processing rate: {len(persons)/kpi_time:.0f} persons/second")
        
        assert kpi_time < 2.0  # Should complete in under 2 seconds
        assert workforce_kpis.total_headcount == 2000

    def test_business_processor_performance(self, business_plan):
        """Test business processor performance with complex plans"""
        from backend.src.services.business_plan_processor_v2 import BusinessPlanProcessorV2
        from backend.src.services.simulation_engine_v2 import GrowthRates
        
        processor = BusinessPlanProcessorV2()
        processor.initialize()
        
        # Load business plan
        processor.load_business_plan(business_plan)
        
        # Test monthly target extraction performance
        start_time = time.time()
        
        for year in range(2025, 2028):  # 3 years
            for month in range(1, 13):  # 12 months each
                targets = processor.get_monthly_targets("Stockholm", year, month)
        
        end_time = time.time()
        
        extraction_time = end_time - start_time
        total_extractions = 3 * 12  # 36 extractions
        
        print(f"\nBusiness Processor Performance:")
        print(f"Monthly extraction time: {extraction_time:.3f} seconds")
        print(f"Total extractions: {total_extractions}")
        print(f"Extraction rate: {total_extractions/extraction_time:.0f} extractions/second")
        
        assert extraction_time < 1.0  # Should complete in under 1 second
        
        # Test growth rate application performance
        growth_rates = GrowthRates()
        
        start_time = time.time()
        result = processor.apply_growth_rates(business_plan, growth_rates, 2026)
        end_time = time.time()
        
        growth_time = end_time - start_time
        
        print(f"Growth rate application time: {growth_time:.3f} seconds")
        
        assert growth_time < 0.5  # Should complete in under 0.5 seconds
        assert result is True

    def test_snapshot_loader_performance(self, large_workforce_entries):
        """Test snapshot loader performance with large datasets"""
        from backend.src.services.snapshot_loader_v2 import SnapshotLoaderV2
        from backend.src.services.simulation_engine_v2 import PopulationSnapshot
        
        loader = SnapshotLoaderV2()
        loader.initialize()
        
        # Create large snapshot
        large_snapshot = PopulationSnapshot(
            id="large-performance-snapshot",
            office_id="Performance-Office",
            snapshot_date="2025-01",
            name="Large Performance Snapshot",
            workforce=large_workforce_entries
        )
        
        # Test office state initialization performance
        start_time = time.time()
        office_state = loader.initialize_office_state(large_snapshot)
        end_time = time.time()
        
        initialization_time = end_time - start_time
        workforce_size = len(large_workforce_entries)
        
        print(f"\nSnapshot Loader Performance:")
        print(f"Office state initialization time: {initialization_time:.3f} seconds")
        print(f"Workforce size: {workforce_size}")
        print(f"Processing rate: {workforce_size/initialization_time:.0f} persons/second")
        
        assert initialization_time < 3.0  # Should complete in under 3 seconds
        assert len(office_state.persons) == workforce_size
        
        # Test validation performance
        start_time = time.time()
        validation_result = loader.validate_snapshot(large_snapshot)
        end_time = time.time()
        
        validation_time = end_time - start_time
        
        print(f"Snapshot validation time: {validation_time:.3f} seconds")
        print(f"Validation rate: {workforce_size/validation_time:.0f} persons/second")
        
        assert validation_time < 2.0  # Should complete in under 2 seconds
        assert validation_result.is_valid is True


class TestScalabilityLimits:
    """Test scalability limits and breaking points"""

    @pytest.mark.slow
    def test_maximum_workforce_size(self):
        """Test maximum workforce size the system can handle"""
        from backend.src.services.simulation_engine_v2 import PopulationSnapshot, WorkforceEntry
        from backend.src.services.snapshot_loader_v2 import SnapshotLoaderV2
        
        loader = SnapshotLoaderV2()
        loader.initialize()
        
        # Test increasingly large workforces until failure
        test_sizes = [1000, 2000, 5000, 10000]
        max_successful_size = 0
        
        for size in test_sizes:
            try:
                # Generate workforce entries
                workforce_entries = []
                for i in range(size):
                    entry = WorkforceEntry(
                        id=f"stress-test-{i}",
                        role="Consultant",
                        level="A",
                        hire_date="2024-01",
                        level_start_date="2024-01",
                        office="StressTest"
                    )
                    workforce_entries.append(entry)
                
                # Create snapshot
                large_snapshot = PopulationSnapshot(
                    id=f"stress-test-{size}",
                    office_id="StressTest",
                    snapshot_date="2025-01",
                    name=f"Stress Test {size} Persons",
                    workforce=workforce_entries
                )
                
                # Test initialization with timeout
                start_time = time.time()
                office_state = loader.initialize_office_state(large_snapshot)
                end_time = time.time()
                
                if end_time - start_time < 30.0:  # Must complete within 30 seconds
                    max_successful_size = size
                    print(f"Successfully processed {size} persons in {end_time - start_time:.2f}s")
                else:
                    print(f"Timeout at {size} persons")
                    break
                
            except MemoryError:
                print(f"Memory error at {size} persons")
                break
            except Exception as e:
                print(f"Error at {size} persons: {e}")
                break
        
        print(f"\nScalability Results:")
        print(f"Maximum workforce size: {max_successful_size} persons")
        
        # Should handle at least 2000 persons
        assert max_successful_size >= 2000

    @pytest.mark.slow
    def test_maximum_simulation_duration(self, population_snapshot, business_plan):
        """Test maximum simulation duration the system can handle"""
        engine = SimulationEngineV2Factory.create_dev_engine()
        engine.validation_enabled = False
        
        # Load data
        engine.snapshot_loader.loaded_snapshots[population_snapshot.id] = population_snapshot
        engine.business_processor.load_business_plan(business_plan)
        
        # Test increasingly long simulations
        test_durations = [1, 2, 5, 10]  # years
        max_successful_duration = 0
        
        for years in test_durations:
            try:
                scenario = ScenarioRequest(
                    name=f"Duration Test {years} Years",
                    description="Long duration scalability test",
                    time_range=TimeRange(
                        start_year=2025,
                        start_month=1,
                        end_year=2025 + years - 1,
                        end_month=12
                    ),
                    office_scope=["Stockholm"],
                    levers=Levers(),
                    use_snapshot=True,
                    snapshot_id=population_snapshot.id,
                    use_business_plan=True
                )
                
                start_time = time.time()
                results = engine.execute_scenario(scenario)
                end_time = time.time()
                
                execution_time = end_time - start_time
                
                if execution_time < 300.0:  # Must complete within 5 minutes
                    max_successful_duration = years
                    months_simulated = years * 12
                    print(f"Successfully simulated {years} years ({months_simulated} months) in {execution_time:.2f}s")
                else:
                    print(f"Timeout at {years} years")
                    break
                
            except MemoryError:
                print(f"Memory error at {years} years")
                break
            except Exception as e:
                print(f"Error at {years} years: {e}")
                break
        
        print(f"\nDuration Scalability Results:")
        print(f"Maximum simulation duration: {max_successful_duration} years")
        
        # Should handle at least 2 years
        assert max_successful_duration >= 2

    def test_memory_leak_detection(
        self, performance_engine, population_snapshot, business_plan
    ):
        """Test for memory leaks during repeated simulations"""
        import gc
        import psutil
        
        process = psutil.Process(os.getpid())
        
        # Load data
        performance_engine.snapshot_loader.loaded_snapshots[population_snapshot.id] = population_snapshot
        performance_engine.business_processor.load_business_plan(business_plan)
        
        # Baseline memory
        gc.collect()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        memory_readings = [baseline_memory]
        
        # Run multiple simulations
        for i in range(5):
            scenario = ScenarioRequest(
                name=f"Memory Leak Test {i}",
                description="Test for memory leaks",
                time_range=TimeRange(start_year=2025, start_month=1, end_year=2025, end_month=3),
                office_scope=["Stockholm"],
                levers=Levers(),
                use_snapshot=True,
                snapshot_id=population_snapshot.id,
                use_business_plan=True
            )
            
            # Execute simulation
            results = performance_engine.execute_scenario(scenario)
            
            # Force garbage collection and measure memory
            gc.collect()
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_readings.append(current_memory)
            
            print(f"Simulation {i+1}: {current_memory:.1f} MB")
        
        # Analyze memory trend
        memory_increase = memory_readings[-1] - memory_readings[0]
        max_increase_between_runs = max(
            memory_readings[i+1] - memory_readings[i] 
            for i in range(len(memory_readings)-1)
        )
        
        print(f"\nMemory Leak Analysis:")
        print(f"Baseline memory: {baseline_memory:.1f} MB")
        print(f"Final memory: {memory_readings[-1]:.1f} MB")
        print(f"Total increase: {memory_increase:.1f} MB")
        print(f"Max increase between runs: {max_increase_between_runs:.1f} MB")
        
        # Memory leak thresholds
        assert memory_increase < 50.0  # Total increase should be less than 50MB
        assert max_increase_between_runs < 20.0  # No single run should increase by more than 20MB