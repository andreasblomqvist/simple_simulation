#!/usr/bin/env python3
"""
Debug why recruitment and churn numbers are growing when they should be constant.
"""
import json
import requests

BASE_URL = "http://localhost:8000"

def debug_constant_numbers():
    """Debug the constant recruitment/churn issue."""
    
    # Get the most recent realistic scenario
    response = requests.get(f"{BASE_URL}/scenarios/list")
    scenarios = response.json().get("scenarios", [])
    recent_scenario = sorted(scenarios, key=lambda x: x.get("created_at", ""), reverse=True)[0]
    
    scenario_id = recent_scenario["id"]
    scenario_name = recent_scenario.get("name", "Unknown")
    
    print(f"🔍 Debugging Constant Numbers Issue")
    print(f"📋 Scenario: {scenario_name}")
    print(f"📋 ID: {scenario_id}")
    print("=" * 70)
    
    # Fetch results
    response = requests.get(f"{BASE_URL}/scenarios/{scenario_id}/results")
    result_data = response.json()
    results = result_data.get("results", {})
    
    # Analyze month-by-month for each year to see if monthly numbers are consistent
    for year in sorted(results["years"].keys()):
        year_data = results["years"][year]
        
        print(f"\n📅 YEAR {year} MONTH-BY-MONTH ANALYSIS")
        print("-" * 60)
        
        # Track monthly totals across all offices and levels
        monthly_totals = []
        
        for month_idx in range(12):  # 12 months
            month_recruitment = 0
            month_churn = 0
            month_fte = 0
            
            # Sum across all offices, roles, and levels for this month
            for office_name, office_data in year_data.get("offices", {}).items():
                for role_name, role_data in office_data.get("levels", {}).items():
                    for level_name, level_monthly_data in role_data.items():
                        if isinstance(level_monthly_data, list) and month_idx < len(level_monthly_data):
                            month_data = level_monthly_data[month_idx]
                            if isinstance(month_data, dict):
                                month_recruitment += month_data.get("recruitment", 0)
                                month_churn += month_data.get("churn", 0)
                                month_fte += month_data.get("fte", 0)
            
            monthly_totals.append({
                "month": month_idx + 1,
                "recruitment": month_recruitment,
                "churn": month_churn,
                "fte": month_fte
            })
        
        # Display monthly breakdown
        print(f"Month | Recruitment | Churn | Net  | FTE")
        print("-" * 45)
        for monthly in monthly_totals:
            net = monthly["recruitment"] - monthly["churn"]
            print(f"{monthly['month']:>5} | {monthly['recruitment']:>11} | {monthly['churn']:>5} | {net:>+4} | {monthly['fte']:>7,}")
        
        # Check if monthly numbers are consistent
        recruitments = [m["recruitment"] for m in monthly_totals]
        churns = [m["churn"] for m in monthly_totals]
        
        if len(set(recruitments)) == 1 and len(set(churns)) == 1:
            print(f"✅ Monthly numbers are consistent within {year}")
            print(f"   Recruitment: {recruitments[0]} per month")
            print(f"   Churn: {churns[0]} per month")
        else:
            print(f"❌ Monthly numbers vary within {year}")
            print(f"   Recruitment range: {min(recruitments)} - {max(recruitments)}")
            print(f"   Churn range: {min(churns)} - {max(churns)}")
        
        # Check FTE growth pattern
        start_fte = monthly_totals[0]["fte"]
        end_fte = monthly_totals[-1]["fte"]
        print(f"   FTE Growth: {start_fte:,} → {end_fte:,} ({end_fte - start_fte:+,})")
    
    # Now let's examine the input scenario to see what we actually sent
    print(f"\n🔍 EXAMINING INPUT SCENARIO")
    print("=" * 70)
    
    # Fetch the original scenario definition
    response = requests.get(f"{BASE_URL}/scenarios/{scenario_id}")
    if response.status_code == 200:
        scenario_def = response.json()
        baseline_input = scenario_def.get("baseline_input", {})
        
        # Check recruitment values for A-level across different months/years
        if "global" in baseline_input and "recruitment" in baseline_input["global"]:
            consultant_levels = baseline_input["global"]["recruitment"].get("Consultant", {}).get("levels", {})
            
            if "A" in consultant_levels:
                a_level_recruitment = consultant_levels["A"]["recruitment"]["values"]
                
                print(f"📊 A-level recruitment values in input:")
                sample_months = ["202401", "202406", "202412", "202501", "202506", "202512", "202601", "202606", "202612"]
                for month in sample_months:
                    if month in a_level_recruitment:
                        print(f"   {month}: {a_level_recruitment[month]}")
                
                # Check if all values are the same
                unique_values = set(a_level_recruitment.values())
                if len(unique_values) == 1:
                    print(f"✅ Input recruitment values are constant: {list(unique_values)[0]}")
                else:
                    print(f"❌ Input recruitment values vary: {unique_values}")
        
        # Check churn values similarly
        if "global" in baseline_input and "churn" in baseline_input["global"]:
            consultant_levels = baseline_input["global"]["churn"].get("Consultant", {}).get("levels", {})
            
            if "A" in consultant_levels:
                a_level_churn = consultant_levels["A"]["churn"]["values"]
                
                print(f"\n📊 A-level churn values in input:")
                for month in sample_months:
                    if month in a_level_churn:
                        print(f"   {month}: {a_level_churn[month]}")
                
                # Check if all values are the same
                unique_values = set(a_level_churn.values())
                if len(unique_values) == 1:
                    print(f"✅ Input churn values are constant: {list(unique_values)[0]}")
                else:
                    print(f"❌ Input churn values vary: {unique_values}")
    
    # Theory: The growing numbers might be due to growing FTE base affecting recruitment/churn calculations
    print(f"\n🤔 ANALYSIS:")
    print(f"If input values are constant but output is growing, possible causes:")
    print(f"1. Recruitment/churn are calculated as percentages of growing FTE base")
    print(f"2. Levers are being applied multiplicatively over time")
    print(f"3. Engine is interpreting baseline values differently than expected")
    print(f"4. There's a bug in the simulation logic")

def main():
    """Run the debugging analysis."""
    debug_constant_numbers()

if __name__ == "__main__":
    main()