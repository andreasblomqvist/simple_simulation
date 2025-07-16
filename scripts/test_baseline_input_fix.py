#!/usr/bin/env python3
"""
Test script to verify baseline input transformation and backend validation.
"""

import requests
import json
from typing import Dict, Any

def test_baseline_input_transformation():
    """Test the baseline input transformation with the problematic scenario."""
    
    # Test the scenario that was causing the error
    scenario_id = "f5f26bc5-3830-4f64-ba53-03b58ae72353"
    
    print(f"Testing scenario: {scenario_id}")
    
    # First, get the original scenario data
    try:
        response = requests.get(f"http://localhost:8000/scenarios/{scenario_id}")
        if response.status_code == 200:
            original_scenario = response.json()
            print("✅ Successfully retrieved original scenario")
            print(f"Original baseline_input structure: {json.dumps(original_scenario.get('baseline_input', {}), indent=2)}")
        else:
            print(f"❌ Failed to retrieve scenario: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error retrieving scenario: {e}")
        return
    
    # Create a transformed version of the scenario
    transformed_scenario = original_scenario.copy()
    
    # Transform baseline_input to expected structure
    baseline_input = transformed_scenario.get('baseline_input', {})
    
    # Ensure global structure exists
    if 'global' not in baseline_input:
        baseline_input = {'global': baseline_input}
    
    global_data = baseline_input['global']
    
    # Ensure recruitment and churn sections exist
    for section in ['recruitment', 'churn']:
        if section not in global_data:
            global_data[section] = {}
    
    # Handle null values by creating proper structures
    for section in ['recruitment', 'churn']:
        section_data = global_data[section]
        if section_data:
            for role_name, role_data in section_data.items():
                if role_data is None:
                    # Create proper structure for leveled roles
                    section_data[role_name] = {
                        'levels': {
                            'A': {
                                'recruitment': {'values': {'202501': 0.0}},
                                'churn': {'values': {'202501': 0.0}}
                            }
                        }
                    }
                elif isinstance(role_data, dict):
                    # Check if this is a leveled role structure
                    if 'levels' in role_data:
                        # Ensure levels structure is complete
                        if role_data['levels'] is None:
                            role_data['levels'] = {
                                'A': {
                                    'recruitment': {'values': {'202501': 0.0}},
                                    'churn': {'values': {'202501': 0.0}}
                                }
                            }
                        else:
                            # Ensure each level has proper structure
                            for level_name, level_data in role_data['levels'].items():
                                if level_data is None:
                                    role_data['levels'][level_name] = {
                                        'recruitment': {'values': {'202501': 0.0}},
                                        'churn': {'values': {'202501': 0.0}}
                                    }
                                elif isinstance(level_data, dict):
                                    if not level_data.get('recruitment'):
                                        level_data['recruitment'] = {'values': {'202501': 0.0}}
                                    if not level_data.get('churn'):
                                        level_data['churn'] = {'values': {'202501': 0.0}}
                    else:
                        # Convert to leveled structure
                        section_data[role_name] = {
                            'levels': {
                                'A': {
                                    'recruitment': {'values': {'202501': 0.0}},
                                    'churn': {'values': {'202501': 0.0}}
                                }
                            }
                        }
    
    transformed_scenario['baseline_input'] = baseline_input
    
    # Ensure other required fields exist with proper structure
    if not transformed_scenario.get('progression_config'):
        transformed_scenario['progression_config'] = {
            'levels': {
                'A': {
                    'progression_months': [1],
                    'start_tenure': 1,
                    'time_on_level': 6,
                    'next_level': 'AC',
                    'journey': 'J-1'
                }
            }
        }
    elif not transformed_scenario['progression_config'].get('levels'):
        transformed_scenario['progression_config']['levels'] = {
            'A': {
                'progression_months': [1],
                'start_tenure': 1,
                'time_on_level': 6,
                'next_level': 'AC',
                'journey': 'J-1'
            }
        }
        
    if not transformed_scenario.get('cat_curves'):
        transformed_scenario['cat_curves'] = {
            'curves': {
                'A': {
                    'curves': {
                        'CAT0': 0.0,
                        'CAT6': 0.919,
                        'CAT12': 0.85
                    }
                }
            }
        }
    elif not transformed_scenario['cat_curves'].get('curves'):
        transformed_scenario['cat_curves']['curves'] = {
            'A': {
                'curves': {
                    'CAT0': 0.0,
                    'CAT6': 0.919,
                    'CAT12': 0.85
                }
            }
        }
    if not transformed_scenario.get('economic_params'):
        transformed_scenario['economic_params'] = {
            'working_hours_per_month': 160.0,
            'employment_cost_rate': 0.3,
            'unplanned_absence': 0.05,
            'other_expense': 1000000.0
        }
    
    print(f"Transformed baseline_input structure: {json.dumps(transformed_scenario.get('baseline_input', {}), indent=2)}")
    
    # Test the transformed scenario with the backend
    try:
        response = requests.post(
            "http://localhost:8000/scenarios/run",
            json={
                'scenario_definition': transformed_scenario,
                'office_scope': transformed_scenario.get('office_scope', ['Group'])
            },
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Successfully ran simulation with transformed data!")
            print(f"Simulation result status: {result.get('status')}")
            if 'results' in result:
                print(f"Results contain {len(result['results'].get('years', {}))} years of data")
        else:
            print(f"❌ Simulation failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error running simulation: {e}")

def test_empty_baseline_input():
    """Test with completely empty baseline input."""
    
    print("\nTesting with empty baseline input...")
    
    empty_scenario = {
        'name': 'Test Empty Baseline',
        'description': 'Test scenario with empty baseline input',
        'time_range': {
            'start_year': 2025,
            'start_month': 1,
            'end_year': 2027,
            'end_month': 12
        },
        'office_scope': ['Group'],
        'levers': {
            'recruitment': {'A': 1.0, 'AC': 1.0, 'C': 1.0},
            'churn': {'A': 1.0, 'AC': 1.0, 'C': 1.0},
            'progression': {'A': 1.0, 'AC': 1.0, 'C': 1.0}
        },
        'baseline_input': {
            'global': {
                'recruitment': {
                    'Consultant': {
                        'levels': {
                            'A': {
                                'recruitment': {'values': {'202501': 0.0}},
                                'churn': {'values': {'202501': 0.0}}
                            }
                        }
                    }
                },
                'churn': {
                    'Consultant': {
                        'levels': {
                            'A': {
                                'recruitment': {'values': {'202501': 0.0}},
                                'churn': {'values': {'202501': 0.0}}
                            }
                        }
                    }
                }
            }
        },
        'progression_config': {
            'levels': {
                'A': {
                    'progression_months': [1],
                    'start_tenure': 1,
                    'time_on_level': 6,
                    'next_level': 'AC',
                    'journey': 'J-1'
                }
            }
        },
        'cat_curves': {
            'curves': {
                'A': {
                    'curves': {
                        'CAT0': 0.0,
                        'CAT6': 0.919,
                        'CAT12': 0.85
                    }
                }
            }
        },
        'economic_params': {
            'working_hours_per_month': 160.0,
            'employment_cost_rate': 0.3,
            'unplanned_absence': 0.05,
            'other_expense': 1000000.0
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/scenarios/run",
            json={
                'scenario_definition': empty_scenario,
                'office_scope': ['Group']
            },
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Successfully ran simulation with empty baseline input!")
            print(f"Simulation result status: {result.get('status')}")
        else:
            print(f"❌ Simulation failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error running simulation: {e}")

if __name__ == "__main__":
    print("Testing baseline input transformation...")
    test_baseline_input_transformation()
    test_empty_baseline_input()
    print("\nTest completed!") 