#!/usr/bin/env python3
"""
Test simulation with all offices using realistic recruitment and churn numbers.
"""
import json
import requests
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def create_all_offices_scenario():
    """Create a scenario with realistic recruitment and churn numbers for ALL offices."""
    
    # Your specified numbers (monthly)
    recruitment_monthly = {
        "A": 20.4,
        "AC": 8.0,
        "C": 4.0,
        "SrC": 1.0,
        "AM": 0.3,
        "M": 0.0,
        "SrM": 0.0,
        "Pi": 0.0,
        "P": 0.0
    }
    
    churn_monthly = {
        "A": 2.3,
        "AC": 4.0,
        "C": 7.0,
        "SrC": 6.41,
        "AM": 5.25,
        "M": 1.25,
        "SrM": 0.4,
        "Pi": 0.0,
        "P": 0.0
    }
    
    # Convert to integers for the simulation (round to nearest)
    recruitment_int = {level: round(value) for level, value in recruitment_monthly.items()}
    churn_int = {level: round(value) for level, value in churn_monthly.items()}
    
    print(f"📊 Using Realistic Numbers (monthly) for ALL OFFICES:")
    print(f"Recruitment: {recruitment_int}")
    print(f"Churn: {churn_int}")
    
    # Get all available offices from the system
    response = requests.get(f"{BASE_URL}/config")
    if response.status_code == 200:
        config_data = response.json()
        all_offices = list(config_data.keys())
        print(f"🏢 Including offices: {all_offices}")
    else:
        # Fallback to known offices
        all_offices = ["Stockholm", "Munich", "Hamburg", "Helsinki", "Oslo", "Berlin", 
                      "Copenhagen", "Zurich", "Frankfurt", "Amsterdam", "Cologne", "Toronto"]
        print(f"🏢 Using fallback office list: {all_offices}")
    
    # Create scenario structure
    scenario = {
        "name": "All Offices - Realistic Recruitment & Churn",
        "description": "Test with realistic monthly recruitment and churn rates across all offices",
        "time_range": {
            "start_year": 2024,
            "start_month": 1,
            "end_year": 2026,
            "end_month": 12
        },
        "office_scope": all_offices,  # Include ALL offices
        "baseline_input": {
            "global": {
                "recruitment": {
                    "Consultant": {
                        "levels": {}
                    }
                },
                "churn": {
                    "Consultant": {
                        "levels": {}
                    }
                }
            }
        },
        "levers": {
            "recruitment": {"A": 1.0, "AC": 1.0, "C": 1.0, "SrC": 1.0, "AM": 1.0, "M": 1.0, "SrM": 1.0, "Pi": 1.0, "P": 1.0},
            "churn": {"A": 1.0, "AC": 1.0, "C": 1.0, "SrC": 1.0, "AM": 1.0, "M": 1.0, "SrM": 1.0, "Pi": 1.0, "P": 1.0},
            "progression": {"A": 1.0, "AC": 1.0, "C": 1.0, "SrC": 1.0, "AM": 1.0, "M": 1.0, "SrM": 1.0, "Pi": 1.0, "P": 1.0}
        },
        "progression_config": None,
        "cat_curves": None
    }
    
    # Build the baseline input for all levels and months
    all_levels = ["A", "AC", "C", "SrC", "AM", "M", "SrM", "Pi", "P"]
    
    for level in all_levels:
        rec_value = recruitment_int.get(level, 0)
        churn_value = churn_int.get(level, 0)
        
        # Create monthly values for 3 years
        monthly_rec_values = {}
        monthly_churn_values = {}
        
        for year in [2024, 2025, 2026]:
            for month in range(1, 13):
                month_key = f"{year}{month:02d}"
                monthly_rec_values[month_key] = rec_value
                monthly_churn_values[month_key] = churn_value
        
        scenario["baseline_input"]["global"]["recruitment"]["Consultant"]["levels"][level] = {
            "recruitment": {"values": monthly_rec_values},
            "churn": {"values": monthly_churn_values}
        }
        
        scenario["baseline_input"]["global"]["churn"]["Consultant"]["levels"][level] = {
            "recruitment": {"values": monthly_rec_values},
            "churn": {"values": monthly_churn_values}
        }
    
    return scenario, recruitment_int, churn_int, all_offices

def run_all_offices_scenario():
    """Run the all offices scenario."""
    
    print("🚀 Running All Offices Realistic Recruitment & Churn Scenario")
    print("=" * 80)
    
    scenario, recruitment_int, churn_int, all_offices = create_all_offices_scenario()
    payload = {"scenario_definition": scenario}
    
    response = requests.post(f"{BASE_URL}/scenarios/run", json=payload)
    
    if response.status_code != 200:
        print(f"❌ Simulation failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None, None, None, None
    
    result = response.json()
    if result.get("status") != "success":
        print(f"❌ Simulation error: {result.get('error_message', 'Unknown error')}")
        return None, None, None, None
    
    print(f"✅ Simulation completed in {result.get('execution_time', 0):.2f}s")
    print(f"📋 Scenario ID: {result.get('scenario_id')}")
    
    return result, recruitment_int, churn_int, all_offices

def main():
    """Run the all offices realistic recruitment and churn test."""
    
    result, recruitment_int, churn_int, all_offices = run_all_offices_scenario()
    if result:
        print(f"\n🎉 Simulation successful! Use comprehensive_office_analysis.py to see detailed results.")
        print(f"Expected monthly totals across {len(all_offices)} offices:")
        total_monthly_rec = sum(recruitment_int.values()) * len(all_offices)
        total_monthly_churn = sum(churn_int.values()) * len(all_offices)
        print(f"   Monthly Recruitment: {total_monthly_rec:,}")
        print(f"   Monthly Churn: {total_monthly_churn:,}")
        print(f"   Annual Recruitment: {total_monthly_rec * 12:,}")
        print(f"   Annual Churn: {total_monthly_churn * 12:,}")
        print(f"   Annual Net Growth: {(total_monthly_rec - total_monthly_churn) * 12:+,}")
    else:
        print("❌ Failed to run all offices scenario")

if __name__ == "__main__":
    main()