#!/usr/bin/env python3
"""
Explain how aggressive recruitment/progression rates lead to negative financials
"""

def explain_financial_breakdown():
    """Show the mathematical relationship between aggressive rates and negative financials"""
    
    print("💸 HOW AGGRESSIVE RATES DESTROY FINANCIALS")
    print("=" * 60)
    
    print("🎯 THE PROBLEM: Salary Inflation Through Progression")
    print("-" * 50)
    
    # Example: Stockholm C level in January
    print("Example: Stockholm C level progression (January):")
    print("  • Started with: 123 C-level consultants")
    print("  • Progression rate: 26% in ONE MONTH")
    print("  • Result: 47 people promoted from C → SrC")
    print()
    
    # Show the salary impact
    c_salary = 48000  # SEK/month
    src_salary = 53000  # SEK/month
    salary_increase = src_salary - c_salary
    
    print("💰 SALARY IMPACT:")
    print(f"  • C level salary: {c_salary:,} SEK/month")
    print(f"  • SrC level salary: {src_salary:,} SEK/month") 
    print(f"  • Salary increase per person: {salary_increase:,} SEK/month")
    print(f"  • Total monthly cost increase: {47 * salary_increase:,} SEK")
    print(f"  • Annual cost increase: {47 * salary_increase * 12:,} SEK")
    print()
    
    print("🔄 THE COMPOUNDING EFFECT:")
    print("-" * 30)
    print("Month 1: 47 people get +5,000 SEK/month")
    print("Month 2: Another 40+ people get promoted (new C levels)")
    print("Month 3: Even more promotions...")
    print("Result: Salary costs EXPLODE exponentially")
    print()
    
    print("📊 REVENUE vs COST MISMATCH:")
    print("-" * 35)
    
    # Revenue calculation
    c_price = 1154  # SEK/hour
    src_price = 1185  # SEK/hour
    working_hours = 166.4 * 0.95  # 95% utilization
    
    revenue_increase_per_person = (src_price - c_price) * working_hours
    cost_increase_per_person = salary_increase * 1.40  # Including employment costs
    
    print(f"Revenue increase per promoted person:")
    print(f"  • Price difference: {src_price - c_price} SEK/hour")
    print(f"  • Monthly revenue increase: {revenue_increase_per_person:,.0f} SEK")
    print()
    print(f"Cost increase per promoted person:")
    print(f"  • Salary increase: {salary_increase:,} SEK/month")
    print(f"  • With employment costs (40%): {cost_increase_per_person:,.0f} SEK/month")
    print()
    print(f"NET IMPACT PER PROMOTION:")
    print(f"  • Revenue increase: +{revenue_increase_per_person:,.0f} SEK/month")
    print(f"  • Cost increase: -{cost_increase_per_person:,.0f} SEK/month")
    print(f"  • Net loss per promotion: {revenue_increase_per_person - cost_increase_per_person:,.0f} SEK/month")
    print()
    
    print("🚨 THE DEATH SPIRAL:")
    print("-" * 25)
    print("1. Aggressive progression rates promote too many people")
    print("2. Each promotion increases costs more than revenue")
    print("3. Multiply by hundreds of promotions per month")
    print("4. Compound over multiple years")
    print("5. Result: Costs grow exponentially faster than revenue")
    print()
    
    print("📈 NUMERICAL EXAMPLE (3-year simulation):")
    print("-" * 45)
    
    # Rough calculation for 3 years
    months = 36
    promotions_per_month = 100  # Conservative estimate across all levels/offices
    net_loss_per_promotion = cost_increase_per_person - revenue_increase_per_person
    
    total_monthly_loss = promotions_per_month * net_loss_per_promotion
    total_3_year_loss = total_monthly_loss * months
    
    print(f"Estimated promotions per month (all levels): {promotions_per_month}")
    print(f"Net loss per promotion: {net_loss_per_promotion:,.0f} SEK/month")
    print(f"Monthly loss from promotions: {total_monthly_loss:,.0f} SEK")
    print(f"3-year accumulated loss: {total_3_year_loss/1_000_000:,.0f} million SEK")
    print()
    
    print("✅ THE SOLUTION:")
    print("-" * 20)
    print("• Use realistic progression rates (2-5% annually, not 26% monthly)")
    print("• Balance progression with recruitment of junior levels")
    print("• Ensure revenue growth matches or exceeds cost growth")
    print("• Test with conservative rates first")

if __name__ == "__main__":
    explain_financial_breakdown() 