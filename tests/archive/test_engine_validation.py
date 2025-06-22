#!/usr/bin/env python3
"""
Test script to validate simulation engine basic functionality
Tests with the existing engine to verify it works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.src.services.simulation_engine import SimulationEngine
import random

def test_baseline_simulation():
    """Test engine with default rates (no levers) to check baseline behavior"""
    print("🧪 Testing Baseline Simulation (No Levers)")
    print("=" * 50)
    
    # Seed for reproducible results
    random.seed(42)
    
    # Create engine - it will automatically load real data
    engine = SimulationEngine()
    
    # Get initial state for Stockholm
    stockholm = engine.offices.get('Stockholm')
    if not stockholm:
        print("❌ Stockholm office not found")
        return
    
    initial_consultant_a = stockholm.roles['Consultant']['A'].total if 'A' in stockholm.roles['Consultant'] else 0
    initial_consultant_ac = stockholm.roles['Consultant']['AC'].total if 'AC' in stockholm.roles['Consultant'] else 0
    initial_total = sum(
        level.total for role_data in stockholm.roles.values() 
        for level in (role_data.values() if isinstance(role_data, dict) else [role_data])
    )
    
    print(f"📊 Initial Stockholm State:")
    print(f"   Consultant A: {initial_consultant_a} FTE")
    print(f"   Consultant AC: {initial_consultant_ac} FTE") 
    print(f"   Total FTE: {initial_total}")
    
    # Run simulation for 3 months with no levers (baseline rates)
    results = engine.run_simulation(
        start_year=2025, start_month=1,
        end_year=2025, end_month=3,
        lever_plan=None  # No levers = use default rates
    )
    
    print(f"\n📈 After 3 months simulation (baseline rates):")
    
    # Check final state from results
    final_consultant_a = None
    final_consultant_ac = None
    final_total = 0
    
    # Look for March 2025 results
    if '2025' in results['years'] and 'offices' in results['years']['2025']:
        stockholm_results = results['years']['2025']['offices'].get('Stockholm')
        if stockholm_results and 'levels' in stockholm_results:
            consultant_levels = stockholm_results['levels'].get('Consultant', {})
            
            # Get final values (last entry in each level's list)
            if 'A' in consultant_levels and len(consultant_levels['A']) > 0:
                final_consultant_a = consultant_levels['A'][-1]['total']
            if 'AC' in consultant_levels and len(consultant_levels['AC']) > 0:
                final_consultant_ac = consultant_levels['AC'][-1]['total']
            
            # Calculate total FTE
            for role_name, role_levels in stockholm_results['levels'].items():
                if isinstance(role_levels, dict):  # Roles with levels
                    for level_name, level_data in role_levels.items():
                        if len(level_data) > 0:
                            final_total += level_data[-1]['total']
                elif isinstance(role_levels, list) and len(role_levels) > 0:  # Flat roles
                    final_total += role_levels[-1]['total']
    
    print(f"   Consultant A: {final_consultant_a} FTE")
    print(f"   Consultant AC: {final_consultant_ac} FTE")
    print(f"   Total FTE: {final_total}")
    
    # Analyze results
    if final_consultant_a is not None and final_consultant_ac is not None:
        a_change = final_consultant_a - initial_consultant_a
        ac_change = final_consultant_ac - initial_consultant_ac
        total_change = final_total - initial_total
        
        print(f"\n🔍 Changes Analysis:")
        print(f"   A Level: {initial_consultant_a} → {final_consultant_a} ({a_change:+d})")
        print(f"   AC Level: {initial_consultant_ac} → {final_consultant_ac} ({ac_change:+d})")
        print(f"   Total FTE: {initial_total} → {final_total} ({total_change:+d})")
        
        # Validate growth is reasonable (not explosive)
        growth_rate = (total_change / initial_total * 100) if initial_total > 0 else 0
        print(f"   Growth rate: {growth_rate:.1f}%")
        
        if abs(growth_rate) < 10:  # Less than 10% change in 3 months
            print("✅ Growth appears reasonable")
        else:
            print("❌ Growth appears excessive for 3 months")
            
        # Check if progression is working (AC should increase if A progresses)
        if ac_change > 0 and a_change < ac_change:
            print("✅ Progression appears to be working")
        elif ac_change == 0 and a_change == 0:
            print("⚠️ No progression occurred (may be normal if no evaluation month)")
        else:
            print("❌ Progression behavior unclear")
    else:
        print("❌ Could not extract final results")
    
    return results

def test_zero_lever_simulation():
    """Test engine with zero levers to ensure it produces stable results"""
    print("\n🧪 Testing Zero Levers (Stability Test)")
    print("=" * 50)
    
    # Seed for reproducible results
    random.seed(42)
    
    # Create engine
    engine = SimulationEngine()
    
    # Get initial Stockholm total
    stockholm = engine.offices.get('Stockholm')
    if not stockholm:
        print("❌ Stockholm office not found")
        return
    
    initial_total = sum(
        level.total for role_data in stockholm.roles.values() 
        for level in (role_data.values() if isinstance(role_data, dict) else [role_data])
    )
    
    print(f"📊 Initial Total FTE: {initial_total}")
    
    # Create zero levers for Stockholm Consultant A
    zero_levers = {
        'Stockholm': {
            'Consultant': {
                'A': {
                    'recruitment_1': 0.0, 'recruitment_2': 0.0, 'recruitment_3': 0.0,
                    'churn_1': 0.0, 'churn_2': 0.0, 'churn_3': 0.0,
                    'progression_1': 0.0, 'progression_2': 0.0, 'progression_3': 0.0
                }
            }
        }
    }
    
    # Run simulation for 3 months with zero levers for A level
    results = engine.run_simulation(
        start_year=2025, start_month=1,
        end_year=2025, end_month=3,
        lever_plan=zero_levers
    )
    
    # Check final state
    final_total = 0
    final_a = None
    
    if '2025' in results['years'] and 'offices' in results['years']['2025']:
        stockholm_results = results['years']['2025']['offices'].get('Stockholm')
        if stockholm_results and 'levels' in stockholm_results:
            # Get A level final value
            consultant_levels = stockholm_results['levels'].get('Consultant', {})
            if 'A' in consultant_levels and len(consultant_levels['A']) > 0:
                final_a = consultant_levels['A'][-1]['total']
            
            # Calculate total FTE
            for role_name, role_levels in stockholm_results['levels'].items():
                if isinstance(role_levels, dict):
                    for level_name, level_data in role_levels.items():
                        if len(level_data) > 0:
                            final_total += level_data[-1]['total']
                elif isinstance(role_levels, list) and len(role_levels) > 0:
                    final_total += role_levels[-1]['total']
    
    print(f"📈 After 3 months with zero A levers:")
    print(f"   A Level: {final_a} FTE")
    print(f"   Total FTE: {final_total}")
    
    # Analyze A level stability
    initial_a = stockholm.roles['Consultant']['A'].total if 'A' in stockholm.roles['Consultant'] else 0
    if final_a is not None:
        a_change = final_a - initial_a
        print(f"   A Level change: {a_change:+d}")
        
        if a_change == 0:
            print("✅ Zero levers test PASSED - A level stable")
        else:
            print(f"❌ Zero levers test FAILED - A level changed by {a_change}")
    else:
        print("❌ Could not find A level in results")
    
    return results

def test_simple_lever_simulation():
    """Test engine with simple levers to verify lever application works"""
    print("\n🧪 Testing Simple Levers")
    print("=" * 50)
    
    # Seed for reproducible results
    random.seed(42)
    
    # Create engine
    engine = SimulationEngine()
    
    # Get initial A level
    stockholm = engine.offices.get('Stockholm')
    if not stockholm:
        print("❌ Stockholm office not found")
        return
    
    initial_a = stockholm.roles['Consultant']['A'].total if 'A' in stockholm.roles['Consultant'] else 0
    print(f"📊 Initial A Level: {initial_a} FTE")
    
    # Create simple levers - small recruitment increase for A level
    simple_levers = {
        'Stockholm': {
            'Consultant': {
                'A': {
                    'recruitment_1': 0.1,  # 10% recruitment in January only
                    'recruitment_2': 0.0,
                    'recruitment_3': 0.0,
                    'churn_1': 0.0,        # No churn
                    'churn_2': 0.0,
                    'churn_3': 0.0,
                    'progression_1': 0.0,  # No progression
                    'progression_2': 0.0,
                    'progression_3': 0.0
                }
            }
        }
    }
    
    # Run simulation
    results = engine.run_simulation(
        start_year=2025, start_month=1,
        end_year=2025, end_month=3,
        lever_plan=simple_levers
    )
    
    # Check final A level
    final_a = None
    if '2025' in results['years'] and 'offices' in results['years']['2025']:
        stockholm_results = results['years']['2025']['offices'].get('Stockholm')
        if stockholm_results and 'levels' in stockholm_results:
            consultant_levels = stockholm_results['levels'].get('Consultant', {})
            if 'A' in consultant_levels and len(consultant_levels) > 0:
                final_a = consultant_levels['A'][-1]['total']
    
    print(f"📈 After simple levers (10% recruitment in Jan):")
    print(f"   A Level: {final_a} FTE")
    
    if final_a is not None:
        a_change = final_a - initial_a
        expected_recruits = int(initial_a * 0.1)  # 10% of initial
        
        print(f"   A Level change: {a_change:+d}")
        print(f"   Expected recruits: ~{expected_recruits}")
        
        if a_change > 0 and a_change <= expected_recruits + 2:  # Allow some variance
            print("✅ Simple levers test PASSED - recruitment working")
        else:
            print(f"❌ Simple levers test FAILED - unexpected change")
    else:
        print("❌ Could not find A level in results")
    
    return results

if __name__ == "__main__":
    print("🔧 Simulation Engine Validation Tests")
    print("=" * 60)
    
    # Test 1: Baseline simulation
    test_baseline_simulation()
    
    # Test 2: Zero levers stability
    test_zero_lever_simulation()
    
    # Test 3: Simple levers functionality
    test_simple_lever_simulation()
    
    print("\n" + "=" * 60)
    print("✅ Engine validation tests completed!") 