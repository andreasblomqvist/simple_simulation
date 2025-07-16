#!/usr/bin/env python3
"""
Comprehensive test for churn fix using real scenario file with all consultant levels
"""
import json
import sys
import os
from typing import Dict, Any
from src.services.scenario_service import ScenarioService
from src.services.config_service import ConfigService
from src.services.simulation_engine import SimulationEngine
from src.services.kpi.kpi_models import EconomicParameters

def test_comprehensive_churn_fix():
    """Test churn fix using scenario with all consultant levels"""
    
    print("COMPREHENSIVE CHURN FIX TEST")
    print("=" * 50)
    print("Using scenario: 4597dfb5-a1ab-463a-932b-da8f0a6df3f3.json")
    print("This scenario has data for ALL consultant levels (A through PiP)")
    print()
    
    # Load the comprehensive scenario
    scenario_file = 'data/scenarios/definitions/4597dfb5-a1ab-463a-932b-da8f0a6df3f3.json'
    with open(scenario_file, 'r') as f:
        scenario_data = json.load(f)
    
    print("SCENARIO OVERVIEW:")
    print(f"Name: {scenario_data['name']}")
    print(f"Office scope: {scenario_data['office_scope']}")
    print(f"Time range: {scenario_data['time_range']['start_year']}-{scenario_data['time_range']['start_month']} to {scenario_data['time_range']['end_year']}-{scenario_data['time_range']['end_month']}")
    print()
    
    # Analyze the expected churn data
    analyze_expected_churn(scenario_data)
    
    # Now test the simulation
    print("\\nRUNNING SIMULATION TEST:")
    print("-" * 30)
    
    try:
        # Create required services
        config_service = ConfigService()
        scenario_service = ScenarioService(config_service)
        
        # Resolve scenario to get offices
        resolved_data = scenario_service.resolve_scenario(scenario_data)
        offices = resolved_data['offices']
        progression_config = resolved_data['progression_config']
        cat_curves = resolved_data['cat_curves']
        
        print(f"✓ Successfully resolved scenario with {len(offices)} offices")
        
        # Create simulation engine
        engine = SimulationEngine()
        
        # Run simulation for just first 6 months to test the fix
        time_range = scenario_data['time_range']
        results = engine.run_simulation_with_offices(
            offices=offices,
            start_year=time_range['start_year'],
            start_month=time_range['start_month'],
            end_year=time_range['start_year'],
            end_month=min(time_range['start_month'] + 5, 12),  # 6 months
            progression_config=progression_config,
            cat_curves=cat_curves,
            economic_params=EconomicParameters()
        )
        
        print("✓ Simulation completed successfully")
        print()
        
        # Analyze results
        analyze_simulation_results(results, scenario_data)
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()

def analyze_expected_churn(scenario_data: Dict[str, Any]):
    """Analyze the expected churn data from the scenario"""
    
    print("EXPECTED CHURN DATA (from scenario file):")
    print("-" * 40)
    
    baseline = scenario_data.get('baseline_input', {}).get('global', {})
    churn_data = baseline.get('churn', {}).get('Consultant', {})
    recruitment_data = baseline.get('recruitment', {}).get('Consultant', {})
    
    print("Consultant levels with churn/recruitment data:")
    for level in ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']:
        churn_monthly = churn_data.get(level, {})
        recruitment_monthly = recruitment_data.get(level, {})
        
        if churn_monthly or recruitment_monthly:
            # Calculate first 6 months
            first_6_months = [f"20250{i}" for i in range(1, 7)]
            
            churn_6months = sum(churn_monthly.get(month, 0) for month in first_6_months)
            recruitment_6months = sum(recruitment_monthly.get(month, 0) for month in first_6_months)
            
            print(f"  {level:4}: {churn_6months:2} churn, {recruitment_6months:2} recruitment (first 6 months)")

def analyze_simulation_results(results: Dict[str, Any], scenario_data: Dict[str, Any]):
    """Analyze the simulation results to validate the churn fix"""
    
    print("SIMULATION RESULTS ANALYSIS:")
    print("-" * 30)
    
    # Get results for 2025
    year_2025 = results.get('years', {}).get('2025', {})
    offices = year_2025.get('offices', {})
    
    if not offices:
        print("❌ No office results found!")
        return
    
    print(f"Found results for {len(offices)} offices:")
    
    total_actual_churn = 0
    total_expected_churn = 0
    total_actual_recruitment = 0
    total_expected_recruitment = 0
    
    for office_name, office_data in offices.items():
        print(f"\\n{office_name}:")
        
        consultant_data = office_data.get('levels', {}).get('Consultant', {})
        
        if not consultant_data:
            print("  No consultant data found")
            continue
        
        office_churn = 0
        office_recruitment = 0
        
        # Check each consultant level
        for level in ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']:
            level_data = consultant_data.get(level, [])
            
            if not level_data:
                continue
            
            # Sum up churn and recruitment across all months for this level
            level_churn = sum(month.get('churn_count', 0) for month in level_data)
            level_recruitment = sum(month.get('recruitment_count', 0) for month in level_data)
            
            if level_churn > 0 or level_recruitment > 0:
                print(f"  {level:4}: {level_churn:2} churn, {level_recruitment:2} recruitment")
                office_churn += level_churn
                office_recruitment += level_recruitment
        
        print(f"  Total: {office_churn:2} churn, {office_recruitment:2} recruitment")
        
        total_actual_churn += office_churn
        total_actual_recruitment += office_recruitment
    
    print(f"\\nOVERALL RESULTS:")
    print(f"  Total actual churn: {total_actual_churn}")
    print(f"  Total actual recruitment: {total_actual_recruitment}")
    
    # Compare with expected (from scenario baseline for first 6 months)
    baseline = scenario_data.get('baseline_input', {}).get('global', {})
    churn_data = baseline.get('churn', {}).get('Consultant', {})
    recruitment_data = baseline.get('recruitment', {}).get('Consultant', {})
    
    first_6_months = [f"20250{i}" for i in range(1, 7)]
    
    expected_churn = 0
    expected_recruitment = 0
    
    for level in ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']:
        level_churn = sum(churn_data.get(level, {}).get(month, 0) for month in first_6_months)
        level_recruitment = sum(recruitment_data.get(level, {}).get(month, 0) for month in first_6_months)
        
        expected_churn += level_churn
        expected_recruitment += level_recruitment
    
    print(f"  Expected churn (6 months): {expected_churn}")
    print(f"  Expected recruitment (6 months): {expected_recruitment}")
    
    print(f"\\nFIX VALIDATION:")
    if total_actual_churn > 0 and expected_churn > 0:
        print("✅ CHURN FIX WORKING: Actual churn > 0, shows fix is effective")
    elif total_actual_churn == 0 and expected_churn > 0:
        print("❌ CHURN FIX ISSUE: Expected churn but got 0")
    elif expected_churn == 0:
        print("ℹ️  No churn expected in this scenario")
    
    if total_actual_recruitment > 0 and expected_recruitment > 0:
        print("✅ RECRUITMENT FIX WORKING: Actual recruitment > 0, shows fix is effective")
    elif total_actual_recruitment == 0 and expected_recruitment > 0:
        print("❌ RECRUITMENT FIX ISSUE: Expected recruitment but got 0")
    elif expected_recruitment == 0:
        print("ℹ️  No recruitment expected in this scenario")

if __name__ == "__main__":
    test_comprehensive_churn_fix()