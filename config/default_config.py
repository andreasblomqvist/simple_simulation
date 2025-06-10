"""Default configuration settings for the simulation engine."""

# Simulation defaults
DEFAULT_PERIODS = 12
DEFAULT_GROWTH_RATE = 0.05

# Career progression matrix
DEFAULT_PROGRESSION_MATRIX = {
    1: {'base_probability': 0.1, 'max_level': 2},  # Junior
    2: {'base_probability': 0.05, 'max_level': 3},  # Mid-level
    3: {'base_probability': 0.02, 'max_level': 4},  # Senior
    4: {'base_probability': 0.01, 'max_level': 5}   # Lead
}

# Office size thresholds
OFFICE_THRESHOLDS = {
    'new': 25,        # 0-25 FTE
    'emerging': 200,  # 25-200 FTE
    'established': 500,  # 200-500 FTE
    'mature': float('inf')  # 500+ FTE
}

# Simulation parameters
SIMULATION_PARAMS = {
    'churn_rate': 0.02,  # 2% monthly churn
    'promotion_rate': 0.05,  # 5% monthly promotion rate
    'hiring_lead_time': 2  # 2 months to fill positions
} 