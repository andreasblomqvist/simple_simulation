#!/usr/bin/env python3
"""
Test script to debug the office builder and verify that recruitment values are preserved.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.src.services.office_builder import OfficeBuilder
from backend.src.services.scenario_resolver import ScenarioResolver
from backend.src.services.config_service import config_service

def test_office_builder():
    """Test that the office builder preserves recruitment values."""
    
    # Initialize services
    resolver = ScenarioResolver(config_service)
    builder = OfficeBuilder()
    
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
    
    # Check the resolved config
    stockholm_config = resolved['offices_config']['Stockholm']
    consultant_a_config = stockholm_config['roles']['Consultant']['A']
    
    print("Resolved config values:")
    print(f"recruitment_abs_1: {consultant_a_config.get('recruitment_abs_1', 0)}")
    print(f"recruitment_1: {consultant_a_config.get('recruitment_1', 0)}")
    print(f"churn_abs_1: {consultant_a_config.get('churn_abs_1', 0)}")
    print(f"churn_1: {consultant_a_config.get('churn_1', 0)}")
    
    # Build offices
    offices = builder.build_offices_from_config(resolved['offices_config'], resolved['progression_config'])
    
    # Check the built office
    stockholm_office = offices['Stockholm']
    consultant_a_level = stockholm_office.roles['Consultant']['A']
    
    print("\nBuilt office values:")
    print(f"recruitment_abs_1: {getattr(consultant_a_level, 'recruitment_abs_1', 'NOT FOUND')}")
    print(f"recruitment_1: {getattr(consultant_a_level, 'recruitment_1', 'NOT FOUND')}")
    print(f"churn_abs_1: {getattr(consultant_a_level, 'churn_abs_1', 'NOT FOUND')}")
    print(f"churn_1: {getattr(consultant_a_level, 'churn_1', 'NOT FOUND')}")
    
    # Check if values were preserved
    if getattr(consultant_a_level, 'recruitment_abs_1', 0) > 0:
        print("✅ Recruitment values preserved in office builder")
    else:
        print("❌ Recruitment values not preserved in office builder")
    
    if getattr(consultant_a_level, 'churn_abs_1', 0) > 0:
        print("✅ Churn values preserved in office builder")
    else:
        print("❌ Churn values not preserved in office builder")

if __name__ == "__main__":
    test_office_builder() 