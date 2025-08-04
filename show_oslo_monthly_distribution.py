#!/usr/bin/env python3
"""
Show the exact monthly recruitment and churn distribution for Oslo by level.
"""
import json
import requests
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def show_oslo_monthly_distribution():
    """Show Oslo's monthly recruitment and churn values by level."""
    
    print("📊 OSLO MONTHLY RECRUITMENT & CHURN DISTRIBUTION BY LEVEL")
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
    
    if "years" not in results or "2024" not in results["years"]:
        print("❌ No 2024 data found")
        return
    
    year_data = results["years"]["2024"]
    
    if "Oslo" not in year_data.get("offices", {}):
        print("❌ Oslo not found in results")
        return
    
    oslo_data = year_data["offices"]["Oslo"]
    
    # Collect Oslo data by level and month
    oslo_levels = {}
    
    for role_name, role_data in oslo_data.get("levels", {}).items():
        for level_name, level_monthly_data in role_data.items():
            if isinstance(level_monthly_data, list):
                oslo_levels[level_name] = level_monthly_data
    
    if not oslo_levels:
        print("❌ No level data found for Oslo")
        return
    
    # Sort levels
    sorted_levels = sorted(oslo_levels.keys())
    
    # Create recruitment table
    print(f"\n📈 OSLO MONTHLY RECRUITMENT BY LEVEL - 2024")
    print("=" * 120)
    
    # Header
    header = f"{'Level':<6}"
    for month in range(1, 13):
        header += f"{'M' + str(month):>5}"
    header += f"{'Total':>7}"
    print(header)
    print("-" * 120)
    
    # Rows for each level
    for level_name in sorted_levels:
        level_data = oslo_levels[level_name]
        row = f"{level_name:<6}"
        total_recruitment = 0
        
        for month_idx in range(12):
            if month_idx < len(level_data) and isinstance(level_data[month_idx], dict):
                recruitment = level_data[month_idx].get("recruitment", 0)
                total_recruitment += recruitment
                row += f"{recruitment:>5}"
            else:
                row += f"{'0':>5}"
        
        row += f"{total_recruitment:>7}"
        print(row)
    
    # Global totals
    global_monthly_rec = [0] * 12
    global_total_rec = 0
    
    for level_name in sorted_levels:
        level_data = oslo_levels[level_name]
        for month_idx in range(12):
            if month_idx < len(level_data) and isinstance(level_data[month_idx], dict):
                recruitment = level_data[month_idx].get("recruitment", 0)
                global_monthly_rec[month_idx] += recruitment
                global_total_rec += recruitment
    
    row = f"{'TOTAL':<6}"
    for month_total in global_monthly_rec:
        row += f"{month_total:>5}"
    row += f"{global_total_rec:>7}"
    print("-" * 120)
    print(row)
    
    # Create churn table
    print(f"\n📉 OSLO MONTHLY CHURN BY LEVEL - 2024")
    print("=" * 120)
    
    # Header
    header = f"{'Level':<6}"
    for month in range(1, 13):
        header += f"{'M' + str(month):>5}"
    header += f"{'Total':>7}"
    print(header)
    print("-" * 120)
    
    # Rows for each level
    for level_name in sorted_levels:
        level_data = oslo_levels[level_name]
        row = f"{level_name:<6}"
        total_churn = 0
        
        for month_idx in range(12):
            if month_idx < len(level_data) and isinstance(level_data[month_idx], dict):
                churn = level_data[month_idx].get("churn", 0)
                total_churn += churn
                row += f"{churn:>5}"
            else:
                row += f"{'0':>5}"
        
        row += f"{total_churn:>7}"
        print(row)
    
    # Global totals
    global_monthly_churn = [0] * 12
    global_total_churn = 0
    
    for level_name in sorted_levels:
        level_data = oslo_levels[level_name]
        for month_idx in range(12):
            if month_idx < len(level_data) and isinstance(level_data[month_idx], dict):
                churn = level_data[month_idx].get("churn", 0)
                global_monthly_churn[month_idx] += churn
                global_total_churn += churn
    
    row = f"{'TOTAL':<6}"
    for month_total in global_monthly_churn:
        row += f"{month_total:>5}"
    row += f"{global_total_churn:>7}"
    print("-" * 120)
    print(row)
    
    # Create FTE table for context
    print(f"\n💼 OSLO MONTHLY FTE BY LEVEL - 2024")
    print("=" * 120)
    
    # Header
    header = f"{'Level':<6}"
    for month in range(1, 13):
        header += f"{'M' + str(month):>5}"
    header += f"{'Avg':>7}"
    print(header)
    print("-" * 120)
    
    # Rows for each level
    for level_name in sorted_levels:
        level_data = oslo_levels[level_name]
        row = f"{level_name:<6}"
        total_fte = 0
        
        for month_idx in range(12):
            if month_idx < len(level_data) and isinstance(level_data[month_idx], dict):
                fte = level_data[month_idx].get("fte", 0)
                total_fte += fte
                row += f"{fte:>5.0f}"
            else:
                row += f"{'0':>5}"
        
        avg_fte = total_fte / 12
        row += f"{avg_fte:>7.0f}"
        print(row)
    
    print(f"\n🔍 OSLO ANALYSIS:")
    print("-" * 50)
    print(f"Total Annual Recruitment: {global_total_rec}")
    print(f"Total Annual Churn: {global_total_churn}")
    print(f"Net Growth: {global_total_rec - global_total_churn:+}")
    
    # Check which levels have workforce but no churn
    print(f"\nLevels with FTE but 0 churn:")
    for level_name in sorted_levels:
        level_data = oslo_levels[level_name]
        if level_data:
            avg_fte = sum(month.get("fte", 0) for month in level_data if isinstance(month, dict)) / 12
            total_churn = sum(month.get("churn", 0) for month in level_data if isinstance(month, dict))
            
            if avg_fte > 0 and total_churn == 0:
                print(f"  {level_name}: {avg_fte:.0f} avg FTE, 0 churn ❌")
    
    print(f"\n💡 Expected vs Actual:")
    print("Based on previous analysis, Oslo should get ~24 annual recruitment and ~18 annual churn")
    print(f"Actual: {global_total_rec} recruitment, {global_total_churn} churn")
    
    if global_total_churn == 0:
        print("🚨 Oslo gets 0 churn across ALL levels and ALL months - this confirms the systematic bug!")

def main():
    """Show Oslo's monthly distribution."""
    show_oslo_monthly_distribution()

if __name__ == "__main__":
    main()