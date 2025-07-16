#!/usr/bin/env python3
"""
Debug script to analyze progression and CAT curve effects on FTE.
Compares scenarios with and without progression to isolate the impact.
"""

import sys
import json
import requests
from typing import Dict, Any, List

def create_no_progression_scenario(scenario_id: str) -> Dict[str, Any]:
    """Create a modified scenario with no progression to isolate recruitment/churn effects."""
    
    # Load original scenario
    try:
        response = requests.get(f"http://localhost:8000/scenarios/{scenario_id}")
        response.raise_for_status()
        original_scenario = response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error loading scenario: {e}")
        sys.exit(1)
    
    # Create a copy with no progression
    no_progression_scenario = original_scenario.copy()
    
    # Set all progression rates to 0 (only if progression_config exists and is not None)
    if 'progression_config' in no_progression_scenario and no_progression_scenario['progression_config'] is not None:
        for level_config in no_progression_scenario['progression_config'].values():
            if 'progression_rates' in level_config:
                for target_level in level_config['progression_rates']:
                    level_config['progression_rates'][target_level] = 0.0
    
    # Set all CAT curve rates to 0 (only if cat_curves exists and is not None)
    if 'cat_curves' in no_progression_scenario and no_progression_scenario['cat_curves'] is not None:
        for level_config in no_progression_scenario['cat_curves'].values():
            if 'attrition_rates' in level_config:
                for tenure in level_config['attrition_rates']:
                    level_config['attrition_rates'][tenure] = 0.0
    
    return no_progression_scenario

def run_scenario_with_data(scenario_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run a scenario with the provided data."""
    try:
        response = requests.post(f"http://localhost:8000/scenarios/run", json=scenario_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error running scenario: {e}")
        sys.exit(1)

def analyze_fte_changes(results: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze FTE changes from simulation results."""
    analysis = {
        'total_fte_by_year': {},
        'office_changes': {},
        'summary': {}
    }
    
    offices = results.get('offices', {})
    
    # Calculate total FTE by year
    for office_name, office_data in offices.items():
        for year_data in office_data.get('years', []):
            year = year_data.get('year')
            fte = year_data.get('fte', 0)
            
            if year not in analysis['total_fte_by_year']:
                analysis['total_fte_by_year'][year] = 0
            analysis['total_fte_by_year'][year] += fte
    
    # Analyze office-level changes
    for office_name, office_data in offices.items():
        fte_by_year = {}
        for year_data in office_data.get('years', []):
            year = year_data.get('year')
            fte = year_data.get('fte', 0)
            fte_by_year[year] = fte
        
        if len(fte_by_year) >= 2:
            years = sorted(fte_by_year.keys())
            start_fte = fte_by_year[years[0]]
            end_fte = fte_by_year[years[-1]]
            total_change = end_fte - start_fte
            
            analysis['office_changes'][office_name] = {
                'start_year': years[0],
                'end_year': years[-1],
                'start_fte': start_fte,
                'end_fte': end_fte,
                'total_change': total_change,
                'fte_by_year': fte_by_year
            }
    
    # Summary
    if analysis['total_fte_by_year']:
        years = sorted(analysis['total_fte_by_year'].keys())
        start_fte = analysis['total_fte_by_year'][years[0]]
        end_fte = analysis['total_fte_by_year'][years[-1]]
        total_change = end_fte - start_fte
        
        analysis['summary'] = {
            'start_year': years[0],
            'end_year': years[-1],
            'start_fte': start_fte,
            'end_fte': end_fte,
            'total_change': total_change,
            'fte_by_year': analysis['total_fte_by_year']
        }
    
    return analysis

def print_comparison(original_analysis: Dict[str, Any], no_progression_analysis: Dict[str, Any]):
    """Print comparison between scenarios with and without progression."""
    print(f"\n{'='*80}")
    print(f"📊 PROGRESSION EFFECT ANALYSIS")
    print(f"{'='*80}")
    
    # Original scenario (with progression)
    print(f"\n📈 ORIGINAL SCENARIO (WITH PROGRESSION)")
    print(f"{'-'*50}")
    if original_analysis['summary']:
        summary = original_analysis['summary']
        print(f"Start FTE ({summary['start_year']}): {summary['start_fte']:.2f}")
        print(f"End FTE ({summary['end_year']}): {summary['end_fte']:.2f}")
        print(f"Total Change: {summary['total_change']:+.2f} FTE")
        print(f"Annual Change: {summary['total_change'] / (summary['end_year'] - summary['start_year']):+.2f} FTE/year")
        
        print(f"\nFTE by Year:")
        for year, fte in summary['fte_by_year'].items():
            print(f"  {year}: {fte:.2f} FTE")
    
    # No progression scenario
    print(f"\n🚫 NO PROGRESSION SCENARIO")
    print(f"{'-'*50}")
    if no_progression_analysis['summary']:
        summary = no_progression_analysis['summary']
        print(f"Start FTE ({summary['start_year']}): {summary['start_fte']:.2f}")
        print(f"End FTE ({summary['end_year']}): {summary['end_fte']:.2f}")
        print(f"Total Change: {summary['total_change']:+.2f} FTE")
        print(f"Annual Change: {summary['total_change'] / (summary['end_year'] - summary['start_year']):+.2f} FTE/year")
        
        print(f"\nFTE by Year:")
        for year, fte in summary['fte_by_year'].items():
            print(f"  {year}: {fte:.2f} FTE")
    
    # Comparison
    print(f"\n🔍 COMPARISON")
    print(f"{'-'*50}")
    if original_analysis['summary'] and no_progression_analysis['summary']:
        orig_change = original_analysis['summary']['total_change']
        no_prog_change = no_progression_analysis['summary']['total_change']
        progression_effect = orig_change - no_prog_change
        
        print(f"Original Scenario Change: {orig_change:+.2f} FTE")
        print(f"No Progression Change: {no_prog_change:+.2f} FTE")
        print(f"Progression Effect: {progression_effect:+.2f} FTE")
        
        if progression_effect < 0:
            print(f"⚠️  Progression is causing FTE LOSS of {abs(progression_effect):.2f} FTE")
        elif progression_effect > 0:
            print(f"✅ Progression is causing FTE GAIN of {progression_effect:.2f} FTE")
        else:
            print(f"⚖️  Progression has no net effect on FTE")
        
        # Expected vs Actual
        print(f"\n📋 EXPECTED VS ACTUAL")
        print(f"Expected (from recruitment/churn): +35.00 FTE")
        print(f"Actual (no progression): {no_prog_change:+.2f} FTE")
        print(f"Difference: {no_prog_change - 35.00:+.2f} FTE")
        
        if abs(no_prog_change - 35.00) > 5:
            print(f"⚠️  Large difference! Recruitment/churn may not be applied correctly")
        else:
            print(f"✅ Recruitment/churn is working correctly")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/debug_progression_effects.py <scenario_id>")
        sys.exit(1)
    
    scenario_id = sys.argv[1]
    
    print(f"🔍 Analyzing Progression Effects for Scenario: {scenario_id}")
    print(f"{'='*80}")
    
    # Run original scenario
    print("📈 Running original scenario (with progression)...")
    original_results = run_scenario_with_data({"scenario_id": scenario_id})
    original_analysis = analyze_fte_changes(original_results)
    
    # Create and run no-progression scenario
    print("🚫 Creating scenario without progression...")
    no_progression_data = create_no_progression_scenario(scenario_id)
    
    print("🚀 Running scenario without progression...")
    no_progression_results = run_scenario_with_data(no_progression_data)
    no_progression_analysis = analyze_fte_changes(no_progression_results)
    
    # Print comparison
    print_comparison(original_analysis, no_progression_analysis)
    
    print(f"\n{'='*80}")
    print(f"✅ Progression analysis complete!")
    print(f"{'='*80}")

if __name__ == "__main__":
    main() 