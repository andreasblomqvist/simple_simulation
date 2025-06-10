import pytest
from src.services.simulation_engine import SimpleSimulationEngine

def test_basic_simulation():
    engine = SimpleSimulationEngine()
    results = engine.run_simulation(
        initial_headcount=100,
        growth_rate=0.05,
        periods=12
    )
    
    assert len(results['headcount']) == 13  # Initial + 12 periods
    assert results['headcount'][0] == 100
    assert results['growth_rate'] == 0.05
    assert results['periods'] == 12

def test_progression_calculation():
    engine = SimpleSimulationEngine()
    progression_matrix = {
        1: {'base_probability': 0.1},
        2: {'base_probability': 0.05}
    }
    
    # Test level 1 with 6 months experience
    prob1 = engine.calculate_progression(1, 6, progression_matrix)
    assert 0 < prob1 < 0.1  # Should be less than base due to time factor
    
    # Test level 2 with 12 months experience
    prob2 = engine.calculate_progression(2, 12, progression_matrix)
    assert prob2 == 0.05  # Should be exactly base due to time factor cap
    
    # Test invalid level
    prob3 = engine.calculate_progression(3, 6, progression_matrix)
    assert prob3 == 0.0  # Should be 0 for invalid level 