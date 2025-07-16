#!/usr/bin/env python3
"""
Debug script to analyze recruitment vs churn values in a scenario.
Shows the net effect on FTE and helps identify why FTE might be declining.
"""

import sys
import json
import requests
from typing import Dict, Any, List
import pandas as pd

def load_scenario(scenario_id: str) -> Dict[str, Any]:
    """Load scenario data from the backend."""
    try:
        response = requests.get(f"http://localhost:8000/scenarios/{scenario_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error loading scenario: {e}")
        sys.exit(1)

def analyze_baseline_input(baseline_input: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze recruitment vs churn values in baseline input."""
    analysis = {
        'recruitment': {},
        'churn': {},
        'net_effect': {},
        'summary': {}
    }
    
    global_data = baseline_input.get('global', {})
    recruitment_data = global_data.get('recruitment', {})
    churn_data = global_data.get('churn', {})
    
    # Analyze recruitment values
    for role, levels in recruitment_data.items():
        analysis['recruitment'][role] = {}
        for level, months in levels.items():
            total_recruitment = sum(months.values())
            analysis['recruitment'][role][level] = {
                'total': total_recruitment,
                'monthly_avg': total_recruitment / len(months) if months else 0,
                'months': months
            }
    
    # Analyze churn values
    for role, levels in churn_data.items():
        analysis['churn'][role] = {}
        for level, months in levels.items():
            total_churn = sum(months.values())
            analysis['churn'][role][level] = {
                'total': total_churn,
                'monthly_avg': total_churn / len(months) if months else 0,
                'months': months
            }
    
    # Calculate net effect
    all_roles = set(analysis['recruitment'].keys()) | set(analysis['churn'].keys())
    for role in all_roles:
        analysis['net_effect'][role] = {}
        recruitment_levels = analysis['recruitment'].get(role, {})
        churn_levels = analysis['churn'].get(role, {})
        all_levels = set(recruitment_levels.keys()) | set(churn_levels.keys())
        
        for level in all_levels:
            recruitment_total = recruitment_levels.get(level, {}).get('total', 0)
            churn_total = churn_levels.get(level, {}).get('total', 0)
            net = recruitment_total - churn_total
            
            analysis['net_effect'][role][level] = {
                'recruitment': recruitment_total,
                'churn': churn_total,
                'net': net,
                'net_monthly_avg': net / 36 if net != 0 else 0  # 36 months for 3 years
            }
    
    # Summary statistics
    total_recruitment = sum(
        level_data['total'] 
        for role_data in analysis['recruitment'].values() 
        for level_data in role_data.values()
    )
    total_churn = sum(
        level_data['total'] 
        for role_data in analysis['churn'].values() 
        for level_data in role_data.values()
    )
    total_net = total_recruitment - total_churn
    
    analysis['summary'] = {
        'total_recruitment': total_recruitment,
        'total_churn': total_churn,
        'total_net': total_net,
        'net_monthly_avg': total_net / 36 if total_net != 0 else 0,
        'recruitment_vs_churn_ratio': total_recruitment / total_churn if total_churn > 0 else float('inf')
    }
    
    return analysis

def run_scenario_and_analyze(scenario_id: str) -> Dict[str, Any]:
    """Run the scenario and analyze the results."""
    print(f"🔍 Running scenario: {scenario_id}")
    
    # Run the scenario
    try:
        response = requests.post(f"http://localhost:8000/scenarios/run", json={
            "scenario_id": scenario_id
        })
        response.raise_for_status()
        results = response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error running scenario: {e}")
        sys.exit(1)
    
    return results

def analyze_office_results(results: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze office-level FTE changes."""
    analysis = {
        'office_changes': {},
        'summary': {}
    }
    
    offices = results.get('offices', {})
    
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
            annual_change = total_change / (len(years) - 1) if len(years) > 1 else 0
            
            analysis['office_changes'][office_name] = {
                'start_year': years[0],
                'end_year': years[-1],
                'start_fte': start_fte,
                'end_fte': end_fte,
                'total_change': total_change,
                'annual_change': annual_change,
                'fte_by_year': fte_by_year
            }
    
    # Summary statistics
    if analysis['office_changes']:
        total_start_fte = sum(office['start_fte'] for office in analysis['office_changes'].values())
        total_end_fte = sum(office['end_fte'] for office in analysis['office_changes'].values())
        total_change = total_end_fte - total_start_fte
        
        analysis['summary'] = {
            'total_start_fte': total_start_fte,
            'total_end_fte': total_end_fte,
            'total_change': total_change,
            'avg_annual_change': total_change / (len(analysis['office_changes']) * 2) if analysis['office_changes'] else 0
        }
    
    return analysis

def print_analysis(scenario_id: str, baseline_analysis: Dict[str, Any], results_analysis: Dict[str, Any]):
    """Print the analysis results in a readable format."""
    print(f"\n{'='*80}")
    print(f"📊 RECRUITMENT VS CHURN ANALYSIS")
    print(f"{'='*80}")
    print(f"Scenario ID: {scenario_id}")
    
    # Baseline Input Analysis
    print(f"\n📈 BASELINE INPUT ANALYSIS")
    print(f"{'-'*50}")
    
    summary = baseline_analysis['summary']
    print(f"Total Recruitment: {summary['total_recruitment']:.2f} FTE")
    print(f"Total Churn: {summary['total_churn']:.2f} FTE")
    print(f"Net Effect: {summary['total_net']:.2f} FTE")
    print(f"Net Monthly Average: {summary['net_monthly_avg']:.2f} FTE/month")
    print(f"Recruitment/Churn Ratio: {summary['recruitment_vs_churn_ratio']:.2f}")
    
    if summary['total_net'] < 0:
        print(f"⚠️  WARNING: Net effect is negative - churn exceeds recruitment!")
    elif summary['total_net'] > 0:
        print(f"✅ Net effect is positive - recruitment exceeds churn")
    else:
        print(f"⚖️  Net effect is zero - recruitment equals churn")
    
    # Detailed breakdown by role and level
    print(f"\n🔍 DETAILED BREAKDOWN BY ROLE/LEVEL")
    print(f"{'-'*50}")
    
    for role, levels in baseline_analysis['net_effect'].items():
        print(f"\n{role}:")
        for level, data in levels.items():
            net = data['net']
            status = "📈" if net > 0 else "📉" if net < 0 else "➡️"
            print(f"  {level}: {status} Net: {net:.2f} (Rec: {data['recruitment']:.2f}, Churn: {data['churn']:.2f})")
    
    # Office Results Analysis
    print(f"\n🏢 OFFICE FTE CHANGES")
    print(f"{'-'*50}")
    
    if results_analysis['summary']:
        summary = results_analysis['summary']
        print(f"Total Start FTE: {summary['total_start_fte']:.2f}")
        print(f"Total End FTE: {summary['total_end_fte']:.2f}")
        print(f"Total Change: {summary['total_change']:.2f}")
        print(f"Average Annual Change: {summary['avg_annual_change']:.2f}")
    
    print(f"\nOffice Details:")
    for office_name, office_data in results_analysis['office_changes'].items():
        change = office_data['total_change']
        status = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        print(f"  {office_name}: {status} {change:+.1f} FTE ({office_data['start_fte']:.1f} → {office_data['end_fte']:.1f})")
    
    # Correlation Analysis
    print(f"\n🔗 CORRELATION ANALYSIS")
    print(f"{'-'*50}")
    
    baseline_net = baseline_analysis['summary']['total_net']
    actual_change = results_analysis['summary']['total_change'] if results_analysis['summary'] else 0
    
    print(f"Expected Net Change (from baseline): {baseline_net:.2f} FTE")
    print(f"Actual Net Change (from simulation): {actual_change:.2f} FTE")
    print(f"Difference: {actual_change - baseline_net:.2f} FTE")
    
    if abs(actual_change - baseline_net) > 10:  # Allow some tolerance
        print(f"⚠️  WARNING: Large difference between expected and actual FTE change!")
        print(f"   This suggests other factors (progression, CAT curves) are affecting FTE")
    else:
        print(f"✅ Expected and actual changes are reasonably close")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/debug_recruitment_vs_churn.py <scenario_id>")
        sys.exit(1)
    
    scenario_id = sys.argv[1]
    
    print(f"🔍 Debugging Recruitment vs Churn for Scenario: {scenario_id}")
    print(f"{'='*80}")
    
    # Load scenario data
    print("📋 Loading scenario data...")
    scenario_data = load_scenario(scenario_id)
    
    # Analyze baseline input
    print("📊 Analyzing baseline input...")
    baseline_input = scenario_data.get('baseline_input', {})
    baseline_analysis = analyze_baseline_input(baseline_input)
    
    # Run scenario and analyze results
    print("🚀 Running scenario...")
    results = run_scenario_and_analyze(scenario_id)
    
    # Analyze office results
    print("🏢 Analyzing office results...")
    results_analysis = analyze_office_results(results)
    
    # Print comprehensive analysis
    print_analysis(scenario_id, baseline_analysis, results_analysis)
    
    print(f"\n{'='*80}")
    print(f"✅ Analysis complete!")
    print(f"{'='*80}")

if __name__ == "__main__":
    main() 