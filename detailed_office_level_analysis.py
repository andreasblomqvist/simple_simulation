#!/usr/bin/env python3
"""
Detailed office and level analysis with comprehensive KPI tables.
"""
import json
import requests
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def create_detailed_office_level_analysis():
    """Create detailed analysis for each office, level, and year with comprehensive KPIs."""
    
    # Get the most recent scenario
    response = requests.get(f"{BASE_URL}/scenarios/list")
    scenarios = response.json().get("scenarios", [])
    recent_scenario = sorted(scenarios, key=lambda x: x.get("created_at", ""), reverse=True)[0]
    
    scenario_id = recent_scenario["id"]
    scenario_name = recent_scenario.get("name", "Unknown")
    
    print(f"🏢 DETAILED OFFICE & LEVEL ANALYSIS")
    print(f"📋 Scenario: {scenario_name}")
    print(f"📋 ID: {scenario_id}")
    print("=" * 120)
    
    # Fetch results
    response = requests.get(f"{BASE_URL}/scenarios/{scenario_id}/results")
    result_data = response.json()
    results = result_data.get("results", {})
    
    if "years" not in results:
        print("❌ No years data found")
        return
    
    # Collect comprehensive data
    comprehensive_data = {}
    all_offices = set()
    all_levels = set()
    
    for year in sorted(results["years"].keys()):
        year_data = results["years"][year]
        comprehensive_data[year] = {"offices": {}}
        
        # Process all offices
        for office_name, office_data in year_data.get("offices", {}).items():
            all_offices.add(office_name)
            comprehensive_data[year]["offices"][office_name] = {
                "levels": {},
                "office_totals": {
                    "avg_fte": 0, "total_revenue": 0, "total_cost": 0,
                    "total_recruitment": 0, "total_churn": 0, "total_progression": 0,
                    "profit": 0, "profit_margin": 0, "churn_rate": 0,
                    "revenue_per_fte": 0, "cost_per_fte": 0
                }
            }
            
            office_totals = comprehensive_data[year]["offices"][office_name]["office_totals"]
            
            # Process all roles and levels
            for role_name, role_data in office_data.get("levels", {}).items():
                for level_name, level_monthly_data in role_data.items():
                    all_levels.add(level_name)
                    
                    level_metrics = {
                        "avg_fte": 0, "total_revenue": 0, "total_cost": 0,
                        "total_recruitment": 0, "total_churn": 0, "total_progression": 0,
                        "profit": 0, "profit_margin": 0, "churn_rate": 0,
                        "revenue_per_fte": 0, "cost_per_fte": 0
                    }
                    
                    if isinstance(level_monthly_data, list):
                        for month_data in level_monthly_data:
                            if isinstance(month_data, dict):
                                fte = month_data.get("fte", 0)
                                price = month_data.get("price", 0)
                                salary = month_data.get("salary", 0)
                                recruitment = month_data.get("recruitment", 0)
                                churn = month_data.get("churn", 0)
                                progression = month_data.get("promoted_people", 0)
                                
                                monthly_revenue = fte * price
                                monthly_cost = fte * salary
                                
                                # Accumulate level metrics
                                level_metrics["avg_fte"] += fte
                                level_metrics["total_revenue"] += monthly_revenue
                                level_metrics["total_cost"] += monthly_cost
                                level_metrics["total_recruitment"] += recruitment
                                level_metrics["total_churn"] += churn
                                level_metrics["total_progression"] += progression
                    
                    # Calculate derived metrics for level
                    level_metrics["avg_fte"] = level_metrics["avg_fte"] / 12  # Average across 12 months
                    level_metrics["profit"] = level_metrics["total_revenue"] - level_metrics["total_cost"]
                    level_metrics["profit_margin"] = (level_metrics["profit"] / level_metrics["total_revenue"] * 100) if level_metrics["total_revenue"] > 0 else 0
                    level_metrics["churn_rate"] = (level_metrics["total_churn"] / level_metrics["avg_fte"] * 100) if level_metrics["avg_fte"] > 0 else 0
                    level_metrics["revenue_per_fte"] = level_metrics["total_revenue"] / level_metrics["avg_fte"] if level_metrics["avg_fte"] > 0 else 0
                    level_metrics["cost_per_fte"] = level_metrics["total_cost"] / level_metrics["avg_fte"] if level_metrics["avg_fte"] > 0 else 0
                    
                    comprehensive_data[year]["offices"][office_name]["levels"][level_name] = level_metrics
                    
                    # Add to office totals
                    for key in ["avg_fte", "total_revenue", "total_cost", "total_recruitment", "total_churn", "total_progression"]:
                        office_totals[key] += level_metrics[key]
            
            # Calculate derived office metrics
            office_totals["profit"] = office_totals["total_revenue"] - office_totals["total_cost"]
            office_totals["profit_margin"] = (office_totals["profit"] / office_totals["total_revenue"] * 100) if office_totals["total_revenue"] > 0 else 0
            office_totals["churn_rate"] = (office_totals["total_churn"] / office_totals["avg_fte"] * 100) if office_totals["avg_fte"] > 0 else 0
            office_totals["revenue_per_fte"] = office_totals["total_revenue"] / office_totals["avg_fte"] if office_totals["avg_fte"] > 0 else 0
            office_totals["cost_per_fte"] = office_totals["total_cost"] / office_totals["avg_fte"] if office_totals["avg_fte"] > 0 else 0
    
    all_offices = sorted(all_offices)
    all_levels = sorted(all_levels)
    years = sorted(comprehensive_data.keys())
    
    # Generate detailed tables
    print_detailed_office_level_tables(comprehensive_data, all_offices, all_levels, years)
    print_comprehensive_kpi_tables(comprehensive_data, all_offices, all_levels, years)

def print_detailed_office_level_tables(data: Dict, all_offices: list, all_levels: list, years: list):
    """Print detailed office and level tables for each year."""
    
    for year in years:
        print(f"\n📊 DETAILED OFFICE & LEVEL BREAKDOWN - YEAR {year}")
        print("=" * 120)
        
        # Office Summary Table
        print(f"\n🏢 OFFICE SUMMARY - {year}")
        print("-" * 100)
        header = f"{'Office':<15}{'Avg FTE':<10}{'Revenue ($)':<15}{'Cost ($)':<15}{'Profit ($)':<15}{'Recruitment':<12}{'Churn':<8}{'Net':<6}"
        print(header)
        print("-" * 100)
        
        for office in all_offices:
            if office in data[year]["offices"]:
                totals = data[year]["offices"][office]["office_totals"]
                net_growth = totals["total_recruitment"] - totals["total_churn"]
                
                row = (f"{office:<15}"
                      f"{totals['avg_fte']:<10,.0f}"
                      f"${totals['total_revenue']:<14,.0f}"
                      f"${totals['total_cost']:<14,.0f}"
                      f"${totals['profit']:<14,.0f}"
                      f"{totals['total_recruitment']:<12,}"
                      f"{totals['total_churn']:<8,}"
                      f"{net_growth:<+6,}")
                print(row)
        
        # Detailed Level Breakdown for each office
        for office in all_offices:
            if office in data[year]["offices"] and data[year]["offices"][office]["levels"]:
                print(f"\n📋 {office.upper()} - LEVEL DETAILS - {year}")
                print("-" * 110)
                header = f"{'Level':<8}{'Avg FTE':<10}{'Revenue ($)':<15}{'Cost ($)':<15}{'Profit ($)':<15}{'Rec':<6}{'Churn':<8}{'Prog':<6}{'Churn%':<8}"
                print(header)
                print("-" * 110)
                
                for level in all_levels:
                    if level in data[year]["offices"][office]["levels"]:
                        level_data = data[year]["offices"][office]["levels"][level]
                        
                        row = (f"{level:<8}"
                              f"{level_data['avg_fte']:<10,.0f}"
                              f"${level_data['total_revenue']:<14,.0f}"
                              f"${level_data['total_cost']:<14,.0f}"
                              f"${level_data['profit']:<14,.0f}"
                              f"{level_data['total_recruitment']:<6,}"
                              f"{level_data['total_churn']:<8,}"
                              f"{level_data['total_progression']:<6,}"
                              f"{level_data['churn_rate']:<8.1f}%")
                        print(row)

def print_comprehensive_kpi_tables(data: Dict, all_offices: list, all_levels: list, years: list):
    """Print comprehensive KPI tables."""
    
    print(f"\n💰 COMPREHENSIVE KPI ANALYSIS")
    print("=" * 120)
    
    # Global KPI Summary
    print(f"\n🌍 GLOBAL KPI SUMMARY")
    print("-" * 100)
    header = f"{'Year':<8}{'Avg FTE':<12}{'Revenue ($)':<15}{'Cost ($)':<15}{'Profit ($)':<15}{'Margin%':<10}{'Churn%':<10}{'Net Growth':<12}"
    print(header)
    print("-" * 100)
    
    for year in years:
        global_totals = {"avg_fte": 0, "total_revenue": 0, "total_cost": 0, "total_recruitment": 0, "total_churn": 0}
        
        for office in all_offices:
            if office in data[year]["offices"]:
                office_totals = data[year]["offices"][office]["office_totals"]
                for key in global_totals:
                    global_totals[key] += office_totals[key]
        
        global_profit = global_totals["total_revenue"] - global_totals["total_cost"]
        global_margin = (global_profit / global_totals["total_revenue"] * 100) if global_totals["total_revenue"] > 0 else 0
        global_churn_rate = (global_totals["total_churn"] / global_totals["avg_fte"] * 100) if global_totals["avg_fte"] > 0 else 0
        net_growth = global_totals["total_recruitment"] - global_totals["total_churn"]
        
        row = (f"{year:<8}"
              f"{global_totals['avg_fte']:<12,.0f}"
              f"${global_totals['total_revenue']:<14,.0f}"
              f"${global_totals['total_cost']:<14,.0f}"
              f"${global_profit:<14,.0f}"
              f"{global_margin:<10.1f}%"
              f"{global_churn_rate:<10.1f}%"
              f"{net_growth:<+12,}")
        print(row)
    
    # Office KPI Comparison Table
    print(f"\n🏢 OFFICE KPI COMPARISON - ALL YEARS")
    print("-" * 150)
    
    for metric_name, metric_key in [("Average FTE", "avg_fte"), ("Profit Margin %", "profit_margin"), 
                                   ("Churn Rate %", "churn_rate"), ("Revenue per FTE", "revenue_per_fte")]:
        print(f"\n📊 {metric_name.upper()}")
        print("-" * 80)
        
        header = f"{'Office':<15}"
        for year in years:
            header += f"{'Year ' + year:<12}"
        print(header)
        print("-" * (15 + 12 * len(years)))
        
        for office in all_offices:
            row = f"{office:<15}"
            for year in years:
                if office in data[year]["offices"]:
                    value = data[year]["offices"][office]["office_totals"][metric_key]
                    if metric_key in ["profit_margin", "churn_rate"]:
                        formatted_value = f"{value:.1f}%"
                    elif metric_key == "revenue_per_fte":
                        formatted_value = f"${value:,.0f}"
                    else:
                        formatted_value = f"{value:,.0f}"
                else:
                    formatted_value = "N/A"
                row += f"{formatted_value:<12}"
            print(row)
    
    # Level Performance Analysis
    print(f"\n📊 LEVEL PERFORMANCE ANALYSIS")
    print("-" * 120)
    
    for year in years:
        print(f"\n📈 LEVEL PERFORMANCE - {year}")
        print("-" * 90)
        
        # Aggregate level data across all offices
        level_aggregates = {}
        for office in all_offices:
            if office in data[year]["offices"]:
                for level, level_data in data[year]["offices"][office]["levels"].items():
                    if level not in level_aggregates:
                        level_aggregates[level] = {"avg_fte": 0, "total_revenue": 0, "total_cost": 0, 
                                                 "total_recruitment": 0, "total_churn": 0, "total_progression": 0}
                    
                    for key in level_aggregates[level]:
                        level_aggregates[level][key] += level_data[key]
        
        header = f"{'Level':<8}{'Avg FTE':<12}{'Revenue ($)':<15}{'Recruitment':<12}{'Churn':<8}{'Churn%':<10}{'Rev/FTE':<12}"
        print(header)
        print("-" * 90)
        
        for level in all_levels:
            if level in level_aggregates:
                level_data = level_aggregates[level]
                churn_rate = (level_data["total_churn"] / level_data["avg_fte"] * 100) if level_data["avg_fte"] > 0 else 0
                rev_per_fte = level_data["total_revenue"] / level_data["avg_fte"] if level_data["avg_fte"] > 0 else 0
                
                row = (f"{level:<8}"
                      f"{level_data['avg_fte']:<12,.0f}"
                      f"${level_data['total_revenue']:<14,.0f}"
                      f"{level_data['total_recruitment']:<12,}"
                      f"{level_data['total_churn']:<8,}"
                      f"{churn_rate:<10.1f}%"
                      f"${rev_per_fte:<11,.0f}")
                print(row)

def main():
    """Generate detailed office and level analysis."""
    create_detailed_office_level_analysis()

if __name__ == "__main__":
    main()