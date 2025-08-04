#!/usr/bin/env python3
"""
Generate detailed KPI tables and FTE breakdowns for the realistic scenario.
"""
import json
import requests
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def create_kpi_tables():
    """Create detailed KPI tables and FTE breakdowns."""
    
    # Get the most recent realistic scenario
    response = requests.get(f"{BASE_URL}/scenarios/list")
    scenarios = response.json().get("scenarios", [])
    recent_scenario = sorted(scenarios, key=lambda x: x.get("created_at", ""), reverse=True)[0]
    
    scenario_id = recent_scenario["id"]
    scenario_name = recent_scenario.get("name", "Unknown")
    
    print(f"📊 DETAILED KPI ANALYSIS")
    print(f"📋 Scenario: {scenario_name}")
    print(f"📋 ID: {scenario_id}")
    print("=" * 80)
    
    # Fetch results
    response = requests.get(f"{BASE_URL}/scenarios/{scenario_id}/results")
    result_data = response.json()
    results = result_data.get("results", {})
    
    if "years" not in results:
        print("❌ No years data found")
        return
    
    # Collect data for all years
    yearly_data = {}
    
    for year in sorted(results["years"].keys()):
        year_data = results["years"][year]
        yearly_data[year] = {
            "global_kpis": {
                "total_fte": 0,
                "total_revenue": 0,
                "total_cost": 0,
                "total_recruitment": 0,
                "total_churn": 0,
                "total_progression": 0,
                "months_analyzed": 0,
                "average_utr": 0,
                "utr_values": []
            },
            "office_fte": {},
            "level_fte": {},
            "office_level_fte": {}
        }
        
        # Process all offices and levels
        for office_name, office_data in year_data.get("offices", {}).items():
            yearly_data[year]["office_fte"][office_name] = 0
            yearly_data[year]["office_level_fte"][office_name] = {}
            
            for role_name, role_data in office_data.get("levels", {}).items():
                for level_name, level_monthly_data in role_data.items():
                    if level_name not in yearly_data[year]["level_fte"]:
                        yearly_data[year]["level_fte"][level_name] = 0
                    
                    yearly_data[year]["office_level_fte"][office_name][level_name] = 0
                    
                    if isinstance(level_monthly_data, list):
                        for month_data in level_monthly_data:
                            if isinstance(month_data, dict):
                                fte = month_data.get("fte", 0)
                                price = month_data.get("price", 0)
                                salary = month_data.get("salary", 0)
                                recruitment = month_data.get("recruitment", 0)
                                churn = month_data.get("churn", 0)
                                progression = month_data.get("promoted_people", 0)
                                utr = month_data.get("utr", 0)
                                
                                monthly_revenue = fte * price
                                monthly_cost = fte * salary
                                
                                # Accumulate global KPIs
                                yearly_data[year]["global_kpis"]["total_fte"] += fte
                                yearly_data[year]["global_kpis"]["total_revenue"] += monthly_revenue
                                yearly_data[year]["global_kpis"]["total_cost"] += monthly_cost
                                yearly_data[year]["global_kpis"]["total_recruitment"] += recruitment
                                yearly_data[year]["global_kpis"]["total_churn"] += churn
                                yearly_data[year]["global_kpis"]["total_progression"] += progression
                                yearly_data[year]["global_kpis"]["months_analyzed"] += 1
                                
                                if utr > 0:
                                    yearly_data[year]["global_kpis"]["utr_values"].append(utr)
                                
                                # Accumulate FTE data
                                yearly_data[year]["office_fte"][office_name] += fte
                                yearly_data[year]["level_fte"][level_name] += fte
                                yearly_data[year]["office_level_fte"][office_name][level_name] += fte
        
        # Calculate averages
        if yearly_data[year]["global_kpis"]["utr_values"]:
            yearly_data[year]["global_kpis"]["average_utr"] = sum(yearly_data[year]["global_kpis"]["utr_values"]) / len(yearly_data[year]["global_kpis"]["utr_values"])
    
    # Generate Global KPIs Table
    print_global_kpis_table(yearly_data)
    
    # Generate FTE Tables
    print_fte_tables(yearly_data)

def print_global_kpis_table(yearly_data: Dict[str, Any]):
    """Print global KPIs table for all years."""
    
    print(f"\n📊 GLOBAL KPIs BY YEAR")
    print("=" * 80)
    
    # Table header
    years = sorted(yearly_data.keys())
    header = f"{'Metric':<25}"
    for year in years:
        header += f"{'Year ' + year:>15}"
    print(header)
    print("-" * (25 + 15 * len(years)))
    
    # Calculate derived metrics for each year
    derived_metrics = {}
    for year in years:
        kpis = yearly_data[year]["global_kpis"]
        total_profit = kpis["total_revenue"] - kpis["total_cost"]
        profit_margin = (total_profit / kpis["total_revenue"]) * 100 if kpis["total_revenue"] > 0 else 0
        avg_fte = kpis["total_fte"] / 12 if kpis["total_fte"] > 0 else 0  # Average across 12 months
        revenue_per_fte = kpis["total_revenue"] / avg_fte if avg_fte > 0 else 0
        cost_per_fte = kpis["total_cost"] / avg_fte if avg_fte > 0 else 0
        net_growth = kpis["total_recruitment"] - kpis["total_churn"]
        churn_rate = (kpis["total_churn"] / avg_fte) * 100 if avg_fte > 0 else 0
        
        derived_metrics[year] = {
            "total_profit": total_profit,
            "profit_margin": profit_margin,
            "avg_fte": avg_fte,
            "revenue_per_fte": revenue_per_fte,
            "cost_per_fte": cost_per_fte,
            "net_growth": net_growth,
            "churn_rate": churn_rate
        }
    
    # Print metrics rows
    metrics = [
        ("Average FTE", "avg_fte", "{:,.0f}"),
        ("Total Revenue ($)", "total_revenue", "${:,.0f}"),
        ("Total Cost ($)", "total_cost", "${:,.0f}"),
        ("Total Profit ($)", "total_profit", "${:,.0f}"),
        ("Profit Margin (%)", "profit_margin", "{:.1f}%"),
        ("Revenue per FTE ($)", "revenue_per_fte", "${:,.0f}"),
        ("Cost per FTE ($)", "cost_per_fte", "${:,.0f}"),
        ("Total Recruitment", "total_recruitment", "{:,}"),
        ("Total Churn", "total_churn", "{:,}"),
        ("Net Growth", "net_growth", "{:+,}"),
        ("Annual Churn Rate (%)", "churn_rate", "{:.1f}%"),
        ("Total Progression", "total_progression", "{:,}"),
        ("Average UTR", "average_utr", "{:.2f}")
    ]
    
    for metric_name, metric_key, format_str in metrics:
        row = f"{metric_name:<25}"
        for year in years:
            if metric_key in ["total_profit", "profit_margin", "avg_fte", "revenue_per_fte", "cost_per_fte", "net_growth", "churn_rate"]:
                value = derived_metrics[year][metric_key]
            else:
                value = yearly_data[year]["global_kpis"][metric_key]
            
            formatted_value = format_str.format(value)
            row += f"{formatted_value:>15}"
        print(row)

def print_fte_tables(yearly_data: Dict[str, Any]):
    """Print FTE breakdown tables."""
    
    years = sorted(yearly_data.keys())
    
    # Get all offices and levels
    all_offices = set()
    all_levels = set()
    for year_data in yearly_data.values():
        all_offices.update(year_data["office_fte"].keys())
        all_levels.update(year_data["level_fte"].keys())
    
    all_offices = sorted(all_offices)
    all_levels = sorted(all_levels)
    
    # Office FTE Table
    print(f"\n🏢 AVERAGE FTE BY OFFICE AND YEAR")
    print("=" * 80)
    
    header = f"{'Office':<15}"
    for year in years:
        header += f"{'Year ' + year:>12}"
    print(header)
    print("-" * (15 + 12 * len(years)))
    
    for office in all_offices:
        row = f"{office:<15}"
        for year in years:
            # Convert total FTE to average (divide by 12 months)
            avg_fte = yearly_data[year]["office_fte"].get(office, 0) / 12
            row += f"{avg_fte:>12,.0f}"
        print(row)
    
    # Add total row
    total_row = f"{'TOTAL':<15}"
    for year in years:
        total_avg_fte = yearly_data[year]["global_kpis"]["total_fte"] / 12
        total_row += f"{total_avg_fte:>12,.0f}"
    print("-" * (15 + 12 * len(years)))
    print(total_row)
    
    # Level FTE Table
    print(f"\n📊 AVERAGE FTE BY LEVEL AND YEAR")
    print("=" * 80)
    
    header = f"{'Level':<8}"
    for year in years:
        header += f"{'Year ' + year:>12}"
    print(header)
    print("-" * (8 + 12 * len(years)))
    
    for level in all_levels:
        row = f"{level:<8}"
        for year in years:
            # Convert total FTE to average (divide by 12 months)
            avg_fte = yearly_data[year]["level_fte"].get(level, 0) / 12
            row += f"{avg_fte:>12,.0f}"
        print(row)
    
    # Add total row
    total_row = f"{'TOTAL':<8}"
    for year in years:
        total_avg_fte = yearly_data[year]["global_kpis"]["total_fte"] / 12
        total_row += f"{total_avg_fte:>12,.0f}"
    print("-" * (8 + 12 * len(years)))
    print(total_row)
    
    # Detailed Office x Level FTE Tables for each year
    for year in years:
        print(f"\n📋 DETAILED FTE BREAKDOWN - YEAR {year}")
        print("=" * 80)
        
        # Office x Level matrix
        header = f"{'Office':<12}"
        for level in all_levels:
            header += f"{level:>8}"
        header += f"{'Total':>10}"
        print(header)
        print("-" * (12 + 8 * len(all_levels) + 10))
        
        for office in all_offices:
            row = f"{office:<12}"
            office_total = 0
            for level in all_levels:
                # Convert total FTE to average (divide by 12 months)
                avg_fte = yearly_data[year]["office_level_fte"].get(office, {}).get(level, 0) / 12
                office_total += avg_fte
                row += f"{avg_fte:>8,.0f}"
            row += f"{office_total:>10,.0f}"
            print(row)
        
        # Add total row
        total_row = f"{'TOTAL':<12}"
        grand_total = 0
        for level in all_levels:
            level_total = yearly_data[year]["level_fte"].get(level, 0) / 12
            grand_total += level_total
            total_row += f"{level_total:>8,.0f}"
        total_row += f"{grand_total:>10,.0f}"
        print("-" * (12 + 8 * len(all_levels) + 10))
        print(total_row)

def main():
    """Generate detailed KPI and FTE tables."""
    create_kpi_tables()

if __name__ == "__main__":
    main()