#!/usr/bin/env python3
"""
Show detailed table of distributed recruitment and churn values for each office and level.
"""
import json
import requests
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def show_distributed_recruitment_churn():
    """Show the exact distributed recruitment and churn values for each office and level."""
    
    print("📊 DISTRIBUTED RECRUITMENT & CHURN VALUES BY OFFICE AND LEVEL")
    print("=" * 100)
    
    # Get the most recent scenario
    response = requests.get(f"{BASE_URL}/scenarios/list")
    scenarios = response.json().get("scenarios", [])
    recent_scenario = sorted(scenarios, key=lambda x: x.get("created_at", ""), reverse=True)[0]
    
    scenario_id = recent_scenario["id"]
    scenario_name = recent_scenario.get("name", "Unknown")
    
    print(f"📋 Scenario: {scenario_name}")
    print(f"📋 ID: {scenario_id}")
    
    # Get scenario definition to see the baseline input
    response = requests.get(f"{BASE_URL}/scenarios/{scenario_id}")
    scenario_data = response.json()
    
    baseline_input = scenario_data.get("baseline_input", {})
    global_data = baseline_input.get("global", {})
    
    print(f"\n🌍 GLOBAL BASELINE VALUES:")
    print("-" * 50)
    
    # Show global churn rates that were configured
    if "churn" in global_data and "Consultant" in global_data["churn"]:
        levels_data = global_data["churn"]["Consultant"]["levels"]
        for level, level_data in levels_data.items():
            churn_values = level_data.get("churn", {}).get("values", {})
            if churn_values:
                sample_month = list(churn_values.keys())[0]
                sample_value = churn_values[sample_month]
                print(f"  {level}: {sample_value} churn/month")
    
    # Get office configuration to understand FTE distribution
    with open('backend/config/office_configuration.json', 'r') as f:
        office_config = json.load(f)
    
    # Calculate total FTE for proportional distribution
    total_global_fte = sum(office.get('total_fte', 0) for office in office_config.values())
    print(f"\n📈 Total Global FTE: {total_global_fte:,}")
    
    # Create detailed table for each office
    offices_to_show = ["Oslo", "Helsinki", "Stockholm", "Munich"]  # Focus on key offices
    
    for office_name in offices_to_show:
        if office_name not in office_config:
            continue
            
        office_data = office_config[office_name]
        office_fte = office_data.get('total_fte', 0)
        office_proportion = office_fte / total_global_fte if total_global_fte > 0 else 0
        
        print(f"\n🏢 {office_name.upper()} (FTE: {office_fte}, Proportion: {office_proportion:.3f})")
        print("=" * 80)
        
        # Get the office's level structure
        consultant_levels = office_data.get('roles', {}).get('Consultant', {})
        
        # Calculate expected distributed values
        print(f"{'Level':<6} {'Level FTE':<10} {'Expected Monthly':<16} {'Expected Annual':<15}")
        print(f"{'':6} {'':10} {'Rec':>7} {'Churn':>7} {'Rec':>7} {'Churn':>7}")
        print("-" * 70)
        
        total_expected_rec = 0
        total_expected_churn = 0
        
        for level_name in ["A", "AC", "C", "SrC", "AM", "M", "SrM", "PiP"]:
            if level_name in consultant_levels:
                level_fte = consultant_levels[level_name].get('fte', 0)
                
                # Get global rates for this level
                global_rec_rate = 0
                global_churn_rate = 0
                
                if ("recruitment" in global_data and 
                    "Consultant" in global_data["recruitment"] and
                    "levels" in global_data["recruitment"]["Consultant"] and
                    level_name in global_data["recruitment"]["Consultant"]["levels"]):
                    
                    level_rec_data = global_data["recruitment"]["Consultant"]["levels"][level_name]
                    rec_values = level_rec_data.get("recruitment", {}).get("values", {})
                    if rec_values:
                        sample_month = list(rec_values.keys())[0]
                        global_rec_rate = rec_values[sample_month]
                
                if ("churn" in global_data and 
                    "Consultant" in global_data["churn"] and
                    "levels" in global_data["churn"]["Consultant"] and
                    level_name in global_data["churn"]["Consultant"]["levels"]):
                    
                    level_churn_data = global_data["churn"]["Consultant"]["levels"][level_name]
                    churn_values = level_churn_data.get("churn", {}).get("values", {})
                    if churn_values:
                        sample_month = list(churn_values.keys())[0]
                        global_churn_rate = churn_values[sample_month]
                
                # Calculate expected distributed values based on office proportion
                expected_monthly_rec = global_rec_rate * office_proportion
                expected_monthly_churn = global_churn_rate * office_proportion
                
                total_expected_rec += expected_monthly_rec
                total_expected_churn += expected_monthly_churn
                
                print(f"{level_name:<6} {level_fte:<10} {expected_monthly_rec:>7.1f} {expected_monthly_churn:>7.1f} {expected_monthly_rec*12:>7.0f} {expected_monthly_churn*12:>7.0f}")
        
        print("-" * 70)
        print(f"{'TOTAL':<6} {office_fte:<10} {total_expected_rec:>7.1f} {total_expected_churn:>7.1f} {total_expected_rec*12:>7.0f} {total_expected_churn*12:>7.0f}")
    
    # Now get the actual simulation results to compare
    print(f"\n📊 ACTUAL SIMULATION RESULTS (for comparison)")
    print("=" * 80)
    
    response = requests.get(f"{BASE_URL}/scenarios/{scenario_id}/results")
    result_data = response.json()
    results = result_data.get("results", {})
    
    if "years" in results and "2024" in results["years"]:
        year_data = results["years"]["2024"]
        
        print(f"{'Office':<12} {'Actual Annual':<15} {'Expected Annual':<16} {'Match?'}")
        print(f"{'':12} {'Rec':>7} {'Churn':>7} {'Rec':>7} {'Churn':>7}")
        print("-" * 60)
        
        for office_name in offices_to_show:
            if office_name in year_data.get("offices", {}):
                office_results = year_data["offices"][office_name]
                
                # Calculate actual totals
                actual_total_rec = 0
                actual_total_churn = 0
                
                for role_name, role_data in office_results.get("levels", {}).items():
                    for level_name, level_monthly_data in role_data.items():
                        if isinstance(level_monthly_data, list):
                            level_total_rec = sum(month.get("recruitment", 0) for month in level_monthly_data if isinstance(month, dict))
                            level_total_churn = sum(month.get("churn", 0) for month in level_monthly_data if isinstance(month, dict))
                            
                            actual_total_rec += level_total_rec
                            actual_total_churn += level_total_churn
                
                # Calculate expected totals for this office
                office_data = office_config[office_name]
                office_fte = office_data.get('total_fte', 0)
                office_proportion = office_fte / total_global_fte if total_global_fte > 0 else 0
                
                expected_annual_rec = 0
                expected_annual_churn = 0
                
                # Sum up all global rates
                if "churn" in global_data and "Consultant" in global_data["churn"]:
                    for level_name, level_data in global_data["churn"]["Consultant"]["levels"].items():
                        churn_values = level_data.get("churn", {}).get("values", {})
                        if churn_values:
                            sample_month = list(churn_values.keys())[0]
                            global_churn_rate = churn_values[sample_month]
                            expected_annual_churn += global_churn_rate * office_proportion * 12
                
                if "recruitment" in global_data and "Consultant" in global_data["recruitment"]:
                    for level_name, level_data in global_data["recruitment"]["Consultant"]["levels"].items():
                        rec_values = level_data.get("recruitment", {}).get("values", {})
                        if rec_values:
                            sample_month = list(rec_values.keys())[0]
                            global_rec_rate = rec_values[sample_month]
                            expected_annual_rec += global_rec_rate * office_proportion * 12
                
                # Check if they match (within rounding)
                rec_match = "✅" if abs(actual_total_rec - expected_annual_rec) <= 1 else "❌"
                churn_match = "✅" if abs(actual_total_churn - expected_annual_churn) <= 1 else "❌"
                
                print(f"{office_name:<12} {actual_total_rec:>7} {actual_total_churn:>7} {expected_annual_rec:>7.0f} {expected_annual_churn:>7.0f} {rec_match}{churn_match}")
                
                if office_name == "Oslo" and actual_total_churn == 0:
                    print(f"              🚨 Oslo still showing 0 churn - this is the bug!")

def main():
    """Show distributed recruitment and churn values."""
    show_distributed_recruitment_churn()

if __name__ == "__main__":
    main()