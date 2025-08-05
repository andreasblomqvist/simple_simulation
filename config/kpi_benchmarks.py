"""
KPI Benchmarks Configuration for Simulation Engine

This file defines the benchmark values for various Key Performance Indicators
that are tested in the engine KPI test suite.
"""

# PERFORMANCE KPIs
PERFORMANCE_KPIs = {
    # Execution time limits
    'max_execution_time_10_years': 1.0,  # seconds
    'max_execution_time_large_scale': 5.0,  # seconds for 50 years
    
    # Memory usage limits
    'max_memory_increase_large_sim': 50,  # MB
    
    # Throughput requirements
    'min_throughput_simulations_per_second': 5,  # simulations/second
}

# ACCURACY KPIs
ACCURACY_KPIs = {
    # Growth calculation accuracy
    'max_growth_rate_deviation': 0.05,  # 5% deviation allowed
    
    # Progression probability accuracy
    'max_progression_probability_deviation': 0.01,  # 1% deviation allowed
    
    # Growth rate consistency
    'max_growth_rate_variance': 0.5,  # 50% variance from target allowed
}

# BUSINESS LOGIC KPIs
BUSINESS_LOGIC_KPIs = {
    # Workforce growth patterns
    'headcount_must_never_decrease': True,
    'growth_must_be_consistent': True,
    
    # Career progression bounds
    'progression_probability_min': 0.0,
    'progression_probability_max': 1.0,
    
    # Edge case handling
    'zero_growth_maintains_headcount': True,
    'negative_growth_decreases_headcount': True,
}

# DATA QUALITY KPIs
DATA_QUALITY_KPIs = {
    # Result completeness
    'required_result_fields': ['headcount', 'periods', 'growth_rate', 'start_date'],
    
    # Data integrity
    'results_must_be_deterministic': True,
    'headcount_values_must_be_positive_integers': True,
    
    # Array length consistency
    'headcount_array_length_formula': 'periods + 1',  # includes initial value
}

# SIMULATION PARAMETERS FOR TESTING
TEST_PARAMETERS = {
    # Standard test simulation
    'standard_simulation': {
        'initial_headcount': 100,
        'growth_rate': 0.05,
        'periods': 12
    },
    
    # Large scale simulation
    'large_scale_simulation': {
        'initial_headcount': 10000,
        'growth_rate': 0.01,
        'periods': 600  # 50 years
    },
    
    # Memory intensive simulation
    'memory_intensive_simulation': {
        'initial_headcount': 5000,
        'growth_rate': 0.05,
        'periods': 240  # 20 years
    },
    
    # Throughput test simulation
    'throughput_test_simulation': {
        'initial_headcount': 100,
        'growth_rate': 0.02,
        'periods': 24,
        'num_iterations': 10
    }
}

# PROGRESSION MATRIX FOR TESTING
TEST_PROGRESSION_MATRIX = {
    1: {'base_probability': 0.15},
    2: {'base_probability': 0.10},
    3: {'base_probability': 0.05}
}

# EXPECTED PROGRESSION PROBABILITIES
EXPECTED_PROGRESSION_PROBABILITIES = {
    # (level, months, expected_probability)
    (1, 0, 0.0),     # 0 months should give 0 probability
    (1, 6, 0.075),   # 6 months should give half base probability
    (1, 12, 0.15),   # 12 months should give full base probability
    (1, 24, 0.15),   # 24 months should be capped at base probability
}

# KPI ALERT THRESHOLDS
ALERT_THRESHOLDS = {
    # Performance degradation alerts
    'execution_time_warning': 0.8,  # 80% of max execution time
    'memory_usage_warning': 40,     # 80% of max memory increase
    'throughput_warning': 6,        # 120% of min throughput
    
    # Accuracy degradation alerts
    'growth_accuracy_warning': 0.03,  # 3% deviation warning
    'progression_accuracy_warning': 0.008,  # 0.8% deviation warning
}

# REPORTING CONFIGURATION
REPORTING_CONFIG = {
    'precision_decimals': 3,
    'include_performance_metrics': True,
    'include_accuracy_metrics': True,
    'include_business_logic_metrics': True,
    'include_data_quality_metrics': True,
    'generate_benchmark_report': True
}