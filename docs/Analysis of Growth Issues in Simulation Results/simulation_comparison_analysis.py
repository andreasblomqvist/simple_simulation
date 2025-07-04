import json
import pandas as pd

print("=== SIMULATION INCONSISTENCY ANALYSIS ===")
print()

# Data from new screenshot (5-year simulation)
new_simulation_results = {
    'A': {'year_0': 163, 'year_5': 318, 'change': 155, 'pct_change': 95.1, 'trend': 'Rapid Growth'},
    'AC': {'year_0': 231, 'year_5': 251, 'change': 20, 'pct_change': 8.7, 'trend': 'Growing'},
    'AM': {'year_0': 418, 'year_5': 408, 'change': -10, 'pct_change': -2.4, 'trend': 'Declining'},
    'C': {'year_0': 356, 'year_5': 348, 'change': -8, 'pct_change': -2.2, 'trend': 'Declining'},
    'M': {'year_0': 156, 'year_5': 150, 'change': -6, 'pct_change': -3.8, 'trend': 'Declining'},
    'PiP': {'year_0': 43, 'year_5': 43, 'change': 0, 'pct_change': 0.0, 'trend': 'Stable'},
    'SrC': {'year_0': 409, 'year_5': 399, 'change': -10, 'pct_change': -2.4, 'trend': 'Declining'},
    'SrM': {'year_0': 66, 'year_5': 62, 'change': -4, 'pct_change': -6.1, 'trend': 'Declining'}
}

# Summary from new simulation
new_summary = {
    'starting_total': 1842,
    'ending_total': 1979,
    'net_growth': 137,
    'total_pct_growth': 7.4,
    'annual_growth_rate': 1.4,
    'monthly_growth_rate': 0.120
}

print("1. NEW SIMULATION RESULTS (5-Year):")
print("===================================")
print("Level | Year 0 | Year 5 | Change | % Change | Trend")
print("------|--------|--------|--------|----------|----------")

total_year_0 = 0
total_year_5 = 0

for level, data in new_simulation_results.items():
    print(f"{level:5} | {data['year_0']:6} | {data['year_5']:6} | {data['change']:6} | {data['pct_change']:7.1f}% | {data['trend']}")
    total_year_0 += data['year_0']
    total_year_5 += data['year_5']

print("------|--------|--------|--------|----------|----------")
print(f"TOTAL | {total_year_0:6} | {total_year_5:6} | {total_year_5 - total_year_0:6} | {((total_year_5/total_year_0 - 1) * 100):7.1f}% | Overall")

print(f"\nNew Simulation Summary:")
print(f"- Starting Total: {new_summary['starting_total']:,} people")
print(f"- Ending Total: {new_summary['ending_total']:,} people") 
print(f"- Net Growth: +{new_summary['net_growth']} people (+{new_summary['total_pct_growth']:.1f}%)")
print(f"- Annual Growth Rate: {new_summary['annual_growth_rate']:.1f}%")
print(f"- Monthly Growth Rate: {new_summary['monthly_growth_rate']:.3f}%")

print("\n2. PREVIOUS SIMULATION RESULTS (6-Year):")
print("========================================")

# Load and analyze previous simulation data
try:
    with open('/home/ubuntu/upload/simulation_results_20250630_161229.json', 'r') as f:
        old_data = json.load(f)
    
    # Calculate final results from the 6-year simulation
    old_simulation_results = {}
    
    # Get the final year data (2030)
    final_year = '2030'
    if final_year in old_data['years']:
        for office, office_data in old_data['years'][final_year]['offices'].items():
            for role, role_data in office_data['levels'].items():
                if isinstance(role_data, dict):
                    for level, level_data in role_data.items():
                        if level not in old_simulation_results:
                            old_simulation_results[level] = 0
                        
                        # Get December data (final month)
                        if len(level_data) >= 12:
                            old_simulation_results[level] += level_data[11]['total']  # December (index 11)
    
    print("Level | Year 0 | Year 6 | Change | % Change | Growth Factor")
    print("------|--------|--------|--------|----------|---------------")
    
    old_total_final = 0
    baseline_total = sum(data['year_0'] for data in new_simulation_results.values())
    
    for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
        if level in old_simulation_results and level in new_simulation_results:
            year_0 = new_simulation_results[level]['year_0']  # Same starting point
            year_6 = old_simulation_results[level]
            change = year_6 - year_0
            pct_change = ((year_6 / year_0) - 1) * 100 if year_0 > 0 else 0
            growth_factor = year_6 / year_0 if year_0 > 0 else 0
            
            print(f"{level:5} | {year_0:6} | {year_6:6} | {change:6} | {pct_change:7.1f}% | {growth_factor:13.1f}x")
            old_total_final += year_6
    
    print("------|--------|--------|--------|----------|---------------")
    old_total_change = old_total_final - baseline_total
    old_total_pct = ((old_total_final / baseline_total) - 1) * 100
    old_growth_factor = old_total_final / baseline_total
    
    print(f"TOTAL | {baseline_total:6} | {old_total_final:6} | {old_total_change:6} | {old_total_pct:7.1f}% | {old_growth_factor:13.1f}x")
    
    print(f"\nOld Simulation Summary:")
    print(f"- Starting Total: {baseline_total:,} people")
    print(f"- Ending Total: {old_total_final:,} people")
    print(f"- Net Growth: +{old_total_change:,} people (+{old_total_pct:.1f}%)")
    print(f"- Growth Factor: {old_growth_factor:.1f}x over 6 years")
    
except Exception as e:
    print(f"Error loading old simulation data: {e}")
    old_total_final = 0
    old_total_pct = 0

print("\n3. DIRECT COMPARISON:")
print("====================")

if old_total_final > 0:
    print("Simulation Comparison (Same Starting Point):")
    print("--------------------------------------------")
    print(f"New Simulation (5 years): {baseline_total:,} → {total_year_5:,} (+{((total_year_5/baseline_total - 1) * 100):.1f}%)")
    print(f"Old Simulation (6 years): {baseline_total:,} → {old_total_final:,} (+{old_total_pct:.1f}%)")
    
    # Normalize to same time period (5 years)
    old_5_year_equivalent = baseline_total * ((old_total_final / baseline_total) ** (5/6))
    old_5_year_pct = ((old_5_year_equivalent / baseline_total) - 1) * 100
    
    print(f"\nNormalized to 5-year period:")
    print(f"New Simulation: +{((total_year_5/baseline_total - 1) * 100):.1f}% growth")
    print(f"Old Simulation: +{old_5_year_pct:.1f}% growth (estimated)")
    
    growth_difference = old_5_year_pct - ((total_year_5/baseline_total - 1) * 100)
    print(f"Difference: {growth_difference:+.1f} percentage points")
    
    if abs(growth_difference) > 10:
        print("🚨 CRITICAL: Massive inconsistency between simulation runs!")
    elif abs(growth_difference) > 5:
        print("⚠️  WARNING: Significant inconsistency between simulation runs")
    else:
        print("✅ Simulations show reasonable consistency")

print("\n4. LEVEL-BY-LEVEL ANALYSIS:")
print("===========================")

print("Comparing growth patterns by level:")
print("Level | New 5Y Growth | Old 6Y Growth | Consistency")
print("------|---------------|---------------|-------------")

for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    if level in new_simulation_results and level in old_simulation_results:
        new_growth = new_simulation_results[level]['pct_change']
        
        year_0 = new_simulation_results[level]['year_0']
        old_final = old_simulation_results[level]
        old_growth = ((old_final / year_0) - 1) * 100 if year_0 > 0 else 0
        
        # Normalize old growth to 5 years
        old_5y_growth = ((old_final / year_0) ** (5/6) - 1) * 100 if year_0 > 0 else 0
        
        difference = abs(new_growth - old_5y_growth)
        
        if difference < 5:
            consistency = "✅ Consistent"
        elif difference < 20:
            consistency = "⚠️  Moderate diff"
        else:
            consistency = "🚨 Major diff"
        
        print(f"{level:5} | {new_growth:12.1f}% | {old_5y_growth:12.1f}% | {consistency}")

print("\n5. CRITICAL FINDINGS:")
print("====================")

critical_issues = []

# Check for major inconsistencies
if old_total_final > 0:
    total_difference = abs(old_5_year_pct - ((total_year_5/baseline_total - 1) * 100))
    
    if total_difference > 50:
        critical_issues.append("MASSIVE growth inconsistency between simulation runs")
    elif total_difference > 20:
        critical_issues.append("Significant growth inconsistency between simulation runs")
    
    # Check individual levels
    major_level_issues = []
    for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
        if level in new_simulation_results and level in old_simulation_results:
            new_growth = new_simulation_results[level]['pct_change']
            year_0 = new_simulation_results[level]['year_0']
            old_final = old_simulation_results[level]
            old_5y_growth = ((old_final / year_0) ** (5/6) - 1) * 100 if year_0 > 0 else 0
            
            if abs(new_growth - old_5y_growth) > 50:
                major_level_issues.append(f"Level {level}: {new_growth:.1f}% vs {old_5y_growth:.1f}%")
    
    if major_level_issues:
        critical_issues.append(f"Major level inconsistencies: {', '.join(major_level_issues)}")

if critical_issues:
    print("🚨 CRITICAL ISSUES IDENTIFIED:")
    for i, issue in enumerate(critical_issues, 1):
        print(f"{i}. {issue}")
    
    print("\n💡 IMPLICATIONS:")
    print("- Simulation engine is NOT reliable")
    print("- Same inputs producing different outputs")
    print("- Cannot trust results for business planning")
    print("- Requires immediate investigation of simulation logic")
    
else:
    print("✅ No critical inconsistencies found")
    print("Simulations show reasonable consistency given different time periods")

print(f"\nAnalysis complete. Simulation reliability assessment: {'FAILED' if critical_issues else 'PASSED'}")

