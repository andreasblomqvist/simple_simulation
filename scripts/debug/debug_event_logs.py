print('=== DEBUG EVENT LOGS SCRIPT STARTED ===')

def debug_event_logs():
    import sys
    import os
    import random
    from datetime import datetime
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from backend.src.services.simulation_engine import SimulationEngine
    from backend.src.services.config_service import config_service
    from backend.config.progression_config import PROGRESSION_CONFIG, CAT_CURVES

    print("🔍 Debugging Event Logs")
    print("=" * 60)
    random.seed(42)
    engine = SimulationEngine(config_service)
    test_config = {
        "TestOffice": {
            "office_name": "TestOffice",
            "name": "TestOffice",
            "total_fte": 100,
            "journey": "Mature Office",
            "roles": {
                "Consultant": {
                    "A": {"fte": 20, "price_1": 1200, "salary_1": 45000, "utr_1": 0.85},
                    "AC": {"fte": 25, "price_1": 1300, "salary_1": 55000, "utr_1": 0.88},
                    "C": {"fte": 30, "price_1": 1400, "salary_1": 65000, "utr_1": 0.90},
                    "SrC": {"fte": 15, "price_1": 1500, "salary_1": 75000, "utr_1": 0.92},
                    "AM": {"fte": 8, "price_1": 1600, "salary_1": 85000, "utr_1": 0.94},
                    "M": {"fte": 2, "price_1": 1700, "salary_1": 95000, "utr_1": 0.95}
                }
            }
        }
    }
    config_service._config_data = test_config
    config_service._config_checksum = None
    config_service._offices_cache = None
    config_service._last_loaded_checksum = None
    config_service._last_loaded_config = None
    engine.reinitialize_with_config()
    print("✅ Configuration loaded successfully")
    print(f"📊 Test office: {engine.offices['TestOffice'].name}")
    print(f"👥 Total FTE: {engine.offices['TestOffice'].total_fte}")
    test_office = engine.offices['TestOffice']
    consultant_role = test_office.roles['Consultant']
    print("\n👥 Initial Population:")
    for level_name, level in consultant_role.items():
        print(f"  {level_name}: {level.total} people")
        if level.total > 0:
            print(f"    Sample person: {level.people[0] if level.people else 'None'}")
    print("\n🚀 Running 1-year simulation...")
    results = engine.run_simulation(
        start_year=2025, 
        start_month=1, 
        end_year=2025, 
        end_month=12
    )
    print("✅ Simulation completed successfully")
    print("\n👥 Final Population:")
    for level_name, level in consultant_role.items():
        print(f"  {level_name}: {level.total} people")
    print("\n📝 Event Logger Analysis:")
    event_logger = engine.simulation_results.get('event_logger')
    if event_logger:
        print(f"  Event logger type: {type(event_logger)}")
        print(f"  Event logger run_id: {getattr(event_logger, 'run_id', 'None')}")
        all_events = event_logger.get_all_events()
        print(f"  Total events: {len(all_events)}")
        event_types = {}
        for event in all_events:
            event_type = event.get('event_type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
        print(f"  Event types: {event_types}")
        if all_events:
            print("\n📋 Sample Events:")
            for i, event in enumerate(all_events[:5]):
                print(f"  Event {i+1}: {event}")
        else:
            print("  No events found!")
        print("\n🔍 Checking Progression Events:")
        promotion_events = [e for e in all_events if e.get('event_type') == 'promotion']
        print(f"  Promotion events: {len(promotion_events)}")
        if promotion_events:
            print("  Sample promotion events:")
            for i, event in enumerate(promotion_events[:3]):
                print(f"    {i+1}: {event.get('from_level')} -> {event.get('to_level')} on {event.get('date')}")
        else:
            print("  No promotion events found!")
        recruitment_events = [e for e in all_events if e.get('event_type') == 'recruitment']
        churn_events = [e for e in all_events if e.get('event_type') == 'churn']
        print(f"  Recruitment events: {len(recruitment_events)}")
        print(f"  Churn events: {len(churn_events)}")
    else:
        print("  No event logger found in simulation results!")
    print("\n📊 Monthly Metrics Analysis:")
    monthly_metrics = results.get('monthly_office_metrics', {})
    if 'TestOffice' in monthly_metrics:
        office_metrics = monthly_metrics['TestOffice']
        print(f"  Months with data: {len(office_metrics)}")
        for date, month_data in office_metrics.items():
            if 'promotion_details' in month_data:
                details = month_data['promotion_details']
                if details:
                    print(f"  {date}: {len(details)} promotion details")
                    for detail in details[:3]:
                        print(f"    {detail}")
                else:
                    print(f"  {date}: No promotion details")
            else:
                print(f"  {date}: No promotion_details key")
    else:
        print("  No TestOffice found in monthly metrics!")
    return results

if __name__ == "__main__":
    try:
        debug_event_logs()
    except Exception as e:
        import traceback
        print('Exception occurred:')
        traceback.print_exc() 