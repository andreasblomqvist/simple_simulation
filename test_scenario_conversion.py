#!/usr/bin/env python3
"""
Test script to verify scenario conversion between frontend and backend formats
"""
import sys
import os
sys.path.append('backend')

from backend.src.services.scenario_service import ScenarioService
from backend.src.services.config_service import config_service

def test_scenario_conversion():
    """Test that scenario conversion works correctly"""
    
    print("TESTING SCENARIO CONVERSION")
    print("=" * 50)
    
    # Create scenario service
    scenario_service = ScenarioService(config_service)
    
    # Create a test scenario with all fields populated
    scenario_data = {
        "name": "Test Conversion Scenario",
        "description": "Test scenario for conversion validation",
        "time_range": {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 3
        },
        "office_scope": ["Stockholm"],
        "baseline_input": {
            "global": {
                "recruitment": {
                    "Consultant": {
                        "levels": {
                            "A": {
                                "recruitment": {"values": {"202501": 5.0, "202502": 3.0, "202503": 7.0}},
                                "churn": {"values": {"202501": 2.0, "202502": 1.0, "202503": 3.0}}
                            },
                            "AC": {
                                "recruitment": {"values": {"202501": 3.0, "202502": 2.0, "202503": 4.0}},
                                "churn": {"values": {"202501": 1.0, "202502": 1.0, "202503": 2.0}}
                            }
                        }
                    }
                },
                "churn": {
                    "Consultant": {
                        "levels": {
                            "A": {
                                "recruitment": {"values": {"202501": 5.0, "202502": 3.0, "202503": 7.0}},
                                "churn": {"values": {"202501": 2.0, "202502": 1.0, "202503": 3.0}}
                            },
                            "AC": {
                                "recruitment": {"values": {"202501": 3.0, "202502": 2.0, "202503": 4.0}},
                                "churn": {"values": {"202501": 1.0, "202502": 1.0, "202503": 2.0}}
                            }
                        }
                    }
                }
            }
        },
        "levers": {
            "recruitment": {
                "Consultant": {
                    "A": 1.2,
                    "AC": 0.8
                }
            },
            "churn": {
                "Consultant": {
                    "A": 1.1,
                    "AC": 0.9
                }
            },
            "progression": {
                "Consultant": {
                    "A": 1.0,
                    "AC": 1.0
                }
            }
        },
        "economic_params": {
            "price_increase": 0.04,
            "salary_increase": 0.03,
            "unplanned_absence": 0.18,
            "hy_working_hours": 168.0,
            "other_expense": 20000000,
            "utr_adjustment": 0.01
        }
    }
    
    try:
        # Create the scenario
        result = scenario_service.create_scenario(scenario_data)
        scenario_id = result['scenario_id']
        print(f"✅ SUCCESS: Created scenario with ID: {scenario_id}")
        
        # Retrieve the scenario
        retrieved_scenario = scenario_service.get_scenario(scenario_id)
        print(f"✅ SUCCESS: Retrieved scenario: {retrieved_scenario['name']}")
        
        # Check if all fields are present
        print(f"  Name: {retrieved_scenario['name']}")
        print(f"  Description: {retrieved_scenario['description']}")
        print(f"  Time Range: {retrieved_scenario['time_range']}")
        print(f"  Office Scope: {retrieved_scenario['office_scope']}")
        print(f"  Has Baseline Input: {retrieved_scenario.get('baseline_input') is not None}")
        print(f"  Has Levers: {retrieved_scenario.get('levers') is not None}")
        print(f"  Has Economic Params: {retrieved_scenario.get('economic_params') is not None}")
        
        if retrieved_scenario.get('economic_params'):
            print(f"  Price Increase: {retrieved_scenario['economic_params']['price_increase']}")
            print(f"  Salary Increase: {retrieved_scenario['economic_params']['salary_increase']}")
            print(f"  Unplanned Absence: {retrieved_scenario['economic_params']['unplanned_absence']}")
        
        # Clean up
        scenario_service.delete_scenario(scenario_id)
        print(f"✅ SUCCESS: Cleaned up test scenario")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILURE: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_scenario_conversion()
    sys.exit(0 if success else 1) 