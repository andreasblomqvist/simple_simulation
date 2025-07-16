#!/usr/bin/env python3
"""
Complete Scenario Definition Example
====================================

This script demonstrates a fully specified scenario definition that matches
exactly what the simulation engine expects, using absolute numbers for
recruitment and churn (never percentages).

Key Requirements:
- All offices, roles, and levels explicitly defined
- Absolute recruitment/churn values (not percentages)
- All required fields populated
- No reliance on defaults or transformations
"""

import requests
import json
from datetime import datetime

def create_complete_scenario_definition():
    """Create a fully specified scenario definition with absolute values."""
    
    # Generate all months for 2025-2027
    months = []
    for year in [2025, 2026, 2027]:
        for month in range(1, 13):
            months.append(f"{year}{month:02d}")
    
    # Create monthly recruitment/churn data with absolute numbers
    def create_monthly_data(value):
        return {month: value for month in months}
    
    scenario_definition = {
        "name": "Complete Absolute Values Test",
        "description": "Fully specified scenario with absolute recruitment/churn values",
        "time_range": {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2027,
            "end_month": 12
        },
        "office_scope": ["Stockholm", "Gothenburg", "Malmö"],
        "levers": {},  # No lever multipliers - using absolute values only
        "economic_params": {
            "working_hours_per_month": 160.0,
            "employment_cost_rate": 0.3,
            "unplanned_absence": 0.05,
            "other_expense": 1000000.0
        },
        "baseline_input": {
            "offices": {
                "Stockholm": {
                    "name": "Stockholm",
                    "total_fte": 821,
                    "journey": "Mature Office",
                    "roles": {
                        "Consultant": {
                            "A": {
                                "fte": 69.0,
                                "price_1": 1200.0,
                                "salary_1": 45000.0,
                                "utr_1": 0.85,
                                "recruitment_abs_1": 10,  # Absolute recruitment for January
                                "recruitment_abs_2": 10,  # Absolute recruitment for February
                                "recruitment_abs_3": 10,
                                "recruitment_abs_4": 10,
                                "recruitment_abs_5": 10,
                                "recruitment_abs_6": 10,
                                "recruitment_abs_7": 10,
                                "recruitment_abs_8": 10,
                                "recruitment_abs_9": 10,
                                "recruitment_abs_10": 10,
                                "recruitment_abs_11": 10,
                                "recruitment_abs_12": 10,
                                "churn_abs_1": 5,  # Absolute churn for January
                                "churn_abs_2": 5,  # Absolute churn for February
                                "churn_abs_3": 5,
                                "churn_abs_4": 5,
                                "churn_abs_5": 5,
                                "churn_abs_6": 5,
                                "churn_abs_7": 5,
                                "churn_abs_8": 5,
                                "churn_abs_9": 5,
                                "churn_abs_10": 5,
                                "churn_abs_11": 5,
                                "churn_abs_12": 5
                            },
                            "AC": {
                                "fte": 45.0,
                                "price_1": 1300.0,
                                "salary_1": 55000.0,
                                "utr_1": 0.85,
                                "recruitment_abs_1": 8,
                                "recruitment_abs_2": 8,
                                "recruitment_abs_3": 8,
                                "recruitment_abs_4": 8,
                                "recruitment_abs_5": 8,
                                "recruitment_abs_6": 8,
                                "recruitment_abs_7": 8,
                                "recruitment_abs_8": 8,
                                "recruitment_abs_9": 8,
                                "recruitment_abs_10": 8,
                                "recruitment_abs_11": 8,
                                "recruitment_abs_12": 8,
                                "churn_abs_1": 4,
                                "churn_abs_2": 4,
                                "churn_abs_3": 4,
                                "churn_abs_4": 4,
                                "churn_abs_5": 4,
                                "churn_abs_6": 4,
                                "churn_abs_7": 4,
                                "churn_abs_8": 4,
                                "churn_abs_9": 4,
                                "churn_abs_10": 4,
                                "churn_abs_11": 4,
                                "churn_abs_12": 4
                            },
                            "C": {
                                "fte": 120.0,
                                "price_1": 1400.0,
                                "salary_1": 65000.0,
                                "utr_1": 0.85,
                                "recruitment_abs_1": 15,
                                "recruitment_abs_2": 15,
                                "recruitment_abs_3": 15,
                                "recruitment_abs_4": 15,
                                "recruitment_abs_5": 15,
                                "recruitment_abs_6": 15,
                                "recruitment_abs_7": 15,
                                "recruitment_abs_8": 15,
                                "recruitment_abs_9": 15,
                                "recruitment_abs_10": 15,
                                "recruitment_abs_11": 15,
                                "recruitment_abs_12": 15,
                                "churn_abs_1": 8,
                                "churn_abs_2": 8,
                                "churn_abs_3": 8,
                                "churn_abs_4": 8,
                                "churn_abs_5": 8,
                                "churn_abs_6": 8,
                                "churn_abs_7": 8,
                                "churn_abs_8": 8,
                                "churn_abs_9": 8,
                                "churn_abs_10": 8,
                                "churn_abs_11": 8,
                                "churn_abs_12": 8
                            }
                        },
                        "Operations": {
                            "fte": 12.0,
                            "price_1": 80.0,
                            "salary_1": 35000.0,
                            "utr_1": 0.85,
                            "recruitment_abs_1": 2,
                            "recruitment_abs_2": 2,
                            "recruitment_abs_3": 2,
                            "recruitment_abs_4": 2,
                            "recruitment_abs_5": 2,
                            "recruitment_abs_6": 2,
                            "recruitment_abs_7": 2,
                            "recruitment_abs_8": 2,
                            "recruitment_abs_9": 2,
                            "recruitment_abs_10": 2,
                            "recruitment_abs_11": 2,
                            "recruitment_abs_12": 2,
                            "churn_abs_1": 1,
                            "churn_abs_2": 1,
                            "churn_abs_3": 1,
                            "churn_abs_4": 1,
                            "churn_abs_5": 1,
                            "churn_abs_6": 1,
                            "churn_abs_7": 1,
                            "churn_abs_8": 1,
                            "churn_abs_9": 1,
                            "churn_abs_10": 1,
                            "churn_abs_11": 1,
                            "churn_abs_12": 1
                        }
                    }
                },
                "Gothenburg": {
                    "name": "Gothenburg",
                    "total_fte": 245,
                    "journey": "Established Office",
                    "roles": {
                        "Consultant": {
                            "A": {
                                "fte": 25.0,
                                "price_1": 1100.0,
                                "salary_1": 42000.0,
                                "utr_1": 0.85,
                                "recruitment_abs_1": 5,
                                "recruitment_abs_2": 5,
                                "recruitment_abs_3": 5,
                                "recruitment_abs_4": 5,
                                "recruitment_abs_5": 5,
                                "recruitment_abs_6": 5,
                                "recruitment_abs_7": 5,
                                "recruitment_abs_8": 5,
                                "recruitment_abs_9": 5,
                                "recruitment_abs_10": 5,
                                "recruitment_abs_11": 5,
                                "recruitment_abs_12": 5,
                                "churn_abs_1": 3,
                                "churn_abs_2": 3,
                                "churn_abs_3": 3,
                                "churn_abs_4": 3,
                                "churn_abs_5": 3,
                                "churn_abs_6": 3,
                                "churn_abs_7": 3,
                                "churn_abs_8": 3,
                                "churn_abs_9": 3,
                                "churn_abs_10": 3,
                                "churn_abs_11": 3,
                                "churn_abs_12": 3
                            },
                            "C": {
                                "fte": 35.0,
                                "price_1": 1300.0,
                                "salary_1": 60000.0,
                                "utr_1": 0.85,
                                "recruitment_abs_1": 8,
                                "recruitment_abs_2": 8,
                                "recruitment_abs_3": 8,
                                "recruitment_abs_4": 8,
                                "recruitment_abs_5": 8,
                                "recruitment_abs_6": 8,
                                "recruitment_abs_7": 8,
                                "recruitment_abs_8": 8,
                                "recruitment_abs_9": 8,
                                "recruitment_abs_10": 8,
                                "recruitment_abs_11": 8,
                                "recruitment_abs_12": 8,
                                "churn_abs_1": 4,
                                "churn_abs_2": 4,
                                "churn_abs_3": 4,
                                "churn_abs_4": 4,
                                "churn_abs_5": 4,
                                "churn_abs_6": 4,
                                "churn_abs_7": 4,
                                "churn_abs_8": 4,
                                "churn_abs_9": 4,
                                "churn_abs_10": 4,
                                "churn_abs_11": 4,
                                "churn_abs_12": 4
                            }
                        },
                        "Operations": {
                            "fte": 8.0,
                            "price_1": 75.0,
                            "salary_1": 32000.0,
                            "utr_1": 0.85,
                            "recruitment_abs_1": 1,
                            "recruitment_abs_2": 1,
                            "recruitment_abs_3": 1,
                            "recruitment_abs_4": 1,
                            "recruitment_abs_5": 1,
                            "recruitment_abs_6": 1,
                            "recruitment_abs_7": 1,
                            "recruitment_abs_8": 1,
                            "recruitment_abs_9": 1,
                            "recruitment_abs_10": 1,
                            "recruitment_abs_11": 1,
                            "recruitment_abs_12": 1,
                            "churn_abs_1": 1,
                            "churn_abs_2": 1,
                            "churn_abs_3": 1,
                            "churn_abs_4": 1,
                            "churn_abs_5": 1,
                            "churn_abs_6": 1,
                            "churn_abs_7": 1,
                            "churn_abs_8": 1,
                            "churn_abs_9": 1,
                            "churn_abs_10": 1,
                            "churn_abs_11": 1,
                            "churn_abs_12": 1
                        }
                    }
                },
                "Malmö": {
                    "name": "Malmö",
                    "total_fte": 156,
                    "journey": "Emerging Office",
                    "roles": {
                        "Consultant": {
                            "A": {
                                "fte": 18.0,
                                "price_1": 1050.0,
                                "salary_1": 40000.0,
                                "utr_1": 0.85,
                                "recruitment_abs_1": 4,
                                "recruitment_abs_2": 4,
                                "recruitment_abs_3": 4,
                                "recruitment_abs_4": 4,
                                "recruitment_abs_5": 4,
                                "recruitment_abs_6": 4,
                                "recruitment_abs_7": 4,
                                "recruitment_abs_8": 4,
                                "recruitment_abs_9": 4,
                                "recruitment_abs_10": 4,
                                "recruitment_abs_11": 4,
                                "recruitment_abs_12": 4,
                                "churn_abs_1": 2,
                                "churn_abs_2": 2,
                                "churn_abs_3": 2,
                                "churn_abs_4": 2,
                                "churn_abs_5": 2,
                                "churn_abs_6": 2,
                                "churn_abs_7": 2,
                                "churn_abs_8": 2,
                                "churn_abs_9": 2,
                                "churn_abs_10": 2,
                                "churn_abs_11": 2,
                                "churn_abs_12": 2
                            },
                            "C": {
                                "fte": 22.0,
                                "price_1": 1250.0,
                                "salary_1": 58000.0,
                                "utr_1": 0.85,
                                "recruitment_abs_1": 6,
                                "recruitment_abs_2": 6,
                                "recruitment_abs_3": 6,
                                "recruitment_abs_4": 6,
                                "recruitment_abs_5": 6,
                                "recruitment_abs_6": 6,
                                "recruitment_abs_7": 6,
                                "recruitment_abs_8": 6,
                                "recruitment_abs_9": 6,
                                "recruitment_abs_10": 6,
                                "recruitment_abs_11": 6,
                                "recruitment_abs_12": 6,
                                "churn_abs_1": 3,
                                "churn_abs_2": 3,
                                "churn_abs_3": 3,
                                "churn_abs_4": 3,
                                "churn_abs_5": 3,
                                "churn_abs_6": 3,
                                "churn_abs_7": 3,
                                "churn_abs_8": 3,
                                "churn_abs_9": 3,
                                "churn_abs_10": 3,
                                "churn_abs_11": 3,
                                "churn_abs_12": 3
                            }
                        },
                        "Operations": {
                            "fte": 6.0,
                            "price_1": 70.0,
                            "salary_1": 30000.0,
                            "utr_1": 0.85,
                            "recruitment_abs_1": 1,
                            "recruitment_abs_2": 1,
                            "recruitment_abs_3": 1,
                            "recruitment_abs_4": 1,
                            "recruitment_abs_5": 1,
                            "recruitment_abs_6": 1,
                            "recruitment_abs_7": 1,
                            "recruitment_abs_8": 1,
                            "recruitment_abs_9": 1,
                            "recruitment_abs_10": 1,
                            "recruitment_abs_11": 1,
                            "recruitment_abs_12": 1,
                            "churn_abs_1": 1,
                            "churn_abs_2": 1,
                            "churn_abs_3": 1,
                            "churn_abs_4": 1,
                            "churn_abs_5": 1,
                            "churn_abs_6": 1,
                            "churn_abs_7": 1,
                            "churn_abs_8": 1,
                            "churn_abs_9": 1,
                            "churn_abs_10": 1,
                            "churn_abs_11": 1,
                            "churn_abs_12": 1
                        }
                    }
                }
            }
        },
        "cat_curves": {
            "A": {"CAT0": 0.0, "CAT6": 0.919, "CAT12": 0.85, "CAT18": 0.0, "CAT24": 0.0, "CAT30": 0.0},
            "AC": {"CAT0": 0.0, "CAT6": 0.054, "CAT12": 0.759, "CAT18": 0.400, "CAT24": 0.0, "CAT30": 0.0},
            "C": {"CAT0": 0.0, "CAT6": 0.050, "CAT12": 0.442, "CAT18": 0.597, "CAT24": 0.278, "CAT30": 0.643, "CAT36": 0.200, "CAT42": 0.0},
            "SrC": {"CAT0": 0.0, "CAT6": 0.206, "CAT12": 0.438, "CAT18": 0.317, "CAT24": 0.211, "CAT30": 0.206, "CAT36": 0.167, "CAT42": 0.0, "CAT48": 0.0, "CAT54": 0.0, "CAT60": 0.0},
            "AM": {"CAT0": 0.0, "CAT6": 0.0, "CAT12": 0.0, "CAT18": 0.189, "CAT24": 0.197, "CAT30": 0.234, "CAT36": 0.048, "CAT42": 0.0, "CAT48": 0.0, "CAT54": 0.0, "CAT60": 0.0},
            "M": {"CAT0": 0.0, "CAT6": 0.00, "CAT12": 0.01, "CAT18": 0.02, "CAT24": 0.03, "CAT30": 0.04, "CAT36": 0.05, "CAT42": 0.06, "CAT48": 0.07, "CAT54": 0.08, "CAT60": 0.10},
            "SrM": {"CAT0": 0.0, "CAT6": 0.00, "CAT12": 0.005, "CAT18": 0.01, "CAT24": 0.015, "CAT30": 0.02, "CAT36": 0.025, "CAT42": 0.03, "CAT48": 0.04, "CAT54": 0.05, "CAT60": 0.06},
            "Pi": {"CAT0": 0.0},
            "P": {"CAT0": 0.0},
            "X": {"CAT0": 0.0},
            "OPE": {"CAT0": 0.0}
        }
    }
    
    return scenario_definition

def run_complete_scenario():
    """Run the complete scenario with absolute values."""
    
    print("🚀 Running Complete Scenario with Absolute Values")
    print("=" * 60)
    
    # Create the scenario definition
    scenario_definition = create_complete_scenario_definition()
    
    # Prepare the request
    request_data = {
        "scenario_definition": scenario_definition
    }
    
    print(f"📋 Scenario Name: {scenario_definition['name']}")
    print(f"📅 Time Range: {scenario_definition['time_range']['start_year']}-{scenario_definition['time_range']['start_month']} to {scenario_definition['time_range']['end_year']}-{scenario_definition['time_range']['end_month']}")
    print(f"🏢 Offices: {', '.join(scenario_definition['office_scope'])}")
    
    # Show absolute recruitment/churn values
    print(f"\n📊 ABSOLUTE RECRUITMENT/CHURN VALUES (2025 only):")
    print("-" * 50)
    
    baseline_input = scenario_definition['baseline_input']
    offices = baseline_input['offices']
    
    for office_name, office_data in offices.items():
        print(f"\n{office_name}:")
        roles = office_data['roles']
        
        for role_name, role_data in roles.items():
            if role_name == 'Operations':
                # Flat role
                print(f"  {role_name}:")
                print(f"    FTE: {role_data['fte']}")
                print(f"    Recruitment (Jan): {role_data['recruitment_abs_1']} people")
                print(f"    Churn (Jan): {role_data['churn_abs_1']} people")
            else:
                # Leveled role
                print(f"  {role_name}:")
                for level_name, level_data in role_data.items():
                    print(f"    {level_name}:")
                    print(f"      FTE: {level_data['fte']}")
                    print(f"      Recruitment (Jan): {level_data['recruitment_abs_1']} people")
                    print(f"      Churn (Jan): {level_data['churn_abs_1']} people")
    
    # Send request to backend
    print(f"\n🌐 Sending request to backend...")
    
    try:
        response = requests.post(
            "http://localhost:8000/scenarios/run",
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            results = response.json()
            print("✅ Simulation completed successfully!")
            
            # Analyze results
            print(f"\n📈 RESULTS SUMMARY:")
            print("-" * 40)
            
            # Check if we have years data
            years_data = results.get('results', {}).get('years', {})
            if years_data:
                print(f"Found {len(years_data)} years of data:")
                total_fte_by_year = {}
                
                for year_str, year_data in years_data.items():
                    year = int(year_str)
                    fte = year_data.get('fte', 0) if isinstance(year_data, dict) else year_data
                    total_fte_by_year[year] = fte
                    print(f"  {year}: {fte:.1f} FTE")
                
                # Summary
                years = sorted(total_fte_by_year.keys())
                if len(years) >= 2:
                    start_fte = total_fte_by_year[years[0]]
                    end_fte = total_fte_by_year[years[-1]]
                    net_change = end_fte - start_fte
                    print(f"\n📊 NET CHANGE: {net_change:+.1f} FTE ({net_change/start_fte*100:+.1f}%)")
                    
                    # Calculate expected change from recruitment/churn
                    total_recruitment = 0
                    total_churn = 0
                    
                    for office_name, office_data in offices.items():
                        roles = office_data['roles']
                        for role_name, role_data in roles.items():
                            if role_name == 'Operations':
                                total_recruitment += role_data['recruitment_abs_1'] * 12  # 12 months
                                total_churn += role_data['churn_abs_1'] * 12
                            else:
                                for level_name, level_data in role_data.items():
                                    total_recruitment += level_data['recruitment_abs_1'] * 12
                                    total_churn += level_data['churn_abs_1'] * 12
                    
                    expected_net = total_recruitment - total_churn
                    print(f"🎯 EXPECTED (from recruitment/churn): {expected_net:+.1f} FTE")
                    print(f"   Total Recruitment: {total_recruitment:.0f} people")
                    print(f"   Total Churn: {total_churn:.0f} people")
            else:
                print("❌ No years data found in results")
                print(f"Available keys: {list(results.get('results', {}).keys())}")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    run_complete_scenario() 