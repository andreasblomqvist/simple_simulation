#!/usr/bin/env python3
"""
Test that replicates the exact spreadsheet calculation from the user's data
to identify where the simulation logic differs
"""

def test_exact_spreadsheet_calculation():
    """Test using the exact values from the user's spreadsheet"""
    
    print("📋 EXACT SPREADSHEET CALCULATION TEST")
    print("=" * 60)
    
    # Exact values from the user's spreadsheet
    test_cases = [
        {"price": 1098, "salary": 42000, "level": "A"},
        {"price": 1116, "salary": 46000, "level": "AC"}, 
        {"price": 1124, "salary": 51000, "level": "C"},
        {"price": 1153, "salary": 58000, "level": "SrC"},
        {"price": 1226, "salary": 66000, "level": "AM"},
        {"price": 1328, "salary": 78000, "level": "M"},
        {"price": 1480, "salary": 96000, "level": "SrM"},
        {"price": 1427, "salary": 115000, "level": "SrM2"},
        {"price": 1807, "salary": 124000, "level": "PiP"}
    ]
    
    # Constants from spreadsheet
    total_time = 166.4  # hours per month
    ascense = 15.7  # vacation/absence hours
    consultant_time = 150.7  # working hours (total_time - ascense)
    utr = 0.85  # 85% utilization
    invoiced_time = 128.095  # consultant_time * utr
    
    # Employment cost multipliers from spreadsheet
    social_multiplier = 1.25  # 25% social costs
    pension_multiplier = 1.15  # 15% pension
    
    print(f"📊 Using exact spreadsheet parameters:")
    print(f"   Total time: {total_time} hours")
    print(f"   Ascense: {ascense} hours") 
    print(f"   Consultant time: {consultant_time} hours")
    print(f"   UTR: {utr*100}%")
    print(f"   Invoiced time: {invoiced_time} hours")
    print(f"   Social multiplier: {social_multiplier}")
    print(f"   Pension multiplier: {pension_multiplier}")
    print()
    
    for case in test_cases:
        price = case["price"]
        salary = case["salary"]
        level = case["level"]
        
        # Revenue calculation (exact from spreadsheet)
        revenue = price * invoiced_time
        
        # Cost calculation (exact from spreadsheet)
        salary_cost = salary * social_multiplier  # Social costs
        pension_cost = salary * pension_multiplier  # Pension costs
        total_cost = salary_cost + pension_cost
        
        # Profit calculation
        profit = revenue - total_cost
        margin = (profit / revenue) * 100 if revenue > 0 else 0
        
        print(f"{level:4}: {revenue:8.0f} SEK revenue - {total_cost:8.0f} SEK cost = {profit:8.0f} SEK profit ({margin:5.1f}%)")
    
    print()
    print("🔍 KEY INSIGHT: All results should be POSITIVE!")
    print("If the simulation shows negative values, there's a fundamental error in the logic.")

if __name__ == "__main__":
    test_exact_spreadsheet_calculation() 