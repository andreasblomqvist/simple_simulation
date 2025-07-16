#!/usr/bin/env python3
"""
Test Global vs Offices Structure
================================

Test to compare how the scenario resolver handles different baseline_input structures.
"""

import requests
import json
from test_scenarios import get_scenario_by_name

def test_global_structure():
    """Test with global structure (what the resolver expects)."""
    
    print("🌍 TESTING GLOBAL STRUCTURE")
    print("=" * 50)
    
    # Create scenario with global structure
    scenario_definition = {
        "name": "Global Structure Test",
        "description": "Test with global baseline input structure",
        "time_range": {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2025,
            "end_month": 12
        },
        "office_scope": ["Stockholm"],
        "levers": {},
        "economic_params": {
            "working_hours_per_month": 160.0,
            "employment_cost_rate": 0.3,
            "unplanned_absence": 0.05,
            "other_expense": 1000000.0
        },
        "baseline_input": {
            "global": {
                "recruitment": {
                    "Consultant": {
                        "A": {
                            "202501": 5.0,  # 5 people in January 2025
                            "202502": 5.0,  # 5 people in February 2025
                            "202503": 5.0,
                            "202504": 5.0,
                            "202505": 5.0,
                            "202506": 5.0,
                            "202507": 5.0,
                            "202508": 5.0,
                            "202509": 5.0,
                            "202510": 5.0,
                            "202511": 5.0,
                            "202512": 5.0
                        }
                    }
                },
                "churn": {
                    "Consultant": {
                        "A": {
                            "202501": 2.0,  # 2 people in January 2025
                            "202502": 2.0,
                            "202503": 2.0,
                            "202504": 2.0,
                            "202505": 2.0,
                            "202506": 2.0,
                            "202507": 2.0,
                            "202508": 2.0,
                            "202509": 2.0,
                            "202510": 2.0,
                            "202511": 2.0,
                            "202512": 2.0
                        }
                    }
                }
            }
        },
        "cat_curves": {
            "A": {
                "CAT0": 0.0,
                "CAT6": 0.919,
                "CAT12": 0.85,
                "CAT18": 0.0,
                "CAT24": 0.0,
                "CAT30": 0.0
            },
            "AC": {
                "CAT0": 0.0,
                "CAT6": 0.054,
                "CAT12": 0.759,
                "CAT18": 0.4,
                "CAT24": 0.0,
                "CAT30": 0.0
            },
            "C": {
                "CAT0": 0.0,
                "CAT6": 0.05,
                "CAT12": 0.442,
                "CAT18": 0.597,
                "CAT24": 0.278,
                "CAT30": 0.643,
                "CAT36": 0.2,
                "CAT42": 0.0
            },
            "SrC": {
                "CAT0": 0.0,
                "CAT6": 0.206,
                "CAT12": 0.438,
                "CAT18": 0.317,
                "CAT24": 0.211,
                "CAT30": 0.206,
                "CAT36": 0.167,
                "CAT42": 0.0,
                "CAT48": 0.0,
                "CAT54": 0.0,
                "CAT60": 0.0
            },
            "AM": {
                "CAT0": 0.0,
                "CAT6": 0.0,
                "CAT12": 0.0,
                "CAT18": 0.189,
                "CAT24": 0.197,
                "CAT30": 0.234,
                "CAT36": 0.048,
                "CAT42": 0.0,
                "CAT48": 0.0,
                "CAT54": 0.0,
                "CAT60": 0.0
            },
            "M": {
                "CAT0": 0.0,
                "CAT6": 0.0,
                "CAT12": 0.01,
                "CAT18": 0.02,
                "CAT24": 0.03,
                "CAT30": 0.04,
                "CAT36": 0.05,
                "CAT42": 0.06,
                "CAT48": 0.07,
                "CAT54": 0.08,
                "CAT60": 0.1
            },
            "SrM": {
                "CAT0": 0.0,
                "CAT6": 0.0,
                "CAT12": 0.005,
                "CAT18": 0.01,
                "CAT24": 0.015,
                "CAT30": 0.02,
                "CAT36": 0.025,
                "CAT42": 0.03,
                "CAT48": 0.04,
                "CAT54": 0.05,
                "CAT60": 0.06
            },
            "Pi": {
                "CAT0": 0.0
            },
            "P": {
                "CAT0": 0.0
            },
            "X": {
                "CAT0": 0.0
            },
            "OPE": {
                "CAT0": 0.0
            }
        }
    }
    
    # Run simulation
    print("🔄 Running simulation with global structure...")
    
    request_data = {
        "scenario_definition": scenario_definition
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/scenarios/run",
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            results = response.json()
            print("✅ Simulation completed!")
            
            # Show results
            years_data = results.get('results', {}).get('years', {})
            for year_str, year_data in years_data.items():
                print(f"\n📅 YEAR {year_str}:")
                offices_data = year_data.get('offices', {})
                
                for office_name, office_data in offices_data.items():
                    print(f"\n🏢 {office_name}:")
                    roles_data = office_data.get('roles', {})
                    
                    for role_name, role_data in roles_data.items():
                        if isinstance(role_data, dict):
                            for level_name, level_data in role_data.items():
                                if isinstance(level_data, list) and level_data:
                                    last_month = level_data[-1]
                                    fte = last_month.get('fte', 0)
                                    revenue = last_month.get('revenue', 0)
                                    cost = last_month.get('cost', 0)
                                    profit = last_month.get('profit', 0)
                                    
                                    print(f"  {role_name}.{level_name}:")
                                    print(f"    FTE: {fte:.1f}")
                                    print(f"    Revenue: ${revenue:,.0f}")
                                    print(f"    Cost: ${cost:,.0f}")
                                    print(f"    Profit: ${profit:,.0f}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_offices_structure():
    """Test with offices structure (what our test scenarios use)."""
    
    print("\n🏢 TESTING OFFICES STRUCTURE")
    print("=" * 50)
    
    # Use our existing minimal scenario (which has offices structure)
    scenario_definition = get_scenario_by_name("minimal")
    
    # Run simulation
    print("🔄 Running simulation with offices structure...")
    
    request_data = {
        "scenario_definition": scenario_definition
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/scenarios/run",
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            results = response.json()
            print("✅ Simulation completed!")
            
            # Show results
            years_data = results.get('results', {}).get('years', {})
            for year_str, year_data in years_data.items():
                print(f"\n📅 YEAR {year_str}:")
                offices_data = year_data.get('offices', {})
                
                for office_name, office_data in offices_data.items():
                    print(f"\n🏢 {office_name}:")
                    roles_data = office_data.get('roles', {})
                    
                    for role_name, role_data in roles_data.items():
                        if isinstance(role_data, dict):
                            for level_name, level_data in role_data.items():
                                if isinstance(level_data, list) and level_data:
                                    last_month = level_data[-1]
                                    fte = last_month.get('fte', 0)
                                    revenue = last_month.get('revenue', 0)
                                    cost = last_month.get('cost', 0)
                                    profit = last_month.get('profit', 0)
                                    
                                    print(f"  {role_name}.{level_name}:")
                                    print(f"    FTE: {fte:.1f}")
                                    print(f"    Revenue: ${revenue:,.0f}")
                                    print(f"    Cost: ${cost:,.0f}")
                                    print(f"    Profit: ${profit:,.0f}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def main():
    """Main function."""
    
    print("🔍 COMPARING GLOBAL vs OFFICES STRUCTURE")
    print("=" * 60)
    
    # Test both structures
    test_global_structure()
    test_offices_structure()
    
    print(f"\n" + "=" * 60)
    print("✅ Comparison completed!")

if __name__ == "__main__":
    main() 