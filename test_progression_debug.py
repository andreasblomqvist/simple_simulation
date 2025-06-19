#!/usr/bin/env python3
"""
Debug script to test progression specifically in January and June
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.src.services.simulation_engine import SimulationEngine

def test_progression_in_jan_june():
    """Test progression specifically in January and June"""
    print("🔍 Testing Progression in January and June")
    print("=" * 50)
    
    # Initialize simulation engine (uses real headcount data)
    engine = SimulationEngine()
    
    print("📊 Running simulation for 2025...")
    print()
    
    # Run simulation for full year 2025
    results = engine.run_simulation(
        start_year=2025, start_month=1,
        end_year=2025, end_month=12
    )
    
    print("📈 Month-by-Month Progression Analysis:")
    print("-" * 60)
    
    if not results or '2025' not in results.get('years', {}):
        print("❌ No simulation results found for 2025")
        return
    
    year_2025 = results['years']['2025']
    
    # Analyze progression data month by month across all offices and roles
    monthly_progression = {}
    for month in range(1, 13):
        monthly_progression[month] = {'progressed_out': 0, 'progressed_in': 0}
    
    # Process all offices
    for office_name, office_data in year_2025.get('offices', {}).items():
        if 'levels' not in office_data:
            continue
            
        # Process all roles with levels (Consultant, Sales, Recruitment)
        for role_name, role_data in office_data['levels'].items():
            if not isinstance(role_data, dict):
                continue
                
            # Process all levels within the role
            for level_name, level_data in role_data.items():
                if not isinstance(level_data, list) or len(level_data) != 12:
                    continue
                
                # Check each month (index 0 = January, index 11 = December)
                for month_index, period_data in enumerate(level_data):
                    month = month_index + 1  # Convert to 1-based month
                    
                    progressed_out = period_data.get('progressed_out', 0)
                    progressed_in = period_data.get('progressed_in', 0)
                    
                    if progressed_out > 0 or progressed_in > 0:
                        monthly_progression[month]['progressed_out'] += progressed_out
                        monthly_progression[month]['progressed_in'] += progressed_in
                        
                        # Show specific details for January and June
                        if month in [1, 6]:
                            print(f"    📍 {office_name} {role_name} {level_name} - Month {month}")
                            print(f"       Progressed Out: {progressed_out}, Progressed In: {progressed_in}")
    
    # Summary by month
    print("\n📊 Monthly Progression Summary:")
    for month in range(1, 13):
        month_name = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][month-1]
        
        prog_out = monthly_progression[month]['progressed_out']
        prog_in = monthly_progression[month]['progressed_in']
        
        if prog_out > 0 or prog_in > 0:
            print(f"  {month_name} 2025: {prog_out} progressed out, {prog_in} progressed in")
        else:
            print(f"  {month_name} 2025: No progression")
    
    # Highlight expected progression months
    print("\n💡 Expected Progression Months: January and June")
    jan_prog = monthly_progression[1]['progressed_out'] + monthly_progression[1]['progressed_in']
    jun_prog = monthly_progression[6]['progressed_out'] + monthly_progression[6]['progressed_in']
    print(f"   January total progression: {jan_prog}")
    print(f"   June total progression: {jun_prog}")
    
    print()
    
    # Check final FTE counts
    print("🎯 Final FTE Counts by Level:")
    if results and 'years' in results:
        # Get the 2025 year data
        year_2025 = results['years'].get('2025', {})
        if 'offices' in year_2025:
            for office_name, office_data in year_2025['offices'].items():
                if office_name == 'Stockholm':  # Focus on Stockholm
                    print(f"  {office_name}:")
                    if 'levels' in office_data:
                        for role_name, role_data in office_data['levels'].items():
                            if role_name == 'Consultant':  # Focus on Consultant
                                for level_name, level_data in role_data.items():
                                    if level_name in ['C', 'SrC']:  # Focus on C and SrC
                                        # Get final month data (December)
                                        if level_data and len(level_data) > 0:
                                            final_fte = level_data[-1].get('total', 0)
                                            print(f"    {role_name} {level_name}: {final_fte} FTE")
    
    # Check progression rates configuration
    print("\n🔧 Progression Configuration Check:")
    from backend.config.default_config import DEFAULT_RATES
    progression_config = DEFAULT_RATES['progression']
    print(f"   Evaluation months: {progression_config['evaluation_months']}")
    print(f"   Base progression rates:")
    for transition, rate in progression_config['base_rates'].items():
        print(f"     {transition}: {rate*100:.1f}% per year")
    
    print(f"\n📋 Simulation completed successfully!")
    if jan_prog > 0 or jun_prog > 0:
        print("✅ Progression detected in expected months!")
    else:
        print("⚠️  No progression detected - this might indicate an issue with progression logic")

if __name__ == "__main__":
    test_progression_in_jan_june() 