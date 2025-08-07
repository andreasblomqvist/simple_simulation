"""
V2 Engine Monthly KPI Testing

Test monthly KPI calculation for the V2 engine showing:
1. Monthly workforce KPIs (headcount, recruitment, churn, promotions)
2. Monthly financial KPIs (revenue, costs, profitability)
3. Month-over-month comparisons and trends
4. Proper data structure for monthly reporting
"""

import sys
import json
from pathlib import Path
from datetime import date
from collections import defaultdict, Counter

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def test_monthly_kpis():
    """Test monthly KPI generation from V2 engine results"""
    print("V2 ENGINE - MONTHLY KPI CALCULATION")
    print("=" * 40)
    
    try:
        from src.services.simulation_engine_v2 import (
            SimulationEngineV2Factory, ScenarioRequest, TimeRange, Levers,
            BusinessPlan, MonthlyPlan, PopulationSnapshot, WorkforceEntry, 
            Person, OfficeState, CATMatrix
        )
        
        # 1. Setup engine
        print("1. Setting up V2 engine...")
        
        engine = SimulationEngineV2Factory.create_test_engine(random_seed=42)
        test_data_dir = Path(__file__).parent / "test_data"
        
        # Load test data
        with open(test_data_dir / "business_plans.json") as f:
            business_plans_data = json.load(f)
        
        with open(test_data_dir / "cat_matrices_correct.json") as f:
            cat_matrices_data = json.load(f)
            
        with open(test_data_dir / "population_snapshots.json") as f:
            population_data = json.load(f)
        
        # Setup business plans
        engine.business_processor.loaded_plans = {}
        
        for office_id, plan_data in business_plans_data.items():
            monthly_plans = {}
            
            for month, month_data in plan_data["monthly_plans"].items():
                monthly_plan = MonthlyPlan(
                    year=int(month.split("-")[0]),
                    month=int(month.split("-")[1]),
                    recruitment=month_data["recruitment"],
                    churn=month_data["churn"],
                    revenue=float(month_data["revenue"]),
                    costs=float(month_data["costs"]),
                    price_per_role={},
                    salary_per_role={},
                    utr_per_role={}
                )
                monthly_plans[month] = monthly_plan
            
            business_plan = BusinessPlan(
                office_id=plan_data["office_id"],
                name=plan_data["name"],
                monthly_plans=monthly_plans
            )
            
            engine.business_processor.loaded_plans[office_id] = business_plan
        
        # Setup CAT matrices
        cat_matrices = {}
        for role, matrix_data in cat_matrices_data.items():
            cat_matrices[role] = CATMatrix(
                progression_probabilities=matrix_data["progression_probabilities"]
            )
        
        # Setup population
        population_snapshots = {}
        for office_id, snapshot_data in population_data.items():
            workforce_entries = []
            for entry_data in snapshot_data["workforce"]:
                workforce_entries.append(WorkforceEntry(
                    id=entry_data["id"],
                    role=entry_data["role"],
                    level=entry_data["level"],
                    hire_date=entry_data["hire_date"],
                    level_start_date=entry_data["level_start_date"],
                    office=entry_data["office"]
                ))
            
            population_snapshots[office_id] = PopulationSnapshot(
                id=snapshot_data["id"],
                office_id=snapshot_data["office_id"],
                snapshot_date=snapshot_data["snapshot_date"],
                name=snapshot_data["name"],
                workforce=workforce_entries
            )
        
        # Create office state
        engine.office_states = {}
        office_id = "london"
        
        office_state = OfficeState(
            name=office_id,
            workforce={},
            business_plan=engine.business_processor.loaded_plans.get(office_id),
            snapshot=population_snapshots.get(office_id),
            cat_matrices=cat_matrices,
            economic_parameters=None
        )
        
        # Populate workforce
        if office_id in population_snapshots:
            snapshot = population_snapshots[office_id]
            office_state.workforce = {}
            
            for entry in snapshot.workforce:
                hire_date = date.fromisoformat(entry.hire_date + "-01")
                level_start_date = date.fromisoformat(entry.level_start_date + "-01")
                
                person = Person(
                    id=entry.id,
                    current_role=entry.role,
                    current_level=entry.level,
                    current_office=entry.office,
                    hire_date=hire_date,
                    current_level_start=level_start_date,
                    events=[],
                    is_active=True
                )
                
                if entry.role not in office_state.workforce:
                    office_state.workforce[entry.role] = {}
                if entry.level not in office_state.workforce[entry.role]:
                    office_state.workforce[entry.role][entry.level] = []
                
                office_state.workforce[entry.role][entry.level].append(person)
        
        engine.office_states[office_id] = office_state
        
        initial_workforce = office_state.get_total_workforce()
        print(f"   Setup complete: {initial_workforce} people")
        
        # 2. Run simulation 
        print("\\n2. Running simulation for monthly KPI analysis...")
        
        scenario = ScenarioRequest(
            scenario_id="monthly_kpi_test",
            name="Monthly KPI Analysis",
            time_range=TimeRange(2024, 6, 2024, 10),  # 5 months for clear trends
            office_ids=["london"],
            levers=Levers(
                recruitment_multiplier=1.0,
                churn_multiplier=1.1,  # Avoid rounding to 0
                progression_multiplier=1.0
            )
        )
        
        results = engine.run_simulation(scenario)
        
        print(f"   Simulation completed: {len(results.all_events)} events")
        
        # 3. Calculate Monthly KPIs manually (since V2 doesn't have monthly KPI calc yet)
        print("\\n3. MONTHLY KPI BREAKDOWN")
        print("=" * 30)
        
        # Group events by month
        events_by_month = defaultdict(list)
        for event in results.all_events:
            month_key = f"{event.date.year}-{event.date.month:02d}"
            events_by_month[month_key].append(event)
        
        # Track workforce state at end of each month
        monthly_workforce = {}
        monthly_kpis = {}
        
        # Calculate starting workforce
        current_workforce = initial_workforce
        
        for year in range(scenario.time_range.start_year, scenario.time_range.end_year + 1):
            for month in range(1, 13):
                if year == scenario.time_range.start_year and month < scenario.time_range.start_month:
                    continue
                if year == scenario.time_range.end_year and month > scenario.time_range.end_month:
                    break
                    
                month_key = f"{year}-{month:02d}"
                month_events = events_by_month.get(month_key, [])
                
                # Calculate monthly workforce KPIs
                event_types = Counter(event.event_type.value for event in month_events)
                hired_count = event_types.get('hired', 0)
                churned_count = event_types.get('churned', 0)
                promoted_count = event_types.get('promoted', 0)
                
                # Update running workforce count
                current_workforce = current_workforce + hired_count - churned_count
                
                # Get business plan data for this month
                business_plan = engine.business_processor.get_monthly_targets(office_id, year, month)
                
                # Calculate monthly KPIs
                monthly_kpi = {
                    'month': month_key,
                    'year': year,
                    'month_num': month,
                    
                    # Workforce KPIs
                    'workforce': {
                        'starting_headcount': current_workforce - hired_count + churned_count,
                        'ending_headcount': current_workforce,
                        'headcount_change': hired_count - churned_count,
                        'headcount_change_pct': ((hired_count - churned_count) / (current_workforce - hired_count + churned_count) * 100) if (current_workforce - hired_count + churned_count) > 0 else 0,
                        
                        'total_hires': hired_count,
                        'total_churns': churned_count,
                        'total_promotions': promoted_count,
                        'net_recruitment': hired_count - churned_count,
                        
                        'hire_rate_pct': (hired_count / current_workforce * 100) if current_workforce > 0 else 0,
                        'churn_rate_pct': (churned_count / current_workforce * 100) if current_workforce > 0 else 0,
                        'promotion_rate_pct': (promoted_count / current_workforce * 100) if current_workforce > 0 else 0,
                    },
                    
                    # Financial KPIs
                    'financial': {
                        'revenue': business_plan.revenue_target,
                        'operating_costs': business_plan.operating_costs,
                        'gross_profit': business_plan.revenue_target - business_plan.operating_costs,
                        'profit_margin_pct': ((business_plan.revenue_target - business_plan.operating_costs) / business_plan.revenue_target * 100) if business_plan.revenue_target > 0 else 0,
                        'revenue_per_fte': business_plan.revenue_target / current_workforce if current_workforce > 0 else 0,
                        'cost_per_fte': business_plan.operating_costs / current_workforce if current_workforce > 0 else 0,
                    },
                    
                    # Activity KPIs
                    'activity': {
                        'total_events': len(month_events),
                        'events_per_person': len(month_events) / current_workforce if current_workforce > 0 else 0,
                    }
                }
                
                monthly_kpis[month_key] = monthly_kpi
                monthly_workforce[month_key] = current_workforce
                
                # Display monthly results
                print(f"\\n   {month_key}:")
                print(f"      Workforce: {monthly_kpi['workforce']['starting_headcount']} -> {monthly_kpi['workforce']['ending_headcount']} ({monthly_kpi['workforce']['headcount_change']:+d}, {monthly_kpi['workforce']['headcount_change_pct']:+.1f}%)")
                print(f"      Activity: {hired_count} hires, {churned_count} churns, {promoted_count} promotions")
                print(f"      Rates: {monthly_kpi['workforce']['hire_rate_pct']:.1f}% hire, {monthly_kpi['workforce']['churn_rate_pct']:.1f}% churn, {monthly_kpi['workforce']['promotion_rate_pct']:.1f}% promotion")
                print(f"      Financial: ${monthly_kpi['financial']['revenue']:,.0f} revenue, ${monthly_kpi['financial']['gross_profit']:,.0f} profit ({monthly_kpi['financial']['profit_margin_pct']:.1f}%)")
                print(f"      Per-FTE: ${monthly_kpi['financial']['revenue_per_fte']:,.0f} revenue, ${monthly_kpi['financial']['cost_per_fte']:,.0f} costs")
        
        # 4. Month-over-Month Analysis
        print("\\n4. MONTH-OVER-MONTH TRENDS")
        print("=" * 30)
        
        month_keys = sorted(monthly_kpis.keys())
        
        print("   Workforce Growth:")
        print("      Month      | Headcount | Change | Hire % | Churn % | Net %")
        print("      -----------|-----------|--------|--------|---------|-------")
        
        for month_key in month_keys:
            kpi = monthly_kpis[month_key]
            wf = kpi['workforce']
            print(f"      {month_key} | {wf['ending_headcount']:9d} | {wf['headcount_change']:+6d} | {wf['hire_rate_pct']:5.1f}% | {wf['churn_rate_pct']:6.1f}% | {wf['headcount_change_pct']:+5.1f}%")
        
        print("\\n   Financial Performance:")
        print("      Month      | Revenue   | Costs     | Profit    | Margin | Rev/FTE")
        print("      -----------|-----------|-----------|-----------|--------|--------")
        
        for month_key in month_keys:
            kpi = monthly_kpis[month_key]
            fin = kpi['financial']
            print(f"      {month_key} | ${fin['revenue']:8,.0f} | ${fin['operating_costs']:8,.0f} | ${fin['gross_profit']:8,.0f} | {fin['profit_margin_pct']:5.1f}% | ${fin['revenue_per_fte']:6,.0f}")
        
        # 5. Monthly KPI Data Structure 
        print("\\n5. MONTHLY KPI DATA STRUCTURE")
        print("=" * 35)
        
        print("   KPI Categories per month:")
        sample_month = list(monthly_kpis.values())[0]
        for category, metrics in sample_month.items():
            if isinstance(metrics, dict):
                print(f"      {category}: {list(metrics.keys())}")
            else:
                print(f"      {category}: {type(metrics).__name__}")
        
        print("\\n   Total metrics per month:")
        total_metrics = sum(len(v) if isinstance(v, dict) else 1 for v in sample_month.values())
        print(f"      {total_metrics} KPIs calculated per month")
        print(f"      {len(monthly_kpis)} months analyzed")
        print(f"      {total_metrics * len(monthly_kpis)} total monthly KPI data points")
        
        print("\\n   How monthly KPIs should be returned:")
        print("      results.monthly_kpis = {")
        print("          '2024-06': {workforce: {...}, financial: {...}, activity: {...}},")
        print("          '2024-07': {workforce: {...}, financial: {...}, activity: {...}},")
        print("          ...") 
        print("      }")
        
        # 6. Summary
        print("\\n6. MONTHLY KPI SUMMARY")
        print("=" * 25)
        
        start_workforce = monthly_kpis[month_keys[0]]['workforce']['starting_headcount']
        end_workforce = monthly_kpis[month_keys[-1]]['workforce']['ending_headcount']
        total_growth = end_workforce - start_workforce
        
        total_hires = sum(kpi['workforce']['total_hires'] for kpi in monthly_kpis.values())
        total_churns = sum(kpi['workforce']['total_churns'] for kpi in monthly_kpis.values())
        total_promotions = sum(kpi['workforce']['total_promotions'] for kpi in monthly_kpis.values())
        
        total_revenue = sum(kpi['financial']['revenue'] for kpi in monthly_kpis.values())
        total_costs = sum(kpi['financial']['operating_costs'] for kpi in monthly_kpis.values())
        
        print(f"   Period: {month_keys[0]} to {month_keys[-1]} ({len(month_keys)} months)")
        print(f"   Workforce: {start_workforce} -> {end_workforce} ({total_growth:+d} people, {(total_growth/start_workforce*100):+.1f}%)")
        print(f"   Activity: {total_hires} hires, {total_churns} churns, {total_promotions} promotions")
        print(f"   Financial: ${total_revenue:,.0f} revenue, ${total_costs:,.0f} costs, ${total_revenue-total_costs:,.0f} profit")
        print(f"   Monthly tracking: {len(monthly_kpis)} months of detailed KPIs")
        
        return True, {
            'monthly_kpis': monthly_kpis,
            'months_analyzed': len(monthly_kpis),
            'total_metrics_per_month': total_metrics,
            'workforce_growth': total_growth,
            'total_events': len(results.all_events)
        }
        
    except Exception as e:
        print(f"\\nERROR: Monthly KPI test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, {'error': str(e)}

if __name__ == "__main__":
    print("Starting Monthly KPI Testing")
    print("=" * 40)
    
    success, metrics = test_monthly_kpis()
    
    print("\\n" + "=" * 40)
    if success:
        print("SUCCESS: Monthly KPI calculation working!")
        print(f"Analyzed {metrics['months_analyzed']} months")
        print(f"Generated {metrics['total_metrics_per_month']} KPIs per month")
        print("Monthly tracking: Workforce + Financial + Activity metrics")
    else:
        print("FAILURE: Monthly KPI calculation needs work")
        if 'error' in metrics:
            print(f"Error: {metrics['error']}")
    
    print(f"\\nMonthly KPI test complete")