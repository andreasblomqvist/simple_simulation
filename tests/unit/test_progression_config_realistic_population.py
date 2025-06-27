import random
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
import csv
import pandas as pd

# Level: (time_on_level, start_tenure, end_tenure)
LEVEL_TENURE_TABLE = [
    ('A', 6, 0, 6),
    ('AC', 9, 6, 15),
    ('C', 18, 15, 33),
    ('SrC', 18, 33, 51),
    ('AM', 48, 51, 99),
    ('M', 48, 99, 147),
    ('SrM', 120, 147, 267),
    ('Pi', 12, 267, 279),
    ('P', 1000, 279, 1279),
    ('X', 1000, 1279, 1279),
    ('OPE', 1000, 1279, 2279),
]

SAVED_POPULATION = []

def generate_population():
    random.seed(42)
    population = []
    for level, time_on_level, start_tenure, end_tenure in LEVEL_TENURE_TABLE:
        print(f'\nLevel {level} population:')
        for i in range(10):
            if end_tenure > start_tenure:
                total_tenure = random.randint(start_tenure, end_tenure)
            else:
                total_tenure = start_tenure
            months_on_level = total_tenure - start_tenure
            print(f'  id={level}_{i}, total_tenure={total_tenure}, months_on_level={months_on_level}')
            population.append({
                'level': level,
                'id': f'{level}_{i}',
                'total_tenure': total_tenure,
                'months_on_level': months_on_level
            })
    return population

# Save the population for reuse
def get_saved_population():
    global SAVED_POPULATION
    if not SAVED_POPULATION:
        SAVED_POPULATION = generate_population()
    return SAVED_POPULATION

def test_progression_eligibility_over_years():
    from backend.src.services.simulation.models import Person, Level
    from backend.config.progression_config import PROGRESSION_CONFIG
    pop = get_saved_population()
    print("\nEligibility over 3 years (36 months):")
    for fte in pop:
        level_name = fte['level']
        config = PROGRESSION_CONFIG.get(level_name, {})
        progression_months = config.get('progression_months', [1])
        # Simulate 36 months
        eligible_count = 0
        for m in range(36):
            # Calculate the simulated date
            year = 2025 + (m // 12)
            month = 1 + (m % 12)
            date = f"{year}-{month:02d}"
            # Calculate FTE's time on level at this date
            months_on_level = fte['months_on_level'] + m
            # Only check eligibility in progression months
            if month in progression_months:
                # Eligible if time on level >= 0 (or use min_time_on_level if you want)
                if months_on_level >= 0:
                    eligible_count += 1
        print(f"id={fte['id']}, level={level_name}, start_months_on_level={fte['months_on_level']}, eligible_windows={eligible_count}")

def export_promotions_to_excel(promotion_history, monthly_stats, filename='progression_simulation.xlsx'):
    """Export promotion history and statistics to Excel format with multiple sheets"""
    
    # Create Excel writer
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        
        # Sheet 1: Promotion History
        df_promotions = pd.DataFrame(promotion_history)
        df_promotions.to_excel(writer, sheet_name='Promotion History', index=False)
        
        # Sheet 2: Monthly Statistics
        df_monthly = pd.DataFrame(monthly_stats)
        df_monthly.to_excel(writer, sheet_name='Monthly Statistics', index=False)
        
        # Sheet 3: Summary by Level
        level_summary = []
        for promo in promotion_history:
            level_summary.append({
                'from_level': promo['from_level'],
                'to_level': promo['to_level'],
                'months_on_level': promo['months_on_level'],
                'cat': promo['cat'],
                'probability': promo['probability'],
                'date': promo['date']
            })
        
        df_level_summary = pd.DataFrame(level_summary)
        level_stats = df_level_summary.groupby('from_level').agg({
            'months_on_level': ['count', 'mean', 'min', 'max'],
            'probability': ['mean', 'min', 'max'],
            'cat': ['mean', 'min', 'max']
        }).round(2)
        
        # Flatten column names
        level_stats.columns = ['_'.join(col).strip() for col in level_stats.columns]
        level_stats.reset_index(inplace=True)
        level_stats.to_excel(writer, sheet_name='Level Summary', index=False)
        
        # Sheet 4: CAT Analysis
        cat_analysis = df_level_summary.groupby(['from_level', 'cat']).agg({
            'months_on_level': ['count', 'mean'],
            'probability': 'mean'
        }).round(3)
        
        # Flatten column names
        cat_analysis.columns = ['_'.join(col).strip() for col in cat_analysis.columns]
        cat_analysis.reset_index(inplace=True)
        cat_analysis.to_excel(writer, sheet_name='CAT Analysis', index=False)
        
        # Sheet 5: Monthly Promotion Counts
        monthly_promos = df_promotions.groupby('date').size().reset_index(name='promotions')
        monthly_promos.to_excel(writer, sheet_name='Monthly Promotions', index=False)
        
        # Sheet 6: Progression Path Analysis
        progression_paths = df_promotions.groupby(['from_level', 'to_level']).size().reset_index(name='count')
        progression_paths = progression_paths.sort_values('count', ascending=False)
        progression_paths.to_excel(writer, sheet_name='Progression Paths', index=False)
    
    print(f"Progression simulation exported to {filename}")
    print(f"Sheets created:")
    print(f"  - Promotion History: Individual promotion events")
    print(f"  - Monthly Statistics: Population and promotion counts by month")
    print(f"  - Level Summary: Statistics aggregated by level")
    print(f"  - CAT Analysis: Analysis by Career Advancement Time categories")
    print(f"  - Monthly Promotions: Promotion counts by month")
    print(f"  - Progression Paths: Most common progression routes")

def test_full_progression_simulation():
    """Run full progression logic with CAT curves and track promotions over 3 years, with Excel export"""
    from collections import defaultdict
    from backend.src.services.simulation.models import Person, Level
    from backend.config.progression_config import PROGRESSION_CONFIG
    from backend.src.services.simulation.office_manager import OfficeManager
    
    # Get the realistic population
    pop = get_saved_population()
    
    # Initialize tracking
    promotion_history = []
    level_populations = {}
    monthly_stats = []
    
    # Initialize level populations
    for fte in pop:
        level = fte['level']
        if level not in level_populations:
            level_populations[level] = []
        level_populations[level].append({
            'id': fte['id'],
            'total_tenure': fte['total_tenure'],
            'months_on_level': fte['months_on_level'],
            'current_level': level,
            'promoted': False,
            'promotion_month': None
        })
    
    # Simulate 36 months
    for month in range(36):
        year = 2025 + (month // 12)
        month_num = 1 + (month % 12)
        date = f"{year}-{month_num:02d}"
        
        month_promotions = []
        month_stats = {
            'date': date,
            'total_promotions': 0,
            'promotions_by_level': {},
            'population_by_level': {}
        }
        
        # Track current population
        for level in PROGRESSION_CONFIG.keys():
            month_stats['population_by_level'][level] = len(level_populations.get(level, []))
        
        # Process each level for progression
        for level, ftes in list(level_populations.items()):
            config = PROGRESSION_CONFIG.get(level, {})
            progression_months = config.get('progression_months', [1])
            next_level = config.get('next_level')
            
            # Only process in progression months
            if month_num not in progression_months:
                continue
                
            if not next_level:
                continue  # No progression possible (e.g., OPE)
            
            level_promotions = 0
            
            # Process each FTE in this level
            for fte in ftes[:]:  # Copy list to avoid modification during iteration
                if fte['promoted']:
                    continue
                
                # Calculate current time on level
                current_months_on_level = fte['months_on_level'] + month
                
                # Determine CAT based on time on level
                cat = determine_cat(current_months_on_level)
                
                # Get progression probability from CAT curve
                progression_prob = get_progression_probability(level, cat)
                
                # Simulate progression
                if random.random() < progression_prob:
                    # Promotion occurs
                    fte['promoted'] = True
                    fte['promotion_month'] = date
                    level_promotions += 1
                    
                    # Move to next level
                    if next_level not in level_populations:
                        level_populations[next_level] = []
                    
                    promoted_fte = {
                        'id': fte['id'],
                        'total_tenure': fte['total_tenure'] + month,
                        'months_on_level': 0,  # Reset for new level
                        'current_level': next_level,
                        'promoted': False,
                        'promotion_month': None
                    }
                    level_populations[next_level].append(promoted_fte)
                    
                    # Remove from current level
                    ftes.remove(fte)
                    
                    # Record promotion
                    promotion_history.append({
                        'date': date,
                        'fte_id': fte['id'],
                        'from_level': level,
                        'to_level': next_level,
                        'months_on_level': current_months_on_level,
                        'cat': cat,
                        'probability': progression_prob
                    })
            
            month_stats['promotions_by_level'][level] = level_promotions
            month_stats['total_promotions'] += level_promotions
        
        monthly_stats.append(month_stats)
    
    # Export to Excel
    export_promotions_to_excel(promotion_history, monthly_stats)
    
    # Print summary statistics
    print(f"\n=== PROGRESSION SIMULATION SUMMARY ===")
    print(f"Total promotions over 3 years: {len(promotion_history)}")
    print(f"Average promotions per month: {len(promotion_history)/36:.2f}")
    
    # Print final population by level
    print(f"\nFinal population by level:")
    for level in sorted(PROGRESSION_CONFIG.keys()):
        count = len(level_populations.get(level, []))
        print(f"  {level}: {count} FTEs")
    
    # Print promotion statistics by level
    print(f"\nPromotion statistics by level:")
    level_promotions = defaultdict(list)
    for promo in promotion_history:
        level_promotions[promo['from_level']].append(promo)
    
    for level in sorted(level_promotions.keys()):
        promos = level_promotions[level]
        avg_months = sum(p['months_on_level'] for p in promos) / len(promos)
        avg_prob = sum(p['probability'] for p in promos) / len(promos)
        print(f"  {level}: {len(promos)} promotions, avg {avg_months:.1f} months on level, avg probability {avg_prob:.3f}")
    
    # Return for further analysis if needed
    return promotion_history, level_populations, monthly_stats

def determine_cat(months_on_level):
    """Determine CAT based on time on level"""
    if months_on_level < 6:
        return 1
    elif months_on_level < 12:
        return 2
    elif months_on_level < 18:
        return 3
    elif months_on_level < 24:
        return 4
    elif months_on_level < 36:
        return 5
    else:
        return 6

def get_progression_probability(level, cat):
    """Get progression probability from CAT_CURVES in progression_config.py"""
    from backend.config.progression_config import CAT_CURVES
    # Map CAT number to CAT category string
    cat_mapping = {
        1: 'CAT0',   # 0-6 months (no progression)
        2: 'CAT6',   # 6-12 months
        3: 'CAT12',  # 12-18 months
        4: 'CAT18',  # 18-24 months
        5: 'CAT24',  # 24-30 months
        6: 'CAT30',  # 30+ months
        7: 'CAT36',  # 36+ months
        8: 'CAT42',  # 42+ months
        9: 'CAT48',  # 48+ months
        10: 'CAT54', # 54+ months
        11: 'CAT60', # 60+ months
    }
    cat_category = cat_mapping.get(cat, 'CAT0')
    probability = CAT_CURVES.get(level, {}).get(cat_category, 0.0)
    return probability

def test_print_realistic_population():
    generate_population() 