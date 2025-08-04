#!/usr/bin/env python3
"""
Test script to debug baseline input processing.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.src.services.scenario_resolver import ScenarioResolver
from backend.src.services.config_service import config_service

def test_baseline_processing():
    """Test that baseline input is processed correctly."""
    
    # Initialize scenario resolver
    resolver = ScenarioResolver(config_service)
    
    # Get base config
    base_config = config_service.get_config()
    
    # Create test scenario with baseline input
    test_scenario = {
        'name': 'test',
        'description': 'test',
        'time_range': {
            'start_year': 2025,
            'start_month': 1,
            'end_year': 2027,
            'end_month': 12
        },
        'office_scope': ['Group'],
        'levers': {},
        'economic_params': {},
        'baseline_input': {
            'global': {
                'recruitment': {
                    'Consultant': {
                        'levels': {
                            'A': {
                                'recruitment': {
                                    'values': {
                                        '202501': 10.0,
                                        '202502': 10.0,
                                        '202503': 10.0
                                    }
                                },
                                'churn': {
                                    'values': {
                                        '202501': 2.0,
                                        '202502': 2.0,
                                        '202503': 2.0
                                    }
                                }
                            }
                        }
                    }
                },
                'churn': {
                    'Consultant': {
                        'levels': {
                            'A': {
                                'recruitment': {
                                    'values': {
                                        '202501': 2.0,
                                        '202502': 2.0,
                                        '202503': 2.0
                                    }
                                },
                                'churn': {
                                    'values': {
                                        '202501': 2.0,
                                        '202502': 2.0,
                                        '202503': 2.0
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    # Resolve scenario
    resolved = resolver.resolve_scenario(test_scenario)
    
    # Check Stockholm office
    stockholm = resolved['offices_config']['Stockholm']
    consultant_a = stockholm['roles']['Consultant']['A']
    
    print("Stockholm Consultant A baseline values:")
    print(f"recruitment_abs_1: {consultant_a.get('recruitment_abs_1', 0)}")
    print(f"recruitment_1: {consultant_a.get('recruitment_1', 0)}")
    print(f"churn_abs_1: {consultant_a.get('churn_abs_1', 0)}")
    print(f"churn_1: {consultant_a.get('churn_1', 0)}")
    
    # Check if values were applied
    if consultant_a.get('recruitment_abs_1', 0) > 0:
        print("✅ Recruitment baseline applied correctly")
    else:
        print("❌ Recruitment baseline not applied")
    
    if consultant_a.get('churn_abs_1', 0) > 0:
        print("✅ Churn baseline applied correctly")
    else:
        print("❌ Churn baseline not applied")

if __name__ == "__main__":
    test_baseline_processing() 