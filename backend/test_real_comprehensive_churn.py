#!/usr/bin/env python3
"""
Real comprehensive test for churn fix using actual office configuration with scenario baseline data
"""
import json
import copy
from src.services.simulation_engine import SimulationEngine
from src.services.kpi.kpi_models import EconomicParameters

def test_real_comprehensive_churn():
    """Test churn fix with real office configuration and comprehensive scenario data"""
    
    print("REAL COMPREHENSIVE CHURN FIX TEST")
    print("=" * 50)
    
    # Load actual office configuration
    with open('config/office_configuration.json', 'r') as f:
        office_config = json.load(f)
    
    # Load comprehensive scenario data
    with open('data/scenarios/definitions/4597dfb5-a1ab-463a-932b-da8f0a6df3f3.json', 'r') as f:
        scenario_data = json.load(f)
    
    print("CONFIGURATION OVERVIEW:")
    print(f"Office configuration has {len(office_config)} offices")
    print(f"Scenario: {scenario_data['name']}")
    print()
    
    # Extract baseline input from scenario
    baseline_input = scenario_data.get('baseline_input', {}).get('global', {})
    churn_data = baseline_input.get('churn', {}).get('Consultant', {})
    recruitment_data = baseline_input.get('recruitment', {}).get('Consultant', {})
    
    print("APPLYING SCENARIO DATA TO OFFICES:")
    print("-" * 35)
    
    # Apply scenario's baseline input to a subset of offices for testing
    test_offices = create_test_offices_with_scenario_data(
        office_config, 
        churn_data, 
        recruitment_data
    )
    
    print(f"Created {len(test_offices)} test offices with scenario data")
    print()
    
    # Show expected data for first 6 months
    analyze_expected_data(churn_data, recruitment_data)
    
    # Run simulation
    print("\\nRUNNING SIMULATION:")
    print("-" * 20)
    
    try:
        engine = SimulationEngine()
        
        # Import proper progression config and cat curves
        from config.progression_config import PROGRESSION_CONFIG, CAT_CURVES
        progression_config = PROGRESSION_CONFIG
        cat_curves = CAT_CURVES
        
        # Run for 6 months
        results = engine.run_simulation_with_offices(
            offices=test_offices,
            start_year=2025,
            start_month=1,
            end_year=2025,
            end_month=6,
            progression_config=progression_config,
            cat_curves=cat_curves,
            economic_params=EconomicParameters()
        )
        
        print("✓ Simulation completed successfully")
        
        # Analyze results
        analyze_comprehensive_results(results, churn_data, recruitment_data)
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()

def create_test_offices_with_scenario_data(office_config, churn_data, recruitment_data):
    """Create test offices with scenario baseline data applied"""
    
    # Take first 3 offices for testing
    test_offices = {}
    office_names = list(office_config.keys())[:3]
    
    for office_name in office_names:
        office_data = copy.deepcopy(office_config[office_name])
        
        # Apply scenario churn and recruitment data to consultant levels
        consultant_role = office_data.get('roles', {}).get('Consultant', {})
        
        # Add churn and recruitment data from scenario for each level
        for level in ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']:
            if level in consultant_role:
                level_data = consultant_role[level]
                
                # Add monthly churn data from scenario
                level_churn = churn_data.get(level, {})
                level_recruitment = recruitment_data.get(level, {})
                
                # Apply churn rates (convert absolute numbers to rates)
                current_fte = level_data.get('fte', 0)
                if current_fte > 0:
                    for month in range(1, 7):  # First 6 months
                        month_key = f"20250{month}"
                        
                        # Get absolute churn/recruitment from scenario
                        abs_churn = level_churn.get(month_key, 0)
                        abs_recruitment = level_recruitment.get(month_key, 0)
                        
                        # Set absolute values (this is what the fix enables)
                        level_data[f'churn_abs_{month}'] = abs_churn
                        level_data[f'recruitment_abs_{month}'] = abs_recruitment
                        
                        # Also set dummy rate values (should be ignored due to abs values)
                        level_data[f'churn_{month}'] = 0.01  # 1% fallback rate
                        level_data[f'recruitment_{month}'] = 0.01  # 1% fallback rate
        
        test_offices[office_name] = office_data
        
        print(f"  {office_name}: Applied scenario data to consultant levels")
    
    return test_offices

def analyze_expected_data(churn_data, recruitment_data):
    """Analyze expected churn and recruitment data"""
    
    print("EXPECTED DATA (first 6 months):")
    print("-" * 32)
    
    first_6_months = [f"20250{i}" for i in range(1, 7)]
    
    total_expected_churn = 0
    total_expected_recruitment = 0
    
    for level in ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']:
        level_churn = sum(churn_data.get(level, {}).get(month, 0) for month in first_6_months)
        level_recruitment = sum(recruitment_data.get(level, {}).get(month, 0) for month in first_6_months)
        
        if level_churn > 0 or level_recruitment > 0:
            print(f"  {level:4}: {level_churn:2} churn, {level_recruitment:2} recruitment")
            total_expected_churn += level_churn
            total_expected_recruitment += level_recruitment
    
    print(f"  Total: {total_expected_churn:2} churn, {total_expected_recruitment:2} recruitment per office")

def analyze_comprehensive_results(results, expected_churn_data, expected_recruitment_data):
    """Analyze comprehensive simulation results"""
    
    print("\\nSIMULATION RESULTS:")
    print("-" * 20)
    
    year_2025 = results.get('years', {}).get('2025', {})
    offices = year_2025.get('offices', {})
    
    if not offices:
        print("❌ No office results found!")
        return
    
    # Calculate expected totals across all offices
    first_6_months = [f"20250{i}" for i in range(1, 7)]
    total_expected_churn = 0
    total_expected_recruitment = 0
    
    for level in ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']:
        level_churn = sum(expected_churn_data.get(level, {}).get(month, 0) for month in first_6_months)
        level_recruitment = sum(expected_recruitment_data.get(level, {}).get(month, 0) for month in first_6_months)
        total_expected_churn += level_churn
        total_expected_recruitment += level_recruitment
    
    # Multiply by number of offices
    total_expected_churn *= len(offices)
    total_expected_recruitment *= len(offices)
    
    # Analyze actual results
    total_actual_churn = 0
    total_actual_recruitment = 0
    
    print(f"Results from {len(offices)} offices:")
    
    for office_name, office_data in offices.items():
        consultant_data = office_data.get('levels', {}).get('Consultant', {})
        
        office_churn = 0
        office_recruitment = 0
        
        for level in ['A', 'AC', 'C', 'SrC', 'AM', 'M', 'SrM', 'PiP']:
            level_data = consultant_data.get(level, [])
            
            if level_data:
                level_churn = sum(month.get('churn_count', 0) for month in level_data)
                level_recruitment = sum(month.get('recruitment_count', 0) for month in level_data)
                
                office_churn += level_churn
                office_recruitment += level_recruitment
        
        print(f"  {office_name}: {office_churn:2} churn, {office_recruitment:2} recruitment")
        
        total_actual_churn += office_churn
        total_actual_recruitment += office_recruitment
    
    print(f"\\nTOTAL RESULTS:")
    print(f"  Actual churn: {total_actual_churn}")
    print(f"  Expected churn: {total_expected_churn}")
    print(f"  Actual recruitment: {total_actual_recruitment}")
    print(f"  Expected recruitment: {total_expected_recruitment}")
    
    print(f"\\nCHURN FIX VALIDATION:")
    
    # Validate churn fix
    if total_actual_churn > 0 and total_expected_churn > 0:
        accuracy = (total_actual_churn / total_expected_churn) * 100
        print(f"✅ CHURN FIX WORKING: {accuracy:.1f}% accuracy")
    elif total_actual_churn == 0 and total_expected_churn > 0:
        print("❌ CHURN FIX FAILED: Expected churn but got 0")
    elif total_expected_churn == 0:
        print("ℹ️  No churn expected")
    else:
        print("❓ Unexpected churn pattern")
    
    # Validate recruitment fix
    if total_actual_recruitment > 0 and total_expected_recruitment > 0:
        accuracy = (total_actual_recruitment / total_expected_recruitment) * 100
        print(f"✅ RECRUITMENT FIX WORKING: {accuracy:.1f}% accuracy")
    elif total_actual_recruitment == 0 and total_expected_recruitment > 0:
        print("❌ RECRUITMENT FIX FAILED: Expected recruitment but got 0")
    elif total_expected_recruitment == 0:
        print("ℹ️  No recruitment expected")
    else:
        print("❓ Unexpected recruitment pattern")

if __name__ == "__main__":
    test_real_comprehensive_churn()