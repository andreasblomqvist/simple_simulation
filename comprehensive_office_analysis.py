#!/usr/bin/env python3
"""
Comprehensive office analysis - detailed tables for each office and year.
"""
import json
import requests
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def create_comprehensive_office_analysis():
    """Create comprehensive office analysis with all offices and detailed KPIs."""
    
    # Get the most recent scenario
    response = requests.get(f"{BASE_URL}/scenarios/list")
    scenarios = response.json().get("scenarios", [])
    recent_scenario = sorted(scenarios, key=lambda x: x.get("created_at", ""), reverse=True)[0]
    
    scenario_id = recent_scenario["id"]
    scenario_name = recent_scenario.get("name", "Unknown")
    
    print(f"🏢 COMPREHENSIVE OFFICE ANALYSIS")
    print(f"📋 Scenario: {scenario_name}")
    print(f"📋 ID: {scenario_id}")
    print("=" * 100)
    
    # Fetch results
    response = requests.get(f"{BASE_URL}/scenarios/{scenario_id}/results")
    result_data = response.json()
    results = result_data.get("results", {})
    
    if "years" not in results:
        print("❌ No years data found")
        return
    
    # Collect data for all years and offices
    yearly_data = {}
    all_offices = set()
    all_levels = set()
    
    for year in sorted(results["years"].keys()):
        year_data = results["years"][year]
        yearly_data[year] = {
            "offices": {},
            "totals": {
                "total_fte": 0,
                "total_revenue": 0,
                "total_cost": 0,
                "total_recruitment": 0,
                "total_churn": 0,
                "total_progression": 0
            }
        }
        
        # Process all offices
        for office_name, office_data in year_data.get("offices", {}).items():
            all_offices.add(office_name)
            
            office_metrics = {
                "office_totals": {
                    "fte": 0,
                    "revenue": 0,
                    "cost": 0,
                    "recruitment": 0,
                    "churn": 0,
                    "progression": 0
                },
                "levels": {}
            }
            
            # Process all roles and levels in this office
            for role_name, role_data in office_data.get("levels", {}).items():
                for level_name, level_monthly_data in role_data.items():
                    all_levels.add(level_name)
                    
                    if level_name not in office_metrics["levels"]:
                        office_metrics["levels"][level_name] = {
                            "fte": 0,
                            "revenue": 0,
                            "cost": 0,
                            "recruitment": 0,
                            "churn": 0,
                            "progression": 0
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
                                office_metrics["levels"][level_name]["fte"] += fte
                                office_metrics["levels"][level_name]["revenue"] += monthly_revenue
                                office_metrics["levels"][level_name]["cost"] += monthly_cost
                                office_metrics["levels"][level_name]["recruitment"] += recruitment
                                office_metrics["levels"][level_name]["churn"] += churn
                                office_metrics["levels"][level_name]["progression"] += progression
                                
                                # Accumulate office totals
                                office_metrics["office_totals"]["fte"] += fte
                                office_metrics["office_totals"]["revenue"] += monthly_revenue
                                office_metrics["office_totals"]["cost"] += monthly_cost
                                office_metrics["office_totals"]["recruitment"] += recruitment
                                office_metrics["office_totals"]["churn"] += churn
                                office_metrics["office_totals"]["progression"] += progression
            
            yearly_data[year]["offices"][office_name] = office_metrics
            
            # Add to year totals
            yearly_data[year]["totals"]["total_fte"] += office_metrics["office_totals"]["fte"]
            yearly_data[year]["totals"]["total_revenue"] += office_metrics["office_totals"]["revenue"]
            yearly_data[year]["totals"]["total_cost"] += office_metrics["office_totals"]["cost"]
            yearly_data[year]["totals"]["total_recruitment"] += office_metrics["office_totals"]["recruitment"]
            yearly_data[year]["totals"]["total_churn"] += office_metrics["office_totals"]["churn"]
            yearly_data[year]["totals"]["total_progression"] += office_metrics["office_totals"]["progression"]
    
    all_offices = sorted(all_offices)
    all_levels = sorted(all_levels)
    years = sorted(yearly_data.keys())
    
    # Global Summary Table
    print_global_summary(yearly_data, years)
    
    # Office-by-Office Annual Summary
    print_office_annual_summary(yearly_data, all_offices, years)
    
    # Detailed Office Tables for Each Year
    for year in years:
        print_detailed_office_year_table(yearly_data[year], all_offices, all_levels, year)

def print_global_summary(yearly_data: Dict, years: list):
    """Print global summary across all years."""
    print(f"\n🌍 GLOBAL SUMMARY ACROSS ALL YEARS")
    print("=" * 80)
    
    header = f"{'Metric':<25}"
    for year in years:
        header += f"{'Year ' + year:>15}"
    print(header)
    print("-" * (25 + 15 * len(years)))
    
    metrics = [
        ("Average FTE", "avg_fte"),
        ("Total Revenue ($)", "total_revenue"),
        ("Total Cost ($)", "total_cost"),
        ("Total Recruitment", "total_recruitment"),
        ("Total Churn", "total_churn"),
        ("Net Growth", "net_growth"),
        ("Total Progression", "total_progression")
    ]
    
    for metric_name, metric_key in metrics:
        row = f"{metric_name:<25}"
        for year in years:
            totals = yearly_data[year]["totals"]
            
            if metric_key == "avg_fte":
                value = totals["total_fte"] / 12  # Average across 12 months
                formatted_value = f"{value:,.0f}"
            elif metric_key == "net_growth":
                value = totals["total_recruitment"] - totals["total_churn"]
                formatted_value = f"{value:+,}"
            elif metric_key in ["total_revenue", "total_cost"]:
                key = metric_key.replace("total_", "")
                value = totals[f"total_{key}"]
                formatted_value = f"${value:,.0f}"
            else:
                key = metric_key.replace("total_", "")
                value = totals[f"total_{key}"]
                formatted_value = f"{value:,}"
            
            row += f"{formatted_value:>15}"
        print(row)

def print_office_annual_summary(yearly_data: Dict, all_offices: list, years: list):
    """Print office-by-office annual summary."""
    print(f"\n🏢 OFFICE ANNUAL SUMMARY")
    print("=" * 100)
    
    for office in all_offices:
        print(f"\n📍 {office.upper()}")
        print("-" * 60)
        
        header = f"{'Metric':<20}"
        for year in years:
            header += f"{'Year ' + year:>12}"
        print(header)
        print("-" * (20 + 12 * len(years)))
        
        office_metrics = [
            ("Avg FTE", "avg_fte"),
            ("Revenue ($)", "revenue"),
            ("Cost ($)", "cost"),
            ("Recruitment", "recruitment"),
            ("Churn", "churn"),
            ("Net Growth", "net_growth"),
            ("Progression", "progression")
        ]
        
        for metric_name, metric_key in office_metrics:
            row = f"{metric_name:<20}"
            for year in years:
                if office in yearly_data[year]["offices"]:
                    office_data = yearly_data[year]["offices"][office]["office_totals"]
                    
                    if metric_key == "avg_fte":
                        value = office_data["fte"] / 12
                        formatted_value = f"{value:,.0f}"
                    elif metric_key == "net_growth":
                        value = office_data["recruitment"] - office_data["churn"]
                        formatted_value = f"{value:+,}"
                    elif metric_key in ["revenue", "cost"]:
                        value = office_data[metric_key]
                        formatted_value = f"${value:,.0f}"
                    else:
                        value = office_data[metric_key]
                        formatted_value = f"{value:,}"
                else:
                    formatted_value = "N/A"
                
                row += f"{formatted_value:>12}"
            print(row)

def print_detailed_office_year_table(year_data: Dict, all_offices: list, all_levels: list, year: str):
    """Print detailed office x level breakdown for a specific year."""
    print(f"\n📊 DETAILED BREAKDOWN - YEAR {year}")
    print("=" * 120)
    
    # FTE Table
    print(f"\n💼 AVERAGE FTE BY OFFICE AND LEVEL - {year}")
    print("-" * 80)
    
    header = f"{'Office':<15}"
    for level in all_levels:
        header += f"{level:>8}"
    header += f"{'Total':>10}"
    print(header)
    print("-" * (15 + 8 * len(all_levels) + 10))
    
    for office in all_offices:
        if office in year_data["offices"]:
            office_data = year_data["offices"][office]
            row = f"{office:<15}"
            office_total = 0
            
            for level in all_levels:
                if level in office_data["levels"]:
                    avg_fte = office_data["levels"][level]["fte"] / 12
                    office_total += avg_fte
                    row += f"{avg_fte:>8,.0f}"
                else:
                    row += f"{'0':>8}"
            
            row += f"{office_total:>10,.0f}"
            print(row)
    
    # Recruitment Table
    print(f"\n📈 ANNUAL RECRUITMENT BY OFFICE AND LEVEL - {year}")
    print("-" * 80)
    
    header = f"{'Office':<15}"
    for level in all_levels:
        header += f"{level:>8}"
    header += f"{'Total':>10}"
    print(header)
    print("-" * (15 + 8 * len(all_levels) + 10))
    
    for office in all_offices:
        if office in year_data["offices"]:
            office_data = year_data["offices"][office]
            row = f"{office:<15}"
            office_total = 0
            
            for level in all_levels:
                if level in office_data["levels"]:
                    recruitment = office_data["levels"][level]["recruitment"]
                    office_total += recruitment
                    row += f"{recruitment:>8,}"
                else:
                    row += f"{'0':>8}"
            
            row += f"{office_total:>10,}"
            print(row)
    
    # Churn Table
    print(f"\n📉 ANNUAL CHURN BY OFFICE AND LEVEL - {year}")
    print("-" * 80)
    
    header = f"{'Office':<15}"
    for level in all_levels:
        header += f"{level:>8}"
    header += f"{'Total':>10}"
    print(header)
    print("-" * (15 + 8 * len(all_levels) + 10))
    
    for office in all_offices:
        if office in year_data["offices"]:
            office_data = year_data["offices"][office]
            row = f"{office:<15}"
            office_total = 0
            
            for level in all_levels:
                if level in office_data["levels"]:
                    churn = office_data["levels"][level]["churn"]
                    office_total += churn
                    row += f"{churn:>8,}"
                else:
                    row += f"{'0':>8}"
            
            row += f"{office_total:>10,}"
            print(row)

def main():
    """Generate comprehensive office analysis."""
    create_comprehensive_office_analysis()

if __name__ == "__main__":
    main()