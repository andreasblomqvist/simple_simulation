import json
import pandas as pd

print("=== USER'S ENGINE vs CLAUDE AI COMPARISON ===")
print()

# Claude AI's results (from the screenshot - 5 year simulation)
claude_results = {
    'A': {'start': 163, 'end': 318, 'growth': 95.1, 'trend': 'Rapid Growth'},
    'AC': {'start': 231, 'end': 251, 'growth': 8.7, 'trend': 'Growing'},
    'AM': {'start': 418, 'end': 408, 'growth': -2.4, 'trend': 'Declining'},
    'C': {'start': 356, 'end': 348, 'growth': -2.2, 'trend': 'Declining'},
    'M': {'start': 156, 'end': 150, 'growth': -3.8, 'trend': 'Declining'},
    'PiP': {'start': 43, 'end': 43, 'growth': 0.0, 'trend': 'Stable'},
    'SrC': {'start': 409, 'end': 399, 'growth': -2.4, 'trend': 'Declining'},
    'SrM': {'start': 66, 'end': 62, 'growth': -6.1, 'trend': 'Declining'}
}

claude_summary = {
    'starting_total': 1842,
    'ending_total': 1979,
    'net_growth': 137,
    'total_growth_pct': 7.4,
    'annual_growth_rate': 1.4,
    'monthly_growth_rate': 0.120
}

print("1. CLAUDE AI SIMULATION RESULTS (5 Years):")
print("==========================================")
print("Level | Start | End   | Change | Growth% | Trend")
print("------|-------|-------|--------|---------|----------")

claude_total_start = 0
claude_total_end = 0

for level, data in claude_results.items():
    print(f"{level:5} | {data['start']:5} | {data['end']:5} | {data['end']-data['start']:6} | {data['growth']:6.1f}% | {data['trend']}")
    claude_total_start += data['start']
    claude_total_end += data['end']

print("------|-------|-------|--------|---------|----------")
print(f"TOTAL | {claude_total_start:5} | {claude_total_end:5} | {claude_total_end-claude_total_start:6} | {((claude_total_end/claude_total_start-1)*100):6.1f}% | Overall")

print(f"\nClaude Summary:")
print(f"- Net Growth: +{claude_summary['net_growth']} people (+{claude_summary['total_growth_pct']:.1f}%)")
print(f"- Annual Growth Rate: {claude_summary['annual_growth_rate']:.1f}%")
print(f"- Monthly Growth Rate: {claude_summary['monthly_growth_rate']:.3f}%")

print("\n2. USER'S ENGINE RESULTS (Normalized to 5 Years):")
print("=================================================")

# Load user's simulation data
try:
    with open('/home/ubuntu/upload/simulation_results_20250630_161229.json', 'r') as f:
        user_data = json.load(f)
    
    # Calculate user's results - get final state after 5 years (2030 data)
    user_results = {}
    
    # Get 2030 data (5 years from 2025)
    final_year = '2030'
    if final_year in user_data['years']:
        for office, office_data in user_data['years'][final_year]['offices'].items():
            for role, role_data in office_data['levels'].items():
                if isinstance(role_data, dict):
                    for level, level_data in role_data.items():
                        if level not in user_results:
                            user_results[level] = 0
                        
                        # Get December data (final month of 5th year)
                        if len(level_data) >= 12:
                            user_results[level] += level_data[11]['total']  # December (index 11)
    
    print("Level | Start | End   | Change | Growth% | vs Claude")
    print("------|-------|-------|--------|---------|----------")
    
    user_total_start = 0
    user_total_end = 0
    
    for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
        if level in user_results and level in claude_results:
            start = claude_results[level]['start']  # Same starting point
            end = user_results[level]
            change = end - start
            growth_pct = ((end / start) - 1) * 100 if start > 0 else 0
            
            claude_growth = claude_results[level]['growth']
            difference = growth_pct - claude_growth
            
            print(f"{level:5} | {start:5} | {end:5} | {change:6} | {growth_pct:6.1f}% | {difference:+7.1f}pp")
            
            user_total_start += start
            user_total_end += end
    
    user_total_growth = ((user_total_end / user_total_start) - 1) * 100
    total_difference = user_total_growth - claude_summary['total_growth_pct']
    
    print("------|-------|-------|--------|---------|----------")
    print(f"TOTAL | {user_total_start:5} | {user_total_end:5} | {user_total_end-user_total_start:6} | {user_total_growth:6.1f}% | {total_difference:+7.1f}pp")
    
    print(f"\nUser's Engine Summary:")
    print(f"- Net Growth: +{user_total_end-user_total_start} people (+{user_total_growth:.1f}%)")
    print(f"- Difference from Claude: {total_difference:+.1f} percentage points")
    
except Exception as e:
    print(f"Error loading user's simulation data: {e}")
    user_results = {}
    user_total_end = 0
    user_total_growth = 0

print("\n3. DETAILED COMPARISON ANALYSIS:")
print("================================")

if user_results:
    print("Comparing growth patterns:")
    print("Level | Claude Growth | User Growth | Difference | Issue Type")
    print("------|---------------|-------------|------------|------------")
    
    major_issues = []
    moderate_issues = []
    minor_issues = []
    
    for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
        if level in user_results and level in claude_results:
            claude_growth = claude_results[level]['growth']
            
            start = claude_results[level]['start']
            user_end = user_results[level]
            user_growth = ((user_end / start) - 1) * 100 if start > 0 else 0
            
            difference = user_growth - claude_growth
            abs_diff = abs(difference)
            
            if abs_diff > 50:
                issue_type = "🚨 MAJOR"
                major_issues.append(level)
            elif abs_diff > 20:
                issue_type = "⚠️  MODERATE"
                moderate_issues.append(level)
            elif abs_diff > 5:
                issue_type = "ℹ️  MINOR"
                minor_issues.append(level)
            else:
                issue_type = "✅ OK"
            
            print(f"{level:5} | {claude_growth:12.1f}% | {user_growth:10.1f}% | {difference:+9.1f}pp | {issue_type}")
    
    print("\n4. ISSUE CLASSIFICATION:")
    print("========================")
    
    print(f"Major Issues (>50pp difference): {len(major_issues)} levels")
    if major_issues:
        for level in major_issues:
            claude_g = claude_results[level]['growth']
            user_g = ((user_results[level] / claude_results[level]['start']) - 1) * 100
            print(f"  - Level {level}: Claude {claude_g:.1f}% vs User {user_g:.1f}% ({user_g-claude_g:+.1f}pp)")
    
    print(f"\nModerate Issues (20-50pp difference): {len(moderate_issues)} levels")
    if moderate_issues:
        for level in moderate_issues:
            claude_g = claude_results[level]['growth']
            user_g = ((user_results[level] / claude_results[level]['start']) - 1) * 100
            print(f"  - Level {level}: Claude {claude_g:.1f}% vs User {user_g:.1f}% ({user_g-claude_g:+.1f}pp)")
    
    print(f"\nMinor Issues (5-20pp difference): {len(minor_issues)} levels")
    if minor_issues:
        for level in minor_issues:
            claude_g = claude_results[level]['growth']
            user_g = ((user_results[level] / claude_results[level]['start']) - 1) * 100
            print(f"  - Level {level}: Claude {claude_g:.1f}% vs User {user_g:.1f}% ({user_g-claude_g:+.1f}pp)")

print("\n5. BASELINE CONSISTENCY CHECK:")
print("==============================")

# Check which simulation is more consistent with the original baseline
baseline_rates = {
    'A': {'rec_rate': 1.27, 'churn_rate': 0.15, 'net_rate': 1.12},
    'AC': {'rec_rate': 0.28, 'churn_rate': 0.14, 'net_rate': 0.14},
    'AM': {'rec_rate': 0.00, 'churn_rate': 0.04, 'net_rate': -0.04},
    'C': {'rec_rate': 0.04, 'churn_rate': 0.08, 'net_rate': -0.04},
    'M': {'rec_rate': 0.00, 'churn_rate': 0.07, 'net_rate': -0.07},
    'PiP': {'rec_rate': 0.00, 'churn_rate': 0.00, 'net_rate': 0.00},
    'SrC': {'rec_rate': 0.01, 'churn_rate': 0.05, 'net_rate': -0.04},
    'SrM': {'rec_rate': 0.00, 'churn_rate': 0.10, 'net_rate': -0.10}
}

print("Expected vs Actual Growth (based on baseline monthly rates):")
print("Level | Expected 5Y | Claude 5Y | User 5Y | Claude vs Exp | User vs Exp")
print("------|-------------|-----------|---------|---------------|-------------")

claude_total_deviation = 0
user_total_deviation = 0

for level in ['A', 'AC', 'AM', 'C', 'M', 'PiP', 'SrC', 'SrM']:
    if level in baseline_rates and level in claude_results:
        net_monthly_rate = baseline_rates[level]['net_rate']
        
        # Calculate expected growth over 5 years (60 months)
        expected_5y = ((1 + net_monthly_rate/100) ** 60 - 1) * 100
        
        claude_actual = claude_results[level]['growth']
        claude_vs_exp = claude_actual - expected_5y
        claude_total_deviation += abs(claude_vs_exp)
        
        if level in user_results:
            start = claude_results[level]['start']
            user_actual = ((user_results[level] / start) - 1) * 100 if start > 0 else 0
            user_vs_exp = user_actual - expected_5y
            user_total_deviation += abs(user_vs_exp)
        else:
            user_actual = 0
            user_vs_exp = 0
        
        print(f"{level:5} | {expected_5y:11.1f}% | {claude_actual:9.1f}% | {user_actual:7.1f}% | {claude_vs_exp:13.1f}% | {user_vs_exp:11.1f}%")

print("------|-------------|-----------|---------|---------------|-------------")
print(f"TOTAL |             |           |         | {claude_total_deviation:13.1f}% | {user_total_deviation:11.1f}%")

print(f"\nBaseline Consistency Assessment:")
print(f"- Claude AI deviation from baseline: {claude_total_deviation:.1f}%")
if user_results:
    print(f"- User's engine deviation from baseline: {user_total_deviation:.1f}%")
    if claude_total_deviation < user_total_deviation:
        print("✅ Claude AI is MORE consistent with baseline expectations")
        print("❌ User's engine deviates MORE from baseline expectations")
    else:
        print("❌ Claude AI deviates MORE from baseline expectations")
        print("✅ User's engine is MORE consistent with baseline expectations")
else:
    print("- Cannot compare user's engine (data loading error)")

print("\n6. PRELIMINARY DIAGNOSIS:")
print("=========================")

if user_results:
    total_issues = len(major_issues) + len(moderate_issues) + len(minor_issues)
    
    if total_issues == 0:
        print("✅ No significant issues found - engines produce similar results")
    elif len(major_issues) > 0:
        print("🚨 CRITICAL: Major discrepancies found in user's engine")
        print("   Likely causes: Fundamental calculation errors, parameter bugs, or logic flaws")
    elif len(moderate_issues) > 0:
        print("⚠️  WARNING: Moderate discrepancies found in user's engine")
        print("   Likely causes: Parameter scaling issues or minor calculation errors")
    else:
        print("ℹ️  INFO: Minor discrepancies found in user's engine")
        print("   Likely causes: Rounding differences or minor parameter variations")
    
    print(f"\nNext steps: Detailed analysis of user's engine logic and calculations")
else:
    print("❌ Cannot complete analysis due to data loading issues")

print(f"\nAnalysis complete. User's engine shows {'significant' if len(major_issues) > 0 else 'minor'} discrepancies vs Claude AI.")

