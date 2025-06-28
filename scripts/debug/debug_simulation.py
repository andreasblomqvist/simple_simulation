#!/usr/bin/env python3
"""
Debug script to test simulation engine directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.config_service import config_service

def debug_simulation():
    """Debug the simulation engine directly"""
    
    print("🔍 Debugging simulation engine...")
    
    # Create simulation engine
    engine = SimulationEngine()
    
    # Check if engine is initialized
    print(f"✅ Engine created: {engine is not None}")
    
    # Check offices
    print(f"🏢 Number of offices: {len(engine.offices) if hasattr(engine, 'offices') else 'No offices attribute'}")
    
    if hasattr(engine, 'offices') and engine.offices:
        print(f"🏢 Office names: {list(engine.offices.keys())}")
        
        # Check first office
        first_office_name = list(engine.offices.keys())[0]
        first_office = engine.offices[first_office_name]
        print(f"🏢 First office ({first_office_name}):")
        print(f"  - Total FTE: {first_office.total_fte}")
        print(f"  - Journey: {first_office.journey}")
        print(f"  - Roles: {list(first_office.roles.keys())}")
        
        # Check Consultant role
        if 'Consultant' in first_office.roles:
            consultant_roles = first_office.roles['Consultant']
            print(f"  - Consultant levels: {list(consultant_roles.keys())}")
            
            # Check first level
            if consultant_roles:
                first_level_name = list(consultant_roles.keys())[0]
                first_level = consultant_roles[first_level_name]
                print(f"  - Level {first_level_name}:")
                print(f"    - FTE: {first_level.total if hasattr(first_level, 'total') else 'No total'}")
                print(f"    - People: {len(first_level.people) if hasattr(first_level, 'people') else 'No people'}")
                print(f"    - Recruitment rate: {getattr(first_level, 'recruitment_1', 'N/A')}")
                print(f"    - Churn rate: {getattr(first_level, 'churn_1', 'N/A')}")
    
    # Try to run a simple simulation
    print("\n🚀 Running simple simulation...")
    
    try:
        results = engine.run_simulation(
            start_year=2025,
            start_month=1,
            end_year=2025,
            end_month=12,
            price_increase=0.02,
            salary_increase=0.02
        )
        
        print(f"✅ Simulation completed!")
        print(f"📋 Result keys: {list(results.keys())}")
        
        if 'years' in results:
            years = results['years']
            print(f"📅 Years: {list(years.keys())}")
            
            if years:
                first_year = list(years.keys())[0]
                year_data = years[first_year]
                print(f"📊 Year {first_year} keys: {list(year_data.keys())}")
                
                if 'offices' in year_data:
                    offices = year_data['offices']
                    print(f"🏢 Offices in results: {list(offices.keys())}")
                    
                    if offices:
                        first_office_name = list(offices.keys())[0]
                        office_data = offices[first_office_name]
                        print(f"🏢 First office data: {list(office_data.keys())}")
                    else:
                        print("❌ No offices in results!")
                        
                        # Debug: Check what's in the year_data
                        print(f"🔍 Year data content: {year_data}")
                else:
                    print("❌ No 'offices' key in year data!")
                    print(f"🔍 Year data content: {year_data}")
        else:
            print("❌ No 'years' key in results!")
            
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_simulation() 