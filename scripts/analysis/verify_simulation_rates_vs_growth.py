#!/usr/bin/env python3
"""
Verify Simulation: Recruitment, Churn, and Progression Rates vs. Observed Growth
Aggregates rates across all levels and months (including sub-roles), compares to simulation results
"""

import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Tuple

def aggregate_rates(role_config: dict) -> dict:
    """Aggregate recruitment, churn, progression rates across all months for a role."""
    months = [str(i) for i in range(1, 13)]
    recruitment_rates = []
    churn_rates = []
    progression_rates = []
    for m in months:
        recruitment = role_config.get(f'recruitment_{m}', None)
        churn = role_config.get(f'churn_{m}', None)
        progression = role_config.get(f'progression_{m}', None)
        if recruitment is not None:
            recruitment_rates.append(recruitment)
        if churn is not None:
            churn_rates.append(churn)
        if progression is not None:
            progression_rates.append(progression)
    # Fallback to base if no monthly rates
    if not recruitment_rates and 'recruitment' in role_config:
        recruitment_rates.append(role_config['recruitment'])
    if not churn_rates and 'churn' in role_config:
        churn_rates.append(role_config['churn'])
    if not progression_rates and 'progression' in role_config:
        progression_rates.append(role_config['progression'])
    return {
        'recruitment': sum(recruitment_rates) / len(recruitment_rates) if recruitment_rates else 0.0,
        'churn': sum(churn_rates) / len(churn_rates) if churn_rates else 0.0,
        'progression': sum(progression_rates) / len(progression_rates) if progression_rates else 0.0
    }

def aggregate_fte_and_rates(role_config: dict) -> Tuple[float, float, float, float]:
    """Recursively aggregate FTE and rates for a role and all sub-roles."""
    total_fte = 0.0
    weighted_recruitment = 0.0
    weighted_churn = 0.0
    weighted_progression = 0.0
    # If this is a leaf role (has 'fte'), aggregate rates
    if 'fte' in role_config:
        fte = role_config.get('fte', 0.0)
        rates = aggregate_rates(role_config)
        total_fte += fte
        weighted_recruitment += rates['recruitment'] * fte
        weighted_churn += rates['churn'] * fte
        weighted_progression += rates['progression'] * fte
    # If this role has sub-roles (dicts), recurse
    for k, v in role_config.items():
        if isinstance(v, dict):
            sub_fte, sub_rec, sub_churn, sub_prog = aggregate_fte_and_rates(v)
            total_fte += sub_fte
            weighted_recruitment += sub_rec
            weighted_churn += sub_churn
            weighted_progression += sub_prog
    return total_fte, weighted_recruitment, weighted_churn, weighted_progression

def verify_simulation_rates_vs_growth(sim_file: str, config_file: str):
    print(f"🔍 VERIFYING SIMULATION RATES vs GROWTH: {sim_file}")
    print("=" * 80)
    # Load simulation results
    with open(sim_file, 'r') as f:
        sim_data = json.load(f)
    # Load configuration
    with open(config_file, 'r') as f:
        config = json.load(f)
    years = sim_data.get('years', {})
    year_list = sorted(years.keys())
    print(f"📅 Analyzing {len(year_list)} years: {year_list[0]} → {year_list[-1]}")
    # For each office, aggregate rates and compare
    for office_name, office_config in config.items():
        if not isinstance(office_config, dict) or 'roles' not in office_config:
            continue
        print(f"\n🏢 {office_name}")
        total_fte = 0.0
        weighted_recruitment = 0.0
        weighted_churn = 0.0
        weighted_progression = 0.0
        for role_name, role_config in office_config['roles'].items():
            fte, rec, churn, prog = aggregate_fte_and_rates(role_config)
            total_fte += fte
            weighted_recruitment += rec
            weighted_churn += churn
            weighted_progression += prog
            print(f"  {role_name:12s} FTE: {fte:4.0f}")
        if total_fte == 0:
            print("  (No FTE in config)")
            continue
        avg_recruitment = weighted_recruitment / total_fte
        avg_churn = weighted_churn / total_fte
        avg_progression = weighted_progression / total_fte
        net_monthly_growth = avg_recruitment - avg_churn
        expected_annual_growth = ((1 + net_monthly_growth) ** 12 - 1) * 100
        print(f"  Weighted Avg Recruitment: {avg_recruitment:.3f} ({avg_recruitment*100:.1f}%)")
        print(f"  Weighted Avg Churn: {avg_churn:.3f} ({avg_churn*100:.1f}%)")
        print(f"  Weighted Avg Progression: {avg_progression:.3f} ({avg_progression*100:.1f}%)")
        print(f"  Net Monthly Growth: {net_monthly_growth:.3f} ({net_monthly_growth*100:.1f}%)")
        print(f"  Expected Annual Growth: {expected_annual_growth:.1f}%")
        # Compare to observed
        if office_name in years[year_list[0]]['offices']:
            start_fte = years[year_list[0]]['offices'][office_name]['total_fte']
            end_fte = years[year_list[-1]]['offices'][office_name]['total_fte']
            if start_fte > 0:
                observed_growth = ((end_fte - start_fte) / start_fte) * 100
                years_span = int(year_list[-1]) - int(year_list[0])
                observed_annual_growth = observed_growth / years_span if years_span > 0 else 0
                print(f"  Observed Growth: {start_fte:.0f} → {end_fte:.0f} ({observed_growth:.1f}% total)")
                print(f"  Observed Annual Growth: {observed_annual_growth:.1f}%")
                diff = observed_annual_growth - expected_annual_growth
                print(f"  Growth Difference: {diff:+.1f}%")
                if abs(diff) > 10:
                    print(f"    ⚠️  SIGNIFICANT DIFFERENCE: {diff:+.1f}%")
                elif abs(diff) > 5:
                    print(f"    📊 MODERATE DIFFERENCE: {diff:+.1f}%")
                else:
                    print(f"    ✅ GOOD MATCH: {diff:+.1f}%")
    print("\n📅 Verification completed: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verify_simulation_rates_vs_growth.py <simulation_file.json>")
        sys.exit(1)
    sim_file = sys.argv[1]
    config_file = 'backend/config/office_configuration.json'
    verify_simulation_rates_vs_growth(sim_file, config_file) 