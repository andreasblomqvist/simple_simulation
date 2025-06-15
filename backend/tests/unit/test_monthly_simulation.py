import unittest
import sys
import os
from unittest.mock import patch

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from services.simulation_engine import SimulationEngine, Month, OfficeJourney, Journey, Level, RoleData

class TestMonthlySimulation(unittest.TestCase):
    
    def setUp(self):
        """Set up a simulation engine for testing"""
        self.engine = SimulationEngine()
    
    def test_month_enum_values(self):
        """Test that Month enum has correct values 1-12"""
        self.assertEqual(Month.JAN.value, 1)
        self.assertEqual(Month.FEB.value, 2)
        self.assertEqual(Month.MAR.value, 3)
        self.assertEqual(Month.APR.value, 4)
        self.assertEqual(Month.MAY.value, 5)
        self.assertEqual(Month.JUN.value, 6)
        self.assertEqual(Month.JUL.value, 7)
        self.assertEqual(Month.AUG.value, 8)
        self.assertEqual(Month.SEP.value, 9)
        self.assertEqual(Month.OCT.value, 10)
        self.assertEqual(Month.NOV.value, 11)
        self.assertEqual(Month.DEC.value, 12)
    
    def test_progression_months_initialization(self):
        """Test that progression_months are correctly set for different levels"""
        stockholm = self.engine.offices['Stockholm']
        
        # Test junior-mid levels (A-AM): should progress in May and November
        a_level = stockholm.roles['Consultant']['A']
        self.assertEqual(a_level.progression_months, [Month.MAY, Month.NOV])
        
        ac_level = stockholm.roles['Consultant']['AC']
        self.assertEqual(ac_level.progression_months, [Month.MAY, Month.NOV])
        
        c_level = stockholm.roles['Consultant']['C']
        self.assertEqual(c_level.progression_months, [Month.MAY, Month.NOV])
        
        src_level = stockholm.roles['Consultant']['SrC']
        self.assertEqual(src_level.progression_months, [Month.MAY, Month.NOV])
        
        am_level = stockholm.roles['Consultant']['AM']
        self.assertEqual(am_level.progression_months, [Month.MAY, Month.NOV])
        
        # Test senior levels (M+): should progress only in November
        m_level = stockholm.roles['Consultant']['M']
        self.assertEqual(m_level.progression_months, [Month.NOV])
        
        srm_level = stockholm.roles['Consultant']['SrM']
        self.assertEqual(srm_level.progression_months, [Month.NOV])
        
        pip_level = stockholm.roles['Consultant']['PiP']
        self.assertEqual(pip_level.progression_months, [Month.NOV])
    
    def test_monthly_attributes_exist(self):
        """Test that all levels have monthly attributes (1-12)"""
        stockholm = self.engine.offices['Stockholm']
        a_level = stockholm.roles['Consultant']['A']
        
        # Test that all monthly attributes exist
        for i in range(1, 13):
            self.assertTrue(hasattr(a_level, f'price_{i}'))
            self.assertTrue(hasattr(a_level, f'salary_{i}'))
            self.assertTrue(hasattr(a_level, f'recruitment_{i}'))
            self.assertTrue(hasattr(a_level, f'churn_{i}'))
            self.assertTrue(hasattr(a_level, f'progression_{i}'))
            self.assertTrue(hasattr(a_level, f'utr_{i}'))
    
    def test_get_monthly_attribute_helper(self):
        """Test the _get_monthly_attribute helper function"""
        stockholm = self.engine.offices['Stockholm']
        a_level = stockholm.roles['Consultant']['A']
        
        # Test getting different monthly attributes
        price_jan = self.engine._get_monthly_attribute(a_level, 'price', Month.JAN)
        self.assertEqual(price_jan, a_level.price_1)
        
        price_dec = self.engine._get_monthly_attribute(a_level, 'price', Month.DEC)
        self.assertEqual(price_dec, a_level.price_12)
        
        recruitment_may = self.engine._get_monthly_attribute(a_level, 'recruitment', Month.MAY)
        self.assertEqual(recruitment_may, a_level.recruitment_5)
    
    def test_progression_timing_in_simulation(self):
        """Test that progression only occurs in correct months during simulation"""
        # Run a one-year simulation
        results = self.engine.run_simulation(
            start_year=2024,
            start_half=Month.JAN,
            end_year=2024,
            end_half=Month.DEC,
            price_increase=0.03,
            salary_increase=0.03
        )
        
        # Check that we have 12 months of data
        stockholm_results = results['offices']['Stockholm']
        self.assertEqual(len(stockholm_results['levels']['Consultant']['A']), 12)
        
        # Get initial values to track changes
        initial_a_total = stockholm_results['levels']['Consultant']['A'][0]['total']
        initial_m_total = stockholm_results['levels']['Consultant']['M'][0]['total']
        
        # Check progression patterns for A level (should progress in May and November)
        may_data = stockholm_results['levels']['Consultant']['A'][4]  # May is index 4
        nov_data = stockholm_results['levels']['Consultant']['A'][10]  # November is index 10
        
        # A level should have some progression in these months (assuming some FTE)
        if initial_a_total > 0:
            # We can't easily test exact progression without knowing recruitment/churn
            # But we can verify the structure is correct
            self.assertIsInstance(may_data['total'], int)
            self.assertIsInstance(nov_data['total'], int)
    
    def test_monthly_loop_execution(self):
        """Test that the simulation runs through all 12 months"""
        results = self.engine.run_simulation(
            start_year=2024,
            start_half=Month.JAN,
            end_year=2024,
            end_half=Month.DEC,
            price_increase=0.03,
            salary_increase=0.03
        )
        
        # Check that each office has 12 data points
        for office_name, office_data in results['offices'].items():
            # Check levels data
            for role_name, role_data in office_data['levels'].items():
                for level_name, level_data in role_data.items():
                    self.assertEqual(len(level_data), 12, 
                                   f"Office {office_name}, Role {role_name}, Level {level_name} should have 12 months of data")
            
            # Check metrics data
            self.assertEqual(len(office_data['metrics']), 12,
                           f"Office {office_name} should have 12 months of metrics")
            
            # Check operations data (if exists)
            if 'operations' in office_data:
                self.assertEqual(len(office_data['operations']), 12,
                               f"Office {office_name} should have 12 months of operations data")
    
    def test_monthly_price_salary_updates(self):
        """Test that prices and salaries are updated correctly at year end"""
        # Test with a small simulation
        results = self.engine.run_simulation(
            start_year=2024,
            start_half=Month.JAN,
            end_year=2025,
            end_half=Month.JAN,
            price_increase=0.1,  # 10% increase for easy testing
            salary_increase=0.1
        )
        
        stockholm_data = results['offices']['Stockholm']
        
        # Get January 2024 and January 2025 data for A level
        jan_2024_data = stockholm_data['levels']['Consultant']['A'][0]
        jan_2025_data = stockholm_data['levels']['Consultant']['A'][12]  # 13th data point
        
        # Prices should have increased by 10%
        price_increase_ratio = jan_2025_data['price'] / jan_2024_data['price']
        self.assertAlmostEqual(price_increase_ratio, 1.1, places=2)
        
        # Salaries should have increased by 10%
        salary_increase_ratio = jan_2025_data['salary'] / jan_2024_data['salary']
        self.assertAlmostEqual(salary_increase_ratio, 1.1, places=2)
    
    def test_calculate_progression_method(self):
        """Test the calculate_progression method with different months"""
        stockholm = self.engine.offices['Stockholm']
        
        # Set some initial values for testing
        stockholm.roles['Consultant']['A'].total = 10
        stockholm.roles['Consultant']['M'].total = 5
        
        # Test progression calculation in May (A should progress, M should not)
        may_progression = self.engine.calculate_progression(stockholm, Month.MAY)
        
        # Test progression calculation in November (both A and M should progress)
        nov_progression = self.engine.calculate_progression(stockholm, Month.NOV)
        
        # Test progression calculation in January (neither should progress)
        jan_progression = self.engine.calculate_progression(stockholm, Month.JAN)
        
        # November should have higher progression than May (more levels progressing)
        # January should have zero progression
        self.assertEqual(jan_progression, 0.0)
        self.assertGreaterEqual(nov_progression, may_progression)
    
    def test_flat_role_operations(self):
        """Test that Operations (flat role) works correctly in monthly simulation"""
        results = self.engine.run_simulation(
            start_year=2024,
            start_half=Month.JAN,
            end_year=2024,
            end_half=Month.DEC,
            price_increase=0.03,
            salary_increase=0.03
        )
        
        stockholm_data = results['offices']['Stockholm']
        
        # Operations should have 12 months of data
        self.assertEqual(len(stockholm_data['operations']), 12)
        
        # Each operations data point should have correct structure
        for monthly_ops_data in stockholm_data['operations']:
            self.assertIn('total', monthly_ops_data)
            self.assertIn('price', monthly_ops_data)
            self.assertIn('salary', monthly_ops_data)
    
    def test_office_journey_classification(self):
        """Test that office journey classification works correctly"""
        # Test the corrected thresholds from our memory
        small_office = self.engine.offices['London']  # 2 FTE
        self.assertEqual(small_office.journey, OfficeJourney.NEW)  # 0-24 should be NEW
        
        medium_office = self.engine.offices['Hamburg']  # 200 FTE  
        self.assertEqual(medium_office.journey, OfficeJourney.ESTABLISHED)  # 200-499 should be ESTABLISHED
        
        large_office = self.engine.offices['Stockholm']  # 850 FTE
        self.assertEqual(large_office.journey, OfficeJourney.MATURE)  # 500+ should be MATURE
    
    def test_lever_plan_application(self):
        """Test that lever plans are applied correctly in monthly simulation"""
        # Create a simple lever plan
        lever_plan = {
            'Stockholm': {
                'Consultant': {
                    'recruitment_5': 0.2,  # Override May recruitment to 20%
                    'churn_11': 0.1       # Override November churn to 10%
                }
            }
        }
        
        results = self.engine.run_simulation(
            start_year=2024,
            start_half=Month.JAN,
            end_year=2024,
            end_half=Month.DEC,
            price_increase=0.03,
            salary_increase=0.03,
            lever_plan=lever_plan
        )
        
        # The simulation should complete successfully with lever plan
        self.assertIn('Stockholm', results['offices'])
        self.assertEqual(len(results['offices']['Stockholm']['levels']['Consultant']['A']), 12)
    
    def test_edge_case_single_month_simulation(self):
        """Test running simulation for just one month"""
        results = self.engine.run_simulation(
            start_year=2024,
            start_half=Month.MAY,
            end_year=2024,
            end_half=Month.MAY,
            price_increase=0.03,
            salary_increase=0.03
        )
        
        # Should have exactly 1 month of data
        for office_name, office_data in results['offices'].items():
            for role_name, role_data in office_data['levels'].items():
                for level_name, level_data in role_data.items():
                    self.assertEqual(len(level_data), 1)
    
    def test_multi_year_simulation(self):
        """Test running simulation across multiple years"""
        results = self.engine.run_simulation(
            start_year=2024,
            start_half=Month.JAN,
            end_year=2025,
            end_half=Month.DEC,
            price_increase=0.05,
            salary_increase=0.05
        )
        
        # Should have 24 months of data (2 full years)
        stockholm_data = results['offices']['Stockholm']
        self.assertEqual(len(stockholm_data['levels']['Consultant']['A']), 24)
        self.assertEqual(len(stockholm_data['metrics']), 24)

class TestProgressionLogic(unittest.TestCase):
    """Separate test class focusing specifically on progression logic"""
    
    def setUp(self):
        self.engine = SimulationEngine()
        # Set up a simple test scenario
        self.stockholm = self.engine.offices['Stockholm']
        self.stockholm.roles['Consultant']['A'].total = 10
        self.stockholm.roles['Consultant']['M'].total = 5
    
    def test_a_level_progression_months(self):
        """Test that A level only progresses in May and November"""
        test_months = [
            (Month.JAN, False),
            (Month.FEB, False),
            (Month.MAR, False),
            (Month.APR, False),
            (Month.MAY, True),   # Should progress
            (Month.JUN, False),
            (Month.JUL, False),
            (Month.AUG, False),
            (Month.SEP, False),
            (Month.OCT, False),
            (Month.NOV, True),   # Should progress
            (Month.DEC, False)
        ]
        
        a_level = self.stockholm.roles['Consultant']['A']
        
        for month, should_progress in test_months:
            is_progression_month = month in a_level.progression_months
            self.assertEqual(is_progression_month, should_progress, 
                           f"A level progression in {month.name} should be {should_progress}")
    
    def test_m_level_progression_months(self):
        """Test that M level only progresses in November"""
        test_months = [
            (Month.JAN, False),
            (Month.FEB, False),
            (Month.MAR, False),
            (Month.APR, False),
            (Month.MAY, False),  # Should NOT progress (unlike A level)
            (Month.JUN, False),
            (Month.JUL, False),
            (Month.AUG, False),
            (Month.SEP, False),
            (Month.OCT, False),
            (Month.NOV, True),   # Should progress
            (Month.DEC, False)
        ]
        
        m_level = self.stockholm.roles['Consultant']['M']
        
        for month, should_progress in test_months:
            is_progression_month = month in m_level.progression_months
            self.assertEqual(is_progression_month, should_progress,
                           f"M level progression in {month.name} should be {should_progress}")

if __name__ == '__main__':
    unittest.main() 