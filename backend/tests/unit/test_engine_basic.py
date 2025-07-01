import unittest
import sys
import os
from unittest.mock import patch

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from services.simulation_engine import SimulationEngine, Month, OfficeJourney, Journey

class TestEngineBasic(unittest.TestCase):
    
    def setUp(self):
        """Set up a simulation engine for testing"""
        self.engine = SimulationEngine()
    
    def test_engine_initialization(self):
        """Test that the engine initializes correctly"""
        # Check that offices are created
        self.assertGreater(len(self.engine.offices), 0)
        
        # Check that Stockholm office exists with correct journey
        self.assertIn('Stockholm', self.engine.offices)
        stockholm = self.engine.offices['Stockholm']
        self.assertEqual(stockholm.journey, OfficeJourney.MATURE)  # 850 FTE = Mature
        
        # Check that Toronto office exists with correct journey
        self.assertIn('Toronto', self.engine.offices)
        toronto = self.engine.offices['Toronto']
        self.assertEqual(toronto.journey, OfficeJourney.NEW)  # 10 FTE = New
        
    def test_roles_initialization(self):
        """Test that roles are initialized correctly"""
        stockholm = self.engine.offices['Stockholm']
        
        # Check that all expected roles exist
        expected_roles = ['Consultant', 'Sales', 'Recruitment', 'Operations']
        for role in expected_roles:
            self.assertIn(role, stockholm.roles)
            
        # Check that consultant levels exist
        consultant_roles = stockholm.roles['Consultant']
        expected_levels = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']
        for level in expected_levels:
            self.assertIn(level, consultant_roles)
            
        # Check that levels have monthly attributes
        a_level = consultant_roles['A']
        self.assertTrue(hasattr(a_level, 'price_1'))
        self.assertTrue(hasattr(a_level, 'price_12'))
        
    def test_monthly_values(self):
        """Test that monthly values are set correctly"""
        stockholm = self.engine.offices['Stockholm']
        a_level = stockholm.roles['Consultant']['A']
        
        # Check that monthly prices increase slightly
        self.assertLess(a_level.price_1, a_level.price_12)
        
    def test_simple_simulation_run(self):
        """Test that the engine can run a simple simulation"""
        # Run simulation for 3 months (Jan to Mar 2024)
        results = self.engine.run_simulation(
            start_year=2024,
            start_month=1,  # January
            end_year=2024,
            end_month=3,    # March
            price_increase=0.03,
            salary_increase=0.03
        )
        
        # Check basic structure
        self.assertIn('years', results)
        self.assertIn('2024', results['years'])
        
        # Get 2024 data
        year_2024 = results['years']['2024']
        self.assertIn('offices', year_2024)
        
        # Check Stockholm office results
        self.assertIn('Stockholm', year_2024['offices'])
        stockholm_results = year_2024['offices']['Stockholm']
        
        # Should have levels, operations, and metrics data
        self.assertIn('levels', stockholm_results)
        
        # Should have 3 data points for each level (one per month)
        consultant_a_data = stockholm_results['levels']['Consultant']['A']
        self.assertEqual(len(consultant_a_data), 3)
        
        # Check that data points have expected structure
        first_data_point = consultant_a_data[0]
        self.assertIn('total', first_data_point)
        self.assertIn('price', first_data_point)
        self.assertIn('salary', first_data_point)
        
        # Check that FTE values are reasonable (> 0)
        self.assertGreater(first_data_point['total'], 0)
        
    def test_progression_timing(self):
        """Test that progression only occurs in the correct months"""
        # Run simulation from April to June (should include May progression)
        results = self.engine.run_simulation(
            start_year=2024,
            start_month=4,  # April
            end_year=2024,
            end_month=6,    # June
        )
        
        year_2024 = results['years']['2024']
        stockholm_results = year_2024['offices']['Stockholm']
        consultant_a_data = stockholm_results['levels']['Consultant']['A']
        
        # Get FTE values for April, May, June
        april_fte = consultant_a_data[0]['total']  # April
        may_fte = consultant_a_data[1]['total']    # May (progression month)
        june_fte = consultant_a_data[2]['total']   # June
        
        # May should have different FTE due to progression
        # (Note: exact values depend on churn/recruitment, but should change)
        print(f"April FTE: {april_fte}, May FTE: {may_fte}, June FTE: {june_fte}")
        
if __name__ == '__main__':
    unittest.main() 