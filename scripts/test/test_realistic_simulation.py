#!/usr/bin/env python3
"""
Test script to run a full simulation with realistic population initialization.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from backend.src.services.simulation.office_manager import OfficeManager
from backend.src.services.simulation.workforce import WorkforceManager
from backend.src.services.config_service import ConfigService
from backend.src.services.simulation.models import Month
from collections import defaultdict, Counter
import pandas as pd
from backend.config.progression_config import PROGRESSION_CONFIG

def run_realistic_simulation():
    """Run a full simulation with realistic population"""
    
    print("=== REALISTIC SIMULATION TEST ===")
    
    # Initialize services
    config_service = ConfigService()
    office_manager = OfficeManager(config_service)
    workforce_manager = WorkforceManager({})
    
    # Initialize offices with realistic people
    offices = office_manager.initialize_offices_from_config()
    workforce_manager.offices = offices
    
    print(f"Initialized {len(offices)} offices with realistic population")
    
    # Track simulation results
    monthly_metrics = {}
    promotion_history = []
    
    # For promotion tracking: store previous FTE counts by office/role/level
    prev_fte_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    
    # Run simulation for 3 years (36 months)
    start_year = 2025
    start_month = 1
    
    print(f"\nRunning simulation from {start_year}-{start_month:02d} for 36 months...")
    
    for month_offset in range(36):
        current_year = start_year + (start_month + month_offset - 1) // 12
        current_month = ((start_month + month_offset - 1) % 12) + 1
        current_date = f"{current_year}-{current_month:02d}"
        
        print(f"\nProcessing {current_date}...")
        
        # Process the month
        workforce_manager.process_month(
            current_year, 
            current_month, 
            current_date, 
            monthly_metrics
        )
        
        # Track promotions by comparing FTE counts between levels
        for office_name, office in offices.items():
            for role_name, role_data in office.roles.items():
                if isinstance(role_data, dict):
                    for level_name, level in role_data.items():
                        prev_fte = prev_fte_counts[office_name][role_name][level_name]
                        curr_fte = level.total
                        # If FTE increased, assume promotions in (from lower level)
                        if curr_fte > prev_fte and prev_fte > 0:
                            promotions = curr_fte - prev_fte
                            print(f"  {office_name} {role_name} {level_name}: {promotions} promotions in")
                            promotion_history.append({
                                'date': current_date,
                                'office': office_name,
                                'role': role_name,
                                'to_level': level_name,
                                'count': promotions
                            })
                        prev_fte_counts[office_name][role_name][level_name] = curr_fte
    
    # Analyze results
    print("\n=== SIMULATION RESULTS ===")
    
    # Final population by office and level
    print("\nFinal Population by Office:")
    for office_name, office in offices.items():
        print(f"\n{office_name} (Total FTE: {office.total_fte}):")
        for role_name, role_data in office.roles.items():
            if isinstance(role_data, dict):
                for level_name, level in role_data.items():
                    if level.total > 0:
                        print(f"  {role_name} {level_name}: {level.total} FTE")
            else:
                if role_data.total > 0:
                    print(f"  {role_name}: {role_data.total} FTE")
    
    # Promotion summary
    total_promotions = sum(p['count'] for p in promotion_history)
    print(f"\nTotal promotions over 3 years: {total_promotions}")
    print(f"Average promotions per month: {total_promotions / 36:.2f}")

    # --- CAT Progression Matrix Analysis ---
    print("\n=== CAT PROGRESSION MATRIX ANALYSIS BY LAF ===")
    # For each level, for each LAF, build a matrix: CAT stage (columns), rows: 'Leveled', 'Not leveled'
    # 1. Track for each person: at which CAT and LAF (month) they leveled (if at all)
    # 2. For people still at a level, record their current CAT
    # Map: level -> LAF month -> cat_stage (int) -> count
    leveled_at_cat_laf = defaultdict(lambda: defaultdict(Counter))
    stuck_at_cat = defaultdict(Counter)
    total_at_cat = defaultdict(Counter)
    # Helper: get CAT stage (0, 6, 12, ...)
    def get_cat_stage(months):
        if months < 6:
            return 0
        return 6 * ((months // 6))
    # Helper: get LAF month (1=Jan, 4=Apr, 7=Jul, 10=Oct, etc.)
    def get_laf_month(date_str):
        return int(date_str.split('-')[1])
    # 1. Track promotions by CAT and LAF
    for date, offices_data in monthly_metrics.items():
        for office_name, office_data in offices_data.items():
            promotion_details = office_data.get('promotion_details', [])
            for promo in promotion_details:
                level = promo['level']
                laf_month = get_laf_month(promo['date'])
                cat = promo['cat']
                # Only count if this is a valid progression month for this level
                valid_months = PROGRESSION_CONFIG.get(level, {}).get('progression_months', [1])
                if laf_month in valid_months:
                    leveled_at_cat_laf[level][laf_month][cat] += 1
                else:
                    print(f"[WARNING] Promotion for {level} in invalid month {laf_month} (not in {valid_months}) - ignored in matrix.")
    # For each office, role, level, person: record their current CAT at end
    for office in offices.values():
        for role_name, role_data in office.roles.items():
            if isinstance(role_data, dict):
                for level_name, level in role_data.items():
                    for person in level.people:
                        months = person.get_level_tenure_months('2028-01')  # End of simulation
                        cat = get_cat_stage(months)
                        stuck_at_cat[level_name][cat] += 1
                        total_at_cat[level_name][cat] += 1
            else:
                for person in role_data.people:
                    months = person.get_level_tenure_months('2028-01')
                    cat = get_cat_stage(months)
                    stuck_at_cat[role_name][cat] += 1
                    total_at_cat[role_name][cat] += 1
    # Print the matrix for each level and LAF
    for level in sorted(set(list(leveled_at_cat_laf.keys()) + list(stuck_at_cat.keys()) + list(total_at_cat.keys()))):
        print(f"\nLevel: {level}")
        # Gather all LAF months for this level
        laf_months = sorted(leveled_at_cat_laf[level].keys())
        cats = sorted(set(list(stuck_at_cat[level].keys()) + [6, 12, 18, 24, 30, 36, 42]))
        for laf in laf_months:
            print(f"  LAF Month: {laf}")
            header = "    CAT | " + " | ".join(str(cat) for cat in cats)
            print(header)
            print("    " + "-" * (len(header)-4))
            print("    Leveled | " + " | ".join(str(leveled_at_cat_laf[level][laf].get(cat, 0)) for cat in cats))
        # Print not leveled (stuck) at end
        print("    Not leveled | " + " | ".join(str(stuck_at_cat[level].get(cat, 0)) for cat in cats))
        print("    Total | " + " | ".join(str(total_at_cat[level].get(cat, 0)) for cat in cats))
    # --- End CAT Progression Matrix Analysis ---

    # Export results to Excel
    export_simulation_results(monthly_metrics, promotion_history)
    
    print("\n=== SIMULATION COMPLETE ===")
    print("Results exported to 'realistic_simulation_results.xlsx'")

def export_simulation_results(monthly_metrics, promotion_history):
    """Export simulation results to Excel"""
    
    with pd.ExcelWriter('realistic_simulation_results.xlsx', engine='openpyxl') as writer:
        
        # Sheet 1: Monthly Population
        monthly_data = []
        for date, offices_data in monthly_metrics.items():
            for office_name, office_data in offices_data.items():
                for role_name, role_data in office_data.items():
                    if isinstance(role_data, dict):
                        for level_name, level_data in role_data.items():
                            if isinstance(level_data, dict):  # Only process if dict
                                monthly_data.append({
                                    'date': date,
                                    'office': office_name,
                                    'role': role_name,
                                    'level': level_name,
                                    'fte': level_data.get('total_fte', 0),
                                    'recruited': level_data.get('recruited', 0),
                                    'churned': level_data.get('churned', 0),
                                    'progressed_out': level_data.get('progressed_out', 0),
                                    'progressed_in': level_data.get('progressed_in', 0)
                                })
                    elif isinstance(role_data, dict):
                        continue
                    else:
                        if isinstance(role_data, dict):
                            continue
                        # Flat roles (Operations)
                        # Not expected in this config, but handle gracefully
                        monthly_data.append({
                            'date': date,
                            'office': office_name,
                            'role': role_name,
                            'level': 'N/A',
                            'fte': getattr(role_data, 'total', 0),
                            'recruited': 0,
                            'churned': 0,
                            'progressed_out': 0,
                            'progressed_in': 0
                        })
        
        df_monthly = pd.DataFrame(monthly_data)
        df_monthly.to_excel(writer, sheet_name='Monthly Population', index=False)
        
        # Sheet 2: Promotion History
        df_promotions = pd.DataFrame(promotion_history)
        df_promotions.to_excel(writer, sheet_name='Promotion History', index=False)
        
        # Sheet 3: Summary Statistics
        summary_data = []
        for office_name in set(df_monthly['office']):
            office_data = df_monthly[df_monthly['office'] == office_name]
            total_promotions = office_data['progressed_out'].sum()
            total_recruitment = office_data['recruited'].sum()
            total_churn = office_data['churned'].sum()
            
            summary_data.append({
                'office': office_name,
                'total_promotions': total_promotions,
                'total_recruitment': total_recruitment,
                'total_churn': total_churn,
                'net_growth': total_recruitment - total_churn
            })
        
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='Summary Statistics', index=False)

if __name__ == "__main__":
    run_realistic_simulation() 