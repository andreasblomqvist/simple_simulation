#!/usr/bin/env python3
"""
Test the updated employment cost calculations to see the impact of including pensions and other benefits
"""

def compare_employment_costs():
    """Compare old vs new employment cost calculations"""
    
    print("💰 Employment Cost Comparison")
    print("=" * 50)
    
    # Example: Stockholm A level consultant
    base_salary_monthly = 42000  # SEK
    base_salary_annual = base_salary_monthly * 12
    consultant_count = 69  # Stockholm A baseline
    
    # Old calculation (25% social costs only)
    old_rate = 0.25
    old_total_cost_per_consultant = base_salary_annual * (1 + old_rate)
    old_total_cost_organization = old_total_cost_per_consultant * consultant_count
    
    # New calculation (40% total employment costs)
    new_rate = 0.40
    new_total_cost_per_consultant = base_salary_annual * (1 + new_rate)
    new_total_cost_organization = new_total_cost_per_consultant * consultant_count
    
    # Calculate the difference
    cost_increase_per_consultant = new_total_cost_per_consultant - old_total_cost_per_consultant
    cost_increase_organization = new_total_cost_organization - old_total_cost_organization
    percentage_increase = ((new_total_cost_per_consultant / old_total_cost_per_consultant) - 1) * 100
    
    print(f"📊 Base Salary (Annual): {base_salary_annual:,} SEK")
    print(f"👥 Consultant Count: {consultant_count}")
    print("")
    
    print(f"🔴 OLD Calculation (25% social costs):")
    print(f"   Cost per consultant: {old_total_cost_per_consultant:,.0f} SEK/year")
    print(f"   Total organization cost: {old_total_cost_organization:,.0f} SEK/year")
    print("")
    
    print(f"🟢 NEW Calculation (40% total employment costs):")
    print(f"   Cost per consultant: {new_total_cost_per_consultant:,.0f} SEK/year")
    print(f"   Total organization cost: {new_total_cost_organization:,.0f} SEK/year")
    print("")
    
    print(f"📈 Impact:")
    print(f"   Increase per consultant: +{cost_increase_per_consultant:,.0f} SEK/year ({percentage_increase:.1f}%)")
    print(f"   Increase for organization: +{cost_increase_organization:,.0f} SEK/year")
    print("")
    
    # What this means for margins
    print(f"💡 What this means:")
    print(f"   - More realistic employment costs including pensions, health insurance, etc.")
    print(f"   - Will reduce EBITDA margins by ~{percentage_increase:.1f}% relative to revenue")
    print(f"   - Better reflects true cost of employment in European markets")
    print(f"   - Should make financial projections more accurate")

def breakdown_employment_costs():
    """Show what the 40% total employment cost rate includes"""
    
    print("\n🏢 Employment Cost Breakdown (Typical European Consulting Firm)")
    print("=" * 65)
    
    base_salary = 100  # Use 100 as base for percentage calculation
    
    components = [
        ("Base Salary", 100.0, "Direct salary payment"),
        ("Social Security (Employer)", 15.0, "Employer portion of social security"),
        ("Pension Contributions", 8.0, "Employer pension contributions"),
        ("Health Insurance", 5.0, "Employer health insurance costs"),
        ("Vacation/Holiday Accruals", 8.0, "Paid time off provisions"),
        ("Other Benefits", 4.0, "Training, equipment, other mandatory benefits")
    ]
    
    total_cost = sum(cost for _, cost, _ in components)
    
    print(f"{'Component':<25} {'Cost':<8} {'%':<6} {'Description'}")
    print("-" * 65)
    
    for component, cost, description in components:
        percentage = (cost / base_salary) * 100
        print(f"{component:<25} {cost:>6.0f} {percentage:>5.1f}% {description}")
    
    print("-" * 65)
    print(f"{'TOTAL EMPLOYMENT COST':<25} {total_cost:>6.0f} {(total_cost/base_salary)*100:>5.1f}%")
    print("")
    print(f"📊 This means for every 100 SEK in base salary,")
    print(f"    the true employment cost is {total_cost:.0f} SEK")
    print(f"    (an additional {total_cost - base_salary:.0f}% on top of base salary)")

if __name__ == "__main__":
    compare_employment_costs()
    breakdown_employment_costs() 