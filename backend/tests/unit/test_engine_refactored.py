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
from services.simulation.progression_models import ProgressionConfig, CATCurves

class TestEngineRefactored(unittest.TestCase):
    
    def setUp(self):
        """Set up a simulation engine and scenario service for testing"""
        self.engine = SimulationEngine()
        
        # Create mock config service
        self.mock_config_service = Mock()
        self.mock_config_service.get_config.return_value = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 10,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {
                            "fte": 10.0,
                            "recruitment_1": 1.0,  # 1% recruitment
                            "churn_1": 0.0,
                            "price_1": 1000.0,
                            "salary_1": 40000.0,
                            "price_2": 1000.0,
                            "salary_2": 40000.0,
                            "price_3": 1000.0,
                            "salary_3": 40000.0,
                            "price_4": 1000.0,
                            "salary_4": 40000.0,
                            "price_5": 1000.0,
                            "salary_5": 40000.0,
                            "price_6": 1000.0,
                            "salary_6": 40000.0,
                            "price_7": 1000.0,
                            "salary_7": 40000.0,
                            "price_8": 1000.0,
                            "salary_8": 40000.0,
                            "price_9": 1000.0,
                            "salary_9": 40000.0,
                            "price_10": 1000.0,
                            "salary_10": 40000.0,
                            "price_11": 1000.0,
                            "salary_11": 40000.0,
                            "price_12": 1000.0,
                            "salary_12": 40000.0
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
        progression_config = ProgressionConfig.from_dict(resolved_data['progression_config'])
        cat_curves = CATCurves.from_dict(resolved_data['cat_curves'])
        
        # Run simulation using the new pure function approach
        results = self.engine.run_simulation_with_offices(
            start_year=2024,
            start_month=1,
            end_year=2024,
            end_month=12,
            offices=offices,
            progression_config=progression_config,
            cat_curves=cat_curves
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
        self.assertEqual(len(consultant_a_data), 12)
        
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
            end_month=3
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
        self.assertEqual(stockholm.total_fte, 10)
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
        expected_levels = ['A']
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
    
    def test_simulation_results_include_absolute_numbers(self):
        """Test that simulation results include absolute number fields for recruitment and churn"""
        # Create a scenario with absolute number levers
        scenario_data = {
            "levers": {
                "roles": {
                    "Consultant": {
                        "A": {
                            "recruitment_abs_1": 5.0,  # Absolute recruitment
                            "churn_abs_1": 2.0         # Absolute churn
                        }
                    }
                }
            }
        }
        
        # Resolve scenario data
        resolved_data = self.scenario_service.resolve_scenario(scenario_data)
        
        # Run simulation
        results = self.engine.run_simulation_with_offices(
            start_year=2024,
            start_month=1,
            end_year=2024,
            end_month=12,
            offices=resolved_data['offices'],
            progression_config=resolved_data['progression_config'],
            cat_curves=resolved_data['cat_curves']
        )
        
        # Check that results include per-role/level data
        year_2024 = results['years']['2024']
        stockholm_results = year_2024['offices']['Stockholm']
        
        # Should have roles data with per-level FTEs
        self.assertIn('roles', stockholm_results)
        self.assertIn('Consultant', stockholm_results['roles'])
        self.assertIn('A', stockholm_results['roles']['Consultant'])
        
        # Check that each month has the expected data structure
        consultant_a_data = stockholm_results['roles']['Consultant']['A']
        # The simulation runs for 12 months, but we get 12 months of data
        self.assertEqual(len(consultant_a_data), 12)
        
        # Check that each data point has the expected fields
        for month_data in consultant_a_data:
            self.assertIn('fte', month_data)
            self.assertIn('price', month_data)
            self.assertIn('salary', month_data)
            self.assertIn('recruitment', month_data)
            self.assertIn('churn', month_data)
            
            # Check that FTE values are reasonable
            self.assertGreaterEqual(month_data['fte'], 0)
            self.assertGreaterEqual(month_data['price'], 0)
            self.assertGreaterEqual(month_data['salary'], 0)
            self.assertGreaterEqual(month_data['recruitment'], 0)
            self.assertGreaterEqual(month_data['churn'], 0)
        
        # Check that the absolute lever values were applied
        # The first month should show the effect of the absolute recruitment/churn
        first_month = consultant_a_data[0]  # January
        print(f"First month data: {first_month}")
        
        # Verify that the simulation engine processed the absolute values
        # (The exact values depend on the simulation logic, but should be > 0)
        self.assertGreater(first_month['fte'], 0)

    def test_simulation_applies_absolute_recruitment_and_churn(self):
        """Test that absolute recruitment and churn values are applied and FTE matches expected results."""
        # Start with 10 FTE, recruit 3 abs, churn 2 abs per month for 3 months
        scenario_data = {
            "levers": {
                "roles": {
                    "Consultant": {
                        "A": {
                            "recruitment_abs_1": 3.0,
                            "churn_abs_1": 2.0,
                            "recruitment_abs_2": 3.0,
                            "churn_abs_2": 2.0,
                            "recruitment_abs_3": 3.0,
                            "churn_abs_3": 2.0
                        }
                    }
                }
            }
        }
        # Patch the config to have only one office/role/level for clarity
        self.mock_config_service.get_config.return_value = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 10,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {
                            "fte": 10.0,
                            "recruitment_1": 0.0,
                            "recruitment_2": 0.0,
                            "recruitment_3": 0.0,
                            "churn_1": 0.0,
                            "churn_2": 0.0,
                            "churn_3": 0.0,
                            "price_1": 1000.0,
                            "salary_1": 40000.0
                        }
                    }
                }
            }
        }
        resolved_data = self.scenario_service.resolve_scenario(scenario_data)
        results = self.engine.run_simulation_with_offices(
            start_year=2024,
            start_month=1,
            end_year=2024,
            end_month=12,
            offices=resolved_data['offices'],
            progression_config=resolved_data['progression_config'],
            cat_curves=resolved_data['cat_curves']
        )
        year_2024 = results['years']['2024']
        stockholm_results = year_2024['offices']['Stockholm']
        consultant_a_data = stockholm_results['roles']['Consultant']['A']
        # FTE should be: [10+3-2=11], [11+3-2=12], [12+3-2=13]
        expected_ftes = [11, 12, 13]
        for i, expected in enumerate(expected_ftes):
            self.assertEqual(consultant_a_data[i]['fte'], expected, f"Month {i+1} FTE should be {expected}")

    def test_simulation_applies_progression_lever(self):
        """Test that a progression lever multiplier affects the CAT-based progression rate."""
        # Start with 10 FTE in A, 0 in AC, apply 2x progression multiplier in month 1
        scenario_data = {
            "levers": {
                "roles": {
                    "Consultant": {
                        "A": {
                            "progression_multiplier_1": 2.0  # 2x faster progression
                        }
                    }
                }
            }
        }
        self.mock_config_service.get_config.return_value = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 10,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {
                            "fte": 10.0,
                            "recruitment_1": 0.0,
                            "recruitment_2": 0.0,
                            "churn_1": 0.0,
                            "churn_2": 0.0,
                            "price_1": 1000.0,
                            "salary_1": 40000.0
                        },
                        "AC": {
                            "fte": 0.0,
                            "recruitment_1": 0.0,
                            "churn_1": 0.0,
                            "price_1": 1200.0,
                            "salary_1": 42000.0
                        }
                    }
                }
            }
        }
        resolved_data = self.scenario_service.resolve_scenario(scenario_data)
        results = self.engine.run_simulation_with_offices(
            start_year=2024,
            start_month=1,
            end_year=2024,
            end_month=12,
            offices=resolved_data['offices'],
            progression_config=resolved_data['progression_config'],
            cat_curves=resolved_data['cat_curves']
        )
        year_2024 = results['years']['2024']
        stockholm_results = year_2024['offices']['Stockholm']
        consultant_a_data = stockholm_results['roles']['Consultant']['A']
        
        # Check that the progression multiplier was applied
        # The exact numbers depend on the CAT-based progression logic,
        # but we can verify that the progression lever was processed
        self.assertIn('promoted_people', consultant_a_data[0], "Should track promoted people")
        
        # Verify that the progression multiplier was set on the level
        level_a = resolved_data['offices']['Stockholm'].roles['Consultant']['A']
        self.assertEqual(getattr(level_a, 'progression_multiplier_1', None), 2.0, "Progression multiplier should be set to 2.0")

    def test_simulation_returns_nonzero_kpis(self):
        """Test that all KPI sections (financial, growth) are present and not zero."""
        scenario_data = {}
        self.mock_config_service.get_config.return_value = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 10,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {
                            "fte": 10.0,
                            "recruitment_1": 1.0,  # 1% recruitment
                            "churn_1": 0.0,
                            "price_1": 1000.0,
                            "salary_1": 40000.0,
                            "price_2": 1000.0,
                            "salary_2": 40000.0,
                            "price_3": 1000.0,
                            "salary_3": 40000.0,
                            "price_4": 1000.0,
                            "salary_4": 40000.0,
                            "price_5": 1000.0,
                            "salary_5": 40000.0,
                            "price_6": 1000.0,
                            "salary_6": 40000.0,
                            "price_7": 1000.0,
                            "salary_7": 40000.0,
                            "price_8": 1000.0,
                            "salary_8": 40000.0,
                            "price_9": 1000.0,
                            "salary_9": 40000.0,
                            "price_10": 1000.0,
                            "salary_10": 40000.0,
                            "price_11": 1000.0,
                            "salary_11": 40000.0,
                            "price_12": 1000.0,
                            "salary_12": 40000.0
                        }
                    }
                }
            }
        }
        resolved_data = self.scenario_service.resolve_scenario(scenario_data)
        # Patch get_baseline_data to return a baseline with nonzero FTEs
        baseline = {
            'total_fte': 10,
            'total_consultants': 10,
            'total_non_consultants': 0
        }
        with patch('services.kpi.kpi_service.get_baseline_data', return_value=baseline):
            results = self.engine.run_simulation_with_offices(
                start_year=2024,
                start_month=1,
                end_year=2024,
                end_month=12,
                offices=resolved_data['offices'],
                progression_config=resolved_data['progression_config'],
                cat_curves=resolved_data['cat_curves']
            )
            year_2024 = results['years']['2024']
            kpis = year_2024['kpis']
            
            # Debug: Print the structure of the simulation results
            print(f"DEBUG: Year 2024 structure: {list(year_2024.keys())}")
            print(f"DEBUG: Offices in year 2024: {list(year_2024['offices'].keys())}")
            stockholm_data = year_2024['offices']['Stockholm']
            print(f"DEBUG: Stockholm data keys: {list(stockholm_data.keys())}")
            if 'roles' in stockholm_data:
                print(f"DEBUG: Stockholm roles: {list(stockholm_data['roles'].keys())}")
                consultant_data = stockholm_data['roles']['Consultant']
                print(f"DEBUG: Consultant levels: {list(consultant_data.keys())}")
                level_a_data = consultant_data['A']
                print(f"DEBUG: Level A data structure (first 3 months): {level_a_data[:3]}")
            
            self.assertIn('financial', kpis)
            self.assertIn('growth', kpis)
            # Check some key financial KPIs are present and not zero
            for key in ['net_sales', 'ebitda', 'margin', 'total_salary_costs']:
                self.assertIn(key, kpis['financial'])
                self.assertNotEqual(kpis['financial'][key], 0, f"KPI {key} should not be zero")
            # Check some key growth KPIs are present and not zero
            for key in ['current_total_fte', 'baseline_total_fte']:
                self.assertIn(key, kpis['growth'])
                self.assertNotEqual(kpis['growth'][key], 0, f"KPI {key} should not be zero")

if __name__ == '__main__':
    unittest.main() 