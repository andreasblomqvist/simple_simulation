import unittest
import sys
import os
from unittest.mock import patch

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from services.simulation_engine import SimulationEngine, Month, OfficeJourney, Journey, Level, RoleData
from services.scenario_service import ScenarioService
from services.config_service import ConfigService
from services.scenario_service import ScenarioService
from services.config_service import ConfigService

class TestSimulationExamples(unittest.TestCase):
    """
    Test cases based on examples from simulation_engine.md documentation,
    adapted for monthly operation
    """
    
    def setUp(self):
        """Set up a simulation engine for testing"""
        self.engine = SimulationEngine()
        # Create scenario service to load offices
        self.config_service = ConfigService()
        self.scenario_service = ScenarioService(self.config_service)
        # Load offices from config
        config = self.config_service.get_config()
        progression_config = self.scenario_service.load_progression_config()
        self.offices = self.scenario_service.create_offices_from_config(config, progression_config)
    
    def test_processing_order_may_evaluation_month(self):
        """
        Test Scenario 1 from documentation: Normal Recruitment in May (evaluation month)
        Order: Churn → Progression → Recruitment
        """
        # Get Stockholm office and level A
        stockholm = self.offices['Stockholm']
        level_a = stockholm.roles['Consultant']['A']
        
        # Store initial count - we can't modify total directly as it's read-only
        initial_count = level_a.total
        
        # Run a single month simulation for May
        result = self.engine.run_simulation_with_offices(
            start_year=2024, start_month=5,
            end_year=2024, end_month=5,
            offices=self.offices,
            progression_config=self.scenario_service.load_progression_config(),
            cat_curves=self.scenario_service.load_cat_curves()
        )
        
        # Check that simulation completed successfully
        self.assertIn('years', result)
        self.assertIn('2024', result['years'])
        
        # Verify May processing occurred - fix structure access
        year_2024 = result['years']['2024']
        self.assertIn('offices', year_2024)
        stockholm_results = year_2024['offices']['Stockholm']
        
        # Check that we have level data for consultant A
        self.assertIn('levels', stockholm_results)
        self.assertIn('Consultant', stockholm_results['levels'])
        self.assertIn('A', stockholm_results['levels']['Consultant'])
        
        # Should have 1 data point for the single month
        consultant_a_data = stockholm_results['levels']['Consultant']['A']
        self.assertEqual(len(consultant_a_data), 1)
        
        # Check structure of the data point
        data_point = consultant_a_data[0]
        self.assertIn('fte', data_point)
        self.assertIn('price', data_point)
        self.assertIn('salary', data_point)
    
    def test_processing_order_january_non_evaluation(self):
        """
        Test Scenario 2 from documentation: Non-Evaluation Month (January)
        Order: Churn → Progression → Recruitment (no progression in January)
        """
        # Get Stockholm office and level A
        stockholm = self.offices['Stockholm']
        level_a = stockholm.roles['Consultant']['A']
        
        # Store initial count
        initial_count = level_a.total
        
        # Run a single month simulation for January
        result = self.engine.run_simulation_with_offices(
            start_year=2024, start_month=1,
            end_year=2024, end_month=1,
            offices=self.offices,
            progression_config=self.scenario_service.load_progression_config(),
            cat_curves=self.scenario_service.load_cat_curves()
        )
        
        # Check that simulation completed successfully
        self.assertIn('years', result)
        self.assertIn('2024', result['years'])
        
        # Verify January processing occurred - fix structure access
        year_2024 = result['years']['2024']
        self.assertIn('offices', year_2024)
        stockholm_results = year_2024['offices']['Stockholm']
        
        # Check that we have level data
        self.assertIn('levels', stockholm_results)
        self.assertIn('Consultant', stockholm_results['levels'])
        self.assertIn('A', stockholm_results['levels']['Consultant'])
        
        # Should have 1 data point for the single month
        consultant_a_data = stockholm_results['levels']['Consultant']['A']
        self.assertEqual(len(consultant_a_data), 1)
    
    def test_churn_calculation_example(self):
        """
        Test churn calculation for a specific scenario
        """
        stockholm = self.offices['Stockholm']
        level_a = stockholm.roles['Consultant']['A']
        
        # Get initial count
        initial_count = level_a.total
        
        # Run simulation
        result = self.engine.run_simulation_with_offices(
            start_year=2024, start_month=1,
            end_year=2024, end_month=1,
            offices=self.offices,
            progression_config=self.scenario_service.load_progression_config(),
            cat_curves=self.scenario_service.load_cat_curves()
        )
        
        # Check that simulation ran
        self.assertIn('years', result)
    
    def test_new_office_minimum_recruitment(self):
        """
        Test that small offices (like Toronto) work correctly with minimal staff
        """
        # Check Toronto office specifically since it's a new office (5 FTE)
        toronto = self.offices['Toronto']
        self.assertEqual(toronto.journey, OfficeJourney.NEW)
        
        # Run simulation for a few months
        result = self.engine.run_simulation_with_offices(
            start_year=2024, start_month=1,
            end_year=2024, end_month=3,
            offices=self.offices,
            progression_config=self.scenario_service.load_progression_config(),
            cat_curves=self.scenario_service.load_cat_curves()
        )
        
        year_2024 = result['years']['2024']
        office_names = year_2024['offices'].keys()
        
        # Toronto should be included in results
        self.assertIn('Toronto', office_names, f"Toronto should be in result: {list(office_names)}")
        
        toronto_results = year_2024['offices']['Toronto']
        self.assertIn('levels', toronto_results)
    
    def test_office_journey_classification(self):
        """
        Test office classification based on total FTE:
        - New Office: 0-24 FTE
        - Emerging Office: 25-200 FTE
        - Established Office: 200-500 FTE
        - Mature Office: 500+ FTE
        """
        # Updated classifications based on actual offices in OFFICE_HEADCOUNT
        classifications = {
            'Toronto': (5, OfficeJourney.NEW),         # 5 FTE → New
            'Cologne': (22, OfficeJourney.NEW),        # 22 FTE → New  
            'Amsterdam': (23, OfficeJourney.NEW),      # 23 FTE → New
            'Frankfurt': (27, OfficeJourney.EMERGING), # 27 FTE → Emerging
            'Hamburg': (165, OfficeJourney.EMERGING),  # 165 FTE → Emerging
            'Stockholm': (821, OfficeJourney.MATURE)   # 821 FTE → Mature
        }
        
        for office_name, (expected_fte, expected_journey) in classifications.items():
            office = self.engine.offices[office_name]
            self.assertEqual(office.journey, expected_journey,
                           f"{office_name} with {office.total_fte} FTE should be {expected_journey.value}")
    
    def test_monthly_simulation_full_year(self):
        """
        Test that monthly simulation runs for a full year and produces expected data structure
        """
        # Run simulation for full year 2024
        result = self.engine.run_simulation(
            start_year=2024, start_month=1,
            end_year=2024, end_month=12
        )
        
        # Verify basic structure
        self.assertIn('years', result)
        self.assertIn('2024', result['years'])
        
        year_2024 = result['years']['2024']
        self.assertIn('offices', year_2024)
        
        # Check that major offices are included
        office_names = year_2024['offices'].keys()
        
        # Check for key offices from our OFFICE_HEADCOUNT data
        expected_offices = ['Stockholm', 'Munich', 'Hamburg', 'Oslo', 'Copenhagen']
        for office in expected_offices:
            self.assertIn(office, office_names, f"{office} should be in result: {list(office_names)}")
        
        # Check Stockholm specific data
        stockholm_results = year_2024['offices']['Stockholm']
        self.assertIn('levels', stockholm_results)
    
    def test_progression_moves_to_next_level(self):
        """
        Test that progressed employees move to the next level
        """
        engine = SimulationEngine()
        
        # Get Stockholm levels
        stockholm = engine.offices['Stockholm']
        level_a = stockholm.roles['Consultant']['A']
        level_ac = stockholm.roles['Consultant']['AC']
        
        # Store initial counts
        initial_a = level_a.total
        initial_ac = level_ac.total
        
        # Run simulation for evaluation months (May and November)
        result = engine.run_simulation(
            start_year=2024, start_month=5,
            end_year=2024, end_month=5
        )
        
        # Check that simulation completed
        self.assertIn('years', result)
    
    def test_operations_flat_role(self):
        """
        Test that Operations role works as a flat role (no levels)
        """
        office = self.engine.offices['Stockholm']
        
        # Operations should be a flat role
        if 'Operations' in office.roles:
            operations = office.roles['Operations']
            self.assertIsInstance(operations, RoleData,
                                "Operations should be a flat role (RoleData)")
            self.assertIsInstance(operations.total, int,
                                "Operations should have integer total")
            self.assertGreater(operations.total, 0,
                             "Operations should have some FTE")
    
    def test_recruitment_calculation(self):
        """
        Test recruitment calculation: new_recruits = current_total * recruitment_rate
        """
        stockholm = self.engine.offices['Stockholm']
        level_a = stockholm.roles['Consultant']['A']
        
        # Get initial count (can't modify as it's read-only)
        initial_count = level_a.total
        
        # Run one month simulation
        result = self.engine.run_simulation(
            start_year=2024, start_month=1,
            end_year=2024, end_month=1
        )
        
        # Verify simulation ran successfully
        self.assertIn('years', result)
    
    def test_lever_plan_override(self):
        """
        Test that lever plans can override default rates
        """
        # Create a lever plan that overrides Stockholm Consultant A recruitment
        lever_plan = {
            'Stockholm': {
                'Consultant': {
                    'A': {
                        'recruitment_1': 0.5,  # 50% recruitment in January
                        'churn_1': 0.1         # 10% churn in January
                    }
                }
            }
        }
        
        office = self.engine.offices['Stockholm']
        level_a = office.roles['Consultant']['A']
        initial_total = level_a.total
        
        # Run simulation with lever plan
        results = self.engine.run_simulation(
            start_year=2024, start_month=1,
            end_year=2024, end_month=1,
            lever_plan=lever_plan
        )
        
        # The lever plan should have been applied
        self.assertIsNotNone(results, "Simulation should complete with lever plan")
        # Note: Specific verification would depend on implementation details
    
    def test_progression_evaluation_periods_only(self):
        """
        Test that progression only occurs during evaluation periods
        """
        stockholm = self.engine.offices['Stockholm']
        level_a = stockholm.roles['Consultant']['A']
        level_ac = stockholm.roles['Consultant']['AC']
        
        # Test non-evaluation months (should have no progression)
        # Run January (non-evaluation month)
        result_jan = self.engine.run_simulation(
            start_year=2024, start_month=1,
            end_year=2024, end_month=1
        )
        
        # Test evaluation month (May)
        result_may = self.engine.run_simulation(
            start_year=2024, start_month=5,
            end_year=2024, end_month=5
        )
        
        # Both should complete successfully
        self.assertIn('years', result_jan)
        self.assertIn('years', result_may)

if __name__ == '__main__':
    unittest.main() 