#!/usr/bin/env python3
"""
Comprehensive test for churn fix using real scenario files and multiple offices
"""
import json
import os
from glob import glob
from src.services.simulation_engine import SimulationEngine
from src.services.scenario_service import ScenarioService
from src.services.kpi import EconomicParameters

def test_churn_with_real_scenarios():
    """Test churn calculations with real scenario files"""
    
    print("Testing churn fix with real scenario files")
    print("=" * 50)
    
    # Find scenario files
    scenario_files = glob('data/scenarios/definitions/*.json')
    if not scenario_files:
        print("No scenario files found!")
        return
    
    # Test with first few scenarios
    for i, scenario_file in enumerate(scenario_files[:3]):
        print(f"\nTesting scenario {i+1}: {os.path.basename(scenario_file)}")
        print("-" * 40)
        
        try:
            # Load scenario
            with open(scenario_file, 'r') as f:
                scenario_data = json.load(f)
            
            # Check if it has multiple offices
            office_scope = scenario_data.get('office_scope', [])
            print(f"Office scope: {office_scope}")
            
            # Create scenario service to resolve the scenario
            scenario_service = ScenarioService()
            
            # Try to resolve and run simulation
            try:
                resolved_data = scenario_service.resolve_scenario(scenario_data)
                offices = resolved_data.get('offices', {})
                
                if not offices:
                    print("  ⚠️  No offices resolved from scenario")
                    continue
                
                print(f"  ✓ Resolved {len(offices)} offices: {list(offices.keys())}")
                
                # Create engine and run simulation
                engine = SimulationEngine()
                
                # Extract time range
                time_range = scenario_data.get('time_range', {})
                if not time_range:
                    print("  ⚠️  No time range in scenario")
                    continue
                
                # Run simulation with offices
                results = engine.run_simulation_with_offices(
                    offices=offices,
                    start_year=time_range.get('start_year', 2025),
                    start_month=time_range.get('start_month', 1),
                    end_year=time_range.get('start_year', 2025),  # Just first year
                    end_month=min(time_range.get('start_month', 1) + 5, 12),  # 6 months max
                    economic_params=EconomicParameters()
                )
                
                # Analyze churn across all offices
                analyze_churn_results(results, scenario_data['name'])
                
            except Exception as e:
                print(f"  ❌ Error running simulation: {e}")
                continue
                
        except Exception as e:
            print(f"  ❌ Error loading scenario: {e}")
            continue

def analyze_churn_results(results, scenario_name):
    """Analyze churn results across all offices"""
    
    print(f"  Churn analysis for '{scenario_name}':")
    
    total_churn_events = 0
    total_expected_churn = 0.0
    
    # Check each office
    for year, year_data in results.get('years', {}).items():
        for office_name, office_data in year_data.get('offices', {}).items():
            print(f"    {office_name}:")
            
            # Check each role and level
            for role_name, role_data in office_data.get('levels', {}).items():
                for level_name, level_months in role_data.items():
                    if isinstance(level_months, list) and level_months:
                        # Calculate totals for this level
                        level_churn_events = sum(month.get('churn_count', 0) for month in level_months)
                        level_expected_churn = sum(
                            month.get('churn_rate', 0) * month.get('fte', 0) 
                            for month in level_months
                        )
                        
                        if level_churn_events > 0 or level_expected_churn > 0.1:
                            print(f"      {role_name}.{level_name}: {level_churn_events} churn events, expected {level_expected_churn:.2f}")
                        
                        total_churn_events += level_churn_events
                        total_expected_churn += level_expected_churn
    
    print(f"    TOTAL: {total_churn_events} churn events, expected {total_expected_churn:.2f}")
    
    # Validation
    if total_expected_churn > 1 and total_churn_events == 0:
        print("    ❌ Expected churn but got 0 - potential issue!")
    elif total_expected_churn > 1 and total_churn_events > 0:
        print("    ✅ Churn working as expected")
    elif total_expected_churn < 1:
        print("    ℹ️  Low expected churn - integer truncation is normal")
    
    return total_churn_events, total_expected_churn

def test_churn_with_high_rates():
    """Test churn with artificially high rates to verify the fix works"""
    
    print("\n" + "=" * 50)
    print("Testing churn fix with high churn rates")
    print("=" * 50)
    
    # Create test config with high churn rates
    test_config = {
        "Stockholm": {
            "name": "Stockholm",
            "total_fte": 100,
            "journey": "Mature Office",
            "roles": {
                "Consultant": {
                    "A": {
                        "fte": 50,
                        "churn_1": 0.02,  # 2% monthly = 1 person
                        "churn_2": 0.04,  # 4% monthly = 2 people
                        "churn_3": 0.06,  # 6% monthly = 3 people
                        "recruitment_1": 0.0, "recruitment_2": 0.0, "recruitment_3": 0.0,
                        "price_1": 1000, "price_2": 1000, "price_3": 1000,
                        "salary_1": 50000, "salary_2": 50000, "salary_3": 50000,
                        "utr_1": 0.85, "utr_2": 0.85, "utr_3": 0.85
                    }
                }
            }
        },
        "Berlin": {
            "name": "Berlin",
            "total_fte": 80,
            "journey": "Growing Office",
            "roles": {
                "Consultant": {
                    "A": {
                        "fte": 40,
                        "churn_1": 0.025,  # 2.5% monthly = 1 person
                        "churn_2": 0.05,   # 5% monthly = 2 people
                        "churn_3": 0.075,  # 7.5% monthly = 3 people
                        "recruitment_1": 0.0, "recruitment_2": 0.0, "recruitment_3": 0.0,
                        "price_1": 900, "price_2": 900, "price_3": 900,
                        "salary_1": 45000, "salary_2": 45000, "salary_3": 45000,
                        "utr_1": 0.85, "utr_2": 0.85, "utr_3": 0.85
                    }
                }
            }
        }
    }
    
    # Run simulation with test config
    engine = SimulationEngine()
    results = engine.run_simulation_with_offices(
        offices=test_config,
        start_year=2025,
        start_month=1,
        end_year=2025,
        end_month=3,
        economic_params=EconomicParameters()
    )
    
    # Analyze results
    analyze_churn_results(results, "High Churn Rate Test")

if __name__ == "__main__":
    test_churn_with_real_scenarios()
    test_churn_with_high_rates()