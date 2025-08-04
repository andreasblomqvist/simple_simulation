#!/usr/bin/env python3
"""
Test simulation with realistic recruitment and churn numbers.
"""
import json
import requests
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def create_realistic_scenario():
    """Create a scenario with realistic recruitment and churn numbers."""
    
    # Your specified numbers
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
    
    print(f"📊 Using Realistic Numbers (monthly):")
    print(f"Recruitment: {recruitment_int}")
    print(f"Churn: {churn_int}")
    
    # Create scenario structure
    scenario = {
        "name": "Realistic Recruitment & Churn Test",
        "description": "Test with realistic monthly recruitment and churn rates",
        "time_range": {
            "start_year": 2024,
            "start_month": 1,
            "end_year": 2026,
            "end_month": 12
        },
        "office_scope": ["Stockholm", "Munich"],
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
    
    return scenario, recruitment_int, churn_int

def run_realistic_scenario():
    """Run the realistic scenario."""
    
    print("🚀 Running Realistic Recruitment & Churn Scenario")
    print("=" * 70)
    
    scenario, recruitment_int, churn_int = create_realistic_scenario()
    payload = {"scenario_definition": scenario}
    
    response = requests.post(f"{BASE_URL}/scenarios/run", json=payload)
    
    if response.status_code != 200:
        print(f"❌ Simulation failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None, None, None
    
    result = response.json()
    if result.get("status") != "success":
        print(f"❌ Simulation error: {result.get('error_message', 'Unknown error')}")
        return None, None, None
    
    print(f"✅ Simulation completed in {result.get('execution_time', 0):.2f}s")
    return result, recruitment_int, churn_int

def analyze_realistic_results(result: Dict[str, Any], recruitment_int: Dict[str, int], churn_int: Dict[str, int]):
    """Analyze the realistic scenario results."""
    
    if not result or not result.get("results"):
        print("❌ No results data found")
        return
    
    scenario_id = result.get("scenario_id")
    print(f"\n📋 Scenario ID: {scenario_id}")
    
    results_data = result["results"]
    
    if "years" not in results_data:
        print("❌ No years data found")
        return
    
    print(f"\n🎯 REALISTIC SCENARIO ANALYSIS")
    print("=" * 70)
    
    # Expected annual totals (monthly * 12 months * 2 offices)
    expected_annual_recruitment = {level: value * 12 * 2 for level, value in recruitment_int.items()}
    expected_annual_churn = {level: value * 12 * 2 for level, value in churn_int.items()}
    
    total_expected_rec = sum(expected_annual_recruitment.values())
    total_expected_churn = sum(expected_annual_churn.values())
    expected_net_growth = total_expected_rec - total_expected_churn
    
    print(f"📊 Expected Annual Totals (per year, 2 offices):")
    print(f"   Total Expected Recruitment: {total_expected_rec:,}")
    print(f"   Total Expected Churn: {total_expected_churn:,}")
    print(f"   Expected Net Growth: {expected_net_growth:+,}")
    
    # Analyze each year
    for year in sorted(results_data["years"].keys()):
        year_data = results_data["years"][year]
        
        print(f"\n📅 YEAR {year} RESULTS")
        print("-" * 50)
        
        year_totals = {"recruitment": 0, "churn": 0, "progression": 0, "fte": 0}
        level_totals = {}
        
        # Collect data by level
        for office_name, office_data in year_data.get("offices", {}).items():
            for role_name, role_data in office_data.get("levels", {}).items():
                for level_name, level_monthly_data in role_data.items():
                    if level_name not in level_totals:
                        level_totals[level_name] = {"recruitment": 0, "churn": 0, "progression": 0, "fte": 0}
                    
                    if isinstance(level_monthly_data, list):
                        for month_data in level_monthly_data:
                            if isinstance(month_data, dict):
                                recruitment = month_data.get("recruitment", 0)
                                churn = month_data.get("churn", 0)
                                progression = month_data.get("promoted_people", 0)
                                fte = month_data.get("fte", 0)
                                
                                level_totals[level_name]["recruitment"] += recruitment
                                level_totals[level_name]["churn"] += churn
                                level_totals[level_name]["progression"] += progression
                                level_totals[level_name]["fte"] += fte
                                
                                year_totals["recruitment"] += recruitment
                                year_totals["churn"] += churn
                                year_totals["progression"] += progression
                                year_totals["fte"] += fte
        
        net_growth = year_totals["recruitment"] - year_totals["churn"]
        
        print(f"📊 Actual Results:")
        print(f"   Total Recruitment: {year_totals['recruitment']:,}")
        print(f"   Total Churn: {year_totals['churn']:,}")
        print(f"   Net Growth: {net_growth:+,}")
        print(f"   Total Progression: {year_totals['progression']:,}")
        print(f"   Average FTE: {year_totals['fte'] // 12:,}")  # Divide by 12 months
        
        print(f"\n📈 Comparison to Expected:")
        rec_diff = year_totals["recruitment"] - total_expected_rec
        churn_diff = year_totals["churn"] - total_expected_churn
        net_diff = net_growth - expected_net_growth
        
        print(f"   Recruitment: {rec_diff:+,} ({year_totals['recruitment']:,} vs {total_expected_rec:,})")
        print(f"   Churn: {churn_diff:+,} ({year_totals['churn']:,} vs {total_expected_churn:,})")
        print(f"   Net Growth: {net_diff:+,} ({net_growth:+,} vs {expected_net_growth:+,})")
        
        # Level-by-level comparison
        print(f"\n📊 Level-by-Level Analysis:")
        print(f"{'Level':<4} {'Expected R':<10} {'Actual R':<9} {'Expected C':<10} {'Actual C':<9} {'Net':<6}")
        print("-" * 60)
        
        for level in sorted(level_totals.keys()):
            level_data = level_totals[level]
            expected_r = expected_annual_recruitment.get(level, 0)
            expected_c = expected_annual_churn.get(level, 0)
            actual_net = level_data["recruitment"] - level_data["churn"]
            
            print(f"{level:<4} {expected_r:<10} {level_data['recruitment']:<9} {expected_c:<10} {level_data['churn']:<9} {actual_net:<+6}")
        
        # Calculate churn rates by level
        print(f"\n📊 Churn Rates by Level:")
        for level in sorted(level_totals.keys()):
            level_data = level_totals[level]
            if level_data["fte"] > 0:
                avg_fte = level_data["fte"] // 12  # Average FTE across 12 months
                churn_rate = (level_data["churn"] / avg_fte) * 100 if avg_fte > 0 else 0
                print(f"   {level}: {churn_rate:.1f}% ({level_data['churn']:,} churn / {avg_fte:,} avg FTE)")

def main():
    """Run the realistic recruitment and churn test."""
    
    result, recruitment_int, churn_int = run_realistic_scenario()
    if result:
        analyze_realistic_results(result, recruitment_int, churn_int)
    else:
        print("❌ Failed to run realistic scenario")

if __name__ == "__main__":
    main()