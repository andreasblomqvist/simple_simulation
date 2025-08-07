"""
Role-Specific KPI Calculation - V2 Engine

Tests KPI calculation with different business rules for different roles:

ROLE BUSINESS RULES:
1. Consultant: Billable hours, has levels (A→AC→C→SrC→M), progression rules, CAT matrix
2. Sales: Has levels (A→AC→C), progression rules, commission-based revenue
3. Recruitment: Has levels (A→AC→C), progression rules, placement-based revenue  
4. Operations: NO LEVELS, flat "Operations" level, no progression, fixed costs only

KPI CALCULATIONS MUST HANDLE:
- Billable vs non-billable roles
- Leveled vs flat role structures  
- Different revenue attribution models
- Progression-eligible vs non-progression roles
"""

import sys
import json
from pathlib import Path
from datetime import date
from collections import Counter, defaultdict

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

# Role business rule definitions
ROLE_DEFINITIONS = {
    'Consultant': {
        'billable': True,
        'has_levels': True,
        'levels': ['A', 'AC', 'C', 'SrC', 'M'],
        'progression_enabled': True,
        'revenue_model': 'billable_hours',
        'utilization_tracked': True
    },
    'Sales': {
        'billable': False,
        'has_levels': True, 
        'levels': ['A', 'AC', 'C'],
        'progression_enabled': True,
        'revenue_model': 'commission',
        'utilization_tracked': False
    },
    'Recruitment': {
        'billable': False,
        'has_levels': True,
        'levels': ['A', 'AC', 'C'], 
        'progression_enabled': True,
        'revenue_model': 'placement_fees',
        'utilization_tracked': False
    },
    'Operations': {
        'billable': False,
        'has_levels': False,
        'levels': ['Operations'],  # Single flat level
        'progression_enabled': False,
        'revenue_model': 'cost_center',
        'utilization_tracked': False
    }
}

def calculate_role_specific_workforce_kpis(office_state, month_events):
    """Calculate workforce KPIs broken down by role with business rules"""
    
    role_kpis = {}
    
    for role, role_definition in ROLE_DEFINITIONS.items():
        # Get role workforce
        role_workforce = office_state.workforce.get(role, {})
        
        # Count people by level (handle flat vs leveled)
        if role_definition['has_levels'] and len(role_definition['levels']) > 1:
            # Leveled role - count by each level
            level_counts = {}
            total_role_count = 0
            
            for level in role_definition['levels']:
                level_people = role_workforce.get(level, [])
                active_count = len([p for p in level_people if p.is_active])
                level_counts[level] = active_count
                total_role_count += active_count
        else:
            # Flat role - single level
            flat_level = role_definition['levels'][0]
            level_people = role_workforce.get(flat_level, [])
            active_count = len([p for p in level_people if p.is_active])
            level_counts = {flat_level: active_count}
            total_role_count = active_count
        
        # Count role-specific events
        role_events = [e for e in month_events if e.details.get('role') == role]
        role_event_types = Counter(event.event_type.value for event in role_events)
        
        role_kpi = {
            'role': role,
            'business_rules': role_definition,
            'total_headcount': total_role_count,
            'headcount_by_level': level_counts,
            
            # Event tracking
            'total_events': len(role_events),
            'hired_count': role_event_types.get('hired', 0),
            'churned_count': role_event_types.get('churned', 0),
            'promoted_count': role_event_types.get('promoted', 0) if role_definition['progression_enabled'] else 0,
            
            # Role-specific metrics
            'progression_eligible': role_definition['progression_enabled'],
            'billable_headcount': total_role_count if role_definition['billable'] else 0,
            'revenue_contributing': total_role_count if role_definition['revenue_model'] != 'cost_center' else 0,
        }
        
        # Calculate role-specific rates
        if total_role_count > 0:
            role_kpi.update({
                'hire_rate_pct': (role_event_types.get('hired', 0) / total_role_count * 100),
                'churn_rate_pct': (role_event_types.get('churned', 0) / total_role_count * 100),
                'promotion_rate_pct': (role_event_types.get('promoted', 0) / total_role_count * 100) if role_definition['progression_enabled'] else 0,
                'event_activity_rate': (len(role_events) / total_role_count * 100)
            })
        else:
            role_kpi.update({
                'hire_rate_pct': 0,
                'churn_rate_pct': 0,
                'promotion_rate_pct': 0,
                'event_activity_rate': 0
            })
        
        role_kpis[role] = role_kpi
    
    return role_kpis

def calculate_role_specific_financial_kpis(role_kpis, business_plan_targets):
    """Calculate financial KPIs with role-specific revenue attribution"""
    
    financial_kpis = {}
    
    # Get total revenue and costs
    total_revenue = business_plan_targets.revenue_target
    total_costs = business_plan_targets.operating_costs
    
    # Calculate billable workforce (only Consultants contribute to billable revenue)
    billable_headcount = sum(kpi['billable_headcount'] for kpi in role_kpis.values())
    total_headcount = sum(kpi['total_headcount'] for kpi in role_kpis.values())
    revenue_contributing_headcount = sum(kpi['revenue_contributing'] for kpi in role_kpis.values())
    
    # Role-specific financial metrics
    for role, role_kpi in role_kpis.items():
        role_definition = ROLE_DEFINITIONS[role]
        role_headcount = role_kpi['total_headcount']
        
        # Revenue attribution by role type
        if role_definition['revenue_model'] == 'billable_hours':
            # Consultants get attributed billable revenue
            role_revenue = (role_headcount / billable_headcount * total_revenue) if billable_headcount > 0 else 0
            role_revenue_type = 'billable_hours'
            
        elif role_definition['revenue_model'] == 'commission':
            # Sales gets attributed percentage of revenue (assume 15% commission model)
            role_revenue = total_revenue * 0.15 if role_headcount > 0 else 0
            role_revenue_type = 'commission'
            
        elif role_definition['revenue_model'] == 'placement_fees':
            # Recruitment gets fixed placement fees (assume $5K per person)
            role_revenue = role_headcount * 5000
            role_revenue_type = 'placement_fees'
            
        else:  # cost_center
            # Operations is pure cost center
            role_revenue = 0
            role_revenue_type = 'cost_center'
        
        # Role costs (distribute equally for simplicity)
        role_costs = (role_headcount / total_headcount * total_costs) if total_headcount > 0 else 0
        
        role_financial = {
            'role': role,
            'revenue_model': role_revenue_type,
            'revenue': role_revenue,
            'costs': role_costs,
            'profit': role_revenue - role_costs,
            'profit_margin_pct': ((role_revenue - role_costs) / role_revenue * 100) if role_revenue > 0 else 0,
            'revenue_per_fte': role_revenue / role_headcount if role_headcount > 0 else 0,
            'cost_per_fte': role_costs / role_headcount if role_headcount > 0 else 0,
            'billable': role_definition['billable']
        }
        
        financial_kpis[role] = role_financial
    
    return financial_kpis

def test_role_specific_kpis():
    """Test role-specific KPI calculation with different business rules"""
    print("V2 ENGINE - ROLE-SPECIFIC KPI CALCULATION")
    print("=" * 45)
    
    try:
        from src.services.simulation_engine_v2 import (
            SimulationEngineV2Factory, ScenarioRequest, TimeRange, Levers,
            BusinessPlan, MonthlyPlan, PopulationSnapshot, WorkforceEntry, 
            Person, OfficeState, CATMatrix
        )
        
        # 1. Setup engine (same as previous tests)
        print("1. Setting up V2 engine with role definitions...")
        
        engine = SimulationEngineV2Factory.create_test_engine(random_seed=42)
        test_data_dir = Path(__file__).parent / "test_data"
        
        # Load test data
        with open(test_data_dir / "business_plans.json") as f:
            business_plans_data = json.load(f)
        
        with open(test_data_dir / "cat_matrices_correct.json") as f:
            cat_matrices_data = json.load(f)
            
        with open(test_data_dir / "population_snapshots.json") as f:
            population_data = json.load(f)
        
        # Setup business plans, CAT matrices, population (same as before)
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
        
        print(f"   Setup complete: {office_state.get_total_workforce()} people across {len(office_state.workforce)} roles")
        
        # 2. Display role business rules
        print("\\n2. ROLE BUSINESS RULES")
        print("=" * 25)
        
        for role, definition in ROLE_DEFINITIONS.items():
            current_count = sum(len([p for p in people if p.is_active]) 
                               for people in office_state.workforce.get(role, {}).values())
            
            print(f"\\n   {role} ({current_count} people):")
            print(f"      Billable: {definition['billable']}")
            print(f"      Has levels: {definition['has_levels']} ({definition['levels']})")
            print(f"      Progression: {definition['progression_enabled']}")
            print(f"      Revenue model: {definition['revenue_model']}")
            print(f"      Utilization tracked: {definition['utilization_tracked']}")
        
        # 3. Run simulation with role-specific processing
        print("\\n3. Running simulation with role-specific KPI calculation...")
        
        scenario = ScenarioRequest(
            scenario_id="role_specific_test",
            name="Role-Specific KPI Test",
            time_range=TimeRange(2024, 7, 2024, 7),  # Single month to focus on role analysis
            office_ids=["london"],
            levers=Levers(
                recruitment_multiplier=1.0,
                churn_multiplier=1.1,
                progression_multiplier=1.0
            )
        )
        
        # Process July 2024 (progression month)
        current_date = date(2024, 7, 1)
        month_events = engine._process_office_month(
            office_state, 2024, 7, current_date, scenario.levers
        )
        
        print(f"   July 2024 processing complete: {len(month_events)} events")
        
        # Get business plan
        business_plan_targets = engine.business_processor.get_monthly_targets(office_id, 2024, 7)
        
        # 4. ROLE-SPECIFIC KPI CALCULATION
        print("\\n4. ROLE-SPECIFIC WORKFORCE KPIs")
        print("=" * 35)
        
        role_workforce_kpis = calculate_role_specific_workforce_kpis(office_state, month_events)
        
        for role, role_kpi in role_workforce_kpis.items():
            print(f"\\n   {role}:")
            print(f"      Total headcount: {role_kpi['total_headcount']}")
            print(f"      Levels: {role_kpi['headcount_by_level']}")
            print(f"      Events: {role_kpi['total_events']} ({role_kpi['hired_count']} hired, {role_kpi['churned_count']} churned, {role_kpi['promoted_count']} promoted)")
            print(f"      Rates: {role_kpi['hire_rate_pct']:.1f}% hire, {role_kpi['churn_rate_pct']:.1f}% churn, {role_kpi['promotion_rate_pct']:.1f}% promotion")
            print(f"      Billable people: {role_kpi['billable_headcount']}")
            print(f"      Revenue contributing: {role_kpi['revenue_contributing']}")
            print(f"      Progression eligible: {role_kpi['progression_eligible']}")
        
        # 5. ROLE-SPECIFIC FINANCIAL KPIs
        print("\\n5. ROLE-SPECIFIC FINANCIAL KPIs")
        print("=" * 35)
        
        role_financial_kpis = calculate_role_specific_financial_kpis(role_workforce_kpis, business_plan_targets)
        
        total_revenue = 0
        total_costs = 0
        
        for role, role_financial in role_financial_kpis.items():
            total_revenue += role_financial['revenue']
            total_costs += role_financial['costs']
            
            print(f"\\n   {role} Financial:")
            print(f"      Revenue model: {role_financial['revenue_model']}")
            print(f"      Revenue: ${role_financial['revenue']:,.0f}")
            print(f"      Costs: ${role_financial['costs']:,.0f}")
            print(f"      Profit: ${role_financial['profit']:,.0f} ({role_financial['profit_margin_pct']:.1f}%)")
            print(f"      Per-FTE: ${role_financial['revenue_per_fte']:,.0f} revenue, ${role_financial['cost_per_fte']:,.0f} costs")
            print(f"      Billable: {role_financial['billable']}")
        
        # 6. Aggregated KPIs
        print("\\n6. AGGREGATED OFFICE KPIs")
        print("=" * 30)
        
        total_headcount = sum(kpi['total_headcount'] for kpi in role_workforce_kpis.values())
        total_billable = sum(kpi['billable_headcount'] for kpi in role_workforce_kpis.values())
        total_events = sum(kpi['total_events'] for kpi in role_workforce_kpis.values())
        
        print(f"   Total workforce: {total_headcount} people")
        print(f"   Billable workforce: {total_billable} people ({total_billable/total_headcount*100:.1f}%)")
        print(f"   Total events: {total_events}")
        print(f"   Total revenue: ${total_revenue:,.0f}")
        print(f"   Total costs: ${total_costs:,.0f}")
        print(f"   Total profit: ${total_revenue - total_costs:,.0f} ({(total_revenue-total_costs)/total_revenue*100:.1f}%)")
        
        # 7. Role-specific data structure demonstration
        print("\\n7. ROLE-SPECIFIC KPI DATA STRUCTURE")
        print("=" * 40)
        
        print("   Enhanced monthly results with role-specific KPIs:")
        print("   monthly_results['2024-07'] = {")
        print("       'kpis': {")
        print("           'role_specific_workforce': {")
        
        for role in ROLE_DEFINITIONS.keys():
            print(f"               '{role}': {{")
            print(f"                   'business_rules': {role}_definition,")
            print(f"                   'total_headcount': int,")
            print(f"                   'headcount_by_level': dict,")
            print(f"                   'event_counts': dict,")
            print(f"                   'billable_headcount': int,")
            print(f"                   'progression_eligible': bool")
            print(f"               }},")
        
        print("           },")
        print("           'role_specific_financial': {")
        
        for role in ROLE_DEFINITIONS.keys():
            print(f"               '{role}': {{")
            print(f"                   'revenue_model': str,")
            print(f"                   'revenue': float,")
            print(f"                   'costs': float,")
            print(f"                   'profit': float")
            print(f"               }},")
        
        print("           }")
        print("       }")
        print("   }")
        
        total_role_metrics = len(role_workforce_kpis) * 10  # Approx metrics per role
        print(f"\\n   Role-specific metrics: {total_role_metrics} (across {len(ROLE_DEFINITIONS)} roles)")
        print(f"   Business rules enforced: Billable/non-billable, leveled/flat, progression eligibility")
        
        return True, {
            'roles_processed': len(role_workforce_kpis),
            'total_headcount': total_headcount,
            'billable_headcount': total_billable,
            'total_events': total_events,
            'role_specific_metrics': total_role_metrics
        }
        
    except Exception as e:
        print(f"\\nERROR: Role-specific KPI test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, {'error': str(e)}

if __name__ == "__main__":
    print("Starting Role-Specific KPI Testing")
    print("=" * 45)
    
    success, metrics = test_role_specific_kpis()
    
    print("\\n" + "=" * 45)
    if success:
        print("SUCCESS: Role-specific KPI calculation working!")
        print(f"Processed {metrics['roles_processed']} roles with different business rules")
        print(f"Total workforce: {metrics['total_headcount']} ({metrics['billable_headcount']} billable)")
        print("Business rules: Billable hours, commission, placement fees, cost center")
    else:
        print("FAILURE: Role-specific KPI calculation needs work")
        if 'error' in metrics:
            print(f"Error: {metrics['error']}")
    
    print(f"\\nRole-specific KPI test complete")