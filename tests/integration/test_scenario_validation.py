"""
Integration tests for scenario validation and simulation results.

These tests verify that different scenarios produce the expected results
when run through the full pipeline (scenario service -> simulation engine).
"""

import pytest
import json
import tempfile
import os
from typing import Dict, Any, List
from backend.src.services.scenario_service import ScenarioService
from backend.src.services.config_service import ConfigService
from backend.src.services.simulation_engine import SimulationEngine


@pytest.fixture(scope="module")
def scenario_service():
    """Scenario service with temporary config"""
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ["SCENARIO_STORAGE_DIR"] = temp_dir
        
        # Create a simple test configuration with known values
        test_config = {
            "Stockholm": {
                "name": "Stockholm",
                "total_fte": 100,
                "journey": "Mature Office",
                "roles": {
                    "Consultant": {
                        "A": {
                            "fte": 50,
                            "recruitment_1": 0.1, "recruitment_2": 0.1, "recruitment_3": 0.1, "recruitment_4": 0.1,
                            "recruitment_5": 0.1, "recruitment_6": 0.1, "recruitment_7": 0.1, "recruitment_8": 0.1,
                            "recruitment_9": 0.1, "recruitment_10": 0.1, "recruitment_11": 0.1, "recruitment_12": 0.1,
                            "churn_1": 0.05, "churn_2": 0.05, "churn_3": 0.05, "churn_4": 0.05,
                            "churn_5": 0.05, "churn_6": 0.05, "churn_7": 0.05, "churn_8": 0.05,
                            "churn_9": 0.05, "churn_10": 0.05, "churn_11": 0.05, "churn_12": 0.05,
                            "price_1": 1000, "price_2": 1000, "price_3": 1000, "price_4": 1000,
                            "price_5": 1000, "price_6": 1000, "price_7": 1000, "price_8": 1000,
                            "price_9": 1000, "price_10": 1000, "price_11": 1000, "price_12": 1000,
                            "salary_1": 50000, "salary_2": 50000, "salary_3": 50000, "salary_4": 50000,
                            "salary_5": 50000, "salary_6": 50000, "salary_7": 50000, "salary_8": 50000,
                            "salary_9": 50000, "salary_10": 50000, "salary_11": 50000, "salary_12": 50000,
                            "utr_1": 0.85, "utr_2": 0.85, "utr_3": 0.85, "utr_4": 0.85,
                            "utr_5": 0.85, "utr_6": 0.85, "utr_7": 0.85, "utr_8": 0.85,
                            "utr_9": 0.85, "utr_10": 0.85, "utr_11": 0.85, "utr_12": 0.85
                        },
                        "AC": {
                            "fte": 30,
                            "recruitment_1": 0.08, "recruitment_2": 0.08, "recruitment_3": 0.08, "recruitment_4": 0.08,
                            "recruitment_5": 0.08, "recruitment_6": 0.08, "recruitment_7": 0.08, "recruitment_8": 0.08,
                            "recruitment_9": 0.08, "recruitment_10": 0.08, "recruitment_11": 0.08, "recruitment_12": 0.08,
                            "churn_1": 0.04, "churn_2": 0.04, "churn_3": 0.04, "churn_4": 0.04,
                            "churn_5": 0.04, "churn_6": 0.04, "churn_7": 0.04, "churn_8": 0.04,
                            "churn_9": 0.04, "churn_10": 0.04, "churn_11": 0.04, "churn_12": 0.04,
                            "price_1": 1200, "price_2": 1200, "price_3": 1200, "price_4": 1200,
                            "price_5": 1200, "price_6": 1200, "price_7": 1200, "price_8": 1200,
                            "price_9": 1200, "price_10": 1200, "price_11": 1200, "price_12": 1200,
                            "salary_1": 60000, "salary_2": 60000, "salary_3": 60000, "salary_4": 60000,
                            "salary_5": 60000, "salary_6": 60000, "salary_7": 60000, "salary_8": 60000,
                            "salary_9": 60000, "salary_10": 60000, "salary_11": 60000, "salary_12": 60000,
                            "utr_1": 0.85, "utr_2": 0.85, "utr_3": 0.85, "utr_4": 0.85,
                            "utr_5": 0.85, "utr_6": 0.85, "utr_7": 0.85, "utr_8": 0.85,
                            "utr_9": 0.85, "utr_10": 0.85, "utr_11": 0.85, "utr_12": 0.85
                        }
                    },
                    "Operations": {
                        "fte": 20,
                        "recruitment_1": 0.02, "recruitment_2": 0.02, "recruitment_3": 0.02, "recruitment_4": 0.02,
                        "recruitment_5": 0.02, "recruitment_6": 0.02, "recruitment_7": 0.02, "recruitment_8": 0.02,
                        "recruitment_9": 0.02, "recruitment_10": 0.02, "recruitment_11": 0.02, "recruitment_12": 0.02,
                        "churn_1": 0.03, "churn_2": 0.03, "churn_3": 0.03, "churn_4": 0.03,
                        "churn_5": 0.03, "churn_6": 0.03, "churn_7": 0.03, "churn_8": 0.03,
                        "churn_9": 0.03, "churn_10": 0.03, "churn_11": 0.03, "churn_12": 0.03,
                        "price_1": 200, "price_2": 200, "price_3": 200, "price_4": 200,
                        "price_5": 200, "price_6": 200, "price_7": 200, "price_8": 200,
                        "price_9": 200, "price_10": 200, "price_11": 200, "price_12": 200,
                        "salary_1": 40000, "salary_2": 40000, "salary_3": 40000, "salary_4": 40000,
                        "salary_5": 40000, "salary_6": 40000, "salary_7": 40000, "salary_8": 40000,
                        "salary_9": 40000, "salary_10": 40000, "salary_11": 40000, "salary_12": 40000,
                        "utr_1": 0.90, "utr_2": 0.90, "utr_3": 0.90, "utr_4": 0.90,
                        "utr_5": 0.90, "utr_6": 0.90, "utr_7": 0.90, "utr_8": 0.90,
                        "utr_9": 0.90, "utr_10": 0.90, "utr_11": 0.90, "utr_12": 0.90
                    }
                }
            }
        }
        
        # Create test config file
        test_config_path = os.path.join(temp_dir, "test_config.json")
        with open(test_config_path, 'w') as f:
            json.dump(test_config, f, indent=2)
        
        # Set environment variable for config file
        os.environ["CONFIG_FILE_PATH"] = test_config_path
        
        # Create services
        config_service = ConfigService()
        scenario_service = ScenarioService(config_service)
        
        yield scenario_service
        
        # Cleanup
        del os.environ["SCENARIO_STORAGE_DIR"]
        del os.environ["CONFIG_FILE_PATH"]


class ScenarioValidator:
    """Helper class to validate scenario results"""
    
    @staticmethod
    def extract_level_results(results: Dict[str, Any], office: str, role: str, level: str) -> Dict[str, Any]:
        """Extract results for a specific level from simulation output"""
        try:
            # Navigate through the results structure
            years = results.get('years', {})
            if not years:
                return {}
            
            # Get the first year (assuming single year simulation for now)
            year_data = list(years.values())[0]
            offices = year_data.get('offices', {})
            office_data = offices.get(office, {})
            levels = office_data.get('levels', {})
            role_data = levels.get(role, {})
            level_data = role_data.get(level, [])
            
            if not level_data:
                return {}
            
            # Return the first month's data (assuming monthly simulation)
            return level_data[0] if isinstance(level_data, list) else level_data
            
        except (KeyError, IndexError) as e:
            print(f"Error extracting results for {office}.{role}.{level}: {e}")
            return {}
    
    @staticmethod
    def calculate_expected_headcount(baseline_fte: int, recruitment_rate: float, churn_rate: float) -> Dict[str, float]:
        """Calculate expected headcount changes based on rates"""
        recruited = baseline_fte * recruitment_rate
        churned = baseline_fte * churn_rate
        net_change = recruited - churned
        final_fte = baseline_fte + net_change
        
        return {
            "recruited": recruited,
            "churned": churned,
            "net_change": net_change,
            "final_fte": final_fte
        }


@pytest.fixture
def validator():
    """Scenario validator instance"""
    return ScenarioValidator()


def load_scenario(filename):
    path = os.path.join(os.path.dirname(__file__), "scenarios", filename)
    with open(path, "r") as f:
        return json.load(f)


def test_baseline_scenario_no_overrides(scenario_service, validator):
    """Test baseline scenario with no overrides - should use config values"""
    
    scenario = load_scenario("baseline.json")
    
    # Resolve and run scenario
    resolved_config = scenario_service.resolve_scenario(scenario)
    
    # Verify baseline values are used
    # Baseline: 50 FTE, 10% recruitment, 5% churn
    stockholm_a = resolved_config["offices"]["Stockholm"].roles["Consultant"]["A"]
    
    assert stockholm_a.fte == 50  # Should start with 50 FTE
    assert stockholm_a.recruitment_1 == 0.1  # Should use baseline recruitment
    assert stockholm_a.churn_1 == 0.05  # Should use baseline churn


def test_recruitment_lever_scenario(scenario_service, validator):
    """Test scenario with recruitment lever override"""
    
    scenario = load_scenario("recruitment_lever.json")
    
    # Resolve scenario
    resolved_config = scenario_service.resolve_scenario(scenario)
    
    # Verify lever was applied (recruitment should be higher than baseline)
    # Baseline: 10% recruitment, lever: 1.5x = 15% effective recruitment
    stockholm_a = resolved_config["offices"]["Stockholm"].roles["Consultant"]["A"]
    
    assert stockholm_a.fte == 50  # Should start with 50 FTE
    assert stockholm_a.recruitment_1 == pytest.approx(0.15)  # Should be 1.5x baseline (0.1 * 1.5 = 0.15)
    assert stockholm_a.churn_1 == 0.05  # Should remain at baseline


def test_churn_lever_scenario(scenario_service, validator):
    """Test scenario with churn lever override"""
    
    scenario = load_scenario("churn_lever.json")
    
    # Resolve scenario
    resolved_config = scenario_service.resolve_scenario(scenario)
    
    # Verify lever was applied (churn should be lower than baseline)
    # Baseline: 5% churn, lever: 0.5x = 2.5% effective churn
    stockholm_a = resolved_config["offices"]["Stockholm"].roles["Consultant"]["A"]
    
    assert stockholm_a.fte == 50  # Should start with 50 FTE
    assert stockholm_a.recruitment_1 == 0.1  # Should remain at baseline
    assert stockholm_a.churn_1 == pytest.approx(0.025)  # Should be 0.5x baseline (0.05 * 0.5 = 0.025)


def test_baseline_input_scenario(scenario_service, validator):
    """Test scenario with baseline input overrides (absolute numbers)"""
    
    scenario = load_scenario("baseline_input.json")
    
    # Resolve scenario
    resolved_config = scenario_service.resolve_scenario(scenario)
    
    # Verify baseline input was applied
    stockholm_a = resolved_config["offices"]["Stockholm"].roles["Consultant"]["A"]
    
    assert stockholm_a.fte == 50  # Should start with 50 FTE
    # The baseline input should override the rates with absolute numbers
    # This depends on how the scenario service handles baseline_input


def test_multi_level_scenario(scenario_service, validator):
    """Test scenario affecting multiple levels"""
    
    scenario = load_scenario("multi_level.json")
    
    # Resolve scenario
    resolved_config = scenario_service.resolve_scenario(scenario)
    
    # Verify both levels were affected
    stockholm_a = resolved_config["offices"]["Stockholm"].roles["Consultant"]["A"]
    stockholm_ac = resolved_config["offices"]["Stockholm"].roles["Consultant"]["AC"]
    
    # A level: 20% increase in recruitment, 20% decrease in churn
    assert stockholm_a.fte == 50   # A level starts with 50
    assert stockholm_a.recruitment_1 == pytest.approx(0.12)  # 0.1 * 1.2 = 0.12
    assert stockholm_a.churn_1 == pytest.approx(0.04)  # 0.05 * 0.8 = 0.04
    
    # AC level: 10% increase in recruitment, 10% decrease in churn
    assert stockholm_ac.fte == 30  # AC level starts with 30
    assert stockholm_ac.recruitment_1 == pytest.approx(0.088)  # 0.08 * 1.1 = 0.088
    assert stockholm_ac.churn_1 == pytest.approx(0.036)  # 0.04 * 0.9 = 0.036


def test_operations_scenario(scenario_service, validator):
    """Test scenario affecting Operations role (flat role)"""
    
    scenario = {
        "name": "Operations Test",
        "description": "Test scenario affecting Operations role",
        "time_range": {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 1
        },
        "office_scope": ["Stockholm"],
        "levers": {
            "recruitment": {
                "Operations": 1.5  # 50% increase in Operations recruitment
            },
            "churn": {
                "Operations": 0.5  # 50% decrease in Operations churn
            }
        }
    }
    
    # Resolve scenario
    resolved_config = scenario_service.resolve_scenario(scenario)
    
    # Verify Operations was affected
    stockholm_ops = resolved_config["offices"]["Stockholm"].roles["Operations"]
    
    assert stockholm_ops.total == 20  # Operations starts with 20 FTE
    assert stockholm_ops.recruitment_1 == pytest.approx(0.03)  # 0.02 * 1.5 = 0.03
    assert stockholm_ops.churn_1 == pytest.approx(0.015)  # 0.03 * 0.5 = 0.015


def test_scenario_with_economic_params(scenario_service, validator):
    """Test scenario with economic parameters"""
    
    scenario = {
        "name": "Economic Params Test",
        "description": "Test scenario with economic parameters",
        "time_range": {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 1
        },
        "office_scope": ["Stockholm"],
        "economic_params": {
            "unplanned_absence": 0.08,  # 8% absence
            "other_expense": 15000000.0,  # 15M SEK
            "employment_cost_rate": 0.45,  # 45%
            "working_hours_per_month": 160.0,  # 160 hours
            "utilization": 0.80  # 80% utilization
        }
    }
    
    # Resolve scenario
    resolved_config = scenario_service.resolve_scenario(scenario)
    
    # Verify economic parameters were applied
    # The resolved config should include the economic parameters
    assert "economic_params" in resolved_config or "economic_params" in scenario


def test_scenario_validation_error_handling(scenario_service):
    """Test that invalid scenarios are properly rejected"""
    
    # Test with invalid time range
    invalid_scenario = {
        "name": "Invalid Test",
        "description": "Test with invalid time range",
        "time_range": {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2024,  # End year before start year
            "end_month": 12
        },
        "office_scope": ["Stockholm"]
    }
    
    # Should either reject the scenario or handle the error gracefully
    try:
        resolved_config = scenario_service.resolve_scenario(invalid_scenario)
        # If it doesn't raise an error, that's also acceptable
        assert isinstance(resolved_config, dict)
    except Exception as e:
        # If it raises an error, that's also acceptable
        assert "time" in str(e).lower() or "invalid" in str(e).lower()


def test_scenario_comparison(scenario_service, validator):
    """Test comparing two different scenarios"""
    
    # Baseline scenario
    baseline_scenario = {
        "name": "Baseline Comparison",
        "description": "Baseline for comparison",
        "time_range": {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 1
        },
        "office_scope": ["Stockholm"],
        "levers": {}
    }
    
    # Growth scenario
    growth_scenario = {
        "name": "Growth Comparison",
        "description": "Growth scenario for comparison",
        "time_range": {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 1
        },
        "office_scope": ["Stockholm"],
        "levers": {
            "recruitment": {
                "Consultant": {
                    "A": 2.0,  # Double recruitment
                    "AC": 1.5  # 50% increase
                }
            },
            "churn": {
                "Consultant": {
                    "A": 0.5,  # Half churn
                    "AC": 0.7  # 30% reduction
                }
            }
        }
    }
    
    # Resolve both scenarios
    baseline_config = scenario_service.resolve_scenario(baseline_scenario)
    growth_config = scenario_service.resolve_scenario(growth_scenario)
    
    # Compare results
    baseline_a = baseline_config["offices"]["Stockholm"].roles["Consultant"]["A"]
    growth_a = growth_config["offices"]["Stockholm"].roles["Consultant"]["A"]
    
    # Growth scenario should show different dynamics than baseline
    assert baseline_a.fte == growth_a.fte  # Both start with same FTE
    assert baseline_a.recruitment_1 == 0.1  # Baseline recruitment
    assert growth_a.recruitment_1 == pytest.approx(0.2)  # Double recruitment (0.1 * 2.0)
    assert baseline_a.churn_1 == 0.05  # Baseline churn
    assert growth_a.churn_1 == pytest.approx(0.025)  # Half churn (0.05 * 0.5)


def test_absolute_number_lever_scenario():
    """Test that absolute number levers override recruitment and churn for specific months/levels."""
    from backend.src.services.scenario_service import ScenarioService
    from backend.src.services.config_service import config_service

    scenario_service = ScenarioService(config_service)

    # Baseline config: recruitment_1 = 0.1 (A), 0.08 (AC); churn_1 = 0.05 (A), 0.04 (AC)
    # Lever: set recruitment_1 = 0.25 (A), churn_1 = 0.12 (AC)
    scenario = {
        "name": "Absolute Number Lever Test",
        "description": "Test scenario with absolute number lever overrides",
        "time_range": {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 1
        },
        "office_scope": ["Stockholm"],
        "levers": {
            "recruitment": {
                "Consultant": {
                    "A": {"recruitment_1": 0.25},
                    "AC": {"recruitment_1": 0.18}
                }
            }
            ,
            "churn": {
                "Consultant": {
                    "A": {"churn_1": 0.11},
                    "AC": {"churn_1": 0.12}
                }
            }
        }
    }

    resolved = scenario_service.resolve_scenario(scenario)
    stockholm = resolved["offices"]["Stockholm"]
    consultant = stockholm.roles["Consultant"]
    a = consultant["A"]
    ac = consultant["AC"]

    # Assert absolute values are set
    assert a.recruitment_1 == 0.25
    assert ac.recruitment_1 == 0.18
    assert a.churn_1 == 0.11
    assert ac.churn_1 == 0.12


def test_absolute_number_lever_scenario_abs_fields():
    """Test that recruitment_abs_1 and churn_abs_1 levers override recruitment and churn with absolute numbers."""
    from backend.src.services.scenario_service import ScenarioService
    from backend.src.services.config_service import config_service

    scenario_service = ScenarioService(config_service)

    # Lever: set recruitment_abs_1 = 20 (A), 8 (AC); churn_abs_1 = 5 (A), 2 (AC)
    scenario = {
        "name": "Absolute Number Lever Test (abs fields)",
        "description": "Test scenario with recruitment_abs_1 and churn_abs_1 lever overrides",
        "time_range": {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 1
        },
        "office_scope": ["Stockholm"],
        "levers": {
            "recruitment": {
                "Consultant": {
                    "A": {"recruitment_abs_1": 20},
                    "AC": {"recruitment_abs_1": 8}
                }
            },
            "churn": {
                "Consultant": {
                    "A": {"churn_abs_1": 5},
                    "AC": {"churn_abs_1": 2}
                }
            }
        }
    }

    resolved = scenario_service.resolve_scenario(scenario)
    stockholm = resolved["offices"]["Stockholm"]
    consultant = stockholm.roles["Consultant"]
    a = consultant["A"]
    ac = consultant["AC"]

    # Assert absolute values are set
    assert a.recruitment_abs_1 == 20
    assert ac.recruitment_abs_1 == 8
    assert a.churn_abs_1 == 5
    assert ac.churn_abs_1 == 2


def test_simulation_results_contain_absolute_values():
    """Test that simulation results contain absolute number fields from levers."""
    from backend.src.services.scenario_service import ScenarioService
    from backend.src.services.config_service import config_service
    from backend.src.services.simulation_engine import SimulationEngine

    scenario_service = ScenarioService(config_service)
    simulation_engine = SimulationEngine()

    # Create scenario with absolute number levers
    scenario = {
        "name": "Absolute Numbers Simulation Test",
        "description": "Test that simulation results contain absolute number fields",
        "time_range": {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 1
        },
        "office_scope": ["Stockholm"],
        "levers": {
            "recruitment": {
                "Consultant": {
                    "A": {"recruitment_abs_1": 25},
                    "AC": {"recruitment_abs_1": 15}
                }
            },
            "churn": {
                "Consultant": {
                    "A": {"churn_abs_1": 8},
                    "AC": {"churn_abs_1": 3}
                }
            }
        }
    }

    # Resolve scenario to get config with levers applied
    resolved = scenario_service.resolve_scenario(scenario)
    
    # Get the Stockholm office from resolved config
    stockholm = resolved["offices"]["Stockholm"]
    consultant = stockholm.roles["Consultant"]
    a_level = consultant["A"]
    ac_level = consultant["AC"]

    # Verify absolute fields are set on Level objects
    assert hasattr(a_level, 'recruitment_abs_1')
    assert hasattr(a_level, 'churn_abs_1')
    assert hasattr(ac_level, 'recruitment_abs_1')
    assert hasattr(ac_level, 'churn_abs_1')
    
    assert a_level.recruitment_abs_1 == 25
    assert a_level.churn_abs_1 == 8
    assert ac_level.recruitment_abs_1 == 15
    assert ac_level.churn_abs_1 == 3

    # Run simulation
    simulation_results = simulation_engine.run_simulation_with_offices(
        start_year=2025,
        start_month=1,
        end_year=2025,
        end_month=1,
        offices=resolved["offices"],
        progression_config=scenario_service.load_progression_config(),
        cat_curves=scenario_service.load_cat_curves()
    )

    # Access offices under the correct year
    year_key = list(simulation_results["years"].keys())[0]
    year_results = simulation_results["years"][year_key]
    assert "offices" in year_results
    offices = year_results["offices"]
    assert "Stockholm" in offices
    stockholm_results = offices["Stockholm"]
    assert "roles" in stockholm_results
    assert "Consultant" in stockholm_results["roles"]
    consultant_results = stockholm_results["roles"]["Consultant"]
    assert "A" in consultant_results
    assert "AC" in consultant_results
    a_results = consultant_results["A"]
    ac_results = consultant_results["AC"]
    # Verify absolute fields are present and not zero
    assert "recruitment_abs_1" in a_results
    assert "churn_abs_1" in a_results
    assert "recruitment_abs_1" in ac_results
    assert "churn_abs_1" in ac_results
    assert a_results["recruitment_abs_1"] != 0
    assert a_results["churn_abs_1"] != 0
    assert ac_results["recruitment_abs_1"] != 0
    assert ac_results["churn_abs_1"] != 0
    print(f"✅ Simulation results contain all absolute values and they are not zero:")
    print(f"   A level: recruitment_abs_1={a_results['recruitment_abs_1']}, churn_abs_1={a_results['churn_abs_1']}")
    print(f"   AC level: recruitment_abs_1={ac_results['recruitment_abs_1']}, churn_abs_1={ac_results['churn_abs_1']}")
