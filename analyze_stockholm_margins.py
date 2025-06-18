#!/usr/bin/env python3
"""
Analyze Stockholm profit margins to see if promotions should be profitable
"""

def analyze_stockholm_margins():
    """Analyze profit margins for Stockholm levels"""
    
    print("💰 STOCKHOLM PROFIT MARGIN ANALYSIS")
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
    utilization = 0.95  # 95%
    employment_cost_multiplier = 1.40  # 40% employment costs
    billable_hours = working_hours_per_month * utilization
    
    print("📊 INDIVIDUAL LEVEL ANALYSIS:")
    print("-" * 40)
    
    margins = {}
    
    for level in stockholm_prices.keys():
        price = stockholm_prices[level]
        salary = stockholm_salaries[level]
        
        # Monthly calculations
        monthly_revenue = price * billable_hours
        monthly_cost = salary * employment_cost_multiplier
        monthly_profit = monthly_revenue - monthly_cost
        margin_percent = (monthly_profit / monthly_revenue) * 100
        
        margins[level] = {
            'revenue': monthly_revenue,
            'cost': monthly_cost,
            'profit': monthly_profit,
            'margin': margin_percent
        }
        
        print(f"{level:>3}: {price:>7.0f} SEK/h × {billable_hours:>5.1f}h = {monthly_revenue:>8.0f} SEK revenue")
        print(f"     {salary:>7.0f} SEK/m × {employment_cost_multiplier:>4.2f} = {monthly_cost:>8.0f} SEK cost")
        print(f"     Profit: {monthly_profit:>8.0f} SEK ({margin_percent:>5.1f}% margin)")
        print()
    
    print("🔄 PROMOTION IMPACT ANALYSIS:")
    print("-" * 40)
    
    promotions = [
        ('A', 'AC'), ('AC', 'C'), ('C', 'SrC'), ('SrC', 'AM'),
        ('AM', 'M'), ('M', 'SrM'), ('SrM', 'PiP')
    ]
    
    for from_level, to_level in promotions:
        from_data = margins[from_level]
        to_data = margins[to_level]
        
        revenue_change = to_data['revenue'] - from_data['revenue']
        cost_change = to_data['cost'] - from_data['cost']
        profit_change = to_data['profit'] - from_data['profit']
        
        print(f"{from_level} → {to_level}:")
        print(f"  Revenue change: {revenue_change:>+8.0f} SEK/month")
        print(f"  Cost change:    {cost_change:>+8.0f} SEK/month")
        print(f"  Profit change:  {profit_change:>+8.0f} SEK/month")
        
        if profit_change > 0:
            print(f"  ✅ PROFITABLE promotion (+{profit_change:,.0f} SEK/month)")
        else:
            print(f"  ❌ UNPROFITABLE promotion ({profit_change:,.0f} SEK/month)")
        print()
    
    print("🎯 KEY INSIGHTS:")
    print("-" * 20)
    
    profitable_promotions = sum(1 for from_level, to_level in promotions 
                               if margins[to_level]['profit'] > margins[from_level]['profit'])
    
    print(f"• Profitable promotions: {profitable_promotions}/{len(promotions)}")
    
    # Find the problematic promotions
    unprofitable = []
    for from_level, to_level in promotions:
        if margins[to_level]['profit'] <= margins[from_level]['profit']:
            unprofitable.append(f"{from_level}→{to_level}")
    
    if unprofitable:
        print(f"• Unprofitable promotions: {', '.join(unprofitable)}")
    else:
        print("• All promotions are profitable!")
    
    # Show margin ranges
    min_margin = min(data['margin'] for data in margins.values())
    max_margin = max(data['margin'] for data in margins.values())
    print(f"• Margin range: {min_margin:.1f}% to {max_margin:.1f}%")
    
    return margins

if __name__ == "__main__":
    analyze_stockholm_margins() 