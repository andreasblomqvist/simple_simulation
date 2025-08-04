#!/usr/bin/env python3
"""
Show recruitment and churn values for each office and level in table format.
"""
import json
import requests
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def show_office_level_table():
    """Show recruitment and churn values for each office and level."""
    
    print("📊 RECRUITMENT & CHURN VALUES BY OFFICE AND LEVEL")
    print("=" * 100)
    
    # Get the most recent scenario results
    response = requests.get(f"{BASE_URL}/scenarios/list")
    scenarios = response.json().get("scenarios", [])
    recent_scenario = sorted(scenarios, key=lambda x: x.get("created_at", ""), reverse=True)[0]
    
    scenario_id = recent_scenario["id"]
    scenario_name = recent_scenario.get("name", "Unknown")
    
    print(f"📋 Scenario: {scenario_name}")
    print(f"📋 ID: {scenario_id}")
    
    # Get results
    response = requests.get(f"{BASE_URL}/scenarios/{scenario_id}/results")
    result_data = response.json()
    results = result_data.get("results", {})
    
    if "years" not in results:
        print("❌ No years data found")
        return
    
    # Process 2024 data
    year = "2024"
    if year not in results["years"]:
        print(f"❌ No {year} data found")
        return
    
    year_data = results["years"][year]
    offices = year_data.get("offices", {})
    
    # Collect data for all offices and levels
    office_data = {}
    all_levels = set()
    
    for office_name, office_results in offices.items():
        office_data[office_name] = {}
        
        for role_name, role_data in office_results.get("levels", {}).items():
            for level_name, level_monthly_data in role_data.items():
                all_levels.add(level_name)
                
                if isinstance(level_monthly_data, list):
                    # Sum up annual totals
                    annual_recruitment = sum(month.get("recruitment", 0) for month in level_monthly_data if isinstance(month, dict))
                    annual_churn = sum(month.get("churn", 0) for month in level_monthly_data if isinstance(month, dict))
                    avg_fte = sum(month.get("fte", 0) for month in level_monthly_data if isinstance(month, dict)) / 12
                    
                    office_data[office_name][level_name] = {
                        "recruitment": annual_recruitment,
                        "churn": annual_churn,
                        "avg_fte": avg_fte
                    }
    
    # Sort levels and offices
    sorted_levels = sorted(all_levels)
    sorted_offices = sorted(office_data.keys())
    
    # Create recruitment table
    print(f"\n📈 ANNUAL RECRUITMENT BY OFFICE AND LEVEL - {year}")
    print("=" * 120)
    
    # Header
    header = f"{'Office':<12}"
    for level in sorted_levels:
        header += f"{level:>8}"
    header += f"{'Total':>10}"
    print(header)
    print("-" * 120)
    
    # Rows
    for office_name in sorted_offices:
        row = f"{office_name:<12}"
        office_total_rec = 0
        
        for level in sorted_levels:
            if level in office_data[office_name]:
                rec_value = office_data[office_name][level]["recruitment"]
                office_total_rec += rec_value
                row += f"{rec_value:>8}"
            else:
                row += f"{'0':>8}"
        
        row += f"{office_total_rec:>10}"
        print(row)
    
    # Global totals
    global_totals_rec = {}
    for level in sorted_levels:
        global_totals_rec[level] = sum(
            office_data[office].get(level, {}).get("recruitment", 0) 
            for office in sorted_offices
        )
    
    total_global_rec = sum(global_totals_rec.values())
    
    row = f"{'GLOBAL':<12}"
    for level in sorted_levels:
        row += f"{global_totals_rec[level]:>8}"
    row += f"{total_global_rec:>10}"
    print("-" * 120)
    print(row)
    
    # Create churn table
    print(f"\n📉 ANNUAL CHURN BY OFFICE AND LEVEL - {year}")
    print("=" * 120)
    
    # Header
    header = f"{'Office':<12}"
    for level in sorted_levels:
        header += f"{level:>8}"
    header += f"{'Total':>10}"
    print(header)
    print("-" * 120)
    
    # Rows
    for office_name in sorted_offices:
        row = f"{office_name:<12}"
        office_total_churn = 0
        
        for level in sorted_levels:
            if level in office_data[office_name]:
                churn_value = office_data[office_name][level]["churn"]
                office_total_churn += churn_value
                row += f"{churn_value:>8}"
            else:
                row += f"{'0':>8}"
        
        row += f"{office_total_churn:>10}"
        print(row)
    
    # Global totals
    global_totals_churn = {}
    for level in sorted_levels:
        global_totals_churn[level] = sum(
            office_data[office].get(level, {}).get("churn", 0) 
            for office in sorted_offices
        )
    
    total_global_churn = sum(global_totals_churn.values())
    
    row = f"{'GLOBAL':<12}"
    for level in sorted_levels:
        row += f"{global_totals_churn[level]:>8}"
    row += f"{total_global_churn:>10}"
    print("-" * 120)
    print(row)
    
    # Create average FTE table for context
    print(f"\n💼 AVERAGE FTE BY OFFICE AND LEVEL - {year}")
    print("=" * 120)
    
    # Header
    header = f"{'Office':<12}"
    for level in sorted_levels:
        header += f"{level:>8}"
    header += f"{'Total':>10}"
    print(header)
    print("-" * 120)
    
    # Rows
    for office_name in sorted_offices:
        row = f"{office_name:<12}"
        office_total_fte = 0
        
        for level in sorted_levels:
            if level in office_data[office_name]:
                fte_value = office_data[office_name][level]["avg_fte"]
                office_total_fte += fte_value
                row += f"{fte_value:>8.0f}"
            else:
                row += f"{'0':>8}"
        
        row += f"{office_total_fte:>10.0f}"
        print(row)
    
    # Summary statistics
    print(f"\n📊 SUMMARY STATISTICS")
    print("=" * 60)
    print(f"Total Global Recruitment: {total_global_rec:,}")
    print(f"Total Global Churn: {total_global_churn:,}")
    print(f"Net Global Growth: {total_global_rec - total_global_churn:+,}")
    
    # Highlight Oslo specifically
    if "Oslo" in office_data:
        oslo_total_rec = sum(office_data["Oslo"].get(level, {}).get("recruitment", 0) for level in sorted_levels)
        oslo_total_churn = sum(office_data["Oslo"].get(level, {}).get("churn", 0) for level in sorted_levels)
        
        print(f"\n🔍 OSLO SPECIFIC:")
        print(f"Oslo Recruitment: {oslo_total_rec}")
        print(f"Oslo Churn: {oslo_total_churn}")
        print(f"Oslo Net Growth: {oslo_total_rec - oslo_total_churn:+}")
        
        if oslo_total_churn == 0:
            print("🚨 Oslo shows 0 churn - this is the bug!")

def main():
    """Show the office level table."""
    show_office_level_table()

if __name__ == "__main__":
    main()