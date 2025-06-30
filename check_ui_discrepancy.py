#!/usr/bin/env python3
"""
Check discrepancy between simulation engine and UI FTE values
"""

import sys
sys.path.append('.')
from backend.src.services.simulation_engine import SimulationEngine

def check_ui_discrepancy():
    """Check the discrepancy between simulation engine and UI FTE values"""
    
    print("🔍 UI vs SIMULATION ENGINE FTE DISCREPANCY")
    print("=" * 50)
    
    # Run simulation
    engine = SimulationEngine()
    results = engine.run_simulation(2025, 1, 2028, 12)
    
    # Get simulation FTE for 2028
    simulation_fte = results['years']['2028'].get('total_fte', 0)
    print(f"📊 Simulation Engine FTE (2028): {simulation_fte}")
    
    # Get engine internal FTE
    engine_fte = sum(office.total_fte for office in engine.offices.values())
    print(f"🔧 Engine Internal FTE: {engine_fte}")
    
    # UI reported FTE
    ui_fte = 1893
    print(f"🖥️  UI Reported FTE: {ui_fte}")
    
    print("\n📈 Comparison:")
    print(f"  Simulation vs Engine: {simulation_fte} vs {engine_fte}")
    print(f"  Simulation vs UI: {simulation_fte} vs {ui_fte}")
    print(f"  Engine vs UI: {engine_fte} vs {ui_fte}")
    
    # Calculate differences
    sim_ui_diff = ui_fte - simulation_fte
    engine_ui_diff = ui_fte - engine_fte
    
    print(f"\n❓ Discrepancies:")
    print(f"  UI - Simulation: {sim_ui_diff} ({sim_ui_diff:+d})")
    print(f"  UI - Engine: {engine_ui_diff} ({engine_ui_diff:+d})")
    
    # Check if they match
    if simulation_fte == engine_fte:
        print("✅ Simulation and Engine FTE match")
    else:
        print("❌ Simulation and Engine FTE don't match")
    
    if simulation_fte == ui_fte:
        print("✅ Simulation and UI FTE match")
    else:
        print("❌ Simulation and UI FTE don't match")
    
    if engine_fte == ui_fte:
        print("✅ Engine and UI FTE match")
    else:
        print("❌ Engine and UI FTE don't match")
    
    # Office breakdown
    print(f"\n🏢 Office Breakdown (Engine Internal):")
    for name, office in engine.offices.items():
        print(f"  {name}: {office.total_fte}")
    
    total_from_breakdown = sum(office.total_fte for office in engine.offices.values())
    print(f"  Total from breakdown: {total_from_breakdown}")

if __name__ == "__main__":
    check_ui_discrepancy() 