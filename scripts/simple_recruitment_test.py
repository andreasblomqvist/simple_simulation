#!/usr/bin/env python3
"""
Simple test script that directly sends baseline input to the simulation engine.
Bypasses all the complex scenario resolution and transformation layers.
"""

import sys
import json
import requests
from typing import Dict, Any

def create_simple_baseline_input() -> Dict[str, Any]:
    """Create a simple baseline input with clear recruitment vs churn values."""
    
    # Simple test: 10 FTE recruitment per month, 5 FTE churn per month
    # Should result in +5 FTE net growth per month = +60 FTE over 3 years
    
    baseline_input = {
        "global": {
            "recruitment": {
                "Consultant": {
                    "A": {
                        "202501": 10, "202502": 10, "202503": 10, "202504": 10,
                        "202505": 10, "202506": 10, "202507": 10, "202508": 10,
                        "202509": 10, "202510": 10, "202511": 10, "202512": 10,
                        "202601": 10, "202602": 10, "202603": 10, "202604": 10,
                        "202605": 10, "202606": 10, "202607": 10, "202608": 10,
                        "202609": 10, "202610": 10, "202611": 10, "202612": 10,
                        "202701": 10, "202702": 10, "202703": 10, "202704": 10,
                        "202705": 10, "202706": 10, "202707": 10, "202708": 10,
                        "202709": 10, "202710": 10, "202711": 10, "202712": 10
                    }
                }
            },
            "churn": {
                "Consultant": {
                    "A": {
                        "202501": 5, "202502": 5, "202503": 5, "202504": 5,
                        "202505": 5, "202506": 5, "202507": 5, "202508": 5,
                        "202509": 5, "202510": 5, "202511": 5, "202512": 5,
                        "202601": 5, "202602": 5, "202603": 5, "202604": 5,
                        "202605": 5, "202606": 5, "202607": 5, "202608": 5,
                        "202609": 5, "202610": 5, "202611": 5, "202612": 5,
                        "202701": 5, "202702": 5, "202703": 5, "202704": 5,
                        "202705": 5, "202706": 5, "202707": 5, "202708": 5,
                        "202709": 5, "202710": 5, "202711": 5, "202712": 5
                    }
                }
            }
        }
    }
    
    return baseline_input

def run_simple_test():
    """Run a simple test with direct baseline input."""
    
    print("🧪 SIMPLE RECRUITMENT/CHURN TEST")
    print("=" * 60)
    
    # Create simple baseline input
    baseline_input = create_simple_baseline_input()
    
    print("📊 Test Setup:")
    print(f"  - Recruitment: 10 FTE/month for 36 months = 360 FTE total")
    print(f"  - Churn: 5 FTE/month for 36 months = 180 FTE total")
    print(f"  - Expected Net Growth: +180 FTE over 3 years")
    print(f"  - Expected Monthly Growth: +5 FTE/month")
    
    # Create scenario definition
    scenario_definition = {
        "name": "Simple Recruitment Test",
        "description": "Test recruitment vs churn with simple values",
        "time_range": {
            "start_year": 2025,
            "start_month": 1,
            "end_year": 2027,
            "end_month": 12
        },
        "office_scope": ["Group"],
        "levers": {},
        "baseline_input": baseline_input,
        "progression_config": None,  # No progression
        "cat_curves": None  # No CAT curves
    }
    
    # Create API request
    request_data = {
        "scenario_definition": scenario_definition
    }
    
    print("\n🚀 Running simulation...")
    
    try:
        response = requests.post(
            "http://localhost:8000/scenarios/run",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        results = response.json()
        
        print("✅ Simulation completed successfully!")
        
        # Debug: Show the response structure
        print(f"\n🔍 DEBUG - Response Structure:")
        print(f"Response keys: {list(results.keys())}")
        if 'results' in results:
            print(f"Results keys: {list(results['results'].keys())}")
            if 'offices' in results['results']:
                print(f"Offices count: {len(results['results']['offices'])}")
                if results['results']['offices']:
                    first_office = list(results['results']['offices'].keys())[0]
                    print(f"First office: {first_office}")
                    office_data = results['results']['offices'][first_office]
                    print(f"Office data keys: {list(office_data.keys())}")
        
        # Print recruitment and churn values for each level and month
        print(f"\n📊 RECRUITMENT AND CHURN VALUES:")
        print("=" * 60)
        
        baseline_input = scenario_definition['baseline_input']
        global_data = baseline_input.get('global', {})
        recruitment_data = global_data.get('recruitment', {})
        churn_data = global_data.get('churn', {})
        
        for role, levels in recruitment_data.items():
            print(f"\n{role}:")
            for level, months in levels.items():
                print(f"  {level}:")
                # Show first 3 months as example
                month_count = 0
                for month, value in months.items():
                    if month_count >= 3:
                        break
                    churn_value = churn_data.get(role, {}).get(level, {}).get(month, 0)
                    net = value - churn_value
                    print(f"    {month}: Rec={value}, Churn={churn_value}, Net={net:+.1f}")
                    month_count += 1
                print(f"    ... (36 months total)")
        
        # Analyze results
        print("\n📈 RESULTS SUMMARY:")
        print("-" * 40)
        
        # Check if we have years data
        years_data = results.get('results', {}).get('years', [])
        if years_data:
            print(f"Found {len(years_data)} years of data:")
            print(f"Years data type: {type(years_data)}")
            # Print the first year data safely for dict or list
            if isinstance(years_data, dict):
                first_year_val = next(iter(years_data.values()))
                print(f"First year data: {first_year_val}")
            elif isinstance(years_data, list):
                print(f"First year data: {years_data[0] if years_data else 'None'}")
            
            total_fte_by_year = {}
            
            # Handle different possible structures
            if isinstance(years_data, dict):
                # If it's a dictionary with year keys
                for year_str, year_data in years_data.items():
                    year = int(year_str)
                    fte = year_data.get('fte', 0) if isinstance(year_data, dict) else year_data
                    total_fte_by_year[year] = fte
                    print(f"  {year}: {fte:.1f} FTE")
            elif isinstance(years_data, list):
                # If it's a list of year objects
                for year_data in years_data:
                    if isinstance(year_data, dict):
                        year = year_data.get('year')
                        fte = year_data.get('fte', 0)
                        total_fte_by_year[year] = fte
                        print(f"  {year}: {fte:.1f} FTE")
                    else:
                        print(f"  Unexpected year data format: {year_data}")
            else:
                print(f"  Unexpected years data type: {type(years_data)}")
                print(f"  Years data: {years_data}")
            
            # Summary
            years = sorted(total_fte_by_year.keys())
            if len(years) >= 2:
                start_fte = total_fte_by_year[years[0]]
                end_fte = total_fte_by_year[years[-1]]
                total_change = end_fte - start_fte
                
                print(f"\n📊 SUMMARY:")
                print(f"Start FTE ({years[0]}): {start_fte:.1f}")
                print(f"End FTE ({years[-1]}): {end_fte:.1f}")
                print(f"Total Change: {total_change:+.1f} FTE")
                print(f"Expected Change: +180.0 FTE")
                print(f"Difference: {total_change - 180.0:+.1f} FTE")
                
                if abs(total_change - 180.0) < 10:
                    print("✅ SUCCESS: Recruitment/churn is working correctly!")
                else:
                    print("❌ ISSUE: Large difference from expected result")
                
                # Show monthly breakdown
                print(f"\n📅 MONTHLY BREAKDOWN:")
                for year in years:
                    fte = total_fte_by_year[year]
                    expected_monthly_growth = 5.0  # +5 FTE per month
                    months_elapsed = (year - years[0]) * 12
                    expected_fte = start_fte + (expected_monthly_growth * months_elapsed)
                    print(f"  {year}: {fte:.1f} FTE (expected: {expected_fte:.1f}, diff: {fte - expected_fte:+.1f})")
        else:
            print("❌ No years data found in results")
            print(f"Available keys in results: {list(results.get('results', {}).keys())}")
            print(f"Full results structure: {json.dumps(results.get('results', {}), indent=2)}")
        
        # Show what we sent vs what we got
        print(f"\n🔍 INPUT vs OUTPUT ANALYSIS:")
        print("-" * 40)
        print(f"Input: 10 recruitment, 5 churn per month = +5 net per month")
        print(f"Expected: 36 months × 5 net = +180 FTE total")
        
        if years_data and len(years_data) >= 2:
            start_fte = years_data[0].get('fte', 0)
            end_fte = years_data[-1].get('fte', 0)
            total_change = end_fte - start_fte
            print(f"Actual: {total_change:+.1f} FTE total")
            
            if total_change > 0:
                print("✅ Recruitment/churn is being applied and showing growth!")
            else:
                print("❌ Something is preventing growth despite positive recruitment")
        else:
            print("❌ Cannot analyze results - missing data")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error running simulation: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        sys.exit(1)

if __name__ == "__main__":
    run_simple_test() 