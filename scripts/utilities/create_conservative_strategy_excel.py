#!/usr/bin/env python3
"""
Create a conservative strategy Excel file with realistic recruitment/churn rates
Goal: Achieve 50% Journey 1 over 3-4 years without breaking financial model
"""

import pandas as pd
from datetime import datetime

def create_conservative_strategy():
    """Create conservative strategy with small rate adjustments"""
    
    print("📊 Creating Conservative Journey 1 Strategy")
    print("=" * 50)
    
    # Conservative strategy: Small incremental changes
    # Current Journey 1: 40.7% (750 FTE out of 1,842)
    # Target Journey 1: 50.0% (921 FTE)
    # Gap: 171 FTE (9.3%)
    
    # Strategy: Gradual 3-4 year approach with small monthly increases
    
    offices = ['Stockholm', 'Oslo', 'Copenhagen', 'Helsinki', 'Munich', 
               'Zurich', 'Amsterdam', 'Berlin', 'Frankfurt', 'Hamburg', 'Cologne']
    
    roles = ['Consultant', 'Sales', 'Recruitment', 'Operations']
    levels = ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']
    
    config_data = []
    
    for office in offices:
        for role in roles:
            for level in levels:
                # Base rates (current default rates from engine)
                base_recruitment = 0.02  # 2% baseline
                base_churn = 0.015       # 1.5% baseline
                
                # Conservative Journey 1 enhancement
                if level in ['A', 'AC', 'C']:  # Journey 1 levels
                    if level == 'A':
                        # Slight boost to A-level recruitment
                        recruitment_rate = 0.025  # +0.5% (2.5% total)
                        churn_rate = 0.014        # -0.1% (1.4% total)
                    elif level == 'AC':
                        # Moderate boost to AC recruitment  
                        recruitment_rate = 0.023  # +0.3% (2.3% total)
                        churn_rate = 0.014        # -0.1% (1.4% total)
                    else:  # C level
                        # Small boost to C recruitment
                        recruitment_rate = 0.021  # +0.1% (2.1% total)
                        churn_rate = 0.015        # Same (1.5% total)
                
                elif level in ['SrC', 'AM']:  # Journey 2 levels
                    # Slight increase in churn to create space
                    recruitment_rate = 0.018   # -0.2% (1.8% total)
                    churn_rate = 0.017         # +0.2% (1.7% total)
                
                elif level in ['M', 'SrM']:  # Journey 3 levels
                    # Small increase in churn
                    recruitment_rate = 0.015   # -0.5% (1.5% total)
                    churn_rate = 0.018         # +0.3% (1.8% total)
                
                else:  # PiP (Journey 4)
                    # Minimal change
                    recruitment_rate = 0.012   # -0.8% (1.2% total)
                    churn_rate = 0.016         # +0.1% (1.6% total)
                
                # Create monthly rates (same for all months - no seasonality)
                monthly_recruitment = [recruitment_rate] * 12
                monthly_churn = [churn_rate] * 12
                monthly_progression = [0.0] * 12  # Will be handled by CAT system
                
                # Get FTE from baseline (simplified - using Stockholm as reference)
                if office == 'Stockholm':
                    fte_map = {
                        'A': 69, 'AC': 73, 'C': 89, 'SrC': 95,
                        'AM': 78, 'M': 67, 'SrM': 45, 'PiP': 25
                    }
                    fte = fte_map.get(level, 10)
                else:
                    # Scale other offices proportionally
                    scale_factors = {
                        'Oslo': 0.6, 'Copenhagen': 0.4, 'Helsinki': 0.3,
                        'Munich': 0.25, 'Zurich': 0.2, 'Amsterdam': 0.15,
                        'Berlin': 0.1, 'Frankfurt': 0.08, 'Hamburg': 0.06, 'Cologne': 0.05
                    }
                    base_fte = {'A': 69, 'AC': 73, 'C': 89, 'SrC': 95,
                               'AM': 78, 'M': 67, 'SrM': 45, 'PiP': 25}.get(level, 10)
                    fte = max(1, int(base_fte * scale_factors.get(office, 0.1)))
                
                # Create row
                row = {
                    'Office': office,
                    'Role': role,
                    'Level': level,
                    'FTE': fte
                }
                
                # Add monthly columns
                for i in range(1, 13):
                    row[f'Recruitment_{i}'] = monthly_recruitment[i-1]
                    row[f'Churn_{i}'] = monthly_churn[i-1]
                    row[f'Progression_{i}'] = monthly_progression[i-1]
                
                config_data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(config_data)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conservative_strategy_{timestamp}.xlsx"
    
    # Save to Excel
    df.to_excel(filename, index=False)
    
    print(f"✅ Conservative strategy saved to: {filename}")
    print(f"📊 Total configurations: {len(config_data)}")
    
    # Print strategy summary
    print("\n🎯 Conservative Strategy Summary:")
    print("=" * 40)
    print("Journey 1 Enhancements:")
    print("  • A level: 2.5% recruitment (+0.5%), 1.4% churn (-0.1%)")
    print("  • AC level: 2.3% recruitment (+0.3%), 1.4% churn (-0.1%)")
    print("  • C level: 2.1% recruitment (+0.1%), 1.5% churn (same)")
    print("\nSenior Level Adjustments:")
    print("  • SrC/AM: 1.8% recruitment (-0.2%), 1.7% churn (+0.2%)")
    print("  • M/SrM: 1.5% recruitment (-0.5%), 1.8% churn (+0.3%)")
    print("  • PiP: 1.2% recruitment (-0.8%), 1.6% churn (+0.1%)")
    print("\n🎯 Expected Outcome:")
    print("  • Gradual Journey 1 increase over 3-4 years")
    print("  • Sustainable financial performance")
    print("  • Realistic growth rates")
    
    return filename

if __name__ == "__main__":
    filename = create_conservative_strategy()
    print(f"\n✅ Ready to import: {filename}") 