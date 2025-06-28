#!/usr/bin/env python3
"""
Test edge cases and large data for progression and event logging.
"""

import sys
import os
import random
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.src.services.simulation_engine import SimulationEngine
from backend.src.services.config_service import config_service
from backend.config.progression_config import PROGRESSION_CONFIG

def test_edge_cases_event_logs():
    print('=== EDGE CASES & LARGE DATA EVENT LOG TEST ===')
    random.seed(123)

    # 1. Large, diverse config with edge cases
    test_config = {
        "OfficeA": {
            "office_name": "OfficeA",
            "name": "OfficeA",
            "total_fte": 200,
            "journey": "Mature Office",
            "roles": {
                "Consultant": {
                    # Edge: Just below and above minimum tenure for A
                    "A": {
                        "fte": 10, "price_1": 1200, "salary_1": 45000, "utr_1": 0.85,
                        "recruitment_1": 0.03, "churn_1": 0.02,  # 3% recruitment, 2% churn
                        "recruitment_2": 0.03, "churn_2": 0.02,
                        "recruitment_3": 0.03, "churn_3": 0.02,
                        "recruitment_4": 0.03, "churn_4": 0.02,
                        "recruitment_5": 0.03, "churn_5": 0.02,
                        "recruitment_6": 0.03, "churn_6": 0.02,
                        "recruitment_7": 0.03, "churn_7": 0.02,
                        "recruitment_8": 0.03, "churn_8": 0.02,
                        "recruitment_9": 0.03, "churn_9": 0.02,
                        "recruitment_10": 0.03, "churn_10": 0.02,
                        "recruitment_11": 0.03, "churn_11": 0.02,
                        "recruitment_12": 0.03, "churn_12": 0.02
                    },
                    "AC": {
                        "fte": 10, "price_1": 1300, "salary_1": 55000, "utr_1": 0.88,
                        "recruitment_1": 0.03, "churn_1": 0.02,  # 3% recruitment, 2% churn
                        "recruitment_2": 0.03, "churn_2": 0.02,
                        "recruitment_3": 0.03, "churn_3": 0.02,
                        "recruitment_4": 0.03, "churn_4": 0.02,
                        "recruitment_5": 0.03, "churn_5": 0.02,
                        "recruitment_6": 0.03, "churn_6": 0.02,
                        "recruitment_7": 0.03, "churn_7": 0.02,
                        "recruitment_8": 0.03, "churn_8": 0.02,
                        "recruitment_9": 0.03, "churn_9": 0.02,
                        "recruitment_10": 0.03, "churn_10": 0.02,
                        "recruitment_11": 0.03, "churn_11": 0.02,
                        "recruitment_12": 0.03, "churn_12": 0.02
                    },
                    # Edge: Large C population, some with CAT0
                    "C": {
                        "fte": 80, "price_1": 1400, "salary_1": 65000, "utr_1": 0.90,
                        "recruitment_1": 0.03, "churn_1": 0.02,  # 3% recruitment, 2% churn
                        "recruitment_2": 0.03, "churn_2": 0.02,
                        "recruitment_3": 0.03, "churn_3": 0.02,
                        "recruitment_4": 0.03, "churn_4": 0.02,
                        "recruitment_5": 0.03, "churn_5": 0.02,
                        "recruitment_6": 0.03, "churn_6": 0.02,
                        "recruitment_7": 0.03, "churn_7": 0.02,
                        "recruitment_8": 0.03, "churn_8": 0.02,
                        "recruitment_9": 0.03, "churn_9": 0.02,
                        "recruitment_10": 0.03, "churn_10": 0.02,
                        "recruitment_11": 0.03, "churn_11": 0.02,
                        "recruitment_12": 0.03, "churn_12": 0.02
                    },
                    # Edge: Top level - only churn, no recruitment
                    "M": {
                        "fte": 5, "price_1": 1700, "salary_1": 95000, "utr_1": 0.95,
                        "recruitment_1": 0.0, "churn_1": 0.02,  # 0% recruitment, 2% churn
                        "recruitment_2": 0.0, "churn_2": 0.02,
                        "recruitment_3": 0.0, "churn_3": 0.02,
                        "recruitment_4": 0.0, "churn_4": 0.02,
                        "recruitment_5": 0.0, "churn_5": 0.02,
                        "recruitment_6": 0.0, "churn_6": 0.02,
                        "recruitment_7": 0.0, "churn_7": 0.02,
                        "recruitment_8": 0.0, "churn_8": 0.02,
                        "recruitment_9": 0.0, "churn_9": 0.02,
                        "recruitment_10": 0.0, "churn_10": 0.02,
                        "recruitment_11": 0.0, "churn_11": 0.02,
                        "recruitment_12": 0.0, "churn_12": 0.02
                    }
                },
                "Sales": {
                    "A": {
                        "fte": 5, "price_1": 1000, "salary_1": 40000, "utr_1": 0.80,
                        "recruitment_1": 0.03, "churn_1": 0.02,  # 3% recruitment, 2% churn
                        "recruitment_2": 0.03, "churn_2": 0.02,
                        "recruitment_3": 0.03, "churn_3": 0.02,
                        "recruitment_4": 0.03, "churn_4": 0.02,
                        "recruitment_5": 0.03, "churn_5": 0.02,
                        "recruitment_6": 0.03, "churn_6": 0.02,
                        "recruitment_7": 0.03, "churn_7": 0.02,
                        "recruitment_8": 0.03, "churn_8": 0.02,
                        "recruitment_9": 0.03, "churn_9": 0.02,
                        "recruitment_10": 0.03, "churn_10": 0.02,
                        "recruitment_11": 0.03, "churn_11": 0.02,
                        "recruitment_12": 0.03, "churn_12": 0.02
                    },
                    "C": {
                        "fte": 5, "price_1": 1200, "salary_1": 50000, "utr_1": 0.85,
                        "recruitment_1": 0.03, "churn_1": 0.02,  # 3% recruitment, 2% churn
                        "recruitment_2": 0.03, "churn_2": 0.02,
                        "recruitment_3": 0.03, "churn_3": 0.02,
                        "recruitment_4": 0.03, "churn_4": 0.02,
                        "recruitment_5": 0.03, "churn_5": 0.02,
                        "recruitment_6": 0.03, "churn_6": 0.02,
                        "recruitment_7": 0.03, "churn_7": 0.02,
                        "recruitment_8": 0.03, "churn_8": 0.02,
                        "recruitment_9": 0.03, "churn_9": 0.02,
                        "recruitment_10": 0.03, "churn_10": 0.02,
                        "recruitment_11": 0.03, "churn_11": 0.02,
                        "recruitment_12": 0.03, "churn_12": 0.02
                    }
                }
            }
        },
        "OfficeB": {
            "office_name": "OfficeB",
            "name": "OfficeB",
            "total_fte": 150,
            "journey": "Emerging Office",
            "roles": {
                "Consultant": {
                    "A": {
                        "fte": 20, "price_1": 1200, "salary_1": 45000, "utr_1": 0.85,
                        "recruitment_1": 0.03, "churn_1": 0.02,  # 3% recruitment, 2% churn
                        "recruitment_2": 0.03, "churn_2": 0.02,
                        "recruitment_3": 0.03, "churn_3": 0.02,
                        "recruitment_4": 0.03, "churn_4": 0.02,
                        "recruitment_5": 0.03, "churn_5": 0.02,
                        "recruitment_6": 0.03, "churn_6": 0.02,
                        "recruitment_7": 0.03, "churn_7": 0.02,
                        "recruitment_8": 0.03, "churn_8": 0.02,
                        "recruitment_9": 0.03, "churn_9": 0.02,
                        "recruitment_10": 0.03, "churn_10": 0.02,
                        "recruitment_11": 0.03, "churn_11": 0.02,
                        "recruitment_12": 0.03, "churn_12": 0.02
                    },
                    "AC": {
                        "fte": 20, "price_1": 1300, "salary_1": 55000, "utr_1": 0.88,
                        "recruitment_1": 0.03, "churn_1": 0.02,  # 3% recruitment, 2% churn
                        "recruitment_2": 0.03, "churn_2": 0.02,
                        "recruitment_3": 0.03, "churn_3": 0.02,
                        "recruitment_4": 0.03, "churn_4": 0.02,
                        "recruitment_5": 0.03, "churn_5": 0.02,
                        "recruitment_6": 0.03, "churn_6": 0.02,
                        "recruitment_7": 0.03, "churn_7": 0.02,
                        "recruitment_8": 0.03, "churn_8": 0.02,
                        "recruitment_9": 0.03, "churn_9": 0.02,
                        "recruitment_10": 0.03, "churn_10": 0.02,
                        "recruitment_11": 0.03, "churn_11": 0.02,
                        "recruitment_12": 0.03, "churn_12": 0.02
                    },
                    "C": {
                        "fte": 30, "price_1": 1400, "salary_1": 65000, "utr_1": 0.90,
                        "recruitment_1": 0.03, "churn_1": 0.02,  # 3% recruitment, 2% churn
                        "recruitment_2": 0.03, "churn_2": 0.02,
                        "recruitment_3": 0.03, "churn_3": 0.02,
                        "recruitment_4": 0.03, "churn_4": 0.02,
                        "recruitment_5": 0.03, "churn_5": 0.02,
                        "recruitment_6": 0.03, "churn_6": 0.02,
                        "recruitment_7": 0.03, "churn_7": 0.02,
                        "recruitment_8": 0.03, "churn_8": 0.02,
                        "recruitment_9": 0.03, "churn_9": 0.02,
                        "recruitment_10": 0.03, "churn_10": 0.02,
                        "recruitment_11": 0.03, "churn_11": 0.02,
                        "recruitment_12": 0.03, "churn_12": 0.02
                    },
                    "SrC": {
                        "fte": 10, "price_1": 1500, "salary_1": 75000, "utr_1": 0.92,
                        "recruitment_1": 0.03, "churn_1": 0.02,  # 3% recruitment, 2% churn
                        "recruitment_2": 0.03, "churn_2": 0.02,
                        "recruitment_3": 0.03, "churn_3": 0.02,
                        "recruitment_4": 0.03, "churn_4": 0.02,
                        "recruitment_5": 0.03, "churn_5": 0.02,
                        "recruitment_6": 0.03, "churn_6": 0.02,
                        "recruitment_7": 0.03, "churn_7": 0.02,
                        "recruitment_8": 0.03, "churn_8": 0.02,
                        "recruitment_9": 0.03, "churn_9": 0.02,
                        "recruitment_10": 0.03, "churn_10": 0.02,
                        "recruitment_11": 0.03, "churn_11": 0.02,
                        "recruitment_12": 0.03, "churn_12": 0.02
                    },
                    "AM": {
                        "fte": 5, "price_1": 1600, "salary_1": 85000, "utr_1": 0.94,
                        "recruitment_1": 0.0, "churn_1": 0.02,  # 0% recruitment, 2% churn
                        "recruitment_2": 0.0, "churn_2": 0.02,
                        "recruitment_3": 0.0, "churn_3": 0.02,
                        "recruitment_4": 0.0, "churn_4": 0.02,
                        "recruitment_5": 0.0, "churn_5": 0.02,
                        "recruitment_6": 0.0, "churn_6": 0.02,
                        "recruitment_7": 0.0, "churn_7": 0.02,
                        "recruitment_8": 0.0, "churn_8": 0.02,
                        "recruitment_9": 0.0, "churn_9": 0.02,
                        "recruitment_10": 0.0, "churn_10": 0.02,
                        "recruitment_11": 0.0, "churn_11": 0.02,
                        "recruitment_12": 0.0, "churn_12": 0.02
                    }
                },
                "Recruitment": {
                    "A": {
                        "fte": 3, "price_1": 900, "salary_1": 35000, "utr_1": 0.75,
                        "recruitment_1": 0.03, "churn_1": 0.02,  # 3% recruitment, 2% churn
                        "recruitment_2": 0.03, "churn_2": 0.02,
                        "recruitment_3": 0.03, "churn_3": 0.02,
                        "recruitment_4": 0.03, "churn_4": 0.02,
                        "recruitment_5": 0.03, "churn_5": 0.02,
                        "recruitment_6": 0.03, "churn_6": 0.02,
                        "recruitment_7": 0.03, "churn_7": 0.02,
                        "recruitment_8": 0.03, "churn_8": 0.02,
                        "recruitment_9": 0.03, "churn_9": 0.02,
                        "recruitment_10": 0.03, "churn_10": 0.02,
                        "recruitment_11": 0.03, "churn_11": 0.02,
                        "recruitment_12": 0.03, "churn_12": 0.02
                    }
                }
            }
        }
    }

    # 2. Patch config_service
    config_service._config_data = test_config
    config_service._config_checksum = None
    config_service._offices_cache = None
    config_service._last_loaded_checksum = None
    config_service._last_loaded_config = None

    # 3. Run simulation (2 years, to catch all edge cases)
    engine = SimulationEngine(config_service)
    engine.reinitialize_with_config()
    print('✅ Configuration loaded')
    results = engine.run_simulation(
        start_year=2025, start_month=1, end_year=2026, end_month=12
    )
    print('✅ Simulation completed')

    # 4. Analyze event logs
    event_logger = results.get('event_logger')
    if not event_logger:
        print('❌ No event logger found!')
        return
    all_events = event_logger.get_all_events()
    print(f'🔎 Total events: {len(all_events)}')
    
    # Debug: Check actual event_type values
    unique_event_types = set()
    for event in all_events:
        event_type = event.get('event_type', 'unknown')
        unique_event_types.add(event_type)
    print(f'🔍 Unique event types found: {unique_event_types}')

    # Print the raw event_type for the first 10 events
    print('\n🔬 Raw event_type values for first 10 events:')
    for i, event in enumerate(all_events[:10]):
        print(f'  Event {i}: event_type={event.get("event_type")!r}')

    event_types = {}
    for event in all_events:
        event_type = event.get('event_type', 'unknown')
        event_types[event_type] = event_types.get(event_type, 0) + 1
    print(f'🔎 Event types: {event_types}')

    # 5. Edge case checks
    # a) Promotions in disallowed months
    disallowed_promos = [e for e in all_events if e.get('event_type') == 'promotion' and e.get('from_level') in PROGRESSION_CONFIG and int(e.get('date').split('-')[1]) not in PROGRESSION_CONFIG[e.get('from_level')]['progression_months']]
    print(f'❌ Promotions in disallowed months: {len(disallowed_promos)}')
    if disallowed_promos:
        for e in disallowed_promos[:3]:
            print(f'  {e}')

    # b) Promotions with insufficient tenure
    insufficient_tenure = [e for e in all_events if e.get('event_type') == 'promotion' and e.get('from_level') in PROGRESSION_CONFIG and e.get('time_on_level_months', 0) < PROGRESSION_CONFIG[e.get('from_level')]['time_on_level']]
    print(f'❌ Promotions with insufficient tenure: {len(insufficient_tenure)}')
    if insufficient_tenure:
        for e in insufficient_tenure[:3]:
            print(f'  {e}')

    # c) Promotions from top level
    top_level_promos = [e for e in all_events if e.get('event_type') == 'promotion' and PROGRESSION_CONFIG.get(e.get('from_level'), {}).get('next_level') == e.get('from_level')]
    print(f'❌ Promotions from top level: {len(top_level_promos)}')
    if top_level_promos:
        for e in top_level_promos[:3]:
            print(f'  {e}')

    # d) Promotions with CAT0
    cat0_promos = [e for e in all_events if e.get('event_type') == 'promotion' and e.get('cat_category') == 'CAT0']
    print(f'❌ Promotions with CAT0: {len(cat0_promos)}')
    if cat0_promos:
        for e in cat0_promos[:3]:
            print(f'  {e}')

    # e) Churn and recruitment events - robust enum value filtering
    def get_event_type_value(e):
        t = e.get('event_type')
        return getattr(t, 'value', str(t))

    churn_events = [e for e in all_events if get_event_type_value(e) == 'churn']
    recruitment_events = [e for e in all_events if get_event_type_value(e) == 'recruitment']
    print(f'✅ Churn events: {len(churn_events)}')
    print(f'✅ Recruitment events: {len(recruitment_events)}')
    
    # Debug: Show a few sample churn and recruitment events
    if churn_events:
        print('\n📋 Sample Churn Events:')
        for e in churn_events[:3]:
            print(f'  {e}')
    
    if recruitment_events:
        print('\n📋 Sample Recruitment Events:')
        for e in recruitment_events[:3]:
            print(f'  {e}')

    # f) Simultaneous promotions
    promo_counts = {}
    for e in all_events:
        if e.get('event_type') == 'promotion':
            key = (e.get('date'), e.get('from_level'), e.get('office'))
            promo_counts[key] = promo_counts.get(key, 0) + 1
    max_simul = max(promo_counts.values()) if promo_counts else 0
    print(f'✅ Max simultaneous promotions in a single cohort: {max_simul}')

    # g) Print a few sample events
    print('\n📋 Sample Promotion Events:')
    promo_events = [e for e in all_events if e.get('event_type') == 'promotion']
    for e in promo_events[:5]:
        print(f'  {e}')

    # === DEEP ANALYSIS OF ALL EVENTS ===
    print('\n=== DEEP ANALYSIS OF ALL EVENTS ===')
    from collections import defaultdict, Counter

    # 1. Summarize event counts by type, month, level, role, office
    event_summary = defaultdict(lambda: Counter())
    for e in all_events:
        etype = get_event_type_value(e)
        key = (etype, e.get('date'), e.get('level'), e.get('role'), e.get('office'))
        event_summary[key] += Counter({'count': 1})
    print('\nEvent counts by type, month, level, role, office:')
    for key, count in sorted(event_summary.items()):
        print(f'  {key}: {count["count"]}')

    # 2. Check logic for each event type
    print('\nLogic checks:')
    # a) Promotions
    bad_promos = []
    for e in all_events:
        if get_event_type_value(e) == 'promotion':
            from_level = e.get('from_level')
            date = e.get('date')
            month = int(date.split('-')[1])
            tenure = e.get('time_on_level_months', 0)
            cat = e.get('cat_category')
            # Allowed months
            if from_level in PROGRESSION_CONFIG:
                allowed_months = PROGRESSION_CONFIG[from_level]['progression_months']
                min_tenure = PROGRESSION_CONFIG[from_level]['time_on_level']
                next_level = PROGRESSION_CONFIG[from_level]['next_level']
                if month not in allowed_months:
                    bad_promos.append(('disallowed_month', e))
                if tenure < min_tenure:
                    bad_promos.append(('insufficient_tenure', e))
                if next_level == from_level:
                    bad_promos.append(('from_top_level', e))
            if cat == 'CAT0':
                bad_promos.append(('cat0', e))
    if bad_promos:
        print(f'❌ Promotion logic errors: {len(bad_promos)}')
        for reason, e in bad_promos[:5]:
            print(f'  {reason}: {e}')
    else:
        print('✅ All promotions pass logic checks')

    # b) Churn: Only from existing FTE, matches expected rates
    # c) Recruitment: Only to levels with recruitment > 0, matches expected rates
    # For these, we will aggregate expected churn/recruitment per month/level/role/office
    # and compare to event counts
    # First, reconstruct the config for easy lookup
    def get_monthly_rate(config, office, role, level, month, rate_type):
        try:
            return config[office]['roles'][role][level][f'{rate_type}_{month}']
        except Exception:
            return 0.0
    # Build FTE tracker
    fte_tracker = defaultdict(lambda: 0)
    # Initialize FTEs
    for office, odata in test_config.items():
        for role, rdata in odata['roles'].items():
            for level, ldata in rdata.items():
                fte_tracker[(office, role, level)] += ldata.get('fte', 0)
    # Simulate month by month
    from collections import defaultdict
    fte_monthly = defaultdict(list)  # (office, role, level) -> list of FTEs per month
    months = []
    for year in [2025, 2026]:
        for m in range(1, 13):
            months.append(f'{year}-{m}')
    # Track FTEs and events
    fte_by_month = {k: [v] for k, v in fte_tracker.items()}
    for month in months:
        # Count churn and recruitment events for this month
        churn_counts = defaultdict(int)
        recruit_counts = defaultdict(int)
        for e in all_events:
            if e.get('date') == month:
                k = (e.get('office'), e.get('role'), e.get('level'))
                if get_event_type_value(e) == 'churn':
                    churn_counts[k] += 1
                if get_event_type_value(e) == 'recruitment':
                    recruit_counts[k] += 1
        # Apply churn
        for k, fte in fte_tracker.items():
            office, role, level = k
            churn_rate = get_monthly_rate(test_config, office, role, level, int(month.split('-')[1]), 'churn')
            expected_churn = int(fte * churn_rate)
            actual_churn = churn_counts[k]
            if actual_churn != expected_churn:
                print(f'❌ Churn mismatch {month} {k}: expected {expected_churn}, got {actual_churn}')
            fte_tracker[k] -= actual_churn
        # Apply recruitment
        for k, fte in fte_tracker.items():
            office, role, level = k
            recruit_rate = get_monthly_rate(test_config, office, role, level, int(month.split('-')[1]), 'recruitment')
            expected_recruit = int(fte * recruit_rate)
            actual_recruit = recruit_counts[k]
            if actual_recruit != expected_recruit:
                print(f'❌ Recruitment mismatch {month} {k}: expected {expected_recruit}, got {actual_recruit}')
            fte_tracker[k] += actual_recruit
        # Save FTEs for this month
        for k in fte_tracker:
            fte_by_month[k].append(fte_tracker[k])
    print('\n✅ Deep analysis complete. See above for any mismatches or errors.')

    # === AGGREGATE TOTALS OVER WHOLE SIMULATION ===
    print('\n=== AGGREGATE TOTALS OVER WHOLE SIMULATION ===')
    
    # Calculate expected totals over the whole simulation
    expected_churn_totals = defaultdict(int)
    expected_recruitment_totals = defaultdict(int)
    
    # Initialize starting FTEs
    starting_fte = defaultdict(int)
    for office, odata in test_config.items():
        for role, rdata in odata['roles'].items():
            for level, ldata in rdata.items():
                starting_fte[(office, role, level)] = ldata.get('fte', 0)
    
    # Calculate expected events over all months
    for month in months:
        year, month_num = month.split('-')
        month_num = int(month_num)
        
        for office, odata in test_config.items():
            for role, rdata in odata['roles'].items():
                for level, ldata in rdata.items():
                    key = (office, role, level)
                    
                    # Get rates for this month
                    churn_rate = get_monthly_rate(test_config, office, role, level, month_num, 'churn')
                    recruitment_rate = get_monthly_rate(test_config, office, role, level, month_num, 'recruitment')
                    
                    # Use starting FTE for expected calculation (simplified)
                    # In reality, FTE changes over time, but this gives us a baseline
                    fte = starting_fte[key]
                    
                    expected_churn_totals[key] += int(fte * churn_rate)
                    expected_recruitment_totals[key] += int(fte * recruitment_rate)
    
    # Calculate actual totals from events
    actual_churn_totals = defaultdict(int)
    actual_recruitment_totals = defaultdict(int)
    
    for e in all_events:
        key = (e.get('office'), e.get('role'), e.get('level'))
        if get_event_type_value(e) == 'churn':
            actual_churn_totals[key] += 1
        elif get_event_type_value(e) == 'recruitment':
            actual_recruitment_totals[key] += 1
    
    # Compare totals
    print('\nChurn totals comparison:')
    print('(office, role, level): expected vs actual')
    for key in sorted(set(expected_churn_totals.keys()) | set(actual_churn_totals.keys())):
        expected = expected_churn_totals[key]
        actual = actual_churn_totals[key]
        status = '✅' if expected == actual else '❌'
        print(f'{status} {key}: {expected} vs {actual}')
    
    print('\nRecruitment totals comparison:')
    print('(office, role, level): expected vs actual')
    for key in sorted(set(expected_recruitment_totals.keys()) | set(actual_recruitment_totals.keys())):
        expected = expected_recruitment_totals[key]
        actual = actual_recruitment_totals[key]
        status = '✅' if expected == actual else '❌'
        print(f'{status} {key}: {expected} vs {actual}')
    
    # Overall summary
    total_expected_churn = sum(expected_churn_totals.values())
    total_actual_churn = sum(actual_churn_totals.values())
    total_expected_recruitment = sum(expected_recruitment_totals.values())
    total_actual_recruitment = sum(actual_recruitment_totals.values())
    
    print(f'\nOverall Summary:')
    print(f'Churn: {total_expected_churn} expected vs {total_actual_churn} actual')
    print(f'Recruitment: {total_expected_recruitment} expected vs {total_actual_recruitment} actual')
    
    if total_expected_churn == total_actual_churn and total_expected_recruitment == total_actual_recruitment:
        print('✅ Aggregate totals match perfectly!')
    else:
        print('❌ Aggregate totals have discrepancies (likely due to FTE changes over time)')

if __name__ == "__main__":
    test_edge_cases_event_logs() 