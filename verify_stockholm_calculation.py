#!/usr/bin/env python3
"""
Verify Stockholm calculation based on user's real data showing 44M SEK monthly profit TOTAL
"""

def verify_stockholm_real_data():
    """Calculate Stockholm's expected financials based on user's spreadsheet"""
    
    print("💰 STOCKHOLM REAL DATA VERIFICATION")
    print("=" * 60)
    
    # From user's spreadsheet - these appear to be individual profit values per person
    # But the TOTAL Stockholm profit shown is 44,843,320.87 SEK
    stockholm_total_monthly_profit = 44843320.87  # SEK per month
    stockholm_total_people = 669  # Total consultants
    
    print("📊 Stockholm Real Data from Spreadsheet:")
    print("-" * 50)
    print(f"Total Stockholm Monthly Profit: {stockholm_total_monthly_profit:>12,.0f} SEK")
    print(f"Total Stockholm Consultants:    {stockholm_total_people:>3} people")
    print(f"Average Profit per Person:      {stockholm_total_monthly_profit/stockholm_total_people:>10,.0f} SEK")
    
    # Compare with simulation
    print("\n🔍 COMPARISON WITH SIMULATION:")
    print("-" * 50)
    
    # From our debug output
    simulation_total_profit = 73730995  # SEK for entire organization
    simulation_stockholm_estimate = simulation_total_profit * 0.6  # Stockholm is ~60% of org
    
    print(f"Expected Stockholm profit:      {stockholm_total_monthly_profit:>12,.0f} SEK/month")
    print(f"Simulation total profit:        {simulation_total_profit:>12,.0f} SEK/month (ALL offices)")
    print(f"Estimated Stockholm (60%):      {simulation_stockholm_estimate:>12,.0f} SEK/month")
    print(f"Gap:                            {stockholm_total_monthly_profit - simulation_stockholm_estimate:>12,.0f} SEK")
    
    # Calculate the ratio
    ratio = stockholm_total_monthly_profit / simulation_stockholm_estimate
    print(f"Stockholm should be {ratio:.1f}x higher than simulation shows")
    
    print("\n🚨 PROBLEM IDENTIFIED:")
    print("-" * 50)
    print("Stockholm alone should generate 44.8M SEK monthly profit")
    print("But simulation estimates only ~44M SEK for Stockholm (60% of 73.7M total)")
    print("This suggests the simulation is roughly correct in magnitude!")
    
    print("\n🔍 DETAILED ANALYSIS:")
    print("-" * 50)
    
    # Let's check if the issue is in the data interpretation
    # From the spreadsheet, let's extract the actual per-person profits
    stockholm_levels = {
        'A': {'count': 69, 'revenue': 140648, 'cost': 80273},
        'AC': {'count': 54, 'revenue': 142954, 'cost': 86829},
        'C': {'count': 123, 'revenue': 143978, 'cost': 70666},
        'SrC': {'count': 162, 'revenue': 147693, 'cost': 64318},
        'AM': {'count': 178, 'revenue': 157044, 'cost': 62169},
        'M': {'count': 47, 'revenue': 170110, 'cost': 57985},
        'SrM': {'count': 32, 'revenue': 189580, 'cost': 51580},
        'PiP': {'count': 4, 'revenue': 182791, 'cost': 17479}
    }
    
    total_calculated_profit = 0
    total_calculated_revenue = 0
    total_calculated_cost = 0
    
    print("Level | Count | Revenue/person | Cost/person | Profit/person | Total Profit")
    print("-" * 70)
    
    for level, data in stockholm_levels.items():
        count = data['count']
        revenue_per_person = data['revenue']
        cost_per_person = data['cost']
        profit_per_person = revenue_per_person - cost_per_person
        total_profit = profit_per_person * count
        
        total_calculated_profit += total_profit
        total_calculated_revenue += revenue_per_person * count
        total_calculated_cost += cost_per_person * count
        
        print(f"{level:>4} | {count:>5} | {revenue_per_person:>10,} | {cost_per_person:>9,} | {profit_per_person:>11,} | {total_profit:>11,}")
    
    print("-" * 70)
    print(f"TOTAL: {stockholm_total_people:>4} | {total_calculated_revenue:>10,} | {total_calculated_cost:>9,} | {total_calculated_profit//stockholm_total_people:>11,} | {total_calculated_profit:>11,}")
    
    print(f"\nCalculated Stockholm profit: {total_calculated_profit:>12,.0f} SEK/month")
    print(f"Expected Stockholm profit:   {stockholm_total_monthly_profit:>12,.0f} SEK/month")
    print(f"Difference:                  {abs(total_calculated_profit - stockholm_total_monthly_profit):>12,.0f} SEK")

if __name__ == "__main__":
    verify_stockholm_real_data() 