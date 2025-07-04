import pytest
import time
import psutil
import os
import numpy as np
from src.services.simulation_engine import SimpleSimulationEngine

class TestEngineKPIs:
    """Test suite for verifying engine Key Performance Indicators."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.engine = SimpleSimulationEngine()
        self.process = psutil.Process(os.getpid())
        
    # PERFORMANCE KPIs
    
    def test_simulation_execution_time_kpi(self):
        """Test that simulation execution time meets performance KPI."""
        start_time = time.time()
        
        # Run a moderately complex simulation
        results = self.engine.run_simulation(
            initial_headcount=1000,
            growth_rate=0.03,
            periods=120  # 10 years
        )
        
        execution_time = time.time() - start_time
        
        # KPI: Simulation should complete within 1 second for 10 years
        assert execution_time < 1.0, f"Execution time {execution_time:.3f}s exceeds KPI of 1.0s"
        assert results is not None, "Simulation should return results"
        
    def test_memory_usage_kpi(self):
        """Test memory usage during simulation stays within acceptable limits."""
        initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        # Run memory-intensive simulation
        results = self.engine.run_simulation(
            initial_headcount=5000,
            growth_rate=0.05,
            periods=240  # 20 years
        )
        
        peak_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory
        
        # KPI: Memory increase should be less than 50MB for large simulations
        assert memory_increase < 50, f"Memory increase {memory_increase:.1f}MB exceeds KPI of 50MB"
        assert len(results['headcount']) == 241, "Should have correct number of data points"
        
    def test_throughput_kpi(self):
        """Test simulation throughput meets performance requirements."""
        num_simulations = 10
        start_time = time.time()
        
        # Run multiple simulations
        for i in range(num_simulations):
            self.engine.run_simulation(
                initial_headcount=100,
                growth_rate=0.02,
                periods=24
            )
        
        total_time = time.time() - start_time
        throughput = num_simulations / total_time
        
        # KPI: Should handle at least 5 simulations per second
        assert throughput >= 5, f"Throughput {throughput:.1f} sims/sec is below KPI of 5 sims/sec"
        
    # ACCURACY KPIs
    
    def test_growth_rate_accuracy_kpi(self):
        """Test that growth rate calculations are accurate."""
        initial_headcount = 100
        growth_rate = 0.10  # 10% growth
        periods = 12
        
        results = self.engine.run_simulation(
            initial_headcount=initial_headcount,
            growth_rate=growth_rate,
            periods=periods
        )
        
        # Calculate expected vs actual growth
        expected_final = initial_headcount * (1 + growth_rate) ** periods
        actual_final = results['headcount'][-1]
        
        # KPI: Growth calculation should be within 5% of mathematical expectation
        accuracy = abs(actual_final - expected_final) / expected_final
        assert accuracy < 0.05, f"Growth accuracy {accuracy:.3f} exceeds KPI of 5% deviation"
        
    def test_progression_probability_bounds_kpi(self):
        """Test that progression probabilities stay within valid bounds."""
        progression_matrix = {
            1: {'base_probability': 0.15},
            2: {'base_probability': 0.10},
            3: {'base_probability': 0.05}
        }
        
        # Test various scenarios
        test_cases = [
            (1, 0, 0.0),     # 0 months should give 0 probability
            (1, 6, 0.075),   # 6 months should give half base probability
            (1, 12, 0.15),   # 12 months should give full base probability
            (1, 24, 0.15),   # 24 months should be capped at base probability
        ]
        
        for level, months, expected in test_cases:
            prob = self.engine.calculate_progression(level, months, progression_matrix)
            
            # KPI: All probabilities must be between 0 and 1
            assert 0 <= prob <= 1, f"Probability {prob} for level {level} is out of bounds"
            
            # KPI: Probability should be within 0.01 of expected
            assert abs(prob - expected) < 0.01, f"Probability {prob} deviates from expected {expected}"
    
    # BUSINESS LOGIC KPIs
    
    def test_workforce_growth_consistency_kpi(self):
        """Test that workforce growth follows consistent patterns."""
        results = self.engine.run_simulation(
            initial_headcount=50,
            growth_rate=0.08,
            periods=24
        )
        
        headcounts = results['headcount']
        
        # KPI: Headcount should never decrease
        for i in range(1, len(headcounts)):
            assert headcounts[i] >= headcounts[i-1], f"Headcount decreased from {headcounts[i-1]} to {headcounts[i]}"
        
        # KPI: Growth should be approximately exponential
        growth_rates = []
        for i in range(1, len(headcounts)):
            if headcounts[i-1] > 0:
                rate = (headcounts[i] - headcounts[i-1]) / headcounts[i-1]
                growth_rates.append(rate)
        
        # Growth rates should be relatively consistent (within 50% of target)
        target_rate = 0.08
        for rate in growth_rates:
            assert abs(rate - target_rate) / target_rate < 0.5, f"Growth rate {rate:.3f} deviates too much from target {target_rate}"
    
    def test_progression_matrix_handling_kpi(self):
        """Test robust handling of progression matrix edge cases."""
        # Test with empty matrix
        prob1 = self.engine.calculate_progression(1, 12, {})
        assert prob1 == 0.0, "Empty matrix should return 0 probability"
        
        # Test with None matrix
        prob2 = self.engine.calculate_progression(1, 12, None)
        assert prob2 == 0.0, "None matrix should return 0 probability"
        
        # Test with missing level
        matrix = {1: {'base_probability': 0.1}}
        prob3 = self.engine.calculate_progression(2, 12, matrix)
        assert prob3 == 0.0, "Missing level should return 0 probability"
        
        # Test with malformed matrix
        bad_matrix = {1: {}}  # Missing base_probability
        prob4 = self.engine.calculate_progression(1, 12, bad_matrix)
        assert prob4 == 0.0, "Malformed matrix should return 0 probability"
    
    # DATA QUALITY KPIs
    
    def test_result_completeness_kpi(self):
        """Test that simulation results contain all expected data."""
        results = self.engine.run_simulation(
            initial_headcount=75,
            growth_rate=0.06,
            periods=18
        )
        
        # KPI: Results must contain all required fields
        required_fields = ['headcount', 'periods', 'growth_rate', 'start_date']
        for field in required_fields:
            assert field in results, f"Missing required field: {field}"
        
        # KPI: Headcount array should have correct length
        expected_length = 18 + 1  # periods + initial
        assert len(results['headcount']) == expected_length, f"Headcount length {len(results['headcount'])} != expected {expected_length}"
        
        # KPI: All headcount values should be positive integers
        for i, count in enumerate(results['headcount']):
            assert isinstance(count, int), f"Headcount at period {i} is not an integer: {count}"
            assert count > 0, f"Headcount at period {i} is not positive: {count}"
    
    def test_data_integrity_kpi(self):
        """Test data integrity across multiple simulation runs."""
        # Run same simulation multiple times
        params = {
            'initial_headcount': 100,
            'growth_rate': 0.04,
            'periods': 12
        }
        
        results1 = self.engine.run_simulation(**params)
        results2 = self.engine.run_simulation(**params)
        
        # KPI: Identical inputs should produce identical outputs
        assert results1['headcount'] == results2['headcount'], "Identical simulations should produce identical results"
        assert results1['growth_rate'] == results2['growth_rate'], "Growth rate should be preserved"
        assert results1['periods'] == results2['periods'], "Periods should be preserved"
    
    def test_edge_case_handling_kpi(self):
        """Test engine behavior with edge cases."""
        # Test zero growth
        results_zero = self.engine.run_simulation(
            initial_headcount=50,
            growth_rate=0.0,
            periods=12
        )
        
        # KPI: Zero growth should maintain constant headcount
        for count in results_zero['headcount']:
            assert count == 50, f"Zero growth should maintain headcount at 50, got {count}"
        
        # Test negative growth (should still work mathematically)
        results_negative = self.engine.run_simulation(
            initial_headcount=100,
            growth_rate=-0.02,
            periods=5
        )
        
        # KPI: Negative growth should decrease headcount
        assert results_negative['headcount'][-1] < 100, "Negative growth should decrease headcount"
        
        # Test single period
        results_single = self.engine.run_simulation(
            initial_headcount=25,
            growth_rate=0.10,
            periods=1
        )
        
        # KPI: Single period should work correctly
        assert len(results_single['headcount']) == 2, "Single period should have 2 data points"
        assert results_single['headcount'][0] == 25, "Initial headcount should be preserved"
        
    def test_large_scale_simulation_kpi(self):
        """Test engine performance with large-scale simulations."""
        start_time = time.time()
        
        # Large scale simulation
        results = self.engine.run_simulation(
            initial_headcount=10000,
            growth_rate=0.01,
            periods=600  # 50 years
        )
        
        execution_time = time.time() - start_time
        
        # KPI: Large scale simulations should complete within 5 seconds
        assert execution_time < 5.0, f"Large scale simulation took {execution_time:.3f}s, exceeds KPI of 5.0s"
        
        # KPI: Results should be mathematically reasonable
        final_headcount = results['headcount'][-1]
        assert final_headcount > 10000, "Final headcount should be greater than initial"
        # Expected: 10000 * (1.01)^600 ≈ 3,978,800 (1% monthly compounded over 600 months)
        expected_growth = 10000 * (1.01 ** 600)
        # Allow 10% tolerance for integer rounding in the simulation
        assert abs(final_headcount - expected_growth) / expected_growth < 0.1, f"Final headcount {final_headcount} deviates too much from expected {expected_growth:.0f}"