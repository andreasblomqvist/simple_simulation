import unittest
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from services.simulation_engine import SimulationEngine, Month

class TestRecruitmentDebug(unittest.TestCase):
    
    def test_recruitment_calculation_simple(self):
        """Test a simple recruitment calculation to debug the logic"""
        engine = SimulationEngine()
        
        # Get Stockholm office for testing
        office = engine.offices['Stockholm']
        level_a = office.roles['Consultant']['A']
        
        # Set a known state for testing
        level_a.total = 10
        print(f"[TEST] Starting with {level_a.total} FTE")
        
        # Test recruitment calculation manually  
        recruitment_rate = level_a.recruitment_1  # January recruitment rate (should be 0.1)
        print(f"[TEST] Recruitment rate for January: {recruitment_rate}")
        
        if level_a.total == 0:
            new_recruits = int(recruitment_rate * 10)
            print(f"[TEST] Zero FTE case: {new_recruits} recruits")
        else:
            new_recruits = int(level_a.total * recruitment_rate)
            print(f"[TEST] Normal case: {level_a.total} * {recruitment_rate} = {new_recruits} recruits")
        
        expected_final = level_a.total + new_recruits
        print(f"[TEST] Expected final FTE: {expected_final}")
        
        # Run a single month simulation to see what happens
        results = engine.run_simulation(2024, 1, 2024, 1)
        
        # Check the actual result
        final_fte = office.roles['Consultant']['A'].total
        print(f"[TEST] Actual final FTE: {final_fte}")
        
        # Compare with expectation
        print(f"[TEST] Expected vs Actual: {expected_final} vs {final_fte}")

if __name__ == '__main__':
    unittest.main() 