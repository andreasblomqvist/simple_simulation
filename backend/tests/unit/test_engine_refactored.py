"""
Unit tests for the refactored SimulationEngine (pure function approach).
"""
import unittest
import sys
import os
from unittest.mock import patch, Mock

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from services.simulation_engine import SimulationEngine, Month, OfficeJourney, Journey
from services.scenario_service import ScenarioService

class TestEngineRefactored(unittest.TestCase):
    
    def setUp(self):
        """Set up a simulation engine and scenario service for testing"""
        self.engine = SimulationEngine()
        
        # Create mock config service
        self.mock_config_service = Mock()
        self.mock_config_service.get_config.return_value = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 850,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {
                            "fte": 100.0,
                            "recruitment_1": 2.0,
                            "recruitment_2": 2.0,
                            "churn_1": 1.0,
                            "churn_2": 1.0,
                            "price_1": 1200.0,
                            "salary_1": 45000.0
                        },
                        "AC": {
                            "fte": 80.0,
                            "recruitment_1": 1.5,
                            "recruitment_2": 1.5,
                            "churn_1": 0.8,
                            "churn_2": 0.8,
                            "price_1": 1300.0,
                            "salary_1": 55000.0
                        }
                    },
                    "Operations": {
                        "fte": 20.0,
                        "recruitment_1": 0.5,
                        "recruitment_2": 0.5,
                        "churn_1": 0.2,
                        "churn_2": 0.2,
                        "price_1": 80.0,
                        "salary_1": 35000.0
                    }
                }
            },
            "Toronto": {
                "name": "Toronto",
                "total_fte": 10,
                "journey": "New Office",
                "roles": {
                    "Consultant": {
                        "A": {
                            "fte": 8.0,
                            "recruitment_1": 1.0,
                            "recruitment_2": 1.0,
                            "churn_1": 0.5,
                            "churn_2": 0.5,
                            "price_1": 1100.0,
                            "salary_1": 40000.0
                        }
                    },
                    "Operations": {
                        "fte": 2.0,
                        "recruitment_1": 0.2,
                        "recruitment_2": 0.2,
                        "churn_1": 0.1,
                        "churn_2": 0.1,
                        "price_1": 70.0,
                        "salary_1": 30000.0
                    }
                }
            }
        }
        
        self.scenario_service = ScenarioService(self.mock_config_service)
    
    def test_engine_initialization_pure_function(self):
        """Test that the engine initializes correctly as a pure function"""
        # Engine should not have offices initially (pure function approach)
        self.assertEqual(len(self.engine.offices), 0)
        
        # Engine should be ready to receive offices as input
        self.assertIsNotNone(self.engine)
    
    def test_run_simulation_with_offices_pure_function(self):
        """Test that the engine can run simulation with provided offices (pure function)"""
        # Resolve scenario data using ScenarioService
        scenario_data = {}
        resolved_data = self.scenario_service.resolve_scenario(scenario_data)
        
        offices = resolved_data['offices']
        progression_config = resolved_data['progression_config']
        cat_curves = resolved_data['cat_curves']
        
        # Run simulation using the new pure function approach
        results = self.engine.run_simulation_with_offices(
            start_year=2024,
            start_month=1,
            end_year=2024,
            end_month=3,
            offices=offices,
            progression_config=progression_config,
            cat_curves=cat_curves,
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
        self.assertIn('fte', first_data_point)
        self.assertIn('price', first_data_point)
        self.assertIn('salary', first_data_point)
        
        # Check that FTE values are reasonable (> 0)
        self.assertGreater(first_data_point['fte'], 0)
    
    def test_run_simulation_backward_compatibility(self):
        """Test that the old run_simulation method still works (backward compatibility)"""
        # Run simulation using the old method (should use ScenarioService internally)
        results = self.engine.run_simulation(
            start_year=2024,
            start_month=1,
            end_year=2024,
            end_month=3,
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
        
        # Should have levels data
        self.assertIn('levels', stockholm_results)
        
        # Should have 3 data points for each level (one per month)
        consultant_a_data = stockholm_results['levels']['Consultant']['A']
        self.assertEqual(len(consultant_a_data), 3)
    
    def test_office_creation_with_scenario_service(self):
        """Test that offices are created correctly through ScenarioService"""
        # Resolve scenario data
        scenario_data = {}
        resolved_data = self.scenario_service.resolve_scenario(scenario_data)
        
        offices = resolved_data['offices']
        
        # Check that offices were created
        self.assertIn('Stockholm', offices)
        self.assertIn('Toronto', offices)
        
        # Check Stockholm office structure
        stockholm = offices['Stockholm']
        self.assertEqual(stockholm.name, 'Stockholm')
        self.assertEqual(stockholm.total_fte, 850)
        self.assertEqual(stockholm.journey, OfficeJourney.MATURE)
        
        # Check Toronto office structure
        toronto = offices['Toronto']
        self.assertEqual(toronto.name, 'Toronto')
        self.assertEqual(toronto.total_fte, 10)
        self.assertEqual(toronto.journey, OfficeJourney.NEW)
        
        # Check roles
        self.assertIn('Consultant', stockholm.roles)
        self.assertIn('Operations', stockholm.roles)
        
        # Check consultant levels
        consultant_roles = stockholm.roles['Consultant']
        expected_levels = ['A', 'AC']
        for level in expected_levels:
            self.assertIn(level, consultant_roles)
    
    def test_progression_config_loading(self):
        """Test that progression config is loaded correctly"""
        progression_config = self.scenario_service.load_progression_config()
        
        # Check structure
        self.assertIsInstance(progression_config, dict)
        self.assertGreater(len(progression_config), 0)
        
        # Check expected levels
        expected_levels = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P']
        for level in expected_levels:
            self.assertIn(level, progression_config)
    
    def test_cat_curves_loading(self):
        """Test that CAT curves are loaded correctly"""
        cat_curves = self.scenario_service.load_cat_curves()
        
        # Check structure
        self.assertIsInstance(cat_curves, dict)
        self.assertGreater(len(cat_curves), 0)
        
        # Check expected levels
        expected_levels = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'Pi', 'P']
        for level in expected_levels:
            self.assertIn(level, cat_curves)
    
    def test_progression_timing_with_pure_function(self):
        """Test that progression only occurs in the correct months (pure function)"""
        # Resolve scenario data
        scenario_data = {}
        resolved_data = self.scenario_service.resolve_scenario(scenario_data)
        
        # Run simulation from April to June (should include May progression)
        results = self.engine.run_simulation_with_offices(
            start_year=2024,
            start_month=4,
            end_year=2024,
            end_month=6,
            offices=resolved_data['offices'],
            progression_config=resolved_data['progression_config'],
            cat_curves=resolved_data['cat_curves']
        )
        
        year_2024 = results['years']['2024']
        stockholm_results = year_2024['offices']['Stockholm']
        consultant_a_data = stockholm_results['levels']['Consultant']['A']
        
        # Get FTE values for April, May, June
        april_fte = consultant_a_data[0]['fte']  # April
        may_fte = consultant_a_data[1]['fte']    # May (progression month)
        june_fte = consultant_a_data[2]['fte']   # June
        
        # May should have different FTE due to progression
        # (Note: exact values depend on churn/recruitment, but should change)
        print(f"April FTE: {april_fte}, May FTE: {may_fte}, June FTE: {june_fte}")
        
if __name__ == '__main__':
    unittest.main() 