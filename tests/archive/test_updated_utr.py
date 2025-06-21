#!/usr/bin/env python3
"""
Test the updated 85% UTR to verify all promotions are now profitable
"""

def test_stockholm_with_85_utr():
    """Test Stockholm profit margins with 85% UTR"""
    
    print("💰 STOCKHOLM MARGINS WITH 85% UTR")
    print("=" * 50)
    
    # Stockholm data from config
    stockholm_prices = {
        'A': 1106.61, 'AC': 1114.57, 'C': 1153.80, 'SrC': 1185.03,
        'AM': 1247.87, 'M': 1377.61, 'SrM': 1461.70, 'PiP': 2000.00
    }
    
    stockholm_salaries = {
        'A': 42000, 'AC': 44000, 'C': 48000, 'SrC': 53000,
        'AM': 58000, 'M': 70000, 'SrM': 84000, 'PiP': 90000
    }
    
    # Constants
    working_hours_per_month = 166.4
    utilization = 0.85  # Updated to 85% UTR
    employment_cost_multiplier = 1.40  # 40% employment costs
    
    print(f"📊 Using {utilization*100}% UTR (was 75%)")
    print()
    
    # Calculate margins for each level
    for level, price in stockholm_prices.items():
        salary = stockholm_salaries[level]
        
        # Revenue calculation
        billable_hours = working_hours_per_month * utilization
        monthly_revenue = price * billable_hours
        
        # Cost calculation
        monthly_cost = salary * employment_cost_multiplier
        
        # Profit calculation
        monthly_profit = monthly_revenue - monthly_cost
        margin_percent = (monthly_profit / monthly_revenue) * 100
        
        print(f"{level:3}: {monthly_revenue:8.0f} SEK revenue - {monthly_cost:8.0f} SEK cost = {monthly_profit:8.0f} SEK profit ({margin_percent:5.1f}%)")
    
    print()
    print("🔍 PROMOTION PROFITABILITY:")
    print("-" * 40)
    
    # Check promotion profitability
    promotions = [
        ('A', 'AC'), ('AC', 'C'), ('C', 'SrC'), ('SrC', 'AM'),
        ('AM', 'M'), ('M', 'SrM'), ('SrM', 'PiP')
    ]
    
    for from_level, to_level in promotions:
        # Calculate profit change
        from_profit = (stockholm_prices[from_level] * working_hours_per_month * utilization) - (stockholm_salaries[from_level] * employment_cost_multiplier)
        to_profit = (stockholm_prices[to_level] * working_hours_per_month * utilization) - (stockholm_salaries[to_level] * employment_cost_multiplier)
        
        profit_change = to_profit - from_profit
        status = "✅ PROFITABLE" if profit_change > 0 else "❌ LOSS"
        
        print(f"{from_level} → {to_level}: {profit_change:+8.0f} SEK/month {status}")

if __name__ == "__main__":
    test_stockholm_with_85_utr() 