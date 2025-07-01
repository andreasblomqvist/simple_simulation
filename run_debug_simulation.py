#!/usr/bin/env python3
"""
Debug simulation script to capture detailed logging and analyze the bug
"""

import sys
import os
import json
from datetime import datetime

# Add the backend to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.config_service import config_service

def run_debug_simulation():
    """Run a short simulation with debug logging"""
    
    print("🔍 RUNNING DEBUG SIMULATION")
    print("=" * 50)
    
    # Initialize the simulation engine
    engine = SimulationEngine()
    
    # Run a short simulation (3 months) to capture detailed logs
    simulation_params = {
        "start_year": 2025,
        "start_month": 1,
        "end_year": 2025,
        "end_month": 3,  # Only 3 months for debugging
        "price_increase": 0.03,
        "salary_increase": 0.03
    }
    
    print(f"📊 Running simulation: {simulation_params['start_month']}/{simulation_params['start_year']} to {simulation_params['end_month']}/{simulation_params['end_year']}")
    print(f"📁 Debug log will be saved to: debug_simulation_*.log")
    
    try:
        # Run the simulation
        results = engine.run_simulation(**simulation_params)
        
        print("\n✅ Simulation completed successfully!")
        print(f"📊 Results saved to: {results.get('result_file', 'N/A')}")
        
        # Show summary of results
        if 'years' in results:
            print("\n📈 SIMULATION SUMMARY:")
            for year, year_data in results['years'].items():
                print(f"\n  Year {year}:")
                total_fte = 0
                for office_name, office_data in year_data.get('offices', {}).items():
                    office_fte = 0
                    for level_name, level_data in office_data.get('levels', {}).items():
                        fte = level_data.get('fte', 0)
                        office_fte += fte
                        if fte > 0:
                            print(f"    {office_name} - {level_name}: {fte:.1f} FTE")
                    total_fte += office_fte
                    print(f"    {office_name} TOTAL: {office_fte:.1f} FTE")
                print(f"  YEAR {year} TOTAL: {total_fte:.1f} FTE")
        
        # Find the debug log file
        debug_files = [f for f in os.listdir('.') if f.startswith('debug_simulation_') and f.endswith('.log')]
        if debug_files:
            latest_debug_file = max(debug_files, key=os.path.getctime)
            print(f"\n📋 Debug log saved to: {latest_debug_file}")
            print(f"📏 File size: {os.path.getsize(latest_debug_file) / 1024:.1f} KB")
            
            # Show a preview of the debug log
            print(f"\n🔍 DEBUG LOG PREVIEW (first 20 lines):")
            print("-" * 50)
            with open(latest_debug_file, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if i >= 20:
                        print("... (truncated)")
                        break
                    print(line.rstrip())
        
        return results
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    run_debug_simulation() 