#!/usr/bin/env python3
"""
Debug recruitment vs churn balance to understand the discrepancies.
"""
import json
import requests

BASE_URL = "http://localhost:8000"

def analyze_recruitment_churn_balance():
    """Analyze the recruitment vs churn balance from the recent growth scenario."""
    
    # Get the most recent scenario (should be our 3-year growth scenario)
    response = requests.get(f"{BASE_URL}/scenarios/list")
    if response.status_code != 200:
        print(f"❌ Failed to fetch scenarios: {response.status_code}")
        return
    
    scenarios = response.json().get("scenarios", [])
    recent_scenario = sorted(scenarios, key=lambda x: x.get("created_at", ""), reverse=True)[0]
    
    scenario_id = recent_scenario["id"]
    scenario_name = recent_scenario.get("name", "Unknown")
    
    print(f"🔍 Analyzing Recruitment vs Churn Balance")
    print(f"📋 Scenario: {scenario_name}")
    print(f"📋 ID: {scenario_id}")
    print("=" * 70)
    
    # Fetch results
    response = requests.get(f"{BASE_URL}/scenarios/{scenario_id}/results")
    if response.status_code != 200:
        print(f"❌ Failed to fetch results: {response.status_code}")
        return
    
    result_data = response.json()
    results = result_data.get("results", {})
    
    if "years" not in results:
        print("❌ No years data found")
        return
    
    # Analyze each year in detail
    for year in sorted(results["years"].keys()):
        year_data = results["years"][year]
        
        print(f"\n📅 YEAR {year} DETAILED ANALYSIS")
        print("-" * 50)
        
        year_totals = {
            "recruitment": 0,
            "churn": 0,
            "fte_start": 0,
            "fte_end": 0,
            "monthly_details": []
        }
        
        # Track by level for detailed analysis
        level_totals = {}
        
        # Go through each office
        for office_name, office_data in year_data.get("offices", {}).items():
            print(f"\n🏢 Office: {office_name}")
            
            office_recruitment = 0
            office_churn = 0
            
            # Go through each role and level
            for role_name, role_data in office_data.get("levels", {}).items():
                for level_name, level_monthly_data in role_data.items():
                    if level_name not in level_totals:
                        level_totals[level_name] = {"recruitment": 0, "churn": 0, "fte_start": 0, "fte_end": 0}
                    
                    if isinstance(level_monthly_data, list) and len(level_monthly_data) > 0:
                        # Get first and last month FTE for this level
                        first_month = level_monthly_data[0]
                        last_month = level_monthly_data[-1]
                        
                        level_fte_start = first_month.get("fte", 0)
                        level_fte_end = last_month.get("fte", 0)
                        
                        level_totals[level_name]["fte_start"] += level_fte_start
                        level_totals[level_name]["fte_end"] += level_fte_end
                        
                        # Sum up recruitment and churn for the whole year
                        level_recruitment = sum(month.get("recruitment", 0) for month in level_monthly_data)
                        level_churn = sum(month.get("churn", 0) for month in level_monthly_data)
                        
                        level_totals[level_name]["recruitment"] += level_recruitment
                        level_totals[level_name]["churn"] += level_churn
                        
                        office_recruitment += level_recruitment
                        office_churn += level_churn
                        
                        year_totals["recruitment"] += level_recruitment
                        year_totals["churn"] += level_churn
            
            net_office_growth = office_recruitment - office_churn
            print(f"   Recruitment: {office_recruitment:,}")
            print(f"   Churn: {office_churn:,}")
            print(f"   Net Growth: {net_office_growth:+,}")
        
        # Calculate year totals
        net_year_growth = year_totals["recruitment"] - year_totals["churn"]
        
        print(f"\n📊 YEAR {year} TOTALS:")
        print(f"   Total Recruitment: {year_totals['recruitment']:,}")
        print(f"   Total Churn: {year_totals['churn']:,}")
        print(f"   Net Growth (R-C): {net_year_growth:+,}")
        
        # Show level breakdown
        print(f"\n📈 Level Breakdown:")
        for level_name in sorted(level_totals.keys()):
            level_data = level_totals[level_name]
            level_net = level_data["recruitment"] - level_data["churn"]
            fte_change = level_data["fte_end"] - level_data["fte_start"]
            
            print(f"   {level_name:>4}: R={level_data['recruitment']:>3}, C={level_data['churn']:>3}, Net={level_net:>+4}, FTE_Δ={fte_change:>+6}")
        
        # Check if net growth matches FTE changes
        total_fte_start = sum(level_data["fte_start"] for level_data in level_totals.values())
        total_fte_end = sum(level_data["fte_end"] for level_data in level_totals.values())
        actual_fte_change = total_fte_end - total_fte_start
        
        print(f"\n🔍 Consistency Check:")
        print(f"   Net Growth (R-C): {net_year_growth:+,}")
        print(f"   Actual FTE Change: {actual_fte_change:+,}")
        print(f"   Difference: {actual_fte_change - net_year_growth:+,}")
        
        if abs(actual_fte_change - net_year_growth) > 10:  # Allow small rounding differences
            print(f"   ⚠️  Large discrepancy detected!")
        else:
            print(f"   ✅ Numbers are consistent")

def main():
    """Run the recruitment vs churn balance analysis."""
    analyze_recruitment_churn_balance()

if __name__ == "__main__":
    main()