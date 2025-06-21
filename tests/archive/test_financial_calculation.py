#!/usr/bin/env python3
"""
Test to understand why financial calculations are producing negative values
"""

def calculate_simple_financials(consultants, price_per_hour, salary_annual):
    """Simple financial calculation to understand the problem"""
    
    # Constants
    working_hours_per_month = 166.4
    months_per_year = 12
    social_cost_rate = 0.25  # 25% social costs
    unplanned_absence = 0.05  # 5% absence
    
    print(f"📊 Financial Calculation for {consultants:,} consultants")
    print(f"   Price per hour: {price_per_hour:,.0f} SEK")
    print(f"   Annual salary: {salary_annual:,.0f} SEK")
    print("")
    
    # Revenue calculation
    billable_hours_per_month = working_hours_per_month * (1 - unplanned_absence)
    revenue_per_consultant_per_month = billable_hours_per_month * price_per_hour
    revenue_per_consultant_per_year = revenue_per_consultant_per_month * months_per_year
    total_revenue = consultants * revenue_per_consultant_per_year
    
    print(f"💰 Revenue Calculation:")
    print(f"   Billable hours/month: {billable_hours_per_month:.1f}")
    print(f"   Revenue/consultant/month: {revenue_per_consultant_per_month:,.0f} SEK")
    print(f"   Revenue/consultant/year: {revenue_per_consultant_per_year:,.0f} SEK")
    print(f"   Total annual revenue: {total_revenue:,.0f} SEK")
    print("")
    
    # Cost calculation
    cost_per_consultant_per_year = salary_annual * (1 + social_cost_rate)
    total_costs = consultants * cost_per_consultant_per_year
    
    print(f"💸 Cost Calculation:")
    print(f"   Salary + social costs: {cost_per_consultant_per_year:,.0f} SEK/year")
    print(f"   Total annual costs: {total_costs:,.0f} SEK")
    print("")
    
    # Profitability
    ebitda = total_revenue - total_costs
    margin = (ebitda / total_revenue * 100) if total_revenue > 0 else 0.0
    
    print(f"📈 Profitability:")
    print(f"   EBITDA: {ebitda:,.0f} SEK")
    print(f"   Margin: {margin:.1f}%")
    print("")
    
    return {
        'revenue': total_revenue,
        'costs': total_costs,
        'ebitda': ebitda,
        'margin': margin
    }

def test_financial_scenarios():
    """Test different scenarios to understand the problem"""
    
    print("🔧 Financial Calculation Analysis")
    print("=" * 60)
    
    # Scenario 1: Normal baseline (Stockholm A level)
    print("📋 Scenario 1: Normal Baseline (Stockholm A level)")
    print("-" * 40)
    baseline = calculate_simple_financials(
        consultants=69,  # Stockholm A baseline
        price_per_hour=1106.61,  # Stockholm A price
        salary_annual=42000 * 12  # Stockholm A monthly salary * 12
    )
    
    # Scenario 2: 10x growth (explosive growth scenario)
    print("📋 Scenario 2: 10x Growth (Explosive Growth)")
    print("-" * 40)
    explosive = calculate_simple_financials(
        consultants=690,  # 10x consultants
        price_per_hour=1106.61,  # Same price
        salary_annual=42000 * 12  # Same salary
    )
    
    # Scenario 3: What if salary is being calculated wrong?
    print("📋 Scenario 3: Wrong Salary Calculation (Monthly as Annual)")
    print("-" * 40)
    wrong_salary = calculate_simple_financials(
        consultants=690,  # 10x consultants
        price_per_hour=1106.61,  # Same price
        salary_annual=42000  # Monthly salary treated as annual (WRONG!)
    )
    
    # Scenario 4: Check if price is wrong
    print("📋 Scenario 4: Wrong Price Calculation (Monthly as Hourly)")
    print("-" * 40)
    wrong_price = calculate_simple_financials(
        consultants=690,  # 10x consultants
        price_per_hour=42000,  # Monthly salary as hourly price (WRONG!)
        salary_annual=42000 * 12  # Correct salary
    )
    
    print("🔍 Analysis Summary:")
    print("=" * 60)
    print(f"Baseline margin: {baseline['margin']:.1f}%")
    print(f"10x growth margin: {explosive['margin']:.1f}%")
    print(f"Wrong salary margin: {wrong_salary['margin']:.1f}%")
    print(f"Wrong price margin: {wrong_price['margin']:.1f}%")
    print("")
    
    if baseline['margin'] > 0 and explosive['margin'] > 0:
        print("✅ Growth should maintain positive margins")
    elif baseline['margin'] > 0 and explosive['margin'] < 0:
        print("❌ Something is wrong with the calculation logic")
    
    if wrong_salary['margin'] < 0:
        print("💡 Negative margins could be caused by wrong salary calculation")
    
    if abs(wrong_price['margin'] - explosive['margin']) < 1:
        print("💡 Price calculation might be the issue")

if __name__ == "__main__":
    test_financial_scenarios() 