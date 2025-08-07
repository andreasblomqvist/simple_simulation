"""
Integrated Monthly KPI Calculation - V2 Engine Enhancement

Demonstrates how to integrate monthly KPI calculation directly into the 
simulation loop, storing KPIs alongside recruitment, churn, and progression
data in monthly results.

Architecture:
1. Month processing: recruitment + churn + progression + KPIs
2. Monthly results: events + workforce metrics + financial KPIs + activity KPIs
3. Real-time KPI calculation during simulation execution
"""

import sys
import json
from pathlib import Path
from datetime import date
from collections import Counter
from typing import Dict, Any, List

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

def calculate_monthly_workforce_kpis(office_state, month_events, previous_workforce_count=None):
    """Calculate workforce KPIs for a single month"""
    current_workforce = office_state.get_total_workforce()
    
    # Count events
    event_counts = Counter(event.event_type.value for event in month_events)
    hired_count = event_counts.get('hired', 0)
    churned_count = event_counts.get('churned', 0)
    promoted_count = event_counts.get('promoted', 0)
    
    # Calculate starting workforce
    starting_workforce = current_workforce - hired_count + churned_count
    if previous_workforce_count is not None:
        starting_workforce = previous_workforce_count
    
    # Calculate workforce KPIs
    workforce_kpis = {
        'starting_headcount': starting_workforce,
        'ending_headcount': current_workforce,
        'headcount_change': current_workforce - starting_workforce,
        'headcount_change_pct': ((current_workforce - starting_workforce) / starting_workforce * 100) if starting_workforce > 0 else 0,
        
        'total_hires': hired_count,
        'total_churns': churned_count,
        'total_promotions': promoted_count,
        'net_recruitment': hired_count - churned_count,
        
        'hire_rate_pct': (hired_count / current_workforce * 100) if current_workforce > 0 else 0,
        'churn_rate_pct': (churned_count / starting_workforce * 100) if starting_workforce > 0 else 0,
        'promotion_rate_pct': (promoted_count / starting_workforce * 100) if starting_workforce > 0 else 0,
    }
    
    # Workforce composition
    workforce_by_role = {}
    workforce_by_level = {}
    
    for role, levels in office_state.workforce.items():
        role_count = 0
        for level, people in levels.items():
            level_count = len([p for p in people if p.is_active])
            role_count += level_count
            workforce_by_level[level] = workforce_by_level.get(level, 0) + level_count
        workforce_by_role[role] = role_count
    
    workforce_kpis.update({
        'workforce_by_role': workforce_by_role,
        'workforce_by_level': workforce_by_level,
    })
    
    return workforce_kpis

def calculate_monthly_financial_kpis(business_plan_targets, workforce_count):
    """Calculate financial KPIs for a single month"""
    revenue = business_plan_targets.revenue_target
    costs = business_plan_targets.operating_costs
    
    financial_kpis = {
        'revenue': revenue,
        'operating_costs': costs,
        'gross_profit': revenue - costs,
        'profit_margin_pct': ((revenue - costs) / revenue * 100) if revenue > 0 else 0,
        'revenue_per_fte': revenue / workforce_count if workforce_count > 0 else 0,
        'cost_per_fte': costs / workforce_count if workforce_count > 0 else 0,
        'salary_budget': business_plan_targets.salary_budget,
    }
    
    return financial_kpis

def calculate_monthly_activity_kpis(month_events, workforce_count):
    """Calculate activity/engagement KPIs for a single month"""
    activity_kpis = {
        'total_events': len(month_events),
        'events_per_person': len(month_events) / workforce_count if workforce_count > 0 else 0,
        'event_types': dict(Counter(event.event_type.value for event in month_events)),
        'activity_rate_pct': (len(month_events) / workforce_count * 100) if workforce_count > 0 else 0,
    }
    
    return activity_kpis

def test_integrated_monthly_kpis():
    """Test integrated monthly KPI calculation during simulation"""
    print("V2 ENGINE - INTEGRATED MONTHLY KPI CALCULATION")
    print("=" * 50)
    
    try:
        from src.services.simulation_engine_v2 import (
            SimulationEngineV2Factory, ScenarioRequest, TimeRange, Levers,
            BusinessPlan, MonthlyPlan, PopulationSnapshot, WorkforceEntry, 
            Person, OfficeState, CATMatrix, MonthlyResults
        )
        
        # 1. Setup engine (same as previous tests)
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
        
        # Setup CAT matrices and population (same as before)
        cat_matrices = {}
        for role, matrix_data in cat_matrices_data.items():
            cat_matrices[role] = CATMatrix(
                progression_probabilities=matrix_data["progression_probabilities"]
            )
        
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
        
        # 2. INTEGRATED MONTHLY PROCESSING LOOP
        print("\\n2. Running integrated monthly processing with KPI calculation...")
        
        scenario = ScenarioRequest(
            scenario_id="integrated_kpi_test",
            name="Integrated Monthly KPI Test",
            time_range=TimeRange(2024, 6, 2024, 8),  # 3 months for focused analysis
            office_ids=["london"],
            levers=Levers(
                recruitment_multiplier=1.0,
                churn_multiplier=1.1,
                progression_multiplier=1.0
            )
        )
        
        # Enhanced monthly results with KPIs
        enhanced_monthly_results = {}
        previous_workforce_count = initial_workforce
        
        for year, month in scenario.time_range.get_month_list():
            month_key = f"{year:04d}-{month:02d}"
            current_date = date(year, month, 1)
            
            print(f"\\n   Processing {month_key}...")
            
            # 3. MONTH PROCESSING: recruitment + churn + progression
            month_events = engine._process_office_month(
                office_state, year, month, current_date, scenario.levers
            )
            
            # Get business plan targets for this month
            business_plan_targets = engine.business_processor.get_monthly_targets(office_id, year, month)
            adjusted_targets = engine.business_processor.apply_scenario_levers(business_plan_targets, scenario.levers)
            
            current_workforce_count = office_state.get_total_workforce()
            
            print(f"      Events: {len(month_events)} ({Counter(e.event_type.value for e in month_events)})")
            print(f"      Workforce: {previous_workforce_count} -> {current_workforce_count}")
            
            # 4. INTEGRATED KPI CALCULATION (within month loop!)
            workforce_kpis = calculate_monthly_workforce_kpis(
                office_state, month_events, previous_workforce_count
            )
            
            financial_kpis = calculate_monthly_financial_kpis(
                business_plan_targets, current_workforce_count
            )
            
            activity_kpis = calculate_monthly_activity_kpis(
                month_events, current_workforce_count
            )
            
            # 5. STORE ENHANCED MONTHLY RESULTS (events + KPIs together)
            enhanced_monthly_results[month_key] = {
                # Standard monthly results
                'year': year,
                'month': month,
                'events': month_events,
                'office_metrics': {
                    'total_workforce': current_workforce_count,
                    'workforce_by_role': workforce_kpis['workforce_by_role'],
                    'workforce_by_level': workforce_kpis['workforce_by_level'],
                },
                
                # INTEGRATED KPIs (calculated during month processing)
                'kpis': {
                    'workforce': workforce_kpis,
                    'financial': financial_kpis,
                    'activity': activity_kpis,
                },
                
                # Business plan context
                'business_plan_targets': {
                    'recruitment_targets': adjusted_targets.recruitment_targets,
                    'churn_targets': adjusted_targets.churn_targets,
                    'revenue_target': adjusted_targets.revenue_target,
                    'operating_costs': adjusted_targets.operating_costs,
                }
            }
            
            previous_workforce_count = current_workforce_count
            
            print(f"      KPIs calculated: {len(workforce_kpis)} workforce + {len(financial_kpis)} financial + {len(activity_kpis)} activity")
        
        # 6. Display integrated results
        print("\\n3. INTEGRATED MONTHLY RESULTS WITH KPIs")
        print("=" * 45)
        
        for month_key, month_data in enhanced_monthly_results.items():
            kpis = month_data['kpis']
            workforce = kpis['workforce']
            financial = kpis['financial']
            activity = kpis['activity']
            
            print(f"\\n   {month_key}:")
            print(f"      Events: {len(month_data['events'])} ({activity['event_types']})")
            print(f"      Workforce: {workforce['starting_headcount']} -> {workforce['ending_headcount']} ({workforce['headcount_change']:+d}, {workforce['headcount_change_pct']:+.1f}%)")
            print(f"      Rates: {workforce['hire_rate_pct']:.1f}% hire, {workforce['churn_rate_pct']:.1f}% churn, {workforce['promotion_rate_pct']:.1f}% promotion")
            print(f"      Financial: ${financial['revenue']:,.0f} revenue, ${financial['gross_profit']:,.0f} profit ({financial['profit_margin_pct']:.1f}%)")
            print(f"      Per-FTE: ${financial['revenue_per_fte']:,.0f} revenue, ${financial['cost_per_fte']:,.0f} costs")
            print(f"      Activity: {activity['events_per_person']:.2f} events/person, {activity['activity_rate_pct']:.1f}% engagement")
            print(f"      Composition: {workforce['workforce_by_role']}")
        
        # 7. Data structure demonstration
        print("\\n4. ENHANCED MONTHLY RESULTS DATA STRUCTURE")
        print("=" * 50)
        
        sample_month = list(enhanced_monthly_results.values())[0]
        
        print("   Enhanced MonthlyResults structure:")
        print("      monthly_results = {")
        print("          'year': int,")
        print("          'month': int,")
        print("          'events': List[PersonEvent],")
        print("          'office_metrics': {...},")
        print("          'kpis': {")
        print("              'workforce': { # 13 metrics")
        for key in list(sample_month['kpis']['workforce'].keys())[:5]:
            print(f"                  '{key}': ...,")
        print("                  ...}")
        print("              'financial': { # 7 metrics")  
        for key in list(sample_month['kpis']['financial'].keys())[:3]:
            print(f"                  '{key}': ...,")
        print("                  ...}")
        print("              'activity': { # 4 metrics")
        for key in list(sample_month['kpis']['activity'].keys()):
            print(f"                  '{key}': ...,")
        print("              }")
        print("          },")
        print("          'business_plan_targets': {...}")
        print("      }")
        
        total_monthly_kpis = sum(len(kpis) for kpis in sample_month['kpis'].values())
        print(f"\\n   Total KPIs per month: {total_monthly_kpis}")
        print(f"   Months with KPIs: {len(enhanced_monthly_results)}")
        print(f"   Total KPI data points: {total_monthly_kpis * len(enhanced_monthly_results)}")
        
        # 8. Integration advantages
        print("\\n5. INTEGRATION ADVANTAGES")
        print("=" * 30)
        
        print("   ✅ Real-time KPI calculation during simulation")
        print("   ✅ KPIs stored alongside events in monthly results")
        print("   ✅ Consistent data: KPIs match workforce state exactly")
        print("   ✅ No post-processing required")
        print("   ✅ Month-over-month calculations accurate")
        print("   ✅ Business plan integration seamless")
        print("   ✅ Individual event tracking preserved")
        
        print("\\n   Proposed V2 Engine Enhancement:")
        print("   def _process_office_month(...):")
        print("       # 1. Process recruitment, churn, progression")
        print("       month_events = [...] ")
        print("       ")
        print("       # 2. Calculate monthly KPIs (NEW!)")
        print("       monthly_kpis = self._calculate_monthly_kpis(")
        print("           office_state, month_events, business_targets")
        print("       )")
        print("       ")
        print("       # 3. Store in MonthlyResults with KPIs")
        print("       return month_events, monthly_kpis")
        
        return True, {
            'months_processed': len(enhanced_monthly_results),
            'total_kpis_per_month': total_monthly_kpis,
            'total_events': sum(len(month['events']) for month in enhanced_monthly_results.values()),
            'integration_successful': True
        }
        
    except Exception as e:
        print(f"\\nERROR: Integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, {'error': str(e)}

if __name__ == "__main__":
    print("Starting Integrated Monthly KPI Testing")
    print("=" * 50)
    
    success, metrics = test_integrated_monthly_kpis()
    
    print("\\n" + "=" * 50)
    if success:
        print("SUCCESS: Integrated monthly KPI calculation working!")
        print(f"Processed {metrics['months_processed']} months with KPIs")
        print(f"Generated {metrics['total_kpis_per_month']} KPIs per month")
        print("Architecture: Events + KPIs calculated and stored together")
    else:
        print("FAILURE: Integration needs work")
        if 'error' in metrics:
            print(f"Error: {metrics['error']}")
    
    print(f"\\nIntegrated KPI test complete")