#!/usr/bin/env python3
"""
Analyze Simulation JSON Results
Shows key metrics and verification points from simulation results
"""

import json
import sys
from datetime import datetime
import os
import matplotlib.pyplot as plt

def analyze_simulation_json(filename):
    """Analyze a simulation JSON file and show key metrics"""
    
    print(f"🔍 Analyzing simulation results: {filename}")
    print("=" * 60)
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        return
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in file: {filename}")
        return
    
    # 1. Basic Structure Check
    print("\n📋 1. DATA STRUCTURE VERIFICATION")
    print("-" * 40)
    
    required_sections = ['years', 'simulation_period', 'configuration', 'monthly_office_metrics']
    for section in required_sections:
        if section in data:
            print(f"✅ {section} section present")
        else:
            print(f"❌ {section} section missing")
    
    # 2. Simulation Period
    print(f"\n📅 2. SIMULATION PERIOD")
    print("-" * 40)
    if 'simulation_period' in data:
        period = data['simulation_period']
        print(f"Start: {period.get('start_year', 'N/A')}")
        print(f"End: {period.get('end_year', 'N/A')}")
        print(f"Months: {period.get('total_months', 'N/A')}")
    
    # 3. Growth Analysis
    print(f"\n📈 3. GROWTH ANALYSIS")
    print("-" * 40)
    
    if 'years' in data:
        years_data = data['years']
        years = list(years_data.keys())
        years.sort()
        
        if len(years) >= 2:
            first_year = years[0]
            last_year = years[-1]
            
            first_fte = years_data[first_year].get('total_fte', 0)
            last_fte = years_data[last_year].get('total_fte', 0)
            
            growth = last_fte - first_fte
            growth_pct = (growth / first_fte * 100) if first_fte > 0 else 0
            
            print(f"Starting FTE ({first_year}): {first_fte:,.0f}")
            print(f"Ending FTE ({last_year}): {last_fte:,.0f}")
            print(f"Total Growth: {growth:+,.0f} ({growth_pct:+.1f}%)")
            
            # Annual growth rate
            num_years = len(years)
            annual_growth = ((last_fte / first_fte) ** (1/num_years) - 1) * 100
            print(f"Annual Growth Rate: {annual_growth:.1f}%")
    
    # 4. Office Analysis
    print(f"\n🏢 4. OFFICE ANALYSIS")
    print("-" * 40)
    
    if 'monthly_office_metrics' in data:
        monthly_data = data['monthly_office_metrics']
        if monthly_data:
            # Get first and last month
            months = list(monthly_data.keys())
            months.sort()
            
            if len(months) >= 2:
                first_month = months[0]
                last_month = months[-1]
                
                first_offices = monthly_data[first_month]
                last_offices = monthly_data[last_month]
                
                print(f"First month ({first_month}): {len(first_offices)} offices")
                print(f"Last month ({last_month}): {len(last_offices)} offices")
                
                # Show top 5 offices by growth
                office_growth = {}
                for office_name in first_offices.keys():
                    if office_name in last_offices:
                        start_fte = first_offices[office_name].get('total_fte', 0)
                        end_fte = last_offices[office_name].get('total_fte', 0)
                        growth = end_fte - start_fte
                        office_growth[office_name] = growth
                
                # Sort by growth
                sorted_offices = sorted(office_growth.items(), key=lambda x: x[1], reverse=True)
                
                print(f"\nTop 5 offices by FTE growth:")
                for i, (office, growth) in enumerate(sorted_offices[:5], 1):
                    print(f"  {i}. {office}: {growth:+.0f} FTE")
    
    # 5. Configuration Check
    print(f"\n⚙️ 5. CONFIGURATION VERIFICATION")
    print("-" * 40)
    
    if 'configuration' in data:
        config = data['configuration']
        print(f"Configuration type: {type(config)}")
        
        if isinstance(config, dict):
            print(f"Total offices in config: {len(config)}")
            
            # Handle different config structures
            total_fte = 0
            zero_fte_offices = []
            
            for office_name, office_data in config.items():
                if isinstance(office_data, dict):
                    fte = office_data.get('total_fte', 0)
                    total_fte += fte
                    if fte == 0:
                        zero_fte_offices.append(office_name)
                else:
                    print(f"⚠️  Unexpected office data type for {office_name}: {type(office_data)}")
            
            print(f"Total FTE in config: {total_fte:,.0f}")
            
            if zero_fte_offices:
                print(f"⚠️  Offices with 0 FTE: {', '.join(zero_fte_offices)}")
            else:
                print("✅ All offices have FTE > 0")
        else:
            print(f"⚠️  Configuration is not a dict: {type(config)}")
    
    # 6. Monthly Progression Check
    print(f"\n📊 6. MONTHLY PROGRESSION CHECK")
    print("-" * 40)
    
    if 'monthly_office_metrics' in data:
        monthly_data = data['monthly_office_metrics']
        months = list(monthly_data.keys())
        months.sort()
        
        if len(months) >= 3:
            # Check for consistent growth
            fte_progression = []
            for month in months:
                total_fte = sum(office.get('total_fte', 0) for office in monthly_data[month].values())
                fte_progression.append(total_fte)
            
            # Check for any decreases
            decreases = 0
            for i in range(1, len(fte_progression)):
                if fte_progression[i] < fte_progression[i-1]:
                    decreases += 1
            
            if decreases == 0:
                print("✅ Consistent month-over-month growth")
            else:
                print(f"⚠️  {decreases} months with FTE decrease")
            
            # Show monthly changes
            print(f"\nMonthly FTE progression (first 6 months):")
            for i, fte in enumerate(fte_progression[:6]):
                if i > 0:
                    change = fte - fte_progression[i-1]
                    print(f"  Month {i+1}: {fte:,.0f} ({change:+.0f})")
                else:
                    print(f"  Month {i+1}: {fte:,.0f}")
    
    # 7. Summary
    print(f"\n🎯 7. VERIFICATION SUMMARY")
    print("-" * 40)
    
    issues = []
    
    # Check for reasonable growth
    if 'years' in data:
        years_data = data['years']
        years = list(years_data.keys())
        if len(years) >= 2:
            first_fte = years_data[years[0]].get('total_fte', 0)
            last_fte = years_data[years[-1]].get('total_fte', 0)
            growth_pct = ((last_fte / first_fte) - 1) * 100 if first_fte > 0 else 0
            
            if growth_pct > 100:  # More than 100% growth
                issues.append(f"Very high growth: {growth_pct:.1f}%")
            elif growth_pct < 0:  # Negative growth
                issues.append(f"Negative growth: {growth_pct:.1f}%")
            elif growth_pct > 50:  # High but reasonable
                print(f"📈 High growth: {growth_pct:.1f}% (reasonable for 3 years)")
            else:
                print(f"📈 Moderate growth: {growth_pct:.1f}%")
    
    # Check data consistency
    if 'years' in data and 'monthly_office_metrics' in data:
        years_data = data['years']
        monthly_data = data['monthly_office_metrics']
        
        if years_data and monthly_data:
            last_year = list(years_data.keys())[-1]
            last_month = list(monthly_data.keys())[-1]
            
            year_fte = years_data[last_year].get('total_fte', 0)
            month_fte = sum(office.get('total_fte', 0) for office in monthly_data[last_month].values())
            
            if abs(year_fte - month_fte) > 1:  # Allow for rounding
                issues.append(f"FTE mismatch: Year={year_fte}, Month={month_fte}")
            else:
                print("✅ FTE consistency verified")
    
    if issues:
        print(f"\n⚠️  Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ No major issues detected")
    
    print(f"\n📅 Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def visualize_monthly_growth_rate(filename):
    """Visualize monthly growth rate for each level from simulation JSON results"""
    import matplotlib.pyplot as plt
    print(f"🔍 Analyzing simulation results: {filename}")
    print("=" * 60)
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        return
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in file: {filename}")
        return
    
    if "years" not in data or not isinstance(data["years"], dict):
        print("❌ Could not find expected 'years' dict in result JSON.")
        return
    years = data["years"]
    # We'll aggregate by level across all offices and roles
    level_fte_by_month = {}  # {level: [fte0, fte1, ...]}
    months_labels = []
    # Sort years chronologically
    for year in sorted(years.keys()):
        year_data = years[year]
        offices = year_data.get("offices", {})
        # For each office
        for office_name, office_data in offices.items():
            levels = office_data.get("levels", {})
            # For each role (e.g., Consultant, Sales, etc.)
            for role_name, role_levels in levels.items():
                if isinstance(role_levels, dict):
                    # For each level (e.g., A, AC, AM, ...)
                    for level, months in role_levels.items():
                        if not isinstance(months, list):
                            continue
                        for i, month_data in enumerate(months):
                            # Compose a unique key for level (role+level)
                            level_key = f"{role_name} {level}"
                            if level_key not in level_fte_by_month:
                                level_fte_by_month[level_key] = []
                            # Extend the list if needed
                            while len(level_fte_by_month[level_key]) <= i + len(months_labels):
                                level_fte_by_month[level_key].append(None)
                            # Use 'total' as FTE for this month
                            fte = month_data.get("total", 0)
                            # Place in the correct month index
                            idx = i + len(months_labels)
                            level_fte_by_month[level_key][idx] = fte
                elif isinstance(role_levels, list):
                    # Treat the role as a single level (e.g., 'Operations')
                    level_key = role_name
                    for i, month_data in enumerate(role_levels):
                        if level_key not in level_fte_by_month:
                            level_fte_by_month[level_key] = []
                        while len(level_fte_by_month[level_key]) <= i + len(months_labels):
                            level_fte_by_month[level_key].append(None)
                        fte = month_data.get("total", 0)
                        idx = i + len(months_labels)
                        level_fte_by_month[level_key][idx] = fte
                else:
                    print(f"⚠️ Unexpected type for role_levels in role '{role_name}': {type(role_levels)}")
                    continue
            # Only add month labels once per year (assuming all offices/roles/levels have same months)
            if not months_labels:
                # Get the number of months from the first available level's months list
                try:
                    first_role = next(iter(levels.values()))
                    first_level = next(iter(first_role.values()))
                    for i in range(len(first_level)):
                        months_labels.append(f"{year}-M{i+1}")
                except Exception as e:
                    print(f"Error determining months: {e}")
                    pass
    # Calculate monthly growth rates for each level
    growth_rates = {}
    for level, fte_list in level_fte_by_month.items():
        rates = []
        for i in range(1, len(fte_list)):
            prev = fte_list[i-1]
            curr = fte_list[i]
            if prev in (None, 0) or curr is None:
                rate = 0
            else:
                rate = (curr - prev) / prev * 100
            rates.append(rate)
        growth_rates[level] = rates
    # Plot
    plt.figure(figsize=(14, 8))
    for level, rates in growth_rates.items():
        plt.plot(range(1, len(rates)+1), rates, label=level)
    plt.xlabel("Month")
    plt.ylabel("Monthly Growth Rate (%)")
    plt.title("Monthly Growth Rate by Level (All Offices)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_simulation_json.py <simulation_file.json>")
        print("Example: python analyze_simulation_json.py simulation_results_20250630_121737.json")
        sys.exit(1)
    
    filename = sys.argv[1]
    analyze_simulation_json(filename)
    visualize_monthly_growth_rate(filename) 