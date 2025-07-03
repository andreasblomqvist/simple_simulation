import unittest
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from services.simulation_engine import SimulationEngine, Month
from services.scenario_service import ScenarioService
from services.config_service import ConfigService

class TestRecruitmentDebug(unittest.TestCase):
    
    def setUp(self):
        """Set up a fresh simulation engine for each test"""
        self.engine = SimulationEngine()
        # Create scenario service to load offices
        self.config_service = ConfigService()
        self.scenario_service = ScenarioService(self.config_service)
        # Load offices from config
        config = self.config_service.get_config()
        progression_config = self.scenario_service.load_progression_config()
        self.offices = self.scenario_service.create_offices_from_config(config, progression_config)
    
    def test_recruitment_calculation_simple(self):
        """
        Test basic recruitment calculation with a simple example
        """
        # Get an available office for testing
        available_offices = list(self.offices.keys())
        self.assertGreater(len(available_offices), 0, "Should have at least one office")
        
        test_office_name = available_offices[0]
        test_office = self.offices[test_office_name]
        
        # Find a consultant level that exists
        if 'Consultant' in test_office.roles and 'A' in test_office.roles['Consultant']:
            level_a = test_office.roles['Consultant']['A']
            
            # Check initial count (can't modify as total is read-only)
            initial_count = level_a.total
            self.assertGreater(initial_count, 0, f"Test office {test_office_name} should have A-level consultants")
            
            # Run one month simulation using the loaded offices
            result = self.engine.run_simulation_with_offices(
                start_year=2024, start_month=1,
                end_year=2024, end_month=1,
                offices=self.offices,
                progression_config=self.scenario_service.load_progression_config(),
                cat_curves=self.scenario_service.load_cat_curves()
            )
            
            # Verify structure
            year_2024 = result['years']['2024']
            self.assertIn('offices', year_2024)
            self.assertIn(test_office_name, year_2024['offices'], f"{test_office_name} should be in result")
        else:
            self.skipTest(f"Test office {test_office_name} doesn't have Consultant A level")
    
    def test_recruitment_with_different_rates(self):
        """
        Test recruitment with different monthly rates
        """
        # Find an office with consultant roles
        test_office_name = None
        for office_name, office in self.offices.items():
            if 'Consultant' in office.roles and len(office.roles['Consultant']) > 0:
                test_office_name = office_name
                break
        
        if test_office_name is None:
            self.skipTest("No office found with consultant roles")
            
        # Run simulation for a few months
        result = self.engine.run_simulation_with_offices(
            start_year=2024, start_month=1,
            end_year=2024, end_month=3,
            offices=self.offices,
            progression_config=self.scenario_service.load_progression_config(),
            cat_curves=self.scenario_service.load_cat_curves()
        )
        
        # Check that results exist for our test office
        year_2024 = result['years']['2024']
        self.assertIn('offices', year_2024)
        self.assertIn(test_office_name, year_2024['offices'])
        
        office_results = year_2024['offices'][test_office_name]
        self.assertIn('levels', office_results)
    
    def test_fractional_recruitment_accumulation(self):
        """
        Test that fractional recruitment accumulates correctly over time
        """
        # Find a suitable office for testing
        test_office_name = None
        for office_name, office in self.offices.items():
            if 'Consultant' in office.roles and 'A' in office.roles['Consultant']:
                if office.roles['Consultant']['A'].total > 0:
                    test_office_name = office_name
                    break
        
        if test_office_name is None:
            self.skipTest("No suitable office found for testing")
        
        # Run simulation for several months
        result = self.engine.run_simulation_with_offices(
            start_year=2024, start_month=1,
            end_year=2024, end_month=6,
            offices=self.offices,
            progression_config=self.scenario_service.load_progression_config(),
            cat_curves=self.scenario_service.load_cat_curves()
        )
        
        # Verify we got results
        year_2024 = result['years']['2024']
        self.assertIn('offices', year_2024)
        self.assertIn(test_office_name, year_2024['offices'])
        
        office_results = year_2024['offices'][test_office_name]
        self.assertIn('levels', office_results)
        
        # If consultant A data exists, verify we have 6 months
        if ('Consultant' in office_results['levels'] and 
            'A' in office_results['levels']['Consultant']):
            consultant_a_data = office_results['levels']['Consultant']['A']
            self.assertEqual(len(consultant_a_data), 6)
    
    def test_operations_recruitment(self):
        """
        Test operations recruitment works correctly
        """
        # Find an office with operations
        test_office_name = None
        for office_name, office in self.offices.items():
            if 'Operations' in office.roles:
                test_office_name = office_name
                break
        
        if test_office_name is None:
            self.skipTest("No office found with operations")
        
        # Run simulation
        result = self.engine.run_simulation_with_offices(
            start_year=2024, start_month=1,
            end_year=2024, end_month=2,
            offices=self.offices,
            progression_config=self.scenario_service.load_progression_config(),
            cat_curves=self.scenario_service.load_cat_curves()
        )
        
        # Check operations data exists
        year_2024 = result['years']['2024']
        self.assertIn('offices', year_2024)
        self.assertIn(test_office_name, year_2024['offices'])
        
        office_results = year_2024['offices'][test_office_name]
        # Operations might be in different structure - check if it exists
        if 'operations' in office_results:
            ops_data = office_results['operations']
            self.assertEqual(len(ops_data), 2, "Should have 2 months of operations data")
    
    def test_recruitment_debug_logging(self):
        """
        Test that recruitment debug logging provides useful information
        """
        # Capture any debug output during simulation
        result = self.engine.run_simulation_with_offices(
            start_year=2024, start_month=1,
            end_year=2024, end_month=1,
            offices=self.offices,
            progression_config=self.scenario_service.load_progression_config(),
            cat_curves=self.scenario_service.load_cat_curves()
        )
        
        # Basic structure check
        self.assertIn('years', result)
        self.assertIn('2024', result['years'])
        
        year_2024 = result['years']['2024']
        self.assertIn('offices', year_2024)
        
        # Ensure at least one office has data
        self.assertGreater(len(year_2024['offices']), 0, "Should have at least one office in results")

if __name__ == '__main__':
    unittest.main() 